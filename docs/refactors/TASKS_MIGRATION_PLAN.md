# Tasks Migration Plan — Phase 0 inventory

**Generated:** 2026-04-29T16:37:46+00:00
**Source:** `core/tasks.py`
**Generator:** `scripts/phase0_tasks_inventory.py`

> Read-only static analysis. No code was modified. The proposed destinations are first-match-wins regex rules in the script — treat them as a starting point, not a final assignment.

## Summary

- **Total tasks:** 333
- **Already name-pinned (`name=`):** 333
- **Unpinned (need Phase 1 edit):** 0
- **Tasks with `bind=True`:** 96
- **Tasks with custom time limits:** 43
- **Tasks referenced in beat schedule:** 31
- **Helpers in tasks.py (private + `validate_agent_output`):** 97
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
| `tasks_backfill.py` | 7 |
| `tasks_experiments.py` | 7 |
| `tasks_push_notifications.py` | 1 |

## Per-destination task lists

### `tasks_agents.py` — 45 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 445 | `cleanup_stale_agent_executions` | `core.tasks.cleanup_stale_agent_executions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 783 | `run_autonomy_cycle` | `core.tasks.run_autonomy_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 795 | `execute_agent_task` | `core.tasks.execute_agent_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 813 | `execute_initiative_stage_task` | `core.tasks.execute_initiative_stage_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 2388 | `agent_think_and_synthesize` | `core.tasks.agent_think_and_synthesize` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2408 | `embed_agent_activity` | `core.tasks.embed_agent_activity` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2855 | `generate_agent_dreams` | `core.tasks.generate_agent_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3354 | `update_agent_mood` | `core.tasks.update_agent_mood` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3360 | `check_mood_expirations` | `core.tasks.check_mood_expirations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3364 | `apply_mood_trigger_rules` | `core.tasks.apply_mood_trigger_rules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3368 | `evolve_agent_relationships` | `core.tasks.evolve_agent_relationships` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3416 | `update_alliance_strengths` | `core.tasks.update_alliance_strengths` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3430 | `broadcast_relationship_status` | `core.tasks.broadcast_relationship_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3434 | `process_agent_activity_xp` | `core.tasks.process_agent_activity_xp` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3438 | `check_level_milestones` | `core.tasks.check_level_milestones` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3475 | `broadcast_evolution_status` | `core.tasks.broadcast_evolution_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 4234 | `calculate_agent_accuracy` | `learning_loop.calculate_agent_accuracy` | yes | — | — | non-standard registered name `learning_loop.calculate_agent_accuracy` — preserve verbatim during move |
| 6808 | `run_market_monitoring_agents` | `core.tasks.run_market_monitoring_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6904 | `run_business_strategy_agents` | `core.tasks.run_business_strategy_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6908 | `exercise_all_dormant_agents` | `core.tasks.exercise_all_dormant_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7302 | `agent_workspace_status_report` | `core.tasks.agent_workspace_status_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7306 | `agent_research_to_workspace` | `core.tasks.agent_research_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7310 | `agent_content_to_workspace` | `core.tasks.agent_content_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7596 | `aggregate_tool_call_stats` | `core.tasks.aggregate_tool_call_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7600 | `agent_daily_summary` | `core.tasks.agent_daily_summary` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8838 | `universal_agent_workspace_output` | `core.tasks.universal_agent_workspace_output` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 9014 | `agent_category_rotation` | `core.tasks.agent_category_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9022 | `full_agent_rotation` | `core.tasks.full_agent_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9227 | `run_strategy_marketing_agents` | `core.tasks.run_strategy_marketing_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9253 | `run_research_analysis_agents` | `core.tasks.run_research_analysis_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9345 | `run_development_tech_agents` | `core.tasks.run_development_tech_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9374 | `run_executive_leadership_agents` | `core.tasks.run_executive_leadership_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9405 | `run_podcast_debate_agents` | `core.tasks.run_podcast_debate_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9451 | `run_campaign_series_agents` | `core.tasks.run_campaign_series_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9470 | `run_system_orchestration_agents` | `core.tasks.run_system_orchestration_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9505 | `run_quality_audit_agents` | `core.tasks.run_quality_audit_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9524 | `run_specialty_agents` | `core.tasks.run_specialty_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9872 | `run_agent_health_rotation` | `core.tasks.run_agent_health_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10160 | `run_agent_remediation_batch` | `core.tasks.run_agent_remediation_batch` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10960 | `claude_code_engineer_task` | `core.tasks.claude_code_engineer_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 10967 | `claude_code_agent_respond` | `core.tasks.claude_code_agent_respond` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 10974 | `process_pa_chat_task` | `core.tasks.process_pa_chat_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 10982 | `rebuild_pa_context_task` | `core.tasks.rebuild_pa_context_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11096 | `process_pa_tts_task` | `core.tasks.process_pa_tts_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11424 | `analyze_pa_tool_patterns` | `core.tasks.analyze_pa_tool_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |

### `tasks_backfill.py` — 7 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 1075 | `backfill_spider_embeddings` | `core.tasks.backfill_spider_embeddings` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 1126 | `backfill_signal_scores` | `backfill_signal_scores` | yes | — | — | non-standard registered name `backfill_signal_scores` — preserve verbatim during move |
| 3314 | `backfill_memory_embeddings` | `core.tasks.backfill_memory_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3350 | `backfill_conversation_embeddings` | `core.tasks.backfill_conversation_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 9077 | `backfill_voice_scores` | `content_studio.backfill_voice_scores` | yes | — | — | non-standard registered name `content_studio.backfill_voice_scores` — preserve verbatim during move |
| 10853 | `backfill_stage_documents` | `core.tasks.backfill_stage_documents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 12240 | `backfill_deliverable_workspaces` | `core.tasks.backfill_deliverable_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |

### `tasks_body_systems.py` — 13 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 6728 | `run_heartbeat` | `core.tasks.run_heartbeat` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6732 | `check_breathing` | `core.tasks.check_breathing` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6736 | `daily_cost_forecast` | `core.tasks.daily_cost_forecast` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6740 | `reset_daily_respiratory_stats` | `core.tasks.reset_daily_respiratory_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6772 | `check_circulation` | `core.tasks.check_circulation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 6776 | `check_spine_alignment` | `core.tasks.check_spine_alignment` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6780 | `immune_scan` | `core.tasks.immune_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6784 | `check_digestion` | `core.tasks.check_digestion` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6788 | `check_muscular` | `core.tasks.check_muscular` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6792 | `check_brain` | `core.tasks.check_brain` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6796 | `check_skin` | `core.tasks.check_skin` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6800 | `check_nervous` | `core.tasks.check_nervous` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6804 | `coordinate_body` | `core.tasks.coordinate_body` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_content.py` — 38 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 449 | `cleanup_stale_content` | `core.tasks.cleanup_stale_content` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 550 | `execute_workspace_pipeline` | `core.tasks.execute_workspace_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 555 | `execute_demo_pipeline_task` | `core.tasks.execute_demo_pipeline_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 824 | `produce_content_package` | `core.tasks.produce_content_package` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 2814 | `trigger_project_research` | `core.tasks.trigger_project_research` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 4031 | `generate_content_package` | `core.tasks.generate_content_package` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4035 | `generate_ai_series` | `core.tasks.generate_ai_series` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4238 | `run_autonomous_content_studio` | `core.tasks.run_autonomous_content_studio` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4242 | `generate_content_for_channel` | `autonomous_studio.generate_content` | yes | — | — | non-standard registered name `autonomous_studio.generate_content` — preserve verbatim during move<br>custom time limits — production timing-critical; do not alter on move |
| 4246 | `track_content_performance` | `core.tasks.track_content_performance` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4505 | `run_narrative_drift_cycle` | `narrative_drift.run_detector_cycle` | yes | — | — | non-standard registered name `narrative_drift.run_detector_cycle` — preserve verbatim during move |
| 4509 | `update_narrative_statuses` | `narrative_drift.update_narrative_statuses` | yes | — | — | non-standard registered name `narrative_drift.update_narrative_statuses` — preserve verbatim during move |
| 4577 | `trigger_content_from_narrative_shift` | `narrative_drift.trigger_content_from_shift` | yes | — | — | non-standard registered name `narrative_drift.trigger_content_from_shift` — preserve verbatim during move |
| 5157 | `generate_podcast_episode` | `core.tasks.generate_podcast_episode` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5295 | `generate_self_blog_task` | `core.tasks.generate_self_blog_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5299 | `draft_legal_document_task` | `core.tasks.draft_legal_document_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5332 | `generate_blog_with_topic_task` | `core.tasks.generate_blog_with_topic_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5359 | `generate_self_blog_deliberation_task` | `core.tasks.generate_self_blog_deliberation_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5365 | `generate_operator_edge_newsletter` | `core.tasks.generate_operator_edge_newsletter` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 5491 | `generate_weekly_synthesis` | `core.tasks.generate_weekly_synthesis` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5495 | `generate_pending_reviews` | `core.tasks.generate_pending_reviews` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 5726 | `generate_checklist_content_async` | `core.tasks.generate_checklist_content_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6912 | `check_content_diversity` | `core.tasks.check_content_diversity` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7101 | `process_content_ideas` | `core.tasks.process_content_ideas` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 7314 | `enhance_blog_task` | `core.tasks.enhance_blog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7318 | `evaluate_unscored_blogs` | `core.tasks.evaluate_unscored_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7366 | `reevaluate_enhanced_blogs` | `core.tasks.reevaluate_enhanced_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7370 | `auto_publish_approved_blogs` | `core.tasks.auto_publish_approved_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7415 | `content_autonomy_loop` | `core.tasks.content_autonomy_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 7511 | `auto_enhance_blogs` | `core.tasks.auto_enhance_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7515 | `score_unscored_deliverables` | `core.tasks.score_unscored_deliverables` | yes | — | `_calculate_deliverable_quality` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _calculate_deliverable_quality |
| 9073 | `score_episode_voice` | `content_studio.score_episode_voice` | yes | — | — | non-standard registered name `content_studio.score_episode_voice` — preserve verbatim during move |
| 9187 | `run_content_creation_agents` | `core.tasks.run_content_creation_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9320 | `run_narrative_culture_agents` | `core.tasks.run_narrative_culture_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9426 | `auto_generate_podcast_episode` | `core.tasks.auto_generate_podcast_episode` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9430 | `run_content_studio_agents` | `core.tasks.run_content_studio_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 11132 | `generate_step_content` | `core.tasks.generate_step_content` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 12072 | `generate_competitor_comparison_task` | `core.tasks.generate_competitor_comparison_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |

### `tasks_conversations.py` — 9 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 569 | `cleanup_automated_conversation_artifacts` | `core.tasks.cleanup_automated_conversation_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2796 | `run_agent_conversation` | `core.tasks.run_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 2800 | `run_multi_agent_conversation` | `core.tasks.run_multi_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 2847 | `broadcast_conversation_status` | `core.tasks.broadcast_conversation_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2851 | `run_project_conversation` | `core.tasks.run_project_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10397 | `run_triggered_conversation` | `core.tasks.run_triggered_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 10667 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` | yes | — | — | non-standard registered name `trigger_signal_driven_conversation` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 11367 | `cleanup_conversation_duplicates_task` | `core.tasks.cleanup_conversation_duplicates_task` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 12082 | `summarize_conversation_task` | `core.tasks.summarize_conversation_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs |

### `tasks_experiments.py` — 7 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 578 | `cleanup_halted_experiments` | `core.tasks.cleanup_halted_experiments` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 584 | `cleanup_stale_running_experiments` | `core.tasks.cleanup_stale_running_experiments` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 695 | `reconcile_experiment_status_outcome` | `core.tasks.reconcile_experiment_status_outcome` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5730 | `monitor_running_experiments` | `core.tasks.monitor_running_experiments` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5793 | `update_experiment_kpis` | `core.tasks.update_experiment_kpis` | yes | — | `_send_kpi_update_discord_notification` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _send_kpi_update_discord_notification |
| 5865 | `check_kpi_alerts` | `core.tasks.check_kpi_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5913 | `send_weekly_kpi_summary` | `core.tasks.send_weekly_kpi_summary` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_financial.py` — 25 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 4155 | `check_sec_filings_alert` | `core.tasks.check_sec_filings_alert` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4185 | `run_stock_audit_cycle` | `core.tasks.run_stock_audit_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4222 | `run_market_intelligence_desk` | `core.tasks.run_market_intelligence_desk` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4226 | `check_market_events_and_rerun` | `core.tasks.check_market_events_and_rerun` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4230 | `track_prediction_outcomes` | `learning_loop.track_prediction_outcomes` | yes | — | — | non-standard registered name `learning_loop.track_prediction_outcomes` — preserve verbatim during move |
| 4731 | `run_blockchain_security_monitor` | `autonomous.blockchain_security_monitor` | yes | — | — | non-standard registered name `autonomous.blockchain_security_monitor` — preserve verbatim during move |
| 4735 | `run_stock_market_intelligence` | `core.tasks.run_stock_market_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5075 | `run_crypto_sentiment_monitor` | `core.tasks.run_crypto_sentiment_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5145 | `run_sec_filing_analyzer` | `core.tasks.run_sec_filing_analyzer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5149 | `run_earnings_predictor` | `core.tasks.run_earnings_predictor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5499 | `collect_kalshi_prediction_markets` | `core.tasks.collect_kalshi_prediction_markets` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5503 | `collect_kalshi_market_intelligence` | `core.tasks.collect_kalshi_market_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5507 | `collect_sports_odds` | `core.tasks.collect_sports_odds` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5511 | `collect_sports_odds_intelligence` | `core.tasks.collect_sports_odds_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5515 | `daily_betting_digest` | `core.tasks.daily_betting_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5519 | `market_intelligence_scan` | `core.tasks.market_intelligence_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5523 | `market_movement_alerts` | `core.tasks.market_movement_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5527 | `snapshot_odds_for_line_movement` | `core.tasks.snapshot_odds_for_line_movement` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 5531 | `scan_arbs_and_notify` | `core.tasks.scan_arbs_and_notify` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5535 | `verify_betting_outcomes` | `core.tasks.verify_betting_outcomes` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5585 | `generate_daily_betting_brief` | `core.tasks.generate_daily_betting_brief` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5589 | `evaluate_ml_predictions` | `core.tasks.evaluate_ml_predictions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 6857 | `run_blockchain_monitoring_agents` | `core.tasks.run_blockchain_monitoring_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9272 | `run_stock_financial_agents` | `core.tasks.run_stock_financial_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9300 | `run_prediction_market_agents` | `core.tasks.run_prediction_market_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |

### `tasks_initiatives.py` — 10 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 466 | `cleanup_junk_initiatives` | `core.tasks.cleanup_junk_initiatives` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10475 | `advance_initiative_pipeline` | `core.tasks.advance_initiative_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10639 | `auto_kickstart_stuck_initiatives` | `core.tasks.auto_kickstart_stuck_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10679 | `extract_action_items_from_session` | `core.tasks.extract_action_items_from_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10723 | `dispatch_pending_action_items` | `core.tasks.dispatch_pending_action_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 10727 | `retry_blocked_research` | `core.tasks.retry_blocked_research` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10731 | `check_blocked_research_for_unblock` | `core.tasks.check_blocked_research_for_unblock` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10769 | `process_initiative_auto_progression` | `core.tasks.process_initiative_auto_progression` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10773 | `detect_duplicate_initiatives` | `core.tasks.detect_duplicate_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10849 | `generate_initiative_stage_document` | `core.tasks.generate_initiative_stage_document` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |

### `tasks_learning.py` — 14 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 470 | `run_learning_loop_cycle` | `core.tasks.run_learning_loop_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 505 | `summarize_learning_readback` | `core.tasks.summarize_learning_readback` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 528 | `cleanup_learning_readback_events` | `core.tasks.cleanup_learning_readback_events` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 541 | `decay_learning_patterns` | `core.tasks.decay_learning_patterns` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 2092 | `update_learning_profiles` | `core.tasks.update_learning_profiles` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2096 | `run_daily_learning_pipeline` | `core.tasks.run_daily_learning_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2384 | `run_agent_learning_cycle` | `core.tasks.run_agent_learning_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2392 | `update_agent_effectiveness_from_learning` | `core.tasks.update_agent_effectiveness_from_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2396 | `broadcast_learning_status` | `core.tasks.broadcast_learning_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2404 | `embed_daily_agent_learning` | `core.tasks.embed_daily_agent_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3622 | `run_project_learning_cycle` | `core.tasks.run_project_learning_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3671 | `run_single_project_learning` | `core.tasks.run_single_project_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7112 | `mine_learning_patterns` | `core.tasks.mine_learning_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 12181 | `check_learning_loop_slo` | `core.check_learning_loop_slo` | yes | — | — | non-standard registered name `core.check_learning_loop_slo` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_media.py` — 11 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 804 | `create_talking_video_task` | `core.tasks.create_talking_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 1741 | `poll_pending_3d_models` | `core.tasks.poll_pending_3d_models` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3819 | `transcribe_video_task` | `core.tasks.transcribe_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3825 | `generate_video_content_pack_task` | `core.tasks.generate_video_content_pack_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3829 | `ingest_video_task` | `core.tasks.ingest_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3833 | `youtube_whisper_task` | `core.tasks.youtube_whisper_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 4914 | `start_resolve_render` | `core.tasks.start_resolve_render` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4919 | `poll_resolve_job_status` | `core.tasks.poll_resolve_job_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4923 | `record_resolve_outcome` | `core.tasks.record_resolve_outcome` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5137 | `run_thumbnail_optimizer` | `core.tasks.run_thumbnail_optimizer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10471 | `poll_processing_videos` | `core.tasks.poll_processing_videos` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_ops.py` — 134 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 459 | `reap_zombie_work` | `core.tasks.reap_zombie_work` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 560 | `auto_process_extracted_artifacts` | `core.tasks.auto_process_extracted_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1745 | `record_all_user_style_evolution` | `core.tasks.record_all_user_style_evolution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1749 | `execute_scheduled_workflow` | `core.tasks.execute_scheduled_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1753 | `sync_workflow_schedules` | `core.tasks.sync_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1764 | `check_workflow_schedules` | `core.tasks.check_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom retry policy — preserve verbatim |
| 1814 | `execute_pending_opportunity_tasks` | `core.tasks.execute_pending_opportunity_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1818 | `expire_old_opportunities` | `core.tasks.expire_old_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1822 | `generate_opportunity_report` | `core.tasks.generate_opportunity_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1826 | `train_ml_scoring_model` | `core.tasks.train_ml_scoring_model` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1830 | `evaluate_ml_model_performance` | `core.tasks.evaluate_ml_model_performance` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1834 | `process_realtime_scoring_queue` | `core.tasks.process_realtime_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1838 | `process_batch_scoring_queue` | `core.tasks.process_batch_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1888 | `cleanup_stale_scoring_requests` | `core.tasks.cleanup_stale_scoring_requests` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1896 | `process_distribution` | `core.tasks.process_distribution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 2080 | `update_distribution_analytics` | `core.tasks.update_distribution_analytics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2084 | `discover_success_patterns` | `core.tasks.discover_success_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2088 | `generate_user_insights` | `core.tasks.generate_user_insights` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2135 | `run_proactive_system_check` | `core.tasks.run_proactive_system_check` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2180 | `check_all_alerts` | `core.tasks.check_all_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2210 | `generate_smart_suggestions` | `core.tasks.generate_smart_suggestions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2253 | `execute_scheduled_automations` | `core.tasks.execute_scheduled_automations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2314 | `cleanup_old_notifications` | `core.tasks.cleanup_old_notifications` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 2351 | `expire_old_suggestions` | `core.tasks.expire_old_suggestions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2400 | `validate_knowledge_sources` | `core.tasks.validate_knowledge_sources` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2818 | `propagate_new_policies` | `core.tasks.propagate_new_policies` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2859 | `broadcast_dream_journal` | `core.tasks.broadcast_dream_journal` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2863 | `score_and_promote_dreams` | `core.tasks.score_and_promote_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2867 | `process_approved_dreams` | `core.tasks.process_approved_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2871 | `cleanup_stale_dreams` | `core.tasks.cleanup_stale_dreams` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 2875 | `execute_dream_implementations` | `core.tasks.execute_dream_implementations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 3259 | `explore_dream_topic` | `core.tasks.explore_dream_topic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3263 | `run_hive_mind_session` | `core.tasks.run_hive_mind_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3310 | `generate_memory_embedding` | `core.tasks.generate_memory_embedding` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3479 | `sync_project_knowledge` | `core.tasks.sync_project_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3548 | `process_research_feedback` | `core.tasks.process_research_feedback` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3801 | `auto_resolve_knowledge_gaps` | `core.tasks.auto_resolve_knowledge_gaps` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3805 | `process_document_async` | `core.tasks.process_document_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3809 | `process_url_async` | `core.tasks.process_url_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3813 | `generate_document_embeddings` | `core.tasks.generate_document_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3837 | `collect_training_data` | `core.tasks.collect_training_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3841 | `collect_training_data_full` | `core.tasks.collect_training_data_full` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3993 | `cleanup_celery_task_events` | `core.tasks.cleanup_celery_task_events` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4006 | `cleanup_llm_call_logs` | `core.tasks.cleanup_llm_call_logs` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4019 | `generate_weekly_opportunity_digest` | `core.tasks.generate_weekly_opportunity_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4023 | `send_proactive_opportunity_alerts` | `core.tasks.send_proactive_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4027 | `send_personalized_opportunity_alerts` | `core.tasks.send_personalized_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4039 | `assemble_chunked_upload` | `core.tasks.assemble_chunked_upload` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4043 | `cleanup_expired_uploads` | `core.tasks.cleanup_expired_uploads` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4085 | `sync_pipeline_insights_to_collective` | `core.tasks.sync_pipeline_insights_to_collective` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4089 | `run_autonomous_intelligence_loop` | `core.tasks.run_autonomous_intelligence_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4122 | `run_daily_intelligence_digest` | `core.tasks.run_daily_intelligence_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4250 | `process_hitl_escalations` | `core.tasks.process_hitl_escalations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4285 | `expire_overdue_validations` | `core.tasks.expire_overdue_validations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4324 | `process_event_bus_scoring_queue` | `core.tasks.process_event_bus_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4358 | `process_event_bus_validation_queue` | `core.tasks.process_event_bus_validation_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4392 | `process_event_bus_analytics_queue` | `core.tasks.process_event_bus_analytics_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4427 | `claim_stale_events` | `core.tasks.claim_stale_events` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4472 | `get_event_bus_stats` | `core.tasks.get_event_bus_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4581 | `unified_pipeline_health_check` | `unified_pipeline.health_check` | yes | — | — | non-standard registered name `unified_pipeline.health_check` — preserve verbatim during move |
| 4590 | `aggregate_roi_metrics_daily` | `core.tasks.aggregate_roi_metrics_daily` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4599 | `generate_weekly_intelligence_brief` | `core.tasks.generate_weekly_intelligence_brief` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4603 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_view` — preserve verbatim during move |
| 4630 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_click` — preserve verbatim during move |
| 4660 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_application` — preserve verbatim during move |
| 4690 | `record_revenue_event` | `roi_metrics.record_revenue` | yes | — | — | non-standard registered name `roi_metrics.record_revenue` — preserve verbatim during move |
| 4739 | `process_trigger_events` | `triggers.process_trigger_events` | yes | — | — | non-standard registered name `triggers.process_trigger_events` — preserve verbatim during move |
| 4883 | `create_default_triggers` | `triggers.create_default_triggers` | yes | — | — | non-standard registered name `triggers.create_default_triggers` — preserve verbatim during move |
| 4927 | `cleanup_old_resolve_jobs` | `core.tasks.cleanup_old_resolve_jobs` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4973 | `run_design_trends_monitor` | `core.tasks.run_design_trends_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4977 | `run_viral_content_predictor` | `core.tasks.run_viral_content_predictor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4981 | `run_job_match_intelligence` | `core.tasks.run_job_match_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5032 | `run_side_hustle_detector` | `core.tasks.run_side_hustle_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5079 | `run_tech_stack_tracker` | `core.tasks.run_tech_stack_tracker` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5083 | `run_ai_model_monitor` | `core.tasks.run_ai_model_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5087 | `run_case_law_monitor` | `core.tasks.run_case_law_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5091 | `run_regulatory_change_detector` | `core.tasks.run_regulatory_change_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5141 | `run_freelance_opportunity_scout` | `core.tasks.run_freelance_opportunity_scout` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5153 | `run_skill_gap_analyzer` | `core.tasks.run_skill_gap_analyzer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5372 | `run_autonomous_thinking_cycle` | `core.tasks.run_autonomous_thinking_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5376 | `scan_concerns_for_human_action` | `core.tasks.scan_concerns_for_human_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5380 | `batch_extract_artifacts` | `core.tasks.batch_extract_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5423 | `execute_approved_artifacts` | `core.tasks.execute_approved_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5443 | `execute_single_artifact` | `core.tasks.execute_single_artifact` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5593 | `maintain_dream_backlog` | `core.tasks.maintain_dream_backlog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5597 | `refresh_system_state_cache` | `core.tasks.refresh_system_state_cache` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5639 | `auto_triage_dreams` | `core.tasks.auto_triage_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5789 | `monitor_celery_health` | `core.tasks.monitor_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 6573 | `generate_human_attention_items` | `core.tasks.generate_human_attention_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6577 | `process_human_attention_lifecycle` | `core.tasks.process_human_attention_lifecycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6620 | `process_hivemind_sessions` | `core.tasks.process_hivemind_sessions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 6670 | `process_high_scoring_opportunities` | `core.tasks.process_high_scoring_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6916 | `check_celery_health` | `core.tasks.check_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6920 | `execute_orchestration_async` | `core.tasks.execute_orchestration_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6970 | `check_orchestration_timeouts` | `core.tasks.check_orchestration_timeouts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6974 | `check_orchestration_auto_approvals` | `core.tasks.check_orchestration_auto_approvals` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7002 | `execute_approved_dreams_via_orchestration` | `core.tasks.execute_approved_dreams_via_orchestration` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 7051 | `execute_single_dream` | `core.tasks.execute_single_dream` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7156 | `maintain_knowledge_freshness` | `core.tasks.maintain_knowledge_freshness` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7194 | `promote_to_shared_knowledge` | `core.tasks.promote_to_shared_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7396 | `verify_autopilot_action` | `core.tasks.verify_autopilot_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 9081 | `workspace_autopilot_tick` | `workspace.autopilot_tick` | yes | — | — | non-standard registered name `workspace.autopilot_tick` — preserve verbatim during move |
| 9549 | `update_mythology_pattern_statistics` | `core.tasks.update_mythology_pattern_statistics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9876 | `run_system_self_audit` | `core.tasks.run_system_self_audit` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9880 | `discover_and_import_audits` | `core.tasks.discover_and_import_audits` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9896 | `assign_open_findings_to_agents` | `core.tasks.assign_open_findings_to_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9911 | `execute_remediation_tasks` | `core.tasks.execute_remediation_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9950 | `verify_completed_fixes` | `core.tasks.verify_completed_fixes` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9977 | `run_autonomous_remediation_cycle` | `core.tasks.run_autonomous_remediation_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10026 | `assign_and_execute_remediation` | `core.tasks.assign_and_execute_remediation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10412 | `cleanup_resolved_signatures` | `core.tasks.cleanup_resolved_signatures` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10446 | `detect_failure_task` | `core.tasks.detect_failure_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10458 | `run_conceptforge_pipeline` | `core.tasks.run_conceptforge_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10671 | `process_pending_auto_topics` | `process_pending_auto_topics` | yes | — | — | non-standard registered name `process_pending_auto_topics` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10675 | `cleanup_expired_signals` | `cleanup_expired_signals` | yes | yes | — | non-standard registered name `cleanup_expired_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 10857 | `run_daily_priority_scan` | `core.tasks.run_daily_priority_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10888 | `check_operating_rhythm_status` | `core.tasks.check_operating_rhythm_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10933 | `cleanup_audio_cache` | `core.tasks.cleanup_audio_cache` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10940 | `auto_archive_stale_deliverables` | `core.tasks.auto_archive_stale_deliverables` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 10947 | `check_orphan_deliverables` | `core.tasks.check_orphan_deliverables` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 10953 | `enforce_db_retention` | `core.tasks.enforce_db_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11136 | `run_all_desks_intelligence` | `core.tasks.run_all_desks_intelligence` | yes | — | `_run_desks_inner` | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>depends on 1 helper(s): _run_desks_inner |
| 11363 | `surface_top_dreams` | `core.tasks.surface_top_dreams` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 11385 | `rescan_active_workspaces` | `core.tasks.rescan_active_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 11503 | `cleanup_expired_pa_insights` | `core.tasks.cleanup_expired_pa_insights` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11533 | `enforce_data_retention` | `core.tasks.enforce_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 12078 | `run_source_pack_workflow` | `core.tasks.run_source_pack_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12092 | `ops_control_loop` | `core.tasks.ops_control_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12096 | `check_llm_cost_spike` | `core.tasks.check_llm_cost_spike` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 12100 | `run_ops_autopilot` | `core.tasks.run_ops_autopilot` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 12120 | `post_ops_digest` | `core.tasks.post_ops_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 12130 | `sync_congress_data` | `core.tasks.sync_congress_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12167 | `execute_code_job` | `core.tasks.execute_code_job` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 12175 | `rag_retrieval_canary` | `core.rag_retrieval_canary` | yes | — | — | non-standard registered name `core.rag_retrieval_canary` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_push_notifications.py` — 1 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 2272 | `send_pending_notifications` | `core.tasks.send_pending_notifications` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_spiders.py` — 19 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 905 | `run_spider_by_category` | `core.tasks.run_spider_by_category` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 909 | `execute_single_spider` | `core.tasks.execute_single_spider` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 913 | `isolate_documents_batch` | `core.tasks.isolate_documents_batch` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 917 | `monitor_isolation_progress` | `core.tasks.monitor_isolation_progress` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 963 | `cleanup_isolation_metadata` | `core.tasks.cleanup_isolation_metadata` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1010 | `collect_spider_data` | `core.tasks.collect_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1016 | `process_spider_data_automatic` | `core.tasks.process_spider_data_automatic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1067 | `process_core_spider_data` | `core.tasks.process_core_spider_data` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 1071 | `run_spider_network` | `core.tasks.run_spider_network` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 1145 | `execute_single_spider_lightweight` | `core.tasks.execute_single_spider_lightweight` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1768 | `score_opportunities_from_spider_data` | `core.tasks.score_opportunities_from_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1892 | `score_spider_data_async` | `core.tasks.score_spider_data_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2810 | `trigger_spider_conversations` | `core.tasks.trigger_spider_conversations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3512 | `recalculate_spider_priorities` | `core.tasks.recalculate_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3584 | `update_project_spider_priorities` | `core.tasks.update_project_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3845 | `cleanup_spider_item_hashes` | `core.tasks.cleanup_spider_item_hashes` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 3884 | `spider_data_retention` | `core.tasks.spider_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6720 | `process_spider_actions` | `core.tasks.process_spider_actions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10663 | `aggregate_spider_signals` | `aggregate_spider_signals` | yes | yes | — | non-standard registered name `aggregate_spider_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |

## Helpers (candidates for `tasks_helpers.py`)

| Line | Name | Used by N task(s) |
| ---: | --- | ---: |
| 3707 | `_analyze_spider_data_for_trends` | 0 |
| 124 | `_apply_task_routing_override` | 0 |
| 10042 | `_assign_and_execute_remediation_DISABLED` | 0 |
| 11908 | `_auto_research_competitor` | 0 |
| 3134 | `_build_image_prompt_from_dream` | 0 |
| 5160 | `_build_operational_context` | 0 |
| 7549 | `_calculate_deliverable_quality` | 1 |
| 6071 | `_calculate_kpi_delta` | 0 |
| 309 | `_circuit_breaker_check` | 0 |
| 390 | `_circuit_breaker_record_timeout` | 0 |
| 383 | `_circuit_breaker_release` | 0 |
| 1495 | `_collect_angellist` | 0 |
| 1315 | `_collect_coingecko` | 0 |
| 1691 | `_collect_crowdfunding` | 0 |
| 1507 | `_collect_design_platform` | 0 |
| 1243 | `_collect_devto` | 0 |
| 1539 | `_collect_education_platform` | 0 |
| 1374 | `_collect_etherscan` | 0 |
| 1437 | `_collect_financial_default` | 0 |
| 1527 | `_collect_freelance_default` | 0 |
| 1217 | `_collect_hackernews` | 0 |
| 1270 | `_collect_hashnode` | 0 |
| 1593 | `_collect_legal_platform` | 0 |
| 1716 | `_collect_news_default` | 0 |
| 1415 | `_collect_opensea` | 0 |
| 1426 | `_collect_premium_financial` | 0 |
| 1148 | `_collect_spider_data_sync` | 0 |
| 1462 | `_collect_weworkremotely` | 0 |
| 1347 | `_collect_yahoo_finance` | 0 |
| 2436 | `_conversation_spawn_allowed` | 0 |
| 2411 | `_conversation_temporal_context` | 0 |
| 4742 | `_create_blockchain_alert_from_trigger` | 0 |
| 3767 | `_create_learning_notification` | 0 |
| 835 | `_create_spider_instance` | 0 |
| 4814 | `_create_stock_alert_from_trigger` | 0 |
| 10642 | `_detect_initiative_content_type` | 0 |
| 3746 | `_detect_research_deltas` | 0 |
| 3223 | `_detect_visual_style` | 0 |
| 5916 | `_evaluate_pilot_outcome` | 0 |
| 2912 | `_execute_content_implementation` | 0 |
| 2973 | `_execute_experiment_implementation` | 0 |
| 2878 | `_execute_feature_implementation` | 0 |
| 7439 | `_execute_gate_repair` | 0 |
| 3004 | `_execute_generic_implementation` | 0 |
| 2942 | `_execute_research_implementation` | 0 |
| 3035 | `_execute_visual_implementation` | 0 |
| 10776 | `_extract_agent_content` | 0 |
| 8234 | `_extract_agent_output_content` | 0 |
| 2678 | `_extract_conversation_knowledge` | 0 |
| 186 | `_extract_discourse_markers` | 0 |
| 5998 | `_extract_experiment_learning` | 0 |
| 2733 | `_extract_hivemind_knowledge` | 0 |
| 152 | `_extract_opener` | 0 |
| 3674 | `_extract_topics_from_project` | 0 |
| 6084 | `_feed_learnings_to_collective_intelligence` | 0 |
| 9790 | `_format_metrics_for_audit` | 0 |
| 5733 | `_gather_experiment_metrics` | 0 |
| 10490 | `_gather_initiative_research` | 0 |
| 9588 | `_gather_live_system_metrics` | 0 |
| 6284 | `_generate_checklist_documentation` | 0 |
| 8847 | `_get_agent_class` | 0 |
| 8961 | `_get_next_task_for_agent` | 0 |
| 194 | `_get_overused_markers` | 0 |
| 3732 | `_get_previous_findings` | 0 |
| 10606 | `_get_previous_stage_context` | 0 |
| 10478 | `_get_stage_document_type` | 0 |
| 7237 | `_get_workspace_for_skin_layer` | 0 |
| 2630 | `_handle_conversation_delegation` | 0 |
| 137 | `_is_media_task_blocked` | 0 |
| 3179 | `_is_visual_dream` | 0 |
| 8795 | `_preflight_check_agent_data` | 0 |
| 2492 | `_preflight_gather_agent_data` | 0 |
| 6196 | `_process_single_gate` | 0 |
| 233 | `_record_timeout_signature` | 0 |
| 7418 | `_route_gate_repair` | 0 |
| 10103 | `_route_spec_to_human_attention_standalone` | 0 |
| 9089 | `_run_agent_group` | 14 |
| 10180 | `_run_agent_remediation_batch_DISABLED` | 0 |
| 8885 | `_run_agent_warmup` | 0 |
| 11581 | `_run_comparison_generation` | 0 |
| 11164 | `_run_desks_inner` | 1 |
| 848 | `_run_spider_adapter` | 0 |
| 6545 | `_send_gate_processing_discord` | 0 |
| 5761 | `_send_halt_discord_notification` | 0 |
| 6167 | `_send_implementation_discord` | 0 |
| 5832 | `_send_kpi_update_discord_notification` | 1 |
| 4512 | `_send_narrative_alerts_to_discord` | 0 |
| 4531 | `_send_narrative_digest_to_discord` | 0 |
| 6135 | `_send_pilot_evaluation_discord` | 0 |
| 5984 | `_simulate_kpi_progress` | 0 |
| 11492 | `_summarize_diff` | 0 |
| 11482 | `_summarize_params` | 0 |
| 303 | `_task_hash` | 0 |
| 9148 | `_track_group_contribution` | 0 |
| 11427 | `_ttl_days` | 0 |
| 11438 | `_upsert_insight` | 0 |
| 203 | `validate_agent_output` | 0 |

## Beat-schedule references found in `core/celery.py`

Static grep over `core/celery.py` for `'task': '<name>'` literals. PeriodicTask DB rows are not enumerated here (static analysis only).

- `aggregate_spider_signals` — ✓ matches a tasks.py task
- `ai_core.tasks.clean_stale_data` — ?  not from tasks.py (sibling file or external)
- `ai_core.tasks.collect_real_opportunities` — ?  not from tasks.py (sibling file or external)
- `ai_core.tasks.warm_up_spider_network` — ?  not from tasks.py (sibling file or external)
- `cleanup_expired_signals` — ✓ matches a tasks.py task
- `core.tasks.auto_archive_stale_deliverables` — ✓ matches a tasks.py task
- `core.tasks.backfill_spider_embeddings` — ✓ matches a tasks.py task
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

**24 task(s) already carry a non-standard registered name** (no `core.tasks.` prefix). Phase 1 skips them — they're already pinned. **Phase 3 (module moves) MUST preserve every existing `name=` value verbatim**; see the Phase 3 warning section below for the full list grouped by prefix.

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

**24 task(s) carry non-standard registered names** that don't follow the `core.tasks.<func>` convention. Every one of these names is a runtime contract: it appears in beat schedules, `PeriodicTask` rows, `send_task()` callers, or code that hasn't been audited. **During module moves (Phase 3+), preserve each `name=` kwarg verbatim** — do not "normalize" them, do not drop the existing prefix, do not rewrite to match the destination module's path.

### Bare names (5) — highest collision risk

These tasks register with no prefix at all, so their registered name lives in Celery's global namespace and can collide with names from any other module. Treat each move as a security-sensitive change.

| Line | Function | Registered name |
| ---: | --- | --- |
| 1126 | `backfill_signal_scores` | `backfill_signal_scores` |
| 10663 | `aggregate_spider_signals` | `aggregate_spider_signals` |
| 10667 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` |
| 10671 | `process_pending_auto_topics` | `process_pending_auto_topics` |
| 10675 | `cleanup_expired_signals` | `cleanup_expired_signals` |

### Prefixed names (19)

#### `autonomous.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4731 | `run_blockchain_security_monitor` | `autonomous.blockchain_security_monitor` |

#### `autonomous_studio.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4242 | `generate_content_for_channel` | `autonomous_studio.generate_content` |

#### `content_studio.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 9073 | `score_episode_voice` | `content_studio.score_episode_voice` |
| 9077 | `backfill_voice_scores` | `content_studio.backfill_voice_scores` |

#### `core.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 12175 | `rag_retrieval_canary` | `core.rag_retrieval_canary` |
| 12181 | `check_learning_loop_slo` | `core.check_learning_loop_slo` |

#### `learning_loop.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4230 | `track_prediction_outcomes` | `learning_loop.track_prediction_outcomes` |
| 4234 | `calculate_agent_accuracy` | `learning_loop.calculate_agent_accuracy` |

#### `narrative_drift.*` — 3 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4505 | `run_narrative_drift_cycle` | `narrative_drift.run_detector_cycle` |
| 4509 | `update_narrative_statuses` | `narrative_drift.update_narrative_statuses` |
| 4577 | `trigger_content_from_narrative_shift` | `narrative_drift.trigger_content_from_shift` |

#### `roi_metrics.*` — 4 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4603 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` |
| 4630 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` |
| 4660 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` |
| 4690 | `record_revenue_event` | `roi_metrics.record_revenue` |

#### `triggers.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4739 | `process_trigger_events` | `triggers.process_trigger_events` |
| 4883 | `create_default_triggers` | `triggers.create_default_triggers` |

#### `unified_pipeline.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4581 | `unified_pipeline_health_check` | `unified_pipeline.health_check` |

#### `workspace.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 9081 | `workspace_autopilot_tick` | `workspace.autopilot_tick` |

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
