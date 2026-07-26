# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2977 CLOSED. Workflow reframe validated for the **eighth walk** (S2969–S2977); **fourth walk of the Rigby-drafted-spec origination variant** (S2973 + S2974 + S2975 + S2977). One code PR shipped this session: **#3608 (sec_edgar form_type interleave + rebuild_embedding_text command)**. Chris handed Deliverable `4e4534db` (Rigby-drafted spec) asking to verify News/Investing/SEC embedding + searchability + normalize empty sentinels (TheOdds deferred). I sampled sec_edgar + 6 news + 4 investing spiders via Django ORM BEFORE T1 SIGN — the sampling picked the fix. Found News + Investing already healthy (real Feed Explorer hits: yahoo_finance 'stock'=191, financial 'earnings'=52, reuters 'election'=2). Found ONE real extractor mismatch in SEC: raw_data holds 384 8-Ks + 94 10-Qs + 25 10-Ks in 7d, but `LegacySpiderData.get_searchable_text` caps `items[:20]` and 8-Ks (filed ~20× more frequently) dominate the top slice — 10-K/10-Q never make it into `embedding_text`. Chris ratified Path B (fix + one-shot re-extract) via plain-english decision framing. Ship shape: `sec_spider.py` round-robin interleave by form_type + new `rebuild_embedding_text` bounded command that refreshes `embedding_text` for existing rows without touching stored embedding vectors (verified vectors are unused by real search paths). Rigby T1: 3× AGREE + 1 F-BLOCKER (backfill policy — resolved by Chris ratifying Path B). Rigby A2: 3× AGREE + 1 F-BLOCKER (reversibility — assessed as paper-only since rollback is deterministic given raw_data immutability; follow-up seed logged for `--dump-old-jsonl` snapshot flag). 79/79 tests pass. Live-verify: **10-K search 3→13 real hits, 10-Q 1→23 real hits, 8-K unchanged at 54** (no regression). Full context: `docs/handoffs/SESSION_2977_SEC_FORM_TYPE_INTERLEAVE.md`.

**Session cost this session:** ~4 PA dispatches (fetch-spec / T1 SIGN / A2 SIGN / verdict-repeat / deliverable-update), 1 PR shipped (planned via SIGN; no revision cycles), no v2 subprocess dispatches. Rigby tool_runs 18 substantive across T1 + A2.

**HEAD at close:** `8de4c0fac` (PR #3608 merged; docs cascade PR TBD). Workers recycled after merge per PLAYBOOK-7.4.4.

---

## S2978 first-action — WAIT FOR CHRIS (same as S2969–S2977)

The reframe held for the **eighth time**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2977_SEC_FORM_TYPE_INTERLEAVE.md` in full — especially §"Findings from sampling", §"Live-verify", §"SIGN cycle log" (Rigby A2 F-BLOCKER assessed as paper-only is the interesting fold).
4. **Optionally probe the shipped state:**
   - From Django shell: `from core.services.spider_feed import query_spider_feed; [print(q, query_spider_feed(query=q, spider_name='sec_edgar', embedding_status='present', limit=5)['total']) for q in ['10-K', '10-Q', '8-K']]` — should show 13 / 23 / 54.
   - Or: `python manage.py rebuild_embedding_text --spider sec_edgar` (dry-run) — should report `unchanged: 24` (or similar) since the fix already applied to 7d rows.
5. **Report readiness in one short message and wait.** Something like: "Oriented. S2977 closed — reframe validated for the eighth walk. SEC form_type interleave shipped; 10-K search now returns 13 real filings, 10-Q returns 23 (was 3 and 1). Ready when you have a spec pointer."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:** follow the S2969–S2977 pattern — read spec, targeted "existing implementation analysis" (Cycle 1A verify-before-build), **for diagnostic-shape arcs, complete the ORM sampling BEFORE T1 SIGN** (S2974 fold #11 corroborated at S2975 + S2977), **for cross-spider audits, sample MULTIPLE spiders with intent to find shared patterns** (S2975 fold), T1 SIGN to Rigby with zoom-out ask, fold, implement, A2 SIGN with grep spot-check for predicate drift when new sentinels/predicates are introduced (S2975 fold), merge with `--admin`, `make recycle-all`, live-verify in-shell (Django `Client().force_login` for auth-gated routes; **`HTTP_HOST='localhost'` required or DisallowedHost fires**), Rigby verifies from her tool surface, report three-part summary to Chris.

---

## S2978 high-value seeds (Chris picks whether to open)

**sec_spider Form 4 / S-1 / 13F-HR fetch loop expansion (NEW from S2977).** Spider's FILING_TYPES advertises 6 types but fetch loop covers 3. Small (~10 line) mini-PR + tests + retriage post-merge via existing `rebuild_embedding_text --spider sec_edgar --apply`.

**rebuild_embedding_text --dump-old-jsonl (Rigby A2 F-BLOCKER mitigation, NEW from S2977).** Persists old→new pairs as JSONL before writing. Belt-and-suspenders — rollback is already deterministic given raw_data immutability, but a snapshot flag would let operators diff without re-running the command. ~30 min.

**remoteok pre-dedup filter (STILL OPEN from S2975).** Root cause identified: `ai_core/spiders/remoteok_spider.py` saves API legal preamble as only "unique" item because `last_updated` mutates every fetch. Small (~1-2 files) + tests + `retriage_no_items --spider remoteok --apply` post-merge.

**huggingface `all_deduped` write suppression (STILL OPEN from S2974 + S2975).** Spider writes an audit row every 30 min for "all items were duplicates". Top-5 non-deferred producer. Options: drop to run-log table, or suppress writes on `diagnostic.status='success_empty'`.

**theodds auth-failure fix (STILL OPEN from S2972+S2973+S2974+S2975+S2977).** Top NO_ITEMS producer at ~84 rows / 30d (post-S2975 cleanup), unchanged. Requires Chris to rotate `THE_ODDS_API_KEY` (or verify API quota).

**Shape sampling for remaining top-10 producers.** Post-S2975: `behance` / `udemy` / `coursera` / `freecodecamp` (all at 11/30d). Sample ~10 rows each, classify per S2973+S2974+S2977 rubric.

**Deliverable-as-spec fold @ trigger 8 — Playbook rule candidate READY TO PROPOSE.** Pattern has walked 8 times (S2969–S2977) across 4 variants (Chris-paste S2969–S2972, Rigby-drafted S2973+S2974+S2975+S2977). Chris directive at S2974 close said "propose at S2975 close if the pattern holds one more walk" — it did at S2975. Chris said "hold" at S2975 close. Ready when Chris says go.

**Per-item `timestamp=datetime.now()` cleanup in sec_spider (NEW from S2977 Rigby folds).** Hinders dedup auditability. Corroborated across T1 Fold B + A2 Fold D. Separate cleanup arc.

**Extractor-coupling debt (NEW from S2977 Rigby T1 Fold A).** items[:20] cap is a global assumption; if a second spider hits the same dominant-subtype-crowds-out-minority issue, promote to generic extractor-side solution. Future trigger — do NOT open unless trigger fires.

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

Branch `feat/s2968-pr-b-deliverable-as-spec` remains pushed to origin, no PR opened. Chris now has EIGHT data points on how the reframe works (S2969–S2977) — the manual UUID-paste flow works cleanly, no exempt-list / schema plumbing strictly required. Options A/C from S2968 close still apply.

---

## Candidate folds surfaced through S2977 (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger unless otherwise noted:**

1. **Soft-key-vs-LLM-schema-gate.** **Trigger count: 1** (S2968).
2. **"Duplicate of a thing we already have" pattern.** **Trigger count: 2** (S2968).
3. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969).
4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 8** (S2969–S2977). **Eight-trigger corpus.** Playbook rule PROPOSAL READY at any time Chris directs. Four variants now: Chris-paste (S2969–S2972) + Rigby-drafted-per-Chris-ratification (S2973 + S2974 + S2975 + S2977). All walk the same 10-step shape.
5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** **Trigger count: 5** (S2970, S2972, S2974, S2975, S2977). Reinforced.
6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** **Trigger count: 1** (S2970).
7. **"Route-placement is a settable expectation, not a spec constraint."** **Trigger count: 1** (S2971).
8. **"Rigby web_fetch_tool can't authenticate against Django session-cookie endpoints."** **Trigger count: 3** (S2971, S2972, S2977 — Rigby's A2 verdict text got truncated over pa_chat display; not the same class but log for Rigby Tool Gap Ledger). Watch.
9. **"Rigby-drafted spec deliverable is a first-class origination path."** **Trigger count: 4** (S2973, S2974, S2975, S2977). Now a stable variant of fold #4.
10. **"Sampling extrapolation past ~10k rows produces cross-session drift."** **Trigger count: 1** (S2972).
11. **"Sample-before-plan cuts T1 revision cycles to zero."** **Trigger count: 3** (S2974, S2975, S2977). Ready for Playbook rule proposal when Chris directs. S2977: sampling 11 spiders picked the fix + ruled out 10 phantom bugs before any code.
12. **"Retriage-command-as-primitive over blanket ORM update"** **Trigger count: 3** (S2974 `retriage_no_items`, S2975 `cleanup_stale_no_items`, S2977 `rebuild_embedding_text`). **Now three independent primitives** following the same pattern: dry-run default, scoped spider/date filter, non-destructive reversible update, prints candidates/diff before apply. **Playbook rule candidate READY.**
13. **"Cross-spider sampling reveals system-wide fix leverage."** **Trigger count: 2** (S2975 stale cleanup, S2977 sec_edgar audit — 11 spiders sampled with intent to find shared patterns; found News/Investing were fine, isolated the SEC-specific bug). **Corroborated. Ready for Playbook rule candidate.**
14. **"Rigby A2 SIGN grep spot-check catches predicate-drift bugs same-session."** **Trigger count: 2** (S2975 PR3 → spider_feed gaps; S2977 A2 verified 13 embedding_text__icontains consumers, confirmed no regression). **Corroborated.**
15. **NEW: "Rigby A2 F-BLOCKER can be paper-only if rollback path is deterministic from immutable inputs."** **Trigger count: 1** (S2977 — reversibility F-BLOCKER assessed as paper-only because raw_data is immutable and reverting extractor code + re-running command reproduces old text). Log as fold; watch for second — if pattern repeats, add explicit "F-BLOCKER-adjacent" designation to SIGN vocabulary.
16. **NEW: "Vectors decoupled from text — extractor updates need not touch persisted embeddings."** **Trigger count: 1** (S2977 — verified stored vectors are unused by real search paths; Feed Explorer hits `embedding_text__icontains`, semantic_search regenerates on-the-fly). Watch for second — could unlock cheap text-only refresh commands as a class.

---

## Universal open sequence (unchanged)

1. `context-kit orient` — source-of-truth chain, latest handoff
2. Absorb `MEMORY.md` + `CLAUDE.md` (both auto-injected)
3. Read this `00-START-NEXT-SESSION.md` in full
4. **Session-open atomic mint check:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2978 pin minted at S2977 close cascade. If not fresh, run `python manage.py session_lifecycle close --label s2977-sec-form-type-interleave --allow-no-mirror` first (per `feedback_session_open_atomic_mint_before_pa_dispatch`).
5. Verify `claude` CLI availability (if v2 dispatches are on the day's plan): `which claude && claude --version` (should show 2.1.114+ at `~/.local/bin/claude`)
6. Read `docs/handoffs/SESSION_2977_SEC_FORM_TYPE_INTERLEAVE.md` — full context on this session's shipped code + reframe walk 8
7. **Wait for Chris to hand you a spec pointer via Rigby.** Do not proactively propose work.

---

## What's forbidden at S2978 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward.

- **Do not automatically merge S2968 PR-B** — its dispatch wiring is architecturally stale under the reframe.
- **Do not proactively dispatch v2 test runs at session open** — each burns ~$0.15-0.20.
- **Do not chase spider parsing bugs for reddit / sports_injuries** — S2969/S2970 verified code path works.
- **Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env** — aiodns 3.5.0 is broken here; the flag default is `true` intentionally.
- **Do NOT expand the Policy A exclusion list (`core/services/no_items_policy.py`) without shape-sampling target rows first** — false exclusions HIDE real data-quality bugs. Sample before adding.
- **S2974: Do NOT clear `[NO_ITEMS]` sentinels via blanket ORM update.** Always route through `retriage_no_items --spider <name>` which recomputes `get_searchable_text` per row and clears only where non-empty.
- **S2975: Do NOT introduce a new sentinel or predicate on `embedding_text` without extending `BACKFILL_SKIP_SENTINELS` in `core/services/no_items_policy.py` AND grep-checking all call sites.**
- **NEW at S2977: Do NOT use `rebuild_embedding_text` on rows outside the extractor-change scope.** The command is a targeted refresh, not a general-purpose text rewrite. Always pass `--spider <name>` (already required). If a rows `raw_data` is stable and its extractor unchanged, running the command is a no-op — but the operator should have a specific reason to run it (extractor / spider fix that would change `get_searchable_text` output).

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2977 additions:**
- sec_spider Form 4 / S-1 / 13F-HR fetch loop expansion (~10 line change; tests + retriage)
- rebuild_embedding_text --dump-old-jsonl snapshot flag (Rigby A2 F-BLOCKER mitigation)
- Per-item `timestamp=datetime.now()` cleanup in sec_spider (T1 Fold B + A2 Fold D corroborated)
- SECSpider.name='sec' vs registry key mismatch (latent risk)

**S2975 additions:**
- remoteok pre-dedup filter (spider-side; ~1-2 files)
- Post-cleanup shape sampling for remaining top producers (behance / udemy / coursera / freecodecamp)
- Deliverable-as-spec Playbook rule proposal (fold #4 at trigger 8)

**S2974 additions:**
- huggingface `all_deduped` write suppression (STILL open — one of top-5 non-deferred post-cleanup)

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

**All ratified sweep scope discharged as of S2940.** S2971–S2977 were net-new engineering (Signal Intelligence UI + intake-quality arc + SEC extractor fix), not sweep work.

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

## For fuller context (S2846 → S2977)

See:
- **S2977 handoff (current):** `docs/handoffs/SESSION_2977_SEC_FORM_TYPE_INTERLEAVE.md`
- **S2977 shipped code:** PR #3608 (`sec_edgar form_type interleave + rebuild_embedding_text`)
- **S2977 spec deliverable:** `4e4534db-0e30-48b9-8cc5-e4a5e182aa54` (Rigby-drafted, status=completed)
- **S2977 support conversation:** `pa-5ad154766ca64d2d`
- **S2975 handoff:** `docs/handoffs/SESSION_2975_NO_ITEMS_STALE_CLEANUP.md`
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
