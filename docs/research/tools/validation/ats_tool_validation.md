# `ats_tool` — Validation Report (S2919)

**Tool:** `ats_tool`
**Schema:** `core/services/pa_tool_schemas.py:5021`
**Handler:** `core/services/td_handlers_gateway.py:2600` (`_handle_ats`)
**Register site:** `core/services/tool_dispatcher.py:590`
**Session:** S2919 (Slice 4 batch 2 — gateway small-tier read-only quartet: discord + distribution + ats + narrative)
**HEAD at validation:** `12d3114b9` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2919 T0 SIGN AGREE — batch-1 pure-read template preserved; span 93 lines to EOF; 0/3 Appendix A/N first-hop literals in span 2600-2693; 0/4 mutation verbs (pure ORM SELECT + Sum/Avg/Count aggregate).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`ats_tool` surfaces resume/ATS-optimization telemetry from three tables: `ATSKeywordMapping` (canonical keywords with frequency stats and interview-correlation scores), `ResumeOptimizationLog` (per-user resume optimization runs with initial/final ATS scores + revenue), and `PersonaResumeTemplate` (marketable resume templates by industry/experience level). Use it when the operator asks "which keywords correlate with interviews?" / "how much has my resume improved?" / "what templates are on sale?" / "aggregate ATS revenue?".

Distinct from `campaign_tool` (client campaigns, not resume optimization), from `deliverable_tool` (content deliverables, not resume artifacts), and from `analytics_tool` (behavioral events, not ATS-specific metrics).

## Covered actions

- `keywords` — **in scope this ship** — lists `ATSKeywordMapping` rows ordered by `-job_frequency` (highest-demand first). Supports `category` filter. Returns `{action, count, keywords: [{id, canonical, category, variations, resume_frequency, job_frequency, interview_correlation}]}`. Note `variations` is truncated to first 3 elements at line 2622.
- `optimizations` — **in scope this ship** — lists `ResumeOptimizationLog` rows ordered by `-created_at`. Auto-scopes to `user_id`. Returns `{action, count, optimizations: [{id, job_title_target, industry, initial_ats_score, final_ats_score, current_stage, revenue_cents}]}`.
- `templates` — **in scope this ship** — lists `PersonaResumeTemplate` rows filtered by `is_active=True`, ordered by `name`. Returns `{action, count, templates: [{id, name, industry, experience_level, template_type, price_cents, avg_ats_score_improvement}]}`.
- `stats` — **in scope this ship** — default action; system-wide keyword count + user-scoped optimization aggregate. Returns `{action, total_keywords, total_optimizations, avg_score_improvement, total_revenue_cents, active_templates}` — no shared "results" key.

Default action = `stats` (per `payload.get('action', 'stats')` at handler line 2602).

## 3. Schema notes

- **Required:** `action` (enum: `keywords` / `optimizations` / `templates` / `stats`).
- **Optional:** `category` (string — only applied on `keywords` action; silently ignored on other actions), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 2603; applies to `keywords` / `optimizations` / `templates` — `stats` returns full-window aggregate).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:5019-5045`.
- **Envelope shape asymmetry:** 3 list actions return `{action, count, <domain_key>: [...]}` with distinct `keywords` / `optimizations` / `templates` list keys; `stats` returns 5 top-level rollup fields (no `count`). Consumers keying on `count` must handle its absence for `stats`.
- **`variations` truncation:** `keywords` action silently truncates each row's `variations` list to first 3 elements at line 2622. Not schema-declared; consumers wanting full variations must direct-ORM.
- **`avg_score_improvement` short-circuit:** `stats` action computes improvement only if both `avg_init` and `avg_final` are truthy (line 2676); returns `None` if either is null. Silent nil-safety.

## 4. Golden-path examples

**Example 1 — aggregate ATS stats (most operator-common):**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_keywords": <int>, "total_optimizations": <int>, "avg_score_improvement": <float|null>, "total_revenue_cents": <int>, "active_templates": <int>}`.

**Example 2 — top keywords by job frequency (technical category):**
```json
{"action": "keywords", "category": "technical", "limit": 15}
```
Expected envelope: `{"action": "keywords", "count": <int ≤ 50>, "keywords": [{"id": ..., "canonical": "python", "category": "technical", "variations": ["...", "...", "..."], "resume_frequency": <float>, "job_frequency": <float>, "interview_correlation": <float>}, ...]}` — sorted desc by `job_frequency`.

**Example 3 — recent user resume optimizations:**
```json
{"action": "optimizations", "limit": 10}
```
Expected envelope: `{"action": "optimizations", "count": <int ≤ 50>, "optimizations": [{"id": ..., "job_title_target": "...", "industry": "...", "initial_ats_score": <float>, "final_ats_score": <float>, "current_stage": "...", "revenue_cents": <int>}, ...]}`.

**Example 4 — active persona templates:**
```json
{"action": "templates", "limit": 20}
```
Expected envelope: `{"action": "templates", "count": <int ≤ 50>, "templates": [{"id": ..., "name": "...", "industry": "...", "experience_level": "...", "template_type": "...", "price_cents": <int>, "avg_ats_score_improvement": <float|null>}, ...]}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown ats_tool action: <action>"}` at handler line 2686. Not raised — in-envelope.
- **Handler exception:** caught at line 2688, logged via `logger.error(..., exc_info=True)` (ATS log stream), returns `{"error": <str>}`. No `error_code` field — **legacy-error envelope** (11th corroborating instance; batch-2 continues broadening the different-tool-block footprint).
- **Empty result set:** returns `count: 0` + empty list (for list actions) or zero-valued aggregate (for `stats`). No error.
- **`category` filter ignored on non-`keywords` actions:** silent. Corroborates the distribution_tool `status` and audit_tool `status` silent-ignore pattern — 3rd instance of "schema param declared but ignored on subset of actions" → **triggers evaluation** (was 2/3 at S2918 with analytics_tool `role` + audit_tool `status` on `citations`; this is 3rd).
- **`limit` hard cap:** 50.
- **`variations` truncated to 3:** undocumented in schema; consumers should know they're seeing a summary, not the full variation list.
- **`stats` mixes system-wide and user-scoped counts:** `total_keywords` and `active_templates` are system-wide (no `user_id` filter); `total_optimizations` and revenue/score aggregates are user-scoped. Not incorrect per model semantics (keywords/templates are canonical resources; optimizations are per-user), but a discoverability sharp edge.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ATSKeywordMapping.objects.order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:2610-2614, 2665, 2679` | ORM SELECT; documented |
| `ResumeOptimizationLog.objects.order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:2630-2633, 2666-2668, 2680` | ORM SELECT; documented |
| `PersonaResumeTemplate.objects.filter(is_active=True)` | `read` | `td_handlers_gateway.py:2649, 2683` | ORM SELECT; documented |
| `opts.aggregate(Sum, Avg)` | `read` | `td_handlers_gateway.py:2669-2673` | ORM AGGREGATE; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2919 T0 SIGN Q2 per-tool confirmation: ats span 2600-2693 contains none of these literals — grep receipts in Rigby T0 SIGN turn 3.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2919 handoff. Expected shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `campaign_tool` (client campaigns) — batch 1; `analytics_tool` (behavioral events) — batch 1; `deliverable_tool` (content search, not resumes).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_ats_optimization.py` (`ATSKeywordMapping`, `ResumeOptimizationLog`, `PersonaResumeTemplate`).
- **Prior ratifications:** S2892 Path B open, S2918 Slice 4 batch 1 (analytics/audit/campaign/experiment quartet — same gateway ORM-direct shape).
- **Ledger rows relevant to this ship:**
  - **Schema-drift "param declared but ignored on subset of actions" — 3rd instance** — analytics_tool `role` (S2918) + audit_tool `status` on `citations` (S2918) + ats_tool `category` on non-`keywords` actions. Meets 3/3 threshold per 00-START forbidden-list — **triggers evaluation** for candidate promotion.
  - **Legacy-error envelope 11th instance** — continued corroboration in batch-2 different-tool-block. Still gated on explicit Chris directive per 00-START forbidden-list.
  - **`variations` truncation-to-3 undeclared in schema** — usability sharp edge; candidate for future post-D6 doc-fix ratification.
