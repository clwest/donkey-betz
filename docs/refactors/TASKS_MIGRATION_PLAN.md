# Tasks Migration Plan — Phase 0 inventory

**Generated:** 2026-04-29T23:09:15+00:00
**Source:** `core/tasks.py`
**Generator:** `scripts/phase0_tasks_inventory.py`

> Read-only static analysis. No code was modified. The proposed destinations are first-match-wins regex rules in the script — treat them as a starting point, not a final assignment.

## Summary

- **Total tasks:** 178
- **Already name-pinned (`name=`):** 178
- **Unpinned (need Phase 1 edit):** 0
- **Tasks with `bind=True`:** 60
- **Tasks with custom time limits:** 22
- **Tasks referenced in beat schedule:** 12
- **Helpers in tasks.py (private + `validate_agent_output`):** 93
- **Tasks needing review (no rule matched):** 0

## Counts by proposed destination

| Destination | Tasks |
| --- | ---: |
| `tasks_ops.py` | 115 |
| `tasks_spiders.py` | 19 |
| `tasks_body_systems.py` | 13 |
| `tasks_media.py` | 11 |
| `tasks_initiatives.py` | 10 |
| `tasks_conversations.py` | 9 |
| `tasks_push_notifications.py` | 1 |

## Per-destination task lists

### `tasks_body_systems.py` — 13 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 5494 | `run_heartbeat` | `core.tasks.run_heartbeat` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 5498 | `check_breathing` | `core.tasks.check_breathing` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5502 | `daily_cost_forecast` | `core.tasks.daily_cost_forecast` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5506 | `reset_daily_respiratory_stats` | `core.tasks.reset_daily_respiratory_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5538 | `check_circulation` | `core.tasks.check_circulation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 5542 | `check_spine_alignment` | `core.tasks.check_spine_alignment` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5546 | `immune_scan` | `core.tasks.immune_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5550 | `check_digestion` | `core.tasks.check_digestion` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5554 | `check_muscular` | `core.tasks.check_muscular` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5558 | `check_brain` | `core.tasks.check_brain` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5562 | `check_skin` | `core.tasks.check_skin` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5566 | `check_nervous` | `core.tasks.check_nervous` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5570 | `coordinate_body` | `core.tasks.coordinate_body` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_conversations.py` — 9 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 538 | `cleanup_automated_conversation_artifacts` | `core.tasks.cleanup_automated_conversation_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2334 | `run_agent_conversation` | `core.tasks.run_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 2338 | `run_multi_agent_conversation` | `core.tasks.run_multi_agent_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 2381 | `broadcast_conversation_status` | `core.tasks.broadcast_conversation_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2385 | `run_project_conversation` | `core.tasks.run_project_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 8308 | `run_triggered_conversation` | `core.tasks.run_triggered_conversation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 8546 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` | yes | — | — | non-standard registered name `trigger_signal_driven_conversation` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 9059 | `cleanup_conversation_duplicates_task` | `core.tasks.cleanup_conversation_duplicates_task` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 9706 | `summarize_conversation_task` | `core.tasks.summarize_conversation_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs |

### `tasks_initiatives.py` — 10 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 517 | `cleanup_junk_initiatives` | `core.tasks.cleanup_junk_initiatives` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 8354 | `advance_initiative_pipeline` | `core.tasks.advance_initiative_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8518 | `auto_kickstart_stuck_initiatives` | `core.tasks.auto_kickstart_stuck_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8554 | `extract_action_items_from_session` | `core.tasks.extract_action_items_from_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 8598 | `dispatch_pending_action_items` | `core.tasks.dispatch_pending_action_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 8602 | `retry_blocked_research` | `core.tasks.retry_blocked_research` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 8606 | `check_blocked_research_for_unblock` | `core.tasks.check_blocked_research_for_unblock` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 8644 | `process_initiative_auto_progression` | `core.tasks.process_initiative_auto_progression` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 8648 | `detect_duplicate_initiatives` | `core.tasks.detect_duplicate_initiatives` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 8724 | `generate_initiative_stage_document` | `core.tasks.generate_initiative_stage_document` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |

### `tasks_media.py` — 11 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 559 | `create_talking_video_task` | `core.tasks.create_talking_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 1407 | `poll_pending_3d_models` | `core.tasks.poll_pending_3d_models` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3141 | `transcribe_video_task` | `core.tasks.transcribe_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3147 | `generate_video_content_pack_task` | `core.tasks.generate_video_content_pack_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3151 | `ingest_video_task` | `core.tasks.ingest_video_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3155 | `youtube_whisper_task` | `core.tasks.youtube_whisper_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 4027 | `start_resolve_render` | `core.tasks.start_resolve_render` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4032 | `poll_resolve_job_status` | `core.tasks.poll_resolve_job_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4036 | `record_resolve_outcome` | `core.tasks.record_resolve_outcome` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4206 | `run_thumbnail_optimizer` | `core.tasks.run_thumbnail_optimizer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 8350 | `poll_processing_videos` | `core.tasks.poll_processing_videos` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_ops.py` — 115 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 529 | `auto_process_extracted_artifacts` | `core.tasks.auto_process_extracted_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1411 | `record_all_user_style_evolution` | `core.tasks.record_all_user_style_evolution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 1415 | `execute_scheduled_workflow` | `core.tasks.execute_scheduled_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1419 | `sync_workflow_schedules` | `core.tasks.sync_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1430 | `check_workflow_schedules` | `core.tasks.check_workflow_schedules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom retry policy — preserve verbatim |
| 1480 | `execute_pending_opportunity_tasks` | `core.tasks.execute_pending_opportunity_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1484 | `generate_opportunity_report` | `core.tasks.generate_opportunity_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1488 | `train_ml_scoring_model` | `core.tasks.train_ml_scoring_model` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1492 | `evaluate_ml_model_performance` | `core.tasks.evaluate_ml_model_performance` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1496 | `process_realtime_scoring_queue` | `core.tasks.process_realtime_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1500 | `process_batch_scoring_queue` | `core.tasks.process_batch_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1554 | `process_distribution` | `core.tasks.process_distribution` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1738 | `update_distribution_analytics` | `core.tasks.update_distribution_analytics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1742 | `discover_success_patterns` | `core.tasks.discover_success_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1746 | `generate_user_insights` | `core.tasks.generate_user_insights` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1756 | `run_proactive_system_check` | `core.tasks.run_proactive_system_check` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1801 | `check_all_alerts` | `core.tasks.check_all_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1831 | `generate_smart_suggestions` | `core.tasks.generate_smart_suggestions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1874 | `execute_scheduled_automations` | `core.tasks.execute_scheduled_automations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1946 | `validate_knowledge_sources` | `core.tasks.validate_knowledge_sources` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2352 | `propagate_new_policies` | `core.tasks.propagate_new_policies` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2389 | `broadcast_dream_journal` | `core.tasks.broadcast_dream_journal` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2393 | `score_and_promote_dreams` | `core.tasks.score_and_promote_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2397 | `process_approved_dreams` | `core.tasks.process_approved_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2401 | `execute_dream_implementations` | `core.tasks.execute_dream_implementations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 2785 | `explore_dream_topic` | `core.tasks.explore_dream_topic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2789 | `run_hive_mind_session` | `core.tasks.run_hive_mind_session` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2836 | `generate_memory_embedding` | `core.tasks.generate_memory_embedding` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2852 | `sync_project_knowledge` | `core.tasks.sync_project_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2921 | `process_research_feedback` | `core.tasks.process_research_feedback` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3123 | `auto_resolve_knowledge_gaps` | `core.tasks.auto_resolve_knowledge_gaps` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3127 | `process_document_async` | `core.tasks.process_document_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3131 | `process_url_async` | `core.tasks.process_url_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3135 | `generate_document_embeddings` | `core.tasks.generate_document_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3159 | `collect_training_data` | `core.tasks.collect_training_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3163 | `collect_training_data_full` | `core.tasks.collect_training_data_full` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3319 | `generate_weekly_opportunity_digest` | `core.tasks.generate_weekly_opportunity_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3323 | `send_proactive_opportunity_alerts` | `core.tasks.send_proactive_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3327 | `send_personalized_opportunity_alerts` | `core.tasks.send_personalized_opportunity_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3331 | `assemble_chunked_upload` | `core.tasks.assemble_chunked_upload` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3341 | `sync_pipeline_insights_to_collective` | `core.tasks.sync_pipeline_insights_to_collective` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3345 | `run_autonomous_intelligence_loop` | `core.tasks.run_autonomous_intelligence_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3378 | `run_daily_intelligence_digest` | `core.tasks.run_daily_intelligence_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3415 | `process_hitl_escalations` | `core.tasks.process_hitl_escalations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3457 | `process_event_bus_scoring_queue` | `core.tasks.process_event_bus_scoring_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3491 | `process_event_bus_validation_queue` | `core.tasks.process_event_bus_validation_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3525 | `process_event_bus_analytics_queue` | `core.tasks.process_event_bus_analytics_queue` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3560 | `claim_stale_events` | `core.tasks.claim_stale_events` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3605 | `get_event_bus_stats` | `core.tasks.get_event_bus_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3702 | `unified_pipeline_health_check` | `unified_pipeline.health_check` | yes | — | — | non-standard registered name `unified_pipeline.health_check` — preserve verbatim during move |
| 3711 | `aggregate_roi_metrics_daily` | `core.tasks.aggregate_roi_metrics_daily` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3720 | `generate_weekly_intelligence_brief` | `core.tasks.generate_weekly_intelligence_brief` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3724 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_view` — preserve verbatim during move |
| 3751 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_click` — preserve verbatim during move |
| 3781 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_application` — preserve verbatim during move |
| 3811 | `record_revenue_event` | `roi_metrics.record_revenue` | yes | — | — | non-standard registered name `roi_metrics.record_revenue` — preserve verbatim during move |
| 3852 | `process_trigger_events` | `triggers.process_trigger_events` | yes | — | — | non-standard registered name `triggers.process_trigger_events` — preserve verbatim during move |
| 3996 | `create_default_triggers` | `triggers.create_default_triggers` | yes | — | — | non-standard registered name `triggers.create_default_triggers` — preserve verbatim during move |
| 4046 | `run_design_trends_monitor` | `core.tasks.run_design_trends_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4050 | `run_viral_content_predictor` | `core.tasks.run_viral_content_predictor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4054 | `run_job_match_intelligence` | `core.tasks.run_job_match_intelligence` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4105 | `run_side_hustle_detector` | `core.tasks.run_side_hustle_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4148 | `run_tech_stack_tracker` | `core.tasks.run_tech_stack_tracker` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4152 | `run_ai_model_monitor` | `core.tasks.run_ai_model_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4156 | `run_case_law_monitor` | `core.tasks.run_case_law_monitor` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4160 | `run_regulatory_change_detector` | `core.tasks.run_regulatory_change_detector` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4210 | `run_freelance_opportunity_scout` | `core.tasks.run_freelance_opportunity_scout` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4214 | `run_skill_gap_analyzer` | `core.tasks.run_skill_gap_analyzer` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4360 | `run_autonomous_thinking_cycle` | `core.tasks.run_autonomous_thinking_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 4364 | `scan_concerns_for_human_action` | `core.tasks.scan_concerns_for_human_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4368 | `batch_extract_artifacts` | `core.tasks.batch_extract_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4411 | `execute_approved_artifacts` | `core.tasks.execute_approved_artifacts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 4431 | `execute_single_artifact` | `core.tasks.execute_single_artifact` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 4481 | `maintain_dream_backlog` | `core.tasks.maintain_dream_backlog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4485 | `refresh_system_state_cache` | `core.tasks.refresh_system_state_cache` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4527 | `auto_triage_dreams` | `core.tasks.auto_triage_dreams` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4669 | `monitor_celery_health` | `core.tasks.monitor_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 5339 | `generate_human_attention_items` | `core.tasks.generate_human_attention_items` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5343 | `process_human_attention_lifecycle` | `core.tasks.process_human_attention_lifecycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5386 | `process_hivemind_sessions` | `core.tasks.process_hivemind_sessions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 5436 | `process_high_scoring_opportunities` | `core.tasks.process_high_scoring_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5578 | `check_celery_health` | `core.tasks.check_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 5582 | `execute_orchestration_async` | `core.tasks.execute_orchestration_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5632 | `check_orchestration_timeouts` | `core.tasks.check_orchestration_timeouts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5636 | `check_orchestration_auto_approvals` | `core.tasks.check_orchestration_auto_approvals` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5664 | `execute_approved_dreams_via_orchestration` | `core.tasks.execute_approved_dreams_via_orchestration` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 5713 | `execute_single_dream` | `core.tasks.execute_single_dream` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5765 | `maintain_knowledge_freshness` | `core.tasks.maintain_knowledge_freshness` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5803 | `promote_to_shared_knowledge` | `core.tasks.promote_to_shared_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5915 | `verify_autopilot_action` | `core.tasks.verify_autopilot_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 7436 | `workspace_autopilot_tick` | `workspace.autopilot_tick` | yes | — | — | non-standard registered name `workspace.autopilot_tick` — preserve verbatim during move |
| 7483 | `update_mythology_pattern_statistics` | `core.tasks.update_mythology_pattern_statistics` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7806 | `run_system_self_audit` | `core.tasks.run_system_self_audit` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7810 | `discover_and_import_audits` | `core.tasks.discover_and_import_audits` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7826 | `assign_open_findings_to_agents` | `core.tasks.assign_open_findings_to_agents` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7841 | `execute_remediation_tasks` | `core.tasks.execute_remediation_tasks` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7880 | `verify_completed_fixes` | `core.tasks.verify_completed_fixes` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7907 | `run_autonomous_remediation_cycle` | `core.tasks.run_autonomous_remediation_cycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7956 | `assign_and_execute_remediation` | `core.tasks.assign_and_execute_remediation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8325 | `detect_failure_task` | `core.tasks.detect_failure_task` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8337 | `run_conceptforge_pipeline` | `core.tasks.run_conceptforge_pipeline` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 8550 | `process_pending_auto_topics` | `process_pending_auto_topics` | yes | — | — | non-standard registered name `process_pending_auto_topics` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 8728 | `run_daily_priority_scan` | `core.tasks.run_daily_priority_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8759 | `check_operating_rhythm_status` | `core.tasks.check_operating_rhythm_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 8828 | `run_all_desks_intelligence` | `core.tasks.run_all_desks_intelligence` | yes | — | `_run_desks_inner` | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>depends on 1 helper(s): _run_desks_inner |
| 9055 | `surface_top_dreams` | `core.tasks.surface_top_dreams` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 9077 | `rescan_active_workspaces` | `core.tasks.rescan_active_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9702 | `run_source_pack_workflow` | `core.tasks.run_source_pack_workflow` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 9716 | `ops_control_loop` | `core.tasks.ops_control_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 9720 | `check_llm_cost_spike` | `core.tasks.check_llm_cost_spike` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 9724 | `run_ops_autopilot` | `core.tasks.run_ops_autopilot` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 9744 | `post_ops_digest` | `core.tasks.post_ops_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 9754 | `sync_congress_data` | `core.tasks.sync_congress_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 9791 | `execute_code_job` | `core.tasks.execute_code_job` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 9799 | `rag_retrieval_canary` | `core.rag_retrieval_canary` | yes | — | — | non-standard registered name `core.rag_retrieval_canary` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_push_notifications.py` — 1 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 1893 | `send_pending_notifications` | `core.tasks.send_pending_notifications` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_spiders.py` — 19 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 637 | `run_spider_by_category` | `core.tasks.run_spider_by_category` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 641 | `execute_single_spider` | `core.tasks.execute_single_spider` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 645 | `isolate_documents_batch` | `core.tasks.isolate_documents_batch` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 649 | `monitor_isolation_progress` | `core.tasks.monitor_isolation_progress` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 695 | `cleanup_isolation_metadata` | `core.tasks.cleanup_isolation_metadata` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 742 | `collect_spider_data` | `core.tasks.collect_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 748 | `process_spider_data_automatic` | `core.tasks.process_spider_data_automatic` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 799 | `process_core_spider_data` | `core.tasks.process_core_spider_data` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 803 | `run_spider_network` | `core.tasks.run_spider_network` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 811 | `execute_single_spider_lightweight` | `core.tasks.execute_single_spider_lightweight` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1434 | `score_opportunities_from_spider_data` | `core.tasks.score_opportunities_from_spider_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 1550 | `score_spider_data_async` | `core.tasks.score_spider_data_async` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2348 | `trigger_spider_conversations` | `core.tasks.trigger_spider_conversations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2885 | `recalculate_spider_priorities` | `core.tasks.recalculate_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 2957 | `update_project_spider_priorities` | `core.tasks.update_project_spider_priorities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3167 | `cleanup_spider_item_hashes` | `core.tasks.cleanup_spider_item_hashes` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 3206 | `spider_data_retention` | `core.tasks.spider_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 5486 | `process_spider_actions` | `core.tasks.process_spider_actions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 8542 | `aggregate_spider_signals` | `aggregate_spider_signals` | yes | yes | — | non-standard registered name `aggregate_spider_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |

## Helpers (candidates for `tasks_helpers.py`)

| Line | Name | Used by N task(s) |
| ---: | --- | ---: |
| 3029 | `_analyze_spider_data_for_trends` | 0 |
| 196 | `_apply_task_routing_override` | 0 |
| 7972 | `_assign_and_execute_remediation_DISABLED` | 0 |
| 9538 | `_auto_research_competitor` | 0 |
| 2660 | `_build_image_prompt_from_dream` | 0 |
| 4217 | `_build_operational_context` | 0 |
| 4837 | `_calculate_kpi_delta` | 0 |
| 381 | `_circuit_breaker_check` | 0 |
| 462 | `_circuit_breaker_record_timeout` | 0 |
| 455 | `_circuit_breaker_release` | 0 |
| 1161 | `_collect_angellist` | 0 |
| 981 | `_collect_coingecko` | 0 |
| 1357 | `_collect_crowdfunding` | 0 |
| 1173 | `_collect_design_platform` | 0 |
| 909 | `_collect_devto` | 0 |
| 1205 | `_collect_education_platform` | 0 |
| 1040 | `_collect_etherscan` | 0 |
| 1103 | `_collect_financial_default` | 0 |
| 1193 | `_collect_freelance_default` | 0 |
| 883 | `_collect_hackernews` | 0 |
| 936 | `_collect_hashnode` | 0 |
| 1259 | `_collect_legal_platform` | 0 |
| 1382 | `_collect_news_default` | 0 |
| 1081 | `_collect_opensea` | 0 |
| 1092 | `_collect_premium_financial` | 0 |
| 814 | `_collect_spider_data_sync` | 0 |
| 1128 | `_collect_weworkremotely` | 0 |
| 1013 | `_collect_yahoo_finance` | 0 |
| 1974 | `_conversation_spawn_allowed` | 0 |
| 1949 | `_conversation_temporal_context` | 0 |
| 3855 | `_create_blockchain_alert_from_trigger` | 0 |
| 3089 | `_create_learning_notification` | 0 |
| 567 | `_create_spider_instance` | 0 |
| 3927 | `_create_stock_alert_from_trigger` | 0 |
| 8521 | `_detect_initiative_content_type` | 0 |
| 3068 | `_detect_research_deltas` | 0 |
| 2749 | `_detect_visual_style` | 0 |
| 4682 | `_evaluate_pilot_outcome` | 0 |
| 2438 | `_execute_content_implementation` | 0 |
| 2499 | `_execute_experiment_implementation` | 0 |
| 2404 | `_execute_feature_implementation` | 0 |
| 5954 | `_execute_gate_repair` | 0 |
| 2530 | `_execute_generic_implementation` | 0 |
| 2468 | `_execute_research_implementation` | 0 |
| 2561 | `_execute_visual_implementation` | 0 |
| 8651 | `_extract_agent_content` | 0 |
| 6660 | `_extract_agent_output_content` | 0 |
| 2216 | `_extract_conversation_knowledge` | 0 |
| 258 | `_extract_discourse_markers` | 0 |
| 4764 | `_extract_experiment_learning` | 0 |
| 2271 | `_extract_hivemind_knowledge` | 0 |
| 224 | `_extract_opener` | 0 |
| 2996 | `_extract_topics_from_project` | 0 |
| 4850 | `_feed_learnings_to_collective_intelligence` | 0 |
| 7724 | `_format_metrics_for_audit` | 0 |
| 4613 | `_gather_experiment_metrics` | 0 |
| 8369 | `_gather_initiative_research` | 0 |
| 7522 | `_gather_live_system_metrics` | 0 |
| 5050 | `_generate_checklist_documentation` | 0 |
| 7263 | `_get_agent_class` | 0 |
| 7377 | `_get_next_task_for_agent` | 0 |
| 266 | `_get_overused_markers` | 0 |
| 3054 | `_get_previous_findings` | 0 |
| 8485 | `_get_previous_stage_context` | 0 |
| 8357 | `_get_stage_document_type` | 0 |
| 5846 | `_get_workspace_for_skin_layer` | 0 |
| 2168 | `_handle_conversation_delegation` | 0 |
| 209 | `_is_media_task_blocked` | 0 |
| 2705 | `_is_visual_dream` | 0 |
| 7221 | `_preflight_check_agent_data` | 0 |
| 2030 | `_preflight_gather_agent_data` | 0 |
| 4962 | `_process_single_gate` | 0 |
| 305 | `_record_timeout_signature` | 0 |
| 5933 | `_route_gate_repair` | 0 |
| 8033 | `_route_spec_to_human_attention_standalone` | 0 |
| 8091 | `_run_agent_remediation_batch_DISABLED` | 0 |
| 7301 | `_run_agent_warmup` | 0 |
| 9211 | `_run_comparison_generation` | 0 |
| 8856 | `_run_desks_inner` | 1 |
| 580 | `_run_spider_adapter` | 0 |
| 5311 | `_send_gate_processing_discord` | 0 |
| 4641 | `_send_halt_discord_notification` | 0 |
| 4933 | `_send_implementation_discord` | 0 |
| 3637 | `_send_narrative_alerts_to_discord` | 0 |
| 3656 | `_send_narrative_digest_to_discord` | 0 |
| 4901 | `_send_pilot_evaluation_discord` | 0 |
| 4750 | `_simulate_kpi_progress` | 0 |
| 9180 | `_summarize_diff` | 0 |
| 9170 | `_summarize_params` | 0 |
| 375 | `_task_hash` | 0 |
| 9115 | `_ttl_days` | 0 |
| 9126 | `_upsert_insight` | 0 |
| 275 | `validate_agent_output` | 0 |

## Beat-schedule references found in `core/celery.py`

Static grep over `core/celery.py` for `'task': '<name>'` literals. PeriodicTask DB rows are not enumerated here (static analysis only).

- `aggregate_spider_signals` — ✓ matches a tasks.py task
- `ai_core.tasks.clean_stale_data` — ?  not from tasks.py (sibling file or external)
- `ai_core.tasks.collect_real_opportunities` — ?  not from tasks.py (sibling file or external)
- `ai_core.tasks.warm_up_spider_network` — ?  not from tasks.py (sibling file or external)
- `cleanup_expired_signals` — ?  not from tasks.py (sibling file or external)
- `core.tasks.auto_archive_stale_deliverables` — ?  not from tasks.py (sibling file or external)
- `core.tasks.backfill_spider_embeddings` — ?  not from tasks.py (sibling file or external)
- `core.tasks.check_celery_health` — ✓ matches a tasks.py task
- `core.tasks.cleanup_audio_cache` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_boardroom_junk` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_celery_task_events` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_conversation_duplicates_task` — ✓ matches a tasks.py task
- `core.tasks.cleanup_expired_pa_insights` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_expired_uploads` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_junk_initiatives` — ✓ matches a tasks.py task
- `core.tasks.cleanup_learning_readback_events` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_llm_call_logs` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_old_notifications` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_old_resolve_jobs` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_resolved_signatures` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_spider_item_hashes` — ✓ matches a tasks.py task
- `core.tasks.cleanup_stale_agent_executions` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_stale_content` — ?  not from tasks.py (sibling file or external)
- `core.tasks.cleanup_stale_dreams` — ?  not from tasks.py (sibling file or external)
- `core.tasks.decay_learning_patterns` — ?  not from tasks.py (sibling file or external)
- `core.tasks.enforce_data_retention` — ?  not from tasks.py (sibling file or external)
- `core.tasks.enforce_db_retention` — ?  not from tasks.py (sibling file or external)
- `core.tasks.generate_operator_edge_newsletter` — ?  not from tasks.py (sibling file or external)
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

**12 task(s) already carry a non-standard registered name** (no `core.tasks.` prefix). Phase 1 skips them — they're already pinned. **Phase 3 (module moves) MUST preserve every existing `name=` value verbatim**; see the Phase 3 warning section below for the full list grouped by prefix.

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

**12 task(s) carry non-standard registered names** that don't follow the `core.tasks.<func>` convention. Every one of these names is a runtime contract: it appears in beat schedules, `PeriodicTask` rows, `send_task()` callers, or code that hasn't been audited. **During module moves (Phase 3+), preserve each `name=` kwarg verbatim** — do not "normalize" them, do not drop the existing prefix, do not rewrite to match the destination module's path.

### Bare names (3) — highest collision risk

These tasks register with no prefix at all, so their registered name lives in Celery's global namespace and can collide with names from any other module. Treat each move as a security-sensitive change.

| Line | Function | Registered name |
| ---: | --- | --- |
| 8542 | `aggregate_spider_signals` | `aggregate_spider_signals` |
| 8546 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` |
| 8550 | `process_pending_auto_topics` | `process_pending_auto_topics` |

### Prefixed names (9)

#### `core.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 9799 | `rag_retrieval_canary` | `core.rag_retrieval_canary` |

#### `roi_metrics.*` — 4 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 3724 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` |
| 3751 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` |
| 3781 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` |
| 3811 | `record_revenue_event` | `roi_metrics.record_revenue` |

#### `triggers.*` — 2 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 3852 | `process_trigger_events` | `triggers.process_trigger_events` |
| 3996 | `create_default_triggers` | `triggers.create_default_triggers` |

#### `unified_pipeline.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 3702 | `unified_pipeline_health_check` | `unified_pipeline.health_check` |

#### `workspace.*` — 1 task(s)

| Line | Function | Registered name |
| ---: | --- | --- |
| 7436 | `workspace_autopilot_tick` | `workspace.autopilot_tick` |

**Reviewer checklist for each Phase 3 module move:** before approving, grep the moved task's `name=` value against the current `core/tasks.py` and confirm character-for-character match. Any normalization, prefix change, or rename — even well-intentioned — silently breaks every existing caller.

## Pre-existing dead task-string references (rename-drift sweep)

**22 string-based task reference(s) across 2 file(s) point at task names that don't resolve to any registered task in `core/tasks.py`.** These are pre-existing rename-drift bugs — calls / lookups that would already fail today if invoked. Phase 1 does not introduce them, does not depend on them, and does not fix them. **Treat as a separate follow-up sweep, not a blocker for Phase 1.**

### `core/services/celery_health.py` — 3 dead reference(s)

| Line | Referenced task name |
| ---: | --- |
| 69 | `core.tasks.check_heart` |
| 70 | `core.tasks.check_circulatory` |
| 72 | `core.tasks.check_content_diversity` |

### `core/views_autonomous_dashboard.py` — 19 dead reference(s)

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
| 153 | `autonomous.blockchain_security_monitor` |
| 161 | `core.tasks.run_stock_market_intelligence` |
| 171 | `core.tasks.run_tech_stack_analysis` |
| 179 | `core.tasks.run_ai_model_monitoring` |
| 187 | `core.tasks.run_skill_gap_analysis` |
| 197 | `core.tasks.run_case_law_monitoring` |
| 205 | `core.tasks.run_regulatory_monitoring` |

**Suggested follow-up:** open a separate issue for the rename-drift sweep. For each dead reference, either rename the call site to match the actual registered task name, or delete the dead caller entirely if the feature is no longer wired up. This sweep should land independently of the Wave B tasks refactor.

---

_Regenerate this plan after any change to `core/tasks.py` or the domain rules in `scripts/phase0_tasks_inventory.py`._
