# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2970 CLOSED. Workflow reframe second walk validated. Two code PRs shipped: #3593 (PR-B RSS-first fixes for reddit + sports_injuries) and #3594 (PR-B.1 flag-gated aiohttp ThreadedResolver swap unblocking PR-B live-verify). Reddit now produces 20 unique items per run (DoD ≥5 exceeded); sports_injuries produces 6 unique items (DoD ≥10 short by 4, Rigby verdict PASS-as-is due to off-season MLB/NHL thinness). Root cause of the sports_injuries baseline "never_run" symptom + PR-B initial 0-items outcome now both classified correctly: reddit's `.rss` swap works cleanly, sports_injuries' rotowire per-sport swap works, and the DNS bug that S2969 identified as "worker egress infra arc" turned out to be an aiohttp/aiodns issue Fixable in one line behind `SPIDER_USE_THREADED_DNS_RESOLVER` flag (default true). Full context: `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md`.

**Session cost this session:** minimal — no v2 subprocess dispatches; only PA-tool calls to Rigby (5 turns: T1 SIGN + ack + A2 SIGN + PR-B.1 decision + close verdict).

**HEAD at close:** `d11d7fcee` (PRs #3593 + #3594 merged; docs cascade PR TBD). Worker recycled twice per PLAYBOOK-7.4.4; third recycle after docs cascade merge.

---

## S2971 first-action — WAIT FOR CHRIS (same as S2969, S2970)

The reframe held for the second time. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md` in full — especially §"The workflow reframe: second walk" and §"Live-verify results (post-PR-B.1 merge + recycle)".
4. **Report readiness in one short message and wait.** Something like: "Oriented. S2970 closed — reframe validated for the second walk. Reddit + sports_injuries now producing real items via RSS; aiohttp DNS bug fixed one-liner behind flag. Ready when you have a spec pointer."
5. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:** follow the S2969/S2970 pattern — read spec, explore code + probe live, T1 SIGN to Rigby with zoom-out, fold, implement, A2 SIGN with file+line evidence, merge with `--admin`, `make recycle-all`, live-verify in-shell, Rigby verifies from her tool surface, report three-part summary to Chris.

---

## S2970 candidate follow-ups (Chris picks whether to open)

**sports_injuries keyword tuning (small mini-PR).** Current filter uses 31 keywords but doesn't catch return-to-play tokens ("Poised to practice", "Cleared for full practices") which are legitimate injury-availability updates. Adding 2-3 conservative keywords (`cleared for`, `activated`) would push NFL/MLB yield from 1-3 → 3-5 items each and get sports_injuries over ≥10. Rigby verdict at S2970 close: only worth doing if Chris insists on hitting ≥10 as a hard requirement; off-season MLB/NHL thinness will resolve naturally with season activity.

**S2969 candidate arc STILL OPEN:** worker egress validation — S2970 PR-B.1 root-caused the DNS piece of this (aiohttp/aiodns bug, ~5 LOC to fix behind flag). Broader worker-egress questions (HTTPS access to all spider target hosts, network policy in production, worker daemon inheriting env correctly) remain uninvestigated. Small arc if Chris cares about spider coverage beyond the 2 that S2969/S2970 addressed.

---

## S2968 PR-B branch decision — STILL OPEN

_(unchanged from S2970 open — S2970 did not touch the S2968 PR-B branch)_

**Branch `feat/s2968-pr-b-deliverable-as-spec` remains pushed to origin, no PR opened.** Chris now has TWO data points on how the reframe works (S2969 + S2970) — the manual UUID-paste flow works cleanly, no exempt-list / schema plumbing strictly required. Options A/C from S2968 close still apply.

---

## Candidate folds surfaced this session (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger unless otherwise noted:**

Carrying forward from S2969:

1. **Soft-key-vs-LLM-schema-gate.** **Trigger count: 1** (S2968 PR #3589). No new instance at S2970.

2. **"We're building a duplicate of a thing we already have" pattern.** **Trigger count: 2** (S2968). No new instance at S2970.

3. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969). No new instance at S2970.

4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 2** (S2969 + S2970). Two-trigger corpus reached. If S2971 + S2972 continue the pattern, consider promoting to a Playbook rule about spec-driven session shape.

New at S2970:

5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** PR-B's `empty_reason=fetch_failed` diagnostic (added at request of the spec) then triggered on live-verify, correctly pointing at the aiohttp/aiodns DNS bug. Observability functioning as designed — the diagnostic *is* the debugging tool. **Trigger count: 1** (S2970). Watch for a second instance.

6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** PR-B.1 folded the aiohttp resolver fix into the same session as PR-B, using a feature flag for rollback safety, instead of deferring to a "worker egress validation" arc. Rigby's rationale: "the spec/intent Chris asked for is 'make them actually fetch.' Right now they still fetch 0 in the real runtime path." **Trigger count: 1** (S2970). Watch for a second instance.

---

## Universal open sequence (unchanged)

1. `context-kit orient` — source-of-truth chain, latest handoff
2. Absorb `MEMORY.md` + `CLAUDE.md` (both auto-injected)
3. Read this `00-START-NEXT-SESSION.md` in full
4. **Session-open atomic mint check:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2971 pin minted at S2970 close cascade. If not fresh, run `python manage.py session_lifecycle close --label s2970-pr-b-rss-first` first (per `feedback_session_open_atomic_mint_before_pa_dispatch`).
5. Verify `claude` CLI availability (if v2 dispatches are on the day's plan): `which claude && claude --version` (should show 2.1.114+ at `~/.local/bin/claude`)
6. Read `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md` — full context on this session's shipped code + reframe second walk
7. **Wait for Chris to hand you a spec pointer via Rigby.** Do not proactively propose work.

---

## What's forbidden at S2971 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2968-S2970 forbidden entries:**
- **Do not automatically merge S2968 PR-B** — its dispatch wiring is architecturally stale under the reframe.
- **Do not proactively dispatch v2 test runs at session open** — each burns ~$0.15-0.20.
- **Do not chase spider parsing bugs for reddit / sports_injuries** — S2969 verified code path works; S2970 verified RSS fetches actually deliver items. Any remaining spider-code work is scope-follow-up (keyword tuning), not "the parser is broken."
- **Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env** — aiodns 3.5.0 is broken here; the flag default is `true` intentionally.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2970 additions:**
- **sports_injuries keyword tuning** — 2-3 conservative additions (`cleared for`, `activated`) to catch return-to-play tokens. Small (~10 min) if Chris insists on ≥10.
- **Worker egress validation arc (broader)** — DNS piece is fixed in S2970; broader HTTPS/network/env questions remain.

**S2969 additions (unchanged):**
- **Retention task Beat schedule** — `cleanup_empty_spider_runs` ships un-scheduled per Rigby T1. Add Beat entry if accumulation exceeds expected rate.

**S2968 additions (unchanged):**
- PR-C (Deliverable status write-back), PR-D (v2 default flip + v1 deletion), Path A (nightly beat + drift dashboard), Path B (per-slice named predicate graduation), Path C (Ledger #20 + #21 fix arc).

**Long-standing (carry forward):** Docs restructuring arc, Slice 5-hardening executable invariants, Tier 2 lint promotion, Advanced paste-UUID fallback for cluster picker, Server-side search + pagination on `/eligible/`, Z1/Z2/Z4 signal-dispatch UI polish, Rank + cap + paginate follow-ups, Per-pattern-type diversity floors, Ledger candidates backlog, W2 #1 / #2b / #2c pending Chris re-slate, LLMCallLog field splits, Bulk `workspace_budget_tool` operations, C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** S2970 was net-new engineering (RSS-first + DNS fix), not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2970)

See:
- **S2970 handoff (current):** `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md`
- **S2970 shipped code:**
  - PR-B (#3593): `ai_core/spiders/real_data_collector.py` (URL swaps + injury filter + fetch_stats), `core/services/spider_diagnostic.py` (`EMPTY_REASON_FETCH_FAILED` + `derive_empty_reason` + extended `build_empty_run_diagnostic`), `core/tasks_spiders.py` (fetch_stats threading in both runner paths), `core/tests/test_spider_rss_first.py` (23 tests)
  - PR-B.1 (#3594): `ai_core/spiders/real_data_collector.py` (`SPIDER_USE_THREADED_DNS_RESOLVER` flag + `_build_client_session_kwargs`), `core/tests/test_spider_rss_first.py` (5 tests)
- **S2969 handoff (prior):** `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`
- **S2968 handoff:** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
- **S2967 handoff:** `docs/handoffs/SESSION_2967_SLICE_7_TOOL_GAP_FIXES.md`
- **S2966 handoff:** `docs/handoffs/SESSION_2966_GOLDEN_EVALS_HARNESS_PR2B.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89`
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
