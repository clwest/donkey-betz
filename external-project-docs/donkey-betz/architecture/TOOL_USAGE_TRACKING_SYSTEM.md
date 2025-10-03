# Tool Usage Tracking System

## Overview

The Tool Usage Tracking System provides comprehensive visibility into how agents use tools during their execution. This system tracks every tool call with performance metrics, success/failure rates, and detailed usage statistics.

## Features Implemented

### 1. ToolUsage Model
- **Location**: `agent_orchestra/models.py`
- **Tracks**: Tool name, agent, user, orchestration context, parameters, results, timing, success status
- **Indexes**: Optimized for querying by tool name, agent, user, and timestamp
- **Performance Metrics**: Response time, success rate, data size, token consumption

### 2. Enhanced Executor Integration
- **Location**: `agent_orchestra/enhanced_sync_executor.py`
- **Features**:
  - Automatic tool usage logging for every tool call
  - Timing measurement with millisecond precision
  - Error capture with detailed error messages
  - Step context tracking
  - Success/failure status recording

### 3. Tool Usage Statistics API
- **Endpoint**: `GET /api/agent-orchestra/tool-usage/statistics/`
- **Query Parameters**:
  - `days`: Number of days to look back (default: 30)
  - `agent_type`: Filter by agent template name
  - `tool_name`: Filter by specific tool name

### 4. Enhanced Tool Visibility
- **Agent Reports**: Tool usage section with success rates and timing
- **Step Results**: Clear tool call formatting with emojis and status indicators
- **AgentResult Integration**: Tool usage summary included in all results

## API Response Format

```json
{
  "overview": {
    "total_tool_calls": 150,
    "successful_calls": 142,
    "failed_calls": 8,
    "overall_success_rate": 94.67,
    "avg_response_time_ms": 1250,
    "date_range_days": 30
  },
  "most_used_tools": [
    {
      "tool_name": "web_search",
      "usage_count": 45,
      "success_count": 43,
      "success_rate": 95.56,
      "avg_response_time": 850,
      "total_response_time": 38250
    }
  ],
  "agent_tool_usage": [
    {
      "agent__template__name": "Market Intelligence Agent",
      "tool_name": "web_search",
      "usage_count": 25,
      "success_rate": 96.0
    }
  ],
  "recent_activity": {
    "last_24h_usage": 12,
    "last_24h_success_rate": 91.67
  },
  "performance_trends": [
    {
      "hour": "2025-01-22T10:00:00Z",
      "call_count": 5,
      "success_count": 5,
      "success_rate": 100.0,
      "avg_response_time": 1100
    }
  ],
  "slowest_tools": [
    {
      "tool_name": "statista_api",
      "avg_response_time": 3500,
      "usage_count": 8
    }
  ],
  "error_prone_tools": [
    {
      "tool_name": "reddit_api",
      "total_calls": 12,
      "failed_calls": 3,
      "failure_rate": 25.0
    }
  ]
}
```

## Database Schema

```sql
CREATE TABLE agent_orchestra_toolusage (
    id SERIAL PRIMARY KEY,
    tool_name VARCHAR(100) NOT NULL,
    agent_id INTEGER REFERENCES agent_orchestra_agentinstance(id),
    user_id INTEGER REFERENCES auth_user(id),
    orchestration_id INTEGER REFERENCES agent_orchestra_taskorchestration(id),
    step_description VARCHAR(500),
    parameters JSONB DEFAULT '{}',
    result_data JSONB DEFAULT '{}',
    success BOOLEAN DEFAULT TRUE,
    response_time_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_consumed INTEGER DEFAULT 0,
    data_size_bytes INTEGER DEFAULT 0
);

-- Indexes for optimal performance
CREATE INDEX idx_toolusage_tool_timestamp ON agent_orchestra_toolusage(tool_name, timestamp DESC);
CREATE INDEX idx_toolusage_agent_tool ON agent_orchestra_toolusage(agent_id, tool_name);
CREATE INDEX idx_toolusage_user_timestamp ON agent_orchestra_toolusage(user_id, timestamp DESC);
CREATE INDEX idx_toolusage_success_tool ON agent_orchestra_toolusage(success, tool_name);
```

## Usage Examples

### 1. Get Overall Tool Statistics
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/agent-orchestra/tool-usage/statistics/"
```

### 2. Filter by Date Range
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/agent-orchestra/tool-usage/statistics/?days=7"
```

### 3. Filter by Agent Type
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/agent-orchestra/tool-usage/statistics/?agent_type=Market%20Intelligence"
```

### 4. Filter by Specific Tool
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/agent-orchestra/tool-usage/statistics/?tool_name=web_search"
```

## Tool Visibility Enhancements

### In Agent Reports
Each agent report now includes a comprehensive tool usage section:

```markdown
## 🔧 Tools and Data Sources Used:

- ✅ **Web Search Tool**
  - Used 3 time(s) with 100% success rate
  - Average response time: 850ms
  - Used for: Market research, Competitive analysis

- ⚠️ **Reddit API Tool**
  - Used 2 time(s) with 50% success rate
  - Average response time: 2100ms
  - Used for: Social sentiment analysis

*All data above is from real API calls made during this analysis.*
```

### In Step Results
Tool calls are now clearly visible with status indicators:

```markdown
🔧 **Web Search Tool Results:**

✅ **Success** - 
1. **OpenAI Valued at $86 Billion in Latest Funding Round**
   OpenAI has raised funding at an $86 billion valuation...
   🔗 https://techcrunch.com/2024/openai-valuation

*End of Web Search Tool results*
```

## Performance Considerations

1. **Lightweight Logging**: Tool usage logging is designed to be lightweight and not slow down agent execution
2. **Database Indexes**: Comprehensive indexing for fast queries on tool statistics
3. **Error Handling**: Logging failures don't interrupt agent execution
4. **Data Retention**: Consider implementing data retention policies for long-term deployments

## Monitoring and Analytics

### Key Metrics to Track
- **Tool Success Rates**: Identify unreliable tools
- **Response Times**: Monitor tool performance
- **Usage Patterns**: Understand which tools are most valuable
- **Agent Efficiency**: Compare tool usage across agent types
- **Error Trends**: Identify patterns in tool failures

### Alerts and Notifications
Consider setting up alerts for:
- Tool success rates dropping below 80%
- Response times exceeding 5 seconds
- High error rates for specific tools
- Unusual usage spikes

## Testing

Run the test script to verify the system:

```bash
python test_tool_usage_tracking.py
```

The test script will:
1. Check for recent tool usage data
2. Display statistics and performance metrics
3. Simulate API responses
4. Verify system readiness

## Future Enhancements

1. **Real-time Dashboards**: Live tool usage monitoring
2. **Cost Tracking**: Track API costs per tool
3. **Performance Optimization**: Automatic tool selection based on performance
4. **Historical Analysis**: Long-term trends and patterns
5. **Tool Recommendations**: Suggest optimal tools for specific tasks

## Files Modified/Created

### New Files
- `test_tool_usage_tracking.py` - Test script for the tracking system
- `documentation/TOOL_USAGE_TRACKING_SYSTEM.md` - This documentation

### Modified Files
- `agent_orchestra/models.py` - Added ToolUsage model
- `agent_orchestra/enhanced_sync_executor.py` - Added tool usage logging
- `agent_orchestra/views.py` - Added statistics API endpoint
- `agent_orchestra/urls.py` - Added API route
- `agent_orchestra/migrations/0025_toolusage.py` - Database migration

## Integration Status

✅ **Model Created**: ToolUsage model with comprehensive fields and indexes
✅ **Executor Integration**: Enhanced sync executor logs all tool calls
✅ **Statistics API**: Full-featured API with filtering and analytics
✅ **Visibility Enhanced**: Clear tool usage in reports and step results
✅ **Database Migration**: Schema updated and ready
✅ **Testing**: Test script validates system functionality

The tool usage tracking system is now fully operational and ready to provide comprehensive insights into agent tool usage patterns, performance, and reliability.