# Tasks Migration Plan — Phase 0 inventory

**Generated:** 2026-04-29T16:06:47+00:00
**Source:** `core/tasks.py`
**Generator:** `scripts/phase0_tasks_inventory.py`

> Read-only static analysis. No code was modified. The proposed destinations are first-match-wins regex rules in the script — treat them as a starting point, not a final assignment.

## Summary

- **Total tasks:** 348
- **Already name-pinned (`name=`):** 348
- **Unpinned (need Phase 1 edit):** 0
- **Tasks with `bind=True`:** 97
- **Tasks with custom time limits:** 43
- **Tasks referenced in beat schedule:** 32
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
| `tasks_boardroom.py` | 15 |
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
| 419 | `cleanup_stale_agent_executions` | `core.tasks.cleanup_stale_agent_executions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 769 | `run_autonomy_cycle` | `core.tasks.run_autonomy_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 781 | `execute_agent_task` | `core.tasks.execute_agent_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 799 | `execute_initiative_stage_task` | `core.tasks.execute_initiative_stage_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 2374 | `agent_think_and_synthesize` | `core.tasks.agent_think_and_synthesize` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2394 | `embed_agent_activity` | `core.tasks.embed_agent_activity` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2867 | `generate_agent_dreams` | `core.tasks.generate_agent_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3366 | `update_agent_mood` | `core.tasks.update_agent_mood` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3372 | `check_mood_expirations` | `core.tasks.check_mood_expirations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3376 | `apply_mood_trigger_rules` | `core.tasks.apply_mood_trigger_rules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3380 | `evolve_agent_relationships` | `core.tasks.evolve_agent_relationships` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3428 | `update_alliance_strengths` | `core.tasks.update_alliance_strengths` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3442 | `broadcast_relationship_status` | `core.tasks.broadcast_relationship_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3446 | `process_agent_activity_xp` | `core.tasks.process_agent_activity_xp` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3450 | `check_level_milestones` | `core.tasks.check_level_milestones` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3487 | `broadcast_evolution_status` | `core.tasks.broadcast_evolution_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 4246 | `calculate_agent_accuracy` | `learning_loop.calculate_agent_accuracy` | yes | — | — | non-standard registered name `learning_loop.calculate_agent_accuracy` — preserve verbatim during move |
| 6864 | `run_market_monitoring_agents` | `core.tasks.run_market_monitoring_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6960 | `run_business_strategy_agents` | `core.tasks.run_business_strategy_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6964 | `exercise_all_dormant_agents` | `core.tasks.exercise_all_dormant_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7368 | `agent_workspace_status_report` | `core.tasks.agent_workspace_status_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7372 | `agent_research_to_workspace` | `core.tasks.agent_research_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7376 | `agent_content_to_workspace` | `core.tasks.agent_content_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7662 | `aggregate_tool_call_stats` | `core.tasks.aggregate_tool_call_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7666 | `agent_daily_summary` | `core.tasks.agent_daily_summary` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8904 | `universal_agent_workspace_output` | `core.tasks.universal_agent_workspace_output` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 9080 | `agent_category_rotation` | `core.tasks.agent_category_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9088 | `full_agent_rotation` | `core.tasks.full_agent_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9293 | `run_strategy_marketing_agents` | `core.tasks.run_strategy_marketing_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9319 | `run_research_analysis_agents` | `core.tasks.run_research_analysis_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9411 | `run_development_tech_agents` | `core.tasks.run_development_tech_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9440 | `run_executive_leadership_agents` | `core.tasks.run_executive_leadership_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9471 | `run_podcast_debate_agents` | `core.tasks.run_podcast_debate_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9517 | `run_campaign_series_agents` | `core.tasks.run_campaign_series_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9536 | `run_system_orchestration_agents` | `core.tasks.run_system_orchestration_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9571 | `run_quality_audit_agents` | `core.tasks.run_quality_audit_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9590 | `run_specialty_agents` | `core.tasks.run_specialty_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9938 | `run_agent_health_rotation` | `core.tasks.run_agent_health_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10226 | `run_agent_remediation_batch` | `core.tasks.run_agent_remediation_batch` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 11026 | `claude_code_engineer_task` | `core.tasks.claude_code_engineer_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11033 | `claude_code_agent_respond` | `core.tasks.claude_code_agent_respond` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11040 | `process_pa_chat_task` | `core.tasks.process_pa_chat_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 11048 | `rebuild_pa_context_task` | `core.tasks.rebuild_pa_context_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11162 | `process_pa_tts_task` | `core.tasks.process_pa_tts_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11490 | `analyze_pa_tool_patterns` | `core.tasks.analyze_pa_tool_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |

### `tasks_backfill.py` — 7 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 1061 | `backfill_spider_embeddings` | `core.tasks.backfill_spider_embeddings` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 1112 | `backfill_signal_scores` | `backfill_signal_scores` | yes | — | — | non-standard registered name `backfill_signal_scores` — preserve verbatim during move |
| 3326 | `backfill_memory_embeddings` | `core.tasks.backfill_memory_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3362 | `backfill_conversation_embeddings` | `core.tasks.backfill_conversation_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 9143 | `backfill_voice_scores` | `content_studio.backfill_voice_scores` | yes | — | — | non-standard registered name `content_studio.backfill_voice_scores` — preserve verbatim during move |
| 10919 | `backfill_stage_documents` | `core.tasks.backfill_stage_documents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 12306 | `backfill_deliverable_workspaces` | `core.tasks.backfill_deliverable_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |

### `tasks_boardroom.py` — 15 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 524 | `cleanup_boardroom_junk` | `core.tasks.cleanup_boardroom_junk` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 528 | `auto_approve_boardroom_items` | `core.tasks.auto_approve_boardroom_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 542 | `cleanup_expired_boardroom_items` | `core.tasks.cleanup_expired_boardroom_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2790 | `auto_promote_decisions` | `core.tasks.auto_promote_decisions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5661 | `auto_approve_low_risk_gates` | `core.tasks.auto_approve_low_risk_gates` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5669 | `auto_promote_low_risk_decisions` | `core.tasks.auto_promote_low_risk_decisions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5673 | `report_pending_review_metrics` | `core.tasks.report_pending_review_metrics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5677 | `ai_promote_decisions` | `core.tasks.ai_promote_decisions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 5681 | `auto_complete_pilots` | `core.tasks.auto_complete_pilots` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5685 | `evaluate_pilots_with_thinking_agent` | `core.tasks.evaluate_pilots_with_thinking_agent` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5957 | `evaluate_and_complete_pilots` | `core.tasks.evaluate_and_complete_pilots` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6212 | `execute_pilot_implementations` | `core.tasks.execute_pilot_implementations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6245 | `process_gates_and_deploy_pilots` | `core.tasks.process_gates_and_deploy_pilots` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 6672 | `enrich_boardroom_ml_predictions` | `core.tasks.enrich_boardroom_ml_predictions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 7157 | `process_gate_progression` | `core.tasks.process_gate_progression` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_body_systems.py` — 13 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 6784 | `run_heartbeat` | `core.tasks.run_heartbeat` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6788 | `check_breathing` | `core.tasks.check_breathing` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6792 | `daily_cost_forecast` | `core.tasks.daily_cost_forecast` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6796 | `reset_daily_respiratory_stats` | `core.tasks.reset_daily_respiratory_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6828 | `check_circulation` | `core.tasks.check_circulation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 6832 | `check_spine_alignment` | `core.tasks.check_spine_alignment` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6836 | `immune_scan` | `core.tasks.immune_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6840 | `check_digestion` | `core.tasks.check_digestion` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6844 | `check_muscular` | `core.tasks.check_muscular` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6848 | `check_brain` | `core.tasks.check_brain` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6852 | `check_skin` | `core.tasks.check_skin` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6856 | `check_nervous` | `core.tasks.check_nervous` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6860 | `coordinate_body` | `core.tasks.coordinate_body` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_content.py` — 38 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 423 | `cleanup_stale_content` | `core.tasks.cleanup_stale_content` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 532 | `execute_workspace_pipeline` | `core.tasks.execute_workspace_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 537 | `execute_demo_pipeline_task` | `core.tasks.execute_demo_pipeline_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 810 | `produce_content_package` | `core.tasks.produce_content_package` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 2826 | `trigger_project_research` | `core.tasks.trigger_project_research` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 4043 | `generate_content_package` | `core.tasks.generate_content_package` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4047 | `generate_ai_series` | `core.tasks.generate_ai_series` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4250 | `run_autonomous_content_studio` | `core.tasks.run_autonomous_content_studio` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4254 | `generate_content_for_channel` | `autonomous_studio.generate_content` | yes | — | — | non-standard registered name `autonomous_studio.generate_content` — preserve verbatim during move<br>custom time limits — production timing-critical; do not alter on move |
| 4258 | `track_content_performance` | `core.tasks.track_content_performance` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4517 | `run_narrative_drift_cycle` | `narrative_drift.run_detector_cycle` | yes | — | — | non-standard registered name `narrative_drift.run_detector_cycle` — preserve verbatim during move |
| 4521 | `update_narrative_statuses` | `narrative_drift.update_narrative_statuses` | yes | — | — | non-standard registered name `narrative_drift.update_narrative_statuses` — preserve verbatim during move |
| 4589 | `trigger_content_from_narrative_shift` | `narrative_drift.trigger_content_from_shift` | yes | — | — | non-standard registered name `narrative_drift.trigger_content_from_shift` — preserve verbatim during move |
| 5169 | `generate_podcast_episode` | `core.tasks.generate_podcast_episode` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5307 | `generate_self_blog_task` | `core.tasks.generate_self_blog_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5311 | `draft_legal_document_task` | `core.tasks.draft_legal_document_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5344 | `generate_blog_with_topic_task` | `core.tasks.generate_blog_with_topic_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5371 | `generate_self_blog_deliberation_task` | `core.tasks.generate_self_blog_deliberation_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5377 | `generate_operator_edge_newsletter` | `core.tasks.generate_operator_edge_newsletter` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 5503 | `generate_weekly_synthesis` | `core.tasks.generate_weekly_synthesis` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5507 | `generate_pending_reviews` | `core.tasks.generate_pending_reviews` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 5766 | `generate_checklist_content_async` | `core.tasks.generate_checklist_content_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6968 | `check_content_diversity` | `core.tasks.check_content_diversity` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7167 | `process_content_ideas` | `core.tasks.process_content_ideas` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 7380 | `enhance_blog_task` | `core.tasks.enhance_blog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7384 | `evaluate_unscored_blogs` | `core.tasks.evaluate_unscored_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7432 | `reevaluate_enhanced_blogs` | `core.tasks.reevaluate_enhanced_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7436 | `auto_publish_approved_blogs` | `core.tasks.auto_publish_approved_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7481 | `content_autonomy_loop` | `core.tasks.content_autonomy_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 7577 | `auto_enhance_blogs` | `core.tasks.auto_enhance_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7581 | `score_unscored_deliverables` | `core.tasks.score_unscored_deliverables` | yes | — | `_calculate_deliverable_quality` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _calculate_deliverable_quality |
| 9139 | `score_episode_voice` | `content_studio.score_episode_voice` | yes | — | — | non-standard registered name `content_studio.score_episode_voice` — preserve verbatim during move |
| 9253 | `run_content_creation_agents` | `core.tasks.run_content_creation_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9386 | `run_narrative_culture_agents` | `core.tasks.run_narrative_culture_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9492 | `auto_generate_podcast_episode` | `core.tasks.auto_generate_podcast_episode` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9496 | `run_content_studio_agents` | `core.tasks.run_content_studio_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 11198 | `generate_step_content` | `core.tasks.generate_step_content` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 12138 | `generate_competitor_comparison_task` | `core.tasks.generate_competitor_comparison_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |

### `tasks_conversations.py` — 9 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 555 | `cleanup_automated_conversation_artifacts` | `core.tasks.cleanup_automated_conversation_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2782 | `run_agent_conversation` | `core.tasks.run_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 2786 | `run_multi_agent_conversation` | `core.tasks.run_multi_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 2859 | `broadcast_conversation_status` | `core.tasks.broadcast_conversation_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2863 | `run_project_conversation` | `core.tasks.run_project_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10463 | `run_triggered_conversation` | `core.tasks.run_triggered_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 10733 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` | yes | — | — | non-standard registered name `trigger_signal_driven_conversation` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 11433 | `cleanup_conversation_duplicates_task` | `core.tasks.cleanup_conversation_duplicates_task` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 12148 | `summarize_conversation_task` | `core.tasks.summarize_conversation_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs |

### `tasks_experiments.py` — 7 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 564 | `cleanup_halted_experiments` | `core.tasks.cleanup_halted_experiments` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 570 | `cleanup_stale_running_experiments` | `core.tasks.cleanup_stale_running_experiments` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 681 | `reconcile_experiment_status_outcome` | `core.tasks.reconcile_experiment_status_outcome` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5770 | `monitor_running_experiments` | `core.tasks.monitor_running_experiments` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5833 | `update_experiment_kpis` | `core.tasks.update_experiment_kpis` | yes | — | `_send_kpi_update_discord_notification` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _send_kpi_update_discord_notification |
| 5905 | `check_kpi_alerts` | `core.tasks.check_kpi_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5953 | `send_weekly_kpi_summary` | `core.tasks.send_weekly_kpi_summary` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_financial.py` — 25 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 4167 | `check_sec_filings_alert` | `core.tasks.check_sec_filings_alert` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4197 | `run_stock_audit_cycle` | `core.tasks.run_stock_audit_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4234 | `run_market_intelligence_desk` | `core.tasks.run_market_intelligence_desk` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4238 | `check_market_events_and_rerun` | `core.tasks.check_market_events_and_rerun` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4242 | `track_prediction_outcomes` | `learning_loop.track_prediction_outcomes` | yes | — | — | non-standard registered name `learning_loop.track_prediction_outcomes` — preserve verbatim during move |
| 4743 | `run_blockchain_security_monitor` | `autonomous.blockchain_security_monitor` | yes | — | — | non-standard registered name `autonomous.blockchain_security_monitor` — preserve verbatim during move |
| 4747 | `run_stock_market_intelligence` | `core.tasks.run_stock_market_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5087 | `run_crypto_sentiment_monitor` | `core.tasks.run_crypto_sentiment_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5157 | `run_sec_filing_analyzer` | `core.tasks.run_sec_filing_analyzer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5161 | `run_earnings_predictor` | `core.tasks.run_earnings_predictor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5511 | `collect_kalshi_prediction_markets` | `core.tasks.collect_kalshi_prediction_markets` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5515 | `collect_kalshi_market_intelligence` | `core.tasks.collect_kalshi_market_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5519 | `collect_sports_odds` | `core.tasks.collect_sports_odds` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5523 | `collect_sports_odds_intelligence` | `core.tasks.collect_sports_odds_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5527 | `daily_betting_digest` | `core.tasks.daily_betting_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5531 | `market_intelligence_scan` | `core.tasks.market_intelligence_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5535 | `market_movement_alerts` | `core.tasks.market_movement_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5539 | `snapshot_odds_for_line_movement` | `core.tasks.snapshot_odds_for_line_movement` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 5543 | `scan_arbs_and_notify` | `core.tasks.scan_arbs_and_notify` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5547 | `verify_betting_outcomes` | `core.tasks.verify_betting_outcomes` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5597 | `generate_daily_betting_brief` | `core.tasks.generate_daily_betting_brief` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5601 | `evaluate_ml_predictions` | `core.tasks.evaluate_ml_predictions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 6913 | `run_blockchain_monitoring_agents` | `core.tasks.run_blockchain_monitoring_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9338 | `run_stock_financial_agents` | `core.tasks.run_stock_financial_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |
| 9366 | `run_prediction_market_agents` | `core.tasks.run_prediction_market_agents` | yes | — | `_run_agent_group` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _run_agent_group |

### `tasks_initiatives.py` — 10 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 440 | `cleanup_junk_initiatives` | `core.tasks.cleanup_junk_initiatives` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10541 | `advance_initiative_pipeline` | `core.tasks.advance_initiative_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10705 | `auto_kickstart_stuck_initiatives` | `core.tasks.auto_kickstart_stuck_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10745 | `extract_action_items_from_session` | `core.tasks.extract_action_items_from_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10789 | `dispatch_pending_action_items` | `core.tasks.dispatch_pending_action_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 10793 | `retry_blocked_research` | `core.tasks.retry_blocked_research` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10797 | `check_blocked_research_for_unblock` | `core.tasks.check_blocked_research_for_unblock` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10835 | `process_initiative_auto_progression` | `core.tasks.process_initiative_auto_progression` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10839 | `detect_duplicate_initiatives` | `core.tasks.detect_duplicate_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10915 | `generate_initiative_stage_document` | `core.tasks.generate_initiative_stage_document` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |

### `tasks_learning.py` — 14 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 444 | `run_learning_loop_cycle` | `core.tasks.run_learning_loop_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 479 | `summarize_learning_readback` | `core.tasks.summarize_learning_readback` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 502 | `cleanup_learning_readback_events` | `core.tasks.cleanup_learning_readback_events` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 515 | `decay_learning_patterns` | `core.tasks.decay_learning_patterns` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 2078 | `update_learning_profiles` | `core.tasks.update_learning_profiles` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2082 | `run_daily_learning_pipeline` | `core.tasks.run_daily_learning_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2370 | `run_agent_learning_cycle` | `core.tasks.run_agent_learning_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2378 | `update_agent_effectiveness_from_learning` | `core.tasks.update_agent_effectiveness_from_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2382 | `broadcast_learning_status` | `core.tasks.broadcast_learning_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2390 | `embed_daily_agent_learning` | `core.tasks.embed_daily_agent_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3634 | `run_project_learning_cycle` | `core.tasks.run_project_learning_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3683 | `run_single_project_learning` | `core.tasks.run_single_project_learning` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7178 | `mine_learning_patterns` | `core.tasks.mine_learning_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 12247 | `check_learning_loop_slo` | `core.check_learning_loop_slo` | yes | — | — | non-standard registered name `core.check_learning_loop_slo` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_media.py` — 11 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 790 | `create_talking_video_task` | `core.tasks.create_talking_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 1727 | `poll_pending_3d_models` | `core.tasks.poll_pending_3d_models` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3831 | `transcribe_video_task` | `core.tasks.transcribe_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3837 | `generate_video_content_pack_task` | `core.tasks.generate_video_content_pack_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3841 | `ingest_video_task` | `core.tasks.ingest_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3845 | `youtube_whisper_task` | `core.tasks.youtube_whisper_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 4926 | `start_resolve_render` | `core.tasks.start_resolve_render` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4931 | `poll_resolve_job_status` | `core.tasks.poll_resolve_job_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4935 | `record_resolve_outcome` | `core.tasks.record_resolve_outcome` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5149 | `run_thumbnail_optimizer` | `core.tasks.run_thumbnail_optimizer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10537 | `poll_processing_videos` | `core.tasks.poll_processing_videos` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_ops.py` — 134 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 433 | `reap_zombie_work` | `core.tasks.reap_zombie_work` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 546 | `auto_process_extracted_artifacts` | `core.tasks.auto_process_extracted_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1731 | `record_all_user_style_evolution` | `core.tasks.record_all_user_style_evolution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1735 | `execute_scheduled_workflow` | `core.tasks.execute_scheduled_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1739 | `sync_workflow_schedules` | `core.tasks.sync_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1750 | `check_workflow_schedules` | `core.tasks.check_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom retry policy — preserve verbatim |
| 1800 | `execute_pending_opportunity_tasks` | `core.tasks.execute_pending_opportunity_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1804 | `expire_old_opportunities` | `core.tasks.expire_old_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1808 | `generate_opportunity_report` | `core.tasks.generate_opportunity_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1812 | `train_ml_scoring_model` | `core.tasks.train_ml_scoring_model` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1816 | `evaluate_ml_model_performance` | `core.tasks.evaluate_ml_model_performance` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1820 | `process_realtime_scoring_queue` | `core.tasks.process_realtime_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1824 | `process_batch_scoring_queue` | `core.tasks.process_batch_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1874 | `cleanup_stale_scoring_requests` | `core.tasks.cleanup_stale_scoring_requests` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1882 | `process_distribution` | `core.tasks.process_distribution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 2066 | `update_distribution_analytics` | `core.tasks.update_distribution_analytics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2070 | `discover_success_patterns` | `core.tasks.discover_success_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2074 | `generate_user_insights` | `core.tasks.generate_user_insights` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2121 | `run_proactive_system_check` | `core.tasks.run_proactive_system_check` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2166 | `check_all_alerts` | `core.tasks.check_all_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2196 | `generate_smart_suggestions` | `core.tasks.generate_smart_suggestions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2239 | `execute_scheduled_automations` | `core.tasks.execute_scheduled_automations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2300 | `cleanup_old_notifications` | `core.tasks.cleanup_old_notifications` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 2337 | `expire_old_suggestions` | `core.tasks.expire_old_suggestions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2386 | `validate_knowledge_sources` | `core.tasks.validate_knowledge_sources` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2830 | `propagate_new_policies` | `core.tasks.propagate_new_policies` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2871 | `broadcast_dream_journal` | `core.tasks.broadcast_dream_journal` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2875 | `score_and_promote_dreams` | `core.tasks.score_and_promote_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2879 | `process_approved_dreams` | `core.tasks.process_approved_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2883 | `cleanup_stale_dreams` | `core.tasks.cleanup_stale_dreams` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 2887 | `execute_dream_implementations` | `core.tasks.execute_dream_implementations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 3271 | `explore_dream_topic` | `core.tasks.explore_dream_topic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3275 | `run_hive_mind_session` | `core.tasks.run_hive_mind_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3322 | `generate_memory_embedding` | `core.tasks.generate_memory_embedding` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3491 | `sync_project_knowledge` | `core.tasks.sync_project_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3560 | `process_research_feedback` | `core.tasks.process_research_feedback` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3813 | `auto_resolve_knowledge_gaps` | `core.tasks.auto_resolve_knowledge_gaps` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3817 | `process_document_async` | `core.tasks.process_document_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3821 | `process_url_async` | `core.tasks.process_url_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3825 | `generate_document_embeddings` | `core.tasks.generate_document_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3849 | `collect_training_data` | `core.tasks.collect_training_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3853 | `collect_training_data_full` | `core.tasks.collect_training_data_full` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4005 | `cleanup_celery_task_events` | `core.tasks.cleanup_celery_task_events` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4018 | `cleanup_llm_call_logs` | `core.tasks.cleanup_llm_call_logs` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4031 | `generate_weekly_opportunity_digest` | `core.tasks.generate_weekly_opportunity_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4035 | `send_proactive_opportunity_alerts` | `core.tasks.send_proactive_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4039 | `send_personalized_opportunity_alerts` | `core.tasks.send_personalized_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4051 | `assemble_chunked_upload` | `core.tasks.assemble_chunked_upload` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4055 | `cleanup_expired_uploads` | `core.tasks.cleanup_expired_uploads` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4097 | `sync_pipeline_insights_to_collective` | `core.tasks.sync_pipeline_insights_to_collective` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4101 | `run_autonomous_intelligence_loop` | `core.tasks.run_autonomous_intelligence_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4134 | `run_daily_intelligence_digest` | `core.tasks.run_daily_intelligence_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4262 | `process_hitl_escalations` | `core.tasks.process_hitl_escalations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4297 | `expire_overdue_validations` | `core.tasks.expire_overdue_validations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4336 | `process_event_bus_scoring_queue` | `core.tasks.process_event_bus_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4370 | `process_event_bus_validation_queue` | `core.tasks.process_event_bus_validation_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4404 | `process_event_bus_analytics_queue` | `core.tasks.process_event_bus_analytics_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4439 | `claim_stale_events` | `core.tasks.claim_stale_events` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4484 | `get_event_bus_stats` | `core.tasks.get_event_bus_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4593 | `unified_pipeline_health_check` | `unified_pipeline.health_check` | yes | — | — | non-standard registered name `unified_pipeline.health_check` — preserve verbatim during move |
| 4602 | `aggregate_roi_metrics_daily` | `core.tasks.aggregate_roi_metrics_daily` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4611 | `generate_weekly_intelligence_brief` | `core.tasks.generate_weekly_intelligence_brief` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4615 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_view` — preserve verbatim during move |
| 4642 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_click` — preserve verbatim during move |
| 4672 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_application` — preserve verbatim during move |
| 4702 | `record_revenue_event` | `roi_metrics.record_revenue` | yes | — | — | non-standard registered name `roi_metrics.record_revenue` — preserve verbatim during move |
| 4751 | `process_trigger_events` | `triggers.process_trigger_events` | yes | — | — | non-standard registered name `triggers.process_trigger_events` — preserve verbatim during move |
| 4895 | `create_default_triggers` | `triggers.create_default_triggers` | yes | — | — | non-standard registered name `triggers.create_default_triggers` — preserve verbatim during move |
| 4939 | `cleanup_old_resolve_jobs` | `core.tasks.cleanup_old_resolve_jobs` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 4985 | `run_design_trends_monitor` | `core.tasks.run_design_trends_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4989 | `run_viral_content_predictor` | `core.tasks.run_viral_content_predictor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4993 | `run_job_match_intelligence` | `core.tasks.run_job_match_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5044 | `run_side_hustle_detector` | `core.tasks.run_side_hustle_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5091 | `run_tech_stack_tracker` | `core.tasks.run_tech_stack_tracker` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5095 | `run_ai_model_monitor` | `core.tasks.run_ai_model_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5099 | `run_case_law_monitor` | `core.tasks.run_case_law_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5103 | `run_regulatory_change_detector` | `core.tasks.run_regulatory_change_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5153 | `run_freelance_opportunity_scout` | `core.tasks.run_freelance_opportunity_scout` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5165 | `run_skill_gap_analyzer` | `core.tasks.run_skill_gap_analyzer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5384 | `run_autonomous_thinking_cycle` | `core.tasks.run_autonomous_thinking_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5388 | `scan_concerns_for_human_action` | `core.tasks.scan_concerns_for_human_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5392 | `batch_extract_artifacts` | `core.tasks.batch_extract_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5435 | `execute_approved_artifacts` | `core.tasks.execute_approved_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5455 | `execute_single_artifact` | `core.tasks.execute_single_artifact` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5605 | `maintain_dream_backlog` | `core.tasks.maintain_dream_backlog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5609 | `refresh_system_state_cache` | `core.tasks.refresh_system_state_cache` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5651 | `auto_triage_dreams` | `core.tasks.auto_triage_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5829 | `monitor_celery_health` | `core.tasks.monitor_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 6625 | `generate_human_attention_items` | `core.tasks.generate_human_attention_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6629 | `process_human_attention_lifecycle` | `core.tasks.process_human_attention_lifecycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6676 | `process_hivemind_sessions` | `core.tasks.process_hivemind_sessions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 6726 | `process_high_scoring_opportunities` | `core.tasks.process_high_scoring_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6972 | `check_celery_health` | `core.tasks.check_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6976 | `execute_orchestration_async` | `core.tasks.execute_orchestration_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7026 | `check_orchestration_timeouts` | `core.tasks.check_orchestration_timeouts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7030 | `check_orchestration_auto_approvals` | `core.tasks.check_orchestration_auto_approvals` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7058 | `execute_approved_dreams_via_orchestration` | `core.tasks.execute_approved_dreams_via_orchestration` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 7107 | `execute_single_dream` | `core.tasks.execute_single_dream` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7222 | `maintain_knowledge_freshness` | `core.tasks.maintain_knowledge_freshness` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7260 | `promote_to_shared_knowledge` | `core.tasks.promote_to_shared_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7462 | `verify_autopilot_action` | `core.tasks.verify_autopilot_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 9147 | `workspace_autopilot_tick` | `workspace.autopilot_tick` | yes | — | — | non-standard registered name `workspace.autopilot_tick` — preserve verbatim during move |
| 9615 | `update_mythology_pattern_statistics` | `core.tasks.update_mythology_pattern_statistics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9942 | `run_system_self_audit` | `core.tasks.run_system_self_audit` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9946 | `discover_and_import_audits` | `core.tasks.discover_and_import_audits` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9962 | `assign_open_findings_to_agents` | `core.tasks.assign_open_findings_to_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9977 | `execute_remediation_tasks` | `core.tasks.execute_remediation_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10016 | `verify_completed_fixes` | `core.tasks.verify_completed_fixes` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10043 | `run_autonomous_remediation_cycle` | `core.tasks.run_autonomous_remediation_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10092 | `assign_and_execute_remediation` | `core.tasks.assign_and_execute_remediation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10478 | `cleanup_resolved_signatures` | `core.tasks.cleanup_resolved_signatures` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10512 | `detect_failure_task` | `core.tasks.detect_failure_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10524 | `run_conceptforge_pipeline` | `core.tasks.run_conceptforge_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10737 | `process_pending_auto_topics` | `process_pending_auto_topics` | yes | — | — | non-standard registered name `process_pending_auto_topics` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10741 | `cleanup_expired_signals` | `cleanup_expired_signals` | yes | yes | — | non-standard registered name `cleanup_expired_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 10923 | `run_daily_priority_scan` | `core.tasks.run_daily_priority_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10954 | `check_operating_rhythm_status` | `core.tasks.check_operating_rhythm_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 10999 | `cleanup_audio_cache` | `core.tasks.cleanup_audio_cache` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 11006 | `auto_archive_stale_deliverables` | `core.tasks.auto_archive_stale_deliverables` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 11013 | `check_orphan_deliverables` | `core.tasks.check_orphan_deliverables` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 11019 | `enforce_db_retention` | `core.tasks.enforce_db_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11202 | `run_all_desks_intelligence` | `core.tasks.run_all_desks_intelligence` | yes | — | `_run_desks_inner` | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>depends on 1 helper(s): _run_desks_inner |
| 11429 | `surface_top_dreams` | `core.tasks.surface_top_dreams` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 11451 | `rescan_active_workspaces` | `core.tasks.rescan_active_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 11569 | `cleanup_expired_pa_insights` | `core.tasks.cleanup_expired_pa_insights` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11599 | `enforce_data_retention` | `core.tasks.enforce_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 12144 | `run_source_pack_workflow` | `core.tasks.run_source_pack_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12158 | `ops_control_loop` | `core.tasks.ops_control_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12162 | `check_llm_cost_spike` | `core.tasks.check_llm_cost_spike` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 12166 | `run_ops_autopilot` | `core.tasks.run_ops_autopilot` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 12186 | `post_ops_digest` | `core.tasks.post_ops_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 12196 | `sync_congress_data` | `core.tasks.sync_congress_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12233 | `execute_code_job` | `core.tasks.execute_code_job` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 12241 | `rag_retrieval_canary` | `core.rag_retrieval_canary` | yes | — | — | non-standard registered name `core.rag_retrieval_canary` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_push_notifications.py` — 1 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 2258 | `send_pending_notifications` | `core.tasks.send_pending_notifications` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_spiders.py` — 19 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 891 | `run_spider_by_category` | `core.tasks.run_spider_by_category` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 895 | `execute_single_spider` | `core.tasks.execute_single_spider` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 899 | `isolate_documents_batch` | `core.tasks.isolate_documents_batch` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 903 | `monitor_isolation_progress` | `core.tasks.monitor_isolation_progress` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 949 | `cleanup_isolation_metadata` | `core.tasks.cleanup_isolation_metadata` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 996 | `collect_spider_data` | `core.tasks.collect_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1002 | `process_spider_data_automatic` | `core.tasks.process_spider_data_automatic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1053 | `process_core_spider_data` | `core.tasks.process_core_spider_data` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 1057 | `run_spider_network` | `core.tasks.run_spider_network` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 1131 | `execute_single_spider_lightweight` | `core.tasks.execute_single_spider_lightweight` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1754 | `score_opportunities_from_spider_data` | `core.tasks.score_opportunities_from_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1878 | `score_spider_data_async` | `core.tasks.score_spider_data_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2822 | `trigger_spider_conversations` | `core.tasks.trigger_spider_conversations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3524 | `recalculate_spider_priorities` | `core.tasks.recalculate_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3596 | `update_project_spider_priorities` | `core.tasks.update_project_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3857 | `cleanup_spider_item_hashes` | `core.tasks.cleanup_spider_item_hashes` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 3896 | `spider_data_retention` | `core.tasks.spider_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6776 | `process_spider_actions` | `core.tasks.process_spider_actions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10729 | `aggregate_spider_signals` | `aggregate_spider_signals` | yes | yes | — | non-standard registered name `aggregate_spider_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |

## Helpers (candidates for `tasks_helpers.py`)

| Line | Name | Used by N task(s) |
| ---: | --- | ---: |
| 3719 | `_analyze_spider_data_for_trends` | 0 |
| 98 | `_apply_task_routing_override` | 0 |
| 10108 | `_assign_and_execute_remediation_DISABLED` | 0 |
| 11974 | `_auto_research_competitor` | 0 |
| 3146 | `_build_image_prompt_from_dream` | 0 |
| 5172 | `_build_operational_context` | 0 |
| 7615 | `_calculate_deliverable_quality` | 1 |
| 6115 | `_calculate_kpi_delta` | 0 |
| 283 | `_circuit_breaker_check` | 0 |
| 364 | `_circuit_breaker_record_timeout` | 0 |
| 357 | `_circuit_breaker_release` | 0 |
| 1481 | `_collect_angellist` | 0 |
| 1301 | `_collect_coingecko` | 0 |
| 1677 | `_collect_crowdfunding` | 0 |
| 1493 | `_collect_design_platform` | 0 |
| 1229 | `_collect_devto` | 0 |
| 1525 | `_collect_education_platform` | 0 |
| 1360 | `_collect_etherscan` | 0 |
| 1423 | `_collect_financial_default` | 0 |
| 1513 | `_collect_freelance_default` | 0 |
| 1203 | `_collect_hackernews` | 0 |
| 1256 | `_collect_hashnode` | 0 |
| 1579 | `_collect_legal_platform` | 0 |
| 1702 | `_collect_news_default` | 0 |
| 1401 | `_collect_opensea` | 0 |
| 1412 | `_collect_premium_financial` | 0 |
| 1134 | `_collect_spider_data_sync` | 0 |
| 1448 | `_collect_weworkremotely` | 0 |
| 1333 | `_collect_yahoo_finance` | 0 |
| 2422 | `_conversation_spawn_allowed` | 0 |
| 2397 | `_conversation_temporal_context` | 0 |
| 4754 | `_create_blockchain_alert_from_trigger` | 0 |
| 3779 | `_create_learning_notification` | 0 |
| 821 | `_create_spider_instance` | 0 |
| 4826 | `_create_stock_alert_from_trigger` | 0 |
| 10708 | `_detect_initiative_content_type` | 0 |
| 3758 | `_detect_research_deltas` | 0 |
| 3235 | `_detect_visual_style` | 0 |
| 5960 | `_evaluate_pilot_outcome` | 0 |
| 2924 | `_execute_content_implementation` | 0 |
| 2985 | `_execute_experiment_implementation` | 0 |
| 2890 | `_execute_feature_implementation` | 0 |
| 7505 | `_execute_gate_repair` | 0 |
| 3016 | `_execute_generic_implementation` | 0 |
| 2954 | `_execute_research_implementation` | 0 |
| 3047 | `_execute_visual_implementation` | 0 |
| 10842 | `_extract_agent_content` | 0 |
| 8300 | `_extract_agent_output_content` | 0 |
| 2664 | `_extract_conversation_knowledge` | 0 |
| 160 | `_extract_discourse_markers` | 0 |
| 6042 | `_extract_experiment_learning` | 0 |
| 2719 | `_extract_hivemind_knowledge` | 0 |
| 126 | `_extract_opener` | 0 |
| 3686 | `_extract_topics_from_project` | 0 |
| 6128 | `_feed_learnings_to_collective_intelligence` | 0 |
| 9856 | `_format_metrics_for_audit` | 0 |
| 5773 | `_gather_experiment_metrics` | 0 |
| 10556 | `_gather_initiative_research` | 0 |
| 9654 | `_gather_live_system_metrics` | 0 |
| 6336 | `_generate_checklist_documentation` | 0 |
| 8913 | `_get_agent_class` | 0 |
| 9027 | `_get_next_task_for_agent` | 0 |
| 168 | `_get_overused_markers` | 0 |
| 3744 | `_get_previous_findings` | 0 |
| 10672 | `_get_previous_stage_context` | 0 |
| 10544 | `_get_stage_document_type` | 0 |
| 7303 | `_get_workspace_for_skin_layer` | 0 |
| 2616 | `_handle_conversation_delegation` | 0 |
| 111 | `_is_media_task_blocked` | 0 |
| 3191 | `_is_visual_dream` | 0 |
| 8861 | `_preflight_check_agent_data` | 0 |
| 2478 | `_preflight_gather_agent_data` | 0 |
| 6248 | `_process_single_gate` | 0 |
| 207 | `_record_timeout_signature` | 0 |
| 7484 | `_route_gate_repair` | 0 |
| 10169 | `_route_spec_to_human_attention_standalone` | 0 |
| 9155 | `_run_agent_group` | 14 |
| 10246 | `_run_agent_remediation_batch_DISABLED` | 0 |
| 8951 | `_run_agent_warmup` | 0 |
| 11647 | `_run_comparison_generation` | 0 |
| 11230 | `_run_desks_inner` | 1 |
| 834 | `_run_spider_adapter` | 0 |
| 6597 | `_send_gate_processing_discord` | 0 |
| 5801 | `_send_halt_discord_notification` | 0 |
| 6215 | `_send_implementation_discord` | 0 |
| 5872 | `_send_kpi_update_discord_notification` | 1 |
| 4524 | `_send_narrative_alerts_to_discord` | 0 |
| 4543 | `_send_narrative_digest_to_discord` | 0 |
| 6179 | `_send_pilot_evaluation_discord` | 0 |
| 6028 | `_simulate_kpi_progress` | 0 |
| 11558 | `_summarize_diff` | 0 |
| 11548 | `_summarize_params` | 0 |
| 277 | `_task_hash` | 0 |
| 9214 | `_track_group_contribution` | 0 |
| 11493 | `_ttl_days` | 0 |
| 11504 | `_upsert_insight` | 0 |
| 177 | `validate_agent_output` | 0 |

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
- `core.tasks.cleanup_boardroom_junk` — ✓ matches a tasks.py task
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
| 1112 | `backfill_signal_scores` | `backfill_signal_scores` |
| 10729 | `aggregate_spider_signals` | `aggregate_spider_signals` |
| 10733 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` |
| 10737 | `process_pending_auto_topics` | `process_pending_auto_topics` |
| 10741 | `cleanup_expired_signals` | `cleanup_expired_signals` |

### Prefixed names (19)

#### `autonomous.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4743 | `run_blockchain_security_monitor` | `autonomous.blockchain_security_monitor` |

#### `autonomous_studio.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4254 | `generate_content_for_channel` | `autonomous_studio.generate_content` |

#### `content_studio.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 9139 | `score_episode_voice` | `content_studio.score_episode_voice` |
| 9143 | `backfill_voice_scores` | `content_studio.backfill_voice_scores` |

#### `core.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 12241 | `rag_retrieval_canary` | `core.rag_retrieval_canary` |
| 12247 | `check_learning_loop_slo` | `core.check_learning_loop_slo` |

#### `learning_loop.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4242 | `track_prediction_outcomes` | `learning_loop.track_prediction_outcomes` |
| 4246 | `calculate_agent_accuracy` | `learning_loop.calculate_agent_accuracy` |

#### `narrative_drift.*` — 3 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4517 | `run_narrative_drift_cycle` | `narrative_drift.run_detector_cycle` |
| 4521 | `update_narrative_statuses` | `narrative_drift.update_narrative_statuses` |
| 4589 | `trigger_content_from_narrative_shift` | `narrative_drift.trigger_content_from_shift` |

#### `roi_metrics.*` — 4 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4615 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` |
| 4642 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` |
| 4672 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` |
| 4702 | `record_revenue_event` | `roi_metrics.record_revenue` |

#### `triggers.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4751 | `process_trigger_events` | `triggers.process_trigger_events` |
| 4895 | `create_default_triggers` | `triggers.create_default_triggers` |

#### `unified_pipeline.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 4593 | `unified_pipeline_health_check` | `unified_pipeline.health_check` |

#### `workspace.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 9147 | `workspace_autopilot_tick` | `workspace.autopilot_tick` |

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
