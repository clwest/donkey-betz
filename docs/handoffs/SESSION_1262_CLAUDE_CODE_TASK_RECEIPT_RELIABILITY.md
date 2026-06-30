---
session: 1262
status: closed
date: 2026-06-30
arc: Claude Code task receipt reliability — fix the S1257 P1 receipts gap that re-surfaced in S1261 when Rigby's recursive claude_code_tool dispatch silently vanished
prs_merged: [2752]
prs_open: []
companions:
  - docs/handoffs/SESSION_1261_EMPLOYEE_OS_FOUNDATION_HARDENING.md
deliverables: []
---

# Session 1262 — Claude Code Task Receipt Reliability

## TL;DR

The S1257 P1 task-receipt gap that re-surfaced in S1261 is closed.
PR #2752 makes `claude_code_engineer_task` write an `AgentExecution`
row at task entry + wire the existing S1174 follow-up wake stack +
make `_post_to_conversation` fail-loud. Five recent dispatches that
silently vanished (task_ids 9d601010, 068ee853, bf7ca961, 18734082,
f8a4d3c2) are now diagnosable; the auto-wake banner Rigby's
PAConversationConsumer publishes appears automatically end-to-end.
Discovery → Rigby Phase 1 SIGN → implementation → 10 new tests +
224 regression tests → 3 live dispatches verified → Rigby Phase 4
SIGN → admin-merge → post-merge prod-verified, all in one session.

## What shipped — PR #2752 (admin-merged 2026-06-30, merge SHA `5e30143e`)

**Pure infrastructure repair. No new architecture. Reuses canonical
AgentExecution + S1174 follow-up wake stack.**

| File | Net | Purpose |
|---|---|---|
| `core/services/claude_code_engineer.py` | +342 | 4 new helpers + fail-loud `_post_to_conversation` |
| `core/tasks.py` | +86 | `claude_code_engineer_task` AgentExecution lifecycle + auto-wake wiring + `max_retries=0` |
| `core/tests/test_claude_code_task_receipts_s1262.py` | +310 | 10 new contract tests |

Total: 3 files, +769 / -31.

### Root cause (smoking-gun evidence)

Five recent `claude_code_engineer_task` dispatches ALL returned
`CeleryTaskEvent.status=SUCCESS` after 33-128 seconds of LLM work but
produced **zero** AgentExecution rows and **zero** ChatConversation
post-backs. The work happened. The result vanished.

| task_id (first 8) | When | dur_s | AgentExecution | Post-back |
|---|---|---|---|---|
| `9d601010` | today 15:16Z (S1261 receipts gap) | 39.4 | ❌ | ❌ |
| `068ee853` | yesterday 21:25Z (S1257 P1 incident) | 40.7 | ❌ | ❌ |
| `bf7ca961` | yesterday 16:43Z | 33.8 | ❌ | ❌ |
| `18734082` | 2026-06-28 | 58.1 | ❌ | ❌ |
| `f8a4d3c2` | 2026-06-27 | 128.7 | ❌ | ❌ |

Two concrete bugs:

1. **`claude_code_engineer_task` did NOT write an `AgentExecution` row**, so
   the canonical S1174 PR-2 follow-up wake stack
   (`AgentFollowupSubscription` → signal handler →
   `PAConversationConsumer.agent_completed`) had no anchor to bind to.
2. **`_post_to_conversation` (`claude_code_engineer.py:841`)** was guarded
   by four `if conversation_id:` checks at lines 717, 733, 820, 836.
   When `conversation_id` arrived as None (dispatcher's
   `self._conversation_id` None at dispatch time, or kwarg lost across
   the queue boundary), the entire post-back chain was silently
   skipped — no log, no error, no observable artifact.

### Repair — reuses canonical pattern from `core/tasks_agents.py:2270-2325`

**Per Rigby Phase 1 SIGN refinements:**

1. **Canonical agent-name resolver with alias fallback** — `claude-code`
   preferred, `ClaudeCode` accepted. WARN-logs `[CLAUDE_CODE_AGENT_DUP]`
   when both exist so a future hygiene PR can consolidate without this
   PR coupling to it.
2. **`max_retries=0` + `acks_late=False`** — fail-loud raise from
   `_post_to_conversation` does NOT trigger Celery's default 3-retry
   behavior. LLM budget protected.
3. **`conversation_id=None` is NOT a raise** — the LLM run succeeded;
   ERROR-log `[CLAUDE_CODE_POSTBACK_DROPPED]` + persist the result on
   the AgentExecution row for later retrieval.
4. **`ChatConversation.create` failure IS a raise** — mark
   `AgentExecution.output_data['post_back_status']='failed'`, ERROR-log
   `[CLAUDE_CODE_POSTBACK_FAILED]`, then RAISE so
   `CeleryTaskEvent.status=FAILURE` becomes visible. Summary preserved
   on AgentExecution for retrieval.
5. **Both `create_implicit_followup_subscription` AND
   `fire_agent_followup_subscriptions`** wired in the task body. The
   former arms the auto-wake; the latter transitions armed → fired
   since the execution is already terminal at that point. Without both,
   the S1174 stack would arm a subscription that never fires.

## Live verification (3 real dispatches, plus 10/10 unit tests + 224 regression tests)

### Happy path round 1 — Rigby dispatch `8e700597` (15:47Z)

- CeleryTaskEvent SUCCESS dur 39.4s
- AgentExecution `3e318692-…` status=completed, conversation_id set
- AgentFollowupSubscription armed
- ChatConversation post-back row 1618 landed, metadata.agent=claude_code_engineer

### Happy path round 2 — Rigby dispatch `8a417bde` (15:51Z, after `fire_agent_followup_subscriptions` added)

- CeleryTaskEvent SUCCESS dur 2.3s
- AgentExecution `6022e255-…` status=completed
- AgentFollowupSubscription state=**FIRED** + `result_payload.status=completed`
- ChatConversation post-back row 1619 "Receipt test S1262"
- **Rigby-authored auto-followup row 1620** at 15:51:19.342Z, source=pa —
  the completion banner that previously never appeared. The full S1174
  consumer-side path fires end-to-end.

### Failure path — direct shell dispatch `dc07dfd6` with `conversation_id=None`

- `[CLAUDE_CODE_EXECUTION_CREATED]` INFO log
- `[CLAUDE_CODE_POSTBACK_DROPPED]` ERROR log: `"conversation_id is
  empty/None — ChatConversation post-back skipped. summary_len=23
  files_changed=[] pr_url=None agent_execution_id=f8b987f1-…. Result IS
  retrievable via AgentExecution.output_data when agent_execution_id is
  set."`
- AgentExecution status=completed, `output_data.summary='RECEIPT-FAILURE-PATH-OK'`
- Zero ChatConversation post-back (correct — no conversation to write to)
- Task itself returned SUCCESS (no raise — preserves no-retry contract)

### Post-merge prod verification — Rigby dispatch `3b36216b` (15:58Z, after admin-merge)

- CeleryTaskEvent SUCCESS dur 1.8s
- AgentExecution status=completed, `output_data.summary='S1262 POST-MERGE OK'`
- AgentFollowupSubscription state=fired
- ChatConversation post-back row 1623 "S1262 POST-MERGE OK"

## What's preserved unchanged

- `claude_code_tool` PA tool response shape: `{status, task_id,
  request_mode, message}` — verified via Rigby's verbose Tool Runs
  block across all 4 dispatches.
- MissionRunner: zero edits.
- Employee OS: zero edits.
- JobContract dataclass: zero new fields.
- `employee_tool`, `mission_verdict`, all other PA tools: zero touches.
- No new models, no new tables, no new PA tools, no new DB primitives.
- All other tests unaffected (224/224 regression pass).

## New log markers (greppable diagnostics)

| Marker | Level | When | Purpose |
|---|---|---|---|
| `[CLAUDE_CODE_EXECUTION_CREATED]` | INFO | every dispatch | Anchor receipt — execution_id + celery_task_id + conversation_id |
| `[CLAUDE_CODE_POSTBACK_DROPPED]` | ERROR | conv_id is None at worker | Replaces the prior silent skip. Result still queryable via AgentExecution.output_data |
| `[CLAUDE_CODE_POSTBACK_FAILED]` | ERROR | ChatConversation.create raised | Triggers task FAILURE; max_retries=0 prevents LLM budget re-spend |
| `[CLAUDE_CODE_AGENT_DUP]` | WARN | both `claude-code` + `ClaudeCode` rows match | Surfaces duplicate-Agent-row condition without blocking the fix. Future hygiene PR can consolidate |
| `[CLAUDE_CODE_FOLLOWUP_WIRE_FAILED]` | WARN | auto-wake wiring raised | Result still posted via `_post_to_conversation`; only the auto-banner is missed |
| `[CLAUDE_CODE_NO_AGENT_ROW]` | WARN | no Agent row resolvable | Defensive — telemetry skipped, result still flows via CeleryTaskEvent + post-back |

## Disagreement with the S1257 diagnosis

The S1257 memory listed three gaps (a) `no AgentExecution row`,
(b) `silent post-back failure`, (c) `no Chat UI receipt`. **(a) and (b)
have the same root cause** — the post-back chain had no authoritative
record to bind to. Fixing (a) with the canonical AgentExecution pattern
automatically delivered (b) — the AgentExecution row carries the result
whether or not conversation_id is set. (c) is UI work; out of scope for
this infrastructure PR.

## Memory observations worth keeping

- **Verifier-loop pattern caught the right size of fix.** Discovery
  showed `_post_to_conversation` had FOUR silent-skip guards, not the
  one or two the S1257 memory implied. Independent grep + ORM probe of
  5 historical dispatches grounded the fix in evidence, not speculation.
- **Reuse over invention paid off.** The S1174 PR-2a follow-up wake
  stack (signal handler + consumer + auto-followup ChatConversation
  row) was already built and waiting. Wiring `claude_code_engineer_task`
  into it required ZERO new primitives. The result is a fix that's
  smaller than the gap it closes — net +769 / -31 lines, most of which
  are docstrings + tests.
- **Two-step follow-up wiring is needed.** `create_implicit_followup_
  subscription` alone arms the subscription but leaves it `state=armed`
  forever if no signal handler fires it. The canonical
  `_impl_execute_agent_task` calls `fire_agent_followup_subscriptions`
  AFTER terminal-state-save. Round 1 of verification missed the second
  call — sub stayed armed, banner didn't appear. Adding the explicit
  fire call fixed it (round 2: sub transitioned to `fired`, Rigby got
  the auto-banner).

## What's next (Session 1263 entry point)

The receipts gap arc is closed. Next priorities (per S1262 close
+ Rigby SIGN follow-up watch suggestion):

1. **Watch the new log markers** for ~24h to confirm no unexpected
   volume (per Rigby Phase 4 SIGN suggestion — not a blocker, just
   hygiene)
2. **Consolidate the duplicate Agent rows** (`claude-code` + `ClaudeCode`)
   — surfaced by `[CLAUDE_CODE_AGENT_DUP]` WARN. Separate ~10-line
   hygiene PR.
3. **Pre-existing SLO breaches** — `agent_timeout_rate` 12× over,
   `celery_task_success_rate` marginally under. Investigation.
4. **MissionRunner `authority_check_fn` preflight hook** (warn-mode) —
   S1260 P4 recommendation, deferred from S1261.
5. **Read-only `/api/employees/` + `/api/missions/`** — S1260 P5
   recommendation.
6. **Hygiene PRs** — orphan `content.*` route in CELERY_TASK_ROUTES,
   CLAUDE.md autoblock + agent taxonomy drift refresh.
7. **Employee #4** — architecturally ready, awaiting Chris's call on
   which employee.
