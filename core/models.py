"""
core/models.py — TOMBSTONE

Historical monolith. As of Session 1242 PR #2677 + Session 1243 PR (this one),
all class definitions and module-level code that lived here have been removed.

WHY THIS FILE IS A TOMBSTONE
============================

Python's import machinery prefers `core/models/` (the package) over
`core/models.py` (this file) when both exist. Django therefore loads the
package; this file's class definitions and signal handlers were never
loaded. `apps.get_model('core', '<name>')` resolves to package classes,
not this file's classes — which means every class previously here was
provably dead text.

The shadowing pattern was discovered in Session 1242 close while doing the
Cat 2 Phantom Dependencies audit. PR #2677 surgically removed one class
(`AgentLearningSession`); this PR removes the remaining 24 by tombstoning
the file outright after a per-class `apps.get_model()` resolution scan
confirmed each was dead.

WHERE TO FIND THE LIVE MODELS
=============================

Active classes live in:

  core/models/                — domain-split package (base, system, users,
                                jobs, conversations, ai_learning, projects).
                                Loaded by Django via core.apps.CoreConfig.
  core/models_unified_system.py
                              — sibling monolith file. Imported via
                                `from ..models_unified_system import *`
                                in core/models/__init__.py.
  core/models_*.py            — other sibling models files. Each imported
                                explicitly in core/models/__init__.py.

`from core.models import X` resolves to the PACKAGE. Always has.

AUDIT TRAIL
===========

- Discovery + first removal:  docs/handoffs/SESSION_1242_*.md
- Per-class resolution scan:  Session 1243 P2c (Cat 2 Finding 2.1)
- Cat 2 deliverable:          86870fdd-e8d8-48d3-9760-4bea75ec10e3
- Related open findings (NOT closed by this PR):
    Cat 1 finding 1.x — PaMessageFeedback stillborn endpoint
      (`/api/pa/feedback/` is live but `core_pamessagefeedback`
      table was never created; product question pending).
    Cat 2 finding — Revenue + other models_unified_system entries
      need their own audit pass.

DO NOT ADD MODELS HERE. Add them under core/models/<domain>/ instead.
"""
