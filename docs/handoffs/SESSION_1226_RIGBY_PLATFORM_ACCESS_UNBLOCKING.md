# Session 1226 — Rigby Platform-Access Unblocking + claude_code_tool Wiring Repair + Verifier-Loop Audit

**Status:** Twelve-PR session — full pivot from outreach/Operator-Edge work to a focused Rigby-access unblocking arc, a deep investigation that root-caused the multi-session `claude_code_tool` dispatch failure as a three-layer wiring break, AND a verifier-loop-pattern deliverables audit that surfaced + shipped fixes for an active prompt-leak and agent_name fragmentation.

**Note on doc shape:** This handoff was originally shipped as v1 (#2555, 5 PRs covered). The v2 update extends the manifest + adds Arc 4 for the verifier-loop audit work that followed close v1.
**Date:** 2026-06-23 (continued from Session 1225 close, same UTC day; into 2026-06-24 UTC).
**Active conversation:** `pa-77bbcd97a625424d` — fresh thread spun mid-Session 1225 after the prior pin hit `suggest_fresh`. Carried Session 1226 from open to close with no rotation.
**Prior session:** [`SESSION_1225_OUTREACH_REFINEMENT_AND_CONVERSATION_ROTATION.md`](./SESSION_1225_OUTREACH_REFINEMENT_AND_CONVERSATION_ROTATION.md).
**Next session entry point:** Session 1227 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1227".

## TL;DR

Session opened pointed at the Session 1225 carryover (Operator Edge Friday-1 prep, outreach beat first-fire watch). Chris pivoted mid-session — after seeing Rigby hit deliverable-query blockers — to a meta-shift: **make Rigby's platform access a top-tier workstream, not a backlog item**, with the framing "the more she can access the platform and the agents, the better the platform will perform."

Five PRs shipped under that rubric, with the last three coming from a single multi-layer investigation:

1. **#2550** — `session_tool action=whoami` closes the conversation-ownership verification gap Rigby filed at Session 1225 close.
2. **#2551** — `deliverable_tool.list` gains `has_initiative` filter + corrected `initiative_id` schema description. Closes the canonical "which of agent X's deliverables are attached to initiatives?" query Chris remembered was blocked.
3. **#2552** — `make celery` starts a local `code_jobs` queue worker. Procfile had a `code-worker` for Railway, but the local Makefile omitted it, so every `claude_code_tool` dispatch since the tool existed had been silently queued forever, no telemetry.
4. **#2553** — local `code_jobs` worker switched to `--pool=solo` after the new prefork worker SIGSEGV-crashed on every fork (macOS-specific, CLAUDE.md-documented).
5. **#2554** — PA dispatcher payload now carries `conversation_id` by default. Closed the autonomous-engineer post-back bug: `_post_to_conversation` was being skipped because `conversation_id=None` was reaching `claude_code_engineer_task`.

The investigation also surfaced **two non-code items** for follow-up:
- **Anthropic credits are exhausted.** Backlog drain showed all 7 historical dispatches got `error 400: "Your credit balance is too low to access the Anthropic API."` Chris-side fix at https://console.anthropic.com/billing.
- **Agent-name normalization drift.** Rigby's first run of the new `has_initiative` filter showed both `claude-code` and `ClaudeCode` spellings in deliverable rows. Fragments any agent-based rollup. New carryover for Session 1227.

GH Actions billing still failing — all 5 PRs admin-merged per existing Chris session authorization.

## Session Manifest

### PRs merged (12 total)

| # | Title | What |
|---|---|---|
| **#2550** | `feat(session-1226): session_tool action=whoami — close ownership-verification gap` | Returns user identity (`user_id`, `username`, `email`, `is_staff`, `is_superuser`) + owner facts on the current or supplied conversation (`conversation_owner_user_id`, `conversation_owner_username`, `conversation_owner_match` bool). 6 unit tests. |
| **#2551** | `feat(session-1226): deliverable_tool.list has_initiative filter + initiative_id schema clarification` | New `has_initiative` boolean filter. `initiative_id` filter had always existed but schema described it as link-only — corrected. Canonical query unlocked: `deliverable_tool action=list agent='ResearchAgent' has_initiative=true`. 6 unit tests. |
| **#2552** | `fix(session-1226): start a local code_jobs worker in make celery` | New `make celery` block + matching `make celery-stop` block for the `code_jobs` queue. Mirrors the Procfile profile. Closed the silent-queue-forever symptom. |
| **#2553** | `fix(session-1226): code_jobs worker pool=solo on macOS (prefork SIGSEGVs)` | Local worker swapped to `--pool=solo`. Procfile stays prefork for Linux/Railway. |
| **#2554** | `fix(session-1226): inject conversation_id into PA tool payloads` | `_build_tool_payload` now `setdefault`s `conversation_id` from `self.conversation_id`. Closes the missing-attribute fallback chain. |
| **#2555** | `docs(session-1226): close — Rigby platform-access unblocking + claude_code_tool wiring repair + 1227 start-here` (v1) | Original close handoff (covered #2550–#2554). |
| **#2556** | `feat(session-1226): claude_code_engineer OpenAI fallback path` | Temporary workaround for exhausted Anthropic credits. `CLAUDE_CODE_ENGINE_PROVIDER=openai` routes the autonomous engineer through `gpt-5-mini` via OpenAI factory with translated tool format. Unset env var to revert when Anthropic credits land. 6 unit tests. |
| **#2557** | `fix(session-1226): close active research-prompt-leak in TEMPLATE_LEAK_TITLE_TOKENS` | Added `'this topic using external sources'` token. Closes audit P0 — 32-row cluster, 28 in last 7d, ResearchAgent. +1 gate test. |
| **#2558** | `chore(session-1226): rotate pa_local.sh pin → pa-08bdd7c9b348415a` | Mid-session rotation after pa-77bbcd97a625424d crossed ~28 turns. New pin verified via `session_tool.whoami`. |
| **#2559** | `fix(session-1226): canonicalize agent_name aliases in core_deliverables` | Migration 0365: `rigby`→`Rigby` (1 row) + `ClaudeCode`→`claude-code` (17 rows). Closes audit F2 history side. 5 tests. |
| **#2560** | `feat(session-1226): agent_name write-time canonicalization in deliverable_factory` | Module-level `_AGENT_NAME_ALIASES` + `_canonicalize_agent_name()` helper applied at the top of `create_deliverable()`. Closes audit §4.4 P1 'Enforcement' bullet — prevents future drift. 10 tests. Lockstep-asserted against migration 0365's `_ALIAS_MAP`. |
| **(this PR)** | `docs(session-1226): close v2 — verifier-loop audit arc + final 1227 start-here` | This update — extends the manifest with #2556-#2560 + new Arc 4 for the audit work + new memory rule on the verifier-loop pattern + Session 1227 first-thing refresh. |

### Carryover items NOT touched this session (intentional)

- Outreach daily beat first-fire watch (scheduled 2026-06-24 13:30 UTC — about 10 hours from session close)
- Operator Edge Friday-1 dry-run check (Friday 2026-06-26)
- Watchdog #5 24-48h re-run from Session 1223
- CI billing (Chris-side)
- Outreach tone tweak nice-to-haves from Session 1225 Rigby tone review
- `research_agent.py:1103` upstream sanitizer (gated on hygiene daily-audit signal)

## The two arcs

### Arc 1 — Rigby blocker inventory + whoami + has_initiative (PRs #2550, #2551)

**Trigger:** Chris noted Rigby had hit a deliverable-related blocker earlier. Pivoted Session 1226 focus to platform-access unblocking.

**Step 1 — Inventory.** Asked Rigby for a full raw dump of blockers (confirmed + suspected), with workarounds + impact. Her response separated cleanly:
- **Confirmed blockers**: `claude_code_tool` dispatch (Session 1225 filed), `whoami`/`conversation.owner` gap (Session 1225 filed).
- **Intentional non-bugs**: daily cap, local-only default, conversation rotation cost.
- **Suspected but unverifiable in this session's context**: deliverable-side errors Chris had referenced earlier (Rigby honestly flagged she couldn't characterize them without a repro).

Chris remembered the specific suspected blocker mid-session: "I asked Rigby what agents' deliverables had initiatives and she said she didn't have the tools to check that." That converted Suspected → Confirmed.

**Step 2 — `whoami` (#2550).** Smallest of the three confirmed items. New `session_tool action=whoami` returns identity + conversation ownership facts. Rigby's verification call on the new conversation: `username: chris, is_staff: true, is_superuser: true, conversation_owner_match: true` — implicit-by-reachability ownership now becomes a tool-surface answer. Tier A item 1 closed.

**Step 3 — `has_initiative` (#2551).** Investigation finding worth preserving:
- `initiative_id` filter on `deliverable_tool.list` had existed since Session 1077.
- `agent` filter on the same had existed too.
- **The schema description showed `initiative_id` ONLY as a parameter for `link_initiative`**, so Rigby couldn't see it was a list filter. Discoverability gap, not capability gap.
- Genuinely missing: a `has_initiative` boolean filter for "does this deliverable have ANY initiative attached?" — the actual canonical-query primitive.

Shipped both: corrected `initiative_id` description + new `has_initiative` filter. Rigby's verification run unlocked the answer Chris had originally asked for — multiple agents (ContentWriterAgent, ResearchAgent, Rigby, claude-code, ClaudeCode) have initiative-linked deliverables; ResearchAgent alone has 53 linked + 25 unlinked.

**Rigby flagged in the same response:** `claude-code` vs `ClaudeCode` agent_name spellings BOTH exist in deliverable rows. Fragments any agent-based rollup. **New Session 1227 carryover** — normalization sweep.

### Arc 2 — `claude_code_tool` dispatch investigation (PRs #2552, #2553, #2554)

**Tier A item 3 — the big one.** Rigby filed this at Session 1225 close as a wiring investigation. Approach: investigate first, surface findings, then code.

**Finding 1 — Architectural mental-model correction (no code change).**

`claude_code_tool` was never designed to bridge to the human-facing Claude Code CLI session. The schema description ("Spawn an autonomous Claude Code engineering session") **reads** like delegation to the same Claude Code instance — but the implementation in `td_handlers_codejobs.py:330` dispatches to `claude_code_engineer_task` (Celery), which calls `execute_engineering_task()` in `claude_code_engineer.py:360`. That function spawns an **independent** Anthropic-API agent running `claude-sonnet-4-20250514`, iterates with codebase tools, and posts the final result back to the PA conversation via `_post_to_conversation()`.

Rigby's "didn't reach Claude Code session" symptom was real, but mis-attributed — the autonomous engineer was supposed to run on its own, not relay to my session. Once I clarified the architecture, the actual broken paths got localized.

**Finding 2 — Queue topology drift (PR #2552).**

`claude_code_engineer_task` routes to queue `'code_jobs'` (per `app.conf.task_routes`). The Procfile defines a `code-worker` process listening on that queue. **The local Makefile `celery` target started workers for `default,agents,content` / `pa` / `long_running,ml` / `broadcast` — but NOT `code_jobs`.**

Consequence: every dispatch since the tool existed went to Redis `code_jobs`, sat there forever, no worker picked it up, no telemetry emitted (no worker = no `CeleryTaskEvent`). Confirmed: `CeleryTaskEvent.objects.filter(task_name__icontains='claude_code_engineer').count()` returned **0 all-time**.

PR #2552 adds the missing local worker block to `make celery`, mirroring the Procfile profile.

**Finding 3 — macOS prefork SIGSEGV (PR #2553).**

The new local worker came up, started consuming the backlog, and SIGSEGV-crashed on every single message:

```
[ERROR/MainProcess] Process 'ForkPoolWorker-N' pid:PID exited with 'signal 11 (SIGSEGV)'
WorkerLostError: Worker exited prematurely: signal 11 (SIGSEGV) Job: N.
```

This is the macOS Celery prefork issue documented in `CLAUDE.md`. `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` in the env doesn't help for the autonomous-agent fork specifically. Fix: `--pool=solo` locally. Procfile stays prefork for Linux/Railway.

PR #2553 makes that swap. Confirmed: 7 backlog tasks (going back to Rigby's original Session 1225 dispatch `0077cd79-…`) ALL transitioned to SUCCESS within 10 seconds of the new worker coming up.

**Finding 4 — Anthropic credits exhausted (Chris-side, not code).**

The SUCCESS transition was Celery-layer. Every actual autonomous run failed inside the engineer with `error 400: "Your credit balance is too low to access the Anthropic API."` The autonomous engineer uses Claude Sonnet via Anthropic, separate from your OpenAI balance (which Chris topped up to $40 in Session 1224 for the outreach work).

No code fix — Chris-side at https://console.anthropic.com/billing. Flagged for Session 1227 verification once credits land.

**Finding 5 — `conversation_id` wiring bug (PR #2554).**

Even on error, Rigby saw no message land back in her chat. Traced via `claude_code_engineer._post_to_conversation`:

```python
if conversation_id:
    _post_to_conversation(conversation_id, error_msg, [], None)
```

Only fires when `conversation_id` is truthy. The `claude_code_tool` handler's auto-inject:

```python
conversation_id = payload.get('conversation_id')
if not conversation_id and hasattr(self, '_conversation_id'):
    conversation_id = self._conversation_id
```

Both branches always miss:
- `payload['conversation_id']` is only present when the LLM explicitly sets it in tool args (it usually doesn't — schema marks it optional).
- `self._conversation_id` is **never set anywhere in the codebase** (I grepped). Same for `self._current_conversation_id` (read by `session_tool whoami` but also never written).

The dispatcher RECEIVES `conversation_id` at `tool_dispatcher.execute(... conversation_id=self.conversation_id ...)` from `unified_pa_entrypoint.py:832`, but uses it ONLY for telemetry emission — never propagated to handlers.

PR #2554 fixes this at the cleanest layer: `_build_tool_payload` `setdefault`s `conversation_id` from `self.conversation_id`. Every PA-routed tool call now sees it. Handler-level overrides still win when the LLM explicitly sets it.

This also incidentally fixes `session_tool whoami`'s same-shape gap — the read at `td_handlers_core.py:3719` gracefully fell back to identity-only, but now `whoami` callers don't need to pass `conversation_id` explicitly either.

### Arc 4 — Verifier-loop deliverables audit (PRs #2556, #2557, #2559, #2560 + deliverable `e2964e4a-…`)

**Trigger:** Chris pivoted from "use the autonomous engineer for the agent-name audit (Tier 3 #4)" to "right agent for the job — Rigby has `deliverable_tool`, use her directly." He flagged that the chat UI didn't surface Rigby's progress during long-running work and proposed the verifier-loop pattern: Rigby executes via her tool surface, Claude verifies every claim directly via Django ORM, Claude reports gaps + corrections to Chris in real-time.

**Trust failures the verifier-loop caught:**
1. Rigby's first attempt — **wrote the 4-part scaffold then marked the deliverable `completed` without any actual findings**. Classic placeholder pattern (memory rule `feedback_rigby_deliverable_content.md`). Claude pulled the deliverable detail directly, surfaced the 513-char outline, and re-prompted with explicit anti-placeholder rules.
2. On the second attempt — **Rigby's workspace-scoped baseline was wrong**: she reported 152 deliverables; ORM showed 300. Her `deliverable_tool.list` was hiding 148 rows (entire `blocked` status invisible). Caught + flagged as a tool-surface gap before any analysis built on the wrong number.

**What the audit ultimately produced:** deliverable `e2964e4a-08e9-4ff1-bc01-7fe3adb5a99c`, 26,465 chars across 4 verified parts, status `completed`:
- **Part 1 — Agent Identity Audit** (appended by Claude via ORM after Rigby's placeholder; 5,519 chars): 313 total deliverables, 35 distinct `agent_name` strings, 2 alias groups (`Rigby`/`rigby` + `ClaudeCode`/`claude-code`), 18 rows would change under normalization.
- **Part 2 — Metric Drift** (Rigby, 4,744 chars; arithmetic + 3 file paths verified): top-10 before/after normalization; `claude-code` ranks **#14 → #4** post-normalization.
- **Part 3 — Duplicate / Template-Leak Cluster Analysis** (Rigby, with ORM cluster data from Claude; 7,155 chars; classifications + token-catch verified): 6 duplicate clusters, **Cluster #1 surfaced as a NEW prompt-leak pattern Gate 4 missed** (32 rows, 28 in last 7 days, ResearchAgent, status mix 31 blocked + 1 archived).
- **Part 4 — Findings / Evidence / Risk / Fixes / Quick Wins / Tool-Surface Gaps** (Rigby; correction applied for non-matching token; 8,532 chars): 5 findings ranked by impact, 5 tool-surface additions proposed, P0/P1/P2 prioritization.

**Concrete fixes shipped from the audit:**
- **#2557 (P0)** — added `'this topic using external sources'` to `TEMPLATE_LEAK_TITLE_TOKENS`. Stops the 28-per-week bleed. Verified via cross-substring check against actual stored 101-char-truncated title; Rigby's belt-and-suspenders second token (`'do not use query_internal_data'`) was caught as a non-match by the verifier-loop and dropped.
- **#2559 (P1 data fix)** — migration 0365 canonicalizes 18 rows. Applied locally; post-state matches audit prediction exactly (33 distinct `agent_name` values, `claude-code` count = 21, rank #4).
- **#2560 (P1 enforcement)** — write-time alias map in `deliverable_factory.create_deliverable`. Prevents future drift. Lockstep test asserts the alias map matches migration 0365's `_ALIAS_MAP` exactly.

**Deferred from the audit (Session 1227 lead candidate):**
- §4.6 tool-surface additions (5 items): `set_status`, `list show_all` flag, `stats full_by_agent`, first-class `duplicates` action, optional `normalize` action. Together these turn this kind of audit from "ORM archaeology" into "one tool call."

## Behavioral invariants post-Session-1226

For ops monitoring (Rigby's lane):

1. **`session_tool action=whoami` returns the authenticated user's identity** + conversation owner facts. Any "not found" / null fields indicate a real ownership or data integrity issue, not a tool-surface gap.
2. **`deliverable_tool.list has_initiative=true` returns only initiative-linked deliverables**; `has_initiative=false` returns only unlinked. Combined with `agent='<name>'` answers the canonical cross-query.
3. **`make celery` locally starts 5 workers**: default, pa, long_running, broadcast, **code_jobs** (was 4 — now 5). Verify with `ps aux | grep "hostname=code_jobs@" | grep -v grep`.
4. **Every PA-routed tool payload contains `conversation_id`** (post-PR #2554). Handlers that need to post-back to the user's chat (`claude_code_tool`, future similar) can read `payload.get('conversation_id')` and rely on it being set.
5. **`claude_code_tool` dispatches now execute end-to-end** when Anthropic credits are available. SUCCESS in `CeleryTaskEvent` no longer means "credits failure was silently swallowed" — it means real work happened.

## Rollback levers

| PR | Lever | When to use |
|---|---|---|
| #2550 | Comment out the `elif action == 'whoami'` block at `td_handlers_core.py:3739+`. Existing actions unaffected. | Only if `whoami` somehow exposes a user field that shouldn't be returnable — unlikely; only `user_id`/`username`/`email`/`is_staff`/`is_superuser` are surfaced, all already in the user's own context. |
| #2551 | Comment out the `has_initiative` block in `_apply_common_filters` + revert the schema description. Existing filters unaffected. | Unlikely needed. |
| #2552 | Comment out the `code_jobs` worker block in `make celery` + matching stop block. `claude_code_tool` dispatches will resume silent-queueing. | If the local worker introduces unrelated resource contention. Don't expect this. |
| #2553 | Switch `--pool=solo` back to `--pool=prefork` in the `code_jobs` block. The SIGSEGV loop will return. | Only if testing prod-shape behavior locally. |
| #2554 | Remove the `payload.setdefault('conversation_id', self.conversation_id)` line in `_build_tool_payload`. PA tool calls revert to needing explicit `conversation_id` in args (or use the never-set `self._conversation_id` fallback that always misses). | Unlikely — no caller currently overrides `conversation_id` via tool args anyway. |

## 24h watch checklist

1. **Anthropic credit-refill verification** — once Chris tops up credits at https://console.anthropic.com/billing, Rigby retries `claude_code_tool` with a trivial task. Confirm: (a) celery `CeleryTaskEvent.status=SUCCESS`, (b) worker log shows no `error 400`, (c) message lands in Rigby's PA chat with the autonomous engineer's output.
2. **Outreach daily beat first fire** — 2026-06-24 at 13:30 UTC. Same verification as Session 1225's 24h watch.
3. **Operator Edge Friday-1 dry-run** — 2026-06-26. Same verification path as Session 1222 close.
4. **`whoami` ergonomics check** — Rigby should naturally use it to set scope on scope-sensitive workflows over the next session or two. If she doesn't reach for it, the schema description may need a discoverability tweak.

## Open ops issues filed this session

1. **Anthropic credits exhausted** — Chris-side; will not auto-recover.
2. **Agent-name normalization drift** (`claude-code` vs `ClaudeCode`) — surfaced by Rigby's first run of the `has_initiative` filter. Fragments any agent-based rollup. Effort: small (data + tool-layer canonicalization), but needs a design pass on which spelling wins and whether to backfill historical rows.

## Memory rules added

| File | Why |
|---|---|
| `feedback_procfile_makefile_queue_parity.md` (added below) | The `code_jobs` worker omission cost a multi-session silent failure. Any future PR that adds a queue route in `app.conf.task_routes` AND adds a Procfile worker for it MUST also add the matching `make celery` block locally, or local testing of any task routed there will silently fail. Recurrence risk is non-trivial — task routing is sprawling (200+ entries in `task_routes`). |

## Lessons / pattern notes

1. **The schema description IS the user surface.** `deliverable_tool.list initiative_id` had been a working list filter since Session 1077, but the schema description only mentioned it for `link_initiative`. Rigby couldn't see it. The fix that mattered was a sentence in the schema, not a code change. When a tool feature exists but no one uses it, check the schema description first.

2. **"Worker telemetry SUCCESS" doesn't equal "user-visible outcome."** All 7 backlog `claude_code_engineer_task` runs returned `SUCCESS` to Celery even though every single one hit an Anthropic 400 inside. The error was caught and returned as a `{'status': 'error', ...}` dict, which Celery accepts as a successful task return. Always cross-check telemetry with the user-visible chain — in this case, the conversation post-back.

3. **Three-layer failures can hide each other.** The `claude_code_tool` dispatch had been failing for multiple sessions because of THREE separate breaks (no worker → no telemetry; macOS pool segfault → no consumption; credits exhausted → no real work; conv_id wiring → no post-back). Each layer hid the next from view. Investigation methodology that worked: start at the symptom, find one layer, fix it, observe the new symptom, repeat. Resist the urge to assume "we fixed it" after the first layer.

4. **Mental-model correction is sometimes the biggest fix.** Rigby and Chris both initially assumed `claude_code_tool` was a bridge to the human-facing Claude Code CLI. The investigation's first deliverable was naming the actual architecture (it's an autonomous Anthropic-API agent that posts to the conversation), which immediately localized the broken paths and stopped us from chasing the wrong fix.

5. **Investigation-first pays off when the surface area is unknown.** I asked Chris up front whether to investigate or ship code; he said investigate. By the time I touched code, I knew exactly which 4 things to fix and in what order. Code-first on this one would have shipped a wrong fix and burned the session.

## Stack state at session close

- **Branches:** all 5 feature branches merged + deleted on origin. `main` advanced from `8542f2c4` (Session 1225 close) to `10c33325` (#2554 merge commit) plus this close PR.
- **Local environment:** Daphne restarted 2× during session. Celery restarted 3× (after #2552, #2553, #2554 + worker registration). All 5 workers healthy at session close, including the new `code_jobs@%h` solo worker.
- **OpenAI credits:** still good ($40 added Session 1224 carrying outreach pipeline).
- **Anthropic credits:** exhausted — Chris-side fix needed.
- **CI billing:** still failing — Chris-side carryover from 1223 → 1224 → 1225 → 1226.
- **Active conversation:** `pa-77bbcd97a625424d` — same pin from Session 1225 mid-session rotation. Carried 1226 cleanly. Health-check threshold (~40 turns) likely hit during the investigation arc — re-check at Session 1227 open.

## Open carryover into Session 1227

See 00-START-NEXT-SESSION.md FIRST THING. Highlights:

- **Anthropic credit refill + autonomous engineer end-to-end verify** — once Chris tops up, Rigby retries `claude_code_tool` to close the full loop documented above.
- **Outreach daily beat first-fire watch** — 2026-06-24 13:30 UTC (already past by Session 1227 open). Verify per Session 1225 watch checklist.
- **Operator Edge Friday-1 dry-run** — 2026-06-26 (Friday). Calendar-driven.
- **Agent-name normalization (`claude-code` vs `ClaudeCode`)** — Rigby's flag from has_initiative verification.
- **Watchdog #5 re-run** — optional carryover from 1223.
- **CI billing fix** — Chris-side.

## What didn't happen

- **No outreach work this session** — Session 1225's deferred items (beat task first-fire watch, tone tweaks) all carry into 1227 untouched.
- **No new memory rule beyond Procfile↔Makefile parity** — the three-layer investigation lessons were valuable but specific to the `claude_code_tool` shape; documenting them inline in this handoff was cleaner than a generic rule.
- **No code touched in `claude_code_engineer.py`** — that file's logic was working correctly all along; every bug was upstream (queue, pool, payload).
