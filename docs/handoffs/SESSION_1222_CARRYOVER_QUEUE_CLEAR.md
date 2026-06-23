# Session 1222 — Carryover Queue Clear (P1 + P2 + P3 all closed)

**Status:** All 4 carryovers from Sessions 1216-1218 closed in one session. 4 small PRs.
**Date:** 2026-06-23.
**Active conversation:** `pa-58737666f25741dc` (continued from Sessions 1217-1221).
**Prior session:** [`SESSION_1221_TIER_1_PLUS_TIER_2_FROM_7AE61CF7.md`](./SESSION_1221_TIER_1_PLUS_TIER_2_FROM_7AE61CF7.md).
**Next session entry point:** Session 1223 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1223".

## TL;DR

After the watchdog/timeout investigation arc closed in Session 1221, Session 1222 swept through the four deferred carryovers that had been bouncing across the start-here doc since Sessions 1216-1218. All four closed cleanly — three were deterministic deletes once telemetry verification surfaced zero historical usage; the fourth (reasoning-contract enforce promotion) was a 24-line workflow flip after the violation count on main stayed at zero through a 2-session burn-in.

## Session Manifest

### PRs merged

| # | Title | Carryover from |
|---|---|---|
| **#2522** | `chore(session-1222): remove OpenAIProvider class (B2 follow-on from PR #2507)` | Session 1217 PR #2507 |
| **#2523** | `chore(session-1222): trim zero-execution agent refs from content_studio + ops timeout map (P2 Cat A+B)` | Session 1218 P2 |
| **#2524** | `chore(session-1222): remove dormant gateway dispatch actions (P2 Cat C)` | Session 1218 P2 |
| **#2525** | `chore(session-1222): promote check-reasoning-contract.yml from --warn-only to enforce (P3)` | Session 1216 Phase E |
| **(this PR)** | `docs(session-1222): close — carryover queue clear + Session 1223 start-here` | — |

## Item-by-item close

### P1 (PR #2522) — OpenAIProvider B2 follow-on

Session 1217 PR #2507 replaced `OpenAIProvider.generate` with a deprecation stub raising `NotImplementedError` while waiting for telemetry confirmation. **Session 1222 verification ran first:** all `real_*` agent classes (RealContentCreator, RealJobExecutor, RealWorkDeliveryEngine, RealClientAcquisition, AIProposalEngine, FreelanceJobAnalyzer, ConcreteExecutor) had **zero `AgentExecution` rows + zero `LLMCallEvent` rows all-time**. Codebase grep for `generate_llm_response` and `process_with_llm` (the methods that `enable_agent_with_llm` attaches) returned **zero callers**.

**Changes:** `ai_core/agents/agent_llm_integration.py` shrunk 202 → 99 lines. `OpenAIProvider` class gone, `'openai'` branch collapsed in `generate_for_agent`, `_track_usage` simplified, unused `get_async_openai_client` import dropped. Stub test rewritten as a 3-test lock-in suite (`test_openai_provider_no_longer_importable`, `test_singleton_default_provider_excludes_openai`, `test_anthropic_and_mock_providers_still_registered`).

### P2 (PR #2523 + #2524) — remaining 9 gateway-referenced classes

Session 1218 P2 left these 9 classes in because they were still referenced by gateway code:

- `td_handlers_content.py`: `ContentDiversityOrchestrator`, `ContrarianAgent`, `LineMovementAnalyzer`, `PerformanceAnalystAgent`, `SharpActionDetector`, `VoiceCriticAgent`
- `td_handlers_ops.py` / `td_handlers_core.py`: `ResolveAgent`, `TalkingCharacterAgent`, `WhaleWatcherAgent`

Telemetry re-verification: **zero AgentExecution rows + zero LLMCallEvent rows all-time** for every one. Triaged with Rigby into 3 categories:

| Category | Sites | Risk | Handling |
|---|---|---|---|
| **A** — read-only string list | `td_handlers_content.py:4513` `studio_agents` list | None | Trim 4 names from list. |
| **B** — timeout config map | `td_handlers_ops.py:3487-3492` `_ops_timeout_config_read` defaults | None | Trim 3 entries from dict. |
| **C** — active gateway dispatch actions | `content_tool.sharp_action`, `content_tool.line_movements`, `studio_tool.generate_talking_video` | Public-ish tool surface | Drop the actions per Rigby's lean (zero usage = dormant). |

Per Rigby's packaging recommendation: **Cat A + B together** in PR #2523 (89 → 22 lines net) for "pure trims, extremely safe"; **Cat C alone** in PR #2524 for "tool-surface removal deserves its own review/merge message" (net -67 lines).

**Bonus:** PR #2524 also removed the `unified_pa_entrypoint.py` formatters for the dropped actions. The formatters assumed synchronous `{items, total}` shape but the dispatcher was async (returned `{task_id, mode: 'async'}`) — a schema mismatch dating back to the Session 1075 async conversion. Both ends gone now.

**Tool-surface change visible to users:** these `studio_tool` / `content_tool` actions are now removed from the schema. Future "why is `generate_talking_video` missing?" questions: agent class file remains in `core/agents/talking_character_agent.py`; the **surviving entry point** is `studio_tool.create_talking_video` (different pipeline, uses `create_talking_video_task`, generates the image AND the talking video in one step).

### P3 (PR #2525) — promote `check-reasoning-contract.yml` to enforce

Session 1216 Phase E shipped the AST-based reasoning-contract checker in `--warn-only` mode. The Phase C+D close-out left zero violations on main; Sessions 1217-1221 also left zero violations. Local run on current main this session re-confirmed:

```
$ python tools/check_reasoning_contract.py --root . --whitelist .ci/reasoning_guard_whitelist.txt
Reasoning-contract check: no violations.
```

**Changes:** dropped `--warn-only` from the python invocation. Updated inline comment + `GITHUB_STEP_SUMMARY` copy from "warn-only" to "enforce." 24-line workflow flip.

**From here on:** PRs that introduce a forbidden kwarg (`max_tokens`, `temperature`, `top_p`, `frequency_penalty`, `presence_penalty`) to gpt-5.x reasoning models via direct OpenAI SDK calls fail this check. Companion runtime guard in `core/services/openai_client_factory.py` (env: `OPENAI_REASONING_GUARD`, default `warn`).

## Rollback levers (if something breaks)

The enforce-mode flip is the only change in this session that can block other PRs. If a false positive surfaces or an urgent fix needs to land:

```bash
# Re-add --warn-only to .github/workflows/check-reasoning-contract.yml line ~42:
#   python tools/check_reasoning_contract.py --root . --whitelist .ci/reasoning_guard_whitelist.txt --warn-only
```

Single-line revert. The runtime guard stays in `warn` mode by default, so production callers see no behavior change either way — only PR CI does.

The B2 + Cat A/B/C removals are deletes-of-dormant-code. Restoration is `git revert` if needed; no dependents to fix.

## What this session did NOT do (Session 1223 candidates)

1. **Tier 3 from P2 deliverable (`7ae61cf7-…`)** — wrap the openai_client_factory clients at construction time. Heavier contract change. Defer unless Tier 1 + Tier 2 leakage persists.
2. **Production observation window for the Session 1221 watchdog fixes** — Tier 1 + Tier 2 merged ~2h before Session 1222 opened. Real signal needs longer burn-in.
3. **Delete the dormant agent class files** (`SharpActionDetector`, `LineMovementAnalyzer`, `TalkingCharacterAgent`, `ContentDiversityOrchestrator`, `ContrarianAgent`, `LineMovementAnalyzer`, `PerformanceAnalystAgent`, `SharpActionDetector`, `VoiceCriticAgent`, `ResolveAgent`, `WhaleWatcherAgent`). Per Rigby's recommendation, files stay in `core/agents/` for future re-enable. Could be a Session 1224+ cleanup if Chris wants the deeper trim.
4. **Verify the enforce flip didn't introduce false positives** — first 24-48h of PR CI runs are the canary. See "Production observation window" in Session 1223 start-here.

## Memory updates worth carrying forward

No new feedback memories this session. Three existing rules dogfooded:
- `feedback_rigby_collaboration.md` — sent a 3-category triage card; Rigby ratified the 2-PR packaging (Cat A+B together, Cat C alone) over my initial 3-PR plan.
- `feedback_corpus_walks_surface_mechanism_drift.md` — schema-vs-dispatcher mismatch on `sharp_action` / `line_movements` (formatters expecting sync `{items, total}` vs dispatcher returning async `{task_id, mode}`) was a Session 1075 drift surfaced by removal.
- `feedback_triage_decision_card_pattern.md` — Cat A / B / C lean + ratification path matched the "agree all" pattern Chris validated three times in Session 1170.

## Files touched this session

```
ai_core/agents/agent_llm_integration.py                                         (-103 lines net)
tests/ai_core_tests/test_agent_llm_integration_provider_stub.py                 (rewrote as 3-test lock-in suite)
core/services/td_handlers_content.py                                            (-37 lines)
core/services/td_handlers_core.py                                               (-19 lines net)
core/services/td_handlers_ops.py                                                (-3 lines net)
core/services/unified_pa_entrypoint.py                                          (-30 lines)
core/services/pa_tool_schemas.py                                                (-3 lines net)
.github/workflows/check-reasoning-contract.yml                                  (-4 lines net)
docs/handoffs/SESSION_1222_CARRYOVER_QUEUE_CLEAR.md                             (NEW, this file)
00-START-NEXT-SESSION.md                                                        (Session 1223 FIRST THING rewrite)
```

Total net delta across all 4 code PRs: **~200 lines removed** from main.
