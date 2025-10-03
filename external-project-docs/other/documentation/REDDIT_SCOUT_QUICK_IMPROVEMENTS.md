# Reddit Scout Quick Improvements

## 🚀 Quick Wins (< 1 day each)

### 1. **Add More Subreddits**
```python
EXPANDED_SUBREDDITS = [
    # Current
    'r/startupideas', 'r/SomebodyMakeThis', 'r/Business_Ideas',
    'r/Entrepreneur', 'r/smallbusiness',
    
    # Add these
    'r/Startup', 'r/SaaS', 'r/sidehustle', 'r/EntrepreneurRideAlong',
    'r/indiehackers', 'r/growmybusiness', 'r/AskEntrepreneurs',
    'r/businessideas', 'r/Lightbulb', 'r/alphaandbetausers'
]
```

### 2. **Enhance Scoring Details**
```python
# Add more granular scoring
ENHANCED_SCORING = {
    'market_size': {
        'weight': 0.20,
        'sub_criteria': ['tam', 'sam', 'som', 'growth_rate']
    },
    'competitive_advantage': {
        'weight': 0.15,
        'sub_criteria': ['uniqueness', 'barriers_to_entry', 'network_effects']
    },
    'execution_difficulty': {
        'weight': 0.10,
        'sub_criteria': ['technical', 'regulatory', 'capital_required']
    }
}
```

### 3. **Add Idea Tags**
```python
IDEA_TAGS = {
    'hot': lambda score: score >= 8.5,
    'quick-win': lambda idea: idea.get('time_to_market_score', 0) >= 8,
    'low-competition': lambda idea: idea.get('competition_score', 0) >= 8,
    'high-revenue': lambda idea: idea.get('revenue_potential_score', 0) >= 8,
    'social-impact': lambda idea: idea.get('social_impact_score', 0) >= 8,
    'technical': lambda idea: 'AI' in idea['title'] or 'ML' in idea['title'],
    'b2b': lambda idea: 'business' in idea['target_market'].lower(),
    'b2c': lambda idea: 'consumer' in idea['target_market'].lower()
}
```

### 4. **Save Reddit Metrics**
```python
# Extend RedditIdea model
class RedditIdea(models.Model):
    # ... existing fields ...
    
    # Add these
    reddit_score = models.IntegerField(default=0)  # Upvotes - downvotes
    reddit_comments = models.IntegerField(default=0)
    reddit_awards = models.IntegerField(default=0)
    reddit_url = models.URLField(blank=True)
    discovered_date = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now=True)
```

### 5. **Add Email Notifications**
```python
# Send email for high-scoring ideas
from api.services.email_service import EmailService

async def notify_high_score_ideas(user, ideas):
    high_score_ideas = [i for i in ideas if i['score'] >= 8.5]
    if high_score_ideas:
        await EmailService.send_high_score_ideas_notification(
            user=user,
            ideas=high_score_ideas,
            subject="🚀 Hot Startup Ideas Found!"
        )
```

### 6. **Batch Operations Enhancement**
```python
# Add more bulk actions
BULK_ACTIONS = {
    'create_business_plans': 'Create plans for all selected',
    'export_to_notion': 'Export to Notion database',
    'share_with_team': 'Share with team members',
    'schedule_review': 'Schedule for later review',
    'archive': 'Archive ideas',
    'merge_similar': 'Merge similar ideas'
}
```

### 7. **Quick Filters**
```python
# Add preset filters
PRESET_FILTERS = {
    'hot_today': {'score__gte': 8, 'created_at__gte': today},
    'quick_wins': {'time_to_market_score__gte': 8},
    'low_competition': {'competition_score__gte': 8},
    'my_favorites': {'is_favorite': True},
    'ready_to_build': {'status': 'approved'},
    'needs_review': {'status': 'discovered', 'score__gte': 7}
}
```

### 8. **Progress Tracking**
```python
# Track idea lifecycle
IDEA_LIFECYCLE = {
    'discovered': 'Just found',
    'reviewing': 'Under review',
    'researching': 'Market research',
    'approved': 'Ready to build',
    'in_progress': 'Building',
    'launched': 'Live product',
    'abandoned': 'Did not pursue'
}

# Add metrics
def get_idea_metrics(user):
    return {
        'total_discovered': RedditIdea.objects.filter(user=user).count(),
        'conversion_rate': launched_count / total_count * 100,
        'avg_time_to_launch': avg_days,
        'success_rate': successful_launches / total_launches * 100
    }
```

### 9. **Competitive Analysis**
```python
# Quick competitor check
async def check_competitors(idea):
    # Search for similar products
    search_terms = extract_keywords(idea['title'])
    
    # Check domains
    domain_available = check_domain_availability(idea['title'])
    
    # Search Product Hunt
    similar_on_ph = search_product_hunt(search_terms)
    
    # Search Google
    google_results = search_google(f"{search_terms} competitor")
    
    return {
        'domain_available': domain_available,
        'similar_products': similar_on_ph,
        'potential_competitors': google_results[:5]
    }
```

### 10. **Smart Categorization**
```python
# Auto-categorize based on content
def auto_categorize(idea):
    categories = []
    
    # Keywords mapping
    CATEGORY_KEYWORDS = {
        'ai_ml': ['AI', 'ML', 'machine learning', 'artificial intelligence'],
        'saas': ['SaaS', 'subscription', 'software', 'platform'],
        'marketplace': ['marketplace', 'connect', 'buyers', 'sellers'],
        'mobile': ['app', 'mobile', 'iOS', 'Android'],
        'ecommerce': ['shop', 'store', 'sell', 'buy', 'commerce'],
        'fintech': ['payment', 'finance', 'banking', 'crypto', 'investment'],
        'health': ['health', 'fitness', 'medical', 'wellness'],
        'education': ['learn', 'teach', 'course', 'education', 'training']
    }
    
    # Check title and description
    text = f"{idea['title']} {idea['problem']} {idea['solution']}".lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in text for keyword in keywords):
            categories.append(category)
    
    return categories
```

## 🎯 Implementation Order

1. **Day 1**: Add more subreddits + Enhanced scoring
2. **Day 2**: Email notifications + Quick filters
3. **Day 3**: Competitive analysis + Smart categorization
4. **Day 4**: Progress tracking + Batch operations
5. **Day 5**: Testing and refinement

These improvements can be implemented quickly and will significantly enhance the Reddit Scout experience without requiring major architectural changes.