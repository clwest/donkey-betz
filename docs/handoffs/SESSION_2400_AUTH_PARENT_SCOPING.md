---
session: 2400
status: open (S2400 Group 2400 Auth (Session Lifecycle + Permission Floor + Silent-401 Resolution) arc-open at parent scoping doc CLOSED — playbook §11.1 20-section parent-scoping template TENTH application per S2299 canonical summary handoff line 100 statement (prior applications across arcs Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 per exemplar chain; Group 2400 = ELEVENTH formal arc under Research OS but §11.1 template TENTH application per prior arc's noted skip; specific §11.1 skipped-arc identification deferred to S2499 xx99 close if load-bearing per S2200 §playbook_application precedent); Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence via dedicated fresh SIGN pin `pa-32400781523b4d5b` retired at cycle close via `session_tool.retire`; single-batch × 4-Q parent-scoping-light-SIGN cadence per S1899 + S1999 + S2099 + S2199 + S2299 five-consecutive tested pattern — **SIXTH-consecutive same-cadence application at parent-scoping stage; MC-10 codification-ready extension candidate**; 4 folds landed pre-Chris-ratification — Q1 SIGN-with-edits (new §3.5 Auth-adjacent probes disposition 12-row table addressing token rotation / JWT vs opaque / CSRF / session fixation / rate limiting / audit logging / MFA / lockout / SSO / cookie defaults / password policy / impersonation → Cat A/B/C evidence or defer/N/A + cross-cutter posture guardrail) + Q2 SIGN-with-edits (§7.1 Cat B + Cat D leak-vector guardrails strengthened with MEASURE-CLASSIFY-RECOMMEND explicit framing + anti-pattern-to-avoid callouts + S2203 A3 ~40% untraced sample reference) + Q3 SIGN-with-edits (header acceptance criteria block augmented with per-criterion "_Measured by:_" clauses for #1-#6 to prevent Group 2500 registry-authoring drift + Group 2500 API contract SoT drift + Group 2200 R6 error-boundary framework drift) + Q4 SIGN-with-edits (§2 evidence-provenance disclaimer marking ~108 PUBLIC_PATHS + ~630 call-sites + 15 persistent-state surfaces + file:line anchors as ESTIMATE with per-Cat re-verification-at-HEAD requirement + one preserved SPECULATIVE flag cookie defaults); cycle 2 NOT required; Chris "agree all + commit it" 2026-07-05 ratified shape-card + drafted-doc wholesale; arc pin `pa-6279ead1714c4630` ACTIVE at S2400 open via `session_tool.create_fresh` — ELEVENTH formal arc pin under Research OS; ARCHITECTURE_INDEX v82 → v83 with §1.86 registration; OPEN_ARCS Group 2400 "pending" → "In-progress: S2400 parent scoping (2026-07-05)"; 00-START-NEXT-SESSION.md overwritten with S2401 P1 Cat A open priorities; tools/pa_local.sh:280 rotated + header ledger updated with S2200 retirement + S2400 open stanzas; Runtime target 6 sessions — **1 of 6 shipped**)
date: 2026-07-05
arc: Research Group 2400 (Auth — Session Lifecycle + Permission Floor + Silent-401 Resolution) — S2400 arc-open at parent scoping doc + arc-open cascade
head_commit_before: be56a17d (S2299 arc-close merge PR #2907)
head_commit_after: fe2d7624 (S2400 arc-open merge PR #2908)
arc_pin: pa-6279ead1714c4630 (ACTIVE at S2400 open via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline — ELEVENTH formal arc pin under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten; prior `pa-f7fd5016600f4513` retired at S2299 close — TENTH formal arc-pin retirement)
sign_pin: pa-32400781523b4d5b (RETIRED at S2400 parent-scoping SIGN cycle 1 close via `session_tool.retire` per playbook §15 SIGN-isolation discipline; updated_count=4, retired=true, previously_active=true — ELEVENTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 prior ten — 10 xx99 + 1 parent-scoping-light-SIGN)
---

# Session 2400 — Group 2400 Auth — Domain Scoping (Arc Open)

## What shipped

**Doc:** `docs/research/domains/auth/2400_auth_domain_scoping.md` (1229 lines post-Rigby-SIGN-4-folds; `status: active` post-Chris-"commit it"-2026-07-05 ratification).

**Playbook §11.1 20-section parent-scoping template TENTH application** per S2299 canonical summary handoff line 100 statement. Group 2400 = ELEVENTH formal arc under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten; §11.1 template TENTH application per prior arc's noted skip; specific §11.1 skipped-arc identification deferred to S2499 xx99 close if load-bearing per S2200 §playbook_application precedent.

**Rigby SIGN cycle 1 result: SIGN-with-edits at Medium-High confidence** via dedicated fresh SIGN isolation pin `pa-32400781523b4d5b` (minted at draft-complete via `session_tool.create_fresh` per playbook §15 SIGN-isolation discipline; retired at cycle close via `session_tool.retire`). Single-batch × 4-Q parent-scoping-light-SIGN cadence per S1899 + S1999 + S2099 + S2199 + S2299 five-consecutive tested pattern — **SIXTH-consecutive same-cadence application at parent-scoping stage; MC-10 codification-ready extension candidate**. **4 folds landed pre-Chris-ratification.** Cycle 2 NOT required per Rigby cycle-1 Medium-High confidence + all folds landable.

**4 SIGN folds by question:**

- **Q1 SIGN-with-edits** — new §3.5 Auth-adjacent probes disposition (12-row table): token rotation policy → Cat A + Cat C evidence; refresh token security posture → Cat C; JWT vs opaque tokens → Cat A + Cat C; CSRF discipline → Conditionally Cat C IF cookie-auth surface exists; session fixation defense → Cat C; rate limiting / brute-force → Inventory-only, defer post-arc; audit logging (auth events) → Inventory-only, Group 1700 Observability adjacent; password policy + reset flow → Non-candidate; MFA / TOTP / hardware token → Non-candidate (anti-scope #6 SSO/OAuth adjacent); impersonation / sudo mode → Non-candidate; account lockout / suspicious-activity blocks → Non-candidate; cookie SameSite / Secure / HttpOnly defaults → Cat C evidence. Plus cross-cutter posture guardrail preventing any child from surfacing an auth-adjacent probe finding beyond its disposition row.

- **Q2 SIGN-with-edits** — §7.1 Cat B + Cat D leak-vector guardrails strengthened. Cat B guardrail: measures (S2203 A3 sampled 20 endpoints ~40% permission-untraced rate extension across full ~1,864 `path()`) + classifies (per-endpoint permission-floor cell) + recommends (three-option decision space per S2203 §19.1 R2); does NOT design nor author registry (Group 2500 API scope). Explicit anti-pattern: Cat B produces "recommended permission-floor mapping table" reads as de-facto registry authoring → MUST land as decision-space evidence table with Chris-D-verdict-request instead. Cat D guardrail: measures (~630-of-~1,300 silent-401 call-site blast radius ESTIMATE inherited from S2203 A3 grep-based hedged for wrapper duplicates; Cat D re-verifies at HEAD) + classifies (per call-site money/governance/read/write) + recommends (three typed-error-envelope design candidates); does NOT execute envelope adoption at call sites (Group 2500 API + Group 2200 R6 error-boundary framework scope).

- **Q3 SIGN-with-edits** — header acceptance criteria block augmented with per-criterion "_Measured by:_" clauses: #1 permission-floor observability measured by Cat B endpoint-inventory matrix + permission-untraced-rate reduction; #2 failure surfacing measured by Cat D api.ts:48-56 audit + silent-401 call-site classification + typed-envelope candidate-design mapping; #3 logout cleanup contract measured by Cat C 15-surface storageKeys cleanup-table per surface + Zustand persist logout hygiene evidence; #4 session lifecycle discipline measured by Cat C session-model inventory + declared-refresh-posture evidence + Chris-D-verdict on silent-refresh vs explicit-re-login vs hybrid; #5 cross-arc coordination flags preserved measured by xx99 §5.4 cross-arc coordination flag count ≥ 2 (Group 2500 API + Group 2600 PA at minimum); #6 trust boundary inventory measured by Cat A trust-boundary registry existence + smoke-test coverage inventory (rate ≥ one-smoke-test-per-mechanism) + hard-runtime-gate vs soft-prompt-only vs permissive-fallback classification evidence.

- **Q4 SIGN-with-edits** — §2 evidence-provenance disclaimer added marking inherited numeric counts + file:line anchors as ESTIMATE: `~108 PUBLIC_PATHS` ESTIMATE per §3.27 platform_architecture_inventory (S1273 v2 review baseline), Cat A re-verifies at HEAD; `~630 of ~1,300 gated call-sites at silent-401 risk` ESTIMATE per S2203 A3 grep-based extraction hedged for wrapper duplicates, Cat D re-verifies at HEAD; `15 persistent-state surfaces (12 direct localStorage + 3 Zustand persist)` ESTIMATE per S2204 §14 F1 baseline at S2204 HEAD, Cat C re-verifies at S2403 HEAD in case new stores landed since S2204 close; file:line anchors (core/auth_middleware.py:563-681, .py:541-544 610-614, .py:548-556 615-623, core/services/fleet_auth_drf.py:65-150, core/vip_middleware.py:50-105, frontend/src/lib/api.ts:48-56) ESTIMATE per S1273 v2 review + S2203 §14 F3.5, Cat A + Cat D re-verify at HEAD line ranges (line-drift possible since S1273 review closed). One SPECULATIVE flag preserved: §2.3 "No cookie SameSite/Secure default declared in searchable form" — Cat C verifies at S2403.

**Chris "commit it" ratification 2026-07-05** on drafted parent scoping doc post-Rigby SIGN cycle 1 4 folds. Prior Chris "agree all" 2026-07-05 shape-card ratification (Q1-Q4 leans) locked pre-draft:

1. Q1 Option C 4-child taxonomy (STRONG both leans) — P1 Cat A Authentication+Trust Boundaries / P2 Cat B Authorization+Permission-Floor / P3 Cat C Session Lifecycle+Logout Cleanup / P4 Cat D Frontend Integration+Silent-401
2. Q2 Rigby-tightened central lens verbatim (drop "five surfaces" count + foreground failure-mode pivot)
3. Q3 6-criterion acceptance (5 start-here + Rigby "Trust boundary inventory explicit + testable" fold)
4. Q4 6-item anti-scope (5 start-here + Rigby "No new auth provider additions SSO/OAuth at parent scope" fold)

## Central lens question (§lens verbatim, Rigby SIGN-preview tightened wording)

*"Is the platform's auth model a contract (explicit trust boundaries + declared permission floors + declared session/refresh/logout semantics + consistent failure surfacing), or an accretion of per-surface defaults whose failures are silently swallowed (e.g., silent 401 / permissive fallbacks / ad-hoc public path lists)?"*

Canonical seam candidate: "defaults that silently swallow failure vs contracts that surface failure" — extends the S2299 Group 2200 frontend framing upstream through backend middleware + DRF permission classes + PA workspace context + Fleet HMAC boundary.

## Arc-open mechanics executed 2026-07-05

- `platform_config_tool overview` on retired Group 2200 arc pin `pa-f7fd5016600f4513` → confirmed `service_context: local`, `railway_environment: local`, `railway_service: local`, `database_name: unified_donkey_betz`, `default_llm_provider: openai`
- `session_tool.create_fresh` minted arc pin `pa-6279ead1714c4630` (ELEVENTH formal arc pin under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten)
- `tools/pa_local.sh:280` rotated from retired `pa-f7fd5016600f4513` to `pa-6279ead1714c4630`
- pa_local.sh header ledger updated with S2200 retirement stanza (Sessions 2200-2204 + S2299 arc summary; TENTH formal arc-pin retirement in Research OS) + S2400 open stanza (ELEVENTH formal arc pin under Research OS with full scope description)
- Pin ownership verified as chris via `session_tool whoami` — `conversation_owner_match=true` per `feedback_pa_local_verify_ownership.md`
- SIGN pin `pa-32400781523b4d5b` minted at draft-complete via `session_tool.create_fresh`; retired at cycle close via `session_tool.retire` (updated_count=4, retired=true, previously_active=true)

## MC-4 dial-back-resolution 5th confirming arc candidate

Group 2400 Auth 4-child structure extends MC-4 CODIFICATION-CONFIRMED across-4-consecutive-arcs (Groups 1900 + 2000+ + 2100 + 2200) to across-5-consecutive-arcs, resolving S2199 Q3 STRENGTHEN dial-back ("fully generalized" removal contingent on 5th arc or materially different stress condition) at S2499 close per §5.3 Group 2200 canonical summary. **Auth is materially different in scope** (full auth stack — authentication + authorization + session lifecycle + trust boundaries + frontend integration — not a single UI surface family), so the 5th-arc extension IS a stress test of MC-4's generality.

## Anchor updates landed this session

- **ARCHITECTURE_INDEX.md v82 → v83** — new §1.86 registered above §1.85 (S2299 canonical summary); frontmatter `last_verified` field bumped with full S2400 arc-open description; prior v82 preserved as narrative.
- **OPEN_ARCS.md** — Group 2400 row transitioned "pending — S2400 arc-open queued" → "S2400 parent scoping (2026-07-05) — Chris commit it ratified"; arc pin field populated with `pa-6279ead1714c4630` ACTIVE; SIGN pin retirement recorded; `last_updated` field bumped with full S2400 arc-open description.
- **00-START-NEXT-SESSION.md** — overwritten with S2401 P1 Cat A open priorities (Session Ready Check + scope + expected outputs + sub-agent dispatch shape + Rigby SIGN cadence).
- **tools/pa_local.sh** — line 280 rotated to `pa-6279ead1714c4630`; header ledger updated with S2200 retirement + S2400 open stanzas at appropriate insertion points per prior arc-open documentation pattern.
- **docs/research/domains/auth/** — new directory + parent scoping doc landed.

## Post-merge cascade artifacts (this handoff PR)

- `docs/INDEX.md` regenerated via `python manage.py build_docs_index` — 2928 docs indexed, 861,446 lines, status summary: active=1184 + draft=11 + superseded=1733
- `.rag/corpus.jsonl` regenerated via `python manage.py build_rag_corpus` — 32,328 chunks across 2928 files (chunk_size=1200; not tracked in git)
- Document + DocumentChunk tables synced via `python manage.py sync_docs_index_to_documents` — 1 created + 4 updated + 2923 skipped + 0 errors
- Unembedded documents embedded via `python manage.py embed_documents --all-unembedded` — 1 unembedded doc found (S2400 parent scoping doc itself); 106 chunks embedded via text-embedding-3-small
- `docs/_provenance.json` regenerated via `python manage.py build_docs_provenance` — 2378 docs indexed, HIGH=1560 / MEDIUM=351 / LOW=3 / UNKNOWN=464
- Chunk count evidence per `feedback_cascade_pr_must_include_embed_step` requirement: **106 chunks embedded for S2400 parent scoping doc** (verified against Document.chunk_count post-embed via `embed_documents --all-unembedded` output "Embedded: 106 chunks").

## Runtime target status

Group 2400 Auth: 1 of 6 sessions shipped
- **S2400 parent scoping** (this session) ✓
- S2401 P1 Cat A Authentication Surface + Trust Boundaries (NEXT)
- S2402 P2 Cat B Authorization + Permission-Floor Uniformity
- S2403 P3 Cat C Session Lifecycle + Logout Cleanup Contract
- S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC Resolution
- S2499 xx99 Canonical Summary + arc close

Runtime cap: 8 sessions. Never invoked in prior arcs.

## Next-session priority: S2401 P1 Cat A Authentication Surface + Trust Boundaries

**Scope (per S2400 §3.A):** Enumerate every authentication mechanism the platform runs (standard user token auth + ~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + FleetSignatureAuthentication HMAC + VIP demo prompt-only + service tokens PA_DB_HEALTH_RPC_TOKEN + PUBLIC_INTEL_TOKEN). For each: intended caller class + allowed routes + gate type (hard runtime vs soft prompt-only vs permissive fallback) + failure mode.

**Central question the audit answers.** *Does the platform have an explicit, enumerated trust-boundary inventory across every auth mechanism it runs, or has the authentication surface accreted via per-mechanism defaults without a single source-of-truth inventory?*

**Expected outputs (a) through (g)** per S2400 §3.A — auth mechanism inventory + trust boundary inventory + PUBLIC_PATHS ~108-entry audit + intent classification + VIP demo blast-radius quantification + Fleet permissive fallback quantification + service token audit + smoke-test coverage inventory (blocker to acceptance criterion #6).

**Rigby SIGN cycle 1 REQUIRED** per playbook §15 stage-scoped routing (child audit = required full SIGN via dedicated fresh isolation pin). Expected cadence: 4-batch × 5-Q = 20 total Q per S2201-S2204 five-consecutive tested child-audit pattern (not single-batch × 4-Q; that's parent-scoping-light-SIGN cadence). SIXTH-consecutive 20-Q cadence application candidate.

**Sub-agent dispatch** per playbook §13 six-parallel-agent shape — Agents 1-6 covering Models+Persistence / Services+RuntimeFlows / APIs+Tools+Tasks+Commands / Integrations+CrossDomain (Group 1900 boundary preservation) / Documentation+PriorResearch / Drift+Debt+Ownership+Maturity.

**S2401 open command (Chris short command):** `Continue research group 2400: P1 Cat A` or `Continue research group 2400: authentication surface` or equivalent invocation.
