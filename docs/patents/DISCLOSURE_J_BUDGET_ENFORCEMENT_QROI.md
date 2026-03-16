# Invention Disclosure J: Multi-Tier Budget Enforcement with Model Downgrade Routing and Quality-Weighted ROI Throttling

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Three-Tier Autonomous Budget Enforcement for LLM-Powered Systems with Model Downgrade Routing, Purpose-Based Exemptions, and Quality-Weighted ROI Agent Throttling

---

## 2. Field / Technical Domain

Cost management for autonomous AI platforms running multiple LLM providers. Specifically, methods for enforcing budget limits through graduated tiers (model downgrade → budget freeze), computing per-agent quality-weighted ROI to selectively throttle low-value agents while protecting critical functions, and tracking per-call cost with attribution to agents, desks, and system objectives.

---

## 3. Problem

**a) LLM spend is unbounded without per-call controls.** Autonomous agents making hundreds of LLM calls per hour can exceed daily budget caps before human operators notice.

**b) Blanket budget freezes block critical functions.** Freezing all LLM calls when budget is exceeded blocks PA chat, governance decisions, and incident response — the exact functions needed when the system is under stress.

**c) ROI varies dramatically between agents.** Some agents produce high-value outputs (published content, revenue) at low cost; others consume significant budget with negligible output. Treating all agents equally wastes budget.

**d) Quality and cost are managed separately.** An agent with high ROI but low-quality output appears efficient but produces work that must be revised. Cost management that ignores quality optimizes for the wrong outcome.

---

## 4. Solution Summary

A three-layer budget system:

1. **Three-Tier Budget Enforcement**: Normal (0-70% of daily cap, no restrictions) → Soft Limit (70%, model downgrade to cheaper provider) → Hard Limit (95%, freeze all non-critical calls). Recovery is automatic when spend drops below thresholds.

2. **Quality-Weighted ROI Throttling (QROI)**: Per-agent QROI = (outcome_count / call_count) × quality_weight. Low-QROI agents receive graduated cooldowns (60min / 30min / 10min). Protected purposes (PA chat, governance, auth) are never throttled. Throttles only active during budget pressure.

3. **Per-Call Cost Tracking**: Every LLM call logged to `LLMCallLog` with agent_name, provider, model, tokens, cost, latency. Enables real-time spend aggregation, top-spender identification, and attribution to system objectives.

---

## 5. As-Built Mechanism

### Component 1: Three-Tier Budget Controller

**File:** `core/services/ops_autopilot/budget.py` (lines 238-506)

**Spend Computation** (lines 253-308): Queries `LLMCallLog` for hourly and daily spend via SQL aggregation (`Sum('cost')`, `Count('id')`). Also computes top 10 agents and top 10 models by cost.

**Tier Transitions:**

| Tier | Condition | Action | SystemConfiguration Key |
|------|-----------|--------|------------------------|
| Normal | daily < 70% of $100 cap | No restrictions; clear any active flags | Delete `budget_downgrade_active`, `budget_freeze_active` |
| Soft Limit | daily >= 70% | Model downgrade: route non-critical calls to `gpt-5-mini` | Set `budget_downgrade_active=True` |
| Hard Limit | daily >= 95% | Budget freeze: block all non-critical LLM calls | Set `budget_freeze_active=True` |

**Critical Purposes (never blocked/downgraded):**
```python
BUDGET_CRITICAL_PURPOSES = {'governance', 'auth', 'incident_response', 'pa_chat'}
```

**LLM Enforcer Integration** (`core/llm_enforcer.py` lines 126-214):
- Line 151: Check `budget_freeze_active` → block if not critical
- Line 173: Check `budget_downgrade_active` → route to cheaper model
- Line 191: Check ROI throttle → block if on cooldown
- Line 232: Execute LLM call with effective model
- Line 627: Log to `LLMCallLog` with all metadata

**Recovery:** `clear_budget_flags()` (lines 438-461) deletes SystemConfiguration keys when spend returns below soft limit threshold.

### Component 2: Quality-Weighted ROI Enforcer

**File:** `core/services/ops_autopilot/budget.py` (lines 510-975)

**QROI Computation** (lines 709-763):
```
For each active agent (24h window):
  agent_spend = SUM(LLMCallLog.cost)
  call_count = COUNT(LLMCallLog)
  completed = COUNT(AgentExecution WHERE status='completed')
  published = COUNT(Deliverable WHERE status='published')
  impacts = COUNT(ImpactEvent)

  combined_outcomes = completed + published + impacts
  ROI = combined_outcomes / max(call_count, 1)

  quality_weight = average(Deliverable.quality_score)  # 0-1
                   OR content pipeline avg quality
                   OR impact rate
                   OR execution success rate
                   fallback: 0.5

  QROI = ROI × quality_weight
```

**Throttle Tiers** (lines 530-534):

| QROI Range | Cooldown | Meaning |
|------------|----------|---------|
| < 0.05 (5%) | 60 min | Very low value — execute at most once per hour |
| < 0.15 (15%) | 30 min | Low value — at most once per 30 min |
| < 0.30 (30%) | 10 min | Below average — at most once per 10 min |
| >= 0.30 | 0 | Normal operation |

**Protected Purposes** (lines 524-527):
```python
PROTECTED_PURPOSES = frozenset({
    'pa_chat', 'personalassistant', 'unifiedpa',
    'governance', 'auth', 'incident_response',
})
```

**Throttle Storage** (lines 841-907): Stored as `SystemConfiguration` records:
```
key: roi_throttle:{agent_name}
value: {cooldown_minutes, roi, qroi, quality_weight, expires_at, set_at}
```

Expired throttles cleaned up on each check cycle.

**Budget Coupling:** Throttles only applied when `budget_downgrade_active` or `budget_freeze_active` is set. During normal budget tier, all agents operate freely regardless of QROI.

### Component 3: Per-Call Cost Tracking

**Model:** `LLMCallLog` (`core/models_llm_routing.py` lines 297-362)

| Field | Type | Purpose |
|-------|------|---------|
| agent_name | CharField(indexed) | Which agent made the call |
| provider | CharField | openai, anthropic, etc. |
| model_id | CharField | gpt-5.2, claude-sonnet-4, etc. |
| task_type | CharField | embedding, chat, completion |
| prompt_tokens | IntegerField | Input tokens |
| completion_tokens | IntegerField | Output tokens |
| cost | DecimalField(10,6) | USD cost per call |
| latency_ms | IntegerField | Response time |
| success | BooleanField | Did call succeed |
| trace_id | CharField(indexed) | Correlation ID |
| created_at | DateTimeField(indexed) | When call was made |

**Indexes:** (agent_name, -created_at), (provider, model_id, -created_at), (-created_at), (success, -created_at)

**Population:** Every LLM call via `LLMEnforcer._save_cost_tracking()` (line 627-666).

---

## 6. Novelty Hooks (Section 102)

**a) Model downgrade as an intermediate budget tier.** Between "no restrictions" and "full freeze," the system routes to a cheaper model. No known LLM cost system implements automated model downgrade as a budget response.

**b) QROI = ROI × quality_weight multiplies cost efficiency by output quality.** Separating ROI (volume efficiency) from quality (output merit) and multiplying them creates a metric where an agent must be both cost-efficient AND produce quality output to avoid throttling. No known system uses this multiplicative quality-cost metric.

**c) Purpose-based exemptions apply to the same agent for different invocations.** The same agent throttled for content generation is unthrottled when invoked for governance. Exemption is by purpose, not by identity.

**d) Budget-tier-gated throttling means QROI throttles are dormant during normal spend.** Throttles activate only under budget pressure. During normal operation, even low-QROI agents run freely. This selective activation is absent from cost management systems.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Model downgrade as a budget response is non-obvious.** The standard response to budget pressure is either alert-and-wait (human decides) or blanket freeze. Automatically routing to a cheaper model is non-obvious because it requires confidence that the cheaper model produces acceptable output — which the QROI system provides.

**b) Multiplicative QROI is non-obvious because cost and quality are traditionally separate metrics.** CFOs track cost; quality teams track quality. Multiplying them creates a unified metric that is non-obvious because the interaction between cost efficiency and output quality is non-linear.

**c) Dormant throttles that activate under pressure is non-obvious.** The standard design is: if you compute a throttle, apply it always. Gating throttle application on budget tier is non-obvious because it means the same QROI score produces different behavior depending on external spend conditions.

---

## 8. Operational Benefits

- **No blanket freezes:** Critical functions (PA, governance) always work
- **Graduated response:** Model downgrade reduces cost ~60% before freezing
- **Precision throttling:** Low-QROI agents throttled first, high-QROI preserved
- **Automatic recovery:** Spend drops → flags cleared → normal operation resumes
- **Per-call attribution:** Every dollar traced to agent + provider + model

---

## 9. Alternative Embodiments

**a) Dynamic budget caps per desk.** Instead of a global daily cap, each desk (sports, content, research) could have its own budget derived from its IQROI.

**b) Predictive budget management.** ML model predicts end-of-day spend from current trajectory, triggering early downgrade.

**c) Cost-per-outcome tracking.** Instead of cost-per-call, track cost-per-published-blog or cost-per-revenue-dollar for more business-aligned metrics.

**d) Multi-provider arbitrage.** Under budget pressure, route to whichever provider offers lowest cost for acceptable quality (compare OpenAI vs Anthropic vs Together AI pricing in real-time).

**e) User-specific budget pools.** Each user could have a personal budget allocation with their own soft/hard limits.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for managing LLM expenditure in an autonomous multi-agent system, the method comprising:

(a) tracking, for each LLM API call, the calling agent, provider, model, token counts, and cost in a per-call cost log;

(b) computing aggregate spend over configurable time windows by querying the cost log;

(c) upon aggregate spend exceeding a first threshold, automatically routing non-critical LLM calls to a cheaper model while maintaining the original model for calls designated as critical purposes;

(d) upon aggregate spend exceeding a second, higher threshold, blocking all LLM calls except those designated as critical purposes;

(e) computing, for each agent, a quality-weighted return-on-investment score (QROI) by multiplying a ratio of successful outcomes to total API calls by an average output quality score;

(f) applying graduated cooldown periods to agents based on their QROI score, wherein agents with lower QROI receive longer cooldowns; and

(g) activating the cooldown periods of step (f) only when aggregate spend exceeds the first threshold, and deactivating the cooldown periods when spend returns below the first threshold.

### Dependent Claims

1. Wherein the critical purposes comprise conversational interface operations, governance decisions, authentication, and incident response.

2. Wherein the quality weight is derived from deliverable quality scores, content pipeline metrics, impact rates, or execution success rates, with a neutral default when no quality data is available.

3. Wherein the graduated cooldown periods comprise at least three tiers: a first tier of 60 minutes for QROI below 5%, a second tier of 30 minutes for QROI below 15%, and a third tier of 10 minutes for QROI below 30%.

4. Wherein the cooldown periods are stored as configuration records with expiry timestamps and automatically cleaned up upon expiration.

5. Wherein aggregate spend computation includes both hourly and daily windows, and either window exceeding its respective threshold triggers the corresponding budget tier.

6. Wherein the automatic routing of step (c) is implemented by setting a flag in a shared configuration store that is checked by an LLM enforcer module prior to each API call.

7. Further comprising automatic recovery wherein, when aggregate spend drops below the first threshold, the model downgrade and cooldown flags are automatically cleared.

8. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Three-Tier Budget Enforcement**
```
Daily Spend ($)
    |
$95 |═══════ HARD LIMIT: Freeze (only critical purposes)
    |         budget_freeze_active = True
$70 |─────── SOFT LIMIT: Model downgrade + QROI throttles
    |         budget_downgrade_active = True
    |         QROI cooldowns activated
 $0 |         NORMAL: No restrictions
    +──────────────────────────────────────→ Time
```

**Figure 2 — QROI Computation and Throttle Assignment**
```
[LLMCallLog] → agent_spend, call_count
[AgentExecution] → completed_outcomes
[Deliverable] → published + quality_score
[ImpactEvent] → impact_count

ROI = outcomes / calls
quality_weight = avg(quality_score) or fallback 0.5
QROI = ROI × quality_weight

QROI < 0.05 → 60min cooldown
QROI < 0.15 → 30min cooldown
QROI < 0.30 → 10min cooldown
QROI >= 0.30 → no throttle
```

---

## 12. Prior Art Buckets

**a) Cloud Cost Management (AWS Cost Explorer, GCP Budget Alerts)** — Teaches spend alerting and automated instance termination but not model downgrade routing or quality-weighted agent throttling.

**b) API Rate Limiting (Token Bucket, Leaky Bucket)** — Teaches request-level rate limiting but not per-agent ROI-based throttling or budget-tier-gated activation.

**c) LLM Cost Optimization (LiteLLM, Router)** — Teaches model routing for cost but not graduated budget tiers with automatic recovery or QROI-based per-agent throttling.

**d) FinOps Platforms (Kubecost, CloudHealth)** — Teaches resource cost attribution but not quality-weighted ROI computation or purpose-based exemptions.

---

## Examiner Story

Prior art teaches cloud cost alerting (AWS Budgets), API rate limiting (token buckets), and LLM model routing for cost optimization (LiteLLM). However, no single reference teaches a system that (1) implements three graduated budget tiers where the intermediate tier routes to a cheaper model rather than freezing, (2) computes per-agent QROI by multiplying cost efficiency by output quality to create a unified throttle metric, (3) applies QROI-based cooldowns only during budget pressure and deactivates them during normal spend, and (4) exempts critical purposes (not critical agents) from all budget restrictions. The combination is non-predictable because cost systems treat all calls equally, quality systems don't influence cost decisions, and budget responses are typically binary (alert or freeze) rather than graduated with intermediate model-switching.
