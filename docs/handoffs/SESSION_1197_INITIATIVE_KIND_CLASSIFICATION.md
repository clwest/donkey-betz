# Session 1197 — Initiative `kind` enum + Projects-in-Workspace-layer ship

**Status:** Wrapped clean. **7 PRs opened against `main`** (5 atomic ship + 1 INDEX rebuild + 1 close-out additions). All retargeted to `main` directly — no stacked-PR base-deletion footgun.
**Date:** 2026-06-22
**Active conversation:** `pa-ea12236c83eb4826` (continued from Session 1196).
**Prior session:** [`SESSION_1196_INITIATIVE_DIAGNOSTIC_CONTRACT.md`](./SESSION_1196_INITIATIVE_DIAGNOSTIC_CONTRACT.md).

## TL;DR

Reviving the Session 1193 cluster-recon insight that had been parked DEFERRED-pending-backbone (which shipped across Sessions 1194-1196). Locked Rigby's design memo via the agree-all decision card with Chris, then shipped: a 4-value `Initiative.kind` enum (orthogonal to `status`) + a small `related_initiatives` JSONField for directional Initiative-to-Initiative links + an idempotent classifier mgmt cmd that retro-labels existing rows per an 11-row SPEC mapping the 9 Donkey Betz clusters + a backfill-safety report cmd with a default-only detector.

**Net result:** 11 Initiative rows in the Donkey Betz workspace now carry intentional `kind` classification (5 project / 3 recurring_artifact / 2 investigation / 1 spec_backlog). The flat-deliverable problem Chris surfaced in Session 1193 has a first-class semantic overlay. Status remains the lifecycle axis; kind names the work shape.

## PRs shipped

| PR | Branch | Theme |
|---|---|---|
| **#2416** | `feat/session-1197-initiative-kind-migration` | Migration 0362 — `kind` CharField (4 choices, default=project, db_indexed) + `related_initiatives` JSONField (default=[]) |
| **#2417** | `feat/session-1197-initiative-kind-apply` | `apply_initiative_kind_classification` mgmt cmd — 11-row SPEC, idempotent `--dry-run` / `--apply`, two-pass split-pair linker |
| **#2418** | `feat/session-1197-initiative-kind-report` | `report_initiative_kinds` mgmt cmd — cross-tab + 2 heuristic flag signals |
| **#2419** | `feat/session-1197-initiative-kind-docs` | §6.4 added to `INITIATIVES_FIRST_BACKBONE.md` + AC11-14 + provenance entry |
| **#2420** | `feat/session-1197-initiative-kind-tests` | 14-case regression suite |
| **#2421** | `docs/session-1197-rebuild-index` | `docs/INDEX.md` rebuild after §6.4 add |
| **#2422** | `feat/session-1197-initiative-kind-closeout` | Rigby's close-out additions: idempotency rule + "safe placeholder" sentence + `default_only_projects` detector + AC15 + test #15 |

## Architecture — design lock from Rigby's memo

Two paths were on the table when this session opened:

| Option | Shape | Verdict |
|---|---|---|
| **A. Collections / Folders entity** | New model below Initiative — many-to-many membership of deliverables | **Rejected.** Use cases (M2M / pure-nav / nested hierarchy / rollups) don't exist today. Promote to a real model only when a workflow demands it. |
| **B. TRIAGE Initiatives as the "collection" primitive** | Use existing Initiative model with TRIAGE status as the container | Half-right — status was already overloaded; the missing axis was semantic type, not lifecycle. |
| **C. `kind` enum on existing Initiative** | Add semantic classification orthogonal to status | **Chosen.** Smallest schema change. Lifecycle (`status`) and work-shape (`kind`) are independently meaningful. |

Rigby's key argument for orthogonality: "If we collapse semantics into status, TRIAGE becomes a junk drawer again."

Two `kind` enum values handle the 4 natural patterns from the Session 1193 recon plus one container:

| `kind` | Shape | Examples |
|---|---|---|
| `project` | 5-stage arc, time-bounded, finish-line semantics | MLB Run Line Desk v1; Session 1184 Provenance Linkage |
| `recurring_artifact` | Periodic output stream, no finish line | COO Daily Analysis; Business News Tracker; Weekend Digest Issue Production |
| `investigation` | Recon / mapping / question-driven workstream — has DOD (question answered) but no implementation arc | Orchestration Mapping; Spider Context Utilization Recon |
| `spec_backlog` | Follow-up engineering items that aren't a project arc but still need an attribution anchor | Session 1192 Workspace Consolidation Follow-ups |

For hybrid clusters that produce both a finish-line artifact AND an ongoing stream, the design uses split-pair Initiatives linked via `related_initiatives` JSON with a directional `spawns` / `spawned_from` relation pair (3a↔3b for Spider Context, 9a↔9b for Weekend Digest).

## Behavioral invariants — what's now true post-merge

- `Initiative.kind` field exists with 4 enum values. Default = `project` (safe placeholder, **not** a semantic assertion — see "silent-rot signal" below).
- `Initiative.related_initiatives` JSONField stores a list of directional links. Schema: `[{"id": "<uuid>", "relation": "spawns"|"spawned_from", "note": "..."}]`. No FK.
- `apply_initiative_kind_classification --apply` is idempotent — re-running against current state produces 0 net writes (validated locally + AC12).
- Split-pair links MUST be bidirectional. The apply cmd writes both directions in a single transaction. Both must skip duplicate `(id, relation)` pairs on re-run.
- Status orthogonality: the apply cmd does NOT touch `status` on existing rows. Kind is a labeling overlay, not a lifecycle reclassification.
- `report_initiative_kinds` surfaces a `default_only_projects` list — any project Initiative not named in the SPEC. This is the silent-rot detector: visible signal that a row got default kind via migration but was never explicitly reviewed.

## Local apply outcome on Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)

```
Kind distribution after classification:
  project              5  (1, 2, 3b, 8, 9a)
  recurring_artifact   3  (5, 7, 9b)
  investigation        2  (3a, 6)
  spec_backlog         1  (4)
  ──────────────────  ──
  Total               11

Existing rows matched (no creates, kind=project default already aligned):
  077ff8b4  Session 1171 — ML Queue + Auth Middleware Triage    (ARCHIVED)
  997fb39b  MLB Run Line Desk v1 — 24h Board + DM Alerts        (ACTIVE)
  3e59354c  Weekend Digest Autopilot — Build/Ship                (TRIAGE)

New rows created (8):
  Session 1184 — Provenance Linkage                              project / COMPLETED
  Spider Context Utilization — Recon & Findings                  investigation / COMPLETED
  Spider Context Utilization — Retune & Implementation           project / TRIAGE
  Session 1192 — Workspace Consolidation Follow-ups              spec_backlog / TRIAGE
  COO Daily Analysis — Daily Run                                 recurring_artifact / ACTIVE
  Orchestration Mapping Investigation — Parallel Agent Runs      investigation / TRIAGE
  Business News Tracker — June 2026                              recurring_artifact / ACTIVE
  Weekend Digest — Issue Production (Weekly)                     recurring_artifact / ACTIVE

Split-pair links written (4, bidirectional):
  3a (Recon)      —spawns→         3b (Retune)
  3b (Retune)     —spawned_from→   3a (Recon)
  9a (Build/Ship) —spawns→         9b (Issue Production)
  9b (Issue Prod) —spawned_from→   9a (Build/Ship)

Default-only detector (3 legitimate "review me" rows on first run):
  7e23d621  Tool Migration Hardening                            (spine Initiative 3)
  2071a9c6  Agent Capability Map + Router Contracts             (spine Initiative 2)
  6941372d  Initiatives-First Wiring + No-Orphan Output         (spine Initiative 1)
  ↑ All real long-arc projects — kind=project is correct. Flagged because they
    pre-existed the SPEC and weren't explicitly classified by the apply cmd.

Re-apply: 0 creates / 0 kind updates / 0 link writes (idempotent ✓).
```

## Rollback / disable levers

| Surface | Lever | Effect |
|---|---|---|
| Migration 0362 | `python manage.py migrate core 0361` | Drops both new fields. Additive-only migration, safe rollback. |
| Apply cmd creates | `Initiative.objects.filter(created_by='session-1197-kind-classifier').delete()` | Removes the 8 new rows. Existing-row kind updates would need manual reversion (but in practice all were no-ops because default=project). |
| Apply cmd kind writes (existing rows) | `Initiative.objects.update(kind='project')` | Resets everything to default. Re-run apply cmd to re-classify. |
| Split-pair links | `Initiative.objects.update(related_initiatives=[])` | Wipes all link entries. Re-run apply cmd to re-wire. |
| Per-row kind override | `Initiative.objects.filter(id='<uuid>').update(kind='<new_kind>')` | Manual reclassification. Apply cmd does not touch rows that already match the SPEC. |
| Report cmd | No state; read-only. Removing the file is the only way to disable. | — |

The whole ship is data-layer reversible. Worst case is `migrate core 0361` + a `kind` field drop, which loses the 8 new rows' classification + the 4 link entries but doesn't damage upstream FK relationships.

## What's deliberately NOT in scope

- **Enforcement on Initiative create paths** — new Initiatives still land at `kind=project` default with no required field. Rigby and I agreed to defer enforcement until we've watched a week of "default-then-classify-later" behavior. The `default_only_projects` detector is the visibility signal that tells us whether enforcement is warranted.
- **Status reclassification** — the apply cmd does NOT touch status on existing rows even when the SPEC suggests a different one (e.g., cluster 1's `077ff8b4` is ARCHIVED locally; SPEC notes COMPLETED would be semantically nicer). Status changes belong in a separate operator pass.
- **Cluster 1's 4 sub-task initiatives** (1171-1/2/3/4) — left at kind=project default. The SPEC handles the wrapper row only.
- **`20d520c6` umbrella** (the session-1197 work container) — kept as kind=project per Rigby's recommendation since the work that followed shipped an implementation, not just an answer.
- **Workspace UI filter by kind** — vertical slice step 6 in the original decision card. Parked as P2/P3 for follow-up once kind enum has bedded in.

## Open items for Session 1198

| Item | Priority | Notes |
|---|---|---|
| **Merge the 7 PRs** | P0 | All target `main`. Earliest-first (#2416 → ... → #2422) is cleanest because later PRs reference earlier work, but no PR hard-depends on a prior merge — they all rebase cleanly. |
| **24h watch on `default_only_projects` signal** | P1 (time-gated) | Start 2026-06-23. Re-run `report_initiative_kinds --workspace-id <DBZ>`. If new project rows appear in the list, that's a callsite filing project Initiatives without classification → candidate for enforcement Phase 2. |
| **§6.2 Phase 2 inference design** | P2 | Carryover from 00-START-NEXT-SESSION. Now has a real input shape: orphan Initiative creators (Rigby=33, ResearchAgent=24, ClaudeCode=11, ContentWriterAgent=9) can be cross-referenced against `kind` defaults to seed inference rules. |
| **Plan C 7-day watch + Phase 2 hard-reject flip** | P1 (time-gated, NEW) | Carryover. Starts 2026-06-29. Independent of this session's work. |
| **Session 1196 7-day watch** | P1 (time-gated) | Carryover. Starts 2026-06-29. Independent of this session's work. |
| **`load_all_agents_advisors` baseline fix (155→87)** | P2 | Pre-existing CI red. Unaffected by this session. |
| **Local test DB infra (pgbouncer CREATE DATABASE blocker)** | P2 | Re-surfaced in PR #2420 / #2422 — pgbouncer transaction pool can't proxy CREATE DATABASE. CI runs the suite; local needs `DJANGO_TEST_DATABASE_URL` to a non-pooled DSN. |

## Memory candidates (surfaced; not yet persisted)

1. **`kind` ⊥ `status` is a model design pattern, not a one-off.** When a model has both lifecycle AND semantic-type concerns, split into two fields. Don't overload status. Rigby's "TRIAGE becomes a junk drawer again" argument is the test.
2. **Hand-trim `makemigrations` output when bundling sees unrelated drift.** `makemigrations` pulled 16 AlterField ops + 4 Narrative CreateModel ops belonging to Session 1196 parked drift into PR-A's auto-output. Trimmed by hand to keep PR atomic. Worth a memory: when adding a single field, expect to trim — don't blindly accept auto-output.
3. **Idempotency rule for JSON-list link writes:** writers MUST skip duplicate `(id, relation)` pairs. Otherwise re-running the writer doubles the entries. Codified in §6.4.
4. **Default-value detector pattern.** When a migration sets a default on existing rows, downstream code can't distinguish "intentional choice" from "rows that got default but were never reviewed." Pair every default-set migration with a detector that surfaces unreviewed rows. Generalizes beyond this session.

## Pinned reference (Donkey Betz workspace)

- **Workspace ID:** `b4503364-2573-4401-9e28-61a739e0ce50`
- **Initiative count (this session close):** 11 in DBZ workspace (was 3 — added 8 from clusters 2/3a/3b/4/5/6/7/9b)
- **Platform-wide Initiative count:** 42 (was 34 — added the same 8)
- **Spine Initiatives:** still 3 ACTIVE, all kind=project, all in `default_only_projects` detector flag list (expected — they pre-existed the SPEC)

## Collaboration shape

- **Claude owned:** SPEC design + 7 PRs + migration trim + apply cmd + report cmd + handoff doc + Rigby loops at every design decision point.
- **Rigby owned:** the locked design memo (4-kind enum + status orthogonality + Collections-vs-Initiative argument + tag-link convention + idempotency rule + safe-placeholder framing + default-only detector idea).
- **Chris owned:** the agree-all ratification on the 11-row classification + fold-into-PR-7 call on Rigby's close-out additions.

The pattern worked because the 5-PR + 1-INDEX scope was small enough to ship in a single session without burning Rigby's iteration cap. PR-F (close-out) was a clean fold of Rigby's review feedback rather than a separate scope add.

---

**Conversation thread `pa-ea12236c83eb4826`** is still open at session close. Session 1198 can continue on it or spin fresh.

**No prod actions taken** — local-only per memory rule. The migration + apply + report all ran against local DB. Production rollout would follow the same playbook as Session 1196 P0: prod apply on Operator's go-signal, then 24h watch.
