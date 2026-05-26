---
originating_session: 1158
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1158 handoff. Largest single-session corpus deliverable to date — 15 narratives + 4 cleanup PRs + recon + new memory entry.
---

# Session 1158 — corpus-narrative program (15 narratives + cleanup arc)

**Date:** 2026-05-25 (fourteenth back-to-back session, first session of the post-P3.5 pivot's main work)
**Branch state at session close:** All work merged. Main is clean. Six PRs landed.

---

## TL;DR

Session 1158 was the actual execution of the corpus-narrative program that the Session 1157 handoff scoped. Chris's framing at the start: "I still want to finish going through all of the /docs/. Right now they are just a bunch of text from the last few years of building. But what we need it to do is read in a way anyone can understand it if they don't have access to the UI."

Output: **15 subsystem narratives** in `docs/narratives/` (A–O), template-locked at v1 after batch A passed Rigby's review. Plus three side-effect PRs (topic-doc drift fixes, cited-handoff frontmatter, reports/patents recon). Plus one new memory entry captured from a late-session local PA hang debug.

Late-session interruption: laptop disk hit 99% full, swap exhausted, PA worker started failing in a "consume-1-then-hang" pattern. Diagnosed and captured as memory entry; restart unblocked after cleanup.

---

## What shipped

| PR | Theme | Merge SHA |
|----|-------|-----------|
| **#2246** | Narrative A pilot — Agents, Autonomy & Governance (template-LOCKED v1 after Rigby PASS) | `0bd2f4cc` |
| **#2247** | Narrative B — Content Pipeline | `dc7d9f1b` |
| **#2248** | Narrative C — Signal Intelligence | `a41f2ad6` |
| **#2249** | Narrative D — Personal Assistant (Rigby) | `36d6ddfa` |
| **#2250** | Narrative slate completion — 11 narratives (E–O) in one PR | `3730f993` |
| **#2251** | Topic-doc drift sweep — 7 docs corrected against runtime | `5ff6361b` |
| **#2252** | Cited-handoff frontmatter — 5 handoffs got HIGH provenance with narrative-citation note | `ecb66e8d` |
| **#2253** | docs/reports/ + docs/patents/ recon (read-only; no action) | `201008df` |

Six narrative PRs (A–O) + three follow-up cleanup PRs = 9 squash-merge commits to main, all via bypass-mode (GH Actions billing still down).

---

## The 15 narratives

All on main in `docs/narratives/`:

| File | Center of gravity |
|---|---|
| `AGENTS_AND_AUTONOMY.md` | Knowledge pipeline (Session 400) → governance arc (Sessions 1092–1099) → code-health refactor (Session 1115). 8 milestones. |
| `CONTENT_PIPELINE.md` | Session 964 deliberation watershed (ClaimsPack → 3-reviewer → DecisionEnforcer → PublishGate). 8 milestones. |
| `SIGNAL_INTELLIGENCE.md` | Session 900 provenance chain through Session 1033 "first initiatives EVER completed." 8 milestones. |
| `PERSONAL_ASSISTANT.md` | Session 1036 GPT-5.2 function calling watershed (replaced 506-line keyword router). 8 milestones. |
| `WORKERS_AND_INFRASTRUCTURE.md` | OOM arc (Sessions 1029–1064) culminating in `sync_task_queues` + `QueuePreservingScheduler`. macOS playbook. 8 milestones. |
| `BODY_SYSTEMS.md` | 9 systems + BodyCoordinator. NERVOUS clarified as not-in-scan via core/tasks.py:body_systems list. 6 milestones. |
| `FRONTEND.md` | 9→5 tab consolidation (Session 1100); 61 routes; 3 PA surfaces. 8 milestones. |
| `KNOWLEDGE_RAG_MEMORY.md` | 3 memory surfaces + 2 RAG paths (production pgvector vs local Ollama). 8 milestones. |
| `ADVISORS.md` | Session 1142 rename: 25 legendary → 30 functional specialists. 26/26 domains. 5 milestones. |
| `DECISION_COMMAND.md` | Cross-cut of A/B/C/D for the boardroom/governance surface. 6 milestones. |
| `DISCORD.md` | 25 Cogs, 96 commands, Session 1115 144→96 correction. 7 milestones. |
| `SPORTS_MONETIZATION_ML.md` | Verifiable feedback loops (sports/stocks/Gumroad). 8 milestones. |
| `FLEET_INTEGRATION.md` | 7 Docker apps + HMAC + Move 3 R2 replay + footgun. 8 milestones. |
| `STRATEGY_247_GLOBAL_AI.md` | Atlas v1 + Jessica's 22 decisions + Chris's ratification. 8 milestones. |
| `SPOKESPERSON_CHARACTER_OS.md` | Phase 4+ vision + Session 1117 first pass + avatar split. 6 milestones. |

All narratives:
- Anchor counts to `PLATFORM_INVENTORY.md` 2026-05-25 (`d513cd7f`)
- Label uncertainty inline (Known / Inferred / Unknown)
- Use Rigby's v1-LOCKED 7-section template
- Cross-reference each other (A↔B↔C↔D↔E↔F↔G↔H↔I↔J↔K↔L↔M↔N↔O)
- Audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI

---

## Side-effect work (PRs #2251–#2253)

### PR #2251 — topic-doc drift sweep

Narrative-writing surfaced specific drift between topic docs and runtime/inventory. 7 topic docs corrected:

- `celery-workers.md`: 271 → 401 Celery tasks
- `spider-network.md`: 18 → 41 categories; 7 → 10 pattern types (added competitive_signal, market_movement, user_need)
- `body-systems.md`: clarified NERVOUS is a service but not in `run_all_systems_scan` (resolves narrative F's open question)
- `DISCORD_INTEGRATION.md`: 144 → 96 commands (regex double-count via Session 1115 AST audit)
- `personal-assistant.md`: 106/171 → 104/169 tools
- `initiative-pipeline.md`: backlog threshold 20 → 50 (env default)
- `frontend.md`: 9-tab table relabeled as legacy sub-area taxonomy under post-1100 5-primary-tab architecture

Pattern: narratives become canon; topic docs get corrected to match.

### PR #2252 — cited-handoff frontmatter

24 handoffs cited by Session 1158 narratives. 22 already had full provenance frontmatter from the P3.5 backfill arc (Sessions 1147–1156). 5 needed work — added HIGH-confidence frontmatter with explicit `provenance_note` recording which narrative(s) cite each handoff:

- `SESSION_969b_PA_LIVE_TELEMETRY.md` (frontmatter added from scratch)
- `SESSION_993_PA_CAPABILITY_GAPS.md` (frontmatter added from scratch)
- `SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md` (added missing fields)
- `SESSION_1117_LOCAL_PORTFOLIO_GROUNDING_BRIDGE.md` (added missing fields)
- `SESSION_1141_JESSICA_RATIFICATION_DEEP_DIVES.md` (added missing fields)

Demonstrates the cited-by-narrative pattern as a triage signal: cited = evidence-of-importance = priority for HIGH provenance.

### PR #2253 — docs/reports/ + docs/patents/ recon (read-only)

Recon-only PR per Session 1147 deferral. Findings:

**`docs/reports/` (33 files, 360 KB):**
- 19 already have `DOC-POINTER-V2 Superseded` headers (Session 1143 pass)
- 9 Jan 21 vintage docs lack headers — candidates for header pass
- 2 have older V1 headers — candidates for V2 upgrade
- 1 auto-generated (`VERIFY_REPORT.md`)
- 1 INDEX.md drift (claims 30, actual 33)
- 1 recent codex-audit doc — classification needed

**`docs/patents/` (16 files, 316 KB):** HIGH-VALUE IP material.
- 12 substantive invention disclosure drafts (A–L), March 16, 2026
- 4 executive summaries (top + WS2/WS3/WS4)
- Status: "Draft — Attorney Review Pending". Inventor: Chris West.
- **All 12 disclosures map 1:1 to platform subsystems** in Session 1158 narratives — cross-link map in `docs/recons/REPORTS_PATENTS_RECON_2026_05_25.md`

No files moved/archived/deleted in this PR. Recon doc is the deliverable; recommendations are proposals for Chris's call.

---

## Late-session incident: PA "consume-1-then-hang"

Mid-late session, attempts to reach Rigby (for narrative review + queued corpus sweep) failed with "Task not found or result expired" pattern. PA worker would process exactly one task in ~15–20s, complete it, then go silent.

**Root cause:** laptop disk at 99% full (5.8 GiB free of 460 GiB), swap at 91% used (1 GiB free of 12.3 GiB). PA worker has `--max-memory-per-child=200 MB`; under that pressure, a single PA task's working set silently exceeded the cap, OS killed the child without a clean log line, parent couldn't fork a new clean child.

**Diagnosis sequence:**
1. `redis-cli LLEN pa` on DB2 showed 5 tasks queued (including Chris's "Are you working?" from ChatUI) → broker fine
2. Worker process alive in `ps`, but `inspect ping --destination=pa@…` silent → worker dead-but-not-dead
3. Restart of Celery worked for 1 task each time, then re-hang
4. `df -h /System/Volumes/Data` + `sysctl vm.swapusage` revealed the actual constraint

**Fix:** Chris freed disk to 37 GiB. Restarted daphne + celery (not Docker — `unified-postgres` lives there). Worker resumed processing tasks back-to-back without dying.

**Captured to memory:** `feedback_pa_hang_from_disk_pressure.md`. Future sessions will recognize the consume-1-then-hang pattern as a disk-pressure symptom before going down the Celery rabbit hole.

---

## Carryover items into Session 1159

### Rigby-blocked items (retry once PA is reliably reachable)

1. **Rigby's review of narratives B/C/D.** Queued earlier but the worker hung mid-task. Same template-compliance + accuracy + drift pass she did on A. Now that disk is healthy, retry.
2. **Rigby's corpus sweep on A's open questions** (OpportunityScoring replacement trigger / fate of 6 Struggling agents / `learning_bridge_audit` generator status). Queued before the hang; never resolved.

### Chris-call items (need explicit decision)

3. **`docs/reports/donkey-betz-codex-audit.md`** — marketing material (keep as external case study) or experiment leftover (move/archive)? Recon doc surfaced the question; no header applies cleanly to either case.
4. **May 25 09:36 batch (12 docs)** — what agent generated this? All landed within minutes of each other; smells like a single agent run. Worth understanding the source before deciding whether to consolidate.

### Side-effect work queued (Chris's call on priority)

5. **Reports cleanup mechanical pass.** Add `DOC-POINTER-V2 Superseded` to 9 Jan 21 docs. Upgrade 2 V1 headers to V2. Fix `INDEX.md` drift (30→33). Leave `VERIFY_REPORT.md` alone (auto-gen). ~1 PR, fully scriptable.
6. **Patents preservation + cross-linking.** Write `docs/patents/README.md` with workstream structure + narrative cross-link map. Add provenance frontmatter to all 16 patent files. Cross-link narratives A/B/C/F/J/E to relevant disclosures.
7. **Old `docs/topics/` sweep** (7 Feb-March docs deferred from Session 1147 #2221). Still queued.
8. **Cosmetic `load_all_agents_advisors.py 149→139` fix.** Queued from Session 1149.
9. **The 783 not-HIGH untagged handoffs** — partial dent made via the cited-by-narrative pass (PR #2252). Remaining 778 need different treatment. Narrative-citation-as-triage-signal is the working model now; uncited handoffs after batch A–O = candidates for archive or alternate provenance heuristic. The corpus-narrative program may eventually surface more citations and reduce the uncited count organically.

### Deferred infrastructure track (unchanged from Session 1157)

10. **`celery-beat-schedule` CONFLICT — detector signal cleanup.** Session 1157 closed the underlying code-level footgun (PR #2243). Context-kit detector still flags ~36 files broader than the closed pair. Two paths: detector tuning OR targeted phrasing sweep.
11. **Pre-existing 3-row PeriodicTask drift** (80 DB rows vs 77 in `core/celery.py`). Folds into #10.
12. **`exists_on_disk: false` flag in `_provenance.json`** (Session 1145+). 326 dead paths. Schema bump v1→v2.
13. **Beat-schedule the regens** (Session 1145+). Weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
14. **Fix `build_learning_bridge_audit.py` generator** (Session 1146+). Falsely flags "ABC unused" — generator-stale.
15. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites). Mirror the OpenAI/Anthropic factory pattern.

### Chris-call-only carryovers (still parked)

16. Decision Command backend cleanup — 5 Python files (regressed feature).
17. DaVinci route removal — `core/views_davinci.py` still routed.
18. Mission refresh PR #2190 — preserved branch.

---

## New memory entry captured

**`feedback_pa_hang_from_disk_pressure.md`** — PA worker "consume-1-then-hang" pattern is usually disk + swap pressure, not Celery. Before deeper Celery diagnosis, check `df -h` + `sysctl vm.swapusage`. If disk single-digit GiB or swap < 2 GiB free, free disk first (Docker prune, simctl delete unavailable, npm cache clean, pip cache, browser caches). Don't restart Docker — `unified-postgres` lives there. Listed in `MEMORY.md` next to the Celery PID cache entry.

Pointer added to `MEMORY.md` in the feedback section.

---

## Counts at session close

| Metric | Value |
|---|---|
| Narratives in `docs/narratives/` | **15** (A–O) |
| Topic docs corrected (drift) | 7 |
| Handoffs gaining HIGH provenance via cited-by-narrative | 5 |
| Recon docs (no action taken) | 1 (`docs/recons/REPORTS_PATENTS_RECON_2026_05_25.md`) |
| New memory entries | 1 (`feedback_pa_hang_from_disk_pressure.md`) |
| PRs merged | 8 |
| PRs merged via bypass mode | 8 |
| Code changes | 0 (doc-only across all PRs) |
| Disk reclaimed during session | ~31 GiB (5.8 → 37 GiB free) |

---

## Cross-session lessons (carry forward)

- **Narratives become canon, topic docs get corrected to match.** The pattern that fell out of the program: narrative-writing surfaces drift; the topic-doc drift sweep is a mechanical pass once narratives exist.
- **Cited-by-narrative is a triage signal.** For the 783 not-HIGH handoffs, narrative citation is evidence-of-importance. Uncited after batch A–O = candidates for archive or alternate treatment.
- **Disk + swap pressure mimics Celery bugs.** Captured to memory. Saved future sessions from the same diagnostic spiral.
- **`unified-postgres` lives in Docker.** Don't `docker system prune` or restart Docker as a whole.
- **Bypass-merge mode held discipline.** 8 PRs landed cleanly; merge commits all documented the bypass + the pre-existing CONFLICT + the doc-only scope.
- **Multi-narrative single-PR is viable.** PR #2250 batched 11 narratives in one PR and merged cleanly. Compared to the merge-conflict-resolution dance for A→B→C→D's individual PRs, batching was significantly faster.
