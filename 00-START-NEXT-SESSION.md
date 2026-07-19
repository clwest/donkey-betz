# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2831 CLOSED (2026-07-19; picks up as S2832) — **RAG INTENT-GATE DIAGNOSTICS TAB SHIPPED (Step 2 anti-drift canary substrate)**

**Refreshed 2026-07-19 (SESSION 2831 CLOSED — Chris opened with "Please begin" after S2830 close. Sanity checks per session-open protocol all green: pg15 clean; `backfill_document_status_from_docs_index --dry-run` = 0 mismatches; Pattern B/C/D queries all top-1 canonical; bare backfill correctly rejected; INTENT_MECHANISMS registry present; parity harness + smoke tests 28/28 PASS. Per `feedback_engineering_bias_over_audit` at session open, proposed 3 net-new candidates; Chris picked #1 (RAG intent-gate diagnostics Workspace tab, leveraging S2830 DORMANT registry as observability substrate). Joint Claude+Rigby SIGN cycle 1: 5 questions with tool-grounded verdicts backed by 5+ `repo_tool` reads over `core/rag_integration.py`, `tests/regression/rag_registry_parity/`, and `frontend/src/pages/workspace/tabs/`. Rigby verdicts: Q1 STRENGTHEN (use DORMANT `INTENT_MECHANISMS[*].detect()` as canary), Q2 DISAGREE (skip log capture — concurrency-hostile), Q3 DISAGREE (ephemeral only, no DB model), Q4 DISAGREE (defer drift-WARN — scope creep), Q5 STRENGTHEN (versioned schema + best-effort `filter_summary` + GET-not-POST + hard-caps + audit-adjacency concern surfaced). Q5(c) concern (audit-adjacent, not net-new user capability) routed to Chris as paths-fork; Chris D-verdict "ship refined tab, keep it thin" ratified. Implementation: `GET /api/rag/observability/intent-gate/` endpoint with hard-capped params (limit 1..20, threshold 0.0..1.0) + registry-canary `matched_patterns` + versioned schema; `RagDiagnosticsTab.tsx` under Intelligence → RAG Diagnostics sub-tab with ephemeral URL-param state + 4 seed-query buttons + collapsible debug filter_summary panel. Coverage: 19/19 endpoint tests PASS + curl E2E on live daphne verified Pattern B/C/D + no-pattern correctness + Chris confirmed browser render on 3 live queries ("How many spiders are there", "What are the Agents capable of", "Can an Agent build an app"). Merged as PR #3275, SHA `6a893db18`. `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. SEVENTY-SIXTH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first user-facing observability surface that consumes the S2830 DORMANT registry — makes Step 2 refactor's zero-behavior-change contract enforceable at BOTH the registry AND the Workspace UI; first arc where Rigby's Q5(c) genuine concern (audit-adjacency contradicting the engineering-bias memory rule Claude used) was surfaced to Chris as paths-fork rather than swallowed into refinement edits; first close-cycle after S2830 to preserve Playbook v0.9 sync-update-path-completeness trigger count at 3/2 (no new evidence added).**

**S2831 ship (1 atomic PR):**

| Focus | PR / Event | SHA | Merged to | Files |
|---|---|---|---|---|
| RAG intent-gate diagnostics Workspace tab (Step 2 canary) | **#3275** | `6a893db18` | main | 7 files: 639 insertions / 1 deletion |

**Handoff:** `docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md`
**Endpoint:** `GET /api/rag/observability/intent-gate/` in `core/views_rag_observability.py`
**Tests:** `core/tests/test_views_rag_intent_gate_diagnostics_2831.py` (19 tests / 6 classes)
**Tab:** `frontend/src/pages/workspace/tabs/RagDiagnosticsTab.tsx`
**Wiring:** `frontend/src/pages/WorkspacePageNew.tsx` (Intelligence → RAG Diagnostics)
**Metadata layer post-S2831:** ✅ 0 mismatches vs docs/_index.json (S2829 substrate intact)

**Arc state at S2831 close:**
- **Discovery-layer arc:** Pattern B (COUNT) MERGED at S2826. Pattern C (SELF_REFERENCE) MERGED at S2827. Pattern D (LITERAL-FILENAME) MERGED at S2828. Metadata drift RE-REPAIRED with substrate hardening at S2829. Shared "pointer-intent registry" DORMANT substrate + design + parity harness RATIFIED at S2830 as Step 1. **S2831 shipped RAG Diagnostics Workspace tab consuming DORMANT registry as user-facing Step 2 anti-drift canary.** Step 2 refactor (search_embeddings iterating INTENT_MECHANISMS) still deferred to separate SIGN arc + fresh Chris D-verdict per Rigby SIGN Q4 hard-boundary; NEW invariant at S2831: Step 2 must preserve BOTH registry detect() results AND per-row intent_gate_name (RAG Diagnostics tab renders both — divergence is visible). Post-Pattern-D Phase-0.5 baseline: 12/18 = 66.7% strict top-1 (unchanged — S2831 was UI-only, not measurement-changing).
- **Metadata layer:** ✅ 0 mismatches (S2829 substrate hardening intact). `--apply` guard prevents unattended bulk sweeps. Sync skip-branch closure means no future drift-persistence-on-unchanged-content.
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817, unchanged).

---

## S2832 CANDIDATES

### ⭐ Recommended default direction — **Net-new engineering work** (per user-ready = platform capability memory rule + engineering-bias-over-audit memory rule)

Chris's memory-rule bias at session open is toward **net-new builds** over refactor/audit. S2831 shipped an observability tab (audit-adjacent, though justified as Step 2 canary). Next-obvious net-new candidates:

- **Colorado Phase 4 statute-citation content quality** — real legal-doc capability. Ship a citation-verifier spider + PA tool that flags un-cited claims in draft docs. Vertical slice: spider → tool schema + handler → Workspace Files-tab surface → demo.
- **BettingPage first-user trace** — Chris IS the first user. Instrument BettingPage end-to-end (React route → API → data → response), find the first place it breaks or shows mock data, fix that one seam. Directly serves `feedback_user_ready_means_capability_not_polish`.
- **New spider / new PA tool / new dashboard tab** — actively propose 1-3 net-new candidates per session per `feedback_engineering_bias_over_audit`.

### Available if Chris pivots to refactor/substrate/audit

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS` per design §6 Step 2. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + **NEW at S2831**: RAG Diagnostics tab must produce identical matched_patterns + per-row intent_gate_name post-refactor. Both surfaces are now anti-drift substrates.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug follow-ups surfaced by S2831:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls that should be `status=` (targeted hygiene PR)
  - LucideIcon typing drift in `WorkspacePageNew.tsx` (all 16 icons + my new `Radar` fail the same assignability check; `PrimaryTab.icon` type widening or `lucide-react` type ergonomics fix)
- **Playbook v0.9 amendment authoring** — sync-update-path-completeness discipline. Trigger count 3/2 (S2826 §5.2 fold + S2829 skip-branch hole + S2830/S2831 no new triggers). Ratifiable per S2830 §8.4 forward-carry note.
- **DISCOVERY policy-class mechanism** — 2 remaining rows (Q10/Q11).
- **CONCEPTUAL / PROCEDURAL semantic-general future arc** — 4 rows (Q9, Q12, Q13, Q18) — semantic-general mechanism (LLM-lite intent classifier).
- **§2.2 methodology revision** — Chris D6 said wait until all pattern mechanisms measured; Pattern B/C/D data now available.
- **13 out-of-index Document rows investigation** — Chris D6 recorded as separate post-Phase-0.5 follow-up.

**Recommended default (per engineering-bias memory rule):** Propose 1-3 net-new engineering candidates at S2832 open; gate Step 2 refactor + PR3 + Playbook amendment + latent-bug hygiene behind them.

---

## SESSION PIN — S2831 RETIRED (fresh mint required at S2832 open)

**Pin history (S2831):**

- `pa-01d9ef16cd6b484b` (label `s2831-rag-diagnostics-workspace-tab`) minted at S2831 open; **retired at S2831 close (`force=true`, sixty-second consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2832 first-action fresh mint.

**S2832 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2831 handoff §5-§8 (implementation + lessons + follow-up carry)
# Read S2830 design doc §0 + §4 + §6 if pursuing Step 2 refactor

# Sanity checks (must be green — S2829 substrate + S2830 DORMANT + S2831 UI tab all intact)
brew services list | grep postgres

# Verify metadata layer clean
python manage.py backfill_document_status_from_docs_index --dry-run 2>&1 | tail -8
# expect Total mismatches: 0

# Verify Pattern B/C/D top-1 canonical
python manage.py shell -c "from core.rag_integration import search_embeddings; \
  c = search_embeddings(query='where do I start', limit=1, similarity_threshold=0.4); \
  print('Pattern C:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='How many spiders', limit=1, similarity_threshold=0.4); \
  print('Pattern B:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='PLATFORM_INVENTORY', limit=1, similarity_threshold=0.4); \
  print('Pattern D:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name'))"
# expect all three top-1 canonical, NO DRIFT WARN

# Verify --apply guard works
python manage.py backfill_document_status_from_docs_index 2>&1 | tail -3
# expect: CommandError: Explicit mode required

# Verify S2830 DORMANT invariant + S2831 tab endpoint
python manage.py shell -c "from core.rag_integration import INTENT_MECHANISMS; \
  print('registry:', [m.name for m in INTENT_MECHANISMS])"
# expect: ['count', 'self_reference', 'literal_filename']

# Verify S2831 diagnostics endpoint responds
curl -s -H "Authorization: Token [REDACTED - HISTORICAL SECRET]" \
  "http://localhost:8000/api/rag/observability/intent-gate/?query=where%20do%20I%20start&limit=1&threshold=0.4" \
  | python -c "import json,sys;d=json.load(sys.stdin);print('S2831 tab:',d['matched_patterns'],d['results'][0]['file_path'] if d['results'] else '')"
# expect: ['self_reference'] 00-START-NEXT-SESSION.md

# Verify parity harness + smoke tests still green + S2831 endpoint tests
python -m pytest tests/regression/rag_registry_parity/ tests/unit/test_intent_mechanism_registry.py core/tests/test_views_rag_intent_gate_diagnostics_2831.py -q 2>&1 | tail -3

python manage.py session_lifecycle open --label s2832-<slug>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2831 lessons to carry (also in handoff §7):**

1. **Rigby's Q5(c) zoom-out concern was substantive — surfaced to Chris as paths-fork.** She flagged that this candidate was audit-adjacent, contradicting the engineering-bias memory rule Claude used. Surfacing the concern (not swallowing it into Q5 STRENGTHEN edits) let Chris make an informed D-verdict. Precedent: raise Rigby concerns that touch upstream framing assumptions to Chris even after joint agreement is reached.
2. **Registry canary as anti-drift substrate — expanded to UI.** RAG Diagnostics tab renders BOTH `matched_patterns` (from DORMANT registry) and per-row `intent_gate_name` (from search_embeddings). Any Step 2 refactor that drifts detection creates a visible divergence in the UI.
3. **Latent-bug preservation on adjacent code.** `views_rag_observability.py` has 10 pre-existing `status_code=` calls that would raise TypeError if hit; my S2831 code uses `status=` correctly but does NOT fix the 10 broken sites per "bug fix doesn't need surrounding cleanup".
4. **DO NOT couple observability to log capture** (Rigby Q2 substrate reason — concurrency-hostile).
5. **DO NOT relax hard-caps on limit/threshold** — server-side clamps are the DOS boundary.
6. **DO NOT wire the registry into search_embeddings() without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary (unchanged).
7. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract (unchanged).
8. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure (unchanged).
9. **DO NOT collapse Pattern B/C/D anchor maps, bonuses, or gate patterns** — design §3 anti-collapse invariant (unchanged).
10. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred (unchanged).
11. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards (unchanged).

---

## Twin-pointer card

📁 **Repo — S2831 artifacts:**

- **Backend view:** `core/views_rag_observability.py` (`rag_intent_gate_diagnostics` at file tail)
- **URL:** `core/urls.py` — `path('api/rag/observability/intent-gate/', ...)`
- **Tests:** `core/tests/test_views_rag_intent_gate_diagnostics_2831.py` (19 tests / 6 classes)
- **Frontend tab:** `frontend/src/pages/workspace/tabs/RagDiagnosticsTab.tsx`
- **Frontend wiring:** `frontend/src/pages/WorkspacePageNew.tsx` (Intelligence → RAG Diagnostics)
- **Barrel export:** `frontend/src/pages/workspace/tabs/index.ts`
- **Handoff:** `docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md`
- **Merge SHA:** `6a893db18` · **PR:** #3275

🖥️ **Workspace UI — S2831 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: minted at close cascade in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` (bypasses pa_deliverables_tool diagnostic-flag bug); category `governance`; `diagnostic_status=None`.

---

## Current repository state (S2831 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `6a893db18` (S2831 PR #3275 merge) + close-cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged; v0.9-candidate sync-update-path-completeness discipline still at 3/2 triggers — S2831 did not add a new trigger) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Metadata layer** | ✅ **0 mismatches** (S2829 substrate hardening intact); `--apply` guard active; sync skip-branch closure active |
| **Discovery-layer arc state** | Pattern B/C/D all shipped + retrieval integrity holds. Registry Step 1 DORMANT substrate shipped at S2830. **S2831 shipped RAG Diagnostics Workspace tab consuming DORMANT registry as user-facing Step 2 anti-drift canary.** Step 2 (search_embeddings refactor) deferred; NEW invariant: registry + tab both must preserve behavior post-refactor. Post-Pattern-D Phase-0.5 baseline: 12/18 = 66.7% strict top-1 (unchanged). |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2832 recommended lean | Propose 1-3 NET-NEW engineering candidates at open (Colorado Phase 4 / BettingPage first-user trace / new spider or PA tool) per engineering-bias memory rule. Step 2 refactor + PR3 + Playbook amendment + latent-bug hygiene gated behind net-new. |
| Session pin | `pa-01d9ef16cd6b484b` (retired at S2831 close, force=true, sixty-second consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2832 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2831 (post-#3275 merge, seventy-sixth consecutive) |
| Next move | S2832 opens with net-new engineering candidate proposal; fresh pin `s2832-<slug>`. |

---

## Recommended session-open protocol (S2832, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2831 handoff §5-§8 (implementation + lessons + follow-up carry)
4. Read S2830 design doc §0 + §4 + §6 if pursuing Step 2 refactor
5. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + bare backfill → CommandError + INTENT_MECHANISMS registry present + S2831 endpoint responds + parity harness green)
6. `git log --oneline -8` — should show S2831 close cascade + #3275 + S2830 close cascade + #3274 + #3273
7. Mint fresh pin scoped to whatever S2832 pursues
8. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
9. **PROPOSE 1-3 NET-NEW ENGINEERING CANDIDATES** at open per `feedback_engineering_bias_over_audit`
10. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary
11. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule
12. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary
13. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
14. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
15. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant
16. **DO NOT relax `include_superseded=False` default** — Chris D6 retrieval integrity rule (unchanged)
17. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
18. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
19. **DO NOT auto-adopt semantic default flips** (per S2821)
20. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
21. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
22. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
23. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
24. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
25. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2832:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md`](docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md) — **S2831 handoff (current)**
3. [`docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md`](docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md) — S2830 registry context
4. [`docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md) — registry design + 3-cycle SIGN record + §6 migration sequence
5. [`docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md`](docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md) — S2829 substrate context
6. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
7. [`core/views_rag_observability.py`](core/views_rag_observability.py) — S2831 `rag_intent_gate_diagnostics` endpoint at file tail
8. [`frontend/src/pages/workspace/tabs/RagDiagnosticsTab.tsx`](frontend/src/pages/workspace/tabs/RagDiagnosticsTab.tsx) — S2831 diagnostics tab
9. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — Pattern B/C/D Measured Boundary Summaries + retrieval-failure-diagnosis-order
10. [`tests/regression/rag_registry_parity/`](tests/regression/rag_registry_parity/) — 15-case parity harness
11. [`tests/unit/test_intent_mechanism_registry.py`](tests/unit/test_intent_mechanism_registry.py) — 13 registry smoke tests
12. [`core/tests/test_views_rag_intent_gate_diagnostics_2831.py`](core/tests/test_views_rag_intent_gate_diagnostics_2831.py) — S2831 endpoint tests
13. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
14. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — Phase-0.5 arc row
