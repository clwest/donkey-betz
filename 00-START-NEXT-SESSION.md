# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2969 CLOSED. Workflow reframe validated on first walk. One code PR shipped (#3591 PR-A spider diagnostic persistence). Chris + Rigby produced spec deliverable → Chris handed UUID to CC on session open → CC executed with T1/A2×2 SIGN cycles → merged + recycled → Rigby verified via `spider_status_tool.history` → Chris ratified via terminal. Zero terminal yes/no asks during execution. Reddit + sports_injuries "never_run" symptom RESOLVED at the dashboard/tool-surface level. Root cause of 0-items outcome (network/DNS egress) surfaced as a candidate infra arc. PR-B (fix spider code) CLOSED under Rigby verdict — spider code isn't the bug. Full context: `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`.

**Session cost this session:** minimal — no v2 subprocess dispatches; only PA-tool calls to Rigby (2 T1/A2 cycles + 1 spider_status_tool verify + 1 live-verify report).

**HEAD at close:** `e6dea2d52` (PR #3591 merged; docs cascade PR TBD). Worker recycled once per PLAYBOOK-7.4.4; second recycle after docs cascade merge.

---

## S2970 first-action — WAIT FOR CHRIS (same as S2969)

The reframe held. Same open shape as S2969:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md` in full — especially §"The workflow reframe: first walk" and §"What deferred / closed under Rigby's verdict."
4. **Report readiness in one short message and wait.** Something like: "Oriented. S2969 closed — workflow reframe validated. Spider observability shipped, root cause of 0-items is worker egress (deferred to infra arc). Ready when you have a spec pointer."
5. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:**

1. Read the spec: `bash tools/pa_local.sh "deliverable_tool action=get id=<UUID>"` (or read directly from ORM if faster — surface truncates around ~8k chars).
2. Confirm you understand: "Got it — spec title is X, acceptance criteria are Y, out of scope is Z. Starting."
3. Explore the code surface + probe live state before drafting a plan (S2969 pattern: shell probe surfaced `SpiderExecutionLog` had 76 successful runs while `LegacySpiderData` had 0 — this reframed the entire fix from "spider parsing" to "auditability primitive lives in a different table").
4. Route T1 pre-code plan to Rigby with tool-verify directives + mandatory zoom-out ask.
5. Fold refinements → implement → tests → route A2 post-code SIGN with concrete file+line evidence per PLAYBOOK-6.10.9.
6. On AGREE: commit + PR + merge with `--admin` + `make recycle-all` per PLAYBOOK-7.4.4.
7. Live-verify (in-shell dispatch bypasses singleton locks; or dispatch through worker via `apply_async`).
8. Ping Rigby to verify from HER tool surface — "loop closed" is when Rigby's PA tool returns the expected result, not when CC's ORM query does.
9. Report back to Chris with the three-part plain-English summary.

---

## S2968 PR-B branch decision — STILL OPEN

**Branch `feat/s2968-pr-b-deliverable-as-spec` remains pushed to origin, no PR opened.** S2969 did not touch it. Chris now has empirical data on how the reframe works in practice; the A/B/C options from S2968 close still apply:

| Option | What it does | Cost |
|---|---|---|
| **A. Rework** | Rip out the subprocess-dispatch wiring; keep the exempt-list addition + doc note. New PR ships as "engineering_spec type + doc" only. Minimum viable version of the reframe (Chris types deliverable UUID at session open; CC reads via `deliverable_tool.get`). | ~30 min rework + tests + SIGN |
| **B. Push as draft** | Open PR-B as `[DRAFT — do not merge]` for visibility; note that dispatch wiring needs rework under reframe. Preserves work without acting. | ~2 min |
| **C. Delete** | `git push origin --delete feat/s2968-pr-b-deliverable-as-spec` — throw it away. Rebuild from scratch when needed. | ~1 min |

**S2969 datapoint:** Chris DID hand a deliverable UUID by pasting it into terminal alongside the callback conversation_id. CC picked it up via `deliverable_tool.get` (surface) + ORM (full content). Worked cleanly, zero code needed. This SUPPORTS closing PR-B to option C (delete) — the manual UUID-paste flow is fine and no exempt-list / schema plumbing is strictly required for the workflow to function. But option A (ship the exempt-list + doc note only) still has value if Rigby needs to CREATE engineering_spec deliverables that would otherwise get flagged as diagnostic.

**Recommend Chris pick between A and C at S2970 open.**

---

## S2969 candidate arc queued (Chris picks whether to open)

**Worker egress validation.** S2969 live-verify surfaced that reddit + sports_injuries + github + spotify + discord all fetch 0 items even from the worker daemon (not just Chris's local shell). Root cause is likely worker-environment DNS resolution or HTTPS egress being blocked for these hosts. Investigation would answer: which spider targets are worker-reachable? Does `make celery` inherit network egress permissions from Chris's env? Should the worker run under a network profile that whitelists spider target hosts?

**Small arc — no urgency.** If Chris cares about actual spider data (not just observability), this is the next spec Rigby should write. If Chris only cared about the "never_run" dashboard lie, that's already fixed and this can wait indefinitely.

---

## Candidate folds surfaced this session (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger:**

Carrying forward from S2968:

1. **Soft-key-vs-LLM-schema-gate.** When any param must be passed by an LLM caller, it MUST be declared in the tool schema. Soft-keys only work for internal Python callers. **Trigger count: 1** (S2968 PR #3589).

2. **"We're building a duplicate of a thing we already have" pattern.** Option β caught it once (homegrown coding loop reimplementing `claude` CLI). Chris's end-of-session reframe caught it again (Rigby-side coding agent reimplementing the user's CC terminal). **Trigger count: 2 within one session (S2968).** Cross-domain (code + orchestration).

New at S2969:

3. **"Auditability primitive already exists in a different plane" pattern.** `SpiderExecutionLog` already recorded every run with success/error/duration — the "never_run" symptom was really a dashboard-reads-wrong-table bug. Fix could have been "make dashboard read both surfaces" (Path β) instead of "persist a second signal" (Path α). We shipped α because the spec was explicit + it doesn't require dashboard changes, but the pattern is worth naming: **before adding a new observability signal, check what existing primitive already carries the answer, and consider whether the fix is at the reader instead of the writer.** **Trigger count: 1** (S2969 live probe surfaced it).

4. **"Deliverable-as-spec first walk validates the workflow reframe."** S2968 end-of-session reframe held in practice: Chris + Rigby produce spec → hand UUID to CC → CC executes with SIGN cycles → merges → reports. Zero terminal yes/no asks during execution. **Trigger count: 1** (S2969 arc). If this pattern holds across another 2-3 arcs, worth surfacing as a first-class rule about "spec-driven session shape" vs the older "direct-instruction session shape." Related but distinct from #2 above — this is about SESSION SHAPE, that one is about DUPLICATE CAPABILITY.

---

## Universal open sequence (unchanged)

1. `context-kit orient` — source-of-truth chain, latest handoff
2. Absorb `MEMORY.md` + `CLAUDE.md` (both auto-injected)
3. Read this `00-START-NEXT-SESSION.md` in full
4. **Session-open atomic mint check:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2970 pin minted at S2969 close cascade. If not fresh, run `python manage.py session_lifecycle close --label s2969-spider-diagnostic-persistence` first (per `feedback_session_open_atomic_mint_before_pa_dispatch`).
5. Verify `claude` CLI availability (if v2 dispatches are on the day's plan): `which claude && claude --version` (should show 2.1.114+ at `~/.local/bin/claude`)
6. Read `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md` — full context on tonight's shipped code + the reframe first-walk
7. **Wait for Chris to hand you a spec pointer via Rigby.** Do not proactively propose work.

---

## What's forbidden at S2970 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2968-S2969 forbidden entries:**
- **Do not automatically merge S2968 PR-B** — its dispatch wiring is architecturally stale under the reframe. Chris picks Option A/C above before any merge.
- **Do not proactively dispatch v2 test runs at session open** — each burns ~$0.15-0.20. Only dispatch when Chris explicitly requests a v2 run.
- **Do not chase spider parsing bugs for reddit / sports_injuries** — S2969 verified the code path works; the 0-items outcome is worker-egress at the environment level. Any fix belongs in a "worker egress validation" arc, not a spider-code arc.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2969 additions:**
- **Worker egress validation arc** — investigate whether the worker daemon has outbound DNS + HTTPS access to spider target hosts (`reddit.com`, `rotowire.com`, `rss.nytimes.com`, etc.). Would need to be a Rigby-authored spec Deliverable; CC picks it up.
- **Retention task Beat schedule** — `cleanup_empty_spider_runs` ships un-scheduled per Rigby T1. If empty-run rows accumulate faster than expected, add a Beat entry in `core/celery.py` (daily at 03:00 UTC is the suggested cadence but hold until we see actual accumulation rate).

**S2968 additions (unchanged):**
- **PR-C (Deliverable status write-back)** — reconsider after the reframe walk. May not be needed if pickup-queue design supplants dispatch-and-write-back.
- **PR-D (v2 default flip + v1 deletion)** — deferred until we know whether autonomous dispatch is a keeper feature.
- **Path A (nightly beat + drift dashboard for Golden Evals)** — deferred from S2968 first-action; still on the queue for whenever Chris wants it.
- **Path B (per-slice named predicate graduation)** — Golden Evals arc follow-up.
- **Path C (Ledger #20 + #21 fix arc)** — ToolCallRecord.trace_id + PA write regression.

**Long-standing (carry forward):**
- Docs restructuring arc (Chris-ratified S2800)
- Slice 5-hardening executable invariants
- Tier 2 lint promotion
- Advanced paste-UUID fallback for cluster picker
- Server-side search + pagination on `/eligible/`
- Z1/Z2/Z4 signal-dispatch UI polish
- Rank + cap + paginate follow-ups
- Per-pattern-type diversity floors
- Ledger candidates backlog
- W2 #1 / #2b / #2c pending Chris re-slate
- LLMCallLog field splits
- Bulk `workspace_budget_tool` operations
- C4/C5/C6 character-os follow-ons

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953) + Golden Evals arc (S2954-S2966) + Slice 7 tool-gap sweep (S2967) + Option β + reframe (S2968) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2969)

See:
- **S2969 handoff (current):** `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`
- **S2969 shipped code:**
  - `core/services/spider_diagnostic.py` (NEW — env-flag helpers + persist_diagnostic_row + SPIDER_REQUIRED_ENV_KEYS)
  - `core/tasks_spiders.py` (`_impl_run_spider_network` preflight + empty-run + enriched metrics at lines 436, 498-519, 534-545, 585-599; `_impl_execute_single_spider_lightweight` Phase 1A parity at lines 799-822)
  - `core/tasks.py:1527` (`cleanup_empty_spider_runs` task with `_raw_delete` + `batch_cap`)
  - `docs/topics/spider-network.md` ("Diagnostic run persistence (S2969)" section)
  - `core/tests/test_spider_diagnostic_persistence.py` (30 tests)
- **S2968 handoff (prior):** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
- **S2968 shipped code:**
  - `core/services/claude_code_engineer.py` (v2 subprocess dispatch — `execute_engineering_task_v2` at line 1428+ + helpers)
  - `core/services/pa_tool_schemas.py` (`engine_mode` schema addition on `claude_code_tool`)
  - `core/tasks.py:11873` (`claude_code_engineer_task` router: payload > env > 'v1')
  - `core/services/td_handlers_codejobs.py:330` (`engine_mode` payload soft-key passthrough — LLM callers still gated on schema)
  - `docs/topics/claude-code-engineer.md` (`Engine mode` section)
  - `core/tests/test_engineer_v2_subprocess.py` (13 tests)
- **S2968 pushed-not-merged code** (branch `feat/s2968-pr-b-deliverable-as-spec`, commit `1189232a6`):
  - `core/services/deliverable_factory.py` (+8: `'engineering_spec'` in exempt frozenset)
  - `core/services/pa_tool_schemas.py` (+21: `deliverable_id` on `claude_code_tool`)
  - `core/services/td_handlers_codejobs.py` (+121: `_handle_claude_code` deliverable_id branch)
  - `docs/topics/claude-code-engineer.md` (+20: `Deliverable-as-spec` subsection)
  - `core/tests/test_engineer_deliverable_spec.py` (NEW, 10 tests, all pass)
- **S2968 design doc:** `docs/research/platform/S2968_CLAUDE_CODE_TOOL_OPTION_BETA_ARC_OPEN.md`
- **S2967 handoff:** `docs/handoffs/SESSION_2967_SLICE_7_TOOL_GAP_FIXES.md`
- **S2966 handoff:** `docs/handoffs/SESSION_2966_GOLDEN_EVALS_HARNESS_PR2B.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — Ledger #22 DISCHARGED at S2967; no S2968 additions.
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89` — Chat UI response-relay gap (unchanged this session)
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
