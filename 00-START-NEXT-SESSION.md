# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2829 CLOSED (2026-07-19; picks up as S2830) — **CANONICAL ANCHOR DRIFT TRIAGE SHIPPED; S2826-CLASS RE-MANIFESTATION FIXED AT THE SUBSTRATE**

**Refreshed 2026-07-19 (SESSION 2829 CLOSED — Chris opened with "Please begin" after S2828 close. Sanity checks per session-open protocol immediately surfaced drift: 870 mismatches in the metadata layer (S2828 close asserted 0), and all three Pattern B/C/D queries returned non-canonical top-1 docs via DRIFT WARN paths. Joint Claude+Rigby SIGN over 2 cycles (5 questions cycle 1 + writer-narrowed cycle 2; tool_runs verified non-empty per anti-rubber-stamp) traced two independent defects that let the S2826 drift class re-manifest: (1) `backfill_document_status_from_docs_index` was unguarded — bare invocations wrote against mid-flight `_index.json`, causing bulk-flip of 866 rows at 2026-07-19T03:17:40 UTC to `status='archived'`; (2) `sync_docs_index_to_documents` skip-branch (`content_hash == content_hash` → return `'skipped'`) never touched status, so every subsequent sync preserved the archived state on the 3 canonical anchors whose file content hadn't changed. Chris D-verdict "approved" for A→B sequence with Rigby guardrail (identify writer FIRST, then repair). PR1 (#3271, SHA `584f13026`) shipped: `--apply`/`--dry-run` explicit-mode guard on backfill + `_index.json` bytes snapshot + sha256 hash log at command start + sync skip-branch status-refresh closure + `status_refreshed` stats counter + 3 canonical anchors restored via targeted ORM save + 9 new pytests + 1 regression fix. PR2 executed post-merge: `backfill --apply` → 867 rows restored → dry-run reports **0 mismatches**. Pattern B/C/D smoke all green: `where do I start` → `00-START-NEXT-SESSION.md`; `How many spiders` → `docs/PLATFORM_INVENTORY.md`; `PLATFORM_INVENTORY` → `docs/PLATFORM_INVENTORY.md`. PR3 (canonical-anchor invariant design + divergent-retrieval-stack diagnostic) DEFERRED as separate architectural arc per Chris D3 + Rigby Q5. `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. SEVENTY-FOURTH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first empirical validation that S2826 fix had a 2nd-order skip-branch hole; first empirical validation of same-microsecond `updated_at` bulk-signature as a forensic writer-narrowing technique; first arc where a session-open sanity-check failure caused arc-scope pivot from the recommended-default lean (registry primitive extraction) to a substrate-drift-repair.**

**S2829 ship (1 atomic PR + 1 data-only backfill execution):**

| Focus | PR / Event | SHA | Merged to | Files/Rows |
|---|---|---|---|---|
| Metadata-sync hardening — stop-writer + skip-branch closure + anchor restore | **#3271** | `584f13026` | main | 5 files: 352 insertions / 15 deletions |
| Bounded backfill run (867-row restore) | PR2 execution | — | data-only | 867 Document rows: archived → processed |

**Handoff:** `docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md`
**Pytest coverage:** `core/tests/test_s2829_metadata_sync_hardening.py` (9 tests)
**Metadata layer post-S2829:** ✅ 0 mismatches vs docs/_index.json

**Arc state at S2829 close:**
- **Metadata layer:** ✅ 0 mismatches. `--apply` guard prevents unattended bulk sweeps. Sync skip-branch closure means no future drift-persistence-on-unchanged-content. `_index.json` snapshot + hash log makes mid-flight regeneration detectable in post-hoc audits.
- **Discovery-layer arc:** Pattern B (COUNT) MERGED at S2826. Metadata drift REPAIRED at S2826 → RE-DRIFTED between S2828 close and S2829 open → **RE-REPAIRED at S2829 with substrate hardening (S2826 2nd-order hole closed)**. Pattern C (SELF_REFERENCE) MERGED at S2827. Pattern D (LITERAL-FILENAME) MERGED at S2828. Post-Pattern-D Phase-0.5 baseline: 12/18 = 66.7% strict top-1 (unchanged from S2828). Shared "pointer-intent registry" primitive extraction remains a candidate arc (S2828 Chris D-Q3 forward-carry) but was NOT pursued in S2829 due to drift-triage pivot.
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817, unchanged).

---

## S2830 CANDIDATES

### ⭐ Recommended default direction — Return to S2828's original recommended default: shared "pointer-intent registry" primitive extraction design

**Rationale:** S2828 close-brief recommended default was the pointer-intent registry primitive design per Chris D-Q3 forward-carry. That was pre-empted at S2829 open by the metadata drift discovery. Now that the drift is fully repaired + substrate-hardened (S2826 skip-branch hole closed; --apply guard in place), the Chris D-Q3/D-Q7 gate is again open with the discovery layer on a stable, verified baseline.

**Concrete first steps at S2830 open:**
1. Read S2829 handoff §5-§7 (implementation + lessons — new substrate context)
2. Read S2828 handoff §3-§5 (Rigby SIGN + Chris D-verdicts + measurement evidence — original registry framing)
3. Read `docs/KNOWLEDGE_PIPELINE.md` §Pattern D + §Pattern C Measured Boundary Summaries + §retrieval-failure-diagnosis-order (unchanged; still LOAD-BEARING)
4. Read `core/rag_integration.py` Pattern B (`:60-105`) + Pattern C (`:106-255`) + Pattern D (`:258-410`) side-by-side to characterize shared skeleton
5. Draft "pointer-intent registry" design doc per S2828 close-brief §4 shape (shape survey, shape divergence, primitive shape proposal, zero-behavior-change guarantee, migration sequence)
6. Route registry design to Rigby joint SIGN
7. Chris D-verdict on design (whether to build in S2830 or defer)

**⚠ IMPORTANT** — Chris D-Q7 at S2828 was explicit: "Only then evaluate the shared pointer-intent registry as its own architectural arc." "Evaluate" ≠ "build automatically." Route as design proposal first.

### Available if Chris pivots

- **PR3 (S2829 deferred)** — Canonical-anchor invariant design: anchors pinned/boosted + immune from bulk status sweeps + not hidden by processed-only filters. Playbook v0.9-adjacent. + divergent-retrieval-stack diagnostic (query → top-3 matrix across `search_embeddings` vs `kb_tool.semantic_search`).
- **DISCOVERY policy-class mechanism** — 2 remaining rows (Q10 canon/INDEX target, Q11 DISCOVERY intent) — Chris D5 distinct-mechanism class.
- **CONCEPTUAL / PROCEDURAL semantic-general future arc** — 4 rows (Q9, Q12, Q13, Q18) — semantic-general mechanism (LLM-lite intent classifier).
- **§2.2 methodology revision** — Chris D6 said wait until all pattern mechanisms measured; Pattern B/C/D data now available.
- **Playbook v0.9 amendment authoring** — sync-update-path-completeness discipline (S2826 §5.2 fold, now with S2829 skip-branch hole trigger reinforcing it → potentially 4/2 triggers).
- **13 out-of-index Document rows investigation** — Chris D6 recorded as separate post-Phase-0.5 follow-up.
- **Colorado Phase 4** — statute-citation content quality.
- **BettingPage first-user trace** — real user-facing capability.

**Recommended default:** Shared "pointer-intent registry" primitive design + Rigby SIGN (per S2828 Chris D-Q3/D-Q7 sequencing, now with clean baseline).

---

## SESSION PIN — S2829 RETIRED (fresh mint required at S2830 open)

**Pin history (S2829):**

- `pa-d3a4d67126b64e7f` (label `s2829-canonical-anchor-drift-triage`) minted at S2829 open; **retired at S2829 close (`force=true`, sixtieth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2830 first-action fresh mint.

**S2830 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2829 handoff §5-§7 (implementation + lessons)
# Read S2828 handoff §3-§5 (registry-primitive framing) if pursuing recommended default
# Read core/rag_integration.py Pattern B/C/D sections side-by-side

# Sanity checks (must be green — S2829 substrate hardening should hold)
brew services list | grep postgres

# Verify metadata layer clean
python manage.py backfill_document_status_from_docs_index --dry-run 2>&1 | tail -8
# expect Total mismatches: 0

# Verify Pattern B/C/D all working
python manage.py shell -c "from core.rag_integration import search_embeddings; \
  c = search_embeddings(query='where do I start', limit=1, similarity_threshold=0.4); \
  print('Pattern C:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='How many spiders', limit=1, similarity_threshold=0.4); \
  print('Pattern B:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='PLATFORM_INVENTORY', limit=1, similarity_threshold=0.4); \
  print('Pattern D:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name'))"
# expect all three top-1 canonical, NO DRIFT WARN

# Verify --apply guard works
python manage.py backfill_document_status_from_docs_index 2>&1 | tail -3
# expect: CommandError: Explicit mode required

python manage.py session_lifecycle open --label s2830-pointer-intent-registry-primitive-design
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2829 lessons to carry (also in handoff §7):**

1. **S2826's sync-defect fix had a 2nd-order skip-branch hole.** The update-branch (`content_hash` mismatch) refresh was necessary but not sufficient. The skip-branch (`content_hash` matches) must ALSO refresh status against docs_index_status; otherwise ANY prior drift persists indefinitely on unchanged-content docs.
2. **Backfill commands touching `_index.json` should snapshot it in-memory at command start.** Mid-flight regeneration between backfill start and finish can silently invert command meaning. Snapshot + hash-log makes divergence detectable in post-hoc audits.
3. **Bare-invocation writes must be forbidden for bulk-status commands.** `--apply` guard: one CLI flag, closes the "unattended run at the wrong moment" writer class.
4. **`updated_at` bucketing by microsecond is a reliable forensic writer-narrowing signature.** Same-microsecond ≈ one SQL `.update()`. Different-microsecond sequences ≈ per-row `.save()`. Narrows writer class from "any code path" to "commands using fixed-`now` in `.update()` loops".
5. **`content_hash` disk-vs-DB parity is the sync skip-branch entry test.** When investigating drift-on-unchanged-content, verify hash comparison before assuming sync ran and did nothing.
6. **DO NOT run docs cascade steps manually against uncertainly-fresh `_index.json`.** Any manual step (build_docs_index / sync / backfill) should be a single monotonic sequence, not intermixed with other repo work.
7. **DO NOT bundle PR3 architectural work with substrate repairs.** Rigby Q5 caught it — invariant design + divergent-stack investigation belong in their own arc.
8. **DO NOT relax the `--apply` guard on backfill.** Prevents recurrence of the S2829 writer class.
9. **DO NOT relax the sync skip-branch status refresh.** Prevents recurrence of the S2826 2nd-order defect.

---

## Twin-pointer card

📁 **Repo — S2829 artifacts:**

- **Implementation:** `core/management/commands/backfill_document_status_from_docs_index.py` (--apply/--dry-run guard + snapshot hash); `core/management/commands/sync_docs_index_to_documents.py` (skip-branch closure at :265-290)
- **Pytest coverage:** `core/tests/test_s2829_metadata_sync_hardening.py` (9 tests, all pass)
- **Handoff:** `docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md`
- **Merge SHA:** `584f13026` · **PR:** #3271

🖥️ **Workspace UI — S2829 twin-pointer workspace deliverable:**

- To mint at close cascade: `ratification_record` in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), category `governance`, `diagnostic_status=None`. ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.

---

## Current repository state (S2829 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `584f13026` (S2829 PR #3271 merge) + close-cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged; v0.9-candidate sync-update-path-completeness discipline now potentially 4/2 triggers after S2829) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Metadata layer** | ✅ **0 mismatches (S2829 restored)**; `--apply` guard active; sync skip-branch closed |
| **Discovery-layer arc state** | Pattern B/C/D all shipped + retrieval integrity RESTORED post-S2829. Post-Pattern-D Phase-0.5 baseline: 12/18 = 66.7% strict top-1 (unchanged; S2829 was substrate-repair, not measurement-changing). |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2830 recommended lean | Shared "pointer-intent registry" primitive design (returns to S2828's recommended default now that baseline is clean) |
| Session pin | `pa-d3a4d67126b64e7f` (retired at S2829 close, force=true, sixtieth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2830 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2829 (post-#3271 merge) |
| Next move | S2830 opens registry primitive design under Chris D-Q3/D-Q7 constraints. Fresh pin `s2830-pointer-intent-registry-primitive-design`. |

---

## Recommended session-open protocol (S2830, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2829 handoff §5-§7 (implementation + lessons — substrate context)
4. Read S2828 handoff §3-§5 (Rigby SIGN + Chris D-verdicts + measurement evidence — registry framing)
5. Read `docs/KNOWLEDGE_PIPELINE.md` §Pattern D + §Pattern C Measured Boundary Summaries + §retrieval-failure-diagnosis-order
6. Read `core/rag_integration.py` Pattern B + C + D sections side-by-side
7. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + bare backfill → CommandError)
8. `git log --oneline -8` — should show S2829 close cascade + #3271 + S2828 close cascade + #3270 + #3269
9. Mint fresh pin scoped `s2830-pointer-intent-registry-primitive-design`
10. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
11. **REGISTRY PRIMITIVE DESIGN AUTHORED UNDER CHRIS D-Q3 / D-Q7 CONSTRAINTS** — zero-behavior-change guarantee; migration sequence; per-mechanism registration; Chris-ratification-first
12. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
13. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
14. **DO NOT relax include_superseded=False default** — Chris D6 retrieval integrity rule (unchanged)
15. **DO NOT proceed to implementation without explicit Chris D-verdict** — Chris D-Q7 said "evaluate as its own architectural arc"
16. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
17. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
18. **DO NOT auto-adopt semantic default flips** (per S2821)
19. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
20. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
21. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
22. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
23. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
24. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2830:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md`](docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md) — **S2829 handoff (current)**
3. [`docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md`](docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md) — S2828 handoff (registry-primitive framing)
4. [`docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md) — registry-primitive design reference
5. [`docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md`](docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md) — Pattern C design
6. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D side-by-side reference
7. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — Pattern B/C/D Measured Boundary Summaries + retrieval-failure-diagnosis-order
8. [`core/management/commands/sync_docs_index_to_documents.py`](core/management/commands/sync_docs_index_to_documents.py) — S2829 skip-branch closure
9. [`core/management/commands/backfill_document_status_from_docs_index.py`](core/management/commands/backfill_document_status_from_docs_index.py) — S2829 --apply guard + snapshot
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
11. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — Phase-0.5 arc row (updated at S2829 close)
12. [`core/tests/test_s2829_metadata_sync_hardening.py`](core/tests/test_s2829_metadata_sync_hardening.py) — 9-case pytest reference
