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
- `python manage.py backfill_doc_provenance --add-frontmatter --paths-include docs/handoffs/ --limit 75 --with-confidence --with-note "auto-added by backfill_doc_provenance"` — **P3.5 round 3 invocation (Session 1150's sole charter; 446 more handoffs eligible after Session 1148's round 2)**.
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145+1146+1147+1148+1149 ran 100% subject-tagged. Keep the streak.

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

## SESSION 1149 CLOSED — 2 PRs PENDING MERGE ON CI BILLING BLOCKER (2026-05-25)

**2 PRs open + this handoff PR. Merges blocked by GitHub Actions billing.** Full handoff: [`docs/handoffs/SESSION_1149_SYSTEM_OWNER_SECTION_3_AND_DRIFT_FIXES.md`](docs/handoffs/SESSION_1149_SYSTEM_OWNER_SECTION_3_AND_DRIFT_FIXES.md).

### 🚨 BLOCKER: GitHub Actions billing

Both Session 1149 PRs fail CI with:

> *"The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings."*

Affected workflows: **Repo Guardrails** + **Direct LLM SDK usage check**. GitGuardian (different vendor) passes. Session 1148 PRs (~12 hrs prior) all passed those same workflows. **This is a new billing failure, not a code issue.**

**Chris must resolve before any PR merges this session.** Repo Settings → Billing & plans → update payment method or raise spending cap. Then re-run failed workflows (`gh run rerun <id>` or GH UI) and merge in order below.

Per Rigby's explicit call (Session 1149 close): **do NOT admin-merge bypassing failed guardrails.**

### Session 1149 PRs (pending merge)

| PR | Branch | Files | What |
|----|--------|-------|------|
| **#2226** | `docs/session-1149-system-owner-section-3-rewrite` | 2 (+165/-82) | SYSTEM_OWNER.md §3 fully rewritten with current ops paths (HTTP/Django-shell/`autopilot_tool`) + INDEX regen. Closes Session 1148 follow-up #8. |
| **#2227** | `docs/session-1149-verify-doc-claims-drift-fixes` | 2 (+21/-13) | Re-pegged 3 drifted verifier baselines: persona_agent_count 148→155, total 231→238, mgmt_cmds 174→182 (+BACKEND_INVENTORY body update). drift now=0. Closes Session 1148 follow-up #3 (the registered-claim portion). |

Plus this handoff PR.

Rigby's recommended merge order (after billing fix): **#2227 → #2226 → handoff PR**.

---

## SESSION 1150 — CURRENT ENTRY POINT

### FIRST THING this session

**Verify GH Actions billing is fixed.** Run:
```bash
gh pr checks 2226 2227
```
If still showing the "payments have failed / spending limit" annotation, Chris must resolve in Repo Settings → Billing & plans before any other work. Once green, merge Session 1149 PRs in Rigby's recommended order (#2227 → #2226 → handoff).

### SOLE CHARTER (Rigby's spec)

**P3.5 round 3.** One bounded mechanical PR. Same invocation as round 2 — no scope creep:

```bash
python manage.py backfill_doc_provenance \
    --add-frontmatter \
    --paths-include docs/handoffs/ \
    --limit 75 \
    --with-confidence \
    --with-note "auto-added by backfill_doc_provenance"
```

**Survey expectation** (post-Session 1148 round 2): ~446 handoffs add-eligible (down from 521 before round 2's 75). Pick 75 most-recent. Bundle `docs/INDEX.md` + `docs/_provenance.json` regen per Rigby's Session 1148 tweak.

**Why sole charter:** Sessions 1148 and 1149 both ran 2-PR "quick wins" mode. Session 1150 needs the next mechanical batch reviewed in the right mental mode — not bundled with other meaningful PRs.

### Carryovers queued for Session 1151+

**Docs-cleanup track:**
- **(2) Older `docs/topics/` sweep** (recon-first) — 7 Feb-March docs deferred from Session 1147 #2221.
- **(3 NEW) Topic-doc body-count sweep** — what Session 1149 #2227 *didn't* do. Explicit scope when activated: "no hardcoded platform counts remain in `docs/topics/*` except definitional constants; everything else links to PLATFORM_INVENTORY / inventory generator outputs."
- **(4) `docs/reports/` + `docs/patents/` recon** — large piles, recon-first.

**Infra track:**
- **(5) `exists_on_disk: false` flag** (carried since Session 1145) — 326 dead paths in `_provenance.json`. Schema bump v1→v2.
- **(6) Beat-schedule the regens** (carried since Session 1145) — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
- **(7) Fix `build_learning_bridge_audit.py` generator** (carried since Session 1146) — falsely flags "ABC unused".
- **(8) Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

**New from Session 1149:**
- **(9 NEW) Cosmetic cleanup of `load_all_agents_advisors.py`** — fix the misleading "149 Specialized Agents" docstring + `self.stdout.write` (actual `agents_data` has 139 tuples). Trivial; bundle into the next docs session that touches that file.

### Chris-call-only carryovers (still parked)

1. **Decision Command backend cleanup** — 5 Python files (regressed feature).
2. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
3. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons (Sessions 1145–1149)

- **Recon before sweep.** Five back-to-back sessions where mid-recon findings flipped the PR plan. (Session 1149: "topic-doc body counts" framing masked 3 unrelated registered-claim drifts.)
- **Filename overrides for canonical names** (Session 1147 PR #2219) — `SESSION_NNNN_*.md` is unambiguous.
- **`session: NNNN` → `originating_session: NNNN`** is the standard.
- **`build_*_audit` generators can lag reality.** Fix the generator, not the output.
- **Quick-wins-only is valid mode** when review fatigue is real.
- **NEW (1149):** "Counts-hygiene" framing in start-here docs is ambiguous — always disambiguate registered-claim drift vs body-level hardcoded counts. Different PRs.
- **NEW (1149):** Stale log/docstring text inside command files can mislead future baselines (148→139→155 reconciliation). When registering `verify_doc_claims` baselines against commands, anchor to `len(data_structure)`, not to comments/logs.
- **NEW (1149):** GH Actions billing failures are Chris-only blockers. Don't admin-merge-bypass; surface to user; headline in handoff.

---

## RECENT SESSION ARCS

- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes. 2 PRs (+ handoff), pending merge on GH Actions billing.
- **Session 1148** — P3.5 round 2 + SYSTEM_OWNER drift label. 3 PRs (all merged).
- **Session 1147** — P3.5 round 1 (50 handoffs + filename override upstream) + apps light-touch + topics pragmatic sweep. 3 PRs.
- **Session 1146** — Root-level audits sweep. DOC-AUTOGEN finding flipped plan; regen + Runtime Evidence canon section. 3 PRs.
- **Session 1145** — Architecture sweep + Provenance Plan B. `_provenance.json` + `search_docs` originating_session filter. 3 PRs.
- **Session 1144** — `/docs/` cleanup wave. 10 PRs.
- **Earlier:** see `docs/handoffs/CURRENT.md`.
