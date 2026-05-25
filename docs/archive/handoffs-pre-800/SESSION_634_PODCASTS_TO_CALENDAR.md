# Session 634: Podcasts Tab Move + Enhanced Script Modal

**Date:** December 30, 2025
**Previous Session:** 633 (Coordinator Debate Fix + Script Extraction)
**Focus:** Move Podcasts from Autonomous to Calendar tab + Show full 3-agent debate content

---

## Summary

Reorganized UI to group content-related features together and enhanced the Script modal to display the complete 3-agent debate content (~8,000+ chars instead of just the 1,544 char intro).

---

## Changes Made

### 1. Moved Podcasts Sub-Tab to Calendar

**Before:**
```
🤖 Autonomous
  ├── Overview
  ├── Triggers
  ├── Spiders
  ├── Narrative Drift
  └── Podcasts ← was here
```

**After:**
```
📅 Calendar
  ├── Schedule (default)
  └── Podcasts ← moved here

🤖 Autonomous
  ├── Overview
  ├── Triggers
  ├── Spiders
  └── Narrative Drift
```

### 2. Enhanced Script Modal

The Script button now shows complete podcast content:

| Section | Content |
|---------|---------|
| Episode Script | The generated script (1,544 chars) |
| TopicMiner | Trending topic analysis (2,000 chars) |
| Contrarian | Counter-arguments (2,000 chars) |
| Analyst | Performance predictions (2,000 chars) |
| Decision Reasoning | Synthesis of debate (574 chars) |

**Total: ~8,000+ chars** (previously only showed 1,544)

### 3. Fixed Script Display Bug

The podcast_script API was returning `episode.description` (71 chars placeholder) instead of `episode.script` (1,544 chars actual content).

---

## Files Modified

| File | Change |
|------|--------|
| `content_calendar_panel.html` | Added sub-tab nav (Schedule/Podcasts), wrapper divs, podcast include |
| `autonomous_dashboard_panel.html` | Removed Podcasts tab button, include, and JS handling |
| `podcast_studio_panel.html` | Removed Bootstrap tab-pane classes, enhanced Script modal with 3-agent debate cards |
| `core/views_podcast.py` | Fixed to use `episode.script`, added ContentDebate data to response |

---

## API Changes

### `GET /api/podcasts/<episode_id>/script/`

Now returns debate content for ChannelEpisode:

```json
{
  "success": true,
  "episode": {...},
  "script": "Hi — I'm Ava, welcome to AI Tech Weekly...",
  "debate": {
    "topic": "Latest AI Developments...",
    "proposed_by": "AutonomousContentStudioCoordinator",
    "topic_miner": "I ran a fast topic scan...",
    "contrarian": "While the topics are trending...",
    "analyst": "Based on historical performance...",
    "decision_reasoning": "After considering all positions...",
    "consensus_reached": true
  },
  "word_count": 250
}
```

---

## Commits

| Hash | Description |
|------|-------------|
| `30f30a10` | Move Podcasts sub-tab from Autonomous to Calendar |
| `de2c872f` | Fix Script button to show full script, not description |
| `5f4828f2` | Enhanced Script modal with 3-agent debate content |

---

## Testing

Verified:
- ✅ Calendar tab shows Schedule and Podcasts sub-tabs
- ✅ Autonomous tab no longer has Podcasts
- ✅ Sub-tab switching works correctly
- ✅ Script button shows full 1,544 char script
- ✅ 3-agent debate content displays in modal
- ✅ Each agent card is scrollable for long content
- ✅ Decision reasoning shows at bottom

---

## UI Preview

### Script Modal Layout
```
┌─────────────────────────────────────────────────┐
│ 📜 AI Tech Weekly: Latest AI Developments...   │
├─────────────────────────────────────────────────┤
│ 🎤 Episode Script                              │
│ ┌─────────────────────────────────────────────┐│
│ │ Hi — I'm Ava, welcome to AI Tech Weekly... ││
│ └─────────────────────────────────────────────┘│
│                                                 │
│ 💬 3-Agent Debate                              │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│ │TopicMiner │ │Contrarian │ │ Analyst   │     │
│ │   🟢      │ │    🔴     │ │    🟡     │     │
│ │ 2000 chars│ │ 2000 chars│ │ 2000 chars│     │
│ └───────────┘ └───────────┘ └───────────┘     │
│ ┌─────────────────────────────────────────────┐│
│ │ ⚖️ Decision Reasoning (574 chars)          ││
│ └─────────────────────────────────────────────┘│
├─────────────────────────────────────────────────┤
│                    [Close] [Copy Script]        │
└─────────────────────────────────────────────────┘
```

---

## Related Sessions

| Session | Feature |
|---------|---------|
| 633 | Coordinator direct debate fix, script extraction |
| 632 | Generate Now button |
| 631 | Episode Content Viewer modal |
| 630 | Script field added to ChannelEpisode |
| 502 | Original Podcast Studio implementation |
