"""Acceptance-criteria runners for the Golden Evals validator harness.

Each slice YAML declares an ``acceptance_criteria`` list of predicate
identifiers per prompt (see ``evals/tier1/system_intelligence_agent.yaml``
line 103 for the canonical shape). This module maps those identifiers to
callables and executes them against an ``EvalRunContext`` + the agent
response body.

**PR-2a scope (S2965):** universal predicates only —
``required_fields_present``, ``assistant_response_length_gte_N``. Named
Rigby-specific predicates from ``rigby_agent.yaml`` §252-266
(``no_fabricated_tool_runs``, ``detects_and_surfaces_tool_runs_empty_vs_claimed``,
etc.) and named SIA-specific predicates (``tool_call_get_system_attention_invoked``,
``counts_reconcile_with_tool_output``, ``severity_filter_argument_is_critical``)
are DEFERRED to PR-2b + follow-ons. Unknown predicates return
``INCONCLUSIVE`` rather than pass or fail — the harness prints an
explicit inconclusive count in the run summary so the abstraction ships
without silently masking coverage gaps.

**Rigby A2 REVISE gating (S2965 T1 SIGN):** Rigby-specific fabrication
predicates that inspect the ``ToolCallRecord`` ledger MUST inspect
``EvalRunContext.ledger_health`` first and return ``INCONCLUSIVE`` when
health is not ``ok`` (see :data:`~core.services.golden_evals.context.LEDGER_HEALTH_OK`),
so passing/failing does not accrete against a broken evidence substrate
(Ledger #20 + #21). PR-2b registers those predicates; the gating
convention lives here so authors of the PR-2b runners follow it by
default.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .context import EvalRunContext
from .executors import FailureReason


@dataclass
class PredicateVerdict:
    """Result of evaluating one acceptance-criteria predicate.

    Verdict shape mirrors :class:`~core.services.golden_evals.executors.SchemaVerdict`
    but adds an ``inconclusive`` state so ``ledger_health != OK`` cases
    (Rigby A2 REVISE) are distinguishable from pass/fail in the run summary.
    """

    predicate: str
    passed: bool | None  # None means INCONCLUSIVE
    failure_reason: FailureReason | None = None
    detail: str = ""

    @property
    def inconclusive(self) -> bool:
        return self.passed is None


@dataclass
class RunnerVerdict:
    """Aggregate result for one prompt across all its acceptance predicates."""

    passed: bool
    failure_reasons: list[FailureReason] = field(default_factory=list)
    inconclusive_predicates: list[str] = field(default_factory=list)
    verdicts: list[PredicateVerdict] = field(default_factory=list)


# ── Universal predicates ────────────────────────────────────────────────


def _required_fields_present(
    ctx: EvalRunContext,
    response: Any,
    expected_output_shape: dict[str, Any] | None,
    **_: Any,
) -> PredicateVerdict:
    """Verify every field in ``expected_output_shape.required`` is present.

    Complements the JSON Schema executor (which checks the same invariant
    plus type / range / enum constraints). Kept as a standalone predicate
    so slices can declare ``required_fields_present`` without the full
    ``expected_output_shape`` block — useful for prompts that are
    structurally lax but must include a minimal handshake set.
    """
    required = []
    if isinstance(expected_output_shape, dict):
        required = expected_output_shape.get("required") or []
    if not required:
        return PredicateVerdict(
            predicate="required_fields_present",
            passed=None,
            detail=(
                "expected_output_shape.required is empty — predicate has no "
                "assertion to make. Fill in the schema or drop the predicate."
            ),
        )

    if not isinstance(response, dict):
        return PredicateVerdict(
            predicate="required_fields_present",
            passed=False,
            failure_reason=FailureReason(
                predicate="required_fields_present",
                detail=(
                    f"response is not a mapping (got {type(response).__name__}); "
                    "cannot check required fields."
                ),
            ),
        )

    missing = [f for f in required if f not in response]
    if missing:
        return PredicateVerdict(
            predicate="required_fields_present",
            passed=False,
            failure_reason=FailureReason(
                predicate="required_fields_present",
                detail=f"missing required field(s): {sorted(missing)}",
            ),
        )
    return PredicateVerdict(predicate="required_fields_present", passed=True)


_LENGTH_GTE_RE = re.compile(r"^assistant_response_length_gte_(?P<n>\d+)$")


def _assistant_response_length_gte(
    ctx: EvalRunContext,
    response: Any,
    predicate_name: str,
    **_: Any,
) -> PredicateVerdict:
    """Parametric predicate — ``assistant_response_length_gte_40`` etc.

    Slice YAMLs express minimum response lengths as predicate names
    encoding the threshold (e.g., ``assistant_response_length_gte_100``).
    The runner extracts the integer from the predicate name and asserts
    against either ``response["summary"]`` (canonical field) or the
    stringified response itself.
    """
    match = _LENGTH_GTE_RE.match(predicate_name)
    if not match:
        return PredicateVerdict(
            predicate=predicate_name,
            passed=None,
            detail=(
                f"predicate name {predicate_name!r} did not match "
                "'assistant_response_length_gte_N' — the parametric runner "
                "requires an integer threshold suffix."
            ),
        )
    threshold = int(match.group("n"))

    body: str
    if isinstance(response, dict):
        body = str(response.get("summary") or response.get("assistant_response") or "")
    else:
        body = str(response) if response is not None else ""

    if len(body) >= threshold:
        return PredicateVerdict(predicate=predicate_name, passed=True)
    return PredicateVerdict(
        predicate=predicate_name,
        passed=False,
        failure_reason=FailureReason(
            predicate=predicate_name,
            detail=f"response length {len(body)} < required {threshold}",
        ),
    )


# ── Registry ────────────────────────────────────────────────────────────


PredicateRunner = Callable[..., PredicateVerdict]


REGISTRY: dict[str, PredicateRunner] = {
    "required_fields_present": _required_fields_present,
}


def _dispatch(predicate_name: str) -> PredicateRunner | None:
    """Look up a predicate runner by name.

    Direct-registry lookup is preferred; parametric predicate families
    (``assistant_response_length_gte_N``) fall through to a regex-matched
    fallback runner. Everything else returns ``None`` — the outer
    ``run_predicates`` records these as ``INCONCLUSIVE`` rather than
    failing the prompt (see module docstring).
    """
    if predicate_name in REGISTRY:
        return REGISTRY[predicate_name]
    if _LENGTH_GTE_RE.match(predicate_name):
        return _assistant_response_length_gte
    return None


def run_predicates(
    ctx: EvalRunContext,
    response: Any,
    predicates: list[str],
    expected_output_shape: dict[str, Any] | None = None,
) -> RunnerVerdict:
    """Evaluate ``predicates`` against ``response`` and return a verdict.

    Aggregation rules:

    * All predicates ``passed=True`` → ``verdict.passed=True``.
    * Any predicate ``passed=False`` → ``verdict.passed=False`` and the
      predicate's ``failure_reason`` is appended.
    * A predicate ``passed=None`` (inconclusive) does NOT flip the
      verdict either way — the predicate name is recorded in
      ``verdict.inconclusive_predicates`` for run-summary reporting. A
      prompt where every predicate is inconclusive is reported as
      ``passed=True`` with a non-empty inconclusive list — the caller
      decides how to render that (typically as "INCONCLUSIVE" in the
      summary, not as pass).
    """
    verdicts: list[PredicateVerdict] = []
    reasons: list[FailureReason] = []
    inconclusive: list[str] = []

    for name in predicates:
        runner = _dispatch(name)
        if runner is None:
            verdicts.append(
                PredicateVerdict(
                    predicate=name,
                    passed=None,
                    detail=(
                        f"predicate {name!r} not registered in PR-2a "
                        "universal runner set; deferred to PR-2b or later."
                    ),
                )
            )
            inconclusive.append(name)
            continue

        verdict = runner(
            ctx=ctx,
            response=response,
            expected_output_shape=expected_output_shape,
            predicate_name=name,
        )
        verdicts.append(verdict)
        if verdict.inconclusive:
            inconclusive.append(name)
        elif verdict.passed is False and verdict.failure_reason is not None:
            reasons.append(verdict.failure_reason)

    # Any concrete failure → verdict fails; otherwise passes (inconclusive
    # predicates alone never fail a prompt — they are surfaced separately).
    passed = all(v.passed is not False for v in verdicts)

    return RunnerVerdict(
        passed=passed,
        failure_reasons=reasons,
        inconclusive_predicates=inconclusive,
        verdicts=verdicts,
    )


__all__ = [
    "PredicateVerdict",
    "PredicateRunner",
    "REGISTRY",
    "RunnerVerdict",
    "run_predicates",
]
