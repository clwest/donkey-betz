# Claude Code Implementation Guide: Unified API Access for All Agents

## Executive Summary for Claude Code

**Project**: move_that_ass  
**Location**: /Users/donkeyking/development/move_that_ass  
**Problem**: Multiple agent types (Stock Scout, Reddit Scout, regular Agents) can't consistently access the same 40+ APIs. When one type gets access, others lose it.  
**Solution**: Create a unified tool configuration system that ensures all agents have proper API access.

## Context for Claude Code

This project has ~40 APIs that ALL AI agents should access. Currently:
- Agents use generic tool names like "financial_data" or "technical_analysis"
- These need to map to specific APIs like "polygon_market_data" or "polygon_technicals"
- Different agent types (Stock Scout, Reddit Scout, Financial Agents) are getting different tool sets
- The tool mapping in `enhanced_sync_executor.py` is incomplete

## Task 1: Create Unified Tool Configuration

**File to create**: `/Users/donkeyking/development/move_that_ass/backend/agent_orchestra/unified_tool_config.py`

**Purpose**: Single source of truth for all tool definitions and agent assignments

**Requirements**:
- Define all 40+ tools with descriptions
- Create tool aliases (e.g., "financial_data" → "polygon_market_data")
- Define which tools each agent type should have
- Provide methods to resolve tool names and get tools for any agent type

**Key sections to implement**:
1. `ALL_TOOLS` dictionary with all 40+ available APIs
2. `TOOL_ALIASES` mapping generic names to specific APIs
3. `AGENT_TOOL_SETS` defining which tools each agent type gets
4. Methods: `get_tools_for_agent()`, `resolve_tool_name()`, `get_all_tools()`

**Special agent types to support**:
- `stock_scout`: Needs all financial APIs + Reddit + sentiment
- `reddit_scout`: Needs Reddit API + sentiment + basic financial
- `financial_analyst`: Needs all financial and analysis tools
- `market_intelligence`: Needs research and competitive tools

## Task 2: Update Enhanced Sync Executor

**File to modify**: `/Users/donkeyking/development/move_that_ass/backend/agent_orchestra/enhanced_sync_executor.py`

**Changes needed**:
1. Add import: `from .unified_tool_config import UnifiedToolConfig`
2. In the `_process_tool_calls_with_error_tracking` method, replace the hardcoded `tool_aliases` dictionary with:
   ```python
   actual_tool_name = UnifiedToolConfig.resolve_tool_name(tool_name)
   ```
3. Add logging when a tool alias is resolved to actual name

## Task 3: Create Tool Access Monitor

**File to create**: `/Users/donkeyking/development/move_that_ass/backend/agent_orchestra/tool_access_monitor.py`

**Purpose**: Monitor and auto-fix tool access issues

**Key methods**:
- `validate_agent_tools()`: Check if agent has correct tools
- `ensure_tool_access()`: Auto-fix missing tools
- `get_orchestration_tool_status()`: Check all agents in an orchestration

## Task 4: Create Management Command

**File to create**: `/Users/donkeyking/development/move_that_ass/backend/agent_orchestra/management/commands/update_agent_tools.py`

**Purpose**: Update all existing agent templates with correct tools

**Requirements**:
- Map agent names to agent types
- Update each template with tools from UnifiedToolConfig
- Create Stock Scout and Reddit Scout templates if missing
- Show before/after tool counts

## Task 5: Integration Points

**Update these existing files**:

1. **`enhanced_agent_service.py`**: 
   - In `execute_agent_with_resilience()`, add at the beginning:
     ```python
     from agent_orchestra.tool_access_monitor import ToolAccessMonitor
     ToolAccessMonitor.ensure_tool_access(agent)
     ```

2. **Any orchestration creation code**:
   - After creating orchestration, add validation:
     ```python
     from agent_orchestra.tool_access_monitor import ToolAccessMonitor
     status = ToolAccessMonitor.get_orchestration_tool_status(orchestration.id)
     ```

## Testing Instructions

After implementation, test with:

```bash
# Update all agent templates
cd /Users/donkeyking/development/move_that_ass/backend
python manage.py update_agent_tools

# Test in Django shell
python manage.py shell
```

```python
# In shell, verify configuration
from agent_orchestra.unified_tool_config import UnifiedToolConfig

# Check Stock Scout gets all needed tools
stock_tools = UnifiedToolConfig.get_tools_for_agent('stock_scout')
print(f"Stock Scout has {len(stock_tools)} tools")
print("Has Polygon APIs:", any('polygon' in t for t in stock_tools))
print("Has Reddit API:", 'reddit_api' in stock_tools)

# Check tool resolution works
print(UnifiedToolConfig.resolve_tool_name('financial_data'))  # Should return 'polygon_market_data'
print(UnifiedToolConfig.resolve_tool_name('technical_analysis'))  # Should return 'polygon_technicals'

# Check all agent types
for agent_type in ['stock_scout', 'reddit_scout', 'financial_analyst']:
    tools = UnifiedToolConfig.get_tools_for_agent(agent_type)
    print(f"{agent_type}: {len(tools)} tools")
```

## Success Criteria

1. **All agents get consistent tools**: Same agent type = same tools every time
2. **Tool aliases work**: Agents can use "financial_data" and get "polygon_market_data"
3. **No more switching issues**: Stock Scout having access doesn't break Reddit Scout
4. **All 40+ APIs accessible**: Every agent type can access appropriate APIs
5. **Auto-fixing works**: Missing tools are automatically added

## Implementation Order

1. Create `unified_tool_config.py` first (it's standalone)
2. Create `tool_access_monitor.py` (depends on config)
3. Update `enhanced_sync_executor.py` to use the config
4. Create the management command
5. Run the command to update all templates
6. Update integration points in other files
7. Test everything works

## Notes for Claude Code

- The existing code has ~40 APIs defined in `enhanced_tools.py`
- Agent templates are stored in the database (Django models)
- The project uses Django with async support
- Logs are important - add logging for tool resolution
- Some agents might have custom names - map them in the management command

## Expected Outcome

After implementation:
- Stock Market Scout will reliably access Polygon APIs, Reddit, and sentiment
- Reddit Scout will access Reddit API and market data
- Financial Agents will have all financial tools
- No more "musical chairs" with API access
- One configuration file controls everything

This unified system will prove that AI agents can work together harmoniously when given proper architectural guidance!