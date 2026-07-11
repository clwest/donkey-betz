"""
support_code generator per Failure-Data Safety Contract §5.

Format: RUR-<COMPONENT>-<yyMMdd>-<opaque-hex>
Example: RUR-AUTH-260710-a4f2

- Prefix `RUR` identifies the Real User Readiness program
- `<COMPONENT>` enumerated at §5.1: AUTH, PERM, WORKSPACE, RATE, BUSY,
  UPSTREAM, COST, CANCEL, INTERNAL, VALIDATE, INPUT, MISSING, TENANT
  (TENANT added at I-0303 Phase 2 as the async-boundary component per
  contract §10 amendment landed with the tenant_boundary_violation
  reason_code addition)
- `<yyMMdd>` UTC date component (privacy assessed acceptable for alpha
  per §5.2 — reveals rough timing, not tenant data)
- `<opaque-hex>` 4-char hex from ``secrets.token_hex(2)`` = 16 bits per
  §5.3 (65,536 codes per component-day bucket; sufficient for gated
  alpha cohort)
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Final

_ALLOWED_COMPONENTS: Final[frozenset[str]] = frozenset({
    "AUTH",
    "PERM",
    "WORKSPACE",
    "RATE",
    "BUSY",
    "UPSTREAM",
    "COST",
    "CANCEL",
    "INTERNAL",
    "VALIDATE",
    "INPUT",
    "MISSING",
    "TENANT",
})


def make_support_code(component: str) -> str:
    """Generate a support_code conforming to safety contract §5.1.

    Raises ValueError if the component is not in the enumerated set.
    """
    component = component.upper()
    if component not in _ALLOWED_COMPONENTS:
        raise ValueError(
            f"Unknown safety-contract support_code component: {component!r}. "
            f"Allowed: {sorted(_ALLOWED_COMPONENTS)}"
        )
    date_component = datetime.now(timezone.utc).strftime("%y%m%d")
    opaque = secrets.token_hex(2)
    return f"RUR-{component}-{date_component}-{opaque}"
