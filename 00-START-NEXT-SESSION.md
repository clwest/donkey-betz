# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2836 CLOSED (2026-07-19; picks up as S2837) — **GROUP 2800 T3a DUPLICATE-CONTENT AUDIT RATIFIED · SCHEMA V1.1 UNCHANGED · ESCALATE_TO_CHRIS DEFERRAL POLICY ESTABLISHED · T3b ORPHAN-AUDIT OPENS AT S2837**

**Refreshed 2026-07-19 (SESSION 2836 CLOSED — fresh session opened per S2835 pointer. Chris opened with "Please begin"; after seeing candidate menu (net-new engineering first per `feedback_engineering_bias_over_audit`, plus ratified T3a default from S2835 D-verdict) Chris picked the ratified default: open T3a. All S2836 open-protocol sanity checks green at open (pg15 started, backfill 0 mismatches, Pattern B/C canonical, parity harness 47/47 in 193.71s). Fresh pin `pa-90ea529a09234d57` (label `s2836-t3a-duplicate-content-audit`) minted at first-action. Claude built `tools/audit_2803a_duplicate_content.py` (5-word overlapping token shingles + inverted-index Jaccard scoring + containment_A/B for subset-overlap + T2 RENAMED-map pre-clustering seed from `/tmp/t2_scan_out.json` per T2 §5.6). Scanner ran in ~3s over 792 non-handoff in-scope files (789 `docs/**` + 3 root anchors); 7,246 raw pairs above Jaccard 0.10; top-2000 breakdown: 171 SESSION_819 intra-cluster (Jaccard 0.928-0.960) + 1,828 V2-pointer-stub-vs-V2-stub pairs (Jaccard ~0.86) + 1 substantive pair. Manual classification of top-40 substantive (V2-stub-filtered) pairs surfaced 15 non-cluster candidates: (a) PA_TOOLS_GAP_MAP_S2795/S2796 near-identical consecutive session snapshot; (b) SYSTEM_ARCHITECTURE_MAP vs SYSTEM_MAP arch-subdir needs-judgment; (c) CLAUDE_CONTEXT_SYSTEM_PACK vs SYSTEM_FULL_ACTIVATION_PLAN plans-subdir needs-judgment; (d) ENGINEERING_PLAYBOOK vs playbook_authoring_sessions load-bearing-both; (e) I-0100 phase acceptance + i0302 arc/phase-close sibling ratification envelopes load-bearing-both; (f) app-brief template family load-bearing-both; (g) cross-domain audit siblings load-bearing-both. Joint Claude+Rigby joint SIGN over 2 cycles reached agreement. Cycle 1 (substantive tool_runs — `repo_tool.read` DOC_LIFECYCLE §1 + 3 sample V2 stubs `AUDIO_GENERATION.md` + `DAVINCI_PHASE_3_PLAN.md` + `agents/INDEX.md` at lines 1-8 each + `repo_tool.search "SESSION_819"` in `core/management/commands/` **zero-match runner-independence proof** + `repo_tool.read` parent §4 T3a rubric text + `search_docs "schema v1.1 locked"` + `repo_tool.read` 2801 §10.1 + 2800 §4 T5 spec): 1 AGREE (Q1 V2-stub classification — DOC-POINTER-V2 stubs load-bearing per DOC_LIFECYCLE §1; 110-file scale is corpus-shape signal not consolidate signal) + 4 STRENGTHEN (Q2 SESSION_819 archive-vs-runner-fix ordering — folded runner-independence proof + parallel-track note; Q3 escalate_to_chris as own severity class — folded `needs-judgment` sub-classification for §2.4-§2.5 + §5.7 v1.2 Option C candidate; Q4 v1.2 schema mid-arc amendment — folded §5.3 acceptance criteria (i)-(iv); Q5 zoom-out — folded §5.6 T3a↔T5 boundary rule + `t5_may_override` annotations + scope-creep guard). Cycle 2 (substantive `repo_tool.read` of §2.1/§4.1/§2.10/§3/§2.4/§2.5/§5.3/§5.6/§5.7 with cited line numbers): Q6 AGREE (Q2 fold verified) + Q7 AGREE (Q3 fold + YAML sample sync-with-text per S2835 Q7 discipline — SYSTEM_ARCHITECTURE_MAP YAML sample added and matches §2.4 text severity) + Q8 AGREE (Q4 fold — all four (i)-(iv) present + deferral-default explicit) + Q9 AGREE (Q5 fold — §5.6 boundary + §5.7 Option C preference). Anti-rubber-stamp verified per `feedback_verify_rigby_tool_runs_before_trusting_sign` across both cycles; caught 3 real F-BLOCKING refinements. Chris D-verdict verbatim: `"Continue on but let's defer the two issue and any others like it until we have the /docs/ audit completed incase other issues come up."` **NEW ARC-LEVEL POLICY ESTABLISHED:** all `recommended_action: escalate_to_chris` rows across T3a/T3b/T4/T5 DEFER to arc close `2899` canonical summary, NOT resolved child-by-child; rationale = canonical designation judgment benefits from cross-child context that only emerges AFTER later children complete; `2899` MUST include consolidated "Chris judgment queue" for single-session workshop. Post-fold defect population: **0 P0** (§10.4(b) root-stability P0 gate NOT triggered) + **2 P1 classes / ~172 pair rows** (SESSION_819_SYSTEM_AUDIT_* 19-file cluster → archive to `docs/archive/2026-07/audits/session_819_snapshots/` with parallel runner-fix ticket; PA_TOOLS_GAP_MAP_S2795/S2796 → consolidate_into S2796) + **2 P2 needs-judgment classes DEFERRED to 2899** (SYSTEM_ARCH_MAP + CLAUDE_CONTEXT_SYSTEM_PACK) + **~1,800 P3 load-bearing-both pairs** (V2-stub cluster + playbook siblings + phase-doc siblings + app-brief template family + cross-domain audit siblings). §10.1 v1.1 schema UNCHANGED — three v1.2 candidates recorded across §5.3 (`coverage_content_dup` third axis; T2 §5.7 = 2nd witness; T3a §5.3 = 3rd witness of the coverage-split need) + §5.5 (`template_family` field for load-bearing-both) + §5.7 (`judgment_state: known | ambiguous` field for needs-judgment; Option C preferred as most additive) — all `future_trigger` for 2899 close; §5.3 (i)-(iv) acceptance criteria codified: purely additive + backward-compatible + parser-compat plan + documented deprecation path. **T3a↔T5 boundary rule adopted** (§5.6): T3a MUST NOT finalize disposition for T5-territory files (`docs/audits/**` + `docs/reports/**`); §4.1 rows carry `t5_may_override: YES`. Migration queue frozen; routed to future §3 execution arc post-2899 close. Ratification envelope authored at `docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md`. 2803a doc frontmatter updated status: proposed→ratified with full ratification block. Group 2800 arc registration in `docs/research/OPEN_ARCS.md` updated (3→4 of 6 shipped). **NEW MEMORY ESTABLISHED:** `feedback_arc_close_deferral_for_escalate_to_chris` — generalized pattern for multi-child audit arcs. `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. EIGHTY-SECOND close-cycle post-PLAYBOOK-7.4.4. Handoff: `docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md`.**

**S2836 ship (T3a child audit):**

| Focus | Artifact | Location |
|---|---|---|
| T3a child audit (792-file scan + top-40 manual classification + Rigby-folded findings) | New | `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md` (~944 lines, status ratified) |
| T3a scanner tool | New | `tools/audit_2803a_duplicate_content.py` |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 4/6 shipped) |
| S2836 handoff | New | `docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md` |
| S2837 pointer | Updated | THIS file — recommended default = T3b orphan-and-reachability audit |
| New memory | New | `feedback_arc_close_deferral_for_escalate_to_chris.md` + MEMORY.md index update |

**Arc state at S2836 close:**
- **Group 2800 /docs/ content audit arc**: **T3a RATIFIED at S2836 (schema v1.1 unchanged; escalate_to_chris deferral policy established; T3a↔T5 boundary rule adopted)**. **4 of 6 shipped** (parent + T1 + T2 + T3a). T3b opens at S2837. Migration queue frozen; routed to future §3 execution arc post-2899 close.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue DEFERRED. (Unchanged.)
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

---

## S2837 CANDIDATES

Per `feedback_engineering_bias_over_audit` — net-new engineering pivots listed first; ⭐ marks the S2836-derived ratified default (T3b next per Group 2800 sequence).

### A. Net-new engineering pivots (per engineering-bias rule)

1. **Colorado Phase 4 statute-citation quality pass** — Chris personal legal work; real capability
2. **BettingPage first-user trace** — Chris IS the first user; wire the real path end-to-end
3. **New spider / PA tool / Workspace tab** — pick a concrete gap

### B. ⭐ Ratified default — T3b orphan-and-reachability audit (Group 2800 fourth child)

Per Group 2800 arc sequence + S2836 close pointer.

**Recommended S2837 session shape:**

1. Fresh pin `s2837-t3b-orphan-reachability-audit`
2. Author `docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md`
3. Scope (per parent §4 T3b): ~792-file corpus (same as T3a); reverse-index build → for each file determine reachability from (a) CLAUDE.md anchor graph, (b) `docs/INDEX.md` autogen references, (c) `search_docs` corpus inclusion + top-K retrieval frequency for probe queries
4. **Pre-clustering signal from T3a §5.4:** 110-file V2-stub list from T3a §2.3 as reachable-only-from-search skip-list (V2 stubs are EXPECTED to be search-only-reachable per DOC_LIFECYCLE §1 link-rot prevention pattern; NOT orphan candidates)
5. **Pre-clustering signal from T2 §5.6:** basename RENAMED map still available at `/tmp/t2_scan_out.json`
6. Emit YAML findings per §10.1 v1.1 schema
7. Rigby joint SIGN + Chris D-verdict
8. **Any `escalate_to_chris` rows DEFER to 2899** per S2836 D-verdict new policy
9. Migration-queue routing to future §3 execution arc

**Anti-pattern to actively challenge (parent §4 T3b):** "unreachable = orphan = archive candidate." V2 pointer stubs are unreachable-except-via-search BY DESIGN. Classify severity (`unreachable-from-all-3-graphs` / `reachable-from-search-only` / `cited-but-search-invisible` / `cited-multi-graph-OK`) with V2-stub context.

### C. §7 anchor updates (Group 2700 deferred at S2832)

Bucket A auto-actionable ~1 session:
- PLATFORM_INVENTORY: add Group 2800 arc-opening + T1/T2/T3a close notes
- ARCHITECTURE_INDEX: register Group 2800 + T1/T2/T3a close
- CLAUDE.md: fix the P0 line 262 discord count in-place (root-stability §10.4 (b) gate from S2834 T1)

### D. Substrate / refactor (available if Chris pivots)

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + RAG Diagnostics tab (S2831) must produce identical `matched_patterns` post-refactor.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug hygiene:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
  - LucideIcon typing drift in `WorkspacePageNew.tsx` (P2 per T2 §2.8 Rigby Q3 fold)

**Recommended default (per Group 2800 sequence):** Open T3b orphan-and-reachability audit at S2837 as `2803b_docs_content_orphan_audit.md`.

---

## SESSION PIN — S2836 RETIRED (fresh mint required at S2837 open)

**Pin history (S2836):**

- `pa-90ea529a09234d57` (label `s2836-t3a-duplicate-content-audit`) minted at S2836 open turn 1; served as both session pin AND arc SIGN pin (2 cycles preserved for future arc reference); **retired at S2836 close (`force=true`, sixty-seventh consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2837 first-action fresh mint.

**S2837 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2836 handoff §3-§8 (Rigby SIGN 2-cycle status + Chris D-verdict + new deferral policy + T3a↔T5 boundary rule)
# Read S2836 ratification envelope §1-§7 (v1.1 schema unchanged + 3 v1.2 future_triggers + new governance patterns)
# Read 2803a T3a §5.4 (V2-stub skip-list pre-clustering signal for T3b) + §5.6 T3a↔T5 boundary + §5.7 needs_judgment v1.2 candidate
# Read 2800 parent scoping §4 T3b spec
# Read new memory feedback_arc_close_deferral_for_escalate_to_chris

# Sanity checks (must be green)
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

python manage.py session_lifecycle open --label s2837-t3b-orphan-reachability-audit
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2836 lessons to carry (also in handoff §7):**

1. **`escalate_to_chris` accumulates to arc close** in multi-child audit arcs — do NOT route mid-arc unless the deferral cost outweighs the cross-child-context benefit. First trigger corpus established at S2836 D-verdict.
2. **Rigby's grep-based zero-match** is a first-class runner-independence proof — cheaper and stronger than "we assume no dependency" language.
3. **Boundary rules between adjacent child audits** matter more than in-child rigor when arcs have territorial overlap (T3a↔T5 pattern).
4. **YAML sample sync-with-text discipline** (S2835 Q7 lesson) held — cycle 2 Q7 caught SYSTEM_ARCHITECTURE_MAP sample gap during review and it was folded pre-D-verdict.
5. **Three-witness threshold for schema amendment** now reached for `coverage` axis split. 2899 close is the natural amendment window; acceptance criteria (i)-(iv) apply.
6. **Rigby writes workspace deliverables** — second exercise of the S2835-established pattern; ORM-direct fallback only if Rigby's tool surface fails.
7. **DO NOT open T3b in same session as T3a ratification** (parent §5 sequential-child discipline).
8. **DO NOT execute any /docs/ file operations during Group 2800.**
9. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.** Locked at S2834; three v1.2 candidates recorded but NOT applied.
10. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.**
11. **DO NOT audit in-flight arc children** (per parent §7 anti-scope).
12. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary.
13. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule.
14. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary.
15. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract.
16. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure.
17. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant.
18. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred.
19. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards.
20. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary.
21. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4.
22. **DO NOT bypass Rigby for workspace deliverable creation** — S2835 rule; S2836 second exercise.
23. **DO NOT route T3b/T4/T5 `escalate_to_chris` rows mid-arc** — S2836 new policy; accumulate to 2899.
24. **DO NOT finalize disposition on T5-territory files (`docs/audits/**` + `docs/reports/**`)** in T3b (or any child) — T3a↔T5 boundary rule generalizes.

---

## Twin-pointer card

📁 **Repo — S2836 artifacts:**

- **T3a audit doc (RATIFIED):** `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md`
- **Handoff:** `docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md`
- **Scanner tool:** `tools/audit_2803a_duplicate_content.py`
- **Scanner output (raw top-2000):** `/tmp/t3a_dup_scan_out_full.json`
- **Scanner output (V2-stub-filtered):** `/tmp/t3a_dup_scan_substantive.json`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 4/6 shipped)
- **Rigby SIGN conversation:** `pa-90ea529a09234d57` (2 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2836 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: **Rigby creates** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via PA `deliverable_tool.create` per `feedback_rigby_writes_workspace_deliverables` (second exercise); category `governance`; `deliverable_type=ratification_record`. Claude routes explicit instruction post-merge with content body + envelope body + workspace ID + create spec; Claude verifies tool_runs + ORM cross-check.

---

## Current repository state (S2836 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2836 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged; 205 rules) |
| **Group 2800 arc state** | **T3a RATIFIED (S2836, schema v1.1 unchanged; escalate_to_chris deferral policy established); 4 of 6 shipped; T3b opens at S2837.** |
| Group 2700 arc state | ARC CLOSED (S2817); §3 target tree RATIFIED (S2832); §7 + §8 DEFERRED (unchanged) |
| Metadata layer | ✅ 0 mismatches (S2829 substrate intact) |
| Discovery-layer arc state | Pattern B/C/D shipped + Registry Step 1 DORMANT + UI canary tab shipped (S2818-S2831). Step 2 refactor deferred. |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| Content-audit schema | §10.1 v1.1 (locked at S2834; unchanged at S2836 — three v1.2 candidates recorded across §5.3/§5.5/§5.7 as future_triggers for 2899 close; acceptance criteria (i)-(iv) codified) |
| Chris escalation queue (deferred to 2899) | 2 rows from T3a (SYSTEM_ARCH_MAP + CLAUDE_CONTEXT_SYSTEM_PACK) — new policy per S2836 D-verdict; T3b/T4/T5 accumulate more |
| Chris escalation open (immediate) | none |
| S2837 recommended lean | Open T3b orphan-and-reachability audit as `2803b_docs_content_orphan_audit.md`. Alternatives available if Chris pivots. |
| Session pin | `pa-90ea529a09234d57` (retired at S2836 close, force=true, sixty-seventh consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2837 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2836 (post-cascade merge, eighty-second consecutive) |
| Next move | S2837 opens with T3b orphan-and-reachability audit; fresh pin `s2837-t3b-orphan-reachability-audit`. |

---

## Recommended session-open protocol (S2837, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2836 handoff §3-§8 (Rigby SIGN 2-cycle status + Chris D-verdict + new deferral policy + T3a↔T5 boundary rule)
4. Read S2836 ratification envelope §1-§7 (v1.1 schema unchanged + 3 v1.2 future_triggers + new governance patterns)
5. Read 2803a T3a §5.4 (V2-stub skip-list pre-clustering signal for T3b) + §5.6 (T3a↔T5 boundary) + §5.7 (needs_judgment v1.2 candidate)
6. Read 2800 parent scoping §4 T3b spec
7. Read new memory `feedback_arc_close_deferral_for_escalate_to_chris`
8. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + parity harness 47/47)
9. `git log --oneline -10` — should show S2836 close cascade + S2835 close cascade + S2834 close cascade
10. Mint fresh pin `s2837-t3b-orphan-reachability-audit`
11. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
12. **YAML SAMPLE SYNC-WITH-TEXT** — cycle 2 verification MUST re-read sample rows against text (S2835 Q7 lesson)
13. **Rigby writes workspace deliverables** — do NOT bypass with ORM-direct (S2835 rule; S2836 second exercise)
14. **`escalate_to_chris` DEFERS to 2899** — do NOT route T3b findings to Chris mid-arc (S2836 new policy)
15. **T3a↔T5 boundary generalizes** — T3b MUST NOT finalize disposition on T5-territory files
16. **DEFAULT: open T3b orphan-and-reachability audit** per Group 2800 arc sequence
17. **All T3b findings inherit `schema_version: 1.1` from frontmatter** — no per-row tag
18. Consume T3a's V2-stub skip-list (§2.3 cluster: 110 files) as reachable-only-from-search pre-classified list
19. Consume T2's RENAMED map from `/tmp/t2_scan_out.json` (regenerate via `python tools/audit_2802_reference_graph.py` if lost) as basename-collision seed
20. **DO NOT execute any /docs/ file operations** during Group 2800 (per §5 non-goals)
21. **DO NOT modify §10.1 v1.1 schema** — locked at S2834; three v1.2 candidates recorded, NOT applied
22. **DO NOT audit T4-T5 corpora** — T3b is orphan-and-reachability only
23. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary
24. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule
25. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary
26. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
27. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
28. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant
29. **DO NOT relax `include_superseded=False` default** — Chris D6 retrieval integrity rule (unchanged)
30. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
31. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
32. **DO NOT auto-adopt semantic default flips** (per S2821)
33. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
34. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
35. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
36. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
37. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
38. **DO NOT bypass Rigby for workspace deliverable creation** — S2835 rule; S2836 second exercise
39. **DO NOT route T3b `escalate_to_chris` rows mid-arc** — S2836 new policy; accumulate to 2899
40. **DO NOT finalize disposition on T5-territory files (`docs/audits/**` + `docs/reports/**`)** in T3b — T3a↔T5 boundary generalizes
41. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2837:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md`](docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md) — **S2836 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md`](docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md) — **S2836 ratification envelope**
4. [`docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`](docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md) — **RATIFIED T3a audit (~944 lines; §5.4 T3b pre-clustering signal + §5.6 T3a↔T5 boundary + §5.7 needs_judgment v1.2 candidate)**
5. [`docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`](docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md) — RATIFIED T2 (§5.6 basename map + §5.7 v1.2 future_trigger)
6. [`docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`](docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md) — RATIFIED T1 (§4.1a T3a pre-scan hint honored)
7. [`docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`](docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md) — Group 2800 parent (D1-D9 RATIFIED S2833)
8. [`docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md`](docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md) — S2835 T2 handoff
9. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §1 V2 pointer pattern (Q1 grounding) + §2b + §2c + §3 governance canonical
10. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc manifest (Group 2800 In-progress, 4/6)
11. [`tools/audit_2803a_duplicate_content.py`](tools/audit_2803a_duplicate_content.py) — T3a scanner (re-usable for follow-up)
12. [`tools/audit_2802_reference_graph.py`](tools/audit_2802_reference_graph.py) — T2 scanner (basename map for T3b)
13. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
14. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
