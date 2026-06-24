"""Canonical alias map for `Deliverable.agent_name` (and future fields).

Session 1227 PR4 — extracted from `deliverable_factory._AGENT_NAME_ALIASES`
and `core/migrations/0365_session_1226_agent_name_canonicalization.py`
(which previously held two near-duplicate copies kept in lockstep via
comments). This module is now the single source of truth; both the
write-time canonicalizer in deliverable_factory and the
`deliverable_tool.normalize` action import from here.

Why a separate module (rather than re-using deliverable_factory directly):
- normalize is a "drift detection + hygiene" surface; if it imports from
  the factory it risks circular imports as the factory grows.
- A tiny shared-constant module is the cleanest long-term contract.

Adding a new alias:
  1. Add the (variant → canonical) row to AGENT_NAME_ALIASES below.
  2. Open a one-time data-migration if existing rows hold the variant.
     (For new aliases that catch fresh drift, the tool can sweep them
     via `deliverable_tool.normalize`.)
  3. No changes needed in `deliverable_factory` — it imports from here.

Canonical reasoning (anchored in Session 1226 audit `e2964e4a-…` §1c):
  - 'Rigby' wins (101/102 existing rows already use that spelling).
  - 'claude-code' wins (matches autonomous engineer source field
    `claude_code_engineer.py:501`, the Procfile worker name
    `code-worker`, and the feedback-memory file naming).
"""
from __future__ import annotations

from typing import Optional


AGENT_NAME_ALIASES: dict[str, str] = {
    'rigby': 'Rigby',
    'ClaudeCode': 'claude-code',
}


def canonicalize_agent_name(agent_name: Optional[str]) -> str:
    """Return the canonical spelling for `agent_name`, or the input unchanged.

    Empty/None inputs return ''. Unknown values pass through unchanged so the
    map stays a strict alias surface, not an opinion engine.
    """
    if not agent_name:
        return ''
    return AGENT_NAME_ALIASES.get(agent_name, agent_name)
