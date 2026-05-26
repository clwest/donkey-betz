---
title: "Invention Disclosure L: Self-Tuning Policy Framework with A/B Experimentation, Conflict Arbitration, and Governance Audit Trail"
kind: invention_disclosure
disclosure_id: L
workstream: WS4 (Budget Enforcement + Experimentation)
status: draft (Attorney Review Pending)
last_updated: 2026-03-16
originating_session: pre-session-tracking (March 16, 2026 batch)
inventor: Chris West (DonkeyKing)
provenance_confidence: HIGH
provenance_note: One of 12 invention disclosures drafted as a single March 16, 2026 batch. Frontmatter added Session 1160 (2026-05-26) as part of the patents preservation pass. Operator-facing narrative `docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md` shipped Session 1162 (PR #2280); §13 addendum appended Session 1163 morning to record class-path drift; §14 addendum appended Session 1163 afternoon to record a deeper mechanism drift (the `FinalAppliedOverrides` model in §5 Component 4 is aspirational — as-built is a single-row overwrite in `SystemConfiguration`). Counsel call queued in §14.3. Disclosure body §1–§12 unchanged from original draft.
maps_to_narratives:
  - docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md
companion_docs:
  - docs/patents/README.md
  - docs/patents/EXECUTIVE_SUMMARY_WS4.md
  - docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md
---

# Invention Disclosure L: Self-Tuning Policy Framework with A/B Experimentation, Conflict Arbitration, and Governance Audit Trail

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Self-Tuning Autonomous Policy Framework with Metric-Driven Parameter Optimization, A/B Experimentation with Auto-Promotion and Rollback, and Multi-Policy Conflict Arbitration with Anti-Flap Detection

---

## 2. Field / Technical Domain

Autonomous operations governance for self-modifying AI systems. Specifically, methods for autonomously tuning policy parameters based on historical effectiveness metrics, A/B testing policy variants with automatic promotion of winners and rollback of losers, detecting and resolving conflicts when multiple policies write the same configuration parameter, and maintaining a complete governance audit trail of all autonomous configuration changes.

---

## 3. Problem

**a) Policy parameters are static despite changing conditions.** A timeout threshold of 3 that worked when there were 50 agents may be too aggressive with 218 agents. Manual tuning requires operational knowledge and is slow.

**b) Policy changes are risky without empirical validation.** Changing a budget threshold or cooldown period might improve or worsen system behavior. Without A/B testing, changes are speculative.

**c) Multiple autonomous policies writing the same configuration create conflicts.** When the budget controller sets a model downgrade flag AND the self-tuner adjusts the downgrade model AND the release governor freezes deploys, the resulting state may be inconsistent.

---

## 4. Solution Summary

1. **PolicyOptimizer**: Analyzes 7+ days of policy action history, identifies parameters with high false-positive rates or ineffective thresholds, recommends adjustments, and applies them (max 1 change per day, 2 per day hard cap). All changes recorded in AutopilotAction with governance visibility.

2. **ExperimentEngine**: Creates baseline vs. treatment variants for policy parameters, runs experiments for up to 7 days, auto-promotes treatments that improve IQROI by >= 10%, auto-rolls back treatments that regress by >= 5%, and expires experiments that don't converge.

3. **PolicyArbitrator**: Runs LAST in the policy cycle. Detects when multiple policies wrote the same SystemConfiguration key. Enforces priority-based resolution, hold-time minimums, and anti-flap detection (3+ changes to same knob in 24h → lock + alert). Records FinalAppliedOverrides snapshot per cycle.

All three share `SystemConfiguration` as the runtime parameter store and `AutopilotAction` as the audit trail.

---

## 5. As-Built Mechanism

### Component 1: PolicyOptimizer (Self-Tuning)

**File:** `core/services/ops_autopilot/core.py` (lines 1224-1328)
**File:** `core/services/ops_autopilot/governance.py`

**Cycle:** Runs at most once per `TUNING_INTERVAL_HOURS` (default 24h). Rate-limited by checking `AutopilotAction` records.

**Evaluation Process:**
1. Query 7+ days of `AutopilotAction` records grouped by policy
2. For each policy, compute effectiveness metrics:
   - False positive rate (actions that were rolled back or resolved without effect)
   - Average time to recovery (how long before the issue resolved)
   - Impact on system health (before vs. after action)
3. Identify parameters where metrics suggest adjustment:
   - High false-positive rate → raise threshold (be less aggressive)
   - Long recovery time → adjust timeout or cooldown
   - Low effectiveness → consider disabling or restructuring
4. Generate recommendations with old_value, new_value, reason, confidence, metrics

**Application Constraints:**
- `TUNING_MAX_CHANGES_PER_CYCLE = 1` — One parameter change per evaluation
- `TUNING_MAX_CHANGES_PER_DAY = 2` — Hard daily cap across all evaluations
- Every change creates `AutopilotAction` record + `HumanAttentionItem` for governance

**Governance trail:** Each change includes undo instructions:
```
"How to undo: Set SystemConfiguration key
 autopilot_tuning:{param} back to {old_value}"
```

### Component 2: AutopilotConfig Runtime Override System

**File:** `core/services/ops_autopilot/config.py` (lines 229-365)

**Two-layer configuration:**
1. **Class-level defaults:** Hardcoded in `AutopilotConfig` class attributes
2. **Runtime overrides:** Stored in `SystemConfiguration` with key prefix `autopilot_tuning:`

**Resolution:** `AutopilotConfig.get(param_name)`:
1. Check `_override_cache` (populated from `SystemConfiguration` records with `autopilot_tuning:` prefix)
2. If override exists, coerce to match type of class-level default (bool, float, int)
3. If no override, return class-level default

This means every parameter can be tuned at runtime via SystemConfiguration without code deployment.

### Component 3: ExperimentEngine (A/B Testing)

**File:** `core/services/ops_autopilot/experiment.py`
**File:** `core/services/ops_autopilot/core.py` (lines 1693-1746)

**Experiment Lifecycle:**

| Phase | Duration | Action |
|-------|----------|--------|
| Setup | Instant | Create PolicyExperiment with baseline_params and treatment_params |
| Active | Up to 7 days | Collect metrics for both variants; treatment_params applied to SystemConfiguration |
| Evaluation | Each autopilot cycle | Compare treatment metrics vs. baseline metrics |
| Promotion | On success | treatment_params become permanent; experiment status = 'promoted' |
| Rollback | On regression | Revert to baseline_params; status = 'rolled_back' |
| Expiry | After 7 days | If not promoted, revert to baseline; status = 'expired' |

**Auto-Promotion Condition:**
```python
if treatment_iqroi > baseline_iqroi * 1.10:  # 10% improvement
    status = 'promoted'
    # treatment_params written permanently to SystemConfiguration
```

**Auto-Rollback Condition:**
```python
if treatment_iqroi < baseline_iqroi * 0.95:  # 5% regression
    status = 'rolled_back'
    # Revert to baseline_params
```

**Supported Policy Experiments:**
- `portfolio_allocator`: Budget allocation per desk
- `roi_throttle`: Low-QROI agent cooldown thresholds
- `budget_controller`: LLM spend limits (soft/hard percentages)

**Governance:** Each promotion/rollback creates `AutopilotAction` + `HumanAttentionItem`.

### Component 4: PolicyArbitrator (Conflict Resolution)

**File:** `core/services/ops_autopilot/core.py` (lines 2643-2706)
**File:** `core/services/ops_autopilot/governance.py`

**Execution order:** Runs LAST in every autopilot cycle (after all other policies have written).

**Three conflict detection mechanisms:**

**Mechanism 1: Priority-Based Resolution**
```
Knob Registry per SystemConfiguration key:
  key: 'agent_timeout_seconds'
    WrittenBy: [timeout_remediation_playbook, release_governor]
    Priority: timeout_remediation_playbook > release_governor
    MergeStrategy: priority_wins

  key: 'budget_hard_limit_pct'
    WrittenBy: [budget_controller, self_tuning]
    Priority: budget_controller > self_tuning
    MergeStrategy: max (safety-first: take highest value)
```

When two policies wrote the same key in the same cycle, the higher-priority policy's value wins. Lower-priority write is suppressed.

**Mechanism 2: Anti-Flap Detection**
```python
def _detect_flap(knob_name, window_hours=24):
    recent_changes = count changes to knob in window
    if changes >= 3:
        return True  # FLAPPING
```

When a knob flaps (3+ changes in 24h):
- Lock the knob (prevent further changes)
- Create `HumanAttentionItem` for manual review
- Log: "Hold violation: {knob} changed {N} times in 24h"

**Mechanism 3: Hold-Time Enforcement**
```
Each knob has a minimum hold time:
  agent_timeout_seconds: 1 hour
  budget_hard_limit_pct: 4 hours
  content_panel_size: 1 hour
```

If a policy tries to change a knob within its hold time, the change is suppressed.

**FinalAppliedOverrides Snapshot** (end of each cycle):
```python
FinalAppliedOverrides.objects.create(
    cycle_id=uuid,
    cycle_ts=now,
    knob_count=len(active_overrides),
    applied_values={key: value for all autopilot_ keys},
)
```

This creates a complete record of which configuration values were actually in effect at the end of each 10-minute cycle.

---

## 6. Novelty Hooks (Section 102)

**a) Autonomous policy parameter tuning with rate-limited application.** The system analyzes its own action history to identify ineffective parameters and adjusts them — but caps at 1 change per evaluation and 2 per day. No known autonomous system tunes its own operational parameters with explicit rate limits.

**b) A/B testing for autonomous ops policies.** The ExperimentEngine creates controlled experiments on operational parameters (not product features), with auto-promotion on 10% improvement and auto-rollback on 5% regression. No known system A/B tests its own operational control parameters.

**c) Multi-policy conflict arbitration with knob registry.** A centralized registry tracks which policies write which configuration keys, with priority ordering and merge strategies. No known multi-policy system provides explicit conflict resolution.

**d) Anti-flap detection with hold-time enforcement.** When a configuration key changes 3+ times in 24 hours, the system locks it and escalates to human governance. This prevents configuration oscillation from competing policies.

**e) FinalAppliedOverrides snapshot per cycle.** A complete record of all active configuration values at the end of each policy cycle enables time-travel debugging ("what was the system configured to do at 3:42 PM?").

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Self-tuning with rate limits contradicts the goal of rapid optimization.** The obvious approach to self-tuning is to apply all beneficial changes immediately. Rate-limiting to 1 change per day is non-obvious because it appears to slow optimization. The insight: policy parameters interact non-linearly, and changing multiple parameters simultaneously makes it impossible to attribute improvements to specific changes.

**b) A/B testing operational parameters is borrowed from product experimentation.** A/B testing is standard for user-facing features (button colors, layouts) but non-obvious for operational parameters (timeout thresholds, budget limits). The insight: operational parameters have measurable impact on system IQROI, making them amenable to the same statistical testing framework.

**c) Anti-flap detection implies that autonomous systems can fight themselves.** Most autonomous system designs assume policies cooperate. Anti-flap detection acknowledges that independently operating policies can create oscillations — a failure mode that is non-obvious to designers who think of policies as coordinated.

**d) Hold-time enforcement creates deliberate sluggishness.** Preventing a configuration change within a hold period appears to reduce system responsiveness. The insight: for operational parameters, stability is more valuable than responsiveness, and rapid changes are more likely to be oscillations than genuine improvements.

---

## 8. Operational Benefits

- **Continuous optimization:** Parameters improve over time without human intervention
- **Safe experimentation:** A/B framework validates changes before permanent application
- **Conflict prevention:** Arbitrator prevents policy fights that waste resources
- **Anti-oscillation:** Flap detection and hold times maintain stable configuration
- **Full auditability:** Every change, experiment, and conflict recorded with timestamps and reasons
- **Time-travel debugging:** FinalAppliedOverrides snapshots enable root-cause analysis

---

## 9. Alternative Embodiments

**a) Bayesian optimization for parameter tuning.** Instead of heuristic analysis, use Gaussian Process-based Bayesian optimization to explore the parameter space efficiently.

**b) Multi-armed bandit for experiment allocation.** Instead of fixed baseline/treatment split, use Thompson Sampling to dynamically allocate traffic based on emerging results.

**c) Graph-based conflict detection.** Instead of a flat knob registry, model policy dependencies as a DAG and detect cycles that indicate structural conflicts.

**d) Graduated hold times.** Hold times could increase with each detected flap (1h → 4h → 12h), creating backoff pressure on unstable parameters.

**e) Cross-cycle conflict detection.** Instead of detecting conflicts within a single cycle, detect patterns where policies consistently override each other across cycles.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for self-tuning an autonomous policy framework governing a multi-agent AI system, the method comprising:

(a) analyzing historical records of autonomous policy actions over a configurable lookback period to identify policy parameters with suboptimal effectiveness metrics;

(b) generating parameter adjustment recommendations constrained by a maximum number of changes per evaluation period and a maximum number of changes per day;

(c) applying recommended adjustments to a shared runtime configuration store, recording each adjustment with its prior value, new value, and justification in an audit trail;

(d) creating, for selected parameter adjustments, controlled experiments comparing baseline parameter values to treatment values, and automatically promoting treatments that improve a target metric by a configurable percentage and rolling back treatments that regress the metric by a configurable percentage;

(e) detecting, after all policies in a cycle have executed, conflicts where multiple policies wrote to the same configuration key, and resolving conflicts using a priority-ordered knob registry with merge strategies;

(f) detecting configuration key flapping where a key was changed more than a configurable number of times within a configurable window, and upon detecting flapping, locking the key and escalating to human governance; and

(g) recording, at the end of each policy cycle, a snapshot of all active configuration overrides for time-series auditability.

### Dependent Claims

1. Wherein the effectiveness metrics comprise false positive rate, average time to recovery, and before-versus-after system health impact.

2. Wherein the controlled experiments of step (d) are automatically expired after a configurable maximum duration if neither promotion nor rollback thresholds are met, and baseline values are restored upon expiry.

3. Wherein the merge strategies in the knob registry comprise at least: priority_wins (highest-priority policy's value used) and max (highest value used for safety-critical parameters).

4. Wherein the hold-time enforcement prevents any configuration key from being changed within a configurable minimum interval since its last change, regardless of which policy requests the change.

5. Wherein the runtime configuration store uses a two-layer resolution: class-level defaults overridden by database-stored values with a prefix-based namespace, and values are type-coerced to match the default's type.

6. Wherein each parameter adjustment, experiment outcome, and conflict resolution creates both an audit trail record and a human-visible governance alert with undo instructions.

7. Wherein the maximum number of changes per evaluation period is one and the maximum per day is two, ensuring parameter interactions can be observed before further changes.

8. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Self-Tuning Feedback Loop**
```
[7+ days of AutopilotAction records]
      |
[PolicyOptimizer.evaluate()]
      |
[Identify: high false-positive rate on TIMEOUT_SPIKE_THRESHOLD=3]
      |
[Recommend: raise to 5 (68% of blocks were unnecessary)]
      |
[Apply: max 1 change per eval, 2 per day]
      |
[Record: AutopilotAction + HumanAttentionItem]
      |
[Next 7 days: observe effect of threshold=5]
```

**Figure 2 — A/B Experiment Lifecycle**
```
[Create Experiment]
  baseline: {budget_soft_limit: 0.70}
  treatment: {budget_soft_limit: 0.65}
      |
[Active (up to 7 days)]
  Collect IQROI under treatment
      |
[Evaluate each cycle]
      |
  ┌─────────┴─────────┐
  v                    v
[IQROI +10%]      [IQROI -5%]      [7 days, no change]
  |                    |                    |
[PROMOTE]          [ROLLBACK]          [EXPIRE]
  |                    |                    |
[Permanent]        [Revert]            [Revert]
```

**Figure 3 — Policy Arbitrator Conflict Resolution**
```
Cycle N: 3 policies wrote 'content_panel_size':
  - deliberation_remediation: set to 2 (L1)
  - self_tuning: set to 1 (optimization)
  - experiment_engine: set to 3 (treatment)

Knob Registry:
  priority: deliberation_remediation > experiment_engine > self_tuning
  merge: priority_wins

Resolution: content_panel_size = 2 (deliberation_remediation wins)
Suppressed: self_tuning (value 1), experiment_engine (value 3)
```

**Figure 4 — Anti-Flap Detection**
```
Timeline for knob 'budget_soft_limit_pct':
  T-20h: self_tuning set to 0.65
  T-14h: budget_controller reset to 0.70
  T-8h:  self_tuning set to 0.65 again
  T-2h:  budget_controller reset to 0.70 again

Changes in 24h: 4 (>= 3 threshold)
  → FLAP DETECTED
  → Lock knob at current value (0.70)
  → Create HumanAttentionItem: "Flapping detected on budget_soft_limit_pct"
  → Require manual intervention to unlock
```

---

## 12. Prior Art Buckets

**a) AutoML / Hyperparameter Optimization (Optuna, Ray Tune)** — Teaches parameter optimization for ML models but not for operational policy parameters with rate limits and governance trails.

**b) A/B Testing Platforms (Optimizely, LaunchDarkly Experimentation)** — Teaches controlled experiments for user-facing features but not for autonomous operational parameters with auto-promotion/rollback.

**c) Configuration Management (Consul, etcd, ZooKeeper)** — Teaches distributed configuration storage but not multi-writer conflict detection, anti-flap, or hold-time enforcement.

**d) Policy Engines (OPA, Casbin)** — Teaches policy evaluation but not self-tuning, A/B experimentation, or conflict arbitration between competing policies.

**e) Chaos Engineering (Gremlin, Chaos Monkey)** — Teaches controlled system perturbation but not automated parameter optimization based on perturbation outcomes.

---

## Examiner Story

Prior art teaches hyperparameter optimization for ML models (Optuna), A/B testing for user features (Optimizely), distributed configuration management (Consul), and policy evaluation engines (OPA). However, no single reference teaches a system that (1) analyzes its own policy action history to identify ineffective parameters and autonomously adjusts them with rate-limited application (max 1 per day), (2) A/B tests operational policy parameters (not user features) with automatic promotion on metric improvement and rollback on regression, (3) detects multi-policy conflicts on shared configuration keys using a priority-ordered knob registry with merge strategies, (4) detects configuration oscillation (flapping) and locks affected keys with human escalation, and (5) records per-cycle snapshots of all active configuration overrides for time-travel auditability. The combination is non-predictable because AutoML optimizes model parameters not operational policies, A/B platforms test features not infrastructure parameters, config managers don't detect multi-writer conflicts, and policy engines don't tune themselves.

---

## 13. Addendum — Code path locations (as-of 2026-05-26)

**Status:** Append-only addendum. The disclosure body §1–§12 above is the original draft (March 16, 2026) and is **not edited** by this section. This addendum exists to record path drift between the disclosure's as-built §5 citations and the current code state, so a future reader of the disclosure (attorney, examiner, future operator) can follow the cited mechanism to running code without a dead-link detour.

**Surfaced by:** `docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md` §6.1 (Session 1162, batch R). The narrative is the operator-facing translation of this disclosure and is the canonical source for the current-state mechanism. This addendum closes the cross-reference loop in the other direction.

### 13.1 The refactor

This disclosure cites code locations as they existed during the March 2026 drafting window; subsequent reorganization of the `ops_autopilot` codebase relocated certain class definitions into a domain-organized package. The wrappers remain accurate; this addendum maps the cited elements to their current canonical locations as-of 2026-05-26.

**For historical context:** commit **`fe94c928`** ("refactor: split `ops_autopilot.py` (553KB) into 11-module package", **2026-03-09**) extracted 37 classes from the monolithic `core/services/ops_autopilot.py` into a package at `core/services/ops_autopilot/`. The disclosure's mechanism description (§5) is unaffected by the reorganization — only file locations shifted.

### 13.2 Class definitions — moved out of `core.py`

| Class | Disclosure §5 citation | Current canonical location (2026-05-26) |
|---|---|---|
| `PolicyOptimizer` | `core/services/ops_autopilot/core.py` (lines 1224-1328) + `governance.py` | `core/services/ops_autopilot/governance.py:702` |
| `ExperimentEngine` | `core/services/ops_autopilot/experiment.py` + `core.py` (lines 1693-1746) | `core/services/ops_autopilot/experiment.py:236` |
| `PolicyArbitrator` | `core/services/ops_autopilot/core.py` (lines 2643-2706) + `governance.py` | `core/services/ops_autopilot/governance.py:1118` |
| `AutopilotConfig` | `core/services/ops_autopilot/config.py` (lines 229-365) | `core/services/ops_autopilot/config.py:229` (still accurate) |

Verified against git HEAD `1b10f361` (2026-05-26 Session 1162 close-out merge). Reproduce: `grep -n "^class \(PolicyOptimizer\|PolicyArbitrator\|ExperimentEngine\)" core/services/ops_autopilot/{governance,experiment}.py`.

### 13.3 Cycle wrappers — still in `core.py`, line numbers shifted

The disclosure's §5 citations to `core.py` line ranges actually pointed at the **cycle wrappers** that call into each class, not the class definitions themselves. The cycle-wrapper functions are still in `core.py`; only the line numbers drifted as `core.py` evolved post-refactor.

| Cycle wrapper | Disclosure §5 citation | Current line range (2026-05-26) | Calls class via lazy import |
|---|---|---|---|
| `_policy_self_tuning` | `core.py` lines 1224-1328 | `core.py:1239-1346` | `from core.services.ops_autopilot.governance import PolicyOptimizer` |
| `_policy_experiment_engine` | `core.py` lines 1693-1746 | `core.py:1708-1764` | `from core.services.ops_autopilot.experiment import ExperimentEngine` |
| `_policy_policy_arbitrator` | `core.py` lines 2643-2706 | `core.py:2658-2724` | `from core.services.ops_autopilot.governance import PolicyArbitrator` |

The mechanism §5 describes (rate-limited apply, A/B promotion/rollback, three-mechanism arbitration, FinalAppliedOverrides snapshot) lives entirely in the class files now; the `core.py` wrappers are thin entry points that instantiate the class and forward arguments.

### 13.4 What this addendum does NOT change

- **No claim text changes.** §10 (claim skeleton) is unaffected — claims describe the method, not file paths.
- **No novelty-hook changes.** §6 hooks describe the mechanism, not its layout.
- **No mechanism changes.** §5 is the canonical record of the as-built design as of March 2026; the mechanism description is still accurate today. Only the citation paths drifted.
- **No editing of §1–§12.** Per the frozen-artifact convention for filed disclosures, the original body is preserved verbatim; this addendum is the recorded path-resolution overlay.

### 13.5 Future drift policy

For future code reorganizations affecting the §5 paths cited above, the same addendum-only pattern applies: append a new sub-section to §13 (`13.6`, `13.7`, …) with the new canonical locations and the commit SHA that moved them. Do not edit §5 inline. The operator-facing narrative (`docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md`) is the place to track current paths as living documentation; this disclosure body is the frozen IP artifact.

---

## 14. Addendum — `FinalAppliedOverrides` mechanism drift (as-of 2026-05-26)

**Status:** Append-only addendum. Append-only convention preserved from §13. Surfaced by Session 1163 recon while implementing the §6.4 ergonomic follow-on from `docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md`. Captures a substantive divergence between the disclosure's as-built §5 mechanism and the production code state. The §5 description is the original mechanism intent; this addendum records what is actually built today and the planned correct-fix path.

### 14.1 What §5 Component 4 describes

The disclosure §5 Component 4 ("PolicyArbitrator — Conflict Resolution") shows the snapshot mechanism as:

```python
FinalAppliedOverrides.objects.create(
    cycle_id=uuid,
    cycle_ts=now,
    knob_count=len(active_overrides),
    applied_values={key: value for all autopilot_ keys},
)
```

This implies a Django model `FinalAppliedOverrides` with at least `cycle_id`, `cycle_ts`, `knob_count`, and `applied_values` fields, with a NEW row appended per cycle. The novelty hook §6(e) and the operational benefit "Time-travel debugging" in §8 both depend on per-cycle history existing.

### 14.2 What the code actually does (2026-05-26, HEAD `9bf87f4e`)

No Django model named `FinalAppliedOverrides` exists in the codebase. Verify: `grep -rn "^class FinalAppliedOverrides" core/` returns zero matches.

The snapshot is written by `PolicyArbitrator.record_overrides_snapshot()` (currently at `core/services/ops_autopilot/governance.py:1616` after the Session 1163 follow-on `get_latest_snapshot()` method was inserted; pre-Session-1163 the writer was at `governance.py:1525`). The writer uses `update_or_create` on a **single** `SystemConfiguration` row:

```python
SystemConfiguration.objects.update_or_create(
    key='policy_arbitrator_snapshot',
    defaults={'value': json.dumps({
        'cycle_id': str(cycle_id),
        'ts': now.isoformat(),
        'knobs': snapshot,
        'knob_count': len(snapshot),
    })},
)
```

Each cycle overwrites the previous snapshot. There is no `cycle_ts` column to query against, no per-cycle row history, and therefore **no time-travel query is possible** against the as-built mechanism. The novelty hook §6(e) and operational benefit "Time-travel debugging" in §8 are aspirational, not as-built.

### 14.3 What this means for the claims (§10)

The independent method claim §10(g) reads:

> "(g) recording, at the end of each policy cycle, a snapshot of all active configuration overrides for time-series auditability."

Strict reading: a single-row overwrite arguably satisfies "recording a snapshot at the end of each cycle" because each cycle does produce a new snapshot value. It does NOT satisfy "for time-series auditability" — the prior cycle's snapshot is overwritten and unrecoverable. Counsel may want to assess whether (i) the claim text needs amendment to match the as-built mechanism, or (ii) the as-built mechanism should be migrated to per-cycle storage so the claim reads accurately. **This addendum surfaces the question; it does not answer it.**

### 14.4 The planned correct-fix path (B-style follow-on)

The follow-on work is queued in `docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md` §6.4. Shape:

1. Add a Django model `FinalAppliedOverrides(cycle_id UUID, cycle_ts TIMESTAMPZ indexed, knob_count INTEGER, applied_values JSONB)` with a migration.
2. Change `PolicyArbitrator.record_overrides_snapshot()` from `SystemConfiguration.update_or_create(key='policy_arbitrator_snapshot', ...)` to `FinalAppliedOverrides.objects.create(...)`.
3. Add a PA tool action `final_overrides_at(t)` that runs `FinalAppliedOverrides.objects.filter(cycle_ts__lte=t).order_by('-cycle_ts').first()` and returns the snapshot active at time T.
4. Decide retention policy (Rigby's Session 1163 design Q): keep every cycle forever, or prune after N days. The arbitrator runs roughly every 10 minutes per the existing cycle structure, so unbounded retention would accumulate ~52,560 rows/year per knob set.
5. Decide payload size policy: JSONB indexing strategy; consider compressing or storing diffs vs. full snapshots if knob counts grow.

Until that work ships, the operator-visible compromise (C-style honest fix shipped Session 1163) is the `latest_overrides_snapshot` PA tool action — returns only the most recent snapshot, with an explicit `storage.mechanism` field documenting the single-row overwrite reality.

### 14.5 The honest interim tool — `latest_overrides_snapshot`

Shipped in the same Session 1163 PR as this addendum. `core.services.ops_autopilot.governance.PolicyArbitrator.get_latest_snapshot()` reads the single `SystemConfiguration(key='policy_arbitrator_snapshot')` row, returns the parsed JSON payload, and includes an explicit `storage` block naming the as-built mechanism:

```json
{
  "found": true,
  "cycle_id": "…",
  "ts": "2026-…",
  "row_updated_at": "2026-…",
  "knob_count": N,
  "knobs": {…},
  "storage": {
    "model": "SystemConfiguration",
    "key": "policy_arbitrator_snapshot",
    "mechanism": "single-row overwrite per cycle (no per-cycle history)"
  },
  "note": "Per-cycle history is not stored; time-travel queries are not supported by the current implementation. row_updated_at carries the database row mtime so callers can answer \"is this fresh?\" without inferring from cycle cadence. See Disclosure L §14 addendum for the drift record."
}
```

The `row_updated_at` field (added during Session 1163 review per Rigby's nit) lets callers answer "is this snapshot fresh?" without having to know the cycle cadence. `ts` is the timestamp the arbitrator captured into the JSON payload (from `now.isoformat()` inside `record_overrides_snapshot`); `row_updated_at` is the database row's `updated_at` (Django auto-managed). The two are usually milliseconds apart; if they ever diverge significantly that itself is a debugging signal.

The tool exists so operators can answer "what's configured right now?" without an ORM recipe. It does NOT pretend to support time-travel. The intent is C-style honest exposure that does not lock in the as-built mechanism — when §14.4 ships, the same tool can be extended to accept a `time` argument without renaming.

### 14.6 What this addendum does NOT change

- **No claim text changes.** §10(g) is preserved verbatim. Counsel decides whether claim amendment is needed (see §14.3).
- **No novelty-hook changes.** §6(e) is preserved verbatim — the disclosure as filed remains the historical record.
- **No mechanism changes to §5.** §5 Component 4 stays as the original mechanism description; §14 records the divergence.
- **No editing of §1–§13.** Frozen-artifact convention preserved.
