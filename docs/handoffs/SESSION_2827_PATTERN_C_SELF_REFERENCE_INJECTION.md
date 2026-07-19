---
title: "S2827 — Pattern C SELF_REFERENCE Candidate Injection + Corpus Label Repair"
session: 2827
date: 2026-07-19
status: shipped
authority: implementation + governance
scope: |
  S2827 shipped Pattern C SELF_REFERENCE candidate injection + Chris-
  ratified corpus label ground-truth repair as one atomic PR (#3267,
  SHA `47f3650d1`). Post-implementation Phase-0.5 re-measurement:
  6/18 → 10/18 = 55.6% strict top-1 (+4 conversions Q14/Q15/Q16/Q17,
  matches design projection exactly). Q20 + Q24 (literal-filename)
  explicitly deferred to future Pattern D per Chris D-Q4. Rigby joint
  SIGN cleared with 4 DISAGREE + 1 AGREE-with-caveat reconciled into
  v2 design; Chris D-verdicts D-Q1..D-Q5 all YES with refinements
  applied (measured smallest-bonus discipline; corpus label
  correction as ground-truth repair; shared pointer-intent primitive
  as post-Pattern-D codification candidate; literal-filename ownership
  to Pattern D; sequential arc ordering). SEVENTY-SECOND close-cycle
  post-PLAYBOOK-7.4.4.
predecessor: docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md
merge_pr: 3267
merge_sha: 47f3650d1
---

# S2827 — Pattern C SELF_REFERENCE Candidate Injection

## §1 One-paragraph summary

Shipped Pattern C SELF_REFERENCE candidate injection into
`core/rag_integration.py` embedding lane as a sibling to S2826 Pattern B
(COUNT gate). Narrow 4-pattern regex intent gate (Rigby-Q1 tightened
after DISAGREE — required file-context word on "session start"; literal-
filename patterns removed and ceded to future Pattern D per Chris D-Q4).
Canonical-anchor injection via `_fetch_self_reference_anchor_chunks`
under the SAME filter chain (Chris D6 no-`include_superseded`-relaxation
invariant preserved). Bounded ranking bonus +0.23 — smallest tested
static value converting all 4 intended cases (Q14/Q15/Q16/Q17) while
preserving all negative controls, per Chris D-Q1 "smallest reliable
adjustment; record tested alternatives + margins" discipline. Same PR
shipped ground-truth corpus label repair (Chris D-Q2): 4 SELF_REFERENCE
rows had strict + loose targets pointing at a path (`docs/00-START-NEXT-SESSION.md`)
that does not exist; corrected to real repo-root path (`00-START-NEXT-SESSION.md`);
8-line surgical edit, content otherwise untouched. Post-implementation
Phase-0.5 re-measurement (post-corpus-correction; NOT unchanged-corpus per
Chris D-Q2): 6/18 → **10/18 = 55.6%** strict top-1, exactly matching
design projection. Pattern B COUNT smoke: no regression. Pytest: 34/34
passing. Full evidence in design doc §7.5. Permanent architectural
reference added to `docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured
Boundary Summary per Chris close directive.

## §2 Ship

### Files shipped

**PR #3267 — atomic per Chris D-Q5:**

| # | File | Change |
|---|---|---|
| 1 | `core/rag_integration.py` | +285 lines Pattern C impl (patterns/anchors/gate/fetch/composition/sort/WARN/diagnostics) |
| 2 | `docs/research/discovery_layer/PHASE_0_5/corpus.json` | 8-line surgical label repair (Q14/Q15/Q16/Q20 strict + loose) |
| 3 | `docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md` | New — SIGN reconciliation summary + design + full §7.5 measurement evidence |
| 4 | `tests/unit/test_s2827_pattern_c_self_reference_gate.py` | New — 34 pytest cases |

**Merge:** SHA `47f3650d1` (2026-07-19) via `gh pr merge --admin --squash --delete-branch 3267`. Post-merge `make celery-recycle` executed per PLAYBOOK-7.4.4.

### Ledger delta

- Zoom-out ledger: no new folds this session (design was reconciled through Rigby SIGN before implementation; no post-hoc drift observed).
- Pattern registry (Chris D-Q3 forward-carry): now 2 intent-gated policy-class mechanisms (Pattern B COUNT, Pattern C SELF_REFERENCE); Pattern D literal-filename queued as third. At 3 shipped instances, the shared "pointer-intent registry" primitive becomes a codification candidate per §14.2 default two-trigger threshold.

## §3 Rigby joint SIGN records (S2827)

### §3.1 — First SIGN cycle (design v1)

5 questions routed (mirroring S2826 Q1-Q5 shape + PLAYBOOK-6.10.7 zoom-out):

Rigby tool_runs (anti-rubber-stamp check per S2777): `search_docs` (3 calls),
`repo_tool.read_file` + `search` (multiple), `kb_tool.semantic_search`
(multiple — independent verification of §3.2 baseline retrieval on Q14–Q20).
Tool-grounded verdicts, not rubber-stamp.

Rigby verdicts:
- **Q1** DISAGREE — gate too permissive; remove literal-filename patterns (ceded to Pattern D per Chris D5); tighten `session start` (require file-context word); broaden `project rules?` (singular/plural)
- **Q2** DISAGREE — Strategy B (deterministic re-rank) overreaches Chris D2 "bounded policy bonus"; adopt Strategy A (bounded bonus + injection-if-missing, mirrors Pattern B)
- **Q3** DISAGREE — Q20 belongs in Pattern D (literal-filename policy class per Chris D5); Pattern C should own only semantic pointer intent
- **Q4** DISAGREE (framing-AGREE) — corpus path-label defect is real blocker; recommend corpus label correction (lighter-touch than authoring strict-hit scorer)
- **Q5** AGREE-with-caveat — ship as-designed; extract shared "pointer-intent registry" primitive after Pattern D also ships; ensure diagnostics detect false-positive gate firing AND injection frequency

### §3.2 — Reconciliation cycle (design v2)

Rigby verdicts on R1-R5 refinements: **all AGREE** including R4 framing
(surface to Chris; recommend corpus label correction). Joint Claude+Rigby
agreement reached before Chris routing per S2753 "reach agreement before
Chris yes/no."

## §4 Chris D-verdicts (all RATIFIED with refinements — same session)

- **D-Q1 YES** — with refinement: `+0.15` initial proposal was a hypothesis,
  not a constitutional constant. Use SMALLEST reliable adjustment; record
  tested alternatives + margins. Applied → §7.5.2 bonus sweep table +
  `_SELF_REFERENCE_INTENT_BONUS = 0.23`.
- **D-Q2 YES** — corpus label correction is ground-truth repair, not
  benchmark tuning. Apply only to mislabeled path fields (no query text /
  semantics / unrelated rows changed). Post-correction corpus is the
  authoritative baseline; do NOT describe as "unchanged-corpus." Applied →
  8-line surgical edit; JSON reformat caught mid-flight and reverted to
  targeted string edit only.
- **D-Q3 YES** — shared "pointer-intent registry" primitive as forward-
  carry Playbook-v0.9-candidate; NOT built in S2827. Post-Pattern-D
  trigger evaluation.
- **D-Q4 YES** — literal-filename queries (Q20 + explicit CLAUDE.md /
  00-START-NEXT-SESSION literal) belong in Pattern D. Pattern C owns
  SEMANTIC pointer intent: "where to begin / where to continue /
  session-start guidance / project rules."
- **D-Q5 YES** — merge order: implement + measure → atomic PR → close
  S2827 → open Pattern D as separate arc → NO Pattern B refactor in
  S2827.

## §5 Post-implementation measurement evidence — verbatim

### §5.1 — Chris D-Q1 tuning discipline (bonus sweep + margins)

Baseline anchor-vs-competitor gaps (2026-07-19 22:25 PT):

| qid | anchor | anchor raw sim | top-1 non-anchor sim | gap |
|---|---|:-:|:-:|:-:|
| Q14 | `00-START-NEXT-SESSION.md` | 0.4569 | 0.6816 | +0.2247 |
| Q15 | `00-START-NEXT-SESSION.md` | 0.2605 | 0.3843 | +0.1238 |
| Q16 | `00-START-NEXT-SESSION.md` | 0.3146 | 0.4422 | +0.1276 |
| Q17 | `CLAUDE.md` | 0.3833 | 0.4723 | +0.0889 |

Static-bonus sweep:

| Bonus | Q14 | Q15 | Q16 | Q17 | Positive conversions | Negative gate over-fires |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0.05 | ✗ | ✓ | ✗ | ✗ | 1/4 | 0/8 |
| 0.10 | ✗ | ✓ | ✗ | ✓ | 2/4 | 0/8 |
| 0.15 | ✗ | ✓ | ✓ | ✓ | 3/4 | 0/8 |
| 0.20 | ✗ | ✓ | ✓ | ✓ | 3/4 | 0/8 |
| **0.23** | **✓** | **✓** | **✓** | **✓** | **4/4** | **0/8** |
| 0.25 | ✓ | ✓ | ✓ | ✓ | 4/4 | 0/8 |

**Selected: `_SELF_REFERENCE_INTENT_BONUS = 0.23`.** Smallest reliable
adjustment; Q14 was the limiting case; negative controls hold at every
tested value (gate is regex-narrow, not bonus-dependent).

### §5.2 — Per-query positive evidence

| qid | query | anchor natural? | injected? | orig sim | bonus | eff sim | final rank |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Q14 | `the next session start doc` | False | True | 0.4569 | +0.23 | 0.6869 | **1** |
| Q15 | `where do I start` | False | True | 0.2605 | +0.23 | 0.4905 | **1** |
| Q16 | `start here` | False | True | 0.3146 | +0.23 | 0.5446 | **1** |
| Q17 | `project rules` | False | True | 0.3833 | +0.23 | 0.6133 | **1** |

All 4 rows: anchor was absent from natural top-N pool; injected under
same filter chain; bounded bonus applied; final rank 1.

### §5.3 — Negative controls

| id | query | top-1 file | gate name | fired | injected? | verdict |
|---|---|---|---|:-:|:-:|:-:|
| N1 | `add a new spider` | (handoff doc) | None | False | False | ✓ |
| N2 | `how many spiders` | `docs/PLATFORM_INVENTORY.md` | count | True | False | ✓ (count gate) |
| N3 | `morning brief workflow` | (handoff doc) | None | False | False | ✓ |
| N4 | `where do I start with a new spider` | `docs/roadmap/06-SPIDER-HEALTH.md` | self_reference | True | False | ✓ (topic competitor legitimately outranks anchor) |
| N5 | `start the celery worker` | (handoff doc) | None | False | False | ✓ |
| N6 | `project rules for spiders` | `CLAUDE.md` | self_reference | True | True | ✓ (pointer intent wins) |
| N7 | `what does the platform inventory list` | `docs/PLATFORM_INVENTORY.md` | None | False | False | ✓ |
| N8 | `PLATFORM_INVENTORY` (literal) | (research doc) | None | False | False | ✓ (Pattern D forward-carry) |
| N9 | `session start reflection` | (handoff doc) | None | False | False | ✓ (v2 tightening) |
| N10 | `00-START-NEXT-SESSION` (literal) | (handoff doc) | None | False | False | ✓ (Pattern D forward-carry) |
| N11 | `CLAUDE.md` (literal) | (handoff doc) | None | False | False | ✓ (Pattern D forward-carry) |

**Injection frequency:** gate fired 6× across 15 tested queries; actual
anchor injection performed 5× (anchor was not already in oversample pool).

### §5.4 — Pattern B COUNT regression check

`How many spiders` → top-1 `docs/PLATFORM_INVENTORY.md`, sim 0.5577,
effective 0.6077, `count_bonus=0.05`, `gate=count`. **No regression.**

### §5.5 — Full 18-row Phase-0.5 re-measurement (post-corpus-correction)

Corpus label repair applied: Q14/Q15/Q16/Q20 strict + loose targets
`docs/00-START-NEXT-SESSION.md` → `00-START-NEXT-SESSION.md`. Post-
correction corpus is the authoritative baseline going forward (per
Chris D-Q2 directive; this is NOT an unchanged-corpus comparison).

| Session | Strict top-1 hits | Delta | Mechanism family |
|---|:-:|:-:|---|
| S2825 baseline | 0/16 = 0.0% | — | none |
| S2826 (metadata repair + Pattern B) | 6/18 = 33.3% | +6 | 3× Pattern B + 3× metadata repair alone |
| **S2827 (Pattern C + corpus repair)** | **10/18 = 55.6%** | **+4** | **4× Pattern C SELF_REFERENCE** |

### §5.6 — Pytest coverage

34/34 PASSING (`tests/unit/test_s2827_pattern_c_self_reference_gate.py`):
- 12 positive gate-fire cases
- 16 negative gate-hold cases
- 6 wiring invariants (pattern↔anchor sync, anchor path defect prevention,
  return-type tuple, dedup, multi-anchor)

## §6 Pattern C measured boundary summary (permanent architectural record)

Per Chris close directive 2026-07-19: added to
`docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured Boundary Summary
(S2827 addendum) as companion to S2826 §retrieval-failure-diagnosis-order.

Concise summary (verbatim from that section):

- **Selected bonus:** `+0.23` (smallest tested value converting all
  intended semantic SELF_REFERENCE rows).
- **Q14 was the limiting case** (largest measured similarity gap).
- **All 4 positives required injection** (canonical anchor absent from
  natural candidate pool).
- **Pattern B COUNT regression** remained clean.
- **Negative controls** remained clean, including ambiguous-pointer
  cases (N4 where topic competitor legitimately won).
- **Literal-filename ownership** intentionally deferred to Pattern D.
- **Corpus label repair** was ground-truth correction, not benchmark
  optimization.

Full details: `docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured Boundary
Summary + design doc §7.5.

## §7 Twin-pointer

Per parent handoff pattern + memory `feedback_twin_deliverable_at_every_ratification`:

- **Repo doc:** this handoff at merge SHA `47f3650d1`
- **Workspace deliverable:** `5d064c40-3f09-4487-94a4-993aac14cf12`
  in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)
  — created via ORM-direct at S2827 close per memory
  `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`
  (bypasses pa_deliverables_tool diagnostic-flag bug); type
  `ratification_record`, category `governance`, status `ready`, pinned,
  `diagnostic_status=None` (cleared).

## §8 Lessons for S2828

1. **Pattern D is the next arc — literal-filename policy class.** Q20
   + Q24 forward-carried. Design should mirror Pattern C shape but
   with literal-filename anchor-by-name gate (compile filename
   variants; case-insensitive; strip extensions). After Pattern D
   ships, the "pointer-intent registry" primitive becomes a 3-instance
   codification candidate.
2. **Chris D-Q1 "smallest reliable adjustment" discipline is
   generalizable.** For any bounded-policy-bonus mechanism: sweep
   values; find smallest that meets acceptance; record margins in the
   design doc §7.x evidence table. Do not retune to reach a projected
   number — report the actual result.
3. **JSON mass-reformat trap.** `json.dump(indent=2)` on a file that
   uses mixed inline+indented formatting will produce a large diff
   even for a small semantic change. Prefer targeted string edits
   (`Edit` tool with `replace_all=True`) for label repairs. Caught
   this in-session via `git diff --stat` before staging.
4. **Corpus label defect discovery via ORM query.** The
   `docs/00-START-NEXT-SESSION.md` path defect was caught by a
   simple ORM query on `Document.file_path` — same "step 1 metadata
   inspection" discipline S2826 codified. Extending: whenever a
   corpus/benchmark labels a target that doesn't resolve in the
   Document table, that's ground-truth-repair territory (Chris D-Q2),
   not mechanism-tuning territory.
5. **Rigby SIGN Q1 refinement was load-bearing.** Removing the
   literal-filename patterns from Pattern C v1 preserved Chris D5
   distinct-mechanism-per-class discipline that Chris later ratified
   explicitly in D-Q4. Rigby's SIGN caught this BEFORE Chris routing —
   validates the "reach agreement with Rigby before Chris yes/no"
   pattern.
6. **N4/N6 negative controls demonstrate retrieval integrity in
   action.** When the pointer-intent gate fires on a semantically
   ambiguous query and a topic-specific competitor legitimately
   outranks the anchor, Pattern C does NOT force-rank the anchor.
   That's the Chris D3 "retrieval must prove retrieval" invariant.
   Future Pattern D should carry the same invariant.

## §9 Current repository state (S2827 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `47f3650d1` (S2827 PR #3267 merge) + close-cascade cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged; v0.9-candidate sync-update-path-completeness discipline 3/2 triggers ready) |
| Playbook rule count | 205 (unchanged) |
| Phase-0.5 arc state | **Pattern C SHIPPED. Post-Pattern-C baseline: 10/18 = 55.6% strict top-1. Pattern D queued for S2828.** |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2826 pin | `pa-def161f46bb2419f` (retired at S2826 close) |
| S2827 pin | `pa-fdf0a44a75b34e8f` (label `s2827-pattern-c-self-reference-injection`, retired at S2827 close, force=true, fifty-eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2828 open) |
| Session close cascade | THIS session — S2827 |
| Docs cascade | 4-step per feedback_docs_cascade_at_every_close (build_docs_index / build_rag_corpus / sync_docs_index_to_documents / embed_documents --all-unembedded) |
| Recycle post-merge | ✅ `make celery-recycle` executed after #3267 merge (PLAYBOOK-7.4.4) |
| Metadata layer health | ✅ 0 mismatches vs docs/_index.json (post-S2826, unchanged) |

## §10 Twin-pointer card (for S2828 open protocol)

📁 **Repo — S2827 artifacts:**

- **Pattern C implementation:** `core/rag_integration.py` §S2827 Pattern C (patterns/anchors/gate at :106-217; composition at :377-395; drift WARN at :499-522)
- **Corpus label repair:** `docs/research/discovery_layer/PHASE_0_5/corpus.json` (Q14/Q15/Q16/Q20 strict + loose targets)
- **Design + measurement evidence:** `docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md` (§7.5 full evidence)
- **Pattern C measured boundary summary:** `docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured Boundary Summary (S2827 addendum)
- **Pytest:** `tests/unit/test_s2827_pattern_c_self_reference_gate.py` (34 tests)
- **This handoff:** `docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md`
- **Merge SHA:** `47f3650d1` · **PR:** #3267

🖥️ **Workspace UI — S2827 twin-pointer workspace deliverable:**

- **`5d064c40-3f09-4487-94a4-993aac14cf12`** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) — type `ratification_record`, category `governance`, status `ready`, pinned. ORM-direct create bypasses `pa_deliverables_tool` diagnostic-flag bug per memory `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.

## §11 Appendix — Provenance

- **Predecessor:** S2826 (metadata sync-drift repair + Pattern B COUNT gate; PR #3265, SHA `9c53ab880`)
- **Novel this session:** first empirical validation of the Chris D-Q1 "smallest reliable adjustment" discipline via static-bonus sweep with per-value negative-control fire count; first arc to combine ratifiable engineering artifact + ground-truth benchmark-label repair in a single atomic PR (per Chris D-Q2 "not benchmark tuning"); first application of Rigby-SIGN-then-Chris-D-verdict-then-implementation sequence with 5-question mirror of the S2826 shape.
- **Chris D-verdict cascade:** D-Q1..D-Q5 all YES-with-refinements — refinements applied verbatim to the shipped implementation.
- **Rigby SIGN cycle:** 5 questions → 4 DISAGREE + 1 AGREE-with-caveat → reconciled v2 with all refinements applied → joint Claude+Rigby agreement → Chris D-verdict.
