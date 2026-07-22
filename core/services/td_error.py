"""ToolDispatcher handler-level error envelope helper — canonical shared module.

S2888 Ledger #13 extraction — factored out from 6 adopter files after the
S2875 6-adopter gate met at S2886 close. The `_handler_error` function-body
had reached function-body identical shape across all 6 adopters; each carried
a file-local copy pending this extraction.

NOT the ops tool-gateway `_tool_error` helper. That helper lives in
`td_handlers_ops.py`, emits a distinct 3-key envelope
(``{'error', 'error_code', **fields}``) used by 12 gateway-layer adopters
(spider_status_tool / kb_tool paths), and stays file-local per Rigby's
S2875 Q3=A. Do NOT collapse the two shapes without a fresh SIGN cycle.

Adopter enumeration (Ledger #22 sunset arc, 6/6 gate met):

  * ``td_handlers_governance.py`` — S2879 (origin)
  * ``td_handlers_ops.py``        — S2879 (origin)
  * ``td_handlers_agents.py``     — S2884
  * ``td_handlers_newsletter.py`` — S2884
  * ``td_handlers_content.py``    — S2885
  * ``td_handlers_core.py``       — S2886 (6/6 gate met at this session)

Taxonomy (S2879 4-code minimal + S2882 5th code):

  * ``invalid_params``      — missing or invalid input
  * ``not_found``           — target resource does not exist
  * ``unknown_action``      — action string not in the valid set
  * ``dependency_missing``  — optional model/service import failed
  * ``permission_denied``   — caller lacks required authorization
    (S2882 close: Rigby SIGN + Chris D-verdict added this 5th code so
    ``_authorize_staff`` not-staff denial gets a structured envelope;
    scope is strictly authz — do NOT expand to other access-control
    failures without a fresh SIGN.)

Contract stability (Rigby SIGN S2888):

  Additive metadata via ``**fields`` is safe. Required-shape changes
  (new mandatory keys, renamed keys) are NOT safe and require either
  (a) a new helper name (e.g. ``_handler_error_v2``), or (b) a fresh
  SIGN cycle. Treat the 5-key envelope
  ``{success, error_code, error, action, **fields}`` as frozen.
"""
from typing import Any, Dict


def _handler_error(action: str, code: str, message: str, **fields) -> Dict[str, Any]:
    """S2879 canonical handler-level structured error envelope.

    Shape: ``{success: False, error_code, error, action, **fields}``.
    """
    return {
        'success': False,
        'error_code': code,
        'error': message,
        'action': action,
        **fields,
    }
