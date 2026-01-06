# Session 677 - Start Here

**Previous Session:** 676 (Agent-Model Routing Architecture Design)
**Date:** January 5, 2026
**Focus:** Implement Agent-Model Router Foundation
**Status:** 100% Reality Score | Architecture Design Complete

---

## Session 676 Summary: Agent-Model Routing Architecture

### Key Insight
Different agents have different ML needs - a ResearchAgent needs semantic embeddings while a StockAnalystAgent needs time-series LSTM. Currently ALL agents use the same LightGBM + rules hybrid.

### Architecture Document Created
**READ THIS FIRST:** `docs/handoffs/SESSION_676_AGENT_MODEL_ROUTING_ARCHITECTURE.md`

This comprehensive document (500+ lines) contains:
- Complete inventory of 9 existing models
- 7 new models to add (LSTM, Prophet, RL, GNN, VAE, DBSCAN, Bayesian)
- Agent-to-model mapping for all 72 agents
- 5-phase implementation plan (Sessions 677-681)
- Database schema for AgentModelConfig
- API endpoints to create
- Testing strategy
- Success metrics

### Models Currently Available

| Model | Location | Best For |
|-------|----------|----------|
| LightGBM | ml_scoring_engine.py | General scoring |
| XGBoost | ml_scoring_engine.py | Robust predictions |
| Random Forest | ml/core/ml_engine.py | Classification |
| Isolation Forest | agents/ml_algorithms.py | Anomaly detection |
| K-Means | agents/ml_algorithms.py | Clustering |
| MLP Neural Network | ml/core/ml_engine.py | Pattern recognition |
| DistilBERT | ml/core/ml_engine.py | Sentiment analysis |
| OpenAI Embeddings | memory_embedding_service.py | Semantic search |
| Cosine Similarity | ml_algorithms.py | Recommendations |

### Models to Add (Priority Order)

| Priority | Model | Best For | Target Agent |
|----------|-------|----------|--------------|
| P1 | LSTM | Time series | StockAnalystAgent |
| P1 | Prophet | Seasonal trends | TrendAnalysisAgent |
| P2 | Reinforcement Learning | Decision optimization | OpportunityPipelineAgent |
| P2 | Graph Neural Network | Relationships | WhaleWatcherAgent |
| P3 | VAE Autoencoder | Novel anomalies | ExploitDetectorAgent |

---

## Session 677 Priorities

### Priority 1: Create Agent-Model Router Foundation

**Files to Create:**
```
core/services/agent_model_router.py     # Main routing logic
core/services/model_registry.py         # Model wrapper registry
core/models_agent_models.py             # Database models
core/migrations/XXXX_agent_model_config.py
```

**Key Classes:**
```python
# AgentModelConfig - stores agent → model mapping
class AgentModelConfig(models.Model):
    agent_name = models.CharField(max_length=100, unique=True)
    primary_model = models.CharField(max_length=50)
    secondary_model = models.CharField(max_length=50, blank=True)
    model_weights = models.JSONField(default=dict)
    # ... see full schema in architecture doc

# ModelRegistry - wraps all available models
class ModelRegistry:
    AVAILABLE_MODELS = {
        'lightgbm': LightGBMWrapper,
        'xgboost': XGBoostWrapper,
        'embeddings': EmbeddingWrapper,
        # ...
    }

# AgentModelRouter - routes agents to optimal models
class AgentModelRouter:
    def route(self, agent_name: str, task_data: dict) -> ModelPrediction:
        config = AgentModelConfig.objects.get(agent_name=agent_name)
        # Get models, combine predictions
        pass
```

### Priority 2: Wrap Existing Models

Create `BaseModelWrapper` interface and wrap:
- LightGBM (from ml_scoring_engine.py)
- XGBoost (from ml_scoring_engine.py)
- Embeddings (from memory_embedding_service.py)
- Isolation Forest (from ml_algorithms.py)
- DistilBERT (from ml_engine.py)

### Priority 3: Default Agent Configurations

Populate AgentModelConfig for all 72 agents with sensible defaults:
- Most agents: lightgbm:0.6 + rules:0.4 (current behavior)
- ResearchAgent: embeddings:0.9 + lightgbm:0.1
- BlockchainAuditCoordinator: isolation_forest:0.7 + xgboost:0.3
- etc.

---

## Implementation Phases (Full Plan)

| Phase | Session | Focus | Deliverables |
|-------|---------|-------|--------------|
| 1 | 677 | Foundation | Router, Registry, Config models |
| 2 | 678 | Time-Series | LSTM, Prophet wrappers |
| 3 | 679 | Anomaly Detection | VAE Autoencoder |
| 4 | 680 | Reinforcement Learning | RL for task routing |
| 5 | 681 | Graph Neural Networks | GNN for blockchain |

---

## Quick Commands

```bash
# Start services
make start && make celery

# Check system health
curl http://localhost:8000/health/ping/

# View current ML scoring (will be replaced by router)
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.services.ml_scoring_engine import get_ml_scoring_engine
engine = get_ml_scoring_engine()
print(f'Current model: {engine.model_type}')"

# List all agents (to configure)
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.agent_router import AgentRouter
router = AgentRouter()
print(f'Routable agents: {len(router.agents)}')"
```

---

## System Stats (Session 676)

| Component | Count | Notes |
|-----------|-------|-------|
| Agents | 72 | **All need model config** |
| Existing ML Models | 9 | LightGBM, XGBoost, RF, etc. |
| Models to Add | 7 | LSTM, Prophet, RL, GNN, VAE, DBSCAN, Bayesian |
| Spiders | 77 | 72 working |
| PA Tools | 82 | All working |
| Celery Tasks | 127 | 4 workers running |

---

## Architecture Reference

See `docs/handoffs/SESSION_676_AGENT_MODEL_ROUTING_ARCHITECTURE.md` for:
- Complete agent-to-model mapping table
- Database schema details
- API endpoint specifications
- Testing strategy
- Success metrics
- Risk mitigation
