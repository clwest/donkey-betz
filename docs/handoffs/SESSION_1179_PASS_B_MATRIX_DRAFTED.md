# Session 1179 — Pass B matrix Cells 3-8 drafted in deliverable 61247479

**Status:** All 6 cells drafted with the same 7-section template as Cells 1-2 (Agent / Terminal outcome / Client state / Dispatch / Watch / Pass / Fail signature / Duration). Predicted findings filed from code-walk recon — none have been live-verified yet. Live execution = Session 1180 PRIORITY 1.
**Date:** 2026-06-20
**Driving question:** Rigby's Session 1178 close ranking: "Pass B is the hardening pass that prevents the next 'looks wired but breaks in edge cases' incident."
**Prior session handoffs:**
- [SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md](./SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md) — Phase 2 auto-wake live-verified
- [SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md](./SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md) — Pass B matrix scaffold + Cells 1-2 PASS, Cells 3-8 TBD

## TL;DR

Cells 3-8 of the Pass B follow-up wake matrix are now drafted in deliverable `61247479-1976-4ba8-bc8a-ea67f66ead45` (Local QA workspace). Each cell follows the Cells 1-2 template and includes a code-walk recon finding that PREDICTS the fail signature with specific file:line references. No live execution yet — this is the design + predicted-finding pass. Session 1180 picks up the actual stress-test run, ~1 hour estimated (6 cells × ~10min each).

## Cells drafted

| # | Theme | Predicted finding | Code reference |
|---|---|---|---|
| **3** | Revoke/cancel terminal | Sub stays armed → expired; no banner, no bubble | `agent_router.py:1584-1597` — cancel path updates `status='cancelled'` but does NOT call `fire_agent_followup_subscriptions` (5 sites in `tasks_agents.py` do call it) |
| **4** | Refresh-mid-run + WS reconnect | Banner missed, but bubble persists. No replay endpoint | `paStore.ts:48` — seenCompletions ring dedupes by execution_id but no "fetch missed since" |
| **5** | Second-tab dedupe | Two consumers → two ChatConversation rows (bubble dedupe bug) | `consumers_pa_conversation.py:103-139` — `create_completion_row` is `.create()`, not `.get_or_create()`. No DB uniqueness on (conversation_id, metadata.execution_id) |
| **6** | Tab-not-focused / backgrounded | Persistence proof — bubble survives. Banner refire on focus = nice-to-have | (no defect predicted; behavioral test) |
| **7** | Multi-agent dispatch in one turn | 2nd completion overwrites 1st banner. Bubbles persist correctly | `paStore.ts:350-356` — `recentAgentCompletion` is single state slot, no queue |
| **8** | Media-artifact agent | `artifact_pointers={}` hardcoded — banner/bubble don't surface generated artifacts | `tasks_agents.py:133` — Phase 1 open follow-up #6 deferred indefinitely |

## Rigby's summary footer (auto-added)

Quoted verbatim from the deliverable:

> Pass B Cells 3–8 are now drafted as a targeted stress-test matrix for the follow-up wake feature under real UX conditions (cancel terminal, refresh/reconnect, multi-tab, backgrounding, multi-dispatch fanout, and media artifacts). The current recon predicts (1) **cancelled terminals won't fire auto-wake** because the cancel path updates status without calling `fire_agent_followup_subscriptions`; (2) **WS reconnect won't replay missed completion banners**, and the durable bubble only surfaces on a subsequent chat-history fetch; (3) **multi-tab will duplicate persisted completion bubbles** because each tab consumer independently calls `ChatConversation.objects.create()` with no uniqueness guard; (4) **multi-agent completions can overwrite banners** due to a single `recentAgentCompletion` slot (no queue), even though bubbles persist; and (5) **media completions provide no navigation** because `artifact_pointers` is still hardcoded `{}` despite artifacts living in `AgentExecution.output_data`. Phase 3 work should therefore: add `fire_agent_followup_subscriptions()` to the cancel terminal path; implement **completion replay on WS reconnect** (or an explicit "missed completions since" endpoint) so users don't need a refresh/switch to see bubbles; enforce **idempotent persistence** for completion bubbles (DB constraint + get_or_create or move persistence server-side pre-broadcast); change the banner store to a small **queue**; and populate `artifact_pointers` from known `output_data` fields plus render click-through links/previews in the banner and/or bubble.

Cell 6 is treated as a behavioral test, not a predicted defect — hence 5 predicted findings, not 6.

## Workflow notes worth carrying

1. **`deliverable_tool append` is the only reliable write for >6kB docs.** All 6 cell appends (3152 / 3647 / 3204 / 3709 / 3755 / 3989 chars) landed without silent fallback. Per `feedback_deliverable_tool_use_append_for_large_payloads` — F1 from Session 1176 still unfixed. `update` would have rejected at least Cells 4-8.
2. **The stub-then-append pattern leaves duplicate headings in the doc.** Each `### Cell N — [TBD]` stub stayed at the top of the matrix section; the full content went at the end. Acceptable for v1 — a Pass B v2 deliverable can do a clean rewrite once the live runs add PASS/FAIL evidence per cell.
3. **Code-walk recon before drafting each cell paid off.** Five of six cells have a specific file:line that predicts the fail signature. When Session 1180 runs the actual tests, each PASS or FAIL is testable against a concrete code location instead of vague "wake feature broken" framing.
4. **Decision-card-with-leans confirmed again.** Rigby pushed back per-cell only on Cell 7 (start with 2-agent, expand to 3 if clean) — all other cells ratified as drafted.

## Carry-forward — Session 1180

### Priority 1: Live execution of the Pass B matrix

Walk each cell's "Dispatch sequence" + "Watch" sections in the browser + DB + worker log. Record PASS/FAIL with concrete evidence (execution_ids, subscription_ids, SQL counts, log snippets, screenshots). Estimated ~1 hour total (~10 min per cell including write-up).

Recommended order (highest-prediction-confidence first):
1. **Cell 5** (second-tab dedupe) — single SQL count assertion, easiest to verify
2. **Cell 3** (cancel terminal) — backend-only check, no UI dependency
3. **Cell 4** (refresh-mid-run) — clean WS reconnect test
4. **Cell 7a** (2-agent fanout) — banner overwrite is visual + reproducible
5. **Cell 8** (media artifact) — image_generation_agent runtime is the biggest unknown
6. **Cell 6** (backgrounded tab) — persistence proof, lowest defect probability

### Conversation hygiene

`pa-9b82bcc72e1945ce` retired at 60/100, ~30 turns, ~15k tokens, 10 topics — Rigby `suggest_fresh`. Successor `pa-a5fecc400c0f4152` (Session 1180 — Pass B matrix execution + evidence) created via `session_tool create_fresh`. `tools/pa_local.sh` updated.

### After Pass B execution — Phase 3 follow-up PRs

Each predicted FAIL becomes a small focused PR:
- PR: add `fire_agent_followup_subscriptions(execution_record)` to `agent_router.py:1597` cancel path
- PR: `consumers_pa_conversation.create_completion_row` → `get_or_create` on `(conversation_id, metadata->>'execution_id')` + DB-level partial unique index
- PR: `paStore.handleAgentCompleted` → queue + banner displays head, fades 6s per item
- PR: `fire_agent_followup_subscriptions` populates `artifact_pointers` from `AgentExecution.output_data` (image_id / video_id / deliverable_id / media_id / blog_id / asset_id) + frontend banner renders click-through
- PR (longer): `GET /api/pa/conversations/<id>/completions?since=<timestamp>` + paStore calls it on WS reconnect

## Files touched this session

- `deliverable 61247479-1976-4ba8-bc8a-ea67f66ead45` — content grew from 13,171 → 33,138 chars across 7 appends (6 cells + summary footer)
- `tools/pa_local.sh` — pinned conversation updated to `pa-a5fecc400c0f4152`
- `00-START-NEXT-SESSION.md` — Session 1180 entry point reset
- `docs/handoffs/SESSION_1179_PASS_B_MATRIX_DRAFTED.md` (this file)

No code changes. No PRs needed for the matrix work itself — Phase 3 PRs come after Session 1180's live execution surfaces FAIL evidence.
