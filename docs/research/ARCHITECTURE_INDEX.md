---
title: "Architecture Research Index — front page of Donkey Betz's engineering encyclopedia"
status: active
authority: navigation
session_added: 1268
last_verified: 2026-06-30
companion_anchors:
  - docs/PLATFORM_INVENTORY.md       # runtime anchor (counts source)
  - docs/PLATFORM_WHAT_IT_IS.md      # narrative anchor (glossary)
  - docs/EMPLOYEE_OS_PRIMITIVES.md   # canonical primitives + anti-duplication
  - docs/00-START-HERE/DOC_LIFECYCLE.md  # governs the corpus itself
  - docs/KNOWLEDGE_PIPELINE.md       # runtime flow map
  - docs/AUDIT_FINDINGS.md           # canonical Celery deferred list
verifier_loop: |
  Inventoried docs/research/ at 2026-06-30. Three docs present
  (all S1268). Re-read each frontmatter before classifying. After
  drafting, ran one self-verifier-loop pass looking for missing
  docs, duplicate classifications, incorrect dependency ordering,
  inconsistent statuses, and discoverability gaps — adjustments
  folded in. This index will need an update whenever the next
  research doc lands (see §10 maintenance rules).
owner: claude (drafted S1268)
---

# Architecture Research Index

> **What this is.** The front page of Donkey Betz's engineering
> encyclopedia. A Staff Engineer joining the project six months
> from now should read this document **first** — before opening
> any code, before reading CLAUDE.md, before touching a runtime
> file. It tells them what architectural research exists, why it
> exists, what order to read it in, and what decisions should
> never be made before reading specific documents.
>
> **What this is not.** A markdown link list. A taxonomy of every
> file under `docs/`. A historical archive. The wider `docs/`
> corpus has its own lifecycle (see
> `docs/00-START-HERE/DOC_LIFECYCLE.md`); this index governs the
> **research library specifically** — the docs that capture
> architectural reasoning *before* implementation.

---

## 0. Philosophy — why a research library exists

Before any system on this platform gets built or rebuilt, four
disciplines apply, in order:

1. **Research first.** Open-ended questions get a doc, not a
   sprint plan. The doc captures evidence with file:line cites
   and explicit unknowns; nothing is invented.
2. **Inventory before design.** Before you propose a primitive,
   you have to know what primitives already exist. The platform
   has **585 models**, **83 agents**, **113 PA tool schemas**,
   **91 enabled beat tasks** (see `docs/PLATFORM_INVENTORY.md`).
   Anything you "design" without that count in front of you is
   likely either re-inventing or violating
   `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 (the anti-duplication
   matrix).
3. **Reuse before invention.** If an existing primitive does
   80% of the job, the right move is a wrapper, not a new model.
   Every "new model" instinct has cost an operator hour before;
   the names of those hours live in
   `EMPLOYEE_OS_PRIMITIVES.md` §2.
4. **Implementation last.** Once research + inventory + reuse
   are documented and reviewed, only then does code follow.
   PRs reference the research that justified them; the research
   exists to make the PR small.

These four disciplines map to the four document types you will
find in this library: **Audit**, **Inventory**, **Sketch**,
**Decision Record**. The first three precede code; the fourth
documents what the team decided once code is imminent.

**The verifier loop is the load-bearing rule.** Every research
doc in this library is grounded in direct file reads (Grep,
Read, ORM probes) — never recall, never assumption. When a
sub-agent produces evidence, the parent agent re-verifies a
sample by directly reading the cited file:line before
synthesizing. Rigby (the platform's PA / co-author) gets an
independent SIGN review on every doc before it's considered
publishable. Verdicts are **SIGN-clean**, **SIGN-with-edits**,
or **NEEDS-MORE**; edits are folded and the verifier_loop
frontmatter field is updated.

---

## 1. Current Architecture Research Library

The library has **three documents today**, all produced in
Session 1268. They build on each other. Read them in the order
listed here unless you have a specific goal (see §2 for goal-
based reading paths).

### 1.1 `employee_os_communication_substrate_audit.md`

- **Title.** Employee OS Communication Substrate — Audit
- **Purpose.** Inventory every communication / collaboration
  primitive the platform already ships, classify each one for
  reuse, and identify the failure classes any future
  inter-employee protocol would inherit.
- **Status.** Draft → Active (SIGN-clean from Rigby S1268
  conversation `pa-01e90a1d36f54880`).
- **Research type.** Inventory + Architecture Audit + Failure
  Analysis (composite).
- **Primary questions answered.**
  - What communication substrates exist today?
  - Which are safe / wrappable / off-limits for reuse?
  - What's the receipt contract on Celery-dispatched tools?
  - What's the silent-failure history Employee OS would
    inherit?
- **Dependencies.** `PLATFORM_INVENTORY.md` (runtime
  anchor), `EMPLOYEE_OS_PRIMITIVES.md` (§2 anti-duplication
  matrix), `topics/employee-os.md`,
  `topics/agent-system.md`, `topics/personal-assistant.md`,
  `handoffs/SESSION_1267_*.md`.
- **Recommended next reads.** §1.2 (protocol sketch), then
  §1.3 (collaboration patterns).
- **Overall importance.** Foundational. Anything that touches
  inter-employee or inter-agent comms needs this read first.

### 1.2 `employee_os_communication_protocol_sketch.md`

- **Title.** Employee OS Comms Protocol Sketch — Platform
  Auditor → Chief of Staff
- **Purpose.** Take the substrate audit's `SAFE TO REUSE`
  primitives and scope the *first* concrete inter-employee
  write path. Reuse-only — explicit "do not enable
  `messaging_tool.send_message`" + explicit "no new model."
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; two substantive edits folded — L3 helper-side dedupe
  + cadence expires_at default; two clarifications folded).
- **Research type.** Design Research / Protocol Sketch (not a
  decision record — no implementation greenlight).
- **Primary questions answered.**
  - What does an inter-employee notice look like as a bounded
    DM on existing `MessageThread` + `DirectMessage`
    primitives?
  - How does it thread without polluting the existing
    per-(employee, job) shift-report channels?
  - What's the dedupe contract (helper-side L1/L2/L3,
    caller-side defense-in-depth)?
  - What stays out of scope for v0 (HumanAttentionItem
    spawning, reply lane, fan-out, cross-fleet)?
- **Dependencies.** §1.1 (substrate audit must be read
  first); `EMPLOYEE_OS_PRIMITIVES.md`;
  `handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md`.
- **Recommended next reads.** §1.3 (the wider collaboration
  audit Rigby asked for as the next-mission frame).
- **Overall importance.** High for anyone scoping the first
  cross-employee write surface. Lower for anyone whose work
  doesn't touch inter-employee messaging.

### 1.3 `employee_os_collaboration_patterns.md`

- **Title.** Employee OS Collaboration Patterns — Platform-
  Wide Audit
- **Purpose.** Step back from "how do employees communicate"
  to "how do autonomous components *already* collaborate
  across the platform?" — so any future Employee OS work
  reuses existing collaboration mechanisms rather than
  reinventing them.
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; one substantive correction folded — MissionRunner
  `verdict_issued` event is conditional on
  `auto_emit_verdict=True`, not guaranteed; one architectural
  blind-spot note added on canonical idempotency key across
  the two orthogonal orchestration paths).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite).
- **Primary questions answered.**
  - Q1–Q8 from the mission spec, answered explicitly in the
    doc.
  - What are the eleven distinct collaboration substrates
    already in production?
  - Which 33 primitives are SAFE to reuse, which 10 need
    wrappers, which 4 should not be reused, and which 5 are
    UNKNOWN?
  - What 29 documented failure modes does any future
    collaboration design inherit (12 new beyond the substrate
    audit's baseline)?
  - What is the canonical foundation for future Employee OS
    collaboration? (MissionRunner + OpsRun + OpsRunEvent +
    AgentFollowupSubscription + `post_shift_report`-style
    helpers.)
- **Dependencies.** §1.1 + §1.2 (both prior research docs);
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md`;
  `topics/employee-os.md`, `topics/celery-workers.md`,
  `topics/agent-system.md`, `topics/initiative-pipeline.md`.
- **Recommended next reads.** Once this lands, the
  recommended **next research mission** is Governance +
  Authority Evolution (see §5 below). The next *design* work
  is the protocol sketch's v0 PR (assuming Chris greenlights
  it).
- **Overall importance.** Mandatory for anyone touching
  collaboration, orchestration, scheduling, mission
  coordination, or autonomy escalation.

### 1.4 Index doc (this file)

- **Title.** Architecture Research Index
- **Purpose.** Navigation. This doc.
- **Status.** Active (first edition, S1268).
- **Research type.** Navigation / Decision Record (light).
- **Maintenance rule.** Every future research doc must update
  this index — see §10.

---

## 2. Recommended Reading Paths

Engineers join with different goals. Each path lists docs in
order; bracketed numbers point back to §1.

### Path A — "I need to understand Employee OS"

1. `CLAUDE.md` (Quick Start + Working with Rigby section)
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives +
   anti-duplication matrix)
3. `docs/topics/employee-os.md` (subsystem narrative)
4. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1]
5. `docs/research/employee_os_collaboration_patterns.md`
   [§1.3]
6. Latest handoff: `docs/handoffs/SESSION_1267_*.md`

You will now know: the four current employees, the lifecycle
primitives that compose them, the comms surfaces they expose,
and the collaboration substrates available across the wider
platform.

### Path B — "I want to design new employees"

1. Path A above (in full).
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` §5 ("Quick-Start for
   Adding a New Employee").
3. `docs/research/employee_os_collaboration_patterns.md` §8
   (reuse classification — esp. SAFE rows) and §9
   (anti-duplication mapping).
4. `core/employees/jobs.py:74-162` (frozen `AIEmployee` +
   `JobContract` dataclass shapes) — read code, not docs.
5. `core/employees/mission_runner.py:1-230` (module docstring
   + lifecycle).
6. `core/employees/comms_docs_manager.py:1-122` (canonical
   per-employee comms wrapper pattern).

**Hard rule before opening a PR for Employee #5:** read
`EMPLOYEE_OS_PRIMITIVES.md` §2 + §4 in full. The 23-row "do
NOT build" matrix and the 7 explicit warnings exist because
each one cost real time before.

### Path C — "I want to understand governance"

1. `docs/EMPLOYEE_OS_PRIMITIVES.md` row 17 (GovernanceState +
   KillSwitch).
2. `docs/research/employee_os_collaboration_patterns.md` §2
   rows 55-56 + §10 Q11 (open question on authority
   enforcement).
3. `core/models_governance.py:17-189` (GovernanceState +
   KillSwitch model definitions).
4. `core/employees/mission_runner.py:258-275` (authority
   warn-mode constants + S1264 design).
5. `docs/handoffs/SESSION_1264_*.md` (authority
   contract observation design + Rigby SIGN edits).

**Gap to know:** there is no dedicated research doc on
governance/authority evolution yet. Per §1.3's §11
recommendation, that's the next research mission. Until it
exists, `mission_runner.py:258-275` is the authoritative
contract; warn-mode never blocks.

### Path D — "I want to build new communication"

1. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1] — esp. §8 reuse classifications and §7 known risks.
2. `docs/research/employee_os_communication_protocol_sketch.md`
   [§1.2] — concrete pattern to mirror.
3. `core/employees/comms.py:228-367`
   (`post_shift_report` — canonical bounded-comms helper).
4. `core/employees/comms_docs_manager.py:1-122` (thin
   wrapper pattern).
5. `core/models_messaging.py:21-141`
   (MessageThread / ThreadParticipant / DirectMessage shapes).

**Hard rule:** do NOT propose enabling
`messaging_tool.send_message` in any design. It is OFF by
design (per `EMPLOYEE_OS_PRIMITIVES.md` §4.7 and
substrate audit §8 DO-NOT-REUSE row). Free-form LLM outbound
is the wrong shape for structured comms; bounded helpers in
`core/employees/comms*.py` are the right shape.

### Path E — "I need to understand orchestration"

1. `docs/research/employee_os_collaboration_patterns.md` §3
   (12 collaboration flow diagrams) + §4 (delegation
   mechanism comparison table).
2. `docs/topics/celery-workers.md` (worker / queue topology).
3. `core/employees/mission_runner.py:1-1758` (one orchestrator).
4. `ai_core/agents/hybrid_executor.py:244,351` (the other
   orchestrator — Celery chain + group).
5. `core/agents/workflow_orchestration_agent.py:47,302`
   (ThreadPoolExecutor fan-out variant).

**Big finding to internalize:** there are **two orthogonal
durable orchestration paths** (Celery chain in
`hybrid_executor.py` vs. MissionRunner step loop in
`mission_runner.py`). They do NOT compose today. Choose one
based on durability needs; do not mix.

### Path F — "I want to understand autonomous execution"

1. `docs/topics/spider-network.md` + `docs/topics/initiative-pipeline.md`.
2. `docs/research/employee_os_collaboration_patterns.md` §3.6
   (Spider → Signal → Trigger → Work flow) and §3.7 (Spider →
   EventBus → Consumer Group flow).
3. `core/services/signal_aggregation_service.py:33-1161`
   (entity-token clustering; pattern detection).
4. `core/services/event_bus.py:21-728` (8 streams + DLQ).
5. `core/services/body_coordinator.py:110-300+` (9 body
   systems autonomic reflex layer).

**Gap to know:** autonomous→initiative auto-creation
(AutoTopic → Initiative) is UNCERTAIN per collaboration audit
§10 Q2 — no creation task traced. Treat as not-yet-wired.

### Path G — "I need to understand platform reliability"

1. `docs/research/employee_os_collaboration_patterns.md` §5
   (mission coordination — what survives process / Redis / DB
   restarts) and §7 (29 failure modes).
2. `docs/research/employee_os_communication_substrate_audit.md`
   §7 (12 incident classes).
3. `docs/AUDIT_FINDINGS.md` (canonical Celery deferred list,
   S1115 multi-batch audit).
4. `docs/topics/celery-workers.md` (queue + worker
   architecture).
5. `core/services/anthropic_client_factory.py:38-50` +
   `core/services/openai_client_factory.py:68-72`
   (centralized timeout contract — must use these factories).

**Hard rule:** any new LLM client call site MUST go through
the factory (per memory rules
`feedback_anthropic_client_factory` and
`feedback_openai_client_factory`). Bare `Anthropic()` /
`OpenAI()` defaults to 600s timeout, causing the zombie-thread
class documented in collaboration audit §7 row 17.

---

## 3. Architecture Domains

The platform is partitioned into ~17 domains below. For each,
the table lists what research exists (in this library), what
is still missing, and current maturity.

| Domain | Existing research | Canonical anchors | Missing research | Maturity |
|---|---|---|---|---|
| **Employee OS — core** | §1.1, §1.2, §1.3 | EMPLOYEE_OS_PRIMITIVES.md; topics/employee-os.md | (none today; covered by §1.1 + §1.3) | **High** — 4 production employees, fully audited |
| **Mission System (MissionRunner)** | §1.3 (§2 row 19, §3.9, §6) | mission_runner.py (1758 lines); jobs.py:74-162 | Dedicated MissionRunner architecture doc (could lift from §1.3's flow + reuse rows) | **High** — production for 4 employees |
| **Governance** | §1.3 (§2 rows 55-56) | models_governance.py | **Governance Evolution research doc** | **Medium** — primitives exist; cross-employee scope untested |
| **Authority** | §1.3 (§2 row 26 + §10 Q11) | mission_runner.py:258-275 (S1264 warn-mode) | **Authority Evolution research doc** (warn → enforce; symbol mapping) | **Low** — warn-mode only; no enforcement |
| **Communication (employee comms)** | §1.1 (full); §1.2 (specific path) | comms.py, comms_docs_manager.py, EMPLOYEE_OS_PRIMITIVES.md §4.7 | Inter-employee reply lane (§1.3 F4); cross-fleet messaging | **Medium** — outbound shift reports work; inter-employee design sketched but not built |
| **Messaging (raw substrate)** | §1.1 (§2 rows 35-37); §1.3 (§2 row 36) | models_messaging.py:21-141 | inbox UI semantics for `thread_kind='inter_employee_notice'` (frontend ticket, not research) | **High** — substrate is production |
| **Memory (employee / agent)** | (none in research library) | core/models_agent_memory.py | **Memory Architecture research doc** — esp. how do employees remember each other's past verdicts? | **Low / UNKNOWN** — no research yet |
| **Decision Making** | §1.3 (§2 rows 38-42 + §3.10) | models_human_interface.py; models_orchestration.py | Decision precedent + multi-stakeholder approvals (§1.3 §10 Q6) | **Medium** — HAI lifecycle is robust; collaborative decisions absent |
| **Human Interface** | §1.3 (§2 rows 38-42, 58-59) | HumanAttentionItem + HumanFeedbackRecord + HumanPreference; views_inbox.py | DM-arrived WebSocket event surfacing (frontend ticket) | **High** — HAI lifecycle service production |
| **Automation (workflow autopilot)** | §1.3 (§2 row 47 — `WorkspaceTrigger`) | models_skin_layer.py | `workspace_autopilot_tick` location UNKNOWN (§1.3 §10 Q1); needs trace | **Medium / UNKNOWN** |
| **Agents (BaseAgent + AGENT_MAP)** | §1.1 (§3); §1.3 (§2 rows 1-9) | core/agent_router.py; core/agents/base_agent.py; topics/agent-system.md | (well-covered) | **High** — 83 agents production |
| **Spiders** | §1.3 (§3.6 + §3.7) | ai_core/spiders/; topics/spider-network.md | (well-covered) | **High** — 80 spiders + 1.14M item hashes |
| **Signal Processing** | §1.3 (§2 rows 48-50) | signal_aggregation_service.py; content_scoring_service.py | AutoTopic → Initiative wiring (§1.3 §10 Q2) | **Medium** — clustering production; downstream uncertain |
| **Workflows (Initiative pipeline)** | §1.3 (§2 rows 43-44 + §3.8) | models_document_registry.py; topics/initiative-pipeline.md; DREAM_INITIATIVE_WORKFLOW.md | (Initiative is documented; cross-employee composition is not) | **High** (pipeline) / **Medium** (composition) |
| **Scheduling (beat)** | §1.3 (§3.11) + 5-agent scheduling sweep evidence | core/celery.py:37-797; topics/celery-workers.md; AUDIT_FINDINGS.md §12 | **Cross-employee scheduling research doc** | **Medium** — beat tasks documented; cross-employee handoffs absent |
| **Observability** | §1.3 (§6 evidence scoring) | OpsRunEvent + AgentExecution + ToolCallRecord + LLMCallEvent + CeleryTaskEvent | (well-covered) | **High** — five audit tables compose |
| **Telemetry (LLM costs)** | §1.3 (§2 rows 8, 63-64) | models_llm_telemetry.py | (well-covered) | **High** — cleanup watchdog + total-request bound |
| **Reliability** | §1.3 (§5 + §7) | anthropic_client_factory.py; openai_client_factory.py; cleanup beat tasks | (well-covered) | **High** — multi-layer defense |
| **Infrastructure** | (none in research library — runtime evidence only) | topics/infrastructure.md; topics/celery-workers.md; Procfile | Redis broker persistence config — UNKNOWN (§1.3 §10 Q5) | **Medium / UNKNOWN** |
| **Knowledge Pipeline** | (none in research library) | docs/KNOWLEDGE_PIPELINE.md | (covered by KNOWLEDGE_PIPELINE.md narrative) | **High** — production pipeline |

---

## 4. Architecture Dependency Graph

The library's documents build on each other in a specific
order. Reading them out of order is technically possible but
each downstream doc assumes its upstream context.

```
                ┌─────────────────────────────────────────┐
                │  PLATFORM_INVENTORY.md (runtime anchor) │
                │  PLATFORM_WHAT_IT_IS.md (narrative)     │
                └────────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │  EMPLOYEE_OS_PRIMITIVES.md          │
                    │  (canonical primitives + §2 anti-   │
                    │   duplication matrix)               │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  research/employee_os_communication_substrate_  │
        │  audit.md                                       │
        │  (Inventory of comms primitives + reuse class)  │
        └───────────────────┬─────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            ▼                                ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  research/employee_os_    │    │  research/employee_os_         │
│  communication_protocol_  │    │  collaboration_patterns.md     │
│  sketch.md                │    │  (Platform-wide inventory of   │
│  (One concrete path:      │    │  collaboration; 64-row table;  │
│  Auditor → Chief of Staff)│    │  11 substrates; 29 failures)   │
└──────────┬────────────────┘    └────────────────┬───────────────┘
           │                                      │
           ▼                                      ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  [Future: v0 PR for the   │    │  [Future research mission]     │
│  protocol — gated by      │    │  Governance + Authority        │
│  Chris's greenlight]      │    │  Evolution (recommended next)  │
└───────────────────────────┘    └────────────────┬───────────────┘
                                                  │
                                                  ▼
                                ┌──────────────────────────────────┐
                                │  [Further future research —      │
                                │  see §9 roadmap]                 │
                                │  Memory · Trust Propagation ·    │
                                │  Cross-Employee Scheduling ·     │
                                │  Mission Composition · …         │
                                └──────────────────────────────────┘
```

**Reading the graph.** The two prior anchors at the top
(`PLATFORM_INVENTORY` + `PLATFORM_WHAT_IT_IS`) and the
primitives doc (`EMPLOYEE_OS_PRIMITIVES`) are *not* in the
research library but are **load-bearing context** for
everything in it. Any research doc that doesn't honor those
three is broken at the root.

The protocol sketch (§1.2) and the collaboration patterns
audit (§1.3) are siblings, both downstream of the substrate
audit (§1.1). They were written in the same session
(S1268) — the sketch came first, the wider audit came
second once Rigby's review of the sketch surfaced the broader
"how does collaboration work everywhere" question.

**Convention.** Every new research doc declares its parents
via the `companion_docs` frontmatter field. The dependency
graph above is reconstructable from those declarations.

---

## 5. Research Gaps

The library is **young** — 3 docs, all S1268. There are real
gaps. Below are the ones that have surfaced explicitly during
S1268 research, with priority and rationale. Each is a
*research* gap — i.e., something that should get its own
research doc before it gets implemented.

### 5.1 Governance + Authority Evolution (HIGH — recommended next)

- **Why it matters.** S1264 shipped `authority_contract_observed`
  in warn-mode only. Per `mission_runner.py:264-894`, the event
  emits shape evidence but **never blocks**. Every research doc
  in this library has hit "but warn-mode doesn't enforce" as a
  boundary. Cross-employee dispatch is the first surface where
  the boundary actually matters.
- **Priority.** P0 next research mission per §1.3's §11
  recommendation. Rigby SIGN-clean on that recommendation.
- **Dependencies.** §1.3 (esp. §10 Q11), `mission_runner.py:258-275`,
  `docs/handoffs/SESSION_1264_*.md`,
  `core/employees/jobs.py:489-505` (Platform Auditor
  authority dict shape).
- **Expected outcome.** A research doc that scopes the
  symbol-mapping work needed to take authority strings (like
  `"recommend_remediations"`) and bind them to runtime symbols
  (tool names, FK methods). Plus trust-propagation primitives
  (when Employee A trusts Employee B's verdict, what's the
  contract?). Plus boundary cases (what happens when an
  authority contract changes mid-run?).

### 5.2 Memory Architecture (MEDIUM)

- **Why it matters.** Employees do not "remember" each other's
  past verdicts in their reasoning today. Bug Triage *queries*
  OpsRun rows from other employees (read-only composition), but
  there is no synthesized memory layer — no "last week the
  Auditor flagged this same finding" awareness inside the
  reasoning context. Derived from §1.3 §1 Finding F4 (no
  in-platform A→A reply contract today) — memory naturally
  falls out as a sub-question under trust propagation once
  inter-employee read-of-other-employee semantics exist.
- **Priority.** P1. Probably falls out of the Governance + Authority
  research naturally — but if it doesn't, it deserves its own
  pass.
- **Dependencies.** Governance research (above);
  `core/models_agent_memory.py` (current per-agent memory shape).
- **Expected outcome.** A doc that maps the existing
  `AgentMemory` / `AgentLearning` / `LearningInsight` /
  `SharedKnowledge` primitives, identifies whether they're
  shared-readable across employees, and proposes (research-only)
  what a "cross-employee episodic memory" layer would reuse vs.
  invent.

### 5.3 Cross-Employee Scheduling (MEDIUM)

- **Why it matters.** Per §1.3 §1 Finding F4 and Q8, the
  minimum missing runtime surface for inter-employee delegation
  is **a durable "subscribe-to-(employee, verdict)" primitive**
  that routes verdicts to a target employee's *next mission's
  preflight*. Today's AgentFollowupSubscription handles
  conversation-scoped wakeups, not mission-to-mission handoffs.
- **Priority.** P1 — depends on Governance research closing
  first because authority semantics gate the dispatch.
- **Dependencies.** §1.2 (protocol sketch), §1.3 (§2 rows 27-29).
- **Expected outcome.** A research doc that scopes whether the
  primitive is (a) a new model, (b) an extension of
  `AgentFollowupSubscription`, or (c) a pure read-side query
  pattern. Not a design — just the scope of the smallest
  missing piece.

### 5.4 Mission Composition (MEDIUM)

- **Why it matters.** Per Rigby S1268 review architectural-blind-
  spot note (folded into §1.3 §10 Q12), the two durable
  orchestration paths (Celery chain vs. MissionRunner step
  loop) don't compose. When a future mission needs to chain
  Celery tasks across employees, the canonical idempotency key
  across substrates is an open question — calendar-date scope
  (MissionRunner) vs. task_id (Celery) vs. event_id (EventBus)
  vs. UUID (AgentExecution) don't reconcile.
- **Priority.** P1 — touches Reliability + Observability if
  done poorly.
- **Dependencies.** §1.3 (Q12), `topics/celery-workers.md`.
- **Expected outcome.** A doc that names the canonical
  idempotency key (or proves none exists and what would have to
  give).

### 5.5 Observability / Failure Recovery (LOW — already strong)

- **Why it matters.** Observability is well-covered by §1.3 §6
  (evidence-and-auditability scoring). Failure recovery is
  well-covered by §1.3 §7 (29 documented failure modes).
- **Priority.** P2. Most failure classes are already
  documented with mitigations. A dedicated doc would be a
  consolidation pass, not new research.
- **Dependencies.** §1.3 §6 + §7; `docs/AUDIT_FINDINGS.md`.
- **Expected outcome.** Optional consolidated "failure
  taxonomy" doc that pulls the §7 incidents into a single
  reference. Not blocking.

### 5.6 Security Model / Permission Model (UNKNOWN — needs scoping)

- **Why it matters.** Service-token auth is referenced
  (`core/auth_middleware.py:113` only documents
  `PA_DB_HEALTH_RPC_TOKEN`), but the full scope of
  dispatch surfaces requiring auth is UNKNOWN per substrate
  audit §9 Q3. Cross-fleet messaging requires this answered.
- **Priority.** P2 — only blocking if a future research
  mission wants to cross fleet boundaries.
- **Dependencies.** TBD; needs an initial scoping pass to
  even know what to audit.
- **Expected outcome.** First a *scoping* doc (one page) to
  identify which surfaces need auth; then full research if the
  surface is non-trivial.

### 5.7 Configuration Architecture (UNKNOWN — possibly out of scope)

- **Why it matters.** Feature flags
  (`RIGBY_EVENT_INTAKE_ENABLED`, `MESSAGING_TOOL_ALLOW_SEND`,
  `CTO_DIAGNOSTIC_ENABLED`, `COO_DIAGNOSTIC_ENABLED`) are
  scattered. There may be an implicit convention but no
  documented one.
- **Priority.** P3 — UNKNOWN whether this needs research or
  just a one-page note in
  `docs/00-START-HERE/DOC_LIFECYCLE.md`.
- **Dependencies.** TBD.
- **Expected outcome.** Either a one-page convention note OR
  a scoping doc.

### 5.8 Knowledge Graph (UNKNOWN — not raised yet)

- **Why it matters.** Mentioned in the mission spec as a
  candidate. Not raised in any prior research. No production
  evidence found for a knowledge-graph layer today.
- **Priority.** P? — premature. Surface only if a future
  research mission has a specific use case for it.

---

## 6. Research Principles

The principles below are extracted from the three S1268 docs
and the verifier-loop pattern they all share. They are not
opinion — they are what *worked* on the first three docs,
verified by Rigby's SIGN reviews.

1. **Evidence before opinion.** Every claim in a research doc
   carries a file:line cite or is marked UNKNOWN. There is no
   third option. "I think the system does X" without a cite is
   forbidden.
2. **Inventory before implementation.** Before you can propose
   a primitive, you must list the existing primitives that
   already cover the same surface. Anti-duplication is load-
   bearing per `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1.
3. **Reuse before invention.** "Wrapper" beats "new model"
   beats "new admin UI." If a wrapper fits, the new model
   doesn't ship.
4. **Architecture before code.** Research docs exist to make
   PRs small. If a PR is small because the research is solid,
   the team has won.
5. **Document uncertainty.** When evidence is thin, mark
   UNKNOWN. Don't guess; don't fill gaps with plausible
   inference. The UNKNOWN list in §10 of each doc is the
   honest seed for the next research mission.
6. **Never silently assume.** When two doc-claims disagree
   (substrate audit said 6 EventBus streams; runtime says 8),
   the runtime wins per `DOC_LIFECYCLE.md` §2c. Flag the drift
   in the new doc; do not silently inherit the wrong number.
7. **Use verifier loops.** The doc author re-reads
   sub-agent cites by direct Grep/Read before synthesizing.
   No exceptions.
8. **Rigby independent review before architectural
   decisions.** Every research doc gets routed to Rigby via
   `tools/pa_local.sh` on the S1268 pinned conversation. The
   verdict (SIGN-clean / SIGN-with-edits / NEEDS-MORE) is
   recorded in the `verifier_loop` frontmatter field. Edits
   are folded before the doc is considered Active.
9. **Frontmatter declares lineage.** Every research doc lists
   its `companion_docs` so the dependency graph in §4 is
   reconstructable. If you don't declare your parents, you're
   not ready to publish.
10. **Authority is the only "must change" boundary.**
    Research-only missions don't touch runtime. The single
    exception: if mid-doc you discover that a prior research
    claim is wrong, the doc surfaces it (drift call) but does
    not patch the prior doc — patching happens in a separate
    pass with its own review.

---

## 7. Decision Matrix — "If you're about to work on…"

A pre-PR sanity gate. Find the row that matches your work;
read the documents in column 2 first. Skipping the read is the
fastest way to land a PR that violates the anti-duplication
matrix or re-introduces a closed failure class.

| About to work on… | Read these first |
|---|---|
| **Employee communication (anything)** | §1.1 + §1.2 + `EMPLOYEE_OS_PRIMITIVES.md` §4.7 (messaging_tool send guard) |
| **A new AI Employee** | Path B in full + `EMPLOYEE_OS_PRIMITIVES.md` §5 quick-start |
| **MissionRunner internals** | §1.3 §2 rows 17-23 + `mission_runner.py:1-230` + S1267 handoff |
| **`MissionRunnerConfig.auto_emit_verdict` semantics** | §1.3 Executive Summary item 6 (corrected by Rigby S1268 SIGN-with-edits) + §1.3 §2 row 19 + §1.3 §7 row 29 (protocol invariant change) + `core/employees/mission_runner.py:1127-1145` |
| **Governance flags or modes** | §1.3 §2 rows 55-56 + Path C |
| **Authority enforcement (vs. observation)** | §1.3 §10 Q11 + §1.3 §11 (recommendation for Governance + Authority Evolution next research) + S1264 handoff |
| **Adding any new tool to PA** | §1.1 §4.4 (handler/schema delta gotcha) + memory rule `feedback_llm_autofills_boolean_params_with_false.md` |
| **`messaging_tool` (any change)** | `EMPLOYEE_OS_PRIMITIVES.md` §4.7 + §1.1 §8 DO-NOT-REUSE row + `td_handlers_core.py:3693-3711` |
| **Mission scheduling (any new beat)** | Path E + `topics/celery-workers.md` + `EMPLOYEE_OS_PRIMITIVES.md` §4.6 (app.conf.imports requirement) |
| **Observability or audit chain** | §1.3 §6 (evidence-and-auditability scoring) + §1.3 §2 rows 7-9 |
| **Reliability / timeout / retry policy** | Path G + §1.3 §7 (rows 10, 17, 18, 19 esp.) |
| **Escalation surfaces** | §1.3 §3.5 (HAI creators) + §1.3 §3.9 (MissionRunner escalation) + §1.2 §8.1 (Auditor has no HAI creation authority) |
| **Human attention (HAI lifecycle)** | §1.3 §2 rows 38-41 + §3.5 + `core/services/human_attention_lifecycle.py:36-728` |
| **Deliverable creation / status flips** | Memory rules `feedback_deliverable_tool_use_append_for_large_payloads`, `feedback_deliverable_status_via_content_complete`, `feedback_deliverable_create_defaults_to_completed` + §1.1 §7.8 |
| **Spider → downstream work chains** | Path F + §1.3 §3.6 + §3.7 |
| **Anything that says "new model"** | `EMPLOYEE_OS_PRIMITIVES.md` §2 (anti-duplication matrix) + §1.3 §9 (anti-duplication analysis). If a row matches, you are not adding a model. |

---

## 8. Architecture Timeline

The library is young. Here is the actual chronology with
influence callouts.

| When | Doc | What it added | Influenced |
|---|---|---|---|
| **S1268 P0 #1** (2026-06-30) | `employee_os_communication_substrate_audit.md` (§1.1) | First inventory of comms primitives between AI employees. 36-row table. Reuse classifications. 12 incident-class failure history. Rigby SIGN-clean. | Made §1.2 possible — the protocol sketch reused the SAFE rows directly. Also stated EventBus had "6 named streams" at line 135 — runtime is **8** per `event_bus.py:21-30`. The drift was caught in §1.3 §12 and Rigby independently corroborated it. The substrate audit text itself has **not** been amended (research-only constraint per S1268); the drift is flagged in §1.3 §12 (cross-reference + documentation drift table) and propagated forward as the canonical value. |
| **S1268 P0 #2** (2026-06-30) | `employee_os_communication_protocol_sketch.md` (§1.2) | First concrete inter-employee write path scoped (Platform Auditor → Chief of Staff). Helper signature, metadata envelope, threading model, 3-layer dedupe, terminal-gate, expires_at freshness boundary. Rigby SIGN-with-edits — 2 substantive edits folded (L3 helper-side dedupe + cadence Option A default). | Surfaced the question "but how does collaboration work *everywhere else* on the platform?" — which became §1.3. |
| **S1268 P0 #3** (2026-06-30) | `employee_os_collaboration_patterns.md` (§1.3) | Platform-wide audit. 64-row primitive inventory. 11 distinct collaboration substrates. 12 flow diagrams. 29 documented failure modes (12 new). Q1-Q8 answered. Rigby SIGN-with-edits — 1 substantive correction folded (MissionRunner verdict event is conditional, not guaranteed) + 1 architectural blind-spot note added (canonical idempotency key across orchestration paths). | Set the recommendation for the next research mission (Governance + Authority Evolution). Surfaced gaps that become §5.1–§5.7. |
| **S1268 P0 #4** (2026-06-30) | `ARCHITECTURE_INDEX.md` (this doc) | The first navigation / index doc for the research library. Establishes the corpus's identity, dependency graph, and maintenance rules. | Will be cited by every future research doc's `companion_docs`. |

**Pattern observation.** All four docs are S1268. The library
started in a single session because that was the session where
the platform's growth crossed the threshold at which "where
should I read about X?" became a load-bearing question. The
library's *next* growth event is the Governance + Authority
Evolution doc; until that lands, this index is the front door.

---

## 9. Future Research Roadmap

Not a design. Not a build plan. A recommended *research*
ordering to minimize architectural uncertainty.

The ordering rule: each research mission unlocks the next.
Skipping a dependency means the downstream doc has to invent
context it should have inherited.

```
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1 — Governance + Authority Evolution                     │
│  (recommended next per §1.3 §11)                                │
│                                                                  │
│  Scope: symbol mapping for JobContract.authority, warn→enforce  │
│  prerequisites, trust-propagation primitives, contract-change   │
│  mid-run semantics. Resolves §1.3 §10 Q11.                      │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  STAGE 2a       │  │  STAGE 2b       │  │  STAGE 2c       │
│  Cross-Employee │  │  Mission        │  │  Memory         │
│  Scheduling     │  │  Composition    │  │  Architecture   │
│  (§5.3)         │  │  (§5.4)         │  │  (§5.2)         │
│                 │  │                 │  │                 │
│  Minimum new    │  │  Canonical      │  │  Cross-employee │
│  surface for    │  │  idempotency    │  │  episodic       │
│  Employee A →   │  │  key across     │  │  memory shape   │
│  Employee B     │  │  orchestration  │  │                 │
│  delegation     │  │  paths          │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 3                     │
                │  Employee Delegation Design  │
                │  (DESIGN, not research —     │
                │  prerequisites must close    │
                │  first)                      │
                └──────────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 4 — Implementation    │
                │  (PRs, with research as the  │
                │  justification artifact)     │
                └──────────────────────────────┘

Lateral research that does not block the main chain:

  • Security / Permission scoping (§5.6) — if cross-fleet
    surfaces enter scope.
  • Configuration Architecture note (§5.7) — when feature-flag
    growth becomes a documentation problem.
  • Observability consolidation (§5.5) — optional; no blocking
    downstream.
  • Knowledge Graph scoping (§5.8) — only if a use case
    materializes.
```

**Pacing note.** All Stage 1 + 2 work is research-only — no
PRs, no models. Stage 3 is the first design-with-PR-intent
mission. Stage 4 is implementation. The discipline that holds
this together is the verifier loop + Rigby SIGN review on
every transition.

---

## 10. Maintenance Rules

This index must evolve in lockstep with the library. The
rules below apply whenever any change happens.

### 10.1 When a new research doc is added

Within the same PR (or same session if no PR yet):

1. **Add a row to §1.** With Title / Purpose / Status / Type /
   Primary questions / Dependencies / Recommended next reads /
   Importance.
2. **Add the doc to §4 dependency graph.** Show its parents
   (via `companion_docs`) and where it sits in the lineage.
3. **Update §2 reading paths.** If the new doc belongs in
   Path A-G (or a new path), add it.
4. **Update §3 domain map.** Move the relevant domain row's
   "Missing research" → "Existing research" (or update
   maturity).
5. **Update §5 gaps.** If the new doc closes one of the named
   gaps, mark it closed with a pointer. If it surfaces new
   gaps, add them.
6. **Update §7 decision matrix.** If there's a class of work
   that should now read the new doc first, add the row.
7. **Update §8 timeline.** Append a new row chronologically.
8. **Update §9 roadmap.** If the new doc was the next stage,
   move the arrow forward.
9. **Bump `last_verified` in this doc's frontmatter.**

### 10.2 When a research doc is superseded

1. Add a pointer header at the top of the superseded doc per
   `DOC_LIFECYCLE.md` V2 conventions.
2. In §1, change Status to `Deprecated` and add a "Superseded
   by: [link]" line.
3. In §4, move the superseded doc to a "historical" footnote
   below the main graph. Do not remove from the corpus —
   per memory rule `feedback_docs_never_delete`, preservation
   matters.
4. In §7 decision matrix, replace references to the
   superseded doc with the successor.

### 10.3 When a doc's status changes (Draft → Active, Active → Canonical)

1. Update the doc's own frontmatter `status` field.
2. Update §1 row Status column.
3. If the doc has been moved to Canonical, add it to the
   appropriate canonical-anchor list in adjacent docs
   (`PLATFORM_INVENTORY.md`, `EMPLOYEE_OS_PRIMITIVES.md`,
   or this index's frontmatter `companion_anchors` if
   applicable).

### 10.4 When drift between docs is discovered

1. Per `DOC_LIFECYCLE.md` §2c: **inventory wins** on counts.
2. Add a drift call to the *newer* doc's drift section (every
   research doc has one — substrate audit cross-reference
   lives in Appendix A, collaboration patterns drift section
   lives in its §12).
3. Do **not** silently edit the older doc. If the older doc
   needs correction, that's a separate review pass with its
   own SIGN verdict.

### 10.5 When this index itself drifts from the library

If `ls docs/research/` shows a doc that isn't in §1, that's
the index's drift. Open a small fix-up PR that just updates
§1, §4, §5, §7, §8. Do not bundle it with anything else.

### 10.6 Authority on this index

This index is **authority: navigation**, not
**authority: canonical** — it points to canonical docs
without being one. If the index disagrees with a canonical
anchor (EMPLOYEE_OS_PRIMITIVES, PLATFORM_INVENTORY,
DOC_LIFECYCLE), the anchor wins; the index gets edited.

---

## Appendix A — Verifier-loop pass notes

This index was drafted from direct inventory of
`docs/research/` at 2026-06-30 (`ls` showed 3 .md files),
plus frontmatter re-reads of each, plus cross-reference
against `docs/` canonical anchors via `Glob`.

**Self-verifier pass (one round) before finalization
identified and fixed:**

- **Missing doc check.** `ls docs/research/` returns exactly
  3 files; all 3 cataloged in §1. No subdirectories. No
  hidden docs. ✓
- **Duplicate classifications.** Originally tagged §1.1 as
  pure "Inventory"; on second pass added "+ Architecture
  Audit + Failure Analysis" because §7 of that doc is
  substantively failure analysis. Same fix on §1.3. ✓
- **Dependency ordering.** First draft showed §1.2 and §1.3
  as parallel children of §1.1 in §4 graph. Re-verified
  against the actual creation order (§1.2 was written
  *before* §1.3 within the same session) and timeline §8 —
  graph is correct; chronologically §1.3 was the audit that
  surfaced the "wider question" raised by Rigby's review of
  §1.2. ✓
- **Inconsistent statuses.** First draft listed all three as
  "Active." Re-read each frontmatter and found all three are
  literally `status: draft` per their YAML. Updated §1 rows
  to "Draft → Active (SIGN-... from Rigby)" to honor both the
  frontmatter literal and the review-state reality. ✓
- **Discoverability.** Originally Path G ("platform
  reliability") didn't mention the client factories. Added
  the hard-rule callout on `anthropic_client_factory.py` /
  `openai_client_factory.py` because the memory rules
  (`feedback_anthropic_client_factory`,
  `feedback_openai_client_factory`) and the zombie-thread
  failure class (§1.3 §7 row 17) all converge on that
  enforcement. ✓
- **§3 domain map** — Memory domain originally not listed;
  added on second pass because §5.2 calls it out as a real
  research gap. Same for Knowledge Pipeline (added per
  `KNOWLEDGE_PIPELINE.md` existing as a canonical anchor
  outside the research library). ✓
- **§7 decision matrix** — first draft was missing the row
  for `MissionRunnerConfig.auto_emit_verdict`. Added on second
  pass because the protocol-invariant-change row (§1.3 §7 row
  29) was Rigby's SIGN-with-edits correction and deserves a
  decision-matrix anchor of its own.

**Status after self-verifier pass.** Publishable as v1.
Rigby independent SIGN review on this index is **not**
required per S1268 mission spec scope (the spec asks for a
verifier loop, not a Rigby pass on the index itself). If a
future session wants Rigby's read on the index, that's a fine
small follow-up.
