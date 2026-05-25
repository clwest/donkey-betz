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

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`).
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts).
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
5. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
6. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
7. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
8. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
9. **`docs/specs/`** — engineering specs.
10. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence. Regenerate with `build_*_audit` mgmt commands.
11. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`**.
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N` — per-session cluster (PR #2205).
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json` (per-doc index w/ handoff filename override per PR #2219).
- `python manage.py backfill_doc_provenance --add-frontmatter --paths-include docs/handoffs/ --limit 75 --with-confidence --with-note "auto-added by backfill_doc_provenance"` — P3.5 round 3 invocation (521 more handoffs eligible as of Session 1148 close).
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145+1146+1147+1148 ran 100% subject-tagged. Keep the streak.

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- **PA tool registration needs BOTH daphne AND celery restart.** `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **search_docs originating_session filter cache:** `lru_cache(1)` per process. After `build_docs_provenance` regen, restart workers.

---

## SESSION 1148 CLOSED CLEAN (2026-05-25, evening — 4th back-to-back today)

**2 PRs open in review queue.** Full handoff: [`docs/handoffs/SESSION_1148_P35_ROUND2_AND_SYSTEM_OWNER_DRIFT_LABEL.md`](docs/handoffs/SESSION_1148_P35_ROUND2_AND_SYSTEM_OWNER_DRIFT_LABEL.md).

| PR | Branch | Files | What |
|----|--------|-------|------|
| **#2223** | `docs/session-1148-p35-round2` | 76 (+903/-216) | P3.5 round 2 — 75 handoffs FM-tagged (range SESSION_1146 → SESSION_891), cap 75 raised from round 1's 50, scope narrowed to handoffs-only |
| **#2224** | `docs/session-1148-system-owner-drift-label` | 1 (+7/-2) | SYSTEM_OWNER.md V1 banner refresh + flag for stale §3 emergency commands (skin_lock/quarantine_agent/list_quarantined don't exist) |

Plus this handoff PR.

Rigby's recommended merge order: **#2223 → #2224**.

Index post-P3.5 r2: 2056 docs / HIGH=1273 / MEDIUM=294 / UNKNOWN=489.

---

## SESSION 1149 — CURRENT ENTRY POINT

### FIRST THING this session

Decide what to merge from the Session 1148 PR queue. Rigby's recommended order is `#2223 → #2224`. If anything needs revisions before merge, surface it now before starting new work.

### 9 follow-ups queued (8 from Session 1147 carryover + 1 NEW from #2224)

**Docs-cleanup track (6):**
1. **P3.5 round 3** — 521 more handoffs eligible. Same invocation as round 2.
2. **Older `docs/topics/` sweep** (recon-first) — 7 Feb-March docs deferred from Session 1147 #2221.
3. **Counts-hygiene on the 7 already-bannered topic docs** — agent-system 8 hits, personal-assistant 4, etc.
8. **Rewrite SYSTEM_OWNER.md §3 emergency procedures** (NEW from #2224) — with current operational paths (Rigby tool invocations + Django shell snippets for SKIN lock / agent quarantine).
9. **`docs/reports/` + `docs/patents/` recon** — large piles, recon-first.

**Infra track (4):**
4. **`exists_on_disk: false` flag** (carried since Session 1145) — 326 dead paths in `_provenance.json`. Schema bump v1→v2.
5. **Beat-schedule the regens** (carried since Session 1145) — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
6. **Fix `build_learning_bridge_audit.py` generator** (carried since Session 1146) — falsely flags "ABC unused".
7. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

### Chris-call-only carryovers (still parked)

1. **Decision Command backend cleanup** — 5 Python files (regressed feature).
2. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
3. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons to apply (Sessions 1145–1148)

- **Recon before sweep.** Four back-to-back sessions where mid-recon findings flipped the PR plan.
- **Filename overrides for canonical names** (Session 1147 PR #2219) — `SESSION_NNNN_*.md` is unambiguous; trust it over git's first-commit attribution.
- **`session: NNNN` → `originating_session: NNNN`** is the standard convention.
- **`build_*_audit` generators can lag reality** (LEARNING_BRIDGE still flags closed Session-1115 finding). Don't fix output; fix the generator.
- **Quick-wins-only is a valid mode** (Session 1148) — when there's a lot of momentum but review fatigue is real, pick 2 small mechanical PRs.

---

## RECENT SESSION ARCS

- **Session 1147** — P3.5 round 1 (50 handoffs + filename override upstream) + apps light-touch + topics pragmatic sweep. 3 PRs.
- **Session 1146** — Root-level audits sweep. DOC-AUTOGEN finding flipped plan; regen + Runtime Evidence canon section. 3 PRs.
- **Session 1145** — Architecture sweep + Provenance Plan B. `_provenance.json` + `search_docs` originating_session filter. 3 PRs.
- **Session 1144** — `/docs/` cleanup wave. 10 PRs.
- **Earlier:** see `docs/handoffs/CURRENT.md`.
