# SESSION 2970 — PR-B RSS-first fixes for reddit + sports_injuries shipped (workflow reframe second walk)

**HEAD at close:** `d11d7fcee` (PR-B #3593 + PR-B.1 #3594 merged; docs cascade PR TBD)
**Branch shape:**
- `feat/s2970-rss-first-reddit-sports-injuries` → main (merged, branch deleted)
- `feat/s2970-pr-b1-threaded-dns-resolver` → main (merged, branch deleted)

**PR count:** 2 code PRs merged (#3593, #3594)
**Session cost:** minimal — no v2 subprocess dispatches; only PA-tool calls to Rigby (T1 + ack + A2 + PR-B.1 decision + close verdict = 5 PA turns)

---

## What shipped

**Two code PRs merged tonight:**

| PR | Title | Shape |
|---|---|---|
| **#3593** | `feat(s2970): PR-B — RSS-first fixes for reddit + sports_injuries spiders` | +825/-16 across 4 files: URL swaps (reddit `.rss`, sports_injuries rotowire per-sport) + injury-keyword filter + fetch_stats plumbing + `empty_reason='fetch_failed'` in spider_diagnostic + 23 tests |
| **#3594** | `feat(s2970): PR-B.1 — flag-gated aiohttp ThreadedResolver swap` | +114/-1 across 2 files: `SPIDER_USE_THREADED_DNS_RESOLVER` flag (default true) + 6 tests. Unblocks fetches broken by aiodns 3.5.0 DNS bug on this env |

**One docs cascade PR to file at session close:** this handoff + 00-START refresh + wrapper pin bump.

---

## The workflow reframe: second walk

**S2969 was the first walk. S2970 is the second.** Chris + Rigby produced an engineering-spec Deliverable (`6f2799f7-26aa-4e57-b71d-d94a01b193f8` — *PR-B Spec: RSS-first fixes*). Chris handed the deliverable UUID + callback conversation ID (`pa-ab10ffdb0e5f4597`) to CC on session open. CC:

1. Read the spec via `deliverable_tool.get`
2. Explored code surface: `SPIDER_TARGET_URLS`, `parse_rss_feed`, `collect_spider_data`, dedup service, runner empty-branch (S2969's `_impl_run_spider_network` line 549-570), lightweight-execute parity (S2969 line 799-822)
3. Live-probed reddit `.rss` (Atom, 25 entries, rate-limits on burst) and sports_injuries alternatives — discovered all 3 currently-listed URLs return HTTP 404; identified rotowire per-sport news feeds as best-available replacement (~15-25 combined pre-filter, injury-relevant post-filter)
4. Routed T1 pre-code SIGN to Rigby via `pa-ab10ffdb0e5f4597` with mandatory zoom-out
5. Rigby REVISE (light): (a) fold `fetch_failure` into `empty_reason='fetch_failed'` in existing schema instead of new top-level status, (b) sports_injuries needs injury-keyword filter to prevent semantic drift into roster news
6. Acked folds + implemented + tested (23/23 for new file, 30/30 S2969 regression, 3/3 governance regression)
7. Routed A2 post-code SIGN with file+line evidence per PLAYBOOK-6.10.9 + fixture titles (pass / reject list) per Rigby's A2-instructions
8. Rigby AGREE with 1 optional fold (add MRI + illness + covid keywords) — folded
9. Pushed PR-B + merged with `--admin` + `make recycle-all` per PLAYBOOK-7.4.4
10. Live-verified via `_impl_run_spider_network` in-shell — **both spiders reported `empty_reason=fetch_failed`**. Root-caused via direct aiohttp probe: aiodns 3.5.0 `ClientConnectorDNSError: Could not contact DNS servers` even though `socket.getaddrinfo` + `urllib` + `curl` all resolve fine
11. Routed decision to Rigby (A / B / C options) — she picked A with a feature flag + one call site + safe rollback
12. Implemented PR-B.1 in one call site behind `SPIDER_USE_THREADED_DNS_RESOLVER` (default true per `feedback_local_truth_no_production`) + 5 tests
13. Pushed PR-B.1 + merged with `--admin` + `make recycle-all`
14. Live-verified second time — **reddit 20 unique items, sports_injuries 6 unique items** (down from 0/0 baseline)
15. Routed sports_injuries DoD gap (6 < 10) to Rigby for verdict
16. Rigby verified from her tool surface (`spider_status_tool.history`) — both spiders show new source_urls (reddit `.rss`, sports_injuries rotowire per-sport). Verdict: **PASS as-is**; sports_injuries yield will grow with season activity; small keyword tuning available as a follow-up only if Chris insists on hitting exactly ≥10
17. Chris ratified via terminal + directed `open the close cascade PR`

The reframe held again. Zero terminal yes/no asks during execution. Everything decisional routed through Rigby.

---

## PR #3593 — RSS-first fixes

**Reddit (`ai_core/spiders/real_data_collector.py:79-88`):** replaces 8 JSON API endpoints (`hot.json?limit=15`) with **3 Atom `.rss` endpoints** (`/r/webdev`, `/r/programming`, `/r/Entrepreneur`). Kept to 3 subreddits to reduce 429 rate-limit surface; each Atom feed returns ~25 canonical permalinks.

**Sports_injuries (`ai_core/spiders/real_data_collector.py:299-311`):** replaces 3 dead URLs (rotowire `injuries.xml`, cbssports `injuries/`, rotogrinders `injury-report.xml` — all HTTP 404) with **5 rotowire per-sport news feeds** (`news.php?sport=NFL|MLB|NBA|NHL|SOCCER`). Combined pre-filter ~15-25 items typical.

**Injury-keyword filter (`ai_core/spiders/real_data_collector.py:319-378`):** `SPORTS_INJURY_KEYWORDS` (31 tokens: injur, questionable, doubtful, out, ruled out, sidelined, day-to-day, dtd, dnp, il, ir, PUP, will miss, surgery, concussion, hamstring, ACL, MCL, sprain, strain, torn, fracture, contusion, MRI, illness, covid) + `filter_injury_items(items)` (case-insensitive substring match on `f' {title.lower()} {description.lower()} '`, spider-scoped to sports_injuries only, applied post-parse pre-dedup in `collect_spider_data`).

**Fetch-stats plumbing (`ai_core/spiders/real_data_collector.py:2264-2320`):** `collect_spider_data` tracks per-URL `fetch_stats` (attempts, successes, `urls_attempted`, `failed_urls`) and returns it in the result dict. Not routed via `data['failure_type']` — keeps `spider_success=True` when the spider ran without exception (Rigby T1 REVISE: don't create a new top-level status).

**Spider_diagnostic extensions:**
- `EMPTY_REASON_FETCH_FAILED = 'fetch_failed'` (`core/services/spider_diagnostic.py:64`)
- `derive_empty_reason(items_before_dedup, unique_after_dedup, fetch_stats=None)` (line 66-85): precedence **fetch_failed > no_items > all_deduped**. `fetch_failed` requires `attempts > 0 AND successes == 0`. `all_deduped` requires `items_before_dedup > 0 AND unique_after_dedup == 0` (Rigby T1 explicit guardrail).
- `build_empty_run_diagnostic` extended (line ~110-146) to accept optional `fetch_stats`; when `empty_reason == fetch_failed`, payload carries `urls_attempted` + `failed_urls`.

**Runner threading:**
- `_impl_run_spider_network` empty branch (`core/tasks_spiders.py:548-582`): passes `fetch_stats` from `data.get('fetch_stats')` into `build_empty_run_diagnostic`.
- `_impl_execute_single_spider_lightweight` (`core/tasks_spiders.py:820-855`): same threading for on-demand Execute path. `_collect_spider_data_sync` in `core/tasks.py` returns `None` for fetch_stats today so derived reason falls back to no_items/all_deduped cleanly.
- `spider_results` (`core/tasks_spiders.py:588-611`): now surfaces derived `empty_reason` alongside status.

**Tests (`core/tests/test_spider_rss_first.py`, +648 LOC, 23 tests):**
- `SpiderTargetUrlsConfigTests` (3): URL guards prevent regression back to `.json` / dead URLs
- `ParseRssFeedFixtureTests` (2): parse_rss_feed on reddit Atom + rotowire RSS fixtures
- `FilterInjuryItemsTests` (4): positive keeps injury items, **negative drops** roster news ("Remains on left squad list", "Heading to Philadelphia", "Agrees to rookie contract", "Inks two-year deal") per Rigby T1 pushback, mixed batch splits correctly
- `DeriveEmptyReasonTests` (5): precedence matrix including the all_deduped-requires-items-before-dedup-positive guardrail
- `BuildEmptyRunDiagnosticFetchFailureTests` (2): fetch-failure payload carries urls; success branches don't leak URL lists
- `CollectSpiderDataFetchStatsTests` (4): fetch_stats populated on all-failure / partial-success; injury filter spider-scoped (reddit items pass through)
- `DedupStabilityRssTests` (1): 2-run stability on same reddit permalinks (first N unique, second 0 unique / N duplicates)
- `RunnerFetchFailureIntegrationTests` (2): full runner integration for fetch_failed diagnostic + reported empty_reason

---

## PR #3594 — PR-B.1 ThreadedResolver fold

**Root cause discovered post-PR-B merge:** `aiohttp` picks up `aiodns` automatically when installed. `aiodns` 3.5.0's pycares backend fails on macOS + certain Linux configs where the system DNS is mediated by a stub (mDNSResponder) it doesn't read. `socket.getaddrinfo` / `urllib` / `curl` all work; only aiohttp fails.

**Fix (`ai_core/spiders/real_data_collector.py:20-46, 2287`):** two-line helper `_use_threaded_dns_resolver()` reads env flag `SPIDER_USE_THREADED_DNS_RESOLVER` (default `true`) + factory `_build_client_session_kwargs()` returns `{'connector': aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver())}` when flag is on, else `{}`. Applied at exactly one call site: `aiohttp.ClientSession(**_build_client_session_kwargs())` in `collect_spider_data`.

Default `true` per `feedback_local_truth_no_production` + `project_single_user_pre_prod_operating_context` — the working default matches Chris's actual runtime. Any env with a known-good aiodns can flip the flag off.

**Tests (5 additional in `ThreadedDnsResolverFlagTests`):** flag default+overrides; kwargs threaded-resolver when on; kwargs empty when off; end-to-end collector wires ThreadedResolver via ClientSession spy (isolates verification without hitting the network).

**Post-swap probe:** rotowire NFL → HTTP 200 / 3140 bytes / 5 entries. Reddit → HTTP 429 (rate-limited on burst but reachable).

---

## Live-verify results (post-PR-B.1 merge + recycle)

**Baseline (before this session):**
- reddit: 2 rows last 24h; last row `src=hot.json` `empty_reason=no_items`
- sports_injuries: 1 row last 24h; last row `src=injuries.xml` `empty_reason=no_items`

**After PR-B + PR-B.1 (in-shell dispatch of `_impl_run_spider_network`):**
- **reddit: 20 unique items** ✅ (spec DoD ≥5)
- **sports_injuries: 6 unique items** (spec DoD ≥10 short by 4 due to off-season MLB/NHL thinness + return-to-play tokens like "poised to practice" / "cleared for full practices" not in initial keyword list)

**Rigby tool-surface verification:**
- `spider_status_tool.history reddit limit=5` → 4 new rows all `src=https://www.reddit.com/r/webdev/.rss` (the 5th is the S2969 baseline row)
- `spider_status_tool.history sports_injuries limit=5` → 4 new rows all `src=https://www.rotowire.com/rss/news.php?sport=NFL` (the 5th is the S2969 baseline `injuries.xml` row)

**Rotowire per-URL yield tonight (SPORTS_INJURY_KEYWORDS filter):**
```
NFL: 5 parsed → 1 kept (only "PUP"; "Poised to practice" + "Cleared for full practices" not in initial keyword list)
MLB: 5 → 3 (game recaps with injury references in descriptions)
NBA: 1 → 0 (LeBron trade only)
NHL: 1 → 0 (Schmid signing only)
SOCCER: 5 → 2 (groin surgery + torn MCL)
TOTAL: 17 parsed → 6 kept-after-filter
```

**Rigby verdict on the DoD gap:** PASS/close as-is; open a small "sports_injuries keyword tuning" mini-PR only if Chris insists on hitting exactly ≥10. Off-season thinness will resolve naturally with season activity; conservative keyword expansion (`cleared for`, `activated`) is the low-risk lever if needed.

---

## Governance shape this session

**Not a Playbook amendment session** — no [GR] rules changed.

**SIGN cycles:**
- T1 pre-code (Rigby): REVISE (light) — 2 folds (fetch_failure → empty_reason='fetch_failed'; injury-keyword filter mandatory)
- A2 post-code (Rigby): AGREE with 1 optional fold (MRI + illness + COVID keywords)
- Post-PR-B live-verify DNS root-cause decision (Rigby): Option A with flag-gate + safe rollback
- Post-PR-B.1 live-verify DoD gap decision (Rigby): PASS/close (6 < 10 acceptable given RSS-first works + observability shipped + off-season thinness explains the gap)

Every SIGN routing included the mandatory zoom-out ask per `feedback_zoom_out_ask_per_rigby_sign`. Rigby's zoom-out surfaced substantive REVISE items in the T1 cycle (fold-in-existing-schema architectural preference + semantic-drift protection).

**Chris D-verdicts:**
- 1 arc-open ratification via deliverable handoff (S2970 first-action = RSS-first spec, from Chris + Rigby joint work pre-session)
- 1 close ratification via terminal `open the close cascade PR`

**Playbook rule adherences:**
- **PLAYBOOK-6.10.9** (fold evidence admission): both A2 SIGNs included concrete file+line evidence and (for PR-B) explicit fixture titles for the pass/reject sets
- **PLAYBOOK-7.4.4** (recycle-after-merge): `make recycle-all` executed after PR-B merge and PR-B.1 merge; will execute again after docs cascade merge
- `feedback_gh_pr_merge_admin_until_billing_fixed`: both PRs merged with `--admin`
- `feedback_local_truth_no_production`: local `make celery-recycle` treated as deploy step; live-verify via in-shell dispatch is the ship criterion
- `feedback_zoom_out_ask_per_rigby_sign`: every SIGN routing included zoom-out
- `feedback_verify_rigby_tool_runs_before_trusting_sign`: verified Rigby's `deliverable_tool.get` + `spider_status_tool.history` tool_runs before accepting verdicts
- `feedback_claude_directs_rigby_then_verifies`: Rigby executed tool-surface probes; CC verified independently via ORM + live shell dispatch
- `feedback_session_close_three_part_summary`: close message delivered to Chris as three-part plain-English (what/how it improves/next action)
- `feedback_claude_rigby_agree_first_chris_yes_no`: PR-B.1 A/B/C options resolved between Claude + Rigby before ratification; final DoD-gap decision was Claude+Rigby agreement (PASS as-is) which Chris ratified

**Candidate folds for future ratification (NOT codified this session):**

Carrying forward from S2969:

1. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969 arc). No new instance surfaced this session.

2. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 2** (S2969 + S2970 arcs). Two-trigger corpus reached. Per Chris's four-trigger threshold on IOS-lifecycle-adjacent codifications (see `project_deployment_state_between_merged_and_active`), still need 2+ more triggers before Playbook amendment. Consider promoting to a Playbook rule once triggers 3 + 4 appear.

New at S2970:

3. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** PR-B added `empty_reason=fetch_failed`; PR-B live-verify then triggered exactly that reason, correctly pointing at the aiohttp/aiodns DNS issue. This is the S2969 observability arc functioning as designed — the diagnostic *is* the debugging tool. Worth naming as a pattern once a second trigger appears: **shipping observability makes root causes visible; the next PR often addresses what observability just surfaced.** **Trigger count: 1** (S2970 arc).

4. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** PR-B.1 folded the aiohttp resolver fix into the same session as the PR-B ship, using a feature flag for rollback safety. Alternative would have been to defer to a "worker egress validation" arc (as S2969 originally did for the DNS issue). Rigby preferred fold-in-scope because "the spec/intent Chris asked for is 'make them actually fetch.' Right now they still fetch 0 in the real runtime path." Worth naming: **when live-verify surfaces a small-diff infra bug directly blocking spec DoD, fold-in with a feature flag beats defer-to-follow-up arc.** **Trigger count: 1** (S2970 arc).

---

## Session-close hygiene

- ✅ HEAD `d11d7fcee` — worker recycled after PR-B merge and PR-B.1 merge per PLAYBOOK-7.4.4 (events logged to `logs/recycle_events.jsonl`)
- ✅ All spider RSS-first tests green (29/29 in `test_spider_rss_first`)
- ✅ Regression check: S2969 diagnostic tests still green (30/30); governance still green (3/3)
- ⏭ Session lifecycle close + wrapper pin bump: this docs cascade PR
- ⏭ Docs cascade PR: this handoff + 00-START refresh + wrapper pin bump
- ⏭ Second `make recycle-all` after docs cascade merge (per PLAYBOOK-7.4.4)

---

## Post-close addendum — `backfill-spider-embeddings` PeriodicTask re-enabled

After the S2970 close cascade merged (`25918ec91`), Rigby flagged that PeriodicTask `backfill-spider-embeddings` (task `core.tasks.backfill_spider_embeddings`, every 15 min, queue `ml`) was disabled and had never run in the current env.

**Diagnostic findings (Rigby's report vs ground truth):**
- ✅ `enabled=False` — correct
- ✅ Task path / schedule / queue — correct
- ❌ "Last run: null (has never run)" — **misleading**. `last_run_at=None` but `total_run_count=644`. Task ran 644 times historically; someone reset `last_run_at` when disabling. Not a discovery bug.

**Why it was off (intentional, S1222):** PeriodicTask.description recorded the disable rationale at S1222 P6 audit B2: "Backfill is complete (644 historical runs). Re-enable on demand if a new embedding model warrants a fresh backfill — leave it off otherwise to keep the ml queue clear."

**Why that rationale no longer holds:** current embedding coverage is **0 / 16,874 (0.0%)**. Sustained spider ingestion + S2969 diagnostic rows + S2970 RSS-first real items accumulated 16,874 pending rows since S1222. The "backfill complete" claim was true at the time but has been overtaken by new work.

**Infrastructure health verified:**
- Task at `core/tasks.py:1418` has full guardrail stack: `@singleton_task(ttl=600)` + fail-open ml-queue depth-gate (skip if depth > 50 msgs, per S1171 mitigation for the 06-14 → 06-19 533-msg accumulation incident) + `batch_size=500` with `.only()` column filter (S1083 mitigation for the 1.37GB memory spike incident).
- `ml` queue drained by `long_running` worker per `Makefile:326` (`--queues=long_running,ml`). Verified via Rigby's `cockpit_tool queue_lengths`: all queues GREEN, depth=0.
- S2969/S2970 diagnostic rows (`items: []`) handled correctly by `spider_semantic_search.backfill_embeddings`: first pass marks `embedding_text='[NO_ITEMS]'` and permanently short-circuits future runs.

**Decision routing (Rigby-first per `feedback_claude_rigby_agree_first_chris_yes_no`):**
- Routed A/B/C/D options to Rigby via `pa-ab10ffdb0e5f4597` with zoom-out ask
- Rigby verdict: **Option A** — flip it on now. Rationale: "spider ingestion is working again; embeddings are the next hop that makes the data usable for semantic search + clustering. Old rationale no longer applies. Guardrails make re-enabling low-risk."
- Chris ratified via terminal: `yes flip it on`

**ORM operation executed:**
```python
from django_celery_beat.models import PeriodicTask
pt = PeriodicTask.objects.get(name='backfill-spider-embeddings')
pt.enabled = True
pt.description = (
    'Re-enabled Session 2970 (2026-07-25): 16,874 rows pending embedding vs 0 coverage — '
    'the S1222 P6 "backfill complete" rationale no longer holds after sustained spider ingestion + '
    'S2969 diagnostic rows + S2970 RSS-first real items. Guardrail stack still in place: '
    '@singleton_task ttl=600 + fail-open ml-queue depth-gate (skip if depth > 50 msgs) + '
    'batch_size=500 with .only() column filter for bounded memory (S1083 mitigation). '
    'ml queue drained by long_running worker (Makefile queues=long_running,ml). '
    'Route joint verdict: Claude+Rigby AGREE Option A / Chris ratified via terminal.\n\n'
    '--- Prior description (S1222 P6 audit B2) ---\n'
) + prior_description
pt.save(update_fields=['enabled', 'description'])
```

Result: `enabled=True`, `total_run_count=644` preserved (unchanged), description now records both the S2970 re-enable rationale and the S1222 disable note appended.

**Sanity-check window opens next Beat tick** (`*/15 * * * *` America/Denver). Expected trajectory: first cycle drains 500 rows → coverage moves off 0% within 15-30 min → steady-state drain of the remaining 16,874 within ~8-10 hours if batch_size holds.

**S2971 first-action follow-up (see 00-START):** verify at least one cycle has run cleanly before opening any new arc.

