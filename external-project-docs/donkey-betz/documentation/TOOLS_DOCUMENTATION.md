# Agent Tools Documentation

## Overview
This document provides comprehensive documentation for all available tools in the Agent Orchestra system. Each tool is categorized by its purpose and includes information about required parameters, API dependencies, and usage examples.

## Tool Categories

### 1. Core Tools (Always Available)

#### web_search
- **Description**: Perform web search using a search API
- **Parameters**: 
  - `query` (str): Search query
  - `num_results` (int, default=5): Number of results to return
- **API Required**: SERPER_API_KEY
- **Returns**: Structured search results with title, link, and snippet

#### web_fetch
- **Description**: Fetch content from a URL and extract text or specific elements
- **Parameters**:
  - `url` (str): The URL to fetch
  - `extract_text` (bool, default=True): Whether to extract text content
  - `selector` (str, optional): CSS selector for specific elements
- **API Required**: None
- **Returns**: Dictionary with url, title, content, and metadata

#### data_analyzer
- **Description**: Analyze data and extract insights
- **Parameters**:
  - `data` (Dict): Data to analyze
  - `analysis_type` (str, default='general'): Type of analysis
- **API Required**: None
- **Returns**: Analysis results with key metrics and insights

#### document_generator
- **Description**: Generate formatted documents
- **Parameters**:
  - `content` (str): Document content
  - `format` (str, default='markdown'): Output format
  - `title` (str, optional): Document title
- **API Required**: None
- **Returns**: Formatted document

### 2. Financial & Market Data Tools

#### polygon_market_data
- **Description**: Get comprehensive market data from Polygon API
- **Parameters**:
  - `symbol` (str): Stock symbol
  - `data_type` (str): Type of data (quote, aggregates, trades, etc.)
  - Additional parameters vary by data_type
- **API Required**: POLYGON_API_KEY
- **Returns**: Market data based on requested type

#### sec_edgar_api
- **Description**: Access SEC EDGAR filings
- **Parameters**:
  - `symbol` (str, optional): Company stock symbol
  - `company` (str, optional): Company name
  - `filing_type` (str, optional): Type of filing (10-K, 10-Q, etc.)
- **API Required**: SEC_API_KEY (optional, enhances rate limits)
- **Returns**: SEC filing data

#### earnings_api
- **Description**: Get earnings data and calendar
- **Parameters**:
  - `symbol` (str, optional): Stock symbol
  - `timeframe` (str, default='upcoming'): upcoming, historical, or calendar
- **API Required**: ALPHA_VANTAGE_API_KEY
- **Returns**: Earnings data with estimates and actuals

### 3. News & Research Tools

#### news_api
- **Description**: Search news articles
- **Parameters**:
  - `query` (str): Search query
  - `category` (str, default='business'): News category
  - `limit` (int, default=10): Number of articles
- **API Required**: NEWS_API_KEY
- **Returns**: News articles with title, description, url, and publishedAt

#### reddit_api
- **Description**: Access Reddit data
- **Parameters**:
  - `subreddit` (str, optional): Specific subreddit
  - `subreddits` (List[str], optional): Multiple subreddits
  - `limit` (int, default=25): Number of posts
  - `sort` (str, default='hot'): Sort order (hot, new, top)
  - `search_parameters` (Dict, optional): Search filters
- **API Required**: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
- **Returns**: Reddit posts with title, score, comments, and sentiment

### 4. Government & Legal Tools

#### congress_api
- **Description**: Access congressional data
- **Parameters**:
  - `query` (str, optional): Search query
  - `chamber` (str, optional): house or senate
  - `limit` (int, default=20): Number of results
- **API Required**: None (uses public API)
- **Returns**: Congressional bills and member information

#### federal_register
- **Description**: Search Federal Register documents
- **Parameters**:
  - `query` (str): Search query
  - `document_type` (str, default='rule'): Document type
- **API Required**: None (uses public API)
- **Returns**: Federal Register documents

#### gov_contracts_api
- **Description**: Search government contracts
- **Parameters**:
  - `query` (str): Search query
  - `agency` (str, optional): Specific agency
- **API Required**: None (uses public API)
- **Returns**: Government contract data

### 5. Technical & Development Tools

#### github_api
- **Description**: Search GitHub repositories and code
- **Parameters**:
  - `query` (str): Search query
  - `search_type` (str, default='repositories'): repositories, code, or issues
- **API Required**: GITHUB_TOKEN (optional, increases rate limits)
- **Returns**: GitHub search results

#### stackoverflow
- **Description**: Search Stack Overflow
- **Parameters**:
  - `query` (str): Search query
  - `tags` (List[str], optional): Filter by tags
- **API Required**: None
- **Returns**: Stack Overflow questions and answers

#### patent_api
- **Description**: Search patent database
- **Parameters**:
  - `query` (str): Search query
  - `classification` (str, optional): Patent classification
- **API Required**: None
- **Returns**: Patent search results

### 6. Business Intelligence Tools

#### industry_reports
- **Description**: Get industry analysis and reports
- **Parameters**:
  - `industry` (str): Industry name
  - `report_type` (str, default='overview'): Type of report
- **API Required**: None (uses internal data)
- **Returns**: Industry analysis with market size, trends, and leaders

#### competitor_api
- **Description**: Analyze competitors
- **Parameters**:
  - `company` (str, optional): Company name
  - `industry` (str, optional): Industry for comparison
  - `query` (str, optional): Search query
- **API Required**: None (aggregates from multiple sources)
- **Returns**: Competitor analysis

### 7. System Introspection Tools

#### database_introspection
- **Description**: Query and analyze the agent system's own data
- **Parameters**:
  - `action` (str): Action to perform
  - Additional parameters vary by action
- **API Required**: None
- **Actions**: query_deployments, query_beliefs, find_stuck_agents, analyze_code, trace_agent

#### system_architecture_map
- **Description**: Get comprehensive AI system architecture
- **Parameters**: None
- **API Required**: None
- **Returns**: System component map

### 8. Memory & Knowledge Tools

#### search_ukf_memories
- **Description**: Search unified memory system
- **Parameters**:
  - `query` (str): Search query
  - `user_id` (int): User ID
  - `limit` (int, default=10): Number of results
  - `search_type` (str, default='semantic'): semantic or keyword
- **API Required**: None
- **Returns**: Relevant memories with similarity scores

## Tool Usage Examples

### Example 1: Web Search
```python
result = await EnhancedAgentTools.web_search(
    query="AI market trends 2024",
    num_results=10
)
```

### Example 2: Stock Market Data
```python
result = await EnhancedAgentTools.polygon_market_data(
    symbol="AAPL",
    data_type="quote"
)
```

### Example 3: Reddit Sentiment Analysis
```python
result = await EnhancedAgentTools.reddit_api(
    subreddits=["stocks", "wallstreetbets"],
    search_parameters={"q": "NVDA"},
    limit=50
)
```

## API Configuration

To enable specific tools, configure the following environment variables:

```bash
# Web Search
SERPER_API_KEY=your_key

# Market Data
POLYGON_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key

# News & Social
NEWS_API_KEY=your_key
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=your_agent

# Development
GITHUB_TOKEN=your_token  # Optional, increases rate limits

# AI Services (for agent execution)
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_GENERATIVE_AI_KEY=your_key
```

## Tool Availability Checking

Before agent execution, check tool availability:

```python
from agent_orchestra.utils.tool_availability import ToolAvailabilityChecker

# Get availability report
report = ToolAvailabilityChecker.get_availability_report()
print(report)

# Check specific agent's tools
validation = ToolAvailabilityChecker.validate_agent_tools(agent_template)
if not validation['valid']:
    print(f"Missing tools: {validation['missing_tools']}")
    print(f"Missing APIs: {validation['missing_apis']}")
```

## Error Handling

All tools implement comprehensive error handling:

1. **API Unavailable**: Returns error message with suggestion to contact support
2. **Parameter Mismatch**: Automatically filters to valid parameters
3. **Missing Required Parameters**: Provides smart defaults where possible
4. **Rate Limits**: Returns appropriate error messages

## Performance Considerations

1. **Caching**: Many tools implement caching to reduce API calls
2. **Batch Operations**: Some tools support batch requests
3. **Async Execution**: All tools are async for concurrent execution
4. **Parameter Validation**: Tools validate and sanitize inputs

## Adding New Tools

To add a new tool:

1. Add the method to `EnhancedAgentTools` class
2. Add tool mapping in `execute_tool` method
3. Add parameter mappings if needed
4. Update API requirements in `tool_availability.py`
5. Document the tool in this file

## Troubleshooting

### Common Issues

1. **"Tool not found" error**: Check tool name in execute_tool mapping
2. **"API not configured" error**: Check environment variables
3. **Parameter errors**: Check parameter mappings and defaults
4. **No results**: Verify API keys and rate limits

### Debug Mode

Enable debug logging to see tool execution details:

```python
import logging
logging.getLogger('agent_orchestra.enhanced_tools').setLevel(logging.DEBUG)
```