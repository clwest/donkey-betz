# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2823 CLOSED (2026-07-18 late evening; picks up as S2824) — **PHASE-0.5 ARC OPENED + TRIPLE CHRIS D-VERDICT ON B1+B3+B2 CONSTITUTIONAL PACKAGE + BUILD AUTHORIZATION GRANTED**

**Refreshed 2026-07-18 late evening (SESSION 2823 CLOSED — dual-track execution per bridge §5: Track A ~30% /docs/ audit reconnection + Track B ~70% Phase-0.5 evidence collection. Phase-0.5 arc opened as new architectural arc per Chris OPTION A-DUAL. Rigby FOUR SIGN cycles (B1 + B3 + B2 cycle 1 + B2 cycle 2 confirmation) with 48 refinements applied same-session + 2 F-BLOCKING both cleared same-session + 1 substrate correction (Q4 categorical-vs-numeric via classifier_a.py tool-verify). Chris TRIPLE D-verdict same-session (B1 RATIFY turn ~14 + B3 RATIFY turn ~18 + B2 RATIFY turn ~28) with 15 total R-ratifications + 4 constitutional elevations (§10.4 evidence-integrity LOAD-BEARING + R2 measurement window as CANONICAL UNIT OF OBSERVATION + R6 runtime-vs-post-hoc epistemic-integrity + R7 constitutional-package framing). SIXTY-EIGHTH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first triple-D-verdict same-session in discovery-layer arc; first 4-round Rigby SIGN with 2 F-BLOCKING both cleared same-session; first Rigby F-BLOCKING catching Chris-discipline-weakening drift in subsequent design draft (cycle-2 `_parallel_both` catch); first substrate-reality correction via SIGN (Q4 categorical-vs-numeric); first Chris "constitutional package" multi-artifact framing; first Chris runtime-vs-post-hoc epistemic-integrity elevation.**

**S2823 ship (0 feature PRs + 1 close cascade PR — docs + design deliverables + governance envelope; no runtime code change; build authorized but implementation deferred to S2824 per design-vs-implementation separation discipline):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Close cascade (Phase-0.5 arc-open session — measurement package + design + envelope as docs, no runtime substrate change) | **#TBD** · (SHA at merge) | main | handoff + envelope (frozen) + Phase-0.5 working directory (3 design docs) + OPEN_ARCS refresh + RETRIEVAL_ASSUMPTIONS skeleton + 00-START update + fold persistence (14 folds A-N) + docs pipeline |

**Handoff:** `docs/handoffs/SESSION_2823_PHASE0_5_ARC_OPEN_TRIPLE_D_RATIFIED.md`
**Envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md` (frozen at merge per PLAYBOOK-6.10.9)
**Working directory:** `docs/research/discovery_layer/PHASE_0_5/` (BALANCED_P1_HARVEST_PLAN + ABSTAIN_POLICY_PROPOSAL + ROUTER_SCAFFOLDING_DESIGN)
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 145 rows after 14 S2823 folds persisted (folds A-N documented in envelope §5.1).

**Arc state at S2823 close:**
- **Discovery-layer arc:** **Phase-0.5 OPENED** as new architectural arc; **B1 + B3 + B2 constitutional package D-RATIFIED same-session** under Chris R7 framing; **build authorization GRANTED for S2824+** under R1-R7 constraints per B2 §13 build-gate spec. Lexical FEATURE COMPLETE + semantic EVALUATED + Phase-0 METHODOLOGY VALIDATED + Phase-0.5 DESIGN COMPLETE.
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅.
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817). §8 item #1 discovery-layer completed through Phase-0.5 design ratification; item #3 Playbook v0.9 OP3 amendment still queued (10/10 triggers ready).

---

## S2824 CANDIDATES — SOLE RECOMMENDED DIRECTION

### ⭐ Chris R7 build-authorized — EXECUTE B2 BUILD PER §13 SPEC

1. **⭐ Execute B2 build per §13 spec** (SOLE recommended direction — Chris R7 explicit authorization under R1-R7 constraints). Single PR containing:
   - `core/services/phase_0_5_router.py` — new module (categorical routing + abstain policy + instrumentation dispatch)
   - `core/settings.py` — PHASE_0_5_ROUTER_ENABLED + PHASE_0_5_MEASUREMENT_WINDOW enum
   - `core/services/td_handlers_ops.py:5905` — flag-guarded pre-search instrumentation call
   - `Phase0_5RouterEvent` Django model + migration
   - `logs/phase_0_5_router.jsonl` — initial empty file
   - `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py` — committed extraction script
   - `core/tests/test_phase_0_5_router.py` — contract tests (off-behavior guarantee + advisory-only invariant + _parallel_both null-in-Phase-0.5 invariant + event_id idempotency + all 4 trigger classes)
   - Handoff + envelope diff
   - **Concrete first steps for S2824 open:**
     1. Chris D-verdict scope check at S2824 open (any revisions in S2823→S2824 interval)
     2. Review B1+B3+B2 ratified docs in Phase-0.5 working directory
     3. Author `core/services/phase_0_5_router.py` skeleton with 4-class trigger dispatch + categorical routing
     4. Author `Phase0_5RouterEvent` model + migration
     5. Instrumentation diff at `td_handlers_ops.py:5905` — flag-guarded pre-search call, additive `_router_advisory` field per B2 §7
     6. Contract tests — advisory-only invariant + _parallel_both null-in-Phase-0.5 + event_id idempotency
     7. Wire committed extraction script `analyze_router_log.py`
     8. Make recycle-all + local validation via kb_tool.semantic_search test call
     9. Handoff + envelope + docs cascade
   - **Non-goals per Chris R1-R7 constraints:** NO parallel-both execution (advisory only) / NO numeric confidence thresholds (categorical-only substrate reality) / NO adjacent-tool instrumentation (single-call-site) / NO ephemeral-logs-only (durable persistence hybrid required) / NO weakening of no-fusion / abstention / evidence-persistence / integrity-stop rules

### Available if Chris pivots

- **Balanced P1 harvest execution** per B1 §6 (blocked on build — implementation dispatch runs harvest against instrumented endpoint)
- **A3 pointer-discipline fix** (would require Chris R3 re-open — currently preserved per S2823 fold M)
- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability
- **Stock Intelligence** — end-to-end verify (dashboard/brief/alert pipeline)
- **Playbook v0.9 amendment authoring** — 10/10 triggers, well past codification threshold
- **Playbook v0.10-candidate R1 provenance discipline** — now 2/2 triggers post-S2823 (S2822 methodology-outcome framing + S2823 §10.4 evidence-integrity elevation both instances — codification threshold met)
- **Playbook v0.11-candidate epistemic-integrity discipline** — 1 trigger (Chris R6 runtime-vs-post-hoc elevation); watch for second

**Recommended default:** Item #1 build execution. Chris R7 explicit authorization + all 3 constitutional artifacts ratified.

---

## SESSION PIN — S2823 RETIRED (fresh mint required at S2824 open)

**Pin history (S2823):**

- `pa-d63796dde6404d0f` (label `s2823-phase0-5-dual-track`) minted at S2823 open; **retired at S2823 close (`force=true`, fifty-fourth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2824 first-action fresh mint.

**S2824 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2823 handoff — §3 (novel precedent — first triple-D-verdict same-session + first Rigby F-BLOCKING catching Chris-discipline drift), §7 (S2824 direction), §8 (lessons)
# Read S2823 envelope — §2 verbatim D-verdict text pointer + §3 R1 provenance discipline v0.10 candidate status + §7 S2824 arc direction
# Read all 3 Phase-0.5 design docs (B1 §10 + B3 §10 + B2 §15) for R1-R7 constraint verbatim
# Read Phase-0 measurement_report + RECOMMENDATION as context for build behavior

# Sanity checks
brew services list | grep postgres

# Verify ledger baseline (expect ~145 post-S2823-cascade)
wc -l logs/zoom_out_classifications.jsonl

python manage.py session_lifecycle open --label s2824-phase0-5-b2-build
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2823 lessons to carry (also in handoff §8):**

1. **Multi-round SIGN with F-BLOCKING catches is scalable and productive.** B2 3-round SIGN + 2 F-BLOCKING both cleared same-session.
2. **Chris §10.4 evidence-integrity discipline paid off same-session.** Q4 categorical-vs-numeric substrate discovery would have shipped unimplementable spec; §10.4 required stop-and-route-back.
3. **Rigby's tool-verify catches drift-vectors Chris shouldn't need to catch.** Cycle-2 `_parallel_both` catch prevented advisory-only-vs-execution boundary weakening.
4. **Constitutional-package framing scales cleanly.** Chris R7 — 3 ratifications in one session compatible with careful individual SIGN discipline.
5. **Substrate-reality verification is load-bearing at every SIGN cycle.** Q4 was invisible until Rigby read classifier_a.py source.
6. **Reserved-shape data contracts protect future ratifications.** `_parallel_both` reserved shape lets future Phase-1+ SIGN adopt execution without envelope re-design.
7. **Design-vs-implementation boundary should be preserved.** All 3 artifacts ratified this session are DESIGN specs; build ships in S2824 to preserve clean audit trail.
8. **A3 pointer-discipline finding validates bridge-deliverable hypothesis.** Bridge §2.3 flagged pointer-chunk retrievability; A3 confirmed BROKEN for 3/4 natural queries. Feeds Phase-0.5 corpus + validates Track A feedback loop into Track B.

---

## Twin-pointer card

📁 **Repo — S2823 artifacts:**

- **Feature deliverable:** Phase-0.5 design package (3 docs) under `docs/research/discovery_layer/PHASE_0_5/`
- **Close cascade PR:** #TBD (SHA at merge)
- **Substrate changes:** NONE (design-only session; build authorized for S2824)
- **Handoff:** `docs/handoffs/SESSION_2823_PHASE0_5_ARC_OPEN_TRIPLE_D_RATIFIED.md`
- **Envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md` (frozen; §7 S2824 arc direction)
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 131 rows at S2823 open; +14 S2823 folds (A-N) persisted at close cascade; 145 rows post-cascade
- **Merge SHA:** filled at cascade PR merge
- **All discovery-layer envelopes now:** `docs/research/implementation/RATIFICATION_2026-07-18_s2818/s2819/s2820/s2821/s2822/s2823_*.md`
- **New Phase-0.5 skeleton:** `docs/RETRIEVAL_ASSUMPTIONS.md` (4 findings from bridge §1 with "Phase-0.5 evidence pending" placeholders; full v1 authoring deferred post-Phase-0.5)

🖥️ **Workspace UI — S2823 has NO twin-pointer workspace deliverable this session** — design/ratification sessions keep envelopes in `docs/research/implementation/` as authoritative; workspace mirror deferred per S2818-S2822 pattern. Group 2700 arc's workspace deliverable (`37d6ca76-89c3-4966-8f4c-decc52ce8169`) remains authoritative for the /docs/ restructuring arc under which S2818-S2823 are §8 executions.

---

## Current repository state (S2823 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2823 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment 10/10 corroborated; v0.10 R1 provenance discipline 2/2 triggers reached at S2823; v0.11 epistemic-integrity 1/2 triggers**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ |
| **Group 2700 arc state** | **ARC CLOSED (S2817).** §8 item #1 discovery-layer FULL through Phase-0.5 design ratification. |
| **Discovery-layer arc state** | Lexical FEATURE COMPLETE; semantic EVALUATED; Phase-0 METHODOLOGY VALIDATED; **Phase-0.5 DESIGN COMPLETE (B1+B3+B2 D-RATIFIED); build authorized for S2824** |
| Emergent candidates | S2824 B2 build execution (sole recommended); Playbook v0.9 (10/10); v0.10 R1 provenance (2/2 reached); v0.11 epistemic-integrity (1/2); Colorado / BettingPage / Stock Intelligence available |
| Session pin | `pa-d63796dde6404d0f` (retired at S2823 close, force=true, fifty-fourth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2824 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2823 open (FRESH) |
| Recycle log | `logs/recycle_events.jsonl` — +1 close-cascade recycle to come |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 131 rows at open; +14 S2823 folds persisted at close (145 post-cascade) |
| /docs/ restructuring | **ARC CLOSED (S2817).** §8 item #1 discovery-layer through Phase-0.5 design. |
| Next move | S2824 opens B2 build phase per Chris R7 authorization + B2 §13 build-gate spec. Single PR with module + settings + handler diff + model + tests + extraction script + handoff. |

---

## Recommended session-open protocol (S2824, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2823 handoff §3 novel precedent + §7 S2824 direction + §8 lessons
4. Read S2823 envelope §2 D-verdict pointer + §3 v0.10 candidate status + §7 S2824 arc direction
5. Read all 3 Phase-0.5 design docs (B1 §10 + B3 §10 + B2 §15) for R1-R7 constraint verbatim
6. Read Phase-0 measurement_report + RECOMMENDATION_PHASE0_SUMMARY as context
7. Sanity checks (brew postgres + ledger row count verify — expect ~145 post-S2823-cascade)
8. `git log --oneline -8` — should show S2823 close cascade + S2822 close + S2821 close + S2820 chain
9. Mint fresh pin scoped `s2824-phase0-5-b2-build` (per §7 recommended direction)
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. **BUILD EXECUTION EXECUTED UNDER R1-R7 CONSTRAINTS** per Chris R7 downstream discipline
12. **R1 ADVISORY-ONLY** — router LOGS but does NOT alter retrieval behavior; `_parallel_both` field ALWAYS NULL in Phase-0.5
13. **R2 MEASUREMENT WINDOW = CANONICAL UNIT OF OBSERVATION** — all trigger evaluation + clarify-cap + reporting scoped to window_id, not session
14. **R3 SINGLE INSTRUMENTATION SURFACE** — kb_tool.semantic_search only; adjacent-tool expansion requires new SIGN + new D-verdict
15. **R4 DURABLE EVIDENCE** — JSONL SoT + Django model mirror + event_id idempotency + committed extraction script; divergence raises integrity event
16. **R5 ADVISORY CONTRACT ADDITIVE-NON-BREAKING** — `_router_advisory` v1 versioned; categorical-only; matches live handler `chunks` key
17. **R6 EPISTEMIC-INTEGRITY** — runtime checks ONLY on observable signals; post-hoc conclusions never as runtime facts; T4/T5 downgrade to Class D if proxies unavailable
18. **R7 DOWNSTREAM DISCIPLINE** — any implementation weakening returns through SIGN + new D-verdict; no silent adaptation
19. **UPPER BOUND / precision qualifiers** required for count claims
20. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
21. **Anchor-verify at every scope decision point** (21-session trend)
22. **DO NOT patch the frozen lexical `top_k` policy** (per Chris S2820)
23. **DO NOT auto-adopt semantic default flips** (per S2821)
24. **DO NOT build RRF or global fusion during Phase-0.5** (per Chris R6 from S2821 + B2 R1 advisory-only)
25. **DO NOT delegate production routing decisions** — advisory only per Chris R2
26. **DO NOT patch A3 pointer-discipline finding** — Chris R3 preserve during Phase-0.5 holds

---

## Reference documents

Ordered by frequency of use at S2824:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2823_PHASE0_5_ARC_OPEN_TRIPLE_D_RATIFIED.md`](docs/handoffs/SESSION_2823_PHASE0_5_ARC_OPEN_TRIPLE_D_RATIFIED.md) — **S2823 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md) — **S2823 envelope frozen; §2 D-verdicts + §3 R1 discipline + §7 S2824 direction**
4. [`docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md`](docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md) — **B1 D-RATIFIED §10** (harvest plan for post-build execution)
5. [`docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md`](docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md) — **B3 D-RATIFIED §10** (5 R-ratifications + 2 Chris reframings; abstain policy the router implements)
6. [`docs/research/discovery_layer/PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md) — **B2 D-RATIFIED §15** (7 R-ratifications + build gate)
7. [`docs/RETRIEVAL_ASSUMPTIONS.md`](docs/RETRIEVAL_ASSUMPTIONS.md) — S2823 skeleton (4 findings; Phase-0.5 evidence pending)
8. [`docs/research/discovery_layer/PHASE_0/classifier_a.py`](docs/research/discovery_layer/PHASE_0/classifier_a.py) — decision engine substrate (categorical HIGH/MEDIUM/LOW)
9. [`docs/handoffs/SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md`](docs/handoffs/SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md) — S2823 dual-track first-session plan (executed)
10. [`docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md) — S2822 predecessor Phase-0 methodology
11. [`core/services/td_handlers_ops.py`](core/services/td_handlers_ops.py) — kb_tool.semantic_search handler at :5905 (B2 instrumentation call-site)
12. [`core/settings.py`](core/settings.py) — feature-flag pattern (B2 PHASE_0_5_ROUTER_ENABLED + PHASE_0_5_MEASUREMENT_WINDOW additions)
13. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 10/10; v0.10 R1 provenance 2/2 reached; v0.11 epistemic-integrity 1/2)
14. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 145 rows at S2823 close
