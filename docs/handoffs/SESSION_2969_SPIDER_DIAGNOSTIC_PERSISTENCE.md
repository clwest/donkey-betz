# SESSION 2969 — Spider diagnostic persistence shipped (Chris→Rigby→CC workflow first walk)

**HEAD at close:** `e6dea2d52` (PR #3591 merged; docs cascade PR TBD)
**Branch shape:** `feat/s2969-spider-diagnostic-persistence` → main (merged, branch deleted)
**PR count:** 1 code PR merged (#3591)
**Session cost:** minimal — no v2 subprocess dispatches this session; only PA-tool calls to Rigby

---

## What shipped

**One code PR merged tonight:**

| PR | Title | Shape |
|---|---|---|
| **#3591** | `feat(s2969): PR-A — spider diagnostic persistence (empty-runs + missing-creds)` | +1024/-5 across 5 files (new spider_diagnostic module + runner refactor + retention task + 30 tests + docs section) |

**One docs cascade PR to file at session close:** handoff + 00-START refresh + wrapper pin bump.

---

## The workflow reframe: first walk

**This session was the first application of the S2968 end-of-session reframe.** Chris + Rigby produced an engineering-spec Deliverable (`ae3a9ffb-8091-45d9-a1f0-eca2af6b642a` — *Spider Fix Plan*). Chris handed the deliverable UUID + callback conversation ID (`pa-026c3ac3ae60`) to CC on session open. CC:

1. Read the spec via `deliverable_tool.get` (surface truncated → verified full via ORM)
2. Explored the code surface (runner path + spider registrations + dedup service + execution log model)
3. Ran a live probe → discovered `SpiderExecutionLog` shows 76/72 successful runs for reddit/sports_injuries last 7d, but 0 `LegacySpiderData` rows. The "never_run" symptom was really a dashboard-reads-wrong-table bug
4. Routed a plan + zoom-out ask to Rigby via `pa-026c3ac3ae60` (T1 pre-code SIGN)
5. Rigby AGREE'd with 3 tweaks — folded
6. Implemented + tested (30/30 passing)
7. Routed A2 post-code SIGN with concrete file+line evidence per PLAYBOOK-6.10.9
8. Rigby REVISE'd on retention strategy + on-demand parity — folded
9. Cycle-2 AGREE from Rigby
10. Pushed + opened PR-A + merged with `--admin` (billing directive) + `make recycle-all` per PLAYBOOK-7.4.4
11. Live-verified via `_impl_run_spider_network` in-shell (bypassed singleton lock beat was holding)
12. Rigby verified via `spider_status_tool.history` — reddit `count: 2`, sports_injuries `count: 1` (was 0/0). "never_run" symptom resolved from the PA-tool surface
13. Rigby verdict: **close PR-B without shipping spider code changes** — 0-items outcome is now correctly classified as `no_items` with fetch failures; root cause is worker network/DNS egress, not spider parsing. Any pursuit of real data is a separate infra arc, not a spider-code arc

**Chris ratified via terminal "ratify."**

The reframe worked. Initiation direction flipped as designed (Chris→Rigby→CC instead of Chris→CC→Rigby). Zero terminal yes/no asks during execution — all decision routing went through Rigby.

---

## PR #3591 — spider diagnostic persistence

**What it adds:**

- **New module `core/services/spider_diagnostic.py`** (+151 LOC): pure helpers for env-flag reads (`SPIDER_EMPTY_RUN_PERSISTENCE_MODE` ∈ `{'off', 'diagnostic_7d', 'always'}` default `diagnostic_7d`; `SPIDER_SKIP_MISSING_CREDS_LOUDLY` default `true`), missing-cred detection (`check_missing_credentials(spider_name)`), diagnostic-dict builders (`build_empty_run_diagnostic`, `build_missing_creds_diagnostic`), and `persist_diagnostic_row()`. Opt-in `SPIDER_REQUIRED_ENV_KEYS` map seeded for `github` / `spotify` / `discord` (verified env key names against actual code usage).
- **Runner changes to `_impl_run_spider_network`** in `core/tasks_spiders.py`:
  - **Phase 1B preflight** at line 436: skip-loudly on missing credentials → persist `skipped_missing_credentials` diagnostic row + `continue` past the fetch entirely
  - **Phase 1A empty-run** at line 498-519: when `unique_items=[]` AND mode != `off`, persist `success_empty` diagnostic row with `empty_reason` (`no_items` | `all_deduped`), `items_before_dedup`, `duplicates`, `ephemeral_empty_run` tag
  - **Phase 1C metrics** at line 534-545 (success) and line 585-599 (exception): `spider_results[i]` now carries `status`, `items_before_dedup`, `unique_after_dedup`, `duplicates`, `persisted_row`
  - **Rigby A2 tweak:** all diagnostic dicts carry `execution_log_id` back-pointer bridging to `SpiderExecutionLog` (documented as best-effort debugging pointer, not FK)
- **Runner changes to `_impl_execute_single_spider_lightweight`** (dashboard Execute button, Rigby A2 REVISE #2) at line 799-822: **Phase 1A only** — persists empty-run diagnostic row so the operator hits Execute and sees a row materialize. Phase 1B/1C intentionally NOT extended here (would confuse operator "poke" surface)
- **New retention task** `core/tasks.cleanup_empty_spider_runs(days=7, batch_cap=5000)` at line 1527: uses `_raw_delete()` to bypass the `SET_NULL` cascade to `NarrativeEvidence` (Rigby A2 REVISE #1). Cap bounds per-run delete. Ships un-scheduled per Rigby T1 verdict — invoke manually until accumulation rates are known
- **New docs section** in `docs/topics/spider-network.md` — "Diagnostic run persistence (S2969)" with feature flags, retention, and a guardrail blockquote clarifying `execution_log_id` is a best-effort pointer, not an FK

**Live proof:**

1. **In-shell dispatch of `_impl_run_spider_network`** (bypasses singleton lock): 80 spiders_run, 548 items_collected, 0 errors, **80 data_collected rows** (was 0 for reddit + sports_injuries at baseline)
2. **Rigby `spider_status_tool.history`**: reddit `count: 2`, sports_injuries `count: 1` — both were `count: 0` at baseline
3. **Diagnostic rows verified via ORM**: reddit + sports_injuries + github + spotify + discord all show `status=success_empty`, `empty_reason=no_items`, `ephemeral=True`, `execution_log_id` linked
4. **Missing-creds preflight not exercised live** because Chris's local env has `GITHUB_TOKEN` / `SPOTIFY_CLIENT_ID` / `DISCORD_BOT_TOKEN` set — the check correctly returned empty list and proceeded to fetch. Unit tests cover the missing-creds branch (`RunnerMissingCredsSkipTests`)

**Test coverage:** 30 tests pass (12 unit + 3 Beat runner + 2 missing-creds + 1 result-shape + 2 lightweight-execute parity + 6 retention filter-semantics + 4 task-shape). Regression check: `core/tests/test_spider_network_governance.py` still 3/3 passing.

---

## What deferred / closed under Rigby's verdict

**PR-B (fix reddit + sports_injuries at the spider level) — CLOSED without ship.** Original spec DoD said "reddit produces ≥5 unique items / sports_injuries produces ≥10 unique items." Rigby's reframe: those acceptance criteria were an **implicit proxy** for "spiders are actually running and status is trustworthy." PR-A achieved that. The remaining "0 items" outcome is now correctly classified as `no_items` with fetch failures — root cause is worker-environment network/DNS egress, not spider parsing bugs. Spider-code tweaks won't fix DNS.

**Follow-on arc queued (Chris picks whether to open):** "Worker egress validation" — does the worker environment have outbound DNS + HTTPS access to `reddit.com` / `rotowire.com` / `rss.nytimes.com` / etc.? Infra arc, not spider code.

---

## Governance shape this session

**Not a Playbook amendment session** — no [GR] rules changed.

**SIGN cycles:**

- T1 pre-code (Rigby): AGREE with 3 tweaks (execution_log_id back-pointer, split PR-A/PR-B, ship 1D unscheduled) — all folded
- A2 post-code cycle-1 (Rigby): AGREE + 2 REVISE items (`_raw_delete` + batch cap; lightweight-execute Phase 1A parity) — both folded
- A2 post-code cycle-2 (Rigby): AGREE — ship

Every SIGN routing included the mandatory zoom-out ask (per `feedback_zoom_out_ask_per_rigby_sign`). Rigby's cycle-1 zoom-out surfaced 2 real REVISE items that shipped in the amended commit before push.

**Chris D-verdicts:**
- 1 arc-open ratification via deliverable handoff (S2969 first-action = Spider Fix Plan spec, from Chris + Rigby joint work pre-session)
- 1 close ratification via terminal `ratify`

**Playbook rule adherences:**
- PLAYBOOK-6.10.9 (fold evidence admission): all SIGN attestations included concrete file+line evidence for state claims
- PLAYBOOK-7.4.4 (recycle-after-merge): `make recycle-all` executed after PR #3591 merge; will execute again after docs cascade PR merge
- `feedback_gh_pr_merge_admin_until_billing_fixed`: PR #3591 merged with `--admin`
- `feedback_local_truth_no_production`: local `make celery-recycle` treated as deploy step
- `feedback_zoom_out_ask_per_rigby_sign`: every SIGN routing included the mandatory zoom-out ask
- `feedback_verify_rigby_tool_runs_before_trusting_sign`: verified Rigby's live spider_status_tool call (2 tool_runs with concrete result payloads) before accepting her "loop closed" verdict
- `feedback_claude_directs_rigby_then_verifies`: Rigby executed the spider_status_tool verify; CC verified independently via ORM
- `feedback_session_close_three_part_summary`: close message delivered to Chris as three-part plain-English (what/how it improves/next action)

**Candidate folds for future ratification (NOT codified this session):**

1. **"Auditability primitive already exists in a different plane" pattern.** SpiderExecutionLog already recorded every run with success/error/duration. The "never_run" symptom was really a "dashboard reads the wrong table" bug. Fix could have been "make dashboard read both surfaces" (Path β) instead of "persist a second signal" (Path α, what we shipped). We shipped α because the spec was explicit + it doesn't require dashboard changes, but the pattern is worth naming: **before adding a new observability signal, check what existing primitive already carries the answer, and consider whether the fix is at the reader instead of the writer.** **Trigger count: 1** (S2969 arc surfaced it via live probe). Watch for a second before Playbook amendment.

2. **"Deliverable-as-spec first walk validates the workflow reframe."** Confirms S2968 end-of-session reframe holds in practice: Chris + Rigby produce spec → hand UUID to CC → CC executes with SIGN cycles → merges → reports. Zero terminal yes/no asks. If this pattern holds across another 2-3 arcs, worth surfacing as a first-class rule about "spec-driven session shape" vs the older "direct-instruction session shape."

---

## Session-close hygiene

- ✅ HEAD `e6dea2d52` — worker recycled after PR #3591 merge per PLAYBOOK-7.4.4 (event logged to `logs/recycle_events.jsonl`)
- ✅ All spider diagnostic tests green (30/30)
- ✅ Regression check on existing spider network tests green (3/3)
- ⏭ Session lifecycle close + wrapper pin bump: TBD as part of docs cascade
- ⏭ Docs cascade PR: this handoff + 00-START refresh + wrapper pin bump
- ⏭ Second `make recycle-all` after docs cascade merge (per PLAYBOOK-7.4.4)
