# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars.

## SOURCE OF TRUTH

Per Session 1144 PR #2208 (canon rebase), the canonical entry points are:

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`). Regenerate with `python manage.py generate_platform_inventory`.
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts). Regenerate with `python manage.py build_docs_index`.
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution (V1/V2 pointer headers, §0 scope boundary, §2b runtime-coupled paths, §2c sole-counts-source rule, §3 root-stability).
5. **`docs/AUDIT_INDEX.md`** — audit taxonomy (`audit/` current vs `audit-2026/` April historical vs `audits/` pre-2026 archive).
6. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
7. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
8. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
9. **`docs/specs/`** — engineering specs (Atlas-anchored).
10. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`** (both upstream).
- `python scripts/verify_repo_guardrails.py`
- **NEW Session 1144:** `python manage.py session_provenance --session N` — clusters docs+code by session of origin. Default excludes `docs/archive/`, `docs/docs-pattern/`. See PR #2205.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## NEW Session 1144: COMMIT-MESSAGE HYGIENE RULE

Every session-NNNN commit subject should include `session-NNNN` somewhere. Preferred form:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Why: `session_provenance` (shipped #2205) flags `coverage_warning: true` when no subject-tagged commits exist for a session. Session 1144's own 11 commits had only 1 subject-tagged (`feat(session-1144 provenance): ...`); the rest matched only via body fallback at MEDIUM confidence. Future sessions should aim for ≥80% subject-tagged.

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra   # private repo: github.com/clwest/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compat shims only.
- Rigby resolves `global` vs `workspace` mode from request/profile/context.
- **PA tool registration needs BOTH daphne AND celery restart.** Each celery worker loads its own tool registry. `pkill -f "daphne -b 127.0.0.1 -p 8000"; pkill -f "celery -A core"; make start && make celery`.
- **`make celery` doesn't restart workers if `.celery*.pid` files exist.** Add `rm -f .celery*.pid` between pkill and make celery.

---

## SESSION 1144 CLOSED CLEAN (2026-05-25)

**10 PRs open in review queue.** Full handoff: [`docs/handoffs/SESSION_1144_DOCS_CLEANUP_PROVENANCE_AND_LEAK_FIX.md`](docs/handoffs/SESSION_1144_DOCS_CLEANUP_PROVENANCE_AND_LEAK_FIX.md).

Highlights:
- **#2201** Postgres `CONN_MAX_AGE=60` + `CONN_HEALTH_CHECKS=True` + per-process caching in OpenAI/Anthropic SDK factories — stops 33K TIME_WAIT leak (72% to :5432) caused by Session 142's `CONN_MAX_AGE=0` brute-force.
- **#2202–#2204** Three-PR docs cleanup: §0 scope boundary, CLAUDE+CAPABILITIES reframe, 17-doc banner sweep — enforces §2c sole-counts-source across active corpus.
- **#2205** `session_provenance` management command (Plan A) — clusters docs+code by session of origin. Validated against Session 1143 (38 commits, 9 docs created, 633 modified). Schema includes `coverage` + per-commit `match_level` + `paths_touched_count`.
- **#2206** This handoff.
- **#2207** `build_docs_index` fixes: "Current Session" was 6 sessions stale (regex picked first match); INDEX.md itself published hardcoded stale counts (meta-§2c violation).
- **#2208** Canon rebase — removed deprecated DaVinci entry, seeded with 5 real anchors (PLATFORM_INVENTORY + DOC_LIFECYCLE + INDEX + 00-START-NEXT-SESSION + AUDIT_INDEX), added "canon ≤10 docs" operating principle.
- **#2209** Spec status cleanup — 2 FLEET_MOVE specs `spec` → `implemented`.
- **#2210** Plans labeled historical — 13 files (11 V1 banners + INDEX rewrite + B-full status corrected, git-verified shipped via PR #2016/#2017/#2018).

**Operational:** password reset for `donkeyking` (Chris was locked out due to ephemeral-port exhaustion blocking daphne's async Redis subscriber). Two sysctl tunes: `net.inet.tcp.msl=1000` + `net.inet.ip.portrange.first=32768`.

---

## SESSION 1145 — CURRENT ENTRY POINT

### FIRST THING this session

Decide what to merge from the Session 1144 PR queue. Rigby's recommended merge order is in the handoff doc (Table at end of "ADDENDUM"). If anything needs revisions before merge, surface it now before starting new work.

### Top priority — Architecture sweep (Rigby pre-specced)

**Target:** `docs/architecture/` — the biggest remaining "canonical but stale" zone in the corpus.

**Sweep rules (apply in order):**
1. Identify "entry point" docs first (indexes / maps / overviews).
2. For each, enforce:
   - V1 banner present pointing to `PLATFORM_INVENTORY` for counts (per §2c).
   - No hardcoded counts in body.
   - If stale-but-canonical: add `Last verified Session ####` line + `Refresh-in-place; do not move` note.
   - If superseded by another doc: V2-Deprecated banner + pointer to replacement.
3. Prefer **pointer edits** over content edits (Option B principle from Session 1144's `docs/plans/` sweep — make drift visible without breaking links).

**Files to expect:** `docs/architecture/` has multi-agent / AI-assistant / sports-betting / system-map docs. Several carry V1 banners already (from earlier work) — verify they point to PLATFORM_INVENTORY, not PLATFORM_WHAT_IT_IS.

### Provenance Plan B (Rigby green-lit, can be parallel)

1. **`docs/_provenance.json` generation** — regenerable, builds for every session 1..N using `session_provenance` Plan A's schema.
2. **`search_docs` filter integration** — add `originating_session` filter so agents can find docs by session cluster.
3. **Selective frontmatter backfill** — add `originating_session: N` only where match_level=HIGH (subject-tagged commit).

### Remaining sweep targets (after architecture)

- `docs/apps/` — `rigby_standalone_BRIEF.md`, `colorado_family_law_concierge_FUTURE_CONCEPT.md`, signal-studio brief, etc.
- `docs/governance/SYSTEM_OWNER.md` — passes §2c already; staleness check
- `docs/missions/CURRENT_MISSION.md` — runtime-coupled (agents read it), stale; **parked per Chris's docs-only directive** but unparkable if Chris reopens GTM
- `docs/reports/` — large pile of historical reports
- `docs/patents/` — patent disclosures
- Root-level untouched: `24_7_GLOBAL_AI_APP_ATLAS.md`, `COST_SURVIVAL_AUDIT.md`, `BEAT_AUDIT.md`, `ML_AUDIT.md`, `PA_TOOL_AUDIT.md`, `RUNTIME_AUDIT.md`, `MANAGEMENT_COMMAND_AUDIT.md`, `AGENT_OUTPUT_TO_UI_MAPPING.md`, more
- **Non-docs:** Redis pooling sweep — 40+ inline `redis.Redis.from_url(...)` sites need factory treatment (mirror OpenAI/Anthropic from #2201)

### Chris-call-only carryovers (parked from Session 1143; still parked)

1. **Decision Command backend cleanup** — 5 Python files (regressed feature).
2. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
3. **Mission refresh PR #2190** — preserved branch.

### Session 1144 lessons to apply

- **Rigby drives sweep design.** She specced PR0→PR2 sequence + canon strategy + plans Option B. Keep handing her the wheel when scope decisions matter.
- **Verify before claiming.** Used `git log --grep` to confirm B-full actually shipped before flipping ticket status. Don't trust "Status: Queued" without git verification when fixing aged docs.
- **Subject-tag every commit with `session-NNNN`** (see hygiene rule above).
- **macOS ephemeral-port pressure** is a real local-dev concern. Pool DB + LLM clients always; flag Redis next.
- **`make celery` + stale pid files** blocks worker restart. Use `pkill -9 -f celery; rm -f .celery*.pid; make celery`.

---

## RECENT SESSION ARCS (read for context if cold-starting)

- **Session 1143** — Deep `/docs/` audit + Phase 5 cleanup. Methodology lock in `DOC_LIFECYCLE.md` (V1/V2 pointer headers + §0 scope + §2b runtime-coupled paths + §2c sole-counts-source). 39 Cat-B root docs archived + 72 frozen-subdir files + 457 pre-Session-800 handoffs. DaVinci sunset. Reality-score retired.
- **Session 1142** — docs hygiene + `search_docs` PA tool (chunked /docs/ retrieval). 852 active docs embedded + 19,305 chunks in `.rag/corpus.jsonl`.
- **Sessions 1138-1141 arc** — Decision-13 paid-interest demand-gate, entity-token clusterer, judge-stats endpoint, Chris ratification of Jessica's 22 decisions, action-card pre-generation vertical slice, pgvector blocker closed.
- **Earlier:** see `docs/handoffs/CURRENT.md` for latest two-handoff pointer.
