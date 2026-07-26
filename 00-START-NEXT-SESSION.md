# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2975 CLOSED. Workflow reframe validated for the **seventh walk** (S2969–S2975); **third walk of the Rigby-drafted-spec origination variant** (S2973 + S2974 + S2975). Three code PRs shipped this session: **#3604 (cleanup_stale_no_items + observable stale bucket)**, **#3605 (discord_training Policy A)**, **#3606 (spider_feed stale-sentinel fix, caught by Rigby A2 SIGN grep spot-check)**. Chris handed Deliverable `cb8a622c` (Rigby-drafted spec) asking to continue [NO_ITEMS] discovery + repairs (theodds deferred). I sampled 25 rows/spider across FOUR candidates (discord_training, securityweek, remoteok, techcrunch_startups) via Django ORM BEFORE T1 SIGN — the sampling picked the fix and revealed a **cross-spider system-wide pattern**: 10,738 historical rows with `raw_data={}` + `embedding_text='[NO_ITEMS]'` that dominated the 30d NO_ITEMS rate (89.5%) but had fully self-resolved 2026-07-19. Same pattern S2974 saw in ONE spider (huggingface), now confirmed across 15+ spiders. Non-destructive fix: bump matching rows to a distinct `[NO_ITEMS_STALE_EMPTY_RAW]` sentinel + expose `stale_empty_raw_data_total` bucket + centralize `BACKFILL_SKIP_SENTINELS` helper (Rigby T1 mitigation). PR2 added discord_training to Policy A (statistics-rollup shape, confirmed by sampling). PR3 fixed the spider_feed bug Rigby's A2 grep-check surfaced. Rigby T1 + A2 SIGN both AGREE, no F-BLOCKERs; grep spot-check surfaced 3 real gaps → PR3 same-session. 65/65 tests pass. Post-cleanup: **30d NO_ITEMS rate dropped 86.7% → 9.1%** (77.6-point drop; 10,728 rows flagged system-wide). 24h/7d unaffected. Full context: `docs/handoffs/SESSION_2975_NO_ITEMS_STALE_CLEANUP.md`.

**Session cost this session:** higher than S2974 — ~6 PA dispatches (fetch-spec / T1 / A2 / grep verification), 3 PRs shipped vs 1 planned, no v2 subprocess dispatches, no revision cycles.

**HEAD at close:** `8bd3daf3e` (PRs #3604 + #3605 + #3606 merged; docs cascade PR TBD). Workers recycled after merges per PLAYBOOK-7.4.4.

---

## S2976 first-action — WAIT FOR CHRIS (same as S2969–S2975)

The reframe held for the **seventh time**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2975_NO_ITEMS_STALE_CLEANUP.md` in full — especially §"Root cause narrative", §"Ground-truth numbers", §"Live-verify results", §"SIGN cycle log" (Rigby A2 grep spot-check is the interesting fold).
4. **Optionally probe the shipped state:**
   - From Django shell: `LegacySpiderData.objects.filter(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]').count()` — should be ~10,728.
   - Or: `get_spider_semantic_search().get_embedding_stats(include_breakdown=True, breakdown_window_hours=720)['no_items_breakdown']['no_items_rate']` — should be ~9.1% (was 86.7%).
   - Or: `python manage.py cleanup_stale_no_items` (dry-run) — should report 0 remaining candidates.
5. **Report readiness in one short message and wait.** Something like: "Oriented. S2975 closed — reframe validated for the seventh walk. Stale cleanup shipped; 10,728 ghost rows flagged; 30d NO_ITEMS rate 9.1% (was 86.7%). Ready when you have a spec pointer."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:** follow the S2969–S2975 pattern — read spec, targeted "existing implementation analysis" (Cycle 1A verify-before-build), **for diagnostic-shape arcs, complete the ORM sampling BEFORE T1 SIGN** (S2974 fold #11 corroborated at S2975), **for cross-spider audits, sample MULTIPLE spiders with intent to find shared patterns** (S2975 new fold), T1 SIGN to Rigby with zoom-out ask, fold, implement, A2 SIGN with grep spot-check for predicate drift when new sentinels/predicates are introduced (S2975 new fold), merge with `--admin`, `make celery-recycle`, live-verify in-shell (Django `Client().force_login` for auth-gated routes; **`HTTP_HOST='localhost'` required or DisallowedHost fires**), Rigby verifies from her tool surface, report three-part summary to Chris.

---

## S2976 high-value seeds (Chris picks whether to open)

**remoteok pre-dedup filter (NEW from S2975 sampling).** Root cause identified: `ai_core/spiders/remoteok_spider.py` saves the remoteok API's legal preamble (`type: "item", legal: "API Terms of Service..."`) as the only "unique" item because its `last_updated` field mutates every fetch and beats dedup while real jobs get deduped (30 fetched, 29 duplicated, 1 preamble). Fix: pre-dedup filter to skip items with `type == "item"` AND `legal` field present. Small surface, needs tests + `retriage_no_items --spider remoteok --apply` post-merge.

**huggingface `all_deduped` write suppression (STILL OPEN from S2974 + S2975).** Spider writes an audit row every 30 min for "all items were duplicates". Post-S2975 cleanup, this is one of the top-5 non-deferred producers. Options: drop to a separate run-log table, or suppress writes on `diagnostic.status='success_empty'`. Small (~1-2 files) but touches spider write path — needs testing.

**theodds auth-failure fix (STILL OPEN from S2972+S2973+S2974).** Top NO_ITEMS producer at ~294 rows / 30d, unchanged. Fix requires Chris to rotate `THE_ODDS_API_KEY` (or verify API quota). Post-fix: re-run breakdown to validate re-rank.

**Shape sampling for remaining top-10 producers post-cleanup.** After S2975, top non-deferred are `behance` / `udemy` / `coursera` / `freecodecamp` (all at 11 rows/30d). Sample ~10 rows each, classify per S2973+S2974 rubric. May yield another extractor-hardening win.

**Deliverable-as-spec fold @ trigger 7 — Playbook rule candidate READY TO PROPOSE.** Pattern has walked 7 times (S2969–S2975) across 3 variants. Chris directive at S2974 close said "propose at S2975 close if the pattern holds one more walk" — it did. Substrate ready: existing envelope pattern from prior Playbook amendments applies. Chris ratifies whether to open a Playbook amendment arc.

---

## S2971 candidate follow-ups (Chris picks whether to open, unchanged)

**Rail shortcut for /signals** (~5 min). Legacy alias `signals: { primary: 'intelligence', sub: 'signals' }` already wired in `WorkspacePageNew.tsx`. Only need a `<NavLink to="/workspace?tab=signals">` entry in `frontend/src/components/layout/Sidebar.tsx:55` for one-click discoverability.

**Per-view window selector.** Current build shares one window across Dashboard/Feed/Clusters. Iterate only if Chris asks.

**URL persistence for filter state (spec §8 nice-to-have).** Feed + Cluster filter state currently in component state; deep-linking requires plumbing every filter to `useSearchParams`.

**"Create Initiative from Cluster" button (spec §8 nice-to-have).** Wires cluster detail drawer to `work_tool.initiative_create` via PA.

**Migrate Feed Explorer to `persistence.SpiderData`.** Extended fields (`relevance_score`/`opportunity_score`/etc.) absent from `LegacySpiderData`.

---

## S2970 candidate follow-ups still open (unchanged)

**sports_injuries keyword tuning (small mini-PR).** Adding 2-3 conservative keywords (`cleared for`, `activated`) would push NFL/MLB yield from 1-3 → 3-5 items each.

**S2969 candidate arc STILL OPEN:** worker egress validation. S2970 PR-B.1 root-caused the DNS piece (aiohttp/aiodns bug). Broader worker-egress questions remain uninvestigated.

---

## S2968 PR-B branch decision — STILL OPEN

_(unchanged — no session has touched the S2968 PR-B branch since S2971)_

Branch `feat/s2968-pr-b-deliverable-as-spec` remains pushed to origin, no PR opened. Chris now has SIX data points on how the reframe works (S2969–S2974) — the manual UUID-paste flow works cleanly, no exempt-list / schema plumbing strictly required. Options A/C from S2968 close still apply.

---

## Candidate folds surfaced through S2974 (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger unless otherwise noted:**

1. **Soft-key-vs-LLM-schema-gate.** **Trigger count: 1** (S2968).
2. **"Duplicate of a thing we already have" pattern.** **Trigger count: 2** (S2968).
3. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969).
4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 7** (S2969–S2975). **Seven-trigger corpus. Playbook rule PROPOSAL READY at S2976 open per Chris directive.** Three variants now: Chris-paste (S2969–S2972) + Rigby-drafted-per-Chris-ratification (S2973 + S2974 + S2975). All walk the same 10-step shape.
5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** **Trigger count: 4** (S2970, S2972, S2974, S2975). Reinforced.
6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** **Trigger count: 1** (S2970).
7. **"Route-placement is a settable expectation, not a spec constraint."** **Trigger count: 1** (S2971).
8. **"Rigby web_fetch_tool can't authenticate against Django session-cookie endpoints."** **Trigger count: 2** (S2971, S2972). Watch for third — could become Rigby Tool Gap Ledger entry.
9. **"Rigby-drafted spec deliverable is a first-class origination path."** **Trigger count: 3** (S2973, S2974, S2975). Could formalize as variant of fold #4.
10. **"Sampling extrapolation past ~10k rows produces cross-session drift."** **Trigger count: 1** (S2972).
11. **"Sample-before-plan cuts T1 revision cycles to zero."** **Trigger count: 2** (S2974, S2975). For diagnostic-shape arcs, complete ORM sampling BEFORE drafting T1 — evidence-grounded T1 earns Rigby AGREE on first turn, no revision loop. **Corroborated. Ready for Playbook rule proposal when Chris directs.**
12. **"Retriage-command-as-primitive over blanket ORM update"** **Trigger count: 2** (S2974 `retriage_no_items`, S2975 `cleanup_stale_no_items`). Same pattern: dry-run default, scoped spider/date filter, non-destructive reversible update, prints candidates before apply. Corroborated across two independent primitives. **Playbook rule candidate.**
13. **NEW: "Cross-spider sampling reveals system-wide fix leverage."** **Trigger count: 1** (S2975). Sampling MULTIPLE spiders with the intent to find shared patterns produced a 89.5% system-wide fix vs S2974's single-spider 5%. When multiple candidates share a shape/date/error signature, extend sampling to identify the class. Watch for second.
14. **NEW: "Rigby A2 SIGN grep spot-check catches predicate-drift bugs same-session."** **Trigger count: 1** (S2975 PR3). A2 zoom-out "grep for missed predicate sites" caught 3 real `spider_feed.py` gaps that would have shipped latent. Ship the fix same-session, not deferred. Watch for corroboration in future SIGN cycles introducing new sentinels/predicates.

---

## Universal open sequence (unchanged)

1. `context-kit orient` — source-of-truth chain, latest handoff
2. Absorb `MEMORY.md` + `CLAUDE.md` (both auto-injected)
3. Read this `00-START-NEXT-SESSION.md` in full
4. **Session-open atomic mint check:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2976 pin minted at S2975 close cascade. If not fresh, run `python manage.py session_lifecycle close --label s2975-no-items-stale-cleanup --allow-no-mirror` first (per `feedback_session_open_atomic_mint_before_pa_dispatch`).
5. Verify `claude` CLI availability (if v2 dispatches are on the day's plan): `which claude && claude --version` (should show 2.1.114+ at `~/.local/bin/claude`)
6. Read `docs/handoffs/SESSION_2975_NO_ITEMS_STALE_CLEANUP.md` — full context on this session's shipped code + reframe walk 7
7. **Wait for Chris to hand you a spec pointer via Rigby.** Do not proactively propose work.

---

## What's forbidden at S2976 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward.

- **Do not automatically merge S2968 PR-B** — its dispatch wiring is architecturally stale under the reframe.
- **Do not proactively dispatch v2 test runs at session open** — each burns ~$0.15-0.20.
- **Do not chase spider parsing bugs for reddit / sports_injuries** — S2969/S2970 verified code path works.
- **Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env** — aiodns 3.5.0 is broken here; the flag default is `true` intentionally.
- **Do NOT expand the Policy A exclusion list (`core/services/no_items_policy.py`) without shape-sampling target rows first** — false exclusions HIDE real data-quality bugs. Sample before adding.
- **S2974: Do NOT clear `[NO_ITEMS]` sentinels via blanket ORM update.** Always route through `retriage_no_items --spider <name>` which recomputes `get_searchable_text` per row and clears only where non-empty. Blanket clears cause backfill thrash (rows re-mark themselves).
- **NEW at S2975: Do NOT introduce a new sentinel or predicate on `embedding_text` without extending `BACKFILL_SKIP_SENTINELS` in `core/services/no_items_policy.py` AND grep-checking all call sites.** Missed sites are silent bugs (see PR3 — `spider_feed.py` had 3 latent gaps caught only by Rigby A2 SIGN grep spot-check).

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2975 additions:**
- remoteok pre-dedup filter (spider-side; ~1-2 files; identified via S2975 sampling)
- Post-cleanup shape sampling for remaining top producers (behance / udemy / coursera / freecodecamp — all at 11/30d)
- Deliverable-as-spec Playbook rule proposal (fold #4 at trigger 7 per Chris S2974-close directive)

**S2974 additions:**
- huggingface `all_deduped` write suppression (STILL open — one of top-5 non-deferred post-cleanup)
- Shape sampling for `securityweek` / `udemy` / `colorado_family_law` / `freecodecamp` / `techcrunch_startups` / `education_rss` (S2975 sampled 3 of these — see handoff for what's already classified)

**S2971 additions:**
- Rail shortcut for /signals (~5 min)
- Per-view window selector (v1 shipped shared; iterate only if Chris asks)
- URL persistence for filter state (spec §8 nice-to-have)
- "Create Initiative from Cluster" button (spec §8 nice-to-have)
- persistence.SpiderData migration (extended scoring fields; separate arc)

**S2970 additions:**
- sports_injuries keyword tuning (~10 min if Chris insists on ≥10)
- Worker egress validation arc (broader, DNS piece fixed S2970)

**S2969 additions (unchanged):**
- Retention task Beat schedule — `cleanup_empty_spider_runs` un-scheduled per Rigby T1.

**S2968 additions (unchanged):**
- PR-C (Deliverable status write-back), PR-D (v2 default flip + v1 deletion), Path A (nightly beat + drift dashboard), Path B (per-slice named predicate graduation), Path C (Ledger #20 + #21 fix arc).

**Long-standing (carry forward):** Docs restructuring arc, Slice 5-hardening executable invariants, Tier 2 lint promotion, Advanced paste-UUID fallback for cluster picker, Server-side search + pagination on `/eligible/`, Z1/Z2/Z4 signal-dispatch UI polish, Rank + cap + paginate follow-ups, Per-pattern-type diversity floors, Ledger candidates backlog, W2 #1 / #2b / #2c pending Chris re-slate, LLMCallLog field splits, Bulk `workspace_budget_tool` operations, C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** S2971–S2974 were net-new engineering (Signal Intelligence UI + intake-quality arc), not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2975)

See:
- **S2975 handoff (current):** `docs/handoffs/SESSION_2975_NO_ITEMS_STALE_CLEANUP.md`
- **S2975 shipped code:** PR #3604 (`cleanup_stale_no_items + stale bucket`), PR #3605 (`discord_training Policy A`), PR #3606 (`spider_feed stale-sentinel fix`)
- **S2975 spec deliverable:** `cb8a622c-ca94-4b96-b044-c5d7417955a8` (Rigby-drafted)
- **S2975 support conversation:** `pa-f545685143384188`
- **S2974 handoff:** `docs/handoffs/SESSION_2974_LEGISLATION_EXTRACTOR.md`
- **S2974 shipped code:** PR #3602 (`feat(s2974): legislation extractor hardening — wrapped-item shape + retriage`)
- **S2974 spec deliverable:** `914b1118-4eed-4abf-8c84-86ff42a459c3` (Rigby-drafted)
- **S2974 support conversation:** `pa-3377eb5f247a` (shared with S2972+S2973)
- **S2972+S2973 handoff:** `docs/handoffs/SESSION_2972_2973_STATS_ALIGNMENT_AND_NO_ITEMS.md`
- **S2971 handoff:** `docs/handoffs/SESSION_2971_SIGNAL_INTELLIGENCE_UI.md`
- **S2970 handoff:** `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md`
- **S2969 handoff:** `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`
- **S2968 handoff:** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
