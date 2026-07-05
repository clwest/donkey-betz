# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + S2404 CLOSED + S2499 XX99 QUEUED

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**S2404 GROUP 2400 AUTH P4 CAT D CHILD AUDIT COMMITTED AT 2026-07-05.** Group 2400 Auth arc pin `pa-6279ead1714c4630` PRESERVED through S2404 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails (MC-14 CANDIDATE-threshold-satisfied extended to 5-arc-stages via Group 2200 + Group 2400 Cat A + Cat B + Cat C + Cat D = 5 confirming arc-stages). `tools/pa_local.sh:280` restored to arc pin post-SIGN cycle 1 close. S2404 SIGN pin `pa-015448e962ad4038` retired at child-audit SIGN cycle 1 close (FIFTEENTH consecutive dedicated fresh SIGN pin retirement — 10 xx99 + 1 parent-scoping-light-SIGN + Cat A + Cat B + Cat C + this cycle).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.** Pin ownership already verified as chris at S2401 open (conversation_owner_match=true) — Cat A + Cat B + Cat C + Cat D preserved pin, so verification carries forward.

## READ THIS SECOND — GROUP 2400 AUTH ARC IN-PROGRESS (5 OF 6 SHIPPED); NEXT = S2499 P5 XX99 CANONICAL SUMMARY

**Group 2400 Auth: S2404 P4 Cat D CLOSED 2026-07-05.** Chris "commit it" 2026-07-05 ratified 12-fold SIGN-with-edits wholesale at MED-HIGH confidence (~0.80-0.85; HIGHEST Group 2400 child confidence to date exceeding Cat A 0.74 + Cat B ~0.8 + Cat C ~0.82); status flipped `draft` → `active`. NINETEENTH-consecutive application of playbook §11.2 20-section child-audit template per S2403 handoff.

- **Arc pin PRESERVED:** `pa-6279ead1714c4630` per playbook §16 arc-standard behavior (retirement at S2499 close)
- **SIGN pin RETIRED:** `pa-015448e962ad4038` at S2404 SIGN cycle 1 close (updated_count=6)
- **Arc progress:** S2400 parent scoping (shipped) + S2401 P1 Cat A (shipped) + S2402 P2 Cat B (shipped) + S2403 P3 Cat C (shipped) + S2404 P4 Cat D (shipped) → **S2499 P5 xx99 canonical summary (NEXT)**. Runtime target 6 sessions — **5 of 6 shipped**; runtime cap 8.
- **MC-4 dial-back-resolution 5th confirming arc RESOLUTION CANDIDATE at S2499 close** — Group 2400 Auth 4-child structure completes MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails across-5-consecutive-arcs (1900+2000++2100+2200+2400), resolving S2199 Q3 STRENGTHEN dial-back at S2499 close per §5.3 Group 2200 canonical summary. Auth was materially different in scope (full auth stack, not a single UI surface family) — 5th-arc extension IS a validated stress test.

## READ THIS THIRD — S2404 CAT D LOAD-BEARING INPUTS FOR S2499 XX99

**S2404 11 headline Cat D findings (6 HIGH + 5 non-HIGH):**

- **F-D-CALL-1 HIGH** (technical_debt / silent-degrade) — 803 consumer call-sites at HEAD `31398008` (57 direct api.<verb>() + 667 useQuery/useMutation + 79 raw fetch bypass); ~99% silent-swallow rate via api.ts:48-56 console.warn-only path; extends S2203 A3 ~630 baseline via verifier-loop-resolved denominator.
- **F-D-BYPASS-1 HIGH** (boundary_violation / silent-degrade) — 79 raw fetch() across 31 files bypass api.ts interceptor entirely (9.8% of consumer surface); no token attach, no 401 catch, no observability. Notable: LiveMetricsDashboard.tsx:94 uses `fetch('/api/platform/live-metrics/', {credentials:'include'})`.
- **F-D-SIDEBAR-1 HIGH** (missing_connection / silent-degrade NEW BEYOND CAT C) — `Sidebar.tsx:356` onClick clears authStore + syncUser(null) + Zustand persist localStorage clear, but does NOT invoke `authApi.logout()`. Backend `authtoken_token` DB row never deleted via sidebar path. Combined with F-C-REFRESH-1 (no refresh endpoint) + Cat A F-DEC-1 (no expiry): attacker-valid window on leaked token = indefinite.
- **F-D-ENVELOPE-1 HIGH** (missing_connection / silent-degrade) — Grep verified 0 `AxiosError|axios.isAxiosError` matches across `frontend/src/`. Typed-error-envelope adoption is greenfield.
- **F-D-BOUNDARY-1 HIGH** (missing_connection / silent-degrade) — Grep verified 0 error boundaries anywhere (S2201 §15.5 CONFIRMED-STILL-LIVE at HEAD).
- **F-D-PA-1 HIGH** (technical_debt / silent-degrade; Rigby Q10 fold escalated MED→HIGH) — PA-chat endpoints (`/pa/chat/`, `/pa/chat/status/`, `/pa/conversations/`) do NOT match whitelist substring. 401 mid-conversation = silent reject. PA UI enters undefined state (looks like agent-hang).
- **F-D-WHITELIST-1 MED** (drift / silent-degrade) — Extends S2203 §14 F3.5 BRITTLE substring; 0 false-positives at HEAD but scales badly.
- **F-D-OWN-1 MED** (unclear_owner / **governance NON-silent-degrade**) — CODEOWNERS file absent at `.github/`, root, `docs/`. HEAD-verified.
- **F-D-OWN-2 MED** (unclear_owner / **governance NON-silent-degrade**) — No CI test-harness for silent-401 rate observability. Extends F-B-OWN-6.
- **F-D-EVENT-1 MED** (event_gap / silent-degrade) — Zero auth-event emission on any observability channel; `console.warn` only signal is browser-side.
- **F-D-COCKPIT-1 MED** (drift / silent-degrade + ownership-drift-risk flag per Rigby Q19 fold) — 16 cockpit `<Navigate>` at `frontend/src/App.tsx:134-149` NOT wrapped by ProtectedRoute STILL-LIVE at HEAD.

**§14.1 silent-degrade class rate (Rigby Q5 fold):** 17 of 19 findings (89.5%) silent-degrade class. 2 governance findings F-D-OWN-1 + F-D-OWN-2 explicitly named as non-silent-degrade. **Q20 fold TRIGGER #2 CONFIRMED** (Cat C 92.9% + Cat D 89.5% both above codification threshold). Tightened codification claim: silent-degrade dominance across Cat C + Cat D exceeds §20 dual-trigger threshold; promote to v3 candidate focused on **auth failure handling (401/403/refresh/logout)** with explicit UX + telemetry requirements — scope-bounded to auth plane.

**§14.5 803-call-site classification by inheritance-path** — 57 direct + 667 hook + 79 raw fetch; 724 interceptor-routed (90.2%) + 79 bypass (9.8%); ~99% silent-swallow rate at HEAD.

**7 cross-arc coordination flags emitted (CF-D1 → CF-D7)** — CF-D1 Group 2500 API (refresh + envelope + CSD + typed-error + registry) + CF-D2 Group 2600 PA (retire cascade + workspace-context + PA-chat exposure) + CF-D3 Group 1700 Observability (umbrella roll-up extends Cat A CF-2 + Cat B CF-B5 + Cat C CF-C3; adds silent-401 rate + `authHandling: 'suppress_redirect'` telemetry per Rigby Q7 fold) + CF-D4 Group 2300 Mobile + CF-D5 Group 2200 R6 error-boundary framework ⚠ **BLOCKING PREREQUISITE for option-γ** (Rigby Q18 fold) + CF-D6 Group 1900 (KillSwitch preservation) + CF-D7 Group 2400 Auth internal xx99 α/β/γ × 2 intersection with Cat C α/β/γ.

**§19.1 typed-error-envelope decision space (α/β/γ):** Cat D proposes **Option (γ) React-Query error callbacks + top-level ErrorBoundary** as PROPOSED PRIMARY DEFAULT (γ = mechanism; Cat C β "explicit re-login" = message/UX policy nested inside γ per Rigby Q6 fold). Handler MUST distinguish 401/403 vs network/offline vs 5xx (Rigby Q9 fold). Copy MUST avoid time-based "expired" until F-C-VIP-1 resolves (use "Sign-in required" preserving Cat C risk-gate).

**§19.1 whitelist-replacement decision space (α/β/γ × 2 second axis):** Cat D proposes **Option (γ) per-api-module `authHandling: 'default' | 'suppress_redirect'` string enum** (Rigby Q7 fold — NOT boolean; harder to misuse) + telemetry event on every `suppress_redirect` use.

**Cat A/B/C findings STILL-LIVE at HEAD 31398008:** F-DEC-1 (numeric drift-down 68/9→65/10; applied uses 64/9 with definition site in denominator) + F-WS-1 + F-B-CRIT-1 + F-B-CRIT-2 + F-C-VIP-1 + F-C-REFRESH-1 + F-C-CSD-1 + F-C-STORE-1 + F-C-LOGOUT-1 + F-C-COCKPIT-1 all CONFIRMED-STILL-LIVE.

## READ THIS FOURTH — S2499 P5 XX99 SCOPE (CANONICAL SUMMARY + ARC CLOSE)

**S2499 = P5 xx99 canonical summary + arc close under Group 2400.** ELEVENTH-consecutive application of playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology after S1399+S1499+S1599+S1699+S1799+S1899+S1999+S2099+S2199+S2299 prior ten.

**Scope** (per playbook §11.3 12-section template):
- §1 Executive Summary (500-800 words consolidating all four categories)
- §2 What This Arc Answered — per-child rollup of 28 canonical questions
- §3 Consolidated Domain Shape — single map of auth surface
- §4 Cross-Cutting Patterns — themes visible only across multiple children (e.g., silent-degrade dominance; declared-fictional class introduction; two-sided FE-symptom-vs-BE-model framing)
- §5 Resolved Contradictions — where children disagreed; canonical verdict
- §6 Unresolved Unknowns — explicit list; promotes to §8
- §7 Anchor-Update Recommendations (concrete edits; xx99 applies them):
  - §7.1 PLATFORM_INVENTORY (add §Auth autoblock per Cat A AU-1 + Cat B AU-B2 + Cat C AU-C2 + Cat D AU-D3)
  - §7.2 PLATFORM_WHAT_IT_IS (add §Auth narrative subsection per Cat A/B/C/D)
  - §7.3 ARCHITECTURE_INDEX (α/β/γ × 2 decision matrix pointer per Cat D AU-D6)
  - §7.4 Other affected docs (CREATE `docs/topics/auth.md` + AU-D7 DOC_LIFECYCLE cross-link; refresh `docs/topics/frontend.md` per Cat D AU-D1; CODEOWNERS declaration per Cat D AU-D5)
- §8 Follow-On Research Queue — ranked next-mission list (rank-1 co-equal P0 batch preserved from Cat A/B/C + Cat D tiered ordering P0-A/B/C per Rigby Q15 fold)
- §9 Cross-Links to Delegated Arcs — CF-A1..CF-A7 + CF-B1..CF-B5 + CF-C1..CF-C7 + CF-D1..CF-D7 = ~26 total cross-arc coordination flags (dedup + roll-up); umbrella observability roll-up to Group 1700 preserved
- §10 What This Research Taught Us About How to Do Research — meta-methodology retrospective per playbook §11.3 (NON-NEGOTIABLE per feedback_xx99_meta_methodology_section); ELEVENTH-consecutive §10 application. Load-bearing §10.2 codification candidate: silent-degrade-vs-explicit-failure ambiguity on auth-failure-handling plane (Cat C TRIGGER #1 + Cat D TRIGGER #2 CONFIRMED); scope-bounded per Rigby Q5 fold
- §11 Arc Change Log — child + session + Rigby verdict + fold edits ledger
- §12 Appendix — provenance + file paths + verifier-loop history

**Central question xx99 answers.** *Does the Group 2400 Auth arc consolidate a canonical answer to the parent scoping central lens question ("Is the platform's auth model a contract, or an accretion of per-surface defaults whose failures are silently swallowed?"), and what is the Chris D-verdict on Cat B (a)/(b)/(c) + Cat C (α)/(β)/(γ) + Cat D α/β/γ × 2 decision spaces?*

**Load-bearing inputs (xx99 must consume + consolidate):**
- All four Cat A/B/C/D child audit docs at HEAD `31398008` (Cat D)
- Central lens question from S2400 parent scoping
- 6-criterion acceptance from S2400 §5 (§14.5 trust-boundary rate + §14.5 permission-floor rate + §14.2 15-surface × cleanup + §14.5 803-call-site + smoke-test coverage + failure-mode discipline)
- 6-item anti-scope from S2400 §7 (preserved through arc; no in-scope-drift observed)
- Cat A + Cat B + Cat C + Cat D findings inheritance chain (~40 findings total; deduplicate + consolidate)
- 26 cross-arc coordination flags CF-A/B/C/D + roll-up rules per Cat C Q11 fold
- MC-4 5th confirming arc resolution: extends CODIFICATION-CONFIRMED-with-scope-guardrails across-5-consecutive-arcs; resolves S2199 Q3 STRENGTHEN dial-back
- MC-10 codification-ready at 10-arc baseline (9 arcs of 20-Q child cadence + 6 arcs of parent-scoping-light-SIGN cadence + this)
- MC-14 CANDIDATE-threshold-satisfied extended to 5-arc-stages

**Sub-agent dispatch shape (playbook §11.3 note):** xx99 canonical summaries do NOT spawn sub-agents. Single-doc synthesis by parent Claude.

**Rigby SIGN cycle 1 REQUIRED via dedicated fresh isolation pin per playbook §15** (canonical summary = required light SIGN, single-batch × 4-Q per S1399-S2299 TEN-consecutive tested pattern — ELEVENTH-consecutive same-cadence application candidate at canonical-summary stage; NOT the 20-Q child-audit cadence).

**Arc pin retirement.** `pa-6279ead1714c4630` MUST be retired at S2499 close via `session_tool.retire` per playbook §16 arc-close discipline (ELEVENTH formal arc-pin retirement in Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten). SIGN pin minted fresh; retired at cycle close (SIXTEENTH consecutive dedicated fresh SIGN pin retirement).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2404 arc-close cascade residuals

Per Chris "commit it" ratification at S2404 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.
- **Auth topic doc gap preserved** — `docs/topics/auth.md` + `docs/topics/session_lifecycle.md` do NOT exist. Cat D AU-D2 recommends CREATE with 4 subsections (Cat A mechanism inventory + Cat B permission-floor + Cat C session-lifecycle + Cat D FE integration); AU-D7 requires DOC_LIFECYCLE cross-link inside. Candidate S2499 xx99 anchor-update per §7.4.
- **`PLATFORM_INVENTORY §Auth` autoblock gap preserved** — no dedicated Auth autoblock exists. Cat D AU-D3 extends Cat A AU-1 + Cat B AU-B2 + Cat C AU-C2 with silent-401-rate + typed-error-envelope-adoption + interceptor-bypass rate columns. Candidate S2499 xx99 anchor-update per §7.1.
- **`PLATFORM_WHAT_IT_IS §Auth` narrative subsection gap preserved** — no dedicated Auth subsection exists. Cat D AU-D4 extends Cat A/B/C recommendations. Add narrative for silent-degrade-vs-explicit-failure ambiguity as codified §20 weak-spot pattern (post-Q20 fold TRIGGER #2 CONFIRMED). Candidate S2499 xx99 anchor-update per §7.2.
- **CODEOWNERS declaration** — Cat D AU-D5 remediation; single-file addition. Candidate S2499 xx99 §7.4.
- **ARCHITECTURE_INDEX α/β/γ × 2 decision matrix pointer** — Cat D AU-D6 addition per Rigby Q16 fold. Candidate S2499 xx99 §7.3.
- **Auth acceptance criteria (S2400 §5)** — 6 criteria + acceptance/deferral verdict per criterion at xx99 close.
- **Session-lifecycle test coverage gap** — 0-of-17 session-lifecycle endpoints have declared smoke-test coverage. Blocker to acceptance criterion #6; extends Cat A F-CRIT-2. Post-arc smoke-test authoring in follow-on queue.

### S2404 CRITICAL findings post-arc remediation queue (rank-1 co-equal P0 batch with Cat D tiered ordering per Rigby Q15 fold)

Per Cat D §19.2 rank-1 co-equal P0 batch preserved from Cat A + Cat B + Cat C + extended by Cat D (POST-ARC — not xx99's authoring scope):

**P0-A platform-wide / whole-auth-surface blast radius:**
- Cat D F-D-CALL-1 803-scale silent-401 remediation
- Cat D F-D-BYPASS-1 79-raw-fetch bypass reconciliation
- Cat D F-D-ENVELOPE-1 Typed-error-envelope (α/β/γ decision post-Chris-D-verdict at xx99)
- Cat D F-D-BOUNDARY-1 Error-boundary framework establishment (S2299 §8.3 R6 execution)

**P0-B token lifecycle / security window:**
- Cat D F-D-SIDEBAR-1 Sidebar backend-token-revoke fix (single-line addition per Cat C AU-C1)
- Cat C F-C-REFRESH-1 refresh discipline decision-space execution
- Cat C F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT (risk-gate prerequisite for α/β/γ)
- Cat C F-C-CSD-1 Clear-Site-Data emission on logout
- Cat C F-C-STORE-1 15-surface × logout-cleanup declared contract execution

**P0-C endpoint-specific:**
- Cat A F-CRIT-1 PURGE_SECRET hardcoded fallback remediation (preserved)
- Cat A F-BND-4a Unauthenticated bet-placement WRITE remediation (preserved money-path boundary)
- Cat B F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% (Chris D-verdict at xx99 on (a)/(b)/(c))
- Cat B F-B-CRIT-2 Silent-401 SYSTEMIC (Cat D delivered 803-scale evidence + α/β/γ × 2 decision-space)
- Cat D F-D-WHITELIST-1 Whitelist replacement (α/β/γ decision post-Chris-D-verdict at xx99)

### Group 2200 T-slot follow-on queue (owed to Group 2400+ execution — updated with Cat D contribution)

- **T1 Group 2400 Auth cross-arc handoff bundle** — DELIVERED by Group 2400 arc (S2401-S2404) — silent-401 + logout cleanup + session lifecycle + permission-floor uniformity — **S2404 Cat D DELIVERED frontend integration evidence + Silent-401 SYSTEMIC 803-scale + typed-error envelope α/β/γ × 2 decision-space + T1 handoff execution readiness**
- **T2 Group 2500 API cross-arc handoff bundle** — NEXT arc after Group 2400 close per S2299 §8.2 (Cat B CF-B1 + Cat C CF-C1 + Cat D CF-D1 all elevate registry + refresh-endpoint + logout-envelope + Clear-Site-Data + typed-error-envelope design-prep candidate)
- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after Group 2500 close (Cat B CF-B2 + Cat C CF-C2 + Cat D CF-D2 all elevate workspace-context authz + `session_tool.retire` cascade + PA-chat 401 UX design + paStore field-list completeness)
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close (Cat B CF-B5 + Cat C CF-C3 + Cat D CF-D3 all elevate 503-fork asymmetry + login/logout event emit + silent-401 rate + `authHandling: 'suppress_redirect'` telemetry + smoke-test coverage; xx99 Observability umbrella roll-up)
- **Maintainer-decision batch (5 items governance gate)** — CODEOWNERS (Cat D AU-D5) + DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership
- **T2 post-arc T-slot (10 items)** — per S2299 §8
- **T3 conditional post-arc (4 items)** — cross-tab sync + Betting session-scoped state + runtime schema validation + REST↔WS joint T7
- **Cat D contribution to follow-on queue** — silent-401 rate telemetry design (F-D-OWN-2 + CF-D3) + 79-raw-fetch classification refinement (Rigby Q17 fold: 3-axis by auth-required + credentials mode + response type) + optional non-401 failure envelope audit (Rigby Q17 fold — JSON parse + network offline + timeout + aborted)

### S2199 post-arc T-slot execution queue (unchanged carry into S2499)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2499.

### Session count status

- Group 2400 In-progress at 5 of 6 sessions (S2400 parent + S2401 P1 Cat A + S2402 P2 Cat B + S2403 P3 Cat C + S2404 P4 Cat D shipped)
- Next child = S2499 P5 xx99 canonical summary
- xx99 = playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology ELEVENTH-consecutive application after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 ten prior

## SESSION READY CHECK (before opening S2499 P5 xx99)

Before drafting the S2499 xx99 canonical summary:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (Group 2400 arc pin `pa-6279ead1714c4630` PRESERVED through S2404; `tools/pa_local.sh:280` unchanged from S2400 open post-cycle-restore)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology + §11.3 exemplar chain (S2299 most recent) for shape reference
3. Read all four Cat A/B/C/D child audit docs fully — S2499 primary load-bearing input; consolidate + deduplicate + roll-up
4. Read `docs/research/domains/auth/2400_auth_domain_scoping.md` §5 acceptance criteria + §7 anti-scope for xx99 verdict inputs
5. NO sub-agent dispatch per playbook §11.3 note — single-doc synthesis by parent Claude
6. Draft the 12-section canonical summary per §11.3 skeleton with §10 meta-methodology NON-NEGOTIABLE (per feedback_xx99_meta_methodology_section)
7. Route to Rigby SIGN cycle 1 via dedicated fresh isolation pin per playbook §15 (canonical summary = required light SIGN); expected cadence single-batch × 4-Q per S1399-S2299 TEN-consecutive tested pattern (ELEVENTH-consecutive candidate)
8. Fold SIGN edits; land as `status: draft` on filesystem; present Chris ratification card
9. Retire arc pin `pa-6279ead1714c4630` via `session_tool.retire` at S2499 close per playbook §16 arc-close discipline (ELEVENTH formal arc-pin retirement)
10. Execute anchor-update batch per §7 recommendations (PLATFORM_INVENTORY §Auth autoblock + PLATFORM_WHAT_IT_IS §Auth narrative + ARCHITECTURE_INDEX v87 → v88 with §1.91 registration + CREATE `docs/topics/auth.md` + refresh `docs/topics/frontend.md` + CODEOWNERS declaration)
11. Post-close docs cascade + build_docs_provenance per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step` — MANDATORY

**S2499 open command (Chris short command):** `Close research group 2400` or `Continue research group 2400: xx99` or equivalent invocation.
