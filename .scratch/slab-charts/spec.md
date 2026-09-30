# Slab charts (LLT-56)

Status: In review

## Problem
Linear LLT-56 asks for the dashboard charts to use the LLT-53 "Customer behavior" look: vibrant blue isometric slabs, bottom-aligned, light dividers between columns, a label and big number on top, and a lighter ramp down to the next slab.

## Solution
Restyle only the week-by-week chart and the funnel panel in `index.html`. Both render through one `plot()` helper: a `#0B3BE8` slab on one scale and a `#8E9DF0` ramp from its top to the next slab's top. The page chrome, KPI cards, tables, controls and data notes stay green and white.

## Implementation decisions
- Week by week: each week is one `button.slab` holding its label, count, full/partial note and slab, so the whole column selects the week. The scale, metric toggles, `aria-pressed`, focus return, partial-week stripes and table highlighting are unchanged. Gridlines are dropped because every column shows its count.
- Funnel: the same five steps and "% of widget-load count" notes. Slabs share one scale set by the largest step. A note says the ramps are visual joins, not same-person conversions.
- Narrow screens scroll each slab grid inside its own labelled region, as the weekly chart already did.
- No data, refresh, validation or counting changes. No dependencies.
- Hermes previews send CSP `connect-src 'none'`, which blocks `fetch('report.json')`. `loadReport()` therefore uses `window.REPORT` when a page defines it and otherwise fetches `report.json` as before. Only the Builder preview build defines it: it wraps the same committed `report.json` as `report.js` (`window.REPORT=…;`) and adds `<script src="report.js">` after `data.js`. GitHub Pages, the Actions workflow and `refresh.py` are unchanged; the public site never requests `report.js`, and refreshes only ever update `report.json`.

## Open question
AGENTS.md says to keep the existing green-and-white design. Blue appears only in chart marks, matching the published LLT-53 light page (green chrome with blue slabs). If this merges, AGENTS.md should allow the slab blues.

## Verification
`python3 check_refresh.py` and `node check.cjs` pass. Headless Chromium with an isolated profile checked the September and last-7 counts, week selection by click, keyboard and table button, focus return, "Show whole period", metric switching, period changes, limited coverage, the stale warning, a zero period, a failed report load, and 14 weekly slabs at 390px and 1366px with no page overflow. The same suite ran twice: once over plain HTTP, where the page must fetch `report.json` and never request `report.js`, and once over the preview bundle with the exact Hermes CSP, where it must render from `report.js`, never request `report.json`, and log no CSP violations. The pre-fix bundle, served with that CSP, reproduces "Could not load the report."
