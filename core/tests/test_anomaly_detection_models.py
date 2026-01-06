"""
Tests for Anomaly Detection Models (Session 679 - Phase 3)
==========================================================

Tests the VAE anomaly detection model including:
- VAEAnomalyDetector functionality
- AnomalyPrediction dataclass
- Integration with model registry
- Fallback mode behavior
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from django.test import TestCase

from ml.anomaly_detection.vae_anomaly_detector import (
    VAEAnomalyDetector,
    AnomalyPrediction,
    get_vae_detector,
)
from core.services.model_registry import (
    ModelRegistry,
    AutoencoderWrapper,
    get_model_registry,
)


class TestAnomalyPrediction(TestCase):
    """Test AnomalyPrediction dataclass."""

    def test_create_prediction(self):
        """Test creating an anomaly prediction."""
        pred = AnomalyPrediction(
            success=True,
            anomaly_scores=[0.1, 0.2, 0.9, 0.15],
            is_anomaly=[False, False, True, False],
            threshold=0.5,
            confidence=0.75,
            anomaly_indices=[2],
            severity='medium',
        )

        assert pred.success is True
        assert len(pred.anomaly_scores) == 4
        assert pred.is_anomaly[2] is True
        assert pred.anomaly_indices == [2]
        assert pred.severity == 'medium'

    def test_to_dict(self):
        """Test converting to dict."""
        pred = AnomalyPrediction(
            success=True,
            anomaly_scores=[0.1, 0.8],
            is_anomaly=[False, True],
            threshold=0.5,
        )

        result = pred.to_dict()

        assert isinstance(result, dict)
        assert result['success'] is True
        assert result['anomaly_scores'] == [0.1, 0.8]
        assert result['is_anomaly'] == [False, True]


class TestVAEAnomalyDetector(TestCase):
    """Test VAEAnomalyDetector class."""

    def test_init(self):
        """Test detector initialization."""
        detector = VAEAnomalyDetector(model_name="test_vae")

        assert detector.model_name == "test_vae"
        assert detector.is_trained is False
        assert detector.config['latent_dim'] == 16

    def test_train_with_normal_data(self):
        """Test training on normal data."""
        detector = VAEAnomalyDetector()

        # Generate normal data (Gaussian clusters)
        np.random.seed(42)
        normal_data = np.random.randn(100, 5)  # 100 samples, 5 features

        result = detector.train(normal_data)

        assert result['success'] is True
        assert detector.is_trained is True
        assert 'threshold' in result
        assert result['samples_trained'] == 100

    def test_train_insufficient_data(self):
        """Test training with insufficient data."""
        detector = VAEAnomalyDetector()

        result = detector.train(np.random.randn(5, 3))  # Only 5 samples

        assert result['success'] is False
        assert 'samples' in result['error'].lower()

    def test_predict_with_fallback_normal(self):
        """Test fallback prediction on normal data."""
        detector = VAEAnomalyDetector()

        # Generate normal data
        np.random.seed(42)
        data = np.random.randn(50, 3)

        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert len(result.anomaly_scores) == 50
        assert result.metadata.get('fallback_mode') is True
        # Most points should be normal
        assert sum(result.is_anomaly) < len(result.is_anomaly) * 0.2

    def test_predict_with_fallback_dict(self):
        """Test fallback prediction with dict input."""
        detector = VAEAnomalyDetector()

        np.random.seed(42)
        data = {'values': np.random.randn(50, 3).tolist()}

        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert len(result.anomaly_scores) == 50

    def test_predict_insufficient_data(self):
        """Test prediction with insufficient data."""
        detector = VAEAnomalyDetector()

        result = detector.predict_with_fallback([1, 2, 3])  # Only 3 points

        assert result.success is False
        assert 'data points' in result.error.lower()

    def test_detect_anomalies(self):
        """Test detecting actual anomalies."""
        detector = VAEAnomalyDetector()

        # Generate normal data with some outliers
        np.random.seed(42)
        normal_data = np.random.randn(80, 3)  # Normal cluster around 0

        # Add clear outliers (far from mean)
        outliers = np.array([
            [10, 10, 10],
            [-10, -10, -10],
            [15, -15, 15],
        ])
        data = np.vstack([normal_data, outliers])

        result = detector.predict_with_fallback(data)

        assert result.success is True
        # Should detect some anomalies (the outliers we added)
        assert len(result.anomaly_indices) > 0
        # Outliers should have higher scores than normal points
        outlier_scores = [result.anomaly_scores[i] for i in range(80, 83)]
        normal_scores = [result.anomaly_scores[i] for i in range(10)]
        assert np.mean(outlier_scores) > np.mean(normal_scores)

    def test_severity_calculation(self):
        """Test severity classification."""
        detector = VAEAnomalyDetector()

        # Low severity (few mild anomalies)
        severity = detector._calculate_severity(
            np.array([0.1, 0.2, 0.3, 0.6, 0.1]),
            threshold=0.5
        )
        assert severity in ['low', 'medium']

        # Critical severity (extreme outliers)
        severity = detector._calculate_severity(
            np.array([0.1, 0.1, 5.0, 6.0, 7.0]),
            threshold=0.5
        )
        assert severity in ['high', 'critical']

    def test_get_vae_detector_singleton(self):
        """Test singleton pattern."""
        detector1 = get_vae_detector()
        detector2 = get_vae_detector()

        assert detector1 is detector2


class TestVAEFallbackMethods(TestCase):
    """Test different fallback methods."""

    def test_mahalanobis_fallback(self):
        """Test Mahalanobis distance fallback."""
        detector = VAEAnomalyDetector(config={'fallback_method': 'mahalanobis'})

        np.random.seed(42)
        data = np.random.randn(50, 3)

        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert 'mahalanobis' in result.metadata.get('method', '')

    def test_iqr_fallback(self):
        """Test IQR-based fallback."""
        detector = VAEAnomalyDetector(config={'fallback_method': 'iqr'})

        np.random.seed(42)
        data = np.random.randn(50, 3)

        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert 'iqr' in result.metadata.get('method', '')

    def test_zscore_fallback(self):
        """Test Z-score fallback."""
        detector = VAEAnomalyDetector(config={'fallback_method': 'zscore'})

        np.random.seed(42)
        data = np.random.randn(50, 3)

        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert 'zscore' in result.metadata.get('method', '')


class TestAutoencoderWrapper(TestCase):
    """Test AutoencoderWrapper integration."""

    def test_wrapper_init(self):
        """Test wrapper initialization."""
        wrapper = AutoencoderWrapper()

        assert wrapper.model_name == 'autoencoder'
        assert wrapper.version == 'v1.0'

    def test_wrapper_is_available(self):
        """Test wrapper availability."""
        wrapper = AutoencoderWrapper()

        # Should be available (fallback mode works)
        assert wrapper.is_available() is True

    def test_wrapper_predict(self):
        """Test wrapper prediction."""
        wrapper = AutoencoderWrapper()

        np.random.seed(42)
        data = {'values': np.random.randn(50, 3).tolist()}
        result = wrapper.predict(data)

        assert result.success is True
        assert result.model_name == 'autoencoder'
        assert 'is_anomaly' in result.explanation
        assert 'severity' in result.explanation
        assert 'num_anomalies' in result.explanation

    def test_wrapper_from_registry(self):
        """Test getting wrapper from registry."""
        registry = ModelRegistry()
        wrapper = registry.get_model('autoencoder')

        assert wrapper is not None
        assert isinstance(wrapper, AutoencoderWrapper)
        assert wrapper.is_available() is True


class TestRegistryIntegration(TestCase):
    """Test integration with model registry."""

    def test_autoencoder_in_available_models(self):
        """Test autoencoder appears in available models."""
        registry = get_model_registry()
        available = registry.list_available_models()

        assert 'autoencoder' in available

    def test_anomaly_agent_routing(self):
        """Test anomaly agents route to correct models."""
        from core.services.agent_model_router import (
            get_agent_model_router,
            populate_default_configs,
        )

        # Populate configs (needed in test DB)
        populate_default_configs()

        router = get_agent_model_router()
        router.invalidate_cache()  # Clear cache to pick up new configs

        # ExploitDetectorAgent should use autoencoder
        config = router.get_agent_config('ExploitDetectorAgent')
        assert config['primary_model'] == 'autoencoder'

        # TransactionMonitorAgent should use autoencoder
        config = router.get_agent_config('TransactionMonitorAgent')
        assert config['primary_model'] == 'autoencoder'

        # MarketAnomalyDetectorAgent should use autoencoder
        config = router.get_agent_config('MarketAnomalyDetectorAgent')
        assert config['primary_model'] == 'autoencoder'


class TestAnomalyScoring(TestCase):
    """Test anomaly scoring accuracy."""

    def test_normal_data_low_scores(self):
        """Test that normal data gets low anomaly scores."""
        detector = VAEAnomalyDetector()

        # Generate tight normal cluster
        np.random.seed(42)
        data = np.random.randn(100, 5) * 0.1  # Low variance

        result = detector.predict_with_fallback(data)

        assert result.success is True
        # Average score should be low for normal data
        avg_score = sum(result.anomaly_scores) / len(result.anomaly_scores)
        assert avg_score < 0.5

    def test_outliers_high_scores(self):
        """Test that outliers get high anomaly scores."""
        detector = VAEAnomalyDetector()

        # Train on normal data
        np.random.seed(42)
        normal_data = np.random.randn(100, 3)
        detector.train(normal_data)

        # Test with extreme outliers
        outliers = np.array([
            [20, 20, 20],
            [-20, -20, -20],
        ])

        result = detector.predict(outliers)

        assert result.success is True
        # Both outliers should be flagged
        assert all(result.is_anomaly)

    def test_reconstruction_error_correlation(self):
        """Test that anomaly scores correlate with reconstruction error."""
        detector = VAEAnomalyDetector()

        np.random.seed(42)
        data = np.random.randn(50, 3)

        result = detector.predict_with_fallback(data)

        assert result.success is True
        # Higher reconstruction error should mean higher anomaly score
        if len(result.reconstruction_error) > 1:
            # Check correlation direction (not exact, but positive relationship)
            high_error_idx = np.argmax(result.reconstruction_error)
            low_error_idx = np.argmin(result.reconstruction_error)
            assert result.anomaly_scores[high_error_idx] >= result.anomaly_scores[low_error_idx]


class TestEdgeCases(TestCase):
    """Test edge cases and error handling."""

    def test_empty_data(self):
        """Test with empty data."""
        detector = VAEAnomalyDetector()

        result = detector.predict_with_fallback([])

        assert result.success is False
        assert 'valid data' in result.error.lower() or 'no' in result.error.lower()

    def test_single_feature(self):
        """Test with single feature data."""
        detector = VAEAnomalyDetector()

        np.random.seed(42)
        data = np.random.randn(50).tolist()  # 1D data

        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert len(result.anomaly_scores) == 50

    def test_high_dimensional_data(self):
        """Test with high dimensional data."""
        detector = VAEAnomalyDetector()

        np.random.seed(42)
        data = np.random.randn(50, 100)  # 100 features

        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert len(result.anomaly_scores) == 50

    def test_predict_without_training(self):
        """Test prediction without explicit training."""
        detector = VAEAnomalyDetector()

        np.random.seed(42)
        data = np.random.randn(50, 3)

        # Should auto-train and then predict
        result = detector.predict_with_fallback(data)

        assert result.success is True
        assert detector.is_trained is True

    def test_get_model_info(self):
        """Test model info retrieval."""
        detector = VAEAnomalyDetector(model_name="test_detector")

        info = detector.get_model_info()

        assert info['model_name'] == 'test_detector'
        assert 'is_trained' in info
        assert 'config' in info
        assert 'tensorflow_available' in info
