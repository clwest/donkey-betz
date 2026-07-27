---
session: 2989
date: 2026-07-27
head_at_close: d45d8a954 (Phase B merge; docs cascade PR TBD)
prs_merged:
  - "#3638 — fix(s2989): Send-to-Rigby deliverable link — dead route → real workspace tab (f3337f8e9)"
  - "#3639 — feat(s2989): Phase A — Send-to-Rigby spec-shape body (9c17a4775)"
  - "#3640 — feat(s2989): Phase B — Audit Findings surface for docs/research/ (d45d8a954)"
shape: chris_directs → claude_executes → chris_verifies → rigby_pushback_loop_at_design_gate
rigby_sign_cycles: 1 (Phase A + B combined pre-code design review; folds F-A1/A2/A3 + F-B1/B2/B3 all applied inline)
recycle_state: clean at sha=d45d8a954ac6
close_shape: docs_cascade_pending
---

# Session 2989 — Send-to-Rigby spec-shape (Phase A) + Audit Findings surface (Phase B)

## Session shape

S2989 opened as a Chris visual-verify check on S2988's per-bullet Send-to-Rigby button. Chris found a dead link (blank screen on the "Sent — deliverable" hyperlink). One-line fix shipped as PR #3638.

Chris then reframed the ask: "the deliverable I clicked on wasn't looking how I was thinking." His mental model for Send-to-Rigby was NOT "log the bullet as a note" but "package the bullet into an execution-ready spec that Claude can pick up next session" — same shape S2988's ratification deliverables had. He also asked for the audit-triage loop this implies: browse docs/research/, spot open findings, hand them to Rigby, work them off systematically.

Chris chose **A now + B queued but same-day**. Rigby was looped in at the design gate BEFORE any code was written; her pushback (7 substantive concerns across Phase A + B) landed inline as folds F-A1/A2/A3 (spec-generator hardening) + F-B1/B2/B3 (findings surface constraints). Chris ratified the resulting scope with one adjustment (include `implementation/IMPLEMENTATION_DEBT.md`).

Three feature PRs shipped in ~3 hours of continuous work. Post-ship Chris visual-verified a real spec deliverable (`Half-wired drf-spectacular` finding via IDBT-adjacent surface) and confirmed the shape matches his mental model.

## PR #3638 — dead-URL fix (`f3337f8e9`)

Send-to-Rigby "Sent — deliverable" link in `frontend/src/components/platform/CanonicalBriefing.tsx:145` pointed at `/workspaces/{workspaceId}/deliverables/{deliverableId}` (plural, path-style). No such route in `App.tsx` — real client routes are `/workspace/:workspaceId` (dashboard) or `/workspace?tab=deliverables&workspace=…` (query-string). React Router matched nothing → blank screen.

One-line fix to the query-string pattern already used at `WorkspaceDashboardPage.tsx:474,653,828`. Verified in rebuilt bundle: `DocumentViewer-DPPq6BLH.js` now contains the new href.

## PR #3639 — Phase A: Send-to-Rigby spec-shape body (`9c17a4775`)

New module `core/services/briefing_spec_generator.py` — direct `gpt-5-mini` call with `response_format=json_object`, strict schema validation, per-field char caps, fail-open placeholder shape.

**Spec sections rendered:**
- `## Goal` — 1 sentence, imperative
- `## Context` — 2-3 sentences grounded in citations
- `## Open question` — 1 sentence or "None"
- `## Files implicated` — list of `{path, source: citation|inferred}`
- `## Acceptance criteria` — 3-5 imperative bullets
- `## Warnings` — only when degradation occurred
- `## Evidence` — verbatim source + citations

**Endpoint update:** `POST /api/repo/canonical-briefing/send-to-rigby/` now calls `generate_spec_body` and merges `spec_extras` into Deliverable metadata (`llm_success`, `spec_schema_version=SPEC_V1`, `spec_prompt_version`, `spec_warnings`, `llm_failure_reason` on fail-open).

**Rigby SIGN Cycle 1 folds applied inline:**
- **F-A1** — strict schema validation + fallback preserves section layout so downstream never sees a shape drift on LLM failure.
- **F-A2** — `files_implicated` entries claiming `source=citation` MUST match a path in the incoming citations allowlist; violators downgrade to `source=inferred` (+ warning) rather than hallucinate code paths.
- **F-A3** — per-field char caps (goal 300, context 800, open_question 300, per-file 200, per-AC 200); truncation surfaces in `warnings[]`.

**Tests:** 21 existing + 2 new = **23/23 pass in ~0.8s.** New tests cover fail-open shape preservation and file-source downgrade behavior.

## PR #3640 — Phase B: Audit Findings surface (`d45d8a954`)

New Workspace → Intelligence → **Findings** sub-tab backed by `DocResearchFinding` model + 900-row ingest of `docs/research/`.

**Backend:**
- `core/models_audit_findings.py::DocResearchFinding` — named distinctly from the pre-existing security-audit `AuditFinding` in `models_audit_tracking.py`. Fields: `doc_path`, `domain_slug`, `source_type` (audit|canonical_summary|implementation_debt), `source_heading`, `text`, `text_hash` (sha256 uniqueness), `confidence` (high|medium|low), `tags`, `status` (open|fixed|dismissed), `resolved_at`, `resolved_by`, `resolution_note`, `deliverable_id`, `first_seen_at`/`last_seen_at`, `metadata`. Uniqueness `(doc_path, text_hash)`.
- Migration `0398_s2989_doc_research_finding.py` — hand-written minimal so `makemigrations` autopick didn't sweep unrelated schema drift (haidispatchlog + narrative* + spider*).
- `python manage.py index_doc_research_findings [--dry-run] [--verbose]` — walks narrow v1 scope; upserts by `(doc_path, text_hash)`; findings that disappear from source are NOT deleted (`last_seen_at` stays stale to preserve status history).

**v1 ingest scope (Rigby F-B3):**
- `docs/research/domains/**/*_canonical_summary.md`
- `docs/research/domains/**/*_audit.md`
- `docs/research/implementation/IMPLEMENTATION_DEBT.md` (special-parse: only `status: ACTIVE` rows)

Section header allowlist covers Known Drift, Technical Debt, Boundary Violations, Duplicate or Overlapping Systems, Ownership Gaps, Recommended Future Research, Recommendations, Follow-on Research Queue, Follow-ups, Open items, Next Actions, Unresolved Unknowns, Anchor-Update Recommendations, Action items.

**Skipped for v1** (widen later if signal missed): `BACKLOG.md` (needs its own IOS-schema parser), `implementation/*/` subfolders (design-prep, noisier), `RATIFICATION_*.md` (history), `platform/`, `process/`, `tools/`, `domains/*_scoping.md`.

**Confidence heuristic:** `Next Actions` / `Follow-ups` / `Recommendations` → high; `Boundary Violations` / `Known Drift` / `Unresolved` → low; everything else medium. IDBT rows land as high.

**Live ingest (verified):** 909 findings parsed → 900 created (9 dedup on first re-run). 2 IDBT-active, 65 canonical-summary, 833 audit. Confidence: 90 high / 255 medium / 555 low.

**Endpoints** (`core/views_doc_research_findings.py`):
- `GET  /api/repo/doc-research-findings/` — list; filters `status`, `domain_slug`, `source_type`, `confidence`, `min_confidence`, `search`, pagination (`page`, `page_size` max 200).
- `POST /api/repo/doc-research-findings/<uuid>/mark/` — status change with note; auto-sets `resolved_at` + `resolved_by`.
- `POST /api/repo/doc-research-findings/<uuid>/send-to-rigby/` — routes finding through Phase A `generate_spec_body`; creates `briefing_action_item` Deliverable in Donkey Betz workspace; stores `deliverable_id` on finding.

All three DRF `@api_view + IsAuthenticated` for JSON auth failures (not 302 HTML redirect).

**Frontend** — `FindingsTab.tsx` under Intelligence → Findings. Filters (status / source / min-confidence / domain / search). Per-row actions (mark fixed, dismiss, reopen, send to Rigby). Expandable rows show section, tags, resolution note, deliverable back-link. Pagination. Toast notifications on mark/send.

**Rigby SIGN Cycle 1 folds applied inline:**
- **F-B1** — `DocResearchFinding` rows are the single source of truth for status; doc `RESOLVED-BY:` markers deliberately NOT parsed in v1 to avoid dual-authority.
- **F-B2** — every finding tagged with `confidence` + `source_heading`; UI defaults to `min_confidence=medium` so noisy sections don't dominate.
- **F-B3** — narrow v1 scope enforced at ingest layer, not the model — widening = single management-command change, no schema churn.

## Post-merge live verify

Chris visual-verified the shipped spec shape via a real send: finding `4b92f6f0-b84b-47d1-976a-30246f3dbd3d` ("Half-wired drf-spectacular" from `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md::Known Technical Debt`) → Deliverable `9d5134ab-b454-431a-93fa-7f32f2deef82`.

Verified fields:
- `deliverable_type=briefing_action_item`, `category=research_followup`, `diagnostic_status=None`
- `llm_success=true`, `spec_warnings=[]`, `spec_schema_version=SPEC_V1`
- Goal: "Resolve the half-wired drf-spectacular configuration so downstream frontend type-generation succeeds."
- Files implicated: 1 citation-sourced (source doc path) + 2 inferred (`core/settings.py`, `core/urls.py`) correctly tagged `_inferred — verify_`. F-A2 held perfectly — LLM inferred plausible paths from bullet text but didn't hallucinate them as citation-backed.
- Acceptance criteria: 5 concrete testable items covering both fork branches (enable fully vs remove partial config).

Chris quote: "That looks a lot better I think!!"

## Open follow-ups for S2990+

- **Findings — first real use loop** (highest-leverage seed for S2990). Chris picks 3-5 high-confidence findings, sends each to Rigby, and Claude executes them next session. Loop closes when findings marked fixed via UI.
- **v2 ingest scope widening** — add `implementation/BACKLOG.md` parser once we understand IOS schema structure well enough to filter for still-actionable rows (skip SHIPPED / LOCAL_ACCEPTED). Add `implementation/*/` design-prep subfolders once we see if Chris misses signal from them.
- **v2 UI: per-doc "explore" mode** — click a doc row to see all findings for that doc in context. Currently the tab is a flat list; grouping by doc might reduce cognitive load when triaging.
- **Rigby SIGN Cycle 2 on Phase A+B shipped state** — deferred at close; Chris said "go ahead with close cascade" instead. Would exercise a second SIGN loop against the actual shipped surface (spec quality, ingest false-positive rate, UI defaults). Trigger threshold: if Chris uses the Findings surface for 2+ sessions and hits friction, run a second SIGN.
- **F-A2 test coverage widening** — one test currently covers file-path downgrade; add a test for the `warnings[]` array being populated on truncation of goal/context/open_question/AC.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN)** — per-section "Send all", workspace routing inference from arc slug, LLM-mediated deliverable creation via Rigby's actual turn loop (currently direct-call for cost/determinism; Rigby-turn-loop is v3 if we ever want to exercise her natural-language surface for spec authoring).

Also all prior handoff open follow-ups remain (F-D3 tracker-scope wire-up, F-D2 LLM-bypass audit, `memory_hygiene_audit --apply` on 1805 cap-drift, Canonical Briefing v2 scope toggle, substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`, Rigby tool allowlist expansion, S2985 tab-strip visual check, Rigby `claude_code_tool` safeguards, S2984 arcs section visual check, systemic auth-XHR treatment, S2982 stage-doc live-dispatch smoke, PLAYBOOK-7.7.4 dry-run against sibling repo, S2980 Theme Signals UX visual check, Theme Signals Phase B who-benefits/who-loses + LLM summarizer + localStorage sub-tab persistence, Rigby Tool Gap Ledger Fold D `AgentExecution.celery_task_id` uniqueness, Fold B `future_trigger` from v0.8.0 fold-authoring evidence-admission helper, Playbook v0.9.0 + v0.10.0 front-matter `commit_sha` + `content_hash` fill).

## Constitutional context

- **Session was Chris-directed feature extension**, not spec-originated implementation. Per PLAYBOOK-7.7.2 the shape was Claude direct → execute → verify, NOT the full 9-phase spec→ship contract. Rigby SIGN routing happened at the pre-code design gate (unusual for this shape — typically SIGN is Phase 3 T1 or Phase 7 A2), which validated Rigby's advisory role even outside spec-origin flow.
- **PLAYBOOK-7.4.4 recycle-all** ran after PR #3638, #3639, #3640 respective merges. Frontend rebuild fired on #3638 + #3640 (frontend/** in HEAD range); not fired on #3639 (backend-only). Bundle hashes: pre-S2989 `index-BiC39OMh.js` → post-#3638 same → post-#3640 `index-DP_3O6RC.js`. `core/templates/index.html` in sync at close.
- **Chris "loop Rigby in" directive at mid-turn** — triggered pre-code Rigby SIGN routing that landed 7 substantive folds inline before any file was written. Reinforces `feedback_claude_directs_rigby_then_verifies` (Rigby is not just an executor; her judgment at design-time is signal).
- **Wrapper pin** — S2988 pin `pa-1f4d5585ffd14688` still active at close-cascade write time; `session_lifecycle close` will retire + mint next-session pin atomically.

## Handoff pointers

- Prior: `docs/handoffs/SESSION_2988_CANONICAL_BRIEFING_FIX_AND_SEND_TO_RIGBY.md`
- Anchors: `docs/PLATFORM_INVENTORY.md` (regenerable), `docs/PLATFORM_WHAT_IT_IS.md` (narrative)
- New source files:
  - `core/services/briefing_spec_generator.py`
  - `core/models_audit_findings.py`
  - `core/management/commands/index_doc_research_findings.py`
  - `core/views_doc_research_findings.py`
  - `frontend/src/pages/workspace/tabs/FindingsTab.tsx`
