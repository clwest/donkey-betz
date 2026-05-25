# Session 299: Cumulative Intelligence Pipeline

**Date:** December 1, 2025
**Focus:** Wire research agents to persist results with embeddings for semantic search, enabling cumulative intelligence

## Summary

Implemented the "Cumulative Intelligence Pipeline" - a system where business research (competitor analysis, customer research) is automatically saved to the database with embeddings, enabling:
1. Research results to be linked to projects
2. Semantic search to find relevant research
3. Automatic injection of research insights into image generation prompts
4. UI buttons to create content from research with one click

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│   User Research     │         │  BusinessResearch   │         │  Workflow Engine    │
│   "Analyze AI       │ ──────> │  Result + Embedding │ ──────> │  Image Generation   │
│    content market"  │  Save   │  (Semantic Search)  │  Query  │  + Research Cues    │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
                                          │
                                          │ Link
                                          ▼
                                ┌─────────────────────┐
                                │   CreativeProject   │
                                │   (research_reports │
                                │    FK relation)     │
                                └─────────────────────┘
```

## Files Modified

### Backend - Research Persistence

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added `project` FK and `market_topic` field to BusinessResearchResult |
| `core/agents/business/competitor_analysis_agent.py` | Already had save logic - verified working |
| `core/agents/business/customer_research_agent.py` | Already had save logic - verified working |
| `core/migrations/0059_add_research_project_linking.py` | New migration for project linking |

### Backend - Workflow Engine Integration

| File | Changes |
|------|---------|
| `agents/workflow_orchestration_agent.py` | Added Session 299: Research context injection into image prompts |
| `agents/workflow_orchestration_agent.py` | Added Session 299: Auto-link research to created projects |

### Frontend - UI Actions

| File | Changes |
|------|---------|
| `ai_core/templates/ai_image_studio.html` | Added `sendPrefilledMessage()` method to AIAssistant class |
| `ai_core/templates/ai_image_studio.html` | Added "Next Steps" action buttons to research reports |

## Key Features Implemented

### 1. Research Persistence with Embeddings
- `save_customer_research()` and `save_competitor_analysis()` helper methods
- Auto-extract market topic from query using regex patterns
- Generate embeddings using OpenAI `text-embedding-3-small` model
- Store raw data, pain points, personas, recommendations

### 2. Semantic Search for Research
- `semantic_search()` method using cosine similarity
- `get_research_context_for_prompt()` for prompt injection
- Relevance threshold (0.4) to filter low-quality matches

### 3. Research Context in Image Generation
When generating images, the workflow engine now:
1. Queries stored research using semantic search
2. Extracts customer pain points → design cues (e.g., "trust" → "trustworthy stable")
3. Extracts differentiation needs → visual concepts (e.g., "stand out" → "distinctive unique bold")
4. Adds research-informed modifiers to image prompts

### 4. Project Linking
When a project is created from a workflow:
1. Automatically finds related research by market_topic
2. Links unlinked research reports to the new project
3. Tracks `linked_research_count` in result

### 5. UI Action Buttons
Research reports now show "Next Steps" buttons:
- 📁 Create Project - Creates a new project from research
- 🎨 Create Logos - Research-informed logo generation
- 📺 Create Thumbnails - Research-informed thumbnail generation
- 🏢 Create Brand Identity - Full brand identity package
- 👥 + Add Customer Research - Add customer pain points research
- 🎯 + Add Competitor Analysis - Add competitor analysis research

These buttons auto-fill the chat input and send the request via `sendPrefilledMessage()`.

## Usage Flow

### Step 1: Research the Market
```
User: "Analyze competitors in the AI content generation market"
→ CompetitorAnalysisAgent runs
→ Results saved to BusinessResearchResult with embedding
→ Research report displayed with action buttons
```

### Step 2: Research Customers
```
User: "Research customer pain points for AI content tools"
→ CustomerResearchAgent runs
→ Results saved with embedding
→ Both research reports now in database
```

### Step 3: Create Content (One Click)
```
User clicks: "🎨 Create Logos"
→ Message sent: "Research competitive analysis and create 3 professional logos"
→ Workflow engine queries stored research via semantic search
→ Finds pain points: ["trust", "complexity"] → adds "trustworthy stable, simple approachable"
→ Finds differentiation: ["stand out"] → adds "distinctive unique bold"
→ Creates logos with research-informed prompt
→ Links research reports to created project
```

## Database Changes

### BusinessResearchResult Model Updates

```python
# Link to project (optional - research can exist independently)
project = models.ForeignKey(
    'content.CreativeProject',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='research_reports',
)

# Market/topic for grouping related research
market_topic = models.CharField(
    max_length=200,
    blank=True,
)
```

## Test Scenarios

1. **Research → Persistence**: Run competitor analysis, verify record created in DB
2. **Embedding Generation**: Check that embedding field is populated (1536-dim vector)
3. **Semantic Search**: Query for "AI tools" and verify relevant research returned
4. **Prompt Injection**: Generate logos after research, check logs for "Session 299: Enhanced prompt with research insights"
5. **Project Linking**: Create project from workflow, verify `linked_research_count` > 0
6. **UI Buttons**: Click action button, verify message sent and workflow triggered

## Technical Notes

### Pain Point to Design Cue Mapping
```python
'trust' / 'reliable' → 'trustworthy stable'
'simple' / 'complex' → 'simple approachable'
'expensive' / 'cost' → 'value premium quality'
'confus' / 'overwhelm' → 'clear organized'
```

### Differentiation to Visual Cue Mapping
```python
'stand out' / 'differentiate' → 'distinctive unique bold'
'modern' / 'innovative' → 'modern innovative cutting-edge'
```

## Next Steps

1. **Enhanced Prompt Engineering**: Add more pain point → design cue mappings
2. **Research Dashboard**: UI to view all stored research with filters
3. **Cross-Project Research**: Share research between related projects
4. **Research Expiration**: Implement TTL for outdated research
5. **Research Quality Scoring**: Track which research leads to successful projects

## Migration Command

```bash
python manage.py migrate core 0059_add_research_project_linking
```
