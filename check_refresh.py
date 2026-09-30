"""Dependency-free checks at the report-export boundary."""
import unittest
import tempfile
import json
from pathlib import Path
from datetime import date, datetime, timezone
from refresh import plan_ranges, utc_midnight, export_report, FIELDS

class ReportChecks(unittest.TestCase):
    def test_complete_pacific_days_and_new_month(self):
        ranges = plan_ranges(datetime(2026, 10, 2, 10, tzinfo=timezone.utc))
        self.assertEqual(ranges[0], {'id':'2026-10','label':'October 2026','start':'2026-10-01','end':'2026-10-02','requestedStart':'2026-10-01'})
        self.assertEqual(ranges[-1]['id'], 'last90')
        self.assertEqual(ranges[-1]['start'], '2026-09-01')
        self.assertEqual(ranges[-1]['requestedStart'], '2026-07-04')
        self.assertEqual(plan_ranges(datetime(2026,10,1,6,tzinfo=timezone.utc))[0]['end'], '2026-09-30')
        self.assertEqual(plan_ranges(datetime(2026,10,1,10,tzinfo=timezone.utc))[0]['id'], '2026-09')
        self.assertEqual(utc_midnight(date(2026,11,1)), '2026-11-01 07:00:00')
        self.assertEqual(utc_midnight(date(2026,11,2)), '2026-11-02 08:00:00')
        leap = plan_ranges(datetime(2028,3,1,10,tzinfo=timezone.utc))[0]
        self.assertEqual((leap['start'],leap['end']), ('2028-02-01','2028-03-01'))
        self.assertEqual(plan_ranges(datetime(2027,1,2,10,tzinfo=timezone.utc))[0]['id'], '2027-01')

    def test_export_exact_totals_and_preserve_on_failure(self):
        def query(sql):
            # One returning person booked in two different weeks, total is still one.
            return {'columns':['bucket',*FIELDS], 'results':[
                ['total',1,1,1,1,1,1,1,1],
                ['2026-08-31',1,1,1,1,1,1,1,1],
                ['2026-09-07',1,1,1,1,1,1,1,1]]}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'report.json'
            now = datetime(2026,9,9,10,tzinfo=timezone.utc)
            # Only September, so all ranges share coverage except last7.
            report = export_report(now, output, query, {'emails':[], 'patterns':[]})
            month = report['ranges'][0]
            self.assertEqual(month['totals']['booked'], 1)
            self.assertEqual(sum(w['booked'] for w in month['weeks']), 2)
            self.assertEqual(month['weeks'][0]['days'], 6)
            self.assertEqual(month['weeks'][1]['days'], 2)
            self.assertEqual(month['weeks'][1]['end'], '2026-09-09')
            saved = output.read_bytes()
            for response in ({'results':[]}, {'columns':['bucket',*FIELDS], 'results':[['total',-1,0,0,0,0,0,0,0]]}, {'columns':['bucket',*FIELDS], 'results':[['total',1,1,1,1,1,1,1,1]], 'hasMore':True}):
                with self.assertRaises(ValueError):
                    export_report(now, output, lambda sql: response, {'emails':[], 'patterns':[]})
                self.assertEqual(output.read_bytes(), saved)
            def fail(sql):
                raise TimeoutError('simulated')
            with self.assertRaises(TimeoutError):
                export_report(now, output, fail, {'emails':[], 'patterns':[]})
            self.assertEqual(output.read_bytes(), saved)

if __name__ == '__main__':
    unittest.main()
