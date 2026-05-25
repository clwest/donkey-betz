# Session 683 - ML Assistant Integration Complete

**Date:** January 5, 2026
**Previous Session:** 682 (Model Auto-Selection Phase 6)
**Focus:** Integrate Agent-Model Router with GPT Assistant & Agents
**Status:** COMPLETE

---

## Overview

This session integrates the completed Agent-Model Router (Sessions 677-682) with:
1. GPT-5-mini Assistant (new ML Analysis tool)
2. Four key agents (MarketIntelligence, StockAnalyst, WhaleWatcher, OpportunityScoring)

---

## Part 1: ML Analysis Tool for GPT

### Goal
Add `ml_analysis` tool so GPT can invoke ML models for data analysis.

### Files to Modify

**1. `core/assistant/tool_definitions.py`**
Add new tool definition:
```python
def _get_ml_analysis_tool_definition() -> Dict:
    return {
        "type": "function",
        "name": "ml_analysis",
        "description": "Analyze data using ML models. Auto-selects optimal model based on data type (time series, graph, text, anomaly detection). Use for: price predictions, network analysis, anomaly detection, trend forecasting.",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Data to analyze. Can be: time series (with timestamps/values), graph (nodes/edges), text, or numerical arrays."
                },
                "task_type": {
                    "type": "string",
                    "enum": ["auto", "time_series", "graph", "text", "anomaly", "clustering", "classification", "decision"],
                    "default": "auto",
                    "description": "Type of analysis. Use 'auto' to let the system detect."
                },
                "analysis_goal": {
                    "type": "string",
                    "description": "What you want to learn from the data (e.g., 'predict next price', 'find anomalies', 'identify clusters')"
                }
            },
            "required": ["data"]
        }
    }
```

**2. `core/prompts/tool_descriptions.py`**
Add description:
```python
"ml_analysis": """Use this tool to analyze data with ML models. The system auto-selects the best model:
- Time series data (prices, metrics) → LSTM, Prophet for forecasting
- Graph data (networks, relationships) → GNN for community detection, link prediction
- Anomaly detection → VAE Autoencoder, Isolation Forest
- Decision optimization → Reinforcement Learning

Returns: predictions, confidence scores, model explanation."""
```

**3. `core/views_personal_assistant.py`**
Add handler for ml_analysis tool calls:
```python
def handle_ml_analysis(args: dict) -> dict:
    from core.services.agent_model_router import get_agent_model_router
    from ml.auto_selection import TaskType

    router = get_agent_model_router()
    data = args.get('data', {})
    task_type_str = args.get('task_type', 'auto')

    # Map string to TaskType enum
    task_hint = None
    if task_type_str != 'auto':
        task_hint = TaskType(task_type_str)

    result = router.auto_route(data, task_hint=task_hint)

    return {
        'success': result.success,
        'task_detected': result.auto_selection.get('task_type'),
        'models_used': result.models_used,
        'score': result.score,
        'confidence': result.confidence,
        'analysis': result.explanation,
        'selection_reason': result.auto_selection.get('selection_reason'),
    }
```

---

## Part 2: Agent ML Integration

### Agents to Integrate

| Agent | ML Model | Use Case |
|-------|----------|----------|
| MarketIntelligenceAgent | GNN | Market entity relationship graphs |
| StockAnalystAgent | LSTM | Price prediction, trend analysis |
| WhaleWatcherAgent | GNN | Wallet transaction networks |
| OpportunityScoringAgent | RL | Opportunity ranking optimization |

### Integration Pattern

Each agent will:
1. Call `router.auto_route()` or `router.route()` with task data
2. Use ML predictions to enhance GPT prompts
3. Include ML confidence in results

**Example Integration (MarketIntelligenceAgent):**
```python
def execute(self, task, context, scifi_context, spider_context):
    # Get ML analysis for market data
    from core.services.agent_model_router import get_agent_model_router

    router = get_agent_model_router()

    # If we have market relationship data, use GNN
    market_data = context.get('market_data')
    if market_data and 'entities' in market_data:
        graph_data = {
            'nodes': market_data['entities'],
            'edges': market_data.get('relationships', [])
        }
        ml_result = router.auto_route(graph_data)

        # Add ML insights to prompt
        ml_insights = f"""
ML Analysis (GNN):
- Task Type: {ml_result.auto_selection['task_type']}
- Models Used: {ml_result.models_used}
- Confidence: {ml_result.confidence:.2f}
- Key Findings: {ml_result.explanation}
"""
        full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
        full_prompt += ml_insights

    # Continue with GPT call...
```

---

## Part 3: File Changes Summary

### New Files
- None (all modifications to existing files)

### Files to Modify

| File | Changes |
|------|---------|
| `core/assistant/tool_definitions.py` | Add `_get_ml_analysis_tool_definition()` |
| `core/prompts/tool_descriptions.py` | Add ml_analysis description |
| `core/views_personal_assistant.py` | Add `handle_ml_analysis()` handler |
| `core/agents/analysis/market_intelligence_agent.py` | Add GNN integration |
| `core/agents/stocks/stock_analyst_agent.py` | Add LSTM integration |
| `core/agents/blockchain/whale_watcher_agent.py` | Add GNN integration |
| `core/agents/opportunity_scoring_agent.py` | Add RL integration |
| `docs/CAPABILITIES.md` | Document ML integration |
| `docs/AGENTS.md` | Update agent descriptions |

---

## Part 4: Testing Plan

### Unit Tests
```python
# test_ml_assistant_integration.py

def test_ml_analysis_tool_time_series():
    """Test ML tool with time series data."""

def test_ml_analysis_tool_graph():
    """Test ML tool with graph data."""

def test_market_intelligence_with_gnn():
    """Test MarketIntelligenceAgent uses GNN."""

def test_stock_analyst_with_lstm():
    """Test StockAnalystAgent uses LSTM."""

def test_whale_watcher_with_gnn():
    """Test WhaleWatcherAgent uses GNN."""

def test_opportunity_scoring_with_rl():
    """Test OpportunityScoringAgent uses RL."""
```

### Manual Testing
```bash
# Test via API
curl -X POST http://localhost:8000/api/assistant/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze this price data for trends", "data": {"prices": [100, 105, 102, 108]}}'
```

---

## Part 5: Expected Outcomes

### GPT Can Now:
1. Invoke ML models for data analysis
2. Get predictions with confidence scores
3. Choose appropriate model automatically
4. Explain why a model was selected

### Agents Now:
1. Use specialized ML models for their domain
2. Provide ML-backed insights alongside GPT reasoning
3. Have higher accuracy on domain-specific tasks
4. Report ML confidence in results

### User Experience:
1. "Analyze this data" → Auto-detects type, runs ML
2. Market analysis includes GNN relationship insights
3. Stock predictions include LSTM forecasts
4. Whale tracking includes network analysis
5. Opportunity scoring uses RL optimization

---

## Implementation Order

1. **ML Analysis Tool** (GPT integration)
   - Add tool definition
   - Add tool handler
   - Test with assistant

2. **MarketIntelligenceAgent** (GNN)
   - Add router import
   - Add ML analysis call
   - Enhance prompt with ML insights

3. **StockAnalystAgent** (LSTM)
   - Similar pattern to above

4. **WhaleWatcherAgent** (GNN)
   - Similar pattern to above

5. **OpportunityScoringAgent** (RL)
   - Similar pattern to above

6. **Documentation & Tests**
   - Update docs
   - Add integration tests

---

## Architecture After Integration

```
User Request
     ↓
GPT-5-mini (Reasoning)
     ↓
┌────────────────────────────────────┐
│ Tool: ml_analysis                  │
│ ↓                                  │
│ AgentModelRouter.auto_route()      │
│ ↓                                  │
│ TaskAnalyzer → ModelScorer →       │
│ ModelSelector → ML Prediction      │
└────────────────────────────────────┘
     ↓
GPT incorporates ML insights
     ↓
Response to User (with ML confidence)
```

---

## Risk Mitigation

1. **ML models fallback** - All models have statistical fallbacks
2. **GPT remains primary** - ML enhances, doesn't replace GPT
3. **Graceful degradation** - If ML fails, agents continue with GPT-only
4. **Transparent confidence** - Always show when ML was used

---

## Success Criteria

- [x] GPT can call ml_analysis tool
- [x] Auto-selection works from assistant
- [x] 4 agents use ML models (MarketIntelligence, StockAnalyst, WhaleWatcher, OpportunityScoring)
- [x] Tests pass (218 ML tests)
- [x] Documentation updated (CAPABILITIES.md, AGENTS.md)
