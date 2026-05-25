---
originating_session: 1147
provenance_confidence: HIGH
provenance_note: hand-authored Session 1147 handoff
---

# Session 1147 — P3.5 backfill + apps & topics sweeps (3 PRs)

**Date:** 2026-05-25 (afternoon — third back-to-back with Sessions 1145+1146)
**Branch state at session close:** 3 PRs open, all pushed, all reviewable independently. No hard merge ordering constraints.

---

## TL;DR

Session opened with all 4 Session 1146 PRs merged and Chris asking to continue with "/docs/ cleanup." Rigby specced a 3-step plan: regen `_provenance.json` first → P3.5 → apps → topics. All three steps shipped clean.

1. **P3.5 frontmatter backfill** (PR #2219) — extended `backfill_doc_provenance` with `--add-frontmatter` + `--paths-include` + `--with-confidence` + `--with-note` flags. Applied to 50 newest handoffs in `docs/handoffs/`, `docs/specs/`, `docs/canon/`. Also added a filename-override upstream in `build_docs_provenance` so the index agrees with handoff filenames (catches cases like `SESSION_998_*.md` being git-attributed to Session 997 because the file was committed as part of Session 997's wrap-up). 53 files changed, HIGH count jumped from 1122 → 1274.

2. **docs/apps/ frontmatter alignment** (PR #2220) — Rigby specced "light touch" after recon turned up that all 9 BRIEF/CONCEPT docs were already well-curated (rev. 3 against products.ts as their canon, Rigby content-flag review applied, companion-docs cross-refs in frontmatter). Just renamed `session: ####` → `originating_session: ####` across all 9, plus changed colorado's `status: future-concept` → `status: parked_future_concept`. No V1/V2 banners added (would duplicate existing frontmatter signal). 9 files, +10/-10.

3. **docs/topics/ pragmatic banner sweep** (PR #2221) — Recon turned up 19 topic docs (7 already bannered, 12 not). Rigby specced pragmatic option (b): banner only the 5 highest-traffic recent unbannered docs (`README.md`, `obs-remote-control.md`, `multi-repo-management.md`, `fleet-doc-verifier-rollout.md`, `content-pipeline.md`). Defer the 7 older Feb-March docs to a future recon-first sweep. Added a new "Where current truth lives" paragraph to topics/README pointing at PLATFORM_INVENTORY + the 8 autogen audits + docs/INDEX as the §2c routing map. 5 files, +35/-4.

Clean session — no operational fires. Three independent sweeps, three independent PRs, three small enough for fast review.

---

## What landed — 3 open PRs

### #2219 — `docs/session-1147-provenance-backfill-p35`
**`feat(session-1147-provenance): P3.5 frontmatter backfill (50 handoffs) + filename override in build_docs_provenance`**

53 files changed, +1416/-747. Breakdown: 50 handoff `.md` files (+6 lines each = FM block + trailing blank), `docs/_provenance.json` (regenerated), 2 management command files (extended + simplified).

**P3.5 invocation:**

```bash
python manage.py backfill_doc_provenance \
    --add-frontmatter \
    --paths-include docs/handoffs/,docs/specs/,docs/canon/ \
    --limit 50 \
    --with-confidence \
    --with-note "auto-added by backfill_doc_provenance"
```

Each backfilled doc gets a minimal 3-line YAML block:

```yaml
---
originating_session: NNNN
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---
```

**Filename override in `build_docs_provenance`** (Session 1147 coherence fix): `docs/handoffs/SESSION_NNNN_*.md` filenames are unambiguous; they now win over git's first-commit attribution. Catches cases like:

- `SESSION_998_GOVERNANCE_HARDENING.md` — git said 997, filename says 998 → now 998 HIGH `filename`
- `SESSION_1024_SEMANTIC_SPIDER_SEARCH.md` — git said 1023 → now 1024 HIGH `filename`
- `SESSION_1146_ROOT_AUDITS_SWEEP.md` — git said 1145 MEDIUM body → now 1146 HIGH `filename`

223 handoff entries now use `match_source: filename`. Index counts shifted:

| Confidence | Before | After |
|------------|--------|-------|
| HIGH | 1122 | **1274** (+152) |
| MEDIUM | 422 | **292** (-130) |
| UNKNOWN | 511 | **489** (-22) |

This is critical for `search_docs(originating_session=N)` — without the upstream fix, querying for Session 998 wouldn't find SESSION_998_GOVERNANCE_HARDENING.md because the index said 997.

**548 more handoffs remain eligible** for backfill (cap 50/PR per Rigby). Next P3.5 round will pick the next 50 newest.

### #2220 — `docs/session-1147-apps-frontmatter-align`
**`docs(session-1147-apps): align frontmatter — session → originating_session + park colorado_family_law`**

9 files changed, +10/-10. Pure frontmatter key rename.

Per Rigby's "light touch" spec: `docs/apps/` BRIEFs were already well-curated (Session 1135 discovery + rev. 3 corrections against products.ts + Rigby content-flag review). V1/V2 banners would be noise — frontmatter already communicates source/companion docs.

| File | Change |
|------|--------|
| `rigby_standalone_BRIEF.md` + 7 sibling BRIEFs | `session:` → `originating_session:` |
| `colorado_family_law_concierge_FUTURE_CONCEPT.md` | `session:` → `originating_session:` **+** `status: future-concept (...)` → `status: parked_future_concept (...)` |

**NOT changed (per Rigby):** `source_of_truth: products.ts` left as-is (correct canon for GTM docs — NOT PLATFORM_INVENTORY which is runtime canon). No V1/V2 banners. No `provenance_confidence` line (these are drafts, not subject-tagged HIGH commits).

### #2221 — `docs/session-1147-topics-pragmatic-banner-sweep`
**`docs(session-1147-topics): pragmatic V1 banner sweep — 5 high-traffic topic docs + README current-truth pointer`**

5 files changed, +35/-4.

| File | Treatment |
|------|-----------|
| `docs/topics/README.md` | V1 banner + new "Where current truth lives" paragraph + 3 hardcoded count cells in file table replaced with "(count: see PLATFORM_INVENTORY)" |
| `docs/topics/obs-remote-control.md` | V1 banner (newest topic doc, May 25) |
| `docs/topics/multi-repo-management.md` | V1 banner + pointer to `config/external_repos/` |
| `docs/topics/fleet-doc-verifier-rollout.md` | V1 banner flagging "7 PRs / 1 merged" as Session-1120 snapshot |
| `docs/topics/content-pipeline.md` | V1 banner + pointer to `topics/agent-system.md` |

**Deferred to future sweep:** 7 older topic docs (Feb-March mtimes) + the 7 already-bannered topic docs (counts-hygiene refresh on those is a separate ticket).

---

## Rigby decisions during session

All scope calls explicitly handed to Rigby (conversation `pa-4b4784ecd989`):

1. **Order:** B → A → D from her earlier Session 1147 opening message — P3.5 first (mechanical, unblocks search_docs filtering), then apps/ (small scoped), then topics/ (high-leverage subsystem docs).
2. **Step 0:** Regenerate `_provenance.json` BEFORE running P3.5 so the backfill has freshest HIGH-confidence attributions including Sessions 1145/1146 merges.
3. **Filename override scope:** When I caught off-by-one cases mid-dry-run (SESSION_998 → 997), moved the override upstream into `build_docs_provenance` instead of just patching the backfill command — keeps the index coherent for the search_docs filter too.
4. **apps/ light touch (b):** "A V1 banner adds noise and duplicates what the frontmatter already communicates (source_of_truth + companion docs). We'll reserve banners for drift-prone architecture/ops docs."
5. **topics/ pragmatic (b):** "docs/topics/ is exactly where drift silently corrupts agent/operator understanding, and the recent unbannered docs are likely being read. We can get 80% of the value with ~1 hour and keep PR scope reviewable."
6. **Session stopping point:** After the 3-PR sweep; six other follow-ups (P3.5 round 2 with 548 more handoffs, exists_on_disk flag, beat-schedule regens, fix `build_learning_bridge_audit`, Redis pooling, older topics + 7 already-bannered topic-docs refresh) deserve fresh session boundary.

---

## Carryover follow-ups for Session 1148+

(All independent; can ship in any order.)

1. **P3.5 round 2** — 548 more handoffs eligible (cap 50/PR per Rigby). Run again to backfill next 50 newest.
2. **`exists_on_disk: false` flag** (carried since Session 1145) — for 326 dead paths in `_provenance.json`.
3. **Beat-schedule the regens** (carried since Session 1145) — weekly Celery beat task for `_provenance.json` + the 8 `build_*_audit` commands. ~50s total, no LLM/DB.
4. **Fix `build_learning_bridge_audit.py` generator** (carried since Session 1146) — falsely flags "ABC unused" even though Session 1115 closed it.
5. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory treatment from PR #2201.
6. **Older `docs/topics/` sweep** — recon-first pass on the 7 Feb-March docs deferred from #2221 (body-systems, collaboration-protocol, local-askdocs, spider-network, stock-intelligence, tool-consolidation, video-upload).
7. **Counts-hygiene refresh on the 7 already-bannered topic docs** — agent-system has 8 hardcoded count hits, personal-assistant has 4, infrastructure + active-module-ownership-map have 2 each. Not blocking but worth a sweep.
8. **`docs/governance/SYSTEM_OWNER.md` staleness check** — passes §2c already, but mtime check is overdue.
9. **`docs/reports/` + `docs/patents/` recon** — large piles, recon-first.

---

## Operational notes

None — clean session, no fires. All commands ran cleanly.

The lru_cache(1) on `_load_provenance_docs()` in `td_handlers_ops.py` means daphne + celery workers need to be restarted after `_provenance.json` is regenerated for the cached value to refresh (per the `make celery` + stale pid files gotcha):

```bash
pkill -9 -f celery; rm -f .celery*.pid; make celery
```

After PR #2219 merges, that's the right time to do the restart.

---

## ADDENDUM — merge order recommendation

No hard ordering constraints. All 3 PRs independent. If Chris wants max value first: **#2219 → #2221 → #2220** (provenance infra > topics-doc clarity > apps frontmatter polish).

| PR | Branch | Files | What |
|----|--------|-------|------|
| #2219 | `docs/session-1147-provenance-backfill-p35` | 53 (+1416/-747) | P3.5 frontmatter backfill + filename override upstream |
| #2220 | `docs/session-1147-apps-frontmatter-align` | 9 (+10/-10) | apps frontmatter rename |
| #2221 | `docs/session-1147-topics-pragmatic-banner-sweep` | 5 (+35/-4) | topics V1 banners on 5 high-traffic files + README current-truth paragraph |

---

## Session 1148 — entry points

`00-START-NEXT-SESSION.md` will queue:

1. **FIRST:** decide Session 1147 PR queue merge order + flag any revisions before starting new work.
2. **Top priority:** continue docs cleanup — P3.5 round 2 + older topics sweep + governance staleness check.
3. **Infra carryovers** (parallel-ok): exists_on_disk flag, beat-schedule regens, build_learning_bridge_audit generator fix, Redis pooling sweep.

Chris-call-only carryovers (still parked):
- Decision Command backend cleanup
- DaVinci route removal (`core/views_davinci.py` still routed)
- Mission refresh PR #2190

---

*Handoff written by Claude Code per the context-kit pattern. Third back-to-back session with same arc (Rigby-driven scope decisions, mechanical execution, pragmatic scoping). Three PRs, all reviewable independently.*
