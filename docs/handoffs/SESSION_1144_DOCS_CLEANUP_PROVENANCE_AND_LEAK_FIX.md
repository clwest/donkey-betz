# Session 1144 — /docs/ cleanup + provenance command + socket leak fix

**Date:** 2026-05-25
**Branch state at session-checkpoint:** 5 PRs open, all pushed, all reviewable independently. Session may continue (Chris directive: walk all of /docs/ today); this handoff captures the morning's work.

---

## TL;DR

Session opened with Chris asking to walk `/docs/` together post-Session-1143 cleanup. Mid-session detour into a serious socket leak that was breaking redis-cli / Postgres / Rigby polling. Both threads landed clean:

1. **Socket leak diagnosed + fixed** (PR #2201) — 33K TIME_WAIT sockets accumulating in ~20 min (72% to Postgres). Root cause: `CONN_MAX_AGE=0` from Session 142 (Nov 2025). Modern fix: `CONN_HEALTH_CHECKS=True` + 60s reuse window. Also added per-process caching to OpenAI + Anthropic SDK factories (each call was building a fresh client with its own httpx pool).
2. **/docs/ cleanup wave** (PRs #2202–#2204) — Rigby specced a 3-PR sequence enforcing DOC_LIFECYCLE §2c (sole-counts-source rule, locked Session 1143) across CLAUDE.md + CAPABILITIES.md + 17 other docs carrying the "Session 1099 verifier" V1 boilerplate banner. Scoped excludes for `docs/docs-pattern/**` (context-kit framework master) per a new §0 boundary lock added in PR0.
3. **Doc provenance command** (PR #2205) — Chris's organizing idea: cluster docs by session of origin. Plan A shipped — `python manage.py session_provenance --session N` reads git history + frontmatter and assembles the cluster. Rigby specced + reviewed; final schema includes a `coverage` block + per-commit `match_level` / `match_source` / `session_tag_present` / `paths_touched_count` + `counts` + `scope` echo + an explicit hygiene-gap note when subject-tagged commits are missing.

Plus one operational fix: Chris was locked out of the login UI because daphne's async Redis client couldn't grab an ephemeral source port (16,381 of 16,384 in TIME_WAIT). `sudo sysctl -w net.inet.ip.portrange.first=32768` doubled the range and unblocked him. Password reset applied for `donkeyking` (he was prompted to rotate immediately).

---

## What landed — 5 merged-pending PRs

### #2201 — `fix/db-connection-pooling`
**`fix(infra): pool DB + LLM SDK connections — stop 33K TIME_WAIT leak on local`**

Commit `9d2e16a7`.

- `core/settings.py`: replace `CONN_MAX_AGE=0` with `CONN_MAX_AGE=60` + `CONN_HEALTH_CHECKS=True`. The Session 142 brute-force fix predated `CONN_HEALTH_CHECKS` (Django 4.1, Aug 2022); we're on 5.0.6.
- `core/services/openai_client_factory.py`: add `(api_key, base_url)`-keyed module-level cache so repeat callers share one client (and one internal httpx pool). `**kwargs` calls bypass cache. Forbidden-kwarg guard preserved.
- `core/services/anthropic_client_factory.py`: same pattern, keyed on resolved api_key.

**Verified:** TIME_WAIT count flat at ~33,338 across t=2m–t=6m post-restart (was growing ~21/sec startup + ~4/sec steady-state pre-fix).

**Out of scope (documented for follow-up):** 40+ inline `redis.Redis.from_url(...)` call sites across `core/tasks_agents.py`, `core/tasks_body_systems.py`, `core/tasks.py`, `core/consumers_base.py`, `core/views_*.py` need the same factory treatment. Only `core/production_websocket.py` uses `ConnectionPool` correctly today.

### #2202 — `docs/lifecycle-scope-boundary`
**`docs(lifecycle): add §0 scope boundary — u-d-b /docs/ vs context-kit framework`**

Commit `d061c0f0`. 1 file, 9 insertions.

> Edits in this session intentionally targeted the **u-d-b `/docs/` instance corpus** and excluded the **context-kit framework master** under `docs/docs-pattern/`.

Locks the distinction in `docs/00-START-HERE/DOC_LIFECYCLE.md` before any sweep crosses the line. Mechanical sweeps must exclude `docs/docs-pattern/**` by default. The two anchor docs (PLATFORM_WHAT_IT_IS narrative, PLATFORM_INVENTORY runtime) are u-d-b's **instances** of the context-kit anchor pattern.

### #2203 — `docs/entrypoints-counts-source`
**`docs(entry-points): align CLAUDE.md + CAPABILITIES.md with §2c sole-counts-source rule`**

Commit `dda4eb94`. 2 files, 16 insertions / 14 deletions.

- `CLAUDE.md`: strip "source of truth for numbers" from PLATFORM_WHAT_IT_IS references in the top banner + Key Files + Reference Documentation table. Reframe as "context-kit narrative anchor; counts in PLATFORM_INVENTORY." Delete the stale manual "PA Tools 101/166" row in Detailed Breakdown — it contradicted the autoblock above it (104/169 or 106/171 per fresh inventory).
- `CAPABILITIES.md`: flip V1 banner link target to PLATFORM_INVENTORY; add explicit "historical snapshot — do not cite as current" callout above the System Overview table.

### #2204 — `docs/banner-sweep-platform-inventory`
**`docs(sweep): flip 17 DOC-POINTER-V1 banners to PLATFORM_INVENTORY (§2c)`**

Commit `795aeba8`. 17 files, 17 insertions / 17 deletions. Mechanical.

Three patterns:
- **A** (5 docs, PWII-only): AGENTS.md, SERVICES.md, SPIDERS.md, DISCORD_INTEGRATION.md, BACKEND_REFERENCE.md
- **B** (7 docs, PWII via `../` from topics/): docs/topics/{infrastructure, agent-system, frontend, active-module-ownership-map, personal-assistant, celery-workers, initiative-pipeline}.md
- **C** (5 docs, both PWII + INVENTORY): ARCHITECTURE.md, SYSTEM_OVERVIEW.md, AUTONOMOUS_SYSTEMS.md, WIREMAP.md, DOC_LIFECYCLE.md (the V1 template example itself)

Scoped excludes honored per PR0: `docs/docs-pattern/**`, `docs/archive/**`, `docs/handoffs/**`.

### #2205 — `feat/session-provenance-command`
**`feat(provenance): session_provenance management command (Plan A scaffolding)`**

Three commits: `b58a338c` (initial) → `1689576a` (non-docs + body-fallback) → `5ae517fa` (Rigby schema review).

New `python manage.py session_provenance --session N [--format md|json]`. Reads git history + frontmatter + handoff naming to assemble the cluster for a session. Default excludes per DOC_LIFECYCLE §0.

**Final JSON shape includes:**
- `coverage` block — `matched_commits`, `subject_match_count`, `body_match_count`, `session_tag_in_subject_rate`, `coverage_warning`, `commit_hygiene_recommendation`
- `counts` block — int counts per bucket
- `scope` block — `root`, `excludes` echo
- Per-commit fields — `match_level` (HIGH/MEDIUM), `match_source` (subject/body), `session_tag_present`, `paths_touched_count`
- Buckets — `docs_created`, `docs_modified`, `non_docs_created`, `non_docs_modified`, `frontmatter_only`
- `notes` — explicit hygiene-gap callout when no subject-tagged commits exist

**Validated against:** Session 1143 (38 commits, 1 handoff, 9 docs_created, 633 docs_modified) and Session 250 (older "Session N" subject convention, 1 commit / 1 doc created — Hive Mind Mode).

---

## Themes / lessons learned

### Commit hygiene gap surfaced
Provenance command revealed only **1 of this session's 6 PR commits** carries `session-1144` in subject (this commit is the one that does: `feat(session-1144 provenance): ...`). PR0/PR1/PR2 commit bodies cite Session 1143 (the source of the rules they're enforcing) but never name Session 1144 as the SESSION they belong to. The remaining 5 surface only via body-fallback or not at all.

**Going forward:** every commit in a session should carry the session tag in subject (`docs(session-NNNN): ...`, `fix(session-NNNN): ...`, etc.) so future provenance runs are HIGH confidence by default. The tool now emits a `coverage_warning` + explicit note when this is missed.

### Outdated brute-force workarounds rot into bugs
The Session 142 `CONN_MAX_AGE=0` "fix" worked when the platform was small. With 80+ enabled beat tasks + 4 worker processes, it became a self-inflicted DoS that took down redis-cli, Postgres polling, and Rigby's API path within ~20 minutes of stack uptime. Always check whether a workaround has a modern primitive replacement (here: `CONN_HEALTH_CHECKS=True`, available since Django 4.1).

### macOS ephemeral port range can be the actual bottleneck on dev
33K outstanding TIME_WAITs against the default 16K ephemeral port range = total exhaustion. The kernel doesn't reap aggressively under sustained pressure even with `net.inet.tcp.msl=1000`. `sysctl -w net.inet.ip.portrange.first=32768` is the immediate-unblock lever; the durable fix is connection pooling everywhere.

### Context-kit/u-d-b separability needs to be explicit in cleanup ops
Without §0 in DOC_LIFECYCLE, a mechanical sweep would have rewritten 7 framework template files under `docs/docs-pattern/` as if they were u-d-b instance docs. The boundary is now a first-class rule + the provenance command's default excludes encode it too.

---

## Operational notes from this session

- **Chris locked out → password reset.** PBKDF2 hash applied via UPDATE on `core_unifieduser`. Temp delivered in chat (`Y!RVwpU*fE&@rpVTKeKCTm*N`); Chris was told to rotate immediately.
- **`sudo sysctl -w net.inet.ip.portrange.first=32768`** is the magic lever when ephemeral ports are exhausted. Reverts on reboot. Pair with `sudo sysctl -w net.inet.tcp.msl=1000` (reduces TIME_WAIT from 30s to 2s for NEW connections).
- **`make celery` doesn't restart workers when `.celery*.pid` files exist.** During the leak debug, the pa worker stuck in a Redis-connect retry loop after macOS port exhaustion. Recovery: `pkill -9 -f celery; rm -f .celery*.pid; make celery`.

---

## Carryovers — Session 1145+

### Green-lit by Rigby (provenance follow-ons)
1. **`docs/_provenance.json` persistent index** — regenerable, fed by `session_provenance` for every session 1..N. Same schema this PR adds.
2. **`search_docs` filter integration** — let agents filter chunks by `originating_session >= X` or "show cluster for session N".
3. **Selective frontmatter backfill** — add `originating_session: N` only where confidence is HIGH (subject-tagged commits). Skip MEDIUM-confidence cases.

### Process / hygiene
4. **Commit-message convention enforcement** — pre-commit hook that warns when a commit subject doesn't carry `session-NNNN`. Optional. Could be project-local hook.
5. **Redis pooling sweep** — 40+ inline `redis.Redis.from_url(...)` sites need factory treatment. Mirror the OpenAI/Anthropic pattern from #2201.

### Chris-call-only (parked from Session 1143)
6. **Decision Command backend cleanup** — 5 Python files of the regressed feature (Session 1143 finding).
7. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py` despite docstring deprecation.
8. **Mission refresh PR #2190** — preserved branch, parked per Chris's docs-only directive.

### Possibly more from rest-of-day docs walk (if session continues)
This handoff is a checkpoint; Chris signaled intent to continue walking `/docs/` after the 5 PRs land. Findings beyond this snapshot will append to this doc or open as their own PRs.

---

## Suggested merge order

| Order | PR | Why |
|---|---|---|
| 1 | **#2201** | Stops the leak. No other PR depends on it, but it's the most impactful fix and unblocks local dev. |
| 2 | **#2202** | §0 boundary lock. PR3 + PR4 explicitly depend on this being in main for clean scope. |
| 3 | **#2203** | Entry-point reframe. Visible to anyone reading CLAUDE.md / CAPABILITIES.md; lower risk than PR4. |
| 4 | **#2204** | 17-file mechanical sweep. Easy revert (one line per file). Worth landing while §2c framing is fresh. |
| 5 | **#2205** | Tooling addition. Read-only; doesn't change any other doc. Safe to land last. |

---

## Risks / rollback notes

- **#2201 (pooling):** Postgres `max_connections=100` default; with 5 workers × ~2-4 persistent conns each we hold ≤20. Well under limit. If long-lived connections cause issues (stale prepared statements, schema changes), drop `CONN_MAX_AGE` to 30s. SDK clients are documented thread-safe; the cache uses a module lock for first-call races.
- **#2204 (sweep):** Mechanical edit. If anything broke, `git revert` is a clean one-line-per-file rollback. Verified the post-sweep grep is clean.
- **#2205 (provenance):** Read-only command. No risk to existing data.

---

## Files cited in code (for the next session)

- `core/settings.py:270-279` — Postgres connection config (post-#2201)
- `core/services/openai_client_factory.py` — `_CLIENT_CACHE` + `get_openai_client()`
- `core/services/anthropic_client_factory.py` — same pattern
- `core/management/commands/session_provenance.py` — the new command
- `docs/00-START-HERE/DOC_LIFECYCLE.md:13-21` — new §0 scope boundary

---

**Co-authored with Rigby (PA) — she specced both the docs cleanup sequence and the provenance command's schema. Conversation pa-4b4784ecd989.**
