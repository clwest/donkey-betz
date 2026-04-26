<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Rich-data presence audit
>
> **Where to look now:**
> - [docs/PLATFORM_INVENTORY.md](/docs/PLATFORM_INVENTORY.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Rich Data Audit - API Response Analysis

**Created:** Session 695 (January 6, 2026)
**Purpose:** Document backend API data available for frontend display

---

## Summary

This audit examines what rich data is returned by backend APIs vs. what's currently displayed in the React frontend. Many APIs return detailed metadata that could enhance the UI.

---

## 1. Recent Activity API

**Endpoint:** `GET /api/recent-activity/`
**Used by:** AgentsPage (Activity tab)

### Response Fields

| Field | Type | Currently Displayed | Notes |
|-------|------|---------------------|-------|
| `id` | uuid | Yes (as key) | |
| `type` | string | Yes | dream/conversation/decision/pilot |
| `icon` | emoji | Yes (Session 694) | 💭 🗣️ 🏛️ 🧪 |
| `title` | string | Yes | |
| `subtitle` | string | Yes | |
| `timestamp` | ISO date | Yes | |
| `timestamp_display` | string | Yes (Session 694) | "20m ago" format |
| `agents` | string[] | Yes (Session 694) | Participating agents |
| `agent` | string | No | Single agent for dreams |
| `category` | string | No | Dream category (observation/prediction) |
| `status` | string | No | For decisions/pilots |
| `decision_type` | string | No | For decisions |
| `kpi` | string | No | For pilots |

### Enhancement Opportunities
- Show dream category badge (observation vs prediction)
- Show decision/pilot status indicator
- Show KPI name for pilots

---

## 2. Learning Activity API

**Endpoint:** `GET /api/agent-learning/activity/`
**Used by:** AgentsPage (Learning tab)

### Response Fields

| Field | Type | Currently Displayed | Notes |
|-------|------|---------------------|-------|
| `timestamp` | ISO date | Yes | |
| `type` | string | Yes | knowledge_transfer |
| `source` | string | No | "Knowledge transfer" |
| `description` | string | No | Full description |
| `teacher` | string | Yes | |
| `student` | string | Yes | |
| `knowledge` | string | No | Full knowledge text |
| `knowledge_full.title` | string | Yes | |
| `knowledge_full.summary` | string | No | Full summary text |
| `knowledge_full.key_insights` | array | Yes (Session 694) | May contain objects! |
| `knowledge_full.knowledge_type` | string | Yes | trend/insight/etc |
| `knowledge_full.confidence` | float | Yes | 0-1 |
| `key_points` | string[] | Fallback | |
| `was_useful` | bool | Yes | |
| `usefulness_score` | float | Yes | 0-1 |
| `effectiveness_gain` | float | No | Often 0 |

### Additional Response Fields

| Field | Type | Currently Displayed | Notes |
|-------|------|---------------------|-------|
| `stats.total_knowledge` | int | Yes | |
| `stats.connections` | int | Yes | |
| `stats.today_transfers` | int | Yes | |
| `stats.avg_effectiveness` | float | Yes | |
| `top_learners` | array | Yes (Session 694) | Name, count, effectiveness |

### Enhancement Opportunities
- Show full `description` in expanded view
- Display `knowledge_full.summary` on hover/modal
- Show `effectiveness_gain` when non-zero

---

## 3. Agent Dreams API

**Endpoint:** `GET /api/agent-dreams/`
**Used by:** Could be used more prominently

### Response Fields

| Field | Type | Rich Data | Notes |
|-------|------|-----------|-------|
| `id` | uuid | | |
| `agent_id` | uuid | | |
| `agent_name` | string | | |
| `title` | string | | |
| `content` | string | **RICH** | Full dream narrative |
| `dream_type` | string | | observation/prediction |
| `inspiration` | string | **RICH** | What inspired the dream |
| `related_topics` | array | | Topics array |
| `vividness` | float | **RICH** | 0-1 creativity metric |
| `creativity` | float | **RICH** | 0-1 creativity metric |
| `shown_to_user` | bool | | |
| `user_reaction` | string | | Reaction emoji |
| `dreamed_at` | ISO date | | |

### Summary Stats
- `today_count`: 1512 dreams today
- `unread_count`: 1512 unread

### Enhancement Opportunities
- **Dream detail modal** with full `content` and `inspiration`
- **Creativity visualization** using vividness/creativity scores
- **Dream gallery** showing unread dreams prominently
- **Reaction feature** to mark dreams (✨ 🔥 💡)

---

## 4. Agent Conversations API

**Endpoint:** `GET /api/agent-conversations/`
**Used by:** Partially displayed

### Response Fields

| Field | Type | Rich Data | Notes |
|-------|------|-----------|-------|
| `id` | uuid | | |
| `topic` | string | | |
| `type` | string | | devils_advocate/etc |
| `type_display` | string | | |
| `trigger` | string | | scheduled/user/etc |
| `status` | string | | concluded/active |
| `initiator` | string | | |
| `initiator_emoji` | emoji | **RICH** | 🤖 🔍 etc |
| `participants` | array | **RICH** | [{name, emoji}] |
| `message_count` | int | **RICH** | Number of messages |
| `quality_score` | float | **RICH** | 0-1 conversation quality |
| `conclusion` | string | **RICH** | Full conclusion text |
| `insights` | array | | Generated insights |
| `started_at` | ISO date | | |
| `ended_at` | ISO date | | Duration calculable |
| `messages` | array | **RICH** | Full message thread |

### Message Object Fields
- `agent`: string
- `agent_emoji`: emoji
- `content`: string (full message)
- `type`: question/answer/synthesis
- `sequence`: int
- `relevance`: float
- `created_at`: ISO date

### Enhancement Opportunities
- **Conversation viewer** showing full message threads
- **Quality score badge** on conversation cards
- **Duration display** (ended_at - started_at)
- **Conversation type icons** (devils_advocate, brainstorm, etc)
- **Expandable conclusion** preview

---

## 5. Boardroom Decisions API

**Endpoint:** `GET /api/boardroom/decisions/`
**Used by:** Intelligence page (partially)

### Response Fields

| Field | Type | Rich Data | Notes |
|-------|------|-----------|-------|
| `id` | uuid | | |
| `topic` | string | | |
| `decision_type` | string | | experiment/pipeline/guideline |
| `decision_type_display` | string | | |
| `impact_area` | string | | product/security/etc |
| `impact_area_display` | string | | |
| `key_insights` | array | **RICH** | Bullet points of insights |
| `recommended_stance` | string | **RICH** | Action recommendation |
| `suggested_feature` | string | **RICH** | Feature proposal |
| `rationale` | string | **RICH** | Why this decision |
| `participants` | array | | Agent names |
| `status` | string | | draft/approved/rejected |
| `is_canonical` | bool | | Promoted to canon |
| `promoted_at` | ISO date | | |
| `promoted_by` | string | | |
| `source_type` | string | | conversation/hive_session |
| `source_id` | uuid | | Link to source |
| `source_topic` | string | | |
| `created_at` | ISO date | | |

### Summary Stats
- `total`: 571 decisions
- `canonical_count`: 75 promoted
- `type_counts`: breakdown by type
- `source_counts`: breakdown by source

### Enhancement Opportunities
- **Decision detail modal** with full rationale and insights
- **Feature proposals section** showing suggested_feature
- **Canon badge** for promoted decisions
- **Link to source conversation** via source_id

---

## 6. Pilot Gates API

**Endpoint:** `GET /api/pilot-gates/`
**Used by:** Intelligence page (Gates tab)

### Response Fields

| Field | Type | Rich Data | Notes |
|-------|------|-----------|-------|
| `id` | uuid | | |
| `decision_id` | uuid | | |
| `decision_topic` | string | | |
| `decision_type` | string | | |
| `impact_area` | string | | |
| `status` | string | | not_started/in_progress/ready/approved |
| `risk_level` | string | | low/medium/high/critical |
| `summary` | string | | |
| `checklist_total` | int | | |
| `checklist_completed` | int | | |
| `checklist_percentage` | float | | |
| `checklist_items` | array | **RICH** | Full checklist with AI content |
| `latency` | object | **RICH** | Timing metrics |
| `approved_by` | string | | |
| `created_at` | ISO date | | |
| `running_pilot` | object | | If pilot started |

### Checklist Item Fields
- `id`: uuid
- `item_type`: basic_review/success_metrics/etc
- `title`: string
- `description`: string
- `status`: pending/completed
- `is_required`: bool
- `generated_content`: **RICH** - Full AI-generated markdown
- `has_content`: bool

### Latency Object Fields
- `decision_to_readiness_hours`
- `readiness_duration_hours`
- `approval_wait_hours`
- `total_gate_hours`
- `pilot_duration_hours`

### Enhancement Opportunities
- **Checklist viewer** with expandable AI content
- **Latency visualization** showing pipeline timing
- **Risk level badges** with color coding

---

## 7. Experiments API

**Endpoint:** `GET /api/pilot-experiments/`
**Used by:** Intelligence page (Experiments tab)

### Response Fields

| Field | Type | Rich Data | Notes |
|-------|------|-----------|-------|
| `id` | uuid | | |
| `name` | string | | |
| `hypothesis` | string | **RICH** | Full hypothesis text |
| `status` | string | | running/success/failure |
| `kpi_owner` | string | | |
| `primary_kpi` | string | | |
| `target_value` | string | | |
| `current_value` | string | | |
| `secondary_kpis` | array | | |
| `extracted_metrics.raw_content` | string | **RICH** | Full AI metrics markdown |
| `extracted_metrics.source` | string | | ai_generated |
| `started_at` | ISO date | | |
| `ended_at` | ISO date | | |
| `learnings` | string | **RICH** | For completed experiments |
| `pilot_id` | uuid | | Link to pilot |
| `decision_topic` | string | | |
| `decision_id` | uuid | | |
| `risk_level` | string | | |
| `is_halted` | bool | | |
| `halted_at` | ISO date | | |
| `halted_by` | string | | |
| `halt_reason` | string | **RICH** | |
| `outcome_classification` | string | | pending/success/failure |

### Enhancement Opportunities
- **Experiment detail modal** (already implemented in Session 693)
- **KPI progress visualization**
- **Learnings display** for completed experiments
- **Halt history** section

---

## 8. Agents Comprehensive API

**Endpoint:** `GET /api/v1/agents/comprehensive/`
**Used by:** AgentsPage (Directory tab)

### Response Fields Per Agent

| Field | Type | Currently Displayed | Notes |
|-------|------|---------------------|-------|
| `name` | string | Yes | |
| `category` | string | Yes | |
| `description` | string | Yes | |
| `keywords` | array | No | Search terms |
| `examples` | array | No | Usage examples |
| `is_routable` | bool | Yes (as badge) | |
| `is_active` | bool | No | |
| `priority` | int | No | Routing priority |

### Enhancement Opportunities
- **Examples tooltip** showing usage examples
- **Keywords tags** for each agent
- **Priority indicator** for routable agents
- **Active/Inactive toggle** visibility

---

## Priority Enhancement Recommendations

### High Priority (High Impact, Low Effort)

1. **Dream Gallery Modal**
   - Show full `content` and `inspiration`
   - Display vividness/creativity as visual bars
   - Add reaction buttons

2. **Conversation Thread Viewer**
   - Full message history
   - Agent emojis and quality scores
   - Expandable conclusion

3. **Decision Insights Panel**
   - Show `key_insights` as bullet list
   - Display `recommended_stance` prominently
   - Show `suggested_feature` proposal

### Medium Priority

4. **Agent Examples Tooltip**
   - Show `examples` array on hover
   - Display `keywords` as tags

5. **Latency Dashboard**
   - Visualize gate timing metrics
   - Show pipeline bottlenecks

6. **Dream Type Filtering**
   - Filter by observation vs prediction
   - Sort by vividness/creativity

### Lower Priority

7. **Conversation Quality Metrics**
   - Quality score badges
   - Message count indicators

8. **Effectiveness Tracking**
   - Show `effectiveness_gain` trends
   - Learning velocity charts

---

## API Data Quality Issues Found

1. **key_insights can contain objects** - Fixed in Session 694
2. **activity.icon can be object** - Fixed in Session 694
3. **Truncated fields** - Some fields were truncated (fixed in Session 693)

---

## Next Steps

1. Prioritize enhancements based on user value
2. Create modals for rich content (dreams, conversations, decisions)
3. Add filtering/sorting using metadata fields
4. Consider WebSocket real-time updates for live data

