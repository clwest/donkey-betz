# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2000+ Event / Integration Architecture arc pin `pa-dd7e973617da464d` is ACTIVE as of S2000 open 2026-07-04 (preserved through S2001 close 2026-07-04). Minted via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2000+ arc (S2000 → S2001 → **S2002** → S2003 → S2004 → S2099) — playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2000+ P1 CAT A LANDED AT S2001; NEXT-SESSION = S2002 P2 CAT B HAI EVENT CONTRACT DESIGN

**Group 2000+ Event / Integration Architecture arc: S2000 parent shipped + S2001 P1 shipped → next is S2002 P2 Cat B HAI Event Contract Design child audit** per parent `2000_event_integration_architecture_domain_scoping.md` §5.2.

- **Active arc pin:** `pa-dd7e973617da464d` — preserved through S2001; no rotation between children per playbook §16 arc-standard-behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close.
- **Arc progress:** S2000 parent (shipped) + S2001 P1 Cat A EventBus Producer/Consumer Map + Contract Verification (shipped) → S2002 P2 (next) → S2003 P3 → S2004 P4 → S2099 xx99 canonical summary. On-track for 6-session arc-completion path per parent §9.3.

## READ THIS THIRD — S2001 P1 CAT A CHILD AUDIT LANDED; SIGN CYCLE 1 CLEAN; F9 CRITICAL + F11 HIGH SIGN-EXPANDED + F7 STRENGTHENED

Session 2001 shipped the **Group 2000+ P1 Cat A EventBus Producer/Consumer Map + Contract Verification child audit** at `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` (`status: draft`, `category: research`, `session: 2001`, `child_slot: P1_cat_a`, `domain_slug: event_integration_architecture`, `research_group: 2000`, `mission_type: child_audit`; ~953 lines post-Rigby SIGN cycle 1 3 folds landed pre-commit).

**S2001 P1 audit ships:**

- **§10.1 stream × direction producer/consumer map** — **zero UNKNOWN attestation held** (Rigby S2001 SIGN emphasis #1 satisfied). 8 streams + 1 DLQ, every pair classified STRONG / WEAK / MISSING with file:line evidence citation. Only OPPORTUNITY_SCORED has STRONG producer (2 sites in `scoring_dispatcher.py:282,480`); OPPORTUNITY_CREATED has no wrapper at all; 5 of 7 wrappers have zero callers; DLQ has no reader.
- **§10.2 α — Schema-shape doc per stream** — 9-row table with `schema_version` posture, envelope defaults, field types per Rigby SIGN emphasis #3 stream-by-stream discipline.
- **§10.3 β — Runtime assert audit** — universal finding: zero `assert` statements on payload across all 7 handlers; all use `data.get(key, default)`.
- **§10.4 γ — Version gate policy** — universal finding: no versioning; S1275 precedent NOT adopted. Hands off to S2002 P2.
- **§10.5 δ — Replay-test enumeration** — `EventBus.replay()` exists at `event_bus.py:311` with zero callers; OPPORTUNITY_SCORED is the ONE stream with production replay potential today.
- **§10.6 Handler-registration vs stream-subscription overlap audit** — surfaces F8 as concrete drift (SYSTEM_ALERT handler registered but no worker subscribes).
- **18 findings F1–F18** covering dead_code + missing_connection + drift + boundary_violation + technical_debt. Full inventory in §20.7 finding index.

**Load-bearing findings:**

- **F9 CRITICAL — 4 of 5 EventBus consumer beat tasks unscheduled at runtime.** `process_event_bus_scoring_queue` + `_validation_queue` + `_analytics_queue` + `get_event_bus_stats` all have ZERO PeriodicTask rows (verified via Rigby `scheduled_tasks_tool` ORM probe). Only `claim_stale_events` runs at `cron(*/5 * * * *)` with `total_runs=4983`. Entire consumer runtime dormant; events accumulate in Redis Streams until STREAM_MAX_LEN=10000 silent-truncates.
- **F7 SIGN-STRENGTHENED — MODEL_TRAINED wrapper 0 callers → MISSING (corrects S1273 §3.31 UNKNOWN).** Real retrain path `_impl_train_ml_scoring_model` at `core/tasks_financial.py:32-201` writes `MLModelVersion.objects.create(...)` at :157-168 with fields identical to the MODEL_TRAINED wrapper contract but never calls the wrapper — bypasses EventBus for ORM. Risk raised LOW→MEDIUM at SIGN.
- **F11 SIGN-EXPANDED HIGH — THREE substrates for "spider-data → agents":** (i) EventBus dormant, (ii) `ai_core/agents/spider_agent_connector.py:40:SpiderAgentConnector.publish_spider_data` at :311 uses raw `redis.publish()` on `self.channels['spider_data']` with 2 real callers, (iii) `intelligence/spider_agent_connector.py:20:SpiderAgentConnector` — completely separate class same name different app — uses in-process `Dict[str, List[str]]` category → agent keyword routing with 6 real caller sites. Two identically-named classes in two Django apps. Risk raised MEDIUM→HIGH; type expanded to `boundary_violation / duplicate_model`. Inherits forward to S2003 P3.
- **F16 CORRECTION** — DLQ `mi:dead_letter` bounded at `maxlen=1000` (corrects S1274 §6.2 "unbounded" characterization). Real DLQ gap is no reader + no alerting + no fed from handler failures (F15).

**Rigby SIGN cycle 1 CLEAN at 0.86 confidence 2026-07-04** on preserved Group 2000+ arc pin `pa-dd7e973617da464d`. **3 folds landed pre-commit** (Q1 F9 CONFIRMED + Q2 F7 STRENGTHENED + Q3 F11 EXPANDED). **D48 39th arm turn 1 CLEAN → 32-consecutive-fully-clean-arms sub-pattern EXTENDED to 34-consecutive** per single-batch-3-question criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 33 → 34). Cycle 2 NOT REQUIRED.

**Chris ratification 2026-07-04** on interpretation of "start research group 2001" as S2001 P1 Cat A child audit + Rigby's 3 emphasis rules pre-audit (zero-UNKNOWN + evidence-backed classification with file:line + α/β/γ/δ tables stream-by-stream). All 3 emphases satisfied in delivered doc.

## S2002 P2 next-session priority

**S2002 P2 Cat B HAI Event Contract Design child audit** per parent §5.2. Runtime target 1–2 sessions.

**Scope:** designs event-emission contract semantics for four HAI candidate transitions (`record_decision` + `record_verification` + `auto_approve` + `auto_escalate`) + six-plane learning-surface event-emission gap resolution + `source_kind` enum value adoption + schema-versioning policy pick + retention posture + consumer registry design.

**Scope guardrail (per parent §5.2 + Rigby S2000 SIGN cycle 1 Q1 fold):** authority MECHANISM (resolution logic, AuthorityService reads, per-user policy binding) is OUT-OF-SCOPE and post-arc. P2 designs event-emission contract semantics only. F.PER-USER-AUTHORITY-MECHANISM event-emission contract is in-scope per S1903 §19 inheritance (per-user authority resolution triggers), but the mechanism itself remains post-arc.

**Deliverables (all in one design contract doc):**

- **Event schema for four HAI candidate transitions.** Per-event: field shape, required vs optional, JSON schema, mapping to existing HAI models (HAI + HFR + HumanPreference). Consumes S1806 §10 durable-at-six catalog.
- **Six-plane learning-surface event schema.** For each of 6 planes (HAI-mediated + autonomous_bridge + non_bridge_direct + verification_outcome + external_signal + shadow_service): plane-transition event + payload shape. Adopts `source_kind` enum from R.HAI.SOURCE-KIND-ENUM-ADR (joint Group 1300 + Group 1800 T0/Gate item 5).
- **Schema versioning policy pick.** Adopt S1275 precedent (per-event `schema_version` field with graduation contract) OR design new policy. Justify with backward-compat + forward-compat requirements. Consumes S2001 §10.4 γ current-state (no versioning) as baseline.
- **Retention posture.** Pair with joint R.OBSERVABILITY.RETENTION-UNIFIED-ADR (Group 1700 T0/Gate) + R.HAI.RETENTION-UNIFIED-ADR (Group 1800 T0/Gate). Recommend TTL per event class; recommend Redis Streams retention (`MAXLEN`) vs. audit-table retention hybrid.
- **Consumer registry.** Per event, enumerate expected consumers. Draft consumer contracts. Registry documents the contract even if not all consumers implemented at P2 close.
- **F.PER-USER-AUTHORITY-MECHANISM event-emission contract.** Per S1903 §19 inheritance, design HAI event candidates for per-user authority resolution triggers. Not the mechanism; the event-emission contract that downstream per-user authority resolution will consume.

**Deliverable path:** `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md` per playbook §11.2 template modified for design-contract framing (§11.2 §7 Runtime Flows → §7 HAI Event Schema Contract; §11.2 §12 Research Coverage → §12 Schema Alternatives Rejected; §11.2 §17 Duplicate or Overlapping Systems → §17 Consumer Registry + Retention Posture).

**Prereqs:**

- S2001 P1 shipped (α + γ current-state as baseline; F14/F15 handler-failure constraints).
- S1275 event schema design shipped.
- S1806 §10 durable-at-six catalog shipped.
- R.HAI.SOURCE-KIND-ENUM-ADR enum values (parked T0/Gate; P2 inherits enum shape but does not re-open joint ADR scope).

**Rigby SIGN cadence:** Cycle 1 pre-commit REQUIRED + optional Cycle 2 post-Chris-gate to pressure-test the versioning-policy choice.

**Chris-gate:** Multi-verdict at close — D8N-series covering each of (a) schema per transition + (b) versioning policy + (c) retention posture + (d) consumer registry. Design contract, not full implementation.

## Session-open protocol (universal)

1. `context-kit orient` — source-of-truth chain + latest handoff.
2. Absorb this `CLAUDE.md` + `MEMORY.md` (both auto-injected).
3. Read this `00-START-NEXT-SESSION.md` in full.
4. Read Research OS §0–§5 (skim §6–§9 headings).
5. Record repo state (branch + SHA + `git status`).
6. Note request context (change vs explain; explicit constraints; for bugs: repro path).
7. Classify the request via OS §5 router → load the matching §8 startup contract.
8. If PA calls will happen: verify `service_context: local` via `platform_config_tool overview`.
9. Verify arc pin `pa-dd7e973617da464d` still routed via `tools/pa_local.sh:215` (Group 2000+ arc-standard).

## Post-commit docs cascade for S2001 close

Per `feedback_docs_cascade_at_every_close.md` + `feedback_cascade_pr_must_include_embed_step.md` — MUST run all 4 steps after commit merges:

1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py embed_documents --all-unembedded` (state chunk count in PR body as evidence)

Then `python manage.py build_docs_provenance` per §11.4 provenance discipline.
