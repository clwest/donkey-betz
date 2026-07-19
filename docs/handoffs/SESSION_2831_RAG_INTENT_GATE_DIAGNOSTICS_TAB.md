---
title: "S2831 — RAG Intent-Gate Diagnostics Workspace Tab (Step 2 Canary)"
session: 2831
date: 2026-07-19
status: shipped
authority: implementation
scope: |
  S2831 opened with sanity checks green (S2829 substrate hardening +
  S2830 DORMANT registry invariant both intact). Chris picked
  net-new-engineering candidate #1 from S2831 open menu: RAG intent-
  gate diagnostics Workspace tab under Intelligence → RAG Diagnostics.
  Joint Claude+Rigby SIGN cycle 1: 5 questions with tool-grounded
  verdicts (repo_tool reads across core/rag_integration.py + tests/
  regression/rag_registry_parity/ + frontend/src/pages/workspace/
  tabs/). Rigby: Q1 STRENGTHEN (use DORMANT registry as canary);
  Q2 DISAGREE (skip log capture); Q3 DISAGREE (ephemeral only);
  Q4 DISAGREE (defer drift-WARN); Q5 STRENGTHEN (versioned schema +
  best-effort filter_summary + GET-not-POST fresh pushback). Q5(c)
  concern surfaced (audit-adjacent, not net-new user capability);
  Chris ratified "ship refined tab, keep it thin" as Step 2 risk-
  reducer. Refined thin tab shipped: GET /api/rag/observability/
  intent-gate/ endpoint + RagDiagnosticsTab.tsx wired into
  WorkspacePageNew.tsx Intelligence primary. 19/19 endpoint tests
  PASS. E2E verified via curl on live daphne (Pattern B/C/D +
  no-pattern all correct) + Chris confirmed browser render on 3
  live queries. Merged as PR #3275, SHA `6a893db18`. `make
  recycle-all` clean post-merge per PLAYBOOK-7.4.4. SEVENTY-SIXTH
  close-cycle post-PLAYBOOK-7.4.4.
predecessor: docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md
merge_pr: 3275
merge_sha: 6a893db18
---

# S2831 — RAG Intent-Gate Diagnostics Workspace Tab (Step 2 Canary)

## §1 Session shape

Chris opened S2831 with "Please begin". Sanity checks per S2830
handoff §Recommended session-open protocol all green:

- postgres pg15 started clean
- `backfill_document_status_from_docs_index --dry-run` = 0 mismatches
- Pattern B/C/D top-1 canonical (docs/PLATFORM_INVENTORY.md for B/D,
  00-START-NEXT-SESSION.md for C)
- bare `backfill_document_status_from_docs_index` correctly rejected
  with `CommandError: Explicit mode required`
- `INTENT_MECHANISMS` registry present with names
  `['count', 'self_reference', 'literal_filename']`
- Parity harness + smoke tests: 28/28 PASS (15 parity + 13 smoke)

S2829 substrate hardening + S2830 DORMANT invariant both intact.

Per `feedback_engineering_bias_over_audit` + `feedback_user_ready_
means_capability_not_polish` memory rules at session open, Claude
proposed three net-new candidates:

1. **RAG intent-gate diagnostics Workspace tab** (leverages S2830
   DORMANT registry as observability substrate)
2. **Colorado Phase 4 statute-citation quality pass** (legal-doc
   content quality)
3. **BettingPage first-user trace** (real user-facing capability)

Chris picked candidate #1.

## §2 Root-cause investigation

N/A — this session was a net-new feature ship, not a bug triage.
No root-cause investigation performed.

## §3 Joint Claude+Rigby SIGN cycle 1 (tool-grounded, anti-rubber-stamp verified)

Routed to Rigby via `bash tools/pa_local.sh` on fresh pin
`pa-01d9ef16cd6b484b` with 5 questions:

- Q1 SHAPE: matched_patterns computation — DORMANT registry classes
  (`INTENT_MECHANISMS[*].detect(query)`) vs standalone helpers?
- Q2 SHAPE: per-request caplog handler attach for log capture yes/no?
- Q3 SCOPE: persistence — `RagDiagnosticQuery` DB model vs ephemeral?
- Q4 SCOPE: surface drift-WARN in this tab vs defer?
- Q5 ZOOM OUT: what are we accreting? Simpler surface? Is this
  drifting from engineering-bias? Fresh pushback?

Rigby returned tool-grounded verdicts backed by `repo_tool` reads of
`core/rag_integration.py`, `tests/regression/rag_registry_parity/
test_parity.py`, `tests/regression/rag_registry_parity/` tree, and
`frontend/src/pages/workspace/tabs/` (including reading
`ToolCallAnalyticsTab.tsx` as convention reference).

**Verdicts:**

- **Q1 STRENGTHEN** — Use `INTENT_MECHANISMS[*].detect()`. Makes the
  tab a **canary for Step 2** behavior-preservation; avoids creating
  a second source-of-truth surface.
- **Q2 DISAGREE** — Skip log capture in v1. Substrate reason: logger
  handler attach/detach is **global + concurrency-hostile**; risks
  cross-request log contamination; brittle coupling to log strings.
- **Q3 DISAGREE** — Ephemeral only (component state + SessionStorage
  + URL params). Adding a DB model introduces retention/governance/
  schema surface area for low value; no existing Workspace tab
  establishes a DB "query history" convention.
- **Q4 DISAGREE** — Defer drift-WARN. Surfacing it requires either
  log capture (bad per Q2) or dup detection logic in the endpoint
  (brittle) — scope creep.
- **Q5 STRENGTHEN** — (a) Version response schema; mark
  `filter_summary` as debug/best-effort not contract. (b) Simpler
  surfaces exist (PA tool / CLI); since Chris ratified Workspace-
  tab + vertical-slice, ship the tab **thin** (don't grow a debug
  console platform). (c) This is observability/audit-adjacent, not
  end-user value; justify as **Step 2 risk-reducer**, tight scope.
  (d) Fresh pushback: don't couple to logs; hard-cap server-side
  limit/threshold; clarify precedence + per-mechanism booleans;
  consider **GET vs POST** (unless Workspace convention dictates
  POST).

Anti-rubber-stamp check: `tool_runs` non-empty (5+ `repo_tool` calls
inspected before verdicts) — Rigby was NOT rubber-stamping.

Method-name spot check: Rigby said `.detect(query)`; Claude verified
against `core/rag_integration.py:517-534,587,633,707` — confirmed
`detect(query)` is the correct method.

## §4 Chris D-verdict

Rigby's Q5(c) concern (audit-adjacent, not net-new user value) was
surfaced to Chris as a paths-fork:

1. Ship refined tab per SIGN verdicts (accept audit-adjacent framing,
   justify as Step 2 canary).
2. Reroute to Colorado Phase 4 or BettingPage first-user trace
   (cleaner match to engineering-bias rule).

**Chris D-verdict:** *"ship refined tab, keep it thin"*.

## §5 Implementation shipped (PR #3275, SHA `6a893db18`)

### §5.1 Backend

`core/views_rag_observability.py` — new view `rag_intent_gate_diagnostics`
appended after existing S954/I-0302 endpoints:

- `@csrf_exempt` + `@require_http_methods(["GET"])`
- Auth: `request.user.is_authenticated` → 401 if not
- Query params: `query` (required, 400 if missing/empty), `limit`
  (default 5, hard-capped 1..20), `threshold` (default 0.4, hard-
  capped 0.0..1.0). Invalid types fall back to defaults, not 400.
- **Registry canary**: iterates `INTENT_MECHANISMS`, calls
  `m.detect(query)` once per mechanism, computes `matched_patterns`
  and `intent_gates` dict from the results.
- Calls `search_embeddings(query, limit, similarity_threshold)` to
  get retrieval rows.
- Returns JSON with `schema_version='1'`, `matched_patterns`,
  `intent_gates`, `results` (rank + file_path + intent_gate_name +
  intent_gate_fired + similarity_score + chunk_id + chunk_index +
  category + document_class + title), `filter_summary`, and a
  `notice` marking `filter_summary` as best-effort debug.

`core/urls.py` — added `rag_intent_gate_diagnostics` to the import
list from `core.views_rag_observability` + registered
`path('api/rag/observability/intent-gate/', ...)` after
`.../classify/`.

**Latent bug NOT touched (out of scope):** the existing views in
`views_rag_observability.py` all call `api_error(..., status_code=NNN)`
but `api_helpers.api_error` takes `status=` not `status_code=`. My
new view uses `status=` correctly. Fixing the 10 pre-existing sites
is a separate cleanup.

### §5.2 Tests

`core/tests/test_views_rag_intent_gate_diagnostics_2831.py` — 19 tests
across 6 test classes:

- `TestRegistryCanary` (4 tests) — matched_patterns correctness for
  Pattern B/C/D + no-pattern queries.
- `TestHardCaps` (6 tests) — limit clamped to 1..20 + threshold
  clamped to 0.0..1.0 + defaults on invalid types.
- `TestValidation` (3 tests) — missing/empty/whitespace-only query
  returns 400.
- `TestAuth` (1 test) — unauthenticated returns 401.
- `TestContract` (4 tests) — schema_version present, notice marks
  filter_summary as debug, response shape keys, filter_summary
  echoes intent_gates.
- `TestMethod` (1 test) — POST returns 405.

**19/19 PASS.**

### §5.3 Frontend

`frontend/src/pages/workspace/tabs/RagDiagnosticsTab.tsx` — new tab
component:

- Query input + limit slider (1..20) + threshold slider (0.0..1.0)
- Submit → useQuery hook → GET `/api/rag/observability/intent-gate/`
- Renders:
  - Intent-gate badges (COUNT / SELF_REFERENCE / LITERAL_FILENAME)
    with active/idle state
  - `matched_patterns` as literal JSON below badges
  - Results table (rank, file_path, intent_gate, similarity, category)
  - Collapsible `filter_summary` debug panel with the not-a-stable-
    contract notice inline
- **Ephemeral state** (Rigby Q3): query + limit + threshold persist
  to URL params (`?rq=...&rl=5&rt=0.40`); no DB model.
- 4 seed-query buttons: Pattern B (count), Pattern C (self-ref),
  Pattern D (filename), No pattern.

`frontend/src/pages/workspace/tabs/index.ts` — added
`export { RagDiagnosticsTab } from './RagDiagnosticsTab'` barrel.

`frontend/src/pages/WorkspacePageNew.tsx`:
- Imported `RagDiagnosticsTab` + `Radar` lucide icon
- Added `{ id: 'rag-diagnostics', label: 'RAG Diagnostics', icon: Radar }`
  as fourth sub-tab under Intelligence primary
- Added render branch:
  `{activePrimary === 'intelligence' && activeSub === 'rag-diagnostics' && (<RagDiagnosticsTab />)}`

Type-check: 0 new tsc errors from RagDiagnosticsTab.tsx / index.ts.
Pre-existing LucideIcon assignability warnings on WorkspacePageNew.tsx
lines 142-153 apply identically to `Radar` — pre-existing codebase
type-def drift, not new breakage.

Frontend built successfully (3.28s, 2.7MB bundle).

## §6 E2E verification

### §6.1 Curl on live daphne

| Query | matched_patterns | Top result | intent_gate_name |
|---|---|---|---|
| "How many spiders do we have" | `['count']` | docs/PLATFORM_INVENTORY.md | count |
| "where do I start" | `['self_reference']` | 00-START-NEXT-SESSION.md | self_reference |
| "PLATFORM_INVENTORY" | `['literal_filename']` | docs/PLATFORM_INVENTORY.md | literal_filename |
| "celery worker configuration" | `[]` | (semantic-only, no gate) | None |

### §6.2 Chris browser verification

Chris hit `/workspace?tab=intelligence&sub=rag-diagnostics` and ran
three real queries:

1. "How many spiders are there"
2. "What are the Agents capable of"
3. "Can an Agent build an app"

All three rendered correctly. Chris confirmed "browser seems to be
working correctly" — `feedback_last_mile_ui` satisfied.

## §7 Lessons to carry

1. **Rigby's Q5(c) concern was substantive.** She flagged that this
   candidate was observability/audit-adjacent, not net-new user
   capability — directly contradicting the memory-rule bias Claude
   used to propose it. Surfacing the concern to Chris (not swallowing
   it into the Q5 STRENGTHEN edits) let him make an informed
   D-verdict rather than assume the recommendation was aligned.
   Precedent: raise Rigby concerns that touch upstream framing
   assumptions to Chris even after joint agreement is reached, so
   the D-verdict is genuinely informed.

2. **Registry canary as anti-drift substrate.** Using DORMANT
   `INTENT_MECHANISMS[*].detect()` in a user-facing surface means
   any Step 2 refactor that drifts detection behavior will produce
   a visible divergence between `matched_patterns` (from the
   registry) and per-row `intent_gate_name` (from search_embeddings
   control flow). This is a NEW anti-drift substrate that didn't
   exist before S2831 — Step 2 authors have to preserve BOTH surfaces.

3. **Latent-bug preservation on adjacent code.** `views_rag_observability.py`
   has 10 pre-existing `status_code=` calls that would raise
   TypeError if invoked (`api_helpers.api_error` takes `status=`).
   Per the "bug fix doesn't need surrounding cleanup" rule, my S2831
   PR uses the correct kwarg but does NOT fix the 10 broken sites.
   Follow-up candidate for a targeted hygiene PR.

4. **Frontend LucideIcon type-def drift is codebase-wide.** All
   icons in `primaryTabs` (lines 142-153 of WorkspacePageNew.tsx)
   fail the same LucideIcon → ComponentType check. Adding `Radar`
   inherits the pre-existing drift; not new breakage. Follow-up
   candidate for a targeted `lucide-react` type ergonomics fix.

5. **DO NOT couple observability tab to log capture.** Per Rigby Q2
   substrate reason: attach/detach handlers per-request is
   concurrency-hostile and creates cross-request contamination
   risk. If drift-WARN surfacing is later added (Rigby Q4 deferred),
   compute WARN conditions server-side from registry state, not from
   log tailing.

6. **DO NOT relax hard-caps on limit/threshold.** Server-side hard-
   caps (1..20 + 0.0..1.0) are the boundary that prevents
   observability requests from becoming DOS vectors. Any future
   "bulk probe" mode requires a separate endpoint + separate SIGN.

7. **DO NOT wire the registry into `search_embeddings()`** — S2830
   Step 2 hard boundary (unchanged).

8. **DO NOT relax `--apply` guard, sync skip-branch closure, or
   include_superseded default** — S2829 substrate contracts
   (unchanged).

## §8 Follow-up carry

### §8.1 Step 2 refactor (S2830 deferred, unchanged)

Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS` per
design §6 Step 2. Requirements before opening:

- Fresh Rigby joint SIGN (log-line preservation + diagnostic-field
  shape + precedence + injection order)
- Fresh Chris D-verdict
- Golden-file parity fixture PASS
- 95/95 Pattern C+D pytest PASS post-refactor
- **New at S2831**: RAG Diagnostics tab must produce identical
  `matched_patterns` + per-row `intent_gate_name` post-refactor.
  Both surfaces are now anti-drift substrates.

### §8.2 Latent bugs surfaced by S2831 (candidate follow-ups)

- **`views_rag_observability.py` `status_code=` → `status=`** — 10 pre-
  existing broken calls. Targeted hygiene PR. Fix keyword only; do
  not otherwise refactor the file.
- **LucideIcon typing drift in WorkspacePageNew.tsx** — pre-existing
  on all 16 icons; my `Radar` addition inherits it. Targeted typing
  ergonomics fix or `PrimaryTab.icon` type widening.

### §8.3 Other open follow-ups (unchanged from S2830)

- **PR3 S2829** (canonical-anchor invariant + divergent-retrieval-
  stack diagnostic) — still deferred as separate architectural arc.
- **13 out-of-index Document rows** — still deferred per Chris D6.
- **Playbook v0.9 amendment authoring** — sync-update-path-completeness
  discipline. Trigger count 3/2 (S2826 §5.2 fold + S2829 skip-branch
  hole + S2830/S2831 did not add). Ratifiable per S2830 §8.4 note.
- **Colorado Phase 4** — statute-citation content quality.
- **BettingPage first-user trace** — real user-facing capability.
  Deferred at S2831 open when Chris picked candidate #1.

## §9 Twin-pointer card

📁 **Repo — S2831 artifacts:**

- **Backend view**: `core/views_rag_observability.py`
  (`rag_intent_gate_diagnostics` at file tail after
  `_classify_document`)
- **URL**: `core/urls.py` — `path('api/rag/observability/intent-gate/', ...)`
- **Tests**: `core/tests/test_views_rag_intent_gate_diagnostics_2831.py`
  (19 tests, 6 classes)
- **Frontend tab**: `frontend/src/pages/workspace/tabs/RagDiagnosticsTab.tsx`
- **Frontend wiring**: `frontend/src/pages/WorkspacePageNew.tsx`
  (Intelligence → RAG Diagnostics sub-tab)
- **Barrel export**: `frontend/src/pages/workspace/tabs/index.ts`
- **Merge SHA**: `6a893db18` · **PR**: #3275
- **This handoff**: `docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md`

🖥️ **Workspace UI — S2831 twin-pointer deliverables:**

To mint at close cascade (ORM-direct per
`feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`):

- **Content mirror**: `initiative_phase_doc` in Donkey Betz workspace
  (`b4503364-2573-4401-9e28-61a739e0ce50`), category `governance`
  (feature-ship engineering truth).
- **Ratification envelope**: `ratification_record` in Donkey Betz
  workspace, category `governance`, `diagnostic_status=None`.

## §10 Current repository state (S2831 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `6a893db18` (S2831 PR #3275 merge) + close-cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Discovery-layer arc state | Pattern B/C/D shipped (S2826/S2827/S2828); metadata drift substrate-hardened (S2829); pointer-intent registry DORMANT Step 1 shipped (S2830); **S2831 shipped RAG Diagnostics Workspace tab as Step 2 canary**. Step 2 refactor still deferred; ratified anti-drift substrate expanded (registry + tab both must preserve behavior post-refactor). |
| Metadata layer | ✅ 0 mismatches; `--apply` guard active; sync skip-branch closure active (S2829 substrate intact) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2830 pin | `pa-f6341a9fe3de414a` (retired at S2830 close) |
| S2831 pin | `pa-01d9ef16cd6b484b` (label `s2831-rag-diagnostics-workspace-tab`, retired at S2831 close, force=true, sixty-second consecutive per S2770+) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2832 open) |
| Session close cascade | THIS session — S2831 |
| Docs cascade | 4-step per `feedback_docs_cascade_at_every_close` (build_docs_index / build_rag_corpus / sync_docs_index_to_documents / embed_documents --all-unembedded) + build_docs_provenance |
| Recycle post-merge | ✅ `make recycle-all` executed after #3275 merge (PLAYBOOK-7.4.4, seventy-sixth consecutive) |
