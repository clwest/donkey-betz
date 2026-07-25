# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2967 CLOSED (three functional arcs, 10 PRs total across afternoon + evening + late-night). AFTERNOON ARC (Slice 7 tool-gap fixes, PR #3576): `workspace_tool action=update` (Ledger #22 discharge) + `claude_code_tool` auto-resolve-repo via `workspace_id → ProjectWorkspace.root_path`. EVENING ARC (safety batch, PRs #3578-#3582): Makefile openai override revert + 51-site Anthropic model ID refresh + `max_iterations` + `max_cost_usd` schema caps + persister allowlist fix. LATE-NIGHT ARC (PR-2 attempt + Option β pivot, PRs #3584-#3585 + docs #3583+cascade-amend): PR-2 context pre-injection shipped, A2 SIGN caught a real regression (T1 hit iteration cap without producing an answer on a small answer-mode task while T2 opt-out shipped in 14 iters — 10KB injected context distracted the model), Chris asked two reframing questions (are we using an actual coding model? / would Deliverable-as-spec be better than free-form prompt?), we identified that we're running a general chatbot model (Sonnet 4.6 + 5 primitive tools) as a homegrown reimplementation of what Anthropic's `claude` CLI already ships, ratified **Option β = replace homegrown engineer with subprocess dispatch to `claude` CLI + Deliverable-as-spec pattern**, reverted PR-2 as prerequisite (PR #3585), drafted S2968 arc-open doc `docs/research/platform/S2968_CLAUDE_CODE_TOOL_OPTION_BETA_ARC_OPEN.md` (Rigby T1 SIGN AGREE with 3 refinements incorporated: ship PR-A only tonight behind flag, don't assume deliverable_type='engineering_spec' passes tool allowlist without check, `claude` CLI availability + JSON schema stability = primary risk to prove BEFORE PR-B/C). **13 consecutive terminal ratifications S2957→S2967.** **S2968 first-action = PR-A: subprocess dispatch prototype behind `CLAUDE_CODE_ENGINE_MODE=v2` env flag** per arc-open doc §5.1. Both engines live in parallel; feature-flag flip after 3+ successful A/B pairs prove v2 ≥ v1 on cost + iterations + output quality.

**Pre-flight state fix (S2967 open):** 4 ProjectWorkspace rows had stale `/Users/donkeyking/development/unified-donkey-betz` root_paths — Chris moved the tree without updating the DB. Fixed via ORM at S2967 open (before the tool-gap fix that would have enabled Rigby to self-serve). All 4 rows now on the correct `/Users/donkeyking/Donkey_Betz/unified-donkey-betz` prefix.

**End-to-end proof:** post-fix `claude_code_tool` dispatch with `workspace_id=b4503364-…` returned the exact single filename that exists in `docs/governance/` (`SYSTEM_OWNER.md`) — proving the engineer ran against the real working tree, not the pre-fix `/app`-fallback that produced generic "no repo detected" no-ops.

**Governance:** Rigby T1 pre-code SIGN = 4 `repo_tool.read_file` verifications + 1 `deliverable_tool.append` for Ledger #22 + 2 REVISEs surfaced via mandatory open-ended zoom-out ask (both accepted pre-code). Chris D-verdict = joint Claude+Rigby recommendation via plain-English framing (Q1 "do we lose anything?" no / Q2 "is it more work later?" no). Rigby A2 post-code SIGN = 4 tool_run verifications + one real bug caught mid-verify (empty-string business_status regression) + patched + re-verified before AGREE.

**Golden Evals arc status:**

| Session | Phase | Ship | HEAD |
|---------|-------|------|------|
| S2954 | arc open | Tier-1 list + Day-1 scope | (arc-open doc) |
| S2955-S2962 | Tier-1 spec-authoring (8/8) | 8 canon_v1 YAMLs | `6bf8d9a81` (S2962) |
| S2963 | arc close | canon_v2 ratification (6 items) | `882626d8f` |
| S2964 | harness PR-1 (foundation) | allowlist + EvalRunContext scaffold + skeleton adapters + mgmt cmd + `GoldenEvalRun` model | `137410e86` |
| S2965 | harness PR-2a (executors + runners + --execute) | JSON Schema executor + fault-injection parser + universal runners + SIA canonicalizer + full adapter build-out + `--execute` flag + SIA end-to-end dogfood | `38ee09602` |
| S2966 | harness PR-2b (Rigby runners + slice 8 dogfood + AgentRouter dispatch) | 6 Rigby fabrication predicates + one_of dispatcher + 7 canonicalizers + AgentRouter.route() dispatch + marker resolver + process_pa_chat_task synchronous dispatch + SIA/Rigby/Research end-to-end dogfood | `76710a425` |
| **S2967** | **mid-session re-slate — Slice 7 tool-gap sweep** | **`workspace_tool.update` + `claude_code_tool` auto-resolve-repo (Ledger #22 discharged)** | **`acfea6972`** |
| S2968 (next) | Path A — nightly beat + drift dashboard | scheduled runs + pass-rate telemetry (S2963 arc structure) | TBD |

**PRs shipped this session (S2967):**
- u-d-b PR **#3576** — S2967 Slice 7 tool-gap fixes (+256 / -33 across 5 files).
- u-d-b PR **#TBD** — S2967 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Post-merge:** `make recycle-all` executed per PLAYBOOK-7.4.4 (workers advanced to sha=`acfea6972cd9`).

Full session context: `docs/handoffs/SESSION_2967_SLICE_7_TOOL_GAP_FIXES.md`.

---

## S2968 open sequence

**S2968 first-action = PR-A (Option β subprocess dispatch prototype)** — ratified 2026-07-25 (Chris terminal, late-night). Original S2968 first-action (Path A: nightly beat + drift dashboard) DEFERRED to S2969+ because Chris's two reframing questions during S2967 close-cascade evening surfaced that the whole `claude_code_tool` engine needs architectural replacement, not further optimization.

**PR-A (RATIFIED S2968 first-action):** Ship `execute_engineering_task_v2` behind `CLAUDE_CODE_ENGINE_MODE=v2` env flag. Subprocess dispatch to `claude` CLI (`subprocess.run(['claude', '--print', '--dangerously-skip-permissions', '--max-turns', ..., '--output-format', 'json', task])`). Parses JSON output, maps to existing envelope shape. Both engines live in parallel (v1 legacy preserved as fallback). Feature-flag default flips to v2 only after 3+ successful A/B pairs. Estimated ~2-3h + tests + A2 SIGN. Full design at `docs/research/platform/S2968_CLAUDE_CODE_TOOL_OPTION_BETA_ARC_OPEN.md`.

**PR-B (S2968 follow-on, after PR-A A/B validates):** Deliverable-as-spec — add `deliverable_id` param to `claude_code_tool` schema; handler resolves Deliverable → constructs engineer prompt "read Deliverable <UUID> via deliverable_tool.get, execute per acceptance criteria." **Pre-work: verify `deliverable_type='engineering_spec'` passes tool + schema allowlists without diagnostic-flagging (per feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic).**

**PR-C (S2968 follow-on, after PR-B):** Deliverable status write-back. Engineer marks its own Deliverable `completed`/`partial`/`blocked`/`escalated` on ship. Full audit trail across dispatches.

**PR-D (S2968 arc-close):** Flip default to v2 + delete ~600 LOC legacy engineer LLM loop + `_execute_tool` + 5 primitive tools + `CHANGE/ANSWER_SYSTEM_PROMPT` + `_infer_request_mode`.

**Deferred to S2969+ (originally S2968 candidates before Option β re-slate):**
- **Path A** — nightly beat + drift dashboard for Golden Evals. Uses `GoldenEvalRun` rows already persisting.
- **Path B** — per-slice named predicate graduation.
- **Path C** — Ledger #20 + #21 fix arc (ToolCallRecord.trace_id + PA write regression).

### Universal open sequence

1. **Live-verify S2967 fixes:**
   - `bash tools/pa_local.sh "workspace_tool action=list"` — confirm all 4 formerly-stale workspaces show `/Users/donkeyking/Donkey_Betz/unified-donkey-betz` prefix.
   - `bash tools/pa_local.sh "claude_code_tool task='ANSWER MODE: echo the current git HEAD SHA from the repo root' workspace_id=b4503364-2573-4401-9e28-61a739e0ce50 conversation_id=<S2968 pin>"` — smoke test auto-resolve-repo + follow-up wake.
2. **Live-verify S2953 drift scanner:** `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77 active).
3. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --check` — confirm gap-map headline (`100 full / 2 untested` last observed at S2963).
4. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2968 pin (retired at S2967 close cascade).
5. **Read S2967 handoff + shipped code:** `docs/handoffs/SESSION_2967_SLICE_7_TOOL_GAP_FIXES.md` + `core/services/td_handlers_agents.py:2421` (workspace_tool.update handler) + `core/services/td_handlers_codejobs.py:330` (`_handle_claude_code` workspace_id resolver) + `core/services/claude_code_engineer.py:589` (`_execute_tool(..., repo_root)`) + `core/services/claude_code_engineer.py:626` (`_resolve_repo_root()`).
6. **Read canon_v2 doc if not already loaded:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines).
7. **Verify Rigby Tool Gap Ledger:** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — **Ledger #22 discharged at S2967**; carry-forward candidates (Ledger #17 unchanged, #20 + #21 unchanged, Rigby outbound-messaging still un-logged with 2 triggers).

### S2968 scope note

**In scope for S2968 (Chris to pick path):** nightly beat + drift dashboard (Path A default) OR per-slice named predicate graduation (Path B) OR Ledger #20 + #21 fix arc (Path C).

**Out of scope for S2968:** WorkflowOrchestrationAgent wrapper key-name mismatch (F1 from S2958). Latent migration drift remediation.

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after Path A ships)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2967 close)

**S2967 additions:**
- **Claude Code auto-bind conversation_id at framework level** — Fix 3 cut from S2967; separate arc. Not urgent because `follow_up_will_fire` echo gives callers observability.

**Carry forward from S2966:**
- **Nightly beat + drift dashboard (S2968 Path A candidate).**
- **Per-slice named predicate graduation (S2968 Path B candidate).**
- **Ledger #20 + #21 fix arc (S2968 Path C candidate).**
- **Rigby outbound-messaging gap** — SECOND TRIGGER OBSERVED S2966. Log as ledger entry at S2968.

**Carry forward from S2965:**
- S2965 known limitation CLOSED S2966.

**Carry forward from S2964:**
- Latent migration drift (Narrative* / HAIDispatchLog AlterField pile).
- `claude_code_tool` stdout / duration_ms capture gap (Probe 3 caveat from S2964).
- Complex-boolean-in-canon-doc misread pattern (one trigger observed).

**Carry forward from S2963:**
- Fold P2 / S1 / U1 / P1 / V1 / U2 — all DISCHARGED as canon_v2 Items 1/2/3/4/5/6 at S2963 arc-close.

**Long-standing (carry forward):**
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## What's forbidden at S2967 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2967 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2967 additions:** see §Deferred queue above.

**Long-standing:**
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953) + Golden Evals arc (S2954-S2966) + Slice 7 tool-gap sweep (S2967) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2966)

See:
- **S2967 handoff (current):** `docs/handoffs/SESSION_2967_SLICE_7_TOOL_GAP_FIXES.md`
- **S2967 shipped code:**
  - `core/services/pa_tool_schemas.py` (workspace_tool + claude_code_tool schemas)
  - `core/services/td_handlers_agents.py:2421` (workspace_tool.update handler)
  - `core/services/td_handlers_codejobs.py:330` (`_handle_claude_code` workspace resolver)
  - `core/tasks.py:11873` (`claude_code_engineer_task` workspace_root_path kwarg)
  - `core/services/claude_code_engineer.py` (REPO_ROOT refactor + `_resolve_repo_root` + `_execute_tool(..., repo_root)`)
- **S2966 handoff:** `docs/handoffs/SESSION_2966_GOLDEN_EVALS_HARNESS_PR2B.md`
- **S2965 handoff:** `docs/handoffs/SESSION_2965_GOLDEN_EVALS_HARNESS_PR2A.md`
- **S2964 handoff:** `docs/handoffs/SESSION_2964_GOLDEN_EVALS_HARNESS_PR1.md`
- **S2963 handoff:** `docs/handoffs/SESSION_2963_GOLDEN_EVALS_ARC_CLOSE_CANON_V2.md`
- **S2963 canon_v2 ratification doc:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines)
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — **Ledger #22 DISCHARGED at S2967**.
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89` — Chat UI response-relay gap (unchanged this session)
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
