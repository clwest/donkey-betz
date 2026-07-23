# Session 2914 — Slice 3 batch 4 (td_handlers_core allowlist sweep) + post-merge doc-fix

**Session:** S2914
**Date:** 2026-07-23
**Closed at HEAD:** `a3ade5b43` (post doc-fix)
**Wrapper pin at open:** `pa-5732c3f93cc044a4` (bumps to next-session pin at close via `session_lifecycle close`)
**Session cumulative:** 1 batch shipped × 2 tools = **2 tools closed** in Slice 3, plus 1 post-merge doc-fix PR

---

## READ THIS FIRST

S2914 shipped **Slice 3 batch 4** (2 tools: `work_tool` + `intelligence_tool`) using the **explicit READ-only allowlist + documented transitive exclusions** shape ratified at Rigby T0 SIGN. First sweep batch to codify allowlists by name rather than "read-only in spirit" framing — Rigby's Q3 zoom-out corrective for the "gateway ambiguity debt" she named as the coupling risk accreting at accelerated pace.

**Rigby T0 SIGN CRITICAL CATCH:** `intelligence_tool.search` reclassified READ_ONLY → MUTATION. `source='web'` transitively routes to `_handle_web_search` (`td_handlers_agents.py:384` — network I/O). Same class of issue as S2913 batch 2 `conversation_tool.search` LLM-cost catch. Second instance of the "hidden network/LLM cost in read-shaped gateway" pattern.

**Post-merge live verification surfaced a doc overstatement.** Rigby's live dispatch of `intelligence_tool.search source=web query='test'` via `pa_local.sh` at HEAD `3c8b00ffc` succeeded and hit network (~3052ms, DuckDuckGo scrape). The `TOOL_ACTION_METADATA` `MUTATION` classification gates the T1a harness but NOT the live PA runtime. Doc-fix PR shipped to soften the §5a language on both docs to accurately frame the classification as descriptive audit metadata, not a runtime gate.

## PRs shipped this session

- u-d-b PR [#3457](https://github.com/clwest/donkey-betz-platform/pull/3457) — Slice 3 batch 4 (2 tools: `work_tool` + `intelligence_tool`), merged at `3c8b00ffc`.
- u-d-b PR [#3458](https://github.com/clwest/donkey-betz-platform/pull/3458) — Batch 4 doc-fix (soften "harness prevents accidental exercise" → "descriptive audit metadata, not a runtime gate"), merged at `a3ade5b43`.
- u-d-b PR `<TBD>` — S2914 close cascade (handoff + 00-START refresh + wrapper pin bump).

## Batch shipped

### Batch 4 (PR #3457) — explicit READ-only allowlist + documented transitive exclusions

- **`work_tool`** — 16 actions classified (7 READ_ONLY in scope + 9 MUTATION gated).
  - **In scope:** `initiative_list`, `initiative_detail`, `initiative_deliverables`, `action_item_list`, `agent_conversations`, `workflows`, `stats`.
  - **Excluded (MUTATION):** `initiative_create`, `initiative_promote`, `initiative_update_status`, `initiative_update`, `initiative_link`, `action_item_start`, `action_item_complete`, `action_item_cleanup`, `bulk_cleanup`.
  - T1a harness: 5 success + 2 error_captured on required-arg-missing + 9 skipped_mutation.
- **`intelligence_tool`** — 19 actions classified (16 READ_ONLY dispatched via harness; 6 direct pure-ORM in scope this batch; 10 delegate/composite paths documented-but-not-verified per "not read-only in spirit"; 3 MUTATION gated).
  - **In scope (direct pure-ORM):** `stock_briefs`, `ml_predictions`, `signal_clusters`, `sports_sharp_signals`, `congress_members`, `legislation_tracked`.
  - **Documented-not-verified (delegate/composite):** `overview`, `briefs`, `stocks_*` trio, `sports_predictions/arbs/wagers`, `legislation_search/summary`.
  - **Excluded (MUTATION):** `search` (RECLASSIFIED — hidden network via `_handle_web_search`), `kb_ingest` (KB write), `sports_record_wager` (SportsWager write).

### Batch 4 doc-fix (PR #3458) — post-merge honesty correction

- `intelligence_tool_validation.md §5a` — softened; added S2914 post-merge live-dispatch evidence citation (3052ms DuckDuckGo scrape confirmed metadata classification is NOT a runtime gate).
- `work_tool_validation.md §5a` — parallel clarification; distinguished the Session 1228 PR-A dual-gate on `action_item_cleanup` + `bulk_cleanup` (which IS a runtime gate at the handler layer) from the descriptive classification (which isn't).
- Zero code/metadata/test changes.

## Sweep progress (post-S2914)

- **Slice 3 (`td_handlers_core`):** batch 4 × 2 tools = **14/22 shipped; 8 remaining.**
- Total corpus untested: 57 → **55** (-2).
- Gap map: **44 full + 10 partial + 55 untested**.
- Session cumulative pace: 2 tools / 1 batch / 1 session (mixed with post-merge verification cycle + doc-fix). Sustainable pace decoupled from S2913's triple-ship shape.
- **Rigby T0 SIGN Q2 AGREE:** close Slice 3 sweep at ~14/22 after batch 4; remaining 8 tools split by risk class into 3 specialty batches (network trio / async trio / row-create trio).

## Concern C — Slice 3 schema↔doc drift count reaches 5

Per Rigby T0 SIGN Q4 Concern C threshold: schema `description` field does not enumerate all discrete `action` enum values on 5 Slice 3 tools now:
1. `platform_awareness_tool` (S2913 batch 1)
2. `platform_config_tool` (S2913 batch 1)
3. `governance_tool` (S2913 batch 3)
4. `work_tool` (S2914 batch 4)
5. `intelligence_tool` (S2914 batch 4)

**5 instances >= the ≥5-core-tools threshold Rigby named at S2913 batch 1 T0 SIGN Q4.** Evaluated at Slice 3 CLOSE per Rigby's threshold + D6 moratorium (no substrate arc opens mid-slice). Candidate framings for Slice 3 CLOSE evaluation: (a) action-enum appendix in schema description auto-populated from enum values, (b) doc-only lint that fails if enum values are not mentioned in description, (c) accept the drift as intrinsic to gateway-shaped tools (description names action-families rather than each action).

## Rigby joint SIGN cycles (1 substantive T0 + 1 post-merge verify, zero rubber-stamp)

- **Batch 4 T0 SIGN:** AGREE-with-edits (8+ `repo_tool` probes, tool-grounded). Q1 (a)-with-scoping applied — work_tool + intelligence_tool with explicit allowlists; **CRITICAL CATCH** — intelligence_tool.search reclassified MUTATION (hidden network via cross-file `_handle_web_search`). Q2 AGREE — close Slice 3 at ~14/22 with 8 deferred to specialty batches. Q3 zoom-out — "gateway ambiguity debt" as pace-accreting coupling risk; batch 4 corrective = explicit allowlists (not "read-only in spirit").
- **Batch 4 post-merge verify:** live PA dispatch of 5 actions (4 in-scope READ + 1 excluded search). READ subset returned clean well-shaped envelopes. `search source=web` succeeded and hit network (3052ms) — surfaced doc-language overstatement. Rigby confirmed doc-fix framing before shipping PR #3458.

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- PR #3457 recycled clean at HEAD `3c8b00ffc`: 5 fresh workers, zero surviving old PIDs.
- PR #3458 doc-only — no recycle needed (no worker-behavior-affecting changes).

## Forward-carry observations (D6 moratorium in force)

- **Metadata-classification-vs-runtime-gate distinction** — S2914 batch 4 doc-fix corrected the framing. Watch for the same overstatement pattern in future batch validation docs. If it recurs, propose a doc-template guardrail or shared "how to describe classification" boilerplate for the sweep template at Slice 3 CLOSE.
- **"Hidden network/LLM in read-shaped gateway" pattern — 2nd instance** — first S2913 batch 2 (`conversation_tool.search` LLM); now S2914 batch 4 (`intelligence_tool.search` network). Forward-carry: if a 3rd instance surfaces in Slice 3 batch 5 / Slice 4 / Slice 5, evaluate for Fold promotion per PLAYBOOK-6.10 (still under D6 moratorium — no substrate arc opens without explicit Chris directive).
- **Concern C at 5 instances** — see §Concern C above.

## Twin-pointer docs card (S2914 batch 4 artifacts)

**Repo `/docs/` tree:**
- Batch 4 validation docs: `docs/research/tools/validation/work_tool_validation.md`, `docs/research/tools/validation/intelligence_tool_validation.md`
- Sweep gap map: `docs/audits/PA_TOOLS_GAP_MAP.md` (regenerated at close — 44 full / 10 partial / 55 untested)
- PA tool audit: `docs/PA_TOOL_AUDIT.md` (auto-generated by `build_pa_tool_audit`)
- Handoff: `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md` (this file)
- Metadata seed: `core/services/tool_action_metadata.py` (16 work_tool records + 19 intelligence_tool records)

**Workspace UI `/workspaces`:** twin-workspace mirror deferred to close cascade (per `feedback_rigby_writes_workspace_deliverables` — Rigby to write, not Claude ORM-direct).
