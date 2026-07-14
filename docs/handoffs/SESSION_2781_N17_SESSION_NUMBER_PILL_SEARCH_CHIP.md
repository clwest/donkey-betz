---
title: "SESSION 2781 — N17: session_number pill in ledger search chip"
session: 2781
status: closed
date: 2026-07-13
close_pr: 3174
close_pr_merge_sha: 2fc68b79d
arc: n17_session_number_pill_search_chip
predecessor: SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md
---

## §1. What shipped

Small UX shortcut for the S2771 N14 close-ceremony ledger search input in
OpsConsoleTab. When the operator types a 4- or 5-digit session number,
an inline "→ S{num}" pill appears on the right edge of the input. One
click promotes the substring text scan to an exact session-scope filter
(`sessionMin = sessionMax = num`, text cleared), replacing a slow full-
body scan with a fast bounded query. A 5-second "↩ Undo" chip protects
against destructive misclick.

**Files touched:**
- `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — added
  `parsedSessionFromText` memo, `n17UndoState` local state + 5s
  timeout, promote/undo handlers, wrapped input in relative div,
  rendered pill + undo chip as absolute-positioned buttons.
- `tools/pa_local.sh` — S2781 pin refresh.

**Close PR:** #3174 · merged as `2fc68b79d` · `--admin --squash --delete-branch`.

---

## §2. Novel-precedent moment

**First observed in-wild consumer of the S2780 N22 v3 read surface** —
Rigby dogfooded `zoom_out_tool.list` during her T1 SIGN verification of
N17 to consult the ledger for prior UI-scope folds. That is exactly the
future consumer the N22 arc named ("Rigby herself during joint SIGN
loops"), verified in-wild one session after the ship. The arc's
articulated use case has now been observed used.

---

## §3. SIGN cycle summary

| Slot | Verdict | Disposition |
|---|---|---|
| V1 pill shape (inline "→ S{num}") | AGREE | Shipped as designed |
| V2 regex | DISAGREE (non-blocking) | Tightened `\d{2,5}` → `\d{4,5}` — real session numbers ≥ 1000 |
| V3 state transition | AGREE + mitigation | Added 5s Undo chip + tooltip/aria warning |
| V4 discoverability | AGREE | Added title + aria-label hints |
| V5 zoom-out (mandatory) | 2 folds classified + persisted | See §4 |

**Rigby dogfooded S2780 N22 v3 substrate** — invoked `zoom_out_tool.list`
alongside `search_docs` and `repo_tool` during T1 verification. First
observed non-Rigby-authoring consumer of the ledger read path.

---

## §4. V5 zoom-out folds (per PLAYBOOK-6.10.7 + 6.10.8)

| # | Fold | Classification | Mitigation applied |
|---|---|---|---|
| V5.1 | Smart command box creep — session pill today, dates/arcs/tags tomorrow, hidden semantics inflation | `future_trigger` | Deferred; trigger = proposal of a 2nd non-session inline pill on same search input OR user-confusion signal about "special" inputs |
| V5.2 | Accidental destructive clear causes distrust — one misclick loses typed query with no undo | `same_pr_mitigatable` | 5-second Undo chip + tooltip/aria warning shipped in same PR |

Ledger state at close: **22 rows** (12 same_pr_actionable + 8 same_pr_mitigatable + 2 future_trigger).

---

## §5. Verification

- **Type-check:** `npx tsc --noEmit` exit 0. No new errors from this change; pre-existing WorkspacePageNew / paStore warnings unchanged.
- **Vite compile:** dev server compiled `OpsConsoleTab.tsx` successfully (HTTP 200 on module URL after edits).
- **Backend regression:** unchanged from S2780; no backend files touched.
- **Not visually verified in a browser.** Chris should hard-refresh
  `localhost:8000/workspace?tab=system&sub=ops`, type "2779" into the
  ledger search input, expect "→ S2779" pill on right edge; click
  should trigger transition to session-scoped filter with "↩ Undo"
  chip visible for 5 seconds.

---

## §6. Ledger state at close

- **22 rows total** (20 baseline from S2780 + 2 V5 folds from S2781 T1 SIGN)
- Counts: 12 same_pr_actionable / 8 same_pr_mitigatable / 2 future_trigger

---

## §7. Open items rolled forward to S2782

**From S2780 close still open (unchanged unless noted):**
- P0.5 cost-threshold, P0.75 CI billing
- S2758 D1/D2/D4/D5
- S2761 smoke test (ops-surface, still gated)
- N13 handoff-date-format normalizer
- HMAC signing of `x-acting-user-id`
- 30+ lambda-`__import__` sites in `core/urls.py`
- N15 v2 / N21 v2 candidates (deferred pending row accumulation)
- First observed partial-recycle event (N10/N11 trigger)
- Rigby S2774 forward-carry ops-surface pause (still held; N17 was frontend-only, unaffected)
- Postgres cleanup follow-ups (S2774 carryover)
- **Chris eyeball verification of N22 v3 UI + N17 UI** — both now shipped; hard-refresh
- **Wire GovernanceTab into WorkspacePageNew** — dead-code cleanup

**New from S2781:**
- **N17 smart-command-box creep** — persisted to ledger row 21 as `future_trigger`. Watch for a 2nd non-session inline pill proposal on the same search input, or a user-confusion signal about which inputs are "special." If either fires, revisit the smart-command-box design as a coherent whole rather than accreting one-off pills.

---

## §8. Session pin

- Pin history: `pa-bef4ec475900443d` (label `s2781-n17-session-number-pill-search-chip`)
- Retired at S2781 close (force=true, twelfth consecutive per S2770+ pattern)
- Wrapper `tools/pa_local.sh` retained pointer at retired pin — intended failure mode forces fresh mint at S2782 open

---

## §9. Meta-observation

**S2781 was a deliberate palate cleanser after a 4-session substrate arc (N22 write path → codification → read surface → factor-out + UI).** N17 was on the ready list since S2775 and cleared cleanly in one session with no F-BLOCKING. That's a healthy cadence pattern: substrate arcs earn quick housekeeping wins between them, and small UX polish work benefits from the same joint-SIGN discipline as big rewrites (V2 caught the regex tuning; V3 caught the missing undo path; V5 caught the smart-command-box drift risk).

**S2771 rule streak now covers 11 sessions (S2771–S2781)** with 3 F-BLOCKING DISAGREEs (S2776 Q1, S2778 V1, S2780 V1+V3) and 1 constitutional codification. Every session has produced substantive folds. No drift into ritual. The ledger has grown 13 → 22 rows in 8 sessions since the seed backfill — a real longitudinal record of what SIGN pressure surfaces in practice.

**First observed in-wild consumer of N22 v3 substrate** — the arc paid off one session after ship. Rigby has now used the tool the arc built; the next test is whether she'd use it unprompted. This session's use was in service of my directive ("dogfood your verifications"), not autonomous. Watch for autonomous consultation as the truer signal.
