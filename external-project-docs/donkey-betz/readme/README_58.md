# AI-Powered Fact-Checking & Social Media Monitoring System

A comprehensive Django application for monitoring public figures' statements across social media and news sources, performing AI-powered fact-checking, and tracking engagement metrics.

## Features

- **Real-time Monitoring**: Automated monitoring of social media platforms (Twitter/X, Truth Social, Facebook) and news sources
- **AI Fact-Checking**: GPT-4 powered analysis of statements with source verification
- **Engagement Tracking**: Real-time tracking of likes, shares, replies, and viral spread
- **Trending Analysis**: Detection and analysis of viral misinformation
- **Alert System**: Automated alerts for false statements going viral
- **Public API**: RESTful API for accessing fact-check data
- **Admin Dashboard**: Django admin interface for management

## System Architecture

### Core Components

1. **Models** (`models.py`):
   - `PublicFigure`: People being monitored
   - `Statement`: Individual statements/posts
   - `FactCheckResult`: AI analysis results
   - `FactCheckSource`: Sources used in verification
   - `TrendingStatement`: Viral content tracking
   - `MonitoringAlert`: Alert system
   - `EngagementSnapshot`: Historical engagement data

2. **Monitoring Agents** (`agents/`):
   - `SocialMediaMonitor`: Scrapes social media platforms
   - `NewsMonitor`: Monitors news websites for quotes

3. **Analysis Engine** (`analyzers/`):
   - `StatementAnalyzer`: AI-powered fact-checking
   - `TrendingAnalyzer`: Viral pattern analysis

4. **Background Tasks** (`tasks.py`):
   - Celery tasks for monitoring and analysis
   - Scheduled jobs for data updates

5. **API Endpoints** (`views.py`, `serializers.py`):
   - REST API for all system data
   - Public and authenticated endpoints

## Setup Instructions

### 1. Database Migration

```bash
# Create and apply database migrations
python manage.py makemigrations fact_checker
python manage.py migrate
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

### 3. Add Public Figures

Use the Django admin interface at `/admin/` to add public figures to monitor:

1. Go to "Public figures" → "Add"
2. Fill in name, role, social media handles
3. Set monitoring priority (1=highest, 5=lowest)
4. Activate monitoring

### 4. Configure URLs

Add to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns
    path('fact-checker/', include('fact_checker.urls')),
]
```

### 5. Start Monitoring

#### Manual Testing
```bash
# Test social media monitoring
python manage.py run_fact_check_monitoring --social-only

# Test news monitoring  
python manage.py run_fact_check_monitoring --news-only

# Analyze pending statements
python manage.py run_fact_check_monitoring --analyze-only

# Monitor specific figure
python manage.py run_fact_check_monitoring --figure-id <uuid>

# Dry run (no database changes)
python manage.py run_fact_check_monitoring --dry-run
```

#### Production Monitoring with Celery

1. Install and configure Redis/RabbitMQ
2. Start Celery worker:
   ```bash
   celery -A your_project worker -l info
   ```
3. Start Celery beat for scheduled tasks:
   ```bash
   celery -A your_project beat -l info
   ```

### 6. Configure Celery Beat Schedule

Add to your `settings.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'monitor-social-media': {
        'task': 'fact_checker.tasks.monitor_social_media',
        'schedule': 300.0,  # Every 5 minutes
    },
    'monitor-news-sources': {
        'task': 'fact_checker.tasks.monitor_news_sources', 
        'schedule': 900.0,  # Every 15 minutes
    },
    'update-engagement-metrics': {
        'task': 'fact_checker.tasks.update_engagement_metrics',
        'schedule': 1800.0,  # Every 30 minutes
    },
    'update-trending-analysis': {
        'task': 'fact_checker.tasks.update_trending_analysis',
        'schedule': 3600.0,  # Every hour
    },
    'update-accuracy-scores': {
        'task': 'fact_checker.tasks.update_figure_accuracy_scores',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-old-data': {
        'task': 'fact_checker.tasks.cleanup_old_data',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}
```

## API Endpoints

### Public Endpoints (No Authentication)

- `GET /fact-checker/api/figures/` - List public figures
- `GET /fact-checker/api/statements/` - List statements
- `GET /fact-checker/api/fact-checks/` - List fact-check results
- `GET /fact-checker/api/trending/` - Trending statements
- `GET /fact-checker/api/dashboard/overview/` - Dashboard overview
- `GET /fact-checker/api/public/recent_fact_checks/` - Recent fact-checks
- `GET /fact-checker/api/public/figure_rankings/` - Figure accuracy rankings
- `GET /fact-checker/api/public/trending_false/` - Trending false statements

### Authenticated Endpoints

- `GET /fact-checker/api/alerts/` - Monitoring alerts
- `POST /fact-checker/api/statements/{id}/recheck/` - Re-fact-check statement
- `POST /fact-checker/api/alerts/{id}/acknowledge/` - Acknowledge alert

### Query Parameters

Most list endpoints support filtering and pagination:

- `?page=1&page_size=20` - Pagination
- `?search=keyword` - Text search
- `?fact_check_status=verified_false` - Filter by status
- `?figure=<uuid>` - Filter by figure
- `?days=7` - Filter by recent days
- `?min_shares=1000` - Filter by engagement

## Data Flow

1. **Monitoring**: Background tasks scrape social media and news sources every 5-15 minutes
2. **Detection**: AI determines if posts contain fact-checkable claims
3. **Storage**: New statements are stored with initial engagement metrics
4. **Analysis**: Statements are queued for AI fact-checking analysis
5. **Verification**: AI researches claims using multiple sources
6. **Results**: Fact-check results are stored with confidence scores
7. **Alerts**: System generates alerts for viral false statements
8. **Tracking**: Engagement metrics are updated regularly
9. **Trending**: Viral patterns are analyzed hourly

## Performance Considerations

- Uses database indexes for efficient queries
- Implements pagination for large datasets
- Caches frequently accessed data
- Rate limits external API calls
- Processes statements in batches

## Security & Privacy

- Only monitors public statements and accounts
- No personal data collection beyond public posts
- Secure API authentication for sensitive endpoints
- Rate limiting to prevent abuse
- Content hashing to detect duplicates

## Monitoring & Alerts

The system automatically generates alerts for:

- False statements going viral (>1000 shares)
- High-impact false statements from priority figures
- Patterns of repeated false statements
- Coordinated misinformation campaigns

## Production Deployment

For production deployment:

1. Use PostgreSQL database
2. Configure Redis for Celery
3. Set up proper logging
4. Configure error monitoring (Sentry)
5. Use environment variables for sensitive settings
6. Set up monitoring for background tasks
7. Configure load balancing for API endpoints

## Dependencies

The system integrates with your existing Django project and requires:

- Django REST Framework
- Celery for background tasks
- BeautifulSoup for web scraping
- aiohttp for async HTTP requests
- Your existing AI service integration

## Limitations

- Social media scraping may be limited by platform restrictions
- Real-time monitoring requires significant server resources
- AI fact-checking quality depends on available sources
- Some platforms require API keys (not included in this demo)

## Future Enhancements

- Real social media API integrations
- Advanced NLP for better claim extraction
- Machine learning for trend prediction
- Browser automation for JavaScript-heavy sites
- Integration with professional fact-checking databases
- Multi-language support
- Real-time WebSocket updates for dashboards