# Session 435: Discord Research Result Formatting + Notification Fixes

**Date:** December 13, 2025
**Status:** Complete
**Focus:** Fix Discord bot research results display + knowledge notification formatting

---

## Summary

Fixed three Discord-related display issues:
1. Research agent results not showing actual content (just "Query: X, Completed in Yms")
2. Knowledge sharing notifications displaying raw JSON instead of formatted text
3. HiveMind conversation topics showing generic "recent insights" instead of meaningful topics

---

## Changes Made

### 1. Research Result Formatting (`core/services/discord_bot.py`)

**Problem:** `/agent-task ResearchAgent "query"` only showed "Query: X, Completed in Yms" without actual search results.

**Root Cause:** Two issues:
- `spider_query` tool returns a **list** directly, but code expected a dict
- `analyze_trends` tool returns a dict with `discussions`/`projects` keys, not `items`/`results`

**Fix (Lines 2813-2843):**
```python
# Handle different data formats from various tools
if isinstance(data, list):
    # spider_query returns a list directly
    items = data
elif isinstance(data, dict):
    # analyze_trends returns dict with 'discussions', 'projects'
    # web_search returns dict with 'items' or 'results'
    items = (
        data.get('discussions', []) or
        data.get('projects', []) or
        data.get('items', []) or
        data.get('results', [])
    )
```

### 2. Knowledge Sharing Notification Format (`core/tasks.py`)

**Problem:** Discord notifications showed raw JSON:
```
{"query": "...", "sources_used": [...], "result_count": 2, "success": true}
```

**Fix (Lines 3027-3070):** Parse JSON and format nicely:
```
Query: "What's trending in AI?"
Sources: analyze_trends, spider_query
Results: 2 items
```

### 3. Conversation Topic Extraction (`core/tasks.py`)

**Problem:** HiveMind conversations showing generic "recent insights" as topic.

**Fix:** Extract meaningful topics from JSON summaries when `knowledge.title` is missing:

- **Lines 4133-4154:** Two-agent conversations
- **Lines 4762-4774:** Panel discussions
- **Lines 6461-6472:** Agent dreams

All now use fallback chain: `title` → `JSON query/topic/insight` → `knowledge_type`

---

## Files Modified

| File | Lines | Change |
|------|-------|--------|
| `core/services/discord_bot.py` | 2813-2843 | Research result data format handling |
| `core/tasks.py` | 3027-3070 | Knowledge sharing notification formatting |
| `core/tasks.py` | 4133-4154 | Two-agent conversation topic extraction |
| `core/tasks.py` | 4762-4774 | Panel discussion topic extraction |
| `core/tasks.py` | 6461-6472 | Dream topic extraction |

---

## Testing

1. **Research Results:** Tested `/agent-task ResearchAgent "AI trends"` - now shows formatted results with clickable links
2. **Knowledge Notifications:** Triggered agent cycle - notifications show formatted text instead of JSON
3. **Conversation Topics:** Agent conversations now display meaningful topics extracted from knowledge summaries

---

## Technical Notes

### Data Format Discovery

Used Django shell to inspect actual return values:
```python
# spider_query returns list directly
>>> search_spider_data("AI")
[{'title': '...', 'url': '...', ...}, ...]

# analyze_trends returns dict with discussions/projects keys
>>> analyze_trends("AI")
{'discussions': [...], 'projects': [...], 'topics': [...]}
```

### Topic Extraction Fallback Chain

```python
# Try title first
topic = knowledge_item.title

# If empty or generic, try JSON summary
if not topic or topic == "recent insights":
    try:
        data = json.loads(knowledge_item.summary)
        topic = data.get('query') or data.get('topic') or data.get('insight', '')[:80]
    except (json.JSONDecodeError, TypeError):
        topic = knowledge_item.summary[:80]

# Final fallback: use knowledge type
if not topic:
    topic = f"{knowledge_item.knowledge_type.replace('_', ' ').title()} from {agent.name}"
```

---

## Web App Sync (`core/views_agent_learning.py`)

Ensured web app displays same full conversation content as Discord:

### 1. AgentConversation Messages - No More Truncation

**Before:** `conv.messages.all()[:10]` - Only first 10 messages returned
**After:** `conv.messages.all().order_by('sequence_number')` - ALL messages returned

### 2. HiveMindSession Messages - Parsed from Synthesis

**Before:** `messages: []` - Empty array, only synthesis_summary shown
**After:** Synthesis text parsed into individual messages

```python
# Parse "AgentName: message" paragraphs from synthesis
paragraphs = re.split(r'\n\n|\n(?=[A-Z][a-zA-Z]+Agent:)', session.synthesis)
for para in paragraphs:
    match = re.match(r'^([A-Z][a-zA-Z]+(?:Agent)?):?\s*(.+)', para, re.DOTALL)
    if match:
        messages_data.append({
            'agent': match.group(1),
            'content': match.group(2).strip(),
            ...
        })
```

### Dream Promotion to Boardroom

Also implemented dream promotion workflow:
1. Found WorkflowAgent's "Agents That Build Agents" prediction dream
2. Promoted to Boardroom with high scores (84.3% composite)
3. Generated 15-message panel discussion with 5 agents
4. Sent full transcript to Discord in multiple messages (bypassing 4096 char limit)

---

## Files Modified (Complete List)

| File | Change |
|------|--------|
| `core/services/discord_bot.py` | Research result data format handling |
| `core/tasks.py` | Knowledge formatting + topic extraction |
| `core/views_agent_learning.py` | Full messages for web app |

---

## Next Session

- Continue Discord-First development (Phase 6 if planned)
- Monitor agent dreams and conversations for quality
- Consider adding more research tools to Discord commands
