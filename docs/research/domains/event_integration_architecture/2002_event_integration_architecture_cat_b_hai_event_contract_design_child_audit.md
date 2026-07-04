---
title: "Group 2000+ — Cat B — HAI Event Contract Design (S2002 P2)"
status: draft
session: 2002
child_slot: P2_cat_b
domain_slug: event_integration_architecture
research_group: 2000
mission_type: child_audit
date: 2026-07-04
authority: |
  P2 child audit under Group 2000+ Event / Integration Architecture arc.
  Scope inherited from parent scoping §5.2
  (`2000_event_integration_architecture_domain_scoping.md`), which
  itself consumes S1899 §8.1 item 6
  (R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES), S1806 §10 durable-at-six
  event-emission gap catalog, S1275 event schema precedent
  (per-event `schema_version` field with graduation contract), S2001
  §10.4 γ current-state baseline (no versioning), and S2000 SIGN
  cycle 1 Q1 fold (authority MECHANISM out-of-scope; contract
  semantics only).

  This doc is DESIGN CONTRACT only. It defines the event-emission
  contract semantics for four HAI candidate transitions
  (`record_decision`, `record_verification`, `auto_approve`,
  `auto_escalate`), the six-plane learning-surface event schema
  (with `source_kind` enum adoption), the schema-versioning policy
  go-forward pick, retention posture per event class, consumer
  registry per event, and the F.PER-USER-AUTHORITY-MECHANISM
  event-emission contract inherited from S1903 §19.

  Explicit non-scope, per playbook §14.5 no-implementation rule and
  parent §5.2 scope guardrail:
  - Does NOT design authority MECHANISM (resolution logic,
    AuthorityService reads, per-user policy binding). Contract
    semantics only — the events downstream authority resolution
    consumes; not the resolution itself.
  - Does NOT ship EventBus wrapper changes, model migrations,
    beat-schedule enrollment, consumer subscription code, or DLQ
    consumer implementation.
  - Does NOT re-open the joint T0/Gate ADRs R.HAI.SOURCE-KIND-ENUM-ADR
    (parked Group 1300 + Group 1800), R.OBSERVABILITY.RETENTION-
    UNIFIED-ADR (Group 1700), or R.HAI.RETENTION-UNIFIED-ADR
    (Group 1800). P2 inherits enum shape + retention posture inputs;
    the ADRs themselves remain post-arc.
  - Does NOT re-scope Group 1900 authority enforcement (P2 designs
    the event-emission contract that per-user authority resolution
    downstream in Group 1900 will consume — the mechanism is
    Group 1900's).
  - Does NOT re-scope P3 (Cross-Substrate Composition Design,
    S2003) — P2 designs HAI-specific event schemas; P3 designs the
    6-substrate assignment rules that decide which substrate any
    given HAI event lands on.
  - Does NOT re-open S1806 §10 durable-at-six catalog. Consumes as
    prior work.
  - Does NOT execute R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE (S1899
    §8.1 T0/Gate CRITICAL, 4 break-points A/B/C/D). P2 designs
    event-emission contract; the loop repair is post-arc but is a
    documented pre-condition for full contract adoption.

  Load-bearing inheritance chain re-attested at S2002 open:
  - S2001 §10.2 α (schema-shape doc per stream — 8 streams + 1 DLQ
    baseline).
  - S2001 §10.3 β (runtime assert audit — universal zero-assert
    finding).
  - S2001 §10.4 γ (version gate policy current state — no versioning).
  - S2001 §10.5 δ (replay-test enumeration — EventBus.replay() exists
    with zero callers).
  - S2001 F9 CRITICAL (4 of 5 consumer beat tasks unscheduled —
    contract adoption requires beat enrollment or contract remains
    dormant).
  - S2001 F11 HIGH (three substrates for spider-data → agents —
    inherits forward to S2003 P3, not P2).
  - S2001 F12 HIGH (schema_version not adopted — γ baseline for
    P2 policy pick).
  - S2001 F14/F15 (handler-failure DLQ gap — retention posture must
    account for handler-failed events, not just parse-errors).
  - S1275 §7.1 (`schema_version` field definition — semver string
    top-level required field).
  - S1275 §7.3 (optional fields + rationale table — reserved-keys
    policy inheritance).
  - S1275 §7.5 (major/minor bump graduation contract).
  - S1275 §11 (mapping confidence DEFINITE/DECLARED/HEURISTIC/UNKNOWN).
  - S1275 §12 (drift detection strategy — NULL rate + wrong non-NULL
    + stale producer).
  - S1806 §10 durable-at-six event-emission gap catalog
    (six-plane taxonomy: HAI-mediated, autonomous_bridge,
    non_bridge_direct, verification_outcome, external_signal,
    shadow_service).
  - S1899 §8.1 item 6 R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES parent
    scope; item 3 R.OBSERVABILITY.RETENTION-UNIFIED-ADR pairing;
    item 4 R.HAI.RETENTION-UNIFIED-ADR pairing; item 5
    R.HAI.SOURCE-KIND-ENUM-ADR enum shape inheritance.
  - S1903 §19 F.PER-USER-AUTHORITY-MECHANISM event-emission contract
    inheritance (contract only; mechanism deferred).
companion_docs:
  - docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md
  - docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md
  - docs/research/symbol_mapping_event_schema_design.md
  - docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md
  - docs/research/domains/human_attention/1899_human_attention_canonical_summary.md
  - docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_child_audit.md
  - docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/EVENT_SYSTEM_INVENTORY.md
verifier_loop: |
  Pre-Explore (playbook §14 MC-1 REQUIRED, CODIFICATION-CONFIRMED at
  S1899 close). Direct file:line reads before any sub-agent dispatch:

  (a) `HumanAttentionItem.record_decision` at
      `core/models_human_interface.py:184-214` — signature
      `def record_decision(self, decision: str, feedback: str='',
      confidence: float=None)`. Body creates HumanFeedbackRecord
      row + updates HAI status. NO EventBus emission at HEAD; a
      Django `post_save` signal on HumanFeedbackRecord fires the
      S1802 FeedbackProcessor with best-effort exception-swallow.
      Callers: `HumanInterfaceService.record_decision` at
      `human_interface_service.py:295-353`, REST endpoint
      `/api/human/attention/<id>/decide/` at `views_human_interface.py:245`,
      `BulkAttentionDecideView.post` (needs refactor per T2.5).
  (b) `HumanAttentionItem.record_verification` at
      `core/models_human_interface.py:216-227` — signature
      `def record_verification(self, outcome: str, profit: float=None,
      notes: str='')`. Body updates HAI verification-tier fields
      (:155-163). NO event, NO signal, NO log. Callers: REST at
      `views_human_interface.py:245`,
      `BettingOutcomeVerifier._verify_arb_item` at
      `betting_outcome_verifier.py:413` (automated caller
      UNSCHEDULED per S1805 F1).
  (c) `HALifecycleService.auto_approve_item` at
      `core/services/human_attention_lifecycle.py:298-325` — signature
      `def auto_approve_item(self, item, reason: str='...')`. Body
      creates HumanFeedbackRecord directly at :325 (bypasses
      `record_decision()` — S1802 Q2 orphan + S1899 §1 break-point B),
      sets HAI status='auto_approved', writes `fed_to_ml=False`.
      NO event fired. Caller: `HALifecycleService._auto_approve_low_risk_items`
      at :223-296, invoked by Celery beat task
      `process_human_attention_lifecycle` at `core/tasks.py:560`
      (every 10 min).
  (d) `auto_escalate` — DOES NOT EXIST AT HEAD. Verified via
      `grep -n "def auto_escalate\|def auto_escalate_item"` across
      `core/`. Zero matches. F7 CRITICAL break-point D per S1899 §1
      (inherited S1801 D5). Escalation path unowned.
  (e) `OrchestratorApprovalRequest.auto_approve` at
      `core/models_orchestration.py:503-508` — distinct method on a
      DIFFERENT model (governance domain), NOT the HAI lifecycle
      `auto_approve`. F0 boundary risk: two methods named
      `auto_approve` in two apps — HAI event contract MUST
      disambiguate. Not the P2 candidate; documented here to prevent
      cross-substrate confusion.
  (f) `HumanFeedbackRecord` at `core/models_human_interface.py` —
      FK to HumanAttentionItem + fields (decision, feedback_text,
      confidence, ml_prediction JSON, ml_confidence, human_agreed_with_ml,
      fed_to_ml bool). 36-line class. Post-save signal fires
      FeedbackProcessor.
  (g) `HumanPreference` at `core/models_human_interface.py` — 3-plane
      model (governance / learning / notification). Reads:
      `auto_approve_low_risk` flag consumed by HALifecycleService.
      Update-path: `_update_preferences_from_decision` — S1804 owner
      + Cat D scope.
  (h) `EventStream` enum at `core/services/event_bus.py:21-30` —
      8 stream values verified at S2001 pre-Explore. Zero HAI-adjacent
      streams. No `HAI_DECISION_RECORDED`, `HAI_VERIFICATION_RECORDED`,
      `HAI_AUTO_APPROVED`, `HAI_AUTO_ESCALATED` streams exist at HEAD.
      P2 designs the contract; enum extension is post-arc
      implementation.
  (i) `STREAM_MAX_LEN = 10000` at `event_bus.py:104`. `DEAD_LETTER_STREAM
      = "mi:dead_letter"` at :106 with `maxlen=1000` (S2001 F16
      correction). Retention baseline for P2 retention-posture pick.
  (j) `schema_version` grep across `event_bus.py` and
      `models_human_interface.py` — 0 matches. γ current-state:
      no versioning (S2001 §10.4 γ verified).
  (k) `source_kind` grep across `core/models*.py` and
      `core/services/*.py` — 0 matches. Enum values parked in
      R.HAI.SOURCE-KIND-ENUM-ADR T0/Gate; not yet materialized in
      code. P2 designs shape; implementation is post-arc.
  (l) S1275 event schema doc at
      `docs/research/symbol_mapping_event_schema_design.md`
      §7.1-§7.5 — read in full at S2002 open. Semver string,
      top-level required, major/minor graduation contract, fail-open
      on unknown version.
  (m) S1899 §8.1 items 3/4/5/6 — read in full at S2002 open.
      Retention ADRs, source_kind ADR, HAI event contract candidates
      parked as T0/Gate.
  (n) S1806 §10 durable-at-six catalog — read in full at S2002 open.
      Six-plane taxonomy, per-plane event-emission gap, per-plane
      model reference.
  (o) S2001 F9 CRITICAL — 4 of 5 EventBus consumer beat tasks
      unscheduled. Load-bearing constraint for P2 consumer registry:
      an event contract without beat enrollment produces
      contract-on-paper-only. P2 §17 consumer registry MUST specify
      beat enrollment as a first-class contract obligation, not an
      implementation detail.

  Sub-agent dispatches: 1 Explore agent at S2002 open (prereq
  gathering across S1275 + S1806 + S1899 + code substrate).
  Per playbook §14 MC-1 CODIFICATION-CONFIRMED — Pre-Explore
  discipline satisfied by (a)-(o) direct file:line reads;
  Explore agent used to compact prereq context, not to source
  primary evidence. Every design assertion in §7-§17 cites
  file:line evidence from (a)-(o) direct reads OR S2001/S1899/
  S1806/S1275 with explicit §-reference.

  Zero-UNKNOWN attestation (inherits S2001 Rigby SIGN emphasis #1):
  every one of the 4 candidate transitions has a payload schema
  AND a retention posture AND a consumer registry entry. Where a
  transition (auto_escalate) has no current implementation, that is
  documented explicitly as MISSING with recommended contract
  shape — not parked as UNKNOWN.

  Evidence-backed attestation (inherits S2001 Rigby SIGN emphasis #2):
  every payload field cites current-code model field (file:line)
  OR is marked NEW with design rationale. Every versioning-policy
  claim cites S1275 §-reference. Every retention TTL claim cites
  either R.OBSERVABILITY.RETENTION-UNIFIED-ADR posture or
  R.HAI.RETENTION-UNIFIED-ADR posture with explicit T0/Gate
  attribution.

  Stream-by-stream discipline (inherits S2001 Rigby SIGN emphasis #3):
  §7.1-§7.4 use per-transition table format (record_decision,
  record_verification, auto_approve, auto_escalate rows). §10.2-§10.6
  use per-plane table format (six planes). §17.2 uses per-consumer
  table format.

  Design-alternative rejection posture (P2-specific): §12 documents
  three schema alternatives considered + rejected (in-envelope
  schema_version vs external registry table vs implicit-from-topic-
  name) with rationale. §12.5 documents two retention posture
  alternatives considered + rejected.
---

# Session 2002 — Group 2000+ Cat B — HAI Event Contract Design

## 1. Executive Summary

Session 2002 designs the event-emission contract for the four HAI
candidate transitions (`record_decision`, `record_verification`,
`auto_approve`, `auto_escalate`) that the S1899 canonical summary
parked as R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES at T0/Gate, plus
the six-plane learning-surface event schema (adopting `source_kind`
enum values from R.HAI.SOURCE-KIND-ENUM-ADR), plus the schema
versioning go-forward policy (adopting the S1275 precedent), plus
the retention posture (per-event-class TTL + Redis Streams MAXLEN
posture pairing), plus the consumer registry (per event, the
expected consumers + their subscription contract obligations), plus
the F.PER-USER-AUTHORITY-MECHANISM event-emission contract
inherited from S1903 §19 (contract semantics only; mechanism
deferred to Group 1900).

**What P2 ships:**

- **§7 HAI Event Schema Contract** — Per-transition payload
  schema for the 4 candidates. Each with envelope fields
  (`schema_version`, `event_type`, `emitted_at`, `producer`,
  `source_kind`), typed payload fields (mapped 1:1 to existing
  HAI/HFR/HumanPreference model fields where possible, with NEW
  fields flagged and justified), required vs optional per field,
  and consumer contract shape. `auto_escalate` is documented as
  MISSING implementation with recommended contract shape.
- **§10 Event Flows — six-plane learning-surface event schema.**
  Per-plane transition event, per-plane payload shape, per-plane
  `source_kind` enum value binding. Six planes: HAI-mediated,
  autonomous_bridge, non_bridge_direct, verification_outcome,
  external_signal, shadow_service.
- **§12 Schema Alternatives Rejected (renamed from Research Coverage
  per §11.2 template modification).** Three schema-versioning
  alternatives considered + rejected (in-envelope
  semver vs external registry table vs implicit-from-topic-name).
  Adopts S1275 precedent (per-event `schema_version` field with
  major/minor graduation contract) with justification.
- **§17 Consumer Registry + Retention Posture (renamed from
  Duplicate/Overlapping Systems per §11.2 template modification).**
  Per event, the expected consumer group(s) + subscription contract
  obligations + beat-enrollment requirement (F9 CRITICAL S2001
  constraint). Retention posture: pairs with
  R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.HAI.RETENTION-UNIFIED-ADR
  T0/Gate parked ADRs; recommends TTL per event class + Redis
  Streams `MAXLEN` posture + audit-table retention hybrid where
  durable auditability required.
- **§20.9 F.PER-USER-AUTHORITY-MECHANISM event-emission contract**
  — Per S1903 §19 inheritance: HAI event candidates for per-user
  authority resolution triggers. Contract semantics only;
  mechanism (resolution logic, AuthorityService reads, per-user
  policy binding) OUT-OF-SCOPE per parent §5.2 + Rigby S2000 SIGN
  cycle 1 Q1 fold.

**Design decisions load-bearing to the arc:**

- **D1 Adopt S1275 per-event `schema_version`.** Semver string,
  top-level envelope field, required, fail-open on unknown version
  at consumer. Rationale: S1275 shipped a graduation contract that
  handles both greenfield (this arc) and evolution (subsequent
  arcs); a second policy would fragment schema discipline.
  Justification body in §12.1.
- **D2 Adopt R.HAI.SOURCE-KIND-ENUM-ADR enum values as event
  envelope field.** Values: `HAI_mediated`, `autonomous_bridge`,
  `non_bridge_direct`, `verification_outcome`, `external_signal`,
  `shadow_service`, `other`. Justification body in §7.5.
- **D3 Adopt a two-class retention posture.** Class-1 governance
  events (record_decision + record_verification + auto_approve +
  auto_escalate) → durable, audit-table backed, no TTL. Class-2
  learning-surface events (bridge dispatch, plane transitions) →
  Redis Streams `MAXLEN=10000` bounded, no audit-table backup.
  Justification body in §17.3.
- **D4 Consumer registry adopts beat-enrollment as first-class
  contract obligation.** S2001 F9 CRITICAL: consumer registry
  entry without corresponding `PeriodicTask` row = contract-on-
  paper-only. §17 lists beat enrollment per consumer as a
  contract line item; adoption in later arcs MUST enroll the
  beat when subscribing.
- **D5 Adopt hybrid emission strategy per transition.** Not every
  transition needs an EventBus stream — `record_decision` +
  `record_verification` land on EventBus (governance visibility +
  cross-substrate handoff) but `auto_approve` + `auto_escalate`
  land on OpsRunEvent (system-initiated, audit-trail-forever
  posture matches OpsRun semantics). P3 finalizes 6-substrate
  assignment; P2 documents the recommended assignment for each
  candidate.

**F.PER-USER-AUTHORITY-MECHANISM inheritance (from S1903 §19):**
Design provides HAI event candidates that per-user authority
resolution (Group 1900 authority MECHANISM, out of scope here)
will consume: `authority_check_evaluated`, `authority_decision_
overridden`, `authority_policy_bound_to_user`. Contract semantics
only; the resolution logic remains post-arc.

**What P2 does NOT ship** (per §5.2 scope guardrail): authority
resolution logic; EventBus wrapper implementations; migrations;
beat schedule enrollment; DLQ consumer implementation; the joint
retention ADR resolutions; the source_kind enum ADR resolution.
All materialize post-arc.

**Runtime:** 1 session (this one). May extend if Rigby SIGN
cycle 1 discovers a versioning-policy fold requiring cycle 2
per parent §5.2 SIGN cadence.

## 2. Domain Purpose

### 2.1 What the P2 design contract represents

The HAI event contract is the boundary between the **HAI feedback
plane** (Human Attention Item lifecycle transitions — a human
decision, a verified sports outcome, a system-initiated auto-
approve, a lifecycle escalation) and the **learning + governance
consumers** downstream (FeedbackProcessor, SportsBettingLearning-
Bridge, ML retraining pipelines, per-user authority resolution,
observability dashboards, audit rows).

At HEAD, this boundary is invisible: HAI transitions fire only
Django post_save signals (best-effort exception-swallow per S1802
F7), which produces the S1806 durable-at-six event-emission gap
(no cross-substrate visibility, no structured payload, no version
gate, no retention posture, no consumer registry). P2 designs
the contract that makes this boundary durable, versioned, and
observable.

### 2.2 Why the contract is a design contract, not an implementation

Per parent §5.2 scope guardrail: P2 designs event-emission
**contract semantics** — schema, versioning, retention, consumer
registry, source_kind enum binding, per-user authority trigger
enumeration. P2 does NOT ship:

- EventBus wrapper implementations (`publish_hai_decision_
  recorded_event`, etc.) — post-arc.
- HAI model changes (adding envelope-field storage, `source_kind`
  column) — post-arc.
- Beat-schedule enrollment for HAI consumer workers — post-arc
  (but §17 documents beat enrollment as first-class contract
  obligation per D4).
- DLQ consumer for failed HAI events — post-arc.
- Migration to backfill `source_kind` on existing HFR rows —
  post-arc.
- The authority resolution mechanism (Group 1900 authority
  MECHANISM) — explicitly out of scope per parent §5.2 + Rigby
  S2000 SIGN cycle 1 Q1 fold.

The contract designed here is what a subsequent implementation
arc (post-arc) executes against. Its consumers are: (a) implementers
of HAI event emission sites, (b) subscribers designing HAI event
consumers, (c) the joint retention + source_kind ADR resolutions
(Group 1300 + Group 1700 + Group 1800), and (d) the Group 1900
authority MECHANISM arc consuming F.PER-USER-AUTHORITY-MECHANISM
event contracts.

### 2.3 Anti-scope

Explicitly outside P2's contract:

- **Authority resolution mechanism** — Group 1900 owns this. P2
  provides event candidates the resolution consumes; not the
  resolution itself.
- **Cross-substrate assignment rules** — P3 (S2003) owns "which
  substrate does this event land on across EventBus vs
  WebSocket vs CeleryTaskEvent vs LLMCallEvent vs OpsRunEvent
  vs ToolCallRecord?" P2 recommends per-transition per §7 D5;
  P3 finalizes the arbitration.
- **Loop-coupling repair** — S1899 §8.1 R.HAI.LOOP-COUPLING-
  REPAIR-ADR-BUNDLE (T0/Gate CRITICAL) is a pre-condition for
  full contract adoption. P2 designs contract shape; the repair
  materializes 4 break-points A/B/C/D and enables the contract
  to close (not itself P2's work).
- **Migration to backfill history** — Any implementation arc
  adopting the contract must decide whether to backfill
  `source_kind` on existing HFR rows. Not designed here.
- **Consumer implementations** — §17 lists expected consumers +
  contract obligations; implementations are post-arc.

## 3. Canonical Entry Points

The design contract is written from the current-code entry points
where each transition materializes. Adopters implement emission
sites at these entry points.

### 3.1 record_decision entry points

- **Model method:** `HumanAttentionItem.record_decision` at
  `core/models_human_interface.py:184-214`. Signature
  `record_decision(self, decision: str, feedback: str='',
  confidence: float=None)`. Creates HFR row + updates HAI
  status.
- **Service method:** `HumanInterfaceService.record_decision` at
  `core/services/human_interface_service.py:295-353`. Public
  service surface; wraps model method + fires post_save signal.
- **REST endpoint:** `POST /api/human/attention/<id>/decide/`
  wired at `core/views_human_interface.py:245` — direct model
  method call.
- **Bulk endpoint:** `BulkAttentionDecideView.post` — S2001 T2.5
  refactor pending.

**Emission site recommendation (§7.1):** Emit at
`HumanInterfaceService.record_decision:353` (after HFR persistence
+ before signal fires). Rationale: single-emission site avoids
the signal-fanout ambiguity; REST + bulk paths route through the
service; a future emission wrapper at the model method fires on
every write regardless of caller path.

### 3.2 record_verification entry points

- **Model method:** `HumanAttentionItem.record_verification` at
  `core/models_human_interface.py:216-227`. Signature
  `record_verification(self, outcome: str, profit: float=None,
  notes: str='')`.
- **REST endpoint:** `POST /api/human/attention/<id>/verify/` at
  `core/views_human_interface.py:245`.
- **Automated caller:** `BettingOutcomeVerifier._verify_arb_item`
  at `core/services/betting_outcome_verifier.py:413` (UNSCHEDULED
  per S1805 F1 — a durable emission contract MUST resolve this
  or events fire only on manual REST calls).

**Emission site recommendation (§7.2):** Emit at
`HumanAttentionItem.record_verification:227` (model method exit).
Rationale: 2-caller topology + no service-layer wrapper today;
model-method emission catches both REST + BettingOutcomeVerifier
paths. Requires S1805 F1 beat enrollment resolution as
pre-condition for automated caller to fire.

### 3.3 auto_approve entry points

- **Service method:** `HALifecycleService.auto_approve_item` at
  `core/services/human_attention_lifecycle.py:298-325`. Creates
  HFR directly at :325 with `fed_to_ml=False` (bypasses
  `record_decision()` — S1802 Q2 orphan + S1899 §1 break-point B).
- **Caller:** `HALifecycleService._auto_approve_low_risk_items`
  at :223-296 (internal).
- **Beat task:** `process_human_attention_lifecycle` at
  `core/tasks.py:560` (every 10 min).

**Emission site recommendation (§7.3):** Emit at
`HALifecycleService.auto_approve_item:325` (after HFR persistence).
Rationale: single-caller topology (only `_auto_approve_low_risk_
items` calls `auto_approve_item`, which in turn is only called by
the beat task); a single emission at the service method covers
the full path. Explicit non-recommendation: do NOT emit from
`record_decision()` — auto_approve is a distinct semantic event
(system-initiated, `human_agreed_with_ml=None`, `fed_to_ml=False`)
and conflating with human-initiated `record_decision` breaks the
downstream consumer contract at §17.

### 3.4 auto_escalate entry points

**DOES NOT EXIST AT HEAD** — F7 CRITICAL break-point D per S1899
§1 (inherited S1801 D5). Escalation path unowned.

**Recommended contract shape (§7.4):** New method
`HumanAttentionItem.auto_escalate(self, reason: str)` at model
layer. Callers TBD (candidate: `HALifecycleService._escalate_
stale_items` at a new service method, invoked by a new beat
task or extended `process_human_attention_lifecycle`).

**Emission site recommendation:** Emit at
`HumanAttentionItem.auto_escalate` (new method) on entry.
Rationale: escalation is a system-initiated boundary event;
consumers (authority resolution, on-call notification, ML
retraining feedback) require the event fires unconditionally,
before any downstream state change.

**Pre-condition:** S1899 §8.1 R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE
T0/Gate CRITICAL must resolve break-point D before the emission
site materializes. P2 designs contract; the escalation method
itself materializes post-arc.

### 3.5 Six-plane learning-surface entry points

Per S1806 §10 six-plane taxonomy — the plane-transition events
are new (no current emission sites). Recommended entry points
per §10:

| Plane | Recommended emission entry point | Current code substrate |
|---|---|---|
| HAI-mediated | `HumanInterfaceService.record_decision:353` | ✓ Live |
| autonomous_bridge | Per-bridge `dispatch()` method exit (9 bridges) | ✓ Live (9 receivers) |
| non_bridge_direct | 4 non-bridge write sites (revenue/models.py, core/models/jobs, td_handlers_content.py, agent_execution_learning_bridge.py) | ✓ Live |
| verification_outcome | `HumanAttentionItem.record_verification:227` | ✓ Live |
| external_signal | RedditLearningBridge + BlueskyLearningBridge dataclass return sites | ✓ Live (D6 dead-code status) |
| shadow_service | Redis pubsub emission sites in AgentLearningEngine / PersistentLearningEngine | ✓ Live (unused) |

### 3.6 F.PER-USER-AUTHORITY-MECHANISM entry points

Per S1903 §19 inheritance — per-user authority resolution triggers
that emit HAI event candidates. Entry points are those where
current authority resolution logic reads or writes.

- **Authority check evaluated:** wherever a decision is guarded
  by an `AuthorityService.check(...)` call. Currently distributed;
  Group 1900 authority MECHANISM will centralize. P2 designs
  event contract shape.
- **Authority decision overridden:** wherever a manual override
  fires. Rare path; contract designed for future auditability.
- **Authority policy bound to user:** wherever a policy binding
  writes to a PerUserAuthorityPolicy row (Group 1900 model, does
  not yet exist). Contract designed for future emission.

**Emission site recommendation:** Deferred to Group 1900 authority
MECHANISM arc. P2 designs the payload contract; the mechanism arc
picks emission sites.

## 4. Major Models

The event contract binds to five existing models + one anticipated
future model. All models are current-code (no P2 schema changes;
adopters may add fields post-arc per §12 versioning contract).

### 4.1 HumanAttentionItem

Location: `core/models_human_interface.py`.

Purpose: primary lifecycle model for a queued human-attention item.
8-state lifecycle: pending → viewed → deferred → watching → acted
→ verified (plus auto_approved + auto_escalated terminal / interim
states).

Fields consumed by P2 event contract:
- `id` (UUID) — HAI-item envelope key.
- `user_id` (FK) — actor scope.
- `status` (str) — 8-state enum.
- `verification_outcome`, `profit`, `notes`, `verified_at`,
  `event_completed_at` — verification-tier fields (:155-163).
- `created_at`, `updated_at` — envelope `emitted_at` derivation
  fallbacks.

**No P2 schema changes on this model.** Future implementation
arc may add `source_kind` and `authority_scope` columns per D2
+ F.PER-USER-AUTHORITY-MECHANISM inheritance; that materializes
post-arc.

### 4.2 HumanFeedbackRecord (HFR)

Location: `core/models_human_interface.py`. 36-line class.

Purpose: durable record of a human decision (or system-initiated
auto-approve) on an HAI item.

Fields consumed by P2 event contract:
- `id` (UUID) — HFR envelope key.
- `hai_item_id` (FK) — parent HAI reference.
- `decision` (str) — enum of decision choices.
- `feedback_text` (str) — free-form feedback.
- `confidence` (float, 0-1) — reported confidence.
- `ml_prediction` (JSON) — ML system's prediction at decision time.
- `ml_confidence` (float, 0-1) — ML system's confidence.
- `human_agreed_with_ml` (bool | None) — agreement flag; None for
  auto_approve (no human comparison).
- `fed_to_ml` (bool) — whether row feeds ML retraining; False for
  auto_approve per HALifecycleService semantics.
- `created_at` (datetime) — envelope `emitted_at` fallback.

**No P2 schema changes.** Future implementation arc may add
`source_kind` per D2; post-arc.

### 4.3 HumanPreference

Location: `core/models_human_interface.py`. 3-plane model
(governance / learning / notification).

Purpose: per-user preference state; consumed by HALifecycleService
for auto-approve gating.

Fields consumed by P2 event contract:
- `user_id` (FK) — actor scope.
- `auto_approve_low_risk` (bool) — gates auto_approve emission.
- `update_learned_stats` (method) — updates on decision write.

**No P2 schema changes.** Note: S1804 Cat D owns HumanPreference
transitions; P2 emits events consuming the current schema. Future
`update_preferences_from_decision` emission is post-arc.

### 4.4 EventStream enum (existing 8 values)

Location: `core/services/event_bus.py:21-30`.

Current values (S2001 §10.1 baseline):
`SPIDER_DATA`, `OPPORTUNITY_CREATED`, `OPPORTUNITY_SCORED`,
`VALIDATION_REQUIRED`, `VALIDATION_DECIDED`, `OUTCOME_RECORDED`,
`MODEL_TRAINED`, `SYSTEM_ALERT`.

**Recommended P2 additions (post-arc implementation):**
- `HAI_DECISION_RECORDED` — record_decision emission stream.
- `HAI_VERIFICATION_RECORDED` — record_verification emission stream.
- `HAI_AUTO_APPROVED` — auto_approve emission stream.
- `HAI_AUTO_ESCALATED` — auto_escalate emission stream (materializes
  post-R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE break-point D).

**Anti-recommendation:** Do NOT reuse `OUTCOME_RECORDED` for
`record_verification`. `OUTCOME_RECORDED` is Session 470 phase-4
intended-for-ML-outcome semantics; conflating with HAI verification
(which is a governance/audit event) violates D5 per-transition
substrate discipline.

### 4.5 OpsRunEvent

Location: `core/models_ops_runs.py`.

Purpose: audit-table for system-initiated operations. Fields
include `domain`, `event_type`, `payload` (JSON), `occurred_at`.

Consumed by D5: `auto_approve` + `auto_escalate` land on
OpsRunEvent (audit-forever posture) instead of EventBus (bounded
retention). Full mapping in §17.

**No P2 schema changes.** OpsRunEvent already supports the
required envelope + typed payload.

### 4.6 PerUserAuthorityPolicy (anticipated future model)

Location: does not exist at HEAD.

Purpose: per-user authority resolution binding. Group 1900
authority MECHANISM will introduce.

P2 designs the event-emission contract that this future model
consumes; the model itself is out of scope. Contract designed
in §20.9 F.PER-USER-AUTHORITY-MECHANISM.

## 5. Major Services

### 5.1 HumanInterfaceService

Location: `core/services/human_interface_service.py`.

Owns: `record_decision` path (line 295-353); wraps model method +
signal fanout to FeedbackProcessor.

**Contract obligation:** Emits `HAI_DECISION_RECORDED` event per
§7.1 (recommended emission site at line 353, post-HFR persistence).

### 5.2 HALifecycleService

Location: `core/services/human_attention_lifecycle.py`.

Owns: `auto_approve_item` (line 298-325), `_auto_approve_low_risk_
items` (line 223-296), future `auto_escalate_item` (post-arc per
S1899 R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE break-point D
resolution).

**Contract obligation:** Emits `HAI_AUTO_APPROVED` per §7.3 +
future `HAI_AUTO_ESCALATED` per §7.4.

### 5.3 BettingOutcomeVerifier

Location: `core/services/betting_outcome_verifier.py`.

Owns: `_verify_arb_item` (line 413) + `_create_learning_records`
(line 127-135, only site coupling to SportsBettingLearningBridge —
S1805 F4 asymmetric).

**Contract obligation:** Emits `HAI_VERIFICATION_RECORDED` per §7.2
(via model method) + emits `verification_outcome` plane-transition
event per §10.4 (via bridge dispatch).

**Pre-condition:** S1805 F1 UNSCHEDULED beat resolution — without
enrollment, the automated verification path fires only on manual
REST calls.

### 5.4 FeedbackProcessor (S1802 owner)

Location: post_save signal handler on HFR.

Currently: exception-swallow best-effort per S1802 F7 defect.

**Contract obligation:** Consumer of `HAI_DECISION_RECORDED` +
`HAI_AUTO_APPROVED` events per §17.2. Should replace or supplement
the post_save signal path post-contract-adoption.

### 5.5 SportsBettingLearningBridge (S1803 owner)

Location: `core/services/learning_bridges/sports_betting_learning_
bridge.py`.

Currently: coupling only in `BettingOutcomeVerifier._create_
learning_records:127-135` — REST verifications never trigger
bridge (S1805 F4).

**Contract obligation:** Consumer of `HAI_VERIFICATION_RECORDED`
per §17.2. Post-contract-adoption, bi-directional coupling closes.

### 5.6 AuthorityService (future — Group 1900 owner)

Location: does not exist at HEAD (Group 1900 arc-open designs it).

**Contract obligation:** Consumer of F.PER-USER-AUTHORITY-MECHANISM
events per §20.9. Contract shape designed; mechanism deferred.

## 6. Major APIs and Interfaces

### 6.1 REST endpoints (existing)

- `POST /api/human/attention/<id>/decide/` — `record_decision` REST
  path.
- `POST /api/human/attention/<id>/verify/` — `record_verification`
  REST path.
- (No REST for `auto_approve` — internal Celery beat path only.)
- (No REST for `auto_escalate` — does not exist at HEAD.)

### 6.2 EventBus publish API (existing)

- `EventBus.publish(stream: EventStream, event: Event)` at
  `event_bus.py:132-190`.
- Publisher wrapper convention at `event_bus.py:539+` — 7 existing
  wrappers per S2001 §10.1.

**P2 contract obligation:** Recommended future wrappers per §7:
- `publish_hai_decision_recorded_event(hai_item_id, hfr_id, decision, ...)`.
- `publish_hai_verification_recorded_event(hai_item_id, outcome, profit, ...)`.
- `publish_hai_auto_approved_event(hai_item_id, hfr_id, reason, ...)`.
- `publish_hai_auto_escalated_event(hai_item_id, reason, ...)`.

Wrapper implementation is post-arc; contract designed here.

### 6.3 OpsRunEvent write API (existing)

- `OpsRunEvent.objects.create(domain=..., event_type=..., payload=..., occurred_at=...)`.

**P2 contract obligation:** `auto_approve` + `auto_escalate` write
to OpsRunEvent per D5 (audit-forever posture). Contract designed in
§17.3.

### 6.4 EventBus subscribe API (existing)

- `EventBus.subscribe(consumer_name, consumer_group, streams, handler)` at
  `event_bus.py:191-224`.

**P2 contract obligation:** Consumer registry per §17.2 lists
expected `consumer_group` names + streams to subscribe. Beat
enrollment per D4 is a first-class contract obligation.

### 6.5 source_kind enum (parked ADR)

Location: R.HAI.SOURCE-KIND-ENUM-ADR (S1899 §8.1 item 5, T0/Gate).

Values inherited (P2 does not re-open ADR scope):
`HAI_mediated`, `autonomous_bridge`, `non_bridge_direct`,
`verification_outcome`, `external_signal`, `shadow_service`, `other`.

**P2 contract obligation:** `source_kind` is a top-level envelope
field on every P2 event (§7 + §10). Enum value binding per
transition + per plane documented in §7.5 + §10.

## 7. HAI Event Schema Contract

*(§11.2 template modification: §7 Runtime Flows → §7 HAI Event Schema Contract per parent §5.2 design-contract framing.)*

This section is the core P2 deliverable. Per-transition contract:
envelope + payload + required-vs-optional per field + recommended
substrate per D5 + `source_kind` binding per D2 + retention posture
class per §17.3.

### 7.0 Common envelope (all HAI events)

Every P2 HAI event carries the following top-level envelope fields.
These are the S1275-precedent-adopted envelope + P2 additions.

| Field | Type | Required | Rationale | Source |
|---|---|---|---|---|
| `schema_version` | str (semver) | ✓ | Per-event versioning; fail-open on unknown at consumer | S1275 §7.1; D1 |
| `event_type` | str (enum) | ✓ | Discriminator for consumer dispatch | S1275 §7.1 |
| `event_id` | str (UUID) | ✓ | Idempotency + replay identity | S1275 §7.3 optional → P2 elevates to required for HAI events (audit posture) |
| `emitted_at` | datetime (ISO 8601 UTC) | ✓ | Event fire time; distinct from HAI row `created_at` | S1275 §7.1 |
| `producer` | str | ✓ | Emission site identity (service/module) | S1275 §7.1 |
| `producer_version` | str (semver) | ○ | Producer code version at emission | S1275 §7.3 |
| `source_kind` | str (enum) | ✓ | Enum per D2 (`HAI_mediated`, `autonomous_bridge`, etc.) | R.HAI.SOURCE-KIND-ENUM-ADR + D2 |
| `authority_scope` | str \| null | ○ | Per-user authority binding — populated when applicable; null when not | F.PER-USER-AUTHORITY-MECHANISM inheritance; §20.9 |
| `idempotency_key` | str | ○ | For at-least-once emission dedup | S1275 §7.3 |
| `mission_id` | str \| null | ○ | Employee OS mission correlation | S1275 §7.3 |
| `boundary_crossed` | str \| null | ○ | Cross-substrate emission trace (P3 inheritance) | S1275 §7.3 |
| `caller_actor` | str \| null | ○ | Actor role: `executor_actor` \| `sponsor_actor` \| `principal_user` | S1275 §7.2 + §9 |

Envelope fields not consumed by HAI events (declared for future
extension): none at P2. Envelope is intentionally aligned with
S1275 to allow cross-substrate consumer reuse.

**Envelope drift protection (S1275 §12 inheritance):** Consumers
MAY NOT invent ad-hoc envelope keys. Undeclared keys fire an
invariant warning and are dropped from projections. Producer
adherence: envelope population is centralized in the future
`publish_hai_*_event` wrapper functions; wrappers enforce
envelope shape at publish time.

### 7.1 record_decision event

**Event:** `HAI_DECISION_RECORDED`

**Recommended substrate:** EventBus stream `HAI_DECISION_RECORDED`
(new — post-arc enum extension). Rationale: cross-substrate
handoff to FeedbackProcessor consumer + observability dashboards
+ future ML retraining consumers. Fire-and-forget acceptable;
consumer dispatch is not synchronous with the REST response.

**source_kind:** `HAI_mediated` (per D2 + §10.1).

**Retention posture class:** Class-1 governance event (audit-table
backed via HFR row; EventBus stream capped at `MAXLEN=10000`).
Per D3.

**Emission site:** `HumanInterfaceService.record_decision:353`
(post-HFR persistence, before signal fanout).

**Payload:**

| Field | Type | Required | Source (model field / NEW) | Rationale |
|---|---|---|---|---|
| `hai_item_id` | str (UUID) | ✓ | `HumanAttentionItem.id` | Item identity |
| `hfr_id` | str (UUID) | ✓ | `HumanFeedbackRecord.id` | Feedback identity |
| `user_id` | str (UUID) | ✓ | `HumanAttentionItem.user_id` | Actor scope |
| `decision` | str (enum) | ✓ | `HumanFeedbackRecord.decision` | Decision choice |
| `feedback_text` | str | ○ | `HumanFeedbackRecord.feedback_text` | Free-form feedback (may be empty) |
| `confidence` | float (0-1) | ○ | `HumanFeedbackRecord.confidence` | Reported confidence |
| `ml_prediction` | JSON | ○ | `HumanFeedbackRecord.ml_prediction` | ML prediction at decision time |
| `ml_confidence` | float (0-1) | ○ | `HumanFeedbackRecord.ml_confidence` | ML confidence |
| `human_agreed_with_ml` | bool \| null | ○ | `HumanFeedbackRecord.human_agreed_with_ml` | Agreement flag |
| `fed_to_ml` | bool | ✓ | `HumanFeedbackRecord.fed_to_ml` | ML retraining feed flag |
| `prior_hai_status` | str (enum) | ✓ | Derived from HAI row pre-transition | State-transition context (S1275 §7.3 caller_actor peer) |
| `new_hai_status` | str (enum) | ✓ | Derived from HAI row post-transition | State-transition context |

**Consumer contract obligations:** See §17.2. Primary consumers:
FeedbackProcessor (replaces post_save signal per S1802 F7 repair
path), observability dashboards, future ML retraining ingestion.

**Alternative rejected:** Emit at model method
`HumanAttentionItem.record_decision:214` — rejected per §3.1 (single
service-layer site avoids signal-fanout ambiguity).

### 7.2 record_verification event

**Event:** `HAI_VERIFICATION_RECORDED`

**Recommended substrate:** EventBus stream
`HAI_VERIFICATION_RECORDED` (new — post-arc enum extension).
Rationale: cross-substrate handoff to SportsBettingLearningBridge
(closes S1805 F4 asymmetric coupling per §5.5 contract obligation).

**source_kind:** `verification_outcome` (per D2 + §10.4).

**Retention posture class:** Class-1 governance event (audit-table
backed via HAI verification-tier fields; EventBus stream capped at
`MAXLEN=10000`).

**Emission site:** `HumanAttentionItem.record_verification:227`
(model method exit — 2-caller topology per §3.2 requires model-
level emission).

**Payload:**

| Field | Type | Required | Source | Rationale |
|---|---|---|---|---|
| `hai_item_id` | str (UUID) | ✓ | `HumanAttentionItem.id` | Item identity |
| `user_id` | str (UUID) | ✓ | `HumanAttentionItem.user_id` | Actor scope |
| `outcome` | str (enum) | ✓ | `HumanAttentionItem.verification_outcome` (:155) | Outcome enum |
| `profit` | Decimal | ○ | `HumanAttentionItem.profit` (:157) | Profit / loss delta |
| `notes` | str | ○ | `HumanAttentionItem.notes` (:159) | Free-form notes |
| `verified_at` | datetime | ✓ | `HumanAttentionItem.verified_at` (:161) | Verification timestamp |
| `event_completed_at` | datetime \| null | ○ | `HumanAttentionItem.event_completed_at` (:163) | Underlying event completion time (sports event finish) |
| `verification_source` | str (enum) | ✓ | Derived: `REST` \| `automated_verifier` | Distinguishes manual vs automated caller |
| `prior_hai_status` | str (enum) | ✓ | Derived | State-transition context |
| `new_hai_status` | str (enum) | ✓ | Derived (typically `verified`) | State-transition context |

**Consumer contract obligations:** See §17.2. Primary consumers:
SportsBettingLearningBridge (closes S1805 F4), ML retraining
ingestion for outcome-based learning, observability dashboards.

**Alternative rejected:** Emit at
`BettingOutcomeVerifier._verify_arb_item:413` — rejected. Model-
level emission catches both REST + automated paths (§3.2). Emitting
at the automated caller only breaks the REST path.

### 7.3 auto_approve event

**Event:** `HAI_AUTO_APPROVED`

**Recommended substrate:** **OpsRunEvent** (per D5 hybrid emission
strategy). Rationale: `auto_approve` is a system-initiated
governance event with audit-forever posture; OpsRunEvent semantics
match (persistent audit row, no Redis-Streams bounded retention).
EventBus stream is redundant for this transition.

**source_kind:** `HAI_mediated` (per D2 + §10.1; system-initiated
but structured as human-side per HFR row semantics —
`human_agreed_with_ml=None` distinguishes).

**Retention posture class:** Class-1 governance event
(audit-table via OpsRunEvent row; no TTL). Per D3.

**Emission site:** `HALifecycleService.auto_approve_item:325`
(post-HFR persistence). Single-caller topology per §3.3.

**Payload (OpsRunEvent structure):**

- `domain = "human_attention"`
- `event_type = "hai_auto_approved"`
- `occurred_at = <emission time>`
- `payload = { ... envelope + P2 payload fields ... }`

**Payload fields inside OpsRunEvent.payload JSON:**

| Field | Type | Required | Source | Rationale |
|---|---|---|---|---|
| `hai_item_id` | str (UUID) | ✓ | `HumanAttentionItem.id` | Item identity |
| `hfr_id` | str (UUID) | ✓ | `HumanFeedbackRecord.id` (auto-created at :325) | Feedback identity |
| `user_id` | str (UUID) | ✓ | `HumanAttentionItem.user_id` | Actor scope |
| `reason` | str | ✓ | `auto_approve_item(reason=...)` param | Approval rationale |
| `system_confidence` | float (0-1) | ✓ | Hard-coded `1.0` per HALifecycleService semantics | System-initiated confidence |
| `low_risk_criteria_matched` | list[str] | ○ | Derived from `_auto_approve_low_risk_items` selection logic | Which criteria fired |
| `preference_gate` | bool | ✓ | `HumanPreference.auto_approve_low_risk` at emission time | Gate flag verification |
| `fed_to_ml` | bool | ✓ | Hard `False` per HALifecycleService semantics | ML retraining feed flag |
| `prior_hai_status` | str (enum) | ✓ | Derived (typically `pending`) | State-transition context |
| `new_hai_status` | str (enum) | ✓ | Derived (typically `auto_approved`) | State-transition context |

**Consumer contract obligations:** See §17.2. Primary consumers:
observability dashboards (audit trail), governance visibility
surfaces, future FeedbackProcessor extension for auto-approve-
aware ML retraining semantics.

**Alternative rejected:** Emit on EventBus stream
`HAI_AUTO_APPROVED` — rejected per D5. Auto-approve is not a
cross-substrate handoff; the primary consumer is audit/observability,
not a real-time bridge. OpsRunEvent is the correct substrate.

### 7.4 auto_escalate event (RESERVED — Rigby S2002 SIGN cycle 1 batch 3 Q8 FOLD)

**Event:** `HAI_AUTO_ESCALATED` (RESERVED event type)

**Status per SIGN batch 3 Q8 FOLD:** Reduced to **conditional +
minimal reserved contract** per SIGN discipline. Full payload
schema deferred to §20.14 as **non-binding draft** pending
R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE T0/Gate CRITICAL
break-point D resolution.

**Rationale:** Shipping a fully-specified contract before the
mechanism exists risks encoding assumptions (e.g., per-escalation
emission vs time-window aggregation; deferred-auto-reopen vs
escalation-ladder-N-th-position vs unbounded-attention-decay-
signal) that break-point D resolution may invalidate. Reserved
minimal shape keeps forward alignment without locking in wrong
semantics.

**Pre-condition:** R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE
break-point D resolution — must implement
`HumanAttentionItem.auto_escalate` method + owner service +
callers.

**Minimal reserved contract (this event is legitimately declared
at v0.x pending resolution):**

**Reserved substrate posture:** Canonical EventBus stream
`HAI_AUTO_ESCALATED` + REQUIRED OpsRunEvent mirror per §7.9
canonical+mirror rule. Locked in reserved contract; canonical
substrate change is a major bump.

**Reserved envelope:** All §7.0 required envelope fields
(schema_version, event_type, event_id, emitted_at, producer,
source_kind, and payload plane discriminators per §10.0).

**Reserved required payload fields (MINIMAL — locked pre-resolution):**

| Field | Type | Required | Rationale |
|---|---|---|---|
| `event_id` | str (UUID) | ✓ | Envelope; per §7.0 |
| `hai_item_id` (aka `source_object_id`) | str (UUID) | ✓ | Item identity — the object being escalated |
| `user_id` | str (UUID) | ✓ | Actor scope |
| `escalation_reason_code` | str (enum) | ✓ | Reason enum — pre-resolution enum members TBD; MUST be present + non-null at emission |
| `triggering_signal_ref` | str \| null | ✓ | Reference to upstream trigger (deferred-auto-reopen source, time-window aggregate window ID, attention-decay signal ID); may be null if root-cause emission but MUST be declared |
| `occurred_at` | datetime (ISO 8601 UTC) | ✓ | Envelope; per §7.0 |

**source_kind:** `HAI_mediated` (per D2; reserved).

**Retention posture class:** Class-1 governance event (per D3;
reserved).

**Emission site:** `HumanAttentionItem.auto_escalate` (new method,
post-resolution) OR alternative site TBD. Emission ordering:
canonical EventBus first + mirror OpsRunEvent second on
`transaction.on_commit`.

**Payload schema TBD (non-binding pending break-point D
resolution):** Full payload schema — see §20.14 (`Proposed Draft
Schema for HAI_AUTO_ESCALATED — non-binding pending break-point D
resolution`). Fields such as `time_since_created`,
`time_since_last_view`, `escalation_ladder_position`,
`prior_hai_status`, `new_hai_status`, `notification_targets`
appear in §20.14 as candidate additions — but they are OPTIONAL
until R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE break-point D
resolves.

**Versioning note (SIGN batch 3 Q8 FOLD):** Any implementation
that deviates from the §20.14 proposed draft schema may ship as
v1.0.0 upon break-point D resolution. Pre-resolution artifacts
are v0.x and **non-binding**. This is the only P2 event that
ships at v0.x; the other three (§7.1-§7.3) ship at v1.0.0 on
adoption.

**Consumer contract obligations:** See §17.2. Primary consumers:
on-call notification, observability dashboards, future ML
retraining ingestion for attention-decay signal, per-user
authority resolution (Group 1900 F.PER-USER-AUTHORITY-MECHANISM).
Consumers subscribe to the reserved event type; must accept
v0.x → v1.0.0 major bump on payload finalization.

**Alternative rejected:** Design full contract now over Rigby SIGN
batch 3 Q8 rejection — pre-resolution assumptions risk locking in
wrong semantics per SIGN fold.

### 7.5 source_kind enum binding per transition

Per D2 — the `source_kind` envelope field carries an enum value
that identifies the semantic origin of the event. Value binding
per P2 transition:

| Transition | `source_kind` value | Rationale |
|---|---|---|
| `record_decision` (human-initiated) | `HAI_mediated` | Human decision through feedback plane |
| `record_verification` (REST + automated) | `verification_outcome` | Verified sports/arb outcome; distinct plane |
| `auto_approve` (system-initiated) | `HAI_mediated` | System-initiated but structured as HAI-plane (HFR row created; `human_agreed_with_ml=None` distinguishes from human decision) |
| `auto_escalate` (system-initiated) | `HAI_mediated` | System-initiated within HAI plane |

Per D2 + R.HAI.SOURCE-KIND-ENUM-ADR — value set:
`HAI_mediated`, `autonomous_bridge`, `non_bridge_direct`,
`verification_outcome`, `external_signal`, `shadow_service`,
`other`.

**Cross-plane binding for §10 six-plane events:** each plane's
transition event carries a distinct `source_kind` value per
§10.1-§10.6. This is the load-bearing cross-plane query enabler
per S1806 §10 durable-at-six catalog motivation.

### 7.6 Payload field inheritance from S1275 §7.3 optional set

S1275 §7.3 declared 5 optional envelope fields:
`idempotency_key`, `caller_actor`, `producer_version`, `mission_id`,
`boundary_crossed`. P2 inherits all 5 as optional envelope fields
(§7.0). Rationale: cross-substrate consumer reuse; adopting a
subset would fragment consumer implementations.

**Elevation of `event_id` from optional to required (HAI-specific):**
S1275 §7.3 places `event_id` as optional; P2 elevates to required
for HAI events. Rationale: HAI audit posture requires idempotent
replay; a UUID envelope key is minimal cost. Compatibility: this
is an HAI-event-only elevation and does NOT alter S1275 policy
for other event families.

### 7.7 Cross-transition consistency rules

Every P2 event MUST satisfy the following invariants at emission:

1. **Envelope shape (§7.0):** All required envelope fields
   present + non-null. `source_kind` present + one of the
   R.HAI.SOURCE-KIND-ENUM-ADR values.
2. **Actor triple:** `user_id` in payload matches
   `caller_actor.principal_user` in envelope where declared.
   Mismatches fire an invariant warning.
3. **State-transition invariant:** `prior_hai_status` +
   `new_hai_status` must be a legal transition in the HAI
   8-state lifecycle. Illegal transitions fire an invariant
   warning + are logged; event still emits (fail-open).
4. **Idempotency:** `event_id` MUST be unique per event
   emission. Duplicate emission within same producer session
   is a bug; consumers dedupe on `event_id`.
5. **Timestamp discipline:** `emitted_at` MUST be >= source-row
   `updated_at` where applicable. Emission-before-write is a
   bug; contract does not attempt to detect (consumer-side
   invariant).

### 7.9 Canonical emission + mirror policy (Rigby S2002 SIGN cycle 1 batch 2 Q4 STRENGTHEN)

Per Rigby SIGN cycle 1 batch 2 Q4 STRENGTHEN — the D5 hybrid
emission strategy is refined: EventBus-first canonical + OpsRunEvent
mirror-audit is the correct pattern, not competing-canonical.

**Canonical emission rule.** For each of the 4 HAI candidate
transitions (§7.1-§7.4), the **canonical** event emission is on
EventBus (Redis Streams). EventBus is the system-of-record for
pub/sub semantics; downstream consumers subscribe uniformly across
all 4 candidate transitions.

**Mirror-audit rule.** For Class-1 governance events requiring
audit-forever posture (`auto_approve` + `auto_escalate` +
`record_decision` (optional mirror) + `record_verification`
(optional mirror)), a **mirror** OpsRunEvent write MAY accompany
the canonical EventBus emission, with:

- Same `event_id` (envelope UUID) tying canonical + mirror.
- Explicit `source_event_stream` field on the OpsRunEvent payload
  identifying which EventBus stream the mirror derives from.
- Emission ordering: canonical EventBus emission fires FIRST +
  mirror OpsRunEvent write follows on `transaction.on_commit`
  hook.

**Forbidden posture.** Emitting two independent events with
different `event_id` values for the same transition is forbidden.
Adopters MUST NOT create parallel canonical identities across
substrates.

**S1275 §7.5 substrate-change rules (extended per SIGN fold):**

- **Changing the canonical substrate for a transition** (e.g.,
  moving `auto_approve` from EventBus to only-OpsRunEvent) is a
  **major bump** on the affected event's `schema_version`.
- **Adding a mirror** on a new substrate (e.g., adding an
  OpsRunEvent mirror to `record_decision` where none existed) is
  a **minor bump** — provided `event_id` equality holds between
  canonical + mirror.
- **Removing a mirror** is a **minor bump** — consumers of the
  mirror substrate lose the row; canonical EventBus consumers
  are unaffected.

**Per-transition posture (updated per SIGN batch 2 Q4 fold):**

| Transition | Canonical | Mirror | Rationale |
|---|---|---|---|
| `record_decision` (§7.1) | EventBus `HAI_DECISION_RECORDED` | OpsRunEvent (recommended) | Cross-substrate consumer uniformity + human-initiated governance audit |
| `record_verification` (§7.2) | EventBus `HAI_VERIFICATION_RECORDED` | OpsRunEvent (recommended) | Cross-substrate consumer uniformity + sports outcome audit-forever posture |
| `auto_approve` (§7.3) | EventBus `HAI_AUTO_APPROVED` | OpsRunEvent (REQUIRED for audit) | System-initiated governance; canonical EventBus enables uniform ML retraining subscription; mirror is required for audit-forever |
| `auto_escalate` (§7.4) | EventBus `HAI_AUTO_ESCALATED` | OpsRunEvent (REQUIRED for audit) | System-initiated critical governance; same posture as auto_approve |

**Substrate policy for §7.1-§7.4 tables (retrospective adjustment):**
Per this fold, §7.3 and §7.4 "Recommended substrate: OpsRunEvent"
declaration is refined — canonical is EventBus (uniform consumer
subscription); OpsRunEvent is the REQUIRED audit mirror carrying
the same `event_id`. §7.1 and §7.2 gain OpsRunEvent as recommended
mirror (was audit-table via HFR/HAI row; the mirror is additional
+ carries envelope + payload for cross-substrate consumers).

**Shared wrapper mandate (SIGN cycle 1 batch 2 Q6 STRENGTHEN
inheritance):** Adopters MUST implement emission via a shared
wrapper (`publish_hai_*_event` per §6.2) that enforces canonical
+ mirror discipline. Direct `EventBus.publish` calls that bypass
the wrapper are a defect.

**Scope of the canonical+mirror rule (Rigby S2002 SIGN cycle 1
batch 4 Q10b FOLD):** This canonical+mirror rule applies to
**Class-1 governance / candidate-transition events** (the four
HAI candidates per §7.1-§7.4 and any F.PER-USER-AUTHORITY
governance events per §20.9), NOT to Class-2 learning-plane
emissions in §10.2-§10.6 unless a plane event is explicitly
promoted to Class-1 per the §17.3 Class-2 → Class-1 promotion
rule. Class-2 events default to canonical-EventBus-only with no
OpsRunEvent mirror.

### 7.8 Failure semantics

Per parent §5.2 + S1275 §12 drift-detection posture:

- **Emission failure:** wrapper failure at publish time (Redis
  down, OpsRunEvent write failure) → log + increment counter;
  do NOT block the underlying HAI transition. Emission is
  fire-and-forget from the transition's perspective.
- **Consumer failure:** handler failure at consumer worker →
  DLQ per S2001 §10.1 DLQ semantics (with F14/F15 gap noted
  — handler-failed events do NOT flow to DLQ at HEAD; adoption
  requires resolving this gap or accepting lossy consumer
  semantics).
- **Version mismatch:** consumer sees `schema_version` newer
  than it supports → fail-open per D1 (S1275 §7.5). Consumer
  logs + processes best-effort; does NOT block.
- **Enum mismatch:** consumer sees `source_kind` value not in
  its known enum set → fail-open; log + process best-effort.
  Rationale: enum extensions are minor-bump additions per
  S1275 §7.5.

## 8. Data Ownership and Lifecycle

### 8.1 Ownership matrix per event

| Event | Owning service | Owning model(s) | Contract stewardship |
|---|---|---|---|
| `HAI_DECISION_RECORDED` | HumanInterfaceService | HumanAttentionItem + HumanFeedbackRecord | HAI arc (S1801 Cat A + S1802 Cat B) |
| `HAI_VERIFICATION_RECORDED` | HumanAttentionItem model + BettingOutcomeVerifier | HumanAttentionItem (verification tier) | HAI arc (S1805 Cat E) + Sports arc (S1503) |
| `HAI_AUTO_APPROVED` | HALifecycleService | HumanAttentionItem + HumanFeedbackRecord + HumanPreference | HAI arc (S1801 Cat A lifecycle) |
| `HAI_AUTO_ESCALATED` | HALifecycleService (future method) | HumanAttentionItem | HAI arc (S1801 Cat A lifecycle) + Group 1900 authority resolution consumer |
| Plane-transition events (§10) | Per-plane owner (§10.1-§10.6) | Per-plane models | S1806 Cat F consolidation catalog |
| F.PER-USER-AUTHORITY-MECHANISM events (§20.9) | AuthorityService (future) | PerUserAuthorityPolicy (future) | Group 1900 authority MECHANISM arc |

**Contract stewardship** means the arc responsible for maintaining
the schema version + graduation contract per §12. HAI arc owns
schemas for HAI-mediated events; Group 1900 owns
F.PER-USER-AUTHORITY-MECHANISM schemas.

### 8.2 Lifecycle bindings

- **Emission → source-row persistence order.** Every P2 event
  MUST fire AFTER the source row (HAI/HFR/OpsRunEvent) has
  committed. Rationale: consumers reading source-row fields at
  handler time need the row to exist. Producer wrapper enforces
  via post-transaction hooks (Django `transaction.on_commit`).
- **Emission → downstream state change order.** Emission MUST
  fire BEFORE any downstream state change that depends on the
  event (e.g., `auto_escalate` emits before notification fires).
  Rationale: emission failure should not corrupt downstream
  state assumptions.
- **HAI row deletion.** If HAI row is deleted, historical events
  in EventBus stream / OpsRunEvent remain (event history is
  immutable per audit posture). Consumers dereference
  `hai_item_id` defensively (row may be deleted).

### 8.3 Retention lifecycle summary

- **Class-1 (governance, audit-forever):** `HAI_AUTO_APPROVED`,
  `HAI_AUTO_ESCALATED`, F.PER-USER-AUTHORITY-MECHANISM events →
  OpsRunEvent row, no TTL. Retention posture bounded by R.HAI.
  RETENTION-UNIFIED-ADR + R.OBSERVABILITY.RETENTION-UNIFIED-ADR
  resolution (T0/Gate parked).
- **Class-1 (governance, bounded-history):** `HAI_DECISION_
  RECORDED`, `HAI_VERIFICATION_RECORDED` → EventBus stream
  capped at `MAXLEN=10000` + audit-table via HFR/HAI row (which
  is durable). EventBus copy is bounded; audit source is durable.
- **Class-2 (learning-surface, bounded):** Plane-transition events
  (§10) → EventBus stream capped at `MAXLEN=10000`. No audit-table
  backup by default; adopters may add if per-plane audit posture
  requires.

Full per-event retention in §17.3.

## 9. Integrations With Other Domains

### 9.1 Cross-domain integration matrix

| Domain | Integration | Strength (S1274 §11) | P2 contract obligation |
|---|---|---|---|
| Group 1300 Memory | source_kind enum origin (joint ADR) | STRONG (parked ADR) | Consumes R.HAI.SOURCE-KIND-ENUM-ADR values per D2 |
| Group 1500 Sports | SportsBettingLearningBridge consumer | WEAK (S1805 F4 asymmetric) | Contract closes coupling: bridge consumes `HAI_VERIFICATION_RECORDED` per §17.2 |
| Group 1700 Observability | Retention posture (joint ADR) + LLMCallEvent 30d baseline | STRONG (parked ADR) | Consumes R.OBSERVABILITY.RETENTION-UNIFIED-ADR posture per D3 |
| Group 1800 Human Attention | Primary domain — HAI + HFR + HumanPreference models | STRONG (owner) | Contract designed here; HAI arc is contract steward per §8.1 |
| Group 1900 Authority Enforcement | F.PER-USER-AUTHORITY-MECHANISM consumer | MISSING (mechanism not yet built) | Contract designed here (§20.9); mechanism materializes in Group 1900 arc |
| Group 2000+ P1 (S2001) | EventBus baseline (α/β/γ/δ contract verification) | STRONG (baseline shipped) | Consumes §10.4 γ current-state; inherits F9/F14/F15 constraints |
| Group 2000+ P3 (S2003 planned) | Cross-substrate composition | WEAK (P3 not yet run) | Recommends per-transition substrate per D5; P3 finalizes 6-substrate arbitration |
| Symbol Mapping (S1275) | Schema envelope + versioning precedent | STRONG (adopted per D1) | Consumes §7.1/§7.3/§7.5 |

### 9.2 Handoff obligations to future arcs

- **To Group 1900 (authority MECHANISM arc):** §20.9
  F.PER-USER-AUTHORITY-MECHANISM event contract shape; consumer
  contract obligations documented per §17.2.
- **To Group 2000+ P3 (S2003 Cross-Substrate Composition Design):**
  Per-transition recommended substrate per D5 (EventBus vs
  OpsRunEvent). P3 arbitrates + finalizes the 6-substrate rule
  set. P2 does NOT bind P3's decision; the recommendation is
  input.
- **To Group 2000+ P4 (S2004 Cat F Adjacent / Separation Boundaries
  CONSOLIDATION):** Consumer registry contract obligations (§17.2)
  form part of the separation-boundary posture between Event /
  Integration Architecture and adjacent domains.
- **To Group 2000+ P99 (S2099 canonical summary):** F.PER-USER-
  AUTHORITY-MECHANISM inheritance closure — the arc canonical
  summary tracks whether Group 1900 has consumed the contract by
  the time this arc closes.

## 10. Event Flows — Six-Plane Learning-Surface Event Schema

*(§11.2 template §10 Event Flows — enriched with six-plane learning-surface schema per parent §5.2 deliverable 2.)*

This section designs the six-plane learning-surface event schema.
Per S1806 §10 durable-at-six catalog, six planes exist where
learning-plane transitions happen today WITHOUT durable event
emission. P2 designs the per-plane event contract.

### 10.0 Common envelope for plane-transition events

All six plane-transition events share the §7.0 envelope. The
distinguishing field is `source_kind` (per plane per D2) + a
`plane` field naming the specific plane.

| Envelope field | Type | Required | Rationale |
|---|---|---|---|
| (All §7.0 fields) | (see §7.0) | (see §7.0) | Inherited envelope |
| `plane` | str (enum) | ✓ | Distinguishing plane discriminator — one of `HAI_mediated`, `autonomous_bridge`, `non_bridge_direct`, `verification_outcome`, `external_signal`, `shadow_service` |
| `plane_transition_type` | str (enum) | ✓ | Per-plane transition discriminator (e.g., for autonomous_bridge: `bridge_dispatched`, `bridge_write_committed`) |

**Note on `plane` vs `source_kind` field duality:** These are
semantically related but not identical. `source_kind` describes
event origin (used for cross-plane query); `plane` describes the
learning-surface plane classification (used for plane-transition
consumer routing). Overlap is intentional; consumers may filter
on either.

### 10.1 Plane 1 — HAI-mediated

**Semantic:** Human decision recorded on queued HAI item; feedback-
plane round-trip via HFR.

**Plane-transition event:** subsumed by §7.1 `HAI_DECISION_
RECORDED` + §7.3 `HAI_AUTO_APPROVED` (which carry `source_kind
= HAI_mediated` per §7.5). No separate plane-transition event
needed — the four HAI candidate transitions already cover the
plane.

**Owner:** HAI arc (S1801 Cat A + S1802 Cat B).

**source_kind:** `HAI_mediated`.

**Consumer contract obligation:** See §17.2 (subsumed by
`HAI_DECISION_RECORDED` + `HAI_AUTO_APPROVED` consumer contracts).

### 10.2 Plane 2 — autonomous_bridge

**Semantic:** Domain-signal → UserAgentLearning write via 9 core
LearningBridges (RevenueAttributionLearningLoop,
SportsBettingLearningBridge, AgentExecutionLearningBridge, plus 6
others per S1803 Cat C).

**Plane-transition event:** `BRIDGE_DISPATCHED`

**Emission site:** Per-bridge `dispatch()` method exit (9 bridges).

**Owner:** S1803 Cat C bridge owners.

**source_kind:** `autonomous_bridge`.

**Recommended substrate:** EventBus stream `BRIDGE_DISPATCHED`
(new; post-arc enum extension). Rationale: cross-substrate handoff
to observability + coverage dashboards; bounded retention
acceptable (learning-surface).

**Retention posture class:** Class-2 (learning-surface, bounded).
EventBus `MAXLEN=10000`; no audit-table backup by default.

**Payload:**

| Field | Type | Required | Source / Rationale |
|---|---|---|---|
| `bridge_name` | str | ✓ | Bridge class name (`RevenueAttributionLearningLoop`, etc.) |
| `user_id` | str (UUID) | ✓ | Actor scope |
| `learning_row_id` | str (UUID) | ✓ | UserAgentLearning row created |
| `signal_source` | str | ✓ | Upstream signal source (domain-signal event type) |
| `signal_id` | str \| null | ○ | Upstream signal identity (if traceable) |
| `learning_delta` | JSON | ○ | Structured learning delta (bridge-specific) |
| `dispatch_latency_ms` | int | ○ | Signal-to-dispatch latency |

**Consumer contract obligations:** See §17.2. Primary consumers:
observability dashboards (coverage-query T3.9 candidate per S1806
R11), future audit dashboards, cross-bridge signal-loss detection.

### 10.3 Plane 3 — non_bridge_direct

**Semantic:** Direct ORM writes to AgentLearning / UserAgentLearning
outside the bridge abstraction. 4 non-bridge write sites identified
per S1803 R.HAI.NON-BRIDGE-USERAGENTLEARNING-WRITER-ROUTING-
DECISION (S1899 §8.2 T1.12): `revenue/models.py`,
`core/models/jobs`, `td_handlers_content.py`,
`agent_execution_learning_bridge.py`.

**Plane-transition event:** `NON_BRIDGE_LEARNING_WRITE`

**Emission site:** Each of the 4 non-bridge write sites emits on
row-create commit.

**Owner:** Distributed across 4 sites; consolidation candidate
per S1803 R.HAI.NON-BRIDGE-USERAGENTLEARNING-WRITER-ROUTING-
DECISION T1.12 (post-arc).

**source_kind:** `non_bridge_direct`.

**Recommended substrate:** EventBus stream
`NON_BRIDGE_LEARNING_WRITE` (new; post-arc enum extension).

**Retention posture class:** Class-2 (learning-surface, bounded).

**Payload:**

| Field | Type | Required | Source / Rationale |
|---|---|---|---|
| `writer_site` | str | ✓ | Enum: `revenue_models` / `jobs_models` / `td_handlers_content` / `agent_execution_bridge` |
| `writer_file` | str | ✓ | Source file path |
| `writer_line` | int | ○ | Source line of write |
| `user_id` | str (UUID) | ✓ | Actor scope |
| `learning_row_id` | str (UUID) | ✓ | AgentLearning or UserAgentLearning row |
| `model_name` | str (enum) | ✓ | `AgentLearning` or `UserAgentLearning` |
| `write_rationale` | str \| null | ○ | Why the site bypasses bridge abstraction (populates T1.12 audit) |

**Consumer contract obligations:** See §17.2. Primary consumer:
observability + T1.12 routing-decision audit (documents which
sites remain non-bridge intentionally vs which should migrate).

### 10.4 Plane 4 — verification_outcome

**Semantic:** Sports arbitrage event verified; profit/loss recorded
on HAI verification tier.

**Plane-transition event:** subsumed by §7.2 `HAI_VERIFICATION_
RECORDED` (which carries `source_kind = verification_outcome` per
§7.5).

**Owner:** HAI arc (S1805 Cat E) + Sports arc (S1503) consumer.

**source_kind:** `verification_outcome`.

**Recommended substrate:** EventBus stream `HAI_VERIFICATION_
RECORDED` (per §7.2).

**Retention posture class:** Class-1 (governance, bounded-history).
EventBus `MAXLEN=10000` + audit-table via HAI row (durable).

**Consumer contract obligation:** See §17.2 (subsumed by §7.2
consumer contracts; SportsBettingLearningBridge is primary consumer
closing S1805 F4 asymmetric coupling).

### 10.5 Plane 5 — external_signal

**Semantic:** On-demand intelligence ingestion via Reddit /
Bluesky external bridges. Currently returns dataclass only; no
HAI escalation, no event emission (D6 dead-code status per S1806
Cat F.a).

**Plane-transition event:** `EXTERNAL_SIGNAL_INGESTED`

**Emission site:** RedditLearningBridge + BlueskyLearningBridge
dataclass return sites.

**Owner:** S1806 Cat F.a external bridge owners.

**source_kind:** `external_signal`.

**Recommended substrate:** EventBus stream `EXTERNAL_SIGNAL_
INGESTED` (new; post-arc enum extension) — pending activation of
Reddit / Bluesky bridges out of D6 dead-code status.

**Retention posture class:** Class-2 (learning-surface, bounded).

**Payload:**

| Field | Type | Required | Source / Rationale |
|---|---|---|---|
| `bridge_name` | str (enum) | ✓ | `RedditLearningBridge` or `BlueskyLearningBridge` |
| `external_source_id` | str | ✓ | Upstream identity (Reddit post ID, Bluesky post URI) |
| `external_source_url` | str | ○ | Direct URL |
| `signal_confidence` | float (0-1) | ○ | Bridge-reported confidence |
| `signal_payload` | JSON | ✓ | Structured signal payload (bridge-specific) |
| `escalated_to_hai` | bool | ✓ | Whether signal produced an HAI escalation (currently always False per D6 dead-code status; contract supports future activation) |

**Consumer contract obligations:** See §17.2. Primary consumers:
observability + future HAI escalation ingestion (post-D6-activation).

**Contract-level note:** This plane is in D6 dead-code status
today. Contract designed for post-activation completeness; adopters
may defer emission-site implementation until bridge activation.

### 10.6 Plane 6 — shadow_service

**Semantic:** Unused / legacy learning engines
(AgentLearningEngine unfed, PersistentLearningEngine unused,
AgentLearningSystem fallback-only). 4 shadow services per S1806
Cat F.d.

**Plane-transition event:** `SHADOW_SERVICE_INVOKED`

**Emission site:** Redis pubsub emission sites in
AgentLearningEngine (:202-221) or ORM write sites in
PersistentLearningEngine (:65) if activated.

**Owner:** S1806 Cat F.d shadow-service owners; consolidation
candidate per S1806 R1 (post-arc).

**source_kind:** `shadow_service`.

**Recommended substrate:** EventBus stream `SHADOW_SERVICE_
INVOKED` (new; post-arc enum extension) — pending consolidation
decision per S1806 R1.

**Retention posture class:** Class-2 (learning-surface, bounded).

**Payload:**

| Field | Type | Required | Source / Rationale |
|---|---|---|---|
| `service_name` | str (enum) | ✓ | `AgentLearningEngine` / `PersistentLearningEngine` / `AgentLearningService` / `AgentLearningSystem` |
| `invocation_path` | str | ✓ | `pubsub` \| `orm_write` \| `service_call` |
| `payload_shape` | JSON | ○ | Structured invocation payload |
| `learning_row_id` | str (UUID) \| null | ○ | Downstream row created (if ORM write) |

**Consumer contract obligations:** See §17.2. Primary consumer:
observability + S1806 R1 consolidation audit.

**Contract-level note:** Multiple shadow services in the codebase
today are inactive or fallback-only. Contract emission is designed
for consolidation-time or activation-time; adopters may defer.

### 10.7 Six-plane cross-plane query enabler

Per S1806 §10 catalog motivation: the load-bearing driver for the
six-plane schema is enabling cross-plane query — "what did we
learn about Agent X across all signal types?" — which today
cannot be answered because there is no shared schema, no
`source_kind` provenance tag, no cross-plane query surface.

**P2 contract enables cross-plane query via:**

1. **Shared `source_kind` envelope field** (D2 + §7.0) — enables
   filtering on plane origin across all events.
2. **Shared envelope structure** (§7.0 + §10.0) — enables
   consumer implementations to project across plane boundaries.
3. **Shared `event_id` UUID** — enables cross-plane event
   correlation via joins on downstream tables.
4. **Consumer registry (§17.2)** — enables discovery of which
   consumers project across which planes.

**Cross-plane query pattern (post-adoption):** A consumer
subscribing to all six planes filters by `source_kind` (or `plane`)
to build a per-agent learning-trace across bridges + non-bridge
writers + verification outcomes + external signals + shadow
services. Today this is impossible; post-adoption it is a single
Redis Streams `xreadgroup` per plane.

### 10.8 Per-plane emission activation posture summary

| Plane | Current status | Activation readiness | Blocker |
|---|---|---|---|
| HAI_mediated (§10.1) | Alive; no emission | Ready | HAI_DECISION_RECORDED wrapper post-arc |
| autonomous_bridge (§10.2) | 9 bridges alive; no emission | Ready | Per-bridge dispatch() emission post-arc |
| non_bridge_direct (§10.3) | 4 sites alive; no emission | Ready | Per-site emission post-arc; T1.12 routing decision informs whether all 4 remain or some migrate |
| verification_outcome (§10.4) | Alive; no emission | Ready | HAI_VERIFICATION_RECORDED wrapper post-arc + S1805 F1 automated caller beat enrollment |
| external_signal (§10.5) | D6 dead-code status | Deferred | Bridge activation (post-D6 revival) precedes emission |
| shadow_service (§10.6) | 4 shadow services (mostly inactive) | Deferred | S1806 R1 consolidation decision precedes emission |

## 11. Existing Documentation

- `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md` — parent scoping; §5.2 defines P2 scope.
- `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` — S2001 P1 baseline; §10.1-§10.6 EventBus current state (8 streams + 1 DLQ) + §10.4 γ no-versioning baseline + F9 consumer dormancy + F14/F15 handler-failure DLQ gap.
- `docs/research/symbol_mapping_event_schema_design.md` — S1275 event schema precedent; §7.1 envelope + §7.3 optional fields + §7.5 major/minor graduation contract + §12 drift detection posture. Adopted per D1.
- `docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md` — S1806 §10 durable-at-six event-emission gap catalog; six-plane taxonomy foundational to P2 §10.
- `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md` — §8.1 item 6 R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES parent scope; §8.1 items 3/4/5 retention + source_kind ADR pairings; break-points A/B/C/D per §1 (R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE T0/Gate CRITICAL).
- `docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md` — Group 1900 authority enforcement canonical summary; §19 (S1903 §19 inheritance) F.PER-USER-AUTHORITY-MECHANISM handoff.
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` — §11.2 child audit 20-section template; §14 evidence rules; §15 stage-scoped Rigby routing; §16 draft-first commit policy.
- `docs/research/ARCHITECTURE_INDEX.md` — library navigation.
- `docs/research/OPEN_ARCS.md` — live arc manifest.
- `docs/EVENT_SYSTEM_INVENTORY.md` — event system inventory reference.

## 12. Schema Alternatives Rejected

*(§11.2 template modification: §12 Research Coverage → §12 Schema Alternatives Rejected per parent §5.2 design-contract framing. This section documents the schema-versioning policy pick per parent §5.2 deliverable 3, plus alternatives considered and rejected.)*

### 12.1 Adopted policy: S1275 per-event `schema_version` (D1)

**Decision D1:** Adopt S1275 §7.1 per-event `schema_version` field
convention. Semver string, top-level envelope field, required,
fail-open on unknown version at consumer.

**Rationale summary:**

- **Precedent consistency.** S1275 shipped a graduation contract
  (§7.5 major/minor bump policy) already in production for
  symbol-mapping events. A second policy would fragment schema
  discipline across event families.
- **Greenfield + evolution both handled.** For P2 (greenfield —
  no existing HAI events), all events start at `1.0.0`; for
  future evolution, the S1275 graduation contract handles minor
  additions (optional field adds, enum extensions) and major
  breaks (field removal, required field adds, enum narrowing).
- **Consumer-side fail-open.** S1275 §7.5 defines fail-open on
  unknown version — consumer logs + processes best-effort. This
  is essential for a bounded-retention EventBus where old events
  may outlive the consumer's known-version set.
- **Envelope + payload separation.** S1275 places `schema_version`
  in envelope; P2 payload fields (§7.1-§7.4) evolve independently
  of envelope. Envelope changes are rarer + require broader
  coordination; payload changes are frequent + local.

**Substrate-split rule (Rigby S2002 SIGN cycle 1 batch 1 Q1 FOLD):**
`schema_version` location depends on substrate.

- **EventBus / Redis Streams substrate:** `schema_version` is a
  top-level envelope field on the Redis Streams event (per §7.0).
  Required, semver string.
- **OpsRunEvent (DB / audit-table) substrate:** `schema_version`
  MUST be present, but may be stored either (a) as a first-class
  column if/when the OpsRunEvent schema is extended to support
  envelope columns, or (b) inside the `payload` JSON at key
  `payload.schema_version` (until such extension lands). In both
  cases, `event_type` + `domain` remain the stable identifiers.
- **Terminology.** "Top-level" means "outside the domain payload
  when the substrate supports it"; otherwise `payload.schema_version`
  is the canonical location. Consumers dereference by substrate.
- **Cross-substrate consumer discipline.** A consumer that projects
  across both substrates MUST read `schema_version` from the
  substrate-appropriate location. Contract accommodates both.

### 12.2 Alternative rejected: External schema registry table

**Alternative:** Store schema versions in a Django model
(`EventSchemaRegistry`); events emit only `schema_id` (FK) and
consumers dereference to get schema shape.

**Rejection rationale:**

- **Consumer join cost.** Every event handler would incur an ORM
  join to resolve schema — turns EventBus (Redis Streams,
  in-memory) into a Postgres-hop path.
- **Consumer offline capability.** A consumer subscribing to
  events at replay time (e.g., regression harness per S2001
  §10.5 δ) would need registry access; the schema-registry
  service becomes a dependency for consumers that today only
  need Redis.
- **Complicates versioning graduation.** S1275 §7.5 major/minor
  bump policy is local to the wrapper + event; a registry table
  introduces a shared coordination surface across all event
  families that P2 does not need.
- **Precedent misalignment.** S1275 explicitly does NOT recommend
  this. Adopting registry-table style would create parallel
  policies (per-event field for symbol_mapping events, registry
  table for HAI events).

### 12.3 Alternative rejected: Implicit-from-topic-name versioning

**Alternative:** Encode version in the EventStream enum name
(`HAI_DECISION_RECORDED_V1`, `HAI_DECISION_RECORDED_V2`, etc.);
no envelope `schema_version` field.

**Rejection rationale:**

- **Stream proliferation.** Each version bump creates a new
  Redis Stream; historical streams stay populated (bounded by
  `MAXLEN`). Registry of active vs deprecated streams becomes a
  side management burden.
- **Consumer subscribe cost.** A consumer supporting versions
  V1 + V2 must subscribe to two streams + implement two handlers;
  a single handler with version dispatch is simpler.
- **Envelope-agnostic consumers.** A consumer inspecting an
  event without subscribing to a specific stream (e.g., audit
  dashboards reading OpsRunEvent rows) cannot determine version
  without inspecting `event_type` string — brittle.
- **Cross-substrate impossibility.** OpsRunEvent rows are not
  Redis Streams; there is no "topic name" to encode a version
  into. This alternative would work for EventBus but break for
  OpsRunEvent — half of P2's substrates lose versioning.
- **Precedent misalignment.** S1275 does not use this pattern.

### 12.4 Alternative rejected: No versioning (γ current-state extension)

**Alternative:** Do not add `schema_version` field at all;
consumers infer shape from `event_type` and current codebase
knowledge.

**Rejection rationale:**

- **γ current-state failure mode replication.** S2001 §10.4 γ
  documented this posture as the current EventBus reality — no
  versioning, ad-hoc field additions silently work but removals
  are invisible. This posture is the WHAT-P2-FIXES, not the
  what-P2-adopts.
- **Consumer breakage on payload evolution.** Any field removal,
  type change, or enum narrowing silently breaks consumers. HAI
  audit posture cannot accept silent breakage.
- **Replay fragility.** S2001 §10.5 δ documented `EventBus.replay()`
  exists but zero callers today. A replay tool over events with
  no version discipline is unreliable — old events replayed to
  new consumer versions produces undefined behavior.
- **Contradicts D1 stewardship.** §8.1 contract stewardship
  assigns each event a version owner; no versioning = no
  stewardship = no arc-level graduation policy.

### 12.5 Retention alternative rejected: Uniform 30-day TTL

**Alternative:** Adopt the LLMCallEvent 30-day TTL baseline for
ALL HAI events (both Class-1 governance and Class-2 learning-
surface) per R.OBSERVABILITY.RETENTION-UNIFIED-ADR uniform
posture.

**Rejection rationale:**

- **Audit posture mismatch.** `auto_approve` + `auto_escalate` +
  F.PER-USER-AUTHORITY-MECHANISM events are audit-critical (HFR
  row exists but the emission event captures additional context —
  auto-approval rationale, escalation ladder position, authority
  policy binding). 30-day retention loses this context.
- **Load-bearing consumer misalignment.** Sports betting
  regulatory audit (SportsBettingLearningBridge downstream) may
  need multi-year verification-outcome history. Uniform 30-day
  breaks compliance.
- **Class-2 events don't need 30 days.** Plane-transition events
  (§10.2 bridge_dispatched, §10.3 non_bridge_learning_write) are
  bounded-history operational-observability signal. 30 days is
  vast overkill; 10000-event `MAXLEN` is closer to the right
  posture.
- **Precedent for hybrid.** OpsRunEvent already stores audit-
  forever; LLMCallEvent bounded 30-day. Precedent supports
  per-event-class retention (D3 two-class posture matches).

**Deferred to joint ADR:** R.OBSERVABILITY.RETENTION-UNIFIED-ADR
+ R.HAI.RETENTION-UNIFIED-ADR (both T0/Gate parked). If the
joint ADRs resolve to a uniform 30-day baseline over P2's
protest, P2 recommends carving out HAI Class-1 events as an
explicit exception preserving audit-forever posture.

### 12.6 Retention alternative rejected: Uniform audit-forever

**Alternative:** Store ALL P2 events (Class-1 + Class-2) in
audit-table backing with no TTL.

**Rejection rationale:**

- **Storage cost unbounded.** Class-2 plane-transition events
  fire on every bridge dispatch (9 bridges) + every non-bridge
  write + every plane transition. At platform scale this is
  millions of rows per year.
- **Query performance degradation.** OpsRunEvent audit-table
  storing millions of learning-surface rows makes governance
  queries slower (need to filter out learning noise).
- **Purpose misalignment.** Class-2 events are operational
  observability — bounded-history retention matches the
  consumer use case (dashboards, coverage-query tools). No
  consumer needs multi-year plane-transition history.

## 13. Architecture Maturity

- **Current state at HEAD:** MISSING / EXPERIMENTAL. Zero HAI
  events emit today; four HAI transition surfaces exist but
  none have emission sites.
- **Post-contract-adoption target:** WORKING. Contract defines
  the emission sites, envelope, payload, retention, consumer
  registry. Contract-adopting arcs (post-P2) implement the
  emission sites + wire the consumers + enroll the beat tasks
  (F9 constraint from S2001).
- **Post-consumer-adoption target:** STABLE. Post the joint
  retention ADR resolutions + R.HAI.LOOP-COUPLING-REPAIR-ADR-
  BUNDLE break-point D resolution + Group 1900 authority
  MECHANISM arc completion — the contract has full consumer
  coverage.
- **Path to CANONICAL:** Multi-arc; not P2's scope. Requires
  S2099 xx99 canonical summary + downstream implementation
  arc verification.

**Maturity per event:**

| Event | Current | Post-contract-adoption | Blocker to STABLE |
|---|---|---|---|
| `HAI_DECISION_RECORDED` | MISSING | WORKING | FeedbackProcessor consumer refactor per S1802 F7 |
| `HAI_VERIFICATION_RECORDED` | MISSING | WORKING | SportsBettingLearningBridge S1805 F4 asymmetric close + S1805 F1 beat enrollment |
| `HAI_AUTO_APPROVED` | MISSING | WORKING | None (single-caller topology; OpsRunEvent substrate ready) |
| `HAI_AUTO_ESCALATED` | MISSING | EXPERIMENTAL | R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE break-point D resolution |
| Plane-transition events (§10) | MISSING | PARTIAL (Class-2 planes activate incrementally) | Per-plane emission-site implementation (bridge dispatch instrumentation, etc.) |
| F.PER-USER-AUTHORITY-MECHANISM events | MISSING | EXPERIMENTAL | Group 1900 authority MECHANISM arc completion |

## 14. Known Drift

### 14.1 Envelope-level drift risks

- **Producer-side envelope drift.** Multiple emission sites
  populating envelope inconsistently. Mitigation: centralize
  envelope construction in `publish_hai_*_event` wrapper
  functions (post-arc). §7.7 rule 1 declares invariant.
- **`source_kind` enum drift.** Adopters may add ad-hoc enum
  values not in R.HAI.SOURCE-KIND-ENUM-ADR. Mitigation: pin
  enum values to the joint ADR resolution; enum extensions
  are minor-bump per S1275 §7.5.
- **`event_type` string drift.** Adopters may use inconsistent
  event_type strings across substrates. Mitigation: contract
  declares canonical names (§7.1-§7.4); post-arc implementation
  uses Python enum for compile-time enforcement.

### 14.2 Payload-level drift risks

- **NULL rate drift** (S1275 §12 pattern). Optional payload
  fields may become effectively-mandatory (never NULL) or
  effectively-unused (always NULL). Consumer must handle both.
- **Wrong non-NULL drift** (S1275 §12 pattern). Optional field
  populated with sentinel values (e.g., empty string as "no
  feedback") vs true absence. Consumer contract must specify.
- **Stale producer drift.** Producer implementation ships with
  `schema_version=1.0.0` but does not update field mapping when
  HAI model changes. Detected via S1275 §12 drift-detection
  posture (NULL rate + wrong non-NULL + cross-source conflict).

### 14.3 Cross-substrate drift risks

- **EventBus vs OpsRunEvent duality drift.** D5 hybrid emission
  places 2 events on EventBus + 2 events on OpsRunEvent. Adopters
  may over-emit (both substrates for one event) or under-emit
  (neither). Mitigation: contract per §7.1-§7.4 specifies
  exactly one recommended substrate per event; P3 arbitrates
  post-arc.
- **Plane-transition + candidate-transition duplication.** §10.1
  and §10.4 subsume `HAI_DECISION_RECORDED` and `HAI_VERIFICATION_
  RECORDED` respectively — one event fires but carries `plane`
  envelope field. Adopters may accidentally emit TWO events (one
  candidate + one plane). Mitigation: §10.1 + §10.4 explicit
  "subsumed by" language + wrapper design.

**Double-emission detection + prevention (Rigby S2002 SIGN cycle 1
batch 2 Q6 STRENGTHEN):**

1. **Single-emission rule.** For a given `(event_id,
   transition_type)` pair there MUST be exactly one transition
   event emitted. Plane semantics MUST be encoded inside the
   transition event payload (envelope `plane` field per §10.0,
   plus `plane_transition_type` where applicable) — NOT via a
   distinct second emission.
2. **Double-emission detector.** A lightweight consumer or
   periodic audit job (post-arc; contract obligation) scans
   recent EventBus entries + OpsRunEvent mirrors and flags cases
   where both a transition event and a plane event share the
   same underlying source-row identity (`hai_item_id` +
   `updated_at` window) within a short window (recommended:
   30 seconds). Detected duplicates fire an invariant warning +
   are logged to a `DoubleEmissionDefect` audit surface.
3. **Producer guardrail (shared wrapper mandate).** Adopters
   MUST route all emissions through the shared wrapper functions
   (`publish_hai_*_event` per §6.2). Direct `EventBus.publish`
   calls bypassing the wrapper are a defect. Even though wrapper
   implementation materializes post-arc, the contract mandates
   "use the wrapper" as the adoption rule. Wrapper enforces:
   (a) canonical + mirror discipline per §7.9, (b) envelope
   shape per §7.0, (c) single-emission rule (a plane event MUST
   NOT be emitted separately from its subsuming candidate
   transition event).

### 14.4 Handler-failure DLQ gap drift (inherited from S2001 F14/F15)

- **Handler failure does not flow to DLQ.** Per S2001 F14/F15,
  handler failures increment `events_failed` counter but do NOT
  ACK and do NOT move to DLQ. Consequence for P2: if adopters
  wire an HAI consumer + the consumer fails, the event is
  neither ACKed nor moved to DLQ — future consumer restart may
  re-process the event (at-least-once but no dedup surface).
- **Contract obligation:** §17.2 consumer registry entries
  MUST include idempotency-key handling per §7.0 envelope
  `event_id`. Consumers dedupe on `event_id`.

## 15. Known Technical Debt

- **T1 auto_escalate method + owner service missing.** Per §7.4
  pre-condition + S1899 §1 break-point D. Contract designed;
  emission materializes post-repair. Debt owner: HAI arc
  (R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE T0/Gate CRITICAL).
- **T2 EventStream enum extension for 4 HAI events + 5 plane-
  transition events.** Post-arc implementation. Debt owner:
  Group 2000+ Event / Integration Architecture arc.
- **T3 Publisher wrappers for 4 HAI events + 5 plane-transition
  events.** Post-arc implementation. Debt owner: Group 2000+
  Event / Integration Architecture arc.
- **T4 Consumer worker + beat enrollment for HAI event
  consumers.** Post-arc implementation. Debt owner: HAI arc
  (per event: FeedbackProcessor refactor, SportsBetting bridge
  coupling closure, observability dashboards) + Group 2000+ P3
  (beat schedule).
- **T5 Retention ADR resolution.** Joint T0/Gate parked;
  R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.HAI.RETENTION-
  UNIFIED-ADR. Debt owner: Group 1700 + Group 1800 canonical-
  summary handoff.
- **T6 source_kind enum ADR resolution.** Joint T0/Gate parked;
  R.HAI.SOURCE-KIND-ENUM-ADR. Debt owner: Group 1300 + Group
  1800 canonical-summary handoff.
- **T7 Loop-coupling repair ADR bundle.** T0/Gate CRITICAL;
  R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE. Break-points A/B/C/D
  per S1899 §1. Debt owner: HAI arc.
- **T8 Handler-failure DLQ gap.** S2001 F14/F15. Contract-adoption
  depends on resolution or accept lossy consumer semantics per
  §14.4. Debt owner: Group 2000+ P4 (Cat F consolidation).
- **T9 Group 1900 authority MECHANISM arc scope.** F.PER-USER-
  AUTHORITY-MECHANISM contract designed here (§20.9); mechanism
  designed post-arc. Debt owner: Group 1900 authority MECHANISM
  arc.
- **T10 Beat enrollment for automated verification path.** S1805
  F1 UNSCHEDULED. Blocks `HAI_VERIFICATION_RECORDED` automated
  emission per §7.2. Debt owner: HAI arc (S1805 owner).

## 16. Boundary Violations

### 16.1 auto_approve bypass of record_decision (S1802 Q2 orphan)

`HALifecycleService.auto_approve_item:325` creates HFR directly
without calling `HumanAttentionItem.record_decision`. Consequence:
the S1802 FeedbackProcessor post_save signal does fire (via HFR
post_save), but the boundary between HAI-mediated (human decision)
and system-initiated (auto-approve) is invisible in code.

**P2 contract resolution:** Two events (`HAI_DECISION_RECORDED` +
`HAI_AUTO_APPROVED`) with distinct `event_type` + `source_kind`
values (both `HAI_mediated` per §7.5, but disambiguated via
`event_type`). Consumers filter accordingly. §7.3 emission at
service method preserves the current bypass semantics; the event
contract makes the bypass observable + audit-tractable rather
than fixing the code path.

**Post-arc option:** Refactor `auto_approve_item` to call
`record_decision` internally. Not required for contract adoption;
current bypass is compatible if `event_type` disambiguation holds.

### 16.2 OrchestratorApprovalRequest.auto_approve vs HAI auto_approve name collision

Per verifier_loop item (e): two methods named `auto_approve`
exist in two apps (governance + HAI). P2 contract event names
disambiguate via `event_type = "hai_auto_approved"` (namespaced
prefix). No cross-boundary event collision.

**Contract obligation:** Governance orchestrator approval events
(if introduced) MUST namespace with distinct `event_type` +
different `domain` on OpsRunEvent (e.g., `domain =
"orchestration"` vs `domain = "human_attention"`).

### 16.3 REST + automated caller topology for record_verification

Per §3.2 + §7.2: two callers (REST + BettingOutcomeVerifier)
emit via model-method emission (`record_verification:227`).
Boundary risk: emission fires on both paths, but only the
BettingOutcomeVerifier caller has S1805 F1 UNSCHEDULED — REST
path is on-demand.

**P2 contract resolution:** `verification_source` payload field
(§7.2) distinguishes `REST` vs `automated_verifier`; consumers
filter on need.

### 16.4 Group 1900 authority MECHANISM boundary

Per parent §5.2 scope guardrail: P2 designs event-emission
contract for authority triggers (§20.9); MECHANISM (resolution
logic) is Group 1900. Boundary MUST hold across arcs — P2
adopters MUST NOT infer resolution logic from event contract.

**Contract obligation:** §20.9 explicitly documents contract-vs-
mechanism separation.

## 17. Consumer Registry + Retention Posture

*(§11.2 template modification: §17 Duplicate or Overlapping Systems → §17 Consumer Registry + Retention Posture per parent §5.2 design-contract framing. This section documents the consumer registry per parent §5.2 deliverable 4 + retention posture per deliverable 5.)*

### 17.1 Consumer contract obligations (universal)

Every HAI event consumer MUST satisfy the following contract
obligations, inherited from S1275 §12 posture + S2001 F9
constraint + P2 D4 decision:

1. **Beat enrollment (D4).** For any consumer implemented as a
   Celery consumer task subscribing to an EventBus stream via
   `EventConsumerWorker`, a corresponding `PeriodicTask` row
   MUST exist AND be enabled. S2001 F9 documented 4 of 5 EventBus
   consumer beat tasks unscheduled today — contract adoption
   requires resolving this per event.
2. **Idempotency (§7.7 rule 4).** Consumers dedupe on
   `event_id`. Duplicate emission is possible (at-least-once
   semantics + potential handler-restart replay).
3. **Fail-open on version (D1).** Consumers seeing
   `schema_version` newer than known → log + process best-effort.
   Consumers seeing older version → attempt process; if envelope
   or payload shape mismatch, log + skip (do not block).
4. **Fail-open on enum extension (D2).** Consumers seeing
   `source_kind` or other enum value outside known set → log +
   process best-effort.
5. **Consumer-registry declaration.** Every consumer implementation
   arc MUST update §17.2 with the consumer_name + consumer_group
   + subscribed events + beat enrollment status. Registry drift
   is a defect.
6. **Handler-failure discipline (Rigby S2002 SIGN cycle 1
   batch 1 Q3 STRENGTHEN).** Handler failures produce
   `events_failed` counter increment. Adopters accept at-least-
   once + potential replay; MUST NOT rely on DLQ flow for
   handler failures until S2001 F14/F15 gap resolves. Class-1
   governance events add two additional contract constraints:
   - **Idempotency scope.** Governance-event idempotency MUST
     be keyed on `(event_type, event_id)` and consumers MUST be
     side-effect safe (no duplicate writes, no double state
     transitions). Weak idempotency (dedup on partial payload)
     is a defect.
   - **Audit trail safety.** Governance consumers MUST write
     an append-only receipt / "seen event" marker so duplicate
     emissions are observable (not silently ignored) and failures
     can be replayed without ambiguity. Marker rows include
     `event_id` + `consumer_name` + `processed_at`.
7. **Consumer replay + monitoring obligation (Rigby S2002 SIGN
   cycle 1 batch 1 Q3 STRENGTHEN).** DLQ is NOT the correctness
   mechanism; correctness comes from idempotency + replayability
   + durable audit receipt. Adopters MUST document consumer
   retry / replay procedures AND detect "stuck pending" events
   (monitoring / stats surface) — otherwise Class-1 emission is
   not safe.

### 17.2 Per-event consumer registry

*(Rigby S2002 SIGN cycle 1 batch 2 Q5 FOLD landed: added
`security_audit_consumer` REQUIRED rows across 3 governance
events; promoted `ml_training_signal_consumer` (was
`ml_retraining_hai_consumer`) on `HAI_VERIFICATION_RECORDED` to
REQUIRED; downgraded `user_notification_service` on
`HAI_AUTO_APPROVED` to OPTIONAL + added DEFERRED
`notification_adapter` row; demoted HumanPreference-update
consumer proposal to DEFERRED per implementation-status
discipline; added `Exists today` column to prevent
REQUIRED-from-nowhere labeling drift.)*

| Event | Consumer group | Consumer name | Subscribed stream | Handler | Beat enrollment | Exists today | Status |
|---|---|---|---|---|---|---|---|
| `HAI_DECISION_RECORDED` | `hai_feedback_workers` | `feedback_processor_hai_consumer` | `HAI_DECISION_RECORDED` | `handle_hai_decision_recorded_event` (post-arc) | `process_hai_feedback_queue` beat every 1 min | N (S1802 post_save signal handler exists; consumer refactor post-arc) | REQUIRED — replaces post_save signal per S1802 F7 |
| `HAI_DECISION_RECORDED` | `hai_observability_workers` | `hai_dashboard_consumer` | `HAI_DECISION_RECORDED` | Read-only projection to dashboards | Not required (read-only) | N | OPTIONAL |
| `HAI_DECISION_RECORDED` | `hai_ml_workers` | `ml_training_signal_consumer` | `HAI_DECISION_RECORDED` | Filter `fed_to_ml=True` + feed ML training signal (retraining executed downstream) | Existing ML retraining beat (already enrolled) | Y (existing ML retraining beat consumes HFR post_save today; consumer refactor to subscribe HAI_DECISION_RECORDED post-arc) | REQUIRED for retraining loop closure |
| `HAI_DECISION_RECORDED` | `hai_security_workers` | `security_audit_consumer` | `HAI_DECISION_RECORDED` | Durable security-trace projection (independent of product dashboards); filters authority-gated decisions via `authority_scope` envelope field | New beat every 1 min | N | REQUIRED — Class-1 governance security trace per SIGN batch 2 Q5 FOLD |
| `HAI_DECISION_RECORDED` | `hai_preference_workers` | `human_preference_update_consumer` | `HAI_DECISION_RECORDED` | Close S1804 `update_preferences_from_decision` loop | New beat every 5 min | N | DEFERRED — post-S1804 owner ratification |
| `HAI_VERIFICATION_RECORDED` | `hai_sports_workers` | `sports_betting_bridge_consumer` | `HAI_VERIFICATION_RECORDED` | `handle_hai_verification_recorded_event` (post-arc); closes S1805 F4 asymmetric | New beat `process_hai_verification_queue` every 5 min | N (bridge coupling exists only in `BettingOutcomeVerifier._create_learning_records:127-135` today — bidirectional close is post-arc) | REQUIRED — closes S1805 F4 |
| `HAI_VERIFICATION_RECORDED` | `hai_observability_workers` | `hai_dashboard_consumer` | `HAI_VERIFICATION_RECORDED` | Read-only projection | Not required (read-only) | N | OPTIONAL |
| `HAI_VERIFICATION_RECORDED` | `hai_ml_workers` | `ml_training_signal_consumer` (extended) | `HAI_VERIFICATION_RECORDED` | Outcome-based ML training signal — arguably the highest-value learning input per SIGN batch 2 Q5 FOLD | Existing ML retraining beat (already enrolled; extend to subscribe verification stream) | N | REQUIRED — outcome-based learning is load-bearing to the six-plane learning surface per SIGN batch 2 Q5 FOLD |
| `HAI_AUTO_APPROVED` (OpsRunEvent mirror + EventBus canonical per §7.9) | N/A (OpsRunEvent consumers query directly) | `governance_audit_view` | `OpsRunEvent.filter(event_type='hai_auto_approved')` | Read-only projection to governance dashboards | Not required | N | REQUIRED for audit visibility |
| `HAI_AUTO_APPROVED` | `hai_security_workers` | `security_audit_consumer` | `HAI_AUTO_APPROVED` (canonical EventBus per §7.9) | Durable security-trace projection for system-initiated governance | New beat every 1 min | N | REQUIRED — Class-1 governance security trace per SIGN batch 2 Q5 FOLD |
| `HAI_AUTO_APPROVED` | `hai_ml_workers` | `ml_training_signal_consumer` (extended) | `HAI_AUTO_APPROVED` (canonical EventBus per §7.9) | Auto-approve-aware ML signal (with `fed_to_ml=False` filter — signal-only, not retraining input) | Existing ML retraining beat | N | OPTIONAL (post-arc extension) |
| `HAI_AUTO_APPROVED` | `hai_notification_workers` | `user_notification_service` | `HAI_AUTO_APPROVED` (canonical EventBus per §7.9) | User notification that their item was auto-approved | New beat (post-adapter) | N | OPTIONAL — awaits defined user surface + SLA per SIGN batch 2 Q5 FOLD |
| `HAI_AUTO_APPROVED` | `hai_notification_workers` | `notification_adapter` (surface-agnostic) | `HAI_AUTO_APPROVED` | Notification adapter delivering to per-user-preference channel (email / in-app / etc.) | Post-adapter design | N | DEFERRED — parked so it's not forgotten per SIGN batch 2 Q5 FOLD |
| `HAI_AUTO_ESCALATED` (OpsRunEvent mirror + EventBus canonical per §7.9) | N/A | `escalation_notification_service` | `OpsRunEvent.filter(event_type='hai_auto_escalated')` | On-call notification dispatch (Slack, PagerDuty) | New beat every 1 min | N | DEFERRED (promotes to REQUIRED at v1.0.0) — graduation trigger: break-point D resolved + §7.4 v0.x → v1.0.0 schema locked. Per SIGN batch 4 Q10a FOLD |
| `HAI_AUTO_ESCALATED` | `hai_security_workers` | `security_audit_consumer` (v0.x — minimal-fields-only) | `HAI_AUTO_ESCALATED` (canonical EventBus per §7.9) | Durable security-trace projection restricted to reserved-minimal fields (`event_id`, `occurred_at`, `source_object_id`, `escalation_reason_code`, `schema_version`); MUST NOT depend on non-minimal fields until v1.0.0 | New beat every 1 min | N | REQUIRED (v0.x — minimal-fields-only per SIGN batch 4 Q10a FOLD) — Class-1 governance security trace |
| `HAI_AUTO_ESCALATED` | N/A | `authority_resolution_consumer` | (Group 1900 designed) | Group 1900 authority MECHANISM consumer | Group 1900 arc-designed beat | N (Group 1900 mechanism does not exist) | DEFERRED (promotes to REQUIRED post-Group 1900 + §7.4 v0.x → v1.0.0). Per SIGN batch 4 Q10a FOLD |
| `BRIDGE_DISPATCHED` (§10.2) | `learning_coverage_workers` | `bridge_coverage_dashboard` | `BRIDGE_DISPATCHED` | Coverage projection per S1806 R11 | New beat every 1 min | N | OPTIONAL |
| `NON_BRIDGE_LEARNING_WRITE` (§10.3) | `learning_coverage_workers` | `t112_routing_audit_consumer` | `NON_BRIDGE_LEARNING_WRITE` | T1.12 routing-decision audit | New beat every 1 hour | N | OPTIONAL |
| `EXTERNAL_SIGNAL_INGESTED` (§10.5) | `learning_coverage_workers` | (post-D6-activation) | `EXTERNAL_SIGNAL_INGESTED` | (post-D6-activation) | Deferred | N | DEFERRED |
| `SHADOW_SERVICE_INVOKED` (§10.6) | `learning_coverage_workers` | (post-consolidation) | `SHADOW_SERVICE_INVOKED` | (post-consolidation) | Deferred | N | DEFERRED |
| F.PER-USER-AUTHORITY events (§20.9) | N/A | `authority_resolution_consumer` | (Group 1900 designed) | (Group 1900 designed) | (Group 1900 designed) | N (Group 1900 mechanism does not exist) | REQUIRED post-Group 1900 |

**Registry stewardship:** §17.2 rows are contract-declared, not
implementation-verified. Implementation arcs update `Exists today`
+ `Beat enrollment` columns to verified state as consumers land.

**REQUIRED-from-nowhere discipline (SIGN batch 2 Q5 FOLD):** A
consumer labeled REQUIRED without a corresponding `Exists today: Y`
row is a contract obligation on the implementation arc, not a
declaration that the consumer already exists. Adopters MUST NOT
skip REQUIRED rows; they MUST implement them (or downgrade with
explicit rationale documented in the row).

### 17.3 Retention posture per event class

Per D3 two-class posture + parent §5.2 deliverable 5 (retention
posture pair with joint ADRs):

**Class-1: Governance events (audit-forever posture)**

| Event | Substrate | TTL | Audit-table backing | Notes |
|---|---|---|---|---|
| `HAI_DECISION_RECORDED` | EventBus stream + HFR row | EventBus: `MAXLEN=10000` bounded. HFR row: durable (no TTL). | HFR row | EventBus is bounded copy; HFR is durable audit source |
| `HAI_VERIFICATION_RECORDED` | EventBus stream + HAI verification-tier fields | EventBus: `MAXLEN=10000`. HAI row: durable. | HAI row | Same posture |
| `HAI_AUTO_APPROVED` | OpsRunEvent | No TTL (audit-forever) | OpsRunEvent itself | System-initiated governance; audit-forever |
| `HAI_AUTO_ESCALATED` | OpsRunEvent | No TTL (audit-forever) | OpsRunEvent itself | System-initiated critical governance |
| F.PER-USER-AUTHORITY events (§20.9) | OpsRunEvent (recommended; Group 1900 finalizes) | No TTL (audit-forever) | OpsRunEvent itself | Authority resolution audit |

**Class-2: Learning-surface events (bounded posture)**

| Event | Substrate | TTL | Audit-table backing | Notes |
|---|---|---|---|---|
| `BRIDGE_DISPATCHED` (§10.2) | EventBus stream | `MAXLEN=10000` bounded | None by default | Operational observability |
| `NON_BRIDGE_LEARNING_WRITE` (§10.3) | EventBus stream | `MAXLEN=10000` | None | Operational + T1.12 audit signal |
| `EXTERNAL_SIGNAL_INGESTED` (§10.5) | EventBus stream (post-activation) | `MAXLEN=10000` | Optional per adopter | Deferred |
| `SHADOW_SERVICE_INVOKED` (§10.6) | EventBus stream (post-consolidation) | `MAXLEN=10000` | Optional | Deferred |

**Redis Streams MAXLEN posture:** `STREAM_MAX_LEN=10000` per
`event_bus.py:104` is the current EventBus posture (S2001 §10.4
γ baseline). P2 adopts this posture for Class-2 events + Class-1
EventBus copies. Post-arc, joint retention ADR resolution may
alter this posture; contract carries a mitigation posture
(§12.5 rejection commentary).

**Adopter override posture:** An adopter arc that determines
audit-forever backing is required for a Class-2 event (e.g.,
verification_outcome plane already Class-1 governance) MUST
declare the override in §17.2 registry row + update this table.
Contract accommodates adopter judgment where the joint retention
ADR is silent.

**Audit-critical test — Class-1 vs Class-2 classification rule
(Rigby S2002 SIGN cycle 1 batch 1 Q2 STRENGTHEN):**

An event's retention class is determined by the audit-critical
test:

- **Class-1 (audit-critical):** the event can change authority,
  approval state, enforcement status, or constitutes an
  operator-visible decision or verification.
- **Class-2 (learning-surface, non-authoritative):** the event
  is purely telemetry / learning-surface and can be recomputed
  or is non-authoritative.

Every event in §17.3 tables passes the test into its assigned
class. Adopters classifying new events apply the same test.

**Class-2 → Class-1 promotion rule.** Any Class-2 event that is
later used as an input to a governance decision (e.g., a bridge
dispatch signal that becomes an input to `auto_approve` low-risk
criteria evaluation) MUST have either (a) an audit-table mirror
(OpsRunEvent audit row for the specific derived signal, not
raw telemetry), or (b) a deterministic reconstruction path
recorded (documented transform from raw telemetry to the
derived signal + retention of raw telemetry sufficient to
reconstruct).

**Rejection rationale one-liners for the joint ADR handoff:**

- Uniform 30-day TTL rejection: breaks governance / audit trace
  continuity for HAI Class-1 events (auto_approve rationale,
  auto_escalate ladder history, authority decision provenance).
- Uniform audit-forever rejection: cost + noise + over-collection
  for high-volume learning-surface events (bridge dispatch
  counts scale with signal throughput; unbounded storage
  economically infeasible).

### 17.4 Retention posture handoff to joint ADRs

Per §12.5 + §12.6 rejection commentary:

- **To R.OBSERVABILITY.RETENTION-UNIFIED-ADR:** P2 recommends
  a per-event-class posture over uniform TTL. If ADR resolution
  adopts uniform 30-day baseline, P2 recommends carving out
  HAI Class-1 as audit-forever exception.
- **To R.HAI.RETENTION-UNIFIED-ADR:** Six divergent retention
  regimes at HEAD per S1899 §299. P2 posture: Class-1
  (audit-forever via OpsRunEvent + audit-model rows for
  bounded-history), Class-2 (bounded-history via Redis
  MAXLEN=10000). ADR resolution should align or intentionally-
  diverge per event class.

### 17.5 Runtime activation obligation (Rigby S2002 SIGN cycle 1 batch 3 Q9 STRENGTHEN reframe)

*(Per SIGN batch 3 Q9 STRENGTHEN — reframed from "beat-enrollment
obligation" to "runtime activation obligation" to accommodate
consumers whose activation mode is not periodic polling.)*

Per D4 + S2001 F9 constraint: consumer registry rows for REQUIRED
consumers MUST specify a runtime activation mode. Contract-adopting
arc obligations:

**Activation mode declaration.** For each REQUIRED consumer,
the contract MUST specify **exactly one** activation mode:

1. **`PeriodicTask` cadence** — Celery beat schedule row with a
   cron / interval schedule. Applicable to polling consumers +
   scan-oriented consumers.
2. **Long-running worker subscription** — dedicated worker
   process consuming an EventBus stream via
   `EventConsumerWorker` (per S2001 §10.6 handler-registration
   pattern). Applicable to real-time low-latency consumers.
3. **On-demand trigger pathway** — activation on external
   trigger (webhook, REST endpoint, cross-arc signal). Explicitly
   named + documented; not automatically-scheduled. Applicable
   to human-in-the-loop or infrequent audit consumers.

**PeriodicTask enrollment discipline (S2001 F9 constraint
compliance).** When the activation mode is `PeriodicTask` cadence:

1. Create Django management command that ensures
   `PeriodicTask` rows exist for each such REQUIRED consumer.
2. Add rows to `core/celery.py:beat_schedule` where code-defined
   schedule is authoritative (S2001 §10.1(h) precedent).
3. Verify per S2001 F9 discipline: `PeriodicTask.objects.filter(
   task__endswith='<task>').values_list(...)` returns non-empty
   + `enabled=True`.
4. Document in §17.2 registry `Beat enrollment` column.

**Anti-pattern:** Assuming `@shared_task` definition auto-
enrolls. It does not — S2001 F9 documented 4 of 5 consumer
tasks with `@shared_task` but zero `PeriodicTask` rows.

**DEFERRED activation posture (SIGN batch 3 Q9 STRENGTHEN):**
For DEFERRED / not-yet-scoped consumers (§17.2 rows marked
DEFERRED status), the activation mode is **TBD** and explicitly
excluded from the beat enrollment requirement until the consumer
promotes to REQUIRED + `Exists today = Y`. Contract does not
prescribe cadence for consumers whose implementation is not
designed.

**Anti-drift rule (SIGN batch 3 Q9 STRENGTHEN):** A REQUIRED
consumer with `Exists today = Y` and activation_mode unset is a
**contract violation**. Adopters MUST fill activation_mode when
promoting a consumer to REQUIRED-with-implementation.

**Activation mode column in §17.2 (implicit per SIGN batch 3
Q9 STRENGTHEN):** §17.2 rows carry implicit activation mode
information via the `Beat enrollment` column. Adopter arcs may
extend the registry with an explicit `activation_mode` column
without breaking §17.2 semantics.

**Teeth clause — REQUIRED+exists-today=Y verification (Rigby
S2002 SIGN cycle 1 batch 4 Q10c FOLD):** For any consumer marked
REQUIRED with `Exists today = Y`, missing activation_mode is a
**contract violation**. P3 (S2003) verification MUST record the
concrete activation artifact per row: (a) `PeriodicTask` row
name (if activation mode is periodic cadence), (b) worker
subscription entrypoint (if activation mode is long-running
worker), OR (c) on-demand trigger path (if activation mode is
external-trigger). Without a recorded activation artifact, the
consumer row is a `defined-but-dormant` defect — the exact
S2001 F9 recurrence pattern this rule prevents.

**DEFERRED graduation trigger obligation (Rigby S2002 SIGN cycle 1
batch 4 Q11 STRENGTHEN):** Every DEFERRED consumer row in §17.2
MUST include (a) a **promotion trigger** (event-based condition
that graduates DEFERRED → REQUIRED) and (b) a **default owner**
(may be "unassigned" but MUST be explicit). Without a graduation
trigger, DEFERRED rows silently rot; without an owner, the
graduation trigger has no accountable steward.

## 18. Ownership Gaps

### 18.1 auto_escalate ownership gap (T1)

- **Method:** `HumanAttentionItem.auto_escalate` — does not exist.
- **Service owner:** No HALifecycleService method exists for
  escalation.
- **Caller:** No beat task, no REST endpoint.
- **Root cause:** Escalation path unowned per S1899 §1 break-
  point D (inherited S1801 D5).
- **Contract impact:** `HAI_AUTO_ESCALATED` event (§7.4) has no
  emission site. Contract designed for post-repair adoption.
- **Ownership assignment:** HAI arc — R.HAI.LOOP-COUPLING-
  REPAIR-ADR-BUNDLE T0/Gate CRITICAL resolves.

### 18.2 Consumer registry stewardship gap (T3)

- **Registry maintenance:** §17.2 declares expected consumers;
  no arc owns the registry-as-implementation-truth.
- **Root cause:** Contract-first design; implementation gap.
- **Contract impact:** Adopters may implement inconsistent
  consumers or omit REQUIRED consumers.
- **Ownership assignment:** Group 2000+ P99 (S2099) canonical
  summary owns registry-verification at arc close. Post-arc
  implementation arc updates individual rows.

### 18.3 Handler-failure DLQ ownership gap (T8, inherited S2001 F14/F15)

- **Handler failure flow:** Handler failures increment counter
  but do NOT ACK + do NOT flow to DLQ.
- **Root cause:** S2001 F14/F15 documented gap in
  `EventConsumerWorker.process_batch` (event_handlers.py:415-475).
- **Contract impact:** P2 events face at-least-once + no dedup
  surface at consumer failure boundary.
- **Ownership assignment:** Group 2000+ P4 (S2004 Cat F
  consolidation) — handler-failure discipline is separation-
  boundary concern.

### 18.4 Group 1900 authority MECHANISM ownership boundary

- **Ownership:** Group 1900 authority MECHANISM arc.
- **P2 contribution:** §20.9 event-emission contract shape.
- **Handoff shape:** Contract MUST NOT infer mechanism; §20.9
  explicit contract-vs-mechanism separation.

### 18.5 Joint retention ADR resolution ownership

- **Ownership:** Group 1700 canonical summary (S1799) +
  Group 1800 canonical summary (S1899).
- **P2 contribution:** §12.5 + §12.6 rejection commentary + §17.4
  handoff.
- **Handoff shape:** ADRs resolve post-P2; contract accommodates
  either resolution posture.

### 18.6 source_kind enum ADR ownership

- **Ownership:** Group 1300 canonical summary + Group 1800
  canonical summary (joint).
- **P2 contribution:** Consumes enum values per D2 + §7.5.
  Does NOT re-open ADR scope.

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows (per
playbook §11.2 §19 discipline). Higher rank = higher priority.

### R1 (HIGH — post-arc implementation arc)

**Scope:** Implement EventStream enum extension + publisher
wrappers + consumer workers + beat enrollment for the 4 HAI
candidate transitions (§7) + 5 plane-transition events (§10).

**Why HIGH:** Full contract-to-runtime materialization; unblocks
consumer contract obligations per §17.2 REQUIRED rows.

**Blockers:** T1 auto_escalate ownership (R.HAI.LOOP-COUPLING-
REPAIR-ADR-BUNDLE break-point D); T5 retention ADR joint
resolution; T6 source_kind enum ADR joint resolution.

**Dependency:** P2 (this arc) + T1/T5/T6 pre-conditions.

### R2 (HIGH — Group 1900 authority MECHANISM arc)

**Scope:** Consume §20.9 F.PER-USER-AUTHORITY-MECHANISM contract;
design per-user authority resolution logic + AuthorityService +
PerUserAuthorityPolicy model + consumer implementation.

**Why HIGH:** Unblocks per-user authority resolution capability
across the platform.

**Blockers:** P2 (contract shape) shipped; Group 1900 arc scope
open.

### R3 (MEDIUM — S1802 FeedbackProcessor refactor)

**Scope:** Replace S1802 F7 post_save signal (exception-swallow)
with `HAI_DECISION_RECORDED` consumer per §17.2. Closes S1802
F7 defect.

**Why MEDIUM:** Improves feedback plane reliability; not blocking.

**Blockers:** R1 (event contract emission live).

### R4 (MEDIUM — SportsBettingLearningBridge S1805 F4 asymmetric closure)

**Scope:** Wire SportsBettingLearningBridge as consumer of
`HAI_VERIFICATION_RECORDED` per §17.2. Closes S1805 F4 asymmetric
coupling.

**Why MEDIUM:** Restores bi-directional coupling; closes sports
learning loop.

**Blockers:** R1 (event emission live) + T10 (S1805 F1 automated
verification path beat enrollment).

### R5 (MEDIUM — Group 2000+ P3 6-substrate arbitration)

**Scope:** Consume P2 D5 per-transition substrate recommendations;
finalize 6-substrate rule set across EventBus + WebSocket +
CeleryTaskEvent + LLMCallEvent + OpsRunEvent + ToolCallRecord.

**Why MEDIUM:** Architectural closure for cross-substrate
composition; P2 recommends per event but P3 has arc scope for
arbitration.

**Blockers:** P2 shipped; P3 arc scope open.

### R6 (MEDIUM — Handler-failure DLQ gap resolution)

**Scope:** S2001 F14/F15 resolution. Handler failure MUST ACK +
move to DLQ + consumer registry declares DLQ consumer per event.

**Why MEDIUM:** Adopters accept at-least-once + no dedup surface
without this; contract mitigates via `event_id` idempotency (§7.7
rule 4) but full at-most-once semantics blocked.

**Blockers:** S2001 F14/F15 debt; T8 owner (Group 2000+ P4 Cat F
consolidation).

### R7 (LOW — Coverage-query dashboards T3.9)

**Scope:** Implement observability projection consuming
`BRIDGE_DISPATCHED` + `NON_BRIDGE_LEARNING_WRITE` per S1806 R11.
Cross-plane query dashboard.

**Why LOW:** Operational observability; not blocking.

**Blockers:** R1 (Class-2 event emission live).

### R8 (LOW — Non-bridge routing decision T1.12 audit)

**Scope:** Post-adoption, materialize `NON_BRIDGE_LEARNING_WRITE`
consumer that audits the 4 non-bridge sites for T1.12 routing
decision (migrate to bridge vs stay non-bridge vs consolidate).

**Why LOW:** Documented in S1899 §8.2 T1.12; audit is post-arc
consumer work.

**Blockers:** R1 (event emission live).

### R9 (LOW — External signal + shadow service activation)

**Scope:** Activate Reddit / Bluesky external signal bridges out
of D6 dead-code status; consolidate 4 shadow services per S1806
R1. Emissions land on P2-designed contract streams.

**Why LOW:** External signal / shadow service planes are deferred
per §10.5 + §10.6.

**Blockers:** D6 dead-code decision (external signal); S1806 R1
consolidation (shadow service).

### R10 (LOW — F.PER-USER-AUTHORITY-MECHANISM cross-substrate audit)

**Scope:** Once Group 1900 mechanism ships, audit whether the
F.PER-USER-AUTHORITY-MECHANISM events cross substrates as
expected (OpsRunEvent audit + EventBus real-time signals for
authority-triggered actions).

**Why LOW:** Post-Group 1900 audit; not blocking.

**Blockers:** R2 (Group 1900 arc completion).

## 20. Appendix

### 20.1 Files inspected

- `core/services/event_bus.py` — EventStream enum + STREAM_MAX_LEN
  + publisher wrappers.
- `core/services/event_handlers.py` — consumer worker structure.
- `core/models_human_interface.py` — HumanAttentionItem +
  HumanFeedbackRecord + HumanPreference models.
- `core/services/human_interface_service.py` — record_decision
  service layer.
- `core/services/human_attention_lifecycle.py` — HALifecycleService
  auto_approve path.
- `core/services/betting_outcome_verifier.py` — automated
  verification caller.
- `core/models_orchestration.py` — OrchestratorApprovalRequest
  (namespace collision surface).
- `core/models_ops_runs.py` — OpsRunEvent audit substrate.
- `core/tasks.py` — Celery consumer tasks + process_hai_lifecycle
  beat.
- `core/settings.py` — task_routes for consumer tasks.
- `core/celery.py` — beat_schedule code-defined authoritative.
- `core/views_human_interface.py` — REST endpoint dispatch.

### 20.2 Docs inspected

- `docs/research/domains/event_integration_architecture/2000_event_integration_architecture_domain_scoping.md` (parent §5.2).
- `docs/research/domains/event_integration_architecture/2001_event_integration_architecture_cat_a_eventbus_producer_consumer_map_child_audit.md` (S2001 baseline, all sections).
- `docs/research/symbol_mapping_event_schema_design.md` (S1275 §7.1/§7.3/§7.5/§9/§11/§12).
- `docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md` (S1806 §10 durable-at-six catalog).
- `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md` (S1899 §8.1 items 3/4/5/6 + break-points A/B/C/D).
- `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_child_audit.md` (S1903 §19 F.PER-USER-AUTHORITY-MECHANISM inheritance).
- `docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md` (Group 1900 canonical summary).
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 template + §14 evidence + §15 SIGN + §16 draft-first).

### 20.3 Grep patterns used

- `def record_decision\|def record_verification\|def auto_approve\|def auto_escalate` across `core/`.
- `EventStream\|EventBus\|STREAM_MAX_LEN` across `core/services/event_bus.py`.
- `schema_version\|source_kind` across `core/`.
- `publish_[a-z_]+_event` across `core/` (extends S2001 pre-Explore item c).
- `EventBus.subscribe\|consumer_group` across `core/`.
- `PeriodicTask.objects.filter\|beat_schedule` across `core/` + ORM probe.
- `OpsRunEvent.objects.create\|domain=` across `core/`.
- `post_save.*HumanFeedbackRecord\|post_save.*HumanAttentionItem` across `core/`.

### 20.4 Unresolved unknowns

- **U1: exact emission-site for record_decision.** §7.1
  recommends `HumanInterfaceService.record_decision:353`. Post-arc
  adopter may prefer model-method emission for callers that
  bypass the service layer (BulkAttentionDecideView refactor
  pending per S2001 T2.5). Contract accommodates either; adopters
  decide.
- **U2: auto_escalate method signature.** §7.4 recommends
  `def auto_escalate(self, reason: str)` but the reason enum
  values are unowned. Post-repair (R.HAI.LOOP-COUPLING-REPAIR-
  ADR-BUNDLE break-point D resolution) fills the enum.
- **U3: F.PER-USER-AUTHORITY event names.** §20.9 recommends
  three (`authority_check_evaluated`, `authority_decision_
  overridden`, `authority_policy_bound_to_user`) but Group 1900
  mechanism may design different event topology (more granular,
  fewer, or different names). P2 contract shape is a
  recommendation; Group 1900 arc may modify.
- **U4: retention posture for plane-transition events under
  joint ADR.** §17.3 places all Class-2 as bounded via Redis
  MAXLEN=10000; joint retention ADR may impose additional posture
  (e.g., audit-mirror to OpsRunEvent for specific plane
  transitions). Contract accommodates but does not pre-commit.

### 20.5 Conflicts between sources

None discovered at S2002 open. S1275 event schema + S1806 §10
durable-at-six catalog + S1899 §8.1 R.EVENTS.HAI-EVENT-CONTRACT-
CANDIDATES + S2001 §10.4 γ current-state baseline + S1903 §19
F.PER-USER-AUTHORITY-MECHANISM are all mutually consistent.

If Rigby SIGN cycle 1 discovers a conflict, folded into a §20.5
appendix row.

### 20.6 Verifier-loop corrections

Pending Rigby SIGN cycle 1 pressure-test. Folds landed pre-commit
recorded here at SIGN completion.

*(Placeholder — populated at SIGN cycle 1 fold-in.)*

### 20.7 Finding index

| Finding | Type | Risk | Section | Rationale |
|---|---|---|---|---|
| F0 | boundary_violation | LOW | §16.2 | OrchestratorApprovalRequest.auto_approve vs HAI auto_approve name collision |
| F1 | dead_code | MEDIUM | §7.4 + §18.1 | auto_escalate method + owner service missing |
| F2 | technical_debt | HIGH | §15 T1-T10 | 10-item post-arc implementation debt inventory |
| F3 | drift | HIGH | §14.4 + §17.1 (6) | Handler-failure DLQ gap (inherited S2001 F14/F15) |
| F4 | missing_connection | HIGH | §16.3 + §17.2 | SportsBettingLearningBridge asymmetric coupling (S1805 F4) — contract resolves |
| F5 | missing_connection | MEDIUM | §5.4 + §17.2 | S1802 FeedbackProcessor post_save signal fragility — contract-adoption path via consumer |
| F6 | boundary_violation | LOW | §16.1 | auto_approve bypass of record_decision (S1802 Q2 orphan) |
| F7 | boundary_violation | LOW | §16.4 | Group 1900 authority MECHANISM boundary — MUST NOT infer mechanism from contract |
| F8 | drift | MEDIUM | §14.3 | EventBus vs OpsRunEvent duality drift risk (D5 hybrid strategy) |
| F9 | drift | MEDIUM | §14.3 | Plane-transition + candidate-transition duplication risk |
| F10 | technical_debt | HIGH | §17.5 + §18.3 | Beat-enrollment discipline required per D4 (S2001 F9 constraint) |
| F11 | boundary_violation | MEDIUM | §12.5 + §17.4 | Joint retention ADR posture; P2 recommends per-class not uniform |
| F12 | unclear_owner | HIGH | §18.5 | Joint retention ADR ownership (Group 1700 + Group 1800 handoff) |
| F13 | unclear_owner | HIGH | §18.4 | Group 1900 authority MECHANISM ownership boundary |
| F14 | drift | LOW | §14.1 | Envelope-level drift risks (producer inconsistency, source_kind enum drift, event_type string drift) |
| F15 | drift | LOW | §14.2 | Payload-level drift risks (NULL rate, wrong non-NULL, stale producer per S1275 §12) |
| F16 | mature_primitive | (positive) | §12.1 + D1 | S1275 per-event schema_version graduation contract adopted; mature enough to underpin HAI event evolution |
| F17 | extraction_candidate | LOW | §10.7 | Cross-plane query enabler post-adoption; extract into shared consumer library |
| F18 | mature_primitive | (positive) | §7.0 + §10.0 | Shared envelope structure across HAI events + plane-transition events; enables cross-substrate consumer reuse |
| F19 | technical_debt | HIGH | §7.4 pre-condition + §18.1 | auto_escalate blocked on R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE break-point D |
| F20 | extraction_candidate | MEDIUM | §7.6 | S1275 §7.3 optional envelope field set — 5-field inheritance is candidate for shared envelope specification |
| F21 | technical_debt | MEDIUM | §17.3 + §18 (new gap) | OpsRunEvent write-volume risk for `authority_check_evaluated` + `auto_approve` + `auto_escalate` at platform scale (Rigby S2002 SIGN cycle 1 batch 4 Q11 STRENGTHEN). At storm-scale authority checks per user action, OpsRunEvent audit table grows unbounded — retention TTL (§17.3) is the primary lever but indexing pressure and write-amplification remain. Post-arc obligation: expected event rate ranges + indexing considerations + sampling / aggregation posture per §20.9.0 extension hook |
| F22 | unclear_owner | MEDIUM | §18 (new gap) + §17.2 | `security_audit_consumer` is REQUIRED (3-way — HAI_DECISION_RECORDED + HAI_AUTO_APPROVED + HAI_AUTO_ESCALATED-minimal) but has unclear owner / ship-arc (Rigby S2002 SIGN cycle 1 batch 4 Q11 STRENGTHEN). Remediation pointer: likely Group 1900 authority MECHANISM arc extension, OR a new "Security Audit Surface" arc; owner assignment + acceptance criteria required |

### 20.8 Design decision index (recap)

- **D1** — Adopt S1275 per-event `schema_version` (§12.1).
- **D2** — Adopt R.HAI.SOURCE-KIND-ENUM-ADR enum as envelope
  field (§7.0 + §7.5).
- **D3** — Two-class retention posture (Class-1 audit-forever
  / bounded-history; Class-2 bounded-history) (§17.3).
- **D4** — Beat-enrollment as first-class consumer registry
  contract obligation (§17.5).
- **D5** — Hybrid emission strategy per transition (2 EventBus,
  2 OpsRunEvent) (§7.1-§7.4 + §17.3).

### 20.14 Proposed Draft Schema for HAI_AUTO_ESCALATED (non-binding, per SIGN batch 3 Q8 FOLD)

**Status:** NON-BINDING. Payload schema pending R.HAI.LOOP-
COUPLING-REPAIR-ADR-BUNDLE T0/Gate CRITICAL break-point D
resolution. Reserved-minimal contract in §7.4 is the binding
piece; this appendix is candidate expansion the resolution arc
may adopt or replace.

**Candidate payload fields (proposed; adopters may modify):**

| Field | Type | Proposed required? | Candidate source | Rationale |
|---|---|---|---|---|
| `time_since_created` | duration | ○ | Derived: `emitted_at - hai_item.created_at` | Age at escalation |
| `time_since_last_view` | duration \| null | ○ | Derived: `emitted_at - hai_item.last_viewed_at` (if HAI has `last_viewed_at`; post-arc field) | Attention decay indicator |
| `escalation_ladder_position` | int (1-N) | ○ | Derived: N-th escalation in item lifecycle | Multi-escalation tracking; assumes escalation is per-item incremental (may be wrong if resolution designs time-window aggregation instead) |
| `prior_hai_status` | str (enum) | ○ | Derived (typically `deferred` or `pending`) | State-transition context |
| `new_hai_status` | str (enum) | ○ | Derived (typically `escalated` — assumes escalation adds a new HAI state; may be wrong if resolution designs escalation as an out-of-band signal without state change) | State-transition context |
| `notification_targets` | list[str] | ○ | Derived from HumanPreference notification plane | Who was notified downstream |
| `aggregation_window_start`, `aggregation_window_end` | datetime | ○ | Non-binding candidates IF resolution designs time-window aggregation | Alternative to per-item incremental escalation |

**What the resolution arc decides:**

- **Per-item vs time-window aggregation.** Does escalation fire
  per-item (as this reserved contract assumes) or over aggregated
  time windows? Resolution answers.
- **New status vs out-of-band signal.** Does escalation create
  a new HAI state (e.g., `escalated`) or is it an audit-only
  signal without state change?
- **Escalation ladder semantics.** Is escalation single-shot,
  incremental (ladder position), or unbounded (attention-decay
  signal)?
- **Reason enum members.** Which enum values does
  `escalation_reason_code` accept?

Post-resolution: this appendix migrates into §7.4 body OR is
replaced by resolution-arc-designed schema. §7.4 reserved
contract remains binding; §20.14 is provisional.

### 20.9 F.PER-USER-AUTHORITY-MECHANISM Event-Emission Contract

*(Per S1903 §19 inheritance. Per parent §5.2 deliverable 6.
Contract semantics ONLY. Mechanism (resolution logic,
AuthorityService reads, per-user policy binding) is OUT OF SCOPE
per parent §5.2 + Rigby S2000 SIGN cycle 1 Q1 fold. Group 1900
authority MECHANISM arc consumes this contract; the mechanism
is not designed here.)*

#### 20.9.0 Provisional contract surface disclaimer (Rigby S2002 SIGN cycle 1 batch 3 Q7 STRENGTHEN)

Per SIGN batch 3 Q7 STRENGTHEN fold — these events define **what
MUST be observable**, not how authority is computed. Group 1900
authority MECHANISM arc consumes this contract as **provisional
contract surface**; Group 1900 mechanism scoping may extend the
event set per the graduation rules in §12.1 (minor bump adds
allowed; major bump only if canonical substrate changes).

**Volume rationale (SIGN batch 3 Q7 STRENGTHEN):** P2 does NOT
emit `AUTHORITY_CHECK_STARTED` alongside `AUTHORITY_CHECK_EVALUATED`
to avoid check-storm amplification (a high-volume path invoking
`AuthorityService.check(...)` many times per user action would
emit 2N events instead of N). `AUTHORITY_CHECK_EVALUATED` is the
canonical per-evaluation tracepoint. If storm-audit is needed,
Group 1900 may add STARTED as a minor bump — but only gated by
sampling / aggregation rules per §20.9.6 extension hook.

**Audit-log-first classification (SIGN batch 3 Q7 STRENGTHEN
extending §7.9 posture):** F.PER-USER-AUTHORITY events are
**audit-log-first**; canonical substrate is OpsRunEvent (not
EventBus per §7.9 default). EventBus canonical emission is
OPTIONAL and only required if downstream non-governance consumers
(e.g., real-time authority-decision dashboards) are expected. If
Group 1900 later promotes any of the 3 events to EventBus, it is
a **major bump** (substrate change per §12.1) UNLESS introduced
as a mirror carrying the same `event_id` as the OpsRunEvent
canonical.

**Sampling / aggregation extension hook (SIGN batch 3 Q7
STRENGTHEN):** Group 1900 may add a future
`AUTHORITY_CHECK_AGGREGATE_WINDOW` event rather than emitting a
STARTED/EVALUATED pair — this shape allows storm-scale auditing
without forcing per-check start/stop instrumentation. Event shape
proposed here for future adoption; contract accommodates via
§12.1 minor bump.

#### 20.9.1 Contract-vs-mechanism boundary

**In scope for §20.9:**
- Event names + envelope + payload schema.
- Recommended substrate per event.
- Recommended emission trigger criteria.
- Consumer contract obligations (§17.2 rows).
- Retention posture per event class.
- Interaction with the 4 HAI candidate transitions (§7).

**Out of scope for §20.9 (Group 1900 owns):**
- Authority resolution logic.
- `AuthorityService` design.
- `PerUserAuthorityPolicy` model design.
- Per-user policy binding mechanism.
- Authority-check evaluation semantics.
- Override validation logic.

#### 20.9.2 Recommended events

| Event | source_kind (per D2) | Substrate | Retention class | Emission trigger criteria |
|---|---|---|---|---|
| `AUTHORITY_CHECK_EVALUATED` | `HAI_mediated` (if HAI-plane) or `other` (if system-scoped) | OpsRunEvent (audit-forever) | Class-1 | Fires when `AuthorityService.check(...)` (Group 1900 mechanism) evaluates a policy binding + returns a decision |
| `AUTHORITY_DECISION_OVERRIDDEN` | `HAI_mediated` | OpsRunEvent (audit-forever) | Class-1 | Fires when a manual override modifies an authority decision post-evaluation |
| `AUTHORITY_POLICY_BOUND_TO_USER` | `other` | OpsRunEvent (audit-forever) | Class-1 | Fires when a policy binding writes to `PerUserAuthorityPolicy` (Group 1900 model) |

#### 20.9.3 AUTHORITY_CHECK_EVALUATED payload

**Substrate:** OpsRunEvent.

- `domain = "authority_enforcement"`
- `event_type = "authority_check_evaluated"`
- `occurred_at = <emission time>`
- `payload = { ... envelope + P2 payload fields ... }`

**Payload fields:**

| Field | Type | Required | Rationale |
|---|---|---|---|
| `user_id` | str (UUID) | ✓ | Actor scope (whose authority) |
| `policy_id` | str (UUID) | ✓ | Group 1900 PerUserAuthorityPolicy row referenced |
| `policy_scope` | str (enum) | ✓ | Scope discriminator (Group 1900 designs enum) |
| `decision` | str (enum) | ✓ | `ALLOWED` / `DENIED` / `ESCALATED` / other Group 1900-designed |
| `decision_rationale` | str | ○ | Free-form or structured (Group 1900 designs) |
| `evaluated_at` | datetime | ✓ | Evaluation timestamp |
| `caller_context` | JSON | ○ | Downstream caller identity (which method fired the check) |
| `related_hai_item_id` | str (UUID) \| null | ○ | Related HAI item (if evaluation was HAI-triggered) |
| `related_decision_id` | str (UUID) \| null | ○ | Related HFR (if HAI-mediated) |
| `authority_scope` (envelope) | str \| null | ✓ | Per-user authority binding (may be null for system-scope) |

#### 20.9.4 AUTHORITY_DECISION_OVERRIDDEN payload

**Substrate:** OpsRunEvent.

- `domain = "authority_enforcement"`
- `event_type = "authority_decision_overridden"`
- `occurred_at = <emission time>`

**Payload fields:**

| Field | Type | Required | Rationale |
|---|---|---|---|
| `user_id` | str (UUID) | ✓ | Actor scope |
| `overridden_by_user_id` | str (UUID) | ✓ | Actor doing the override |
| `original_check_event_id` | str (UUID) | ✓ | Reference to prior `AUTHORITY_CHECK_EVALUATED` event |
| `original_decision` | str (enum) | ✓ | Prior decision |
| `override_decision` | str (enum) | ✓ | New decision |
| `override_reason` | str | ✓ | Rationale for override |
| `override_at` | datetime | ✓ | Override timestamp |

#### 20.9.5 AUTHORITY_POLICY_BOUND_TO_USER payload

**Substrate:** OpsRunEvent.

- `domain = "authority_enforcement"`
- `event_type = "authority_policy_bound_to_user"`
- `occurred_at = <emission time>`

**Payload fields:**

| Field | Type | Required | Rationale |
|---|---|---|---|
| `user_id` | str (UUID) | ✓ | Actor scope |
| `policy_id` | str (UUID) | ✓ | Group 1900 PerUserAuthorityPolicy row created / updated |
| `policy_scope` | str (enum) | ✓ | Scope discriminator |
| `binding_action` | str (enum) | ✓ | `CREATED` / `UPDATED` / `REMOVED` |
| `binding_reason` | str | ✓ | Rationale for binding |
| `bound_at` | datetime | ✓ | Binding timestamp |
| `bound_by_user_id` | str (UUID) | ○ | Actor doing the binding (if administratively initiated) |

#### 20.9.6 Interaction with HAI event contracts (§7)

**Envelope field pass-through.** The §7.0 envelope declares
`authority_scope` (optional) — an authority binding identifier
populated when applicable. HAI events (record_decision,
record_verification, auto_approve, auto_escalate) populate this
field if the HAI transition was authority-gated.

**Cross-event correlation.** F.PER-USER-AUTHORITY events reference
HAI event `event_id` via `related_hai_item_id` +
`related_decision_id` (§20.9.3). This creates a cross-substrate
audit-trace: HAI event on EventBus / OpsRunEvent + authority event
on OpsRunEvent share a `related_*` correlation ID.

**Emission ordering.** When an HAI transition is authority-gated:

1. `AUTHORITY_CHECK_EVALUATED` fires FIRST (before HAI state
   change).
2. HAI event fires SECOND (post-state-change, per §8.2
   lifecycle bindings).
3. If overridden: `AUTHORITY_DECISION_OVERRIDDEN` fires THIRD
   (post-override).

Consumers reading OpsRunEvent by `occurred_at` see the ordering.

#### 20.9.7 Consumer contract obligations (specific to F.PER-USER-AUTHORITY-MECHANISM)

Per §17.1 universal obligations + F.PER-USER-AUTHORITY-specific:

1. **Group 1900 arc arc-close obligation.** Group 1900 canonical
   summary MUST update §17.2 registry row
   `authority_resolution_consumer` with the actual consumer
   implementation identity + verified status.
2. **Cross-domain audit consumer.** Governance dashboards MUST
   project OpsRunEvent audit rows for `authority_enforcement`
   domain per §17.2.
3. **Downstream HAI-consumer awareness.** HAI consumers (per
   §17.2 REQUIRED rows) MUST accept envelope `authority_scope`
   field + not fail on null.

#### 20.9.8 What Group 1900 arc consumes from this contract

- **Event names + envelope + payload schema.** Contract-frozen
  once P2 ships. Group 1900 arc may add fields (minor bump per
  §12.1 graduation contract) but MUST NOT remove or rename
  required fields without major bump.
- **Recommended substrate per event.** Group 1900 mechanism
  implementation writes to OpsRunEvent per §20.9.2. Deviation
  requires §17 registry update.
- **Consumer registry contract.** §17.2 row for
  `authority_resolution_consumer` is the contract Group 1900
  fulfills.
- **Retention posture.** Class-1 audit-forever per D3 + §17.3.

#### 20.9.9 What this contract does NOT bind

- **Group 1900 mechanism design.** Resolution logic,
  AuthorityService structure, PerUserAuthorityPolicy shape.
  Group 1900 arc chooses.
- **Additional events beyond the 3 named.** Group 1900 may add
  more (e.g., `AUTHORITY_POLICY_VIOLATION_DETECTED`) — minor bump
  per §12.1 graduation contract; contract accommodates extension.
- **Enum values within events.** `decision`, `policy_scope`,
  `binding_action`, etc. — Group 1900 finalizes enum members.
  P2 contract specifies the fields exist; not the enum contents.

### 20.10 Rigby SIGN cycle 1 pressure-test payload

Per parent §5.2 SIGN cadence + playbook §15 stage-scoped routing.

**Pressure-test focus areas** (Rigby to challenge):

1. **D1 versioning policy pick.** Is S1275 the right adoption
   vs. designing an HAI-specific policy? §12 alternatives cover
   3 rejections; is any of them stronger than P2 believes?
2. **D3 two-class retention posture.** Is Class-1 audit-forever
   right for `auto_approve` + `auto_escalate` given OpsRunEvent
   scale considerations? Should Class-2 have OpsRunEvent
   audit-mirror rows for specific planes?
3. **D5 hybrid emission strategy.** Is placing `auto_approve` +
   `auto_escalate` on OpsRunEvent + `record_decision` +
   `record_verification` on EventBus the right split? Should
   any be on both substrates?
4. **§17.2 consumer registry completeness.** Are any REQUIRED
   consumers missing? Are any listed as OPTIONAL that should be
   REQUIRED?
5. **§20.9 F.PER-USER-AUTHORITY-MECHANISM contract shape.** Does
   the 3-event set cover the authority resolution surface?
   Should there be more granular events (e.g., separate
   `AUTHORITY_CHECK_STARTED` before `AUTHORITY_CHECK_EVALUATED`)?
6. **§14.4 handler-failure DLQ gap acceptance.** Is at-least-
   once with idempotency-key dedup acceptable for governance
   events, or must S2001 F14/F15 resolve before P2 contract can
   adopt?
7. **§10.1 + §10.4 subsumption.** Do §10.1 HAI-mediated and §10.4
   verification_outcome plane events truly subsume the §7.1 and
   §7.2 candidate transitions? Or is a distinct plane-transition
   event required alongside?
8. **§7.4 auto_escalate contract vs pre-condition.** Should P2
   ship the contract when the method does not exist at HEAD +
   the R.HAI.LOOP-COUPLING-REPAIR-ADR-BUNDLE break-point D
   resolution is post-arc? Or should P2 defer §7.4 to a future
   arc?

**Expected fold posture:** Cycle 1 pre-commit expected CLEAN or
folds landed pre-commit (per S2001 CYCLE1-CLEAN precedent).
Cycle 2 optional post-Chris-gate to pressure-test D1 versioning
choice per parent §5.2 SIGN cadence.

### 20.11 Zero-UNKNOWN attestation

Every one of the 4 candidate transitions has a payload schema
(§7.1-§7.4) + retention posture (§17.3) + consumer registry
entry (§17.2). `auto_escalate` (does not exist at HEAD) is
documented as MISSING implementation with recommended contract
shape — not parked as UNKNOWN.

Every one of the 6 planes (§10.1-§10.6) has plane-transition
event definition + `source_kind` enum binding + retention class.
Planes in deferred activation posture (external_signal + shadow_
service per §10.5 + §10.6) are documented as DEFERRED — not
parked as UNKNOWN.

Every one of the 3 F.PER-USER-AUTHORITY events (§20.9.2) has
payload + substrate + retention class + consumer registry entry.

### 20.12 Evidence-backed attestation

Every payload field in §7 + §10 + §20.9 cites either (a) a
current-code model field via file:line OR (b) is marked NEW with
design rationale in the Rationale column. Every versioning-policy
claim cites S1275 §-reference. Every retention-TTL claim cites
either R.OBSERVABILITY.RETENTION-UNIFIED-ADR posture or
R.HAI.RETENTION-UNIFIED-ADR posture with explicit T0/Gate
attribution.

### 20.15 Meta-methodology capture — What This SIGN Cycle Taught Us (Rigby S2002 SIGN cycle 1 batch 4 Q12 STRENGTHEN)

*(For xx99 §10 "What This Research Taught Us About How to Do
Research" inheritance per playbook §11.3 canonical summary
template. Captured pre-close so S2099 §10 has arc-local material
to fold.)*

**Batched-SIGN posture for large design-contract audits.** SIGN
cycle 1 for this 2600-line design contract ran in 4 batches with
12 pressure-test questions and 12 folds landed pre-commit
(confidence trend 0.82 → 0.80 → 0.79 → CLEAN-METHOD closing). A
single 3-4 question pass (the S2001 descriptive-audit precedent)
would have missed the cross-sectional coupling issues caught
here — specifically the canonical+mirror substrate rule (Q4) +
activation-mode reframe (Q9) + reserved-minimal auto_escalate
(Q8) + Class-2→Class-1 promotion rule (Q2) triangulation. The
fragmentation cost is outweighed by reduced reviewer thrash +
fewer late-inconsistency defects.

**Playbook §11.2 template update suggestion — design-contract
overlay:** Design-contract-shape audits (as opposed to
descriptive-audit shape like S2001) need **two additional
explicit sections / checklists** that descriptive audits don't:

1. **Contract Surface Matrix.** Per event: substrate → canonical
   vs mirror → versioning → retention class → idempotency key →
   activation mode → required consumers. Single table row per
   event → guarantees no dimension is missing. Enables cross-
   section drift detection (e.g., a v0.x-reserved event that
   accidentally declares v1.0.0 REQUIRED consumers).
2. **Consistency Invariants Checklist.** Reserved-minimal vs
   required consumers alignment; canonical/mirror scope
   boundaries (Class-1 vs Class-2); DEFERRED consumer promotion
   triggers; ownership required for REQUIRED consumers;
   verification hooks required for REQUIRED-with-exists-today=Y
   consumers.

**Meta-lesson.** Design contracts need a matrix + invariants
section; otherwise cross-section drift appears after folds. The
matrix is a **structural** solution to the drift risk that
manifested here as 3 cross-sectional folds in batch 4 alone.

**xx99 §10 handoff pointer.** S2099 canonical summary §10 folds
this meta-lesson into playbook §11.3 §20 two-triggers-rule
evaluation. If a second design-contract arc (post-P2) confirms
the same pattern, playbook §11.2 gains the design-contract
overlay per Chris directive at S1399 close.

### 20.13 Stream-by-stream discipline

§7.1-§7.4 use per-transition table format. §10.1-§10.6 use
per-plane subsection format. §17.2 uses per-consumer table
format. §20.9.3-§20.9.5 use per-authority-event subsection
format.


