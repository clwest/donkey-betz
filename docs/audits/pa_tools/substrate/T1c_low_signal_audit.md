# T1c — Low-Signal Tool Audit

**Parent:** [S2900 substrate arc scoping](S2900_substrate_arc_scoping.md)
**Session estimate:** ~1 session (fast pass; may fit within a session that also opens T1a).
**Position:** FIRST thread executed (per Rigby SIGN B tweak — parent §3). Locks the in-class boundary before T1a is built.
**Blocks:** T1a auto-harness build (T1a's surface area depends on T1c's bucket decisions).

---

## 1. Goal

Fast triage pass over the tools that are NOT in the current sweep queue (`untested` category). Two overlapping groups:

**Group A — Explicit low-signal categories in `PA_TOOLS_GAP_MAP.md`:**
- `validated (doc, unknown coverage)` — 7 tools
- `validated (partial)` — 3 tools
- 4 doc/unknown/partial `td_handlers_ops` tools carried from 00-START: `agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool`.

**Group B — `agent (via run_agent)` category:**
- 44 tools that dispatch through the `run_agent` gateway rather than a direct handler.
- Explicit decision needed: do these fold into the PA tools sweep at all, or are they a distinct validation class governed by agent-level validation (different substrate)?

Plus one metadata-decision task (Rigby Fold Q2, arc parent §4 pointer).

## 2. Deliverable

A single triage table (in this doc, updated at T1c session) with these columns:

| Tool | Current category | Bucket | Rationale (≤1 line) |
|---|---|---|---|

**Bucket values:**
- `defer_indefinitely` — genuinely low signal for the sweep goal (e.g., external-service-only tool whose validation surface belongs elsewhere). Removed from harness surface.
- `promote_to_sweep` — belongs in the standard sweep queue; category upgrade or session slot needed.
- `close_with_short_note` — validated enough for current use; short authoritative note added to gap-map or per-tool doc.
- `out_of_class_agent` — Group B tools that dispatch through `run_agent`; governed by agent validation substrate, not PA tools sweep. Explicitly removed from harness surface.

## 3. Decision inputs

For each tool, T1c author checks:
- Schema location + handler path (from PA_TOOL_AUDIT).
- Any existing partial validation doc in `docs/research/tools/validation/`.
- Whether tool has external dependencies (Railway, external APIs, hardware, LLM providers) that would make harness-run impractical.
- Whether tool is user-facing OR internal-only (internal-only tools may be lower-priority for validation coverage).

Fast-pass posture: each tool gets ≤5 minutes of investigation. If a tool needs more, its bucket defaults to `defer_indefinitely` with a `revisit_trigger` note; sweep-time decides.

## 4. Action Metadata Map location decision (Rigby Fold Q2)

T1c also decides where per-action `applicability` metadata lives:

**Candidate A — In code, adjacent to `ToolDispatcher` (Rigby's lean; adopted at parent §4).**
- Pros: harness can programmatically reason about safety without doc-scraping.
- Pros: schema and metadata co-locate; drift is a code-review concern.
- Cons: metadata changes require code changes; higher friction than doc edits.

**Candidate B — Per-tool doc frontmatter.**
- Pros: metadata authoring is doc-authoring; low friction.
- Cons: harness must scrape frontmatter; drift is harder to catch.
- Cons: no metadata for tools without validation docs.

**T1c decision at session-execution time:** confirm Candidate A OR document Candidate B pivot with reasons. Default (per Rigby SIGN + parent adoption) is **Candidate A**.

If Candidate A confirmed: T1c also decides the exact file location (e.g., `core/services/tool_action_metadata.py` — one module registering a `TOOL_ACTION_METADATA` dict keyed by `(tool_name, action)`).

## 5. Anti-goals

- **Not** an exhaustive audit of the 14 low-signal tools. Fast-pass, ≤5 min each.
- **Not** a decision about the 25 `td_handlers_agents` tools already in the sweep queue (those stay in queue).
- **Not** a re-scoping of the Path B sweep methodology (S2892 ratification stands).

## 6. Close criteria

T1c closes when:
1. Triage table populated for all Group A + Group B tools (14 + 44 = 58 entries). **Executed count is 10 + 44 = 54 unique entries** — see §7 count reconciliation.
2. Action Metadata Map location decision recorded with rationale.
3. Updated bucket counts fed to T1a as scoping input (specifically: how many tools remain in-class for the harness, informing T1a's MVP surface).

## 7. Triage table

**Executed:** S2901 (2026-07-22).

### 7.0 Count reconciliation (author correction)

Parent §1 said "14 low-signal tools (7 doc-unknown + 3 partial + 4 doc-only ops)". Fast-pass identified: the 4 doc-only ops tools are **not a separate bucket** — they already reside in the doc-unknown / partial groups per `docs/audits/PA_TOOLS_GAP_MAP.md` (HEAD at triage: `7891ee9c`):

- `agent_introspection_tool` — `validated (doc, unknown coverage)` (line 151)
- `kb_tool` — `validated (doc, unknown coverage)` (line 218)
- `search_docs` — `validated (doc, unknown coverage)` (line 268)
- `ops_tool` — `validated (partial)` (line 239)

Whether the parent "14" was a double-count or a phrasing choice is not provable from the gap map itself (Rigby SIGN correction). Unique Group A membership from gap-map evidence = **10 tools** (7 doc-unknown + 3 partial). Group B unchanged = 44. Total triage rows = **54**.

### 7.1 Group A — 10 low-signal tools

| Tool | Current category | Bucket | Rationale |
|---|---|---|---|
| `agent_introspection_tool` | doc-unknown (ops) | `close_with_short_note` | S2728 validation report exists (`agent_introspection_run_agent_validation.md`); missing bare `## Covered actions` heading is the sole reason classifier flags it. Add heading. |
| `claude_code_tool` | doc-unknown | `close_with_short_note` | S2728 Batch A tool 4/5; VERIFIED status; single-action tool (task dispatch). Add heading. |
| `deliverable_tool` | doc-unknown | `close_with_short_note` | S2728 validation report; Rigby cross-check pending per prior campaign §10.1 step 12. Add heading. Rigby cross-check itself is separate work, not a T1c blocker. |
| `kb_tool` | doc-unknown (ops) | `close_with_short_note` | Combined doc `search_docs_kb_tool_validation.md`; 5-action gateway; needs per-tool `## Covered actions` split. |
| `repo_tool` | doc-unknown | `close_with_short_note` | S2728→S2729 Batch B tool 2/5; VERIFIED with 3 patches + 15 regression tests; 4 actions (`tree`/`read_file`/`search`/`git_info`). Add heading. |
| `search_docs` | doc-unknown (ops) | `close_with_short_note` | Combined doc with kb_tool; single-action tool. Add per-tool `## Covered actions`. |
| `session_tool` | doc-unknown | `close_with_short_note` | S2728 Batch A tool 2/5; VERIFIED + 7 new + 33 existing regression tests. Add heading. |
| `autopilot_tool` | partial (ops) | `close_with_short_note` | Already has full `## Covered actions` with 76 read-only actions exercised live at S2895; 29 mutations queued as Slice 1.5b per parent §5. Category upgrade to `validated_full` waits on Slice 1.5b, not on T1c. |
| `ops_tool` | partial (ops) | `promote_to_sweep` | Has `## Covered actions` heading but 18 of 20 declared actions carry `runtime-not-executed` marker (only `version` + `recent_recycles` verified live at S2796). Substantial coverage gap; needs a sweep slot as part of remaining ops slice work. |
| `workspace_tool` | partial | `promote_to_sweep` | Only nominally "partial" — `workspace_retrieval_validation.md` traces `WorkspaceManager` / `workspace_resolver` / `BaseAgent.execute_with_workspace` (substrate mechanics), NOT the `workspace_tool` PA schema+handler. False-positive `validated_partial` classification. Effectively untested; needs sweep slot. |

### 7.2 Group B — 44 `agent (via run_agent)` tools

**Bucket decision (single-line for all 44):** `out_of_class_agent`.

**Rationale:** `run_agent` is intercepted at `core/services/unified_pa_entrypoint.py:2236` BEFORE the dispatcher — the LLM invokes `run_agent(agent_name='X')`, which pops `agent_name` and re-dispatches under `actual_tool_name`. The 44 `agent_via_run_agent` tools have handlers registered in `tool_dispatcher._tool_handlers` but **no PA schema** — the LLM cannot invoke them directly. Their validation surface is agent-level (BaseAgent tests, agent-execution regression tests, agent registry provenance), not PA-tool-invariant sweep. Explicitly removed from PA tools sweep + harness surface.

**44 tools (out_of_class_agent):**

`ai_series_workflow_agent`, `audio_generation_agent`, `autonomous_content_studio_coordinator`, `bear_case_agent`, `blockchain_audit_coordinator`, `brand_identity_agent`, `campaign_orchestrator_agent`, `code_review_agent`, `content_audit_agent`, `content_diversity_orchestrator`, `contrarian_agent`, `coo_agent`, `creative_director_agent`, `cto_agent`, `editor_agent`, `game_predictor`, `image_generation_agent`, `line_movement_analyzer`, `market_intelligence_coordinator`, `meeting_coordinator_agent`, `memory_isolation_agent`, `opportunity_pipeline_agent`, `opportunity_scoring_agent`, `performance_analyst_agent`, `platform_audit_agent`, `podcast_coordinator_agent`, `prediction_market_analyst`, `research_agent`, `resolve_agent`, `security_agent`, `seo_optimizer_agent`, `sharp_action_detector`, `social_media_agent`, `stock_analyst_agent`, `stock_audit_coordinator`, `system_intelligence_agent`, `talking_character_agent`, `thinking_agent`, `topic_miner_agent`, `trained_creation_agent`, `trend_analysis_agent`, `video_generation_agent`, `voice_critic_agent`, `whale_watcher_agent`.

**Follow-on (not T1c-scope):** Agent-level validation substrate is a distinct future concern (a peer to the PA-tools sweep, not a child). Not opened here; not queued. Chris directive required before any agent-substrate validation arc is opened.

### 7.3 Bucket totals

| Bucket | Count |
|---|---|
| `close_with_short_note` | 8 |
| `promote_to_sweep` | 2 (`ops_tool` + `workspace_tool`) |
| `defer_indefinitely` | 0 |
| `out_of_class_agent` | 44 |
| **Total** | **54** |

## 8. Action Metadata Map location decision

**Decision: Candidate A confirmed** (per parent §4 default + Rigby SIGN lean).

**Exact location:** `core/services/tool_action_metadata.py` — one module registering a `TOOL_ACTION_METADATA` dict keyed by `(tool_name, action)` tuples, values are dataclasses declaring per-action metadata fields. Minimum viable field set for T1a MVP:

- `safety_class`: `Literal['READ_ONLY', 'WRITE_GATED', 'MUTATION', 'IRREVERSIBLE']`.
- `applicability`: `Literal['always', 'conditional', 'gated']` (parent Fold Q1 semantics).
- `notes`: free-form string for conditions / gating rules / revisit triggers.

**Rationale:**
- Harness (`pa_tool_validate_harness`) can programmatically reason about safety without doc-scraping; drift is a code-review concern (mypy + registration lint catch missing entries).
- Metadata and schema co-locate in `core/services/` — same working set for schema authors.
- Doc-scraping (Candidate B) was rejected because harness would need YAML frontmatter parsers, drift catches are harder, and tools without validation docs have no metadata.

**T1a input:** The harness reads `TOOL_ACTION_METADATA[(tool_name, action)]` for every dispatch; missing entries surface as `metadata_missing` classifier warnings (not blockers at MVP). Registration lint (bootable at T1a Phase 2) enforces one entry per `(tool_name, action)` pair for in-class tools.

## 9. T1a MVP surface — post-T1c inputs

- **In-class tools for harness:** 94 untested (existing sweep queue) + 2 `promote_to_sweep` from T1c (`ops_tool` + `workspace_tool`) = **96 in-class tools** for T1a harness surface.
- **Out-of-harness explicit:** 44 `out_of_class_agent` + 1 `run_agent` meta-tool = 45 tools NOT in harness surface.
- **Close_with_short_note tools (8):** remain in-class; harness re-verifies against existing validation reports. No T1a code change required for these.
- **Harness action-count target:** aggregate schema-declared actions across the 96 in-class tools. Preliminary ballpark from PA_TOOL_AUDIT — 300-450 actions total; refined at T1a Phase 1 scaffold.

## 10. Follow-on carry to T1a

- **Doc heading fix pass** (T1a-adjacent, doc-only): 8 tools need a `## Covered actions` heading added so the classifier re-categorizes them from `doc-unknown` / `partial` to `validated_full` (where the underlying reports already cover all schema actions). Can bundle into T1a Phase 0 scaffold PR or ship as a separate doc PR — Rigby's preference at T1a open.
- **`ops_tool` + `workspace_tool` sweep slots:** promote into standard sweep queue after T1a harness ships; both benefit from harness auto-execution of remaining actions.
- **Agent-substrate validation as peer arc:** flagged in §7.2 follow-on; not opened, not queued. Requires Chris directive.

## 11. Zoom-out folds (Rigby SIGN, T1c close)

Four zoom-out concerns surfaced by Rigby's "cold read before T1a opens" pass. Classified per PLAYBOOK zoom-out fold discipline.

### Fold A — Coupling risk on rewritten `run_agent` → `actual_tool_name` boundary
**Classification:** `future_trigger` — T1a Phase 1 scaffold requirement.
**Concern:** If telemetry / tool-call-logging records the rewritten `actual_tool_name` (e.g., `stock_analyst_agent`) rather than the invoked-by-LLM name (`run_agent`), the harness could double-count agent_via_run_agent tools as "invoked directly" and try to validate them as in-class. T1a must explicitly filter tool-call events by `original_tool_name == 'run_agent'` and exclude the rewrite from harness surface.
**T1a action:** Add exclusion filter at harness ingestion; add a T1a Phase 1 regression test verifying `run_agent`-rewritten calls do NOT enter the in-class validation queue.

### Fold B — `close_with_short_note` requires schema↔doc action-list diff check
**Classification:** `future_trigger` — T1a Phase 0 scope requirement.
**Concern:** T1c buckets 8 tools as `close_with_short_note` on the strength of "existing validation report + missing `## Covered actions` heading". But if the tool's schema has drifted since the validation report was written (new actions added, existing actions renamed), a heading-fix will misclassify them as `validated_full` while real coverage gaps persist. T1a Phase 0 doc-heading-fix pass must include an automated `schema.actions ⊆ doc.covered_actions` diff; mismatches auto-escalate the tool to `promote_to_sweep`.
**T1a action:** Add `pa_tool_validate_harness --check-doc-schema-parity` gate at Phase 0; block the heading-fix bundle if any of the 8 tools show drift.

### Fold C — Count-stability / gap-map snapshot pinning
**Classification:** `same_pr_mitigatable` — MITIGATED at this doc.
**Concern:** The "96 in-class (94 untested + 2 promoted)" framing is brittle if `PA_TOOLS_GAP_MAP.md` regenerates or edits mid-T1a-scaffold, causing coverage math to flap.
**Mitigation applied:** T1c §7.0 now pins the gap-map HEAD at triage time (`7891ee9c`). T1a scaffold references this pin as the coverage-math baseline; any T1a session that observes gap-map drift MUST recompute the 96-count against the current HEAD before proceeding.

### Fold D — `validated (full)` is a doc-status label, not runtime confidence
**Classification:** `future_trigger` — T1a harness anti-goal / gotcha entry.
**Concern:** Tools currently classified `validated (full)` on doc-status alone may still have low runtime evidence (analogous to the `ops_tool` case where the doc claims 20 actions but only 2 were live-verified). If T1a harness treats `validated (full)` as "no harness work required," it will miss real coverage gaps.
**T1a action:** T1a harness must verify EVERY in-class tool regardless of doc-status. Doc-status is a discovery signal ("which tools have prior evidence"), not a coverage gate ("which tools can skip harness"). Add this to T1a §2 anti-goals list at scaffold time.

### Fold status summary

| Fold | Classification | Landing |
|---|---|---|
| A — run_agent rewrite exclusion | `future_trigger` | T1a Phase 1 |
| B — schema↔doc parity check | `future_trigger` | T1a Phase 0 |
| C — gap-map snapshot pinning | `same_pr_mitigatable` | Mitigated at §7.0 pin |
| D — validated≠runtime-confidence | `future_trigger` | T1a §2 anti-goals |

None of Folds A/B/D require substrate-arc-scoped SIGN or expand T1c scope; they carry forward as T1a scope inputs. Fold C is closed inline.
