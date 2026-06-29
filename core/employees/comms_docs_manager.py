"""
Documentation Manager shift-report config (Session 1253 PR 4 → PR-A).

Holds the docs-cascade-specific defaults that ``post_shift_report``
takes as kwargs: thread subject, body formatter, extra metadata keys.
Calls ``core.employees.comms.post_shift_report`` underneath — this
module exists to keep job-specific text/templates out of the generic
helper.

See ``docs/EMPLOYEE_OS_PRIMITIVES.md`` for the broader pattern: every
employee job gets its own thin module like this when it wants a
human-tuned shift-report body. The generic default body in
``comms.py`` is the fallback when a job hasn't declared one.
"""

from __future__ import annotations

from typing import Any, Dict

from core.employees import RIGBY
from core.employees.comms import post_shift_report


# ── Documentation-Manager-specific config ────────────────────────────


THREAD_SUBJECT = "Rigby — Documentation Manager"

# Extra summary keys (beyond BASE_METADATA_KEYS in comms.py) that
# docs_manager shift reports carry. None of these are unbounded —
# all are short strings or scalars. Never include error_tail.
EXTRA_METADATA_KEYS: tuple[str, ...] = (
    "drift_count",
    "failed_step",
    "escalation_deliverable_id",
)


def format_body(mission, summary: Dict[str, Any]) -> str:
    """Build the body string per Rigby's PR 4 templates.

    Three terminal branches:
      * certified  — "Docs Manager mission <id> passed. Docs cascade
                       completed in <s>. Drift <N> items observed. No
                       escalation."
      * rejected   — "Docs Manager mission <id> failed at <step>.
                       Escalation deliverable <id> created." (or
                       "No escalation deliverable recorded." if
                       missing)
      * deferred   — "Docs Manager mission <id> deferred. Awaiting
                       follow-up review."
    """
    verdict = summary.get("verdict")
    wall_ms = summary.get("wall_time_ms")
    seconds = (
        f"{wall_ms / 1000:.1f}"
        if isinstance(wall_ms, (int, float))
        else "?"
    )

    if verdict == "certified":
        drift = summary.get("drift_count")
        drift_part = (
            f"Drift {drift} items observed."
            if isinstance(drift, int)
            else "Drift count unavailable."
        )
        return (
            f"Docs Manager mission {mission.id} passed. "
            f"Docs cascade completed in {seconds}s. "
            f"{drift_part} No escalation."
        )

    if verdict == "rejected":
        failed_step = summary.get("failed_step") or "<unknown step>"
        escalation_id = summary.get("escalation_deliverable_id")
        if escalation_id:
            esc_sentence = (
                f"Escalation deliverable {escalation_id} created."
            )
        else:
            esc_sentence = "No escalation deliverable recorded."
        return (
            f"Docs Manager mission {mission.id} failed at "
            f"{failed_step}. {esc_sentence}"
        )

    if verdict == "deferred":
        return (
            f"Docs Manager mission {mission.id} deferred. "
            f"Awaiting follow-up review."
        )

    # Shouldn't reach — the generic helper's terminal-gate normally
    # filters before we get here. Guard anyway.
    return (
        f"Docs Manager mission {mission.id} reached terminal state "
        f"with verdict={verdict!r}."
    )


# ── Thin caller wrapper ─────────────────────────────────────────────


def post_docs_manager_shift_report(mission) -> Dict[str, Any]:
    """Post a Documentation Manager shift report for ``mission``.

    Thin wrapper around ``core.employees.comms.post_shift_report`` that
    bakes in the docs_manager-specific subject, body formatter, extra
    metadata keys, and ``sender_type='rigby'`` (one of the model's
    allowed choices). Same idempotency + terminal-gate semantics as
    the generic helper.
    """
    return post_shift_report(
        employee=RIGBY,
        job="docs_manager",
        mission=mission,
        body_formatter=format_body,
        extra_metadata_keys=EXTRA_METADATA_KEYS,
        thread_subject=THREAD_SUBJECT,
        sender_type="rigby",
    )
