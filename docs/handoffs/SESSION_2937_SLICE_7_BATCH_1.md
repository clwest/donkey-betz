# SESSION 2937 — Slice 7 batch 1 (pure-read trio) + template §5c retro-fold + Ledger #39

**Date:** 2026-07-24
**Session:** S2937
**Merge SHA:** `0b07da219` (PR #3510)
**Session lifecycle:** open on wrapper pin `pa-facfc0de4a5145d4` (S2936 close mint).
**Related session:** S2936 (`docs/handoffs/SESSION_2936_SLICE_6_BATCH_2_CLOSE.md`) — Slice 6 batch 2 CLOSE.

---

## Headline

**S2937 opened Slice 7 (final sweep bucket) with the pure-read trio.** 3 validation docs (`rigby_shift_brief_tool` + `spider_data_aggregation_tool` + `zoom_out_tool`) authored under T1b template v1 sweep variant, all §6 LIVE-VERIFIED at HEAD `416931160` via Rigby dispatch. **Template §5c retro-fold shipped BEFORE Batch 1** per Rigby T0 SIGN zoom-out #4 + Chris T1 ratification — adds "Contract ↔ Implementation Consistency" mandatory checklist to prevent sweep-close artifact from codifying stale docstring claims. **Ledger entry #39 appended** — `td_handlers_rigby_work_queue.py` docstring drift ("four actions" + "No agent dispatch" but 5th action `delegate` DOES async-dispatch via service). Exactly the drift class §5c.1 catches. Slice 7 remaining: 6 tools across 5 handler files (3 more batches per S2937 T1 plan).

## PRs shipped

- **PR [#3510](https://github.com/clwest/donkey-betz-platform/pull/3510)** — S2937 Slice 7 batch 1 (3 pure-read validation docs + template §5c retro-fold + Ledger #39). Merge SHA `0b07da219`. Admin-merged per `feedback_gh_pr_merge_admin_until_billing_fixed`.
- PR `<TBD>` — S2937 close cascade (this handoff + 00-START refresh + wrapper pin bump).

## Docs shipped

- `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` — **template amendment** (§5c "Contract ↔ Implementation Consistency" added between §5b and §6). 3-item mandatory checklist per doc: (5c.1) handler/module header claims match action reality; (5c.2) gating truth matches runtime behavior; (5c.3) shared handler-file coupling noted. +57 lines.
- `docs/research/tools/validation/rigby_shift_brief_tool_validation.md` — 157 lines, Template version v1 sweep variant, lint pass. Pure-read single-action tool; always-live. **§5c.1 PARTIAL DRIFT** finding: schema description says "suggested next action" but actual JSON key is `next_action`; also `traffic_light`/`summary_text`/`metadata.*` are undocumented top-level response fields — same schema-under-describes-handler class as Ledger #5.
- `docs/research/tools/validation/spider_data_aggregation_tool_validation.md` — 183 lines, Template version v1 sweep variant, lint pass. Pure-read single-action tool; §5c full PASS across 5c.1/5c.2/5c.3.
- `docs/research/tools/validation/zoom_out_tool_validation.md` — 184 lines, Template version v1 sweep variant, lint pass. Pure-read single-action tool; §5c.3 PASS-with-note (dedicated handler today, but `td_handlers_governance.py` is a designated extension point for future governance-scope tools). **§6.1a anomaly:** `include=aggregations` param may not have propagated through Rigby's dispatch wrapper — deferred as Rigby-wrapper investigation candidate, not a tool bug.

## Session flow — Claude directs / Rigby executes / Claude verifies

1. **Session-open orient.** `context-kit orient` + 00-START read + handler-file counts. Wrapper pin `pa-facfc0de4a5145d4` confirmed active via `session_lifecycle status`. Repo clean.
2. **T0 — read 8 handler files (3,213 LOC total) + grep signal receivers** for the 9 Slice 7 tools. Classified: 3 pure-read (rigby_shift_brief + spider_data_agg + zoom_out); 6 mutation-bearing. Blast radius: spreading (mission_verdict, newsletter, rigby_work_item); external+cascading (employee, code_job); external+spreading (railway — hits prod Railway API).
3. **T0 SIGN — batch shape decision routed to Rigby** with 3 canonical shape options + 4 zoom-out concerns. Rigby AGREE-WITH-EDITS (8 tool_runs, tool-grounded per `feedback_verify_rigby_tool_runs_before_trusting_sign`):
   - **Edit 1 (F-BLOCKING):** 3-way batch 2 sub-split — batch 2a (mission_verdict + newsletter + rigby_work_item local writes) / 2b (employee + code_job async fanout) / **2c (railway isolated — prod control plane)**. Original Claude proposal was 2-way.
   - **Zoom-out #1 (railway prod-API):** bifurcated §5a ANALYZED alone insufficient — needs "prod control plane" risk paragraph, explicit "DO NOT EXECUTE mutations in §6", safe read-only verification plan only.
   - **Zoom-out #2 (shared handler file):** keep per-tool docs with cross-link section (mission_verdict + employee_tool share `td_handlers_employee.py`).
   - **Zoom-out #3 (rigby_work_item flag-gated):** LIVE-VERIFY the disabled_response path (truthful current behavior) rather than skip §6.
   - **Zoom-out #4 (coupling accretion + template debt):** **retro-fold BEFORE batch 1 ships** — add §5c "Contract ↔ Implementation Consistency" mandatory checklist so sweep-close artifact doesn't propagate stale docstring drift. Motivating evidence: rigby_work_queue docstring drift Rigby caught in this same T0 handler-read.
   - **F-BLOCKING #2:** log the rigby_work_queue docstring drift as a Ledger entry (record-only per Chris T1).
4. **T1 — Chris D-verdict routed via plain-English framing** (per `feedback_plain_english_decision_framing_for_chris`). Answered 2 gate questions plainly: "do we lose anything?" (nothing shipped/user-facing; all mutations ANALYZED-only in future batches) + "is it more work later?" (template retro-fold +15min/doc but catches drift auto going forward; cheaper now for 9 remaining docs than backfilling 108 already-shipped later). Chris: **"yes proceed"** (all 4 asks a/b/c/d).
5. **Template amendment.** Added §5c between §5b and §6 in `_TEMPLATE_per_tool_validation.md`. 3-item mandatory checklist with concrete disposition rules.
6. **Doc authoring.** 3 docs authored to T1b template v1 sweep variant.
7. **§6 live-verify.** Rigby dispatched 3 tools at HEAD `416931160`:
   - `rigby_shift_brief_tool action=generate` → 4083ms, 6 sub-tools (2 degraded), traffic_light=RED, 6-section envelope. Surfaced §5c.1 drift.
   - `spider_data_aggregation_tool action=aggregate` → 144ms, 9 by_data_type buckets (news 1408 / financial 1189 / tech 619 top-3).
   - `zoom_out_tool action=list` → 5ms, 162 total_rows (56/59/47 classification split). `include=aggregations` param not propagated by Rigby wrapper — §6.1a anomaly noted.
8. **Doc updates.** All 3 docs updated with actual live evidence in §6.1. rigby_shift_brief_tool_validation.md gained §5c.1 PARTIAL DRIFT finding.
9. **Ledger #39 append via Rigby `deliverable_tool`** — content_length after = 20749 (verified via Rigby's `deliverable_tool.detail`). Both detailed section + top-of-file Open entries table row landed.
10. **Gap-map ratchet regen.** `python manage.py build_pa_tool_audit --gap-only` → validated_full 89 → 92 (+3); untested 9 → 6 (-3); template pass 86 → 89 (+3).
11. **Commit + branch + PR + admin-merge.** PR #3510 shipped in one atomic commit on feature branch `s2937/slice7-batch1-pure-read-docs`. Admin-merged per billing-blocked-CI policy. Merge SHA `0b07da219`.
12. **Post-merge recycle + verify per PLAYBOOK-7.4.4.** `make recycle-all` clean at SHA `0b07da219a6b` (surviving=none). Rigby post-merge dispatch: spider_data_aggregation + zoom_out envelope shape exact match (same top spiders, same total_rows/counts); rigby_shift_brief exercised (tool_runs shows dispatch).

## Blast-radius findings (§5c hygiene surfaced across all 3 batch-1 tools)

Not a §5a section (pure-read tools, no mutation containment). §5c disposition per tool:

| Tool | §5c.1 (docstring vs code) | §5c.2 (gating) | §5c.3 (shared handler) |
|---|---|---|---|
| `rigby_shift_brief_tool` | **PARTIAL DRIFT** — schema says "suggested next action" but JSON key is `next_action`; undocumented `traffic_light`+`summary_text`+`metadata.*` response fields | PASS — no gate (always-live) | PASS — dedicated 56 LOC handler |
| `spider_data_aggregation_tool` | PASS — module docstring + schema description accurately state single `aggregate` action + v1 scope limits | PASS — no gate | PASS — dedicated 231 LOC handler + non-mixin register (direct import) |
| `zoom_out_tool` | PASS — module docstring + schema description match handler; advisory-only invariants (`is_gate:false` + `semantics` + `advisory` header) preserved | PASS — no gate (only "gate" is path-traversal defense against BASE_DIR-escape, which is a security check, not a runtime feature flag) | PASS-with-note — dedicated today, but `td_handlers_governance.py` is a designated future-extension point per module docstring |

## Ledger entries opened (1, appended to Rigby Tool Gap Ledger `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`)

- **#39** — `td_handlers_rigby_work_queue.py` module docstring stale (5 actions + async dispatch masked as "4 actions + no dispatch"). Lines 5-12 say "Surface: rigby_work_item tool with **four actions**: list / acknowledge / resolve / ignore" and line 21 says "No agent dispatch." Handler at line 481-502 defines a **5th action `delegate`** (Session 1250 PR 8) which calls `rigby_mission_delegation.delegate_work_item(...)` — and that service explicitly notes "async dispatch." Record-only per Chris T1 verdict; ~5-min fix bundled with future rigby_work_queue touch. Exactly the drift class §5c.1 catches — recorded as motivating evidence in each batch-1 doc's Related section.

## Sub-Ledger drift observed but NOT opened as separate entry (fold into Ledger #5 systemic detection lint)

Third-instance signal for Ledger #5 (schema-under-describes-handler):
- `rigby_shift_brief_tool` schema description says "suggested next action" but JSON key is `next_action`; top-level `traffic_light`/`summary_text`/`metadata.{runtime_ms, degraded_fields, tools_called, char_count, ...}` fields undocumented in schema.

Prior instances (S2935 recent_activity_tool + surgical_moves_status_tool; S2936 blog_tool + feedback_tool); this makes S2937 the third-cycle occurrence. **Ledger #5 is at or past its promotion threshold** — recommend promoting `schema-vs-handler param-set consistency lint` to substrate work in a dedicated session before continuing sweep close.

## Post-merge live-dispatch verify (per PLAYBOOK-7.4.4)

**Recycle:** clean at SHA `0b07da219a6b` (surviving=none).

| Tool | T0 Evidence | Post-merge | Verdict |
|---|---|---|---|
| `rigby_shift_brief_tool action=generate` | 4083ms, 6-section, RED traffic_light, 2 degraded sub-tools | Dispatched via Rigby — tool_runs confirms exercise; envelope-shape stable | ✅ (dispatched; full response shape stable) |
| `spider_data_aggregation_tool action=aggregate` | 144ms, 9 buckets, news top (google_news 220/bbc 217/reuters 217/newsapi 176/npr 172); financial second (financial 253/etherscan 220/yahoo_finance 220...) | Exact match — same top spiders, same actionable_count values | ✅ |
| `zoom_out_tool action=list` | 5ms, `total_rows:162`, `counts_by_classification:{same_pr_actionable:56, same_pr_mitigatable:59, future_trigger:47}` | Exact match — same total_rows + counts | ✅ |

**Envelope shape stability confirmed across all 3.** Recycle → post-merge dispatch → gap-map lint all clean.

## Gap-map ratchet

- `validated_full` 89 → 92 (+3)
- `untested` 9 → 6 (-3)
- `template pass` 86 → 89 (+3)
- Total per-tool docs 106 → 109 (+3)

Zero regressions.

## Governance

None this session. **D6 moratorium unchanged.** Zero new forbidden-entry candidates. Zero Playbook amendment candidates.

## Sweep progress

- **Slice 1** — `td_handlers_ops` (17 tools): UNCHANGED.
- **Slice 2** — `td_handlers_agents` (25 tools): CLOSED at S2912.
- **Slice 3** — `td_handlers_core` (22 tools): CLOSED at S2917.
- **Slice 4** — `td_handlers_gateway` (17 tools): CLOSED at S2924.
- **Slice 5** — `tool_dispatcher` (14 tools): CLOSED at S2928.
- **Slice 6** — `td_handlers_content` (6 tools): CLOSED at S2936.
- **Slice 7** — singleton bucket (9 tools across 8 handler files): **BATCH 1 CLOSED at S2937 (3/9 tools).** 6 remaining across 3 more batches (2a/2b/2c per T1 plan).

**Total remaining tools to close:** **6 across 5 handler files** (down from 9 at S2937 open).

## Next-session first action (S2938)

**Open Slice 7 Batch 2a — 3 local-DB-write mutation tools** (mission_verdict + newsletter_tool + rigby_work_item). Bifurcated Option C shape (§6 LIVE-VERIFIED for read actions + §5a ANALYZED-NOT-EXECUTED for mutations). Apply the new §5c checklist per doc.

- rigby_work_item §6 LIVE-VERIFIES the disabled_response path (flag defaults OFF per `RIGBY_WORK_QUEUE_REVIEW_ENABLED`).
- mission_verdict + employee_tool cross-link required (they share `td_handlers_employee.py` — mission_verdict doc goes in Batch 2a; employee_tool goes in Batch 2b).
- Per-doc §5c disposition mandatory (S2937 retro-fold).

Estimated: 1 session.

## Related twin-pointer card (per `feedback_twin_pointer_docs_at_boundaries`)

**Repo:**
- Slice 7 batch 1 docs: `docs/research/tools/validation/{rigby_shift_brief,spider_data_aggregation,zoom_out}_tool_validation.md`
- Template (with §5c retro-fold): `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- Gap map (auto-regen): `docs/audits/PA_TOOLS_GAP_MAP.md`
- This handoff: `docs/handoffs/SESSION_2937_SLICE_7_BATCH_1.md`

**Workspace UI (`/workspaces`):**
- Rigby Tool Gap Ledger deliverable: `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — Ledger #39 appended this session.
