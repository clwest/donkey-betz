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

## READ THIS SECOND — PA "CONSUME-1-THEN-HANG" IS USUALLY DISK PRESSURE

NEW gotcha from Session 1158 captured to memory (`feedback_pa_hang_from_disk_pressure.md`). If the PA worker processes exactly one task and then goes silent, check `df -h /System/Volumes/Data` + `sysctl vm.swapusage` BEFORE deeper Celery debugging. Single-digit GiB free or swap < 2 GiB free → free disk first (Docker prune, simctl delete unavailable, npm cache clean, pip cache, browser caches). Don't restart Docker — `unified-postgres` lives there.

Session 1158 diagnosis: 99% disk + 91% swap → worker children silently exceeded `--max-memory-per-child=200 MB` cap. After freeing disk to 37 GiB, restart worked.

## SOURCE OF TRUTH

Per Session 1144 PR #2208 (canon rebase) + Session 1146 PR #2216 (Runtime Evidence promotion) + Session 1158 (narratives layer):

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`).
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts).
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/narratives/`** — 15 subsystem narratives (A–O) shipped Session 1158. Operator-handbook layer. Audience: future-Claude / future-hire / future-Chris who can't access UI. Cross-referenced; anchored to PLATFORM_INVENTORY for counts; uncertainty labelled Known/Inferred/Unknown.
5. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
6. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
7. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
8. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
9. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
10. **`docs/specs/`** — engineering specs.
11. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence. Regenerate with `build_*_audit` mgmt commands.
12. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`**.
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N` — per-session cluster (PR #2205).
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json`.
- `python manage.py backfill_doc_provenance --add-frontmatter --paths-include docs/handoffs/ --limit 75 --with-confidence --with-note "auto-added by backfill_doc_provenance"` — **P3.5 track COMPLETE (Session 1156 ran round 9 final pass).** Session 1158 added 5 more via narrative-citation pattern (PR #2252).
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145+1146+1147+1148+1149+1150+1151+1152+1153+1154+1155+1156+1157+1158 ran 100% subject-tagged. Keep the streak.

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

## SESSION 1158 CLOSED — corpus-narrative program (15 narratives + cleanup arc) (2026-05-25)

**8 PRs merged via bypass mode** + 1 new memory entry. Full handoff: [`docs/handoffs/SESSION_1158_CORPUS_NARRATIVE_PROGRAM.md`](docs/handoffs/SESSION_1158_CORPUS_NARRATIVE_PROGRAM.md).

| PR | Theme |
|----|------|
| **#2246** | Narrative A pilot — Agents, Autonomy & Governance (template-LOCKED v1 after Rigby PASS) |
| **#2247** | Narrative B — Content Pipeline |
| **#2248** | Narrative C — Signal Intelligence |
| **#2249** | Narrative D — Personal Assistant (Rigby) |
| **#2250** | Narrative slate completion — 11 narratives (E–O) in one PR |
| **#2251** | Topic-doc drift sweep — 7 docs corrected against runtime |
| **#2252** | Cited-handoff frontmatter — 5 handoffs got HIGH provenance with narrative-citation note |
| **#2253** | docs/reports/ + docs/patents/ recon (read-only; no action) |

**15 narratives now in `docs/narratives/`** (A–O). Template v1-LOCKED. Operator-handbook layer.

**1 new memory entry:** `feedback_pa_hang_from_disk_pressure.md` — PA "consume-1-then-hang" is usually disk + swap pressure, not Celery.

### Previous closed work still relevant for context

- **Session 1157** — celery-beat-schedule cleanup option A. Code-level footgun closed (PR #2243); context-kit CONFLICT signal still flags due to broader detector heuristic.
- **Session 1156** — P3.5 TRACK COMPLETE. Pool exhausted; 646 handoffs auto-backfilled across 9 rounds.

### Previous merge waves (still relevant context)

| PR | Theme | Session |
|----|-------|---------|
| #2243 | celery-beat-schedule option A | 1157 |
| #2244 | Session 1157 handoff | 1157 |
| #2245 | Session 1158 charter pivot to corpus-narrative | 1157 close |

---

## 🚨 ACTIVE ISSUES carrying into Session 1159

### 1. GitHub Actions billing — still down

Same annotation: *"The job was not started because recent account payments have failed or your spending limit needs to be increased."* Multi-day outage until Chris funds account.

**Self-merge protocol during outage** (Sessions 1149 + 1150 + 1158 pattern):

For every PR, run local mirrors before push:
```bash
.venv/bin/python scripts/verify_repo_guardrails.py --inventory-advisory
.venv/bin/python tools/check_direct_llm_calls.py --root . --whitelist .ci/llm_whitelist.txt --warn-only
```

Self-merge with bypass requires:
1. Both local mirrors run.
2. Only failure is the pre-existing `celery-beat-schedule` CONFLICT.
3. Merge commit body documents the bypass with both `billing outage` and `pre-existing CONFLICT` named.
4. PR scope is documentation or low-risk verifier baselines (no production code changes).

### 2. `celery-beat-schedule` CONFLICT — code-level fix done, detector signal pending

**Session 1157 (PR #2243):** Underlying code-vs-code contradiction CLOSED. `add_critical_celery_tasks.py` no longer carries its own `CRITICAL_TASKS` schedule.

**Context-kit CONFLICT signal still flags** because its detector heuristic is keyword/path-based across ~36 files. Session 1158 did NOT touch this. Queued for Session 1159+.

### 3. Disk + swap pressure on Chris's laptop — partially relieved Session 1158

Disk freed from 5.8 GiB → 37 GiB during Session 1158 (~31 GiB recovered). Swap still tight at session close (~1 GiB free of 12.3 GiB). PA worker functioning post-cleanup. Monitor at session 1159 open; if disk has crept back up, retry the cleanup sequence from `feedback_pa_hang_from_disk_pressure.md`.

---

## SESSION 1159 — CURRENT ENTRY POINT

### FIRST THING this session

**Check the PA stack is healthy.** Post Session 1158's disk-cleanup arc, the PA worker should be reachable.

1. Run `platform_config_tool overview` through Rigby to confirm `service_context: local`.
2. Confirm PA worker responds: `.venv/bin/celery -A core inspect ping --destination=pa@Chriss-MacBook-Pro.local` should reply pong (note: if it doesn't but tasks still process, that's a known inspect-mingle quirk — check `redis-cli LLEN pa` instead).
3. Check disk: `df -h /System/Volumes/Data`. If < 10 GiB free, run the cleanup playbook from `feedback_pa_hang_from_disk_pressure.md` before doing anything else.

If PA is healthy, retry the two Rigby-blocked items from Session 1158:

**A. Rigby's narrative review for B/C/D.** Queued during Session 1158 but worker hung mid-task. Use the same structured-review request format that worked for narrative A — per-narrative Template PASS/iterate + Voice PASS/iterate + Accuracy + Other notes, then cross-narrative coherence + drift list. All 15 narratives now on main; she can read them directly.

**B. Rigby's corpus sweep** on narrative A's open questions (OpportunityScoring replacement trigger / fate of 6 Struggling agents / `learning_bridge_audit` generator status). Queued before the hang.

### Then, after Rigby's review lands

Apply review feedback to relevant narratives if she flags iteration items. Otherwise proceed to the queued cleanup work below.

### Chris-call decisions (need explicit answers)

1. **`docs/reports/donkey-betz-codex-audit.md`** — marketing material (keep) or experiment leftover (move/archive)? Surfaced by Session 1158's recon (`docs/recons/REPORTS_PATENTS_RECON_2026_05_25.md`).
2. **May 25 09:36 batch** (12 docs in `docs/reports/` that landed within minutes of each other) — what agent generated this? Worth understanding the source before deciding whether to consolidate.

### Queued cleanup work (Chris's call on priority)

3. **Reports cleanup mechanical pass** — add `DOC-POINTER-V2 Superseded` to 9 Jan 21 docs, upgrade 2 V1 → V2, fix `INDEX.md` drift (30 → 33). Fully scriptable.
4. **Patents preservation + cross-linking** — write `docs/patents/README.md` with workstream structure + narrative cross-link map; add provenance frontmatter to all 16 patent files; cross-link narratives A/B/C/F/J/E to relevant disclosures. High-value because patents map 1:1 to subsystems.
5. **The 783 not-HIGH untagged handoffs (now 778 after Session 1158)** — alternate treatment for handoffs that didn't get cited by any Session 1158 narrative. Options: leave as-is (low-cost); manual hand-authored frontmatter pass; alternative provenance heuristic (e.g., session-arc grouping); selective archival.
6. **Old `docs/topics/` sweep** — 7 Feb-March docs deferred from Session 1147 #2221.
7. **Cosmetic `load_all_agents_advisors.py 149→139` fix** — queued from Session 1149.

### Deferred infrastructure track (avoid during offline-CI window)

8. **`celery-beat-schedule` CONFLICT — second-half cleanup** (detector signal clear). Two paths: (preferred) detector tuning — read-only investigation of context-kit's detector source. (fallback) Targeted 36-file token-pattern phrasing sweep.
9. **Pre-existing 3-row PeriodicTask drift** (80 DB rows vs 77 entries in `core/celery.py`). Folds into #8.
10. **`exists_on_disk: false` flag** in `_provenance.json` (since Session 1145) — 326 dead paths. Schema bump v1 → v2.
11. **Beat-schedule the regens** (since Session 1145) — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
12. **Fix `build_learning_bridge_audit.py` generator** (since Session 1146) — falsely flags "ABC unused".
13. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

### Chris-call-only carryovers (still parked)

14. **Decision Command backend cleanup** — 5 Python files (regressed feature).
15. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
16. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons (Sessions 1145–1158)

- **Recon before sweep.** Multiple back-to-back sessions where mid-recon findings flipped the PR plan. Session 1158 recon doc proved the pattern again.
- **Filename overrides for canonical names** (Session 1147 PR #2219).
- **`session: NNNN` → `originating_session: NNNN`** is the standard.
- **`build_*_audit` generators can lag reality.** Fix the generator, not the output.
- **Quick-wins-only is valid mode** when review fatigue is real.
- **(1149)** "Counts-hygiene" framing in start-here docs is ambiguous — disambiguate registered-claim drift vs body-level hardcoded counts.
- **(1149)** Stale log/docstring text inside command files can mislead future baselines (148 → 139 → 155 reconciliation).
- **(1149)** GH Actions billing failures are Chris-only blockers initially.
- **(1150)** Bypass-merging during a CI outage is workable IF disciplined. Local mirrors + per-merge bypass documentation + Rigby gate-checking the rules makes self-merge safe enough during a multi-day outage window.
- **(1150)** "One mechanical batch then stop" applies even when batches are easy.
- **NEW (1158)** **Narratives become canon; topic docs get corrected to match.** Narrative-writing surfaces drift; topic-doc drift sweep is a mechanical pass once narratives exist.
- **NEW (1158)** **Cited-by-narrative is a triage signal.** For the 783 not-HIGH handoffs, narrative citation = evidence-of-importance. Uncited after batch A–O = candidates for archive or alternate treatment.
- **NEW (1158)** **Disk + swap pressure mimics Celery bugs.** Captured to memory. Check disk before Celery rabbit-hole.
- **NEW (1158)** **`unified-postgres` lives in Docker.** Don't `docker system prune` or restart Docker as a whole.
- **NEW (1158)** **Multi-narrative single-PR is viable.** PR #2250 batched 11 narratives in one PR and merged cleanly. Faster than the merge-conflict-resolution dance for A→B→C→D's individual PRs.

---

## RECENT SESSION ARCS

- **Session 1158** — corpus-narrative program: 15 narratives (A–O) + drift sweep + cited-handoff frontmatter + reports/patents recon + 1 memory entry. 8 PRs merged.
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
