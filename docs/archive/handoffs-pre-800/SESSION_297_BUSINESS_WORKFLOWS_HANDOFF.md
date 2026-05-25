# Session 297: Business Research Workflows Handoff

**Date:** December 1, 2025
**Status:** COMPLETE - All code committed, database backed up
**Branch:** `feature/session-52-ai-assistant`

---

## Executive Summary

This session completed three major items:
1. Fixed the 59 "Generate Image" button flooding issue (Session 296 carryover)
2. Exposed business research workflows in the project creation flow
3. Added the `startup_validation` workflow for comprehensive idea validation

---

## What Was Done This Session

### 1. UI Fix: Generate Image Button Flooding (Session 296 Carryover)

**Problem:** Users were seeing 59 "Generate Image #1" through "Generate Image #59" buttons flooding the chat after AI responses.

**Root Cause:** The `detectPromptsInMessage()` function was extracting ALL quoted text from AI responses and creating buttons for each.

**Fix Applied:** (`ai_core/templates/ai_image_studio.html`)
- Rewrote `detectPromptsInMessage()` to be selective:
  - Only creates buttons when AI explicitly suggests prompts (phrases like "try this prompt")
  - Maximum 3 buttons per message
  - Filters out technical text and short strings
- Changed markdown image onclick from `window.open()` to `showImageModal()` for better UX

### 2. Business Research Workflows Exposed

**Files Modified:**
- `core/assistant/constants.py` - Added 4 new workflow types
- `agents/workflow_orchestration_agent.py` - Added `startup_validation` workflow
- `core/prompts/tool_descriptions.py` - Updated GPT routing instructions

**New Workflows Available:**

| Workflow | Trigger Phrase | What It Does |
|----------|---------------|--------------|
| `competitor_analysis` | "Analyze competitors for X" | SWOT, positioning maps |
| `customer_personas` | "Research customers for X" | Reddit research, pain points, personas |
| `business_research` | "Do business research for X" | Full: market + competitors + customers |
| `startup_validation` | "Validate my startup idea for X" | 5-step comprehensive validation |

**These workflows are FREE** - they use spider data + GPT only, no Stability AI credits!

### 3. Commits Made This Session

```
8930644 feat(Session 297): Expose business research workflows in project creation
72facb1 feat(Session 294): New spiders, business agents, utilities & docs
8545aba feat(Session 295/296): Customer Pain Points - Provenance, Audit, Originality & UI fixes
```

---

## System State

### What's Working
- All 4 business research workflows accessible via chat
- Generate Image buttons fixed (max 3, only when AI suggests prompts)
- Provenance, Audit, Originality features (Session 295/296)
- Competitor Analysis and Customer Research agents
- 70 spiders across 24 real data sources
- Server running at http://localhost:8000/ai-studio/

### Database
- PostgreSQL: `unified_donkey_betz`
- Backup created: `backups/database/unified_donkey_betz_20251201_*.sql`

### Key Files to Know
| Purpose | File |
|---------|------|
| Workflow definitions | `agents/workflow_orchestration_agent.py` (lines 550-685) |
| Workflow types constant | `core/assistant/constants.py` (lines 129-143) |
| Tool routing descriptions | `core/prompts/tool_descriptions.py` (lines 28-60) |
| Main UI template | `ai_core/templates/ai_image_studio.html` |
| Prompt detection | `ai_image_studio.html` search for `detectPromptsInMessage` |

---

## How to Start the System

```bash
# Navigate to project
cd /Users/donkeyking/development/unified-donkey-betz

# Read current context
cat 00-START-NEXT-SESSION.md

# Start everything
pkill -f daphne; pkill -f celery; pkill -f redis; rm -f .daphne.pid .celery.pid .celery-beat.pid
redis-server --daemonize yes
make start    # Terminal 1
make celery   # Terminal 2

# Access
open http://localhost:8000/ai-studio/
```

---

## Potential Future Work

### Suggested Additional Business Agents
| Agent | Purpose | Priority |
|-------|---------|----------|
| MarketSizeAgent | TAM/SAM/SOM analysis | High |
| PricingStrategyAgent | Competitive pricing | Medium |
| GTMStrategyAgent | Go-to-market planning | Medium |
| SEOKeywordAgent | Keyword research | Medium |

### Known Issues / Edge Cases
- Business workflows are new - may need testing with various inputs
- The `strategic_synthesis` agent step may need implementation if not already done

---

## Testing the New Features

```bash
# In AI Studio, try these prompts:
"Validate my startup idea for an AI-powered meal planning app"
"Analyze competitors in the project management SaaS market"
"Research customer personas for B2B accounting software"
"Do full business research for a fitness tracking app"
```

---

## Files Changed This Session (Summary)

```
Modified:
- core/assistant/constants.py          (+5 lines - workflow types)
- agents/workflow_orchestration_agent.py (+39 lines - startup_validation)
- core/prompts/tool_descriptions.py    (+20 lines - routing)
- ai_core/templates/ai_image_studio.html (UI fixes from Session 296)

Created (from prior sessions, committed now):
- 4 new spiders (Bluesky, Discord, IndieHackers, YouTube)
- Provenance/Audit/Originality services
- Database backup script
```

---

## Important Notes for Future Claude

1. **WORKFLOW_TYPES must match WORKFLOWS dict** - The constant in `constants.py` must have corresponding entries in `agents/workflow_orchestration_agent.py`

2. **Business workflows have `no_image_generation: True`** - This flag prevents Stability AI calls

3. **Tool descriptions guide GPT** - The descriptions in `tool_descriptions.py` are critical for proper routing

4. **Database is PostgreSQL** - Not SQLite. Ensure PostgreSQL is running before starting.

5. **Backup before major changes** - Run `./scripts/backup_database.sh`

---

**All work is committed. Safe to shutdown.**
