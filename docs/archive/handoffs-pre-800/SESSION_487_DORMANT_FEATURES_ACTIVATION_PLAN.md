# Session 487: Dormant Features Activation Plan

**Created:** December 18, 2025
**Goal:** Connect all built-but-dormant features to achieve 100% utilization
**Estimated Time:** 4-6 hours of focused work

---

## Executive Summary

After auditing ~500 sessions of development, we discovered significant untapped value:

| Category | Built | Connected | Gap |
|----------|-------|-----------|-----|
| Services | 66 | 52 | 14 orphaned |
| Models | 172 | 143 | 29 unused |
| Celery Tasks | 152 | 72 | 80 unscheduled |
| Autonomous Situations | 18 | 1 | 17 dormant |
| Management Commands | 35 | ~5 | 30 forgotten |

---

## Priority 1: Autonomous Situations (CRITICAL)

These were built to run 24/7 but only 1 is scheduled in Celery Beat.

### Location: `core/celery.py`

Add these to `beat_schedule`:

```python
# AUTONOMOUS SITUATIONS - Session 487 Activation
'run-autonomous-content-studio': {
    'task': 'core.tasks.run_autonomous_content_studio',
    'schedule': crontab(hour='*/4'),  # Every 4 hours
    'options': {'queue': 'autonomous'}
},
'check-narrative-drift': {
    'task': 'core.tasks.check_narrative_drift',
    'schedule': crontab(hour='*/6'),  # Every 6 hours
    'options': {'queue': 'autonomous'}
},
'match-jobs-to-profile': {
    'task': 'core.tasks.match_jobs_to_profile',
    'schedule': crontab(hour='8,12,18'),  # 3x daily
    'options': {'queue': 'autonomous'}
},
'scout-freelance-opportunities': {
    'task': 'core.tasks.scout_freelance_opportunities',
    'schedule': crontab(hour='9,15,21'),  # 3x daily
    'options': {'queue': 'autonomous'}
},
'monitor-crypto-markets': {
    'task': 'core.tasks.monitor_crypto_markets',
    'schedule': crontab(minute='*/30'),  # Every 30 min
    'options': {'queue': 'autonomous'}
},
'monitor-sec-filings': {
    'task': 'core.tasks.monitor_sec_filings',
    'schedule': crontab(hour='6,10,14,18'),  # 4x daily during market hours
    'options': {'queue': 'autonomous'}
},
'audit-blockchain-events': {
    'task': 'core.tasks.audit_blockchain_events',
    'schedule': crontab(minute='*/15'),  # Every 15 min
    'options': {'queue': 'autonomous'}
},
'monitor-case-law': {
    'task': 'core.tasks.monitor_case_law',
    'schedule': crontab(hour='7'),  # Daily at 7 AM
    'options': {'queue': 'autonomous'}
},
'analyze-skill-gaps': {
    'task': 'core.tasks.analyze_skill_gaps',
    'schedule': crontab(day_of_week='monday', hour='6'),  # Weekly
    'options': {'queue': 'autonomous'}
},
```

### Verification After Adding:
```bash
celery -A core inspect scheduled
```

---

## Priority 2: Orphaned Services (13 total)

### 2.1 Semantic Routing (HIGH IMPACT)
**File:** `core/services/semantic_routing.py`
**Session:** 293
**What:** Routes queries to agents using embeddings instead of keywords

**Integration Point:** `core/agent_router.py`

```python
# Add to agent_router.py
from core.services.semantic_routing import SemanticRoutingService

class AgentRouter:
    def __init__(self):
        self.semantic_router = SemanticRoutingService()

    def route(self, query: str, user=None):
        # Try semantic routing first
        semantic_result = self.semantic_router.route_query(query)
        if semantic_result.confidence > 0.7:
            return semantic_result.agent_name
        # Fall back to keyword routing
        return self._keyword_route(query)
```

### 2.2 Streaming Progress (HIGH IMPACT - UX)
**File:** `core/services/streaming_progress.py`
**Session:** 482
**What:** Real-time progress updates via WebSocket

**Integration Point:** `core/consumers.py`

```python
# Add WebSocket consumer for progress
from core.services.streaming_progress import ProgressTracker

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        await self.channel_layer.group_add(f'progress_{self.task_id}', self.channel_name)
        await self.accept()
```

**Frontend Integration:** `ai_core/templates/ai_image_studio.html`
```javascript
// Add progress WebSocket connection
function connectProgressSocket(taskId) {
    const ws = new WebSocket(`ws://${window.location.host}/ws/progress/${taskId}/`);
    ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        updateProgressUI(data.stage, data.percent, data.message);
    };
}
```

### 2.3 Implicit Learning
**File:** `core/services/implicit_learning.py`
**Session:** 210
**What:** Learns from user behavior (downloads, shares, time spent)

**Integration Points:**

1. **Download tracking** - `core/views_image.py` download endpoint:
```python
from core.services.implicit_learning import track_behavior

@api_view(['GET'])
def download_image(request, image_id):
    # ... existing download logic ...
    track_behavior(request.user, 'download', image_id, 'image')
    return response
```

2. **Share tracking** - Add to share endpoints
3. **View time** - Frontend JS to track time on gallery items

### 2.4 Domain Extraction
**File:** `core/services/domain_extraction_service.py`
**Session:** 350
**What:** Extracts business domains for targeted spider queries

**Integration Point:** `core/agents/research_agent.py`

```python
from core.services.domain_extraction_service import DomainExtractionService

class ResearchAgent(BaseAgent):
    def execute(self, task: str, **kwargs):
        # Extract domains for targeted queries
        domain_service = DomainExtractionService()
        domains = domain_service.extract_domains(task)

        # Use domain-specific queries for spiders
        spider_queries = domains['spider_queries']
        # ... rest of research logic
```

### 2.5 Memory Embedding Service
**File:** `core/services/memory_embedding_service.py`
**Session:** 293
**What:** Semantic search across agent memories

**Integration Point:** `core/agents/base_agent.py`

```python
from core.services.memory_embedding_service import MemoryEmbeddingService

class BaseAgent:
    def _get_relevant_memories(self, task: str):
        service = MemoryEmbeddingService()
        return service.search_memories(
            agent=self.agent_record,
            query=task,
            top_k=5
        )
```

### 2.6 Agent Intelligence Context
**File:** `core/services/agent_intelligence_context.py`
**Session:** 351
**What:** Aggregates agent knowledge for research context

**Integration Point:** Business research agents

```python
from core.services.agent_intelligence_context import get_agent_intelligence_context

class CompetitorAnalysisAgent(BaseAgent):
    def execute(self, task: str, **kwargs):
        # Get context from other agents' learnings
        context_service = get_agent_intelligence_context()
        agent_context = context_service.get_context_for_research(task)

        # Inject into prompt
        self.context = agent_context
```

### 2.7 Blockchain Event Listener
**File:** `core/services/blockchain_event_listener.py`
**Session:** 461
**What:** Real-time blockchain event monitoring

**Integration:** Add to Celery Beat (see Priority 1) and Discord notifications

### 2.8 Reference Resolver
**File:** `core/services/reference_resolver.py`
**Session:** 482
**What:** Resolves "it", "that", "the first one" in conversations

**Integration Point:** `core/personal_ai_assistant_enhanced.py`

```python
from core.services.reference_resolver import ReferenceResolver

class PersonalAIAssistant:
    def __init__(self):
        self.reference_resolver = ReferenceResolver()

    def process_message(self, message: str, conversation_history: list):
        # Resolve references before processing
        resolved_message = self.reference_resolver.resolve(
            message,
            conversation_history
        )
```

### 2.9 Resolve Learning
**File:** `core/services/resolve_learning.py`
**Session:** 478
**What:** Learns which color grades perform best

**Integration Point:** `core/agents/resolve_agent.py` (already exists, verify connection)

### 2.10-2.13 Remaining Services
- `classification_integration.py` - Connect to query classifier
- `discord_bot.py` - Running via management command
- `discord_voice.py` - Voice channel features
- `proactive_intelligence.py` - Already partially connected

---

## Priority 3: Revenue Features (MONETIZATION)

### 3.1 Gumroad Publishing
**File:** `core/services/gumroad_publishing.py`
**Session:** 295

**Frontend Integration:** Add "Sell on Gumroad" button to image gallery

```html
<!-- In ai_image_studio.html, add to image action buttons -->
<button onclick="publishToGumroad('${image.id}')" class="btn-gumroad">
    Sell on Gumroad
</button>
```

```javascript
async function publishToGumroad(imageId) {
    const response = await fetch('/api/gumroad/publish/', {
        method: 'POST',
        body: JSON.stringify({ image_id: imageId, price: 5.00 })
    });
    // Handle response
}
```

### 3.2 Marketplace Discovery
**File:** `core/services/marketplace_discovery_service.py`
**Session:** 295

**Integration:** Show marketplace suggestions when viewing images

```python
# Add endpoint
@api_view(['GET'])
def get_marketplace_suggestions(request, image_id):
    from core.services.marketplace_discovery_service import MarketplaceDiscoveryService
    service = MarketplaceDiscoveryService()
    suggestions = service.find_marketplaces_for_image(image_id)
    return Response({'marketplaces': suggestions})
```

### 3.3 Certificate Service
**File:** `core/services/certificate_service.py`
**Session:** 295

**Integration:** Add "Download Certificate" to image menu

```python
@api_view(['GET'])
def download_certificate(request, image_id):
    from core.services.certificate_service import CertificateService
    service = CertificateService()
    certificate = service.generate_certificate(image_id, request.user)
    return FileResponse(certificate, filename=f'certificate_{image_id}.pdf')
```

---

## Priority 4: A/B Testing Framework

**File:** `core/views_ab_testing.py`
**Session:** 235

### Models to Activate:
- `ABTest` - Experiment definitions
- `ABVariant` - Test variations
- `ABAssignment` - User assignments
- `ABConversion` - Conversion tracking
- `ABExperimentResult` - Results analysis

### Integration Points:

1. **Prompt A/B Testing:**
```python
from core.services.ab_testing import get_ab_variant

def generate_image(prompt, user):
    # Get A/B variant for prompt enhancement
    variant = get_ab_variant(user, 'prompt_enhancement_v1')

    if variant == 'enhanced':
        prompt = enhance_prompt(prompt)
    elif variant == 'style_added':
        prompt = add_style_keywords(prompt)
    # Control group uses original prompt
```

2. **Model A/B Testing:**
```python
variant = get_ab_variant(user, 'model_selection_v1')
model = {
    'fast': 'core',
    'quality': 'sd3',
    'premium': 'ultra'
}.get(variant, 'sdxl')
```

---

## Priority 5: Unused Models (29 total)

### High-Value Models to Activate:

| Model | Purpose | Integration Needed |
|-------|---------|-------------------|
| `UserPreferenceProfile` | Store user preferences | Connect to implicit learning |
| `StyleEvolution` | Track style preferences over time | Connect to style recommendations |
| `AdvisorInsight` | Store advisor recommendations | Show in dashboard |
| `SpiderAnalytics` | Spider performance metrics | Analytics dashboard |
| `TrendSnapshot` | Historical trend data | Trend comparison features |
| `SavedOpportunity` | User-saved opportunities | Opportunity bookmarking UI |
| `LegalCase` | Case management | Legal assistant panel |
| `ValidationDecision` | HITL decisions | Validation dashboard |

---

## Priority 6: Management Commands to Document/Expose

### Most Valuable Commands:

```bash
# System Health
python manage.py reality_check          # Comprehensive health check
python manage.py validate_data_integrity  # Data validation
python manage.py validate_security       # Security audit

# Agent Management
python manage.py force_agent_cycle       # Force dreams/conversations
python manage.py sync_agent_learning     # Sync learning across agents
python manage.py connect_all_agents      # Ensure all agents connected

# Data Operations
python manage.py bulk_embed_spiders      # Embed all spider data
python manage.py process_spider_data     # Process pending spider data
python manage.py discover_learning_cohorts  # Find learning patterns

# Platform
python manage.py init_platform           # Initialize platform
python manage.py seed_golden_path_demo   # Create demo data
```

### Add to Admin Dashboard:
Create `/admin/commands/` page with buttons to trigger these.

---

## Verification Checklist

After each integration, verify:

- [ ] Service imports without errors
- [ ] Endpoint returns expected response
- [ ] Frontend calls endpoint successfully
- [ ] Celery task executes (if applicable)
- [ ] Logs show expected behavior
- [ ] No performance degradation

---

## Testing Commands

```bash
# Test service imports
python -c "from core.services.semantic_routing import SemanticRoutingService; print('OK')"

# Test Celery tasks
celery -A core inspect scheduled

# Test API endpoints
curl http://localhost:8000/api/ab-testing/experiments/

# Check logs
tail -f logs/django.log | grep -E "ERROR|WARNING"
```

---

## Session 488+ Roadmap

1. **Session 488:** Enable all 18 Autonomous Situations
2. **Session 489:** Connect Semantic Routing + Streaming Progress
3. **Session 490:** Activate A/B Testing Framework
4. **Session 491:** Connect Implicit Learning + Behavior Tracking
5. **Session 492:** Enable Revenue Features (Gumroad, Marketplace, Certificates)
6. **Session 493:** Activate Memory Embedding for all agents
7. **Session 494:** Final verification and 100% utilization celebration

---

## Notes

- The watermark integration (Session 487) is now complete and serves as an example of how to connect dormant features
- Each feature typically needs: import → service call → API endpoint → frontend integration
- Test each integration before moving to the next
- Some features may have dependency chains (e.g., implicit learning needs behavior tracking first)

---

**Let's get to 100% utilization!**
