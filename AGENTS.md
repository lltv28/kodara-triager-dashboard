# Dashboard conventions

Keep this dashboard dependency-free. Publish aggregate counts only: no credentials, customer rows, person IDs, or personal test-account addresses. Keep the existing green-and-white design and accessible native controls.

## Agent skills

Issues and specs live in local Markdown under `.scratch/`; see `docs/agents/issue-tracker.md`. Domain documentation is single-context; see `docs/agents/domain.md` and `CONTEXT.md`.

Run `python3 check_refresh.py` and `node check.cjs` before publishing. Verify changed interactions in a browser. Never sum weekly unique counts to produce a range total.
