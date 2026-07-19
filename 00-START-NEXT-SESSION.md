# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2834 CLOSED (2026-07-19; picks up as S2835) — **GROUP 2800 T1 ANCHOR CONTENT AUDIT RATIFIED · SCHEMA V1.1 LOCKED · T2 REFERENCE-GRAPH AUDIT OPENS AT S2835**

**Refreshed 2026-07-19 (SESSION 2834 CLOSED — fresh session opened per S2833 pointer. Chris opened with "Please begin"; after seeing candidate menu (net-new engineering first per `feedback_engineering_bias_over_audit`, plus S2833-D-verdict default) Chris picked the ratified default: open T1. All S2834 open-protocol sanity checks green at open (pg15 started, backfill 0 mismatches, Pattern B/C canonical, S2831 endpoint responds, parity harness 47/47 in 191.6s). Fresh pin `pa-5fa195547db04260` (label `s2834-t1-anchor-content-audit`) minted. Claude authored T1 audit doc at `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md` (1305 lines, 33 files classified in v1.1 YAML schema). Joint Rigby SIGN 3 cycles: cycle-1 (6 tool_runs) 4 STRENGTHEN + 1 DISAGREE (Q3 class-P0-status-ok histogram pollution) + 1 AGREE; cycle-2 (5 tool_runs) 4 STRENGTHEN + 1 AGREE (Q10 lock v1.1 not gold-plating); cycle-3 (5 tool_runs) 1 STRENGTHEN + 2 AGREE. Anti-rubber-stamp verified across all 3 cycles per `feedback_verify_rigby_tool_runs_before_trusting_sign`. Chris D-verdict: **"ratify T1 as-is + schema v1.1"**. Real drifts caught: 1 active P0 (CLAUDE.md line 262 "Discord bot: 144 commands" contradicts linked doc's S1115 correction AND CLAUDE.md's own live autogen block line 148 which shows 96) + 4 P1 (KNOWLEDGE_PIPELINE line 25 "64 spiders" → 80; topics/personal-assistant.md line 6/12/13 stale counts; AGENTS + SPIDERS V1-banner retrofit) + 9 P2 (structural_only coverage on 8 large refs + refresh cadence banner candidates). Schema §10.1 → v1.1 with 5 new backward-compatible fields (schema_version frontmatter tag; claim_source; finding_state; coverage with §5.5 waiver protocol; claim_density_hint). §10.4 root-stability P0 clarification adopted. §4.1a T3a pre-scan hint recorded. Ratification envelope authored at `docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md`. 2801 doc frontmatter updated status: proposed→ratified with full ratification block. Group 2800 arc registration in `docs/research/OPEN_ARCS.md` updated (1→2 of 6 shipped). Merged as PR #NNNN, SHA `TBD` (filled at cascade merge). `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. EIGHTIETH close-cycle post-PLAYBOOK-7.4.4. Handoff: `docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md`.**

**S2834 ship (T1 child audit + schema v1.1):**

| Focus | Artifact | Location |
|---|---|---|
| T1 child audit (33-file classification + schema v1.1 spec) | New | `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md` (1305 lines, status ratified) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 2/6 shipped) |
| S2834 handoff | New | `docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md` |
| S2835 pointer | Updated | THIS file — recommended default = T2 reference-graph audit |

**Arc state at S2834 close:**
- **Group 2800 /docs/ content audit arc**: **T1 RATIFIED at S2834 (schema v1.1 locked)**. **2 of 6 shipped** (parent + T1). T2 opens at S2835. Migration queue frozen; routed to future §3 execution arc post-2899 close.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue DEFERRED. (Unchanged.)
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

---

## S2835 CANDIDATES

Per `feedback_engineering_bias_over_audit` — net-new engineering pivots listed first; ⭐ marks the S2834-derived ratified default (T2 next per Group 2800 sequence).

### A. Net-new engineering pivots (per engineering-bias rule)

1. **Colorado Phase 4 statute-citation quality pass** — Chris personal legal work; real capability
2. **BettingPage first-user trace** — Chris IS the first user; wire the real path end-to-end
3. **New spider / PA tool / Workspace tab** — pick a concrete gap

### B. ⭐ Ratified default — T2 reference-graph audit (Group 2800 second child)

Per Group 2800 arc sequence + S2834 close pointer.

**Recommended S2835 session shape:**

1. Fresh pin `s2835-t2-reference-graph-audit`
2. Author `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`
3. Scope (per parent §4 T2): relative-path links, ADR references
   (`ADR-NNNN`), session-handoff cross-refs (`SESSION_NNNN`), file-path
   citations (`core/services/X.py:LINE`) — across all in-scope files
4. Method: mechanical grep + resolver; classify PASS / 404 /
   renamed-target-exists-elsewhere / ambiguous
5. Emit YAML findings per §10.1 v1.1 schema locked at S2834 (all rows
   inherit `schema_version: 1.1` from frontmatter)
6. Rigby joint SIGN + Chris D-verdict
7. Migration-queue routing to future §3 execution arc

**Anti-pattern to actively challenge (parent §4 T2):** "if grep says the
target resolves, the reference is healthy." Some refs cite a specific
line range that's semantically moved; sample-verify.

### C. §7 anchor updates (Group 2700 deferred at S2832)

Bucket A auto-actionable ~1 session:
- PLATFORM_INVENTORY: add Group 2800 arc-opening + T1 close notes
- ARCHITECTURE_INDEX: register Group 2800 + T1 close
- CLAUDE.md: fix the P0 line 262 discord count in-place (root-stability §10.4 (b) gate)

### D. Substrate / refactor (available if Chris pivots)

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + RAG Diagnostics tab (S2831) must produce identical `matched_patterns` post-refactor.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug hygiene:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
  - LucideIcon typing drift in `WorkspacePageNew.tsx`

**Recommended default (per Group 2800 sequence):** Open T2 reference-graph audit at S2835 as `2802_docs_content_reference_audit.md`.

---

## SESSION PIN — S2834 RETIRED (fresh mint required at S2835 open)

**Pin history (S2834):**

- `pa-5fa195547db04260` (label `s2834-t1-anchor-content-audit`) minted at S2834 open; served as both session pin AND arc SIGN pin (3 cycles preserved for future arc reference); **retired at S2834 close (`force=true`, sixty-fifth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2835 first-action fresh mint.

**S2835 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2834 handoff §3-§8 (Rigby SIGN 3-cycle status + Chris D-verdict + follow-up carry)
# Read S2834 ratification envelope §1-§4 (D1-D9 + SIGN cycles + schema v1.1 delta)
# Read 2801 T1 §5 v1.1 schema + §10.1 findings shape (T2 executes the same schema)
# Read 2800 parent scoping §4 T2 spec

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

python manage.py session_lifecycle open --label s2835-t2-reference-graph-audit
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2834 lessons to carry (also in handoff §7):**

1. **Verify tool_runs non-empty is not a check-box — it's a gate.** Rigby cycle-1 Q3 DISAGREE would not have surfaced under rubber-stamp discipline.
2. **Anti-worship discipline (Rigby Q10 AGREE lock v1.1)**: schema refinements were justified by observed failure modes surfaced in the T1 pass. Not gold-plating. Lock at close, defer further embellishments to `future_trigger` at 2899.
3. **Small canary corpus catches heterogeneity signals.** 2 topics added at cycle-1 Q1 — 1 stale (PA), 1 clean (agent-system) — validated the T3a pre-scan hint.
4. **Backward compat = schema versioning discipline.** Frontmatter `schema_version`, not per-row tags.
5. **Coverage contract > free-text notes.** `structural_only` as a contract-level field is enforceable; free-text notes are not.
6. **DO NOT open T2 in same session as T1 ratification** (parent §5 sequential-child discipline; Rigby cycle-3 corroboration).
7. **DO NOT execute any /docs/ file operations during Group 2800.** Same discipline as Group 2700. Classification only.
8. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.** Locked at S2834.
9. **DO NOT collapse T3a/T3b back into single T3** — Rigby cycle-1 Q1 STRENGTHEN evidence stands (S2833).
10. **DO NOT expand T4 into per-handoff content review.** Quarantined by S2833 D4 refinement.
11. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.** Locked at S2833 D9.
12. **DO NOT audit in-flight arc children** (per parent §7 anti-scope).
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

---

## Twin-pointer card

📁 **Repo — S2834 artifacts:**

- **T1 audit doc (RATIFIED):** `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md`
- **Handoff:** `docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 2/6 shipped)
- **Rigby SIGN conversation:** `pa-5fa195547db04260` (3 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2834 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: mint at close cascade in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`; category `governance`; `deliverable_type=ratification_record`; `diagnostic_status=None`.

---

## Current repository state (S2834 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2834 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged; 205 rules) |
| **Group 2800 arc state** | **T1 RATIFIED (S2834, schema v1.1 locked); 2 of 6 shipped; T2 opens at S2835.** |
| Group 2700 arc state | ARC CLOSED (S2817); §3 target tree RATIFIED (S2832); §7 + §8 DEFERRED (unchanged) |
| Metadata layer | ✅ 0 mismatches (S2829 substrate intact) |
| Discovery-layer arc state | Pattern B/C/D shipped + Registry Step 1 DORMANT + UI canary tab shipped (S2818-S2831). Step 2 refactor deferred. |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| Content-audit schema | §10.1 v1.1 (locked at S2834; 5 new backward-compatible fields via frontmatter `schema_version:1.1`) |
| S2835 recommended lean | Open T2 reference-graph audit as `2802_docs_content_reference_audit.md`. Alternatives available if Chris pivots. |
| Session pin | `pa-5fa195547db04260` (retired at S2834 close, force=true, sixty-fifth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2835 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2834 (post-cascade merge, eightieth consecutive) |
| Next move | S2835 opens with T2 reference-graph audit; fresh pin `s2835-t2-reference-graph-audit`. |

---

## Recommended session-open protocol (S2835, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2834 handoff §3-§8 (Rigby SIGN 3-cycle status + Chris D-verdict + follow-up carry + schema v1.1 delta)
4. Read S2834 ratification envelope §1-§4 (v1.1 schema delta + root-stability P0 clarification + migration waiver protocol)
5. Read 2801 T1 §5 (schema v1.1) + §10.1 findings shape (T2 executes SAME schema)
6. Read 2800 parent scoping §4 T2 (T2 spec) — mechanical grep + resolver methodology
7. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + S2831 endpoint responds + parity harness 47/47)
8. `git log --oneline -10` — should show S2834 close cascade + S2833 close cascade + S2832 close cascade
9. Mint fresh pin `s2835-t2-reference-graph-audit`
10. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
11. **DEFAULT: open T2 reference-graph audit** per Group 2800 arc sequence
12. **All T2 findings inherit `schema_version: 1.1` from frontmatter** — no per-row tag
13. Populate `coverage: full_claim_walk` explicitly (per v1.1 shape) — grep+resolver IS a full walk for T2's scope
14. **DO NOT execute any /docs/ file operations** during Group 2800 (per §5 non-goals)
15. **DO NOT modify §10.1 v1.1 schema** — locked at S2834
16. **DO NOT audit T3-T5 corpora** — T2 is reference-graph only
17. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary
18. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule
19. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary
20. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
21. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
22. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant
23. **DO NOT relax `include_superseded=False` default** — Chris D6 retrieval integrity rule (unchanged)
24. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
25. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
26. **DO NOT auto-adopt semantic default flips** (per S2821)
27. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
28. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
29. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
30. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
31. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
32. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2835:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md`](docs/handoffs/SESSION_2834_T1_ANCHOR_CONTENT_AUDIT.md) — **S2834 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md`](docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md) — **S2834 ratification envelope (v1.1 schema)**
4. [`docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`](docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md) — **RATIFIED T1 audit (33 files + v1.1 schema in §5)**
5. [`docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`](docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md) — Group 2800 parent (D1-D9 RATIFIED S2833)
6. [`docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md`](docs/handoffs/SESSION_2833_DOCS_CONTENT_AUDIT_PARENT_SCOPING.md) — S2833 parent-scoping handoff
7. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2b + §2c + §3 governance canonical (§3 root-stability referenced by T1 §10.4 clarification)
8. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc manifest (Group 2800 In-progress, 2/6)
9. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
10. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — Pattern B/C/D Measured Boundary Summaries **(P1 finding at line 25 — "64 spiders" → 80 in migration queue)**
11. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
