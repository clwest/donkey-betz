# Section 5: Business Intelligence Systems
**Agent Name: Business Systems Reviewer**

## Scope Overview
This section covers the business intelligence features including stock analysis, Reddit opportunity discovery, and business planning systems.

### Primary Components:
- Stock Scout - Market intelligence and analysis
- Reddit Scout - Social media opportunity mining
- Business Hub - Business plan generation and management
- Financial data integration and analysis

## Analysis Instructions for Claude Code Agent

### 1. Stock Scout Implementation
**Investigate:**
- `backend/api/business_hub/views/stock_scout_views.py` - Stock endpoints
- `backend/api/business_hub/services/stock_service.py` - Stock data service
- `backend/api_services/polygon_service.py` - Polygon.io integration
- `backend/api/business_hub/models/stock_models.py` - Stock data models

**Key Questions:**
- How is real-time stock data fetched?
- What technical indicators are calculated?
- How are stock alerts configured?
- What is the WebSocket streaming setup?

### 2. Market Data Integration
**Investigate:**
- `backend/api_services/polygon_service.py` - Primary market data
- `backend/api_services/market_data_service.py` - Data aggregation
- `backend/api/business_hub/services/batch_quote_service.py` - Batch operations
- Cache implementations for rate limiting

**Key Questions:**
- What are the API rate limits?
- How is data cached?
- What fallback mechanisms exist?
- How are market hours handled?

### 3. Reddit Scout System
**Investigate:**
- `backend/api/business_hub/views/reddit_scout_views.py` - Reddit endpoints
- `backend/api/business_hub/services/reddit_service.py` - Reddit operations
- `backend/api/business_hub/models/reddit_idea.py` - Reddit data model
- `backend/api_services/reddit_api.py` - Reddit API wrapper

**Key Questions:**
- How are subreddits monitored?
- What scoring algorithms are used?
- How are duplicates prevented?
- What is the refresh strategy?

### 4. Business Opportunity Extraction
**Investigate:**
- `backend/api/business_hub/services/opportunity_extractor.py` - Extraction logic
- `backend/api/business_hub/services/idea_scorer.py` - Scoring algorithms
- `backend/api/business_hub/models/business_opportunity.py` - Opportunity model

**Key Questions:**
- How are opportunities identified?
- What scoring criteria exist?
- How are ideas prioritized?
- What filters are applied?

### 5. Business Hub Features
**Investigate:**
- `backend/api/business_hub/views/business_views.py` - Business endpoints
- `backend/api/business_hub/services/business_service.py` - Business operations
- `backend/universal_builder/` - Business plan generation
- `backend/api/business_hub/models/business.py` - Business model

**Key Questions:**
- How are business plans generated?
- What templates are available?
- How is progress tracked?
- What export formats exist?

### 6. Financial Analysis Tools
**Investigate:**
- `backend/agent_orchestra/agents/financial_analysis_agent.py` - Financial agent
- `backend/api/business_hub/services/financial_calculator.py` - Calculations
- `backend/api/business_hub/services/projection_service.py` - Projections

**Key Questions:**
- What financial metrics are calculated?
- How are projections generated?
- What data sources are used?
- How accurate are predictions?

### 7. Scout Hub Architecture
**Investigate:**
- `backend/api/scout_hub/` - Unified scout platform
- `backend/api/scout_hub/services/scout_aggregator.py` - Data aggregation
- `backend/api/scout_hub/models/` - Scout models

**Key Questions:**
- How are different scouts unified?
- What is the extensibility model?
- How is data normalized?
- What future scouts are planned?

### 8. Real-time Updates
**Investigate:**
- `backend/api/business_hub/consumers.py` - WebSocket consumers
- `backend/api/business_hub/routing.py` - WebSocket routing
- `backend/api/business_hub/services/realtime_service.py` - Real-time updates

**Key Questions:**
- How are real-time updates delivered?
- What events trigger updates?
- How is connection state managed?
- What is the reconnection strategy?

### 9. Data Quality & Validation
**Investigate:**
- `backend/api/business_hub/services/data_validator.py` - Validation logic
- `backend/api/business_hub/services/source_verifier.py` - Source verification
- `backend/api/business_hub/utils/data_quality.py` - Quality metrics

**Key Questions:**
- How is data quality ensured?
- What validation rules exist?
- How are anomalies detected?
- What happens with bad data?

### 10. Integration with AI Agents
**Investigate:**
- `backend/agent_orchestra/agents/market_research_agent.py` - Market agent
- `backend/agent_orchestra/agents/competitive_analysis_agent.py` - Competition agent
- `backend/api/business_hub/services/agent_integration.py` - Integration layer

**Key Questions:**
- How do agents access market data?
- What analysis do agents provide?
- How is agent data integrated?
- What are the execution patterns?

## Critical Files to Review
1. `backend/api_services/polygon_service.py` - Core market data service
2. `backend/api/business_hub/services/reddit_service.py` - Reddit mining logic
3. `backend/universal_builder/services/builder_service.py` - Business generation
4. `backend/api/business_hub/services/opportunity_extractor.py` - Opportunity logic
5. `backend/api/business_hub/consumers.py` - Real-time WebSocket handling

## Business Intelligence Components
1. **Stock Scout** - Real-time market intelligence
2. **Reddit Scout** - Social media opportunity mining
3. **Patent Scout** (planned) - IP opportunity discovery
4. **Twitter Scout** (planned) - Trending topic analysis
5. **Business Builder** - Automated business planning
6. **Financial Projector** - Revenue forecasting
7. **Market Analyzer** - Competition analysis
8. **Opportunity Ranker** - Idea prioritization

## Expected Outputs from Analysis
1. Complete data flow diagram
2. API integration inventory
3. WebSocket protocol documentation
4. Scoring algorithm analysis
5. Performance benchmarks
6. Data quality report
7. Scout extensibility guide
8. Business template catalog

## Special Considerations
- The migration from Alpha Vantage to Polygon.io
- Rate limiting and API cost management
- The "hypothetical data" issue in market analysis
- Reddit API changes and restrictions
- Real-time data accuracy requirements
- Business plan quality assurance
- Opportunity duplicate detection
- The 19 businesses created vs "350 deployments" myth