# Session 2885 — content_tool structured error-envelope migration (file-completing) + pgbouncer collision resolution

**Date:** 2026-07-22
**Session pin (retired at close):** `pa-42342895674d4878` (labeled `s2885-open`; minted at S2885 open after character-os collision resolution)
**Prior pin retired at S2885 open:** `pa-261ad03bdd634e70` (S2884 close mint, atomically retired via `session_lifecycle close --label s2885-open`)
**Slate label:** S2885 — `td_handlers_content.py` file-completing critical-slice error-envelope migration (Slate 5)
**PRs:** #3394 (`5495736fb`) + `<docs cascade>` at close
**Combined regression:** 220/220 (S2869 baseline + 8 S2884 + **13 S2885** − 1 retired S2877 backfill = 220 vs 207 at S2884 close)

---

## S2885 open — pgbouncer auth block RESOLVED

S2884 close deferred pgbouncer triage to S2885 first-action. **Chris's character-os collision hypothesis was correct** — but the resolution surfaced three stacked problems, not one.

### Root cause: 3 stacked infra faults, all surfacing as `auth_backend_unavailable` (503) or `token rejected` (401)

1. **character-os `pgvector/pg16` Docker container captured `:5433` via IPv6 wildcard.** Container ID `d2296646a7d1`, mapping `0.0.0.0:5433->5432/tcp` (IPv6 wildcard `*:5433`). u-d-b's native pgbouncer (PID 1513) held IPv4 `127.0.0.1:5433`. `localhost:5433` resolves to `::1` first → Django hit character-os postgres, not pgbouncer. **Fix:** `USE_PGBOUNCER=0` in `.env` in BOTH `/Donkey_Betz/unified-donkey-betz/` and `/development/unified-donkey-betz/` checkouts (symmetric bypass). Revert-to-1 trigger: cross-repo port ownership resolved. Chris flagged the roadmap ties u-d-b + character-os together; universalization may be required.
2. **Orphan Daphne from `/development/unified-donkey-betz/`** (PID 60841, elapsed 4h38m, parent=launchd) held `:8000`. `make restart-daphne` in `/Donkey_Betz/` silently failed to bind (`Address already in use`, CRITICAL logged to `server.log`). Health endpoint validated whoever was on `:8000` — the `/development/` Daphne with stale env. Env flip in `/Donkey_Betz/` had zero runtime effect. **Fix:** `kill 60841`, then `make restart-daphne` from `/Donkey_Betz/`. `/development/` checkout designated legacy by Chris.
3. **`.env` `PA_API_TOKEN` was 11 days stale.** DB `chris` token was rotated 2026-07-11 (S2758 post-travel triage era) to `8c0f15633e84...`; `.env` still had the orphan `0256880456bb...`. Even after fixing (1) and (2), whoami returned 401. Nobody noticed for 11 days because past pins were cached in `~/.claude-pa-verified/<pin>.json` and skipped the verify step. **Fix:** update `PA_API_TOKEN` in `/Donkey_Betz/.env` to match DB.

**Verification at S2885 open (00:15 MDT):** full end-to-end Rigby loop confirmed — wrapper verify → `/api/pa/whoami/` HTTP 200 (`chris`, `is_staff=true`) → PA dispatch → GPT-5.2 response.

**Rigby Tool Gap Ledger entry #24 persisted** (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, appended 2874 chars, new total body 50822 chars). Rigby's `tool_runs` verified the append + follow-up `deliverable_tool.detail` cross-check per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

---

## Shipped

### PR #3394 `5495736fb` — S2885 slate (2 files, +439/-13)

- **`core/services/td_handlers_content.py`** (+50/-13) — new local `_handler_error` helper at module top (adopter #5 for the S2879 shape, one short of Rigby's `td_error.py` extraction gate). Migrated 13 sites across 5 handlers (see migration diff table below).
- **`core/tests/test_s2885_content_error_envelope.py`** (NEW, 402 lines) — 13 test rows exercising the full `ToolDispatcher.execute_sync` path via `deliverable_tool`, `feedback_tool`, and `content_tool`. Reuses S2879 `_assert_migrated_envelope` helper. **First slate to require `TransactionTestCase`** — see Fold 1 below.

### Migration diff — 13 sites × 4 codes × 5 handlers × 3 dispatched tools

| Handler | Site | Prior return shape | New `error_code` | Helper | Dispatched tool |
|---|---|---|---|---|---|
| `_handle_deliverable_initiative_link` | content.py:178 | `{'error': 'deliverable_id is required', 'action': action}` | `invalid_params` | `_handler_error` | `deliverable_tool` |
| `_handle_deliverable_initiative_link` | content.py:182 | `{'error': f'Deliverable {id} not found', 'action': action}` | `not_found` | `_handler_error` | `deliverable_tool` |
| `_handle_deliverable_initiative_link` | content.py:186 | `{'error': 'initiative_id is required for link_initiative', 'action': action}` | `invalid_params` | `_handler_error` | `deliverable_tool` |
| `_handle_deliverable_initiative_link` | content.py:190 | `{'error': f'Initiative {id} not found', 'action': action}` | `not_found` | `_handler_error` | `deliverable_tool` |
| `_handle_feedback` | content.py:3654 | `{'error': 'comment is required for submit'}` | `invalid_params` | `_handler_error` | `feedback_tool` |
| `_handle_content` | content.py:4788 | `{'error': f'Unknown content_tool action: {action}. Valid: ...'}` | `unknown_action` | `_handler_error` | `content_tool` |
| `_handle_bulk_archive` | content.py:4821 | `{'error': 'Cannot bulk archive published/archived items. Valid statuses: ...'}` | `invalid_params` | `_handler_error` | `content_tool` (action=`bulk_archive`) |
| `_handle_bulk_archive_published` | content.py:4966 | `{'error': 'Permission denied. bulk_archive_published requires admin/staff.', 'status': 403}` | `permission_denied` (legacy `status: 403` dropped per SIGN T1c) | `_handler_error` | `content_tool` (action=`bulk_archive_published`) |
| `_handle_bulk_archive_published` | content.py:4971 | `{'error': 'Blogs are not supported by bulk_archive_published. ...'}` | `invalid_params` | `_handler_error` | `content_tool` |
| `_handle_bulk_archive_published` | content.py:4976 | `{'error': 'categories (list of strings) is required. ...'}` | `invalid_params` | `_handler_error` | `content_tool` |
| `_handle_bulk_archive_published` | content.py:4980 | `{'error': 'created_before (ISO-8601 datetime) is required for safety.'}` | `invalid_params` | `_handler_error` | `content_tool` |
| `_handle_bulk_archive_published` | content.py:4984 | `{'error': f'Invalid created_before datetime: {v}. ...'}` | `invalid_params` | `_handler_error` | `content_tool` |
| `_handle_bulk_archive_published` | content.py:5046 | `{'error': 'Execute requires confirm=true. ...', **result}` | `invalid_params` (dry-run preview preserved via `**{k: v for k, v in result.items() if k != 'action'}` per SIGN T1d) | `_handler_error` | `content_tool` |

**Post-S2885 handler-file population:** 5 → **4 files** (`core.py=73`, `gateway.py=57`, `railway.py=18`, `codejobs.py=15`). Bare-return count: 176 → 163.

## Rigby SIGN cycles

### Pre-code SIGN Q1 (routing-map refresh, tool-grounded per `feedback_verify_rigby_tool_runs_before_trusting_sign`)

Rigby ran 6+ `repo_tool.read_file` + `repo_tool.search` invocations at HEAD `43f40edd5` to independently verify the 13-site routing map before AGREEing to any of it. Empty `tool_runs` = rubber-stamp signal; this cycle's tool_runs were substantive.

### Pre-code SIGN T1a–T1e (routing map + taxonomy + micro-decisions + gate)

- **T1a Routing map accuracy:** AGREE (all 13 lines + handler-scope assignments verified against file at HEAD).
- **T1b Taxonomy code selection:** AGREE (all 13 sites map cleanly to existing 5-code taxonomy: 1× `unknown_action`, 9× `invalid_params`, 2× `not_found`, 1× `permission_denied`).
- **T1c Micro-decision (1) drop `status: 403` at L4966:** AGREE (matches S2882 agents_tool precedent; no in-repo consumers key on `error.status`).
- **T1d Micro-decision (2) filter `action` from `**result` at L5046:** AGREE (avoids `TypeError` collision with `_handler_error`'s `action` positional; dry-run preview payload preserved).
- **T1e Ledger #13 6-adopter gate:** AGREE (S2885 takes count 4/6 → 5/6; content.py's staff-gated write-path adds real substrate for the extraction decision but doesn't change the 6-adopter target).

### Pre-code SIGN zoom-out (b) — CONFIRMS S2884 concern, drives Slate B pivot

Rigby's response: this slate **confirms** her S2884 concern that file-completing can leave the highest-volume / riskiest files (`core.py=73`, `gateway.py=57`) for last. Content.py demonstrates file-completing isn't always low-criticality (it includes a staff + confirm-gated write-path), but it still delays confronting the nastiest surfaces. **Recommendation: after S2885, Slate B pivots to criticality-first grep across the remaining 4 files (core.py + gateway.py first)**, NOT continue file-completing on codejobs.py (15).

**Chris D-verdict (S2885, 2026-07-22):**

- Pre-code: pre-approved routing map + both micro-decisions ("approved, route the SIGN to Rigby").
- Post-SIGN: chose Option 1 (ship Slate A as-scoped, record Slate B pivot recommendation for next-session first-action) over Option 2 (bundle Slate A + codejobs.py). Ratified with "go with 1, write the code."

### Post-code SIGN (live envelope verification)

Post-merge dispatch via Rigby confirmed structured envelope shape:

- `deliverable_tool` action=`link_initiative` (no `deliverable_id`) → `{success: False, error_code: 'invalid_params', error: 'deliverable_id is required', action: 'link_initiative', gateway: 'deliverable_tool'}` **VERIFIED**.
- `feedback_tool` action=`submit` (no `comment`) → `{success: False, error_code: 'invalid_params', error: 'comment is required for submit', action: 'submit'}` **VERIFIED**.
- `content_tool` action=`__bogus_s2885__` — **blocked at OpenAI schema enum guard** (Rigby's tool-schema constrains `action` to a known enum). Migration IS in place at L4788; the schema guard prevents Rigby from testing the fallthrough via the normal dispatch path. The `test_unknown_action_returns_unknown_action` test in the S2885 regression suite exercises the exact code path directly via `ToolDispatcher.execute_sync` (bypassing schema enum) — 13/13 pass validates the internal envelope.

## Fold observations

### Fold 1 (1st trigger) — `TransactionTestCase` required whenever setUp-created rows must be visible to `ToolDispatcher.execute_sync`

**Discovery:** `ToolDispatcher.execute_sync` at `core/services/tool_dispatcher.py:1160` spins up a fresh asyncio event loop (`asyncio.new_event_loop().run_until_complete(...)`). The handler's ORM queries land on a Django connection that doesn't see the test's wrapping transaction, so `setUp`-created fixtures (real `Deliverable`, real staff/non-staff `User`) are **invisible under plain `TestCase`**.

Prior slates (S2879 → S2884) avoided this issue by only using nonexistent UUIDs (no fixtures required — `Deliverable.DoesNotExist` fires cleanly regardless of connection isolation). **S2885 is the first slate that needed real fixtures**: L186 (missing `initiative_id` — requires a valid `deliverable_id` to reach the initiative check), L190 (missing Initiative — requires a real Deliverable + missing initiative), and L4971–L5046 (all require a `staff_user` to pass the L4966 admin gate).

**Fix:** `DeliverableInitiativeLinkMigratedEnvelopeTests` and `ContentToolMigratedEnvelopeTests` use `TransactionTestCase` (commits between setUp and dispatch so fixtures are visible to any connection). `FeedbackToolMigratedEnvelopeTests` doesn't need fixtures — kept plain `TestCase`.

**Trigger count:** 1 — watch for corroboration in Slate B (`core.py` / `gateway.py` will have similar staff-gated write-paths). If Slate B also requires fixtures, promote to Playbook amendment candidate. Ledger candidate now.

### Fold 2 (1st trigger) — L190 test was false-passing before fortification

**Discovery:** With fixture invisibility under plain `TestCase`, the "missing Initiative → not_found" test was actually reaching the "missing Deliverable → not_found" branch (both return `not_found` code, so `_assert_migrated_envelope` passed for the wrong reason).

**Fortification:** Added `self.assertIn('Initiative', result.get('error', ''), ...)` to disambiguate which branch fired.

**Test-authoring lesson:** when two branches in the same handler return the same taxonomy code, always assert on the message body to disambiguate. Otherwise a regression that breaks the L182 check would silently allow the L190 test to keep passing.

**Trigger count:** 1 — Playbook amendment candidate if this pattern re-triggers in Slate B. Log to ledger.

### Fold 3 (5th observation) — Ledger #13 adopter #5 (S2879 helper duplication)

Local `_handler_error` copy added to `td_handlers_content.py` — post-S2885 count = **5** (ops + governance + agents + newsletter + content). Rigby's 6-adopter gate on `td_error.py` extraction (set at S2875) is now **1 file short**. Slate B (whichever file gets migrated first) is the natural extraction-arc trigger candidate.

### Fold 4 (1st trigger, close as N/A pending 2nd trigger) — Cross-repo Docker infra collision pattern

Character-os's Docker postgres captured u-d-b's pgbouncer port via IPv6 wildcard. Same failure mode could recur with any sibling Docker container (Redis, MinIO, Elasticsearch — any port shared across repos). Chris flagged the roadmap ties both u-d-b + character-os together; universalization ("everything will need to be universal") is a coming work item. This entry stays in the "watching for 2nd trigger" pile until a second cross-repo collision surfaces. `feedback_post_travel_port_collision_triage` remains the operative rule for triage-order.

## Chris strategic input (recorded)

**Cross-repo universalization (S2885 open, plain-English quote):** "one of the roadmaps tied both together so I am starting the process of seeing what that looks like but it might require two Claudes running at the same time in different repos so everything will need to be universal I guess lol."

Not a decision-point tonight — flagged as forward-carry context for whichever arc actually opens the u-d-b ↔ character-os shared-infra work. Fold 4 above is the substrate signal.

## Test + regression posture

**S2885 file suite:** 13/13 pass (18.4s, `--keepdb --noinput`).

**Combined S2879 → S2885:** 62/62 pass (S2879=8 + S2880=5 + S2881=6 + S2882=12 + S2883=10 + S2884=8 + **S2885=13**).

**Full sunset-arc regression (S2869 → S2885 + `test_zoom_out_tool_2780`):** 220/220 (207 baseline S2884 close + 13 S2885).

## Post-merge cascade (this handoff)

1. **`make recycle-all`** completed at post-merge SHA `5495736fb76a`. Clean recycle event recorded in `logs/recycle_events.jsonl`.
2. **Live Rigby envelope verification** — 2/3 endpoints verified end-to-end via `deliverable_tool` + `feedback_tool`; `content_tool` blocked at OpenAI schema enum guard (feature, not bug — internal dispatcher path verified by 13/13 regression).
3. **Docs cascade PR** — this handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump + `docs/INDEX.md` refresh.
4. **`session_lifecycle close --label s2885-content-error-envelope`** at end — atomically retires `pa-42342895674d4878`, mints fresh S2886 pin, rewrites `tools/pa_local.sh`. Wrapper commit follows per `feedback_commit_wrapper_pin_bump_at_close`.

## Open items / carry-forward to S2886

### S2886 first-action decision

Chris pre-ratified at S2885 mid-slate: **Slate B pivots to criticality-first grep** across the remaining 4 files, `core.py` + `gateway.py` first (not continue file-completing on codejobs.py). Rigby's zoom-out (b) response is the substrate signal.

Concrete S2886 pre-code work: Rigby SIGN Q1 routing-map refresh across `core.py` (73 sites) + `gateway.py` (57 sites) — grep + categorize by handler criticality (write-path / auth / tenant / read-only), pick highest-risk cluster. Warm-cadence Q1 same shape as S2879/S2880/S2881/S2882/S2883.

### `/development/` checkout status

Chris designated the checkout legacy at S2885 open. Not deleted at S2885 close — Chris to decide `rm -rf` vs dormant at S2886 open. Once deleted, `feedback_post_travel_port_collision_triage` gets a follow-up note referencing this session.

### `.env` restoration triggers

Both `USE_PGBOUNCER=0` overrides (in `/Donkey_Betz/` and `/development/` `.env` files) have inline comments pointing at S2885 with restore-to-`1` trigger: "cross-repo port ownership resolved." Same holds for `PA_API_TOKEN` sync — the value is authoritative now, no revert planned.

### Forward-carried backlog (unchanged from S2884)

All prior deferred items from S2883/S2882/S2881/S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc. remain carried. See §Net-new engineering candidates in `00-START-NEXT-SESSION.md`.

### New candidates surfaced at S2885

- **Fold 1 (`TransactionTestCase` requirement) — ledger candidate.** Watch S2886 for 2nd trigger.
- **Fold 2 (false-pass on shared taxonomy codes) — ledger candidate + Playbook amendment candidate.** Watch S2886 for 2nd trigger.
- **Fold 4 (cross-repo Docker infra collision) — ledger candidate at 1st trigger.** Watch for 2nd trigger before promoting to `feedback_post_travel_port_collision_triage` extension.
- **`PA_API_TOKEN` drift alarm** (subitem of Ledger #24) — verify-cache masks the drift for weeks; consider CI check that `.env` token matches DB token for the wrapper-owning user. Deferred.

---

## S2885 close — what shipped

**Repo canonical (Claude-authored):**
- **PR #3394** `5495736fb` — S2885 slate: `td_handlers_content.py` file-completing critical-slice structured error-envelope migration (2 files, +439/-13)
- **PR `<this docs cascade>`** — S2885 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2886 open + `docs/INDEX.md` refresh

**Workspace canonical (Rigby-authored):**
- **Rigby Tool Gap Ledger entry #24** — S2884→S2885 pgbouncer auth block resolution, appended to deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` at S2885 first-action (2874 chars appended, new total 50822 chars). `tool_runs` verified.

**Runtime impact:**
- Eighth wave (second file-completing shape) of real handler migrations in the S2876 backfill sunset arc.
- Legacy-file population S2884=5 files → **S2885=4 files** (`content.py` EXITS).
- Sub-population count 176 → **163 bare-returns** across 4 remaining files.
- Regression suite grew from 207 → **220** (+13 S2885 rows).
- 13 sites no longer surface `error_code='legacy_error'`; consumers can key on 5-code taxonomy.
- No new helper introduced. No taxonomy expansion. No new PLAYBOOK amendment.
- Ledger #13 (`td_error.py` extraction) adopter count = **5/6** — 1 more adopter needed to trigger dedicated arc. Slate B is a natural trigger candidate.

**Session infra work resolved (not shipped as PR, but persisted):**
- Character-os postgres collision on `:5433` (bypassed via `USE_PGBOUNCER=0` in both `.env` files).
- Orphan Daphne from `/development/` checkout (killed; checkout designated legacy).
- 11-day-stale `PA_API_TOKEN` in `.env` (synced to current DB value).
