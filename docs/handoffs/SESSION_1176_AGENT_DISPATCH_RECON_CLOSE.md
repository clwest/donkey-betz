# Session 1176 — Agent dispatch + follow-up wake stress-test recon (closed)

**Status:** Closed. 3 findings filed. 2 cells of the Pass B matrix verified end-to-end (success path; failed-branch backend). Cells 3–8 deferred.
**Date:** 2026-06-20
**Driving question:** "Where are wires built but not completely connected?" — specifically in the Session 1175 follow-up wake feature shipped end-of-prior-session.
**Prior session handoffs:**
- [SESSION_1175_FOLLOWUP_WAKE_CLOSE.md](./SESSION_1175_FOLLOWUP_WAKE_CLOSE.md) — feature ship close
- [SESSION_1175_AGENT_FOLLOWUP_DEMO.md](./SESSION_1175_AGENT_FOLLOWUP_DEMO.md) — 60s demo script

**Tracking deliverable:** `61247479-1976-4ba8-bc8a-ea67f66ead45` ("Session 1176 Recon — Half-wired paths to stress-test"), in Local QA workspace `6372a003-9a3e-4ce3-8c57-bf3912c9ca75`. Final content_length: 10017 chars.

## TL;DR

Session 1176 took the Session 1175 vertical slice and stress-tested it through Rigby. Live verification confirmed the **follow-up wake success path is fully wired end-to-end** (backend → WS → AgentCompletionBanner UI; three browser observations across two agents). The failed-terminal branch is verified at the backend level (immediate-fire returns `mode=delivered_immediately, state=fired` on `status=failed`) but visual banner confirmation was blocked by F3 (EditorAgent non-determinism). Three real findings filed; none are P0.

The session was also a structural test of Rigby's tool discipline — running the matrix one cell at a time per `feedback_rigby_deliverable_content` and surfacing places where her tools or scope drifted.

## Verified end-to-end

| Branch | Method | Evidence |
|---|---|---|
| Follow-up wake SUCCESS path (`mode=delivered_immediately` on `status=completed`) | Live dispatch + browser observation | 3 banner sightings in Command Center composer footer (Chris confirmed visually). Executions: ResearchAgent `2935f7bb…`; EditorAgent `660f9234…` (unexpected success — see F3). |
| Follow-up wake FAILED branch (backend only) | EditorAgent fail-loud + tool-response inspection | Execution `6e9e42ad…` reached `status=failed` in 3.6s with typed `error_message`; schedule_followup returned `mode=delivered_immediately, state=fired`. Visual confirmation deferred (see F3). |
| schedule_followup return-shape stability (PR-2b-2) | 11-key assertion on success and failed branches | All 11 keys (`success, mode, subscription_id, execution_id, execution_status, state, expires_at, fired_at, after_seconds, message, error`) present on both branches. |
| PR-1 conversation_id gate | Live test on non-PA execution | schedule_followup on ContentWriterAgent watchdog timeout `5c103be3…` (beat-task origin) returned clear error: "Cannot subscribe: ... conversation_id is NULL. Follow-up requires a PA-originated dispatch." Gate doing its job. |

## Findings filed in deliverable 61247479

### F1 — `deliverable_tool update` silent fallback above size threshold

- **Observed:** updates worked at content_length 3962 and 5621; failed silently at would-be ~7100 (Cell 3 attempt, payload contained nested-JSON-in-string from AudioAgent error). PA tool dispatcher returned `{"action":"list"}` instead of `{"action":"update"}` — payload was rejected before reaching the update handler, with no exception raised.
- **Second repro during close-out:** another update at would-be ~7260 chars (NO nested JSON, ~2.7kB clean-prose append) also fell back to list. Workaround: `deliverable_tool append` does NOT hit the threshold and persisted cleanly to final 10017 chars.
- **Updated hypothesis:** threshold is size-based around 6–7kB, NOT solely the nested-JSON escape character (F1's filed description still lists both — bisect needed).
- **Severity:** silent — no exception, no warning. Callers think the update succeeded.
- **Workaround:** `deliverable_tool append` for any content larger than ~6kB.

### F2 — Non-PA-originated executions cannot surface via follow-up wake

- **Observed:** schedule_followup on ContentWriterAgent watchdog timeout `5c103be3` (Operator Edge weekly newsletter beat task) returned `success=false` with explicit error "conversation_id is NULL. Follow-up requires a PA-originated dispatch."
- **By design:** PR-1's `AgentExecution.conversation_id` gating field is doing what it was built to do — prevent cross-tenant follow-up leakage.
- **Implication:** all beat-task crashes, watchdog timeouts, autonomous-workflow failures are **invisible to Rigby via the follow-up path**. They're observable only via `ops_tool failure_signatures` polling.
- **Coverage gap to note:** before any user-facing claim like "Rigby will tell me when things break", we need either (a) `ops_tool failure_signatures` polling integrated with the PA inbox, or (b) a non-PA-origin escalation path that still respects tenant boundaries. Not a bug, but a real gap before broad messaging.

### F3 — EditorAgent non-deterministic on empty content (fail-loud bypassed by generation fallback)

- **Observed:** two consecutive dispatches with IDENTICAL task body `Edit the following text for clarity and correctness. Preserve meaning. Text:\n` produced different outcomes:
  - Run `6e9e42ad`: `status=failed` in 3612ms with typed error "No content provided. Include 'blog_id' or 'content' in context." (CORRECT per `feedback_editor_fail_loud`).
  - Run `660f9234`: `status=completed` in 17761ms, empty error_message (5x runtime — the agent LLM-generated content from nothing).
- **Smoking gun:** the 5× runtime delta. Run 2's 17.7s is consistent with LLM generation; run 1's 3.6s is consistent with validation-and-return.
- **Mechanism (hypothesis):** typed validation fires sometimes; generation fallback fires other times. Path divergence is inside the agent body, not at the dispatcher.
- **Severity:** masks caller bugs — empty-context callers sometimes "succeed" with hallucinated content. This is exactly the failure mode `feedback_editor_fail_loud` warned about: "fix at dispatcher layer, never inside agent."

## Deferred to Session 1177+

| Item | What | Why deferred |
|---|---|---|
| Cells 3–8 of Pass B matrix | revoke/cancel terminal, refresh-mid-run WS reconnect, second-tab dedup, media-artifact agent path | Session ran on token budget; 3 findings already filed; can resume in the fresh conversation |
| Visual confirmation of failed-status banner | render failed status + error_message in Command Center | Blocked by F3 — EditorAgent non-determinism makes visual repro unreliable. Need a different deterministic-failure path (force typed error in another agent, or Django shell mark-as-failed bypass) |
| F1 bisect | confirm threshold is size vs nested-JSON | Two repros (one with nested JSON at ~7100, one clean prose at ~7260) both fell back to list — strong signal for size-only, but worth a clean bisect to nail the threshold |

## Operational artifacts

- **Tracking deliverable:** `61247479-1976-4ba8-bc8a-ea67f66ead45` (Local QA workspace, content_length 10017)
- **Conversations:**
  - `pa-58c916edf96044cc` retired at health 25/100 (43 turns, ~21.5k tokens, 9 topics)
  - Successor `pa-9b82bcc72e1945ce` ("Session 1177 — TBD") created via `session_tool create_fresh`
  - `tools/pa_local.sh` updated to pin the new conversation
- **Live test executions (PA-originated, this session, conv `pa-58c916edf96044cc`):**
  - `2935f7bb-d806-4244-9f26-280ce1156715` — ResearchAgent, completed (23.6s) — Cell 2 baseline
  - `6e9e42ad-e3b8-4f18-b856-96a408e982cc` — EditorAgent, failed (3.6s) — failed-branch backend test
  - `660f9234-0a60-4e93-bd03-92b89136800a` — EditorAgent, completed unexpectedly (17.8s) — F3 evidence
  - `80e68a77-1cff-486d-9f7d-9a9dd8ba96eb` — ResearchAgent, completed — Rigby-drift artifact, not used
- **Scratch artifact:** `691e9833-14af-4128-9899-9d684c361383` ("SCRATCH — update test") used to confirm `deliverable_tool update` works on small payloads (47 chars). Safe to delete in Session 1177 if cleaning up.

## How to continue in Session 1177

Lowest-friction paths from where this session ended:

1. **Visual confirmation of FAILED banner.** Use ContentWriterAgent (not EditorAgent — F3) dispatched from PA with a deliberately-missing required field, OR Django shell to mark a fresh PA-originated execution as failed manually. Then schedule_followup + watch browser.
2. **F1 root cause.** Two paths: (a) bisect via clean-prose updates at 6500 / 6700 / 6900 / 7100 to find size threshold; (b) read the `deliverable_tool` dispatcher code (likely under `core/services/td_handlers_deliverables.py` or similar) and trace the silent fallback to default action.
3. **Cells 4–8 of Pass B.** Continue per the deliverable scaffold. Revoke/cancel is the last terminal outcome; refresh-mid-run + second-tab stress the WS subscription side; media-artifact tests artifact linking.

## Session structure / Rigby discipline notes

- **Memory rule `feedback_rigby_deliverable_content` validated:** Rigby fabricated an 8-cell preview in chat on the first ask but only persisted 61 chars. Caught via tool-run verbose block check. The fix-pattern (Claude writes Cell 1 verbatim, Rigby extends one cell at a time with `update + detail` verification) worked cleanly for Cells 1–2.
- **`feedback_rigby_tool_verification` validated:** when Rigby claimed "`deliverable_tool update` is broken," the SCRATCH 3-call test (create → update → detail) proved update works at small payloads. Her original claim was wrong; the real bug is the size threshold (F1).
- **`feedback_rigby_scope` partially validated:** Rigby self-drove dispatch + polling + result analysis correctly for Cells 1–2, but on the round asking for an EditorAgent failure repro she dispatched a ResearchAgent with a success-path task instead. Reset prompt got her back on track. Pattern: when the ask requires a specific failure mechanism, name it concretely in the prompt (don't trust "pick a deterministic failure").
