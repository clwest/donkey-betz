"""YAML slice discovery + parse + substrate-type validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .context import KNOWN_SUBSTRATES


TIER1_ROOT = Path("evals") / "tier1"


class SliceLoadError(ValueError):
    """Raised when a YAML slice fails validation at load time."""


@dataclass
class LoadedSlice:
    """One parsed YAML slice."""

    path: Path
    agent: str
    substrate_type: str
    canon_version: int
    schema_version: int
    prompt_ids: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


_SUBSTRATE_ALIAS: dict[str, str] = {
    # meta.substrate_pivot uses "chat_conversation_row_substrate" (S2962 slice 8);
    # older AgentExecution slices don't set the field at all — the loader
    # defaults to SUBSTRATE_AGENT_EXECUTION when meta.substrate_pivot is absent.
    "chat_conversation_row_substrate": "chat_conversation",
    "agent_execution_row_substrate": "agent_execution",
}


def discover_slices(root: Path = TIER1_ROOT) -> list[Path]:
    """Return ``evals/tier1/*.yaml`` paths, sorted for deterministic order."""
    if not root.is_dir():
        return []
    return sorted(p for p in root.glob("*.yaml") if p.is_file())


def load_slice(path: Path) -> LoadedSlice:
    """Parse one YAML slice + validate its substrate declaration.

    Enforces the zoom-out guardrail Rigby surfaced at S2964 T1 SIGN Q5
    REVISE: the substrate identity must reduce to a member of
    :data:`~core.services.golden_evals.context.KNOWN_SUBSTRATES` at load
    time, so downstream adapter dispatch cannot silently pick the wrong
    normalization path.
    """
    raw = yaml.safe_load(path.read_text())
    if not isinstance(raw, dict):
        raise SliceLoadError(f"{path}: top-level YAML is not a mapping")

    meta = raw.get("meta") or {}
    canon_version = raw.get("canon_version")
    schema_version = raw.get("schema_version")
    if canon_version is None or schema_version is None:
        raise SliceLoadError(
            f"{path}: missing schema_version + canon_version at file top "
            "(canon_v1 §1 requirement)"
        )

    substrate_pivot = meta.get("substrate_pivot")
    substrate_type: str
    if substrate_pivot is None:
        substrate_type = "agent_execution"
    else:
        substrate_type = str(_SUBSTRATE_ALIAS.get(substrate_pivot, substrate_pivot))

    if substrate_type not in KNOWN_SUBSTRATES:
        raise SliceLoadError(
            f"{path}: substrate_type={substrate_type!r} (derived from "
            f"meta.substrate_pivot={substrate_pivot!r}) is not in "
            f"KNOWN_SUBSTRATES {sorted(KNOWN_SUBSTRATES)}. Add the constant "
            "in core/services/golden_evals/context.py + ship an adapter first."
        )

    prompts = raw.get("prompts") or []
    prompt_ids = [
        p.get("id", "<missing_id>")
        for p in prompts
        if isinstance(p, dict)
    ]

    return LoadedSlice(
        path=path,
        agent=str(meta.get("agent") or "<unknown>"),
        substrate_type=substrate_type,
        canon_version=int(canon_version),
        schema_version=int(schema_version),
        prompt_ids=prompt_ids,
        raw=raw,
    )
