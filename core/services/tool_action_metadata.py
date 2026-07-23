"""Action Metadata Map — per-(tool, action) safety + applicability classification.

Ratified at S2902 (Row 161 substrate arc, T1a Phase 1) via Claude+Rigby joint
SIGN + Chris green-light. Per T1c §8 (Candidate A confirmed): in-code registry
adjacent to ``ToolDispatcher``. Consumed by ``pa_tool_validate_harness``.

Design summary (all four decisions ratified in S2902 SIGN cycle):

- **SafetyClass** — 4 values: ``READ_ONLY / WRITE_GATED / MUTATION / IRREVERSIBLE``.
  ``IRREVERSIBLE`` = cannot be safely run in harness even with owner/staff
  identity or a ``dry_run`` flag (kill switches, non-recoverable deletes).
- **Field set** — 3 fields per action: ``safety_class`` + ``applicability`` +
  ``notes`` (T1c §8 MVP boundary). ``env_required`` deliberately NOT promoted
  to a top-level field — encode env/deps in ``notes`` per convention below.
- **Tool-level defaults** — ``TOOL_DEFAULTS`` lets a tool declare a
  ``default_safety_class`` so obviously-safe read-only surfaces don't need
  per-action metadata authored before the harness can dispatch (mitigates
  the "metadata-debt gating tax" zoom-out concern).
- **Missing metadata** — harness treats unclassified ``(tool, action)`` pairs
  as *skip*, never as WRITE_GATED-dispatch-with-empty-payload. See
  ``resolve_safety`` semantics.

Notes convention (parseable by T1b template extraction):

- ``env: external:<name>``  — action needs an external service (railway, obs, …)
- ``env: local:<key>``      — action needs a local runtime (redis, celery, …)
- ``deps: <handle>``        — action depends on a specific data substrate
- ``gate: <reason>``        — action gated on flag/role/permission
- ``revisit: <trigger>``    — revisit classification when trigger fires

Multiple keys space-separated (``env: external:railway gate: staff``).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple


SafetyClass = Literal['READ_ONLY', 'WRITE_GATED', 'MUTATION', 'IRREVERSIBLE']
Applicability = Literal['always', 'conditional', 'gated']


@dataclass(frozen=True)
class ToolActionMetadata:
    """Per-``(tool_name, action)`` classification record."""

    safety_class: SafetyClass
    applicability: Applicability = 'always'
    notes: str = ''
    # S2909 T2: name of the external bridge this action depends on, if any.
    # Values are opaque strings that ``pa_tool_validate_harness._probe_bridge``
    # dispatches on (currently 'obs' and 'resolve_node'). ``None`` means the
    # action does not depend on an external bridge and skips the preflight
    # entirely — used for tools whose only dependency is the local Django
    # ORM or in-process constants.
    bridge: Optional[str] = None


@dataclass(frozen=True)
class ToolDefaults:
    """Tool-level defaults applied when a per-action record is absent.

    Presence of a default does NOT auto-classify every action — the harness
    still requires the action to be enumerated in the tool's schema. Defaults
    cover the "obvious surface" (e.g., a ``ops_tool`` whose read paths are
    uniformly safe) without forcing per-action authoring for every enum value.
    """

    default_safety_class: SafetyClass
    default_applicability: Applicability = 'always'
    notes: str = ''


# ── Pattern-selection rule (S2905 Rigby SIGN zoom-out AGREE-with-edits) ─────
#
# The metadata map exposes two coexisting patterns for a reason:
#
# - Uniform-safety tool (every action shares one safety class) → ``TOOL_DEFAULTS``.
#   Cheaper to author, harder to drift: adding a new action to the schema
#   inherits the default automatically.
# - Mixed-safety tool (actions split across READ_ONLY + MUTATION, or with
#   auth-required overrides) → per-action ``TOOL_ACTION_METADATA`` records.
#   Every action is enumerated explicitly; per-action records win over
#   tool defaults per ``resolve_safety`` precedence.
#
# **Risk of coexistence:** without the selection rule stated, future authors
# might mix patterns arbitrarily — e.g., add a per-action override to a
# uniform tool "just to be explicit", or ship a mixed-safety tool with only
# a TOOL_DEFAULTS entry that silently misclassifies the deviant action.
# Enforcement is convention today (S2905); if drift emerges across ≥3 sweep
# sessions, promote to a lint that flags per-action records shadowing a
# tool default with the SAME safety class (redundant override).
#
# ── Tool-level defaults ─────────────────────────────────────────────────────
#
# Seeded conservatively for T1a MVP. Adding a default here is a signed-off
# claim that ALL actions of that tool share the declared safety class. If any
# action of a tool deviates, either (a) remove the tool-level default and
# author per-action records, or (b) override with a specific record in
# ``TOOL_ACTION_METADATA`` (per-action records win over tool defaults).

TOOL_DEFAULTS: Dict[str, ToolDefaults] = {
    # T1a Phase 2 seed (S2903). Four tools authored from validation-doc
    # evidence — every action in each is read-only per its respective
    # validation report. Per-action overrides live in ``TOOL_ACTION_METADATA``
    # below for the ONE deviation (``ops_tool.focus_mode_update``).
    #
    # Authoring evidence:
    # - ops_tool: `docs/research/tools/validation/ops_tool_validation.md` §5
    #   ("All actions are read-only except `focus_mode_update`")
    # - kb_tool: handler at `td_handlers_ops.py:7548` — all 5 actions are
    #   ORM/pgvector queries, no writes
    # - agent_introspection_tool: read-only introspection surface (list,
    #   stats, details, capabilities, tools)
    # - repo_tool: `docs/research/tools/validation/repo_tool_validation.md`
    #   line 3 ("read-only codebase introspection")
    'ops_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: git-head, worker-recycle-log, OpsRun/CeleryTaskEvent',
    ),
    'kb_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: UnifiedEmbedding + DocumentEmbedding (pgvector)',
    ),
    'agent_introspection_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: AGENT_MAP, Agent table, ToolCallRecord',
    ),
    'repo_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: local repo filesystem + git',
    ),
    # Slice 2 batch 1 seed (S2905). Four tools from td_handlers_agents.py
    # authored from handler-trace evidence. Three uniformly READ_ONLY via
    # TOOL_DEFAULTS; revenue_tracker_tool is mixed (stats/list READ_ONLY +
    # create MUTATION) and uses per-action overrides in TOOL_ACTION_METADATA.
    #
    # Authoring evidence:
    # - gates_tool: `td_handlers_agents.py:5059` — 3 actions
    #   (list/stats/detail) all ORM reads against PilotReadinessGate
    # - pilots_tool: `td_handlers_agents.py:5131` — 3 actions
    #   (list/stats/detail) all ORM reads against PilotExecution
    # - cost_telemetry_tool: `td_handlers_agents.py:4854` — 3 actions
    #   (summary/top_agents/recent_calls) all aggregate reads against
    #   LLMCallLog
    'gates_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: PilotReadinessGate ORM',
    ),
    'pilots_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: PilotExecution ORM',
    ),
    'cost_telemetry_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: LLMCallLog ORM aggregates',
    ),
    # Slice 2 batch 2 seed (S2906). Four actionless tools from
    # td_handlers_agents.py — schema_action_count=0 for all four; TOOL_DEFAULTS
    # covers "everything the tool exposes" trivially because there is no
    # action enum to iterate. Uniform READ_ONLY per handler-trace evidence in
    # each tool's S2906 validation doc.
    #
    # Batch composition rationale (per Rigby S2906 T0 SIGN AGREE-with-edits +
    # zoom-out fold): actionless-only batch validates the doc-shape variant
    # that the T1a harness cannot pre-populate. S2907 commits to a small-
    # actionful all-read-only tool to stress the handler-trace-evidence
    # claim under non-trivial action enumeration.
    #
    # Authoring evidence:
    # - get_body_vitals: `td_handlers_agents.py:4766` — reads BodyCoordinator
    #   `get_all_vitals` / `get_system_vitals` (LUNGS substrate). Read-only.
    # - check_resource_budget: `td_handlers_agents.py:4796` — delegates to
    #   `body_vitals.check_budget` (LUNGS substrate). Pre-flight gate; no
    #   persisted decision.
    # - get_system_alerts: `td_handlers_agents.py:4822` — same
    #   `get_all_vitals` source, filters `alerts` slice by severity. S2906
    #   same-PR fix expands handler param acceptance; safety class unchanged.
    # - web_search: `td_handlers_agents.py:384` — Serper HTTP search;
    #   handler-side max_results clamp; no local writes.
    'get_body_vitals': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: BodyCoordinator vitals; actionless schema',
    ),
    'check_resource_budget': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: LUNGS body_vitals.check_budget; actionless schema',
    ),
    'get_system_alerts': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: BodyCoordinator alerts slice; actionless schema',
    ),
    'web_search': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='env: external:serper; actionless schema',
    ),
    # Slice 2 batch 3 seed (S2907). Three small-actionful all-READ_ONLY tools
    # from td_handlers_agents.py. Closes S2906 T0 SIGN Fold A commitment
    # (small-actionful stress test of `## Covered actions` handler-trace-
    # evidence claim under non-trivial action enumeration).
    #
    # Batch composition rationale (per Rigby S2907 T0 SIGN AGREE + zoom-out E):
    # uniform READ_ONLY sustains actionless-shape/small-actionful shape
    # separation from S2906. S2908 batch 4 committed to break the uniform-
    # only pattern (mixed-tool-scoped-to-READ_ONLY-subset OR gated-write
    # dry_run-only) per Rigby zoom-out E precedent-setting warning.
    #
    # Authoring evidence:
    # - ml_analysis: `td_handlers_agents.py:1711` — 3 actions
    #   (status/decision_pattern/detect_opportunity) delegate to MLEngine
    #   read methods (get_system_health / analyze_user_decision_pattern /
    #   detect_cross_domain_opportunity). No persisted writes.
    # - voice_clone_tool: `td_handlers_agents.py:4312` — 5 actions
    #   (list/detail/clone_requests/marketplace/stats) all ORM reads against
    #   VoiceProfile + VoiceCloneRequest. Cloning itself is Web UI /
    #   Discord `/voice clone`; this tool exposes read-only inspection.
    # - orm_inspect_tool: `td_handlers_agents.py:592` — 5 actions
    #   (list_models/describe_model/get/filter/count_by) explicitly built
    #   read-only at S2866 (Rigby Tool Gap Ledger #3). Docstring:
    #   "No .save / .update / .delete surface — construction only."
    'ml_analysis': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: MLEngine read methods (get_system_health / '
              'analyze_user_decision_pattern / detect_cross_domain_opportunity)',
    ),
    'voice_clone_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: VoiceProfile + VoiceCloneRequest ORM; '
              'cloning path is UI/Discord, not this tool',
    ),
    'orm_inspect_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: allowlisted Django ORM read-only inspection '
              '(Rigby Tool Gap Ledger #3, S2866)',
    ),
    # Slice 2 batch 5 seed (S2910). Three actionless tools from
    # td_handlers_agents.py. Batch 5 mixed shape across 4 tools:
    #   - brainstorm_tool (7 actions, mixed READ_ONLY + MUTATION) →
    #     per-action records below (Pattern C — session_tool /
    #     revenue_tracker_tool / bpaas_tool precedent).
    #   - web_fetch_tool + schedule_followup + legal_doc_drafter_agent
    #     (actionless schemas — `_schema_actions()` returns []) → uniform
    #     TOOL_DEFAULTS. Safety class + notes are doc-primary for these
    #     since the harness emits 0-action artifacts; metadata drives
    #     gap-map + audit surfaces rather than harness dispatch. Same
    #     precedent as web_search (S2906 batch 2).
    #
    # Authoring evidence:
    # - web_fetch_tool: `td_handlers_agents.py:426` — single-verb GET/POST
    #   surface. httpx.Client with capped timeout (1-60s), max_bytes
    #   (1024-2M), scheme allowlist (http/https), method allowlist
    #   (GET/POST). No platform ORM write. Returns {ok, status_code,
    #   final_url, content_type, body_bytes, truncated, body_text, ...}
    #   on success; {ok: false, error, ...} on error. Rigby Tool Gap
    #   Ledger #15, shipped S2865.
    # - schedule_followup: `td_handlers_agents.py:6389` — single-verb
    #   subscribe surface. Requires PA-context conversation_id (promoted
    #   by unified_pa_entrypoint per _CONTEXT_PROMOTE_KEYS) + one of
    #   execution_id / task_id. Writes AgentFollowupSubscription row via
    #   get_or_create (idempotent). Rejects non-PA dispatches (NULL
    #   conversation_id on AgentExecution) and cross-conversation
    #   subscribes. Returns stable 11-key contract per
    #   `_make_followup_response` (Session 1175 PR-2b-2).
    # - legal_doc_drafter_agent: `td_handlers_agents.py:295` — single-verb
    #   async dispatch surface (Session 1035). Routes through shared
    #   `dispatch_legal_draft` helper (S2803 Phase 3.0) → Celery legal
    #   queue. Gated by `disclaimer_acknowledged=True` in payload/context;
    #   `DisclaimerRequired` exception maps to `error_code=disclaimer_required`
    #   envelope. Writes `LegalDocumentDispatchLog` audit row on dispatch.
    'web_fetch_tool': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='env: external:network deps: httpx GET/POST; scheme/method '
              'allowlist; caps timeout+max_bytes; no ORM write; '
              'actionless schema',
    ),
    'schedule_followup': ToolDefaults(
        default_safety_class='WRITE_GATED',
        default_applicability='conditional',
        notes='deps: AgentFollowupSubscription get_or_create (idempotent); '
              'gate: pa_context (conversation_id promoted by '
              'unified_pa_entrypoint) + execution_id|task_id; '
              'actionless schema',
    ),
    'legal_doc_drafter_agent': ToolDefaults(
        default_safety_class='MUTATION',
        default_applicability='conditional',
        notes='deps: dispatch_legal_draft → Celery legal queue + '
              'LegalDocumentDispatchLog audit; gate: '
              'disclaimer_acknowledged=True; actionless schema',
    ),
    # Slice 2 batch 6b seed (S2912) — Slice 2 close. Dedicated scrutiny for
    # the agent-invocation-class dispatcher (peer of reasoning_engine_tool
    # shipped as batch 6b pre-req at S2911). Actionless schema, so
    # TOOL_DEFAULTS is the correct pattern (does NOT increment the S2905
    # per-action metadata-pattern-selection lint counter).
    #
    # Authoring evidence:
    # - universal_agent_tool: `td_handlers_agents.py:1771` — single-verb
    #   async dispatch surface (Session 1088; async since). Dispatches
    #   `execute_agent_task.apply_async(agent_name, task_text, context,
    #   queue='long_running')` UNCONDITIONALLY when `task` is non-empty
    #   (only guard is `raise ValueError` on empty task at `:1821-1823`).
    #   Fan-out surface: routes to any of 74 enabled AGENT_MAP entries;
    #   auto-substitutes unknown names → task-text extraction → fallback
    #   `ResearchAgent`. Surfaces substitution envelope
    #   (`agent_name_requested/effective/substituted`, `auto_routed`,
    #   `substitution_reason`) + async envelope (`task_id, mode='async'`).
    #   No dry_run/noop fast-path — post-merge verification is contract-
    #   level (schema/handler/metadata alignment) + worker recycle
    #   freshness per PLAYBOOK-7.4.4, NOT live dispatch. Batch 6b Rigby
    #   T0 SIGN Q3 explicitly rejected live-fire verification for this
    #   tool; Chris ratified Option A (contract-only, no dry_run add).
    'universal_agent_tool': ToolDefaults(
        default_safety_class='MUTATION',
        default_applicability='conditional',
        notes='deps: execute_agent_task.apply_async → Celery long_running '
              'queue; can invoke any of 74 AGENT_MAP agents; may cause '
              'DB writes / spider dispatches / external API calls / LLM '
              'cost depending on selected agent; auto-substitutes unknown '
              'agent_name (surfaces substitution envelope); no dry_run '
              'fast-path; actionless schema',
    ),
    # Slice 3 batch 1 seed (S2913). Opens the td_handlers_core sweep.
    # paid_interest_status is the only truly-actionless tool in the batch —
    # TOOL_DEFAULTS is the correct pattern (does NOT increment the S2905
    # per-action metadata-pattern-selection lint counter). The other 3 batch
    # 1 tools (platform_awareness_tool / persona_tool / platform_config_tool)
    # have action enums with unsafe siblings and land per-action records
    # below.
    #
    # Authoring evidence:
    # - paid_interest_status: `td_handlers_core.py:188` — no action switch;
    #   delegates to `core.services.fleet_paid_interest.evaluate_trigger_state`
    #   with optional payload (app_slug default 'signal-studio',
    #   manual_override default False). Pure config + ORM read; no writes,
    #   no Celery, no HTTP. Session 1138 (Decision 13 demand-gate readback).
    'paid_interest_status': ToolDefaults(
        default_safety_class='READ_ONLY',
        default_applicability='always',
        notes='deps: fleet_paid_interest.evaluate_trigger_state(app_slug, '
              'manual_override); reads APP_TRIGGER_CONFIG + PaidInterest '
              'ORM rows; no writes / no Celery / no HTTP; actionless schema',
    ),
}


# ── Per-(tool, action) records ──────────────────────────────────────────────
#
# T1a Phase 1 seed: two records against ``ops_tool`` verified live at S2796
# (per T1c §7.1). Phase 2 (S2903) extends with:
#   - ``ops_tool.focus_mode_update`` override (WRITE_GATED — the one
#     mutating action in ops_tool per validation doc §5)
#   - ``session_tool`` mixed-safety fan-out (3 READ_ONLY + 4 MUTATION) —
#     tool-level default not usable because the safety class splits per
#     action (verified in ``session_tool_validation.md`` §4 handler trace).

TOOL_ACTION_METADATA: Dict[Tuple[str, str], ToolActionMetadata] = {
    ('ops_tool', 'version'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: git-head; verified live S2796',
    ),
    ('ops_tool', 'recent_recycles'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: worker-recycle-log; verified live S2796',
    ),
    # ops_tool override: everything else is READ_ONLY (via TOOL_DEFAULTS)
    # EXCEPT focus_mode_update, which writes Focus Mode config
    # (`td_handlers_ops.py:317` calls ``set_config`` — a persisted write).
    # Classified WRITE_GATED because the write path exists; harness does not
    # dispatch WRITE_GATED at MVP so no auth-boundary assertion needed. Auth
    # enforcement location not verified at seed time; revisit if/when we add
    # WRITE_GATED harness dispatch.
    ('ops_tool', 'focus_mode_update'): ToolActionMetadata(
        safety_class='WRITE_GATED',
        applicability='conditional',
        notes='writes Focus Mode config; revisit: auth-boundary at harness-dispatch',
    ),
    # session_tool — mixed. Read side classified for harness dispatch;
    # write side flagged for future MUTATION coverage (not exercised at MVP).
    ('session_tool', 'health_check'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ChatConversation; default action per handler',
    ),
    ('session_tool', 'list_recent'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ChatConversation queryset (F-S-3 mitigation shipped S2728)',
    ),
    ('session_tool', 'whoami'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: current conversation binding; provenance surface',
    ),
    ('session_tool', 'create_fresh'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='creates a new ChatConversation row',
    ),
    ('session_tool', 'retire'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='sets session_active=False; F-S-6 mitigation shipped S2728',
    ),
    ('session_tool', 'set_active'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='sets session_active=True on target conversation',
    ),
    ('session_tool', 'seed'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes ChatMessage with [SYSTEM SEED] marker',
    ),
    # revenue_tracker_tool — mixed. stats + list are ORM aggregates/reads
    # against Revenue; create writes a new Revenue row (MUTATION).
    # No TOOL_DEFAULTS entry — per-action records are the safety source.
    # Verified via `td_handlers_agents.py:1605` (_handle_revenue_tracker).
    ('revenue_tracker_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Revenue ORM aggregate',
    ),
    ('revenue_tracker_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Revenue ORM query',
    ),
    ('revenue_tracker_tool', 'create'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='creates a new Revenue row',
    ),
    # Slice 2 batch 4 seed (S2908). Four mixed-safety tools from
    # td_handlers_agents.py, scoped to READ_ONLY subset for validation-doc
    # coverage this ship; mutation actions seeded here as per-action records
    # so the harness never dispatches them (resolve_safety() returns MUTATION
    # / IRREVERSIBLE → harness skips).
    #
    # Batch composition rationale (per Rigby S2908 T0 SIGN AGREE-with-edits
    # + Chris-ratified Fold A commitment from S2907): mixed-tool scoped to
    # READ_ONLY subset breaks the S2906+S2907 uniform-READ_ONLY-multi-action
    # precedent. Per-action records for ALL 20 actions (13 READ_ONLY + 7
    # mutation) — Pattern C precedent from revenue_tracker_tool. Chosen over
    # Pattern A (TOOL_DEFAULTS + mutation overrides) to keep this session
    # UNIFORM per-action (does NOT increment the S2905 metadata-pattern-
    # selection lint counter — mixed-pattern coexistence stays 1/3 sweep
    # sessions post-S2908).
    #
    # Authoring evidence:
    # - bpaas_tool: `td_handlers_agents.py:6268` — 4 actions. get_schema +
    #   get_example return in-memory constants (BUILD_PACKET_SCHEMA /
    #   NORMAN_HANDYMAN_EXAMPLE). create_project + generate_close_pack
    #   invoke packet_service side-effects (project creation + SOW/proposal
    #   artifact generation).
    # - davinci_tool: `td_handlers_agents.py:4435` — 6 actions. health /
    #   status / result / jobs / grades all query-only via ResolveNodeClient
    #   or COLOR_GRADE_PRESETS constant. render starts an external DaVinci
    #   Resolve render job (async side-effect on external system).
    # - obs_tool: `td_handlers_agents.py:4494` — 6 actions. health / status /
    #   last are bridge GETs against the local OBS bridge. start / stop
    #   toggle recording state (bridge POST). upload_last uploads the newest
    #   recording file and creates a VideoHistory row.
    # - media_tool: `td_handlers_agents.py:4161` — 4 actions. list / detail /
    #   stats are user-scoped ORM reads across ImageHistory / VideoHistory /
    #   AudioHistory. delete destroys the row via `obj.delete()` — no
    #   confirm flag, no soft-delete: classified IRREVERSIBLE.
    #
    # dependency_surface (doc-note discipline per Rigby T0 SIGN edit — kept
    # as validation-doc annotation, NOT a metadata field this ship):
    # - bpaas_tool: internal (packet_service + BUILD_PACKET_SCHEMA constants)
    # - davinci_tool: external_bridge (ResolveNodeClient → resolve_node HTTP)
    # - obs_tool: external_bridge (`_obs_bridge_request` → local OBS bridge)
    # - media_tool: internal (Django ORM)
    ('bpaas_tool', 'get_schema'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: BUILD_PACKET_SCHEMA constant',
    ),
    ('bpaas_tool', 'get_example'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: NORMAN_HANDYMAN_EXAMPLE constant',
    ),
    ('bpaas_tool', 'create_project'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='creates ProjectWorkspace + repos + preview env + magic link '
              'via packet_service.create_project_from_packet',
    ),
    ('bpaas_tool', 'generate_close_pack'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='generates SOW + delivery checklist + proposal via '
              'packet_service.generate_close_pack',
    ),
    ('davinci_tool', 'health'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ResolveNodeClient.health_check (external_bridge)',
        bridge='resolve_node',
    ),
    ('davinci_tool', 'status'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ResolveNodeClient.get_status (external_bridge)',
        bridge='resolve_node',
    ),
    ('davinci_tool', 'result'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ResolveNodeClient.get_result_url (external_bridge)',
        bridge='resolve_node',
    ),
    ('davinci_tool', 'jobs'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ResolveNodeClient.list_jobs (external_bridge)',
        bridge='resolve_node',
    ),
    ('davinci_tool', 'grades'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: COLOR_GRADE_PRESETS constant (internal)',
    ),
    ('davinci_tool', 'render'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='starts external DaVinci Resolve render job via '
              'ResolveNodeClient.start_render',
    ),
    ('obs_tool', 'health'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: OBS bridge GET /health (external_bridge)',
        bridge='obs',
    ),
    ('obs_tool', 'status'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: OBS bridge GET /v1/recording/status (external_bridge)',
        bridge='obs',
    ),
    ('obs_tool', 'last'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: OBS bridge GET /v1/recording/last (external_bridge)',
        bridge='obs',
    ),
    ('obs_tool', 'start'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='POST /v1/recording/start — toggles OBS recording state',
    ),
    ('obs_tool', 'stop'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='POST /v1/recording/stop — toggles OBS recording state',
    ),
    ('obs_tool', 'upload_last'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='POST /v1/recording/upload_last — uploads file + creates '
              'VideoHistory row',
    ),
    ('media_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ImageHistory / VideoHistory / AudioHistory ORM read',
    ),
    ('media_tool', 'detail'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: user-scoped media row lookup by UUID',
    ),
    ('media_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: media row counts by type',
    ),
    ('media_tool', 'delete'): ToolActionMetadata(
        safety_class='IRREVERSIBLE',
        applicability='always',
        notes='destroys media row via obj.delete() — no confirm flag, '
              'no soft-delete',
    ),
    # Slice 2 batch 5 per-action records (S2910). brainstorm_tool is the
    # one multi-action tool in batch 5 (schema `action` enum at
    # `pa_tool_schemas.py:65-69`). Six READ_ONLY discovery/search
    # actions + one MUTATION create action that dispatches a
    # ThinkingAgent brainstorm conversation via Celery long_running
    # queue. Per-action pattern (Pattern C) mirrors bpaas_tool + session_tool
    # + revenue_tracker_tool precedent — chosen because create's MUTATION
    # class deviates from the read-only default the other 6 actions share.
    # Verified via `td_handlers_agents.py:6136` (_handle_brainstorm).
    #
    # dependency_surface (doc-note discipline per S2908 Rigby T0 SIGN):
    # - all READ_ONLY actions: internal (BrainstormSearchService ORM reads
    #   against Discussion/Panel/BrainstormConversation)
    # - create: internal (Celery long_running queue dispatch of
    #   ThinkingAgent via execute_agent_task.apply_async)
    ('brainstorm_tool', 'search'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: BrainstormSearchService.search; '
              'requires: query (raises ValueError if missing)',
    ),
    ('brainstorm_tool', 'recent'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: BrainstormSearchService.get_recent_summaries; '
              'defaults days=7 limit=20',
    ),
    ('brainstorm_tool', 'details'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: BrainstormSearchService.get_conversation_insights; '
              'requires: conversation_id | id (raises ValueError if missing)',
    ),
    ('brainstorm_tool', 'by_category'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: BrainstormSearchService.get_ideas_by_category; '
              'requires: category (raises ValueError if missing)',
    ),
    ('brainstorm_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: BrainstormSearchService.list_conversations; '
              'defaults days=30 offset=0 limit=50 (cap 200)',
    ),
    ('brainstorm_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: BrainstormSearchService.get_stats; defaults days=30',
    ),
    ('brainstorm_tool', 'create'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='deps: execute_agent_task.apply_async(ThinkingAgent) via '
              'Celery long_running queue; requires: topic OR query '
              '(non-empty after strip)',
    ),
    # Slice 2 batch 6a per-action records (S2911). Four mixed-safety tools
    # from td_handlers_agents.py, scoped to READ_ONLY subset for validation-
    # doc coverage this ship. Batch 6a excludes the two agent-invocation
    # tools (reasoning_engine_tool + universal_agent_tool) — those ship in
    # batch 6b with dedicated scrutiny for LLM cost + agent-execution side
    # effects (per Claude+Rigby T0 SIGN AGREE-with-edits + Chris ratify).
    #
    # Batch composition rationale (per Rigby S2911 T0 SIGN Q1 AGREE):
    #   - opportunity_manager_tool / task_manager_tool / video_history_tool
    #     have mixed READ_ONLY + mutation actions; scoped-to-READ_ONLY-subset
    #     via per-action records prevents accidental writes at the schema
    #     contract layer, not just intent (S2908 shape-break precedent).
    #   - pipeline_orchestrator_tool has a single READ_ONLY action; per-action
    #     record chosen over TOOL_DEFAULTS to keep this session's pattern
    #     UNIFORM per-action (does NOT increment the S2905 metadata-pattern-
    #     selection lint counter).
    #
    # Rigby T0 SIGN Q4 zoom-out findings tracked (not acted this ship):
    #   - task_manager_tool.create HIDDEN MUTATION: implicitly creates an
    #     Opportunity row when payload lacks opportunity_id (handler
    #     `td_handlers_agents.py:1452-1464`). Documented in
    #     `task_manager_tool_validation.md` §5a — MUTATION containment.
    #   - opportunity_manager_tool.delete CASCADES to linked OpportunityTask
    #     rows (handler `:1369-1377`) — classified IRREVERSIBLE, aligning
    #     with `media_tool.delete` precedent (S2908).
    #   - Schema↔handler drift on `reasoning_engine_tool` (schema advertises
    #     {query, reasoning_type}; handler dispatches on action in
    #     {status, thoughts, trigger}) — 1st confirmed instance of Rigby
    #     Q4 concern #3. Blocks batch 6b until pre-fix.
    #
    # Authoring evidence:
    # - opportunity_manager_tool: `td_handlers_agents.py:1178` — 6 actions
    #   (list/get/stats READ_ONLY; update_status/create MUTATION; delete
    #   IRREVERSIBLE via cascade). Scope param defaults to 'mine' (user
    #   filter); 'all' opts into platform-wide pool (Session 1222 P4).
    # - task_manager_tool: `td_handlers_agents.py:1384` — 6 actions
    #   (list/stats READ_ONLY; create/update/complete MUTATION; delete
    #   IRREVERSIBLE). Base queryset always user-filtered when user_id
    #   present. `complete` sets status='won' (domain semantics).
    # - pipeline_orchestrator_tool: `td_handlers_agents.py:1558` — 1
    #   action (status). Aggregate reads against Initiative model
    #   (by_stage 1-5 + by_status + active count).
    # - video_history_tool: `td_handlers_agents.py:4551` — 7 actions
    #   (list/search/detail/resolve/transcript_status READ_ONLY;
    #   transcribe/content_pack MUTATION dispatching Celery async jobs).
    #   transcribe idempotent-guards on existing queued/running transcript;
    #   content_pack requires prior completed transcript.
    ('opportunity_manager_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Opportunity ORM query; scope="mine" (default) filters '
              'by user_id, scope="all" surfaces platform-wide lead pool '
              '(spider-ingested rows owned by system user)',
    ),
    ('opportunity_manager_tool', 'get'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: Opportunity.objects.filter(id=opp_id).first(); '
              'requires: opportunity_id | id (raises ValueError if missing)',
    ),
    ('opportunity_manager_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Opportunity aggregate (by_status + by_type + '
              'total_potential_revenue); scope="all" adds owner_breakdown',
    ),
    ('opportunity_manager_tool', 'update_status'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes Opportunity.status field via save(update_fields); '
              'requires: id + status (validated against '
              'active|pending|applied|accepted|rejected|expired)',
    ),
    ('opportunity_manager_tool', 'create'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='creates a new Opportunity row; requires: user_id + title '
              '(non-empty after strip)',
    ),
    ('opportunity_manager_tool', 'delete'): ToolActionMetadata(
        safety_class='IRREVERSIBLE',
        applicability='conditional',
        notes='destroys Opportunity row via opp.delete() — CASCADE deletes '
              'linked OpportunityTask rows; no confirm flag, no soft-delete; '
              'requires: id | opportunity_id',
    ),
    ('task_manager_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: OpportunityTask ORM query; user-scoped when user_id '
              'present; status + priority optional filters',
    ),
    ('task_manager_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: OpportunityTask aggregate (by_status + by_priority + '
              'total)',
    ),
    ('task_manager_tool', 'create'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='creates OpportunityTask row; HIDDEN MUTATION: implicitly '
              'creates a standalone Opportunity row when opportunity_id '
              'is absent (to satisfy FK); requires: user_id + title',
    ),
    ('task_manager_tool', 'update'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes OpportunityTask fields (status | priority | title | '
              'description) via save(update_fields); requires: id; '
              'Session 1228 PR-A key-in-payload guard prevents accidental '
              'field clear from LLM autofill=""',
    ),
    ('task_manager_tool', 'complete'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='sets OpportunityTask.status="won" (domain-specific '
              'complete semantics); requires: id',
    ),
    ('task_manager_tool', 'delete'): ToolActionMetadata(
        safety_class='IRREVERSIBLE',
        applicability='conditional',
        notes='destroys OpportunityTask row via task.delete() — no confirm '
              'flag, no soft-delete; requires: id',
    ),
    ('pipeline_orchestrator_tool', 'status'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Initiative aggregate (by_stage 1-5 + by_status + '
              'initiatives_active where current_stage<5 AND status=ACTIVE)',
    ),
    ('video_history_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: VideoHistory ORM query; user-scoped when user_id '
              'present; video_type + status filters; defaults status='
              '"completed"; limit capped at 50',
    ),
    ('video_history_tool', 'search'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: VideoHistory ORM Q-filter on prompt|original_filename '
              'icontains; user-scoped + status="completed"; '
              'requires: query (raises ValueError if missing)',
    ),
    ('video_history_tool', 'detail'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: VideoHistory single-row lookup by id OR sequential_number '
              '(sequential is computed via order_by created_at index); '
              'requires: id | sequential_number',
    ),
    ('video_history_tool', 'resolve'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: core.video_resolver.resolve_video (VideoHistory lookup); '
              'accepts: id | sequential_number | query (as URL)',
    ),
    ('video_history_tool', 'transcript_status'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: VideoTranscript ORM read by transcript_id, or latest '
              'by video ref (id|sequential_number); text truncated at 3000 '
              'chars when status=completed',
    ),
    ('video_history_tool', 'transcribe'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='creates VideoTranscript row + dispatches transcribe_video_task '
              'to Celery (Whisper async); idempotent-guarded against '
              'existing queued|running transcript; requires: id | '
              'sequential_number',
    ),
    ('video_history_tool', 'content_pack'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='dispatches generate_video_content_pack_task to Celery '
              '(async LLM-heavy content-pack gen); requires: id | '
              'sequential_number + a completed VideoTranscript',
    ),
    # reasoning_engine_tool drift-fix per-action records (S2911 batch 6b
    # pre-req PR). Schema at pa_tool_schemas.py:294-315 was aligned to
    # handler behavior this ship — dead params (query + reasoning_type)
    # removed, action enum added matching handler dispatch branches at
    # td_handlers_agents.py:5374-5418 (status | thoughts | trigger).
    # Direction: schema→handler (handler was authoritative with real
    # dispatch logic; schema params were never referenced anywhere in
    # handler code).
    #
    # Rigby T0 SIGN Q4b (S2911): reasoning_engine schema↔handler drift
    # was 1st confirmed instance of schema↔handler drift class. This PR
    # closes the drift + establishes reasoning_engine as substrate for
    # batch 6b (agent-invocation scrutiny lane).
    ('reasoning_engine_tool', 'status'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: hardcoded {engine, status} envelope; ThinkingAgent '
              'registry lookup not required for status',
    ),
    ('reasoning_engine_tool', 'thoughts'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: AgentExecution ORM query filtered by '
              'agent_name="ThinkingAgent"; defaults limit=10',
    ),
    ('reasoning_engine_tool', 'trigger'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='deps: registry.execute_agent(ThinkingAgent, {task: "Reflect '
              'on recent system activity..."}) — invokes real LLM-backed '
              'ThinkingAgent reflection cycle (LLM cost)',
    ),
    # Slice 3 batch 1 per-action records (S2913). First batch of the
    # td_handlers_core.py sweep. 3 mixed-safety tools scoped to READ_ONLY
    # subset via per-action records; unsafe siblings (HTTP + LLM-agent
    # execution) declared MUTATION so harness resolve_safety() skips at
    # dispatch. Actionless peer (paid_interest_status) lands as
    # TOOL_DEFAULTS above.
    #
    # Batch composition rationale (per Rigby S2913 T0 SIGN Q1 AGREE-with-
    # edits + T1 V2 AGREE-with-edits):
    #   - Slice 3 has meaningfully denser side-effect surfaces than Slice 2
    #     (network calls, Celery dispatch, row creates). Batch 1 opens
    #     conservatively — 4 pure-read invocations with unsafe siblings
    #     explicitly pinned + excluded via safety class.
    #   - Explicit action pinning (not "default action is safe" invariant)
    #     defends against future default drift per Rigby T1 V4 zoom-out.
    #
    # Rigby T0/T1 SIGN Q4 zoom-out findings tracked (forward-carry, not
    # acted this ship):
    #   - Concern C (schema↔doc drift on core tools): platform_awareness_tool
    #     + platform_config_tool are GAP_MAP-flagged "actions_not_mentioned
    #     _in_description". 1st instance in Slice 3 batch 1 → forward-carry
    #     note only; promote to slice-level fold candidate at 2nd instance.
    #   - Concern E (FT-5 minimal_safe_args_v2 forcing function): none of
    #     the 4 batch 1 picks required handcrafting beyond TOOL_DEFAULTS +
    #     default-action-select. No trigger this batch.
    #
    # Authoring evidence:
    # - platform_awareness_tool: `td_handlers_core.py:823` — 7 actions.
    #   get_manifest (default) + list_routes + check_route + system_overview
    #   + list_api_dependencies + tool_registry all read from
    #   core.views_app_manifest (get_manifest_data / _load_manifest /
    #   _summarize_tool_schemas). verify_deploy is admin-only + fires HTTP
    #   via core.views_deploy_verify.run_verification against DEPLOY_BASE_URL.
    #   Session 1069 base + Session 1228 PR-A auth_required coerce.
    # - persona_tool: `td_handlers_core.py:1189` — 2 actions.
    #   list is a pure ORM read against AgentModel (filter is_active=True,
    #   exclude AGENT_MAP names, category filter, top-50 slice + Counter
    #   summary). invoke routes through AgentRouter (LLM-backed persona
    #   execution). Session 1088 (139 DB-only personas).
    # - platform_config_tool: `td_handlers_core.py:1274` — 5 actions.
    #   overview (default) + llm_providers + env_vars + feature_flags all
    #   read from django.conf.settings + os.environ (secrets masked via
    #   local `_mask()` helper). web_config fires HTTP via urllib.request
    #   against WEB_SERVICE_URL (cross-service config compare). Session 1069.
    ('platform_awareness_tool', 'get_manifest'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: core.views_app_manifest.get_manifest_data(user) | '
              '_load_manifest(); reads routes + studios + capabilities + '
              'api_dependencies; RBAC-filtered when user_id present',
    ),
    ('platform_awareness_tool', 'list_routes'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: filtered slice of manifest.routes; optional category + '
              'auth_required filters (Session 1228 PR-A coerce_optional_bool '
              'defends against LLM autofill=False)',
    ),
    ('platform_awareness_tool', 'check_route'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: manifest.routes lookup by path; requires: path '
              '(empty-string path always misses)',
    ),
    ('platform_awareness_tool', 'system_overview'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: manifest aggregate (routes_by_category + studio_count '
              '+ capabilities + build_sha + api_dependency counts)',
    ),
    ('platform_awareness_tool', 'verify_deploy'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='deps: core.views_deploy_verify.run_verification against '
              'DEPLOY_BASE_URL (HTTP); admin-only gate '
              '(user.is_superuser or user.is_staff); requires: caller user_id',
    ),
    ('platform_awareness_tool', 'list_api_dependencies'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: manifest.api_dependencies; optional path filter + '
              'writes_only filter (mutation endpoints only)',
    ),
    ('platform_awareness_tool', 'tool_registry'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: core.views_app_manifest._summarize_tool_schemas(); '
              'returns registered PA tool names + descriptions + action enums',
    ),
    ('persona_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: AgentModel ORM query (is_active=True, exclude AGENT_MAP '
              'names via AgentRouter.AGENT_MAP.keys()); optional category '
              'filter; top-50 by (agent_type, name); Counter over agent_type '
              'for categories summary; descriptions truncated to 150 chars',
    ),
    ('persona_tool', 'invoke'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='deps: AgentRouter.route(persona_name, task, context) — '
              'invokes real LLM-backed persona execution via '
              'DynamicPersonaAgent fallback; LLM cost; may side-effect '
              'downstream; requires: persona_name + task',
    ),
    ('platform_config_tool', 'overview'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: django.conf.settings + os.environ; masks secret keys '
              'via local _mask() helper (KEY/SECRET/TOKEN/PASSWORD/'
              'CREDENTIAL/DSN/DATABASE_URL/REDIS_URL/BROKER_URL)',
    ),
    ('platform_config_tool', 'llm_providers'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: os.environ read for 6 LLM provider keys (OpenAI + '
              'Anthropic + Together AI + DeepSeek + Gemini + Ollama); '
              'reports configured flag + masked key prefix',
    ),
    ('platform_config_tool', 'env_vars'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: full os.environ enumeration; skips noisy system vars '
              '(__/npm_/LESS_/LS_ prefixes); masks secret values via '
              '_mask() helper',
    ),
    ('platform_config_tool', 'feature_flags'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: django.conf.settings read for 7 explicit flag attrs '
              '(LUNGS_ENFORCE_HARD_LIMIT / CELERY_TASK_EVENT_RETENTION_DAYS '
              '/ LLM_CALL_LOG_RETENTION_DAYS / BODY_THROTTLE_MAX_DELAY_'
              'SECONDS / CONTENT_AUTO_PUBLISH / SPIDER_ENABLED / DREAM_ENABLED)',
    ),
    ('platform_config_tool', 'web_config'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='deps: urllib.request GETs to WEB_SERVICE_URL /api/v1/health/ '
              '+ /api/internal/config-snapshot/ (HTTP; 5s timeout); cross-'
              'service config compare; may fail-loud when web service is '
              'unreachable or config-snapshot endpoint undeployed',
    ),
    # Slice 3 batch 2 per-action records (S2913, second batch this session).
    # 4 mixed-safety tools continuing the batch 1 scoped-to-READ_ONLY-subset
    # shape. Rigby T1 SIGN AGREE-with-edits (short cycle — batch 2 mirrors
    # batch 1 shape; Rigby had warm context).
    #
    # Course-correction applied post-Rigby-verdict: `conversation_tool.search`
    # reclassified from Rigby-assumed READ_ONLY to MUTATION after Claude's
    # direct handler read (`td_handlers_core.py:2038`) confirmed
    # `EmbeddingService.create_embedding(query, agent_name='conversation_tool')`
    # is invoked on every search call. This is LLM cost, not pure ORM. Per
    # feedback_verify_rigby_tool_runs_before_trusting_sign — Rigby V1 verdict
    # softened to include this factual correction. `remember_tool.search`
    # remains READ_ONLY (verified pure `.filter(content__icontains=query)`
    # at handler line 2345-2348 — no embedding).
    #
    # Batch 2 composition rationale (per Rigby T1 SIGN + Claude course-correct):
    #   - active_repo_tool: 1R + 2M (get pure cache+ORM read; set writes cache
    #     with 7-day TTL; clear deletes cache).
    #   - db_health_tool: 7R at env='local' + env='prod' escalation to urllib
    #     RPC documented-not-tested. Per Rigby V2 AGREE-with-edits — safety
    #     class classifies intrinsic action (env='local' default is safe);
    #     env='prod' escalation noted in per-action metadata.
    #   - conversation_tool: 2R + 3M (get + recent pure ORM reads; search LLM
    #     embedding; summary async Celery; pin_memory row create + embed).
    #   - remember_tool: 2R + 1M + 1IR (list + search pure ORM reads; save
    #     row create; delete row destroy).
    #
    # Rigby T1 SIGN Q4 zoom-out findings (forward-carry, not acted this ship):
    #   - Concern C (schema↔doc drift): batch 2 hits ZERO new instances —
    #     GAP_MAP flags all four batch 2 tools with no drift lints. Slice 3
    #     drift count stays at 2 (from batch 1 only). Sub-threshold for
    #     slice-level fold candidate.
    #   - db_health env='prod' path is a NEW dependency-surface class
    #     (env-parameter-dependent MUTATION) not seen in batch 1. Per
    #     Rigby V4 AGREE-with-edits — documented-not-tested; no substrate
    #     change (D6 moratorium).
    #
    # Authoring evidence:
    # - active_repo_tool: `td_handlers_core.py:89` — 3 actions.
    #   get returns cache.get(cache_key) + workspace lookup snapshot. set
    #   writes cache.set with _ACTIVE_REPO_TTL_SECONDS (7 days). clear
    #   writes cache.delete. Session 1119 carryover #4.
    # - db_health_tool: `td_handlers_core.py:1442` — 7 actions.
    #   Default env='local' path is `_handle_db_health_local` at :1469
    #   (connection.introspection, call_command('showmigrations'), row
    #   counts, pgvector extension). env='prod' path is
    #   `_delegate_remote_db_health` at :1788 (urllib.request.urlopen to
    #   PA_DB_HEALTH_RPC_URL, Token auth, 30s timeout). Session 1069 base
    #   + Session 1249 P2(a) prod RPC client.
    # - conversation_tool: `td_handlers_core.py:1974` — 5 actions.
    #   get (paginated ChatConversation read). search (EmbeddingService
    #   embed + pgvector semantic + keyword fallback ConversationMemory
    #   + ChatConversation dedupe). summary (async
    #   summarize_conversation_task.apply_async via apply_async_with_actor
    #   at :2119). pin_memory (create_deliverable + ConversationMemory.
    #   objects.create at :2160 + embed via EmbeddingService). recent
    #   (aggregate distinct conversation_ids). Session 1086 pagination.
    # - remember_tool: `td_handlers_core.py:2210` — 4 actions.
    #   save (UserMemoryContext.objects.create at :2273 + dedup via
    #   content_hash + cache.clear + OpsRun event). list (UserMemoryContext
    #   filter+top-20 read). delete (UserMemoryContext.filter.delete +
    #   cache.clear). search (UserMemoryContext.filter(content__icontains)
    #   — pure ORM, no embedding).
    ('active_repo_tool', 'get'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: cache.get(_active_repo_cache_key(user_id)); returns '
              'cached ProjectWorkspace snapshot with set flag; no DB write',
    ),
    ('active_repo_tool', 'set'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes cache.set with _ACTIVE_REPO_TTL_SECONDS (7 days); '
              'requires: repo (workspace name / repo_id); resolves '
              'ProjectWorkspace user-scoped then falls back to name-only',
    ),
    ('active_repo_tool', 'clear'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='writes cache.delete(_active_repo_cache_key(user_id)); '
              'reports cleared=True when cache had a value',
    ),
    ('db_health_tool', 'overview'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='READ_ONLY when env=local (default); env=prod escalates to '
              'urllib RPC (documented not tested this batch); deps: '
              'connection.vendor + call_command showmigrations + core '
              'table counts',
    ),
    ('db_health_tool', 'migrations'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='READ_ONLY when env=local (default); env=prod escalates to '
              'urllib RPC (documented not tested this batch); deps: '
              'MigrationLoader + showmigrations diff',
    ),
    ('db_health_tool', 'tables'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='READ_ONLY when env=local (default); env=prod escalates to '
              'urllib RPC (documented not tested this batch); deps: raw '
              'SQL row counts across canonical core tables',
    ),
    ('db_health_tool', 'pgvector'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='READ_ONLY when env=local (default); env=prod escalates to '
              'urllib RPC (documented not tested this batch); deps: '
              'pg_extension row read + embedding_count aggregate',
    ),
    ('db_health_tool', 'verify_table'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='READ_ONLY when env=local (default); env=prod escalates to '
              'urllib RPC (documented not tested this batch); deps: '
              'information_schema lookup; requires: table_name',
    ),
    ('db_health_tool', 'search_tables'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='READ_ONLY when env=local (default); env=prod escalates to '
              'urllib RPC (documented not tested this batch); deps: '
              'information_schema.tables prefix filter (default core_)',
    ),
    ('db_health_tool', 'learning_stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='READ_ONLY when env=local (default); env=prod escalates to '
              'urllib RPC (documented not tested this batch); deps: '
              'ReadbackLog + Consultation + UserAgentLearning aggregate '
              '(learning-feedback-loop introspection)',
    ),
    ('conversation_tool', 'get'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: ChatConversation ORM query filter by conversation_id; '
              'paginated via offset+page_size (max 30 turns/page, 1000-char '
              'content cap per turn); requires: conversation_id',
    ),
    ('conversation_tool', 'search'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='deps: EmbeddingService.create_embedding(query) — LLM cost '
              'via query-side embedding generation at handler line 2038 '
              '(before pgvector CosineDistance semantic search); ChatConv '
              'keyword fallback dedupe against semantic hits; requires: '
              'query',
    ),
    ('conversation_tool', 'summary'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='deps: summarize_conversation_task.apply_async_with_actor '
              'at handler line 2119 → Celery async LLM summarization; '
              'returns task_id + mode=async; requires: conversation_id',
    ),
    ('conversation_tool', 'pin_memory'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='deps: create_deliverable + ConversationMemory.objects.create '
              'at handler line 2160 + EmbeddingService.create_embedding for '
              'the pinned content (LLM cost); requires: pin_title + '
              'pin_content (both non-empty after strip)',
    ),
    ('conversation_tool', 'recent'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ChatConversation aggregate filtered to conversation_id '
              'starts-with "pa-"; user-scoped when user_id present; '
              'distinct conversation_ids with Max(created_at) as '
              'last_activity',
    ),
    ('remember_tool', 'list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: UserMemoryContext.filter(user=user).order_by('
              '-importance, -created_at)[:20] + total count aggregate; '
              'no writes; requires: caller user_id (fail-loud '
              'permission_denied envelope if missing)',
    ),
    ('remember_tool', 'search'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: UserMemoryContext.filter(user=user, content__icontains'
              '=query).order_by(-importance)[:10] — pure ORM text search '
              '(no embedding, no LLM cost); requires: query + caller '
              'user_id',
    ),
    ('remember_tool', 'save'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes UserMemoryContext row via .objects.create at handler '
              'line 2273; dedup via content_hash (sha256[:16] of '
              'lowercased content+memory_type) — duplicate returns '
              'status=duplicate_updated without new row; cap enforced '
              'via MEMORY_MAX_ITEMS env (default 200); requires: content '
              '+ caller user_id',
    ),
    ('remember_tool', 'delete'): ToolActionMetadata(
        safety_class='IRREVERSIBLE',
        applicability='conditional',
        notes='destroys UserMemoryContext row via '
              '.filter(user=user, id=memory_id).delete(); user-scoped '
              'so cross-user delete not possible; clears '
              'memory_context_service cache; requires: memory_id + '
              'caller user_id',
    ),
    # Slice 3 batch 3 per-action records (S2913, third batch this session —
    # session close batch). 4 mixed-safety tools; batch 3 mirrors batch 1+2
    # shape unchanged. Rigby T1 SIGN AGREE-with-edits (short cycle — batch
    # 3 close-out; Rigby had full context from batches 1+2).
    #
    # Rigby T1 SIGN V1 verify-before-commit flags — Claude verified all 3:
    # (a) messaging_tool read-receipt: VERIFIED no read-receipt update on
    #     get_thread/list_threads/unread_count paths. Participation.
    #     unread_count is READ, not written. See doc §5a for confirmation.
    # (b) messaging_tool send_message: NOT in schema action enum but handler
    #     path exists at :3850 (Session 1253 PR 4 defense-in-depth gate via
    #     MESSAGING_TOOL_ALLOW_SEND=False). Added as MUTATION metadata to
    #     document the code path even though it's schema-inaccessible.
    # (c) governance_tool decision_create naming: VERIFIED clean — schema
    #     uses `decision_create` (singular); handler DECISIONS_MAP at :3770
    #     maps to underlying `'create'` action. Not drift.
    # (d) LLM calls on read actions: VERIFIED no LLM/agent dispatch or
    #     summarization on any covered read action (learning is pure
    #     PAToolInsight ORM; dream is pure AgentDream ORM; governance
    #     read paths are direct FailureSignature/AuditRemediationTask
    #     ORM + gateway forwarding to boardroom/human_decisions read
    #     handlers).
    #
    # Batch 3 composition (per Rigby T1 SIGN):
    #   - messaging_tool: 3 schema-enum actions all READ_ONLY + 1 handler-
    #     only schema-hidden send_message MUTATION (defense-in-depth).
    #   - learning_tool: 4R + 2M (list_candidates/list_approved/list_expired
    #     /stats read PAToolInsight; approve/reject .update() safety_class).
    #   - dream_tool: 3R + 3M (list_top/details/stats read AgentDream;
    #     approve fires post_save signal → promote_to_initiative +
    #     execute_single_dream.delay async; dismiss updates outcome only;
    #     create writes AgentDream row).
    #   - governance_tool: 11R + 6M (gateway pattern via BOARDROOM_MAP +
    #     DECISIONS_MAP; also 3 direct-dispatch actions — stats/
    #     failure_signatures/remediation_tasks).
    #
    # Authoring evidence:
    # - messaging_tool: `td_handlers_core.py:3834` — 3 schema actions +
    #   send_message hidden path. Session 1253 PR 4 defense-in-depth gate.
    # - learning_tool: `td_handlers_core.py:1904` — 6 actions against
    #   PAToolInsight. approve/reject use .update() (bulk field write).
    # - dream_tool: `td_handlers_core.py:282` — 6 actions against
    #   AgentDream. approve at :348 → post_save → promote_to_initiative
    #   + execute_single_dream.delay (Celery dispatch cascade). dismiss
    #   at :365 only updates outcome fields. create at :380 writes new row.
    # - governance_tool: `td_handlers_core.py:3702` — 17 actions gateway
    #   pattern. BOARDROOM_MAP (10 actions → boardroom_tool). DECISIONS_MAP
    #   (4 actions → human_decisions_tool). Direct: stats/
    #   failure_signatures/remediation_tasks. Session 1079 base + Session
    #   1100 read-only extensions.
    ('messaging_tool', 'list_threads'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ThreadParticipant ORM query filtered by user + '
              'archived=False; joins last DirectMessage per thread; '
              'reads participant.unread_count (no write); top-20 '
              'ordered by thread.updated_at desc',
    ),
    ('messaging_tool', 'get_thread'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: ThreadParticipant lookup by (thread_id, user) then '
              'DirectMessage top-50 ordered by created_at; NO read-receipt '
              'mutation on fetch (verified S2913 Rigby T1 V1); dual-'
              'semantic error envelope preserves participant enumeration '
              'oracle (Rigby SIGN F2); requires: thread_id',
    ),
    ('messaging_tool', 'unread_count'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: ThreadParticipant aggregate sum(unread_count) over '
              'user, archived=False, is_muted=False; no writes',
    ),
    ('messaging_tool', 'send_message'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='NOT in schema action enum but handler path exists at '
              ':3850 (Session 1253 PR 4 defense-in-depth). Gated by '
              'settings.MESSAGING_TOOL_ALLOW_SEND=False (default). If '
              'enabled: creates MessageThread + ThreadParticipant + '
              'DirectMessage rows + broadcasts WebSocket. Requires: '
              'recipient_username + message',
    ),
    ('learning_tool', 'list_candidates'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: PAToolInsight ORM query filter '
              'safety_class="candidate"; optional tool_name filter; '
              'top-N ordered by evidence_count desc, confidence desc; '
              'no LLM cost',
    ),
    ('learning_tool', 'list_approved'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: PAToolInsight ORM query filter '
              'safety_class="approved"; optional tool_name filter; '
              'top-N ordered by confidence desc, evidence_count desc',
    ),
    ('learning_tool', 'list_expired'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: PAToolInsight ORM query filter '
              'expires_at__lte=now(); optional tool_name filter; '
              'top-N ordered by expires_at desc',
    ),
    ('learning_tool', 'approve'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes PAToolInsight.safety_class="approved" via .update() '
              '(bulk field write, not .save); requires: id (UUID); guard '
              'filter includes safety_class="candidate" so already-'
              'approved rows are no-op',
    ),
    ('learning_tool', 'reject'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes PAToolInsight.safety_class="rejected" via .update() '
              '(bulk field write); requires: id (UUID); guard filter '
              'includes safety_class="candidate" so already-decided '
              'rows are no-op',
    ),
    ('learning_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: PAToolInsight aggregate group by (safety_class, '
              'insight_type) with Count; totals dict for candidate/'
              'approved/rejected',
    ),
    ('dream_tool', 'list_top'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: AgentDream ORM query filter composite_score>=0.5; '
              'select_related agent; top-N ordered by composite_score '
              'desc, dreamed_at desc',
    ),
    ('dream_tool', 'details'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: AgentDream.objects.get(id=dream_id) with '
              'select_related agent; requires: id (raises ValueError '
              'if missing or dream not found)',
    ),
    ('dream_tool', 'approve'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes AgentDream.decision_outcome="approved" + '
              'user_reaction="loved" + user_feedback via .save('
              'update_fields=[...]); FIRES post_save signal → '
              'promote_to_initiative() + execute_single_dream.delay() '
              '(async Celery dispatch); requires: id',
    ),
    ('dream_tool', 'dismiss'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes AgentDream.decision_outcome="rejected" + '
              'user_reaction="dismissed" + user_feedback via .save('
              'update_fields=[...]); no signal-driven Celery cascade '
              '(unlike approve); requires: id',
    ),
    ('dream_tool', 'create'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='creates AgentDream row via .objects.create; resolves PA '
              'as attributed agent via Agent.filter(name__icontains='
              '"personal assistant").first() with active-agent fallback; '
              'requires: title (non-empty after strip)',
    ),
    ('dream_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: AgentDream aggregate total + by_outcome + shown_count '
              '+ with_initiative + avg composite/creativity/actionability/'
              'relevance scores',
    ),
    ('governance_tool', 'inbox'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch via BOARDROOM_MAP[inbox] → '
              'boardroom_tool.stats (attention + decision counts + top '
              'items); no writes',
    ),
    ('governance_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: bundled aggregate — boardroom_tool.stats + '
              'human_decisions_tool.stats + FailureSignature count + '
              'AuditRemediationTask count; Session 1103c bundle to '
              'replace multi-step chains',
    ),
    ('governance_tool', 'attention_list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch via BOARDROOM_MAP → '
              'boardroom_tool.list_attention (pending attention items)',
    ),
    ('governance_tool', 'attention_detail'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: gateway dispatch via BOARDROOM_MAP → '
              'boardroom_tool.lookup (ID-based detail per Session 1097); '
              'requires: id',
    ),
    ('governance_tool', 'attention_lookup'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: gateway dispatch via BOARDROOM_MAP → '
              'boardroom_tool.lookup (title-query based find); requires: '
              'title_query',
    ),
    ('governance_tool', 'attention_approve'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → boardroom_tool.'
              'approve_attention; downstream may trigger further '
              'state transitions; requires: id',
    ),
    ('governance_tool', 'attention_ignore'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → boardroom_tool.'
              'ignore_attention; requires: id',
    ),
    ('governance_tool', 'decision_list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch via BOARDROOM_MAP → '
              'boardroom_tool.list_decisions (draft decision summaries)',
    ),
    ('governance_tool', 'decision_promote'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → boardroom_tool.'
              'promote_decision (draft → canonical); requires: id',
    ),
    ('governance_tool', 'decision_reject'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → boardroom_tool.'
              'reject_decision; requires: id + optional reason',
    ),
    ('governance_tool', 'decisions_list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch via DECISIONS_MAP → '
              'human_decisions_tool.list (pending human decisions; '
              'distinct from decision_list which surfaces boardroom '
              'draft decisions)',
    ),
    ('governance_tool', 'decisions_stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch via DECISIONS_MAP → '
              'human_decisions_tool.stats (decision statistics)',
    ),
    ('governance_tool', 'decision_create'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → human_decisions_tool.create '
              '(new decision request row); requires: title + summary',
    ),
    ('governance_tool', 'decision_decide'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → human_decisions_tool.decide '
              '(approve/reject/defer/watch on a decision); param '
              'translation id→item_id in wrapper; requires: id + decision',
    ),
    ('governance_tool', 'triage_batch'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch via BOARDROOM_MAP → '
              'boardroom_tool.get_triage_batch (batch of items for '
              'triage — read-only surface; batch_size default 5)',
    ),
    ('governance_tool', 'failure_signatures'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: FailureSignature ORM query direct read — top-N '
              'ordered by last_seen_at desc; Session 1100 read-only '
              'surface (no gateway dispatch); limit capped at 30',
    ),
    ('governance_tool', 'remediation_tasks'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: AuditRemediationTask ORM query direct read with '
              'select_related finding — top-N ordered by id desc; '
              'Session 1100 read-only surface; limit capped at 30',
    ),
    # ── S2914 batch 4: work_tool (gateway over initiative_tool + direct data actions) ──
    ('work_tool', 'initiative_list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch → initiative_tool.list (ORM read '
              'of Initiative queryset with status/owner/stage filters); '
              'Session 1078 thin dispatcher',
    ),
    ('work_tool', 'initiative_detail'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: gateway dispatch → initiative_tool.details (ORM '
              'read by id/human_id/seq_id/name); requires: id or name',
    ),
    ('work_tool', 'initiative_deliverables'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='deps: gateway dispatch → initiative_tool.'
              'initiative_deliverables (paginated reverse-projection read '
              'of Deliverable rows linked to a given initiative_id, '
              'Session 1194 Plan B §3.B.3); requires: initiative_id',
    ),
    ('work_tool', 'action_item_list'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: gateway dispatch → initiative_tool.action_items '
              '(ORM read of InitiativeActionItem with status/priority/'
              'initiative_id filters); param translation status→'
              'item_status in wrapper',
    ),
    ('work_tool', 'agent_conversations'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: AgentConversation ORM query direct read with '
              'select_related initiator + prefetch_related participants; '
              'Session 1100 read-only surface (not delegated); limit '
              'capped at 30',
    ),
    ('work_tool', 'workflows'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: AgentExecution ORM query direct read filtered by '
              'agent name in {WorkflowAgent, WorkflowOrchestrationAgent, '
              'CampaignOrchestratorAgent, AISeriesWorkflowAgent}; '
              'Session 1100 read-only surface; limit capped at 30',
    ),
    ('work_tool', 'stats'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Initiative + InitiativeActionItem + AgentExecution + '
              'AgentConversation ORM aggregate reads (Count by status); '
              'Session 1103c bundled overview to avoid multi-step chains',
    ),
    ('work_tool', 'initiative_create'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.create '
              '(new Initiative row); requires: name',
    ),
    ('work_tool', 'initiative_promote'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.promote '
              '(status transition TRIAGE/ON_HOLD → ACTIVE); '
              'requires: id',
    ),
    ('work_tool', 'initiative_update_status'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.'
              'update_status (status change; auto-cancels pending '
              'action items on COMPLETED/ARCHIVED); requires: id + status',
    ),
    ('work_tool', 'initiative_update'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.update '
              '(field patch — target_workspace_id/description/kind; '
              'idempotent no-op returns updated_fields=[]); Session '
              '1202 §A.1; requires: id',
    ),
    ('work_tool', 'initiative_link'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.link '
              '(bidirectional related_initiatives entry between '
              'parent_id and child_id; mirror direction auto-computed; '
              'idempotent); Session 1202 §A.1; requires: parent_id + '
              'child_id + relation',
    ),
    ('work_tool', 'action_item_start'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.'
              'start_action_item (status transition → in_progress); '
              'param translation id→item_id in wrapper; requires: id',
    ),
    ('work_tool', 'action_item_complete'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.'
              'complete_action_item (status transition → completed with '
              'optional notes); param translation id→item_id in wrapper; '
              'requires: id',
    ),
    ('work_tool', 'action_item_cleanup'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → initiative_tool.'
              'cleanup_action_items (finds/cancels junk items); dry_run '
              'default True per Session 1228 PR-A dual-gate (dry_run + '
              'confirm)',
    ),
    ('work_tool', 'bulk_cleanup'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='always',
        notes='writes via gateway dispatch → initiative_tool.'
              'bulk_cleanup (archives stalled/noise/duplicate '
              'initiatives); dry_run default True per Session 1228 PR-A '
              'dual-gate (dry_run + confirm)',
    ),
    # ── S2914 batch 4: intelligence_tool (unified desk gateway) ──
    # In-scope READ_ONLY subset (direct pure-ORM, no transitive network/LLM):
    ('intelligence_tool', 'stock_briefs'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: MarketIntelligenceBrief ORM query direct read '
              'ordered by -brief_date; Session 1100 read-only surface; '
              'limit capped at 50',
    ),
    ('intelligence_tool', 'ml_predictions'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: sports.MLPrediction ORM query direct read with '
              'select_related game + predicted_winner; Session 1100 '
              'read-only surface; limit capped at 30',
    ),
    ('intelligence_tool', 'signal_clusters'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: SignalCluster ORM query direct read with optional '
              'query/pattern_type/min_confidence/source_spider/'
              'window_hours filters; source_breakdown JSONField '
              'has_key/has_any_keys filter (S2869 Ledger #4); Session '
              '1100 read-only surface; limit capped at 30',
    ),
    ('intelligence_tool', 'sports_sharp_signals'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Deliverable ORM query direct read filtered by '
              "category='Sharp Action Detection' + created_at cutoff "
              '(hours default 48, Session 1228 PR-B autofill safety); '
              'Gap 4 read-only surface; limit capped at 30',
    ),
    ('intelligence_tool', 'congress_members'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: CongressMember ORM query direct read filtered by '
              'in_office=True + optional state/chamber/party/query; '
              'STATE_ABBREV resolution for full state names; Gap 6 '
              'read-only surface; limit capped at 50',
    ),
    ('intelligence_tool', 'legislation_tracked'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='deps: Bill ORM query direct read with optional status/'
              'chamber/query filters ordered by -updated_at; Gap 7 '
              'read-only surface; limit capped at 50',
    ),
    # Documented-out-of-scope: mutations + transitive-dependency composites/delegates.
    ('intelligence_tool', 'search'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='TRANSITIVE COST: source=web routes to _handle_web_search '
              '(network I/O, defined in td_handlers_agents.py:384); '
              'source=kb routes to _handle_rag_query.search (embedding '
              'lookup); source=spider routes to _handle_spider_data.'
              'search (may hit ingest paths). Rigby T0 SIGN classified '
              'as hidden-network like conversation_tool.search LLM-cost '
              'catch. Excluded from batch 4 READ_ONLY subset; requires: '
              'query',
    ),
    ('intelligence_tool', 'kb_ingest'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → rag_query_tool.ingest '
              '(KB write path); requires: url',
    ),
    ('intelligence_tool', 'sports_record_wager'): ToolActionMetadata(
        safety_class='MUTATION',
        applicability='conditional',
        notes='writes via gateway dispatch → sports_betting_tool.'
              'record_wager (new SportsWager row); requires: stake + '
              'odds + description + wager_type',
    ),
    ('intelligence_tool', 'overview'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='COMPOSITE with unverified transitive deps — calls '
              '_handle_stock_intelligence + _handle_sports_betting + '
              '_handle_legislation (each action=overview). Excluded '
              'from batch 4 in-scope subset per Rigby T0 SIGN "ban '
              'composite/overview actions that may transitively call '
              'network/LLM paths unless verified otherwise". Documented-'
              'not-tested; deferred to future targeted batch',
    ),
    ('intelligence_tool', 'briefs'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='COMPOSITE with unverified transitive deps — dispatches '
              'to stock_intelligence_tool.briefs / sports_betting_tool.'
              'brief / legislation_tool.trending by desk param. '
              'Excluded from batch 4 in-scope subset (same rationale '
              'as overview). Documented-not-tested',
    ),
    ('intelligence_tool', 'stocks_alerts'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to stock_intelligence_tool.alerts. Excluded from batch '
              '4 in-scope subset until stock_intelligence_tool is '
              'validated. Documented-not-tested',
    ),
    ('intelligence_tool', 'stocks_predictions'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to stock_intelligence_tool.predictions. Excluded from '
              'batch 4 in-scope subset. Documented-not-tested',
    ),
    ('intelligence_tool', 'stocks_sec_filings'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to stock_intelligence_tool.sec_filings. Excluded from '
              'batch 4 in-scope subset. Documented-not-tested',
    ),
    ('intelligence_tool', 'sports_predictions'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to sports_betting_tool.predictions. Excluded from batch '
              '4 in-scope subset. Documented-not-tested',
    ),
    ('intelligence_tool', 'sports_arbs'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to sports_betting_tool.arbs. Excluded from batch 4 '
              'in-scope subset. Documented-not-tested',
    ),
    ('intelligence_tool', 'sports_wagers'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='always',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to sports_betting_tool.wagers. Excluded from batch 4 '
              'in-scope subset. Documented-not-tested',
    ),
    ('intelligence_tool', 'legislation_search'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to legislation_tool.search. Excluded from batch 4 in-'
              'scope subset. Documented-not-tested; requires: query',
    ),
    ('intelligence_tool', 'legislation_summary'): ToolActionMetadata(
        safety_class='READ_ONLY',
        applicability='conditional',
        notes='DELEGATE with unverified transitive deps — dispatches '
              'to legislation_tool.summary. Excluded from batch 4 in-'
              'scope subset. Documented-not-tested; requires: '
              'bill_number',
    ),
}


# ── Lookup API ──────────────────────────────────────────────────────────────


ResolutionSource = Literal['action', 'tool_default', 'unclassified']


def get_metadata(tool_name: str, action: str) -> Optional[ToolActionMetadata]:
    """Return the per-action record, or ``None`` if unclassified."""
    return TOOL_ACTION_METADATA.get((tool_name, action))


def get_defaults(tool_name: str) -> Optional[ToolDefaults]:
    """Return the tool-level defaults, or ``None`` if none registered."""
    return TOOL_DEFAULTS.get(tool_name)


def resolve_safety(
    tool_name: str, action: str
) -> Tuple[Optional[SafetyClass], ResolutionSource]:
    """Resolve the effective safety class for ``(tool_name, action)``.

    Precedence:
    1. Per-action record in ``TOOL_ACTION_METADATA``  → ``'action'``.
    2. Tool-level default in ``TOOL_DEFAULTS``        → ``'tool_default'``.
    3. Neither present                                → ``(None, 'unclassified')``.

    Returning ``None`` for the safety class is the signal the harness uses to
    skip dispatch entirely (never dispatch-with-empty-payload). This is the
    Q4(a) behavior ratified in the S2902 SIGN cycle.
    """
    rec = TOOL_ACTION_METADATA.get((tool_name, action))
    if rec is not None:
        return rec.safety_class, 'action'
    tool_def = TOOL_DEFAULTS.get(tool_name)
    if tool_def is not None:
        return tool_def.default_safety_class, 'tool_default'
    return None, 'unclassified'


def resolve_bridge(tool_name: str, action: str) -> Optional[str]:
    """Return the external bridge name for ``(tool_name, action)`` or ``None``.

    Only per-action records carry the ``bridge`` field — ``TOOL_DEFAULTS`` does
    not, because bridge-dependency is action-specific (e.g., ``davinci_tool.grades``
    is internal while ``davinci_tool.health`` needs the resolve_node bridge).

    Used by ``pa_tool_validate_harness`` for the T2 bridge availability
    precheck (S2909 substrate cleanup arc).
    """
    rec = TOOL_ACTION_METADATA.get((tool_name, action))
    if rec is None:
        return None
    return rec.bridge


def coverage_stats() -> Dict[str, int]:
    """Return counts by resolution class — feeds the harness "top missing" report."""
    return {
        'per_action_records': len(TOOL_ACTION_METADATA),
        'tool_defaults': len(TOOL_DEFAULTS),
        'tools_with_at_least_one_record': len(
            {t for (t, _) in TOOL_ACTION_METADATA.keys()}
        ),
    }
