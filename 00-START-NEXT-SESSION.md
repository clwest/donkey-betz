# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2833 CLOSED (2026-07-19; picks up as S2834) — **GROUP 2800 /docs/ CONTENT AUDIT PARENT SCOPING RATIFIED · T1 ANCHOR CONTENT AUDIT OPENS AT S2834**

**Refreshed 2026-07-19 (SESSION 2833 CLOSED — fresh session opened per S2832 pointer. Chris opened with "Please begin"; after seeing candidate menu picked the S2832 D-verdict default: open file-content audit arc. All S2833 open-protocol sanity checks green at open (pg15 started, backfill 0 mismatches, Pattern B/C canonical, S2831 endpoint, parity harness 47/47). Fresh pin `pa-cc1dbcb7d18c4502` (label `s2833-docs-content-audit-scoping`) minted. Claude drafted parent scoping doc D1-D9 at `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md` (306 lines, 11 sections). Joint Rigby SIGN ran 3 cycles with anti-rubber-stamp discipline verified across all cycles (substantive `repo_tool` + `search_docs` in every verdict). Cycle 1: STRENGTHEN split T3→T3a/T3b + STRENGTHEN add T4 retrieval-harm banner sub-loop; 3 honest CONDITIONAL for Q3/Q4/Q5. Cycle 2: STRENGTHEN move `docs/reports/` into T5 + DISAGREE session-count 4→≥6 + STRENGTHEN add §10 machine-consumable per-file YAML classification schema + cross-arc consumption contract. Cycle 3: 3/5 refinements verified via read; 2/5 unverified due to display truncation (verified locally); Rigby carry-forward fold `future_trigger` addressed inline in §10.1. Chris D-verdict: **"ratify D1-D9, open T1 next session"**. Ratification envelope authored at `docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md`. 2800 doc frontmatter updated status: proposed→ratified with full ratification block. Group 2800 registered in `docs/research/OPEN_ARCS.md` In-progress section. Merged as PR #NNNN, SHA `TBD` (filled at cascade merge). `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. SEVENTY-NINTH close-cycle post-PLAYBOOK-7.4.4. Handoff: `docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md`.**

**S2833 ship (parent-scoping-only session):**

| Focus | Artifact | Location |
|---|---|---|
| Group 2800 parent scoping doc | New | `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md` (D1-D9 locked, status ratified) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 added to In-progress) |
| S2833 handoff | New | `docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md` |
| S2834 pointer | Updated | THIS file — recommended default = T1 anchor content audit |

**Arc state at S2833 close:**
- **Group 2800 /docs/ content audit arc**: **PARENT SCOPING RATIFIED at S2833** (D1-D9 locked). T1 opens at S2834. 6 threads total; ≥6-session estimate; per-file YAML output schema locked.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue DEFERRED. (Unchanged.)
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

---

## S2834 CANDIDATES

### ⭐ Recommended default direction — **T1 anchor & canonical-doc content audit** (per Chris D-verdict S2833)

Chris explicitly opened this next: *"open T1 next session"*. T1 is the first child audit of the Group 2800 arc — smallest corpus, highest-impact, validates the §10 YAML schema before scale-up.

**Recommended S2834 session shape** (single-session child audit):

1. Fresh pin `s2834-t1-anchor-content-audit`
2. Author `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`
3. Corpus (~30 load-bearing docs):
   - Anchors: `docs/PLATFORM_WHAT_IT_IS.md`, `docs/PLATFORM_INVENTORY.md`, `docs/KNOWLEDGE_PIPELINE.md`, `docs/UDB_BEHAVIOR_LAYER.md`, `docs/UDB_TRANSLATION_LAYER.md`
   - Canon rows: 2 files in `docs/canon/`
   - Governance: `docs/governance/SYSTEM_OWNER.md`
   - Onboarding: 3 files in `docs/00-START-HERE/`
   - Root: `CLAUDE.md`, `00-START-NEXT-SESSION.md`, root README(s)
   - Any docs cited from CLAUDE.md's PRIORITY_DOCS/CRITICAL_DOCS graph
4. Method: per file, walk each concrete claim (file path, function name, line range, count) → verify against HEAD → emit YAML finding per §10.1 schema
5. Rigby joint SIGN on findings + schema-validation feedback (first thread validates the schema)
6. Chris ratifies findings + confirms schema binding for T2-T5

**Explicitly out of T1:** T2 broken-refs (mechanical grep), T3a/T3b (dup + orphan scans), T4 (handoff citations), T5 (audits triage). T1 is anchor-only.

**Alternative S2834 opens if Chris pivots:**

### If Chris wants to defer T1 and pivot to net-new engineering (per `feedback_engineering_bias_over_audit`)

- **Colorado Phase 4 statute-citation quality pass** — Chris personal work; real legal-doc capability
- **BettingPage first-user trace** — Chris IS the first user; real user-facing capability
- **New spider / new PA tool / new Workspace tab**

### If Chris wants to ratify §7 anchor updates (Group 2700 deferred at S2832)

Bucket A (auto-actionable low-risk) — ~1 session:
- PLATFORM_INVENTORY: add Group 2700 arc-completion note + Group 2800 arc-opening note
- ARCHITECTURE_INDEX: register Group 2700 + Group 2800 arcs
- CLAUDE.md: ADD 5 missing CRITICAL_DOCS/PRIORITY_DOCS refs
- PLATFORM_WHAT_IT_IS: add companion doc ref + verify `docs/current/` reference

### Available if Chris pivots to refactor/substrate

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + RAG Diagnostics tab (S2831) must produce identical `matched_patterns` post-refactor.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug hygiene:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
  - LucideIcon typing drift in `WorkspacePageNew.tsx`

**Recommended default (per Chris D-verdict S2833):** Open T1 anchor & canonical-doc content audit at S2834 as `2801_docs_content_anchors_audit.md`.

---

## SESSION PIN — S2833 RETIRED (fresh mint required at S2834 open)

**Pin history (S2833):**

- `pa-cc1dbcb7d18c4502` (label `s2833-docs-content-audit-scoping`) minted at S2833 open; served as both session pin AND arc SIGN pin (3 cycles preserved for future arc reference); **retired at S2833 close (`force=true`, sixty-fourth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2834 first-action fresh mint.

**S2834 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2833 handoff §3-§8 (Rigby SIGN 3-cycle status + Chris D-verdict + follow-up carry)
# Read S2833 ratification envelope §1-§4 (D1-D9 + SIGN cycles)
# Read 2800 parent scoping §4 T1 + §10 YAML schema (T1 executes exactly this)

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

curl -s -H "Authorization: Token 8c0f15633e8437621d64388aeb29eb89218882af" \
  "http://localhost:8000/api/rag/observability/intent-gate/?query=where%20do%20I%20start&limit=1&threshold=0.4" \
  | python -c "import json,sys;d=json.load(sys.stdin);print('S2831 tab:',d['matched_patterns'])"
# expect: ['self_reference']

python -m pytest tests/regression/rag_registry_parity/ tests/unit/test_intent_mechanism_registry.py core/tests/test_views_rag_intent_gate_diagnostics_2831.py -q 2>&1 | tail -3

python manage.py session_lifecycle open --label s2834-t1-anchor-content-audit
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2833 lessons to carry (also in handoff §7):**

1. **Cycle-2 Q4 DISAGREE demonstrates anti-rubber-stamp working as designed.** Rigby's tool-grounded 2701 exemplar read forced D8 from 4→≥6 sessions. Preserve this pressure.
2. **Under-designed schemas at parent-scoping level accrete scope creep in migration PRs.** §10 machine-consumable YAML schema locked at parent-lock time (D9) means every child produces consumable output.
3. **CONDITIONAL as an honest verdict.** Rigby's cycle-1 Q3/Q4/Q5 CONDITIONALs were "give me the exact tool commands"; not passive delay. Reward that shape.
4. **Display truncation in pa_chat channel != tool failure.** Cycle-3 Rigby's `repo_tool.read` returned `[OK]` but her summary was display-truncated at line 158 of a 306-line file. Verify locally when display truncates; don't re-run the tool.
5. **DO NOT open T1 in same session as parent ratification** (Chris directive: "next session"). Fresh-context first-child audit + clean pin rotation.
6. **DO NOT execute any /docs/ file operations during Group 2800.** Same discipline as Group 2700. Classification only.
7. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.** Locked at D9.
8. **DO NOT collapse T3a/T3b back into single T3.** Rigby cycle-1 Q1 STRENGTHEN evidence stands.
9. **DO NOT expand T4 into per-handoff content review.** Quarantined by D4 refinement.
10. **DO NOT audit in-flight arc children** (per §7 anti-scope).
11. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary (unchanged).
12. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule (unchanged).
13. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary (unchanged).
14. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract (unchanged).
15. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure (unchanged).
16. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant (unchanged).
17. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred (unchanged).
18. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards (unchanged).
19. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary (unchanged).
20. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4 (unchanged).

---

## Twin-pointer card

📁 **Repo — S2833 artifacts:**

- **Parent scoping doc:** `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md`
- **Handoff:** `docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 In-progress row)
- **Rigby SIGN conversation:** `pa-cc1dbcb7d18c4502` (3 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2833 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: mint at close cascade in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`; category `governance`; `deliverable_type=ratification_record`; `diagnostic_status=None`.

---

## Current repository state (S2833 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2833 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| **Group 2800 arc state** | **PARENT SCOPING RATIFIED (S2833, D1-D9 locked); T1 opens at S2834; 6 threads total; ≥6 sessions estimated.** |
| Group 2700 arc state | ARC CLOSED (S2817); §3 target tree RATIFIED (S2832); §7 + §8 DEFERRED (unchanged) |
| Metadata layer | ✅ 0 mismatches (S2829 substrate intact) |
| Discovery-layer arc state | Pattern B/C/D shipped + Registry Step 1 DORMANT + UI canary tab shipped (S2818-S2831). Step 2 refactor deferred. |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2834 recommended lean | Open T1 anchor & canonical-doc content audit (per Chris D-verdict S2833) as `2801_docs_content_anchors_audit.md`. Alternatives available if Chris pivots. |
| Session pin | `pa-cc1dbcb7d18c4502` (retired at S2833 close, force=true, sixty-fourth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2834 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2833 (post-cascade merge, seventy-ninth consecutive) |
| Next move | S2834 opens with T1 anchor content audit; fresh pin `s2834-t1-anchor-content-audit`. |

---

## Recommended session-open protocol (S2834, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2833 handoff §3-§8 (Rigby SIGN 3-cycle status + Chris D-verdict + follow-up carry)
4. Read S2833 ratification envelope §1-§4 (D1-D9 + SIGN cycles)
5. Read 2800 parent scoping §4 T1 (T1 spec) + §10 YAML schema (findings shape)
6. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + S2831 endpoint responds + parity harness 47/47)
7. `git log --oneline -8` — should show S2833 close cascade + S2832 close cascade + S2831 cascade
8. Mint fresh pin `s2834-t1-anchor-content-audit`
9. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
10. **DEFAULT: open T1 anchor content audit** per Chris D-verdict S2833
11. **DO NOT execute any /docs/ file operations** during Group 2800 (per §5 non-goals)
12. **DO NOT modify §10 YAML schema** — child audits emit exactly the §10.1 shape
13. **DO NOT audit T2-T5 corpus** — T1 is anchor-only; T2 grep is separate session
14. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary
15. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule
16. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary
17. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
18. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
19. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant
20. **DO NOT relax `include_superseded=False` default** — Chris D6 retrieval integrity rule (unchanged)
21. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
22. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
23. **DO NOT auto-adopt semantic default flips** (per S2821)
24. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
25. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
26. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
27. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
28. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
29. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2834:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md`](docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md) — **S2833 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md`](docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md) — **S2833 ratification envelope**
4. [`docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`](docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md) — **RATIFIED Group 2800 parent scoping (D1-D9)**
5. [`docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md`](docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md) — S2832 §3 target-tree ratification
6. [`docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`](docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md) — Group 2700 canonical summary (§3 RATIFIED)
7. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2b + §2c + §3 governance canonical
8. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc manifest (Group 2800 In-progress)
9. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
10. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — Pattern B/C/D Measured Boundary Summaries
11. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
