# Next Session — Start Here

---

## READ THIS FIRST — PLAYBOOK v0.2.0 RATIFIED (SESSION 2737) + §12 KNOWLEDGE RETRIEVAL CAMPAIGN CLOSED (SESSION 2736)

**Refreshed 2026-07-09 (SESSION 2737: Engineering Playbook v0.2.0 MINOR ratified. R1/R2/R3 EOS rules codified into ratified Playbook body as PLAYBOOK-5.2.2/2.2.2/3.2.2. Rule count 190 → 193. Git tag `playbook-v0.2.0`. Full SIGN discipline discharged 15/15 CONFIRMED across 2 batches. Prior arc close SESSION 2736 §12 Knowledge Retrieval Campaign remains valid — all 3 gaps closed via 3-service extension across 6 phases + Rigby SIGN at each gate).**

Session anchors (read in order):
1. [`docs/handoffs/SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md`](docs/handoffs/SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md) — Playbook v0.2.0 ratification record
2. [`docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md`](docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md) — §12 Knowledge Retrieval close

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `3dc2c588` — Playbook v0.2.0 MINOR merged (PR #3048); §12 campaign at `fe25cbd1` (PR #3047) |
| Working tree | 4 modified + 6 new files (see §1 below) |
| Playbook body commit_sha | `ab3c88fa1ddc689a3fbe4cb59d13a5f5fb71cb9b` (v0.2.0 ratifiable body) — prior v0.1.0 at `b372edfe` preserved in prior_ratification block |
| Playbook git tag | `playbook-v0.2.0` (annotated, applied to merge commit `3dc2c588`) — `playbook-v0.1.0` remains on `d82b450a` |
| Playbook rule count | 193 (was 190) — rules added: PLAYBOOK-5.2.2, PLAYBOOK-2.2.2, PLAYBOOK-3.2.2 |
| Pending migrations | 0 |
| PA worker | Post-S2728 restart with Batches A-D. **NEEDS RESTART** to load S2736 P1-P3.1 code when Rigby dispatches begin. Run `make celery-recycle` (F-CW-1 helper from S2732 Batch D). |
| Campaign SIGN pin | `pa-5c76b58f70654409` (title `campaign-s2736-knowledge-retrieval`) — RETIRED at P4 close. |
| Wrapper default pin | `pa-5c76b58f70654409` still in `tools/pa_local.sh:512` at HEAD — next session should rotate to a fresh pin at open, OR retain if directly continuing §12 wrap-up work. |
| Test suite | 51 passed / 0 failed / 0 skipped / 0 xfailed at HEAD (`test_pa_knowledge_retrieval_capability.py` 23 + `test_context_injection_pipeline_validation_2728.py` 28) |

---

## Current constitutional state (unchanged from S2727)

**Engineering Playbook v0.1.0: RATIFIED.** No amendments across §12 campaign.
CD-47 RESOLVED; CD-48 + CD-49 targeted for v0.1.1 PATCH.

**New for S2736** — three EOS rules ratified live at [`docs/EOS_RULES.md`](docs/EOS_RULES.md):
- **R1** Tool Autonomy Principle
- **R2** Capability Discovery Records precede engineering (2 reference CDRs shipped)
- **R3** Acceptance-tests-first (23-test AT harness shipped as reference)

All three queued for Playbook v0.1.1 codification.

---

## Campaign summary — §12 Knowledge Retrieval

| Gap | Phase | Substrate shipped | Status |
|---|---|---|---|
| Gap 1 — PA turn embedding-lane enrichment | P2 + P2.1 | `_retrieve_embedding_context` + `_build_context` embedding block via `ScopedRetrievalService`; citable-path polish (Rigby O5) | ✅ |
| Gap 2 — Runtime lane selector LOCAL vs PROD | P1 + P1.1 | `core/services/rag_lane_selector.py` + `[PA_ROUTING_INIT]` extension; narrow-except polish (Rigby O5) | ✅ |
| Gap 3 — PA/BaseAgent asymmetry closure | P3 + P3.1 | `core/services/relevant_knowledge_service.py` extraction + BaseAgent delegation + PA `_build_context` invocation; empty-keyword guard + docstring correction (Rigby O2/O6) | ✅ |

**All 3 CDR-002 gaps closed.** Capability at HEAD satisfies every requirement of the §10.1 R4 capability statement.

**Observability at HEAD** — `[PA_TASK_SUMMARY]` emits:
```
docs_context_hit=<bool> embedding_context_hit=<bool> agent_knowledge_hit=<bool>
```
One grep answers per turn: "did all three enrichment lanes fire?"

**Rigby SIGN checkpoints:** 3 dispatches (P1, P2, P3), 9 CONFIRMED + 7 REFINEMENTS across all objectives. Every refinement landed as `.1` polish before the next phase opened.

---

## Files awaiting a single close PR

### Modified
- `core/agents/base_agent.py` — `_get_relevant_knowledge_for_task` delegation refactor
- `core/services/unified_pa_entrypoint.py` — P1/P2/P3 enrichment blocks + `[PA_TASK_SUMMARY]` extension
- `docs/research/platform/platform_capability_graph.md` — §25 append-only fold
- `tools/pa_local.sh` — wrapper pin rotation

### New
- `core/services/rag_lane_selector.py` — P1 runtime lane selector
- `core/services/relevant_knowledge_service.py` — P3 shared knowledge substrate
- `core/tests/test_pa_knowledge_retrieval_capability.py` — 23 acceptance tests across 11 classes
- `docs/EOS_RULES.md` — R1/R2/R3 live rule ledger
- `docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`
- `docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md`

---

## Current recommended first task (Chris-choice)

1. **Merge the §12 campaign PR** — single PR consolidating all working-tree
   changes. This is the natural first task if the goal is landing S2736
   work on main.
2. **CDR-001 §16 wrap-up bundle** — 4-item S-M polish (Inbox receiver +
   cross-channel HAIDispatchLog + `channels_fired` convention + dispatch-
   contract normalization). Not a campaign; 1-2 sessions.
3. **Playbook v0.1.1 PATCH** — codify R1 + R2 + R3 from `docs/EOS_RULES.md`
   into the ratified Playbook body. Also folds S2733 retrospective §6
   sections that were queued for v0.1.1.
4. **Next Category A campaign selection** — the Capability Graph has
   §17 Cost Protection P2+, §18 Auth full scope, §19 Conversation
   Lifecycle telemetry, and several other candidates. **MUST run
   Category A per Rule R2 before proposing a campaign scope.**
5. **Rigby CDR-002 §17.4 integration test harness** — deferred future
   arc for a proper Django TestCase-based `_build_context` fixture set.
6. **Something else** — the campaign queue is open.

Recommended session-open protocol:
1. `context-kit orient` (mandatory session-open).
2. Read `docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md` in full.
3. Read `docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md` §11 Lessons Learned + §12+ reconciliation folds.
4. Read `docs/EOS_RULES.md` R1/R2/R3.
5. If Chris chooses (2) or (4): run Category A investigation FIRST per Rule R2.
6. If any Rigby dispatch is planned: `make celery-recycle` to load S2736 code into the PA worker.

---

## Reference documents (read order for post-campaign sessions)

Campaign-closure anchors (S2736):

1. [`docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md`](docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md) — **Session 2736 close.** All governance + code + tests + Rigby SIGN checkpoints in one place.
2. [`docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md`](docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md) — 19-section §12 campaign record.
3. [`docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`](docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md) — first CDR + §16 wrap-up backlog.
4. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3 live rules ratified this session.

Pre-campaign anchors (unchanged):

5. [`docs/handoffs/SESSION_2733_CAMPAIGN_RETROSPECTIVE.md`](docs/handoffs/SESSION_2733_CAMPAIGN_RETROSPECTIVE.md) — Rigby Tool Validation Campaign retrospective.
6. [`docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md`](docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md) — Playbook v0.1.0 ratification ledger.
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified Playbook v0.1.0 body.
8. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap.

---

## Session close summary (Session 2736)

- **Chapter closed**: §12 Knowledge Retrieval campaign shipped end-to-end. All 3 gaps closed via extension of shipped substrate — zero parallel abstractions, zero regression.
- **Governance advances**: two Capability Discovery Records + three EOS rules + one graph fold — the CDR + Rule primitives are now first-class artifacts, not experimental patterns.
- **Rigby-Claude collaboration**: the R1-governed SIGN cycle produced material improvements at every gate. Rule R1 proved itself in production use across 3 phase gates.
- **Test discipline**: 23 acceptance tests written pre-implementation per R3; 28 S2728 regressions preserved; 51 tests total pass at HEAD.
- **PA worker restart** deferred to next session (S2736 P1-P3.1 code shipped but not loaded into the running worker).
- **Handoff + anchor updates:** this file + `docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md` + `docs/EOS_RULES.md` + CDR-001 + CDR-002 + graph §25.

---
