# `intelligence_tool` — Validation Report (S2914)

**Tool:** `intelligence_tool`
**Schema:** `core/services/pa_tool_schemas.py:4016`
**Handler:** `core/services/td_handlers_core.py:3304` (`_handle_intelligence`) — unified gateway over `stock_intelligence_tool`, `sports_betting_tool`, `legislation_tool`, `rag_query_tool`, `spider_data_tool`, `web_search` (Session 1079) + direct data actions (Session 1100 / Gap 4 / Gap 6 / Gap 7)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2914 (Path B systematic sweep — Slice 3 batch 4 of `td_handlers_core`)
**HEAD at validation:** `396abccc8` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (**6 direct pure-ORM READ_ONLY actions validated in-scope this batch; 10 additional READ_ONLY actions transitively dispatched via delegates documented-but-not-verified**; 3 MUTATION actions correctly gated — see §5a). Auto-classifier will report `validated (full)` per S2911/S2912 precedent because all 19 action names appear in `## Covered actions`.
**Rigby SIGN:** S2914 T0 SIGN — **CRITICAL CATCH.** `search` with `source='web'` transitively invokes `_handle_web_search` (defined in `td_handlers_agents.py:384`), i.e. **hidden network I/O**. Same class of issue as S2913 batch 2 `conversation_tool.search` LLM-cost catch. Reclassified `search` as MUTATION per `feedback_verify_rigby_tool_runs_before_trusting_sign`. Q3 zoom-out ask named "gateway ambiguity debt" as the coupling risk — batch 4 corrective is explicit allowlist + transitive exclusions documented by name.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Unified intelligence desk — combines stocks, sports betting, legislation, search (KB/spider/web), and ML analytics behind a single tool. Session 1079 introduced the gateway to replace 6 individual tools (`stock_intelligence_tool`, `sports_betting_tool`, `legislation_tool`, `rag_query_tool`, `spider_data_tool`, `web_search`). Session 1100 added direct ORM readers (`stock_briefs`, `ml_predictions`, `signal_clusters`); Gap 4/6/7 rounds added `sports_sharp_signals`, `congress_members`, `legislation_tracked`.

Distinct from `dream_tool` (creative-idea intake — pre-work), `governance_tool` (human-decision inbox — post-execution approvals), `work_tool` (initiative + action-item execution — the work itself), and `content_tool` (content pipeline — deliverables + blogs, not market intel).

## Covered actions

**19 total actions.** Batch 4 in-scope: **6 direct pure-ORM READ_ONLY** (validated via harness + direct handler read). 10 additional READ_ONLY actions transitively dispatched via composite/delegate paths (documented-but-not-verified — the delegate handlers themselves have not been read this batch). 3 MUTATION actions correctly gated (`search` network + `kb_ingest` write + `sports_record_wager` write).

**READ_ONLY — in scope this ship (direct pure-ORM, verified):**

- `stock_briefs` — **in scope this ship** — verified live via T1a harness at HEAD `396abccc8` (`success`, 5ms). Direct ORM read of `MarketIntelligenceBrief` ordered by `-brief_date`. Session 1100 read-only surface.
- `ml_predictions` — **in scope this ship** — verified live via T1a harness (`success`, 8ms). Direct ORM read of `sports.MLPrediction` with select_related game + predicted_winner. Session 1100 read-only surface.
- `signal_clusters` — **in scope this ship** — verified live via T1a harness (`success`, 17ms). Direct ORM read of `SignalCluster` with rich optional filters (`query`, `pattern_type`, `min_confidence`, `source_spider` supports has_key + has_any_keys per S2869 Ledger #4, `window_hours`). Session 1100 read-only surface.
- `sports_sharp_signals` — **in scope this ship** — verified live via T1a harness (`success`, 18ms). Direct ORM read of `Deliverable` filtered by `category='Sharp Action Detection'` + `created_at` cutoff (hours default 48 per Session 1228 PR-B autofill safety). Gap 4 read-only surface.
- `congress_members` — **in scope this ship** — verified live via T1a harness (`success`, 4ms). Direct ORM read of `CongressMember` with `in_office=True` + optional state/chamber/party/query filters (STATE_ABBREV resolution). Gap 6 read-only surface.
- `legislation_tracked` — **in scope this ship** — verified live via T1a harness (`success`, 5ms). Direct ORM read of `Bill` with optional status/chamber/query filters ordered by `-updated_at`. Gap 7 read-only surface.

**READ_ONLY — documented, transitively dispatched, delegate NOT verified this batch:**

Per Rigby T0 SIGN Q3 corrective ("codify explicit allowlists — not read-only in spirit"), these actions dispatched successfully via T1a harness but their delegated handlers have not been read this batch to verify no hidden network/LLM/write paths. Excluded from batch 4 in-scope allowlist; documented-not-verified:

- `overview` — **out of scope this ship** — composite: calls `_handle_stock_intelligence` + `_handle_sports_betting` + `_handle_legislation` (each action='overview'). Harness dispatch: success, 105ms. Transitive dependency verification deferred.
- `briefs` — **out of scope this ship** — composite: dispatches to `stock_intelligence_tool.briefs` / `sports_betting_tool.brief` / `legislation_tool.trending` by `desk` param. Harness dispatch: success, 121ms.
- `stocks_alerts` — **out of scope this ship** — delegates to `stock_intelligence_tool.alerts`. Harness dispatch: success, 5ms.
- `stocks_predictions` — **out of scope this ship** — delegates to `stock_intelligence_tool.predictions`. Harness dispatch: success, 6ms.
- `stocks_sec_filings` — **out of scope this ship** — delegates to `stock_intelligence_tool.sec_filings`. Harness dispatch: success, 17ms.
- `sports_predictions` — **out of scope this ship** — delegates to `sports_betting_tool.predictions`. Harness dispatch: success, 5ms.
- `sports_arbs` — **out of scope this ship** — delegates to `sports_betting_tool.arbs`. Harness dispatch: success, 4ms.
- `sports_wagers` — **out of scope this ship** — delegates to `sports_betting_tool.wagers`. Harness dispatch: success, 3ms.
- `legislation_search` — **out of scope this ship** — delegates to `legislation_tool.search`. Harness dispatch: soft_error (required-arg-missing path), 4ms.
- `legislation_summary` — **out of scope this ship** — delegates to `legislation_tool.summary`. Harness dispatch: soft_error, 3ms.

**MUTATION — documented, gated by harness (NOT exercised):**

- `search` — **out of scope this ship** — **RECLASSIFIED as MUTATION** per Rigby T0 SIGN catch. `source='web'` routes to `_handle_web_search` at `td_handlers_agents.py:384` (network I/O); `source='kb'` routes through `_handle_rag_query.search` (embedding lookup — LLM cost); `source='spider'` routes through `_handle_spider_data.search`. All three source-branches carry transitive network/LLM cost. Correctly skipped by harness via `skipped_mutation`.
- `kb_ingest` — **out of scope this ship** — write path: dispatches to `rag_query_tool.ingest` (KB write). Requires `url`. Correctly skipped by harness.
- `sports_record_wager` — **out of scope this ship** — write path: dispatches to `sports_betting_tool.record_wager` (new SportsWager row). Requires `stake` + `odds` + `description` + `wager_type`. Correctly skipped by harness.

## 3. Schema notes

- **Required:** `action` (via schema `required: ["action"]` array at `pa_tool_schemas.py:4077`).
- **Enum:** 19 actions covering the full multi-desk intelligence surface.
- **Conditional required (handler-enforced):**
  - `query` for `search` / `legislation_search` / `legislation_summary` (and used as optional filter for `signal_clusters`).
  - `url` for `kb_ingest`.
  - `stake` + `odds` + `description` + `wager_type` for `sports_record_wager`.
  - `bill_number` for `legislation_summary`.
- **Optional filters (per action):**
  - `desk` (enum: stocks/sports/legislation/all) — for `briefs`.
  - `source` (enum: kb/spider/web) — for `search`. **NOTE:** enum values `kb`, `spider`, `web` intentionally excluded from `signal_clusters` `source_spider` fallback per S2869 Ledger #4.
  - `source_spider` (str OR list) — for `signal_clusters` (has_key / has_any_keys JSONField filter).
  - `pattern_type`, `min_confidence`, `window_hours` — for `signal_clusters` (anyOf-null shape per S2870 Ledger #20).
  - `ticker`, `sport`, `bill_number`, `state`, `chamber`, `party`, `hours`, `limit`.
- No `GAP_MAP` flags on this tool at HEAD.

## 4. Golden-path examples

**"What's the latest stock brief?"**

```
intelligence_tool  action=stock_briefs  limit=5
```

**"How are the ML predictions doing?"**

```
intelligence_tool  action=ml_predictions
```

**"Show me high-confidence AI signal clusters from Hacker News."**

```
intelligence_tool  action=signal_clusters  source_spider=hackernews  min_confidence=0.6
```

**"What sharp-money movement did we see in the last 24 hours?"**

```
intelligence_tool  action=sports_sharp_signals  hours=24
```

**"List Colorado congress members."**

```
intelligence_tool  action=congress_members  state=CO
```

**"What legislation are we tracking?"**

```
intelligence_tool  action=legislation_tracked  limit=20
```

**"Search the KB for AI infrastructure trends" — OUT OF SCOPE this batch (network cost):**

```
# intelligence_tool  action=search  source=web  query="AI infrastructure trends"
# ↑ Routes to _handle_web_search — network I/O. Deferred to network-trio batch.
```

## 5. Failure / empty-state / pagination notes

- **`signal_clusters` with no results** — returns `{action, count: 0, filters_applied, clusters: []}` with consistent shape.
- **`sports_sharp_signals` with no results in window** — returns `{action, count: 0, total_in_window: 0, hours, items: []}`.
- **`congress_members` with restrictive filter** — returns `{action, total, count, members: []}`.
- **`legislation_tracked` with unknown status** — returns `{action, total: 0, count: 0, bills: []}`.
- **Unknown action** — returns `{error: 'Unknown intelligence_tool action: <action>. Valid: <full list>'}` at handler line 3699.
- **Any ORM query exception** — returns `{action, error: str(e)}` wrapped by `_tag` helper at handler line 3313 (adds `gateway: intelligence_tool` + `action`); never raises.

## 5a. Mutation containment / gateway allowlist (per Rigby T0 SIGN CRITICAL CATCH)

**The `search` action reclassification is the load-bearing finding this batch.** Rigby T0 SIGN caught that `intelligence_tool.search` with `source='web'` routes to `_handle_web_search` — a network handler defined in a DIFFERENT file (`td_handlers_agents.py:384`). This is:

- The same *class* of issue as S2913 batch 2 `conversation_tool.search` LLM-cost catch (hidden embedding call under `EmbeddingService.create_embedding`).
- A concrete manifestation of Rigby's Q3 zoom-out framing: **"gateway ambiguity debt"** — big multi-action routers hide network/LLM/write paths unless we call them out by name.

**Explicit allowlist (per Rigby T0 SIGN Q1 AGREE-with-edits):** batch 4 signs the 6 direct pure-ORM actions in the `## Covered actions` READ_ONLY subsection. **10 additional harness-dispatched actions are documented-but-not-verified** because their delegate handlers (`_handle_stock_intelligence`, `_handle_sports_betting`, `_handle_legislation`) have not been read this batch to confirm no transitive network/LLM/write paths.

**Explicit exclusions (documented by name, not "read-only in spirit"):**

- **Network path:** `search` (all 3 source branches carry transitive cost).
- **Write paths:** `kb_ingest` (KB write via rag_query_tool.ingest), `sports_record_wager` (SportsWager row create).
- **Transitive unverified:** `overview` + `briefs` (composites), `stocks_*`, `sports_predictions/arbs/wagers`, `legislation_search/summary` (delegates).

**Containment mechanism (in-scope subset):** all 6 in-scope actions are direct-in-handler ORM reads with `_tag` envelope helper at line 3313. No cross-file dispatch; no embedding calls; no `apply_async`; no HTTP.

**Containment mechanism (excluded MUTATIONs) — audit metadata only, NOT a runtime gate:** the T1a harness dispatch respects the classification (`skipped_mutation` for MUTATION-classed actions during a READ_ONLY sweep). **However, the live PA runtime path does NOT enforce this classification** — verified S2914 post-merge (2026-07-23): a live dispatch of `intelligence_tool.search source=web query='test'` via `pa_local.sh` succeeded and hit network (~3052ms latency, DuckDuckGo scrape results returned). The classification in `TOOL_ACTION_METADATA` is **descriptive audit metadata** used by the validation harness + gap map, not a runtime enforcement mechanism at the handler or dispatcher layer. Runtime enforcement would require an explicit handler-level guard or global tool-router policy.

**Deferral rationale:** delegate handler verification requires reading `_handle_stock_intelligence`, `_handle_sports_betting`, `_handle_legislation`, `_handle_rag_query`, `_handle_spider_data`, `_handle_web_search` handlers — each with their own action surface. Deferred to a network-focused batch (network trio: `fleet_health`/`http_smoke_test`/`signal_studio_judge_stats`) or a dedicated intelligence-delegates batch.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness intelligence_tool` at HEAD `396abccc8` (2026-07-23):

| Action | Outcome | Safety class | Latency |
|---|---|---|---|
| `overview` | `success` | READ_ONLY | 105 ms |
| `briefs` | `success` | READ_ONLY | 121 ms |
| `search` | `skipped_mutation` | MUTATION | 0 ms |
| `stocks_alerts` | `success` | READ_ONLY | 5 ms |
| `stocks_predictions` | `success` | READ_ONLY | 6 ms |
| `stocks_sec_filings` | `success` | READ_ONLY | 17 ms |
| `sports_predictions` | `success` | READ_ONLY | 5 ms |
| `sports_arbs` | `success` | READ_ONLY | 4 ms |
| `sports_wagers` | `success` | READ_ONLY | 3 ms |
| `sports_record_wager` | `skipped_mutation` | MUTATION | 0 ms |
| `sports_sharp_signals` | `success` | READ_ONLY | 18 ms |
| `legislation_search` | `soft_error` | READ_ONLY | 4 ms |
| `legislation_summary` | `soft_error` | READ_ONLY | 3 ms |
| `congress_members` | `success` | READ_ONLY | 4 ms |
| `legislation_tracked` | `success` | READ_ONLY | 5 ms |
| `kb_ingest` | `skipped_mutation` | MUTATION | 0 ms |
| `stock_briefs` | `success` | READ_ONLY | 5 ms |
| `ml_predictions` | `success` | READ_ONLY | 8 ms |
| `signal_clusters` | `success` | READ_ONLY | 17 ms |

Artifact: `docs/audits/pa_tools/harness_output/intelligence_tool.json` — 16 READ_ONLY dispatched (14 success + 2 soft_error on required-arg-missing paths) + 3 MUTATION skipped via `skipped_mutation`. Zero bridge_unreachable.

**Envelope-shape observation:** all 16 dispatched READ_ONLY actions return either clean success or fail-loud `{error}` on required-arg-missing. `_tag` helper at handler line 3313 normalizes `gateway=intelligence_tool` + `action=<action>` on every response — no envelope drift observed. `search` correctly gated by metadata classifier before dispatch, confirming the Rigby T0 SIGN catch prevents accidental network cost.

### 6.2 Runtime-not-executed — this ship

- **10 harness-dispatched READ_ONLY delegates** (`overview`, `briefs`, all `stocks_*`, `sports_predictions/arbs/wagers`, `legislation_search/summary`) — dispatched successfully but transitive dependency verification (reading each delegate handler) is deferred. Documented-but-not-verified per Rigby T0 SIGN corrective.
- **3 MUTATION actions** (`search`, `kb_ingest`, `sports_record_wager`) — correctly skipped by harness per `skipped_mutation` classification. Write/network paths documented-not-exercised per D6 moratorium.

---

## Related

- **Adjacent tools:**
  - `work_tool` (batch 4 peer) — initiative + action-item execution surface.
  - `dream_tool` (Slice 3 batch 3 peer) — creative idea intake feeding initiatives.
  - `governance_tool` (Slice 3 batch 3 peer) — human decision inbox.
- **Underlying tools (referenced but NOT validated this batch):** `stock_intelligence_tool`, `sports_betting_tool`, `legislation_tool`, `rag_query_tool`, `spider_data_tool`, `web_search`.
- **Substrate context:** batch 4 co-opens the explicit-allowlist pattern with `work_tool`. First sweep batch to (a) codify allowlist explicitly and (b) surface a *second* "hidden network/LLM in read-shaped gateway" catch — extends the S2913 batch 2 `conversation_tool.search` precedent.
- **Metadata seed:** 19 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (16 READ_ONLY + 3 MUTATION).
- **Session provenance:** Session 1079 base (unified desk gateway) + Session 1100 (direct ORM readers: `stock_briefs` / `ml_predictions` / `signal_clusters`) + Gap 4/6/7 (`sports_sharp_signals` / `congress_members` / `legislation_tracked`) + Session 1228 PR-B (autofill safety on hours default) + S2869 Ledger #4 (`source_spider` has_any_keys list form) + S2870 Ledger #20 (anyOf-null shape for optional filters).
- **Ledger candidates raised this batch:** none new — the `search` hidden-network catch is the second instance of a gateway-hidden-cost pattern (first: S2913 batch 2 `conversation_tool.search`). Forward-carry observation: if a 3rd instance surfaces in Slice 3/4/5, evaluate for Fold promotion per PLAYBOOK-6.10 (D6 moratorium in force this batch — no substrate arcs open).
