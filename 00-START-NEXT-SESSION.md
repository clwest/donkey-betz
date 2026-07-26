# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2968 CLOSED with a workflow reframe. Two code PRs shipped (#3588 PR-A v2 subprocess dispatch + #3589 PR-A schema follow-up), one code branch pushed-not-merged (`feat/s2968-pr-b-deliverable-as-spec`, local commit `1189232a6`). **The end-of-session reframe is the important artifact**: Rigby doesn't need her own coding agent inside the app. The user (Chris) works with Rigby → Rigby writes an engineering-spec Deliverable → the user hands the spec pointer to Claude Code → CC picks it up on orient → CC executes + SIGNs with Rigby + ships. Same workflow shape as tonight; the initiation direction flips (Chris→Rigby→CC instead of Chris→CC→Rigby). Full context: `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`.

**Session cost this session:** ~$0.51 (0.13 CLI probe + 0.17 in-process v2 + 0.02 v1 through worker + 0.19 v2 through worker). No further spend after Chris called timeout mid-PR-B live-verify prep.

**HEAD at close:** `f3c62fbdc` (PR #3589 merged; docs cascade PR TBD). Workers recycled twice per PLAYBOOK-7.4.4.

---

## S2969 first-action — WAIT FOR CHRIS

**Do NOT open the day with a code proposal.** The reframe says the workflow starts with Chris + Rigby, not Chris + CC. Your job at session open:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md` in full — especially §"End-of-session reframe."
4. **Report readiness in one short message and wait.** Something like: "Oriented. S2968 closed with a workflow reframe — you work with Rigby first, then hand me a spec pointer. Ready when you have one."
5. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:**

1. Read the spec: `bash tools/pa_local.sh "deliverable_tool action=get id=<UUID>"` (or read directly from ORM if faster).
2. Confirm you understand: "Got it — spec title is X, acceptance criteria are Y, out of scope is Z. Starting."
3. Execute the code per the spec's acceptance criteria.
4. Ping Rigby for SIGN cycle(s) using the pattern from S2968 (T1 pre-code SIGN with tool-verify directives + mandatory zoom-out ask; A2 post-code SIGN with live verification evidence).
5. On AGREE: commit + PR + merge with `--admin` + `make recycle-all` per PLAYBOOK-7.4.4.
6. Report back to Chris with the per-PR three-part plain-English summary (per `feedback_session_close_three_part_summary` + `feedback_per_pr_summary_signals_close_readiness`).

---

## PR-B branch decision (defer to Chris)

**Branch `feat/s2968-pr-b-deliverable-as-spec` is pushed to origin, no PR opened.** Contains ~470 LOC (deliverable-id resolution branch on `_handle_claude_code`, 10 tests, doc note). Under the reframe:

- The **`engineering_spec` deliverable_type + `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` addition** is still correct regardless of dispatch wiring — the spec IS the interchange format between Rigby and CC.
- The **`deliverable_id` schema addition + resolution branch** is architecturally fine but wired for the wrong path (subprocess dispatch). Under the reframe, `deliverable_id` should route to a queue-for-pickup that CC-orient reads, not to a Celery `claude_code_engineer_task` dispatch.

**Three options for PR-B (Chris picks):**

| Option | What it does | Cost |
|---|---|---|
| **A. Rework** | Rip out the subprocess-dispatch wiring; keep the exempt-list addition + doc note. New PR ships as "engineering_spec type + doc" only. Minimum viable version of the reframe (Chris types deliverable UUID at session open; CC reads via `deliverable_tool.get`). | ~30 min rework + tests + SIGN |
| **B. Push as draft** | Open PR-B as `[DRAFT — do not merge]` for visibility; note that dispatch wiring needs rework under reframe. Preserves work without acting. | ~2 min |
| **C. Delete** | `git push origin --delete feat/s2968-pr-b-deliverable-as-spec` — throw it away. Rebuild from scratch when needed. | ~1 min |

**Recommend A once Chris walks the new workflow once and confirms it feels right.** No urgency — the branch is safely on origin.

---

## What tonight's shipped code still earns under the reframe

**PR #3588 (v2 subprocess dispatch) — DEMOTED but still real.** Not the primary path anymore, but real infrastructure for:
- Scheduled/background dispatches (Rigby nightly evals, autonomous drift-remediation, incident response) where no human is at a terminal
- The A/B validation trail toward eventual PR-D flip is still a valid future arc IF we decide autonomous dispatch matters as a product feature

**PR #3589 (schema follow-up) — still needed.** Exposes `engine_mode` to LLM callers regardless of primary-vs-fallback status.

**Reframe implication:** the S2968 arc's remaining planned PRs (PR-C = Deliverable status write-back, PR-D = v2 default flip + v1 deletion) become **optional / deferred** rather than automatic. Reconsider after walking the new workflow.

---

## Candidate folds surfaced this session (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger:**

1. **Soft-key-vs-LLM-schema-gate.** When any param must be passed by an LLM caller, it MUST be declared in the tool schema. Soft-keys only work for internal Python callers. **Trigger count: 1** (PR #3589 was the manifestation).

2. **"We're building a duplicate of a thing we already have" pattern.** Option β caught it once (homegrown coding loop reimplementing `claude` CLI). Chris's end-of-session reframe caught it again (Rigby-side coding agent reimplementing the user's CC terminal). **Trigger count: 2 within one session.** Cross-domain (code + orchestration); may warrant a rule about "before adding a new capability, ask what already provides it in the platform's actual usage shape."

---

## Universal open sequence (unchanged)

1. `context-kit orient` — source-of-truth chain, latest handoff
2. Absorb `MEMORY.md` + `CLAUDE.md` (both auto-injected)
3. Read this `00-START-NEXT-SESSION.md` in full
4. **Session-open atomic mint check:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2969 pin minted at S2968 close cascade. If not fresh, run `python manage.py session_lifecycle close --label s2968-option-beta-reframe` first (per `feedback_session_open_atomic_mint_before_pa_dispatch`).
5. Verify `claude` CLI availability (if v2 dispatches are on the day's plan): `which claude && claude --version` (should show 2.1.114+ at `~/.local/bin/claude`)
6. Read `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md` — full context on tonight's shipped code + the reframe
7. **Wait for Chris to hand you a spec pointer via Rigby.** Do not proactively propose work.

---

## What's forbidden at S2969 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2968 new forbidden entries:**
- **Do not automatically merge PR-B** — its dispatch wiring is architecturally stale under the reframe. Chris picks Option A/B/C above before any merge.
- **Do not proactively dispatch v2 test runs at session open** — each burns ~$0.15-0.20. Only dispatch when Chris explicitly requests a v2 run.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2968 additions:**
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

## For fuller context (S2846 → S2968)

See:
- **S2968 handoff (current):** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
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
