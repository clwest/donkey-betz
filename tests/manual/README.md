# `tests/manual/` — Browser-Based Manual Tests

**Status:** archival. Use for debugging / visual verification; not run by CI.

## What's in here

4 HTML files moved here from the repo root during **Cleanup Phase 2** (2026-04-20). They're manual browser-testing harnesses built during specific features:

- `test_frontend_data_flow.html` — early frontend WebSocket / data-flow debugging
- `test_notification_system.html` — notification system visual test
- `test_revenue_dashboard_real_data.html` — revenue dashboard data verification
- `test_sports_hub_fixed.html` — sports hub regression test

## How to run

1. Start the Django dev server: `make start`
2. Open one of these HTML files directly in a browser:
   ```bash
   open tests/manual/test_frontend_data_flow.html
   ```
3. The pages typically hit `http://localhost:8000/...` endpoints and display results in-page.

## Why not deleted

Per `docs/docs-pattern/06_dos_and_donts.md` **DO 11**: archive, never delete. These have been useful for one-off regression checks and may be useful again.

## Related

- `docs/cleanup/PHASE_2_EXECUTION_LOG.md` — execution log for this phase
