# Database Audit Report

**Generated:** 2025-12-30T01:44:41.911083
**Status:** ✅ HEALTHY

---

## Summary

| Metric | Count |
|--------|-------|
| Total Models | 394 |
| Healthy (table exists) | 394 |
| Missing Tables | 0 |
| Orphaned Tables | 66 |
| Custom db_table Names | 53 |

---

## By App

| App | Healthy | Missing | Status |
|-----|---------|---------|--------|
| admin | 1 | 0 | ✅ |
| agents | 10 | 0 | ✅ |
| ai_intelligence | 6 | 0 | ✅ |
| ai_opportunities | 4 | 0 | ✅ |
| auth | 2 | 0 | ✅ |
| authtoken | 2 | 0 | ✅ |
| coleadership | 5 | 0 | ✅ |
| content | 22 | 0 | ✅ |
| contenttypes | 1 | 0 | ✅ |
| core | 283 | 0 | ✅ |
| django_celery_beat | 6 | 0 | ✅ |
| django_celery_results | 3 | 0 | ✅ |
| intelligence | 6 | 0 | ✅ |
| ml | 1 | 0 | ✅ |
| mythology | 7 | 0 | ✅ |
| persistence | 7 | 0 | ✅ |
| pipelines | 2 | 0 | ✅ |
| rendering | 1 | 0 | ✅ |
| self_awareness | 6 | 0 | ✅ |
| sessions | 1 | 0 | ✅ |
| sports | 14 | 0 | ✅ |
| style_memory | 4 | 0 | ✅ |

---

## Orphaned Tables

These tables exist in PostgreSQL but have no corresponding Django model:

- `advisor_categories`
- `advisor_collaborations`
- `advisor_collaborations_advisors`
- `advisor_specializations`
- `advisor_verifications`
- `advisors`
- `advisors_specializations`
- `agents_agenttool_compatible_agents`
- `ai_intelligence_actionplan`
- `ai_intelligence_actionplanstep`
- `ai_intelligence_actionstep`
- `ai_intelligence_advisorintelligencefeed`
- `ai_intelligence_advisorrecruitment`
- `ai_intelligence_advisorvote`
- `ai_intelligence_agentexecution`
- `ai_intelligence_agentintelligencefeed`
- `ai_intelligence_agentlearningevent_related_events`
- `ai_intelligence_earningrecord`
- `ai_intelligence_learningdocument_source_events`
- `ai_intelligence_learninginsight_source_events`
- `ai_intelligence_opportunityactionplan`
- `ai_intelligence_opportunitytracking`
- `ai_intelligence_revenuemetrics`
- `ai_intelligence_spiderarmystatus`
- `ai_intelligence_spiderintelligencenode`
- `ai_intelligence_spiderperformancemetrics`
- `ai_intelligence_userincomeprofile`
- `blockchain_monitoring_session`
- `blockchain_security_alert`
- `content_contentgeneration_context_documents`
- `content_contentworkflow_required_knowledge_bases`
- `content_contentworkflow_required_templates`
- `content_document_allowed_users`
- `content_document_related_documents`
- `content_knowledgebase_contributors`
- `content_workflowexecution_generated_content`
- `content_workflowexecution_generated_documents`
- `core_agentconversation_participants`
- `core_agentmemory_connected_memories`
- `core_alliance_members`
- `core_casememorandum_source_documents`
- `core_channelmessage_mentioned_agents`
- `core_collaboration_advisors`
- `core_collaboration_collaborating_agents`
- `core_gamelinehistory`
- `core_memorycluster_related_clusters`
- `core_memorypalaceroom_memories`
- `core_oddssnapshot`
- `core_opportunitytask_assigned_agents`
- `core_teamworkflowstep_depends_on`
- `core_trackedconcern_actions_taken`
- `core_unifieduser_groups`
- `core_unifieduser_user_permissions`
- `design_system_update_source_trends`
- `market_monitoring_session`
- `narrative`
- `narrative_alert`
- `narrative_evidence`
- `narrative_shift`
- `persistence_agentcollaborationsession_knowledge_generated`
- `persistence_agentknowledge_related_knowledge`
- `persistence_spiderdata_similar_discoveries`
- `project_assistant_context`
- `stock_market_alert`
- `style_memory_stylepattern_related_memories`
- `style_memory_stylesuggestion_based_on_patterns`

These may be from deleted models or old migrations. Review before deleting.

---

## Custom Table Names

These models use custom `db_table` instead of Django defaults:

| Model | Custom Table | Default Would Be |
|-------|--------------|------------------|
| admin.LogEntry | django_admin_log | admin_logentry |
| contenttypes.ContentType | django_content_type | contenttypes_contenttype |
| sessions.Session | django_session | sessions_session |
| authtoken.TokenProxy | authtoken_token | authtoken_tokenproxy |
| core.ConversationMemory | core_conversation_memory | core_conversationmemory |
| core.ChatConversation | chat_conversations | core_chatconversation |
| core.GeneratedProject | core_generated_projects | core_generatedproject |
| core.GeneratedCode | core_generated_code | core_generatedcode |
| core.ContentChannel | content_channel | core_contentchannel |
| core.ChannelEpisode | channel_episode | core_channelepisode |
| core.TopicPerformance | topic_performance | core_topicperformance |
| core.ContentDebate | content_debate | core_contentdebate |
| core.DesignTrend | design_trend | core_designtrend |
| core.DesignSystemUpdate | design_system_update | core_designsystemupdate |
| core.ViralContentPrediction | viral_content_prediction | core_viralcontentprediction |
| core.ThumbnailVariant | thumbnail_variant | core_thumbnailvariant |
| core.JobMatchProfile | job_match_profile | core_jobmatchprofile |
| core.JobMatch | job_match | core_jobmatch |
| core.FreelanceOpportunity | freelance_opportunity | core_freelanceopportunity |
| core.SideHustle | side_hustle | core_sidehustle |
| core.SECFilingAnalysis | sec_filing_analysis | core_secfilinganalysis |
| core.CryptoSentiment | crypto_sentiment | core_cryptosentiment |
| core.EarningsPrediction | earnings_prediction | core_earningsprediction |
| core.TechStackTrend | tech_stack_trend | core_techstacktrend |
| core.AIModelRelease | ai_model_release | core_aimodelrelease |
| core.SkillGapAnalysis | skill_gap_analysis | core_skillgapanalysis |
| core.CaseLawUpdate | case_law_update | core_caselawupdate |
| core.RegulatoryChange | regulatory_change | core_regulatorychange |
| core.AutonomousSituationSession | autonomous_situation_session | core_autonomoussituationsession |
| core.SituationTrigger | situation_trigger | core_situationtrigger |
| core.TriggerEvent | trigger_event | core_triggerevent |
| core.PushSubscription | push_subscriptions | core_pushsubscription |
| core.NotificationPreference | notification_preferences | core_notificationpreference |
| core.NotificationLog | notification_logs | core_notificationlog |
| agents.AgentContribution | agent_contributions | agents_agentcontribution |
| coleadership.CoLeadershipDecision | coleadership_decision | coleadership_coleadershipdecision |
| coleadership.AgentRecommendation | coleadership_agent_recommendation | coleadership_agentrecommendation |
| coleadership.HumanDecision | coleadership_human_decision | coleadership_humandecision |
| coleadership.DecisionOutcome | coleadership_decision_outcome | coleadership_decisionoutcome |
| coleadership.CoLeadershipPreferences | coleadership_user_preferences | coleadership_coleadershippreferences |
| pipelines.CreativePipelineTemplate | pipeline_templates | pipelines_creativepipelinetemplate |
| pipelines.CreativePipelineRun | pipeline_runs | pipelines_creativepipelinerun |
| intelligence.SpiderIntelligenceNode | persistence_spiderdata | intelligence_spiderintelligencenode |
| intelligence.RevenueMetrics | persistence_revenuetracker | intelligence_revenuemetrics |
| intelligence.EarningRecord | persistence_revenuetracker | intelligence_earningrecord |
| content.ProjectShare | project_shares | content_projectshare |
| mythology.MythologyEvent | mythology_events | mythology_mythologyevent |
| mythology.MythPattern | myth_patterns | mythology_mythpattern |
| mythology.MythologyGuard | mythology_guards | mythology_mythologyguard |
| mythology.MythologyCleanup | mythology_cleanups | mythology_mythologycleanup |
| mythology.MythologyAlert | mythology_alerts | mythology_mythologyalert |
| mythology.FlaggedHallucination | flagged_hallucinations | mythology_flaggedhallucination |
| mythology.HallucinationReview | hallucination_reviews | mythology_hallucinationreview |

---

## How to Use This Audit

```bash
# Quick health check
python manage.py audit_database

# Detailed output
python manage.py audit_database --verbose

# Fix issues
python manage.py audit_database --fix

# CI/CD mode (exit 1 on issues)
python manage.py audit_database --fail-on-error

# Regenerate this report
python manage.py audit_database --output report
```

---

*Generated by `audit_database` management command (Session 623)*
