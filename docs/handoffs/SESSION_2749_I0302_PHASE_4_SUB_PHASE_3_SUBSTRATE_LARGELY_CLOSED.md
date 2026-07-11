# Session 2749 — I-0302 Phase 4 Sub-phase 3 — 8 PRs, 4 of 6 substrates CLOSED

**Session:** 2749
**Date:** 2026-07-10 (continuous with S2748 close)
**Session type:** Engineering-execution arc — Sub-phase 3 opening moves + Rigby stall post-mortem
**System Owner directive at open:** "continue sub-phase 3"
**System Owner directive at close:** merge #3123 + write S2749 handoff
**PA conversation pin (arc):** `pa-e71c011bfa3d4124` (S2749 pin — minted at session open after retiring `pa-59d27abadeed4411`; label `ios-arc-open-I0302-P4-S2749`; still active at close)
**Preceding arc:** SESSION_2748 handoff (I-0302 Phase 4 Sub-phases 0/1/2 COMPLETE + §5.1.b 5-site hotfix + §14 threshold codification)

---

## §1 Delivery ledger

**8 PRs merged to main this session.** Sub-phase 3 opened with §14 codification per Rigby SIGN and closed 4 of the 6 substrate slots. Two Sub-phase 3 substrates remain open at session close (deferred-surface coverage-gap report + VIP-scope carve-out on `get_deliverable`).

| # | PR | Substrate / Class | HEAD after merge |
|---|---|---|---|
| 1 | [#3116](https://github.com/clwest/donkey-betz-platform/pull/3116) | §14 AST conformance harness — report-only + I-030204 spec doc (Rigby stall fallback path 2) | `f586a2cf` |
| 2 | [#3117](https://github.com/clwest/donkey-betz-platform/pull/3117) | §14 batch-fix — 9 Http404-swallow sites across 3 view files | `40f2bffc` |
| 3 | [#3118](https://github.com/clwest/donkey-betz-platform/pull/3118) | §14 enforcement flip — `ENFORCE_HTTP404_SWALLOW = True` | `f1cf8950` |
| 4 | [#3119](https://github.com/clwest/donkey-betz-platform/pull/3119) | Rigby gpt-5.2 stall post-mortem fix — provider fallback + response body capture on stall | `b91c10d1` |
| 5 | [#3120](https://github.com/clwest/donkey-betz-platform/pull/3120) | Endpoint sentinels — report-only harness (28 cockpit sentinels, **23 posture failures surfaced**) | `5f789519` |
| 6 | [#3121](https://github.com/clwest/donkey-betz-platform/pull/3121) | Sentinel batch-fix — 23 `@superuser_required` additions in `views_diagnostics.py` | `3eeac558` |
| 7 | [#3122](https://github.com/clwest/donkey-betz-platform/pull/3122) | Sentinel enforcement flip — `ENFORCE_SENTINEL_POSTURE = True` | `1a3456bd` |
| 8 | [#3123](https://github.com/clwest/donkey-betz-platform/pull/3123) | Intentional-immutability contract — 48 new matrix cells for Initiative + ChatConversation | `ae1321ba` |

**Cumulative site-level guardrail count shipped this session:**
- **14 code fixes** — 9 Http404-swallow patches (`except Http404: raise`) + 23 `@superuser_required` additions - 18 = **32 fixes** (fresh count: 9 in #3117 + 23 in #3121 = 32)
- **48 new matrix cells** — Initiative + ChatConversation intentional-immutability
- **2 test harnesses** — AST conformance (report + enforce) + endpoint sentinels (report + enforce)
- **1 design spec** — `I-030204_ast_conformance_rule_spec.md` (path 2 Claude drafts + Chris D-verdict)
- **1 memory rule** — `feedback_gpt5_stalls_on_multifold_design_prompts.md`

---

## §2 Substrate arc closes

Three three-PR substrate arcs shipped end-to-end this session, mirroring the same report-only → batch-fix → enforcement-flip pattern:

### §2.1 §14 AST codification substrate — CLOSED

Reference: `docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md`.

- **#3116 (report-only)** — `tests/security/test_i0302_p4_ast_conformance.py`. Scans 212 view files across the allowlist glob. 6-fold rule spec (violation predicate, false-positive avoidance, `get_object_or_404` detection, path allowlist, report format, enforcing-mode signal). 9 violations discovered across 3 files. Design-intent validation: predicted 6th `export_deliverable` site → flagged ✅; 5 fixed §5.1.b sites correctly NOT flagged ✅.
- **#3117 (batch-fix)** — 2-line `except Http404: raise` insertion per site. Sites fixed: `save_deliverable`, `export_deliverable`, `project_agents`, `agent_timeline`, `rate_contribution`, `mark_contribution_selected`, `toggle_project_learning`, `get_project_learning_status`, `trigger_project_learning`. Import added to `views_agent_tracking.py` and `views_projects_api.py`. Verified 0 violations post-fix.
- **#3118 (enforcement flip)** — `ENFORCE_HTTP404_SWALLOW = False → True`. 3/3 tests pass at merged HEAD, 0 violations. Rollback = one-line revert; report JSON still emitted.

### §2.2 Endpoint sentinels substrate — CLOSED

Reference: `tests/security/test_i0302_p4_endpoint_sentinels.py` + I-030203 §1.2 + §7.

- **#3120 (report-only)** — 28 hand-picked cockpit ops sentinels proposed by Rigby via `pa-e71c011bfa3d4124`. Invariant: `anon → 401 / user_a → 403 / user_b → 403 / superuser → NOT 401/403`. First run: **23 of 28 sentinels FAIL** across 3 status classes (200 direct-leak, 400 endpoint-body-ran-then-bailed, 404 agent-lookup). Report at `test_reports/i0302_p4_endpoint_sentinels.json`.
- **#3121 (batch-fix)** — 23 `@superuser_required` additions in `core/views_diagnostics.py`. **Ironic finding for the record:** the module docstring at `views_diagnostics.py:5-12` explicitly claimed "every endpoint in this file is now uniformly gated with @superuser_required" — the sentinel proved that claim wrong at 23 sites. Invariant was known but never test-enforced until Sub-phase 3.
- **#3122 (enforcement flip)** — `ENFORCE_SENTINEL_POSTURE = False → True`. 112/112 checks pass at merged HEAD. Rollback = one-line revert; report JSON still emitted.

### §2.3 Intentional-immutability contract — CLOSED

Reference: `tests/security/test_i0302_p4_matrix_harness.py` §7 (new appended classes) + I-030203 §7 close criteria update.

- **#3123** — 48 new matrix cells asserting `PUT/PATCH/DELETE` against Initiative + ChatConversation LIST + DETAIL endpoints returns `{401, 403, 404, 405}`. 4 roles per cell. Formalizes the S2748 endpoint-discovery finding that Initiative + ChatConversation have no user-facing CRUD UPDATE/DELETE endpoints — Chris D-verdict at S2748 close ("treat as intentional immutability") was the ratification input.
  - Assertion posture is deliberately weaker than the sentinel invariant — the point is "no mutation handler exists to reach," not role-scoped rejection.
  - Assertion width includes 401 and 403 alongside the S2748 handoff's 405/404 spec because middleware auth or DRF `@api_view(['GET'])` role check can fire before method-check reaches the route handler.

### §2.4 Rigby gpt-5.2 stall post-mortem fix — CLOSED

Reference: `feedback_gpt5_stalls_on_multifold_design_prompts.md` + `core/services/unified_pa_entrypoint.py:1979-2016` + `core/models_llm_routing.py` migration 0383.

- **#3119** — Two-part fix + memory rule:
  1. **Provider fallback on stall** in `unified_pa_entrypoint.py`. Before returning the generic "I ran into an issue processing that request" error, try one Anthropic Claude call via `enforce_real_ai(use_claude=True)`. Only fires on the path that would otherwise return the generic error — strictly better than pre-2749 behavior.
  2. **Response body capture on stall** — `LLMCallLog.response_preview` TextField, populated with first 500 chars of the LLM's actual response ONLY when `success=True` but `completion_tokens < 100` (the stall condition). Removes the "success + tiny completion + no visible error" diagnostic blind spot.
  3. **Memory rule** `feedback_gpt5_stalls_on_multifold_design_prompts.md` — workflow guidance: prefer single-flat prompts over F1..F6 numbered-fold scaffolding when routing pure-text design asks through Rigby (gpt-5.2 stalls on multi-fold structural asks).

**IMPORTANT:** the fix is in `main` but the RUNNING PA celery worker still has the old code loaded. Rigby routing this session hit pre-fix behavior on multi-fold prompts. To activate the fix, bounce the PA worker (see §5 open items).

---

## §3 The Rigby stall diagnosis (fold-out)

Root cause of the S2749-open jam: **gpt-5.2 stalls on multi-fold structural design prompts.**

**Evidence from `LLMCallLog`:**
- 8 iterations per stall with tiny 50-150-token completions
- Prompt tokens grew 47k → 65k across iterations (context accumulating each turn)
- `success=True` on every underlying call — no OpenAI-side error
- Bare pings returned 700-1000-token completions cleanly

**Failure path:** `core/services/unified_pa_entrypoint.py:1968-1982` (Sessions 1043 / 1056 / 1063 / 1065 / 1079 evolution). When gpt-5.2 returns degenerate/empty text without tool calls for 2 iterations (initial + Session 1079 retry), the PA loop returns the generic error. Root cause of the stalls themselves: gpt-5.2 has a model-specific weakness on multi-fold structural design prompts (F1..F6 scaffolds) — it keeps trying to figure out "which tool do I call?" instead of just answering with text, accumulating context until giving up.

**Fallback path taken at S2749 open** (path 2 per `feedback_rigby_sign_worker_instability_recovery.md`): Claude drafted the §14 AST rule spec (6 folds) + Chris D-verdict "ratify all" → shipped. **This is why #3116 landed with Claude-authored design content rather than Rigby's.** The provenance is documented in `I-030204_ast_conformance_rule_spec.md` §6.

**#3119 makes future path 2 fallbacks unnecessary** for this specific stall pattern — Anthropic Claude handles multi-fold structural prompts cleanly, so the provider swap in the retry chain will produce a substantive response instead of a generic error.

---

## §4 System Owner directives resolved

Explicit Chris D-verdicts this session:

| Directive | Context | Outcome |
|---|---|---|
| "continue sub-phase 3" | Session open | Sub-phase 3 opened per I-030203 §6 + Rigby final §14 SIGN |
| "go with 1" (path 1 recovery) | Rigby AST-content jam | Retire+create_fresh pin — 2 fresh-pin jams triggered path 2 fallback |
| "go with path 2" | After path 1 exhausted | Claude drafts spec + Chris D-verdict → PR #3116 shipped |
| "ratify all, ship report-only PR, one bundled batch-fix PR" | §14 spec ratification | PRs #3116/#3117/#3118 shipped as three-PR arc |
| "merge them and prep the enforcement flip" | §14 arc close | PRs #3116 + #3117 merged; #3118 prepped and merged |
| "go with 1 and 2, add 4 as memory rule" | Rigby stall fix scope | PR #3119 shipped with provider fallback + response body capture + memory rule |
| "merge 3119 and open endpoint sentinels" | Substrate sequencing | PR #3120 opened after route-to-Rigby endpoint discovery |
| "merge 3120 and open the batch-fix" | Sentinel arc | PR #3121 opened with 23 `@superuser_required` additions |
| "merge 3121 and open the enforcement flip" | Sentinel arc close | PR #3122 opened and merged |
| "merge 3122 and open intentional-immutability contract" | Substrate sequencing | PR #3123 opened with 48 new matrix cells |
| "merge 3123 and write the handoff" | Session close | This handoff |

---

## §5 What's next (Sub-phase 3 continuation)

Per I-030203 §6 + §6.a, two Sub-phase 3 substrates remain:

### §5.1 Deferred-surface coverage-gap report (I-030203 §4.2)

- JSON emit at `test_reports/i0302_p4_coverage_gaps.json`
- Coverage: §5.3.b (C2 ~126 sites) + §5.1.a (D non-view) + §5.5.a (Document WebSocket)
- Cheap posture probes (HEAD/OPTIONS or minimal auth check) where feasible
- Same three-PR arc pattern? Or one-PR if no gaps surface? To be determined by the discovery-first approach used for the sentinels.

### §5.2 VIP-scope carve-out coverage extension on `get_deliverable`

- Extend the `tenant_boundary.py` fixture with a VIP membership row (`VIPScope` or equivalent)
- Add matrix cell for the VIP-workspace read path currently deferred in Sub-phase 2 GET-item cell
- Chris-ratified VIP feature preservation from §5.1.b 5th-site fix (see `views_deliverables.py:191-206`)

### §5.3 Sub-phase 3 research inputs (bounded docs-only passes; per I-030203 §6.a)

Still open — not yet run this session:
- AgentExecution mutation semantics — confirm no user-facing UPDATE/DELETE
- Document `user` vs `owner` field question (`views_rag_embeddings.py:470/836` uses `user=user` on a model whose canonical FK is `owner`)
- CREATE-parent-binding endpoint map across the 5 canonical models
- AGGREGATE endpoint inventory (extends §3.8 canonical JSON path table)
- Non-canonical model follow-on scope decision (`LegalDocument`, `LitigationDocument`, `ReviewDocument`)

### §5.4 Open runtime action items at session close

1. **PA celery worker bounce.** #3119 landed in `main` but the running worker still has old code. To activate the provider-fallback + response-preview features, bounce the PA worker (`OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` + restart per `Makefile`). Deferred to Chris; not urgent — the pre-2749 behavior remains functional.
2. **P0 cost-threshold observation check-in.** Still deferred per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md`. Actionable on any 2026-07-11+ session — S2749 is a 2026-07-10 session (continuous with S2748), so still deferred.

---

## §6 Governance provenance

### §6.1 Substrate / ledger amendments landed this session

- I-030204 (new) — AST conformance rule spec (path 2 fallback)
- I-030201 §5.1.b tail — §14 codification-execution block (9 batch-fix sites documented)
- I-030203 §7 — close criteria updated with Sub-phase 3 substrate PR refs
- I-030203 §8 — chain of custody updated with S2749 substrate ledger

### §6.2 Rigby SIGN cadence

Per Chris "light SIGN per PR" directive at S2748 open. This session's SIGN cadence was interrupted twice:

- **S2749 open — §14 AST rule ask jammed 5x** (3 asks on original pin `pa-59d27abadeed4411`, 2 asks on fresh pin `pa-e71c011bfa3d4124` after retire+create_fresh). Root cause diagnosed as gpt-5.2 stall (see §3). Chris D-verdict "path 2" → Claude drafts + Chris D-verdict + Rigby post-merge verifier-loop.
- **Sentinel endpoint discovery** — worked cleanly. Rigby returned 30 grounded candidates with `repo_tool` verification against HEAD. First truly Rigby-authored contribution since the stall pattern surfaced.
- **All 8 PRs merged with Chris D-verdict + Claude verifier-loop.** Rigby post-merge behavioral-verification still owed on:
  - §14 harness at HEAD (verify JSON report shape matches spec §3.5)
  - Sentinel harness at HEAD (verify 112/112 pass matches sentinel batch-fix evidence)
  - Immutability cells at HEAD (verify 48/48 pass matches the S2748 D-verdict language)

### §6.3 Session pin lifecycle

- **Retired at session open:** `pa-59d27abadeed4411` (S2748 arc pin — retired after 3 consecutive AST-content jams)
- **Minted at session open:** `pa-e71c011bfa3d4124` (label `ios-arc-open-I0302-P4-S2749`)
- **Active at session close:** `pa-e71c011bfa3d4124` — carry-forward to S2750 recommended for Sub-phase 3 continuation. Do NOT retire at S2750 open unless Chris explicitly changes arc scope.

### §6.4 Playbook rule alignment

- PLAYBOOK-6.10.6 (verify-substrate-before-implement) — applied: the report-only harness pattern verified the invariant class before the batch-fix landed. Same shape twice (#3116/#3120 → discovery-only → then #3117/#3121 fix).
- PLAYBOOK-6.6.14 (design-prep discipline) — applied: `I-030204` spec doc codified the AST rule design before code landed.
- §14 two-triggers-plus rule — extended: the S2748 §5.1.b `views_deliverables.py` 5-site tally + S2749 batch-fix's discovery of 9 additional sites across 3 files (`views_agent_tracking.py` × 4, `views_projects_api.py` × 3, `views_deliverables.py` × 2 missed) shows the Http404-swallow class was even more widespread than S2748 close estimated. The AST harness now enforces closure.

---

## §7 Memory candidates (for future codification)

Session surfaced patterns that may become memory rules with more corroboration:

- **Documentation invariants without test enforcement rot silently.** The `views_diagnostics.py` module docstring claimed "every endpoint in this file is now uniformly gated with @superuser_required" — 23 endpoints proved that claim wrong. Watch for a 2nd instance of "docstring says invariant holds but no test enforces it" before codifying as a playbook rule.
- **Discovery-first-then-batch-fix arc pattern (three-PR shape).** Applied twice this session cleanly: §14 codification (#3116/#3117/#3118) and endpoint sentinels (#3120/#3121/#3122). If this repeats a third time (e.g., during Task #8 coverage-gap report), codify as a Sub-phase-3-close playbook rule.
- **Rigby stall = model choice signal.** #3119's fix means Anthropic Claude is now the fallback provider for multi-fold structural asks. If future sessions still hit gpt-5.2 stalls even with the fallback active, consider a fully model-swap for "design-proposal" task type at the PA-routing layer (Path 3 from S2749 open analysis).

---

## §8 Repository state at close

| Field | Value |
|---|---|
| Branch | `main` (this handoff PR merges to `main` on approval) |
| HEAD | `ae1321ba` (PR #3123 merged; intentional-immutability contract) |
| Playbook version | v0.4.1 (unchanged) |
| Playbook rule count | 196 (unchanged) |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-e71c011bfa3d4124` (active — carry-forward to S2750) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-e71c011bfa3d4124` (rotated at S2749 open) |
| Live infra state | Same as S2748 close (cost threshold monitor mode $500/mo, observation period accumulating) |
| RUR arc state | I-0301 CLOSED · I-0302 Phases 1-3 CLOSED · Phase 4 Sub-phases 0/1/2 CLOSED · Phase 4 Sub-phase 3 — 4 of 6 substrates CLOSED (§14 AST, endpoint sentinels, intentional-immutability, Rigby stall fix); 2 remain OPEN (coverage-gap report, VIP-scope carve-out) · Phase 4 close pending · Phase 5 (arc close) not yet opened · I-0303 not yet opened · RUR-C1 parent OPEN |

**End of Session 2749 handoff. S2750 opens on Sub-phase 3 continuation per I-030203 §6 + §6.a — coverage-gap report + VIP-scope carve-out are the two remaining substrates before Phase 4 close criteria (§7) are fully met.**
