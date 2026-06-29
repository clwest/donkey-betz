"""
AI Employee + Job contracts (Session 1252 PR 1).

Frozen-dataclass config. No Django model — the v0 employee/job surface
lives in code, reviewed via PR, versioned in git. Runtime state for
each mission an employee runs lives in existing tables (``OpsRun`` /
``OpsRunEvent`` / ``Deliverable``), not on these objects.

Reflects Rigby's six required edits to the Documentation Manager
contract from Session 1252 discovery review:

  1. Best-effort sync wording (Rigby is accountable for execution,
     verification, and escalation — not for magically fixing schema
     drift, DB issues, storage failures, or long-running embed
     problems).
  2. Required summary stats schema (see ``required_summary_keys``).
  3. drift_count definition is the verify_doc_claims --only-drift
     numeric output if available; otherwise null + degraded_evidence.
  4. Step 4 (embed) timeout requirement is a hard precondition for
     PR 2 (warning 10min, hard failure 30min).
  5. Escalation visibility guarantee — publish_candidate deliverable
     forced to ready/attention-required via canonical status path,
     plus a pinned PA conversation post.
  6. Dedupe rule keys off failure signature from OpsRun/OpsRunEvent
     evidence, not deliverable status.

See ``docs/handoffs/SESSION_1251_CAPABILITY_AUDIT.md`` §5 + Session
1252 discovery report for context.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional


# ── Authority levels ─────────────────────────────────────────────────


class AuthorityLevel(str, enum.Enum):
    """Authority levels a job grants over a class of actions.

    Stored as the string value in JobContract.authority maps so the
    contract serializes cleanly to JSON for ``employee_tool describe``.
    """

    OBSERVE = "observe"            # may read + report; may not act
    RECOMMEND = "recommend"        # may propose action; must escalate
    EXECUTE = "execute"            # may act autonomously within scope
    PROHIBITED = "prohibited"      # explicitly NOT permitted


# ── Core dataclasses ─────────────────────────────────────────────────


@dataclass(frozen=True)
class AIEmployee:
    """An AI worker that can hold one or more job contracts.

    v0: Rigby is the only employee. Identity fields capture how the
    employee is addressed in chat, what UnifiedUser she acts as when
    executing server-side, and where her primary operating thread is.

    Rigby has no dedicated User row — when she runs autonomously
    (beat tasks, server-side helpers), she acts as the ``runs_as_username``
    user account (currently ``chris``). This is honest about the v0
    auth surface; future PRs may introduce a dedicated service account.
    """

    handle: str                              # "rigby" — lowercase id
    display_name: str                        # "Rigby" — chat-facing name
    runs_as_username: str                    # User she acts as server-side
    primary_chat_id: Optional[str] = None    # pinned PA conversation id
    notes: str = ""                          # free-form context


@dataclass(frozen=True)
class JobContract:
    """A single named role assigned to an employee.

    The contract is *policy*: what the employee owns, what authority
    she carries, what evidence each mission must record, when she
    escalates, and how Chris reads the result. Workflow state for any
    given mission lives in ``OpsRun(run_kind=mission_run_kind)`` plus
    the linked ``OpsRunEvent`` rows; this object never persists state
    of its own.

    ``mission_run_kind`` is the value written to ``OpsRun.run_kind``
    when this job creates a MissionRun. The verdict / status / summary
    keys named below are the contract Rigby holds — PR 2 wires the
    daily routine to satisfy them; PR 3 reads them back.
    """

    # ── Identity
    title: str
    employee_handle: str
    manager: str                              # who assigned the job

    # ── Why the job exists
    mission: str                              # one-paragraph charter
    responsibilities: tuple[str, ...]
    success_metrics: tuple[str, ...]
    failure_metrics: tuple[str, ...]

    # ── How the job runs
    triggers: tuple[str, ...]                 # cron / signal / manual
    daily_routine: tuple[str, ...]            # step-by-step
    weekly_routine: tuple[str, ...] = ()
    mission_run_kind: str = ""                # OpsRun.run_kind value

    # ── What Rigby may do
    authority: dict[str, str] = field(
        default_factory=dict
    )                                         # action_class → level
    prohibited_actions: tuple[str, ...] = ()

    # ── Evidence contract (Rigby edit #2)
    required_summary_keys: tuple[str, ...] = ()
    evidence_tables: tuple[str, ...] = ()      # tables that capture truth

    # ── Drift definition (Rigby edit #3)
    drift_count_definition: str = ""

    # ── Step 4 timeout (Rigby edit #4)
    embed_step_timeout: dict[str, int] = field(
        default_factory=dict
    )                                         # {warning_seconds, hard_seconds}

    # ── Escalation (Rigby edits #5 + #6)
    escalation_rules: tuple[str, ...] = ()
    escalation_visibility: tuple[str, ...] = ()
    dedupe_rule: str = ""

    # ── Boundary statements
    what_chris_approves: tuple[str, ...] = ()
    what_claude_handles: tuple[str, ...] = ()
    what_rigby_can_do_alone: tuple[str, ...] = ()

    # Session 1252 PR 2 — single source of truth for the OpsRun.summary
    # JSON key that holds the normalized error-tail hash used for
    # 24h failure-signature dedupe. PR 2's escalation code, the dedupe
    # lookup, and any future audit query all reference this string —
    # changing it here is the only update needed.
    summary_field_for_error_signature: str = "error_signature"


# ── Employee constant ────────────────────────────────────────────────


RIGBY = AIEmployee(
    handle="rigby",
    display_name="Rigby",
    # Honest v0: Rigby has no dedicated User row. Acts as `chris`
    # when running server-side. Tracked in the Session 1252 discovery
    # report as an accepted v0 limitation.
    runs_as_username="chris",
    primary_chat_id="pa-3901b70e61934df7",
    notes=(
        "Personal Assistant + first AI employee. Operates the PA tool "
        "surface (110+ schemas / 170+ handlers) and certifies business "
        "truth for the platform. v0 acts as the `chris` UnifiedUser "
        "server-side; no dedicated service account yet."
    ),
)


# ── Job constant: Documentation Manager (Rigby-edited) ───────────────


DOCUMENTATION_MANAGER = JobContract(
    title="Documentation Manager",
    employee_handle="rigby",
    manager="chris",

    # ── Mission — Rigby edit #1: best-effort sync wording ────────────
    mission=(
        "Rigby owns running the documentation cascade, recording "
        "evidence, certifying successful runs, and escalating failures "
        "or drift. Sync between docs/ on disk and the index / RAG "
        "corpus / Document table / DocumentEmbedding table is a "
        "best-effort operational target contingent on the cascade "
        "commands succeeding. Rigby is accountable for execution, "
        "verification, and escalation — not for magically fixing "
        "schema drift, DB outages, storage failures, corrupted docs, "
        "or long-running embed problems."
    ),

    responsibilities=(
        "Run the 4-step documentation cascade once per weekday morning.",
        "Run `verify_doc_claims --only-drift` as an observation step "
        "(does NOT fail the mission, but the drift count is part of "
        "the daily evidence summary).",
        "On any cascade step failure, escalate per the visibility "
        "guarantee below.",
        "On success, certify the MissionRun via the canonical verdict "
        "path and stay silent — silent success is the contract.",
    ),

    triggers=(
        "Cron only (v0). One PeriodicTask entry, weekdays 06:30 local.",
        "Manual override via `employee_tool action=run_now employee=rigby "
        "job=docs_manager` (lands in PR 3 / PR 2 wiring, not PR 1).",
    ),

    daily_routine=(
        "Step 1 — build_docs_index (refresh docs/INDEX.md + _index.json).",
        "Step 2 — build_rag_corpus (regenerate .rag/corpus.jsonl).",
        "Step 3 — sync_docs_index_to_documents (push to Document table).",
        "Step 4 — sync_docs_index_to_documents --embed (generate "
        "DocumentEmbedding rows). MUST run with the timeout contract "
        "below.",
        "Step 5 — verify_doc_claims --only-drift (observation only).",
        "Step 6 — emit verdict via mission_verdict tool.",
    ),

    weekly_routine=(),

    mission_run_kind="docs_cascade",

    # ── Authority ────────────────────────────────────────────────────
    authority={
        "run_docs_cascade_commands": AuthorityLevel.EXECUTE.value,
        "run_drift_observation": AuthorityLevel.OBSERVE.value,
        "create_escalation_deliverable": AuthorityLevel.EXECUTE.value,
        "post_escalation_to_pa_chat": AuthorityLevel.EXECUTE.value,
        "certify_mission_run": AuthorityLevel.EXECUTE.value,
        "broken_link_sweep": AuthorityLevel.RECOMMEND.value,
        "narrative_refresh_suggestion": AuthorityLevel.RECOMMEND.value,
        "modify_docs_files": AuthorityLevel.PROHIBITED.value,
        "open_pull_request": AuthorityLevel.PROHIBITED.value,
        "delete_document_rows": AuthorityLevel.PROHIBITED.value,
        "delete_document_embedding_rows": AuthorityLevel.PROHIBITED.value,
    },

    prohibited_actions=(
        "Edit any file under docs/ (Claude Code's responsibility).",
        "Open or merge pull requests.",
        "Delete rows from Document or DocumentEmbedding tables.",
        "Decide what is in scope for the job (Chris owns scope).",
    ),

    # ── Success / failure metrics ────────────────────────────────────
    success_metrics=(
        "All 4 cascade steps return exit 0.",
        "DocumentEmbedding count grew or stayed within ±5% of yesterday "
        "(catches accidental mass-delete or mass-regen).",
        "verify_doc_claims drift count is recorded (not gated on).",
        "Total mission wall time < 10 minutes.",
    ),

    failure_metrics=(
        "Any of steps 1–4 returns non-zero exit.",
        "Step 4 wall time exceeds the hard failure timeout below.",
        "3 consecutive successful missions but drift count growing by "
        ">10/day — escalate as 'drift accumulation, cascade healthy "
        "but claims aging'.",
    ),

    # ── Evidence contract (Rigby edit #2) ────────────────────────────
    required_summary_keys=(
        # Cascade telemetry
        "docs_indexed_count",            # may be null if unavailable
        "documents_count_before",
        "documents_count_after",
        "embeddings_count_before",
        "embeddings_count_after",
        "embedding_delta",
        # Drift observation (Rigby edit #3)
        "drift_count",                   # null + degraded_evidence=true if not parseable
        "drift_items_count",             # may be null
        "degraded_evidence",             # bool — true when any count is null
        # Timing + failure capture
        "wall_time_ms",
        "failed_step",                   # null on success
        "error_tail",                    # null on success; last N lines on failure
    ),

    evidence_tables=(
        "OpsRun (domain=mission, run_kind=docs_cascade)",
        "OpsRunEvent (one per step + verdict_issued event)",
        "LLMCallEvent (from step 4 embedding API)",
        "ToolCallRecord (if any cascade command emits one)",
        "Deliverable (publish_candidate, only on escalation)",
    ),

    # ── Drift definition (Rigby edit #3) ─────────────────────────────
    drift_count_definition=(
        "The machine-readable count returned by "
        "`python manage.py verify_doc_claims --only-drift` if the "
        "command exposes a clean numeric output; otherwise null with "
        "degraded_evidence=true. PR 1 does not invent drift parsing — "
        "if the command does not currently surface a parseable count, "
        "PR 2 may improve the command's machine-readable output."
    ),

    # ── Step 4 timeout (Rigby edit #4) ───────────────────────────────
    embed_step_timeout={
        # Warn at 10min — likely an unintended full re-embed instead
        # of an incremental update. Worth Chris's eyes but not a
        # mission failure on its own.
        "warning_seconds": 600,
        # Hard fail at 30min — Step 4 must abort and the mission must
        # finalize as 'failed' with failed_step='step_4_embed'.
        "hard_seconds": 1800,
    },

    # ── Escalation (Rigby edits #5 + #6) ─────────────────────────────
    escalation_rules=(
        "First failure of any step → escalate immediately.",
        "Subsequent failures with the SAME failure signature within "
        "24h → append/reference the prior escalation rather than "
        "create a duplicate deliverable (see dedupe_rule below).",
        "3 failures of any kind within a 7-day rolling window → mark "
        "the job 'trust_status: under_review' in the status tool's "
        "derived response (no state change to the contract itself).",
    ),

    escalation_visibility=(
        "Create a Deliverable with publish_intent=publish_candidate "
        "titled 'Docs Manager — Escalation [YYYY-MM-DD]'.",
        "Force the deliverable to a visible state (ready or "
        "attention-required) via the canonical status path "
        "(`content_tool` or `deliverable_tool.set_status`). Required "
        "because `deliverable_tool.create` currently defaults new "
        "rows to status=completed regardless of explicit param "
        "(see feedback_deliverable_create_defaults_to_completed.md).",
        "Post a one-line escalation summary into the employee's "
        "primary_chat_id (`pa-3901b70e61934df7`) so Chris sees it "
        "in his pinned PA conversation.",
    ),

    dedupe_rule=(
        "Duplicate escalation suppression MUST key off the failure "
        "signature derived from OpsRun.summary.failed_step + a "
        "normalized hash of OpsRun.summary.error_tail (not "
        "deliverable status). Same signature within 24h → append to "
        "or reference the prior escalation. Different signature → "
        "new deliverable, even if the prior one is still open."
    ),

    # ── Boundary statements ──────────────────────────────────────────
    what_chris_approves=(
        "The contract itself (PR 1 review).",
        "Quarterly: reads `employee_tool action=status` (PR 3) and "
        "decides whether to expand Rigby's authority on adjacent "
        "actions.",
        "Acts on escalation deliverables Rigby creates.",
    ),

    what_claude_handles=(
        "Writing PRs 1 / 2 / 3 of this rollout.",
        "Fixing bugs surfaced by escalations (e.g., a flaky cascade "
        "step).",
        "Any infrastructure change to the docs cascade itself "
        "(adding a step, retiring a command, etc.).",
    ),

    what_rigby_can_do_alone=(
        "Run the daily routine.",
        "Certify mission success / rejection / deferral via "
        "mission_verdict (PR 1).",
        "Emit escalation artifacts per the visibility guarantee.",
        "Answer `employee_tool action=status` queries (PR 3).",
    ),
)


# ── Registry helpers ─────────────────────────────────────────────────

_EMPLOYEES_BY_HANDLE: dict[str, AIEmployee] = {
    RIGBY.handle: RIGBY,
}

_JOBS_BY_EMPLOYEE: dict[str, dict[str, JobContract]] = {
    RIGBY.handle: {
        "docs_manager": DOCUMENTATION_MANAGER,
    },
}


def list_employees() -> list[AIEmployee]:
    """Return every registered employee."""
    return list(_EMPLOYEES_BY_HANDLE.values())


def get_employee(handle: str) -> Optional[AIEmployee]:
    """Look up an employee by handle (case-insensitive); None if missing."""
    return _EMPLOYEES_BY_HANDLE.get(handle.lower()) if handle else None


def list_jobs_for_employee(handle: str) -> list[JobContract]:
    """Return every job assigned to ``handle``; empty list if unknown."""
    if not handle:
        return []
    return list(_JOBS_BY_EMPLOYEE.get(handle.lower(), {}).values())


def get_job(employee_handle: str, job_key: str) -> Optional[JobContract]:
    """Look up one job by employee handle + job key; None if missing."""
    if not employee_handle or not job_key:
        return None
    return _JOBS_BY_EMPLOYEE.get(
        employee_handle.lower(), {}
    ).get(job_key.lower())
