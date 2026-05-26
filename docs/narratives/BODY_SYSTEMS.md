---
title: "Body Systems — narrative (batch F)"
status: draft (batch F of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/topics/body-systems.md
  - docs/narratives/WORKERS_AND_INFRASTRUCTURE.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to topic doc + named handoff files for Sessions 701, 702, 976, 986)
provenance_note: The platform monitors its own infrastructure via a human-anatomy metaphor — HEART pulses, LUNGS breathe, etc. This narrative covers what each system actually measures, when it was added, and how the BodyCoordinator turns sensed state into automatic responses. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f). One drift flagged: PLATFORM_INVENTORY counts 9 systems monitored by run_all_systems_scan; topic doc lists 10 — NERVOUS may not be in the scan rotation.
---

# Body Systems

> The platform watches itself with a human-anatomy metaphor.
> HEART pulses every component, LUNGS track budget, MUSCULAR
> watches agent success, IMMUNE scans for threats. Each system
> has a service singleton, a health-check method, a status
> model, and a place in the BodyCoordinator's automatic-reflex
> table. This narrative is shorter than A–E because the
> subsystem is structurally smaller; that's a feature, not a
> gap.

---

## 1. What this is

The Body Systems layer is a self-monitoring sublayer. It does
not produce work; it watches the platform doing work and
classifies the state into anatomic health levels (healthy /
degraded / critical, or per-system equivalents). Other
subsystems either read the state (the Personal Assistant
surfaces it through `status_snapshot_tool` and
`system_health_tool`) or are driven by it (the BodyCoordinator
auto-applies reflexes when a system reports trouble — throttling
LLM calls when LUNGS is exhausted, pausing the spider network
when DIGESTIVE is blocked).

The anatomy metaphor exists because the platform has many
distinct concerns (cost, throughput, throughput, security,
data ingest, agent success rates, file operations, API
routing) and the team needed a vocabulary that wasn't another
acronym soup. "HEART" is easier to remember than
"AggregateComponentHealthService"; "LUNGS exhausted" is more
intuitive than "TokenBudgetUtilizationAboveThreshold". The
metaphor is functional, not decorative — every name maps to a
real model field, a real check method, and a real status
classification.

There are nine systems monitored by `run_all_systems_scan` per
the platform inventory; the topic doc enumerates ten
(including NERVOUS). One of those is drift this narrative
flags as Unknown — see § 6.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **Body system** | A self-monitoring service. Examples: HEART, LUNGS, CIRCULATORY. Each has a service singleton (e.g., `HeartMonitorService`) in `core/services/`, a primary health-check method (`pulse()`, `breathe()`, `circulate()`), and a status model (`ComponentStatus`, `HeartBeat`, system-specific tables). |
| **`run_all_systems_scan`** | The periodic Celery task that exercises every body system in rotation. Runs on the `broadcast` queue per the worker narrative. Output is the data that downstream tools surface. PLATFORM_INVENTORY counts 9 systems in this scan. |
| **`HeartMonitorService.pulse()`** | The aggregator. Walks every component (brain, nervous, organs, sensory, skin, memory, celery) and produces a single overall health verdict: healthy / degraded / critical. The `HEART` system has a 2× weight in the overall-health rollup. |
| **`HeartBeat`** | The model row capturing each pulse. From `core.models_heart`. Fields: `recorded_at` (**not** `created_at`), `overall_status` (**not** `status`). Field names are footgun-friendly — getting them wrong returns silent zero rows. |
| **`ComponentStatus`** | The per-component status row. PK is `component` (**not** `component_name`), timestamp is `last_check` (**not** `last_checked_at`). Same footgun warning. |
| **BodyCoordinator** | The autonomic-nervous-system layer. Listens to 27 event types from individual systems and applies cross-system reflexes automatically. No human in the loop. |
| **27 event types** | The Body Coordinator's reflex table. Examples: `LUNGS_EXHAUSTED → throttle_llm_calls`; `DIGESTIVE_BLOCKED → pause_spider_network`; `MUSCULAR_STRAINED → scale_down_agents`; `IMMUNE_THREAT_HIGH → alert_admins`; `CIRCULATORY_CONGESTED → clear_caches`. Most are documented in the topic doc; the full set lives in `core/services/body_vitals.py` or equivalent. |
| **Overall health rollup** | Weighted average of all systems. HEART = 2× weight (it's the meta-aggregator already). SKIN = 0.5× weight (workspace file operations matter less than throughput or budget). Every other system = 1× weight. |
| **Health levels** | Per-system enumerations. Most use 4–5 tiers. Common patterns: HEART healthy/degraded/critical; LUNGS normal/shallow/labored/gasping/suffocating; CIRCULATORY flowing/slow/congested/blocked; IMMUNE healthy/alert/fighting/overwhelmed/compromised. Each enum is mapped to a numeric score for the rollup. |
| **`can_breathe(provider, agent)`** | LUNGS's budget gate. Called before an LLM call. Returns whether the budget allows the call given current consumption. Thresholds: EXHAUSTED (< 10 % budget), LOW (< 20 %), RECOVERED (> 50 %). |
| **`record_breath(provider, agent, tokens, cost)`** | LUNGS's consumption log. Called after an LLM call to update budget tracking. The pair (`can_breathe` + `record_breath`) is the platform's per-LLM-call cost discipline. |
| **SKIN workspace path** | The "where does generated content go?" question. `_get_workspace_for_skin_layer()` returns the writable target. Auto-generated content routes to `generated_content/` (gitignored). On Railway, writes fail between deploys (ephemeral filesystem) so SKIN's scoring is baselined at 70 points with file-write success excluded. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Session 701 — HEART service** | The first body system. `HeartMonitorService` introduced with `pulse()` aggregator across the existing components (brain, nervous, organs, sensory, skin, memory, celery). `HeartBeat` model added with `recorded_at` + `overall_status`. The anatomy metaphor formally adopted as the platform's self-monitoring vocabulary. | The platform had many monitoring concerns spread across ad-hoc views and logs. "Is the platform healthy?" had no single answer. HEART made it one verb (`pulse()`) returning one verdict. The metaphor was a deliberate choice — names like "HEART" and "pulse" survive code refactors better than utility-class names. | A single rollup health number is now available. The first usable shape of "how is the platform doing right now?" without reading logs. | **Active** — HEART is the meta-aggregator; the 2× weight is still applied in the rollup. | `docs/handoffs/SESSION_701_HEART_SERVICE.md`; `core/services/heart.py`; `core/models_heart.py` |
| **Session 702 — LUNGS service + HEART UI integration** | `LungMonitorService` added with `breathe()` health check and the `can_breathe(provider, agent)` / `record_breath(provider, agent, tokens, cost)` pair for per-LLM-call budget gating. Thresholds: EXHAUSTED < 10 %, LOW < 20 %, RECOVERED > 50 %. Same session integrated HEART's rollup into the frontend so users could see the platform's overall health at a glance. | LLM calls were the platform's biggest variable cost. Without a per-call gate, the budget was a forecast, not an enforcement. LUNGS made the budget a runtime check (`can_breathe` before the call) and a recorded fact (`record_breath` after). | LLM cost is now bounded by per-provider/per-agent thresholds. Hitting EXHAUSTED triggers the BodyCoordinator's `throttle_llm_calls` reflex automatically. | **Active** — `can_breathe` / `record_breath` are the standard call shape for any LLM-using code path. | `docs/handoffs/SESSION_702_LUNGS_SERVICE.md` + `SESSION_702_HEART_UI_INTEGRATION.md`; `core/services/lungs.py` |
| **Foundation expansion — additional 7 systems** *(Inferred, between Session 702 and ~Session 800)* | BRAIN (`think()` — LLM calls, active conversations, RAG queries, token consumption), CIRCULATORY (`circulate()` — Redis/Celery queues, WebSocket channels), DIGESTIVE (`digest()` — spider data ingestion 4-stage), IMMUNE (`scan()` — security threats, quarantine, rate limiting), MUSCULAR (`flex()` — agent execution success by category), SKIN (`feel()` — workspace file ops), SPINE (`align()` — API routing, latency). NERVOUS (`feel()` — WebSocket / Redis channel layer / message throughput) — exists but not in `run_all_systems_scan` per PLATFORM_INVENTORY (drift flagged § 6). | Each system covers a concern that HEART aggregated but didn't deeply measure. Spelling them out as separate systems made each concern's failure modes legible — "DIGESTIVE blocked" is more actionable than "HEART degraded for an unknown reason." | The full anatomy is in place; the BodyCoordinator's reflex table can reference specific systems instead of generic component states. | **Active.** Eight of nine systems are confirmed in `run_all_systems_scan`. NERVOUS's scan rotation is unclear. | `docs/topics/body-systems.md` system table |
| **Session 976 — SKIN layer workspace + Railway adjustment** | Auto-generated content (blogs, summaries, reports) routed to `generated_content/` (gitignored). `.gitignore` patterns added: `/reports/`, `/summaries/`, `/content/blog_*.md`. On Railway, ephemeral filesystem means writes fail between deploys — SKIN's scoring adjusted to a 70-point baseline with file-write success excluded so SKIN doesn't permanently report "damaged" on Railway. | The platform was producing content that landed in the repo as committed files, polluting git history with auto-generated artifacts. Moving them to a gitignored directory closed the leak. Railway's ephemeral filesystem broke SKIN's health score because every deploy reset writes; the baseline adjustment kept the score meaningful in both environments. | Auto-generated content stays out of git; SKIN reports usefully on both local and Railway. The two-environment baseline pattern (baseline value + selectively excluded checks) was set as the precedent for any system that behaves differently across environments. | **Active** — the `generated_content/` convention is the standard; the Railway baseline approach is reused. | `docs/topics/body-systems.md` §"SKIN Layer (Session 976)" |
| **Session 986 — NERVOUS system fix (the channel-layer bug)** | Two bugs found in NERVOUS's `_check_channel_layer()`. **Bug 1:** the method assumed `CHANNEL_LAYERS.CONFIG.hosts` contained `(host, port)` tuples, but Railway provides URL strings. Fixed with type-aware parsing — strings via `redis.from_url()`, tuples via `redis.Redis()`, with `REDIS_URL` env var as a fallback. **Bug 2:** `_get_message_stats()` was hardcoded to zeros. Wired to `CeleryTaskEvent` (introduced in Session 983, covered in narrative E) for real task throughput. Added a mild −10 activity penalty for genuinely zero activity vs no penalty when tracking is unavailable. | NERVOUS was reporting damaged on Railway because the URL parsing assumed a structure that didn't match the actual configuration. Compounding, `_get_message_stats()` was a stub returning zeros — the message-throughput half of the system was vapor. Both bugs made NERVOUS's score meaningless in production. | Railway health rose from 60 % to 90–100 %. Real throughput is now visible in the NERVOUS score. The `CeleryTaskEvent` plumbing introduced by Session 983 has its first concrete consumer here. | **Active.** NERVOUS reports usefully on Railway; the bugfix patterns (type-aware Redis parsing, telemetry-backed throughput) inform similar code elsewhere. | `docs/topics/body-systems.md` §"Nervous System (Session 986 Fix)"; cross-ref `docs/narratives/WORKERS_AND_INFRASTRUCTURE.md` milestone 2 (CeleryTaskEvent) |
| **BodyCoordinator + 27 event types** *(date Unknown; established sometime after the system family was complete)* | An autonomic-nervous-system layer that listens to per-system events and applies cross-system reflexes automatically. 27 event types mapped to reflexes. Examples: `LUNGS_EXHAUSTED → throttle_llm_calls`; `DIGESTIVE_BLOCKED → pause_spider_network`; `MUSCULAR_STRAINED → scale_down_agents`; `IMMUNE_THREAT_HIGH → alert_admins`; `CIRCULATORY_CONGESTED → clear_caches`. Weighted overall-health rollup formalized — HEART 2×, SKIN 0.5×, rest 1×. | The platform had nine sensing systems but no central place where "this happened in system A → do that in system B" was wired up. Without the Coordinator, every reflex would have been ad-hoc — each system would either reach into others (coupling) or push events into a logging layer that nobody read. The Coordinator centralized the cross-system reaction policy. | The platform reacts to its own state without human intervention. LLM-call throttling and spider-network pausing happen as automatic responses, not as 2 AM pages. | **Active** — Body Coordinator is the standard cross-system reflex layer. | `docs/topics/body-systems.md` §"Body Coordinator" |

---

## 4. What came of it

### Wins

- **One number for "how's the platform doing?"** HEART's
  rollup, weighted across nine systems, is the standard
  health verdict. Surfaced through PA's `system_health_tool`
  and `status_snapshot_tool`.
- **Cost is bounded at the call site.** LUNGS'
  `can_breathe` / `record_breath` pair enforces per-LLM
  budget at the call, not after the bill arrives.
- **Reactions are automatic.** BodyCoordinator's 27 event
  types apply cross-system reflexes without paging anyone.
  LUNGS exhausted → LLM throttle happens before the budget
  blows.
- **Environment-aware scoring.** SKIN's Railway baseline
  (Session 976) set the precedent: a system can have
  per-environment baselines and excluded checks without
  becoming useless.
- **The metaphor survives refactors.** Renaming
  `HeartMonitorService` would be a code change. Renaming
  "HEART" would require rewriting every reference in PA
  tools, topic docs, status displays, and developer
  conversations — so the names tend to stay even when
  underlying code moves.

### Tradeoffs

- **Metaphor naming is unforgiving in code.** `ComponentStatus.component`
  vs `component_name`, `HeartBeat.recorded_at` vs
  `created_at`, `HeartBeat.overall_status` vs `status` — all
  silent failures if you guess wrong. The topic doc has a
  "Key Model References" section specifically because the
  pattern keeps biting.
- **NERVOUS may not be in `run_all_systems_scan`.**
  PLATFORM_INVENTORY counts 9 systems in the scan; topic doc
  lists 10. This narrative cannot resolve the drift —
  flagged in § 6.
- **27 event-type table is not source-controlled in a single
  place.** Different events are wired into different
  systems' service code. Reading the full reflex policy
  requires reading multiple files. No single dispatch table.
- **HEART's 2× weight in the rollup is hardcoded.** If
  HEART itself has a bug, the rollup amplifies the error.
  No introspection on whether HEART's read of its sub-checks
  is itself trustworthy.
- **Body system service singletons are global state.** Each
  service is instantiated once and shared. Test isolation
  requires explicit reset; not always done.
- **Cross-environment baselines (Session 976) handle Railway
  ephemerality but introduce a place where scoring rules
  diverge between environments.** A future "why does the
  local score X look different from production?" question
  may take a beat to answer.

### Follow-on systems enabled

- **PA telemetry tools** — `status_snapshot_tool`,
  `system_health_tool` consume HEART's rollup directly.
  Covered in narrative D.
- **BodyCoordinator reflexes** drive cross-system behavior
  (LLM throttling, spider pausing, agent scale-down) that
  the agent narrative (A) and content-pipeline narrative (B)
  rely on. Without the reflex layer, every overload would
  require manual intervention.
- **`CeleryTaskEvent` consumption by NERVOUS** (Session 986)
  is the canonical example for any future "I want real
  throughput numbers" need — covered in narrative E
  milestone 2.

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot 2026-05-25
> (git HEAD `d513cd7f`). 9 body systems monitored by
> `run_all_systems_scan` per the inventory. Topic doc lists 10
> (drift flagged § 6).

**The 9 systems in the scan rotation (per inventory).**
HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE,
MUSCULAR, BRAIN, SKIN. NERVOUS may or may not be in the scan.

**Per-system check method + monitor.**
| System | Method | Monitors | Health levels |
|---|---|---|---|
| HEART | `pulse()` | All components | healthy / degraded / critical |
| LUNGS | `breathe()` | Budget + token consumption | normal / shallow / labored / gasping / suffocating |
| BRAIN | `think()` | LLM calls, conversations, RAG | focused / thinking / overloaded / foggy / confused |
| CIRCULATORY | `circulate()` | Redis + Celery queues, channels | flowing / slow / congested / blocked |
| DIGESTIVE | `digest()` | Spider 4-stage ingestion | healthy / sluggish / bloated / blocked / starving |
| IMMUNE | `scan()` | Threats, quarantine, rate limiting | healthy / alert / fighting / overwhelmed / compromised |
| MUSCULAR | `flex()` | Agent execution success by category | strong / fit / fatigued / strained / paralyzed |
| SKIN | `feel()` | Workspace file ops, rollbacks | healthy / active / irritated / damaged / critical |
| SPINE | `align()` | API routing, latency | aligned / strained / compressed / injured |
| NERVOUS | `feel()` | WebSocket, channel layer, throughput | responsive / active / sluggish / numb / damaged |

**Overall health rollup.** Weighted average. HEART 2×, SKIN
0.5×, rest 1×. Output goes to `HeartBeat.overall_status`.

**BodyCoordinator reflex examples.**
- `LUNGS_EXHAUSTED → throttle_llm_calls`
- `DIGESTIVE_BLOCKED → pause_spider_network`
- `MUSCULAR_STRAINED → scale_down_agents`
- `IMMUNE_THREAT_HIGH → alert_admins`
- `CIRCULATORY_CONGESTED → clear_caches`

**LUNGS budget call shape.**
```python
if lungs.can_breathe(provider, agent):
    result = llm_call(...)
    lungs.record_breath(provider, agent, tokens, cost)
```
Thresholds: EXHAUSTED < 10 %, LOW < 20 %, RECOVERED > 50 %.

**Model field gotchas.**
- `ComponentStatus.component` (PK), `last_check` (timestamp)
- `HeartBeat.recorded_at` (timestamp), `overall_status`
- All from `core.models_heart`. Using `component_name`,
  `last_checked_at`, `created_at`, or `status` returns
  silent zero rows.

**SKIN workspace.** Auto-generated content →
`generated_content/` (gitignored). Railway baseline 70 pts,
file-write checks excluded.

**Where to look when something stops working.**
- Health rollup reading low for unclear reason → query
  individual system status rows; the rollup hides which
  system is dragging the score.
- LUNGS reports EXHAUSTED but bill looks normal → check
  per-provider / per-agent breakdown; the budget is
  per-channel not global.
- NERVOUS reports damaged on Railway → Session 986 pattern;
  check whether `_check_channel_layer()` got the URL parsing
  right; Railway provides string URLs not tuples.
- "I added a system reflex but it doesn't fire" → 27 event
  types are wired across multiple services; check the
  emitting service first, then the BodyCoordinator handler.
- SKIN reports `damaged` permanently → on Railway,
  ephemeral filesystem means writes fail between deploys;
  Session 976's baseline + excluded check should prevent
  this — if not, the SKIN service didn't pick up the
  baseline.
- Status reads return zero rows → almost always wrong field
  name. Use `component` not `component_name`; `last_check`
  not `last_checked_at`; `recorded_at` not `created_at`;
  `overall_status` not `status`.

---

## 6. Open questions / unknown outcomes

- **Is NERVOUS in `run_all_systems_scan`?** *Known:*
  PLATFORM_INVENTORY counts 9 systems in the scan; topic doc
  lists 10 with NERVOUS. *Unknown:* whether NERVOUS is
  scanned but uncounted in the inventory's heuristic, or
  whether NERVOUS exists as a service but isn't in the
  periodic scan rotation. A `grep` for `run_all_systems_scan`
  + the BodyCoordinator's registered systems would resolve.
- **When was the BodyCoordinator introduced?** *Known:* it
  exists with 27 event types and a weighted-rollup formula.
  *Unknown:* the originating session. No specific session
  was found in the topic doc or in the handoff filename
  scan. A `git log -S "BodyCoordinator"` would surface it.
- **When were the 8 non-HEART-non-LUNGS systems added?**
  *Known:* HEART (Session 701), LUNGS (Session 702). The
  other 7–8 are not session-attributed in the corpus
  surveyed. *Unknown:* whether they all landed together in a
  third session or were added incrementally.
- **Full list of 27 event types and their reflexes.**
  *Known:* the topic doc names ~5 examples. *Unknown:* the
  full table. Not consolidated in any single doc — would
  need to read the BodyCoordinator service code to enumerate.
- **How often is the BodyCoordinator overriding decisions
  vs sleeping?** *Known:* the reflex table exists.
  *Unknown:* the actual fire rate per reflex in current
  production. A `CeleryTaskEvent` query for the
  coordinator's task or a per-reflex log would surface this.
- **Are the per-system health levels (4–5 tiers each)
  calibrated against real measurements?** *Known:* the tier
  enums exist. *Unknown:* whether the thresholds were tuned
  empirically or set by intuition. No tuning history is in
  the corpus surveyed.
- **HEART weight (2×) and SKIN weight (0.5×) — calibration
  basis.** *Known:* the weights are hardcoded. *Unknown:*
  whether they were validated against historical data or
  set by judgment.

---

## 7. Source index

### Primary doc sources

- `docs/topics/body-systems.md` — current-state topic doc.
- `docs/PLATFORM_INVENTORY.md` — inventory anchor; "9 body
  systems monitored by `run_all_systems_scan`."
- `docs/narratives/WORKERS_AND_INFRASTRUCTURE.md` — companion
  (E). Cross-references: `CeleryTaskEvent` (Session 983)
  consumed by NERVOUS (Session 986); BodyCoordinator
  reflexes run on the `broadcast` queue.

### Named session handoffs cited above

- `docs/handoffs/SESSION_701_HEART_SERVICE.md` — HEART
  introduction.
- `docs/handoffs/SESSION_702_LUNGS_SERVICE.md` — LUNGS
  introduction.
- `docs/handoffs/SESSION_702_HEART_UI_INTEGRATION.md` —
  frontend rollup integration.
- Session 976 — SKIN layer workspace (referenced in topic
  doc).
- Session 986 — NERVOUS fix (referenced in topic doc).

### Code anchors

- `core/services/heart.py` — `HeartMonitorService`.
- `core/services/lungs.py` — `LungMonitorService`.
- `core/services/body_vitals.py` — likely BodyCoordinator
  home (Inferred from naming pattern).
- `core/services/circulatory.py`, `digestive.py`,
  `immune.py`, `muscular.py`, `body_coordinator.py` — per
  topic doc references.
- `core/models_heart.py` — `HeartBeat` model.
- `core.models` package — `ComponentStatus` model.

### Verification commands

- `python manage.py generate_platform_inventory` —
  regenerate inventory.
- `git log -S "BodyCoordinator"` — surface the session that
  introduced the coordinator (open question § 6).
- `grep -r "run_all_systems_scan" core/services/` — confirm
  which systems are in the scan rotation.
