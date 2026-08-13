# Tasks Migration Plan — Phase 0 inventory

**Generated:** 2026-04-29T18:06:03+00:00
**Source:** `core/tasks.py`
**Generator:** `scripts/phase0_tasks_inventory.py`

> Read-only static analysis. No code was modified. The proposed destinations are first-match-wins regex rules in the script — treat them as a starting point, not a final assignment.

## Summary

- **Total tasks:** 319
- **Already name-pinned (`name=`):** 319
- **Unpinned (need Phase 1 edit):** 0
- **Tasks with `bind=True`:** 92
- **Tasks with custom time limits:** 42
- **Tasks referenced in beat schedule:** 30
- **Helpers in tasks.py (private + `validate_agent_output`):** 96
- **Tasks needing review (no rule matched):** 0

## Counts by proposed destination

| Destination | Tasks |
| --- | ---: |
| `tasks_ops.py` | 134 |
| `tasks_agents.py` | 45 |
| `tasks_content.py` | 38 |
| `tasks_financial.py` | 25 |
| `tasks_spiders.py` | 19 |
| `tasks_learning.py` | 14 |
| `tasks_body_systems.py` | 13 |
| `tasks_media.py` | 11 |
| `tasks_initiatives.py` | 10 |
| `tasks_conversations.py` | 9 |
| `tasks_push_notifications.py` | 1 |

## Per-destination task lists

### `tasks_agents.py` — 45 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 489 | `cleanup_stale_agent_executions` | `core.tasks.cleanup_stale_agent_executions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 626 | `run_autonomy_cycle` | `core.tasks.run_autonomy_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 638 | `execute_agent_task` | `core.tasks.execute_agent_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 656 | `execute_initiative_stage_task` | `core.tasks.execute_initiative_stage_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 2165 | `agent_think_and_synthesize` | `core.tasks.agent_think_and_synthesize` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2185 | `embed_agent_activity` | `core.tasks.embed_agent_activity` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2632 | `generate_agent_dreams` | `core.tasks.generate_agent_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3097 | `update_agent_mood` | `core.tasks.update_agent_mood` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3103 | `check_mood_expirations` | `core.tasks.check_mood_expirations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3107 | `apply_mood_trigger_rules` | `core.tasks.apply_mood_trigger_rules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3111 | `evolve_agent_relationships` | `core.tasks.evolve_agent_relationships` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3159 | `update_alliance_strengths` | `core.tasks.update_alliance_strengths` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3173 | `broadcast_relationship_status` | `core.tasks.broadcast_relationship_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3177 | `process_agent_activity_xp` | `core.tasks.process_agent_activity_xp` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3181 | `check_level_milestones` | `core.tasks.check_level_milestones` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3218 | `broadcast_evolution_status` | `core.tasks.broadcast_evolution_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 3977 | `calculate_agent_accuracy` | `learning_loop.calculate_agent_accuracy` | yes | — | — | non-standard registered name `learning_loop.calculate_agent_accuracy` — preserve verbatim during move |
| 6433 | `run_market_monitoring_agents` | `core.tasks.run_market_monitoring_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6529 | `run_business_strategy_agents` | `core.tasks.run_business_strategy_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6533 | `exercise_all_dormant_agents` | `core.tasks.exercise_all_dormant_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6927 | `agent_workspace_status_report` | `core.tasks.agent_workspace_status_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6931 | `agent_research_to_workspace` | `core.tasks.agent_research_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6935 | `agent_content_to_workspace` | `core.tasks.agent_content_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7221 | `aggregate_tool_call_stats` | `core.tasks.aggregate_tool_call_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7225 | `agent_daily_summary` | `core.tasks.agent_daily_summary` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8463 | `universal_agent_workspace_output` | `core.tasks.universal_agent_workspace_output` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 8639 | `agent_category_rotation` | `core.tasks.agent_category_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8647 | `full_agent_rotation` | `core.tasks.full_agent_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8848 | `run_strategy_marketing_agents` | `core.tasks.run_strategy_marketing_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 8874 | `run_research_analysis_agents` | `core.tasks.run_research_analysis_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 8966 | `run_development_tech_agents` | `core.tasks.run_development_tech_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 8995 | `run_executive_leadership_agents` | `core.tasks.run_executive_leadership_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9026 | `run_podcast_debate_agents` | `core.tasks.run_podcast_debate_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9072 | `run_campaign_series_agents` | `core.tasks.run_campaign_series_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9091 | `run_system_orchestration_agents` | `core.tasks.run_system_orchestration_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9126 | `run_quality_audit_agents` | `core.tasks.run_quality_audit_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9145 | `run_specialty_agents` | `core.tasks.run_specialty_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9493 | `run_agent_health_rotation` | `core.tasks.run_agent_health_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9781 | `run_agent_remediation_batch` | `core.tasks.run_agent_remediation_batch` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10577 | `claude_code_engineer_task` | `core.tasks.claude_code_engineer_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 10584 | `claude_code_agent_respond` | `core.tasks.claude_code_agent_respond` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 10591 | `process_pa_chat_task` | `core.tasks.process_pa_chat_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 10599 | `rebuild_pa_context_task` | `core.tasks.rebuild_pa_context_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 10713 | `process_pa_tts_task` | `core.tasks.process_pa_tts_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11041 | `analyze_pa_tool_patterns` | `core.tasks.analyze_pa_tool_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |

### `tasks_body_systems.py` — 13 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 6353 | `run_heartbeat` | `core.tasks.run_heartbeat` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6357 | `check_breathing` | `core.tasks.check_breathing` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6361 | `daily_cost_forecast` | `core.tasks.daily_cost_forecast` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6365 | `reset_daily_respiratory_stats` | `core.tasks.reset_daily_respiratory_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6397 | `check_circulation` | `core.tasks.check_circulation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 6401 | `check_spine_alignment` | `core.tasks.check_spine_alignment` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6405 | `immune_scan` | `core.tasks.immune_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6409 | `check_digestion` | `core.tasks.check_digestion` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6413 | `check_muscular` | `core.tasks.check_muscular` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6417 | `check_brain` | `core.tasks.check_brain` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6421 | `check_skin` | `core.tasks.check_skin` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6425 | `check_nervous` | `core.tasks.check_nervous` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6429 | `coordinate_body` | `core.tasks.coordinate_body` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_content.py` — 38 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 493 | `cleanup_stale_content` | `core.tasks.cleanup_stale_content` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 594 | `execute_workspace_pipeline` | `core.tasks.execute_workspace_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 599 | `execute_demo_pipeline_task` | `core.tasks.execute_demo_pipeline_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 667 | `produce_content_package` | `core.tasks.produce_content_package` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 2591 | `trigger_project_research` | `core.tasks.trigger_project_research` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3774 | `generate_content_package` | `core.tasks.generate_content_package` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3778 | `generate_ai_series` | `core.tasks.generate_ai_series` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3981 | `run_autonomous_content_studio` | `core.tasks.run_autonomous_content_studio` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3985 | `generate_content_for_channel` | `autonomous_studio.generate_content` | yes | — | — | non-standard registered name `autonomous_studio.generate_content` — preserve verbatim during move<br>custom time limits — production timing-critical; do not alter on move |
| 3989 | `track_content_performance` | `core.tasks.track_content_performance` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4248 | `run_narrative_drift_cycle` | `narrative_drift.run_detector_cycle` | yes | — | — | non-standard registered name `narrative_drift.run_detector_cycle` — preserve verbatim during move |
| 4252 | `update_narrative_statuses` | `narrative_drift.update_narrative_statuses` | yes | — | — | non-standard registered name `narrative_drift.update_narrative_statuses` — preserve verbatim during move |
| 4320 | `trigger_content_from_narrative_shift` | `narrative_drift.trigger_content_from_shift` | yes | — | — | non-standard registered name `narrative_drift.trigger_content_from_shift` — preserve verbatim during move |
| 4900 | `generate_podcast_episode` | `core.tasks.generate_podcast_episode` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5038 | `generate_self_blog_task` | `core.tasks.generate_self_blog_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5042 | `draft_legal_document_task` | `core.tasks.draft_legal_document_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5075 | `generate_blog_with_topic_task` | `core.tasks.generate_blog_with_topic_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5102 | `generate_self_blog_deliberation_task` | `core.tasks.generate_self_blog_deliberation_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5108 | `generate_operator_edge_newsletter` | `core.tasks.generate_operator_edge_newsletter` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 5234 | `generate_weekly_synthesis` | `core.tasks.generate_weekly_synthesis` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5238 | `generate_pending_reviews` | `core.tasks.generate_pending_reviews` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 5469 | `generate_checklist_content_async` | `core.tasks.generate_checklist_content_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6537 | `check_content_diversity` | `core.tasks.check_content_diversity` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6726 | `process_content_ideas` | `core.tasks.process_content_ideas` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 6939 | `enhance_blog_task` | `core.tasks.enhance_blog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6943 | `evaluate_unscored_blogs` | `core.tasks.evaluate_unscored_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6991 | `reevaluate_enhanced_blogs` | `core.tasks.reevaluate_enhanced_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6995 | `auto_publish_approved_blogs` | `core.tasks.auto_publish_approved_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7040 | `content_autonomy_loop` | `core.tasks.content_autonomy_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 7136 | `auto_enhance_blogs` | `core.tasks.auto_enhance_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7140 | `score_unscored_deliverables` | `core.tasks.score_unscored_deliverables` | yes | — | `_calculate_deliverable_quality` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _calculate_deliverable_quality |
| 8698 | `score_episode_voice` | `content_studio.score_episode_voice` | yes | — | — | non-standard registered name `content_studio.score_episode_voice` — preserve verbatim during move |
| 8808 | `run_content_creation_agents` | `core.tasks.run_content_creation_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 8941 | `run_narrative_culture_agents` | `core.tasks.run_narrative_culture_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9047 | `auto_generate_podcast_episode` | `core.tasks.auto_generate_podcast_episode` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9051 | `run_content_studio_agents` | `core.tasks.run_content_studio_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 10749 | `generate_step_content` | `core.tasks.generate_step_content` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 11689 | `generate_competitor_comparison_task` | `core.tasks.generate_competitor_comparison_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |

### `tasks_conversations.py` — 9 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 613 | `cleanup_automated_conversation_artifacts` | `core.tasks.cleanup_automated_conversation_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2573 | `run_agent_conversation` | `core.tasks.run_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 2577 | `run_multi_agent_conversation` | `core.tasks.run_multi_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 2624 | `broadcast_conversation_status` | `core.tasks.broadcast_conversation_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2628 | `run_project_conversation` | `core.tasks.run_project_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10018 | `run_triggered_conversation` | `core.tasks.run_triggered_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 10288 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` | yes | — | — | non-standard registered name `trigger_signal_driven_conversation` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10984 | `cleanup_conversation_duplicates_task` | `core.tasks.cleanup_conversation_duplicates_task` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 11699 | `summarize_conversation_task` | `core.tasks.summarize_conversation_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs |

### `tasks_financial.py` — 25 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 3898 | `check_sec_filings_alert` | `core.tasks.check_sec_filings_alert` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3928 | `run_stock_audit_cycle` | `core.tasks.run_stock_audit_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3965 | `run_market_intelligence_desk` | `core.tasks.run_market_intelligence_desk` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3969 | `check_market_events_and_rerun` | `core.tasks.check_market_events_and_rerun` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3973 | `track_prediction_outcomes` | `learning_loop.track_prediction_outcomes` | yes | — | — | non-standard registered name `learning_loop.track_prediction_outcomes` — preserve verbatim during move |
| 4474 | `run_blockchain_security_monitor` | `autonomous.blockchain_security_monitor` | yes | — | — | non-standard registered name `autonomous.blockchain_security_monitor` — preserve verbatim during move |
| 4478 | `run_stock_market_intelligence` | `core.tasks.run_stock_market_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4818 | `run_crypto_sentiment_monitor` | `core.tasks.run_crypto_sentiment_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4888 | `run_sec_filing_analyzer` | `core.tasks.run_sec_filing_analyzer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4892 | `run_earnings_predictor` | `core.tasks.run_earnings_predictor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5242 | `collect_kalshi_prediction_markets` | `core.tasks.collect_kalshi_prediction_markets` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5246 | `collect_kalshi_market_intelligence` | `core.tasks.collect_kalshi_market_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5250 | `collect_sports_odds` | `core.tasks.collect_sports_odds` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5254 | `collect_sports_odds_intelligence` | `core.tasks.collect_sports_odds_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5258 | `daily_betting_digest` | `core.tasks.daily_betting_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5262 | `market_intelligence_scan` | `core.tasks.market_intelligence_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5266 | `market_movement_alerts` | `core.tasks.market_movement_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5270 | `snapshot_odds_for_line_movement` | `core.tasks.snapshot_odds_for_line_movement` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 5274 | `scan_arbs_and_notify` | `core.tasks.scan_arbs_and_notify` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5278 | `verify_betting_outcomes` | `core.tasks.verify_betting_outcomes` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5328 | `generate_daily_betting_brief` | `core.tasks.generate_daily_betting_brief` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5332 | `evaluate_ml_predictions` | `core.tasks.evaluate_ml_predictions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 6482 | `run_blockchain_monitoring_agents` | `core.tasks.run_blockchain_monitoring_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8893 | `run_stock_financial_agents` | `core.tasks.run_stock_financial_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 8921 | `run_prediction_market_agents` | `core.tasks.run_prediction_market_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |

### `tasks_initiatives.py` — 10 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 510 | `cleanup_junk_initiatives` | `core.tasks.cleanup_junk_initiatives` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10096 | `advance_initiative_pipeline` | `core.tasks.advance_initiative_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10260 | `auto_kickstart_stuck_initiatives` | `core.tasks.auto_kickstart_stuck_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10300 | `extract_action_items_from_session` | `core.tasks.extract_action_items_from_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10344 | `dispatch_pending_action_items` | `core.tasks.dispatch_pending_action_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 10348 | `retry_blocked_research` | `core.tasks.retry_blocked_research` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10352 | `check_blocked_research_for_unblock` | `core.tasks.check_blocked_research_for_unblock` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10390 | `process_initiative_auto_progression` | `core.tasks.process_initiative_auto_progression` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10394 | `detect_duplicate_initiatives` | `core.tasks.detect_duplicate_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10470 | `generate_initiative_stage_document` | `core.tasks.generate_initiative_stage_document` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |

### `tasks_learning.py` — 14 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 514 | `run_learning_loop_cycle` | `core.tasks.run_learning_loop_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 549 | `summarize_learning_readback` | `core.tasks.summarize_learning_readback` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 572 | `cleanup_learning_readback_events` | `core.tasks.cleanup_learning_readback_events` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 585 | `decay_learning_patterns` | `core.tasks.decay_learning_patterns` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 1869 | `update_learning_profiles` | `core.tasks.update_learning_profiles` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1873 | `run_daily_learning_pipeline` | `core.tasks.run_daily_learning_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2161 | `run_agent_learning_cycle` | `core.tasks.run_agent_learning_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2169 | `update_agent_effectiveness_from_learning` | `core.tasks.update_agent_effectiveness_from_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2173 | `broadcast_learning_status` | `core.tasks.broadcast_learning_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2181 | `embed_daily_agent_learning` | `core.tasks.embed_daily_agent_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3365 | `run_project_learning_cycle` | `core.tasks.run_project_learning_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3414 | `run_single_project_learning` | `core.tasks.run_single_project_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6737 | `mine_learning_patterns` | `core.tasks.mine_learning_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 11798 | `check_learning_loop_slo` | `core.check_learning_loop_slo` | yes | — | — | non-standard registered name `core.check_learning_loop_slo` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_media.py` — 11 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 647 | `create_talking_video_task` | `core.tasks.create_talking_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 1518 | `poll_pending_3d_models` | `core.tasks.poll_pending_3d_models` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3562 | `transcribe_video_task` | `core.tasks.transcribe_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3568 | `generate_video_content_pack_task` | `core.tasks.generate_video_content_pack_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3572 | `ingest_video_task` | `core.tasks.ingest_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3576 | `youtube_whisper_task` | `core.tasks.youtube_whisper_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 4657 | `start_resolve_render` | `core.tasks.start_resolve_render` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4662 | `poll_resolve_job_status` | `core.tasks.poll_resolve_job_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4666 | `record_resolve_outcome` | `core.tasks.record_resolve_outcome` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4880 | `run_thumbnail_optimizer` | `core.tasks.run_thumbnail_optimizer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10092 | `poll_processing_videos` | `core.tasks.poll_processing_videos` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_ops.py` — 134 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 503 | `reap_zombie_work` | `core.tasks.reap_zombie_work` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 604 | `auto_process_extracted_artifacts` | `core.tasks.auto_process_extracted_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1522 | `record_all_user_style_evolution` | `core.tasks.record_all_user_style_evolution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1526 | `execute_scheduled_workflow` | `core.tasks.execute_scheduled_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1530 | `sync_workflow_schedules` | `core.tasks.sync_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1541 | `check_workflow_schedules` | `core.tasks.check_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom retry policy — preserve verbatim |
| 1591 | `execute_pending_opportunity_tasks` | `core.tasks.execute_pending_opportunity_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1595 | `expire_old_opportunities` | `core.tasks.expire_old_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1599 | `generate_opportunity_report` | `core.tasks.generate_opportunity_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1603 | `train_ml_scoring_model` | `core.tasks.train_ml_scoring_model` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1607 | `evaluate_ml_model_performance` | `core.tasks.evaluate_ml_model_performance` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1611 | `process_realtime_scoring_queue` | `core.tasks.process_realtime_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1615 | `process_batch_scoring_queue` | `core.tasks.process_batch_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1665 | `cleanup_stale_scoring_requests` | `core.tasks.cleanup_stale_scoring_requests` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1673 | `process_distribution` | `core.tasks.process_distribution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1857 | `update_distribution_analytics` | `core.tasks.update_distribution_analytics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1861 | `discover_success_patterns` | `core.tasks.discover_success_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1865 | `generate_user_insights` | `core.tasks.generate_user_insights` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1912 | `run_proactive_system_check` | `core.tasks.run_proactive_system_check` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1957 | `check_all_alerts` | `core.tasks.check_all_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1987 | `generate_smart_suggestions` | `core.tasks.generate_smart_suggestions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2030 | `execute_scheduled_automations` | `core.tasks.execute_scheduled_automations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2091 | `cleanup_old_notifications` | `core.tasks.cleanup_old_notifications` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 2128 | `expire_old_suggestions` | `core.tasks.expire_old_suggestions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2177 | `validate_knowledge_sources` | `core.tasks.validate_knowledge_sources` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2595 | `propagate_new_policies` | `core.tasks.propagate_new_policies` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2636 | `broadcast_dream_journal` | `core.tasks.broadcast_dream_journal` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2640 | `score_and_promote_dreams` | `core.tasks.score_and_promote_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2644 | `process_approved_dreams` | `core.tasks.process_approved_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2648 | `cleanup_stale_dreams` | `core.tasks.cleanup_stale_dreams` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 2652 | `execute_dream_implementations` | `core.tasks.execute_dream_implementations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 3036 | `explore_dream_topic` | `core.tasks.explore_dream_topic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3040 | `run_hive_mind_session` | `core.tasks.run_hive_mind_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3087 | `generate_memory_embedding` | `core.tasks.generate_memory_embedding` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3222 | `sync_project_knowledge` | `core.tasks.sync_project_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3291 | `process_research_feedback` | `core.tasks.process_research_feedback` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3544 | `auto_resolve_knowledge_gaps` | `core.tasks.auto_resolve_knowledge_gaps` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3548 | `process_document_async` | `core.tasks.process_document_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3552 | `process_url_async` | `core.tasks.process_url_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3556 | `generate_document_embeddings` | `core.tasks.generate_document_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3580 | `collect_training_data` | `core.tasks.collect_training_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3584 | `collect_training_data_full` | `core.tasks.collect_training_data_full` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3736 | `cleanup_celery_task_events` | `core.tasks.cleanup_celery_task_events` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 3749 | `cleanup_llm_call_logs` | `core.tasks.cleanup_llm_call_logs` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 3762 | `generate_weekly_opportunity_digest` | `core.tasks.generate_weekly_opportunity_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3766 | `send_proactive_opportunity_alerts` | `core.tasks.send_proactive_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3770 | `send_personalized_opportunity_alerts` | `core.tasks.send_personalized_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3782 | `assemble_chunked_upload` | `core.tasks.assemble_chunked_upload` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3786 | `cleanup_expired_uploads` | `core.tasks.cleanup_expired_uploads` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 3828 | `sync_pipeline_insights_to_collective` | `core.tasks.sync_pipeline_insights_to_collective` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3832 | `run_autonomous_intelligence_loop` | `core.tasks.run_autonomous_intelligence_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3865 | `run_daily_intelligence_digest` | `core.tasks.run_daily_intelligence_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3993 | `process_hitl_escalations` | `core.tasks.process_hitl_escalations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4028 | `expire_overdue_validations` | `core.tasks.expire_overdue_validations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4067 | `process_event_bus_scoring_queue` | `core.tasks.process_event_bus_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4101 | `process_event_bus_validation_queue` | `core.tasks.process_event_bus_validation_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4135 | `process_event_bus_analytics_queue` | `core.tasks.process_event_bus_analytics_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4170 | `claim_stale_events` | `core.tasks.claim_stale_events` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4215 | `get_event_bus_stats` | `core.tasks.get_event_bus_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4324 | `unified_pipeline_health_check` | `unified_pipeline.health_check` | yes | — | — | non-standard registered name `unified_pipeline.health_check` — preserve verbatim during move |
| 4333 | `aggregate_roi_metrics_daily` | `core.tasks.aggregate_roi_metrics_daily` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4342 | `generate_weekly_intelligence_brief` | `core.tasks.generate_weekly_intelligence_brief` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4346 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_view` — preserve verbatim during move |
| 4373 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_click` — preserve verbatim during move |
| 4403 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_application` — preserve verbatim during move |
| 4433 | `record_revenue_event` | `roi_metrics.record_revenue` | yes | — | — | non-standard registered name `roi_metrics.record_revenue` — preserve verbatim during move |
| 4482 | `process_trigger_events` | `triggers.process_trigger_events` | yes | — | — | non-standard registered name `triggers.process_trigger_events` — preserve verbatim during move |
| 4626 | `create_default_triggers` | `triggers.create_default_triggers` | yes | — | — | non-standard registered name `triggers.create_default_triggers` — preserve verbatim during move |
| 4670 | `cleanup_old_resolve_jobs` | `core.tasks.cleanup_old_resolve_jobs` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4716 | `run_design_trends_monitor` | `core.tasks.run_design_trends_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4720 | `run_viral_content_predictor` | `core.tasks.run_viral_content_predictor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4724 | `run_job_match_intelligence` | `core.tasks.run_job_match_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4775 | `run_side_hustle_detector` | `core.tasks.run_side_hustle_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4822 | `run_tech_stack_tracker` | `core.tasks.run_tech_stack_tracker` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4826 | `run_ai_model_monitor` | `core.tasks.run_ai_model_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4830 | `run_case_law_monitor` | `core.tasks.run_case_law_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4834 | `run_regulatory_change_detector` | `core.tasks.run_regulatory_change_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4884 | `run_freelance_opportunity_scout` | `core.tasks.run_freelance_opportunity_scout` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4896 | `run_skill_gap_analyzer` | `core.tasks.run_skill_gap_analyzer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5115 | `run_autonomous_thinking_cycle` | `core.tasks.run_autonomous_thinking_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5119 | `scan_concerns_for_human_action` | `core.tasks.scan_concerns_for_human_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5123 | `batch_extract_artifacts` | `core.tasks.batch_extract_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5166 | `execute_approved_artifacts` | `core.tasks.execute_approved_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5186 | `execute_single_artifact` | `core.tasks.execute_single_artifact` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5336 | `maintain_dream_backlog` | `core.tasks.maintain_dream_backlog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5340 | `refresh_system_state_cache` | `core.tasks.refresh_system_state_cache` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5382 | `auto_triage_dreams` | `core.tasks.auto_triage_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5528 | `monitor_celery_health` | `core.tasks.monitor_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 6198 | `generate_human_attention_items` | `core.tasks.generate_human_attention_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6202 | `process_human_attention_lifecycle` | `core.tasks.process_human_attention_lifecycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6245 | `process_hivemind_sessions` | `core.tasks.process_hivemind_sessions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 6295 | `process_high_scoring_opportunities` | `core.tasks.process_high_scoring_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6541 | `check_celery_health` | `core.tasks.check_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6545 | `execute_orchestration_async` | `core.tasks.execute_orchestration_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6595 | `check_orchestration_timeouts` | `core.tasks.check_orchestration_timeouts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6599 | `check_orchestration_auto_approvals` | `core.tasks.check_orchestration_auto_approvals` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6627 | `execute_approved_dreams_via_orchestration` | `core.tasks.execute_approved_dreams_via_orchestration` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 6676 | `execute_single_dream` | `core.tasks.execute_single_dream` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6781 | `maintain_knowledge_freshness` | `core.tasks.maintain_knowledge_freshness` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6819 | `promote_to_shared_knowledge` | `core.tasks.promote_to_shared_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7021 | `verify_autopilot_action` | `core.tasks.verify_autopilot_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 8702 | `workspace_autopilot_tick` | `workspace.autopilot_tick` | yes | — | — | non-standard registered name `workspace.autopilot_tick` — preserve verbatim during move |
| 9170 | `update_mythology_pattern_statistics` | `core.tasks.update_mythology_pattern_statistics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9497 | `run_system_self_audit` | `core.tasks.run_system_self_audit` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9501 | `discover_and_import_audits` | `core.tasks.discover_and_import_audits` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9517 | `assign_open_findings_to_agents` | `core.tasks.assign_open_findings_to_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9532 | `execute_remediation_tasks` | `core.tasks.execute_remediation_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9571 | `verify_completed_fixes` | `core.tasks.verify_completed_fixes` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9598 | `run_autonomous_remediation_cycle` | `core.tasks.run_autonomous_remediation_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9647 | `assign_and_execute_remediation` | `core.tasks.assign_and_execute_remediation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10033 | `cleanup_resolved_signatures` | `core.tasks.cleanup_resolved_signatures` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10067 | `detect_failure_task` | `core.tasks.detect_failure_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10079 | `run_conceptforge_pipeline` | `core.tasks.run_conceptforge_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10292 | `process_pending_auto_topics` | `process_pending_auto_topics` | yes | — | — | non-standard registered name `process_pending_auto_topics` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10296 | `cleanup_expired_signals` | `cleanup_expired_signals` | yes | yes | — | non-standard registered name `cleanup_expired_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 10474 | `run_daily_priority_scan` | `core.tasks.run_daily_priority_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10505 | `check_operating_rhythm_status` | `core.tasks.check_operating_rhythm_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10550 | `cleanup_audio_cache` | `core.tasks.cleanup_audio_cache` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10557 | `auto_archive_stale_deliverables` | `core.tasks.auto_archive_stale_deliverables` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 10564 | `check_orphan_deliverables` | `core.tasks.check_orphan_deliverables` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 10570 | `enforce_db_retention` | `core.tasks.enforce_db_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 10753 | `run_all_desks_intelligence` | `core.tasks.run_all_desks_intelligence` | yes | — | `_run_desks_inner` | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>depends on 1 helper(s): _run_desks_inner |
| 10980 | `surface_top_dreams` | `core.tasks.surface_top_dreams` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 11002 | `rescan_active_workspaces` | `core.tasks.rescan_active_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 11120 | `cleanup_expired_pa_insights` | `core.tasks.cleanup_expired_pa_insights` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11150 | `enforce_data_retention` | `core.tasks.enforce_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11695 | `run_source_pack_workflow` | `core.tasks.run_source_pack_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11709 | `ops_control_loop` | `core.tasks.ops_control_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11713 | `check_llm_cost_spike` | `core.tasks.check_llm_cost_spike` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 11717 | `run_ops_autopilot` | `core.tasks.run_ops_autopilot` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 11737 | `post_ops_digest` | `core.tasks.post_ops_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 11747 | `sync_congress_data` | `core.tasks.sync_congress_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11784 | `execute_code_job` | `core.tasks.execute_code_job` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 11792 | `rag_retrieval_canary` | `core.rag_retrieval_canary` | yes | — | — | non-standard registered name `core.rag_retrieval_canary` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_push_notifications.py` — 1 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 2049 | `send_pending_notifications` | `core.tasks.send_pending_notifications` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_spiders.py` — 19 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 748 | `run_spider_by_category` | `core.tasks.run_spider_by_category` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 752 | `execute_single_spider` | `core.tasks.execute_single_spider` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 756 | `isolate_documents_batch` | `core.tasks.isolate_documents_batch` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 760 | `monitor_isolation_progress` | `core.tasks.monitor_isolation_progress` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 806 | `cleanup_isolation_metadata` | `core.tasks.cleanup_isolation_metadata` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 853 | `collect_spider_data` | `core.tasks.collect_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 859 | `process_spider_data_automatic` | `core.tasks.process_spider_data_automatic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 910 | `process_core_spider_data` | `core.tasks.process_core_spider_data` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 914 | `run_spider_network` | `core.tasks.run_spider_network` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 922 | `execute_single_spider_lightweight` | `core.tasks.execute_single_spider_lightweight` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1545 | `score_opportunities_from_spider_data` | `core.tasks.score_opportunities_from_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1669 | `score_spider_data_async` | `core.tasks.score_spider_data_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2587 | `trigger_spider_conversations` | `core.tasks.trigger_spider_conversations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3255 | `recalculate_spider_priorities` | `core.tasks.recalculate_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3327 | `update_project_spider_priorities` | `core.tasks.update_project_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3588 | `cleanup_spider_item_hashes` | `core.tasks.cleanup_spider_item_hashes` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 3627 | `spider_data_retention` | `core.tasks.spider_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6345 | `process_spider_actions` | `core.tasks.process_spider_actions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10284 | `aggregate_spider_signals` | `aggregate_spider_signals` | yes | yes | — | non-standard registered name `aggregate_spider_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |

## Helpers (candidates for `tasks_helpers.py`)

| Line | Name | Used by N task(s) |
| ---: | --- | ---: |
| 3450 | `_analyze_spider_data_for_trends` | 0 |
| 168 | `_apply_task_routing_override` | 0 |
| 9663 | `_assign_and_execute_remediation_DISABLED` | 0 |
| 11525 | `_auto_research_competitor` | 0 |
| 2911 | `_build_image_prompt_from_dream` | 0 |
| 4903 | `_build_operational_context` | 0 |
| 7174 | `_calculate_deliverable_quality` | 1 |
| 5696 | `_calculate_kpi_delta` | 0 |
| 353 | `_circuit_breaker_check` | 0 |
| 434 | `_circuit_breaker_record_timeout` | 0 |
| 427 | `_circuit_breaker_release` | 0 |
| 1272 | `_collect_angellist` | 0 |
| 1092 | `_collect_coingecko` | 0 |
| 1468 | `_collect_crowdfunding` | 0 |
| 1284 | `_collect_design_platform` | 0 |
| 1020 | `_collect_devto` | 0 |
| 1316 | `_collect_education_platform` | 0 |
| 1151 | `_collect_etherscan` | 0 |
| 1214 | `_collect_financial_default` | 0 |
| 1304 | `_collect_freelance_default` | 0 |
| 994 | `_collect_hackernews` | 0 |
| 1047 | `_collect_hashnode` | 0 |
| 1370 | `_collect_legal_platform` | 0 |
| 1493 | `_collect_news_default` | 0 |
| 1192 | `_collect_opensea` | 0 |
| 1203 | `_collect_premium_financial` | 0 |
| 925 | `_collect_spider_data_sync` | 0 |
| 1239 | `_collect_weworkremotely` | 0 |
| 1124 | `_collect_yahoo_finance` | 0 |
| 2213 | `_conversation_spawn_allowed` | 0 |
| 2188 | `_conversation_temporal_context` | 0 |
| 4485 | `_create_blockchain_alert_from_trigger` | 0 |
| 3510 | `_create_learning_notification` | 0 |
| 678 | `_create_spider_instance` | 0 |
| 4557 | `_create_stock_alert_from_trigger` | 0 |
| 10263 | `_detect_initiative_content_type` | 0 |
| 3489 | `_detect_research_deltas` | 0 |
| 3000 | `_detect_visual_style` | 0 |
| 5541 | `_evaluate_pilot_outcome` | 0 |
| 2689 | `_execute_content_implementation` | 0 |
| 2750 | `_execute_experiment_implementation` | 0 |
| 2655 | `_execute_feature_implementation` | 0 |
| 7064 | `_execute_gate_repair` | 0 |
| 2781 | `_execute_generic_implementation` | 0 |
| 2719 | `_execute_research_implementation` | 0 |
| 2812 | `_execute_visual_implementation` | 0 |
| 10397 | `_extract_agent_content` | 0 |
| 7859 | `_extract_agent_output_content` | 0 |
| 2455 | `_extract_conversation_knowledge` | 0 |
| 230 | `_extract_discourse_markers` | 0 |
| 5623 | `_extract_experiment_learning` | 0 |
| 2510 | `_extract_hivemind_knowledge` | 0 |
| 196 | `_extract_opener` | 0 |
| 3417 | `_extract_topics_from_project` | 0 |
| 5709 | `_feed_learnings_to_collective_intelligence` | 0 |
| 9411 | `_format_metrics_for_audit` | 0 |
| 5472 | `_gather_experiment_metrics` | 0 |
| 10111 | `_gather_initiative_research` | 0 |
| 9209 | `_gather_live_system_metrics` | 0 |
| 5909 | `_generate_checklist_documentation` | 0 |
| 8472 | `_get_agent_class` | 0 |
| 8586 | `_get_next_task_for_agent` | 0 |
| 238 | `_get_overused_markers` | 0 |
| 3475 | `_get_previous_findings` | 0 |
| 10227 | `_get_previous_stage_context` | 0 |
| 10099 | `_get_stage_document_type` | 0 |
| 6862 | `_get_workspace_for_skin_layer` | 0 |
| 2407 | `_handle_conversation_delegation` | 0 |
| 181 | `_is_media_task_blocked` | 0 |
| 2956 | `_is_visual_dream` | 0 |
| 8420 | `_preflight_check_agent_data` | 0 |
| 2269 | `_preflight_gather_agent_data` | 0 |
| 5821 | `_process_single_gate` | 0 |
| 277 | `_record_timeout_signature` | 0 |
| 7043 | `_route_gate_repair` | 0 |
| 9724 | `_route_spec_to_human_attention_standalone` | 0 |
| 8710 | `_run_agent_group` | 14 |
| 9801 | `_run_agent_remediation_batch_DISABLED` | 0 |
| 8510 | `_run_agent_warmup` | 0 |
| 11198 | `_run_comparison_generation` | 0 |
| 10781 | `_run_desks_inner` | 1 |
| 691 | `_run_spider_adapter` | 0 |
| 6170 | `_send_gate_processing_discord` | 0 |
| 5500 | `_send_halt_discord_notification` | 0 |
| 5792 | `_send_implementation_discord` | 0 |
| 4255 | `_send_narrative_alerts_to_discord` | 0 |
| 4274 | `_send_narrative_digest_to_discord` | 0 |
| 5760 | `_send_pilot_evaluation_discord` | 0 |
| 5609 | `_simulate_kpi_progress` | 0 |
| 11109 | `_summarize_diff` | 0 |
| 11099 | `_summarize_params` | 0 |
| 347 | `_task_hash` | 0 |
| 8769 | `_track_group_contribution` | 0 |
| 11044 | `_ttl_days` | 0 |
| 11055 | `_upsert_insight` | 0 |
| 247 | `validate_agent_output` | 0 |

## Beat-schedule references found in `core/celery.py`

Static grep over `core/celery.py` for `'task': '<name>'` literals. PeriodicTask DB rows are not enumerated here (static analysis only).

- `aggregate_spider_signals` — ✓ matches a tasks.py task
- `ai_core.tasks.clean_stale_data` — ?  not from tasks.py (sibling file or external)
- `ai_core.tasks.collect_real_opportunities` — ?  not from tasks.py (sibling file or external)
- `ai_core.tasks.warm_up_spider_network` — ?  not from tasks.py (sibling file or external)
- `cleanup_expired_signals` — ✓ matches a tasks.py task
- `core.tasks.auto_archive_stale_deliverables` — ✓ matches a tasks.py task
- `core.tasks.backfill_spider_embeddings` — ?  not from tasks.py (sibling file or external)
- `core.tasks.check_celery_health` — ✓ matches a tasks.py task
- `core.tasks.cleanup_audio_cache` — ✓ matches a tasks.py task
- `core.tasks.cleanup_boardroom_junk` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_celery_task_events` — ✓ matches a tasks.py task
- `core.tasks.cleanup_conversation_duplicates_task` — ✓ matches a tasks.py task
- `core.tasks.cleanup_expired_pa_insights` — ✓ matches a tasks.py task
- `core.tasks.cleanup_expired_uploads` — ✓ matches a tasks.py task
- `core.tasks.cleanup_junk_initiatives` — ✓ matches a tasks.py task
- `core.tasks.cleanup_learning_readback_events` — ✓ matches a tasks.py task
- `core.tasks.cleanup_llm_call_logs` — ✓ matches a tasks.py task
- `core.tasks.cleanup_old_notifications` — ✓ matches a tasks.py task
- `core.tasks.cleanup_old_resolve_jobs` — ✓ matches a tasks.py task
- `core.tasks.cleanup_resolved_signatures` — ✓ matches a tasks.py task
- `core.tasks.cleanup_spider_item_hashes` — ✓ matches a tasks.py task
- `core.tasks.cleanup_stale_agent_executions` — ✓ matches a tasks.py task
- `core.tasks.cleanup_stale_content` — ✓ matches a tasks.py task
- `core.tasks.cleanup_stale_dreams` — ✓ matches a tasks.py task
- `core.tasks.decay_learning_patterns` — ✓ matches a tasks.py task
- `core.tasks.enforce_data_retention` — ✓ matches a tasks.py task
- `core.tasks.enforce_db_retention` — ✓ matches a tasks.py task
- `core.tasks.generate_operator_edge_newsletter` — ✓ matches a tasks.py task
- `core.tasks.monitor_celery_health` — ✓ matches a tasks.py task
- `core.tasks.process_core_spider_data` — ✓ matches a tasks.py task
- `core.tasks.process_spider_actions` — ✓ matches a tasks.py task
- `core.tasks.run_coo_daily_diagnostic` — ?  not from tasks.py (sibling file or external)
- `core.tasks.run_cto_daily_diagnostic` — ?  not from tasks.py (sibling file or external)
- `core.tasks.run_heartbeat` — ✓ matches a tasks.py task
- `core.tasks.run_spider_network` — ✓ matches a tasks.py task
- `core.tasks.run_trend_daily_diagnostic` — ?  not from tasks.py (sibling file or external)
- `core.tasks.spider_data_retention` — ✓ matches a tasks.py task
- `core.tasks.surface_top_dreams` — ✓ matches a tasks.py task
- `intelligence.tasks.cleanup_old_opportunities` — ?  not from tasks.py (sibling file or external)
- `intelligence.tasks.scan_spider_opportunities` — ?  not from tasks.py (sibling file or external)
- `ml.cleanup_old_model_files` — ?  not from tasks.py (sibling file or external)
- `sports.cleanup_old_predictions` — ?  not from tasks.py (sibling file or external)

## Phase 1 — task name pinning

0 unpinned task(s) need an explicit `name="core.tasks.<func>"` kwarg added to their decorator. This edit is mechanical: a script can produce the diff, the runtime behaviour is identical (Celery already auto-registers under that name), and tests pass without modification.

**22 task(s) already carry a non-standard registered name** (no `core.tasks.` prefix). Phase 1 skips them — they're already pinned. **Phase 3 (module moves) MUST preserve every existing `name=` value verbatim**; see the Phase 3 warning section below for the full list grouped by prefix.

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


## Phase 3 — module moves: reviewer warnings

**22 task(s) carry non-standard registered names** that don't follow the `core.tasks.<func>` convention. Every one of these names is a runtime contract: it appears in beat schedules, `PeriodicTask` rows, `send_task()` callers, or code that hasn't been audited. **During module moves (Phase 3+), preserve each `name=` kwarg verbatim** — do not "normalize" them, do not drop the existing prefix, do not rewrite to match the destination module's path.

### Bare names (4) — highest collision risk

These tasks register with no prefix at all, so their registered name lives in Celery's global namespace and can collide with names from any other module. Treat each move as a security-sensitive change.

| Line | Function | Registered name |
| ---: | --- | --- |
| 10284 | `aggregate_spider_signals` | `aggregate_spider_signals` |
| 10288 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` |
| 10292 | `process_pending_auto_topics` | `process_pending_auto_topics` |
| 10296 | `cleanup_expired_signals` | `cleanup_expired_signals` |

### Prefixed names (18)

#### `autonomous.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4474 | `run_blockchain_security_monitor` | `autonomous.blockchain_security_monitor` |

#### `autonomous_studio.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 3985 | `generate_content_for_channel` | `autonomous_studio.generate_content` |

#### `content_studio.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 8698 | `score_episode_voice` | `content_studio.score_episode_voice` |

#### `core.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 11792 | `rag_retrieval_canary` | `core.rag_retrieval_canary` |
| 11798 | `check_learning_loop_slo` | `core.check_learning_loop_slo` |

#### `learning_loop.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 3973 | `track_prediction_outcomes` | `learning_loop.track_prediction_outcomes` |
| 3977 | `calculate_agent_accuracy` | `learning_loop.calculate_agent_accuracy` |

#### `narrative_drift.*` — 3 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4248 | `run_narrative_drift_cycle` | `narrative_drift.run_detector_cycle` |
| 4252 | `update_narrative_statuses` | `narrative_drift.update_narrative_statuses` |
| 4320 | `trigger_content_from_narrative_shift` | `narrative_drift.trigger_content_from_shift` |

#### `roi_metrics.*` — 4 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4346 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` |
| 4373 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` |
| 4403 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` |
| 4433 | `record_revenue_event` | `roi_metrics.record_revenue` |

#### `triggers.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4482 | `process_trigger_events` | `triggers.process_trigger_events` |
| 4626 | `create_default_triggers` | `triggers.create_default_triggers` |

#### `unified_pipeline.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4324 | `unified_pipeline_health_check` | `unified_pipeline.health_check` |

#### `workspace.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 8702 | `workspace_autopilot_tick` | `workspace.autopilot_tick` |

**Reviewer checklist for each Phase 3 module move:** before approving, grep the moved task's `name=` value against the current `core/tasks.py` and confirm character-for-character match. Any normalization, prefix change, or rename — even well-intentioned — silently breaks every existing caller.

## Pre-existing dead task-string references (rename-drift sweep)

**19 string-based task reference(s) across 2 file(s) point at task names that don't resolve to any registered task in `core/tasks.py`.** These are pre-existing rename-drift bugs — calls / lookups that would already fail today if invoked. Phase 1 does not introduce them, does not depend on them, and does not fix them. **Treat as a separate follow-up sweep, not a blocker for Phase 1.**

### `core/services/celery_health.py` — 2 dead reference(s)

| Line | Referenced task name |
| ---: | --- |
| 69 | `core.tasks.check_heart` |
| 70 | `core.tasks.check_circulatory` |

### `core/views_autonomous_dashboard.py` — 17 dead reference(s)

| Line | Referenced task name |
| ---: | --- |
| 51 | `autonomous_studio.run_main_loop` |
| 59 | `core.tasks.run_narrative_drift_detection` |
| 67 | `core.tasks.run_viral_prediction` |
| 77 | `core.tasks.run_design_trend_analysis` |
| 85 | `core.tasks.run_thumbnail_optimization` |
| 95 | `core.tasks.run_job_matching` |
| 103 | `core.tasks.run_freelance_scout` |
| 111 | `core.tasks.run_side_hustle_detection` |
| 121 | `core.tasks.run_market_intelligence` |
| 129 | `core.tasks.run_sec_filing_analysis` |
| 137 | `core.tasks.run_earnings_prediction` |
| 145 | `core.tasks.run_crypto_sentiment` |
| 171 | `core.tasks.run_tech_stack_analysis` |
| 179 | `core.tasks.run_ai_model_monitoring` |
| 187 | `core.tasks.run_skill_gap_analysis` |
| 197 | `core.tasks.run_case_law_monitoring` |
| 205 | `core.tasks.run_regulatory_monitoring` |

**Suggested follow-up:** open a separate issue for the rename-drift sweep. For each dead reference, either rename the call site to match the actual registered task name, or delete the dead caller entirely if the feature is no longer wired up. This sweep should land independently of the Wave B tasks refactor.

---

_Regenerate this plan after any change to `core/tasks.py` or the domain rules in `scripts/phase0_tasks_inventory.py`._
