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

This is **precedence**, not enumeration order. When docs disagree:

1. **`docs/PLATFORM_INVENTORY.md` wins for runtime facts** — counts, schedules, tasks, agents, spiders, models, routes. Runtime-derived; regenerate with `python manage.py generate_platform_inventory`.
2. **`docs/PLATFORM_WHAT_IT_IS.md` is the narrative anchor** — what each subsystem is, why it exists, how it fits together. Use it for conceptual context, not for current numbers.
3. **Archive and handoff docs are historical** unless explicitly promoted by [`docs/handoffs/CURRENT.md`](docs/handoffs/CURRENT.md) or this file. Their numbers and route examples may be stale by design — banners on those docs say so.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift` (Django-side)
- [`docs/verification/VERIFY_REPORT.md`](docs/verification/VERIFY_REPORT.md) (context-kit, regenerated via `context-kit verify --write`)

If you're unsure which doc to trust, read INVENTORY first, then WHAT_IT_IS.

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby / PA endpoint.
- `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compatibility-only shims.
- Rigby resolves `global` vs `workspace` mode explicitly from request/profile/context. Do not infer workspace scope from message text alone.
- The Workspace Files tab now supports preview, edit/save, and file history on the live `FilesTab` surface.
- Close the loop before you call work complete: run the relevant build/tests, update the handoff, and re-run `verify_doc_claims --only-drift` if docs changed.

---

## SESSION 1102+ — CURRENT AUDIT / CLEANUP ENTRY POINT

Phase 1 (Session 1101) closed the spider-count `CONFLICT` and reconciled
active docs. Phase 2B (Session 1102) fixed the CLAUDE.md taxonomy drift
(`73/8/2` → `73/9/1`), added a `<!-- DOC-AUTOGEN -->` header to the
generated `docs/INDEX.md`, and regenerated the index. Verifier reports
`CONFLICT: 0`.

Phase 2A investigation found that `core/rag.py:top_k()` is **dormant in
production** — only consumed by local Ollama dev tools. Production PA RAG
goes through `Document` model + pgvector via
`sync_docs_index_to_documents`. `.rag/corpus.jsonl` is **orphaned** (no
in-repo producer); cleanup decision queued for the next session.

Remaining cleanup: H4 (donkey-logo replacement), `.rag/` decision
(untrack vs. add `build_rag_corpus`), platform-inventory refresh, and
CI guardrail wiring.

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

- Fresh handoff: [`docs/handoffs/SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md`](docs/handoffs/SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md)
- Stable pointer: [`docs/handoffs/CURRENT.md`](docs/handoffs/CURRENT.md) (always points at the latest two handoffs)
- Previous handoff: [`docs/handoffs/SESSION_1101_PHASE1_DOCS_CLEANUP.md`](docs/handoffs/SESSION_1101_PHASE1_DOCS_CLEANUP.md)
- Audit workspace index: [`docs/AUDIT_INDEX.md`](docs/AUDIT_INDEX.md) (canonical = `docs/audit/`; `docs/audit-2026/` and `docs/audits/` are historical)
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
