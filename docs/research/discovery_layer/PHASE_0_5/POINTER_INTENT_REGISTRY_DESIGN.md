---
title: "Pointer-Intent Registry — Shared Skeleton Extraction Design (Pattern B/C/D)"
session: 2830
authored: 2026-07-19
status: draft — awaiting Rigby joint SIGN
authority: engineering
scope: |
  Extract the shared 6-stage skeleton (detect → resolve → inject → bonus
  → diagnose → drift-WARN) that Pattern B (COUNT, S2826), Pattern C
  (SELF_REFERENCE, S2827), and Pattern D (LITERAL-FILENAME, S2828)
  independently duplicate in `core/rag_integration.py` into a single
  `IntentMechanism` protocol + `INTENT_MECHANISMS` registry. Preserves
  Chris D5 distinct-mechanism-per-class discipline: each mechanism keeps
  its own gate patterns, anchor map, bonus values, canonicalization
  rules, MISS-path behavior, and diagnostic field names. The registry
  is a **shape-lifting refactor** — semantics unchanged, distinctness
  preserved, extension shape formalized for future Pattern E.
predecessor: docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md
governing_envelope: docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md
triggers:
  - S2826 shipped Pattern B (COUNT) as 1st instance of the skeleton
  - S2827 shipped Pattern C (SELF_REFERENCE) as 2nd instance
  - S2828 shipped Pattern D (LITERAL-FILENAME) as 3rd instance — Chris
    D-Q3 forward-carry at S2828: "3-instance codification threshold met"
  - Chris D-Q7 S2828: "Evaluate as separate arc post-Pattern-D-ship"
constraints:
  - Chris D-Q3/D-Q7 S2828: zero-behavior-change guarantee is
    load-bearing; every named diagnostic field, precedence, injection
    order, and WARN prefix survives verbatim
  - Chris D5 distinct-mechanism-per-class: MUST NOT collapse gates,
    bonuses, or anchor maps across mechanisms — the registry HOSTS
    three distinct instances, it does NOT unify their contents
  - Chris D3 retrieval-integrity: bounded bonus, NOT force-rank-1;
    invariant survives per-mechanism
  - Chris D6 no `include_superseded` relaxation: preserved
  - Migration is per-mechanism-sequential + individually-reversible;
    no big-bang rewrite
---

# Pointer-Intent Registry — Shared Skeleton Extraction Design

## §0 — Rigby joint SIGN reconciliation summary (v2 — cycle 1 verdicts + R1-R5 refinements applied)

**Cycle 1 dispatch (2026-07-19)**: 5 questions routed with explicit
anti-rubber-stamp directive (S2777 memory rule). Rigby returned
substantive verdicts backed by `repo_tool.read_file` × 5+ over
`core/rag_integration.py` (lines 1-260, 260-760, 760-1020, 1020-1200)
and this design doc. Tool_runs non-empty verified before treating
verdicts as substantive.

| SIGN Q | Rigby verdict | Refinement applied in v2 | Section |
|---|---|---|---|
| Q1 skeleton characterization | **AGREE WITH NUANCE** | `intent_gate_name` clarified as **query-level precedence**, not per-row match truth; co-firing would require multi-gate reporting | §3.5 |
| Q2 protocol shape stress | **AGREE WITH NUANCE** | `fetch_candidate_chunks()` made **optional** with default no-op; `base_qs` documented as `Optional[QuerySet]` that mechanisms MAY ignore; explicit non-injecting mechanism contract (Pattern B legitimate) | §4.1 |
| Q3 verification method | **AGREE WITH NUANCE** | "30 queries sufficient" replaced with **coverage criteria** + minimum required case set (MISS path, inject-skipped-by-exclude, per-mechanism drift WARN, ranking modes). Two-gate co-fire = optional future test, NOT required | §5.2 |
| Q4 migration sequencing | **AGREE** | Hard line added: **Step 1 must NOT change runtime dispatch / must NOT touch `search_embeddings()` control flow**; Step 2 labeled "requires separate SIGN arc + Chris D-verdict" | §6 |
| Q5 zoom-out concerns | 3 concerns raised, no verdict | Anti-worship guardrails codified as **§5.4** (revisit trigger for `intent_gate_name`; `base_qs` optional contract; refactor DEFERRED if protocol forces uniform shapes that don't reflect actual differences) | §5.4 |

**Rigby's overall read at cycle 1**: *"Ratifiable as design-only if
the doc tightens the above nuances and keeps Step 1 purely dormant +
tests (no routing change)."*

**Cycle 2 verification (2026-07-19)**: Rigby re-read the v2 design with
`repo_tool.read_file` and returned R1/R2/R4/R5 AGREE + R3 DISAGREE
(caught a real inconsistency: §7.3 still said "30 queries" contradicting
§5.2's coverage-criteria and Step 1's "15-case manifest"). Substantive
tool-grounded review — not rubber stamp.

**Cycle 3 verification (2026-07-19)**: §7.3 fixed to reference "15
coverage-criteria case classes … cardinality is a side effect of
coverage, not a target; MAY grow if a new observable branch is added,
but MUST NOT be trimmed below the 15-case minimum." Rigby re-read
lines 696-705 and returned **R3 AGREE + Overall verdict:
design-ready-for-Chris-D-verdict = YES**.

**Joint Claude+Rigby agreement reached** per S2753 discipline. Ready
for Chris D-verdict routing per §10.

---

## §1 — Purpose

Codify the shared skeleton that S2826/S2827/S2828 built by duplication.
Chris D-Q3 at S2828 was explicit: "shared 'pointer-intent registry'
primitive extraction is now a candidate arc." Chris D-Q7 S2828 was
equally explicit: "evaluate as separate arc post-Pattern-D-ship." This
design is the evaluation.

**Explicit non-goals** (per Chris D5 + D-Q7):

- **NOT** collapsing Pattern B/C/D into a single mechanism. Each keeps
  its own gate patterns, anchor map, bonus values, ceilings, MISS
  behavior, and diagnostic field names.
- **NOT** changing observable retrieval behavior. Every Phase-0.5 corpus
  query MUST return byte-identical `metadata` dict (same file_path, same
  intent_gate_name, same bonus values, same injected flag) before and
  after the registry lands.
- **NOT** adding a new Pattern E in this arc. Extension shape is
  designed for; instantiation is deferred.
- **NOT** relaxing Chris D3 retrieval-integrity, Chris D5 distinctness,
  or Chris D6 `include_superseded=False` invariants.

**Explicit goals**:

1. **Structural**: one place to look when reading, adding, or auditing
   an intent-gated mechanism. Right now the 6 stages of Pattern C are
   scattered across `core/rag_integration.py` from `:108-255` (detect +
   resolve + inject helper) through `:704-724` (inject call) through
   `:800-816` (bonus loop) through `:907-910` (diagnostic fields)
   through `~:1020` (drift WARN). Pattern D is scattered similarly. A
   future Pattern E author must currently reverse-engineer this
   scatter to build the 4th instance.
2. **Extension**: formalize the contract so Pattern E adds one class
   plus one registry entry, not six edits across four scattered
   regions.
3. **Regression protection**: a single skeleton means a bugfix (e.g.
   S2829's `include_superseded` skip-branch discovery) applies to all
   mechanisms at once, not three times independently.

---

## §2 — Shape survey (current: 3 parallel implementations)

Each mechanism traverses six stages. Verified line ranges in
`core/rag_integration.py` at merge SHA `13616934f`:

| Stage | Pattern B (COUNT) | Pattern C (SELF_REFERENCE) | Pattern D (LITERAL-FILENAME) |
|---|---|---|---|
| 1. Detect | `_detect_count_intent` `:101-105` | `_detect_self_reference_intent` `:169-189` | `_detect_literal_filename_intent` `:397-429` |
| 2. Resolve (anchor map) | `_COUNT_INTENT_BONUS` dict `:96-98` (per-file scalar) | `_SELF_REFERENCE_ANCHORS` + `_PATTERN_TO_ANCHOR` `:142-154` | `_LITERAL_FILENAME_ANCHORS` `:330-337` |
| 3. Inject | — (no injection) | `_fetch_self_reference_anchor_chunks` `:192-255` + call `:713-723` | `_fetch_literal_filename_anchor_chunks` `:432-480` + call `:735-744` |
| 4. Bonus | inline `:788-791` | inline `:800-815` | inline `:824-841` |
| 5. Diagnose | `intent_gate_fired` + `intent_gate_name` + `count_intent_bonus` `:889-903` | `self_ref_intent_bonus` + `self_ref_anchor_key` + `self_ref_matched_pattern_index` + `self_ref_injected` `:907-910` | `literal_filename_intent_bonus` + `literal_filename_anchor_key` + `literal_filename_matched_pattern_index` + `literal_filename_gate_name` + `literal_filename_injected` `:912-917` |
| 6. WARN | `[S2826_PATTERN_B_DRIFT]` `~:1003-1024` | (embedded in Pattern D block per S2827 §5.6 — same shape) | `[S2828_PATTERN_D_DRIFT]` |
| Total lines (approx) | ~30 (no inject) | ~120 | ~155 |
| Total lines (all three) | | | **~305 lines of skeleton across 3 mechanisms** |

**Precedence** (currently hardcoded at `:894-902`): `count > self_reference > literal_filename`. Documented as "for determinism; disjoint by design."

**Composition** (currently hardcoded at `:843-848`):
```
effective_similarity = similarity + count_bonus + self_ref_bonus + literal_filename_bonus
```
Additive. Any two mechanisms can theoretically fire together; the shape
is compositional even though B/C/D are disjoint by construction (Chris
D5 whole-string vs multi-word).

**Injection order** (currently hardcoded `:713-744`): self_reference
injects first, literal_filename injects second. Both dedupe via
`existing_chunk_ids`. Order is observable via which mechanism's chunk
wins the dedupe if both would inject the same document (no such case
exists today, but the invariant is set).

**Oversample trigger** (currently hardcoded at `:692-702`): any of
`authority_weighted`, `count_intent_active`, `self_reference_intent_active`,
`literal_filename_intent_active` → oversample by `limit * 3`, then
Python-side re-sort.

---

## §3 — Divergence points (what MUST NOT collapse)

Per Chris D5, each mechanism owns distinct semantics that survive the
refactor unchanged. This section is the anti-collapse contract.

### §3.1 — Gate shape divergence

| Mechanism | Gate style | Match record shape | Example fire |
|---|---|---|---|
| B COUNT | multi-word substring `\b...\b` | `bool` | "how many spiders" |
| C SELF_REFERENCE | multi-word semantic `\b...\b` | `tuple[(anchor_key, pattern_idx), ...]` | "where do I start" |
| D LITERAL-FILENAME | whole-string `^...$` | `tuple[(canonical_key, pattern_idx, gate_name), ...]` | "PLATFORM_INVENTORY" |

**Load-bearing invariants**:

- Pattern D's `^...$` whole-string anchoring IS Chris D5's disjointness
  guarantee vs Pattern B/C multi-word patterns. Substring-relaxation
  would silently break disjointness and MUST re-run Rigby SIGN + Chris
  D-verdict.
- Match record shape divergence is real, not incidental. Pattern D
  needs `gate_name` in the match record because its bonus is per-gate
  (not per-anchor).

### §3.2 — Bonus scope divergence

| Mechanism | Bonus type | Ceiling | Sizing evidence |
|---|---|---|---|
| B COUNT | `dict[file_path, float]` | none | S2825 gaps 0.025-0.026 → +0.05 flips both |
| C SELF_REFERENCE | single scalar `0.23` for all anchors | none | Q14 gap 0.2247 = tightest → +0.23 flips all four |
| D LITERAL-FILENAME | `dict[gate_name, float]`: P0=0.07, P1=0.09, P2=0.32, P3=0.03 | per-gate `dict[gate_name, float]`: P0=0.35, P1=0.20, P2=0.35, P3=0.10 | S2828 §7.5 per-gate sweep |

**Load-bearing invariant**: Pattern D's per-gate ceiling `dict` MUST NOT
be a single global constant. Chris D-Q1 S2828: "if a positive requires
a bonus > ceiling, it is NOT converted this arc (do NOT raise ceiling
to hit projection)." Per-gate scoping is the mechanism.

### §3.3 — Anchor resolution divergence

| Mechanism | Resolution style | MISS behavior |
|---|---|---|
| B COUNT | static per-file bonus dict (no injection) | N/A |
| C SELF_REFERENCE | pattern-idx → anchor-key → file_path (2-step) | fail closed (no anchor found → no bonus, no WARN) |
| D LITERAL-FILENAME | canonicalize(query) → curated anchor key → file_path; Strategy A + Strategy C | Strategy C log-only `[S2828_PATTERN_D_MISS]` INFO |

**Load-bearing invariants**:

- Pattern D's canonicalization spec (`strip → lower → strip .md → -→_`)
  is a mechanism-owned concern, not a registry concern. Registry MUST
  NOT canonicalize on behalf of a mechanism.
- Pattern D's MISS INFO log is mechanism-owned. Pattern B/C do not emit
  MISS logs today (their gate-fire → known anchor is deterministic).
  Registry MUST support optional MISS log per mechanism.

### §3.4 — Injection divergence

| Mechanism | Injects candidates | Fetch signature |
|---|---|---|
| B COUNT | **No** — bonus applies to naturally-retrieved rows only | N/A |
| C SELF_REFERENCE | Yes | `(matches, base_qs, exclude_ids, query_embedding) → list[chunk]` |
| D LITERAL-FILENAME | Yes | `(matches, exclude_ids, query_embedding) → list[chunk]` (no base_qs; rebuilds status-exclusion inline) |

**Note**: Pattern C's fetch signature takes `base_qs` (unused in the
current implementation — it inherits status exclusion inline). Pattern
D's fetch signature drops `base_qs`. Registry MUST accept this
divergence — either fetch takes `base_qs` or the mechanism inlines
status exclusion; both are current facts.

### §3.5 — Diagnostic field divergence

Each mechanism owns its own field names in the returned `documents`
dict. Registry MUST preserve every field name verbatim; downstream
consumers (95/95 pytest suite; potentially external tools) key by
literal name.

Full field list (**preservation contract**):

- **Query-level (registry-computed, precedence-based; NOT per-row match truth)**: `intent_gate_fired`, `intent_gate_name`
  - **Nuance (Rigby SIGN Q1 refinement)**: `intent_gate_name` reports the **first-active mechanism per registry precedence** at the query level. It is populated identically on every row. This is not "which mechanism matched this row" — it is "which mechanism's gate fired at this query." Today, disjoint-by-construction (Chris D5 whole-string vs multi-word) guarantees at most one mechanism fires per query, so per-row match truth and query-level precedence agree. If a future Pattern E introduces co-firing, the registry MUST revisit this representation (either multi-gate reporting like `intent_gates_fired: list[str]` or per-row gate attribution). See §5.4 anti-worship guardrails.
- **B**: `count_intent_bonus` (per-row: 0.0 or bonus value from `_COUNT_INTENT_BONUS[file_path]`)
- **C**: `self_ref_intent_bonus`, `self_ref_anchor_key`, `self_ref_matched_pattern_index`, `self_ref_injected` (all per-row)
- **D**: `literal_filename_intent_bonus`, `literal_filename_anchor_key`, `literal_filename_matched_pattern_index`, `literal_filename_gate_name`, `literal_filename_injected` (all per-row)
- **Composed (per-row)**: `effective_similarity` (similarity + all mechanism bonuses; additive)

### §3.6 — Precedence divergence

Currently hardcoded `count > self_reference > literal_filename`. This
is DOCUMENTATION of disjoint-by-construction ordering, not a live
tie-break — no query fires two gates today. Registry MUST preserve this
precedence as an explicit registry-level ordering constant, not
distribute it across mechanisms.

---

## §4 — Primitive shape proposal

### §4.1 — `IntentMechanism` protocol

Every mechanism implements this contract. Method signatures are chosen
to fit all three existing mechanisms without shape distortion. Rigby
SIGN Q2 refinement applied: `fetch_candidate_chunks()` is **optional**
via default no-op; `base_qs` is `Optional[QuerySet]` that mechanisms
MAY ignore (Pattern D already does; Pattern C accepts but rebuilds
inline). Pattern B remains cleanly non-injecting — the protocol
accommodates this via `injects_candidates() → False` short-circuit,
NOT via forcing Pattern B to implement an unused stub.

```python
class IntentMechanism(Protocol):
    """Contract for pointer-intent mechanisms in the search_embeddings
    embedding lane. Chris D5 distinct-mechanism discipline: each
    instance owns its patterns, anchors, bonuses, canonicalization,
    and diagnostic field names.

    Anti-worship contract (Rigby SIGN Q2 + Q5): the protocol accepts
    shape divergence between mechanisms. `base_qs` is Optional; a
    mechanism MAY ignore it and inline its own filter chain (Pattern D
    does this). `fetch_candidate_chunks()` has a default no-op so
    non-injecting mechanisms (Pattern B) don't ship dead stubs. If a
    future mechanism needs shape the protocol doesn't accommodate
    (e.g. multi-document joins, tool-driven retrieval), that's the
    signal to REFINE the protocol under new SIGN — not to shoehorn."""

    # Identity
    name: str
    """Machine name — 'count', 'self_reference', 'literal_filename'.
    Used for intent_gate_name precedence + diagnostic field routing."""

    drift_warn_prefix: str
    """e.g. '[S2826_PATTERN_B_DRIFT]'. Preserved verbatim from current
    log strings for grep continuity."""

    # Stage 1 — Detect
    def detect(self, query: str) -> Any:
        """Return truthy match record if gate fires, else falsy.
        Shape is mechanism-owned (bool / tuple / etc)."""

    # Stage 2 + 3 — Inject (optional, per Rigby SIGN Q2)
    def injects_candidates(self) -> bool:
        """Pattern B: False. Pattern C/D: True. Registry short-circuits
        on False — fetch_candidate_chunks is never called."""

    def fetch_candidate_chunks(
        self,
        matches: Any,
        base_qs: 'Optional[QuerySet]',
        exclude_chunk_ids: set,
        query_embedding: list[float],
    ) -> list:
        """Return list of DocumentEmbedding rows to inject. May be [].

        DEFAULT no-op: returns [] — Pattern B inherits this via
        injects_candidates()=False short-circuit and does NOT need to
        override. Only injecting mechanisms override.

        `base_qs` semantics: Optional. Mechanism MAY ignore it and
        rebuild filter chain inline. Pattern C accepts base_qs but
        currently rebuilds status exclusion inline (see current
        `_fetch_self_reference_anchor_chunks`); Pattern D drops base_qs
        entirely and rebuilds inline. Registry MUST NOT assume base_qs
        will be consulted by any given mechanism.

        Mechanism owns status-exclusion re-application per its
        historical fetch behavior (Pattern C + D both use
        `.exclude(document__status=ContentStatus.ARCHIVED)`)."""

    # Stage 4 — Bonus + Stage 5 — Diagnose (fused per row)
    def bonus_and_diagnostics_for_row(
        self, matches: Any, doc, chunk_id, injected_chunk_ids: set
    ) -> tuple[float, dict]:
        """Return (bonus_amount, diagnostic_field_dict).
        diagnostic_field_dict keys are mechanism-owned literal names
        (e.g. 'self_ref_anchor_key'). Bonus is 0.0 when this row is not
        an anchor for the fired matches; diagnostic dict still returned
        with default values (so the field is always present in the
        response — preservation contract)."""

    def default_diagnostic_fields(self) -> dict:
        """Diagnostic dict for rows on queries where gate did NOT fire.
        Ensures schema stability across all responses (some diagnostic
        fields must default to 0.0 or None even when mechanism inactive)."""

    # Stage 6 — Drift WARN
    def canonical_target_paths(self) -> set[str]:
        """File paths this mechanism claims as canonical. Used by
        drift-WARN to detect all-targets-missing shape."""

    def emit_drift_warn(self, matches, returned_doc_paths: set, query: str,
                        include_superseded: bool) -> None:
        """Emit the mechanism's drift WARN if applicable. Preserves
        each mechanism's current WARN log format verbatim."""

    # MISS path (Pattern D only)
    def emit_miss_log(self, query: str, matches) -> None:
        """Emit Strategy-C-style INFO for gate-fires-but-no-anchor.
        No-op for B/C. Registry calls this after fetch_candidate_chunks
        returns [] when matches contains a MISS record."""
```

Method count: **8 methods + 2 attributes**. Small surface. Each maps
1:1 to a current code region — no shape stretching.

### §4.2 — `INTENT_MECHANISMS` registry

A module-level ordered tuple of instances. Order encodes precedence.

```python
INTENT_MECHANISMS: tuple[IntentMechanism, ...] = (
    CountMechanism(),           # precedence: highest — 'intent_gate_name' = 'count'
    SelfReferenceMechanism(),   # precedence: middle
    LiteralFilenameMechanism(), # precedence: lowest
)
```

Adding Pattern E = write class + append instance. Removing = delete
instance. No other code touched.

### §4.3 — Orchestration in `search_embeddings`

Replace scattered inline blocks with iteration. Reference shape (not
final code):

```python
# Stage 1 — Detect all active mechanisms
active: dict[str, Any] = {}
for mech in INTENT_MECHANISMS:
    m = mech.detect(query)
    if m:
        active[mech.name] = m

# Oversample trigger (unchanged: authority_weighted OR any active)
if authority_weighted or active:
    candidate_qs = qs.order_by('distance')[:max(limit * 3, limit)]
    chunks = list(candidate_qs.select_related('document'))
else:
    qs = qs.order_by('distance')[:limit]
    chunks = list(qs.select_related('document'))

# Stage 2+3 — Injection (mechanisms that inject, in registry order)
injected_by_mechanism: dict[str, set[int]] = {}
for mech in INTENT_MECHANISMS:
    if not mech.injects_candidates() or mech.name not in active:
        continue
    matches = active[mech.name]
    existing_ids = {c.id for c in chunks}
    injected = mech.fetch_candidate_chunks(matches, qs, existing_ids, query_embedding)
    injected_ids = set()
    for row in injected:
        injected_ids.add(row.id)
        chunks.append(row)
    injected_by_mechanism[mech.name] = injected_ids
    # MISS log (Pattern D only)
    if not injected and matches:
        mech.emit_miss_log(query, matches)

# Stage 4+5 — Composition loop (bonus + diagnostics per row)
documents = []
for chunk in chunks:
    doc = chunk.document
    similarity = _compute_similarity(chunk)  # unchanged from :773-781
    total_bonus = 0.0
    diagnostics = {}
    for mech in INTENT_MECHANISMS:
        if mech.name in active:
            b, d = mech.bonus_and_diagnostics_for_row(
                active[mech.name], doc, chunk.id,
                injected_by_mechanism.get(mech.name, set()),
            )
            total_bonus += b
            diagnostics.update(d)
        else:
            diagnostics.update(mech.default_diagnostic_fields())
    effective_similarity = similarity + total_bonus
    # intent_gate_name precedence via registry order
    intent_gate_name = next(
        (m.name for m in INTENT_MECHANISMS if m.name in active),
        None,
    )
    documents.append({
        ..., # unchanged base fields
        'intent_gate_fired': bool(active),
        'intent_gate_name': intent_gate_name,
        'effective_similarity': effective_similarity,
        **diagnostics,
    })

# Sort + slice (unchanged: :936-974)
...

# Stage 6 — Drift WARN (mechanisms in registry order)
returned_paths = {(d.get('metadata') or {}).get('file_path') for d in documents}
for mech in INTENT_MECHANISMS:
    if mech.name in active:
        mech.emit_drift_warn(active[mech.name], returned_paths, query, include_superseded)
```

### §4.4 — File/module layout

Two candidates:

**Option A** (recommended for Step 1 migration): keep classes in
`core/rag_integration.py`, immediately below current standalone
functions. Zero module movement; smallest diff; matches Pattern D's
"add to existing file" precedent.

**Option B** (candidate for Step 3): extract to
`core/rag/intent_mechanisms/{count,self_reference,literal_filename}.py`.
Deferred as separate step per migration sequencing; not part of Step 1
zero-behavior-change ship.

---

## §5 — Zero-behavior-change guarantee

### §5.1 — What "zero-behavior-change" means concretely

For every query `q` in a fixed corpus, `search_embeddings(q, **kwargs)`
returns a `list[dict]` that is byte-identical (modulo Python dict key
ordering, which is insertion-order-stable in CPython 3.7+) before and
after this refactor. Specifically:

1. Same list length
2. Same `id` values in same order
3. Same `metadata` dict per row: `file_path`, `title`, `category`,
   `document_class`, `is_pinned`, `tags`, `chunk_index`, `citation`,
   `canonical_authority`
4. Same `importance_score`, `similarity_score`, `effective_similarity`
5. Same `intent_gate_fired`, `intent_gate_name`
6. Same per-mechanism diagnostic fields (`count_intent_bonus`,
   `self_ref_*`, `literal_filename_*`) — including default values
   when mechanism inactive
7. Same log lines (grep-identical WARN + MISS prefixes and content)
8. Same order of INFO/WARN log emissions

### §5.2 — Verification method

Three layers:

**Layer 1 — Existing pytest**: 95/95 Pattern C+D tests + Pattern B
smoke tests pass unchanged. If any assertion breaks, the refactor is
not zero-behavior-change.

**Layer 2 — Golden-file diff by coverage criteria** (Rigby SIGN Q3
refinement): introduce a `tests/regression/rag_registry_parity/`
fixture. Instead of a fixed query count, the manifest is designed to
cover every observable branch. Query cardinality is a side effect of
coverage, not a target.

**Coverage criteria (minimum required cases)**:

| # | Case class | Purpose | Example query |
|---|---|---|---|
| 1 | No-gate baseline | Path where no mechanism fires; sort ordering unchanged | "what's the current weather forecast" |
| 2 | Pattern B fires | COUNT gate hits + bonus applies + drift WARN absent | "how many spiders" |
| 3 | Pattern C fires | SELF_REFERENCE gate hits + inject + bonus + drift WARN absent | "where do I start" |
| 4 | Pattern D fires + curated hit | LITERAL-FILENAME gate hits curated map + inject + bonus | "PLATFORM_INVENTORY" |
| 5 | Pattern D fires + MISS path | Gate fires but no curated anchor; INFO log emitted; no bonus | "SPIDER_NETWORK" |
| 6 | Inject skipped by exclude_chunk_ids | Anchor already in oversample pool; bonus applies without duplicate row | (Phase-0.5 corpus row where anchor naturally wins) |
| 7 | Drift WARN — Pattern B | Target archived; WARN emitted; grep-identical prefix | (query firing gate against corpus with target Document.status=archived) |
| 8 | Drift WARN — Pattern C | Same shape for C | ditto |
| 9 | Drift WARN — Pattern D | Same shape for D | ditto |
| 10 | authority_weighted=True + no intent gate | Weighted ranking path; oversample; tie-break by updated_at DESC, doc.id ASC, chunk.id ASC | any query with kwarg |
| 11 | Intent oversample + authority_weighted=True | Both paths compose; effective_similarity used in weighted_score | query firing gate + kwarg |
| 12 | Q28 no-perturb (Pattern D natural win) | Gate fires + P3 miss-path skips inject; naturally-winning anchor rank 1 preserved | "2701_docs_inventory_topology_audit" |
| 13 | Whole-string invariant | Pattern D gate holds on natural-lang query mentioning filename | "please open CLAUDE.md" |
| 14 | Pattern B/C/D disjointness | No query fires two gates today; assertion holds | (any 3 above) |
| 15 | Empty query | Edge case; all gates return falsy; empty pool | "" |

**Optional (NOT required for Phase-0.5)**: two-mechanism co-fire. No
such query exists in the corpus today. Adding this as a required test
would be scope creep against the current disjoint-by-construction
invariant. Recorded as a **future-invariant test** to add when/if a
mechanism intentionally overlaps (see §5.4 anti-worship guardrail).

Post-refactor, all 15 case classes → deep-equal snapshot. Zero drift
tolerated. This fixture is authored as part of Step 1 (before any
registry code lands) so it captures HEAD behavior.

**Layer 3 — Log-line diff**: same 15-case manifest captured as raw log
lines pre- and post-refactor; ordered diff = empty. Ensures INFO/WARN
prefixes, MISS log content, and drift WARN payload all preserved
verbatim.

### §5.3 — What's explicitly NOT changing

- No new corpus rows
- No new anchors
- No new bonus values
- No new ceilings
- No new gate patterns
- No new diagnostic field names
- No new WARN prefixes
- No `include_superseded` default change
- No authority-weighted path change
- No sort/tie-break change

### §5.4 — Anti-worship guardrails (Rigby SIGN Q5 codification)

Three explicit guardrails against the "premature primitive-worship"
risk Rigby raised at Q5. Each has a trigger condition that, if
observed, forces a re-evaluation rather than silent accommodation.

**Guardrail 1 — `intent_gate_name` representation revisit trigger**

Today `intent_gate_name` is a scalar picked from registry precedence.
The scalar-shape is valid only while gate-firing is disjoint by
construction (Chris D5 whole-string vs multi-word). **Trigger**: any
proposal (Pattern E or later) that would allow two mechanisms to fire
on the same query forces a design revision of `intent_gate_name` (to
`list[str]` or per-row attribution) BEFORE the co-firing mechanism
lands. Not doing so silently misrepresents diagnostics.

**Guardrail 2 — `base_qs` optional contract**

Two current mechanisms (C, D) diverge on whether they consume `base_qs`.
The protocol accepts this. **Trigger**: if a future mechanism proposal
requires `base_qs` to be UNIVERSAL (i.e. proposes making all mechanisms
consult it), that's the signal that a different retrieval substrate is
emerging — REFINE the protocol under new SIGN cycle, don't force
retrofit onto current mechanisms.

**Guardrail 3 — refactor DEFERRED if protocol forces uniform shapes**

If Step 2 refactor evidence surfaces that Pattern B/C/D can only
implement the protocol via awkward stubs or method-signature contortion,
that's a signal the primitive is premature. **Trigger**: DEFER Step 2
and re-open the design with the new evidence. Do NOT ship a
worship-shaped refactor because the design doc predicts it should be
possible. Chris D-Q7 "evaluate as separate arc" is the load-bearing
protection here.

Together, these guardrails preserve the useful shape of the registry
(single audit surface, formalized extension point) without collapsing
Pattern B/C/D's legitimate mechanism-owned distinctness.

---

## §6 — Migration sequence

Three sequential PRs, each individually reversible. Each PR passes 95/95
pytest + Layer 2 golden-file diff before merge.

### Step 1 — Introduce protocol + registry + parity fixture (PR-A) [DORMANT]

**HARD BOUNDARY (Rigby SIGN Q4 refinement)**: Step 1 MUST NOT change
runtime dispatch. Step 1 MUST NOT touch `search_embeddings()` control
flow. Only additive changes: dormant types + fixture + tests. Any Step
1 PR that modifies the composition loop, injection call sites,
oversample trigger, or drift-WARN emit paths is out-of-scope for Step
1 and MUST be reviewed as Step 2 (new SIGN arc required).

Concretely, Step 1 ships:

- Add `IntentMechanism` protocol + `CountMechanism`, `SelfReferenceMechanism`,
  `LiteralFilenameMechanism` classes to `core/rag_integration.py`
  (below current standalone functions).
- Add `INTENT_MECHANISMS = (CountMechanism(), SelfReferenceMechanism(),
  LiteralFilenameMechanism())` registry tuple.
- Add `tests/regression/rag_registry_parity/` fixture per §5.2
  coverage criteria — 15-case manifest + expected-output snapshot
  captured from HEAD.
- Add smoke test asserting `INTENT_MECHANISMS` well-formed (protocol
  conformance, name uniqueness, drift_warn_prefix uniqueness).
- **`search_embeddings` completely unchanged.** Classes exist but no
  code path calls them.

Verification:
- Golden-file diff: PASS by construction (unchanged code path).
- 95/95 existing pytest: PASS by construction.
- New smoke tests: 4 registry-shape tests PASS.

**Trigger for Step 2**: Step 1 lands + Chris D-verdict on Step 2 as a
**separate SIGN arc**. Step 2 is not automatic follow-up of Step 1.

### Step 2 — Refactor `search_embeddings` to iterate registry (PR-B) [REQUIRES SEPARATE SIGN ARC]

**Explicit gate (Rigby SIGN Q4 refinement)**: Step 2 is a
behavior-preserving refactor that requires its own Rigby SIGN cycle +
Chris D-verdict before authoring. Do NOT bundle with Step 1 PR. Do NOT
treat Step 1 D-verdict as tacit approval of Step 2.

Concretely, when Step 2 opens:

- Replace scattered inline blocks with the orchestration shape from
  §4.3.
- Delete standalone `_detect_*`, `_fetch_*_anchor_chunks` functions
  (their logic now lives inside the mechanism classes).
- Preserve exact registry order = precedence order.
- **`INTENT_MECHANISMS` unchanged from Step 1**.
- Golden-file diff: PASS (this is the zero-behavior-change proof).
- 95/95 pytest: PASS.
- Additional pytest: 10 registry-specific tests (registration shape,
  precedence, injection order, MISS-path routing, drift-WARN routing).

**Trigger for Step 3**: Step 2 lands + one week of production
observation with no anomalies (per Chris typical wait-a-cycle
discipline).

### Step 3 — Optional module extraction (PR-C, deferred)

- Move mechanism classes to `core/rag/intent_mechanisms/*.py`.
- No behavior change; pure file organization.
- **Trigger**: only if a 4th mechanism (Pattern E) is proposed AND
  Chris D-verdicts that the file-organization benefit outweighs the
  churn. Otherwise this step never happens.

### Rollback

Each PR is a standalone revert. Rolling back PR-B restores the
scattered inline blocks. Rolling back PR-A removes dormant classes.
No irreversible schema/DB changes.

---

## §7 — Test coverage

### §7.1 — Existing 95 tests transfer unchanged

- `tests/unit/test_s2827_pattern_c_self_reference_gate.py` (34 tests) —
  assertions on `_detect_self_reference_intent`, anchor map, bonus
  value, diagnostic fields. All continue to pass because mechanism
  class exposes the same functions/attributes via delegation OR the
  tests are updated to reference `SelfReferenceMechanism()` (Step 2
  migration decision — recommendation: keep standalone functions as
  thin delegates for test stability).
- `tests/unit/test_s2828_pattern_d_literal_filename_gate.py` (61 tests) —
  same pattern.

### §7.2 — New registry-level tests (Step 2)

10 new tests, target file `tests/unit/test_intent_mechanism_registry.py`:

1. `test_registry_ordering_is_precedence` — assert tuple order matches
   `intent_gate_name` precedence
2. `test_all_registered_mechanisms_implement_protocol` — protocol
   conformance for each instance
3. `test_all_mechanism_names_unique` — no duplicate `name` attributes
4. `test_all_drift_warn_prefixes_unique` — no duplicate log prefixes
5. `test_only_injecting_mechanisms_provide_fetch` — B does not inject;
   C+D do (protocol invariant enforcement)
6. `test_default_diagnostic_fields_present_when_inactive` — every
   mechanism's diagnostic keys present with default values
7. `test_injection_order_matches_registry_order` — Pattern C injects
   before Pattern D on any query firing both
8. `test_bonus_composition_additive` — total = sum(per-mech bonus)
9. `test_miss_log_only_from_declared_mechanisms` — only D emits MISS
   log today
10. `test_drift_warn_uses_correct_prefix_per_mechanism` — WARN routing

### §7.3 — Golden-file regression harness

`tests/regression/rag_registry_parity/manifest.json` — one query per
each of the **15 coverage-criteria case classes** enumerated in §5.2
(cardinality is a side effect of coverage, not a target; the count MAY
grow if a new observable branch is added, but MUST NOT be trimmed
below the 15-case minimum). Paired with a JSON snapshot of expected
`search_embeddings` output per query captured from HEAD at Step 1.

`tests/regression/rag_registry_parity/test_parity.py` — one test
iterating queries, deep-equal against snapshot. Committed at Step 1;
must PASS at Step 2 = zero-behavior-change proof.

---

## §8 — Risks + mitigation

| Risk | Blast radius | Mitigation |
|---|---|---|
| Precedence order changes accidentally | Wrong `intent_gate_name` returned; downstream may branch on this | Registry tuple order pytest + golden-file diff |
| Diagnostic field default value drift | Consumer keying on field gets different value | `default_diagnostic_fields()` pytest per mechanism |
| Injection order changes | Different chunk wins dedupe on overlap | Injection-order pytest + golden fixture |
| MISS log leaks into B/C | Log noise / misleading grep | Only D declares MISS-emit; protocol default is no-op |
| Drift-WARN routing swap | Wrong mechanism attributed | Per-mechanism prefix pytest |
| Composition non-additive | Total ≠ sum | `test_bonus_composition_additive` |
| Test coupling to standalone fns | 95 tests break at Step 2 | Keep standalone `_detect_*` as thin delegates OR update tests in same PR (evaluate at Step 2 time) |
| Protocol runtime cost | Method-dispatch overhead in hot path | Negligible: 3 method calls × N chunks; already dominated by CosineDistance SQL |
| Future author collapses distinct anchor maps | Chris D5 broken | Design doc §3 (this section) as canonical anti-collapse contract |

---

## §9 — Rigby joint SIGN routing plan

**Anti-rubber-stamp directive** (per S2777 memory rule): verify
`tool_runs` non-empty on SIGN task result before treating verdicts as
substantive. Explicit tool-grounded prompts.

### §9.1 — Cycle 1 (5 questions)

**Q1 — Skeleton characterization accuracy**: Read `core/rag_integration.py`
`:101-105`, `:169-189`, `:397-429`, `:713-744`, `:800-848`, `:889-925`,
and this design doc §2. Does the 6-stage skeleton characterization
match the actual code, and does the §3 divergence list capture every
mechanism-specific behavior that MUST NOT collapse?

**Q2 — Protocol shape stress test**: Read §4.1 `IntentMechanism`
protocol. Would each of Pattern B/C/D implement this contract without
shape distortion? Are there current behaviors (e.g. Pattern D's
canonicalization, Pattern D's MISS INFO log, Pattern C's `base_qs`
argument that Pattern D dropped) that the protocol either forces or
awkwardly accommodates?

**Q3 — Zero-behavior-change verification method**: Read §5.2 golden-file
diff proposal. Is a 30-query manifest sufficient? What queries are
missing? Should the fixture include queries that fire two mechanisms
(theoretical only — no such query exists today), or is that scope
creep?

**Q4 — Migration sequencing**: Read §6 Step 1 → Step 2 → Step 3. Chris
D-Q7 S2828 said "evaluate as separate arc." Does the sequencing
respect this — i.e. can Step 1 land as a design-only-ratification PR,
Step 2 land as a behavior-preserving refactor PR, and Step 3 remain
optional? Or does the boundary blur?

**Q5 — Zoom-out (per S2771 memory rule)**: Step back from the immediate
mechanics. What coupling or risk is this design accreting that we
don't see yet? Concretely: is there a hypothetical Pattern E shape
that the current 3-mechanism registry would fail to accommodate? Is
the registry itself an over-abstraction — would Chris D-verdict this
as premature primitive-worship?

### §9.2 — Reconciliation cycle 2

Refinements applied to §2/§3/§4/§5/§6 based on cycle 1 verdicts;
Rigby re-reads v2; re-verdicts each of Q1-Q5.

### §9.3 — Joint agreement gate

Per S2753 discipline: Claude + Rigby AGREE on all refinements before
routing to Chris. If any Q remains DISAGREE after cycle 2, escalate
as explicit tie-break; do NOT present Chris with an unresolved menu.

---

## §10 — Chris D-verdict routing (expected shape)

Chris D-Q7 S2828 wording: "evaluate as its own architectural arc" +
"evaluate ≠ build automatically." This design's expected D-verdicts:

- **D-Q1** — Shape survey (§2) + divergence contract (§3) accurate?
- **D-Q2** — Protocol shape (§4.1) preserves Chris D5 distinctness?
- **D-Q3** — Zero-behavior-change guarantee (§5) load-bearing enough?
- **D-Q4** — Migration sequencing (§6) matches "separate arc" intent?
- **D-Q5** — Golden-file harness (§5.2 Layer 2 + §7.3) sufficient
  regression protection?
- **D-Q6** — Ship Step 1 in S2830 (parity fixture + dormant classes),
  Step 2 in a later session, Step 3 optional? Or defer everything?
- **D-Q7** — Any refinements the D-verdicts require?

**Explicit non-ask**: this design does NOT ask Chris to approve
implementation. It asks him to approve or reject the design shape.
Implementation is a separate D-verdict downstream of design ratification.

---

## §11 — Appendix — Provenance

- **Triggers**: S2826 (Pattern B) + S2827 (Pattern C) + S2828
  (Pattern D) shipped as 3 parallel instances → Chris D-Q3 S2828
  forward-carry ("codification threshold met") → Chris D-Q7 S2828
  ("evaluate as separate arc") → S2830 open recommended default per
  `00-START-NEXT-SESSION.md`.
- **Constitutional constraints preserved**: Chris D3 (retrieval
  integrity, bounded not force-rank-1), D5 (distinct mechanisms),
  D6 (no `include_superseded` relaxation), Playbook §7.4.4 (recycle
  after merge), PLAYBOOK-6.10.8 (fold-authoring evidence admission).
- **Substrate context**: S2829 canonical-anchor drift triage
  established that the metadata layer is now clean and substrate-hardened
  (--apply guard + sync skip-branch closure). Registry design lands on
  a stable, verified baseline.
- **What NOT to bundle**: PR3 S2829 (canonical-anchor invariant design +
  divergent-retrieval-stack diagnostic) is a distinct architectural
  arc. Do NOT combine with this registry design.
