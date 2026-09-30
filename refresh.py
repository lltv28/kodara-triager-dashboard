"""Export exact, aggregate-only Triager ranges. Python standard library only."""
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ZONE = ZoneInfo('America/Los_Angeles')
COVERAGE_START = date(2026, 9, 1)
FIELDS = ['loaded', 'q1', 'emails', 'business', 'revenue', 'calendar', 'time', 'booked']


def utc_midnight(day):
    return datetime.combine(day, datetime.min.time(), ZONE).astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def plan_ranges(now):
    end = now.astimezone(ZONE).date()
    if end <= COVERAGE_START:
        raise ValueError('No complete reporting day available')
    ranges = []
    start = COVERAGE_START
    while start < end:
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        ranges.append({'id':start.strftime('%Y-%m'), 'label':start.strftime('%B %Y'),
                       'start':start.isoformat(), 'end':min(end, next_month).isoformat(),
                       'requestedStart':start.isoformat()})
        start = next_month
    ranges.reverse()
    for days in (7, 30, 90):
        requested = end - timedelta(days=days)
        ranges.append({'id':f'last{days}', 'label':f'Last {days} days',
                       'start':max(COVERAGE_START, requested).isoformat(), 'end':end.isoformat(),
                       'requestedStart':requested.isoformat()})
    return ranges


def sql_string(value):
    return "'" + value.replace('\\', '\\\\').replace("'", "\\'") + "'"


def build_query(start, end, exclusions):
    conditions = ["coalesce(properties.$internal_or_test_user, '') = 'true'",
                  "lower(coalesce(properties.email, '')) LIKE '%@kodara.com'",
                  "lower(coalesce(properties.email, '')) LIKE '%@example.com'"]
    if set(exclusions) != {'emails', 'patterns'}:
        raise ValueError('Private exclusions must contain emails and patterns')
    for kind, operator in [('emails', '='), ('patterns', 'LIKE')]:
        if not isinstance(exclusions[kind], list) or not all(isinstance(v, str) and '@' in v for v in exclusions[kind]):
            raise ValueError('Invalid private exclusions')
        conditions += [f"lower(coalesce(properties.email, '')) {operator} {sql_string(v.lower())}" for v in exclusions[kind]]
    events = [('triager_widget_loaded', None), ('triager_step_completed', 'video_readiness'),
              ('triager_step_completed', 'contact_email'), ('triager_step_completed', 'business_description'),
              ('triager_step_completed', 'monthly_revenue'), ('triager_step_viewed', 'availability_day'),
              ('triager_step_completed', 'availability_time'), ('triager_booking_completed', None)]
    metrics = ',\n'.join(f"uniqExactIf(person_id, event = '{event}'" +
                        (f" AND properties.step_id = '{step}'" if step else '') + f') AS {field}'
                        for field, (event, step) in zip(FIELDS, events))
    where = f"""FROM events WHERE timestamp >= toDateTime('{utc_midnight(start)}', 'UTC')
AND timestamp < toDateTime('{utc_midnight(end)}', 'UTC')
AND properties.environment = 'production'
AND event IN ('triager_widget_loaded','triager_step_completed','triager_step_viewed','triager_booking_completed')
AND person_id NOT IN (SELECT id FROM persons WHERE {' OR '.join(conditions)})"""
    return f"""SELECT 'total' AS bucket, {metrics} {where}
UNION ALL
SELECT toString(toStartOfWeek(toTimeZone(timestamp, 'America/Los_Angeles'), 1)) AS bucket,
{metrics} {where} GROUP BY bucket
LIMIT 100"""


def parse_counts(response, start, end):
    if (response.get('columns') != ['bucket', *FIELDS] or response.get('hasMore')
            or response.get('error') or not isinstance(response.get('results'), list)):
        raise ValueError('Incomplete or invalid PostHog aggregate response')
    counts = {}
    monday = start - timedelta(days=start.weekday())
    valid_weeks = {(monday + timedelta(days=i)).isoformat() for i in range(0, (end-monday).days, 7)}
    for row in response['results']:
        if (not isinstance(row, list) or len(row) != 9 or row[0] in counts
                or row[0] not in {'total', *valid_weeks}
                or any(type(n) is not int or not 0 <= n <= 9007199254740991 for n in row[1:])):
            raise ValueError('Invalid aggregate row')
        counts[row[0]] = dict(zip(FIELDS, row[1:]))
    if 'total' not in counts:
        raise ValueError('Missing independently deduplicated total')
    weeks = []
    for bucket in sorted(valid_weeks):
        week_start = max(start, date.fromisoformat(bucket))
        week_end = min(end, date.fromisoformat(bucket) + timedelta(days=7))
        days = (week_end - week_start).days
        weeks.append({'start':week_start.isoformat(), 'end':week_end.isoformat(), 'days':days,
                      **counts.get(bucket, dict.fromkeys(FIELDS, 0))})
    for field in FIELDS:
        if not max(w[field] for w in weeks) <= counts['total'][field] <= sum(w[field] for w in weeks):
            raise ValueError('Weekly and period totals are inconsistent')
    return counts['total'], weeks


def export_report(now, output, query, exclusions):
    ranges = plan_ranges(now)
    cache = {}
    for period in ranges:
        start, end = date.fromisoformat(period['start']), date.fromisoformat(period['end'])
        key = (start, end)
        if key not in cache:
            cache[key] = parse_counts(query(build_query(start, end, exclusions)), start, end)
        period['totals'], period['weeks'] = cache[key]
    report = {'schemaVersion':1, 'generatedAt':now.astimezone(timezone.utc).isoformat(),
              'timezone':str(ZONE), 'coverageStart':COVERAGE_START.isoformat(),
              'through':(now.astimezone(ZONE).date()-timedelta(days=1)).isoformat(), 'ranges':ranges}
    # Publish only validated numeric aggregates and generated date metadata, never API response metadata.
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(output)
    return report


def posthog_query(sql):
    request = Request('https://us.posthog.com/api/projects/572719/query/',
                      data=json.dumps({'query':{'kind':'HogQLQuery', 'query':sql},
                                       'name':'Public Triager aggregate dashboard', 'refresh':'blocking'}).encode(),
                      headers={'Authorization':'Bearer ' + os.environ['POSTHOG_PERSONAL_API_KEY'],
                               'Content-Type':'application/json'}, method='POST')
    with urlopen(request, timeout=90) as response:
        return json.load(response)


if __name__ == '__main__':
    try:
        exclusions = json.loads(os.environ['TRIAGER_TEST_EXCLUSIONS'])
        report = export_report(datetime.now(timezone.utc), Path('report.json'), posthog_query, exclusions)
        print(f"Exported {len(report['ranges'])} aggregate ranges through {report['through']} Pacific.")
    except Exception as error:
        # Do not log query SQL, private exclusions, credentials, or raw API responses.
        raise SystemExit(f'Refresh failed ({type(error).__name__}); previous snapshot preserved.')
