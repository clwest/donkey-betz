---
title: "Agents, Autonomy & Governance — narrative pilot"
status: draft (pilot for Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1 (Rigby, Session 1158)
companion_docs:
  - docs/topics/agent-system.md
  - docs/AGENTS.md
  - docs/PLATFORM_INVENTORY.md
  - docs/UDB_TRANSLATION_LAYER.md
  - docs/UDB_BEHAVIOR_LAYER.md
provenance_confidence: HIGH (anchored to topics doc + AGENTS.md + handoff filenames + PLATFORM_INVENTORY)
provenance_note: Pilot narrative — synthesizes existing topic doc, agent reference, handoff names, and platform inventory. Counts pulled from PLATFORM_INVENTORY 2026-05-25 snapshot (git HEAD d513cd7f). Session attributions trace to citations in docs/topics/agent-system.md and docs/AGENTS.md, plus the named SESSION_NNNN handoff files. Uncertainty is labelled inline.
---

# Agents, Autonomy & Governance

> Pilot narrative for the corpus-narrative program. The job of this
> doc is to let someone who has never touched the UI understand
> **what the agent system is, what was built into it over time, why
> each piece was added, and what happened as a result.** Counts come
> from `PLATFORM_INVENTORY.md` (regenerable; sole authoritative
> source). Session attributions come from the topic doc, the agent
> reference doc, and the named handoff files. Where the corpus is
> silent on outcome, this doc says so.

---

## 1. What this is

The Donkey Betz platform runs **AI agents**: long-lived Python classes
that take a task, pull in context (recent spider data, user profile,
prior knowledge, advisor wisdom), call a large-language-model with that
context, and return a structured result. They are the platform's hands
— almost everything the platform "does" (write a blog, audit a smart
contract, generate a sports prediction, draft a legal motion) goes
through one of them. The Personal Assistant (Rigby) is itself
front-of-house for the agent system; she routes most user requests to
specific agents, then either returns the result or stages it for
review.

This narrative covers three intertwined surfaces that grew together:

- **The agents themselves** — the registry, how they're routed, what
  context they receive, what tools they share.
- **Autonomy** — the scheduled and event-driven paths that let agents
  run without a user typing anything (diagnostics, daily rotations,
  desk coordinators, reflex spawners).
- **Governance** — the gates, caps, and review pipelines that exist
  to keep an autonomous agent system from drowning the platform in
  garbage outputs.

The audience is operator-grade: you should leave this doc able to
answer "what would I check if agent X stopped working", not just "what
does agent X do".

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`AGENT_MAP`** | The deterministic dictionary in `core/agent_router.py` mapping agent-name strings to agent classes. The router does no LLM inference to pick an agent — it's a dict lookup. Currently holds 83 entries (74 enabled, 8 rerouted, 1 blocked). |
| **`BaseAgent`** | The parent class every agent inherits from. Provides shared infrastructure: prompt building, knowledge retrieval, learning hooks, the tool call wrapper, health-check mode, workspace methods. The file is ~5,500 lines because most cross-cutting behavior lives here rather than being repeated per agent. |
| **`Agent` table** | The database row representation of an agent. Distinct from `AGENT_MAP`: there are 155 DB rows but only 83 code-resident classes. DB rows carry persona metadata, learning telemetry, and agent_type taxonomy; classes carry behavior. |
| **Routable vs non-routable** | A routable agent can be invoked directly by name. Non-routable agents are sub-agents or coordinators — they exist to be called from inside another agent's flow, not from the router entry. |
| **Provenance-tracked** | An agent that includes `provenance`, `publishable`, and `validation_status` in its output. Used for data-grounded agents (stock, blockchain, analysis) where freshness and source matter. |
| **Workspace-aware** | An agent that can write files into a user workspace via `BaseAgent`'s workspace methods. Twenty agents are explicitly listed in `WORKSPACE_AWARE_AGENTS` (`core/epa_handlers_tools.py`) and surfaced through `universal_agent_tool`. |
| **Context layers** | The twelve named slices of information injected into every agent execution before the LLM call (scifi, spider, learning, advisor, feedback, knowledge, workspace, docs, user, risk, platform-tools-directive, user-docs). |
| **Intelligence Desk** | A coordinator agent that fans out work to a domain-specific sub-team (Stocks: 9 agents, Sports: 5, Blockchain: 5, Narrative: 4). All four desks are on-demand only — none are on a scheduled beat. |
| **AutoSpawnerService** | The "missing-reflex" service. Decorators wrap agent entry points; when data is insufficient or stale, the spider that gathers the data is scheduled automatically before the agent runs. |
| **`ToolCallRecord`** | The audit row that captures every tool call any agent makes. `BaseAgent.__init_subclass__()` installs the wrapper at class-creation time, so no per-agent code changes are needed — every subclass inherits it. |
| **`AgentExecution`** | The row that records a single agent run (input task, output, duration, status). Distinct from `DeliberationSession`, which records multi-agent conversations. The Personal Assistant queries both. |
| **`AgentLearningService`** | The service that records every `route()` call and builds per-user, per-agent preference models in Redis, then surfaces the learned preferences back into the next execution's context. |
| **DecisionEnforcerAgent** | The "prefrontal cortex". After a multi-agent debate, this agent forces a single decision (publish / revise / kill) and forbids hedging language. Its mission is to prevent the platform from generating well-reasoned indecision. |
| **`run_market_intelligence_desk`** etc. | Celery task functions for the Intelligence Desks. They exist in `core/tasks.py` but are no longer on the beat schedule (removed in commit `a88fb8e7`, "minimal beat schedule"); to re-enable, register a `PeriodicTask`. |
| **Bounded vs unbounded task** | A bounded task specifies scope, length limit, and "do not delegate / spawn sub-tasks". An unbounded task ("analyze current market trends") tends to time out at 45 minutes. The bounded pattern was the fix for the 2025 wave of timeouts. |
| **Canary** | A small, controlled-injection test path that lets new agent behavior reach the production deliverable pipeline without going through the user-visible UI. Sessions 1092–1098 turned the canary into the standard mechanism for verifying agent reliability before a wider rollout. |

---

## 3. Milestone timeline

Each row is an arc, not a single PR. The "When" column is a session
range; "Outcome" is what changed in the platform's behavior as a
result; "Status" answers "is this still load-bearing today?".
"Pointers" lists the docs, files, or session handoffs where the
evidence sits.

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Sessions 303–400 (foundation)** | `AGENT_MAP` + `BaseAgent` architecture; knowledge pipeline (Spider → embeddings → learning bridges → `AgentKnowledgeSource` → injected into prompts) | The platform needed a way to add new agents without rewiring the router each time, and needed agents to *use* the data spiders were collecting (not re-research from scratch). | Every agent now inherits a shared spine: prompt builder injects learned knowledge automatically; new agents are added by adding a class + a dict entry. Knowledge pipeline runs end-to-end. | **Active** — still the core architecture. | `docs/AGENTS.md` §"Agent Knowledge Pipeline (Session 400)"; `docs/topics/agent-system.md`; `core/agent_router.py`; `core/agents/base_agent.py` |
| **Sessions 695, 858 (capability + personalization)** | SKIN layer — agents inherit workspace methods (can write files into a user workspace). All agents receive personalized `user` context (skills, goals, communication style, risk tolerance, betting prefs). | Agents that only produce text in a response window are scope-limited. Real value needed agents that can save artifacts to real workspaces, and that tune their output to the actual user (not a generic persona). | 20 agents wired into `WORKSPACE_AWARE_AGENTS` and reachable via `universal_agent_tool`. ContentWriter, Research, StockAnalyst, SportsOddsAnalyst gained user-tuned outputs. Workspace writes get an audit trail. | **Active** — workspace methods used in production; user-context injection is a default code path. | `docs/AGENTS.md` §"SKIN Layer Integration (Session 695)" and §"User Context Injection (Session 858)"; `core/epa_handlers_tools.py:WORKSPACE_AWARE_AGENTS` |
| **Sessions 781, 872 (voice + decision discipline)** | Role-anchored conversation voices for 22 agents in multi-agent conversations (CTOAgent = TECHNICAL ARBITER, COOAgent = OPERATIONS REALIST, etc.) with banned-phrase enforcement. DecisionEnforcerAgent ("Prefrontal Cortex"). ResearchContract / ExecutionMandate / SynthesisContract to forbid vague outputs. | Multi-agent debates were collapsing into uniform corporate-speak ("I'd push back slightly", "great point, but…") and ending without decisions. Both problems were prompt-shape problems, not model problems. | Multi-agent conversations now read as distinct voices; debates terminate on a verdict instead of an open synthesis. The contracts prevent agents from producing "research-shaped" outputs that don't actually commit to anything. | **Active** — `core/prompts/registry.py` still anchors the 22 roles; DecisionEnforcerAgent still wired into the content review pipeline. | `docs/AGENTS.md` §"Agent Conversation Voice (Session 781)"; `docs/handoffs/SESSION_781_AGENT_VOICE_FIXES.md`; `docs/topics/agent-system.md` §"Executive Function (Session 872)" |
| **Sessions 953, 970, 988, 1001–1002 (provenance & truth controls)** | Provenance tracking on 26+ agents (`generated_at`, `inputs_used`, `freshness_window`, `publishable`, `validation_status`). `ToolCallRecord` auto-wrap via `__init_subclass__` so every tool call is logged. 14-day knowledge freshness window. Explicit prompt bans on stale-data citations. Spider context fabrication fix. | Agents were citing stale Notion data from 2023, fabricating spider sources, and making tool calls that couldn't be audited later. Without provenance the platform couldn't tell which outputs were grounded. | Stock, blockchain, and analysis agents now flag freshness windows (24h / 4h / varies) and publishable status. Every tool call has a `ToolCallRecord` row. Knowledge older than 14 days is filtered out at the source. | **Active** — provenance fields are still on the data-grounded agents; `ToolCallRecord` is still inherited automatically. | `docs/topics/agent-system.md` §"Provenance Tracking (Session 953)" and §"ToolCallRecord (Session 970)" and §"Agent Knowledge & Conversations (Session 988)"; `docs/handoffs/SESSION_1001_BLOG_TELEMETRY_GROUNDING.md`; `docs/handoffs/SESSION_1002_SPIDER_CONTEXT_FABRICATION_FIX.md` |
| **Sessions 1000, 1002B–1002C (Intelligence Desks + shared tools)** | Four Intelligence Desks defined (Stocks / Sports / Blockchain / Narrative) with coordinator agents fanning out to domain sub-agents. Three shared tools auto-injected into every agent's LLM schema: `web_search` (Tavily), `spider_query`, `delegate_to_specialist`. | The platform had specialist agents but no way for them to compose: stock agents couldn't reach the spider network's market data without re-implementing the lookup, and there was no clean way to delegate a sub-task without re-routing through the user. Desks gave domain bundles a single entry point. | 64 agents wired to shared tools. Four desk coordinators exist as on-demand entry points (`POST /api/home/trigger-desks/`). Stocks desk activates 9 agents; Sports 5; Blockchain 5; Narrative 4. | **Active for the shared tools.** Desks are **defined but not scheduled** — the daily `run_market_intelligence_desk` PeriodicTask was removed in commit `a88fb8e7` ("minimal beat schedule"). Desks fire only when something/someone explicitly invokes them. | `docs/handoffs/SESSION_1000_INTELLIGENCE_DESKS.md`; `docs/handoffs/SESSION_1002B_DELEGATION_SHARED_TOOLS.md`; `docs/topics/agent-system.md` §"Intelligence Desks" and §"Shared Tools & Delegation" |
| **Sessions 1027–1034 (health audit + waste cleanup + bounded tasks)** | Every agent classified Thriving / Struggling / Wasting against mission success rate. 79-agent end-to-end stress test (73 PASS / 6 FAIL, 92.4%). Waste agents removed from dispatch paths: CodeGeneratorAgent (no codebase access on Railway), AudioAgent (ElevenLabs quota), OpportunityScoringAgent (no revenue loop, was spawning 62+ runs/day). RAG user documents wired into all `AGENT_MAP` agents. Bounded task pattern documented: scope + length + "do NOT delegate". | The agent population had grown faster than the visibility into which agents were actually useful. Unbounded tasks were timing out at 45 minutes and burning LLM budget. Three agents were demonstrably wasting cycles. | Three waste paths closed (PRs #1273, #1283, #1284, #1285). 35 agents classified Thriving; 6 Struggling. Bounded-task language reduced timeouts from 45 minutes to seconds for the patterns that adopted it. EditorAgent's broken LLM call fixed (PR #1308). | **Active** — health classification is still the operating model; bounded-task pattern is the documented standard; waste-agent dispatches stayed closed. CodeGeneratorAgent is marked `blocked` in `AGENT_MAP`; AudioAgent is `rerouted`. | `docs/topics/agent-system.md` §"Agent Health Classification" and §"79-Agent Stress Test" and §"Waste Agents Removed"; `docs/handoffs/SESSION_1027_*` through `1034_*` series |
| **Sessions 1092–1099 (governance & autonomy gates — the "anti-spam" arc)** | BaseAgent renderer + 10-agent migration. EditorAgent dispatcher fallback. ThinkingAgent re-shadowing fix. `blocked_at` hygiene. Scheduled diagnostic primitive (CTO / COO / TrendAnalysis as monitors). Daily post cap (COO=2, others=3). Severity escalation rule. Suppressed-rollup counter. Canary Step 2 (controlled-injection deliverable path). `publish_intent` enum migration (`internal_only` / `publish_candidate` / `publish_required`). `verify_doc_claims` doc-vs-reality framework (Session 1099). Full agent audit: 34 active / 19 dormant 90 days / 8 never-executed / 59 fighting for 23 daily budget slots. | The system had become noisy: agents were generating content that wasn't being read, governance gates were stuck, the COO agent was hanging for 60 minutes, and docs were claiming agent counts that didn't match reality. The arc was a planned cleanup, not a single-PR fix. | 11 PRs in Session 1092 alone. Failure rate projected from 9.7% → ~4%. Anti-spam rails verified via 12-alert stress test. `verify_doc_claims` introduced a discipline of regenerable runtime evidence so the same drift can't accumulate again. | **Active** — the canary path is the standard rollout mechanism; the diagnostic primitive is reused by multiple agents; `verify_doc_claims` is part of every session-close. | `docs/handoffs/SESSION_1092_*` through `SESSION_1099_*` series; `core/services/doc_claim_verification.py`; `core/management/commands/verify_doc_claims.py`; MEMORY.md "Recent Major Work" |
| **Session 1115 (code-health refactor)** | `LearningBridge` ABC migration — all 9 bridges now subclass the abstract base, implement four abstract methods, thread ORM through `patterns['_X']`, and keep the original entry as a back-compat shim. Orphan reduction from 272 → 10 (96.3%) across 13 PRs. | The agent system's accumulated learning code had nine ad-hoc bridges that shared no contract. Adding a new bridge required tribal knowledge. Orphan code paths made it impossible to be sure where execution actually went. | The bridges now share a contract and can be safely extended; orphan paths down to a tractable number. Guard severity for AUDIT_FINDINGS #9 dropped from low → medium (closed). | **Active** — the ABC contract is still in force; new bridges follow the pattern. | `MEMORY.md` "Session 1115 — code-health refactors complete"; `project_session_1115_context_kit_audit.md` (memory file) |

---

## 4. What came of it

### Wins

- **Routing decoupled from intelligence.** Because `AGENT_MAP` is a
  deterministic dictionary, routing changes don't require LLM
  inference and can be reviewed like any other code change. Bugs
  show up as KeyErrors, not as "the model picked the wrong agent."
- **A shared spine.** Every agent gets context injection, learning
  hooks, the tool-call audit trail, workspace methods, and
  health-check mode by inheriting `BaseAgent`. New agents are
  cheap; cross-cutting behavior changes in one file.
- **Truth controls.** Provenance tracking + 14-day knowledge
  freshness + explicit stale-data bans + `ToolCallRecord` mean
  the platform can answer "what did this agent see, and when?"
  for any output.
- **Bounded-task discipline.** The pattern of (scope + length +
  "do NOT delegate") turned a class of 45-minute timeouts into
  fast, useful runs.
- **Governance that's actually enforced.** Daily post caps,
  severity escalation rules, the canary path, the
  `verify_doc_claims` runtime evidence — these compound. A new
  agent reaching deliverable surfaces has to go through them.

### Tradeoffs

- **`BaseAgent` is ~5,500 lines.** That's the cost of a shared
  spine: cross-cutting behavior is centralized, but the file is
  not casually readable. Most changes are localized to a section.
- **`AGENT_MAP` size has grown faster than utility.** Session
  1099's audit found 19 agents dormant for 90 days, 8 that have
  never executed, and 59 fighting for 23 daily budget slots.
  Cleanup is an ongoing program, not done.
- **Intelligence Desks are defined but not on a schedule.** Four
  desk task functions exist in `core/tasks.py` but have no
  `PeriodicTask` rows after `a88fb8e7` (the "minimal beat
  schedule" cleanup). To get a desk firing daily again you have
  to add the row back explicitly — easy to miss if you assume
  desks are autonomous.
- **Doc drift.** Even with `verify_doc_claims`, narrative docs
  (this one included) carry stats that age the moment runtime
  changes. The pattern of "runtime anchor wins" exists precisely
  because narrative drift is structural, not fixable by careful
  writing.

### Follow-on systems enabled

- **The PA (Rigby)** is the agent system's user-facing interface;
  she relies on `AGENT_MAP` and the routing layer for everything
  she delegates.
- **Intelligence Desks** are agent-bundle compositions on top of
  the same spine.
- **Content Pipeline / Deliberation** plugs into the
  DecisionEnforcer + ResearchContract + ExecutionMandate
  primitives.
- **`verify_doc_claims`** is the discipline that makes the
  `PLATFORM_INVENTORY` ↔ narrative-docs split workable —
  introduced in this arc, now load-bearing across the whole
  documentation system.

---

## 5. Current state snapshot

> Source for counts: `docs/PLATFORM_INVENTORY.md`, snapshot
> generated 2026-05-25 against git HEAD `d513cd7f`. Regenerate
> with `python manage.py generate_platform_inventory` if this
> doc is being read more than a session or two after the date
> above.

**Population.** 83 agents in `AGENT_MAP` (74 enabled, 8 rerouted,
1 blocked). 155 rows in the `Agent` DB table — DB rows include
persona metadata and learning telemetry for code-resident classes
plus inactive/historical personas.

**Status of the eight rerouted.** `AudioAgent`, `COOAgent`,
`CTOAgent`, `CodeReviewAgent`, `DevOpsAgent`,
`FullStackDeveloperAgent`, `VideoAgent`, `WorkflowAgent`. Rerouted
means the router will resolve them to a different agent (or block
them) rather than running the original class. The reasons vary by
agent: AudioAgent for ElevenLabs quota; COO/CTO for the daily
diagnostic re-shape; the others are documented per-agent.

**Status of the one blocked.** `CodeGeneratorAgent`. Removed
from all six dispatch paths in PRs #1273 / #1283 / #1285. Cause:
no codebase access on Railway, sandbox-only output. The class
still exists; the router refuses to invoke it.

**Routing.** Deterministic dictionary lookup. Optional semantic
routing via embeddings cosine-similarity (threshold 0.35, falls
back to keyword matching) for natural-language queries.

**Context layers per execution.** Twelve: scifi, spider, learning,
advisor, feedback, knowledge, workspace, docs, user, risk,
platform-tools-directive, user-docs. The order and content are
defined in `BaseAgent.gather_context()`.

**Shared tools auto-injected into every agent's LLM schema.**
Three: `web_search` (Tavily), `spider_query`
(`SpiderIntelligenceService`), `delegate_to_specialist`. 64 agents
are wired; four programmatic agents are intentionally skipped
(content_executor, opportunity_pipeline, workflow_orchestration,
workflow_agent).

**Health classification.** 35 Thriving / 6 Struggling / 3 Waste
paths closed (Session 1029). The 79-agent stress test stands at
73 PASS / 6 FAIL (92.4%). The 6 FAIL cases were pre-existing
external-service issues (missing API keys, quotas), not code
bugs.

**Intelligence Desks.** Four defined (Stocks 9 agents, Sports 5,
Blockchain 5, Narrative 4). All four are on-demand only. Trigger
path: `POST /api/home/trigger-desks/`. Cache keys
`desk:{stocks|sports|blockchain|narrative}:latest`. To re-enable
a desk on a schedule, add a `PeriodicTask` row in
`core/celery.py` for the relevant task function.

**Governance gates currently in place.**
- Daily post cap: COO=2, others=3.
- Severity escalation rule (Session 1096).
- Suppressed-rollup counter.
- `gate_hang`, rework/bounce, `publish_intent` (`internal_only`
  / `publish_candidate` / `publish_required`) — Session 1095.
- Canary path (controlled-injection deliverable) — Sessions
  1094–1098.
- `verify_doc_claims` runtime-evidence drift check — Session
  1099.

**Where to look when something stops working.**
- Agent returns no output → check `AgentExecution` rows for that
  agent_name; look at the most recent failed row.
- Tool call missing from audit → check `ToolCallRecord` rows;
  if absent, the agent isn't calling through `_execute_tool_call`
  (rare — the wrapper is inherited).
- Multi-agent conversation didn't terminate on a verdict →
  DecisionEnforcer didn't fire; check the conversation contract.
- Desk didn't run "yesterday" → expected: no PeriodicTask exists
  for any desk. Check whether someone hit the trigger endpoint.
- Output cites 2023 data → 14-day freshness window failed; check
  `_get_agent_knowledge()` in `ConversationOrchestrator`.

---

## 6. Open questions / unknown outcomes

These are points where the corpus is silent on either the original
motivation or the eventual outcome. They are not bugs in the
narrative — they are honest gaps a future operator should know
about.

- **Why exactly 155 DB Agent rows for 83 code-resident classes?**
  *Known:* DB rows include persona metadata beyond code classes
  (top types: income=20, content=17, career=15, business=14,
  job_search=12, finance=12, ai_ml=11, creative=11, marketing=10,
  analytics=7). *Inferred:* DB rows track historical personas
  that have been demoted or whose code class was renamed.
  *Unknown:* whether all 155 rows are actively used by any
  execution path, or whether some are legacy from earlier persona
  experiments. A row-level reconciliation pass would resolve
  this; none is recorded in handoffs so far.
- **Should the four Intelligence Desks be on a schedule again?**
  *Known:* the schedule removal was **deliberate**, not
  accidental — `docs/AUDIT_FINDINGS.md` finding #10 (Session 1115
  audit) records the investigation: `git log -S
  "run_market_intelligence_desk"` showed the schedule was removed
  in commit `a88fb8e7` ("minimal beat schedule" cleanup), and the
  audit's explicit decision was "doc is stale, schedule was
  intentionally removed." All four desks are intentionally
  on-demand only. *Unknown:* whether and when to re-enable a
  schedule — that's a product decision, not a corpus gap. The
  task functions still exist at `core/tasks.py:4356`; a
  `PeriodicTask` row plus a brief on intended cadence would be
  enough to re-activate.
- **What is the actual current utility distribution?** Session
  1099's audit found 19 agents dormant 90 days, 8 never-executed,
  59 fighting for 23 daily budget slots. *Unknown* whether the
  population has been pruned since. The next audit pass against
  current `AgentExecution` data would answer this.
- **`OpportunityScoringAgent` trigger.** Session 1029 disabled
  the `zero_revenue_7d` trigger that was spawning 62+ runs/day.
  *Unknown:* whether the agent has been wired to a replacement
  trigger that respects bounded-task discipline.
- **Voice rules and the Translation Layer.** Session 781 set
  role-anchored voices for 22 agents. *Unknown:* whether this
  list has been extended to cover the agents added since, or
  whether `UDB_TRANSLATION_LAYER.md` is now the canonical place
  for that voice contract. A reconciliation between
  `core/prompts/registry.py` roles and the translation-layer
  persona blocks would close the loop.
- **What happened to the 6 Struggling agents?** Session 1029
  named the classification but the corpus does not record
  per-agent resolutions for the six. *Unknown:* whether they
  were given bounded-task templates, demoted, or are still
  Struggling.
- **`learning_bridge_audit` generator known stale (Session
  1146 note).** The audit generator's "ABC unused" finding
  about LearningBridge is generator-stale (Session 1115 closed
  this). *Known:* the fix should be in the generator, not the
  output. *Unknown:* whether the generator has been patched yet.

---

## 7. Source index

### Primary doc sources

- `docs/topics/agent-system.md` — current-state topic doc; the
  closest companion to this narrative. Most session citations
  here originate from claims in that doc.
- `docs/AGENTS.md` — agent reference doc; longer-form per-agent
  detail (700+ lines). Stats inside it may drift; see
  `PLATFORM_INVENTORY.md` for current counts.
- `docs/PLATFORM_INVENTORY.md` — runtime-generated inventory.
  Sole authoritative source for counts. Snapshot used here was
  2026-05-25, git HEAD `d513cd7f`.
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor; subsystem
  glossary.
- `docs/UDB_TRANSLATION_LAYER.md` — audience contract; relevant
  to how agent outputs are framed across personas.

### Named session handoffs cited above

- `docs/handoffs/SESSION_781_AGENT_VOICE_FIXES.md`
- `docs/handoffs/SESSION_1000_INTELLIGENCE_DESKS.md`
- `docs/handoffs/SESSION_1001_BLOG_TELEMETRY_GROUNDING.md`
- `docs/handoffs/SESSION_1002_SPIDER_CONTEXT_FABRICATION_FIX.md`
- `docs/handoffs/SESSION_1002B_DELEGATION_SHARED_TOOLS.md`
- `docs/handoffs/SESSION_1002C_SUPER_FALLBACK.md`
- Session 1027 / 1029 / 1032 / 1033 / 1034 — agent health,
  stress test, bounded-task pattern, EditorAgent LLM fix
  (specific handoff filenames in `docs/handoffs/`).
- Sessions 1092 / 1093 / 1094 / 1095 / 1096 / 1098 / 1099 — the
  governance & autonomy gates arc. The MEMORY.md entries
  `project_session_1092_governance_noise.md` through
  `project_session_1099_doc_verification_tool.md` are the
  fastest summaries; the handoff files in `docs/handoffs/` are
  authoritative.
- Session 1115 — `project_session_1115_context_kit_audit.md`
  (memory) + handoff files.

### Code anchors

- `core/agent_router.py` — `AGENT_MAP`, routing.
- `core/agents/base_agent.py` — `BaseAgent` (~5,500 lines).
- `core/agents/decision_enforcer_agent.py` — DecisionEnforcer.
- `core/epa_handlers_tools.py` — `WORKSPACE_AWARE_AGENTS`.
- `core/services/agent_learning_service.py` — per-user learning
  loop.
- `core/services/auto_spawner_service.py` — reflex spawning.
- `core/services/doc_claim_verification.py` +
  `core/management/commands/verify_doc_claims.py` — Session 1099
  runtime-evidence drift verifier.
- `core/prompts/registry.py` — role-anchored conversation
  voices (Session 781).
- `core/conversation_orchestrator.py` — multi-agent
  conversation runner; `_get_agent_knowledge()` enforces 14-day
  freshness.

### Verification commands

- `python manage.py generate_platform_inventory` — regenerate
  the inventory anchor.
- `python manage.py verify_doc_claims --only-drift` — list
  which claims drift from runtime.
- `python manage.py build_docs_index` — refresh `docs/INDEX.md`
  + `_index.json` (always commit both after doc changes).
