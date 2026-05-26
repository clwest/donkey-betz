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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars. Current pinned conversation: `pa-f93d77e34f5d` (set Session 1159).

## READ THIS SECOND — PA "CONSUME-1-THEN-HANG" IS USUALLY DISK PRESSURE

Memory: `feedback_pa_hang_from_disk_pressure.md`. If the PA worker processes exactly one task and then goes silent, check `df -h /System/Volumes/Data` + `sysctl vm.swapusage` BEFORE deeper Celery debugging. Single-digit GiB free or swap < 2 GiB free → free disk first (Docker prune, simctl delete unavailable, npm cache clean, pip cache, browser caches). Don't restart Docker — `unified-postgres` lives there.

## SOURCE OF TRUTH

Per Session 1144 PR #2208 (canon rebase) + Session 1146 PR #2216 (Runtime Evidence promotion) + Session 1158 (narratives layer) + Session 1159 (EDITING_GUARDRAILS):

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`).
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts).
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/narratives/`** — 15 subsystem narratives (A–O) shipped Session 1158, hedged + EDITING_GUARDRAILS in Session 1159. Operator-handbook layer. Audience: future-Claude / future-hire / future-Chris who can't access UI.
5. **`docs/narratives/EDITING_GUARDRAILS.md`** — 7-rule editing contract (Session 1159). Applies to every current and future narrative edit.
6. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
7. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
8. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
9. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
10. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
11. **`docs/specs/`** — engineering specs.
12. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence. Regenerate with `build_*_audit` mgmt commands.
13. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

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

Sessions 1145–1159 ran 100% subject-tagged. Keep the streak.

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

## SESSION 1159 CLOSED — PA acks + narrative B/C/D review + EDITING_GUARDRAILS (2026-05-26)

**3 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1159_PA_TASK_ACKS_AND_NARRATIVE_REVIEW.md`](docs/handoffs/SESSION_1159_PA_TASK_ACKS_AND_NARRATIVE_REVIEW.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2255** | `acks_late=False` on `process_pa_chat_task` (production code, explicit Chris bypass auth) | `3a7e347c` |
| **#2256** | Narrative B/C/D iterations + new `EDITING_GUARDRAILS.md` | `d73f6824` |
| **#2257** | Narrative B/C/D follow-ups from Rigby's verification | `77c68c01` |

**New persistent artifact:** `docs/narratives/EDITING_GUARDRAILS.md` — 7-rule editing contract for every current + future narrative.

### Previous closed work still relevant for context

- **Session 1158** — 15 subsystem narratives shipped. Template v1-LOCKED.
- **Session 1157** — celery-beat-schedule cleanup option A. Code-level footgun closed; context-kit CONFLICT signal still flags.
- **Session 1156** — P3.5 TRACK COMPLETE. Pool exhausted; 646 handoffs auto-backfilled across 9 rounds.

---

## 🚨 ACTIVE ISSUES carrying into Session 1160

### 1. GitHub Actions billing — still down

Same annotation as Sessions 1149+. Multi-day outage until Chris funds account.

**Self-merge protocol during outage** (Sessions 1149 + 1150 + 1158 + 1159 pattern):

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

**Session 1159 addition: production-code bypass needs explicit per-PR Chris authorization.** PR #2255 set the precedent — Chris authorizes in-session, merge commit body names the deviation explicitly.

### 2. `celery-beat-schedule` CONFLICT — detector signal pending

Session 1157 (PR #2243) closed the underlying code-vs-code contradiction. Context-kit CONFLICT signal still flags because its detector heuristic is keyword/path-based across ~36 files. Queued for Session 1160+.

### 3. PA `acks_late=False` 24-48h observation window

Session 1159 PR #2255 set `acks_late=False` on `process_pa_chat_task` to fix the unacked-task-stuck-for-an-hour symptom. Watch `pa` queue depth + UI behavior over 24-48 h:
- Tasks should ack immediately on receipt (LLEN pa drops to 0 within seconds).
- No regression in worker crash recovery (rare; user retypes if it happens).
- If symptoms persist, the broker conn instability is upstream of the ack pattern.

---

## SESSION 1160 — CURRENT ENTRY POINT

### FIRST THING this session

**Check the PA stack is healthy.** Run `platform_config_tool overview` through Rigby to confirm `service_context: local`. PA conversation pinned in `tools/pa_local.sh`: `pa-f93d77e34f5d` (set Session 1159 — if Chris opened a new conversation, update the wrapper first).

Disk check: `df -h /System/Volumes/Data`. If < 10 GiB free, run cleanup playbook from `feedback_pa_hang_from_disk_pressure.md` before doing anything else.

### Chris-call decisions still pending (from Session 1158)

1. **`docs/reports/donkey-betz-codex-audit.md`** — marketing material (keep) or experiment leftover (move/archive)?
2. **May 25 09:36 batch** (12 docs in `docs/reports/` that landed within minutes of each other) — what agent generated this batch?

### Queued cleanup work (Chris's call on priority)

3. **Reports cleanup mechanical pass** — add `DOC-POINTER-V2 Superseded` to 9 Jan-21 docs, upgrade 2 V1 → V2, fix `INDEX.md` drift (30 → 33). Fully scriptable.
4. **Patents preservation + cross-linking** — write `docs/patents/README.md` with workstream structure + narrative cross-link map; add provenance frontmatter to all 16 patent files; cross-link narratives A/B/C/F/J/E to relevant disclosures. High-value because patents map 1:1 to subsystems.
5. **The 778 not-HIGH untagged handoffs** — alternate treatment for handoffs that didn't get cited by any Session 1158 narrative. Options: leave as-is (low-cost); manual hand-authored frontmatter pass; alternative provenance heuristic; selective archival.
6. **Old `docs/topics/` sweep** — 7 Feb-March docs deferred from Session 1147 #2221.
7. **Cosmetic `load_all_agents_advisors.py 149→139` fix** — queued from Session 1149.

### New from Session 1159

8. **PA acks_late observation window** (item #3 above in active issues).
9. **Apply EDITING_GUARDRAILS to other narratives** — the contract was derived from B/C/D but applies to all 15. A/E/F/G/H/I/J/K/L/M/N/O have not been reviewed under the guardrails yet. Opportunistic, not batch — pick up when next editing each narrative.

### Deferred infrastructure track (avoid during offline-CI window)

10. **`celery-beat-schedule` CONFLICT — detector tuning** (preferred) or 36-file token-pattern phrasing sweep (fallback).
11. **Pre-existing 3-row PeriodicTask drift** (80 DB rows vs 77 entries in `core/celery.py`). Folds into #10.
12. **`exists_on_disk: false` flag** in `_provenance.json` — 326 dead paths. Schema bump v1 → v2.
13. **Beat-schedule the regens** — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
14. **Fix `build_learning_bridge_audit.py` generator** — falsely flags "ABC unused".
15. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern from PR #2201.

### Chris-call-only carryovers (still parked)

16. **Decision Command backend cleanup** — 5 Python files (regressed feature).
17. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
18. **Mission refresh PR #2190** — preserved branch.

### Cross-session lessons (Sessions 1145–1159)

- **Recon before sweep.** Multiple back-to-back sessions where mid-recon findings flipped the PR plan.
- **Narratives become canon; topic docs get corrected to match** (1158).
- **`docs/*_AUDIT.md` files may be DOC-AUTOGEN** — check line 1 for marker before banner sweep (1146).
- **`build_*_audit` generators can lag reality** — fix the generator, not the output (1146).
- **Counts-hygiene framing in start-here docs is ambiguous** — disambiguate registered-claim drift vs body-level hardcoded counts (1149).
- **Bypass-merging during a CI outage is workable IF disciplined** (1150).
- **"One mechanical batch then stop" applies even when batches are easy** (1150).
- **Cited-by-narrative is a triage signal** for the 778 not-HIGH handoffs (1158).
- **Disk + swap pressure mimics Celery bugs** — check disk first (1158).
- **`unified-postgres` lives in Docker** — don't `docker system prune` or restart Docker as a whole (1158).
- **Multi-narrative single-PR is viable** — PR #2250 batched 11 narratives in one PR (1158).
- **NEW (1159)** **EDITING_GUARDRAILS is load-bearing** for any narrative edit. Rules #1 (number pointers), #5 (soften absolutes), #7 (counts as snapshots) are highest-frequency violations.
- **NEW (1159)** **Self-referential dogfood.** A guardrails-introducing PR can still violate its own rules. Plan for the follow-up loop (review → apply → verify → re-apply); don't assume single-pass.
- **NEW (1159)** **Production-code bypass needs explicit per-PR Chris auth.** Session-1150 protocol covers docs/verifier-baselines; production code is an explicit deviation.
- **NEW (1159)** **Stack restart playbook works in ~30 s** post-Mac-reboot. Clear pids → Docker (auto-restores containers) → `make all`.

---

## RECENT SESSION ARCS

- **Session 1159** — PA acks_late fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs merged.
- **Session 1158** — corpus-narrative program: 15 narratives (A–O) + drift sweep + cited-handoff frontmatter + reports/patents recon + 1 memory entry. 8 PRs merged.
- **Session 1157** — celery-beat-schedule cleanup option A. 1 PR merged (bypass mode) + handoff.
- **Session 1156** — P3.5 round 9 (FINAL) + P3.5 track CLOSE. 1 PR merged (bypass mode) + handoff.
- **Session 1155** — P3.5 round 8. 1 PR merged (bypass mode) + handoff.
- **Session 1154** — P3.5 round 7. 1 PR merged (bypass mode) + handoff.
- **Session 1153** — P3.5 round 6. 1 PR merged (bypass mode) + handoff.
- **Session 1152** — P3.5 round 5. 1 PR merged (bypass mode) + handoff.
- **Session 1151** — P3.5 round 4. 1 PR merged (bypass mode) + handoff.
- **Session 1150** — Session 1149 merge wave + P3.5 round 3. 4 PRs merged (bypass mode).
- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes. 3 PRs (held on billing in 1149; merged in 1150).
- **Earlier:** see `docs/handoffs/CURRENT.md`.
