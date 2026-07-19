# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2824 CLOSED (2026-07-19 early morning; picks up as S2825) — **PHASE-0.5 B2 ROUTER BUILD SHIPPED (advisory-only, flag-guarded, byte-identical when off)**

**Refreshed 2026-07-19 early (SESSION 2824 CLOSED — Chris R7 build authorization from S2823 executed. Single feature PR: `core/services/phase_0_5_router.py` (new module) + `core/services/phase_0_5_classifier_a.py` (mirror, drift-guarded) + `core/settings.py` (3 flag additions) + `core/services/td_handlers_ops.py:5905` (flag-guarded diff, byte-identical when off) + `persistence.Phase0_5RouterEvent` model + migration 0009 + `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py` extraction script + `core/tests/test_phase_0_5_router.py` (18 tests OK) + 2 empty seed JSONL files. Rigby joint SIGN cycle-1 caught Q4 F-BLOCKING (log-on-error missing); fix applied same-turn (try/except/finally + `retrieval_error` + `retrieval_exception_type` fields). Rigby cycle-2 CLEAR across all 6 questions with 6 refinements applied (Q1 mirror drift-guard + Q3 byte-identical safe pattern + Q4 log-on-error + Q5 non-recursion separation + Q6-A window boundary events + Q6-B integrity-stop markdown writer + advisory surface). All 18 contract tests pass. Live flag-off Rigby validation confirmed byte-identical envelope. Live flag-on shell validation confirmed JSONL SoT + Django mirror + categorical-only routing across 3 distinct family shapes (COUNT/IDENTITY/AMBIGUOUS). `make recycle-all` executed clean. SIXTY-NINTH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first Phase-0.5 substrate code execution session; first Rigby build-plan F-BLOCKING catch on an execution PR; first advisory-only feature shipped under a Chris R7 constitutional-package framing.**

**S2824 ship (1 feature PR + 1 close cascade PR):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Phase-0.5 B2 router build (single feature PR) | **#TBD** · (SHA at merge) | main | 10 files: module + mirror + settings + handler diff + model + migration + tests + extraction script + 2 seed JSONL |
| Close cascade | **#TBD** · (SHA at merge) | main | handoff + implementation log + 00-START update + docs cascade |

**Handoff:** `docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md`
**Implementation log:** `docs/research/implementation/IMPLEMENTATION_LOG_2026-07-19_s2824_phase0_5_b2_build_shipped.md` (S2823 envelope was frozen per PLAYBOOK-6.10.9; this log is a separate additive artifact)
**Constitutional anchor:** `docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md` (S2823 frozen; R1-R7 verbatim)
**Router substrate:** `core/services/phase_0_5_router.py` + `core/services/phase_0_5_classifier_a.py`
**Handler diff:** `core/services/td_handlers_ops.py:5905+`
**Test suite:** `core/tests/test_phase_0_5_router.py` (18 tests OK)
**JSONL SoT:** `logs/phase_0_5_router.jsonl` (empty at ship)
**Integrity events:** `logs/phase_0_5_integrity_events.jsonl` (empty at ship) + `docs/research/discovery_layer/PHASE_0_5/integrity_stops/` (populated at runtime)
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 145 rows (unchanged from S2823 close; S2824 was implementation execution, no zoom-out folds required).

**Arc state at S2824 close:**
- **Discovery-layer arc:** **Phase-0.5 substrate SHIPPED**. Feature flag default OFF preserves current-best retrieval behavior; flag ON activates advisory-only instrumentation. B1 balanced P1 harvest now unblocked for S2825 execution.
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅.
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817). §8 item #1 discovery-layer FULL through Phase-0.5 substrate ship; item #3 Playbook v0.9 OP3 amendment still queued (10/10 triggers ready).

---

## S2825 CANDIDATES

### ⭐ Recommended default direction

1. **⭐ Execute balanced P1 harvest per B1 §6** — now unblocked. Instrumentation
   dispatches run harvest against the flag-on endpoint under a fresh measurement
   window (`window_type='harvest_phase'`). Router advisories persist to JSONL
   SoT + Django mirror. Phase-0.5 measurement report authored from
   `analyze_router_log.py` output after harvest closes.
   - **Concrete first steps at S2825 open:**
     1. Set `PHASE_0_5_ROUTER_ENABLED=true` in `.env` + recycle workers
     2. Mint fresh measurement window via router API with `window_type='harvest_phase'`
     3. Execute B1 §6 harvest plan queries (balanced P1 targets across families)
     4. Verify JSONL + model mirror populate correctly + no integrity events triggered
     5. Author interim measurement report snapshot to gauge min-N progress
     6. Handoff + docs cascade

### Available if Chris pivots

- **Playbook v0.9 amendment authoring** — 10/10 triggers well past codification threshold
- **Playbook v0.10-candidate R1 provenance discipline** — 2/2 triggers as of S2823 (potentially 3/3 now with S2824 build execution provenance if Chris rules it corroborates)
- **Playbook v0.11-candidate epistemic-integrity discipline** — 1/2 triggers (S2823 Chris R6 runtime-vs-post-hoc; watch for second)
- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability
- **Stock Intelligence** — end-to-end verify (dashboard/brief/alert pipeline)

**Recommended default:** Item #1 balanced P1 harvest execution.

---

## SESSION PIN — S2824 RETIRED (fresh mint required at S2825 open)

**Pin history (S2824):**

- `pa-b47defa04e9249f6` (label `s2824-phase0-5-b2-build`) minted at S2824 open; **retired at S2824 close (`force=true`, fifty-fifth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2825 first-action fresh mint.

**S2825 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2824 handoff — §3 Rigby cycle-1 F-BLOCKING + cycle-2 CLEAR, §5 live validation, §9 lessons
# Read S2824 implementation log — §3 R1-R7 mapping + §4 Rigby refinements mapping
# Read S2823 frozen envelope §15 R1-R7 verbatim (constitutional constraints)
# Read B1 BALANCED_P1_HARVEST_PLAN §6 for harvest execution shape

# Sanity checks
brew services list | grep postgres

# Verify ledger baseline (expect 145 unchanged from S2823 close)
wc -l logs/zoom_out_classifications.jsonl

# Verify router substrate present
ls core/services/phase_0_5_router.py core/services/phase_0_5_classifier_a.py
python manage.py test core.tests.test_phase_0_5_router -v0 2>&1 | tail -3
# expect "Ran 18 tests in ... OK"

python manage.py session_lifecycle open --label s2825-balanced-p1-harvest
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2824 lessons to carry (also in handoff §9):**

1. **Rigby cycle-1 F-BLOCKING catches keep constitutional discipline honest under implementation pressure.** Q4's log-on-error catch prevented shipping a measurement-bias hole that would corrupt min-N gating for Class B/C triggers.
2. **Same-turn F-BLOCKING resolution extends into implementation.** The S2823 multi-round SIGN pattern worked identically for build execution.
3. **Byte-identical safe pattern (Q3) is the correct discipline.** Preserving existing envelope block verbatim inside a flag-off early-return removes accidental drift risk.
4. **JSONL + Django mirror + event_id idempotency is a clean R4 shape.** Separate integrity-events JSONL prevents recursion structurally.
5. **Contract tests locking R1-R7 make constitutional constraints CI-verifiable.** Class A T1 (no numeric confidence field) is enforced structurally by the dataclass shape + static test.

---

## Twin-pointer card

📁 **Repo — S2824 artifacts:**

- **Router module:** `core/services/phase_0_5_router.py`
- **Classifier mirror:** `core/services/phase_0_5_classifier_a.py`
- **Handler diff:** `core/services/td_handlers_ops.py:5905+`
- **Settings:** `core/settings.py` (`PHASE_0_5_ROUTER_ENABLED` + measurement window enum + N)
- **Model:** `persistence.Phase0_5RouterEvent`
- **Migration:** `persistence/migrations/0009_phase0_5routerevent.py`
- **Tests:** `core/tests/test_phase_0_5_router.py` (18 tests OK)
- **Extraction script:** `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py`
- **JSONL SoT:** `logs/phase_0_5_router.jsonl` — created at runtime by router (`logs/` gitignored)
- **Integrity events:** `logs/phase_0_5_integrity_events.jsonl` — created at runtime
- **Integrity-stop dir:** `docs/research/discovery_layer/PHASE_0_5/integrity_stops/` (populated at runtime)
- **Handoff:** `docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md`
- **Implementation log:** `docs/research/implementation/IMPLEMENTATION_LOG_2026-07-19_s2824_phase0_5_b2_build_shipped.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 145 rows unchanged
- **Merge SHAs:** filled at feature PR + close cascade PR merges

🖥️ **Workspace UI — S2824 has NO new twin-pointer workspace deliverable this session** — implementation execution sessions preserve envelope + implementation log in `docs/research/implementation/` as authoritative; workspace mirror deferred per S2823 pattern. Group 2700 arc's workspace deliverable (`37d6ca76-89c3-4966-8f4c-decc52ce8169`) remains authoritative for the /docs/ restructuring arc.

---

## Current repository state (S2824 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2824 feature PR merge + close cascade PR merge — SHAs filled at merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment 10/10 corroborated; v0.10 R1 provenance discipline 2-3/2 triggers; v0.11 epistemic-integrity 1/2 triggers**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ |
| **Group 2700 arc state** | **ARC CLOSED (S2817).** §8 item #1 discovery-layer FULL through Phase-0.5 substrate ship. |
| **Discovery-layer arc state** | Lexical FEATURE COMPLETE; semantic EVALUATED; Phase-0 METHODOLOGY VALIDATED; **Phase-0.5 SUBSTRATE SHIPPED (advisory-only, flag-guarded, byte-identical when off); balanced P1 harvest unblocked for S2825** |
| Emergent candidates | S2825 balanced P1 harvest execution (sole recommended); Playbook v0.9 (10/10); v0.10 R1 provenance (2-3/2); v0.11 epistemic-integrity (1/2); Colorado / BettingPage / Stock Intelligence available |
| Session pin | `pa-b47defa04e9249f6` (retired at S2824 close, force=true, fifty-fifth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2825 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2824 open (FRESH) |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2824 close-cascade recycle-all (clean, surviving=none) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 145 rows unchanged (S2824 was implementation execution) |
| /docs/ restructuring | **ARC CLOSED (S2817).** §8 item #1 discovery-layer FULL through Phase-0.5 substrate ship. |
| Next move | S2825 opens balanced P1 harvest execution per B1 §6 — router is ready + flag defaults OFF for safety. Fresh pin `s2825-balanced-p1-harvest`. |

---

## Recommended session-open protocol (S2825, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2824 handoff §3 Rigby SIGN + §5 live validation + §9 lessons
4. Read S2824 implementation log §3 R1-R7 mapping + §4 Rigby refinements mapping
5. Read B1 `BALANCED_P1_HARVEST_PLAN.md` §6 for harvest execution shape
6. Sanity checks (brew postgres + ledger row count 145 + `python manage.py test core.tests.test_phase_0_5_router -v0` should be OK)
7. `git log --oneline -6` — should show S2824 feature PR + close cascade + S2823 close
8. Mint fresh pin scoped `s2825-balanced-p1-harvest`
9. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
10. **BALANCED P1 HARVEST EXECUTED UNDER R1-R7 CONSTRAINTS** per S2823 constitutional package (R1 advisory-only / R2 measurement window canonical / R3 single surface / R4 durable evidence / R5 additive non-breaking / R6 epistemic integrity / R7 downstream discipline)
11. **UPPER BOUND / precision qualifiers** required for count claims
12. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
13. **Anchor-verify at every scope decision point** (22-session trend)
14. **DO NOT patch the frozen lexical `top_k` policy** (per Chris S2820)
15. **DO NOT auto-adopt semantic default flips** (per S2821)
16. **DO NOT build RRF or global fusion during Phase-0.5** (per Chris R6 from S2821 + B2 R1 advisory-only)
17. **DO NOT delegate production routing decisions** — advisory only per Chris R2
18. **DO NOT patch A3 pointer-discipline finding** — Chris R3 preserve during Phase-0.5 holds
19. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary; violation is a §12 T1 integrity stop
20. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4; adding one requires SIGN + new D-verdict

---

## Reference documents

Ordered by frequency of use at S2825:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md`](docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md) — **S2824 handoff (current)**
3. [`docs/research/implementation/IMPLEMENTATION_LOG_2026-07-19_s2824_phase0_5_b2_build_shipped.md`](docs/research/implementation/IMPLEMENTATION_LOG_2026-07-19_s2824_phase0_5_b2_build_shipped.md) — **S2824 implementation log; §3 R1-R7 mapping + §4 Rigby refinements mapping**
4. [`docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md) — **S2823 envelope (frozen); §15 R1-R7 verbatim**
5. [`docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md`](docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md) — **B1 D-RATIFIED; harvest plan for S2825 execution**
6. [`docs/research/discovery_layer/PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md) — **B2 D-RATIFIED; router design (implementation source)**
7. [`docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md`](docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md) — **B3 D-RATIFIED; abstain policy the router implements**
8. [`core/services/phase_0_5_router.py`](core/services/phase_0_5_router.py) — router substrate (shipped S2824)
9. [`core/services/phase_0_5_classifier_a.py`](core/services/phase_0_5_classifier_a.py) — classifier mirror (drift-guarded)
10. [`core/services/td_handlers_ops.py`](core/services/td_handlers_ops.py) — kb_tool.semantic_search handler at `:5905` (flag-guarded)
11. [`docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py`](docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py) — extraction script for measurement report
12. [`docs/RETRIEVAL_ASSUMPTIONS.md`](docs/RETRIEVAL_ASSUMPTIONS.md) — S2823 skeleton (4 findings; Phase-0.5 evidence collection begins S2825)
13. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 10/10; v0.10 R1 provenance 2-3/2; v0.11 epistemic-integrity 1/2)
14. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 145 rows unchanged at S2824 close
15. [`logs/phase_0_5_router.jsonl`](logs/phase_0_5_router.jsonl) — router SoT (empty at ship; grows at flag-on runtime)
