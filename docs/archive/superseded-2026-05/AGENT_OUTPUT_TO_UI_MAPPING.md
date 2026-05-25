# Agent Output to UI Mapping

**Created:** Session 760
**Purpose:** Document exactly what each agent returns and where it's displayed in the UI

---

## 1. Agent Output Structure

All 73 agents return `AgentResult` from `core/agents/base_agent.py`:

```python
@dataclass
class AgentResult:
    success: bool                    # Execution status
    message: str                     # Human-readable result text
    data: Dict[str, Any]             # Structured result data
    error: Optional[str]             # Error message (on failure)
    agent_name: str                  # Agent identifier
    execution_time_ms: int           # Duration in milliseconds
    decisions_made: int              # Decision count
    tool_calls: List[Dict]           # Tools invoked
    tokens_used: int                 # Token consumption
    cost: float                      # Execution cost in USD
```

---

## 2. Database Storage

### Primary: `core_agentexecution` (662 records)

| Field | Source | Purpose |
|-------|--------|---------|
| `task` | Input | The task that was requested |
| `status` | AgentResult.success | pending/running/completed/failed |
| `output_data` | AgentResult | Full structured output |
| `tokens_used` | AgentResult | Token count |
| `cost` | AgentResult | Execution cost |
| `execution_time_ms` | AgentResult | Duration |
| `error_message` | AgentResult.error | Error details |

### Secondary: `core_agentmemory` (269 records)

| Field | Source | Purpose |
|-------|--------|---------|
| `title` | Generated from result | Memory title |
| `content` | AgentResult.data | Rich memory content |
| `memory_type` | task/research/creation | Category |
| `valence` | success/failure | Outcome |
| `key_fields_summary` | Extracted | Tools used, task preview |

### Tertiary: `agents_agentcontribution` (226 records)

| Field | Source | Purpose |
|-------|--------|---------|
| `image` | Content FK | Links to ImageHistory |
| `video` | Content FK | Links to VideoHistory |
| `contribution_type` | generation/editing | Type of contribution |

---

## 3. UI Pages That Display Agent Data

### A. AgentsPage (`/agents`) - 8 Tabs

| Tab | Data Source | What's Displayed |
|-----|-------------|------------------|
| **Directory** | `/v1/agents/comprehensive/` | All 73 agents with status, execution count |
| **Activity** | `/recent-activity/` | Real-time execution feed |
| **Learning** | ~~`/agent-learning/activity/`~~ | Removed Session 1009 |
| **Channels** | `/v1/agent-channels/` | Agent communication |
| **Monitoring** | `/v1/agents/monitoring/` | Avg execution time, success rate |
| **Tools** | `/v1/agents/tools/` | Tool definitions, usage stats |
| **Templates** | `/v1/agent-templates/` | Template configurations |
| **Orchestrations** | `/v1/agent-orchestrations/` | Multi-agent workflows |

### B. MemoryPalacePage (`/memory-palace`)

| Section | Data Source | What's Displayed |
|---------|-------------|------------------|
| **Memories** | `/api/memory-palace/agent/{id}/memories/` | Agent memories with content |
| **Clusters** | `/api/memory-palace/clusters/` | Memory groupings |
| **Detail View** | `/api/memory-palace/memory/{id}/` | Full memory with output |

### C. IntelligencePage (`/intelligence`)

| Tab | Data Source | What's Displayed |
|-----|-------------|------------------|
| **Pilots** | `/pilots/` | Running experiments |
| **Opportunities** | `/opportunities/` | Scored opportunities |
| **Gates** | `/gates/` | Quality gates |

### D. HumanPage (`/human`)

| Section | Data Source | What's Displayed |
|---------|-------------|------------------|
| **Agent Grid** | `/v1/agents/list/` | Agent overview cards |
| **Attention Items** | `/human-interface/attention/` | Items needing review |

### E. Dashboard (`/dashboard`)

| Section | Data Source | What's Displayed |
|---------|-------------|------------------|
| **Network Graph** | Aggregated | Active agents, connections |
| **Stats** | Various | Execution counts, success rates |

---

## 4. Agent Output Patterns by Category

### Creation Agents (ImageAgent, VideoAgent, AudioAgent, ThreeDAgent)

**output_data structure:**
```json
{
  "data": {
    "task": "Generate 3 logos",
    "count": 3,
    "images": [
      {
        "image_id": "uuid",
        "file_path": "generated_images/...",
        "image_url": "/media/...",
        "batch_index": 1
      }
    ],
    "original_task": "..."
  },
  "message": "Generated 3 image(s)",
  "result_preview": "Generated 3 image(s)"
}
```

**Displayed On:**
- ContentPage: Generated images grid
- Live Feed: "ImageAgent created 3 images"
- Memory Palace: Memory with image references

### Research Agents (ResearchAgent, CompetitorAnalysisAgent)

**output_data structure:**
```json
{
  "data": {
    "query": "Research AI trends",
    "results": [
      {
        "data": {
          "topics": [{"topic": "ai", "count": 563}]
        },
        "source": "hackernews"
      }
    ]
  },
  "message": "Research completed"
}
```

**Displayed On:**
- Intelligence Page: Research results
- Memory Palace: Research memories

### Content Agents (ContentWriterAgent)

**output_data structure:**
```json
{
  "data": {
    "type": "blog_post",
    "content": "# Blog Title\n\n...",
    "word_count": 1850,
    "seo_score": 85
  },
  "message": "Blog post created"
}
```

**Displayed On:**
- Content Channels Page: Blog listing
- Human Page (Attention): Review items
- Memory Palace: Content memories

### Analysis Agents (TrendAnalysisAgent, OpportunityScoringAgent)

**output_data structure:**
```json
{
  "data": {
    "task": "Analyze trends",
    "tool_results": [
      {
        "tool": "analyze_sector",
        "result": {
          "sector": "tech",
          "highlights": ["..."]
        }
      }
    ]
  }
}
```

**Displayed On:**
- Dashboard: Trend summaries
- Intelligence Page: Analysis results

### Code Agents (CodeGeneratorAgent, FullStackDeveloperAgent)

**output_data structure:**
```json
{
  "data": {},
  "message": "```python\ndef factorial(n):\n    ...\n```"
}
```

**Displayed On:**
- Agent execution modal: Code output
- Memory Palace: Code generation memories

### Orchestration Agents (WorkflowOrchestrationAgent, CampaignOrchestrator)

**output_data structure:**
```json
{
  "data": {
    "workflow_type": "research_and_create",
    "suggested_workflow": [
      {"step": 1, "agent": "ResearchAgent", "task": "..."},
      {"step": 2, "agent": "ContentWriterAgent", "task": "..."}
    ]
  }
}
```

**Displayed On:**
- Agents Page (Orchestrations tab): Workflow results
- Intelligence Page: Pipeline status

---

## 5. Data Flow Summary

```
Agent.execute()
    ↓
AgentResult
    ↓
┌─────────────────────────────────────┐
│   AgentExecution (core_agentexecution)  │
│   - output_data: full structured result │
│   - status, tokens, cost, time          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   AgentMemory (core_agentmemory)       │
│   - content: extracted rich memory     │
│   - key_fields_summary: tools, preview │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   AgentContribution                    │
│   - Links to ImageHistory/VideoHistory │
│   - contribution_type, role            │
└─────────────────────────────────────┘
    ↓
API Endpoints
    ↓
┌─────────────────────────────────────┐
│   Frontend Pages                       │
│   - AgentsPage: 8 tabs                 │
│   - MemoryPalacePage: memories         │
│   - IntelligencePage: pilots           │
│   - Dashboard: stats                   │
└─────────────────────────────────────┘
```

---

## 6. GAPS IDENTIFIED - Data Not Being Displayed

### A. `output_data.data` Details Often Hidden

Many agents return rich data in `output_data.data` but the UI only shows:
- `result_preview` (truncated message)
- Basic stats (tokens, time, cost)

**Missing UI for:**
- Full `images` array with URLs and metadata
- Full `tool_results` with tool outputs
- Full `results` from research with sources

### B. No Dedicated Output Viewer

Currently agent output is shown in:
- Execution modal (basic)
- Memory Palace (processed into memory format)

**Missing:**
- Full JSON output viewer
- Per-agent output formatting
- Image/video preview in output

### C. Tool Calls Not Visualized

`AgentResult.tool_calls` contains valuable info:
```json
[
  {"tool": "search_spider_network", "arguments": {...}},
  {"tool": "generate_content", "arguments": {...}}
]
```

**Currently:** Only shown as "Tools: web_search, generate" in memory summary
**Missing:** Tool call timeline, arguments, individual results

### D. Cost/Token Tracking Not Prominent

Data exists in `AgentExecution`:
- `tokens_used`
- `cost`
- `execution_time_ms`

**Currently:** Shown in monitoring tab aggregate
**Missing:** Per-execution cost breakdown, cost history chart

---

## 7. Recommended Enhancements

1. **Agent Output Detail Modal** - Show full `output_data` with formatting
2. **Tool Call Visualization** - Timeline of tool invocations with results
3. **Image/Video Preview** - For creation agents, show generated assets
4. **Research Results Viewer** - Show spider sources and findings
5. **Cost Dashboard** - Track token/cost usage over time
6. **Orchestration Flow Diagram** - Visualize multi-agent workflows

---

## 8. Quick Reference: Agent → UI Location

| Agent | Primary UI Location | Data Shown |
|-------|---------------------|------------|
| ImageAgent | ContentPage, Live Feed | Generated images |
| VideoAgent | ContentPage, Live Feed | Generated videos |
| AudioAgent | ContentPage | Generated audio |
| ResearchAgent | Intelligence, Memory Palace | Research findings |
| ContentWriterAgent | Content Channels, Human Page | Blog posts |
| TrendAnalysisAgent | Dashboard | Trend summaries |
| CodeGeneratorAgent | Execution modal | Generated code |
| WorkflowOrchestrationAgent | Agents (Orchestrations) | Workflow results |
| StockAnalystAgent | Betting Page | Stock analysis |
| SportsOddsAnalyst | Betting Page | Odds analysis |

---

**Next Steps:** Implement the recommended enhancements to display 100% of agent output data in the UI.
