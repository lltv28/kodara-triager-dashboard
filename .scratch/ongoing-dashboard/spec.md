# Ongoing Triager dashboard

Status: ready-for-agent

## Problem
The published dashboard is a fixed September snapshot and cannot report later months or rolling periods.

## Solution
Keep the existing public aggregate dashboard and add calendar months plus last 7/30/90 days, refreshed daily. User explicitly approved public automatic aggregate publishing and these presets.

## User stories
1. Select any available month without a code change.
2. Compare last 7, 30, or 90 complete Pacific days.
3. See exact unique-person totals, not sums that double-count return visitors.
4. Explore weekly slices inside the selected range.
5. Keep counts and previous-step percentages together in the tables.
6. See Q1/calendar/booked and other existing progression ratios for every range.
7. Understand the date coverage, refresh timestamp, partial weeks, and stale data.
8. Use the same dashboard on mobile and desktop.
9. Continue seeing the last good report if a refresh fails.
10. Keep customer records and credentials out of the public repository and website.

## Implementation decisions
- Native selects and existing static design; no framework or backend.
- Daily GitHub Actions query exact whole-period and weekly counts from PostHog, then publish an allowlisted static artifact through GitHub Pages.
- Read-only project-scoped key and personal test exclusions are GitHub secrets.
- Complete Pacific days through yesterday; Monday weeks clipped to the selected range. Tracking coverage starts September 1, 2026. Longer rolling ranges clearly disclose clipped coverage.
- Every calendar month from coverage start through the latest complete day is available, with the latest month selected initially.
- Retain existing production event definitions, exclusions, and period-ratio caveats. Do not claim these are cohort conversions or attended appointments.
- Replace output only after all queries and schema checks succeed. Display stale warning after 36 hours.

## Testing
Test the snapshot export boundary with deterministic API responses: correct independent totals, Pacific DST/leap/year boundaries, clipped weeks, invalid response handling, and preservation after failures. Keep existing dependency-free ratio checks. Browser-check period changes, zero values, mobile layout and failed data loading. Review against baseline 9cebcb2 before publishing.

## Out of scope
Custom start/end dates, raw customer data, widget changes, new tracking events, and booking tests.
