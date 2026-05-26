---
title: "Invention Disclosure K: Budget-Aware Task Scheduling with Tier Classification, Knob-Based Downscoping, and Attribution Debt Control"
kind: invention_disclosure
disclosure_id: K
workstream: WS4 (Budget Enforcement + Experimentation)
status: draft (Attorney Review Pending)
last_updated: 2026-03-16
originating_session: pre-session-tracking (March 16, 2026 batch)
inventor: Chris West (DonkeyKing)
provenance_confidence: HIGH
provenance_note: One of 12 invention disclosures drafted as a single March 16, 2026 batch. Frontmatter added Session 1160 (2026-05-26) as part of the patents preservation pass; body content unchanged from original draft. See `docs/patents/README.md` for workstream organization and narrative cross-link map.
maps_to_narratives:
  - docs/narratives/WORKERS_AND_INFRASTRUCTURE.md
companion_docs:
  - docs/patents/README.md
  - docs/patents/EXECUTIVE_SUMMARY_WS4.md
---

# Invention Disclosure K: Budget-Aware Task Scheduling with Tier Classification, Knob-Based Downscoping, and Attribution Debt Control

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Budget-Pressure-Adaptive Task Scheduling with Three-Tier Task Classification, Per-Task Knob-Based Downscoping, and Attribution Debt-Gated Portfolio Reallocation

---

## 2. Field / Technical Domain

Autonomous task scheduling for cost-constrained AI platforms. Specifically, methods for classifying scheduled tasks by LLM cost tier, making per-task preflight decisions (proceed/downscope/defer) based on current budget pressure, applying per-task parameter knobs to reduce resource consumption without cancellation, and gating portfolio budget reallocation on attribution debt thresholds.

---

## 3. Problem

**a) Scheduled tasks don't adapt to budget pressure.** Celery Beat dispatches tasks on fixed schedules regardless of current spend. A content generation task consuming $2 per run dispatches even when the daily budget is 95% consumed.

**b) Task cancellation is too coarse.** Deferring an entire task loses all its value. A blog generation task could run with fewer reviewers instead of not running at all.

**c) Budget reallocation between desks is unreliable without attribution.** If 40% of spend can't be attributed to a desk, reallocating budget between desks based on performance creates instability.

---

## 4. Solution Summary

1. **Task Tier Classification**: Tasks classified into Tier 1 (no/minimal LLM, always runs), Tier 2 (moderate LLM/embedding, downscoped under pressure), Tier 3 (heavy LLM, deferred under pressure).

2. **Preflight Decision**: Before expensive task execution, `BudgetAwareScheduler.preflight()` checks current budget utilization and returns proceed/downscope/defer with task-specific knob values.

3. **Knob-Based Downscoping**: Instead of cancellation, reduce task parameters: fewer reviewers (3→1), smaller batch sizes (100→10), shorter lookback windows. Knobs stored in SystemConfiguration for runtime adjustment.

4. **Attribution Debt Control**: Track unattributed spend (agents without desk mapping). When debt > 40%, block portfolio reallocation. When debt > 20%, reduce EWMA smoothing sensitivity to prevent unstable allocations.

---

## 5. As-Built Mechanism

### Component 1: Task Tier Classification

**File:** `core/services/ops_autopilot/budget.py` (lines 998-1033)

| Tier | LLM Usage | Budget Behavior | Example Tasks |
|------|-----------|----------------|---------------|
| **Tier 3** (Heavy) | Full LLM generation + review | Defer under pressure | `generate_self_blog_deliberation_task`, `content_autonomy_loop`, `auto_enhance_blogs` (7 tasks) |
| **Tier 2** (Moderate) | Embeddings, enrichment, predictions | Downscope under pressure | `backfill_spider_embeddings`, `enrich_boardroom_ml_predictions`, `generate_game_predictions` (14 tasks) |
| **Tier 1** (Minimal) | DB queries, API polling, scoring | Always proceeds | `run_spider_network`, `process_core_spider_data`, `update_game_scores` (8 tasks) |

### Component 2: Preflight Decision Engine

**Method:** `BudgetAwareScheduler.preflight(task_name)` (lines 1074-1178)

```
1. Get current budget utilization from BudgetController
2. Classify task into tier (Tier 1/2/3)
3. Determine pressure level:
   - Normal (< 70%): All tiers proceed with normal knobs
   - Pressured (70-95%): Tier 3 deferred, Tier 2 downscoped, Tier 1 proceeds
   - Critical (>= 95%): Tier 3 deferred, Tier 2 deferred or heavy downscope, Tier 1 proceeds

Return: {
    'decision': 'proceed' | 'downscope' | 'defer',
    'pressure': 'normal' | 'pressured' | 'critical',
    'knobs': {param: value, ...},  # Task-specific parameters
    'reason': 'Budget at 78% — downscoping Tier 2 task'
}
```

### Component 3: Per-Task Knob Definitions

**File:** `core/services/ops_autopilot/budget.py` (lines 1035-1059)

```python
DOWNSCOPE_KNOBS = {
    'core.tasks.generate_self_blog_deliberation_task': {
        'max_reviewers': {'normal': 3, 'pressured': 1, 'critical': 0},
        'max_topics': {'normal': 3, 'pressured': 1, 'critical': 0},
    },
    'core.tasks.backfill_spider_embeddings': {
        'batch_size': {'normal': 100, 'pressured': 30, 'critical': 10},
    },
    'core.tasks.auto_enhance_blogs': {
        'max_blogs': {'normal': 5, 'pressured': 2, 'critical': 0},
    },
    'core.tasks.enrich_boardroom_ml_predictions': {
        'batch_size': {'normal': 50, 'pressured': 15, 'critical': 5},
    },
}
```

**Storage:** Applied knobs written to `SystemConfiguration` as `scheduler_knob:{task_name}:{param}`. Tasks read these knobs at execution time.

**Deferable Tasks** (lines 1062-1072): 9 tasks that can be safely deferred:
```python
DEFERABLE = frozenset({
    'core.tasks.generate_self_blog_deliberation_task',
    'core.tasks.content_autonomy_loop',
    'core.tasks.auto_enhance_blogs',
    # ... 6 more
})
```

### Component 4: Attribution Debt Controller

**File:** `core/services/ops_autopilot/impact.py` (lines 1409-1684)

**Agent-to-Desk Mapping** (lines 1427-1502): ~50 agents statically mapped to desks (sports, content, research, career, trading, general). Unmapped agents create attribution debt.

**Debt Computation** (lines 1535-1613):
```
total_spend = SUM(LLMCallLog.cost WHERE created_at >= 24h ago)
attributed_spend = SUM(cost WHERE agent_name in AGENT_DESK_MAP)
unattributed_spend = total_spend - attributed_spend
debt_pct = unattributed_spend / total_spend × 100
```

**Debt Thresholds:**

| Debt % | Effect |
|--------|--------|
| < 20% | Normal operation, EWMA alpha = 0.3 |
| 20-40% | Reduced EWMA alpha = 0.15 (conservative smoothing) |
| > 40% | Block portfolio reallocation entirely |

**Reallocation Blocking** (lines 1615-1624):
```python
def should_block_reallocation(self, debt_report: dict) -> bool:
    return (debt_report['debt_pct'] > DEBT_CRITICAL_PCT
            and debt_report['unattributed_spend'] > DEBT_USD_FLOOR)
```

### Component 5: Portfolio Allocator with Goal-Aware Multipliers

**File:** `core/services/ops_autopilot/impact.py` (lines 509-1056)

**IQROI Computation** (lines 664-673):
```
IQROI = (impact_USD + impact_points × $0.10) / cost_USD
```

**IQROI → Allocation:**

| IQROI | Allocation Multiplier |
|-------|----------------------|
| >= 2.0 | 1.5x (boost) |
| >= 1.0 | 1.2x |
| >= 0.5 | 1.0x (neutral) |
| >= 0.1 | 0.7x (throttle) |
| < 0.1 | 0.5x (minimum) |

**EWMA Smoothing** (lines 675-683):
```
allocation = 0.3 × raw_allocation + 0.7 × prior_allocation
```
When attribution debt > 20%, alpha reduced from 0.3 to 0.15 (more conservative, slower changes).

**Goal-Aware Multipliers** (lines 807-1056):

5 system objectives with configurable weights:
```python
DEFAULT_WEIGHTS = {
    'sports_profit': 0.25,
    'confirmed_revenue': 0.25,
    'content_engagement': 0.20,
    'quality': 0.15,
    'freshness': 0.15,
}
```

Each desk maps to relevant objectives. Desk utility = weighted sum of objective contributions. Final multiplier = `0.75 + 0.50 × utility` (range 0.75x-1.25x).

---

## 6. Novelty Hooks (Section 102)

**a) Per-task knob-based downscoping.** Instead of cancel/proceed binary, tasks receive adjusted parameters (fewer reviewers, smaller batches). Each task has its own knob definitions with values per pressure level. No known scheduler adjusts individual task parameters based on budget pressure.

**b) Three-tier task classification by LLM cost.** Tasks classified by their expected LLM consumption, enabling proportional response: heavy tasks deferred first, moderate tasks downscoped, lightweight tasks always proceed.

**c) Attribution debt gating portfolio reallocation.** When > 40% of spend can't be attributed to a desk, the system blocks budget reallocation to prevent unstable allocations based on incomplete data.

**d) EWMA sensitivity reduction under attribution debt.** When debt > 20%, the EWMA smoothing factor is reduced from 0.3 to 0.15, making allocations change more slowly. This prevents budget oscillation when attribution is unreliable.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Downscoping is non-obvious because it requires per-task parameter knowledge.** Generic schedulers don't know which parameters to reduce. The insight: content generation has reviewers (reduce 3→1), embeddings have batch sizes (reduce 100→10), and blogs have limits (reduce 5→2). This domain-specific knowledge enables graceful degradation.

**b) Attribution debt as a reallocation gate is non-obvious.** The standard approach is to reallocate based on performance regardless of attribution completeness. The insight: reallocating based on 60% of data is worse than not reallocating, because the missing 40% might disproportionately belong to the best-performing desk.

**c) EWMA sensitivity adaptation based on data quality is non-obvious.** EWMA smoothing typically uses a fixed alpha. Reducing alpha when data quality (attribution completeness) decreases is a cross-domain transfer from signal processing (reduce filter responsiveness under noise).

---

## 8. Operational Benefits

- **Graceful degradation:** Content still generates under budget pressure, just with fewer reviewers
- **Tier 1 protection:** Spider collection, health checks, scoring always run
- **Stable allocations:** Attribution debt prevents budget oscillation from incomplete data
- **Runtime adjustable:** Knobs stored in SystemConfiguration, tunable without deploy

---

## 9. Alternative Embodiments

**a) ML-predicted task cost.** Instead of static tier classification, predict per-task cost from historical LLMCallLog data.

**b) Continuous knob interpolation.** Instead of discrete pressure levels (normal/pressured/critical), interpolate knob values linearly based on exact utilization percentage.

**c) Agent-level budget pools.** Each agent receives a daily budget allocation proportional to its IQROI, with independent soft/hard limits.

**d) Feedback from downscoped execution.** Track quality of output produced with downscoped parameters; if quality drops below threshold, promote task back to normal knobs even under pressure.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for budget-adaptive task scheduling in an autonomous AI system, the method comprising:

(a) classifying each scheduled task into one of a plurality of cost tiers based on expected resource consumption;

(b) prior to executing each task, querying current budget utilization from a cost tracking log;

(c) based on the budget utilization and the task's cost tier, making a preflight decision selected from: proceed with normal parameters, proceed with downscoped parameters, or defer execution;

(d) when the preflight decision is to downscope, applying task-specific parameter adjustments stored in a configuration store, the adjustments reducing resource consumption without cancelling the task; and

(e) tracking attribution of expenditure to organizational units, and gating budget reallocation between units on attribution completeness exceeding a configurable threshold.

### Dependent Claims

1. Wherein the cost tiers comprise: a first tier for tasks with no or minimal LLM usage that always proceed, a second tier for tasks with moderate usage that are downscoped under pressure, and a third tier for tasks with heavy usage that are deferred under pressure.

2. Wherein the task-specific parameter adjustments comprise reducing reviewer panel sizes, batch processing sizes, or concurrent execution limits.

3. Wherein the parameter adjustments have different values for each budget pressure level: normal, pressured, and critical.

4. Wherein the attribution threshold for gating reallocation is 60% attributed spend, and when attribution falls between 60-80%, a smoothing factor for allocation changes is reduced to prevent oscillation.

5. Further comprising computing a per-unit impact-quality ROI (IQROI) and mapping IQROI to allocation multipliers ranging from 0.5x to 1.5x.

6. Further comprising a goal-aware allocation layer that weights each organizational unit's allocation based on its contribution to configurable system objectives.

7. Wherein the EWMA smoothing factor for allocation changes is adaptively reduced when attribution debt exceeds a warning threshold.

8. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Preflight Decision Matrix**
```
               | Tier 1 (Light) | Tier 2 (Moderate) | Tier 3 (Heavy) |
Normal (<70%)  | Proceed         | Proceed            | Proceed         |
Pressured(70%) | Proceed         | Downscope          | Defer           |
Critical (95%) | Proceed         | Defer/Heavy DS     | Defer           |
```

**Figure 2 — Attribution Debt Control**
```
Total Spend: $80/day
Attributed: $52 (65%) → Desks know their spend
Unattributed: $28 (35%) → No desk mapping

Debt = 35%
  → Between 20-40%: Reduce EWMA alpha 0.3→0.15
  → Allocations change 50% slower
  → Prevents unstable reallocation
```

---

## 12. Prior Art Buckets

**a) Job Schedulers (Kubernetes CronJob, Airflow)** — Teaches scheduled task execution but not budget-adaptive preflight decisions or per-task parameter downscoping.

**b) Resource Managers (YARN, Mesos)** — Teaches resource allocation and quotas but not LLM-cost-tier classification or knob-based degradation.

**c) FinOps (Kubecost, Spot.io)** — Teaches cost attribution and optimization but not real-time preflight decisions or attribution-debt-gated reallocation.

---

## Examiner Story

Prior art teaches scheduled task execution (Kubernetes CronJob), resource allocation with quotas (YARN), and cloud cost attribution (Kubecost). However, no single reference teaches a system that (1) classifies tasks by LLM cost tier and makes per-task preflight decisions based on real-time budget pressure, (2) applies task-specific parameter knobs to reduce resource consumption without cancellation, (3) tracks attribution of expenditure to organizational units and gates reallocation on attribution completeness, and (4) adaptively reduces EWMA smoothing sensitivity when attribution data quality degrades. The combination is non-predictable because schedulers don't consider budget, resource managers don't have per-task parameter knowledge, and FinOps platforms don't make real-time scheduling decisions.
