---
title: "SESSION 3010 — T-ENVELOPE-2-DEPRECATION Batch 4 complete + Fold E RateLimiting migrated + 2 Rigby Tool Gap Ledger entries"
session: 3010
date: 2026-07-28
type: three_pr_plus_ledger_close
merge_shas:
  - "2cfa01561"   # PR #3694 — Fold E RateLimiting 429 → helper
  - "cd65a3931"   # PR #3695 — Batch 4a PR A: 16 auth-surface sites
  - "c7e0fbc71"   # PR #3696 — Batch 4b PR B: 46 platform-CRUD sites
prs:
  - 3694
  - 3695
  - 3696
ledger_deliverables:
  - "f4e8481f-ac80-477d-b5dd-9f291a21f245"   # Rigby Tool Gap — LLM-side hallucination on file-level code claim (S3009 Fold A)
  - "e6e7fd6d-0f8a-4ba9-8ecb-879612ea779c"   # Rigby Tool Gap — shell-exec surface gap for read-only verification (S3009 Fold C)
related_arcs:
  - "ADR-0007 Layered Envelope Policy (ratified S3005)"
  - "I-0301 Failure-Data Safety Contract (Family E authorizing substrate)"
consumes:
  - "S3009 close cascade — joint recommendation C+B1+A executed as-recommended"
  - "S3009 Fold A/C — ledger entries minted this session"
  - "S3007 Fold E — RateLimiting 429 migration (3rd carry-forward through S3008/S3009/S3010)"
  - "ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION — Batch 4 (final of 5 files) + Fold E"
---

# S3010 — T-ENVELOPE-2-DEPRECATION Batch 4 complete + Fold E RateLimiting migrated + 2 Rigby Tool Gap Ledger entries

**Status:** CLOSED. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now at 5-of-5 files migrated** (Batches 1+2+3+4 + Fold E all shipped). Only remaining scope: 3 `gumroad_webhook` JsonResponse sites deferred to S3011 (Chris-ratified pending Gumroad body-shape sensitivity check) + `api_helpers.py` disposition arc (separate substrate). 3 feature PRs merged + 2 Rigby Tool Gap Ledger entries minted. HEAD `c7e0fbc71`.

## Session shape

Three-PR sequential close following the S3009 joint recommendation shape (C+B1+A). Executed as recommended:
1. **C** (Task C) — 2 Rigby Tool Gap Ledger entries minted in workspace `b4503364-2573-4401-9e28-61a739e0ce50` via `deliverable_tool.create`. Post-create ORM fix applied per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` (set `deliverable_type='engineering_backlog'`, cleared diagnostic_status + diagnostic_code).
2. **B1** (Fold E) — RateLimitingMiddleware 429 dict → helper. Rigby A2 SIGN AGREE 5/5. Merged, restarted, programmatic smoke (middleware is commented-out in settings — hit via RequestFactory).
3. **A** (Batch 4) — 2-PR split ratified by Chris via Rigby. PR A shipped first (16 auth-surface sites), full A2 SIGN + merge + restart + 3-site smoke. PR B shipped next (46 platform-CRUD sites + file added to MIGRATED_FILES), full A2 SIGN + merge + restart + 3-site smoke with behavior-change verification.

**7th consecutive continuous S-cascade** (S3004→S3010; see Fold D). One Chris message mid-session ("Let's defer gumroad") confirmed the Rigby-proxied Q1 decision; one Chris idea recorded (ebook from /docs/ — see `project_ebook_from_docs_folder`).

## PR #3694 (`2cfa01561`) — Fold E: RateLimitingMiddleware 429 → emit_error_envelope() helper

**Scope (1 file, +10 / -9 = +1 net):** Converted the last raw `JsonResponse({'success': False, 'error': {'code': 'rate_limited'...}}, status=429)` pattern in `core/auth_middleware.py` (RateLimitingMiddleware.process_request at L935) to `emit_error_envelope(reason_code='rate_limited', request=request, hint={...}, retry_after_seconds=window)`. Carry-forward since S3007 (3rd session on the queue). Trivial with the S3008 helper.

After this PR: `core/auth_middleware.py` fully helper-based across all 11 emit sites (10 from S3009 B1 + 1 from this PR). No raw envelope patterns remain. `JsonResponse` import dropped (0 callers).

**Hint dict:** `source: 'rate_limit_exceeded'`, `endpoint`, `client_ip`, `limit`, `window_seconds`. Pre-emit f-string log preserved (`Rate limit exceeded for {client_ip} on {endpoint}`).

**Behavior surface (Rigby A2 D4):** HTTP `Retry-After` header is NOT set by the helper — only the envelope body's `retry_after_seconds` field. Pre-existing behavior (raw JsonResponse also didn't set the header). Header-vs-body split is a candidate future Fold if a 429-consuming client keys on the header.

**Rigby A2 SIGN (task ~14:03 UTC):** AGREE 5/5 with tool-grounded verification of helper signature, `retry_after_seconds` gating logic at `error_envelope.py:107-112`, import cleanup, and behavior parity. Zoom-out: 4 AGREE + 2 non-blocking follow-ups (Retry-After header, "fully migrated" tracking category).

**Live-smoke (post make restart):** RateLimitingMiddleware is commented-out in `core/settings.py:279`, so live curl to `/api/v1/auth/login/` 6× rapid-fire didn't trigger 429 (middleware never runs). Programmatic smoke via `RequestFactory` + `mw.process_request(req)` for 6 iterations: attempts 1-5 = `None` (accumulating cache), attempt 6 = **HTTP 429 + Family E envelope + support_code RUR-RATE-260728-b286 + retry_after_seconds=300 in body + terminal_state=RATE_LIMITED**. Pre-emit f-string log emitted from `auth_middleware`; structured helper log from `error_envelope`. Emit path fully verified.

## PR #3695 (`cd65a3931`) — Batch 4a PR A: 16 auth-surface sites

**Scope (1 file, +105 / -19 = +86 net):** First half of Batch 4 (2-PR split per Rigby A1 SIGN + Chris ratification). Migrated 16 sites across `oauth_connect` (3) + `oauth_callback` (7) + `refresh_token` (6) in `core/views_platform_integrations.py`. Highest-sensitivity surface (auth flow) isolated for smaller blast radius.

**Reason-code taxonomy:** 4× not_authenticated, 3× invalid_input, 1× validation_error, 4× internal_error, 2× upstream_provider_error, 3× unavailable.

**9 behavior-change status shifts in PR A:** 400→503×3, 400→502×2, 400→500×3, 400→404×1, 400→401×1. All semantic upgrades (401 for re-auth, 500 for uncaught exceptions, 502 for upstream, 503 for feature unavailability). Documented explicitly in PR description.

**Safety upgrade:** L336 (`oauth_unhandled_exception`) + L499 (`refresh_unhandled_exception`) previously returned raw `f"...{str(e)}"` in user-facing body. Under Family E, `str(e)` never reaches the user; only `exc_type` (safe class name) appears in operator-side hint dict.

**Import strategy correction (Rigby A1 D5):** initial attempt dropped `api_error` from imports at the PR-A phase, which broke 46 remaining sites at `NameError` runtime. Reverted: `api_error` RETAINED in PR A with inline comment `# api_error retained pending PR B (46 remaining sites)`. Django check confirmed. **Class-lesson: PR-split migrations must keep the deprecated import until final PR drops it.**

**Rigby A2 SIGN (task ~14:18 UTC):** AGREE 5/5 with tool-grounded verification of 6 spot-check sites (line citations for reason_code + hint dict shape). Zoom-out: 4 AGREE + 1 nice-to-have (module-level PR-A-of-B split comment).

**Live-smoke (post make restart) — 3 sites verified:**
- `oauth_connect` unauthed → HTTP 401 + Family E + `RUR-AUTH-260728-4fd0`
- `oauth_connect` session-auth w/ unsupported platform → HTTP 400 + `invalid_input` + hint verbatim (`platform: 'nonexistent'`)
- `refresh_token` unauthed → HTTP 401 + `RUR-AUTH-260728-8165`

## PR #3696 (`c7e0fbc71`) — Batch 4b PR B: 46 platform-CRUD sites + MIGRATED_FILES = 5

**Scope (2 files, +297 / -49 = +248 net):** Second half of Batch 4. Migrated 46 platform-CRUD sites across 9 endpoints: `etsy_get_shop` (5) + `etsy_create_listing` (7) + `shutterstock_get_portfolio` (5) + `shutterstock_submit_content` (4) + `gumroad_get_products` (5) + `gumroad_create_product` (7) + `gumroad_publish_image` (7) + `sync_platform_revenue` (4) + `disconnect_platform` (2).

**Combined with PR A: file at 62/62 sites migrated in Family B scope.**

**Lint gate:** `core/views_platform_integrations.py` added to `MIGRATED_FILES` tuple (**4 → 5** tracked files). All 5 T-ENVELOPE-2-DEPRECATION files now zero-tolerance lint-locked:
1. `views_odds_sports.py` (Batch 1)
2. `views_revenue_analytics.py` (Batch 1)
3. `auth_middleware.py` (Batch 2 + S3009 B1 + S3010 Fold E)
4. `views_auto_distribution.py` (Batch 3)
5. `views_platform_integrations.py` (Batch 4)

**24 behavior-change status shifts in PR B:** 400→404×10 (all "no active X account" + image_not_found), 400→500×8 (uncaught exception fallbacks + platform_missing_in_db), 400→502×5 (upstream X API errors), 400→503×1 (revenue_sync_not_implemented). **Combined Batch 4 total: 33 shifts** (PR A 9 + PR B 24). All auto-inferred from `ReasonCode.typical_status`.

**Safety upgrades (8 exception-fallback sites):** All `f"Failed to X: {str(e)}"` patterns replaced. Hint contains `exc_type: type(e).__name__` only — never `str(e)` in user-facing body. `gumroad_publish_image` ValueError catch (L1309) also includes `exc_msg=str(e)` in operator hint (safe: hint stays server-side per Family E contract).

**Import cleanup:** `api_error` dropped from imports (was retained during PR A). `api_success` kept. `JsonResponse` **retained** for deferred `gumroad_webhook` (3 sites, S3011 scope).

**Rigby A2 SIGN (task ~14:28 UTC):** AGREE D1/D2/D4/D5 with 8 spot-checks tool-grounded. PARTIAL D3 (didn't inspect lint script — offered to re-verify if asked; declined as non-blocking since D5 confirmed 0 api_error matches). Zoom-out: 4 non-blocking observations + JsonResponse-lint suggestion (future work).

**Live-smoke (post make restart) — 3 sites with behavior-change verification:**
- `etsy_get_shop` unauthed → HTTP 401 + `RUR-AUTH-260728-ec9c`
- `gumroad_get_products` session-auth (no gumroad account) → **HTTP 404** (400→404 shift verified!) + `RUR-MISSING-260728-ded1` + hint verbatim (`no_active_account`, `platform: 'gumroad'`)
- `sync_platform_revenue` for `shutterstock` (test account created via ORM to bypass 404) → **HTTP 503** (400→503 shift verified!) + `RUR-INTERNAL-260728-cbd5` + hint (`not_implemented`, `platform: 'shutterstock'`)

## Rigby Tool Gap Ledger entries minted (Task C)

Both entries in workspace `b4503364-2573-4401-9e28-61a739e0ce50` (`deliverable_type='engineering_backlog'`, `category='engineering_backlog'`, diagnostic fields cleared).

- **Entry 1** (`f4e8481f-ac80-477d-b5dd-9f291a21f245`) — "Rigby Tool Gap — LLM-side hallucination on file-level code claim (S3009 Fold A 1st trigger)". Body documents the S3009 A2 D3 spurious DISAGREE pattern, 3-channel Claude verification mitigation, proposed extension to `feedback_verify_rigby_tool_runs_before_trusting_sign`, and threshold (1 trigger, watch for 2nd).
- **Entry 2** (`e6e7fd6d-0f8a-4ba9-8ecb-879612ea779c`) — "Rigby Tool Gap — shell-exec surface gap for read-only verification (S3009 Fold C 1st trigger)". Body documents the D5-PARTIAL pattern, proposed `repo_tool.run_command` capability with read-only whitelist, and consolidation candidate with S3008 Fold B (repo_tool.search no total_matches).

Post-create ORM fix applied per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` — Rigby's `deliverable_tool.create` initially set `diagnostic_status='diagnostic'` + `diagnostic_code='missing_initiative_id'` (hides from UI). Fixed via `python manage.py shell` ORM update setting `deliverable_type='engineering_backlog'` and clearing diagnostic fields. Both entries now UI-visible.

## Folds

### Fold A — 7th consecutive continuous S-cascade (**class distinction: full-arc-completion**)

S3004→S3005→...→S3009→S3010 = 7 continuous cascades. S3010 completes the T-ENVELOPE-2-DEPRECATION arc at the 5-file-migration level (Batch 5 = api_helpers.py disposition remains as separate substrate arc). Sub-shape: "arc-completion in continuous-cascade context" — the arc originated at S3005 (ADR-0007 ratification) and closed at S3010 (5th file migrated).

**Observation stays on the queue.** Watch for cascade-class break at S3011.

### Fold B — Middleware/view restart discipline (**4th trigger — Playbook amendment threshold clearly met**)

S3007 = 1st trigger, S3008 = 2nd, S3009 = 3rd, **S3010 = 4th** (3 PRs all required and correctly used `make restart` from outset). Pattern is stable and repeatable. Extending `feedback_recycle_after_merge` into a formal PLAYBOOK-7.4.5 rule is now well-motivated by empirical trigger accumulation.

**Deferral rationale:** the existing memory rule already contains the guidance. Formal amendment can happen in a dedicated Playbook amendment session or as an S3011 secondary directive. Not urgent, but well-warranted.

### Fold C — Rigby A2 SIGN quality stayed clean (**no repeat of S3009 Fold A pattern**)

S3009 Fold A = 1st trigger for LLM-side hallucination on file-level code claim. **S3010: 3 A2 SIGN cycles across 3 PRs, ZERO hallucination triggers.** Rigby correctly quoted line citations, correctly attributed D3 PARTIAL to scope-of-inspection (not code defect), correctly identified gumroad_webhook out-of-scope on PR B D4.

**Threshold status:** 1 trigger (S3009). No 2nd trigger this session. Watch for 2nd trigger before formalizing into Playbook amendment.

### Fold D — Import-cleanup discipline during PR-split migrations (**new pattern, 1st trigger**)

**Trigger:** S3010 PR A initially dropped `api_error` from imports, breaking 46 remaining sites at NameError runtime. Reverted mid-session with inline comment `# api_error retained pending PR B (46 remaining sites)`. Rigby A2 D5 correction (D5 called out that JsonResponse import cannot drop because gumroad_webhook still uses it) validated the pattern generally.

**Rule candidate:** "PR-split migrations MUST retain deprecated imports until the final PR drops them. Any PR that partially migrates a file must include an inline import-line comment naming the follow-up PR that will complete the migration."

**Ledger operational status:** 1 trigger. Watch for 2nd trigger. Similar to Fold C (S3009 middleware-restart pattern) — one-off caught mid-session, forward-carry the general rule.

### Fold E — Rigby JsonResponse-lint suggestion (**future tooling, not yet actionable**)

From Rigby A2 SIGN on PR B Z1(b): "The lint doesn't cover JsonResponse. Reviewers could over-assume [that MIGRATED_FILES protects against str(e) leaks in raw JsonResponse patterns]. A follow-up lint check like 'no JsonResponse error bodies containing str(e)' could be worthwhile."

**Applicability:** Would catch the `gumroad_webhook` L1435 `str(e)` leak (currently the only known instance in the codebase). A small tooling PR (~30 min). Candidate for S3011 or bundled with gumroad_webhook migration.

## Forward carries (open at S3010 close)

### New from S3010

- **Fold A `7th continuous cascade`** — observation stays; watch for cascade-class break.
- **Fold B `4th trigger` (middleware/view restart discipline)** — Playbook amendment strongly motivated. Priority carry-forward.
- **Fold C `stayed at 1st trigger` (Rigby LLM-side hallucination)** — no repeat this session; watch for 2nd trigger before amendment.
- **Fold D `1st trigger` (PR-split import-cleanup discipline)** — new pattern. Watch for 2nd trigger.
- **Fold E** — JsonResponse-str(e) lint check candidate. Small tooling PR at S3011.
- **HTTP Retry-After header** — Rigby A2 Z1(c) on Fold E PR. Follow-up Fold for future — add header from within emit_error_envelope for RATE_LIMITED reason codes.

### T-ENVELOPE-2-DEPRECATION queue after S3010

**Essentially complete.** Remaining scope:

- **gumroad_webhook migration** (3 sites in `core/views_platform_integrations.py` L1418/L1428/L1435): needs verification of Gumroad webhook body-shape sensitivity first. External-consumer contract; body-parse risk unknown. Chris-ratified DEFER at S3010 open. ~1hr PR when scheduled.
- **api_helpers.py disposition arc**: retire vs keep-with-deprecation-warning. Separate substrate arc. Not urgent.

Both are minor scope. The arc's engineering substrate is complete.

### Carried from S3009 (RESOLVED this session)

- **Fold A `1st trigger`** — Rigby LLM-side hallucination on file-level code claim. **Ledger entry minted:** `f4e8481f-ac80-477d-b5dd-9f291a21f245`. No 2nd trigger yet.
- **Fold C `1st trigger`** — Rigby shell-exec tool-surface gap. **Ledger entry minted:** `e6e7fd6d-0f8a-4ba9-8ecb-879612ea779c`. Watch for 2nd trigger.
- **Fold E `future_trigger`** (RateLimiting 429) — **RESOLVED at S3010 as PR #3694.**
- **Fold B `1st trigger`** (repo_tool.search no total_matches from S3008) — still open. Bundle candidate with Fold C ledger entry for repo_tool capability expansion arc.

### Carried from earlier sessions

_(All S3005-S2989 items unchanged this session — see S3009 handoff §Forward carries for the complete inherited list.)_

## HEAD at close

- Fold E merge: `2cfa01561` (PR #3694)
- Batch 4a PR A merge: `cd65a3931` (PR #3695)
- Batch 4b PR B merge: `c7e0fbc71` (PR #3696)
- Close cascade PR (this file + 00-START refresh + INDEX regen + wrapper pin bump + orphan INDEX from S3009): TBD

## Cross-cutting workflow references

- **Constitutional governance:** Playbook v0.10.0. No amendments this session. **Fold B (4th trigger)** is the strongest amendment candidate for a v0.10.1 PATCH or v0.11.0 MINOR extending Ch 7 §7.4 middleware/view restart discipline.
- **ADR corpus:** ADR-0001 through ADR-0007. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now at 5-of-5 files migrated** (all Batches 1+2+3+4 + Fold E shipped). Only `gumroad_webhook` (3 sites) + `api_helpers.py` disposition remain as trailing scope items.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **3× Flow B spec→ship this session** (Fold E: pre-ratified spec straight to A2; Batch 4a PR A: A1→implement→A2; Batch 4b PR B: A1-inherited→implement→A2). Plus 1× Rigby-only task (C ledger entries, no A1 needed since content was pre-drafted by Claude).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **4× substantive Rigby SIGN cycles this session** (Fold E A2 + Batch 4 A1 + PR A A2 + PR B A2). All tool-grounded with line citations. Zero DISAGREE across all 4 cycles (D5 PARTIAL on PR B was scope-of-inspection, not code defect). Substantive per rule.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 2 mid-flight decision surfaces (gumroad_webhook scope + PR split shape) — both routed via Rigby with plain-english framing (do we lose anything? / more work later?). Rigby proxied as Chris; Chris subsequently confirmed DEFER on gumroad. Full decision loop closed.
- **Recycle discipline:** middleware/view diff → `make restart` used correctly on all 3 PRs from outset. **Fold B 4th trigger.**
