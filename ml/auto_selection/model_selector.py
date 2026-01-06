"""
Model Auto-Selection - Automatic ML Model Selection Based on Task Characteristics
==================================================================================

Session 682: Phase 6 of Agent-Model Routing Architecture

This module provides intelligent model selection by:
1. Analyzing input data to detect task characteristics
2. Scoring each available model for the detected task type
3. Selecting optimal model(s) based on scores and constraints
4. Tracking selection history for continuous improvement

Usage:
    from ml.auto_selection import get_model_selector, TaskType

    selector = get_model_selector()
    result = selector.select_models(data)
    # result.recommended_models, result.task_type, result.confidence
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Detected task types for model selection."""
    TIME_SERIES = "time_series"
    GRAPH = "graph"
    TEXT = "text"
    ANOMALY = "anomaly"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    DECISION = "decision"
    UNKNOWN = "unknown"


class DataCharacteristic(Enum):
    """Characteristics detected in input data."""
    SEQUENTIAL = "sequential"
    TEMPORAL = "temporal"
    GRAPH_STRUCTURE = "graph_structure"
    HIGH_DIMENSIONAL = "high_dimensional"
    SPARSE = "sparse"
    DENSE = "dense"
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    TEXTUAL = "textual"
    MIXED = "mixed"
    SMALL_SAMPLE = "small_sample"
    LARGE_SAMPLE = "large_sample"


@dataclass
class TaskAnalysis:
    """Result of analyzing input data for task characteristics."""
    task_type: TaskType
    characteristics: List[DataCharacteristic] = field(default_factory=list)
    confidence: float = 0.0
    data_shape: Optional[Tuple] = None
    num_features: int = 0
    num_samples: int = 0
    has_timestamps: bool = False
    has_edges: bool = False
    has_nodes: bool = False
    has_text: bool = False
    sparsity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_type': self.task_type.value,
            'characteristics': [c.value for c in self.characteristics],
            'confidence': self.confidence,
            'data_shape': self.data_shape,
            'num_features': self.num_features,
            'num_samples': self.num_samples,
            'has_timestamps': self.has_timestamps,
            'has_edges': self.has_edges,
            'has_nodes': self.has_nodes,
            'has_text': self.has_text,
            'sparsity': self.sparsity,
            'metadata': self.metadata,
        }


@dataclass
class ModelScore:
    """Score for a single model."""
    model_name: str
    score: float
    reasons: List[str] = field(default_factory=list)
    penalties: List[str] = field(default_factory=list)
    is_available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_name': self.model_name,
            'score': self.score,
            'reasons': self.reasons,
            'penalties': self.penalties,
            'is_available': self.is_available,
        }


@dataclass
class AutoSelectionResult:
    """Result of automatic model selection."""
    success: bool
    recommended_models: List[str] = field(default_factory=list)
    model_weights: Dict[str, float] = field(default_factory=dict)
    task_analysis: Optional[TaskAnalysis] = None
    model_scores: List[ModelScore] = field(default_factory=list)
    selection_reason: str = ""
    confidence: float = 0.0
    latency_ms: float = 0.0
    fallback_used: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'recommended_models': self.recommended_models,
            'model_weights': self.model_weights,
            'task_analysis': self.task_analysis.to_dict() if self.task_analysis else None,
            'model_scores': [s.to_dict() for s in self.model_scores],
            'selection_reason': self.selection_reason,
            'confidence': self.confidence,
            'latency_ms': self.latency_ms,
            'fallback_used': self.fallback_used,
            'error': self.error,
        }


# =============================================================================
# MODEL CAPABILITIES MATRIX
# =============================================================================

# Each model's suitability for different task types (0.0 - 1.0)
MODEL_TASK_SCORES = {
    # Time-Series Models
    'lstm': {
        TaskType.TIME_SERIES: 0.95,
        TaskType.REGRESSION: 0.7,
        TaskType.DECISION: 0.5,
        TaskType.CLASSIFICATION: 0.4,
    },
    'prophet': {
        TaskType.TIME_SERIES: 0.9,
        TaskType.REGRESSION: 0.6,
    },

    # Anomaly Detection Models
    'autoencoder': {
        TaskType.ANOMALY: 0.95,
        TaskType.CLUSTERING: 0.6,
    },
    'isolation_forest': {
        TaskType.ANOMALY: 0.85,
        TaskType.CLUSTERING: 0.5,
    },

    # Graph Models
    'gnn': {
        TaskType.GRAPH: 0.95,
        TaskType.CLUSTERING: 0.7,
        TaskType.CLASSIFICATION: 0.6,
    },

    # Decision Models
    'rl': {
        TaskType.DECISION: 0.95,
        TaskType.CLASSIFICATION: 0.5,
    },

    # Text/NLP Models
    'distilbert': {
        TaskType.TEXT: 0.95,
        TaskType.CLASSIFICATION: 0.8,
        TaskType.CLUSTERING: 0.5,
    },
    'embeddings': {
        TaskType.TEXT: 0.9,
        TaskType.CLUSTERING: 0.7,
        TaskType.CLASSIFICATION: 0.6,
    },

    # General Purpose Models
    'lightgbm': {
        TaskType.CLASSIFICATION: 0.9,
        TaskType.REGRESSION: 0.9,
        TaskType.ANOMALY: 0.6,
        TaskType.DECISION: 0.6,
        TaskType.TIME_SERIES: 0.5,
    },
    'xgboost': {
        TaskType.CLASSIFICATION: 0.9,
        TaskType.REGRESSION: 0.9,
        TaskType.ANOMALY: 0.6,
    },
    'random_forest': {
        TaskType.CLASSIFICATION: 0.85,
        TaskType.REGRESSION: 0.8,
        TaskType.ANOMALY: 0.5,
    },

    # Clustering Models
    'kmeans': {
        TaskType.CLUSTERING: 0.85,
        TaskType.ANOMALY: 0.4,
    },

    # Similarity Models
    'cosine_similarity': {
        TaskType.TEXT: 0.7,
        TaskType.CLUSTERING: 0.6,
        TaskType.CLASSIFICATION: 0.5,
    },

    # Neural Network
    'mlp': {
        TaskType.CLASSIFICATION: 0.8,
        TaskType.REGRESSION: 0.75,
    },

    # Rules-based
    'rules': {
        TaskType.CLASSIFICATION: 0.5,
        TaskType.DECISION: 0.6,
        TaskType.ANOMALY: 0.4,
    },
}

# Characteristic bonuses - extra score for models that handle certain characteristics well
CHARACTERISTIC_BONUSES = {
    'lstm': {
        DataCharacteristic.SEQUENTIAL: 0.15,
        DataCharacteristic.TEMPORAL: 0.15,
    },
    'prophet': {
        DataCharacteristic.TEMPORAL: 0.2,
        DataCharacteristic.SEQUENTIAL: 0.1,
    },
    'gnn': {
        DataCharacteristic.GRAPH_STRUCTURE: 0.2,
    },
    'autoencoder': {
        DataCharacteristic.HIGH_DIMENSIONAL: 0.1,
        DataCharacteristic.DENSE: 0.05,
    },
    'isolation_forest': {
        DataCharacteristic.SPARSE: 0.1,
        DataCharacteristic.HIGH_DIMENSIONAL: 0.05,
    },
    'kmeans': {
        DataCharacteristic.NUMERICAL: 0.1,
        DataCharacteristic.DENSE: 0.05,
    },
    'distilbert': {
        DataCharacteristic.TEXTUAL: 0.2,
    },
    'embeddings': {
        DataCharacteristic.TEXTUAL: 0.15,
    },
    'lightgbm': {
        DataCharacteristic.CATEGORICAL: 0.1,
        DataCharacteristic.MIXED: 0.1,
        DataCharacteristic.LARGE_SAMPLE: 0.05,
    },
    'random_forest': {
        DataCharacteristic.SMALL_SAMPLE: 0.1,
        DataCharacteristic.MIXED: 0.05,
    },
}

# Characteristic penalties - score reduction for poor fit
CHARACTERISTIC_PENALTIES = {
    'lstm': {
        DataCharacteristic.SMALL_SAMPLE: -0.2,  # LSTM needs more data
        DataCharacteristic.CATEGORICAL: -0.1,
    },
    'gnn': {
        DataCharacteristic.SMALL_SAMPLE: -0.15,
    },
    'autoencoder': {
        DataCharacteristic.SMALL_SAMPLE: -0.25,  # VAE needs more data
    },
    'prophet': {
        DataCharacteristic.SMALL_SAMPLE: -0.15,
    },
    'kmeans': {
        DataCharacteristic.CATEGORICAL: -0.2,
        DataCharacteristic.TEXTUAL: -0.3,
    },
}


class TaskAnalyzer:
    """
    Analyzes input data to detect task type and characteristics.

    Supports multiple input formats:
    - numpy arrays
    - pandas DataFrames
    - lists of dicts
    - graph structures (nodes/edges)
    - time series data
    - text data
    """

    def __init__(self):
        self._text_indicators = {
            'text', 'content', 'message', 'body', 'description',
            'title', 'name', 'summary', 'comment', 'review'
        }
        self._time_indicators = {
            'timestamp', 'time', 'date', 'datetime', 'created_at',
            'updated_at', 'period', 'day', 'month', 'year'
        }
        self._graph_indicators = {
            'nodes', 'edges', 'vertices', 'links', 'source', 'target',
            'from', 'to', 'adjacency', 'neighbors'
        }

    def analyze(self, data: Any, hint: Optional[TaskType] = None) -> TaskAnalysis:
        """
        Analyze input data to determine task type and characteristics.

        Args:
            data: Input data in various formats
            hint: Optional hint about expected task type

        Returns:
            TaskAnalysis with detected characteristics
        """
        characteristics = []
        confidence = 0.5  # Base confidence
        metadata = {}

        # Detect data format and extract properties
        data_shape = None
        num_features = 0
        num_samples = 0
        has_timestamps = False
        has_edges = False
        has_nodes = False
        has_text = False
        sparsity = 0.0

        # Handle different input types
        if isinstance(data, dict):
            result = self._analyze_dict(data)
            characteristics.extend(result['characteristics'])
            has_timestamps = result.get('has_timestamps', False)
            has_edges = result.get('has_edges', False)
            has_nodes = result.get('has_nodes', False)
            has_text = result.get('has_text', False)
            num_samples = result.get('num_samples', 0)
            num_features = result.get('num_features', 0)
            metadata.update(result.get('metadata', {}))

        elif isinstance(data, (list, tuple)):
            result = self._analyze_list(data)
            characteristics.extend(result['characteristics'])
            has_timestamps = result.get('has_timestamps', False)
            has_edges = result.get('has_edges', False)
            has_text = result.get('has_text', False)
            num_samples = result.get('num_samples', len(data))
            data_shape = (num_samples,)

        elif hasattr(data, 'shape'):  # numpy array or pandas
            result = self._analyze_array(data)
            characteristics.extend(result['characteristics'])
            data_shape = result.get('shape')
            num_samples = result.get('num_samples', 0)
            num_features = result.get('num_features', 0)
            sparsity = result.get('sparsity', 0.0)
            has_timestamps = result.get('has_timestamps', False)
            has_text = result.get('has_text', False)

        elif isinstance(data, str):
            has_text = True
            characteristics.append(DataCharacteristic.TEXTUAL)
            num_samples = 1

        # Determine task type
        task_type = self._determine_task_type(
            characteristics, has_timestamps, has_edges, has_nodes, has_text, hint
        )

        # Apply hint if provided
        if hint:
            task_type = hint
            confidence = max(confidence, 0.7)

        # Add sample size characteristics
        if num_samples > 0:
            if num_samples < 100:
                characteristics.append(DataCharacteristic.SMALL_SAMPLE)
            elif num_samples > 10000:
                characteristics.append(DataCharacteristic.LARGE_SAMPLE)

        # Calculate final confidence
        confidence = self._calculate_confidence(
            task_type, characteristics, has_timestamps, has_edges, has_text
        )

        return TaskAnalysis(
            task_type=task_type,
            characteristics=characteristics,
            confidence=confidence,
            data_shape=data_shape,
            num_features=num_features,
            num_samples=num_samples,
            has_timestamps=has_timestamps,
            has_edges=has_edges,
            has_nodes=has_nodes,
            has_text=has_text,
            sparsity=sparsity,
            metadata=metadata,
        )

    def _analyze_dict(self, data: dict) -> Dict[str, Any]:
        """Analyze dictionary input."""
        characteristics = []
        has_timestamps = False
        has_edges = False
        has_nodes = False
        has_text = False
        num_samples = 0
        num_features = len(data)
        metadata = {}

        keys_lower = {k.lower() for k in data.keys()}

        # Check for graph structure
        if keys_lower & self._graph_indicators:
            has_edges = 'edges' in keys_lower or 'links' in keys_lower
            has_nodes = 'nodes' in keys_lower or 'vertices' in keys_lower
            if has_edges or has_nodes:
                characteristics.append(DataCharacteristic.GRAPH_STRUCTURE)
                if 'nodes' in data:
                    num_samples = len(data['nodes'])
                if 'edges' in data:
                    metadata['num_edges'] = len(data['edges'])

        # Check for time indicators
        if keys_lower & self._time_indicators:
            has_timestamps = True
            characteristics.append(DataCharacteristic.TEMPORAL)

        # Check for text content
        if keys_lower & self._text_indicators:
            has_text = True
            characteristics.append(DataCharacteristic.TEXTUAL)

        # Check value types
        has_numerical = False
        has_categorical = False

        for key, value in data.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                has_numerical = True
            elif isinstance(value, str):
                if len(value) > 50:  # Likely text content
                    has_text = True
                else:
                    has_categorical = True
            elif isinstance(value, list):
                num_samples = max(num_samples, len(value))
                if value and isinstance(value[0], (int, float)):
                    has_numerical = True
                    characteristics.append(DataCharacteristic.SEQUENTIAL)

        if has_numerical:
            characteristics.append(DataCharacteristic.NUMERICAL)
        if has_categorical:
            characteristics.append(DataCharacteristic.CATEGORICAL)
        if has_numerical and has_categorical:
            characteristics.append(DataCharacteristic.MIXED)

        return {
            'characteristics': characteristics,
            'has_timestamps': has_timestamps,
            'has_edges': has_edges,
            'has_nodes': has_nodes,
            'has_text': has_text,
            'num_samples': num_samples,
            'num_features': num_features,
            'metadata': metadata,
        }

    def _analyze_list(self, data: list) -> Dict[str, Any]:
        """Analyze list input."""
        characteristics = []
        has_timestamps = False
        has_edges = False
        has_text = False
        num_samples = len(data)

        if not data:
            return {
                'characteristics': characteristics,
                'has_timestamps': False,
                'has_edges': False,
                'has_text': False,
                'num_samples': 0,
            }

        first = data[0]

        # List of tuples (edge list?)
        if isinstance(first, (tuple, list)) and len(first) == 2:
            # Could be edge list
            has_edges = True
            characteristics.append(DataCharacteristic.GRAPH_STRUCTURE)

        # List of dicts
        elif isinstance(first, dict):
            result = self._analyze_dict(first)
            characteristics.extend(result['characteristics'])
            has_timestamps = result.get('has_timestamps', False)
            has_text = result.get('has_text', False)

        # List of strings
        elif isinstance(first, str):
            has_text = True
            characteristics.append(DataCharacteristic.TEXTUAL)

        # List of numbers (sequence)
        elif isinstance(first, (int, float)):
            characteristics.append(DataCharacteristic.SEQUENTIAL)
            characteristics.append(DataCharacteristic.NUMERICAL)

        return {
            'characteristics': characteristics,
            'has_timestamps': has_timestamps,
            'has_edges': has_edges,
            'has_text': has_text,
            'num_samples': num_samples,
        }

    def _analyze_array(self, data: Any) -> Dict[str, Any]:
        """Analyze numpy array or pandas DataFrame."""
        characteristics = []
        has_timestamps = False
        has_text = False

        shape = data.shape
        num_samples = shape[0] if len(shape) > 0 else 0
        num_features = shape[1] if len(shape) > 1 else 1

        # Check for high dimensionality
        if num_features > 50:
            characteristics.append(DataCharacteristic.HIGH_DIMENSIONAL)

        # Check sparsity
        sparsity = 0.0
        try:
            if hasattr(data, 'values'):  # pandas
                arr = data.values
            else:
                arr = data
            if arr.size > 0:
                zeros = np.sum(arr == 0)
                sparsity = zeros / arr.size
                if sparsity > 0.5:
                    characteristics.append(DataCharacteristic.SPARSE)
                else:
                    characteristics.append(DataCharacteristic.DENSE)
        except Exception:
            characteristics.append(DataCharacteristic.DENSE)

        # Check for sequential pattern (2D with time dimension)
        if len(shape) >= 2:
            characteristics.append(DataCharacteristic.SEQUENTIAL)

        # Check column names for pandas
        if hasattr(data, 'columns'):
            cols_lower = {str(c).lower() for c in data.columns}
            if cols_lower & self._time_indicators:
                has_timestamps = True
                characteristics.append(DataCharacteristic.TEMPORAL)
            if cols_lower & self._text_indicators:
                has_text = True
                characteristics.append(DataCharacteristic.TEXTUAL)

        characteristics.append(DataCharacteristic.NUMERICAL)

        return {
            'characteristics': characteristics,
            'shape': shape,
            'num_samples': num_samples,
            'num_features': num_features,
            'sparsity': sparsity,
            'has_timestamps': has_timestamps,
            'has_text': has_text,
        }

    def _determine_task_type(
        self,
        characteristics: List[DataCharacteristic],
        has_timestamps: bool,
        has_edges: bool,
        has_nodes: bool,
        has_text: bool,
        hint: Optional[TaskType]
    ) -> TaskType:
        """Determine the most likely task type from characteristics."""
        if hint:
            return hint

        # Graph tasks
        if has_edges or has_nodes or DataCharacteristic.GRAPH_STRUCTURE in characteristics:
            return TaskType.GRAPH

        # Time series
        if has_timestamps or DataCharacteristic.TEMPORAL in characteristics:
            return TaskType.TIME_SERIES

        # Text tasks
        if has_text or DataCharacteristic.TEXTUAL in characteristics:
            return TaskType.TEXT

        # Sequential data without timestamps could be time series
        if DataCharacteristic.SEQUENTIAL in characteristics:
            return TaskType.TIME_SERIES

        # High dimensional could be anomaly
        if DataCharacteristic.HIGH_DIMENSIONAL in characteristics:
            return TaskType.ANOMALY

        # Sparse data often clustering
        if DataCharacteristic.SPARSE in characteristics:
            return TaskType.CLUSTERING

        # Default to classification for numerical data
        if DataCharacteristic.NUMERICAL in characteristics:
            return TaskType.CLASSIFICATION

        return TaskType.UNKNOWN

    def _calculate_confidence(
        self,
        task_type: TaskType,
        characteristics: List[DataCharacteristic],
        has_timestamps: bool,
        has_edges: bool,
        has_text: bool
    ) -> float:
        """Calculate confidence in the task type detection."""
        confidence = 0.5

        # Strong indicators
        if task_type == TaskType.GRAPH and (has_edges or DataCharacteristic.GRAPH_STRUCTURE in characteristics):
            confidence += 0.3
        elif task_type == TaskType.TIME_SERIES and has_timestamps:
            confidence += 0.3
        elif task_type == TaskType.TEXT and has_text:
            confidence += 0.3

        # Multiple supporting characteristics
        relevant_chars = 0
        for char in characteristics:
            if task_type == TaskType.TIME_SERIES and char in [DataCharacteristic.TEMPORAL, DataCharacteristic.SEQUENTIAL]:
                relevant_chars += 1
            elif task_type == TaskType.GRAPH and char == DataCharacteristic.GRAPH_STRUCTURE:
                relevant_chars += 1
            elif task_type == TaskType.TEXT and char == DataCharacteristic.TEXTUAL:
                relevant_chars += 1
            elif task_type == TaskType.ANOMALY and char in [DataCharacteristic.HIGH_DIMENSIONAL, DataCharacteristic.SPARSE]:
                relevant_chars += 1

        confidence += min(relevant_chars * 0.1, 0.2)

        return min(confidence, 1.0)


class ModelScorer:
    """
    Scores models based on task analysis.

    Uses MODEL_TASK_SCORES matrix plus characteristic bonuses/penalties.
    """

    def __init__(self, registry=None):
        self._registry = registry

    def score_models(
        self,
        task_analysis: TaskAnalysis,
        available_models: List[str]
    ) -> List[ModelScore]:
        """
        Score all available models for the given task.

        Args:
            task_analysis: Result from TaskAnalyzer
            available_models: List of model names that are available

        Returns:
            List of ModelScore sorted by score (highest first)
        """
        scores = []

        for model_name in available_models:
            score, reasons, penalties = self._score_model(model_name, task_analysis)
            scores.append(ModelScore(
                model_name=model_name,
                score=score,
                reasons=reasons,
                penalties=penalties,
                is_available=True,
            ))

        # Add unavailable models with 0 score for completeness
        all_models = set(MODEL_TASK_SCORES.keys())
        missing = all_models - set(available_models)
        for model_name in missing:
            scores.append(ModelScore(
                model_name=model_name,
                score=0.0,
                reasons=[],
                penalties=["Model not available"],
                is_available=False,
            ))

        # Sort by score descending
        scores.sort(key=lambda x: x.score, reverse=True)

        return scores

    def _score_model(
        self,
        model_name: str,
        task_analysis: TaskAnalysis
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculate score for a single model.

        Returns:
            Tuple of (score, reasons, penalties)
        """
        reasons = []
        penalties = []

        # Base score from task type
        task_scores = MODEL_TASK_SCORES.get(model_name, {})
        base_score = task_scores.get(task_analysis.task_type, 0.0)

        if base_score > 0:
            reasons.append(f"Good fit for {task_analysis.task_type.value} tasks ({base_score:.2f})")

        score = base_score

        # Apply characteristic bonuses
        bonuses = CHARACTERISTIC_BONUSES.get(model_name, {})
        for char in task_analysis.characteristics:
            bonus = bonuses.get(char, 0.0)
            if bonus > 0:
                score += bonus
                reasons.append(f"+{bonus:.2f} for {char.value}")

        # Apply characteristic penalties
        penalty_map = CHARACTERISTIC_PENALTIES.get(model_name, {})
        for char in task_analysis.characteristics:
            penalty = penalty_map.get(char, 0.0)
            if penalty < 0:
                score += penalty
                penalties.append(f"{penalty:.2f} for {char.value}")

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        return score, reasons, penalties


class ModelSelector:
    """
    Main class for automatic model selection.

    Combines TaskAnalyzer and ModelScorer to select optimal models.
    """

    def __init__(self, registry=None):
        """
        Initialize the model selector.

        Args:
            registry: Optional ModelRegistry instance for checking availability
        """
        self._registry = registry
        self._analyzer = TaskAnalyzer()
        self._scorer = ModelScorer(registry)
        self._selection_history: List[Dict[str, Any]] = []

    def select_models(
        self,
        data: Any,
        task_hint: Optional[TaskType] = None,
        max_models: int = 2,
        min_score: float = 0.3,
        agent_name: Optional[str] = None,
    ) -> AutoSelectionResult:
        """
        Automatically select optimal models for the given data.

        Args:
            data: Input data to analyze
            task_hint: Optional hint about task type
            max_models: Maximum number of models to recommend
            min_score: Minimum score threshold for recommendation
            agent_name: Optional agent name for context

        Returns:
            AutoSelectionResult with recommended models and analysis
        """
        start_time = time.time()

        try:
            # Step 1: Analyze the task
            task_analysis = self._analyzer.analyze(data, hint=task_hint)

            # Step 2: Get available models
            available_models = self._get_available_models()

            if not available_models:
                return AutoSelectionResult(
                    success=False,
                    error="No models available",
                    latency_ms=(time.time() - start_time) * 1000,
                )

            # Step 3: Score all models
            model_scores = self._scorer.score_models(task_analysis, available_models)

            # Step 4: Select top models
            recommended = []
            weights = {}

            for ms in model_scores:
                if ms.score >= min_score and len(recommended) < max_models:
                    recommended.append(ms.model_name)

            # Calculate weights proportional to scores
            if recommended:
                total_score = sum(
                    ms.score for ms in model_scores
                    if ms.model_name in recommended
                )
                for ms in model_scores:
                    if ms.model_name in recommended:
                        weights[ms.model_name] = ms.score / total_score if total_score > 0 else 1.0 / len(recommended)

            # Fallback if no models meet threshold
            if not recommended:
                # Use best available model
                best = model_scores[0] if model_scores else None
                if best and best.is_available:
                    recommended = [best.model_name]
                    weights = {best.model_name: 1.0}
                    fallback_used = True
                else:
                    # Ultimate fallback
                    recommended = ['lightgbm'] if 'lightgbm' in available_models else available_models[:1]
                    weights = {recommended[0]: 1.0} if recommended else {}
                    fallback_used = True
            else:
                fallback_used = False

            # Build selection reason
            if recommended:
                top_model = recommended[0]
                top_score = next(
                    (ms for ms in model_scores if ms.model_name == top_model), None
                )
                if top_score and top_score.reasons:
                    selection_reason = f"Selected {top_model} for {task_analysis.task_type.value}: {top_score.reasons[0]}"
                else:
                    selection_reason = f"Selected {top_model} for {task_analysis.task_type.value}"
            else:
                selection_reason = "No suitable models found"

            # Record selection
            self._record_selection(
                agent_name=agent_name,
                task_analysis=task_analysis,
                selected_models=recommended,
                model_scores=model_scores,
            )

            return AutoSelectionResult(
                success=True,
                recommended_models=recommended,
                model_weights=weights,
                task_analysis=task_analysis,
                model_scores=model_scores,
                selection_reason=selection_reason,
                confidence=task_analysis.confidence,
                latency_ms=(time.time() - start_time) * 1000,
                fallback_used=fallback_used,
            )

        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            return AutoSelectionResult(
                success=False,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    def _get_available_models(self) -> List[str]:
        """Get list of available models from registry."""
        if self._registry:
            try:
                return self._registry.list_available_models()
            except Exception as e:
                logger.warning(f"Could not get models from registry: {e}")

        # Fallback to known models
        return list(MODEL_TASK_SCORES.keys())

    def _record_selection(
        self,
        agent_name: Optional[str],
        task_analysis: TaskAnalysis,
        selected_models: List[str],
        model_scores: List[ModelScore],
    ):
        """Record selection for history/learning."""
        record = {
            'timestamp': time.time(),
            'agent_name': agent_name,
            'task_type': task_analysis.task_type.value,
            'characteristics': [c.value for c in task_analysis.characteristics],
            'selected_models': selected_models,
            'top_scores': [
                {'model': ms.model_name, 'score': ms.score}
                for ms in model_scores[:5]
            ],
        }
        self._selection_history.append(record)

        # Keep last 1000 selections
        if len(self._selection_history) > 1000:
            self._selection_history = self._selection_history[-1000:]

    def get_selection_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent selection history."""
        return self._selection_history[-limit:]

    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about task type distribution."""
        if not self._selection_history:
            return {}

        task_counts: Dict[str, int] = {}
        model_counts: Dict[str, int] = {}

        for record in self._selection_history:
            task = record.get('task_type', 'unknown')
            task_counts[task] = task_counts.get(task, 0) + 1

            for model in record.get('selected_models', []):
                model_counts[model] = model_counts.get(model, 0) + 1

        return {
            'total_selections': len(self._selection_history),
            'task_distribution': task_counts,
            'model_distribution': model_counts,
        }


# =============================================================================
# SINGLETON ACCESSOR
# =============================================================================

_selector: Optional[ModelSelector] = None


def get_model_selector(registry=None) -> ModelSelector:
    """
    Get the singleton model selector instance.

    Args:
        registry: Optional ModelRegistry for model availability checks

    Returns:
        ModelSelector instance
    """
    global _selector
    if _selector is None:
        _selector = ModelSelector(registry=registry)
    return _selector
