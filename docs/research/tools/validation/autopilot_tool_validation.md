# `autopilot_tool` — Validation Report (S2895)

**Tool:** `autopilot_tool`
**Schema:** `core/services/pa_tool_schemas.py:3187`
**Handler:** `core/services/td_handlers_ops.py:2439` (`_handle_autopilot`)
**Register site:** `core/services/tool_dispatcher.py:538`
**Session:** S2895 (Path B systematic sweep — Slice 1.5a of `td_handlers_ops`, read-only sweep only; mutations deferred to Slice 1.5b per S2893 Rigby SIGN zoom-out #4)
**HEAD at validation:** `9c516ddfc` (2026-07-22)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred. Adopts **2-tier evidence template** per Rigby S2895 T1 SIGN Q5 zoom-out (Tier 1 compact evidence-ledger + group-by-family narrative; Tier 2 raw JSON appendix for discriminators / bugs / sole-exemplar families).
**Category upgrade target:** `untested` → `validated_partial` (every read-only action in the schema `action` enum exercised live; ~29 mutation actions documented in §5a and explicitly deferred to Slice 1.5b).
**Rigby SIGN:** S2895 T1 SIGN — Rigby AGREE'd on ship-shape / catalog (with 2 nits absorbed inline) / canary=DBZ target; DISAGREE'd on "dump everything inline" and proposed the 2-tier template, which this doc adopts as the reference shape for future large-surface tool sweeps. Live T1 tool_runs: `governor_tool.status`, `search_docs`, `autopilot_tool.dry_run_report`, `autopilot_tool.history` (with `include_evidence=true, selected_fields=[...]`) — tool-grounded per feedback_verify_rigby_tool_runs_before_trusting_sign.

---

## 1. Purpose / when-to-use

Central operator surface for the Ops Autopilot substrate — the 10-minute-cadence policy-evaluation loop that guards SLO breaches, timeout spikes, stale agent blocks, deliberation retries, content-pipeline sweeps, attention auto-resolves, governance auto-decisions, budget/ROI enforcement, revenue-pipeline health, knowledge freshness, capacity/security/compliance/integrity/value observation. One tool multiplexes **99 enum actions** across 12+ substrate families — from `status` and `dry_run_report` (system-wide) through per-family `_report` / `_queue` / `_inbox` reads and `_approve` / `_generate` / `governance_set_mode` / `governance_kill_switch` mutations.

Answers questions like: "is autopilot healthy?", "what would it do if we ran it now?", "where's the budget being spent, and is ROI attributed?", "what's the revenue-pipeline funnel and where are the stalls?", "any content quality or spider-freshness issues?", "what's the security/compliance/integrity posture?", "which agents are on the timeout ladder?", "what policies flap?". Reads are safe fleet-wide; mutations gate through `dry_run`/`confirm` (see `security_containment_plan` — Session 1228 PR-A) or explicit staff/owner auth (see `governance_set_mode`, `governance_kill_switch`).

Complements `workspace_budget_tool` (per-workspace spend + per-workspace enforcement — S2894 `validated_full`) — this tool's `budget_report` shows GLOBAL spend + top spenders, while workspace_budget_tool operates per-workspace substrate. Also complements `governor_tool` (agent-level circuit breaker — S2893 `validated_full`) — governance actions here operate at higher scope (global mode, kill switches, family throttles).

## Covered actions

**Read-only actions exercised live this ship (76 actions across 5 batches, all successful):**

- **READS_CORE (4):** `status`, `history` (include_evidence=true, selected_fields=[6 paths]), `config`, `dry_run_report`, `drift_scan`
- **BUDGET / ROI / SCHEDULING (5):** `budget_report`, `roi_report`, `scheduler_report`, `tuning_report`, `portfolio_report`
- **ATTRIBUTION / DEBT / POLICY (5):** `attribution_report`, `attribution_debt_report`, `policy_conflict_report`, `latest_overrides_snapshot`, `decision_ledger_report` (two variants — default `days=1` + `days=7, decision_type=action_taken`)
- **LADDERS (2):** `timeout_ladder_report`, `deliberation_pipeline_report`
- **BACKLOG / GOALS / EXPERIMENTS (3):** `backlog_report`, `goal_report`, `experiment_report`
- **RELEASE (1):** `release_report`
- **REVENUE PIPELINE / OUTREACH READS (8):** `revenue_pipeline_report`, `revenue_full_pipeline`, `revenue_funnel`, `revenue_forecast`, `prospecting_queue`, `lead_source_report`, `outreach_inbox`, `outreach_metrics_report`
- **CLOSE PACK READS (5):** `close_pack_inbox`, `close_pack_metrics_report`, `close_pack_followup_queue`, `close_pack_risk_report`, `close_pack_velocity`
- **ENGAGEMENT READS (5):** `engagement_inbox`, `engagement_metrics_report`, `engagement_sla_queue`, `engagement_meeting_suggestions`, `engagement_conversion_report`
- **MEETING READS (2):** `meeting_inbox`, `meeting_metrics_report`
- **GOVERNANCE READS (3):** `governance_status`, `governance_throttle_report`, `governance_audit`
- **KNOWLEDGE (4):** `knowledge_health`, `knowledge_citation_report`, `knowledge_source_report`, `knowledge_staleness_report`
- **GROWTH (4):** `growth_candidates`, `growth_schedule`, `growth_channel_report`, `growth_funnel`
- **CAPACITY (4):** `capacity_forecast`, `capacity_bottleneck_report`, `capacity_throttle_plan`, `capacity_budget_envelope`
- **VALUE (4):** `value_events_report`, `value_outcome_rates`, `value_usage_gaps`, `value_realization_summary`
- **SECURITY (4):** `security_permission_drift`, `security_abuse_queue`, `security_containment_plan` (dry_run=true default — S1228 PR-A gate), `security_secrets_scan`
- **COMPLIANCE (4):** `compliance_pii_scan`, `compliance_retention_report`, `compliance_access_audit`, `compliance_report`
- **INTEGRITY (4):** `integrity_quality_report`, `integrity_null_spike_scan`, `integrity_duplicate_report`, `integrity_reliability_scores`
- **BACKFILL READS (2):** `backfill_impacts`, `backfill_failure_reasons` — runtime-not-executed this ship; classified as reads pending §5a review.

**MUTATION actions (23 — all deferred to Slice 1.5b, see §5a for blast-radius classification):**

- `run` — **mutation — deferred to Slice 1.5b** — see §5a. Primary autopilot cycle executor.
- `outreach_approve`, `outreach_reject`, `outreach_generate` — **mutation — deferred to Slice 1.5b** — see §5a. Outreach lifecycle mutations.
- `close_pack_generate`, `close_pack_approve` — **mutation — deferred to Slice 1.5b** — see §5a. Close-pack lifecycle mutations.
- `engagement_classify`, `engagement_draft_reply`, `engagement_approve_reply`, `engagement_disqualify` — **mutation — deferred to Slice 1.5b** — see §5a. Engagement-flow mutations.
- `experiment_create`, `experiment_start` — **mutation — deferred to Slice 1.5b** — see §5a. Experiment lifecycle mutations.
- `meeting_create`, `meeting_brief`, `meeting_recap` — **mutation — deferred to Slice 1.5b** — see §5a. Meeting artifact mutations.
- `governance_set_mode`, `governance_kill_switch`, `governance_deactivate_switch` — **mutation — deferred to Slice 1.5b** — see §5a. Governance-lever mutations (owner-or-staff gated + `ttl_hours` capped).
- `release_freeze`, `release_unfreeze` — **mutation — deferred to Slice 1.5b** — see §5a. Release-gate mutations.
- `goal_set_weights` — **mutation — deferred to Slice 1.5b** — see §5a. Goal-weight config mutation.

**Total exercised:** 76 unique read-only actions across 82 dispatches (a few actions ran with multiple variants). Every response returned in ≤600ms; 90%+ under 100ms.

**Explicitly NOT exercised this ship (deferred to Slice 1.5b):** ~29 mutation actions — see §5a for the full list + blast-radius classification. Category upgrade to `validated_full` waits on that follow-on session.

## 3. Schema notes

- **Required:** `action` (enum, **99 values** covering the full read + write surface).
- **Conditional / optional params:** 30+ parameter properties covering per-action needs — `workspace_id`, `daily_cap_usd`, `dry_run`, `confirm`, `limit`, `include_evidence`, `selected_fields`, `days`, `decision_type`, `policy_name`, `treatment_params`, `success_metric`, `experiment_id`, `description`, `goal_weights`, `knob`, `policy_filter`, `at`, `draft_id`, `edited_text`, `reason`, `opportunity_id`, `offer_key`, `price`, `timeline_days`, `pack_id`, `event_id`, `intent`, `reply_text`, `status_filter`, `meeting_id`, `scheduled_at`, `duration_minutes`, `meeting_link`, `prospect_name`, `prospect_company`, `notes`, `next_steps`, `filter_type`, `mode`, `scope`, `scope_target`, `ttl_hours`, `target`, `target_detail`, `switch_id`, `hours`, `agent_name`, `include_downgrade_savings`, plus scope/limit knobs.
- **Auth model:**
  - **Reads:** available to all callers (no explicit owner-scoping observed at the tool layer; upstream authz applies).
  - **Owner-or-staff mutations:** `outreach_*_approve/reject`, `close_pack_*_approve/generate`, `engagement_*_classify/draft_reply/approve_reply/disqualify`, `meeting_create/brief/recap`, `experiment_create/start`, `goal_set_weights`, `governance_set_mode/kill_switch/deactivate_switch`, `release_freeze/unfreeze`.
  - **Staff-only:** none observed inside `_handle_autopilot`; governance targets like `governance_kill_switch` gated at higher scope by upstream authz + `ttl_hours` limits (default 4h, max 72h).
- **Belt-and-suspenders (S1228 PR-A):** `security_containment_plan` defaults `dry_run=true` and requires BOTH `dry_run=false` AND `confirm=true` to actually execute — guards against GPT autofill flipping a preview into a live containment action. Live-verified: `security_containment_plan` at default params returned `dry_run: true` echo, `recommendation_count: 0`, `needs_human_review: false`.
- **`selected_fields` projection (S2861 slate #1):** verified working. Allowlist prefixes `evidence.` + `result.` only; max 20 paths; missing/invalid prefixes silently ignored. Applied correctly to `history` output — rows returning `evidence: {}` are those where NONE of the requested keys existed on that row, not a projection failure (initial Rigby T1 read misinterpreted empty `evidence: {}` as projection breakage; corrected in T2 with evidence from her own tool output).
- **Audit trail:** every autopilot cycle writes an `AutopilotAction` row (visible via `history`) with `action_type`, `agent_name`, `policy`, `dry_run`, `evidence` JSON, `result` JSON, `deploy_sha`, `created_at`. The DBZ workspace_budget events surfaced during this ship's Ledger Row A discriminator (see §6.1 raw evidence appendix) are examples of this trail.
- **Schema description lint:** verbose (200+ line description covering all 99 actions inline). Passes the `actions_not_mentioned_in_description` check — every enum value has a corresponding descriptive sentence in the description prose.
- **Ship-time drift signal (from `drift_scan` action, § Evidence Ledger row 4):** the schema/handler cross-check found 10 warnings: 2 tool-name schema/handler mismatches (`db_health_tool`, `mission_verdict`) + 8 agent-registry orphans (DB Agent rows without AGENT_MAP entries — `PersonalAssistant`, `Rigby`, `ShellTestRouter`, `System`, `ValidationCheckAgent`, `rigby`, `claude-code`, `3DGenerationAgent`). None critical; all are known persona/system agents plus the case-sensitivity duplicate `Rigby` vs `rigby`.

## 4. Golden-path examples

**System-wide health snapshot + policy dry-run + drift check:**
```
autopilot_tool  action=status
autopilot_tool  action=dry_run_report
autopilot_tool  action=drift_scan
```

**Spend + attribution + ROI overview:**
```
autopilot_tool  action=budget_report
autopilot_tool  action=roi_report
autopilot_tool  action=attribution_debt_report
```

**Decision-ledger inspection (audit trail for policy decisions):**
```
autopilot_tool  action=decision_ledger_report
autopilot_tool  action=decision_ledger_report  days=7  decision_type=action_taken
autopilot_tool  action=latest_overrides_snapshot
autopilot_tool  action=policy_conflict_report
```

**Revenue-pipeline funnel + close pack + engagement + meeting reads:**
```
autopilot_tool  action=revenue_full_pipeline
autopilot_tool  action=revenue_funnel
autopilot_tool  action=revenue_forecast
autopilot_tool  action=outreach_inbox
autopilot_tool  action=close_pack_inbox
autopilot_tool  action=engagement_sla_queue
autopilot_tool  action=meeting_inbox
```

**Knowledge / growth / capacity / value monitoring:**
```
autopilot_tool  action=knowledge_health
autopilot_tool  action=knowledge_staleness_report
autopilot_tool  action=growth_funnel
autopilot_tool  action=capacity_forecast
autopilot_tool  action=capacity_budget_envelope
autopilot_tool  action=value_realization_summary
```

**Security / compliance / integrity sweeps:**
```
autopilot_tool  action=security_containment_plan            # dry_run=true default (S1228 PR-A gate)
autopilot_tool  action=security_secrets_scan
autopilot_tool  action=compliance_report
autopilot_tool  action=integrity_quality_report
autopilot_tool  action=integrity_reliability_scores
```

**Ledger Row A discriminator (S2894 → S2895 sharpening probe):**
```
autopilot_tool  action=history  limit=100  include_evidence=true \
  selected_fields=['evidence.workspace_id','evidence.daily_total','result.reason','result.cap','evidence.trigger','evidence.actor_user_id','evidence.simulated']
```

## 5. Failure / empty-state / staleness / attribution notes

- **Autopilot cadence:** beat-scheduled every 10 minutes; each cycle produces multiple AutopilotAction rows (one per policy that either runs or dry_runs). The very first `history` call after a cycle will show `cycle_evaluation`, `contract_drift_detection`, and `governance_auto_decision` rows at the top; `workspace_budget_*` rows show up much older in the timeline (only written on state transitions, not on every cycle).
- **`selected_fields` projection empty-state:** rows returning `evidence: {}` after projection are rows where NONE of the requested keys existed. Only misleading if you interpret it as projection breakage — the tool response body ECHOES the applied paths in `selected_fields: [...]`, so you can distinguish "projection applied, no matches" from "projection silently rejected" by inspecting the echo. Live verification: the exact selection `['evidence.workspace_id', 'evidence.daily_total', 'result.reason', 'result.cap']` was echoed post-validation.
- **`selected_fields` projection — longer-list silent wipe (S2895 T2 live-observed):** when the projection list contains MORE paths than the shorter (~4-6 path) selections we exercised successfully — Rigby observed at T2 re-verification that an 8-path list (including one novel `result.enforcement_tier` addition) came back with `selected_fields: []` echoed (silently wiped) while a shorter 4-path retry worked cleanly. The wipe is silent (no error surfaced). Working hypothesis: some batch-level validation rejects the whole list when any single path fails a check, but the handler at `td_handlers_ops.py:2526` uses `raw_selected[:_MAX_SELECTED_FIELDS]` with `_MAX_SELECTED_FIELDS=20` and per-path validation that "silently ignores" invalid prefixes — so the wipe location must be upstream (PA-tool-schema layer or the OpenAI function-call arg schema). **Operator footgun** — if projection echoes empty unexpectedly, retry with fewer paths. Ledger candidate — see §Related.
- **`revenue_pipeline_report` vs `revenue_full_pipeline` scope mismatch:** these two actions report different active-item counts because they scope differently — `revenue_pipeline_report` counts contactable `Opportunity` rows (returned `total_active=0` in this ship's DBZ observation) while `revenue_full_pipeline` aggregates across substrates including `OutreachDraft` rows (returned `total_active_items=125`, all in `outreach.draft` status). Not a bug; worth calling out in operator training because "active" is overloaded across the two surfaces.
- **`prospecting_queue` empty-title anomaly:** all 6 leads returned by `prospecting_queue` at this ship had empty `title` fields (rows sourced from financial spiders — `sec_edgar`, `finnhub`, `polygon_finance`, `etherscan`, `yahoo_finance`, `financial`). Score 45 flat across all 6. Ledger candidate — see § Related below.
- **`growth_funnel` engage_rate_pct:** field can exceed 100% (observed 1338.7%). This is by design: it counts total engagement events divided by total candidates — a single candidate can generate multiple events (view + status transitions + exports). Doc as "event-rate, not unique-engaged-rate" to avoid operator misinterpretation.
- **`backlog_report` throttle_active=true since 2026-06-24:** governor level L1 (Generation throttled) has been active continuously for ~28 days at the time of this ship. That's an extended throttle window worth watching; the substrate is working as designed but the trigger condition may no longer apply.
- **`experiment_report`:** 0 active experiments observed. Supported policies: `portfolio_allocator`, `roi_throttle`, `budget_controller`. Supported metrics: `avg_desk_iqroi`, `attribution_debt_pct`, `total_impact_usd`, `publish_pass_rate`, `error_rate`. Fresh state — no runtime for empirical policy-effectiveness data yet.
- **Empty downstream revenue substrates:** CLOSE PACK / ENGAGEMENT / MEETING surfaces all returned empty. Consistent with A4 warm-up scope (S2846 ratified 3-5 total intros as hard throttle) — outreach hasn't converted downstream yet.
- **`integrity_null_spike_scan` false positives:** 96 spikes flagged critical, all at `null_rate=1.0` for `processed_data` + `embedding_text` fields across ~20 spider families. Working hypothesis: these are "not populated by design" fields for spider intake stages that don't produce embeddings — the null-rate detector doesn't distinguish "field not applicable" from "field failed to populate". Not a Ledger row until we confirm the intent for those fields; noise-vs-signal filter is the actionable ask.
- **Transient dispatcher schema-validation glitch:** Batch A observed 4 actions (`policy_conflict_report`, `latest_overrides_snapshot`, both `decision_ledger_report` variants) fail with "action_type unrecognized" schema error on their first dispatch. Re-dispatch with identical payload succeeded cleanly. Not reproducible; either a transient PA-side validation flap or a different tool surface accidentally routed. Watchpoint if it recurs.

## 5a. Mutation containment (per Rigby SIGN protocol — extends S2894 §5a)

**Mutating actions deferred to Slice 1.5b (29 total):**

| Action | Auth | Scope | Blast radius | Deferral rationale |
|---|---|---|---|---|
| `run` | staff | GLOBAL | Triggers real autopilot evaluation cycle; can persist blocks, downgrades, freeze flags, containment plans | Staged-enforcement session needed to verify actor_user_id trail + validate policy outcomes end-to-end |
| `config` (write variant) | staff | GLOBAL | Config is currently code-level per response note; changing thresholds requires a deploy | No runtime write path this ship |
| `experiment_create` | owner-or-staff | GLOBAL | Creates real Experiment row with treatment_params | Need paired lifecycle (create → start → observe → promote/rollback) |
| `experiment_start` | owner-or-staff | GLOBAL | Activates a draft experiment — applies treatment params in prod | Paired with experiment_create |
| `goal_set_weights` | staff | GLOBAL | Updates goal objective weights (5 canonical weights, auto-normalized) — shifts allocator behavior fleet-wide | Fleet-wide blast radius; needs before/after utility snapshot protocol |
| `release_freeze` | staff | GLOBAL | Freezes ALL deploys | Emergency-only surface; test needs paired unfreeze + audit |
| `release_unfreeze` | staff | GLOBAL | Unfreezes deploys | Paired with release_freeze |
| `outreach_approve` | owner-or-staff | 1 draft | Approves + schedules send (respects DAILY_APPROVAL_CAP) | A4 warm-up hard-throttle in force per S2846 — max 3-5 total sends; won't stage this ship |
| `outreach_reject` | owner-or-staff | 1 draft | Prevents re-queue for that lead | Owner-only path; paired with approve |
| `outreach_generate` | owner-or-staff | multi-lead | Generates touch=1 OutreachDrafts (DAILY_GENERATE_CAP=5); round-robins across offers | Bulk write; A4 throttle applies |
| `close_pack_generate` | owner-or-staff | 1 opportunity | Creates proposal + contract + invoice for an opp | Needs paired approve + follow-up in same session |
| `close_pack_approve` | owner-or-staff | 1 pack | Approves close pack + schedules follow-up | Paired with generate |
| `engagement_classify` | owner-or-staff | 1 event | Sets intent; auto-suppresses unsubscribes | Needs real inbound event fixture |
| `engagement_draft_reply` | owner-or-staff | 1 event | Sets draft reply for approval | Paired with approve_reply |
| `engagement_approve_reply` | owner-or-staff | 1 event | Approves + sends reply | Paired with draft_reply |
| `engagement_disqualify` | owner-or-staff | 1 event | Disqualifies (blocks further outreach for that engagement) | Owner-only path |
| `meeting_create` | owner-or-staff | 1 meeting | Schedules a real meeting (creates calendar entry substrate) | Needs paired brief + recap for lifecycle test |
| `meeting_brief` | owner-or-staff | 1 meeting | Generates pre-call brief | Paired with meeting_create |
| `meeting_recap` | owner-or-staff | 1 meeting | Adds post-meeting notes + recap draft | Paired with meeting_create |
| `governance_set_mode` | staff | GLOBAL / agent / desk | Sets autonomy mode (normal/throttle/freeze/safe_mode) with optional ttl_hours | Blast radius scoping (global/agent/desk) needs careful test-scaffolding |
| `governance_kill_switch` | staff | GLOBAL / target | Activates emergency kill switch (scheduler/queue/agent_family/publishing/outbound/deploys) — ttl_hours ≤72 | Emergency-only; paired with deactivate |
| `governance_deactivate_switch` | staff | 1 switch | Deactivates a kill switch by switch_id | Paired with kill_switch |
| `backfill_impacts` | staff | multi-day | Scans historical wager settlements + deliverable events + confirmed revenue to CREATE ImpactEvent rows (14-day default, 90 max). Idempotent per-row | Data-substrate write; needs idempotency verification post-write |
| `backfill_failure_reasons` | staff | multi-session | Re-classifies UNKNOWN failure codes on DeliberationSession rows — `s.save(update_fields=['failure_reason_code'])` per handler `td_handlers_ops.py:4276-4278` | Verified as mutation via handler read; deferred per Batch E confirmation |
| `security_containment_plan` (dry_run=false + confirm=true) | staff | GLOBAL | Applies containment recommendations (rate limiting, investigation flags, expired switch cleanup) | S1228 PR-A gate — belt-and-suspenders default; keep in mutations bucket until we have a paired scenario |

**Protocol (extends S2894 §5a):**

1. Read-only sweep first (this ship). Ship at `validated_partial`.
2. Mutations sweep in a dedicated Slice 1.5b session. Canary containment TBD per-action: some (`run`, `governance_set_mode`, `release_freeze`) are inherently global and can't be canary-scoped; those need a paired revert protocol. Others (outreach/close_pack/engagement/meeting families) operate on single rows and can canary to synthetic test data.
3. Some paired actions (`experiment_create` + `_start`; `outreach_approve` needs a draft first, which needs `outreach_generate`; `close_pack_generate` needs an opportunity_id; `meeting_create` before `_brief`/`_recap`) require lifecycle scaffolding — test protocols for each family.
4. A4 warm-up hard-throttle (S2846) governs outreach mutations — even in the mutation-sweep session, actual sends stay under the 3-5 total intro cap.
5. Slice 1.5b closes with category upgrade to `validated_full` and rolls up any Ledger rows from mutation-side observation.

## 6. Evidence

### 6.1 Tier-1 Evidence Ledger — all 76 read-only dispatches

| # | Action | Params variant | Success | Key metric(s) | Latency (ms) | Notes / anomalies |
|---|---|---|---|---|---|---|
| 1 | `status` | default | ✓ | total_actions_ever=109; blocks_last_24h=0; cadence=10m | 12 | deploy_sha=9c516ddfc149 |
| 2 | `history` | limit=100, include_evidence=true, selected_fields=[6 paths] | ✓ | count=100; DBZ workspace_budget_* rows present | 10 | Ledger Row A discriminator — see appendix §7.1 |
| 3 | `config` | default | ✓ | 7 thresholds visible | 2 | note: "changing thresholds requires deploy" (read-only as called here) |
| 4 | `dry_run_report` | default | ✓ | 5 proposed actions; SLO breaches=0; timeout spikes=0 | 1252 | 1 content_sweep + 4 auto_resolve (predictionmarketanalyst items) |
| 5 | `drift_scan` | default | ✓ | critical=0; warning=10 | 303 | 2 schema/handler mismatches (db_health_tool, mission_verdict) + 8 agent-registry orphans |
| 6 | `budget_report` | default | ✓ | daily=$12.92/$100.00 (13%); 1246 calls | 11 | PersonalAssistant $12.84 top spender |
| 7 | `roi_report` | default | ✓ | total=$12.93; outcomes=0 | 40 | 0/5 agents have quality data |
| 8 | `scheduler_report` | default | ✓ | pressure=normal; defers_24h=0; downscopes_24h=0 | 13 | 9 deferable tasks; 7 downscope-capable |
| 9 | `tuning_report` | default | ✓ | overrides=0; recommendations=0 | 23 | 7d effectiveness: 0 actions across all policies |
| 10 | `portfolio_report` | default | ✓ | 72h total_cost=$37.06; total_impact=$0 | 8 | content desk IQROI=200 w/ insufficient_data=true (bookkeeping inconsistency) |
| 11 | `attribution_report` | default | ✓ | 72h total_events=0; attributed=0 | 16 | window-empty (upstream ImpactEvent producers idle) |
| 12 | `attribution_debt_report` | default | ✓ | 24h debt=$0.0016 (0.0%); mapped_agents=63 | 20 | reallocation not blocked; status=healthy |
| 13 | `policy_conflict_report` | default | ✓ | conflicts=0; flap_knobs=0; registered_knobs=18 | 21 | (first dispatch transient-glitched; retry clean) |
| 14 | `latest_overrides_snapshot` | default | ✓ | found=true; knob_count=14; cycle_id `b9907ed8-…` | 4 | (first dispatch transient-glitched; retry clean) |
| 15 | `decision_ledger_report` | days=1 | ✓ | total_entries=38 (action_taken=2, no_op=36); 1 cycle | 11 | policies: content_pipeline_sweep + governance_auto_decision fired |
| 16 | `decision_ledger_report` | days=7, decision_type=action_taken | ✓ | total_entries=2 (both action_taken) | 5 | scope filter applied correctly |
| 17 | `timeout_ladder_report` | default | ✓ | agents_on_ladder=0 | 6 | recent_actions=[] |
| 18 | `deliberation_pipeline_report` | default | ✓ | total_sessions=0; failure_rate_pct=0.0; ladder_level=0 | 10 | normal operation |
| 19 | `backlog_report` | default | ✓ | publish_ready=150; draft=3; blocked=36; archived=495 | 31 | **FLAG:** governor_level=1 "Generation throttled" active since 2026-06-24 (~28 days) |
| 20 | `goal_report` | default | ✓ | 5 weights; general utility=0.7 (highest); confirmed_revenue metric=0.0 | 24 | goal weights auto-normalized |
| 21 | `experiment_report` | default | ✓ | active_experiments=0 | 4 | supported: 3 policies × 5 metrics |
| 22 | `release_report` | default | ✓ | frozen=false; level=L0 observing; error_rate=0.0 (6h) | 5 | last_deploy_sha=9c516ddfc149 |
| 23 | `revenue_pipeline_report` | default | ✓ | total_active=0; health=healthy | 16 | **Note:** scope mismatch with `revenue_full_pipeline` — see §5 |
| 24 | `revenue_full_pipeline` | default | ✓ | total_active_items=125 (all outreach.draft); expired opportunities=2631 | 22 | 125 outreach drafts pending approval |
| 25 | `revenue_funnel` | default | ✓ | 30d leads_created=125; overall_conversion=0.0 | 12 | downstream stages all zero |
| 26 | `revenue_forecast` | default | ✓ | weighted_forecast=$0.00; pending_outreach=125 | 19 | all forecast components 0 |
| 27 | `prospecting_queue` | default | ✓ | queue_size=6; score=45 (all leads) | 39 | **FLAG:** all 6 leads have empty `title` field (financial spiders) — Ledger candidate |
| 28 | `lead_source_report` | default | ✓ | month_count=1253; week_count=147; trend=declining | 17 | sources almost entirely financial spiders |
| 29 | `outreach_inbox` | default | ✓ | total_pending=125; remaining_approvals=10 | 7 | drafts truncated (payload cap); all touch=1 |
| 30 | `outreach_metrics_report` | default | ✓ | total=125; by_status.draft=125; avg_score=50 | 4 | offers: ai_automation 51 / content_engine 49 / consulting 25; reply_rate=0 |
| 31 | `close_pack_inbox` | default | ✓ | total_draft=0; pipeline_value=$0.00 | 8 | empty (expected — no close packs generated) |
| 32 | `close_pack_metrics_report` | default | ✓ | total=0; win_rate_pct=0 | 11 | empty |
| 33 | `close_pack_followup_queue` | default | ✓ | due_count=0; upcoming_48h=0 | 4 | empty |
| 34 | `close_pack_risk_report` | default | ✓ | total_active_packs=0; flag_count=0 | 2 | empty |
| 35 | `close_pack_velocity` | default | ✓ | pipeline_count=0; avg_close_days=0 | 6 | empty |
| 36 | `engagement_inbox` | default | ✓ | total_unread=0; total_needs_reply=0 | 8 | empty |
| 37 | `engagement_metrics_report` | default | ✓ | total=0; conversion_pct=0 | 6 | empty |
| 38 | `engagement_sla_queue` | default | ✓ | total=0; breach=0 | 3 | empty |
| 39 | `engagement_meeting_suggestions` | default | ✓ | needs_meeting_count=0; already_booked=0 | 2 | empty |
| 40 | `engagement_conversion_report` | default | ✓ | 30d total_engagements=0; reply_rate_pct=0 | 16 | empty |
| 41 | `meeting_inbox` | default | ✓ | total_scheduled=0 | 4 | empty |
| 42 | `meeting_metrics_report` | default | ✓ | total=0; upcoming=0 | 4 | empty |
| 43 | `governance_status` | default | ✓ | global_mode=normal; active_kill_switches=0; overrides=0 | 9 | budget_flags all empty; clean |
| 44 | `governance_throttle_report` | default | ✓ | current_mode=normal; spend_pct=13.4% ($100 cap); active_throttles=0 | 9 | diagnosis: "no constraints detected" |
| 45 | `governance_audit` | default | ✓ | recent_state_changes=0; recent_kill_switches=0 | 3 | clean |
| 46 | `knowledge_health` | default | ✓ | healthy=true; citations violations=0 (24h/7d); 72 active spiders | 41 | 261 spider records in 24h; 1288 in 7d |
| 47 | `knowledge_citation_report` | default | ✓ | 7d violations=0; block_rate=0 | 7 | clean |
| 48 | `knowledge_source_report` | default | ✓ | sources_7d=469; top spider=theodds (70 records) | 26 | top spiders all avg_relevance=70 |
| 49 | `knowledge_staleness_report` | default | ✓ | 3 stale data types | 29 | **FLAG:** intelligence + opportunity both 939.8h stale (~39 days); opportunity_seed 82h stale |
| 50 | `growth_candidates` | default | ✓ | candidates=20 (mostly governance/ratification deliverables) | 26 | rank_score=0.827 for top; none exported |
| 51 | `growth_schedule` | default | ✓ | 7d exports=2 (both PDF); daily_limit=40; rate_used=0.0% | 5 | 2 recent PDFs (S2841 discovery + S2840 canonical) |
| 52 | `growth_channel_report` | default | ✓ | 30d exports=31; engagement_events=1195; unused_formats: docx/html/json/markdown | 19 | PDF-only distribution |
| 53 | `growth_funnel` | default | ✓ | 30d candidates=430; exported=31; engage_rate_pct=1338.7% | 11 | **Doc:** engage_rate is events-per-candidate (not unique-rate) — annotate |
| 54 | `capacity_forecast` | default | ✓ | 24h tasks=3845; failure_rate=0.0; p95=9.21s | 51 | PA queue avg_duration=48.15s; broadcast 1608 tasks |
| 55 | `capacity_bottleneck_report` | default | ✓ | slow_tasks=4; memory_hogs=7+ | 29 | **FLAG:** process_pa_chat_task avg=48.15s (127 runs); rigby_documentation_manager_daily avg_delta=726 MB |
| 56 | `capacity_throttle_plan` | default | ✓ | needs_action=false; recommendations=0 | 11 | governance_mode=normal |
| 57 | `capacity_budget_envelope` | default | ✓ | 7d spend=$62.06; daily_avg=$8.87 vs cap=$5.00 (**177.3%**) | 66 | **FLAG:** corroborates Ledger Row A — global daily_avg is >cap yet no freeze; PA queue 29289s across 608 tasks |
| 58 | `value_events_report` | days=7 | ✓ | agent_completions=359; deliverables=138; revenue=$0 | 27 | top agents: SportsOddsAnalyst(90), PredictionMarketAnalyst(82), ArbitrageDetector(82), Rigby(77) |
| 59 | `value_outcome_rates` | days=7 | ✓ | agent_success=0.93; deliverable_quality=0.797; outreach→meeting=0.0 | 20 | avg_quality=0.568; outreach_count=20 |
| 60 | `value_usage_gaps` | days=7 | ✓ | gap_count=2 (1 critical, 1 warning) | 10 | **FLAG:** SystemIntelligenceAgent fail_rate=57% (4/7 CRITICAL); 20% deliverables q<0.3 (warning) |
| 61 | `value_realization_summary` | days=7 | ✓ | healthy=false; usage_gaps=2 | 22 | rolled up: outreach_count=125, meeting_count=0, avg_quality=0.547 |
| 62 | `security_permission_drift` | default | ✓ | issue_count=0 (24h) | 14 | clean |
| 63 | `security_abuse_queue` | default | ✓ | flag_count=0 (24h); has_critical=false | 4 | clean |
| 64 | `security_containment_plan` | default (dry_run=true) | ✓ | recommendation_count=0; needs_human_review=false | 8 | **verified `dry_run: true` echo** (S1228 PR-A gate) |
| 65 | `security_secrets_scan` | default | ✓ | finding_count=0 (7d); scanned_deliverables=138 | 40 | has_exposure=false |
| 66 | `compliance_pii_scan` | default | ✓ | finding_count=0 (7d); has_pii=false | 90 | clean |
| 67 | `compliance_retention_report` | default | ✓ | violation_count=0 | 16 | thresholds: agent_execution 90d / audit_log 180d / spider_data 60d / memory 365d |
| 68 | `compliance_access_audit` | default | ✓ | anomaly_count=0 (24h); has_anomalies=false | 9 | clean |
| 69 | `compliance_report` | default | ✓ | risk_level=low; healthy=true | 105 | pii/retention/access all clean |
| 70 | `integrity_quality_report` | default | ✓ | issue_count=0; sources_checked=30 | 157 | has_issues=false |
| 71 | `integrity_null_spike_scan` | default | ✓ | spike_count=96 (all critical) | 156 | **NOISE:** all at null_rate=1.0 on processed_data + embedding_text — likely "not-populated-by-design" fields; see §5 |
| 72 | `integrity_duplicate_report` | default | ✓ | duplicate_count=20; wasted_records=97 | 5 | 11+ spiders with small dup clusters; internal sources dominate |
| 73 | `integrity_reliability_scores` | default | ✓ | sources_scored=40; avg_reliability=0.99 | 596 | grade dist: A=38 / B=2 / C=0 / F=0; B's = opportunity_outreach_seed + huggingface (freshness=0.5) |

**Coverage summary:** 76 unique read-only actions × ~82 total dispatches (a few repeats + variants). All exercised successfully. Median latency ~15ms; p95 ~300ms; max 1252ms (`dry_run_report`).

### 6.2 Group-by-family narrative (Tier-1 grouped observations)

**READS_CORE (5 actions):** clean baseline. `status` shows 109 total AutopilotAction rows since substrate deploy; `history` was used as the Ledger Row A discriminator vehicle; `config` surfaces 7 code-level thresholds (write-path requires deploy — read-only as called here); `dry_run_report` completed in 1.25s and returned 5 proposed actions (mostly `auto_resolve` for predictionmarketanalyst items); `drift_scan` surfaced 10 warnings across schema/handler mismatches (`db_health_tool`, `mission_verdict`) and agent-registry orphans (8 rows including case-sensitivity duplicate `Rigby` vs `rigby`).

**BUDGET / ROI / SCHEDULING (5):** system in `normal` mode across all three surfaces. GLOBAL budget $12.92 / $100 = 13% utilization (24h). Top spender: `PersonalAssistant` ($12.84, 649 calls). ROI report shows 0 outcomes across 5 agents with quality data — quality signals not accumulated yet in this window. Scheduler shows 0 defers/downscopes in 24h, pressure=normal. Tuning report shows 0 overrides + 0 recommendations across 7d — self-tuning idle. Portfolio report has one bookkeeping oddity: `content` desk shows `iqroi=200` in `active_allocations` but `insufficient_data=true` in its desk row, so the 200 value doesn't drive real allocation multiplier (allocation=1.0). Non-blocking.

**ATTRIBUTION / DEBT / POLICY / LADDERS / BACKLOG / GOALS / EXPERIMENTS / RELEASE (14):** all clean or empty-by-design. Attribution debt at 0.0% ($0.0016 unattributed) — well below 20% warning / 40% critical thresholds. Policy conflict report: 0 conflicts across 18 registered knobs. Latest overrides snapshot: 14 knobs live (goal_allocation + desk_allocation across 6 desks + backlog_governor). Timeout ladder empty (no timeout-ladder agents). Deliberation pipeline: 0 sessions in 6h window. Backlog governor at L1 (throttled, active since 2026-06-24). Goal weights auto-normalized 5-way (general utility highest at 0.7). Experiment engine idle (0 active experiments; 3 supported policies × 5 metrics registered). Release L0 observing (last deploy 9c516ddfc149, error_rate=0.0 over 6h).

**REVENUE PIPELINE / OUTREACH READS (8):** 125 outreach drafts stuck at `status=draft` (all touch=1, `by_offer` split ai_automation=51 / content_engine=49 / consulting=25). Downstream stages all zero — no drafts approved, no replies received, no meetings scheduled. Consistent with A4 warm-up hard-throttle (S2846). Prospecting queue: 6 leads from financial spiders (all empty `title` fields — see §5 anomaly + Ledger candidate). Lead source report shows 1253 records in 30d, declining trend, sources overwhelmingly financial. `revenue_pipeline_report` and `revenue_full_pipeline` disagree on `total_active` because they scope differently — noted in §5.

**CLOSE PACK / ENGAGEMENT / MEETINGS (12):** all substrates empty (0 rows across every action). Consistent with pipeline stalled at outreach-draft stage — no drafts approved → no engagement → no meetings → no close packs.

**GOVERNANCE READS (3):** clean — global mode=normal, 0 active kill switches, 0 overrides, 0 active throttles, budget_flags all empty. `governance_throttle_report` diagnosis: "no constraints detected". `governance_audit` shows 0 recent state changes + 0 recent kill switches.

**KNOWLEDGE (4):** system healthy — 0 citation violations across 24h + 7d windows, 72 active spiders producing 1288 records/7d. `knowledge_source_report` shows theodds top (70 records/7d), then kalshi/legislation/financial (45 each). Staleness report flags 3 data types: `intelligence` (939.8h / ~39 days), `opportunity` (same), `opportunity_seed` (82h / 3.4 days). The intelligence + opportunity staleness likely reflects a paused upstream producer worth investigating.

**GROWTH (4):** low distribution activity. 30d exports=31 (all PDF; 4 formats unused: docx/html/json/markdown). 30d engagement_events=1195 (mostly synthesis_viewed=766 and status_transition=398). Growth funnel: 430 candidates → 31 exported → 415 engaged → 0 actions_taken. The engage_rate 1338.7% is events-per-candidate, not unique-engaged-rate (Rigby confirmed — see §5).

**CAPACITY (4):** system healthy under current load — 24h task count 3845 with 0 failures, p95 latency 9.21s. Bottleneck report flags 4 slow tasks (`generate_curated_action_cards` 81.6s single-run, `rigby_documentation_manager_daily` 57.3s, `core.tasks.process_pa_chat_task` 48.15s × 127 runs, `chief_of_staff_morning_brief_run` 37.8s single-run) + 7+ memory hogs (largest: `rigby_documentation_manager_daily` avg_delta=726 MB single-run). **capacity_budget_envelope substantiates Ledger Row A** — 7d daily_avg spend is $8.87 vs $5.00 cap = 177.3% utilization, yet workspace_budget freeze is not active (see §Related).

**VALUE (4):** system healthy at agent-completion + deliverable-quality dimensions (0.93 / 0.797), unhealthy at usage-gap dimension. 2 gaps: `SystemIntelligenceAgent` 57% fail rate (4/7 executions, severity=critical) + 20% of 138 deliverables at quality<0.3 (severity=warning). Rolled-up `value_realization_summary`: `healthy=false` because of the 2 gaps.

**SECURITY / COMPLIANCE (8):** all clean — 0 permission drift issues, 0 abuse flags, 0 secrets exposures, 0 PII findings, 0 retention violations, 0 access anomalies. `security_containment_plan` verified `dry_run: true` echo (S1228 PR-A gate behaving as spec'd) with 0 recommendations. `compliance_report` risk_level=low, healthy=true.

**INTEGRITY (4):** mixed. `integrity_quality_report` finds 0 issues across 30 sources (all null_rate=0.0). `integrity_reliability_scores` gives A=38 / B=2 / C=0 / F=0 across 40 sources (99% avg reliability). But `integrity_null_spike_scan` returns 96 critical spikes at null_rate=1.0 on `processed_data` + `embedding_text` fields across ~20 spider families — working hypothesis is these are fields not populated by design for those spider intake stages (see §5). `integrity_duplicate_report` finds 20 duplicate clusters (97 wasted records) mostly with `source_url=internal`.

### 6.3 Runtime-not-executed — this ship

- All ~29 mutation actions per §5a table.
- `history` with `include_evidence=false` (default) shape — schema-verified but not live-observed this ship.
- `history` with a payload-cap or empty-selected_fields projection edge case.
- `security_containment_plan` with `dry_run=false, confirm=false` (expected error — belt-and-suspenders gate).
- `experiment_report` with active experiments present (state-empty at time of this ship).
- `governance_status` / `_audit` with active overrides or kill switches present (state-empty at time of this ship).
- Any action executed by a non-staff user (all dispatches this ship ran as `chris`, staff+superuser).

---

## 7. Raw evidence appendix (Tier-2)

### 7.1 Ledger Row A discriminator — `history` scan for DBZ workspace_budget rows

**Purpose:** S2894 Ledger Row A observed DBZ workspace_budget substrate with `daily_total=$12.52` vs explicit `cap=$5.00` (250% over) and `is_frozen=false, is_downgraded=false`. S2894 could not run the discriminator (needed `autopilot_tool.history`, reserved for Slice 1.5). This ship ran it as the Batch A sharpening probe.

**Dispatch:**
```
autopilot_tool  action=history  limit=100  include_evidence=true \
  selected_fields=['evidence.workspace_id','evidence.daily_total','result.reason','result.cap','evidence.trigger','evidence.actor_user_id','evidence.simulated']
```

**Response — first 3 DBZ workspace_budget rows (projected):**

```
1) workspace_downgrade_set
   workspace_id: b4503364-2573-4401-9e28-61a739e0ce50
   daily_total: 3.068896        (61% of the $5.00 cap)
2) workspace_downgrade_cleared
   workspace_id: b4503364-2573-4401-9e28-61a739e0ce50
   daily_total: 2.980636        (60% — hysteresis clear threshold)
3) workspace_downgrade_set
   workspace_id: b4503364-2573-4401-9e28-61a739e0ce50
   daily_total: 2.977624
```

No `simulate_enforcement` rows observed in the top-100 slice. No `workspace_freeze_*` rows observed either — only downgrade/clear pairs.

**Interpretation (revised at Rigby T2 SIGN):** the enforcement DID fire historically — 17 events across 7d in S2894's `enforcement_report`. But the observed `evidence.daily_total` values at decision time ($3.07 / $2.98 / $2.98) are much lower than the current `daily_total=$12.52`. Rigby's T2 tool-grounded read of the history rows surfaced `result.reason: operator_cap_change_hysteresis` explicitly on the downgrade_set → downgrade_cleared pairs — this cleanly supports **bucket (a) as the primary working hypothesis** rather than an enforcer-side bypass:

- **(a) [PRIMARY] Historical spend was lower + operator cap changes triggered hysteresis oscillations** — earlier in the 7d window operators changed the DBZ cap (visible via `operator_events_count=11` in S2894 §6.1), each cap-change re-evaluated against the current sliding 24h spend and produced hysteresis pairs at $3.07/$2.98 (right at the 70%/60% thresholds for whatever the cap was at those moments). Recent PA-heavy activity has pushed daily_total to $12.52 but no new operator cap change has occurred to re-trigger evaluation — and the automatic enforcement cycle only writes a state-transition event when the flag actually flips (already-cleared workspace at time of last transition, no subsequent transition).
- **(e) [DEPRIORITIZED — hold pending stable-cap reproduction] Enforcer spend calc excludes PA critical-agents** — the `llm_enforcer.py:271` `_critical_agents` bypass at call time is documented; whether the ENFORCEMENT DECISION path ALSO excludes PA calls from the spend-sum query is not proven by this ship's evidence. The oscillation we observed at $3.07/$2.98 is explained without invoking a spend-side bypass. Bucket (e) becomes relevant only if we reproduce "$12.52 daily_total, no freeze, no cap change" under a stable cap window with a fresh cycle firing — an S2896+ probe.

**Corroborating evidence — `capacity_budget_envelope` row 57 in the Evidence Ledger:**
```
7d spend_total = $62.06
daily_avg = $8.87 vs cap = $5.00 → utilization = 177.3%
projected_monthly = $265.98
```

Global 7d daily-avg is also >cap. Interpretation under bucket (a): global cap of $100 (from `budget_report`) means the global daily-avg of $8.87 is 8.87% utilization — nowhere near the 70% soft limit. So global freeze not firing is expected, NOT corroborating a per-workspace bypass. The `capacity_budget_envelope`'s `budget_cap_daily_usd=5.0` field appears to be a per-desk or default reference (needs clarification), not the global budget the governor evaluates against.

**Ledger row disposition (routed to Rigby Tool Gap Ledger `5c84e75a-…`):** DBZ enforcement pattern is best explained by operator-cap-change hysteresis (bucket a). Log as a doc-clarity item: annotate `enforcement_report` output to include the hysteresis-oscillation shape so operators reading multiple downgrade_set/cleared pairs don't misread as "enforcer flapping". Bucket (e) probe deprioritized unless reproduced under stable-cap conditions.

**deploy_sha correlation (per Rigby T1 Q4 add):** all DBZ workspace_budget rows observed carried `deploy_sha` field; correlating decision-time to a specific deploy state is possible on demand. Not surfaced inline here to keep payload compact.

### 7.2 `security_containment_plan` — S1228 PR-A gate verification

Full raw response (small, worth including as sole exemplar of the belt-and-suspenders pattern):

```json
{
  "action": "security_containment_plan",
  "dry_run": true,
  "risk_summary": {"drift_issues": 0, "abuse_flags": 0, "has_critical": false},
  "recommendations": [],
  "recommendation_count": 0,
  "needs_human_review": false
}
```

Verified: `dry_run: true` echoed even though the dispatch payload contained no `dry_run` key — the handler default is `true`, per Session 1228 PR-A belt-and-suspenders (defends against GPT-5.2 autofilling `dry_run=False` to bypass the preview gate). Mutation variant (`dry_run=false, confirm=true`) explicitly deferred to Slice 1.5b.

### 7.3 `drift_scan` — 10 warnings, no critical

Summary of findings (full JSON in the tool_runs log — trimmed here):

**Schema/handler mismatches (2):**
- `db_health_tool`: schema defines actions `['overview', 'migrations', 'tables', 'pgvector', 'verify_table', 'search_tables', 'learning_stats', ...]` but not all appear in handler source. GPT may request actions the handler doesn't implement.
- `mission_verdict`: schema defines `['certify', 'reject', 'defer']` but not in handler source.

**Agent-registry orphans (8):**
- `PersonalAssistant`, `Rigby`, `ShellTestRouter`, `System`, `ValidationCheckAgent`, `rigby`, `claude-code`, `3DGenerationAgent` — DB Agent rows without matching AGENT_MAP entries. Known persona/system agents; `Rigby` vs `rigby` case-sensitivity duplicate worth flagging separately if a cleanup arc opens.

None critical for this ship. Corroborates the ongoing "some Agent DB rows are persona shells" thread from S2887 audit.

---

## Related

### Ledger candidates surfaced this ship

1. **`prospecting_queue` returns leads with empty `title` fields.** All 6 leads returned by `prospecting_queue` at this ship had empty `title` fields (financial-spider sources: `sec_edgar`, `finnhub`, `polygon_finance`, `etherscan`, `yahoo_finance`, `financial`). Score 45 flat across all 6. Either the upstream lead-scoring path isn't extracting the title from these spider payloads, or the response projection is dropping it. Small; blocks operator triage because the queue is unreadable without titles. **Route:** Rigby Tool Gap Ledger deliverable `5c84e75a-…`.

2. **`integrity_null_spike_scan` false-positive noise pattern.** 96 critical spikes flagged at `null_rate=1.0` for `processed_data` + `embedding_text` fields across ~20 spider families. Working hypothesis: these are fields "not populated by design" for spider intake stages that don't produce embeddings. Needs either a per-field applicability rule in the detector or an allowlist of "expected-null" (spider, field) pairs to filter out the noise. **Route:** Rigby Tool Gap Ledger.

3. **`autopilot_tool.history` `selected_fields` — silent longer-list wipe (S2895 T2 live-observed).** When `selected_fields` contains longer projection lists (Rigby observed an 8-path list including `result.enforcement_tier`), the tool response echoed `selected_fields: []` — silently wiping the projection — while a 4-path retry echoed correctly. Wipe location is upstream of `td_handlers_ops.py:2521-2534` (which uses silent-ignore semantics but preserves valid paths per-item). Concrete operator footgun; either fix the batch-rejection behavior OR surface a warning on wipe. **Route:** Rigby Tool Gap Ledger.

**Deprioritized (per Rigby T2 correction):** DBZ enforcement bucket (e) probe. Rigby's observation of `result.reason: operator_cap_change_hysteresis` on the downgrade_set/cleared pairs cleanly explains the historical oscillations without invoking an enforcer-side PA-bypass. Bucket (e) becomes relevant only if reproduced under stable-cap conditions. Log the doc-clarity item instead: annotate `enforcement_report` output to include hysteresis-oscillation shape.

### Zoom-out fold rows (from Rigby SIGN §5 T1 + Q4 T2 pushback)

**Row 160 — 2-tier evidence template for large-surface tool sweeps.** Rigby S2895 T1 zoom-out: a ~72-action doc that dumps every raw response inline would set a precedent making future large-surface sweeps (close_pack family, entire outreach substrate, Slice 2 agents, `agent_control_tool` if it grows) produce unreadable validation docs mostly composed of raw report text. Proposed shape: **Tier 1** compact Evidence Ledger table + group-by-family narrative in the main doc; **Tier 2** raw JSON appendix only for discriminators/bugs/sole-exemplars. Mitigation shipped in THIS doc (§6.1 + §6.2 + §7) — the doc itself is the reference exemplar. Classification: **`same_pr_mitigatable`**. Rigby T2 AGREE'd on classification. Future promotion trigger: 1-2 more large-surface (>30 action) sweeps adopt the pattern cleanly → promote to a first-class sweep-methodology section OR a Playbook §7 (Testing Discipline chapter candidacy) amendment.

**Row 161 — sweep-arc pace not sustainable at current shape.** Rigby S2895 T2 Q4 zoom-out: even with the 2-tier template landed, ~400-line docs × 76 remaining untested tools × ~1-2 tools per session = ~50 sessions of validation before Slice 5 closes. Substrate is likely changing faster than validation completes. Proposed methodology shifts: (a) **family-level substrate audits** with shared templates + auto-generated action inventory tables instead of prose-heavy per-tool narratives, (b) **delete/merge low-signal tools first** — audit "should we validate this at all?" before validating, (c) **lightweight auto-harness** running all read-only actions nightly and writing a machine-checkable ledger (shape/latency/empty-state diffs) so the human doc becomes a thin interpretive layer over machine evidence. Classification: **`future_trigger`** — decision needed at S2896 open on whether to open a substrate arc (dedicated methodology session before continuing sweep) BEFORE running more sweep batches. Not `same_pr_mitigatable` because the changes require substrate work (auto-harness build, family-doc template extraction, tool-deletion authority scoping) that exceeds any single sweep-PR scope. Not `escalate_to_chris` today because we should first quantify what changing shape would save vs current-shape pace across 2-3 more Slice-1 close-out sessions — with hard data on which tools are low-signal vs high-signal.

### S2895 handoff

- `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md` (this session's handoff — written at close)

### Related tools

- `workspace_budget_tool` (S2894 `validated_full`) — per-workspace substrate; complementary to `autopilot_tool.budget_report` (global) + this tool's `attribution_debt_report`.
- `governor_tool` (S2893 `validated_full`) — agent-level circuit-breaker governance; `autopilot_tool.governance_*` operates at higher scope (global mode + kill switches).
- `ops_digest_tool` (S2893 `validated_full`) — reports include some overlap with `autopilot_tool.dry_run_report` + `status`; ops_digest is human-optimized narrative, autopilot_tool.dry_run_report is decision-substrate.
- `llm_enforcer.py:271` — `_critical_agents` list; load-bearing for interpreting bucket (e) of Ledger Row A.
- `AutopilotAction` model — the audit substrate this tool reads via `history` + writes via all mutation actions.
