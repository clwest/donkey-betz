# Agent Tool Fix Plan
Generated: July 9, 2025

## Issue Summary
Agents don't know about all available APIs because:
1. Stock Analysis Agent uses generic tool names (`financial_data`, `technical_analysis`) 
2. These generic names need to be mapped to specific APIs (`yahoo_finance`, `polygon_technicals`)
3. The enhanced_sync_executor.py has incomplete mappings

## Current State

### Stock Analysis Agent Tools:
- `web_search` ✅ (mapped correctly)
- `financial_data` ❌ (needs mapping to specific APIs)
- `news` ❌ (needs mapping to `news_api`)
- `reddit` ❌ (needs mapping to `reddit_api`)
- `market_research` ❌ (needs mapping)
- `technical_analysis` ❌ (needs mapping to polygon APIs)
- `sentiment_analysis` ❌ (needs mapping to `sentiment_api`)
- `data_analyzer` ✅ (exists)

## Solution

### 1. Update Tool Aliases in enhanced_sync_executor.py
Add mappings for generic tool names:
```python
tool_aliases = {
    # Existing aliases
    'sec_api': 'sec_edgar_api',
    'stock_api': 'yahoo_finance',
    'stock_market_api': 'yahoo_finance',
    'technical_analysis_api': 'yahoo_finance',
    
    # Add these new mappings
    'financial_data': 'yahoo_finance',  # Or 'polygon_market_data'
    'news': 'news_api',
    'reddit': 'reddit_api',
    'market_research': 'statista_api',
    'technical_analysis': 'polygon_technicals',
    'sentiment_analysis': 'sentiment_api',
    'technical': 'polygon_technicals',
    'sentiment': 'sentiment_api'
}
```

### 2. Update execute_tool Method
The EnhancedAgentTools.execute_tool needs to handle these mapped names.

### 3. Enhanced Prompt Updates
Ensure agents are told explicitly about their available tools in prompts.

## Implementation Steps

1. **Update enhanced_sync_executor.py**
   - Add comprehensive tool aliases
   - Map generic names to specific APIs

2. **Verify EnhancedAgentTools.execute_tool**
   - Ensure it can handle all tool names
   - Add fallback for unknown tools

3. **Update Agent Templates**
   - Consider updating to use specific tool names
   - Or ensure mapping layer works perfectly

4. **Test with Stock Analysis Agent**
   - Run a stock analysis task
   - Verify all tools are called correctly
   - Check that Polygon APIs are used for technical analysis

## Benefits
- Agents will have access to all 40+ APIs
- Stock Scout will use Polygon.io for technical analysis
- Financial agents will get real-time data
- Better data quality and accuracy