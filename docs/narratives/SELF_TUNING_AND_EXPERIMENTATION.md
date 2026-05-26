---
title: "Self-tuning and experimentation — narrative (batch R, draft)"
status: draft (batch R of Session 1162 corpus-narrative program — Chris/Rigby review pending)
last_updated: 2026-05-26
session: 1162
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158) + EDITING_GUARDRAILS v1
companion_docs:
  - docs/patents/DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md
  - docs/narratives/WORKERS_AND_INFRASTRUCTURE.md
  - docs/narratives/DECISION_COMMAND.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/PLATFORM_INVENTORY.md
  - docs/narratives/EDITING_GUARDRAILS.md
provenance_confidence: HIGH (anchored to code paths + Disclosure L patent text + PLATFORM_INVENTORY 2026-05-26 + named session handoffs)
provenance_note: Third new narrative of Session 1162, addressing the "Disclosure L coverage gap" carried over from Session 1161 handoff. Patent Disclosure L (Self-Tuning Policy Framework, March 16, 2026) describes the subsystem but does not exist in the narrative corpus. This doc translates the disclosure into operator-facing narrative form, anchored to current code paths (NOT the Disclosure L paths — see §6.1 drift). Scope is the self-tuning + A/B experimentation + conflict arbitration triangle inside `core/services/ops_autopilot/`; the broader ops_autopilot module (budget / engagement / impact / intelligence / remediation / revenue / verification) is explicitly out of scope and pointed elsewhere. Counts anchored to PLATFORM_INVENTORY 2026-05-26 (git HEAD `373148c7`). Status is "draft pending Rigby review" per Session 1124 co-authored doc pattern.
maps_to_patents:
  - DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md
---

# Self-tuning and experimentation

> **What this doc is.** The platform's ops_autopilot subsystem
> contains a self-tuning + A/B experimentation + conflict
> arbitration triangle that operates *on the platform's own
> operational parameters* — timeout thresholds, budget limits,
> cooldown periods, panel sizes. Three components
> (`PolicyOptimizer`, `ExperimentEngine`, `PolicyArbitrator`)
> share a runtime parameter store (`SystemConfiguration`) and an
> audit trail (`AutopilotAction`), and together they form a
> closed loop: observe → recommend → A/B test → promote-or-
> rollback → arbitrate conflicts → snapshot → observe.
>
> This narrative is the operator-facing translation of patent
> Disclosure L (`docs/patents/DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md`).
> Where the disclosure is structured for patent attorneys
> (problem / novelty hooks / claim skeleton), this doc is
> structured for a future operator who needs to debug a
> stuck experiment, understand why a parameter changed
> overnight, or trace a configuration value back to the
> policy that set it.
>
> **Scope:** the self-tuning + A/B experimentation + conflict
> arbitration triangle only. The broader ops_autopilot module
> (12 files, ~17.7k lines as-of 2026-05-26) also contains
> budget enforcement, engagement scoring, impact analysis,
> intelligence routing, remediation playbooks, revenue
> attribution, and verification gates. Those are out of scope
> for this narrative — see §8 for pointers.
>
> **Companion to WORKERS_AND_INFRASTRUCTURE (N).** That
> narrative covers the worker fleet + Celery routing + cost
> budget that the autopilot operates *against*. This doc
> covers the policy layer that *changes* those parameters.

---

## §1 What this is

The platform's autopilot has a long-standing problem: static
policy parameters age badly. A timeout threshold of 3 that
worked when there were 50 agents may be wrong with 218 agents.
A budget soft-limit of 70% that fit one cost regime may need to
move when LLM provider prices shift. Manual tuning is slow and
requires operational knowledge that doesn't scale across
hundreds of knobs.

The self-tuning subsystem closes that loop. Three components
collaborate against a shared parameter store:

1. **`PolicyOptimizer`** observes the autopilot's own action
   history, identifies parameters with high false-positive
   rates or ineffective thresholds, and recommends adjustments
   — applying at most one change per evaluation and capping at
   the daily limit defined in `AutopilotConfig`.

2. **`ExperimentEngine`** creates baseline vs. treatment
   variants for selected parameters, runs experiments against
   real workload metrics, auto-promotes treatments that
   improve IQROI by a configurable margin, and auto-rolls back
   treatments that regress.

3. **`PolicyArbitrator`** runs *last* in every autopilot
   cycle, detects when multiple policies wrote the same
   `SystemConfiguration` key in the same cycle, resolves the
   conflict using a priority-ordered knob registry, enforces
   hold-time minimums and anti-flap detection, and writes a
   `FinalAppliedOverrides` snapshot so the post-cycle state
   is auditable.

The substrate that makes this work is `AutopilotConfig`'s
two-layer resolution: class-level defaults plus runtime
overrides in `SystemConfiguration` with the
`autopilot_tuning:` prefix. Every parameter can be tuned at
runtime without code deployment, and every change has an
`AutopilotAction` audit record plus a `HumanAttentionItem` for
governance visibility.

**The narrative-shift vs Disclosure L:** the patent disclosure
(March 16, 2026) names class paths in `core.py` that have
since been refactored into dedicated modules (`governance.py`,
`experiment.py`). The disclosure's runtime cycle entry points
in `core.py` are still accurate; the class *definitions* have
moved. §6.1 flags this drift; the narrative cites current
paths throughout.

---

## §2 Vocabulary

| Term | Definition |
|---|---|
| **ops_autopilot module** | The Django service package at `core/services/ops_autopilot/`. 12 files as-of 2026-05-26 (`__init__.py`, `budget.py`, `config.py`, `core.py`, `engagement.py`, `experiment.py`, `governance.py`, `impact.py`, `intelligence.py`, `remediation.py`, `revenue.py`, `verification.py`). Total ~17.7k lines. This narrative covers the policy-tuning triangle inside it; the rest is out of scope. |
| **`PolicyOptimizer`** | The self-tuning component (`core/services/ops_autopilot/governance.py:702`). Observes `AutopilotAction` history, recommends parameter adjustments, applies them at rate. Rate limits live on `AutopilotConfig`. |
| **`ExperimentEngine`** | The A/B testing component (`core/services/ops_autopilot/experiment.py:236`). Creates `PolicyExperiment` rows, runs baseline-vs-treatment evaluations each cycle, auto-promotes / auto-rolls-back based on metric thresholds. |
| **`PolicyArbitrator`** | The conflict resolution component (`core/services/ops_autopilot/governance.py:1118`). Runs LAST in each autopilot cycle. Detects multi-policy writes to the same key, resolves via knob registry, enforces anti-flap + hold-time, snapshots `FinalAppliedOverrides`. |
| **`AutopilotConfig`** | The two-layer config resolver (`core/services/ops_autopilot/config.py:229`). Class-level defaults overridden by `SystemConfiguration` rows with the `autopilot_tuning:` key prefix. Calling `AutopilotConfig.get(name)` returns the runtime value if an override exists, else the class default. Type-coerced to match the default's type. |
| **`SystemConfiguration`** | The runtime parameter store (`core/models.py:411`; also visible at `core/models/system/models.py:9` — both reference the same canonical row). Generic key/value rows. The `autopilot_tuning:` prefix namespace holds the autopilot's runtime overrides. |
| **`AutopilotAction`** | The audit trail row (`core/models_diagnostic_pipeline.py:516`). Every parameter change, experiment promotion, or rollback creates one. Carries the policy name, action type, old/new values, reason, confidence, and metrics. |
| **`PolicyExperiment`** | The A/B experiment record (`core/models_policy_experiment.py:22`). Carries `baseline_params`, `treatment_params`, status (`active` / `promoted` / `rolled_back` / `expired`), and metric snapshots for both variants. |
| **`FinalAppliedOverrides`** | The per-cycle snapshot model. End of each autopilot cycle, the arbitrator writes a row capturing every active `autopilot_tuning:` value at that moment. Enables time-travel debugging — "what was the system configured to do at 3:42 PM?". |
| **`HumanAttentionItem`** | The unified governance escalation surface (`core/models_human_interface.py:20`). Every parameter change, experiment promotion, rollback, flap detection, and hold violation creates one. Surfaced via PA's `governance_tool.attention_list` and the governance UI. See narrative E. |
| **Knob registry** | The priority-ordered map of which policies write which configuration keys, with merge strategies. Lives in code (governance.py); not a DB table. Each entry: key name, list of policies that write it, priority order, merge strategy (`priority_wins` or `max`). |
| **IQROI** | The composite Impact-Quality-ROI metric the autopilot optimizes against. The threshold-based promotion / rollback decisions in `ExperimentEngine` are framed in terms of treatment IQROI vs baseline IQROI. The exact composition lives elsewhere in ops_autopilot/impact.py; treat that as canonical. |
| **Anti-flap detection** | The conflict-mode where one knob gets changed many times by competing policies in a short window. When detected, the arbitrator locks the knob at its current value and escalates. Threshold + window are config constants (see §3M5). |
| **Hold-time enforcement** | The per-knob minimum interval since the last change. If a policy tries to change a knob within its hold time, the change is suppressed and a log line records the suppression. Hold times are knob-specific (see governance.py knob registry). |
| **`TUNING_INTERVAL_HOURS` / `TUNING_MAX_CHANGES_PER_DAY`** | Two rate-limit constants on `AutopilotConfig` (`core/services/ops_autopilot/config.py:288, 290`). Treat the config file as canonical for the current values; this prose may drift. |

---

## §3 Milestone timeline

### Milestone 1 — `AutopilotConfig`'s two-layer override system

**Code anchor:** `core/services/ops_autopilot/config.py:229-365`.

The substrate the entire triangle stands on. `AutopilotConfig`
is a class with hundreds of class-level constants — thresholds,
intervals, cooldowns, panel sizes, hold times. Reading any of
these via `AutopilotConfig.get(name)` does *not* return the
class attribute directly. Instead, the resolver:

1. Checks an `_override_cache` (populated from
   `SystemConfiguration` rows with the `autopilot_tuning:` key
   prefix).
2. If an override exists, type-coerces the stored value to
   match the class attribute's type (bool / float / int).
3. Returns the override, OR falls through to the class default
   if no override is set.

The implication: every autopilot parameter is *runtime-tunable*
without a code deploy. Set
`SystemConfiguration.objects.update_or_create(key='autopilot_tuning:TUNING_INTERVAL_HOURS', defaults={'value': '12'})`
and the next `AutopilotConfig.get('TUNING_INTERVAL_HOURS')`
call returns `12` instead of the class default.

**This is what `PolicyOptimizer` writes to.** The optimizer
doesn't change Python source code; it writes
`SystemConfiguration` rows in the `autopilot_tuning:`
namespace, and the next config-read picks them up.

### Milestone 2 — `PolicyOptimizer` (self-tuning)

**Code anchors:** Class definition at `core/services/ops_autopilot/governance.py:702`. Cycle wrapper that calls it: `core/services/ops_autopilot/core.py:1243-1264`. Rate-limit constants on `AutopilotConfig` at `core/services/ops_autopilot/config.py:288, 290`.

The self-tuning loop. The optimizer:

1. **Observes** — queries the last 7+ days of `AutopilotAction`
   records, grouped by policy.
2. **Computes** — per-policy effectiveness metrics (false
   positive rate, average time to recovery, before-vs-after
   system health impact).
3. **Recommends** — for each policy with concerning metrics,
   identifies the parameter most likely to be the culprit and
   proposes an adjustment with: `old_value`, `new_value`,
   `reason`, `confidence`, supporting metrics.
4. **Applies** — writes the change to `SystemConfiguration`
   via the `autopilot_tuning:` prefix.

**Rate limits** — the daily cap and per-cycle cap are
canonicalized on `AutopilotConfig`
(`core/services/ops_autopilot/config.py:288, 290`); treat the
config file as the source of truth for the current values. The
optimizer enforces them by counting prior `AutopilotAction`
records before applying.

**Each change creates two records:**

- `AutopilotAction` row capturing the change + reason +
  confidence + metrics that justified it.
- `HumanAttentionItem` surfacing the change to governance
  with undo instructions:
  `"How to undo: Set SystemConfiguration key autopilot_tuning:{param} back to {old_value}"`.

**Rate-limiting rationale:** changing multiple parameters in
the same cycle would make it impossible to attribute observed
behavior changes to specific parameter changes. The single-
change-per-cycle limit is deliberate, not conservative.

### Milestone 3 — `ExperimentEngine` (A/B testing for ops policies)

**Code anchors:** Class at `core/services/ops_autopilot/experiment.py:236`. Cycle wrapper at `core/services/ops_autopilot/core.py:1693-1746`. Experiment record model at `core/models_policy_experiment.py:22`.

Some parameter changes are too consequential for fire-and-
forget self-tuning. The experiment engine handles these
through controlled A/B trials.

**Lifecycle phases:**

| Phase | Action |
|---|---|
| Setup | Create `PolicyExperiment` with `baseline_params` + `treatment_params`. Status: `active`. |
| Active | Up to the experiment's max-duration window. Treatment params applied to `SystemConfiguration`; both variants accumulate metric data. |
| Evaluation | Each autopilot cycle, compare treatment IQROI vs baseline IQROI. |
| Promotion | If treatment improvement exceeds the promotion threshold, treatment_params get written permanently to `SystemConfiguration`. Status → `promoted`. |
| Rollback | If treatment regresses past the rollback threshold, revert to baseline_params. Status → `rolled_back`. |
| Expiry | If neither threshold hit within the max-duration window, revert to baseline. Status → `expired`. |

The promotion / rollback / expiry thresholds + the max-duration
window are config constants (treat
`core/services/ops_autopilot/experiment.py` as canonical for
current values; the disclosure cites 10% improvement / 5%
regression / 7-day window as historical values).

**Supported parameter classes** (from Disclosure L): portfolio
allocator (budget allocation per desk), ROI throttle (low-QROI
agent cooldown thresholds), budget controller (LLM spend
limits soft / hard). The experiment engine is extensible to
any parameter where `IQROI` can be measured per-variant; the
support list isn't a hard restriction.

**Every state transition emits both:** an `AutopilotAction`
row + a `HumanAttentionItem` for governance visibility. A
promotion that revealed a regression after promotion is itself
auditable — there's no "silent" experiment outcome.

### Milestone 4 — `PolicyArbitrator` (conflict resolution)

**Code anchor:** Class at `core/services/ops_autopilot/governance.py:1118`. Cycle wrapper at `core/services/ops_autopilot/core.py:2643-2706`.

The cycle's gatekeeper. Three independent mechanisms run
inside the arbitrator, in order:

**Mechanism 1: Priority-based resolution.** The arbitrator
holds a knob registry mapping each `SystemConfiguration` key
to (a) the list of policies that write it, (b) a priority
order among them, and (c) a merge strategy. When two policies
wrote the same key in the same cycle, the merge strategy
fires:

- `priority_wins` — the higher-priority policy's value is
  kept; the other is suppressed and logged.
- `max` — the highest value wins (used for safety-critical
  parameters where the conservative bound matters more than
  which policy proposed it; the budget hard-limit is the
  canonical example).

**Mechanism 2: Anti-flap detection.** If a knob changed
more than N times in the rolling window, the arbitrator locks
the knob at its current value and creates a `HumanAttentionItem`
("Flapping detected on `{knob}`"). Threshold + window are
config constants — treat governance.py as canonical for current
values; the disclosure cites 3+ changes in 24h.

**Mechanism 3: Hold-time enforcement.** Each knob has a
minimum interval since its last change. If a policy tries to
change a knob within its hold time, the change is suppressed
and a log line records "Hold violation: `{knob}` changed
within `{hold_time}` of last change." Hold times are per-knob
and live in the knob registry.

**End-of-cycle snapshot.** After all three mechanisms run,
the arbitrator writes one `FinalAppliedOverrides` row capturing
every active `autopilot_tuning:` override at that moment:

- `cycle_id` (UUID)
- `cycle_ts` (timestamp)
- `knob_count` (length of applied_values dict)
- `applied_values` (full key-value map)

This is the time-travel debugging artifact. A future operator
asking "what was the system configured to do at 14:30 UTC?"
joins `FinalAppliedOverrides` on `cycle_ts` and reads
`applied_values`.

### Milestone 5 — The feedback loop is closed (cycle order matters)

**Code anchor:** The autopilot cycle entry in `core/services/ops_autopilot/core.py`. Cycle structure: budget → engagement → impact → intelligence → remediation → revenue → policy-optimizer → experiment-engine → arbitrator → snapshot.

The order is load-bearing. The arbitrator runs LAST because:

- Earlier policies (budget controller, remediation playbooks,
  release governor) write their parameters into
  `SystemConfiguration` during the cycle.
- The optimizer + experiment engine write THEIR proposed
  changes also during the cycle.
- The arbitrator then sees all writes for the cycle, applies
  conflict resolution / anti-flap / hold-time, and writes the
  snapshot.

**If the cycle order changes**, the arbitrator could miss
late-cycle writes from another policy. **If you see arbitrator
output that disagrees with the actual applied values**, check
the cycle order — has a new policy been inserted *after* the
arbitrator? That's the regression.

### Milestone 6 — Governance audit trail (the operator's view)

**Code anchors:** `AutopilotAction` at `core/models_diagnostic_pipeline.py:516`. `HumanAttentionItem` at `core/models_human_interface.py:20`.

Every action of the triangle produces both:

1. **`AutopilotAction`** — the structured record (policy name,
   action type, old/new values, reason, confidence, metrics).
   Queryable via Django ORM and surfaced via PA's
   `governance_tool.autopilot_actions` action.

2. **`HumanAttentionItem`** — the governance-visible alert
   with urgency + type + source + age. Surfaced via the
   governance page + PA's `governance_tool.attention_list`.
   Carries undo instructions so an operator can revert without
   a code change.

**The PA surface** — narrative D (PERSONAL_ASSISTANT) covers
the consolidated `governance_tool` that exposes these
queries through Rigby. Operator asking Rigby "what changed
overnight?" reads `AutopilotAction` filtered to the recent
window and renders the human-readable summaries.

### Milestone 7 — The two-layer override design is also the rollback mechanism

A subtle but important property: because every runtime
override lives in `SystemConfiguration` rows with the
`autopilot_tuning:` prefix, rolling back a change is one DB
write away. There's no "git revert" needed for parameter
mistakes; the operator deletes (or updates) the
`SystemConfiguration` row and the next `AutopilotConfig.get()`
call returns the class default again.

This is why the `HumanAttentionItem` for every change includes
explicit undo instructions citing the row key. The system
makes the rollback action cheap on purpose.

---

## §4 What came of it

The self-tuning triangle gave the platform four properties
that weren't there before:

- **Continuous parameter optimization without human
  intervention.** The optimizer adjusts thresholds the
  platform was previously wrong about, without anyone needing
  to know what those thresholds were.

- **Safe experimentation on operational parameters.** Before
  the experiment engine, parameter changes were committed
  speculatively. Now the controlled A/B framework validates
  changes against real workload metrics before making them
  permanent.

- **Policy collision prevention.** Before the arbitrator,
  multiple policies could write the same `SystemConfiguration`
  key and the last-write-wins semantics produced incoherent
  state. The knob registry + arbitrator make conflicts
  explicit and resolvable.

- **Time-travel auditability.** The `FinalAppliedOverrides`
  snapshot + `AutopilotAction` history + `HumanAttentionItem`
  governance trail together produce a complete record of
  *which configuration values were in effect at which time
  and why*.

The pattern that matters: the triangle treats the platform's
own operational parameters as a *changeable runtime surface*
governed by the same audit + governance discipline as content
or revenue work. Self-tuning is just a policy that writes to
that surface; experiments are A/B tests against it; the
arbitrator resolves the resulting conflicts. The substrate
(`SystemConfiguration` + `AutopilotConfig.get()`) is uniform
across all of it.

---

## §5 Current state snapshot

As-of PLATFORM_INVENTORY 2026-05-26 (git HEAD `373148c7`):

- **Module structure:** 12 files in `core/services/ops_autopilot/`.
  This narrative covers the policy triangle (governance.py +
  experiment.py + config.py + relevant core.py wrappers); the
  other 8 files (budget / engagement / impact / intelligence /
  remediation / revenue / verification / `__init__`) are out of
  scope — see §8 for pointers.
- **Class locations:** `PolicyOptimizer` and `PolicyArbitrator`
  in `governance.py`; `ExperimentEngine` in `experiment.py`;
  `AutopilotConfig` in `config.py`. Cycle entry wrappers in
  `core.py`.
- **Parameter store:** `SystemConfiguration` (`core/models.py:411`).
  Autopilot namespace: `autopilot_tuning:` key prefix.
- **Audit trail:** `AutopilotAction` (`core/models_diagnostic_pipeline.py:516`).
- **Experiment records:** `PolicyExperiment` (`core/models_policy_experiment.py:22`).
- **Snapshot:** `FinalAppliedOverrides`. Treat the
  governance.py write site as canonical for the schema; the
  arbitrator end-of-cycle handler is the only writer.
- **Governance escalation:** `HumanAttentionItem` (`core/models_human_interface.py:20`).
- **Rate-limit constants:**
  `core/services/ops_autopilot/config.py` (`TUNING_INTERVAL_HOURS`,
  `TUNING_MAX_CHANGES_PER_DAY`). Treat the file as canonical
  for current values.

---

## §6 Open questions

### 6.1 Disclosure L cites paths that have moved — patent text needs an addendum

The patent disclosure (March 16, 2026) cites:

- `PolicyOptimizer` at `core/services/ops_autopilot/core.py:1224-1328`
- `PolicyArbitrator` at `core/services/ops_autopilot/core.py:2643-2706`

Verified 2026-05-26: both classes have been **moved into
`governance.py`**:

- `PolicyOptimizer` at `core/services/ops_autopilot/governance.py:702`
- `PolicyArbitrator` at `core/services/ops_autopilot/governance.py:1118`

The cycle entry wrappers Disclosure L cites in `core.py` are
still accurate; only the class definitions moved. **If you're
debugging from the disclosure and the paths don't resolve**,
this is why — the disclosure pre-dates the refactor.

**Remediation:** the patent disclosure is a frozen artifact
(filed for attorney review). The right fix is a small addendum
section noting the path move, not an inline edit. Filed as a
follow-on PR candidate.

### 6.2 IQROI definition lives in `impact.py` — should this narrative cite the formula?

The narrative repeatedly references "treatment IQROI vs
baseline IQROI" as the experiment evaluation metric. The
composite definition lives in `core/services/ops_autopilot/impact.py`.

This narrative does NOT include the formula because:
(a) the formula drifts (rule 1 risk); (b) impact.py is the
canonical source; (c) reproducing the formula here creates
two places to update.

**If you need the formula**: read impact.py directly. **If you
observe an experiment promotion that seems wrong**, the
diagnostic path is: check the `PolicyExperiment.metrics`
snapshot for both variants, then read impact.py's IQROI
implementation, then check whether the metric was correctly
populated for the experiment window.

### 6.3 The other 8 ops_autopilot files have no narrative

This narrative scopes itself to the policy triangle. The
other files in `core/services/ops_autopilot/`:

- `budget.py` (~1.4k lines) — budget enforcement (separate
  patent disclosure: J + K).
- `engagement.py` (~1.0k) — engagement scoring.
- `impact.py` (~1.8k) — impact + IQROI calculation.
- `intelligence.py` (~2.8k) — intelligence-routing decisions.
- `remediation.py` (~1.7k) — remediation playbooks.
- `revenue.py` (~1.8k) — revenue attribution.
- `verification.py` (~750) — verification gates.

Each is its own narrative candidate. Rigby's call on whether
to write a single `OPS_AUTOPILOT.md` umbrella narrative or
expand each into its own batch entry. For now, anyone reading
into those modules should treat them as out-of-scope here.

### 6.4 `FinalAppliedOverrides` query patterns aren't documented

The model exists; the per-cycle snapshots are written; but
there's no documented PA tool action or admin recipe for
"give me the configuration that was in effect at time T."
The model is queryable via Django ORM but the operator
ergonomics are unbuilt.

**If you need to debug a past configuration:**
`FinalAppliedOverrides.objects.filter(cycle_ts__lte=t).order_by('-cycle_ts').first()`
returns the snapshot active at time T. Worth surfacing as a
PA tool action.

### 6.5 Hold-time + flap-detection constants live in code, not config

Unlike most autopilot parameters, the anti-flap threshold +
window and the per-knob hold times are *not* in the
`autopilot_tuning:` namespace — they're hardcoded in the
knob registry inside `governance.py`. This is by design
(the meta-policy that prevents flapping shouldn't itself
be flap-prone), but it does mean tuning them requires a
code change + deploy.

**If you observe the arbitrator misbehaving on flap detection
or hold-time enforcement**, the fix path is editing the knob
registry in `governance.py`, not flipping a
`SystemConfiguration` row.

---

## §7 Source index

- **March 16, 2026 batch** — patent Disclosure L drafted (12-disclosure batch).
- **Pre-disclosure work** — `AutopilotAction`, `PolicyExperiment`, `FinalAppliedOverrides` models added (no single session anchor found in the survey; the disclosure cites the architecture as in-place by March 2026).
- **Disclosure L → narrative gap flagged** — Session 1161 handoff §6 "Disclosure L narrative coverage gap" carryover.
- **Refactor moving classes from `core.py` → `governance.py` + `experiment.py`** — happened after the disclosure was drafted; not session-tracked in the disclosure metadata. The current code state is verified 2026-05-26 against git HEAD `373148c7`.
- **Session 1162** — this narrative drafted to close the carryover gap.

Inferred from the surrounding system: Sessions 1095-1098
(COO diagnostic + canary), Sessions 1140-1142 (action-card
pre-gen + signal-studio fleet plumbing) used the
`AutopilotConfig` substrate but didn't add or move the
triangle's core classes.

---

## §8 Canonical sources

This narrative is authoritative for:
- The vocabulary table in §2 (self-tuning triangle terms).
- The three-component closed-loop description in §1.
- The cycle-order load-bearing claim in §3M5.
- The "patent paths have moved" drift flag in §6.1.
- The scope boundary against the broader ops_autopilot module
  in §1 and §6.3.

This narrative is NOT authoritative for:
- **The IQROI formula** — see `core/services/ops_autopilot/impact.py` (the canonical source).
- **Budget enforcement mechanics** — patent disclosures J + K, narrative TBD; meanwhile see `core/services/ops_autopilot/budget.py`.
- **Remediation playbook mechanics** — separate subsystem in `core/services/ops_autopilot/remediation.py`; partially covered in narrative on Body Systems (depending on which playbook).
- **Patent claim text + novelty hooks** — see `docs/patents/DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md` (the canonical patent artifact).
- **`SystemConfiguration` general usage** — the autopilot triangle uses one prefix namespace; other subsystems use other prefixes. The model itself is broadly used; this narrative is authoritative only for `autopilot_tuning:`.
- **`HumanAttentionItem` governance UX** — see narrative E (DECISION_COMMAND) for the consolidated governance surface.
- **PA `governance_tool` actions** — see narrative D (PERSONAL_ASSISTANT) for the tool consolidation pattern.
- **Counts** (line totals, file counts, etc.) — see PLATFORM_INVENTORY.md.
- **Canonical constant values** (`TUNING_INTERVAL_HOURS`, rate limits, flap thresholds, hold times) — see the respective config / governance source files.

---

## Draft notes (remove on lock)

- First-draft pending Chris + Rigby review per the Session
  1124 co-authored doc pattern.
- This is the **patent-rooted narrative pattern** — it
  translates Disclosure L into operator form. The mapping
  is recorded in frontmatter via `maps_to_patents`. Future
  patent disclosures with coverage gaps can follow the same
  pattern.
- Scope decision explicit: triangle only, not the broader
  ops_autopilot module. §6.3 flags the gap for future
  narratives.
- 5 Open Questions in §6 — one drift flag (6.1), one
  unbuilt-tool flag (6.4), one scope-decision flag (6.3),
  one "narrative-correct silence" flag (6.2), and one
  design-decision flag (6.5).
- Naming: `SELF_TUNING_AND_EXPERIMENTATION` matches the
  Session 1161 carryover label "self-tuning experimentation
  lacks a narrative." Open to renaming.
- Batch letter: R (next after batch Q /
  INITIATIVES_AND_LIFECYCLE).
