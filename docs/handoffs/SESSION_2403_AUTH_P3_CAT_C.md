---
session: 2403
status: closed (S2403 P3 Cat C Session Lifecycle + Logout Cleanup Contract Audit CLOSED under Group 2400 Auth arc pin `pa-6279ead1714c4630` preserved through S2403 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails; EIGHTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402 prior seventeen; Rigby SIGN cycle 1 SIGN-with-edits at MED-HIGH confidence (~0.82; HIGHER than Cat A 0.74 + Cat B ~0.8) via dedicated fresh SIGN pin `pa-5096f5fc07754b18` retired at cycle close via `session_tool.retire` (updated_count=4, retired=true, previously_active=true — FOURTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + 1 Cat A child audit + 1 Cat B child audit + this cycle); 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2402 seven-consecutive tested pattern — EIGHTH-consecutive same-cadence application at child-audit stage; MC-10 codification-ready-pending-Chris at 8-arc baseline; 32 folds landed pre-Chris-ratification per §20.6 fold ledger (29 SIGN Q folds + 3 pre-commit nit folds from ratification-card review); cycle 2 NOT required per Rigby cycle-1 MED-HIGH confidence + all folds landable; Chris "commit it" 2026-07-05 ratified 32-fold SIGN-with-edits wholesale at MED-HIGH confidence — status flipped `draft` → `active` per playbook §16 draft-first workflow; ARCHITECTURE_INDEX v85 → v86 with §1.89 registration; OPEN_ARCS Group 2400 In-progress row updated from "S2400 parent scoping + S2401 P1 Cat A + S2402 P2 Cat B (2026-07-05) — 3 of 6 shipped" to "S2400 parent scoping + S2401 P1 Cat A + S2402 P2 Cat B + S2403 P3 Cat C (2026-07-05) — 4 of 6 shipped"; 00-START-NEXT-SESSION.md overwritten with S2404 P4 Cat D open priorities; Runtime target 6 sessions — **4 of 6 shipped**)
date: 2026-07-05
arc: Research Group 2400 (Auth — Session Lifecycle + Permission Floor + Silent-401 Resolution) — S2403 P3 Cat C third-child audit + arc-preservation cascade
head_commit_before: 8bc1b0c0 (S2402 P2 Cat B merge PR #2912)
head_commit_after: TBD (S2403 P3 Cat C merge PR TBD)
arc_pin: pa-6279ead1714c4630 (PRESERVED through S2403 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails — ELEVENTH formal arc pin under Research OS; retirement at S2499 close; MC-14 CANDIDATE-threshold-satisfied extended to 4-arc-stages via Group 2200 + Group 2400 Cat A + Group 2400 Cat B + Group 2400 Cat C = 4 confirming arc-stages post-S2403 close)
sign_pin: pa-5096f5fc07754b18 (RETIRED at S2403 SIGN cycle 1 close 2026-07-05 via `session_tool.retire` per playbook §15 SIGN-isolation discipline; updated_count=4, retired=true, previously_active=true — FOURTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 prior ten xx99 + S2400 parent-scoping-light-SIGN + S2401 Cat A child audit + S2402 Cat B child audit + this cycle)
---

# Session 2403 — Group 2400 Cat C — Session Lifecycle + Logout Cleanup Contract Audit

## What shipped

**Doc:** `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` (2,012 lines post-fold; `status: active` post-Chris-"commit it"-2026-07-05 ratification).

**Playbook §11.2 20-section child-audit template EIGHTEENTH-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402 prior seventeen.

**HEAD-verified at `8bc1b0c0`.** Delivers parent §3.C Cat C expected outputs (a-e): session model inventory (SESSION_ + CSRF_ config declarations + Redis + LocMemCache fallback + DRF Token no-expiry + VIPInvite two-timestamp lifecycle) + 15-surface storageKeys × logout-cleanup CONTRACT table + 21-loci lifecycle-observability rate table + three-option decision space (α silent-refresh / β explicit-re-login / γ hybrid) evidence + cockpit two-stage MINOR-DRIFT re-verification STILL-LIVE at HEAD.

**6-parallel-Explore-agent sweep per playbook §13 dispatched.** Agent 1 Session Models + Persistence + Agent 2 Services + Runtime Flows + Agent 3 APIs + Tools + Tasks + Commands + Agent 4 Integrations + Cross-Domain (15-surface × cleanup) + Agent 5 Documentation + Prior Research + Agent 6 Drift + Debt + Ownership + Maturity.

**Parent-Claude verifier-loop per playbook §14 caught 1 sub-agent conflict pre-draft:**

- Agent 3 asserted `/api/v1/auth/logout-enhanced/` has "permission_classes: none"; Agent 1 asserted `logout_enhanced_view` has `@permission_classes([IsAuthenticated])`. Parent verifier-loop independently read `core/auth_views_enhanced.py:539-556` at HEAD and confirmed Agent 1: line 540 carries `@permission_classes([IsAuthenticated])`. Basic `/api/v1/auth/logout/` (`core/auth_views.py:84-94`) has NO permission decorator — silent-200 on unauthenticated confirmed. Corrected in §6 + §7 + §14 F-C-LOGOUT-1/2 severity classification.

**Rigby Batch-2 NEEDS-MORE resolved via mid-cycle HEAD verifier-loop:**

- VIP invite exchange HEAD-verified at `core/views_vip_invite.py:85-163` + `invite.is_valid` property at `models_vip_invite.py:95-103`: confirmed **ONLY `token_expires_at` (72h) enforced, NOT `account_expires_at`**; response body returns `account_expires_at.isoformat()` at `:161` — server tells client an expiry it will NEVER enforce (F-C-VIP-1 declared-fictional aggravator)
- Django `accounts/logout` semantics HEAD-verified at `django/contrib/auth/__init__.py:160-171` (Python 3.11 stdlib): `logout()` calls `request.session.flush()` at line 171 — original §6.1 claim tightened to concrete citation
- Endpoint line-drift corrections: register 48 → 50; forgot 297 → 299; reset 357 → 359 (HEAD-verified via grep)

## Rigby SIGN cycle 1 SIGN-with-edits at MED-HIGH confidence (~0.82) — 32 folds landed

Cycle opened via `session_tool.create_fresh` — fresh dedicated SIGN pin `pa-5096f5fc07754b18`. 4-batch × 5-Q = 20-Q cadence per S2201-S2402 seven-consecutive tested pattern (EIGHTH-consecutive 20-Q cadence application at child-audit stage; MC-10 codification-ready-pending-Chris at 8-arc baseline).

**Rigby overall verdict:** **SIGN-with-edits at MED-HIGH confidence (~0.82)** — HIGHER than both S2401 Cat A (MED 0.74) and S2402 Cat B (MED-HIGH ~0.8). Reason: denominator-discipline pre-emption (per Cat B Q20 fold) succeeded → Rigby caught zero denominator-ambiguity findings. Cycle 2 NOT required per all folds landable pre-Chris-ratification.

**32-fold ledger (per-Q + landing location):**

Batch 1 folds (Q1-Q5 executive framing):
- **F1 (Q1)** — Maturity lens rephrase from "WORKING-CORRECTNESS + EXPERIMENTAL-GOVERNANCE" to "WORKING-mechanisms / PARTIAL-lifecycle-correctness / EXPERIMENTAL-governance" three-axis — §1 executive
- **F2 (Q2)** — Acceptance-criterion scoring 2-axis: Platform outcome (FAIL) vs Audit outcome (PASS) — §1 table
- **F3 (Q3)** — F-C-COOKIE-1 severity MED → LOW-MED (Django defaults correct; documentary only) — §1 + §14.4 + §15
- **F4 (Q4)** — Add 4th seam class "declared-fictional"; F-C-VIP-1 reclassified from silent-swallow to declared-fictional; F-C-LOGOUT-1/2 clarified as silent-swallow; F-C-REFRESH-1/F-C-CSD-1/F-C-COOKIE-1 clarified as contract-absent — §1

Batch 2 folds (Q6-Q10 sections 3-8; NEEDS-MORE resolved via HEAD verifier-loop):
- **F5 (Q6a)** — DiscordLinkCode marked out-of-scope with rationale — §5
- **F6 (Q6b)** — PasswordResetTokenGenerator marked out-of-scope with rationale — §5
- **F7 (Q6c)** — Line-drift corrections: register 48 → 50; forgot 297 → 299; reset 357 → 359 (HEAD-verified) — §6.1
- **F8 (Q7a)** — Cat B SPECULATIVE-fifth-role hypothesis "NEGATIVELY VERIFIED FOR S2403 SNAPSHOT" (Cat C closes for this snapshot; Cat B keeps label for own follow-up) — §4
- **F9 (Q7b)** — F-C-ROLE-SCOPE severity MED → LOW-observational — §4 + §14.4 + §15
- **F10 (Q9a)** — VIP invite exchange HEAD-verified via `views_vip_invite.py:85-163` + `invite.is_valid` at `models_vip_invite.py:95-103` — confirmed ONLY `token_expires_at` enforced; response body returns `account_expires_at.isoformat()` at `:161` (declared-fictional aggravator) — §6.1
- **F11 (Q9b)** — Django `accounts/logout` HEAD-verified: `logout()` calls `request.session.flush()` at `django/contrib/auth/__init__.py:171` — §6.1 with citation
- **F12 (Q10a)** — F-C-FIX-1 label: dropped SPECULATIVE-CONCERN sentinel (evidence is concrete grep zero-match); renamed to "Session key rotation on auth boundary not evidenced" — §14.4 + §15
- **F13 (Q10b)** — F-C-FIX-1 severity: normalized from PARTIAL to LOW on standard ladder — §14.4 + §15

Batch 3 folds (Q11-Q15 sections 9-14):
- **F14 (Q11a)** — CF-C3 kept as single tracking unit with sub-bullets (NOT split into three flags — governance noise avoided) — §9.2
- **F15 (Q11b)** — CF-C8 for Fleet HMAC rejected (Fleet orthogonal per Cat A trust-boundary framing) — §9.2 (not added)
- **F16 (Q12)** — CF-C3 preserved as own tracking unit; explicit link to Cat A CF-2 + Cat B CF-B5 for xx99 §5.4 Observability umbrella roll-up — §9.2
- **F17 (Q13)** — MODERATE+ definition added: "multiple-category audits closing major entry points + runtime flows within a single domain plane; DEEP requires cross-category completion" — §12
- **F18 (Q14a)** — §13 primitives table preserved without DiscordLinkCode/Fleet rows (avoid table bloat; orthogonal per §5) — §13
- **F19 (Q14b)** — Overall maturity verdict PARTIAL preserved (product-contract statement, not primitive-fraction math) — §13
- **F20 (Q15a)** — §1 executive: reconciled "seven headline findings" as "top items worth reading" vs severity distribution "HIGH=4, non-HIGH=3" post-fold-normalization — §1
- **F21 (Q15b)** — F-C-TAB-1 two-context severity split preserved: HIGH (shared-browser) / MED (single-user) — §14.1 + §15

Batch 4 folds (Q16-Q20 sections 15-20 + emerging weak-spot):
- **F22 (Q16a)** — Cat A + Cat B inherited findings preserved as background with "Same-issue lineage" cross-reference lines (F-VIP-1 ↔ F-C-VIP-1; F-TOKEN-1 ↔ F-C-REFRESH-1; F-DUP-2 ↔ F-C-DUP-3); NOT merged — §15
- **F23 (Q16b)** — Cat B F-B-CRIT-1 explicitly labeled "orthogonal / intersects at Cat D" — §15
- **F24 (Q17a)** — F-C-DUP-3 marked "Restatement for lifecycle-plane completeness; no new risk introduced; closes Cat B SPECULATIVE-fifth-role for S2403 snapshot" — §17
- **F25 (Q17b)** — F-C-DUP-1 severity MED preserved (structure finding); added aggravator-pointer label to F-C-LOGOUT-1 (avoids double-counting risk) — §17
- **F26 (Q18)** — F-C-OWN-1 reframed from "owner UNCLEAR" (defect-reading) to "Session-lifecycle plane is cross-arc by design; xx99 is the coordination decision point (Chris)" — §18
- **F27 (Q19)** — §19.1 language tightened: "Cat C proposes β as least-assumption default for xx99 evaluation" (NOT "Cat C recommends"); anti-recommendation reframed as "Risk-gating constraint" — §19.1
- **F28 (Q20a)** — Explicit contrast sentence: "Cat B denominator-ambiguity = measurement / metrics ambiguity; Cat C silent-degrade ambiguity = runtime UX / telemetry ambiguity" — §19.3
- **F29 (Q20b)** — Explicit two-trigger rule statement: Cat C is TRIGGER #1; Cat D likely surfaces TRIGGER #2 in silent-401 SYSTEMIC audit; codification threshold at S2499 xx99 close if Cat D confirms — §19.3

Pre-commit nit folds (Rigby ratification-card review):
- **F30 (Nit 1)** — §1 executive lens sentence tightened to "WORKING mechanisms / PARTIAL lifecycle correctness + EXPERIMENTAL governance" to match scoring language — §1
- **F31 (Nit 2)** — F-C-COOKIE-1 severity label clarified as "LOW-MED (documentary gap only)" with explicit sentence "Django defaults are correct at HEAD; risk is drift if later subdomain/path scoping is introduced." — §1 + §14.4
- **F32 (Nit 3)** — Risk-gating constraint scope tightened from "prerequisite for any α/β/γ decision" to "prerequisite for shipping any user-facing lifecycle change that relies on expiry semantics / VIP safety signals" — §19.1

## 7 headline findings (post-fold; 4 HIGH + 3 non-HIGH)

- **F-C-VIP-1 HIGH (declared-fictional class)** — `VIPInvite.account_expires_at` (14d) NOT ENFORCED at runtime. HEAD-verified: `invite.is_valid` at `models_vip_invite.py:95-103` checks ONLY `token_expires_at > now`; VIP exchange endpoint at `views_vip_invite.py:85-163` returns `account_expires_at.isoformat()` in response body at `:161` — server tells client an expiry date it will never enforce (Cat A F-VIP-1 same-issue lineage; Cat C classifies under lifecycle plane).
- **F-C-REFRESH-1 HIGH (contract-absent class)** — No session-token refresh endpoint. Grep zero-match for `TokenRefresh` / `RefreshView` / `token/refresh/` in auth surface; 3 `path.*refresh` matches at `urls.py:1925,2055,3071` are non-auth (spider / OAuth platform / agent discovery). Combined with Cat A F-TOKEN-1 (Token no expiry): implicit contract "token permanent absent password change/reset/logout event"; no refresh discipline observable at boundary.
- **F-C-CSD-1 HIGH (contract-absent class)** — Zero Clear-Site-Data header emission on logout. Grep zero-match at HEAD `8bc1b0c0` across `core/**` + `frontend/**` (only appears in docs + `tools/pa_local.sh:39` comment). Neither `logout_view` (`auth_views.py:84-94`) nor `logout_enhanced_view` (`auth_views_enhanced.py:539-556`) sets the header.
- **F-C-STORE-1 HIGH (silent-swallow aggregate + contract-absent per-surface)** — 14 of 15 client-side persistence surfaces lack DECLARED logout-cleanup contract. S2204 §14 F1 15-surface baseline (3 Zustand persist + 12 direct localStorage) HEAD-re-verified UNCHANGED at `8bc1b0c0` (zero delta since S2204 close). Declared cleanup rate 1/15 (6.7%); accidental cleanup 3/15; no-cleanup 11/15.
- **F-C-COOKIE-1 LOW-MED (contract-absent class; documentary gap only)** — `SESSION_COOKIE_DOMAIN` + `SESSION_COOKIE_PATH` + `CSRF_COOKIE_DOMAIN` NOT declared (S2400 §2.3 SPECULATIVE flag LIFTED). Django defaults are correct at HEAD; risk is drift if later subdomain/path scoping is introduced. Not immediate-user-harm.
- **F-C-LOGOUT-1 MED (silent-swallow class)** — Basic logout endpoint (`core/auth_views.py:84-94`) has NO `@permission_classes`; silent 200 on unauthenticated (AttributeError swallowed). Enhanced endpoint at `auth_views_enhanced.py:539-556` FIXES this via `@permission_classes([IsAuthenticated])` at `:540`. Basic remains unpatched.
- **F-C-COCKPIT-1 MED (silent-swallow class, bounded)** — Cockpit two-stage auth MINOR-DRIFT re-verified STILL-LIVE at HEAD. `frontend/src/App.tsx:134-149` — 16 `/cockpit/*` `<Navigate>` redirects NOT wrapped by `ProtectedRoute`. S2201 §14.3 baseline preserved through Group 2200 close + Cat A + Cat B without remediation (institutional-drift aggravator justifies Cat C MED bump from S2201 LOW).

## Acceptance criterion 2-axis scoring (Rigby Q2 fold)

| Criterion | Platform Outcome | Audit Outcome |
|---|---|---|
| #1 Permission-floor observability | DEFERRED to Cat B (delivered S2402) | PASS-by-deferral |
| #2 Failure surfacing / typed error envelope | DEFERRED to Cat D | PASS-by-deferral |
| #3 Logout cleanup contract | **FAIL** (14/15 surfaces lack declared cleanup) | **PASS** (evidence plan complete) |
| #4 Session lifecycle discipline | **FAIL** (11/21 lifecycle-observability loci DEAD) | **PASS** (evidence plan complete) |
| #5 Cross-arc coordination flags preserved | PASS-partial (7 flags CF-C1 → CF-C7) | PASS |
| #6 Trust boundary inventory | DEFERRED to Cat A (delivered S2401) | PASS-by-deferral |

## §14.2 15-surface storageKeys × logout-cleanup CONTRACT table

15 surfaces from S2204 F1 baseline preserved at HEAD `8bc1b0c0` (zero delta):
- 1 CLEAN (`auth-storage` — Zustand persist functional-null-state via `authStore.logout()`)
- 3 PARTIAL (`pa-dock-state` via `paStore.syncUser(null)` incomplete field-list; `pipeline_dismissed_${workspaceId}` via workspace-change removeItem; `podcast_voice_profile_id` via profile-change removeItem)
- 11 NO-CLEANUP (`navigation-store` recentEntities + 10 direct localStorage keys)

Cross-user leakage severity: 1 HIGH-CRITICAL (auth-storage — mitigated by CLEAN) + 1 MED-HIGH + 3 MED + 3 LOW + 7 NONE.

## §14.3 21-loci lifecycle-observability rate table (Cat C acceptance criterion #4 evidence)

21 lifecycle-observability loci classified:
- 5 WORKING (session config declared + observable)
- 5 PARTIAL (working with drift or bounded issues)
- 11 DEAD (absent or not-enforced)

11-of-21 loci DEAD → session-lifecycle discipline undeclared at more than half of observable surfaces. Blocker to acceptance criterion #4.

## 7 cross-arc coordination flags (CF-C1 → CF-C7)

- **CF-C1** → Group 2500 API: refresh endpoint + logout response envelope + Clear-Site-Data emission spec
- **CF-C2** → Group 2600 PA: workspace-context lifecycle + `session_tool.retire` on user logout + `paStore.syncUser` field-list completeness
- **CF-C3** → Group 1700 Observability: lifecycle transition observability (single flag with sub-bullets per Rigby Q11 fold; explicitly extends Cat A CF-2 + Cat B CF-B5 for xx99 §5.4 Observability umbrella roll-up)
- **CF-C4** → Group 2300 Mobile: `MobilePushToken.revoked_at` cascade on user-logout
- **CF-C5** → Group 2200 Frontend: R1/R5/R6 execution + session-lifecycle test coverage per surface
- **CF-C6** → Cat D S2404 (this arc): silent-401 SYSTEMIC + typed-error envelope alignment + three-option decision-space intersection
- **CF-C7** → Group 1900 Governance: KillSwitch attestation on logout flow (boundary preserved; anchor-update candidate)

## Emerging weak-spot codification candidate (playbook §20 two-trigger rule)

**Silent-degrade vs explicit-failure ambiguity on session-lifecycle plane.**

Cat C proposes this as codification-candidate distinct from Cat B Q20 fold denominator-ambiguity:
- **Cat B denominator-ambiguity** = measurement / metrics ambiguity (what's the denominator? how do we count?)
- **Cat C silent-degrade ambiguity** = runtime UX / telemetry ambiguity (is the failure declared? is the degrade observable?)

Together they form a maturity discipline: measure first (Cat B), then declare failure modes (Cat C).

**13-of-14 Cat C findings are silent-degrade class.** The plane has near-zero explicit-failure paths.

**Two-trigger rule (Rigby SIGN cycle 1 Q20(b) fold):** Cat C = TRIGGER #1. Cat D (S2404) likely surfaces TRIGGER #2 in silent-401 SYSTEMIC audit — Cat C findings F-C-CSD-1 + F-C-STORE-1 + F-C-TAB-1 all point to Cat D's frontend caller surface. Codification threshold satisfied at S2499 xx99 close if Cat D confirms.

## §19.1 three-option decision space — Cat C proposes β as least-assumption default

Chris D-verdict-request at S2499 xx99 close for Group 2400 auth-contract acceptance criterion #4:

- **Option (α) Silent-refresh** — opaque to user; requires refresh endpoint + rotation-on-use policy + token expiry field. MIGRATION HIGH; OBSERVABILITY HARD.
- **Option (β) Explicit re-login** — visible; user-friction. MIGRATION LOW-MED; OBSERVABILITY LOW-MED; **Cat C proposes β as least-assumption default** (compatible with F-TOKEN-1 baseline; no refresh endpoint required; user-visible = observable).
- **Option (γ) Hybrid** — silent while active, explicit after N-min idle. MIGRATION HIGHEST; multi-tab race-conditions.

**Risk-gating constraint (Rigby SIGN cycle 1 Q19 fold + pre-commit nit 3):** Shipping any user-facing lifecycle change that relies on expiry semantics / VIP safety signals without ALSO closing F-C-VIP-1 (account_expires_at enforcement) creates a misleading safety signal. Treat F-C-VIP-1 remediation as prerequisite for shipping any expiry-signal-bearing UX.

## Cat C emerging weak-spot pattern (Q20 fold)

**Silent-degrade vs explicit-failure ambiguity** — playbook §20 codification candidate at S2499 xx99 close if 2nd application follows (Cat D likely trigger #2).

## Cat C recommendation lean for xx99 Chris D-verdict

**Option (β) explicit-re-login as PROPOSED PRIMARY DEFAULT** for REMEDIATION WINDOW because:
1. Zero token-model changes required (F-TOKEN-1 baseline preserved)
2. Zero new BE endpoint required (F-C-REFRESH-1 gap remains but bounded by documented no-refresh contract)
3. Lowest migration cost (BE + FE small changes)
4. Highest observability (all lifecycle transitions user-visible + event-emit via CF-C3)
5. Compatible with Cat D (S2404) typed-error-envelope work
6. Compatible with F-C-STORE-1 remediation (logout + Clear-Site-Data + storageKeys cleanup align at same emission point)

Option (α) or (γ) as **post-arc ENHANCEMENT** if UX friction / audit compliance / mobile UX warrant refresh discipline.

## Cross-arc coordination summary

- **Arc pin PRESERVED:** `pa-6279ead1714c4630` per playbook §16 arc-standard behavior (retirement at S2499 close). MC-14 CANDIDATE-threshold-satisfied extended to 4-arc-stages post-S2403 close.
- **SIGN pin RETIRED:** `pa-5096f5fc07754b18` at S2403 SIGN cycle 1 close (updated_count=4)
- **Arc progress:** S2400 parent scoping + S2401 P1 Cat A + S2402 P2 Cat B + S2403 P3 Cat C shipped → **S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC (NEXT)** → S2499 xx99. Runtime target 6 sessions — **4 of 6 shipped**; runtime cap 8.

## S2403 CRITICAL findings post-arc remediation queue (Cat C additions to Cat A + Cat B rank-1 P0 batch)

Per Cat A + Cat B §19.2 rank-1 co-equal P0 batch — Cat C extends (POST-ARC — not this session's authoring scope):

- **Cat A F-CRIT-1** PURGE_SECRET hardcoded fallback (P0 PR)
- **Cat A F-BND-4a** Unauthenticated bet-placement WRITE (P0 PR)
- **F-C-VIP-1 NEW P0 CANDIDATE** — VIPInvite.account_expires_at ENFORCEMENT (runtime middleware check OR periodic beat task); risk-gate prerequisite for shipping any α/β/γ expiry-signal-bearing UX per §19.1 constraint

## Follow-on / T-slot queue additions (Cat C)

- F-C-REFRESH-1 refresh discipline decision-space execution (post-Chris-verdict at xx99)
- F-C-CSD-1 Clear-Site-Data emission
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution
- F-C-TAB-1 cross-tab storage-event listener
- F-C-COOKIE-1 cookie Domain/Path declaration
- F-C-LOGOUT-1 basic logout permission decorator or endpoint retirement
- F-C-COCKPIT-1 cockpit two-stage remediation (S2201 T-slot)
- F-C-ROLE-SCOPE role-transition session-scope semantics (if future workflow surfaces requirement)
- F-C-FIX-1 session.cycle_key defense-in-depth
- F-C-LOGOUT-2 enhanced logout silent-200 refinement
- F-C-PA-CONV-1 user-logout session_tool.retire cascade (Group 2600 PA)
- F-C-MOBILE-1 MobilePushToken.revoked_at cascade (Group 2300 Mobile)
- F-C-EVENT-1 login/logout event emit (Group 1700 Observability)

## Session count status post-S2403

- Group 2400 In-progress at 4 of 6 sessions (S2400 parent + S2401 P1 Cat A + S2402 P2 Cat B + S2403 P3 Cat C shipped)
- Next child = S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC Resolution
- Next `xx99` at S2499 canonical summary (playbook §11.3 ELEVENTH application per current TENTH baseline)

## Anchor updates at S2403 close

- **ARCHITECTURE_INDEX v85 → v86** with §1.89 S2403 registration (post-Chris-"commit it"-2026-07-05)
- **OPEN_ARCS Group 2400 In-progress row** updated from "S2400 parent scoping + S2401 P1 Cat A + S2402 P2 Cat B (2026-07-05) — 3 of 6 shipped" to "S2400 parent scoping + S2401 P1 Cat A + S2402 P2 Cat B + S2403 P3 Cat C (2026-07-05) — 4 of 6 shipped"
- **00-START-NEXT-SESSION.md** overwritten with S2404 P4 Cat D open priorities

## Post-arc-close cascade

Per Chris "commit it" ratification at S2403 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge as separate cascade PR.

## S2402 Cat B open items preserved

- **F-B-CRIT-1** Permission-floor implicit-inheritance rate ~80-90% ESTIMATE (post-arc option (a)/(b)/(c) Chris D-verdict at xx99)
- **F-B-CRIT-2** Silent-401 SYSTEMIC (owned by Cat D S2404 — this arc's next session)
- **F-B-HIGH-1** STAFF_REQUIRED_PATHS phantom-entries cleanup OR add explicit views
- **F-B-HIGH-3** Workspace-membership implicit permission gate via WORKSPACE_AWARE_AGENTS (CF-B2 to Group 2600 PA; Cat C reinforces via CF-C2 workspace-context lifecycle)
- **F-B-HIGH-4** `@authentication_classes([])` per-site CRITICAL escalation for login/token flows
- **F-B-OWN-6** CI test-harness enforce permission-floor declarations

Meta-methodology promotions (candidates for §20 codification at S2499):
- **MC-10 EIGHTH-consecutive 20-Q cadence** — codification-ready-pending-Chris at 8-arc baseline (S2201-S2402 seven-consecutive + S2403 = 8-consecutive)
- **MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails** extended to 5th consecutive arc (Group 1900 + 2000+ + 2100 + 2200 + 2400 4-child structure preserved through Cat C)
- **MC-14 CANDIDATE-threshold-satisfied** extended to 4-arc-stages (Group 2200 + Group 2400 Cat A + Cat B + Cat C = 4 confirming arc-stages)
- **NEW MC candidate** — Cat C silent-degrade-vs-explicit-failure ambiguity as playbook §20 codification candidate TRIGGER #1 (awaiting TRIGGER #2 in Cat D or future arc)

## Provenance chain

- 2026-07-05: S2400 parent scoping close (Chris "commit it" ratified; PR #2908/#2909)
- 2026-07-05: S2401 P1 Cat A close (Chris "commit it" ratified; PR #2910/#2911)
- 2026-07-05: S2402 P2 Cat B close (Chris "commit it" ratified; PR #2912)
- 2026-07-05: S2403 P3 Cat C draft written (post-6-parallel-Explore sweep + verifier-loop; 1 sub-agent conflict caught)
- 2026-07-05: Rigby SIGN cycle 1 CLOSED via dedicated fresh SIGN pin `pa-5096f5fc07754b18` (retired); 32 folds landed pre-Chris-ratification; 4-batch × 5-Q = 20-Q cadence EIGHTH-consecutive-tested application
- 2026-07-05: Chris "commit it" ratified 32-fold SIGN-with-edits wholesale at MED-HIGH confidence — status flipped `draft` → `active` per playbook §16
