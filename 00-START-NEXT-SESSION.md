# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3010 CLOSED. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now at 5-of-5 files migrated.** All 62 sites in `core/views_platform_integrations.py` shipped via 2-PR split (16 auth + 46 CRUD) + Fold E RateLimiting 429 migrated + 2 Rigby Tool Gap Ledger entries minted. Arc is **essentially complete**; only trailing scope = 3 gumroad_webhook sites (Chris-deferred pending Gumroad body-shape sensitivity check) + api_helpers.py disposition arc.

**3 feature PRs + 2 ledger deliverables shipped this session.**

**PR #3694 (`2cfa01561`) — Fold E: RateLimiting 429 → helper.** Last raw JsonResponse envelope in auth_middleware.py migrated. File now 11/11 sites helper-based, 0 raw patterns. JsonResponse import dropped. Rigby A2 SIGN AGREE 5/5. Programmatic smoke verified (middleware commented-out in settings; RequestFactory smoke confirmed 429 + Family E + retry_after_seconds=300 + full log-source proof).

**PR #3695 (`cd65a3931`) — Batch 4a PR A: 16 auth-surface sites.** oauth_connect + oauth_callback + refresh_token migrated. 9 status shifts (400→503×3, 400→502×2, 400→500×3, 400→404×1, 400→401×1). Safety upgrade: 2 exception-fallback sites no longer leak str(e) to user-facing body. **Import strategy correction:** api_error RETAINED in PR A (pending PR B) — new Fold D rule pattern for PR-split migrations. Rigby A2 SIGN AGREE 5/5. 3-site smoke PASS.

**PR #3696 (`c7e0fbc71`) — Batch 4b PR B: 46 platform-CRUD sites + MIGRATED_FILES = 5.** etsy + shutterstock + gumroad + sync + disconnect endpoints all migrated. Combined file at 62/62 sites. Added to MIGRATED_FILES tuple (**5 files tracked**). 24 status shifts (400→404×10, 400→500×8, 400→502×5, 400→503×1). 8 exception-fallback safety upgrades. api_error dropped from imports (final cleanup). Rigby A2 SIGN AGREE 4/5 + PARTIAL D3 (scope-of-inspection, not code defect). 3-site smoke PASS with behavior-change verification (400→404 + 400→503 both confirmed live).

**Task C — 2 Rigby Tool Gap Ledger entries** minted in workspace `b4503364-2573-4401-9e28-61a739e0ce50`:
- **`f4e8481f-ac80-477d-b5dd-9f291a21f245`** — Rigby Tool Gap — LLM-side hallucination on file-level code claim (S3009 Fold A)
- **`e6e7fd6d-0f8a-4ba9-8ecb-879612ea779c`** — Rigby Tool Gap — shell-exec surface gap for read-only verification (S3009 Fold C)

Post-create ORM fix applied to both per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.

**Rigby SIGN quality this session:** 4 substantive SIGN cycles, all tool-grounded, ZERO hallucination triggers (contrast S3009 Fold A). Fold C stays at 1st trigger.

**HEAD at close:** `c7e0fbc71` + docs cascade PR (this file + handoff + INDEX regen + wrapper pin bump + orphan docs/INDEX.md carry-over from S3009).

Full context:
- `docs/handoffs/SESSION_3010_T_ENVELOPE_2_DEPRECATION_BATCH_4_COMPLETE.md` — 3-PR close, 5 folds (A/B/C/D/E), forward carries
- `docs/adr/ADR-0007-layered-envelope-policy.md` — parent ADR (ratified S3005)
- `core/security/error_envelope.py:117-154` — helper (shipped S3008)
- `scripts/lint_no_deprecated_family_b.py` — **5 files tracked** (added views_platform_integrations.py this session)

---

## S3011 primary directive candidates — Chris ratifies at open

The T-ENVELOPE-2-DEPRECATION arc is **essentially complete**. S3011 has more options than prior sessions; Chris should choose the direction.

### Option A — Fold B Playbook amendment (middleware/view restart discipline, 4th trigger)

**~1 session.** Fold B has hit 4 triggers (S3007 1st, S3008 2nd, S3009 3rd, S3010 4th). The pattern is stable and repeatable. Extend `feedback_recycle_after_merge` into a formal PLAYBOOK-7.4.5 rule (or v0.10.1 PATCH). Rule text: "Any change to files loaded by Daphne request path (middleware / views / URLs / settings / installed_apps) requires `make restart` or `make recycle-all`, not `make celery-recycle` alone."

Do we lose anything by doing this? No — codifies existing behavior. More work later? No — reduces future re-derivation cost.

Recommended if Chris wants to close out the governance side of the arc.

### Option B — Close-out T-ENVELOPE-2-DEPRECATION trailing scope

**Bundle: gumroad_webhook migration + JsonResponse-str(e) lint check + api_helpers.py disposition.** ~1-2 sessions.

**B1 (~1 hr):** gumroad_webhook migration. 3 sites at `core/views_platform_integrations.py` L1418/L1428/L1435. Need to verify Gumroad webhook body-shape sensitivity first (external consumer contract). Steps:
1. Check Gumroad webhook docs for expected body shape on error / retry semantics
2. If safe (they only check HTTP status): migrate + drop JsonResponse import + smoke via webhook simulation
3. If unsafe: keep raw JsonResponse but at least remove str(e) leak at L1435

**B2 (~30 min):** JsonResponse-str(e) lint check. Rigby S3010 A2 Z1(b) suggestion. Extend `scripts/lint_no_deprecated_family_b.py` (or add new script) that greps for `JsonResponse(...'message': str(e)...)` or `JsonResponse(...'message': f"...{e}...)` patterns. Catches the current gumroad_webhook L1435 leak + prevents regression.

**B3 (~1-2 hr):** api_helpers.py disposition arc. Currently: Family B helpers (`api_success`, `api_error`, etc.) with deprecation docstrings. Decision: (a) retire (breaking change for any leftover callers), (b) keep-with-warning + add runtime DeprecationWarning, (c) split (keep api_success + api_paginated as canonical for success responses per ADR-0007 §3.3, retire error helpers). Includes grep audit for any remaining api_error callers platform-wide.

Do we lose anything by deferring? Nothing user-visible; 3 webhook sites stay Family B. More work later? Yes — the arc will keep 2 small carry-forwards indefinitely if not closed.

Recommended if Chris wants engineering completeness.

### Option C — Fresh engineering thread (Chris bias-engineering rule)

Per `feedback_engineering_bias_over_audit`: at session open, list net-new engineering candidates FIRST. Batch 4 was engineering, but the arc is winding down. Concrete net-new candidates:

- **New spider:** any market/data source Chris wants coverage on (e.g., Kalshi option chains, congressional trades, Fed FOMC calendar).
- **Workspace tab enhancement:** per `feedback_workspace_over_command_center_for_new_ui` — extend Files tab, Deliverables tab, or Initiatives tab with a specific new capability.
- **Agent capability:** new AGENT_MAP entry, new tool_dispatcher handler, new advisor domain specialist.
- **Pipeline:** new signal aggregation rule, new content deliberation stage, new body-system monitor.
- **Dashboard:** new operator-observability view, new revenue attribution surface, new agent-collaboration graph.

Chris raises specifics at S3011 open; Claude proposes 1-3 candidates from repo state.

### Option D — Docs restructuring arc (queued at S2801)

Chris directive S2800 close (2026-07-16): open a parent-scoped research arc auditing `/docs/` using the `/docs/research/` pattern itself. Output = design proposal + migration plan across arc; NOT code changes / file moves. Fresh session; first-action fresh mint. 4 proposed audit threads (inventory / research-pattern extraction / human pain / handoffs+audits proliferation).

**Complementary to Chris's ebook idea** (recorded S3010 in `project_ebook_from_docs_folder`) — the docs restructuring arc could produce the ebook as an output.

### Option E — Chris's own priority

Chris may have surfaced other work between sessions (email, discord, personal channels not in Claude context). Chris-driven directive supersedes A/B/C/D.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3010 handoff (`docs/handoffs/SESSION_3010_T_ENVELOPE_2_DEPRECATION_BATCH_4_COMPLETE.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show docs cascade → `c7e0fbc71` (PR #3696 Batch 4b) → `cd65a3931` (PR #3695 Batch 4a) → `2cfa01561` (PR #3694 Fold E) → `6d8bf37fb` (S3009 close cascade).
   - `python scripts/lint_no_deprecated_family_b.py --list` — confirm **5 tracked files** (Batch 4 addition present).
   - `grep -rn "api_error\|api_unauthorized\|api_forbidden" core/ --include="*.py" | grep -v "views_odds_sports\|views_revenue_analytics\|auth_middleware\|views_auto_distribution\|views_platform_integrations\|api_responses"` — identify remaining callers of Family B helpers OUTSIDE the 5 migrated files. Feeds Option B3 (api_helpers.py disposition audit).

**Joint recommendation at close:** No single clear winner given arc completeness. Preferred order depends on Chris signal:
- If Chris wants **governance closure**: A (Playbook amendment) > B (close-out arc).
- If Chris wants **engineering completeness on the arc**: B (close-out) > A.
- If Chris wants **fresh momentum**: C (fresh engineering) > D (docs arc) > A/B.
- If Chris signals nothing specific: **A first (~1 hr Playbook amendment, quick win + closes the well-motivated 4-trigger pattern) then B1+B2 bundle (~1-1.5 hr close-out gumroad_webhook + lint)** — combined ~2-3 hrs closes multiple loops in one session. Then next session goes C or D.

---

## S3011 carry-forward seeds

### New carry-forward from S3010

- **Fold B `4th trigger` — middleware/view restart discipline.** Playbook amendment strongly motivated. Priority Option A.
- **Fold D `1st trigger` — PR-split import-cleanup discipline.** New rule pattern (deprecated imports must be retained until final PR of a split). Watch for 2nd trigger.
- **Fold E — JsonResponse-str(e) lint check.** Small tooling PR candidate. Bundle with gumroad_webhook migration (Option B1+B2).
- **HTTP Retry-After header** — Rigby S3010 Fold E A2 Z1(c) suggestion. Add header from within emit_error_envelope for RATE_LIMITED reason codes. Future work.
- **Fold A `7th continuous cascade`** — observation stays; watch for cascade-class break.

### T-ENVELOPE-2-DEPRECATION queue after S3010

**Essentially complete.** Only trailing:
- **gumroad_webhook migration** (3 sites deferred per Chris) — Option B1
- **api_helpers.py disposition arc** — Option B3

### Carried from S3009 (RESOLVED this session)

- **Fold A `1st trigger`** (Rigby LLM-side hallucination) — **Ledger entry minted:** `f4e8481f-ac80-477d-b5dd-9f291a21f245`. No 2nd trigger at S3010 (Fold C at S3010 explicitly noted zero repeats). Continue to watch.
- **Fold B `1st trigger`** (repo_tool.search no total_matches, S3008) — still open. Bundle candidate with the second S3009-Fold-C ledger entry (`e6e7fd6d-0f8a-4ba9-8ecb-879612ea779c`) for repo_tool capability expansion arc.
- **Fold C `1st trigger`** (Rigby shell-exec tool-surface gap) — **Ledger entry minted:** `e6e7fd6d-0f8a-4ba9-8ecb-879612ea779c`. Watch for 2nd trigger.
- **Fold E `future_trigger`** (RateLimiting 429) — **RESOLVED at S3010 as PR #3694.**

### Carried from earlier sessions (STILL OPEN — unchanged this session)

- **Fold C `future_trigger` from S3006** — DRF-decorator refactor for inline auth checks. Deferred.
- **Fold A/B/C `informational` (1st trigger) from S3005** — PLAYBOOK-7.7.1 abort-early clause / ADR-baseline drift / `refines:` frontmatter field. Watch for 2nd triggers.
- **Fold A `2nd trigger` from S3004** — Fold-Drain-Same-Surface pattern. Watch for 3rd.
- **Fold B `informational` (1st trigger) from S3004** — shared-const derived-union frontend pattern. Watch for 2nd.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc` from S3004** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger) from S3004** — Rigby repo_tool line-1 read-display truncation false-positive. Watch for 2nd.
- **Fold A `informational` (1st trigger) from S3003** — risk-gate T-slot vs T-ENVELOPE-N scoping.
- **Fold C `informational` (1st trigger) from S3003** — Django reverse-O2O test cache-bust pattern.
- **Fold C `informational` (T-ENVELOPE-0 dev-only) from S3002** — `componentDidCatch` fires twice in dev under StrictMode.
- **Fold D from S3002** — ADR successor discipline VALIDATED PATTERN.
- **Fold B `informational` from S3001** — future ADR-N misread risk.
- **Fold C `informational` (1st trigger) from S3001** — verify target research slot state before accepting scope.
- **Fold A `informational` (1st trigger) from S3000** — reproduce failure at thinnest interface.
- **Fold B `informational` from S3000** — residual APIClient-forcing shapes.
- **Fold B `active watch` from S2999** — metadata accretion governance.
- **Fold C from S2999** — Rigby Tool Gap Ledger, file:line-only scope of consumer verifier.
- **Fold A/B/C `future_trigger` from S2998** — force=true × factory dedupe semantic mismatch / force re-dispatch could emit DeliverableEvent breadcrumb / Rigby Tool Gap Ledger.
- **Fold B `future_trigger` from S2997** — dedupe strictness on stale-ref ACs.
- **Fold F from S2997** — Rigby Tool Gap Ledger (`orm_inspect_tool` JSON-path lookups).
- **Fold C `future_trigger` from S2996** — staleness toast reinforcement.
- **Fold E from S2996** — Rigby Tool Gap Ledger (no in-UI Recheck action).
- **Fold C/D `future_trigger` from S2995** — staleness metadata + periodic staleness beat.
- **Fold E from S2995** — Rigby Tool Gap Ledger (metadata accretion governance).
- **Fold F `future_trigger` from S2995** — WorkspacePageNew param preservation.
- **Fold B/C/D `future_trigger` from S2994** — inline-helper density / Deliverables-tab type badge / Rigby Tool Gap Ledger.
- **Fold B/C ledger candidates from S2993** — dry-run preview for send-to-rigby / executable-prompt tightening.
- **Signal-tweak follow-up for `finding_type` classifier from S2992** (2 acceptable-misses).
- **Data-migration-vs-management-command pattern from S2992** (3rd-trigger check).
- **Dry-run counts pattern from S2991** (3rd-trigger check).
- **Contract-lock-in guardrail from S2991** — updated set.
- **F-D3-tracker-scope wire-up / F-D2-broad LLM-bypass audit / Chris 1805 cap-drift reconciliation / Canonical Briefing v2 scope toggle / _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT substrate fix / Send-to-Rigby follow-ups from S2988** (S2989-S2990 batch).
- **Chris browser visual checks on S2984 arcs section + S2985 Canonical Briefing tab strip (~5 min each).**
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Systemic auth-XHR treatment (S2984 Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails (~15 min).**
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade (~5 min).**
- **Phase B Theme Signals — "Why now" LLM summarizer (~1 session).**
- **Phase B Theme Signals — who-benefits/who-loses (~1-2 sessions).**
- **Theme Signals sub-tab persistence via localStorage (~30 min).**
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id` (~30-60 min).
- **Fold B `future_trigger` from v0.8.0** — fold-authoring evidence-admission helper (3-trigger threshold NOT yet met).
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for v0.9.0 and v0.10.0.
- **Live browser smoke on S3004 VIP-expired modal (~5 min).**
- **ADR-0007 twin-mirror deliverable** — post-close Rigby dispatch to workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` for ratification-record provenance.
- **Batch 3 400→404 image/video not_found verification** (from S3009 forward-carry) — needs UserPlatformAccount test data setup for chris.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Fold B (4th trigger)** is the strongest amendment candidate. Priority Option A at S3011.
- **ADR corpus:** ADR-0001 through ADR-0007. **ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION at 5-of-5 files migrated + Fold E shipped.** Only `gumroad_webhook` (3 sites) + `api_helpers.py` disposition remain.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **3× clean Flow B spec→ship this session** (Fold E pre-ratified spec direct to A2; Batch 4a PR A A1→implement→A2; Batch 4b PR B A1-inherited→implement→A2). Plus 1 Rigby-only task (Task C ledger entries).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **4× substantive Rigby SIGN cycles this session** (Fold E A2 + Batch 4 A1 + PR A A2 + PR B A2). Zero hallucination triggers (contrast S3009). Fold C stayed at 1st trigger.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 2 mid-flight decision surfaces (gumroad_webhook scope + PR split shape) routed via Rigby with plain-english framing. Chris confirmed DEFER on gumroad. Full decision loop closed.
- **Recycle discipline:** middleware/view diff → `make restart` used correctly on all 3 PRs. **Fold B 4th trigger, threshold clearly met.**

---

## Wrapper pin note

The active PA conversation pin at S3010 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3010 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3010 shipped a clean 3-PR sequential close following the S3009 joint recommendation shape (C+B1+A):** ledger entries → Fold E warm-up → Batch 4 (2-PR split). ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION is now at 5-of-5 files migrated. The arc's engineering substrate is complete. **S3011 opens with more options than any prior session:** governance closure (Fold B amendment), close-out (gumroad_webhook + lint + api_helpers), fresh engineering, docs restructuring, or Chris's own priority. Rigby SIGN quality stayed clean this session (zero hallucination triggers, contrast S3009 Fold A which motivated the ledger entry minted this session).
