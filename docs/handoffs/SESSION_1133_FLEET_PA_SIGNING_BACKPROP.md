---
title: "Session 1133 — FLEET_* env back-prop, 5 of 5"
date: 2026-05-23
status: active
session: 1133
previous_handoff: SESSION_1132_LIVE_REFRESH_AND_PA_AUDIT.md
---

# Session 1133 — All 7 fleet apps now sign PA-chat

> **Read this if** you want to know how the audit table went from
> "mostly bearer_only" to "fleet_signature for all 7 fleet apps,"
> what the goal metric per repo looks like in practice, or what
> remains before flipping reject-mode on `/api/pa/chat/`.

## TL;DR

Session 1132 (B-scaffold) shipped the warn-only PA-chat audit
table. Session 1133's lock from Rigby was to make the audit
table actually USEFUL by getting `auth_mode=fleet_signature` rows
from every fleet app — the prerequisite signal for the eventual
reject-mode flip.

5 small PRs opened, one per remaining fleet repo. All goal
metrics achieved + bearer-only canary intact. No code changes
— `brain_client.py` was already wired with
`fleet_path="/api/pa/chat/"` in every repo; these PRs just
populate the FLEET_* env vars that activate the HMAC signing.

| Repo | PR | Identity provisioned |
|---|---|---|
| mentorforge | [#19](https://github.com/clwest/mentorforge/pull/19) | `fs_mentorforge_k1` |
| pitchdeckforge | [#18](https://github.com/clwest/pitchdeckforge/pull/18) | `fs_pitchdeckforge_k1` |
| sellerpilot | [#12](https://github.com/clwest/sellerpilot/pull/12) | `fs_sellerpilot_k1` |
| dealflowtracker | [#16](https://github.com/clwest/dealflowtracker/pull/16) | `fs_dealflowtracker_k1` |
| compliancesentinel | [#12](https://github.com/clwest/compliancesentinel/pull/12) | `fs_compliancesentinel_k1` |

When all 5 land + the prior 1131/1132 signal-studio PR stack
merges, **all 7 fleet repos** (contract-concierge from 1129,
signal-studio from 1131 Phase 1, these 5 from 1133) will be
signing PA-chat requests. Confirmed by audit telemetry below.

## Rigby's 1133 locks (conversation pa-d19c1674b936)

All 5 PRs honor these:

1. **5 small PRs, not one ops-rollup.** Easier rollback +
   isolated failures + easier review.
2. **Identical env var names across all repos** to avoid drift:
   `FLEET_APP_SLUG` / `FLEET_KEY_ID` / `FLEET_SERVICE_SECRET`.
   Same shape as contract-concierge (1129) and signal-studio
   (1131 Phase 1).
3. **Goal metric per repo** — at least one audit row showing
   ALL three:
   - `auth_mode='fleet_signature'`
   - `verified_app_slug='<that app>'`
   - `has_fleet_identity=True`
   **Achieved for all 5 repos.**
4. **Bearer-only canary per repo** — confirm bearer-only paths
   still get audited as `bearer_only` and remain fail-open. All
   5 verified: `ok=True` + `auth_mode=bearer_only` + `match=NULL`.
5. **Audit row is source of truth, NOT request success** — given
   the DRF auth-classifier weirdness from 1132, treat the audit
   row as authoritative. Followed throughout.

## Audit-table state (live, end of session)

```
total rows: 16

by auth_mode:
  bearer_only: 7        ← 5 canary smokes + 2 older test rows
  fleet_signature: 7    ← 5 from this session (one per new repo) + 1 signal-studio + 1 older
  session_user: 2       ← older test rows

fleet_signature rows by verified_app_slug:
  compliancesentinel: 1
  dealflowtracker: 1
  sellerpilot: 1
  pitchdeckforge: 1
  mentorforge: 1
  signal-studio: 1
  '': 1                  ← older test row, predates the dict-access fix
```

**Contract-concierge note**: was provisioned back in Session 1129
and has had `FLEET_*` env vars set since then. No live audit row
generated during this session (no PA chat call from
contract-concierge), but its identity exists and would produce a
`fleet_signature` row on the next call.

## What ships (per repo, identical pattern)

- `.env.example`: documents the canonical FLEET_* block + the
  `python manage.py provision_fleet_identity --app-slug <name>`
  command on u-d-b
- `docker-compose.yml`: passes the FLEET_* env vars to the API
  container

No Python code changes. `brain_client.py` is byte-identical
across all 7 fleet repos and was already wired with
`fleet_path="/api/pa/chat/"`. The PRs just complete the env-var
side.

## Smoke recipe (canonical for future fleet-app additions)

For each new fleet app added to the network:

```bash
# 1. Provision identity on u-d-b
cd ~/development/unified-donkey-betz
.venv/bin/python manage.py provision_fleet_identity \
    --app-slug <new-app-slug> \
    --name "<human readable>"
# (raw secret printed exactly once — save immediately)

# 2. Add to the new app's .env / docker-compose.yml
# (mirror contract-concierge's docker-compose.yml + .env.example)
FLEET_APP_SLUG=<new-app-slug>
FLEET_KEY_ID=fs_<newappslug>_k1
FLEET_SERVICE_SECRET=<raw secret from step 1>

# 3. Recreate container
cd ~/development/<new-app>
docker compose up -d --force-recreate <new-app>_api

# 4. HMAC smoke
docker exec <new-app>_api python -c \
    "from app.brain_client import ask; print(ask('hmac smoke').get('ok'))"
# expect: ok=True

# 5. Audit row check
cd ~/development/unified-donkey-betz
.venv/bin/python manage.py shell -c "
from core.models.fleet import FleetPAChatAuditRow
for r in FleetPAChatAuditRow.objects.filter(
    verified_app_slug='<new-app-slug>'
).order_by('-created_at')[:1]:
    print(r.auth_mode, r.has_fleet_identity, r.verified_app_slug, r.match)
"
# expect: fleet_signature True <new-app-slug> True

# 6. Bearer-only canary
docker exec -e FLEET_KEY_ID= -e FLEET_SERVICE_SECRET= <new-app>_api python -c \
    "from app.brain_client import ask; print(ask('bearer canary').get('ok'))"
# expect: ok=True (fail-open intact)
```

## Memory deltas

No new memory entries this session. The existing rules
(HMAC sign-key = SHA256(secret), `init_db()` doesn't migrate,
fleet_identity is a dict, Docker `--force-recreate`) all
applied without exception across the 5 repos.

## Open carryovers

### (Y) Reject-mode flip in unified_pa_chat

Rigby's hard rule from 1132: `(Y)` flip requires `(X)` done AND
"≥3 days of clean audit telemetry" — no bearer-only calls from
fleet apps, no mismatches between claimed and verified.

**(X) is now done.** The 3-day window starts ticking from when
Chris merges the 5 PRs. Once telemetry shows only
`fleet_signature` rows from fleet apps (no `bearer_only` rows
with `claimed_app_slug != ''` from a fleet app), flipping is
safe.

For a laptop-local fleet with no production traffic, the 3-day
window mostly verifies that no human error reintroduces
bearer-only calls. Rigby can decide whether to compress this
window given the local-only deployment shape.

### (A) Action-card pre-generation for curated

Still deferred per the Phase 1 close forward note. Rigby's
locked shape: u-d-b pre-generates, payload-or-child-rows,
signal-studio renders.

### Open PR stack (current state)

When Chris is ready to review/merge, the order is:

```
u-d-b:
  main
    ↑ docs/session-1131-close            (#2139)
    ↑ docs/session-1131-phase-2-close    (#2141)
    ↑ docs/session-1132-close            (#2143)
    ↑ docs/session-1133-close            (this branch when it lands)

    feat/signal-studio-phase-1-pull-endpoint  (#2138)
      ↑ feat/phase-2-signal-curator-agent     (#2140)
        ↑ feat/pa-chat-audit-scaffold         (#2142)

signal-studio:
  main
    ↑ feat/phase-1-fleet-signal-ingest    (#12)
      ↑ feat/phase-2-curated-signals      (#13)
        ↑ feat/curated-live-refresh       (#14)

5 fleet repos (each independent of the others):
  mentorforge#19, pitchdeckforge#18, sellerpilot#12,
  dealflowtracker#16, compliancesentinel#12
```

13 PRs total across the 1131–1133 arc. The 5 fleet-repo PRs are
all independent (one per repo); merge order doesn't matter
across them.

## Recommended Rigby coordination for next session

If the 5 PRs have merged by next session start AND audit
telemetry shows clean fleet_signature rows (no surprise
bearer-only fleet-app traffic), brief Rigby with:

1. The audit-table snapshot at session start
2. Whether the 3-day window from 1132 still applies given
   laptop-local deployment
3. Confirmation that all 7 fleet repos are signing in their
   current container state

Then she can lock (Y) for the reject-mode flip OR redirect to
(A) if Chris wants visible UX work instead.

If telemetry shows bearer-only fleet-app rows (i.e. someone
reverted the env vars or one of the 5 PRs hasn't merged),
priority for next session is to fix that first — reject-mode
without clean telemetry would break PA chat for fleet apps.

---

*Session 1133 closed 2026-05-23.*
