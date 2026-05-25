# Session 742: Human Page Data Display Enhancement

**Date:** January 10, 2026
**Focus:** Human Interface Layer - Display Hidden Data

## Summary

Deep dive into the Human page revealed significant data gaps between what's available in the model/API and what's displayed on the frontend. This session fixed those gaps by exposing rich payload data and adding visual improvements.

## Problem Identified

The HumanAttentionItem model contains rich data that was NOT being displayed:

| Field | Status Before |
|-------|---------------|
| `payload` (rich structured data) | Stored but mostly ignored |
| `source_id` | Not in API response |
| `impact_estimate` | Not in API response |
| `expires_at` | Not in API response |
| `deferred_until` | Not in API response |
| `item_type` | In API but not prominently displayed |
| `priority_score` | In API but not displayed |

### Payload Data Examples (was hidden)

| Source Type | Rich Payload Data Ignored |
|-------------|---------------------------|
| `arbitrage_detection` | profit_pct, stake_away, stake_home, markets, game_time, rating, home/away teams |
| `betting_monitor` | profit_percentage, expires_in_hours, suggested_actions |
| `pilot_system` | pilot_id, accuracy |
| `monitoring` | spike_percentage, concurrent_executions |
| `content_pipeline` | post_count, quality_score |
| `spider_network` | spider name, duplicate_rate |

## Changes Made

### 1. API Response Enhancement

**File:** `core/services/human_interface_service.py`

Added missing fields to the attention item response:
- `source_id` - Link to original source
- `impact_estimate` - Risk/impact assessment
- `expires_at` - Item expiration timestamp
- `deferred_until` - For deferred items
- `ml_confidence` and `ml_recommendation` at top level

### 2. Frontend TypeScript Interface

**File:** `frontend/src/pages/HumanPage.tsx`

Updated `AttentionItem` interface with new fields:
- `source_id: string`
- `impact_estimate: string | null`
- `deferred_until: string | null`

### 3. Item Type Configuration

Added `ITEM_TYPE_CONFIG` for visual differentiation by item type:
- `arbitrage` - Green with DollarSign icon
- `alert` - Red with AlertTriangle icon
- `approval` - Amber with CheckCircle icon
- `review` - Purple with FileText icon
- `insight` - Cyan with Lightbulb icon
- `milestone` - Primary with Target icon
- `decision` - Orange with Zap icon
- `opportunity` - Green with Sparkles icon

### 4. PayloadDisplay Component

**NEW Component:** `PayloadDisplay({ item })`

Renders rich, type-specific payload data:

**Arbitrage items show:**
- Profit percentage with green highlight
- Rating (HOT shows in red with pulse animation)
- Markets (FanDuel, DraftKings badges)
- Matchup (Away @ Home teams)
- Game time
- Stake amounts for each team
- Suggested actions list

**Pilot/Experiment items show:**
- Pilot ID
- Accuracy percentage
- Improvement percentage
- Target percentage

**Alert items show:**
- Spike percentage (red)
- Concurrent executions

**Review items show:**
- Post count
- Quality score

**Insight items show:**
- Spider name
- Duplicate rate

### 5. Enhanced Decision Modal

- Added item type badge in header (color-coded with icon)
- Added meta bar showing priority score, expiration, impact estimate, and creation date
- Integrated PayloadDisplay component to show rich payload data
- Larger close button for better UX

### 6. Enhanced List View

- Item type icon instead of generic Activity icon
- Item type badge in metadata row
- For arbitrage items:
  - Profit percentage shown inline with title
  - "HOT" badge with pulse animation for hot opportunities

## Data Statistics

Before this session:
- **66 total attention items** (62 pending)
- **56 arbitrage opportunities** with rich betting data NOT displayed
- **0 feedback records** - users weren't making decisions

Now users can see:
- Full profit percentages on arbitrage opportunities
- Markets (FanDuel/DraftKings) for each opportunity
- Game times and matchups
- Suggested betting actions
- All other rich payload data by type

## Files Changed

```
core/services/human_interface_service.py   # +7 fields in API response
frontend/src/pages/HumanPage.tsx           # +210 lines (PayloadDisplay, configs, badges)
```

## Visual Improvements

| Before | After |
|--------|-------|
| Generic Activity icon for all items | Color-coded icons by item type |
| No payload data visible | Rich, type-specific payload rendering |
| No priority score shown | Priority score in meta bar |
| No expiration shown | Expiration timestamp when available |
| No item type differentiation | Color-coded badges with labels |
| Arbitrage profit hidden in payload | Profit % shown inline with title |

## Part 2: Clickable Navigation Audit & Fixes

After initial data display improvements, an audit of all 153 attention items revealed that many items lacked proper navigation links. The audit found 11 unique source_type/item_type combinations:

| Source Type | Item Type | Count | Navigation Added |
|-------------|-----------|-------|------------------|
| `arbitrage_detection` | `arbitrage` | 143 | → `/betting` |
| `betting_monitor` | `arbitrage` | 1 | → `/betting` |
| `content:blog` | `review` | 1 | → `/blog/{id}` |
| `content_pipeline` | `review` | 1 | → `/blog/{id}` (already worked) |
| `experiment_tracker` | `milestone` | 1 | → `/intelligence` |
| `pilot_system` | `approval` | 1 | → `/intelligence` |
| `spider:hackernews` | `insight` | 1 | → `/spiders` |
| `spider:yahoo_finance` | `insight` | 1 | → `/spiders` |
| `spider_network` | `insight` | 1 | → `/spiders` |
| `monitoring` | `alert` | 1 | → `/body-health` |
| `system_alert:health_check` | `alert` | 1 | → `/body-health` |

### Changes Made (Part 2)

#### 1. Pilot/Milestone Items → `/intelligence`
- Pilot ID is now clickable, linking to Intelligence Dashboard
- Added "View in Intelligence Dashboard" quick action link

#### 2. Spider/Insight Items → `/spiders`
- Spider name is now clickable, linking to Spider Integration page
- Added data preview for spider alerts
- Added "View Spider Integration" quick action link

#### 3. Arbitrage Items → `/betting`
- Added "View Betting Dashboard" quick action link in payload display

#### 4. Alert Items → `/body-health`
- Enhanced to show agents/spiders/capacity fields for system health checks
- Added "View Body Health Dashboard" quick action link

#### 5. Review Items → `/content-channels`
- Added "View Content Channels" quick action link
- Handles both blog_ids arrays and single content_id

#### 6. Fixed Orphaned Data
- `content:blog` review item had placeholder `blog-001` ID
- Updated to link to real SelfBlog entry: `b4b06092-c25c-4cf0-a028-6ac5628c632b`

### New BlogViewerPage

**File:** `frontend/src/pages/BlogViewerPage.tsx` (NEW - ~200 lines)

Full blog content viewer accessible at `/blog/:blogId`:
- Header with title, meta description, word count, tone
- Tags display
- Intro, sections, conclusion
- Stats snapshot at time of writing
- Action buttons: Approve for Publishing, Needs Revision

### Files Changed (Part 2)

```
frontend/src/pages/HumanPage.tsx           # +80 lines (navigation links in PayloadDisplay)
frontend/src/pages/BlogViewerPage.tsx      # NEW (~200 lines)
frontend/src/App.tsx                       # +2 lines (blog route)
```

### Summary of All Navigation Links

| Item Type | Primary Link | Quick Action |
|-----------|--------------|--------------|
| `arbitrage` | N/A | View Betting Dashboard |
| `approval` | Pilot ID → /intelligence | View in Intelligence Dashboard |
| `milestone` | Pilot ID → /intelligence | View in Intelligence Dashboard |
| `alert` | N/A | View Body Health Dashboard |
| `review` | Blog titles → /blog/{id} | View Content Channels |
| `insight` | Spider name → /spiders | View Spider Integration |

#### 7. Fixed Empty Arbitrage IDs (143 items)

All 143 `arbitrage_detection` items had empty `payload.id` fields. Fixed by setting:
- `payload.id` = attention item's own UUID
- `source_id` = attention item's own UUID

This ensures all items have consistent, linkable identifiers.

## Final Statistics

| Metric | Value |
|--------|-------|
| Total attention items | 153 |
| Item types with navigation | 11/11 (100%) |
| Orphaned items fixed | 2 (content:blog, arbitrage IDs) |
| New pages created | 1 (BlogViewerPage) |

## Next Steps

- Consider adding filtering by item_type (not just urgency)
- Add bulk actions for similar items (approve all low-risk)
- Connect to real-time WebSocket updates for arbitrage expiration countdown
- Add sound/visual notification for HOT arbitrage opportunities
