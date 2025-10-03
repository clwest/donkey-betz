# HIGH PRIORITY ISSUE: Learning Insights Field Error

## Status: ✅ FIXED (Session 143)

## Issue Description
- `/api/ai-partner/learning/insights/` endpoint returns 500 ERROR
- Trying to access `engagement_score` field that doesn't exist
- Dashboard completely broken due to this error

## Error Details
```python
# Current code trying to access non-existent field
engagement_score = learning_entry.engagement_score  # Field doesn't exist!
```

## Impact
- **Learning Dashboard**: Returns 500 error
- **User Experience**: Cannot view learning insights
- **Data Loss**: Engagement metrics not tracked

## Solutions

### Option 1: Add Missing Field (Recommended)
```python
# Add to model
class LearningEntry(models.Model):
    # ... existing fields ...
    engagement_score = models.FloatField(
        default=0.0,
        help_text="User engagement score 0-1"
    )
```

Create migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Option 2: Remove Field Reference
```python
# Update view to not use engagement_score
def learning_insights(request):
    # Remove or comment out engagement_score references
    data = {
        'insights': insights,
        # 'engagement_score': entry.engagement_score,  # Remove this
    }
```

### Option 3: Use Alternative Field
```python
# Use existing field instead
engagement_score = getattr(entry, 'quality_score', 0.0)  # Fallback
```

## Verification Steps
1. Check if model has engagement_score field
2. If not, decide on solution approach
3. Test endpoint returns 200 status
4. Verify dashboard displays correctly

## Test Command
```bash
curl -H "Authorization: Token <token>" \
  http://localhost:8000/api/ai-partner/learning/insights/
```

## Expected Response
```json
{
  "insights": [...],
  "engagement_score": 0.75,
  "status": "success"
}
```

## Related Files
- Model definition location unknown (need to find)
- View: `ai_partner/views_learning.py` (assumed)
- URL: `ai_partner/urls.py`