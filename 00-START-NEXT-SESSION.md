# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2826 CLOSED (2026-07-19; picks up as S2827) — **METADATA SYNC-DRIFT ROOT CAUSE + FULL-CORPUS REPAIR + PATTERN B COUNT GATE SHIPPED**

**Refreshed 2026-07-19 (SESSION 2826 CLOSED — Chris opened with architectural framing question about the shortest path to improve authoritative retrieval before optimizing router methodology. Three-cycle D-verdict cascade: first ratifying two-mechanism split (Pattern B ranking + Pattern C injection); then triggering D7 stop branch when `authority_weighted=True` proved a no-op (all competitors share `repo_canonical` tier); then diagnosing second D7 when direct code trace revealed 4 of 5 canonical anchors had `Document.status='archived'` in DB despite `docs/_index.json` saying `active` — filtered OUT by default `include_superseded=False` clause BEFORE ranking. Root cause established: `sync_docs_index_to_documents.py` update path refreshed 12 fields but never `Document.status`. Corpus-wide drift: 881 rows (86% of repo_canonical). Chris ratified Option D — full corpus backfill + same-PR sync fix + parallel Rigby SIGN on Pattern B. Executed atomically as PR #3265 (SHA `9c53ab880`) + all Rigby joint SIGN Q1-Q5 refinements applied. **Post-repair Phase-0.5 re-measurement on unchanged 16-row corpus, production settings: 0/16 → 6/18 = 33.3% strict top-1 hits.** 3 hits from Pattern B mechanism (Q21, Q23, Q26 corpus COUNT queries); 3 hits from **metadata repair ALONE** (Q19, Q22, Q28) — empirically validates Chris D6 architectural conclusion. SEVENTY-FIRST close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first empirical validation of retrieval-diagnosis discipline where metadata repair alone converts rows across 3 distinct policy classes; first in-session cascade of 3 D-verdict cycles + D7 stop trigger followed by successful root-cause repair.**

**S2826 ship (1 atomic PR):**

| Focus | PR | SHA | Merged to | Files |
|---|---|---|---|---|
| Metadata sync-drift repair + Pattern B COUNT gate | **#3265** | `9c53ab880` | main | 3 files: 324 insertions / 3 deletions |

**Handoff:** `docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md`
**Architectural conclusion:** cross-linked in `docs/KNOWLEDGE_PIPELINE.md` §retrieval-failure-diagnosis-order (S2826 addendum)

**Arc state at S2826 close:**
- **Discovery-layer arc:** Metadata drift REPAIRED (881 rows corrected). Sync-defect FIXED (same PR). Pattern B COUNT gate MERGED. Post-repair Phase-0.5 baseline: **6/18 = 33.3% strict top-1** (from 0/16 = 0%). Pattern C design QUEUED for S2827 per Chris D6 sequence. §2.2 methodology revision DEFERRED (Chris D6: don't author final numeric bands until post-fix measurement complete — happens after Pattern C too).
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817, unchanged).

---

## S2827 CANDIDATES

### ⭐ Recommended default direction — Pattern C SELF_REFERENCE candidate injection

**Rationale:** S2826 delivered 6/18 = 33.3% via Pattern B + metadata repair. 5 of 12 remaining misses are SELF_REFERENCE class (Q14, Q15, Q16, Q17, Q20) — Chris D2 (first cycle) approved the candidate-injection mechanism. Chris D6 sequence explicitly ratified: "Pattern C candidate-injection design routed through Rigby SIGN before implementation."

**Concrete first steps at S2827 open:**
1. Read S2826 handoff §4 (Chris D-verdicts) + §7 (architectural conclusion) + §9 (lessons)
2. Read `core/rag_integration.py` §S2826 Pattern B (lines 60-100 + 242-296) as design reference
3. Read Rigby Q2 sketch B in S2826 (two-stage rerank with canonical candidate injection + intent gate + suppression list)
4. Draft Pattern C design covering:
   - **SELF_REFERENCE intent patterns** (narrow gate; e.g., `\bstart\s+(here|next|new)\b` / `\bproject\s+rules\b` / `\bwhere\s+do\s+I\s+start\b` / literal filename patterns like `\b00[-_]?START[-_]?NEXT[-_]?SESSION\b` / `\bCLAUDE\.md\b`)
   - **Canonical anchor map** per policy class (e.g., `SELF_REFERENCE_ANCHORS = {'start': '00-START-NEXT-SESSION.md', 'rules': 'CLAUDE.md'}`)
   - **Injection mechanism** — when gate fires, inject the mapped canonical chunk(s) into the candidate pool via SQL UNION (or fetch-and-merge), preserving original similarity scores, then apply bounded policy bonus (per Chris D2)
   - **Diagnostic contract** per Chris D2 — gate name / injected candidates / original similarity / applied adjustment / final rank fields
   - **Negative controls** per Chris D4 — must not over-inject on adjacent queries
5. Route Pattern C design to Rigby joint SIGN (mirror S2826 5-question structure)
6. Iterate refinements
7. Chris D-verdict on design
8. Implementation + validation on the 5 SELF_REFERENCE rows
9. Full 16-row re-measurement
10. If material improvement — proceed to Pattern D (INDEX_DISCOVERY / literal-filename / doc-class-precedence per Chris D5)

### Available if Chris pivots

- **DISCOVERY policy-class mechanism** — 2 remaining rows (Q10 canon/INDEX target, Q11 PLATFORM_INVENTORY under DISCOVERY intent)
- **Literal-filename IDENTITY mechanism** — 1 remaining row (Q24 query="PLATFORM_INVENTORY")
- **§2.2 methodology revision** — Chris D6 says wait until all pattern mechanisms measured; can start skeleton (non-numeric parts) per Chris D6
- **13 out-of-index Document rows investigation** — Chris D6 recorded as separate post-Phase-0.5 follow-up
- **Playbook v0.9 amendment authoring** — 10/10 triggers on OP3; also new candidate from S2826 zoom-out fold §5.2 (sync-update-path completeness discipline, 3-trigger shape S1234/S1235/S2826)
- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability

**Recommended default:** Pattern C SELF_REFERENCE candidate injection design + Rigby SIGN.

---

## SESSION PIN — S2826 RETIRED (fresh mint required at S2827 open)

**Pin history (S2826):**

- `pa-def161f46bb2419f` (label `s2826-audit-vs-methodology-priority-eval`) minted at S2826 open; **retired at S2826 close (`force=true`, fifty-seventh consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2827 first-action fresh mint.

**S2827 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2826 handoff §4 (Chris D-verdicts) + §7 (architectural conclusion) + §9 (lessons)
# Read core/rag_integration.py §S2826 Pattern B (lines 60-100 + 242-296)

# Sanity checks
brew services list | grep postgres

# Verify Pattern B still working post-recycle
python manage.py shell -c "from core.rag_integration import search_embeddings; import json; c = search_embeddings(query='How many spiders', limit=3, similarity_threshold=0.4); print(json.dumps([{'file': (r.get('metadata') or {}).get('file_path'), 'sim': r.get('similarity_score'), 'bonus': r.get('count_intent_bonus'), 'gate': r.get('intent_gate_fired')} for r in c[:3]], indent=2))"
# expect top-1 = docs/PLATFORM_INVENTORY.md with bonus=0.05 gate=True

# Verify metadata layer still healthy
python manage.py backfill_document_status_from_docs_index --dry-run 2>&1 | tail -8
# expect Total mismatches: 0

python manage.py session_lifecycle open --label s2827-pattern-c-self-reference-injection
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2826 lessons to carry (also in handoff §9):**

1. **Metadata layer inspection is Step 1 of any retrieval-failure diagnosis.** Skipping to boost design is a category error. Chris D7 codified via stop branch.
2. **Sync commands whose UPDATE path refreshes only SOME fields create persistent drift classes.** Watch for this pattern in every sync/mirror command.
3. **Chris D6 architectural conclusion is empirical:** 3 of 6 post-repair conversions came from metadata repair ALONE — no policy mechanism ran. The retrieval was always adequate; the corpus was hidden.
4. **Rigby Q5 zoom-out pushback was load-bearing** — reframed the entire recommendation and led to D7 stop trigger + Option D repair path.
5. **DO NOT relax `include_superseded=False` default** to "fix" remaining misses. Chris D6 rule: retrieval integrity requires the filter stay strict.
6. **Pattern C design routed through Rigby SIGN before implementation** per Chris D6 sequence.
7. **13 out-of-index Document rows** — deferred per Chris D6.
8. **Load-bearing constitutional rule (Chris D3 first cycle):** *"Retrieval must prove retrieval. Runtime injection cannot be used to erase a retrieval-layer failure."* Do NOT propose adding docs to universal runtime injection to "fix" retrieval misses.

---

## Twin-pointer card

📁 **Repo — S2826 artifacts:**

- **Backfill command:** `core/management/commands/backfill_document_status_from_docs_index.py`
- **Sync fix:** `core/management/commands/sync_docs_index_to_documents.py:305-320`
- **Pattern B implementation:** `core/rag_integration.py:60-100` + `:242-296` + drift-re-mask WARN at `:397-427`
- **Handoff:** `docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md`
- **Architectural conclusion:** `docs/KNOWLEDGE_PIPELINE.md` §retrieval-failure-diagnosis-order (S2826 addendum)
- **Merge SHA:** `9c53ab880` · **PR:** #3265
- **S2825 antecedent measurement (context):** `docs/research/discovery_layer/PHASE_0_5/measurement_report.md`

🖥️ **Workspace UI — S2826 twin-pointer workspace deliverable:**

- **`f2c39253-8e7a-40af-80d0-d2806014d75a`** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) — type `ratification_record`, category `governance`, status `ready`, pinned. ORM-direct create bypasses pa_deliverables_tool diagnostic-flag bug.

---

## Current repository state (S2826 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `9c53ab880` (S2826 close PR #3265) |
| Playbook version | v0.8.0 (unchanged; **v0.9-candidate sync-update-path-completeness discipline 3/2 triggers likely per S2826 fold §5.2**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Discovery-layer arc state** | **Metadata drift REPAIRED (881 rows). Sync-defect FIXED. Pattern B MERGED. Post-repair Phase-0.5: 6/18 = 33.3%. Pattern C QUEUED for S2827.** |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2827 recommended lean | Pattern C SELF_REFERENCE candidate injection design + Rigby SIGN |
| Session pin | `pa-def161f46bb2419f` (retired at S2826 close, force=true, fifty-seventh consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2827 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +2 at S2826 (post-#3265 merge + close-cascade PR merge) |
| Metadata layer health | ✅ 0 mismatches vs docs/_index.json (post-S2826) |
| Next move | S2827 opens Pattern C SELF_REFERENCE candidate injection design. Fresh pin `s2827-pattern-c-self-reference-injection`. |

---

## Recommended session-open protocol (S2827, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2826 handoff §4 (Chris D-verdicts D1-D7 all cycles) + §7 (architectural conclusion) + §9 (lessons)
4. Read `core/rag_integration.py` §S2826 Pattern B as design reference
5. Sanity checks (brew postgres + Pattern B smoke test + backfill dry-run = 0 mismatches)
6. `git log --oneline -6` — should show S2826 close cascade + #3265 + S2825 close + S2824 backfill + S2824 feature
7. Mint fresh pin scoped `s2827-pattern-c-self-reference-injection`
8. **Anti-rubber-stamp check on first SIGN** — verify Rigby `tool_runs` non-empty
9. **PATTERN C DESIGN AUTHORED UNDER CHRIS D2/D5 CONSTRAINTS** — SELF_REFERENCE intent patterns + canonical anchor map + injection mechanism + bounded policy bonus + diagnostic contract + negative controls
10. **DO NOT relax include_superseded=False default** — Chris D6 retrieval integrity rule
11. **DO NOT collapse policy classes into a generic canonical gate** — Chris D5 mandates distinct mechanisms + measurements per class
12. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3 first cycle: "Retrieval must prove retrieval."
13. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred as separate post-Phase-0.5 investigation
14. **DO NOT author §2.2 methodology final numeric bands** until all pattern mechanisms measured — Chris D6 sequence
15. **DO NOT auto-adopt semantic default flips** (per S2821)
16. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
17. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
18. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
19. Route Pattern C design to Rigby SIGN before implementation per Chris D6 sequence
20. Preserve unchanged 16-row corpus for re-measurement per Chris D5

---

## Reference documents

Ordered by frequency of use at S2827:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md`](docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md) — **S2826 handoff (current)**
3. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B implementation + drift-re-mask WARN (design reference for Pattern C)
4. [`core/management/commands/backfill_document_status_from_docs_index.py`](core/management/commands/backfill_document_status_from_docs_index.py) — S2826 restoration command
5. [`core/management/commands/sync_docs_index_to_documents.py`](core/management/commands/sync_docs_index_to_documents.py) — S2826 sync fix (update-path status refresh)
6. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — §retrieval-failure-diagnosis-order (S2826 addendum)
7. [`docs/handoffs/SESSION_2825_PHASE0_5_HARVEST_EXECUTED_METHODOLOGY_RETURN.md`](docs/handoffs/SESSION_2825_PHASE0_5_HARVEST_EXECUTED_METHODOLOGY_RETURN.md) — S2825 handoff (predecessor; 0/16 baseline)
8. [`docs/research/discovery_layer/PHASE_0_5/measurement_report.md`](docs/research/discovery_layer/PHASE_0_5/measurement_report.md) — S2825 measurement report (LOAD-BEARING context; 0/16 baseline explained)
9. [`docs/research/discovery_layer/PHASE_0_5/corpus.json`](docs/research/discovery_layer/PHASE_0_5/corpus.json) — 20 P1 rows (16 measurable; preserve for Pattern C re-measurement)
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
11. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — Phase-0.5 arc row (updated at S2826 close)
