# SESSION 2918 — Slice 4 batch 1 (gateway small-tier quartet)

**Date:** 2026-07-23
**Session pin:** `pa-5a42a3dfe5614364`
**Head at open:** `e1a09d8d0` (S2917 close)
**Head at close:** `781df0640` (batch 1) → close cascade adds handoff+00-START+wrapper bump
**PRs shipped:** [#3466](https://github.com/clwest/donkey-betz-platform/pull/3466) (batch 1) + `<TBD>` (close cascade)

---

## Headline

**Slice 4 (`td_handlers_gateway`) OPENED.** Shipped batch 1 = 4 small-tier gateway tools (analytics/audit/campaign/experiment, all ~80 lines, all pure ORM SELECT) via S2796 doc-only shape. Rigby T0 SIGN grounded in 20+ `repo_tool` receipts — zero rubber-stamp. **Appendix A (Async-Fanout) + Appendix N (Network-Preflight) declared N/A for gateway** based on 0/17 first-hop literals in `td_handlers_gateway.py` — gateway is ORM-direct dispatch shape, structurally different from Slice 3's callee-heavy first-hop tools. Post-merge live-verify clean at 4 dispatches (20ms/8ms/15ms/10ms), zero critical flags.

**Sweep progress post-S2918:** Slice 4 = 4/17. Total corpus 47 → 43 untested. Gap map: 52 full → **56 full** · 10 partial · 7 unknown · 43 untested.

---

## What shipped

### Tools (4 — Slice 4 batch 1)

- **`analytics_tool`** (`td_handlers_gateway.py:643`, 80 lines, 3 actions: `events_summary` / `atr_dashboard` / `events_query`) — DeliverableEvent counts + ATR-24h dashboard reuse of `stage3_dashboard` view via `RequestFactory`.
- **`audit_tool`** (`td_handlers_gateway.py:2128`, 82 lines, 4 actions: `findings` / `wiring_defects` / `citations` / `p0_summary`) — quality-signal reads across `AuditFinding` / `WiringDefect` / `CitationViolation`.
- **`campaign_tool`** (`td_handlers_gateway.py:2048`, 80 lines, 3 actions: `list` / `detail` / `stats`) — `Campaign` + `CampaignDeliverable` reads (mutation flows live elsewhere).
- **`experiment_tool`** (`td_handlers_gateway.py:1879`, 80 lines, 3 actions: `tests` / `results` / `stats`) — `ABTest` + `ABTestVariant` reads.

No TOOL_DEFAULTS or TOOL_ACTION_METADATA entries this batch (all pure READ_ONLY, auto-classifier upgrades docs to `validated_full`).

### Validation docs (4)

- `docs/research/tools/validation/analytics_tool_validation.md`
- `docs/research/tools/validation/audit_tool_validation.md`
- `docs/research/tools/validation/campaign_tool_validation.md`
- `docs/research/tools/validation/experiment_tool_validation.md`

All 4 use T1b canonical template v1 sweep variant (per S2904 ship-shape ratification).

### Regenerated docs

- `docs/PA_TOOL_AUDIT.md` (161 tools · 117 schemas · 160 handlers)
- `docs/audits/PA_TOOLS_GAP_MAP.md` (56 full · 10 partial · 7 unknown · 43 untested)

---

## Rigby joint SIGN (2-turn cycle + zoom-out, zero rubber-stamp)

### T0 SIGN turn 1 (20+ `repo_tool` runs, tool-grounded)

**Probes executed:**
- `repo_tool.search` `apply_async` in `td_handlers_gateway.py` → 0 matches
- `repo_tool.search` `httpx.get|httpx.post|requests.get|requests.post|urllib.request` in same file → 0 matches
- `repo_tool.search` `openai\.|anthropic\.|litellm\.` in same file → 0 matches
- `repo_tool.read_file` `td_handlers_gateway.py` → 2693 total lines / 132168 bytes
- `repo_tool.search` `def _handle_*` boundaries → 17 handler line-numbers captured, sizes computed via delta

**Line-density verdict (small → large):**
- ~80 lines (batch-1 candidates): analytics (80) · experiment (80) · campaign (80) · vip_invite (81) · audit (82) · conceptforge (84) · calendar (86) · podcast (89)
- ~91-93 lines: discord · distribution · ats
- ~107-127 lines: narrative · self_awareness · mobile
- ~140-188 lines: proactive · profile
- **cockpit: 431 lines** — 5× the next-largest, isolated for future dedicated batch

**Q1 verdict AGREE-with-edits:** mixed pilot pick (analytics + audit + campaign + experiment) over pure all-reads — grounded in probe 2 line-density cluster and S2914 "mixed pilot better than all-write" precedent.

**Q2 verdict DISAGREE:** Appendix A + Appendix N declared N/A for gateway. 0/17 literals means the appendices don't scale to gateway; kept as future-carry conditional patterns for tools whose probes light up later.

### T0 SIGN turn 2 (Q3 + Q4 continuation, output-cap workaround)

**Q2 completion (with deeper probes):**
- `repo_tool.search` `campaign_service` → 0 matches (no such module)
- `repo_tool.search` `from core.services` in `td_handlers_gateway.py` → only `tool_dispatcher` + `task_notification` imports (not per-tool services)
- `repo_tool.search` in `core/views_campaign.py` for `apply_async|httpx|requests|urllib|openai|anthropic|litellm` → 0 matches
- **Action:** keep Appendix A/N as future-carry, conditional appendices, not Slice-4 defaults.

**Q3 verdict AGREE-with-edits:** All 4 doc-only S2796 shape.
- `repo_tool.search` verb-scan in campaign range for `.save()`/`.create(`/`.update(`/`.delete(` → 0 matches
- Direct read of `_handle_campaign` (2048-2126) + `_handle_experiment` (1879-1956) confirms pure ORM SELECT
- Initial "probable mutation surface" verdict on campaign/experiment walked back

**Q4 zoom-out (required per `feedback_zoom_out_ask_per_rigby_sign`):**
- **Carry forward:** probe-first discipline · line-density batching · validation doc template discipline · async hygiene pattern (kept ready)
- **Leave behind:** Appendix A/N as automatic sections (gateway shows 0/17 — writing them by default is doc drag); assuming first-hop behavior lives in handlers (gateway is composition/dispatch + ORM-direct)
- **Slice 3 pattern that broke at scale:** appendix sprawl (once appendices exist, they get copy-pasted where they don't apply)
- **Legacy-error envelope (4× at S2916/S2917):** NOT ready to promote to post-D6 substrate arc on 4 instances concentrated in 1-2 handler files. Recommendation: get one Slice 4 gateway instance in a *different tool block* first, turning "4 sightings" into a general pattern.

### Post-merge live verify (per PLAYBOOK-7.4.4)

4 live READ_ONLY dispatches, all clean:

| Tool | Action | Latency | Result |
|---|---|---|---|
| `analytics_tool` | `events_summary` (7d) | 20ms | 275 events (198 synthesis_viewed / 75 status_transition / 2 deliverable_exported); sources: pa_tool 182 / signals 53 / etc. |
| `audit_tool` | `p0_summary` | 8ms | count 0 (envelope valid) |
| `campaign_tool` | `list` (limit=5) | 15ms | count 0 (envelope valid) |
| `experiment_tool` | `stats` | 10ms | total_tests 0 (envelope valid) |

Envelope shapes match §4 golden-path expectations across all 4. SIGN AGREE — no revert.

---

## Ledger candidates surfaced this batch

- **Legacy-error envelope corroboration 5-8th instances** — extends the S2916/S2917 4× pattern across the entire quartet. All 4 tools use `{"error": str}` without `error_code` field. **Watch next Slice 4 batch for a *different tool block* instance** before opening post-D6 substrate arc (Rigby Q4 recommendation).
- **Schema-drift-fix 2nd instance** — `analytics_tool` schema declares `role` param (`"Filter by role tag (manager, recruiter, developer)"`) but handler ignores it. 1st was S2911 `reasoning_engine`. 2nd instance is signal for a candidate substrate arc.
- **Envelope-key asymmetry across actions** — `audit_tool` returns `findings`/`defects`/`violations` keys per action; `experiment_tool` returns `tests`/`test`/`total_tests` scalars. Not defect; candidate harness-lint "consistent-list-key across actions" if 3rd instance surfaces at Slice 4.
- **Multi-tenant leak candidate** — `campaign_tool.detail` + `experiment_tool.results` bypass `user_id` filter (fetch by ID globally). Under single-user pre-prod (`project_single_user_pre_prod_operating_context`) not a bug today; post-D6 evaluation candidate.
- **"Hidden network/LLM in read-shaped gateway" watch** — `analytics_tool.atr_dashboard` reuses `stage3_dashboard` view via `RequestFactory` + `AnonymousUser`. Documented-not-verified (full `stage3_dashboard` audit out of scope this ship). Would be 3rd instance if audit surfaces LLM/network (currently 2/3 with S2913 `conversation_tool.search` + S2914 `intelligence_tool.search`).

---

## Sweep progress (post-S2918)

- **Slice 4 (`td_handlers_gateway`):** 4/17 shipped (batch 1 CLOSED at 4). Remaining 13: ats · calendar · cockpit · conceptforge · discord · distribution · mobile · narrative · podcast · proactive · profile · self_awareness · vip_invite.
- **Cumulative untested:** 47 → **43** (batch 1 flipped 4 untested → validated_full via auto-classifier).
- **Gap map counts:** 52 full → **56 full** · 10 partial · 7 unknown · 43 untested.
- **Pace:** 4 tools / 1 batch / 1 session (with in-depth 2-turn T0 SIGN + probe-grounded verdicts + 4-dispatch live verify).

---

## Post-merge recycle (per PLAYBOOK-7.4.4)

Clean recycle at `sha=781df064049d`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs) + beat, zero surviving old PIDs. Recorded to `logs/recycle_events.jsonl` (S2768 N7 enriched format).

---

## S2919 open sequence

**Step 1 (required first action) — Slice 4 batch 2 T0 SIGN.** 13 remaining gateway tools. Recommend Rigby T0 SIGN routing:
- **Q1 batch composition:** Next 3-4 small-tier candidates from ~81-93 line cluster: vip_invite (81) · conceptforge (84) · calendar (86) · podcast (89). Alternative: pilot one medium-tier (narrative 107 / self_awareness 118) to test whether the ~80-line cluster generalizes.
- **Q2 continued Appendix N/A watch:** batch 1 established gateway = 0/17 literals. Confirm this holds for the next batch OR flag any tool whose deeper trace surfaces indirect fan-out (`stage3_dashboard`-style view reuse pattern).
- **Q3 shape:** doc-only S2796 remains default.
- **Q4 zoom-out:** Legacy-error envelope watch continues — is next batch a *different tool block*? Any pattern from batch 1 that broke or worked especially well?

**Alternative Step 1 candidates:**
- Cockpit-only batch (431 lines, dedicated batch shape per S2914 mutation-heavy-single-tool precedent).
- Legacy-error envelope substrate arc — **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate, waiting on different-tool-block instance per Rigby Q4).

**D6 moratorium still in force.** All strategic arcs remain gated.

---

## Anchors

- **PR:** [#3466](https://github.com/clwest/donkey-betz-platform/pull/3466) — batch 1 shipped, merged at `781df0640`.
- **T1b canonical template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (v1 sweep variant used by all 4 docs).
- **Prior session handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md` (Slice 3 CLOSE 22/22 + §5b Appendix A introduction).
- **Sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-regenerated).
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`.
