# Cleanup Plan

Phased plan extracted from `docs/audit/AUDIT_V1.md`. This is a read-only
plan for follow-on work. It does not delete historical docs.

## Phase 1 - Reconcile truth with runtime
- Regenerate `docs/PLATFORM_INVENTORY.md` against current HEAD.
- Run `python manage.py verify_doc_claims --only-drift` and update any
  current-doc claims that conflict with runtime.
- Update `00-START-NEXT-SESSION.md` so it no longer frames the repo as
  Session 1099.
- Align `docs/BACKEND_INVENTORY.md` so it points at the canonical
  inventory instead of repeating its own competing summary table.
- Normalize runtime ownership wording in active docs:
  - `core.settings` is the runtime settings module.
  - `run_stock_financial_agents` is a compatibility wrapper that
    delegates to `run_stock_audit_cycle`.

## Phase 2 - Remove tracked generated baggage
- Untrack `venv_ml/` and add it to `.gitignore`.
- Untrack `dist/` and `frontend/dist/` unless a specific artifact is
  required in git.
- Decide whether `.rag/corpus.jsonl` and `docs/_index.json` are source
  or generated output; if generated, move them behind a regen step and
  untrack them.
- Untrack `.pyright-after.txt`.
- Untrack `tests/artifacts/*.png` if they are regenerated test outputs
  rather than required fixtures.
- Reduce or replace `core/static/images/donkey-logo.png`.
- Split or externalize `external-project-docs/ai-content-studio/documentation/master_context_all.md`
  if it is only being vendored for convenience.

## Phase 3 - Consolidate templates and process boundaries
- Consolidate root env templates to one local example and one deploy
  example.
- Add a single index or README for `docs/audits/`, `docs/audit-2026/`,
  and `docs/audit/` so future sessions know which audit workspace is
  active.
- Keep historical docs in place, but stop citing them as current truth.
- Add a stable pointer for active session docs so the next session file
  is obvious without searching by lexicographic order.

## Phase 4 - Put guardrails in place
- Gate drift verification in CI.
- Regenerate the platform inventory after merges or schedule it as a
  post-merge check.
- Treat large binary assets and generated files as explicit artifacts
  with a regeneration path.
- Keep compatibility entrypoints like `run_stock_financial_agents`
  documented so old schedules continue to work while the canonical path
  owns the real behavior.

## Phase 5 - Navigation hygiene
- Add an index for recent handoffs if the live handoff directory keeps
  growing.
- Clarify subsystem boundaries in the active docs:
  - `core/`
  - `frontend/`
  - `mobile/`
  - `resolve_node/`
  - `ai_core/`
  - `docs/`
  - `archive/`

## Notes
- Do not delete historical docs just because they are old.
- Prefer untracking generated artifacts over rewriting historical memory.
- Runtime, config, and canonical docs win over supporting docs.
