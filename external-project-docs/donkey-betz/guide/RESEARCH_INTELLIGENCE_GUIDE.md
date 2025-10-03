# Research Intelligence Feature Guide

## Overview
Research Intelligence is a comprehensive data aggregation and analysis system that unifies search across multiple data sources including Reddit, news, SEC filings, government data, patents, and personal memory. It provides ML-powered relevance scoring, cross-source correlation, and intelligent insights for business intelligence and market research.

## Architecture

### Frontend Components
Located in `/donkey-betz-frontend/src/features/research-intelligence/`

#### Main Components
- `ResearchIntelligence.tsx` - Main page with search interface
- `ResearchDashboard.tsx` - Dashboard for search results and analytics
- `SearchInterface.tsx` - Advanced search form with filters
- `ResultsPanel.tsx` - Search results display with faceted navigation
- `SavedSearches.tsx` - Manage saved searches and alerts
- `ResearchCollections.tsx` - Organize research into collections
- `TrendsPanel.tsx` - Trending topics and insights
- `AIAssistant.tsx` - AI-powered research assistant

#### Supporting Components
- `ResultCard.tsx` - Individual search result display
- `SourceFilter.tsx` - Filter results by data source
- `DateRangeFilter.tsx` - Date range selection
- `SectorFilter.tsx` - Business sector filtering
- `SimilaritySearch.tsx` - Find similar content

#### Hooks
- `useResearchSearch.ts` - Main search functionality
- `useSavedSearches.ts` - Saved search management
- `useCollections.ts` - Research collection management
- `useTrends.ts` - Trending topics data
- `useAIAssistant.ts` - AI assistant interactions

### Backend Services
Located in `/backend/agent_orchestra/services/`

#### Core Service
- `research_intelligence_service.py` - Main aggregation service
  - Handles multi-source searching
  - ML scoring and ranking
  - Vector similarity search
  - Legislative impact detection
  - Faceted search generation

#### Supporting Services
- `reddit_api_service.py` - Reddit data integration
- `enhanced_tools.py` - News, SEC, patents APIs
- `government_api_service.py` - Government data APIs
- `legislative_ml_service.py` - Legislative analysis
- `embedding_service.py` - Vector embeddings for similarity

### API Endpoints
Base URL: `/api/agent-orchestra/research/`

## Data Sources

### 1. Reddit
**Purpose**: Community discussions, problems, and business ideas
**API**: Reddit API via `RedditAPIService`
**Features**:
- Subreddit searching
- Engagement scoring
- Comment analysis
- Trend detection

### 2. News
**Purpose**: Latest industry news and market updates
**API**: News API via `EnhancedAgentTools.news_api`
**Features**:
- Real-time news
- Multiple sources
- Category filtering
- Publication date sorting

### 3. SEC Filings
**Purpose**: Company reports, financial data, regulatory filings
**API**: SEC EDGAR via `EnhancedAgentTools.sec_edgar_api`
**Features**:
- 10-K, 10-Q, 8-K forms
- Insider trading reports
- Company financials
- CIK lookup

### 4. Government Data
**Purpose**: Contracts, RFPs, bills, regulations
**API**: Multiple government APIs via `GovernmentAPIService`
**Features**:
- Federal contracts (SAM.gov)
- Legislative bills (Congress.gov)
- Regulations (Federal Register)
- Agency data

### 5. Patents
**Purpose**: Innovation trends, technology developments
**API**: Patent API via `EnhancedAgentTools.patent_api`
**Features**:
- Patent search
- Classification filtering
- Inventor tracking
- Prior art discovery

### 6. Memory Palace
**Purpose**: Personal knowledge and saved research
**API**: Internal Memory Palace system
**Features**:
- Semantic search
- Personal notes
- Previous research
- Knowledge graph

## Search Features

### Basic Search
```
GET /api/agent-orchestra/research/search/?q=renewable+energy
```

### Advanced Search with Filters
```
GET /api/agent-orchestra/research/search/
  ?q=renewable+energy
  &sources=reddit,news,sec
  &date_range=month
  &sectors=technology,energy
  &min_score=0.7
  &legislative_impact=true
  &limit=20
```

### Parameters
- `q` (required) - Search query
- `sources` - Comma-separated sources (reddit,news,sec,government,patents,memory)
- `date_range` - Time filter (today,week,month,year,all)
- `sectors` - Business sectors filter
- `min_score` - Minimum relevance score (0-1)
- `legislative_impact` - Filter for regulatory opportunities
- `similar_to` - Find similar content using embeddings
- `limit` - Results per page (max: 100)
- `offset` - Pagination offset

## ML Scoring System

### Relevance Scoring Factors
1. **Text Similarity** - Semantic similarity using embeddings
2. **Source Credibility** - Weight by source reliability
   - Government: 1.2x
   - SEC: 1.15x
   - Patents: 1.1x
   - News: 1.0x
   - Reddit: 0.9x
3. **Recency Boost** - Recent content scored higher
   - < 7 days: 1.2x
   - < 30 days: 1.1x
4. **Engagement Signals** - Social metrics
   - Reddit upvotes/comments
   - News shares
5. **Legislative Impact** - Regulatory relevance

## API Issues Fixed

### Issue 1: News API Parameter Error
**Error**: `news_api_wrapped() takes 0 positional arguments but 2 were given`
**Fix**: Changed from positional to keyword arguments
```python
# Before
news_data = await EnhancedAgentTools.news_api(query, limit)
# After
news_data = await EnhancedAgentTools.news_api(query=query, limit=limit)
```

### Issue 2: Patent API Parameter Error
**Error**: `patent_api_wrapped() takes 0 positional arguments but 2 were given`
**Fix**: Used keyword arguments and removed unsupported limit parameter
```python
# Before
patent_data = await EnhancedAgentTools.patent_api(query, limit)
# After
patent_data = await EnhancedAgentTools.patent_api(query=query)
```

### Issue 3: Memory Palace Import Error
**Error**: `cannot import name 'memory_palace_views' from 'memory.views'`
**Fix**: Corrected import path
```python
# Before
from memory.views import memory_palace_views
# After
from memory.views_memory_palace import MemoryPalaceViewSet
```

### Issue 4: Regulatory API NoneType Error
**Error**: `object of type 'NoneType' has no len()`
**Fix**: Added type checking for API responses
```python
# Added validation
if regs_data and isinstance(regs_data, dict) and regs_data.get('documents'):
    # Process results
```

## Response Format

### Search Results
```json
{
  "results": [
    {
      "id": "reddit_123",
      "source": "reddit",
      "title": "Looking for renewable energy solutions",
      "content": "Discussion about battery technology...",
      "url": "https://reddit.com/r/startups/...",
      "author": "user123",
      "date": "2025-07-16T10:00:00Z",
      "relevance_score": 0.92,
      "ml_insights": {
        "text_similarity": 0.85,
        "source_weight": 0.9,
        "recency_boost": 1.2
      },
      "tags": ["technology", "energy"],
      "metadata": {
        "subreddit": "r/startups",
        "score": 156,
        "num_comments": 42
      }
    }
  ],
  "total": 247,
  "hasMore": true,
  "facets": {
    "sources": {
      "reddit": 45,
      "news": 89,
      "sec": 23,
      "government": 90
    },
    "sectors": {
      "technology": 120,
      "energy": 95,
      "finance": 32
    },
    "dateRanges": {
      "today": 12,
      "week": 67,
      "month": 134,
      "year": 34
    }
  }
}
```

## Saved Searches & Collections

### Save a Search
```bash
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Energy Tech", "query": {"query": "renewable energy", "sources": "news,patents"}}' \
  http://localhost:8000/api/agent-orchestra/research/saved-searches/
```

### Create Collection
```bash
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Investment Opportunities", "description": "High-potential sectors"}' \
  http://localhost:8000/api/agent-orchestra/research/collections/
```

## Trends & Insights

### Get Trending Topics
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/agent-orchestra/research/trends/
```

Returns:
- Trending topics with scores
- Hot sectors by activity
- Legislative alerts
- Market signals

## AI Assistant

### Request AI Analysis
```bash
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the opportunities in quantum computing?"}' \
  http://localhost:8000/api/agent-orchestra/research/ai-assistant/
```

Returns:
- AI-generated insights
- Related search suggestions
- Action recommendations
- Market analysis

## Error Handling

### Fallback Mechanisms
All search sources have fallback handling:
1. Try real API
2. On failure, return graceful fallback
3. Continue with other sources
4. Never fail entire search

### Rate Limiting
- Results cached for 5 minutes
- API rate limits respected
- Automatic retry with backoff

## Testing the Feature

### Quick Test Script
```bash
# Basic search
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/agent-orchestra/research/search/?q=artificial+intelligence"

# Multi-source search with filters
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/agent-orchestra/research/search/?q=blockchain&sources=reddit,news,patents&date_range=week&min_score=0.7"

# Legislative impact search
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/agent-orchestra/research/search/?q=healthcare&legislative_impact=true"
```

## Performance Optimizations

### Caching
- Search results cached for 5 minutes
- User patterns cached
- Embedding cache for similarity

### Parallel Processing
- All data sources queried in parallel
- Async/await throughout
- Connection pooling

### Database Indexes
- Vector indexes for embeddings
- Text search indexes
- Date range indexes

## Future Enhancements

1. **Real-time Monitoring**
   - WebSocket updates for new results
   - Alert system for saved searches
   - Live trend tracking

2. **Advanced Analytics**
   - Cross-source correlation analysis
   - Predictive trend modeling
   - Sentiment analysis

3. **Export & Reporting**
   - PDF report generation
   - Data export (CSV, JSON)
   - Automated briefings

4. **Integration**
   - Slack notifications
   - Email digests
   - API webhooks

## Development Status

| Component | Status | Notes |
|-----------|--------|-------|
| Search Engine | ✅ Complete | All sources integrated |
| ML Scoring | ✅ Complete | Embeddings + heuristics |
| Reddit Integration | ✅ Complete | Full API support |
| News Integration | ✅ Fixed | Parameter issue resolved |
| SEC Integration | ✅ Complete | EDGAR API working |
| Government APIs | ✅ Fixed | Type checking added |
| Patent Search | ✅ Fixed | Parameter issue resolved |
| Memory Palace | ✅ Fixed | Import path corrected |
| Saved Searches | ✅ Complete | Database models ready |
| Collections | ✅ Complete | Organization system |
| Trends | ⚠️ Partial | Returns sample data |
| AI Assistant | ⚠️ Partial | Basic implementation |

## Key Files Reference

### Frontend
- Main: `/src/features/research-intelligence/ResearchIntelligence.tsx`
- Components: `/src/features/research-intelligence/components/*.tsx`
- Hooks: `/src/features/research-intelligence/hooks/*.ts`
- Services: `/src/services/api/research.service.ts`

### Backend
- Main Service: `/backend/agent_orchestra/services/research_intelligence_service.py`
- Views: `/backend/agent_orchestra/views_research_intelligence.py`
- Models: `/backend/agent_orchestra/models.py` (SavedSearch, ResearchCollection)
- URLs: `/backend/agent_orchestra/urls.py` (research section)
- Parameter Fixes: `/backend/agent_orchestra/api_parameter_fixes.py`

## Authentication
All endpoints require Token authentication:
```
Authorization: Token YOUR_TOKEN_HERE
```

## Common Issues and Solutions

### Issue: No results from certain sources
**Solution**: Check API keys in environment variables. Some sources may be rate-limited.

### Issue: Slow search performance
**Solution**: Reduce number of sources or use cached results. Check Redis cache status.

### Issue: Memory Palace not returning results
**Solution**: Ensure user has saved memories. Check UnifiedMemoryEntry table.

### Issue: Legislative impact filter not working
**Solution**: Requires LegislativeMLService to be configured with proper models.