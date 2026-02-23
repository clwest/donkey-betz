# Governance Page Redesign — Implementation Spec

## Problem Statement

The current governance tab has three disconnected sections (Emergency Controls, Self-Healing, Pending Decisions) with no unified queue, unclear priorities, no batch operations, and heavy cognitive load. An operator opening the page can't answer "what needs me right now?" in under 5 seconds.

## Current State (GovernanceTab.tsx, ~492 lines)

| Section | Data Source | Issues |
|---------|------------|--------|
| Emergency Controls | `GET /api/platform/governance/` | Static owner card wastes above-fold space |
| Self-Healing | `GET /api/self-healing/progress/` | Agent table is passive — no actions per row |
| Pending Decisions | `HumanAttentionItem` from governance endpoint | Flat list, no filters, no batch, no urgency routing |

## Target Architecture

### A. Information Architecture

```
GovernanceTab
├── TriagePanel (above fold, always visible)
│   ├── CriticalCount badge (red)
│   ├── ApprovalsWaiting badge (amber)
│   ├── StuckGates badge (blue)
│   └── SystemHealth badge (green/red)
│
├── UnifiedQueue (main content)
│   ├── FilterBar
│   │   ├── Urgency: critical / high / medium / low / all
│   │   ├── Type: decision / gate / remediation / alert
│   │   ├── Age: <1h / <24h / >24h / all
│   │   ├── Owner: mine / unassigned / all
│   │   ├── Toggle: "Requires approval"
│   │   └── Toggle: "Safe actions only"
│   │
│   ├── SortControl: urgency desc (default) | age desc | type
│   │
│   ├── BatchBar (visible when items selected)
│   │   ├── "X selected" count
│   │   ├── [Approve All] [Ignore All] [Snooze All] [Assign To...]
│   │   └── [Clear Selection]
│   │
│   └── QueueItems[] (virtualized list, 10 per page)
│       └── QueueItemRow
│           ├── Checkbox (for batch)
│           ├── UrgencyBadge
│           ├── TypeIcon
│           ├── Title (clickable → detail modal)
│           ├── ImpactSentence ("Blocks 3 initiatives")
│           ├── NextAction verb ("Approve" / "Review" / "Assign")
│           ├── Age ("2h ago")
│           ├── Owner avatar (or "Unassigned")
│           └── QuickAction button (primary action without opening modal)
│
├── DetailModal (overlays on item click)
│   ├── Full description
│   ├── Context (source agent, related initiative, risk level)
│   ├── Action buttons: Approve / Dismiss / Snooze / Escalate
│   └── Notes textarea
│
└── CollapsedPanels (below fold)
    ├── SelfHealingProgress (collapsed by default, expandable)
    └── EmergencyControls (collapsed by default, expandable)
```

### B. Interaction Model

#### Triage Workflow
1. Operator opens governance tab
2. TriagePanel shows 4 counts — operator clicks the non-zero badge
3. UnifiedQueue filters to that category
4. Operator scans ImpactSentence + NextAction columns
5. For safe items: clicks QuickAction directly
6. For complex items: clicks row → DetailModal → decides

#### Batch Review Mode
1. Operator clicks checkbox on first item (BatchBar appears)
2. Shift-click or "Select all visible" to grab up to 10
3. Click batch action (Approve All / Ignore All / Snooze All / Assign To)
4. Confirmation toast shows count + undo link (5s window)

#### Risk Segmentation
- **"Safe actions only" toggle** (default ON for new users): Hides items where `payload.risk_level == 'high'` or `item_type in ['emergency', 'security']`. Shows only items that are safe to approve without deep review.
- **"Requires approval" filter**: Shows only items where `status == 'pending'` and `item_type in ['decision', 'gate_review']`.

#### Ownership
- Items with no owner show "Unassigned" in gray
- Clicking "Assign To" opens a dropdown of active operators (from User model)
- "Mine" filter shows items where `user_id` matches current user
- Assigning sets `HumanAttentionItem.user` and adds a `viewed_at` timestamp

### C. Visual Hierarchy

#### Above the Fold (first 300px)
```
┌─────────────────────────────────────────────────────────────┐
│  GOVERNANCE                                    [Emergency ▾]│
├──────────┬──────────┬──────────┬───────────────────────────┤
│ 🔴 2     │ 🟡 5     │ 🔵 1     │ 🟢 System Healthy         │
│ Critical │ Approvals│ Stuck    │ SKIN: Locked              │
│ [View]   │ [View]   │ [View]  │                           │
├──────────┴──────────┴──────────┴───────────────────────────┤
│ Filter: [All ▾] [All Types ▾] [All Ages ▾]  ☐ Safe only   │
│ Sort: Urgency ▾                              ☐ Approvals   │
├─────────────────────────────────────────────────────────────┤
│ ☐ 🔴 Gate blocked: Q1 Revenue Pipeline                     │
│   "Blocks 3 downstream initiatives"    [Approve] 2h  @you  │
│ ☐ 🟡 Decision: Expand spider coverage to crypto feeds      │
│   "Adds 12 new data sources"           [Review]  4h  unassigned│
│ ...                                                          │
└─────────────────────────────────────────────────────────────┘
```

#### Color/Urgency Encoding
| Urgency | Color | Background | Border |
|---------|-------|-----------|--------|
| Critical | `accent-red` | `accent-red/10` | `accent-red/30` |
| High | `accent-amber` | `accent-amber/10` | `accent-amber/30` |
| Medium | `primary-400` | `primary-500/10` | `primary-500/20` |
| Low | `gray-400` | `gray-800` | `gray-700` |

#### Type Icons (lucide-react)
| Type | Icon | Description shown in glossary tooltip |
|------|------|--------------------------------------|
| decision | `CheckSquare` | "A choice the system needs human input on" |
| gate_review | `ShieldCheck` | "A quality gate waiting for approval to proceed" |
| remediation | `Wrench` | "A code fix the system wants to apply" |
| alert | `AlertTriangle` | "A system event that may need attention" |
| security | `Lock` | "A security-related finding" |

### D. Implementation Tickets

---

#### Ticket 1: Unified Queue API Aggregator

**Title:** Add `/api/platform/governance/queue/` endpoint that merges all governance items

**Description:**
Create a single API endpoint that aggregates `HumanAttentionItem`, `PilotReadinessGate` (status=pending_review), and `AuditRemediationTask` (status=assigned/in_progress) into one sorted, filterable feed.

**Acceptance Criteria:**
- [ ] Endpoint returns paginated results (page_size=10, offset-based)
- [ ] Each item has: `id`, `type`, `title`, `impact_sentence`, `next_action`, `urgency`, `age_seconds`, `owner`, `source_agent`, `risk_level`, `payload`
- [ ] Supports query params: `urgency`, `type`, `age_max`, `owner`, `requires_approval`, `safe_only`, `sort`
- [ ] Returns `triage_counts`: `{critical: N, approvals: N, stuck_gates: N}`
- [ ] Response time < 200ms (single DB query with UNION or Python merge of 3 small queries)

**Backend Changes:**
- File: `core/views_platform_command.py`
- New function: `governance_queue_view(request)`
- New helper: `_build_unified_queue(filters, sort, page, page_size)`
- Register URL: `path('api/platform/governance/queue/', governance_queue_view)`
- File: `core/urls.py` — add route

**Impact sentence generation:**
```python
# Per item type:
# HumanAttentionItem: from payload.get('impact') or f"Pending {item_type} from {source_type}"
# PilotReadinessGate: f"Blocks {gate.decision.initiative.name if gate.decision else 'unknown'} progression"
# AuditRemediationTask: f"Fixes {task.finding.category} issue in {task.finding.affected_files[0] if task.finding.affected_files else 'codebase'}"
```

**Next action mapping:**
```python
NEXT_ACTIONS = {
    'decision': 'Approve',
    'gate_review': 'Review',
    'remediation': 'Run Fix',
    'alert': 'Acknowledge',
    'security': 'Investigate',
}
```

---

#### Ticket 2: Batch Actions API

**Title:** Add `/api/platform/governance/batch/` endpoint for bulk operations

**Description:**
Accept a list of item IDs + action and apply to all. Supports approve, ignore, snooze, assign.

**Acceptance Criteria:**
- [ ] POST endpoint accepts `{item_ids: string[], action: "approve"|"ignore"|"snooze"|"assign", assign_to?: number, snooze_hours?: number}`
- [ ] Returns `{success: true, processed: N, failed: N, errors: []}`
- [ ] Snooze sets `expires_at` to now + snooze_hours
- [ ] Approve sets `status='resolved'` + `decision_feedback='approved'`
- [ ] Ignore sets `status='resolved'` + `decision_feedback='dismissed'`
- [ ] Assign sets `user` FK to the specified user
- [ ] Max 50 items per batch

**Backend Changes:**
- File: `core/views_platform_command.py`
- New function: `governance_batch_action_view(request)`
- Register URL in `core/urls.py`

---

#### Ticket 3: Triage Panel Component

**Title:** Create `TriagePanel` component with live counts and filter shortcuts

**Description:**
Above-fold panel showing 4 metric cards. Clicking a card filters the unified queue below.

**Acceptance Criteria:**
- [ ] Shows: Critical count (red), Approvals waiting (amber), Stuck gates (blue), System health (green/red)
- [ ] Each card is clickable → sets the corresponding filter in UnifiedQueue
- [ ] Counts come from `triage_counts` in the queue API response
- [ ] System health reads from existing governance endpoint `emergency_controls`
- [ ] Emergency controls dropdown (collapsed) accessible from top-right

**UI Components:**
- New: `frontend/src/components/platform/TriagePanel.tsx`
- Props: `counts: {critical, approvals, stuck_gates}`, `health: object`, `onFilterChange: (filter) => void`

---

#### Ticket 4: Unified Queue Table Component

**Title:** Create `UnifiedQueueTable` with filters, sorting, and row actions

**Description:**
Replace the three separate sections with one filterable, sortable table.

**Acceptance Criteria:**
- [ ] Filter bar with urgency, type, age, owner, safe-only toggle, requires-approval toggle
- [ ] Sort by urgency (default), age, type
- [ ] Each row shows: checkbox, urgency badge, type icon, title, impact sentence, next action button, age, owner
- [ ] Clicking a row opens the existing `DecisionDetailModal` (extended to handle all item types)
- [ ] QuickAction button performs the next action inline with optimistic UI update
- [ ] Pagination: 10 items per page with "Load more" or page buttons
- [ ] Empty state per filter combination

**UI Components:**
- New: `frontend/src/components/platform/UnifiedQueueTable.tsx`
- New: `frontend/src/components/platform/QueueItemRow.tsx`
- New: `frontend/src/components/platform/FilterBar.tsx`
- Modify: `frontend/src/components/platform/DecisionDetailModal.tsx` — accept all item types

**Frontend Changes:**
- File: `frontend/src/lib/api.ts` — add `platformApi.governanceQueue(filters)` and `platformApi.governanceBatch(action)`
- File: `frontend/src/pages/workspace/tabs/GovernanceTab.tsx` — replace three sections with TriagePanel + UnifiedQueueTable

---

#### Ticket 5: Batch Review Bar

**Title:** Add batch selection bar with bulk actions

**Description:**
When one or more checkboxes are selected, a sticky bar appears above the table with batch actions.

**Acceptance Criteria:**
- [ ] Bar shows: "N selected", Approve All, Ignore All, Snooze All (opens duration picker), Assign To (opens user dropdown), Clear Selection
- [ ] Optimistic UI: items fade out on batch action, revert on error
- [ ] Confirmation toast with undo link (5s)
- [ ] Max 50 items selectable
- [ ] "Select all on this page" checkbox in header

**UI Components:**
- New: `frontend/src/components/platform/BatchActionBar.tsx`
- Uses: shadcn `DropdownMenu` for Assign To, `Popover` for snooze duration

---

#### Ticket 6: Glossary Tooltips

**Title:** Add tooltips for governance-specific terms

**Description:**
Internal terms (gate, remediation, SKIN lock, etc.) should have hover tooltips for first-time users.

**Acceptance Criteria:**
- [ ] Glossary terms defined in a `GOVERNANCE_GLOSSARY` constant
- [ ] `<GlossaryTerm term="gate_review">` component wraps text with dotted underline + tooltip
- [ ] Terms: gate, remediation, SKIN lock, quarantine, initiative, decision, attention item, dream, agent conversation
- [ ] Tooltip shows 1-2 sentence plain-English explanation

**UI Components:**
- New: `frontend/src/components/platform/GlossaryTerm.tsx`
- Uses: shadcn `Tooltip`

---

#### Ticket 7: Collapse Emergency + Self-Healing Panels

**Title:** Move Emergency Controls and Self-Healing into collapsible panels below the queue

**Description:**
These sections are important but not the primary workflow. Move them below the unified queue as collapsible accordions.

**Acceptance Criteria:**
- [ ] Emergency Controls: collapsed by default, expand to show existing EmergencyControls component
- [ ] Self-Healing Progress: collapsed by default, expand to show existing progress table
- [ ] Both show a one-line summary when collapsed (e.g., "System nominal" or "73% — 4 agents active")
- [ ] Accordion state persists in localStorage

**UI Components:**
- Modify: `frontend/src/pages/workspace/tabs/GovernanceTab.tsx`
- Uses: shadcn `Collapsible` or custom accordion

---

### E. Operator Mental Model (2-Minute Guide)

**What is Governance?**
Governance is your command center for everything the AI system needs a human decision on. Think of it as your inbox — but instead of emails, it's decisions, quality gates, and system alerts.

**The 4 numbers at the top tell you what needs attention:**
- **Critical** (red): Something is broken or blocked. Handle these first.
- **Approvals** (amber): The system wants to do something and needs your OK.
- **Stuck Gates** (blue): An initiative can't move forward until you review it.
- **System Health** (green/red): Quick pulse check — is everything running?

**How to work through your queue:**
1. Click the highest non-zero number at the top
2. For each item, read the **impact sentence** (what happens if you ignore it) and the **next action** (what you can do)
3. For quick items: click the action button directly in the row
4. For complex items: click the row to open details, read the context, then decide

**Batch mode:** Check multiple items, then use the bar at the top to approve/ignore/snooze all at once. Great for clearing out a backlog of low-risk approvals.

**Safe mode:** Toggle "Safe actions only" to hide anything that could break things. Only shows low-risk approvals you can confidently clear.

---

### F. Long Output Handling Pattern

Since PA response truncation is a known issue (Session 1065 fix), governance-related PA interactions should implement this pattern:

**When the PA generates governance summaries or reports:**

1. The agentic loop now detects `truncated=true` from `enforce_real_ai` (Session 1065)
2. Auto-continues with `previous_response_id` chaining (max 2 continuations)
3. Parts are joined into one response before returning to the user

**For governance-specific tool responses that could be long:**

The `governance_queue_view` API should:
- Always paginate (max 10 items per page) to keep individual responses small
- Include `total_count` and `has_more` so the PA can decide whether to fetch more
- Return `impact_sentence` and `next_action` pre-computed (no need for the PA to generate these)

**For PA-generated governance reports:**
- The PA tool handler for governance should return structured data, not prose
- The PA's text generation (which could truncate) only adds a 2-3 sentence summary
- Detailed data is in the structured tool response, not in the LLM's text output

This ensures governance summaries never get cut off mid-sentence regardless of queue size.

---

## Migration Path

**Phase 1 (Tickets 1-2):** Backend API — unified queue + batch endpoint. No frontend changes. Existing UI still works.

**Phase 2 (Tickets 3-5):** Frontend — TriagePanel + UnifiedQueueTable + BatchBar. Replace the three sections. Emergency controls and self-healing move to collapsible panels.

**Phase 3 (Tickets 6-7):** Polish — Glossary tooltips, accordion panels, localStorage persistence.

Each phase is independently deployable and testable.
