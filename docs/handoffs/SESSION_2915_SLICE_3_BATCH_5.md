# Session 2915 — Slice 3 batch 5 (row-create trio + §5b first-hop dependency proof)

**Session:** S2915
**Date:** 2026-07-23
**Closed at HEAD:** `0ced0a1b3` (post batch 5 merge)
**Wrapper pin at open:** `pa-a0d7e6e1327a4405` (bumps to next-session pin at close via `session_lifecycle close`)
**Session cumulative:** 1 batch shipped × 3 tools = **3 tools closed** in Slice 3; formal Slice 3 CLOSE at 14/22 core surface

---

## READ THIS FIRST

S2915 shipped **Slice 3 batch 5** (3 tools: `task_breakdown_tool` + `research_and_create_tool` + `competitor_comparison_tool`) — the **row-create trio** — closing Slice 3 at 14/22 core surface per Rigby S2915 T0 SIGN Q1 AGREE. First batch to introduce the **§5b "first-hop dependency proof"** shape per Rigby T0 SIGN Q4 verdict: every action lists direct callees + classification (read / network / llm / db_write / db_delete / dispatch / opaque) + no-hidden-cost verdict. Closes the S2914 gap — explicit action allowlist doesn't prove those actions have no transitive network/LLM/write cost via delegated helpers.

**Rigby T0 SIGN cycle (14+ tool-grounded probes across 4 turns, zero rubber-stamp).** Q1 AGREE close Slice 3 at 14/22 → 3 specialty batches for the remaining 8. Q2 AGREE-with-edits Concern C framing (a) generator-side auto-append action-enum appendix (with carve-out for gateway/meta tools). Q3 AGREE row-create trio as batch 5 (biggest concentrated systematic risk in remaining 8). Q4 AGREE-with-edits scoped transitive-dependency-proof requirement (first-hop proof + no-hidden-cost verdict, NOT "read every leaf helper").

**Post-merge live verify clean.** Rigby dispatched `task_breakdown_tool.summary` (25ms, 168 tasks aggregated) + `competitor_comparison_tool.list` (4ms, empty list). `research_and_create_tool` correctly BLOCKED — Rigby verified `TOOL_DEFAULTS['research_and_create_tool'] = MUTATION` in code without dispatching (no OpenAI call, no Deliverable created). Zero critical flags — no S2914-style hidden network/LLM/write catches.

## PRs shipped this session

- u-d-b PR [#3460](https://github.com/clwest/donkey-betz-platform/pull/3460) — Slice 3 batch 5 (row-create trio + §5b shape), merged at `0ced0a1b3`.
- u-d-b PR `<TBD>` — S2915 close cascade (handoff + 00-START refresh + wrapper pin bump).

## Batch shipped

### Batch 5 (PR #3460) — row-create trio + first-hop dependency proof (§5b)

- **`task_breakdown_tool`** — 2 actions, both READ_ONLY in scope. Low-risk anchor.
  - **In scope:** `summary`, `drilldown`.
  - T1a harness: 1 success + 1 soft_error (drilldown missing `task_name`).
  - §5b: all first-hop deps are pure ORM reads on `CeleryTaskEvent` + `AgentExecution`. Clean.

- **`research_and_create_tool`** — actionless. Second actionless-MUTATION `TOOL_DEFAULTS` entry (after S2910 `legal_doc_drafter_agent`).
  - **Classification:** MUTATION via `TOOL_DEFAULTS`. Three-hop chain: `WebSearchTool.execute` (network) → `LLMProviderRegistry.complete` (openai `gpt-4.1-mini`, max_tokens=4000) → `create_deliverable` (Deliverable row via factory).
  - §5b: 3 opaques with revisit triggers recorded — all three implementations pending their own audits.
  - T1a harness: `actions: []`, `schema_action_count: 0`. Classification is registry/audit signal (no per-action dispatch to skip).

- **`competitor_comparison_tool`** — 8 actions, widest-surface mixed-safety tool in batch 5.
  - **In scope (READ_ONLY):** `list`, `status`, `detail`.
  - **Excluded (MUTATION):** `generate`, `regenerate`, `create_initiative_from_gap`, `export_markdown`.
  - **Excluded (IRREVERSIBLE):** `delete` — second IRREVERSIBLE-classified action after S2908 `media_tool.delete` Ledger candidate.
  - T1a harness: 3 READ_ONLY dispatched (1 success + 2 soft_error) + 5 mutation-class skipped_mutation.
  - §5b: `delete` firm at handler layer but **opaque at cascade layer** (FK cascade behavior in `models_competitor_comparison.py` not read this batch; referenced `Initiative` rows may become orphaned).
  - **Doc format workaround:** action list flattened to bulleted form with inline class prefix (was `### READ_ONLY subset` subsections) because `NEXT_HEADING_RE = re.compile(r'\n#+\s+')` at `pa_tools_gap_map.py:107` matches `###` and truncates the action-name harvest. Preexisting in S2914 `intelligence_tool_validation.md` — 2nd instance. Parser fix deferred per D6 moratorium.

## Sweep progress (post-S2915)

- **Slice 3 (`td_handlers_core`):** batch 5 × 3 tools = **17/22 shipped; 5 remaining.**
- **Slice 3 FORMALLY CLOSED at 14/22 core surface** per Rigby T0 SIGN Q1 AGREE; remaining 5 route to specialty batches 6+7 (network trio + async duo).
- Total gap map: **41 full + 10 partial + 55 untested** (batch 5 flips 3 untested → 1 full + 2 partial: `task_breakdown_tool` = full; `research_and_create_tool` + `competitor_comparison_tool` = partial because §5b marks opaque callees).
- Session cumulative pace: 3 tools / 1 batch / 1 session (with in-depth T0 SIGN + post-merge verify). Sustained decoupled pace vs. S2913's triple-ship shape.
- **Remaining 5 tools split by shape family:**
  - Network trio (batch 6): `fleet_health` + `http_smoke_test` + `signal_studio_judge_stats` — network-preflight test pattern.
  - Async duo (batch 7): `studio_tool` (Celery apply_async + AsyncResult reads) + `workflow_run_tool` (WorkflowRun row create + apply_async + revoke).

## §5b first-hop dependency proof — new shape this batch

Per Rigby T0 SIGN Q4 verdict, every covered action now enumerates:

- **Direct callees** (helpers/classes/tasks the handler calls).
- **Classification per callee:** `read` / `network` / `llm` / `db_write` / `db_delete` / `dispatch` / `opaque`.
- **No-hidden-cost verdict per action:** (a) callee read + classification confirmed, OR (b) marked opaque + trust downgraded + revisit trigger recorded.

Scoped to **first-hop only** — NOT "read every leaf helper" (would slow pace unhelpfully). Closes the exact S2914 failure mode: explicit action allowlist doesn't prove those actions have no hidden network/LLM/write cost via delegated helpers. First substantial use of the "opaque callee trust-downgrade" escape valve: 3 opaques in `research_and_create_tool`, 4 opaques in `competitor_comparison_tool`. Watch discipline across batches 6-7 for opaque-forever creep.

## Rigby joint SIGN cycles (1 substantive T0 + 1 post-merge verify, zero rubber-stamp)

- **Batch 5 T0 SIGN:** 4-turn cycle. Turn 1: Rigby returned preliminary search hits + explicitly refused to verdict without body reads. Turn 2: located all 8 handler entry points; still refused to verdict. Turn 3: read handler bodies (10 successful `read_file` probes covering all 8 handlers + `pa_tool_schemas.py` entries); text response briefly self-contradicted ("I don't have tool access") but tool_runs showed real evidence. Turn 4: Q1+Q2 verdicts with file+line citations; Q3+Q4 followed after truncation nudge. Total: 14+ tool-grounded probes. AGREE / AGREE-with-edits / AGREE / AGREE-with-edits across the four questions.
- **Batch 5 post-merge verify:** 2 live READ_ONLY dispatches (task_breakdown.summary + competitor_comparison.list) — both clean, expected shape. 1 code-verified BLOCKED check on research_and_create_tool without dispatch. Zero flags.

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- PR #3460 recycled clean at HEAD `0ced0a1b3`: 5 fresh workers, zero surviving old PIDs. Recycle event recorded to `logs/recycle_events.jsonl`.

## Forward-carry observations (D6 moratorium in force)

- **Second actionless-MUTATION `TOOL_DEFAULTS` entry** — `research_and_create_tool` after S2910 `legal_doc_drafter_agent`. If a 3rd instance surfaces, evaluate a shared "actionless side-effecting chain" pattern name (multi-hop network+LLM+write exposed as one dispatch).
- **Opaque callee trust-downgrade pattern — first substantial use.** 7 total opaques recorded across batch 5's two write-path tools. Forward-carry: watch whether "opaque, revisit trigger recorded" discipline holds across batches 6+7 (network + async trios) or if opaque-forever creep sets in.
- **Model-file cascade audit gap** — `competitor_comparison_tool.delete` firm at handler layer, opaque at cascade layer. Reveals a systematic gap: handler validation doesn't cover model-file FK cascade rules. Forward-carry: propose a "cascade audit" companion doc pattern for tools with `db_delete` actions at next Slice close or if the pattern hits a 2nd instance.
- **§Covered-actions `###` subsection breaks parity extraction — 2nd instance** (including S2914 `intelligence_tool_validation.md`). Batch 5 workaround = flatten to bulleted list with inline class prefix. Parser fix (`NEXT_HEADING_RE` → `##`-only) deferred per D6 moratorium; propose at Slice 3 CLOSE or 3rd instance.
- **Second IRREVERSIBLE-classified action** — `competitor_comparison_tool.delete` after S2908 `media_tool.delete` Ledger candidate. 3rd instance would trigger "IRREVERSIBLE actions require dry_run flag" harness-side lint Fold candidate per PLAYBOOK-6.10.

## Concern C — Slice 3 schema↔doc drift observation (no substrate arc opens)

Per S2914 handoff, 5 Slice 3 tools flag `actions_not_mentioned_in_description`. Batch 5 did not add new instances (task_breakdown / competitor_comparison / research_and_create all have adequate schema descriptions or actionless). **Rigby T0 SIGN Q2 recommendation:** framing (a) — generator-side auto-append action-enum appendix — with carve-out for gateway/meta tools whose actions are stable families. Deferred per D6 moratorium; evaluate at some future post-moratorium session.

## Twin-pointer docs card (S2915 batch 5 artifacts)

**Repo `/docs/` tree:**
- Batch 5 validation docs: `docs/research/tools/validation/task_breakdown_tool_validation.md`, `docs/research/tools/validation/research_and_create_tool_validation.md`, `docs/research/tools/validation/competitor_comparison_tool_validation.md`
- Sweep gap map: `docs/audits/PA_TOOLS_GAP_MAP.md` (regenerated at close — 41 full / 10 partial / 55 untested)
- PA tool audit: `docs/PA_TOOL_AUDIT.md` (auto-generated by `build_pa_tool_audit` — 161 tool names · 117 schemas · 160 handlers · 116 wired)
- Handoff: `docs/handoffs/SESSION_2915_SLICE_3_BATCH_5.md` (this file)
- Metadata seed: `core/services/tool_action_metadata.py` (1 TOOL_DEFAULTS entry + 10 per-action records)
- Harness artifacts: `docs/audits/pa_tools/harness_output/{task_breakdown_tool,research_and_create_tool,competitor_comparison_tool}.json`

**Workspace UI `/workspaces`:** twin-workspace mirror deferred to close cascade (per `feedback_rigby_writes_workspace_deliverables` — Rigby to write, not Claude ORM-direct).
