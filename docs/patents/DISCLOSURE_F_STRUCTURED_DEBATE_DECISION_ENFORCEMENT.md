# Invention Disclosure F: Structured Multi-Agent Debate with Constructive Tension Enforcement, Decision Mandates, and Governance Escalation

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Structured Multi-Agent Debate System with Enforced Constructive Tension, Mandatory Decision Mandates, and Hierarchical Human-in-the-Loop Governance Escalation

---

## 2. Field / Technical Domain

Multi-agent AI decision-making for autonomous systems. Specifically, methods for structuring debates between heterogeneous AI agents using role-based turn flows with enforced constructive disagreement, forcing decisive outcomes through a "prefrontal cortex" decision enforcer that rejects hedging, and escalating high-stakes decisions to human governance gates with ML confidence tracking and override detection.

---

## 3. Problem (What Breaks in Prior Systems)

Multi-agent AI systems that involve multiple agents collaborating on decisions face three structural failures:

**a) Agents converge on hollow agreement.** When multiple LLM agents "discuss" a topic, they naturally converge on safe, agreeable positions. Without structural enforcement of disagreement, multi-agent conversations produce the same output that a single agent would produce, eliminating the value of multiple perspectives.

**b) Debates produce analysis, not decisions.** Multi-agent frameworks (AutoGen, CrewAI, LangChain) generate rich conversational transcripts but do not enforce that a decisive outcome is produced. Conversations end with "further analysis is recommended" rather than concrete, actionable mandates with owners, deadlines, and kill criteria.

**c) Autonomous decisions lack governance guardrails.** Systems that let agents make decisions autonomously cannot distinguish between low-risk decisions (content topic selection) and high-risk decisions (financial actions, legal commitments, irreversible deployments). There is no mechanism to route high-stakes decisions to human approval while allowing low-stakes decisions to proceed autonomously.

---

## 4. Solution Summary

A three-layer decision architecture:

1. **Structured Debate Layer**: Role-based turn flows (analytical: propose→challenge→synthesize→decide; debate: position→counter→rebut→conclude; etc.) with enforced constructive tension — the system detects and penalizes hollow agreement while rewarding substantive disagreement.

2. **Decision Enforcement Layer**: A "prefrontal cortex" agent (`DecisionEnforcerAgent`) that takes debate transcripts and forces a concrete `ExecutionMandate` with: chosen path, decision owner, confidence, experiments, kill criteria, deadline, rejected paths with rationale, and spawned tasks. Forbidden phrases ("further analysis needed", "more research required") are explicitly blocked.

3. **Governance Escalation Layer**: High-stakes decisions are routed to `HumanAttentionItem` records with ML confidence scores, recommendation tracking, and override detection. Institutional-track initiatives require boardroom approval. A "watch and verify" mode enables paper-trading validation before real execution.

---

## 5. As-Built Mechanism (Numbered Steps + Components)

### Layer 1: Structured Debate with Tension Enforcement

**Component:** `ConversationOrchestrator` (`core/conversation_orchestrator.py`, ~2100 lines)

**6 turn flow patterns (lines 61-68):**

| Type | Flow | Use Case |
|------|------|----------|
| analytical | propose → challenge → synthesize → decide | Content review, technical evaluation |
| creative | brainstorm → expand → refine → select | Topic generation, creative direction |
| debate | position → counter → rebut → conclude | Bull vs. bear, policy disputes |
| planning | goals → steps → dependencies → schedule | Initiative planning, project scoping |
| critique | present → challenge → defend → improve | Content quality review |
| general | explore → discuss → clarify → summarize | Open-ended exploration |

**ConversationState tracking (lines 110-131):**
- `tension_count`: Turns with constructive disagreement (challenges, rebuttals, counter-arguments)
- `grounding_count`: Turns referencing real metrics, data, or system state
- `empty_agreement_count`: Turns with hollow agreement ("Great point!", "I agree completely")
- `last_tension_turn`: When the last substantive challenge occurred
- `used_openers`: Track repetitive opening phrases (Session 781 anti-pattern detection)
- `criteria_met`: Which success criteria are satisfied

**Tension enforcement rules (lines 29-37):**
- Constructive tension required every 2-3 turns — if `turn_number - last_tension_turn > 3`, the system injects a challenge prompt
- Platform grounding required — at least 1 in 4 turns must reference real metrics/systems
- Empty agreement detection — hollow agreement phrases detected and counted as anti-patterns

**Message generation retry logic (lines 1874-1966):**
1. Generate with gpt-4o, reasoning mode, max 1500 tokens (2500 for final turn)
2. If response empty/incomplete → retry with +500 tokens (cap 4000)
3. If final turn missing `=== DecisionSummary ===` → rebuild focused prompt, retry
4. After max retries → append `=== CONVERSATION FAILED ===` block
5. **Fallback decision enforcement** (lines 1265-1298): If no decision extracted after conversation, call DecisionEnforcerAgent with last 3 messages

### Layer 2: Decision Enforcement ("Prefrontal Cortex")

**Component:** `DecisionEnforcerAgent` (`core/agents/decision_enforcer_agent.py`, 528 lines)

**Forbidden phrases (lines 95-103):**
```
"Further analysis recommended"    "More research needed"
"Consider exploring"              "Should validate"
"Needs investigation"             "Productive discussion"
"We should look into"
```

If any of these appear in the decision output, the agent rejects it and regenerates.

**ExecutionMandate output structure (lines 114-141):**

| Field | Type | Purpose |
|-------|------|---------|
| `chosen_path` | string | Specific, actionable decision statement |
| `reason` | string | Why this path, with ACTUAL evidence from debate |
| `decision_owner` | string | Agent or role responsible |
| `confidence` | float (0-1) | Confidence in decision |
| `confidence_reason` | string | Why this confidence level |
| `experiments` | list[string] | Specific experiments with measurable criteria |
| `kill_criteria` | list[string] | Measurable failure conditions with thresholds |
| `deadline` | ISO date | When this must be completed |
| `rejected_paths` | dict | Alternative → why rejected based on debate evidence |
| `acknowledged_risks` | list[string] | Risks being accepted |
| `spawned_tasks` | list[SpawnedTask] | Tasks to execute: agent, action, deadline, priority |

**Execution flow (lines 179-281):**
1. Validate input (must have debate_messages or synthesis)
2. Extract experiment/kill_criteria hints from debate text
3. Build prompt with topic + debate summary + hints
4. LLM call: gpt-4o, temp=0.3, max_tokens=2000
5. Parse JSON → ExecutionMandate, validate (ValueError if invalid)
6. Return AgentResult with mandate dict + markdown + metadata

**Task spawning (lines 445-478):**
For each `spawned_task` in the mandate, creates `queue_agent_task.delay()` with context including `mandate_id`, `mandate_owner`, `deadline`, `priority`.

### Layer 3: Governance Escalation

**Component:** `HumanAttentionItem` (`core/models_human_interface.py`, lines 20-227)

**Escalation trigger conditions:**
- Circuit breaker trips (2+ timeouts in 24h) → creates HumanAttentionItem with `source_type='circuit_breaker'`
- Ops Autopilot governance auto-decision grace period (1 hour) → auto-approves low-blast-radius items
- Initiative institutional track requires boardroom approval
- High-confidence ML recommendations that contradict human preference patterns

**Fields enabling ML-aware human decisions:**

| Field | Purpose |
|-------|---------|
| `ml_prediction` (JSON) | What the AI recommended |
| `ml_confidence` (float) | AI's confidence (0-1) |
| `ml_recommendation` (string) | "approve" / "reject" / etc. |
| `decision` (string) | Human's actual choice |
| `human_overrode_ml` (bool) | Did human disagree with ML? |
| `override_reason` (text) | Why human overrode |
| `time_to_decision_ms` (int) | How long human deliberated |

**Watch and Verify mode (Session 746 — paper trading):**

| Field | Purpose |
|-------|---------|
| `verification_outcome` | pending, won, lost, push, cancelled |
| `verification_profit` (float) | Calculated P/L without executing |
| `event_completed_at` (datetime) | When the real event concluded |

This enables the system to validate AI recommendations against real-world outcomes without committing resources.

**Status flow:** `pending → viewed → acted → verified` (or `deferred → ignored → expired`)

**Override tracking:** `record_decision()` (line 184-214) automatically detects when the human chose differently from `ml_recommendation` and sets `human_overrode_ml=True`. These overrides feed back into the ML training loop.

### Governance Gate: Boardroom Approval

**Component:** Initiative model (`core/models_document_registry.py`, lines 37-490)

**Two execution tracks:**
- **Fast track** (stages 1-2 only): Low-risk initiatives, auto-progression allowed
- **Institutional track** (full 5-stage pipeline): Requires boardroom approval for progression

**Content flags triggering institutional track:**
`external_data`, `user_data`, `public_publishing`, `legal_compliance`, `financial`, `irreversible`

**Boardroom gate fields:**
- `requires_boardroom_approval` (bool)
- `boardroom_approved` (bool)
- `boardroom_approved_by` (string)
- `boardroom_approval_notes` (text)
- Per-stage gates: `stage_2_approved`, `stage_3_approved`, `stage_4_approved`

### Multi-Agent Debate Patterns (4 implementations)

**Pattern 1: Content Debate (4 agents)**
`core/models_autonomous_studio.py` (lines 568-680)
- TopicMinerAgent: "Trending now because..."
- ContrarianAgent: "Too saturated, try..."
- PerformanceAnalystAgent: "Past data shows..."
- CreativeDirectorAgent: "Unique angle could be..."
- Coordinator synthesizes final decision recording all 4 positions

**Pattern 2: Market Intelligence (Bull vs. Bear)**
`core/agents/stocks/market_intelligence_coordinator.py` (lines 703-790)
- BullCaseAgent presents bullish thesis
- BearCaseAgent presents bearish thesis
- **Disagreement as a feature**: When both have HIGH conviction → classified as `debate_zone` (most interesting for alpha generation)
- Does NOT force consensus — preserves and surfaces genuine uncertainty

**Pattern 3: HiveMindSession (Collective Intelligence)**
`core/models_unified_system.py` (lines 9978-10239)
- N agents contribute perspectives to shared question
- Contributions scored by confidence and typed by perspective (analysis, creative, technical, strategic)
- Synthesis combines all views without requiring agreement

**Pattern 4: Content Deliberation (Review + Decision)**
`core/services/content_deliberation_runner.py`
- 3 independent reviewers produce verdicts
- EditorAgent + ContentStrategyAgent discuss reviewer feedback
- DecisionEnforcerAgent forces PUBLISH/REVISE/KILL

---

## 6. Novelty Hooks (Section 102)

**a) Enforced constructive tension with penalty for hollow agreement.** The system tracks `tension_count` and `empty_agreement_count` per conversation, requiring substantive challenges every 2-3 turns. No known multi-agent framework enforces disagreement — all existing frameworks optimize for agent cooperation.

**b) Forbidden-phrase blocking in decision output.** The DecisionEnforcerAgent explicitly rejects hedging language ("further analysis needed", "more research required") and regenerates until a concrete decision is produced. No known decision system bans specific output phrases.

**c) ExecutionMandate with kill criteria and spawned tasks.** The decision output includes not just what to do, but when to stop doing it (kill_criteria with measurable thresholds) and what tasks to spawn (with agent, action, deadline, priority). No known multi-agent decision system produces structured post-decision task dispatching.

**d) ML confidence + human override tracking.** `HumanAttentionItem` records both the AI's recommendation/confidence and the human's decision, automatically detecting overrides. This paired recording enables learning from human corrections. No known governance system tracks both sides of the AI-human decision and computes override rate.

**e) Watch-and-verify paper trading for governance decisions.** The system can track hypothetical outcomes (verification_profit) of decisions without executing them, enabling risk-free validation of AI recommendations against real-world outcomes.

**f) Disagreement as alpha signal.** In the Market Intelligence pattern, high-conviction disagreement between Bull and Bear agents is explicitly classified as the most interesting category (`debate_zone`), not a failure to reach consensus. This inverts the standard multi-agent goal of reaching agreement.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Requiring disagreement contradicts multi-agent design goals.** Multi-agent frameworks (AutoGen, CrewAI) are designed to facilitate agent cooperation. Requiring constructive tension — and penalizing agreement — is counter-intuitive because it appears to degrade system coherence. The non-obvious insight: forced disagreement surfaces blind spots and alternative perspectives that voluntary cooperation misses.

**b) Banning hedging phrases is counter-intuitive for AI safety.** Safety-focused AI systems typically encourage cautious language ("this may not be accurate"). Banning hedging phrases and forcing decisive mandates appears unsafe. The non-obvious insight: in an operational context, indecisive outputs are worse than wrong decisions, because indecisive outputs block the entire downstream pipeline while wrong decisions can be caught by subsequent verification.

**c) Paper trading (watch-and-verify) as a governance mechanism is borrowed from finance, not software.** Applying paper trading to AI governance decisions (track hypothetical outcomes without executing) is a cross-domain transfer from financial trading that is non-obvious in the AI operations context.

**d) Override detection as a learning signal requires paired recording.** Recording both AI recommendation and human decision in the same record — and automatically computing whether an override occurred — is non-obvious because most systems record either the AI output or the human decision, not both in a structure that enables automatic comparison.

---

## 8. Operational Benefits (Measurable Outputs)

- **Decision completion rate:** DecisionEnforcerAgent eliminates conversations that end without actionable outcomes. Every debate produces a structured ExecutionMandate.
- **Tension quality:** Constructive tension tracking ensures multi-agent debates produce diverse perspectives, not echo chambers.
- **Governance coverage:** Content flags automatically route high-risk initiatives to boardroom approval, preventing unauthorized autonomous actions.
- **Override learning:** ML override tracking enables the system to learn from human corrections, improving future AI recommendations.
- **Paper trading validation:** Watch-and-verify mode validates AI recommendations against real outcomes without committing resources, building confidence before live execution.
- **Task spawning:** ExecutionMandate → spawned_tasks creates automatic follow-through, preventing decisions from being made but never executed.

---

## 9. Alternative Embodiments

**a) Weighted voting instead of coordinator synthesis.** Instead of a coordinator synthesizing agent positions, each agent could vote with a confidence-weighted ballot, and the decision could be the highest-weighted option. This removes the coordinator as a single point of bias.

**b) Adversarial red-team agent.** Instead of enforcing tension through conversational rules, a dedicated adversarial agent could be injected into every debate with the explicit objective of finding flaws in the majority position. This structural adversary provides more consistent challenge than tension-tracking heuristics.

**c) Escalation threshold learning.** Instead of fixed content flags triggering institutional track, the system could learn which decision characteristics predict human overrides and automatically escalate decisions with similar characteristics.

**d) Multi-round governance with diminishing human involvement.** For repeated decision types where human overrides decrease over time, the system could gradually reduce governance requirements: first 10 decisions require approval, next 10 require notification only, subsequent decisions are fully autonomous.

**e) Cross-debate knowledge transfer.** Insights from one debate (kill criteria, rejected paths) could be injected into future debates on related topics, enabling institutional memory across decision episodes.

**f) Asynchronous debate with contribution deadlines.** Instead of synchronous turn-taking, agents could contribute asynchronously within a deadline window, enabling agents with different computational costs to participate without blocking faster agents.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for producing decisive outcomes from multi-agent debates in an autonomous AI system, the method comprising:

(a) initiating a structured debate between a plurality of AI agents, each agent assigned a role from a role-based turn flow defining a sequence of debate phases;

(b) tracking, for each turn of the debate, a tension metric indicating whether the turn contains substantive disagreement with a prior turn, and an agreement metric indicating whether the turn contains hollow agreement without substantive contribution;

(c) enforcing a minimum tension frequency by injecting challenge prompts when the number of turns since the last substantive disagreement exceeds a configurable threshold;

(d) upon completion of the debate, submitting the debate transcript to a decision enforcement agent that is prohibited from producing hedging language matching a predefined set of forbidden phrases;

(e) generating, by the decision enforcement agent, a structured execution mandate comprising at minimum: a chosen action path, a decision owner, a confidence score, measurable kill criteria, a deadline, and rejected alternative paths with rationale; and

(f) routing the execution mandate to one of: autonomous execution when the decision pertains to a low-risk category, or human governance review when the decision pertains to a high-risk category determined by content flags.

### Dependent Claims

1. The method of the independent claim, wherein the role-based turn flow is selected from: analytical (propose-challenge-synthesize-decide), debate (position-counter-rebut-conclude), creative (brainstorm-expand-refine-select), planning (goals-steps-dependencies-schedule), and critique (present-challenge-defend-improve).

2. The method of the independent claim, wherein the tension metric detects substantive disagreement by identifying counter-arguments, challenges, rebuttals, and evidence-based objections in the turn content.

3. The method of the independent claim, wherein the forbidden phrases comprise at least: "further analysis recommended," "more research needed," "consider exploring," "should validate," and "needs investigation."

4. The method of the independent claim, wherein the execution mandate further comprises a list of spawned tasks, each task specifying an agent to execute, an action description, a deadline, and a priority level.

5. The method of claim 4, further comprising dispatching each spawned task to a distributed task queue for asynchronous execution with context including the mandate identifier and decision owner.

6. The method of the independent claim, wherein the high-risk categories are determined by content flags comprising: external data usage, user data handling, public publishing, legal compliance requirements, financial transactions, and irreversible actions.

7. The method of the independent claim, wherein the human governance review comprises presenting the execution mandate alongside the AI's confidence score and recommendation, recording the human's decision, and automatically detecting when the human's decision differs from the AI's recommendation.

8. The method of claim 7, further comprising a watch-and-verify mode wherein the execution mandate is not executed but its predicted outcome is tracked against actual real-world events to validate decision quality without committing resources.

9. The method of the independent claim, wherein one debate pattern explicitly preserves disagreement as a valued output, classifying high-conviction disagreement between agents as a signal of genuine uncertainty rather than a failure to reach consensus.

10. The method of the independent claim, further comprising a fallback decision enforcement step wherein, if the debate fails to produce a decision summary after a maximum number of turns, the last N turns are submitted to the decision enforcement agent as a reduced input.

11. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Structured Debate Turn Flow (Analytical)**
```
Turn 1: Agent A [PROPOSE]
  "Based on spider data, we should focus on AI market trends..."
      |
Turn 2: Agent B [CHALLENGE]
  "The data is 48h old and the market shifted — counter-evidence shows..."
      |
Turn 3: Agent A [SYNTHESIZE]
  "Incorporating the counter-evidence, the updated position is..."
      |
Turn 4: Agent B [DECIDE]
  "=== DecisionSummary === ..."
```

**Figure 2 — Tension Enforcement State Machine**
```
[Turn N: Agent speaks]
      |
[Classify turn: tension / grounding / empty_agreement]
      |
[Update ConversationState counters]
      |
[turns_since_last_tension > 3?]
   |YES                |NO
   v                   v
[Inject challenge     [Continue
 prompt into next      normally]
 turn's context]
```

**Figure 3 — Decision Enforcement (Prefrontal Cortex)**
```
[Debate Transcript]
      |
      v
[DecisionEnforcerAgent]
      |
[Generate ExecutionMandate]
      |
[Contains forbidden phrases?]
   |YES → [Reject, regenerate]
   |NO
   v
[Validate: has chosen_path, owner, deadline, kill_criteria?]
   |FAIL → [ValueError, retry]
   |PASS
   v
[ExecutionMandate created]
      |
[Spawn tasks → Celery queue]
```

**Figure 4 — Governance Escalation Hierarchy**
```
[Decision Made]
      |
[Content flags check]
      |
[Low-risk (fast track)]        [High-risk (institutional)]
      |                               |
[Auto-execute]                  [HumanAttentionItem created]
                                      |
                                [Human reviews]
                                      |
                               ┌──────┴──────┐
                               v              v
                          [Approve]      [Override]
                               |              |
                          [Execute]    [Record override]
                                       [Learn from correction]
```

**Figure 5 — Disagreement as Alpha Signal (Bull vs. Bear)**
```
[BullCaseAgent: HIGH conviction]  [BearCaseAgent: HIGH conviction]
         |                                    |
         └──────────┬─────────────────────────┘
                    |
              [Both HIGH?]
              YES → debate_zone (MOST INTERESTING)

[BullCaseAgent: HIGH]  [BearCaseAgent: LOW]
         |                       |
         └──────┬────────────────┘
                |
          [One HIGH, one LOW?]
          YES → clear_direction (HIGH confidence)
```

---

## 12. Prior Art Buckets to Cite Against

**a) Multi-Agent Frameworks (AutoGen, CrewAI, LangChain Agents)**
- Teaches: Agent orchestration, role assignment, multi-turn conversations
- Does NOT teach: Enforced constructive tension with penalty for agreement, forbidden-phrase blocking in decision output, or structured execution mandates with kill criteria

**b) Deliberative Democracy Systems (Pol.is, Loomio, Consul)**
- Teaches: Structured deliberation, proposal/counter-proposal, voting mechanisms
- Does NOT teach: AI agent participants, automated tension enforcement, execution mandate generation, or task spawning from decisions

**c) Debate Systems in AI Safety (Anthropic debate, AI Safety via Debate)**
- Teaches: Two-agent debate as a safety mechanism, judge evaluates debate
- Does NOT teach: N-agent debates with role-based turn flows, constructive tension tracking, hedging prohibition, or governance escalation based on risk classification

**d) Decision Support Systems (GDSS, Expert Systems)**
- Teaches: Structured decision-making, multi-criteria analysis, group decision support
- Does NOT teach: AI agents as autonomous decision participants, enforced disagreement, automatic task spawning from decisions, or ML confidence + human override tracking

**e) Workflow Engines (Temporal, Airflow, Prefect)**
- Teaches: Task orchestration, conditional branching, retry logic
- Does NOT teach: Debate-driven task generation, content-flag-based governance routing, or paper trading validation of decisions

**f) Human-in-the-Loop ML (Active Learning, HITL labeling)**
- Teaches: Human feedback on ML predictions, uncertainty sampling
- Does NOT teach: Structured governance escalation with override detection, watch-and-verify paper trading mode, or paired AI-recommendation/human-decision recording with automatic override computation

---

## Observability Evidence (Proving This Runs in Production)

### Debate Turn Tracking (DeliberationTurn records)
```sql
SELECT turn_number, agent_name, role, length(content), content_hash
FROM core_deliberationturn WHERE session_id = 'abc123'
ORDER BY turn_number;
-- (1, 'EditorAgent', 'present', 1245, 'sha256...')
-- (2, 'ContentStrategyAgent', 'challenge', 982, 'sha256...')
-- (3, 'EditorAgent', 'defend', 1567, 'sha256...')
-- (4, 'ContentStrategyAgent', 'improve', 1103, 'sha256...')
```

### ExecutionMandate Output
```json
{
    "chosen_path": "Publish the AI market analysis with revised crypto section",
    "decision_owner": "ContentWriterAgent",
    "confidence": 0.82,
    "kill_criteria": ["Reader engagement < 2% after 48h", "More than 3 factual corrections needed"],
    "deadline": "2026-03-23T00:00:00Z",
    "rejected_paths": {"Kill the article": "Good structure, just needs crypto update"},
    "spawned_tasks": [{"agent": "ContentWriterAgent", "action": "Revise crypto section", "priority": 1}]
}
```

### HumanAttentionItem with Override
```sql
SELECT title, ml_recommendation, ml_confidence, decision, human_overrode_ml, time_to_decision_ms
FROM core_humanattentionitem WHERE source_type = 'circuit_breaker';
-- ('Circuit breaker: CustomerResearchAgent', 'approve_block', 0.91, 'reject', true, 45200)
```

---

## Examiner Story

Prior art teaches multi-agent conversation frameworks that orchestrate agent interactions (AutoGen, CrewAI), AI safety debate where two agents argue before a judge (Anthropic debate research), and group decision support systems with structured deliberation (GDSS). However, no single reference or obvious combination teaches a system that (1) enforces constructive tension by tracking substantive disagreement per turn and injecting challenge prompts when tension frequency drops below a configurable threshold, (2) penalizes hollow agreement as an anti-pattern rather than a success signal, (3) forces decisive outcomes through a decision enforcement agent that explicitly prohibits hedging language and produces structured execution mandates with kill criteria and spawned tasks, (4) routes decisions to human governance review based on content-risk classification (external data, user data, financial, irreversible) while allowing low-risk decisions to execute autonomously, and (5) tracks both AI recommendations and human decisions in paired records that automatically detect overrides for learning feedback. The combination is non-predictable because (a) multi-agent frameworks optimize for cooperation not enforced disagreement, (b) AI safety debate research uses two agents with a judge rather than N agents with role-based turn flows, (c) decision support systems produce analysis not spawnable execution mandates, and (d) no known system combines debate structure with automatic governance escalation based on decision risk classification.
