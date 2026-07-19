# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2828 CLOSED (2026-07-19; picks up as S2829) — **PATTERN D LITERAL-FILENAME INJECTION SHIPPED; DISCOVERY-LAYER PATTERN B/C/D ALL COMPLETE**

**Refreshed 2026-07-19 (SESSION 2828 CLOSED — Chris opened with "Please begin" after S2827 close. Executed Pattern D LITERAL-FILENAME candidate injection design + Rigby joint SIGN (2 cycles) + Chris D-verdict (7 D-questions) + implementation + per-gate sweep + measurement + atomic PR + close cascade. Rigby joint SIGN cycle 1: 5 questions, 10 tool_runs (`repo_tool.read_file` ×2 on `core/rag_integration.py` + design doc; `kb_tool.semantic_search` ×6; `kb_tool.documents` ×1; `search_docs` ×1). Verdicts: Q1 AGREE-nuanced, Q2 AGREE Strategy A + small Strategy C, **Q3 DISAGREE with flat bonus → prefer per-regex tiers (Strategy 3-B)**, **Q4 DISAGREE with force-rank-1 → keep bounded discipline**, Q5(c) proposed zoom-out fold. Reconciliation cycle 2: R1-R5 applied to §0/§4.1/§4.2/§4.3/§5/§7; Rigby explicit AGREE after full 658-line doc re-read. Joint Claude+Rigby agreement reached BEFORE Chris routing per S2753 discipline. Chris D-Q1..D-Q7 all YES with refinements: D-Q1 per-regex bonus sweep + per-gate ceilings (P0/P2=0.35, P1=0.20, P3=0.10) ratified with "measurements choose bonus" directive; D-Q2 Strategy A curated map + Strategy C log-only miss (rejected Strategy B); D-Q3 retrieval-integrity constitutional (bounded per-gate, not force-rank-1); D-Q4 Q28 no-perturb tolerance; D-Q5 CLAUDE.md literal in scope; D-Q6 Rigby fold persisted `same_pr_mitigatable`; D-Q7 no shared "pointer-intent registry" refactor combined with Pattern D. Executed atomically as PR #3269 (SHA `d26fe5311`). Per-gate sweep selected values: **P0=0.07 (headroom +0.28), P1=0.09 (+0.11), P2=0.32 (+0.03 — tightest), P3=0.03**. Post-implementation Phase-0.5 re-measurement: **10/18 → 12/18 = 66.7% strict top-1** (matches design projection exactly). Q20 + Q24 both converted; Q28 preserved naturally via MISS path. Pattern B/C smoke: no regression. Pytest: 95/95 passing (61 Pattern D + 34 Pattern C regression). SEVENTY-THIRD close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first empirical validation of Chris D-Q1 discipline generalized from single-scalar to per-regex bonus tiers with per-gate ceilings; first empirical validation of Rigby SIGN Q3 DISAGREE catching design tension pre-Chris (v1 flat-bonus → v2 per-regex tiers); first arc where 3-instance codification threshold met (Pattern B/C/D share skeleton); first arc with Rigby-proposed zoom-out fold whose mitigation lands in SAME PR (not deferred).**

**S2828 ship (1 atomic PR):**

| Focus | PR | SHA | Merged to | Files |
|---|---|---|---|---|
| Pattern D LITERAL-FILENAME candidate injection | **#3269** | `d26fe5311` | main | 3 files: 1445 insertions / 14 deletions |

**Handoff:** `docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md`
**Design + measurement evidence:** `docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md` §7.5
**Architectural boundary summary:** `docs/KNOWLEDGE_PIPELINE.md` §Pattern D Measured Boundary Summary (S2828 addendum, LOAD-BEARING)

**Arc state at S2828 close:**
- **Discovery-layer arc:** Pattern B (COUNT) MERGED at S2826. Metadata drift REPAIRED at S2826. Pattern C (SELF_REFERENCE) MERGED at S2827. Corpus label ground-truth repair MERGED at S2827. **Pattern D (LITERAL-FILENAME) MERGED at S2828.** Post-Pattern-D Phase-0.5 baseline: **12/18 = 66.7% strict top-1** (from 10/18 = 55.6% at S2827). All literal-filename + intent-based policy classes shipped. Shared "pointer-intent registry" primitive extraction is a candidate arc per Chris D-Q3 forward-carry (3-instance threshold now met).
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817, unchanged).

---

## S2829 CANDIDATES

### ⭐ Recommended default direction — Shared "pointer-intent registry" primitive extraction (post-Pattern-D per Chris D-Q3)

**Rationale:** Chris D-Q3 forward-carry from S2827 said "shared 'pointer-intent registry' primitive as post-Pattern-D codification candidate; NOT built in S2827." Chris D-Q7 at S2828 reaffirmed: "Do not combine the refactor with Pattern D implementation. Only then evaluate the shared pointer-intent registry as its own architectural arc." That gate is now open. Pattern B/C/D all share the same skeleton (gate → anchor resolve → injection → bounded bonus → diagnostic contract → drift WARN); 3-instance threshold per §14.2 is met. Extraction candidate would consolidate the compositional pattern into a reusable primitive without changing any measured behavior.

**Concrete first steps at S2829 open:**
1. Read S2828 handoff §3-§5 (Rigby SIGN + Chris D-verdicts + measurement evidence)
2. Read `docs/KNOWLEDGE_PIPELINE.md` §Pattern D Measured Boundary Summary + §Pattern C Measured Boundary Summary + §retrieval-failure-diagnosis-order (all three LOAD-BEARING architectural anchors)
3. Read `core/rag_integration.py` Pattern B (`:60-105`) + Pattern C (`:106-255`) + Pattern D (`:258-410`) sections side-by-side to characterize the shared skeleton
4. Draft "pointer-intent registry" design doc covering:
   - **Shape survey** — what's identical across B/C/D (gate detection, anchor resolution, injection, additive bonus composition, drift WARN, diagnostic dict fields)
   - **Shape divergence** — what's genuinely per-mechanism (regex vocabulary, per-regex vs global bonus, curated map vs single-anchor list, gate-precedence)
   - **Primitive shape proposal** — dataclass/protocol for `PointerIntentMechanism` covering the identical parts; each of B/C/D becomes a registered mechanism
   - **Zero-behavior-change guarantee** — refactor MUST preserve every measured behavior. Design includes pytest strategy: run existing Pattern B/C/D tests as-is against refactored code (no test changes); Phase-0.5 measurement re-run must return 12/18 = 66.7% unchanged
   - **Migration sequence** — introduce primitive as a parallel structure; port B → measure; port C → measure; port D → measure; remove old paths only when all three ports proven identical
5. Route registry design to Rigby joint SIGN (mirror S2828 5-question structure; anti-rubber-stamp `tool_runs` check)
6. Chris D-verdict on design (whether to build in S2829 or defer to later arc)
7. Only proceed to implementation on Chris ratification

**⚠ IMPORTANT** — Chris D-Q7 was explicit: "Only then evaluate the shared pointer-intent registry as its own architectural arc." "Evaluate" ≠ "build automatically." Route as a design proposal first; do NOT assume Chris wants the refactor built next-immediately.

### Available if Chris pivots

- **DISCOVERY policy-class mechanism** — 2 remaining rows (Q10 canon/INDEX target, Q11 DISCOVERY intent) — Chris D5 distinct-mechanism class
- **CONCEPTUAL / PROCEDURAL semantic-general future arc** — 4 rows (Q9, Q12, Q13, Q18) — the last remaining Phase-0.5 misses; requires semantic-general mechanism (LLM-lite intent classifier or narrow-topic classifiers)
- **§2.2 methodology revision** — Chris D6 said wait until all pattern mechanisms measured; **Pattern B/C/D data now available** — can start §2.2 numeric bands per Chris D6 sequence
- **13 out-of-index Document rows investigation** — Chris D6 recorded as separate post-Phase-0.5 follow-up
- **Playbook v0.9 amendment authoring** — 10/10 triggers on OP3; sync-update-path-completeness discipline (S2826 §5.2 fold, 3-trigger shape S1234/S1235/S2826, codification-ready)
- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability

**Recommended default:** Shared "pointer-intent registry" primitive design + Rigby SIGN (per Chris D-Q3/D-Q7 sequencing).

---

## SESSION PIN — S2828 RETIRED (fresh mint required at S2829 open)

**Pin history (S2828):**

- `pa-58fa25861f814309` (label `s2828-pattern-d-literal-filename-injection`) minted at S2828 open; **retired at S2828 close (`force=true`, fifty-ninth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2829 first-action fresh mint.

**S2829 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2828 handoff §3 (Rigby SIGN) + §4 (Chris D-verdicts) + §5 (measurement evidence) + §8 (lessons)
# Read docs/KNOWLEDGE_PIPELINE.md §Pattern D + §Pattern C Measured Boundary Summaries + §retrieval-failure-diagnosis-order
# Read core/rag_integration.py Pattern B/C/D sections side-by-side

# Sanity checks
brew services list | grep postgres

# Verify Pattern B/C/D all working post-recycle
python manage.py shell -c "from core.rag_integration import search_embeddings; \
  c = search_embeddings(query='where do I start', limit=1, similarity_threshold=0.4); \
  print('Pattern C:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='How many spiders', limit=1, similarity_threshold=0.4); \
  print('Pattern B:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='PLATFORM_INVENTORY', limit=1, similarity_threshold=0.4); \
  print('Pattern D:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name'))"
# expect Pattern C = 00-START-NEXT-SESSION.md self_reference; Pattern B = docs/PLATFORM_INVENTORY.md count;
# expect Pattern D = docs/PLATFORM_INVENTORY.md literal_filename

# Verify metadata layer still healthy
python manage.py backfill_document_status_from_docs_index --dry-run 2>&1 | tail -8
# expect Total mismatches: 0

python manage.py session_lifecycle open --label s2829-pointer-intent-registry-primitive-design
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2828 lessons to carry (also in handoff §8):**

1. **Chris D-Q1 discipline generalizes from single-scalar to per-regex bonus tiers.** Scalar-scope from S2827 (single +0.23) extended cleanly to per-gate-scope in S2828 (P0=0.07/P1=0.09/P2=0.32/P3=0.03) with per-gate ceilings. Future intent-gated mechanisms with heterogeneous signal strengths should adopt per-gate discipline.
2. **The 3-instance codification threshold is met** — Pattern B + C + D share the same skeleton (gate → anchor resolve → injection → bounded bonus → diagnostic contract → drift WARN). Shared "pointer-intent registry" primitive extraction is now a candidate arc per Chris D-Q3.
3. **P2's +0.03 headroom below ceiling is the tightest observed.** 00-START-NEXT-SESSION's raw anchor sim (0.3979) is unusually low — the doc's embeddings are dissimilar from queries that literally name it. Future canonical targets with similar characteristics will need similar tightness.
4. **Strategy C log-only miss path proved cleanly.** Gate-fires-without-curated-anchor is safe: natural retrieval unchanged, INFO log for future map graduation. Do NOT let Strategy C drift toward runtime resolution to non-canonical Documents.
5. **Q28 as regression control is architecturally load-bearing.** A naturally-winning literal-filename query that Pattern D must not perturb is a permanent invariant. Pytest `test_gate_fires_with_no_anchor_returns_miss_record` guards it.
6. **Whole-string `^...$` invariant is LOAD-BEARING and MUST NEVER be relaxed silently.** Pytest `test_whole_string_holds_across_natural_language` guards this. Substring-relaxation would immediately break disjointness vs Pattern B/C multi-word patterns.
7. **DO NOT relax `include_superseded=False` default** (Chris D6 retrieval integrity rule; unchanged).
8. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3 first cycle: "Retrieval must prove retrieval."
9. **DO NOT collapse Pattern B/C/D into a generic canonical gate WITHOUT explicit Chris ratification.** Chris D5 mandates distinct mechanisms + measurements per class. The registry primitive extraction MUST preserve every measured behavior — refactor with zero behavior change or don't refactor.

---

## Twin-pointer card

📁 **Repo — S2828 artifacts:**

- **Pattern D implementation:** `core/rag_integration.py` §S2828 Pattern D (patterns/anchors/gate/fetch at :258-410; composition + bonus in `search_embeddings`; drift WARN around :796-820)
- **Design + measurement evidence:** `docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md` (§7.5 full evidence)
- **Pattern D measured boundary summary:** `docs/KNOWLEDGE_PIPELINE.md` §Pattern D Measured Boundary Summary (S2828 addendum)
- **Handoff:** `docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md`
- **Pytest coverage:** `tests/unit/test_s2828_pattern_d_literal_filename_gate.py` (61 tests)
- **Merge SHA:** `d26fe5311` · **PR:** #3269

🖥️ **Workspace UI — S2828 twin-pointer workspace deliverable:**

- **`ceca32ff-a5b6-4fa0-8ada-20e436117b98`** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) — type `ratification_record`, category `governance`, status `ready`, pinned, `diagnostic_status=None`. ORM-direct create bypasses pa_deliverables_tool diagnostic-flag bug.

---

## Current repository state (S2828 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `d26fe5311` (S2828 PR #3269 merge) + close-cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged; v0.9-candidate sync-update-path-completeness discipline 3/2 triggers ready per S2826 §5.2 fold) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Discovery-layer arc state** | **Pattern B + Pattern C + Pattern D ALL SHIPPED. Metadata drift repaired. Corpus label repaired. Post-Pattern-D Phase-0.5: 12/18 = 66.7% strict top-1. All literal-filename + intent-based policy classes complete. Shared "pointer-intent registry" primitive extraction candidate open per Chris D-Q3.** |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2829 recommended lean | Shared "pointer-intent registry" primitive extraction design + Rigby SIGN (per Chris D-Q3/D-Q7) |
| Session pin | `pa-58fa25861f814309` (retired at S2828 close, force=true, fifty-ninth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2829 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +2 at S2828 (post-#3269 merge + close-cascade PR merge) |
| Metadata layer health | ✅ 0 mismatches vs docs/_index.json (post-S2826, unchanged) |
| Next move | S2829 opens shared "pointer-intent registry" primitive design. Fresh pin `s2829-pointer-intent-registry-primitive-design`. |

---

## Recommended session-open protocol (S2829, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2828 handoff §3 (Rigby SIGN) + §4 (Chris D-verdicts D-Q1..D-Q7) + §5 (measurement evidence) + §8 (lessons)
4. Read `docs/KNOWLEDGE_PIPELINE.md` §Pattern D + §Pattern C Measured Boundary Summaries + §retrieval-failure-diagnosis-order (all three LOAD-BEARING architectural anchors)
5. Read `core/rag_integration.py` Pattern B + Pattern C + Pattern D sections side-by-side to characterize shared skeleton
6. Sanity checks (brew postgres + Pattern B/C/D smoke tests + backfill dry-run = 0 mismatches)
7. `git log --oneline -6` — should show S2828 close cascade + #3269 + S2827 close cascade + #3267 + S2826 close cascade
8. Mint fresh pin scoped `s2829-pointer-intent-registry-primitive-design`
9. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
10. **REGISTRY PRIMITIVE DESIGN AUTHORED UNDER CHRIS D-Q3 / D-Q7 CONSTRAINTS** — zero-behavior-change guarantee; migration sequence; per-mechanism registration; Chris-ratification-first
11. **DO NOT relax include_superseded=False default** — Chris D6 retrieval integrity rule (unchanged)
12. **DO NOT proceed to implementation without explicit Chris D-verdict** — Chris D-Q7 said "evaluate as its own architectural arc" — build design, route to SIGN, present to Chris, then implement only on ratification
13. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3 first cycle: "Retrieval must prove retrieval."
14. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred as separate post-Phase-0.5 investigation
15. **DO NOT auto-adopt semantic default flips** (per S2821)
16. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
17. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
18. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
19. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest `test_whole_string_holds_across_natural_language` guards; substring-relaxation requires re-SIGN + re-D-verdict
20. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest `test_selected_bonuses_do_not_exceed_ceilings` guards; raising a ceiling is a Chris D-Q1 violation
21. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2: post-correction is the authoritative baseline; NOT unchanged-corpus)

---

## Reference documents

Ordered by frequency of use at S2829:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md`](docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md) — **S2828 handoff (current)**
3. [`docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md) — full design + §7.5 measurement evidence (registry primitive design reference)
4. [`docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md) — Pattern C design + §7.5 measurement evidence
5. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B + C + D side-by-side reference for registry-primitive extraction (Pattern B :60-105; Pattern C :106-255; Pattern D :258-410)
6. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — §retrieval-failure-diagnosis-order (S2826) + §Pattern C Measured Boundary Summary (S2827) + §Pattern D Measured Boundary Summary (S2828) — LOAD-BEARING architectural anchors
7. [`docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md`](docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md) — S2827 handoff (predecessor)
8. [`docs/research/discovery_layer/PHASE_0_5/corpus.json`](docs/research/discovery_layer/PHASE_0_5/corpus.json) — 20 P1 rows post-corpus-correction (authoritative baseline; preserve for registry-refactor re-measurement)
9. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
10. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — Phase-0.5 arc row (updated at S2828 close)
11. [`tests/unit/test_s2828_pattern_d_literal_filename_gate.py`](tests/unit/test_s2828_pattern_d_literal_filename_gate.py) — 61-case pytest reference; must continue passing after any registry refactor
12. [`tests/unit/test_s2827_pattern_c_self_reference_gate.py`](tests/unit/test_s2827_pattern_c_self_reference_gate.py) — 34-case pytest regression reference
