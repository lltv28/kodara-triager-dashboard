# Kodara Triager dashboard

[Public dashboard](https://lltv28.github.io/kodara-triager-dashboard/) · [Refresh runs](https://github.com/lltv28/kodara-triager-dashboard/actions/workflows/dashboard.yml)

Calendar months and last 7/30/90 days, refreshed daily from PostHog project 572719. Only aggregate counts are published. No customer records, person IDs, credentials, or private exclusion addresses are included.

## Reporting behavior

- Dates use America/Los_Angeles. Rolling ranges include complete days through yesterday. New months appear after their first complete day. Weeks start Monday and are clipped to the selected range.
- Coverage starts September 1, 2026. Longer rolling presets disclose incomplete coverage until enough days have elapsed.
- Every range has its own exact unique-person total. Never sum weekly or daily counts to calculate unique range totals.
- Counts and percentage of the previous step appear together. Progression rates are period activity ratios, not ordered cohort conversions.
- Select a month or rolling range, switch chart metrics, or click a week. “Show whole period” restores the whole-range KPIs.
- No activity means zero counts and an empty-state explanation. A zero denominator displays “—”.
- The visible refresh time is the last successful export. After 36 hours, the page warns that the snapshot is stale. Failed queries or validation stop publication and preserve the last good site and snapshot.

## Refresh and deployment

GitHub Actions runs at 10:17 UTC daily (3:17 AM PDT / 2:17 AM PST), on main pushes, and on manual dispatch. Scheduled starts may be delayed by GitHub. New snapshots are committed by the workflow and published with GitHub Pages using the Actions deployment source. Only `index.html`, `data.js`, `report.json`, and `.nojekyll` enter the site artifact. Pull requests run checks without credentials or publishing.

Two repository Actions secrets are required:

- `POSTHOG_PERSONAL_API_KEY`: PostHog personal key restricted to project 572719, with `query:read` only.
- `TRIAGER_TEST_EXCLUSIONS`: JSON with `emails` (exact matches) and `patterns` (SQL LIKE patterns) for private test accounts. Domain exclusions for kodara.com/example.com and the internal/test property are also applied using current person properties.

The script uses the [PostHog query API](https://posthog.com/docs/api/query). It validates numeric aggregate rows and constructs its public output separately; API metadata and SQL are never published or logged. It re-queries historical months so late events and updated exclusions are reflected.

Run a refresh manually with `gh workflow run dashboard.yml --repo lltv28/kodara-triager-dashboard`, then inspect the run. If an API key is revoked, replace the secret and rerun. If GitHub disables scheduled runs, re-enable the workflow in Actions; daily snapshot commits normally keep this repository active. No third-party service or new paid plan is required.

## Local preview and checks

```sh
python3 check_refresh.py
node check.cjs
python3 -m http.server 3211 --bind 127.0.0.1
```

Open http://127.0.0.1:3211. Use a server because the page fetches `report.json`. No dependencies or build step are required. `python3 refresh.py` needs the two environment variables above; never store them in public source.
