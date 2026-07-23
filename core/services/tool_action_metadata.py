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
