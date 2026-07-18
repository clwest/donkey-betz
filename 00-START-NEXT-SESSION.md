# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2814 CLOSED (evening close 2026-07-18; picks up as S2815) — Group 2700 T4 audience segmentation SHIPPED

**Refreshed 2026-07-18 evening (SESSION 2814 CLOSED — EIGHTEENTH-consecutive same-day multi-ship session and SIX-CLOSE-CASCADE day: S2809 + S2810 + S2811 + S2812 + S2813 + S2814 all closed 2026-07-18. Group 2700 T4 audience segmentation audit shipped as PR #3245 `bcc82a1a8`, +366 LOC. 5 discovery surfaces enumerated: (1) search_docs RAG corpus 3217 docs / 65454 chunks, (2) CRITICAL_DOCS 5 items, (2b) PRIORITY_DOCS 10 items, (3) CLAUDE.md pointer graph 45 refs, (4) PLATFORM_WHAT_IT_IS narrative ~7 refs, (5) runtime prompt-pack (bounded to surface 2 for T4). Primary audience counts: 5 Rigby-structural / 5 Rigby-high-priority / ~35-40 Claude-primary / ~5 Multi / ≤1730 Human UPPER-BOUND (residual). Key findings: (i) discovery-vs-injection asymmetry — 3 of 5 CRITICAL_DOCS + 2 of 10 PRIORITY_DOCS NOT in CLAUDE.md pointer graph; (ii) Rot signal — PLATFORM_WHAT_IT_IS references `docs/current/` NOT in T1 §3.1 subdir inventory (flag for T6). **FOURTH-CONSECUTIVE OP3 trigger** — post-authoring SIGN caught CRITICAL_DOCS/PRIORITY_DOCS conflation (open-SIGN pass claimed 10, actual 5). Same failure-mode class as S2811 `docs/18960/` ghost. OP3 pattern now 4/4 across 4 different audit shapes. FIFTY-EIGHTH close-cycle post-PLAYBOOK-7.4.4.**

**S2814 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Group 2700 T4 audit | **#3245** · `bcc82a1a8` | main | `docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md` (+366 LOC, new) |

**Handoff:** `docs/handoffs/SESSION_2814_GROUP_2700_T4_AUDIENCE_SEGMENTATION.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day).

**Arc state at S2814 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring** — Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3 ✅ (S2813) / T4 ✅ (S2814) / T5-T6 + 2799 queued.

---

## S2815 CANDIDATES — CHRIS PICKS FRESH

### ⭐ Continue Group 2700 arc

- **T5 — `2705_docs_handoffs_audits_proliferation_audit.md`** (per parent §11 next-in-sequence). BIG scope: 1035 handoffs + 138 audit files (3 dirs + 20 loose at root) + citation-graph analysis + substrate-integrity spot-check (per parent §4 T5). Likely uses Rigby-runs-tool shape for citation-integrity — third trigger for that methodology if so.
- **Playbook v0.9 amendment (proposal-only interlude arc):** Codify OP3 (audit-shape sessions require post-authoring SIGN). **4/4 triggers now support it.** Separate short-scope arc.

### Colorado / other

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5.1** — un-punt Session 534 spider AJAX (large; unknowable time budget)
- **GPT fallback for form-selection** on low-confidence (row-114 emergent)

### Non-Colorado / non-2700 arcs

- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** T5 to continue docs arc — T5-T6 are the largest remaining scopes and the momentum + Rigby-as-evidence pattern are dialed in.

---

## SESSION PIN — S2814 RETIRED (fresh mint required at S2815 open)

**Pin history (S2814):**

- `pa-0d04376abc074bcd` (label `s2814-group-2700-t4-audience-segmentation`) minted at S2814 open; **retired at S2814 close (`force=true`, forty-fifth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-0d04376abc074bcd` (retired)** — intended failure mode forces S2815 first-action fresh mint.

**S2815 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2814 handoff — §3 (novel-precedent), §6 (candidates)
# If continuing Group 2700 arc (T5), also read parent §4 T5 scope block + T3/T4 findings as evidence
brew services list | grep postgres

DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2815-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2815 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2814 lessons to carry:**

1. **OP3 two-SIGN-per-audit is 4/4 across 4 audit shapes** — measurement (T1), primitive extraction (T2), behavioral pain (T3), audience classification (T4). Pattern empirically ratified. Playbook v0.9 amendment ready.
2. **T4 failure-mode identical to S2811** — Claude open-SIGN misread source code (CRITICAL_DOCS vs PRIORITY_DOCS this time; `ls -la total NNNNN` misread as directory last time). Post-authoring rigor is the rescue mechanism.
3. **UPPER BOUND labels prevent false-precision cascade.** Rigby SIGN Q4 caught that "~1730 Human-primary" would be read as measured truth. Add precision qualifiers (exact / approximate / upper-bound) to all count claims in T5-T6.
4. **Discovery-vs-injection asymmetry is a real substrate finding.** 3 CRITICAL_DOCS + 2 PRIORITY_DOCS are injected into every agent context but NOT in CLAUDE.md pointer graph. Fresh Claude at bootstrap doesn't see them. Canonical summary must decide: add to CLAUDE.md, reduce CRITICAL_DOCS, or accept asymmetry as intentional.
5. **When source file has multiple similar-named data structures, enumerate each explicitly.** T4 conflated CRITICAL_DOCS (line 362, unconditional inject) with PRIORITY_DOCS (line 176, retrieval-scoring boost). Both are hardcoded doc lists in `docs_context_builder.py`; different mechanisms.
6. **Six-close-cascade day sustained.** Today shipped S2809 (~54 LOC) + S2810 (~130 LOC) + S2811 T1 (~406 LOC) + S2812 T2 (~434 LOC) + S2813 T3 (~407 LOC) + S2814 T4 (~366 LOC). Zero folds persisted; ledger stable at 114 all day. Session-cost-per-ship stays bounded when scope discipline + two-SIGN pattern hold.

---

## Twin-pointer card

📁 **Repo — S2814 artifacts:**

- **PR (1, merged):** #3245 (T4 audit · `bcc82a1a8`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md` — new (+366 LOC)
- **Handoff:** `docs/handoffs/SESSION_2814_GROUP_2700_T4_AUDIENCE_SEGMENTATION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day)
- **Merge SHA:** `bcc82a1a8` (T4) → close-cascade SHA filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible UI change this session.** T4 is a research/audit deliverable.
- **However:** T4 §6.3 discovery-vs-injection asymmetry finding has substrate implications — canonical summary decides whether to add missing 5 docs to CLAUDE.md or reduce CRITICAL_DOCS scope.

---

## Current repository state (S2814 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2814 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment threshold satisfied for OP3, now 4/4 triggers**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3 ✅ (S2813) / **T4 ✅ (S2814)** / T5-T6 + 2799 queued. |
| Emergent candidates | T5 next-in-sequence per parent §11; **Playbook v0.9 amendment for OP3 ready** (4/4 triggers); all prior Colorado candidates still queued |
| Session pin | `pa-0d04376abc074bcd` (retired at S2814 close, force=true, forty-fifth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-0d04376abc074bcd` (retired; forces fresh mint at S2815 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2814 open |
| Recycle log | `logs/recycle_events.jsonl` — +12 today across S2809-S2814 (2 per session) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day) |
| /docs/ restructuring | Group 2700 arc live; parent locked; T1 + T2 + T3 + T4 shipped; T5 next |
| Next move | Chris picks direction fresh at S2815 open |

---

## Recommended session-open protocol (S2815, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2814 handoff §3 (novel-precedent) + §6 (candidates)
4. **If continuing Group 2700 arc (T5):** also read parent §4 T5 scope block + skim T3 §7 C1-C5 evidence + T4 §5-§6 (audience matrix) as evidence sources
5. Sanity checks (brew postgres + curl /health/ping/)
6. Freshness + ledger 114 verify — see S2815 open sequence above
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. **Chris picks direction** — see §S2815 CANDIDATES above
9. Mint fresh pin scoped `s2815-<Chris's-direction>`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Route scope through Rigby joint SIGN before authoring
12. **For arc-audit work (T5+):** two SIGN cycles per audit doc (S2811-S2814 all confirm value). T5 will likely use Rigby-runs-tool shape for citation-graph analysis — third trigger for that methodology as first-class arc-audit pattern.
13. **UPPER BOUND / precision qualifiers required for count claims** (S2814 lesson) — canonical-summary authors overfit to point counts; label estimates explicitly.
14. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
15. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
16. **Anchor-verify at every scope decision point (12-session trend):** any factual claim about live state MUST be re-verified. Watch for similar-named-data-structure conflation (S2814 lesson: CRITICAL_DOCS vs PRIORITY_DOCS in same source file).
17. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2815:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2814_GROUP_2700_T4_AUDIENCE_SEGMENTATION.md`](docs/handoffs/SESSION_2814_GROUP_2700_T4_AUDIENCE_SEGMENTATION.md) — **S2814 handoff (current)**
3. [`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`](docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md) — parent scoping (Chris-locked S2801)
4. [`docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md`](docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md) — T1 (S2811)
5. [`docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md`](docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md) — T2 (S2812)
6. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3 (S2813)
7. [`docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md`](docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md) — T4 (S2814, cite as audience-classification source)
8. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — arc process framework (v2)
9. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts
10. [`docs/INDEX.md`](docs/INDEX.md) — docs corpus counts
11. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules; v0.9 amendment ready for OP3 at 4/4 triggers)
12. [`core/services/docs_context_builder.py`](core/services/docs_context_builder.py) — CRITICAL_DOCS (line 362) + PRIORITY_DOCS (line 176) — T4 evidence source
13. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2814 close (unchanged all day)
