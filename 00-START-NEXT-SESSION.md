# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2832 CLOSED (2026-07-19; picks up as S2833) — **2799 §3 TARGET /docs/ TREE RATIFIED · FILE-CONTENT-LEVEL AUDIT ARC OPENS AT S2833**

**Refreshed 2026-07-19 (SESSION 2832 CLOSED — continuation of S2831 terminal session; opened after S2831 close cascade shipped. Chris asked what remained in /docs/ backlog before Colorado Phase 4; Claude surveyed and surfaced that 2799 canonical summary from Group 2700 arc close (S2817) was still PROPOSED, not RATIFIED — blocking whole 8-item follow-on queue. Chris directed "ratify 2799 first". Claude minted S2832 pin `pa-d10f64b5624c43c9` (label `s2832-ratify-2799-docs-restructuring`) and routed 5 pressure-test questions to Rigby with tool-grounded prompts (docs/adr codebase refs / autogen management commands / DOC_LIFECYCLE §2c language / §8 ordering / zoom-out). Rigby ran substantive repo_tool searches; SIGN cycle superseded before verdict extraction when Chris clarified that "audit /docs/" originally meant every file and directory, NOT just /docs/research/. Claude corrected the record: Group 2700 arc DID cover whole tree at STRUCTURAL/STATISTICAL level (T1 inventoried 3247 files; T3/T4 sample-audited; T5 subset-focused; T6 rule-based across surfaces) — but honest gap is FILE-CONTENT audit (no per-file walk of stale/broken/duplicate/orphan by content). Chris D-verdict: **"ratify §3 today, open file-level audit arc"**. §3 target tree ratified as PROPOSED (compatibility-first guardrails preserved; NOT a move-script); §7 anchor updates + §8 queue ordering DEFERRED to future ratification; file-content-level audit arc OPENS at S2833. Ratification envelope authored at `docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md`; 2799 doc frontmatter updated to `status: ratified`; ratification metadata block added. Merged as PR #NNNN, SHA `TBD` (filled at cascade merge). `make recycle-all` clean post-merge per PLAYBOOK-7.4.4. SEVENTY-EIGHTH close-cycle post-PLAYBOOK-7.4.4. Handoff: `docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md`.**

**S2832 ship (governance-only session):**

| Focus | Artifact | Location |
|---|---|---|
| Ratify 2799 §3 target /docs/ tree | Envelope | `docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md` |
| Frontmatter status update | Modified | `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` (status: ratified; ratification block added) |
| S2832 handoff | New | `docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md` |
| S2833 pointer | Updated | THIS file — recommended default = file-content-level audit arc parent scoping |

**Arc state at S2832 close:**
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817. **§3 target tree RATIFIED at S2832** (compatibility-first; NOT authorized for bulk moves). **§7 anchor updates + §8 follow-on queue DEFERRED** (ratifiable separately).
- **File-content-level audit arc**: OPENS at S2833 — parent scoping session picks arc number + strategy. Rough shape: 3247 files; per-file classification (stale/broken/duplicate/orphan); multi-session; NOT scoped by this ratification.
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D shipped; DORMANT registry Step 1 + user-facing diagnostics tab shipped. §8 item #1 completed.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

---

## S2833 CANDIDATES

### ⭐ Recommended default direction — **File-content-level /docs/ audit arc — parent scoping** (per Chris D-verdict S2832)

Chris explicitly opened this arc at S2832 close: *"open file-level audit arc"*. Group 2700 arc did structural/statistical audit; this new arc reads every `.md` file in `/docs/` and flags issues by CONTENT.

**Recommended S2833 session shape** (parent scoping, single session):

1. Author `docs/research/domains/docs_content_audit/2900_docs_content_audit_domain_scoping.md` (or unclaimed arc number; parent-scoping session picks)
2. Scope: 3247 files across `/docs/`; per-file classification rubric (stale-from-HEAD / broken-references / duplicate-content / orphan / OK); NOT structural (that's Group 2700)
3. Excluded from scope per DOC_LIFECYCLE §0: `docs/docs-pattern/**` (context-kit framework); `docs/archive/**` (per parent §7 anti-scope)
4. Effective scope: ~1800 non-archive, non-framework files
5. Rigby joint SIGN on the scoping doc — pressure-test rubric + sub-arc slicing + estimated session count
6. Chris ratifies parent scoping
7. Child audits open in subsequent sessions (T1..Tn per subdir batch)

**Alternative S2833 opens if Chris pivots:**

### If Chris wants to ratify §7 anchor updates (deferred at S2832)

Bucket A (auto-actionable low-risk) — ~1 session:
- PLATFORM_INVENTORY: add Group 2700 arc-completion note
- ARCHITECTURE_INDEX: register Group 2700 arc + update §7 decision matrix
- CLAUDE.md: ADD 5 missing CRITICAL_DOCS/PRIORITY_DOCS refs
- PLATFORM_WHAT_IT_IS: add companion doc ref + verify `docs/current/` reference

Bucket B (separate arcs; require own ratification):
- Parent §4 T5 clause update per MQ-T5-8
- Playbook §15/§16 twin-pin discipline codification
- DOC_LIFECYCLE §2c discovery-layer enforcement clause

### If Chris wants to ratify §8 queue ordering (deferred at S2832)

7 remaining items (item #1 done via S2818-S2831). Strong recommendation: flag item #3 (Playbook v0.9 OP3 amendment, 7/7 over-corroborated) as ready to ship next as smallest-scope governance work.

### If Chris pivots to net-new engineering (per `feedback_engineering_bias_over_audit`)

- **Colorado Phase 4 statute-citation quality pass** — Chris personal work; real legal-doc capability
- **BettingPage first-user trace** — Chris IS the first user; real user-facing capability
- **New spider / new PA tool / new dashboard tab**

### Available if Chris pivots to refactor/substrate/audit

- **Step 2 refactor (S2830 forward-carry, DEFERRED)** — Refactor `search_embeddings()` to iterate `INTENT_MECHANISMS`. Requirements: fresh Rigby joint SIGN + fresh Chris D-verdict + golden-file parity fixture PASS + 95/95 Pattern C+D pytest PASS + RAG Diagnostics tab (S2831) must produce identical `matched_patterns` post-refactor.
- **PR3 (S2829 deferred)** — Canonical-anchor invariant design + divergent-retrieval-stack diagnostic.
- **Latent bug hygiene:**
  - `views_rag_observability.py` — 10 pre-existing `status_code=` calls should be `status=`
  - LucideIcon typing drift in `WorkspacePageNew.tsx` (`PrimaryTab.icon` type widening or `lucide-react` type ergonomics fix)

**Recommended default (per Chris D-verdict S2832):** Open file-content-level audit arc parent scoping at S2833.

---

## SESSION PIN — S2832 RETIRED (fresh mint required at S2833 open)

**Pin history (S2832):**

- `pa-d10f64b5624c43c9` (label `s2832-ratify-2799-docs-restructuring`) minted at S2832 open; **retired at S2832 close (`force=true`, sixty-third consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2833 first-action fresh mint.

**S2833 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2832 handoff §3-§8 (Rigby SIGN status + Chris D-verdict + follow-up carry)
# Read S2832 ratification envelope §1-§3 (what was + wasn't ratified + successor arc scope)
# Read 2799 canonical summary §3 (ratified target tree — DESTINATION only, NOT a move-script)

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

python manage.py backfill_document_status_from_docs_index 2>&1 | tail -3
# expect: CommandError: Explicit mode required

curl -s -H "Authorization: Token [REDACTED - HISTORICAL SECRET]" \
  "http://localhost:8000/api/rag/observability/intent-gate/?query=where%20do%20I%20start&limit=1&threshold=0.4" \
  | python -c "import json,sys;d=json.load(sys.stdin);print('S2831 tab:',d['matched_patterns'])"
# expect: ['self_reference']

python -m pytest tests/regression/rag_registry_parity/ tests/unit/test_intent_mechanism_registry.py core/tests/test_views_rag_intent_gate_diagnostics_2831.py -q 2>&1 | tail -3

python manage.py session_lifecycle open --label s2833-<slug>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2832 lessons to carry (also in handoff §7):**

1. **Route governance ratifications through Rigby SIGN even when Chris pre-empts.** Rigby's tool_runs surfaced substantive codebase evidence (docs/adr references across 15 files) that will inform any future §3 execution. Preserving SIGN conversation `pa-d10f64b5624c43c9` for future reference is right shape.
2. **Chris directives can supersede open SIGN cycles.** Chris clarifying scope mid-SIGN shifts verdict process from "Claude+Rigby agree → Chris yes/no" to "Chris scope clarification → direct execution". Legitimate per `feedback_claude_rigby_agree_first_chris_yes_no` — default shape, not exclusive.
3. **Ratifying destinations without timelines is NOT deferring indefinitely.** §3 ratification pre-commits direction so future PRs don't re-litigate. What it defers is scheduling, not agreement.
4. **File-content-level audit is genuinely a separate arc.** Group 2700 scoped itself at structural/statistical level; content-level was never in scope. Chris's clarification exposed a real gap.
5. **DO NOT execute §3 file moves in the same session as ratification** — ratification is destination shape; each move needs per-PR verification of DOC_LIFECYCLE §2b + generator coordination (item #8 in §8 queue).
6. **DO NOT ratify §7 or §8 without explicit Chris D-verdict** — Chris said "§3 today"; interpret narrowly.
7. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule (unchanged).
8. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary (unchanged).
9. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary (unchanged).
10. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract (unchanged).
11. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure (unchanged).
12. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant (unchanged).
13. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred (unchanged).
14. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards (unchanged).

---

## Twin-pointer card

📁 **Repo — S2832 artifacts:**

- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md`
- **2799 doc frontmatter:** `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` (status: ratified; ratification block added)
- **Handoff:** `docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md`
- **Rigby SIGN conversation:** `pa-d10f64b5624c43c9` (preserved; tool_runs substantive; verdicts unextracted)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2832 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: mint at close cascade in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`; category `governance`; `diagnostic_status=None`.

---

## Current repository state (S2832 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2832 cascade PR SHA (filled at merge) |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| **Group 2700 arc state** | **ARC CLOSED (S2817); §3 target tree RATIFIED (S2832 Chris D-verdict); §7 + §8 DEFERRED (ratifiable separately).** |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Metadata layer** | ✅ **0 mismatches** (S2829 substrate hardening intact); `--apply` guard active; sync skip-branch closure active |
| **Discovery-layer arc state** | Pattern B/C/D shipped + retrieval integrity holds. Registry Step 1 DORMANT + UI canary tab shipped (S2818-S2831). Step 2 (search_embeddings refactor) deferred. §8 item #1 (discovery-layer enforcement) done. |
| **File-content-level audit arc** | **OPENS at S2833 — parent scoping picks arc number + strategy (Chris directive S2832)** |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2833 recommended lean | Open file-content-level audit arc parent scoping (per Chris D-verdict S2832). §7/§8 ratification + Colorado Phase 4 + net-new candidates + Step 2 refactor all available if Chris pivots. |
| Session pin | `pa-d10f64b5624c43c9` (retired at S2832 close, force=true, sixty-third consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2833 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Recycle log | `logs/recycle_events.jsonl` — +1 at S2832 (post-cascade merge, seventy-eighth consecutive) |
| Next move | S2833 opens with file-content-level audit arc parent scoping; fresh pin `s2833-<slug>`. |

---

## Recommended session-open protocol (S2833, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2832 handoff §3-§8 (Rigby SIGN status + Chris D-verdict + follow-up carry)
4. Read S2832 ratification envelope §1-§3 (what was + wasn't ratified + successor arc scope)
5. Read 2799 canonical summary §3 (ratified target tree — DESTINATION only, NOT a move-script)
6. Sanity checks (brew postgres + backfill dry-run = 0 mismatches + Pattern B/C/D top-1 canonical + bare backfill → CommandError + INTENT_MECHANISMS registry present + S2831 endpoint responds + parity harness green)
7. `git log --oneline -8` — should show S2832 close cascade + S2831 cascade + #3275 feat + S2830 close cascade
8. Mint fresh pin scoped to whatever S2833 pursues
9. **Anti-rubber-stamp check on first Rigby SIGN** — verify `tool_runs` non-empty
10. **DEFAULT: open file-content-level audit arc parent scoping** per Chris D-verdict S2832
11. **DO NOT execute §3 file moves** — ratification is destination shape only; each move needs per-PR DOC_LIFECYCLE §2b verification + generator coordination
12. **DO NOT ratify §7 or §8 without explicit Chris D-verdict** — S2832 D-verdict scoped narrowly to "§3 today"
13. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary
14. **DO NOT couple new observability surfaces to log capture** — S2831 Rigby Q2 substrate rule
15. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary
16. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract
17. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure
18. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant
19. **DO NOT relax `include_superseded=False` default** — Chris D6 retrieval integrity rule (unchanged)
20. **DO NOT propose adding docs to universal runtime injection to fix retrieval misses** — Chris D3: "Retrieval must prove retrieval."
21. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred
22. **DO NOT auto-adopt semantic default flips** (per S2821)
23. **DO NOT build RRF or global fusion** (per Chris R6 from S2821)
24. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
25. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4
26. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards
27. **DO NOT alter Pattern D per-gate ceilings without new sweep evidence** — pytest guards
28. Preserve post-corpus-correction 18-row corpus for re-measurement (Chris D-Q2 from S2828)

---

## Reference documents

Ordered by frequency of use at S2833:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md`](docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md) — **S2832 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md`](docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md) — **S2832 ratification envelope**
4. [`docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`](docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md) — **RATIFIED §3 target tree**
5. [`docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md`](docs/handoffs/SESSION_2831_RAG_INTENT_GATE_DIAGNOSTICS_TAB.md) — S2831 UI tab + Step 2 canary
6. [`docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md`](docs/handoffs/SESSION_2830_POINTER_INTENT_REGISTRY_STEP_1.md) — S2830 registry substrate
7. [`docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md`](docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md) — Group 2700 arc close
8. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2b + §2c + §3 governance canonical
9. [`core/rag_integration.py`](core/rag_integration.py) — Pattern B/C/D + DORMANT registry at `:483-799`
10. [`docs/KNOWLEDGE_PIPELINE.md`](docs/KNOWLEDGE_PIPELINE.md) — Pattern B/C/D Measured Boundary Summaries
11. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
12. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc manifest
