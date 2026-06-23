# Session 1208 — CampaignOrchestrator outbound-pack hardening ($2k Automation Sprint)

**Status:** PR #2471 open + live-verified end-to-end before opening; Rigby's review-gate fixes applied as commit `1ff25732` on the same branch (title deterministic + `attempts_used` top-level lift + `.gitignore` for `.obsidian/`). Pending Rigby's final stamp + Chris's merge call.
**Date:** 2026-06-22 (extended past midnight UTC into 2026-06-23)
**Active conversation:** `pa-2d74e36cc3a04787` — Rigby's `session_tool create_fresh` at Session 1208 open. Pinned in `tools/pa_local.sh`. Prior thread `pa-33088358df304016` (Chris's Session 1207 close) retired.
**Prior session:** [`SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md`](./SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md).
**Next session entry point:** Session 1209 — natural candidates listed in §"Open follow-ups" below; Session 1207's 24h watch fires this session (~03:50 UTC) and Session 1208's own 24h watch arms ~tomorrow 03:50 UTC.

## TL;DR

Single-arc session executing the CampaignOrchestrator delegation hardening spec Rigby filed at Session 1207 close (deliverable `ecddb62d-ab01-4b3b-83c4-2601670395d3` on Initiative `29154d73-…`).

**One PR (#2471), 854 lines, all 5 acceptance criteria verified live before open:**

- **AC-1** ONE Deliverable per successful run (workspace=DBZ, category=Outbound, sensitivity=internal). Smoke deliverable `6907bc78-0a56-4a68-b31d-bb87677cde39` proves it.
- **AC-2** Strict JSON schema enforcement via `_validate_outbound_pack` — no drift into blogs/thumbnails/SEO/video.
- **AC-3** Deterministic 3-attempt retry (Try 1 → Try 2 with structured errors → Try 3 with inline JSON skeleton). Smoke hit `attempts_used=2` — Try 1 failed validation, Try 2 passed.
- **AC-4** Provenance block in body + no regression on `output_data.message` / `result_preview` (PR #2463 dual-shape preserved).
- **AC-5** Short + long variants for every message type. Smoke output: initial outreach 213/438 chars; follow-up 1 167/366 chars.

The existing 5-phase campaign pipeline (research/strategy/creation in `_run_research_phase` / `_run_strategy_phase` / `_run_creation_phase`) is **untouched**. The hardened outbound path is reached via a short-circuit in `execute()` that fires only when `context['mode']=='outbound_pack'` OR a narrow keyword trigger matches.

## Session Manifest

### PRs (open + pending final review)

| # | Title | Commits | Files | Verified |
|---|---|---|---|---|
| **#2471** | feat(session-1208): CampaignOrchestrator outbound-pack hardening ($2k Automation Sprint) | `3b877a4d` (initial) + `1ff25732` (Rigby's review-gate fixes) | `core/agents/campaign_orchestrator_agent.py` (+873), `core/tasks_agents.py` (+9), `tools/pa_local.sh` (+/-16), `.gitignore` (+6) | ✅ live x2 (smoke #1 deliverable `6907bc78-…`; smoke #2 deliverable `a37a0c52-…` post-fixes — title deterministic byte-for-byte, attempts_used=2 lifted to top-level output_data) |

### Deliverables filed / touched

| ID | Action | Note |
|---|---|---|
| `6907bc78-0a56-4a68-b31d-bb87677cde39` | **NEW** (smoke evidence) | First-ever CampaignOrchestrator outbound-pack auto-deliverable in DBZ. Title=`CampaignOrchestratorAgent: Outbound Pack — Automation Sprint — $2k Automation Sprint — 2026-06-22` (factory auto-prepended `CampaignOrchestratorAgent: ` AND extracted `— Automation Sprint —` — same pattern Rigby ratified for MIC #2467). Content 8814 chars; metadata `{segments:['smb_founder','agency_owner'], offer_min_deal_size_usd:2000, attempts_used:2, soft_warnings_count:0, sensitivity:internal, trigger_source:session-1208-smoke}`. Kept as audit baseline. |
| `ecddb62d-ab01-4b3b-83c4-2601670395d3` | **CONSUMED** (Session 1207 entry spec) | Rigby's §1-§6 spec implemented in full by PR #2471. Status remains as filed — the spec is the design contract; the implementation references it via PR description + commit message. |

Initiative `29154d73-…` (Platform Capability Audit) holds the spec on a `kind=investigation` row; this session does **not** add a new row.

## Behavioral invariants — what's now true post-merge

1. **`CampaignOrchestratorAgent.execute()` short-circuits into the hardened outbound path when ANY of these is true:**
   - `context['mode'] == 'outbound_pack'` (deterministic override; works regardless of task wording).
   - Task (lowercased, em-dash normalized) contains `"outbound pack"`.
   - Task contains all three: `"$2k"`, `"automation sprint"`, AND at least one of `cold` / `dm` / `email` / `outreach`.

   Detection lives in `_is_outbound_pack_request(task, context)`. Tightened per Rigby's Q1 review to protect against pricing-discussion false positives (`"$2k automation sprint pricing"` does NOT trigger).

2. **The hardened path always opens its own `time_travel_session('outbound_pack_generation', task, input_data=context)`** — separate trace name from the legacy `campaign_orchestration` block so MIC-style audits can filter cleanly.

3. **On success: exactly ONE Deliverable per run.** Workspace pinned to DBZ (`b4503364-2573-4401-9e28-61a739e0ce50`), category `Outbound`, content_format `markdown`, deliverable_type `document`, tags `['outbound', 'automation-sprint', 'campaign-orchestrator']`. Metadata always carries `sensitivity:internal`, `offer_name`, `offer_min_deal_size_usd:2000`, `segments:[seg_key, …]`, `attempts_used`, `soft_warnings_count`, `trigger_source`.

4. **JSON-mode LLM calls.** `_call_openai_json` uses `response_format={'type':'json_object'}` on `gpt-5-mini` for all 3 attempts. Per Rigby Q2: dramatically reduces format failures so the retry budget gets spent on semantic validation, not parser fights.

5. **3-attempt retry semantics, deterministic.** Try 1 normal prompt + schema summary. Try 2 prompt includes structured `PREVIOUS ATTEMPT VALIDATION ERRORS` list + drift reminder. Try 3 additionally appends an inline JSON skeleton from `_outbound_pack_skeleton(offer_name)`. After 3 failures: `AgentResult.success=False`, NO deliverable, `output_data` keeps the canonical shape (PR #2463) with `validation_errors`, `attempts`, `attempts_used` populated.

6. **§4.2 no-drift scan runs on MESSAGE CONTENT ONLY.** Collected via `_collect_outbound_message_strings()` — offer copy + segment messages + objection replies + ctas + segment_label + global.tone. NOT on metadata fields (`do_not_generate`, `compliance_notes`, `personalization_tokens`, `icp_assumptions`, `segment_key`). Pure-helper smoke caught the original false-positive pre-PR: a valid payload's `global.do_not_generate=["blog posts","thumbnails","images"]` was triggering drift detection even though it's the guardrail block instructing "do NOT generate these."

7. **Soft length warnings surface but don't block.** `short` > 300 chars or `long` > 900 chars appends `{type:'length_exceeded', message:'…'}` to `result.data['warnings']`. Validation otherwise passes.

8. **Persistence routes through `_save_to_deliverable` → `create_deliverable`.** So PR #2465 workspace_id guardrail + PR #2464 BLOCKED detector + dedup machinery all apply.

9. **Warnings convention (PR #2469) extended.** Stable type tags emitted by the outbound path: `length_exceeded`, `deliverable_persist_failed`, `deliverable_gated`. Pattern matches MIC's `deliverable_persist_failed` / `deliverable_gated`; generalizable to other agents.

10. **Hook isolation (PR #2467 pattern).** `_record_learning_outcome` and `_create_execution_memory` each in their own try/except inside `_run_outbound_hooks(success=bool)`. A hook crash logs WARN but cannot flip `result.success` or propagate to the outer except.

11. **Legacy 5-phase campaign pipeline is untouched.** Any task that DOESN'T match `_is_outbound_pack_request` falls through to the existing `with self.time_travel_session('campaign_orchestration', ...)` block exactly as before. No regression on prior CampaignOrchestrator behavior.

12. **`tools/pa_local.sh` points at `pa-2d74e36cc3a04787`.** Future Claude Code sessions land in Rigby's Session 1208 thread by default. Previous pin `pa-33088358df304016` (Session 1207 close) retired.

## Rollback levers (per change)

| Lever | Action | Effect |
|---|---|---|
| **Disable the entire outbound path** | Edit `_is_outbound_pack_request` to always return `False`, OR revert PR #2471. | All `CampaignOrchestratorAgent` invocations route through the legacy 5-phase pipeline. Outbound-pack callers get the old behavior. |
| **Disable JUST the deliverable persist (keep validation/retry)** | Comment out the `try: …self._save_to_deliverable…` block in `_execute_outbound_pack`. | Payload generation + validation still runs; no deliverable lands. `result.data['payload']` still carries the JSON. |
| **Force fall-through for a specific message** | Pass `context={'mode': 'campaign'}` (or anything other than `'outbound_pack'`) AND phrase the task without the keyword triggers. | Bypasses short-circuit deterministically. |
| **Loosen / tighten the keyword trigger** | Edit `_is_outbound_pack_request` body. The keyword list (`outbound pack`, `$2k`+`automation sprint`+outbound-ish) is the entire scope. | One source of truth; no cross-file changes. |
| **Revert thread pin** | Edit `tools/pa_local.sh` `--conversation` flag to a prior value (e.g. `pa-33088358df304016`). | Local PA wrapper routes elsewhere. Pure dev-side change. |

## Post-merge gotchas

- **Worker restart required after merge.** PR #2471 modifies `core/agents/campaign_orchestrator_agent.py`, which is imported transitively by `core.tasks.execute_agent_task` → `core.tasks_agents._impl_execute_agent_task` → `agent_router.route`. Per the `sys.modules` cache rule (memory: `feedback_new_shared_task_needs_worker_restart.md`), running workers won't pick up the new code until restarted. Done in-session: workers restarted 22:19 MDT before the smoke dispatch. **For next session: check `ps -eo pid,lstart | grep celery` against `git log -1 main` and restart if workers predate the merge.**

- **Title double-prefix is a known factory behavior, not a bug.** The factory prepends the agent name AND auto-extracts a fragment. Same pattern observed in MIC's `MarketIntelligenceCoordinator: Market Intel Brief — 2026-06-22`. Rigby ratified the MIC version; this session inherits. If we want title normalization, that's a separate factory-level PR affecting all agents — out of scope here.

- **`AgentExecution.output_data.attempts_used` is `None` at top-level.** The PR #2463 canonical writeback lifts only `message`, `result_preview`, `deliverable_id`, `warnings`, `error`, `tool_calls`, `content`, `metadata`. `attempts_used` lives at `output_data.data.attempts_used`. Worth a future PR that promotes `attempts_used` to a canonical top-level key (same pattern as Session 1207 PR #2469 for `deliverable_id`/`warnings`).

- **Pre-existing Pyright diagnostics in the legacy pipeline (lines 65-1477 of `campaign_orchestrator_agent.py`) are untouched by this PR.** They predate Session 1208 work. Cleanup is out of scope.

- **`.obsidian/` untracked dir.** Shows up in `git status` and as `Warning: 1 uncommitted change` when opening PRs. Worth a `.gitignore` entry — filed as a Session 1209 housekeeping nit, not blocking.

## 24h watch checklist (fires ~22:45 MDT 2026-06-23 / ~04:45 UTC 2026-06-24 — ~24h after smoke #2)

Invariants to verify:

1. **Every successful outbound-pack run lands exactly one Deliverable.**
2. **No double-writes.**
3. **`warnings` shape stays consistent (list with `{type, message}` entries; never `None`, never wrong type).**
4. **Drift-keyword false-positive rate stays at 0 on metadata-only mentions.**

```bash
# Invariant 1: successful outbound runs land deliverables (1.0 ratio)
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution
from core.models_deliverables import Deliverable
from datetime import timedelta
from django.utils import timezone
cutoff = timezone.now() - timedelta(hours=24)
co_completed = AgentExecution.objects.filter(
    owner_agent='CampaignOrchestratorAgent',
    status='completed',
    created_at__gte=cutoff,
).count()
co_outbound_deliverables = Deliverable.objects.filter(
    agent_name='CampaignOrchestratorAgent',
    category='Outbound',
    created_at__gte=cutoff,
).count()
print(f'CampaignOrchestrator completed runs (24h): {co_completed}')
print(f'Outbound deliverables (24h):              {co_outbound_deliverables}')
# Note: ratio depends on how many runs were outbound-mode vs legacy.
# Check AgentExecution.input_data['context'].get('mode') for the subset.
"

# Invariant 2: no per-execution duplicates
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_deliverables import Deliverable
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
cutoff = timezone.now() - timedelta(hours=24)
dupes = (Deliverable.objects.filter(
    agent_name='CampaignOrchestratorAgent',
    category='Outbound',
    created_at__gte=cutoff)
    .values('parent_execution_id').annotate(c=Count('id')).filter(c__gt=1))
for d in dupes:
    print(f'POSSIBLE DUPE per exec: {d}')
print('(no output above = no duplicates)')
"

# Invariant 3: warnings list shape is consistent
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution
from datetime import timedelta
from django.utils import timezone
cutoff = timezone.now() - timedelta(hours=24)
for rec in AgentExecution.objects.filter(
    owner_agent='CampaignOrchestratorAgent',
    created_at__gte=cutoff,
).order_by('-created_at')[:20]:
    od = rec.output_data or {}
    w = od.get('warnings', '<MISSING>')
    deliv_id = od.get('deliverable_id', '<MISSING>')
    print(f'{rec.id} status={rec.status} warnings_type={type(w).__name__} '
          f'len={len(w) if isinstance(w, list) else \"n/a\"} '
          f'deliv_id={deliv_id!r}')
"

# Invariant 4: no spurious 'deliverable_persist_failed' or 'deliverable_gated' WARN
grep -E 'CampaignOrchestrator: outbound pack deliverable persist failed|deliverable_gated|deliverable_persist_failed' celery*.log 2>/dev/null | tail -10
# Expected: empty (or only on the smoke-test deliberate failure rows if any test scenarios were run)
```

## Open follow-ups (deferred to Session 1209 or later)

- **Time-gated (Session 1207 24h watch fires ~03:50 UTC tonight)** — checklist in `SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md` §"24h watch checklist". MIC invariants. Carried into this session.
- **Time-gated (Session 1208 24h watch fires ~03:30 UTC tomorrow 2026-06-24)** — Outbound-pack invariants above.
- **P1: Title normalization at factory level** — both MIC + Outbound deliverables show double-prefixing. Worth one cross-agent factory PR rather than per-agent workarounds.
- **P1: Promote `attempts_used` to canonical top-level `output_data` key** — same pattern as PR #2469's `deliverable_id`/`warnings` lift. Affects MIC + outbound + any future retry-style agents.
- **P2: Add `.gitignore` entry for `.obsidian/`** — housekeeping nit. Removes the "1 uncommitted change" PR-open warning.
- **P2: Beat schedule for periodic outbound-pack generation?** — Spec says "2 flagship outbound packs per week". Currently the path is only invocable on-demand (Rigby tool call, manual dispatch, or future tool wrapper). Worth a follow-up PR if the cadence becomes desired.
- **P3: Promote the structured warnings convention to additional agents** — Session 1207 P3 carryover. Now extended by Outbound's `length_exceeded` tag. Pattern is generalizable.
- **P3: Optional `generate_outbound_pack` tool wrapper** — Rigby suggested in Q1 design call that an optional dedicated tool (adapter that sets `context['mode']='outbound_pack'`) would support chat-driven invocation. Not added in V1; the keyword + context-mode entries cover deterministic invocation. Worth adding if Chris wants the tool surface for casual Rigby calls.

### Carryover from prior sessions still valid for Session 1209

- **P0** workspace_id hallucination root-cause trace (deliverable `96b6a72a-…`) — guardrail in place via Session 1206 PR #2465; root cause still unidentified.
- **P1** CI lint rule blocking `\.execute\(` outside `core/agents/` (deliverable `180f4e9f-…`).
- **P1** Layer 1 dashboard refresh — Wakeup Week dispatches have now generated real evidence including MIC + Outbound deliverables.
- **P1** Session 1206 24h watch (already fired) — verify result.
- **P1** Phase B.1 24h watch (already fired ~14:48 UTC) — verify result.
- **P2** TheOdds API key renewal (Chris-owned, billing-gated).

Full priority table lives in [`00-START-NEXT-SESSION.md`](../../00-START-NEXT-SESSION.md) §"Pick this session".

## Design decisions captured in-session

Rigby's design pings on `pa-2d74e36cc3a04787` produced two key choices worth preserving:

### Q1 — Entry point precedence (Rigby answer: option (c) with strict order)

1. **`context['mode'] == 'outbound_pack'`** — deterministic override. Beat schedulers, ops dispatches, and explicit Rigby tool calls use this. No reliance on LLM routing.
2. **Narrow keyword trigger** — covers the "human typed the thing" case. Tightened to (`"outbound pack"`) OR (`"$2k"` AND `"automation sprint"` AND outbound-ish token from `cold`/`dm`/`email`/`outreach`). The outbound-ish token guard came from Rigby's caution about pricing-discussion false positives.
3. **Fall through to legacy pipeline** otherwise.

Rigby's exact words: *"Your whole goal is 'always ONE deliverable, no drift.' [...] keep the canonical path centralized."*

### Q2 — JSON-mode strategy (Rigby answer: option (a))

`response_format={'type':'json_object'}` on `gpt-5-mini` for all 3 attempts. Rigby's exact reasoning: *"If you spend retries just fighting JSON formatting, you'll burn attempts that should be used to fix semantic validation issues (missing segments, missing message types, etc.). JSON-mode dramatically reduces 'wrapped in markdown / stray commentary / trailing commas' failure modes."*

Rigby explicitly declined option (c) (full Structured Outputs with the §3 schema) as premature: *"It's strongest, but it's more integration surface + you'll inevitably tweak the schema during rollout. Start with JSON-mode + your validator."*

### Insertion-point stamp (Rigby's second message on the thread)

Rigby confirmed the short-circuit goes **outside** the existing `time_travel_session('campaign_orchestration', ...)` block — after `_current_*` context capture but before the legacy `with`. Rationale: outbound runs get their own `time_travel_session('outbound_pack_generation', ...)` for cleaner audit/telemetry filtering.

She also stamped the "ONE place that calls `_save_to_deliverable`" invariant: *"To support the 'ONE combined deliverable' invariant, make `_execute_outbound_pack()` the only place that calls `_save_to_deliverable()` in this mode, and ensure the outer `execute()` does not run any post-phases after it returns."*

### §4.2 drift-scan scope correction (caught by pure-helper smoke pre-PR)

Original implementation flattened the whole payload JSON and substring-scanned for drift keywords. Failed on a known-valid payload because `global.do_not_generate=["blog posts","thumbnails","images"]` is the guardrail block — its presence is correct and required. Refactored to `_collect_outbound_message_strings()` which collects only the strings the outbound recipient would actually read. Exclusions: `do_not_generate`, `compliance_notes`, `personalization_tokens`, `icp_assumptions`, `segment_key`.

This is the kind of bug pure-helper smoke catches but a single live LLM dispatch would not — the LLM doesn't include drift words in its outputs typically. Worth keeping the smoke pattern for future agent-validator work.
