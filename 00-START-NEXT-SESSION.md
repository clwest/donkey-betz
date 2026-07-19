# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2827 CLOSED (2026-07-19; picks up as S2828) — **PATTERN C SELF_REFERENCE INJECTION + CORPUS LABEL GROUND-TRUTH REPAIR SHIPPED**

**Refreshed 2026-07-19 (SESSION 2827 CLOSED — Chris opened with "Please proceed" after S2826 close. Executed Pattern C SELF_REFERENCE candidate injection design + Rigby joint SIGN + Chris D-verdict + implementation + measurement + atomic PR + close cascade. Rigby joint SIGN 5-question cycle: 4 DISAGREE + 1 AGREE-with-caveat → reconciled v2 with all refinements applied → joint Claude+Rigby agreement reached BEFORE Chris routing per S2753 discipline. Chris D-Q1..D-Q5 all YES with refinements: D-Q1 "smallest reliable adjustment" measured-bonus discipline (sweep 0.05..0.25 with per-value negative-control fire count; selected +0.23); D-Q2 corpus label ground-truth repair as same-PR fix (4 rows Q14/Q15/Q16/Q20 label-only surgical edit; not benchmark tuning); D-Q3 shared "pointer-intent registry" forward-carry for post-Pattern-D codification; D-Q4 literal-filename explicitly deferred to Pattern D; D-Q5 sequential arc order (Pattern C → close → Pattern D). Executed atomically as PR #3267 (SHA `47f3650d1`). Post-implementation Phase-0.5 re-measurement (post-corpus-correction; NOT unchanged-corpus per Chris D-Q2): **6/18 → 10/18 = 55.6% strict top-1** (matches design projection exactly). All 4 Pattern C conversions Q14/Q15/Q16/Q17 via injection + bounded bonus. Pattern B COUNT smoke: no regression. Pytest: 34/34 passing. SEVENTY-SECOND close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first empirical validation of Chris D-Q1 "smallest reliable adjustment" discipline via bonus sweep with per-value margins; first arc combining ratifiable engineering artifact + ground-truth benchmark-label repair in single atomic PR; first application of full "Rigby SIGN reconciliation → Chris D-verdict → implementation → measurement" sequence with 5-question mirror of S2826 shape.**

**S2827 ship (1 atomic PR):**

| Focus | PR | SHA | Merged to | Files |
|---|---|---|---|---|
| Pattern C SELF_REFERENCE candidate injection + corpus label repair | **#3267** | `47f3650d1` | main | 4 files: 1003 insertions / 27 deletions |

**Handoff:** `docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md`
**Design + measurement evidence:** `docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md` §7.5
**Architectural boundary summary:** `docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured Boundary Summary (S2827 addendum, LOAD-BEARING)

**Arc state at S2827 close:**
- **Discovery-layer arc:** Pattern B (COUNT) MERGED at S2826. Metadata drift REPAIRED at S2826. **Pattern C (SELF_REFERENCE) MERGED at S2827.** Corpus label ground-truth repair MERGED at S2827. Post-Pattern-C Phase-0.5 baseline: **10/18 = 55.6% strict top-1** (from 6/18 = 33.3% at S2826). Pattern D (literal-filename) QUEUED for S2828 per Chris D-Q4/D-Q5 sequence.
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817, unchanged).

---

## S2828 CANDIDATES

### ⭐ Recommended default direction — Pattern D LITERAL-FILENAME candidate injection

**Rationale:** S2827 shipped Pattern C converting 4 SELF_REFERENCE rows. 2 remaining literal-filename rows deferred per Chris D-Q4/D-Q5: **Q20** (`00-START-NEXT-SESSION` literal → SELF_REFERENCE class) + **Q24** (`PLATFORM_INVENTORY` literal → IDENTITY class). Both need literal-filename intent gate + anchor-by-name mechanism. Distinct mechanism per Chris D5.

**Concrete first steps at S2828 open:**
1. Read S2827 handoff §3-§5 (Rigby SIGN + Chris D-verdicts + measurement evidence)
2. Read `docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured Boundary Summary + §retrieval-failure-diagnosis-order (both LOAD-BEARING architectural references)
3. Read `core/rag_integration.py` Pattern C implementation (patterns/anchors at :106-217; composition at :377-395; drift WARN at :499-522) as design reference for Pattern D
4. Draft Pattern D design covering:
   - **LITERAL-FILENAME intent patterns** (canonicalize input: strip extension, lowercase, hyphen/underscore normalize; require capital-letter density OR file-extension suffix; do NOT overlap Pattern C semantic gate patterns)
   - **Literal-filename anchor mechanism** (query IS the filename → resolve via case-normalized Document.file_path match; separate from Pattern C's fixed anchor map)
   - **Bounded policy bonus** (same measured discipline per Chris D-Q1 — sweep values, pick smallest)
   - **Diagnostic contract** (mirror Pattern C: intent_gate_name='literal_filename', literal_filename_injected, matched_pattern_index)
   - **Negative controls** (must not fire on natural-language queries; must not overlap Pattern C's semantic gate)
   - **`[S2828_PATTERN_D_DRIFT]` WARN** (mirror Pattern C drift-re-mask discipline)
5. Route Pattern D design to Rigby joint SIGN (mirror S2827 5-question structure; anti-rubber-stamp `tool_runs` check)
6. Iterate refinements → joint Claude+Rigby agreement
7. Chris D-verdict on design
8. Implementation + measurement (target Q20 + Q24 conversion; expected 10/18 → 12/18 = 66.7%)
9. If Pattern B/C/D all 3 shipped → consider extracting shared "pointer-intent registry" primitive per Chris D-Q3 forward-carry (3-instance codification threshold per §14.2)

### Available if Chris pivots

- **DISCOVERY policy-class mechanism** — 2 remaining rows (Q10 canon/INDEX target, Q11 DISCOVERY intent) — Chris D5 distinct-mechanism class
- **CONCEPTUAL / PROCEDURAL semantic-general future arc** — 4 rows (Q9, Q12, Q13, Q18)
- **§2.2 methodology revision** — Chris D6 says wait until all pattern mechanisms measured; Pattern C data now available; can start §2.2 skeleton (non-numeric parts) per Chris D6 sequence
- **13 out-of-index Document rows investigation** — Chris D6 recorded as separate post-Phase-0.5 follow-up
- **Playbook v0.9 amendment authoring** — 10/10 triggers on OP3; sync-update-path-completeness discipline (S2826 §5.2 fold, 3-trigger shape S1234/S1235/S2826, codification-ready)
- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability

**Recommended default:** Pattern D LITERAL-FILENAME candidate injection design + Rigby SIGN.

---

## SESSION PIN — S2827 RETIRED (fresh mint required at S2828 open)

**Pin history (S2827):**

- `pa-fdf0a44a75b34e8f` (label `s2827-pattern-c-self-reference-injection`) minted at S2827 open; **retired at S2827 close (`force=true`, fifty-eighth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2828 first-action fresh mint.

**S2828 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2827 handoff §3 (Rigby SIGN) + §4 (Chris D-verdicts) + §5 (measurement evidence) + §8 (lessons)
# Read docs/KNOWLEDGE_PIPELINE.md §Pattern C Measured Boundary Summary + §retrieval-failure-diagnosis-order
# Read core/rag_integration.py Pattern C section as design reference

# Sanity checks
brew services list | grep postgres

# Verify Pattern C + Pattern B still working post-recycle
python manage.py shell -c "from core.rag_integration import search_embeddings; import json; \
  c = search_embeddings(query='where do I start', limit=1, similarity_threshold=0.4); \
  print('Pattern C:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='How many spiders', limit=1, similarity_threshold=0.4); \
  print('Pattern B:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name'))"
# expect Pattern C = 00-START-NEXT-SESSION.md self_reference; Pattern B = docs/PLATFORM_INVENTORY.md count

# Verify metadata layer still healthy
python manage.py backfill_document_status_from_docs_index --dry-run 2>&1 | tail -8
# expect Total mismatches: 0

python manage.py session_lifecycle open --label s2828-pattern-d-literal-filename-injection
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2827 lessons to carry (also in handoff §8):**

1. **Chris D-Q1 "smallest reliable adjustment" discipline generalizes.** For any bounded-policy-bonus mechanism: sweep values; find smallest that meets acceptance; record margins in design doc §7.x evidence table. Do not retune to reach a projected number — report the actual result.
2. **JSON mass-reformat trap.** `json.dump(indent=2)` on a file with mixed inline+indented formatting produces a large diff for a small semantic change. Prefer targeted string edits (`Edit` tool with `replace_all=True`) for label repairs.
3. **Corpus label defect discovery via ORM query.** Whenever a benchmark labels a target that doesn't resolve in the Document table, that's ground-truth-repair territory (Chris D-Q2), not mechanism-tuning territory.
4. **Rigby SIGN Q1 refinement was load-bearing.** Removing literal-filename patterns from Pattern C v1 preserved Chris D5 distinct-mechanism-per-class discipline that Chris later ratified in D-Q4.
5. **N4/N6 negative controls demonstrate retrieval integrity in action.** When the pointer-intent gate fires on a semantically ambiguous query and a topic-specific competitor legitimately outranks the anchor, Pattern C does NOT force-rank the anchor — Chris D3 invariant preserved.
6. **DO NOT relax `include_superseded=False` default** (Chris D6 retrieval integrity rule; unchanged).
7. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3 first cycle: "Retrieval must prove retrieval."
8. **DO NOT collapse Pattern C + D + future mechanisms into a generic gate** — Chris D5 mandates distinct mechanisms + measurements per class. Extract shared "pointer-intent registry" primitive AS A REFACTOR AFTER 3 shipped instances (post-Pattern-D per Chris D-Q3).

---

## Twin-pointer card

📁 **Repo — S2827 artifacts:**

- **Pattern C implementation:** `core/rag_integration.py:106-217` (patterns/anchors/gate/fetch) + `:377-395` (composition + bonus) + `:499-522` (drift WARN)
- **Corpus label repair:** `docs/research/discovery_layer/PHASE_0_5/corpus.json` (Q14/Q15/Q16/Q20 strict + loose; 8-line surgical edit)
- **Design + measurement evidence:** `docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md` §7.5
- **Pattern C measured boundary summary:** `docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured Boundary Summary (S2827 addendum)
- **Handoff:** `docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md`
- **Pytest coverage:** `tests/unit/test_s2827_pattern_c_self_reference_gate.py` (34 tests)
- **Merge SHA:** `47f3650d1` · **PR:** #3267

🖥️ **Workspace UI — S2827 twin-pointer workspace deliverable:**

- **`5d064c40-3f09-4487-94a4-993aac14cf12`** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) — type `ratification_record`, category `governance`, status `ready`, pinned. ORM-direct create bypasses pa_deliverables_tool diagnostic-flag bug.

---

## Current repository state (S2827 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `47f3650d1` (S2827 PR #3267 merge) + close-cascade cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged; v0.9-candidate sync-update-path-completeness discipline 3/2 triggers ready per S2826 §5.2 fold) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Discovery-layer arc state** | **Pattern B + Pattern C shipped. Metadata drift repaired. Corpus label repaired. Post-Pattern-C Phase-0.5: 10/18 = 55.6% strict top-1. Pattern D queued for S2828.** |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2828 recommended lean | Pattern D LITERAL-FILENAME candidate injection design + Rigby SIGN |
| Session pin | `pa-fdf0a44a75b34e8f` (retired at S2827 close, force=true, fifty-eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2828 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +2 at S2827 (post-#3267 merge + close-cascade PR merge) |
| Metadata layer health | ✅ 0 mismatches vs docs/_index.json (post-S2826, unchanged) |
| Next move | S2828 opens Pattern D LITERAL-FILENAME candidate injection design. Fresh pin `s2828-pattern-d-literal-filename-injection`. |

---

## Recommended session-open protocol (S2828, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2827 handoff §3 (Rigby SIGN) + §4 (Chris D-verdicts D-Q1..D-Q5) + §5 (measurement evidence) + §8 (lessons)
4. Read `docs/KNOWLEDGE_PIPELINE.md` §Pattern C Measured Boundary Summary + §retrieval-failure-diagnosis-order (both LOAD-BEARING architectural anchors)
5. Read `core/rag_integration.py` Pattern C section as design reference
6. Sanity checks (brew postgres + Pattern B/C smoke tests + backfill dry-run = 0 mismatches)
7. `git log --oneline -6` — should show S2827 close cascade + #3267 + S2826 close cascade + #3265 + S2825 close
8. Mint fresh pin scoped `s2828-pattern-d-literal-filename-injection`
9. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
10. **PATTERN D DESIGN AUTHORED UNDER CHRIS D-Q1 / D-Q4 / D5 CONSTRAINTS** — literal-filename intent patterns + literal-filename anchor mechanism + bounded policy bonus (measured smallest reliable adjustment) + diagnostic contract + negative controls
11. **DO NOT relax include_superseded=False default** — Chris D6 retrieval integrity rule (unchanged)
12. **DO NOT collapse Pattern C + D into a generic canonical gate** — Chris D5 mandates distinct mechanisms + measurements per class; refactor to shared primitive is post-Pattern-D per Chris D-Q3
13. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3 first cycle: "Retrieval must prove retrieval."
14. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred as separate post-Phase-0.5 investigation
15. **DO NOT author §2.2 methodology final numeric bands** until all pattern mechanisms measured (Pattern D still pending) — Chris D6 sequence
16. **DO NOT auto-adopt semantic default flips** (per S2821)
17. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
18. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
19. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
20. Route Pattern D design to Rigby SIGN before implementation per Chris D-Q3/D-Q5 sequence
21. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2: post-correction is the authoritative baseline; NOT unchanged-corpus)

---

## Reference documents

Ordered by frequency of use at S2828:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md`](docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md) — **S2827 handoff (current)**
3. [`docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md) — full design + §7.5 measurement evidence (Pattern D design reference)
4. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B (COUNT :60-100 + :242-296) + Pattern C (SELF_REFERENCE :106-217 + :377-395 + :499-522) implementations as Pattern D design reference
5. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — §retrieval-failure-diagnosis-order (S2826) + §Pattern C Measured Boundary Summary (S2827) — LOAD-BEARING architectural anchors
6. [`docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md`](docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md) — S2826 handoff (predecessor)
7. [`docs/research/discovery_layer/PHASE_0_5/corpus.json`](docs/research/discovery_layer/PHASE_0_5/corpus.json) — 20 P1 rows post-corpus-correction (authoritative baseline; preserve for Pattern D re-measurement)
8. [`docs/research/discovery_layer/PHASE_0_5/measurement_report.md`](docs/research/discovery_layer/PHASE_0_5/measurement_report.md) — S2825 baseline reference
9. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
10. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — Phase-0.5 arc row (updated at S2827 close)
11. [`tests/unit/test_s2827_pattern_c_self_reference_gate.py`](tests/unit/test_s2827_pattern_c_self_reference_gate.py) — pytest structure reference for Pattern D
