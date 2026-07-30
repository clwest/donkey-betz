# Session 3039 — S3037 reliability-audit backlog closeout (S7 + S9 + D10 + PA workspace fix)

**Closed:** 2026-07-29 (evening)
**HEAD at close:** `b5dbb89b6` (post-D10-follow merge, post-recycle)
**Session shape:** 4-PR arc; each PR opened with a live-data ORM probe → Rigby SIGN → ship → recycle → live verify. Every SIGN cycle grounded in ≥4 real tool_runs. All 4 folded as `same_pr_mitigatable` — zero forward-carries opened. The audit shipped as PR #3775 immediately surfaced its own follow-up code bug, which was root-caused + fixed same-session as PR #3776.

---

## What shipped

### PR #3773 (`8f2e72570`) — `feat(s3039-s7): route ThinkingAgent ORM through sync_to_async — drop env-var race`

Discharges S3037 backlog **S7** (CRITICAL, ~1 session, 67% async failure on ThinkingAgent).

- **Root cause:** S2951's `DJANGO_ALLOW_ASYNC_UNSAFE=true` env-var scope in `_execute_sync` was process-global. Under `--pool=threads --concurrency=2` (long_running worker), thread A's `finally` block could pop the flag while thread B was mid-sync-ORM inside its own `asyncio.run` — Django `SynchronousOnlyOperation` fires. Concrete evidence: 6 failed AgentExecution rows on 2026-07-25 02:12–02:50 UTC, all fast (1.4–10s exec, before the LLM call = happens in sync ORM inside `_build_intelligent_prompt`).
- **Fix:** `think()` wraps `_format_context_for_thinking` with `sync_to_async(thread_sensitive=True)` (Rigby ask #1). Removed both env-var toggles in `execute()` + `_execute_sync()` — the env var toggle was racy AND redundant once ORM ran off the loop thread.
- **Regression test** (`test_thinking_agent_async_boundary.py`, 4 cases): env-var invariant guard, 2 concurrent execute() with widened race window via monkeypatched sleep, spot-check that ORM runs off the loop thread, `think` remains async def.
- **Live verify:** 4 parallel Brainstorm dispatches through `execute_agent_task → long_running --pool=threads --concurrency=2` all completed 4/4 post-recycle.

### PR #3774 (`dec58f1a1`) — `feat(s3039-s9): wire was_fallback + was_auto_selected end-to-end through LLMCallLog`

Discharges S3037 backlog **S9** (HIGH, ~1 session, S2853 shipping claim not empirically visible).

- **Gap:** 40,189 LLMCallLog rows in 30d, 0/0/0 population on `was_downgraded` / `was_fallback` / `was_auto_selected`. `was_downgraded` was wired at S2856 in `llm_enforcer._save_cost_tracking`, but `was_fallback` + `was_auto_selected` were never plumbed into the enforcer write site. Router path `_log_call` hardcoded `was_auto_selected=False` and never accepted `was_downgraded`.
- **Fix:** `enforce_real_ai` + `_save_cost_tracking` gain `was_fallback` + `was_auto_selected` kwargs threaded through to `LLMCallLog.objects.create`. Router `_log_call` accepts all 3 flags (no more hardcoded False, `was_downgraded` + `pre_downgrade_model_id` newly accepted for parity).
- **Regression test** (`test_s3039_s9_llm_telemetry_flags.py`, 9 cases across 3 classes): default False persistence + explicit True persistence at each write site + top-level `enforce_real_ai` threading path.
- **Live verify:** Seeded a synthetic row via `_save_cost_tracking` with all 3 flags True → persisted correctly. Defaults row also verified. Test rows cleaned up.
- **Deferred to follow-up:** producer threading. `agent_model_router.auto_route` consumers (~30 call sites per Rigby's inventory) still need to thread `was_auto_selected=True` for the field to emit True in prod. Rigby zoom-out fold: "empty but technically present" telemetry risk — mitigated in-PR via explicit True test coverage.

### PR #3775 (`ce39df4e4`) — `feat(s3039-d10): audit_llmcalllog_workspace_gaps command + PA loss finding`

Discharges S3037 backlog **D10 Phase 1** (multi-session DEFERRABLE — historical workspace backfill for 34,049 NULL rows).

- **Reframed the spec:** ORM probes surfaced that the "reporting quality" framing undercounted the story. 30d NULL bucketing: `system_embedding` 20,786 (61%, legit) + `system_test` 7,252 (21%, dev traffic) + **`pa_workspace_lost` 6,177 (18%, real code bug)** + `unclassified` 0 (clean sweep). PA split: 5,995 attributed vs 6,177 NULL = **50.7% PA attribution loss**.
- **Fix:** Read-only `manage.py audit_llmcalllog_workspace_gaps` mgmt command with `--window-days=30` + `--json` args. `_classify(task_type, agent_name)` helper buckets rows; `task_type='embedding'` auto-buckets as `system_embedding` regardless of agent_name (Rigby ask #1 — future-proofs new RAG callers, exact caller still visible in `top_pairs`). `pa_workspace_attribution_loss` finding fires at HIGH when `pa_null >= 100 OR (pa_total >= 100 AND loss_pct >= 10)`.
- **Regression test** (`test_s3039_d10_workspace_gaps_audit.py`, 13 cases, 2 classes): classifier unit tests, JSON output shape, threshold math (small-N no-flag, large-N HIGH flag, mixed-attribution loss_pct calculation), `--window-days` scoping, human output styling.
- **Live 30d run:** Clean sweep (0 unclassified), PA gap flagged HIGH at 50.7%.

### PR #3776 (`b5dbb89b6`) — `fix(s3039-d10-follow): thread user through PA direct enforce_real_ai calls`

Fixes the code-path bug PR #3775 surfaced same-session.

- **Root cause:** 4 direct `self.llm_enforcer.enforce_real_ai` call sites in `unified_pa_entrypoint.py` bypass `_pa_wrapped_enforce_real_ai` (which auto-injects `enforcer_kwargs.setdefault('user', ...)` at line ~886). Each site landed rows with `user=None` → `workspace_resolver.get_active_workspace(None) = None` → NULL workspace. Sites: anthropic-fallback (line ~2055), enrichment analysis (~5363), summarization fallback (~5418), direct-response fallback (~8205) — all fallback paths triggered on specific error conditions.
- **Fix:** Added `user=getattr(self, 'user', None)` to each site (Rigby ask #1 — defensive `getattr` matches the wrapper's pattern). Refreshed the D10 audit's flagged-finding message so it doesn't become stale post-merge (Rigby ask #3 — was "AUDIT ONLY: bug remains unresolved," now "D10-follow fix shipped; pre-fix rows persist in historical windows").
- **Regression test** (`test_s3039_pa_workspace_user_threading.py`, 2 cases): grep-based lint asserts every `self.llm_enforcer.enforce_real_ai(` call outside `_pa_wrapped_enforce_real_ai` has `user=` OR `**enforcer_kwargs`/`**kwargs`/`**payload` spread within 20 lines (Rigby ask #2 — accept `**kwargs` bypasses). Second test locks in the wrapper's centralized `setdefault('user', ...)` line.
- **Live verify post-recycle:** Fresh PA dispatch landed a new LLMCallLog row with `workspace=b4503364-…` (Donkey Betz) populated. Fallback paths only fire on specific error conditions so full 30d loss_pct drop will take a few days of real traffic; plumbing is live.

---

## Rigby SIGN cycles (all AGREE / same_pr_mitigatable)

| PR | Fold classification | Tool runs (evidence) | Asks folded in-PR |
|---|---|---|---|
| #3773 (S7) | `same_pr_mitigatable` | 4 (env-var repo grep, `.think()` call-site grep, S2951 handoff read, execution_history repro) | (1) `thread_sensitive=True`, (2) concurrent test w/ widened race window, (3) env-var invariant guard |
| #3774 (S9) | `same_pr_mitigatable` | 8 (auto_route caller inventory, LLMCallLog population check, S2856 handoff read, enforcer signature verify) | (1) keep scope to plumbing, (2) 3 flags via kwargs, (3) accept-both-defaults-and-True test coverage |
| #3775 (D10) | `same_pr_mitigatable` | 4+ (workspace-caller inventory, `unified_pa_entrypoint` grep, `get_active_workspace` caller grep, S2856 handoff context) | (1) `task_type='embedding'` auto-bucket + new-caller test, (2) top_pairs per bucket, (3) `AUDIT ONLY` caveat |
| #3776 (D10-follow) | `same_pr_mitigatable` | 5+ (line-range reads of all 4 fixed sites + wrapper, enforce_real_ai caller inventory) | (1) `getattr(self, 'user', None)`, (2) grep test accepts `**kwargs`, (3) D10 audit message refreshed |

Every SIGN cycle grounded in ≥4 real tool_runs — per PLAYBOOK-7.7.2 evidence discipline. Zero rubber-stamps. Zero forward-carries opened.

---

## S3037 backlog status after this session

**8/10 items discharged + audit-surfaced regression closed:**

- **S3037 (5):** A1 orphan cleanup, A2 governance defaults, A6 fail-loud, S4 stale ops cleanup, S5 escalation reopen ✓
- **S3038 (2):** S8 deliverable-tool instrumentation, A3 error-type classifier ✓
- **S3039 (3):** S7 ThinkingAgent async race, S9 telemetry flags, D10 Phase 1 audit ✓
- **S3039 D10-follow:** PA workspace-resolver bug (surfaced + fixed same session) ✓

**Remaining:**

- **A6 Phase 2** (trigger-driven) — root-cause `lane_1_platform_readiness` underlying bug once next `morning_brief` failure fires with the surfaced exception (per S3037 PR #3767).
- **S9 producer-threading follow-up** — thread `was_auto_selected=True` from `agent_model_router.auto_route` consumers (~30 call sites per Rigby's tool_run inventory). Same-shape as S9 itself.
- **D10 Phase 2** — actual historical workspace backfill IF the D10 audit's `pa_workspace_lost` bucket doesn't fully evaporate over post-fix windows. Watch the trend before committing to a multi-session backfill arc.

---

## Playbook exercise this session

- **PLAYBOOK-7.7.1** (spec→ship contract) — 4 Flow B spec→ship cycles (S7, S9, D10, D10-follow). Spec = S3037 audit backlog items + D10 audit's own surfaced code bug.
- **PLAYBOOK-7.7.2** (SIGN evidence discipline) — every Rigby SIGN grounded in ≥4 real tool_runs; zero rubber-stamps.
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — plain-English "do we lose anything / is it more work later?" framing on the D10 reframing decision (Option A vs Option 2 pivot after Phase 0 probe) and on each session-mid continuation prompt.
- **PLAYBOOK-7.7.5** (drift/hardening class-scoped A2 sweep) — did NOT fire; all 4 PRs were net-new plumbing, not drift closure. Playbook stays at v0.11.0.
- **PLAYBOOK-7.4.4** (recycle after merge) — `make recycle-all` executed after each of #3773, #3774, #3775, #3776. Events recorded in `logs/recycle_events.jsonl` for each SHA.
- **Cycle 1A verify-before-build** — 24th consecutive session. Every PR started with an ORM probe / repo grep to verify current state before writing code.

---

## Notable session-shape observations

1. **D10 was a spec-reframing arc.** The S3037 backlog framed D10 as "reporting quality, not runtime correctness." Phase 0 ORM probes surfaced 6,177 PA rows in the NULL bucket — a real 50/50 code-path bug hiding in what the spec called deferrable. Chose Option A (ship audit + let it surface the bug) over Option 2 (skip audit, go straight at PA bug); this preserved the diagnostic + shipped both same-session as an ordered pair (D10 → D10-follow).
2. **Rigby zoom-out folds became substrate.** S9's fold ("empty telemetry" risk) shaped the test coverage strategy; D10's fold ("normalizing the gap") shaped the AUDIT-ONLY caveat AND its post-fix refresh at D10-follow. Both examples of `feedback_zoom_out_ask_per_rigby_sign` producing shippable output, not just meta commentary.
3. **Local test DB required manual reset twice.** `--reuse-db` hit `ProgrammingError: relation "core_curatedsignalentry" already exists` — resolved by `psql postgres -c "DROP DATABASE test_unified_donkey_betz"` before pytest re-created. Not a code issue; local dev-env hygiene. Watch for a third trigger before treating as a pattern.
4. **`make recycle-all` between PRs stayed clean.** 4 recycle events landed in `logs/recycle_events.jsonl` with `surviving=none` each. No leftover workers from prior sessions leaked into any post-merge verify.

---

## Files touched (session summary)

**PR #3773 (S7):**
- `core/agents/thinking_agent.py` (+34/-33)
- `core/tests/test_thinking_agent_async_boundary.py` (+191, new)

**PR #3774 (S9):**
- `core/llm_enforcer.py` (+22/-1)
- `core/services/agent_llm_router.py` (+12/-1)
- `core/tests/test_s3039_s9_llm_telemetry_flags.py` (+240, new)

**PR #3775 (D10):**
- `core/management/commands/audit_llmcalllog_workspace_gaps.py` (+246, new)
- `core/tests/test_s3039_d10_workspace_gaps_audit.py` (+214, new)

**PR #3776 (D10-follow):**
- `core/services/unified_pa_entrypoint.py` (+29/-4)
- `core/management/commands/audit_llmcalllog_workspace_gaps.py` (+7/-4)
- `core/tests/test_s3039_pa_workspace_user_threading.py` (+143, new)

Total: 4 PRs, 9 files touched, +1,131/-43 lines net.

---

## Wrapper pin note

Active PA conversation pin at S3039 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**S3040 first action:** Chris to pick between (a) S9 producer follow-up (~30 file light-touch, ~1 session), (b) net-new engineering candidate (breaks the 5-audit-ship streak), (c) A6 Phase 2 (trigger-driven, wait for next morning_brief failure).
