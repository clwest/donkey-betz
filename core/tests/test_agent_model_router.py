"""
Tests for Agent-Model Router (Session 677)
==========================================

Tests the agent-to-model routing infrastructure including:
- Model registry and wrappers
- AgentModelConfig model
- AgentModelRouter routing logic
- Ensemble predictions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone

from core.models_agent_models import (
    AgentModelConfig,
    ModelPerformanceLog,
    ModelTrainingRun,
)
from core.services.model_registry import (
    ModelRegistry,
    BaseModelWrapper,
    LightGBMWrapper,
    RulesWrapper,
    ModelPrediction,
    get_model_registry,
)
from core.services.agent_model_router import (
    AgentModelRouter,
    EnsemblePrediction,
    DEFAULT_AGENT_CONFIGS,
    populate_default_configs,
    get_agent_model_router,
)


class TestAgentModelConfig(TestCase):
    """Test AgentModelConfig model."""

    def test_create_config(self):
        """Test creating an agent model config."""
        config = AgentModelConfig.objects.create(
            agent_name='TestAgent',
            category='general',
            primary_model='lightgbm',
            secondary_model='rules',
            model_weights={'lightgbm': 0.7, 'rules': 0.3},
        )

        assert config.agent_name == 'TestAgent'
        assert config.category == 'general'
        assert config.primary_model == 'lightgbm'
        assert config.secondary_model == 'rules'
        assert config.is_active is True
        assert config.use_fallback is True

    def test_get_model_ensemble(self):
        """Test getting model ensemble with weights."""
        config = AgentModelConfig.objects.create(
            agent_name='EnsembleTestAgent',
            category='decision',
            primary_model='lightgbm',
            secondary_model='xgboost',
            tertiary_model='rules',
            model_weights={'lightgbm': 0.5, 'xgboost': 0.3, 'rules': 0.2},
        )

        ensemble = config.get_model_ensemble()

        assert len(ensemble) == 3
        assert ensemble[0] == ('lightgbm', 0.5)
        assert ensemble[1] == ('xgboost', 0.3)
        assert ensemble[2] == ('rules', 0.2)

    def test_record_prediction(self):
        """Test recording prediction metrics."""
        config = AgentModelConfig.objects.create(
            agent_name='PredictionTestAgent',
            category='general',
            primary_model='lightgbm',
        )

        # Record successful prediction
        config.record_prediction(success=True, latency_ms=50.0)

        assert config.total_predictions == 1
        assert config.successful_predictions == 1
        assert config.avg_latency_ms == 50.0
        assert config.performance_score == 100.0

        # Record failed prediction
        config.record_prediction(success=False, latency_ms=100.0)

        assert config.total_predictions == 2
        assert config.successful_predictions == 1
        assert config.performance_score == 50.0

    def test_str_representation(self):
        """Test string representation."""
        config = AgentModelConfig.objects.create(
            agent_name='StrTestAgent',
            primary_model='embeddings',
            model_weights={'embeddings': 0.9},
        )

        assert 'StrTestAgent' in str(config)
        assert 'embeddings' in str(config)


class TestModelPerformanceLog(TestCase):
    """Test ModelPerformanceLog model."""

    def test_create_log(self):
        """Test creating a performance log."""
        config = AgentModelConfig.objects.create(
            agent_name='LogTestAgent',
            primary_model='lightgbm',
        )

        log = ModelPerformanceLog.objects.create(
            config=config,
            metric_name='accuracy',
            metric_value=0.95,
            sample_count=1000,
        )

        assert log.config == config
        assert log.metric_name == 'accuracy'
        assert log.metric_value == 0.95
        assert log.sample_count == 1000


class TestModelTrainingRun(TestCase):
    """Test ModelTrainingRun model."""

    def test_create_training_run(self):
        """Test creating a training run."""
        run = ModelTrainingRun.objects.create(
            model_type='lightgbm',
            version='v1.0',
            hyperparameters={'learning_rate': 0.1, 'n_estimators': 100},
        )

        assert run.model_type == 'lightgbm'
        assert run.version == 'v1.0'
        assert run.status == 'queued'
        assert run.hyperparameters['learning_rate'] == 0.1

    def test_mark_completed(self):
        """Test marking training as completed."""
        run = ModelTrainingRun.objects.create(
            model_type='xgboost',
            version='v2.0',
        )
        run.status = 'running'
        run.save()

        run.mark_completed(metrics={'accuracy': 0.92, 'f1': 0.89})

        assert run.status == 'completed'
        assert run.completed_at is not None
        assert run.metrics['accuracy'] == 0.92

    def test_mark_failed(self):
        """Test marking training as failed."""
        run = ModelTrainingRun.objects.create(
            model_type='lstm',
            version='v1.0',
        )
        run.status = 'running'
        run.save()

        run.mark_failed('Out of memory')

        assert run.status == 'failed'
        assert 'Out of memory' in run.error_message


class TestModelRegistry(TestCase):
    """Test ModelRegistry class."""

    def test_list_available_models(self):
        """Test listing available models."""
        registry = ModelRegistry()
        models = registry.list_available_models()

        # Should include at least rules since it's always available
        assert 'rules' in models
        assert isinstance(models, list)

    def test_get_model_lightgbm(self):
        """Test getting LightGBM wrapper."""
        registry = ModelRegistry()
        model = registry.get_model('lightgbm')

        assert model is not None
        assert isinstance(model, LightGBMWrapper)

    def test_get_model_rules(self):
        """Test getting rules wrapper."""
        registry = ModelRegistry()
        model = registry.get_model('rules')

        assert model is not None
        assert isinstance(model, RulesWrapper)

    def test_get_model_unknown(self):
        """Test getting unknown model returns None."""
        registry = ModelRegistry()
        model = registry.get_model('unknown_model')

        assert model is None

    def test_singleton_registry(self):
        """Test get_model_registry returns singleton."""
        registry1 = get_model_registry()
        registry2 = get_model_registry()

        assert registry1 is registry2


class TestRulesWrapper(TestCase):
    """Test RulesWrapper predictions."""

    def test_predict_with_text(self):
        """Test prediction with text in data."""
        wrapper = RulesWrapper()
        result = wrapper.predict({'text': 'This is an AI ml opportunity for profit'})

        assert isinstance(result, ModelPrediction)
        assert result.success is True
        assert result.model_name == 'rules'
        # Should have matched keywords AI, ML, opportunity, profit
        assert result.score > 50

    def test_predict_with_no_keywords(self):
        """Test prediction with text but no matching keywords."""
        wrapper = RulesWrapper()
        result = wrapper.predict({'text': 'Just some random text'})

        assert isinstance(result, ModelPrediction)
        assert result.success is True
        assert result.score == 50  # Base score


class TestAgentModelRouter(TestCase):
    """Test AgentModelRouter class."""

    def test_get_agent_config_from_database(self):
        """Test getting config from database."""
        # Create config in database
        AgentModelConfig.objects.create(
            agent_name='DatabaseTestAgent',
            category='semantic',
            primary_model='embeddings',
            model_weights={'embeddings': 1.0},
        )

        router = AgentModelRouter()
        config = router.get_agent_config('DatabaseTestAgent')

        assert config is not None
        assert config['primary_model'] == 'embeddings'

    def test_get_agent_config_default_fallback(self):
        """Test getting default config for unknown agent."""
        router = AgentModelRouter()
        config = router.get_agent_config('UnknownAgent')

        # Should return default config
        assert config is not None
        assert config['primary_model'] == 'lightgbm'

    def test_route_single_model(self):
        """Test routing with single model."""
        AgentModelConfig.objects.create(
            agent_name='SingleModelAgent',
            primary_model='rules',
            model_weights={'rules': 1.0},
        )

        router = AgentModelRouter()
        result = router.route('SingleModelAgent', {'text': 'AI opportunity for profit'})

        assert isinstance(result, EnsemblePrediction)
        assert result.agent_name == 'SingleModelAgent'
        assert len(result.models_used) >= 1
        assert 'rules' in result.model_scores
        assert result.model_scores['rules'] > 50  # Should have matched keywords

    def test_route_ensemble(self):
        """Test routing with ensemble of models."""
        AgentModelConfig.objects.create(
            agent_name='EnsembleAgent',
            primary_model='rules',
            secondary_model='rules',  # Use rules twice for simplicity
            model_weights={'rules': 0.6},
        )

        router = AgentModelRouter()
        result = router.route('EnsembleAgent', {'text': 'trending market opportunity'})

        assert isinstance(result, EnsemblePrediction)
        assert result.score is not None
        assert result.success is True

    def test_singleton_router(self):
        """Test get_agent_model_router returns singleton."""
        router1 = get_agent_model_router()
        router2 = get_agent_model_router()

        assert router1 is router2

    def test_set_agent_config(self):
        """Test setting agent configuration."""
        router = AgentModelRouter()
        success = router.set_agent_config(
            'NewTestAgent',
            primary_model='xgboost',
            secondary_model='rules',
            model_weights={'xgboost': 0.7, 'rules': 0.3},
            category='decision',
        )

        assert success is True

        # Verify config was saved
        config = AgentModelConfig.objects.filter(agent_name='NewTestAgent').first()
        assert config is not None
        assert config.primary_model == 'xgboost'


class TestDefaultConfigs(TestCase):
    """Test default agent configurations."""

    def test_default_configs_exist(self):
        """Test that default configs are defined."""
        assert len(DEFAULT_AGENT_CONFIGS) > 0

        # Check some key agents
        assert 'ResearchAgent' in DEFAULT_AGENT_CONFIGS
        assert 'StockAnalystAgent' in DEFAULT_AGENT_CONFIGS
        assert 'BlockchainAuditCoordinator' in DEFAULT_AGENT_CONFIGS

    def test_research_agent_config(self):
        """Test ResearchAgent uses embeddings."""
        config = DEFAULT_AGENT_CONFIGS['ResearchAgent']

        assert config['category'] == 'semantic'
        assert config['primary_model'] == 'embeddings'
        assert config['model_weights']['embeddings'] > 0.5

    def test_blockchain_agent_config(self):
        """Test BlockchainAuditCoordinator uses anomaly detection."""
        config = DEFAULT_AGENT_CONFIGS['BlockchainAuditCoordinator']

        assert config['category'] == 'anomaly'
        assert config['primary_model'] == 'isolation_forest'

    def test_populate_default_configs(self):
        """Test populating default configs."""
        # Clear existing configs
        AgentModelConfig.objects.all().delete()

        created, updated = populate_default_configs()

        # Should create configs for all default agents
        assert created >= len(DEFAULT_AGENT_CONFIGS)
        assert updated == 0

        # Verify in database
        assert AgentModelConfig.objects.count() >= len(DEFAULT_AGENT_CONFIGS)

    def test_populate_idempotent(self):
        """Test populating is idempotent."""
        # Clear and populate first time
        AgentModelConfig.objects.all().delete()
        created1, updated1 = populate_default_configs()

        # Populate again
        created2, updated2 = populate_default_configs()

        # Should update, not create duplicates
        assert created2 == 0
        assert updated2 >= len(DEFAULT_AGENT_CONFIGS)


class TestEnsemblePrediction(TestCase):
    """Test EnsemblePrediction dataclass."""

    def test_create_ensemble_prediction(self):
        """Test creating ensemble prediction."""
        prediction = EnsemblePrediction(
            success=True,
            agent_name='TestAgent',
            score=0.75,
            confidence=0.85,
            model_scores={'lightgbm': 0.8, 'rules': 0.7},
            model_weights={'lightgbm': 0.6, 'rules': 0.4},
            models_used=['lightgbm', 'rules'],
            latency_ms=25.5,
        )

        assert prediction.agent_name == 'TestAgent'
        assert prediction.score == 0.75
        assert prediction.confidence == 0.85
        assert len(prediction.model_scores) == 2
        assert prediction.latency_ms == 25.5
        assert prediction.success is True

    def test_ensemble_prediction_to_dict(self):
        """Test converting prediction to dict."""
        prediction = EnsemblePrediction(
            success=True,
            score=0.8,
            agent_name='DictTestAgent',
        )

        result = prediction.to_dict()

        assert isinstance(result, dict)
        assert result['success'] is True
        assert result['score'] == 0.8
        assert result['agent_name'] == 'DictTestAgent'


class TestModelPrediction(TestCase):
    """Test ModelPrediction dataclass."""

    def test_create_model_prediction(self):
        """Test creating a model prediction."""
        pred = ModelPrediction(
            success=True,
            score=0.9,
            confidence=0.85,
            model_name='lightgbm',
        )

        assert pred.success is True
        assert pred.score == 0.9
        assert pred.confidence == 0.85
        assert pred.model_name == 'lightgbm'

    def test_model_prediction_to_dict(self):
        """Test converting to dict."""
        pred = ModelPrediction(
            success=True,
            score=0.75,
            model_name='rules',
        )

        result = pred.to_dict()

        assert isinstance(result, dict)
        assert result['success'] is True
        assert result['score'] == 0.75
