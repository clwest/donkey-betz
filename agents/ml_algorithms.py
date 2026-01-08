"""
DEPRECATED: This module has been moved to core/services/ml_algorithms.py

For new code, use:
    from core.services.ml_algorithms import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.ml_algorithms' is deprecated. "
    "Use 'from core.services.ml_algorithms import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.ml_algorithms import (
    RecommendationEngine,
    DynamicPricingOptimizer,
    CustomerSegmentation,
    InventoryPredictor,
    FraudDetector,
)
