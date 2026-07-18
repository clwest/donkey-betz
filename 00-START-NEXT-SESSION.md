# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2813 CLOSED (evening close 2026-07-18; picks up as S2814) — Group 2700 T3 human pain audit SHIPPED

**Refreshed 2026-07-18 evening (SESSION 2813 CLOSED — SEVENTEENTH-consecutive same-day multi-ship session and FIRST FIVE-CLOSE-CASCADE day: S2809 + S2810 + S2811 + S2812 + S2813 all closed 2026-07-18. Group 2700 T3 human-user pain points audit shipped as PR #3243 `82ae21a2b`, +407 LOC. Novel methodology: Rigby is FIRST-CLASS EVIDENCE SOURCE for 5 of 13 scenarios (C1-C5 are empirical `search_docs` dispatches). Damning discoverability failures surfaced: (a) literal filename query for `2701_docs_inventory_topology_audit` returns INDEX + reference-list entries, not the file (C4); (b) `search_docs("How many spiders")` returns archived Oct 2025 morning report as top-1, falsifying DOC_LIFECYCLE §2c sole-counts-source convention at discovery layer (C5); (c) `search_docs("00-START-NEXT-SESSION")` self-name query fails (C3). 8 of 13 scenarios failed success@3 (~62% failure rate). **THIRD-CONSECUTIVE OP3 trigger — Playbook v0.9 amendment threshold SATISFIED** for codifying "audit-shape sessions require post-authoring SIGN in addition to open-scope SIGN." FIFTY-SEVENTH close-cycle post-PLAYBOOK-7.4.4.**

**S2813 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Group 2700 T3 audit | **#3243** · `82ae21a2b` | main | `docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md` (+407 LOC, new) |

**Handoff:** `docs/handoffs/SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day).

**Arc state at S2813 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring** — Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3 ✅ (S2813) / T4-T6 + 2799 queued.

---

## S2814 CANDIDATES — CHRIS PICKS FRESH

### ⭐ Continue Group 2700 arc

- **T4 — `2704_docs_audience_segmentation_audit.md`** (per parent §11 next-in-sequence). Classify every `/docs/` file by primary audience — load-bearing-for-Rigby (search_docs corpus + tool-context) vs Claude-only (session bootstrap + CLAUDE.md graph) vs human-only (Chris reading in a browser) vs multi-audience. **Method:** cross-reference `search_docs` corpus + `docs_context_builder.py` reads + CLAUDE.md graph + PLATFORM_WHAT_IT_IS narrative surface. **Deliverable:** matrix — file × audience × surface-it-appears-on — plus counts by audience segment.
- **Playbook v0.9 amendment (proposal-only interlude arc):** Codify OP3 (audit-shape sessions require post-authoring SIGN) now that the promotion threshold is satisfied by 3 consecutive triggers across S2811-S2813. Separate short-scope arc; would slot between T3 and T4. Chris ratifies whether to interlude or continue T4 directly.

### Colorado / other

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5.1** — un-punt Session 534 spider AJAX (large; unknowable time budget)
- **GPT fallback for form-selection** on low-confidence (row-114 emergent)

### Non-Colorado / non-2700 arcs

- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** T4 to keep docs arc momentum. Playbook v0.9 amendment interlude is a legitimate alternative if you want to lock the OP3 pattern before T4-T6 continue exercising it.

---

## SESSION PIN — S2813 RETIRED (fresh mint required at S2814 open)

**Pin history (S2813):**

- `pa-8c19ffee44744847` (label `s2813-group-2700-t3-human-user-pain-points`) minted at S2813 open; **retired at S2813 close (`force=true`, forty-fourth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-8c19ffee44744847` (retired)** — intended failure mode forces S2814 first-action fresh mint.

**S2814 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2813 handoff — §3 (novel-precedent), §6 (candidates)
# If continuing Group 2700 arc (T4), also read parent §4 T4 scope block + T3 pain findings (§8) as evidence source
# Chris picks direction; label pin accordingly

# Sanity checks
brew services list | grep postgres

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2814-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2814 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2813 lessons to carry:**

1. **OP3 two-SIGN-per-audit pattern SATISFIED promotion threshold.** Three consecutive triggers across three different audit shapes (T1 measurement / T2 primitive extraction / T3 behavioral pain). All post-authoring SIGN caught substantive errors open-scope SIGN missed. Ready for Playbook v0.9 amendment consideration — separate arc, not urgent.
2. **Rigby-as-first-class-evidence-source (new T3 methodology).** For behavioral substrate audits (T3, likely T4), Rigby runs the scenarios and reports; Claude embeds her findings verbatim; post-authoring SIGN re-runs a subset for drift spot-check. Distinct from Claude-authors-Rigby-reviews pattern of T1/T2.
3. **Rigby drift spot-check as SIGN discipline.** During post-authoring SIGN, re-run 1-2 of the empirical scenarios to distinguish "structural indexing bias" from "query fragility." T3's C4+C5 re-runs returned identical results — findings confirmed structural. Should propagate to T4-T6 audits that use empirical measurement.
4. **DOC_LIFECYCLE §2c "sole authoritative counts source" convention is FALSIFIED at discovery layer.** T3 C5 evidence: searching for a count returns an archived Oct 2025 morning report as top-1, not PLATFORM_INVENTORY.md. Conventions require BOTH in-doc discipline AND discovery-layer enforcement. Substrate integrity finding for canonical summary + downstream implementation.
5. **`/docs/archive/` is not partitioned from RAG search corpus.** Every (c) scenario's search corpus includes 1388 archived files. Canonical summary must decide: archive-corpus segregation OR authority-weighted ranker OR `status: superseded` heavy deprioritization.
6. **Five-close-cascade day sustains** when scope discipline + two-SIGN pattern hold. Today shipped S2809 (~54 LOC) + S2810 (~130 LOC) + S2811 T1 (~406 LOC) + S2812 T2 (~434 LOC) + S2813 T3 (~407 LOC). Zero folds persisted; ledger stable at 114 all day.

---

## Twin-pointer card

📁 **Repo — S2813 artifacts:**

- **PR (1, merged):** #3243 (T3 audit · `82ae21a2b`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md` — new (+407 LOC)
- **Handoff:** `docs/handoffs/SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day)
- **Merge SHA:** `82ae21a2b` (T3) → close-cascade SHA filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible UI change this session.** T3 is a research/audit deliverable.
- **However:** T3 C5 finding directly impacts how Rigby answers count questions until fixed — the archived Oct 2025 morning report remains top-1 for "how many spiders" queries. Downstream implication for canonical summary + implementation session.

---

## Current repository state (S2813 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2813 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment threshold satisfied for OP3 codification** — separate arc when Chris ratifies) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3 ✅ (S2813) / T4-T6 + 2799 queued. |
| Emergent candidates | T4 next-in-sequence per parent §11; **Playbook v0.9 amendment for OP3 ready** as proposal-only interlude arc; all prior Colorado candidates still queued |
| Session pin | `pa-8c19ffee44744847` (retired at S2813 close, force=true, forty-fourth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-8c19ffee44744847` (retired; forces fresh mint at S2814 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2813 open |
| Recycle log | `logs/recycle_events.jsonl` — +10 today across S2809-S2813 (2 per session) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day) |
| /docs/ restructuring | Group 2700 arc live; parent locked; T1 + T2 + T3 shipped; T4 next |
| Next move | Chris picks direction fresh at S2814 open |

---

## Recommended session-open protocol (S2814, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2813 handoff §3 (novel-precedent) + §6 (candidates)
4. **If continuing Group 2700 arc (T4):** also read parent doc §4 T4 scope block + skim T3 pain findings §8 as evidence source
5. Sanity checks (brew postgres + curl /health/ping/)
6. Freshness + ledger 114 verify — see S2814 open sequence above
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. **Chris picks direction** — see §S2814 CANDIDATES above
9. Mint fresh pin scoped `s2814-<Chris's-direction>`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Route scope through Rigby joint SIGN before authoring
12. **For arc-audit work (T4+):** plan for TWO SIGN cycles per audit doc (S2811+S2812+S2813 all confirm value). If T4 uses Rigby-runs-scenarios shape, that's a second trigger for THIS methodology as a first-class arc-audit pattern.
13. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
15. **Anchor-verify at every scope decision point (11-session trend):** any factual claim about live state MUST be re-verified. Watch for `ls -la` `total NNNNN` trap. New: **Rigby search_docs findings are point-in-time snapshots** per T3 §7 Snapshot warning — re-run before relying if authoring T4-T6.
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2814:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md`](docs/handoffs/SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md) — **S2813 handoff (current)**
3. [`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`](docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md) — parent scoping (Chris-locked S2801)
4. [`docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md`](docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md) — T1 (S2811, cite as evidence source)
5. [`docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md`](docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md) — T2 (S2812, cite as evidence source)
6. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3 (S2813, cite as evidence source)
7. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — canonical arc process framework (v2)
8. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate; T3 evidence shows discovery-layer invisibility for count queries)
9. [`docs/INDEX.md`](docs/INDEX.md) — docs corpus counts
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules; v0.9 amendment threshold satisfied for OP3)
11. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2c "sole authoritative counts source" convention (T3 §7 C5 falsifies at discovery layer)
12. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2813 close (unchanged all day)
