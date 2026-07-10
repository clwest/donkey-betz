# Session 2741 — Capability Graph Freshness Sweep (§29 + §30 + §31)

**Session:** 2741
**Date:** 2026-07-10
**Session type:** Meta-methodology arc — full-graph audit under PLAYBOOK-6.10.6
**System Owner directive:** "run the graph freshness sweep" (Option 2 selection after 4-of-4 verify-before-build hits in S2741 opening)
**PA conversation pins (chronological):**
- Session-open §16 arc pin (retired): `pa-09e870b7b98c48f3` was minted as `session-2741-notification-delivery-arc` but became the sweep arc after mid-session pivot
- Arc pin (final title unchanged for continuity): `pa-09e870b7b98c48f3`
**Preceding arc:** SESSION_2740 (Playbook v0.4.0 ratified — PLAYBOOK-6.10.6 codified verify-before-build discipline)
**Merge commit:** `26e8a21e` (PR #3064, squash-merged 2026-07-10)

---

## §1 Delivery ledger

| # | PR | Purpose |
|---|---|---|
| 1 | #3064 (`docs/session-2741-graph-freshness-sweep`) | Full-graph freshness sweep — §29 (per-chain drift audit) + §30 (§20 Tier tables refresh) + §31 (§21 first-chain rec supersession); 2 files, +170/-1 LOC |

**Ledger totals for S2741:** 1 PR · 1 docs · 3 new capability-graph sections · Rigby SIGN APPROVE · zero code · zero regressions.

---

## §2 Arc shape — 4-of-4 verify-before-build hits → systematic sweep

1. **Chris question at S2741 open** — "whats next on the queue?" Claude answered from 00-START; recommended §16 Notification Delivery as highest-leverage candidate.
2. **Chris ratification** — "route §16 to Rigby for scope SIGN"
3. **Pin lifecycle** — retired S2740 Playbook arc pin `pa-6cf25378d80948f2`; minted `pa-09e870b7b98c48f3` (originally titled `session-2741-notification-delivery-arc`); rotated wrapper
4. **Verify-before-build attempt 1** — read graph §16 at HEAD; grepped for `NotificationFanoutService`. **Result:** DOES NOT EXIST. But `HumanPreference`, `NotificationLog`, `PushSubscription`, `expo_push`, `PushNotificationService`, and CDR-001 all EXIST. Multiple Rigby §23 F2 "UNEVIDENCED" claims contradicted at HEAD.
5. **CDR-001 read** — CDR-001 (ratified 2026-07-09) explicitly refuted the §16 campaign. `NotificationFanoutService` class REJECTED. Receiver-driven fanout pattern via `HumanAttentionItem.post_save` is the ratified architecture. Campaign scope collapsed to a 1-2 session wrap-up bundle (§7 Gap 1/2/3).
6. **Verify-before-build attempt 2** — grepped for CDR-001 §7 residual gaps. **Result:** ALL THREE SHIPPED at S2737. Inbox receiver + `HAIDispatchLog` + `channels_fired` helpers + dedicated test file `test_hai_wrap_up_bundle.py`. Entire wrap-up bundle closed 3+ sessions ago.
7. **Report to Chris** — 4-of-4 verify-before-build save rate; recommended Option 2 (full-graph freshness sweep) over point-fix
8. **Chris directive** — "run the graph freshness sweep"
9. **Sweep execution** — Explore sub-agent verified all 19 chains against HEAD `47ae7eda`, bounded to ~10min. Returned per-chain classification table with file:line evidence. Result: 8/19 (42%) drift-touched; 11/19 (58%) baseline stable.
10. **§29 authored** — full-graph freshness sweep as append-only refresh (matches §23/§25/§27 precedent). Per-chain classification, drift-class summary, completeness recomputation, meta-observations, maintenance recommendations, governance refs.
11. **Body SIGN dispatch** — Rigby verified §29 approach + spot-checked §1/§8/§16 at HEAD independently
12. **Body SIGN cycle 1** — **APPROVE** with 2 follow-on recs: add §20/§21 append-only refresh blocks; CDR-002 for canonical fanout pattern (future arc). Zero F-BLOCKING.
13. **§20/§21 refresh folded** — authored §30 (Tier tables reassignment) + §31 (first-chain rec supersession).
14. **Chris ratification** — "ratify — open the PR"
15. **PR #3064 opened + squash-merged as `26e8a21e`**
16. **Post-merge cascade** — 4-step docs cascade + this handoff + 00-START refresh

---

## §3 The four verify-before-build hits (aggregated evidence for CX-P11 elevation)

| # | Session | Candidate | Artifact claim | HEAD reality | Substrate class |
|---|---|---|---|---|---|
| 1 | S2739 | §17 Cost Protection | LLMCallEvent + missing cost_usd field | CostTracking (54.5× more coverage) | Substrate mismatch (wrong architecture) |
| 2 | S2740 | §18 F-D-SIDEBAR-1 | Sidebar.tsx:356 needs `authApi.logout()` | Sidebar.tsx:370 has `await authApi.logout()` — shipped S2735 PR #3036 | Already shipped |
| 3 | S2741 (attempt 1) | §16 NotificationFanoutService | Missing unified fanout service | Rejected as class by CDR-001; receiver-driven pattern is canonical | Class rejected by prior CDR |
| 4 | S2741 (attempt 2) | CDR-001 §7 residual gaps | 3 named gaps (Inbox / HAIDispatchLog / channels_fired) | All 3 shipped S2737 with dedicated test file | Fully shipped |

**Pattern signature:** each hit was caught within seconds of arc opening via file:line grep. None required deep analysis. This is exactly PLAYBOOK-6.10.6's expected cost curve — small verification cost prevents session-scale wasted work.

**CX-P11 CANDIDATE elevation status:** Two-trigger threshold likely met. S2740 §9.2 recorded first occurrence (v0.4.0 codification arc); S2741 §29 sweep is second occurrence (methodology codification within research artifact rather than Playbook body). Not identical shape — the S2741 sweep is a systematic AUDIT rather than same-session pivot — but both are "codify what the sweep learned in the same session it revealed." Codification-eligible for future PATCH; do NOT codify yet, awaits Chris directive.

---

## §4 §29 sweep — per-chain summary

**HEAD:** `47ae7eda1fb07b8f5efa57d63437c9d3a93d73a1` (post-S2740 v0.4.0 cascade merge)

**Distribution:**
- **8/19 drift-touched:** §1, §6, §8, §14, §15, §16 (MISSING-LINKS-SHIPPED) + §17 (already refreshed §27) + §18 (F-D-SIDEBAR-1 shipped) + §4 (partial stale claim)
- **9/19 accurate at HEAD:** §2, §3, §5, §12, §13, §19 (baseline stable) + §9, §10, §11, §7 (Chris-blocked no-refresh-possible)
- **2/19 special cases:** §17 (refreshed in prior arc §27), §7 (inherits §17 drift + independently ADR-blocked)

**Direction of drift: 100% understatement.** Not a single chain overstates HEAD. Bias always: graph body says "still missing" for links that shipped.

**Aggregate understatement:** +16 completeness units. Dominated by §8 (+4, all 4 HAI bridge methods shipped) and §16 (+6, CDR-001 wrap-up bundle shipped).

---

## §5 §30 sweep — Tier reassignments

Post-sweep Tier A is **EMPTY** — every previously-Tier-A chain has either shipped (§1, §6, §16) or reduced to Tier B polish (§8).

Post-sweep Tier B (small polish, unblocked):
1. §8 HAI Escalation residuals (small-scope after all 4 named methods shipped)
2. §14 Platform Health autonomic Governance reaction (Chris-ADR-adjacent)
3. §17 Cat 3 startup config log (leftover from S2739 §17 P2+ arc)

**Interpretation:** the platform has entered a **capability-saturation regime** where residual work is either small-scope polish or gated on constitutional ADRs. This is a milestone.

---

## §6 §31 sweep — first-chain rec supersession

§21's "§16 Notification Delivery FIRST" recommendation was stale on TWO premises: (a) §16 is now MISSING-LINKS-SHIPPED at HEAD, and (b) `NotificationFanoutService` as a class was explicitly rejected by CDR-001 §2.5.

Three replacement candidate classes:

| Class | Character | Example candidates |
|---|---|---|
| **Polish** — Tier B residuals | Small S-M PRs; no leverage unlock; incremental quality | §14 autonomic Governance reaction, §17 Cat 3 startup log, §19 envelope telemetry |
| **Constitutional-ADR unblocking** — Tier D | Requires Chris D-verdicts; unlocks large surface once ratified | §4 D65a-D65e, §7 T1-T8, §9 KillSwitch, §10 Symbol Mapping, §11 D80 write-authority, §18 4-axis §14.14 |
| **Meta-methodology** — codify what the sweep learned | Not per-chain work; improves EOS itself | CDR-002 receiver-driven fanout canonical; PATCH §6.12 for per-chain refresh cadence; CX-P11 second-trigger codification |

**Recommendation:** future sessions selecting from the queue MUST apply PLAYBOOK-6.10.6 verify-before-build to whichever candidate is drawn. §21 is superseded until the graph body is refactored.

---

## §7 Rigby SIGN provenance

| Stage | Pin | Confidence | Verdict | Refinements folded |
|---|---|---|---|---|
| §29 body SIGN | `pa-09e870b7b98c48f3` | Not scored — direct evidence-based verdict | **APPROVE** | 2 follow-on recs: §20/§21 refresh blocks (both folded as §30 + §31); CDR-002 candidate flagged for future arc |

Rigby independently spot-checked §1 (`views_personal_assistant.py` group_send), §8 (Web Push + Discord receivers with `transaction.on_commit` pattern), and §16 (Expo push registration at `mobile/src/push/registerPushToken.ts`) at HEAD. Evidence supports every MISSING-LINKS-SHIPPED classification the Explore sub-agent produced.

Rigby's own S2734-era F2 refinement (which downgraded §16 from 8/15 → 6/15) is folded into §29.4 meta-observations as an in-wild example of the failure mode PLAYBOOK-6.10.6 codifies. Not accusatory — the F2 pass predated the rule; the meta-observation strengthens the rule's evidence chain.

---

## §8 CX-P11 CANDIDATE second-trigger evidence (for future codification)

S2740 §9.2 named the pattern candidate:

> **"Same-session discovery + codification arc class."** S2740 opened as SIDEBAR-1 slice, discovered second trigger, immediately pivoted to codification arc. This pattern of within-session pivot needs additional evidence before proposing constitutional codification. Not codification-eligible at one instance.

S2741 is now the second organic occurrence:

- Opened as §16 Notification Delivery arc
- Discovered 4-of-4 verify-before-build hits
- Immediately pivoted to full-graph freshness sweep
- Sweep is not a "same-session codification" like S2740 (which authored a new Playbook rule) — it's a "same-session systematic audit" of research artifacts

**Question for future arc:** are these the same pattern (within-session pivot to broader-scope work after discovery), or two distinct patterns (Playbook codification vs. research artifact audit)? If same, two-trigger threshold is met and PATCH codification is due. If distinct, each is single-instance and codification remains deferred.

**Recommendation:** wait for a third occurrence to disambiguate. Do NOT codify at this instance.

---

## §9 What this research taught us about how to do research

*(per feedback_xx99_meta_methodology_section.md discipline)*

### §9.1 What worked
- **PLAYBOOK-6.10.6 immediately paid off.** The rule was ratified 24h before this session. Its first application caught two drifts in the first minute of the arc. Constitutional rules with in-wild grounding pay for themselves fast.
- **Explore sub-agent parallelization was the right tool.** 19 chains verified against HEAD in ~10min bounded pass. Doing this sequentially in the main agent would have consumed much more context and time. Sub-agent isolation prevents context bloat + parallel verify-before-build is the right shape.
- **Append-only §29/§30/§31 preserved history.** Bodies of §1-§19 remain authored-record. Readers cross-reference the append blocks for current verdict. Matches §23/§25/§27 precedent — the discipline compounds.

### §9.2 What to codify (candidates — do NOT codify yet)
- **Per-chain refresh cadence.** Every capability chain SHOULD receive a §29-style verdict every N sessions OR when a chain-relevant PR merges. Currently a §29.5 suggestion. Two-trigger threshold: §27 (S2739 §17 refresh) + §29 (S2741 full sweep). Consider PATCH-scope codification in Chapter 6 §6.12 extension points.
- **CDR-002 canonical fanout pattern.** Rigby recommended; §29.5 flagged. Prerequisite: identify a second in-wild pattern of "receiver + task + adapter + kill switch" that isn't the HAI fanout, to prove the pattern generalizes.

### §9.3 Anti-patterns to avoid
- **Do NOT skip verify-before-build even when the candidate looks obviously good.** §16 was Rigby's own recommendation two sessions ago, matched by 00-START, and looked like a defensible next move. It was refuted in 30 seconds by grep. The "highest confidence" candidates are exactly the ones where verify-before-build catches the biggest saves.
- **Do NOT edit §1-§19 bodies in place.** The append-only discipline preserves authorship and enables monitoring the graph's authorship-vs-HEAD delta over time. Editing in place would destroy the drift-tracking value.

### §9.4 Suggestions for the playbook
- Reserve `PLAYBOOK-6.10.7` and beyond per §6.12 reservation convention for future verify-before-you-act extensions.
- Consider a §29-style verdict format as a TEMPLATE codified in Chapter 6, so future sweeps produce comparable outputs. Post two-trigger threshold. Do NOT codify yet.

### §9.5 Suggestions for future direct-EOS campaigns
- Every candidate-scope SIGN dispatch should INCLUDE a verify-before-build outcome. Currently the pattern is (a) Cat A independent read then (b) verify-before-build. Reverse: (a) verify-before-build (30 seconds), (b) if candidate still viable, do Cat A. Saves the entire Cat A cycle when the candidate is closed.
- When the sweep reveals systematic drift (4-of-4 in three sessions), pivot to meta-audit immediately. Point-fixes on N chains would have consumed N sessions without addressing root cause.

---

## §10 Post-merge cascade verification

| Step | Command | Result |
|---|---|---|
| 1. Squash-merge PR #3064 | `gh pr merge 3064 --squash --delete-branch` | Merged as `26e8a21e` |
| 2. Docs index refresh | `python manage.py build_docs_index` | (see cascade output) |
| 3. RAG corpus rebuild | `python manage.py build_rag_corpus` | (see cascade output) |
| 4. Sync docs + embed | `python manage.py sync_docs_index_to_documents --embed` | (see cascade output) |
| 5. Provenance refresh | `python manage.py build_docs_provenance` | (see cascade output) |
| 6. This handoff | `Write` | authored |
| 7. 00-START refresh | `Write` | S2742 candidate queue authored per §31 three-class framework |

Note: no `make celery-recycle` step — docs-only PR; no task registry changes.

---

## §11 Governance references

- **PLAYBOOK-6.10.6** (v0.4.0, ratified 2026-07-10) — verify-before-build discipline this sweep applies four times
- **CDR-001** (`docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`, ratified 2026-07-09) — refuted the §16 campaign this sweep confirms + extends
- **§29-§31** in `docs/research/platform/platform_capability_graph.md` — the sweep body itself
- **PR:** #3064 (merged as `26e8a21e`)
- **Rigby SIGN pin:** `pa-09e870b7b98c48f3` (session-2741-notification-delivery-arc)
- **Prior arc handoffs:** SESSION_2740_PLAYBOOK_V0_4_0_RATIFIED.md (PLAYBOOK-6.10.6 codification); SESSION_2739_COST_PROTECTION_P2_OBSERVATION.md (Trigger 1 of CD-50); SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md (§16 wrap-up bundle shipping, confirmed at S2741 §29)
- **Chris ratification directive:** 2026-07-10 (multi-step: "route §16 to Rigby for scope SIGN" → "ship the CDR-001 wrap-up bundle" → "run the graph freshness sweep" → "ratify — open the PR" → "merge it")

---

## §12 Wrapper pin state at S2741 close

- `tools/pa_local.sh` line 532: `pa-09e870b7b98c48f3` (was `session-2741-notification-delivery-arc`, but pin actually served the graph freshness sweep after mid-session pivot)
- Arc pin held OPEN pending Chris "session close" signal — future S2742 session-open should retire this pin per §16 arc-close discipline and mint fresh S2742 open pin.

---

**Session 2741 CLOSED.** Capability graph freshness sweep complete. 8-of-19 chains refreshed via append-only §29+§30+§31. Post-sweep Tier A is empty; platform enters capability-saturation regime.
