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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars. Current pinned conversation: `pa-f93d77e34f5d` (set Session 1159; carried into 1160).

## READ THIS SECOND — PA "CONSUME-1-THEN-HANG" IS USUALLY DISK PRESSURE

Memory: `feedback_pa_hang_from_disk_pressure.md`. If the PA worker processes exactly one task and then goes silent, check `df -h /System/Volumes/Data` + `sysctl vm.swapusage` BEFORE deeper Celery debugging. Single-digit GiB free or swap < 2 GiB free → free disk first. Don't restart Docker — `unified-postgres` lives there.

## READ THIS THIRD (NEW Session 1160) — `git show` IS THE FIRST MOVE FOR MTIME MYSTERIES

If you see a cluster of doc mtimes within minutes of each other and wonder "what generated this?", run `git log --since="<timestamp - 1min>" --until="<timestamp + 1min>"` first. Session 1160's "May 25 09:36 batch" mystery resolved instantly via `git show 9d75f78f` — it was Chris's own Session 1143 PR #2197. Future similar questions should start with the git history before invoking Rigby's ops tools.

## SOURCE OF TRUTH

Per Session 1144 PR #2208 (canon rebase) + Session 1146 PR #2216 (Runtime Evidence promotion) + Session 1158 (narratives layer) + Session 1159 (EDITING_GUARDRAILS) + Session 1160 (patents README + PR template):

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`).
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts).
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/narratives/`** — 15 subsystem narratives (A–O). Operator-handbook layer.
5. **`docs/narratives/EDITING_GUARDRAILS.md`** — 7-rule editing contract + pre-PR checklist (Session 1160 add).
6. **`docs/patents/README.md`** — 4-workstream + disclosure → narrative cross-link map (Session 1160 add).
7. **`docs/case-studies/`** — historical case studies (Session 1160 added codex-audit + drift-reconciliation table).
8. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
9. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
10. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
11. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
12. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
13. **`docs/specs/`** — engineering specs.
14. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence. Regenerate with `build_*_audit` mgmt commands.
15. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`**.
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N`
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json`.
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145–1160 ran 100% subject-tagged. Keep the streak.

## NARRATIVE-EDIT PR CHECKLIST (Session 1160)

`.github/PULL_REQUEST_TEMPLATE.md` includes a conditional "Narrative-edit checklist" that PR authors fill out when the PR modifies any file in `docs/narratives/`. The 7-item checkbox list maps 1:1 to `docs/narratives/EDITING_GUARDRAILS.md` rules. Required only when changes touch narratives.

Authoring rule of thumb: if the PR introduces a new rule/process, dogfood the rule on its own diff before opening. The `#2256 → #2257` loop (PR #2256 introduced EDITING_GUARDRAILS and still violated rules #1 + #5 in 5 places) is the cautionary tale captured both in the EDITING_GUARDRAILS source addendum and the Session 1159+1160 handoffs.

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

Tested Session 1159 post-Mac-reboot: full stack restart from cold-boot in ~30 s. Clear stale pids first (`rm -f .celery*.pid .daphne.pid`) before `make all`.

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- **PA tool registration needs BOTH daphne AND celery restart.** `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **search_docs originating_session filter cache:** `lru_cache(1)` per process. After `build_docs_provenance` regen, restart workers.
- **`process_pa_chat_task` uses `acks_late=False`** (Session 1159 PR #2255). Overrides the global `CELERY_TASK_ACKS_LATE=True` because the global setting + unstable macOS broker conn was producing tasks stuck in `unacked` for an hour.

---

## SESSION 1160 CLOSED — Session 1158-carryover queue clear + EDITING_GUARDRAILS operational (2026-05-26)

**6 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1160_QUEUE_CLEAR_AND_GUARDRAILS_OPERATIONAL.md`](docs/handoffs/SESSION_1160_QUEUE_CLEAR_AND_GUARDRAILS_OPERATIONAL.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2259** | codex-audit relocation: reports/ → case-studies/ + historical banner | `d8eedb18` |
| **#2260** | May 25 09:36 batch resolved (git show → PR #2197) | `5fc7871b` |
| **#2261** | reports cleanup mechanical pass (9 V2 + 2 V1→V2 + INDEX drift fix) | `7e71b2df` |
| **#2262** | patents preservation + cross-link map (16 files + new README) | `572c4928` |
| **#2263** | narrative → patent reverse cross-links (6 narratives) | `fb5aa7ed` |
| **#2264** | .github/PULL_REQUEST_TEMPLATE.md + EDITING_GUARDRAILS pre-PR checklist | `e876fce5` |
| **#2266** | pa_acks_health mgmt command — observation scaffold for acks_late=False watch | `f5dbea1e` |
| **#2267** | pa_acks_health status + cutoff display (Rigby's E + D feedback) | `4c39501a` |

**New persistent artifacts:** `docs/patents/README.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `core/management/commands/pa_acks_health.py`.

### Previous closed work still relevant for context

- **Session 1159** — PA acks_late fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs.
- **Session 1158** — 15 subsystem narratives shipped. Template v1-LOCKED. 8 PRs.

---

## 🚨 ACTIVE ISSUES carrying into Session 1161

### 1. GitHub Actions billing — still down

Same annotation as Sessions 1149+. Multi-day outage until Chris funds account.

**Self-merge protocol during outage** (Sessions 1149 + 1150 + 1158 + 1159 + 1160 pattern):

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
5. Production-code changes need explicit per-PR Chris-authorization in-session (Session 1159 PR #2255 precedent).

### 2. `celery-beat-schedule` CONFLICT — detector signal pending

Session 1157 PR #2243 closed the code-level footgun. Context-kit CONFLICT signal still flags because its detector heuristic is keyword/path-based across ~36 files. Queued for Session 1161+.

### 3. PA `acks_late=False` 24-48h observation window

Continued from Session 1159 PR #2255. Watch `pa` queue depth + UI behavior:
- Tasks should ack immediately on receipt (LLEN pa drops to 0 within seconds).
- No regression in worker crash recovery.
- If symptoms persist, the broker conn instability is upstream of the ack pattern.

---

## SESSION 1161 — CURRENT ENTRY POINT

### FIRST THING this session

**Check the PA stack is healthy.** Run `platform_config_tool overview` through Rigby to confirm `service_context: local`. PA conversation pinned in `tools/pa_local.sh`: `pa-f93d77e34f5d` (set Session 1159 — if Chris opened a new conversation, update the wrapper first).

Disk check: `df -h /System/Volumes/Data`. If < 10 GiB free, run cleanup playbook from `feedback_pa_hang_from_disk_pressure.md` before doing anything else.

### Queue is clear of Session 1158-1159 carryovers

All Chris-call items from the Session 1158 recon are closed (PRs #2259-2264 inclusive). The remaining queue is composed of passive observation items + active queue items + deferred infrastructure track. **No items are blocked on Chris-decision** at session open — Chris can pick any of the active items below.

### Passive observation items

1. **PA `acks_late=False` observation window** (active issue #3 above). Use `python manage.py pa_acks_health` for snapshots. Baseline at Session 1160 close: OK / 12 SUCCESS / 0 FAILURE / 0 hangs.
2. **EDITING_GUARDRAILS opportunistic rollout** to narratives A / E / F / G / H / I / J / K / L / M / N / O. Pick up when next editing each narrative; not a batch.
3. **Disclosure L narrative coverage gap.** Self-tuning experimentation lacks a Session 1158 narrative. Fold into BODY_SYSTEMS or CONTENT_PIPELINE, or write a new narrative when the subsystem matures.

### `pa_acks_health` follow-ons (from Rigby's PR #2266+#2267 review)

3a. **(A) Ack behavior proxy** — age of oldest queued / STARTED, received-vs-finished delta over window.
3b. **(B) Per-worker attribution** — PID, last heartbeat, per-worker hang/slow counts.
3c. **(C) UI spinner symptom proxy** — chat requests with no assistant response recorded within N minutes (via `ChatConversation` rows).
3d. **Threshold tuning** — three small tunings dependent on item A:
   - WARN on queue depth ≥ 5 (currently ≥ 1).
   - CRIT "no workers sustained" — explicit sustain window (≥ 2 consecutive snapshots).
   - CRIT queue depth ≥ 20 — pair with second condition (workers < 2 OR oldest queued age > 120s).

### Active queue (Chris's call on priority)

4. **Old `docs/topics/` sweep** — 7 Feb-March docs deferred from Session 1147 #2221. Now smaller because Session 1158's drift sweep already corrected the ones surfaced by narratives.
5. **Cosmetic `load_all_agents_advisors.py 149→139` fix** — queued from Session 1149.

### Deferred infrastructure track (avoid during offline-CI window)

6. **`celery-beat-schedule` CONFLICT — detector tuning** (preferred) or 36-file token-pattern phrasing sweep (fallback).
7. **Pre-existing 3-row PeriodicTask drift** (80 DB rows vs 77 entries in `core/celery.py`). Folds into #6.
8. **`exists_on_disk: false` flag** in `_provenance.json` — 326 dead paths. Schema bump v1 → v2.
9. **Beat-schedule the regens** — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
10. **Fix `build_learning_bridge_audit.py` generator** — falsely flags "ABC unused".
11. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

### Chris-call-only carryovers (still parked)

12. **Decision Command backend cleanup** — 5 Python files (regressed feature).
13. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
14. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons (Sessions 1145–1160)

- **Recon before sweep.** Multiple back-to-back sessions where mid-recon findings flipped the PR plan.
- **Narratives become canon; topic docs get corrected to match** (1158).
- **`docs/*_AUDIT.md` files may be DOC-AUTOGEN** — check line 1 for marker before banner sweep (1146).
- **`build_*_audit` generators can lag reality** — fix the generator, not the output (1146).
- **Bypass-merging during a CI outage is workable IF disciplined** (1150).
- **"One mechanical batch then stop" applies even when batches are easy** (1150).
- **Cited-by-narrative is a triage signal** for the 778 not-HIGH handoffs (1158).
- **Disk + swap pressure mimics Celery bugs** — check disk first (1158).
- **`unified-postgres` lives in Docker** — don't `docker system prune` or restart Docker as a whole (1158).
- **EDITING_GUARDRAILS is load-bearing** for any narrative edit (1159).
- **Self-referential dogfood.** A guardrails-introducing PR can still violate its own rules — `#2256 → #2257` (1159). PR-template checklist closes the loop (1160).
- **Production-code bypass needs explicit per-PR Chris auth** (1159).
- **Stack restart playbook works in ~30 s** post-Mac-reboot (1159).
- **NEW (1160)** **`git show` first for mtime mysteries** — before invoking ops tools, `git log --since/--until <timestamp>` resolves nearly every case.
- **NEW (1160)** **Symmetric cross-references prevent half-resolved navigation** — pair `maps_to_*` frontmatter with reverse "Related X" sections.
- **NEW (1160)** **Append-only edits are safer than restructure for high-trust documents** — PR #2263 added cross-link sections at the end of 6 narratives without touching milestone tables or vocabulary sections.

---

## RECENT SESSION ARCS

- **Session 1160** — 1158-carryover queue clear + EDITING_GUARDRAILS operational. 6 PRs merged.
- **Session 1159** — PA acks_late fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs merged.
- **Session 1158** — corpus-narrative program: 15 narratives + drift sweep + cited-handoff frontmatter + reports/patents recon. 8 PRs merged.
- **Session 1157** — celery-beat-schedule cleanup option A. 1 PR merged (bypass mode).
- **Session 1156** — P3.5 round 9 (FINAL) + P3.5 track CLOSE. 1 PR merged.
- **Session 1155** — P3.5 round 8. 1 PR merged.
- **Session 1154** — P3.5 round 7. 1 PR merged.
- **Session 1153** — P3.5 round 6. 1 PR merged.
- **Session 1152** — P3.5 round 5. 1 PR merged.
- **Session 1151** — P3.5 round 4. 1 PR merged.
- **Session 1150** — Session 1149 merge wave + P3.5 round 3. 4 PRs merged.
- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes. 3 PRs.
- **Earlier:** see `docs/handoffs/CURRENT.md`.
