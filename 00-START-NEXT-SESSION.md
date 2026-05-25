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
4. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
5. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
6. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
7. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
8. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
9. **`docs/specs/`** — engineering specs (Atlas-anchored).
10. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence, not competing narrative counts. Regenerate with `build_*_audit` mgmt commands.
11. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`** (both upstream).
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N` — clusters docs+code by session of origin (PR #2205).
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json` (per-doc origin index; consumed by `search_docs(originating_session=N)` per PR #2213, w/ handoff filename override per PR #2219).
- `python manage.py backfill_doc_provenance --add-frontmatter --paths-include docs/handoffs/,docs/specs/,docs/canon/ --limit 50 --with-confidence --with-note "auto-added by backfill_doc_provenance"` — P3.5 backfill (548 more handoffs eligible as of Session 1147 close).
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145+1146+1147 ran 100% subject-tagged. Keep the streak.

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
- **search_docs originating_session filter cache:** `_load_provenance_docs()` is `lru_cache(1)` per process. After `build_docs_provenance` regen, restart workers for cached value to refresh.

---

## SESSION 1147 CLOSED CLEAN (2026-05-25, late afternoon — 3rd back-to-back today)

**3 PRs open in review queue.** Full handoff: [`docs/handoffs/SESSION_1147_P35_BACKFILL_PLUS_APPS_AND_TOPICS_SWEEPS.md`](docs/handoffs/SESSION_1147_P35_BACKFILL_PLUS_APPS_AND_TOPICS_SWEEPS.md).

| PR | Branch | Files | What |
|----|--------|-------|------|
| **#2219** | `docs/session-1147-provenance-backfill-p35` | 53 (+1416/-747) | P3.5 frontmatter backfill (50 handoffs) + filename override upstream in build_docs_provenance |
| **#2220** | `docs/session-1147-apps-frontmatter-align` | 9 (+10/-10) | docs/apps/ light touch — session → originating_session + park colorado |
| **#2221** | `docs/session-1147-topics-pragmatic-banner-sweep` | 5 (+35/-4) | docs/topics/ V1 banners on 5 high-traffic files + README current-truth paragraph |

Plus this handoff PR.

Rigby's recommended merge order: **#2219 → #2221 → #2220** (provenance infra > topics-doc clarity > apps frontmatter polish; no hard constraints; all independent).

Index counts post-P3.5: 2055 docs / HIGH=1274 / MEDIUM=292 / UNKNOWN=489 (223 entries via filename override).

---

## SESSION 1148 — CURRENT ENTRY POINT

### FIRST THING this session

Decide what to merge from the Session 1147 PR queue. Rigby's recommended order is `#2219 → #2221 → #2220`. If anything needs revisions before merge, surface it now before starting new work.

### Top priority — Continue docs cleanup (9 follow-ups queued)

(All independent; all Rigby-approved or naturally next.)

1. **P3.5 round 2** — 548 more handoffs eligible (cap 50/PR per Rigby). Re-run `backfill_doc_provenance --add-frontmatter --paths-include docs/handoffs/,docs/specs/,docs/canon/ --limit 50 --with-confidence --with-note "auto-added by backfill_doc_provenance"`. After PR #2219 merges first.
2. **Older `docs/topics/` sweep** — recon-first pass on 7 Feb-March docs deferred from #2221: `body-systems`, `collaboration-protocol`, `local-askdocs`, `spider-network`, `stock-intelligence`, `tool-consolidation`, `video-upload`. Apply V1/V2 rubric.
3. **Counts-hygiene on the 7 already-bannered topic docs** — `agent-system.md` has 8 hardcoded count hits, `personal-assistant.md` has 4, `infrastructure.md` + `active-module-ownership-map.md` have 2 each. Replace with PLATFORM_INVENTORY pointers per §2c.
4. **`exists_on_disk: false` flag** (carried since Session 1145) — for 326 dead paths in `_provenance.json`. Schema bump v1→v2.
5. **Beat-schedule the regens** (carried since Session 1145) — weekly Celery beat task for `_provenance.json` + the 8 `build_*_audit` commands. No LLM/DB. Could share infra.
6. **Fix `build_learning_bridge_audit.py` generator** (carried since Session 1146) — falsely flags "ABC unused" even though Session 1115 closed it. Fix AST parser, not output markdown.
7. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory treatment from PR #2201.
8. **`docs/governance/SYSTEM_OWNER.md` staleness check** — passes §2c already; mtime overdue for review.
9. **`docs/reports/` + `docs/patents/` recon** — large piles, recon-first.

### Suggested order if Chris keeps the "docs cleanup" framing

A → 1 (P3.5 r2, mechanical) → 2 (older topics, scoped) → 3 (counts on bannered topics) → 8 (governance check, small) → 9 (recon-first on reports/patents)
B → infra-bias variant: 4 (exists_on_disk) + 6 (generator bug) + 5 (beat schedule) — group as one infra-fix PR

### Chris-call-only carryovers (still parked)

1. **Decision Command backend cleanup** — 5 Python files (regressed feature).
2. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
3. **Mission refresh PR #2190** — preserved branch.

### Session 1145/1146/1147 lessons to apply

- **Recon before sweep.** Three back-to-back sessions where mid-recon findings flipped the PR plan (DOC-AUTOGEN markers in 1146, well-curated apps frontmatter in 1147, pragmatic 5-of-12 topics scope in 1147).
- **Filename overrides for canonical names.** `SESSION_NNNN_*.md` is unambiguous; trust it over git's first-commit attribution. Saved as feedback memory.
- **`session: NNNN` → `originating_session: NNNN`** is the standard now (Session 1145+1147). Old `session:` works but prefer `originating_session:` for new frontmatter.
- **`build_*_audit` generators can lag reality** (LEARNING_BRIDGE still flags closed Session-1115 finding). Don't fix output; fix the generator.

---

## RECENT SESSION ARCS (read for context if cold-starting)

- **Session 1146** — Root-level audits sweep. Recon caught 8 audit docs are DOC-AUTOGEN; 3 PRs (Atlas+CS canonical refresh, regen DOC-AUTOGENs + Runtime Evidence canon, AUDIT_FINDINGS V1-living + Char OS V2-parked).
- **Session 1145** — Architecture sweep (2 PRs) + Provenance Plan B (1 PR). `_provenance.json` + `search_docs` originating_session filter + 6/6 unit tests + 2-doc backfill.
- **Session 1144** — `/docs/` cleanup wave (10 PRs): CONN_MAX_AGE=60 socket-leak fix, §0 scope boundary, CLAUDE+CAPABILITIES reframe, 17-doc banner sweep, `session_provenance` Plan A scaffolding, canon rebase (≤10 docs), spec status cleanup, historical plan labeling.
- **Session 1143** — Deep `/docs/` audit + Phase 5 cleanup. `DOC_LIFECYCLE.md` constitution locked.
- **Earlier:** see `docs/handoffs/CURRENT.md` for latest two-handoff pointer.
