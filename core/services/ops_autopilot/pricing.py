"""
Ops-autopilot pricing shim — thin re-export from the canonical catalog.

Historical note: this module was introduced at S2853 to give
``workspace_budget_tool.enforcement_report`` a scoped pricing helper for
downgrade-savings estimation without duplicating pricing math inline. At S2854
the whole-repo canonicalization arc collapsed the 7-way divergence into a
single source of truth at ``core/services/pricing_catalog.py``, and this
module became a thin re-export retained only so existing importers keep
working without a churny rename.

New code should import directly from ``core.services.pricing_catalog``.
"""

from core.services.pricing_catalog import (  # noqa: F401
    MODEL_PRICES,
    calculate_cost,
    estimate_uncached_cost,
    get_model_pricing,
)
