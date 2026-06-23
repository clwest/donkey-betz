# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars. Current pinned conversation: `pa-a60842917d36` (spun mid-Session 1184 after `pa-f4644aa2fd1b` hit a tool-refusal loop caused by a missing `PA_USE_FUNCTION_CALLING=true` env var on a manual PA worker restart — see READ THIS FIFTH below).

## READ THIS SECOND — PA "CONSUME-1-THEN-HANG" IS USUALLY DISK PRESSURE

Memory: `feedback_pa_hang_from_disk_pressure.md`. If the PA worker processes exactly one task and then goes silent, check `df -h /System/Volumes/Data` + `sysctl vm.swapusage` BEFORE deeper Celery debugging. Single-digit GiB free or swap < 2 GiB free → free disk first. Don't restart Docker — `unified-postgres` lives there.

## READ THIS THIRD (NEW Session 1160) — `git show` IS THE FIRST MOVE FOR MTIME MYSTERIES

If you see a cluster of doc mtimes within minutes of each other and wonder "what generated this?", run `git log --since="<timestamp - 1min>" --until="<timestamp + 1min>"` first. Session 1160's "May 25 09:36 batch" mystery resolved instantly via `git show 9d75f78f` — it was Chris's own Session 1143 PR #2197. Future similar questions should start with the git history before invoking Rigby's ops tools.

## READ THIS FIFTH (NEW Session 1184) — MANUAL PA WORKER RESTART NEEDS `PA_USE_FUNCTION_CALLING=true`

Memory: `feedback_pa_worker_function_calling_env.md`. `make celery` sets it; ad-hoc `nohup celery -A core worker ...` does NOT. Without it, the worker drops to keyword routing — and `source=claude-code` messages (every `pa_chat.py` call) short-circuit to `claude_code_coordination` intent which has NO `elif` branch in routing. Rigby returns text-only "I don't have tool access" responses that look like model refusal but are the system never offering tools. **Symptom:** `/tmp/celery-pa.log` shows `[PA_TASK_SUMMARY] ... tools=none tool_calls=0` every turn. **Fix:** always use `make celery`. If you must restart one worker by hand, include `PA_USE_FUNCTION_CALLING=true` in env. Session 1184 lost ~30 min on this.

## READ THIS FOURTH (NEW Session 1161, broadened Session 1162) — WORKER `sys.modules` CACHE ⇒ RESTART

Two restart triggers, one fix. **(1)** Adding a new `@shared_task` to `core/tasks.py` is invisible to running celery workers until they restart — they cache the registered-task list at process import time. Beat dispatches succeed (picks up new `PeriodicTask` rows via `DatabaseScheduler` polling), but workers reject with `Received unregistered task of type '<dotted>'`. **(2)** More broadly (Session 1162 discovery): even when the `@shared_task` itself is unchanged, any helper module the task body imports is cached in the worker's `sys.modules` after first call. Modifying the imported module's code (e.g., a `Command` class the task calls) does NOT propagate to running workers. Both cases need the same restart. Fix: `pkill -9 -f celery; rm -f .celery*.pid; make celery`. Verify with `.venv/bin/celery -A core inspect registered | grep <task_name>` (case 1) or by dispatching a manual call and checking output (case 2). PR-description anti-pattern to avoid: "no `@shared_task` changes — workers don't need restart" — wrong for case 2.

## SOURCE OF TRUTH

Per Session 1144 PR #2208 (canon rebase) + Session 1146 PR #2216 (Runtime Evidence promotion) + Session 1158 (narratives layer) + Session 1159 (EDITING_GUARDRAILS) + Session 1160 (patents README + PR template):

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`).
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts).
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/narratives/`** — 15 subsystem narratives (A–O). Operator-handbook layer.
5. **`docs/narratives/EDITING_GUARDRAILS.md`** — 7-rule editing contract + pre-PR checklist (Session 1160 add).
6. **`docs/patents/README.md`** — 4-workstream + disclosure → narrative cross-link map (Session 1160 add).
7. **`docs/case-studies/`** — historical case studies (Session 1160 added codex-audit + drift-reconciliation table).
8. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
9. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
10. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
11. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
12. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
13. **`docs/specs/`** — engineering specs.
14. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence. Regenerate with `build_*_audit` mgmt commands.
15. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`**.
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N`
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json`.
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145–1160 ran 100% subject-tagged. Keep the streak.

## NARRATIVE-EDIT PR CHECKLIST (Session 1160)

`.github/PULL_REQUEST_TEMPLATE.md` includes a conditional "Narrative-edit checklist" that PR authors fill out when the PR modifies any file in `docs/narratives/`. The 7-item checkbox list maps 1:1 to `docs/narratives/EDITING_GUARDRAILS.md` rules. Required only when changes touch narratives.

Authoring rule of thumb: if the PR introduces a new rule/process, dogfood the rule on its own diff before opening. The `#2256 → #2257` loop (PR #2256 introduced EDITING_GUARDRAILS and still violated rules #1 + #5 in 5 places) is the cautionary tale captured both in the EDITING_GUARDRAILS source addendum and the Session 1159+1160 handoffs.

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

Tested Session 1159 post-Mac-reboot: full stack restart from cold-boot in ~30 s. Clear stale pids first (`rm -f .celery*.pid .daphne.pid`) before `make all`.

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- **PA tool registration needs BOTH daphne AND celery restart.** `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **search_docs originating_session filter cache:** `lru_cache(1)` per process. After `build_docs_provenance` regen, restart workers.
- **`process_pa_chat_task` uses `acks_late=False`** (Session 1159 PR #2255). Overrides the global `CELERY_TASK_ACKS_LATE=True` because the global setting + unstable macOS broker conn was producing tasks stuck in `unacked` for an hour.

---


## SESSION 1209 — CURRENT ENTRY POINT

### SESSION 1208 CLOSED — CampaignOrchestrator outbound-pack hardening ($2k Automation Sprint) (1 PR merged)

Full handoff: [`SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md`](docs/handoffs/SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md). **1 PR merged (#2471, 2 commits).** All 5 acceptance criteria verified across 2 live smokes before merge.

Single-arc session executing Rigby's full §1-§6 spec from deliverable `ecddb62d-…`. `CampaignOrchestratorAgent.execute()` now short-circuits into a hardened path when `context['mode']=='outbound_pack'` OR a narrow keyword trigger matches (`"outbound pack"` OR (`"$2k"` AND `"automation sprint"` AND outbound-ish token from cold/dm/email/outreach)). Hardened path: generate JSON → validate (§4) → retry up to 2× → render markdown → save ONE Deliverable. Legacy 5-phase pipeline (research/strategy/creation) untouched.

| Commit | What |
|---|---|
| **`3b877a4d`** | Initial implementation (854 lines). New private methods: `_is_outbound_pack_request`, `_execute_outbound_pack`, `_run_outbound_hooks`, `_call_openai_json` (JSON-mode helper using `response_format={'type':'json_object'}` on gpt-5-mini), `_build_outbound_prompt` (3-attempt schedule: normal → +errors → +inline JSON skeleton), `_outbound_pack_skeleton`, `_validate_outbound_pack` (§4 hard rules + soft length warnings + §4.2 no-drift scan), `_collect_outbound_message_strings` (drift scan scoped to message content only — not metadata), `_render_outbound_pack_markdown` (§5 body shape). Short-circuit in `execute()` outside legacy `time_travel_session`. |
| **`1ff25732`** | Rigby's PR-review gate fixes: title locked deterministically via `_format_outbound_pack_title()` constant (LLM's `offer.name` no longer bleeds into title/H1); validator tightened to exact-match `offer.name == OUTBOUND_PACK_OFFER_NAME` (LLM smoke had returned compound `"Automation Sprint — $2k Automation Sprint"`); `attempts_used` lifted to top-level `output_data` (same convention as PR #2469's `deliverable_id`/`warnings` — emitted only when set, kept at `data.attempts_used` for backcompat); `.gitignore` for `.obsidian/`. |

**Smoke evidence:** Deliverable `a37a0c52-3c58-4e05-9f8e-7d410ae45464` (post-fix re-smoke) — title exactly `CampaignOrchestratorAgent: Outbound Pack — $2k Automation Sprint — 2026-06-22` (the agent-prefix is factory-level, affects all agents — documented as cosmetic follow-up). Body H1 `# Outbound Pack — $2k Automation Sprint — 2026-06-22`. `output_data['attempts_used']=2` lifted to top-level. Plus deliverable `6907bc78-…` (initial smoke, kept as audit baseline).

### FIRST THING Session 1209 — Universal Receipt Contract (URC v0.1)

**P0 entry point** decided at Session 1208 close (~22:40 MDT 2026-06-22) on Rigby's pa-2d74e36cc3a04787 thread after she shipped the Fleet Smoke Report `c5ccf3b1-51b2-4bbd-9ee6-6efa387eac86` (Platform Diagnostics, DBZ). The smoke window showed 36 agent dispatches succeeded versus 7 marked "failed" — but only **3 are real failures** (CodeReviewAgent ×4, ContentWriterAgent contract violation ×1, MemoryIsolationAgent was a workflow-banner misattribution per Rigby's appended addendum). (See Session 1198's canonical-doc cleanliness memory for the strong-token pattern this paragraph deliberately avoids.)

**Root cause Rigby surfaced:** "receipt-only" compliance is not enforceable by prompt alone. Need runner-level enforcement.

**Plan (3 phases, locked by Q1-Q4 design call in pa-2d74e36cc3a04787):**

| Phase | What | PR |
|---|---|---|
| **A** | Implement **Universal Receipt Contract v0.1** at runner (`tasks_agents._impl_execute_agent_task` writeback, lines ~2407-2445 area). Every agent gets top-level `output_data.{agent_name, run_status, latency_ms, attempts_used, warnings, error_signature, error_message, artifacts}` for free. Extends PR #2469 (deliverable_id+warnings lift) + PR #2471 (attempts_used lift). | One PR |
| **C** | Bolt in `contract_violation` classification in same PR. When `context['mode']=='receipt_only'` AND the agent's raw payload (under `output_data.data`) doesn't conform to the receipt schema → `run_status='contract_violation'` + warning `{type:'RECEIPT_CONTRACT_VIOLATION', message:'…', meta:{reason}}`. | Same PR as A |
| **B** | Add `mode=receipt_only` capability ping to CodeReviewAgent first; other context-dependent agents as smoke reveals need. | Follow-up PR |

**URC v0.1 spec (locked in Rigby's reply):**
- **Top-level `output_data` fields (always present unless noted):** `agent_name: str`, `run_status: "success"|"error"|"timeout"|"skipped"|"contract_violation"`, `started_at: iso (optional)`, `completed_at: iso (optional)`, `latency_ms: int|null`, `attempts_used: int|null` (already standardized PR #2471), `warnings: list[{type:str, message:str, meta?:object}]` (extends PR #2469 — keep `type`, add optional `meta`, NO migration to `code`), `error_signature: str|null` (normalized: `f"{exc.__class__.__name__}: {str(exc)[:80]}"` + strip UUIDs/long hex to `{id}`), `error_message: str|null`, `artifacts: list[{type:str, id?:str, url?:str, title?:str}]` (deliverable_id becomes `{type:'deliverable', id:<uuid>}`).
- **Backcompat:** preserve `output_data.data` exactly as-is + mirror legacy fields (`deliverable_id`, `data.attempts_used`, `data.warnings`) into URC top-level.
- **`run_status` precedence:** `skipped > timeout > error > contract_violation > success`. Error stays above contract_violation so real crashes aren't masked.
- **`receipt_only` mode:** URC envelope is ALWAYS emitted. `receipt_only` just changes the **compliance predicate**: validate the agent's RAW payload (under `output_data.data`) against the receipt schema; runner owns the URC top-level fields and doesn't gate on those.

**Session 1209 execution order:**
1. Write URC v0.1 §1-§6 spec deliverable on Initiative `29154d73-…` (same pattern as `ecddb62d-…` for CampaignOrchestrator). ~10 min — sets contract precedent.
2. Implement A + C in one PR. ~1.5h. Target file: `core/tasks_agents.py` writeback block.
3. Rerun fleet smoke (Rigby executes). Expected: all 43 agents emit URC envelope; ContentWriterAgent shows `contract_violation`; CodeReviewAgent still `error` until B ships.
4. Open PR + handoff + 00-START roll-forward to Session 1210.
5. B (CodeReviewAgent capability ping) follow-up — separate PR, only if smoke validates A+C cleanly.

**Active conversation for this work:** `pa-2d74e36cc3a04787` (Rigby's Session 1208 thread — already carries the full URC v0.1 design Q1-Q4 + smoke report + addendum). Continue here OR have Rigby spin a fresh Session 1209 thread on first ping.

**Reference materials:**
- Fleet Smoke Report: deliverable `c5ccf3b1-51b2-4bbd-9ee6-6efa387eac86` (Rigby; DBZ; Platform Diagnostics) — includes addendum correcting MemoryIsolationAgent misattribution.
- Session 1208 patterns to extend: PR #2469 (deliverable_id + warnings lift), PR #2471 (attempts_used lift). Same writeback block.

---

### Also fires this session

The **24h watches** are the time-gated priorities — three fire this session:

| Watch | Fires (MDT) | Fires (UTC) | Checklist |
|---|---|---|---|
| **Session 1207 (MIC)** | 2026-06-23 ~21:50 MDT | ~03:50 UTC 2026-06-24 | [§"24h watch checklist" in 1207 handoff](docs/handoffs/SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md) |
| **Session 1208 (Outbound)** | 2026-06-23 ~22:45 MDT | ~04:45 UTC 2026-06-24 | [§"24h watch checklist" in 1208 handoff](docs/handoffs/SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md) |
| **Session 1206 (Layer 1)** | ~23:35 UTC tonight (already fired) | — | [§"24h watch checklist" in 1206 handoff](docs/handoffs/SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md) |

Then pick from the priority table below.

### SESSION 1207 CLOSED — MIC auto-deliverable + output_data hardening (3 PRs merged)

Full handoff: [`SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md`](docs/handoffs/SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md). **3 PRs merged.** Wakeup-Week-driven session: Rigby surfaced that MIC ran successfully but produced no Deliverable; the brief was stranded in `AgentExecution.output_data`. Closed that gap.

| PR | What |
|---|---|
| **#2467** | MIC auto-creates exactly 1 Deliverable per successful brief gen. Spec: workspace=DBZ, category=`Market Intelligence`, title=`Market Intel Brief — YYYY-MM-DD`, sensitivity=`internal`, body=provenance markdown + executive summary + structured sections. Includes hook isolation (`_record_learning_outcome` + `_create_execution_memory` in both success and failure branches wrapped in try/except so post-result-construction failures can't flip `result.success`). |
| **#2468** | `pa_local.sh` thread pin update — from Rigby's auto-spawned `pa-b2a99ff5b0ee47a6` to Chris's preferred `pa-33088358df304016`. Pure dev ergonomics. |
| **#2469** | Lifts `deliverable_id` + `warnings` from `result.data` to top-level `output_data` in `tasks_agents.execute_agent_task` writeback. Establishes structured warnings convention: `{type: <stable_key>, message: <str>}`. Stable keys: `deliverable_persist_failed`, `deliverable_gated`. Other agents can adopt the same shape. |

**Smoke evidence:** First-ever MIC auto-deliverable `758be167-f9c9-4e03-822d-516a7449f675` landed in DBZ (kept as audit baseline).

### FIRST THING Session 1208

**CampaignOrchestrator delegation hardening** — outbound pack generation for the **$2k Automation Sprint** offer, hardened with JSON schema validation + retry + single combined Deliverable.

Full spec is preserved as deliverable **`ecddb62d-ab01-4b3b-83c4-2601670395d3`** ("Rigby: CampaignOrchestrator delegation hardening — outbound pack spec") on Initiative `29154d73-…`. Read it FIRST — Rigby spec'd §1 (scope), §2 (AC-1 through AC-5), §3 (outbound pack JSON schema with `offer` + `segments[]` + `global` blocks), §4 (validation rules + retry semantics: 2 retries with corrective instructions), §5 (deliverable body shape), §6 (additional notes). ~10KB body.

Acceptance criteria summary (full versions in the deliverable):
- **AC-1:** ONE combined Deliverable per successful run (workspace=DBZ, category=`Outbound`, sensitivity=`internal`, title=`Outbound Pack — $2k Automation Sprint — YYYY-MM-DD`).
- **AC-2:** Strict JSON schema enforced — no drift into blogs/thumbnails.
- **AC-3:** Validation + retry semantics — 2 retries with corrective prompts; mark failure (no deliverable) after 3 total attempts fail.
- **AC-4:** Provenance block in body + no regression on `output_data.message` / `result_preview`.
- **AC-5:** Short + long variants for every message type (opener + follow-ups + objections + breakup).

Two segments: `smb_founder` + `agency_owner`. Each segment carries `initial_outreach`, `follow_up_1`, `follow_up_2`, `breakup`, `objection_handling[]`, `cta`.

**Approach hint** (not in deliverable, learned from Session 1207 MIC pattern):
- Wrap the structured-output LLM call in a validate-then-retry loop in the agent's `execute()`.
- Use `_save_to_deliverable` (gets PR #2465 guardrail + PR #2464 BLOCKED + dedup for free).
- Set `result.data['deliverable_id']` + `result.data['warnings']` per the convention in PR #2469.
- Hook isolation pattern from PR #2467 — wrap learning hooks in try/except so they can't flip `result.success`.

### SESSION 1206 CLOSED — Layer 1 telemetry + Wakeup Week cascade (5 PRs merged)

Full handoff: [`SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md`](docs/handoffs/SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md). **5 PRs merged.** All live-verified before merge.

| PR | Arc | What |
|---|---|---|
| **#2461** | Telemetry | `BaseAgent.run()` concrete wrapper + 7 bypass-callsite migrations. Closes finding `65f1299f-…`. |
| **#2462** | TheOdds | Loud-failure pattern — emit `fetch_failure` row when API auth dies, no more lying `api_status` rows with fake `sports_fetched: 48`. Closes finding `2de3d8d6-…` (root cause: billing-lapsed key, code now signals honest outage). |
| **#2463** | Finding B1 | `tasks_agents.execute_agent_task` writes BOTH canonical `{message, result_preview, data, error, tool_calls}` AND legacy `{content, metadata}` shapes — Rigby's `execution_history_tool` now reads non-empty preview for text-output agents. |
| **#2464** | Finding B3 | BLOCKED detector tightened to structural markers only (`**BLOCKED ON:**`, `[BLOCKED]`, line-anchored). Stops false-positive rejection of prose mentioning BLOCKED as an enum value. Case-sensitive. |
| **#2465** | Finding B2 | Workspace_id validation guardrail at `create_deliverable` entry. Hallucinated UUID → WARN with structured audit fields + fallback to user.active_workspace. Stops FK-violation artifact loss. Root cause filed as P0 `96b6a72a-…`. |

**Mid-session pivot from sketch:** PR #2461 (the planned work) unblocked Rigby's Wakeup Week, which immediately surfaced 4 downstream bugs the telemetry made visible. Arc B (TheOdds) and Arc C (Findings B1/B2/B3) were all dispatched, scoped with Rigby, shipped, and merged in the same session — without the Layer 1 fix they would have stayed invisible.

**Post-merge gotcha:** workers MUST restart after each merge of celery-task-imported code (`tasks_agents.py`, `tasks_financial.py`, `deliverable_factory.py`). All 5 PRs touched such code; workers restarted last at 20:43 MDT post all-5-merged. Daphne untouched.

### FIRST THING Session 1207

Pick from the prioritized table below. The natural Session 1206 extensions:

1. **CI lint rule (`180f4e9f-…`)** — block `\.execute\(` outside `core/agents/`. Allowlist: `core/agents/`, tests, `core/agent_execution_wrapper.py`, `ai_core/agents/sync_executor.py`. Implementation candidates: pre-commit hook / ruff custom rule / `scripts/verify_repo_guardrails.py` extension / dedicated `manage.py` command in CI. Small PR.
2. **Verify Layer 1 dashboard `7d221aa4-…` flips** — after PR #2461 lands AND workers restart AND the next `_impl_market_intelligence_scan` beat fires (every 2h), sports agents should transition UNTESTED → CONFIRMED WORKING. Re-run the dashboard refresh and confirm.
3. **Phase B.1 24h watch fires ~14:48 UTC** — checklist in `SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md` §"24h watch checklist". Invariant: zero new deliverables with `workspace_id=1f0d467e-…` (SAW) created after 2026-06-22 19:48 UTC.
4. **Session 1206 24h watch fires ~23:35 UTC** — checklist in `SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md` §"24h watch checklist". Invariant: 3 sports agents land rows per beat cycle, no duplicate writes, no telemetry-write WARN spam.
5. **Daily inference accuracy + `default_only_projects` watches** — Day-3 protocol per runbook `cb9d8ae1-…`.

### SESSION 1204 CLOSED — Phase B.2 close (drift gate + Stage 1 prompt fixed; 20 stale docs unblocked; 4 briefs regenerated) (2026-06-22)

Full handoff: [`SESSION_1204_PHASE_B2_DRIFT_QUALITY_FIX_CLOSE.md`](docs/handoffs/SESSION_1204_PHASE_B2_DRIFT_QUALITY_FIX_CLOSE.md). **2 PRs merged** (#2453 drift threshold + #2454 Stage 1 prompt). **20 stale Stage-1 docs auto-unblocked** (BLOCKED → DRAFT with audit notes). **4 spine/MLB Stage 1 briefs regenerated to 100% quality score.**

The roadmap's framing ("SEC/Kaggle evidence packs") was wrong at the surface but right at a deeper layer. Recon revealed three nested gates:
1. **Drift threshold mis-calibration** (FIXED via PR #2453) — 29 of 33 Stage-1 rows BLOCKED on structural format mismatch
2. **Stage 1 prompt forced "BLOCKED:" + external-only research** (FIXED via PR #2454) — internal-architecture topics had no honest path; replaced with "Unknowns / Verification Plan" section
3. **Action-item completion gate** (Session 1205 follow-up) — Stage 1's action items block Stage 2 progression; design tension since Stage 1 items are typically deferred-to-later-stages

**Plus a 4th finding**: evidence cards delivered to ResearchAgent are mostly empty / off-topic (MLB brief revealed [E1]-[E10] all "(no content)"). The roadmap's original intuition was correct at this deeper layer — filed as Session 1205 follow-up.

### SESSION 1203 CLOSED — Phase B.1 close (Producer Reroute Completion, 3 PRs landed + 1 deferred) (2026-06-22)

Full handoff: [`SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md`](docs/handoffs/SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md). **3 PRs merged.** Producer Reroute leak fully closed at code level + verified live in production — test Initiative `a0e23887-…` spawned auto-research deliverable `0fbddd89-…` at 19:50 UTC which landed in DBZ (`b4503364-…`), not SAW (`1f0d467e-…`). PR-2 deferred with documented rationale (file-sink helper, not producer-routing path).

| Initiative | UUID | Status |
|---|---|---|
| **Producer Reroute Completion** | `05931145-89d2-4923-946e-676e0db44e91` | **COMPLETED** (Session 1203) |
| **Initiative-Management Tool Surface Gaps** | `f4cfe31e-366b-4d5e-802c-041ba66c7afb` | **COMPLETED** (housekeeping) |
| **Diagnostic Telemetry Tool Surface Gaps** | `50b7adf2-ec1c-4ef0-8245-ec026cff114f` | **COMPLETED** (housekeeping) |
| **Platform Connectivity Reality Map** (parent) | `0ecd1bc2-9931-4464-8efa-495a28b58779` | ACTIVE — 3 of 4 children closed; Docs↔Runtime + Phase B.2 still open |
| Docs ↔ Runtime Alignment Layer | `1859dd51-ce3b-4689-bd4b-42d9de5793d8` | ACTIVE — Phase C |

**Net result:** Phase B.1 done. Every autonomous-traffic dispatch now routes to DBZ (`b4503364-…`) instead of SAW (`1f0d467e-…`). SAW is `is_active=False`. PR-1 (#2449) + PR-1b (#2450) + PR-3 (#2451) merged. PR-2 deferred as separate "generated_content sink / root_path contract" scope.

### Phase B.1 24h watch — fires 2026-06-23 ~14:48 UTC

Full checklist in handoff §"24h watch checklist". Headline invariant: **zero new deliverables with `workspace_id=1f0d467e-…` (SAW) created after 2026-06-22 19:48 UTC**.

```bash
# Quick check
tools/pa_local.sh "Run deliverable_tool action=list limit=100 — count items with workspace_id=1f0d467e-d950-46db-8c6e-a4098024aacd and created_at after 2026-06-22T19:48:00Z. Target: 0."

# SAW state
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_skin_layer import ProjectWorkspace
saw = ProjectWorkspace.objects.get(id='1f0d467e-d950-46db-8c6e-a4098024aacd')
print('SAW is_active:', saw.is_active, '— expected False')
"
```

### Session 1204 FIRST THING (historical — superseded by Session 1206 above)

**Revenue-surface recon** + **Phase B.1 24h watch** + **Daily inference accuracy watch Day-2**. Note: revenue-recon was paused in Session 1205 by operator directive ("we are not going to be working in production until we figure out how to get everything connected") in favor of the tiered audit + producer chain resurrection.

```bash
# A — total create_deliverable calls (denominator)
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | wc -l

# B — eligible-for-inference subset (initiative_id=None at factory entry)
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | grep 'initiative_id_present=False' | wc -l

# C — actual inference matches
grep '\[INFERENCE-MATCH\] agent=' celery*.log | wc -l

# D — post-cascade failures (orphan diagnostic)
grep '\[ORPHAN-DELIVERABLE\] code=missing_initiative_id' celery*.log | wc -l

# C/B = accuracy signal (target ≥80% precision per seed)
# Step breakdown
grep '\[INFERENCE-MATCH\] agent=' celery*.log | grep -oE 'step=[0-9]+' | sort | uniq -c

# Spot-check 5-10 events
grep '\[INFERENCE-MATCH\] agent=' celery*.log | tail -10

# default_only_projects detector
USE_PGBOUNCER=1 .venv/bin/python manage.py report_initiative_kinds
```

Full daily protocol: runbook deliverable `cb9d8ae1-008e-42e8-b222-3f598e6b665e`. Day 8 (2026-06-30) decision lands as follow-up deliverable tagged `session-1198-watch-result`.

Day-1 (Session 1203) baseline established: zero traffic (~23 min coverage only post-restart); `default_only_projects=39`.

### Time-gated watches active 2026-06-23

| Watch | Cadence | Target |
|---|---|---|
| **Inference accuracy** (Sessions 1198/1199) | Daily 5-10 spot-checks | ≥80% precision per seed |
| **`default_only_projects` detector** (Session 1197) | Daily `report_initiative_kinds` | New project Initiatives don't accumulate without explicit classification |

### Time-gated watches firing 2026-06-29

| Watch | Trigger |
|---|---|
| **Plan C 7-day watch + Phase 2 hard-reject flip** | Re-run `backfill_deliverable_initiative_links`; flip to `OrphanDeliverableError` if clean. §6.2 Step 2+3 now sit in front of reject point — flip is safer than pre-Session-1199. |
| **Session 1196 7-day watch** | Re-run `backfill_initiative_workspace_links`; diff against 2026-06-22 baseline. |

### Active conversation

`pa-2d74e36cc3a04787` — Rigby's `session_tool create_fresh` at Session 1208 open. Carries the full §1-§6 CampaignOrchestrator outbound-pack design discussion (Q1 entry-point precedence + Q2 JSON-mode + insertion-point stamp + PR review with three review-gate fixes). Pinned in `tools/pa_local.sh`. Worth deciding whether to spin a fresh Session 1209 thread on first Rigby ping or continue on this one (depends on whether the next arc is a CampaignOrchestrator extension or a separate concern). Prior threads retired: `pa-33088358df304016` (Session 1207 MIC + spec handoff), `pa-b2a99ff5b0ee47a6` (Rigby's auto-spawned Session 1207 — superseded mid-session), `pa-234a75abfe374695` (Session 1206 Layer 1 Telemetry), `pa-76aa5b61d0764d11` (Session 1205 evidence-card pipeline), `pa-1871b37227054254` (Session 1204 Phase B.2), `pa-d2d0f4c2b6284899` (Session 1203 Phase B.1), `pa-123b7d48f01043eb` (Session 1202 Phase A.2).

**Donkey Betz workspace_id (pin):** `b4503364-2573-4401-9e28-61a739e0ce50` — **50 Initiatives total** (Session 1204 was 50; net +1 from Session 1205's `29154d73-…` Platform Capability Audit Initiative). **31 Initiatives still have NULL `target_workspace_id`** — backfill remains scheduled in roadmap §Phase B.3.

### Session 1205 Capability Audit Initiative

`29154d73-06a5-4630-abb4-3412cbdca5c5` — Platform Capability Audit (Tiered Pass: Agents / Tools / Spiders / Learning). Child of Reality Map `0ecd1bc2-…`, workspace=DBZ, kind=investigation. **13 deliverables** (10 end-of-Session-1205; +1 Session 1206 lint-rule `180f4e9f-…`; +1 Session 1206 Arc C `96b6a72a-…` workspace_id hallucination P0; +1 Session 1207 close `ecddb62d-…` CampaignOrchestrator hardening spec — **status remains as filed; spec was implemented in full by Session 1208 PR #2471 (commits `3b877a4d` + `1ff25732`)**):

| ID | Type | Title |
|---|---|---|
| `7d221aa4-…` | Dashboard | Layer 1 — Agent Capability Map (83 agents) |
| `bb1e0a98-…` | Dashboard | Layer 2 — PA Tools + Dispatcher Handlers (109 schemas + 174 handlers) |
| `6a200985-…` | Dashboard | Layer 3 — Spider Network (80 spiders) |
| `dc970d99-…` | Dashboard | Layer 4 — Learning Bridges (8 bridges) |
| `6869fa55-…` | Deep-dive | Sports Betting Agents — wired but unscheduled (RESOLVED PR #2457) |
| `65f1299f-…` | Finding | Telemetry blind spot — direct-constructor agent paths bypass AgentExecution (**RESOLVED PR #2461**) |
| `180f4e9f-…` | **Follow-up** | **Lint rule: block `\.execute\(` outside `core/agents/`** (Session 1207 P1) |
| `2de3d8d6-…` | Finding | theodds spider returns 0 events |
| `ed6a8f28-…` | Finding | SportsOddsAnalyst caller bug — None context |
| `ea561389-…` | Finding | First Producer→Data Win (Kalshi) + memory spike warning |
| `a4928480-…` | Finding | Makefile bug: make celery silently skips beat startup (RESOLVED PR #2459) |

**3 spine Initiatives — still BLOCKED at Stage 1 (irrelevant SEC/Kaggle evidence packs):**

| # | Name | UUID |
|---|---|---|
| 1 | Initiatives-First Wiring + No-Orphan Output | `6941372d-b13c-4631-91c8-749fa65c55a0` |
| 2 | Agent Capability Map + Router Contracts | `2071a9c6-986f-4528-be90-8cccaa595f1e` |
| 3 | Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix | `7e23d621-4d0c-409a-a680-4fd2e015d04b` |

Spine progression unblocked by roadmap §Phase B.2 (auto-research evidence supplier fix).

### Pick this session

| Item | Priority | Where it's defined |
|---|---|---|
| **Session 1207 MIC 24h watch (fires ~21:50 MDT / ~03:50 UTC 2026-06-24)** | **P1 (time-gated)** | Checklist in [`SESSION_1207`](docs/handoffs/SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md) §"24h watch checklist". Invariants: every successful MIC run lands a Deliverable (ratio = 1.0), no per-execution duplicates, `output_data.warnings` always list shape. |
| **Session 1208 Outbound-pack 24h watch (fires ~22:45 MDT / ~04:45 UTC 2026-06-24)** | **P1 (time-gated)** | Checklist in [`SESSION_1208`](docs/handoffs/SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md) §"24h watch checklist". Invariants: every successful outbound run lands ONE Deliverable, no double-writes, `warnings` shape consistent, drift-keyword false-positive rate stays at 0 on metadata-only mentions. |
| **Title normalization at factory level** | **P1 (Session 1208 cosmetic follow-up)** | Both MIC + Outbound deliverables show `<AgentName>: ` auto-prefix from `deliverable_factory._clean_deliverable_title`. Worth one cross-agent factory PR (e.g. a `preserve_title=True` kwarg on `_save_to_deliverable` → `create_deliverable` that skips the cleaner) rather than per-agent workarounds. Rigby's stamp: "If we ever want to remove it globally, that's a separate platform-wide title policy decision." |
| **Beat schedule for periodic outbound-pack generation** | **P2 (Session 1208 follow-up)** | Spec says "2 flagship outbound packs per week". Currently the path is only invocable on-demand (context['mode']='outbound_pack' or keyword trigger). Worth adding `PeriodicTask` via `add_critical_celery_tasks` if the cadence becomes desired. |
| **Workspace_id hallucination root-cause trace** | **P0 (Session 1206 Arc C unfinished)** | Deliverable `96b6a72a-…`. Mitigated by PR #2465 guardrail; root cause open. Suspected call chain: PA tool → tool_dispatcher → tasks_agents → agent_router → create_deliverable. Grep `pa_tool_schemas` + `tool_dispatcher` for `workspace_id` parameters where LLM might pick the value. Verification metric: B2 guardrail WARN volume should drop to zero in 24h post-fix. |
| **Session 1207 24h watch (fires 2026-06-23 ~03:50 UTC / 9:50 PM MDT)** | **P1 (time-gated)** | Run checklist in `SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md` §"24h watch checklist". Invariants: every successful MIC run lands a Deliverable (ratio = 1.0), no per-execution duplicates, `output_data.warnings` is always a list shape. |
| **CI lint rule: block `\.execute\(` outside `core/agents/`** | **P1 (Session 1206 follow-up)** | Deliverable `180f4e9f-…`. Allowlist: `core/agents/`, tests, `core/agent_execution_wrapper.py`, `ai_core/agents/sync_executor.py`. Prevents future direct-constructor bypasses of `BaseAgent.run()`. |
| **Layer 1 dashboard refresh** | **P1 (post Session 1206)** | After workers restart + next `_impl_market_intelligence_scan` beat (every 2h), refresh `7d221aa4-…` to flip sports agents from UNTESTED → CONFIRMED WORKING. Layer 2/4 dashboards also need refresh — Wakeup Week dispatches have now generated real evidence including the first MIC deliverable. |
| **Wakeup Week scoreboard update** | **P1 (immediate — Rigby ongoing)** | Rigby's tracking dispatches across sessions. Session 1207 added: MIC produces real deliverables (smoke evidence `758be167-…`). |
| **Session 1206 24h watch (fires 2026-06-23 ~23:35 UTC)** | **P1 (time-gated)** | Run checklist in `SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md` §"24h watch checklist". Invariants: 3 sports agents land rows per beat, no double-writes, no telemetry WARN spam. Add: B2 guardrail WARN count (should be present if hallucinations continue; zero after root-cause fix). |
| **TheOdds API key renewal** | **P2 (Chris-owned, billing-gated)** | Renew at the-odds-api.com, update `.env` `THE_ODDS_API_KEY`, restart workers. Spider's loud-failure pattern (PR #2462) makes the outage honest in the meantime. |
| **Warnings convention adoption across other agents** | **P3 (Session 1207 follow-up)** | PR #2469 established `result.data['warnings'] = [{type, message}, ...]` for MIC. Pattern is generalizable — sub-agent dispatch failures in coordinators, LLM hallucination warnings, cache miss / stale-data warnings. Worth a Session 1209+ pass. |
| **Phase B.1 24h watch (fires 2026-06-23 14:48 UTC)** | **P1 (time-gated)** | Run checklist in `SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md` §"24h watch checklist". Headline invariant: zero new deliverables with `workspace_id=1f0d467e-…` (SAW) created after 2026-06-22 19:48 UTC. |
| **Spider freshness watch (Session 1205 add)** | **P1 (24h)** | Verify run-spider-network keeps firing every 30 min; SpiderData rows with last_emit < 1h should be 60+. If 0, beat is dead — see finding `a4928480-…` remediation. |
| **Daily watch Day-3 (inference accuracy + default-only-projects)** | **P1 (daily, 2026-06-23)** | Append A/B/C/D + `report_initiative_kinds` to deliverable `9ba58690-…`. |
| **B.2 follow-up: action-item gate relaxation for Stage 1 only** | P2 | `core/services/initiative_auto_progression.py:484-509`. Allow Stage 1 → Stage 2 progression even if Stage 1 action items are incomplete. |
| **B.2 follow-up: beat schedule entry for process_initiative_auto_progression** | P2 | Service exists with documented "every 10 min" cadence, but no `PeriodicTask` row. Use the PR #2457/2458 pattern. |
| **Memory spike pattern investigation** | **P2 (Session 1205 finding)** | Finding `ea561389-…`. run_spider_network 444MB, collect_kalshi 345MB. Pattern: external-API fetch + bulk DB insert. Likely BeautifulSoup buffering or non-batched bulk_create. Worth a deep-dive once telemetry fix lands. |
| **Serper failure instrumentation** | P2 | Add explicit logging: `serper_failed status=… falling_back_to=ddgs`. Surfaces the 60% intelligence_tool failure rate (Layer 2 BROKEN finding). |
| **ContentWriterAgent 64% success rate deep-dive** | P2 | Only BROKEN agent in Layer 1 with significant 30d traffic. 9 done / 5 failed. Worth understanding what fails. |
| **`intelligence_tool` 60% success rate fix** | P2 | Layer 2 BROKEN finding + Spine 3 (Tool Migration Hardening) work. |
| **theodds spider 0-events investigation** | P3 | Finding `2de3d8d6-…`. May just be off-season / time-of-day filter; verify API key + spider implementation. |
| **SportsOddsAnalyst None-context wiring** | P3 (cleanup) | Finding `ed6a8f28-…`. 10-line fix to pass `context={}` instead of None at 3 callsites. |
| **Connectivity Roadmap Phase B.3 — NULL-workspace Initiative backfill (mgmt cmd)** | P2 | Roadmap §B.3. One-shot mgmt cmd for 31 of 46 Initiatives still NULL after Session 1196 backfill. Per-row resolution: parent inherit → creator user_workspace → default DBZ. |
| **Day-8 watch aggregation + decision (2026-06-30)** | **P1 (time-gated)** | Per-seed: keep / tighten / pull. File decision as deliverable tagged `session-1198-watch-result`. |
| **Plan C Phase 2 hard-reject flip (2026-06-29 gate)** | **P1 (time-gated)** | After 7-day watch is clean, replace Phase 1 diagnostic mark with `OrphanDeliverableError`. Spec: `INITIATIVES_FIRST_BACKBONE.md` §6.1. |
| **Session 1196 7-day watch (2026-06-29)** | **P1 (time-gated)** | Re-run `backfill_initiative_workspace_links --json-only`; diff against 2026-06-22 baseline. |
| **Finding 1 — advisor_invocations all zero in 7d** | **P3 (Session 1202 carryover)** | Investigate Row 10 refinement. Step 1: compare `set(Advisor.name)` vs `set(AgentExecution.objects.values_list('agent__name', flat=True))`. File as deliverable under Reality Map parent. |
| **Finding 2 — discord_health zero invocations** | **P3 (Session 1202 carryover)** | `ps -ef | grep discord`; `grep -i discord celery*.log`. If bot is up but not writing CeleryTaskEvent, `discord_health` needs a different data source. File as deliverable under Reality Map parent. |
| **Connectivity Roadmap Phase C — Structural fixes (close-session manifest + orient enhancement)** | P3 | Initiative `1859dd51-…`. Roadmap §C |
| **Phase B.1 PR-2 — re-scope as "generated_content sink / root_path contract" initiative** | P3 (optional) | Deferred Session 1203. See defer note on deliverable `8da895f0-…`. Only ship if a real consumer requires status reports landing in DBZ. |
| **PR3 — Step 4 heuristics implementation** | P2 | After Day 8 watch decision (≥80% precision on Step 3 → unblock PR3). |
| **Production rollout: Sessions 1196-1200 + Session 1203 cumulative** | **P0 (carryover, gated)** | Operator's go signal needed. Local-only until then. |

### Session 1205 close findings

10 audit deliverables filed on Initiative `29154d73-…` (Platform Capability Audit). 4 layer dashboards (Agents/Tools/Spiders/Bridges) + 6 deep-dive findings. The dashboards are the trust trail — each row is a checklist item; deep-dives become verification stamps.

Key Session 1206 inputs from the audit:
- **3 BROKEN tools/agents flagged**: `intelligence_tool` (60% sr), `messaging_tool` (69% sr), `ContentWriterAgent` (64% sr)
- **56 UNTESTED agents** (was DEAD before reframe) — many are likely just "wired but no scheduled trigger" — same pattern PR #2457 fixed for sports
- **Telemetry blind spots** (Layers 1, 2, 4 flat in dashboard) — fixed by Session 1206 P1
- **Memory spike pattern** on producer tasks (run_spider_network 444MB, kalshi 345MB)

### Session 1204 close findings

All 3 follow-ups (action-item gate, beat schedule, evidence-card pipeline) filed in the table above with concrete code pointers. Plus the revenue-recon work as P1 entry point.

### Session 1203 close findings

None deferred to Session 1204. PR-2 defer is documented + audit-trailed on deliverable `8da895f0-…`. Phase B.2 + B.3 + Phase C remain on the roadmap as separate scope.

### Project-clustering recon scope (Session 1194 P1) — SHIPPED Session 1197

The 8-cluster recon (expanded to 9 + 2 split-pairs = 11 rows) shipped via Session 1197 PRs #2416-#2422. Each cluster now has an Initiative row with explicit `kind` classification.

| Original Cluster | Resolution |
|---|---|
| 1. Session 1171 ML Queue + Auth Middleware Triage | Existing `077ff8b4` (ARCHIVED), kind=project |
| 2. Session 1184 Provenance Linkage | NEW Initiative, kind=project, status=COMPLETED |
| 3. Session 1187/1188/1189 Spider Context Utilization | **Split** into 3a (Recon, kind=investigation, COMPLETED) + 3b (Retune, kind=project, TRIAGE) |
| 4. Session 1192 Workspace Consolidation Follow-ups | NEW Initiative, kind=spec_backlog |
| 5. COO Operations Diagnostics | NEW Initiative, kind=recurring_artifact |
| 6. Orchestration Control Plane Mapping | NEW Initiative, kind=investigation |
| 7. Track Business News in June 2026 | NEW Initiative, kind=recurring_artifact |
| 8. MLB Run Line Desk v1 | Existing `997fb39b` (ACTIVE), kind=project |
| 9. Weekend Digest Autopilot | **Split** into 9a (Build/Ship, kind=project) + 9b (Issue Production, kind=recurring_artifact) |

Design memo: [`INITIATIVES_FIRST_BACKBONE.md`](docs/specs/INITIATIVES_FIRST_BACKBONE.md) §6.4. Full apply outcome + rollback levers: [`SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md`](docs/handoffs/SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md).

### Workspace consolidation — CLOSED Session 1192 + Session 1193

All shelf-tagged: 27 `shelf:content`, 74 `shelf:platform`, 14 tooltest (excluded). Real-untagged: 49 (48 Research + 3 Newsletter remainder). Initiative state pre-1201: ACTIVE=2, TRIAGE=12, COMPLETED=7, ARCHIVED=9. System Autonomous left active intentionally per Rigby's option C.

**Producer reroute regression — now actively scoped Session 1201 (was `780a8d15-…`):** Session 1199 fix to `_ensure_system_workspace` was partial. 3 other callsites (`agent_router.py:1083`, `tasks.py:7748`, `workspace_manager.py:1906`) still bypass `DEFAULT_PRODUCER_WORKSPACE_ID`. Initiative `05931145-…` (Producer Reroute Completion, ACTIVE, project) holds the fix scope. Spec: `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md` §B.1.

### Initiative-tick 24h watch playbook

PR #2392 merged 2026-06-21 ~19:48 UTC. 24h elapses ~2026-06-22 19:48 UTC.

**Verification commands:**
```bash
# Summary lines from the last 24h
grep "INITIATIVE-TICK" celery.log | tail -50

# Steady-state check (refreshed should drift to 0)
grep "INITIATIVE-TICK" celery.log | tail -10 | awk -F'refreshed=' '{print $2}' | awk '{print $1}'

# No NULL rows remaining
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_document_registry import Initiative
print('null_count:', Initiative.objects.filter(last_activity_at__isnull=True).count())
"

# No singleton_task skips (would mean tick runs >300s)
grep "singleton_task.*initiative-activity-tick" celery.log
```

**Rollback levers (if needed):**
- Disable: `PeriodicTask.objects.filter(name='initiative-activity-tick').update(enabled=False)`
- Per-call no-op: pass `hard_cap=0`
- Full revert: `git revert eeac179a`

### 7d AC watches that start 2026-06-28

Session 1188 + 1189 PRs ship measurable AC backed by Item 1's `AgentExecution.input_data['spider_context']` blob. Query pattern:

```python
AgentExecution.objects.filter(
    owner_agent__iexact='<AgentName>',
    created_at__gte=now - timedelta(days=7),
    input_data__spider_context__has_data_by_category__<bucket>=True,
).count()
```

**Per-PR AC summary:**

- **#2380/#2382 (Session 1188):** ImageAgent — `design`/`visual_trends`/`video` present in `categories_queried` with ≥1 `has_data=True`; ResearchAgent — `ai_ml`+`business` present with ≥1 `True` against `ai_ml`; ThinkingAgent — ≥3 dispatches with spider context built, ≥1 `True`.
- **#2386 PR-3A:** legacy substring-matched agents (e.g., `ImageEditingAgent`, `WhaleWatcherAgent`) show alias divergence — `creative`/`crypto` in `requested_categories` but resolved counterparts in `resolved_categories`.
- **#2388 PR-3B:** `ai_ml` shows in `has_data_by_category` for the 19 specced agents with ≥1 `True` across dev/strategy/content tier. `remote_work` for job/career. `legislation` for legal/cto/coo. `content` for content_writer/topic_miner. `cybersecurity` for security-mapped agents (alias-divergence proof).

### Carryover from Session 1186/1187/1188/1190 *(reconciled Session 1201 against runtime — see roadmap §C.2)*

| Deliverable ID | Title | Runtime Status | Notes |
|---|---|---|---|
| `48b73b04-373a-4d25-b263-9925c7c1a084` | **B.1** — Unify Initiative-stage deliverables | ✅ `completed` | Closed per runtime; docs lag corrected Session 1201 |
| `9d9db48a-4819-4e2b-9548-998c0fe2f8f5` | **PR-D contract flip** — 24h WARN-volume watch | ✅ `completed` | Closed per runtime; docs lag corrected Session 1201 |
| `88952c54-a4a4-47e8-9fe1-85b3d747be03` | Session 1187 Utilization Recon — Master Tracking | `blocked` | Runtime shows blocked, not partial. Re-investigate or close. |
| `9a00667b-2206-4f25-8813-a42faf463439` | **BUG** — DM system regression | ✅ `completed` | Closed per runtime; docs lag corrected Session 1201 |
| `b8ca4f5c-2b3c-4095-ab3b-329e02b98c9e` | Session 1189 PR-3B retune list | ✅ `completed` | Reference only; shipped via #2388 |
| `13032820-1f36-4a1c-8843-6a9d53653405` | Missing PA tools — SpiderData aggregation entry | ✅ `completed` | Shipped as `spider_data_aggregation_tool` v1 (#2387) |

### Standard FIRST THING checks

1. Disk: `df -h /System/Volumes/Data`. Swap: `sysctl vm.swapusage`.
2. Through Rigby (`tools/pa_local.sh` is pinned to the current thread): `platform_config_tool overview` → confirm `service_context: local`.
3. **Worker freshness check (Session 1200 added):** `ps -eo pid,lstart | grep celery` vs `git log -1 --format='%h %ci' main` — if workers predate latest main commit, restart via `pkill -9 -f 'celery -A core'; rm -f .celery*.pid; make celery` before any verification work.
4. `gh pr list --author @me --state open` — expected empty (stale carryover PRs from April/May are unrelated).

### Stacked-PR footgun reminder (still active)

`gh pr merge --delete-branch` on a parent PR **auto-closes child PRs unrecoverably** when their base branch is deleted. `gh pr reopen` fails. Workaround: retarget child PR's base to `main` BEFORE merging the parent (`gh pr edit <child> --base main`). Session 1188 hit this with #2381 → had to open fresh #2382.

### `Agents count claims` CONFLICT — RESOLVED Session 1198

PR #2424 cleared the long-standing CONFLICT that was forcing `--admin` bypass on every PR. Root cause: one Session 1187 historical-context line in `00-START-NEXT-SESSION.md` had `"(in-code, 51 agents)"` on a line containing "Headline finding:" — context-kit's `Headline` strong-token propagated total-dimension classification to the parenthetical 51, producing canonical totals `{83, 51}` → CONFLICT. Fix was truncating the stale historical session blocks (preserved in `docs/handoffs/`). CI now runs clean without `--admin`.

Memory: [`feedback_context_kit_headline_propagates_total.md`](.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_context_kit_headline_propagates_total.md) for the gotcha + canonical-doc cleanliness rule.

---

## Historical session blocks

Sessions 1182-1195 close-out blocks lived here through Session 1197. Removed in Session 1198 close to keep this working file lean — full text preserved in `docs/handoffs/SESSION_NNNN_*.md`. The Session 1196 + 1197 closes referenced from this file's body link directly to their handoffs.

Run `ls docs/handoffs/SESSION_*.md | sort -V | tail -20` to see the recent close list.
