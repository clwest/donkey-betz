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
- `python manage.py backfill_doc_provenance --add-frontmatter --paths-include docs/handoffs/ --limit 75 --with-confidence --with-note "auto-added by backfill_doc_provenance"` — **P3.5 round 4 invocation (Session 1151's sole charter; 446 more handoffs eligible after Session 1150's round 3)**.
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145+1146+1147+1148+1149+1150 ran 100% subject-tagged. Keep the streak.

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

## SESSION 1150 CLOSED — 4 PRs MERGED (BYPASS MODE) (2026-05-25)

**Session 1149's 3 PRs + Session 1150's P3.5 r3 all merged with bypass for GH Actions billing + pre-existing CONFLICT.** Full handoff: [`docs/handoffs/SESSION_1150_P35_ROUND3_AND_SESSION_1149_MERGE_WAVE.md`](docs/handoffs/SESSION_1150_P35_ROUND3_AND_SESSION_1149_MERGE_WAVE.md).

| PR | What |
|----|------|
| **#2227** | verify_doc_claims baselines re-pegged (drift now=0) |
| **#2226** | SYSTEM_OWNER.md §3 rewritten with current ops paths + INDEX regen |
| **#2228** | Session 1149 handoff |
| **#2229** | P3.5 round 3 — 75 handoffs FM-backfilled (SESSION_890 → SESSION_806) |

Plus this Session 1150 handoff PR.

Post-r3 state: `_provenance.json` 2058 docs (HIGH=1275 / MEDIUM=294 / UNKNOWN=489); `INDEX.md` 2609 docs / 681,664 lines. 446 handoffs still eligible for future rounds.

---

## 🚨 ACTIVE ISSUES carrying into Session 1151

### 1. GitHub Actions billing — still down

Same annotation: *"The job was not started because recent account payments have failed or your spending limit needs to be increased."* Multi-day outage until Chris funds account.

**Self-merge protocol during outage** (Sessions 1149 + 1150 pattern):

For every PR, run local mirrors before push:
```bash
.venv/bin/python scripts/verify_repo_guardrails.py --inventory-advisory
.venv/bin/python tools/check_direct_llm_calls.py --root . --whitelist .ci/llm_whitelist.txt --warn-only
```

Self-merge with bypass requires:
1. Both local mirrors run.
2. Only failure is the pre-existing `celery-beat-schedule` CONFLICT (item 2 below).
3. Merge commit body documents the bypass with both `billing outage` and `pre-existing CONFLICT` named.
4. PR scope is documentation or low-risk verifier baselines (no production code changes).

Higher-risk code PRs: hold the merge; stack the PR until billing fixes.

### 2. Pre-existing `celery-beat-schedule` CONFLICT

Context-kit finding ID `celery-beat-schedule`, status `CONFLICT`, title "Celery beat schedule ownership." Docs claim exclusive ownership across `CLAUDE.md`, `00-START-NEXT-SESSION.md`, `core/celery.py`, `core/management/commands/add_critical_celery_tasks.py`, etc.

**Not introduced by any Session 1145-1150 PR.** Recommendation: describe the split ownership model accurately or update the exclusive-ownership claim.

**Cleanup queued as:** Future session, needs Chris's input on the ownership model.

---

## SESSION 1151 — CURRENT ENTRY POINT

### FIRST THING this session

**Check whether GH Actions billing is fixed.** Run:
```bash
gh pr checks <latest-pr-num>
```
If still showing the "payments have failed / spending limit" annotation, continue in bypass mode (see protocol above). If fixed, run `gh run rerun <id>` on the next PR's failed runs and resume normal mode.

### SOLE CHARTER (Rigby's spec — same as Session 1150 pattern)

**P3.5 round 4.** One bounded mechanical PR. Same invocation as round 3:

```bash
python manage.py backfill_doc_provenance \
    --add-frontmatter \
    --paths-include docs/handoffs/ \
    --limit 75 \
    --with-confidence \
    --with-note "auto-added by backfill_doc_provenance"
```

**Expected range:** ~`SESSION_805` → `SESSION_731` (next 75 most-recent below SESSION_806). **Survey expectation:** 446 add-eligible → pick 75 most-recent → 371 remaining after round 4.

Bundle `docs/INDEX.md` + `docs/_provenance.json` regen in the same PR. Run local CI mirrors before push.

**Why sole charter (continued from Session 1150):** One mechanical batch per session, audit trail per merge, explicit bypass documentation. Don't chain round 4 with anything else — keep the discipline that's kept the bypass-mode safe across 4 merges so far.

### Carryovers queued (unchanged from Session 1150 close)

**Docs-cleanup track (avoid during offline-CI window):**
- **(2) Older `docs/topics/` sweep** (recon-first) — 7 Feb-March docs deferred from Session 1147 #2221.
- **(3) Topic-doc body-count sweep** — explicit scope when activated: "no hardcoded platform counts remain in `docs/topics/*` except definitional constants; everything else links to PLATFORM_INVENTORY / inventory generator outputs."
- **(4) `docs/reports/` + `docs/patents/` recon** — large piles, recon-first.
- **(9) Cosmetic cleanup of `load_all_agents_advisors.py`** — fix "149 Specialized Agents" → "139". Trivial; bundle into next docs session that touches that file.

**Infra track (avoid during offline-CI window):**
- **(5) `exists_on_disk: false` flag** (since Session 1145) — 326 dead paths in `_provenance.json`. Schema bump v1→v2.
- **(6) Beat-schedule the regens** (since Session 1145) — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
- **(7) Fix `build_learning_bridge_audit.py` generator** (since Session 1146) — falsely flags "ABC unused".
- **(8) Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

**Queued for when GH Actions returns:**
- **`celery-beat-schedule` CONFLICT cleanup** — needs Chris input on ownership model.
- All deferred items above shift back into eligibility.

### Chris-call-only carryovers (still parked)

1. **Decision Command backend cleanup** — 5 Python files (regressed feature).
2. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
3. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons (Sessions 1145–1150)

- **Recon before sweep.** Six back-to-back sessions where mid-recon findings flipped the PR plan.
- **Filename overrides for canonical names** (Session 1147 PR #2219) — `SESSION_NNNN_*.md` is unambiguous.
- **`session: NNNN` → `originating_session: NNNN`** is the standard.
- **`build_*_audit` generators can lag reality.** Fix the generator, not the output.
- **Quick-wins-only is valid mode** when review fatigue is real.
- **(1149)** "Counts-hygiene" framing in start-here docs is ambiguous — disambiguate registered-claim drift vs body-level hardcoded counts.
- **(1149)** Stale log/docstring text inside command files can mislead future baselines (148→139→155 reconciliation). Anchor `verify_doc_claims` baselines to `len(data_structure)`, not comments/logs.
- **(1149)** GH Actions billing failures are Chris-only blockers initially — surface in handoff, then resolve approach with Chris explicitly.
- **NEW (1150)**: Bypass-merging during a CI outage is workable IF disciplined. Local mirrors + per-merge bypass documentation + Rigby gate-checking the rules makes self-merge safe enough during a multi-day outage window.
- **NEW (1150)**: "One mechanical batch then stop" applies even when batches are easy. Round 3 was frictionless; round 4 would have been just as cheap. But Rigby's call to stop after each round specifically preserves audit-trail crispness during offline-CI mode. Easy ≠ safe to chain.

---

## RECENT SESSION ARCS

- **Session 1150** — Session 1149 merge wave + P3.5 round 3. 4 PRs merged (bypass mode).
- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes. 3 PRs (held on billing in 1149; merged in 1150).
- **Session 1148** — P3.5 round 2 + SYSTEM_OWNER drift label. 3 PRs (all merged).
- **Session 1147** — P3.5 round 1 (50 handoffs + filename override upstream) + apps light-touch + topics pragmatic sweep. 3 PRs.
- **Session 1146** — Root-level audits sweep. DOC-AUTOGEN finding flipped plan; regen + Runtime Evidence canon section. 3 PRs.
- **Session 1145** — Architecture sweep + Provenance Plan B. `_provenance.json` + `search_docs` originating_session filter. 3 PRs.
- **Session 1144** — `/docs/` cleanup wave. 10 PRs.
- **Earlier:** see `docs/handoffs/CURRENT.md`.
