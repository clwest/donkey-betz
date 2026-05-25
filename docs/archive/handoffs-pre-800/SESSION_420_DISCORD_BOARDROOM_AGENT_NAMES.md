# Session 420: Discord Boardroom + Agent Name Fix + Training Data Spider

**Date:** December 11, 2025
**Status:** Complete

## Summary

This session focused on:
1. Enhancing Discord integration with new channels
2. Fixing GPT-5-mini token issues
3. **Building a Training Data Collection System** from HuggingFace datasets

## Changes Made

### 1. New Discord Channels Added

Updated `core/services/discord_notifications.py`:
- **#agent-learning** (1448819275459465257) - Dedicated channel for knowledge sharing
- **#boardroom** (1448819855557136595) - Strategic decisions and HiveMind consensus

Added new method `send_boardroom_decision()` with:
- Type-specific emojis (📜 policy, 🏗️ architecture, ⚙️ workflow, 🎯 strategy, ✨ feature, 🔄 process)
- Impact-based colors (blue=low, orange=medium, red=high, purple=critical)
- Rich embeds with participant lists

### 2. Automatic Boardroom Notifications

Updated `core/tasks.py` (~line 8080):
- Automatically posts to #boardroom when HiveMind sessions complete
- Calculates impact level based on participant count:
  - 6+ participants = high impact
  - 4-5 participants = medium impact
  - 1-3 participants = low impact

Updated `core/management/commands/force_agent_cycle.py`:
- Added strategic topic detection for boardroom notifications
- Keywords: 'strategy', 'future', 'improve', 'best practice', 'common mistake', 'emerging trend'

### 3. GPT-5-mini Token Fix

**Problem:** Conversations were very short/empty because GPT-5-mini uses `max_completion_tokens` for BOTH internal reasoning AND visible output.

**Solution:** Increased token limits across `force_agent_cycle.py`:

| API Call | Old Limit | New Limit |
|----------|-----------|-----------|
| Dream generation | 500 | 1500 |
| Dream title | 100 | 500 |
| Conversation | 800 | 2000 |
| Knowledge insight | 400 | 1500 |
| Knowledge title | 100 | 500 |

### 4. Agent Name Fix in Conversations

**Problem:** Discord showed "Agent1:", "Agent2:" instead of actual agent names.

**Solution:** Updated conversation prompt in `force_agent_cycle.py` to explicitly instruct GPT-5-mini:
```python
f"IMPORTANT: Use the ACTUAL agent names in the conversation, not 'Agent1' or 'Agent2'.\n"
f"Format each line as: [AgentName]: [message]\n\n"
f"Example format:\n"
f"{agent1.name}: [first message]\n"
f"{agent2.name}: [response]\n"
```

## Testing Results

- 17 Hive Mind Sessions created successfully
- All 5 Discord channels receiving notifications (HTTP 200)
- Conversations now show actual agent names:
  - `LearningCompanion:`
  - `CreativeDirectorAgent:`
  - `VideoAgent:`
  - etc.

## Files Modified

1. `core/services/discord_notifications.py` - Added new channels and boardroom method
2. `core/tasks.py` - Added automatic boardroom notifications after HiveMind synthesis
3. `core/management/commands/force_agent_cycle.py` - Token limit fixes and agent name formatting

---

## Training Data Collection System (NEW)

### What Was Built

A complete automated training data collection system that fetches high-quality conversation data from HuggingFace datasets for agent learning.

### New Files Created

1. **`ai_core/spiders/specialized/discord_training_spider.py`**
   - Fetches conversation data from 14 HuggingFace datasets
   - Quality filtering (URL detection, length checks, topic classification)
   - Supports both public and gated datasets (with `HUGGING_FACE_API` token)

2. **`core/management/commands/fetch_training_data.py`**
   - CLI for manual training data collection
   - Usage: `python manage.py fetch_training_data --save-to-db`

### Datasets Configured (14 Total)

**Tier 1 - Best Public (No auth required):**
- OpenAssistant/oasst1 - Human-AI dialogue
- databricks/databricks-dolly-15k - Human-written instructions
- tatsu-lab/alpaca - Stanford instruction tuning
- HuggingFaceH4/no_robots - Zero AI slop
- Open-Orca/SlimOrca - Cleaned reasoning
- LDJnr/Capybara - Multi-turn conversations

**Tier 2 - Good Public:**
- cognitivecomputations/wizard_vicuna_70k_unfiltered
- teknium/OpenHermes-2.5
- WizardLM/WizardLM_evol_instruct_V2_196k
- Conversational-Reasoning/Topical-Chat
- jondurbin/airoboros-2.2.1

**Tier 3 - Gated (Requires HF token + terms acceptance):**
- lmsys/lmsys-chat-1m
- HuggingFaceH4/ultrachat_200k
- lmsys/chatbot_arena_conversations

### Celery Beat Schedule

Added to `core/celery.py`:
```python
'collect-training-data-daily': {
    'task': 'core.tasks.collect_training_data',
    'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
},
'collect-training-data-weekly-full': {
    'task': 'core.tasks.collect_training_data_full',
    'schedule': crontab(day_of_week=0, hour=2, minute=30),  # Sunday 2:30 AM
},
```

### Results

- **290 conversations fetched** per run
- **272 high quality** (94% quality rate)
- **Topics:** business, AI, creative, programming, tech
- **50 records saved** per daily run, **200 per weekly run**
- Spider Data Bridge automatically creates learning entries for agents

### Usage

```bash
# Manual fetch
python manage.py fetch_training_data --dry-run
python manage.py fetch_training_data --save-to-db

# Or via Celery
from core.tasks import collect_training_data
collect_training_data.delay()
```

## Next Session Recommendations

1. Monitor Discord channels for any edge cases with agent names
2. Consider adding more strategic topic keywords for boardroom detection
3. Accept LMSYS terms on HuggingFace to unlock 1M+ conversation dataset
4. Add unit tests for training data spider
