---
originating_session: 901
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 901 - Initiative Priority & Portfolio Management

**Date:** February 1, 2026
**Focus:** Transform Initiative UI from firehose to strategic project management

---

## Problem Statement

The Initiative UI was a "firehose" showing all 223 initiatives in a single flat list. Users couldn't distinguish:
- What's actively being worked on vs. just tracked
- High-impact initiatives from low-priority ones
- Strategic programs from random experiments

### Before (Firehose)
```
All 223 initiatives in one list
- No priority indication
- No categorization
- Can't distinguish critical from trivial
```

### After (Strategic Dashboard)
```
4 Tabs: Active | Portfolio | Archive | Stats
- Priority badges (Critical, High, Medium, Low)
- Purpose icons (Revenue, Stability, Learning, etc.)
- Grouped by Program (Growth Intelligence, Monetization, etc.)
- Comprehensive stats view
```

---

## Solution: Priority Model & Portfolio Tabs

### 1. Priority Scoring Formula

```python
priority_score = (
    impact_score * 0.4 +      # 40% weight
    urgency * 0.2 +           # 20% weight
    confidence * 0.2 +        # 20% weight
    revenue_potential * 0.2   # 20% weight
)
```

**Priority Levels:**
| Score | Level | Badge Color |
|-------|-------|-------------|
| ≥ 0.8 | Critical | Red |
| ≥ 0.6 | High | Orange |
| ≥ 0.4 | Medium | Yellow |
| < 0.4 | Low | Gray |

### 2. Purpose Categories

```python
class Purpose(models.TextChoices):
    REVENUE = 'revenue', 'Revenue & Growth'
    STABILITY = 'stability', 'Platform Health'
    LEARNING = 'learning', 'Research & Learning'
    EXPANSION = 'expansion', 'New Capabilities'
    MAINTENANCE = 'maintenance', 'Maintenance'
```

### 3. Program Groupings

```python
class Program(models.TextChoices):
    GROWTH_INTELLIGENCE = 'growth_intelligence', 'Growth Intelligence'
    PLATFORM_HEALTH = 'platform_health', 'Platform Health'
    MONETIZATION = 'monetization', 'Monetization'
    CONTENT_PIPELINE = 'content_pipeline', 'Content Pipeline'
    AI_CAPABILITIES = 'ai_capabilities', 'AI Capabilities'
    USER_EXPERIENCE = 'user_experience', 'User Experience'
    INFRASTRUCTURE = 'infrastructure', 'Infrastructure'
    RESEARCH = 'research', 'Research'
    EXPERIMENTS = 'experiments', 'Experiments'
    UNCATEGORIZED = 'uncategorized', 'Uncategorized'
```

---

## New Model Fields

**File:** `core/models_document_registry.py`

```python
# Added to Initiative model:
purpose = models.CharField(max_length=20, choices=Purpose.choices, default='learning')
program = models.CharField(max_length=30, choices=Program.choices, default='uncategorized')
impact_score = models.FloatField(default=0.5, help_text='Expected impact (0-1)')
urgency = models.FloatField(default=0.5, help_text='Time-sensitivity (0-1)')
confidence = models.FloatField(default=0.5, help_text='Confidence in success (0-1)')
revenue_potential = models.FloatField(default=0.0, help_text='Revenue impact (0-1)')

# Computed properties:
@property
def priority_score(self): ...  # Returns 0-1

@property
def priority_level(self): ...  # Returns 'critical', 'high', 'medium', 'low'
```

---

## Frontend Changes

**File:** `frontend/src/pages/workspace/tabs/InitiativesTab.tsx`

### New Tab Navigation
```tsx
<div className="flex gap-1 p-1 bg-gray-800/50 rounded-lg">
  <TabButton active={activeTab === 'active'}>
    <Target /> Active
  </TabButton>
  <TabButton active={activeTab === 'portfolio'}>
    <Layers /> Portfolio
  </TabButton>
  <TabButton active={activeTab === 'archive'}>
    <Archive /> Archive
  </TabButton>
  <TabButton active={activeTab === 'stats'}>
    <BarChart3 /> Stats
  </TabButton>
</div>
```

### Priority Badge Component
```tsx
function PriorityBadge({ level }: { level?: string }) {
  const config = {
    critical: { icon: Flame, color: 'text-red-400 bg-red-500/20', label: 'Critical' },
    high: { icon: TrendingUp, color: 'text-orange-400 bg-orange-500/20', label: 'High' },
    medium: { icon: Circle, color: 'text-yellow-400 bg-yellow-500/20', label: 'Medium' },
    low: { icon: Circle, color: 'text-gray-400 bg-gray-500/20', label: 'Low' },
  }
  // ...
}
```

### Purpose Icon Component
```tsx
function PurposeIcon({ purpose }: { purpose?: string }) {
  const icons = {
    revenue: { icon: DollarSign, color: 'text-green-400' },
    stability: { icon: Shield, color: 'text-blue-400' },
    learning: { icon: Beaker, color: 'text-purple-400' },
    expansion: { icon: Rocket, color: 'text-orange-400' },
    maintenance: { icon: Wrench, color: 'text-gray-400' },
  }
  // ...
}
```

### Tab Content
- **Active Tab:** Shows ACTIVE status initiatives, sorted by priority
- **Portfolio Tab:** Groups by program with collapsible sections
- **Archive Tab:** Shows COMPLETED and ARCHIVED initiatives
- **Stats Tab:** Comprehensive breakdown by status, purpose, program

---

## API Changes

**File:** `core/views_research_demo.py`

### Priority-Based Sorting
```python
if sort_by == 'priority':
    initiatives = initiatives.annotate(
        computed_priority=Coalesce(F('impact_score'), Value(0.5)) * 0.4 +
                          Coalesce(F('urgency'), Value(0.5)) * 0.2 +
                          Coalesce(F('confidence'), Value(0.5)) * 0.2 +
                          Coalesce(F('revenue_potential'), Value(0.0)) * 0.2
    ).order_by('-computed_priority', '-updated_at')
```

### Stats Endpoint Response
```python
# Added to response:
'stats': {
    'total': 223,
    'active': 180,
    'completed': 15,
    'archived': 28,
    'by_purpose': {'learning': 150, 'revenue': 30, ...},
    'by_program': {'uncategorized': 180, 'research': 20, ...},
    'by_priority': {'low': 100, 'medium': 80, 'high': 30, 'critical': 13},
}
```

---

## Files Changed

| File | Change |
|------|--------|
| `core/models_document_registry.py` | Added Purpose, Program, priority fields + computed properties |
| `core/migrations/0212_session_901_initiative_priority.py` | NEW - Migration for priority fields |
| `core/views_research_demo.py` | Added priority sorting, stats breakdown, new fields in response |
| `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` | 4-tab UI, priority badges, purpose icons, program grouping |

---

## Migration

```bash
# Apply migration locally
python manage.py migrate core 0212_session_901_initiative_priority

# Deploy to Railway
railway up -s donkey-betz-platform
```

---

## Production Verification

Verified in production via `railway run`:

```python
>>> i = Initiative.objects.first()
>>> print(f'Priority: {i.priority_level}, Score: {i.priority_score}')
Priority: medium, Score: 0.4

>>> print(f'Purpose: {i.purpose_display}, Program: {i.program_display}')
Purpose: Research & Learning, Program: Uncategorized
```

---

## PR Created

**PR #679** - feat(Session 901): Initiative Priority & Portfolio Tabs
- Merged to main
- Deployed to Railway
- Verified in production

---

## Next Steps for Session 902

1. **Bulk Edit UI** - Update multiple initiatives' purpose/program at once
2. **Priority Recommendations** - AI suggests priority scores based on content
3. **Program Auto-Assignment** - Auto-categorize based on initiative name/description
4. **Dashboard Widget** - Show priority distribution on home page
