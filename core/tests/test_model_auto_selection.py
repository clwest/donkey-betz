"""
Tests for Model Auto-Selection (Session 682 - Phase 6)
======================================================

Tests the automatic model selection system including:
- TaskAnalyzer for detecting task characteristics
- ModelScorer for scoring models
- ModelSelector for selecting optimal models
- Integration with AgentModelRouter.auto_route()
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase

from ml.auto_selection import (
    TaskAnalyzer,
    ModelScorer,
    ModelSelector,
    TaskType,
    DataCharacteristic,
    TaskAnalysis,
    ModelScore,
    AutoSelectionResult,
    get_model_selector,
    MODEL_TASK_SCORES,
    CHARACTERISTIC_BONUSES,
    CHARACTERISTIC_PENALTIES,
)


class TestTaskType(TestCase):
    """Test TaskType enum."""

    def test_task_types_exist(self):
        """Test all expected task types exist."""
        assert TaskType.TIME_SERIES.value == "time_series"
        assert TaskType.GRAPH.value == "graph"
        assert TaskType.TEXT.value == "text"
        assert TaskType.ANOMALY.value == "anomaly"
        assert TaskType.CLUSTERING.value == "clustering"
        assert TaskType.CLASSIFICATION.value == "classification"
        assert TaskType.REGRESSION.value == "regression"
        assert TaskType.DECISION.value == "decision"
        assert TaskType.UNKNOWN.value == "unknown"


class TestDataCharacteristic(TestCase):
    """Test DataCharacteristic enum."""

    def test_characteristics_exist(self):
        """Test all expected characteristics exist."""
        assert DataCharacteristic.SEQUENTIAL.value == "sequential"
        assert DataCharacteristic.TEMPORAL.value == "temporal"
        assert DataCharacteristic.GRAPH_STRUCTURE.value == "graph_structure"
        assert DataCharacteristic.HIGH_DIMENSIONAL.value == "high_dimensional"
        assert DataCharacteristic.SPARSE.value == "sparse"
        assert DataCharacteristic.DENSE.value == "dense"
        assert DataCharacteristic.TEXTUAL.value == "textual"


class TestTaskAnalysis(TestCase):
    """Test TaskAnalysis dataclass."""

    def test_create_task_analysis(self):
        """Test creating task analysis."""
        analysis = TaskAnalysis(
            task_type=TaskType.TIME_SERIES,
            characteristics=[DataCharacteristic.TEMPORAL, DataCharacteristic.SEQUENTIAL],
            confidence=0.85,
            num_samples=1000,
            has_timestamps=True,
        )

        assert analysis.task_type == TaskType.TIME_SERIES
        assert len(analysis.characteristics) == 2
        assert analysis.confidence == 0.85
        assert analysis.has_timestamps is True

    def test_to_dict(self):
        """Test converting to dict."""
        analysis = TaskAnalysis(
            task_type=TaskType.GRAPH,
            characteristics=[DataCharacteristic.GRAPH_STRUCTURE],
            confidence=0.9,
        )

        result = analysis.to_dict()

        assert result['task_type'] == 'graph'
        assert 'graph_structure' in result['characteristics']


class TestModelScore(TestCase):
    """Test ModelScore dataclass."""

    def test_create_model_score(self):
        """Test creating model score."""
        score = ModelScore(
            model_name='lstm',
            score=0.85,
            reasons=['Good fit for time_series tasks (0.95)'],
            penalties=[],
            is_available=True,
        )

        assert score.model_name == 'lstm'
        assert score.score == 0.85
        assert len(score.reasons) == 1
        assert score.is_available is True

    def test_to_dict(self):
        """Test converting to dict."""
        score = ModelScore(
            model_name='gnn',
            score=0.9,
            reasons=['Good for graphs'],
            is_available=True,
        )

        result = score.to_dict()

        assert result['model_name'] == 'gnn'
        assert result['score'] == 0.9


class TestAutoSelectionResult(TestCase):
    """Test AutoSelectionResult dataclass."""

    def test_create_result(self):
        """Test creating auto-selection result."""
        result = AutoSelectionResult(
            success=True,
            recommended_models=['lstm', 'lightgbm'],
            model_weights={'lstm': 0.7, 'lightgbm': 0.3},
            confidence=0.8,
        )

        assert result.success is True
        assert 'lstm' in result.recommended_models
        assert result.model_weights['lstm'] == 0.7

    def test_to_dict(self):
        """Test converting to dict."""
        result = AutoSelectionResult(
            success=True,
            recommended_models=['gnn'],
            selection_reason='Best for graph data',
        )

        d = result.to_dict()

        assert d['success'] is True
        assert 'gnn' in d['recommended_models']


class TestTaskAnalyzer(TestCase):
    """Test TaskAnalyzer class."""

    def setUp(self):
        self.analyzer = TaskAnalyzer()

    def test_analyze_time_series_dict(self):
        """Test analyzing time series data in dict format."""
        data = {
            'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'price': [100, 105, 102],
            'volume': [1000, 1200, 900],
        }

        analysis = self.analyzer.analyze(data)

        assert analysis.task_type == TaskType.TIME_SERIES
        assert analysis.has_timestamps is True
        assert DataCharacteristic.TEMPORAL in analysis.characteristics

    def test_analyze_graph_data(self):
        """Test analyzing graph data."""
        data = {
            'nodes': ['A', 'B', 'C', 'D'],
            'edges': [['A', 'B'], ['B', 'C'], ['C', 'D']],
        }

        analysis = self.analyzer.analyze(data)

        assert analysis.task_type == TaskType.GRAPH
        assert analysis.has_edges is True
        assert analysis.has_nodes is True
        assert DataCharacteristic.GRAPH_STRUCTURE in analysis.characteristics

    def test_analyze_text_data(self):
        """Test analyzing text data."""
        data = {
            'text': 'This is a long text content that should be detected as textual data for analysis purposes.',
            'label': 'positive',
        }

        analysis = self.analyzer.analyze(data)

        assert analysis.task_type == TaskType.TEXT
        assert analysis.has_text is True
        assert DataCharacteristic.TEXTUAL in analysis.characteristics

    def test_analyze_edge_list(self):
        """Test analyzing edge list format."""
        data = [
            ('user1', 'user2'),
            ('user2', 'user3'),
            ('user1', 'user3'),
        ]

        analysis = self.analyzer.analyze(data)

        assert analysis.task_type == TaskType.GRAPH
        assert analysis.has_edges is True
        assert DataCharacteristic.GRAPH_STRUCTURE in analysis.characteristics

    def test_analyze_numerical_list(self):
        """Test analyzing numerical list."""
        data = [100, 105, 102, 108, 110, 107]

        analysis = self.analyzer.analyze(data)

        assert analysis.task_type == TaskType.TIME_SERIES
        assert DataCharacteristic.SEQUENTIAL in analysis.characteristics
        assert DataCharacteristic.NUMERICAL in analysis.characteristics

    def test_analyze_numpy_array(self):
        """Test analyzing numpy array."""
        data = np.random.randn(100, 10)

        analysis = self.analyzer.analyze(data)

        assert analysis.num_samples == 100
        assert analysis.num_features == 10
        assert DataCharacteristic.NUMERICAL in analysis.characteristics

    def test_analyze_high_dimensional(self):
        """Test detecting high dimensional data."""
        data = np.random.randn(50, 100)  # 100 features

        analysis = self.analyzer.analyze(data)

        assert DataCharacteristic.HIGH_DIMENSIONAL in analysis.characteristics

    def test_analyze_sparse_data(self):
        """Test detecting sparse data."""
        data = np.zeros((100, 50))
        data[0, 0] = 1  # Very sparse

        analysis = self.analyzer.analyze(data)

        assert DataCharacteristic.SPARSE in analysis.characteristics

    def test_analyze_with_hint(self):
        """Test analysis with task hint."""
        data = {'values': [1, 2, 3, 4, 5]}

        analysis = self.analyzer.analyze(data, hint=TaskType.ANOMALY)

        assert analysis.task_type == TaskType.ANOMALY

    def test_analyze_string(self):
        """Test analyzing string input."""
        data = "This is some text content for classification."

        analysis = self.analyzer.analyze(data)

        assert analysis.task_type == TaskType.TEXT
        assert analysis.has_text is True

    def test_analyze_empty_list(self):
        """Test analyzing empty list."""
        data = []

        analysis = self.analyzer.analyze(data)

        assert analysis.num_samples == 0

    def test_analyze_small_sample(self):
        """Test detecting small sample size."""
        data = np.random.randn(50, 5)

        analysis = self.analyzer.analyze(data)

        assert DataCharacteristic.SMALL_SAMPLE in analysis.characteristics

    def test_analyze_large_sample(self):
        """Test detecting large sample size."""
        data = np.random.randn(15000, 5)

        analysis = self.analyzer.analyze(data)

        assert DataCharacteristic.LARGE_SAMPLE in analysis.characteristics


class TestModelScorer(TestCase):
    """Test ModelScorer class."""

    def setUp(self):
        self.scorer = ModelScorer()

    def test_score_models_time_series(self):
        """Test scoring models for time series task."""
        analysis = TaskAnalysis(
            task_type=TaskType.TIME_SERIES,
            characteristics=[DataCharacteristic.TEMPORAL, DataCharacteristic.SEQUENTIAL],
            confidence=0.9,
        )

        available = ['lstm', 'prophet', 'lightgbm', 'kmeans']
        scores = self.scorer.score_models(analysis, available)

        # LSTM should score highest for time series
        assert scores[0].model_name == 'lstm'
        assert scores[0].score > 0.9  # Base 0.95 + bonuses

    def test_score_models_graph(self):
        """Test scoring models for graph task."""
        analysis = TaskAnalysis(
            task_type=TaskType.GRAPH,
            characteristics=[DataCharacteristic.GRAPH_STRUCTURE],
            confidence=0.9,
        )

        available = ['gnn', 'lstm', 'lightgbm', 'kmeans']
        scores = self.scorer.score_models(analysis, available)

        # GNN should score highest for graphs
        assert scores[0].model_name == 'gnn'
        assert scores[0].score > 0.95  # Base 0.95 + graph bonus

    def test_score_models_text(self):
        """Test scoring models for text task."""
        analysis = TaskAnalysis(
            task_type=TaskType.TEXT,
            characteristics=[DataCharacteristic.TEXTUAL],
            confidence=0.85,
        )

        available = ['distilbert', 'embeddings', 'lightgbm', 'kmeans']
        scores = self.scorer.score_models(analysis, available)

        # DistilBERT should score highest for text
        assert scores[0].model_name == 'distilbert'

    def test_score_models_anomaly(self):
        """Test scoring models for anomaly detection."""
        analysis = TaskAnalysis(
            task_type=TaskType.ANOMALY,
            characteristics=[DataCharacteristic.HIGH_DIMENSIONAL],
            confidence=0.8,
        )

        available = ['autoencoder', 'isolation_forest', 'lightgbm']
        scores = self.scorer.score_models(analysis, available)

        # Autoencoder should score highest
        assert scores[0].model_name == 'autoencoder'

    def test_score_models_with_penalties(self):
        """Test that penalties are applied correctly."""
        analysis = TaskAnalysis(
            task_type=TaskType.TIME_SERIES,
            characteristics=[DataCharacteristic.SMALL_SAMPLE],  # Penalty for LSTM
            confidence=0.7,
        )

        available = ['lstm', 'lightgbm']
        scores = self.scorer.score_models(analysis, available)

        # LSTM should have penalty applied
        lstm_score = next(s for s in scores if s.model_name == 'lstm')
        assert any('small_sample' in p.lower() for p in lstm_score.penalties)

    def test_score_models_unavailable(self):
        """Test that unavailable models get 0 score."""
        analysis = TaskAnalysis(
            task_type=TaskType.TIME_SERIES,
            confidence=0.8,
        )

        available = ['lightgbm']  # LSTM not available
        scores = self.scorer.score_models(analysis, available)

        # Find LSTM in results (should be marked unavailable)
        lstm_score = next((s for s in scores if s.model_name == 'lstm'), None)
        if lstm_score:
            assert lstm_score.is_available is False
            assert lstm_score.score == 0.0


class TestModelSelector(TestCase):
    """Test ModelSelector class."""

    def setUp(self):
        self.selector = ModelSelector()

    def test_select_models_time_series(self):
        """Test selecting models for time series data."""
        data = {
            'timestamp': ['2024-01-01', '2024-01-02'],
            'values': [100, 105],
        }

        result = self.selector.select_models(data)

        assert result.success is True
        assert len(result.recommended_models) > 0
        assert result.task_analysis.task_type == TaskType.TIME_SERIES

    def test_select_models_graph(self):
        """Test selecting models for graph data."""
        data = {
            'nodes': ['A', 'B', 'C'],
            'edges': [['A', 'B'], ['B', 'C']],
        }

        result = self.selector.select_models(data)

        assert result.success is True
        assert 'gnn' in result.recommended_models
        assert result.task_analysis.task_type == TaskType.GRAPH

    def test_select_models_with_hint(self):
        """Test selecting with task hint."""
        data = {'values': [1, 2, 3, 4, 5]}

        result = self.selector.select_models(data, task_hint=TaskType.ANOMALY)

        assert result.task_analysis.task_type == TaskType.ANOMALY
        # Should recommend anomaly models
        assert any(m in result.recommended_models for m in ['autoencoder', 'isolation_forest'])

    def test_select_models_max_models(self):
        """Test limiting number of models."""
        data = {'timestamp': ['2024-01-01'], 'value': [100]}

        result = self.selector.select_models(data, max_models=1)

        assert len(result.recommended_models) <= 1

    def test_select_models_min_score(self):
        """Test minimum score threshold."""
        data = {'values': [1, 2, 3]}

        result = self.selector.select_models(data, min_score=0.9)

        # Should still return at least one model (fallback)
        assert len(result.recommended_models) >= 1

    def test_select_models_weights(self):
        """Test that weights are calculated."""
        data = {
            'timestamp': ['2024-01-01', '2024-01-02'],
            'values': [100, 105],
        }

        result = self.selector.select_models(data, max_models=2)

        if len(result.recommended_models) == 2:
            assert len(result.model_weights) == 2
            # Weights should sum to ~1.0
            total = sum(result.model_weights.values())
            assert 0.99 <= total <= 1.01

    def test_select_models_selection_reason(self):
        """Test that selection reason is provided."""
        data = {
            'nodes': ['A', 'B'],
            'edges': [['A', 'B']],
        }

        result = self.selector.select_models(data)

        assert result.selection_reason is not None
        assert len(result.selection_reason) > 0

    def test_get_selection_history(self):
        """Test selection history tracking."""
        # Make some selections
        self.selector.select_models({'values': [1, 2, 3]})
        self.selector.select_models({'nodes': ['A'], 'edges': []})

        history = self.selector.get_selection_history()

        assert len(history) >= 2

    def test_get_task_statistics(self):
        """Test task statistics."""
        # Make some selections
        self.selector.select_models({'timestamp': ['2024-01-01'], 'v': [1]})
        self.selector.select_models({'nodes': ['A'], 'edges': []})

        stats = self.selector.get_task_statistics()

        assert 'total_selections' in stats
        assert 'task_distribution' in stats
        assert 'model_distribution' in stats

    def test_singleton(self):
        """Test singleton accessor."""
        selector1 = get_model_selector()
        selector2 = get_model_selector()

        assert selector1 is selector2


class TestModelTaskScores(TestCase):
    """Test MODEL_TASK_SCORES configuration."""

    def test_lstm_scores(self):
        """Test LSTM task scores."""
        scores = MODEL_TASK_SCORES.get('lstm', {})

        assert scores.get(TaskType.TIME_SERIES, 0) >= 0.9
        assert scores.get(TaskType.REGRESSION, 0) > 0

    def test_gnn_scores(self):
        """Test GNN task scores."""
        scores = MODEL_TASK_SCORES.get('gnn', {})

        assert scores.get(TaskType.GRAPH, 0) >= 0.9

    def test_autoencoder_scores(self):
        """Test autoencoder task scores."""
        scores = MODEL_TASK_SCORES.get('autoencoder', {})

        assert scores.get(TaskType.ANOMALY, 0) >= 0.9

    def test_all_models_have_scores(self):
        """Test that all expected models have scores."""
        expected_models = [
            'lstm', 'prophet', 'autoencoder', 'isolation_forest',
            'gnn', 'rl', 'distilbert', 'embeddings', 'lightgbm',
            'xgboost', 'random_forest', 'kmeans', 'cosine_similarity',
            'mlp', 'rules'
        ]

        for model in expected_models:
            assert model in MODEL_TASK_SCORES, f"{model} not in MODEL_TASK_SCORES"


class TestCharacteristicBonuses(TestCase):
    """Test CHARACTERISTIC_BONUSES configuration."""

    def test_lstm_bonuses(self):
        """Test LSTM characteristic bonuses."""
        bonuses = CHARACTERISTIC_BONUSES.get('lstm', {})

        assert bonuses.get(DataCharacteristic.SEQUENTIAL, 0) > 0
        assert bonuses.get(DataCharacteristic.TEMPORAL, 0) > 0

    def test_gnn_bonuses(self):
        """Test GNN characteristic bonuses."""
        bonuses = CHARACTERISTIC_BONUSES.get('gnn', {})

        assert bonuses.get(DataCharacteristic.GRAPH_STRUCTURE, 0) > 0

    def test_distilbert_bonuses(self):
        """Test DistilBERT characteristic bonuses."""
        bonuses = CHARACTERISTIC_BONUSES.get('distilbert', {})

        assert bonuses.get(DataCharacteristic.TEXTUAL, 0) > 0


class TestCharacteristicPenalties(TestCase):
    """Test CHARACTERISTIC_PENALTIES configuration."""

    def test_lstm_penalties(self):
        """Test LSTM characteristic penalties."""
        penalties = CHARACTERISTIC_PENALTIES.get('lstm', {})

        assert penalties.get(DataCharacteristic.SMALL_SAMPLE, 0) < 0

    def test_autoencoder_penalties(self):
        """Test autoencoder characteristic penalties."""
        penalties = CHARACTERISTIC_PENALTIES.get('autoencoder', {})

        assert penalties.get(DataCharacteristic.SMALL_SAMPLE, 0) < 0


class TestRouterAutoRoute(TestCase):
    """Test AgentModelRouter.auto_route() integration."""

    def test_auto_route_time_series(self):
        """Test auto_route with time series data."""
        from core.services.agent_model_router import get_agent_model_router

        router = get_agent_model_router()

        data = {
            'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'price': [100, 105, 102],
        }

        result = router.auto_route(data)

        assert result.success is True
        assert result.auto_selection is not None
        assert result.auto_selection['task_type'] == 'time_series'
        assert len(result.models_used) > 0

    def test_auto_route_graph(self):
        """Test auto_route with graph data."""
        from core.services.agent_model_router import get_agent_model_router

        router = get_agent_model_router()

        data = {
            'nodes': ['wallet_A', 'wallet_B', 'wallet_C'],
            'edges': [['wallet_A', 'wallet_B'], ['wallet_B', 'wallet_C']],
        }

        result = router.auto_route(data)

        assert result.success is True
        assert result.auto_selection is not None
        assert result.auto_selection['task_type'] == 'graph'

    def test_auto_route_with_hint(self):
        """Test auto_route with task hint."""
        from core.services.agent_model_router import get_agent_model_router
        from ml.auto_selection import TaskType

        router = get_agent_model_router()

        data = {'values': [1, 2, 3, 4, 5]}

        result = router.auto_route(data, task_hint=TaskType.DECISION)

        assert result.auto_selection['task_type'] == 'decision'

    def test_auto_route_with_agent_name(self):
        """Test auto_route with agent name."""
        from core.services.agent_model_router import get_agent_model_router

        router = get_agent_model_router()

        data = {'text': 'Some content for analysis'}

        result = router.auto_route(data, agent_name='TestAgent')

        assert result.agent_name == 'TestAgent'

    def test_auto_route_selection_info(self):
        """Test that auto_selection contains expected fields."""
        from core.services.agent_model_router import get_agent_model_router

        router = get_agent_model_router()

        data = {
            'nodes': ['A', 'B'],
            'edges': [['A', 'B']],
        }

        result = router.auto_route(data)

        assert 'task_type' in result.auto_selection
        assert 'characteristics' in result.auto_selection
        assert 'recommended_models' in result.auto_selection
        assert 'selection_reason' in result.auto_selection
        assert 'selection_confidence' in result.auto_selection

    def test_compare_auto_vs_config(self):
        """Test comparing auto-selection vs config."""
        from core.services.agent_model_router import (
            get_agent_model_router,
            populate_default_configs,
        )

        # Ensure configs exist
        populate_default_configs()

        router = get_agent_model_router()
        router.invalidate_cache()

        data = {
            'timestamp': ['2024-01-01', '2024-01-02'],
            'price': [100, 105],
        }

        comparison = router.compare_auto_vs_config('StockAnalystAgent', data)

        assert 'configured' in comparison
        assert 'auto_selected' in comparison
        assert 'models_match' in comparison
        assert 'score_difference' in comparison
        assert 'recommendation' in comparison

    def test_get_model_selector(self):
        """Test getting model selector from router."""
        from core.services.agent_model_router import get_agent_model_router

        router = get_agent_model_router()
        selector = router.get_model_selector()

        assert selector is not None
        assert hasattr(selector, 'select_models')


class TestEdgeCases(TestCase):
    """Test edge cases and error handling."""

    def test_empty_data(self):
        """Test with empty data."""
        selector = ModelSelector()

        result = selector.select_models({})

        # Should still succeed with fallback
        assert result.success is True
        assert len(result.recommended_models) >= 1

    def test_none_values(self):
        """Test with None values in data."""
        selector = ModelSelector()

        data = {'values': None, 'other': [1, 2, 3]}

        result = selector.select_models(data)

        assert result.success is True

    def test_mixed_data_types(self):
        """Test with mixed data types."""
        selector = ModelSelector()

        data = {
            'numbers': [1, 2, 3],
            'text': 'some content',
            'timestamp': '2024-01-01',
        }

        result = selector.select_models(data)

        assert result.success is True
        # Should detect mixed characteristics
        assert len(result.task_analysis.characteristics) > 1

    def test_very_small_data(self):
        """Test with very small dataset."""
        selector = ModelSelector()

        data = np.array([[1, 2]])

        result = selector.select_models(data)

        assert result.success is True
        assert DataCharacteristic.SMALL_SAMPLE in result.task_analysis.characteristics

    def test_unknown_task_type(self):
        """Test when task type cannot be determined."""
        analyzer = TaskAnalyzer()

        # Minimal data that's hard to classify
        analysis = analyzer.analyze({})

        # Should return UNKNOWN or a reasonable default
        assert analysis.task_type is not None

    def test_all_models_unavailable(self):
        """Test when no models are available."""
        selector = ModelSelector()

        # Mock registry to return no models
        with patch.object(selector, '_get_available_models', return_value=[]):
            result = selector.select_models({'values': [1, 2, 3]})

            assert result.success is False
            assert 'No models available' in result.error
