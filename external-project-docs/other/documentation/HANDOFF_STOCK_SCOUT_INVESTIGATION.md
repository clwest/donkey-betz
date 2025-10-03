# Stock Scout Investigation - July 8, 2025

## Current Issues

### 1. Stock Scout Not Finding Stocks
- Recent Stock Scout reports show no stocks in results
- Agent appears to be running but not extracting opportunities

### 2. Scout Hub Display Issues  
- Stock data in Scout Hub Stock Market Scout is "way off"
- Listed stocks are not updating when new scouts run
- Data appears stale or incorrect

### 3. No Opportunity Extraction
- Stock opportunities not being saved to database
- Scout missions complete but show 0 opportunities found

## Investigation Areas

### 1. Agent Execution
Check if Stock Scout agents are actually running:
```bash
# Check recent orchestrations
python manage.py shell
>>> from agent_orchestra.models import TaskOrchestration, AgentInstance
>>> recent = TaskOrchestration.objects.filter(master_task__icontains='Stock Scout').order_by('-created_at')[:5]
>>> for t in recent:
...     print(f"{t.id}: {t.overall_status} - Agents: {t.agents.count()}")
```

### 2. Agent Results
Verify agents are producing results:
```python
# Check agent outputs
>>> orchestration = TaskOrchestration.objects.get(id=XXX)  # Use ID from above
>>> for agent in orchestration.agents.all():
...     print(f"{agent.agent_type}: {agent.status}")
...     if agent.result:
...         print(f"  Has result: {len(str(agent.result))} chars")
```

### 3. Opportunity Extraction
Check if opportunities are being extracted:
```python
# Check StockOpportunity model
>>> from agent_orchestra.models_stock_opportunities import StockOpportunity
>>> StockOpportunity.objects.filter(scout_orchestration__id=XXX).count()
```

### 4. Auto-Extractor Service
The `StockOpportunityAutoExtractor` should run after scout completion:
- Located at: `/backend/agent_orchestra/services/stock_opportunity_auto_extractor.py`
- Should be triggered by signal when orchestration completes

### 5. Frontend Data Source
Scout Hub might be showing:
- Cached/stale data
- Mock data instead of real API calls
- Data from wrong endpoint

## Debugging Steps

1. **Run a test Stock Scout**:
   ```bash
   # From Django shell
   from agent_orchestra.services.stock_scout_service import StockScoutService
   result = StockScoutService.scout_stock_opportunities(
       user=User.objects.get(username='testuser'),
       scout_type='penny_stocks'
   )
   print(f"Orchestration ID: {result['orchestration_id']}")
   ```

2. **Monitor the orchestration**:
   - Check Django admin for orchestration status
   - Look at agent results
   - Check if signal handlers fire

3. **Check logs**:
   ```bash
   tail -f backend/logs/app.log | grep -i "stock"
   tail -f backend/logs/errors.log | grep -i "scout"
   ```

4. **Verify API endpoints**:
   - `/api/agent-orchestra/stocks/scout/missions/`
   - `/api/agent-orchestra/stocks/scout/{id}/results/`
   - `/api/agent-orchestra/stock-opportunities/`

## Key Files to Check

1. **Backend**:
   - `/backend/agent_orchestra/services/stock_scout_service.py` - Main scout service
   - `/backend/agent_orchestra/services/stock_opportunity_extractor_improved.py` - Extraction logic
   - `/backend/agent_orchestra/services/stock_opportunity_auto_extractor.py` - Auto extraction
   - `/backend/agent_orchestra/views_stock_scout.py` - API endpoints
   - `/backend/agent_orchestra/signals.py` - Signal handlers

2. **Frontend**:
   - `/donkey-betz-frontend/src/features/scout-hub/pages/StockScout.tsx`
   - `/donkey-betz-frontend/src/services/api/stockScout.service.ts`

## Potential Fixes

1. **If agents aren't running**: Check Celery workers and Redis
2. **If extraction failing**: Debug the extractor regex patterns
3. **If signals not firing**: Check signal connections in apps.py
4. **If frontend showing wrong data**: Verify API endpoints and remove any mock data

## Next Session Goals

1. Get Stock Scout finding real stocks again
2. Fix Scout Hub data display
3. Ensure opportunities are properly extracted and saved
4. Verify frontend is using real API data