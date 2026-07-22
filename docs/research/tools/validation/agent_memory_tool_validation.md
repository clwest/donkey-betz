# `agent_memory_tool` — Validation Report (S2892)

**Tool:** `agent_memory_tool`
**Schema:** `core/services/pa_tool_schemas.py:5232`
**Handler:** `core/services/td_handlers_ops.py:7060` (`_handle_agent_memory`)
**Register site:** `core/services/tool_dispatcher.py:610`
**Session:** S2892 (Path B systematic sweep — Slice 1 batch 1 of `td_handlers_ops`)
**HEAD at validation:** `81502903d`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live).
**Rigby SIGN:** S2892 T1 SIGN AGREE-WITH-EDITS; Rigby surfaced the `list` schema-handler drift as a Ledger candidate.

---

## 1. Purpose / when-to-use

Browse agent memories and knowledge sources. Use when the user asks what agents remember, what knowledge sources feed a specific agent, or wants aggregate stats on the memory corpus. Read-only.

Distinct from `kb_tool` (which browses documents + embeddings) — `agent_memory_tool` is scoped to agent-specific memories written by learning bridges and knowledge-source rows attached to specific agents.

## Covered actions

- `list` — **in scope this ship** — verified live (see §6.1). **Behavior mismatch with schema:** the handler REQUIRES `agent_name` (dispatch fails with `invalid_params` when omitted), but the schema does not mark it as required. See §3, §5.
- `knowledge` — **in scope this ship** — verified live. Returns knowledge sources for a specified agent. `agent_name` required at handler.
- `stats` — **in scope this ship** — verified live. Returns global aggregates (total memories, top agents, memory type breakdown). No params required.

## 3. Schema notes

- **Required:** `action`.
- **`agent_name`** — schema declares string, optional at schema level. **Handler requires it for `list` AND `knowledge`** (raises `invalid_params: agent_name is required`). `stats` action ignores it. **Schema-handler drift** — see §5.
- **`query`** — string, optional. Applied as `icontains` filter over memory text on `list` action.
- **`limit`** — integer, default 20.
- **Schema description lint (per S2795 F5):** description does not mention which actions require `agent_name`, so the model has no signal it must supply it for `list`.

## 4. Golden-path examples

**Global memory stats (no agent filter needed):**

```
agent_memory_tool  action=stats
```

**Knowledge sources for a specific agent:**

```
agent_memory_tool  action=knowledge  agent_name=ResearchAgent
```

**Recent memories for a specific agent, filtered by query:**

```
agent_memory_tool  action=list  agent_name=ResearchAgent  query="market signal"
```

## 5. Failure / empty-state / pagination notes

- **`list` without `agent_name` → invalid_params error.** Schema does not surface this requirement. Ledger candidate: (a) mark `agent_name` required in schema for `list`+`knowledge`, or (b) relax handler to allow global list with pagination when omitted. Verified live at S2892 T1 (see §6.1 dispatch #1).
- **`knowledge` without `agent_name`** — same failure mode; not exercised live but expected symmetric.
- **Empty state:** when `agent_name` matches an agent with no memories, `list` returns `total_memories: 0, count: 0, memories: []`. Fail-soft.
- **Pagination:** `limit` supported; no explicit `offset`. Handler applies `limit` after filter.

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2892 T1 (2026-07-22, HEAD `81502903d`, pin `pa-373cf02ba2344b13`):

**`list` (default params, no `agent_name`) — FAILED as expected:**

```
error: invalid_params
message: agent_name is required
```

**`list` with `agent_name=ValidationCheckAgent`:**

```json
{"action": "list", "agent_name": "ValidationCheckAgent",
 "total_memories": 0, "count": 0, "memories": []}
```

Confirms empty-state fail-soft for an agent with no memories yet.

**`knowledge` for `ValidationCheckAgent`:** returned 9 knowledge sources. Populated envelope confirmed.

**`stats` (no params) — populated response:**

```json
{"memory_by_type": {"interaction": 56, "conceptual": 2, "success": 535,
                    "failure": 13, "insight": 56, "partial_failure": 7,
                    "feedback": 58, "technique": 56},
 "top_agents": [
   {"agent": "ResearchAgent", "count": 170},
   {"agent": "TrendAnalysisAgent", "count": 96},
   {"agent": "COOAgent", "count": 94},
   {"agent": "EditorAgent", "count": 82},
   {"agent": "SystemIntelligenceAgent", "count": 41},
   {"agent": "ContentWriterAgent", "count": 34},
   {"agent": "CTOAgent", "count": 29},
   {"agent": "ContentStrategyAgent", "count": 23},
   {"agent": "CustomerResearchAgent", "count": 21},
   {"agent": "CompetitorAnalysisAgent", "count": 18}
 ]}
```

Total memory across 8 types = 783. Top-10 agents cover most of the corpus.

### 6.2 Runtime-not-executed — this ship

- **`list` with `query` filter** — not exercised beyond default. Handler filter semantics (icontains vs full-text) unverified at runtime.
- **`limit > 20` behavior** — not exercised.
- **`knowledge` without `agent_name`** — not exercised (assumed symmetric to `list` fail mode).

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`.
- **Ledger candidate from this ship:** `agent_memory_tool.list` (and `.knowledge`) requires `agent_name` at handler but schema doesn't declare it. Options: (a) mark required in schema so model reliably supplies it, or (b) relax handler to allow global list with pagination.
- **Related tools:** `kb_tool` (document/embedding browsing — no agent-scoping), `agent_introspection_tool` (registry + capability inventory).
