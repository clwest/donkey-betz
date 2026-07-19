---
title: "S2830 — Pointer-Intent Registry Step 1 (Design Ratification + DORMANT Substrate)"
session: 2830
date: 2026-07-19
status: shipped
authority: implementation + governance
scope: |
  S2830 opened with sanity checks green (metadata layer 0 mismatches;
  Pattern B/C/D top-1 canonical; --apply guard active). Chris ratified
  the S2828 recommended default (shared "pointer-intent registry"
  primitive design per D-Q3/D-Q7 forward-carry). Design doc authored
  at docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md
  (827 lines). Joint Claude+Rigby SIGN over 3 cycles reached agreement:
  cycle 1 verdicts + refinements applied; cycle 2 caught real
  §7.3-vs-§5.2 inconsistency (Rigby DISAGREE); cycle 3 verified fix +
  overall verdict "design-ready-for-Chris-D-verdict = YES". Chris D-
  verdict "ship step 1" ratified DORMANT substrate: IntentMechanism
  protocol + Count/SelfReference/LiteralFilename subclasses +
  INTENT_MECHANISMS registry tuple added to core/rag_integration.py.
  search_embeddings() control flow UNCHANGED. 15-case parity harness +
  13 registry smoke tests + 95 pre-existing Pattern C/D regression =
  123/123 PASS. Merged as PR #3273, SHA `095612efd`. `make recycle-all`
  clean post-merge per PLAYBOOK-7.4.4. SEVENTY-FIFTH close-cycle
  post-PLAYBOOK-7.4.4.
predecessor: docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md
merge_pr: 3273
merge_sha: 095612efd
---

# S2830 — Pointer-Intent Registry Step 1 (Design Ratification + DORMANT Substrate)

## §1 Session shape

Chris opened S2830 with "Please begin". Sanity checks per S2829
handoff §Recommended session-open protocol all green: postgres pg15
started clean; `backfill_document_status_from_docs_index --dry-run` =
0 mismatches; Pattern B/C/D queries returned canonical top-1 with no
DRIFT WARN; bare `backfill_document_status_from_docs_index` correctly
rejected with `CommandError`. S2829 substrate hardening intact.

Chris ratified the S2828 D-Q3/D-Q7 forward-carry recommended default:
shared "pointer-intent registry" primitive **design-only** (evaluate,
not build). Design doc authored to §4 close-brief shape from S2828
(shape survey → shape divergence → primitive shape proposal → zero-
behavior-change guarantee → migration sequence).

Joint Claude+Rigby SIGN cycle 1: 5 questions with explicit anti-
rubber-stamp directive (S2777 memory rule). Rigby returned tool-
grounded verdicts backed by 5+ `repo_tool.read_file` calls over
`core/rag_integration.py` (Pattern B `:60-105`, Pattern C `:106-255`,
Pattern D `:258-480`, orchestration + composition `:683-925`, WARN
`:1003-1082`) and the design doc.

Cycle 1 verdicts: Q1/Q2/Q3 AGREE WITH NUANCE with specific refinement
targets; Q4 AGREE with hard-boundary refinement; Q5 zoom-out raised
three anti-worship concerns (intent_gate_name calcification; base_qs
protocol rigidity; premature primitive-worship). Rigby overall read:
*"Ratifiable as design-only if the doc tightens the above nuances
and keeps Step 1 purely dormant + tests (no routing change)."*

R1-R5 refinements applied verbatim to §3.5, §4.1, §5.2, §5.4, §6.
Cycle 2 re-verify caught a real internal inconsistency: §7.3 still
said "30 queries" contradicting §5.2's coverage-criteria framing and
Step 1's "15-case manifest" language. Rigby DISAGREE was substantive.
§7.3 rewritten to reference "15 coverage-criteria case classes …
cardinality is a side effect of coverage, not a target … MUST NOT be
trimmed below 15-case minimum." Cycle 3 verify returned R3 AGREE +
Overall verdict **YES**.

Joint Claude+Rigby agreement reached per S2753 discipline. Chris D-
verdict "ship step 1" ratified.

## §2 Root-cause investigation

N/A — this session was a design ratification + DORMANT substrate
ship, not a bug triage. No root-cause investigation was performed.
The predecessor S2829 handoff covers the drift-repair substrate that
S2830 lands on.

## §3 Rigby joint SIGN records (3 cycles, tool-grounded)

### §3.1 Cycle 1 — 5 questions, tool_runs verified

Dispatched via `tools/pa_local.sh` on pin `pa-f6341a9fe3de414a`. Rigby
returned:

| Q | Verdict | Refinement direction |
|---|---|---|
| Q1 skeleton characterization | AGREE WITH NUANCE | `intent_gate_name` is query-level precedence, NOT per-row match truth |
| Q2 protocol shape stress | AGREE WITH NUANCE | fetch_candidate_chunks() optional + default no-op; base_qs Optional |
| Q3 verification method | AGREE WITH NUANCE | "30 queries" → coverage criteria + minimum required cases |
| Q4 migration sequencing | AGREE | Hard line: Step 1 must NOT change runtime dispatch |
| Q5 zoom-out | (no verdict; 3 concerns) | Anti-worship guardrails (§5.4 new) |

Anti-rubber-stamp discipline verified: 5+ `repo_tool.read_file` +
verdicts cited specific line ranges (e.g. `:889-902`, `:250-253`,
`:1003-1082`). Not rubber stamp.

### §3.2 Cycle 2 — verify R1-R5

Rigby re-read v2 design and returned R1/R2/R4/R5 AGREE + **R3
DISAGREE**: §7.3 still asserted "30 queries" contradicting §5.2's
coverage-criteria + Step 1's "15-case manifest." Substantive catch.

### §3.3 Cycle 3 — verify §7.3 fix

§7.3 rewritten to align with §5.2 coverage-criteria framing. Rigby
re-read lines 696-705 + returned R3 AGREE + **Overall verdict:
design-ready-for-Chris-D-verdict = YES**.

Joint Claude+Rigby agreement reached before Chris routing per S2753
discipline.

**ChatConversation record**: rows 3641 (cycle 1) / 3643 (cycle 2) /
3644 (cycle 3) via pin `pa-f6341a9fe3de414a`.

## §4 Chris D-verdict

Chris routed via terminal ("let's go with the registry design" →
"ship step 1"). Design ratified for Step 1 implementation. Step 2
(actual behavior-preserving refactor to wire `INTENT_MECHANISMS` into
`search_embeddings()` control flow) explicitly deferred to a
**separate SIGN arc + fresh Chris D-verdict** per design §6 and
Rigby SIGN Q4 hard-boundary refinement.

## §5 Implementation

### §5.1 PR #3273 (SHA `095612efd`)

Files changed: 8 (1875 insertions / 1 deletion).

| File | Change |
|------|--------|
| `core/rag_integration.py` | +271 lines: IntentMechanism base + CountMechanism + SelfReferenceMechanism + LiteralFilenameMechanism + `INTENT_MECHANISMS` tuple. Classes are thin wrappers over existing standalone functions (`_detect_count_intent`, `_detect_self_reference_intent`, `_detect_literal_filename_intent`, `_fetch_self_reference_anchor_chunks`, `_fetch_literal_filename_anchor_chunks`). Zero-behavior-change by construction — delegation to existing paths. |
| `docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md` | New — 827-line design doc with 3-cycle Rigby SIGN record |
| `tests/regression/rag_registry_parity/__init__.py` | New |
| `tests/regression/rag_registry_parity/manifest.py` | New — 15-case coverage-criteria manifest per §5.2 |
| `tests/regression/rag_registry_parity/test_parity.py` | New — parametric parity test; log-driven observability (DB-state-independent) |
| `tests/regression/__init__.py` | New |
| `tests/unit/test_intent_mechanism_registry.py` | New — 13 registry-shape smoke tests |
| `tools/pa_local.sh` | Fresh S2830 pin `pa-f6341a9fe3de414a` |

### §5.2 Contract highlights (Rigby SIGN refinements landed)

- **Non-injecting mechanisms** (Pattern B): `injects_candidates() → False`;
  registry short-circuits before calling `fetch_candidate_chunks()`.
  No forced stubs (Rigby SIGN Q2 refinement).
- **`base_qs: Optional[QuerySet]`** — mechanisms MAY ignore. Pattern
  D drops it entirely (Rigby SIGN Q2 refinement).
- **Canonicalization + MISS log** are mechanism-owned. Pattern D's
  `_canonicalize_literal_filename_token` continues to live inside
  its detect() path; its INFO log continues to fire via `emit_miss_log()`.
- **Anti-worship guardrails** (§5.4): three explicit revisit triggers
  (intent_gate_name representation; base_qs universalization; uniform-
  shape shoehorning). Rigby SIGN Q5 concerns codified as design
  invariants.

### §5.3 Test coverage — 123/123 PASS

- **15 parity cases** (`tests/regression/rag_registry_parity/test_parity.py`)
  — no-gate baseline, each Pattern gate firing, MISS path, exclude-id
  dedupe, drift WARN scenarios, authority_weighted paths, Q28 no-
  perturb, whole-string invariant, two-mechanism co-fire (case_14
  documents current disjointness-collision behavior), empty query
- **13 registry smoke tests** (`tests/unit/test_intent_mechanism_registry.py`)
  — registry shape, precedence, protocol conformance, name/prefix
  uniqueness, injecting-vs-non-injecting behavior, canonical target
  paths match source-of-truth, dormancy meta-assertion
- **34 Pattern C regression** — zero regression
- **61 Pattern D regression** — zero regression
- **Total**: 123/123 PASS

### §5.4 Post-merge

- Merged via `gh pr merge --admin --squash --delete-branch 3273`
  (per `feedback_gh_pr_merge_admin_until_billing_fixed` while CI
  billing remains broken).
- `make recycle-all` completed cleanly: sha=`095612efd6ad`, surviving=none.
  Recycle event recorded in `logs/recycle_events.jsonl` (SEVENTY-FIFTH
  post-PLAYBOOK-7.4.4).

## §6 Pass gates verified

| Gate | Check | Result |
|------|-------|--------|
| (i) | Design doc + 3-cycle SIGN + joint agreement | ✓ |
| (ii) | Chris D-verdict ratified | ✓ |
| (iii) | `search_embeddings()` control flow UNCHANGED (verified by `test_registry_dormant_at_step_1`) | ✓ |
| (iv) | 95/95 existing Pattern C+D pytest PASS (no regression) | ✓ |
| (v) | 15/15 parity harness PASS | ✓ |
| (vi) | 13/13 registry smoke tests PASS | ✓ |
| (vii) | S2829 substrate intact: metadata 0 mismatches; `--apply` guard active; Pattern B/C/D top-1 canonical | ✓ |
| (viii) | Post-merge recycle-all clean at merged SHA | ✓ |

## §7 Lessons

1. **Rigby SIGN cycle 2 caught a real internal inconsistency
   Claude missed.** §7.3 still said "30 queries" while §5.2 had been
   updated to coverage-criteria and Step 1 was labeled "15-case
   manifest." Substantive DISAGREE — not rubber stamp. Anti-rubber-
   stamp discipline (S2777) held through 3 cycles.
2. **Log-driven parity assertions are more robust than result-row
   assertions for RAG.** Test-DB is empty; result rows are []; the
   observable branches (gate active flags, drift WARN emission, MISS
   log) all live in log records regardless of DB state. Parity
   harness reads observables from log records only.
3. **Django logger propagation matters for caplog.** `core` logger
   has `propagate: False` in settings.py, so caplog (attached to
   root) never receives records. Fix: fixture attaches `caplog.handler`
   directly to `core.rag_integration` logger.
4. **Thin wrappers preserve zero-behavior-change by construction.**
   The registry mechanism classes call the exact same standalone
   functions the current `search_embeddings()` uses. No new code
   path — dormant means dormant.
5. **Case_14 documents current disjointness-collision behavior.**
   "how many where do I start" fires BOTH Pattern B (COUNT) AND
   Pattern C (SELF_REFERENCE); the current precedence resolves
   `intent_gate_name` to 'count'. This is captured behavior, not
   drift. Step 2 refactor MUST preserve it.
6. **DO NOT wire the registry into search_embeddings() at Step 1.**
   Step 2 requires separate SIGN arc + fresh Chris D-verdict per
   Rigby SIGN Q4 hard boundary refinement. Any Step 1 PR that
   touches search_embeddings control flow is out-of-scope.
7. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer
   contract still active (unchanged).
8. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-
   order defect closure still active (unchanged).
9. **DO NOT collapse Pattern B/C/D anchor maps, bonuses, or gate
   patterns** — Chris D5 distinctness contract is now codified in
   design §3 as anti-collapse invariant.

## §8 Follow-up carry

### §8.1 Step 2 candidate arc (deferred)

Step 2 = refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`.
Requirements before opening:

- **Fresh SIGN cycle** — Rigby joint SIGN with focus on: (a) log-line
  preservation verbatim; (b) diagnostic-field shape preservation; (c)
  precedence + injection order preservation; (d) golden-file diff PASS.
- **Fresh Chris D-verdict** — separate architectural arc per Rigby
  SIGN Q4.
- **Golden-file parity fixture from Step 1** — captured baseline; must
  deep-equal post-refactor.
- **95/95 Pattern C+D pytest PASS** post-refactor.

### §8.2 Step 3 candidate (further deferred)

Optional file-organization: move mechanism classes to
`core/rag/intent_mechanisms/*.py`. Trigger: only if a 4th mechanism
(Pattern E) is proposed AND Chris D-verdicts that file-organization
benefit outweighs the churn.

### §8.3 Pattern E readiness

Design §5.4 anti-worship guardrails codify three revisit triggers:
(1) any co-firing mechanism proposal forces `intent_gate_name`
representation revisit; (2) any proposal requiring `base_qs`
universalization forces protocol refinement under new SIGN; (3) any
Step-2 evidence that mechanisms only fit via awkward stubs → DEFER
Step 2. These guardrails preserve Chris D5 distinctness across
future extensions.

### §8.4 Other open follow-ups (unchanged from S2829)

- **PR3 S2829 (canonical-anchor invariant + divergent-retrieval-stack
  diagnostic)** — still deferred as separate architectural arc.
- **13 out-of-index Document rows** — still deferred per Chris D6.
- **Playbook v0.9 amendment authoring** — sync-update-path-completeness
  discipline. Trigger count now potentially 4/2 (S2826 §5.2 fold +
  S2829 skip-branch hole + S2830 might not add — evaluate at S2831+).
- **Colorado Phase 4** — statute-citation content quality.
- **BettingPage first-user trace** — real user-facing capability.

## §9 Twin-pointer card

📁 **Repo — S2830 artifacts:**

- **DORMANT registry substrate:** `core/rag_integration.py`
  (`IntentMechanism` base + `CountMechanism` + `SelfReferenceMechanism`
  + `LiteralFilenameMechanism` + `INTENT_MECHANISMS` at `:483-799`)
- **Design doc:** `docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md`
- **Parity harness:** `tests/regression/rag_registry_parity/`
  (manifest + parametric test + fixture attaching caplog handler
  directly to `core.rag_integration` logger)
- **Smoke tests:** `tests/unit/test_intent_mechanism_registry.py`
  (13 tests)
- **Merge SHA:** `095612efd` · **PR:** #3273
- **This handoff:** `docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md`

🖥️ **Workspace UI — S2830 twin-pointer deliverables:**

To mint at close cascade (ORM-direct per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`):

- **Content mirror**: `initiative_phase_doc` in Donkey Betz workspace
  (`b4503364-2573-4401-9e28-61a739e0ce50`), category `governance`
  (design doc engineering truth).
- **Ratification envelope**: `ratification_record` in Donkey Betz
  workspace, category `governance`, `diagnostic_status=None`.

## §10 Current repository state (S2830 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `095612efd` (S2830 PR #3273 merge) + close-cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Phase-0.5 arc state | **Pattern B/C/D SHIPPED (S2826/S2827/S2828). Post-Pattern-D baseline: 12/18 = 66.7% strict top-1. S2830 shipped shared "pointer-intent registry" DORMANT substrate — Step 1 of §6 migration.** |
| Metadata layer | ✅ 0 mismatches; --apply guard active; sync skip-branch closure active (S2829 substrate intact) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2829 pin | `pa-d3a4d67126b64e7f` (retired at S2829 close) |
| S2830 pin | `pa-f6341a9fe3de414a` (label `s2830-pointer-intent-registry-primitive-design`, retired at S2830 close, force=true, sixty-first consecutive per S2770+) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2831 open) |
| Session close cascade | THIS session — S2830 |
| Docs cascade | 4-step per `feedback_docs_cascade_at_every_close` (build_docs_index / build_rag_corpus / sync_docs_index_to_documents / embed_documents --all-unembedded) + build_docs_provenance |
| Recycle post-merge | ✅ `make recycle-all` executed after #3273 merge (PLAYBOOK-7.4.4, seventy-fifth consecutive) |

## §11 Appendix — Provenance

- **Predecessor**: S2829 (Canonical Anchor Drift Triage; PR #3271, SHA `584f13026`)
- **Novel this session**:
  - First arc where the S2828 D-Q3 forward-carry (3-instance
    codification threshold) advanced from "candidate" to "DORMANT
    substrate ratified."
  - First joint Rigby SIGN cycle sequence to catch a real internal
    inconsistency at cycle 2 (§7.3-vs-§5.2 contradiction) — anti-
    rubber-stamp discipline validated across 3 cycles.
  - First parity harness using log-driven observability (DB-state-
    independent) — captures observable branches via log records
    only, insulating Step 2's zero-behavior-change proof from
    fixture-DB divergence.
  - First registry primitive shipped as DORMANT — the classes exist
    but no code path calls them, preserving the Chris D-Q7
    "evaluate as separate arc" boundary as a mechanical invariant
    (verified by `test_registry_dormant_at_step_1`).
- **Chris D-verdict**: "let's go with the registry design" → design
  ratified → "ship step 1" → DORMANT substrate shipped.
- **Rigby SIGN cycles**: 3 total (cycle 1: 5 Q + 5+ tool_runs → 4
  AGREE-with-refinement + 1 zoom-out; cycle 2: R1-R5 verify + real
  §7.3 DISAGREE; cycle 3: R3 verify AGREE + Overall YES).
