# Session 1230 — Diagnostic-Family Leak Close + Audit F3 Amendment + Engineer Request-Mode Contract

**Status:** Four-PR session — closed Session 1229 carryover P1 (COOAgent prompt-body title leak), P1b (CTO/Trend/TrendBreak sibling wiring), P2 (Audit `e2964e4a-…` §4.8 F3 amendment), and P4 (Engineer OpenAI behavioral delta + clarification-stall contract). Plus one tracking deliverable filed for a `deliverable_tool.append` audit-trail gap discovered mid-session.

**Date:** 2026-06-24 (UTC).
**Active conversation:** `pa-4086552cdc9840e9` (no rotation this session — continuing the Session 1229 thread; ~30 turns added on top of the rotated baseline; still well under fresh-recommendation threshold).
**Prior session:** [`SESSION_1229_P4_PLUS_RIGBY_TOOL_SURFACE_VERIFICATION.md`](./SESSION_1229_P4_PLUS_RIGBY_TOOL_SURFACE_VERIFICATION.md).
**Next session entry point:** Session 1231 — see `00-START-NEXT-SESSION.md` "FIRST THING Session 1231".

## TL;DR

Two recursion classes closed in one session. **Class 1 — diagnostic-family title leak:** Session 1229's `duplicates` audit surfaced a 6-row `COOAgent` cluster with title `"COO Analysis: You are running the daily COO operations diagnostic. The threshold gate has trip"`. Same bug class as Session 1229 PR #2573 (Research / CustomerResearch) — the agent's `f"<Label>: {task[:80]}"` title build leaks prompt bodies when `task` is a scheduled-diagnostic prompt. P1 (#2580) wired COOAgent + extended `_PROMPT_BODY_MARKERS` to catch the shared diagnostic opener (`"You are running the daily"` + `"The threshold gate has tripped"`). P1b (#2581) wired the three sibling callsites (CTOAgent + TrendAnalysisAgent ×2 + TrendBreakDetectorAgent) with a source-level guard test that locks the wiring against future regressions. **Class 2 — Engineer OpenAI behavioral delta:** Session 1229 Step 5 found gpt-5-mini on the OpenAI fallback path stalled with `"I'm ready to make the change, but I don't yet know what you want me to do. Could you please clarify the engineering task?"` on a readonly line-count task. P4 (#2582) split the single `SYSTEM_PROMPT` into `ANSWER_SYSTEM_PROMPT` + `CHANGE_SYSTEM_PROMPT`, added a `request_mode='auto'|'answer'|'change'` kwarg + verb-heuristic dispatcher (`_infer_request_mode`), and added a clarification-stall contract that retries once with a hardened preamble on answer-mode tasks before flipping the envelope to `status='contract_failure'`. P2 (`deliverable_tool action=append`) appended a §4.8 amendment to audit deliverable `e2964e4a-…` reframing F3's "blocked default filter" symptom as the real cause: GPT-5.2 autofilling `has_initiative=False` over the old `is not None` gate (closed by Session 1227 PR #2562).

All 4 PRs admin-merged the same UTC day on Chris's session authorization. CI billing still failing — same Chris-side carryover from Sessions 1223-1229.

## Session Manifest

### PRs merged (4 total)

| # | Title | What |
|---|---|---|
| **#2580** | `fix(session-1230): COOAgent semantic title — close prompt-body leak (P1)` | COOAgent `_save_to_deliverable` call site at `core/agents/executive/coo_agent.py:303-313` replaces `f"COO Analysis: {task[:80]}"` with `build_semantic_research_title(task, prefix='COO Analysis')`. Helper markers extended in `core/services/deliverable_factory.py:_PROMPT_BODY_MARKERS` with `'You are running the daily'` + `'The threshold gate has tripped'` (covers `coo_daily.py` + `cto_daily.py` + `trend_analysis_daily.py` shared opener). 11 new tests in `test_coo_agent_semantic_title.py` covering clean COO tasks, the exact audit-cluster shape (regression), CTO + Trend sibling prompt shapes, edge cases. 50/50 suite green. |
| **#2581** | `fix(session-1230): COO siblings semantic title — close prompt-body leak family (P1b)` | Wires the three remaining diagnostic-family callsites: `cto_agent.py:321` (`f"CTO Analysis: {task[:80]}"` → `build_semantic_research_title(task, prefix='CTO Analysis')`), `trend_analysis_agent.py:498` + `:541` (`f"Trend Analysis: {task[:50]}"` → helper with `prefix='Trend Analysis'`, both branches), `trend_break_detector_agent.py:799` (`f"Trend Break Detection: {task[:80]}"` → helper with `prefix='Trend Break Detection'`). New `test_diagnostic_family_semantic_title_wiring.py` source-level guard test (3 contract tests: import present, helper called with correct prefix, no `title=f"<Label>: {task[:N]}"` leak pattern). Regex scoped to `title=` kwarg position so `_thinking()` `reasoning=f"Received task: {task[:100]}"` logging strings are not flagged (caught a false positive on first run; tightened). 53/53 suite green. |
| **#2582** | `fix(session-1230): engineer request_mode + clarification-stall contract (P4)` | `core/services/claude_code_engineer.py` — split `SYSTEM_PROMPT` into `ANSWER_SYSTEM_PROMPT` (explicit "do not ask for clarification", "do not propose code changes", "format IS the contract") + `CHANGE_SYSTEM_PROMPT` (prior prompt retitled with explicit "REQUIRES CODE CHANGES" framing). Added `_SYSTEM_PROMPT_BY_MODE`, `_CHANGE_VERBS` (18 verbs), `_CLARIFICATION_STALL_MARKERS` (8 substrings), `_infer_request_mode(task)`, `_looks_like_clarification_stall(text)`. `execute_engineering_task` takes `request_mode='auto'` arg; resolves via heuristic when 'auto', explicit overrides bypass. On answer-mode tasks, post-loop `_looks_like_clarification_stall` check triggers single retry with hardened preamble; if retry also stalls, envelope flips to `status='contract_failure'`. Plumbed through `core/tasks.py:claude_code_engineer_task`, `pa_tool_schemas.py:claude_code_tool` (schema enum add), `td_handlers_codejobs.py:_handle_claude_code` (read + normalize + forward). 24 new tests in `test_engineer_request_mode.py` (heuristic edge cases, stall detector, prompt selection, dispatch resolution, retry contract with `_stub_openai_client` mock helper). 32/32 suite green. Anthropic-path also gets system_prompt selection; retry contract is OpenAI-only until Anthropic credits return + A/B is done. |

### Deliverable updates (in-session)

| Action | Deliverable | What |
|---|---|---|
| **append** | `e2964e4a-08e9-4ff1-bc01-7fe3adb5a99c` (Audit) | §4.8 F3 Amendment — reframes F3's "blocked default filter" symptom as the real cause: GPT-5.2 autofilling `has_initiative=False` over the old `is not None` gate. Cites PR #2562 (Session 1227 fix). 2,518 chars appended (26,465 → 28,983). ORM-verified seam at offset 26,472. |
| **create** | `61f4312b-9f54-447e-abf2-641e082386ba` (Platform Bugs) | Tracking deliverable for `deliverable_tool.append` audit-trail gap discovered during P2: append mutates `content` + `content_length` but does NOT bump `updated_at`. Severity P3, suspected fix in `td_handlers_*` `append` handler. |

### Rigby live verifications (all 4 dispatches)

| Dispatch | Mode | Status | Result |
|---|---|---|---|
| **`fcdbd982-…`** (P1 verify) | n/a (pre-P4) | SUCCESS 67.7s | New COOAgent deliverable `461eeb7c-…` titled `"COO Analysis: Brief — 2026-06-24"` — semantic, no leak. Comparison: pre-merge `b460ec0b-…` titled `"COO Analysis: You are running the daily COO operations diagnostic. The threshold gate has trip"`. Old leaked rows: 5 / Last 7d; new shape: 1. ✓ |
| **`a609214b-…`** (P1b verify) | n/a (pre-P4) | SUCCESS 33.6s | New CTOAgent deliverable `863d776b-…` titled `"CTO Analysis: Brief — 2026-06-24"`. CTO had no active cluster pre-merge (markers were defensive). ✓ |
| **`ea9a89aa-…`** (P4 verify, smoking gun) | `request_mode=auto` → resolved `answer` | SUCCESS 92.9s | Heuristic resolved auto → answer for the Session 1229 line-count task shape. Engineer produced direct structured analysis. **Zero clarification stall.** Retry contract did not fire (primary fix was sufficient). ✓ |
| **`962b4f84-…`** (P4 verify) | `request_mode=answer` (explicit) | SUCCESS 98.6s | Direct structured answer for the readonly docstring lookup. ANSWER_SYSTEM_PROMPT selection verified in worker log `[ClaudeEngineer] dispatch: requested_mode=answer resolved_mode=answer`. ✓ |
| **`7e6c267e-…`** (P4 verify) | `request_mode=change` (explicit) | SUCCESS (>120s) | Thorough planning response with three explicit followup offers. **NO branch created, NO PR opened, NO `write_file`/`git_command` tools invoked** — "don't actually do it" was respected. Change-mode contract held. ✓ |
| **`38c2424b-…`** (P4 verify, bundled bonus) | `request_mode=answer` (explicit) | SUCCESS 53.8s | Direct answer (engineer searched and reported "not found"; engineer's `/tmp/engineer-workspace/` git clone is stale and didn't have `build_semantic_research_title` shipped today in #2573 — see "Workspace staleness" under followups). Stall contract held — direct answer, not a clarification request. ✓ |

ORM cross-checks ran on `b460ec0b/461eeb7c` (COO) + `863d776b` (CTO) + `e2964e4a` (audit append, §4.8 header at offset 26,472) + `61f4312b` (updated_at flag deliverable) + worker `celery-code-jobs.log` (heuristic resolution lines, zero `clarification stall` log lines, zero `retry` log lines).

## Operational Invariants (post-merge)

1. **Diagnostic-family title leak class is closed.** Every known callsite that receives a `"You are running the daily <X> diagnostic"` prompt body now uses `build_semantic_research_title(task, prefix='<Label>')`. Helper markers detect the diagnostic family at the source; `TEMPLATE_LEAK_TITLE_TOKENS` gate at the factory layer remains as a safety net. New COO/CTO/Trend daily fires produce `"<Label>: Brief — YYYY-MM-DD"` (the `_clean_deliverable_title` Step-7 capitalization renders `brief` → `Brief`).
2. **Source-level guard against f-string reintroduction.** `test_diagnostic_family_semantic_title_wiring.py` asserts each rewired file imports the helper, calls it with the correct prefix kwarg, and contains no `title=f"<Label>: {task[:N]}"` leak pattern. Regex scoped to `title=` kwarg position so `_thinking()` `reasoning=` log strings are not flagged.
3. **Engineer `request_mode` contract.** `claude_code_tool` PA tool now accepts `request_mode='auto'|'answer'|'change'`. Default `'auto'` resolves via verb heuristic (`_CHANGE_VERBS`); explicit caller value bypasses heuristic; unknown values warn + fall back. Dispatcher logs the resolution: `[ClaudeEngineer] dispatch: requested_mode=<X> resolved_mode=<Y> task_chars=<N>`. Response envelope echoes `mode`.
4. **Answer-mode clarification-stall retry.** On `request_mode='answer'` tasks (explicit or auto-resolved), post-loop `_looks_like_clarification_stall(final_text)` triggers a single retry with `"READONLY ANSWER TASK — do not ask for clarification..."` preamble prepended to `task_description`. If retry also stalls, envelope flips to `status='contract_failure'` (surfacing the behavioral delta rather than silently posting a stall). Change-mode tasks never trigger retry (legitimate clarification on ambiguous change tasks is correct behavior).
5. **`_clean_deliverable_title` Step-7 capitalization is a known cosmetic pass.** Helper outputs lowercase `'brief'` (line `core/services/deliverable_factory.py:309`); the cleaner's Step 7 (`deliverable_factory.py:549-552`) capitalizes the first character of the post-prefix-strip remainder before reconstruction. Result: `"<Label>: Brief — YYYY-MM-DD"`. Helper-level tests stay correct (test the helper layer); DB-stored titles are semantic + leak-free regardless of casing.

## Rollback / Disable Levers

| Change | Disable lever |
|---|---|
| #2580 helper markers | Revert the two-marker addition in `_PROMPT_BODY_MARKERS` at `core/services/deliverable_factory.py:195-217`; helper falls back to `'brief'` default less aggressively, but the `TEMPLATE_LEAK_TITLE_TOKENS` gate still blocks the resulting rows. |
| #2580 / #2581 wiring | Per-agent revert: swap `build_semantic_research_title(task, prefix='<Label>')` back to `f"<Label>: {task[:N]}"` at the named line numbers. Source-level guard test will fail, alerting on regression. |
| #2582 retry contract | Set `request_mode='change'` on every dispatch (caller-side bypass); change mode never retries. Or comment out the `if (resolved_mode == 'answer' and _looks_like_clarification_stall...)` block at `core/services/claude_code_engineer.py:534-575`. |
| #2582 heuristic | Caller-side bypass: pass explicit `request_mode='answer'` or `'change'` on every dispatch; heuristic only fires on `'auto'` (the schema default). |
| #2582 prompt split | Both prompts share the same `TOOLS` + tool-call loop; reverting to a single prompt is a `_SYSTEM_PROMPT_BY_MODE[<both>] = ANSWER_SYSTEM_PROMPT` or `CHANGE_SYSTEM_PROMPT` edit at module scope. |

## 24h Watch Checklist (copy-paste)

Run any time in the first 24-48h after merge. Each command standalone; no setup.

```bash
# 1. Confirm no new diagnostic-family leak rows are accumulating
.venv/bin/python -c "
import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup()
from core.models_deliverables import Deliverable
for agent in ('COOAgent', 'CTOAgent', 'TrendAnalysisAgent', 'TrendBreakDetectorAgent'):
    leaked = Deliverable.objects.filter(
        agent_name=agent,
        title__icontains='You are running the daily',
        created_at__gte='2026-06-25',
    ).count()
    print(f'{agent}: leaked rows since 2026-06-25 = {leaked}  (expected 0)')
"

# 2. Confirm new semantic-title rows for the diagnostic family
.venv/bin/python -c "
import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup()
from core.models_deliverables import Deliverable
for agent in ('COOAgent', 'CTOAgent', 'TrendAnalysisAgent', 'TrendBreakDetectorAgent'):
    semantic = Deliverable.objects.filter(
        agent_name=agent,
        title__icontains='Brief — 2026',
        created_at__gte='2026-06-25',
    ).count()
    print(f'{agent}: semantic rows since 2026-06-25 = {semantic}  (expected 1/day per active diagnostic)')
"

# 3. Confirm engineer request_mode is being passed through on real dispatches
grep -E '\[ClaudeEngineer\] dispatch:' celery-code-jobs.log | tail -10

# 4. Watch for any clarification-stall retries or contract failures (should be rare)
grep -E '\[ClaudeEngineer:openai\] clarification stall|contract_failure' celery-code-jobs.log | tail -20

# 5. Confirm guard tests still pass (regression sentinel)
.venv/bin/python manage.py test \
  core.tests.test_diagnostic_family_semantic_title_wiring \
  core.tests.test_coo_agent_semantic_title \
  core.tests.test_engineer_request_mode \
  core.tests.test_engineer_openai_fallback \
  -v0 --noinput --keepdb
```

Expected after a clean 24h: zero leaked-shape rows for the four diagnostic-family agents; semantic rows accumulate one per day per fire; clarification-stall retries should be 0 or single-digit (each one is a Rigby-side prompt issue, not a system bug); guard tests stay green.

## Carryover Into Session 1231

### Still Chris-side

- **Anthropic credit refill** at https://console.anthropic.com/billing. One-liner Makefile revert (`unset CLAUDE_CODE_ENGINE_PROVIDER`) when credits land. Once active, A/B the same Session 1229 line-count task on claude-sonnet-4 (Anthropic path) vs the Session 1230 fix on gpt-5-mini (OpenAI path) to confirm the new prompts don't regress the Anthropic-path behavior. If clean, lift the retry contract up out of the OpenAI-only branch so both paths get the same safety net.
- **CI billing** still failing — all 4 Session 1230 PRs admin-merged.

### Calendar items (not due in Session 1230, watch in Session 1231)

- **Outreach beat first-fire verification (2026-06-25 13:30 UTC)** — Session 1228 carryover. PR #2569 corrected the TZ; verify `CeleryTaskEvent.objects.filter(task_name='core.tasks.generate_outreach_drafts_daily').order_by('-started_at').first()` returns SUCCESS dated 2026-06-25. `OutreachDraft.objects.filter(lead_source='opportunity_outreach_seed', created_at__date='2026-06-25').count()` should be 1-5.
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover. PR #2570 changed fire time. Verify `PeriodicTask.last_run_at` reflects 06-26 12:00 UTC + new deliverable created with `status='ready'` or `'preview'` (no auto-publish). After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}`.

### New followups discovered mid-Session 1230

| # | Item | Severity | Notes |
|---|---|---|---|
| **F1** | COOAgent scheduled `'files_generated'` KeyError | High (blocks daily) | Pre-existing bug surfaced during P1 verification. Today's 13:30 UTC scheduled COO dispatch (`f2ecd6f9-…`) failed with `error_message="'files_generated'"`. Manual COO dispatch via Rigby (`fcdbd982-…`) succeeded — so the bug is specific to the scheduled path. Likely in `scheduled_diagnostic_runner.py` or the COOAgent's output-data envelope handling. Worth a focused investigation — daily diagnostic is currently silently failing. |
| **F2** | Meeting-context leak shape (different prompt family) | Low | Spotted on both `COOAgent:9086d485-…` and `CTOAgent:12b24f63-…` titles: `"COO Analysis: As a participant in a technical meeting about \"AC-3 smoke control: empty context"`. One-off shape, not in the duplicates cluster — different prompt template. Helper markers in #2580 don't catch it. Wait to see if it recurs before adding markers; if it becomes a cluster, the fix is one more entry in `_PROMPT_BODY_MARKERS`. |
| **F3** | Engineer workspace staleness | Medium | Engineer's `/tmp/engineer-workspace/` git clone is stale. P4 verification dispatch `38c2424b-…` (build_semantic_research_title docstring lookup) returned "not found" — but the function was shipped today in #2573 and exists at `core/services/deliverable_factory.py:249`. Engineer pointed to `_clean_deliverable_title` as the "similar function" instead. Fix: either auto-pull on dispatch (small overhead), or call `_ensure_git_repo` to update HEAD before each loop. Not a P4 regression — separate workspace-management bug. |
| **F4** | `deliverable_tool.append` audit-trail gap | P3 | See tracking deliverable `61f4312b-…`. `append` action mutates `content` + `content_length` but does NOT bump `updated_at`. Severity is low because the symptom is hidden (`updated_at` queries miss appended content), but the longer it sits the more `updated_at`-based analytics drift. Fix is one-line in the `append` handler in `td_handlers_*`: `save(update_fields=['content', 'content_length', 'updated_at'])`. Same pattern check needed on `prepend` and any other content-mutating actions. |

### Chris-discretion (not on next-session priority list — only if Chris re-prioritizes)

- Fleet sibling apps build-out (7 apps at localhost:8002-8008, no work across 1224-1230).
- Audit #5 (PA tool schemas vs handlers — Δ=43), non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Outreach tone tweaks (Rigby's Session 1225 review) — deferred until ≥10 generates reveal which actually matter.

### Active conversation status

`pa-4086552cdc9840e9` (titled "Session 1229 — tool-surface verification arc"). Session 1230 added ~30 turns on top of the rotated baseline (Session 1229 rotated at score 35). No rotation triggered this session — well under the strong-recommend threshold. Continues into Session 1231 unless Rigby's health check flips during the next session-open `whoami`.

## Authoring Notes

Session 1230 followed the "Claude directs, Rigby executes, Claude verifies" pattern across all 4 PRs. Concrete examples:

- **P1 / P1b code work** — Claude's lane (Rigby has no repo write). Rigby's `duplicates` surfaced the COO cluster at Session 1229 close; Claude wrote the wiring + tests + PRs; Rigby live-verified the post-merge behavior via fresh COOAgent + CTOAgent dispatches.
- **P2 deliverable amendment** — Rigby's lane (deliverable_tool action=append). Claude drafted the §4.8 addendum text (referencing PR #2562 + the memory rule); Rigby executed the append; Claude ORM-verified the §4.8 header landed at offset 26,472 with all three required citations.
- **P4 design call** — Rigby's design judgment was the load-bearing artifact (request_mode kwarg shape, two-prompt split vs branched-prompt, retry-vs-warn vs reject). Claude wrote the code per her design, dispatched her own verification fleet (4 engineer tasks via `claude_code_tool`), and read the post-back bodies via ORM after the worker log confirmed heuristic resolution + zero stalls.

The `deliverable_tool.append` updated_at gap (F4) was discovered during P2 ORM verification — Claude noticed `updated_at` hadn't bumped despite a 2,518-char append; this surfaced as a tracking deliverable in real time so it persists across sessions rather than living in the conversation tail.

The bonus observation that Rigby's "DISPATCH 1" P4 verification task body didn't exactly match Claude's literal request text was not a problem for the contract — the heuristic + prompt selection + no-stall-retry path all held regardless of content correctness. Engineer workspace staleness (F3) is a separate bug class.
