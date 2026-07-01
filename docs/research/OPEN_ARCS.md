---
title: "Open Arcs — cross-session manifest of research groups in flight"
status: active
authority: state
session_added: 1279
last_updated: 2026-07-01 (S1304 close — Group 1300 current-child advanced to S1304 SIGN-clean commit-gated + S1305 queued)
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

| Group | Domain | State | Owner pin | Current parent | Current child | Last activity | Dependencies | Next expected |
|-------|--------|-------|-----------|----------------|---------------|---------------|--------------|---------------|
| **1300** | Memory / Knowledge / Embeddings | in-progress | `pa-aa54193f240f4846` | `1300_memory_domain_scoping.md` (S1300) | `1304_memory_docs_rag_boundary_audit.md` (S1304, SIGN-clean 2026-07-01 via fresh isolation pin `pa-2614a91a920642fa` after 4-must-fix fold + 1-cycle verification pass; commit-gated on Chris per playbook §16). Prior children: `1301_memory_rag_retrieval_lanes_audit.md` (S1301, closed on `main` via PRs #2775 + #2776); `1302_memory_persistence_architecture_audit.md` (S1302, closed on `main` via PR #2777 = `c053272a`); `1303_memory_conversational_thread_memory_audit.md` (S1303, closed on `main` via PR #2778 = `6365f33f`). Next: S1305 queued. | 2026-07-01 | none | **S1305 Runtime Memory Correctness (Category H narrow scope).** Per parent §5 P5 slot: Redis-loss on worker recycle + `lru_cache(1)` staleness only; NOT ops-in-general (per parent §7 anti-scope — Celery worker RSS, PID cache, OBJC_DISABLE_INITIALIZE_FORK_SAFETY, macOS SIGSEGV all remain OUT of scope). Inherits from S1304: D2 lru_cache(1) staleness gap at `td_handlers_ops.py:78-93` as first-order scope evidence; D6 provenance rebuild cadence unscheduled as related concern (worker restart is the invalidation mechanism); T2 remediation options (worker restart trigger vs file-watcher vs Redis TTL vs Redis-backed store) as candidate design surface. Also inherits from S1302: AgentLearningService Redis-only durability (§14 debt d) with no `.expire()` at `agent_learning_service.py:462-483`. Scope discipline: NARROW — memory-correctness drift only, not ops-flavored infrastructure questions. |

> **Priority.** **Group 1300 is the arc that spawned this entire
> research plan** — the Memory scoping session that surfaced the
> parent-with-children pattern which then drove playbook v2, the
> Research OS, and the S1279 installation. **Finish Group 1300
> before opening any new arc.** Full sequence: S1301 → S1302 →
> S1303 → S1304 → S1305 → S1399 canonical summary. Group 1400
> Revenue and everything else in the "Not started" section waits
> until Group 1300 either closes or reaches a natural pause point
> where Chris chooses to parallelize.

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

## Not started (playbook §22 queue)

**Blocked on Group 1300 completion** unless Chris explicitly
parallelizes. Group 1300 is the active priority (see In-progress
above).

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
- **2026-07-01 (S1304 close).** Group 1300 current-child field advanced from *S1303 SIGN-clean (commit-gated) + S1304 queued* to *S1304 SIGN-clean (commit-gated) + S1305 queued next*. Next-expected pointer rotates to Category H Runtime Memory Correctness (narrow scope — Redis-loss + lru_cache staleness only) per parent §5 P5 slot + S1304 §14 D2/D6 first-order scope evidence. **Load-bearing methodology: partial invalidation of S1301 §19 D3 via S1304 verifier-loop** — S1301 broadly claimed both `DocumentEmbedding.source_type` + `ingested_via` are orphan-writes; direct file:line read at `content/embeddings.py:965-973` confirms `semantic_search_sync` applies `.filter(source_type__in=[...])` `source_filter` branch (owner-model-qualified consumer) + presentation at :1007. Only `ingested_via` remains F1-CANDIDATE orphan pending §19 R1 full-tree recheck per S1303 §14 F4-CANDIDATE discipline. Verifier-loop pattern prevents sibling-audit hypothesis propagation before it hardens into library-wide false consensus. Second child audit to reach SIGN-clean in **2 cycles** (matching S1303 discipline; S1301 = 1, S1302 = 3). SIGN-clean verdict logged in audit frontmatter + §20.10 gating checklist cycle 2 box ticked (Chris commit-gate = last remaining).

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
