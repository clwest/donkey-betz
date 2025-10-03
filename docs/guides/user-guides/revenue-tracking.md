# 💰 Revenue Tracking System Documentation

## Overview
Complete revenue tracking pipeline for the Unified Donkey Betz platform, enabling real money tracking from opportunity discovery through payment.

---

## 📊 Revenue Model

### Location
`/core/models.py` lines 1782-1927

### Database Table
`core_revenue`

### Fields
```python
class Revenue(UnifiedBaseModel):
    # User relationship
    user = ForeignKey(User)

    # Money fields
    amount = DecimalField(max_digits=10, decimal_places=2)  # USD amount

    # Status tracking
    status = CharField(choices=[
        'potential',   # Opportunity identified
        'pending',     # Application submitted
        'confirmed',   # Job/project secured
        'received',    # Payment received
        'withdrawn',   # Funds withdrawn
        'cancelled'    # Opportunity cancelled
    ])

    # Source tracking
    source = CharField(choices=[
        'quick_apply',      # Quick Apply jobs
        'freelance',        # Freelance projects
        'consulting',       # Consulting gigs
        'ai_project',       # AI projects
        'content',          # Content creation
        'trading',          # Trading/Investment
        'sports_betting',   # Sports betting
        'affiliate',        # Affiliate commission
        'other'
    ])

    # Opportunity details
    opportunity_id = CharField(255)
    opportunity_title = CharField(500)
    company = CharField(255)

    # Dates
    application_date = DateTimeField()
    confirmation_date = DateTimeField()
    payment_date = DateTimeField()

    # Tracking
    spider_source = CharField(100)      # Which spider found it
    agent_involved = CharField(100)     # Which agent helped
    match_score = FloatField(0-1)       # Match quality
```

### Key Methods
```python
# Get total revenue for a user
Revenue.get_user_total(user, status='potential')

# Get comprehensive stats
Revenue.get_user_stats(user)
# Returns: {
#     'total_potential': amount,
#     'total_pending': amount,
#     'total_confirmed': amount,
#     'total_received': amount,
#     'count_opportunities': number,
#     'avg_amount': average
# }
```

---

## 🔄 Revenue Flow Pipeline

### 1. Spider Discovery
```python
# Spider finds opportunity
opportunity = {
    'id': 'job_001',
    'title': 'Senior Python Developer',
    'company': 'TechCorp',
    'salary_min': 120000,
    'salary_max': 180000,
    'source': 'RemoteOK'
}
cache.set(f'opportunity_{id}', opportunity)
```

### 2. User Applies (Quick Apply)
```python
# In revenue_opportunities_consumer.py
async def handle_quick_apply(self, data):
    # Process application
    response = QuickApplyView.post(request)

    # Track revenue if successful
    if response.success:
        Revenue.objects.create(
            user=self.user,
            amount=(salary_min + salary_max) / 2,
            source='quick_apply',
            status='potential',  # Initial status
            opportunity_id=opportunity_id,
            opportunity_title=title,
            company=company,
            application_date=now(),
            spider_source=data.get('source'),
            agent_involved='QuickApplyAgent',
            match_score=0.75
        )
```

### 3. Status Updates
```python
# When application is confirmed
revenue.status = 'pending'
revenue.save()

# When job is secured
revenue.status = 'confirmed'
revenue.confirmation_date = now()
revenue.save()

# When payment received
revenue.status = 'received'
revenue.payment_date = now()
revenue.save()
```

---

## 🌐 API Endpoints

### Get Revenue Statistics
```http
GET /api/v1/revenue/stats/
Authorization: Bearer {token}

Response:
{
    "total_revenue": {
        "all": 1365000,
        "potential": 850000,
        "pending": 350000,
        "confirmed": 150000,
        "received": 15000
    },
    "time_based": {
        "today": 120000,
        "this_week": 450000,
        "this_month": 1365000
    },
    "by_source": [
        {"source": "quick_apply", "total": 950000, "count": 8},
        {"source": "freelance", "total": 415000, "count": 2}
    ],
    "success_rate": 18.5,
    "average_amount": 136500
}
```

### Track New Revenue
```http
POST /api/v1/revenue/track/
Content-Type: application/json
Authorization: Bearer {token}

{
    "amount": 150000,
    "source": "quick_apply",
    "status": "potential",
    "opportunity_id": "job_123",
    "opportunity_title": "Senior Developer",
    "company": "TechCorp",
    "spider_source": "RemoteOK",
    "agent_involved": "QuickApplyAgent",
    "match_score": 0.85
}

Response:
{
    "success": true,
    "revenue_id": "uuid-here",
    "message": "Revenue tracked successfully"
}
```

### Update Revenue Status
```http
POST /api/v1/revenue/{revenue_id}/update-status/
Content-Type: application/json
Authorization: Bearer {token}

{
    "status": "confirmed"
}

Response:
{
    "success": true,
    "message": "Revenue status updated to confirmed"
}
```

### Get Revenue History
```http
GET /api/v1/revenue/history/?page=1&per_page=20&status=potential
Authorization: Bearer {token}

Response:
{
    "revenues": [...],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 45,
        "pages": 3
    }
}
```

---

## 🔌 WebSocket Integration

### Revenue Dashboard Updates
```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/revenue-dashboard/');

// Listen for revenue updates
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.type === 'revenue_update') {
        // New revenue tracked
        updateDashboard(data.revenue);
    } else if (data.type === 'revenue_status_update') {
        // Status changed
        updateRevenueStatus(data.revenue_id, data.new_status);
    }
};
```

### Revenue Opportunities Consumer
Location: `/core/revenue_opportunities_consumer.py`

Handles:
- Quick Apply actions
- Revenue tracking
- Opportunity streaming
- Real-time updates

---

## 💾 Database Migration

### File
`/core/migrations/0011_add_revenue_model.py`

### Apply Migration
```bash
python manage.py migrate core
```

### Check Revenue Table
```sql
SELECT * FROM core_revenue WHERE user_id = 1;
```

---

## 🧪 Testing Revenue Tracking

### 1. Create Test Revenue
```python
from core.models import Revenue
from django.contrib.auth.models import User

user = User.objects.first()
revenue = Revenue.objects.create(
    user=user,
    amount=150000,
    source='quick_apply',
    status='potential',
    opportunity_title='Test Developer Role',
    company='TestCorp',
    match_score=0.85
)
print(f"Created revenue: ${revenue.amount}")
```

### 2. Test Quick Apply Flow
```python
# Load opportunity into cache
from django.core.cache import cache
cache.set('opportunity_test', {
    'id': 'test_001',
    'title': 'Python Developer',
    'salary_min': 100000,
    'salary_max': 150000,
    'company': 'TestCorp'
})

# Trigger Quick Apply (via WebSocket or API)
# Check Revenue was created
Revenue.objects.filter(opportunity_id='test_001').exists()
```

### 3. Test Statistics
```python
from core.models import Revenue

# Get user stats
stats = Revenue.get_user_stats(user)
print(f"Total Potential: ${stats['total_potential']}")
print(f"Success Rate: {stats['count_opportunities']} opportunities")
```

### 4. Test API
```bash
# Get stats
curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/v1/revenue/stats/

# Track revenue
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {token}" \
     -d '{"amount": 75000, "source": "freelance", "status": "potential"}' \
     http://localhost:8000/api/v1/revenue/track/
```

---

## 📈 Revenue Dashboard Integration

### Frontend Pages
- `/revenue/` - Main revenue dashboard
- `/opportunities/` - Shows opportunities with Quick Apply
- `/income/` - Income builder with revenue tracking

### Key Features
- Real-time revenue updates via WebSocket
- Status progression tracking
- Source breakdown charts
- Time-based analytics
- Success rate metrics

---

## 🚀 Production Checklist

- [ ] Ensure Redis is running for caching
- [ ] WebSocket server active (Daphne/Channels)
- [ ] Database migrations applied
- [ ] Spiders activated and scheduled
- [ ] Quick Apply email configuration
- [ ] Revenue webhook endpoints (for payment processors)
- [ ] Backup strategy for revenue data
- [ ] Monitoring for revenue anomalies

---

## 🔧 Troubleshooting

### Revenue Not Tracking
```python
# Check if Revenue model is accessible
from core.models import Revenue
Revenue.objects.count()

# Check Quick Apply is creating records
# In revenue_opportunities_consumer.py, line 282
# Add logging: logger.info(f"Creating revenue: {potential_amount}")
```

### WebSocket Not Updating
```python
# Check channel layer
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
# Should not be None

# Test broadcast
from asgiref.sync import async_to_sync
async_to_sync(channel_layer.group_send)(
    'revenue_dashboard_1',
    {'type': 'revenue_update', 'revenue': {...}}
)
```

### API Errors
```python
# Check URL configuration
from django.urls import reverse
reverse('revenue-stats')  # Should resolve

# Test view directly
from core.views_revenue_tracking import RevenueStatsView
view = RevenueStatsView()
# Check view.get() method
```

---

## 📝 Future Enhancements

1. **Payment Integration**
   - Stripe/PayPal webhooks
   - Automatic status updates
   - Payment verification

2. **Advanced Analytics**
   - Revenue forecasting
   - Conversion funnel analysis
   - ROI by spider/agent

3. **Automation**
   - Auto-apply to high-match opportunities
   - Revenue goal tracking
   - Alert system for milestones

4. **Reporting**
   - Tax documentation
   - Income verification
   - Performance reports

---

*Last Updated: September 28, 2025 - Session 7*