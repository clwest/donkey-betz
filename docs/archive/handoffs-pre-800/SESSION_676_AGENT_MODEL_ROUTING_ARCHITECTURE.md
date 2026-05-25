# Session 676: Agent-Model Routing Architecture

**Date:** January 5, 2026
**Status:** DESIGN COMPLETE - Ready for Implementation
**Priority:** High - Foundational ML Architecture Enhancement
**Estimated Sessions:** 3-5 sessions for full implementation

---

## Executive Summary

This document outlines the architecture for **Agent-Specific Model Routing** - a system where different agents use different ML models optimized for their specific tasks, rather than all agents using the same hybrid scoring approach.

### The Problem
Currently, ALL 72 agents use the same ML pipeline:
- 60% LightGBM + 40% Rule-based scoring
- One-size-fits-all approach
- Agents with specialized needs (time-series, anomaly detection, semantic search) use generic models

### The Solution
Route each agent to the optimal model(s) for their specific task type:
- Time-series agents → LSTM + XGBoost ensemble
- Semantic agents → Embeddings + Transformer
- Anomaly agents → Isolation Forest + Autoencoder
- Decision agents → Reinforcement Learning + LightGBM

---

## Current System Inventory

### Models Already Available

| Model | File Location | Current Use |
|-------|---------------|-------------|
| LightGBM | `core/services/ml_scoring_engine.py` | Opportunity scoring (default) |
| XGBoost | `core/services/ml_scoring_engine.py` | Alternative scoring |
| Random Forest | `ml/core/ml_engine.py:147` | User behavior, sports predictions |
| Isolation Forest | `agents/ml_algorithms.py:536` | Fraud detection |
| K-Means | `agents/ml_algorithms.py:313` | Customer segmentation |
| MLP Neural Network | `ml/core/ml_engine.py:129` | Pattern recognition |
| DistilBERT | `ml/core/ml_engine.py:197` | Sentiment analysis |
| OpenAI Embeddings | `core/services/memory_embedding_service.py` | Semantic similarity |
| Cosine Similarity | `agents/ml_algorithms.py:55` | Collaborative filtering |
| Gradient Boosting | `ml/core/ml_engine.py:154` | Cross-domain analysis |

### Models to Add

| Model | Purpose | Priority | Complexity |
|-------|---------|----------|------------|
| LSTM/GRU | Time series prediction | P1 | Medium |
| Prophet | Seasonal forecasting | P1 | Low |
| Reinforcement Learning | Decision optimization | P2 | High |
| Graph Neural Network | Relationship analysis | P2 | High |
| VAE/Autoencoder | Anomaly detection | P3 | Medium |
| DBSCAN | Density clustering | P3 | Low |
| Bayesian Optimization | Hyperparameter tuning | P3 | Medium |

---

## Agent-Model Mapping

### Category 1: Time-Series Agents

| Agent | Primary Model | Secondary Model | Reasoning |
|-------|---------------|-----------------|-----------|
| StockAnalystAgent | LSTM | XGBoost | Price movements are temporal sequences |
| MarketMovementMonitorAgent | LSTM | Random Forest | Real-time pattern detection |
| WhaleWatcherAgent | LSTM + GNN | Isolation Forest | Transaction sequences + graph structure |
| TrendAnalysisAgent | Prophet | DistilBERT | Seasonal trends + sentiment |
| SignalScannerAgent | LSTM | LightGBM | Technical indicator sequences |

### Category 2: Semantic/Text Agents

| Agent | Primary Model | Secondary Model | Reasoning |
|-------|---------------|-----------------|-----------|
| ResearchAgent | Embeddings (90%) | LightGBM (10%) | Semantic search is core function |
| ContentWriterAgent | Small Transformer | DistilBERT | Text generation quality |
| SocialMediaAgent | DistilBERT | Prophet | Sentiment + trend timing |
| SEOOptimizerAgent | Embeddings | K-Means | Keyword clustering |
| ContentStrategyAgent | Embeddings | LightGBM | Content-opportunity matching |

### Category 3: Anomaly/Security Agents

| Agent | Primary Model | Secondary Model | Reasoning |
|-------|---------------|-----------------|-----------|
| BlockchainAuditCoordinator | Graph NN | Isolation Forest | Transactions are graphs |
| ExploitDetectorAgent | VAE Autoencoder | XGBoost | Novel anomaly detection |
| SmartContractAuditorAgent | Isolation Forest | Rule-based | Pattern deviation |
| TransactionMonitorAgent | LSTM | Isolation Forest | Temporal + anomaly |
| ContentAuditAgent | Isolation Forest | DistilBERT | Content anomalies |

### Category 4: Decision/Optimization Agents

| Agent | Primary Model | Secondary Model | Reasoning |
|-------|---------------|-----------------|-----------|
| OpportunityScoringAgent | LightGBM | Rule-based | Current (working well) |
| OpportunityPipelineAgent | Reinforcement Learning | LightGBM | Learns optimal routing |
| PredictionMarketAnalyst | XGBoost | Bayesian Opt | Probability calibration |
| ArbitrageDetector | Random Forest | Real-time rules | Speed critical |
| ThinkingAgent | Ensemble (all) | Meta-learning | Uses best model per task |

### Category 5: Segmentation/Clustering Agents

| Agent | Primary Model | Secondary Model | Reasoning |
|-------|---------------|-----------------|-----------|
| MarketIntelligenceAgent | K-Means | DBSCAN | Market segments |
| CustomerResearchAgent | K-Means | Collab. Filtering | User segmentation |
| BrandStrategyAgent | DBSCAN | Embeddings | Brand positioning |
| CompetitorAnalysisAgent | K-Means | Cosine Similarity | Competitive clustering |

---

## Implementation Plan

### Phase 1: Foundation (Session 677)

**Goal:** Create the Agent-Model Router infrastructure

**Files to Create:**
```
core/services/agent_model_router.py     # Main routing logic
core/services/model_registry.py         # Available model registry
core/models_agent_models.py             # Database models for config
```

**Tasks:**
1. Create `AgentModelConfig` database model:
   ```python
   class AgentModelConfig(models.Model):
       agent_name = models.CharField(max_length=100, unique=True)
       primary_model = models.CharField(max_length=50)  # e.g., 'lstm', 'lightgbm'
       secondary_model = models.CharField(max_length=50, blank=True)
       model_weights = models.JSONField(default=dict)  # e.g., {'lstm': 0.7, 'xgboost': 0.3}
       custom_params = models.JSONField(default=dict)
       is_active = models.BooleanField(default=True)
       performance_score = models.FloatField(default=0.0)
       last_evaluated = models.DateTimeField(null=True)
   ```

2. Create `ModelRegistry` class:
   ```python
   class ModelRegistry:
       AVAILABLE_MODELS = {
           'lightgbm': LightGBMWrapper,
           'xgboost': XGBoostWrapper,
           'lstm': LSTMWrapper,
           'isolation_forest': IsolationForestWrapper,
           'embeddings': EmbeddingWrapper,
           'distilbert': DistilBERTWrapper,
           # ... etc
       }

       def get_model(self, model_name: str) -> BaseModelWrapper:
           """Get model instance by name."""
           pass
   ```

3. Create `AgentModelRouter` class:
   ```python
   class AgentModelRouter:
       def route(self, agent_name: str, task_data: dict) -> ModelPrediction:
           """Route agent to optimal model and return prediction."""
           config = AgentModelConfig.objects.get(agent_name=agent_name)
           primary = self.registry.get_model(config.primary_model)
           secondary = self.registry.get_model(config.secondary_model)

           # Weighted ensemble
           primary_pred = primary.predict(task_data)
           secondary_pred = secondary.predict(task_data)

           return self._combine_predictions(
               primary_pred, secondary_pred, config.model_weights
           )
   ```

4. Migration to add default configs for all 72 agents

**Deliverables:**
- [ ] AgentModelConfig model with migration
- [ ] ModelRegistry with all existing models wrapped
- [ ] AgentModelRouter with basic routing
- [ ] Default configurations for all agents
- [ ] Unit tests for routing logic

---

### Phase 2: Time-Series Models (Session 678)

**Goal:** Add LSTM and Prophet for time-series agents

**Files to Create/Modify:**
```
core/services/models/lstm_wrapper.py    # LSTM implementation
core/services/models/prophet_wrapper.py # Prophet implementation
```

**Tasks:**
1. Implement `LSTMWrapper`:
   ```python
   class LSTMWrapper(BaseModelWrapper):
       def __init__(self, sequence_length=30, features=10):
           self.model = self._build_lstm_model()

       def _build_lstm_model(self):
           # PyTorch or TensorFlow LSTM
           pass

       def predict(self, sequence_data: np.ndarray) -> float:
           # Return prediction
           pass

       def train(self, training_data: List[dict]) -> dict:
           # Training logic
           pass
   ```

2. Implement `ProphetWrapper`:
   ```python
   class ProphetWrapper(BaseModelWrapper):
       def __init__(self):
           from prophet import Prophet
           self.model = Prophet(
               yearly_seasonality=True,
               weekly_seasonality=True,
               daily_seasonality=False
           )

       def predict(self, dates: List[datetime], periods: int = 30) -> dict:
           # Forecast future values
           pass
   ```

3. Update agent configs:
   - StockAnalystAgent → lstm (70%) + xgboost (30%)
   - TrendAnalysisAgent → prophet (60%) + distilbert (40%)
   - SignalScannerAgent → lstm (80%) + lightgbm (20%)

4. Create training data pipeline for stock/trend data

**Deliverables:**
- [ ] LSTMWrapper with training and inference
- [ ] ProphetWrapper with seasonal forecasting
- [ ] Integration with StockAnalystAgent
- [ ] Integration with TrendAnalysisAgent
- [ ] Performance benchmarks vs current approach

---

### Phase 3: Enhanced Anomaly Detection (Session 679)

**Goal:** Add VAE Autoencoder and improve Isolation Forest usage

**Files to Create/Modify:**
```
core/services/models/autoencoder_wrapper.py  # VAE implementation
core/services/models/enhanced_isolation.py   # Improved Isolation Forest
```

**Tasks:**
1. Implement `VAEAutoencoderWrapper`:
   ```python
   class VAEAutoencoderWrapper(BaseModelWrapper):
       def __init__(self, latent_dim=32):
           self.encoder = self._build_encoder()
           self.decoder = self._build_decoder()

       def detect_anomaly(self, data: np.ndarray) -> dict:
           reconstructed = self.model(data)
           reconstruction_error = np.mean((data - reconstructed) ** 2)
           return {
               'is_anomaly': reconstruction_error > self.threshold,
               'anomaly_score': reconstruction_error,
               'latent_representation': self.encoder(data)
           }
   ```

2. Update agent configs:
   - ExploitDetectorAgent → autoencoder (60%) + xgboost (40%)
   - BlockchainAuditCoordinator → isolation_forest (50%) + autoencoder (50%)
   - ContentAuditAgent → isolation_forest (70%) + distilbert (30%)

3. Training pipeline for anomaly data (blockchain transactions, content flags)

**Deliverables:**
- [ ] VAEAutoencoderWrapper
- [ ] Enhanced Isolation Forest with SHAP explanations
- [ ] Integration with blockchain agents
- [ ] Anomaly detection benchmarks

---

### Phase 4: Reinforcement Learning (Session 680)

**Goal:** Add RL for decision optimization agents

**Files to Create/Modify:**
```
core/services/models/rl_wrapper.py       # RL implementation
core/services/reward_calculator.py       # Reward signal from outcomes
```

**Tasks:**
1. Implement `RLAgentWrapper`:
   ```python
   class RLAgentWrapper(BaseModelWrapper):
       def __init__(self, state_dim, action_dim):
           self.policy_network = self._build_policy()
           self.value_network = self._build_value()
           self.optimizer = Adam(lr=0.001)

       def select_action(self, state: np.ndarray) -> int:
           # Policy-based action selection
           pass

       def update(self, trajectory: List[Transition]) -> dict:
           # PPO or A2C update
           pass
   ```

2. Create `RewardCalculator`:
   ```python
   class RewardCalculator:
       def calculate_reward(self, outcome: OpportunityOutcome) -> float:
           if outcome.outcome == 'won':
               return outcome.revenue_generated / 100  # Normalized
           elif outcome.outcome == 'partial':
               return 0.3
           else:
               return -0.1  # Small penalty for failed attempts
   ```

3. Update agent configs:
   - OpportunityPipelineAgent → rl (70%) + lightgbm (30%)
   - ThinkingAgent → rl (for model selection)

**Deliverables:**
- [ ] RLAgentWrapper with PPO/A2C
- [ ] RewardCalculator from OpportunityOutcome
- [ ] Integration with OpportunityPipelineAgent
- [ ] Learning curve visualizations

---

### Phase 5: Graph Neural Networks (Session 681)

**Goal:** Add GNN for relationship-based agents

**Files to Create/Modify:**
```
core/services/models/gnn_wrapper.py      # GNN implementation
core/services/graph_builder.py           # Build graphs from data
```

**Tasks:**
1. Implement `GNNWrapper`:
   ```python
   class GNNWrapper(BaseModelWrapper):
       def __init__(self, node_features, edge_features):
           import torch_geometric as pyg
           self.model = pyg.nn.GCN(node_features, hidden_channels=64, out_channels=1)

       def predict_node(self, graph: Data, node_idx: int) -> float:
           # Node-level prediction
           pass

       def detect_community(self, graph: Data) -> List[List[int]]:
           # Community detection
           pass
   ```

2. Create `GraphBuilder`:
   ```python
   class GraphBuilder:
       def build_transaction_graph(self, transactions: List[dict]) -> Data:
           # Nodes = addresses, Edges = transactions
           pass

       def build_agent_collaboration_graph(self, executions: List[dict]) -> Data:
           # Nodes = agents, Edges = collaborations
           pass
   ```

3. Update agent configs:
   - WhaleWatcherAgent → gnn (60%) + lstm (40%)
   - BlockchainAuditCoordinator → gnn (50%) + isolation_forest (50%)

**Deliverables:**
- [ ] GNNWrapper with PyTorch Geometric
- [ ] GraphBuilder for transaction and collaboration graphs
- [ ] Integration with blockchain agents
- [ ] Graph visualization tools

---

## Database Schema

### New Models Required

```python
# core/models_agent_models.py

class AgentModelConfig(models.Model):
    """Configuration for which models each agent uses."""
    agent_name = models.CharField(max_length=100, unique=True, db_index=True)
    primary_model = models.CharField(max_length=50)
    secondary_model = models.CharField(max_length=50, blank=True)
    model_weights = models.JSONField(default=dict)
    custom_params = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    performance_score = models.FloatField(default=0.0)
    last_evaluated = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent_model_config'
        indexes = [
            models.Index(fields=['agent_name', 'is_active']),
        ]


class ModelPerformanceLog(models.Model):
    """Track model performance over time."""
    config = models.ForeignKey(AgentModelConfig, on_delete=models.CASCADE)
    evaluation_date = models.DateTimeField(auto_now_add=True)
    metric_name = models.CharField(max_length=50)  # 'accuracy', 'f1', 'rmse'
    metric_value = models.FloatField()
    sample_count = models.IntegerField()
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'model_performance_log'
        indexes = [
            models.Index(fields=['config', 'evaluation_date']),
        ]


class ModelTrainingRun(models.Model):
    """Track model training runs."""
    model_type = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=20)  # 'running', 'completed', 'failed'
    hyperparameters = models.JSONField(default=dict)
    metrics = models.JSONField(default=dict)
    model_path = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'model_training_run'
```

---

## API Endpoints

### New Endpoints to Create

```python
# core/urls.py additions

# Agent Model Configuration
path('api/agent-models/', views.AgentModelConfigListView.as_view()),
path('api/agent-models/<str:agent_name>/', views.AgentModelConfigDetailView.as_view()),
path('api/agent-models/<str:agent_name>/performance/', views.AgentModelPerformanceView.as_view()),

# Model Management
path('api/models/', views.ModelRegistryView.as_view()),
path('api/models/<str:model_name>/train/', views.ModelTrainingView.as_view()),
path('api/models/<str:model_name>/evaluate/', views.ModelEvaluationView.as_view()),

# Routing
path('api/model-router/predict/', views.ModelRouterPredictView.as_view()),
path('api/model-router/explain/', views.ModelRouterExplainView.as_view()),
```

---

## Testing Strategy

### Unit Tests Required

```python
# tests/services/test_agent_model_router.py

class TestAgentModelRouter:
    def test_route_to_correct_model(self):
        """Verify routing selects correct model for agent."""
        pass

    def test_weighted_ensemble(self):
        """Verify weighted combination of predictions."""
        pass

    def test_fallback_on_model_error(self):
        """Verify graceful fallback when model fails."""
        pass

    def test_performance_logging(self):
        """Verify performance metrics are logged."""
        pass


class TestLSTMWrapper:
    def test_sequence_prediction(self):
        """Test LSTM predicts from sequence data."""
        pass

    def test_training_convergence(self):
        """Test LSTM training converges."""
        pass


class TestRLWrapper:
    def test_action_selection(self):
        """Test RL agent selects actions."""
        pass

    def test_reward_integration(self):
        """Test reward signal updates policy."""
        pass
```

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| ResearchAgent success rate | ~60% | 85%+ | Embedding similarity > keyword |
| Stock prediction accuracy | N/A | 55%+ | LSTM vs baseline |
| Anomaly detection precision | ~70% | 90%+ | Autoencoder vs Isolation Forest alone |
| Task routing efficiency | Manual | Automated | RL learns optimal routing |
| Model inference latency | N/A | <100ms | P95 latency |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Model training requires significant compute | Use Apple M3 MLX for local training |
| LSTM/GNN complexity | Start with pre-trained weights, fine-tune |
| Breaking existing functionality | Feature flag for new routing, gradual rollout |
| Data requirements for RL | Start with synthetic rewards, bootstrap from outcomes |

---

## Dependencies to Install

```bash
# Phase 2: Time Series
pip install prophet torch

# Phase 3: Anomaly Detection
pip install torch  # VAE requires PyTorch

# Phase 4: Reinforcement Learning
pip install stable-baselines3 gymnasium

# Phase 5: Graph Neural Networks
pip install torch-geometric torch-scatter torch-sparse
```

---

## Quick Reference: Agent → Model Mapping

```
# Time-Series Agents
StockAnalystAgent          → lstm:0.7 + xgboost:0.3
MarketMovementMonitorAgent → lstm:0.6 + random_forest:0.4
WhaleWatcherAgent          → lstm:0.4 + gnn:0.4 + isolation_forest:0.2
TrendAnalysisAgent         → prophet:0.6 + distilbert:0.4
SignalScannerAgent         → lstm:0.8 + lightgbm:0.2

# Semantic Agents
ResearchAgent              → embeddings:0.9 + lightgbm:0.1
ContentWriterAgent         → transformer:0.7 + distilbert:0.3
SocialMediaAgent           → distilbert:0.6 + prophet:0.4
SEOOptimizerAgent          → embeddings:0.7 + kmeans:0.3

# Anomaly Agents
BlockchainAuditCoordinator → gnn:0.4 + isolation_forest:0.3 + autoencoder:0.3
ExploitDetectorAgent       → autoencoder:0.6 + xgboost:0.4
ContentAuditAgent          → isolation_forest:0.7 + distilbert:0.3

# Decision Agents
OpportunityScoringAgent    → lightgbm:0.6 + rules:0.4 (current - working)
OpportunityPipelineAgent   → rl:0.7 + lightgbm:0.3
ThinkingAgent              → meta_learning (selects best model per task)

# Clustering Agents
MarketIntelligenceAgent    → kmeans:0.6 + dbscan:0.4
CustomerResearchAgent      → kmeans:0.5 + collaborative:0.5
```

---

## Next Session Checklist

### Session 677 Should:
1. [ ] Read this document first
2. [ ] Create `core/services/agent_model_router.py`
3. [ ] Create `core/services/model_registry.py`
4. [ ] Create `core/models_agent_models.py`
5. [ ] Create migration for AgentModelConfig
6. [ ] Wrap existing models (LightGBM, XGBoost, etc.)
7. [ ] Add default configs for all 72 agents
8. [ ] Write unit tests
9. [ ] Update this document with progress

---

**Document Version:** 1.0
**Created:** Session 676
**Last Updated:** January 5, 2026
