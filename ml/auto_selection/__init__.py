"""
Model Auto-Selection Package (Session 682 - Phase 6)
====================================================

Provides automatic ML model selection based on task characteristics.

Usage:
    from ml.auto_selection import get_model_selector, TaskType

    selector = get_model_selector()

    # Auto-select models for data
    result = selector.select_models(data)
    print(f"Recommended: {result.recommended_models}")
    print(f"Task type: {result.task_analysis.task_type}")

    # With task hint
    result = selector.select_models(data, task_hint=TaskType.TIME_SERIES)

    # Limit to single model
    result = selector.select_models(data, max_models=1)
"""

from .model_selector import (
    # Main classes
    ModelSelector,
    TaskAnalyzer,
    ModelScorer,

    # Dataclasses
    AutoSelectionResult,
    TaskAnalysis,
    ModelScore,

    # Enums
    TaskType,
    DataCharacteristic,

    # Singleton accessor
    get_model_selector,

    # Constants (for customization)
    MODEL_TASK_SCORES,
    CHARACTERISTIC_BONUSES,
    CHARACTERISTIC_PENALTIES,
)

__all__ = [
    # Main classes
    'ModelSelector',
    'TaskAnalyzer',
    'ModelScorer',

    # Dataclasses
    'AutoSelectionResult',
    'TaskAnalysis',
    'ModelScore',

    # Enums
    'TaskType',
    'DataCharacteristic',

    # Singleton accessor
    'get_model_selector',

    # Constants
    'MODEL_TASK_SCORES',
    'CHARACTERISTIC_BONUSES',
    'CHARACTERISTIC_PENALTIES',
]
