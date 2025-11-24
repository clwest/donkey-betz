# START HERE - Session 175

**Last Updated:** November 24, 2025 (Session 174 Complete)
**Current Status:** 99.8% Reality Score | 66+ features operational
**Platform:** Django Web Application (localhost:8000/ai-studio/)
**Previous Session:** Decision Modal UX Polish + Stance Detection
**Total Features:** 66+ working / 66+ total (100% complete!)
**Next Priority:** CRITICAL - Boardroom Memory System Integration

---

## CRITICAL SESSION 175 PRIORITY: MEMORY INTEGRATION

**User's Explicit Request:**
> "Did we tie the Board into the memory system? We might need to take a moment and deep dive into the /docs/ to make sure we are using the memory and prompting system to its fullest capacity"

**The Problem:**
The Boardroom (MeetingCoordinatorAgent) currently **STORES** meeting results to memory but **DOES NOT READ** any context before generating agent opinions. This makes agents "dumb" - they don't know:
- What decisions were made before
- What the user's style preferences are
- What projects exist and their context
- What the user liked/disliked in the past

**The Goal:**
Make agents say things like:
> "Based on our last decision to focus on bold visuals, and given you've consistently liked images with high contrast, I'd recommend..."

Instead of generic responses that could apply to anyone.

---

## SESSION 175 IMPLEMENTATION GUIDE

### Step 1: Understand the Memory System (READ THESE FILES)

```bash
# Core memory system
cat intelligence/shared_memory.py

# Style Memory with embeddings
cat style_memory/models.py
cat style_memory/views.py

# How agents currently use memory
cat agents/meeting_coordinator_agent.py

# The comprehensive audit document
cat docs/architecture/PROMPTING_SYSTEM_COMPREHENSIVE_AUDIT.md
```

### Step 2: Key Files to Modify

**Primary Target:**
- `agents/meeting_coordinator_agent.py` - Add memory retrieval before generating opinions

**Memory System Components:**
- `intelligence/shared_memory.py` - Has `AgentMemoryInterface` with:
  - `remember(memory_type, content)` - Store memories
  - `recall(memory_type)` - Retrieve specific memory
  - `learn_from_others(limit)` - Get experiences from other entities
  - `SharedMemorySystem.get_global_context()` - Get all active contexts

**Style Memory System:**
- `style_memory/models.py` - Has `StyleInteraction`, `StylePattern`, `UserStyleProfile`
- `style_memory/views.py` - Has retrieval functions

### Step 3: What to Implement

**In `MeetingCoordinatorAgent.start_meeting()` - ADD BEFORE generating perspectives:**

```python
# 1. Get past decisions from memory
past_decisions = self.memory.recall('past_decisions')

# 2. Get user's style preferences from Style Memory
# Query StyleInteraction model for user's likes/dislikes
from style_memory.models import StyleInteraction
user_interactions = StyleInteraction.objects.filter(
    user=self.user
).order_by('-created_at')[:20]

# 3. Get project context if project_id provided
if project_id:
    from content.models import Project
    project = Project.objects.filter(id=project_id).first()
    project_context = {
        'name': project.name if project else None,
        'description': project.description if project else None,
        'image_count': project.images.count() if project else 0
    }

# 4. Build context string for agent prompts
context_for_agents = f"""
CONTEXT FROM MEMORY:
- Past Decisions: {past_decisions}
- User Style Preferences: {summarize_preferences(user_interactions)}
- Project: {project_context if project_id else 'No project context'}

Use this context to give personalized, informed recommendations.
"""
```

**Then inject this context into each agent's perspective prompt.**

### Step 4: Test the Integration

```bash
# Start the platform
make start

# Test via UI
open http://localhost:8000/ai-studio/

# Click "New Decision" in Project tab
# Enter a topic like "Should we train on image 32 style?"
# Verify agents reference past decisions and preferences
```

---

## Quick Start Checklist

### 1. Update & Restart (Do This First)

```bash
# Navigate to project
cd /Users/donkeyking/development/unified-donkey-betz

# Stop any running services
make stop

# Check git status
git status

# Pull any updates (if working across machines)
git pull origin feature/session-52-ai-assistant

# Start fresh
make start

# Verify platform is running
open http://localhost:8000/ai-studio/
```

### 2. Verify Services Are Running

```bash
# Check Django (port 8000)
curl -s http://localhost:8000/health/ping/ | head -20

# Check Redis (port 6379)
redis-cli ping

# Check DaVinci status
curl -s http://localhost:8000/api/video/davinci-status/
```

---

## Session 174 Summary - Decision Modal UX Polish

### What Was Done

**Progress Bar Animation:**
- Added animated progress bar to Decision Timeline modal
- Shows visual feedback during ~20-30 second API calls (no more "hanging" feeling)
- Progress bar fills from 0% → 90% while waiting, jumps to 100% on completion
- Status text cycles through agent names: "Alex (CTO) is sharing their perspective..."
- Added `clearInterval()` cleanup in both success and error handlers

**Expandable Recommendation Cards:**
- Changed truncation from 300 to 150 chars
- Added "Read more" / "Show less" toggle
- Users can now read full agent responses

**Dynamic Confidence Scoring:**
- Replaced hardcoded 75% with language-based calculation
- "definitely/certainly" → 90-98%
- "recommend/should" → 75-87%
- "might/could" → 55-70%
- "uncertain" → 40-55%

**Enhanced Stance Detection:**
- Added ~24 support words: "smart move", "lean toward", "definitely"
- Fixed false positive "objection" from "weigh X against Y"
- Changed "against" to specific patterns: "against this", "against it"
- Removed "risk", "challenge", "issue" from concern words (too common)

**Agent AI Context (via Django shell):**
- Updated all 5 agent system prompts to include AI oversight context
- Added "CRITICAL CONTEXT: You oversee AI Assistants and AI Agents, NOT human employees"
- Agents now consider AI-specific factors: training costs, 24/7 operation, near-zero marginal costs

**Files Modified:**
- `ai_core/templates/ai_image_studio.html` - Progress bar HTML + JS animation (+100 lines)
- Agent templates updated in database via Django shell

**Impact:**
- UX improvement for the Co-Leadership feature
- Users now see clear visual feedback that the system is working
- Stance detection more accurate
- Confidence scores meaningful
- Reality Score: Maintained at 99.8%

---

## Session 173 Summary - Co-Leadership System + Training Fixes

### What Was Done

**Conversational Co-Leadership (GAME CHANGER!):**
- Added `coleadership_agent` tool to GPT function calling
- Users can now ask "What do you think about training on image 32 style?"
- AI executive team (CTO, COO, Creative Director, CFO) provides collaborative opinions
- Automatic stance detection (support, concern, objection, alternative)
- Formatted recommendations displayed in chat
- Summary with team consensus included

**Decision Timeline UI:**
- Added "New Decision" button to Project tab Decision Timeline section
- Multi-step modal (4 steps: Create → AI Recommendations → Commit → Log Outcome)
- Agent checkboxes for selecting which executives to consult
- Integration with boardroom/start API for real agent opinions

**Training System Fixes:**
- Fixed character_training_agent tool execution (400 errors)
- Fixed MIN_IMAGES mismatch (handler required 4, ZIP required 5) → Changed to 4
- Reduced training tracker log spam (only log every minute, not every poll)
- Removed verbose "Skipping old model" logs

**Agent Template Fixes:**
- Changed `DataAnalystAgent` to `CFOAgent` (DataAnalyst didn't exist in DB)
- Updated tool definition, handler, and frontend modal

**Files Modified:**
- `core/personal_ai_assistant_enhanced.py` - Co-leadership handler, keywords, tool definition (+180 lines)
- `core/views_image.py` - Added coleadership_agent to execute_tool (+10 lines)
- `ai_core/templates/ai_image_studio.html` - Decision modal, tracking fixes (+350 lines)
- `content/character_training.py` - MIN_IMAGES = 4

**Impact:**
- Reality Score: 99.7% → 99.8% (+0.1%)
- Two new major features: Conversational Co-Leadership + Decision Timeline UI
- Training pipeline working (Character 25 training submitted to Replicate)

---

## Memory System Architecture (FOR SESSION 175)

### intelligence/shared_memory.py

```python
# Key Classes:
SharedMemorySystem - Central memory storage using Redis
AgentMemoryInterface - Interface for agents (what MeetingCoordinatorAgent uses)
AdvisorMemoryInterface - Interface for advisors
AssistantMemoryInterface - Interface for personal assistant

# Key Methods:
store_memory(entity_type, entity_id, memory_type, content) → bool
retrieve_memory(entity_type, entity_id, memory_type) → Optional[Dict]
share_experience(entity_type, entity_id, experience) → bool
learn_from_experiences(entity_type, entity_id, limit) → List[Dict]
get_global_context() → Dict[str, Any]
add_knowledge_edge(from_entity, to_entity, relationship, strength) → None
```

### style_memory/models.py

```python
# Key Models:
StyleInteraction - Tracks user likes/dislikes (👍/👎/❤️ on images)
StylePattern - Learned patterns from interactions
UserStyleProfile - Aggregated user preferences

# Key Fields:
StyleInteraction.rating - 'like', 'dislike', 'love'
StyleInteraction.image - FK to ImageHistory
StyleInteraction.created_at - When interaction happened
```

### What MeetingCoordinatorAgent Currently Does

```python
# Line 60: Creates memory interface
self.memory = AgentMemoryInterface(agent_id='meeting_coordinator')

# Line 264-265: STORES meeting results (but never READS)
memory_key = f"boardroom_meeting_{topic.replace(' ', '_').lower()[:50]}"
self.memory.remember(memory_key, meeting_results)
```

### What MeetingCoordinatorAgent SHOULD Do

**BEFORE generating agent perspectives, add:**

```python
def _get_context_for_agents(self, topic: str, project_id: Optional[str]) -> str:
    """Gather all relevant context from memory systems."""
    context_parts = []

    # 1. Past boardroom decisions
    past_meetings = []
    for key in redis_client.keys(f"{self.memory.memory_prefix}agent:meeting_coordinator:boardroom_*"):
        data = redis_client.get(key)
        if data:
            meeting = json.loads(data)
            past_meetings.append({
                'topic': meeting.get('content', {}).get('topic'),
                'decisions': meeting.get('content', {}).get('decisions', []),
                'date': meeting.get('timestamp')
            })

    if past_meetings:
        recent = past_meetings[-3:]  # Last 3 meetings
        context_parts.append(f"PAST DECISIONS (last {len(recent)} meetings):")
        for m in recent:
            context_parts.append(f"  - {m['topic']}: {', '.join(m.get('decisions', []))}")

    # 2. User's style preferences from StyleInteraction
    if self.user:
        from style_memory.models import StyleInteraction
        likes = StyleInteraction.objects.filter(
            user=self.user, rating='like'
        ).select_related('image')[:10]

        dislikes = StyleInteraction.objects.filter(
            user=self.user, rating='dislike'
        ).select_related('image')[:5]

        if likes.exists() or dislikes.exists():
            context_parts.append("\nUSER STYLE PREFERENCES:")
            if likes:
                liked_styles = [i.image.style_preset for i in likes if i.image and i.image.style_preset]
                context_parts.append(f"  - Likes: {', '.join(set(liked_styles)) or 'various styles'}")
            if dislikes:
                disliked_styles = [i.image.style_preset for i in dislikes if i.image and i.image.style_preset]
                context_parts.append(f"  - Dislikes: {', '.join(set(disliked_styles)) or 'some styles'}")

    # 3. Project context
    if project_id:
        from content.models import Project
        try:
            project = Project.objects.get(id=project_id)
            context_parts.append(f"\nPROJECT CONTEXT:")
            context_parts.append(f"  - Name: {project.name}")
            context_parts.append(f"  - Images: {project.images.count()}")
            context_parts.append(f"  - Videos: {project.videos.count()}")
        except Project.DoesNotExist:
            pass

    return "\n".join(context_parts) if context_parts else "No prior context available."
```

**Then modify the perspective prompt (around line 133) to include:**

```python
# Get context before generating perspectives
memory_context = self._get_context_for_agents(topic, project_id)

perspective_prompt = f"""
Topic for discussion: {topic}

RELEVANT CONTEXT FROM MEMORY:
{memory_context}

You are {agent_template.display_name}. Based on your role and expertise:
{agent_template.system_prompt}

Provide your perspective on this topic in 2-3 sentences.
IMPORTANT: Reference the context above when relevant. If past decisions apply, mention them.
Focus on:
- Your area of expertise
- Key considerations from your domain
- Specific recommendations informed by our history
"""
```

---

## Key File Locations

### For Memory Integration:
```
# Primary target
agents/meeting_coordinator_agent.py

# Memory systems
intelligence/shared_memory.py
style_memory/models.py
style_memory/views.py

# Supporting context
coleadership/views.py
coleadership/models.py
```

### For Debugging During Testing:
```
# AI Assistant (if commands not working)
core/personal_ai_assistant_enhanced.py

# Image operations
core/views_image.py

# Video operations
core/views_video.py

# Frontend UI
ai_core/templates/ai_image_studio.html
```

### Logs:
```bash
# Server logs
tail -f .daphne.log

# Django shell for debugging
.venv/bin/python manage.py shell
```

---

## API Credits Status

Before testing, check available credits:

| Service | Status | Remaining |
|---------|--------|-----------|
| Stability AI | Active | ~6,990 credits |
| Runway ML | Active | ~900 credits (22%) |
| ElevenLabs | Active | Check dashboard |
| OpenAI | Active | Pay-as-you-go |
| Replicate | Active | Pay-as-you-go |

**Credit Conservation Tips:**
- Use ffmpeg operations when possible (FREE!)
- Batch similar operations together
- Test with small images/videos first
- Runway ML credits are limited - prioritize testing

---

## Platform Stats

| Metric | Count |
|--------|-------|
| Core Python code | ~152,000 lines |
| Video system alone | ~8,200 lines |
| AI Assistant | ~6,000 lines |
| Specialized agents | 55 |
| Sessions completed | 174 |
| API integrations | 36 services |
| Total features | 66+ (100%!) |
| Reality Score | 99.8% |

---

## Useful Commands

```bash
# Start everything
make start

# Stop everything
make stop

# Check specific service health
curl -s http://localhost:8000/health/ping/

# Django shell for debugging
.venv/bin/python manage.py shell

# Check database content
.venv/bin/python manage.py shell -c "from content.models import ImageHistory, VideoHistory, MiniFigAsset; print(f'Images: {ImageHistory.objects.count()}, Videos: {VideoHistory.objects.count()}, 3D: {MiniFigAsset.objects.filter(status=\"completed\").count()}')"

# Test API with admin token
TOKEN="19f3b711b2b1995255c5cc0e4182e085423c6557"
curl -s "http://localhost:8000/api/portfolio/?project_id=2ef834f7-31f5-4689-aae9-710a55f90b72" -H "Authorization: Token $TOKEN" | python3 -m json.tool | head -50

# Test boardroom API
curl -s -X POST "http://localhost:8000/api/v1/coleadership/boardroom/start/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test decision", "project_id": "2ef834f7-31f5-4689-aae9-710a55f90b72", "participants": ["CTOAgent", "CFOAgent"]}' | python3 -m json.tool
```

---

## Success Criteria for Session 175

**The integration is complete when:**

1. **Agents reference past decisions:**
   - "In our last meeting, we decided to focus on bold visuals. This aligns with..."

2. **Agents mention user preferences:**
   - "Given your preference for high-contrast images (based on your likes)..."

3. **Agents understand project context:**
   - "For the 'Tech Startup' project with 15 existing images..."

4. **No regression in existing functionality:**
   - Progress bar still works
   - Stance detection still accurate
   - Confidence scoring still meaningful

---

**Ready for Session 175!** Session 174 completed:
- Animated progress bar with status cycling
- Expandable recommendation cards
- Dynamic confidence scoring
- Enhanced stance detection
- Agent AI context prompts

**Session 175 Goal:**
Integrate Boardroom with Memory System so agents give personalized, context-aware recommendations based on past decisions, user preferences, and project context.

**Start with:** Read `agents/meeting_coordinator_agent.py` and `intelligence/shared_memory.py`
