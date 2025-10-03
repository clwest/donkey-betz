# 🚀 Reddit Scout Complete Architecture Documentation

## 📋 Executive Summary

Reddit Scout is a sophisticated AI-powered system for discovering and analyzing startup ideas from Reddit discussions. It operates within the `donkey_betz/backend/agent_orchestra` module and uses real Reddit API integration (via PRAW) combined with AI analysis to identify high-potential business opportunities.

## 🏗️ Architecture Overview

### Core Components

1. **Models** (`agent_orchestra/models.py`)
   - `RedditIdea`: Main model storing discovered startup ideas
   - `DeletedRedditIdea`: Tracks deleted ideas to prevent re-discovery
   - Database schema with comprehensive indexing for performance

2. **Services** 
   - `RedditScoutService` (`services/reddit_scout_service.py`): Main orchestration service
   - `RedditAPIService` (`services/reddit_api_service.py`): Reddit API integration with PRAW
   - `RedditScoutExecutor`: Async execution engine for scouting operations

3. **Views/Endpoints** (`views_reddit_scout.py`)
   - Comprehensive REST API for CRUD operations
   - Bulk operations and export functionality
   - WebSocket support for real-time updates

4. **Management Commands** (`management/commands/scout_reddit_startups.py`)
   - CLI interface for manual/scheduled scouting
   - Dry-run mode for testing

## 📊 Database Schema

### RedditIdea Model

```python
class RedditIdea(models.Model):
    # Status choices
    IDEA_STATUS = [
        ('discovered', 'Discovered'),
        ('reviewing', 'Under Review'),
        ('approved', 'Approved for Business Plan'),
        ('rejected', 'Rejected'),
        ('in_progress', 'Business Plan in Progress'),
        ('completed', 'Business Plan Completed'),
    ]
    
    # Category choices (16 categories)
    IDEA_CATEGORIES = [
        ('saas', 'SaaS / Software'),
        ('marketplace', 'Marketplace'),
        ('ecommerce', 'E-commerce'),
        ('fintech', 'FinTech'),
        ('healthtech', 'HealthTech'),
        ('edtech', 'EdTech'),
        ('ai_ml', 'AI / Machine Learning'),
        ('sustainability', 'Sustainability / Green Tech'),
        ('social', 'Social Network / Community'),
        ('b2b', 'B2B Services'),
        ('b2c', 'B2C Services'),
        ('mobile_app', 'Mobile App'),
        ('hardware', 'Hardware / IoT'),
        ('gaming', 'Gaming / Entertainment'),
        ('crypto', 'Crypto / Blockchain'),
        ('other', 'Other'),
    ]
    
    # Core Fields
    user: ForeignKey(User)
    scout_agent: ForeignKey(AgentInstance)  # AI agent that discovered it
    scout_orchestration: ForeignKey(TaskOrchestration)
    
    # Idea Details
    title: CharField(max_length=500)
    problem: TextField  # Problem the idea solves
    solution: TextField  # Proposed solution
    target_market: CharField(max_length=200)
    reddit_context: TextField  # Original Reddit discussion context
    
    # Categorization
    category: CharField(choices=IDEA_CATEGORIES)
    secondary_categories: JSONField  # Additional categories
    tags: JSONField  # Custom tags
    
    # Scoring
    score: FloatField  # Overall score 1-10
    scoring_details: JSONField  # Detailed breakdown:
        # - engagement_score
        # - reddit_metrics (upvotes, comments, author)
        # - individual_scores:
        #   - market_size
        #   - technical_feasibility
        #   - competition
        #   - revenue_potential
        #   - scalability
    
    # Status & Tracking
    status: CharField(choices=IDEA_STATUS)
    business_plan_orchestration: ForeignKey(TaskOrchestration, nullable)
    user_notes: TextField(blank=True)
    
    # Metadata
    source_subreddit: CharField(max_length=100)
    discovered_at: DateTimeField(auto_now_add=True)
    reviewed_at: DateTimeField(nullable)
    business_plan_started_at: DateTimeField(nullable)
    business_plan_completed_at: DateTimeField(nullable)
    
    # Indexes for Performance
    - user + status
    - score
    - user + status + score
    - user + discovered_at
    - business_plan_orchestration
    - score + discovered_at
    - source_subreddit + user
```

### DeletedRedditIdea Model

```python
class DeletedRedditIdea(models.Model):
    user: ForeignKey(User)
    title: CharField(max_length=500)
    source_subreddit: CharField(max_length=100)
    deleted_at: DateTimeField(auto_now_add=True)
    content_hash: CharField(max_length=64, unique=True)  # SHA256 hash for deduplication
```

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/reddit-scout/deploy/` | POST | Deploy Reddit Scout agent |
| `/api/reddit-ideas/` | GET | List all discovered ideas with filtering |
| `/api/reddit-ideas/<id>/` | GET | Get specific idea details |
| `/api/reddit-ideas/<id>/update/` | PUT/PATCH | Update/edit idea details |
| `/api/reddit-ideas/<id>/delete/` | DELETE | Permanently delete idea |
| `/api/reddit-ideas/<id>/create-business-plan/` | POST | Generate business plan for idea |
| `/api/reddit-ideas/<id>/update-status/` | POST | Update idea status |

### Bulk Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/reddit-ideas/bulk-update/` | POST | Bulk update multiple ideas |
| `/api/reddit-ideas/bulk-update-status/` | POST | Bulk status updates |
| `/api/reddit-ideas/compare/` | POST | Compare multiple ideas side-by-side |
| `/api/reddit-ideas/export/<format>/` | GET | Export ideas (CSV/PDF) |

### Query Parameters for Listing

- `status`: Filter by status (comma-separated for multiple)
- `min_score` / `max_score`: Score range filtering
- `date_from` / `date_to`: Date range filtering
- `subreddit`: Filter by source subreddit
- `search`: Full-text search in title/problem/solution
- `sort_by`: Sort options (score, discovered_at, title, status)

## 🤖 Reddit API Integration

### RedditAPIService Features

1. **Real Reddit API via PRAW**
   - Synchronous and async clients
   - Circuit breaker pattern for reliability
   - Fallback to mock data when API unavailable

2. **Data Sources**
   - Default subreddits: startupideas, SomebodyMakeThis, entrepreneur, Business_Ideas, smallbusiness
   - Business-focused subreddits (15 total)
   - Hot/New/Top/Rising post sorting

3. **Scoring Algorithm**
   ```python
   # Engagement-based scoring
   upvote_score = min(5, upvotes / 20)  # Max 5 points
   comment_score = min(3, comments / 10)  # Max 3 points
   recency_bonus = 2.0  # For recent posts
   
   engagement_score = upvote_score + comment_score + recency_bonus
   final_score = min(10, max(1, engagement_score))
   ```

4. **Circuit Breaker Configuration**
   - Failure threshold: 5 failures
   - Recovery timeout: 60 seconds
   - Automatic fallback to cached/mock data

## 🔄 Execution Flow

### 1. Deployment Phase
```
User Request → deploy_reddit_scout() 
    → Create TaskOrchestration
    → Create AgentInstance
    → Queue async execution
    → Return orchestration ID
```

### 2. Scouting Phase
```
RedditScoutExecutor.execute()
    → Fetch Reddit data (25 posts per subreddit)
    → Analyze and score ideas
    → Filter by threshold (default: 3.0 for testing)
    → Save to database
    → Generate report
```

### 3. Review Phase
```
User Reviews Ideas
    → Update status (reviewing/approved/rejected)
    → Edit details if needed
    → Add notes
    → Create business plans for approved ideas
```

### 4. Business Plan Generation
```
create_business_plan_for_idea()
    → Deploy specialized agents:
        - Business Agent
        - Market Research Agent
        - Financial Agent
        - Marketing Agent
        - Technical Agent
    → Execute agents async
    → Update idea status
    → Send WebSocket notifications
```

## 🎯 Key Features

### 1. Advanced Filtering & Search
- Multi-criteria filtering (status, score, date, subreddit)
- Full-text search across all text fields
- Score distribution analytics
- Status count aggregation

### 2. Bulk Operations
- Bulk status updates
- Bulk categorization
- Bulk tagging
- Bulk deletion with hash tracking

### 3. Export Capabilities
- **CSV Export**: Full data with scoring breakdown
- **PDF Export**: Professional report with:
  - High-potential ideas (8-10 score)
  - Promising ideas table (6-8 score)
  - Detailed scoring metrics
  - Formatted for presentation

### 4. Comparison Engine
- Side-by-side comparison (up to 4 ideas)
- Metric analysis:
  - Highest overall score
  - Most feasible
  - Largest market
  - Best revenue potential
  - Lowest competition
- AI-generated recommendations

### 5. WebSocket Integration
- Real-time status updates
- Progress tracking for business plan generation
- Live notifications for discoveries

## 📝 Management Commands

### scout_reddit_startups

```bash
# Basic usage
python manage.py scout_reddit_startups --user testuser

# With custom threshold
python manage.py scout_reddit_startups --threshold 8.0

# Specific subreddits
python manage.py scout_reddit_startups --subreddits startupideas SaaS

# Dry run (preview only)
python manage.py scout_reddit_startups --dry-run
```

## 🔐 Security & Permissions

1. **Authentication Required**: All endpoints require authenticated user
2. **User Isolation**: Users can only access their own ideas
3. **Deletion Tracking**: Deleted ideas are hashed to prevent re-discovery
4. **Rate Limiting**: Via circuit breaker pattern
5. **Cache Layer**: 5-minute cache for Reddit API responses

## 📊 Performance Optimizations

1. **Database Indexes**
   - Composite indexes for common query patterns
   - Score-based indexes for ranking
   - User + status for dashboard queries

2. **Caching Strategy**
   - Redis cache for API responses (5 min TTL)
   - Query result caching with user variation
   - Fallback data service for reliability

3. **Async Processing**
   - Celery task queue for agent execution
   - Async Reddit API calls with asyncpraw
   - Parallel agent deployment

## 🚨 Error Handling

1. **Circuit Breaker States**
   - CLOSED: Normal operation
   - OPEN: API failures, use fallback
   - HALF_OPEN: Testing recovery

2. **Fallback Mechanisms**
   - Mock data generation
   - Cached results
   - Graceful degradation

3. **Logging**
   - Comprehensive logging at all levels
   - Error tracking with exc_info
   - Performance metrics logging

## 📈 Monitoring & Analytics

### Tracked Metrics
- Total ideas discovered
- Score distribution
- Success rate by category
- API performance (response times)
- User engagement metrics

### Dashboard Statistics
```python
filter_stats = {
    'total_count': total_ideas,
    'status_counts': {
        'discovered': count,
        'reviewing': count,
        'approved': count,
        # ...
    },
    'score_distribution': {
        '0-3': count,
        '3-5': count,
        '5-7': count,
        '7-8': count,
        '8-10': count,
    },
    'subreddits': [unique_subreddits]
}
```

## 🔄 Integration Points

### 1. Agent Orchestra System
- Uses AgentTemplate and AgentInstance models
- Integrates with TaskOrchestration
- Leverages async execution framework

### 2. Business Hub
- Reddit-to-business pipeline endpoint
- Automated business plan generation
- Multi-agent collaboration

### 3. Frontend Integration
- WebSocket support for real-time updates
- RESTful API for CRUD operations
- Export functionality for reports

## 🐛 Testing & Debugging

### Test Files
- `test_reddit_scout_debug.py`
- `test_reddit_scout_deployment.py`
- `test_reddit_scout_session_411.py`
- `test_reddit_ui_session_412.py`

### Debug Configuration
- Lowered scoring threshold (3.0) for testing
- Extensive logging throughout
- Dry-run mode in management command

## 📦 Dependencies

### Python Packages
```python
praw==7.7.1        # Reddit API wrapper
asyncpraw==7.7.1   # Async Reddit API
django>=4.2        # Web framework
celery>=5.3        # Task queue
redis>=4.5         # Caching
reportlab>=4.0     # PDF generation
```

### Environment Variables
```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DonkeyBetz/1.0
```

## 🚀 Deployment Considerations

1. **API Credentials**: Reddit API app registration required
2. **Rate Limits**: Reddit API has 60 requests/minute limit
3. **Database**: PostgreSQL recommended for production
4. **Queue**: Redis + Celery for async processing
5. **WebSockets**: Daphne/Channels for real-time features

## 📝 Future Enhancements

1. **ML Scoring**: GPT-4 integration for better idea analysis
2. **Trend Analysis**: Time-series analysis of trending topics
3. **User Credibility**: Enhanced Reddit user reputation scoring
4. **Auto-categorization**: ML-based category assignment
5. **Sentiment Analysis**: Advanced NLP for comment sentiment
6. **Competitive Analysis**: Automatic competitor identification

---

## 🔑 Key Takeaways for AI Content Studio Integration

### Required Components to Port:

1. **Models**: 
   - RedditIdea model with all fields
   - DeletedRedditIdea for tracking
   - Proper indexing strategy

2. **Services**:
   - Reddit API integration (PRAW)
   - Scoring algorithm
   - Circuit breaker pattern
   - Fallback data service

3. **API Endpoints**:
   - Full CRUD operations
   - Bulk operations
   - Export functionality
   - Comparison engine

4. **Frontend Features**:
   - Filtering and search UI
   - Score visualization
   - Status management
   - Export buttons

### Configuration Needed:
- Reddit API credentials
- Celery/Redis setup (or alternative async)
- Database migrations
- WebSocket support (optional)

### Simplified Implementation Path:
1. Start with basic model and CRUD
2. Add Reddit API integration
3. Implement scoring algorithm
4. Add filtering and search
5. Implement export features
6. Add bulk operations
7. Optional: WebSocket updates