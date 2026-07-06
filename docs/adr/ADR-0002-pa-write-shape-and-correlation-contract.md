---
title: "ADR-0002 — PA write shape + PA↔LLMCallEvent correlation contract"
adr_id: ADR-0002
slug: pa-write-shape-and-correlation-contract
status: accepted
authority: design-decision
proposed: 2026-07-06
ratified: 2026-07-06
ratifier: chris
supersedes: (none)
superseded_by: (none)
intake_id: IB-1799-T1-02
arc_ref: I-0100
design_prep: docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md
source_refs:
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md §5 P4 + §8 F4/F5/F7 + §9.1 + §9.3
  - docs/research/domains/observability/1799_observability_canonical_summary.md §1 point 2 (Cat C PA-path AgentExecution coverage is zero) + §5 D74 + §8.2 T1 item 2
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md (this ADR's canonical design source)
  - docs/adr/ADR-0001-establish-adr-corpus.md §3.3 + §3.4 (frontmatter + body-section templates followed here)
  - core/models_unified_system.py:882 (AgentExecution — the target model)
  - core/models_llm_telemetry.py:30 (LLMCallEvent — the correlation partner)
  - core/services/unified_pa_entrypoint.py (PA agentic loop where writes will land)
reversibility: 4
  # See §6. Data migration to add canonical PA Agent row + feature-flag
  # off write are both trivially undoable. Backfill semantics reversible
  # by nulling flag + running truncate on the marker-tagged rows.
sign_cycle_1: SIGN-with-edits (Rigby; single-batch × 4-Q per IOS §7.2 v1.4 on arc pin pa-c5b235f7b15f45be; Q1 SIGN-with-edits/High + Q2 SIGN-with-edits/Med-High + Q3 SIGN-with-edits/High + Q4 SIGN-clean/Med-High; 8 folds F1-F8 applied inline; no BLOCKED; Cycle 2 NOT requested)
sign_cycle_1_pin: pa-c5b235f7b15f45be
companion_docs:
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md
  - docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md
  - docs/adr/ADR-0001-establish-adr-corpus.md
  - docs/research/domains/observability/1799_observability_canonical_summary.md
---

# ADR-0002 — PA write shape + PA↔LLMCallEvent correlation contract

## 1. Status

**Accepted** — Chris ratified 2026-07-06 via directive "ADR-0002 is ratified. Agree all F1–F8. Approve: Option 1 — per-turn core.AgentExecution writes. Sub-option 1(i) — canonical PersonalAssistant Agent row. Primary correlation contract: LLMCallEvent.execution_id == AgentExecution.id. Accept all Rigby folds without modification." Rigby SIGN Cycle 1 completed same day (SIGN-with-edits + 8 folds F1-F8 applied inline + no BLOCKED + no Cycle 2 requested).

## 2. Context

Arc I-0100 (Observability Correlation Spine + Mission Evidence Substrate) — the first production implementation arc under IOS — cannot advance past Stage 2 without ratifying the PA write shape and the correlation contract between the PA agentic loop and the LLM call telemetry table. Two upstream findings force the decision:

- **1799 xx99 §1 point 2 (Cat C):** "PA-path AgentExecution coverage is zero. PA agentic loop writes 0 AgentExecution rows unless the dispatched tool is a router-registered agent. Every PA turn un-instrumented." This is a broken observability invariant — LLM calls made during a PA turn cannot be correlated back to that turn because `LLMCallEvent.execution_id` is NULL for every such row.
- **Arc I-0100 scoping §8 F5 fold (Chris ratified 2026-07-06):** "ADR-B MUST specify PA↔LLMCallEvent correlation contract (keys + join path) WITHOUT implementing dedup." The contract is Yes-required in ADR-B; the shape of it is what this ADR chooses.

Arc I-0100 scoping doc §5 P4 sequences the runtime discharge of this ADR into a size-L PR gated on this ADR's ratification. F4 fold (Chris ratified) requires ADR-B ratifies FIRST — before ADR-A and optional ADR-C — so this ADR is the pin for Stage 2 exit-gate progress.

### 2.1 Design-preparation source

Per IOS §4.3 Stage 2 v1.4 design-prep equivalence rule: Arc I-0100 scoping doc §9.1 alone did NOT satisfy the design-prep equivalence criteria (consequences-per-option under-specified). A standalone design-preparation document was authored per Chris directive 2026-07-06 ("The Stage 1 scoping document should remain a Stage 1 artifact"). This ADR's canonical design source is:

**`docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md`**

The design-prep document contains the full 3-option × 5-field consequence matrix, pressure test, and recommendation. This ADR's §3 Decision, §4 Consequences, §5 Alternatives, and §6 Reversibility inherit from that analysis. Readers seeking the analytical work behind ratification should read the design-prep first.

## 3. Decision

Two coupled sub-decisions:

### 3.1 Sub-decision A — Write shape

**Adopt Option 1: per-turn `core.AgentExecution` write using the existing model.**

- One `core.AgentExecution` row is created per PA turn (user message → PA agentic loop → response).
- Row fields populated:
  - `agent` = FK to canonical `PersonalAssistant` Agent row (see §3.2).
  - `user` = current PA session's `UnifiedUser`.
  - `task` = initial user message text (truncated per existing TextField semantics).
  - `status` = standard lifecycle (`pending → in_progress → completed | failed | cancelled`).
  - `input_data['source']` = `'pa'` (discriminator marker; enables downstream filtering).
  - `input_data['intent']` = PA-classified intent (`agent_execution`, `deliverable_edit`, etc.).
  - `input_data['tool_selected']` = tool name chosen by PA, if applicable.
  - `input_data['trace_id']` = `pa_trace_id` (Session 1172 live-ticker join key).
  - `output_data['response']` = final composed PA response text.
  - `conversation_id` = `UnifiedPAEntrypoint.conversation_id` string form (`pa-<hex>`).
  - `owner_agent` = `'PersonalAssistant'` (Session 843 field; human-readable marker).
  - `parent_execution_id` = NULL for top-of-loop PA rows; set for nested-dispatch children.
  - Timestamps + tokens + cost per standard `AgentExecution` semantics.
- **Rejected alternatives (per design-prep §4 + §8):** Option 2 per-message span (backward-compat breakage); Option 3 dedicated `PAAgentExecution` model (correlation-semantics fragmentation); Option 4 per-session (violates F5 correlation granularity).

**Row-class discipline (SIGN Cycle 1 F2 fold).** Option 1 introduces a new *row-class* into `core.AgentExecution` — rows where `input_data['source'] == 'pa'` OR `agent__name == 'PersonalAssistant'`. Consumers of `AgentExecution.objects.filter()` that historically assumed "all rows represent a router-agent job" must recognize this new class and filter accordingly. Concrete guidance for consumers: filter by `input_data__source` for source-scoped queries (e.g., router-only: `.exclude(input_data__source='pa')`; PA-only: `.filter(input_data__source='pa')`), OR by `agent__name` when the meta-agent identity is the correct discriminator (e.g., `.exclude(agent__name='PersonalAssistant')`). See §4.2 Obligated for the dashboards / analytics implications of this row-class introduction.

### 3.2 Sub-decision B — PA Agent FK path

**Adopt Sub-option 1(i): data-migration path.** Create a canonical `Agent` row for PersonalAssistant via `RunPython` migration:

```python
def create_pa_agent(apps, schema_editor):
    Agent = apps.get_model('core', 'Agent')
    Agent.objects.get_or_create(
        name='PersonalAssistant',
        defaults={
            'category': 'meta',
            'description': 'Canonical PA / Rigby meta-agent row for AgentExecution FK (ADR-0002 Sub-option 1(i)).',
            # F3 fold: additional required Agent fields populated per model definition — see §3.2.1.
        },
    )
```

- Reverse migration deletes the row iff no `AgentExecution` rows reference it (safe pattern).
- All PA-authored `AgentExecution` rows FK to this single row.
- Preserves `AgentExecution.agent` non-null-FK invariant that current consumers rely on.

**Migration field-completeness discipline (SIGN Cycle 1 F3 fold).** The `RunPython` above is illustrative; the P4 migration MUST read the `Agent` model definition at migration-authoring time and populate every Yes-required field (not just `name` + `category` + `description`). Any Yes-required field left NULL will fail the migration on real DB write. Stage 3 pre-flight includes a step to enumerate the `Agent` model's required-field set and confirm the migration matches it.

**Uniqueness handling (SIGN Cycle 1 F4 fold).** If `Agent` uniqueness constraint is not solely `name` (e.g., includes a `slug`, `handle`, `tenant`, or `category` composite), the `get_or_create` call MUST use the correct lookup keys OR include `defaults` that satisfy every uniqueness constraint. Stage 3 pre-flight verifies the `Agent._meta.unique_together` + `UniqueConstraint` set and confirms the migration handles them. If uniqueness discipline is materially invasive (e.g., requires reserving fields on other rows), Sub-option 1(ii) becomes preferred — see F5 fold below.

- **Rejected alternative (SIGN Cycle 1 F5 fold — reaffirmed):** Sub-option 1(ii) schema relaxation (`AlterField(agent, null=True)`). Rejected because the non-null invariant is preserved by 1(i) at trivial cost; nullability introduces LOW-probability but non-zero consumer-drift risk. **Conditional preference reversal:** if Stage 3 pre-flight discovers Agent-model uniqueness or required-field constraints that make canonical row creation materially invasive (Rigby F4 fold explicit condition), reopen this sub-decision with Chris to switch to Sub-option 1(ii). Do NOT unilaterally switch — route via Rigby + Chris ratification per §7.2 v1.4.

### 3.3 Correlation contract — Keys + join path (F5 fold discharge)

Per F5 fold "ADR-B MUST specify PA↔LLMCallEvent correlation contract (keys + join path) WITHOUT implementing dedup":

- **Primary join key:** `LLMCallEvent.execution_id == AgentExecution.id` (both `UUIDField`). Cross-model FK-shape without DB FK constraint per LLMCallEvent design (survives AgentExecution deletion for postmortem — Session 1098 comment).
- **Secondary aggregation keys:**
  - `AgentExecution.conversation_id` (`CharField(64)`, indexed) — populates from PA session pin; enables cross-turn / cross-session aggregation.
  - `AgentExecution.input_data['trace_id']` — PA `pa_trace_id`; carried forward into `LLMCallEvent.metadata['pa_trace_id']` (JSONField; caller-supplied per LLMCallEvent design) for join independent of AgentExecution row existence.
- **Discriminator:** `AgentExecution.input_data['source'] = 'pa'` marks PA-authored rows. Enables filter without changing schema.
- **Join implementations (verification-method interface concrete queries per F7 — SIGN Cycle 1 F6 fold added query #4):**
  1. **PA turn → LLM calls:** `LLMCallEvent.objects.filter(execution_id=<agent_execution_id>)`.
  2. **LLM call → PA turn:** `AgentExecution.objects.filter(id=<llm_call.execution_id>)`.
  3. **PA session → all turns:** `AgentExecution.objects.filter(input_data__source='pa', conversation_id=<pin>).order_by('created_at')`.
  4. **PA turn → child AgentExecutions (nested-dispatch provenance chain):** `AgentExecution.objects.filter(parent_execution_id=<pa_execution_id>)`. Uses Session 1098 PR-4 `parent_execution_id` field. Traverses the "PA turn spawned this router-agent execution" ancestry. Critical for `deliverable_provenance_tool.trace` walking PA → downstream agent → deliverable.
- **Cross-model join warning (SIGN Cycle 1 F7 fold — CRITICAL for Stage 3 verification-method concrete queries):** `ToolCallRecord.conversation_id` is `UUIDField` while `AgentExecution.conversation_id` is `CharField(max_length=64)`. The PA passes `conversation_id` in string form (`pa-<hex>`), which fails UUID validation on the ToolCallRecord side. Stage 3 pre-flight concrete verification queries MUST NOT use `ToolCallRecord.conversation_id` joins for PA correlation until the schema-type mismatch is resolved (candidate follow-on ADR OR IDBT-0003 debt row). For PA turn ↔ tool call correlation in the interim, use `ToolCallRecord.trace_id` (post-P2 fix — `IB-1799-T1-01` ships trace_id write-side per F3 fold) with `AgentExecution.input_data['trace_id']` matching, NOT ToolCallRecord.conversation_id.
- **Explicitly out of scope for this ADR (per F5 "WITHOUT implementing dedup"):**
  - Identical-call collapse / dedup semantics.
  - Retry correlation semantics (LLMCallEvent.retry_count is per-call — no change).
  - Provider-specific tags in metadata.

### 3.4 Rollout posture

- **Feature flag:** `PA_AGENT_EXECUTION_WRITE_ENABLED` gates all new writes. Off by default at first ship (Arc I-0100 P4).
- **Sequence:**
  1. Data migration creates canonical PA Agent row (per §3.2).
  2. P4 PR ships write logic + flag definition + regression tests. Merges with flag OFF.
  3. Post-merge: Rigby-exercised smoke test verifies zero side-effects when flag OFF.
  4. Flag flip: Chris explicit directive (matches Arc I-0100 F8-iii staged-enable pattern for R3 delegation-handler dormancy — same discipline applies to any staged-enable flag).
  5. Post-flag-flip: Rigby-exercised verification per §3.3 join implementations.
- **Rollback:** Flag flip to OFF halts new writes; existing rows remain (queryable, no functional impact on router-agent path). Full removal reverses the data migration (delete PA Agent row iff no dependent rows) — safe reversal.
- **Backward compatibility:** No changes to router-agent `AgentExecution` write path. Filter by `input_data__source` for PA-specific queries.
- **Pre-flag-flip UI tolerance check (SIGN Cycle 1 F8 fold optional hardening):** Flag flip only after confirming (a) the canonical `PersonalAssistant` Agent row exists in all envs (local + prod) via `Agent.objects.filter(name='PersonalAssistant').exists()` check, AND (b) any agent-list UIs (admin, `all_agents` views, agent-selection dropdowns) tolerate the extra `'PersonalAssistant'` entry gracefully. Nuisance-level risk (not router-breakage), but worth an environments-completeness gate before flip.

## 4. Consequences

### 4.1 Enabled

- **Every PA turn becomes queryable telemetry.** `execution_history_tool.recent(user_id=X, source='pa')` returns the PA-turn history. `ops_tool.execution_summary` aggregates PA in agent breakdown.
- **`LLMCallEvent.execution_id` starts populating for PA calls.** Downstream dashboards using the (execution_id, -started_at) index (`llm_call_exec_time`) light up for PA traffic.
- **`deliverable_provenance_tool.trace` walks PA → downstream agent → deliverable chains** via existing `parent_execution_id` semantics. Session 1174 PR-1 agent-follow-up wake design becomes fully consumable.
- **Arc I-0100 P4 PR (IB-1799-T1-02) unblocks.** F4 fold ordering satisfied; ADR-B ratifies first; ADR-A (P3) proceeds; ADR-C (D74 spine posture) proceeds optionally with correlation contract as ratified input.
- **1799 xx99 §1 point 2 Cat C correlation gap closes for PA path.**

### 4.2 Obligated

- **Consumers filtering `AgentExecution.objects.all()`** must recognize `input_data['source'] == 'pa'` as a valid row-class. Recommended: add `.filter(input_data__source='pa')` for PA-specific views; leave `.all()` unchanged for cross-source aggregation.
- **Dashboards + analytics that treat `AgentExecution` as "agent jobs only" (SIGN Cycle 1 F1 fold Yes-required).** Any query, aggregation, or dashboard that historically assumed `AgentExecution` represents router-agent job executions (e.g., "agent job count over time," "top agents by execution volume," "agent success rate") MUST add `.exclude(input_data__source='pa')` (or the equivalent `.exclude(agent__name='PersonalAssistant')` per §3.1 row-class discipline). Otherwise PA turns will appear as anomalous "jobs" in agent job metrics, distorting rates and counts silently. Stage 3 pre-flight includes a bounded consumer sweep for `AgentExecution.objects.filter(...)` / `AgentExecution.objects.all()` call sites and confirms each is either (a) source-scoped correctly OR (b) intentionally cross-source. Sweep scope: `core/services/` + `core/agents/` + `core/tasks*.py` + `ops_tool` + dashboards views. Estimated ~25 call sites.
- **Rigby tool schemas** for `execution_history_tool.recent` should add optional `source` filter arg. Not blocking on this ADR; Stage 3 pre-flight scopes.
- **P4 regression tests** must cover the four verification queries in §3.3 explicitly.
- **P4 PR body cites this ADR** per IOS §5.2 rule 5 (`adr_ref: ADR-0002`).
- **Backfill NOT required.** Historical LLM calls remain `execution_id: NULL`; new writes populate. Backfill is a separate follow-on decision (out of ADR-B scope).

### 4.3 Non-goals

- **This ADR does NOT resolve D74 six-axis correlation-spine posture.** ADR-C (`ADR-0004` reserved slug) handles.
- **This ADR does NOT alter `ToolCallRecord.trace_id` write semantics.** SPEC_COMPLETE per F3 fold; ships in P2 unconditional of this ADR.
- **This ADR does NOT touch `MISSION_RUNNER_ENABLED` / `RIGBY_DELEGATION_ENABLED` posture.** ADR-A (`ADR-0003` reserved slug) handles.
- **This ADR does NOT decide PA-specific retention.** Preserved as future ADR option; the `input_data__source='pa'` filter enables differential retention if a later ADR wants it.
- **This ADR does NOT unify `intelligence.AgentExecution` with `core.AgentExecution`.** The intelligence model is action-plan-scoped and a distinct concern.

## 5. Alternatives considered

Full alternatives enumeration inherited from design-prep §4 + §8:

### 5.1 Option 2 — Per-message span (rejected)

Shape: one row per PA "message-level event" (user message received, intent classified, tool selected, tool executed, response composed). Adds `AgentExecution.span_type` discriminator + `span_sequence` field.

Reason for rejection: 3–5× write volume increase per turn; silent breakage of "count executions per user action" query semantic across ~25 estimated call sites; requires `granularity=` argument on `execution_history_tool.recent`. Per-message value achievable at lower cost by storing per-message events in `AgentExecution.input_data['events']` JSON blob (already permitted by schema; adopt as follow-on if operator need surfaces).

### 5.2 Option 3 — Dedicated `PAAgentExecution` model (rejected)

Shape: new model in `core/models_pa_execution.py` isolating PA telemetry. `LLMCallEvent` gains `pa_execution_id` field OR `execution_kind` discriminator.

Reason for rejection: fragments correlation semantics (existing "join LLMCallEvent to execution" queries need UNION or discriminator); duplicates 90%+ of `AgentExecution` schema; Rigby tool-surface complexity roughly 2×; violates F5 "clean join" intent even though it satisfies F5's letter.

### 5.3 Option 4 — Per-session AgentExecution (rejected)

Shape: one row per PA session (all turns collapsed). Rejected because it collapses per-turn correlation — impossible to associate LLMCallEvent with a specific turn within a session. Directly violates F5 correlation granularity requirement.

### 5.4 Sub-option 1(ii) — Schema relaxation to nullable Agent FK (rejected)

Shape: `AlterField(AgentExecution.agent, null=True, blank=True)`. PA-authored rows have `agent=NULL`; `owner_agent` CharField carries the string marker.

Reason for rejection: Sub-option 1(i) data migration preserves the non-null-FK invariant that current consumers rely on at trivial cost (~5 lines RunPython). LOW-probability but non-zero consumer-drift risk from nullability. If Chris/Rigby prefer 1(ii) (e.g., resist "PA is an Agent" framing), this ADR ratifies 1(ii) instead on Chris directive — both sub-options are functionally equivalent for the correlation-contract outcome.

## 6. Reversibility

**Rating: 4 (reversible with light effort).**

### 6.1 What "reverse" means

Reversing ADR-0002 means either (a) turning off `PA_AGENT_EXECUTION_WRITE_ENABLED` flag (halts new writes; existing rows remain), (b) removing the canonical PA Agent row + rolled-back migration (data-migration reverse; safe iff no dependent rows), (c) removing PA-authored `AgentExecution` rows (post-truncate via marker filter `input_data__source='pa'`).

### 6.2 Reversal effort

- **Flag flip (a):** trivial — Chris explicit directive; 1-line settings change.
- **Migration reversal (b):** data-migration reverse function deletes PA Agent row iff no CASCADE-dependent rows. If PA turns exist, they must be truncated FIRST (per (c)) before Agent row deletion. Order matters.
- **Row truncate (c):** `AgentExecution.objects.filter(input_data__source='pa').delete()` — bounded scope; safe if flag is OFF (no new writes competing).

### 6.3 What is NOT reversible

- **Downstream consumers that hardened on PA telemetry** (dashboards, tests, ops queries added post-flag-flip) may break if PA rows disappear. This is a general "downstream consumers of any observability output" concern, not ADR-B specific.
- **LLMCallEvent.execution_id populated during flag-ON period** points at deleted `AgentExecution.id` (safe per LLMCallEvent design — "execution_id survives AgentExecution row deletion"), but the join now returns empty. Operator-facing tools should handle "orphaned execution_id" gracefully — already the design intent per LLMCallEvent.execution_id docstring.

Rating 4 reflects the flag-flip primary reversal path (trivial). Full removal (b + c) is heavier but still bounded.

## 7. Provenance

### 7.1 Rigby SIGN record

**Cycle 1 completed 2026-07-06 on arc pin `pa-c5b235f7b15f45be` per IOS §7.2 v1.4.** Single-batch × 4-Q. Overall verdict: **SIGN-with-edits** (no BLOCKED; Cycle 2 NOT requested).

| Q | Sub-Q | Verdict | Confidence | Folds applied inline |
|---|-------|---------|-----------|----------------------|
| Q1 | Write shape (§3.1) — Option 1 discharges F5 without Option 2/3 costs? | SIGN-with-edits | High | **F1** — §4.2 obligated dashboards-add-exclude(source='pa') for agent-jobs-only queries. **F2** — §3.1 row-class introduction note. |
| Q2 | Agent FK sub-decision (§3.2) — 1(i) preserves invariants? | SIGN-with-edits | Med-High | **F3** — §3.2 migration must populate all required Agent fields. **F4** — §3.2 handle Agent uniqueness constraints. **F5** — 1(ii) rejection reaffirmed; conditional reversal only on Stage 3 discovery of materially invasive constraints. |
| Q3 | Correlation contract keys + join (§3.3) — 4 queries correct + Stage-3-usable? | SIGN-with-edits | High | **F6** — §3.3 add 4th query: PA turn → child AgentExecutions via `parent_execution_id`. **F7** — §3.3 CRITICAL warning: ToolCallRecord.conversation_id UUIDField vs AgentExecution.conversation_id CharField(64) mismatch; use `trace_id` not `conversation_id` for PA↔ToolCallRecord until schema resolved. |
| Q4 | Rollout + rollback (§3.4 + §6) — feature-flag + migration safe under blue/green? | SIGN-clean | Med-High | **F8** — §3.4 optional hardening: pre-flag-flip UI tolerance check (canonical Agent row exists all envs + agent-list UIs tolerate). |

Total: 8 folds F1–F8 applied inline. No structural changes to §3.1 write-shape decision or §3.2 sub-decision preference. All folds are additive-clarifying (concrete guidance, warning notes, discipline requirements) — none reverse a §3 Decision commitment.

### 7.2 Chris ratification

**Ratified 2026-07-06.** Chris "agree all F1-F8" wholesale ratification via terminal directive: "ADR-0002 is ratified. Agree all F1–F8. Approve: Option 1 — per-turn core.AgentExecution writes. Sub-option 1(i) — canonical PersonalAssistant Agent row. Primary correlation contract: LLMCallEvent.execution_id == AgentExecution.id. Accept all Rigby folds without modification." Matches S1399-forward wholesale-ratification pattern. `status` frontmatter flipped `proposed → accepted`. `ratified: 2026-07-06`, `ratifier: chris` populated.

### 7.3 Related PRs

- `#2941` (MERGED) First-queue seed — established BACKLOG.
- `#2945` (MERGED) Arc I-0100 Stage 1 arc-open bundle.
- `#2947` (MERGED) IOS v1.3 cascade discipline.
- `#2948` (MERGED) IB-Q1-BOOT-01 P0 prep — ADR corpus + ADR-0001.
- `#2949` (MERGED) IOS v1.4 fresh-session Stage 2 readiness — B1–B6.
- `#2950` (MERGED) Arc I-0100 Stage 2 opening ceremony.
- **This PR** — ADR-0002 authoring + design-prep. Ratification-pending.
- **Future:** P4 PR (IB-1799-T1-02) — gated on this ADR's ratification. Ships write logic + flag + regression tests + P4 rollout.

### 7.4 Related intake rows

- **`IB-1799-T1-02` (BACKLOG.md T1) — the discharge target.** This ADR ratifies the design; P4 PR ships the code. Row flips `IN_ARC → SHIPPED` at P4 merge with `adr_ref: ADR-0002` and `pr_refs: #<P4>`.
- **`IB-Q1-BOOT-01`** already SHIPPED via #2948 (ADR corpus prerequisite).
- **`IB-1799-T1-01`** (P2 trace_id fix) — ships unconditional of this ADR per F3.
- **`IB-1799-T1-03`** (P3 MISSION_RUNNER + RIGBY_DELEGATION) — gated on ADR-A (`ADR-0003` reserved slug), not this ADR.

### 7.5 Related debt rows

- **`IDBT-0002`** — RAG-owned embed-invalidation gap, delegated to Group 2100 RAG. Not affected by this ADR.
- **Potential IDBT-0003 candidate (surfaced during design-prep §1.2):** `ToolCallRecord.conversation_id` UUIDField vs `AgentExecution.conversation_id` CharField(64) type mismatch. PA passes string form — writes to ToolCallRecord.conversation_id would fail UUID validation. Pre-existing schema drift; noted for Stage 3 pre-flight follow-up decision (fold into ADR-B scope OR route to separate ADR OR debt row).

## 8. Follow-on ADRs blocked on this one

Per Arc I-0100 F4 fold ordering:

| ADR ID (reserved) | Slug | Content | Blocked-on shape |
|-------------------|------|---------|------------------|
| `ADR-0003` | `mission-runner-staged-enable-posture` | ADR-A — MISSION_RUNNER + RIGBY_DELEGATION staged unlock; not directly blocked on ADR-0002 correlation contract but ratifies AFTER per F4 |
| `ADR-0004` | `d74-six-axis-correlation-spine-posture` | ADR-C — D74 six-axis correlation-spine posture; consumes this ADR's correlation contract as INPUT for architecture-only decision per F1 |

---

**END ADR-0002-pa-write-shape-and-correlation-contract.md — proposed 2026-07-06.**
