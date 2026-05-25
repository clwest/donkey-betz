# Session 312: Dynamic Reddit Search Implementation

**Date:** December 2, 2025
**Focus:** Enabling agents to search ANY Reddit subreddit in real-time

---

## Problem Solved

The `RedditSpider` was hardcoded to only cache 15 subreddits from a fixed list, with a `[:3]` limit per category that further reduced it. This meant:

- Agents couldn't search industry-specific subreddits (r/podcasting, r/coffee, r/photography)
- Business research was limited to generic subs, missing r/smallbusiness, r/SaaS, r/marketing
- CustomerResearchAgent's system prompt mentioned subreddits that weren't actually searchable

## Solution Implemented

Added a new `reddit_search` tool to both `CustomerResearchAgent` and `ResearchAgent` that enables:

1. **Dynamic subreddit targeting** - Search ANY subreddit, not just cached ones
2. **Subreddit combining** - Use `+` to search multiple: `"SaaS+startups+indiehackers"`
3. **Dual-mode operation**:
   - Primary: Uses `RedditSearchTool` (PRAW) if API credentials configured
   - Fallback: Uses public Reddit JSON API (no auth required)

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/business/customer_research_agent.py` | Added `reddit_search` tool, handler, public JSON fallback |
| `core/agents/research_agent.py` | Added `reddit_search` tool, handler, public JSON fallback |

## New Tool: `reddit_search`

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | (required) | Search query |
| `subreddits` | string | `"all"` | Subreddit(s) joined with `+` |
| `limit` | int | 25 | Max results |
| `sort` | string | `"relevance"` | relevance, hot, top, new |
| `time_filter` | string | `"month"` | hour, day, week, month, year, all |

### Usage Examples

```python
# Single subreddit
reddit_search(query="hosting frustrations", subreddits="podcasting")

# Multiple subreddits
reddit_search(query="need better tools", subreddits="smallbusiness+Entrepreneur+startups")

# All of Reddit
reddit_search(query="AI writing assistant", subreddits="all")
```

## How It Works

### 1. Tool is Called by GPT

When the agent's GPT decides to search Reddit, it calls `reddit_search` with target subreddits.

### 2. Handler Checks for PRAW

```python
from core.tools import ToolRegistry
reddit_tool = ToolRegistry.get_tool('reddit_api')

if reddit_tool and reddit_tool.is_configured:
    # Use PRAW with full API access
    result = reddit_tool.execute(...)
```

### 3. Falls Back to Public JSON

If PRAW isn't configured (no `REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET`):

```python
url = f"https://www.reddit.com/r/{subreddits}/search.json"
response = requests.get(url, headers=headers, params=params)
```

The public JSON API works without authentication but has stricter rate limits.

## Environment Variables (Optional)

For full API access, set these in `.env`:

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DonkeyBetz/1.0  # optional
```

Without these, the public JSON fallback is used automatically.

## Integration with Agent Flow

### CustomerResearchAgent

The system prompt now guides GPT to:
1. Use `spider_query` for cached community data
2. Use `reddit_search` for industry-specific subreddits
3. Both feed into `analyze_pain_points` for synthesis

Example research flow:
```
1. get_prior_research("coffee products")
2. refresh_spider_data()
3. spider_query("coffee frustrations")  # Cached data
4. reddit_search("coffee problems", subreddits="coffee+barista+espresso")  # Live search
5. analyze_pain_points(gathered_discussions)
6. build_persona(...)
```

### ResearchAgent

Similar pattern for general research tasks.

## Subreddit Recommendations by Market

| Market | Subreddits |
|--------|------------|
| Podcasting | `podcasting+podcasts+audioengineering` |
| Coffee | `coffee+barista+espresso+roasting` |
| SaaS | `SaaS+startups+indiehackers+EntrepreneurRideAlong` |
| Fitness | `fitness+running+bodybuilding+loseit` |
| Productivity | `productivity+getdisciplined+ADHD+bulletjournal` |
| Ecommerce | `ecommerce+shopify+dropship+FulfillmentByAmazon` |
| Photography | `photography+photocritique+AskPhotography` |

## Rate Limiting

### With PRAW (API Credentials)
- 60 requests per minute
- Better for high-volume research

### Public JSON (No Auth)
- ~10 requests per minute before 429 errors
- Fine for occasional research
- 0.5s delays between requests recommended

## Testing

### Quick Test (Django Shell)

```python
from core.agents.business.customer_research_agent import CustomerResearchAgent

agent = CustomerResearchAgent()
result = agent._reddit_dynamic_search(
    query="podcast hosting frustrated",
    subreddits="podcasting",
    limit=5
)
print(f"Success: {result.get('success')}")
print(f"Results: {len(result.get('data', {}).get('results', []))}")
```

### Test via Agent

```python
agent = CustomerResearchAgent()
result = agent.execute(
    task="Research customer pain points for podcast hosting tools",
    context={},
    scifi_context={},
    spider_context={}
)
print(result.message)
```

## What's Still Using Cached Spider Data

The `spider_query` tool still uses the original `RedditSpider` cached data. This is useful for:
- Quick lookups without hitting Reddit's API
- Background trend analysis
- Historical data

The new `reddit_search` is for **targeted, real-time** subreddit queries.

## Future Improvements

1. **Subreddit Discovery** - Auto-suggest relevant subreddits based on query
2. **Comment Search** - Currently only searches posts, could add comment depth
3. **Caching Layer** - Cache dynamic search results to reduce API calls
4. **Rate Limit Pooling** - Share rate limits across agents

---

## Summary

Agents can now search ANY Reddit subreddit dynamically, unlocking industry-specific customer research that wasn't possible with the hardcoded spider list. The dual-mode approach (PRAW + public JSON fallback) ensures it works with or without API credentials.
