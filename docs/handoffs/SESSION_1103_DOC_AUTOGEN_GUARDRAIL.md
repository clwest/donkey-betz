---
title: "Session 1103 — DOC-AUTOGEN guardrail (verify_repo_guardrails)"
date: 2026-05-07
status: active
session: 1103
previous_handoff: SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md
---

# Session 1103 — DOC-AUTOGEN guardrail (verify_repo_guardrails)

## TL;DR

- **Shipped:** a lightweight DOC-AUTOGEN guardrail in `scripts/verify_repo_guardrails.py` that fails (strict mode) when `docs/INDEX.md` is missing the autogen marker. Mirrors the existing pure-function/test pattern.
- **Tests:** 4 new unit tests in `tests/test_verify_repo_guardrails.py` (canonical marker, wording-drift tolerance, missing marker, blank first line). All pass alongside the 3 existing inventory-freshness tests.
- **Session guidance:** added "Generated docs — do not hand-edit" rule to `00-START-NEXT-SESSION.md` and a one-line entry to CLAUDE.md.
- **Carryover:** `docker-compose.yml` remains modified and intentionally uncommitted.

---

## What Shipped

### 1. Pure-function classifier + filesystem wrapper

[`scripts/verify_repo_guardrails.py`](../../scripts/verify_repo_guardrails.py):

- `DOCS_INDEX` constant for `docs/INDEX.md`.
- `DOCS_INDEX_AUTOGEN_PATTERN`: `<!--\s*DOC-AUTOGEN:.*build_docs_index` (case-insensitive). Tolerant of minor wording drift while still requiring both the `DOC-AUTOGEN` token and a reference to `build_docs_index`.
- `classify_docs_index_autogen(first_nonblank_line) -> (ok, message)` — pure function, mirrors the testability pattern of `classify_platform_inventory_freshness`.
- `check_docs_index_autogen_marker() -> (ok, message)` — wrapper that opens the file, finds the first non-blank line, and delegates to the classifier.

### 2. Wired into `main()`

- New `print_block("docs/INDEX.md autogen marker", ...)` section after the platform-inventory-freshness block.
- New OK/WARNING line in the per-check status output.
- New strict-mode failure entry: `"docs/INDEX.md is missing the DOC-AUTOGEN marker"`.
- New summary line: `- docs/INDEX.md autogen marker: <bool>`.

### 3. Unit tests

[`tests/test_verify_repo_guardrails.py`](../../tests/test_verify_repo_guardrails.py) — new `DocsIndexAutogenMarkerTests` class with:

- `test_passes_with_canonical_marker`
- `test_passes_with_minor_wording_drift`
- `test_fails_when_marker_missing`
- `test_fails_when_first_line_blank`

`python -m unittest tests.test_verify_repo_guardrails -v` → all 7 tests pass (3 existing + 4 new).

### 4. Session guidance

- [`CLAUDE.md`](../../CLAUDE.md) "Working with Rigby" bullet list: added a "Generated docs are not hand-edited" line that names `docs/INDEX.md`, the regenerator command, and points at the guardrail script.
- [`00-START-NEXT-SESSION.md`](../../00-START-NEXT-SESSION.md): new short section "GENERATED DOCS — DO NOT HAND-EDIT" with a small table mapping the generated file to its regenerator and source of truth, plus explicit warning that hand-edits get overwritten by `.github/workflows/docs-sync.yml` on push to `main`.

---

## Verification

| Check | Result |
|---|---|
| `python -m unittest tests.test_verify_repo_guardrails -v` | ✅ 7/7 pass |
| `python scripts/verify_repo_guardrails.py --no-strict` | ✅ PASS — no blocking rules; new check reports `docs/INDEX.md autogen marker: True` |
| Pyright on `verify_repo_guardrails.py` | Pre-existing warnings on `summarize_json` (lines 73-93). My edits introduced none. |
| `docker-compose.yml` | Still excluded |

### Known follow-up (not in this commit)

- **Platform inventory freshness** still warns (`inventory head e6c7a39b != repo head`). Inventory regen is queued for Phase 2C; requires DB access.
- The new check is wired but **strict mode is not yet enabled in CI**. Wiring `verify_repo_guardrails.py` into a CI workflow remains a separate (deferred) item.

---

## Files Changed

```
M  scripts/verify_repo_guardrails.py             (constants + classifier + check + main wire)
M  tests/test_verify_repo_guardrails.py          (4 new unit tests + import)
M  CLAUDE.md                                     (1 bullet under Working with Rigby)
M  00-START-NEXT-SESSION.md                      (new GENERATED DOCS section + verifier line)
M  docs/handoffs/CURRENT.md                      (re-pointed at SESSION_1103)
A  docs/handoffs/SESSION_1103_DOC_AUTOGEN_GUARDRAIL.md  (this file)
```

Excluded: `docker-compose.yml` (Session 1100 carryover).

---

## Runtime Behavior Changes

**None.** The guardrail script is opt-in (developers and CI run it explicitly). Adding a new check function does not change app, agent, PA, or frontend behavior.

The CI workflow `.github/workflows/docs-sync.yml` was not modified — it already ensures the marker is present by re-running `build_docs_index` on each push to `main`.

---

## Why This Matters

Phase 2B added the `<!-- DOC-AUTOGEN -->` marker to the `build_docs_index` template, but a marker without enforcement is just a comment. This session installs the enforcement: future Claude/agent sessions that try to hand-edit `docs/INDEX.md` will see it fail strict-mode guardrails on the next run. Combined with the existing CI workflow that regenerates the file on each push, hand-edits become self-correcting.

The classifier deliberately tolerates minor wording drift (e.g., "regenerated via" vs "generated by") so future template tweaks in `build_docs_index.py` don't require a coordinated guardrail update — the contract is: "first non-blank line contains both `DOC-AUTOGEN` and `build_docs_index`."

---

## Next Session Picks Up With

1. **`.rag/` decision** (untrack vs. add `build_rag_corpus`).
2. **H4 — donkey-logo replacement** — Phase 2 plan found zero live template references; warrants one more deep static-manifest scan before deletion.
3. **Platform inventory regen** — `python manage.py generate_platform_inventory`. Needs DB access. Will clear the inventory-freshness warning the guardrail currently emits.
4. **CI guardrail wiring** — add `verify_repo_guardrails.py` to a GitHub Actions workflow so drift fails CI rather than only being visible locally.

---

## Rigby / PA / AI Context

- **Conversation ID:** none for this tooling-only session.
- **State at end of session:** verifier `CONFLICT: 0`; new DOC-AUTOGEN check passes; CLAUDE.md taxonomy correct; INDEX.md self-identifies and is now contract-checked.
- **How to resume:** `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-donkeyking-token> .venv/bin/python tools/pa_chat.py "session 1103 follow-up" --conversation <id>`

---

## Cross-References

- Previous handoff: [`SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md`](SESSION_1102_PHASE2B_TAXONOMY_AUTOGEN.md)
- Phase 1 handoff: [`SESSION_1101_PHASE1_DOCS_CLEANUP.md`](SESSION_1101_PHASE1_DOCS_CLEANUP.md)
- Cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Audit V1: [`docs/audit/AUDIT_V1.md`](../audit/AUDIT_V1.md)
- Verification report: [`docs/verification/VERIFY_REPORT.md`](../verification/VERIFY_REPORT.md)
- Canonical truth docs: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md), [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)

---

*Written at end of session 2026-05-07. Do not edit after the next session begins. If the next session finds a bug in this handoff's reasoning, add a note at the bottom rather than rewriting — the original reasoning is history.*
