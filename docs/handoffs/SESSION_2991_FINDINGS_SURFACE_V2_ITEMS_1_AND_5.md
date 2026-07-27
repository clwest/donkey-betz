# Session 2991 — Findings-surface v2 items #1 and #5

**Date:** 2026-07-27
**Head at open:** `847c86c41` (S2990 close cascade merged)
**Head at close:** `7a895c871` + docs cascade
**Shape:** Flow B — spec-originated engineering work per S2990's v2 list; Chris ratified S2991 v2 item #1 as opener at S2990 close.

---

## Summary

Shipped the first two S2991 v2 fix/add/remove items in a single session — the additive `close_mode` taxonomy migration Chris + Rigby jointly designed at framing, plus the paired allowlist entry that unblocks Rigby's Findings-surface SIGN cycles going forward.

- **PR #3647** (`6f9f298b5`) — v2 item #1: additive `close_mode` column on `DocResearchFinding` (nullable 4-value CharField), backfills the 3 S2990 canonical rows, `status` enum untouched
- **PR #3648** (`7a895c871`) — v2 item #5 scoped: `DocResearchFinding` added to `orm_inspect_tool._MODEL_POLICIES` allowlist + 8 tests

Both merged clean under `--admin`. Recycle-all clean after each merge.

---

## PR #3647 — close_mode taxonomy (v2 item #1)

**Files:**
- `core/models_audit_findings.py` — added `CLOSE_MODE_CHOICES` + `close_mode` CharField (nullable, default None)
- `core/migrations/0399_s2991_doc_research_finding_close_mode.py` — schema + backfill for the 3 canonical rows
- `core/views_doc_research_findings.py` — `close_mode` in serializer output; mark endpoint accepts optional `close_mode` with 4-value enum validation

**Framing loop:** Claude proposed a 6-value `status` replacement. Rigby SIGN caught the axis confusion via tool_runs (read model, checked endpoint, confirmed `dismissed` value already exists). Joint recommendation collapsed to: keep `status` lifecycle (`open/fixed/dismissed`) intact, add **orthogonal** `close_mode` column carrying closure mechanism only. Chris ratified the joint recommendation as a single yes/no per `feedback_claude_rigby_agree_first_chris_yes_no` + PLAYBOOK-7.7.3.

**Backfill mapping** (per S2990 close):

| Finding ID | S2990 PR | close_mode |
|---|---|---|
| `4b92f6f0-b84b-47d1-976a-30246f3dbd3d` | #3642 + #3643 (drf-spectacular) | `fixed_via_pr` |
| `023d3301-df86-4879-893f-8fd5b0c460c8` | #3644 (undeclared endpoints evidence report) | `evidence_delivered` |
| `3a89fddc-7b62-4093-afaa-1a9896c540f8` | #3645 (permission_classes evidence + STALE addendum) | `evidence_delivered` |

**Freshness axis deferred:** row #3's "stale-corrected" state stays in `resolution_note` until a 2nd independent trigger justifies a dedicated column (Rigby zoom-out fold + Claude+Rigby joint agreement).

**A2 SIGN verdict:** AGREE-with-concerns (Rigby). Concerns:
1. Rigby-side verification still auth/allowlist gated → resolved same session by PR #3648
2. `close_mode` in payload → stable contract lock-in once consumers depend on it (accepted risk)

---

## PR #3648 — DocResearchFinding on orm_inspect_tool allowlist (v2 item #5, scoped)

**Files:**
- `core/services/td_handlers_agents.py` — `DocResearchFinding` added to `_MODEL_POLICIES` with `expensive_text_fields=(text, resolution_note)`, `sensitive=False`
- `core/tests/test_s2991_close_mode_and_orm_allowlist.py` — 8 tests (3 for close_mode field, 5 for allowlist entry)

**Trigger:** same tool-gap blocker hit twice — S2990 close-marking + S2991 close_mode A2 verify. Two triggers within two sessions justify closing the gap per the S2991 v2 spec.

**Scope narrowing:** original v2 item #5 spec had two halves — allowlist entry AND `web_fetch_tool` session-cookie wiring. The second half deferred as separate carry-forward (bigger design decision + security review needed; Rigby could hit any authenticated endpoint).

**A2 SIGN verdict:** AGREE (Rigby). Dogfooded end-to-end:
- `list_models` — `DocResearchFinding` visible
- `describe_model` — `close_mode` field visible with correct choices
- `filter status=fixed` — 3 rows, `close_mode` value present in row payload
- `count_by close_mode` — 897 null / 2 evidence_delivered / 1 fixed_via_pr (matches spec exactly)

---

## v2 gaps surfaced (carry-forward for S2992+)

### From S2991 A2 SIGNs

1. **`web_fetch_tool` session cookies** — the deferred half of v2 item #5. Rigby can now inspect DB state via `orm_inspect_tool`, but end-to-end HTTP shape verification (serializer output, endpoint auth behavior, etc.) still requires Chris/Claude for anything past the ORM boundary. Needs security-scoped design.
2. **Dry-run counts for bulk-write migrations** — Rigby's PR #3648 zoom-out fold. Future v2 items #2 (classifier at ingest) + #4 (staleness detector) will touch all 897 open rows; both should support a `--dry-run` mode that reports "would classify X rows as decision_evidence, Y as executable" before writing. Prevents accidental bulk backfill.
3. **Freshness axis deferred with 2nd-trigger clause** — codified twice this session (Rigby SIGN #1 + #2). If any future finding surfaces "stale-corrected" state, that is the 2nd trigger; add orthogonal `evidence_freshness` field, do NOT expand `close_mode` values.

### Remaining v2 items (unchanged from S2990 close, minus #1 + #5 partial)

- **#2 finding-type classifier at ingest** — regex signals for `decision_evidence` vs `executable`. ~1-2 sessions. Now easier to verify via `count_by(close_mode)` deltas per Rigby's zoom-out.
- **#3 spec-generator prompt branching on finding_type** — gated behind #2. ~30-60 min.
- **#4 staleness detector at ingest** — walk `file:line` references, tag mismatches. ~1 session.
- **#6 Rigby-SIGN nudge in UI for decision_evidence findings** — ~30 min.
- **#7 F-A2-equivalent for downstream consumers** — verify consumers referenced in ACs actually exist. ~30-60 min.
- **#8 wire-through smoke-check AC for half-wired findings** — auto-add browser-session verification to prevent 401-middleware-style landmines. ~30 min.

---

## Constitutional notes

- **PLAYBOOK-7.7.1** — spec→ship shape. Both PRs used Flow B (spec-originated from S2990's v2 list). Joint framing → Chris yes/no → execute → A2 SIGN → merge → recycle. No phase skipped.
- **PLAYBOOK-7.7.2** — SIGN evidence discipline. Rigby returned real tool_runs on both framings + both A2 SIGNs. Zero rubber-stamping; her T1 DISAGREE on the initial 6-value proposal was the highest-leverage moment of the session.
- **PLAYBOOK-7.7.3** — Chris-facing decision framing. Each Chris-facing routing was one yes/no with "do we lose anything?" + "is it more work later?" per `feedback_plain_english_decision_framing_for_chris`.
- **PLAYBOOK-7.4.4 (S2978 refinement)** — `make recycle-all` after each merge. Both diffs backend-only; path-diff correctly skipped frontend rebuild.

---

## Session close state

- HEAD at close: `7a895c871` + docs cascade PR (this file + 00-START refresh + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`)
- Recycle-all clean at `sha=7a895c871a9f` post-PR-#3648
- 897 open findings unchanged. 3 fixed findings now carry orthogonal `close_mode` values.
- Rigby's `orm_inspect_tool` surface now covers DocResearchFinding for future Findings-surface SIGN cycles.
