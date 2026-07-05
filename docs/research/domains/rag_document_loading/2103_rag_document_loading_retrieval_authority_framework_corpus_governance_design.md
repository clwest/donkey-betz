---
title: "Group 2100 P3 — Retrieval Authority Framework + Corpus Governance Design (S2103)"
status: active
session: 2103
arc: Research Group 2100 (RAG / Document Loading — Knowledge Loop)
child_slot: P3 Cat C Retrieval Authority FRAMEWORK + Corpus Governance Design
generated: 2026-07-04
last_reviewed: 2026-07-04
head_commit: 51923cc9
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/KNOWLEDGE_PIPELINE.md
  - docs/DOC_LIFECYCLE.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
related:
  - docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md
  - docs/research/domains/rag_document_loading/2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md
  - docs/research/domains/rag_document_loading/2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md
  - docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md
  - docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md
  - docs/research/domains/authority_enforcement/1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md
authority: design-preparation for Category C per parent §5.3 D2100.5 authority + Chris "agree all" ratification 2026-07-04 at S2100 close + P1 §19.2 R3.1-R3.5 handoffs + P2 §19.1 P3.1-P3.3 must-ship triage; produces retrieval authority FRAMEWORK (8 axes + conflict-resolution + worked examples) + corpus governance policy across 5 distinguished dimensions + owner assignments for §18 UNASSIGNED axes + artifact lifecycle model + F3 dual-cascade resolution recommendation + F2 D2100.11 retrofill recommendation + F6/F1 backlog dispositions
---

## 1. Executive Summary

**S2103 P3 delivers design-preparation for Category C — Retrieval Authority
FRAMEWORK + Corpus Governance Design.** THIRD child audit under Group 2100
RAG / Document Loading (Knowledge Loop) arc, ELEVENTH-consecutive
application of playbook §11.2 20-section child-audit template after S1301
/ S1401 / S1501 / S1601 / S1701 / S1801 / S1901 / S2001 / S2101 / S2102.
Executes on preserved arc pin `pa-18b095bb7c4740be` per playbook §16 arc-
standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails.

**Scope-vs-form distinction.** This is a **design-preparation** doc, not a
**runtime audit**. §14 findings are DESIGN DECISIONS — framework axes,
conflict-resolution rules, ownership assignments, lifecycle model rules,
cascade resolution recommendations. §15 debt table inherits S2101 T1-T10
+ S2102 T11-T17 by reference and adds P3-scoped design debt only.
Design-preparation authority per D2100.5 — no implementation ships this
arc; execution items enumerate as post-arc T-slots for Chris-gated
scheduling.

**Load-bearing deliverables (per parent §5.3 + P1 §19.2 + P2 §19.1):**

1. **Retrieval authority FRAMEWORK** — 8 axes + conflict-resolution rule
   with runtime-facts vs research-posture split + tie-break rule (per
   Q7 SIGN STRENGTHEN 2026-07-04) + worked-example table for 6 real
   retrieval scenarios. NOT a single universal ranking.
2. **D2100.9 hybrid metadata contract — final ratified shape.** Take
   S2101 §20.2 candidate lists (7-field core-required + 3 doc-type
   profiles + 4 derivable-at-ingest + 5 aspirational) and PROMOTE to
   contract with P2-derived additions (`chunker_id`, `chunker_version`,
   `overlap_size_actual`, upstream `Document.source` provenance).
3. **Owner assignments** for §18 UNASSIGNED axes (Path A cascade,
   Chunker A/B/C regimes, `_derive_source_type`, `Document.source`
   write-sites, `DocumentEmbedding` schema, `docs/_provenance.json`
   writes, retrieval semantics).
4. **Governance-term disambiguation** across 5 meanings
   (ownership / discipline / enforcement / documentation / policy) —
   each Q5-Q8 governance question answered per-axis.
5. **Artifact lifecycle model** (draft / active / canonical / superseded
   / deprecated) with transition triggers + who authorizes each.
6. **F3 dual-cascade resolution recommendation** (R3.5 discharge) —
   Chris-ratified lean (b) fold Path A into Path B OR (a) wire Path B
   beat + deprecate Path A per Q10 SIGN STRENGTHEN 2026-07-04 at S2102
   close.
7. **F2 D2100.11 candidate ratification path** — retrofill decision
   (a) forward-fix only vs (b) forward-fix + retrofill 24,980 sync_docs
   historical rows. Surface as Chris D-verdict at close card.
8. **F1 chunker consolidation design** (R3.7 discharge — backlog) —
   retire Chunker B in favor of Chunker C; STEP 3 `--embed` inline path
   should call `TextSplitter` directly.
9. **F6 backfill activation criteria** (R3.6 discharge — backlog) —
   document activation criteria explicitly OR retire enum value.
10. **R3.8 provenance-index scheduling decision** (backlog) — schedule
    `build_docs_provenance` vs CI-lint enforcement.
11. **Cascade governance canonical doc SPEC** (R3.4 — backlog design;
    execution post-arc) — replace informal MEMORY.md rules with
    canonical doc under `docs/00-START-HERE/`.

**Handoff-mapping footnote (Q1 SIGN STRENGTHEN 2026-07-04):**
Deliverables 1/2 discharge S2101 R3.1-R3.2 (metadata contract + 8-axis
framework); deliverable 3 discharges S2101 R3.3 + S2102 R3.3 (owner
assignments); deliverables 4/5 discharge parent §5.3 W5/Q6/Q7/Q8-b
governance question set; deliverables 6/7/8 discharge S2102 P3.1-P3.3
must-ship triage (F3 dual-cascade + F2 retrofill + F1 chunker
consolidation); deliverables 9/10/11 land as P3.x backlog per S2102
§19.1 (F6 backfill + R3.8 provenance scheduling + R3.4 canonical
governance doc). No new scope introduced beyond S2101 + S2102
handoff surfaces.

**Verifier-loop discharges from P2 unknowns:**

- **U1 (Document.source='api' upstream trace) — RESOLVED.**
  `sync_docs_index_to_documents.py:328-340` writes
  `source=ContentSource.IMPORTED` on every Document create. The `imported`
  value flows through `_derive_source_type` branch 4 (`document.source in
  ('api', 'imported')` → `'api'`) at `content/embeddings.py:53`. Root cause
  of 100% `source_type='api'` monoculture is a single write-site setting
  the field uniformly to `IMPORTED` for every docs-cascade Document. F5-
  partial can now discharge to F5-FULL with the injection-point named.
- **R2.9 (potential 4th chunker in `content/rag_integration.py`) —
  RESOLVED.** No such file exists at `content/`; the actual file
  `core/rag_integration.py` uses `DocumentEmbedding.chunk_text` as a
  FIELD accessor for encrypted-content decryption, not a chunker function.
  §7.3 three-chunker regime map from P2 is complete.

**§14 finding ordering (design-decision maturity).** F1-F8 rank primarily
by *blocking-status for post-arc execution* + secondarily by
*framework-vs-governance axis span*. F1 (framework 8-axis definition) +
F2 (conflict-resolution rule) are co-top because they enable every
subsequent P3 handoff. F3 (dual-cascade resolution) is HIGH governance-
executable — Chris-ratifiable at close card. F4 (governance-term
disambiguation) is HIGH prerequisite — prevents P3 conclusions from
being read as one-thing-fits-all governance decree. F5 (metadata
contract ratification) is HIGH executable. F6 (owner assignments) is
HIGH executable. F7 (artifact lifecycle model) is MEDIUM design-only.
F8 (D2100.11 F2 retrofill) is CHRIS-D-VERDICT candidate at close card.

**Rigby SIGN cycle 1 routing plan.** 4 batches of 5 findings each per
`feedback_rigby_sign_worker_instability_recovery` batching discipline.
Governance-design shape historically yields MORE folds than descriptive-
audit shape (S2003 P3 governance-design yielded 12 folds in 4 batches);
plan for STRENGTHEN-heavy cycle 1 with fold-landing pre-commit.

**Success criteria for S2103 P3 close.**

1. Rigby SIGN cycle 1 CLEAN with ≥ 90% verdicts (STRENGTHEN or CLEAN) —
   playbook §15 minimum bar.
2. All STRENGTHEN folds land pre-commit on preserved arc pin.
3. Chris ratifies D2100.11 F2 retrofill choice (a) or (b) at close card.
4. F3 dual-cascade recommended lean (b) or (a) ratified for post-arc
   execution.
5. All P3.1-P3.3 must-ship handoffs complete; P3.x backlog items either
   design-preparation-shipped OR explicitly deferred to post-arc T-slot.
6. Draft → active status transition on Chris ratification.
7. Commit + PR + full 4-step docs cascade + `build_docs_provenance`
   post-merge.

**Runtime target.** 6-session Group 2100 arc on track — 4 of 6 shipped
after S2103 close (S2100 parent scoping + S2101 P1 + S2102 P2 + S2103
P3). S2104 P4 Behavior Substrate Structured Observation next, then
S2199 xx99 canonical summary.

---

## 2. Domain Purpose

**Purpose statement.** Group 2100 P3 answers the Design authority
question: *"What retrieval-authority axes + conflict-resolution rules
does Rigby use to construct query-appropriate authority orderings, and
who owns each corpus-governance axis?"*

This is DISTINCT from:
- **P1 (S2101)** — Reality→Knowledge Gap Audit (what does the corpus
  contain, and where are its metadata gaps?)
- **P2 (S2102)** — Ingestion / Chunking / Embedding Pipeline Audit
  (how does material get into the corpus, and what are its cascade paths?)
- **P4 (S2104)** — Behavior Substrate Structured Observation (how does
  RAG-quality affect SIGN-quality in observed SIGN cycles?)

**Framing per parent §5.3 W3 correction.** The previous parent-scoping
draft proposed `canonical summary > child audit > parent scoping >
platform inventory > old handoff > raw notes` as a hard-coded ranking.
The W3 correction reframed this as: **ranking IS wrong; framework is
right.** Because ranking is defensible on some axes and wrong on
others:
- (i) Canonical summaries are *synthesized* evidence; child audits are
  *primary* evidence — for exact implementation questions, child audits
  should rank *above* canonicals.
- (ii) `PLATFORM_INVENTORY` is *runtime authority* per
  `DOC_LIFECYCLE.md §2c` inventory-wins-on-conflict — ranking it below
  research artifacts contradicts existing policy.
- (iii) "Old handoff" is not a class — S1268-S1275 foundational handoffs
  outrank any parent scoping on methodology.
- (iv) Recency, specificity, and lifecycle status all matter and no
  single ranking captures them.

P3 therefore designs a FRAMEWORK; individual retrieval queries construct
appropriate orderings from axes + conflict-resolution rules.

**Governance-term disambiguation (per parent §5.3 W5 critique).** The
term "governance" is used across 5 distinct meanings and must be
answered per-axis, not as one blob:
- (i) **ownership** — an `AIEmployee` handle in `core/employees/jobs.py`
- (ii) **discipline** — a repeated ritual (e.g., cascade-at-close)
- (iii) **enforcement** — CI checks, service-side validation, pre-merge
  hooks
- (iv) **documentation** — a canonical doc rather than a memory rule
- (v) **policy** — a stated contract with defined thresholds and
  escalation paths

Each of Q5, Q6, Q7, Q8 (from parent §5.3 W7 redistribution) must be
answered per-axis.

**Central lens question (D2100.6, RATIFIED).** The arc answers: *"Is
Rigby's RAG corpus a passive document search index, or is it a governed
institutional knowledge layer that can reliably shape future research,
SIGN cycles, and platform decisions?"* P3 contributes the DESIGNED
governance substrate; P4 delivers observational evidence; xx99 aggregates
the answer.

---

## 3. Canonical Entry Points

**Design-preparation entry point** is the parent §5.3 spec + D2100.5-10
ratified verdicts + S2101 §19.2 R3.1-R3.5 + S2102 §19.1 P3.1-P3.3 must-
ship triage. This doc has no runtime entry points — it produces design
artifacts consumed by post-arc execution T-slots.

### 3.1 Design-input entry points (upstream)

| Entry point | Location | Purpose |
|-------------|----------|---------|
| Parent §5.3 P3 spec | `2100_rag_document_loading_domain_scoping.md:586-737` | Load-bearing questions + deliverable spec |
| D2100.8 (8-axis framework adoption) | Parent §8 D2100.8 | Framework MUST land in P3 |
| D2100.9 (hybrid metadata contract) | Parent §8 D2100.9 | Contract shape LOCKED; P3 ratifies fields |
| D2100.5 (design-prep authority) | Parent §8 D2100.5 | No implementation ships this arc |
| D2100.10 (Corpus Health Score) | Parent §8 D2100.10 | Deferred to P4 close per Chris "agree all" |
| S2101 R3.1-R3.5 handoffs | S2101 §19.2 | P3 discharges 5 R-slots + inherits candidate lists |
| S2102 R3.1-R3.8 handoffs | S2102 §19.1 | P3 discharges 8 R-slots (3 must-ship + 5 backlog) |
| S2101 §20.2 candidate lists | S2101 §20.2 | 7-field core-required + 3 doc-type profiles |
| S2102 F1-F8 findings | S2102 §14 | Framework + governance decisions inputs |

### 3.2 Design-output artifacts (downstream consumers)

| Artifact | Consumer | Purpose |
|----------|----------|---------|
| Retrieval authority framework | Post-arc ranker execution + Rigby SIGN preambles + D2100.10 Corpus Health Score | Ranking logic constructs per-query orderings |
| D2100.9 ratified metadata contract | Post-arc schema-migration PR + service-side validation PR | Populates DocumentEmbedding.metadata JSONField at ingest |
| Owner assignments (§18) | Post-arc `core/employees/jobs.py` PR | New `AIEmployee` handles OR extend existing (Rigby, Chief of Staff, Platform Auditor) |
| Governance-term disambiguation table | S2104 P4 observation targets + xx99 §5 canonical seam statement | Prevents "governance" over-load in future arcs |
| Artifact lifecycle model | Post-arc DocumentEmbedding schema addition (lifecycle_status field state machine) | Enforces status transitions |
| F3 dual-cascade resolution | Post-arc PR (wire Path B beat OR fold A into B) | Retires architectural debt T13 HIGH |
| D2100.11 F2 retrofill choice | Post-arc `sync_docs_index_to_documents.py:394` PR + optional retrofill mgmt command | Fixes overlap-metadata data lie |
| Cascade governance canonical doc SPEC | Post-arc doc PR — `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` | Replaces informal MEMORY.md rules |

### 3.3 Employee-OS ownership entry point

`core/employees/jobs.py:DOCUMENTATION_MANAGER` (Rigby, employee_handle="rigby",
handle at line 187) owns the docs cascade Path B. P3 owner assignments
either (a) extend Rigby's job contract with new authority responsibilities
for the currently-UNASSIGNED §18 axes, OR (b) add new AIEmployee handles
(candidate: `retrieval_authority_owner`, `chunker_regime_owner`,
`document_source_provenance_owner`) — a design decision surfaced at F6
below.

**Baseline anchor.** Rigby's current authority (§237-250) covers
`run_docs_cascade_commands`, `run_drift_observation`,
`create_escalation_deliverable`, `certify_mission_run`. She's PROHIBITED
from `modify_docs_files`, `open_pull_request`, `delete_document_rows`,
`delete_document_embedding_rows`. This bounds what §18 assignments can
extend within Rigby vs what needs a new AIEmployee handle.

---

## 4. Major Models

Design-preparation arc — no new models proposed for schema migration this
session. §4 documents the model surface P3's contract touches.

### 4.1 `content.Document` — institutional record (P3 governance target)

Fields P3 governance decisions affect:
- `source` — TextChoices (`api`, `imported`, `scraped`, `upload`,
  `internal`, `system`, ...). F5-FULL discharge: cascade write-site
  writes `IMPORTED`; monoculture is not schema-forced, it's write-site
  discipline. P3 governance decides value diversification.
- `status` — TextChoices (`draft`, `ready`, `completed`, ...). Related
  to but distinct from *artifact lifecycle status* (see §14 F7). P3
  clarifies mapping.
- `document_type` + `category` — orthogonal per S2101 §20.3 Q14 fold.
  `document_type` = artifact class; `category` = domain taxonomy. P3
  contract keeps both.
- `extracted_metadata` (JSONField) — where cascade write-site currently
  populates `docs_index_type`, `docs_index_status`, `subsystems`,
  `folder`, `scope='docs_index'` (per
  `sync_docs_index_to_documents.py:317-326`).

### 4.2 `content.DocumentEmbedding` — per-chunk retrieval unit (P3 contract target)

Fields P3 contract must cover per D2100.9:
- `metadata` (JSONField) — currently unstructured; P3 ratifies core-
  required + doc-type profile shape.
- `chunk_text` (TextField, may be encrypted) — carries chunk content.
- `embedding_model` — 100% populated LOCAL; P3 keeps as core-available.
- `source_type` — derived via `_derive_source_type`; P3 governance
  decides diversification.
- `ingested_via` — `unknown` / `sync_docs` / `backfill` enum. F6
  backfill-dormancy discharge decides enum-retirement vs activation.
- NEW FIELDS PROPOSED (P3 CONTRACT ADDITIONS, executed post-arc):
  - `overlap_size_actual` — real chunk overlap in characters (F2 fix
    by contract). Currently persisted as `overlap_size=0` for
    sync_docs population despite 200-char actual overlap.
  - `chunker_id` — enum { `chunker_a_local_jsonl`,
    `chunker_b_sync_cascade_de`, `chunker_c_text_splitter_async` }.
    Discharges F1 chunker-provenance carry.
  - `chunker_version` — semver or hash; prevents stale-chunk retrieval
    after chunking-strategy migration.
  - `provenance_axis` — value domain (per S2101 §20.2 Q13 fold):
    `research_artifact`, `runtime_inventory`, `narrative_anchor`,
    `handoff`, `topic_doc`, `spider_data`. Discriminator that ranking
    layer cannot safely re-infer.

### 4.3 `core/employees/jobs.py` frozen registry (P3 owner-assignment target)

Current 3 employees + 3 job contracts (per `EMPLOYEE_OS_PRIMITIVES.md`):
- `DOCUMENTATION_MANAGER` — Rigby, owns Path B docs cascade.
- `PLATFORM_AUDITOR` — audit orchestration.
- `CHIEF_OF_STAFF` — cross-plane coordination.

P3 owner-assignment options per axis land as extensions to one of these
or as new frozen-dataclass entries. §18 details per-axis assignment
recommendations.

---

## 5. Major Services

Design-preparation arc — no new services proposed for implementation
this session. §5 documents services P3 governance touches.

### 5.1 `content/embeddings.TextSplitter` (Chunker C target)

Owner assignment target: Chunker C regime owner. F1 R3.7 chunker
consolidation designates this as the surviving canonical chunker. STEP
3 `--embed` inline path currently uses Chunker B
(`sync_docs_index_to_documents.chunk_content`); consolidation migrates
to Chunker C.

### 5.2 `content/embeddings._derive_source_type` (source_type discipline target)

Owner assignment target: `_derive_source_type` derivation owner
(currently UNASSIGNED per S2102 §18.1). F5-FULL upstream write-site
now traced to `sync_docs_index_to_documents.py:340`. Governance
decision axis: does ownership go to derivation function or to
write-site? P3 recommendation at §18: **write-site ownership** —
because the derivation function is correct given input; the
uniformity is a write-side discipline gap.

### 5.3 `sync_docs_index_to_documents.py` (F2 + F5-FULL write-site target)

Owner assignment target: `Document.source` write-sites owner. F2
overlap-metadata fix + F5-FULL diversification both land here. R2.7
(1-line `overlap_size=200` fix at line 394) + F5-FULL diversification
(pass appropriate `ContentSource` value at line 340 based on
`doc_data.get('scope')` or similar signal) are the concrete post-arc
execution items.

### 5.4 `refresh_docs_corpus` beat task + `docs_cascade.py` MissionRunner (F3 target)

Path A beat-scheduled + Path B MissionRunner unscheduled. F3 R3.5
resolution + owner assignment go together — Chris ratified recommended
lean (b) fold A into B OR (a) wire B + deprecate A. Ownership either
way remains with `DOCUMENTATION_MANAGER` (Rigby) since her Path B
contract already models the cascade.

### 5.5 `build_docs_provenance` mgmt command (R3.8 target)

Currently manual per S1145 Plan B design intent + Chris directive
(`feedback_docs_cascade_at_every_close`). R3.8 scheduling decision at
§14 F7 governance-decisions cluster.

---

## 6. Major APIs and Interfaces

Design-preparation arc — no new APIs proposed this session.

### 6.1 Retrieval-side interfaces P3 framework contract touches

- `core/rag_integration.py:query_pgvector` — semantic-vector retrieval
  entry point. Consumes `DocumentEmbedding.metadata` + `chunk_text`.
  Framework CONFLICT-RESOLUTION rule executes here at post-arc
  execution.
- Rigby SIGN retrieval — consumes retrieval ranker output. Framework
  drives per-query authority ordering.
- `verify_doc_claims` — consumes retrieval ranker output; contract
  affects drift detection accuracy.

### 6.2 Governance-side interfaces P3 doc-spec produces

- `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` (NEW POST-ARC) —
  replaces informal MEMORY.md rules per R3.4.
- `docs/topics/docs-ingestion-cascade.md` (NEW POST-ARC) — publishes
  the 4-step cascade + three-chunker regime map + dual-orchestrator
  path picture per R3.1.

### 6.3 Post-arc execution surface

- `PeriodicTask` beat entries — F3 R3.5 executable adds beat entry for
  either merged path or wires Path B directly.
- `sync_docs_index_to_documents.py:340` write-site — F5-FULL
  diversification.
- `sync_docs_index_to_documents.py:394` create call — F2 overlap_size
  fix.
- New AIEmployee handles (if elected) — extend `core/employees/jobs.py`.
- CI-lint (if elected for R3.8) — validate `docs/_provenance.json`
  mtime freshness.

---

## 7. Runtime Flows

Design-preparation arc — §7 documents the framework's design-time
"flow" of how a query resolves to an authority ordering. No runtime
implementation ships this arc.

### 7.1 Framework query-resolution flow (design)

```
   Query arrives at retrieval layer
              │
              ▼
   ┌──────────────────────────────────┐
   │ 1. Classify query intent         │
   │    { runtime_facts,              │
   │      research_posture,           │
   │      methodology,                │
   │      mixed }                     │
   └──────────────────────────────────┘

   Per Q2 SIGN STRENGTHEN 2026-07-04 — intent classes:
   - runtime_facts: "how many agents live in AGENT_MAP right now?"
     belongs here; "what is Rigby's job contract mission text?" does
     NOT (research-posture — contract intent).
   - research_posture: "why did Group 1900 defer Q5 auto-approve?"
     belongs here; "which beat entries fire at 4am Denver?" does NOT
     (runtime).
   - methodology: "how does the playbook §11.2 20-section template
     apply here?" belongs here; "when was the last playbook edit?"
     does NOT (runtime).
   - mixed: hybrid queries invoke ALL scoring passes and let the
     conflict-resolution rule decide priority per doc.

   Methodology-questions guardrail: methodology queries MAY consult
   runtime facts for tool availability / entrypoints ("does
   `session_tool retire` exist?") but MUST NOT let inventory outrank
   primary evidence on implementation details ("how does
   MissionRunner escalate on step-4 timeout?" → child audit wins,
   not inventory).
              │
              ▼
   ┌──────────────────────────────────┐
   │ 2. Compute per-doc axis scores   │
   │    (8 axes per D2100.8):         │
   │    - primary vs synthesized      │
   │    - runtime vs research         │
   │    - specificity to query        │
   │    - recency (last_embedded_at)  │
   │    - supersession status         │
   │    - canonical summary status    │
   │    - lifecycle status            │
   │    - + conflict-resolution rule  │
   └──────────────────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ 3. Apply conflict-resolution     │
   │    (per §14 F2):                 │
   │    - PLATFORM_INVENTORY wins on  │
   │      runtime facts               │
   │    - child audits win on primary │
   │      impl evidence               │
   │    - canonical summaries win on  │
   │      synthesized posture unless  │
   │      contradicted by newer src   │
   │    - foundational handoffs win   │
   │      on methodology              │
   │    - supersession OVERRIDES      │
   │      recency                     │
   │    - tie-break: newer measurement│
   │      timestamp else source-of-   │
   │      truth hierarchy             │
   └──────────────────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │ 4. Emit ranked results w/       │
   │    authority-provenance labels   │
   └──────────────────────────────────┘
```

### 7.2 Governance-lifecycle flow (artifact state machine)

Per §14 F7 lifecycle model:

```
   [draft] ──ratification──▶ [active]
              │                  │
              │                  ├──consumed_at_xx99──▶ [canonical]
              │                  │                         │
              │                  │                         ▼
              │                  │                     [superseded]
              │                  │                         │
              │                  └───────supersession───┘  │
              │                                            ▼
              └──────────────abandon────────────▶ [deprecated]
```

Transitions + who authorizes (§14 F7 detail):
- `draft` → `active`: **Chris ratification** post-Rigby SIGN cycle
  clean.
- `active` → `canonical`: **xx99 aggregation** by parent-scoping author.
- `active` → `superseded`: **supersession chain declaration** in newer
  doc frontmatter + verifier-loop confirmation.
- `canonical` → `superseded`: same (canonicals are supersedable when
  next-generation canonical lands).
- `draft` → `deprecated`: abandon-authorization by Chris or session-
  arc-close negative decision.

### 7.3 Post-arc execution flow (F3 R3.5 recommended lean (b) fold)

Design recommendation — NOT executed this arc:

```
   Existing Path A refresh_docs_corpus beat (4 AM Denver daily)
              │
              ▼
   ┌──────────────────────────────────┐
   │ Post-arc PR:                     │
   │ 1. Add hash-delta gate to        │
   │    docs_cascade preflight        │
   │ 2. Wire rigby_documentation_     │
   │    manager_daily beat entry      │
   │ 3. Retire refresh_docs_corpus    │
   │    beat entry                    │
   │ 4. Path A code stays for one     │
   │    release cycle as fallback     │
   │ 5. Rigby's job contract already  │
   │    models Path B — no owner add  │
   └──────────────────────────────────┘
```

Alternative recommendation — Chris may prefer (a) wire Path B + deprecate
Path A. Both preserve Path B's richer safety scaffolding + Rigby's
Employee OS ownership. §14 F3 documents ratification path.

---

## 8. Data Ownership and Lifecycle

### 8.1 Retrieval-authority axis ownership (P3 assignment)

| Axis | Owner (post-P3) | Rationale |
|------|-----------------|-----------|
| primary vs synthesized evidence | Rigby (Documentation Manager) | Consumed by retrieval + SIGN preambles |
| runtime vs research authority | `DOC_LIFECYCLE.md §2c` (existing policy) | Policy already exists; P3 respects it |
| specificity to query | Retrieval ranker (post-arc) | Runtime resolution; no separate owner needed |
| recency (`last_embedded_at`) | Cascade owner (Rigby via Path B) | Cascade populates the field |
| supersession status | Doc author (`supersedes` / `superseded_by` frontmatter) + Rigby (state-machine enforcement) | Author declares; owner enforces |
| canonical summary status | xx99 author (parent-scoping author) | Established by canonical-doc creation |
| lifecycle status | Rigby (state-machine enforcement) | Path B mission enforces per §14 F7 |
| conflict-resolution rule | Chris + Group 2100 arc close (P3 D-verdict) | Meta-policy — belongs to arc closure |

### 8.2 Corpus-governance axis ownership (§18 UNASSIGNED discharges)

Detailed at §18. Summary:
- Path A cascade: retire per F3 R3.5 fold (b) OR Rigby via wire-B option (a).
- Chunker A: unchanged owner = LOCAL keyword-lane consumer (no active Employee OS binding needed since local-only).
- Chunker B: retire per F1 R3.7; ownership vaporizes at retirement.
- Chunker C: Rigby (Documentation Manager) — she runs Path B step 4 embed.
- `_derive_source_type`: no separate owner — write-site discipline is the fix.
- `Document.source` write-sites: Rigby (via Path B cascade write-site policy).
- `DocumentEmbedding` schema: Chief of Staff (cross-plane data-contract owner) OR Rigby with schema-migration authority delegation — P3 recommendation: **Chief of Staff** as neutral cross-plane owner (avoids conflating cascade execution ownership with schema-contract ownership).
- `docs/_provenance.json` writes: Rigby (via cascade tail R3.8 scheduling decision).

### 8.3 Metadata-contract lifecycle (D2100.9 ratification)

Per S2101 §20.2 candidate lists → P3 ratification:

**Core-required (fatal-if-missing for P1/P3 reasoning) — 6 fields
per Q6 SIGN STRENGTHEN 2026-07-04 downgrade of `last_embedded_at`
(S2101 §20.2 baseline had 7; P3 downgrade drops to 6):**
1. `document_id` (UUID)
2. `document_type`
3. `source_path` (file_path)
4. `lifecycle_status` (draft/active/canonical/superseded/deprecated)
5. `chunking_version`
6. `provenance_axis`

**P3 ADDITIONS to core-required (post-P2 chunker findings):**
7. `chunker_id` (F1 discharge — enum { chunker_a, chunker_b, chunker_c })
8. `overlap_size_actual` (F2 discharge — required-but-typed: NULL
   permitted for `chunker_a_local_jsonl`; validator enforces not-null
   for chunker B / chunker C)
9. `upstream_source_provenance` (F5-FULL discharge — the ContentSource
   value used at Document create-time)

**Total core-required contract shape at P3 close: 9 fields.**

**Core-available (schema-present + auto-populated, not core-required):**
- `embedding_model` — 100% populated LOCAL; enforced by write-site
- `last_embedded_at` — Q6 SIGN STRENGTHEN downgrade from core-required;
  derived `embedding_freshness` label degrades gracefully when absent

**Doc-type profiles (per class, recommended):**
- **Profile A** (Research artifact): `research_group`, `session`,
  `domain_slug`, `child_slot`, `canonical_summary`, `head_commit`
- **Profile B** (Handoff): `session`, `handoff_target`,
  `head_commit_before`, `head_commit_after`
- **Profile C** (Topic doc / narrative anchor): `subsystem`,
  `superseded_by`, `supersedes`, `canonical`

**Derivable-at-ingest (schema-computable):**
- `canonical_summary` flag (filename regex)
- `head_commit` at embed time (git rev-parse)
- `source_path` (already `Document.file_path`)
- `last_embedded_at` (already chunk `created_at`)

**Aspirational (defer to future arc):**
- `related_arcs` (contingent — becomes derivable-at-ingest IF P3 mandates
  frontmatter `related:` block; RATIFIED at §14 F5 discharge)
- `T-slot / R-slot references`
- `decisions_locked`
- `implementation_status`
- `parent_doc`

### 8.4 Chunk lifecycle (F7 dependency)

Per S2102 §8.2 — chunks are per-Document children with cascading delete.
P3 governance decision: lifecycle_status on chunk should be **derived
from parent Document.lifecycle_status** (not independently tracked)
because chunks don't have independent authoring — they're artifacts of
ingestion. Exception: `chunker_version` staleness may cause per-chunk
`superseded` status without parent supersession.

---

## 9. Integrations With Other Domains

### 9.1 Group 1300 (Memory) — Boundary

- Boundary respected: P3 governance ONLY touches document / retrieval
  substrate. Personal / conversation memory remains Group 1300 owned.
- Cross-plane read (S1904 §17 pattern): retrieval framework does NOT
  read `AgentMemory` or conversation memories. Retrieval is docs-only.
- Boundary re-attestation: S1304 G5 E↔D boundary that P3 discharges is
  the *docs* side of E↔D, not the memory side.

### 9.2 Group 1700 (Observability) — Delegation

- Filter counters + logger telemetry patterns remain Group 1700
  delegation per S1304 T6.
- P3 does NOT design new observability infrastructure; it may
  RECOMMEND observability targets for the retrieval framework
  (post-arc), which route to Group 1700 for design + implementation.
- F7 EventBus emission decision (S2102 F7) surfaces here — P3
  governance decision to emit cascade EventBus events feeds forward
  to Group 1700's future consumer surface.

### 9.3 Group 1800 (Human Attention) — Independence

- No direct cross-plane dependencies. Retrieval framework does not
  invoke human-in-the-loop escalation directly; escalation is Rigby's
  Path B mission responsibility.

### 9.4 Group 1900 (Authority Enforcement) — Delegation

- Retrieval framework respects `principal_user` access-control gate at
  entry point. Framework does NOT re-implement authority checks —
  those are Group 1900's responsibility.
- Owner-assignment authority (§18) uses Group 1900's `AuthorityLevel`
  enum values (EXECUTE / OBSERVE / RECOMMEND / PROHIBITED).

### 9.5 Group 2000+ (Event / Integration Architecture) — S2099 close consumption

- F7 EventBus emission decision surface consumes S2099 canonical seam
  statement patterns. P3 recommendation: **emit cascade lifecycle
  events** (`docs_cascade.started`, `docs_cascade.step_completed`,
  `docs_cascade.embed_finished`, `docs_cascade.escalation_raised`)
  at post-arc execution. Framework does NOT ship the emission —
  emissions are Group 2000+ retroactive fold-in per S2102 §19.4.

### 9.6 Group 2100 P4 (S2104 — next child)

- P4 consumes P3 framework as observation target. §17.1 posture-
  register format from S1904 inherits to P3 §17.1 (see §17 below).

---

## 10. Event Flows

Design-preparation arc — §10 documents the event surface P3 governance
touches.

### 10.1 Current cascade EventBus emissions

Zero. S2102 F7 confirmed — neither Path A nor Path B emits EventBus
events. Path B uses `OpsRunEvent` (ORM rows on `OpsRun`) as its timeline
substrate; Path A uses structured `[DOCS_CORPUS_REFRESH*]` logger lines.

### 10.2 P3 recommended event surface (post-arc emission — NOT shipped this arc)

Two-layer event architecture (per S2102 §10.4 Q6 SIGN fold candidate):

**Layer 1 — Lifecycle events (EventBus):**
- `docs_cascade.started` — payload: `path`, `head_commit`, `owner`
- `docs_cascade.step_completed` — payload: `path`, `step` (1..4),
  `rows_affected`, `duration_ms`
- `docs_cascade.embed_finished` — payload: `path`,
  `chunks_created`, `chunks_updated`, `chunks_deleted`, `duration_ms`
- `docs_cascade.escalation_raised` — payload: `path`,
  `failure_signature`, `deliverable_id`

**Layer 2 — Retrieval-quality events (framework-emit at query-time):**
- `retrieval.query_resolved` — payload: `query_intent_class`,
  `authority_ordering`, `top_k_provenance_axes`, `conflict_resolution_
  triggered` (bool)
- `retrieval.authority_conflict_detected` — payload: `axis_pair`,
  `resolution_rule_fired`, `chosen_doc_id`

Both layers feed downstream Corpus Health Score (D2100.10 deferred to
P4) + Rigby SIGN preambles + Group 1700 observability dashboards.

### 10.3 Governance-emission events (P3 policy)

Any lifecycle status transition (draft → active, active → canonical,
active → superseded, → deprecated) SHOULD emit a `docs_governance.
lifecycle_transitioned` event. Framework enforcement post-arc.

---

## 11. Existing Documentation

### 11.1 Docs P3 governance touches (existing)

| Doc | Purpose | P3 relationship |
|-----|---------|-----------------|
| `docs/DOC_LIFECYCLE.md` | §2c inventory-wins-on-conflict rule | Framework RESPECTS as inherited policy |
| `docs/PLATFORM_INVENTORY.md` | Runtime counts baseline | Framework treats as runtime-authoritative |
| `docs/PLATFORM_WHAT_IT_IS.md` | Narrative anchor | Framework treats as research-authoritative |
| `docs/KNOWLEDGE_PIPELINE.md` | Cascade flow map | Framework consumes as background |
| `docs/EMPLOYEE_OS_PRIMITIVES.md` | Employee OS canonical primitives | §18 owner-assignment discipline follows |
| `MEMORY.md` cascade rules | 4-step cascade + close-out cascade + embed-step-required | Framework REPLACES via R3.4 canonical doc |

### 11.2 Docs P3 designs to publish (post-arc)

| Doc | Location | Purpose |
|-----|----------|---------|
| `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` | (NEW) | Canonical governance doc — replaces informal MEMORY.md rules per R3.4 |
| `docs/topics/docs-ingestion-cascade.md` | (NEW) | 4-step cascade + three-chunker regime + dual-orchestrator paths per R3.1 |
| `docs/topics/retrieval-authority-framework.md` | (NEW) | 8-axis framework + conflict-resolution rule + worked examples per D2100.8 |

### 11.3 Docs P3 flags for update (existing anchors)

| Doc | Update needed |
|-----|---------------|
| `docs/PLATFORM_WHAT_IT_IS.md` | Add §-subsection under RAG/docs describing the framework + 5-meaning governance disambiguation |
| `docs/PLATFORM_INVENTORY.md` | Add DocumentEmbedding.metadata contract shape row + chunker regime row |
| `docs/DOC_LIFECYCLE.md` | Cross-reference retrieval-authority framework for research-posture axis |
| `CLAUDE.md` | Add pointer under Reference Documentation table |
| `docs/AGENTS.md` / `docs/SERVICES.md` | (NO CHANGES) — P3 does not affect agent or service surface |

---

## 12. Research Coverage

### 12.1 Group 2100 arc coverage (this doc's contribution)

- **P1 (S2101)** covered: what is the corpus (Reality) + where are its
  gaps (Knowledge Gap)?
- **P2 (S2102)** covered: how does material get into the corpus
  (Ingestion / Chunking / Embedding Pipeline)?
- **P3 (S2103)** covers: what retrieval-authority axes + governance
  rules apply (this doc)?
- **P4 (S2104)** will cover: how does RAG-quality affect SIGN-quality
  (Behavior Substrate Observation)?
- **xx99 (S2199)** will consolidate: canonical seam statement.

### 12.2 Cross-arc research consumed by P3

- **S1268-S1275** — Foundational handoffs (methodology-authoritative
  in framework's conflict-resolution rule).
- **S1304** — Memory-docs-RAG boundary audit (E↔D boundary, S1304 G5).
- **S1399** — Canonical summary (canonical-summary evidence class
  status in framework).
- **S1802/S1806** — Human Attention arc §17 posture-register format
  (P3 §17 pattern inheritance).
- **S1904/S1999** — Authority Enforcement arc §17 CONSOLIDATION-shape
  posture-register (P3 §17.1 template).
- **S2001-S2099** — Event / Integration Architecture (S2099 canonical
  seam statement pattern for §7 event flows).
- **S2101 §20.2** — Candidate metadata contract lists (P3 promotes to
  ratified contract).
- **S2102 §14-§20** — F1-F8 findings + T-table + UNASSIGNED matrix
  + P3 triage list + U1-U6 unknowns.

### 12.3 Post-P3 research consumed by P4 + xx99

- **P3 §14 findings F1-F8** — framework + governance design substrate
  for P4 observation targets.
- **P3 §17.1 posture register** — feeds xx99 §5 canonical seam
  statement.
- **P3 §18 owner assignments** — feed post-arc `core/employees/jobs.py`
  PR and xx99 §8 T-slot queue.
- **P3 §19 recommendations** — feed P4 R4.x handoffs + post-arc T-slots.

---

## 13. Architecture Maturity

**Maturity assessment** for design-preparation shape. Per S1902 §14.1
CANONICAL / STABLE / WORKING / PARTIAL / SPEC-ONLY / MISSING rubric.

### 13.1 Retrieval authority framework

- **Current state: SPEC-ONLY** — no ranker implementation exists. Post-
  arc execution items enumerated.
- **Path to WORKING**: R3.2 D2100.9 contract lands → schema migration
  ships → cascade write-sites populate contract fields → ranker
  consumes fields. Estimated: 4-6 post-arc PRs.
- **Path to STABLE**: N observation cycles (P4 R4.2 acceptance criteria
  observation) + Corpus Health Score gates (D2100.10 deferred).
  Estimated: 2-3 post-P4 sessions.

### 13.2 Corpus governance policy

- **Current state: SPEC-ONLY + PARTIAL** — SPEC (P3 designs
  disambiguation table + 5-dim policy). PARTIAL (MEMORY.md rules exist
  as informal governance today — 3 rules currently in force per
  `feedback_docs_pipeline_4_step_cascade` +
  `feedback_docs_cascade_at_every_close` +
  `feedback_cascade_pr_must_include_embed_step`).
- **Path to WORKING**: R3.4 canonical doc lands →
  `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` published →
  supersedes MEMORY.md rules. Estimated: 1 post-arc PR.
- **Path to STABLE**: Owner-assignment PR lands + Rigby's job contract
  extended to enforce lifecycle-status transitions. Estimated: 2 post-
  arc PRs.

### 13.3 Artifact lifecycle model

- **Current state: PARTIAL** — schema field `Document.status` exists
  (draft/ready/completed) but doesn't map cleanly to
  draft/active/canonical/superseded/deprecated. `DocumentEmbedding`
  has no lifecycle_status field today.
- **Path to WORKING**: Schema addition of `lifecycle_status` to
  `DocumentEmbedding.metadata` + state-machine enforcement service.
  Estimated: 2-3 post-arc PRs.

### 13.4 Owner-assignment coverage

- **Current state: PARTIAL** — Documentation Manager (Rigby) owns Path
  B; 12 axes in §18 UNASSIGNED matrix from S2102.
- **Path to WORKING**: R3.3 owner assignments land in
  `core/employees/jobs.py`. Estimated: 1 post-arc PR.

### 13.5 Cascade dual-path resolution

- **Current state: PARTIAL / ARCHITECTURAL DEBT** (S2102 F3 HIGH).
- **Path to WORKING**: F3 R3.5 lean (a) or (b) executed. Estimated:
  1-2 post-arc PRs (with per-release fallback preservation).

### 13.6 F1 chunker consolidation

- **Current state: PARTIAL / MEDIUM-now / HIGH-blocker-for-P3
  execution** (S2102 F1).
- **Path to WORKING**: R3.7 executed — STEP 3 `--embed` inline path
  migrates to `TextSplitter`. Estimated: 1-2 post-arc PRs (+ retrofill
  decision per D2100.11).

### 13.7 F2 overlap-metadata data lie

- **Current state: BROKEN** (S2102 F2 data-integrity defect).
- **Path to WORKING**: 1-line forward-fix + optional retrofill mgmt
  command per D2100.11. Estimated: 1 post-arc PR (+ optional 1 more
  for retrofill).

---

## 14. Known Drift

**Convention.** For design-preparation shape, findings F1-F8 are
DESIGN DECISIONS: framework axes definition, conflict-resolution
rule, governance-term disambiguation, metadata contract ratification,
owner assignments, artifact lifecycle model, F3 dual-cascade
resolution recommendation, D2100.11 F2 retrofill Chris-D-verdict
candidate. Each carries inheritance tag (parent / S2101 / S2102 /
S1304) and disposition (RATIFIED-BY-PARENT / RECOMMENDED / CHRIS-
D-VERDICT-CANDIDATE / BACKLOG).

### F1 — 8-axis retrieval authority framework — RATIFIED-BY-PARENT-D2100.8, populated at P3

- **Evidence:** parent §5.3 lists 8 axes for the framework; Q7 SIGN
  STRENGTHEN 2026-07-04 added definitional split + precedence
  clarifiers + tie-break rule; D2100.8 RATIFIED framework adoption
  as platform default retrieval-trust rubric.
- **P3 population — 7 evidence axes + 1 conflict-resolution rule
  (Q3 SIGN STRENGTHEN 2026-07-04):** the framework consists of 7
  document-scored evidence axes plus a conflict-resolution meta-rule
  applied after scoring. Prior draft called it "8 axes" for parent
  §5.3 lexical parity; corrected framing keeps 8 total elements but
  distinguishes evidence-scoring from rule-application.

**7 evidence axes (scored per doc):**

| # | Axis | Definition | Value domain | Populated from |
|---|------|------------|--------------|----------------|
| 1 | Primary vs synthesized evidence | Is doc primary evidence (child audit, verifier log) or synthesized evidence (canonical summary, executive summary)? | { primary, synthesized } | Doc type + filename regex |
| 2 | Runtime vs research authority | Is doc runtime-derived (PLATFORM_INVENTORY, generated indexes) or research-derived (audits, scoping docs)? | { runtime, research } | Doc metadata + DOC_LIFECYCLE.md §2c |
| 3 | Specificity to query | Does doc name the specific method / model / axis the query is about? | { specific, general } (computed) | Retrieval vector similarity + entity extraction |
| 4 | Recency | When was doc last embedded (proxies content age)? | timestamp | `last_embedded_at` |
| 5 | Supersession status | Is doc explicitly superseded by newer doc? | { current, superseded, deprecated } | `superseded_by` frontmatter |
| 6 | Canonical summary status | Is doc a canonical summary (xx99) or a child artifact? | { canonical, child, other } | Filename regex `NN99_.*_canonical_summary\.md` |
| 7 | Artifact lifecycle status | Where in lifecycle is doc (see F7)? | { draft, active, canonical, superseded, deprecated } | `lifecycle_status` field (P3 CONTRACT) |

**Meta-rule (not scored; applied AFTER scoring):**

| Element | Definition | Value domain | Populated from |
|---------|------------|--------------|----------------|
| Conflict-resolution rule | Which axis-pair rules apply to resolve authority conflicts when 2+ docs score similarly? | See F2 for 3-part rule (definitional split + precedence clarifiers + tie-break) | Framework config |

- **P3 disposition:** RATIFIED per D2100.8 by parent. This audit
  populates the 7 axes with definitions + value domains + population
  sources plus the meta-rule as post-scoring operator. Post-arc
  execution: axis-scoring service + rule engine as post-scoring
  operator.

### F2 — Conflict-resolution rule with runtime-facts vs research-posture split — RATIFIED-BY-PARENT-Q7-SIGN-FOLD, populated at P3

- **Evidence:** parent §5.3 + Q7 SIGN STRENGTHEN 2026-07-04 defined a
  3-part conflict-resolution mechanism:
  1. **Definitional split** — runtime facts vs research posture;
     `DOC_LIFECYCLE.md §2c` inventory-wins applies ONLY inside
     runtime-facts slice.
  2. **Precedence clarifiers** — supersession/deprecated overrides
     recency; canonical summary status is distinct from primary-vs-
     synthesized evidence type.
  3. **Tie-break rule** — newer measurement timestamp for runtime,
     source-of-truth hierarchy fallback.

- **P3 population of the rule:**

**Definitional split (Q4 SIGN STRENGTHEN 2026-07-04 — expanded):**
- **Runtime facts** = current platform state:
  - Registered agents (from `AGENT_MAP`)
  - Live endpoints (from `core/urls*.py`)
  - Active config (from Django settings + `platform_config_tool`)
  - DB schema (from Django models)
  - Beat schedule (from `PeriodicTask` + `core/celery.py`)
  - Health checks (from live probes)
  - Service inventory counts
  - **Feature flags + runtime overrides** (timeout overrides, focus
    mode / governor state, degraded_evidence toggles)
  - **Provider / runtime config surfaces** (LLM providers active,
    environment config, service_context = local|production)
- **Research posture** = interpretation:
  - Strategy (arc scoping docs)
  - Architecture intent (design docs)
  - Recommended plan (R-slot recommendations)
  - Rationale for a decision (D-verdicts)
  - **Constraints + trade-offs** (parked issues, anti-scope
    boundaries, delegated inheritance)
  - **Decision history** (D-verdicts, ADRs, close-card ratifications)
    — includes both the decision and its ratification provenance
- **§2c inventory-wins-on-conflict** applies ONLY inside runtime-facts
  slice; outside it, PLATFORM_INVENTORY is just another artifact.

**Precedence clarifiers:**
- Supersession / deprecated OVERRIDES recency.
- Canonical summary status is a DESIGNATION distinct from primary-vs-
  synthesized evidence type; canonical-summary-status changes default
  trust only in "posture" questions.
- Foundational handoffs (S1268-S1275, playbook v2, RESEARCH_
  OPERATING_SYSTEM.md) WIN on methodology questions.

**Tie-break rule:**
- When two runtime-authority artifacts disagree: prefer **newer
  measurement timestamp** (freshest probe).
- Else fall back to **source-of-truth hierarchy**: live health endpoint
  > cached inventory doc > human note.

- **P3 disposition:** RATIFIED per parent Q7 SIGN fold. Post-arc
  execution: conflict-resolution rule engine (config + code).

### F3 — Dual-cascade resolution recommendation (S2102 F3 R3.5 discharge) — CHRIS-D-VERDICT-CANDIDATE

- **Evidence:** S2102 F3 identified Path A + Path B architectural debt.
  Chris ratified S2102 F3 recommended lean (b) fold Path A gate into
  Path B preflight OR (a) wire Path B beat + deprecate Path A. Option
  (c) retire Path B is off-table per S1252/S1253 intent. Option (d)
  explicit dual-path is not recommended.
- **P3 recommendation — DEFAULT LEAN (b) fold Path A into Path B:**
  Merges hash-delta efficiency into MissionRunner shell; retires
  Path A at cutover; preserves Rigby's Employee OS ownership
  continuity. Option (a) wire Path B + deprecate Path A is acceptable
  fallback if Chris prefers staged migration.
- **Post-arc PR sequence for lean (b) — 3-step retirement sequence
per Q8 SIGN STRENGTHEN 2026-07-04 (idempotency-acceptance-check per
Q12 SIGN STRENGTHEN 2026-07-04):**
  1. **Wire canonical path** — add hash-delta gate to
     `docs_cascade.step_1_index` preflight. **Acceptance check
     BEFORE beat wiring (Q12 SIGN STRENGTHEN):** verify Path B
     idempotent under N re-runs (same inputs) + no duplicate writes
     beyond expected. Only after idempotency-acceptance passes, wire
     `rigby_documentation_manager_daily` beat entry (weekdays 06:30
     local per Rigby's job contract `triggers` field).
  2. **Observe stability** — Path A stays live in parallel for ≥ 1
     release cycle. WARN log line on Path A invocation. Observation
     targets: Path B fires successfully on schedule; no missed
     cascades; escalation Deliverable creation working; latency + error
     rate + embeddings-completeness metrics stay within budget. If any
     observation fails, HALT retirement + investigate.
  3. **Retire / deprecate old path** — retire `refresh_docs_corpus`
     beat entry; Path A code deleted; rollback plan: revert PR to
     restore beat entry + Path A code (both retained in git history).
  Post-cutover: Rigby's job contract already models this — no
  Employee OS surface change needed. Retirement PR MUST include
  explicit rollback note referencing this 3-step sequence.
- **Severity:** HIGH governance (T13 HIGH executable).
- **Disposition:** CHRIS-D-VERDICT-CANDIDATE at S2103 close card.
  Choice presented to Chris: (b) fold OR (a) wire-B + deprecate-A.

### F4 — Governance-term disambiguation across 5 meanings — RATIFIED-BY-PARENT-W5, populated at P3

- **Evidence:** parent §5.3 W5 critique identified "governance" over-
  load: (i) ownership, (ii) discipline, (iii) enforcement, (iv)
  documentation, (v) policy. Each Q5-Q8 governance question must be
  answered per-axis.

- **P3 population of the disambiguation table:**

| Q # | Question | Ownership answer | Discipline answer | Enforcement answer | Documentation answer | Policy answer |
|-----|----------|-------------------|--------------------|---------------------|-----------------------|----------------|
| Q5 | How prevent superseded outranking canonical in specific query contexts? | Rigby (via lifecycle_status enforcement) | Post-arc CI-lint on frontmatter supersession chain | Service-side validation at retrieval query time | `docs/topics/retrieval-authority-framework.md` describes rule | Framework CONFLICT-RESOLUTION rule (F2 supersession-overrides-recency clarifier) |
| Q6 | What lifecycle model applies? Who authorizes transitions? | Rigby (state-machine enforcement) + Chris (draft→active authorization) + xx99 author (active→canonical) + **doc-author (supersession chain declaration in frontmatter)** — Rigby enforces state machine on the declared chains (Q5 SIGN STRENGTHEN 2026-07-04) | Cascade-run + arc-close discipline | Enforcement service checks state transitions | `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` codifies | 5-state lifecycle model (F7) with transition triggers |
| Q7 | How does Rigby know retrieved finding is authoritative? | Retrieval framework designer (Group 2100) | Metadata contract population discipline (Rigby via cascade) | Contract-validation CI check + write-site guardrails | Framework doc describes authority-provenance labels | Framework CONFLICT-RESOLUTION rule + metadata contract |
| Q8-b | What metadata contract MUST every embedded chunk carry? | Chief of Staff owns **contract shape**; Rigby owns **population discipline + enforcement at write-sites**; CI / service-side validators enforce (Q5 SIGN STRENGTHEN 2026-07-04 clarifier) | Cascade population discipline | Service-side validation at ingest + CI check on contract shape | Framework doc + contract table | Hybrid contract per D2100.9 (10 core-required + doc-type profile + derivable + aspirational) |

- **P3 disposition:** RATIFIED per parent W5 critique. Post-arc: each
  cell drives a concrete execution item.

### F5 — D2100.9 metadata contract ratification with P2 additions — RATIFIED-BY-PARENT-D2100.9, populated at P3

- **Evidence:** parent D2100.9 RATIFIED hybrid contract shape (core-
  required + doc-type profile). S2101 §20.2 delivered candidate lists
  (7-field core-required + 3 doc-type profiles + 4 derivable + 5
  aspirational + Chris 18-field cross-reference). S2102 F1 + F2 + F5
  added P3 field additions.

- **P3 ratification — final contract shape:**

**Core-required (9 fields, fatal-if-missing) — Q6 SIGN STRENGTHEN
2026-07-04 downgraded `last_embedded_at`:**
1. `document_id` — UUID; join back to `Document` row
2. `document_type` — artifact class
3. `source_path` — file_path; provenance + supersession reasoning
4. `lifecycle_status` — draft/active/canonical/superseded/deprecated
5. `chunking_version` — semver or hash
6. `provenance_axis` — value enum
7. `chunker_id` — { chunker_a_local_jsonl, chunker_b_sync_cascade_de, chunker_c_text_splitter_async }
8. `overlap_size_actual` — real overlap in chars — **required-but-typed
   (Q6 SIGN STRENGTHEN 2026-07-04):** core-required for chunkers WITH
   overlap (chunker C 200-char + retrofilled chunker B 200-char); NULL
   permitted for no-overlap chunkers (chunker A local JSONL). Validator
   MUST enforce not-null for `chunker_id != chunker_a_local_jsonl`.
9. `upstream_source_provenance` — the ContentSource value at Document create-time

**Core-available (auto-populated, not core-required):**
- `embedding_model` — 100% populated LOCAL; automatically enforced by
  write-site
- `last_embedded_at` — **downgraded from core-required (Q6 SIGN
  STRENGTHEN 2026-07-04):** cannot guarantee write at every embed path
  (may be missing/late); absence must NOT make chunk unusable. Framework
  emits derived **`embedding_freshness`** label (fresh / stale /
  unknown) that degrades gracefully when absent. Populatable at every
  path (recommended); required NEVER.

**Supersession-metadata clarifier (Q6 SIGN STRENGTHEN 2026-07-04):**
`supersedes` / `superseded_by` are NOT core-required — supersession is
DERIVED from `lifecycle_status` (state `superseded` implies chain
exists) + Profile C fields (topic docs carry the pointer explicitly).
If future arcs identify supersession as a primary conflict-resolution
primitive requiring guaranteed presence, promote to core-required at
that point — for now, keep as Profile-C-scoped.

**Doc-type profiles:**
- Profile A (Research artifact): `research_group`, `session`,
  `domain_slug`, `child_slot`, `canonical_summary`, `head_commit`
- Profile B (Handoff): `session`, `handoff_target`, `head_commit_
  before`, `head_commit_after`
- Profile C (Topic doc / narrative anchor): `subsystem`,
  `superseded_by`, `supersedes`, `canonical`

**Derivable-at-ingest (4 fields, plus 1 contingent):**
- `canonical_summary` flag — filename regex
- `head_commit` — git rev-parse at cascade step 4
- `source_path` — already `Document.file_path`
- `last_embedded_at` — already chunk `created_at`
- **CONTINGENT** `related_arcs` — becomes derivable-at-ingest IF P3
  MANDATES frontmatter `related:` block for research-artifact profile;
  P3 CHOOSES to mandate. Moves to derivable-at-ingest.

**Aspirational (deferred to future arc):**
- `T-slot / R-slot references` — research-artifact-specific
- `decisions_locked` — ADR-style
- `implementation_status` — code-adjacent
- `parent_doc` — no formal parent pointer in frontmatter today

- **P3 disposition:** RATIFIED. Post-arc execution: schema migration
  adds `metadata` JSONField validators + service-side validation at
  cascade write-sites.

### F6 — Owner assignments for §18 UNASSIGNED axes — populated at P3

- **Evidence:** S2102 §18.1 UNASSIGNED matrix identified 12 axes
  without Employee OS ownership binding. S1304 T8 STILL-VALID (
  provenance model ownership unassigned). S2101 §18 UNASSIGNED same.

- **P3 population — owner assignment table:**

| Axis | Recommended owner | Employee OS location | Authority | Rationale |
|------|-------------------|----------------------|-----------|-----------|
| Path A `refresh_docs_corpus` | RETIRE per F3 lean (b) fold; if lean (a) wire Path B — Rigby is beat-entry owner | (Rigby via wire-B) | EXECUTE | Consolidates ownership with Path B; Rigby already owns cascade |
| Path B `rigby_documentation_manager_daily` | Rigby (Documentation Manager) — EXISTING | `core/employees/jobs.py:187 DOCUMENTATION_MANAGER` | EXECUTE (unchanged) | Already owned |
| Chunker A regime | LOCAL keyword-lane consumer — no Employee OS binding needed | (N/A — local dev only) | N/A | Isolated to LOCAL dev; no cross-plane surface |
| Chunker B regime | RETIRE per F1 R3.7; ownership vaporizes | (N/A after retirement) | N/A | Migrate to Chunker C |
| Chunker C regime | Rigby (Documentation Manager) | Extension to `DOCUMENTATION_MANAGER` job contract | EXECUTE (extend) | Rigby runs Path B step 4 embed which uses this |
| `_derive_source_type` derivation | No separate owner — write-site discipline is the fix | (N/A) | N/A | Function is correct given input; uniformity is a write-site problem |
| `Document.source` write-sites | Rigby (extend `DOCUMENTATION_MANAGER` authority) | Extension | EXECUTE (extend) | Sync-cascade write-site is Rigby's cascade |
| `DocumentEmbedding` schema | **Chief of Staff** (schema-contract owner) | Extension to `CHIEF_OF_STAFF` job contract | RECOMMEND (Chief of Staff recommends; Chris ratifies via PR review) | Neutral cross-plane owner avoids conflating cascade execution with schema-contract ownership |
| `docs/_provenance.json` writes | Rigby (via cascade tail R3.8 scheduling decision) | Extension | EXECUTE (extend) | Rigby's cascade owns the file |
| Retrieval semantics (framework config) | Chief of Staff (cross-plane owner) | Extension | RECOMMEND (Chief of Staff recommends; Chris ratifies via PR review) | Framework touches multiple plane consumers; neutral cross-plane owner appropriate |
| Corpus Health / drift detection | Rigby (drift observation authority already in contract) | Extended `DOCUMENTATION_MANAGER` responsibilities | EXECUTE + OBSERVE | Rigby already has `run_drift_observation` authority |
| Artifact lifecycle enforcement | Rigby (state-machine enforcement) | Extension | EXECUTE (extend) | Rigby's Path B mission would enforce transitions |

- **P3 disposition:** RECOMMENDED-BY-P3. Chris ratifies via post-arc PR
  extending `core/employees/jobs.py`. Discharges S1304 T8 STILL-VALID
  + S2102 R3.3.

### F7 — Artifact lifecycle model (draft / active / canonical / superseded / deprecated) — populated at P3

- **Evidence:** parent §5.3 called for lifecycle model with transition
  triggers. Q6 in the governance question set. Currently ambiguous
  because `Document.status` (draft/ready/completed) doesn't map cleanly
  to research-artifact lifecycle.

- **P3 population — 5-state lifecycle model:**

**States:**
- `draft` — newly-created, unratified; NOT yet indexed for retrieval
- `active` — ratified + indexed for retrieval; current
- `canonical` — consumed at xx99 aggregation; represents domain summary
- `superseded` — replaced by newer doc via `superseded_by` chain
- `deprecated` — abandoned; NOT indexed for retrieval

**Transition triggers + authorizations:**

| Transition | Trigger | Who authorizes | Enforcement mechanism |
|------------|---------|-----------------|------------------------|
| `draft` → `active` | Chris ratification post-Rigby SIGN cycle clean | Chris (via close card ratification statement) | Cascade write-site sets `lifecycle_status='active'` on ratification; verifier-loop cross-checks |
| `active` → `canonical` | xx99 aggregation event | Parent-scoping author (Claude) | Cascade write-site sets `lifecycle_status='canonical'` at xx99 close; verifier-loop confirms `NN99_` filename regex |
| `active` → `superseded` | Newer doc declares `superseded_by` chain | Author of superseding doc | Cascade write-site cross-references frontmatter; verifier-loop confirms chain |
| `canonical` → `superseded` | Next-generation canonical lands | Parent-scoping author of new canonical | Same as active→superseded |
| `draft` → `deprecated` | Abandon-authorization by Chris OR arc-close negative decision | Chris (via close card OR arc-close verdict) | Cascade write-site sets `lifecycle_status='deprecated'`; retrieval ranker excludes |
| `active` / `canonical` → `deprecated` | Explicit deprecation decision (rare — usually via supersession) | Chris | Same as above |

**Retrieval behavior by lifecycle status (Q11 SIGN STRENGTHEN
2026-07-04 — refined superseded rule):**
- `active` — full retrieval weight per axis scores
- `canonical` — full retrieval weight; canonical-summary-status axis
  boost for "posture" queries only. **"Canonical" means CURRENT BEST,
  not eternal closure** — a canonical can be superseded when the next-
  generation canonical lands.
- `superseded` — **DE-RANKED by default** + label emitted with
  authority-provenance. **EXCLUDED only when** `intent=runtime_facts`
  AND a non-superseded canonical exists for the same domain. Rationale:
  historical / trace queries need access to superseded material;
  hard-exclusion creates "silent missing evidence" failures.
- `deprecated` — EXCLUDED from retrieval (strictly "do not use going
  forward" — distinct from `superseded` which is "replaced by newer").
- `draft` — EXCLUDED from retrieval until ratified.

- **P3 disposition:** DESIGNED. Post-arc execution: schema addition of
  `lifecycle_status` field + state-machine enforcement service +
  Rigby's job contract extension.

### F8 — D2100.11 F2 retrofill choice — CHRIS-D-VERDICT-CANDIDATE at S2103 close card

- **Evidence:** S2102 F2 identified overlap-metadata data lie in sync-
  cascade path — 24,980 chunks report `overlap_size=0` despite
  actually overlapping 200 chars. Chris "agree all" at S2102 close
  surfaced D2100.11 candidate for retrofill decision. R2.7 forward-fix
  is 1-line; retrofill touches historical shared state and needs
  Chris D-verdict.
- **Two options presented:**

**Option (a) — Forward-fix only:**
- 1-line change at `sync_docs_index_to_documents.py:394` passes
  `overlap_size=200` on future create calls.
- Historical 24,980 sync_docs rows carry the lie forever.
- Retrieval consumers computing coverage from `overlap_size` continue
  to under-count sync_docs population for historical rows.
- Migration tools cannot reconstruct chunk boundaries from persisted
  metadata for historical rows.
- **Pros:** minimal-risk, no migration intent required, 1 PR.
- **Cons:** data-integrity defect persists forever for historical
  data.

**Option (b) — Forward-fix + retrofill historical rows:**
- Same forward-fix + one-time management command backfills historical
  `overlap_size=200` for all `ingested_via='sync_docs'` rows.
- Requires migration intent + rollback plan since it touches shared
  state.
- Historical rows become semantically-honest.
- **Pros:** data-integrity defect resolved for entire history.
- **Cons:** migration risk (2 PRs — forward-fix + retrofill mgmt
  command); requires backup + rollback plan; small chance of hidden
  downstream consumer relying on the wrong value.

- **P3 recommendation (Q13 SIGN STRENGTHEN 2026-07-04 — gated on
  PROD probe):** **(b) forward-fix + retrofill AFTER a PROD probe**
  confirms row counts, confirms no unexpected consumers, and
  captures a pre-retrofill snapshot. Without the probe, blind
  retrofill is over-confident given U6 LOCAL↔PROD comparability
  meta-unknown (PROD may have different row count / different
  downstream consumers). PROD probe items:
  1. Count `DocumentEmbedding.objects.filter(ingested_via='sync_docs',
     overlap_size=0).count()` on PROD DB.
  2. Grep PROD codebase for `overlap_size` consumers not present in
     LOCAL.
  3. Capture pre-retrofill dump (JSON export of affected rows) with
     restore path documented.
  4. Only after 1-3 pass, execute retrofill.
  Rollback plan: keep the pre-retrofill dump; if any consumer breaks,
  restore affected rows from dump.
- **Severity:** MEDIUM data-integrity (S2102 F2 dispositioned MEDIUM
  current / HIGH-if-consumer-lands).
- **Disposition:** CHRIS-D-VERDICT-CANDIDATE at S2103 close card.
  Chris chooses (a) or (b) at close.

### Post-arc execution items enumerated per finding

For explicit T-slot queue reference — mapped in §15 T-table extended
per playbook §12 debt classifications.

---

## 15. Known Technical Debt

Per playbook §12 debt classifications. Bounded remediation sketches
only per Q5 SIGN belongs-to boundary. P3 inherits S2101 T1-T10 + S2102
T11-T17 and adds P3-scoped design debt.

### 15.1 Debt-table roll-up (S2101 + S2102 re-attested + S2103 additions)

Inherited from S2102 §15.1 (no changes to items T1-T17). P3 additions:

| ID | Debt | Severity | Origin | Remediation sketch |
|----|------|----------|--------|--------------------|
| T18 | Retrieval authority framework unimplemented (SPEC-ONLY) | MEDIUM | **S2103-new (F1)** | Post-arc: axis-scoring service + ranker consumer at retrieval entry point |
| T19 | Conflict-resolution rule engine unimplemented (SPEC-ONLY) | MEDIUM | **S2103-new (F2)** | Post-arc: rule engine config + code (co-lands with T18) |
| T20 | Owner-assignment PR uncoded | MEDIUM | **S2103-new (F6)** | Post-arc: extend `core/employees/jobs.py` — 1 PR per §18 recommendation table |
| T21 | Artifact lifecycle state machine unimplemented | MEDIUM | **S2103-new (F7)** | Post-arc: schema addition + state-machine enforcement service + Rigby's Path B extension |
| T22 | D2100.9 metadata contract validation gap | MEDIUM | **S2103-new (F5)** | Post-arc: schema migration + cascade write-site validation + CI check |
| T23 | `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` uncreated (R3.4) | LOW | **S2103-new (F4)** | Post-arc: 1-PR doc creation replacing MEMORY.md rules |
| T24 | `docs/topics/retrieval-authority-framework.md` uncreated | LOW | **S2103-new (F1)** | Post-arc: 1-PR doc creation with F1 axes + F2 rule + F4 disambiguation |
| T25 | `docs/topics/docs-ingestion-cascade.md` uncreated (R3.1) | LOW | **S2103-new (inherited R3.1)** | Post-arc: 1-PR doc creation per S1304 T4 + S2101 T4 + S2102 T4 STILL-VALID |

### 15.2 Debt-severity re-attestation summary

| Severity | S2102 close baseline | S2103 status | Change |
|----------|----------------------|---------------|--------|
| HIGH | T1, T2, T13, T16 | T1, T2, T13, T16 STILL-VALID; no P3 additions | 0 net change |
| MEDIUM | T3-T10, T11-T12, T14-T15 | T3-T10, T11-T12, T14-T15 STILL-VALID; **T18, T19, T20, T21, T22 NEW** | +5 net MEDIUM |
| LOW | T17 | T17 STILL-VALID; **T23, T24, T25 NEW** | +3 net LOW |

**P3-scope observation:** No new HIGH debt — P3 findings are DESIGN
DECISIONS that when executed post-arc REMOVE existing HIGH debt (T13
via F3, T16 via F5 chunker_id addition). MEDIUM additions are the new
implementation-substrate debt introduced by the design; LOW additions
are the doc-publication debt.

### 15.3 Knowledge-debt (KD-1..KD-7) re-observation

Per S2101 §15.3 taxonomy. P3 does not re-measure LOCAL DB — S2102
verifier-loop values remain baseline. P3 substrate readiness for each
KD category:

| Category | S2102 status (LOCAL) | S2103 substrate readiness change |
|----------|-----------------------|----------------------------------|
| KD-1 unembedded-on-disk | 0 | UNCHANGED — Path A gate detects |
| KD-2 stale-embed-post-content-change | UNMEASURABLE | **SUBSTRATE DESIGN-COMPLETE** — F5 `chunking_version` + `chunker_id` added to core-required; post-arc execution unlocks measurement |
| KD-3 cascade-PR-forgot-embed-step | 0 currently | UNCHANGED — S1802 remediation holds |
| KD-4 metadata-blank-at-ingest | 24,980 (48.1%) | **RESOLUTION PATH READY** — F5 hybrid contract population + F1 chunker_id would populate metadata JSONField for sync_docs population |
| KD-5 provenance-index-stale | STILL INDETERMINATE | **MECHANISM DESIGNED** — R3.8 §14 governance-decision cluster; post-arc execution required |
| KD-6 orphan-Document-row-post-file-move | 0 | UNCHANGED — spot-check |
| KD-7 mis-linked-embeddings | 0 detected coarse | UNCHANGED — fine-grained deferred |

### 15.4 D2100.11 F2 retrofill decision — CHRIS-D-VERDICT-CANDIDATE

Per F8 above. Chris chooses (a) forward-fix only vs (b) forward-fix +
retrofill at S2103 close card.

### 15.5 R3.6 backfill activation criteria (F6 discharge)

Per parent Q13 + S2102 F6 governance-note. **P3 presents 3-option
Chris D-verdict menu per Q14 SIGN STRENGTHEN 2026-07-04** (since
S2101 D5 originally flagged this as drift + S2102 F6 reclassified to
incomplete-wiring, Chris deserves an explicit menu — not a single
P3-unilateral declaration):

**Option (a) — De-scope / retire enum value (P3 recommended lean):**
- Document that `embed_agent_activity` is manual-only.
- Remove enum value's aspirational status from
  `DocumentEmbedding.ingested_via`.
- Basis: S2102 F6 LOW severity, no observable harm, no product
  decision to activate exists, orphan-infrastructure risk (S2001 F9
  pattern).

**Option (b) — Activate + schedule:**
- Add scheduling with observation targets.
- **Trigger that would justify (b):** clear product driver (specific
  use case for `embed_agent_activity` — dreams/hive-minds/knowledge-
  sources ingestion goes live) + defined cadence (daily / weekly /
  event-triggered) + success metric (e.g., N embed rows per cadence).
- If Chris identifies such a driver, activate.

**Option (c) — Defer to future arc:**
- Keep enum value in place; do not retire; do not activate.
- Revisit at future Group 2200+ RAG-adjacent arc.
- Justified if Chris expects but hasn't yet decided on a driver
  (option (b) trigger).

Chris ratifies at close card. P3 lean = **(a) de-scope**; alternatives
kept explicit per fold discipline.

### 15.6 R3.7 chunker consolidation design (F1 discharge)

Per S2102 F1 + §17.2 near-isomorphism observation. **P3 recommendation:**
**retire Chunker B in favor of Chunker C** — STEP 3 `--embed` inline
path migrates to `TextSplitter`.

**Rationale:**
- Chunkers B and C are NEAR-ISOMORPHIC in chunking regime (same 1000-
  char + 200-overlap + paragraph/sentence boundary).
- Chunker B lacks metadata population discipline (48.2% empty metadata)
  + overlap-metadata data lie (F2).
- Chunker C is centralized library; ownership goes to Rigby via Path B
  extend.
- Retirement resolves F1 + F2 + S2101 F2 48.2%-empty-metadata slice in
  a single minimal-diff PR.

**Post-arc execution (2-3 PRs):**
1. Migrate STEP 3 `--embed` inline path to call `TextSplitter.split_text`.
2. Retrofill decision per D2100.11 (F8 above) resolves overlap metadata
   for historical rows.
3. Delete `chunk_content` function once migration verified stable.

Retrofill option (b) at F8 is preferred because chunker consolidation
provides good migration cover.

### 15.7 R3.8 provenance-index scheduling decision (F7 sub-item)

Per S2102 §15.4 reclassification. **P3 recommendation:**
**schedule `build_docs_provenance` as cascade tail step** (Step 5 of
Path B mission) — rather than adding a separate beat entry or CI-lint.

**Rationale:**
- Cascade-tail placement gives Rigby's Path B mission ownership +
  observation surface.
- Avoids separate beat entry that could drift out of sync with cascade
  runs.
- Chris's MEMORY.md rule (`feedback_docs_cascade_at_every_close`) is
  satisfied automatically since every cascade end runs it.
- CI-lint alternative was fragile (validates mtime, easy to fake).

**Post-arc execution (1 PR):** extend `docs_cascade.py` MissionRunner
with Step 5 `build_docs_provenance` + Rigby's job contract
`daily_routine` extends by 1 step.

**Failure-policy contract (Q15 SIGN STRENGTHEN 2026-07-04):**
- Step 5 `build_docs_provenance` failure MUST NOT fail the entire
  cascade. Emit `[DOCS_CASCADE_STEP5_PROVENANCE_WARN]` structured log
  + retry with 30s backoff (2 retries max) + Rigby records
  `degraded_evidence=true` + drift observation continues.
- **Upper time cap for Step 5: 120 seconds** — must not blow the 10-
  minute daily mission SLA. If wall-time > 120s, abort + emit
  timeout warning + degraded_evidence flag.
- Failure of Step 5 does NOT trigger escalation Deliverable (unlike
  steps 1-4 which are cascade-critical). Failure is observed +
  reported in daily evidence summary.

**Alternative:** separate `PeriodicTask` beat entry — NOT RECOMMENDED
because drift risk (drift out of sync with cascade runs).

Chris ratifies at close card.

---

## 16. Boundary Violations

Per playbook §12 finding types.

**None observed at design-preparation boundaries.**

Adjacent-but-not-violating patterns:
- **Group 1300 (Memory) boundary respected** — retrieval framework
  does not touch `AgentMemory` or conversation memories. E↔D boundary
  from S1304 G5 is respected on the docs side.
- **Group 1700 (Observability) boundary respected** — event surface
  recommendations at §10 route to Group 1700 delegation; framework does
  not design observability primitives directly.
- **Group 1900 (Authority Enforcement) boundary respected** —
  retrieval framework uses `AuthorityLevel` enum values (Group 1900's)
  but does not re-implement authority checks.
- **Group 2000+ (Event / Integration Architecture) boundary
  respected** — event surface recommendations route to Group 2000+
  retroactive fold-in per S2102 §19.4 pattern.
- **Employee OS primitives respected** — §18 owner assignments extend
  existing `AIEmployee` + `JobContract` frozen dataclasses; no new
  MissionRun-model duplication (per `EMPLOYEE_OS_PRIMITIVES.md`).

---

## 17. Duplicate or Overlapping Systems

Per playbook §12 duplicate_model / overcoupling classifications.

**S1904 CONSOLIDATION-shape §17.1 posture-register pattern** inherits
as template (5-plane posture register at S1904 §17.1). P3 §17.1
adopts the CONSOLIDATION-shape pattern with framework-axis columns.

### 17.1 Retrieval-authority framework — per-axis spec-readiness register

**Header rename per Q16 SIGN STRENGTHEN 2026-07-04:** for design-
preparation shape, S1904 audit posture-vocabulary reads like "grading
an implementation that hasn't happened yet". Rename to **spec-readiness
vs runtime-realization** register with mapping:
- **PERMEABLE-BROKEN → "Spec-ready / runtime-missing"** (expected at
  design-prep close — post-arc T-slot execution unblocks realization)
- **STRUCTURAL-DROP** unchanged semantics (excluded from posture matrix
  by design; NOT a correctness statement)
- **STABLE / CANONICAL / CLEAN** unchanged (would require runtime
  realization — not expected at design-prep close)

Master spec-readiness register (columns per parent §5.3 framework spec +
Q7 SIGN fold definitional split):

| Axis | Framework-implementation state | Contract-shape state | Owner-assignment state | Runtime enforcement state | Posture verdict |
|------|--------------------------------|----------------------|-------------------------|---------------------------|-----------------|
| 1. Primary vs synthesized | Definition + population source RATIFIED at P3 §14 F1 | Metadata contract F5 covers doc_type + canonical_summary flag | Rigby via Path B extend | SPEC-ONLY (post-arc T18) | **PERMEABLE-BROKEN** — spec ready, runtime not implemented |
| 2. Runtime vs research | Definition RATIFIED at P3 §14 F2 (runtime-facts vs research-posture split) | Metadata contract F5 covers via provenance_axis + document_type | `DOC_LIFECYCLE.md §2c` existing policy respected | SPEC-ONLY (post-arc T18 + T19) | **PERMEABLE-BROKEN** — spec ready, runtime not implemented |
| 3. Specificity to query | Computed at retrieval query-time (no persistence needed) | N/A (query-time computed) | Retrieval ranker (post-arc) | SPEC-ONLY (post-arc T18) | **STRUCTURAL-DROP** — query-time-computed axis; no separate implementation surface |
| 4. Recency | `last_embedded_at` in core-required contract (F5 field 5) | RATIFIED at P3 §14 F5 | Cascade owner (Rigby via Path B) | PARTIAL — field derivable from chunk `created_at` today | **PERMEABLE-BROKEN** — populatable, but no consumer using recency axis today |
| 5. Supersession status | Definition RATIFIED at P3 §14 F2 (precedence clarifier) + F7 lifecycle model | `superseded_by` + `supersedes` in Profile C (doc-type profile) | Doc author declares + Rigby enforces state-machine | SPEC-ONLY (post-arc T21 lifecycle state machine) | **PERMEABLE-BROKEN** — spec ready, state machine not implemented |
| 6. Canonical summary status | Definition RATIFIED at P3 §14 F1 (axis 6) + F2 (precedence clarifier) | Derivable-at-ingest via filename regex (F5 derivable set) | xx99 author (parent-scoping author) | PARTIAL — filename regex + Profile A `canonical_summary` flag both exist | **PERMEABLE-BROKEN** — spec ready, consumer axis-scoring not implemented |
| 7. Artifact lifecycle status | 5-state model RATIFIED at P3 §14 F7 | `lifecycle_status` in core-required contract (F5 field 4) | Rigby (state-machine enforcement) | SPEC-ONLY (post-arc T21) | **PERMEABLE-BROKEN** — model designed, no field + state-machine yet |
| 8. Conflict-resolution rule | 3-part rule RATIFIED at P3 §14 F2 (definitional split + precedence clarifiers + tie-break) | Framework config, not chunk-level | Chris + Group 2100 arc close | SPEC-ONLY (post-arc T19) | **PERMEABLE-BROKEN** — spec ready, rule engine not implemented |

**Spec-readiness distribution roll-up (Q16 SIGN STRENGTHEN 2026-07-04
renamed):**
- **Spec-ready / runtime-missing** (was PERMEABLE-BROKEN): 7 axes
  (Axes 1, 2, 4, 5, 6, 7, 8) — spec-complete design-preparation,
  runtime not implemented (expected at design-prep close)
- **STRUCTURAL-DROP:** 1 axis (Axis 3 specificity — query-time-computed;
  no persistence surface, verdict "structurally dropped" from the
  posture register for spec-complete-check discipline per S1904 §17.1
  fold pattern; NOT a statement about correctness)
- **STABLE:** 0
- **CANONICAL:** 0
- **CLEAN:** 0

**Cross-axis observation:** all 7 non-dropped axes are Spec-ready /
runtime-missing by *design-preparation-shape convention* — the arc's
job was to spec, not to implement. The 8 axes ARE ready for post-arc
T18-T22 execution. This is the **expected** posture at Group 2100 P3
close; not a defect.

### 17.2 Corpus-governance dimensions — per-dimension posture register

Per §14 F4 5-dimension disambiguation:

| Dimension | Design-decision state | Assignment state | Enforcement state | Documentation state | Posture verdict |
|-----------|------------------------|-------------------|---------------------|----------------------|-----------------|
| Ownership | Recommended at §18 (matrix populated) | RECOMMENDED-BY-P3 — Chris ratifies via post-arc PR | N/A (assignment IS enforcement mechanism) | Contract lands in `core/employees/jobs.py` PR | **PERMEABLE-BROKEN** — spec ready, PR not shipped |
| Discipline | Cascade-run + close-out rituals identified (§14 F4 table + F7 transitions) | Rigby (Path B mission) + Chris (close-card ratification) | Cascade-run enforcement | `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` (post-arc) + MEMORY.md rules (existing) | **PARTIAL** — MEMORY.md rules operate today; canonical doc not shipped |
| Enforcement | Contract-validation CI + service-side validation identified | Rigby (Path B) + CI machinery (post-arc) | SPEC-ONLY (post-arc T22 D2100.9 contract validation) | Framework doc describes CI check | **PERMEABLE-BROKEN** — spec ready, CI not implemented |
| Documentation | Canonical doc + framework doc + cascade doc identified (§11.2) | Claude Code (docs authoring) | N/A (documentation IS itself) | POST-ARC EXECUTION (T23, T24, T25) | **PARTIAL (informal) — Q17 SIGN STRENGTHEN 2026-07-04:** MEMORY.md rules exist as **informal substrate, NOT canonical governance**. Replacement by canonical doc (`docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md`) is explicit post-arc deliverable (T23). MEMORY.md is proto-doc, not authoritative reference — informal substrate qualifier prevents post-arc consumers from over-crediting current-state documentation. |
| Policy | Framework CONFLICT-RESOLUTION rule + lifecycle model + metadata contract land as canonical policy | Chris (via D2100.8, D2100.9, D2100.11) + Group 2100 arc close | Framework itself (retrieval + ranker) | Framework doc | **PERMEABLE-BROKEN** — spec ready, runtime consumers not implemented |

**Governance-dimension posture distribution:**
- **PARTIAL:** 1 dimension (Discipline — cascade-run rituals operate
  today via Rigby's Path B mission)
- **PARTIAL (informal):** 1 dimension (Documentation — MEMORY.md
  informal substrate operates as proto-doc pending canonical replacement)
- **Spec-ready / runtime-missing** (was PERMEABLE-BROKEN per Q16 fold):
  3 dimensions (Ownership + Enforcement + Policy) — spec ready, post-
  arc execution pending

**Cross-dimension observation:** Discipline + Documentation dimensions
have existing informal-substrate (MEMORY.md rules); the P3 designs
replace these with canonical mechanisms. Ownership + Enforcement +
Policy dimensions are fully new — no informal substrate exists.

### 17.3 Cross-arc S1904 §17.1 pattern conformance

P3 §17.1 follows S1904 CONSOLIDATION-shape §17.1 posture-register
pattern with adaptations:
- **S1904 used 8-plane taxonomy;** P3 uses **8-axis framework taxonomy**
  (structurally parallel).
- **S1904's STRUCTURAL-DROP posture** semantics = "excluded from
  cross-plane composition pending prerequisites; NOT a statement about
  correctness" — P3 uses same semantics for Axis 3 (query-time-computed).
- **S1904's CLEAN posture** semantics = "genuinely separated by design"
  — P3 does NOT use CLEAN because no axis is genuinely CLEAN
  (post-arc executable exists for all 7 non-dropped axes).

**Meta-methodology observation:** P3 §17.1 durability at 5-arc running
tally (S1806, S1904, S2004, S2099, S2103) suggests CONSOLIDATION-shape
§17.1 posture-register format is stable. Candidate for playbook v3 §16
CONSOLIDATION-shape template standardization.

---

## 18. Ownership Gaps

Per playbook §12 unclear_owner findings.

### 18.1 Ownership recommendation matrix (P3 R3.3 discharge)

Per §14 F6 owner-assignment table (reproduced with detail):

| Axis (from S2102 §18.1 UNASSIGNED matrix) | P3 recommended owner | Employee-OS location | Authority | Rationale |
|-------------------------------------------|-----------------------|----------------------|-----------|-----------|
| Path A `refresh_docs_corpus` | RETIRE (per F3 lean b) OR Rigby via wire-B (lean a) | (Rigby via Path B) | EXECUTE | Consolidates ownership with Path B |
| Path B `rigby_documentation_manager_daily` | Rigby (EXISTING) | `core/employees/jobs.py:187` | EXECUTE (unchanged) | Already owned |
| Chunker A regime | (no Employee-OS binding needed) | N/A | N/A | LOCAL keyword-lane only |
| Chunker B regime | RETIRE (F1 R3.7) | N/A | N/A | Retire in favor of C |
| Chunker C regime | Rigby (extend) | `DOCUMENTATION_MANAGER` extension | EXECUTE (extend) | Rigby runs Path B step 4 |
| `_derive_source_type` | (no separate owner) | N/A | N/A | Function correct; discipline is at write-site |
| `Document.source` write-sites | Rigby (extend) | `DOCUMENTATION_MANAGER` extension | EXECUTE (extend) | Sync-cascade write-site is Rigby's |
| `DocumentEmbedding` schema | Chief of Staff | `CHIEF_OF_STAFF` extension | RECOMMEND | Cross-plane data-contract owner |
| `docs/_provenance.json` writes | Rigby (extend) | `DOCUMENTATION_MANAGER` extension | EXECUTE (extend) | Rigby's cascade owns the file |
| Retrieval semantics (framework config) | Chief of Staff | `CHIEF_OF_STAFF` extension | RECOMMEND | Framework touches multiple plane consumers |
| Corpus Health / drift detection | Rigby (EXISTING drift-obs authority) | `DOCUMENTATION_MANAGER` responsibility extension | EXECUTE + OBSERVE | Rigby has `run_drift_observation` |
| Artifact lifecycle enforcement | Rigby (extend) | `DOCUMENTATION_MANAGER` extension | EXECUTE (extend) | Path B mission enforces transitions |

### 18.2 Ownership-gap resolution rationale

**Two-employee shape rationale (Rigby + Chief of Staff):**

- Assignments split so that **execution ownership** (write-site
  instrumentation, cascade population, enforcement checks) lives with
  **Rigby** — she already owns Path B and has drift-observation
  authority. Extensions to her contract are additive.
- **Schema-contract ownership** (contract shape + semantics) +
  **framework-config ownership** live with **Chief of Staff** because
  they span multiple plane consumers (retrieval, ingest, framework,
  ranker) and don't fit cleanly into a single-plane execution mission.
- **Scope clarifier (Q7 SIGN STRENGTHEN 2026-07-04):** "Chief of
  Staff RECOMMEND" covers **contract shape + semantics** (what
  DocumentEmbedding.metadata SHOULD carry; what the enum value domain
  is; what conflict-resolution defaults apply). "Rigby EXECUTE" covers
  **write-site instrumentation + enforcement checks** (populate the
  fields at cascade write-site; validate at ingest; open attention
  items on violations). When P3 §18.1 assigns Rigby "Document.source
  write-sites", the scope is **document ingestion interfaces**
  (`sync_docs_index_to_documents.py`, cascade write-sites) — NOT the
  `Document.source` schema field itself (that's Chief of Staff's
  schema-contract territory).
- **No new AIEmployee handles are proposed.** Both owner types
  (Documentation Manager + Chief of Staff) already exist. New handle
  proposals are avoided per `EMPLOYEE_OS_PRIMITIVES.md`
  anti-duplication guidance.

**Alternative considered:** create new `retrieval_authority_owner` +
`chunker_regime_owner` + `document_source_provenance_owner` handles.
REJECTED because:
- Fragments ownership across small missions with no cohesive job
  scope.
- Violates Employee OS anti-duplication guidance.
- Fails the "job coherence" test — a `retrieval_authority_owner` has no
  daily routine, no observation targets, no escalation surface distinct
  from what Chief of Staff already covers.

### 18.3 Rigby's job contract extensions

Post-arc PR extends `DOCUMENTATION_MANAGER` contract with:

- **`responsibilities` additions (Q9 SIGN STRENGTHEN 2026-07-04 —
  phased enforcement pattern):**
  - **Observe** `DocumentEmbedding.metadata` contract population per
    D2100.9 at cascade write-site — **detect violations + open
    attention items** initially (warn-only mode). **Promote to
    hard-fail enforcement conditional on T22 landing** (contract
    fields + validators exist).
  - **Observe** artifact `lifecycle_status` state-machine transitions —
    detect invalid-transition attempts + open attention items
    initially. **Promote to enforcement conditional on T21 landing**
    (state-machine service exists).
  - Own `Document.source` write-site diversification per F5-FULL —
    write-site discipline at document-ingestion interfaces
    (`sync_docs_index_to_documents.py`), NOT schema-field ownership.
  - Own `docs/_provenance.json` cascade-tail rebuild (R3.8).

- **`authority` additions (Q9 SIGN STRENGTHEN 2026-07-04 — phased):**
  - `observe_metadata_contract`: `AuthorityLevel.OBSERVE.value`
    (warn-only mode pre-T22)
  - `enforce_metadata_contract`: `AuthorityLevel.EXECUTE.value`
    (conditional on T22 landing)
  - `observe_lifecycle_transitions`: `AuthorityLevel.OBSERVE.value`
    (attention-item mode pre-T21)
  - `enforce_lifecycle_transitions`: `AuthorityLevel.EXECUTE.value`
    (conditional on T21 landing)
  - `rebuild_provenance_index`: `AuthorityLevel.EXECUTE.value`
  - `diversify_document_source_at_writesite`:
    `AuthorityLevel.EXECUTE.value`

- **`daily_routine` additions:**
  - Step 5 — `build_docs_provenance` (was manual; per R3.8 becomes
    cascade-tail).
  - Step 6 — Contract-validation observation (log any chunks failing
    metadata contract at write-time).

- **`success_metrics` additions:**
  - Cascade-tail `docs/_provenance.json` mtime is newer than latest
    handoff commit.
  - Zero chunks written with metadata-contract-violating shape.
  - Zero lifecycle-status invalid-transition attempts.

### 18.4 Chief of Staff extensions

Post-arc PR extends `CHIEF_OF_STAFF` contract with:

- **`responsibilities` additions:**
  - Own `DocumentEmbedding` schema contract (structure of metadata
    JSONField, chunker_id enum, provenance_axis enum).
  - Own retrieval-authority framework config (axis scoring parameters,
    conflict-resolution rule thresholds).

- **`authority` additions (Q10 SIGN STRENGTHEN 2026-07-04 — tier
  clarifier + future autonomy upgrade path):**
  - `recommend_schema_contract_changes`: `AuthorityLevel.RECOMMEND.value`
    — schema is always RECOMMEND-only; autonomous migrations could
    break prod
  - `recommend_framework_config_changes_authority_semantics`:
    `AuthorityLevel.RECOMMEND.value` — changes to conflict-resolution
    defaults, authority labels, precedence clarifiers stay RECOMMEND
  - **Future autonomy upgrade note (deferred to post-arc):** framework
    config could split into two tiers post-arc — RECOMMEND for
    authority-semantics changes + EXECUTE (bounded) for non-breaking
    tuning knobs (weights/thresholds) with audit log + auto-revert on
    regressions. NOT implemented this arc; noted as future upgrade path.

- **Boundary statements:**
  - Chief of Staff RECOMMENDS; Chris ratifies via PR review. Chief of
    Staff does NOT execute schema migrations or framework-config PRs
    directly.
  - Bounded EXECUTE authority for tuning knobs is a deferred autonomy
    upgrade — not shipped this arc.

### 18.5 Ownership-gap discharge summary

- **S1304 T8 STILL-VALID (provenance model ownership unassigned)** —
  DISCHARGED via §18.3 Rigby extension for `docs/_provenance.json`.
- **S2101 R3.3 owner assignments per §18 UNASSIGNED axes** —
  DISCHARGED via §18.1 matrix.
- **S2102 R3.3 owner assignments for §18.1 UNASSIGNED axes** —
  DISCHARGED via §18.1 matrix.
- **S1304 G5 E↔D boundary unowned** — DISCHARGED (docs side owned by
  Rigby via extended contract; memory side remains Group 1300
  territory per §16 boundary respect).

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows per
playbook §11.2 §19 spec. Feeds P4 R4.x handoffs + xx99 §8 T0/Gate + T1
+ T2 + T3 tiered queue.

### 19.1 P3 → P4 (S2104 — Behavior Substrate Structured Observation)

**P4 triage list (Q18 SIGN STRENGTHEN 2026-07-04).** 8 R4.x handoffs is
heavy for one P4 session. Explicit triage split so P4 knows what MUST
ship vs what is BACKLOG (parallels S2102 §19.1 P3 triage pattern):

- **P4 core must-ship (5 items):** R4.1 (chunker-population correlation)
  + R4.2 (acceptance criteria observation) + R4.3 (Corpus Health
  dimensions) + R4.4 (D2100.7 conditional-elevation logic) + R4.6
  (retrieval framework acceptance).
- **P4 backlog / optional (3 items):** R4.5 (Path A/B activation —
  conditional on F3 choice) + R4.7 (lifecycle-transition observation —
  gated on T21 post-arc landing) + R4.8 (governance-dimension mixed-
  mode observation).
- **Alternative split:** P4a core + P4b backlog. Chris may split at
  P4 open if time permits. Single-child P4 with triage triage is the
  recommended default.

**Individual handoffs:**

- **R4.1 (from P2, re-attested) — MUST-SHIP — Chunker-population
  correlation observation.** Test whether recent SIGN cycles that
  failed retrieval-quality checks correlate with hitting Chunker B
  (sync-cascade) or Chunker C (async) populations. If N ≥ 10 observed
  cases show B-vs-C imbalance, F2 elevates from MEDIUM to HIGH.
- **R4.2 (from P2, re-attested + P3 extended) — MUST-SHIP —
  Institutional-knowledge-layer acceptance criteria observation** per
  parent §5.1 criteria 2-5. Criterion 2 becomes measurable once F1
  chunker regimes are documented (S2102) and F5 metadata contract
  lands post-arc.
- **R4.3 (from P2, re-attested + P3 extended) — MUST-SHIP — Corpus
  Health Score dimension additions.** Add dimensions for P3 §14 F1
  axes coverage ratio, F5 metadata contract population rate, F7
  lifecycle-status transition validity rate. Feeds §5.5 dimension
  list per D2100.10.
- **R4.4 (from P2, re-attested) — MUST-SHIP — D2100.7 conditional-
  elevation logic for freshness bounds.** P4 explicitly discharges
  the D2100.7 rule per Q15 SIGN STRENGTHEN 2026-07-04 at S2101 close.
- **R4.5 (from P2, conditional-on-P3-F3-choice) — BACKLOG — Path A
  vs Path B activation-observation.** If P3 wires Path B beat (F3
  lean a OR b), P4 observes N ≥ 10 daily runs for escalation
  Deliverable dedupe accuracy + step_5 (per Rigby's extended job
  contract) drift observation reliability. If F3 lean chosen is (c)
  or (d), R4.5 SKIPPED per Q19 SIGN STRENGTHEN branch at S2102 close.
- **R4.6 (P3-new) — MUST-SHIP — Retrieval-authority framework
  acceptance observation.** After post-arc T18/T19 lands, P4 observes
  N ≥ 10 retrieval queries with authority-provenance labels emitted;
  classify whether authority-ordering matches human-judged authority
  for each query. Feeds framework calibration (post-P4).
- **R4.7 (P3-new) — BACKLOG (gated on T21) — Artifact lifecycle-
  transition observation.** After post-arc T21 state-machine lands,
  P4 observes N ≥ 10 lifecycle transitions; classify whether
  transitions match designed rules (draft → active from Chris
  ratification, active → canonical from xx99 aggregation, etc.).
- **R4.8 (P3-new) — BACKLOG (framework methodology) — Governance-
  dimension mixed-mode observation.** Observe SIGN cycles where
  governance-term over-load surfaced as a drift; classify whether P3
  §14 F4 disambiguation table would have prevented the drift.

### 19.2 P3 → xx99 (S2199 — canonical summary)

- **R99.1 (P3-new) — Canonical seam statement.** xx99 §5 consumes
  P3 §17.1 posture register + §18 owner-assignment matrix + §14 F1-F8
  design decisions to produce Group 2100 canonical seam statement:
  *"Rigby's RAG corpus IS a governed institutional knowledge layer
  substrate (spec-complete), pending post-arc T18-T25 execution."*
  Cross-arc F5 running tally at S2103 close: 1 pass / 5 DISPROVE / +1
  new DESIGN-COMPLETE-BUT-NOT-EXECUTED verdict (candidate xx99 §10
  meta-methodology observation).
- **R99.2 (P3-new) — Post-arc T-slot queue population.** xx99 §8
  consumes §15 P3 debt table + §19.3 execution items to build tiered
  T0/T1/T2/T3 queue.
- **R99.3 (P3-new) — 5-meaning governance disambiguation carry.** xx99
  §5 preserves F4 disambiguation table as canonical anti-drift
  substrate for future arcs invoking "governance" language.

### 19.3 P3 flags for post-arc T-slot execution

**Execution items enumerated per §15.1 debt table + §14 findings.**

**Two-track dependency structure (Q19 SIGN STRENGTHEN 2026-07-04):**
Prevents the impression that "everything blocks on T22 metadata
contract". T22 is a major enabler for enforcement/ranker correctness
but T13 dual-cascade resolution is INDEPENDENT — T13 determines the
canonical path that will produce contract fields consistently.

- **Track A (canonical path / production):** T13 dual-cascade
  resolution → path B wired + observed stable → then contract
  population instrumentation. T13 is Track A T0/Gate.
- **Track B (schema + enforcement):** T22 metadata contract → enables
  T21 lifecycle state-machine + T18 axis-scoring service + T19 rule
  engine + most governance automation. T22 is Track B T0/Gate.
- **Retrofill (T-D2100.11) is independent of both tracks** — gated
  by PROD probe (per Q13 fold), not by T22 landing.

**T-slot table (Depends-on column reflects two-track structure):**

| T-slot | Description | Owner (post-arc) | Depends on |
|--------|-------------|-------------------|-------------|
| T13 (S2102) | Dual-cascade F3 R3.5 execution | Rigby via extend | Chris D-verdict at S2103 close card (lean a or b) — **Track A T0/Gate** |
| T16 (S2102) | Chunker_id + chunker_version schema addition | Chief of Staff RECOMMEND + Chris ratifies | T22 metadata contract landing — **Track B** |
| T18 (S2103) | Axis-scoring service + ranker consumer | Chief of Staff RECOMMEND | T22 metadata contract landing — **Track B** |
| T19 (S2103) | Conflict-resolution rule engine | Chief of Staff RECOMMEND | T18 co-lands — **Track B** |
| T20 (S2103) | Owner-assignment PR (extend `core/employees/jobs.py`) | Claude Code | Chris ratifies §18 recommendations — **independent** |
| T21 (S2103) | Artifact lifecycle state machine | Rigby via extend + Chief of Staff schema RECOMMEND | T22 metadata contract landing — **Track B** |
| T22 (S2103) | D2100.9 metadata contract validation | Chief of Staff RECOMMEND schema + Rigby via extend enforcement | Chris ratifies contract shape — **Track B T0/Gate** |
| T23 (S2103) | `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` publish | Claude Code | R3.4 — **independent** |
| T24 (S2103) | `docs/topics/retrieval-authority-framework.md` publish | Claude Code | R3.1 pattern — **independent** |
| T25 (S2103) | `docs/topics/docs-ingestion-cascade.md` publish (R3.1) | Claude Code | R3.1 — **independent** |
| T-D2100.11 | F2 retrofill (choice b: forward-fix + retrofill mgmt cmd) | Rigby via extend (write-site) | Chris D-verdict at close card + PROD probe pass — **independent of T22** |
| T-F6 | Backfill enum retirement (recommended) OR activation | Rigby via extend | Chris ratifies recommendation — **independent** |

### 19.4 P3 flags for future non-Group-2100 arcs

- **Group 1700 (Observability) delegation** — F7 EventBus emission
  design + retrieval-query event emission surface. Post-arc execution
  routes to Group 1700's future consumer-surface arcs.
- **Documentation / Research Knowledge System (§3.15 future arc)** —
  R3.4 canonical governance doc could be part of a broader research-
  knowledge-system arc (cross-arc concern).
- **Group 2000+ retroactive fold-in** — F7 EventBus emission event
  contracts for `docs_cascade.*` + `retrieval.*` are candidates for
  Group 2000+ close-out fold-in if any Group 2000+ close-out lands
  another round of event-contract additions.

### 19.5 P3-scoped follow-ups (must land pre-close if adopted)

None mandatory. All above route to P4 handoffs + post-arc T-slot
execution + non-Group-2100 arc flags. P3 status flips `draft` →
`active` on Chris ratification post-Rigby SIGN cycle 1.

---

## 20. Appendix

### 20.1 Verifier-loop evidence log

Executed 2026-07-04 at HEAD `51923cc9`. All queries LOCAL DB or
filesystem unless otherwise noted.

**U1 discharge — `Document.source='api'` upstream write-site trace:**

- `sync_docs_index_to_documents.py:328-340` — verified
  `Document.objects.create(...)` call passes `source=ContentSource.
  IMPORTED` on every docs-index sync.
- `content/models.py:93 class ContentSource(models.TextChoices)`
  line 97: `IMPORTED = 'imported', 'Imported from External System'`.
- `content/embeddings.py:45-63` — `_derive_source_type()` branch 4:
  `document.source in ('api', 'imported')` → `'api'`.
- **Root-cause confirmed:** every docs-cascade-created Document has
  `source='imported'`; every `DocumentEmbedding` for such Documents
  gets `source_type='api'` from branch 4. F5-partial (S2102) now
  discharges to F5-FULL.

**R2.9 discharge — `content/rag_integration.py` 4th chunker suspicion:**

- File does NOT exist at `content/rag_integration.py`.
- Correct file is `core/rag_integration.py` (verified via `find`).
- Grep for chunker functions (`chunk_text` / `chunk_content` /
  `def chunk` / `TextSplitter`) in `core/rag_integration.py` — no
  matches. File uses `chunk.chunk_text` as attribute access on
  `DocumentEmbedding` for decryption at `core/rag_integration.py:177-181`.
- **No 4th chunker exists.** P2 §7.3 three-chunker regime map is
  complete.

**Employee OS baseline — `DOCUMENTATION_MANAGER` verified:**

- `core/employees/jobs.py:187-382` — `DOCUMENTATION_MANAGER` job
  contract intact.
- Existing authority set (line 237-250) includes
  `run_docs_cascade_commands`, `run_drift_observation`,
  `create_escalation_deliverable`, `certify_mission_run`.
- Existing PROHIBITED (line 246-249): `modify_docs_files`,
  `open_pull_request`, `delete_document_rows`,
  `delete_document_embedding_rows`.
- P3 §18.3 extensions ADDITIVE to authority + responsibilities —
  no PROHIBITED conflicts.

**Governance-term 5-meaning drift probe:**

- Grep for "governance discipline / governance policy / governance
  ownership / governance enforcement" across `docs/` returned 30 files
  (see grep output).
- Cross-scan showed governance term used in scope-consistent ways
  across research arcs (Group 1900 authority-enforcement uses
  "governance" for policy + enforcement dimensions primarily; Group
  2100 uses for full 5-dim). No conflicting semantic drift observed
  — P3's disambiguation table is anticipatory, not retroactive.

**S1904 §17.1 posture-register pattern verified:**

- Read `docs/research/domains/authority_enforcement/1904_authority_
  enforcement_cat_f_adjacent_separation_boundaries_child_audit.md`
  lines 643-668.
- Pattern: master posture register with per-plane columns for
  ownership-vs-delegated-vs-shared decisions + posture verdict
  (PERMEABLE-BROKEN / STRUCTURAL-DROP / CLEAN / STABLE / CANONICAL).
- P3 §17.1 adapts to per-axis columns (framework spec-shape) +
  same posture-verdict vocabulary.

### 20.2 Files inspected

- `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md`
  (§5.3, §7, §8 read in full)
- `docs/research/domains/rag_document_loading/2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md`
  (§19.2, §20.2, §20.3 read in full)
- `docs/research/domains/rag_document_loading/2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md`
  (§14, §15, §17, §18, §19, §20.4 read in full)
- `docs/research/domains/authority_enforcement/1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md`
  (§17.1 posture register format sampled)
- `core/employees/jobs.py:187-382` (DOCUMENTATION_MANAGER contract)
- `core/rag_integration.py` (no 4th chunker verified)
- `core/management/commands/sync_docs_index_to_documents.py:328-340`
  (U1 write-site verified)
- `content/embeddings.py:45-63` (_derive_source_type acquitted)
- `content/models.py:93-112` (ContentSource enum verified)

### 20.3 Docs inspected

- `docs/DOC_LIFECYCLE.md` — §2c inventory-wins-on-conflict rule
  cross-referenced
- `docs/PLATFORM_INVENTORY.md` — narrative anchor pass
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — anti-duplication + owner-
  assignment discipline
- MEMORY.md cascade rules (`feedback_docs_pipeline_4_step_cascade`,
  `feedback_docs_cascade_at_every_close`,
  `feedback_cascade_pr_must_include_embed_step`) — will be replaced
  by R3.4 canonical doc

### 20.4 Unresolved unknowns

Per playbook §12 UNKNOWN honesty convention. P3 design-preparation
shape typically has fewer runtime-unknowns than audit shape; §20.4
captures design-choice unknowns.

- **U1 (S2103-new)** — F3 lean choice (a vs b). Chris D-verdict at
  close card resolves. Post-arc execution depends on choice.
- **U2 (S2103-new)** — D2100.11 F2 retrofill choice (a vs b). Chris
  D-verdict at close card resolves. P3 recommends (b) forward-fix +
  retrofill.
- **U3 (S2103-new)** — F6 backfill enum-retirement vs activation
  choice. Chris ratifies at close card. P3 recommends (a) retire enum.
- **U4 (S2103-new)** — Owner-assignment ratification. Chris ratifies
  §18 matrix via post-arc `core/employees/jobs.py` PR review.
- **U5 (S2103-new) — RESOLVED (Q20 SIGN STRENGTHEN 2026-07-04):**
  Chief of Staff schema-contract authority level = RECOMMEND-only.
  §18.4 Q10 SIGN STRENGTHEN fold ratified RECOMMEND-only with bounded-
  EXECUTE tuning-knob deferred as future autonomy upgrade. Design
  choice is closed; no unknown remains at authority-level.
- **U5-replacement (S2103-new)** — **Autonomy-upgrade telemetry
  unknown.** What telemetry will decide when bounded-EXECUTE (for
  non-breaking tuning knobs like weight/threshold changes) is safe to
  activate? Candidate metrics: N observation cycles with
  human-approved recommendations, false-positive rate on auto-reverts,
  regression detection latency. Design TBD at future autonomy-upgrade
  arc — not scoped to Group 2100.
- **U6 (inherited from S2102)** — LOCAL↔PROD comparability meta-
  unknown. P3 governance decisions that depend on PROD-specific
  observations (retrofill scope, event-emission volume, etc.) are
  gated on PROD validation post-arc.

### 20.5 Conflicts between sources

- **P3 §14 F6 recommendation vs S2102 §15.4 disposition rule.** S2102
  §15.4 said "P3 decides schedule vs CI-lint" for
  `build_docs_provenance`. P3 recommends a THIRD option — cascade-
  tail step (Rigby's Path B). This is NOT a conflict; P3 introduces a
  new option not previously enumerated. **Resolution:** the third
  option is preferred; cascade-tail placement is the recommended
  disposition.
- **Parent §5.3 W3 "framework not ranking" vs D2100.8 wording "adopt
  8-axis framework as platform default retrieval-trust rubric".**
  Parent §5.3 says "NOT a fixed ranking"; D2100.8 says "platform
  default retrieval-trust rubric". **Resolution:** not conflicting.
  D2100.8's "rubric" is the framework itself; framework is the
  default rubric that per-query constructs orderings. Rubric = tool;
  ordering = per-query output.
- **P3 §18 recommendation for `DocumentEmbedding` schema owner (Chief
  of Staff) vs S2102 §18.1 explicit UNASSIGNED entry.** S2102 left
  schema owner UNASSIGNED. P3 recommends Chief of Staff. **Resolution:**
  not conflicting; S2102's UNASSIGNED entry is exactly what P3 R3.3
  discharges.

### 20.6 Verifier-loop corrections (Rigby SIGN fold notes)

Populated post Rigby SIGN cycle 1 completion.

### 20.7 Naming conventions used

- **F1..F8** — S2103 design decisions.
- **T18..T25** — S2103 debt-table additions (extending S2102 T1-T17).
- **T-D2100.11 / T-F6** — Chris-D-verdict-candidate + backlog
  execution items.
- **R4.x** — P3 → P4 handoffs.
- **R99.x** — P3 → xx99 handoffs.
- **U1..U6** — Design-choice unknowns.
- **D2100.x** — Chris-ratified D-verdicts from parent §8.
- **KD-1..KD-7** — S2101 knowledge-debt taxonomy (re-observed at §15.3).

### 20.8 Companion anchors touched

- `docs/PLATFORM_INVENTORY.md` — runtime counts baseline (not
  modified)
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor (not modified; §11.3
  flags for future update)
- `docs/DOC_LIFECYCLE.md` — §2c inventory-wins policy respected
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — anti-duplication + primitive-
  reuse discipline followed
- `docs/KNOWLEDGE_PIPELINE.md` — flow-map companion (not modified)
- `core/employees/jobs.py:187 DOCUMENTATION_MANAGER` — extensions
  designed at §18.3 (not applied)
- `core/employees/jobs.py CHIEF_OF_STAFF` — extensions designed at
  §18.4 (not applied)

### 20.9 Provenance chain

- **HEAD at draft:** `51923cc9`
- **Arc pin:** `pa-18b095bb7c4740be` (preserved through S2103)
- **Prior arc close:** S2102 P2 Ingestion / Chunking / Embedding
  Pipeline Audit closed 2026-07-04
- **Parent scoping:** S2100 arc open 2026-07-04 (Chris "agree all" on
  6-item D-verdict card + 10 D2100.x ratifications)
- **Preceding children:** S2101 P1 (2026-07-04) + S2102 P2 (2026-07-04)
- **Playbook version:** §11.2 20-section child-audit template
  (ELEVENTH-consecutive application after S1301, S1401, S1501, S1601,
  S1701, S1801, S1901, S2001, S2101, S2102)

### 20.10 Batch-discipline attestation (per Q4b SIGN fold pattern)

Per Q4b SIGN batch-discipline attestation at S2099 close + parent §5.5
handoff: S2103 P3 lands as a single atomic child-audit doc PR. NO
bundled anchor updates in this PR (queued as separate follow-up per
S2099 residual queue).

Scope of THIS PR:
- Add `2103_rag_document_loading_retrieval_authority_framework_
  corpus_governance_design.md` (child audit)
- Update `docs/research/OPEN_ARCS.md` Group 2100 In-progress row (S2103
  landed)
- Update `docs/research/ARCHITECTURE_INDEX.md` v73 → v74 with §1.77
  S2103 registration
- Update `00-START-NEXT-SESSION.md` for S2104 P4 open
- Add handoff doc `docs/handoffs/SESSION_2103_RAG_DOCUMENT_LOADING_
  RETRIEVAL_AUTHORITY_FRAMEWORK_CORPUS_GOVERNANCE_DESIGN.md`

Explicitly OUT-OF-SCOPE for this PR (queued for follow-up):
- S2099 §7 anchor-update batch (still queued per S2102 handoff)
- Post-arc T18-T25 execution PRs
- `core/employees/jobs.py` extensions
- Schema migration for `chunker_id` / `overlap_size_actual` / etc.

### 20.11 Rigby SIGN cycle 1 routing plan (per playbook §15)

**Cycle 1 target: 4 batches × 5 findings/questions = 20 Q's.**

- **Batch 1 (Q1-Q5)** — Framework foundation + §1 executive summary +
  §7.1 query-resolution flow diagram + §14 F1 8-axis framework
  population + §14 F2 conflict-resolution rule population + §14 F4
  governance-term disambiguation table.
- **Batch 2 (Q6-Q10)** — Contract + Ownership + §14 F5 D2100.9
  metadata contract ratification (10 core-required + doc-type profile
  + derivable + aspirational) + §14 F6 owner assignments + §18.1
  ownership matrix + §18.3 Rigby extension + §18.4 Chief of Staff
  extension.
- **Batch 3 (Q11-Q15)** — Lifecycle + Cascade decisions + §14 F7
  5-state lifecycle model + §14 F3 dual-cascade recommendation + §14
  F8 D2100.11 F2 retrofill Chris D-verdict + §15.5 F6 backfill
  activation criteria + §15.6 F1 chunker consolidation + §15.7 R3.8
  provenance-index scheduling.
- **Batch 4 (Q16-Q20)** — Posture + Handoffs + Unknowns + §17.1
  per-axis posture register + §17.2 per-dimension posture register +
  §19.1 P3 → P4 handoffs + §19.3 T-slot queue + §20.4 unknowns U1-U6
  + §20.5 conflicts between sources.

**Batch discipline per `feedback_rigby_sign_worker_instability_
recovery`:** 5 findings per batch prevents worker-instability on
governance-design shape. Governance-design historically yields MORE
folds than descriptive-audit shape (S2003 P3 governance-design =
12 folds in 4 batches); plan for STRENGTHEN-heavy cycle 1 with
fold-landing pre-commit.

### 20.12 §10 meta-methodology note (per playbook §11.3 template)

Reserved for xx99 §10 meta-methodology observation. P3 design-
preparation shape produces:
- Cross-arc §17.1 CONSOLIDATION-shape posture-register durability at
  5-arc running tally (candidate for playbook v3 §16 standardization).
- Framework-not-ranking codification (parent §5.3 W3 correction) as
  cross-arc reusable methodology for future design-preparation arcs.
- 5-meaning governance disambiguation table (F4) as reusable pattern
  for future arcs invoking "governance" language.

### 20.13 D-verdict compliance (§8 parent D-verdicts applied to P3)

| D-verdict | P3 compliance |
|-----------|----------------|
| D2100.1a — Group 2100 scope lock | Complied — arc scope respected |
| D2100.1b — Framing adoption | Complied — Reality→Research→Knowledge→Behavior + Knowledge Loop framing used |
| D2100.2 — 4-child taxonomy | Complied — P3 = C-child per §3.4 |
| D2100.3 — Fresh arc pin | Complied — `pa-18b095bb7c4740be` preserved |
| D2100.4 — SIGN cycle 1 clean | PENDING — will be attested post-SIGN |
| D2100.5 — Design-preparation authority only | Complied — no implementation ships |
| D2100.6 — Central lens question locked | Complied — P3 contributes designed substrate; P4 delivers observational evidence |
| D2100.7 — RAG-freshness-bounds-SIGN hypothesis | Complied — P4 discharges per Q15 SIGN fold |
| D2100.8 — 8-axis framework adoption | Complied — §14 F1 populates |
| D2100.9 — Hybrid metadata contract | Complied — §14 F5 ratifies with P2 additions |
| D2100.10 — Corpus Health Score deferral | Complied — P4 close per Chris "agree all" |
| D2100.11 (candidate) — F2 retrofill | PENDING Chris ratification at S2103 close card |

### 20.14 Close checklist (per Research OS §14 completion contract)

- [ ] Rigby SIGN cycle 1 CLEAN with all STRENGTHEN folds landed
      pre-commit
- [ ] Chris ratifies D2100.11 F2 retrofill choice at close card
- [ ] Chris ratifies F3 dual-cascade lean (a or b) at close card
- [ ] Chris ratifies F6 backfill enum disposition at close card
- [ ] Chris ratifies §18 owner-assignment matrix at close card
- [ ] Status flip `draft` → `active`
- [ ] Commit + PR opened + green CI + merged
- [ ] Full 4-step docs cascade run (build_docs_index +
      build_rag_corpus + sync_docs_index_to_documents +
      embed_documents --all-unembedded)
- [ ] `build_docs_provenance` executed post-merge
- [ ] Handoff written at
      `docs/handoffs/SESSION_2103_RAG_DOCUMENT_LOADING_RETRIEVAL_
      AUTHORITY_FRAMEWORK_CORPUS_GOVERNANCE_DESIGN.md`
- [ ] `00-START-NEXT-SESSION.md` updated for S2104 P4
- [ ] `ARCHITECTURE_INDEX.md` v73 → v74 with §1.77 registration
- [ ] `OPEN_ARCS.md` Group 2100 In-progress row updated

---

**End of S2103 P3 design-preparation doc. Status `active` post-Rigby
SIGN cycle 1 CLEAN + Chris "agree all" ratification 2026-07-04 with
picks 7=b (fold Path A into Path B) + 8=b (forward-fix + retrofill
after PROD probe) + 9=a (de-scope backfill enum) + 10=yes (proceed
with commit + PR + cascade).**

**Chris ratified 10 items 2026-07-04:**
1. §14 F1 seven-evidence-axes + one-meta-rule framework populated per D2100.8
2. §14 F2 three-part conflict-resolution rule populated per Q7 SIGN fold
3. §14 F4 five-meaning governance disambiguation table populated per parent W5 critique
4. §14 F5 D2100.9 hybrid metadata contract (9 core-required + 2 core-available + 3 profiles + 4 derivable + 5 aspirational)
5. §14 F6 + §18 owner assignments two-employee shape (Rigby EXECUTE + Chief of Staff RECOMMEND); NO new AIEmployee handles
6. §14 F7 five-state lifecycle model with Q11 SIGN superseded-DE-RANKED-not-EXCLUDED refinement
7. §14 F3 dual-cascade — pick (b) fold Path A into Path B with 3-step retirement sequence per Q8/Q12 SIGN folds
8. §14 F8 D2100.11 F2 retrofill — pick (b) forward-fix + retrofill AFTER PROD probe per Q13 SIGN fold
9. §15.5 R3.6 backfill activation — pick (a) de-scope + retire enum value per Q14 SIGN fold
10. Draft→active + commit + PR + full 4-step docs cascade + build_docs_provenance post-merge
