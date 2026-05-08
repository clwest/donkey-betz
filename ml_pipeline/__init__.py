"""
ML Pipeline Module
Enhanced machine learning pipeline for job matching and agent optimization
"""

# NOTE — Session 1113 review (Session 1111 PR-E queue).
# Three modules in `ai_core/intelligence/` reference a missing submodule
# `ml_pipeline.pipeline` (specifically `from ml_pipeline.pipeline import MLPipeline`):
#   - ai_core/intelligence/orchestration.py     (try/except → MockMLPipeline fallback)
#   - ai_core/intelligence/monitoring_dashboard.py  (bare import → ModuleNotFoundError)
#   - ai_core/intelligence/testing_suite.py     (bare import → ModuleNotFoundError)
# This package only exports `EnhancedMLPipeline`; there is no
# `ml_pipeline/pipeline.py` and no `MLPipeline` symbol re-export.
# Decision pending: a one-line shim
#     from .enhanced_ml_pipeline import EnhancedMLPipeline as MLPipeline
# (and a corresponding `ml_pipeline/pipeline.py` that re-exports) would
# revive `orchestration.py` against real code. Until that product call
# (PR-E in the deeper-review queue), the three modules above remain
# labelled PARTIAL / BROKEN-BUT-UNREACHABLE and unchanged.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

from .enhanced_ml_pipeline import EnhancedMLPipeline

__all__ = ['EnhancedMLPipeline']