---
title: "Open Arcs — cross-session manifest of research groups in flight"
status: active
authority: state
session_added: 1279
last_updated: 2026-07-01 (S1399 close — **Group 1300 arc closed**. Canonical summary committed on `main` via PR #2781 (`6318787b`). S1399 SIGN pin `pa-4fc3329d0db6484f` retired (`updated_count: 2, retired: true`). Arc pin `pa-aa54193f240f4846` retirement deferred to next-session open per Rigby safety refusal on currently-bound-thread self-retirement — will retire once next-arc pin is minted + `tools/pa_local.sh` header rotated. Row moved from In-progress → Closed section this commit.)
maintainer: OS-managed (playbook §16 commit gate + OS §14 completion contract)
purpose: machine-readable navigation artifact — not a report
schema_owner: docs/research/process/RESEARCH_OPERATING_SYSTEM.md §6.3
---

# Open Arcs

Live manifest of every research group's state. Updated at every
session close per OS §14 Completion Contract. Reconciliation
ritual per OS §6.6 runs against this file, `00-START-NEXT-SESSION.md`,
and the latest handoff.

**Reading this file:**
- **In-progress** = actively being worked; open child slots exist.
- **Awaiting summary** = all locked child audits shipped; `xx99`
  canonical summary session not yet run.
- **Closed** = graduation criteria (playbook §17) met; group is
  done. Follow-on queue lives on; the arc itself is finished.
- **Stalled** = open Rigby NEEDS-MORE OR blocked children; needs
  Chris intervention.
- **Not started** = queued (playbook §22); range unclaimed.

Conflict resolution: `OPEN_ARCS.md` wins on arc state. Session
priorities in `00-START-NEXT-SESSION.md` win on today's work.
Handoffs win on ship state. See OS §6.6.

---

## In-progress

*(none — Group 1300 Memory closed S1399 2026-07-01 via PR #2781)*

## Awaiting summary

*(none)*

## Closed

| Group | Domain | Closed session | Canonical summary | Notes |
|-------|--------|----------------|-------------------|-------|
| — | **Employee OS depth arc** (§1.1–§1.8) | S1272 | *(no formal `xx99` — pre-playbook)* | 8 research docs across S1268–S1272. Foundation for the entire library. |
| — | **Whole-platform inventory + integration audit** | S1274 | *(single-doc arcs — no summary needed)* | `platform_architecture_inventory.md` (§1.9) + `cross_domain_integration_audit.md` (S1274 sibling). |
| — | **Symbol Mapping design-preparation arc** | S1275 | *(pre-playbook — no formal `xx99`)* | §1.6 → §1.10 → §1.12 design-preparation chain. Option E ratification pending Chris + future ADR corpus. |
| — | **Playbook v2** (§1.11) | S1276 | *(process doc — no summary)* | Playbook restructured to 7 parts / 24 sections. First formal `authority: process` doc. |
| — | **Research Operating System** (§1.14 + §1.15) | S1278 | *(process doc arc — no summary; §20 finalization serves this role)* | Three Rigby SIGN cycles. Ratification READY-WITH-MINOR-FOLLOW-UP → CANONICAL after S1279 installation completes. |
| **1300** | Memory / Knowledge / Embeddings | S1399 | `1399_memory_canonical_summary.md` (§1.21 in ARCHITECTURE_INDEX v18; PR #2781 = `6318787b`) | **First formal `xx99` canonical summary in the library.** Arc closed 2026-07-01 (see Recent reconciliations 2026-07-01 S1399 close for details). 7-session arc: S1300 parent + S1301 Cat D + S1302 Cat A+B+C + S1303 Cat F + S1304 Cat E↔D + S1305 Cat H + S1399 canonical summary. Load-bearing methodology outputs (F1 provenance-filter drift class; F2 row-level orphan-write pattern; F3 Redis-only durability + `@lru_cache` staleness pattern; F4 F1/F4-CANDIDATE + severity-correction discipline as inheritance methodology) named across children. Arc pin `pa-aa54193f240f4846` retirement deferred to next-session open per Rigby safety refusal (currently-bound thread); S1399 SIGN pin `pa-4fc3329d0db6484f` retired at close (`updated_count: 2, retired: true`). Follow-on queue: S1399 §8 21 items ranked; top 5 P1 candidates named in Recent reconciliations. Cat G Mission Memory delegated to Employee OS 1200s arc. Group 1700 Observability inherits 4 aggregated delegations. Post-S1399 design-preparation phase owns 4 ADR/design-preparation docs. |

## Not started (playbook §22 queue)

**Group 1300 closed S1399 2026-07-01.** Next-arc queue is
unblocked. Chris directive resolves at next-session open.

| Group | Domain | Priority rationale |
|-------|--------|-------------------|
| **1400** | Revenue / Outreach / Engagement | Business-value highest under-researched domain; Rigby-caught missed inventory in S1273 review. Queued after Group 1300 completes (S1305 or S1399), OR after Chris explicitly parallelizes with an isolation-pin split. |
| **1500** | Sports / DBAO / Intelligence | Structural question: island vs integrated (S1274 §11.3). |
| **1600** | Content / Deliverables / Publishing | Well-inventoried; integration analysis needed. |
| **1700** | Observability / Telemetry / SLOs | 5-layer execution-telemetry dedup audit (S1273 §5.13 + S1274 §11.6). |
| **1800** | HumanAttention / Feedback / Learning | Round-trip learning loop scope expansion. |
| **1900** | Event / Integration / Runtime Architecture | Downstream of S1274 §11.1 EventBus adoption. |

## Stalled

*(none)*

---

## Session-boundary reconciliation

**On session open:** cross-check this file against
`00-START-NEXT-SESSION.md` and the latest `docs/handoffs/SESSION_*.md`.
If any surface disagrees on arc state, resolve per OS §6.6
reconciliation ritual: OPEN_ARCS wins on arc state, START-NEXT
wins on today's priorities, handoff wins on ship state. Write a
one-line reconciliation note under **Recent reconciliations**
(below) plus the closing handoff.

**On session close:** update the row for any group whose state
changed. Move rows between sections as state transitions
(in-progress → awaiting-summary → closed).

## Recent reconciliations

- **2026-07-01 (S1301 open).** Cross-checked this file against `00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`. All three agreed Group 1300 was `in-progress` with S1301 queued; no reconciliation needed.
- **2026-07-01 (S1301 close).** Group 1300 current-child field advanced from *S1301 queued* to *S1301 SIGN-clean (commit-gated) + S1302 queued next*. Dependencies unchanged. Next-expected pointer rotates to Categories A+B+C per S1301 §19 downstream routing.
- **2026-07-01 (S1302 open).** Cross-checked this file against `00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`. Recent commits show S1301 artifacts already merged to `main` (PR #2775 = `b54b2409`, PR #2776 = `5f6b9863`); working tree clean. S1301 commit-gate status in the S1301 handoff was resolved between sessions. Reconciliation: S1302 branches off `main` (not stacked on S1301) per playbook §16. Chris ratified D8 (launch cadence: PROCEED) + D9 (arc pin: RETAIN `pa-aa54193f240f4846`) via arc pin.
- **2026-07-01 (S1302 close).** Group 1300 current-child field advanced from *S1301 SIGN-clean (commit-gated) + S1302 queued* to *S1302 SIGN-clean (commit-gated) + S1303 queued next*. Next-expected pointer rotates to Category F Conversational/Thread Memory per S1302 §19.1 downstream routing. S1302 headline finding F1 (spider_context['pa_content_feedback'] confirmed dead code) crossed the "escalated from UNKNOWN" boundary — parent §3C UNKNOWN bullet formally resolved as `dead_code` finding. Row-level orphan-write pattern (S1301 §14.3 D3 inheritance) narrowed across three Rigby SIGN cycles from ~11 fields (v1) → 5 strict-orphan + 2 narrow-consumer-safety-filter fields (final). SIGN-clean verdict logged in audit frontmatter `sign_status` field + §20.7 fold notes.
- **2026-07-01 (S1303 open).** Cross-checked this file against `00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`. Recent commits confirmed S1302 artifacts merged to `main` (PR #2777 = `c053272a`); working tree clean on `main`. S1302 commit-gate resolved between sessions. Reconciliation: S1303 branches off `main` (not stacked on S1302) per playbook §16. Chris ratified D10 (launch cadence: PROCEED) + D11 (arc pin: RETAIN `pa-aa54193f240f4846`) via arc pin.
- **2026-07-01 (S1303 close).** Group 1300 current-child field advanced from *S1302 SIGN-clean (commit-gated) + S1303 queued* to *S1303 SIGN-clean (commit-gated) + S1304 queued next*. Next-expected pointer rotates to Category E ↔ D Documentation Corpus ↔ RAG Boundary per S1303 §19 R3 + S1302 §19.1 + S1301 §19 downstream routing. **First-inventory landing in the library** — Cat F had no `platform_architecture_inventory.md` §3.N row at audit open; §4 Major Models + §7 Runtime Flows are load-bearing (not just referential). S1303 verifier-loop spot-checks caught two Agent-6 overreaches BEFORE Rigby SIGN: F3 "would fail at import time" → SOFT FAIL (try/except guard); F4 "confirmed dead code" → CANDIDATE per memory rule `feedback_verify_before_deleting_dead_code.md`. Consequence: SIGN cycles focused on substantive edges (metadata contract, D1 widen for wrong-model+wrong-field, Cat F ↔ Cat D reframe as OBSERVED GAP, maturity bounding, R1 split into R1.a/b/c) rather than evidence corrections. Only child audit to reach SIGN-clean in **2 cycles** (S1301 = 1, S1302 = 3). SIGN-clean verdict logged in audit frontmatter + §20.10 gating checklist 11/12 boxes ticked (Chris commit-gate = last).
- **2026-07-01 (S1304 open).** Cross-checked this file against `00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md`. Recent commits confirmed S1303 artifacts merged to `main` (PR #2778 = `6365f33f`); working tree clean on `main`. S1303 commit-gate resolved between sessions. Reconciliation: S1304 branches off `main` (not stacked on S1303) per playbook §16. Chris ratified D12 (launch cadence: PROCEED) + D13 (arc pin: RETAIN `pa-aa54193f240f4846`) via arc pin.
- **2026-07-01 (S1305 open).** Cross-checked this file against `00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md`. Recent commits confirmed S1304 artifacts merged to `main` (PR #2779 = `4271e913`); working tree clean on `main`. S1304 commit-gate resolved between sessions. Reconciliation: S1305 branches off `main` (not stacked on S1304) per playbook §16. Chris ratified D14 (launch cadence: PROCEED) + D15 (arc pin: RETAIN `pa-aa54193f240f4846`) via arc pin.
- **2026-07-01 (S1305 close).** Group 1300 current-child field advanced from *S1304 SIGN-clean (committed) + S1305 queued* to *S1305 SIGN-clean (commit-gated) + S1399 canonical summary queued next*. **5-child arc complete** — S1301 through S1305 all SIGN-clean and merged to `main` or commit-gated. Next-expected pointer rotates to Group 1300 canonical summary per parent §5 P6 slot. **Load-bearing methodology extension: verifier-loop pattern extended from hypothesis-correction to severity-correction** — S1305 downgraded Agent 6's CRITICAL AgentLearningService durability claim to MEDIUM via Redis AOF context (`settings.py:944 REDIS_APPENDONLY=True` + `:945 REDIS_APPENDFSYNC='everysec'`) matching S1302 T3 sibling classification. First library audit to explicitly apply verifier-loop to severity assertions from sub-agents, not just hypothesis assertions (S1304 pattern). Third child audit to reach SIGN-clean in 2 cycles (matching S1303 + S1304 discipline; S1301 = 1, S1302 = 3). Parent §3H 3 open questions closed at S1305 close: (i) `search_docs` cache location — has NO dedicated LRU (only `_load_provenance_docs` called from it); (ii) `MemoryPromotionService` runtime cache surface — pure DB I/O, no cache; (iii) `MemorySystem` active use — CONFIRMED active via Rigby SIGN cycle 1 grep at `ai_core/agents/intelligent_job_matcher.py:57`. SIGN pin `pa-56a527a2c5528508` retired at close (`updated_count: 2, retired: true`).
- **2026-07-01 (S1304 close).** Group 1300 current-child field advanced from *S1303 SIGN-clean (commit-gated) + S1304 queued* to *S1304 SIGN-clean (commit-gated) + S1305 queued next*. Next-expected pointer rotates to Category H Runtime Memory Correctness (narrow scope — Redis-loss + lru_cache staleness only) per parent §5 P5 slot + S1304 §14 D2/D6 first-order scope evidence. **Load-bearing methodology: partial invalidation of S1301 §19 D3 via S1304 verifier-loop** — S1301 broadly claimed both `DocumentEmbedding.source_type` + `ingested_via` are orphan-writes; direct file:line read at `content/embeddings.py:965-973` confirms `semantic_search_sync` applies `.filter(source_type__in=[...])` `source_filter` branch (owner-model-qualified consumer) + presentation at :1007. Only `ingested_via` remains F1-CANDIDATE orphan pending §19 R1 full-tree recheck per S1303 §14 F4-CANDIDATE discipline. Verifier-loop pattern prevents sibling-audit hypothesis propagation before it hardens into library-wide false consensus. Second child audit to reach SIGN-clean in **2 cycles** (matching S1303 discipline; S1301 = 1, S1302 = 3). SIGN-clean verdict logged in audit frontmatter + §20.10 gating checklist cycle 2 box ticked (Chris commit-gate = last remaining).
- **2026-07-01 (S1399 open).** Cross-checked this file against `00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_1305_MEMORY_RUNTIME_CORRECTNESS.md`. Recent commits confirmed S1305 artifacts merged to `main` (PR #2780 = `4b6f3419`); working tree clean on `main`. S1305 commit-gate resolved between sessions. Reconciliation: S1399 branches off `main` (not stacked on S1305) per playbook §16. Chris ratified D19 (launch cadence: PROCEED via short command "start research group 1399") + D20 (arc pin retention: RETAIN `pa-aa54193f240f4846` — carries S1300-S1305 context needed for S1399 synthesis) via arc pin.
- **2026-07-01 (S1399 mid-session).** Group 1300 canonical summary drafted at `docs/research/domains/memory/1399_memory_canonical_summary.md` (1224 lines, `status: draft`, `authority: research`, `category: canonical_summary`). Rigby SIGN cycle 1 on fresh isolation pin `pa-4fc3329d0db6484f` → verdict **SIGN-clean at High confidence, 0 must-fix**, 1 optional nice-to-have (docs↔code naming/category drift micro-pattern acknowledged as §4.5 adjacent evidence rather than promoted to formal F5 — Rigby explicitly said "not required if you want to keep exactly four"). All 4 pressure-test questions PASS: Q10 child contradictions resolved (§5.1-§5.5); Q11 anchor-update recommendations complete (§7 with 8 targeted proposals); Q12 cross-cutting patterns not missed (F1-F4 multi-child evidence + CANDIDATE vs CONFIRMED discipline preserved); Q13 follow-on queue rankings defensible (§8.1 21 items ranked by uncertainty × risk × unblocked flows). **First formal xx99 canonical summary in the library** — S1268-S1275 arc predated the xx99 convention per playbook §22 note. ARCHITECTURE_INDEX v17 → v18 bump applied same-commit per playbook §16 canonical-summary rule: added §1.21 for the summary + §8 timeline S1399 row + updated `last_verified` frontmatter. **Current row state:** in-progress (SIGN-clean, pending Chris commit-gate). **Row moves in-progress → Closed on Chris merge.**
- **2026-07-01 (S1399 close).** Chris commit-gated + merged S1399 canonical summary via PR #2781 (`6318787b`, squash merge, branch deleted). **Group 1300 arc formally closed** per playbook §17 graduation criteria — all 12 close criteria ticked (5 child audits shipped + SIGN-clean + committed; cross-cutting patterns named; consolidated domain shape delivered; contradictions resolved; unknowns documented; anchor recommendations proposed; follow-on queue ranked; delegated arcs cross-linked; change log complete; provenance appendix complete; Rigby SIGN Q10-Q13 cleared; Chris commit-gate). Group 1300 row moved from In-progress → Closed section this commit. **Post-close cleanup executed:** (i) S1399 SIGN pin `pa-4fc3329d0db6484f` retired via `session_tool.retire` (`updated_count: 2, retired: true, previously_active: true`). (ii) Group 1300 arc pin `pa-aa54193f240f4846` retirement DEFERRED to next-session open — Rigby refused self-retirement on currently-bound thread without `force=true`, warning "retiring it would silence dispatches mid-conversation. Pass force=true to override, then rotate the wrapper pin (`tools/pa_local.sh` line 70) before continuing." Correct sequence for next session: mint new arc pin (Group 1400 Revenue default lean OR single-child follow-on) → rotate `tools/pa_local.sh` line 115 → retire `pa-aa54193f240f4846` with `force=true`. (iii) `00-START-NEXT-SESSION.md` rotated to next-arc mission spec including D21 (next-arc launch cadence) + D22 (arc pin mint) decisions gating next-session launch. **Load-bearing methodology outputs of the arc** (per S1399 §10.2, formerly §10.4 pre-retrofit) canonicalized: F1/F4-CANDIDATE discipline; sibling-inheritance hypothesis-correction; severity-correction via sibling context. All three used across S1303 + S1304 + S1305 = two-triggers threshold met per playbook §20; playbook v3 additions eligible. **Meta-methodology §10 retrofit landed post-close** — S1399 renumbered from 11 sections to 12 sections; playbook §11.3 template updated same-commit per Chris directive that every xx99 canonical summary include §10 "What This Research Taught Us About How to Do Research." First application: S1399 (retrofitted). Memory rules `feedback_xx99_meta_methodology_section.md` + `feedback_docs_cascade_at_every_close.md` saved. **Follow-on queue eligible to open** per S1399 §8: Group 1400 Revenue (default lean per playbook §22 queue); S1304 §19 R1 `ingested_via` full-tree recheck; S1303 §19 R1.a/b/c `context_used` + `agent_results` verification; S1305 §19 R1 `platform_config` LRU F4-CANDIDATE audit; S1305 §19 R6 IntelligentJobMatcher production invocation audit; S1302 §15 T10 write-authority framework design-preparation ADR. Also eligible: Group 1700 Observability arc opens with 4 pre-scoped delegations from S1399 §9.2 (filter-drop telemetry × 2, dead-code / producer-only detection, EventBus adoption for Cat F, worker-recycle instrumentation for Cat H).

---

## Schema reference

Column semantics per OS §6.3:

- **Group** — session-ID range prefix (e.g., `1300` = Memory arc).
- **Domain** — human-readable domain name matching playbook §22
  queue entry.
- **State** — one of `in-progress` / `awaiting-summary` / `closed`
  / `stalled` / `not-started` per playbook §17 graduation states.
- **Owner pin** — active PA conversation pin for the arc; retire
  when arc closes.
- **Current parent** — path to the arc's parent scoping doc.
- **Current child** — the child slot actively being worked (or
  `queued` / `not yet launched`).
- **Last activity** — YYYY-MM-DD of most recent commit.
- **Dependencies** — cross-arc `dependencies_on:` from parent
  frontmatter.
- **Next expected** — the mission the next session in this arc
  should open with.

## Maintenance

- **Update trigger:** every research-class session close.
- **Update authority:** OS-managed via §14 completion contract.
  Claude writes; Chris ratifies commits.
- **Do not delete rows.** Closed groups stay in the closed
  section as historical record (never-delete rule per
  `docs/00-START-HERE/DOC_LIFECYCLE.md`).
- **Runtime automation:** eventually generated from
  `grep -rH "^status:" docs/research/domains/` + frontmatter
  parse. Manual for now (OS §17.4 Future).
