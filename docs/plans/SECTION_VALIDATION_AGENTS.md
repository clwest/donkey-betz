<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# Section Validation Agents

## Concept

Create specialized validation agents for each major section of the platform that can:
1. **Health Check**: Verify endpoints are responding
2. **Integration Test**: Test data flows between components
3. **Smoke Test**: Run quick functional tests
4. **Report Status**: Provide clear health reports

---

## Proposed Sections & Agents

### 1. ImageValidationAgent
**Domain:** Image generation, editing, gallery
**Endpoints to verify:**
- `/api/images/history/` - Gallery listing
- `/api/stability/upscale/` - Image upscaling
- `/api/stability/remove-background/` - Background removal
- `/api/images/<id>/favorite/` - Favorite toggle
- `/api/images/<id>/delete/` - Delete image

**Integration checks:**
- User can list their images
- Images are properly stored with metadata
- Stability AI connection is working

### 2. VideoValidationAgent
**Domain:** Video generation, editing, gallery
**Endpoints to verify:**
- `/api/v1/video/history/` - Video listing
- `/api/v1/video/text-to-video/` - Text to video
- `/api/v1/video/image-to-video/` - Image to video
- `/api/video/trim/` - Video trimming
- `/api/video/speed/` - Speed change
- `/api/video/effects/` - Video effects

**Integration checks:**
- Runway ML connection is working
- Video files are properly stored
- FFmpeg operations complete successfully

### 3. AudioValidationAgent
**Domain:** Voice generation, cloning, marketplace
**Endpoints to verify:**
- `/api/voice-marketplace/` - Voice listings
- `/api/voice-marketplace/voices/` - Available voices
- `/api/voice-marketplace/generate/` - TTS generation

**Integration checks:**
- ElevenLabs API connection
- Voice cloning pipeline
- Audio file storage

### 4. AgentOrchestrationValidationAgent
**Domain:** Agent routing, execution, workflows
**Endpoints to verify:**
- `/api/agents/` - Agent registry
- `/api/agent-dashboard/` - Agent dashboard
- `/api/collective/` - Collective intelligence

**Integration checks:**
- All 32 agents are importable
- Agent router correctly routes tasks
- Workflows execute end-to-end

### 5. SpiderValidationAgent
**Domain:** Spider network, data collection
**Endpoints to verify:**
- `/api/spider-dashboard/` - Spider dashboard
- `/api/spider-intelligence/` - Spider feeds

**Integration checks:**
- Spider registry has all spiders
- Real spiders can fetch data
- Data is stored in SpiderData model

### 6. KnowledgeValidationAgent
**Domain:** RAG, embeddings, search
**Endpoints to verify:**
- RAG search endpoints
- Embedding generation
- Knowledge retrieval

**Integration checks:**
- OpenAI embedding API works
- Vector search returns results
- Knowledge pipeline flows to agents

### 7. DiscordValidationAgent
**Domain:** Discord bot, commands, notifications
**Endpoints to verify:**
- `/api/discord/verify-link-code/` - Discord linking

**Integration checks:**
- Bot is connected
- Commands are registered
- Notifications are sent

### 8. WorkflowValidationAgent
**Domain:** Multi-step workflows, orchestration
**Endpoints to verify:**
- Workflow execution endpoints

**Integration checks:**
- Workflow history is tracked
- Multi-step workflows complete
- Results are stored correctly

---

## Implementation Approach

### Option A: Python Management Command
```bash
python manage.py validate_section --section=images
python manage.py validate_section --all
```

### Option B: API Endpoint
```
GET /api/system/validate/images/
GET /api/system/validate/all/
```

### Option C: Discord Command
```
/validate images
/validate all
```

### Option D: Web Dashboard Panel
Add a "System Health" panel that shows status of all sections.

---

## Example Implementation

```python
# core/validation/image_validator.py
class ImageValidationAgent:
    """Validates the image generation and editing subsystem."""

    def __init__(self, user=None):
        self.user = user
        self.results = []

    def validate_all(self) -> dict:
        """Run all validation checks."""
        return {
            'section': 'images',
            'status': 'healthy' if all(r['pass'] for r in self.results) else 'degraded',
            'checks': self.results,
            'timestamp': timezone.now().isoformat()
        }

    def check_gallery_endpoint(self):
        """Verify gallery listing works."""
        try:
            response = self.client.get('/api/images/history/')
            self.results.append({
                'name': 'gallery_endpoint',
                'pass': response.status_code == 200,
                'message': f'Status: {response.status_code}'
            })
        except Exception as e:
            self.results.append({
                'name': 'gallery_endpoint',
                'pass': False,
                'message': str(e)
            })

    def check_stability_connection(self):
        """Verify Stability AI API is accessible."""
        # Implementation here

    def check_storage(self):
        """Verify image storage is working."""
        # Implementation here
```

---

## Benefits

1. **Proactive Monitoring**: Catch issues before users report them
2. **Regression Detection**: Run after deployments to verify nothing broke
3. **Documentation**: Validators serve as living documentation of what works
4. **Confidence**: Know exactly what's working and what's not
5. **Debugging**: Quickly identify which subsystem has issues

---

## Recommended Implementation Order

1. **ImageValidationAgent** - Most critical, most used
2. **AgentOrchestrationValidationAgent** - Core of the platform
3. **SpiderValidationAgent** - Data pipeline health
4. **VideoValidationAgent** - Second most used creation feature
5. **DiscordValidationAgent** - User-facing integration
6. **AudioValidationAgent** - Voice marketplace validation
7. **KnowledgeValidationAgent** - RAG system health
8. **WorkflowValidationAgent** - Multi-step validation

---

## Implementation Status (Session 452)

### Completed ✅

1. **Base Infrastructure:**
   - `core/validation/__init__.py` - Module exports and `run_all_validations()`
   - `core/validation/base.py` - `BaseValidationAgent` with helper methods

2. **Section Validators:**
   - `core/validation/image_validator.py` - ImageValidationAgent
   - `core/validation/video_validator.py` - VideoValidationAgent
   - `core/validation/agent_validator.py` - AgentOrchestrationValidator
   - `core/validation/spider_validator.py` - SpiderValidationAgent

3. **CLI Interface:**
   - `core/management/commands/validate_section.py`
   - Usage: `python manage.py validate_section --section=images`
   - Usage: `python manage.py validate_section --all`
   - Usage: `python manage.py validate_section --list`

### Sample Output

```
============================================================
Running ALL section validations...
============================================================

Section: images
Status: DEGRADED

  ✗ gallery_endpoint: GET /api/images/history/ -> 400 (17ms)
  ✓ upscale_endpoint_exists: POST /api/stability/upscale/ -> 400 (9ms)
  ✓ image_history_model: ImageHistory: 188 records (min: 0) (0ms)
  ✓ stability_api_key: STABILITY_API_KEY: configured (0ms)
  ✓ image_generation_service_import: Successfully imported (0ms)

Total: 6 checks, Passed: 5, Failed: 1
============================================================
OVERALL STATUS: DEGRADED
Total checks: 36, Passed: 29, Failed: 7
============================================================
```

### Notes

- Endpoint checks return 400 without authentication - this is expected
- To run with authentication: `python manage.py validate_section --all --user=admin`
- The framework is extensible - add new validators by creating new files in `core/validation/`

---

## Future Enhancements

1. Add Discord `/validate` command
2. Add System Health panel to web UI
3. Add AudioValidationAgent for voice marketplace
4. Add KnowledgeValidationAgent for RAG system
5. Add DiscordValidationAgent for bot health
6. Add WorkflowValidationAgent for multi-step workflows
