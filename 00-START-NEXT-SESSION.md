# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2835 CLOSED (2026-07-19; picks up as S2836) — **GROUP 2800 T2 REFERENCE-GRAPH AUDIT RATIFIED · SCHEMA V1.1 UNCHANGED · T3a DUPLICATE-CONTENT AUDIT OPENS AT S2836**

**Refreshed 2026-07-19 (SESSION 2835 CLOSED — fresh session opened per S2834 pointer. Chris opened with "Please begin"; after seeing candidate menu (net-new engineering first per `feedback_engineering_bias_over_audit`, plus ratified T2 default from S2834 D-verdict) Chris picked the ratified default: open T2. All S2835 open-protocol sanity checks green at open (pg15 started, backfill 0 mismatches, Pattern B/C canonical, parity harness 47/47 in 192.06s). Fresh pin `pa-0de182aaedcf43f0` (label `s2835-t2-reference-graph-audit`) minted at first-action. Claude built `tools/audit_2802_reference_graph.py` (basename-index-cached mechanical grep + resolver over 4 reference classes) and ran it across 791 non-handoff in-scope source files / 26,900 total references. Aggregate raw defect rate 40.2%; post-Rigby-fold FP disposition surfaced 3 false-positive classes (FP-1 workspace-canonical Cycle 1A ADRs; FP-2 bare-basename anchor prose mentions dominating file_cite RENAMED; FP-3 regex over-match on code/prose fragments). Joint Claude+Rigby joint SIGN over 2 cycles reached agreement. Cycle 1 (10+ substantive tool_runs — `deliverable_tool.list` workspace enumeration + `repo_tool.read` on HANDOFF_NUMBERING_GAPS.md, PLATFORM_WHAT_IT_IS.md:38-78, 00-START-NEXT-SESSION.md:66-106, T2 §1.4/§2.3/§6.1): 3 DISAGREE (Q1 ADR-0000 workspace-absent split from FP-1; Q3 both would-be P0s misclassified — SESSION_1099 in refresh-block context → P1; WorkspacePageNew typo in D-bucket → P2; Q4 coverage:full_claim_walk overstates T2's actual scan) + 2 STRENGTHEN (Q2 only SESSION_198/205 documented as intentional gaps; Q5 ship-with-loud-limitations valid stance). Cycle 2 (5+ substantive `repo_tool.read` — fold verification): Q6 AGREE (ADR-0000 split landed cleanly) + Q7 DISAGREE→AGREE post-fix (Rigby caught real fold-gap — §2.9 YAML sample severities still P0 on both PLATFORM_WHAT_IT_IS + 00-START samples; fixed same-turn to P1/P2 with Q3 citation) + Q8 AGREE (coverage relabeling landed under current v1.1 semantics; v1.2 split recorded as future_trigger). Anti-rubber-stamp verified across both cycles per `feedback_verify_rigby_tool_runs_before_trusting_sign`; caught 2 real F-BLOCKING refinements. Chris D-verdict: **"ratify T2 as-folded"**. Post-fold defect population: **0 P0** (both would-be P0s downgraded — §10.4(b) root-stability gate NOT triggered) + ~9 P1 (SESSION_1099 refresh-block P1 + ADR-0000 escalate_to_chris P1 + 4 md_link RENAMED path-depth errors in playbook_v0_1 docs + ~3 additional real BROKEN) + ~30-50 P2 (WorkspacePageNew typo + 13 NEW real broken SESSION_NNNN gaps beyond HANDOFF_NUMBERING_GAPS.md's catalog + closed_research_arc + audits_reports) + remainder P3. §10.1 v1.1 schema UNCHANGED — v1.2 `coverage_refs`/`coverage_claims` split proposal recorded as §5.7 future_trigger for 2899 close (NOT applied per S2834 schema-mod boundary). **ADR-0000 disposition escalation surfaced to Chris in T2 §4.1 row 2** (workspace deliverable NOT found; disposition options a/b/c pending). Ratification envelope authored at `docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md`. 2802 doc frontmatter updated status: proposed→ratified with full ratification block. Group 2800 arc registration in `docs/research/OPEN_ARCS.md` updated (2→3 of 6 shipped). **NEW MEMORY ESTABLISHED at S2835 open per Chris directive:** `feedback_rigby_writes_workspace_deliverables` — Rigby creates workspace mirrors via `deliverable_tool.create`, NOT Claude via ORM-direct. First exercise: T2 close cascade. `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. EIGHTY-FIRST close-cycle post-PLAYBOOK-7.4.4. Handoff: `docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md`.**

**S2835 ship (T2 child audit):**

| Focus | Artifact | Location |
|---|---|---|
| T2 child audit (791-file / 4-class ref-graph scan + Rigby-folded findings) | New | `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md` (~950 lines, status ratified) |
| T2 scanner tool | New | `tools/audit_2802_reference_graph.py` |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 3/6 shipped) |
| S2835 handoff | New | `docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md` |
| S2836 pointer | Updated | THIS file — recommended default = T3a duplicate-content audit |
| New memory | New | `feedback_rigby_writes_workspace_deliverables.md` + MEMORY.md index update |

**Arc state at S2835 close:**
- **Group 2800 /docs/ content audit arc**: **T2 RATIFIED at S2835 (schema v1.1 unchanged; ADR-0000 escalation surfaced)**. **3 of 6 shipped** (parent + T1 + T2). T3a opens at S2836. Migration queue frozen; routed to future §3 execution arc post-2899 close.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue DEFERRED. (Unchanged.)
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

---

## S2836 CANDIDATES

Per `feedback_engineering_bias_over_audit` — net-new engineering pivots listed first; ⭐ marks the S2835-derived ratified default (T3a next per Group 2800 sequence).

### A. Net-new engineering pivots (per engineering-bias rule)

1. **Colorado Phase 4 statute-citation quality pass** — Chris personal legal work; real capability
2. **BettingPage first-user trace** — Chris IS the first user; wire the real path end-to-end
3. **New spider / PA tool / Workspace tab** — pick a concrete gap
4. **ADR-0000 disposition** — surfaced from T2 escalate_to_chris; small governance decision

### B. ⭐ Ratified default — T3a duplicate-content audit (Group 2800 third child)

Per Group 2800 arc sequence + S2835 close pointer.

**Recommended S2836 session shape:**

1. Fresh pin `s2836-t3a-duplicate-content-audit`
2. Author `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`
3. Scope (per parent §4 T3a): ~810-file corpus (786 non-handoff + 24 code-review); token-shingling / MinHash near-dup detection → top-K pair candidates → manual severity review on top ~100 pairs
4. **Pre-scan hint inherited from S2834 §4.1a:** topics tagged `count_dense` vs `narrative` before dup detection (grep patterns `\*\*Current runtime counts` + `\b\d+\b\s+(agents|tools|handlers|spiders|services|models)`)
5. **Pre-clustering signal from T2 §5.6:** basename RENAMED map from `/tmp/t2_scan_out.json` identifies files sharing basenames — free duplicate-candidate seed for T3a scanner
6. Emit YAML findings per §10.1 v1.1 schema (all rows inherit `schema_version: 1.1`)
7. Rigby joint SIGN + Chris D-verdict
8. Migration-queue routing to future §3 execution arc

**Anti-pattern to actively challenge (parent §4 T3a):** "identical
content = trivially deletable duplicate." Some near-duplicates are
intentional load-bearing-both (e.g. narrative anchor + reference table)
— classify severity (`identical` / `near-identical` / `partial-overlap-load-bearing-both`
/ `partial-overlap-consolidate-candidate`) not disposition.

### C. §7 anchor updates (Group 2700 deferred at S2832)

Bucket A auto-actionable ~1 session:
- PLATFORM_INVENTORY: add Group 2800 arc-opening + T1/T2 close notes
- ARCHITECTURE_INDEX: register Group 2800 + T1/T2 close
- CLAUDE.md: fix the P0 line 262 discord count in-place (root-stability §10.4 (b) gate from S2834 T1)

### D. Substrate / refactor (available if Chris pivots)

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + RAG Diagnostics tab (S2831) must produce identical `matched_patterns` post-refactor.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug hygiene:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
  - LucideIcon typing drift in `WorkspacePageNew.tsx` (P2 per T2 §2.8 Rigby Q3 fold)

**Recommended default (per Group 2800 sequence):** Open T3a duplicate-content audit at S2836 as `2803a_docs_content_duplicate_audit.md`.

---

## SESSION PIN — S2835 RETIRED (fresh mint required at S2836 open)

**Pin history (S2835):**

- `pa-0de182aaedcf43f0` (label `s2835-t2-reference-graph-audit`) minted at S2835 open turn 1; served as both session pin AND arc SIGN pin (2 cycles preserved for future arc reference); **retired at S2835 close (`force=true`, sixty-sixth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2836 first-action fresh mint.

**S2836 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2835 handoff §3-§8 (Rigby SIGN 2-cycle status + Chris D-verdict + follow-up carry + ADR-0000 escalation)
# Read S2835 ratification envelope §1-§4 (v1.1 schema unchanged + v1.2 future_trigger + FP disposition)
# Read 2802 T2 §5.6 (pre-clustering signal for T3a) + §5.7 (v1.2 schema-split future_trigger)
# Read 2801 T1 §4.1a (T3a pre-scan hint — count_dense vs narrative)
# Read 2800 parent scoping §4 T3a spec

# Sanity checks (must be green — S2829 substrate + S2830 DORMANT + S2831 UI tab all intact)
brew services list | grep postgres

python manage.py backfill_document_status_from_docs_index --dry-run 2>&1 | tail -8
# expect Total mismatches: 0

python manage.py shell -c "from core.rag_integration import search_embeddings; \
  c = search_embeddings(query='where do I start', limit=1, similarity_threshold=0.4); \
  print('Pattern C:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name')); \
  c = search_embeddings(query='How many spiders', limit=1, similarity_threshold=0.4); \
  print('Pattern B:', (c[0].get('metadata') or {}).get('file_path'), c[0].get('intent_gate_name'))"
# expect Pattern C: 00-START-NEXT-SESSION.md self_reference; Pattern B: docs/PLATFORM_INVENTORY.md count

python -m pytest tests/regression/rag_registry_parity/ tests/unit/test_intent_mechanism_registry.py core/tests/test_views_rag_intent_gate_diagnostics_2831.py -q 2>&1 | tail -3

python manage.py session_lifecycle open --label s2836-t3a-duplicate-content-audit
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2835 lessons to carry (also in handoff §7):**

1. **Anti-rubber-stamp discipline caught 2 real F-BLOCKING refinements
   across the arc** (Q1 ADR-0000 split; Q7 YAML sample severity fold lag).
   Both would have shipped defect artifacts had Rigby rubber-stamped.
2. **`deliverable_tool.list` workspace enumeration IS the ADR resolver**
   for Cycle 1A ADRs. A filesystem-only mechanical grep will always miss
   workspace-canonical governance artifacts.
3. **YAML sample sync-with-text fold discipline.** When a table / prose /
   histogram downgrades a severity, YAML sample rows ARE part of the fold
   surface. Cycle 2 Q7 caught this. Next audit's cycle-2 verification MUST
   re-read sample rows.
4. **Coverage semantics under v1.1 overload**: `structural_only` for T1
   (claim-walk-only) vs T2 (ref-graph-only) both fit but conflate. v1.2
   split is a real refinement candidate at 2899 close.
5. **Rigby writes workspace deliverables** (new memory established at
   S2835 open per Chris directive). Claude writes repo files + routes
   explicit instruction to Rigby + verifies. First exercise: T2 close.
   Watch for drift at T3a close.
6. **Ship-with-loud-limitations is a valid audit stance.** Rigby Q5
   STRENGTHEN validated.
7. **DO NOT open T3a in same session as T2 ratification** (parent §5
   sequential-child discipline).
8. **DO NOT execute any /docs/ file operations during Group 2800.**
9. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.**
   Locked at S2834; v1.2 candidate recorded but NOT applied.
10. **DO NOT collapse T3a/T3b back into single T3** — S2833 Rigby cycle-1
    Q1 STRENGTHEN evidence stands.
11. **DO NOT expand T4 into per-handoff content review.**
12. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.**
13. **DO NOT audit in-flight arc children** (per parent §7 anti-scope).
14. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without
    fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary.
15. **DO NOT couple new observability surfaces to log capture** — S2831
    Rigby Q2 substrate rule.
16. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary.
17. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract.
18. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure.
19. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant.
20. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred.
21. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards.
22. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary.
23. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4.
24. **DO NOT bypass Rigby for workspace deliverable creation** — new
    S2835 rule per `feedback_rigby_writes_workspace_deliverables`.

---

## Twin-pointer card

📁 **Repo — S2835 artifacts:**

- **T2 audit doc (RATIFIED):** `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md`
- **Handoff:** `docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md`
- **Scanner tool:** `tools/audit_2802_reference_graph.py`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 3/6 shipped)
- **Rigby SIGN conversation:** `pa-0de182aaedcf43f0` (2 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2835 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: **Rigby creates** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via PA `deliverable_tool.create` per **NEW MEMORY** `feedback_rigby_writes_workspace_deliverables`; category `governance`; `deliverable_type=ratification_record`; `diagnostic_status=None`. Claude routes explicit instruction post-merge with content body + envelope body + workspace ID + create spec; Claude verifies tool_runs + ORM cross-check.

---

## Current repository state (S2835 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2835 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged; 205 rules) |
| **Group 2800 arc state** | **T2 RATIFIED (S2835, schema v1.1 unchanged); 3 of 6 shipped; T3a opens at S2836.** |
| Group 2700 arc state | ARC CLOSED (S2817); §3 target tree RATIFIED (S2832); §7 + §8 DEFERRED (unchanged) |
| Metadata layer | ✅ 0 mismatches (S2829 substrate intact) |
| Discovery-layer arc state | Pattern B/C/D shipped + Registry Step 1 DORMANT + UI canary tab shipped (S2818-S2831). Step 2 refactor deferred. |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| Content-audit schema | §10.1 v1.1 (locked at S2834; unchanged at S2835 — v1.2 `coverage_refs`/`coverage_claims` split proposal recorded as §5.7 future_trigger for 2899 close) |
| Chris escalation open | **ADR-0000 disposition** (§4.1 row 2 escalate_to_chris — workspace deliverable NOT found; options a/b/c pending) |
| S2836 recommended lean | Open T3a duplicate-content audit as `2803a_docs_content_duplicate_audit.md`. Alternatives available if Chris pivots. |
| Session pin | `pa-0de182aaedcf43f0` (retired at S2835 close, force=true, sixty-sixth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2836 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2835 (post-cascade merge, eighty-first consecutive) |
| Next move | S2836 opens with T3a duplicate-content audit; fresh pin `s2836-t3a-duplicate-content-audit`. |

---

## Recommended session-open protocol (S2836, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2835 handoff §3-§8 (Rigby SIGN 2-cycle status + Chris D-verdict + follow-up carry + ADR-0000 escalation)
4. Read S2835 ratification envelope §1-§4 (v1.1 schema unchanged + FP disposition + v1.2 future_trigger)
5. Read 2802 T2 §5.6 (pre-clustering signal from RENAMED map) + §5.7 (v1.2 schema-split future_trigger)
6. Read 2801 T1 §4.1a (T3a topics `count_dense` vs `narrative` pre-scan hint)
7. Read 2800 parent scoping §4 T3a (T3a spec) — token-shingling / MinHash methodology
8. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + parity harness 47/47)
9. `git log --oneline -10` — should show S2835 close cascade + S2834 close cascade + S2833 close cascade
10. Mint fresh pin `s2836-t3a-duplicate-content-audit`
11. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
12. **YAML SAMPLE SYNC-WITH-TEXT** — cycle 2 verification MUST re-read sample rows against text (S2835 Q7 lesson)
13. **Rigby writes workspace deliverables** — do NOT bypass with ORM-direct (S2835 new rule)
14. **DEFAULT: open T3a duplicate-content audit** per Group 2800 arc sequence
15. **All T3a findings inherit `schema_version: 1.1` from frontmatter** — no per-row tag
16. Consume T2's RENAMED map from `/tmp/t2_scan_out.json` (regenerate via `python tools/audit_2802_reference_graph.py` if lost) as free duplicate-candidate seed
17. **DO NOT execute any /docs/ file operations** during Group 2800 (per §5 non-goals)
18. **DO NOT modify §10.1 v1.1 schema** — locked at S2834; v1.2 recorded, NOT applied
19. **DO NOT audit T4-T5 corpora** — T3a is duplicate-content only
20. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary
21. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule
22. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary
23. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
24. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
25. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant
26. **DO NOT relax `include_superseded=False` default** — Chris D6 retrieval integrity rule (unchanged)
27. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
28. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
29. **DO NOT auto-adopt semantic default flips** (per S2821)
30. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
31. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
32. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
33. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
34. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
35. **DO NOT bypass Rigby for workspace deliverable creation** — S2835 new rule
36. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2836:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md`](docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md) — **S2835 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md`](docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md) — **S2835 ratification envelope**
4. [`docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`](docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md) — **RATIFIED T2 audit (~950 lines; §5.6 pre-clustering signal + §5.7 v1.2 future_trigger)**
5. [`docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`](docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md) — RATIFIED T1 (§4.1a T3a pre-scan hint)
6. [`docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`](docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md) — Group 2800 parent (D1-D9 RATIFIED S2833)
7. [`docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md`](docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md) — S2834 T1 handoff
8. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2b + §2c + §3 governance canonical
9. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc manifest (Group 2800 In-progress, 3/6)
10. [`tools/audit_2802_reference_graph.py`](tools/audit_2802_reference_graph.py) — T2 scanner (re-usable for follow-up)
11. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
12. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
