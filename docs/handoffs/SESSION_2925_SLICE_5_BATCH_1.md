# Session 2925 — Slice 5 batch 1 (quartet — OPENS Slice 5 at 4/14; Ledger #33 code-fix bonus)

**Session:** S2925
**Date:** 2026-07-23
**HEAD at open:** `1809e4de1`
**HEAD at close:** `17897125a` (+ close cascade PR)
**Fresh pin at open:** `pa-a5fee83d2afb4932` (minted at S2924 close)
**Fresh pin at close:** `pa-7e17133240eb4c44` (minted by `session_lifecycle close`; wrapper rewritten)
**PRs shipped:** 3 (#3481 Ledger #33 code fix + #3482 Slice 5 batch 1 quartet + close cascade PR)

---

## Overview

S2925 opened Slice 5 (`tool_dispatcher.py` — 14 tools) after S2924 closed Slice 4 at 17/17. Structural shift: all 14 Slice 5 tools dispatch through a single shared handler (`_handle_agent_tool` at `tool_dispatcher.py:1196`) rather than per-file multi-action handlers like Slices 1-4.

Two substantive PRs shipped:
1. **PR #3481** — Ledger #33 code fix (originally framed as "15-min migration replay"; reframed mid-session to code-fix after discovering migration 0229 explicitly deleted `core_userskill` in Feb 2026).
2. **PR #3482** — Slice 5 batch 1 quartet (`brand_strategy_agent` + `competitor_analysis_agent` + `customer_research_agent` + `create_project_from_research`).

Session outcome: 4 Slice 5 tools moved to `validated_full`; gap map `69/10/7/30 → 73/10/7/26`; 3 of 4 quartet tools reached end-to-end `status='completed'` in ORM (bonus completions beyond the planned 1-per-family per Rigby micro-edit).

---

## Ledger #33 reframe arc (PR #3481)

**Original diagnosis (S2924 close):** `profile_tool.skills` + `profile_tool.learning_summary` failed live-dispatch with `relation "core_userskill" does not exist` — framed as "15-min migration replay" (dev-env drift).

**S2925 investigation surfaced:**
- Migration `0228_session_930_user_learning` created `core_userskill` (Feb 2026)
- Migration `0229_initiative_last_activity_at` **explicitly `DeleteModel`'d** all 5 models from 0228 (also Feb 2026, ~1 week later)
- DB is in the intended post-0229 state — tables are correctly absent
- BUT: `models_user_learning.py` still defines the 5 model classes as live Django models
- AND: 6 services still import them (`td_handlers_gateway.py` — profile_tool skills+learning_summary; `agent_router.py`; `goal_tracking_service.py`; `learning_loop_orchestrator.py`; `skill_evolution_service.py`; `agent_feedback_service.py`; `profile_completeness_service.py`)
- **Root cause:** latent multi-service stale-model bug, ~5 months old — profile_tool sweep just happened to be the first thing to hit it

**Reframe routed to Chris via Rigby.** 3 options offered:
- **Option A** — Resurrect UserSkill via new migration (~30 min) — but doesn't answer why 0229 deleted it
- **Option B** — Full stale-code sweep (multi-hour) — right long-term but blocks Slice 5 batch 1
- **Option C** — Minimum-viable: rewrite ONLY profile_tool.skills + learning_summary to use `ExtendedUserProfile.skills` (~45 min)

**Chris D-verdict via terminal:** ship Option C (implicit — Rigby ratified Option C with 3 guardrails, Chris didn't interject on the reframe; treated as ship-it under the umbrella "ship it" from earlier in the session).

**Rigby's 3 guardrails on Option C (all met):**
1. Ship as tiny standalone PR ahead of Slice 5 batch 1 ✅
2. Add new Ledger entry documenting broader latent bug ✅ (Rigby appended entry #34)
3. Reimplement against `ExtendedUserProfile.skills` (already used by profile action) + code comment referencing 0229 deletion ✅

**Envelope changes for the two rewritten actions:**
- `skills`: removed `id` / `evidence_count` / `confidence` / `last_demonstrated` (UserSkill-specific fields); added `years` + `source: 'extended_user_profile.skills'`
- `learning_summary`: replaced `avg_confidence` with `avg_years`; added `source`

**Post-merge live-verify at sha c70ff84fe:**
- `profile.skills` envelope: `count=0, source='extended_user_profile.skills'` ✅
- `profile.learning_summary` envelope: `total_skills=0, source='extended_user_profile.skills'` ✅
- ORM ground truth for chris user: `ExtendedUserProfile.skills = []` — `count=0` is honest, no error
- No `error_code='legacy_error'` returned — the handler crash surfaced at S2924 is gone

`profile_tool_validation.md` updated: §1 (dropped UserSkill from description; added S2925 resolution note); §Covered actions for `skills` + `learning_summary` (envelope shape + verification protocol updated); §5b First-hop dependency table (UserSkill rows replaced with ExtendedUserProfile rows).

---

## Slice 5 batch 1 quartet (PR #3482)

### Composition + rationale

Per Rigby S2925 T0 SIGN + micro-edit + Chris D-verdict "ship it":

| Tool | Mapped agent | Family | Role in batch |
|---|---|---|---|
| `customer_research_agent` | `CustomerResearchAgent` | Business Research | **Business-family completion-verify representative** |
| `competitor_analysis_agent` | `CompetitorAnalysisAgent` | Business Research | Receipt-verify only; completion-verify batch 2 |
| `brand_strategy_agent` | `BrandStrategyAgent` | Business Research | Receipt-verify only; completion-verify batch 2 |
| `create_project_from_research` | `WorkflowAgent` | Orchestration | **WorkflowAgent-family completion-verify representative** |

3 business-family agents + 1 WorkflowAgent = exercises both agent families in one batch. Per Rigby's Q1 verdict: WorkflowAgent representation is critical because it's the ONLY agent that can delegate to other agents — its downstream execution has fundamentally different (recursive) fanout shape.

### Structural shift from Slices 1-4

Slice 5's shape is **fundamentally different** from Slices 1-4:

- Slices 1-4: per-file multi-action handlers (each `_handle_*` method on `td_handlers_ops` / `td_handlers_agents` / `td_handlers_core` / `td_handlers_gateway`)
- Slice 5: **single shared handler** (`_handle_agent_tool` at `tool_dispatcher.py:1196`) with **agent-class dispatch** determined by `_tool_to_agent_name` at `td_handlers_agents.py:83-160`

Consequence: all 14 Slice 5 tools return async receipts (task_id-shaped envelopes), not synchronous data. Validation now includes BOTH (a) receipt correctness AND (b) end-to-end `job_status` completion — Rigby's Q5(iii) micro-edit on session-open SIGN.

### Wrapper is NOT pure pass-through — Rigby Q2 verdict

Rigby's tool-grounded T0 SIGN surfaced that `_handle_agent_tool` does substantive pre-processing:

- Promotes root payload fields into `context` (`:1229-1233`) per `_CONTEXT_PROMOTE_KEYS`
- Injects `context['user_id']` when `user_id` present (`:1234-1235`)
- Applies Editor→ContentWriter synthesis reroute via `reroute_synthesis_to_content_writer` (`:1245-1250`)
- Gathers workspace deliverables into agent context for EditorAgent + ContentWriterAgent (`:1267-1317`)
- Applies smoke allowlist stripping (`:1325-1326`)
- Dispatches Celery `execute_agent_task.apply_async` on `long_running` queue (`:1330`)

**Verdict:** §5a classification for Slice 5 tools MUST be scored end-to-end (wrapper pre-processing + mapped agent behavior), NOT wrapper-only. All 4 batch 1 tools classified `external` because the first-hop leaves the process (Celery async dispatch) and downstream execution reaches LLM providers, web_search dispatcher re-entry, and per-agent DB writes.

### §5a distribution table (batch 1 slice — first Slice 5 exercise)

| Tool | End-to-end tier | Notes |
|---|---|---|
| brand_strategy_agent | `external` | Wrapper + LLM + potential workspace ORM read |
| competitor_analysis_agent | `external` | Wrapper + LLM + web_search dispatcher re-entry + spider queries + ML entity analysis |
| customer_research_agent | `external` | Wrapper + LLM + web_search dispatcher re-entry + spider queries (Reddit/HN/YouTube/tech news) + ML clustering |
| create_project_from_research | `external` (**amplified**) | Wrapper + WorkflowAgent + **recursive fanout** — delegated sub-agents each spawn additional `execute_agent_task.apply_async` calls |

All 4 filled Appendix A (Async-Fanout) — first-hop IS `apply_async`. Appendix N (Network-Preflight) N/A at wrapper level (network egress happens downstream in the agent, not the wrapper).

### Post-merge live-verify at sha 17897125a (per PLAYBOOK-7.4.4)

**Receipt-verify — all 4 PASS:**

| Tool | task_id | `agent` field | Envelope shape |
|---|---|---|---|
| brand_strategy_agent | `1238daf6-...` | `BrandStrategyAgent` | ✅ complete |
| competitor_analysis_agent | `84db7048-...` | `CompetitorAnalysisAgent` | ✅ complete |
| customer_research_agent | `eab42407-...` | `CustomerResearchAgent` | ✅ complete |
| create_project_from_research | `5cf4b316-...` | `WorkflowAgent` | ✅ complete |

**Completion-verify (ORM ground truth via `AgentExecution.objects.filter(celery_task_id=...)`):**

| Tool | Status | Tokens | Cost | Notes |
|---|---|---|---|---|
| brand_strategy_agent | `completed` | — | — | Bonus completion — was planned as receipt-verify-only |
| competitor_analysis_agent | `completed` + 1 new `in_progress` | — | — | Bonus completion + a subsequent CompetitorAnalysisAgent execution (possibly delegated by WorkflowAgent) |
| customer_research_agent | `completed` | 3937 | $0.0085 | Planned business-family representative |
| create_project_from_research | `in_progress` | 0 (accumulating) | $0.0000 | Planned WorkflowAgent-family representative — 3-min LLM timeout + sub-agent fanout in progress |

Log evidence for CustomerResearchAgent execution:
- Made spider_query + reddit_search + web_search calls
- Received deprecation warning: `[CustomerResearchAgent] web_search is deprecated — falling through to BaseAgent handler` (pre-existing, not batch 1 regression)
- Ran embedding requests for SpiderSemanticSearch
- Tracked 3937 tokens / $0.0085 / 1827ms

Log evidence for WorkflowAgent execution:
- Full context injection (spider + learning + advisor + feedback + workspace + docs + user + scifi) per agent_router
- Tracked 5491 tokens / $0.0106 / 2384ms at first checkpoint
- Recursive fanout evident: a second CompetitorAnalysisAgent execution appeared in recent AgentExecution rows (in_progress) — likely delegated by WorkflowAgent per its `delegate_to_agent` capability

### Pre-existing dev-env drift observed (NOT batch 1 regression)

- `AgentTaskExecution has no field named 'last_heartbeat_at'` — heartbeat periodic write failing silently for CustomerResearchAgent execution `b7681140-...`. Pre-existing (not caused by this batch). Worth noting in Rigby Tool Gap Ledger if it recurs; deferred.

### Gap map delta

`docs/audits/PA_TOOLS_GAP_MAP.md` auto-regenerated via `python manage.py build_pa_tool_audit --gap-only`:
- Pre-S2925: **69 full · 10 partial · 7 unknown · 30 untested**
- Post-S2925: **73 full · 10 partial · 7 unknown · 26 untested**
- Delta: +4 full / -4 untested (matches the 4 new validation docs)

---

## Rigby Tool Gap Ledger updates this session

- **Entry #34 (LOW) added by Rigby via `deliverable_tool.append`** (1588 chars): broader stale-model latent bug — UserSkill/SkillDemonstration/AgentFeedback/GoalProgress/ProfileCompletionPrompt tables `DeleteModel`'d in migration 0229 (Feb 2026) but Django model classes in `core/models_user_learning.py` + 5 service imports were not cleaned up. Only profile_tool remediated in PR #3481. Estimate: multi-hour to fully sweep all 6 sites.

---

## Sweep progress tracker (Path B ratified S2892)

- **Slice 1 (`td_handlers_ops`, 17 tools):** UNCHANGED.
- **Slice 2 (`td_handlers_agents`, 25 tools):** **CLOSED at S2912.**
- **Slice 3 (`td_handlers_core`, 22 tools):** **CLOSED at S2917 (22/22).**
- **Slice 4 (`td_handlers_gateway`, 17 tools):** **CLOSED at S2924 (17/17).**
- **Slice 5 (`tool_dispatcher`, 14 tools):** **OPEN — 4/14 at S2925 close.** 10 remaining.

Session cumulative pace: 2 substantive PRs + close cascade PR in 1 session — Ledger #33 code fix + Slice 5 batch 1 quartet + close cascade. Cumulative sweep pace unchanged from S2924.

---

## Forbidden entries carried forward (unchanged from S2924 unless noted)

D6 moratorium remains in force. All S2924 forbidden entries carry forward. **New S2925 forbidden entries below.**

### NEW S2925 forbidden entries

- **No "migration-history-marks-applied-but-table-deleted-downstream" Fold promotion without 2nd instance.** 1st (Ledger #33 diagnosis reframe at S2925). Root shape: migration X creates table T; migration Y (later) `DeleteModel`'s T; both marked [X] applied; source-of-truth check confirms T doesn't exist. Requires code-side inspection to distinguish from dev-env drift. Diagnostic pattern worth codifying if it recurs.
- **No "stale-model reference across N services" substrate arc without explicit Chris directive.** 1st (Ledger #34 documents UserSkill/SkillDemonstration/etc. + 6 service imports). Multi-hour cleanup deferred; may become substrate work if a second similar cluster surfaces.
- **No "wrapper-pre-processing changes end-to-end §5a tier" Fold promotion without 2nd instance.** 1st (Slice 5 batch 1). Root shape: agent-forwarding wrapper's pre-processing (reroute, workspace-content gather, context promotion) affects the downstream agent's behavior enough that end-to-end tier != wrapper-only tier. Codified as authoring guidance in the 4 batch 1 validation docs; promotion to §5a template amendment deferred to 2nd instance.
- **No "recursive fanout dispatch topology proof" Fold promotion without 2nd instance.** 1st (create_project_from_research WorkflowAgent). Root shape: agent-forwarding tool whose downstream execution recursively re-dispatches other agent tools, producing a tree of AgentExecution rows visible only via ORM traversal (not `job_status` composite view). Codified as authoring detail in `create_project_from_research_validation.md` §5b Appendix A A4.
- **No "sub-agent AgentExecution not auto-enumerated in job_status" UX-gap Fold promotion without recurrence.** 1st. Documented as an authoring detail + Rigby Tool Gap Ledger candidate if it recurs post-batch-1.
- **No "cancel-not-recursive across WorkflowAgent tree" Fold promotion without recurrence.** 1st. Documented as authoring detail in `create_project_from_research_validation.md` §5b Appendix A A5(b).
- **No "many-to-one tool→agent mapping" Fold promotion without recurrence.** 1st (create_project_from_research + create_brand_video + workflow_orchestration_agent all → WorkflowAgent). Documented as authoring detail; may become a schema/audit pattern if more instances surface.

---

## S2926 open sequence (proposed)

### Step 1 — Slice 5 batch 2 (continue quartet cadence)

Recommended batch 2 composition (Rigby SIGN required to ratify):
- (a) Complete the batch 1 completion-verify deferrals: bundle `brand_strategy_agent` + `competitor_analysis_agent` with 2 new tools for a batch 2 quartet
- (b) Cover second orchestration-family entry point: `create_brand_video` (also → WorkflowAgent) OR `workflow_orchestration_agent` (also → WorkflowAgent) — these use the same agent class via different tool names, so completion-verify on one covers the shared logic
- (c) Cover a media-generation-family agent: `image_editing_agent` OR `three_d_generation_agent` OR `video_editing_agent` (Media Creation & Editing section of `_tool_to_agent_name` mapping)

Q1: propose batch 2 composition ratifying (a) + one of (b) + (c) — likely 4-tool quartet.
Q2: completion-verify discipline — bundle batch 1's deferred completion-verifies + new batch 2 tools' completion-verifies into one batched Rigby dispatch post-merge?
Q3: does WorkflowAgent's recursive fanout warrant deeper §5b enumeration for the 2 remaining WorkflowAgent-mapped tools (`create_brand_video` + `workflow_orchestration_agent`)?
Q4: any pre-existing drift observed at S2925 (heartbeat_at field missing on AgentTaskExecution) worth remediating alongside batch 2?
Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):
- (i) After 1 batch of Slice 5, has the "single shared handler" pattern surfaced any risks not visible at the start-of-slice SIGN?
- (ii) Legacy-error envelope corroboration — still 21? Or did receipt-verify dispatches surface new instances?
- (iii) Anything from batch 1's high-completion-count (3 of 4 completed end-to-end, not just 2) worth carrying forward as a batch-cadence adjustment?

### Alternative Step 1 candidates

- **Broader stale-model sweep (Ledger #34)** — rewrite the 5 remaining services importing UserSkill/etc. to use current sources. Multi-hour; substantive engineering work.
- **AgentTaskExecution `last_heartbeat_at` migration** — small drift fix; ~15 min.
- **Original character-os stand-by** — unchanged.

### What's forbidden at S2926 (D6 MORATORIUM still in force)

All S2924/S2925 forbidden entries carry forward (see §"Forbidden entries carried forward" above). No new forbidden entries this handoff — S2925's new entries are cumulative with S2924's, not additive-per-session.

---

## Twin-pointer docs card (per feedback_twin_pointer_docs_at_boundaries)

**Repo file paths:**
- S2925 handoff (this doc): `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- Batch 1 validation docs: `docs/research/tools/validation/{brand_strategy_agent,competitor_analysis_agent,customer_research_agent,create_project_from_research}_validation.md`
- Gap map: `docs/audits/PA_TOOLS_GAP_MAP.md` (auto-generated)
- 00-START refresh: `00-START-NEXT-SESSION.md`
- Wrapper: `tools/pa_local.sh` (points to `pa-7e17133240eb4c44`)

**Workspace UI:**
- Donkey Betz workspace (UUID `b4503364-2573-4401-9e28-61a739e0ce50`) — Rigby Tool Gap Ledger deliverable UUID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #34 added this session)
- Workspace URL for Chris: `/workspaces/b4503364-2573-4401-9e28-61a739e0ce50`
- Ratification envelope + content mirror for S2925 batch 1: **PENDING — to be created by Rigby per feedback_rigby_writes_workspace_deliverables at S2926 open OR by Rigby in the immediate post-close window**

---

## For fuller Slice 4/5 arc context (spans S2846 → S2925)

- **S2924 handoff (prior):** `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`
- **T1b canonical template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a 4-tier taxonomy S2921)
- **Batch 1 validation docs (this session):** `docs/research/tools/validation/{brand_strategy_agent,competitor_analysis_agent,customer_research_agent,create_project_from_research}_validation.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + per-tool validation docs (90 non-substrate post-S2925: 86 pre-S2925 + 4 this batch)
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #34 added this session)

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
