---
session: 2990
date: 2026-07-27
head_at_close: 6f78b285a (docs cascade PR TBD)
prs_merged:
  - "#3642 — feat(s2990): enable drf-spectacular — INSTALLED_APPS + schema routes (8bf4e3c2a)"
  - "#3643 — fix(s2990): make drf-spectacular schema endpoints public (ec34f772a)"
  - "#3644 — docs(s2990): API undeclared-endpoints evidence report (808c50603)"
  - "#3645 — docs(s2990): permission_classes implicit-inheritance evidence report (6f78b285a)"
shape: flow_a_findings_surface_real_use_loop — 3 findings executed end-to-end
rigby_sign_cycles: 2 (finding #2 X/Y/Z framing; finding #3 X/Y/Z framing + zoom-out)
recycle_state: clean at sha=6f78b285a
close_shape: docs_cascade_pending
findings_marked_fixed: 3 (with truthful resolution_note capturing actual close state)
---

# Session 2990 — Findings-surface first real-use loop

## Session shape

S2990 opened on **Flow A** per S2989's 00-START (real-use loop of the Audit Findings surface shipped at S2989 Phase B). Chris picked 3 findings from the surface in sequence; each was executed end-to-end (fetch spec → verify state → route to Rigby → frame to Chris → ship PR → live-verify → mark fixed). Two of the three findings uncovered concrete v2 gaps on the surface that S2989 Phase A/B did not anticipate.

## The 3 findings + shipped PRs

### Finding #1 — Half-wired drf-spectacular (executable)

- **DocResearchFinding:** `4b92f6f0-b84b-47d1-976a-30246f3dbd3d`
- **Deliverable:** `9d5134ab-b454-431a-93fa-7f32f2deef82`
- **Chris fork:** Path A (enable) over Path B (rip out)
- **Shipped:** PR #3642 (INSTALLED_APPS + REST_FRAMEWORK DEFAULT_SCHEMA_CLASS + 3 URL routes) + PR #3643 (`PUBLIC_PATHS` middleware bypass after Chris hit 401 in browser)
- **Live at:** `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/`
- **Result:** 918-path OpenAPI 3.0.3 doc, 16 `@extend_schema` decorators (all `sports/views.py`) now producing real metadata

### Finding #2 — ~1,857 undeclared endpoints (decision-evidence)

- **DocResearchFinding:** `023d3301-df86-4879-893f-8fd5b0c460c8`
- **Deliverable:** `b62c2403-fdf6-427f-bf51-2abab64cb171`
- **Rigby SIGN Cycle 1:** joint agreement on X (evidence report) + MODIFY (pinned Boundaries section). Chris caught me skipping Rigby-first on this one — corrected mid-flow.
- **Shipped:** PR #3644 — `docs/research/domains/api/2990_backend_contract_undeclared_endpoints_evidence_report.md` (185 lines)
- **Key numbers surfaced:** 1,871 URL patterns (denominator 1) vs 918 DRF-representable (denominator 2); 16/1,871 = 0.86% coverage; 438 state-changing vs 480 read-only; 121 distinct top-level modules (audit said 93 — growth since S2501)
- **Enforcement verdict deferred to:** Cat D S2504 per source audit

### Finding #3 — permission_classes implicit inheritance (decision-evidence + STALE)

- **DocResearchFinding:** `3a89fddc-7b62-4093-afaa-1a9896c540f8`
- **Deliverable:** `3fbd8098-82d8-4d27-bc3c-83f29677446f`
- **Rigby SIGN Cycle 2:** joint agreement on X + MODIFY (pinned Staleness section FIRST + forward-pointing audit addendum vs history rewrite). Loop-Rigby-first executed correctly this time.
- **Shipped:** PR #3645 — two-file scope:
  - NEW `docs/research/domains/api/2990_permission_classes_implicit_inheritance_evidence_report.md` (161 lines)
  - EDIT `docs/research/domains/api/2501_...audit.md` (+11 lines addendum under bullet #3 at line 1335-1342)
- **Staleness caught:** line refs drifted (`652-653` → `737-738`), LeagueViewSet example inverted (now DECLARES `AllowAny` at line 48), audit rate estimate 80-90% actually **2.3%** via runtime URL-resolver walk (19 of 818 DRF class-based views)
- **Full 18 in-repo implicit views enumerated** and clustered: 8 sports betting + 5 intelligence income + 5 preview infra
- **Enforcement verdict deferred to:** Cat D S2504

## Marked-fixed with truthful resolution notes

All 3 `DocResearchFinding` rows updated to `status='fixed'` via ORM (Rigby couldn't do it — `DocResearchFinding` not in `orm_inspect_tool` allowlist, `web_fetch_tool` has no session — see Rigby tool gap re-hit below). Each got a truthful `resolution_note` capturing the actual close state (`executable-fixed` / `evidence-delivered (decision pending)` / `evidence-delivered + STALE-CORRECTED`) even though the surface's only public status enum is `fixed`.

## v2 gaps surfaced on the Findings surface

Concrete retro from the 3-finding sample. **Highest-leverage adds are (1) finding-type classifier at ingest + (2) close-mode taxonomy on `DocResearchFinding.status`** — together they'd shift ~2/3 of future flows from "improvise → Rigby SIGN rescue" to "template-fit → straight-through."

### ADD

- **Finding-type classifier at ingest** (`index_doc_research_findings`). Regex signals like `Cat A boundary observation` + `Chris-D-verdict at S<NNNN> xx99` → tag `type=decision_evidence`. Signals like `blocks downstream X`, error-at-file-line → `type=executable`. Default `type=unknown`.
- **Close-mode taxonomy on `DocResearchFinding.status`.** Extend beyond `open` / `fixed` to `open` / `fixed_via_pr` / `evidence_delivered` / `deferred_to_arc` / `stale_reverify_required` / `informational`. Migration + UI dropdown.
- **Staleness detector at ingest.** When re-indexing, walk to `file:line` and identifier references in the finding text; verify they still match. Mismatch → tag `staleness=suspected`.
- **Rigby-SIGN nudge in the UI** for findings tagged `type=decision_evidence` — soft hint at Send-to-Rigby time.
- **F-A2-equivalent for downstream consumers.** Verify consumer artifacts exist before ACs reference them (e.g., "frontend api.ts type-generation" AC referenced a non-existent codegen consumer at finding #1).
- **Wire-through smoke-check AC** for half-wired findings — auto-add "verify from Chris's browser session, not just Django test client" to prevent 401-middleware-style landmines.

### FIX

- **Spec-generator prompt awareness of finding type.** `type=decision_evidence` should get pinned "Boundaries (non-prescriptive)" as a default section, not opt-in via Rigby SIGN modification.
- **AC #4-style vagueness** ("Update audit doc"). Split into crisp actions: "add forward-pointing addendum to <path>" vs "create new sibling artifact at <slug>". Spec generator chooses or asks.

### REMOVE

- **Executable-shape spec generation for decision-evidence findings.** Force-fitting Goal/AC/Files onto a Cat-A-boundary-observation finding requires round-peg-square-hole rework every time. Route those to an `evidence_capture` template shape (Snapshot / Boundaries / Data / Verbatim quotes / Non-recommendation / Next-arc pointer).

## Rigby tool gap re-hit (real-use signal, not first observation)

`DocResearchFinding` still not in `orm_inspect_tool` allowlist; `web_fetch_tool` has no session cookies. Rigby honestly reported blocker with 2 real tool_runs (excellent PLAYBOOK-7.7.2 SIGN behavior) instead of pretending. Claude Code executed via ORM directly.

- Ledger entry already exists as carry-forward in S2989 00-START ("Rigby tool allowlist expansion — Add OpsRunEvent + UserMemoryContext + now DocResearchFinding").
- This session provides another concrete adopter signal.
- Combined with the v2 close-mode taxonomy gap, this is now blocking Rigby from being able to close her own finding-execution loop end-to-end.

## Session shape observations

- **Chris-catches-me-first-instance:** finding #2, Chris said "Don't forget to loop in Rigby if you need to" — I had framed X/Y/Z directly to Chris without SIGN. Correction applied at finding #3 (Rigby-first executed correctly). Reinforces `feedback_claude_rigby_agree_first_chris_yes_no`.
- **Rigby-honest-tool-failure-report:** finding-marking step, Rigby reported "I can't do this from my tool surface" with tool_runs proving the attempt, instead of faking success. Textbook `feedback_verify_rigby_tool_runs_before_trusting_sign` counter-example (she flagged her own gap without me having to catch it).
- **Staleness caught by verify-first pattern:** finding #3's stale specifics (line refs + LeagueViewSet + rate estimate) were caught only because I verified state at HEAD before framing to Chris. This confirms `feedback_verify_at_raw_orm_before_trusting_tool_no_data` extends to "verify findings against HEAD before trusting them as executable spec."
- **Two-shape-mismatch pattern (findings #2 + #3):** the Send-to-Rigby spec generator flattens all findings into executable shape. ~2/3 of findings in this session actually needed the evidence-capture template. Not a spec generator failure — a missing input dimension (finding type).

## HEAD lineage at close

```
6f78b285a docs(s2990): permission_classes implicit-inheritance evidence report (#3645)
808c50603 docs(s2990): API undeclared-endpoints evidence report (#3644)
ec34f772a fix(s2990): make drf-spectacular schema endpoints public (#3643)
8bf4e3c2a feat(s2990): enable drf-spectacular — INSTALLED_APPS + schema routes (#3642)
137b21438 docs(s2989): close cascade (#3641)
```

## Recycle-all history this session

Each merge followed by `make recycle-all` (per PLAYBOOK-7.4.4 recycle-after-merge, S2978 refinement — safe default). All backend-only changes (no `frontend/**` diff), so HEAD-range path-diff detection correctly skipped frontend rebuild each time. Clean recycle events recorded in `logs/recycle_events.jsonl` at each SHA.

## Open follow-ups for S2991+

**S2991 primary directive (Chris ratified at S2990 close):** focus S2991 on the v2 Findings-surface fix/add/remove list surfaced this session. See §"v2 gaps surfaced" above.

**Recommended S2991 opening priority order** (dependency-aware):

1. **Add close-mode taxonomy migration** — new `DocResearchFinding.status` enum + backfill existing `fixed` rows using `resolution_note` heuristics. Unblocks proper close state for the 3 findings marked this session. ~1 session.
2. **Add finding-type classifier + backfill.** Regex-based classifier for existing 900 findings; migration adds `finding_type` column. ~1-2 sessions.
3. **Fix spec-generator prompt** — branch on `finding_type=decision_evidence` to swap in the `evidence_capture` template (Boundaries pinned, non-recommendation block, quote-only Path references). ~30-60 min.
4. **Add staleness detector at ingest.** Walk file:line + identifier references; tag `staleness=suspected` on mismatch. Batch pass over existing findings after landing. ~1 session.
5. **Add Rigby tool allowlist entry** for `DocResearchFinding` in `orm_inspect_tool` + wire session cookies into `web_fetch_tool` for authenticated GET/POST. Unblocks Rigby closing her own findings loop end-to-end. ~30-60 min.
6. **Add Rigby-SIGN nudge in UI** for `type=decision_evidence` findings at Send-to-Rigby time. ~30 min.

**Carry-forward from S2989 (STILL OPEN):**

- F-D3-tracker-scope wire-up (OpsRun tracker for PA turns).
- F-D2-broad LLM-bypass audit spec.
- memory_hygiene_audit --apply on 1805 cap-drift.
- Canonical Briefing v2 scope toggle.
- Rigby tool allowlist expansion (now sharper with S2990's real-use hit).
- Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.
- Send-to-Rigby follow-ups from S2988 (per-section "Send all", workspace routing inference, LLM-mediated deliverable creation).

## Cross-cutting workflow references

- **Constitutional governance:** CLAUDE.md blockquote (Playbook v0.10.0). No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. S2990 was NOT spec-originated (Flow A real-use loop from S2989's shipped feature); straight-through Claude direct → verify at HEAD → Rigby SIGN (findings #2 + #3) → Chris yes/no → execute → verify → mark was legitimate.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. Rigby returned real tool_runs on both SIGN cycles + on the failed marking dispatch. Zero rubber-stamping.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Findings #2 and #3 each surfaced as a single yes/no to Chris after Claude+Rigby joint agreement, per `feedback_claude_rigby_agree_first_chris_yes_no`.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. All backend-only, so frontend rebuild correctly skipped.
- **Rigby tool-surface honest-blocker reporting:** an emerging positive pattern — Rigby explicitly reported "I can't do this from my tool surface" with tool_runs proving the attempt, instead of faking success. Reinforces the SIGN discipline PLAYBOOK-7.7.2 aims for.
