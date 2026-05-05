# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm the response includes `service_context: local`.** Don't trust conversation IDs to tell you which instance — the same IDs can exist on both prod and local with different histories.

## SOURCE OF TRUTH

When stats in any doc disagree:
1. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative, conceptual ground truth
2. **`docs/PLATFORM_INVENTORY.md`** — runtime-derived, regenerable via `python manage.py generate_platform_inventory`

Live drift report: `python manage.py verify_doc_claims --only-drift`

If you're unsure which doc to trust, read these two first.

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby / PA endpoint.
- `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compatibility-only shims.
- Rigby resolves `global` vs `workspace` mode explicitly from request/profile/context. Do not infer workspace scope from message text alone.
- The Workspace Files tab now supports preview, edit/save, and file history on the live `FilesTab` surface.
- Close the loop before you call work complete: run the relevant build/tests, update the handoff, and re-run `verify_doc_claims --only-drift` if docs changed.

---

## SESSION 1100+ — CURRENT AUDIT / CLEANUP ENTRY POINT

This repo is now in the Phase 1 cleanup pass for `docs/audit/CLEANUP_PLAN.md`.
Start with the current audit artifacts, not the older Session 1099 canary
window:

- Audit: [`docs/audit/AUDIT_V1.md`](docs/audit/AUDIT_V1.md)
- Cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](docs/audit/CLEANUP_PLAN.md)
- Verification report: [`docs/verification/VERIFY_REPORT.md`](docs/verification/VERIFY_REPORT.md)
- Canonical inventory: [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md)

### Current focus

1. Reconcile active docs with runtime truth.
2. Keep historical canary material in the Session 1098 handoff rather than
   duplicating it here.
3. Treat `core.settings` and `run_stock_audit_cycle` as the runtime sources of
   truth for settings and stock schedule ownership.

### What to read next

- Fresh handoff: [`docs/handoffs/SESSION_1100_CONTEXT_KIT_DRIFT_PREVENTION.md`](docs/handoffs/SESSION_1100_CONTEXT_KIT_DRIFT_PREVENTION.md)
- Previous handoff: [`docs/handoffs/SESSION_1098_WRAP_CANARY_GREEN.md`](docs/handoffs/SESSION_1098_WRAP_CANARY_GREEN.md)
- Current audit: [`docs/audit/AUDIT_V1.md`](docs/audit/AUDIT_V1.md)
- Current cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](docs/audit/CLEANUP_PLAN.md)

### Runtime reminders

- `tools/pa_chat.py` defaults to the production API URL. Set `PA_API_URL`
  explicitly before any local Rigby work.
- `core.settings` is the runtime Django settings module.
- `run_stock_financial_agents` is a compatibility wrapper that delegates to
  `run_stock_audit_cycle`.
- `workspace_id` should come from explicit scope, not guesswork.

### Historical context

The Session 1098 canary story remains in the handoff archive:
[`docs/handoffs/SESSION_1098_WRAP_CANARY_GREEN.md`](docs/handoffs/SESSION_1098_WRAP_CANARY_GREEN.md).
Do not restate it here unless the cleanup pass needs a specific historical
reference.
