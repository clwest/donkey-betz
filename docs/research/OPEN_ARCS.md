---
title: "Open Arcs — cross-session manifest of research groups in flight"
status: active
authority: state
session_added: 1279
last_updated: 2026-07-02
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
| **1300** | Memory / Knowledge / Embeddings | in-progress | `pa-aa54193f240f4846` | `1300_memory_domain_scoping.md` (S1300) | *S1301 queued — not yet launched* | 2026-07-01 | none | S1301 RAG Retrieval Lanes (Category D). Open decisions D6 (launch cadence) + D7 (parent SIGN routing) awaiting Chris ratification before S1301 begins. |

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

*(none — installed clean at S1279)*

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
