"""
Session 1086 PR 2: Priority-aware routing — matching layer.

This package owns the pure-logic side of Rigby's priority-aware router
(initiative 2dcb79d7-6f2b-4e67-a366-a54e96d7870f). It does not modify
``agent_router.route()`` — that integration lives in PR 3.

Contents:

- :mod:`core.services.priority.agent_tags` — the AGENT_TAG_OVERRIDES
  hardcoded dict that maps agent_name → list of derived tag strings.
  Code-reviewed rather than DB-editable per Rigby's Q3 answer during the
  Session 1086 design review.
- :mod:`core.services.priority.priority_router` — :class:`PriorityRouter`
  with the ``check()`` method plus the :class:`PriorityDecision`
  dataclass that describes the match outcome.

See ``00-START-NEXT-SESSION.md`` and the design review conversation
(``pa-ba134ae68c21``) for the locked design contract.
"""

from .priority_router import PriorityDecision, PriorityRouter

__all__ = ["PriorityDecision", "PriorityRouter"]
