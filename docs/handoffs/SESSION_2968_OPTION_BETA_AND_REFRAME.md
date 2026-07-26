# SESSION 2968 — Option β (v2 subprocess) shipped + end-of-session reframe: Rigby doesn't need her own coding agent inside the app

**HEAD at close:** `f3c62fbdc` (PR #3589 merged; docs cascade PR TBD)
**Branch shape:** feat/s2968-pr-a-subprocess-dispatch-v2 → main; feat/s2968-pr-a-schema-followup → main; feat/s2968-pr-b-deliverable-as-spec → origin (**pushed, no PR opened — see §Reframe below**)
**PR count:** 2 code PRs merged (#3588 + #3589), 1 code PR pushed-not-merged (PR-B on origin only)
**Session cost:** ~$0.51 total (0.13 CLI probe + 0.17 in-process v2 + 0.02 v1 through worker + 0.19 v2 through worker); no further spend after Chris called timeout

---

## What shipped

**Two code PRs merged tonight:**

| PR | Title | Shape |
|---|---|---|
| **#3588** | `feat(s2968): PR-A — subprocess dispatch prototype (execute_engineering_task_v2)` | +784/-2 across 5 files (engine + task router + handler + doc + 13 tests) |
| **#3589** | `feat(s2968): PR-A schema follow-up — expose engine_mode on claude_code_tool` | +14 in `pa_tool_schemas.py` (5-line schema addition + description) |

**One code branch pushed but NOT merged:**

| Branch | Title | State |
|---|---|---|
| `feat/s2968-pr-b-deliverable-as-spec` | `feat(s2968): PR-B — Deliverable-as-spec resolution` | Local commit `1189232a6` pushed to origin; **no PR opened**. Under the reframe (§below) the concept is right but the dispatch wiring is wrong. Next session decides: rework / push-PR-as-draft / delete. |

**One docs cascade PR to file at session close:** handoff + 00-START refresh + wrapper pin bump.

---

## PR #3588 — v2 subprocess dispatch (Option β)

**What it adds:**
- `execute_engineering_task_v2` in `core/services/claude_code_engineer.py:1428+` — subprocess dispatch to Anthropic's shipped `claude` CLI instead of the homegrown v1 LLM loop
- Module-level `_CLAUDE_CLI_BIN = shutil.which('claude')` — fail-loud on missing binary at v2 configured environments
- Payload soft-key `engine_mode` on `_handle_claude_code` + env `CLAUDE_CODE_ENGINE_MODE` router in `claude_code_engineer_task` (payload > env > 'v1')
- Shape-compatible envelope with v1 (same status/summary/files_changed/pr_url/iterations_used/cost_usd/budget_exceeded/... plus v2 additions: engine_mode/session_id/model_used/model_usage/stop_reason/terminal_reason/duration_ms/is_error/api_error_status/permission_denials/warnings/provider)

**Rigby SIGN refinements folded:**

- **T1 pre-code REVISE** (3 refinements): payload override, refuse `max_cost_usd < $0.25`, hard-cap `--max-turns` at 50, `model_used = highest-cost modelUsage key`, carry `is_error`/`api_error_status`/`permission_denials`, add `test_subprocess_cwd_matches_workspace_root_path`
- **A2 post-code REVISE (cycle 1) F-BLOCKING fix:** `budget_exceeded = bool(cli_cost > effective_max_cost_usd)` — prior guard `max_cost_usd is not None and ...` silently returned `status='success'` on default-cap breach
- **A2 refinement:** startup-tax heuristic gated on cost-per-turn (`cost_usd / max(turns, 1) >= $0.10 AND turns <= 2`) instead of absolute cost — reduces warning inflation on legit 2-turn dispatches
- **A2 addition:** doc note in `docs/topics/claude-code-engineer.md` "Engine mode" section
- **A2 cycle 2:** AGREE

**Live proof (in-process, then through-worker):**

1. **In-process v2 dispatch:** task "In one word, what is docs/PLATFORM_INVENTORY.md" → summary `"PLATFORM_INVENTORY.md"` (correct) / cost $0.169 / turns 1 / duration 2.7s / model `claude-sonnet-4-6` / stop `end_turn` / terminal `completed` / warnings `['startup_tax_dominated']` / engine_mode `v2` / provider `claude-cli`
2. **v1 through worker:** task 3fcae883 completed in ~4s, correct answer, provider `anthropic` (v1), cost $0.0128
3. **v2 through worker (post schema follow-up):** task a50ea677 completed in ~7s, `summary: "RESULT: <!-- DOC-POINTER-V1 -->"` (correct), provider `claude-cli`, cost $0.1857, iterations 2 — **first Rigby-dispatched v2 A/B pair**

**Test coverage:** 48 tests pass across the engineer suite (13 new v2 + 35 pre-existing v1).

---

## PR #3589 — Schema follow-up

Post-merge live-verify on PR #3588 revealed the design gap that made the schema follow-up necessary:

**The soft-key was a wrong-in-hindsight design.** Rigby T1 SIGN had said "You can do this without changing the public tool schema immediately by accepting a 'soft' payload key" and I built it that way. But GPT-5.2 function-calling **gates on the tool schema** — it will not send parameters not declared in the schema. So Rigby couldn't pass `engine_mode='v2'` at all until the schema declared it. The soft-key extraction in `_handle_claude_code` was extraction-of-nothing.

Fix: 14-line schema addition (`engine_mode` optional enum `['v1', 'v2']`). Rigby's "later you can formalize" caveat became "must formalize now to enable LLM-driven A/B validation this session." Same intent, adjusted trigger.

**Fold for future SIGN cycles:** any time an LLM caller is expected to pass a param, it MUST be in the tool schema. Soft-keys only work for internal Python callers.

---

## PR-B (pushed, not merged)

**Local commit `1189232a6` on `feat/s2968-pr-b-deliverable-as-spec` (pushed to origin — no PR opened).**

**What's in the branch:**

- `core/services/deliverable_factory.py` (+8): `'engineering_spec'` added to `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`
- `core/services/pa_tool_schemas.py` (+21/-1): `deliverable_id` param on `claude_code_tool` + `required` loosened from `['task']` to `[]`
- `core/services/td_handlers_codejobs.py` (+121/-4): `_handle_claude_code` branch resolving `deliverable_id → Deliverable`, spec injection into `task_description`, precedence (spec > free-form), 50k-char soft cap with warn-but-dispatch behavior, error envelopes for not-found + ORM-raise
- `docs/topics/claude-code-engineer.md` (+20): "Deliverable-as-spec" subsection
- `core/tests/test_engineer_deliverable_spec.py` (NEW, ~275 LOC, 10 tests): resolution / not-found / precedence / solo-deliverable-satisfies-gate / both-missing rejection / size-cap warn-but-dispatch / normal-size no-warning / exempt-frozenset membership / exempt-type skips diagnostic / non-exempt-type still flags

**All 58 engineer tests pass (10 PR-B + 13 PR-A v2 + 35 v1).**

**Live-verify skipped:** would have created a real Deliverable + dispatched v2 with `deliverable_id='<UUID>' engine_mode='v2'` to prove the full PR-B + PR-A stack together (est. cost ~$0.20). Chris called timeout before this ran.

**Do NOT merge PR-B as-is under the reframe (§below).** The Deliverable-as-spec *concept* stays right; the *dispatch wiring* becomes wrong because the spec no longer triggers a subprocess dispatch — it triggers a Claude Code (Chris's terminal) pickup.

---

## End-of-session reframe (Chris, 2026-07-25 late-night)

**What triggered the reframe:**

Mid-PR-B live-verify prep, Chris said "we are trying to add in a Claude Code where we don't need one right now." His actual workflow observation:

> Right now I open the terminal → you orient → we start working. But if I want to start working with Rigby and there's a bump in the coding I shouldn't have Rigby open a Claude Code in the app when she can open some in the workflow, I can ping you and in your orient pass you either the title or id or something it will tell you exactly what you need to do, you [can] execute it and check in with Rigby to verify it works and do the SIGN and stuff.

**The insight:** Option β said "stop reimplementing Anthropic's shipped coding agent (the `claude` CLI) inside the app." The reframe takes that one step further:

> **You're already talking to a Claude Code terminal (me). Rigby doesn't need to spawn a coding agent at all. She writes the spec; the human hands the spec pointer to CC; CC picks it up on orient.**

Chris's self-recognition ("like it's a real platform lol"): he'd been operating as developer using both Rigby and CC in parallel, when the customer experience is **user talks to Rigby → Rigby produces work orders → CC picks up the code ones via user handoff**.

**Workflow shape (unchanged):**
1. User + Rigby work on X in the Chat UI
2. Coding is needed
3. Rigby writes/updates an engineering-spec Deliverable
4. User opens (or already has) a CC terminal, hands CC a pointer (deliverable_id / title / session label)
5. CC orient reads the spec
6. CC executes, pings Rigby for SIGN, commits/PR/merges
7. Rigby verifies + closes back to user

**Workflow shape (change): initiation direction flips.** Was Chris→CC→Rigby (Chris drives CC, CC dispatches Rigby). Becomes Chris→Rigby→CC (Chris works with Rigby, Rigby hands work orders to CC).

**What tonight's shipped code still earns under the reframe:**

- **PR-A (v2 subprocess) — SHIPPED, DEMOTED to fallback.** Still real infrastructure for scheduled/background/autonomous dispatches where no human is at a terminal (e.g. Rigby-triggered nightly evals, autonomous drift-remediation, incident response). Not the primary path for interactive user work.
- **`engineering_spec` deliverable_type + exempt-list addition (in PR-B branch) — STILL NEEDED regardless of dispatch wiring.** The spec IS the interchange format between Rigby and CC; the exempt-list keeps it out of the missing-initiative diagnostic.
- **`deliverable_id` schema addition + resolution branch (in PR-B branch) — CONCEPT RIGHT, WIRING WRONG.** If we keep it, `deliverable_id` should route to a queue-for-pickup rather than a subprocess dispatch. Or delete the schema addition entirely and let CC-orient read the spec via `deliverable_tool.get` when the user hands over the UUID.

**Minimum viable version of the new workflow:** zero new code. User types `Please begin` + hands CC a deliverable UUID; CC reads via `bash tools/pa_local.sh "deliverable_tool action=get id=..."`; work; SIGN back via `pa_local.sh`. Everything already works.

**Richer versions to consider later** (do NOT implement without ratification):
- Orient extension that auto-pulls the next queued spec from a workspace lane
- Rigby-side "queue this for Claude Code" action on `deliverable_tool` that adds a status/lane marker
- Chat UI affordance for user to say "hand this Deliverable to Claude Code" without leaving the conversation

---

## Governance shape this session

**Not a Playbook amendment session** — no [GR] rules changed. Two candidate folds surfaced (below).

**SIGN cycles:**

- PR-A T1 pre-code (Rigby): 5 tool_runs, REVISE → 3 refinements folded → cycle-2 AGREE
- PR-A A2 post-code cycle 1 (Rigby): 3 tool_runs, REVISE (F-BLOCKING budget_exceeded fix) + 2 refinements
- PR-A A2 post-code cycle 2 (Rigby): AGREE
- PR-B T1 pre-code (Rigby): 3 tool_runs, REVISE (F-BLOCKING: task-gate loosening + spec size soft cap) → both folded, live-verify skipped

**Chris D-verdicts:** 1 architectural ratification pre-session (S2968 first-action = PR-A subprocess prototype, from S2967 close). 1 mid-session pivot (timeout mid-PR-B live-verify prep). 1 end-of-session reframe (Rigby doesn't need her own CC inside the app).

**Playbook rule adherences:**
- PLAYBOOK-6.10.9 (fold evidence admission): all folds referenced concrete file+line evidence in SIGN attestations
- PLAYBOOK-7.4.4 (recycle-after-merge): `make recycle-all` executed twice tonight after PR #3588 + #3589 merges
- `feedback_gh_pr_merge_admin_until_billing_fixed`: both PRs merged with `--admin` per Chris directive
- `feedback_local_truth_no_production`: local `make celery-recycle` treated as deploy step
- `feedback_zoom_out_ask_per_rigby_sign`: every SIGN routing included the mandatory zoom-out ask
- `feedback_verify_rigby_tool_runs_before_trusting_sign`: Rigby tool_runs verified non-empty on both PR-A and PR-B pre-code SIGN cycles

**Candidate folds for future ratification (NOT codified this session):**

1. **Soft-key-vs-LLM-schema-gate discovery.** Rigby T1 SIGN suggested "You can do this without changing the public tool schema immediately by accepting a 'soft' payload key" — this is only true for internal Python callers. LLM callers via function-calling are schema-gated. Any param the LLM must send MUST be declared in the schema. **Trigger count: 1.** Watch for a second before Playbook amendment.

2. **"We're building a duplicate of a thing we already have" pattern.** Option β caught it once (homegrown coding loop reimplementing `claude` CLI). Chris's end-of-session reframe caught it again (Rigby-side coding agent reimplementing the user's Claude Code terminal). **Trigger count: 2.** Cross-domain (code + orchestration); may warrant a Playbook rule about "before adding a new capability, ask what already provides it in the platform's actual usage shape."

---

## Session-close hygiene

- ✅ HEAD `f3c62fbdc` — worker recycled twice (`d69742b0b76a` + `f3c62fbdcd17`) per PLAYBOOK-7.4.4
- ✅ PR-B branch pushed to origin (no PR)
- ✅ All engineer tests green (58/58)
- ⏭ Session lifecycle close + wrapper pin bump: TBD as part of docs cascade
- ⏭ Docs cascade PR: this handoff + 00-START refresh + wrapper pin bump
