# Session 2845 — S2844 Misdiagnosis Corrected · SignalCluster source_spider Filter Shipped · Rigby Tool Gap Ledger Established

**Session:** S2845 (opened 2026-07-20; closed same day)
**Prior session:** S2844 — D4 picks ratified + SignalCluster semantic-query fix shipped
**Git HEAD at open:** `a6518e71f` (post-#3298 merge)
**Git HEAD at close:** `1ae1d40f5` (post-#3300 merge)
**Playbook version:** v0.8.0 (unchanged)
**Status:** ✅ CLOSED (no ratification-scoped artifacts; two engineering PRs shipped)
**PRs merged:** #3299 (source_spider fix) + #3300 (S2846 slate + ledger established)

---

## 1. What S2845 opened on

Per `00-START-NEXT-SESSION.md` at S2844 close: S2845 opens on A4 engagement #1 scoping AND the deferred A4↔A1 sequencing decision (§12.4 of `S2841_PRESSURE_TEST_ADDENDUM.md`). D6 discovery moratorium in force.

Chris's opening direction: "mint with s2845-planning and route to Rigby" for joint SIGN on sequencing before committing to any A4-vs-A1 execution order.

## 2. First SIGN cycle — A4↔A1 sequencing

**Turn 1 — Claude preliminary lean:** Sequential A1-first + light-touch A4 pipeline warm-up in parallel. Rationale: A4 pitch strengthens when we can point at shipped substrate; A1 week 1 is ~5 days concrete engineering per `docs/COST_SURVIVAL_AUDIT.md` §A.

**Turn 2 — Rigby joint SIGN (task `1020d0a1-...`; conversation `pa-e0053042f1ad40ca`):** AGREE with sequential A1-first, refined to *"A4 pipeline warm-up (prospect list + intro emails) in parallel BUT NOT full engagement packaging until A1 Week 1 substrate ships."* Substrate verification returned tool-grounded (non-rubber-stamped):

- `LLMCallLog.workspace` FK: NOT present in `core/models_llm_routing.py:297`; no partial migration
- Per-workspace cost cap: GLOBAL cap machinery exists (`core/services/ops_autopilot/budget.py:238–506` three-tier controller); no `workspace_daily_cap` / `workspace_budget` symbols — Week 1 must EXTEND, not just wire
- Ledger export: NOT shipped (planned Week 2–3)
- Duration reality check: effort table quotes ~1 working day for FK + ExternalAPICallLog telemetry — real Week 1 could collapse to ~2–3 days if scoped tight

**Response body truncated after §2.4** — §3 zoom-out ask (per `feedback_zoom_out_ask_per_rigby_sign`) missing from Rigby's returned message. Verdict + evidence were substantive enough to proceed; zoom-out deferred.

**Sequencing decision NOT ratified in S2845** — Chris pivoted before D-verdict (see §3).

## 3. Mid-session pivot — reopen S2844 SignalCluster finding

Chris: *"When we wrapped up you check the signals and we didn't have the data. I forgot I meant to ask you why the spiders didn't have the data or if they are collecting it but you and Rigby might not be looking in the correct spot..."*

The S2844 close conclusion — *"spiders feeding cluster aggregation are sports/news/gaming/generic-jobs, not AI-community sources"* — had been drawn from what SignalCluster returned via `intelligence_tool.signal_clusters` semantic query. Chris's question exposed that we'd never verified at the underlying data layer.

## 4. Four-layer investigation

Dispatched Rigby with tool-grounded ask across four layers (spider ingest / raw items content / aggregation pipeline / SignalCluster surface re-query) including explicit zoom-out ask per SIGN rule.

**Rigby's response revealed two tool-surface blockers:**

- **Blocker 1 (Layer 1):** `spider_status_tool.list` returned 44/88 spiders with no pagination — several AI-adjacent spiders reported "not found" that were actually present (later confirmed via `.search`).
- **Blocker 2 (Layer 2):** `spider_status_tool.search` returns items with empty `preview` field despite the underlying model storing content. Rigby couldn't keyword-check spider items from tool output.

**Layer 1 result (from what Rigby COULD return):** All AI-adjacent spiders ARE running — `hackernews` 329 runs / `huggingface` 557 (data_type=`ai_ml`) / `kaggle` 140 / `medium` 342 / `arstechnica` 113 / `hackernoon` 90 — all recent (last runs 9–11 AM MDT 2026-07-19).

**Layers 3+4 not completed by Rigby** due to tool-surface limitations. Claude went ORM-direct.

## 5. ORM-direct probe findings

**Two data planes discovered:**
- `LegacySpiderData` — 15,271 rows; JSONField `raw_data` blob storage; receives ALL spiders
- `SpiderData` (persistence) — 111,400 rows; clean title/content columns; receives ONLY `kalshi` in last 7 days

**Real content IS being collected** — samples from `LegacySpiderData.raw_data['items'][*].title`:
- *"Claude Code uses Bun written in Rust now"* (hackernews, score 201)
- *"GPT-5.6 used a prompt to close a 30-year gap in convex optimization"* (hackernews, score 251)
- Minecraft SDL3 / Anthropic Mythos / Chinese Deepseek / etc.

**Aggregation IS reading LegacySpiderData** — `core/services/signal_aggregation_service.py:262` filters by `is_processed=True | embedding_text != ''`, `[:500]` limit, extracts `raw_data['items'][*].title` at line 400–410.

**SignalCluster contains AI content** — 140 of 619 clusters in 30d (22.6%) have AI-adjacent sources in `source_breakdown`. Examples:
- *"Anthropic, Mythos demand spike"* (hackernews + wired + theverge + techcrunch + government + sports_news)
- *"Chinese, Deepseek emerging trend"* (lifehacker + techcrunch + techcrunch_startups)
- *"Anthropic, Claude knowledge gap"* (udemy + health + mit_tech_review)
- *"Comments, Score emerging trend"* (hackernews x3)

**S2844 conclusion was WRONG.** Data exists, is being clustered, is reachable via `source_breakdown__has_key` filter.

## 6. Root cause + fix

**Root cause:** `intelligence_tool` schema at `core/services/pa_tool_schemas.py:3424` restricted the shared `source` param to enum `["kb", "spider", "web"]` (for the `search` action). The `signal_clusters` handler at `core/services/td_handlers_core.py:3487` already supported `qs.filter(source_breakdown__has_key=<spider_name>`, but GPT-5.2 could never pass a spider name because the schema wouldn't accept one. The description at line 3414 said "source (spider name)" while the enum contradicted it.

**Fix (PR #3299, merge `8bb69d710`, ~15 lines across 2 files):**
- `core/services/pa_tool_schemas.py` — added dedicated `source_spider` string param (no enum); updated `signal_clusters` description
- `core/services/td_handlers_core.py` — reads `source_spider` first; falls back to `source` with existing enum-value guard for backward compat

**E2E verified live** post-recycle: `intelligence_tool.signal_clusters` with `source_spider='hackernews'` returned 8 clusters (matches ORM ~10), sample cluster "Anthropic, Mythos demand spike" mixing AI-adjacent + broader sources. `filters_applied.source_spider='hackernews'` echoed correctly.

## 7. Reflection turn — what the platform taught us

Chris asked before close: *"What has this taught us about the platform? [...] I have noticed that Rigby asked for improvements to tools to help with the research is that something we should consider?"*

**Four systemic lessons named:**
1. Two data planes exist for the same domain and neither is authoritative (LegacySpiderData vs SpiderData accretion)
2. Handlers and schemas drift silently — this session's fix is one instance of a repeatable class
3. Confident wrong answers ship without ORM cross-check (S2844 close was authored, SIGN'd, and ratified without anyone probing raw models)
4. Cluster quality is dominated by naming, not signal — "Anthropic, Mythos" works; "Comments, Score" hides equivalent-quality signal

**Reframing: Rigby's tool surface IS the product substrate** — per D4 ratification (§12 architecture, §13 picks), her tools ARE the A1 SaaS product surface AND the A4 governance-consulting demo. Every gap she hits, a future customer hits. Silent workarounds = friction the customer will pay for.

**Three workflow changes proposed → Chris ratified two:**
- **(a) Handler/schema drift lint** — SLATED for S2846 as candidate #0 (~2 hr; prevents recurring class of misdiagnosis)
- **(c) Rigby Tool Gap Ledger workflow** — codified as memory rule + persistent workspace deliverable
- **(b) Per-tool `debug` action** — discovery-arc deferred; needs Chris ratification before building

## 8. Ledger established

**Workspace deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`** ("Rigby Tool Gap Ledger") created in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`. Rigby-authored via `deliverable_tool.create` per `feedback_rigby_writes_workspace_deliverables`; post-create ORM cleanup applied for the two known gotchas ("Rigby: " title prefix + `diagnostic_status='diagnostic'`/`diagnostic_code='missing_initiative_id'`).

**Five seed entries** from S2845 discoveries:
1. `spider_status_tool.list` pagination missing (~2 hr) — open
2. `spider_status_tool.search` empty preview field (~2 hr) — open
3. `huggingface` returns 0 SignalCluster rows despite 24 spider runs/7d (~half day) — open
4. Multi-source `source_spider` filter (`has_any_keys` for parallel querying) (~1 hr) — open
5. Handler/schema drift lint (~2 hr) — **slated_for_S2846**

Rule for future sessions: when a tool-surface limitation is hit mid-work, Rigby appends to the ledger. Claude reviews at session close and picks 1–2 for next slate. Chris ratifies.

## 9. Memory rules added

Both new feedback memories saved to `~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/` + indexed in `MEMORY.md`:

- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data.md`** — when a PA/Rigby probe returns thin/empty results, verify at raw ORM before concluding data doesn't exist. Extends `feedback_verify_rigby_tool_runs_before_trusting_sign`. Explicitly frames the S2845 "5-day phantom project vs 15-line fix" cost of skipping the check.
- **`feedback_rigby_tool_gap_ledger.md`** — tool-surface limitations logged to workspace ledger, not worked around silently. Points at ledger UUID + workspace UUID + workflow contract. Extends the ORM-verify rule.

## 10. What shipped in S2845

**Repo canonical (Claude-authored):**
- `core/services/pa_tool_schemas.py` — `source_spider` param + description update (#3299)
- `core/services/td_handlers_core.py` — handler reads `source_spider` first (#3299)
- `00-START-NEXT-SESSION.md` — rewritten twice (initial for S2846 open; second update for slate promotion + ledger UUID) (#3299, #3300)
- `docs/INDEX.md` + `docs/_provenance.json` — cascade refresh (#3299)
- `docs/handoffs/SESSION_2845_SIGNAL_CLUSTER_SOURCE_FILTER_FIX.md` (this doc)

**Workspace canonical (Rigby-authored per `feedback_rigby_writes_workspace_deliverables`):**
- Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`

**Memory (Claude-authored):**
- `feedback_verify_at_raw_orm_before_trusting_tool_no_data.md`
- `feedback_rigby_tool_gap_ledger.md`
- `MEMORY.md` index updated with both

**Runtime impact:** `intelligence_tool.signal_clusters` now accepts spider-name filter. Post-merge `make recycle-all` per PLAYBOOK-7.4.4 / `feedback_recycle_after_merge` (sha `8bb69d71004d` recorded to `logs/recycle_events.jsonl`). Docs cascade run per `feedback_docs_cascade_at_every_close` (3281 docs indexed, 0 unembedded, 2717 provenance rows).

## 11. What did NOT ship (deferred to S2846)

- **A4↔A1 sequencing D-verdict** — Chris pivoted to SignalCluster investigation before ratifying. Joint Claude+Rigby recommendation stands (sequential A1-first + light-touch A4 pipeline warm-up); awaits Chris yes/no at S2846 open.
- **No workspace mirror pair** — this session's shipping was engineering bug fixes, not a ratifiable arc close (twin-canonical rule per `feedback_twin_deliverable_at_every_ratification`).
- **No `debug` action per tool** — option (b) from reflection; Chris deferred pending discovery on scope.
- **Two-plane data audit** (LegacySpiderData vs SpiderData deduplication) — real problem, ~3–5 day arc, parked for post-A1-Week-1.
- **AI-source SignalCluster pipeline** as originally scoped in S2844 close (3–5 days) — **RETIRED** as based on the S2844 misdiagnosis. Real gap was tool-surface, now fixed.

## 12. What S2846 opens on

Per `00-START-NEXT-SESSION.md` refresh:

1. **First action: atomic mint** — wrapper still points at `pa-e0053042f1ad40ca` (intended failure mode). Run `python manage.py session_lifecycle close --label s2846-<slug>` FIRST.
2. **Ratify A4↔A1 sequencing** — route to Chris early; joint recommendation is sequential A1-first + light A4 pipeline warm-up in parallel.
3. **First engineering work: handler/schema drift lint** (S2846 candidate #0, ~2 hr) — prevents recurring S2844-class misdiagnoses across entire tool surface.
4. **A4 pipeline warm-up now unblocked** by S2845 fix — `intelligence_tool.signal_clusters` with `source_spider='hackernews'`/`'devto'`/`'techcrunch_startups'`/`'producthunt'`/`'huggingface'`/`'mit_tech_review'`/`'arstechnica'` returns AI-tooling market signals as discovery substrate.

**D6 moratorium still in force.** No new strategic discovery arcs, no D4 reopening.

## 13. Provenance

- Rigby SIGN task IDs: `1020d0a1-ba58-44d9-8a9a-227d9f25d9f1` (A4↔A1 sequencing SIGN), `d62a56ea-b52a-4357-b328-b95af923081e` (four-layer investigation), `90abec8f-69d2-4a73-a2fc-e05170417cca` (source_spider live verify), `594a5f85-317b-4201-8851-0dd668004273` (ledger create)
- Session conversation pin: `pa-e0053042f1ad40ca` (retired at close; seventy-sixth consecutive per S2770+ pattern; fresh mint required at S2846 open)
- Workspace: Donkey Betz `b4503364-2573-4401-9e28-61a739e0ce50`
- Ledger deliverable: `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- PRs: #3299 (source_spider fix), #3300 (S2846 slate + ledger doc)
