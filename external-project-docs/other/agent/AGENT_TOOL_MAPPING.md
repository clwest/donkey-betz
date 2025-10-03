# Agent Tool Mapping Documentation
Generated: July 9, 2025

## Overview
This document maps all available APIs/tools to the agents that should have access to them.

## Available Enhanced Tools (37 total)

### Financial Data APIs
- `yahoo_finance` - Real-time stock quotes and financial data
- `sec_edgar_api` - SEC filings and regulatory documents
- `earnings_api` - Earnings calendars and reports
- `polygon_market_data` - Professional market data
- `polygon_quote` - Real-time quotes
- `polygon_technicals` - Technical indicators
- `polygon_trades` - Trade data
- `polygon_options` - Options data
- `polygon_historical` - Historical data
- `polygon_flat_files` - Bulk data files
- `get_real_time_quote` - Quick quote lookup

### Research & Intelligence
- `web_search` - Internet search (Serper API)
- `news_api` - News aggregation
- `reddit_api` - Reddit discussions
- `reddit_trending_stocks` - Trending stock mentions
- `sentiment_api` - Sentiment analysis
- `statista_api` - Market statistics
- `patent_api` - Patent search
- `industry_reports` - Industry analysis

### Business Intelligence
- `crunchbase_api` - Startup and funding data
- `competitor_api` - Competitive analysis
- `github_api` - Code repositories
- `stackoverflow` - Technical Q&A

### Government & Legal
- `congress_api` - Congressional data
- `federal_register` - Federal regulations
- `gov_contracts_api` - Government contracts

### Data Processing & Generation
- `data_analyzer` - Comprehensive analysis
- `spreadsheet_generator` - Financial models
- `chart_creator` - Visualizations
- `pdf_generator` - Report generation
- `document_generator` - Document creation
- `trend_detector` - Pattern detection
- `risk_calculator` - Risk assessment
- `comparison_tool` - Comparative analysis
- `alert_system` - Notifications
- `calendar_checker` - Event tracking

## Current Agent Assignments

### Financial Agents (11 agents)
**Have access to:** 8-11 tools each
**Should also have:** `polygon_technicals`, `polygon_trades`, `polygon_options`

### Research Agents (7 agents)
**Have access to:** 3-8 tools each
**Should also have:** More financial APIs for comprehensive research

### Business Agents (2 agents)
**Have access to:** 8-10 tools each
**Well configured**

### Technical Agents (5 agents)
**Have access to:** 2-9 tools each
**Should also have:** More API integration tools

### Marketing Agents (3 agents)
**Have access to:** 8-9 tools each
**Well configured**

### Stock Scout Agents (missing in list!)
**Should have:** `reddit_api`, `sentiment_api`, `yahoo_finance`, `polygon_market_data`, `news_api`, `trend_detector`

## Key Findings

1. **Most agents are reasonably well-configured** with 8-10 tools
2. **Polygon.io APIs are underutilized** - Only basic `yahoo_finance` is assigned, missing specialized Polygon tools
3. **Stock Scout agents** don't appear in the template list but are crucial
4. **Some specialized agents have too few tools** (Technical Chart Agent has only 2)

## Recommendations

1. **Add Polygon Technical APIs** to all financial agents:
   - `polygon_technicals` for technical indicators
   - `polygon_options` for options analysis
   - `polygon_trades` for detailed trade data

2. **Enhance Research Agents** with more data sources:
   - Add financial APIs to research agents for comprehensive analysis
   - Include `reddit_trending_stocks` for social sentiment

3. **Create/Update Stock Scout Agent Templates** with appropriate tools

4. **Verify Tool Execution** - Ensure agents can actually call these tools through the enhanced_agent_service.py

## Tool Categories by Agent Type

### Financial/Stock Analysis Agents Should Have:
- All Polygon APIs (market_data, quote, technicals, trades, options, historical)
- `yahoo_finance`, `sec_edgar_api`, `earnings_api`
- `news_api`, `sentiment_api`, `reddit_api`
- `risk_calculator`, `trend_detector`, `chart_creator`
- `spreadsheet_generator`, `pdf_generator`

### Research/Intelligence Agents Should Have:
- `web_search`, `news_api`, `statista_api`
- `patent_api`, `industry_reports`
- `crunchbase_api`, `competitor_api`
- `reddit_api`, `sentiment_api`
- `document_generator`, `pdf_generator`

### Business Strategy Agents Should Have:
- `crunchbase_api`, `competitor_api`, `industry_reports`
- `web_search`, `news_api`, `statista_api`
- `gov_contracts_api` (for B2G opportunities)
- `trend_detector`, `comparison_tool`
- `spreadsheet_generator`, `pdf_generator`

### Technical/Development Agents Should Have:
- `github_api`, `stackoverflow`, `patent_api`
- `web_search`, `competitor_api`
- `trend_detector`, `comparison_tool`
- `document_generator`

### Marketing Agents Should Have:
- `reddit_api`, `sentiment_api`, `news_api`
- `competitor_api`, `trend_detector`
- `statista_api` (for market data)
- `chart_creator`, `pdf_generator`
- `alert_system` (for campaigns)