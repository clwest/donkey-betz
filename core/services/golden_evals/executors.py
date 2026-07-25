"""Executors for the Golden Evals validator harness.

Executors take a resolved slice + prompt spec + dispatched agent response
and produce a structured pass/fail verdict with typed failure reasons.
Kept intentionally small at PR-2a: one shape validator (JSON Schema over
``expected_output_shape``) and a stable ``FailureReason`` shape so
downstream acceptance-criteria runners can accrete new predicate types
without changing the outer verdict shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class FailureReason:
    """One structured predicate failure.

    Emitted by both the JSON Schema executor and the Pydantic
    acceptance-criteria runners. Persisted verbatim into
    ``GoldenEvalRun.failure_reasons`` when the harness runs with
    ``--execute``.
    """

    predicate: str
    detail: str
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "predicate": self.predicate,
            "detail": self.detail,
            "path": self.path,
        }


@dataclass
class SchemaVerdict:
    """Result of validating one response against an ``expected_output_shape``."""

    passed: bool
    failure_reasons: list[FailureReason] = field(default_factory=list)


def validate_expected_output_shape(
    response: Any,
    expected_output_shape: dict[str, Any] | None,
) -> SchemaVerdict:
    """Validate ``response`` against the ``expected_output_shape`` JSON Schema.

    The slice YAMLs (canon_version=1, S2955-frozen) declare
    ``expected_output_shape`` per prompt as an inline JSON Schema fragment
    with ``type``, ``required``, and ``properties`` — see
    ``evals/tier1/system_intelligence_agent.yaml:96-108`` for the canonical
    shape.

    Behavior:

    * ``expected_output_shape`` is ``None`` or empty → verdict passes with
      zero reasons. Slices are permitted to omit shape when the prompt is
      free-form (e.g., interviewer-style Rigby happy-path turns).
    * ``response`` is not a JSON-serializable ``dict``/``list``/scalar →
      fails with one predicate ``expected_output_shape`` (Draft 2020-12
      only validates JSON documents).
    * Validation errors are emitted one predicate per error, so downstream
      dashboards can distinguish "missing required field X" from "field Y
      shorter than declared minLength".
    """
    if not expected_output_shape:
        return SchemaVerdict(passed=True)

    validator = Draft202012Validator(expected_output_shape)
    errors = sorted(validator.iter_errors(response), key=lambda e: list(e.path))

    if not errors:
        return SchemaVerdict(passed=True)

    reasons = [
        FailureReason(
            predicate="expected_output_shape",
            detail=str(err.message),
            path=".".join(str(p) for p in err.absolute_path),
        )
        for err in errors
    ]
    return SchemaVerdict(passed=False, failure_reasons=reasons)


def compile_schema(expected_output_shape: dict[str, Any]) -> Draft202012Validator:
    """Validate that ``expected_output_shape`` is itself a legal JSON Schema.

    Raises :class:`jsonschema.exceptions.SchemaError` when the shape block
    is malformed. Called by the harness at slice load time so authoring
    errors surface in the loader, not at first ``--execute`` invocation.
    """
    Draft202012Validator.check_schema(expected_output_shape)
    return Draft202012Validator(expected_output_shape)


__all__ = [
    "FailureReason",
    "SchemaVerdict",
    "compile_schema",
    "validate_expected_output_shape",
    # Re-export so callers don't have to import jsonschema directly for
    # exception handling.
    "jsonschema",
]
