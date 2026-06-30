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


# ── Employee OS-scoped defaults ──────────────────────────────────────

# Default workspace every Employee OS job operates inside today. Used by
# each job module's escalation deliverable spec factory (and by Platform
# Audit's inline ORM lookup for its audit deliverable). Confidence and
# dedupe defaults already live as ``MissionRunnerConfig`` field defaults
# in ``mission_runner.py`` — do NOT duplicate those here.
#
# If a future employee operates in a different workspace, the job's
# escalation_spec_factory can return ``EscalationDeliverableSpec(
# workspace_name="...")`` to override per-mission without changing this
# constant. Don't promote this to a "global platform default" — it is
# Employee OS-scoped policy.
EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME: str = "Donkey Betz"


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


# ── Employee constant: Platform Auditor (Session 1257 PR 2.1) ────────


PLATFORM_AUDITOR = AIEmployee(
    handle="platform_auditor",
    display_name="Platform Auditor",
    # Honest v0: like Rigby, the Platform Auditor has no dedicated User
    # row. Acts as the ``chris`` UnifiedUser server-side when running
    # autonomously. Tracked as a known v0 limitation.
    runs_as_username="chris",
    # No pinned PA chat — the auditor reports via the audit Deliverable
    # itself + the standard shift-report DM, not via a dedicated chat
    # thread. Empty primary_chat_id is intentional.
    primary_chat_id=None,
    notes=(
        "Second AI employee (Session 1257). Owns the weekly platform "
        "audit — read-only inspection of docs, integrations, env "
        "config status, and database model counts. Wraps the existing "
        "PlatformAuditAgent (core/agents/platform_audit_agent.py). "
        "v0 acts as the ``chris`` UnifiedUser server-side; no "
        "dedicated service account yet. Beat schedule + task runner "
        "land in subsequent PRs (2.2/2.3); PR 2.1 registers the "
        "contract only."
    ),
)


# ── Job constant: Platform Audit (Session 1257 PR 2.1) ───────────────


PLATFORM_AUDIT_JOB = JobContract(
    title="Platform Audit",
    employee_handle="platform_auditor",
    manager="chris",

    # ── Mission ─────────────────────────────────────────────────────
    mission=(
        "Platform Auditor owns running the weekly internal platform "
        "audit, recording evidence, certifying healthy audits, and "
        "escalating drift or anomalies. The audit is strictly "
        "read-only: it inspects platform docs, integration "
        "configuration status, environment-variable presence (values "
        "masked), and key database-model row counts. The auditor "
        "does NOT modify any platform state, write to env config, "
        "delete database rows, execute arbitrary code, or access "
        "actual secret values. Findings are persisted as a structured "
        "audit Deliverable; failures escalate per the standard "
        "Employee OS visibility guarantee."
    ),

    responsibilities=(
        "Run the platform audit once per week (cadence finalized in "
        "PR 2.3 when the beat schedule lands).",
        "Inspect the canonical platform docs (CLAUDE.md, "
        "SPIDERS.md, AGENTS.md, SERVICES.md, ARCHITECTURE.md, "
        "CAPABILITIES.md) for surface-level drift.",
        "Inventory integrations (LLM providers, media APIs, spider "
        "credentials, payment, infrastructure) and report which have "
        "credentials configured vs missing.",
        "Audit environment-variable configuration coverage by "
        "category (api_keys, database, redis, feature_flags) — "
        "values masked; only existence reported.",
        "Count key database models (Agent, AgentExecution, "
        "AgentMemory, LegacySpiderData, Conversation, User, "
        "ImageHistory, VideoHistory) and report current totals.",
        "Synthesize the findings into a structured audit Deliverable "
        "(Executive Summary / Integration Health / Configuration "
        "Status / Database Health / Top Risks / Green Checks).",
        "On clean audit → certify mission via mission_verdict + stay "
        "silent. Silent success is the contract.",
        "On any audit failure → escalate per the visibility "
        "guarantee below.",
    ),

    triggers=(
        "Cron only (v0). Beat schedule lands in PR 2.3 — weekly "
        "cadence to be finalized then (proposed: Monday 06:30 local).",
        "Manual override via ``employee_tool action=run_now "
        "employee=platform_auditor job=platform_audit`` — lands in "
        "PR 2.2 (run_now path) along with the task runner.",
    ),

    # No daily routine — the audit is weekly v0. Listed empty so the
    # contract dataclass is explicit about cadence rather than implicit.
    daily_routine=(),

    weekly_routine=(
        "Step 1 — read_documentation: sweep the 6 canonical docs.",
        "Step 2 — inventory_integrations: capture credential-status "
        "snapshot across all integration categories.",
        "Step 3 — check_env_config: presence-only audit across "
        "all env categories (values masked).",
        "Step 4 — count_database_models: capture row counts for the "
        "8 canonical models.",
        "Step 5 — generate_audit_report: synthesize the findings "
        "into a structured Deliverable (Executive Summary / "
        "Integration Health / Configuration Status / Database "
        "Health / Top Risks / Green Checks).",
        "Step 6 — emit verdict via mission_verdict.",
    ),

    mission_run_kind="platform_audit",

    # ── Authority — read-only by design ─────────────────────────────
    authority={
        "read_platform_docs": AuthorityLevel.EXECUTE.value,
        "inventory_integrations": AuthorityLevel.EXECUTE.value,
        "check_env_config_status": AuthorityLevel.OBSERVE.value,
        "count_database_models": AuthorityLevel.OBSERVE.value,
        "generate_audit_report": AuthorityLevel.EXECUTE.value,
        "save_audit_to_deliverable": AuthorityLevel.EXECUTE.value,
        "certify_mission_run": AuthorityLevel.EXECUTE.value,
        "recommend_remediations": AuthorityLevel.RECOMMEND.value,
        "modify_any_file": AuthorityLevel.PROHIBITED.value,
        "modify_env_config": AuthorityLevel.PROHIBITED.value,
        "delete_database_rows": AuthorityLevel.PROHIBITED.value,
        "execute_arbitrary_code": AuthorityLevel.PROHIBITED.value,
        "access_secret_values": AuthorityLevel.PROHIBITED.value,
        "open_pull_request": AuthorityLevel.PROHIBITED.value,
        "modify_settings": AuthorityLevel.PROHIBITED.value,
    },

    prohibited_actions=(
        "Modify any file (config, code, docs).",
        "Modify environment-variable configuration.",
        "Execute arbitrary code outside the named audit tools.",
        "Access actual secret values from env vars "
        "(presence-only, masked).",
        "Delete or update rows in any database model.",
        "Open or merge pull requests.",
        "Decide what is in scope for the audit "
        "(Chris owns scope).",
    ),

    # ── Success / failure metrics ───────────────────────────────────
    success_metrics=(
        "All 5 audit steps return without raising.",
        "Synthesized audit Deliverable includes the 6 required "
        "sections (Executive Summary, Integration Health, "
        "Configuration Status, Database Health, Top Risks, "
        "Green Checks).",
        "Audit Deliverable persisted with deliverable_type='analysis' "
        "(matches the agent's existing actionable_config item shape).",
        "Total mission wall time < 5 minutes.",
        "findings_count + issues_found_count recorded in the "
        "mission summary.",
    ),

    failure_metrics=(
        "Any of the 5 audit steps raises or returns a malformed "
        "shape (e.g., LLM synthesis empty without fallback).",
        "Audit Deliverable missing one or more required sections.",
        "Audit wall time exceeds 10 minutes (LLM synthesis stall).",
        "3 failures within a 7-day rolling window → mark the job "
        "'trust_status: under_review' in the status tool's derived "
        "response (no state change to the contract itself).",
    ),

    # ── Evidence contract ───────────────────────────────────────────
    required_summary_keys=(
        # Audit shape
        "audit_type",                   # 'integrations' / 'configuration' / 'database' / 'comprehensive'
        "findings_count",               # int — total findings flagged
        "issues_found_count",           # int — subset that are actionable issues
        # Step-level evidence
        "docs_audited",                 # list[str] — doc names actually read in step 1
        "integrations_audited_count",   # int — integrations enumerated in step 2
        "env_vars_checked_count",       # int — env vars probed in step 3
        "models_counted",               # dict[str, int] — model_name → row count
        # Synthesis output
        "report_deliverable_id",        # UUID — the audit Deliverable from step 5
        "report_chars",                 # int — synthesis length
        # Timing + failure capture
        "wall_time_ms",
        "failed_step",                  # null on success
        "error_tail",                   # null on success
        "degraded_evidence",            # bool — true when any evidence field is null
    ),

    evidence_tables=(
        "OpsRun (domain=mission, run_kind=platform_audit)",
        "OpsRunEvent (one per audit step + verdict_issued event)",
        "LLMCallEvent (from gpt-5.2 synthesis + tool calls)",
        "ToolCallRecord (from each platform audit tool invocation)",
        "Deliverable (audit report — created on every run, not "
        "just on escalation)",
    ),

    # ── Drift definition ───────────────────────────────────────────
    drift_count_definition=(
        "Not applicable to the Platform Auditor. The audit is "
        "observational — its findings count is reported via "
        "``findings_count`` and ``issues_found_count`` rather than "
        "a docs-cascade-style drift metric. The runner does not "
        "consult a verify_doc_claims-equivalent for this job."
    ),

    # ── Step timeout (mirrors docs-cascade contract shape) ──────────
    # Platform audit doesn't have a separate long-running step like the
    # docs cascade's embed step. The LLM synthesis is bounded by the
    # standard MissionRunner soft/hard time limits inherited from the
    # Celery task wrapper (configured in PR 2.2 when the task lands).
    # Empty dict here is explicit about no per-step override.
    embed_step_timeout={},

    # ── Escalation (mirrors docs cascade conventions) ──────────────
    escalation_rules=(
        "First failure of any step → escalate immediately.",
        "Subsequent failures with the SAME failure signature within "
        "24h → append/reference the prior escalation rather than "
        "create a duplicate Deliverable (24h dedupe window).",
        "3 failures of any kind within a 7-day rolling window → mark "
        "the job 'trust_status: under_review' in the status tool's "
        "derived response.",
    ),

    escalation_visibility=(
        "Create a Deliverable with "
        "publish_intent=publish_candidate titled 'Platform Audit "
        "Escalation [YYYY-MM-DD]'.",
        "Force the Deliverable to a visible state (ready or "
        "attention-required) via the canonical status path with "
        "audit transition source='PlatformAuditor'. Required "
        "because Deliverable.create currently defaults new rows "
        "to status=completed regardless of explicit param.",
        "No PA chat post for v0 — the auditor has no pinned PA "
        "conversation. Findings + escalations are visible in the "
        "/inbox web UI via the shift-report DM (post_shift_report).",
    ),

    dedupe_rule=(
        "Duplicate escalation suppression MUST key off the failure "
        "signature derived from OpsRun.summary.failed_step + a "
        "normalized hash of OpsRun.summary.error_tail (canonical "
        "MissionRunner.make_error_signature). Same signature within "
        "24h → append to or reference the prior escalation. "
        "Different signature → new Deliverable, even if the prior "
        "one is still open."
    ),

    # ── Boundary statements ────────────────────────────────────────
    what_chris_approves=(
        "The contract itself (PR 2.1 review).",
        "Quarterly: reads ``employee_tool action=status "
        "employee=platform_auditor`` and decides whether to expand "
        "the auditor's authority (e.g., adding new audit categories).",
        "Acts on findings flagged in the weekly audit Deliverable.",
    ),

    what_claude_handles=(
        "Writing PRs 2.1 / 2.2 / 2.3 of this rollout.",
        "Fixing bugs surfaced by audit-failure escalations.",
        "Adding new platform components to the audit scope (new "
        "integration categories, additional doc files, additional "
        "models to count).",
    ),

    what_rigby_can_do_alone=(
        # JobContract reuses the ``what_rigby_can_do_alone`` field
        # name from PR 1 — it's the generic "what this employee can
        # do alone" slot. The contract dataclass name predates the
        # multi-employee surface; the semantic is correct.
        "Run the weekly audit routine.",
        "Read the 6 canonical platform docs.",
        "Inventory all integrations + env var configuration status.",
        "Count rows in the 8 canonical database models.",
        "Generate + persist the audit Deliverable.",
        "Certify / reject / defer the mission via mission_verdict.",
        "Emit escalation artifacts per the visibility guarantee.",
        "Answer ``employee_tool action=status`` queries.",
    ),
)


# ── Employee constant: Chief of Staff (Session 1257 PR 3.1) ──────────


CHIEF_OF_STAFF = AIEmployee(
    handle="chief_of_staff",
    display_name="Chief of Staff",
    # Honest v0: like Rigby + Platform Auditor, Chief of Staff has no
    # dedicated User row. Acts as the ``chris`` UnifiedUser server-side
    # when running autonomously. Tracked as a known v0 limitation.
    runs_as_username="chris",
    # No pinned PA chat — the brief itself is the daily-read surface
    # (lands in the "Morning Brief" workspace + a shift-report DM into
    # the persistent inbox thread). No dedicated chat channel in v0.
    primary_chat_id=None,
    notes=(
        "Third AI employee (Session 1257). Owns the daily Chief-of-"
        "Staff morning brief — a read-only synthesis of platform "
        "readiness, build focus, competitive landscape, and a "
        "rotating market lane into one consolidated brief Deliverable "
        "Chris reads at 07:00 local. Wraps the existing "
        "morning_brief workflow in WorkflowOrchestrationAgent "
        "(core/services/workflow_orchestration_agent.py:733). v0 "
        "acts as the ``chris`` UnifiedUser server-side; no dedicated "
        "service account yet. Task runner + beat schedule land in "
        "subsequent PRs (3.2/3.3); PR 3.1 registers the contract only."
    ),
)


# ── Job constant: Daily Morning Brief (Session 1257 PR 3.1) ──────────


MORNING_BRIEF_JOB = JobContract(
    title="Daily Morning Brief",
    employee_handle="chief_of_staff",
    manager="chris",

    # ── Mission ─────────────────────────────────────────────────────
    mission=(
        "Chief of Staff owns running the daily Chief-of-Staff "
        "morning brief, recording evidence, certifying healthy "
        "briefs, and escalating workflow failures. The brief is "
        "strictly read-only synthesis: it pulls platform-readiness "
        "telemetry, build-focus deltas, competitive-landscape signals, "
        "and a rotating market/signal lane, then synthesizes them "
        "into 1-3 explicit Decision Cards plus a TL;DR pointer. The "
        "Chief of Staff does NOT send emails or external messages, "
        "modify source documentation, change schedules, approve "
        "decisions on Chris's behalf, execute business actions, post "
        "publicly, edit financial records, or create/modify "
        "users/accounts/settings. The brief is persisted as a "
        "Deliverable in the 'Morning Brief' workspace; failures "
        "escalate per the standard Employee OS visibility guarantee."
    ),

    responsibilities=(
        "Run the morning brief once per weekday morning "
        "(daily 07:00 America/Denver; beat row "
        "``generate-morning-brief-daily`` routes to "
        "``chief_of_staff_morning_brief_run`` per S1258 PR 3.3).",
        "Resolve the Lane 4 rotation slot per the priority chain "
        "(caller-forced → incident → revenue → signal → calendar → "
        "weekday default).",
        "Pull overnight platform-readiness telemetry (SLO breaches, "
        "failing tasks, queue backlog, fleet degradation) — Lane 1.",
        "Pull the build-focus delta (shipping progress, blocked "
        "initiatives, approvals needed in last 24h) — Lane 2.",
        "Pull the competitive-landscape change-only snapshot "
        "(competitor launches/pricing/features/fundraising in last "
        "72h) — Lane 3.",
        "Dispatch the rotating market/signal lane per the slot "
        "resolved by Step 1 — Lane 4.",
        "Synthesize 1-3 explicit Decision Cards from the 4 lanes + "
        "governance/work/ops snapshots.",
        "Compile the final brief markdown with TL;DR pointer to the "
        "Decision Card and persist as a Deliverable into the "
        "'Morning Brief' workspace.",
        "On any step failure → escalate per the visibility guarantee "
        "below.",
        "On clean run → certify mission via mission_verdict + stay "
        "silent. Silent success is the contract (the brief itself is "
        "the visibility).",
    ),

    triggers=(
        "Cron — daily 07:00 local (America/Denver). Beat row "
        "``generate-morning-brief-daily`` at "
        "``core/celery.py:463-481``; task target "
        "``chief_of_staff_morning_brief_run`` at "
        "``core/tasks_chief_of_staff.py``. Beat field flipped to the "
        "MissionRunner-backed runner in S1258 PR 3.3.",
        "Manual override via ``employee_tool action=run_now "
        "employee=chief_of_staff job=morning_brief`` (PR 3.2 task "
        "runner + ``_RUN_NOW_TASKS`` registry entry in "
        "``core/services/td_handlers_employee.py``).",
    ),

    daily_routine=(
        "Step 1 — rotation_slot_resolve: pure-logic priority-chain "
        "selection of the Lane 4 rotating slot.",
        "Step 2 — lane_1_platform_readiness: overnight health snapshot "
        "from system_intelligence_agent.",
        "Step 3 — lane_2_build_focus: shipping delta + blocked "
        "initiatives from coo_agent.",
        "Step 4 — lane_3_competitive_landscape: competitor change "
        "snapshot from trend_analysis_agent.",
        "Step 5 — lane_4_rotating_focus: rotating market/signal lane "
        "dispatched per the resolved slot.",
        "Step 6 — decision_card_synthesis: LLM synthesis of 1-3 "
        "explicit decisions from the 4 lanes + governance/work/ops "
        "snapshots.",
        "Step 7 — strategic_synthesis: compile final brief markdown "
        "with TL;DR pointer to the Decision Card.",
        "Step 8 — create_deliverable: persist final brief into the "
        "'Morning Brief' workspace as a Deliverable.",
        "Step 9 — emit verdict via mission_verdict.",
    ),

    weekly_routine=(),

    mission_run_kind="morning_brief",

    # ── Authority — read-only synthesis + Deliverable persistence ───
    authority={
        # Read-only lane data pulls
        "read_platform_readiness_telemetry": AuthorityLevel.OBSERVE.value,
        "read_build_focus_delta": AuthorityLevel.OBSERVE.value,
        "read_competitive_landscape_snapshot": AuthorityLevel.OBSERVE.value,
        "read_rotating_market_signals": AuthorityLevel.OBSERVE.value,
        "read_governance_state": AuthorityLevel.OBSERVE.value,
        "read_recent_action_items": AuthorityLevel.OBSERVE.value,
        # Synthesis + Deliverable persistence
        "resolve_rotation_slot": AuthorityLevel.EXECUTE.value,
        "synthesize_decision_card": AuthorityLevel.EXECUTE.value,
        "synthesize_strategic_brief": AuthorityLevel.EXECUTE.value,
        "save_brief_to_deliverable": AuthorityLevel.EXECUTE.value,
        "certify_mission_run": AuthorityLevel.EXECUTE.value,
        # Recommend-only — the brief surfaces priorities but does not act
        "recommend_daily_priorities": AuthorityLevel.RECOMMEND.value,
        "recommend_remediations": AuthorityLevel.RECOMMEND.value,
        # PROHIBITED — Chris's PR 3.1 directive list
        "send_emails_externally": AuthorityLevel.PROHIBITED.value,
        "send_external_messages": AuthorityLevel.PROHIBITED.value,
        "modify_source_documents": AuthorityLevel.PROHIBITED.value,
        "change_schedules": AuthorityLevel.PROHIBITED.value,
        "approve_decisions": AuthorityLevel.PROHIBITED.value,
        "execute_business_actions": AuthorityLevel.PROHIBITED.value,
        "post_publicly": AuthorityLevel.PROHIBITED.value,
        "edit_financial_records": AuthorityLevel.PROHIBITED.value,
        "create_or_modify_users": AuthorityLevel.PROHIBITED.value,
        "create_or_modify_accounts": AuthorityLevel.PROHIBITED.value,
        "modify_platform_settings": AuthorityLevel.PROHIBITED.value,
        "open_pull_request": AuthorityLevel.PROHIBITED.value,
    },

    prohibited_actions=(
        "Send emails or any external messages to humans or systems.",
        "Modify source documentation (docs/, CLAUDE.md, README, etc.).",
        "Change schedules — beat tasks, PeriodicTask rows, cron entries.",
        "Approve decisions on Chris's behalf — the brief surfaces "
        "decision cards but never marks them resolved.",
        "Execute business actions (Stripe charges, opportunity status "
        "transitions, contract sign-offs, etc.).",
        "Post publicly to any channel (blog, social, marketing site).",
        "Edit financial records (revenue rows, expense ledgers, "
        "invoice state).",
        "Create or modify user accounts, service accounts, or platform "
        "settings.",
        "Open or merge pull requests.",
        "Decide what is in scope for the brief (Chris owns scope; the "
        "rotation slot is data-driven, the lanes are fixed).",
    ),

    # ── Success / failure metrics ───────────────────────────────────
    success_metrics=(
        "All 8 brief steps complete without raising.",
        "Final brief Deliverable persisted into the 'Morning Brief' "
        "workspace with the canonical sections (TL;DR, Lane 1-4 "
        "summaries, Decision Card, recommended priorities).",
        "Decision Card carries 1-3 explicit decisions with clear "
        "options + recommended action.",
        "Total mission wall time < 15 minutes (existing workflow "
        "typically completes in 10-15 minutes).",
        "deliverable_id + rotation_slot + lane_4_slot_used recorded "
        "in the mission summary.",
    ),

    failure_metrics=(
        "Any of the 8 brief steps raises or returns success=False.",
        "create_deliverable step fails to persist the Deliverable "
        "row (workspace lookup fails, ORM error, etc.).",
        "LLM synthesis steps (decision_card_synthesis, "
        "strategic_synthesis) return empty content.",
        "Brief wall time exceeds 20 minutes (likely LLM stall).",
        "3 failures within a 7-day rolling window → mark the job "
        "'trust_status: under_review' in the status tool's derived "
        "response.",
    ),

    # ── Evidence contract ───────────────────────────────────────────
    required_summary_keys=(
        # Lane execution evidence
        "rotation_slot",                 # str — slot selected by Step 1
        "lane_4_slot_used",              # str — actual slot dispatched in Step 5
        "lanes_completed_count",         # int — 0-4
        # Synthesis output
        "decision_count",                # int — number of Decision Cards in the brief
        "decision_card_chars",           # int — length of decision card markdown
        # Deliverable output
        "deliverable_id",                # UUID — the brief Deliverable from Step 8
        "workspace_id",                  # UUID — "Morning Brief" workspace
        "brief_chars",                   # int — final brief markdown length
        # Timing + failure capture
        "wall_time_ms",
        "failed_step",                   # null on success
        "error_tail",                    # null on success
        "degraded_evidence",             # bool
    ),

    evidence_tables=(
        "OpsRun (domain=mission, run_kind=morning_brief)",
        "OpsRunEvent (one per lane/step + verdict_issued event)",
        "LLMCallEvent (from decision_card + strategic synthesis + "
        "lane sub-agent LLM calls)",
        "ToolCallRecord (from sub-agent tool invocations)",
        "Deliverable (morning brief — created on every run, in the "
        "'Morning Brief' workspace)",
    ),

    # ── Drift definition ───────────────────────────────────────────
    drift_count_definition=(
        "Not applicable to Chief of Staff. The morning brief is "
        "observational — its 'findings' surface as Decision Cards "
        "rather than a docs-cascade-style drift metric. The runner "
        "does not consult a drift-equivalent for this job."
    ),

    # ── Step timeout ────────────────────────────────────────────────
    embed_step_timeout={},

    # ── Escalation ──────────────────────────────────────────────────
    escalation_rules=(
        "First failure of any step → escalate immediately.",
        "Subsequent failures with the SAME failure signature within "
        "24h → append/reference the prior escalation rather than "
        "create a duplicate Deliverable (24h dedupe window).",
        "3 failures of any kind within a 7-day rolling window → mark "
        "the job 'trust_status: under_review' in the status tool's "
        "derived response.",
    ),

    escalation_visibility=(
        "Create a Deliverable with "
        "publish_intent=publish_candidate titled 'Chief of Staff "
        "Escalation [YYYY-MM-DD]'.",
        "Force the Deliverable to a visible state (ready or "
        "attention-required) via the canonical status path with "
        "audit transition source='ChiefOfStaff'.",
        "No PA chat post for v0 — Chief of Staff has no pinned PA "
        "conversation. Escalations are visible in the /inbox web UI "
        "via the shift-report DM.",
    ),

    dedupe_rule=(
        "Duplicate escalation suppression MUST key off the failure "
        "signature derived from OpsRun.summary.failed_step + a "
        "normalized hash of OpsRun.summary.error_tail (canonical "
        "MissionRunner.make_error_signature). Same signature within "
        "24h → append to or reference the prior escalation. "
        "Different signature → new Deliverable, even if the prior "
        "one is still open."
    ),

    # ── Boundary statements ────────────────────────────────────────
    what_chris_approves=(
        "The contract itself (PR 3.1 review).",
        "Quarterly: reads ``employee_tool action=status "
        "employee=chief_of_staff`` and decides whether to expand "
        "Chief of Staff's authority on adjacent actions (e.g., "
        "auto-resolving Decision Cards once history is established).",
        "Acts on Decision Cards surfaced in the daily brief — "
        "decisions are surfaced, not executed by Chief of Staff.",
    ),

    what_claude_handles=(
        "Writing PRs 3.1 / 3.2 / 3.3 of this rollout.",
        "Fixing bugs surfaced by brief-failure escalations (e.g., a "
        "flaky lane sub-agent).",
        "Adding new lanes to the rotation (Lane 4 slot list) or new "
        "lanes to the brief structure.",
    ),

    what_rigby_can_do_alone=(
        # JobContract reuses ``what_rigby_can_do_alone`` as the
        # generic "what this employee can do alone" slot — the field
        # name predates the multi-employee surface and is reused
        # verbatim by Platform Auditor + Chief of Staff for the same
        # semantic.
        "Run the daily morning brief workflow.",
        "Resolve the Lane 4 rotation slot.",
        "Pull all 4 lanes' data + synthesize decision cards.",
        "Persist the final brief Deliverable to the 'Morning Brief' "
        "workspace.",
        "Certify / reject / defer the mission via mission_verdict.",
        "Emit escalation artifacts per the visibility guarantee.",
        "Answer ``employee_tool action=status`` queries.",
    ),
)


# ── Registry helpers ─────────────────────────────────────────────────

_EMPLOYEES_BY_HANDLE: dict[str, AIEmployee] = {
    RIGBY.handle: RIGBY,
    PLATFORM_AUDITOR.handle: PLATFORM_AUDITOR,
    CHIEF_OF_STAFF.handle: CHIEF_OF_STAFF,
}

_JOBS_BY_EMPLOYEE: dict[str, dict[str, JobContract]] = {
    RIGBY.handle: {
        "docs_manager": DOCUMENTATION_MANAGER,
    },
    PLATFORM_AUDITOR.handle: {
        "platform_audit": PLATFORM_AUDIT_JOB,
    },
    CHIEF_OF_STAFF.handle: {
        "morning_brief": MORNING_BRIEF_JOB,
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


def list_jobs_with_keys(handle: str) -> list[tuple[str, JobContract]]:
    """Return ``(job_key, contract)`` tuples for every job on ``handle``.

    Session 1257 PR 2.1: added to support describing employees with
    multiple jobs (or any employee beyond Rigby) without hardcoding
    the reverse-lookup in the describe handler. ``list_jobs_for_employee``
    drops the key; ``list_jobs_with_keys`` preserves it.
    """
    if not handle:
        return []
    return list(_JOBS_BY_EMPLOYEE.get(handle.lower(), {}).items())


def list_job_keys_for_employee(handle: str) -> list[str]:
    """Return the registered job keys for ``handle``; empty if unknown.

    Session 1257 PR 2.1: helper used by the describe handler's
    unknown-job error branch to surface the actual known job keys
    instead of hardcoding ``['docs_manager']``.
    """
    if not handle:
        return []
    return list(_JOBS_BY_EMPLOYEE.get(handle.lower(), {}).keys())


def get_job(employee_handle: str, job_key: str) -> Optional[JobContract]:
    """Look up one job by employee handle + job key; None if missing."""
    if not employee_handle or not job_key:
        return None
    return _JOBS_BY_EMPLOYEE.get(
        employee_handle.lower(), {}
    ).get(job_key.lower())
