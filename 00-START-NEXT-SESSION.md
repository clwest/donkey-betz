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
- `python manage.py backfill_doc_provenance --add-frontmatter --paths-include docs/handoffs/ --limit 75 --with-confidence --with-note "auto-added by backfill_doc_provenance"` — **P3.5 track COMPLETE (Session 1156 ran round 9 final pass; survey now reports `skipped_no_fm=0`). 783 not-HIGH handoffs remain untagged but need different treatment.**
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145+1146+1147+1148+1149+1150+1151+1152+1153+1154+1155+1156+1157 ran 100% subject-tagged. Keep the streak.

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

## SESSION 1157 CLOSED — celery-beat-schedule footgun closed (BYPASS MODE) (2026-05-25)

**1 PR merged + this handoff.** Full handoff: [`docs/handoffs/SESSION_1157_CELERY_BEAT_SCHEDULE_CLEANUP.md`](docs/handoffs/SESSION_1157_CELERY_BEAT_SCHEDULE_CLEANUP.md).

| PR | What |
|----|------|
| **#2243** | celery-beat-schedule option A — refactored `add_critical_celery_tasks` to materialize from `core/celery.py:app.conf.beat_schedule` (canonical); removed 100-entry `CRITICAL_TASKS` dict that contradicted minimal-mode + risked re-enabling conserve-mode-disabled tasks |

Plus this Session 1157 handoff PR.

**Underlying footgun: closed.** Smoke-test on main: 77/77 entries translate, 0 DB churn, idempotent.

**Context-kit CONFLICT signal: still flagged.** Its detector heuristic spans ~36 files (broader than the add_critical_celery_tasks ↔ core/celery.py pair). The architectural fix is in; clearing the signal needs detector tuning OR a targeted 36-file token-pattern sweep — queued for Session 1158.

### Previous closed work still relevant for context

- **Session 1156** — P3.5 TRACK COMPLETE. Pool exhausted at `skipped_no_fm=0`. 646 handoffs auto-backfilled across 9 rounds + 49 pre-existing = 695 total HIGH-tagged.
- **Sessions 1149-1155** — P3.5 rounds 3-8 + the Session 1149 cleanup merge wave + SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes.

### Previous merge waves (still relevant context)

| PR | Theme | Session |
|----|-------|---------|
| #2227, #2226, #2228 | Session 1149 cleanup wave (verifier + §3 rewrite + handoff) | 1149 → merged 1150 |
| #2229 | P3.5 round 3 | 1150 |
| #2230 | Session 1150 handoff | 1150 |

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

### 2. `celery-beat-schedule` CONFLICT — code-level fix done, detector signal pending

**Session 1157 (PR #2243):** Underlying code-vs-code contradiction CLOSED. `add_critical_celery_tasks.py` no longer carries its own `CRITICAL_TASKS` schedule; it now materializes from `core/celery.py:app.conf.beat_schedule` (canonical per option A).

**Context-kit CONFLICT signal still flags** because its detector heuristic is keyword/path-based across ~36 files (other sync commands, services, views, migrations, tests, docs). Session 1158 charter: investigate the detector source to find the specific tokens triggering "ownership claim," then either propose an upstream tuning OR apply a targeted 36-file phrasing sweep.

---

## SESSION 1158 — CURRENT ENTRY POINT (NEW CHARTER: corpus-narrative program)

### Why the charter changed

Chris's framing at end of Session 1157:

> *"I still want to finish going through all of the /docs/. Right now they are just a bunch of text from the last few years of building. But what we need it to do is read in a way anyone can understand it if they don't have access to the UI. So things like what sessions added what Agents and what was the reason behind adding it, what was the outcome of us adding it? Those are the things I am trying to get out of the /docs/."*

This shifts the work from **navigation infrastructure** (P3.5 frontmatter tagging, drift baselines, INDEX freshness — all done) to the **actual value of the corpus**: turning 2615 session-handoff fragments into a readable chronicle of *what was built, why, and what came of it.* This is `UDB_TRANSLATION_LAYER.md` applied to the historical corpus instead of current-state surfaces.

This is a **multi-session program**, not a single charter.

### FIRST THING this session

**Ping Rigby with the corpus-narrative vision and ask for her scoping proposal.** She needs to design:

1. **Slicing unit** — chronological (session-by-session story arcs) vs thematic (per-subsystem: "the story of the agent system", "the story of the spider network") vs per-component ("how the Personal Assistant evolved")?
2. **Template per narrative** — Chris's phrasing already suggests one: *added what* + *why we added it* + *what came of it.* Plus probably "what's still working" vs "what's been deprecated/superseded."
3. **Audience** — "anyone who can't access the UI" maps closer to *future-Claude / future-hire / future-Chris* than to *external Suite consumer* in the existing translation layer's persona blocks. Voice matters.
4. **Validation cadence** — Chris reads 1-2 sample narratives, signs off on template + voice, then we batch. He should not have to read all 2615 docs to trust the output — but he should read enough of the *first few* to trust the template before scaling.

Briefing message to Rigby was sent at Session 1157 close (timestamp 2026-05-25) so she's already pre-thinking this when fresh session opens. Pick up from her response.

### Then, after Rigby's design lands

1. **Chris picks the slice he wants to see first** — one agent's story? One subsystem's? One session arc?
2. **Produce a single sample narrative** to that template.
3. **Chris reads + reacts.** Iterate template if needed.
4. **Batch through remaining slices** at the cadence Rigby specs (probably 1 per session, like the P3.5 rhythm — but tuned to narrative-writing pace, not mechanical-backfill pace).

### Don't lose these — deferred but still real (NOT abandoned)

The Session 1158 charter previously slotted these as top priority. They're now deferred behind the corpus-narrative program. **They are not abandoned** — just re-ordered.

**Deferred top-priority** (next available slot after corpus-narrative is operational):

1. **`celery-beat-schedule` CONFLICT — second-half cleanup (detector signal clear).** Session 1157 closed the underlying code-level footgun (PR #2243); the context-kit CONFLICT signal still flags because the detector heuristic spans ~36 files. Two paths:
   - **(preferred)** Detector tuning — read-only investigation of context-kit's `celery-beat-schedule` detector source. Find tokens triggering "exclusive ownership claim." If it's a simple keyword regex, propose an upstream fix distinguishing "incidental mention" from "ownership claim."
   - **(fallback)** Targeted 36-file token-pattern phrasing sweep with consistent canonical-source language.

2. **Pre-existing 3-row PeriodicTask drift.** 80 DB rows vs 77 entries in `core/celery.py:app.conf.beat_schedule`. Folds naturally into the CONFLICT-detector work above.

### Other carryovers (unchanged from Session 1157 close)

**If Actions is BACK** (and after corpus-narrative work is operational):
- Topic-doc body-count sweep (the explicit-scope one)
- Infra track: exists_on_disk flag, beat-schedule regens, build_learning_bridge_audit generator fix, Redis pooling sweep

**Continued bypass mode (small offline-CI-safe items):**
- Older `docs/topics/` sweep (recon-first) — 7 Feb-March docs deferred from Session 1147 #2221
- Cosmetic `load_all_agents_advisors.py 149→139` fix
- `docs/reports/` + `docs/patents/` recon

**Chris-call-only carryovers (still parked):**
1. Decision Command backend cleanup
2. DaVinci route removal
3. Mission refresh PR #2190

**Not-HIGH handoffs (783 remaining untagged):** The P3.5 backfill only handled HIGH-provenance handoffs. The 783 not-HIGH ones need different treatment — manual hand-authored frontmatter or alternative provenance heuristics. Note: the **corpus-narrative program may naturally surface frontmatter for these** as a side effect of reading + synthesizing them. Re-evaluate this track after the narrative program has run for a few sessions.

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

- **Session 1157** — celery-beat-schedule cleanup option A. 1 PR merged (bypass mode) + handoff. Underlying code-level footgun closed; context-kit signal pending broader follow-up.
- **Session 1156** — P3.5 round 9 (FINAL) + P3.5 track CLOSE. 1 PR merged (bypass mode) + handoff. Pool exhausted; 646 backfilled across 9 rounds.
- **Session 1155** — P3.5 round 8. 1 PR merged (bypass mode) + handoff.
- **Session 1154** — P3.5 round 7. 1 PR merged (bypass mode) + handoff.
- **Session 1153** — P3.5 round 6. 1 PR merged (bypass mode) + handoff.
- **Session 1152** — P3.5 round 5. 1 PR merged (bypass mode) + handoff.
- **Session 1151** — P3.5 round 4. 1 PR merged (bypass mode) + handoff.
- **Session 1150** — Session 1149 merge wave + P3.5 round 3. 4 PRs merged (bypass mode).
- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes. 3 PRs (held on billing in 1149; merged in 1150).
- **Session 1148** — P3.5 round 2 + SYSTEM_OWNER drift label. 3 PRs (all merged).
- **Session 1147** — P3.5 round 1 (50 handoffs + filename override upstream) + apps light-touch + topics pragmatic sweep. 3 PRs.
- **Session 1146** — Root-level audits sweep. DOC-AUTOGEN finding flipped plan; regen + Runtime Evidence canon section. 3 PRs.
- **Session 1145** — Architecture sweep + Provenance Plan B. `_provenance.json` + `search_docs` originating_session filter. 3 PRs.
- **Session 1144** — `/docs/` cleanup wave. 10 PRs.
- **Earlier:** see `docs/handoffs/CURRENT.md`.
