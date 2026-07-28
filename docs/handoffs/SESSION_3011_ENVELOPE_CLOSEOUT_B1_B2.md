---
title: "SESSION 3011 — T-ENVELOPE-2-DEPRECATION close-out (B1 gumroad_webhook + B2 str(e) lint) — B3 rescoped as T-ENVELOPE-3"
session: 3011
date: 2026-07-28
type: two_pr_close_plus_arc_rescope
merge_shas:
  - "96326c20e"   # PR #3698 — B1 gumroad_webhook 3 error sites → emit_error_envelope helper
  - "6a1d8645a"   # PR #3699 — B2 AST-based str(e) body-leak lint + grandfather list
prs:
  - 3698
  - 3699
new_arcs_opened:
  - "T-ENVELOPE-3 — retire api_helpers.py Family B (api_error/api_success) across ~90 caller sites in 4 primary files + 6 minor sites"
related_arcs:
  - "ADR-0007 §4.3 Layered Envelope Policy (T-ENVELOPE-2-DEPRECATION — CLOSED this session)"
consumes:
  - "S3010 00-START Option B1 (gumroad_webhook migration, deferred pending body-shape check)"
  - "S3010 Fold E A2 Z1(b) — str(e) lint expansion suggestion"
  - "S3010 forward-carry — trailing scope api_helpers.py disposition"
---

# S3011 — T-ENVELOPE-2-DEPRECATION close-out + T-ENVELOPE-3 arc opened

**Status:** CLOSED. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION arc is now fully complete** — all 62 sites in `core/views_platform_integrations.py` migrated (including the 3 previously-deferred `gumroad_webhook` sites) + new AST-based str(e) body-leak lint gate ships with 32 grandfathered debt sites cataloged. Chris ratified Option B (B1 + B2) then Option F for B3 (defer full retirement to T-ENVELOPE-3 next session). 2 feature PRs merged. HEAD `6a1d8645a`.

## Session shape

Two-PR sequential close following S3011 00-START Option B (recommended if Chris wants engineering completeness on the arc):
1. **B1** — `gumroad_webhook` 3 error sites (L1382, L1389, L1435) migrated to `emit_error_envelope()`. str(e) leak at L1435 removed as safety upgrade. Success paths (L1418/L1428) preserved as raw JsonResponse per ADR-0007 §4.3 scope.
2. **B2** — `scripts/lint_no_deprecated_family_b.py` extended with AST-based str(e) body-leak detector + `STR_E_LEAK_GRANDFATHER` frozenset (32 pre-existing DRF Response leaks in `core/views_odds_sports.py` cataloged) + `--regenerate-grandfather` flag.

Third PR (B3 — api_helpers.py disposition) audit surfaced ~90 caller sites across 4 primary files. Chris re-scoped as T-ENVELOPE-3 successor arc for S3012 open per Option F (close-clean on B1+B2 wins).

**8th consecutive continuous S-cascade** (S3004→S3011). Two mid-session Chris interactions: (1) approve Option B for B1+B2; (2) workflow correction on wall-clock time estimation (see Fold C).

## PR #3698 (`96326c20e`) — B1: gumroad_webhook 3 error sites → emit_error_envelope() helper

**Scope (1 file, +23 -3):** Three raw `JsonResponse({'status': 'error', 'message': ...}, status=4XX/500)` sites in `core/views_platform_integrations.py::gumroad_webhook` migrated to `emit_error_envelope(reason_code=..., request=request, hint={...})`.

- **L1382** (`json.JSONDecodeError` after form-data fallback fails) → `invalid_input` (400→400) with `hint={source, reason='json_decode_failed'}`.
- **L1393** (missing `product_id`) → `invalid_input` (400→400) with `hint={source, reason='missing_field', field='product_id'}`.
- **L1447** (unhandled `Exception`) → `internal_error` (500→500) with `hint={source, reason='unhandled_exception', exc_type=type(e).__name__}`. **Safety upgrade:** raw `str(e)` no longer leaks to user-facing body (matches L1499 pattern for `sync_platform_revenue`).

Success paths (L1430 Sale recorded / L1440 Product not tracked) preserved as raw JsonResponse per ADR-0007 §4.3 error-only scope. `JsonResponse` import at L30 retained.

**Gumroad body-shape verdict:** Public docs behind auth walls (WebFetch could not verify). Defaulted to standard webhook convention: Gumroad Ping consumes HTTP status only for retry semantics. Justified by view docstring ("Gumroad sends form data (not JSON)") + implementation uses `request.POST.dict()` first — Gumroad does not expect structured JSON response. Status codes preserved (400/400/500 unchanged) → retry semantics safe (4xx=no-retry, 5xx=retry).

**Rigby A1 SIGN:** 3 STRENGTHEN + 2 AGREE, 5 tool_runs. Adopted all: hint reason `no_data_received` → `json_decode_failed`; exception smoke uses `price='not_an_int'` (int() runs before product_id guard per L1384-1386); sequential vs bundled shape (this PR unbundled from B2 lint expansion — webhook is sensitive integration surface, keep blast radius small). Zoom-out: don't try to "improve semantics" (e.g., flipping invalid_input to 200 to stop retries) — keep purely "envelope + no leaks."

**Rigby A2 SIGN:** 4 AGREE + 1 STRENGTHEN (post-merge live curl smoke per Z1 to catch "wrong process restarted" issues), 2 tool_runs. Ready-to-ship verdict.

**Smoke evidence (all PASS):**
- RequestFactory: 3 sites × PASS with support codes RUR-INPUT-260728-7af3, RUR-INPUT-260728-28ff, RUR-INTERNAL-260728-d807.
- Live curl post-`make restart`: 3 sites × PASS with FRESH support codes (74d2, 7905, a08c) — proves merge landed + restart picked up new code.
- str(e) leak verified in operator log ONLY (`invalid literal for int() with base 10: 'not_an_int'` via `logger.exception`), NOT in user body (only human_message + support_code + reason_code + retryable + terminal_state + timestamp).

**Fold B 4th trigger:** `make restart` used correctly post-merge (Daphne request path).

## PR #3699 (`6a1d8645a`) — B2: AST-based str(e) body-leak lint + grandfather list

**Scope (1 file, +174 -4):** Extended `scripts/lint_no_deprecated_family_b.py` with a second file-scoped zero-tolerance rule per Rigby S3010 Fold E A2 Z1(b).

**Detector (AST-based):**
- Walks each `MIGRATED_FILE`, locates `ast.Return` where value is `ast.Call`.
- Matches function name `JsonResponse` or `Response` (excludes logger calls by construction — only scans return statements).
- Walks call args via `ast.walk`; flags any nested node that is:
  - `str(e)` with bare `Name(id='e')` (via `_is_str_of_e`)
  - `ast.JoinedStr` (f-string) containing `ast.FormattedValue` with `Name(id='e')` or `_is_str_of_e` expression
- Uses `node.lineno` from the return statement (start line of call, not textual leak line — consistent across regenerate + check paths).

**Grandfather set (`STR_E_LEAK_GRANDFATHER`):** 32 pre-existing leak sites in `core/views_odds_sports.py` cataloged as `frozenset[tuple[str, int]]`. This file entered MIGRATED_FILES at S3006 Batch 1 (Family B helper migration) but DRF `Response` error paths were not in that scope — B2 discovery surfaces them as tech debt for follow-up ("sports odds leak drain" arc per Rigby A1 Z1). Other 4 MIGRATED_FILES are clean (0 grandfathered).

**Ratchet mechanism:**
- `--regenerate-grandfather` prints copy-paste-ready frozenset from current scan (recovers from line-number churn).
- Stale grandfather entries (leak fixed but not removed from set) trigger "safe to remove" hint at exit 0 (doesn't fail lint — just informs).

**Rigby A1 SIGN (audit-driven scope discovery):** After I grepped MIGRATED_FILES and found the ~32 DRF Response leaks, presented 4 shape options. Rigby DECIDE Shape 4 (grandfather list, Response+JsonResponse coverage), 3 STRENGTHENs (AST over regex; grandfather by (path,lineno) with regenerate flag; exclude logger calls). 4 tool_runs. Chris-routing within Rigby authority since lint-only + catalog + no behavioral changes.

**Rigby A2 SIGN:** 3 AGREE + 1 STRENGTHEN P1-minor (guidance text said `build_user_facing_envelope` but should say `emit_error_envelope` which is the actual helper used in migrated code). 2 tool_runs. Deferrable: grandfather growth risk acceptable (stale-detection + regenerate flag = ratchet mechanism).

**Test evidence (6/6 PASS):**
1. Baseline: `✅ ADR-0007 Family B deprecation lint OK (5 files checked, 32 grandfathered str(e) leaks)`
2. `--list`: unchanged behavior
3. `--regenerate-grandfather`: copy-paste-ready output with per-file counts
4. Injected fake new leak (`JsonResponse({'error': str(e)})` in `views_auto_distribution.py`): exit 1 + correct guidance ("replace with `emit_error_envelope(...)`")
5. Fixed grandfathered leak (L924 mutated): exit 0 + "1 stale grandfather entries (safe to remove)" hint listing `core/views_odds_sports.py:924`
6. Python syntax: OK

**Fold B not applicable:** lint-only tooling; nothing on Daphne request path. `make celery-recycle` or no-op post-merge.

## B3 audit findings (informs T-ENVELOPE-3 arc)

### api_helpers.py current state
81 lines, contains:
- `smart_truncate()` (L12-60) — text utility, INDEPENDENT of envelope arc (11 file callers, all safe — do NOT touch).
- `api_success(data, message, status=200)` (L63-70) — success helper, raw JsonResponse.
- `api_error(message, status=400, errors=None)` (L73-81) — error helper, Family B.

**Correction to S3011 00-START:** doc stated helpers have "deprecation docstrings." They do NOT. No deprecation markers anywhere in `api_helpers.py`.

### Family B caller count (outside 5 migrated + api_helpers/api_responses + migrations)

| File | Sites |
|------|-------|
| `core/views_ab_testing.py` | 37 |
| `core/views_learning_loop.py` | 25 |
| `core/views_rag_observability.py` | 13 |
| `core/tasks_conversations.py` | 11 |
| 6 minor files (tests, LLM wrappers, models) | 1-2 each |
| **Total** | **~90 sites** |

`APIResponseEnvelope.error / .unauthorized / etc.` usage OUTSIDE `api_responses.py`: **0 sites**. Clean.

### Existing bug discovered (T-ENVELOPE-3 bundle candidate)

`core/views_rag_observability.py` has ~7 sites (L43/L68/L98/L127/L155/L182/L210/L239/L293) using `status_code=401`/`status_code=500`/`status_code=403` kwargs. `api_helpers.api_error` signature accepts `status=`, NOT `status_code=`. Any actual call would raise `TypeError: api_error() got an unexpected keyword argument 'status_code'`.

Two possibilities: (a) these code paths are dead / never exercised, (b) some other `api_error` is being imported — but grep confirms only `core.api_helpers.api_error` is in scope. So (a): dead-code sites, OR they've been broken since inception.

**Chris ratification:** bundle bug fix into the `views_rag_observability.py` T-ENVELOPE-3 migration PR (`s/status_code/status/g` + envelope migration in one diff). Cleaner than a separate one-off correctness PR.

## Folds

### Fold A — S3010 00-START line-number drift (1st trigger, informational)

**Trigger:** S3010 00-START-NEXT-SESSION.md listed gumroad_webhook sites as "L1418/L1428/L1435" but L1418/L1428 are actually SUCCESS paths (status 200) outside ADR-0007 §4.3 error-only scope. Actual error sites are L1382/L1389/L1435.

**Root cause:** Line numbers in cross-session forward-carry docs stale between session close and next-session file reads. Common when the source file is actively edited between sessions.

**Mitigation applied:** S3011 A1 SIGN spec explicitly corrected the line numbers and provided proposed migration code inline. Rigby A1 verified via `repo_tool.read_file` (5 tool_runs).

**Rule extraction potential:** Not yet — 1st trigger, informational. Watch for 2nd. If it becomes a pattern, candidate `feedback_00_start_line_numbers_stale` rule (do line-number lookups fresh at session open, don't trust doc-stored linenos).

**Classification per PLAYBOOK-6.10.8:** `same_pr_mitigatable` — mitigated at S3011 A1 spec drafting; no ship-blocking impact.

### Fold B — Fold B 4th trigger continues (`middleware/view diff → make restart`)

**Trigger:** PR #3698 (gumroad_webhook migration) is Django view served on Daphne request path — required `make restart` post-merge. B1 executed correctly. 4th continuous trigger since S3007.

**Status:** Fold B at 4 triggers → PLAYBOOK-7.4.5 amendment is the strongest v0.10.1 PATCH candidate. Rule text draft: "Any change to files loaded by Daphne request path (middleware / views / URLs / settings / installed_apps) requires `make restart` or `make recycle-all`, NOT `make celery-recycle` alone."

**Action for S3012+:** Option A candidate for next session ratification (~1 hr Playbook amendment). Alternatively bundle into T-ENVELOPE-3 close cascade.

### Fold C — Wall-clock time estimation inflation (1st trigger, corrective)

**Trigger:** In B3 A1 SIGN dispatch, Claude estimated Option A (full retirement) at "~4-5 hrs minimum" — using human-effort framing. Chris mid-session message: *"Remember when you look at work don't use wall clock for time, you are writing all of the code and you have Rigby that's looking at the repo using tools along with you so you guys should be able to work a lot faster."*

**Root cause:** Claude scope estimates were 5-10x inflated because framed as human-developer wall-clock time rather than Claude+Rigby machine-speed cooperation. A 90-site 4-file migration at Batch 4a/4b sequential-PR cadence is ~45-90 min of session work, not ~4-5 hrs.

**Mitigation applied:** Re-scoped B3 with corrected estimate (~45-90 min for full retirement). Chris re-evaluated and chose Option F (defer to T-ENVELOPE-3) on the basis of session-scope-fit (already 2 PRs deep + close cascade pending), not effort cost.

**Rule extraction potential:** Watch for 2nd trigger. If Claude scope estimates continue to be inflated across sessions, candidate `feedback_machine_speed_scope_estimation` rule (Claude+Rigby cadence ≈ 1/5 to 1/10 of human wall-clock; scope estimates should reflect machine-speed reality).

**Classification per PLAYBOOK-6.10.8:** `same_pr_mitigatable` — mitigated within B3 A1 SIGN turn; Chris routed to explicit choice-check.

### Fold D — B3 scope surprise (audit-driven, informational)

**Trigger:** S3011 00-START described B3 as "~1-2 hr disposition arc" for `api_helpers.py`. Audit revealed ~90 caller sites across 4 primary files — not a disposition, a full migration arc.

**Root cause:** S3010 close-cascade authored B3 without doing the caller audit; assumed the disposition would be small based on `api_helpers.py` file size (81 lines) rather than call-site count.

**Mitigation applied:** Ran the caller audit inside B3 A1 SIGN (before touching any code). Rigby A1 concurred on rescope. Chris chose Option F (defer as T-ENVELOPE-3).

**Rule extraction potential:** Watch for 2nd trigger. If cross-session forward-carry scope estimates repeatedly miss audit-driven surprises, candidate rule: "close-cascade estimates that name a new arc MUST include a caller-count or file-count audit result, not just narrative scope."

**Classification per PLAYBOOK-6.10.8:** `informational` — no ship-blocking impact; corrected in-session; T-ENVELOPE-3 successor arc registered.

### Fold E — DRF Response scope-drift discovery (1st trigger, informational)

**Trigger:** B2 A1 audit grep found `core/views_odds_sports.py` (S3006 Batch 1 MIGRATED_FILES) has ~32 DRF `Response({'error': str(e)}, ...)` leak sites. These were never in scope for S3006 Batch 1 (which was Family B helper migration, not raw response body cleanup).

**Root cause:** S3006 Batch 1 MIGRATED_FILES gate was scoped to deprecated helper CALLS (`api_error`, `APIResponseEnvelope.error`, etc.) but did NOT cover raw `JsonResponse` / `Response` construction with `str(e)` in the body. This class of leak was invisible until the B2 lint expansion revealed it.

**Mitigation applied:** B2 lint grandfathered the 32 existing leaks via `STR_E_LEAK_GRANDFATHER` set (does not fail CI immediately) + registered "sports odds leak drain" arc as Rigby A1 Z1 follow-up.

**Rule extraction potential:** Watch for 2nd trigger (e.g., another migration batch missing a class of leak that a later lint discovers). If pattern repeats, candidate rule: "MIGRATED_FILES lint additions must include audit of both helper-call AND raw-construction leak classes for the file(s) being added."

**Classification per PLAYBOOK-6.10.8:** `informational` — grandfathered debt cataloged; no ship-blocking impact.

## Forward carries into S3012

### New from S3011

- **T-ENVELOPE-3 primary arc** — retire `api_helpers.api_error` (+ `api_success` per split disposition) across ~90 sites in 4 primary files + 6 minor sites. Bundled bug fix in `views_rag_observability.py` (`status_code`→`status` kwarg name). Estimate at machine-speed cadence: ~45-90 min via 4 sequential mini-PRs (one per primary file) or 2-batch split like Batch 4a/4b.
- **Fold B 4th trigger** — PLAYBOOK-7.4.5 amendment (`make restart` requirement for Daphne request path) — v0.10.1 PATCH candidate. Bundle candidate with T-ENVELOPE-3 close or standalone.
- **Fold A 1st trigger** — 00-START line-number drift. Watch for 2nd; do line-number lookups fresh at session open.
- **Fold C 1st trigger** — Wall-clock time inflation. Watch for 2nd; use machine-speed framing in scope estimates.
- **Fold D 1st trigger** — Close-cascade scope estimates without caller audits. Watch for 2nd.
- **Fold E 1st trigger** — MIGRATED_FILES lint scope-drift (helper-call vs raw-construction leak classes). Watch for 2nd.
- **Sports odds leak drain arc** — 32 DRF Response `str(e)` sites in `views_odds_sports.py` grandfathered by B2 lint. Follow-up arc; each drained site removes one grandfather entry.
- **future_str_e_variants** — `repr(e)` / `force_str(e)` / `f"{e!r}"` detection extension for B2 lint (per Rigby A2 STRENGTHEN, deferred beyond promised scope).

### Carried from S3010 (RESOLVED this session)

- **Fold B `4th trigger`** — still open (this session's B1 was 4th trigger; amendment ready).
- **B1 gumroad_webhook migration** — RESOLVED at PR #3698.
- **B2 JsonResponse-str(e) lint check** — RESOLVED at PR #3699 (extended scope: JsonResponse+Response via AST).
- **B3 api_helpers.py disposition arc** — RESCOPED as T-ENVELOPE-3 for S3012+ per Chris Option F.

### Carried from S3009 (STATUS UNCHANGED)

- **Fold A `1st trigger` ledger entry** `f4e8481f-...` (LLM-side hallucination) — still open, watch for 2nd trigger. **ZERO hallucinations at S3011** (all Rigby SIGN cycles tool-grounded; matches S3010 pattern).
- **Fold B `1st trigger`** (`repo_tool.search` no total_matches) — still open.
- **Fold C `1st trigger` ledger entry** `e6e7fd6d-...` (Rigby shell-exec tool-surface gap) — still open, watch for 2nd trigger.

### Carried from earlier sessions (STILL OPEN — unchanged this session)

(Full list preserved in S3010 handoff; no delta at S3011.)

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Fold B (4th trigger)** remains the strongest amendment candidate for v0.10.1 PATCH.
- **ADR corpus:** ADR-0001 through ADR-0007. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now FULLY COMPLETE.** T-ENVELOPE-3 successor arc opens for `api_helpers.py` retirement.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× clean Flow B spec→ship this session** (B1 A1→implement→A2→ship→restart→live-curl; B2 A1→implement→A2→ship). Plus 1 audit-driven decision cycle (B3 A1 rescope, no ship).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **5× substantive Rigby SIGN cycles this session** (B1 A1 + B1 A2 + B2 A1 + B2 A2 + B3 A1). All tool-grounded. **Zero hallucination triggers.** Matches S3010 pattern (2 sessions of zero-hallucination continuous).
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 3 mid-flight decision surfaces (B1 shape, B2 sequential-vs-bundled, B3 audit rescope). All routed via Rigby-then-Chris with plain-English framing. Chris re-scope on B3 confirmed via Option F choice.
- **Recycle discipline:** B1 (view diff) → `make restart` used correctly. **Fold B 4th trigger.** B2 (lint-only) → no restart needed. Cascade PR (docs only) → no restart needed.

## Wrapper pin note

The active PA conversation pin at S3011 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Committed the wrapper diff in the S3011 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
