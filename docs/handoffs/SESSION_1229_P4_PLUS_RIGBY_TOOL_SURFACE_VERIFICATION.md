# Session 1229 — P4 Semantic Research Title + Session 1227 Stack Admin-Merge Sweep + Rigby Tool-Surface Verification Arc

**Status:** Seven-PR session — closed Session 1228 carryover P4 (semantic research title helper, the upstream side of the `TEMPLATE_LEAK_TITLE_TOKENS` reactive gate), then admin-merged Rigby's entire Session 1227 deliverable_tool stack (5 PRs that had been auto-closed when bases were deleted — recreated against `main` in order with mostly DOC-AUTOGEN + additive schema/enum conflicts), then ran an end-to-end Rigby tool-surface verification arc on a fresh PA conversation to confirm every new addition is wired and working.

**Date:** 2026-06-24 (UTC).
**Active conversation:** rotated mid-session `pa-08bdd7c9b348415a` → `pa-4086552cdc9840e9`. Old conv carried Sessions 1226-1229 (33 turns / 16.5k tokens / 11.9h, score 35 at rotation, strongly_recommend_fresh). New conv titled "Session 1229 — tool-surface verification arc".
**Prior session:** [`SESSION_1228_AUTOFILL_SWEEP_PLUS_BEAT_TZ_FIXES.md`](./SESSION_1228_AUTOFILL_SWEEP_PLUS_BEAT_TZ_FIXES.md).
**Next session entry point:** Session 1230 — see `00-START-NEXT-SESSION.md` "FIRST THING Session 1230".

## TL;DR

Three arcs, seven PRs, one PA conversation rotation. Arc 1 closed P4: built `build_semantic_research_title()` helper next to the `TEMPLATE_LEAK_TITLE_TOKENS` gate it replaces as primary defense, wired into 5 caller sites across `research_agent.py` (3) and `customer_research_agent.py` (2). Arc 2 admin-merged Rigby's Session 1227 stack (`#2562`, `#2574`-`#2577`) — four of them had been auto-closed when GitHub deleted the parent branch during the upstream merge; recreated each in order against `main` with merge conflicts resolved (DOC-AUTOGEN `docs/INDEX.md` + additive schema/enum/handler entries). Arc 3 verified the full new tool surface end-to-end via Rigby on a fresh conversation: visibility family (show_all / has_initiative / applied_filters / full_by_agent), duplicates action, normalize action (both safety gates), agent dispatch + P4 confirmation, claude_code_tool via OpenAI fallback. Final Makefile fix made the fallback env var persist across `make celery` bounces.

All 7 PRs admin-merged the same UTC day on Chris's session authorization. CI billing still failing — same Chris-side carryover from Sessions 1223-1228.

## Session Manifest

### PRs merged (7 total)

| # | Title | What |
|---|---|---|
| **#2573** | `fix(session-1229): semantic research title — close upstream prompt-leak gate (P4)` | New `core/services/deliverable_factory.build_semantic_research_title()` helper. 4-step resolution (`## Research Topic` section → clean `task` → `topics_detected` fallback → `"brief"`). Always strips `[User Context: …]` tail, normalizes whitespace, truncates at word boundary at 80 chars, appends `— YYYY-MM-DD`. Five caller sites collapse to one `semantic_title` variable: 3 in `research_agent.py` (`_share_knowledge` title, content H1, `_save_to_deliverable` title) + 2 in `customer_research_agent.py` (`prefix='Customer Research'`). `TEMPLATE_LEAK_TITLE_TOKENS` gate intentionally preserved as safety net. 14 new tests. |
| **#2562** | `feat(session-1227): deliverable_tool visibility — has_initiative autofill safety + show_all + applied_filters + full_by_agent` | Rigby's PR1, admin-merged first. Conflict: only `docs/INDEX.md` (DOC-AUTOGEN, regenerated). |
| **#2574** | `feat(session-1227): deliverable_tool first-class duplicates action (reopens #2563)` | Originally `#2563`; auto-closed when `#2562`'s base branch was deleted during admin-merge. Same head branch, rebased onto fresh main. Conflict: `pa_tool_schemas.py` additive entries (group_by, min_count, window_days, exclude_archived) + INDEX.md. |
| **#2575** | `feat(session-1227): deliverable_tool set_status — surgical, audited completed↔ready flip (reopens #2564)` | Originally `#2564`; same auto-close pattern. Conflict: schema entries (set_status enum + description + reason field) + handler enum (ACTION_MAP `set_status`) + INDEX.md. Adds 129-line `set_status` handler in `td_handlers_agents.py`. |
| **#2576** | `feat(session-1227): deliverable_tool normalize — dry-run alias-map sweep (reopens #2565)` | Originally `#2565`; same pattern. Three conflicts: schema (normalize enum + description + field arg) — note: dropped HEAD's duplicate `dry_run`/`confirm` declarations since Session 1228 PR-A had already added them for bulk_archive/cleanup. Handler enum + INDEX.md. Adds 129-line `normalize` handler + new module `core/services/deliverable_aliases.py` as canonical source. |
| **#2577** | `docs(session-1227): close handoff doc (reopens #2566)` | Slimmed-down reopen. Original `#2566` would have written a Session 1228 start-here (now historical). This version keeps only the Session 1227 handoff doc + INDEX.md regen. |
| **#2578** | `fix(session-1229): code_jobs worker fallback env var + pa_local.sh pin rotation` | Two coupled local-dev infra fixes. Makefile: adds `CLAUDE_CODE_ENGINE_PROVIDER=openai` to the code_jobs worker env preamble so the PR #2556 OpenAI fallback persists across `make celery` bounces (without it the engineer defaults back to Anthropic and hits "credit balance too low" 400 — verified during the Session 1229 Step 5 retry). `tools/pa_local.sh`: rotates pin to `pa-4086552cdc9840e9` + retires `pa-08bdd7c9b348415a` to the historical-pins paragraph. |

## Arc 1 — Session 1229 P4 close (PR #2573)

### The bug

Audit deliverable `e2964e4a-…` §4.4 P1 carried Sessions 1226 → 1227 → 1228 without closure. The token gates at `core/services/deliverable_factory.py:157` (`TEMPLATE_LEAK_TITLE_TOKENS`) were the *symptom* — every new leak pattern that ResearchAgent emitted required another entry in the token tuple. PR #2557 added the 5th token (`'this topic using external sources'`) at Session 1226 close; audit explicitly recorded the gate as reactive whack-a-mole.

Root cause: `core/agents/research_agent.py:1103` built titles with `title=f"Research: {task[:100]}"`. When `task` was a clean user query, the title was fine. When `task` was a leaked Stage-1 prompt body (from `core/tasks_initiatives.py:2735` dispatch), the title became the literal first-100-chars of the prompt body — including `"BINDING DIRECTIVE"` / `"EXTERNAL sources"` / `"DO NOT use query_internal_data"`. Audit found 32 rows with the same leaked title; 28 of them created in the last 7 days at audit time.

Same class of bug at three other sites in the same agent:
- `:1071` — `_share_knowledge` title with `task[:60]`
- `:1090` — content H1 `# Research: {task}\n` (full task body dumped)
- `:1103` — `_save_to_deliverable` title with `task[:100]`

And two parallel sites in `core/agents/business/customer_research_agent.py`:
- `:1115` — `_save_to_deliverable` title with `task[:80]`
- `:1127` — `_share_knowledge` title

### The fix

New helper at `core/services/deliverable_factory.py`:

```python
def build_semantic_research_title(
    task: str,
    *,
    prefix: str = 'Research',
    topics_detected: Optional[Iterable[str]] = None,
    max_topic_chars: int = 80,
    today: Optional[date] = None,
) -> str:
    """..."""
```

Resolution order:

1. **Extract `## Research Topic` section** if `task` is a Stage-1 prompt body that includes it (the current `tasks_initiatives.py:2735` prompt shape).
2. **Else if `task` doesn't look templated** (no marker from `_PROMPT_BODY_MARKERS`), use it directly.
3. **Else fall back to `topics_detected[:3]`** joined with `· ` (older Session-923 prompt format that had no `## Research Topic` block but did have `EXTERNAL sources`).
4. **Else default to `"brief"`** (last-resort).

Always strips the `[User Context: …]` tail (added by `research_agent.py:780` user-context augmentation), normalizes whitespace, truncates at word boundary at `max_topic_chars` (default 80), appends ` — YYYY-MM-DD` suffix for cross-day uniqueness (the audit cluster surfaced 32 identical titles; the suffix bounds duplication to one per day per topic).

`prefix` argument lets `CustomerResearchAgent` reuse with `prefix='Customer Research'`.

### Verification

14 new tests in `core/tests/test_deliverable_factory_semantic_research_title.py` across 3 classes (happy path, prompt-body leak variants including the exact 32-row audit cluster, edge cases). Live shell smoke confirmed both real prompt shapes produce semantic titles.

Live verification at Session 1229 close (Arc 3 Step 4): Rigby dispatched `run_agent agent_name=ResearchAgent task='3-sentence summary…'` → resulting `Deliverable.title` was `'Research: 3-sentence summary of the top 3 open-source LLM releases in June 2026 — names — 2026-06-24'`. Exact semantic-helper pattern. NOT the leaked form.

## Arc 2 — Session 1227 stack admin-merge sweep (PRs #2562, #2574-#2577)

Chris authorized admin-merging the Session 1227 stack (Rigby's work, intentionally pending Chris's nod per Session 1228 start-here). Stack was 5 PRs: `#2562` → `#2563` → `#2564` → `#2565` → `#2566`, each stacked on the previous branch.

### The unexpected close-cascade

Standard `gh pr merge --admin --delete-branch` on `#2562` succeeded — but **also auto-closed `#2563` because its base branch was deleted**. GitHub's default behavior: when a base branch is deleted, child PRs auto-close. Cannot reopen a closed PR whose base branch no longer exists (`gh pr reopen` fails with "Could not open"). Cannot retarget the base (`gh pr edit --base main` fails with "Cannot change the base branch of a closed pull request").

Cascading: merging `#2562` closed `#2563`. Merging `#2574` (new PR replacing `#2563`) closed `#2564`. Same chain through `#2565`, `#2566`.

### The recreation pattern

For each closed PR, the recipe was:

1. Check out the original head branch (still on remote).
2. `git merge origin/main` — surfaces conflicts.
3. Resolve conflicts. The recurring shape:
   - `docs/INDEX.md` — DOC-AUTOGEN. `git checkout --theirs` + regenerate via `python manage.py build_docs_index`.
   - `pa_tool_schemas.py` — additive enum + property entries. Keep HEAD's additions; for `#2576` had to also drop HEAD's `dry_run`/`confirm` declarations that Session 1228 PR-A had already added on main.
   - `td_handlers_agents.py` — additive `elif action == 'X':` handler blocks. Keep HEAD entirely.
   - `td_handlers_content.py` — additive `ACTION_MAP` dict entries. Keep HEAD.
4. Stage, commit the merge, push.
5. Open a NEW PR against `main` with a `(reopens #NNNN)` title suffix.
6. Admin-merge with `--delete-branch`.

### Verification through the chain

After each merge, ran a cross-feature test sweep to confirm nothing regressed. By the time #2577 landed:
- 68/68 tests passed across `test_deliverable_factory_semantic_research_title`, `test_deliverable_tool_has_initiative_filter`, `test_deliverable_tool_duplicates`, `test_deliverable_tool_set_status`, `test_deliverable_tool_normalize`.
- The 3 fail + 15 err in the broader 111-test sweep reproduce on clean main (stashed + retested) — pre-existing `Deliverable provenance missing for non-PA agent` from Session 1199 PR-D contract, unrelated.

## Arc 3 — Rigby tool-surface verification on fresh conv

Chris's framing: *"the goal is for Rigby to be able to do it; you can verify it for her but she needs to be able to do it, this includes calling all of her tools, dispatching Agents, etc."* Classic Session 1227 collaboration shape ratified — Claude directs, Rigby executes, Claude verifies via ORM.

### Pre-flight

Workers had started yesterday at 23:19 local. The 7 PRs landed today between 17:11-19:11 UTC. Per `feedback_new_shared_task_needs_worker_restart.md` Case 2, modules imported by task body get cached in `sys.modules` at process import time — disk changes don't propagate. Bounced via `pkill -9 -f celery; rm -f .celery*.pid; make celery`. 6 workers + beat back up with new code loaded.

### Conv rotation (Step 0)

First Rigby call: `session_tool action=whoami` + `health_check` + `create_fresh` if health was low.
- `whoami`: `chris token confirmed; conversation_owner_match=true` ✓
- `health_check`: `turn_count=33, score=35, recommendation=strongly_recommend_fresh` (well past threshold)
- `create_fresh`: new `pa-4086552cdc9840e9` titled "Session 1229 — tool-surface verification arc"

`tools/pa_local.sh` repinned to the new conv. The recently-rotated `pa-08bdd7c9b348415a` retired to the historical-pins paragraph (had carried Sessions 1226-1229 — agent_name canonicalization + verifier-loop audit + Session 1227 surface additions stack + Session 1228 LLM-autofill class sweep + Session 1229 P4 close + workers-bounce).

### Step 1 — visibility tool family (PR #2562)

Rigby ran four calls in one turn:

1. `deliverable_tool action=list show_all=true limit=5` → rows + `applied_filters: {has_initiative: skipped, …}` ✓
2. `deliverable_tool action=list has_initiative=true limit=5` → all rows had non-null `initiative_id` ✓
3. `deliverable_tool action=list has_initiative='false' limit=5` (STRING per autofill-safety contract) → all rows had null `initiative_id` ✓
4. `deliverable_tool action=stats full_by_agent=true` → `by_agent_truncated: false`, 33 distinct agent_name values ✓

**ORM cross-check matched exactly**: total=316, has_initiative split 131/185, distinct agents=33, top-5 counts (Rigby:104, ResearchAgent:78, ContentWriterAgent:26, claude-code:21, COOAgent:14) identical.

### Step 2 — duplicates action (PR #2574)

`deliverable_tool action=duplicates min_count=3 window_days=7 limit=10` returned 3 groups. ORM aggregate matched all three counts/timestamps exactly.

Critical signal: **The exact 32-row P4 cluster appears in the duplicates output** — `"Research: This topic using EXTERNAL sources (web_search, spider_query).\nDO NOT use query_internal_dat"` count=32, last_7d=28, all ResearchAgent, status_distribution: blocked:31 + archived:1. Cluster #2 in the same shape: 9-row `"Research: This topic to advance the initiative.\n\nBINDING DIRECTIVE…"`, all archived. Both should stop growing now that PR #2573 is live in workers (Step 4 confirms).

**Side discovery (followup for next session):** Cluster #3 — `"COO Analysis: You are running the daily COO operations diagnostic. The threshold gate has trip"` count=6, last_7d=5, COOAgent. **Same bug class as P4 but in a different agent.** COOAgent has the same `task[:N]` f-string title build. `build_semantic_research_title(prefix='COO Analysis')` is reusable; small follow-on PR.

### Step 3 — normalize action (PR #2576)

Two-call gate verification:

**A) Dry-run preview:** `deliverable_tool action=normalize field=agent_name dry_run=true show_all=true` → previewed 0 changes for both alias mappings (`rigby → Rigby: 0`, `ClaudeCode → claude-code: 0`). Confirms PRs #2559 + #2560 already canonicalized history. ORM cross-check: 0 rows still hold the old aliases.

**B) Belt-and-suspenders gate verify:** Two-layer defense surfaced:

- **First call** `dry_run=false` (no `show_all`, no `confirm`) → rejected at the **scope-safety layer**: "normalize requires either workspace_id (default scope) or show_all=true (explicit global sweep)."
- **Second call** `dry_run=false show_all=true` (still no `confirm`) → handler **silently downgrades to dry-run** + emits warning `"Preview (write requires both dry_run=false AND confirm=true): …"` Friendlier than hard reject; mutation still blocked.

Both layers do exactly what the contract docs say.

### Step 4 — agent dispatch + P4 verification

`run_agent agent_name=ResearchAgent task='3-sentence summary of the top 3 open-source LLM releases in June 2026 — names, parameter counts, primary differentiator'` (async). Returned `task_id=c20b51e5-8b07-48d4-9aa1-5a12ec44b9b8`.

75 seconds later: AgentExecution `23b8fdaf-521b-4ee4-a360-0fe1e7a10fe7` completed. Agent emitted a `BLOCKED ON:` synthesis because spider evidence cards were retail deals + SEC filings, no LLM news — but the execution itself worked end-to-end.

**P4 verified live.** Resulting Deliverable:
```
id=54bd71f1-41f1-44d1-8497-55ae1fc2cc6c
title='Research: 3-sentence summary of the top 3 open-source LLM releases in June 2026 — names — 2026-06-24'
status=blocked
```

Exact semantic-helper pattern: `task` had no template markers → used directly → truncated at word boundary at 80 chars → date suffix appended. Not the leaked form. `build_semantic_research_title()` is doing its job in workers.

### Step 5 — claude_code_tool via OpenAI fallback (PR #2556 + #2578)

First two dispatches (`6b6633a4`, `cc3feb6e`) both `SUCCESS`-d in celery in <1s — too short for real work. Worker log revealed the cause: both hit `POST https://api.anthropic.com/v1/messages "HTTP/1.1 400 Bad Request"` with credit-exhausted error. The PR #2556 OpenAI fallback path was NOT active because `make celery` never set `CLAUDE_CODE_ENGINE_PROVIDER=openai` on the code_jobs worker line.

Manually restarted the code_jobs worker with the env var. Retry: `2b796e7b-85c9-469e-8924-b857bc69d2b1`. CeleryTaskEvent SUCCESS dur=34.18s, real work. Worker log shows `[ClaudeEngineer:openai]` across 12 OpenAI `/v1/chat/completions` iterations, result envelope `provider: 'openai'`. Fallback verified live.

**Behavioral delta worth flagging (followup):** the engineer ran 12 `read_file` iterations on a trivial line-count request, then concluded with `"I'm ready to make the change, but I don't yet know what you want me to do. Could you please clarify the engineering task?"` instead of answering the trivial question. Rigby's fix proposal: tighten system prompt with a `READONLY_REQUEST=true` mode for tasks answerable via repo scans + add a contract test asserting the final assistant message contains the requested deliverable shape. Separate from infra.

### Step 5 followup — Makefile patch (PR #2578)

`make celery` had to be updated to persist the fallback across worker bounces. Single line addition (`CLAUDE_CODE_ENGINE_PROVIDER=openai`) on the code_jobs worker preamble, with a comment tagging the line as REMOVE-ON-CREDIT-REFILL and pointing to the one-liner revert. Bundled with the `pa_local.sh` conv rotation in PR #2578.

## Behavioral invariants (post-merge)

1. **ResearchAgent + CustomerResearchAgent titles are semantic, not leaked.** `build_semantic_research_title()` is the primary defense; `TEMPLATE_LEAK_TITLE_TOKENS` gate remains as safety net for any future caller that bypasses the helper.
2. **`deliverable_tool` visibility surface** echoes `applied_filters` on every list call. `has_initiative` autofill safety is enforced (Python bool false is no-op autofill; explicit `'false'` string is the filter sentinel; truthy enables the with-initiative filter).
3. **`deliverable_tool.duplicates`** returns audit-ready group shapes (`count`, `first_created_at`, `last_created_at`, `last_7d_count`, `agent_name_distribution`, `status_distribution`) with `applied_filters` echo.
4. **`deliverable_tool.set_status`** only supports `completed↔ready` transitions; flips emit a `DeliverableEvent` with actor + trace_id + reason; `completed→ready` requires non-empty `reason`.
5. **`deliverable_tool.normalize`** requires both `dry_run='false'` AND `confirm=true` to apply. Scope safety: requires `workspace_id` OR `show_all=true` before the mutation gate even fires. Write without confirm silently downgrades to dry-run + warning.
6. **`claude_code_tool`** runs via OpenAI gpt-5-mini fallback path when `CLAUDE_CODE_ENGINE_PROVIDER=openai` is set in the code_jobs worker env. `make celery` now persists this env var across bounces.

## Rollback levers per change

| Change | Disable / revert |
|---|---|
| PR #2573 P4 helper | Revert the imports in `research_agent.py:38` and `customer_research_agent.py:42`, restore the 5 `task[:N]` f-string title sites. `TEMPLATE_LEAK_TITLE_TOKENS` gate still catches anything that slips through. |
| PR #2562 has_initiative autofill safety | Edit `td_handlers_agents.py` filter block to revert to `is not None`. Schema still documents the new contract; remove the doc string update for full revert. |
| PR #2574 duplicates action | Remove the `'duplicates': 'duplicates'` ACTION_MAP entry in `td_handlers_content.py` + the `elif action == 'duplicates':` handler block in `td_handlers_agents.py`. |
| PR #2575 set_status action | Same shape — remove the ACTION_MAP entry + the 129-line handler block. |
| PR #2576 normalize action | Same shape — remove ACTION_MAP + 129-line handler block. `core/services/deliverable_aliases.py` can stay (re-exports from `deliverable_factory.py` for backward compat). |
| PR #2578 Makefile env var | Single-line revert: delete `CLAUDE_CODE_ENGINE_PROVIDER=openai \` from Makefile line ~317. Engineer immediately defaults back to Anthropic on next worker bounce. Use when Anthropic credits return. |

## 24h watch checklist

```bash
# 1. P4 holding — the two leak clusters should stop growing
.venv/bin/python manage.py shell -c "
from core.models_deliverables import Deliverable
for t in [
    'Research: This topic using EXTERNAL sources (web_search, spider_query).\nDO NOT use query_internal_dat',
    'Research: This topic to advance the initiative.\n\nBINDING DIRECTIVE: Your output must directly advance',
]:
    qs = Deliverable.objects.filter(title=t)
    print(f'{t[:50]}... | count={qs.count()}')
"
# Expected: counts unchanged from Session 1229 close baseline (32 and 9 respectively).

# 2. COOAgent leak — does it keep growing post-Session-1229-restart?
.venv/bin/python manage.py shell -c "
from core.models_deliverables import Deliverable
qs = Deliverable.objects.filter(title='COO Analysis: You are running the daily COO operations diagnostic. The threshold gate has trip')
print(f'COOAgent leak count={qs.count()} last={qs.order_by(\"-created_at\").first().created_at if qs.exists() else None}')
"
# Expected: count growing daily — confirms the followup PR is needed.

# 3. claude_code_tool via OpenAI fallback — no Anthropic 400 in worker log
grep -E "credit balance too low|api\.anthropic" celery-code-jobs.log | tail -5
# Expected: empty (after Makefile patch, no more Anthropic calls from this worker).
```

## Session 1230 carryover

1. **COOAgent prompt-body title leak** (NEW — Session 1229 discovery). Same bug class as P4 #2573 but in COOAgent. Apply `build_semantic_research_title(prefix='COO Analysis')` at the COOAgent `_save_to_deliverable` call site. Small follow-on PR. 6-row cluster currently, 5 in last 7d; will keep growing until fixed.
2. **Engineer OpenAI behavioral delta** (NEW — Session 1229 discovery). Engineer on OpenAI fallback path runs 12 read_file iterations on trivial requests then asks for clarification instead of answering. Rigby's fix: `READONLY_REQUEST=true` mode + final-message contract test. Separate from infra.
3. **Audit deliverable `e2964e4a-…` F3 amendment** (NOW UNBLOCKED — PR #2562 landed). Append addendum noting actual cause (GPT-5.2 autofilling `has_initiative=False` over old `is not None` gate) + reference PR #2562. Trivial via `deliverable_tool action=update`.
4. **Calendar-driven items**:
   - Outreach beat first-fire verification (2026-06-25 13:30 UTC) — Session 1228 carryover.
   - Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC) — Session 1228 carryover.
5. **Anthropic credit refill** (Chris-side) — when this lands, `unset CLAUDE_CODE_ENGINE_PROVIDER` is a one-line Makefile revert. Until then, fallback is the path.
6. **CI billing fix** (Chris-side) — same carryover thread from Sessions 1223-1228.
