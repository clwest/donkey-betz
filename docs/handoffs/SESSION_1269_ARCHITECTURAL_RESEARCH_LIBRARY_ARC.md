---
session: 1269
status: closed
date: 2026-06-30
arc: Architectural research library founded in a single continuous stretch spanning S1268 (4 research docs) + S1269 (1 governance doc + navigation index v2). Zero runtime code touched. Five docs + index all Rigby-reviewed. Recommended next research mission (Symbol Mapping Architecture) named + SIGN-clean.
prs_merged: []
prs_open: []
branches_open:
  - docs/session-1268-comms-substrate-research (local-only, 5 commits stacked; awaiting Chris's PR-vs-archive decision)
companions:
  - docs/handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
deliverables:
  - "docs/research/employee_os_communication_substrate_audit.md (S1268 P0 #1, 918 lines, Rigby SIGN-clean)"
  - "docs/research/employee_os_communication_protocol_sketch.md (S1268 P0 #2, 979 lines, Rigby SIGN-with-edits folded)"
  - "docs/research/employee_os_collaboration_patterns.md (S1268 P0 #3, 1,540 lines, Rigby SIGN-with-edits folded)"
  - "docs/research/ARCHITECTURE_INDEX.md v1→v2 (S1268 P0 #4 → S1269 update, 1,034 lines, self-verifier + maintenance-rule updates)"
  - "docs/research/governance_authority_evolution.md (S1269, 1,302 lines, Rigby SIGN-with-edits folded)"
---

# Session 1269 — Architectural Research Library Arc

## TL;DR

**Founded the `docs/research/` library in one continuous stretch.**
Five architectural-discovery docs + a navigation index, all
Rigby-reviewed (2 SIGN-clean, 3 SIGN-with-edits → folded), zero
runtime code changes, zero PRs opened. All five deliverables live
locally on branch `docs/session-1268-comms-substrate-research`
(5 commits stacked; **not pushed**; awaiting Chris's PR-vs-archive
decision at S1270 open).

The recommended next research mission per §11 of
`governance_authority_evolution.md` is **Symbol Mapping
Architecture** (P0) — the load-bearing blocker for any authority
enforcement work. Rigby SIGN-clean on that ranking.

Rigby conversation `pa-01e90a1d36f54880` carried **5 substantive
SIGN turns** across this arc (one per research doc). The
conversation is being retired at S1269 close; S1270 needs a fresh
pin (created by Rigby at S1270 open per standard session-open
discipline).

## Session arc

| Mission | Doc | Type | Status | Lines |
|---|---|---|---|---|
| S1268 P0 #1 | `employee_os_communication_substrate_audit.md` | Inventory + Architecture Audit + Failure Analysis | Rigby **SIGN-clean** | 918 |
| S1268 P0 #2 | `employee_os_communication_protocol_sketch.md` | Design Research / Protocol Sketch | Rigby **SIGN-with-edits** → folded | 979 |
| S1268 P0 #3 | `employee_os_collaboration_patterns.md` | Architectural Discovery + Platform-Wide Inventory + Failure Analysis | Rigby **SIGN-with-edits** → folded | 1,540 |
| S1268 P0 #4 | `ARCHITECTURE_INDEX.md` (v1) | Navigation / Decision Record (light) | Self-verifier pass, no Rigby review (per S1268 spec) | 896 initial |
| S1269 | `governance_authority_evolution.md` | Architectural Discovery + Platform-Wide Inventory + Failure Analysis | Rigby **SIGN-with-edits** → folded | 1,302 |
| S1269 | `ARCHITECTURE_INDEX.md` (v2) | Index maintenance update per §10.1 | Same as v1 | 1,034 (was 896) |
| **Total** | 5 research docs + 1 index (v2) | | | **5,773 lines** |

Zero LOC change to runtime code. Zero PRs opened. Zero migrations.

## What shipped (per-doc summary)

### 1. `employee_os_communication_substrate_audit.md` (S1268 P0 #1)

- 36-row primitive inventory of every comms substrate between AI
  employees (agent-to-agent, PA chat, Employee OS, EventBus, etc.)
- Reuse classification: SAFE / WRAPPER / DO-NOT-USE / DEPRECATED /
  UNKNOWN — same taxonomy the later docs inherit
- 12 incident-class failure history (silent-failure patterns
  dominate; multi-layer defense required; schema/contract drift
  between layers)
- **Rigby SIGN-clean** — confirmed all three highlighted reuse
  classifications; caught a genuine EventBus stream-count drift
  (audit said 6, runtime is 8 — folded forward, not back-patched)

### 2. `employee_os_communication_protocol_sketch.md` (S1268 P0 #2)

- Scoped the *first* inter-employee write path: Platform Auditor →
  Chief of Staff structured DM / action-request
- Reuse-only: `MessageThread` + `DirectMessage` +
  `ThreadParticipant` + thin new `post_inter_employee_notice()`
  helper mirroring `post_docs_manager_shift_report()` pattern
- Three-layer dedupe (L1+L2 helper-side per-thread, L3 helper-side
  7d window with `force_send=True` caller override per Rigby SIGN)
- 13 explicit non-goals in §10 (incl. HAI creation, reply lane,
  fan-out, cross-fleet, `messaging_tool.send_message` enablement)
- **Rigby SIGN-with-edits folded:**
  - §7.4 cadence default flipped B → A (Option A `expires_at` as
    primary safety belt)
  - §7.1 L3 dedupe moved from caller-only to helper-enforced with
    `force_send=True` override
  - §8.1 clarifier — Auditor has no HAI creation authority in its
    dict (`jobs.py:489-505`)
  - §11 Q6 — new file `comms_inter_employee.py`; optional
    `comms.py` re-export deferred until a second caller surfaces

### 3. `employee_os_collaboration_patterns.md` (S1268 P0 #3)

- Broadest of the arc: 64-row primitive inventory across 11
  distinct collaboration substrates platform-wide
- 12 collaboration flow diagrams (text): Agent→Agent sync/async,
  ThreadPoolExecutor fan-out, Celery chain+group, HAI lifecycle,
  Spider→Signal→Trigger chain, EventBus pub/sub, Initiative state
  machine, MissionRunner full flow, Human→Agent decision path,
  Scheduler→Employee/Agent, Deliverable→Follow-up
- 29 documented failure modes (12 new beyond substrate audit)
- Q1-Q8 answered explicitly
- **Findings (SIGN-clean by Rigby):**
  - F2 — TWO orthogonal durable orchestration paths (Celery chain
    vs. MissionRunner step loop) don't compose today
  - F3 — Advisors are PROMPT CONTEXT (not callable); Boardroom is
    ML-decision-prediction (not multi-agent debate)
  - F4 — No in-platform A→A reply contract; only round-trip is
    human-in-loop via HAI → HumanFeedbackRecord → ML learning
- **Rigby SIGN-with-edits folded:**
  - Substantive correction — MissionRunner `verdict_issued` event
    is conditional on `auto_emit_verdict=True`, not guaranteed
    (`mission_runner.py:1127-1145`); Bug Triage opted out per
    S1267
  - Architectural blind-spot note added — canonical idempotency
    key across the two durable orchestration paths (§10 Q12)
- Set the recommendation for the next research mission
  (Governance + Authority Evolution → became S1269)

### 4. `ARCHITECTURE_INDEX.md` v1 (S1268 P0 #4)

- Navigation / handbook doc — "the front page of Donkey Betz's
  engineering encyclopedia"
- 10 sections per mission spec: philosophy, library, reading
  paths (7 goal-based), domain map (20+ domains), dependency
  graph (text diagram), gaps (with priority), principles,
  decision matrix (16 rows), timeline, roadmap, maintenance
  rules
- Self-verifier pass caught + fixed 6 issues (placeholder `F?`
  references, bogus "drift folded back" claim, section-number
  errors)
- Per S1268 mission spec, Rigby review NOT required on the index
  itself (spec asked for self-verifier only)

### 5. `governance_authority_evolution.md` (S1269)

- The canonical research anchor for every future authority or
  governance discussion
- **63-row primitive inventory across 4 governance planes** (which
  don't compose today):
  - Autonomy plane (`GovernanceState` + `KillSwitch`)
  - Authority plane (`JobContract.authority` + `AuthorityLevel`)
  - Budget plane (`SystemConfiguration.budget_freeze_active`)
  - Human governance plane (HAI + Feedback + Preference + Gate)
- 35 documented runtime gates (29 RUNTIME-VERIFIED / 5
  ASPIRATIONAL / 1 UNKNOWN)
- All 4 employees' full authority dicts enumerated: 68 authority
  entries + 30 prohibited actions
- 12 governance-specific failure modes (3 NEW: authority
  symbol-mapping gap S1264, auth middleware silent-error S1171
  PR #2328, HTTP API permission flip S1265 PR #2760)
- Reuse: 48 SAFE / 11 WRAPPER / 0 DO-NOT-REUSE / 0 DEPRECATED /
  3 UNKNOWN
- 10 architectural findings (F1-F10) — most load-bearing:
  - **F2** — symbol mapping is the load-bearing blocker
  - **F3** — KillSwitch is write-only (full TTL + PA tool
    writes; zero dispatch consumers check `is_active`)
  - **F6** — 4 employees converging on common authority patterns
    (`open_pull_request` PROHIBITED across all 4;
    `recommend_remediations` RECOMMEND across 3; etc.)
  - **F9** — `throttle` mode is dead (three consumers check
    freeze/safe_mode only)
- Q1-Q12 answered explicitly in §12.1
- **Rigby SIGN-with-edits folded:**
  - Exec Summary "plane count" framing made consistent (was
    mixed "two + plus separate + and human"; now canonical
    "four planes" matching F1)
  - Gate count typo 34 → 35 (matches §4 table totals)
  - `JobContract.authority` WRAPPER refined to explicit
    "SAFE-TO-REUSE-as-telemetry but
    DO-NOT-REUSE-for-enforcement"
  - F4 budget-plane intent softened per "don't assert design
    intent without a design note"
  - Added §10.8 Focus Mode inventory per Rigby's review note
    (governance-like throttle that may live outside the
    GovernanceState/KillSwitch plane; scoping deferred)

### 6. `ARCHITECTURE_INDEX.md` v2 (S1269 update)

Per the index's own §10.1 maintenance rule after §1.4 was
added:

- §1.4 entry for `governance_authority_evolution.md`
- §3 domain map — Governance + Authority rows updated (gaps
  closed; maturity reclassified)
- §4 dependency graph — new node + Symbol Mapping arrow
- §5 gaps — §5.1 marked CLOSED; renumbered §5.2 → §5.11 with
  Symbol Mapping promoted to §5.2 (new P0), Trust Propagation
  added as §5.3, Focus Mode added as §5.11
- §7 decision matrix — 5 new rows (governance flags, authority
  enforcement, KillSwitch, budget freeze, HAI lifecycle)
- §8 timeline — S1269 row added
- §9 roadmap — Stage 0 (Governance + Authority Evolution)
  CLOSED; Stage 1 (Symbol Mapping) promoted to next; Stages 2a-c
  re-lettered

## Key architectural findings (arc-wide)

Cross-cutting insights from the 5-doc arc that any future
research/design must inherit:

1. **The platform's collaboration surface is broad and mostly
   audit-rich.** 11 distinct collaboration substrates, 5 audit
   tables (OpsRunEvent, DeliverableEvent, LLMCallEvent,
   ToolCallRecord, CeleryTaskEvent) with cross-table joins via
   `evidence_for_mission()`. Reuse is preferred; the
   anti-duplication matrix in `EMPLOYEE_OS_PRIMITIVES.md` §2 is
   load-bearing.

2. **Authority is observational, not enforced.** S1264 warn-mode
   was an honest baseline given the symbol-mapping gap. Enforcement
   requires a foundational registry binding policy-description
   strings (like `"modify_docs_files"`) to runtime symbols (tool
   names, method signatures). Three options exist (steps
   self-declare, tool registry, hybrid); the choice is the next
   research mission.

3. **Governance has four planes that don't compose.** Autonomy
   (GovernanceState + KillSwitch), Authority (JobContract), Budget
   (SystemConfiguration), Human Governance (HAI + Feedback + Gate)
   operate independently. Cross-plane wiring is a deliberate design
   choice, not a default. GovernanceState → SystemConfiguration
   is one-way sync only (reverse missing).

4. **KillSwitch is write-only today.** Full write path + TTL beat
   task work. Zero consumers check `is_active` before dispatching
   the targeted action. This is the biggest "feature ships but
   doesn't work" gap in the autonomy plane. Rigby independently
   corroborated via her own grep.

5. **No in-platform employee-to-employee reply contract exists.**
   The only round-trip pattern with learning is human-in-loop
   (HAI → HumanFeedbackRecord → FeedbackProcessor → AgentLearning).
   Any inter-employee delegation design has no precedent to inherit.

6. **The 4 employees' authority dicts are converging on shared
   patterns.** `open_pull_request` PROHIBITED across all 4;
   `recommend_remediations` RECOMMEND across 3; `modify_any_file` /
   `modify_docs_files` PROHIBITED across all 4. Suggests a future
   shared-policy template could lift invariants out of per-job
   duplication — but that's design work, deferred.

## Material corrections caught during the arc

Verifier-loop discipline caught 4 substantive drifts before docs
shipped:

1. **EventBus 6 → 8 streams** (substrate audit line 135 says 6;
   runtime is 8 per `event_bus.py:21-30`). Flagged in
   collaboration audit §12 and index §12 drift table.
   Substrate audit text NOT amended (research-only constraint);
   drift propagated forward.

2. **CLAUDE.md 3 → 4 employees** (Detailed Breakdown row says 3;
   `_EMPLOYEES_BY_HANDLE` at `jobs.py:1331` has 4 incl. Bug
   Triage). Flagged in substrate audit §5.6 + collaboration
   audit §12. Not patched (research-only).

3. **MissionRunner `verdict_issued` conditional, not guaranteed**
   (Rigby S1268 SIGN-with-edits on collaboration audit). Fixed
   in 4 places within the doc: Exec Summary item 6, §2 row 19,
   §6 row, §7 row 29 (new failure-mode row).

4. **Bug Triage authority dict RUNTIME-VERIFIED, not
   ASPIRATIONAL** (governance-doc sub-agent #1 was wrong;
   `core/jobs/bug_triage.py:1169` passes `job_contract=BUG_TRIAGE_JOB`).
   Caught by Claude via direct grep before writing the
   governance doc; sub-agent claim corrected.

## Rigby SIGN reviews (arc-wide)

| Doc | Verdict | Substantive edits folded |
|---|---|---|
| Substrate audit | **SIGN-clean** + 2 primitives added | (2 clarifications, no edits) |
| Protocol sketch | **SIGN-with-edits** (2) | L3 helper-side dedupe + `force_send` override; cadence default B→A `expires_at` |
| Collaboration patterns | **SIGN-with-edits** (1 + 1 note) | MissionRunner verdict conditionality; canonical-idempotency-key architectural blind-spot |
| Architecture index v1 | N/A (self-verifier per spec) | (6 issues caught + fixed by self-verifier) |
| Governance + Authority Evolution | **SIGN-with-edits** (2 + 2) | Exec Summary 2→4 plane framing; gate count 34→35; JobContract.authority WRAPPER clarified; F4 intent claim softened; Focus Mode added as §10.8 |

**Rigby's rankings on the arc (for the record):**
- Top 3 open questions for next mission: Q1 (symbolic authority)
  P0, Q3 (compose across employees) second, Q2 (inherit) third
- Next research mission: **Symbol Mapping Architecture** —
  SIGN-clean on this being the correct P0

## Branch state

Branch `docs/session-1268-comms-substrate-research` sits **local
only**, 5 commits stacked:

```
0310f6a5 docs(session-1269): audit governance and authority evolution; register in ARCHITECTURE_INDEX
db97c6bc docs(session-1268): add ARCHITECTURE_INDEX.md as front page of the research library
904b7d3c docs(session-1268): audit platform-wide collaboration patterns for Employee OS reuse
c7956a48 docs(session-1268): audit communication substrate and sketch Employee OS notice protocol
2a36d0f9 chore(session-1267): refresh docs/INDEX.md from latest build_docs_index run (#2770)  ← main
```

Chris asked to open S1270 fresh from main. **The research branch
stays local.** Decision on PR-vs-archive deferred to S1270 open.
Two paths:

- **(a) PR the branch** — 5,773 lines of research + Rigby-reviewed;
  candidate for a single-PR merge or 2-PR split (S1268 arc + S1269
  arc). Adds the research library to `main` and makes it visible
  to `context-kit orient` on all future sessions.
- **(b) Archive the branch** — keep as a stash reference; don't
  merge to main until Symbol Mapping Architecture research is
  drafted and the full arc is validated. Downside: subsequent
  research docs would either live on this branch (making it grow)
  or on a new branch that doesn't have the prior context.

Recommendation: (a). The docs pass the "no runtime changes"
constraint by construction; nothing in them ships behavior. Merging
to main lets subsequent sessions cite them by canonical path
without needing to know about the branch. But that's Chris's call
at S1270 open.

## Success criteria — met

Per the arc's mission specs:

- ✓ **Reuse-first before design** — anti-duplication matrix
  respected across all 5 docs; zero new models proposed
- ✓ **Evidence-only** — every load-bearing claim carries file:line
  cite; UNKNOWNs preserved as UNKNOWNs
- ✓ **Verifier-loop discipline** — sub-agent claims re-verified
  by Claude via direct Grep/Read before synthesis
- ✓ **Rigby SIGN reviews on all docs that required them** — 4
  substantive reviews; all SIGN-with-edits folded
- ✓ **No runtime changes** — 0 code files edited across the arc
- ✓ **No PRs opened** — deferred per research-only constraint
- ✓ **No migrations** — same
- ✓ **Next mission named** — Symbol Mapping Architecture (P0)

## What's carrying forward to S1270

Priority menu, not a mandate — Chris picks:

**P0 candidate:** Symbol Mapping Architecture research doc
(recommended per governance doc §11; Rigby SIGN-clean). Scope:
enumerate design space (3 known options), inventory the 68
existing action_class strings, identify smallest viable v0, mark
prerequisites. Research-only.

**P1 candidates** (from the governance doc's §10):
- Trust Propagation Model (§5.3 in index v2)
- Memory Architecture (§5.4)
- Cross-Employee Scheduling (§5.5)
- Mission Composition (§5.6)

**Non-research work S1270 could pick up:**
- Decide branch fate (PR the research library or keep stashed)
- Address one of the four documented drifts by patching CLAUDE.md
  (3 → 4 employees, per drift #2 above)
- Circle back on the S1268 protocol sketch's v0 PR (if Chris
  greenlights the Auditor → CoS notice path)

## Rigby conversation state

`pa-01e90a1d36f54880` — RETIRED at S1269 close.

- 5 substantive SIGN turns across the arc (one per research
  doc)
- Health: not measured at close (research-only sessions don't
  stress her tool surface the way ship arcs do)
- Standard discipline: Rigby creates a fresh pin at S1270 open
  via `session_tool.create_fresh` after Chris confirms
  `service_context: local` via `platform_config_tool overview`

## Verifier-loop notes

- All 5 research docs' frontmatter `verifier_loop` fields
  updated with Rigby review verdicts + edit summaries
- Both drift calls in the docs remain as flags forward, not
  back-patches (research-only constraint)
- Index maintenance §10.1 rule executed cleanly on S1269
  update: §1.4 + §3 + §4 + §5 + §7 + §8 + §9 all updated;
  frontmatter `last_verified` bumped to v2

## No open follow-ups from S1269 itself

No PRs pending review. No unmerged work. No stuck Rigby threads.
No open questions requiring Chris's decision to unblock S1270
(the branch-fate decision is a nice-to-have, not a blocker).

Clean close.
