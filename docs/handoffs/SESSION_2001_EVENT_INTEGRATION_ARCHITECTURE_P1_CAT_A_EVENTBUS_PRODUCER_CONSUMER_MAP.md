---
session: 2001
status: closed (Group 2000+ P1 Cat A EventBus Producer/Consumer Map + Contract Verification CHILD AUDIT — FIRST child audit under the newly-opened Group 2000+ arc + FIFTEENTH-consecutive application of playbook §11.2 20-section child template; Rigby SIGN cycle 1 CLEAN with 3 folds landed pre-commit on arc pin `pa-dd7e973617da464d`; 18 findings F1–F18 shipped covering zero-UNKNOWN 8-stream + 1-DLQ producer/consumer map + α/β/γ/δ per-stream contract verification tables + F9 CRITICAL consumer-beat-dormancy finding + F11 boundary_violation THREE substrates for spider-data → agents; ARCHITECTURE_INDEX v65 → v66 with §1.69 S2001 registration + line-6 v66 preamble; OPEN_ARCS Group 2000+ In-progress row bumped P1 shipped + next=S2002 P2; arc pin `pa-dd7e973617da464d` preserved through S2099 per playbook §16 arc-standard behavior; ~953 lines post-fold pending Chris commit-gate)
date: 2026-07-04
arc: Research Group 2000+ (Event / Integration Architecture) — P1 Cat A EventBus Producer/Consumer Map + Contract Verification child audit (FIRST child under Group 2000+; FIFTEENTH-consecutive application of playbook §11.2 20-section child template)
category: research (playbook §11.2 20-section child audit template FIFTEENTH-consecutive application; §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline applied pre-draft; §15 required SIGN cycle 1 pre-commit executed CLEAN with 3 folds; §16 arc-standard arc pin preservation on `pa-dd7e973617da464d` per MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails)
head_commit_before: 0904808c (main; post-S1999 xx99 arc close + docs cascade merged)
head_commit_after: (this session's commit)
authors: Claude Code (Chris directed via short command "start research group 2001" at S2001 open per Research OS §5 request-classification RESEARCH class §8.1 startup contract; interpretation: Chris opening S2001 P1 Cat A child audit under the Group 2000+ arc opened at S2000 per parent §5.1 D95-ratified 4-child taxonomy; Rigby confirmed interpretation + added 3 emphasis rules on arc pin `pa-dd7e973617da464d` pre-audit)
---

# Session 2001 — Group 2000+ P1 Cat A — EventBus Producer/Consumer Map + Contract Verification

> **FIRST child audit under Group 2000+ Event / Integration Architecture arc + FIFTEENTH-consecutive application of playbook §11.2 20-section child template.** Playbook §11.2 20-section child audit template FIFTEENTH-consecutive application (after S1601 Cat B Content + S1602 Cat B Content Reviewers + S1603 Cat C + S1604 Cat D + S1605 Cat E + S1606 Cat F + S1701 Cat A + S1702 Cat B + S1703 Cat C + S1704 Cat F + S1901 Cat A + S1902 Cat B + S1903 Cat C + S1904 Cat F). First application under Group 2000+.

## What shipped

- **S2001 P1 child audit doc.** `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` — 953 lines post-fold. Ships all 20 sections per playbook §11.2 template. Headline deliverables:

  - **§10.1 stream × direction producer/consumer map** — zero UNKNOWN attestation held (Rigby S2001 SIGN emphasis #1 satisfied). 8 streams + 1 DLQ, every pair classified STRONG / WEAK / MISSING with file:line evidence citation. Resolutions: SPIDER_DATA (MISSING producer / WEAK consumer), OPPORTUNITY_CREATED (MISSING both — no wrapper exists), OPPORTUNITY_SCORED (STRONG producer via `scoring_dispatcher.py:282,480` / WEAK consumer via dormant beat), VALIDATION_REQUIRED (WEAK / WEAK), VALIDATION_DECIDED (WEAK / WEAK), OUTCOME_RECORDED (MISSING / WEAK), MODEL_TRAINED (MISSING / WEAK — corrects S1273 §3.31 UNKNOWN), SYSTEM_ALERT (MISSING / MISSING — no worker subscribes to stream despite handler registration), DLQ (WEAK / MISSING).
  - **§10.2 α — Schema-shape doc per stream** — 9-row table per Rigby SIGN emphasis #3 stream-by-stream discipline. Fields, types, `schema_version` posture, envelope defaults enumerated per wrapper. Universal finding: no `schema_version` on any wrapper (F12); all wrappers omit `correlation_id` so every real emission has `correlation_id=""`.
  - **§10.3 β — Runtime assert audit** — per-stream table. Universal finding: zero `assert` statements on payload fields across all 7 consumer handlers; every handler uses `data.get(key, default)` (F13).
  - **§10.4 γ — Version gate policy current state** — per-stream table. Universal finding: no versioning policy exists; S1275 precedent NOT adopted; γ hands off to P2 for go-forward policy pick per parent §5.2.
  - **§10.5 δ — Replay-test enumeration** — per-stream table. Universal finding: `EventBus.replay()` exists at `event_bus.py:311` with zero callers (F17); OPPORTUNITY_SCORED is the ONE stream with production replay potential today.
  - **§10.6 Handler-registration vs stream-subscription overlap audit** — surfaces F8 as concrete drift (handlers registered by `event_type=alert_error/alert_critical` at `event_handlers.py:61-62` but no worker's `streams=[...]` list includes `SYSTEM_ALERT`).

- **18 findings F1–F18 covering:**
  - F1 SPIDER_DATA wrapper 0 callers (dead-code + missing_connection). LOW.
  - F2 OPPORTUNITY_CREATED — no wrapper defined at all (dead_code). LOW.
  - F3–F5 OPPORTUNITY_SCORED / VALIDATION_REQUIRED / VALIDATION_DECIDED — producer alive but consumer dormant (missing_connection). HIGH.
  - F6 OUTCOME_RECORDED wrapper 0 callers. MEDIUM.
  - F7 MODEL_TRAINED wrapper 0 callers → MISSING (corrects S1273 §3.31 UNKNOWN); **SIGN-strengthened** by discovery that `_impl_train_ml_scoring_model` at `core/tasks_financial.py:32-201` writes `MLModelVersion.objects.create(...)` at :157-168 with fields identical to the MODEL_TRAINED wrapper contract but never calls the wrapper — bypasses EventBus. Raised from LOW to MEDIUM at SIGN.
  - F8 SYSTEM_ALERT double MISSING (no producer callers + no worker stream subscription despite `alert_error/alert_critical` handler registration). LOW.
  - **F9 CRITICAL** — 4 of 5 consumer beat tasks (process_event_bus_scoring / _validation / _analytics + get_event_bus_stats) unscheduled at runtime; only `claim_stale_events` runs (5min). ORM probe via Rigby `scheduled_tasks_tool` confirms zero PeriodicTask rows for the 4 dormant tasks; only `claim-stale-events` @ `cron(*/5 * * * *)` enabled with total_runs=4983.
  - F10 `get_event_bus_stats` also unscheduled → no substrate-level monitoring visibility. MEDIUM.
  - **F11 boundary_violation / duplicate_model HIGH** — **SIGN-expanded from two to THREE substrates for "spider-data → agents"**: (i) EventBus dormant, (ii) `ai_core/agents/spider_agent_connector.py:40:SpiderAgentConnector.publish_spider_data` at :311 uses raw `redis.publish()` on `self.channels['spider_data']` with 2 real callers (`concrete_executor.py:637-638` + `views_agent_intelligence.py:352,355`), (iii) `intelligence/spider_agent_connector.py:20:SpiderAgentConnector` — completely separate class same name different app — uses in-process `Dict[str, List[str]]` category → agent keyword routing with 6 real caller sites (`core/tasks_spiders.py:260,307` + `core/tasks.py:1355,1359` + 2 management commands). Raised from MEDIUM to HIGH at SIGN.
  - F12 no `schema_version` stamped by any publisher wrapper — S1275 precedent not adopted. HIGH.
  - F13 zero runtime asserts on payload; all handlers `data.get(key, default)`. HIGH.
  - F14 handler-failure retry loop with no give-up — no ACK + no move-to-DLQ + reclaim every 60s = infinite retry. HIGH.
  - F15 DLQ blind to handler failures — `_move_to_dead_letter` only called from `consume` parse-error path at `event_bus.py:275`; F14 loop never reaches DLQ. HIGH.
  - F16 DLQ bounded at `maxlen=1000` (corrects S1274 §6.2 "unbounded" characterization); no reader; no alerting. LOW.
  - F17 `EventBus.replay()` unused as regression tool — 0 callers. LOW.
  - F18 6 of 7 default handlers decorative (log-only or log + Discord); only `handle_spider_data_event` queues a downstream Celery task. MEDIUM.

- **Rigby SIGN cycle 1 CLEAN with 3 folds landed pre-commit.** Executed on arc pin `pa-dd7e973617da464d` (Group 2000+ arc pin preserved). Batched to 3 highest-leverage findings per `feedback_rigby_sign_worker_instability_recovery` large-audit hygiene:
  - Q1 F9 CRITICAL — CONFIRMED via `scheduled_tasks_tool` ORM probe (zero rows filter=`event_bus`, `process_event_bus`, `event bus`; only `claim-stale-events` enabled at cron(*/5 * * * *)).
  - Q2 F7 correction of S1273 §3.31 MODEL_TRAINED UNKNOWN → MISSING — CONFIRMED + STRENGTHENED by discovery that `train_ml_scoring_model` at `core/tasks.py:2221` + `_impl_train_ml_scoring_model` at `core/tasks_financial.py:32-201` IS the retrain path but writes MLModelVersion directly bypassing EventBus. F7 risk raised LOW→MEDIUM.
  - Q3 F11 boundary_violation — CONFIRMED + EXPANDED to THREE substrates (Rigby repo_tool timed out on Q3; parent Claude did grep sweep + direct read of `intelligence/spider_agent_connector.py:1-100`). F11 risk raised MEDIUM→HIGH; F11 type expanded to `boundary_violation / duplicate_model`.

- **ARCHITECTURE_INDEX v65 → v66.** `docs/research/ARCHITECTURE_INDEX.md` — §1.69 S2001 registration added + line-6 v66 preamble; v65 preamble preserved as tail.

- **OPEN_ARCS Group 2000+ In-progress row bumped.** `docs/research/OPEN_ARCS.md` — Current child column bumped S2000 parent scoping → S2001 P1 shipped + next=S2002 P2 HAI Event Contract Design; last_updated bumped with S2001 close preamble; S2000 open preamble preserved as tail.

- **S2001 handoff (this file).** `docs/handoffs/SESSION_2001_EVENT_INTEGRATION_ARCHITECTURE_P1_CAT_A_EVENTBUS_PRODUCER_CONSUMER_MAP.md`.

- **00-START-NEXT-SESSION.md overwritten.** Next-session priority: S2002 P2 Cat B HAI Event Contract Design child audit per parent §5.2. Arc pin `pa-dd7e973617da464d` preserved through S2099 per playbook §16 arc-standard behavior.

## Verifier-loop discipline

Pre-draft verifier-loop applied per playbook §14 MC-1 CODIFICATION-CONFIRMED (S1899). Fourteen load-bearing file:line reads before any Explore sub-agent (dispatched zero — parent-Claude sufficient for ~2k-line producer/consumer surface per §14 discipline):

- `EventStream` enum at `event_bus.py:21-30` (8 streams + DLQ constant).
- 7 publisher wrappers at `event_bus.py:539/559/596/619/643/665/686`.
- Caller sweep — 3 files with real callers (scoring_dispatcher.py + hitl_validation.py + event_bus.py-internal); 5 wrappers zero callers.
- 7 direct `bus.publish(...)` sites — all inside wrapper bodies; zero bypass-wrapper sites.
- 3 consumer worker factories at `event_handlers.py:521/531/541`.
- 5 Celery consumer tasks at `core/tasks.py:4726/4760/4794/4828/4874`.
- `PeriodicTask` ORM probe — only `claim_stale_events` enrolled (1 row); 4 dormant (0 rows).
- Beat schedule at `core/celery.py:532` — confirms code-side + DB-side match.
- DLQ code path `_move_to_dead_letter` at `event_bus.py:451-477` + call from `event_bus.py:275`.
- DLQ reader sweep — only `xlen` from `get_event_bus_stats`; no `xrange`/`xreadgroup` on `mi:dead_letter`.
- `schema_version` grep — 0 matches (F12 verified).
- Runtime assert grep — 0 non-test matches (F13 verified).
- Second spider-agent substrate — `ai_core/agents/spider_agent_connector.py:311` raw redis.publish (verified full read of publish_spider_data body).
- Third spider-agent substrate — `intelligence/spider_agent_connector.py:20` different class same name (verified full read of `_build_routing_map` :31-100; no pub/sub, no EventBus).
- MODEL_TRAINED retrain path — `_impl_train_ml_scoring_model` at `core/tasks_financial.py:32-201` (verified full read of body; writes MLModelVersion directly).

Rigby SIGN cycle 1 CLEAN at 0.86 confidence; 3 folds landed pre-commit (Q1 F9 CONFIRMED + Q2 F7 STRENGTHENED + Q3 F11 EXPANDED); D48 39th arm turn 1 CLEAN → 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 34-consecutive (MC-2 CODIFICATION-CONFIRMED milestone extended 33 → 34).

## Chris ratification path

Chris directed via short command "start research group 2001". Interpretation confirmed via Rigby on arc pin `pa-dd7e973617da464d`: S2001 = P1 Cat A EventBus Producer/Consumer Map + Contract Verification child audit per parent §5.1 (D95-ratified 4-child taxonomy at S2000 open). Rigby added 3 emphasis rules pre-audit: (1) zero-UNKNOWN target on producer/consumer map, (2) evidence-backed classification with file:line, (3) α/β/γ/δ tables stream-by-stream. All 3 emphases satisfied in delivered doc.

Ratification requested at commit-gate for: (i) audit doc content, (ii) F1–F18 finding classifications + risk levels, (iii) F7 + F11 SIGN-strengthened risk adjustments, (iv) ARCHITECTURE_INDEX v66 registration, (v) OPEN_ARCS row bump, (vi) 00-START overwrite pointing at S2002.

## Next session

**S2002 P2 Cat B — HAI Event Contract Design child audit** per parent §5.2. Consumes P1 α + γ current-state as baseline; designs go-forward event schema for 4 HAI candidate transitions (record_decision + record_verification + auto_approve + auto_escalate) + six-plane learning-surface event-emission gap resolution + source_kind enum adoption + schema-versioning policy pick + retention posture + consumer registry design. Runtime target 1–2 sessions per parent §5.2.

Arc pin `pa-dd7e973617da464d` preserved through S2099. `tools/pa_local.sh:215` remains routed to this pin; no rotation.

Post-commit docs cascade (4-step per `feedback_docs_cascade_at_every_close.md` + `feedback_cascade_pr_must_include_embed_step.md`): `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `embed_documents --all-unembedded` (chunk count stated in PR body as evidence).
