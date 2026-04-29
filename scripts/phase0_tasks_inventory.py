"""Phase 0 — Tasks migration inventory (read-only static analysis).

Parses ``core/tasks.py`` with the stdlib ``ast`` module, enumerates
every Celery task registered in the file, classifies each into a
proposed sibling destination (per the Wave B refactor plan), and
emits ``docs/refactors/TASKS_MIGRATION_PLAN.md``.

Read-only by contract:
  * No imports of project code (Django apps stay un-bootstrapped).
  * No Celery interactions (worker isn't pinged).
  * No DB queries (PeriodicTask rows aren't enumerated; this is a
    static analysis only).

Run from anywhere:
    python3 scripts/phase0_tasks_inventory.py

Exit codes:
    0  Plan generated successfully.
    1  Source file missing or unreadable.
"""

from __future__ import annotations

import ast
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
TASKS_FILE = PROJECT / "core" / "tasks.py"
CELERY_FILE = PROJECT / "core" / "celery.py"
OUTPUT = PROJECT / "docs" / "refactors" / "TASKS_MIGRATION_PLAN.md"


# ---------------------------------------------------------------------------
# Domain rules — first match wins, evaluated in this order.
# Each rule is (regex_against_function_name, destination_filename).
# Tweak with care; this is the load-bearing classification surface.
# ---------------------------------------------------------------------------
NEEDS_REVIEW = "NEEDS_REVIEW"

DOMAIN_RULES: list[tuple[str, str]] = [
    # ---- Most specific first (hard-coded names that span multiple buckets) ----

    # Diagnostics — daily CTO/COO/Trend, plus a few diagnostic-pipeline tasks
    (r"^(run|post)_(cto|coo|trend)_daily_diagnostic$", "tasks_diagnostics.py"),
    (r"^run_diagnostic_pipeline_task$", "tasks_diagnostics.py"),
    (r"^run_metrics_action_check$", "tasks_diagnostics.py"),

    # Backfill — anything starting with backfill_
    (r"^backfill_", "tasks_backfill.py"),

    # ---- Body systems (existing sibling) ----
    (
        r"^(run_heartbeat|check_breathing|check_circulation|check_spine_alignment|"
        r"immune_scan|check_digestion|check_muscular|check_brain|check_skin|"
        r"check_nervous|coordinate_body|daily_cost_forecast|"
        r"reset_daily_respiratory_stats)$",
        "tasks_body_systems.py",
    ),

    # ---- Financial / sports betting / kalshi / market / SEC / earnings ----
    (
        r"_(betting|kalshi|odds|arb|earnings|sec_filing)_|"
        r"^(check_sec_filings_alert|run_sec_filing_analyzer|run_earnings_predictor|"
        r"run_stock_(audit_cycle|market_intelligence|financial_agents)|"
        r"run_market_intelligence_desk|check_market_events_and_rerun|"
        r"run_blockchain_(security_monitor|monitoring_agents)|"
        r"track_prediction_outcomes|evaluate_ml_predictions|"
        r"verify_betting_outcomes|scan_arbs_and_notify|"
        r"snapshot_odds_for_line_movement|market_intelligence_scan|"
        r"market_movement_alerts|generate_daily_betting_brief|"
        r"daily_betting_digest|collect_kalshi_(prediction_markets|market_intelligence)|"
        r"collect_sports_(odds|odds_intelligence)|"
        r"run_(crypto_sentiment_monitor|prediction_market_agents))$",
        "tasks_financial.py",
    ),

    # ---- Spiders (broader: substring _spider_ + named tasks) ----
    (
        r"_spider_|"
        r"^(run_spider_by_category|run_spider_network|execute_single_spider"
        r"(_lightweight)?|collect_spider_data|process_(core_)?spider_data"
        r"(_automatic)?|isolate_documents_batch|monitor_isolation_progress|"
        r"cleanup_isolation_metadata|recalculate_spider_priorities|"
        r"update_project_spider_priorities|score_spider_data_async|"
        r"spider_data_retention|aggregate_spider_signals|process_spider_actions|"
        r"trigger_spider_conversations|score_opportunities_from_spider_data)$",
        "tasks_spiders.py",
    ),

    # ---- Learning loop ----
    (
        r"_learning_|"
        r"^(run_learning_loop_cycle|summarize_learning_readback|"
        r"cleanup_learning_readback_events|decay_learning_patterns|"
        r"update_learning_profiles|run_daily_learning_pipeline|"
        r"run_agent_learning_cycle|broadcast_learning_status|"
        r"run_project_learning_cycle|mine_learning_patterns|"
        r"check_learning_loop_slo|run_single_project_learning|"
        r"update_agent_effectiveness_from_learning|embed_daily_agent_learning)$",
        "tasks_learning.py",
    ),

    # ---- Boardroom / governance / pilots / gates ----
    (
        r"_boardroom|"
        r"^(cleanup_boardroom_junk|auto_approve_boardroom_items|"
        r"cleanup_expired_boardroom_items|enrich_boardroom_ml_predictions|"
        r"auto_promote_decisions|ai_promote_decisions|"
        r"auto_approve_low_risk_gates|auto_promote_low_risk_decisions|"
        r"auto_complete_pilots|evaluate_pilots_with_thinking_agent|"
        r"evaluate_and_complete_pilots|execute_pilot_implementations|"
        r"process_gates_and_deploy_pilots|process_gate_progression|"
        r"report_pending_review_metrics)$",
        "tasks_boardroom.py",
    ),

    # ---- Experiments / KPI ----
    (
        r"_experiment(s)?$|"
        r"^(cleanup_halted_experiments|cleanup_stale_running_experiments|"
        r"reconcile_experiment_status_outcome|monitor_running_experiments|"
        r"update_experiment_kpis|check_kpi_alerts|send_weekly_kpi_summary)$",
        "tasks_experiments.py",
    ),

    # ---- Conversations ----
    (
        r"_conversation|"
        r"^(broadcast_conversation_status|run_project_conversation|"
        r"summarize_conversation_task|run_multi_agent_conversation|"
        r"run_triggered_conversation|cleanup_automated_conversation_artifacts)$",
        "tasks_conversations.py",
    ),

    # ---- Initiatives ----
    (
        r"^(cleanup_junk_initiatives|advance_initiative_pipeline|"
        r"auto_kickstart_stuck_initiatives|retry_blocked_research|"
        r"check_blocked_research_for_unblock|process_initiative_auto_progression|"
        r"detect_duplicate_initiatives|generate_initiative_stage_document|"
        r"dispatch_pending_action_items|extract_action_items_from_session)$",
        "tasks_initiatives.py",
    ),

    # ---- Media (video, resolve, youtube) ----
    (
        r"_video_task$|"
        r"^(create_talking_video_task|transcribe_video_task|youtube_whisper_task|"
        r"generate_video_content_pack_task|start_resolve_render|"
        r"poll_resolve_job_status|record_resolve_outcome|poll_processing_videos|"
        r"poll_pending_3d_models|generate_thumbnail_optimizer|run_thumbnail_optimizer)$",
        "tasks_media.py",
    ),

    # ---- Content / blog / podcast (must come before agent runners that mention content) ----
    (
        r"_blog|"
        r"^(generate_podcast_episode|auto_generate_podcast_episode|"
        r"generate_ai_series|generate_self_blog_task|generate_blog_with_topic_task|"
        r"generate_self_blog_deliberation_task|generate_operator_edge_newsletter|"
        r"generate_competitor_comparison_task|run_autonomous_content_studio|"
        r"run_content_creation_agents|run_content_studio_agents|"
        r"run_narrative_drift_cycle|run_narrative_culture_agents|"
        r"track_content_performance|generate_content_for_channel|"
        r"process_content_ideas|trigger_content_from_narrative_shift|"
        r"cleanup_stale_content|execute_workspace_pipeline|"
        r"execute_demo_pipeline_task|produce_content_package|"
        r"generate_content_package|content_autonomy_loop|"
        r"check_content_diversity|score_episode_voice|"
        r"score_unscored_deliverables|enhance_blog_task|"
        r"evaluate_unscored_blogs|reevaluate_enhanced_blogs|"
        r"auto_publish_approved_blogs|auto_enhance_blogs|"
        r"draft_legal_document_task|update_narrative_statuses|"
        r"generate_step_content|generate_checklist_content_async|"
        r"generate_pending_reviews|generate_weekly_synthesis|"
        r"trigger_project_research|run_project_conversation)$",
        "tasks_content.py",
    ),

    # ---- Agents — multi-runner pattern + agent activity tasks ----
    (r"^run_.*_agents$", "tasks_agents.py"),
    (
        r"_agent_|"
        r"^(run_autonomy_cycle|execute_agent_task|execute_initiative_stage_task|"
        r"cleanup_stale_agent_executions|full_agent_rotation|"
        r"exercise_all_dormant_agents|run_agent_health_rotation|"
        r"run_agent_remediation_batch|claude_code_agent_respond|"
        r"agent_think_and_synthesize|embed_agent_activity|"
        r"run_agent_conversation|generate_agent_dreams|"
        r"update_agent_mood|evolve_agent_relationships|"
        r"process_agent_activity_xp|calculate_agent_accuracy|"
        r"universal_agent_workspace_output|"
        r"agent_workspace_status_report|agent_research_to_workspace|"
        r"agent_content_to_workspace|agent_daily_summary|"
        r"agent_category_rotation|claude_code_engineer_task|"
        r"check_mood_expirations|apply_mood_trigger_rules|"
        r"update_alliance_strengths|broadcast_relationship_status|"
        r"check_level_milestones|broadcast_evolution_status|"
        r"aggregate_tool_call_stats|analyze_pa_tool_patterns|"
        r"process_pa_chat_task|rebuild_pa_context_task|process_pa_tts_task)$",
        "tasks_agents.py",
    ),

    # ---- Phase 0 follow-up: resolved NEEDS_REVIEW assignments (2026-04-29) ----
    # Approved by team after the initial automated classification surfaced
    # five ambiguous tasks. Captured here so the plan is self-contained and
    # any future re-run produces zero NEEDS_REVIEW entries.
    (r"^check_all_alerts$", "tasks_ops.py"),
    (r"^send_pending_notifications$", "tasks_push_notifications.py"),
    (r"^process_event_bus_(scoring|validation|analytics)_queue$", "tasks_ops.py"),

    # ---- Generic ops bucket — final catch-all for routine housekeeping ----
    (
        r"^(cleanup_|reap_|monitor_|expire_|claim_|enforce_|"
        r"auto_(approve|process|extract|triage|complete|resolve|archive)_)|"
        r"^(process_event_bus_|get_event_bus_stats|"
        r"run_proactive_system_check|run_ops_autopilot|post_ops_digest|"
        r"ops_control_loop|check_llm_cost_spike|monitor_celery_health|"
        r"check_celery_health|aggregate_roi_metrics_daily|"
        r"refresh_system_state_cache|unified_pipeline_health_check|"
        r"run_autonomous_remediation_cycle|assign_open_findings_to_agents|"
        r"execute_remediation_tasks|verify_completed_fixes|"
        r"assign_and_execute_remediation|run_system_self_audit|"
        r"discover_and_import_audits|process_human_attention_lifecycle|"
        r"generate_human_attention_items|process_hitl_escalations|"
        r"process_high_scoring_opportunities|process_pending_auto_topics|"
        r"run_daily_priority_scan|check_operating_rhythm_status|"
        r"enforce_data_retention|enforce_db_retention|"
        r"check_orphan_deliverables|run_all_desks_intelligence|"
        r"generate_smart_suggestions|expire_old_suggestions|"
        r"generate_user_insights|discover_success_patterns|"
        r"propagate_new_policies|run_autonomous_thinking_cycle|"
        r"scan_concerns_for_human_action|process_distribution|"
        r"update_distribution_analytics|process_realtime_scoring_queue|"
        r"process_batch_scoring_queue|train_ml_scoring_model|"
        r"evaluate_ml_model_performance|update_mythology_pattern_statistics|"
        r"sync_workflow_schedules|check_workflow_schedules|"
        r"execute_scheduled_workflow|execute_scheduled_automations|"
        r"execute_orchestration_async|check_orchestration_timeouts|"
        r"check_orchestration_auto_approvals|execute_pending_opportunity_tasks|"
        r"expire_old_opportunities|generate_opportunity_report|"
        r"send_proactive_opportunity_alerts|send_personalized_opportunity_alerts|"
        r"generate_weekly_opportunity_digest|record_opportunity_view|"
        r"record_opportunity_click|record_opportunity_application|"
        r"record_revenue_event|sync_congress_data|"
        r"run_design_trends_monitor|run_viral_content_predictor|"
        r"run_job_match_intelligence|run_side_hustle_detector|"
        r"run_tech_stack_tracker|run_ai_model_monitor|"
        r"run_case_law_monitor|run_regulatory_change_detector|"
        r"run_freelance_opportunity_scout|run_skill_gap_analyzer|"
        r"run_market_monitoring_agents|run_business_strategy_agents|"
        r"run_strategy_marketing_agents|run_research_analysis_agents|"
        r"run_executive_leadership_agents|run_podcast_debate_agents|"
        r"run_campaign_series_agents|run_system_orchestration_agents|"
        r"run_quality_audit_agents|run_specialty_agents|"
        r"run_development_tech_agents|"
        r"run_autonomous_intelligence_loop|run_daily_intelligence_digest|"
        r"generate_weekly_intelligence_brief|"
        r"surface_top_dreams|maintain_dream_backlog|"
        r"score_and_promote_dreams|process_approved_dreams|"
        r"execute_dream_implementations|explore_dream_topic|"
        r"execute_approved_dreams_via_orchestration|execute_single_dream|"
        r"broadcast_dream_journal|process_hivemind_sessions|"
        r"run_hive_mind_session|sync_project_knowledge|"
        r"auto_resolve_knowledge_gaps|validate_knowledge_sources|"
        r"maintain_knowledge_freshness|promote_to_shared_knowledge|"
        r"generate_document_embeddings|process_document_async|"
        r"process_url_async|generate_memory_embedding|"
        r"process_research_feedback|workspace_autopilot_tick|"
        r"verify_autopilot_action|rescan_active_workspaces|"
        r"batch_extract_artifacts|execute_approved_artifacts|"
        r"execute_single_artifact|process_trigger_events|"
        r"create_default_triggers|trigger_signal_driven_conversation|"
        r"run_source_pack_workflow|execute_code_job|rag_retrieval_canary|"
        r"run_conceptforge_pipeline|detect_failure_task|"
        r"record_all_user_style_evolution|collect_training_data|"
        r"collect_training_data_full|assemble_chunked_upload|"
        r"sync_pipeline_insights_to_collective)$",
        "tasks_ops.py",
    ),
]


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _is_celery_decorator(deco: ast.expr) -> bool:
    """True if ``deco`` is one of Celery's task-registration decorators.

    Matches:
      * ``@shared_task``
      * ``@shared_task(...)``
      * ``@app.task`` / ``@celery.task`` / ``@celery_app.task``
      * ``@app.task(...)`` etc.
    """
    if isinstance(deco, ast.Name):
        return deco.id == "shared_task"
    if isinstance(deco, ast.Attribute):
        return deco.attr == "task"
    if isinstance(deco, ast.Call):
        return _is_celery_decorator(deco.func)
    return False


def _decorator_kwargs(deco: ast.expr) -> dict[str, ast.expr]:
    """Return kwargs of a called decorator; empty dict for bare or unparseable."""
    if not isinstance(deco, ast.Call):
        return {}
    out: dict[str, ast.expr] = {}
    for kw in deco.keywords:
        if kw.arg is not None:
            out[kw.arg] = kw.value
    return out


def _string_constant(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _is_truthy_constant(node: ast.expr) -> bool:
    if isinstance(node, ast.Constant):
        return bool(node.value)
    return False


def _has_kwarg(deco_kwargs: dict[str, ast.expr], name: str) -> bool:
    return name in deco_kwargs


def _function_name(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    return node.name


def _is_helper_name(name: str) -> bool:
    """Helpers are: underscore-prefixed names + ``validate_agent_output``."""
    return name.startswith("_") or name == "validate_agent_output"


def _called_helpers_in(funcdef: ast.AST, helper_names: set[str]) -> list[str]:
    """Walk the body of ``funcdef`` looking for references to helper functions
    by name. Returns sorted unique names."""
    used: set[str] = set()
    for sub in ast.walk(funcdef):
        if isinstance(sub, ast.Name) and sub.id in helper_names:
            used.add(sub.id)
        elif isinstance(sub, ast.Attribute):
            # core.tasks._helper / self._helper etc — only direct name lookups count
            continue
    return sorted(used)


# ---------------------------------------------------------------------------
# Beat schedule extraction (static, regex-based)
# ---------------------------------------------------------------------------


_BEAT_TASK_RE = re.compile(r"['\"]task['\"]\s*:\s*['\"]([^'\"]+)['\"]")


def _extract_beat_task_names(celery_src: str) -> set[str]:
    """Pull out every ``'task': 'core.tasks.X'``-style reference from the
    beat schedule region of celery.py. Conservative: matches anywhere in
    the file, not just inside ``app.conf.beat_schedule``."""
    return set(_BEAT_TASK_RE.findall(celery_src))


# ---------------------------------------------------------------------------
# Domain proposal
# ---------------------------------------------------------------------------


def _propose_destination(func_name: str) -> str:
    for pattern, dest in DOMAIN_RULES:
        if re.search(pattern, func_name):
            return dest
    return NEEDS_REVIEW


# ---------------------------------------------------------------------------
# Risk notes
# ---------------------------------------------------------------------------


def _risk_notes(*, name_explicit: str | None, deco_kwargs: dict[str, ast.expr],
                helpers_used: list[str], destination: str,
                beat_referenced: bool) -> list[str]:
    notes: list[str] = []

    if name_explicit is not None:
        if not name_explicit.startswith("core.tasks."):
            notes.append(
                f"non-standard registered name `{name_explicit}` — preserve verbatim during move"
            )
        else:
            notes.append("name= already pinned (no Phase 1 edit needed for this task)")

    if _has_kwarg(deco_kwargs, "bind"):
        notes.append("bind=True — uses self; tests must mock-bind, helpers must be method-safe")

    if any(k in deco_kwargs for k in ("soft_time_limit", "time_limit")):
        notes.append("custom time limits — production timing-critical; do not alter on move")

    if _has_kwarg(deco_kwargs, "max_retries"):
        notes.append("custom retry policy — preserve verbatim")

    if _has_kwarg(deco_kwargs, "ignore_result"):
        notes.append("ignore_result=True — result-backend interaction differs")

    if helpers_used:
        notes.append(f"depends on {len(helpers_used)} helper(s): {', '.join(helpers_used)}")

    if beat_referenced:
        notes.append("referenced by beat schedule — name pin is non-optional")

    if destination == NEEDS_REVIEW:
        notes.append("no domain rule matched — needs human classification")

    return notes


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _md_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"


def _render_plan(*, tasks: list[dict], helpers: dict[str, ast.FunctionDef],
                 beat_task_names: set[str]) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    total = len(tasks)
    pinned = sum(1 for t in tasks if t["name_explicit"] is not None)
    unpinned = total - pinned
    needs_review = sum(1 for t in tasks if t["destination"] == NEEDS_REVIEW)
    bound_tasks = sum(1 for t in tasks if t["bind"])
    timed_tasks = sum(
        1 for t in tasks
        if any(k in t["deco_kwargs_keys"] for k in ("soft_time_limit", "time_limit"))
    )
    beat_tasks = sum(1 for t in tasks if t["beat_referenced"])

    counts_by_dest = Counter(t["destination"] for t in tasks)

    lines: list[str] = []
    lines.append("# Tasks Migration Plan — Phase 0 inventory")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Source:** `{TASKS_FILE.relative_to(PROJECT)}`")
    lines.append(f"**Generator:** `{Path(__file__).relative_to(PROJECT)}`")
    lines.append("")
    lines.append(
        "> Read-only static analysis. No code was modified. The proposed "
        "destinations are first-match-wins regex rules in the script — "
        "treat them as a starting point, not a final assignment."
    )
    lines.append("")

    # Headline counts
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total tasks:** {total}")
    lines.append(f"- **Already name-pinned (`name=`):** {pinned}")
    lines.append(f"- **Unpinned (need Phase 1 edit):** {unpinned}")
    lines.append(f"- **Tasks with `bind=True`:** {bound_tasks}")
    lines.append(f"- **Tasks with custom time limits:** {timed_tasks}")
    lines.append(f"- **Tasks referenced in beat schedule:** {beat_tasks}")
    lines.append(f"- **Helpers in tasks.py (private + `validate_agent_output`):** {len(helpers)}")
    lines.append(f"- **Tasks needing review (no rule matched):** {needs_review}")
    lines.append("")

    # Counts by destination
    lines.append("## Counts by proposed destination")
    lines.append("")
    lines.append(_md_table_row(["Destination", "Tasks"]))
    lines.append(_md_table_row(["---", "---:"]))
    for dest in sorted(counts_by_dest, key=lambda d: (-counts_by_dest[d], d)):
        lines.append(_md_table_row([f"`{dest}`", str(counts_by_dest[dest])]))
    lines.append("")

    # Per-destination listings
    lines.append("## Per-destination task lists")
    lines.append("")
    by_dest: dict[str, list[dict]] = defaultdict(list)
    for t in tasks:
        by_dest[t["destination"]].append(t)
    for dest in sorted(by_dest, key=lambda d: (d == NEEDS_REVIEW, d)):
        ts = by_dest[dest]
        lines.append(f"### `{dest}` — {len(ts)} task(s)")
        lines.append("")
        lines.append(_md_table_row([
            "Line",
            "Function",
            "Registered name",
            "Already pinned?",
            "Beat?",
            "Helpers",
            "Risk notes",
        ]))
        lines.append(_md_table_row(["---:", "---", "---", ":---:", ":---:", "---", "---"]))
        for t in sorted(ts, key=lambda x: x["lineno"]):
            risk = "<br>".join(t["risk_notes"]) if t["risk_notes"] else "—"
            helpers_cell = ", ".join(f"`{h}`" for h in t["helpers_used"]) or "—"
            pinned_mark = "yes" if t["name_explicit"] is not None else "no"
            beat_mark = "yes" if t["beat_referenced"] else "—"
            lines.append(_md_table_row([
                str(t["lineno"]),
                f"`{t['name']}`",
                f"`{t['registered_name']}`",
                pinned_mark,
                beat_mark,
                helpers_cell,
                risk,
            ]))
        lines.append("")

    # Helpers list
    lines.append("## Helpers (candidates for `tasks_helpers.py`)")
    lines.append("")
    lines.append(_md_table_row(["Line", "Name", "Used by N task(s)"]))
    lines.append(_md_table_row(["---:", "---", "---:"]))
    helper_usage: Counter[str] = Counter()
    for t in tasks:
        for h in t["helpers_used"]:
            helper_usage[h] += 1
    for name, node in sorted(helpers.items()):
        lines.append(_md_table_row([
            str(node.lineno),
            f"`{name}`",
            str(helper_usage.get(name, 0)),
        ]))
    lines.append("")

    # Beat schedule references
    if beat_task_names:
        lines.append("## Beat-schedule references found in `core/celery.py`")
        lines.append("")
        lines.append(
            "Static grep over `core/celery.py` for `'task': '<name>'` "
            "literals. PeriodicTask DB rows are not enumerated here "
            "(static analysis only)."
        )
        lines.append("")
        for name in sorted(beat_task_names):
            inferred = any(t["registered_name"] == name for t in tasks)
            mark = "✓ matches a tasks.py task" if inferred else "?  not from tasks.py (sibling file or external)"
            lines.append(f"- `{name}` — {mark}")
        lines.append("")

    # Phase 1 — task name pinning (script + workflow + safety)
    lines.append("## Phase 1 — task name pinning")
    lines.append("")
    lines.append(_phase_1_safety_paragraph(tasks=tasks))
    lines.append("")
    lines.append(_PHASE_1_NARRATIVE)
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "_Regenerate this plan after any change to `core/tasks.py` or the "
        "domain rules in `scripts/phase0_tasks_inventory.py`._"
    )
    return "\n".join(lines) + "\n"


_PHASE_1_NARRATIVE = """\
Generated by `scripts/phase1_pin_task_names.py` from this inventory.
That script is read-only by default; it emits a unified diff to stdout.
Optional `--write` applies the diff in place and refuses to run when
`core/tasks.py` has uncommitted changes.

### Why name pinning is required

Celery's `@shared_task` decorator registers the task under a name
derived from `<module>.<function>`. Moving `cleanup_stale_content`
from `core.tasks` to `core.tasks_ops` therefore changes the registered
name from `core.tasks.cleanup_stale_content` to
`core.tasks_ops.cleanup_stale_content`. Three concrete failure modes
follow:

1. **Beat schedule references break.** The 42 task-name strings found
   in `core/celery.py:beat_schedule` plus the corresponding
   `PeriodicTask` DB rows reference the names verbatim. After a module
   move without a name pin, beat tries to dispatch `core.tasks.X` and
   the worker only knows `core.tasks_<dest>.X` — the task is silently
   dropped.
2. **String-dispatched calls break.** Any
   `current_app.send_task("core.tasks.X")` call elsewhere in the
   codebase fails the same way.
3. **Mid-deploy queue messages break.** A task queued before the
   deploy is dispatched after; if the worker has registered the task
   under a different name, the message is rejected.

The fix is mechanical: adding `name="core.tasks.<func>"` to the
decorator freezes the registered name regardless of where the
function later lives. Phase 1 must complete before any module move.

### How to review the generated diff

Every diff hunk follows one of three patterns.

Bare decorator:

```
- @shared_task
+ @shared_task(name="core.tasks.<func>")
```

Single-line called decorator:

```
- @shared_task(bind=True, soft_time_limit=300)
+ @shared_task(bind=True, soft_time_limit=300, name="core.tasks.<func>")
```

Multi-line called decorator:

```
  @shared_task(
      bind=True,
      max_retries=3,
+     name="core.tasks.<func>",
  )
```

Spot-checks during review:

- The `<func>` in the new `name=` value matches the function name
  immediately below it — exactly, no typos, no rename.
- Existing kwargs are preserved verbatim. The diff adds `name=` and
  nothing else; `bind=`, `time_limit=`, `max_retries=`, etc. are
  untouched.
- Decorators that already had `name=` appear **nowhere** in the diff.
  `backfill_signal_scores` (the one task with a non-`core.tasks.`
  prefix) is in this group — Phase 3 must preserve its existing
  legacy name verbatim during the module move.
- For multi-line decorators that didn't have a trailing comma, the
  diff also adds a comma to the previous arg. That's deliberate —
  Python accepts both styles, but trailing commas keep future diffs
  smaller. Reviewer should confirm the change is comma-only.

If any hunk shows changes outside a `name=` insertion (function-body
edit, arg reorder, comment removal), the rewriter has a bug — stop and
investigate before applying.

### What must be verified before applying

In order:

1. **Diff applies cleanly.** `git apply --check <diff>` exits 0.
2. **Rewritten source parses.**
   `python3 -c "import ast; ast.parse(open('core/tasks.py').read())"`
   exits 0.
3. **Every task now carries `name=`.** Re-run
   `scripts/phase0_tasks_inventory.py` after applying. The
   `unpinned (need Phase 1 edit)` count must drop to zero; the
   `already pinned (skipped)` count must rise to 356.
4. **No registered names changed.** For each task in the file the
   pinned `name=` value must match what Celery would have produced
   automatically (`core.tasks.<func>`) — except for
   `backfill_signal_scores`, which keeps its existing non-prefixed
   name. The full test suite must pass without modification.
5. **Beat schedule still resolves.** After a worker restart, every
   string in `core/celery.py:beat_schedule` (and every
   `PeriodicTask.task` row in the DB) must correspond to a registered
   task name. Mismatches indicate either a typo in the original
   schedule (unrelated to this refactor — flag separately) or a
   rewriter bug.

Phase 1 must land as a single commit / PR. Do not split — the safety
contract is "all 263 unpinned tasks gain `name=` at once," and a
partial merge leaves some tasks exposed to the very name-drift
failure mode this work exists to prevent.
"""


def _phase_1_safety_paragraph(*, tasks: list[dict]) -> str:
    nonstandard = [t for t in tasks if t["name_explicit"] is not None
                   and not t["name_explicit"].startswith("core.tasks.")]
    safe_to_pin = sum(1 for t in tasks if t["name_explicit"] is None)
    parts = [
        f"{safe_to_pin} unpinned task(s) need an explicit "
        f"`name=\"core.tasks.<func>\"` kwarg added to their decorator. "
        f"This edit is mechanical: a script can produce the diff, the "
        f"runtime behaviour is identical (Celery already auto-registers "
        f"under that name), and tests pass without modification.",
    ]
    if nonstandard:
        names = ", ".join(f"`{t['name']}`" for t in nonstandard)
        parts.append(
            f"\n\n**One special case** ({len(nonstandard)} task(s)): "
            f"{names} carry a non-standard registered name (no "
            f"`core.tasks.` prefix). Phase 1 must preserve these "
            f"verbatim — do not 'normalize' them. Migrating these tasks "
            f"to a sibling file requires the same `name=...` they "
            f"currently use."
        )
    return "".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _walk_tasks(tree: ast.Module) -> tuple[list[ast.FunctionDef | ast.AsyncFunctionDef],
                                            dict[str, ast.FunctionDef]]:
    """Return (task_funcs, helpers). Walks only top-level definitions."""
    task_funcs: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    helpers: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(_is_celery_decorator(d) for d in node.decorator_list):
                task_funcs.append(node)
            elif _is_helper_name(node.name) and isinstance(node, ast.FunctionDef):
                helpers[node.name] = node
    return task_funcs, helpers


def _build_task_record(node: ast.FunctionDef | ast.AsyncFunctionDef,
                       helper_names: set[str],
                       beat_task_names: set[str]) -> dict:
    func_name = _function_name(node)

    # Find the celery decorator (there may be other decorators stacked).
    celery_deco: ast.expr | None = None
    for d in node.decorator_list:
        if _is_celery_decorator(d):
            celery_deco = d
            break

    deco_kwargs = _decorator_kwargs(celery_deco) if celery_deco is not None else {}

    name_explicit = (
        _string_constant(deco_kwargs["name"]) if "name" in deco_kwargs else None
    )
    registered_name = name_explicit if name_explicit is not None else f"core.tasks.{func_name}"

    bind = _is_truthy_constant(deco_kwargs["bind"]) if "bind" in deco_kwargs else False
    helpers_used = _called_helpers_in(node, helper_names)

    beat_referenced = registered_name in beat_task_names

    destination = _propose_destination(func_name)

    risk_notes = _risk_notes(
        name_explicit=name_explicit,
        deco_kwargs=deco_kwargs,
        helpers_used=helpers_used,
        destination=destination,
        beat_referenced=beat_referenced,
    )

    return {
        "name": func_name,
        "lineno": node.lineno,
        "registered_name": registered_name,
        "name_explicit": name_explicit,
        "bind": bind,
        "deco_kwargs_keys": set(deco_kwargs.keys()),
        "helpers_used": helpers_used,
        "destination": destination,
        "beat_referenced": beat_referenced,
        "risk_notes": risk_notes,
    }


def main() -> int:
    if not TASKS_FILE.is_file():
        print(f"phase0_tasks_inventory: source file not found: {TASKS_FILE}", file=sys.stderr)
        return 1

    src = TASKS_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)

    celery_src = CELERY_FILE.read_text(encoding="utf-8") if CELERY_FILE.is_file() else ""
    beat_task_names = _extract_beat_task_names(celery_src)

    task_nodes, helpers = _walk_tasks(tree)
    helper_names = set(helpers.keys())

    tasks: list[dict] = [
        _build_task_record(n, helper_names, beat_task_names) for n in task_nodes
    ]
    tasks.sort(key=lambda t: t["lineno"])

    plan = _render_plan(tasks=tasks, helpers=helpers, beat_task_names=beat_task_names)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(plan, encoding="utf-8")

    rel = OUTPUT.relative_to(PROJECT)
    print(f"phase0_tasks_inventory: wrote {rel}")
    print(f"  tasks:          {len(tasks)}")
    print(f"  helpers:        {len(helpers)}")
    print(f"  beat refs:      {len(beat_task_names)}")
    pinned = sum(1 for t in tasks if t["name_explicit"] is not None)
    print(f"  already pinned: {pinned}")
    print(f"  needs Phase 1:  {len(tasks) - pinned}")
    needs_review = sum(1 for t in tasks if t["destination"] == NEEDS_REVIEW)
    print(f"  needs review:   {needs_review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
