# UI Audit - Session 502

**Date:** December 19, 2025
**Purpose:** Identify redundancies, gaps, and consolidation opportunities

---

## Current Main Tabs (18 Visible)

| # | Tab | Purpose | Sub-tabs |
|---|-----|---------|----------|
| 1 | **Assistant** | Main landing, AI chat | None (inline features) |
| 2 | **Agents** | Agent ecosystem | Overview, Profile, Social, Intelligence, Growth, Memory, Workflows |
| 3 | **Analytics** | Performance monitoring | ? |
| 4 | **Autonomous** | 19 situations dashboard | Overview, Trigger Tuning, **Spider Operations**, Narrative Drift, ML Scoring |
| 5 | **Collaborate** | Real-time collaboration | ? |
| 6 | **Distribute** | Smart content distribution | ? |
| 7 | **Intelligence** | Spider data hub | Trending, Markets, Opportunities, **Spiders**, Data Feed, Knowledge, Timeline, Documents |
| 8 | **Leadership** | Executive dashboard | ? |
| 9 | **Legal** | Legal assistant | Case management, Drafting |
| 10 | **Marketplace** | Content marketplace | ? |
| 11 | **Opportunities** | Income opportunities | ? |
| 12 | **Portfolio** | User portfolio | ? |
| 13 | **Preferences** | Settings | Profile, Image, Video, Audio, Research, Agents |
| 14 | **Projects** | Project management | ? |
| 15 | **Teams** | Team collaboration | ? |
| 16 | **Upload** | File upload | ? |
| 17 | **Voices** | Voice marketplace | ? |

### Hidden Tabs (6)
- Images, Characters, Video, Audio, Gallery, Sessions (moved to Creative Toolbox in Projects)

---

## REDUNDANCIES IDENTIFIED

### 1. SPIDERS (Appears in 2 places)

| Location | What It Shows |
|----------|---------------|
| **Intelligence → Spiders** | Spider network status, categories, data counts |
| **Autonomous → Spider Operations** | Spider operations, runs, success rates |

**Recommendation:** Consolidate into ONE location. Intelligence Hub is the better home since it's about data. Autonomous should link TO it, not duplicate it.

---

### 2. OPPORTUNITIES (Appears in 2+ places)

| Location | What It Shows |
|----------|---------------|
| **Intelligence → Opportunities** | Job/freelance opportunities from spiders |
| **Opportunities Tab** | Income opportunities matching |
| **Agents → Intelligence** | May overlap with opportunity data |

**Recommendation:** Single "Opportunities" experience. Intelligence should FEED opportunities, not duplicate the view.

---

### 3. AGENTS DATA (Scattered)

| Location | What It Shows |
|----------|---------------|
| **Agents Tab** | Full agent ecosystem (7 sub-tabs!) |
| **Intelligence → Knowledge** | What agents learned from spiders |
| **Autonomous → Overview** | Agent-related situations |
| **Preferences → Agents** | Agent settings/configuration |

**Recommendation:** Agents Tab should be the SINGLE source of truth. Other tabs should link to it.

---

### 4. ANALYTICS (Scattered)

| Location | What It Shows |
|----------|---------------|
| **Analytics Tab** | Performance monitoring |
| **Agents → Workflows → Analytics** | Workflow analytics |
| **Intelligence → Timeline** | Data collection analytics |
| **Autonomous → ML Scoring** | ML model analytics |

**Recommendation:** Consolidate all analytics into Analytics Tab with sub-sections.

---

## DISCORD vs WEB APP PARITY

### Discord-Only Features (Not on Web)
| Feature | Discord Command | Web Equivalent |
|---------|-----------------|----------------|
| Voice chat | `/voice-chat`, `/voice-ask` | ❌ Missing |
| Voice cloning | `/voice-clone` | Partial (Voices tab) |
| Podcasts | `/podcast-create`, `/podcast-list` | ❌ Missing |
| Content Series | `/series-create`, `/series-list` | ❌ Missing |
| Blockchain audit | `/audit-contract` | ❌ Missing |
| Narrative drift | `/narrative-*` commands | ❌ Missing |
| ROI dashboard | `/roi-*` commands | ❌ Missing |

### Web-Only Features (Not on Discord)
| Feature | Web Location | Discord Equivalent |
|---------|--------------|-------------------|
| Legal Assistant | Legal tab | `/legal-*` (partial) |
| Full image editing | Images (hidden) | ❌ Missing |
| Video editing | Video (hidden) | ❌ Missing |
| Character training | Characters (hidden) | ❌ Missing |
| Project management | Projects tab | ❌ Missing |
| Portfolio | Portfolio tab | `/profile` (partial) |
| Team collaboration | Teams tab | ❌ Missing |
| Real-time collab | Collaborate tab | ❌ Missing |

---

## RECOMMENDED CONSOLIDATION

### Phase 1: Remove Duplicates

1. **Spider Operations** → Remove from Autonomous, keep in Intelligence
2. **Opportunities in Intelligence** → Link to Opportunities Tab instead
3. **Knowledge in Intelligence** → Move to Agents Tab (it's about agents learning)

### Phase 2: Simplify Navigation

**BEFORE (18 tabs):**
```
Assistant | Agents | Analytics | Autonomous | Collaborate | Distribute |
Intelligence | Leadership | Legal | Marketplace | Opportunities |
Portfolio | Preferences | Projects | Teams | Upload | Voices
```

**PROPOSED (12 tabs):**
```
Assistant | Agents | Intelligence | Autonomous | Create | Opportunities |
Legal | Analytics | Settings
```

Where:
- **Create** = Projects + Upload + Voices (content creation)
- **Settings** = Preferences + Profile
- **Removed:** Collaborate, Distribute, Leadership, Marketplace, Portfolio, Teams (low usage or merge into others)

### Phase 3: Discord Parity

Add to Web:
1. Podcast Studio UI (matches `/podcast-*`)
2. Content Series UI (matches `/series-*`)
3. ROI Dashboard (matches `/roi-*`)
4. Narrative Drift viewer (matches `/narrative-*`)

Add to Discord:
1. Full image editing commands
2. Project management commands
3. Team collaboration commands

---

## QUESTIONS FOR USER

1. Which tabs do you actually USE regularly?
2. Are Leadership/Marketplace/Teams/Collaborate being used?
3. Should we prioritize Discord feature parity or Web cleanup first?
4. Any features you wish existed that don't?

---

## COMPLEXITY SCORE

| Metric | Current | Target |
|--------|---------|--------|
| Main tabs | 18 | 10-12 |
| Total sub-tabs | ~45 | ~25 |
| Redundant features | 4 identified | 0 |
| Discord/Web parity | ~60% | 90%+ |
