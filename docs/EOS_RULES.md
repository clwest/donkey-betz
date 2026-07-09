---
title: "Engineering Operating System — Live Rules"
status: active (living document — new rules append; superseded rules annotate, don't delete)
last_updated: 2026-07-09
authority: Chris ratifies; Claude drafts; Rigby cross-checks
companion_docs:
  - docs/ENGINEERING_PLAYBOOK.md (v0.1.0 ratified — constitutional codification)
  - docs/research/platform/platform_capability_graph.md (planning artifact)
  - docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md (CDR-001)
---

# Engineering Operating System — Live Rules

> **What this doc is.** The running index of EOS rules that Chris has ratified
> *between* Playbook releases. Each rule is operational immediately from the
> date it lands here; it will be absorbed into the next Playbook PATCH
> (currently v0.1.1) at constitutional codification. This doc is append-only:
> if a rule is superseded, its entry gains a `superseded_by:` note and the
> new rule appears below — the prior rule is not deleted.
>
> **How to use.** At session open, `context-kit orient` should surface this
> doc alongside the anchors. Every campaign selection reads this doc before
> proposing scope. Every CDR references the rules that governed the
> investigation.

---

## Rule R1 — Tool Autonomy Principle

**Ratified:** 2026-07-09 (Chris directive during §12 Knowledge Retrieval
campaign start).

**Rule.** Claude defines the engineering objective. Rigby determines which
platform tools are necessary to independently verify that objective. Unless
the methodology itself requires a constrained verification approach (for
example: read-only verification, no mutations, runtime validation), Claude
should not direct Rigby to use or avoid specific platform tools.

**Why.** Two failure modes are prevented:
1. Claude under-instructs Rigby and she picks a narrower tool set than the
   objective requires — verification is superficial. (Prior instance: CDR-001
   §12.5 Rigby Q4 refinement — the initial dispatch under-scoped what
   "contract semantics" would require to verify.)
2. Claude over-instructs Rigby and she can't apply her operational knowledge
   of which tools have known correctness / performance / dedup / observability
   characteristics. She's the platform's first-class interface; giving her
   real tool autonomy exercises and improves that interface every session.

**How to apply.** When dispatching a verification ask to Rigby:
- State the objective clearly (what she is proving/refuting).
- State any methodological constraint (read-only, no writes, must run
  against HEAD SHA X, etc.) — but only if the methodology requires it.
- **Do not enumerate the tools to use.** Do not write "use repo_tool + ORM +
  celery_task_history." Trust Rigby to pick.
- State the return format (verdict shape, evidence requirements).

**Example — good dispatch.**
> "Independent SIGN pass on §12 Knowledge Retrieval Category A. Objective:
> confirm or refute Claude's §12 completeness score. Read-only against HEAD
> `<sha>`. Return: SIGN-CONFIRMED / WITH-REFINEMENTS / REFUTED per numbered
> claim with file:line evidence for any refutation."

**Example — bad dispatch.**
> "Please use repo_tool to grep for `_get_relevant_knowledge_for_task`, then
> use ORM to count Document rows, then use celery_task_history to check…"

**Anti-application — when Claude DOES specify tools.**
- Runtime validation ("verify via `[PA_ROUTING_INIT]` log grep against a
  live worker") — the methodology binds the tool.
- Read-only enforcement ("no mutations; use search/read tools only") — the
  methodology binds the surface.
- Convergent-evidence requirements ("evidence must come from BOTH ORM AND
  file read to catch dual-schema drift") — the methodology binds the count.

**Codification path.** Absorbed into Playbook v0.1.1 chapter on
Claude/Rigby role boundaries at constitutional codification. Until then,
this doc is authoritative.

---

## Rule R2 — Capability Discovery Records precede engineering

**Ratified:** 2026-07-09 (CDR-001 authorship + Chris directive
"Every Category A investigation that materially changes campaign scope
must create a Capability Discovery Record before engineering begins").

**Rule.** When a Category A investigation materially changes the scope of a
proposed engineering campaign — deleting work, discovering existing
substrate, invalidating graph assumptions, or expanding scope beyond the
originally-scoped budget — a Capability Discovery Record must be authored
and ratified before any code lands. The CDR is a governance artifact,
not an implementation deliverable.

**Required sections** (numbered, all present, in this order):
1. Original Capability Graph assumptions
2. Repository evidence discovered
3. Assumptions proven false
4. Existing substrate identified
5. New capability score
6. Engineering work deleted because of the discovery
7. Remaining work
8. Whether the Capability Graph should be updated
9. Ratification path
10. Scope of this document
11. Lessons Learned (permanent — see §11 of CDR-001)
12+ Reconciliation folds from Rigby SIGN (append-only per playbook §14)

**Numbering.** CDR-001 is the first. Numbering is monotonic across the
platform's lifetime.

**Location.** `docs/research/platform/CDR_<NNN>_<slug>.md`.

**Codification path.** Absorbed into Playbook v0.1.1 methodology chapter
at constitutional codification. Reference implementation: CDR-001.

---

## Rule R3 — Acceptance tests before implementation

**Ratified:** 2026-07-09 (Rigby SIGN refinement folded into §12 campaign
start; Chris echoed verbatim: "Before proposing implementation, define
the acceptance tests that prove the capability exists. The tests should
not be reverse-engineered after implementation.").

**Rule.** Before proposing implementation for a capability engineering
campaign, define the acceptance tests that prove the capability exists.
Tests are written first as part of the campaign scope. They are not
reverse-engineered from the implementation.

**Why.** Prevents the "assumed gap" failure mode that CDR-001 corrected on
§16: without acceptance tests, "capability increase" is unfalsifiable and
the campaign can drift into reorganization.

**How to apply.** Campaign scope deliverable must contain:
- A "Capability definition" section stating what the capability IS
  (measurable, observable, third-party-verifiable).
- An "Acceptance tests" section enumerating the tests that prove the
  capability. Tests should reference measurable substrate: file:line for
  code paths exercised, ORM queries for state assertions, log grep for
  observability, latency bounds for performance, etc.
- Tests must be verifiable at HEAD *before* the campaign closes. If a
  test can only be run post-implementation, it is not an acceptance test
  — it is a regression test.

**Codification path.** Absorbed into Playbook v0.1.1 methodology chapter
alongside R2 CDR discipline.

---

## Rule set discipline

- **Append-only.** New rules go below existing ones. Rules are numbered
  monotonically (R1, R2, R3, …). Superseded rules gain a `superseded_by:`
  annotation but stay in the document.
- **Constitutional codification.** Rules on this list are operational
  immediately from ratification date. They are absorbed into the next
  Playbook PATCH at constitutional codification, at which point the
  rule entry here can be annotated `codified_in: playbook-v0.1.1` but
  MUST NOT be deleted — the append-only ledger persists.
- **Discovery via `context-kit orient`.** This doc should be surfaced by
  the orient sequence at session open. CLAUDE.md carries a one-line
  pointer under the Working-with-Rigby section.
- **CDR references.** When a CDR cites a rule from this doc (e.g., "this
  Category A investigation was run under Rule R1 Tool Autonomy
  Principle"), the CDR reference is enough — the rule text itself is
  not duplicated into the CDR.
