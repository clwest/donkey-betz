# Session 1248 — P2a + P2b shipped, P2c deferred, local↔prod parity named as a theme

**Session window:** 2026-06-27 Saturday late-evening CDT (continuous from S1247 close, ~3h elapsed).

**Theme:** Tonight's session executed the S1247 P2 sprint top-3. P2a (`session_tool` retire/set_active/seed + dispatcher gate) and P2b (`deliverable_tool.create` status echo + `return_detail` opt-in) shipped + live-verified. P2c (prod DB query surface) routed through Rigby with three concrete architecture forks — she picked **defer** (C) for tonight because both viable shapes need prod-side prereqs that land on Chris. Late-session reframe: Chris named **local↔prod parity** as the deeper pattern behind multiple recent friction points, asked whether it's even possible. Recorded that as a session theme for S1249+ with concrete leverage points.

---

## TL;DR

- **2 PRs shipped + admin-merged:**
  - [#2709](https://github.com/clwest/donkey-betz-platform/pull/2709) — session_tool retire/set_active/seed + conversation_action_dispatcher session_active gate (merge SHA `761d68d6`).
  - [#2710](https://github.com/clwest/donkey-betz-platform/pull/2710) — deliverable_tool.create status echo + return_detail opt-in (merge SHA `c4532362`).
- **Both PRs live-verified via Rigby post-bounce + ORM cross-checked.** Verifier-loop pattern held across both.
- **P2c (prod DB query surface) deferred** — Rigby's pick after design discussion (3 forks: A direct DB / B RPC endpoint / C defer). B is her recommended target shape when prod-side prereqs are aligned.
- **Closes ~$3.60/day stale-thread dispatch waste audit** (S1212→S1248 carried across ~36 sessions in flight). AC-1, AC-2, AC-3 from audit deliverable `777d9cd8-…` all met by PR #2709.
- **Closes the verify-then-set_status round-trip** documented in `feedback_deliverable_create_defaults_to_completed.md` via PR #2710's top-level `status` echo.
- **New theme named:** local↔prod parity (see § "S1249+ theme" below).

### Net stats

- **2 PRs** merged
- **28 new tests** total (20 in P2a test file + 8 in P2b test file), all green
- **42 existing tests** still green across the 4 adjacent test files swept (13 session_tool S1247 + 29 deliverable-adjacent), no regression on either PR
- **PA worker bounced twice** (post-#2709 PID 25463, post-#2710 PID 27471) — sys.modules cache rule honored
- **3 verification artifact rows** in the throwaway thread `pa-4b3f8a171a7b417c` + 2 throwaway deliverables (`60407d89-…` ready, `007e5a3c-…` completed) on Donkey Betz workspace
- **2 PA tool gap audit items closed** (top-3 sprint from S1247 deliverable `6b5570c2-…`); 1 deferred (P2c)

---

## What shipped

### PR #2709 — session_tool retire/set_active/seed + dispatcher gate

**Branch:** `feat/session-1248-session-tool-retire-set-active-seed`
**Merge SHA:** `761d68d6`
**Files changed:** 5 (+637/-4)

**Three new actions on `session_tool`:**

| Action | Behavior | Design note |
|---|---|---|
| `retire(conversation_id, force?=False)` | Bulk-flips `session_active=False` on all rows. Returns `updated_count` + `previously_active` + `is_current_bound`. Requires `force=True` when retiring the currently-bound thread, with pin_rotation_notice. | Q1c per Rigby; `_bound_conversation_id` sentinel injected by entrypoint so handler can detect "is this the live chat?" without trusting LLM-overridable fields. |
| `set_active(conversation_id)` | Symmetric inverse (un-retire). Idempotent. | Q2c per Rigby — scope this PR to pure un-retire; do NOT introduce parallel pin-of-truth field. |
| `seed(conversation_id, content)` | Appends a `[SYSTEM SEED]`-prefixed message row with `source='pa'`. Empty/whitespace content rejected at handler edge. | Q3a per Rigby — `source='pa'` not `'claude-code'`; hard marker for grep/filter. |

**Conversation_action_dispatcher gate** (vertical-slice fix — Q4a per Rigby):

- Short-circuits with clear error payload when every `ChatConversation` row for the `conversation_id` has `session_active=False`.
- Fail-opens on DB errors so a flaky DB can't take down the live dispatch path.
- `context.allow_retired=True` escape hatch (logs WARN; intended for staff/debug).

**Closes:** S1212 audit deliverable `777d9cd8-…` ("Audit: Stale-Thread Conversation Action Dispatcher"). AC-1 (4 named retired threads no longer dispatch), AC-2 (active thread unaffected), AC-3 (24h watch starts at `761d68d6`) all structurally satisfied.

**Live verification (via Rigby on PA worker PID 25463 + ORM cross-check):**

| Step | Input | Expected | Actual |
|---|---|---|---|
| 1 create_fresh | throwaway TEST_CID | conversation_id returned, starter_prompt populated | `pa-4b3f8a171a7b417c`, starter matches carry_forward — proves PR #2707 Finding 2 still working |
| 2 retire cross-thread | `conversation_id=TEST_CID` | `retired=true`, `updated_count=1`, `is_current_bound=false` | ✅ exact |
| 3 idempotent retire | retire again | `retired=true`, `updated_count=0`, `previously_active=false` | ✅ exact |
| 4 retire bound thread no force | `conversation_id=pa-3901b70e61934df7` (live pin) | `retired=false`, `is_current_bound=true`, error contains "force=true", **zero row mutation** | ✅ ORM confirmed 14/14 rows still `session_active=True` |
| 5 set_active | reactivate TEST_CID | `reactivated=true`, `updated_count=1` | ✅ |
| 6 seed | content="<73 chars>" | `seeded=true`, marker=[SYSTEM SEED], real `seed_message_id` | ✅ row id=1519 with source='pa' + prefix confirmed via ORM |
| 7 seed empty | `content=""` | error "non-empty content" | ✅ |

### PR #2710 — deliverable_tool.create status echo + return_detail opt-in

**Branch:** `feat/session-1248-deliverable-tool-create-return-detail`
**Merge SHA:** `c4532362`
**Files changed:** 3 (+227/-1)

**Two complementary fixes:**

1. **Top-level `status` always echoed** in successful create response. BC-safe extra key. Fixes the common case immediately for the 90%+ of callers who just need to know `completed` vs `ready` to decide whether to follow up with `set_status`.
2. **`return_detail: bool = False` opt-in.** When truthy, runs follow-up `_handle_deliverables(action='detail', id=<new_id>)` and embeds sanitized dict under `detail` key with `detail_included: bool` flag. Detail-fetch failure is soft (warn + flag=False; create still ok=True).

**Design alignment with Rigby (4 deltas captured in commit body):**

| Delta | Resolved by |
|---|---|
| #1 echo *stored* status not requested | Handler reads `obj.status` from post-create instance |
| #2 canonical field name `status` (no drift) | Tests assert no `created_status`/`to_status` |
| #3 detail.status echoed but top-level is source of truth | Both populated; tests verify equality + top-level remains canonical |
| #4 `detail_included: bool` flag when return_detail=True | Set False on soft-fail; True on success; absent when return_detail=False |

**Closes:** `feedback_deliverable_create_defaults_to_completed.md` round-trip class.

**Live verification (via Rigby on PA worker PID 27471 + ORM cross-check):**

| Step | Response shape | ORM verify |
|---|---|---|
| 1 create no-detail | `status='completed'` at top level; no `detail`/`detail_included` keys | row exists in Donkey Betz |
| 2 create return_detail=true | top-level `status='completed'` + `detail.status='completed'` (equal) + `detail_included=true` + full provenance/content fields embedded | row exists, content_length=854 matches |
| 3 set_status to ready | `from_status=completed`, `to_status=ready`, transition_event_id real | row status now `'ready'` ✅ |

### Both PRs were admin-merged

Per S1246/S1247 pattern given the Anthropic billing failure still preventing GitHub Actions CI runs. Admin-merge is the team's working norm during this billing gap.

---

## P2c — deferred (Rigby pick: C; second-choice: B)

**Three architecture forks discussed with Rigby:**

| Fork | Shape | Pros | Cons |
|---|---|---|---|
| **A** | Extend `db_health_tool` with `env='prod'` selector + direct DB connection via `PROD_READONLY_DATABASE_URL` | Smallest diff (~50 lines + Postgres role + env var) | Prod DB creds in local `.env`; .env leak = direct prod DB read |
| **B** | Extend `db_health_tool` with `env='prod'` selector + HTTP RPC to new prod-side `/api/db-health-rpc/` endpoint | No prod DB creds on local. Prod owns its own DB access. Per-call audit at prod-side. | Bigger diff (~150 lines, 2 natural PRs — server + client) |
| **C** | Defer entirely. Unblock immediate P3 question (FleetServiceKey count) via Chris/Rigby manual prod check. | Zero new attack surface. Clean exit tonight. | P2c stays on menu without code surface |

**Rigby's pick: C** ("both A and B ultimately require prod-side secrets/roles or service-token wiring you can't complete without Chris tonight, so the MVP-safe path is to unblock P3 with a one-off manual prod check and revisit a hardened RPC design (B) after the morning_brief window").

**Second-choice for "real implementation": B** (security-correct long-term shape).

---

## S1249+ theme — local↔prod parity

Late-session Chris reframe: many recent friction points (this session alone — `pa_chat.py` defaulting to prod URL twice this week, `FleetServiceKey.count==0` ambiguous-locally questions, `audit_celery_zero_fire` only seeing local telemetry, docs corpus 12d stale in prod, etc.) are all symptoms of **observability gap** (can't see prod state from local without Railway shell) + **parity-detection gap** (don't know when a local-green code path is prod-broken until something breaks).

**Recorded position on what to do about it:**

- **Full parity is NOT the right goal.** Prod has real data/traffic by design. Trying to mirror that on local is a foot-gun.
- **Solvable in pieces; doesn't need a sweeping rewrite.**
- Concrete leverage points, biggest payoff first:
  1. **P2c-B (RPC prod-side endpoint)** — single source for "is X populated in prod?" questions. Rigby's recommended target shape. One PR with prod-side view + local-side tool that calls it.
  2. **Wrapper-trap cleanup** — `pa_chat.py` defaulting to prod URL is the #1 footgun. Flip default to local, require explicit `--env prod`. Tiny PR.
  3. **Env-parity probe** — daily beat task runs the same 5-7 canned health checks on both envs (via P2c-B), surfaces drift as a deliverable.
  4. **`make env-diff` mgmt cmd** — diffs config keys / migrations applied / Celery task list / PeriodicTask counts across local↔prod. Run when something feels off.
- **What NOT to do:** seed prod data locally; write "prod-shape" tests pretending prod runtime state from local fixtures; try to make local Postgres identical to prod (scale differences = different planner behavior).

These are the recommended top-of-queue items for S1249.

---

## Memory rules referenced (no new rules added)

- `feedback_claude_directs_rigby_then_verifies.md` — verifier-loop held cleanly across both PRs; Rigby's reports + ORM cross-checks agreed every time.
- `feedback_deliverable_create_defaults_to_completed.md` — root cause closed by PR #2710's status echo (round-trip now optional, not required).
- `feedback_local_only_default.md` — directly informed P2c discussion ("forks A and B both introduce prod-touching state from local for the first time"); helped Rigby reach the C verdict.
- `feedback_stop_putting_chris_to_bed.md` — observed; close framing names actual carryover (P1 in ~9h, S1249 leverage points) without "go to bed" framing.

---

## What's open at S1248 close

**Time-bound (carries over from S1247):**

- **P1 morning_brief CUMULATIVE verification — ~13:00 UTC Sunday 06-28 (07:00 MDT)**. Runbook deliverable `421eeaca-fab8-4753-bd11-33a9b831ee96` still staged. ~9h away at S1248 close.

**Carried over from S1247 (still open):**

- Finding 3 (workspace_tool counter decoupling)
- Section 5B verification of `autopilot_tool.drift_scan` + `diagnostics_tool.schema_handler_diff`
- `pa-2bb73c969fd24802` 26→29 turn growth (something still writing to retired S1246 thread)

**New deferred:**

- P2c implementation (Rigby's pick B / RPC endpoint shape; needs prod-side endpoint + Chris-side env var/auth setup)
- P3 content/char-training retirement (still blocked on prod FleetServiceKey verification; P2c-B would unblock this programmatically)
- Local↔prod parity theme leverage points (named above; pick at S1249 open)

**Pre-existing carryover (unchanged):**

- P3 workspace leak watch "real fix" investigation
- P4 S1115 #12 deferred list re-audit (~2026-07-13 telemetry-valid window)
- P5 audit-domain pick (Spider pipeline / RAG / 24/7 advisor system — PA tools struck from list after S1247 gap audit deliverable `6b5570c2-…`)
- Anthropic credit refill (still blocking CI lint runs — both #2709 and #2710 admin-merged for this reason)

---

## Conversation health at close

- **Active pin:** `pa-3901b70e61934df7` ("Session 1247 — morning_brief P1 verification + content/char-training retirement"). Title is now stale (session 1247 was yesterday; tonight closed S1248) but thread is still healthy.
- **Estimated state at S1248 close:** ~22-26 turns total (S1247 open started at 10; S1248 added ~12-16 turns across P0 health probe + P2a design Qs + P2a verify + P2b design Q + P2b verify + P2c design discussion). Light enough that pre-rotation `health_check` at S1249 open should return `recommendation: continue`. If it surfaces `suggest_fresh` at S1249 open, rotate as documented.
- **Throwaway artifacts (discardable):** `pa-4b3f8a171a7b417c` (P2a/P2b verify thread with 2 rows + 1 [SYSTEM SEED] row); throwaway deliverables `60407d89-…` (status=ready, P2b step 1) and `007e5a3c-…` (status=completed, P2b step 2) in Donkey Betz workspace.
- **Retired (still tracked):** `pa-2bb73c969fd24802` (S1246; was 26 turns at S1247 rotation, grew to 29 by S1247 close, no follow-up grep done — still on the carryover list).

---

## Recommended FIRST THING Session 1249

**07:00 MDT (~13:00 UTC) Sunday 06-28 — P1 morning_brief CUMULATIVE verification fire window.** Runbook deliverable `421eeaca-fab8-4753-bd11-33a9b831ee96` is the canonical procedure. Pre-fire checklist: celery worker alive + beat alive + long_running queue depth = 0; post-fire scrub regexes + cf708a2e workspace leak watch already coded into the runbook's Python block.

After P1 fires (one way or the other), the natural S1249 priority queue is:

1. **Pick from the local↔prod parity leverage menu** (theme named above). P2c-B + wrapper-trap cleanup are the two smallest + highest-leverage starts.
2. **P3 content/char-training retirement** — now unblockable either via Chris running a one-off `railway run python -c "from core.models import FleetServiceKey; print(FleetServiceKey.objects.count())"` OR via P2c-B shipping first.
3. Lower-priority backlog as it stands (Finding 3, audit menu, etc.).

Pin health-check `pa-3901b70e61934df7` at session open via `session_tool action=health_check conversation_id=pa-3901b70e61934df7` — fix from PR #2707 means the explicit conversation_id is now honored.
