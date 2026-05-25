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

Per Session 1144 PR #2208 (canon rebase) + Session 1146 PR #2216 (Runtime Evidence promotion):

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`). Regenerate with `python manage.py generate_platform_inventory`.
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts). Regenerate with `python manage.py build_docs_index`.
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution (V1/V2 pointer headers, §0 scope boundary, §2b runtime-coupled paths, §2c sole-counts-source rule, §3 root-stability).
5. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
6. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
7. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
8. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
9. **`docs/specs/`** — engineering specs (Atlas-anchored).
10. **NEW Session 1146 — Runtime Evidence (auto-generated):** the 8 `docs/*_AUDIT.md` files (`CELERY_AUDIT`, `BEAT_AUDIT`, `BODY_SYSTEM_AUDIT`, `CAPABILITY_AUDIT`, `LEARNING_BRIDGE_AUDIT`, `MANAGEMENT_COMMAND_AUDIT`, `DISCORD_AUDIT`, `ML_AUDIT`). DOC-AUTOGEN — per-subsystem runtime evidence, **not** competing narrative counts. Regenerate with `build_*_audit` mgmt commands. Per §2c: PLATFORM_INVENTORY is the sole narrative counts registry; these are backing artifacts. Do not hand-edit.
11. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`** (both upstream).
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N` — clusters docs+code by session of origin (PR #2205).
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json` (per-doc origin index; consumed by `search_docs(originating_session=N)` per PR #2213).
- **NEW Session 1146:** the 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN` somewhere. Preferred form:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

`session_provenance` flags `coverage_warning: true` when no subject-tagged commits exist for a session. Sessions 1145+1146 ran 100% subject-tagged; keep the streak.

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
- **Session 1145 P2 cache note:** `search_docs` originating_session filter caches `_provenance.json` per process (`lru_cache(1)`). After `build_docs_provenance` regen, restart workers for cached value to refresh.

---

## SESSION 1146 CLOSED CLEAN (2026-05-25, afternoon)

**3 PRs open in review queue.** Full handoff: [`docs/handoffs/SESSION_1146_ROOT_AUDITS_SWEEP.md`](docs/handoffs/SESSION_1146_ROOT_AUDITS_SWEEP.md).

| PR | Branch | Files | What |
|----|--------|-------|------|
| **#2215** | `docs/session-1146-canon-refresh` | 2 (+12/-0) | Atlas + COST_SURVIVAL_AUDIT canonical refresh-in-place V1 banners |
| **#2216** | `docs/session-1146-autogen-audit-regen` | 5 (+513/-152) | Regen 4 DOC-AUTOGEN audits with real drift (CELERY 397→401, BEAT 42→77 + 7→0 broken refs, MANAGEMENT 167→182) + Runtime Evidence canon section per §2c |
| **#2217** | `docs/session-1146-handwritten-doc-banners` | 3 (+23/-0) | AUDIT_FINDINGS V1-living-runbook + MERGE_PROPOSAL_CHARACTER_OS{,_NATIVE} V2-parked-backlog |

Plus the handoff PR for this file + the handoff doc + CURRENT.md pointer shift.

Rigby's recommended merge order: **#2216 → #2215 → #2217** (no hard constraints; all independent).

Canon registry now: 6 entries (1 technical + 4 operational + 1 runtime-evidence + 0 creative). Still under ≤10 cap from #2208.

---

## SESSION 1147 — CURRENT ENTRY POINT

### FIRST THING this session

Decide what to merge from the Session 1146 PR queue. Rigby's recommended order is `#2216 → #2215 → #2217`. If anything needs revisions before merge, surface it now before starting new work.

### Top priority — Six independent follow-ups queued

(All Rigby-approved, all parallel-ok. Pick by impact/interest. None depend on each other.)

1. **P3.5 frontmatter backfill** (carried since Session 1145) — extend `backfill_doc_provenance` to add NEW frontmatter blocks (not just update existing) for HIGH-confidence docs in `docs/handoffs/**`, `docs/specs/**`, optionally `docs/canon/**`. Cap 50 files per PR. Minimal frontmatter: `originating_session`, `provenance_confidence`, optional `provenance_note: "auto-added by backfill_doc_provenance"`. No content edits beyond block insertion. Survey result from Session 1145: 767 HIGH-confidence narrative docs would benefit.

2. **`exists_on_disk: false` flag for dead paths** (carried since Session 1145) — 326 entries in `docs/_provenance.json` point at files git history records but no longer exist on disk. Mark explicitly (don't delete — preserves history); exclude from default consumers unless requested. Schema bump from v1 to v2; update `build_docs_provenance` and the `search_docs` filter to honor.

3. **Beat-schedule the regens** (carried since Session 1145) — weekly Celery beat task to rebuild `_provenance.json` + run all 8 `build_*_audit` commands. No LLM, no DB writes, file-only, ~50s total. Log single-line summary per regen (totals, drift detected).

4. **Fix `build_learning_bridge_audit.py` generator** (NEW Session 1146 follow-up) — AST parser falsely flags `Abstract base LearningBridge is unused` even though Session 1115 closed it (all 9 bridges inherit from `LearningBridge` per `core/learning_bridges/base.py`). Fix the detection logic in the generator, not the output markdown.

5. **Redis pooling sweep** (top-level from earlier sessions) — ~40 inline `redis.Redis.from_url(...)` sites need factory treatment (mirror OpenAI/Anthropic factory pattern from Session 1144 PR #2201). Same TIME_WAIT-leak risk surface as Postgres was.

6. **`docs/apps/` sweep** — `rigby_standalone_BRIEF.md`, `colorado_family_law_concierge_FUTURE_CONCEPT.md`, signal-studio brief. Apply same approach as Session 1146 root sweep: recon first, then ping Rigby for scope, then ship.

### Remaining sweep targets (after the 6 above)

- `docs/governance/SYSTEM_OWNER.md` — passes §2c already; staleness check.
- `docs/missions/CURRENT_MISSION.md` — runtime-coupled (agents read it), stale; **parked per Chris's docs-only directive** but unparkable if Chris reopens GTM.
- `docs/reports/` — large pile of historical reports.
- `docs/patents/` — patent disclosures.
- `docs/topics/` — subsystem deep-dive docs (per-topic stats tables may drift; check vs PLATFORM_INVENTORY).

### Chris-call-only carryovers (still parked)

1. **Decision Command backend cleanup** — 5 Python files (regressed feature).
2. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
3. **Mission refresh PR #2190** — preserved branch.

### Session 1146 lessons to apply

- **Recon before sweep.** Initial recon assumed 13-14 hand-written audit docs; finding the DOC-AUTOGEN markers on 8 of them flipped the entire PR plan. Always grep for `DOC-AUTOGEN` before assuming hand-written content. Saved as feedback memory.
- **`build_*_audit` generator findings can lag reality.** `LEARNING_BRIDGE_AUDIT` flags "ABC unused" even though Session 1115 closed it. Don't fix output by editing — fix the generator.
- **Real drift is in code, not docs.** Regen captured 7→0 broken beat refs (Session 1115 fix), 397→401 tasks, 42→77 beat entries, 167→182 mgmt commands. The docs are downstream; the truth lives in the runtime.
- **Rigby's §2c constraint:** DOC-AUTOGEN runtime inventories ≠ narrative counts source. PLATFORM_INVENTORY remains sole counts registry; everything else (autogen audits + canon) points at it.

---

## RECENT SESSION ARCS (read for context if cold-starting)

- **Session 1145** — Architecture sweep (PRs #2211/#2212) + Provenance Plan B (PR #2213). 2052-doc `_provenance.json` + `search_docs` originating_session filter + 6/6 unit tests + 2-doc HIGH-confidence frontmatter backfill. Saved git-log-name-only feedback memory.
- **Session 1144** — `/docs/` cleanup wave (10 PRs): CONN_MAX_AGE=60 socket-leak fix, §0 scope boundary, CLAUDE+CAPABILITIES reframe, 17-doc banner sweep, `session_provenance` Plan A scaffolding, canon rebase (≤10 docs), spec status cleanup, historical plan labeling. Commit-message hygiene rule introduced.
- **Session 1143** — Deep `/docs/` audit + Phase 5 cleanup. `DOC_LIFECYCLE.md` constitution locked (V1/V2 pointer headers + §0 scope + §2b runtime-coupled paths + §2c sole-counts-source). 39 Cat-B root docs archived + 72 frozen-subdir files + 457 pre-Session-800 handoffs. DaVinci sunset. Reality-score retired.
- **Session 1142** — docs hygiene + `search_docs` PA tool (chunked /docs/ retrieval). 852 active docs embedded + 19,305 chunks in `.rag/corpus.jsonl`. Plan B in 1145 extended this with originating_session filter.
- **Earlier:** see `docs/handoffs/CURRENT.md` for latest two-handoff pointer.
