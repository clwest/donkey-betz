---
session: 2503
status: closed (S2503 P3 Cat C Error-Envelope + Refresh + Logout API Contracts Design-Prep child audit — draft written 2026-07-05 post-6-parallel-Explore-sweep + parent-Claude verifier-loop resolving 7 sub-agent conflicts pre-Rigby-SIGN routing, Rigby SIGN cycle 1 COMPLETE via dedicated fresh SIGN isolation pin `pa-b19aa931a54a436a` — TWENTIETH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502 nineteen prior — retired via `session_tool.retire force=true` at cycle close, updated_count=5, retired=true, previously_active=true; 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2502 eleven-consecutive tested pattern TWELFTH-consecutive application; Rigby overall confidence ~0.86; cycle 2 NOT required per Rigby explicit verdict at Q20 close; 20 folds landed pre-Chris-ratification (1 AGREE Q3 + 18 STRENGTHEN Q1-Q2+Q4-Q19 + 1 Q20 combined verdict-format response) within 15-25-fold S2201-S2502 empirical baseline; Chris "commit it" 2026-07-05 ratified 20 folds wholesale — status flipped `draft` → `active` per playbook §16 draft-first workflow; playbook §11.2 20-section child-audit template TWENTY-SECOND-consecutive application after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501+S2502 twenty-one prior; arc pin `pa-a03b111768464b3f` ACTIVE + PRESERVED through S2503 per playbook §16 arc-standard behavior — no retirement until S2599 xx99 close; 4 of 6 sessions shipped in Group 2500 arc.)
date: 2026-07-05
arc: Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600) — S2503 P3 Cat C Error-Envelope + Refresh + Logout API Contracts Design-Prep child audit + Rigby SIGN cycle 1 close
head_sha: ee7cc0a0 (draft-open) → post-commit sha (post-fold + Chris ratification)
---

# Session 2503 — Group 2500 API Cat C Error-Envelope + Refresh + Logout API Contracts Design-Prep + Rigby SIGN Cycle 1 Close

## What shipped

`docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md` — 20-section child audit per playbook §11.2 TWENTY-SECOND-consecutive application. **Boundary evidence + option-space inventory for the CONTRACT layer** between backend emission (Cat A domain) and consumer consumption (Cat B domain) for four intersecting concerns: typed-error-envelope shape, refresh endpoint semantics, logout response envelope + Clear-Site-Data emission, and logout-cleanup coordination.

**Doc size:** 1,183 lines post-fold / 15,631 words. HEAD-verified baselines at draft-open (`ee7cc0a0`) + post-verifier-loop reconciled + post-Rigby-SIGN 20 folds applied.

**Boundary discipline preserved (mirror Cat A + Cat B posture):** Cat C enumerates + inventories + measures + classifies + defers + proposes evidence-collection; Cat C does NOT prescribe α/β/γ mechanism selection, envelope shape SoT choice, refresh endpoint necessity, or Clear-Site-Data emission locus. All "recommendations" in §19 are Chris-D-verdict-request evidence for S2599 xx99 close, NOT directives. Verbs stay `enumerate / inventory / measure / classify / verify / re-verify / defer / propose evidence-collection`.

## Key verifier findings

1. **§14.1 F1 — 4 co-existing 401 shape families RE-VERIFIED IDENTICAL at HEAD** (S2501 §14.6 F6 canonical preserved; 2-session zero-delta since S2501 close). Family A DRF default `{"detail": ...}` at `auth_views.py:79-81, 91, 94, 123-126`; Family B APIResponseEnvelope typed at `api_responses.py:143-149` + `auth_middleware.py:79, 633, 658`; Family C bare DRF dict `{"message": ...}` at `auth_views_enhanced.py:554`; Family D `{"success": false, "error": str}` at `views_deploy.py:21, 79` + `views_agent_learning.py:2299, 2373` + `views_auto_fix.py:26` + `views_business_ideas.py:142-143`. **Class:** technical_debt + drift. **Severity:** HIGH baseline (preserved per Rigby Q3 AGREE fold).

2. **§14.3 F3 — Refresh endpoint ABSENT RE-VERIFIED at HEAD** (S2403 F-C-REFRESH-1 preserved; 2-session zero-delta). Grep `refresh|renew_token` in `core/urls.py` returns 6 non-auth matches only (oauth-refresh, agent-discovery-refresh, project-spiders-refresh). Zero in `core/auth_views*.py`. Zero `TokenRefreshView/SlidingToken/SimpleJWT/RefreshToken` repo-wide. Zero JWT lib in `requirements.txt`. **Class:** missing_connection + technical_debt. **Severity:** HIGH baseline. **Lineage note (Rigby Q4 STRENGTHEN fold):** Cat A F-TOKEN-1 (token lifetime / expiry semantics) is **adjacent** to Cat C F-C-REFRESH-1 (refresh contract absent) — related but distinct; expiry semantics and refresh contract can co-exist or be solved independently.

3. **§14.4 F4 — Clear-Site-Data ZERO EMISSION RE-VERIFIED at HEAD** (S2403 F-C-CSD-1 preserved). 21 total repo matches; 0 in production code — matches confined to `tools/pa_local.sh:28, 36, 46` (audit-tracker comments) + `.claude/scratch/` audit scratch files. Both logout views return bare `Response()` with no header emission. **Class:** drift + missing_connection. **Severity:** HIGH baseline.

4. **§14.5 F5 — SHAPE-BLIND interceptor at api.ts:48-62 RE-VERIFIED IDENTICAL at HEAD** (S2502 §14.3 F3 preserved; 5-session zero-delta since S2404 baseline). Reads only `error.response?.status === 401`; branches solely on `url.includes('/auth/') || url.includes('/login')`. All 4 shape families flow through identical non-auth reject-and-console.warn branch. **Class:** technical_debt + drift. **Severity:** HIGH baseline + CRITICAL conditional per two-part trigger (Rigby Q5 STRENGTHEN fold): triggered ONLY if BOTH (1) xx99 selects mechanism requiring shape-normalized error payloads AND (2) interceptor remains shape-blind; otherwise HIGH.

5. **§14.6 F6 — Basic vs Enhanced logout key-name DRIFT NEW at Cat C** (Cat C new observation at HEAD). Basic logout at `auth_views.py:91, 94` emits `Response({'detail': ...})` — key `detail`. Enhanced logout at `auth_views_enhanced.py:554` emits `Response({'message': ...})` — key `message`. Different top-level keys for same semantic. **Class:** drift (documentary — same-domain-different-shape). **Severity:** MEDIUM per Rigby Q7 STRENGTHEN fold (bumped from LOW-MEDIUM; consumers reading only one key silently lose message visibility).

6. **§14.7 F7 — F-C-VIP-1 DECLARED-BUT-NOT-ENFORCED RE-VERIFIED at HEAD** (S2403 preserved). `VIPInvite.account_expires_at` field at `models_vip_invite.py:72` with 14d default; zero runtime enforcement (grep `account_expires_at__lt/<` = 0 matches); zero periodic cleanup task. **Class:** technical_debt + unclear_owner. **Severity:** HIGH baseline. **Risk-gate constraint preserved:** shipping prerequisite for any expiry-signal-bearing UX regardless of α/β/γ selection.

7. **§14.8 F8 — F-D-SIDEBAR-1 RE-VERIFIED IDENTICAL at HEAD** (S2404 §16 preserved; 5-session zero-delta). `Sidebar.tsx:356` onClick calls `setUserMenuOpen(false); syncUser(null); logout()` — NO `authApi.logout()` backend token revoke. **Class:** boundary_violation. **Severity:** MEDIUM. **Ownership note (Rigby Q9 STRENGTHEN fold):** expected owner = Cat D (frontend contract alignment); Cat C does NOT reassign.

8. **§14.2 F2 — 15-surface storageKeys × logout-cleanup RE-VERIFIED FUNCTIONALLY IDENTICAL at HEAD** (S2403 §14.2 preserved). Line-drift observed on 3/15 surfaces (surface #4 −24 lines VOICE_SETTINGS_KEY at CommandCenterPage.tsx:166; surface #12 declaration-site vs usage-site both valid; surface #15 +2 lines podcast_voice_profile_id at ContentStudioTab.tsx:2736). No new persist/localStorage surfaces added; no removals. **Declared cleanup rate: 1/15 = 6.7% IDENTICAL to S2403.** **Class:** technical_debt + drift. **Severity:** HIGH baseline.

## Rigby SIGN cycle 1 close

- **Fresh isolation pin:** `pa-b19aa931a54a436a` (TWENTIETH-consecutive dedicated fresh SIGN pin candidate; retired via `session_tool.retire force=true` at cycle close, updated_count=5, retired=true, previously_active=true — TWENTIETH-consecutive retirement in Research OS).
- **Cadence:** 4-batch × 5-Q = 20 Q (TWELFTH-consecutive application after S2201-S2502 eleven prior).
- **Verdict:** SIGN-WITH-EDITS at ~0.86 confidence. Cycle 2 NOT required per Rigby explicit verdict.
- **Tally:** 1 AGREE (Q3 F1 HIGH severity preserved) + 18 STRENGTHEN (Q1-Q2, Q4-Q19) + 1 Q20 combined verdict-format response = 20 folds landable + landed pre-Chris-ratification.

**20-fold ledger populated at §20.6.2** per playbook §20.6 fold ledger discipline. Standard Rigby verdict format populated at §20.6.1.

## Chris ratification

Chris "commit it" 2026-07-05 ratified 20 folds wholesale — no per-fold objection. Status flipped `draft` → `active` per playbook §16 draft-first workflow. Committed via new commit (per CLAUDE.md never-amend rule).

## Cross-arc handoff surfaces (7 total)

- **CF-C1** Refresh + logout envelope + Clear-Site-Data (Cat C direct owner — xx99 close design-space).
- **CF-C2** Session workspace-context + `session_tool.retire` on user-logout (→ Group 2600 PA).
- **CF-C3** Login/logout structured event emit + envelope-adoption metric emit + Cat D whitelist-γ telemetry (→ Group 1700 Observability).
- **CF-C4** Mobile token revocation on logout (→ Group 2300 Mobile).
- **CF-C5** 15-surface storageKeys cleanup + R6 error-boundary framework (→ Group 2200 post-arc T-slot).
- **CF-C7** KillSwitch consumer attestation on logout (→ Group 1900 Authority; boundary preserved at HEAD).
- **CF-C8 NEW (Rigby SIGN cycle 1 Q11 STRENGTHEN fold)** Content/Publishing surfaces call auth-protected endpoints; inconsistent 401/envelope shapes can leak into editor/publisher UX (→ Group 1600 Content — consumer only, Cat C records contract variability).
- **T7 REST↔WS message-contract joint** (Cat C touches at typed-error-envelope; owned by Cat D + Group 2600 co-authorship).

## S2504 P4 Cat D queue (Permission-floor registry design-prep + REST↔WS T7 joint)

**Next child audit** per S2500 parent §5 child mission sequence Chris-locked "agree all" 2026-07-05:
- Mission: per-endpoint permission-floor registry (Cat B (c) LONG-TERM GOVERNANCE per S2499 CF-B1) + REST↔WS message contract strictness joint 2500+2600 (S2203 §17.3 T7 + S2202 §17 T6).
- Blast radius baseline: 1,864 URL routes + ~40 WS emit sites + 21-loci permission-floor rate (S2402 §14.5 baseline; RE-VERIFY at S2504 HEAD).
- Findings inheritance: S2499 CF-B1 per-endpoint permission registry Cat B (c) + S2203 §17.3 T7 REST↔WS parallel + S2202 §17 T6 message routing.
- Cross-arc coordination: Group 2400 (Cat B (c) matured into design-prep); Group 2600 PA (REST↔WS T7 joint owner + workspace-context authz).
- Playbook §11.2 20-section child-audit template TWENTY-THIRD-consecutive candidate.
- SIGN pin: TWENTY-FIRST-consecutive dedicated fresh SIGN pin candidate.

## Arc pin preservation

- **Arc pin `pa-a03b111768464b3f`** ACTIVE + PRESERVED through S2503 per playbook §16 arc-standard behavior. TWELFTH formal arc pin under Research OS. No retirement until S2599 xx99 close.
- **4 of 6 sessions shipped** in Group 2500 arc (S2500 parent + S2501 Cat A + S2502 Cat B + S2503 Cat C).
- Runtime target per parent §5: 6 sessions (S2500 + S2501-S2504 + S2599 xx99). 2 sessions remaining (S2504 Cat D + S2599 xx99 canonical summary).

## Deferred to post-commit docs cascade PR

Per S2502 close pattern (bundled cascade PR) — deferred:
- 4-step docs cascade: `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed` + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Chunk count reporting required in cascade PR body.
- ARCHITECTURE_INDEX.md §1.94 S2502 backfill + §1.95 S2503 registration + v89 → v92 version bump.
- OPEN_ARCS.md Group 2500 In-progress row "3 of 6 shipped" → "4 of 6 shipped" + NEXT = S2504 update.
- Anchor-update deferrals to S2599 xx99: `docs/topics/api.md` CREATE + PLATFORM_INVENTORY §API autoblock + PLATFORM_WHAT_IT_IS §API narrative subsection + `platform_architecture_inventory.md` §3.22 revise + ARCHITECTURE_INDEX §α/β/γ decision matrix pointer.

## Post-arc remediation queue (unchanged carry into S2504 execution scope)

Group 2400 S2499 §8.1 rank-1 co-equal P0 batch preservation preserved. Distribution across arcs unchanged; Group 2500 arc scope inherits P0-A + P0-B items for design-prep. Cat C now owned execution scope items per S2503 close:

- **F-D-CALL-1 803-scale silent-401 remediation** — Cat D S2504 primary owner (deferred).
- **F-D-BYPASS-1 79-raw-fetch bypass reconciliation** — Cat D S2504 post-arc T-slot classification.
- **F-D-ENVELOPE-1 typed-error-envelope** — **Cat C S2503 CLOSED as design-prep evidence-plane; execution deferred to xx99 verdict + post-arc PR.**
- **F-D-BOUNDARY-1 error-boundary framework** — dual-owned Cat C S2503 (typed-envelope prerequisite) + Group 2200 post-arc T-slot (global error UX contract). Coordination note added per Rigby Q13 fold.
- **F-D-SIDEBAR-1 Sidebar backend-token-revoke fix** — expected owner Cat D per Rigby Q9 fold; post-arc PR post-S2504.
- **F-C-REFRESH-1 refresh discipline decision-space** — **Cat C S2503 CLOSED as design-prep evidence-plane; execution coupled to R1 α/β/γ verdict.**
- **F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT** — 4-option evidence-candidates enumerated at §19.3 R11 with selection criteria; execution locus Chris-D-verdict at xx99 OR post-arc dedicated ADR.
- **F-C-CSD-1 Clear-Site-Data emission on logout** — **Cat C S2503 CLOSED as design-prep evidence-plane; execution deferred to xx99 verdict on locus + emission spec.**
- **F-C-STORE-1 15-surface × logout-cleanup declared contract** — **Cat C S2503 CLOSED as design-prep evidence-plane; execution CROSS-ARC coordination to Group 2200 post-arc T-slot + Group 2600 PA co-owner.**
- **F-D-WHITELIST-1 Whitelist replacement (Cat D α/β/γ × 2)** — Cat D S2504 primary owner (evidence-inheritance from S2404 §19.1 preserved).

## Session count status

- Group 2500 API arc OPEN at S2500 (4 of 6 sessions shipped: S2500 parent + S2501 Cat A + S2502 Cat B + S2503 Cat C).
- Group 2400 Auth arc CLOSED at S2499 (previous arc).
- TWENTY-SECOND-consecutive child-audit template application at S2503.
- TWELFTH formal arc pin ACTIVE + PRESERVED through S2503 (`pa-a03b111768464b3f`).
- TWENTIETH consecutive dedicated fresh SIGN pin retirement completed at S2503 Rigby SIGN cycle 1 close.

## Meta-methodology signals worth tracking to xx99

- 22-consecutive playbook §11.2 template application (MC-5 CODIFICATION-CONFIRMED-with-scope-guardrails candidate extension for xx99 review — codification claim CONDITIONAL per Rigby Q19 discipline preservation).
- 20-fold cycle-1 close per Cat C matches Cat B S2502 20-fold precedent — TWO-consecutive same-cycle-cadence at 20 folds (Cat B 20 + Cat C 20 = mirrors both content + cadence discipline).
- Rigby confidence trajectory in Group 2500: S2501 (Cat A) ~0.85 → S2502 (Cat B) ~0.85 → S2503 (Cat C) ~0.86 → monotonically stable-to-slightly-increasing. Matches Group 2400 arc trajectory pattern.
- Level 0 explicit-contract-missing anchor at §16 (Rigby Q17 fold) is a NEW xx99 decision-space handle not present in Cat A/B — evidence that Cat C's boundary evidence produces new xx99 decision axes without prescription.
