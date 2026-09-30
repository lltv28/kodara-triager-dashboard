# Triager reporting

A period contains independently deduplicated PostHog person counts for eight steps, plus Monday-start weekly slices. A progression rate divides two activity counts; it is not an ordered same-person conversion funnel. Weekly counts must never be added to calculate a period total.

The public GitHub Pages site receives aggregate snapshots only. A daily GitHub Actions refresh queries project 572719 using a read-only secret. Reporting starts September 1, 2026 and uses America/Los_Angeles calendar dates. Last 7/30/90 days mean complete Pacific days through yesterday. New months appear once their first complete day is available. Failed refreshes preserve the previous snapshot and its timestamp.
