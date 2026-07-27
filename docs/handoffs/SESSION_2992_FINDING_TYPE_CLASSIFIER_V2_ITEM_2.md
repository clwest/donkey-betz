# Session 2992 — Finding-type classifier at ingest (v2 item #2)

**Date:** 2026-07-27
**Head at open:** `8debe2e5e` (S2991 close cascade merged)
**Head at close:** `ab21d7a88` + docs cascade
**Shape:** Flow B — spec-originated engineering work per S2991's v2 list; Chris ratified S2992 v2 item #2 as opener via "Ship v2 item #2" session-open directive.

---

## Summary

Shipped v2 item #2 end-to-end in two PRs across a single session — the additive `finding_type` classification axis plus the 900-row corpus backfill. Sets up the next three v2 items (#3 prompt branching, #4 staleness detector, #6 UI nudge) which all depend on `finding_type` being populated at ingest time.

- **PR #3650** (`5f4652f8d`) — v2 item #2 PR (a): additive `finding_type` CharField on `DocResearchFinding` (3-value enum, default `unknown`, `db_index=True`), regex classifier at ingest via `_classify_finding_type`, `--reclassify-existing` command mode with safety-first dry-run default, 21 tests
- **PR #3651** (`ab21d7a88`) — v2 item #2 PR (b): data migration 0401 backfills the 900-row corpus (139 decision_evidence / 138 executable / 623 unknown = 15.4/15.3/69.2%; 277 rows flipped)

Both merged clean under `--admin`. Recycle-all clean after each merge.

---

## PR #3650 — finding_type + classifier + dry-run command (v2 item #2 PR a)

**Files:**
- `core/models_audit_findings.py` — new `FINDING_TYPE_CHOICES` + `finding_type` CharField (default `unknown`, `db_index=True`)
- `core/migrations/0400_s2992_doc_research_finding_finding_type.py` — schema-only additive migration
- `core/management/commands/index_doc_research_findings.py` — new `_classify_finding_type(text, source_heading)` helper wired into both `_parse_finding_sections` and `_parse_implementation_debt`; new `--reclassify-existing` mode with `--apply` gate
- `core/views_doc_research_findings.py` — serializer surfaces `finding_type`; list endpoint accepts optional `finding_type` query filter
- `core/tests/test_s2992_finding_type_classifier.py` — 21 tests

**Framing loop:** Claude ran ORM-direct validation on the 900-row corpus before framing (spec's literal `"blocks downstream X"` had 0 matches). Rigby T1 SIGN sampled 10 real rows via `orm_inspect_tool` and flagged that plainly actionable findings without `.py:line` anchors were collapsing into `unknown`. Signal set widened before code:

**decision_evidence** (any match, wins on collision):
- Text: `/Cat[egory]? ?A/`, `/boundary (observation|violation)s?/`, `/xx99/`, `/D-verdict/`
- Source heading: `boundary violations`

**executable** (any match):
- Text: file:line anchor for `.py|.ts|.tsx|.js|.jsx|.go|.rs|.md`
- Text: imperative verbs `rename|delete|remove|add|implement|wire|fix|refactor|migrate|bump|pin|extract|split|merge|backfill|deprecate`
- Source heading: `next actions | action items | todos`

**Default:** `unknown`.

**Chris ratification:** Plain-english decision routing via Rigby per PLAYBOOK-7.7.3. Chris replied yes ("I replied yes in the chat but yours got in right before mine") after seeing the shape summary with the imperative-verb tweak folded in.

**A2 SIGN verdict:** AGREE (Rigby). Real tool_runs:
- `describe_model` — finding_type field visible (19 fields, up from 18)
- `count_by finding_type` — all 900 rows at `unknown` (schema default confirmed)
- 10-row real-corpus classification sample — 8/10 matched her gut; 2 minor acceptable misses noted (see "v2 gaps surfaced" below)
- Distribution sanity: 15.4/15.3/69.2 passes smell test

---

## PR #3651 — finding_type backfill (v2 item #2 PR b)

**Files:**
- `core/migrations/0401_s2992_finding_type_backfill.py` — data migration that re-runs `_classify_finding_type` over every row via `apps.get_model(...).iterator(chunk_size=500)`; only flips rows whose classifier output differs; reverse resets non-unknown rows back to `unknown`

**Live post-migration distribution (matches PR #3650 dry-run exactly):**

| finding_type | count | pct |
|---|---|---|
| decision_evidence | 139 | 15.4% |
| executable | 138 | 15.3% |
| unknown | 623 | 69.2% |
| **TOTAL** | **900** | 100% |

**Final Rigby verify:** exact match confirmed via `orm_inspect_tool count_by(finding_type)` post-recycle.

---

## v2 gaps surfaced (carry-forward for S2993+)

### From S2992 A2 SIGN (non-blocking future signal tweaks)

1. **`boundary drift` not classified as decision_evidence** — current regex expects `boundary (observation|violation)`. Rigby saw "boundary drift" phrasing in real corpus (falls into `unknown`). Small regex widening; wait for signal-tweak trigger.
2. **`VERIFIED at HEAD` evidence records land in `executable`** — because they cite `file:line`. Arguably these are decision-record evidence (a doc claim verified against runtime), not action items. If we want evidence records to cluster together, tighten precedence or add a `verified_at_head` short-circuit before the executable check.

Neither is blocking. Both are candidates for a single signal-tweak PR if S2993 or later observes a 2nd independent trigger.

### Remaining v2 items (from S2990 → S2991 → S2992; #1, #2, #5 shipped so far)

- **#3 spec-generator prompt branching on finding_type** — now unblocked. Branch template selection on `finding_type=decision_evidence` (evidence-capture template) vs `executable` (normal engineering spec). ~30–60 min.
- **#4 staleness detector at ingest** — walks `file:line` + identifier references, verifies still-matches at HEAD, tags `staleness=suspected` on mismatch. `--dry-run` mode required per PR #3648 zoom-out fold. ~1 session.
- **#5 web_fetch_tool session cookies (deferred half)** — bigger design change; security review needed.
- **#6 Rigby-SIGN nudge in UI for `finding_type=decision_evidence`** — now unblocked. ~30 min.
- **#7 F-A2-equivalent for downstream consumers** — verify consumers referenced in ACs actually exist. ~30–60 min.
- **#8 wire-through smoke-check AC for half-wired findings** — ~30 min.

---

## Constitutional notes

- **PLAYBOOK-7.7.1** — Flow B (spec-originated). Joint framing → Chris yes/no → execute → A2 SIGN → merge → recycle for both PRs. No phase skipped.
- **PLAYBOOK-7.7.2** — SIGN evidence discipline. Rigby returned real `orm_inspect_tool` tool_runs on both T1 framing (10-row sample) + A2 verify (describe_model + count_by) + final verify post-PR-b. Zero rubber-stamping.
- **PLAYBOOK-7.7.3** — Chris-facing decision framing. Chris ratification was one yes/no with "do we lose anything? / is it more work later?" framing.
- **PLAYBOOK-7.4.4 (S2978 refinement)** — `make recycle-all` after each merge. Both diffs backend-only (models, migrations, management command, view, tests); path-diff correctly skipped frontend rebuild.
- **PR #3648 zoom-out fold applied** — `--reclassify-existing` defaults to dry-run; `--apply` required to persist. Prevented accidental bulk backfill during PR (a) integration testing.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Claude ran ORM-direct signal validation BEFORE framing (spec's literal signals didn't match corpus reality). Prevented shipping a classifier that would over-collapse into `unknown`.

---

## Session close state

- HEAD at close: `ab21d7a88` + docs cascade PR (this file + 00-START refresh + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`)
- Recycle-all clean at `sha=ab21d7a8846b` post-PR-#3651
- 900 findings now carry classifier-derived `finding_type` values.
- Ingest classifier runs on every new `index_doc_research_findings` invocation; new rows are auto-classified.
- Signal tweak future-carry (boundary drift + VERIFIED at HEAD) tracked here, no PR needed yet.
