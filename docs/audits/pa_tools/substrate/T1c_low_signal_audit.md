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
1. Triage table populated for all Group A + Group B tools (14 + 44 = 58 entries).
2. Action Metadata Map location decision recorded with rationale.
3. Updated bucket counts fed to T1a as scoping input (specifically: how many tools remain in-class for the harness, informing T1a's MVP surface).

## 7. Triage table

_(populated at T1c execution session)_

| Tool | Current category | Bucket | Rationale |
|---|---|---|---|
| _TBD at T1c execution_ | | | |
