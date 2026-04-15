"""
Model Registry - Unified Interface for All ML Models
=====================================================

Session 677: Phase 1 of Agent-Model Routing

This module provides:
1. BaseModelWrapper - Abstract interface for all ML models
2. Individual wrappers for each available model type
3. ModelRegistry - Central registry for model discovery and instantiation

Usage:
    from core.services.model_registry import get_model_registry

    registry = get_model_registry()
    model = registry.get_model('lightgbm')
    prediction = model.predict(features)
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ModelPrediction:
    """Standardized prediction result from any model."""
    success: bool
    score: float = 0.0
    confidence: float = 0.0
    predictions: List[float] = field(default_factory=list)
    explanation: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    model_name: str = ""
    model_version: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'score': self.score,
            'confidence': self.confidence,
            'predictions': self.predictions,
            'explanation': self.explanation,
            'latency_ms': self.latency_ms,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'error': self.error,
        }


class BaseModelWrapper(ABC):
    """
    Abstract base class for all ML model wrappers.

    All model wrappers must implement:
    - predict(): Make predictions on input data
    - is_available(): Check if model is ready for predictions
    - get_model_info(): Return model metadata
    """

    def __init__(self, model_name: str, version: str = "v1.0"):
        self.model_name = model_name
        self.version = version
        self._model = None
        self._is_loaded = False

    @abstractmethod
    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        """Make predictions on input data."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if model is loaded and ready for predictions."""
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata."""
        return {
            'name': self.model_name,
            'version': self.version,
            'is_loaded': self._is_loaded,
            'type': self.__class__.__name__,
        }

    def _timed_predict(self, predict_fn, *args, **kwargs) -> ModelPrediction:
        """Helper to time prediction calls."""
        start = time.time()
        try:
            result = predict_fn(*args, **kwargs)
            latency = (time.time() - start) * 1000
            result.latency_ms = latency
            result.model_name = self.model_name
            result.model_version = self.version
            return result
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"{self.model_name} prediction error: {e}")
            return ModelPrediction(
                success=False,
                error=str(e),
                latency_ms=latency,
                model_name=self.model_name,
                model_version=self.version,
            )


# =============================================================================
# EXISTING MODEL WRAPPERS (9 models currently available)
# =============================================================================

class LightGBMWrapper(BaseModelWrapper):
    """Wrapper for LightGBM gradient boosting model."""

    def __init__(self):
        super().__init__("lightgbm", "v1.0")
        self._engine = None

    def _get_engine(self):
        """Lazy load the ML scoring engine."""
        if self._engine is None:
            try:
                from core.services.ml_scoring_engine import get_ml_scoring_engine
                self._engine = get_ml_scoring_engine()
                self._is_loaded = self._engine.is_trained
            except Exception as e:
                logger.warning(f"Failed to load LightGBM engine: {e}")
        return self._engine

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            engine = self._get_engine()
            if engine is None:
                return ModelPrediction(success=False, error="Engine not available")

            # If data is SpiderData, use score_opportunity
            if hasattr(data, 'spider_name'):
                result = engine.score_opportunity(data)
                return ModelPrediction(
                    success=result.success,
                    score=result.hybrid_score,
                    confidence=result.confidence,
                    explanation={
                        'ml_score': result.ml_score,
                        'rule_score': result.rule_score,
                        'shap': result.shap_explanation.to_dict() if result.shap_explanation else None,
                    },
                )

            # If data is feature array, predict directly
            if isinstance(data, np.ndarray):
                if engine.model is not None:
                    pred = engine.model.predict(data)
                    return ModelPrediction(
                        success=True,
                        score=float(pred[0]) if len(pred) > 0 else 0.0,
                        predictions=pred.tolist(),
                    )

            return ModelPrediction(success=False, error="Unsupported data type")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        engine = self._get_engine()
        return engine is not None and engine.is_trained


class XGBoostWrapper(BaseModelWrapper):
    """Wrapper for XGBoost gradient boosting model."""

    def __init__(self):
        super().__init__("xgboost", "v1.0")
        self._model = None

    def _load_model(self):
        """Load XGBoost model."""
        if self._model is None:
            try:
                from core.services.ml_scoring_engine import MLScoringEngine, MODEL_TYPE_XGBOOST
                engine = MLScoringEngine(model_type=MODEL_TYPE_XGBOOST)
                if engine.is_trained:
                    self._model = engine.model
                    self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load XGBoost: {e}")

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            self._load_model()
            if self._model is None:
                return ModelPrediction(success=False, error="XGBoost model not loaded")

            if isinstance(data, np.ndarray):
                pred = self._model.predict(data)
                return ModelPrediction(
                    success=True,
                    score=float(pred[0]) if len(pred) > 0 else 0.0,
                    predictions=pred.tolist(),
                )

            return ModelPrediction(success=False, error="Unsupported data type")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        self._load_model()
        return self._model is not None


class RandomForestWrapper(BaseModelWrapper):
    """Wrapper for Random Forest from ml_engine."""

    def __init__(self):
        super().__init__("random_forest", "v1.0")
        self._ml_engine = None

    def _get_engine(self):
        if self._ml_engine is None:
            # Session 1083 round 41: SKIP_NLP_MODELS=1 on macOS Celery
            # workers skips ALL heavy ML loads, not just DistilBERT —
            # instantiating MLEngine() triggers joblib.load of
            # sports_crypto_lstm / options_betting_nn / user_behavior_rf
            # which race with ml_scoring_engine's lightgbm joblib load
            # and hit Abseil RAW: Lock blocking. The env var is
            # historically misnamed — treat it as SKIP_ALL_ML_MODELS
            # for macOS worker safety.
            import os
            if os.environ.get('SKIP_NLP_MODELS') == '1':
                logger.debug(
                    "[model_registry] SKIP_NLP_MODELS=1 — RandomForestWrapper "
                    "reports unavailable to avoid MLEngine mutex deadlock"
                )
                return None
            try:
                from ml.core.ml_engine import MLEngine
                self._ml_engine = MLEngine()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load MLEngine: {e}")
        return self._ml_engine

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            engine = self._get_engine()
            if engine is None:
                return ModelPrediction(success=False, error="MLEngine not available")

            model = engine.models.get('user_behavior_rf')
            if model is None:
                return ModelPrediction(success=False, error="Random Forest model not found")

            if isinstance(data, np.ndarray):
                try:
                    pred = model.predict(data)
                    return ModelPrediction(
                        success=True,
                        predictions=pred.tolist(),
                        score=float(pred[0]) if len(pred) > 0 else 0.0,
                    )
                except Exception as e:
                    return ModelPrediction(success=False, error=f"Prediction failed: {e}")

            return ModelPrediction(success=False, error="Unsupported data type")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        engine = self._get_engine()
        return engine is not None and 'user_behavior_rf' in (engine.models or {})


class IsolationForestWrapper(BaseModelWrapper):
    """Wrapper for Isolation Forest anomaly detection."""

    def __init__(self):
        super().__init__("isolation_forest", "v1.0")
        self._detector = None

    def _get_detector(self):
        if self._detector is None:
            try:
                from core.services.ml_algorithms import FraudDetector
                self._detector = FraudDetector(project_path="")
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load FraudDetector: {e}")
        return self._detector

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            detector = self._get_detector()
            if detector is None:
                return ModelPrediction(success=False, error="Detector not available")

            # If data is a transaction dict, use fraud detection
            if isinstance(data, dict):
                # Ensure model is trained
                if detector.fraud_model is None:
                    return ModelPrediction(
                        success=False,
                        error="Fraud model not trained. Call train_fraud_detector first."
                    )
                result = detector.detect_fraud(data)
                return ModelPrediction(
                    success=True,
                    score=1.0 if result['is_fraudulent'] else 0.0,
                    confidence=abs(result['anomaly_score']),
                    explanation={
                        'is_anomaly': result['is_fraudulent'],
                        'risk_level': result['risk_level'],
                        'risk_factors': result['risk_factors'],
                    },
                )

            # If data is array, use raw prediction
            if isinstance(data, np.ndarray) and detector.fraud_model is not None:
                scaled = detector.scaler.transform(data) if hasattr(detector, 'scaler') else data
                pred = detector.fraud_model.predict(scaled)
                scores = detector.fraud_model.score_samples(scaled)
                return ModelPrediction(
                    success=True,
                    predictions=pred.tolist(),
                    score=float(scores[0]) if len(scores) > 0 else 0.0,
                )

            return ModelPrediction(success=False, error="Unsupported data type or model not trained")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        detector = self._get_detector()
        return detector is not None


class KMeansWrapper(BaseModelWrapper):
    """Wrapper for K-Means clustering."""

    def __init__(self):
        super().__init__("kmeans", "v1.0")
        self._segmenter = None

    def _get_segmenter(self):
        if self._segmenter is None:
            try:
                from core.services.ml_algorithms import CustomerSegmentation
                self._segmenter = CustomerSegmentation(project_path="")
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load CustomerSegmentation: {e}")
        return self._segmenter

    def predict(self, data: Any, n_clusters: int = 5, **kwargs) -> ModelPrediction:
        def _predict():
            segmenter = self._get_segmenter()
            if segmenter is None:
                return ModelPrediction(success=False, error="Segmenter not available")

            # If data is DataFrame, perform segmentation
            try:
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    result = segmenter.segment_customers(data, n_segments=n_clusters)
                    return ModelPrediction(
                        success=True,
                        score=result.get('silhouette_score', 0.0),
                        explanation={
                            'n_segments': result['n_segments'],
                            'profiles': result['segment_profiles'],
                        },
                    )
            except Exception as e:
                return ModelPrediction(success=False, error=f"Segmentation failed: {e}")

            return ModelPrediction(success=False, error="Unsupported data type")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        return self._get_segmenter() is not None


class MLPWrapper(BaseModelWrapper):
    """Wrapper for MLP Neural Network."""

    def __init__(self):
        super().__init__("mlp", "v1.0")
        self._ml_engine = None

    def _get_engine(self):
        if self._ml_engine is None:
            try:
                from ml.core.ml_engine import MLEngine
                self._ml_engine = MLEngine()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load MLEngine: {e}")
        return self._ml_engine

    def predict(self, data: Any, model_key: str = 'sports_crypto_lstm', **kwargs) -> ModelPrediction:
        def _predict():
            engine = self._get_engine()
            if engine is None:
                return ModelPrediction(success=False, error="MLEngine not available")

            model = engine.models.get(model_key)
            if model is None:
                return ModelPrediction(success=False, error=f"MLP model '{model_key}' not found")

            if isinstance(data, np.ndarray):
                try:
                    pred = model.predict(data)
                    return ModelPrediction(
                        success=True,
                        predictions=pred.tolist(),
                        score=float(pred[0]) if len(pred) > 0 else 0.0,
                    )
                except Exception as e:
                    return ModelPrediction(success=False, error=f"Prediction failed: {e}")

            return ModelPrediction(success=False, error="Unsupported data type")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        engine = self._get_engine()
        return engine is not None


class DistilBERTWrapper(BaseModelWrapper):
    """Wrapper for DistilBERT sentiment analysis."""

    def __init__(self):
        super().__init__("distilbert", "v1.0")
        self._analyzer = None

    def _get_analyzer(self):
        if self._analyzer is None:
            # Session 1083 round 41: SKIP_NLP_MODELS=1 short-circuits
            # before MLEngine() instantiation (which loads sports
            # LSTM/NN and races with lightgbm on macOS Abseil mutex).
            import os
            if os.environ.get('SKIP_NLP_MODELS') == '1':
                logger.debug(
                    "[model_registry] SKIP_NLP_MODELS=1 — DistilBERTWrapper "
                    "reports unavailable to avoid MLEngine mutex deadlock"
                )
                return None
            try:
                from ml.core.ml_engine import MLEngine
                engine = MLEngine()
                self._analyzer = engine.sentiment_analyzer
                self._is_loaded = self._analyzer is not None
            except Exception as e:
                logger.warning(f"Failed to load sentiment analyzer: {e}")
        return self._analyzer

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            analyzer = self._get_analyzer()
            if analyzer is None:
                return ModelPrediction(success=False, error="Sentiment analyzer not available")

            # If data is string, analyze sentiment
            if isinstance(data, str):
                result = analyzer(data)
                if result and len(result) > 0:
                    sentiment = result[0]
                    score = sentiment['score'] if sentiment['label'] == 'POSITIVE' else 1 - sentiment['score']
                    return ModelPrediction(
                        success=True,
                        score=score,
                        confidence=sentiment['score'],
                        explanation={
                            'label': sentiment['label'],
                            'raw_score': sentiment['score'],
                        },
                    )

            # If data is list of strings, batch analyze
            if isinstance(data, list) and all(isinstance(x, str) for x in data):
                results = analyzer(data)
                scores = []
                for r in results:
                    s = r['score'] if r['label'] == 'POSITIVE' else 1 - r['score']
                    scores.append(s)
                return ModelPrediction(
                    success=True,
                    predictions=scores,
                    score=np.mean(scores) if scores else 0.0,
                )

            return ModelPrediction(success=False, error="Unsupported data type (expected string)")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        return self._get_analyzer() is not None


class EmbeddingsWrapper(BaseModelWrapper):
    """Wrapper for OpenAI Embeddings semantic similarity."""

    def __init__(self):
        super().__init__("embeddings", "v1.0")
        self._service = None

    def _get_service(self):
        if self._service is None:
            try:
                from core.services.memory_embedding_service import MemoryEmbeddingService
                self._service = MemoryEmbeddingService()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load MemoryEmbeddingService: {e}")
        return self._service

    def predict(self, data: Any, query: str = None, **kwargs) -> ModelPrediction:
        def _predict():
            service = self._get_service()
            if service is None:
                return ModelPrediction(success=False, error="Embedding service not available")

            # If data is string, generate embedding
            if isinstance(data, str):
                try:
                    embedding = service.generate_embedding(data)
                    return ModelPrediction(
                        success=True,
                        predictions=embedding if isinstance(embedding, list) else embedding.tolist(),
                        score=1.0,  # Embedding generation success
                    )
                except Exception as e:
                    return ModelPrediction(success=False, error=f"Embedding failed: {e}")

            # If data is embedding array and query provided, compute similarity
            if isinstance(data, (list, np.ndarray)) and query:
                try:
                    query_embedding = service.generate_embedding(query)
                    similarity = self._cosine_similarity(query_embedding, data)
                    return ModelPrediction(
                        success=True,
                        score=similarity,
                        confidence=similarity,
                    )
                except Exception as e:
                    return ModelPrediction(success=False, error=f"Similarity failed: {e}")

            return ModelPrediction(success=False, error="Unsupported data type")

        return self._timed_predict(_predict)

    def _cosine_similarity(self, a, b):
        """Compute cosine similarity between two vectors."""
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def is_available(self) -> bool:
        return self._get_service() is not None


class CosineSimilarityWrapper(BaseModelWrapper):
    """Wrapper for cosine similarity recommendations."""

    def __init__(self):
        super().__init__("cosine_similarity", "v1.0")
        self._is_loaded = True  # No external dependencies

    def predict(self, data: Any, target: Any = None, **kwargs) -> ModelPrediction:
        def _predict():
            if target is None:
                return ModelPrediction(success=False, error="Target required for similarity")

            try:
                from sklearn.metrics.pairwise import cosine_similarity

                data_arr = np.array(data).reshape(1, -1) if isinstance(data, list) else data
                target_arr = np.array(target).reshape(1, -1) if isinstance(target, list) else target

                if data_arr.ndim == 1:
                    data_arr = data_arr.reshape(1, -1)
                if target_arr.ndim == 1:
                    target_arr = target_arr.reshape(1, -1)

                similarity = cosine_similarity(data_arr, target_arr)
                score = float(similarity[0][0])

                return ModelPrediction(
                    success=True,
                    score=score,
                    confidence=score,
                )
            except Exception as e:
                return ModelPrediction(success=False, error=f"Similarity failed: {e}")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        return True


class RulesWrapper(BaseModelWrapper):
    """Wrapper for rule-based heuristic scoring."""

    def __init__(self):
        super().__init__("rules", "v1.0")
        self._is_loaded = True

    def predict(self, data: Any, rules: Dict[str, Any] = None, **kwargs) -> ModelPrediction:
        def _predict():
            if rules is None:
                # Default scoring rules
                rules_config = {
                    'keyword_weights': {
                        'ai': 15, 'ml': 15, 'trending': 10, 'urgent': 10,
                        'opportunity': 10, 'profit': 10, 'revenue': 10,
                    },
                    'base_score': 50,
                }
            else:
                rules_config = rules

            # If data is SpiderData
            if hasattr(data, 'raw_data'):
                raw = data.raw_data or {}
                title = str(raw.get('title', '')).lower()

                score = rules_config.get('base_score', 50)
                matched = []

                for keyword, weight in rules_config.get('keyword_weights', {}).items():
                    if keyword in title:
                        score += weight
                        matched.append(keyword)

                return ModelPrediction(
                    success=True,
                    score=min(100, max(0, score)),
                    explanation={'matched_keywords': matched, 'rules': rules_config},
                )

            # If data is dict with 'text' key
            if isinstance(data, dict) and 'text' in data:
                text = data['text'].lower()
                score = rules_config.get('base_score', 50)
                matched = []

                for keyword, weight in rules_config.get('keyword_weights', {}).items():
                    if keyword in text:
                        score += weight
                        matched.append(keyword)

                return ModelPrediction(
                    success=True,
                    score=min(100, max(0, score)),
                    explanation={'matched_keywords': matched},
                )

            return ModelPrediction(success=False, error="Unsupported data type")

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        return True


# =============================================================================
# FUTURE MODEL WRAPPERS (Placeholders for Phase 2-5)
# =============================================================================

class LSTMWrapper(BaseModelWrapper):
    """Wrapper for LSTM time series model (Session 678 - Phase 2)."""

    def __init__(self):
        super().__init__("lstm", "v1.0")
        self._lstm_model = None

    def _get_model(self):
        """Lazy load the LSTM model."""
        if self._lstm_model is None:
            try:
                from ml.time_series.lstm_time_series import get_lstm_model
                self._lstm_model = get_lstm_model()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load LSTM model: {e}")
        return self._lstm_model

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            model = self._get_model()
            if model is None:
                return ModelPrediction(success=False, error="LSTM model not available")

            # Use fallback method which works with or without TensorFlow
            result = model.predict_with_fallback(data)

            if not result.success:
                return ModelPrediction(
                    success=False,
                    error=result.error,
                    model_name=self.model_name,
                )

            return ModelPrediction(
                success=True,
                score=result.predictions[-1] if result.predictions else 0.0,
                confidence=result.confidence,
                predictions=result.predictions,
                explanation={
                    'direction': result.direction,
                    'trend_strength': result.trend_strength,
                    'volatility': result.volatility,
                    'support_level': result.support_level,
                    'resistance_level': result.resistance_level,
                    'metadata': result.metadata,
                },
            )

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        model = self._get_model()
        return model is not None


class ProphetWrapper(BaseModelWrapper):
    """Wrapper for Prophet seasonal forecasting (Session 678 - Phase 2)."""

    def __init__(self):
        super().__init__("prophet", "v1.0")
        self._prophet_model = None

    def _get_model(self):
        """Lazy load the Prophet model."""
        if self._prophet_model is None:
            try:
                from ml.time_series.prophet_forecaster import get_prophet_model
                self._prophet_model = get_prophet_model()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load Prophet model: {e}")
        return self._prophet_model

    def predict(self, data: Any, periods: int = None, **kwargs) -> ModelPrediction:
        def _predict():
            model = self._get_model()
            if model is None:
                return ModelPrediction(success=False, error="Prophet model not available")

            # Use fallback method which works with or without Prophet
            result = model.predict_with_fallback(data, periods=periods)

            if not result.success:
                return ModelPrediction(
                    success=False,
                    error=result.error,
                    model_name=self.model_name,
                )

            return ModelPrediction(
                success=True,
                score=result.predictions[-1] if result.predictions else 0.0,
                confidence=result.confidence,
                predictions=result.predictions,
                explanation={
                    'trend': result.trend,
                    'trend_slope': result.trend_slope,
                    'seasonality': result.seasonality,
                    'changepoints': result.changepoints,
                    'lower_bounds': result.lower_bounds,
                    'upper_bounds': result.upper_bounds,
                    'dates': result.dates,
                    'metadata': result.metadata,
                },
            )

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        model = self._get_model()
        return model is not None


class GNNWrapper(BaseModelWrapper):
    """Wrapper for Graph Neural Network reasoning (Session 681 - Phase 5)."""

    def __init__(self):
        super().__init__("gnn", "v1.0")
        self._gnn_reasoner = None

    def _get_reasoner(self):
        """Lazy load the GNN reasoner."""
        if self._gnn_reasoner is None:
            try:
                from ml.graph_neural_network.gnn_graph_reasoner import get_gnn_reasoner
                self._gnn_reasoner = get_gnn_reasoner()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load GNN reasoner: {e}")
        return self._gnn_reasoner

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            reasoner = self._get_reasoner()
            if reasoner is None:
                return ModelPrediction(success=False, error="GNN reasoner not available")

            # Use fallback method which works with or without PyTorch/PyG
            result = reasoner.predict_with_fallback(data)

            if not result.success:
                return ModelPrediction(
                    success=False,
                    error=result.error,
                    model_name=self.model_name,
                )

            # Calculate overall score from centrality
            if result.centrality_scores:
                overall_score = max(result.centrality_scores.values())
            else:
                overall_score = 0.5

            return ModelPrediction(
                success=True,
                score=float(overall_score),
                confidence=result.confidence,
                predictions=list(result.centrality_scores.values()) if result.centrality_scores else [],
                explanation={
                    'node_scores': result.node_scores,
                    'centrality_scores': result.centrality_scores,
                    'communities': result.communities,
                    'link_predictions': result.link_predictions,
                    'graph_embedding': result.graph_embedding,
                    'num_nodes': result.metadata.get('num_nodes', 0),
                    'num_edges': result.metadata.get('num_edges', 0),
                    'method': result.metadata.get('method', 'unknown'),
                    'metadata': result.metadata,
                },
            )

        return self._timed_predict(_predict)

    def analyze_graph(self, graph: Any) -> Dict[str, Any]:
        """Full graph analysis returning detailed results."""
        reasoner = self._get_reasoner()
        if reasoner is None:
            return {'success': False, 'error': 'Reasoner not available'}
        result = reasoner.analyze_graph(graph)
        return result.to_dict()

    def is_available(self) -> bool:
        reasoner = self._get_reasoner()
        return reasoner is not None


class AutoencoderWrapper(BaseModelWrapper):
    """Wrapper for VAE Autoencoder anomaly detection (Session 679 - Phase 3)."""

    def __init__(self):
        super().__init__("autoencoder", "v1.0")
        self._vae_detector = None

    def _get_detector(self):
        """Lazy load the VAE detector."""
        if self._vae_detector is None:
            try:
                from ml.anomaly_detection.vae_anomaly_detector import get_vae_detector
                self._vae_detector = get_vae_detector()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load VAE detector: {e}")
        return self._vae_detector

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        def _predict():
            detector = self._get_detector()
            if detector is None:
                return ModelPrediction(success=False, error="VAE detector not available")

            # Use fallback method which works with or without TensorFlow
            result = detector.predict_with_fallback(data)

            if not result.success:
                return ModelPrediction(
                    success=False,
                    error=result.error,
                    model_name=self.model_name,
                )

            # Calculate overall anomaly score (mean of all scores)
            overall_score = sum(result.anomaly_scores) / len(result.anomaly_scores) if result.anomaly_scores else 0.0

            return ModelPrediction(
                success=True,
                score=overall_score,
                confidence=result.confidence,
                predictions=result.anomaly_scores,
                explanation={
                    'is_anomaly': result.is_anomaly,
                    'anomaly_indices': result.anomaly_indices,
                    'reconstruction_error': result.reconstruction_error,
                    'threshold': result.threshold,
                    'severity': result.severity,
                    'num_anomalies': len(result.anomaly_indices),
                    'anomaly_rate': result.metadata.get('anomaly_rate', 0.0),
                    'method': result.metadata.get('method', 'unknown'),
                    'metadata': result.metadata,
                },
            )

        return self._timed_predict(_predict)

    def is_available(self) -> bool:
        detector = self._get_detector()
        return detector is not None


class RLWrapper(BaseModelWrapper):
    """Wrapper for Reinforcement Learning decision optimizer (Session 680 - Phase 4)."""

    def __init__(self):
        super().__init__("rl", "v1.0")
        self._rl_optimizer = None

    def _get_optimizer(self):
        """Lazy load the RL optimizer."""
        if self._rl_optimizer is None:
            try:
                from ml.reinforcement_learning.rl_decision_optimizer import get_rl_optimizer
                self._rl_optimizer = get_rl_optimizer()
                self._is_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load RL optimizer: {e}")
        return self._rl_optimizer

    def predict(self, data: Any, actions: List[str] = None, **kwargs) -> ModelPrediction:
        def _predict():
            optimizer = self._get_optimizer()
            if optimizer is None:
                return ModelPrediction(success=False, error="RL optimizer not available")

            # Use fallback method which works with or without PyTorch
            result = optimizer.predict_with_fallback(data, actions=actions)

            if not result.success:
                return ModelPrediction(
                    success=False,
                    error=result.error,
                    model_name=self.model_name,
                )

            # Map action to score (normalized)
            action_idx = result.metadata.get('action_index', 0)
            max_value = max(result.action_values) if result.action_values else 1.0
            score = result.action_values[action_idx] / (abs(max_value) + 1e-8) if max_value else 0.5

            return ModelPrediction(
                success=True,
                score=float(score),
                confidence=result.confidence,
                predictions=result.action_values,
                explanation={
                    'recommended_action': result.recommended_action,
                    'action_values': result.action_values,
                    'action_probabilities': result.action_probabilities,
                    'exploration_bonus': result.exploration_bonus,
                    'expected_reward': result.expected_reward,
                    'method': result.metadata.get('method', 'unknown'),
                    'metadata': result.metadata,
                },
            )

        return self._timed_predict(_predict)

    def update(self, state: Any, action: Any, reward: float, next_state: Any = None, done: bool = False) -> Dict[str, Any]:
        """Update RL model with observed reward."""
        optimizer = self._get_optimizer()
        if optimizer is None:
            return {'success': False, 'error': 'Optimizer not available'}
        return optimizer.update(state, action, reward, next_state, done)

    def is_available(self) -> bool:
        optimizer = self._get_optimizer()
        return optimizer is not None


class DBSCANWrapper(BaseModelWrapper):
    """Wrapper for DBSCAN clustering (Phase 3)."""

    def __init__(self):
        super().__init__("dbscan", "v0.0")

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        return ModelPrediction(
            success=False,
            error="DBSCAN not yet implemented (Phase 3)",
            model_name=self.model_name,
        )

    def is_available(self) -> bool:
        return False


class TransformerWrapper(BaseModelWrapper):
    """Wrapper for small Transformer model (Phase 2)."""

    def __init__(self):
        super().__init__("transformer", "v0.0")

    def predict(self, data: Any, **kwargs) -> ModelPrediction:
        return ModelPrediction(
            success=False,
            error="Transformer not yet implemented (Phase 2)",
            model_name=self.model_name,
        )

    def is_available(self) -> bool:
        return False


# =============================================================================
# MODEL REGISTRY
# =============================================================================

class ModelRegistry:
    """
    Central registry for all ML models.

    Provides:
    - Model discovery and instantiation
    - Lazy loading of models
    - Model availability checking
    """

    # Map model names to wrapper classes
    MODEL_CLASSES = {
        # Currently available (9)
        'lightgbm': LightGBMWrapper,
        'xgboost': XGBoostWrapper,
        'random_forest': RandomForestWrapper,
        'isolation_forest': IsolationForestWrapper,
        'kmeans': KMeansWrapper,
        'mlp': MLPWrapper,
        'distilbert': DistilBERTWrapper,
        'embeddings': EmbeddingsWrapper,
        'cosine_similarity': CosineSimilarityWrapper,
        'rules': RulesWrapper,
        # Future (Phase 2-5)
        'lstm': LSTMWrapper,
        'prophet': ProphetWrapper,
        'gnn': GNNWrapper,
        'autoencoder': AutoencoderWrapper,
        'rl': RLWrapper,
        'dbscan': DBSCANWrapper,
        'transformer': TransformerWrapper,
    }

    def __init__(self):
        self._instances: Dict[str, BaseModelWrapper] = {}
        # Session 1083 round 41: lock prevents two threads from
        # concurrently instantiating the same wrapper class. Without
        # this, RandomForestWrapper/DistilBERTWrapper could both race
        # into MLEngine() and hit the Abseil mutex deadlock.
        import threading as _mr_threading
        self._instances_lock = _mr_threading.Lock()

    def get_model(self, model_name: str) -> Optional[BaseModelWrapper]:
        """
        Get a model wrapper instance by name.

        Uses lazy loading - models are instantiated on first request.
        Thread-safe per round 41.
        """
        if model_name not in self.MODEL_CLASSES:
            logger.warning(f"Unknown model: {model_name}")
            return None

        if model_name not in self._instances:
            with self._instances_lock:
                # Double-checked locking — re-read under lock
                if model_name not in self._instances:
                    wrapper_class = self.MODEL_CLASSES[model_name]
                    self._instances[model_name] = wrapper_class()

        return self._instances[model_name]

    def list_models(self) -> List[str]:
        """List all registered model names."""
        return list(self.MODEL_CLASSES.keys())

    def list_available_models(self) -> List[str]:
        """List models that are currently available for predictions."""
        available = []
        for name in self.MODEL_CLASSES:
            model = self.get_model(name)
            if model and model.is_available():
                available.append(name)
        return available

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a model."""
        model = self.get_model(model_name)
        if model:
            info = model.get_model_info()
            info['is_available'] = model.is_available()
            return info
        return None

    def get_all_model_info(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all models."""
        return {name: self.get_model_info(name) for name in self.MODEL_CLASSES}


# Singleton instance
_registry = None
# Session 1083 round 41: lock for thread-safe singleton init
import threading as _registry_threading
_registry_lock = _registry_threading.Lock()


def get_model_registry() -> ModelRegistry:
    """Get the singleton model registry instance. Thread-safe per round 41."""
    global _registry
    if _registry is None:
        with _registry_lock:
            # Double-checked locking — re-read under lock
            if _registry is None:
                _registry = ModelRegistry()
    return _registry
