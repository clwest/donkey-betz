# SESSION 2988 — Canonical Briefing: field-name bug fix + prompt tightening + Send-to-Rigby

**Date:** 2026-07-27 morning (US/Denver)
**Merges:**
- `8580a67ba` — PR #3635 (bug fix: `embedding` → `embedding_vector`)
- `81c61c40d` — PR #3636 (prompt tightening + per-bullet Send-to-Rigby)
**Session shape:** Bug-report → diagnosis → PR1 → visual confirm working → Chris usability asks → PR2 → close cascade.
**Rigby cycles:** none — bug fix + follow-up were bounded engineering with no design ambiguity (Claude directed + verified, per collaboration shape).

---

## Three-part summary

**What was done (plain English):**
Fixed a bug that had every canonical summary in Workspace → Research Arcs (Repo) rendering *"Briefing unavailable — Briefing generation failed"*. Root cause: a wrong pgvector column name (`embedding` vs. `embedding_vector`) in the scope-filtered retrieval query. Then in the same session, tightened the LLM prompt that produces the briefing bullets (they were dense, jargon-heavy, meta-descriptive) and added a per-bullet **"Send to Rigby"** button that creates a workspace deliverable in Donkey Betz so Claude can pick the work up next session.

**How it improves the platform (before / after):**
- **Before:** Every canonical summary click 500'd on the backend and rendered the red "Show raw markdown instead" fallback. Even after the pgvector fix, bullets read like `This canonical summary is authored with authority: research and is evidence-consuming synthesis-only, so recommendations require implementation via child follow-on or design-preparation work.` (28 words, meta-descriptive, opaque `Cat D`/`xx99`/`verdict cascade` jargon). No way to convert a "Next Action" bullet into a tracked deliverable.
- **After:** Briefings render. Bullets are ≤ 20 words, plain English, one idea, jargon expanded or dropped (live-verified: PA canonical summary regenerated with 21 bullets, 0 over the cap). Every non-empty bullet has a "Send to Rigby" button → click → `briefing_action_item` deliverable lands in Donkey Betz workspace (`b4503364-…`) with the bullet + citations + source anchor as body content, visible in the workspace UI (not diagnostic-flagged), ready for Claude to pick up.

**Next-session first action:**
Chris opens Workspace → Research Arcs (Repo) → any canonical summary → confirms (1) bullets read cleaner than the pre-S2988 rendering and (2) clicking "Send to Rigby" on one bullet produces a deliverable that appears in the Donkey Betz workspace UI. If both pass, S2989 opens with no queued arc — high-value seeds from S2987 still apply: F-D3-tracker-scope wire-up (highest leverage), F-D2-broad LLM-bypass audit, or `memory_hygiene_audit --apply` on the 1805-row cap-drift.

---

## Session timeline

1. **09:22** — Chris reports: "Whenever I click on a Canonical summary all I get is 'Briefing unavailable — Briefing generation failed'."
2. **09:24** — Grep + service trace surfaces the failing line. `core/services/canonical_briefing.py:135` uses `CosineDistance("embedding", …)` but the model field is `embedding_vector`. Every real request throws `FieldError`; view catches as 500. All 5 existing S2985 tests `@patch(retrieve_scoped_chunks)` so the ORM query never ran under CI.
3. **09:27** — Reported diagnosis to Chris. Green-lit.
4. **09:30** — PR #3635 opened (`fix/s2988-canonical-briefing-field-name`): one-string swap + new `CanonicalBriefingRealORMRetrievalTests` seeding a real Document + DocumentEmbedding row + running un-mocked `retrieve_scoped_chunks`. 16/16 tests pass (was 15).
5. **09:34** — Chris merges. `--admin --squash --delete-branch`. `make recycle-all` clean at `sha=8580a67ba`. Live verify via `Client(HTTP_HOST=…)`: HTTP 200, 5 sections, 27 chunks, 17 fully-cited bullets against `docs/research/domains/memory/…`.
6. **10:34** — Chris opens PA canonical summary in browser. Confirms fix. Two follow-up asks:
   - Bullets feel dense and jargon-heavy.
   - No way to send a bullet to Rigby → create workspace deliverable so it becomes executable work.
7. **10:36** — Framed both asks per PLAYBOOK-7.7.3 (plain English, "do we lose anything?" + "more work later?"). Three design decisions surfaced: **granularity** (my lean: per-bullet), **workspace** (my lean: always Donkey Betz for v1), **deliverable type** (my lean: `briefing_action_item` / `research_followup`). Chris: "both bundled, per-bullet, donkey betz workspace."
8. **10:40** — Started PR2. Prompt tightening in `core/services/canonical_briefing.py`: bumped `PROMPT_VERSION` v1→v2, added voice rules to `_build_prompt` (≤20 words, one idea, plain English, expand or drop insider jargon like `Cat D`/`xx99`/`Path A`/`verdict cascade`/`F-D-2`, no stacked sub-clauses, no meta-descriptions), lowered `DEFAULT_MAX_BULLETS_PER_SECTION` 10→6.
9. **10:43** — Added `'briefing_action_item'` to `deliverable_factory._TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`. This is the substrate mechanism (existing) that keeps `ratification_record` / `engineering_spec` off the `missing_initiative_id` diagnostic path — without which the row would be hidden from the workspace UI per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.
10. **10:45** — New `canonical_briefing_send_to_rigby_view` in `core/views_repo_canonical_briefing.py`. Uses same `deliverable_factory.create_deliverable` path Rigby's `deliverable_tool.create` uses so downstream sees an identically-shaped row. URL registered at `/api/repo/canonical-briefing/send-to-rigby/`. Live smoke: HTTP 201, deliverable `206456a0-…` created in Donkey Betz workspace with `diagnostic_status=None` (exemption confirmed working). Smoke row deleted post-verify.
11. **10:46** — Frontend `SendToRigbyButton` in `CanonicalBriefing.tsx`. Per-bullet, idle→sending (spinner)→sent (green check + link to `/workspaces/<ws>/deliverables/<id>`) / error (red with retry). Suppressed on "Insufficient support in canonical docs" placeholders.
12. **10:47** — Added `CanonicalBriefingSendToRigbyTests` covering: anonymous returns JSON not 302 / missing bullet_text 400 / anchor outside docs 403 / citations not-a-list 400 / happy path (201 + no diagnostic flag regression guard). Fixed initial `ProjectWorkspace` field name (`user` not `owner`) after first run failed. Full suite: **21/21 pass** (was 16; +5).
13. **10:48** — Live-regenerated PA canonical briefing with tightened prompt. All 21 bullets under the 20-word cap. Old meta-descriptive framing gone (`"This canonical summary is authored with authority: research…"` replaced with `"Authority is research; recommendations require design-prep follow-ons for implementation."` — 9 words).
14. **10:49** — Committed + pushed. PR #3636 opened.
15. **10:52** — Chris asks for merge + recycle. `--admin --squash --delete-branch` on #3636. `make recycle-all` clean at `sha=81c61c40d`; frontend `dist/` rebuilt at 10:52 (path diff on `frontend/**` in HEAD~1..HEAD triggered rebuild + collectstatic per PLAYBOOK-7.4.4 refined at S2978).
16. **10:53+** — Close cascade.

---

## Two-PR summary

### PR #3635 — `8580a67ba` — bug fix

- **Files:** `core/services/canonical_briefing.py` (1 line), `core/tests/test_canonical_briefing.py` (+64 lines / 1 new test class).
- **Change:** `CosineDistance("embedding", …)` → `CosineDistance("embedding_vector", …)`.
- **Regression guard:** `CanonicalBriefingRealORMRetrievalTests` seeds a real Document + DocumentEmbedding row and calls un-mocked `retrieve_scoped_chunks`. Schema drift on the pgvector column will fail this test with a FieldError before reaching production.
- **Tests:** 16/16 pass (was 15).

### PR #3636 — `81c61c40d` — prompt tightening + Send-to-Rigby

- **Files:**
  - `core/services/canonical_briefing.py` — voice rules + `PROMPT_VERSION` v1→v2 + `MAX_WORDS_PER_BULLET=20` constant.
  - `core/views_repo_canonical_briefing.py` — new `canonical_briefing_send_to_rigby_view` + helpers (`_compose_action_item_body`, `_derive_title`) + `DEFAULT_MAX_BULLETS_PER_SECTION` 10→6.
  - `core/services/deliverable_factory.py` — `'briefing_action_item'` added to `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.
  - `core/urls.py` — new URL `/api/repo/canonical-briefing/send-to-rigby/`.
  - `frontend/src/components/platform/CanonicalBriefing.tsx` — `SendToRigbyButton` component + state per bullet + component-signature updates for `anchorPath` + `section` props.
  - `core/tests/test_canonical_briefing.py` — `CanonicalBriefingSendToRigbyTests` (5 tests).
- **Tests:** 21/21 pass (was 16; +5).
- **Live verify:** PA canonical briefing regenerated with 21 compliant bullets; endpoint 201 with clean deliverable (`diagnostic_status=None`).

---

## Post-merge findings

**Chris visual confirmation of #3635 succeeded on the PA canonical summary** — briefing rendered with 5 sections, 36 chunks, all bullets citation-backed. This is where the follow-up asks (density + Send-to-Rigby) came from.

**Chris visual confirmation of #3636 is still open.** Session close does not gate on it — the feature has been live-verified at the service and endpoint layers, and the frontend rebuild landed clean. Chris will test the UI after this cascade closes.

---

## Fold classifications

None — this session was a bug fix + a bounded feature follow-up with clear direction. No Rigby SIGN cycles ran (per PLAYBOOK-7.7.2 discipline, SIGN is for spec-originated implementation; ad-hoc bug fixes and Chris-directed feature extensions where design is unambiguous route straight through Claude direct→execute→verify).

---

## Open follow-ups for S2989+

Everything from `docs/handoffs/SESSION_2987_MEMORY_MAXIMALIZATION_PR2.md` §Open follow-ups still applies. New from this session:

1. **Chris visual verify of both PRs** (~2 min): open any canonical summary → confirm tightened bullets + "Send to Rigby" produces a Donkey Betz deliverable visible in the workspace UI.
2. **Follow-up if Chris hits UX issues** — the natural next iterations if problems surface: per-section "Send all" button, workspace routing inference from arc slug (e.g. `pa/` → PA-specific workspace if one exists), LLM-mediated deliverable creation (currently direct-ORM for cost/determinism — future v2 could route through Rigby's turn loop to exercise the natural-language interface).
3. **Substrate fix candidate (LOW priority):** `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` still open — the `_handle_deliverables` create-path in `td_handlers_agents.py:2139` still marks caller-created deliverables as `diagnostic` when caller doesn't supply `initiative_id`, requiring per-type exemption in the factory. My PR added `'briefing_action_item'` to the exempt list; the systemic fix (default `deliverable_type` from `category` + skip missing_initiative_id marker for governance-scoped categories) is still an open engineering candidate.

---

## HEAD at close

- After feature merges: `81c61c40d`
- After docs cascade: filled at cascade merge time.
- Recycle-all clean at `sha=81c61c40d` (post-#3636 merge).
- Wrapper pin diff (from `session_lifecycle close`): committed as part of the docs cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
