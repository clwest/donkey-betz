---
title: "Arc I-0100 P4 Stop Condition #1 PR-B1 — Category C AgentExecution consumer review"
status: draft-awaiting-chris-ratification
authority: pre-flag-flip-review-document
arc_id: I-0100
arc_slug: observability_spine_mission_evidence_substrate
stage: 3
stop_condition: p4-1-consumer-sweep
category: C
opened: 2026-07-06
opener: claude-code
paired_prs:
  - "#2959 (PR-A1) — body-system + learning per-agent (merged)"
  - "#2960 (PR-A2) — dashboard views per-agent (merged)"
  - "#2961 (PR-A3) — diagnostics per-agent (merged)"
  - "#2962 (PR-A4) — misc per-agent (merged)"
depends_on_adr: ADR-0002 §4.2 F1 fold
canonical_pa_exclude_form: ".exclude(agent__name='PersonalAssistant')"
review_scope: docs-only, no runtime code
next_step: Chris agree-all / per-row edits ratification
---

# Arc I-0100 P4 Stop Condition #1 — Category C review

## §1. Purpose

Chris directive (post-PR-A4 merge, 2026-07-06):

> Proceed next with PR-B1:
> - Category C review document only
> - classify each ambiguous family/site
> - recommend include PA / exclude PA / needs Chris decision
> - no runtime code

This document enumerates the remaining ambiguous AgentExecution
consumer sites that neither PR-A1..PR-A4 patched nor obvious
Category A/D disqualifiers cleared. For each site the review offers
a preliminary disposition; Chris ratifies before any Category C
runtime PR ships.

### Categories recap (ADR-0002 §4.2 F1 fold)

- **A** — intentionally cross-source (all agent rows should show).
  Examples: single-execution lookup by ID, user-explicit
  `agent_name` filter, per-user activity accounting.
- **B** — per-agent aggregation that treats each `agent__name` as
  a router-agent dispatch target. PA volume would dominate
  incorrectly. **~24 sites patched via PR-A1..PR-A4 with the
  canonical `.exclude(agent__name='PersonalAssistant')` form.**
- **C** — ambiguous. Semantic intent depends on stakeholder view
  of PA-as-agent vs PA-as-meta-agent.
- **D** — dead / unreferenced.

### Fix form (when a Category C row lands on `exclude`)

Per ADR-0002 §4.2 F1 fold equivalent form + PR-A1 Postgres JSONField
NULL-semantics finding: use `.exclude(agent__name='PersonalAssistant')`
NOT `.exclude(input_data__source='pa')`. Cross-model exclusion (at
the `Agent.objects` queryset) applies where the false-positive is
at the Agent-universe level, not the AgentExecution level (mirrors
PR-A3 stale-agent detection at `views_diagnostics.py:3280` +
PR-A4 `top_performers` at `views_analytics.py:2355`).

## §2. Review methodology + scope

**Enumeration source:** `grep AgentExecution.objects` across
`core/` (86 files touched). Files already patched by PR-A1..PR-A4
are excluded from this review at the specific-site level; other
sites in the same files remain in-scope.

**Selection filter for Category C:**
- Excludes single-row-by-ID lookups (Category A).
- Excludes user-facing search endpoints with explicit `agent_name`
  filter parameters (Category A).
- Excludes writes-only sites (`.objects.create`, `.save()`).
- Excludes migration + fixture sites.
- Includes any site where the intent (per-agent vs cross-source)
  is not obvious from local code context alone.

**Disposition dictionary:**

| Recommendation | Meaning |
|---|---|
| `exclude_pa` | Claude's read: this is Category B in disguise; should ship an exclude patch. |
| `include_pa` | Claude's read: PA rows belong; leave as-is. Formal Category A. |
| `needs_chris` | Claude cannot resolve semantically; requires Chris ratification (or Rigby SIGN pressure). |

**Not in scope:**
- Runtime code changes (per Chris directive).
- Sites already patched in PR-A1..PR-A4.
- The `views_analytics.py` `exec.agent_name` latent bug (recorded
  as §5 debt item; separate from Category C review).

## §3. Category C candidate roster (organized by disposition)

### §3.1 Sites recommended to ship as `exclude_pa` (Claude read: Category B in disguise)

| # | Site | Kind | Reason PA-exclude fits |
|---|------|------|------------------------|
| 1 | `core/views_analytics.py:1507` | Daily execution counts for content-production trend | Time-series counts per day are read as "router-agent throughput"; PA agentic loop inflates without semantic value. |
| 2 | `core/views_analytics.py:1559` | Daily cost rollup for revenue chart | Cost aggregation without agent slicing; PA cost is not "revenue attribution" cost. Reader treats it as agent-job cost. |
| 3 | `core/views_agent_analytics.py:146` | Recent failures top-agents list (7d) | Per-agent failure ranking; identical shape to PR-A1 `feedback_loop_engine.needs_attention`. |
| 4 | `core/services/td_handlers_content.py:3167` | Success rate per-agent (aggregation) | Router-agent job success tracking; PA agentic loop success is a different denominator. |
| 5 | `core/tasks.py:10456` | Top failing agents (7d) in system SLO report | Per-agent failure ranking; identical shape to PR-A3 `top_failing_agents_24h`. |
| 6 | `core/services/ops_autopilot/budget.py:599` | ROI outcome counts (`agent__name__in=spend_list`) | Already filtered to a spend-list allowlist; PA won't naturally appear, but explicit exclude locks in the semantic. Recommend keep as-is + add comment. |

**Sub-total: ~6 sites recommend `exclude_pa` if ratified.**

Semantic pattern: per-agent aggregation ranking + per-agent
success/failure rate + per-day counts that will be read as
router-agent throughput. All isomorphic to sites Chris ratified in
PR-A1..PR-A4.

### §3.2 Sites recommended to leave as `include_pa` (Category A in disguise)

| # | Site | Kind | Reason PA-include fits |
|---|------|------|------------------------|
| 7 | `core/views_analytics.py:1622` | Total execution count for user-engagement chart | Cross-source liveness metric; PA activity IS engagement. |
| 8 | `core/views_analytics.py:2410` | Anomaly detection (system-wide failure rate) | Cross-source SLO anomaly; PA failure rate change is a real signal. |
| 9 | `core/views_agent_execution.py:874` | Agent detail view (per-agent execution history) | Single-agent lookup by name; if user selects PA, they want PA rows. |
| 10 | `core/views_agent_dashboard.py:148` | Aggregate cost across all executions | Financial metric across universe; PA cost is real cost. |
| 11 | `core/views_dashboard_stats.py:85`, `:134` | Per-user 24h execution + token counts | Per-user budget accounting; PA usage is legitimately their usage. |
| 12 | `core/views_trace_viewer.py:61` | Trace artifact gather by trace_id | Debug/replay; ALL rows in trace belong regardless of source. |
| 13 | `core/services/td_handlers_ops.py:1021` | Execution detail by ID | Single-row lookup; Category A. |
| 14 | `core/services/td_handlers_ops.py:1059` | Execution search with optional filters | User-explicit filter surface; if agent_name unset the user asked for "recent" = all. |
| 15 | `core/services/td_handlers_ops.py:4151` | Agent introspection recent (7d) for a specific agent | Filtered to a single agent lookup; Category A. |
| 16 | `core/services/deliverable_provenance.py:81` | Parent execution lookup by ID | Single-row lookup for provenance traceability. |
| 17 | `core/services/heart.py:295` | Recent activity check (1h) | Liveness/heartbeat; any execution proves the system is alive. |
| 18 | `core/services/discord_bot.py:2841` | User agent interaction count | Per-user activity metric; PA is part of user activity. |
| 19 | `core/self_development/self_awareness_engine.py:244` | User success rate over total executions | Per-user metric; PA usage counts. |
| 20 | `core/self_development/self_awareness_engine.py:308` | Executed-agents gap set | Which agents user tried; if user tried PA it should show. |
| 21 | `core/self_development/learning_orchestrator.py:208` | User learning stats recent execution count | Per-user learning tracker; PA usage is learning-relevant. |
| 22 | `core/consumers/system_events_consumer.py:268` | System-status recent_executions_24h count | Platform liveness broadcast; cross-source. |
| 23 | `core/models_skin_layer.py:527` | Workspace op execution-time match (agent_name + 5min window) | Match-a-specific-op site; explicit filter. |
| 24 | `core/tasks_agents.py:1588`, `:1600`, `:4647` | Stale execution cleanup + attention items | Ops/maintenance surfaces; all executions need cleanup regardless of source. |
| 25 | `core/tasks_ops.py:3477`, `:3488` | Initiative dispatch caps + dedup | Already scoped to `input_data__source='initiative_action_dispatch'`; PA source distinct — no collision. |
| 26 | `core/services/finance_content_context.py:184` | Market analysis agent execution scan | Filtered to a narrow pattern (market/stock/prediction agent names); PA won't naturally match. |
| 27 | `core/services/platform_context_service.py:429` | Failure pattern extraction (top error messages) | Diagnostic — PA failure messages are legitimate signal. |
| 28 | `core/views_agent_analytics.py:64` | Failures-today cross-source count | System anomaly metric; cross-source. |
| 29 | `core/services/td_handlers_ops.py:3442` | Ops digest activity `agent_runs` count | Platform digest — Chris uses this to see if fleet is alive; cross-source count of any AgentExecution. |
| 30 | `core/tasks.py:10420` | System metrics `activity` 24h count | Telemetry/observability; end-to-end audit visibility across universe. |

**Sub-total: ~24 sites recommend `include_pa` (Claude read: Category A).**

Semantic pattern: single-row lookups, per-user metrics, cross-source
SLO anomaly detection, operational cleanup surfaces, liveness
metrics, filtered-by-explicit-source counts. PA belongs.

### §3.3 Sites requiring Chris ratification (`needs_chris`)

| # | Site | Kind | Ambiguity |
|---|------|------|-----------|
| 31 | `core/views_analytics.py:1486` | Content production by agent-type filter (whitelist) | Whitelist of content agents; PA won't naturally appear. But if PA enters the whitelist later (agentic-writer role), does it count? Semantic: production ≠ dispatch. Recommend: keep as-is short-term; revisit when PA gains writer subskill. |
| 32 | `core/views_analytics.py:2496`, `:2501`, `:2566` | Forecast + trend time-series (executions/cost) | Time-series values for forecasting model input. If forecast is "router-agent throughput", exclude. If forecast is "platform total", include. Depends on downstream consumer intent. |
| 33 | `core/views_analytics.py:2724` | Export raw executions (100 rows) for user download | User-facing raw export. Should exported row set reflect PA rows too? Depends on user intent for the export. |
| 34 | `core/views_agent_execution.py:583` | Performance metrics overview (success rate + counts) | System-wide metric family, but reader may interpret as router-agent SLO. Semantically borderline. |
| 35 | `core/agents/podcast/podcast_coordinator_agent.py:957` | Story filter for narrative agents (failed / slow-success, recent 20) | Rendered as a "recent agent failure" story. If PA appears in top-20 recent failures, it's shown as a story. Chris may want PA failures narrated OR filtered out. |
| 36 | `core/services/pa_knowledge_injector.py:213` | Agent execution stats for PA's own context injection | Metaphysically odd — PA reads its own context. Include? Exclude? Filter to router-agent only so PA sees "what its downstream agents did"? |
| 37 | `core/services/platform_context_service.py:116` | Agent execution stats (hours_back, top agents, failures) | Aggregate call surface used by multiple callers. Depends on caller's semantic. Recommend: add an `include_pa` param defaulting to True (preserve current) + upgrade downstream callers over time. |
| 38 | `core/services/workflow_orchestration_agent.py:4841` | Recent activity health check (30min window) | Liveness probe by distinct agent count. If PA is the only recent activity, is the fleet "healthy"? |
| 39 | `core/services/experiment_metrics.py:150` | Error rate for experiment window | Experiment-scoped; falls back to time-window when FK unpopulated. Boundary case — need to know if experiments ever attach PA rows. |
| 40 | `core/services/td_handlers_content.py:3104` | Recent activity log (hourly) | User-facing activity feed; user may care about their own PA usage OR only about "background agents". |
| 41 | `core/services/ops_autopilot/budget.py:599` | ROI attribution (see §3.1 entry #6 for comment recommendation) | Currently allowlist-filtered; formal exclude adds documentation but no behavior change. |
| 42 | `core/tasks.py:5576` | Daily report 72h agent executions summary | Periodic digest to Chris; cross-source vs per-agent view — Chris's own preference matters. |
| 43 | `core/tasks_agents.py:5219` | Daily stats (execution count + status breakdown) | Periodic reporter; similar to #42. |

**Sub-total: ~13 sites need Chris ratification.**

Semantic pattern: time-series forecasting inputs (unclear
downstream consumer), narrative rendering (whether PA belongs in
"agent failure" stories), self-referential PA context, platform
context surface used by multiple callers, periodic digests where
Chris's own reading preference matters.

## §4. Rollup

| Disposition | Count | % of Category C | Recommendation |
|---|---:|---:|---|
| `exclude_pa` | ~6 | ~20% | Ship as PR-A5 (small runtime PR with regression tests) — only after Chris ratifies each row here. |
| `include_pa` | ~24 | ~55% | No code change. Record as ratified Category A in this doc so future consumer sweeps skip re-review. |
| `needs_chris` | ~13 | ~25% | Discussion / SIGN cycle. Not shippable as-is. |

Total Category C candidates surfaced: ~43. (Higher than the earlier
"~30" rough estimate because the sweep found more borderline
sites than Claude first flagged. Some rows will collapse into `A`
or `B` upon Chris review.)

## §5. Follow-on debt items (recorded for BACKLOG)

- **DBT-A4-01** — `views_analytics.py` `comparison_v2` +
  `breakdown_v2` reference `exec.agent_name` which does not exist
  on the `AgentExecution` model. PR-A4 shipped the correct
  `.exclude()` on those sites but did not fix the pre-existing
  latent attribute bug. Symptoms: silent iteration falls through
  to `"unknown"` bucket (or `AttributeError` if `exec.agent_name`
  is ever evaluated in isolation). Fix candidate: rewrite iteration
  to use `exec.agent.name if exec.agent else "unknown"` per the
  test approach.

## §6. Not doing in PR-B1

Per Chris directive:
- No runtime code.
- No new tests.
- No feature-flag flip.
- No P4 Stop Condition #2 or #3 work.
- No P3 Stop Condition work.

## §7. What PR-B1 does

- Adds this review document at
  `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_p4_stop_condition_1_category_c_review.md`.
- Provides the ~43 Category C candidate roster + preliminary
  disposition + reasoning.
- Records the follow-on debt item (§5).

## §8. What Chris needs to do to unblock the next PR

Ratify §3.1 (~6 rows) `exclude_pa` disposition (agree-all or
per-row edits). This unblocks PR-A5 (final Category B/C runtime
sweep) which discharges the remaining ~1 known Category B row +
these ratified Category C rows.

Optionally: ratify §3.2 (~24 rows) `include_pa` as formal
Category A so future sweeps do not re-litigate. This is optional
because leaving unratified only costs future review time, not
runtime correctness.

The §3.3 rows (`needs_chris`) do not block PR-A5 — they can flow
to a separate Rigby SIGN cycle later.

## §9. P4 Stop Condition #1 progress after PR-B1 close

- Category A: implicit (~all AgentExecution consumers that were
  never in scope + §3.2 explicit ratifications).
- Category B patched: 24/~25 (PR-A1..PR-A4).
- Category B remaining: ~1 (surfaced only if §3.1 §3.3 rows
  reclassify B during Chris review).
- Category C surfaced: ~43 (this doc).
- Category C dispositioned: 0 pre-ratification / ~30 post-Chris
  ratification (§3.1 + §3.2 combined).
- Category D: none surfaced (nothing removed / discovered as
  orphaned).

P4 Stop Condition #1 fully discharges once §3.1 ratifies + PR-A5
merges. No blocker to PA_AGENT_EXECUTION_WRITE_ENABLED flip
remains from Stop Condition #1 after that point. Stop Conditions
#2 (early-return path decision) and #3 (LLMCallEvent.execution_id
verification) remain independent gates.

## §10. Provenance

- Enumeration: bash `grep -rn AgentExecution.objects core/`
  (2026-07-06 post-PR-A4-merge, `main` at `6722b4bd`).
- Sweep filter: manual per-site read of ~43 candidate lines.
- Prior PRs consulted: #2959, #2960, #2961, #2962 + their test
  files as canonical row-shape templates.
- ADR consulted: ADR-0002 §4.2 F1 fold (canonical exclude form).
- IOS consulted: IOS v1.5 §7.2 SIGN cadence for the Chris
  ratification step.
