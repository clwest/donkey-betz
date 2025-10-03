# 🎯 NEXT SESSION: Fix Opportunity Detail Data Display

## Current Status ✅
- **View Function**: Working (queries database successfully)
- **URL Routing**: Working (page loads at `/opportunity-detail/?id=<id>`)
- **Template**: Created but not displaying data
- **Database**: 8 opportunities available for user 'chris'
- **Server**: Running at http://localhost:8000

## The Problem 🔧

**URL**: `http://localhost:8000/opportunity-detail/?id=sports_bet_003`

The page loads but displays a **bare/empty page** instead of showing the opportunity details. The template structure exists but data isn't rendering.

## What Needs to Be Fixed

### 1. Debug the View Function
**File**: `core/views_unified.py` (line 697-724)

Add debug logging to verify:
- Opportunity is being retrieved from database
- Data is being passed to template context
- opportunity_data JSON field contains expected data

```python
# Add after line 711:
logger.info(f"Loaded opportunity: {opportunity.opportunity_id}")
logger.info(f"Opportunity data keys: {opportunity.opportunity_data.keys()}")
logger.info(f"Context being passed: {context}")
```

### 2. Verify Template Variable Rendering
**File**: `core/templates/unified/opportunity_detail.html`

**Test these progressively**:

#### Step 1: Test basic variable
```html
<!-- Add at top of template after back button -->
<h1>DEBUG: {{ opportunity }}</h1>
<p>Title: {{ opportunity.opportunity_title }}</p>
<p>Type: {{ opportunity.opportunity_type }}</p>
<p>Status: {{ opportunity.status }}</p>
```

#### Step 2: Check opportunity_data structure
```html
<h2>Opportunity Data:</h2>
<pre>{{ opportunity.opportunity_data }}</pre>
```

#### Step 3: Test specific fields
```html
<p>Description: {{ opportunity.opportunity_data.description }}</p>
<p>Match Score: {{ opportunity.opportunity_data.match_score }}</p>
<p>Skills: {{ opportunity.opportunity_data.skills }}</p>
```

### 3. Check OpportunityTracking Model
**File**: `intelligence/models.py` (line 418-475)

Verify the data structure in the database:
```bash
python manage.py shell -c "
from intelligence.models import OpportunityTracking
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='chris')
opp = OpportunityTracking.objects.get(opportunity_id='sports_bet_003', user=user)

print(f'\n=== Opportunity Data ===')
print(f'ID: {opp.opportunity_id}')
print(f'Title: {opp.opportunity_title}')
print(f'Type: {opp.opportunity_type}')
print(f'Status: {opp.status}')
print(f'\nOpportunity Data JSON:')
import json
print(json.dumps(opp.opportunity_data, indent=2))
"
```

### 4. Common Issues to Check

#### Issue A: Empty opportunity_data
If `opportunity_data` is `{}`, we need to populate it with real data.

#### Issue B: Template variable names mismatch
Ensure template uses correct variable names:
- `{{ opportunity.opportunity_title }}` not `{{ opp.title }}`
- `{{ opportunity.opportunity_data.description }}` not `{{ description }}`

#### Issue C: Missing context data
Verify view is actually passing `opportunity` to context:
```python
return render(request, 'unified/opportunity_detail.html', {
    'opportunity': opportunity,  # ← Confirm this exists
    'page_title': opportunity.opportunity_title
})
```

## Expected Data Structure

Based on the opportunity storage system, `opportunity_data` should contain:

```python
{
    "title": "MLB: Dodgers vs Giants - Dodgers -1.5",
    "description": "Sports betting opportunity...",
    "match_score": 85,
    "skills": ["sports analysis", "odds calculation"],
    "action_steps": ["Research team stats", "Calculate odds", "Place bet"],
    "budget": "100-500",
    "platform": "DraftKings",
    "url": "https://...",
    "odds": "-110",
    "confidence": "High"
}
```

## Testing Steps

1. Start Django shell and inspect the opportunity object
2. Add debug output to the view
3. Reload the page and check server logs
4. Add simple template debug at the top of the page
5. Progressively test each section of the template
6. Once data displays, remove debug statements

## Success Criteria ✅

- [ ] Page displays opportunity title prominently
- [ ] Description shows full text
- [ ] Match score circle displays percentage
- [ ] Financial info shows budget/revenue
- [ ] Skills display as badges
- [ ] Action steps show as numbered list
- [ ] Status badge shows correct color
- [ ] Back button works
- [ ] External link button appears (if URL exists)

## Files to Review/Modify

- `core/views_unified.py` - Add debug logging
- `core/templates/unified/opportunity_detail.html` - Fix data rendering
- `intelligence/models.py` - Check OpportunityTracking structure
- Check Django debug toolbar if available

## Quick Win Test

**Simplest possible test** - add this at the top of the template:
```html
<div style="background: red; color: white; padding: 20px;">
    <h1>{{ opportunity.opportunity_title }}</h1>
    <p>{{ opportunity.opportunity_type }}</p>
</div>
```

If this shows red box with title → data is being passed, just need to fix template rendering.
If this shows red box but no text → data not being passed from view.
If no red box at all → template not loading.

---

**Commit Hash**: 7bd90ac
**Branch**: feature/reality-fixes-implementation
**Ready for**: Debugging data display issue
