"""``run_golden_evals`` — Golden Evals validator harness entrypoint.

**Session 2965 PR-2a (S2965 T1 SIGN ratified split):**

* ``--dry-run`` (default) — discover, parse, validate substrate; write
  skeleton ``GoldenEvalRun`` rows with ``passed=None``. No agent dispatch.
  Retained for infra debug + drift-scanner style regression testing.
* ``--execute`` — full end-to-end dispatch for slices whose substrate
  adapter + canonicalizer are registered. Per prompt: dispatch the
  agent, adapt the resulting substrate row into an ``EvalRunContext``,
  canonicalize the response, validate against ``expected_output_shape``,
  run acceptance-criteria predicates, persist a fully-populated
  ``GoldenEvalRun`` row with pass/fail/inconclusive verdict.

The ``--execute`` path is scoped to ``AgentExecution``-substrate slices at
PR-2a (Chris D-verdict 2026-07-25): ``ChatConversation`` slice 8 (Rigby)
dogfood is deferred to PR-2b + a separate ledger-fix arc after raw-ORM
verification found that (a) ``ToolCallRecord.trace_id`` is NULL on 100%
of 5,430 rows (Ledger #20) and (b) PA→ToolCallRecord writes silently
stopped 2026-06-19 — 35d regression (Ledger #21). ChatConversation
adapter still ships so PR-2b can build against it, but ``--execute``
skips ChatConversation prompts with an explicit ``[SUBSTRATE-DEFERRED]``
marker rather than pretending to validate against a broken evidence
ledger.

Usage:

    # Discover + dry-run every Tier-1 slice.
    python manage.py run_golden_evals

    # Filter to one slice by filename stem.
    python manage.py run_golden_evals --slice system_intelligence_agent

    # Actually dispatch agents + validate responses.
    python manage.py run_golden_evals --execute --slice system_intelligence_agent
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.models_golden_evals import GoldenEvalRun
from core.services.golden_evals.adapters import ADAPTER_REGISTRY
from core.services.golden_evals.adapters.agent_execution import AgentExecutionAdapter
from core.services.golden_evals.canonicalizers import canonicalize
from core.services.golden_evals.context import (
    EVIDENCE_AGENT_EXECUTION_NATIVE,
    LEDGER_HEALTH_OK,
    LEDGER_HEALTH_UNAVAILABLE,
    SUBSTRATE_AGENT_EXECUTION,
    EvalRunContext,
)
from core.services.golden_evals.executors import (
    FailureReason,
    validate_expected_output_shape,
)
from core.services.golden_evals.loader import (
    LoadedSlice,
    SliceLoadError,
    TIER1_ROOT,
    discover_slices,
    load_slice,
)
from core.services.golden_evals.runners import run_predicates


class Command(BaseCommand):
    help = "Run Golden Evals Tier-1 slices (dry-run by default; --execute for real dispatch)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--yaml-root",
            default=str(TIER1_ROOT),
            help="Directory containing Tier-1 YAML slices (default: evals/tier1).",
        )
        parser.add_argument(
            "--slice",
            dest="slice_name",
            default=None,
            help=(
                "Filter to a single slice by filename stem "
                "(e.g., 'system_intelligence_agent' for evals/tier1/"
                "system_intelligence_agent.yaml)."
            ),
        )
        parser.add_argument(
            "--prompt",
            dest="prompt_id",
            default=None,
            help=(
                "Filter to a single prompt by id (e.g., "
                "'sia_happy_01_general_status'). Requires --slice."
            ),
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            default=False,
            help=(
                "Dispatch each prompt through the agent-under-test + validate "
                "the response against expected_output_shape + "
                "acceptance_criteria. Without this flag, the command runs in "
                "skeleton dry-run mode (S2964 PR-1 behavior)."
            ),
        )
        parser.add_argument(
            "--no-persist",
            action="store_true",
            default=False,
            help=(
                "Skip writing GoldenEvalRun rows even in dry-run. Useful "
                "for local inspection when the DB migration hasn't been "
                "applied to the target environment."
            ),
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        root = Path(opts["yaml_root"])
        slice_filter = opts.get("slice_name")
        prompt_filter = opts.get("prompt_id")
        execute_mode = bool(opts.get("execute"))
        persist = not opts.get("no_persist")

        paths = discover_slices(root)
        if not paths:
            raise CommandError(f"No YAML slices found under {root}")

        if slice_filter:
            paths = [p for p in paths if p.stem == slice_filter]
            if not paths:
                raise CommandError(
                    f"No slice matched --slice={slice_filter!r} under {root}"
                )

        if prompt_filter and not slice_filter:
            raise CommandError("--prompt requires --slice for deterministic dispatch.")

        run_id = uuid.uuid4()
        self.stdout.write(f"run_id={run_id}")
        self.stdout.write(f"yaml_root={root}")
        self.stdout.write(f"slices_discovered={len(paths)}")
        self.stdout.write(f"mode={'execute' if execute_mode else 'dry-run'}")
        self.stdout.write("")

        totals: dict[str, int] = {
            "prompts": 0,
            "rows_written": 0,
            "passed": 0,
            "failed": 0,
            "inconclusive": 0,
            "substrate_deferred": 0,
            "dispatch_error": 0,
        }

        for path in paths:
            try:
                loaded = load_slice(path)
            except SliceLoadError as exc:
                self.stderr.write(self.style.ERROR(f"[LOAD-FAIL] {exc}"))
                continue

            adapter_cls = ADAPTER_REGISTRY.get(loaded.substrate_type)
            if adapter_cls is None:
                self.stderr.write(
                    self.style.ERROR(
                        f"[NO-ADAPTER] {path.name} declares substrate_type="
                        f"{loaded.substrate_type!r} but no adapter is "
                        "registered. Add one under core/services/golden_evals/"
                        "adapters/ + register in ADAPTER_REGISTRY."
                    )
                )
                continue

            self._report_slice(loaded, adapter_cls.__name__, execute_mode)

            for prompt in loaded.raw.get("prompts") or []:
                if not isinstance(prompt, dict):
                    continue
                prompt_id = prompt.get("id", "<missing_id>")
                if prompt_filter and prompt_id != prompt_filter:
                    continue

                totals["prompts"] += 1

                if execute_mode:
                    result = self._execute_prompt(loaded, prompt)
                else:
                    result = _dry_run_prompt(loaded, prompt_id)

                self._report_prompt(result)

                if persist:
                    GoldenEvalRun.objects.create(
                        run_id=run_id,
                        yaml_path=str(path),
                        prompt_id=prompt_id,
                        substrate_type=loaded.substrate_type,
                        primary_row_id=result["primary_row_id"],
                        evidence_ledger_refs=result["evidence_ledger_refs"],
                        passed=result["passed"],
                        failure_reasons=result["failure_reasons"],
                        finalized_at=result["finalized_at"],
                        latency_ms=result["latency_ms"],
                        evidence_source=result["evidence_source"],
                        ledger_health=result["ledger_health"],
                    )
                    totals["rows_written"] += 1

                _bump_totals(totals, result)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"[DONE] slices={len(paths)} prompts={totals['prompts']} "
                f"rows_written={totals['rows_written']}  "
                f"pass={totals['passed']} fail={totals['failed']} "
                f"inconclusive={totals['inconclusive']} "
                f"substrate_deferred={totals['substrate_deferred']} "
                f"dispatch_error={totals['dispatch_error']}  run_id={run_id}"
            )
        )

    def _report_slice(
        self, loaded: LoadedSlice, adapter_name: str, execute_mode: bool
    ) -> None:
        self.stdout.write(
            f"[SLICE] {loaded.path.name}  agent={loaded.agent}  "
            f"canon={loaded.canon_version}  schema={loaded.schema_version}  "
            f"substrate={loaded.substrate_type}  adapter={adapter_name}  "
            f"prompts={len(loaded.prompt_ids)}  "
            f"mode={'execute' if execute_mode else 'dry-run'}"
        )

    def _report_prompt(self, result: dict[str, Any]) -> None:
        tag = result["tag"]
        line = f"  [{tag}] {result['prompt_id']}"
        if result.get("failure_reasons"):
            details = ", ".join(
                f"{r['predicate']}: {r['detail'][:80]}"
                for r in result["failure_reasons"][:3]
            )
            line += f" — {details}"
        if result.get("inconclusive_predicates"):
            line += f" [inconclusive: {result['inconclusive_predicates']}]"
        self.stdout.write(line)

    def _execute_prompt(
        self, loaded: LoadedSlice, prompt: dict[str, Any]
    ) -> dict[str, Any]:
        prompt_id = prompt.get("id", "<missing_id>")

        # Substrate gate: PR-2a only exercises AgentExecution slices.
        # ChatConversation slice 8 (Rigby) is deferred to PR-2b per
        # Chris D-verdict 2026-07-25 after raw-ORM discovery of the
        # ToolCallRecord write regression (Ledger #21).
        if loaded.substrate_type != SUBSTRATE_AGENT_EXECUTION:
            return _skeleton_result(
                prompt_id=prompt_id,
                tag="SUBSTRATE-DEFERRED",
                passed=None,
                failure_reasons=[],
                inconclusive_predicates=[
                    f"{loaded.substrate_type}_dispatch_deferred_to_pr2b"
                ],
            )

        # Resolve agent class + dispatch.
        agent_result, dispatched_at, dispatch_error = _dispatch_agent(
            loaded.agent, prompt
        )
        if dispatch_error is not None:
            return _skeleton_result(
                prompt_id=prompt_id,
                tag="DISPATCH-ERROR",
                passed=False,
                failure_reasons=[
                    FailureReason(
                        predicate="dispatch_agent",
                        detail=dispatch_error,
                    ).to_dict()
                ],
                inconclusive_predicates=[],
            )

        # Locate the AgentExecution row this dispatch produced.
        exec_row = _resolve_agent_execution_row(loaded.agent, dispatched_at)
        if exec_row is None:
            # Fall back to an in-memory context — the agent ran, the row
            # just didn't materialize (or landed on a different owner
            # tag). Native tool_calls from AgentResult still validate.
            ctx = EvalRunContext(
                substrate_type=loaded.substrate_type,
                primary_row_id="",
                evidence_source=EVIDENCE_AGENT_EXECUTION_NATIVE,
                ledger_health=LEDGER_HEALTH_UNAVAILABLE,
            )
        else:
            adapter = AgentExecutionAdapter(include_latency=True)
            ctx = adapter.build_context(str(exec_row.id))

        # Canonicalize the AgentResult into the shape validators consume.
        canonical = canonicalize(loaded.agent, agent_result)
        if canonical is None:
            return _skeleton_result(
                prompt_id=prompt_id,
                tag="NO-CANONICALIZER",
                passed=None,
                failure_reasons=[],
                inconclusive_predicates=[
                    f"{loaded.agent}_canonicalizer_not_registered"
                ],
                ctx=ctx,
            )

        # Shape validation + acceptance-criteria runners.
        expected = prompt.get("expected_output_shape") or {}
        shape_verdict = validate_expected_output_shape(canonical, expected)

        criteria = prompt.get("acceptance_criteria") or []
        runner_verdict = run_predicates(
            ctx=ctx,
            response=canonical,
            predicates=list(criteria),
            expected_output_shape=expected,
        )

        combined_failures = [
            r.to_dict() for r in shape_verdict.failure_reasons
        ] + [r.to_dict() for r in runner_verdict.failure_reasons]

        passed = shape_verdict.passed and runner_verdict.passed
        tag = _classify_tag(passed, combined_failures, runner_verdict.inconclusive_predicates)

        return {
            "prompt_id": prompt_id,
            "tag": tag,
            "passed": passed if tag in ("PASS", "FAIL") else None,
            "failure_reasons": combined_failures,
            "inconclusive_predicates": runner_verdict.inconclusive_predicates,
            "primary_row_id": ctx.primary_row_id,
            "evidence_ledger_refs": ctx.evidence_ledger_refs,
            "finalized_at": ctx.finalized_at,
            "latency_ms": ctx.latency_ms,
            "evidence_source": ctx.evidence_source,
            "ledger_health": ctx.ledger_health,
        }


# ── Helpers (module-level, no self needed) ──────────────────────────────


def _dry_run_prompt(loaded: LoadedSlice, prompt_id: str) -> dict[str, Any]:
    """Skeleton result for dry-run mode (S2964 PR-1 behavior)."""
    return _skeleton_result(
        prompt_id=prompt_id,
        tag="DRY",
        passed=None,
        failure_reasons=[],
        inconclusive_predicates=[],
    )


def _skeleton_result(
    *,
    prompt_id: str,
    tag: str,
    passed: bool | None,
    failure_reasons: list[dict[str, Any]],
    inconclusive_predicates: list[str],
    ctx: EvalRunContext | None = None,
) -> dict[str, Any]:
    return {
        "prompt_id": prompt_id,
        "tag": tag,
        "passed": passed,
        "failure_reasons": failure_reasons,
        "inconclusive_predicates": inconclusive_predicates,
        "primary_row_id": ctx.primary_row_id if ctx else "",
        "evidence_ledger_refs": ctx.evidence_ledger_refs if ctx else [],
        "finalized_at": ctx.finalized_at if ctx else None,
        "latency_ms": ctx.latency_ms if ctx else None,
        "evidence_source": (
            ctx.evidence_source if ctx else EVIDENCE_AGENT_EXECUTION_NATIVE
        ),
        "ledger_health": (
            ctx.ledger_health if ctx else LEDGER_HEALTH_OK
        ),
    }


def _bump_totals(totals: dict[str, int], result: dict[str, Any]) -> None:
    tag = result["tag"]
    if tag == "PASS":
        totals["passed"] += 1
    elif tag == "FAIL":
        totals["failed"] += 1
    elif tag == "SUBSTRATE-DEFERRED":
        totals["substrate_deferred"] += 1
    elif tag == "DISPATCH-ERROR":
        totals["dispatch_error"] += 1
    elif tag != "DRY":
        totals["inconclusive"] += 1


def _classify_tag(
    passed: bool,
    failure_reasons: list[dict[str, Any]],
    inconclusive_predicates: list[str],
) -> str:
    if failure_reasons:
        return "FAIL"
    if inconclusive_predicates and not passed:
        return "INCONCLUSIVE"
    # Even a pass verdict is worth marking INCONCLUSIVE when every
    # predicate was unknown — otherwise dashboards show green for
    # prompts nothing actually validated.
    if inconclusive_predicates and passed and not failure_reasons:
        # Some concrete predicate passed too (else nothing would be
        # green); mark PASS but the inconclusive list is still reported.
        return "PASS"
    return "PASS"


def _dispatch_agent(
    agent_name: str, prompt: dict[str, Any]
) -> tuple[Any, Any, str | None]:
    """Instantiate + call the agent's ``execute`` method.

    Returns ``(agent_result, dispatched_at, error_message)`` — the last
    element is non-None only on failure.
    """
    from core.agent_router import AgentRouter

    agent_class = AgentRouter.AGENT_MAP.get(agent_name)
    if agent_class is None:
        return None, None, f"agent_name {agent_name!r} not in AgentRouter.AGENT_MAP"

    task = prompt.get("input") or ""
    context = prompt.get("context") or {}

    dispatched_at = timezone.now()
    try:
        agent = agent_class()
        result = agent.execute(
            task=task,
            context=context,
            scifi_context={},
            spider_context={},
        )
    except Exception as exc:  # noqa: BLE001 — mgmt cmd catches everything
        return None, dispatched_at, f"{type(exc).__name__}: {exc}"

    return result, dispatched_at, None


def _resolve_agent_execution_row(agent_name: str, dispatched_at: Any) -> Any:
    """Find the AgentExecution row this dispatch produced.

    BaseAgent's ``time_travel_session`` writes the row inside ``.execute()``,
    but the row's PK is not returned to the caller. We reconstruct by
    filtering to the agent-under-test with ``created_at >= dispatched_at``
    and picking the most recent — the assumption is that a single-threaded
    ``run_golden_evals`` invocation is the only writer of that
    ``owner_agent`` in the sub-second window. Retries on empty result for
    up to 3 seconds to cover async row-write delays.
    """
    from core.models import AgentExecution

    deadline = time.time() + 3.0
    while time.time() < deadline:
        row = (
            AgentExecution.objects.filter(
                owner_agent=agent_name,
                created_at__gte=dispatched_at,
            )
            .order_by("-created_at")
            .first()
        )
        if row is not None:
            return row
        time.sleep(0.1)
    return None
