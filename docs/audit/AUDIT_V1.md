# Audit V1

> Audit of the unified-donkey-betz repository's load-bearing
> infrastructure: docs, anchors, repo hygiene, and source-of-truth
> conflicts. Runtime and config win over docs. Historical docs are
> memory, not current truth.

## Metadata
- Date: 2026-05-03
- Branch / HEAD: `feature/stock-financial-rotation-fix` / `ba03c3d0`
- Context-kit flow run: `inspect`, `verify --write`, `audit --write`,
  `hotpath`, `doctor`
- Verification summary: 0 verified, 2 doc-only, 5 conflict
- Scope note: no code changes were made for this audit

## Executive Summary
- The repo is buildable, but the documentation layer is materially stale
  and the repository still tracks large generated artifacts and a full
  virtualenv.
- The strongest load-bearing docs are present, but several active docs
  still describe a prior session state or ambiguous ownership.
- The main runtime truth is in `core/settings.py`, `core/tasks.py`, and
  the current `core/services/doc_claim_verification.py` report, not the
  session memory docs.

## P0

### 1. Tracked virtualenv and generated outputs are inflating the repo
Real repo issue.
- `venv_ml/` is tracked in git. `context-kit inspect` reports 311 files.
- `dist/` is tracked in git.
- `frontend/dist/` is present as tracked build output.
- Large generated artifacts are also tracked: `.rag/corpus.jsonl`,
  `docs/_index.json`, `.pyright-after.txt`, and `tests/artifacts/*.png`.
- `context-kit hotpath` shows the largest offenders as
  `core/static/images/donkey-logo.png` (24.00 MB),
  `external-project-docs/ai-content-studio/documentation/master_context_all.md`
  (17.86 MB), `.rag/corpus.jsonl` (6.20 MB), and
  `venv_ml/share/jupyter/nbextensions/jupyter-js-widgets/extension.js.map`
  (3.44 MB).
- Impact: slower clones, larger diffs, noisier searches, and worse
  context quality for agents.

### 2. The top-level session entry doc is stale
Real repo issue.
- `00-START-NEXT-SESSION.md:20-30` still frames the repo as "Session 1099"
  and centers the old DeliverableAppend canary window.
- Current HEAD is `ba03c3d0` and the recent branch work fixed the
  stock-financial rotation path.
- This is the highest-visibility doc in the repo; stale framing here
  causes the next session to start from an out-of-date premise.

## P1

### 3. Verification output shows real doc drift, but only at the doc layer
Real repo issue.
- `docs/verification/VERIFY_REPORT.md` reports:
  - `DOC_ONLY`: API count claims, frontend page count claims
  - `CONFLICT`: agents count claims, spiders count claims, tracked
    generated artifacts, Celery beat schedule ownership, Django settings
    module
- The conflicts are not runtime failures. They are doc-vs-runtime
  mismatches that should be reconciled against the current code.
- Canonical docs under `.context-kit/verify.yaml` are the ones that need
  to be corrected first.

### 4. Celery schedule ownership is split between alias and canonical task
Real repo issue, but the compatibility alias is intentional.
- `core/tasks.py:9439-9450` keeps `run_stock_financial_agents()` as a
  thin wrapper that logs and delegates to `run_stock_audit_cycle()`.
- `core/settings.py:1124` still routes `core.tasks.run_stock_financial_agents`
  to the `agents` queue.
- `core/settings.py:1192` routes `core.tasks.run_stock_audit_cycle` to the
  `long_running` queue.
- The wrapper is backward-compatible and should remain, but the schedule
  ownership now spans two task names. That should be documented as a
  compatibility path, not treated as a second independent implementation.

### 5. Django settings source of truth is split in docs vs runtime
Real repo issue.
- Runtime entrypoints point at `core.settings`:
  - `core/asgi.py`
  - `core/celery.py`
  - `core/wsgi.py`
  - `manage.py`
- `.env.example:9` still declares `DJANGO_SETTINGS_MODULE=backend.settings`.
- The doc/config surface should converge on the actual runtime module
  (`core.settings`) instead of preserving an older module path in the
  example env file.

### 6. Environment template drift is real and avoidable
Real repo issue.
- Root-level env templates include:
  - `.env`
  - `.env.example`
  - `.env.production`
  - `.env.railway`
- The canonical templates are now `.env.example` for local use and
  `.env.railway` for Railway deployment.
- `.env.production` remains a transitional fallback snapshot until the cleanup
  pass removes it or deliberately keeps it.
- This is a maintenance hazard because different docs and scripts can
  point at different templates.

### 7. Docs/RAG/context layer is large enough to be a runtime risk
Real repo issue, not a tool bug.
- `docs/` contains 1,900+ markdown files and 662 session handoffs.
- `.rag/corpus.jsonl` exists and is large enough to matter for search
  and retrieval behavior.
- `docs/_index.json` is also large and appears to be generated.
- Risk: if active docs drift, retrieval-backed systems can amplify stale
  claims instead of correcting them.

### 8. Historical docs are not the same thing as current truth
Real repo issue when active docs are allowed to cite them as current.
- The archive trees (`archive/`, `docs/archive/`, `external-project-docs/`)
  are useful memory, but they should not be treated as runtime truth.
- Several numbers in the verifier output are clearly historical drift.
- This is not a reason to delete historical docs. It is a reason to stop
  promoting them as current state.

## P2

### 9. There are multiple audit workspaces with no single index
Process risk.
- `docs/audits/`
- `docs/audit-2026/`
- `docs/audit/`
- The current audit lives in `docs/audit/`, but the other two still exist
  and can confuse future agents.

### 10. The docs root is too broad for easy orientation
Process risk.
- `docs/` has a very large top-level surface area and mixes anchors,
  work-in-progress material, and archive-like material.
- This is not a deletion recommendation. It is a sign that the root needs
  better navigation aids and stronger canonical pointers.

### 11. `run_stock_financial_agents` is a compatibility path, not dead code
Compatibility note.
- The task entrypoint still exists and should remain because schedules
  and callers may still invoke it.
- The implementation now delegates to `run_stock_audit_cycle()` and the
  new regression test verifies that behavior without touching the DB.

## Tool Limitations
- `context-kit verify --write` and `context-kit audit --write` can
  produce or skip output based on file existence; the tool skipping the
  write is not a repo problem.
- The verifier reports doc claims by pattern matching against runtime
  evidence. It is useful for drift detection, but it is not a runtime
  execution engine.
- `context-kit hotpath` tells us which files are large, but not whether a
  given large file is intentionally generated. The repo owner still needs
  to decide source-vs-artifact ownership.

## Subsystem Boundaries
- `core/`: Django runtime, Celery tasks, settings, agents, services.
- `frontend/`: React/Vite UI.
- `mobile/`: separate JavaScript app surface.
- `resolve_node/`: Node-based integration surface.
- `ai_core/`: spider and AI-adjacent utilities.
- `external-project-docs/`: vendored external context; treat as borrowed
  material, not repo truth.
- `archive/`: historical memory.
- `docs/`: active documentation and retrieval layer.
- `.rag/`: retrieval corpus.

## Bottom Line
- The repo is usable and buildable, but it is not clean.
- The most urgent work is removing tracked generated baggage and
  refreshing active docs to match current runtime truth.
- The stock-financial fix itself is safe and backward-compatible; it is
  not a blocking issue for this audit.
