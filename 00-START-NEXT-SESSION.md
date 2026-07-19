# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2830 CLOSED (2026-07-19; picks up as S2831) — **POINTER-INTENT REGISTRY STEP 1 SHIPPED (DORMANT SUBSTRATE + PARITY HARNESS RATIFIED)**

**Refreshed 2026-07-19 (SESSION 2830 CLOSED — Chris opened with "Please begin" after S2829 close. Sanity checks per session-open protocol all green: postgres pg15 clean; `backfill_document_status_from_docs_index --dry-run` = 0 mismatches; Pattern B/C/D queries all top-1 canonical; bare backfill correctly rejected. S2829 substrate hardening intact. Chris ratified the S2828 D-Q3/D-Q7 forward-carry recommended default: shared "pointer-intent registry" primitive **design-only** (evaluate, not build). Design doc authored at `docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md` (827 lines) per S2828 close-brief §4 shape (shape survey → shape divergence → primitive shape proposal → zero-behavior-change guarantee → migration sequence). Joint Claude+Rigby SIGN over 3 cycles reached agreement: cycle 1 → 5 Q + 5+ tool_runs → 4 AGREE-with-refinement + 1 zoom-out with 3 anti-worship concerns; cycle 2 → R1-R5 verify, Rigby caught real §7.3-vs-§5.2 inconsistency (DISAGREE); cycle 3 → §7.3 fix verified + Overall verdict "design-ready-for-Chris-D-verdict = YES". Chris D-verdict "ship step 1" ratified DORMANT substrate: `IntentMechanism` protocol + Count/SelfReference/LiteralFilename subclasses + `INTENT_MECHANISMS` registry tuple added to `core/rag_integration.py`. **`search_embeddings()` control flow UNCHANGED** (verified by `test_registry_dormant_at_step_1`). Classes are thin wrappers over existing standalone functions — zero-behavior-change by construction. 15-case parity harness + 13 registry smoke tests + 95 pre-existing Pattern C/D regression = **123/123 PASS**. Merged as PR #3273, SHA `095612efd`. `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. SEVENTY-FIFTH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first arc where the S2828 D-Q3 forward-carry (3-instance codification threshold) advanced from "candidate" to "DORMANT substrate ratified"; first joint Rigby SIGN cycle sequence to catch a real internal inconsistency at cycle 2 — anti-rubber-stamp discipline validated across 3 cycles; first parity harness using log-driven observability (DB-state-independent) captured via caplog handler direct-attached to `core.rag_integration` (Django `core` logger has `propagate: False` — root-attached caplog silently misses records); first registry primitive shipped as DORMANT with mechanical dormancy assertion.**

**S2830 ship (1 atomic PR):**

| Focus | PR / Event | SHA | Merged to | Files |
|---|---|---|---|---|
| Pointer-intent registry DORMANT substrate + design + parity harness | **#3273** | `095612efd` | main | 8 files: 1875 insertions / 1 deletion |

**Handoff:** `docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md`
**Design doc:** `docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md`
**Test coverage:** `tests/regression/rag_registry_parity/` (15 cases) + `tests/unit/test_intent_mechanism_registry.py` (13 tests)
**Metadata layer post-S2830:** ✅ 0 mismatches vs docs/_index.json (S2829 substrate intact)

**Arc state at S2830 close:**
- **Discovery-layer arc:** Pattern B (COUNT) MERGED at S2826. Pattern C (SELF_REFERENCE) MERGED at S2827. Pattern D (LITERAL-FILENAME) MERGED at S2828. Metadata drift RE-REPAIRED with substrate hardening at S2829. **Shared "pointer-intent registry" DORMANT substrate + design + parity harness RATIFIED at S2830 as Step 1 of §6 migration sequence.** Step 2 (actual behavior-preserving refactor to iterate `INTENT_MECHANISMS` inside `search_embeddings()`) explicitly deferred to separate SIGN arc + fresh Chris D-verdict per Rigby SIGN Q4 hard-boundary refinement. Post-Pattern-D Phase-0.5 baseline: 12/18 = 66.7% strict top-1 (unchanged — S2830 was DORMANT, not measurement-changing).
- **Metadata layer:** ✅ 0 mismatches (S2829 substrate hardening intact). `--apply` guard prevents unattended bulk sweeps. Sync skip-branch closure means no future drift-persistence-on-unchanged-content.
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817, unchanged).

---

## S2831 CANDIDATES

### ⭐ Recommended default direction — **Net-new engineering work** (per user-ready = platform capability memory rule + engineering-bias-over-audit memory rule)

Chris's memory-rule bias at session open is toward **net-new builds** over refactor/audit. S2830 shipped the last piece of the discovery-layer arc that could ship without live user context. Next-obvious net-new candidates:

- **BettingPage first-user trace** — real user-facing capability; verify end-to-end that the betting UI actually delivers to Chris as a first user. Per `feedback_user_ready_means_capability_not_polish`.
- **New spider / new PA tool / new dashboard tab** — actively propose 1-3 net-new candidates per session per `feedback_engineering_bias_over_audit`. Suggestions:
  - Colorado Phase 4 statute-citation content quality (real legal-doc capability)
  - A Workspace tab that exposes the RAG intent-gate diagnostics visually (real observability — leverages S2830 diagnostic field surface)
  - A new spider category or a follow-up on discord command coverage
- **Ops Console extension** — Workspace tab per `feedback_workspace_over_command_center_for_new_ui`.

### Available if Chris pivots to refactor/substrate/audit

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS` per design §6 Step 2. Requires: fresh Rigby joint SIGN (focus on log-line preservation + diagnostic-field shape + precedence + injection order) + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS post-refactor. NOT automatic follow-up of Step 1.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Playbook v0.9 amendment authoring** — sync-update-path-completeness discipline. Trigger count now potentially 3/2 (S2826 §5.2 fold + S2829 skip-branch hole + S2830 didn't add new trigger).
- **DISCOVERY policy-class mechanism** — 2 remaining rows (Q10/Q11).
- **CONCEPTUAL / PROCEDURAL semantic-general future arc** — 4 rows (Q9, Q12, Q13, Q18) — semantic-general mechanism (LLM-lite intent classifier).
- **§2.2 methodology revision** — Chris D6 said wait until all pattern mechanisms measured; Pattern B/C/D data now available.
- **13 out-of-index Document rows investigation** — Chris D6 recorded as separate post-Phase-0.5 follow-up.

**Recommended default (per engineering-bias memory rule):** Propose 1-3 net-new engineering candidates at S2831 open; gate Step 2 refactor + PR3 + Playbook amendment behind them.

---

## SESSION PIN — S2830 RETIRED (fresh mint required at S2831 open)

**Pin history (S2830):**

- `pa-f6341a9fe3de414a` (label `s2830-pointer-intent-registry-primitive-design`) minted at S2830 open; **retired at S2830 close (`force=true`, sixty-first consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2831 first-action fresh mint.

**S2831 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2830 handoff §5-§8 (implementation + lessons + follow-up carry)
# Read S2830 design doc §0 + §4 + §6 if pursuing Step 2 refactor
# Read core/rag_integration.py :483-799 (dormant classes; will drive Step 2 refactor)

# Sanity checks (must be green — S2829 substrate hardening + S2830 DORMANT invariant)
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

# Verify S2830 DORMANT invariant: registry defined, classes exist, but not wired into search_embeddings
python manage.py shell -c "from core.rag_integration import INTENT_MECHANISMS; \
  print('registry:', [m.name for m in INTENT_MECHANISMS])"
# expect: ['count', 'self_reference', 'literal_filename']

# Verify parity harness + smoke tests still green
python -m pytest tests/regression/rag_registry_parity/ tests/unit/test_intent_mechanism_registry.py -q 2>&1 | tail -3

python manage.py session_lifecycle open --label s2831-<slug>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2830 lessons to carry (also in handoff §7):**

1. **Rigby SIGN cycle 2 caught a real internal inconsistency Claude missed.** §7.3 said "30 queries" while §5.2 had been updated to coverage-criteria. Substantive DISAGREE, not rubber stamp. Anti-rubber-stamp discipline (S2777) held across 3 cycles.
2. **Log-driven parity assertions are more robust than result-row assertions for RAG.** Test-DB is empty; result rows are []; observable branches (gate active flags, drift WARN, MISS log) all live in log records regardless of DB state.
3. **Django logger propagation matters for caplog.** `core` logger has `propagate: False` in settings.py → caplog attached to root never receives records. Fix: fixture attaches `caplog.handler` DIRECTLY to `core.rag_integration` logger.
4. **Thin wrappers preserve zero-behavior-change by construction.** Registry mechanism classes call the exact same standalone functions `search_embeddings()` currently uses. No new code path — dormant means dormant.
5. **Case_14 documents current disjointness-collision behavior.** "how many where do I start" fires BOTH Pattern B AND Pattern C; precedence resolves `intent_gate_name` to 'count'. This is captured behavior, not drift. Step 2 refactor MUST preserve it.
6. **DO NOT wire the registry into search_embeddings() at Step 2 without fresh SIGN + fresh Chris D-verdict.** Rigby SIGN Q4 hard-boundary refinement makes this a mechanical invariant.
7. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract (unchanged).
8. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure (unchanged).
9. **DO NOT collapse Pattern B/C/D anchor maps, bonuses, or gate patterns** — Chris D5 distinctness contract now codified in design §3 as anti-collapse invariant.
10. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred (unchanged).
11. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards (unchanged).

---

## Twin-pointer card

📁 **Repo — S2830 artifacts:**

- **DORMANT registry substrate:** `core/rag_integration.py` (`IntentMechanism` base + `CountMechanism` + `SelfReferenceMechanism` + `LiteralFilenameMechanism` + `INTENT_MECHANISMS` tuple at `:483-799`)
- **Design doc:** `docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md` (827 lines, 3-cycle Rigby SIGN record)
- **Parity harness:** `tests/regression/rag_registry_parity/` (15 coverage-criteria cases; log-driven observability)
- **Registry smoke tests:** `tests/unit/test_intent_mechanism_registry.py` (13 tests)
- **Handoff:** `docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md`
- **Merge SHA:** `095612efd` · **PR:** #3273

🖥️ **Workspace UI — S2830 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: mint at close cascade in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` (bypasses pa_deliverables_tool diagnostic-flag bug); category `governance`; `diagnostic_status=None`.

---

## Current repository state (S2830 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `095612efd` (S2830 PR #3273 merge) + close-cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged; v0.9-candidate sync-update-path-completeness discipline still at 3/2 triggers — S2830 did not add a new trigger) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Metadata layer** | ✅ **0 mismatches** (S2829 substrate hardening intact); `--apply` guard active; sync skip-branch closure active |
| **Discovery-layer arc state** | Pattern B/C/D all shipped + retrieval integrity holds. **Registry Step 1 DORMANT substrate shipped at S2830.** Step 2 (search_embeddings refactor) deferred to separate SIGN arc + fresh D-verdict. Post-Pattern-D Phase-0.5 baseline: 12/18 = 66.7% strict top-1 (unchanged — S2830 was DORMANT). |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2831 recommended lean | Propose 1-3 NET-NEW engineering candidates at open (BettingPage first-user trace / Colorado Phase 4 / RAG diagnostic Workspace tab / etc.) per engineering-bias memory rule. Step 2 refactor + PR3 + Playbook amendment gated behind net-new. |
| Session pin | `pa-f6341a9fe3de414a` (retired at S2830 close, force=true, sixty-first consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2831 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2830 (post-#3273 merge, seventy-fifth consecutive) |
| Next move | S2831 opens with net-new engineering candidate proposal; fresh pin `s2831-<slug>`. |

---

## Recommended session-open protocol (S2831, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2830 handoff §5-§8 (implementation + lessons + follow-up carry)
4. Read S2830 design doc §0 + §4 + §6 if pursuing Step 2 refactor
5. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + bare backfill → CommandError + INTENT_MECHANISMS registry present + parity harness green)
6. `git log --oneline -8` — should show S2830 close cascade + #3273 + S2829 close cascade + #3272 + #3271
7. Mint fresh pin scoped to whatever S2831 pursues
8. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
9. **PROPOSE 1-3 NET-NEW ENGINEERING CANDIDATES** at open per `feedback_engineering_bias_over_audit`
10. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary
11. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
12. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
13. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant
14. **DO NOT relax `include_superseded=False` default** — Chris D6 retrieval integrity rule (unchanged)
15. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
16. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
17. **DO NOT auto-adopt semantic default flips** (per S2821)
18. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
19. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
20. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
21. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
22. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
23. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2831:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md`](docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md) — **S2830 handoff (current)**
3. [`docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md) — registry design + 3-cycle SIGN record + §6 migration sequence
4. [`docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md`](docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md) — S2829 substrate context
5. [`docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md`](docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md) — Pattern D + original registry framing
6. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
7. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — Pattern B/C/D Measured Boundary Summaries + retrieval-failure-diagnosis-order
8. [`tests/regression/rag_registry_parity/`](tests/regression/rag_registry_parity/) — 15-case parity harness (log-driven observability reference)
9. [`tests/unit/test_intent_mechanism_registry.py`](tests/unit/test_intent_mechanism_registry.py) — 13 registry smoke tests
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
11. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — Phase-0.5 arc row (will update at S2830 close cascade)
