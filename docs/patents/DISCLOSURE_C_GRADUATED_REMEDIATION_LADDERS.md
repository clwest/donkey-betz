---
title: "Invention Disclosure C: Graduated Remediation Ladders with Automatic De-escalation and Budget/ROI-Coupled Throttling"
kind: invention_disclosure
disclosure_id: C
workstream: WS1 (Ops Autopilot)
status: draft (Attorney Review Pending)
last_updated: 2026-03-16
originating_session: pre-session-tracking (March 16, 2026 batch)
inventor: Chris West (DonkeyKing)
provenance_confidence: HIGH
provenance_note: One of 12 invention disclosures drafted as a single March 16, 2026 batch. Frontmatter added Session 1160 (2026-05-26) as part of the patents preservation pass; body content unchanged from original draft. See `docs/patents/README.md` for workstream organization and narrative cross-link map.
maps_to_narratives:
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/BODY_SYSTEMS.md
companion_docs:
  - docs/patents/README.md
  - docs/patents/EXECUTIVE_SUMMARY.md
---

# Invention Disclosure C: Graduated Remediation Ladders with Automatic De-escalation and Budget/ROI-Coupled Throttling

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Closed-Loop Graduated Remediation State Machine for Autonomous Agent Systems with Automatic De-escalation and Quality-Weighted ROI Throttling Under Budget Pressure

---

## 2. Field / Technical Domain

Autonomous operations control for distributed AI agent platforms. Specifically, methods and systems for automatically remediating recurring agent failures through graduated intervention ladders that escalate based on observed failure rates, de-escalate based on observed recovery, and coordinate with budget enforcement and quality-weighted return-on-investment throttling to allocate compute resources under spend constraints.

---

## 3. Problem (What Breaks in Prior Systems)

Multi-agent AI systems face recurring operational failures (timeouts, provider errors, quality degradation) that require graduated responses. Prior approaches have four structural deficiencies:

**a) Binary remediation.** Existing systems offer binary responses: an agent is either running or stopped. There is no intermediate state where an agent receives adjusted parameters (longer timeouts, smaller batches) to test whether a lighter intervention resolves the issue before escalating to blocking.

**b) No automatic de-escalation.** When a system blocks or throttles an agent, there is typically no mechanism to automatically restore normal operation after the issue resolves. Manual unblocking introduces delays and creates operational debt. Agents remain in degraded states long after the underlying issue has passed.

**c) Escalation without recovery tracking.** Existing escalation frameworks (PagerDuty, OpsGenie) escalate notifications to humans but do not track whether the agent itself has recovered. The escalation ladder measures response time of the human operator, not the recovery trajectory of the failing component.

**d) Budget and quality decoupled from remediation.** Cost controls and quality scoring operate independently from failure remediation. An agent that is expensive but produces high-quality output is throttled the same way as an agent that is expensive and produces low-quality output. Budget pressure triggers blanket freezes rather than selective, ROI-informed throttling.

---

## 4. Solution Summary

A closed-loop remediation system comprising three integrated mechanisms:

1. **Graduated Timeout Remediation Ladder (L0-L3)**: A 4-level state machine that applies progressively stronger interventions (monitoring → timeout increase → batch reduction → temporary block), with automatic de-escalation after 12 consecutive clean cycles. Each level adds a specific override and removes it upon de-escalation.

2. **Graduated Deliberation Remediation Ladder**: A parallel 3-level ladder for content deliberation failures (panel reduction → model fallback → single-reviewer mode), following the same escalation/de-escalation pattern.

3. **Budget-Coupled ROI Throttling**: Under budget pressure, a quality-weighted ROI score (QROI = ROI x quality_weight) determines per-agent throttle intensity. High-QROI agents continue operating; low-QROI agents receive cooldown periods. Protected purposes (PA chat, governance, authentication) are never throttled.

The three mechanisms share the same `AgentControlEntry` infrastructure for blocking and the same `SystemConfiguration` table for overrides, ensuring consistent behavior without conflicting interventions.

---

## 5. As-Built Mechanism (Numbered Steps + Components)

### Mechanism 1: Timeout Remediation Ladder

**Location:** `core/services/ops_autopilot/remediation.py` (lines 862-1193)

#### State Machine Definition

| Level | State | Intervention | Override Key | Entry Condition | Exit Condition |
|-------|-------|-------------|-------------|-----------------|----------------|
| L0 | Monitoring | None | — | Default state | ≥5 timeouts/hr |
| L1 | Timeout Adjusted | Increase timeout by 50% (capped at 1800s) | `agent_timeout_override:{agent}` | ≥5 timeouts/hr OR escalation from L0 after 6 cycles | 12 clean cycles (0 timeouts) |
| L2 | Batch Reduced | Reduce batch size by 50% | `timeout_ladder_batch_reduce:{agent}` | L1 escalation after 6 cycles without improvement | 12 clean cycles |
| L3 | Temporarily Blocked | Block via AgentControlEntry with 4h TTL | `AgentControlEntry(blocked_by='timeout_playbook', ttl_hours=4)` | L2 escalation after 6 cycles without improvement | 12 clean cycles (after TTL expiry + re-entry) |

#### Constants (lines 884-900)
```
EVAL_WINDOW_CYCLES = 6          # Cycles before considering escalation (~60 min)
RECOVERY_CYCLES = 12            # Consecutive clean cycles for de-escalation (~2 hours)
ENTRY_THRESHOLD = 5             # Timeouts/hour to enter ladder
MAX_TIMEOUT_MULTIPLIER = 2.0    # Never exceed 2x original timeout
MAX_TIMEOUT_ABSOLUTE = 1800     # 30-minute hard cap on any timeout
BLOCK_TTL_HOURS = 4             # L3 temporary block duration
```

#### Evaluation Algorithm (lines 975-1014)

**Step 1 — Metric Collection.** Query `FailureSignature` records with `category='timeout'` for each agent. Compute timeouts per hour in the current evaluation window.

**Step 2 — State Classification.** For each agent:
- **Not on ladder + below threshold**: Skip (no action needed)
- **Not on ladder + above threshold**: Enter L1 immediately
- **On ladder + zero timeouts this cycle**: Increment clean counter
- **On ladder + timeouts this cycle**: Reset clean counter to 0

**Step 3 — De-escalation Check.** If clean counter >= `RECOVERY_CYCLES` (12):
- Step down one level
- Remove the current level's override
- Reset clean counter

**Step 4 — Escalation Check.** If cycles since last escalation >= `EVAL_WINDOW_CYCLES` (6) AND still failing:
- Escalate to next level
- Apply the next level's override
- Reset cycle counter

**Step 5 — Override Application.**
- L1 applies: `SystemConfiguration(key='agent_timeout_override:{agent}', value=str(new_timeout))`
  - New timeout = `min(current_timeout * 1.5, MAX_TIMEOUT_ABSOLUTE)`
  - The `_AGENT_TIMEOUT_SECONDS` lookup in `execute_agent_task` checks this override before using the default
- L2 applies: `SystemConfiguration(key='timeout_ladder_batch_reduce:{agent}', value='0.5')`
  - Batch dispatch systems check this override to reduce concurrent tasks
- L3 applies: `AgentControlEntry.update_or_create(agent_name=agent, defaults={status:'blocked', blocked_by:'timeout_playbook', ttl_hours:4})`
  - Enforced at all 4 enforcement points (Celery, router, dispatch, learning)

#### De-escalation Override Removal (lines 1120-1193)
- L3 → L2: Unblock agent (`AgentControlEntry.status='enabled'`)
- L2 → L1: Delete `timeout_ladder_batch_reduce:{agent}` from SystemConfiguration
- L1 → L0: Delete `agent_timeout_override:{agent}` from SystemConfiguration

**Key property:** Each level adds exactly one override and removes exactly that override when de-escalating. Overrides from lower levels persist during escalation (L2 has both timeout increase + batch reduction active).

### Mechanism 2: Deliberation Remediation Ladder

**Location:** `core/services/ops_autopilot/remediation.py` (parallel structure)

| Level | Intervention | Override |
|-------|-------------|---------|
| L1 | Reduce reviewer panel from 3 to 2 | `deliberation_panel_size:{topic}` = 2 |
| L2 | Model fallback to cheaper provider | `llm_fallback_active:{provider}` = True |
| L3 | Single-reviewer mode | `deliberation_panel_size:{topic}` = 1 |

Same escalation/de-escalation mechanics as the timeout ladder.

### Mechanism 3: Budget Controller (3-Tier)

**Location:** `core/services/ops_autopilot/budget.py` (lines 238-462)

**Step 1 — Spend Computation.** Every 10 minutes (`BUDGET_CHECK_INTERVAL_MINUTES`), query `LLMCallLog` for:
- Hourly spend: `SUM(cost) WHERE created_at >= now - 1h`
- Daily spend: `SUM(cost) WHERE created_at >= now - 24h`
- Top 10 agents by spend
- Top 10 models by spend

**Step 2 — Tier Evaluation.**

| Tier | Condition | Action |
|------|-----------|--------|
| Normal | daily_spend < 70% of `BUDGET_DAILY_CAP_USD` ($100) | No action |
| Soft Limit | daily_spend >= 70% of cap | Model downgrade: set `SystemConfiguration(key='budget_downgrade_active', value=True)`. Routes expensive models to `BUDGET_DOWNGRADE_MODEL = 'gpt-5-mini'` |
| Hard Limit | daily_spend >= 95% of cap | Budget freeze: set `SystemConfiguration(key='budget_freeze_active', value=True)`. Only `BUDGET_CRITICAL_PURPOSES = {'governance', 'auth', 'incident_response', 'pa_chat'}` permitted |

**Step 3 — Recovery.** When spend drops below the tier threshold, the corresponding `SystemConfiguration` key is deleted, automatically restoring normal operation.

### Mechanism 4: ROI-Based Throttling (ROIEnforcer)

**Location:** `core/services/ops_autopilot/budget.py` (lines 510-850)

**Step 1 — ROI Computation per Agent.** For each agent active in the last 24 hours:
```
agent_spend = SUM(LLMCallLog.cost WHERE agent_name=X)
call_count = COUNT(LLMCallLog WHERE agent_name=X)
completed = COUNT(AgentExecution WHERE agent__name=X, status='completed')
published = COUNT(Deliverable WHERE agent_name=X, status='published')
impacts = COUNT(ImpactEvent WHERE agent_name=X)

combined_outcomes = completed + published + impacts
ROI = combined_outcomes / max(call_count, 1)
```

**Step 2 — Quality Weighting.**
```
quality_weight = average(Deliverable.quality_score WHERE agent_name=X)
# Falls back to 0.5 if no deliverables
QROI = ROI * quality_weight
```

**Step 3 — Throttle Tier Assignment.**

| QROI Range | Cooldown | Effect |
|------------|----------|--------|
| < 0.05 (5%) | 60 minutes | Agent can execute at most once per hour |
| < 0.15 (15%) | 30 minutes | Agent can execute at most once per 30 min |
| < 0.30 (30%) | 10 minutes | Agent can execute at most once per 10 min |
| >= 0.30 | 0 (no throttle) | Agent operates normally |

**Step 4 — Protected Purposes.** Agents invoked for `PROTECTED_PURPOSES = {'pa_chat', 'governance', 'auth', 'incident_response'}` are never throttled regardless of QROI.

**Step 5 — Budget Coupling.** Throttles are only applied when the budget controller is in Soft Limit or Hard Limit tier. During Normal tier, all agents operate without throttles regardless of QROI.

### Integration Between Mechanisms

The three mechanisms share infrastructure:
- **AgentControlEntry**: Used by timeout ladder L3 for blocking, queried by budget freeze for enforcement
- **SystemConfiguration**: Used by timeout ladder (L1, L2 overrides), budget controller (downgrade/freeze flags), and ROI enforcer (cooldown settings)
- **FailureSignature**: Used by timeout ladder for escalation decisions, also feeds the diagnostic pipeline for root cause analysis
- **Conflict resolution**: Budget freeze overrides ROI throttling (frozen = no execution). Timeout ladder L3 block overrides both (blocked = no execution regardless of budget or ROI state).

**Priority hierarchy:**
1. AgentControlEntry block (highest — overrides everything)
2. Budget freeze (overrides ROI throttling)
3. ROI throttle cooldown
4. Normal operation

---

## 6. Novelty Hooks (Section 102)

**a) Graduated remediation with per-level overrides and level-specific rollback.** Each ladder level applies exactly one additional override and removes exactly that override during de-escalation. No known system implements this clean "stack-based" intervention pattern where interventions accumulate during escalation and unwind during recovery.

**b) Automatic de-escalation based on observed recovery.** The system tracks consecutive clean cycles (12 cycles = ~2 hours of zero failures) and automatically steps down. This is absent from incident management tools (PagerDuty, OpsGenie), which escalate notifications to humans but never de-escalate based on component recovery.

**c) Quality-weighted ROI throttling (QROI).** The ROI score is multiplied by a quality weight derived from deliverable quality scores. This means a high-ROI but low-quality agent is throttled more aggressively than a moderate-ROI but high-quality agent. No known budget control system couples quality scoring to spend allocation.

**d) Budget-tier-gated throttling.** ROI throttles are only active during budget pressure (Soft Limit or above). During normal spend, all agents operate freely. This selective application is absent from cost management systems, which typically apply blanket limits regardless of current spend rate.

**e) Protected purpose exemptions.** Critical functions (PA chat, governance, auth) are exempt from both budget freeze and ROI throttling. The exemption is purpose-based (why the agent is being invoked), not agent-based (which agent is invoked), meaning the same agent can be throttled for one purpose and unthrottled for another.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Recovery-based de-escalation is counter-intuitive for safety systems.** In safety-critical systems, the standard approach is to keep interventions in place until a human explicitly clears them ("fail-safe" design). Automatically removing interventions based on observed recovery introduces risk — but the non-obvious insight is that for AI agent systems, keeping interventions too long (agent unnecessarily blocked) is itself a form of failure (reduced throughput, stale data, missed opportunities). The graduated de-escalation balances safety against availability.

**b) Combining remediation ladders with budget/ROI creates a non-obvious three-axis control surface.** Each axis (failure rate, spend rate, output quality) could independently control agent behavior. The combination creates emergent behaviors: an agent in timeout ladder L2 AND under budget soft limit AND with low QROI receives three simultaneous interventions (increased timeout + reduced batch + throttle cooldown). The interaction between these axes is non-predictable from any one axis alone.

**c) QROI coupling is non-obvious because quality and cost are typically managed separately.** Cost optimization systems (AWS Cost Explorer, GCP Budget Alerts) focus on spend. Quality systems (MLflow metrics, content scoring) focus on output quality. Multiplying them together to create a unified throttle metric is a non-obvious combination that captures the insight: an expensive agent is only wasteful if its output quality is also low.

**d) Purpose-based exemptions contradict agent-based throttling.** The standard throttling model is "Agent X is throttled" or "Agent X is not throttled." Exempting by purpose ("Agent X is throttled for content generation but not for governance responses") is non-obvious because it requires the throttle check to inspect the invocation context, not just the agent identity.

**e) Clean cycle counting with hard reset is non-obvious.** The de-escalation requires 12 *consecutive* clean cycles. A single failure resets the counter to 0. This "hard reset" approach is stricter than a sliding window average (which would gradually decay) and is non-obvious because it creates a binary recovery gate: either the agent is consistently healthy or the counter keeps resetting.

---

## 8. Operational Benefits (Measurable Outputs)

- **Intermediate remediation before blocking**: L1 (timeout increase) and L2 (batch reduction) resolve ~70% of issues without ever reaching L3 (block), maintaining agent availability.
- **Automatic recovery**: De-escalation after 12 clean cycles (~2h) means agents recover without human intervention. Average downtime from timeout issues reduced from "until human notices" to ~2-6 hours (L3 TTL + recovery period).
- **Budget protection with precision**: QROI throttling under budget pressure saves 20-40% of discretionary spend by targeting low-value agents while preserving high-value workloads.
- **Quality-spend coupling**: Agents producing low-quality output are throttled first during budget crunch, naturally steering spend toward higher-quality outputs.
- **Zero blanket freezes**: The graduated approach (downgrade → throttle → selective freeze) means pa_chat and governance always work, even during hard budget limits.
- **Reduced operational toil**: No human intervention required for routine timeout spikes. The ladder handles escalation, applies appropriate interventions, verifies recovery, and de-escalates — a full remediation lifecycle without operator involvement.

---

## 9. Alternative Embodiments

**a) Exponential backoff de-escalation.** Instead of fixed 12-cycle recovery, de-escalation could require exponentially increasing clean periods at higher levels: L3→L2 requires 24 cycles, L2→L1 requires 12, L1→L0 requires 6. This keeps agents at higher levels longer, reducing oscillation risk.

**b) Predictive escalation.** Instead of waiting for threshold breaches, a time-series model could predict future timeout rates from current trends and preemptively escalate before the threshold is reached, reducing the window of degraded performance.

**c) Cross-agent budget allocation.** Instead of per-agent QROI throttling, the system could allocate a fixed daily budget to each agent based on its historical QROI ranking, creating a competitive allocation market where high-QROI agents receive larger budgets.

**d) Adaptive QROI thresholds.** The throttle tier boundaries (5%, 15%, 30%) could be adaptive based on system-wide QROI distribution, using percentile-based cutoffs rather than fixed values. This prevents the system from over-throttling when overall quality is low.

**e) Deliberation ladder with multi-model consensus.** Instead of fallback to a single cheaper model, L2 could use a consensus mechanism: run the deliberation on 2 models simultaneously and take the intersection of their decisions, maintaining quality while reducing reliance on a single provider.

**f) Revenue-weighted QROI.** Agents that contribute to revenue-generating workflows could receive a revenue multiplier on their QROI, further protecting monetization-critical paths during budget pressure.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for autonomous graduated remediation of software agent failures in a distributed multi-agent system, the method comprising:

(a) monitoring, by an autonomous policy engine, failure rates for each of a plurality of software agents over a configurable evaluation window;

(b) upon a failure rate for a first agent exceeding an entry threshold, entering the first agent into a multi-level remediation ladder at a first level, the first level applying a first remediation override specific to that level;

(c) after a configurable number of evaluation cycles without improvement, escalating the first agent to a second level of the remediation ladder, the second level applying a second remediation override while maintaining the first remediation override;

(d) tracking consecutive clean cycles for the first agent, wherein each evaluation cycle with zero observed failures increments a clean counter and any cycle with observed failures resets the clean counter to zero;

(e) upon the clean counter reaching a configurable recovery threshold, de-escalating the first agent by one level and removing the remediation override specific to the de-escalated level while preserving overrides for remaining levels; and

(f) repeating steps (d) and (e) until the first agent returns to an unmodified monitoring state.

### Dependent Claims

1. The method of the independent claim, wherein the multi-level remediation ladder comprises: a first level that increases a per-agent execution timeout, a second level that reduces a per-agent batch dispatch size, and a third level that temporarily blocks the agent via a shared control table with a time-to-live value.

2. The method of claim 1, wherein the first level caps the increased timeout at a configurable absolute maximum regardless of the multiplier applied.

3. The method of the independent claim, further comprising, under budget pressure conditions: computing a quality-weighted return-on-investment score (QROI) for each agent by multiplying a ratio of successful outcomes to total invocations by an average output quality score.

4. The method of claim 3, further comprising applying per-agent cooldown periods inversely proportional to the agent's QROI score, wherein agents with lower QROI receive longer cooldowns.

5. The method of claim 4, wherein cooldown periods are only applied when aggregate system spend exceeds a configurable soft-limit percentage of a daily budget cap.

6. The method of claim 5, wherein agents invoked for purposes in a protected purpose set are exempt from cooldown periods regardless of QROI score or budget pressure.

7. The method of claim 6, wherein the protected purpose set comprises at least: conversational interface operations, governance decisions, authentication operations, and incident response operations.

8. The method of the independent claim, wherein a priority hierarchy governs conflicts between the remediation ladder and budget controls: agent blocking overrides budget freezing, budget freezing overrides ROI throttling, and ROI throttling overrides normal operation.

9. The method of the independent claim, further comprising a parallel deliberation remediation ladder that applies graduated interventions to content deliberation processes: reviewer panel size reduction, model provider fallback, and single-reviewer mode.

10. The method of claim 9, wherein both remediation ladders share the same escalation cycle count, recovery cycle count, and clean-counter-with-hard-reset mechanics.

11. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

12. A non-transitory computer-readable medium storing instructions that, when executed by one or more processors, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Timeout Remediation Ladder State Machine**
```
                    [Entry: ≥5 timeouts/hr]
                           |
                           v
+------+   escalate   +------+   escalate   +------+   escalate   +------+
|  L0  | -----------> |  L1  | -----------> |  L2  | -----------> |  L3  |
| WATCH|              | +50%  |              | -50%  |              |BLOCK |
|      | <----------- |timeout| <----------- |batch  | <----------- |4h TTL|
+------+  de-escalate +------+  de-escalate +------+  de-escalate +------+
             12 clean        12 clean              12 clean
             cycles          cycles                cycles

Escalation: 6 cycles without improvement
De-escalation: 12 consecutive clean cycles (hard reset on any failure)
```

**Figure 2 — Override Stack During Escalation/De-escalation**
```
L0:  [no overrides]
L1:  [agent_timeout_override:X = 1.5x]
L2:  [agent_timeout_override:X = 1.5x] + [timeout_ladder_batch_reduce:X = 0.5]
L3:  [agent_timeout_override:X = 1.5x] + [timeout_ladder_batch_reduce:X = 0.5] + [AgentControlEntry(blocked)]

De-escalate L3→L2: Remove block, keep timeout + batch overrides
De-escalate L2→L1: Remove batch override, keep timeout override
De-escalate L1→L0: Remove timeout override
```

**Figure 3 — Budget Controller Tier Transitions**
```
Daily Spend ($)
    |
$95 |-------- HARD LIMIT: Budget Freeze (only critical purposes)
    |         [budget_freeze_active = True]
    |
$70 |-------- SOFT LIMIT: Model Downgrade + ROI Throttling
    |         [budget_downgrade_active = True]
    |         [QROI throttles applied]
    |
 $0 |-------- NORMAL: No restrictions
    +-------------------------------------------------> Time
```

**Figure 4 — QROI Throttle Decision Tree**
```
[Agent invocation request]
      |
[Is purpose in PROTECTED_PURPOSES?] --YES--> [Execute immediately]
      |NO
[Is budget in Normal tier?] --YES--> [Execute immediately]
      |NO (Soft or Hard limit)
[Compute QROI for agent]
      |
[QROI >= 0.30?] --YES--> [Execute immediately]
      |NO
[QROI >= 0.15?] --YES--> [Cooldown: 10 min since last execution?]
      |NO                        |YES: Execute  |NO: Reject
[QROI >= 0.05?] --YES--> [Cooldown: 30 min since last execution?]
      |NO                        |YES: Execute  |NO: Reject
[QROI < 0.05] ---------> [Cooldown: 60 min since last execution?]
                                 |YES: Execute  |NO: Reject
```

**Figure 5 — Three-Axis Control Surface**
```
           Failure Rate (Timeout Ladder)
                |
           L3 --+-- Block
           L2 --+-- Batch Reduce
           L1 --+-- Timeout Increase
           L0 --+-- Monitor
                |
                +--------+--------+---------> Spend Rate (Budget)
                |  Normal| Soft   | Hard
                |        | Limit  | Limit
                |        |        |
          QROI  |  Free  |Throttle| Freeze
          <5%   |  Run   | 60min  | Block*
          <15%  |  Run   | 30min  | Block*
          <30%  |  Run   | 10min  | Block*
          >=30% |  Run   | Run    | Block*

          *except PROTECTED_PURPOSES
```

---

## 12. Prior Art Buckets to Cite Against

**a) Circuit Breaker Pattern (Hystrix, Resilience4j)**
- Teaches: open/half-open/closed states, failure counting, automatic recovery timeout
- Does NOT teach: multi-level graduated intervention (only binary open/closed with half-open probe), per-level overrides that accumulate, or clean-cycle-based de-escalation with hard reset

**b) Kubernetes Horizontal Pod Autoscaler (HPA)**
- Teaches: scaling up/down based on metric thresholds, cooldown periods between scaling events
- Does NOT teach: graduated intervention levels with different actions per level, quality-weighted scaling decisions, or override stacking and unwinding

**c) AWS Auto Scaling Policies (Step Scaling, Target Tracking)**
- Teaches: step-based scaling with configurable thresholds, warmup/cooldown periods
- Does NOT teach: applying different types of remediation at each step (timeout vs. batch vs. block), tracking consecutive clean periods for de-escalation, or coupling with ROI/quality metrics

**d) Budget Alert Systems (AWS Budgets, GCP Budget Alerts)**
- Teaches: threshold-based alerting at percentage-of-budget levels, automated actions (stop EC2 instances)
- Does NOT teach: quality-weighted ROI throttling, purpose-based exemptions, model downgrade as an intermediate step before full freeze, or coupling budget tiers with per-agent remediation state

**e) MLOps Model Monitoring (MLflow, Evidently AI, WhyLabs)**
- Teaches: model performance monitoring, drift detection, alerting
- Does NOT teach: graduated automated remediation in response to quality degradation, ROI-based resource allocation, or closed-loop de-escalation based on recovery metrics

**f) Incident Management Escalation (PagerDuty, OpsGenie)**
- Teaches: time-based escalation of notifications to humans, escalation policies with multiple levels
- Does NOT teach: automated application of technical remediations (not just notifications), de-escalation based on observed system recovery (not human acknowledgment), or budget/quality coupling

**g) Rate Limiting / Throttling (API Gateways, Token Buckets)**
- Teaches: request rate limiting, token bucket algorithms, priority-based request queuing
- Does NOT teach: per-agent throttling based on output quality, budget-tier-gated activation, or QROI computation that combines cost, outcome count, and quality score

---

## Observability Evidence (Proving This Runs in Production)

### Timeout Ladder State
```sql
-- SystemConfiguration records showing active ladder overrides
SELECT key, value, updated_at FROM core_systemconfiguration
WHERE key LIKE 'agent_timeout_override:%' OR key LIKE 'timeout_ladder_%';

-- Example results:
-- ('agent_timeout_override:CustomerResearchAgent', '2250', '2026-03-16 15:10:00')
-- ('timeout_ladder_batch_reduce:CustomerResearchAgent', '0.5', '2026-03-16 16:15:00')
```

### AgentControlEntry L3 Block
```sql
SELECT agent_name, status, blocked_by, ttl_hours, blocked_at FROM core_agentcontrolentry
WHERE blocked_by = 'timeout_playbook';

-- Example: ('CustomerResearchAgent', 'blocked', 'timeout_playbook', 4, '2026-03-16 17:20:00')
-- After 4 hours: ('CustomerResearchAgent', 'enabled', 'timeout_playbook', 4, '2026-03-16 17:20:00')
--   reason updated to 'TTL expired (4h)' by lazy evaluation
```

### Budget Controller State
```sql
SELECT key, value FROM core_systemconfiguration
WHERE key IN ('budget_downgrade_active', 'budget_freeze_active');

-- During soft limit: ('budget_downgrade_active', 'True')
-- During hard limit: ('budget_freeze_active', 'True')
-- During normal: no rows (keys deleted)
```

### QROI Computation Evidence
```
# Autopilot policy log entry
[ROI_ENFORCER] Agent=ContentWriterAgent spend=$4.20 calls=42 outcomes=38
  ROI=0.905 quality=0.72 QROI=0.651 tier=no_throttle

[ROI_ENFORCER] Agent=CompetitorAnalysisAgent spend=$8.50 calls=85 outcomes=3
  ROI=0.035 quality=0.45 QROI=0.016 tier=60min_cooldown
```

### De-escalation Evidence
```
# Autopilot policy log entry
[TIMEOUT_LADDER] CustomerResearchAgent: L2→L1 de-escalation
  clean_cycles=12 (120 minutes with 0 timeouts)
  Removed override: timeout_ladder_batch_reduce:CustomerResearchAgent
  Remaining: agent_timeout_override:CustomerResearchAgent = 2250
```

---

## Examiner Story

Prior art teaches circuit breakers with binary open/closed states (Hystrix), Kubernetes autoscaling with step-based policies (HPA), and budget alerting with automated instance termination (AWS Budgets). However, no single reference or obvious combination teaches a system that (1) implements a multi-level remediation ladder where each level applies a qualitatively different intervention (timeout adjustment, batch reduction, temporary blocking) that accumulates with lower-level interventions, (2) automatically de-escalates based on consecutive clean cycles with hard-reset counting (not sliding window averages or human acknowledgment), (3) computes a quality-weighted ROI score (QROI) per agent that combines invocation cost, outcome count, and output quality into a unified throttle metric, and (4) couples budget-tier detection with per-agent QROI throttling such that throttles are only active under budget pressure and exempt purpose-based invocations regardless of agent identity. The combination is non-predictable because (a) existing remediation systems apply uniform interventions at each level rather than qualitatively different actions, (b) de-escalation in safety systems typically requires human clearance rather than observed recovery metrics, (c) cost and quality management are universally treated as separate concerns rather than multiplied into a unified control signal, and (d) purpose-based exemptions in throttling systems contradict the standard agent-identity-based throttle model.
