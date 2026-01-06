"""
Tests for Time-Series Models (Session 678 - Phase 2)
=====================================================

Tests the LSTM and Prophet time-series models including:
- LSTMTimeSeriesModel functionality
- ProphetForecaster functionality
- Integration with model registry
- Fallback mode behavior
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from django.test import TestCase

from ml.time_series.lstm_time_series import (
    LSTMTimeSeriesModel,
    LSTMPrediction,
    get_lstm_model,
)
from ml.time_series.prophet_forecaster import (
    ProphetForecaster,
    ProphetPrediction,
    get_prophet_model,
)
from core.services.model_registry import (
    ModelRegistry,
    LSTMWrapper,
    ProphetWrapper,
    get_model_registry,
)


class TestLSTMPrediction(TestCase):
    """Test LSTMPrediction dataclass."""

    def test_create_prediction(self):
        """Test creating an LSTM prediction."""
        pred = LSTMPrediction(
            success=True,
            predictions=[100.5, 101.2, 102.0],
            direction='up',
            confidence=0.75,
            trend_strength=0.6,
            volatility=0.05,
        )

        assert pred.success is True
        assert len(pred.predictions) == 3
        assert pred.direction == 'up'
        assert pred.confidence == 0.75

    def test_to_dict(self):
        """Test converting to dict."""
        pred = LSTMPrediction(
            success=True,
            predictions=[100.0, 101.0],
            direction='neutral',
        )

        result = pred.to_dict()

        assert isinstance(result, dict)
        assert result['success'] is True
        assert result['predictions'] == [100.0, 101.0]


class TestLSTMTimeSeriesModel(TestCase):
    """Test LSTMTimeSeriesModel class."""

    def test_init(self):
        """Test model initialization."""
        model = LSTMTimeSeriesModel(model_name="test_lstm")

        assert model.model_name == "test_lstm"
        assert model.is_trained is False
        assert model.config['sequence_length'] == 60

    def test_predict_with_fallback_list(self):
        """Test fallback prediction with list input."""
        model = LSTMTimeSeriesModel()

        # Generate sample data
        data = list(np.random.randn(100).cumsum() + 100)

        result = model.predict_with_fallback(data)

        assert result.success is True
        assert len(result.predictions) == 5  # Default prediction horizon
        assert result.direction in ['up', 'down', 'neutral']
        assert 0 <= result.confidence <= 1
        assert result.metadata.get('fallback_mode') is True

    def test_predict_with_fallback_dict(self):
        """Test fallback prediction with dict input."""
        model = LSTMTimeSeriesModel()

        data = {'prices': list(np.linspace(100, 120, 100))}  # Upward trend

        result = model.predict_with_fallback(data)

        assert result.success is True
        assert result.direction == 'up'

    def test_predict_insufficient_data(self):
        """Test prediction with insufficient data."""
        model = LSTMTimeSeriesModel()

        result = model.predict_with_fallback([1, 2, 3])  # Only 3 points

        assert result.success is False
        assert 'data points' in result.error.lower()

    def test_predict_with_fallback_downtrend(self):
        """Test fallback detects downtrend."""
        model = LSTMTimeSeriesModel()

        # Create downward trending data
        data = list(np.linspace(120, 80, 100))

        result = model.predict_with_fallback(data)

        assert result.success is True
        assert result.direction == 'down'

    def test_get_lstm_model_singleton(self):
        """Test singleton pattern."""
        model1 = get_lstm_model()
        model2 = get_lstm_model()

        assert model1 is model2


class TestProphetPrediction(TestCase):
    """Test ProphetPrediction dataclass."""

    def test_create_prediction(self):
        """Test creating a Prophet prediction."""
        pred = ProphetPrediction(
            success=True,
            predictions=[100.5, 101.2, 102.0],
            trend='increasing',
            trend_slope=0.5,
            confidence=0.7,
        )

        assert pred.success is True
        assert pred.trend == 'increasing'
        assert pred.trend_slope == 0.5

    def test_to_dict(self):
        """Test converting to dict."""
        pred = ProphetPrediction(
            success=True,
            predictions=[100.0],
            dates=['2026-01-01'],
            trend='stable',
        )

        result = pred.to_dict()

        assert isinstance(result, dict)
        assert result['trend'] == 'stable'
        assert result['dates'] == ['2026-01-01']


class TestProphetForecaster(TestCase):
    """Test ProphetForecaster class."""

    def test_init(self):
        """Test forecaster initialization."""
        model = ProphetForecaster(model_name="test_prophet")

        assert model.model_name == "test_prophet"
        assert model.is_trained is False
        assert model.config['prediction_days'] == 30

    def test_predict_with_fallback_list(self):
        """Test fallback prediction with list input."""
        model = ProphetForecaster()

        data = list(np.random.randn(100).cumsum() + 100)

        result = model.predict_with_fallback(data, periods=10)

        assert result.success is True
        assert len(result.predictions) == 10
        assert result.trend in ['increasing', 'decreasing', 'stable']
        assert len(result.dates) == 10
        assert result.metadata.get('fallback_mode') is True

    def test_predict_with_fallback_dict(self):
        """Test fallback prediction with dict input."""
        model = ProphetForecaster()

        data = {'values': list(np.linspace(100, 150, 100))}  # Uptrend

        result = model.predict_with_fallback(data)

        assert result.success is True
        assert result.trend == 'increasing'

    def test_predict_insufficient_data(self):
        """Test prediction with insufficient data."""
        model = ProphetForecaster()

        result = model.predict_with_fallback([1, 2, 3, 4, 5])  # Only 5 points

        assert result.success is False
        assert 'data points' in result.error.lower()

    def test_predict_with_bounds(self):
        """Test predictions include bounds."""
        model = ProphetForecaster()

        data = list(np.random.randn(50).cumsum() + 100)

        result = model.predict_with_fallback(data, periods=5)

        assert result.success is True
        assert len(result.lower_bounds) == 5
        assert len(result.upper_bounds) == 5
        # Upper bounds should be greater than predictions
        for i in range(5):
            assert result.upper_bounds[i] >= result.predictions[i]
            assert result.lower_bounds[i] <= result.predictions[i]

    def test_get_prophet_model_singleton(self):
        """Test singleton pattern."""
        model1 = get_prophet_model()
        model2 = get_prophet_model()

        assert model1 is model2


class TestLSTMWrapper(TestCase):
    """Test LSTMWrapper integration."""

    def test_wrapper_init(self):
        """Test wrapper initialization."""
        wrapper = LSTMWrapper()

        assert wrapper.model_name == 'lstm'
        assert wrapper.version == 'v1.0'

    def test_wrapper_is_available(self):
        """Test wrapper availability."""
        wrapper = LSTMWrapper()

        # Should be available (fallback mode works)
        assert wrapper.is_available() is True

    def test_wrapper_predict(self):
        """Test wrapper prediction."""
        wrapper = LSTMWrapper()

        data = {'prices': list(np.random.randn(100).cumsum() + 100)}
        result = wrapper.predict(data)

        assert result.success is True
        assert result.model_name == 'lstm'
        assert 'direction' in result.explanation
        assert 'trend_strength' in result.explanation

    def test_wrapper_from_registry(self):
        """Test getting wrapper from registry."""
        registry = ModelRegistry()
        wrapper = registry.get_model('lstm')

        assert wrapper is not None
        assert isinstance(wrapper, LSTMWrapper)
        assert wrapper.is_available() is True


class TestProphetWrapper(TestCase):
    """Test ProphetWrapper integration."""

    def test_wrapper_init(self):
        """Test wrapper initialization."""
        wrapper = ProphetWrapper()

        assert wrapper.model_name == 'prophet'
        assert wrapper.version == 'v1.0'

    def test_wrapper_is_available(self):
        """Test wrapper availability."""
        wrapper = ProphetWrapper()

        # Should be available (fallback mode works)
        assert wrapper.is_available() is True

    def test_wrapper_predict(self):
        """Test wrapper prediction."""
        wrapper = ProphetWrapper()

        data = {'prices': list(np.random.randn(100).cumsum() + 100)}
        result = wrapper.predict(data, periods=7)

        assert result.success is True
        assert result.model_name == 'prophet'
        assert 'trend' in result.explanation
        assert 'seasonality' in result.explanation

    def test_wrapper_from_registry(self):
        """Test getting wrapper from registry."""
        registry = ModelRegistry()
        wrapper = registry.get_model('prophet')

        assert wrapper is not None
        assert isinstance(wrapper, ProphetWrapper)
        assert wrapper.is_available() is True


class TestRegistryIntegration(TestCase):
    """Test integration with model registry."""

    def test_lstm_in_available_models(self):
        """Test LSTM appears in available models."""
        registry = get_model_registry()
        available = registry.list_available_models()

        assert 'lstm' in available

    def test_prophet_in_available_models(self):
        """Test Prophet appears in available models."""
        registry = get_model_registry()
        available = registry.list_available_models()

        assert 'prophet' in available

    def test_time_series_agent_routing(self):
        """Test time-series agents route to correct models."""
        from core.services.agent_model_router import (
            get_agent_model_router,
            populate_default_configs,
        )

        # Populate configs (needed in test DB)
        populate_default_configs()

        router = get_agent_model_router()
        router.invalidate_cache()  # Clear cache to pick up new configs

        # StockAnalystAgent should use LSTM
        config = router.get_agent_config('StockAnalystAgent')
        assert config['primary_model'] == 'lstm'

        # TrendAnalysisAgent should use Prophet
        config = router.get_agent_config('TrendAnalysisAgent')
        assert config['primary_model'] == 'prophet'


class TestFallbackBehavior(TestCase):
    """Test fallback behavior when full models unavailable."""

    def test_lstm_fallback_uses_moving_average(self):
        """Test LSTM fallback uses moving average extrapolation."""
        model = LSTMTimeSeriesModel()

        # Create data with clear uptrend
        data = list(range(50, 150))  # Steady increase

        result = model.predict_with_fallback(data)

        assert result.success is True
        assert result.metadata.get('fallback_mode') is True
        assert result.metadata.get('method') == 'moving_average_extrapolation'
        # Predictions should continue upward trend
        assert result.predictions[-1] > result.predictions[0]

    def test_prophet_fallback_uses_linear_trend(self):
        """Test Prophet fallback uses linear trend."""
        model = ProphetForecaster()

        # Create data with clear downtrend
        data = list(range(150, 50, -1))  # Steady decrease

        result = model.predict_with_fallback(data)

        assert result.success is True
        assert result.metadata.get('fallback_mode') is True
        assert result.metadata.get('method') == 'linear_trend_with_weekly_seasonality'
        assert result.trend == 'decreasing'
