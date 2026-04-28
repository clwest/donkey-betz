# Cleanup Follow-ups

> Open issues surfaced during cleanup phases that don't fit cleanly
> into the current `ROOT_CLEANUP_PLAN.md` phase structure but should
> not be lost. Append-only — close items by editing in place with a
> "Closed: <date> by <commit>" note rather than removing.

---

## ORIENT-2026-04-28 — `context-kit orient` still picks the wrong "latest handoff"

**Status:** Open. Worked around in Phase 1 (`1c1ba538`) but the
deeper bug is unresolved.

**Symptom.** Running `context-kit orient` from this repo's root
reports the wrong `LATEST HANDOFF` block. Pre-Phase-1 it picked
`docs/handoffs/SESSION_ROADMAP_DISCONNECTED_FIXES.md` (Session 646,
Dec 2025). Post-Phase-1 (after that file was renamed to
`ROADMAP_DISCONNECTED_FIXES.md`), it now picks
`docs/handoffs/SESSION_999_STOCK_INTELLIGENCE_HUB.md` instead of
the actually-most-recent `SESSION_1098_*` family.

**Root cause.** `context-kit orient` (upstream:
`cli/orient.py`) discovers handoffs via
`sorted(p for p in handoffs_dir.glob("SESSION_*.md") if p.is_file())`
and takes the last entry. That sort is **lexicographic on the
filename**, not by mtime or by the embedded session number. With
ASCII ordering, `'9' > '1'`, so `SESSION_999_*` lex-sorts AFTER
`SESSION_1098_*`. Renaming `SESSION_ROADMAP_*` only closed the
outermost layer of this trap.

**Two viable fixes, in order of preference:**

1. **Upstream fix.** File an issue against `clwest/context-kit`
   asking `cli/orient.py` to either (a) sort handoffs by mtime or
   (b) parse the leading digits and sort numerically with an
   alphabetical tiebreak. (b) is preferable because mtime is noisy
   under git checkout / rebase. This is a one-function change in
   the orient module; tests already exist for orient's basic shape
   and adding a "picks 1098 over 999" case is straightforward.

2. **Local zero-pad.** Mass-rename every `docs/handoffs/SESSION_NNN_*.md`
   to `docs/handoffs/SESSION_NNNN_*.md` (3-digit -> 4-digit). Touches
   ~662 files, many history references, and breaks any external link
   that quoted a handoff path. Costly enough that it's only
   worth doing as part of a larger handoff-archiving phase (Phase 5
   in `docs/audit/CLEANUP_PLAN.md` — yearly subdirs).

**Workaround in the meantime.**
`ls -t docs/handoffs/SESSION_*.md | head -5` lists handoffs by
mtime and is the reliable way to find "what shipped last" until
one of the fixes above lands.

**Cross-references.**
- Audit finding: `docs/audit/AUDIT_V1.md` § P0 #4
- Phase 1 commit that partially addressed it: `1c1ba538`
  (`docs(cleanup): restore runtime truth anchors for Session 1100`)
- Upstream module to file the issue against:
  `clwest/context-kit` — `cli/orient.py:121` (the `sorted(...)` line)

---

## VERIFIER-2026-04-28 — `verify_doc_claims --only-drift` returns empty while inventory reports 45 drifts

**Status:** Open. Surfaced during Phase 1 verification but out of
Phase 1 scope.

**Symptom.** During the Phase 1 truth-restore run, two adjacent
sources of truth disagreed:

- `python manage.py verify_doc_claims --only-drift` reported
  `No matching claims to run.`
- The freshly-regenerated `docs/PLATFORM_INVENTORY.md` executive
  summary reports the *Doc-vs-Reality Verifier State* row as
  `65 registered claims across 30 docs: 20 OK, 45 drifts`.

So 45 known drifts exist according to the inventory, but
`--only-drift` matched zero claims to actually run. That's
contradictory and means we don't currently know which 45 claims
are red.

**Likely causes (untriaged).**

- `--only-drift` may filter by claim *source-doc* or *category*
  rather than result-status, in which case the empty match is
  semantic, not a bug.
- The verifier's claim corpus may be loaded from a different
  cache or DB table than the inventory's snapshot, so the two
  reports are looking at different generations of the same data.
- `--only-drift` may be inverting its filter (e.g. requires a
  claim to first be marked drift and the marking step never ran).

**Suggested next step (not Phase 1).** Run
`python manage.py verify_doc_claims` *without* `--only-drift`
to see the full claim list and what's red. Once you have the full
picture, decide whether the `--only-drift` flag needs a
docstring/behavior fix in `core/services/doc_claim_verification.py`
(the module the inventory references) before it can be relied on
for CI gating in Phase 3.

**Why this matters.** Phase 3 of `docs/audit/CLEANUP_PLAN.md`
proposes adding `verify_doc_claims --only-drift` as a required PR
step. We should not gate on a flag whose result is contradictory
with the same data's other surface — fix the verifier surface
before the CI gate.

**Cross-references.**
- Audit finding: `docs/audit/AUDIT_V1.md` § P0 #1 (mentions the
  verifier as the discipline-as-code anchor)
- Phase 3 plan: `docs/audit/CLEANUP_PLAN.md` § Phase 3 (CI gating)
- Inventory section that reports the drift count:
  `docs/PLATFORM_INVENTORY.md` — *Doc-vs-Reality Verifier State*
- Verifier source: `core/services/doc_claim_verification.py`
