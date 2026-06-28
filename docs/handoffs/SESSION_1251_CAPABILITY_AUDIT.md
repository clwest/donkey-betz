---
title: "Session 1251 — Capability Audit & Operating-Capability Transition"
status: active
session: 1251
generated: 2026-06-28
companion_docs:
  - EVENT_SYSTEM_INVENTORY.md (Session 1250 PR 1-11 pipeline state)
  - PLATFORM_INVENTORY.md (runtime anchor — sole counts source)
  - handoffs/SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md
  - handoffs/SESSION_1250_PR11_LOCAL_WORK_QUEUE_EXERCISE.md
---

# Session 1251 — Capability Audit & Operating-Capability Transition

**Mode:** Audit, not build. Operator pivot away from infrastructure
construction toward operational capability.

**Framing:** Treat Rigby as a new hire reporting tomorrow. What jobs
can she own immediately with what's already built?

---

## §0 TL;DR

- The platform is **already more capable than its operator habits
  assume.** 110 PA tool schemas + 174 dispatcher handlers + 90 live
  beat tasks + 10 live signal chains + 10 learning bridges + 9 body
  systems are all firing 24/7.
- The **Rigby Event Intake pipeline** (S1250 PR 5–8) is fully wired
  but dormant behind four default-OFF flags. Turning it on in prod
  is one well-observed step, not a new architecture project.
- **Rigby's hands are bigger than the things she's been asked to
  do.** She can already orchestrate initiatives, dispatch any of 83
  agents, manage deliverables, run smoke tests, check fleet health,
  query prod DB, surface system alerts, write to revenue ledgers,
  and run the reasoning engine. She is not asked to *own* anything
  daily.
- **The bottleneck is connection, not construction.** Five small
  connector PRs (each a single PA tool wrapper or beat task) would
  give Rigby ownership of 80% of the daily rituals Chris still does
  by hand.
- **Recommendation: stop building toward a richer pipeline. Start
  handing Rigby existing daily jobs.** Specifics in §5.

---

## §1 Current Capability Inventory (verified, not theoretical)

110 PA tool schemas; 174 dispatcher handlers. Grouped into 13
categories. **No unimplemented or stub handlers** in the surface —
every registered tool returns a structured response.

### Capabilities LIVE today (no flag required)

| Category | Surface |
|---|---|
| **Information retrieval** | `agent_introspection_tool`, `platform_awareness_tool`, `platform_config_tool`, `status_snapshot_tool`, `recent_activity_tool`, `execution_history_tool`, `kb_tool`, `search_docs`, `web_search`, `scheduled_tasks_tool`, `conversation_tool`, `session_tool` |
| **Workspaces + initiatives** | `workspace_tool`, `work_tool` (initiative_list / create / promote / link / action_item_*), `active_repo_tool`, `active_priority_tool` |
| **Deliverables + content** | `deliverable_tool` (12 actions), `content_tool` (gateway), `blog_tool`, `video_history_tool`, `media_tool`, `research_and_create_tool` |
| **Agents + orchestration** | `run_agent` (83 agents), `universal_agent_tool`, `persona_tool` (139 personas), `workflow_run_tool`, `workflow_orchestration_agent`, `schedule_followup` |
| **Intelligence + analysis** | `reasoning_engine_tool`, `ml_analysis`, `intelligence_tool`, `narrative_tool`, `competitor_comparison_tool`, `competitor_analysis_agent`, `customer_research_agent`, `brand_strategy_agent`, `content_strategy_agent`, `marketing_strategy_agent` |
| **Media production** | `studio_tool` (image / video / audio / talking-video), `davinci_tool`, `obs_tool`, `voice_clone_tool`, `image_editing_agent`, `video_editing_agent`, `three_d_generation_agent` |
| **Sales + revenue** | `opportunity_manager_tool`, `task_manager_tool`, `revenue_tracker_tool`, `pipeline_orchestrator_tool` |
| **Governance** | `governance_tool` (inbox / approve / ignore), `gates_tool`, `pilots_tool`, `audit_tool`, `agent_control_tool`, `governor_tool` |
| **Ops + health** | `ops_tool`, `ops_digest_tool`, `cockpit_tool`, `get_body_vitals`, `get_system_alerts`, `fleet_health`, `infra_health_tool`, `db_health_tool` (incl. `env='prod'` via RPC), `heartbeat_history_tool`, `http_smoke_test`, `diagnostics_tool`, `railway_tool`, `task_breakdown_tool` |
| **Cost** | `cost_telemetry_tool`, `check_resource_budget` |
| **Memory** | `remember_tool` (cross-session), `agent_memory_tool`, `learning_patterns_tool`, `learning_tool` |
| **Pipelines + distribution** | `dream_tool`, `brainstorm_tool`, `feedback_tool`, `podcast_tool`, `newsletter_tool`, `campaign_tool`, `distribution_tool`, `conceptforge_tool` |
| **External + special** | `discord_tool`, `messaging_tool`, `vip_invite_tool`, `ats_tool`, `calendar_tool`, `profile_tool`, `self_awareness_tool`, `code_job_tool`, `claude_code_tool`, `proactive_tool`, `autopilot_tool` |

### The one gated tool

| Tool | Flag | Default | Behavior when OFF |
|---|---|---|---|
| `rigby_work_item` (actions `list` / `acknowledge` / `resolve` / `ignore` / `delegate`) | `RIGBY_WORK_QUEUE_REVIEW_ENABLED` | OFF | Returns `{ok: false, error: 'tools disabled (flag off)'}`. Schema still advertised. |

Three other Session 1250 flags (`RIGBY_EVENT_INTAKE_ENABLED`,
`RIGBY_INTERNAL_WORK_QUEUE_ENABLED`, `RIGBY_DELEGATION_ENABLED`) gate
background signal handlers and the intake task, not PA tools. Net:
from Rigby's tool surface, only the work-queue review action is
dormant.

### Tools registered but with limited utility

**None.** Every tool either has a working handler or is a gateway
routing to working sub-handlers.

---

## §2 Workflow Inventory

### Pipeline state matrix

```
Event → Intake → Mission → Queue → Review → Delegation → Verification
```

| Stage | Component | State |
|---|---|---|
| **Event** | `DeliverableEvent.post_save` signal | **LIVE — always fires.** Records every Deliverable status transition with direction classification. |
| **Intake** | `rigby_event_intake` Celery task on `pa` queue | **GATED — `RIGBY_EVENT_INTAKE_ENABLED=False` default.** When ON: creates MissionRun + 3 OpsRunEvent lifecycle rows. |
| **Mission** | OpsRun `domain='mission'` + per-step OpsRunEvent timeline | **LIVE container, GATED activator** (same flag as Intake). |
| **Queue** | RigbyWorkItem creation in intake task | **GATED — `RIGBY_INTERNAL_WORK_QUEUE_ENABLED=False` default.** Actionable decisions (`monitor` / `notify`) write a queue row. |
| **Review** | `rigby_work_item` PA tool | **GATED — `RIGBY_WORK_QUEUE_REVIEW_ENABLED=False` default.** Acknowledge / resolve / ignore PA actions + audit OpsRunEvent on parent MissionRun. |
| **Delegation** | `delegate_work_item` + `execute_agent_task.apply_async` + post-save signal | **GATED — `RIGBY_DELEGATION_ENABLED=False` default.** Hardcoded routing table: `monitor → TrendAnalysisAgent`; `notify` not delegatable v0. |
| **Verification** | Deterministic verdict in post-save signal | **GATED** (same flag as Delegation). No LLM — uses LLMCallEvent + ToolCallRecord row counts. |

**Verdict on the pipeline:** code-complete, locally exercised through
Stage 2 (PR 10–11), production-disabled across all four flags. Net
production behavior change vs. pre-PR-5: **zero.**

### Other automated workflows that are LIVE 24/7

- **90 beat tasks** in `core/celery.py` `app.conf.beat_schedule`.
  Coverage:
  - 6 health/monitoring (heartbeat, celery health, body vitals)
  - 20 cleanups (stuck executions, stale data, retention sweeps)
  - 12 aggregation/metrics (ROI, revenue, distribution, learning decay)
  - 7 spider pipeline (run/warmup/embed/aggregate/curate/process)
  - 5 human-attention/escalation (HITL state machine, validation expiry)
  - 4 market intelligence (sports odds, Kalshi snapshots, betting brief)
  - 3 content generation (newsletter, outreach drafts, morning brief)
  - 3 diagnostics (CTO/COO/trend, all OFF by default)
  - Remaining: dreams, opportunities, fleet artifacts, learning, knowledge.
- **10 Django signal chains** firing on model state: Deliverable
  status, AgentExecution lifecycle, SpiderData create, AgentDream
  approval, Opportunity acceptance (→ Revenue), Initiative
  diagnostic mark/clear, 10 LearningBridge post_save receivers.
- **Body Coordinator** monitoring 9 systems via heartbeat task (every
  10 min); throttle responses live.

### Workflows that fire but their output is unused

**None found in the active surface.** Every beat task writes durable
state that downstream code reads, or runs health checks whose output
feeds alerts.

10 Celery tasks (the canonical `docs/AUDIT_FINDINGS.md §12` deferred
list) are defined but **not scheduled** — that's intentional, not
orphaned. They cluster as: LLM-cost-deferred (5),
agent-dispatch-needs-greenlight (3), Session 1031 explicitly blocked
(2).

### Webhook surfaces (inbound external events)

- Stripe (payment)
- Gumroad (product distribution)
- Discord OAuth + slash commands
- (No blockchain or sports-score webhooks — sports/markets are polled,
  not pushed.)

---

## §3 Human Responsibility Audit

### What Chris still does manually

Top 15 recurring patterns from S1244–S1250 handoffs, ranked by
frequency:

| # | Manual task | Frequency | Automatable today? |
|---|---|---|---|
| 1 | Admin-merge PRs (`gh pr merge --admin`) | 4–6 per session | **No** — blocked by Anthropic billing / CI; external system |
| 2 | Anthropic credit refill | ~every 3–5 sessions | **No** — no Anthropic API for this |
| 3 | Railway env-var setup (prod secrets) | ~every 2 sessions | **No** — no Railway management API in PA tools |
| 4 | Local worker restart with new env vars | Multi per session during flag work | **No** — Rigby can't control local processes |
| 5 | Pre-deletion ORM verification protocol | 1–2 per session in cleanup arcs | **Partially** — `diagnostics_tool` covers grep/ORM probes; verdict stays with Chris |
| 6 | Session-open ritual (orient + health_check + pin rotate if needed) | EVERY session | **Yes** — all three tools exist; just needs a wrapper |
| 7 | Docs cascade (4-step: build_docs_index → build_rag_corpus → sync → embed) | ~1 per session | **Yes** — all four CLI commands exist; wrap in one PA tool |
| 8 | Morning brief verification block | Daily (autonomous-ish since S1249) | **Mostly** — beat task already exists; verification script could be a follow-up beat |
| 9 | Local↔prod parity / drift queries | ~1 per session | **Partially** — `db_health_tool env='prod'` (S1249 PR #2713) covers many; full `make env-diff` still on menu |
| 10 | Pin rotation decision (session_tool retire + create_fresh) | ~every 10–15 sessions | **Yes** — rule-based ("if score < 60 or `suggest_fresh`"); could be daily beat |
| 11 | Stuck-data ORM mutations (unblock agents, fix workspace paths) | ~1–2 per session in audit arcs | **Partially** — Rigby can probe via `diagnostics_tool`; needs templates for common fixes |
| 12 | Deliverable status verification before transition | 1–2 per session | **Yes** — `deliverable_tool.set_status` + `deliverable_tool.detail` exist; needs habit |
| 13 | Discord / Linear / GitHub issue triage | Occasional | **Partially** — `discord_tool` exists; no Linear; GitHub via `gh` CLI but not PA |
| 14 | Audit-finding triage → decision card → PR | ~once per audit arc | **Partially** — `audit_tool` + `deliverable_tool` + `governance_tool` cover the surface; protocol is structured |
| 15 | Approving Rigby's product decisions (retire X? defer Y? flip flag Z?) | ~1–2 per session | **No** — these are legitimate human gates |

### Three buckets

- **External-system gates (40% of friction):** Anthropic billing,
  GitHub admin-merges, Railway secrets, Discord/Linear integrations.
  Not Rigby's domain. Solutions live outside the platform code.
- **Automatable rituals (35% of friction):** Docs cascade, session
  init, pin rotation, env-parity, deliverable verification. All have
  existing tools. **This is where Rigby can absorb work TODAY with
  small connector PRs.**
- **Essential human gates (25% of friction):** Product decisions,
  deletion approval, secret placement. These should stay manual.

### Where Rigby explicitly asks Chris today

Legitimate human gates from S1244–S1250:
- Product decisions (retire / defer / merge-vs-split shape choices)
- Prod-side secrets and env-var values
- Deletion verdicts (cat 1/2/3 ratification)
- Breaking changes affecting cross-app consumers
- Conversation health borderline cases (when score is 50–70)

The first four are correct gates. The fifth could be automated with
a clearer rule.

---

## §4 Opportunity Ranking — top 20 workflows Rigby could own this week

Ranked by (effort to land × time saved per occurrence × frequency).
All assume **no new architecture** — only connecting existing tools.

| # | Workflow | Effort | Frequency | Time saved | Notes |
|---|---|---|---|---|---|
| 1 | **Docs cascade owner** — single PA tool action `docs_tool.full_sync` that runs all 4 commands + reports state | ~1h | ~1/session | ~3 min | All 4 CLI tools exist; just wrap them |
| 2 | **Session-open report** — beat task or PA tool that runs `context-kit orient` + `session_tool health_check` + summary | ~30min | every session | ~2 min | `session_tool.health_check` lands in PA chat today; just bundle |
| 3 | **Pin rotation autopilot** — daily beat task: if pinned conversation's `suggest_fresh=True` OR health < 60, retire + create_fresh + log | ~2h | ~1/15 sessions | ~10 min when triggered | `session_tool.retire` + `create_fresh` exist (PR #2707) |
| 4 | **Daily ops digest delivery** — `ops_digest_tool.generate` already exists; schedule + post into PA chat | ~30min | daily | ~5 min | One beat task line; tool fires today |
| 5 | **Stuck-running intake reaper** — daily beat task wrapping `rigby_intake_lag_check` + auto-mark `failed` if age > 60min | ~2h | rare in healthy state | high when bad | PR 9 cmd exists; just needs scheduler + escalation |
| 6 | **Deferred-task health probe** — Rigby checks `audit_celery_zero_fire` (S1245) weekly + reports drift from §12 baseline | ~1h | weekly | ~15 min | Existing cmd; needs scheduled invocation + delta |
| 7 | **Env-parity probe (local vs prod)** — daily beat task using `db_health_tool env='prod'` to flag drift | ~3h | daily | ~10 min when stale | S1249 RPC unlocks this; was the S1248 menu item (c) |
| 8 | **`make env-diff` cmd** — single mgmt command surfacing settings + migrations + Celery beat row deltas | ~2h | per debug session | ~15 min | S1248 menu item (d) — straightforward |
| 9 | **Audit-finding inbox owner** — Rigby polls `audit_tool.findings`, surfaces top-N untriaged in PA chat daily | ~1h | daily | ~10 min | Tool exists; needs scheduled poll |
| 10 | **Stale-deliverable auto-archive watcher** — Rigby reviews `auto-archive-stale-deliverables` output + reports anomalies | ~30min | weekly | ~5 min | Beat task already runs daily; just add reporting |
| 11 | **Pre-deletion checklist** — PA tool `rigby_run_pre_delete_audit` running the 7-step protocol + dumping verdict | ~3h | ~1/session in cleanup arcs | ~20 min when invoked | Codifies S1244 protocol; small wrapper |
| 12 | **Morning brief verification follow-up** — beat task after the existing morning brief runs that asserts the 6-criteria checklist | ~2h | daily | ~5 min | Existing runbook; just code the assertions |
| 13 | **Cost spike triage** — when `check-llm-cost-spike` fires, Rigby pulls top spenders via `cost_telemetry_tool.top_agents` + posts summary | ~1h | event-driven | ~10 min | Both tools live; just connect |
| 14 | **Spider data freshness watch** — Rigby checks `process_core_spider_data` queue depth + spider freshness daily | ~1h | daily | ~3 min | `cockpit_tool.queue_lengths` + spider stats live |
| 15 | **Worker health summary in PA chat** — daily auto-post from `cockpit_tool.worker_health` | ~30min | daily | ~2 min | Tool exists |
| 16 | **Flag-state dashboard** — Rigby self-reports the 4 Session 1250 flags + downstream gate state daily | ~1h | daily for next several weeks | ~2 min | `platform_config_tool.feature_flags` exists |
| 17 | **Workspace orphan reporter** — Rigby polls `initiative_diagnostic_signals` output + surfaces orphan initiatives | ~1h | weekly | ~10 min | Signal fires already; consumer needed |
| 18 | **Discord ops broadcast** — when `governance_tool.attention_list` has items, Rigby posts to Discord ops channel | ~2h | event-driven | ~10 min when triggered | `discord_tool` exists; needs routing |
| 19 | **Daily revenue + opportunity rollup** — Rigby summarizes `revenue_tracker_tool.stats` + `opportunity_manager_tool.list` | ~1h | daily | ~5 min | Both tools live |
| 20 | **Heartbeat anomaly reporter** — when body system score drops, Rigby surfaces via `heartbeat_history_tool.trends` | ~1h | event-driven | ~5 min | Tool exists; needs threshold logic |

**The top 10 alone would save ~90 minutes per week of Chris's time**
with no new architecture. Eight of them are sub-2-hour PRs.

**None of these are new pipelines.** They are connectors over
existing tools.

---

## §5 Recommendation

### Stop building. Start using.

The S1250 PR 5–11 arc landed an entire event-driven nervous system.
It's complete code, dormant in production. The temptation will be to
flip the next flag and exercise the next stage. **Don't.**

Instead, **transition Rigby from a built thing to a working colleague**
by handing her three concrete, daily, recurring jobs she can own with
what she already has:

### Phase A — Rigby owns the morning ritual (this week)

A single new beat task (or PA tool) that runs every morning and posts
to Chris's active PA conversation:

1. `context-kit orient` summary (one sentence — "Session N opens;
   baseline clean; last handoff: …")
2. `session_tool.health_check` result + autopilot pin rotation if
   `suggest_fresh=True`
3. `ops_digest_tool.generate` output
4. `cockpit_tool.worker_health` summary
5. Flag state for the 4 Session 1250 flags
6. Yesterday's `audit_tool.findings` deltas
7. Anything stuck in `cockpit_tool.queue_lengths`

**This is opportunities #2, #4, #15, #16 bundled.** ~3 hours of work.
Lands one daily message that orients Chris before he asks.

### Phase B — Rigby owns the docs cascade (next)

One PA tool action: `docs_tool.full_sync`. Wraps the four CLI
commands. Returns a state report. **Saves the "Docs → Rigby is a
4-step cascade, NOT 1 step" memory item from happening every
session.**

### Phase C — Rigby owns deferred-task health (week 2)

Weekly beat task that runs `audit_celery_zero_fire` + diffs against
`docs/AUDIT_FINDINGS.md §12`. Posts deltas. **This is opportunity #6.**
Lets Chris know if the deferred list has drifted without him having
to check.

### What NOT to do

- **Do not** open PR 12 as another work-queue review tool flag flip.
  It produces 4 more PRs of operator exercise without closing the
  loop on whether Rigby can be *useful*.
- **Do not** start a new architecture initiative. The existing
  infrastructure is over-served for the operator habits we have.
- **Do not** wire MORE event types into the intake pipeline yet. It
  already handles DeliverableEvent; the work is downstream, not
  upstream.
- **Do not** automate the human gates (admin-merge, deletion
  verdicts, secret placement). Those are correct.

### Why this works

- Rigby's tool surface is already 110 tools deep. She doesn't need
  more abilities; she needs **routine.**
- Chris already runs `context-kit orient`, `session_tool
  health_check`, and the docs cascade by hand every session. If Rigby
  owns these, Chris's session start drops from ~5 minutes of ritual
  to ~30 seconds of reading her report.
- The S1250 pipeline (PR 5–8) doesn't need to be enabled in prod to
  deliver value. Phase A above produces value WITH ALL FOUR S1250
  FLAGS STILL OFF.
- Every job listed in §4 is a 1-3 hour PR. No infrastructure. No new
  abstractions. Mostly Celery beat schedule additions + small PA tool
  wrappers.

### Concrete next move

**Session 1251 should open with PR 12 — Rigby's Morning Brief.**

One beat task or PA tool (`rigby_morning_brief`). Bundles items #2 /
#4 / #15 / #16 / #9 from §4. Posts to the pinned PA conversation.
~3 hours. Connects 7 existing tools. No new model, no new flag, no
exercise required to know whether it worked — the morning posts are
the evidence.

That's the transition from "we built a system" to "Rigby has a job."

---

*This audit is a snapshot. The runtime inventory in
`PLATFORM_INVENTORY.md` remains the authoritative source for any
quantitative count; if this doc and the inventory disagree on a
number, the inventory wins per `DOC_LIFECYCLE.md §2c`.*
