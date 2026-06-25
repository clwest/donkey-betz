---
title: "Morning Brief Spec — daily Chief-of-Staff brief for Chris"
status: active
session: 1232
generated: 2026-06-24
ratified: 2026-06-24 (Chris — "agree all" via Rigby decision card)
author: rigby (draft) + claude (capture)
companion_docs:
  - 00-START-NEXT-SESSION.md
  - docs/PLATFORM_INVENTORY.md
  - docs/UDB_BEHAVIOR_LAYER.md
arc: daily-CoS product wedge (Sessions 1232 → 1235)
---

# Morning Brief Spec — v1

> **Status:** v1 active. Drafted by Rigby in Session 1232 Priority 0
> Sub-step A consultation; ratified by Chris via "agree all" on the
> 7-question decision card (same session, same day). Drives Sub-step B
> (`WORKFLOWS['morning_brief']` template build), Sub-step C
> (workspace + PeriodicTask), Sub-step D (polish), Sub-step E
> (dogfood + iterate).

## Intent

A consistent, 5–7 minute morning read that:

1. Prevents "platform surprise" — Chris doesn't sit down to broken state.
2. Tracks competitive motion (change-only, not digest).
3. Surfaces what shipped + what's blocked across active initiatives.
4. Ends with explicit decisions Chris can act on today.

**Default structure:** 4 lanes (3 fixed + 1 rotating) + a Decision Card synthesis section.

**Read shape:** TL;DR at top → 4 lanes → Decision Card at bottom. Top of brief carries a single pointer: *"If you only read one thing: skip to the Decision Card."*

---

## Lane 1 (Fixed, Internal): Platform Readiness — Overnight Health + What's Broken

**Why this lane:** highest-signal because it directly drives what Chris can safely merge/ship today (beats, gates, failures, smoke outcomes).

**Dispatch prompt:**
> *Agent:* SystemIntelligenceAgent (or Ops/Autopilot surface).
> *Task:* "Generate the Morning Brief Lane: Platform Readiness. Summarize last 24h platform health: SLO breaches, failing Celery tasks, agent timeout spikes, governor/autopilot state, blocked agents, queue backlog, and any fleet app degradation. Include: top 3 issues by impact + recommended fix/owner."
> *Inputs:* `window=24h`; `include_breakdowns=true`; include `failure_signatures` top 5.

**Output shape:**
- **TL;DR:** 3 bullets (max 1 line each)
- **Main bullets:** 6–10 bullets total
- **Action items:** 3 max (each: *owner + next step + ETA*)
- **Citations:** internal only (tool outputs referenced by name; no web citations required)

**Source (agents + data feeds):**
- `ops_tool`: `overview`, `slo_status`, `failure_signatures`, `zombie_thread_rate`
- `cockpit_tool`: `queue_lengths`, `recent_failures` (if queues are hot)
- `fleet_health`: per-app degraded/unreachable
- `autopilot_tool`: `governance_status`, `dry_run_report` (if something is about to trip)
- (Optional) `gates_tool` if publishing/quality gates are blocking

---

## Lane 2 (Fixed, Internal): Build Focus — What moved + What's blocked

**Why this lane:** prevents the brief from drifting into news-only. Forces an initiative checkpoint per top initiative.

**Dispatch prompt:**
> *Agent:* COOAgent (or a lightweight "Build/Execution" agent).
> *Task:* "Generate the Morning Brief Lane: Build Focus. Summarize last 24h shipping delta and current execution focus: merged/ready-to-merge PRs, active initiatives, blocked action items, and anything needing Chris's approval. Emphasize only deltas and blockers."
> *Inputs:* `window=24h`; include PRs if available; include initiatives in ACTIVE/TRIAGE; include top 10 newest deliverables in DBZ workspace.

**Output shape:**
- **TL;DR:** 2 bullets
- **Main bullets:**
  - "Shipped / Ready" (3–6 bullets)
  - "Blocked / Risk" (3–6 bullets)
- **Action items:** 3 max (explicit approvals/merges/priority calls)
- **Citations:** internal references (initiative IDs, deliverable IDs, PR numbers if available)

**Source (agents + data feeds):**
- `work_tool`: `initiative_list (ACTIVE)`, `action_item_list (blocked/in_progress)`, `stats`
- `execution_history_tool` (optional): recent failures on key agents
- `deliverable_tool`: recent DBZ deliverables (ready/completed)
- `governance_tool`: `inbox` (if attention items exist)

---

## Lane 3 (Fixed, Product/Market): Competitive Landscape — Who shipped what overnight

**Why this lane:** Chris is building product + positioning; a "who shipped what" delta is useful when it's *change-only* (new launch, pricing, new feature, major PR), not a broad market digest.

**Dispatch prompt:**
> *Agent:* TrendAnalysisAgent (or ResearchAgent).
> *Task:* "Generate the Morning Brief Lane: Competitive Landscape for Donkey Betz. Provide a change-only snapshot (last 24–72h): notable launches, pricing changes, major feature releases, fundraising, or viral adoption signals among the closest AI agent/autonomous ops competitors. Limit to 2–4 competitors and only include items with clear evidence."
> *Inputs:* `timeframe=72h`; `competitor_shortlist=[predefined list]`; output must include links.

**Output shape:**
- **TL;DR:** 2 bullets ("1 threat / 1 opportunity")
- **Main bullets:** 5–8 bullets
- **Action items:** 1–2 max (e.g., "update positioning line," "ship wedge X this week")
- **Citations:** **required** for external claims (source URLs). If no credible sources found: output *"No verified competitive deltas found."*

**Source (agents + data feeds):**
- Spider data: producthunt / news / reddit / hn / tech-news feeds
- `intelligence_tool.search (web/spider)` for verification links
- Optional: `competitor_comparison_tool` *only when triggered* (not daily) to avoid scope blowup

---

## Lane 4 (Rotating, "Money/Signals"): One Focus Lane Per Day

**Why this lane:** market lanes are valuable but only when tied to Chris's current active positions/attention. Rotation prevents noise; overrides keep it responsive.

### Default rotation schedule (Mon–Fri)

| Day | Slot | Reason |
|-----|------|--------|
| **Mon** | AI Infra Deep Dive | Start-of-week architecture/infra updates influence what we build all week. |
| **Tue** | Competitor Wedge (Lane 3 deepen) | Tuesday is good for product positioning / GTM copy tweaks. |
| **Wed** | Ticker / Catalyst Watch | Mid-week market alignment; avoids daily ticker noise. |
| **Thu** | GTM / Pipeline Health | Forces revenue motion + approvals before week ends. |
| **Fri** | Sports OR Prediction Markets (alternating week A/B) | End-of-week best for optional lanes; rotate to prevent noise. |

If Chris prefers Sports as a fixed anchor, swap Fri ↔ Mon.

### Override triggers (replace the scheduled slot)

Priority order, highest first:

1. **Incident override** — if Lane 1 finds CRITICAL/P0 (fleet degraded, queues RED, deploy freeze, runaway failures) → Lane 4 becomes **Incident Focus** (remediation plan + owner assignment).
2. **Revenue override** — if there's a meeting today, close pack pending approval, or high-intent engagement needing reply → Lane 4 becomes **GTM/Pipeline Health** regardless of day.
3. **Signal override** — if signal aggregation exceeds threshold:
   - Sports: sharp signals above threshold in last 24–48h
   - Prediction markets: contract volume/odds shock
   - Stocks: unusual filings/catalyst within 7 days / high-confidence ML prediction shift
   → pick the relevant lane.
4. **Calendar override** — known events (earnings day, major sports slate, regulatory hearings) force the relevant lane.

### Dispatch prompt (base template)

> *Agent:* MarketIntelligenceCoordinator (or Intelligence Desk Agent for the lane).
> *Task:* "Generate the Morning Brief Rotating Lane: `<ROTATION_SLOT>`. Provide actionable signals only (not a news dump). Include 3–7 bullets with 'why it matters today' and an explicit action recommendation if applicable."
> *Inputs:* `slot=<sports|prediction_markets|tickers|gtm_pipeline|ai_infra_deep_dive>`; `timeframe=24–72h`; `max_items=7`.

### Output shape

- **TL;DR:** 1 bullet (max 1 line)
- **Main bullets:** 3–7 bullets (each must include *"why it matters today"*)
- **Action items:** 1–3 max (must be explicit: owner + next step)
- **Citations:**
  - **Required** when quoting prices/odds/contracts/filings (include source URL or internal tool reference).
  - If evidence is weak: label as *"unverified signal"* and do **not** recommend action beyond "monitor."

### Source (agents + feeds), by slot

| Slot | Agents | Feeds |
|------|--------|-------|
| Sports Edge Scan | `GamePredictor`, `LineMovementAnalyzer`, `SharpActionDetector` | odds/lines spiders + sharp-signal tables + wagers history (`intelligence_tool.sports_*`) |
| Prediction Markets | `PredictionMarketAnalyst` | prediction-market spiders + `intelligence_tool` market pulls (contracts/odds deltas) |
| Ticker / Catalyst Watch | `StockAnalystAgent`, `MarketIntelligenceCoordinator` | SEC filings, stock briefs, alerts (`intelligence_tool.stocks_*`) |
| GTM / Pipeline Health | `OpportunityPipelineAgent` (or autopilot revenue surfaces) | `autopilot_tool.revenue_full_pipeline` / `revenue_pipeline_report` + opportunities/tasks |
| AI Infra Deep Dive | `ResearchAgent` / `TrendAnalysisAgent` | spiders (framework releases / news), `intelligence_tool.search(source=web|spider)` for verification links |

---

## Decision Card — Today's Decisions / Asks

**Placement:** **Bottom** of the brief.

**Top-of-brief pointer:** *"If you only read one thing: skip to the Decision Card."*

**What feeds it (hybrid):**

Primary: **dedicated CoS synthesis dispatch** that ingests:
- Lane 1 output (Platform Readiness)
- Lane 2 output (Build Focus)
- Lane 3 output (Competitive deltas)
- Lane 4 output (Rotating focus)

Plus **guardrail tool reads** to prevent hallucinated "asks":
- `governance_tool.inbox` (pending attention/decisions)
- `work_tool.action_item_list` (blocked + high priority)
- `ops_tool.slo_status` (breaches → forced ask)
- (Optional) `autopilot_tool.governance_status` (if throttled/frozen → include as "ask")

**Output shape:**
- **1–3 decisions max** (hard cap)
- Each decision entry includes:
  - **Decision:** 1 sentence
  - **Recommendation:** 1 sentence
  - **Why now:** 1 bullet (evidence-linked)
  - **Next step:** owner + timebox (e.g., "Claude Code — by 11:00 AM MST")

---

## Workflow template skeleton — `WORKFLOWS['morning_brief']`

Bare step list (no code — what the workflow runner must dispatch in order). Each step lists agent + inputs (key names) + writes (key names produced).

### Pre-step: `rotation_slot_resolve`
- **Agent:** none (pure logic)
- **Inputs:** weekday, override flags (incident/revenue/signal/calendar)
- **Writes:** `rotation_slot` (resolved enum string)

### Step 1: `lane_1_platform_readiness`
- **Agent:** `SystemIntelligenceAgent` (or ops harness)
- **Inputs:** `window_hours`, `include_breakdowns`
- **Writes:** `lane_1_text`, `lane_1_findings[]`

### Step 2: `lane_2_build_focus`
- **Agent:** `coo_agent` (or COO persona)
- **Inputs:** `window_hours`, `initiative_statuses`, `workspace_id`
- **Writes:** `lane_2_text`, `lane_2_blocks[]`

### Step 3: `lane_3_competitive_landscape`
- **Agent:** `trend_analysis_agent` (fallback: `research_agent`)
- **Inputs:** `timeframe_hours` (72), `competitor_shortlist[2-4]`, `require_citations` (true), `max_items` (8)
- **Writes:** `lane_3_text`, `lane_3_deltas[{competitor, change, evidence_url}]`, `lane_3_action_suggestions[]`

### Step 4: `lane_4_rotating_focus`
- **Agent:** slot-resolved (one of: `sharp_action_detector` | `prediction_market_analyst` | `market_intelligence_coordinator`/`stock_analyst_agent` | `opportunity_pipeline_agent` | `research_agent`/`trend_analysis_agent`)
- **Inputs:** `rotation_slot`, `override_triggers{incident,revenue,signal,calendar}`, `timeframe_hours` (48), `watchlist[]` (optional), `sport` (optional), `max_items` (7), `require_citations` (true when quoting odds/prices)
- **Writes:** `lane_4_slot_used`, `lane_4_text`, `lane_4_signals[{signal, why_today, evidence_ref}]`, `lane_4_action_suggestions[]`

### Step 5: `decision_card_synthesis`
- **Agent:** `coo_agent` (or dedicated CoS/brief agent)
- **Inputs:** `lane_1_text`, `lane_2_text`, `lane_3_text`, `lane_4_text`, `governance_snapshot` (optional), `initiative_snapshot` (optional), `ops_snapshot` (optional), `max_decisions` (3)
- **Writes:** `decision_card[{decision, recommendation, why_now, next_step_owner, next_step_timebox}]`, `decision_card_text`

### Step 6: `strategic_synthesis` (uses F7 handler from PR #2592)
- **Agent:** `strategic_review` (or `thinking_agent`)
- **Inputs:** `lane_1_text`, `lane_2_text`, `lane_3_text`, `lane_4_text`, `decision_card_text` (or structured `decision_card`), `brief_date` (ISO), `time_zone` (`America/Denver`), `audience` (`chris`)
- **Writes:** `morning_brief_markdown`, `morning_brief_title`, `brief_highlights[]`

### Step 7: `deliverable_create`
- **Agent:** `deliverable_tool` (action=`create`)
- **Inputs:** `workspace_id` (Morning Brief workspace UUID), `title` (`morning_brief_title` or `Morning Brief — YYYY-MM-DD`), `content` (`morning_brief_markdown`), `category` (`Morning Brief`), `tags` (`morning_brief`, `daily_cos`), `data_sensitivity` (`internal`), `agent_name` (`WorkflowAgent`)
- **Writes:** `deliverable_id`, `deliverable_url` (optional), `deliverable_status` (typically `ready`)

---

## Scheduling

- **Beat name:** `generate-morning-brief-daily`
- **Schedule:** **13:00 UTC** during DST (07:00 Denver MDT). Switch to **14:00 UTC** during MST. Use `crontab(hour=<UTC hour>, minute=0)` — explicit UTC. See Session 1228 PRs #2569/#2570 for the TZ trap fix pattern.
- **Workspace:** persistent "Morning Brief" workspace. Deliverables accumulate over time so Chris can scroll back.

---

## Open questions for Chris (ratification decision card)

1. **4-lane structure OK?** (1 Readiness + 2 Build + 3 Competitive + 4 Rotating + Decision Card synthesis)
2. **Rotation schedule:** Mon=AI-infra / Tue=Competitor / Wed=Tickers / Thu=GTM / Fri=Sports/Kalshi alternating. Swap Fri ↔ Mon if Sports should be the start-of-week anchor instead.
3. **Override priority order:** Incident → Revenue → Signal → Calendar. Reorder if revenue should always win.
4. **Competitor shortlist for Lane 3:** Rigby's draft says "predefined list" — Chris needs to name the 2–4 competitors.
5. **Watchlist for Wed ticker slot:** NVDA + AMD baseline. Anything else? Rotation cadence (weekly? monthly?).
6. **Schedule window:** 13:00 UTC (07:00 MDT) — start of day. Adjust if Chris wants the brief landing earlier or later.
7. **Workspace name:** "Morning Brief" — or a different name like "Daily CoS" / "Chris's Morning Read"?

---

## Definition of done

- **Sub-step A (Session 1232):** spec exists + Chris-ratified. ✅
- **Sub-step B.1 (Session 1233):** plumbing-first cut. `_update_context` lane writes + `lane_4_rotating_focus` slot-driven internal handler (default `ai_infra_deep_dive`) + `decision_card_synthesis` real LLM handler + `strategic_synthesis` morning_brief mode + `create_morning_brief_deliverable` handler. Workflow produces a real markdown brief end-to-end on a hardcoded Monday slot. ✅
- **Sub-step B.2 (Session 1233):** `rotation_slot_resolve` pre-step + override-trigger inputs (incident → revenue → signal → calendar) + slot-resolution tests across all 7 weekdays + Friday alternation. ✅
- **Sub-step C (Session 1233, this PR):** persistent "Morning Brief" workspace materialized via `get_or_create` at deliverable-persist time + `generate_morning_brief_daily` Celery beat task at `crontab(hour=7, minute=0)` Denver. First-fire verify is post-merge (next Railway morning). ← *current*
- **Sub-step D (Session 1234+):** polish based on Chris's read of first 1–2 briefs.
- **Sub-step E (Session 1235+):** dogfood Mon–Fri. Decision point: does the format work?

**Whole-arc DoD:** Chris reads the morning brief 4 of 5 weekday mornings of one full week without needing to ask Rigby for any topic-specific dispatches separately. At that point: user 1 + daily active usage + empirically-true product pitch.

## B.1 implementation notes (Session 1233)

The PR scopes per Rigby's Option A+ recommendation: ship plumbing + Lane 4 slot-driven-with-default first; defer rotation pre-step to B.2. Result: a real morning brief can be produced today on the Monday AI-infra slot; rotation lands as an additive PR.

Internal handlers added (all in `core/services/workflow_orchestration_agent.py`):

- `_execute_lane_4_rotating_focus_step` — reads `context['rotation_slot']` (default `ai_infra_deep_dive`), maps to agent via `_MORNING_BRIEF_LANE_4_SLOT_AGENT`, dispatches via AGENT_MAP fallback router. Returns `slot_used` for downstream `_update_context` capture.
- `_execute_decision_card_synthesis_step` — reads `lane_1_text` … `lane_4_text`, calls gpt-5-mini at `max_completion_tokens=4000` (per gpt-5* floor rule), writes `context['decision_card_text']`. Graceful sentinel ("No urgent decisions today — monitor only") when no lane outputs.
- `_execute_create_morning_brief_deliverable_step` — persists `context['morning_brief_markdown']` as a `Deliverable` row with `category='Morning Brief'`. Workspace UUID stays `None` for B.1; Sub-step C wires the actual workspace.

`_execute_strategic_synthesis_step` extended with `_synthesis_mode='morning_brief'` branch that reads lane keys + `decision_card_text` and produces the final brief markdown (TL;DR pointer + 4 lane sections + decision card embed). Default synthesis path unchanged.

`_update_context` extended with branches for `lane_1_platform_readiness` / `lane_2_build_focus` / `lane_3_competitive_landscape` / `lane_4_rotating_focus` / `decision_card_synthesis` step names — captures step outputs into `context['lane_N_text']` etc. so downstream synthesis can read them.

v0 template (`WORKFLOWS['morning_brief']`) updated: Step 4 agent → `lane_4_rotating_focus` (internal); Step 5 agent → `decision_card_synthesis` (internal); Step 7 agent → `create_morning_brief_deliverable` (internal).

Test coverage: `core/tests/test_morning_brief_workflow_template.py` — 25 tests across 5 test classes (template shape contract, synthesis-mode branching, Lane 4 slot dispatch with 5 slots, decision_card sentinel, lane-plumbing capture). 25/25 green + 6/6 adjacent F4 fallback tests pass post-merge.

## B.2 implementation notes (Session 1233 — landed)

`rotation_slot_resolve` ships as a pure-logic workflow-internal handler at **Step 1** of the morning_brief template (the rest shifted from 1–7 to 2–8). It populates `context['rotation_slot']` before Lane 4 reads it, replacing B.1's static default.

Resolution priority chain (first match wins):

1. **Caller-forced** — `context['rotation_slot']` already set. Bypass override + weekday logic; respect the caller's choice. Reason tag: `caller_forced`.
2. **Override flags** in `context['rotation_override']` dict:
   - `incident: True` → `ai_infra_deep_dive` (deepens Lane 1 coverage; a dedicated `incident_focus` slot can land in a future Sub-step). Reason: `override_incident`.
   - `revenue: True` → `gtm_pipeline_health`. Reason: `override_revenue`.
   - `signal_slot: <shorthand>` → mapped slot. Reason: `override_signal:<shorthand>`.
   - `calendar_slot: <shorthand>` → mapped slot. Reason: `override_calendar:<shorthand>`.
3. **Weekday default** from `_WEEKDAY_DEFAULT_SLOT`. Friday alternates via ISO week parity (`iso_week % 2 == 0` → `sports_edge_scan`, odd → `prediction_markets`). Reason: `weekday_default:<n>` or `fri_alt_iso_week_parity:4`.

Override shorthand → full slot map (`_ROTATION_OVERRIDE_SHORTHAND_TO_SLOT`):

| Shorthand | Full slot |
|---|---|
| `sports` | `sports_edge_scan` |
| `markets` | `prediction_markets` |
| `tickers` | `ticker_catalyst_watch` |
| `gtm` | `gtm_pipeline_health` |
| `ai_infra` | `ai_infra_deep_dive` |

Test seam: `_get_now_utc()` is a static method that tests can `patch.object` to inject a fixed weekday + ISO week without monkey-patching `datetime` at the module level.

**Deferred to a future Sub-step:**

- **Tuesday's `competitor_wedge` slot.** Spec § Lane 4 rotation table calls for `competitor_wedge` on Tue, but that's a Lane-3-deepen concept rather than a Lane 4 slot. B.2 falls back to `ai_infra_deep_dive` for Tue; a future PR can add the dedicated slot mapped to `TrendAnalysisAgent`/`CompetitorAnalysisAgent` with a deeper task.
- **Incident-specific slot.** Currently incident override falls back to `ai_infra_deep_dive`. A future PR could introduce `incident_focus` mapped to `SystemIntelligenceAgent` for a Lane 1 deepen.
- **Auto-populated override flags.** Override flags are caller-provided in B.2. A future PR could auto-populate them: incident from Lane 1's CRITICAL findings (needs Lane 1 → re-resolve loop), revenue from `governance_tool.inbox`, signal from signal aggregation thresholds, calendar from a known-events table.

Test coverage: 21 rotation-specific tests in `MorningBriefRotationSlotResolveTests` covering Mon-Sun defaults, Fri alternation (both parities), caller-forced bypass, full override chain priority (incident > revenue > signal > calendar), shorthand mapping for all 5 slots, unknown-shorthand fallback, handler context write + reason tag capture, and dispatcher registration. 59/59 tests green across the morning_brief + F4 fallback suites.

## C implementation notes (Session 1233 — landed)

Sub-step C closes the daily-CoS arc scheduling. Two surfaces shipped:

**1. Workspace materialization.** `_execute_create_morning_brief_deliverable_step` calls a new `_get_or_create_morning_brief_workspace(user)` helper that does `ProjectWorkspace.objects.get_or_create(user=user, name='Morning Brief', defaults={...})`. First fire bootstraps the workspace per-user with `workspace_type='local'`, `root_path='/morning-brief'` (symbolic — no filesystem access), idempotent on subsequent fires. The Deliverable row is created with `workspace=workspace` so all briefs accumulate in the same workspace and Chris can scroll back through past days.

**2. Daily beat task.** `core.tasks.generate_morning_brief_daily(user_id=None, dry_run=False)` dispatches the `morning_brief` workflow. Defaults to looking up `username='chris'` when `user_id` is omitted (matches CLAUDE.md § Session 1098 fix). Returns structured telemetry (`success`, `workflow`, `deliverable_id`, `rotation_slot`, `lane_4_slot_used`, `date`, `user_id`, `dry_run`) so `CeleryTaskEvent` rows can surface per-fire diagnostics. Beat schedule entry in `core/celery.py`:

```python
'generate-morning-brief-daily': {
    'task': 'core.tasks.generate_morning_brief_daily',
    'schedule': crontab(hour=7, minute=0),  # 7:00 AM Denver
    'options': {'queue': 'default', 'expires': 3600},
},
```

Time drifts seasonally per Celery's `CELERY_TIMEZONE=America/Denver` convention: 13:00 UTC during MDT, 14:00 UTC during MST. Matches the Session 1228 PRs #2569/#2570 TZ trap fix pattern.

**Local guard.** `generate-morning-brief-daily` is in `LOCAL_DENY_TASKS` in `add_critical_celery_tasks.py` so the beat row only materializes on Railway. Local dispatches stay manual via `manage.py` invocation or the PA tool surface. Reason: 5+ LLM calls per fire (3 lane synthesis + decision card + strategic synthesis) is expensive locally + Chris reads it on Railway anyway.

**First-fire verify (carryover).** The next Railway 7:00 AM Denver fire (≈13:00 UTC) produces the first scheduled morning brief. Verify via:

```python
CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
).order_by('-started_at').first()
# Expected: SUCCESS, result['success']=True, result['deliverable_id'] non-null

Deliverable.objects.filter(
    user__username='chris',
    category='Morning Brief',
).order_by('-created_at').first()
# Expected: today's brief, workspace.name='Morning Brief', status='ready'
```

Test coverage (12 new tests in `MorningBriefWorkspaceMaterializationTests` + `MorningBriefDeliverableWorkspaceLinkTests` + `GenerateMorningBriefDailyTaskTests` + `MorningBriefBeatScheduleRegistrationTests`):

- Workspace materialization: first call creates, second call reuses (idempotent), scoped per-user, None user returns None
- Deliverable workspace link: workspace_id populated, multiple briefs accumulate in same workspace, no-markdown smoke no-op preserved
- Daily task: default lookup falls back to 'chris', missing user returns error (no exception), workflow exception returns failure telemetry (no exception propagation)
- Beat schedule registration: entry present in `app.conf.beat_schedule`, crontab is `hour=7, minute=0`, task is `generate-morning-brief-daily` in `LOCAL_DENY_TASKS`

71/71 tests green across all morning_brief suites + F4 fallback.
