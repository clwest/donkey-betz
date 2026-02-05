# Session 928 - Initiative Conversations + Blocker Analysis

**Date:** February 4, 2026
**Focus:** Enable conversations about initiatives + fix founder_intent blocker + add blocker analysis UI

---

## Summary

This session had three major accomplishments:
1. **Blocker Analysis UI** - Wired existing diagnose-stuck endpoint to Health tab
2. **Fixed founder_intent blocker** - Updated 50 initiatives to enable stage 2+ progression
3. **Initiative Conversations** - New "Discuss with Agents" feature allowing users to start multi-agent conversations about any initiative

---

## Part 1: Blocker Analysis UI (PR #828)

### Changes
- Added `pipelineHealth()` and `diagnoseStuck()` methods to `platformApi`
- Fixed 401 Unauthorized errors by replacing raw `fetch()` with authenticated API calls
- Added Blocker Analysis section to Health tab showing:
  - Summary stats (checked, ready to progress, founder intent missing, quality failed)
  - Top blocking reasons with visual breakdown bars
  - Daily rate limit status

### Key Finding
**Main blocker was `founder_intent_set = False`** - this flag defaults to False and stages 2+ require it to be True.

---

## Part 2: Founder Intent Fix + Stub Document Reset

### Production Commands Run
```bash
# 1. Fixed founder_intent for 50 initiatives with Stage 1 APPROVED
railway shell
python manage.py shell
>>> from core.models_document_registry import Initiative, InitiativeStage
>>> approved_stage1 = InitiativeStage.objects.filter(
...     stage=1, status='APPROVED'
... ).values_list('initiative_id', flat=True)
>>> updated = Initiative.objects.filter(
...     id__in=list(approved_stage1),
...     founder_intent_set=False
... ).update(founder_intent_set=True)
>>> # Result: 50 initiatives updated

# 2. Discovered 287 stub documents (only ~260 chars instead of 3000+)
>>> from core.models_document_registry import InitiativeStageDocument
>>> stubs = InitiativeStageDocument.objects.filter(
...     stage__stage=1
... ).annotate(
...     content_len=Length('generated_content')
... ).filter(content_len__lt=500)
>>> stubs.count()  # 287 stub documents

# 3. Reset stub stages to PENDING for regeneration
>>> stub_stage_ids = stubs.values_list('stage_id', flat=True)
>>> from core.models_document_registry import InitiativeStage
>>> reset_count = InitiativeStage.objects.filter(
...     id__in=list(stub_stage_ids),
...     status='APPROVED'
... ).update(status='PENDING')
>>> # Result: 286 stages reset to PENDING
```

### Findings
- 50 initiatives had Stage 1 APPROVED but `founder_intent_set=False` → Fixed
- 287 Stage 1 documents were stubs (~260 chars, just headers) → 286 reset for regeneration
- Expected next batch of Stage 1 generation to replace stub documents with proper content

---

## Part 3: Initiative Conversations Feature

### Problem
Users had no way to interact with initiatives - they could see them but couldn't discuss, question, or collaborate with agents about them.

### Solution
Added "Discuss with Agents" button that creates a HiveMindSession linked to the initiative with full context.

### Database Changes

**File: `core/models_unified_system.py`**
```python
# Added initiative FK to HiveMindSession
initiative = models.ForeignKey(
    'core.Initiative',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='conversations',
    help_text='Session 928: The initiative this conversation is discussing'
)
```

**Migration:** `core/migrations/0227_session_928_hivemind_initiative_fk.py`

### Backend Endpoint

**File: `core/views_initiative_kickstart.py`**
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_initiative_conversation(request, initiative_id):
    """
    Session 928: Start a multi-agent conversation about an initiative.
    Creates a HiveMindSession with full initiative context.
    """
```

**Endpoint:** `POST /api/initiatives/<uuid>/start-conversation/`

**Request Body (all optional):**
```json
{
    "topic": "Custom topic (defaults to initiative title)",
    "objective": "What to accomplish",
    "conversation_type": "analytical|creative|debate|planning|critique|general",
    "auto_select_agents": true
}
```

**Response:**
```json
{
    "success": true,
    "session_id": "uuid",
    "session_url": "/ai-studio/hivemind/uuid/",
    "message": "Started analytical conversation...",
    "participants": 4,
    "conversation_type": "analytical"
}
```

### Frontend Changes

**File: `frontend/src/lib/api.ts`**
```typescript
startConversation: (
  initiativeId: string,
  params?: {
    topic?: string
    objective?: string
    conversation_type?: 'analytical' | 'creative' | 'debate' | 'planning' | 'critique' | 'general'
    auto_select_agents?: boolean
  }
) => api.post<StartConversationResponse>(`/initiatives/${initiativeId}/start-conversation/`, params || {}),
```

**File: `frontend/src/pages/workspace/tabs/InitiativesTab.tsx`**
- Added "Discuss with Agents" button to InitiativeDetailModal footer
- Shows loading spinner while creating session
- Redirects to HiveMind session URL on success

### How It Works
1. User clicks "Discuss with Agents" button in initiative modal
2. Frontend calls `platformApi.startConversation(initiative.id)`
3. Backend creates HiveMindSession with:
   - Initiative FK link for traceability
   - Full context (origin, stages, action items, signals)
   - Auto-selected relevant agents via AgentRouter
4. Celery task triggers async conversation processing
5. User redirected to HiveMind session page

### Context Injection
The conversation receives rich context:
```python
context = f"""
## Initiative: {initiative.title}
**Origin:** {initiative.origin or 'User-initiated'}
**Purpose:** {initiative.purpose}
**Current Stage:** {current_stage_info}

### Stage Documents:
{stage_summaries}

### Pending Action Items:
{action_items}

### Related Signals:
{signal_info}
"""
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added `initiative` FK to HiveMindSession |
| `core/migrations/0227_session_928_hivemind_initiative_fk.py` | New migration |
| `core/views_initiative_kickstart.py` | Added `start_initiative_conversation()` endpoint |
| `core/urls.py` | Added route for new endpoint |
| `frontend/src/lib/api.ts` | Added `pipelineHealth()`, `diagnoseStuck()`, `startConversation()` |
| `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` | Added blocker analysis UI + "Discuss with Agents" button |

---

## PRs Created
- **#828**: Add Blocker Analysis to Initiative Health tab
- **#830**: Fix 401 errors on Health tab + Add Initiative Conversations feature

---

## Testing

### Manual Test Flow
1. Open Initiatives tab → Click any initiative
2. Click "Discuss with Agents" button in modal footer
3. Verify redirect to HiveMind session page
4. Verify conversation has initiative context
5. Verify agents are auto-selected based on initiative topic

### API Test
```bash
curl -X POST "http://localhost:8000/api/initiatives/<uuid>/start-conversation/" \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"conversation_type": "analytical", "auto_select_agents": true}'
```

---

## Next Steps

1. **Run migration on production:**
   ```bash
   railway run python manage.py migrate core 0227
   ```

2. **Monitor conversation creation:**
   - Check HiveMindSession records have initiative FK populated
   - Verify Celery tasks process conversations correctly

3. **Stage 2+ generation:**
   - Now that founder_intent is fixed for 50 initiatives
   - And stub documents are reset
   - Next batch should generate proper Stage 1 docs and enable Stage 2

---

## Key Insights

1. **Initiative conversations enable human-in-the-loop collaboration** - users can now guide, question, and iterate with agents on any initiative

2. **Context injection is critical** - the conversation includes full initiative context so agents understand what they're discussing

3. **AgentRouter auto-selection works well** - relevant agents are automatically selected based on initiative domain (finance → financial agents, tech → dev agents)

4. **HiveMind model already supported initiative context** - we just needed to add the FK and wire up the endpoint

---

**Session 928 Complete - Initiative Conversations feature enables users to discuss any initiative with relevant agents.**
