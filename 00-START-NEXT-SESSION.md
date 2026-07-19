# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2838 CLOSED (2026-07-19; picks up as S2839) — **GROUP 2800 T4 HANDOFF CITATION-INTEGRITY + RETRIEVAL-HARM AUDIT RATIFIED · SCHEMA V1.1 UNCHANGED · 99 ESCALATE ROWS ACCUMULATED TO 2899 · 6/6 GROUP 2800 SHIPPED · T5 REPORTS+AUDITS TRIAGE OPENS AT S2839**

**Refreshed 2026-07-19 (SESSION 2838 CLOSED — fresh session opened per S2837 pointer. Chris opened with "Please begin"; after seeing candidate menu (net-new engineering first per `feedback_engineering_bias_over_audit`, plus ratified T4 default from S2837 D-verdict) Chris picked the ratified default: open T4. All S2838 open-protocol sanity checks green at open (pg15 started, backfill 0 mismatches, Pattern B/C canonical, parity harness 47/47 in 194.68s). Fresh pin `pa-683fb793ab944cd0` (label `s2838-t4-handoff-citation-integrity-audit`) minted at first-action. Claude authored `tools/audit_2804_handoff_citation_integrity.py` (~550 lines; three sub-loops consuming T2 §5.6 citation-edge substrate + T3b §5.4 citing-doc reachability substrate). Scanner ran in ~3s over 1061 handoff files. Findings: ZERO P0 (§10.4(b) root-stability gate NOT triggered). Handoff citation surface small (145 path-form + 17 short-form = 162 edges); 90.3% of citations trace to anchor-reachable canonical docs; 89.6% of handoffs never cited (write-once-terminal healthy state); decay curve peaks at S2500-2999 (26.8%) and S1000-1499 (17.7%). **Sub-loop (b) EMPIRICAL FALSIFICATION** of parent §4 T4 hypothesis: ZERO `#K` chunk-ID form citations in corpus; only 3 fragment-form edges total; post-S1143 chunk-ID reset concern UNFOUNDED at current corpus state. **Sub-loop (c) retrieval-harm banner candidates: 13 unique handoffs** (12 from initial 10-probe set + SESSION_2759 added at cycle-2 Q2 fold per Rigby's proposed "recycle-all/stale" ops-recovery probe with `search_docs` verification). Joint Claude+Rigby SIGN over 3 cycles reached agreement. Cycle 1 (5 questions, ~10 substantive tool_runs): 2 STRENGTHEN + 2 RE-ROUTE (Q3/Q4 blocked on Rigby's /tmp JSON access; Claude verified via shell) + Q5 truncated tail. Cycle 1b (Claude shell verification for Q1/Q3/Q4): 5/5 T2 short-form BROKEN_404 samples confirmed prose LINK_FORM: False; no clean rank elbow (rank 1-3 mean 0.5437 vs rank 4-8 mean 0.5276); 1061 handoff count verified with +3 delta explained via git log. Cycle 2 (evidence route + Q5 completion): 4 AGREE/STRENGTHEN with actionable fold directives + Q5 STRENGTHEN completed (keep T4 as-is + record post-2899 follow-on operator-time-loss audit thread proposal as future_trigger). **Cycle 3 (clean AGREE-check with fold verification): 5 AGREE + 3 STRENGTHEN — Rigby caught real errors post-cycle-2-narrative-stability:** §1.1 table STILL had leftover "+3 drift" phrasing after cycle-2 correction; §5.7a needed explicit scope-creep guardrail sentence ("This doc makes NO instrumentation request"); §3.3 vs §5.5 math inconsistency (99 vs 98) + envelope §8 accumulation math claimed "T1: 3" without evidence. All 3 cycle-3 STRENGTHEN folds landed before D-verdict routing. Anti-rubber-stamp discipline HELD in cycle 3 (not just cycles 1-2) — Rigby's tool-grounded verification with 8+ `repo_tool.read_file` + `repo_tool.search` operations independently caught Claude's T1:3 overclaim; corrected to authoritative S2837 pointer numbers (T1+T2=0 to accumulation, T3a=2, T3b=75, T4=22, total 99). Chris D-verdict verbatim: `"Go for it!"` (also thanked Claude for reading Rigby's full responses per `feedback_read_full_rigby_response_not_just_tail` — the S2837 rule paid off catching Q5 truncated body via `sed '/--- Tool Runs (verbose) ---/,$d'` filter). **S2836 arc-close deferral policy carries over** (no new policy at S2838 — 99 total escalate rows accumulate to 2899 workshop). **§5.7a follow-on audit thread proposal recorded** as future_trigger for post-2899 evaluation (behavioral operator-time-loss measurement is orthogonal to T4's structural shape; two candidate substrate approaches recorded with explicit scope-creep guardrail). **Cross-child pre-clustering pattern reaches three-trigger corroboration** (T3a←T2, T3b←T3a+T2, T4←T2+T3b): candidate for Playbook v3 codification. **`null_result` finding class two-trigger corroboration** (T3b §2.1 + T4 §2.4): candidate for Playbook §11.3 template. Ratification envelope authored at `docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md`. 2804 doc frontmatter updated status: proposed→ratified with full ratification block. Group 2800 arc registration in `docs/research/OPEN_ARCS.md` updated (5→6 of 6 shipped). `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. EIGHTY-FOURTH close-cycle post-PLAYBOOK-7.4.4. Handoff: `docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md`.**

**S2838 ship (T4 child audit):**

| Focus | Artifact | Location |
|---|---|---|
| T4 child audit (1061-file scan + 3 sub-loops + 3 cycles of joint SIGN folds) | New | `docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md` (~1022 lines, status ratified) |
| T4 scanner tool | New | `tools/audit_2804_handoff_citation_integrity.py` (~550 lines) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 6/6 shipped) |
| S2838 handoff | New | `docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md` |
| S2839 pointer | Updated | THIS file — recommended default = T5 reports+audits triage audit |

**Arc state at S2838 close:**
- **Group 2800 /docs/ content audit arc**: **T4 RATIFIED at S2838 (schema v1.1 unchanged; deferral policy carries over; cross-child pre-clustering pattern three-trigger corroborated)**. **6 of 6 shipped** (parent + T1 + T2 + T3a + T3b + T4). T5 opens at S2839. 2899 canonical summary follows T5 close. Migration queue frozen; routed to future §3 execution arc post-2899 close.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue DEFERRED. (Unchanged.)
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

---

## S2839 CANDIDATES

Per `feedback_engineering_bias_over_audit` — net-new engineering pivots listed first; ⭐ marks the S2838-derived ratified default (T5 next per Group 2800 sequence).

### A. Net-new engineering pivots (per engineering-bias rule)

1. **Colorado Phase 4 statute-citation quality pass** — Chris personal legal work; real capability
2. **BettingPage first-user trace** — Chris IS the first user; wire the real path end-to-end
3. **New spider / PA tool / Workspace tab** — pick a concrete gap
4. **README.md corpus-inclusion fix** (T3b P1 finding, `same_pr_actionable`) — 1-line `build_docs_index` scope edit + cascade; would resolve the 1 P1 in isolation from the 2899 workshop
5. **SESSION_2759 stale-daphne handoff banner** (T4 §2.5 rank-1 candidate for "recycle-all/stale" ops-recovery probe) — same-PR banner marker fix if Chris pivots to substrate

### B. ⭐ Ratified default — T5 reports+audits triage audit (Group 2800 sixth child)

Per Group 2800 arc sequence + S2838 close pointer.

**Recommended S2839 session shape:**

1. Fresh pin `s2839-t5-reports-audits-triage-audit`
2. Author `docs/research/domains/docs_content_audit/2805_docs_content_reports_audits_triage.md`
3. Scope (per parent §4 T5): `docs/audits/**` (93 files) + `docs/audit-2026/**` (15 files) + `docs/audit/**` (10 files) + 20 root-level `*_AUDIT.md` + **`docs/reports/**` (33 files — cycle-2 Q3 STRENGTHEN)**. Includes the 19 `SESSION_819_SYSTEM_AUDIT_*` files currently untracked in git status.
4. Method:
   - Classify each file by (a) one-shot session snapshot vs standing reference; (b) referenced from anchor graph vs orphan; (c) content-stale vs still-valid; (d) whether existing V1/V2 pointer already tells the right story
   - **Pre-clustering signal from T3b §5.4 (T5 workflow directive generalized):** T5 SHOULD ingest `/tmp/t3b_orphan_scan_out.json` — 151 T5-territory files already carry `t5_may_override: YES` classification; NOT re-derive reachability graphs
   - **Pre-clustering signal from T4:** `/tmp/t4_handoff_audit_out.json` provides handoff-related citation-graph context if T5 encounters `SESSION_*_AUDIT.md` handoff-side artifacts
5. Emit YAML findings per §10.1 v1.1 schema
6. Rigby joint SIGN + Chris D-verdict
7. **Any `escalate_to_chris` rows DEFER to 2899** per S2836 policy (still in effect); T5 rows likely dominant (T3b 41 + T3a 32 t5_territory rows already flagged)
8. Migration-queue routing to future §3 execution arc

**Anti-pattern to actively challenge (parent §4 T5):** "audit content review" is quarantined — T5 is TRIAGE only (classify + recommend disposition). Do NOT walk every audit file for content quality; classification against the four axes is the load-bearing measurement.

**T5 dependencies on T4:**
- No hard dependency; T5 is structurally the last thread, closing the arc for 2899
- Soft dependency: if T5 encounters a `SESSION_NNN_AUDIT.md` file that appears in T4 §2.5 banner candidates, treat T4's banner recommendation as one input to T5's disposition (not authoritative)

### C. §7 anchor updates (Group 2700 deferred at S2832)

Bucket A auto-actionable ~1 session:
- PLATFORM_INVENTORY: add Group 2800 arc-opening + T1/T2/T3a/T3b/T4 close notes
- ARCHITECTURE_INDEX: register Group 2800 + T1/T2/T3a/T3b/T4 close
- CLAUDE.md: fix the P0 line 262 discord count in-place (root-stability §10.4 (b) gate from S2834 T1)

### D. Substrate / refactor (available if Chris pivots)

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + RAG Diagnostics tab (S2831) must produce identical `matched_patterns` post-refactor.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug hygiene:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
  - LucideIcon typing drift in `WorkspacePageNew.tsx` (P2 per T2 §2.8 Rigby Q3 fold)

**Recommended default (per Group 2800 sequence):** Open T5 reports+audits triage audit at S2839 as `2805_docs_content_reports_audits_triage.md`.

---

## SESSION PIN — S2838 RETIRED (fresh mint required at S2839 open)

**Pin history (S2838):**

- `pa-683fb793ab944cd0` (label `s2838-t4-handoff-citation-integrity-audit`) minted at S2838 open turn 1; served as both session pin AND arc SIGN pin (3 cycles preserved for future arc reference); **retired at S2838 close (`force=true`, sixty-ninth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2839 first-action fresh mint.

**S2839 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2838 handoff §3-§7 (Rigby SIGN 3-cycle status + Chris D-verdict + cycle-3 STRENGTHEN catches + lessons for T5)
# Read S2838 ratification envelope §1-§7 (v1.1 schema unchanged + four v1.2 future_triggers + cross-child pre-clustering three-trigger)
# Read 2804 T4 §5.7a (follow-on audit thread proposal + scope-creep guardrail) + §6.1 (limitations) + §2.5 (retrieval-harm banner candidates)
# Read 2800 parent scoping §4 T5 spec

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

python manage.py session_lifecycle open --label s2839-t5-reports-audits-triage-audit
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2838 lessons to carry (also in handoff §7):**

1. **Cross-child pre-clustering consumption is now three-trigger corroborated** — T3a←T2, T3b←T3a+T2, T4←T2+T3b. T5 SHOULD consume `/tmp/t3b_orphan_scan_out.json` for `t5_may_override: YES` pre-classified rows (T3b §5.4 T5 workflow directive generalized) + potentially `/tmp/t4_handoff_audit_out.json` for handoff-adjacent audit-file signal.
2. **Anti-rubber-stamp holds under cycle 3 pressure.** Rigby's tool-grounded verification in cycle 3 (not just cycles 1-2) caught 3 real STRENGTHEN issues (§1.1 drift leftover, §5.7a scope-creep, §8 T1:3 overclaim) after "cycle 2 folded" narrative had stabilized. T5 SHOULD run a 3-cycle floor for SIGN — cycle 3 clean-check is NOT ceremonial.
3. **Read full Rigby response, not just tool_runs tail.** `feedback_read_full_rigby_response_not_just_tail` established at S2837 close paid off at S2838 cycle 1 — Q5 body was truncated at the tail; `sed '/--- Tool Runs (verbose) ---/,$d'` filter caught the full prose body above the separator. T5 SHOULD maintain the discipline.
4. **Empirical falsification is a first-class finding.** T4 §2.4 (0 chunk-ID citations) is now second null-result finding in Group 2800 (T3b §2.1 was first — 0 unreachable-from-all-3-graphs). If T5 encounters null results (e.g., "0 T5-territory files are anchor-orphaned"), report as positive findings.
5. **Scope-creep guardrails belong in the audit doc itself.** T4 §5.7a follow-on audit proposal only became safe to include AFTER cycle-3 Q7 STRENGTHEN forced the "makes NO instrumentation request" guardrail sentence. If T5 records any future_trigger substrate proposal, include the guardrail up front.
6. **Rigby writes workspace deliverables** — fourth exercise of the S2835-established pattern; ORM-direct fallback only if Rigby's tool surface fails.
7. **DO NOT open T5 in same session as T4 ratification** (parent §5 sequential-child discipline).
8. **DO NOT execute any /docs/ file operations during Group 2800.**
9. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.** Locked at S2834; now FOUR v1.2 candidates recorded (T2 §5.7 coverage split + T3a §5.3/§5.5/§5.7 + T3b §5.3/§5.7/§6.1 + T4 §2.6 citation_style + T4 §5.7 canonical probe-query set + T4 §5.4 null_result finding class) — still NOT applied.
10. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.**
11. **DO NOT audit in-flight arc children** (per parent §7 anti-scope).
12. **DO NOT walk all 1061 handoffs for content quality** — T4 completed CITATION-INTEGRITY + RETRIEVAL-HARM only; terminal-write-once discipline holds through T5 + 2899.
13. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary.
14. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule.
15. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary.
16. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract.
17. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure.
18. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant.
19. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred.
20. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards.
21. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary.
22. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4.
23. **DO NOT bypass Rigby for workspace deliverable creation** — S2835 rule; S2838 fourth exercise.
24. **DO NOT route T5 `escalate_to_chris` rows mid-arc** — S2836 policy; accumulate to 2899.
25. **DO NOT re-derive T2/T3b/T4 substrate in T5** — ingest `/tmp/*_scan_out.json` per generalized workflow directive.
26. **DO NOT open post-2899 follow-on audit thread without Chris arc-open authorization** (T4 §5.7a scope-creep guardrail).

---

## Twin-pointer card

📁 **Repo — S2838 artifacts:**

- **T4 audit doc (RATIFIED):** `docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md`
- **Handoff:** `docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md`
- **Scanner tool:** `tools/audit_2804_handoff_citation_integrity.py`
- **Scanner output:** `/tmp/t4_handoff_audit_out.json`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 6/6 shipped)
- **Rigby SIGN conversation:** `pa-683fb793ab944cd0` (3 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2838 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: **Rigby creates** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via PA `deliverable_tool.create` per `feedback_rigby_writes_workspace_deliverables` (fourth exercise); category `governance`; `deliverable_type=ratification_record`. Claude routes explicit instruction post-merge with content body + envelope body + workspace ID + create spec; Claude verifies tool_runs + ORM cross-check.

---

## Current repository state (S2838 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2838 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged; 205 rules) |
| **Group 2800 arc state** | **T4 RATIFIED (S2838, schema v1.1 unchanged; deferral policy carries over from S2836; cross-child pre-clustering three-trigger corroborated); 6 of 6 shipped; T5 opens at S2839; 2899 canonical summary follows T5.** |
| Group 2700 arc state | ARC CLOSED (S2817); §3 target tree RATIFIED (S2832); §7 + §8 DEFERRED (unchanged) |
| Metadata layer | ✅ 0 mismatches (S2829 substrate intact) |
| Discovery-layer arc state | Pattern B/C/D shipped + Registry Step 1 DORMANT + UI canary tab shipped (S2818-S2831). Step 2 refactor deferred. |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| Content-audit schema | §10.1 v1.1 (locked at S2834; unchanged at S2838 — FOUR v1.2 candidates recorded across T2 §5.7 + T3a §5.3/§5.5/§5.7 + T3b §5.3/§5.7/§6.1 + T4 §2.6/§5.7/§5.4 as future_triggers for 2899 close; acceptance criteria (i)-(iv) codified at T3a §5.3) |
| Chris escalation queue (deferred to 2899) | 99 rows total (T3a 2 + T3b 75 + T4 22 — 6 P1 path-form + 13 P2 retrieval-harm + 3 P2 fragment-form) — arc-close deferral policy; T5 will accumulate more |
| Chris escalation open (immediate) | none |
| S2839 recommended lean | Open T5 reports+audits triage audit as `2805_docs_content_reports_audits_triage.md`. Alternatives available if Chris pivots. |
| Session pin | `pa-683fb793ab944cd0` (retired at S2838 close, force=true, sixty-ninth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2839 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2838 (post-cascade merge, eighty-fourth consecutive) |
| Next move | S2839 opens with T5 reports+audits triage audit; fresh pin `s2839-t5-reports-audits-triage-audit`. |

---

## Reference documents

Ordered by frequency of use at S2839:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md`](docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md) — **S2838 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md`](docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md) — **S2838 ratification envelope**
4. [`docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md`](docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md) — **RATIFIED T4 audit (~1022 lines; §5.7a follow-on proposal + scope-creep guardrail; §2.5 13 banner candidates; §2.4 chunk-ID null_result)**
5. [`docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md`](docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md) — RATIFIED T3b (T5 pre-clustering source)
6. [`docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`](docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md) — RATIFIED T3a
7. [`docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`](docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md) — RATIFIED T2
8. [`docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`](docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md) — RATIFIED T1
9. [`docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`](docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md) — Group 2800 parent (D1-D9 RATIFIED S2833)
10. [`docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md`](docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md) — S2837 T3b handoff
11. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §1 V2 pointer pattern + §2b + §2c + §3 governance canonical
12. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc manifest (Group 2800 In-progress, 6/6)
13. [`tools/audit_2804_handoff_citation_integrity.py`](tools/audit_2804_handoff_citation_integrity.py) — T4 scanner (reusable for follow-up + T5 pre-clustering signal for handoff-adjacent audit files)
14. [`tools/audit_2803b_orphan_reachability.py`](tools/audit_2803b_orphan_reachability.py) — T3b scanner (T5 primary pre-clustering source per §5.4 T5 workflow directive)
15. [`tools/audit_2803a_duplicate_content.py`](tools/audit_2803a_duplicate_content.py) — T3a scanner
16. [`tools/audit_2802_reference_graph.py`](tools/audit_2802_reference_graph.py) — T2 scanner (basename map)
17. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
18. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
