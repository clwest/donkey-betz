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
- `python manage.py session_provenance --session N` — clusters docs+code by session of origin (PR #2205).
- **NEW Session 1145:** `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json` (per-doc origin index; consumed by `search_docs(originating_session=N)` per PR #2213).

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN` somewhere. Preferred form:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

`session_provenance` flags `coverage_warning: true` when no subject-tagged commits exist for a session. Session 1145's commits were all subject-tagged — keep that streak.

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
- **Session 1145 P2 note:** `search_docs` originating_session filter caches `_provenance.json` per process (`lru_cache(1)`). After `build_docs_provenance` regen, restart workers for cached value to refresh.

---

## SESSION 1145 CLOSED CLEAN (2026-05-25)

**3 PRs open in review queue.** Full handoff: [`docs/handoffs/SESSION_1145_ARCHITECTURE_SWEEP_AND_PROVENANCE_PLAN_B.md`](docs/handoffs/SESSION_1145_ARCHITECTURE_SWEEP_AND_PROVENANCE_PLAN_B.md).

| PR | Branch | Files | What |
|----|--------|-------|------|
| **#2211** | `docs/session-1145-architecture-entrypoints` | 2 (+53/-364) | `docs/architecture/{INDEX,README}.md` rewrite as folder-local nav |
| **#2212** | `docs/session-1145-architecture-banner-sweep` | 8 (+53/-0) | V1/V2 banners on 8 unbannered architecture docs (3 V1 + 5 V2) |
| **#2213** | `docs/session-1145-provenance-plan-b` | 8 (+32711/-4) | `_provenance.json` index + `search_docs` filter + backfill command + 6 passing tests |

After this session + #2211 + #2212 merge, **22 of 24** docs in `docs/architecture/` carry V1/V2 banners (the remaining 2 are folder-local nav handled by #2211).

Rigby's recommended merge order if Chris wants "max value first": **#2213 → #2211 → #2212** (no hard constraints; all independent).

Plus the handoff PR for this file + the handoff doc + CURRENT.md pointer shift.

---

## SESSION 1146 — CURRENT ENTRY POINT

### FIRST THING this session

Decide what to merge from the Session 1145 PR queue. Rigby's recommended order is `#2213 → #2211 → #2212`. If anything needs revisions before merge, surface it now before starting new work.

### Top priority — Root-level audits sweep (Rigby-approved)

**Target:** root-level `docs/*.md` audit files — the highest drift-risk truth surfaces.

**Files to expect** (not exhaustive):

- `docs/24_7_GLOBAL_AI_APP_ATLAS.md` — strategy anchor (canonical — refresh-in-place if drifted)
- `docs/COST_SURVIVAL_AUDIT.md` — Phase 0 gating constraints
- `docs/BEAT_AUDIT.md`, `docs/ML_AUDIT.md`, `docs/PA_TOOL_AUDIT.md`, `docs/RUNTIME_AUDIT.md`, `docs/MANAGEMENT_COMMAND_AUDIT.md`
- `docs/AGENT_OUTPUT_TO_UI_MAPPING.md`
- Other root-level audit/audit-style docs

**Sweep rules** (same as architecture sweep from Session 1145):

1. Identify which are canonical vs superseded.
2. For each, enforce:
   - V1 banner pointing to `PLATFORM_INVENTORY` for counts (per §2c).
   - No hardcoded counts in body.
   - If stale-but-canonical: add `Last verified Session ####` line + `Refresh-in-place; do not move` note.
   - If superseded: V2-Deprecated banner + pointer to replacement.
3. Prefer **pointer edits** over content edits (Option B principle from Session 1143/1144).
4. Hand scope calls to Rigby before starting (per Session 1144/1145 lesson: she drives sweep design).

### Parallel-ok — Rigby's 3 greenlit Plan B follow-ups

(All approved end of Session 1145; can run in parallel with audit sweep.)

1. **P3.5: broader backfill rules.** Add NEW frontmatter blocks (not just update existing) for HIGH-confidence docs in `docs/handoffs/**`, `docs/specs/**`, optionally `docs/canon/**`. Cap 50 files per PR. Minimal frontmatter: `originating_session`, `provenance_confidence`, optional `provenance_note: "auto-added by backfill_doc_provenance"`. No content edits beyond block insertion.
2. **`exists_on_disk: false` flag for dead paths.** 326 entries in `_provenance.json` point at files git history records but no longer exist. Mark explicitly (don't delete), exclude from default consumers unless requested.
3. **Beat-schedule the regen.** Weekly Celery beat task (Sunday early morning) to rebuild `_provenance.json`. No LLM, no DB, ~10s. Log single-line summary (total/HIGH/MEDIUM/UNKNOWN/dead).

### Remaining sweep targets (after root-level audits)

- `docs/apps/` — `rigby_standalone_BRIEF.md`, `colorado_family_law_concierge_FUTURE_CONCEPT.md`, signal-studio brief, etc.
- `docs/governance/SYSTEM_OWNER.md` — passes §2c already; staleness check.
- `docs/missions/CURRENT_MISSION.md` — runtime-coupled (agents read it), stale; **parked per Chris's docs-only directive** but unparkable if Chris reopens GTM.
- `docs/reports/` — large pile of historical reports.
- `docs/patents/` — patent disclosures.
- **Non-docs:** Redis pooling sweep — 40+ inline `redis.Redis.from_url(...)` sites need factory treatment (mirror OpenAI/Anthropic from #2201).

### Chris-call-only carryovers (still parked)

1. **Decision Command backend cleanup** — 5 Python files (regressed feature).
2. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
3. **Mission refresh PR #2190** — preserved branch.

### Session 1145 lessons to apply

- **Rigby drives sweep design.** She specced PR1/PR2 split, banner-classification rubric, two V1 overrides, P3 wording convention, Plan B sub-task ordering. Keep handing her the wheel on scope.
- **Origin = `min(sessions_touched)`, not max-confidence later attribution.** Confidence reflects the FIRST commit that introduced the doc's session, not whichever later commit was subject-tagged.
- **`git log --name-only` + `--pretty=format:` interleaves files into format output.** Single-pass parsing breaks; use two passes (metadata via ASCII US/RS delimiters, file list via separate call merged by SHA). Saved as feedback memory.
- **`lru_cache(1)` on file loads needs worker restart to refresh.** `_load_provenance_docs()` won't pick up a new `_provenance.json` until daphne + celery restart.

---

## RECENT SESSION ARCS (read for context if cold-starting)

- **Session 1144** — `/docs/` cleanup wave (10 PRs): CONN_MAX_AGE=60 socket-leak fix, §0 scope boundary, CLAUDE+CAPABILITIES reframe, 17-doc banner sweep, `session_provenance` Plan A scaffolding, canon rebase (≤10 docs), spec status cleanup, historical plan labeling. Commit-message hygiene rule introduced.
- **Session 1143** — Deep `/docs/` audit + Phase 5 cleanup. `DOC_LIFECYCLE.md` constitution locked (V1/V2 pointer headers + §0 scope + §2b runtime-coupled paths + §2c sole-counts-source). 39 Cat-B root docs archived + 72 frozen-subdir files + 457 pre-Session-800 handoffs. DaVinci sunset. Reality-score retired.
- **Session 1142** — docs hygiene + `search_docs` PA tool (chunked /docs/ retrieval). 852 active docs embedded + 19,305 chunks in `.rag/corpus.jsonl`. Plan B (this session) extends that pipeline with the originating_session filter.
- **Sessions 1138-1141 arc** — Decision-13 paid-interest demand-gate, entity-token clusterer, judge-stats endpoint, Chris ratification of Jessica's 22 decisions, action-card pre-generation vertical slice, pgvector blocker closed.
- **Earlier:** see `docs/handoffs/CURRENT.md` for latest two-handoff pointer.
