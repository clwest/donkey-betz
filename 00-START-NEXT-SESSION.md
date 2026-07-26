# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2974 CLOSED. Workflow reframe validated for the **sixth walk** (S2969–S2974); **second walk of the Rigby-drafted-spec origination variant** (S2973 was first). One code PR shipped: **#3602 (S2974 legislation extractor hardening + retriage command)**. Chris handed Deliverable `914b1118` (Rigby-drafted spec) asking to classify + reduce [NO_ITEMS] for huggingface + legislation. I sampled 25 rows/spider via Django ORM BEFORE T1 SIGN — the sampling picked the fix. Huggingface's recent NO_ITEMS is 100% legitimate `all_deduped` (Class 2); the historical Class 3 empty-raw rows self-resolved 2026-07-17. **Legislation was 100% Class 4 extractor mismatch**: every item is a wrapped envelope carrying pre-computed `item['embedding_text']` (like `"H7030. Establishes the healthcare worker platform..."`) — the extractor just never looked there. Fix at `core/models_unified_system.py:3898`: new `_extract_item_text` helper supports three shapes (spider-provided embedding_text with sentinel + length guards / nested `item['raw_data']` / flat top-level unchanged) + new `retriage_no_items --spider <name> [--apply]` management command (recompute-driven, dry-run default). 50/50 tests pass. Rigby T1 + A2 SIGN both AGREE, no F-BLOCKERs. Post-merge: retriage cleared 61 rows, direct backfill embedded all 61 (0 failed). **24h intake NO_ITEMS rate dropped 79.1% → 71.0%** from one spider's fix. Legislation dropped OFF top-20 producers in 24h AND 7d windows. Full context: `docs/handoffs/SESSION_2974_LEGISLATION_EXTRACTOR.md`.

**Session cost this session:** minimal — 5 PA turns (fetch-spec / T1 / A2 / tool-verify / verdict), no v2 subprocess dispatches, no revision cycles.

**HEAD at close:** `c331a0404` (PR #3602 merged; docs cascade PR TBD). Workers recycled after merge per PLAYBOOK-7.4.4.

---

## S2975 first-action — WAIT FOR CHRIS (same as S2969–S2974)

The reframe held for the **sixth time**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2974_LEGISLATION_EXTRACTOR.md` in full — especially §"Root cause narrative", §"Ground-truth numbers", §"Live-verify results".
4. **Optionally probe the shipped state:**
   - `curl -s -H "Cookie: sessionid=<yours>" 'http://localhost:8000/api/signals/embedding-coverage/?include_breakdown=1&window=168'` — legislation should be OFF the top-20 spiders list.
   - Or from Django shell: `LegacySpiderData.objects.filter(spider_name='legislation', embedding__isnull=False).count()` — should be ≥61.
   - Or `python manage.py retriage_no_items --spider legislation` (dry-run) — should show `would clear: 0, still empty: 564` (unrecoverable historical rows).
5. **Report readiness in one short message and wait.** Something like: "Oriented. S2974 closed — reframe validated for the sixth walk. Legislation extractor shipped; 61 rows recovered; 24h NO_ITEMS rate 71.0% (was 79.1%). Ready when you have a spec pointer."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer:** follow the S2969–S2974 pattern — read spec, targeted "existing implementation analysis" (Cycle 1A verify-before-build), **for diagnostic-shape arcs, complete the ORM sampling BEFORE T1 SIGN** (S2974 candidate fold #11), T1 SIGN to Rigby with zoom-out ask, fold, implement, A2 SIGN with file+line evidence, merge with `--admin`, `make recycle-all`, live-verify in-shell (Django `Client().force_login` for auth-gated routes; **`HTTP_HOST='localhost'` required or DisallowedHost fires**), Rigby verifies from her tool surface, report three-part summary to Chris.

---

## S2975 high-value seeds (Chris picks whether to open)

**huggingface `all_deduped` write suppression.** Rigby's suggested follow-up during S2974 T1: spider writes an audit row every 30 min saying "all items were duplicates". Only 9 rows / 24h, but adds noise to intake metrics and shows up in the 24h NO_ITEMS rate calc. Options: drop to a separate run-log table, or suppress writes on `diagnostic.status='success_empty'`. Small (~1-2 files touched) but touches spider write path — needs testing.

**theodds auth-failure fix (STILL OPEN from S2972+S2973).** Top NO_ITEMS producer at ~294 rows / 30d. Rigby's S2973 shape-sampling confirmed rows carry `auth_failure_circuit_breaker` / `error_summary` envelopes. Fix requires Chris to rotate `THE_ODDS_API_KEY` (or verify API quota). Post-fix: re-run 24h + 30d breakdown to validate top-producers list re-ranks and rate drops.

**Shape sampling for remaining top-10 producers** (`securityweek`, `udemy`, `colorado_family_law`, `behance`, `freecodecamp`, `techcrunch_startups`, `education_rss` — all at 10 rows / 7d after legislation dropped off). Sample ~10 rows each, classify into class 1/2/3/4 per S2973+S2974 rubric. May yield another extractor-hardening win or 1-2 policy additions.

**Deliverable-as-spec fold @ trigger 6 — Playbook rule candidate.** Reframe pattern has now walked 6 times (S2969–S2974) in two variants. If S2975 continues the pattern, propose as a Playbook §5 or §6 rule at S2975 close. Substrate is ready: existing envelope pattern from prior Playbook amendments applies directly.

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
4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 6** (S2969–S2974). **Six-trigger corpus. Strong Playbook rule candidate.** Two variants: Chris-paste (S2969–S2972) + Rigby-drafted-per-Chris-ratification (S2973 + S2974). Both walk the same 10-step shape. **Recommend proposing as Playbook rule at S2975 session close if the pattern holds one more walk.**
5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** **Trigger count: 3** (S2970, S2972, S2974).
6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** **Trigger count: 1** (S2970).
7. **"Route-placement is a settable expectation, not a spec constraint."** **Trigger count: 1** (S2971).
8. **"Rigby web_fetch_tool can't authenticate against Django session-cookie endpoints."** **Trigger count: 2** (S2971, S2972). Watch for third — could become Rigby Tool Gap Ledger entry.
9. **"Rigby-drafted spec deliverable is a first-class origination path."** **Trigger count: 2** (S2973, S2974). Could formalize as variant of fold #4.
10. **"Sampling extrapolation past ~10k rows produces cross-session drift."** **Trigger count: 1** (S2972).
11. **NEW: "Sample-before-plan cuts T1 revision cycles to zero."** **Trigger count: 1** (S2974). For diagnostic-shape arcs, complete the ORM sampling BEFORE drafting T1 — evidence-grounded T1 earns Rigby AGREE + refinements on first turn, no revision loop. Watch for second.
12. **NEW: "Retriage-command-as-primitive over blanket ORM update"** **Trigger count: 1** (S2974). When extractor improvement retroactively unblocks marked rows, ship a recompute-driven clear command with dry-run default + required spider arg — not a blanket ORM update or a generic "re-triage all" primitive. Watch for second when next extractor improvement lands.

---

## Universal open sequence (unchanged)

1. `context-kit orient` — source-of-truth chain, latest handoff
2. Absorb `MEMORY.md` + `CLAUDE.md` (both auto-injected)
3. Read this `00-START-NEXT-SESSION.md` in full
4. **Session-open atomic mint check:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2975 pin minted at S2974 close cascade. If not fresh, run `python manage.py session_lifecycle close --label s2974-legislation-extractor --allow-no-mirror` first (per `feedback_session_open_atomic_mint_before_pa_dispatch`).
5. Verify `claude` CLI availability (if v2 dispatches are on the day's plan): `which claude && claude --version` (should show 2.1.114+ at `~/.local/bin/claude`)
6. Read `docs/handoffs/SESSION_2974_LEGISLATION_EXTRACTOR.md` — full context on this session's shipped code + reframe walk 6
7. **Wait for Chris to hand you a spec pointer via Rigby.** Do not proactively propose work.

---

## What's forbidden at S2975 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward.

- **Do not automatically merge S2968 PR-B** — its dispatch wiring is architecturally stale under the reframe.
- **Do not proactively dispatch v2 test runs at session open** — each burns ~$0.15-0.20.
- **Do not chase spider parsing bugs for reddit / sports_injuries** — S2969/S2970 verified code path works.
- **Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env** — aiodns 3.5.0 is broken here; the flag default is `true` intentionally.
- **Do NOT expand the Policy A exclusion list (`core/services/no_items_policy.py`) without shape-sampling target rows first** — false exclusions HIDE real data-quality bugs. Sample before adding.
- **NEW at S2974: Do NOT clear `[NO_ITEMS]` sentinels via blanket ORM update.** Always route through `retriage_no_items --spider <name>` which recomputes `get_searchable_text` per row and clears only where non-empty. Blanket clears cause backfill thrash (rows re-mark themselves).

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2974 additions:**
- huggingface `all_deduped` write suppression (small; deferred per Rigby T1 fold #1)
- Shape sampling for `securityweek` / `udemy` / `colorado_family_law` / `behance` / `freecodecamp` / `techcrunch_startups` / `education_rss` (all tied at 10 rows / 7d)

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

## For fuller context (S2846 → S2974)

See:
- **S2974 handoff (current):** `docs/handoffs/SESSION_2974_LEGISLATION_EXTRACTOR.md`
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
