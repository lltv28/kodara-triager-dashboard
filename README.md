# September Triager dashboard

Interactive dashboard based on verified PostHog aggregates through September 29, 2026 at 8:35 PM Pacific. This is a saved snapshot, not a live analytics integration.

Published with GitHub Pages: https://lltv28.github.io/kodara-triager-dashboard/

The public site contains aggregate counts only. It does not include credentials, customer records or the internal project handoff.

## Local preview

Open `index.html` directly, or serve this directory:

```sh
python3 -m http.server 3211 --bind 127.0.0.1
```

Then visit http://127.0.0.1:3211. No build or dependencies required.

The question-by-question table shows each count prominently with its percentage of the preceding column underneath. Both are always visible; no view toggle is needed. Percentages are period activity ratios, not ordered cohort conversion rates.

A second weekly table compares Q1 to calendar/booked, email to calendar/booked, calendar to booked, and widget loaded to booked. Each rate shows its numerator and denominator; monthly rates use independently deduplicated monthly totals.

Select a reporting week, switch the chart metric, or click a chart bar/table week. Monthly totals are independently deduplicated; do not calculate them by summing the weeks. Definitions, exclusions and coverage limitations are available in the dashboard.

Run `node check.cjs` to verify aggregate totals and calculations. Browser verification covered all four chart metrics, week selection, monthly reset and a 390px mobile viewport without page overflow or console errors.

## Publishing updates

GitHub Pages serves the root of `main`. Push changes to `index.html` and `data.js` to update the site. Run `node check.cjs` before publishing data changes. Update the visible snapshot date when refreshing the underlying data.
