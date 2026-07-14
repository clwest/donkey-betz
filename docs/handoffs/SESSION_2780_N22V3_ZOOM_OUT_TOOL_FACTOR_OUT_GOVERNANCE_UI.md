---
title: "SESSION 2780 — N22 v3: zoom_out_tool factor-out + SIGN Ledger UI"
session: 2780
status: closed
date: 2026-07-13
close_pr: 3172
close_pr_merge_sha: b16b3b981
arc: n22v3_zoom_out_ledger_workspace_ui
predecessor: SESSION_2779_N22V2_ZOOM_OUT_LEDGER_READ_SURFACE.md
---

## §1. What shipped

The second half of the N22 arc — the S2779 fold that named its own successor.

S2779 shipped `ops_tool.zoom_out_ledger` as Rigby's read surface for the
zoom-out concern ledger, and simultaneously classified `future_trigger` on
"ops_tool scope creep" with two explicit trigger conditions. Trigger B
("first non-Rigby consumer of zoom_out_ledger") fires the moment Chris
gets a UI surface. S2780 pointed at that UI, saw the trigger fire, and
executed the factor-out in the same PR per PLAYBOOK-6.10.8 discipline.

**Factor-out shipped:**

- **New `zoom_out_tool` PA tool** in `core/services/td_handlers_governance.py`
  (`GovernanceHandlersMixin`) — moved from `ops_tool.zoom_out_ledger`.
  Action `list` (v1); dedicated home for future governance-scope tools.
- **New `/api/governance/zoom-out-ledger/` REST endpoint** in
  `core/views_governance.py` — separate namespace from `/api/ops/*`
  respects the S2774 forward-carry pause + preserves the semantic
  boundary Rigby flagged in V7 fold A.
- **New Workspace sub-tab** `system.sign-ledger` + `ZoomOutLedgerSection`
  component — advisory-posture-first (banner + repeated copy + `is_gate: false`),
  non-severity color palette (indigo/slate/amber, no red/orange), inline help
  toggle, filters for session/classification/arc/limit.
- **OpsConsole preview card** — one-click hop to the canonical home;
  discoverability without semantic mixing.

**Removed:**

- `ops_tool.zoom_out_ledger` action + `_ops_zoom_out_ledger` handler
  (dispatch elif + method + orphaned params).
- `core/tests/test_ops_zoom_out_ledger_2779.py` (superseded by
  `test_zoom_out_tool_2780.py`).

**Bonus catch:** live smoke exposed the LLM autofill idiom hitting the
new tool — Rigby autofilled `session=0` on default calls, and my initial
handler treated that as "filter to session 0" (dropping everything). Fixed
with the same guard used in `_d14_resolve_min_session` (session > 0 only).

**Close PR:** #3172 · merged as `b16b3b981` · `--admin --squash --delete-branch`.

---

## §2. Novel-precedent moments this session

1. **Same-session `future_trigger` discharge** — S2779 fold classified
   ops_tool scope creep as `future_trigger` with explicit trigger conditions;
   S2780 fired trigger B (first non-Rigby consumer) and executed the
   corresponding amendment (factor-out) in the same session. First
   in-wild example of the future_trigger→amendment loop closing without
   a gap session between trigger firing and amendment ship.

2. **F-BLOCKING DISAGREE resolved by scope expansion (not scope reduction)** —
   S2778 V1 catch resolved by re-slotting. S2780 V1 catch resolved by
   EXPANDING scope (add factor-out to what was UI-only). Chris authorized
   the expansion ("A: factor-out + UI") after joint Claude+Rigby agreed
   on the corrected design. Precedent: F-BLOCKING doesn't always mean
   "trim the ship"; sometimes it means "you're shipping too little."

3. **Substrate ownership migration** — the S2779 handler code moved from
   `td_handlers_ops.py` to `td_handlers_governance.py` unchanged (modulo
   the autofill guard fix). Same behavior; different semantic home. First
   time the arc has produced a code-move-without-behavior-change PR in
   service of the semantic boundary V7 fold flagged.

4. **Trigger predicate wins over deferral instinct** — my instinct at
   T1 was to defer the factor-out ("fold was `future_trigger`, meaning
   'defer to trigger'; UI ship doesn't NECESSARILY force factor-out
   same-PR"). Rigby's F-BLOCKING corrected this: `future_trigger`
   semantics per PLAYBOOK-6.10.8 mean "amendment deferred TO the trigger
   condition" — when trigger fires, amendment happens, not later.
   Anti-rubber-stamp discipline paid off again.

---

## §3. Amendment cycle timeline

| Turn | Action | Outcome |
|---|---|---|
| S2780 open | Baseline verify + pin mint | Pin `pa-922038da42334842`; FRESH · SHA `039f1546dbb2`; regression 83/83 PASS |
| S2780 T1 | Rigby SIGN V1..V7 (anti-rubber-stamp gate PASS) | V1 F-BLOCKING DISAGREE (Trigger B mandates same-PR factor-out), V3 F-BLOCKING DISAGREE (canonical home = GovernanceTab not OpsConsole), V2/V4/V5/V6 PASS with folds; V7 zoom-out produced 2 same_pr_actionable folds (A + B); overall DISAGREE ship-as-proposed |
| S2780 ledger dogfood | 2 V7 folds recorded via `record_zoom_out_concern` | Ledger 18 → 20 rows |
| S2780 Chris D-verdict | "A: factor-out + UI" | Expanded scope authorized |
| S2780 authoring | Backend factor-out + endpoint + UI sub-tab + tests | 13 files touched, 1048 additions / 287 deletions |
| S2780 tests | 21 new tool tests + 5 new governance auth tests | Full 7-suite regression 90/90 PASS in 1.081s |
| S2780 smoke | 3 Rigby dispatches of new `zoom_out_tool.list` | Advisory posture intact; ledger at 20 rows; autofill guard fix verified |
| S2780 close | PR + merge + recycle + cascade | b16b3b981 |

---

## §4. Rigby SIGN Summary (per PLAYBOOK-6.10.7 + 6.10.8)

**Design-lean verifications (V1–V6):**
- V1 F-BLOCKING DISAGREE → resolved by expanding scope to include factor-out
- V2 PASS (S2774 ops-surface pause applies) → mitigated by `/api/governance/*` namespace
- V3 F-BLOCKING DISAGREE (home) → resolved by dedicated sub-tab (chose over BoardroomTab or GovernanceTab-mount since GovernanceTab is currently dead code)
- V4 PASS with fold (thin wrapper OK; must call new dispatch, not `_call_ops_tool`)
- V5 PASS with caution (advisory posture must be dominant + repeated) — shipped: banner + counts-row repeat + `is_gate: false` payload field
- V6 PASS (staff-only auth) — shipped: `@_governance_staff_only` mirror

**Zoom-out folds (V7) — per PLAYBOOK-6.10.7 mandate, classified per PLAYBOOK-6.10.8, persisted to ledger:**

| # | Fold | Classification | Mitigation applied |
|---|---|---|---|
| V7a | Semantic boundary erosion (OpsConsole becoming governance dumping ground) | `same_pr_actionable` | Dedicated `sign-ledger` sub-tab + preview-card-only in OpsConsole |
| V7b | Trigger B fired ⇒ same-PR factor-out required | `same_pr_actionable` | Full backend factor-out to `td_handlers_governance.py` |

Ledger state at close: **20 rows** (11 same_pr_actionable + 7 same_pr_mitigatable + 2 future_trigger).

---

## §5. Test surface

**New:** `core/tests/test_zoom_out_tool_2780.py` — 21 tests covering 10 contracts
1. Default action is `list`; unknown returns structured error
2. Missing log fail-soft with note
3. Advisory posture on every response
4. Aggregates span full ledger
5. Filter composition (session/classification/arc)
6. Limit clamping (default 20, max 100, min 1 negative, 0→default)
7. Malformed lines skipped
8. Path-traversal defense
9. Unknown classification → empty items
10. session=0 autofill guard (`0 = unset`)

**New:** `core/tests/test_governance_auth_regression_2780.py` — 5 tests mirroring
S2772 pattern for `/api/governance/*` namespace, with route-inventory guard.

**Full 7-suite regression stack:** 90/90 PASS in 1.081s.

**Live smoke:** 3 Rigby dispatches of new `zoom_out_tool.list` returned shape
with advisory posture intact. Autofill guard fix verified.

**Frontend verification:** `npx tsc --noEmit` exit 0 (no new errors from this
change; pre-existing warnings unchanged). Vite dev-server compiled all
edited/new files (HTTP 200 on module URLs). NOT visually verified in a
browser — Chris should eyeball `localhost:8000/workspace?tab=system&sub=sign-ledger`.

---

## §6. Ledger state at close

- **20 rows total** (18 baseline from S2779 + 2 V7 folds from S2780 T1 SIGN)
- Counts: 11 same_pr_actionable / 7 same_pr_mitigatable / 2 future_trigger

---

## §7. Open items rolled forward to S2781

**From S2779 close still open (unchanged unless noted):**
- P0.5 cost-threshold, P0.75 CI billing
- S2758 D1/D2/D4/D5
- S2761 smoke test (ops-surface, still gated)
- N13 handoff-date-format normalizer
- HMAC signing of `x-acting-user-id`
- 30+ lambda-`__import__` sites in `core/urls.py`
- N15 v2 / N21 v2 candidates (deferred pending row accumulation)
- First observed partial-recycle event (N10/N11 trigger)
- Rigby S2774 forward-carry ops-surface pause (still held; N22 v3 REST used `/api/governance/*` — unaffected)
- Postgres cleanup follow-ups (S2774 carryover)
- **N22 v3 Chris eyeball verification** — Chris should hard-refresh `localhost:8000/workspace?tab=system&sub=sign-ledger` to confirm the UI renders as intended (feedback_last_mile_ui rule)

**New from S2780:**
- **Wire `GovernanceTab` into WorkspacePageNew** — GovernanceTab.tsx exports but is currently dead code (never mounted). Not blocking N22 v3 (SIGN Ledger uses its own sub-tab); note this for a future cleanup pass if self-healing UI is wanted alongside the SIGN ledger.
- **Watch for time-window filter demand** — S2779 V3 non-blocking fold. Trigger: user asks for temporal filtering OR ledger reaches ~50+ rows across weeks.
- **First observed graceful-degradation on PLAYBOOK-6.10.8** still pending (watch for `record_zoom_out_concern` command failure).

**N22 v4+ candidates (deferred):**
- Django model migration (multi-writer OR cross-table joins)
- JSONL rotation (~500 rows away; currently at 20)
- Auto-hook into ratification envelope creation
- OpsConsole preview card → potentially expand to a mini-sparkline or trend indicator

---

## §8. Session pin

- Pin history: `pa-922038da42334842` (label `s2780-n22v3-zoom-out-ledger-workspace-tab`)
- Retired at S2780 close (force=true, eleventh consecutive per S2770+ pattern)
- Wrapper `tools/pa_local.sh` retained pointer at retired pin — intended
  failure mode forces fresh mint at S2781 open

---

## §9. Meta-observation

**Substrate arc N22 is now 3 sessions deep** (S2777 write path → S2778 constitutional codification → S2779 read surface → S2780 factor-out + UI). Each session extended the previous without breaking it; each session's fold or trigger determined the next session's work; each session honored the discipline the prior session codified. The arc has produced:

- 1 substrate (JSONL + CLI)
- 1 constitutional amendment (Playbook v0.7.0)
- 1 PA-tool read surface (S2779)
- 1 dedicated tool + REST endpoint + UI (S2780)
- 8 ledger rows dogfooded during authoring (S2778: 4 + S2779: 1 + S2780: 2 + 1 for S2780 T1 pin arc = actual math: baseline 13 + 4 [S2778] = 17 + 1 [S2779] = 18 + 2 [S2780] = 20 ✓)

**S2771 rule streak now covers 10 sessions (S2771–S2780)** with 3 F-BLOCKING DISAGREEs (S2776 Q1, S2778 V1, S2780 V1+V3) and 1 constitutional codification. No drift into ritual — S2780 T1 caught two BLOCKING design leans and one non-blocking scope expansion (V4 wrapper choice) that would have shipped a smaller but semantically-mixed artifact.

The arc's next natural pause: consumer breadth. If a second consumer of the SIGN Ledger emerges (external dashboard, Slack bot, mobile app), the `zoom_out_tool` interface will be exercised by heterogeneous callers and its abstraction quality will be tested. Until then, the current shape suffices.
