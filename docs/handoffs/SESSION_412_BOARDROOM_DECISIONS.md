# Session 412: Boardroom Decisions Implementation

**Date:** December 10, 2025
**Status:** Complete
**Previous Session:** 410 (Document Threading + Response Session UI)

## Summary

Implemented the complete Boardroom Decisions system from the Session 322 blueprint. This system captures structured decisions from agent conversations, displays them in a UI, and feeds canonical policies back into agent prompts to influence future behavior.

## What Was Implemented

### Phase 1: Data Layer

1. **AgentDecisionSummary Model** (`core/models_unified_system.py:14848-15037`)
   - UUID primary key
   - Dual ForeignKey support: `conversation` (legacy AgentConversation) + `hive_session` (new HiveMindSession)
   - Decision types: policy, architecture, pipeline, product, experiment, guideline
   - Impact areas: prompting, memory, image, video, audio, workflow, agents, security, infrastructure, product, legal, research, spider
   - Key fields: topic, key_insights (JSON), recommended_stance, suggested_feature, rationale
   - Canonical promotion: is_canonical, promoted_at, promoted_by
   - Supersedes chain via `supersedes_id` (UUIDField)

2. **DecisionExtractor Service** (`core/services/decision_extractor.py`)
   - Uses GPT-5-mini to extract structured decisions from conversation conclusions
   - Methods:
     - `extract_decision()` - For AgentConversation
     - `extract_decision_from_hive_session()` - For HiveMindSession
     - `create_decision_from_conversation()` - Create and save from AgentConversation
     - `create_decision_from_hive_session()` - Create and save from HiveMindSession
     - `create_decision_from_any()` - Polymorphic creator

3. **Migration** (`core/migrations/0080_session_412_boardroom_decisions.py`)
   - Created and applied successfully

4. **Backfill Command** (`core/management/commands/backfill_decisions.py`)
   - Processes both AgentConversation and HiveMindSession records
   - Options: `--limit`, `--dry-run`, `--verbose`, `--source`
   - Usage: `.venv/bin/python manage.py backfill_decisions --limit=50`

### Phase 2: API + UI

1. **API Endpoints** (`core/views_agent_learning.py:1087-1205`)
   - `GET /api/boardroom/decisions/` - List decisions with filtering
   - Query params: `limit`, `canonical_only`, `decision_type`, `impact_area`
   - Response includes: source_type, source_id, source_topic, source_counts

2. **Boardroom UI** (`ai_core/templates/ai_image_studio.html:50277-50307`)
   - Added source type badges (Hive Mind / Conversation)
   - Source icons: 🐝 for hive sessions, 💬 for conversations

### Phase 3: Policy Injection

1. **PolicyContextService** (`core/services/policy_context.py`)
   - Maps agents to relevant impact areas
   - Added new agents: LegalDocDrafterAgent, VideoEditingAgent
   - Added new impact areas: legal, research, spider

2. **BaseAgent Integration** (`core/agents/base_agent.py:589-597`)
   - Policy injection in `_build_prompt()` method
   - Agents automatically receive relevant canonical policies
   - Maximum 3 policies per agent to avoid prompt bloat

## Database State

```
Total decisions: 499
From AgentConversation: 499
From HiveMindSession: 0
Canonical policies: 12
```

## Technical Notes

### HiveMindSession Field Mapping
- Uses `synthesis` field (not `synthesis_result`)
- Uses `question` for hive_mind mode topic
- Uses `conversation_topic` for conversation mode topic
- `participant_ids` is JSONField with agent UUIDs

### GPT-5-mini Configuration
- Uses `max_completion_tokens=2000` (not max_tokens)
- No temperature parameter (reasoning model)
- Uses `response_format={"type": "json_object"}`

## Files Modified

1. `core/models_unified_system.py` - Added AgentDecisionSummary model
2. `core/services/decision_extractor.py` - Updated for HiveMindSession support
3. `core/services/policy_context.py` - Added new impact areas and agents
4. `core/management/commands/backfill_decisions.py` - Fixed HiveMindSession fields
5. `core/views_agent_learning.py` - Updated API with source info
6. `ai_core/templates/ai_image_studio.html` - Added source badges to UI
7. `core/agents/base_agent.py` - Added policy injection

## Testing

```bash
# Test backfill (dry run)
.venv/bin/python manage.py backfill_decisions --dry-run --verbose --limit=5

# Test API
curl "http://localhost:8000/api/boardroom/decisions/?limit=3"
curl "http://localhost:8000/api/boardroom/decisions/?canonical_only=true"

# Test policy injection
.venv/bin/python manage.py shell -c "
from core.services.policy_context import get_policy_context_service
ps = get_policy_context_service()
print(ps.get_policies_for_agent('ImageAgent'))
"
```

## The Feedback Loop

1. **Agents have conversations** → Conclusions stored
2. **DecisionExtractor extracts decisions** → Structured summaries created
3. **Humans promote to canonical** → `is_canonical=True`
4. **PolicyContextService injects** → Canonical policies in agent prompts
5. **Agents influenced by policies** → Behavior shapes future decisions

This creates a governance feedback loop where agent decisions influence future agent behavior.

## Next Steps

- Run full backfill on production data
- Monitor policy injection effectiveness
- Consider UI for promoting decisions to canonical status
- Add metrics for policy influence tracking
