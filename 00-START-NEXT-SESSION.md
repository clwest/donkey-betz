# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2837 CLOSED (2026-07-19; picks up as S2838) — **GROUP 2800 T3b ORPHAN-AND-REACHABILITY AUDIT RATIFIED · SCHEMA V1.1 UNCHANGED · 77 ESCALATE ROWS ACCUMULATED TO 2899 · T4 HANDOFF AUDIT OPENS AT S2838**

**Refreshed 2026-07-19 (SESSION 2837 CLOSED — fresh session opened per S2836 pointer. Chris opened with "Please begin"; after seeing candidate menu (net-new engineering first per `feedback_engineering_bias_over_audit`, plus ratified T3b default from S2836 D-verdict) Chris picked the ratified default: open T3b. All S2837 open-protocol sanity checks green at open (pg15 started, backfill 0 mismatches, Pattern B/C canonical, parity harness 47/47 in 192.72s). Fresh pin `pa-7ebe273640e14691` (label `s2837-t3b-orphan-reachability-audit`) minted at first-action. Claude authored `tools/audit_2803b_orphan_reachability.py` (three-graph reachability scanner: CLAUDE.md link-BFS + docs/INDEX.md autogen refs + content.Document.file_path corpus + T3a §5.4 V2-stub direct-marker skip-list + T2 §5.6 RENAMED basename map). Scanner ran in ~2s over 793 non-handoff in-scope files: 491 anchor-reachable + 106 index-cited + 792 corpus-included. Zero unreachable-from-all-3-graphs files (positive tree-health signal). Sub-classification of 302 search-only-reachable via 8 `search_only_kind` values reduces escalate volume ~4x. Joint Claude+Rigby joint SIGN over 3 cycles reached agreement. Cycle 1 (5 questions, ~10 substantive tool_runs): Q1 STRENGTHEN (§1.5 grep-inflation warning — 633 file matches inflated ~4x vs 170 first-1KB scan) + Q2 STRENGTHEN (docs/research/tools/ narrowed to validation/ only — Rigby real leak-catch on campaign plan "awaiting Chris's review") + Q3+Q4 honest DISAGREE-pending (anti-rubber-stamp working) + Q5 truncated. Cycle 1b (Q3+Q4 evidence + Q5(a)): Q3 AGREE (`repo_tool.tree docs/topics depth=2` returned 21 topics + `repo_tool.search "collaboration-protocol"` zero anchor-graph citations) + Q4 AGREE (`repo_tool.read core/management/commands/build_docs_index.py:200` root_doc list `['CLAUDE.md', '00-START-NEXT-SESSION.md']` — README.md NOT listed + ORM `Document.objects.filter(file_path='README.md', is_active=True).exists()==False`) + Q5(a) STRENGTHEN future_trigger. Cycle 2: Q5(b) STRENGTHEN + Q5(c) STRENGTHEN. Cycle 3: 7/7 AGREE explicit with cited line numbers + Q5(d) STRENGTHEN future_trigger. Anti-rubber-stamp verified per `feedback_verify_rigby_tool_runs_before_trusting_sign` across all cycles (~30+ substantive tool_runs). Post-fold defect population: **0 P0** + **1 P1** (README.md cited-but-search-invisible — 1-line build_docs_index scope oversight OR codify-in-DOC_LIFECYCLE §1) + **76 P2 unclassified** (real escalate queue: 10 specs + 9 apps briefs + 9 initiatives capitalize-opportunity + 9 roadmap + 11 spokesperson + 6 non-eng playbooks + 5 designs + 5 narratives + 3 docs/topics COUNTER-SIGNAL (T1 dense-canonical claim INCOMPLETE — 3 of 21 topic files miss anchor graph) + 2 architecture + 2 tools + 1 decisions + 4 top-level docs/research/tools/tools_*.md) + **716 P3 keep_as_is** (~90.3%). §10.1 v1.1 schema UNCHANGED — three v1.2 candidates recorded: §5.3 `coverage_reachability` fourth axis (3rd witness) + §5.7 closed-arc sentinel marker/allowlist + §6.1(7) usage/salience metric. **T3a↔T5 boundary rule GENERALIZED** to T3b (§5.4): 151 T5-territory files carry `t5_may_override: YES`; cycle-2 Q5(c) added T5 workflow directive — 2805 SHOULD ingest `/tmp/t3b_orphan_scan_out.json`, not re-derive graphs. **`docs/INDEX.md` is strict subset of CLAUDE.md BFS** (0 index-only files) — §5.1 cross-cutting signal for 2899 discussion. Direct-marker V2-stub scan confirmed 170 V2 stubs (stronger than T3a §2.3 shingle-inference "110+" bound). Chris D-verdict verbatim: `"ratify T3b as-folded"`. **S2836 arc-close deferral policy carries over** (no new policy at S2837 — 77 escalate rows accumulate to 2899 workshop). Ratification envelope authored at `docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md`. 2803b doc frontmatter updated status: proposed→ratified with full ratification block. Group 2800 arc registration in `docs/research/OPEN_ARCS.md` updated (4→5 of 6 shipped). `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. EIGHTY-THIRD close-cycle post-PLAYBOOK-7.4.4. Handoff: `docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md`.**

**S2837 ship (T3b child audit):**

| Focus | Artifact | Location |
|---|---|---|
| T3b child audit (793-file scan + 3-graph reachability + 8-value sub-classification + 3 cycles of joint SIGN folds) | New | `docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md` (~1213 lines, status ratified) |
| T3b scanner tool | New | `tools/audit_2803b_orphan_reachability.py` (~570 lines) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 5/6 shipped) |
| S2837 handoff | New | `docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md` |
| S2838 pointer | Updated | THIS file — recommended default = T4 handoff citation-integrity + retrieval-harm audit |

**Arc state at S2837 close:**
- **Group 2800 /docs/ content audit arc**: **T3b RATIFIED at S2837 (schema v1.1 unchanged; deferral policy carries over; T3a↔T5 boundary generalized)**. **5 of 6 shipped** (parent + T1 + T2 + T3a + T3b). T4 opens at S2838. Migration queue frozen; routed to future §3 execution arc post-2899 close.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue DEFERRED. (Unchanged.)
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

---

## S2838 CANDIDATES

Per `feedback_engineering_bias_over_audit` — net-new engineering pivots listed first; ⭐ marks the S2837-derived ratified default (T4 next per Group 2800 sequence).

### A. Net-new engineering pivots (per engineering-bias rule)

1. **Colorado Phase 4 statute-citation quality pass** — Chris personal legal work; real capability
2. **BettingPage first-user trace** — Chris IS the first user; wire the real path end-to-end
3. **New spider / PA tool / Workspace tab** — pick a concrete gap
4. **README.md corpus-inclusion fix** (T3b P1 finding, `same_pr_actionable`) — 1-line build_docs_index scope edit + cascade; would resolve the 1 P1 in isolation from the 2899 workshop

### B. ⭐ Ratified default — T4 handoff citation-integrity + retrieval-harm audit (Group 2800 fifth child)

Per Group 2800 arc sequence + S2837 close pointer.

**Recommended S2838 session shape:**

1. Fresh pin `s2838-t4-handoff-citation-integrity-audit`
2. Author `docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md`
3. Scope (per parent §4 T4): **1058** `docs/handoffs/*.md` files; per-file content NOT reviewed except as noted in sub-loop (c)
4. Method:
   - **(a) Citation-graph:** `grep` in-corpus for citations of the form `docs/handoffs/SESSION_NNNN*`; measure hit rate + decay curve
   - **(b) Citation-integrity spot-check:** 10-doc sample per Group 2700 T5 substrate concern — do old `[docs/handoffs/SESSION_NNN.md#K]` fragment citations still resolve after any post-1143 chunk-ID resets?
   - **(c) Retrieval-harm / staleness-banner sub-loop:** for the top-K handoffs that surface in `search_docs` results for common operational queries (e.g. `"in-progress arc"`, `"how many spiders"`), inspect whether the handoff's claim-context is stale — deliverable = narrow list of handoffs recommended for DOC-POINTER-V1 stats-drift banner
5. **Pre-clustering signal from T3b §5.4 (T5 workflow directive generalized):** T4 SHOULD ingest `/tmp/t3b_orphan_scan_out.json` at authoring for handoff reachability signal — NOT re-derive
6. **Pre-clustering signal from T2 §5.6:** basename RENAMED map still available at `/tmp/t2_scan_out.json`
7. Emit YAML findings per §10.1 v1.1 schema
8. Rigby joint SIGN + Chris D-verdict
9. **Any `escalate_to_chris` rows DEFER to 2899** per S2836 policy (still in effect)
10. Migration-queue routing to future §3 execution arc

**Anti-pattern to actively challenge (parent §4 T4):** "handoff content review" is quarantined — T4 is CITATION-INTEGRITY + RETRIEVAL-HARM only. Do NOT walk all 1058 handoffs for content quality; the terminal-write-once discipline holds.

### C. §7 anchor updates (Group 2700 deferred at S2832)

Bucket A auto-actionable ~1 session:
- PLATFORM_INVENTORY: add Group 2800 arc-opening + T1/T2/T3a/T3b close notes
- ARCHITECTURE_INDEX: register Group 2800 + T1/T2/T3a/T3b close
- CLAUDE.md: fix the P0 line 262 discord count in-place (root-stability §10.4 (b) gate from S2834 T1)

### D. Substrate / refactor (available if Chris pivots)

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + RAG Diagnostics tab (S2831) must produce identical `matched_patterns` post-refactor.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug hygiene:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
  - LucideIcon typing drift in `WorkspacePageNew.tsx` (P2 per T2 §2.8 Rigby Q3 fold)

**Recommended default (per Group 2800 sequence):** Open T4 handoff citation-integrity + retrieval-harm audit at S2838 as `2804_docs_content_handoff_audit.md`.

---

## SESSION PIN — S2837 RETIRED (fresh mint required at S2838 open)

**Pin history (S2837):**

- `pa-7ebe273640e14691` (label `s2837-t3b-orphan-reachability-audit`) minted at S2837 open turn 1; served as both session pin AND arc SIGN pin (3 cycles preserved for future arc reference); **retired at S2837 close (`force=true`, sixty-eighth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2838 first-action fresh mint.

**S2838 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2837 handoff §3-§7 (Rigby SIGN 3-cycle status + Chris D-verdict + T3a↔T5 generalization + lessons for T4)
# Read S2837 ratification envelope §1-§7 (v1.1 schema unchanged + 3 v1.2 future_triggers + T5 workflow directive)
# Read 2803b T3b §5.4 (T5 workflow directive — T4 pre-clustering signal to ingest) + §5.7 (broad-prefix risk) + §6.1 (limitations)
# Read 2800 parent scoping §4 T4 spec

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

python manage.py session_lifecycle open --label s2838-t4-handoff-citation-integrity-audit
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2837 lessons to carry (also in handoff §7):**

1. **Cross-child pre-clustering consumption is first-class pattern** — T3a consumed T2 §5.6 RENAMED map; T3b consumed T3a §5.4 V2-stub direct-marker scan. T4 SHOULD consume T3b's `/tmp/t3b_orphan_scan_out.json` for handoff reachability signal (T3b §5.4 T5 workflow directive generalizes).
2. **Anti-rubber-stamp holds under pressure.** Rigby declined Q3+Q4 rather than fake-AGREE — extend the discipline: when Rigby says "I did not complete the required tool runs," route again with evidence + require independent verification.
3. **Sub-classification against known-benign patterns is ~4x escalate volume reduction.** T4 SHOULD sub-classify handoff citations by staleness + retrieval-harm class before flooding Chris judgment queue.
4. **Direct-marker scan > shingle-pair-inference for stub detection.** Prefer direct signal detection where feasible.
5. **Zoom-out ask still catches issues cycle 1 doesn't.** Continue including at least one zoom-out ask per SIGN cycle per `feedback_zoom_out_ask_per_rigby_sign`.
6. **Rigby writes workspace deliverables** — third exercise of the S2835-established pattern; ORM-direct fallback only if Rigby's tool surface fails.
7. **DO NOT open T4 in same session as T3b ratification** (parent §5 sequential-child discipline).
8. **DO NOT execute any /docs/ file operations during Group 2800.**
9. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.** Locked at S2834; three v1.2 candidates recorded but NOT applied (now 4 candidates counting T3b §5.3 coverage_reachability).
10. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.**
11. **DO NOT audit in-flight arc children** (per parent §7 anti-scope).
12. **DO NOT walk all 1058 handoffs for content quality** — T4 is CITATION-INTEGRITY + RETRIEVAL-HARM only; terminal-write-once discipline holds.
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
23. **DO NOT bypass Rigby for workspace deliverable creation** — S2835 rule; S2837 third exercise.
24. **DO NOT route T4/T5 `escalate_to_chris` rows mid-arc** — S2836 policy; accumulate to 2899.
25. **DO NOT finalize disposition on T5-territory files (`docs/audits/**` + `docs/reports/**`)** in T4 — T3a↔T5 boundary rule generalized (T3b §5.4 fold).

---

## Twin-pointer card

📁 **Repo — S2837 artifacts:**

- **T3b audit doc (RATIFIED):** `docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md`
- **Handoff:** `docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md`
- **Scanner tool:** `tools/audit_2803b_orphan_reachability.py`
- **Scanner output:** `/tmp/t3b_orphan_scan_out.json`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 5/6 shipped)
- **Rigby SIGN conversation:** `pa-7ebe273640e14691` (3 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2837 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: **Rigby creates** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via PA `deliverable_tool.create` per `feedback_rigby_writes_workspace_deliverables` (third exercise); category `governance`; `deliverable_type=ratification_record`. Claude routes explicit instruction post-merge with content body + envelope body + workspace ID + create spec; Claude verifies tool_runs + ORM cross-check.

---

## Current repository state (S2837 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2837 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged; 205 rules) |
| **Group 2800 arc state** | **T3b RATIFIED (S2837, schema v1.1 unchanged; deferral policy carries over from S2836); 5 of 6 shipped; T4 opens at S2838.** |
| Group 2700 arc state | ARC CLOSED (S2817); §3 target tree RATIFIED (S2832); §7 + §8 DEFERRED (unchanged) |
| Metadata layer | ✅ 0 mismatches (S2829 substrate intact) |
| Discovery-layer arc state | Pattern B/C/D shipped + Registry Step 1 DORMANT + UI canary tab shipped (S2818-S2831). Step 2 refactor deferred. |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| Content-audit schema | §10.1 v1.1 (locked at S2834; unchanged at S2837 — four v1.2 candidates recorded across T2 §5.7 + T3a §5.3/§5.5/§5.7 + T3b §5.3/§5.7/§6.1 as future_triggers for 2899 close; acceptance criteria (i)-(iv) codified at T3a §5.3) |
| Chris escalation queue (deferred to 2899) | 77 rows total (T3a 2 + T3b 75) — arc-close deferral policy; T4/T5 accumulate more |
| Chris escalation open (immediate) | none |
| S2838 recommended lean | Open T4 handoff citation-integrity + retrieval-harm audit as `2804_docs_content_handoff_audit.md`. Alternatives available if Chris pivots. |
| Session pin | `pa-7ebe273640e14691` (retired at S2837 close, force=true, sixty-eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2838 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2837 (post-cascade merge, eighty-third consecutive) |
| Next move | S2838 opens with T4 handoff citation-integrity + retrieval-harm audit; fresh pin `s2838-t4-handoff-citation-integrity-audit`. |

---

## Reference documents

Ordered by frequency of use at S2838:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md`](docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md) — **S2837 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md`](docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md) — **S2837 ratification envelope**
4. [`docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md`](docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md) — **RATIFIED T3b audit (~1213 lines; §5.4 T3a↔T5 boundary generalized + T5 workflow directive; §5.7 broad-prefix risk future_trigger; §6.1 limitations)**
5. [`docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`](docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md) — RATIFIED T3a
6. [`docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`](docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md) — RATIFIED T2
7. [`docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`](docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md) — RATIFIED T1
8. [`docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`](docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md) — Group 2800 parent (D1-D9 RATIFIED S2833)
9. [`docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md`](docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md) — S2836 T3a handoff
10. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §1 V2 pointer pattern + §2b + §2c + §3 governance canonical
11. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc manifest (Group 2800 In-progress, 5/6)
12. [`tools/audit_2803b_orphan_reachability.py`](tools/audit_2803b_orphan_reachability.py) — T3b scanner (reusable for follow-up + T4 pre-clustering)
13. [`tools/audit_2803a_duplicate_content.py`](tools/audit_2803a_duplicate_content.py) — T3a scanner
14. [`tools/audit_2802_reference_graph.py`](tools/audit_2802_reference_graph.py) — T2 scanner (basename map for T4)
15. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
16. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
