"""
Agent-Model Router - Routes Agents to Optimal ML Models
========================================================

Session 677: Phase 1 of Agent-Model Routing Architecture
Session 682: Phase 6 - Added auto_route() for automatic model selection

This module provides the central routing logic that:
1. Looks up the AgentModelConfig for a given agent
2. Gets the appropriate model(s) from the ModelRegistry
3. Makes predictions using weighted ensemble
4. Records performance metrics
5. Auto-selects models based on data characteristics (Phase 6)

Usage:
    from core.services.agent_model_router import get_agent_model_router

    router = get_agent_model_router()
    result = router.route('ResearchAgent', task_data)
    # result.score, result.confidence, result.explanation

    # Auto-select models based on data (Session 682)
    result = router.auto_route(data)
    # result.score, result.auto_selection (with task_type, recommended_models)

    # Or use async version
    result = await router.route_async('StockAnalystAgent', market_data)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from core.services.model_registry import (
    BaseModelWrapper,
    ModelPrediction,
    get_model_registry,
)
from ml.auto_selection import (
    get_model_selector,
    AutoSelectionResult,
    TaskType,
)

logger = logging.getLogger(__name__)


@dataclass
class EnsemblePrediction:
    """Result from ensemble prediction across multiple models."""
    success: bool
    score: float = 0.0
    confidence: float = 0.0
    model_scores: Dict[str, float] = field(default_factory=dict)
    model_weights: Dict[str, float] = field(default_factory=dict)
    explanation: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    agent_name: str = ""
    models_used: List[str] = field(default_factory=list)
    fallback_used: bool = False
    error: Optional[str] = None
    # Session 682: Auto-selection info when using auto_route()
    auto_selection: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'success': self.success,
            'score': self.score,
            'confidence': self.confidence,
            'model_scores': self.model_scores,
            'model_weights': self.model_weights,
            'explanation': self.explanation,
            'latency_ms': self.latency_ms,
            'agent_name': self.agent_name,
            'models_used': self.models_used,
            'fallback_used': self.fallback_used,
            'error': self.error,
        }
        if self.auto_selection:
            result['auto_selection'] = self.auto_selection
        return result


class AgentModelRouter:
    """
    Routes agents to their optimal ML models based on configuration.

    The router:
    1. Looks up AgentModelConfig for the requested agent
    2. Gets model instances from ModelRegistry
    3. Makes predictions using weighted ensemble
    4. Falls back to default model on errors
    5. Records performance metrics
    """

    # Default configuration for agents without custom config
    DEFAULT_CONFIG = {
        'primary_model': 'lightgbm',
        'secondary_model': 'rules',
        'model_weights': {'lightgbm': 0.6, 'rules': 0.4},
    }

    def __init__(self):
        self._registry = get_model_registry()
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_time: Dict[str, float] = {}

    def _get_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for an agent, with caching.

        Falls back to DEFAULT_CONFIG if no database config exists.
        """
        now = time.time()

        # Check cache
        if agent_name in self._config_cache:
            if now - self._cache_time.get(agent_name, 0) < self._cache_ttl:
                return self._config_cache[agent_name]

        # Try to load from database
        try:
            from core.models_agent_models import AgentModelConfig

            config = AgentModelConfig.objects.filter(
                agent_name=agent_name,
                is_active=True
            ).first()

            if config:
                result = {
                    'primary_model': config.primary_model,
                    'secondary_model': config.secondary_model,
                    'tertiary_model': config.tertiary_model,
                    'model_weights': config.model_weights or {},
                    'custom_params': config.custom_params or {},
                    'use_fallback': config.use_fallback,
                    'fallback_model': config.fallback_model,
                    'config_id': str(config.id),
                }
                self._config_cache[agent_name] = result
                self._cache_time[agent_name] = now
                return result

        except Exception as e:
            logger.debug(f"Could not load config for {agent_name}: {e}")

        # Return default config
        return self.DEFAULT_CONFIG.copy()

    def _get_models_for_agent(self, agent_name: str) -> List[tuple]:
        """
        Get list of (model, weight) tuples for an agent.

        Returns models in order of priority with their weights.
        """
        config = self._get_config(agent_name)
        weights = config.get('model_weights', {})
        models = []

        # Primary model
        primary = config.get('primary_model')
        if primary:
            model = self._registry.get_model(primary)
            if model and model.is_available():
                weight = weights.get(primary, 0.6)
                models.append((model, weight, primary))
            else:
                logger.warning(f"{agent_name}: Primary model {primary} not available")

        # Secondary model
        secondary = config.get('secondary_model')
        if secondary:
            model = self._registry.get_model(secondary)
            if model and model.is_available():
                weight = weights.get(secondary, 0.3)
                models.append((model, weight, secondary))

        # Tertiary model
        tertiary = config.get('tertiary_model')
        if tertiary:
            model = self._registry.get_model(tertiary)
            if model and model.is_available():
                weight = weights.get(tertiary, 0.1)
                models.append((model, weight, tertiary))

        # Normalize weights
        total_weight = sum(w for _, w, _ in models)
        if total_weight > 0 and total_weight != 1.0:
            models = [(m, w / total_weight, n) for m, w, n in models]

        return models

    def route(self, agent_name: str, data: Any, **kwargs) -> EnsemblePrediction:
        """
        Route an agent to its configured models and return ensemble prediction.

        Args:
            agent_name: Name of the agent (e.g., 'ResearchAgent')
            data: Input data for prediction
            **kwargs: Additional parameters passed to models

        Returns:
            EnsemblePrediction with combined scores and explanations
        """
        start_time = time.time()
        config = self._get_config(agent_name)
        models = self._get_models_for_agent(agent_name)

        if not models:
            # No models available, try fallback
            if config.get('use_fallback', True):
                fallback_name = config.get('fallback_model', 'lightgbm')
                fallback = self._registry.get_model(fallback_name)
                if fallback and fallback.is_available():
                    logger.info(f"{agent_name}: Using fallback model {fallback_name}")
                    result = fallback.predict(data, **kwargs)
                    return EnsemblePrediction(
                        success=result.success,
                        score=result.score,
                        confidence=result.confidence,
                        model_scores={fallback_name: result.score},
                        model_weights={fallback_name: 1.0},
                        explanation=result.explanation,
                        latency_ms=(time.time() - start_time) * 1000,
                        agent_name=agent_name,
                        models_used=[fallback_name],
                        fallback_used=True,
                        error=result.error,
                    )

            return EnsemblePrediction(
                success=False,
                agent_name=agent_name,
                error="No models available for this agent",
                latency_ms=(time.time() - start_time) * 1000,
            )

        # Make predictions with all models
        model_predictions: Dict[str, ModelPrediction] = {}
        model_weights: Dict[str, float] = {}

        for model, weight, name in models:
            try:
                pred = model.predict(data, **kwargs)
                model_predictions[name] = pred
                model_weights[name] = weight
            except Exception as e:
                logger.error(f"{agent_name}: Error with {name}: {e}")

        if not model_predictions:
            return EnsemblePrediction(
                success=False,
                agent_name=agent_name,
                error="All model predictions failed",
                latency_ms=(time.time() - start_time) * 1000,
            )

        # Combine predictions using weighted average
        combined_score = 0.0
        combined_confidence = 0.0
        total_weight = 0.0
        model_scores = {}
        all_explanations = {}

        for name, pred in model_predictions.items():
            if pred.success:
                weight = model_weights[name]
                combined_score += pred.score * weight
                combined_confidence += pred.confidence * weight
                total_weight += weight
                model_scores[name] = pred.score
                if pred.explanation:
                    all_explanations[name] = pred.explanation

        if total_weight > 0:
            combined_score /= total_weight
            combined_confidence /= total_weight

        # Record performance
        self._record_prediction(agent_name, True, (time.time() - start_time) * 1000)

        return EnsemblePrediction(
            success=True,
            score=combined_score,
            confidence=combined_confidence,
            model_scores=model_scores,
            model_weights=model_weights,
            explanation=all_explanations,
            latency_ms=(time.time() - start_time) * 1000,
            agent_name=agent_name,
            models_used=list(model_predictions.keys()),
            fallback_used=False,
        )

    async def route_async(self, agent_name: str, data: Any, **kwargs) -> EnsemblePrediction:
        """
        Async version of route() for use in async contexts.

        Runs synchronous model predictions in a thread pool.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.route(agent_name, data, **kwargs)
        )

    # =========================================================================
    # AUTO-SELECTION METHODS (Session 682 - Phase 6)
    # =========================================================================

    def auto_route(
        self,
        data: Any,
        task_hint: Optional[TaskType] = None,
        max_models: int = 2,
        min_score: float = 0.3,
        agent_name: Optional[str] = None,
        **kwargs
    ) -> EnsemblePrediction:
        """
        Automatically select and route to optimal models based on data characteristics.

        This method analyzes the input data to detect task type and characteristics,
        then selects the best models without requiring pre-configured agent settings.

        Args:
            data: Input data for prediction
            task_hint: Optional hint about task type (TaskType enum)
            max_models: Maximum models to use (default 2)
            min_score: Minimum score threshold for model selection
            agent_name: Optional agent name for tracking
            **kwargs: Additional parameters passed to models

        Returns:
            EnsemblePrediction with scores and auto_selection info

        Example:
            router = get_agent_model_router()

            # Auto-detect task type
            result = router.auto_route(price_data)
            # result.auto_selection['task_type'] == 'time_series'
            # result.models_used == ['lstm', 'prophet']

            # With task hint
            result = router.auto_route(wallet_graph, task_hint=TaskType.GRAPH)
        """
        start_time = time.time()

        # Get the model selector
        selector = get_model_selector(self._registry)

        # Perform auto-selection
        selection = selector.select_models(
            data=data,
            task_hint=task_hint,
            max_models=max_models,
            min_score=min_score,
            agent_name=agent_name,
        )

        if not selection.success:
            return EnsemblePrediction(
                success=False,
                agent_name=agent_name or "auto",
                error=selection.error or "Auto-selection failed",
                latency_ms=(time.time() - start_time) * 1000,
                auto_selection=selection.to_dict(),
            )

        # Get models based on selection
        models = []
        for model_name in selection.recommended_models:
            model = self._registry.get_model(model_name)
            if model and model.is_available():
                weight = selection.model_weights.get(model_name, 0.5)
                models.append((model, weight, model_name))

        if not models:
            return EnsemblePrediction(
                success=False,
                agent_name=agent_name or "auto",
                error="No selected models available",
                latency_ms=(time.time() - start_time) * 1000,
                auto_selection=selection.to_dict(),
            )

        # Make predictions with selected models
        model_predictions: Dict[str, ModelPrediction] = {}
        model_weights: Dict[str, float] = {}

        for model, weight, name in models:
            try:
                pred = model.predict(data, **kwargs)
                model_predictions[name] = pred
                model_weights[name] = weight
            except Exception as e:
                logger.warning(f"Auto-route: Error with {name}: {e}")

        if not model_predictions:
            return EnsemblePrediction(
                success=False,
                agent_name=agent_name or "auto",
                error="All auto-selected model predictions failed",
                latency_ms=(time.time() - start_time) * 1000,
                auto_selection=selection.to_dict(),
            )

        # Combine predictions
        combined_score = 0.0
        combined_confidence = 0.0
        total_weight = 0.0
        model_scores = {}
        all_explanations = {}

        for name, pred in model_predictions.items():
            if pred.success:
                weight = model_weights[name]
                combined_score += pred.score * weight
                combined_confidence += pred.confidence * weight
                total_weight += weight
                model_scores[name] = pred.score
                if pred.explanation:
                    all_explanations[name] = pred.explanation

        if total_weight > 0:
            combined_score /= total_weight
            combined_confidence /= total_weight

        # Build auto-selection summary for result
        auto_selection_info = {
            'task_type': selection.task_analysis.task_type.value if selection.task_analysis else 'unknown',
            'characteristics': [c.value for c in selection.task_analysis.characteristics] if selection.task_analysis else [],
            'recommended_models': selection.recommended_models,
            'selection_reason': selection.selection_reason,
            'selection_confidence': selection.confidence,
            'selection_latency_ms': selection.latency_ms,
        }

        return EnsemblePrediction(
            success=True,
            score=combined_score,
            confidence=combined_confidence,
            model_scores=model_scores,
            model_weights=model_weights,
            explanation=all_explanations,
            latency_ms=(time.time() - start_time) * 1000,
            agent_name=agent_name or "auto",
            models_used=list(model_predictions.keys()),
            fallback_used=selection.fallback_used,
            auto_selection=auto_selection_info,
        )

    async def auto_route_async(
        self,
        data: Any,
        task_hint: Optional[TaskType] = None,
        **kwargs
    ) -> EnsemblePrediction:
        """Async version of auto_route()."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.auto_route(data, task_hint=task_hint, **kwargs)
        )

    def compare_auto_vs_config(
        self,
        agent_name: str,
        data: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compare auto-selected models vs configured models for an agent.

        Useful for evaluating if auto-selection would pick better models
        than the current configuration.

        Args:
            agent_name: Agent to compare
            data: Input data
            **kwargs: Additional parameters

        Returns:
            Dict with both results and comparison
        """
        # Get configured result
        config_result = self.route(agent_name, data, **kwargs)

        # Get auto-selected result
        auto_result = self.auto_route(data, agent_name=agent_name, **kwargs)

        # Build comparison
        config_models = config_result.models_used
        auto_models = auto_result.models_used

        return {
            'agent_name': agent_name,
            'configured': {
                'models': config_models,
                'score': config_result.score,
                'confidence': config_result.confidence,
                'latency_ms': config_result.latency_ms,
            },
            'auto_selected': {
                'models': auto_models,
                'score': auto_result.score,
                'confidence': auto_result.confidence,
                'latency_ms': auto_result.latency_ms,
                'task_type': auto_result.auto_selection.get('task_type') if auto_result.auto_selection else None,
                'selection_reason': auto_result.auto_selection.get('selection_reason') if auto_result.auto_selection else None,
            },
            'models_match': set(config_models) == set(auto_models),
            'score_difference': auto_result.score - config_result.score,
            'recommendation': 'use_auto' if auto_result.score > config_result.score else 'keep_config',
        }

    def get_model_selector(self):
        """Get the ModelSelector instance for advanced usage."""
        return get_model_selector(self._registry)

    def _record_prediction(self, agent_name: str, success: bool, latency_ms: float):
        """Record prediction metrics in database."""
        try:
            from django.db.models import F
            from core.models_agent_models import AgentModelConfig

            AgentModelConfig.objects.filter(
                agent_name=agent_name,
                is_active=True
            ).update(
                total_predictions=F('total_predictions') + 1,
                successful_predictions=F('successful_predictions') + (1 if success else 0),
            )
        except Exception as e:
            logger.debug(f"Could not record prediction: {e}")

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get the current configuration for an agent."""
        return self._get_config(agent_name)

    def set_agent_config(
        self,
        agent_name: str,
        primary_model: str,
        secondary_model: str = '',
        model_weights: Dict[str, float] = None,
        **kwargs
    ) -> bool:
        """
        Set or update configuration for an agent.

        Args:
            agent_name: Name of the agent
            primary_model: Primary model to use
            secondary_model: Secondary model (optional)
            model_weights: Weight distribution for ensemble
            **kwargs: Additional config parameters

        Returns:
            True if config was saved successfully
        """
        try:
            from core.models_agent_models import AgentModelConfig

            defaults = {
                'primary_model': primary_model,
                'secondary_model': secondary_model,
                'model_weights': model_weights or {primary_model: 0.6, secondary_model: 0.4},
                'is_active': True,
            }
            defaults.update(kwargs)

            config, created = AgentModelConfig.objects.update_or_create(
                agent_name=agent_name,
                defaults=defaults
            )

            # Invalidate cache
            if agent_name in self._config_cache:
                del self._config_cache[agent_name]

            logger.info(f"{'Created' if created else 'Updated'} config for {agent_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to set config for {agent_name}: {e}")
            return False

    def list_agent_configs(self) -> List[Dict[str, Any]]:
        """List all agent configurations."""
        try:
            from core.models_agent_models import AgentModelConfig

            configs = AgentModelConfig.objects.filter(is_active=True)
            return [
                {
                    'agent_name': c.agent_name,
                    'category': c.category,
                    'primary_model': c.primary_model,
                    'secondary_model': c.secondary_model,
                    'model_weights': c.model_weights,
                    'performance_score': c.performance_score,
                    'total_predictions': c.total_predictions,
                }
                for c in configs
            ]
        except Exception as e:
            logger.error(f"Failed to list configs: {e}")
            return []

    def get_available_models(self) -> List[str]:
        """List all available models that can be used."""
        return self._registry.list_available_models()

    def invalidate_cache(self, agent_name: str = None):
        """Invalidate configuration cache."""
        if agent_name:
            self._config_cache.pop(agent_name, None)
            self._cache_time.pop(agent_name, None)
        else:
            self._config_cache.clear()
            self._cache_time.clear()


# =============================================================================
# DEFAULT AGENT CONFIGURATIONS
# =============================================================================

# These are the recommended model configurations for each agent category.
# Used when populating initial database configs.

DEFAULT_AGENT_CONFIGS = {
    # Time-Series Agents (Phase 2 - LSTM and Prophet)
    'StockAnalystAgent': {
        'category': 'time_series',
        'primary_model': 'lstm',  # Phase 2: LSTM for price prediction
        'secondary_model': 'lightgbm',
        'model_weights': {'lstm': 0.7, 'lightgbm': 0.3},
    },
    'MarketMovementMonitorAgent': {
        'category': 'time_series',
        'primary_model': 'lstm',  # Phase 2: LSTM for market movements
        'secondary_model': 'random_forest',
        'model_weights': {'lstm': 0.6, 'random_forest': 0.4},
    },
    'WhaleWatcherAgent': {
        'category': 'graph',
        'primary_model': 'gnn',  # Phase 5: GNN for wallet relationship graphs
        'secondary_model': 'isolation_forest',
        'model_weights': {'gnn': 0.6, 'isolation_forest': 0.4},
    },
    'TrendAnalysisAgent': {
        'category': 'time_series',
        'primary_model': 'prophet',  # Phase 2: Prophet for seasonal trends
        'secondary_model': 'lstm',
        'model_weights': {'prophet': 0.6, 'lstm': 0.4},
    },
    'SignalScannerAgent': {
        'category': 'time_series',
        'primary_model': 'lstm',  # Phase 2: LSTM for signal detection
        'secondary_model': 'rules',
        'model_weights': {'lstm': 0.7, 'rules': 0.3},
    },

    # Semantic/Text Agents
    'ResearchAgent': {
        'category': 'semantic',
        'primary_model': 'embeddings',
        'secondary_model': 'lightgbm',
        'model_weights': {'embeddings': 0.9, 'lightgbm': 0.1},
    },
    'ContentWriterAgent': {
        'category': 'semantic',
        'primary_model': 'distilbert',
        'secondary_model': 'embeddings',
        'model_weights': {'distilbert': 0.7, 'embeddings': 0.3},
    },
    'SocialMediaAgent': {
        'category': 'graph',
        'primary_model': 'gnn',  # Phase 5: GNN for social network analysis
        'secondary_model': 'distilbert',
        'model_weights': {'gnn': 0.5, 'distilbert': 0.5},
    },
    'SEOOptimizerAgent': {
        'category': 'semantic',
        'primary_model': 'embeddings',
        'secondary_model': 'kmeans',
        'model_weights': {'embeddings': 0.7, 'kmeans': 0.3},
    },
    'ContentStrategyAgent': {
        'category': 'semantic',
        'primary_model': 'embeddings',
        'secondary_model': 'lightgbm',
        'model_weights': {'embeddings': 0.6, 'lightgbm': 0.4},
    },

    # Anomaly/Security Agents (Phase 3 - VAE Autoencoder)
    'BlockchainAuditCoordinator': {
        'category': 'anomaly',
        'primary_model': 'isolation_forest',
        'secondary_model': 'autoencoder',  # Phase 3: VAE for complex patterns
        'model_weights': {'isolation_forest': 0.5, 'autoencoder': 0.5},
    },
    'ExploitDetectorAgent': {
        'category': 'anomaly',
        'primary_model': 'autoencoder',  # Phase 3: VAE for exploit detection
        'secondary_model': 'isolation_forest',
        'model_weights': {'autoencoder': 0.6, 'isolation_forest': 0.4},
    },
    'SmartContractAuditorAgent': {
        'category': 'anomaly',
        'primary_model': 'isolation_forest',
        'secondary_model': 'autoencoder',  # Phase 3: VAE as secondary
        'model_weights': {'isolation_forest': 0.5, 'autoencoder': 0.5},
    },
    'TransactionMonitorAgent': {
        'category': 'anomaly',
        'primary_model': 'autoencoder',  # Phase 3: VAE for transaction anomalies
        'secondary_model': 'isolation_forest',
        'model_weights': {'autoencoder': 0.6, 'isolation_forest': 0.4},
    },
    'MarketAnomalyDetectorAgent': {
        'category': 'anomaly',
        'primary_model': 'autoencoder',  # Phase 3: VAE for market anomalies
        'secondary_model': 'isolation_forest',
        'model_weights': {'autoencoder': 0.7, 'isolation_forest': 0.3},
    },
    'ContentAuditAgent': {
        'category': 'anomaly',
        'primary_model': 'isolation_forest',
        'secondary_model': 'distilbert',
        'model_weights': {'isolation_forest': 0.7, 'distilbert': 0.3},
    },

    # Decision/Optimization Agents (Phase 4 - Reinforcement Learning)
    'OpportunityScoringAgent': {
        'category': 'decision',
        'primary_model': 'rl',  # Phase 4: RL for opportunity ranking
        'secondary_model': 'lightgbm',
        'model_weights': {'rl': 0.6, 'lightgbm': 0.4},
    },
    'OpportunityPipelineAgent': {
        'category': 'decision',
        'primary_model': 'lightgbm',
        'secondary_model': 'rl',  # Phase 4: RL as secondary
        'model_weights': {'lightgbm': 0.6, 'rl': 0.4},
    },
    'PredictionMarketAnalyst': {
        'category': 'decision',
        'primary_model': 'prophet',  # Phase 2: Prophet for market predictions
        'secondary_model': 'rl',  # Phase 4: RL for action selection
        'model_weights': {'prophet': 0.5, 'rl': 0.5},
    },
    'ArbitrageDetector': {
        'category': 'decision',
        'primary_model': 'rl',  # Phase 4: RL for arbitrage decisions
        'secondary_model': 'rules',
        'model_weights': {'rl': 0.7, 'rules': 0.3},
    },
    'ThinkingAgent': {
        'category': 'decision',
        'primary_model': 'rl',  # Phase 4: RL for decision evaluation
        'secondary_model': 'embeddings',
        'model_weights': {'rl': 0.6, 'embeddings': 0.4},
    },

    # Segmentation/Clustering Agents (Phase 5 - GNN for relationship graphs)
    'MarketIntelligenceAgent': {
        'category': 'clustering',
        'primary_model': 'gnn',  # Phase 5: GNN for market entity relationships
        'secondary_model': 'kmeans',
        'model_weights': {'gnn': 0.6, 'kmeans': 0.4},
    },
    'CustomerResearchAgent': {
        'category': 'clustering',
        'primary_model': 'gnn',  # Phase 5: GNN for customer networks
        'secondary_model': 'kmeans',
        'model_weights': {'gnn': 0.6, 'kmeans': 0.4},
    },
    'BrandStrategyAgent': {
        'category': 'clustering',
        'primary_model': 'embeddings',
        'secondary_model': 'gnn',  # Phase 5: GNN for brand relationships
        'model_weights': {'embeddings': 0.5, 'gnn': 0.5},
    },
    'CompetitorAnalysisAgent': {
        'category': 'clustering',
        'primary_model': 'gnn',  # Phase 5: GNN for competitor networks
        'secondary_model': 'cosine_similarity',
        'model_weights': {'gnn': 0.6, 'cosine_similarity': 0.4},
    },
}

# Default config for agents not in the above list
GENERAL_DEFAULT_CONFIG = {
    'category': 'general',
    'primary_model': 'lightgbm',
    'secondary_model': 'rules',
    'model_weights': {'lightgbm': 0.6, 'rules': 0.4},
}


def populate_default_configs():
    """
    Populate database with default configurations for all agents.

    This should be run once after migrations to set up initial configs.
    """
    from core.models_agent_models import AgentModelConfig

    # Get all known agents from AgentRouter
    try:
        from core.agent_router import AgentRouter
        router = AgentRouter()
        all_agents = list(router.agents.keys())
    except Exception:
        all_agents = list(DEFAULT_AGENT_CONFIGS.keys())

    created_count = 0
    updated_count = 0

    for agent_name in all_agents:
        # Get specific config or use general default
        config = DEFAULT_AGENT_CONFIGS.get(agent_name, GENERAL_DEFAULT_CONFIG).copy()

        try:
            obj, created = AgentModelConfig.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'category': config.get('category', 'general'),
                    'primary_model': config['primary_model'],
                    'secondary_model': config.get('secondary_model', 'rules'),
                    'model_weights': config.get('model_weights', {}),
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception as e:
            logger.error(f"Failed to create config for {agent_name}: {e}")

    logger.info(f"Populated agent configs: {created_count} created, {updated_count} updated")
    return created_count, updated_count


# Singleton instance
_router = None


def get_agent_model_router() -> AgentModelRouter:
    """Get the singleton agent model router instance."""
    global _router
    if _router is None:
        _router = AgentModelRouter()
    return _router
