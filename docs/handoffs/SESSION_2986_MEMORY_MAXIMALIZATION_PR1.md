# SESSION 2986 — Memory Maximalization PR1 (remember_tool fix + operator doc + PA header rename)

**Date:** 2026-07-26 evening (US/Denver)
**Merge:** `857633411` — PR #3631
**Spec deliverable:** `ba968ac1-95b4-4e14-82be-3cb02598edac` (Donkey Betz workspace `b4503364-…`)
**Session shape:** PLAYBOOK-7.7.1 spec→ship, all 9 phases walked (PR1 of 2)
**Rigby cycles:** 4 SIGN passes (T1 × 3 + A2 PROCEED-TO-MERGE)

---

## Three-part summary

**What was done (plain English):**
`remember_tool.save` now reliably persists memories and tells you what it did — the return payload includes `status` (`created` or `duplicate_updated`), `truncated`, and `original_len`, so you can see when dedupe kicked in or content was clamped to 500 chars. Cap-hit uses the modern error shape. A pre-parse gate rejects oversized `remember_tool.save` calls before they fail on JSON truncation (the exact failure mode you hit before this session). PA's memory prompt header is renamed to reduce the "you asked me to remember X" parroting. Operator doc at `docs/topics/memory-system.md` explains the three memory layers. PR #3631, sha `857633411`.

**How it improves the platform (before / after):**
- **Before:** `remember_tool.save` returned an inconsistent envelope on cap-hit (legacy `{'error':...}` shape only backfilled with `error_code='legacy_error'` by the dispatcher). Long content silently truncated with no signal. Dedupe returned a status field but success didn't. Long content caused JSON parse failures with a generic retry hint. PA header text nudged the model to over-quote memory back to the user.
- **After:** Every save-return path carries `status`/`truncated`/`original_len` fields. Cap-hit uses the S2879 canonical shape (`error_code='cap_hit'`). Oversized args (>3000 raw chars) are rejected at the entrypoint with a targeted "summarize to under 500 chars" hint before `json.loads` risks mid-stream truncation. Header renamed to neutral "PERSISTENT USER CONTEXT (use only if relevant; do not mention unless asked)". Ten new happy-path tests fill the S2886 coverage gap. Operator doc names the three memory layers, contracts, and PR2 scope.

**Next-session first action:**
PR2 for spec `ba968ac1` — memory utilization trace with layer discriminator (`user_memory_context` / `user_agent_learning` / `conversation_memory`), `memory_hygiene_audit` management command, `UserMemoryContext.is_active` + `superseded_by` + `superseded_at` migration for supersede-not-delete semantics, and narrow non-PA preflight wired into `ProjectBuilderOrchestrator` only (Rigby's LLM-bypass sweep found 14+ candidates; broader sweep is a follow-up spec, not PR2).

---

## Session timeline

Playbook-7.7.1 nine-phase walk:

| Phase | What happened |
|---|---|
| **1 — Spec ingestion** | Fetched deliverable `ba968ac1` via Rigby (`deliverable_tool.detail` full body). 5 deliverables (D1 fix, D2 preflight, D3 trace, D4 hygiene, D5 doc). |
| **2 — Pre-code sampling** | Read handler at `td_handlers_core.py:2210-2364`, `UserMemoryContext` model at `conversations/models.py:253`, PA memory injection at `unified_pa_entrypoint.py:2940-2958`, tool-args JSON parse at `unified_pa_entrypoint.py:2185`. Identified 9 concrete gaps. |
| **3 — T1 SIGN pass 1** | Routed to Rigby with 9 findings. Verdict: **REVISE** with 10 tool_runs, verified all findings + surfaced 3 substantive additions (F-D1a truncation signaling, F-D1b agent-side prevention not just handler, F-D3a layer discriminator). |
| **3 — T1 SIGN pass 2** | Folded 7 same-PR mitigations. Verdict: **REVISE** with 8 tool_runs, corrected F-D1b implementation (can't inspect `arguments['content']` before parse — must gate on raw-string length). Located D2 shift-brief as no-op (deterministic, no LLM). |
| **3 — T1 SIGN pass 3** | Fixed F-D1b to raw-string gate + narrowed D2 to LLM-driven flows only. Rigby did LLM-bypass site sweep: 14 `enforce_real_ai(` sites + 9 `client.responses.create(` + 80 `client.chat.completions.create(` non-PA callsites. Verdict: **PROCEED** with note that Phase 5 Chris decision MUST fire (MVP-vs-sweep for D2 in PR2). |
| **4 — Fold** | 7 same-PR mitigations folded (F-D1a/b/c/d/e + F-D5a + F-Z1). 3 future_triggers logged (F-ZO2 relevance filter, F-ZO3 structured citations, F-D2-broad non-PA sweep). |
| **5 — Chris framing** | Presented 1 decision: split into 2 PRs (PR1 today: fix + doc + header; PR2 next: trace + hygiene + preflight) or bundle into one. Chris ratified split. |
| **6 — Implement** | Handler save-branch refactor (35+/11- in `td_handlers_core.py`), pre-parse gate + envelope helper + constants + header rename (98+/2- in `unified_pa_entrypoint.py`), 10 tests (`test_s2986_remember_tool.py`, +278), operator doc (`memory-system.md`, +126). |
| **7 — A2 SIGN** | Routed to Rigby with test result (10/10 pass, S2886 regression check 17/17). Verdict: **PROCEED-TO-MERGE** with 8 tool_runs verifying all 7 shipped items at exact line ranges. Zoom-out low-risk both prompts. |
| **8 — Ship** | Committed as `c13df38f6`, pushed, PR #3631 opened, merged via `gh pr merge --admin --squash --delete-branch` at sha `857633411`. |
| **9 — Recycle + close** | `make recycle-all` clean at `sha=85763341193d`. Live-dispatch smoke: cap_hit envelope live-verified in new S2879 shape. Cap divergence surfaced (see §Post-merge findings). This handoff + 00-START refresh + session_lifecycle close. |

---

## Rigby cycle discipline

**T1 pass 1** — 10 tool_runs. Rigby's zoom-out surfaced ZO1 (header parroting risk) and ZO2/ZO3 (relevance-threshold + citation-strength — deferred as future_trigger). REVISE verdict was substantive, not rubber-stamp; my pre-code sampling missed the agent-side prevention path (fixing the handler doesn't stop the mid-stream args truncation at the root).

**T1 pass 2** — 8 tool_runs. Critical technical catch: my proposed F-D1b of "inspect `arguments['content']` and reject if > 1500 chars" is impossible before `json.loads` runs. Rigby's D2 investigation found `rigby_shift_brief_tool` is deterministic (no LLM) — so memory preflight is a no-op there. Spec's D2 assumptions ("shift brief needs preflight") were partly wrong. Real preflight universe is LLM-driven bypass sites only.

**T1 pass 3** — 8 tool_runs. LLM-bypass sweep confirmed the universe is dozens of files. Rigby recommended PR2 MVP = `ProjectBuilderOrchestrator` only + Rigby Tool Gap Ledger entry + follow-up audit spec for broader sweep.

**A2 SIGN** — 8 tool_runs at exact line ranges (2210-2350, 2350-2470, 120-280, 2168-2263, 2263-2383, 3028-3083, 1-81, 1-126). All 7 shipped items CONFIRMED. Non-blocking future-tweak offered (add "If the user asks what you remember, you may quote/summarize" to header) — not shipped, logged for observation.

**Zoom-out per PLAYBOOK-6.10.7:**
- **ZO1 (T1 pass 1):** Header parroting risk → folded as F-Z1, shipped.
- **ZO2:** Relevance-threshold pre-injection filter → future_trigger.
- **ZO3:** Structured citations / post-hoc classifier → future_trigger; MVP self-report in PR2.
- **A2 ZO1:** Coupling between REMEMBER_CONTENT_TOO_LONG and TOOL_ARGS_JSON_MALFORMED envelopes → judged low-risk (complementary, not conflicting).
- **A2 ZO2:** Header rename risk for "what do you remember" style questions → judged manageable (still injects context; "unless asked" clause covers explicit requests).

---

## Fold classifications

**Same-PR mitigatable (all shipped in PR #3631):**
- F-D1a — save-return `truncated:bool` + `original_len:int`
- F-D1b — pre-parse raw-string gate at `unified_pa_entrypoint.py:2232-2272` (revised from parsed-content check per T1 pass 2 correction)
- F-D1c — cap-hit envelope migrated to `_handler_error('save', 'cap_hit', ...)`
- F-D1d — save-status consolidation (`'created'` | `'duplicate_updated'`)
- F-D1e — 10 happy-path tests
- F-D5a — operator doc mentions three-layer split
- F-Z1 — PA prompt header rename

**Future_trigger (logged to Rigby Tool Gap Ledger + next-session queue):**
- F-ZO2 — relevance-threshold pre-injection filter (needs relevance-scoring infra; not blocking).
- F-ZO3 — structured citations OR post-hoc classifier for stronger "used" signal (self-report MVP in PR2).
- F-D2-broad — broader non-PA LLM-bypass audit spec (Rigby's sweep found dozens of candidates; PR2 targets `ProjectBuilderOrchestrator` only).
- **NEW at close:** F-D4-cap-drift — the live-dispatch smoke discovered Chris's user has 1803 `UserMemoryContext` rows against a 200 cap. This isn't a PR1 regression (the cap-hit branch is working exactly as designed) but is a real hidden auto-accumulation. Directly validates D4 hygiene urgency for PR2.

---

## Post-merge findings

**Live-dispatch smoke (via Rigby):**

The cap-hit envelope was **live-verified in production form** — return matched the S2879 canonical shape exactly:

```json
{
  "success": false,
  "error_code": "cap_hit",
  "error": "Memory limit reached (200 items). Delete old memories first.",
  "action": "save",
  "current_count": 1803,
  "max_items": 200
}
```

The created / duplicate_updated / truncated paths could not be live-exercised because the save was gated by cap-hit. These paths are locked by the 10 unit tests + Rigby's A2 line-range verification. Live E2E on those paths deferred to PR2 (post-hygiene when a `memory_hygiene_audit` command exists to safely inspect/prune the 1803 rows).

**Cap drift discovery (new future_trigger for PR2):**
1803 rows against a 200 cap indicates one of:
- `MEMORY_MAX_ITEMS` was previously higher, memories accumulated, then it was lowered
- Some non-`remember_tool` code path bypasses the cap check and writes directly
- The cap was never enforced before this session's migration (legacy shape)

Sampling the top rows shows many are auto-generated `"Event: Deploying"` / `"Version Build: ..."` / `"Repo Slug: ..."` content that looks like an auto-memory ingestor writing on release/deploy events. Investigating and reconciling this is directly in-scope for PR2's `memory_hygiene_audit` command.

---

## Open follow-ups for S2987+

**PR2 for spec ba968ac1 (queued as S2987 first-action):**
- MemoryUtilizationTrace with layer discriminator (D3)
- `memory_hygiene_audit` management command (D4)
- `UserMemoryContext` migration: `is_active` + `superseded_by` + `superseded_at`
- Narrow non-PA preflight for `ProjectBuilderOrchestrator._build_project_with_llm_only` (D2 MVP)
- Reconcile the 1803-vs-200 cap divergence surfaced in this session's live-dispatch smoke

**Broader D2 audit (future spec, not PR2):**
Rigby's LLM-bypass sweep found 14 `enforce_real_ai(` sites + 9 `client.responses.create(` + 80 `client.chat.completions.create(` non-PA callsites. Follow-up spec should audit each for user-facing personalization impact and decide preflight scope. Log to Rigby Tool Gap Ledger as "audit non-PA LLM flows for memory preflight".

---

## Playbook adherence

- ✅ **PLAYBOOK-7.7.1** (spec→ship, 9 phases) — all walked.
- ✅ **PLAYBOOK-7.7.2** (SIGN tool_runs mandatory) — 34 total tool_runs across 4 SIGN passes; no rubber-stamps.
- ✅ **PLAYBOOK-7.7.3** (Chris-facing framing plain English + ≤1 decision) — presented 1 decision (2-PR split vs bundle).
- ✅ **PLAYBOOK-7.4.4** (recycle after merge, `recycle-all` for frontend) — backend-only PR; `make recycle-all` used (diff detection correctly skipped frontend rebuild).
- ✅ **PLAYBOOK-6.10.7** (zoom-out ask per SIGN cycle) — 2 zoom-out prompts per SIGN (5 total across passes).
- ✅ **PLAYBOOK-6.10.8** (fold classification SIGN discipline) — 7 same-PR + 3 future_trigger classified, 4th future_trigger added at close from live-dispatch discovery.
- ✅ **PLAYBOOK-3.2.3** (TransactionTestCase for dispatcher-path handler tests) — S2986 tests use TransactionTestCase per S2885 Fold 1 (2nd trigger + subsequent, now Playbook v0.9.0 rule).

---

**HEAD at close:** `857633411` (PR #3631 merged; docs cascade PR TBD; recycle-all clean at `sha=85763341193d`).
