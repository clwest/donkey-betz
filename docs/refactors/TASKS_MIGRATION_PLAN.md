# Tasks Migration Plan — Phase 0 inventory

**Generated:** 2026-04-29T05:09:51+00:00
**Source:** `core/tasks.py`
**Generator:** `scripts/phase0_tasks_inventory.py`

> Read-only static analysis. No code was modified. The proposed destinations are first-match-wins regex rules in the script — treat them as a starting point, not a final assignment.

## Summary

- **Total tasks:** 356
- **Already name-pinned (`name=`):** 93
- **Unpinned (need Phase 1 edit):** 263
- **Tasks with `bind=True`:** 104
- **Tasks with custom time limits:** 49
- **Tasks referenced in beat schedule:** 35
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
| `tasks_diagnostics.py` | 8 |
| `tasks_backfill.py` | 7 |
| `tasks_experiments.py` | 7 |
| `tasks_push_notifications.py` | 1 |

## Per-destination task lists

### `tasks_agents.py` — 45 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 401 | `cleanup_stale_agent_executions` | `core.tasks.cleanup_stale_agent_executions` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 751 | `run_autonomy_cycle` | `core.tasks.run_autonomy_cycle` | no | — | — | — |
| 888 | `execute_agent_task` | `core.tasks.execute_agent_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 906 | `execute_initiative_stage_task` | `core.tasks.execute_initiative_stage_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 2480 | `agent_think_and_synthesize` | `core.tasks.agent_think_and_synthesize` | no | — | — | — |
| 2500 | `embed_agent_activity` | `core.tasks.embed_agent_activity` | no | — | — | — |
| 2973 | `generate_agent_dreams` | `core.tasks.generate_agent_dreams` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3472 | `update_agent_mood` | `core.tasks.update_agent_mood` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3478 | `check_mood_expirations` | `core.tasks.check_mood_expirations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3482 | `apply_mood_trigger_rules` | `core.tasks.apply_mood_trigger_rules` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3486 | `evolve_agent_relationships` | `core.tasks.evolve_agent_relationships` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3534 | `update_alliance_strengths` | `core.tasks.update_alliance_strengths` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3548 | `broadcast_relationship_status` | `core.tasks.broadcast_relationship_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3552 | `process_agent_activity_xp` | `core.tasks.process_agent_activity_xp` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3556 | `check_level_milestones` | `core.tasks.check_level_milestones` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 3593 | `broadcast_evolution_status` | `core.tasks.broadcast_evolution_status` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 4350 | `calculate_agent_accuracy` | `learning_loop.calculate_agent_accuracy` | yes | — | — | non-standard registered name `learning_loop.calculate_agent_accuracy` — preserve verbatim during move |
| 6966 | `run_market_monitoring_agents` | `core.tasks.run_market_monitoring_agents` | no | — | — | — |
| 7062 | `run_business_strategy_agents` | `core.tasks.run_business_strategy_agents` | no | — | — | — |
| 7066 | `exercise_all_dormant_agents` | `core.tasks.exercise_all_dormant_agents` | no | — | — | — |
| 7470 | `agent_workspace_status_report` | `core.tasks.agent_workspace_status_report` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7474 | `agent_research_to_workspace` | `core.tasks.agent_research_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7478 | `agent_content_to_workspace` | `core.tasks.agent_content_to_workspace` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7764 | `aggregate_tool_call_stats` | `core.tasks.aggregate_tool_call_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7768 | `agent_daily_summary` | `core.tasks.agent_daily_summary` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9006 | `universal_agent_workspace_output` | `core.tasks.universal_agent_workspace_output` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 9182 | `agent_category_rotation` | `core.tasks.agent_category_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9190 | `full_agent_rotation` | `core.tasks.full_agent_rotation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 9395 | `run_strategy_marketing_agents` | `core.tasks.run_strategy_marketing_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9421 | `run_research_analysis_agents` | `core.tasks.run_research_analysis_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9513 | `run_development_tech_agents` | `core.tasks.run_development_tech_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9542 | `run_executive_leadership_agents` | `core.tasks.run_executive_leadership_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9573 | `run_podcast_debate_agents` | `core.tasks.run_podcast_debate_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9619 | `run_campaign_series_agents` | `core.tasks.run_campaign_series_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9638 | `run_system_orchestration_agents` | `core.tasks.run_system_orchestration_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9673 | `run_quality_audit_agents` | `core.tasks.run_quality_audit_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9692 | `run_specialty_agents` | `core.tasks.run_specialty_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 10044 | `run_agent_health_rotation` | `core.tasks.run_agent_health_rotation` | no | — | — | — |
| 10332 | `run_agent_remediation_batch` | `core.tasks.run_agent_remediation_batch` | no | — | — | — |
| 11171 | `claude_code_engineer_task` | `core.tasks.claude_code_engineer_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11178 | `claude_code_agent_respond` | `core.tasks.claude_code_agent_respond` | no | — | — | custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11185 | `process_pa_chat_task` | `core.tasks.process_pa_chat_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 11193 | `rebuild_pa_context_task` | `core.tasks.rebuild_pa_context_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11307 | `process_pa_tts_task` | `core.tasks.process_pa_tts_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 11635 | `analyze_pa_tool_patterns` | `core.tasks.analyze_pa_tool_patterns` | no | — | — | ignore_result=True — result-backend interaction differs |

### `tasks_backfill.py` — 7 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 1168 | `backfill_spider_embeddings` | `core.tasks.backfill_spider_embeddings` | no | yes | — | ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 1219 | `backfill_signal_scores` | `backfill_signal_scores` | yes | — | — | non-standard registered name `backfill_signal_scores` — preserve verbatim during move |
| 3432 | `backfill_memory_embeddings` | `core.tasks.backfill_memory_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3468 | `backfill_conversation_embeddings` | `core.tasks.backfill_conversation_embeddings` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 9245 | `backfill_voice_scores` | `content_studio.backfill_voice_scores` | yes | — | — | non-standard registered name `content_studio.backfill_voice_scores` — preserve verbatim during move |
| 11064 | `backfill_stage_documents` | `core.tasks.backfill_stage_documents` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 12451 | `backfill_deliverable_workspaces` | `core.tasks.backfill_deliverable_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |

### `tasks_boardroom.py` — 15 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 506 | `cleanup_boardroom_junk` | `core.tasks.cleanup_boardroom_junk` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 510 | `auto_approve_boardroom_items` | `core.tasks.auto_approve_boardroom_items` | no | — | — | — |
| 524 | `cleanup_expired_boardroom_items` | `core.tasks.cleanup_expired_boardroom_items` | no | — | — | — |
| 2896 | `auto_promote_decisions` | `core.tasks.auto_promote_decisions` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5763 | `auto_approve_low_risk_gates` | `core.tasks.auto_approve_low_risk_gates` | no | — | — | — |
| 5771 | `auto_promote_low_risk_decisions` | `core.tasks.auto_promote_low_risk_decisions` | no | — | — | — |
| 5775 | `report_pending_review_metrics` | `core.tasks.report_pending_review_metrics` | no | — | — | — |
| 5779 | `ai_promote_decisions` | `core.tasks.ai_promote_decisions` | no | — | — | ignore_result=True — result-backend interaction differs |
| 5783 | `auto_complete_pilots` | `core.tasks.auto_complete_pilots` | no | — | — | — |
| 5787 | `evaluate_pilots_with_thinking_agent` | `core.tasks.evaluate_pilots_with_thinking_agent` | no | — | — | — |
| 6059 | `evaluate_and_complete_pilots` | `core.tasks.evaluate_and_complete_pilots` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6314 | `execute_pilot_implementations` | `core.tasks.execute_pilot_implementations` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6347 | `process_gates_and_deploy_pilots` | `core.tasks.process_gates_and_deploy_pilots` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 6774 | `enrich_boardroom_ml_predictions` | `core.tasks.enrich_boardroom_ml_predictions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 7259 | `process_gate_progression` | `core.tasks.process_gate_progression` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_body_systems.py` — 13 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 6886 | `run_heartbeat` | `core.tasks.run_heartbeat` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6890 | `check_breathing` | `core.tasks.check_breathing` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6894 | `daily_cost_forecast` | `core.tasks.daily_cost_forecast` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6898 | `reset_daily_respiratory_stats` | `core.tasks.reset_daily_respiratory_stats` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6930 | `check_circulation` | `core.tasks.check_circulation` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 6934 | `check_spine_alignment` | `core.tasks.check_spine_alignment` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6938 | `immune_scan` | `core.tasks.immune_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6942 | `check_digestion` | `core.tasks.check_digestion` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6946 | `check_muscular` | `core.tasks.check_muscular` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6950 | `check_brain` | `core.tasks.check_brain` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6954 | `check_skin` | `core.tasks.check_skin` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6958 | `check_nervous` | `core.tasks.check_nervous` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6962 | `coordinate_body` | `core.tasks.coordinate_body` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |

### `tasks_content.py` — 38 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 405 | `cleanup_stale_content` | `core.tasks.cleanup_stale_content` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 514 | `execute_workspace_pipeline` | `core.tasks.execute_workspace_pipeline` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 519 | `execute_demo_pipeline_task` | `core.tasks.execute_demo_pipeline_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 917 | `produce_content_package` | `core.tasks.produce_content_package` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 2932 | `trigger_project_research` | `core.tasks.trigger_project_research` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 4147 | `generate_content_package` | `core.tasks.generate_content_package` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4151 | `generate_ai_series` | `core.tasks.generate_ai_series` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4354 | `run_autonomous_content_studio` | `core.tasks.run_autonomous_content_studio` | no | — | — | — |
| 4358 | `generate_content_for_channel` | `autonomous_studio.generate_content` | yes | — | — | non-standard registered name `autonomous_studio.generate_content` — preserve verbatim during move<br>custom time limits — production timing-critical; do not alter on move |
| 4362 | `track_content_performance` | `core.tasks.track_content_performance` | no | — | — | — |
| 4621 | `run_narrative_drift_cycle` | `narrative_drift.run_detector_cycle` | yes | — | — | non-standard registered name `narrative_drift.run_detector_cycle` — preserve verbatim during move |
| 4625 | `update_narrative_statuses` | `narrative_drift.update_narrative_statuses` | yes | — | — | non-standard registered name `narrative_drift.update_narrative_statuses` — preserve verbatim during move |
| 4693 | `trigger_content_from_narrative_shift` | `narrative_drift.trigger_content_from_shift` | yes | — | — | non-standard registered name `narrative_drift.trigger_content_from_shift` — preserve verbatim during move |
| 5271 | `generate_podcast_episode` | `core.tasks.generate_podcast_episode` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5409 | `generate_self_blog_task` | `core.tasks.generate_self_blog_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5413 | `draft_legal_document_task` | `core.tasks.draft_legal_document_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5446 | `generate_blog_with_topic_task` | `core.tasks.generate_blog_with_topic_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5473 | `generate_self_blog_deliberation_task` | `core.tasks.generate_self_blog_deliberation_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 5479 | `generate_operator_edge_newsletter` | `core.tasks.generate_operator_edge_newsletter` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 5605 | `generate_weekly_synthesis` | `core.tasks.generate_weekly_synthesis` | no | — | — | — |
| 5609 | `generate_pending_reviews` | `core.tasks.generate_pending_reviews` | no | — | — | custom time limits — production timing-critical; do not alter on move |
| 5868 | `generate_checklist_content_async` | `core.tasks.generate_checklist_content_async` | no | — | — | — |
| 7070 | `check_content_diversity` | `core.tasks.check_content_diversity` | no | — | — | — |
| 7269 | `process_content_ideas` | `core.tasks.process_content_ideas` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 7482 | `enhance_blog_task` | `core.tasks.enhance_blog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7486 | `evaluate_unscored_blogs` | `core.tasks.evaluate_unscored_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7534 | `reevaluate_enhanced_blogs` | `core.tasks.reevaluate_enhanced_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7538 | `auto_publish_approved_blogs` | `core.tasks.auto_publish_approved_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7583 | `content_autonomy_loop` | `core.tasks.content_autonomy_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 7679 | `auto_enhance_blogs` | `core.tasks.auto_enhance_blogs` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7683 | `score_unscored_deliverables` | `core.tasks.score_unscored_deliverables` | yes | — | `_calculate_deliverable_quality` | name= already pinned (no Phase 1 edit needed for this task)<br>depends on 1 helper(s): _calculate_deliverable_quality |
| 9241 | `score_episode_voice` | `content_studio.score_episode_voice` | yes | — | — | non-standard registered name `content_studio.score_episode_voice` — preserve verbatim during move |
| 9355 | `run_content_creation_agents` | `core.tasks.run_content_creation_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9488 | `run_narrative_culture_agents` | `core.tasks.run_narrative_culture_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9594 | `auto_generate_podcast_episode` | `core.tasks.auto_generate_podcast_episode` | no | — | — | — |
| 9598 | `run_content_studio_agents` | `core.tasks.run_content_studio_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 11343 | `generate_step_content` | `core.tasks.generate_step_content` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 12283 | `generate_competitor_comparison_task` | `core.tasks.generate_competitor_comparison_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |

### `tasks_conversations.py` — 9 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 537 | `cleanup_automated_conversation_artifacts` | `core.tasks.cleanup_automated_conversation_artifacts` | no | — | — | — |
| 2888 | `run_agent_conversation` | `core.tasks.run_agent_conversation` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 2892 | `run_multi_agent_conversation` | `core.tasks.run_multi_agent_conversation` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 2965 | `broadcast_conversation_status` | `core.tasks.broadcast_conversation_status` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2969 | `run_project_conversation` | `core.tasks.run_project_conversation` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10569 | `run_triggered_conversation` | `core.tasks.run_triggered_conversation` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 10879 | `trigger_signal_driven_conversation` | `trigger_signal_driven_conversation` | yes | — | — | non-standard registered name `trigger_signal_driven_conversation` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 11578 | `cleanup_conversation_duplicates_task` | `core.tasks.cleanup_conversation_duplicates_task` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 12293 | `summarize_conversation_task` | `core.tasks.summarize_conversation_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>ignore_result=True — result-backend interaction differs |

### `tasks_diagnostics.py` — 8 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 755 | `run_cto_daily_diagnostic` | `core.tasks.run_cto_daily_diagnostic` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 767 | `post_cto_daily_diagnostic` | `core.tasks.post_cto_daily_diagnostic` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 801 | `run_coo_daily_diagnostic` | `core.tasks.run_coo_daily_diagnostic` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 820 | `post_coo_daily_diagnostic` | `core.tasks.post_coo_daily_diagnostic` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 848 | `run_trend_daily_diagnostic` | `core.tasks.run_trend_daily_diagnostic` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>referenced by beat schedule — name pin is non-optional |
| 862 | `post_trend_daily_diagnostic` | `core.tasks.post_trend_daily_diagnostic` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 10040 | `run_metrics_action_check` | `core.tasks.run_metrics_action_check` | no | — | — | — |
| 10582 | `run_diagnostic_pipeline_task` | `core.tasks.run_diagnostic_pipeline_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |

### `tasks_experiments.py` — 7 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 546 | `cleanup_halted_experiments` | `core.tasks.cleanup_halted_experiments` | no | — | — | — |
| 552 | `cleanup_stale_running_experiments` | `core.tasks.cleanup_stale_running_experiments` | no | — | — | — |
| 663 | `reconcile_experiment_status_outcome` | `core.tasks.reconcile_experiment_status_outcome` | no | — | — | — |
| 5872 | `monitor_running_experiments` | `core.tasks.monitor_running_experiments` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 5935 | `update_experiment_kpis` | `core.tasks.update_experiment_kpis` | no | — | `_send_kpi_update_discord_notification` | depends on 1 helper(s): _send_kpi_update_discord_notification |
| 6007 | `check_kpi_alerts` | `core.tasks.check_kpi_alerts` | no | — | — | — |
| 6055 | `send_weekly_kpi_summary` | `core.tasks.send_weekly_kpi_summary` | no | — | — | — |

### `tasks_financial.py` — 25 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 4271 | `check_sec_filings_alert` | `core.tasks.check_sec_filings_alert` | no | — | — | — |
| 4301 | `run_stock_audit_cycle` | `core.tasks.run_stock_audit_cycle` | no | — | — | — |
| 4338 | `run_market_intelligence_desk` | `core.tasks.run_market_intelligence_desk` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4342 | `check_market_events_and_rerun` | `core.tasks.check_market_events_and_rerun` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 4346 | `track_prediction_outcomes` | `learning_loop.track_prediction_outcomes` | yes | — | — | non-standard registered name `learning_loop.track_prediction_outcomes` — preserve verbatim during move |
| 4845 | `run_blockchain_security_monitor` | `autonomous.blockchain_security_monitor` | yes | — | — | non-standard registered name `autonomous.blockchain_security_monitor` — preserve verbatim during move |
| 4849 | `run_stock_market_intelligence` | `core.tasks.run_stock_market_intelligence` | no | — | — | — |
| 5189 | `run_crypto_sentiment_monitor` | `core.tasks.run_crypto_sentiment_monitor` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5259 | `run_sec_filing_analyzer` | `core.tasks.run_sec_filing_analyzer` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5263 | `run_earnings_predictor` | `core.tasks.run_earnings_predictor` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5613 | `collect_kalshi_prediction_markets` | `core.tasks.collect_kalshi_prediction_markets` | no | — | — | — |
| 5617 | `collect_kalshi_market_intelligence` | `core.tasks.collect_kalshi_market_intelligence` | no | — | — | — |
| 5621 | `collect_sports_odds` | `core.tasks.collect_sports_odds` | no | — | — | — |
| 5625 | `collect_sports_odds_intelligence` | `core.tasks.collect_sports_odds_intelligence` | no | — | — | — |
| 5629 | `daily_betting_digest` | `core.tasks.daily_betting_digest` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5633 | `market_intelligence_scan` | `core.tasks.market_intelligence_scan` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5637 | `market_movement_alerts` | `core.tasks.market_movement_alerts` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5641 | `snapshot_odds_for_line_movement` | `core.tasks.snapshot_odds_for_line_movement` | no | — | — | ignore_result=True — result-backend interaction differs |
| 5645 | `scan_arbs_and_notify` | `core.tasks.scan_arbs_and_notify` | no | — | — | — |
| 5649 | `verify_betting_outcomes` | `core.tasks.verify_betting_outcomes` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5699 | `generate_daily_betting_brief` | `core.tasks.generate_daily_betting_brief` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5703 | `evaluate_ml_predictions` | `core.tasks.evaluate_ml_predictions` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 7015 | `run_blockchain_monitoring_agents` | `core.tasks.run_blockchain_monitoring_agents` | no | — | — | — |
| 9440 | `run_stock_financial_agents` | `core.tasks.run_stock_financial_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |
| 9468 | `run_prediction_market_agents` | `core.tasks.run_prediction_market_agents` | no | — | `_run_agent_group` | depends on 1 helper(s): _run_agent_group |

### `tasks_initiatives.py` — 10 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 422 | `cleanup_junk_initiatives` | `core.tasks.cleanup_junk_initiatives` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 10687 | `advance_initiative_pipeline` | `core.tasks.advance_initiative_pipeline` | no | — | — | — |
| 10851 | `auto_kickstart_stuck_initiatives` | `core.tasks.auto_kickstart_stuck_initiatives` | no | — | — | — |
| 10891 | `extract_action_items_from_session` | `core.tasks.extract_action_items_from_session` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10935 | `dispatch_pending_action_items` | `core.tasks.dispatch_pending_action_items` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 10939 | `retry_blocked_research` | `core.tasks.retry_blocked_research` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10943 | `check_blocked_research_for_unblock` | `core.tasks.check_blocked_research_for_unblock` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10981 | `process_initiative_auto_progression` | `core.tasks.process_initiative_auto_progression` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10985 | `detect_duplicate_initiatives` | `core.tasks.detect_duplicate_initiatives` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 11060 | `generate_initiative_stage_document` | `core.tasks.generate_initiative_stage_document` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |

### `tasks_learning.py` — 14 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 426 | `run_learning_loop_cycle` | `core.tasks.run_learning_loop_cycle` | no | — | — | — |
| 461 | `summarize_learning_readback` | `core.tasks.summarize_learning_readback` | no | — | — | ignore_result=True — result-backend interaction differs |
| 484 | `cleanup_learning_readback_events` | `core.tasks.cleanup_learning_readback_events` | no | yes | — | ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 497 | `decay_learning_patterns` | `core.tasks.decay_learning_patterns` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 2184 | `update_learning_profiles` | `core.tasks.update_learning_profiles` | no | — | — | — |
| 2188 | `run_daily_learning_pipeline` | `core.tasks.run_daily_learning_pipeline` | no | — | — | — |
| 2476 | `run_agent_learning_cycle` | `core.tasks.run_agent_learning_cycle` | no | — | — | — |
| 2484 | `update_agent_effectiveness_from_learning` | `core.tasks.update_agent_effectiveness_from_learning` | no | — | — | — |
| 2488 | `broadcast_learning_status` | `core.tasks.broadcast_learning_status` | no | — | — | — |
| 2496 | `embed_daily_agent_learning` | `core.tasks.embed_daily_agent_learning` | no | — | — | — |
| 3740 | `run_project_learning_cycle` | `core.tasks.run_project_learning_cycle` | no | — | — | — |
| 3789 | `run_single_project_learning` | `core.tasks.run_single_project_learning` | no | — | — | — |
| 7280 | `mine_learning_patterns` | `core.tasks.mine_learning_patterns` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 12392 | `check_learning_loop_slo` | `core.check_learning_loop_slo` | yes | — | — | non-standard registered name `core.check_learning_loop_slo` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_media.py` — 11 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 897 | `create_talking_video_task` | `core.tasks.create_talking_video_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 1834 | `poll_pending_3d_models` | `core.tasks.poll_pending_3d_models` | no | — | — | — |
| 3936 | `transcribe_video_task` | `core.tasks.transcribe_video_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3941 | `generate_video_content_pack_task` | `core.tasks.generate_video_content_pack_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3945 | `ingest_video_task` | `core.tasks.ingest_video_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 3949 | `youtube_whisper_task` | `core.tasks.youtube_whisper_task` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim<br>ignore_result=True — result-backend interaction differs |
| 5028 | `start_resolve_render` | `core.tasks.start_resolve_render` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5033 | `poll_resolve_job_status` | `core.tasks.poll_resolve_job_status` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5037 | `record_resolve_outcome` | `core.tasks.record_resolve_outcome` | no | — | — | — |
| 5251 | `run_thumbnail_optimizer` | `core.tasks.run_thumbnail_optimizer` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10683 | `poll_processing_videos` | `core.tasks.poll_processing_videos` | no | — | — | — |

### `tasks_ops.py` — 134 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 415 | `reap_zombie_work` | `core.tasks.reap_zombie_work` | no | — | — | — |
| 528 | `auto_process_extracted_artifacts` | `core.tasks.auto_process_extracted_artifacts` | no | — | — | ignore_result=True — result-backend interaction differs |
| 1838 | `record_all_user_style_evolution` | `core.tasks.record_all_user_style_evolution` | no | — | — | ignore_result=True — result-backend interaction differs |
| 1842 | `execute_scheduled_workflow` | `core.tasks.execute_scheduled_workflow` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1846 | `sync_workflow_schedules` | `core.tasks.sync_workflow_schedules` | no | — | — | — |
| 1856 | `check_workflow_schedules` | `core.tasks.check_workflow_schedules` | no | — | — | custom retry policy — preserve verbatim |
| 1906 | `execute_pending_opportunity_tasks` | `core.tasks.execute_pending_opportunity_tasks` | no | — | — | — |
| 1910 | `expire_old_opportunities` | `core.tasks.expire_old_opportunities` | no | — | — | — |
| 1914 | `generate_opportunity_report` | `core.tasks.generate_opportunity_report` | no | — | — | — |
| 1918 | `train_ml_scoring_model` | `core.tasks.train_ml_scoring_model` | no | — | — | — |
| 1922 | `evaluate_ml_model_performance` | `core.tasks.evaluate_ml_model_performance` | no | — | — | — |
| 1926 | `process_realtime_scoring_queue` | `core.tasks.process_realtime_scoring_queue` | no | — | — | — |
| 1930 | `process_batch_scoring_queue` | `core.tasks.process_batch_scoring_queue` | no | — | — | — |
| 1980 | `cleanup_stale_scoring_requests` | `core.tasks.cleanup_stale_scoring_requests` | no | — | — | — |
| 1988 | `process_distribution` | `core.tasks.process_distribution` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 2172 | `update_distribution_analytics` | `core.tasks.update_distribution_analytics` | no | — | — | — |
| 2176 | `discover_success_patterns` | `core.tasks.discover_success_patterns` | no | — | — | — |
| 2180 | `generate_user_insights` | `core.tasks.generate_user_insights` | no | — | — | — |
| 2227 | `run_proactive_system_check` | `core.tasks.run_proactive_system_check` | no | — | — | — |
| 2272 | `check_all_alerts` | `core.tasks.check_all_alerts` | no | — | — | — |
| 2302 | `generate_smart_suggestions` | `core.tasks.generate_smart_suggestions` | no | — | — | — |
| 2345 | `execute_scheduled_automations` | `core.tasks.execute_scheduled_automations` | no | — | — | — |
| 2406 | `cleanup_old_notifications` | `core.tasks.cleanup_old_notifications` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 2443 | `expire_old_suggestions` | `core.tasks.expire_old_suggestions` | no | — | — | — |
| 2492 | `validate_knowledge_sources` | `core.tasks.validate_knowledge_sources` | no | — | — | — |
| 2936 | `propagate_new_policies` | `core.tasks.propagate_new_policies` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2977 | `broadcast_dream_journal` | `core.tasks.broadcast_dream_journal` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2981 | `score_and_promote_dreams` | `core.tasks.score_and_promote_dreams` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2985 | `process_approved_dreams` | `core.tasks.process_approved_dreams` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 2989 | `cleanup_stale_dreams` | `core.tasks.cleanup_stale_dreams` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 2993 | `execute_dream_implementations` | `core.tasks.execute_dream_implementations` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move |
| 3377 | `explore_dream_topic` | `core.tasks.explore_dream_topic` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3381 | `run_hive_mind_session` | `core.tasks.run_hive_mind_session` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3428 | `generate_memory_embedding` | `core.tasks.generate_memory_embedding` | no | — | — | — |
| 3597 | `sync_project_knowledge` | `core.tasks.sync_project_knowledge` | no | — | — | — |
| 3666 | `process_research_feedback` | `core.tasks.process_research_feedback` | no | — | — | — |
| 3919 | `auto_resolve_knowledge_gaps` | `core.tasks.auto_resolve_knowledge_gaps` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3923 | `process_document_async` | `core.tasks.process_document_async` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3927 | `process_url_async` | `core.tasks.process_url_async` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3931 | `generate_document_embeddings` | `core.tasks.generate_document_embeddings` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 3953 | `collect_training_data` | `core.tasks.collect_training_data` | no | — | — | — |
| 3957 | `collect_training_data_full` | `core.tasks.collect_training_data_full` | no | — | — | — |
| 4109 | `cleanup_celery_task_events` | `core.tasks.cleanup_celery_task_events` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 4122 | `cleanup_llm_call_logs` | `core.tasks.cleanup_llm_call_logs` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 4135 | `generate_weekly_opportunity_digest` | `core.tasks.generate_weekly_opportunity_digest` | no | — | — | — |
| 4139 | `send_proactive_opportunity_alerts` | `core.tasks.send_proactive_opportunity_alerts` | no | — | — | — |
| 4143 | `send_personalized_opportunity_alerts` | `core.tasks.send_personalized_opportunity_alerts` | no | — | — | — |
| 4155 | `assemble_chunked_upload` | `core.tasks.assemble_chunked_upload` | no | — | — | — |
| 4159 | `cleanup_expired_uploads` | `core.tasks.cleanup_expired_uploads` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 4201 | `sync_pipeline_insights_to_collective` | `core.tasks.sync_pipeline_insights_to_collective` | no | — | — | — |
| 4205 | `run_autonomous_intelligence_loop` | `core.tasks.run_autonomous_intelligence_loop` | no | — | — | — |
| 4238 | `run_daily_intelligence_digest` | `core.tasks.run_daily_intelligence_digest` | no | — | — | — |
| 4366 | `process_hitl_escalations` | `core.tasks.process_hitl_escalations` | no | — | — | — |
| 4401 | `expire_overdue_validations` | `core.tasks.expire_overdue_validations` | no | — | — | — |
| 4440 | `process_event_bus_scoring_queue` | `core.tasks.process_event_bus_scoring_queue` | no | — | — | — |
| 4474 | `process_event_bus_validation_queue` | `core.tasks.process_event_bus_validation_queue` | no | — | — | — |
| 4508 | `process_event_bus_analytics_queue` | `core.tasks.process_event_bus_analytics_queue` | no | — | — | — |
| 4543 | `claim_stale_events` | `core.tasks.claim_stale_events` | no | — | — | — |
| 4588 | `get_event_bus_stats` | `core.tasks.get_event_bus_stats` | no | — | — | — |
| 4697 | `unified_pipeline_health_check` | `unified_pipeline.health_check` | yes | — | — | non-standard registered name `unified_pipeline.health_check` — preserve verbatim during move |
| 4705 | `aggregate_roi_metrics_daily` | `core.tasks.aggregate_roi_metrics_daily` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4713 | `generate_weekly_intelligence_brief` | `core.tasks.generate_weekly_intelligence_brief` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 4717 | `record_opportunity_view` | `roi_metrics.record_opportunity_view` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_view` — preserve verbatim during move |
| 4744 | `record_opportunity_click` | `roi_metrics.record_opportunity_click` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_click` — preserve verbatim during move |
| 4774 | `record_opportunity_application` | `roi_metrics.record_opportunity_application` | yes | — | — | non-standard registered name `roi_metrics.record_opportunity_application` — preserve verbatim during move |
| 4804 | `record_revenue_event` | `roi_metrics.record_revenue` | yes | — | — | non-standard registered name `roi_metrics.record_revenue` — preserve verbatim during move |
| 4853 | `process_trigger_events` | `triggers.process_trigger_events` | yes | — | — | non-standard registered name `triggers.process_trigger_events` — preserve verbatim during move |
| 4997 | `create_default_triggers` | `triggers.create_default_triggers` | yes | — | — | non-standard registered name `triggers.create_default_triggers` — preserve verbatim during move |
| 5041 | `cleanup_old_resolve_jobs` | `core.tasks.cleanup_old_resolve_jobs` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 5087 | `run_design_trends_monitor` | `core.tasks.run_design_trends_monitor` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5091 | `run_viral_content_predictor` | `core.tasks.run_viral_content_predictor` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5095 | `run_job_match_intelligence` | `core.tasks.run_job_match_intelligence` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5146 | `run_side_hustle_detector` | `core.tasks.run_side_hustle_detector` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5193 | `run_tech_stack_tracker` | `core.tasks.run_tech_stack_tracker` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5197 | `run_ai_model_monitor` | `core.tasks.run_ai_model_monitor` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5201 | `run_case_law_monitor` | `core.tasks.run_case_law_monitor` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5205 | `run_regulatory_change_detector` | `core.tasks.run_regulatory_change_detector` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5255 | `run_freelance_opportunity_scout` | `core.tasks.run_freelance_opportunity_scout` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5267 | `run_skill_gap_analyzer` | `core.tasks.run_skill_gap_analyzer` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 5486 | `run_autonomous_thinking_cycle` | `core.tasks.run_autonomous_thinking_cycle` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5490 | `scan_concerns_for_human_action` | `core.tasks.scan_concerns_for_human_action` | no | — | — | — |
| 5494 | `batch_extract_artifacts` | `core.tasks.batch_extract_artifacts` | no | — | — | — |
| 5537 | `execute_approved_artifacts` | `core.tasks.execute_approved_artifacts` | no | — | — | custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5557 | `execute_single_artifact` | `core.tasks.execute_single_artifact` | no | — | — | custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 5707 | `maintain_dream_backlog` | `core.tasks.maintain_dream_backlog` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 5711 | `refresh_system_state_cache` | `core.tasks.refresh_system_state_cache` | no | — | — | — |
| 5753 | `auto_triage_dreams` | `core.tasks.auto_triage_dreams` | no | — | — | — |
| 5931 | `monitor_celery_health` | `core.tasks.monitor_celery_health` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 6727 | `generate_human_attention_items` | `core.tasks.generate_human_attention_items` | no | — | — | — |
| 6731 | `process_human_attention_lifecycle` | `core.tasks.process_human_attention_lifecycle` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 6778 | `process_hivemind_sessions` | `core.tasks.process_hivemind_sessions` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move |
| 6828 | `process_high_scoring_opportunities` | `core.tasks.process_high_scoring_opportunities` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7074 | `check_celery_health` | `core.tasks.check_celery_health` | no | yes | — | ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 7078 | `execute_orchestration_async` | `core.tasks.execute_orchestration_async` | no | — | — | — |
| 7128 | `check_orchestration_timeouts` | `core.tasks.check_orchestration_timeouts` | no | — | — | — |
| 7132 | `check_orchestration_auto_approvals` | `core.tasks.check_orchestration_auto_approvals` | no | — | — | — |
| 7160 | `execute_approved_dreams_via_orchestration` | `core.tasks.execute_approved_dreams_via_orchestration` | no | — | — | custom time limits — production timing-critical; do not alter on move |
| 7209 | `execute_single_dream` | `core.tasks.execute_single_dream` | no | — | — | — |
| 7324 | `maintain_knowledge_freshness` | `core.tasks.maintain_knowledge_freshness` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7362 | `promote_to_shared_knowledge` | `core.tasks.promote_to_shared_knowledge` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 7564 | `verify_autopilot_action` | `core.tasks.verify_autopilot_action` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>ignore_result=True — result-backend interaction differs |
| 9249 | `workspace_autopilot_tick` | `workspace.autopilot_tick` | yes | — | — | non-standard registered name `workspace.autopilot_tick` — preserve verbatim during move |
| 9717 | `update_mythology_pattern_statistics` | `core.tasks.update_mythology_pattern_statistics` | no | — | — | — |
| 10048 | `run_system_self_audit` | `core.tasks.run_system_self_audit` | no | — | — | — |
| 10052 | `discover_and_import_audits` | `core.tasks.discover_and_import_audits` | no | — | — | — |
| 10068 | `assign_open_findings_to_agents` | `core.tasks.assign_open_findings_to_agents` | no | — | — | — |
| 10083 | `execute_remediation_tasks` | `core.tasks.execute_remediation_tasks` | no | — | — | — |
| 10122 | `verify_completed_fixes` | `core.tasks.verify_completed_fixes` | no | — | — | — |
| 10149 | `run_autonomous_remediation_cycle` | `core.tasks.run_autonomous_remediation_cycle` | no | — | — | — |
| 10198 | `assign_and_execute_remediation` | `core.tasks.assign_and_execute_remediation` | no | — | — | — |
| 10624 | `cleanup_resolved_signatures` | `core.tasks.cleanup_resolved_signatures` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 10658 | `detect_failure_task` | `core.tasks.detect_failure_task` | no | — | — | — |
| 10670 | `run_conceptforge_pipeline` | `core.tasks.run_conceptforge_pipeline` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 10883 | `process_pending_auto_topics` | `process_pending_auto_topics` | yes | — | — | non-standard registered name `process_pending_auto_topics` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 10887 | `cleanup_expired_signals` | `cleanup_expired_signals` | yes | yes | — | non-standard registered name `cleanup_expired_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 11068 | `run_daily_priority_scan` | `core.tasks.run_daily_priority_scan` | no | — | — | — |
| 11099 | `check_operating_rhythm_status` | `core.tasks.check_operating_rhythm_status` | no | — | — | — |
| 11144 | `cleanup_audio_cache` | `core.tasks.cleanup_audio_cache` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 11151 | `auto_archive_stale_deliverables` | `core.tasks.auto_archive_stale_deliverables` | no | yes | — | custom time limits — production timing-critical; do not alter on move<br>referenced by beat schedule — name pin is non-optional |
| 11158 | `check_orphan_deliverables` | `core.tasks.check_orphan_deliverables` | no | — | — | custom time limits — production timing-critical; do not alter on move |
| 11164 | `enforce_db_retention` | `core.tasks.enforce_db_retention` | no | yes | — | custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11347 | `run_all_desks_intelligence` | `core.tasks.run_all_desks_intelligence` | yes | — | `_run_desks_inner` | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>depends on 1 helper(s): _run_desks_inner |
| 11574 | `surface_top_dreams` | `core.tasks.surface_top_dreams` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 11596 | `rescan_active_workspaces` | `core.tasks.rescan_active_workspaces` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task) |
| 11714 | `cleanup_expired_pa_insights` | `core.tasks.cleanup_expired_pa_insights` | no | yes | — | ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 11744 | `enforce_data_retention` | `core.tasks.enforce_data_retention` | no | yes | — | ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 12289 | `run_source_pack_workflow` | `core.tasks.run_source_pack_workflow` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12303 | `ops_control_loop` | `core.tasks.ops_control_loop` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12307 | `check_llm_cost_spike` | `core.tasks.check_llm_cost_spike` | no | — | — | ignore_result=True — result-backend interaction differs |
| 12311 | `run_ops_autopilot` | `core.tasks.run_ops_autopilot` | no | — | — | ignore_result=True — result-backend interaction differs |
| 12331 | `post_ops_digest` | `core.tasks.post_ops_digest` | no | — | — | ignore_result=True — result-backend interaction differs |
| 12341 | `sync_congress_data` | `core.tasks.sync_congress_data` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs |
| 12378 | `execute_code_job` | `core.tasks.execute_code_job` | yes | — | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>custom retry policy — preserve verbatim |
| 12386 | `rag_retrieval_canary` | `core.rag_retrieval_canary` | yes | — | — | non-standard registered name `core.rag_retrieval_canary` — preserve verbatim during move<br>ignore_result=True — result-backend interaction differs |

### `tasks_push_notifications.py` — 1 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 2364 | `send_pending_notifications` | `core.tasks.send_pending_notifications` | no | — | — | — |

### `tasks_spiders.py` — 19 task(s)

| Line | Function | Registered name | Already pinned? | Beat? | Helpers | Risk notes |
| ---: | --- | --- | :---: | :---: | --- | --- |
| 998 | `run_spider_by_category` | `core.tasks.run_spider_by_category` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 1002 | `execute_single_spider` | `core.tasks.execute_single_spider` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 1006 | `isolate_documents_batch` | `core.tasks.isolate_documents_batch` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom retry policy — preserve verbatim |
| 1010 | `monitor_isolation_progress` | `core.tasks.monitor_isolation_progress` | no | — | — | — |
| 1056 | `cleanup_isolation_metadata` | `core.tasks.cleanup_isolation_metadata` | no | — | — | — |
| 1103 | `collect_spider_data` | `core.tasks.collect_spider_data` | no | — | — | — |
| 1109 | `process_spider_data_automatic` | `core.tasks.process_spider_data_automatic` | no | — | — | — |
| 1160 | `process_core_spider_data` | `core.tasks.process_core_spider_data` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 1164 | `run_spider_network` | `core.tasks.run_spider_network` | no | yes | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |
| 1238 | `execute_single_spider_lightweight` | `core.tasks.execute_single_spider_lightweight` | no | — | — | — |
| 1860 | `score_opportunities_from_spider_data` | `core.tasks.score_opportunities_from_spider_data` | no | — | — | — |
| 1984 | `score_spider_data_async` | `core.tasks.score_spider_data_async` | no | — | — | — |
| 2928 | `trigger_spider_conversations` | `core.tasks.trigger_spider_conversations` | no | — | — | bind=True — uses self; tests must mock-bind, helpers must be method-safe |
| 3630 | `recalculate_spider_priorities` | `core.tasks.recalculate_spider_priorities` | no | — | — | — |
| 3702 | `update_project_spider_priorities` | `core.tasks.update_project_spider_priorities` | no | — | — | — |
| 3961 | `cleanup_spider_item_hashes` | `core.tasks.cleanup_spider_item_hashes` | no | yes | — | referenced by beat schedule — name pin is non-optional |
| 4000 | `spider_data_retention` | `core.tasks.spider_data_retention` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>custom time limits — production timing-critical; do not alter on move<br>ignore_result=True — result-backend interaction differs<br>referenced by beat schedule — name pin is non-optional |
| 6878 | `process_spider_actions` | `core.tasks.process_spider_actions` | yes | yes | — | name= already pinned (no Phase 1 edit needed for this task)<br>referenced by beat schedule — name pin is non-optional |
| 10875 | `aggregate_spider_signals` | `aggregate_spider_signals` | yes | yes | — | non-standard registered name `aggregate_spider_signals` — preserve verbatim during move<br>bind=True — uses self; tests must mock-bind, helpers must be method-safe<br>referenced by beat schedule — name pin is non-optional |

## Helpers (candidates for `tasks_helpers.py`)

| Line | Name | Used by N task(s) |
| ---: | --- | ---: |
| 3825 | `_analyze_spider_data_for_trends` | 0 |
| 80 | `_apply_task_routing_override` | 0 |
| 10214 | `_assign_and_execute_remediation_DISABLED` | 0 |
| 12119 | `_auto_research_competitor` | 0 |
| 3252 | `_build_image_prompt_from_dream` | 0 |
| 5274 | `_build_operational_context` | 0 |
| 7717 | `_calculate_deliverable_quality` | 1 |
| 6217 | `_calculate_kpi_delta` | 0 |
| 265 | `_circuit_breaker_check` | 0 |
| 346 | `_circuit_breaker_record_timeout` | 0 |
| 339 | `_circuit_breaker_release` | 0 |
| 1588 | `_collect_angellist` | 0 |
| 1408 | `_collect_coingecko` | 0 |
| 1784 | `_collect_crowdfunding` | 0 |
| 1600 | `_collect_design_platform` | 0 |
| 1336 | `_collect_devto` | 0 |
| 1632 | `_collect_education_platform` | 0 |
| 1467 | `_collect_etherscan` | 0 |
| 1530 | `_collect_financial_default` | 0 |
| 1620 | `_collect_freelance_default` | 0 |
| 1310 | `_collect_hackernews` | 0 |
| 1363 | `_collect_hashnode` | 0 |
| 1686 | `_collect_legal_platform` | 0 |
| 1809 | `_collect_news_default` | 0 |
| 1508 | `_collect_opensea` | 0 |
| 1519 | `_collect_premium_financial` | 0 |
| 1241 | `_collect_spider_data_sync` | 0 |
| 1555 | `_collect_weworkremotely` | 0 |
| 1440 | `_collect_yahoo_finance` | 0 |
| 2528 | `_conversation_spawn_allowed` | 0 |
| 2503 | `_conversation_temporal_context` | 0 |
| 4856 | `_create_blockchain_alert_from_trigger` | 0 |
| 3885 | `_create_learning_notification` | 0 |
| 928 | `_create_spider_instance` | 0 |
| 4928 | `_create_stock_alert_from_trigger` | 0 |
| 10854 | `_detect_initiative_content_type` | 0 |
| 3864 | `_detect_research_deltas` | 0 |
| 3341 | `_detect_visual_style` | 0 |
| 6062 | `_evaluate_pilot_outcome` | 0 |
| 3030 | `_execute_content_implementation` | 0 |
| 3091 | `_execute_experiment_implementation` | 0 |
| 2996 | `_execute_feature_implementation` | 0 |
| 7607 | `_execute_gate_repair` | 0 |
| 3122 | `_execute_generic_implementation` | 0 |
| 3060 | `_execute_research_implementation` | 0 |
| 3153 | `_execute_visual_implementation` | 0 |
| 10988 | `_extract_agent_content` | 0 |
| 8402 | `_extract_agent_output_content` | 0 |
| 2770 | `_extract_conversation_knowledge` | 0 |
| 142 | `_extract_discourse_markers` | 0 |
| 6144 | `_extract_experiment_learning` | 0 |
| 2825 | `_extract_hivemind_knowledge` | 0 |
| 108 | `_extract_opener` | 0 |
| 3792 | `_extract_topics_from_project` | 0 |
| 6230 | `_feed_learnings_to_collective_intelligence` | 0 |
| 9958 | `_format_metrics_for_audit` | 0 |
| 5875 | `_gather_experiment_metrics` | 0 |
| 10702 | `_gather_initiative_research` | 0 |
| 9756 | `_gather_live_system_metrics` | 0 |
| 6438 | `_generate_checklist_documentation` | 0 |
| 9015 | `_get_agent_class` | 0 |
| 9129 | `_get_next_task_for_agent` | 0 |
| 150 | `_get_overused_markers` | 0 |
| 3850 | `_get_previous_findings` | 0 |
| 10818 | `_get_previous_stage_context` | 0 |
| 10690 | `_get_stage_document_type` | 0 |
| 7405 | `_get_workspace_for_skin_layer` | 0 |
| 2722 | `_handle_conversation_delegation` | 0 |
| 93 | `_is_media_task_blocked` | 0 |
| 3297 | `_is_visual_dream` | 0 |
| 8963 | `_preflight_check_agent_data` | 0 |
| 2584 | `_preflight_gather_agent_data` | 0 |
| 6350 | `_process_single_gate` | 0 |
| 189 | `_record_timeout_signature` | 0 |
| 7586 | `_route_gate_repair` | 0 |
| 10275 | `_route_spec_to_human_attention_standalone` | 0 |
| 9257 | `_run_agent_group` | 14 |
| 10352 | `_run_agent_remediation_batch_DISABLED` | 0 |
| 9053 | `_run_agent_warmup` | 0 |
| 11792 | `_run_comparison_generation` | 0 |
| 11375 | `_run_desks_inner` | 1 |
| 941 | `_run_spider_adapter` | 0 |
| 6699 | `_send_gate_processing_discord` | 0 |
| 5903 | `_send_halt_discord_notification` | 0 |
| 6317 | `_send_implementation_discord` | 0 |
| 5974 | `_send_kpi_update_discord_notification` | 1 |
| 4628 | `_send_narrative_alerts_to_discord` | 0 |
| 4647 | `_send_narrative_digest_to_discord` | 0 |
| 6281 | `_send_pilot_evaluation_discord` | 0 |
| 6130 | `_simulate_kpi_progress` | 0 |
| 11703 | `_summarize_diff` | 0 |
| 11693 | `_summarize_params` | 0 |
| 259 | `_task_hash` | 0 |
| 9316 | `_track_group_contribution` | 0 |
| 11638 | `_ttl_days` | 0 |
| 11649 | `_upsert_insight` | 0 |
| 159 | `validate_agent_output` | 0 |

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
- `core.tasks.run_coo_daily_diagnostic` — ✓ matches a tasks.py task
- `core.tasks.run_cto_daily_diagnostic` — ✓ matches a tasks.py task
- `core.tasks.run_heartbeat` — ✓ matches a tasks.py task
- `core.tasks.run_spider_network` — ✓ matches a tasks.py task
- `core.tasks.run_trend_daily_diagnostic` — ✓ matches a tasks.py task
- `core.tasks.spider_data_retention` — ✓ matches a tasks.py task
- `core.tasks.surface_top_dreams` — ✓ matches a tasks.py task
- `intelligence.tasks.cleanup_old_opportunities` — ?  not from tasks.py (sibling file or external)
- `intelligence.tasks.scan_spider_opportunities` — ?  not from tasks.py (sibling file or external)
- `ml.cleanup_old_model_files` — ?  not from tasks.py (sibling file or external)
- `sports.cleanup_old_predictions` — ?  not from tasks.py (sibling file or external)

## Phase 1 mechanical-safety assessment

263 unpinned task(s) need an explicit `name="core.tasks.<func>"` kwarg added to their decorator. This edit is mechanical: a script can produce the diff, the runtime behaviour is identical (Celery already auto-registers under that name), and tests pass without modification.

**One special case** (24 task(s)): `backfill_signal_scores`, `track_prediction_outcomes`, `calculate_agent_accuracy`, `generate_content_for_channel`, `run_narrative_drift_cycle`, `update_narrative_statuses`, `trigger_content_from_narrative_shift`, `unified_pipeline_health_check`, `record_opportunity_view`, `record_opportunity_click`, `record_opportunity_application`, `record_revenue_event`, `run_blockchain_security_monitor`, `process_trigger_events`, `create_default_triggers`, `score_episode_voice`, `backfill_voice_scores`, `workspace_autopilot_tick`, `aggregate_spider_signals`, `trigger_signal_driven_conversation`, `process_pending_auto_topics`, `cleanup_expired_signals`, `rag_retrieval_canary`, `check_learning_loop_slo` carry a non-standard registered name (no `core.tasks.` prefix). Phase 1 must preserve these verbatim — do not 'normalize' them. Migrating these tasks to a sibling file requires the same `name=...` they currently use.

---

_Regenerate this plan after any change to `core/tasks.py` or the domain rules in `scripts/phase0_tasks_inventory.py`._
