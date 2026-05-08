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

## Phase 6 - Label dormant / partial / broken-but-unreachable code (Session 1113)

Annotation-only follow-up to the deeper-review map. Each touched file
gained a top-of-file banner classifying it as **PARTIAL**,
**ARCHIVE-CANDIDATE**, **BROKEN-BUT-UNREACHABLE**, or
**ACTIVE-COMPANION-PARTIAL**. No runtime behavior changes, no
deletions, no archival moves, no route wiring, no model migrations.

Banners point at `docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md` for
the full classification rationale, and they exist precisely so the
next contributor (human or agent) doesn't re-run the audit.

| Path | Label | Decision pending |
|---|---|---|
| `agents/urls_deployment.py` | PARTIAL | Wire into `core/urls.py` or treat as dormant (PR-E) |
| `agents/views_deployment.py` | PARTIAL | Same as `urls_deployment.py` |
| `agents/views_deployment_execute.py` | PARTIAL | Same |
| `agents/views_deployment_execute_improved.py` | PARTIAL | Same; only external consumer is `tests/spiders/test_agent_modes.py` |
| `agents/views_all_agents.py` | PARTIAL | Same |
| `agents/views_all_agents_simple.py` | PARTIAL | Same |
| `sports_betting/__init__.py` | ARCHIVE-CANDIDATE | Future surface or abandoned experiment? |
| `intelligence/urls_ai_jobs.py` | BROKEN-BUT-UNREACHABLE | Archive after revival check |
| `ai_core/intelligence/monitoring_dashboard.py` | BROKEN-BUT-UNREACHABLE | Archive (with the rest of the family) |
| `ai_core/intelligence/testing_suite.py` | BROKEN-BUT-UNREACHABLE | Archive (same family) |
| `revenue/models.py` | ACTIVE-COMPANION-PARTIAL | Rehome models in installed app or accept verifier as Redis-only |
| `ai_core/intelligence/orchestration.py` | PARTIAL | Revive (`MLPipeline = EnhancedMLPipeline` shim) or mark dormant |
| `ml_pipeline/__init__.py` | (note only) | Documents the missing `ml_pipeline.pipeline` shim consumed by the three `ai_core/intelligence/*` modules above |

Verification snapshot at the time of this phase:

- `python manage.py check` → `System check identified no issues (0 silenced)`
- Smoke imports for every banner-touched module match their classifications: PARTIAL/note/archive-candidate import cleanly, BROKEN-BUT-UNREACHABLE fail with the exact errors documented in the banner text, ACTIVE-COMPANION-PARTIAL raises the documented `RuntimeError`.
- `python scripts/verify_repo_guardrails.py --inventory-advisory` → 0 blocking, 4 DOC_ONLY (advisory), 2 VERIFIED.
- `context-kit verify --json` → CONFLICT 0.

## Phase 7 - Document active-but-underdocumented modules (Session 1114, PR-D)

PR-D from the Session 1111 deeper-review queue. Docs-only — no code
changes. New topic doc:
[`docs/topics/active-module-ownership-map.md`](../topics/active-module-ownership-map.md)
covers all five Session 1111 PR-D items in one cohesive map:

| Subsystem | Doc section |
|---|---|
| `revenue/revenue_verifier.py` (active Redis-only verifier) | §1 — including failure semantics + relationship to the Session 1113 `revenue/models.py` companion banner |
| `advisors/registry.py` + `advisors/llm_advisor_system.py` | §2 — corrects the Session 1111 namespace-package claim (real `__init__.py` exists), enumerates 16+ active importers, advises against relocation |
| Top-level `llm/` (52 LOC Ollama helper) | §3 — explicitly contrasts with `core/services/agent_llm_router.py`, `core/services/llm_provider_registry.py`, `core/services/llm_call_wrapper.py` |
| `core/tasks_*.py` (12 modules, ~31.7k LOC) | §4 — documents the `_impl_*` lazy-import wrapper pattern in `core/tasks.py` and why only `core.tasks_agents` is in `app.conf.imports` |
| `core/urls.py` (4,750 LOC) vs `core/urls_unified.py` (118 LOC) | §5 — corrects Session 1111's swap; `core/urls.py` is the entrypoint *and* the monolith |

`docs/topics/README.md` updated with a new row pointing at the file so
the embedding pipeline picks it up alongside the other topic docs.

PR-D status: **complete**. PR-E (decisions: revive `ml_pipeline.pipeline`
shim, wire `agents/urls_deployment.py`, rehome `revenue/models.py`)
remains gated on Rigby/Chris.

## Notes
- Do not delete historical docs just because they are old.
- Prefer untracking generated artifacts over rewriting historical memory.
- Runtime, config, and canonical docs win over supporting docs.
