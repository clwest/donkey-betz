# UI Audit - Session 659

**Date:** January 1, 2026
**Template:** `ai_core/templates/ai_image_studio.html`
**Size:** 80,747 lines
**API Endpoints Used:** ~335 unique patterns

---

## Executive Summary

The UI has grown organically over 600+ sessions into a massive single-file template with:
- **29 Main Tabs** (top-level navigation)
- **60+ Sub-tabs** (nested within main tabs)
- **335 API endpoints** referenced
- **Multiple WebSocket connections** for real-time updates

### Key Issues Identified
1. **Redundancy:** Multiple tabs show similar data (Trending vs Intelligence Hub vs Spiders)
2. **Missing Features:** New Session 658 Decision Promoter not in UI
3. **Stale Data:** Some sections reference deprecated endpoints
4. **Overwhelming:** 29 tabs is too many for practical navigation

---

## Main Tabs Inventory (29 Total)

### Category: Content Creation (8 tabs)
| # | Tab ID | Title | Sub-tabs | Status |
|---|--------|-------|----------|--------|
| 1 | `assistant` | AI Assistant - Voice & Text | 0 | ✅ Active |
| 2 | `content-studio` | Content Studio | 0 | ✅ Active |
| 3 | `images` | AI Image Generation | 10 | ✅ Active |
| 4 | `character-training` | Character Training | 4 | ✅ Active |
| 5 | `video` | AI Video Generation | 7 | ✅ Active |
| 6 | `audio` | AI Audio Generation | 5 | ✅ Active |
| 7 | `upload` | Upload Content | 0 | ✅ Active |
| 8 | `voices` | Voice Marketplace | 0 | ⚠️ Limited |

### Category: Intelligence & Monitoring (7 tabs)
| # | Tab ID | Title | Sub-tabs | Status |
|---|--------|-------|----------|--------|
| 9 | `intelligence-command-center` | Intelligence Command Center | 6 | ✅ Active |
| 10 | `trending` | Intelligence Hub (Spiders) | 8 | ⚠️ Redundant |
| 11 | `agents` | Agent Collaboration | 8 | ✅ Active |
| 12 | `autonomous` | Autonomous Systems | 0 | ✅ Active |
| 13 | `agent-performance` | Agent Performance | 0 | ⚠️ Redundant |
| 14 | `analytics` | Analytics & Performance | 0 | ✅ Active |
| 15 | `research-demo` | Research Demo | 10 | ⚠️ Demo Only |

### Category: Business & Ops (7 tabs)
| # | Tab ID | Title | Sub-tabs | Status |
|---|--------|-------|----------|--------|
| 16 | `betting` | Betting Dashboard | 0 | ✅ Active |
| 17 | `opportunities` | Opportunities | 0 | ✅ Active |
| 18 | `content-calendar` | Content Calendar | 0 | ⚠️ Limited |
| 19 | `distribution` | Smart Distribution | 0 | ⚠️ Limited |
| 20 | `marketplace` | Workflow Marketplace | 0 | ❌ Unused |
| 21 | `legal-assistant` | Legal Assistant | 0 | ✅ Active |
| 22 | `leadership` | Co-Leadership | 0 | ❌ Hidden |

### Category: Organization & Settings (7 tabs)
| # | Tab ID | Title | Sub-tabs | Status |
|---|--------|-------|----------|--------|
| 23 | `all-gallery` | All Gallery | 0 | ✅ Active |
| 24 | `sessions` | Sessions | 0 | ✅ Active |
| 25 | `portfolio` | Portfolio | 0 | ⚠️ Limited |
| 26 | `preferences` | Preferences | 6 | ✅ Active |
| 27 | `projects` | Projects | 0 | ✅ Active |
| 28 | `collaborate` | Collaboration | 0 | ❌ Hidden |
| 29 | `teams` | Teams | 0 | ❌ Hidden |

---

## Intelligence Command Center (ICC) - Sub-tabs Detail

This is the main operational dashboard with 6 sub-tabs:

| Sub-tab | ID | Purpose | Data Source | Status |
|---------|-----|---------|-------------|--------|
| **Gates** | `icc-gates` | Pilot readiness gates | `/api/pilot-gates/` | ✅ Working |
| **Pilots** | `icc-pilots` | Running experiments | `/api/pilots/` | ✅ Working |
| **Experiments** | `icc-experiments` | Experiment tracking | `/api/experiments/` | ✅ Working |
| **Learning** | `icc-learning` | Learning dashboard | `/api/learning/dashboard/` | ✅ Working |
| **Activity** | `icc-activity` | Recent activity | WebSocket | ⚠️ Check WS |
| **Governance** | `icc-governance` | Decision governance | **MISSING API** | ❌ Needs Work |

### ICC Governance - MISSING FEATURE
Session 658 added AI Decision Promoter but the ICC Governance sub-tab doesn't display:
- Total decisions (977)
- Canonical decisions (884 / 90.5%)
- AI-promoted count (754)
- Remaining drafts (79)

**Recommendation:** Add governance stats API and display cards.

---

## Agents Tab - Sub-tabs Detail (8 sub-tabs)

| Sub-tab | ID | Purpose | Data Source | Status |
|---------|-----|---------|-------------|--------|
| **Overview** | `agents-overview` | Agent list & stats | `/api/agents/` | ✅ Working |
| **Profile** | `agents-profile` | Individual agent details | `/api/agents/{id}/` | ✅ Working |
| **Social** | `agents-social` | Conversations & Dreams | `/api/agent-conversations/` | ✅ Working |
| **Intelligence** | `agents-intelligence` | Agent knowledge | `/api/agent-knowledge/` | ✅ Working |
| **Growth** | `agents-growth` | XP & Evolution | `/api/agents/evolution/` | ⚠️ Limited |
| **Memory** | `agents-memory` | Agent memories | `/api/agent-memories/` | ✅ Working |
| **Workflows** | `agents-workflows` | Agent workflows | `/api/workflows/` | ⚠️ Limited |
| **Quarantine** | `agents-quarantine` | Problematic agents | N/A | ❌ Empty |

---

## Trending/Intelligence Hub - Sub-tabs (8 sub-tabs)

| Sub-tab | ID | Purpose | Redundant With |
|---------|-----|---------|----------------|
| **Trending** | `intel-trending` | Trending topics | ICC Activity |
| **Markets** | `intel-markets` | Market data | Betting tab |
| **Opportunities** | `intel-opportunities` | Opportunities | Opportunities tab |
| **Spiders** | `intel-spiders` | Spider status | ICC (spiders shown there too) |
| **Feed** | `intel-feed` | Data feed | ICC Activity |
| **Knowledge** | `intel-knowledge` | Knowledge base | Agents Intelligence |
| **Timeline** | `intel-timeline` | Event timeline | ICC Activity |
| **Documents** | `intel-documents` | Documents | Separate feature |

**Recommendation:** Consolidate with ICC or remove redundant sub-tabs.

---

## Identified Redundancies

### 1. Spider Data Displayed In Multiple Places
- `intelligence-command-center` → Shows spider stats
- `trending` → `intel-spiders` sub-tab
- `research-demo` → Shows spider data in graphs

### 2. Agent Activity In Multiple Places
- `agents` tab → Full agent management
- `agent-performance` tab → Agent metrics
- `intelligence-command-center` → Activity sub-tab
- `research-demo` → Agent visualization

### 3. Opportunities In Multiple Places
- `opportunities` tab → Main opportunities view
- `trending` → `intel-opportunities` sub-tab
- `betting` → Shows betting opportunities

---

## Hidden/Unused Tabs (Candidates for Removal)

| Tab | Reason | Recommendation |
|-----|--------|----------------|
| `leadership` | Hidden (Session 502) | Remove or repurpose |
| `teams` | Hidden (Session 502) | Remove or repurpose |
| `collaborate` | Hidden (Session 502) | Remove or repurpose |
| `marketplace` | No content | Remove |
| `agent-performance` | Redundant with Agents tab | Merge into Agents |

---

## Missing From UI (Should Be Added)

### 1. Decision Governance Dashboard (Session 658)
**Location:** ICC Governance sub-tab
**Should Show:**
- Total decisions: 977
- Canonical: 884 (90.5%)
- AI-promoted: 754
- Remaining drafts: 79
- AI Promoter status (last run, next run)

### 2. Celery Task Monitor
**Location:** ICC or Analytics
**Should Show:**
- 158 scheduled tasks
- Task execution status
- Failed tasks
- Queue depths

### 3. System Health Dashboard
**Location:** ICC Activity or new sub-tab
**Should Show:**
- Redis status
- Daphne/WebSocket status
- Celery worker status
- Database stats

---

## Recommended Consolidation

### Proposal: Reduce to 15 Main Tabs

| Keep | Merge Into | Remove |
|------|------------|--------|
| Assistant | - | - |
| Content Studio | Images, Video, Audio | - |
| - | - | Images (merge) |
| - | - | Video (merge) |
| - | - | Audio (merge) |
| Character Training | - | - |
| Gallery | - | - |
| **Command Center** (ICC) | Trending, Analytics | - |
| Agents | Agent Performance | - |
| - | - | Agent Performance (merge) |
| - | - | Trending (merge) |
| - | - | Analytics (merge) |
| Autonomous | - | - |
| Betting | - | - |
| Opportunities | - | - |
| Legal Assistant | - | - |
| Projects | - | - |
| Sessions | - | - |
| Preferences | - | - |
| Research Demo | - | Keep for demos |
| - | - | Leadership (remove) |
| - | - | Teams (remove) |
| - | - | Collaborate (remove) |
| - | - | Marketplace (remove) |
| - | - | Distribution (low use) |
| - | - | Content Calendar (low use) |
| - | - | Portfolio (low use) |
| - | - | Voices (low use) |
| - | - | Upload (merge into Gallery) |

**Result:** 15 focused tabs instead of 29

---

## Priority Action Items

### P0 - Critical (Session 659-660)
1. Add Decision Governance stats to ICC Governance sub-tab
2. Fix any broken WebSocket connections
3. Verify all main tabs load without errors

### P1 - High (Next Week)
4. Hide/remove unused tabs (Leadership, Teams, Collaborate, Marketplace)
5. Consolidate Trending into ICC
6. Add Celery task monitor

### P2 - Medium (Future)
7. Merge Content Creation tabs into Content Studio
8. Merge Agent Performance into Agents tab
9. Add System Health dashboard
10. Reduce to 15-tab structure

---

## API Endpoints Audit Needed

The UI references ~335 API endpoints. A full audit should verify:
1. Which endpoints exist and work
2. Which are deprecated
3. Which return authentication errors
4. Which are unused

**Suggested approach:** Create a test script that hits each endpoint and logs status.

---

## Conclusion

The UI is functional but bloated. The most impactful improvements would be:
1. **Add missing Session 658 governance stats** - Quick win
2. **Hide/remove 4+ unused tabs** - Reduces clutter
3. **Consolidate redundant sections** - Better UX

The 80,747-line single-file template is a maintenance challenge. Consider:
- Breaking into component files
- Using a frontend framework (React/Vue)
- Or at minimum, separating CSS/JS into external files

---

*Generated by Session 659 UI Audit*
