---
title: "Decision Command / Boardroom — narrative (batch J)"
status: draft (batch J of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/governance_redesign.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/narratives/SIGNAL_INTELLIGENCE.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to governance_redesign.md, AGENTS.md, PLATFORM_INVENTORY, MEMORY.md feedback entries; deliberately cross-cuts narratives A/B/C/D)
provenance_note: Decision Command sits at the intersection of agent system (A), content pipeline (B), signal intelligence (C), and personal assistant (D). This narrative is the operator-handbook view of "the platform decides things and asks the human to confirm" — boardroom, attention queue, decisions, HiveMind consultations. Heavy cross-references; deliberately compact on topics already covered in A-D.
---

# Decision Command / Boardroom

> The platform's deliberation-and-decision surface.
> `DecisionEnforcerAgent` forces a verdict after multi-agent
> debate; `HumanAttentionItem` queues things requiring human
> review; `HiveMindSession` records the conversation that
> produced the decision; `AgentDecisionSummary` and the
> `publish_intent` enum formalize the decision's contract.
> The governance page is the UI surface that brings the
> queue, the gates, and the system-health snapshot together.

---

## 1. What this is

The Decision Command layer answers three operator questions:

1. **What needs my attention right now?** Surfaced through the
   unified `HumanAttentionItem` queue with urgency badges
   (critical / high / medium / low), type filters
   (decision / gate / remediation / alert), and batch
   actions (approve all / ignore all / snooze all). The
   governance page's planned redesign (per
   `governance_redesign.md`) makes "what needs me?" the
   above-fold question.
2. **What decisions has the platform already made on its own?**
   Surfaced via `AgentDecisionSummary` rows. Each carries a
   stance (publish / revise / kill, or domain-specific
   verdicts), insights, participating agents, and links to
   the originating HiveMind session.
3. **What's the contract for "this is meant to be public" vs
   "this is internal only"?** Answered by the `publish_intent`
   enum on Deliverables (`internal_only` /
   `publish_candidate` / `publish_required`) — Session 1095.

The decision layer doesn't run agents directly; it ratifies,
rejects, or routes outputs from the agents (narrative A), the
content pipeline (B), and the initiative pipeline (C). It is
the platform's "gate that closes" mechanism — the place where
"the system thought about this; here's the verdict; here's
what's left for the human."

Most of the engine for this lives in code paths covered in
narratives A–D. This doc maps how those engines compose into
a single operator surface.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`DecisionEnforcerAgent`** | The "Prefrontal Cortex" agent (Session 872). Forces a verdict after multi-agent debate. Forbids hedging phrases. Outputs `chosen_path`, `reason`, `kill_criteria`, `deadline`, `rejected_paths`, `acknowledged_risks`. Covered in narrative A milestone 3 + narrative B § 2. |
| **`HumanAttentionItem`** | The unified attention-queue row. Carries urgency, type (decision / gate / remediation / alert), source, owner, age. The "what needs me?" data source. Surfaced via the governance page + PA `governance_tool.attention_list`. |
| **`HiveMindSession`** | Multi-agent conversation tied to an Initiative via FK. Records the conversation that produced a decision. Carries `signal_cluster` FK + `auto_topic` FK for provenance. Covered in narrative C § 2 + milestone 2. |
| **`AgentDecisionSummary`** | The formal decision row. Includes topic, stance, insights, participants. Surfaced via PA's `governance_tool.decisions_list` and `decisions_stats`. |
| **`AIDecisionPromoterService`** | The service that promotes platform-made decisions to formal status when they meet acceptance criteria. The autonomic side of the decision loop — equivalent of the BodyCoordinator's reflex layer (narrative F § 2) but for governance. |
| **`publish_intent` enum (Session 1095)** | Deliverable model field. Values: `internal_only` / `publish_candidate` / `publish_required`. Distinct from `status` (workflow state). The contract that makes "should this be public?" a first-class field instead of inferred from `is_internal` boolean. Covered in narrative B milestone 8. |
| **Canary path (Sessions 1094–1098)** | Controlled-injection deliverable path that lets new agent behavior reach the production pipeline without going through the user-visible UI. Uses `publish_intent` to route the injection. Covered in narrative A milestone 7. |
| **`ResearchContract` / `ExecutionMandate` / `SynthesisContract` (Session 872)** | Contracts that prevent vague outputs from agents. Each names what the output must include (e.g., decisions, deadlines, acknowledged risks). Enforced at the prompt-shape level. |
| **TRIAGE intake state (Session 994)** | The pre-active state for auto-created initiatives. PA `update_status` promotes TRIAGE → ACTIVE. Prevents auto-generated work from polluting the active pipeline. Covered in narrative C milestone 3. |
| **Decision summary extraction (Session 902)** | `=== DecisionSummary ===` sections in HiveMind conversation conclusions get parsed into `InitiativeActionItem` rows. The pattern: agents close conversations with structured decision blocks; the platform extracts. Covered in narrative C milestone 4. |
| **Daily post cap + severity escalation (Session 1095/1096)** | Anti-spam governance: COO posts capped at 2/day, others at 3. Severity escalation rule (Session 1096) — repeated low-severity events promote to higher severity. Suppressed rollup counter. Covered in narrative A milestone 7. |
| **`gate_hang` + rework/bounce gate (Session 1095)** | Gates that catch stuck decisions. `gate_hang` flags decisions that have been pending too long without progression. Rework/bounce catches decisions that have ping-ponged between states. Both wire into `DeliverableEvent.status_transition` signal infrastructure. |
| **Governance gateway tool (Session 1079)** | PA `governance_tool` — one of the 6 gateway tools from the Session 1079 consolidation. Absorbed `boardroom_tool` + `human_decisions_tool`. Actions: `inbox`, `attention_list`, `attention_approve`, `attention_ignore`, `attention_lookup`, `decisions_list`, `decisions_stats`, `decision_create`, `decision_decide`, `decision_promote`, `decision_reject`, `triage_batch`. Covered in narrative D milestone 6. |
| **Governance page** | Frontend surface that renders the queue + filters + batch actions. Pre-redesign (current state) has three disconnected sections (Emergency Controls, Self-Healing, Pending Decisions). Post-redesign spec in `governance_redesign.md` consolidates into TriagePanel + UnifiedQueue. |
| **Boardroom learning** | `BoardroomLearningService` + `BoardroomMLService` (in inventory). The platform's mechanism for learning from boardroom decisions over time. Specifics live in `core/services/boardroom_learning_service.py`. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — disconnected governance surfaces** *(Inferred, pre-Session 872)* | Boardroom, decisions, and attention items existed as separate UI components with separate endpoints. The governance page had three sections (Emergency Controls, Self-Healing, Pending Decisions) — no unified queue, no filter bar, no batch actions. | The platform had decisions to make and humans to notify, but the surfaces were structured by source rather than by what-needs-the-human. Operators were doing manual filter + dedupe across three separate panels. | Decisions got made; the cognitive load on the operator was high. Spawned the redesign spec (current state, see milestone 6). | **Active as the current UI state.** Post-redesign spec exists in `governance_redesign.md` but is not yet implemented. | `docs/governance_redesign.md` §"Current State"; `frontend/src/pages/.../GovernanceTab.tsx` |
| **Session 872 — DecisionEnforcerAgent + contracts (the decisive-output discipline)** | `DecisionEnforcerAgent` ("Prefrontal Cortex") introduced. Forces verdicts after multi-agent debate. Forbids hedging. Outputs structured fields: `chosen_path`, `reason`, `kill_criteria`, `deadline`, `rejected_paths`, `acknowledged_risks`. `ResearchContract`, `ExecutionMandate`, `SynthesisContract` introduced as prompt-level contracts preventing agents from producing "research-shaped" or "open-ended-synthesis-shaped" outputs that don't commit to anything. `AutoSpawnerService` triggered as data-gathering reflex layer in the same arc. | Multi-agent debates were ending without verdicts. Agents were producing well-reasoned indecision. The platform needed a place where "discussion stops; verdict is recorded" was structurally enforced. Contracts made vague outputs impossible at the prompt level. | DecisionEnforcer is now part of the content pipeline (narrative B § 2) and any other multi-agent debate path. The contracts are reused across agents. The platform stopped producing decisions-shaped non-decisions. | **Active** — DecisionEnforcerAgent is in `AGENT_MAP`; contracts are part of the standard prompt-construction. | `docs/topics/agent-system.md` §"Executive Function (Session 872)"; `core/agents/decision_enforcer_agent.py`; cross-ref `docs/narratives/AGENTS_AND_AUTONOMY.md` milestone 3 |
| **Sessions 902 + 928 + 994 — initiative ↔ decision integration (cross-ref C)** | (902) `=== DecisionSummary ===` sections extracted from HiveMind conversation conclusions; `InitiativeActionItem` rows materialized with status, priority, timeline, agent + user assignment, M2M dependencies. (928) "Discuss with Agents" button on initiatives → creates `HiveMindSession` FK'd to initiative with full context (origin, stages, action items, signals); auto-selects relevant agents via `AgentRouter`. (994) TRIAGE intake state introduced; quality gate before promotion (reject 2+ explore patterns, require action verb, require 1000+ char conversation); activity tracking via `update_activity()`. PA `flow_metrics` action surfaces creation rate / backlog / stage distribution / circuit breaker. | Decisions were happening in HiveMind conversations but weren't surfacing as structured work. The integration made the conversation → decision → action-item → initiative path explicit. TRIAGE made auto-generated decisions a gated intake state. | Initiatives now carry structured action items extracted from decisions; conversations can be re-triggered from initiatives; TRIAGE-vs-ACTIVE separation prevents auto-decisions from drowning the human queue. Cross-ref narrative C milestones 3 and 4. | **Active** — full path is in production. | Cross-ref `docs/narratives/SIGNAL_INTELLIGENCE.md` milestones 3 + 4; `docs/topics/initiative-pipeline.md` §§"Action Item Tracking", "Initiative Conversations", "TRIAGE Status" |
| **Session 1079 — governance gateway consolidation (cross-ref D)** | PA `governance_tool` absorbed `boardroom_tool` + `human_decisions_tool` into a single gateway with 12+ actions (`inbox`, `attention_list`, `attention_approve`, `attention_ignore`, `attention_lookup`, `decisions_list`, `decisions_stats`, `decision_create`, `decision_decide`, `decision_promote`, `decision_reject`, `triage_batch`). Schema budget reduced; routing decisions cleaner; the gateway model became the standard pattern. | The PA had separate tools per governance concept (boardroom items, human decisions, attention items). Boundary lines weren't clean — the model sometimes called redundant tools. One gateway with an action enum is unambiguous. | One PA-tool surface for the whole decision/governance/attention space. Each action is documented; the PA picks the right one from natural-language intent. Cross-ref narrative D milestone 6. | **Active** — `governance_tool` is the standard PA path; the 12+ actions are the canonical action surface. | Cross-ref `docs/narratives/PERSONAL_ASSISTANT.md` milestone 6 |
| **Sessions 1094–1098 + 1095 — canary path + COO gates + publish_intent enum** | (1094) Scheduled diagnostic primitive — CTO / COO / TrendAnalysis as monitors that produce decisions, not just reports. Canary Step 1 (controlled injection paths). (1095) **Three concurrent shipments:** `gate_hang` gate; rework/bounce gate (with `DeliverableEvent.status_transition` signal infrastructure); `publish_intent` enum migration (`internal_only` / `publish_candidate` / `publish_required`) on Deliverable model — migration 0333 + backfill of 122 rows. (1096) Anti-spam safety rails — severity escalation rule; daily post cap (COO=2, others=3); suppressed rollup counter. (1098) Canary Step 2 (CW + Editor canary path) ratified GREEN. Plan A controlled injection committed; append cleanly (655 → 1907 chars, 0 integrity errors). Test artifact + blog intentionally live for 24h observation. | The platform's governance gates were rough. Decisions could hang (no time bound), bounce (loop between states), or be ambiguous about whether they're meant to be public. The COO and CTO were generating noise (60-min hangs from MeetingCoordinator thread leakage — disabled in Session 1099). All five sessions together created a governance layer that catches gate-hangs, rate-limits noisy agents, formalizes publish intent, and provides a canary path for new agent behavior. | Failure rate (per memory MEMORY.md "Session 1092 Governance Noise") projected 9.7 % → ~4 %. The canary is the standard rollout mechanism for new agent behavior. `publish_intent` is part of the deliverable contract; the canary uses it. Cross-ref narrative A milestone 7 and narrative B milestone 8. | **Active** — all these gates are in production; canary path is the standard rollout mechanism. | Cross-ref `docs/narratives/AGENTS_AND_AUTONOMY.md` milestone 7; `docs/narratives/CONTENT_PIPELINE.md` milestone 8; MEMORY.md `project_session_1095_coo_gates_complete.md`, `feedback_publish_intent_enum.md` |
| **Governance page redesign spec** *(date Unknown — `governance_redesign.md` exists)* | UX spec for collapsing the three-section governance page into a TriagePanel (above-fold, always-visible: CriticalCount badge, ApprovalsWaiting, StuckGates, SystemHealth) + UnifiedQueue (filter bar, sort control, batch bar, virtualized item rows). 7 implementation tickets. | The current governance page (three disconnected sections, no batch actions, no urgency routing) puts cognitive load on operators. The redesign answers "what needs me right now?" in under 5 s. | **Spec only.** Implementation status: not yet shipped (the current page is still the disconnected three-section version). Tickets queued. | **Active spec.** Implementation pending. | `docs/governance_redesign.md` |

---

## 4. What came of it

### Wins

- **Verdicts, not non-decisions.** DecisionEnforcerAgent
  (Session 872) is the "discussion stops; verdict is
  recorded" enforcement layer. Multi-agent debates now
  terminate.
- **Initiative ↔ decision is structured.**
  `=== DecisionSummary ===` extraction (Session 902) +
  "Discuss with Agents" (Session 928) make conversations
  re-triggerable and decisions auto-converted into action
  items.
- **TRIAGE separates raw decisions from human queue.**
  Auto-generated decisions go to TRIAGE; PA promotes to
  ACTIVE; the human attention queue stays focused.
- **`publish_intent` enum is a first-class field.** Session
  1095's migration 0333 + backfill closed the
  inference-from-boolean class. The canary path uses it
  directly.
- **Gate hangs are caught.** `gate_hang` + rework/bounce
  gates flag decisions stuck or ping-ponging.
- **Daily post cap enforces spam discipline.** COO=2,
  others=3. Severity escalation prevents floods.
- **One PA tool surface.** `governance_tool` with 12+
  actions covers the whole decision/governance/attention
  surface; the model routes via action enum, not
  tool-name.

### Tradeoffs

- **Governance page redesign is spec-only.** The
  three-section disconnected UI is still the current
  state. Operators are still doing manual filter + dedupe.
  Implementation queued; not shipped.
- **Reject-mode flip pending (cross-ref narrative D).**
  The PA-chat audit table is warm in warn-only mode.
  Reject-mode is gated on ≥ 3 days clean telemetry; not
  yet enabled.
- **`AIDecisionPromoterService` criteria are opaque.**
  Auto-promotion happens; the criteria aren't documented
  in any topic doc.
- **`HumanAttentionItem` urgency calibration.**
  Critical/high/medium/low tiers are heuristic-based; no
  empirical calibration recorded.
- **Boardroom learning** (`BoardroomLearningService` +
  `BoardroomMLService`) exists in inventory but isn't
  surfaced in any topic doc. Function inferred from name;
  details Unknown.
- **Governance signals span multiple narratives.**
  DecisionEnforcer (A), publish_intent (B), TRIAGE (C),
  governance_tool (D), governance page (G). An operator
  has to read across A-G to get the full picture; this
  narrative (J) is the index.
- **DecisionSummary extraction expects a specific marker.**
  `=== DecisionSummary ===` — if the agent's output drifts
  in format, action-item extraction silently fails. No
  schema enforcement.
- **Canary path is gated on Chris's manual review** (per
  Session 1098 close). The "GREEN" decision is a human
  call, not an automated one. Acceptable but a bottleneck.

### Follow-on systems enabled

- **Content pipeline (B)** — DecisionEnforcer at step 4 of
  the deliberation pipeline.
- **Initiative pipeline (C)** — DecisionSummary → action
  items → initiatives; TRIAGE state.
- **PA (D)** — `governance_tool` consolidates 12+ actions;
  reject-mode flip queued.
- **Agent governance arc (A milestone 7)** — gate_hang,
  rework/bounce, publish_intent, canary, daily post cap,
  severity escalation, scheduled diagnostics, verify_doc_claims.
- **`BodyCoordinator` reflex layer (F)** is the parallel
  autonomic reaction layer for infrastructure; the
  decision-layer is its peer for governance.

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot
> 2026-05-25 (git HEAD `d513cd7f`). The decision layer
> spans multiple subsystems — counts here cross-reference
> A–D.

**Tools.** PA `governance_tool` with 12+ actions:
`inbox`, `attention_list`, `attention_approve`,
`attention_ignore`, `attention_lookup`, `decisions_list`,
`decisions_stats`, `decision_create`, `decision_decide`,
`decision_promote`, `decision_reject`, `triage_batch`.

**Models.**
- `HumanAttentionItem` — unified attention queue rows.
- `AgentDecisionSummary` — formal decision rows.
- `HiveMindSession` — multi-agent conversations with
  `signal_cluster` + `auto_topic` FKs.
- `InitiativeActionItem` — extracted from
  `=== DecisionSummary ===` sections.
- `Deliverable` with `publish_intent` enum.
- `DeliverableEvent` with `status_transition` signal
  infrastructure.

**Services.**
- `DecisionEnforcerAgent` — `core/agents/decision_enforcer_agent.py`.
- `AIDecisionPromoterService` —
  `core/services/ai_decision_promoter.py`.
- `BoardroomLearningService` /
  `BoardroomMLService` — `core/services/boardroom_*.py`
  (function inferred from naming; details Unknown).

**Governance gates active.**
- `gate_hang` — pending too long without progression.
- rework/bounce — ping-pong between states.
- Daily post cap (COO=2, others=3).
- Severity escalation rule.
- Suppressed rollup counter.
- Canary path with `publish_intent` routing.
- `verify_doc_claims` doc-vs-reality.

**Frontend.** Governance page (three disconnected sections,
pre-redesign). Spec for redesign in
`docs/governance_redesign.md`. Implementation pending.

**Where to look when something stops working.**
- Attention queue not showing items → check
  `HumanAttentionItem` rows; check PA
  `governance_tool.attention_list` action; check the
  governance page data source.
- Decisions stuck → `gate_hang` should flag; check
  `DeliverableEvent.status_transition` rows for the
  decision's deliverable.
- DecisionSummary not extracting → agent output drifted
  from `=== DecisionSummary ===` marker format; check
  agent's conversation prompt template.
- TRIAGE backlog growing → PA hasn't run `update_status`
  TRIAGE → ACTIVE in a while; needs PA pass.
- `publish_intent` wrong → check the source that set it
  (canary path, content pipeline, initiative creation);
  enum values are `internal_only` / `publish_candidate` /
  `publish_required` — typos will fail enum validation.
- Daily post cap exceeded → check the agent's recent
  posts; cap is hardcoded per agent (COO=2, others=3) in
  the dispatch path.
- Boardroom learning unexpected → `BoardroomLearningService`
  / `BoardroomMLService` — function not documented in
  topic doc; read service code to understand current
  behavior.

---

## 6. Open questions / unknown outcomes

- **When does the governance page redesign ship?**
  *Known:* spec exists in `docs/governance_redesign.md`
  with 7 implementation tickets. *Unknown:* whether any
  tickets are in flight. The page is still the
  three-section pre-redesign UI.
- **`AIDecisionPromoterService` promotion criteria.**
  *Known:* it auto-promotes decisions. *Unknown:* the
  criteria (what makes a decision eligible). Read service
  code to enumerate.
- **`BoardroomLearningService` + `BoardroomMLService`
  function.** *Known:* both exist in inventory.
  *Unknown:* what they do beyond what naming suggests. No
  topic doc covers them.
- **PA-chat audit reject-mode flip status.** *Known:*
  queued on ≥ 3 days clean telemetry post-Session-1133
  merge. *Unknown:* current status. Cross-ref narrative
  D open question.
- **Daily post cap calibration.** *Known:* COO=2, others=3.
  *Inferred:* set in Session 1096 based on observed spam
  patterns. *Unknown:* whether the cap has been
  re-evaluated since.
- **DecisionSummary marker format.** *Known:*
  `=== DecisionSummary ===` is the literal extraction
  marker. *Unknown:* what happens when an agent's output
  drifts — does the extraction silently fail, or is there
  any monitoring? No specific failure-mode telemetry in
  the corpus.
- **`HumanAttentionItem` urgency calibration.** *Known:*
  4-tier (critical / high / medium / low). *Unknown:*
  whether the thresholds were tuned empirically or set
  by intuition.
- **Canary path Step 3+** — *Known:* Step 1 (Session
  1094) and Step 2 (Session 1098) are documented.
  *Unknown:* whether Step 3 exists or whether the canary
  is at its terminal state.

---

## 7. Source index

### Primary doc sources

- `docs/governance_redesign.md` — UX redesign spec for
  governance page (7 tickets; pending implementation).
- `docs/topics/agent-system.md` §"Executive Function
  (Session 872)" — DecisionEnforcer + contracts.
- `docs/topics/initiative-pipeline.md` §§"Action Item
  Tracking", "Initiative Conversations", "TRIAGE Status"
  — Sessions 902, 928, 994.
- `docs/topics/personal-assistant.md` §"Key tools (6
  gateways)" — `governance_tool` consolidation (Session
  1079).
- `docs/PLATFORM_INVENTORY.md` — `BoardroomLearningService`,
  `BoardroomMLService`, `AIDecisionPromoterService` listed
  in services inventory.

### Named session handoffs cited above

- Session 872 — DecisionEnforcer + contracts. Handoff
  filename in `docs/handoffs/`.
- Session 902 — DecisionSummary extraction → action items.
- Session 928 — initiative conversations.
- Session 994 — TRIAGE intake + quality gate + flow_metrics.
- Session 1079 — governance gateway consolidation.
- Sessions 1094 / 1095 / 1096 / 1098 — canary + COO gates
  + publish_intent + anti-spam rails. Memory files:
  `project_session_1094_governance_diagnostic_future_gates.md`,
  `project_session_1095_coo_gates_complete.md`,
  `project_session_1096_anti_spam_rails.md`,
  `project_session_1098_canary_green.md`.

### Code anchors

- `core/agents/decision_enforcer_agent.py` —
  DecisionEnforcer.
- `core/services/ai_decision_promoter.py` — auto-promoter.
- `core/services/boardroom_learning_service.py` /
  `core/services/boardroom_ml_service.py` — boardroom
  learning (details Unknown).
- `core.models` — `HumanAttentionItem`,
  `AgentDecisionSummary`, `HiveMindSession`,
  `InitiativeActionItem`, `Deliverable.publish_intent`.
- `core/tools/governance_tool.py` (or equivalent) — PA
  gateway tool with 12+ actions.
- Frontend `GovernanceTab.tsx` (pre-redesign).

### Verification commands

- `python manage.py generate_platform_inventory` —
  regenerate inventory.
- PA: `governance_tool action=inbox` — see what's
  waiting.
- PA: `governance_tool action=decisions_stats` — see
  what's been decided lately.
- PA: `governance_tool action=triage_batch` — bulk
  promote TRIAGE → ACTIVE.
