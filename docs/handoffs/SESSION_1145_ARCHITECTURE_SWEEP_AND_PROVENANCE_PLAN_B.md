---
originating_session: 1145
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1145 — Architecture sweep (2 PRs) + Provenance Plan B (1 PR)

**Date:** 2026-05-25
**Branch state at session close:** 3 PRs open, all pushed, all reviewable independently. No merge ordering constraints.

---

## TL;DR

All 10 Session 1144 PRs merged before this session opened, queue was clean. Session 1145 was straight execution against the priorities Rigby pre-specced in `00-START-NEXT-SESSION.md`:

1. **Architecture sweep** (Rigby-driven scope decisions) — closed the `docs/architecture/` corpus: PR1 (#2211) rewrote `INDEX.md` + `README.md` as folder-local nav (removed Session 85 "master architecture" + "99.9% Reality" + "34 features" + "20+ tools" + "Launch readiness 85%" claims that violated `DOC_LIFECYCLE.md` §2c). PR2 (#2212) applied V1/V2 banners to 8 unbannered docs (3 V1-DriftWarning + 5 V2-Deprecated; Rigby overrode 2 of my V2 proposals to V1 to preserve still-useful design intent). After this session, **22 of 24** docs in `docs/architecture/` carry V1/V2 banners.

2. **Provenance Plan B** (#2213) — extended Plan A's `session_provenance` (PR #2205) into a regenerable per-doc index. P1: `build_docs_provenance` management command writes `docs/_provenance.json` (2052 docs, HIGH=1120 / MEDIUM=421 / UNKNOWN=511). P2: `search_docs` PA tool now accepts optional `originating_session: int` filter; pure-function helper extracted; 6/6 unit tests pass. P3: `backfill_doc_provenance` command, cap 25, HIGH-only, existing-frontmatter-only — survey found just 2 eligible candidates (most narrative docs have no frontmatter), both backfilled.

Clean session — no operational fires. Rigby called the stopping point and greenlit three follow-ups for next session (P3.5 broader backfill rules, dead-path flag, beat-schedule the regen).

---

## What landed — 3 open PRs

### #2211 — `docs/session-1145-architecture-entrypoints`
**`docs(session-1145): rewrite docs/architecture/{INDEX,README}.md as folder-local nav`**

2 files changed, +53/-364.

- `INDEX.md`: V1 banner + removed hardcoded "Total Documents: 22". File list annotated with "superseded" markers reflecting existing `DOC-POINTER-V2 (Session 1143)` banners.
- `README.md`: V1 banner removing platform-wide claims. Reframed from "master architecture document" → "this folder is part of the docs corpus; it is not the platform's source of truth." Added Start-here pointer table (PLATFORM_INVENTORY, PLATFORM_WHAT_IT_IS, canon/INDEX, topics/, DOC_LIFECYCLE, docs/INDEX). Removed old pattern catalogues, decision logs, Session 84 file-path inventory (paths like `agents/video_agent.py` no longer match the monorepo), DaVinci-as-current references (sunset Session 1143).

### #2212 — `docs/session-1145-architecture-banner-sweep`
**`docs(session-1145): banner sweep — 3 V1 drift + 5 V2 deprecated across docs/architecture/`**

8 files changed, +53/-0 (pure banner additions).

**V1 Drift Warning (3):**
- `PROMPTING_SYSTEM.md` (Session 238) — orchestrator + function-calling concept current; counts (`21 spider sources`, `149 agents`, `80+ styles`) and `GPT-5.1` model version stale. Already carried an inline historical note for `/api/pa/chat/`.
- `WORKFLOW_ORCHESTRATION_AGENT.md` (Session 191) — wrap-model-in-workflow pattern remains central; listed workflows (image-gen specific) and `13 tools` count are stale. **Rigby override from V2:** V2 reads like "do not read"; V1 keeps the pattern visible.
- `ml_architecture.md` (Jan 2026) — aspirational M3/MLX/scikit-learn stack marked "not implemented as specified, preserved as exploration context." **Rigby override from V2:** same rationale.

**V2-Deprecated (5):**
- `MEMORY_SYSTEM_ARCHITECTURE.md` (Session 178) — pgvector unblocked Session 1140, Document table has 852/14149 chunks, search_docs PA tool live, frontend moved off ai_image_studio.html.
- `PERFECT_WORKFLOW_DESIGN.md` (Nov 2025) — image-gen workflow design doc; current pipeline lives in topics/content-pipeline.md.
- `learning_system.md` (Sep 2025) — pre-Session-1115 LearningBridge ABC migration; reality-score framing retired Session 1143.
- `partnership_model.md` (Sep 2025) — pre-24/7 Global AI brand lock; product vision, not architecture.
- `sports_betting_integration.md` (Sep 2025) — bridge file still exists at `core/learning_bridges/sports_betting_bridge.py`, but surrounding architecture refactored Session 1115.

**Wording convention** (Rigby spec): V1 = `Last reviewed for drift labeling: Session 1145` (we verified the *label*, not content-vs-code). V2 = `Deprecated: Session 1145`. Both reference `DOC_LIFECYCLE.md` §2c.

### #2213 — `docs/session-1145-provenance-plan-b`
**`feat(session-1145-provenance): docs/_provenance.json + search_docs filter + selective backfill (Plan B)`**

8 files changed, +32711/-4 (~32K = the JSON index itself; code ~600 lines).

**P1 — `build_docs_provenance` management command** writes `docs/_provenance.json`. Per-doc schema: `originating_session`, `confidence` (HIGH/MEDIUM/LOW/UNKNOWN), `match_source`, `first_commit_{sha,date,subject}`, `sessions_touched[]`, `commit_count`, `prs[]`. Confidence ladder:
- HIGH = first session-attribution came from a subject-tagged commit
- MEDIUM = first attribution from commit body only
- LOW = frontmatter-only override (no commit reference)
- UNKNOWN = no session reference anywhere

Origin rule: `min(sessions_touched)` — earliest session that touched the doc, not the highest-confidence later attribution. Excludes `docs/archive/` + `docs/docs-pattern/` per §0.

Implementation gotcha worth remembering: combining `git log --name-only` with `--pretty=format:` interleaves files INTO the format output between commits, breaking a single-pass parser. Resolved with two passes (metadata via ASCII US/RS delimiters, file list via separate `--name-only` call merged by SHA).

Current repo output: 2052 docs indexed (HIGH=1120, MEDIUM=421, LOW=0, UNKNOWN=511) from 6571 commits.

**P2 — `originating_session` filter on `search_docs`** added optional integer param. Handler loads provenance once per process via `lru_cache(1)`; overshoots `k` by 4x when filter active; response carries `filter: {originating_session, pre_filter_count, excluded_mismatch, excluded_missing_provenance}`. Missing-provenance = excluded. Non-breaking when omitted.

Pure-function helper `_filter_chunks_by_originating_session(chunks, session, docs)` extracted for testability. 6/6 unit tests pass (0.06s), no Django/auth/dispatcher mocking required.

**P3 — `backfill_doc_provenance` command** adds `originating_session: N` to YAML frontmatter. Rules per Rigby spec: HIGH-only, cap 25, existing-frontmatter-only (no NEW blocks), skip already-tagged, sort by session DESC.

Survey for current repo: only **2 eligible candidates** (most HIGH docs are narrative markdown without any frontmatter). Both applied:
- `docs/specs/FLEET_MOVE_1_AND_2_SPEC.md` → `originating_session: 1128`
- `docs/handoffs/SESSION_1056_COST_THROTTLE_AND_PA_LOOP_FIX.md` → `originating_session: 1056`

Full survey: 2 eligible / 932 not-HIGH / 767 no-frontmatter / 24 already-tagged / 326 missing-file (paths git history records but no longer on disk).

---

## How to regenerate

```bash
python manage.py build_docs_provenance
python manage.py backfill_doc_provenance --dry-run
python manage.py backfill_doc_provenance              # apply
```

After workers restart (`pkill -9 -f celery; rm -f .celery*.pid; make celery`), the `originating_session` filter is live on `search_docs`.

---

## Rigby decisions during session

All scope calls explicitly handed to Rigby (conversation `pa-4b4784ecd989`); she drove:

1. **PR shape for architecture sweep:** 2 PRs (entry-point rewrite separated from banner mechanics) instead of 1 combined.
2. **Banner classification rubric:** V1 for "pattern still valid, drift on counts/names"; V2 for "architecture replaced, preserved as history."
3. **Two V1 overrides from V2:** WORKFLOW_ORCHESTRATION_AGENT + ml_architecture — "V2 reads like don't-read; keep them visible with explicit drift label."
4. **Wording convention:** V1 = "Last reviewed for drift labeling"; V2 = "Deprecated."
5. **Plan B sub-task order:** P1 → P2 → P3 (don't try to "session-tag the world"; precision over recall on backfill).
6. **P3 cap:** 25, "unless purely mechanical."

---

## Three follow-ups Rigby greenlit for next session

(All deferred to Session 1146 — not in this session's PRs.)

1. **P3.5: broader backfill rules.** Add NEW frontmatter blocks (not just update existing) for HIGH-confidence docs in `docs/handoffs/**`, `docs/specs/**`, and optionally `docs/canon/**`. Cap 50 files per PR. Minimal frontmatter: `originating_session`, `provenance_confidence`, optional `provenance_note: "auto-added by backfill_doc_provenance"`. No content edits beyond block insertion.
2. **`exists_on_disk: false` flag for dead paths.** 326 entries in `_provenance.json` point at files git history records but no longer exist. Don't delete (preserves history); mark explicitly and exclude from default consumers unless requested.
3. **Beat-schedule the regen.** Weekly Celery beat task to rebuild `_provenance.json`. No LLM, no DB, ~10s. Log single-line summary (total/HIGH/MEDIUM/UNKNOWN/dead).

---

## Operational notes

None — clean session, no fires. No password resets, no sysctl tunes, no service restarts required during the session itself. The provenance regen + backfill ran under 5s each.

The lru_cache(1) on `_load_provenance_docs()` means daphne + celery workers need to be restarted after `_provenance.json` is regenerated for the cached value to refresh (per the memory rule about `make celery` + stale pid files: `pkill -9 -f celery; rm -f .celery*.pid; make celery`).

---

## ADDENDUM — merge order recommendation

Per Rigby: no ordering constraints; if Chris wants "max value first," merge **#2213 → #2211 → #2212**.

| PR | Branch | Files | What |
|----|--------|-------|------|
| #2213 | `docs/session-1145-provenance-plan-b` | 8 (+32711/-4) | `_provenance.json` index + `search_docs` filter + backfill command + 6 passing tests |
| #2211 | `docs/session-1145-architecture-entrypoints` | 2 (+53/-364) | `docs/architecture/{INDEX,README}.md` rewrite as folder-local nav |
| #2212 | `docs/session-1145-architecture-banner-sweep` | 8 (+53/-0) | V1/V2 banners on 8 unbannered architecture docs |

---

## Session 1146 — entry points

`00-START-NEXT-SESSION.md` queues:

1. **FIRST:** decide Session 1145 PR queue merge order + flag any revisions before starting new work.
2. **Top priority:** root-level audits sweep (`24_7_GLOBAL_AI_APP_ATLAS.md`, `COST_SURVIVAL_AUDIT.md`, `BEAT_AUDIT.md`, `ML_AUDIT.md`, `PA_TOOL_AUDIT.md`, `RUNTIME_AUDIT.md`, `MANAGEMENT_COMMAND_AUDIT.md`, `AGENT_OUTPUT_TO_UI_MAPPING.md` + others). Highest drift-risk truth surfaces, biggest leverage.
3. **Then:** `docs/apps/` sweep (rigby_standalone_BRIEF, colorado_family_law_concierge_FUTURE_CONCEPT, signal-studio brief).
4. **Then:** Redis pooling sweep (~40 inline `redis.Redis.from_url(...)` sites — mirror OpenAI/Anthropic factory pattern from #2201).
5. **Parallel-ok:** Rigby's 3 greenlit follow-ups (P3.5 + dead-path flag + beat-schedule regen).

Chris-call-only carryovers (parked):
- Decision Command backend cleanup
- DaVinci route removal (`core/views_davinci.py` still routed from `core/urls.py`)
- Mission refresh PR #2190

---

*Handoff written by Claude Code per the context-kit pattern. Rigby-driven scope; Claude executed. Three PRs, all reviewable independently.*
