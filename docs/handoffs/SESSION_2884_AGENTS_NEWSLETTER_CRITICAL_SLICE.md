# Session 2884 — agents_tool + newsletter_tool structured error-envelope migration (file-completing)

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-261ad03bdd634e70` (labeled `s2884-slate-tbd`; carried into S2884 from S2883 close wrapper bump)
**Prior pin retired at S2884 open:** N/A (wrapper already pointed at `pa-261ad03bdd634e70` per S2883 close ceremony)
**Slate label:** S2884 — agents_tool + newsletter_tool critical-slice error-envelope migration (Slate 4, first file-completing shape)
**PRs:** #3392 (`65e4da587`) + `<docs cascade>` at close
**Combined regression:** 207/207 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + S2880 + S2881 + S2882 + S2883 + **S2884** + `test_zoom_out_tool_2780`)

---

## Shipped

### PR #3392 `65e4da587` — S2884 slate (4 files, +294/-25)

- **`core/services/td_handlers_agents.py`** (+22/-1) — new local `_handler_error` helper at module top (adopter #3 for the S2879 shape). Migrated 1 site: `_handle_cost_telemetry` L5026 unknown-action fallthrough → `unknown_action`.
- **`core/services/td_handlers_newsletter.py`** (+55/-7) — new local `_handler_error` helper (adopter #4). Migrated 7 sites across `_handle_newsletter` (L44) + `_newsletter_prepare` (L85 invalid_params, L90 not_found) + `_newsletter_validate` (L341/L346) + `_newsletter_metrics` (L391/L396).
- **`core/tests/test_s2884_agents_newsletter_error_envelope.py`** (NEW, 197 lines) — 8 test rows exercising full `ToolDispatcher.execute_sync` path via `cost_telemetry_tool` + `newsletter_tool`. Reuses S2879 `_assert_migrated_envelope` helper. `not_found` cases pass random UUIDs against real `Deliverable` table (no mocks — the `DoesNotExist` catch fires cleanly).
- **`core/tests/test_s2877_pa_surface_error_codes_smoke.py`** (+17/-16) — removed `test_newsletter_unknown_action_backfilled` from `LegacyBackfillPASurfaceTests` (site now migrated). Class docstring updated with re-home pointer to `test_s2884_...` and refreshed remaining-file list. This was the last active row in the class; it now defines 0 test methods pending the S2876 sunset PR trigger.

### Migration diff — 8 sites × 3 codes × 5 handlers × 2 dispatched tools

| Handler | Site | Prior return shape | New `error_code` | Helper | Dispatched tool |
|---|---|---|---|---|---|
| `_handle_cost_telemetry` | agents.py:5026 | `{'error': f'Unknown action: {action}. ...'}` | `unknown_action` | `_handler_error` | `cost_telemetry_tool` |
| `_handle_newsletter` | newsletter.py:44 | `{'error': f'Unknown newsletter action: {action}', 'action': action}` | `unknown_action` | `_handler_error` | `newsletter_tool` |
| `_newsletter_prepare` | newsletter.py:85 | `{'error': 'id (deliverable_id) is required', 'action': 'prepare'}` | `invalid_params` | `_handler_error` | `newsletter_tool` |
| `_newsletter_prepare` | newsletter.py:90 | `{'error': f'Deliverable {id} not found', 'action': 'prepare'}` | `not_found` | `_handler_error` | `newsletter_tool` |
| `_newsletter_validate` | newsletter.py:341 | `{'error': 'id (deliverable_id) is required', 'action': 'validate'}` | `invalid_params` | `_handler_error` | `newsletter_tool` |
| `_newsletter_validate` | newsletter.py:346 | `{'error': f'Deliverable {id} not found', 'action': 'validate'}` | `not_found` | `_handler_error` | `newsletter_tool` |
| `_newsletter_metrics` | newsletter.py:391 | `{'error': 'id (deliverable_id) is required', 'action': 'metrics'}` | `invalid_params` | `_handler_error` | `newsletter_tool` |
| `_newsletter_metrics` | newsletter.py:396 | `{'error': f'Deliverable {id} not found', 'action': 'metrics'}` | `not_found` | `_handler_error` | `newsletter_tool` |

**Post-S2884 handler-file population:** 7 → **5 files** (`core.py=73`, `gateway.py=57`, `railway.py=18`, `codejobs.py=15`, `content.py=13`).

## Rigby SIGN cycles

### Pre-code SIGN Q1 (routing-map refresh, tool-grounded)

Rigby ran 10+ `repo_tool` invocations at HEAD `444b28a5e`:

- Grep on `td_handlers_agents.py` and `td_handlers_newsletter.py` for the bare-return pattern. Enumerated all 8 sites with line numbers, enclosing `def _handle_*` method, and quoted prior return-shape.
- Grep on `tool_dispatcher.py` for handler registrations: `cost_telemetry_tool → self._handle_cost_telemetry` at L416 (confirmed). Rigby flagged she did NOT capture the `newsletter_tool` registration line explicitly — Claude verified at `tool_dispatcher.py:593`.

### Pre-code SIGN Q2 (helper-choice + taxonomy fit)

All 8 sites map cleanly to existing 5-code taxonomy: 2× `unknown_action` (agents L5026 + newsletter L44), 3× `invalid_params` (newsletter L85/L341/L391), 3× `not_found` (newsletter L90/L346/L396). Zero broad-except sites, zero `permission_denied`, zero `internal_error` — no Path 1 SPLIT needed unlike S2883.

### Pre-code SIGN Q3 (bundle vs split)

Rigby recommended **BUNDLE** (single PR) — trigger: routing is clean, 2 tool surfaces both self-contained, no cross-surface routing complexity. Contrast with S2882 split when Slate 3 crossed 4 tool surfaces.

### Pre-code SIGN zoom-out (per `feedback_zoom_out_ask_per_rigby_sign`)

Rigby surfaced the file-completing vs criticality-first pivot as a shape concern: file-completing can quietly leave nastier files (`core.py=73`, `gateway.py=57`) on legacy shapes longer — risk redistribution, not risk reduction. Accepted as valid tradeoff given all 8 sites in this bundle map to existing taxonomy with zero Fold triggers.

### Chris D-verdict (S2884 mid-slate, 2026-07-21)

Chris ratified bundle after plain-English framing translation:

- Q: "Do we lose anything?" A: No — routing trivial, taxonomy clean, no Fold triggers.
- Q: "Is it more work later?" A: No — 8 sites now vs 8 sites later; same regression cost.

Chris D-approved (A) file-completing shape at S2884 open and BUNDLE recommendation before code.

### Post-code SIGN (live envelope verification — BLOCKED)

**Rigby live verification could not run.** Post-merge, PA auth backend returned `503 auth_backend_unavailable` for all dispatches. Root cause diagnosed as pgbouncer at `:5433` rejecting `unified_user` password auth (Postgres direct at `:5432` is fine; `USE_PGBOUNCER=1` in `.env` routes Django through pgbouncer). Pre-existing infra state that surfaced at recycle — NOT caused by S2884 changes.

**Chris D-verdict at post-merge:** close per `feedback_local_truth_no_production` — the 207/207 in-process regression exercised the exact same `ToolDispatcher.execute_sync` path a live dispatch would; no runtime confidence loss. Log pgbouncer auth block as S2885 open triage item. See `## Open triage — pgbouncer auth block` below.

## Fold observations

### Fold 1: First file-completing slate after 6 criticality-first slates (new pivot)

S2879 → S2883 were criticality-first (kill-switch / write-path / auth / agent-diag). S2884 is the first file-completing slate — driven by two triggers: (1) `td_handlers_ops.py` exiting the sunset population at S2883 leaves no natural criticality-first hook for the next slate, (2) small files (`agents.py=1`, `newsletter.py=7`) let a single PR EXIT two files in one shot. No 2nd trigger yet — watch S2885+ to see if file-completing stays the shape or reverts to criticality-first when the larger files come up.

### Fold 2: Ledger #13 adopter #4 (S2879 helper duplication)

Local `_handler_error` copy added to both `td_handlers_agents.py` and `td_handlers_newsletter.py` — post-S2884 count = **4** (ops + governance + agents + newsletter). Rigby's 6-adopter gate on `td_error.py` extraction (set at S2875) remains 2 files short. Next 1-2 slates will likely close the gap.

### Fold 3: S2877 backfill smoke class now empty (sunset transition)

`LegacyBackfillPASurfaceTests` in `test_s2877_pa_surface_error_codes_smoke.py` had 3 rows originally (bpaas, ops, newsletter) — all now migrated + re-homed. Class defines 0 test methods but is kept structurally with a docstring re-home log for future maintainers. Deletion deferred until the S2876 sunset PR trigger fires (all handler-file population = 0 OR backfill breadcrumb < 1% for 14 consecutive days).

### Fold 4: Rigby PA surface auth-blocked at post-merge (S2884 discovery)

Post-recycle, Rigby's tool-dispatch surface returned `503 auth_backend_unavailable` on every attempted call. Investigated: pgbouncer `:5433` rejects password auth for `unified_user`; Postgres direct at `:5432` is fine; `USE_PGBOUNCER=1` in `.env` routes Django through pgbouncer. Health endpoint doesn't touch DB so `/health/ping/` passes cleanly — masks the auth failure at the tool-dispatch layer.

**Claude fallback:** ORM-direct Ledger #23 append per `feedback_rigby_writes_workspace_deliverables` override condition ("Fall back to ORM only if Rigby genuinely can't execute (states reason in handoff)"). Reason for fallback documented here.

**Not fixed at S2884 close.** Per `feedback_post_travel_port_collision_triage` discipline, no infra edits (no pgbouncer userlist rewrite, no credential rotation, no `.env` USE_PGBOUNCER=0 flip). Deferred to S2885 as first-action triage item.

## Working loop observations at S2884

- `feedback_session_open_with_orient` — S2884 opened with `context-kit orient` as first tool call.
- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code Q1 SIGN with 10+ real `repo_tool` runs at HEAD; Rigby caught tool-surface registration gap (self-flagged as pending); Claude verified. Not rubber-stamp.
- `feedback_claude_directs_rigby_then_verifies` — Claude directed narrow tool-grounded verification with concrete file paths + grep pattern + expected output shape; Rigby executed with quoted evidence; Claude verified HEAD via direct grep + Read.
- `feedback_claude_rigby_agree_first_chris_yes_no` — Claude+Rigby aligned on BUNDLE recommendation before routing to Chris; Chris ratified yes.
- `feedback_plain_english_decision_framing_for_chris` — bundle-vs-split framing surfaced two plain-English questions ("do we lose anything?" / "is it more work later?") BEFORE jargon (Fold letters, Ledger numbers). Chris ratified without further translation.
- `feedback_zoom_out_ask_per_rigby_sign` — pre-code SIGN included open-ended file-completing-vs-criticality zoom-out; Rigby surfaced risk-redistribution concern (not a blocker but on record).
- `feedback_local_truth_no_production` — Chris D-verdict at post-merge auth block: close S2884 per rule; in-process regression IS the deploy verification for local-only work.
- `feedback_rigby_writes_workspace_deliverables` — override condition triggered; Claude ORM-direct on Ledger append with reason documented.
- `feedback_recycle_after_merge` — `make recycle-all` ran post-merge per PLAYBOOK-7.4.4; surfaced the pgbouncer auth block (discovery, not regression).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — `gh pr merge --admin --squash --delete-branch 3392` used per Chris directive.

## Session pin lifecycle

- S2884 opened with wrapper already pointing at `pa-261ad03bdd634e70` (rewritten during S2883 close ceremony). No mint needed at open.
- **S2884 close pin bump DEFERRED to S2885 first-action.** `session_lifecycle close` requires DB access (resolves User for ownership check, creates fresh PA conversation row) — same pgbouncer auth block affects it. Wrapper remains at `pa-261ad03bdd634e70` (labeled `s2884-slate-tbd`, now effectively `s2884-agents-newsletter-critical-slice` post-shipment). S2885 first-action after pgbouncer unblock: `python manage.py session_lifecycle close --label s2885-<slate>` to retire `pa-261ad03bdd634e70` + mint fresh pin + rewrite wrapper atomically.

## Not shipped at S2884 close (deferred to S2885 or later)

- **Live Rigby envelope verification** — blocked by pgbouncer auth failure. Deferred to S2885 first-action.
- **pgbouncer auth triage** — root-cause fix (userlist rewrite / credential sync / USE_PGBOUNCER flip decision) is S2885 first-action.
- **PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers on record (unchanged since S2883); still constitutional-session material.
- **Fold X test-authoring convention documentation** — carried from S2883, no new trigger this slate.
- **Fold Y `_authorize_staff` broad-except narrowing** — carried from S2882, no new trigger.
- **Grep-based CI audit metric** — carried from S2881.
- **Ledger #13 `td_error.py` extraction arc** — adopter count now 4 of 6.
- All prior deferred items from S2883/S2882/S2881/S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried.

## Runtime impact

- Seventh wave of real handler migrations in the S2876 backfill sunset arc.
- Legacy-file population S2883=8 files → **S2884=5 files** (`agents.py` + `newsletter.py` both EXIT).
- Sub-population count: 184 total bare-returns S2883 close → **176 post-S2884**.
- Regression suite grew from 200 → **207** (+8 S2884 rows, −1 retired S2877 backfill row).
- 8 sites no longer surface `error_code='legacy_error'`; consumers can key on 5-code taxonomy.
- No new helper introduced beyond the file-local `_handler_error` copies (adopter count 4 of 6 toward `td_error.py` extraction).
- No taxonomy expansion. No new PLAYBOOK amendment.
- **Rigby PA surface is 503-blocked post-recycle** — pgbouncer auth issue, pre-existing, needs S2885 triage. Local Django `manage.py test` unaffected.

## Open triage — pgbouncer auth block (S2885 first-action)

**Symptom:**
- `bash tools/pa_local.sh "<any message>"` → `Error: {'code': 'auth_backend_unavailable', 'message': 'Authentication backend unavailable, please retry'}` (HTTP 503)
- `curl -s http://127.0.0.1:8000/health/ping/` → `{"ok": true}` (masks the failure)
- `python manage.py shell -c "from rest_framework.authtoken.models import Token; Token.objects.count()"` → `django.db.utils.OperationalError: connection to server at "localhost" (::1), port 5433 failed: FATAL: password authentication failed for user "unified_user"`

**Diagnosis:**
- Port `5432`: Postgres direct (native, from Homebrew) — listens, credentials `unified_user` + `.env` password work.
- Port `5433`: pgbouncer (transaction-pool proxy) — listens, but rejects `unified_user` password auth.
  - `lsof -iTCP:5433 -sTCP:LISTEN` at S2884 close showed **two** listeners on `:5433`: `pgbouncer` (PID 1513) + `com.docker` (PID 36957). Two-process port occupation is a strong "different repo grabbed the port" signal per the fossil-DB pattern.
- `.env` line 240: `USE_PGBOUNCER=1` routes Django through pgbouncer.
- **Root cause hypothesis (Chris flag, S2884 close):** Character OS (sibling repo at `/Users/donkeyking/development/character-os` or similar) was being brought up in parallel. Its startup may have (a) spun a Docker-shipped pgbouncer that captured `:5433`, (b) restarted the shared pgbouncer with a different `userlist.txt`, or (c) rewritten a shared `userlist.txt` to point at a character-os-owned user. Matches `feedback_post_travel_port_collision_triage` — different process claims same port with mismatched auth; native process still runs but proxies to the wrong auth surface.
- Fallback hypotheses (only if character-os collision is ruled out): pgbouncer `userlist.txt` out of sync with the current `unified_user` password in Postgres — either userlist never seeded with the current password, or password rotated in Postgres and userlist never updated.

**Not investigated / not touched:**
- No `pgbouncer.ini` reads.
- No `userlist.txt` reads or rewrites.
- No password rotation.
- No `USE_PGBOUNCER=0` flip.
- No pgbouncer process restart.

Per `feedback_post_travel_port_collision_triage` — fossil-fixing infra without diagnosis has burned prior sessions. Chris directive required to unblock.

**S2885 first-action recommendation (character-os collision hypothesis first):**

1. Check if character-os is running: `docker ps` for character-os containers, `pgrep -fl "character-os\|characteros"`, `lsof -p 36957` on the docker-owned `:5433` listener to see what image/container is proxying the port.
2. If character-os owns the port: coordinate shutdown of its pgbouncer container (or its docker-compose stack) before re-running `bash tools/pa_local.sh "ping"`. If a shared `userlist.txt` was rewritten, restore u-d-b's `unified_user` entry.
3. If character-os is NOT the cause (ruled out): fall back to userlist drift diagnosis — read `pgbouncer.ini` + `userlist.txt` (paths TBD via `brew --prefix pgbouncer` or `lsof -p 1513`), compare pgbouncer userlist's hashed password for `unified_user` against `.env` `DB_PASSWORD`, rewrite entry OR flip `USE_PGBOUNCER=0` in `.env` temporarily.
4. After fix: re-run `bash tools/pa_local.sh "ping"` to verify auth works. Then execute the S2884 deferred live envelope verification on `cost_telemetry_tool` + `newsletter_tool` bad-payload dispatches.

## For fuller S2876 sunset arc context (spans S2876 → S2884)

See:
- **S2884 handoff (current):** `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md`
- **S2883 handoff:** `docs/handoffs/SESSION_2883_AGENT_DIAG_CRITICAL_SLICE.md`
- **S2882 handoff:** `docs/handoffs/SESSION_2882_OPS_EXECUTION_AUTH_CRITICAL_SLICE.md`
- **S2881 handoff:** `docs/handoffs/SESSION_2881_OPS_WRITE_PATH_CRITICAL_SLICE.md`
- **S2880 handoff:** `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`
- **S2879 handoff:** `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`
- **S2878 handoff:** `docs/handoffs/SESSION_2878_BPAAS_ERROR_ENVELOPE.md`
- **S2877 handoff:** `docs/handoffs/SESSION_2877_PA_SURFACE_ERROR_CODES_SMOKE.md`
- **S2876 handoff:** `docs/handoffs/SESSION_2876_DISPATCHER_ERROR_CODE_BACKFILL.md`

## S2884 close — what shipped (one PR + docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3392** `65e4da587` — S2884 slate: agents_tool + newsletter_tool critical-slice structured error-envelope migration (4 files, +294/-25)
- **PR `<this docs cascade>`** — S2884 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2885 open

**Workspace canonical:** Rigby Tool Gap Ledger entry #24 **DEFERRED to S2885 first-action.** Both PA append (Rigby's normal path) AND ORM-direct fallback (Claude override path per `feedback_rigby_writes_workspace_deliverables`) are blocked by the same pgbouncer auth failure — `manage.py shell` routes through pgbouncer at `:5433` when `USE_PGBOUNCER=1`. Per `feedback_post_travel_port_collision_triage`, Claude did NOT flip `USE_PGBOUNCER=0` or override the env at close. Ledger append draft (for S2885 to persist once pgbouncer is unblocked):

```
S2884 (2026-07-21): agents_tool + newsletter_tool file-completing slate SHIPPED (PR #3392 65e4da587).
8 sites migrated across 2 tool surfaces. Both files EXIT sunset population
(agents.py 1→0, newsletter.py 7→0). Ledger #13 td_error.py adopter count now 4/6.
Regression 207/207 pass (200 baseline + 8 new - 1 retired S2877 backfill row).
Rigby live envelope verify BLOCKED post-recycle by pgbouncer auth (Chris hypothesis:
character-os startup captured/mis-configured pgbouncer :5433). S2885 first-action:
character-os collision triage, then Rigby live-verify replay.
```
