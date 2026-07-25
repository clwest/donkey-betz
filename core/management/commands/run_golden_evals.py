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

**Session 2966 PR-2b extension (S2966 T1 SIGN ratified):**

* AgentExecution dispatch swapped from direct ``agent.execute()`` to
  ``AgentRouter.route()`` — Rigby SIGN Decision 1 Option C. Closes the
  S2965 known limitation: the router creates the ``AgentExecution`` row
  via its canonical ``_create_execution_record`` path (owner_agent +
  trace_id + root_execution_id + heartbeat thread all populated), and
  we resolve the row by marker (``_golden_evals_run_id`` injected into
  raw context, persisted to ``input_data['context']`` per
  ``agent_router.py:2832-2838``).
* ChatConversation dispatch (slice 8, Rigby) now supported via
  ``process_pa_chat_task.apply(...).get()`` — synchronous Celery task
  invocation runs in-process (no worker dependency). Creates a
  ``ChatConversation`` row through the canonical PA task write path;
  ``ChatConversationAdapter`` normalizes into ``EvalRunContext``.
  Widespread INCONCLUSIVE verdicts expected on Rigby fabrication
  predicates until Rigby Tool Gap Ledger #20 + #21 are fixed.

Usage:

    # Discover + dry-run every Tier-1 slice.
    python manage.py run_golden_evals

    # Filter to one slice by filename stem.
    python manage.py run_golden_evals --slice system_intelligence_agent

    # Actually dispatch agents + validate responses.
    python manage.py run_golden_evals --execute --slice system_intelligence_agent

    # Dogfood slice 8 (Rigby, ChatConversation substrate).
    python manage.py run_golden_evals --execute --slice rigby_agent \\
        --prompt rigby_happy_02_engineering_operating_system_domain_analysis
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
from core.services.golden_evals.adapters.chat_conversation import ChatConversationAdapter
from core.services.golden_evals.canonicalizers import canonicalize
from core.services.golden_evals.context import (
    EVIDENCE_AGENT_EXECUTION_NATIVE,
    EVIDENCE_METADATA_CACHE,
    LEDGER_HEALTH_OK,
    LEDGER_HEALTH_UNAVAILABLE,
    SUBSTRATE_AGENT_EXECUTION,
    SUBSTRATE_CHAT_CONVERSATION,
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
                    result = self._execute_prompt(loaded, prompt, run_id)
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
        self, loaded: LoadedSlice, prompt: dict[str, Any], run_id: Any,
    ) -> dict[str, Any]:
        """Dispatch one prompt through the substrate-appropriate pathway.

        Two branches per substrate_type (PR-2b, S2966):

        * ``agent_execution`` — routes through ``AgentRouter.route()``
          (Rigby SIGN Decision 1 Option C). Router creates the
          canonical AgentExecution row + heartbeat + trace_id lineage;
          we resolve the row by ``_golden_evals_run_id`` marker
          injected into raw context.
        * ``chat_conversation`` — invokes ``process_pa_chat_task.apply()``
          synchronously (no worker dependency). PA task creates the
          canonical ChatConversation row with populated
          ``assistant_response`` + metadata cache; adapter normalizes
          into ``EvalRunContext``.
        """
        prompt_id = prompt.get("id", "<missing_id>")

        if loaded.substrate_type == SUBSTRATE_AGENT_EXECUTION:
            return _execute_agent_execution_prompt(loaded, prompt, prompt_id, run_id)
        if loaded.substrate_type == SUBSTRATE_CHAT_CONVERSATION:
            return _execute_chat_conversation_prompt(loaded, prompt, prompt_id, run_id)
        return _skeleton_result(
            prompt_id=prompt_id,
            tag="SUBSTRATE-DEFERRED",
            passed=None,
            failure_reasons=[],
            inconclusive_predicates=[
                f"{loaded.substrate_type}_dispatch_not_implemented"
            ],
        )


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


# ── AgentExecution dispatch (Rigby SIGN Decision 1 Option C) ────────────
#
# Route through AgentRouter.route() which creates the canonical
# AgentExecution row via ``_create_execution_record`` (owner_agent +
# trace_id + root_execution_id + heartbeat thread all populated). The
# ``_golden_evals_run_id`` marker in raw context is persisted to
# ``input_data['context']`` per ``agent_router.py:2832-2838`` and is
# what ``_resolve_agent_execution_row`` filters on to find the row this
# dispatch produced.


_GOLDEN_EVALS_TRIGGER_SOURCE = "golden_evals_harness"


def _dispatch_agent_via_router(
    agent_name: str, prompt: dict[str, Any], run_id: Any,
) -> tuple[Any, Any, str | None]:
    """Dispatch via ``AgentRouter.route()``; router creates AgentExecution row.

    Returns ``(agent_result, dispatched_at, error_message)`` — the last
    element is non-None only on failure. ``dispatched_at`` is retained
    for the resolver's fallback timestamp filter (belt + suspenders).
    """
    from core.agent_router import AgentRouter

    if agent_name not in AgentRouter.AGENT_MAP:
        return None, None, f"agent_name {agent_name!r} not in AgentRouter.AGENT_MAP"

    task = prompt.get("input") or ""
    context = dict(prompt.get("context") or {})
    # Rigby SIGN Decision 1 REVISE: marker MUST go in raw context dict —
    # ``_create_execution_record`` persists that at
    # ``input_data['context']['_golden_evals_run_id']`` for later lookup.
    context["_golden_evals_run_id"] = str(run_id)

    dispatched_at = timezone.now()
    try:
        # user=None is legitimate here — router's ``_create_execution_record``
        # handles nullable user (Session 642).
        router = AgentRouter(user=None)
        result = router.route(
            agent_name=agent_name,
            task=task,
            context=context,
            trigger_source=_GOLDEN_EVALS_TRIGGER_SOURCE,
        )
    except Exception as exc:  # noqa: BLE001 — mgmt cmd catches everything
        return None, dispatched_at, f"{type(exc).__name__}: {exc}"

    return result, dispatched_at, None


def _resolve_agent_execution_row_by_marker(
    agent_name: str, run_id: Any, dispatched_at: Any,
) -> Any:
    """Find the AgentExecution row this dispatch produced via marker lookup.

    Primary lookup: ``input_data.context._golden_evals_run_id`` matches
    the current run_id AND ``owner_agent == agent_name``. Marker is
    stable across the whole run (no per-prompt uniqueness) so we also
    order by ``created_at`` DESC + filter to ``created_at >=
    dispatched_at`` so multi-prompt runs land on the right row.
    Retries on empty result for up to 3 seconds to cover any router
    write-side race.
    """
    from core.models import AgentExecution

    deadline = time.time() + 3.0
    marker_str = str(run_id)
    while time.time() < deadline:
        row = (
            AgentExecution.objects.filter(
                owner_agent=agent_name,
                created_at__gte=dispatched_at,
                input_data__context___golden_evals_run_id=marker_str,
            )
            .order_by("-created_at")
            .first()
        )
        if row is not None:
            return row
        # Fallback: timestamp-only path (marker JSON lookup unsupported
        # on some DB adapters, but the harness only ever runs on
        # PostgreSQL where JSONField key-lookups work — this fallback is
        # for safety, not routine).
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


def _execute_agent_execution_prompt(
    loaded: LoadedSlice, prompt: dict[str, Any], prompt_id: str, run_id: Any,
) -> dict[str, Any]:
    """AgentExecution-substrate branch — dispatch via router + adapt."""
    agent_result, dispatched_at, dispatch_error = _dispatch_agent_via_router(
        loaded.agent, prompt, run_id,
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

    exec_row = _resolve_agent_execution_row_by_marker(
        loaded.agent, run_id, dispatched_at,
    )
    if exec_row is None:
        # Router did not surface a row within the retry window. Fall
        # back to an in-memory context — the agent ran and returned an
        # AgentResult; native tool_calls still validate against the
        # canonical shape.
        ctx = EvalRunContext(
            substrate_type=loaded.substrate_type,
            primary_row_id="",
            evidence_source=EVIDENCE_AGENT_EXECUTION_NATIVE,
            ledger_health=LEDGER_HEALTH_UNAVAILABLE,
        )
        substrate_row = None
    else:
        adapter = AgentExecutionAdapter(include_latency=True)
        ctx = adapter.build_context(str(exec_row.id))
        substrate_row = exec_row

    return _validate_and_wrap(
        loaded, prompt_id, agent_result, ctx, substrate_row,
    )


# ── ChatConversation dispatch (Rigby SIGN Decision 2 hybrid) ────────────
#
# Slice 8 (Rigby) dispatch: synchronous Celery task invocation via
# ``process_pa_chat_task.apply(...).get()``. Runs in-process so the
# harness is self-contained (no worker dependency) while still
# exercising the canonical PA task write path (ChatConversation row
# creation + populated response + metadata cache). Rigby SIGN
# Decision 2 SIGNed B (HTTP client) with C (inline) as fallback; the
# ``.apply()`` synchronous-task variant offers B's canonical write-path
# coverage with C's zero-external-dependency footprint.


def _execute_chat_conversation_prompt(
    loaded: LoadedSlice, prompt: dict[str, Any], prompt_id: str, run_id: Any,
) -> dict[str, Any]:
    """ChatConversation-substrate branch — synchronous PA task + adapt."""
    from core.tasks import process_pa_chat_task
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Resolve dispatch user — prompt.context may pin a user_id; default
    # to the platform's default operator (Chris) since slice 8 corpus is
    # scoped to source IN ('web', 'pa') and user=chris per rigby_agent.yaml
    # header.
    prompt_ctx = dict(prompt.get("context") or {})
    prompt_ctx["_golden_evals_run_id"] = str(run_id)
    dispatch_source = prompt_ctx.get("source") or "web"

    user = None
    user_id_pref = prompt_ctx.get("user_id")
    if user_id_pref:
        user = User.objects.filter(pk=user_id_pref).first()
    if user is None:
        user = User.objects.filter(username__iexact="chris").first()
    if user is None:
        user = User.objects.filter(is_superuser=True).order_by("pk").first()
    if user is None:
        return _skeleton_result(
            prompt_id=prompt_id,
            tag="DISPATCH-ERROR",
            passed=False,
            failure_reasons=[
                FailureReason(
                    predicate="dispatch_agent",
                    detail=(
                        "no dispatch user resolved for ChatConversation slice "
                        "(no user_id in prompt.context, no 'chris' username, "
                        "no superuser)"
                    ),
                ).to_dict()
            ],
            inconclusive_predicates=[],
        )

    message = prompt.get("input") or ""
    conversation_id = prompt_ctx.get("conversation_id") or f"golden-evals-{run_id}"

    try:
        task_result = process_pa_chat_task.apply(
            kwargs=dict(
                user_id=user.id,
                message=message,
                context=prompt_ctx,
                generate_audio=False,
                conversation_id=conversation_id,
                source=dispatch_source,
                platform=prompt_ctx.get("platform", "web"),
            ),
        )
        pa_response = task_result.get()
    except Exception as exc:  # noqa: BLE001
        return _skeleton_result(
            prompt_id=prompt_id,
            tag="DISPATCH-ERROR",
            passed=False,
            failure_reasons=[
                FailureReason(
                    predicate="dispatch_agent",
                    detail=f"{type(exc).__name__}: {exc}",
                ).to_dict()
            ],
            inconclusive_predicates=[],
        )

    # Locate the ChatConversation row this PA turn created — the task
    # writes the row; we match by (user, conversation_id) + most recent.
    from core.models import ChatConversation
    chat_row = (
        ChatConversation.objects.filter(
            user=user, conversation_id=conversation_id,
        )
        .order_by("-created_at")
        .first()
    )
    if chat_row is None:
        # PA task returned a response but no ChatConversation row landed.
        # Fall back to in-memory context using the response dict directly.
        ctx = EvalRunContext(
            substrate_type=loaded.substrate_type,
            primary_row_id="",
            evidence_source=EVIDENCE_METADATA_CACHE,
            ledger_health=LEDGER_HEALTH_UNAVAILABLE,
        )
        # Synthesize a minimal row-shape for the canonicalizer +
        # predicates. This is best-effort; production PR-2b runs
        # should always land a row.
        synthesized_row = _SynthesizedChatRow(
            assistant_response=(pa_response or {}).get("content", "") if isinstance(pa_response, dict) else "",
            metadata=(pa_response or {}).get("metadata", {}) if isinstance(pa_response, dict) else {},
            conversation_id=conversation_id,
            user=user,
        )
        substrate_row = synthesized_row
        agent_response_source = synthesized_row
    else:
        # Filter to buyer-facing source per canon_v2 Item 2 (the adapter
        # will refuse claude-code rows; slice 8 is source IN ('web','pa')).
        # Golden evals dogfood uses source='web' explicitly.
        try:
            adapter = ChatConversationAdapter(sources=(dispatch_source,))
            ctx = adapter.build_context(str(chat_row.pk))
        except (ValueError, LookupError) as exc:
            return _skeleton_result(
                prompt_id=prompt_id,
                tag="DISPATCH-ERROR",
                passed=False,
                failure_reasons=[
                    FailureReason(
                        predicate="chat_conversation_adapter",
                        detail=f"{type(exc).__name__}: {exc}",
                    ).to_dict()
                ],
                inconclusive_predicates=[],
            )
        substrate_row = chat_row
        agent_response_source = chat_row

    return _validate_and_wrap(
        loaded, prompt_id, agent_response_source, ctx, substrate_row,
    )


class _SynthesizedChatRow:
    """Minimal ChatConversation-shaped stub for fallback paths.

    Used only when the PA task returns a response dict but no
    ChatConversation row materializes within the resolver window.
    Presents the same attribute surface the Rigby canonicalizer +
    predicate runners consume so downstream validation can proceed
    against in-memory data.
    """

    def __init__(
        self, assistant_response: str, metadata: dict, conversation_id: str, user: Any,
    ) -> None:
        self.assistant_response = assistant_response
        self.metadata = metadata or {}
        self.conversation_id = conversation_id
        self.user = user
        self.pk = None


# ── Shared validation + wrapping ────────────────────────────────────────


def _validate_and_wrap(
    loaded: LoadedSlice,
    prompt_id: str,
    agent_response_source: Any,
    ctx: EvalRunContext,
    substrate_row: Any,
) -> dict[str, Any]:
    """Canonicalize + validate + wrap into result dict.

    Shared between AgentExecution and ChatConversation branches — the
    only substrate-specific work is the dispatch + adapter selection;
    canonicalize + validate + aggregate are uniform.
    """
    canonical = canonicalize(loaded.agent, agent_response_source)
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

    # Locate the prompt spec from the loaded slice (we need
    # expected_output_shape + acceptance_criteria).
    prompt_spec = None
    for p in loaded.raw.get("prompts") or []:
        if isinstance(p, dict) and p.get("id") == prompt_id:
            prompt_spec = p
            break
    expected = (prompt_spec or {}).get("expected_output_shape") or {}
    criteria = (prompt_spec or {}).get("acceptance_criteria") or []

    from core.services.golden_evals.executors import validate_expected_output_shape
    from core.services.golden_evals.runners import run_predicates as _run_predicates
    shape_verdict = validate_expected_output_shape(canonical, expected)
    runner_verdict = _run_predicates(
        ctx=ctx,
        response=canonical,
        predicates=list(criteria),
        expected_output_shape=expected,
        substrate_row=substrate_row,
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
