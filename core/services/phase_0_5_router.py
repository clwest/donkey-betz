"""Phase-0.5 advisory-only dogfood router.

Per S2823 constitutional package (B1 harvest plan + B3 abstain policy + B2
router scaffolding, all Chris D-RATIFIED). Router runs before
`search_embeddings()` at `td_handlers_ops.py:5905` (kb_tool.semantic_search),
predicts a family + categorical confidence via classifier_a, and LOGS the
decision plus abstain outcome. It NEVER alters retrieval behavior (Chris R1
advisory-only). Envelope gets an additive `_router_advisory` v1 field when
the feature flag is on; byte-identical when off.

Constitutional constraints (Chris D-verdict §15 R1-R7):

- R1: advisory-only; `_parallel_both` ALWAYS null in Phase-0.5
- R2: measurement window = CANONICAL UNIT OF OBSERVATION
- R3: single instrumentation surface = kb_tool.semantic_search only
- R4: JSONL = SoT, Django model = mirror, event_id idempotency, divergence
     raises integrity event (never silent reconciliation)
- R5: `_router_advisory` v1, categorical confidence only, additive
     non-breaking, matches live handler `chunks` key
- R6: runtime checks only on observable signals; T4/T5 downgrade to Class D
     if proxies unavailable
- R7: any implementation weakening returns through SIGN + new D-verdict

S2824 Rigby cycle-2 refinements applied:

- Q4: log_decision() fires in `finally` even if search_embeddings raises;
     retrieval_error + retrieval_exception_type fields added
- Q5: integrity events written to separate JSONL file (non-recursion guard)
- Q6-A: window_start / window_end events written to durable log
- Q6-B: evidence_integrity_stop_<trigger>_<ts>.md markdown writer + advisory
       surface via `_router_advisory.integrity_stop`
"""
from __future__ import annotations

import json
import logging
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.conf import settings

from core.services.phase_0_5_classifier_a import ClassifierAResult, classify_a

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Log locations (JSONL = source of truth per R4 + Q5 non-recursion split)
# ---------------------------------------------------------------------------

_LOGS_DIR = Path(settings.BASE_DIR) / "logs"
ROUTER_LOG_PATH = _LOGS_DIR / "phase_0_5_router.jsonl"
INTEGRITY_LOG_PATH = _LOGS_DIR / "phase_0_5_integrity_events.jsonl"
INTEGRITY_STOP_DOC_DIR = (
    Path(settings.BASE_DIR)
    / "docs"
    / "research"
    / "discovery_layer"
    / "PHASE_0_5"
    / "integrity_stops"
)


# ---------------------------------------------------------------------------
# Row-type discriminators for the router-log JSONL
# ---------------------------------------------------------------------------

ROW_TYPE_ROUTER_DECISION = "router_decision"
ROW_TYPE_WINDOW_START = "window_start"
ROW_TYPE_WINDOW_END = "window_end"


# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouterDecision:
    """Result of one router.classify() call — bound to a measurement window.

    Categorical confidence only per R4. NO numeric confidence field anywhere;
    attempting to add one is a §12 T1 integrity-stop trigger.
    """
    event_id: str
    measurement_window_id: str
    measurement_window_type: str
    predicted_family: str | None
    confidence_categorical: str
    matched_rules: list[str]
    abstain_reason: str | None
    abstain_option: str | None
    clarify_context_type: str | None
    suggested_alternative_substrate: str | None
    integrity_stop_trigger: str | None = None
    integrity_stop_reason: str | None = None


@dataclass
class _WindowState:
    """Per-window mutable counters + abort flag."""
    window_id: str
    window_type: str
    routed_count: int = 0
    ambiguous_count: int = 0
    unclassifiable_count: int = 0
    context_needed_count: int = 0
    clarify_count: int = 0
    operator_override_count: int = 0
    aborted: bool = False
    abort_trigger: str | None = None
    abort_reason: str | None = None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------


class Phase0_5Router:
    """Advisory-only router. Never alters retrieval behavior (Chris R1).

    Constitutional discipline: this module ONLY writes to durable logs +
    envelope metadata. It does not touch `search_embeddings` args, does not
    reorder chunks, does not fuse substrates.
    """

    # Minimum-N gate for Class B/C triggers per B3 §7 + design §12.
    MIN_N_FOR_TRIGGERS = 20
    # Abstain-rate cap: AMBIGUOUS + UNCLASSIFIABLE > 30% of routed within window.
    ABSTAIN_RATE_CAP = 0.30
    # Operator-override cap: router_recommendation_followed=False > 50%.
    OPERATOR_OVERRIDE_CAP = 0.50

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._windows: dict[str, _WindowState] = {}
        self._active_window_id: str | None = None

    # ------------------------------------------------------------------
    # Measurement window lifecycle
    # ------------------------------------------------------------------

    def start_measurement_window(
        self,
        window_type: str | None = None,
        window_id: str | None = None,
    ) -> str:
        """Mint or accept a measurement window; write window_start event.

        Per R2: measurement window = CANONICAL UNIT OF OBSERVATION.
        """
        wtype = (
            window_type
            or getattr(settings, "PHASE_0_5_MEASUREMENT_WINDOW", "session")
        )
        wid = window_id or f"win-{uuid.uuid4().hex[:16]}"
        with self._lock:
            self._windows[wid] = _WindowState(window_id=wid, window_type=wtype)
            self._active_window_id = wid
        self._write_router_log_row({
            "event_id": f"WSTART-{wid}",
            "row_type": ROW_TYPE_WINDOW_START,
            "ts": _utc_iso(),
            "measurement_window_id": wid,
            "measurement_window_type": wtype,
        })
        return wid

    def end_measurement_window(
        self,
        window_id: str,
        reason: str = "boundary",
    ) -> None:
        """Write window_end event with counter snapshot."""
        with self._lock:
            state = self._windows.pop(window_id, None)
            if self._active_window_id == window_id:
                self._active_window_id = None
        if state is None:
            return
        self._write_router_log_row({
            "event_id": f"WEND-{window_id}",
            "row_type": ROW_TYPE_WINDOW_END,
            "ts": _utc_iso(),
            "measurement_window_id": window_id,
            "measurement_window_type": state.window_type,
            "reason": reason,
            "counters": {
                "routed_count": state.routed_count,
                "ambiguous_count": state.ambiguous_count,
                "unclassifiable_count": state.unclassifiable_count,
                "context_needed_count": state.context_needed_count,
                "clarify_count": state.clarify_count,
                "operator_override_count": state.operator_override_count,
                "aborted": state.aborted,
                "abort_trigger": state.abort_trigger,
            },
        })

    def _get_or_start_active_window(self) -> _WindowState:
        with self._lock:
            wid = self._active_window_id
            if wid is not None and wid in self._windows:
                return self._windows[wid]
        # No active window — mint a default session-scoped one.
        new_wid = self.start_measurement_window()
        return self._windows[new_wid]

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(self, query: str) -> RouterDecision:
        """Classify a query against the active measurement window.

        Returns advisory-only RouterDecision. If the window is in an
        aborted state (§12 integrity stop), returns a decision with
        integrity_stop_trigger populated and abstain_reason set —
        callers surface this via `_router_advisory.integrity_stop`.
        """
        state = self._get_or_start_active_window()

        if state.aborted:
            return RouterDecision(
                event_id=f"evt-{uuid.uuid4().hex[:16]}",
                measurement_window_id=state.window_id,
                measurement_window_type=state.window_type,
                predicted_family=None,
                confidence_categorical="LOW",
                matched_rules=[],
                abstain_reason=f"INTEGRITY_STOP_{state.abort_trigger}",
                abstain_option=None,
                clarify_context_type=None,
                suggested_alternative_substrate=None,
                integrity_stop_trigger=state.abort_trigger,
                integrity_stop_reason=state.abort_reason,
            )

        result = classify_a(query)
        abstain_reason, abstain_option, clarify_ctx = _map_classifier_to_abstain(result)

        with self._lock:
            state.routed_count += 1
            if abstain_reason == "AMBIGUOUS":
                state.ambiguous_count += 1
            elif abstain_reason == "UNCLASSIFIABLE":
                state.unclassifiable_count += 1
            elif abstain_reason == "CONTEXT_NEEDED":
                state.context_needed_count += 1
            if abstain_option == "(a)":
                state.clarify_count += 1

        return RouterDecision(
            event_id=f"evt-{uuid.uuid4().hex[:16]}",
            measurement_window_id=state.window_id,
            measurement_window_type=state.window_type,
            predicted_family=(
                result.family
                if abstain_reason is None
                else None
            ),
            confidence_categorical=result.confidence,
            matched_rules=list(result.matched_rules),
            abstain_reason=abstain_reason,
            abstain_option=abstain_option,
            clarify_context_type=clarify_ctx,
            suggested_alternative_substrate=_suggest_substrate(result, abstain_reason),
        )

    # ------------------------------------------------------------------
    # Persistence (R4 discipline)
    # ------------------------------------------------------------------

    def log_decision(
        self,
        query: str,
        decision: RouterDecision,
        chosen_substrate: str,
        actual_substrate: str,
        retrieval_count: int,
        retrieval_error: str | None = None,
        retrieval_exception_type: str | None = None,
        operator_style: str = "unknown",
        session: int | None = None,
        router_recommendation_followed: bool | None = None,
    ) -> None:
        """Write router-decision row to JSONL (SoT) + Django model mirror.

        Guaranteed to fire in the caller's `finally` block per Rigby S2824
        Q4 fix. If retrieval raised, `retrieval_error` +
        `retrieval_exception_type` will be populated and `retrieval_count`
        will be 0.
        """
        row = {
            "event_id": decision.event_id,
            "row_type": ROW_TYPE_ROUTER_DECISION,
            "ts": _utc_iso(),
            "session": session,
            "measurement_window_id": decision.measurement_window_id,
            "measurement_window_type": decision.measurement_window_type,
            "operator_style": operator_style,
            "original_query": query,
            "predicted_family": decision.predicted_family,
            "confidence_categorical": decision.confidence_categorical,
            "matched_rules": decision.matched_rules,
            "abstain_reason": decision.abstain_reason,
            "abstain_option": decision.abstain_option,
            "clarify_context_type": decision.clarify_context_type,
            "chosen_substrate": chosen_substrate,
            "actual_substrate": actual_substrate,
            "retrieval_count": retrieval_count,
            "retrieval_error": retrieval_error,
            "retrieval_exception_type": retrieval_exception_type,
            "router_recommendation_followed": router_recommendation_followed,
            "integrity_stop_trigger": decision.integrity_stop_trigger,
            "operator_correction": None,
            "final_successful_substrate": None,
        }

        self._write_router_log_row(row)
        self._mirror_to_model(row)

        # Post-log trigger evaluation (Class B window-level, min-N gated).
        self._evaluate_window_triggers(decision.measurement_window_id)

    def _write_router_log_row(self, row: dict[str, Any]) -> None:
        """Append one row to router JSONL. Atomic via file lock."""
        ROUTER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with ROUTER_LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, default=str) + "\n")

    def _mirror_to_model(self, row: dict[str, Any]) -> None:
        """Best-effort mirror to Phase0_5RouterEvent. JSONL is SoT.

        Divergence between JSONL and model raises an integrity event via a
        separate log path (per Rigby S2824 Q5 non-recursion guard).
        """
        try:
            # Lazy import to avoid circular deps during Django app loading.
            from persistence.models import Phase0_5RouterEvent  # type: ignore
        except Exception:
            # Model not migrated yet (fresh checkout / test setup). JSONL
            # remains SoT; no integrity event.
            return

        try:
            Phase0_5RouterEvent.objects.update_or_create(
                event_id=row["event_id"],
                defaults={
                    "ts": row.get("ts") or _utc_iso(),
                    "row_type": row.get("row_type", ROW_TYPE_ROUTER_DECISION),
                    "session": row.get("session"),
                    "measurement_window_id": row.get("measurement_window_id") or "",
                    "measurement_window_type": row.get("measurement_window_type") or "",
                    "operator_style": row.get("operator_style", "unknown"),
                    "original_query": row.get("original_query", "") or "",
                    "predicted_family": row.get("predicted_family"),
                    "confidence_categorical": row.get("confidence_categorical", "") or "",
                    "matched_rules": row.get("matched_rules") or [],
                    "abstain_reason": row.get("abstain_reason"),
                    "abstain_option": row.get("abstain_option"),
                    "clarify_context_type": row.get("clarify_context_type"),
                    "chosen_substrate": row.get("chosen_substrate") or "",
                    "actual_substrate": row.get("actual_substrate") or "",
                    "retrieval_count": row.get("retrieval_count") or 0,
                    "retrieval_error": row.get("retrieval_error"),
                    "retrieval_exception_type": row.get("retrieval_exception_type"),
                    "router_recommendation_followed": row.get(
                        "router_recommendation_followed"
                    ),
                    "integrity_stop_trigger": row.get("integrity_stop_trigger"),
                },
            )
        except Exception as exc:
            self._raise_integrity_event(
                trigger_id="MIRROR_DIVERGENCE",
                reason=(
                    f"Django model mirror save failed for event_id="
                    f"{row.get('event_id')}: {type(exc).__name__}: {exc}"
                ),
                context={"row_event_id": row.get("event_id")},
            )

    # ------------------------------------------------------------------
    # Runtime abort triggers (§12 T1-T5, R6 epistemic-integrity)
    # ------------------------------------------------------------------

    def _evaluate_window_triggers(self, window_id: str) -> None:
        """Run Class B abort triggers on a window after each event.

        Class A (T1 numeric-threshold) is enforced structurally by the
        dataclass + schema — no numeric confidence field exists.

        Class B min-N gate: skip while routed_count < MIN_N_FOR_TRIGGERS.

        Class C (T4/T5) inactive in Phase-0.5 (advisory-only-vs-execution
        boundary; parallel-both is NOT executed).
        """
        state = self._windows.get(window_id)
        if state is None or state.aborted:
            return
        if state.routed_count < self.MIN_N_FOR_TRIGGERS:
            return

        abstain_rate = (
            (state.ambiguous_count + state.unclassifiable_count)
            / state.routed_count
        )
        if abstain_rate > self.ABSTAIN_RATE_CAP:
            self._abort_window(
                window_id=window_id,
                trigger_id="T2",
                reason=(
                    f"abstain_rate={abstain_rate:.3f} exceeds cap "
                    f"{self.ABSTAIN_RATE_CAP} within window "
                    f"(routed_count={state.routed_count})"
                ),
            )
            return

        override_rate = state.operator_override_count / state.routed_count
        if override_rate > self.OPERATOR_OVERRIDE_CAP:
            self._abort_window(
                window_id=window_id,
                trigger_id="T3",
                reason=(
                    f"operator_override_rate={override_rate:.3f} exceeds "
                    f"cap {self.OPERATOR_OVERRIDE_CAP} within window "
                    f"(routed_count={state.routed_count})"
                ),
            )

    def _abort_window(self, window_id: str, trigger_id: str, reason: str) -> None:
        state = self._windows.get(window_id)
        if state is None:
            return
        with self._lock:
            state.aborted = True
            state.abort_trigger = trigger_id
            state.abort_reason = reason
        self._raise_integrity_event(
            trigger_id=trigger_id,
            reason=reason,
            context={
                "measurement_window_id": window_id,
                "measurement_window_type": state.window_type,
                "counters": {
                    "routed_count": state.routed_count,
                    "ambiguous_count": state.ambiguous_count,
                    "unclassifiable_count": state.unclassifiable_count,
                    "context_needed_count": state.context_needed_count,
                    "operator_override_count": state.operator_override_count,
                },
            },
        )

    def _raise_integrity_event(
        self,
        trigger_id: str,
        reason: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Write integrity event to separate JSONL + evidence markdown file.

        Rigby S2824 Q5 refinement: separate log path so this write can
        never recurse back into log_decision(). Rigby S2824 Q6-B: also
        emit `evidence_integrity_stop_<trigger>_<ts>.md` per §12 spec.
        """
        ts = _utc_iso()
        event = {
            "event_id": f"integrity-{uuid.uuid4().hex[:16]}",
            "ts": ts,
            "trigger_id": trigger_id,
            "reason": reason,
            "context": context or {},
        }
        INTEGRITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with INTEGRITY_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, default=str) + "\n")
        logger.error(
            "phase_0_5_router integrity event trigger=%s reason=%s",
            trigger_id,
            reason,
        )
        self._write_integrity_stop_markdown(trigger_id, reason, context or {}, ts)

    def _write_integrity_stop_markdown(
        self,
        trigger_id: str,
        reason: str,
        context: dict[str, Any],
        ts: str,
    ) -> None:
        """Write §12 evidence-integrity-stop record.

        Path: docs/research/discovery_layer/PHASE_0_5/integrity_stops/
        Filename: evidence_integrity_stop_<trigger>_<utc_iso>.md
        """
        INTEGRITY_STOP_DOC_DIR.mkdir(parents=True, exist_ok=True)
        safe_ts = ts.replace(":", "").replace("-", "").replace(".", "_")
        path = (
            INTEGRITY_STOP_DOC_DIR
            / f"evidence_integrity_stop_{trigger_id}_{safe_ts}.md"
        )
        counters = context.get("counters", {})
        body = (
            f"# Evidence-Integrity Stop — {trigger_id}\n\n"
            f"- **Timestamp (UTC):** {ts}\n"
            f"- **Trigger:** {trigger_id}\n"
            f"- **Reason:** {reason}\n"
            f"- **Measurement window:** "
            f"{context.get('measurement_window_id', 'n/a')} "
            f"({context.get('measurement_window_type', 'n/a')})\n"
            f"- **Counter snapshot:** {json.dumps(counters, default=str)}\n"
            f"- **Router state at abort:** disabled for remainder of window\n"
            f"- **Re-enable:** next measurement window boundary "
            f"(per design §12 abort scope)\n"
            f"- **Route back:** Rigby SIGN cycle + Chris D-verdict required "
            f"before router logic changes.\n"
        )
        path.write_text(body, encoding="utf-8")


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_ROUTER_SINGLETON: Phase0_5Router | None = None
_SINGLETON_LOCK = threading.Lock()


def get_router() -> Phase0_5Router:
    """Return the process-local router singleton."""
    global _ROUTER_SINGLETON
    if _ROUTER_SINGLETON is None:
        with _SINGLETON_LOCK:
            if _ROUTER_SINGLETON is None:
                _ROUTER_SINGLETON = Phase0_5Router()
    return _ROUTER_SINGLETON


def reset_router_for_tests() -> None:
    """Reset the singleton for test isolation. NOT for runtime use."""
    global _ROUTER_SINGLETON
    with _SINGLETON_LOCK:
        _ROUTER_SINGLETON = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _map_classifier_to_abstain(
    result: ClassifierAResult,
) -> tuple[str | None, str | None, str | None]:
    """Map classifier_a output to (abstain_reason, abstain_option, clarify_ctx).

    Per B3 §2.2/§2.3/§2.4 + §3.1 categorical routing rules.
    """
    family = result.family
    if family == "AMBIGUOUS":
        # (c) parallel-both is the ratified fallthrough, but NOT executed in
        # Phase-0.5 per §7 CRITICAL SCOPE DISTINCTION — logged as advised.
        return "AMBIGUOUS", "(c)", None
    if family == "UNCLASSIFIABLE":
        return "UNCLASSIFIABLE", "(d)", None
    if family == "CONTEXT_NEEDED":
        return "CONTEXT_NEEDED", "(a)", "operational"
    # LOW confidence with defined family → escalate to (d) no-action per B3
    # §3.1: "LOW confidence is effectively no meaningful signal."
    if result.confidence == "LOW":
        return "UNCLASSIFIABLE", "(d)", None
    return None, None, None


def _suggest_substrate(
    result: ClassifierAResult,
    abstain_reason: str | None,
) -> str | None:
    """Suggest a non-authoritative alternative substrate.

    Advisory-only per Chris R1 — this is NEVER used to alter retrieval; it
    only surfaces via `_router_advisory.suggested_alternative_substrate`.
    """
    if abstain_reason is not None:
        return None
    family = result.family
    if family in {"COUNT", "IDENTITY", "SELF-REFERENCE"}:
        return "lexical"
    if family == "CONCEPTUAL":
        return "semantic"
    return None
