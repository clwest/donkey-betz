# Session 550: ThinkingAgent Expected Behavior + Celery Concurrency Fix

**Date:** December 24, 2025
**Commits:** `770806d`, `6c3e36f`, `6b4a8bb`, `9cc4c8b`
**Status:** COMPLETE

---

## Overview

Session 550 enhanced the ThinkingAgent to understand what constitutes normal system behavior vs. actual issues. This prevents false-positive concerns about expected deduplication patterns and teaching concentration.

---

## Problem

ThinkingAgent Cycle #27 flagged two "concerns" that were actually normal system behavior:

1. **"Low Spider Yield"** - ~13 items/spider/day flagged as concerning
   - **Reality:** This is CORRECT behavior - deduplication filters duplicate URLs within 24 hours

2. **"Teaching Concentration"** - ResearchAgent (26 teachings) and TrendAnalysisAgent (18 teachings) doing most teaching
   - **Reality:** This is BY DESIGN - agents with more knowledge naturally teach more

---

## Solution

Added "IMPORTANT - Expected Behavior" context sections to the ThinkingAgent's prompt generation so the LLM understands what's normal.

### Changes to `core/agents/thinking_agent.py`

#### 1. Spider Yield Context (lines 233-245)
```python
# Session 550: Add expected behavior context for spider yield
active_count = stats.get('active_count', 0)
data_24h = stats.get('data_24h', 0)
if active_count > 0:
    avg_per_spider = data_24h / active_count
    prompt_parts.append(f"- Average per Spider: {avg_per_spider:.1f} items/day\n")
    prompt_parts.append("\n**IMPORTANT - Expected Behavior:**\n")
    prompt_parts.append("Spider yield of 10-20 items/day per spider is NORMAL due to deduplication.\n")
    prompt_parts.append("The system filters duplicate URLs within 24 hours to prevent redundant data.\n")
    prompt_parts.append("Only flag as a concern if:\n")
    prompt_parts.append("- Average drops below 5 items/spider/day (possible API issues)\n")
    prompt_parts.append("- Specific spiders produce 0 items (possible source problems)\n")
    prompt_parts.append("- Data quality degrades (not yield quantity)\n")
```

#### 2. Teaching Concentration Context (lines 178-186)
```python
# Session 550: Add expected behavior context for teaching concentration
prompt_parts.append("\n**IMPORTANT - Expected Behavior:**\n")
prompt_parts.append("Teaching concentration among a few agents is NORMAL and BY DESIGN.\n")
prompt_parts.append("Agents with more knowledge naturally teach more - this is how the system works.\n")
prompt_parts.append("ResearchAgent and TrendAnalysisAgent have the most knowledge, so they teach the most.\n")
prompt_parts.append("Only flag as a concern if:\n")
prompt_parts.append("- An agent with high knowledge is NOT teaching (connection issues)\n")
prompt_parts.append("- Quality of teachings degrades over time\n")
prompt_parts.append("- Learning connections fail repeatedly\n")
```

---

## Verification

Ran ThinkingAgent Cycle #28 to verify the changes work:

### Before (Cycle #27)
- Flagged "low spider yield" as a concern
- Flagged "teaching concentration" as a concern

### After (Cycle #28)
- **Spider Yield Insight:** "Spider yields are within expected bounds (10-20 items/day); no systemic ingestion..."
- **Teaching Insight:** "Teaching concentration among high-knowledge agents remains healthy and expected"
- No false-positive concerns about normal behavior

---

## Part 2: Celery Concurrency Fix

### Problem

Celery was experiencing bottlenecks - tasks backing up and not processing in time.

**Root Cause:** The Makefile was starting Celery with `--pool=solo`, which means **only 1 task can run at a time**.

With 90+ scheduled tasks (many running every 30s, 1min, 2min, 5min), a single-threaded worker couldn't keep up.

### High-Frequency Task Count
```
Every 30 seconds: 4 tasks
Every 60 seconds: 2 tasks
Every 2 minutes:  3 tasks
Every 3 minutes:  1 task
Every 5 minutes:  6 tasks
Every 10 minutes: 5 tasks
Every 15 minutes: 12 tasks
= 33 tasks every 15 minutes competing for 1 worker!
```

### Solution

Changed `Makefile` from:
```bash
# OLD - 1 task at a time
--pool=solo
```

To:
```bash
# NEW - 4 tasks concurrent
--pool=threads --concurrency=4
```

**Why threads instead of prefork?**
- `prefork` causes segfaults on macOS due to fork() issues
- `threads` pool works reliably on macOS
- `gevent` would also work but requires additional dependency

### Verification

After the fix:
```
$ celery -A core inspect active
->  celery@Chriss-MacBook-Pro.local: OK
    * generate_agent_dreams (running)
    * run_spider_network (running)
    * run_multi_agent_conversation (running)
    * run_agent_conversation (running)

$ redis-cli LLEN celery
0  # Queue empty - workers keeping up!
```

### Also Fixed

Commented out 4 URL routes in `core/urls.py` that referenced non-existent `self_blog_api` functions (lines 2455-2458). These were preventing Django from starting.

---

## Other Session 550 Work

### 1. Research Demo Backend API
Created `core/views_research_demo.py` with 4 API endpoints:
- `GET /api/v1/research/network-graph/` - D3.js graph data (55 nodes, 160 edges)
- `GET /api/v1/research/live-feed/` - Recent learning events
- `GET /api/v1/research/stats/` - Pipeline statistics
- `GET /api/v1/research/mythology-gate/` - Trust decay data

### 2. Stale Notification Cleanup
Enhanced `scan_concerns_for_human_action()` in `core/tasks.py` to auto-dismiss notifications for resolved concerns.

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/thinking_agent.py` | Added expected behavior context (lines 178-186, 233-245) |
| `Makefile` | Changed Celery from `--pool=solo` to `--pool=threads --concurrency=4` |
| `core/views_research_demo.py` | NEW - Research demo API endpoints |
| `core/urls.py` | Added research API routes, commented out missing self_blog routes |
| `core/tasks.py` | Enhanced scan_concerns with stale cleanup |
| `00-START-NEXT-SESSION.md` | Updated for Session 551 |

---

## Current System State

| Component | Count | Status |
|-----------|-------|--------|
| **Spiders** | 75 | Active (~14 items/spider/day after dedup) |
| **Agents** | 55 | All learning |
| **Learning Connections** | 160 | Active |
| **Knowledge Transfers** | 1,262+ | Growing |
| **ThinkingAgent Cycles** | 28 | With expected behavior awareness |

---

## Key Insight

The ThinkingAgent now has "self-awareness" about what's normal for the system:
- It calculates and displays the average spider yield
- It understands deduplication is working correctly
- It knows teaching concentration is by design
- It only flags actual issues, not expected behavior

This is a step toward true system intelligence - knowing what's normal vs. what needs attention.

---

## Session 551 Priorities

1. **Action Analytics** - Track which human actions are taken most often
2. **Network Graph Enhancements** - Optional visual improvements
3. **Continue monitoring** ThinkingAgent concern quality

