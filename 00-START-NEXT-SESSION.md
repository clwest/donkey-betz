# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2885 CLOSE → content_tool file-completing slate shipped + pgbouncer collision fully resolved + Slate B pivot to criticality-first ratified (2026-07-22; picks up as S2886) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2885 close).** S2885 was the eighth handler migration slate — **second file-completing slate** after S2884 opened the shape. **Two PRs shipped.** `td_handlers_content.py` (13→0) EXITS the S2876 sunset population. **Pgbouncer collision from S2884 close fully resolved** (three stacked infra faults diagnosed + fixed). **Rigby zoom-out (b) fold + Chris D-verdict ratified Slate B pivot to criticality-first grep across the 4 remaining files** — file-completing is retired as the default shape.

- **PR #3394** `5495736fb` — S2885 slate (2 files, +439/-13)
  - **content_tool cluster** (`_handle_deliverable_initiative_link` L178/L182/L186/L190, `_handle_feedback` L3654, `_handle_content` L4788, `_handle_bulk_archive` L4821, `_handle_bulk_archive_published` L4966/L4971/L4976/L4980/L4984/L5046): 13 sites across 5 handlers, 3 dispatched tool surfaces (`deliverable_tool`, `feedback_tool`, `content_tool`).
  - **Codes:** 1× `unknown_action`, 9× `invalid_params`, 2× `not_found`, 1× `permission_denied`. All 13 sites map cleanly to existing 5-code taxonomy — no broad-except, no `internal_error`, no new codes.
  - **Micro-decisions (Chris pre-approved + Rigby SIGN AGREE):** T1c legacy `status: 403` field dropped from L4966 permission_denied envelope; T1d L5046 `**result` dry-run preview preserved via `**{k: v for k, v in result.items() if k != 'action'}` filter (avoids TypeError collision with helper's `action` positional).
  - **Helper-choice = uniform `_handler_error`** (file-local copy, same shape as S2879/S2882/S2883/S2884). **Ledger #13 adopter count now 5/6** — 1 more adopter needed to trigger `td_error.py` extraction arc.
  - **Two folds captured inline in test module docstring:** Fold 1 (`TransactionTestCase` required whenever setUp-created rows must be visible to `ToolDispatcher.execute_sync` — S2885 is 1st trigger; watch S2886 for corroboration), Fold 2 (L190 was false-passing before fortification when two branches return the same taxonomy code — Playbook amendment candidate if re-triggers).
  - **Combined regression:** S2869 → **S2885** + `test_zoom_out_tool_2780` = **220/220 pass** (207 baseline + 13 new).
- **PR `<docs cascade>`** — S2885 handoff + this file refresh + wrapper pin bump (`pa-42342895674d4878` → S2886 mint) + `docs/INDEX.md` refresh.

### S2885 open — pgbouncer auth block fully resolved (three stacked faults)

Chris's character-os collision hypothesis at S2884 close was correct. Investigation surfaced two additional stacked faults; all three fixed at S2885 first-action:

1. **Character-os `pgvector/pg16` Docker container captured `:5433` via IPv6 wildcard** (`0.0.0.0:5433->5432/tcp`). u-d-b's native pgbouncer (PID 1513) held IPv4 `127.0.0.1:5433`. `localhost:5433` resolves to `::1` first → Django hit character-os postgres. Fix: `USE_PGBOUNCER=0` in `.env` in BOTH `/Donkey_Betz/unified-donkey-betz/` and `/development/unified-donkey-betz/` checkouts (symmetric bypass).
2. **Orphan Daphne from `/development/unified-donkey-betz/`** (PID 60841, elapsed 4h38m, parent=launchd) held `:8000`. `make restart-daphne` silently failed to bind (`Address already in use`). Fix: `kill 60841`, then restart from `/Donkey_Betz/`. Chris designated `/development/` legacy — deletion decision deferred to S2886 open.
3. **`.env` `PA_API_TOKEN` was 11 days stale** (rotated 2026-07-11 S2758-era). Fix: sync to current DB value (`8c0f15633e84...`).

**Rigby Tool Gap Ledger entry #24 persisted** (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`, 2874 chars appended, new total 50822 chars) at S2885 first-action.

Full context: `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`.

## PRIOR SESSIONS — S2884 close + S2883 close + S2882 close + S2881 close + S2880 close

- **PR #3393** `43f40edd5` — S2884 docs cascade. See `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md`.
- **PR #3392** `65e4da587` — S2884 slate: agents_tool + newsletter_tool file-completing (4 files, +294/-25).
- **PR #3391** `444b28a5e` — S2883 docs cascade + wrapper pin bump. See `docs/handoffs/SESSION_2883_AGENT_DIAG_CRITICAL_SLICE.md`.
- **PR #3390** `ca61c7725` — S2883 slate: agent-diag family critical-slice (2 files, +396/-10).
- **PR #3389** `de78ba609` — S2882 docs cascade + wrapper pin bump.
- **PR #3388** `377f39364` — S2882 close follow-on: `permission_denied` 5th taxonomy code + not-staff branch migration.
- **PR #3387** `6331c833e` — S2882 slate: `ops_tool` EXECUTION + AUTH critical-slice.

---

## S2886 open sequence

### Step 1 — Slate B pivot to criticality-first (Chris pre-ratified)

**4 handler files remain in the S2876 sunset population:**

| File | Bare-return count |
|---|---|
| `td_handlers_core.py` | 73 |
| `td_handlers_gateway.py` | 57 |
| `td_handlers_railway.py` | 18 |
| `td_handlers_codejobs.py` | 15 |
| **Total** | **163** |

**S2886 pre-code SIGN Q1 (per zoom-out (b) discipline):** grep `core.py` + `gateway.py` (highest-volume; 73+57=130 sites, 80% of remaining population) for `return \{('error'|"error")` returns AND enclosing `def _handle_*` scope. Categorize by handler criticality (write-path / auth / tenant / read-only). Pick highest-risk cluster for Slate B. Warm-cadence Q1 same shape as S2879/S2880/S2881/S2882/S2883.

**Recommended default:** Slate B targets a `core.py` write-path or auth cluster (matches S2879→S2883 criticality-first cadence). Fold-in `gateway.py` if a naturally-linked cluster surfaces during Q1 routing map. `railway.py` (18) + `codejobs.py` (15) are the file-completing tail — hold for later slates when only they remain.

### Step 2 — Deferred S2885 close artifacts (housekeeping)

1. **Fold 1 + Fold 2 promotion decision:** if Slate B testing also requires `TransactionTestCase` for setUp fixtures, Fold 1 is at 2nd trigger — ledger entry becomes Playbook amendment candidate. If Slate B has two branches returning the same taxonomy code, Fold 2 hits 2nd trigger.
2. **`/development/` checkout status:** Chris to decide `rm -rf` vs dormant.
3. **`.env` `USE_PGBOUNCER` restoration triggers:** stay `=0` until cross-repo port ownership resolved.

### Step 3 — Net-new engineering candidates for S2886 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2885 close — `TransactionTestCase` requirement as first-class testing rule.** Fold 1 substrate. If Slate B corroborates, promote to Playbook amendment. Otherwise, hold.

2. **NEW at S2885 close — false-pass discipline for shared-taxonomy branches.** Fold 2 substrate. Same corroboration gate.

3. **NEW at S2885 close — Cross-repo Docker infra collision documentation.** Fold 4 substrate. Character-os collision now confirmed as 1st trigger; watch for 2nd trigger before promoting to `feedback_post_travel_port_collision_triage` extension.

4. **NEW at S2885 close — `.env` `PA_API_TOKEN` drift alarm.** Subitem of Ledger #24. Consider CI check that `.env` token matches DB token for the wrapper-owning user. Deferred.

5. **Carried from S2884 — Ledger #13 unified helper extraction (`td_error.py`)** — adopter signal now 5/6. Slate B is the extraction-arc trigger candidate.

6. **Carried from S2883 — Fold X test-authoring convention documentation** — 2nd trigger at S2883. Standardize on `TransactionTestCase` or ORM-boundary mocking for dispatcher-path tests requiring DB-visible state. **S2885 Fold 1 corroborates this.**

7. **Carried from S2882 — Fold Y `_authorize_staff` broad `except Exception:` narrowing** to `User.DoesNotExist` — behavior change, requires own SIGN.

8. **Carried from S2882 — PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers + Rigby zoom-out (b) refinement.

9. **Carried from S2881 — Grep-based CI audit metric** — count bare `return {'error':}` returns across `core/services/*.py`; fail CI on regression.

10. **Carried from S2880 — Fold A/B/C from S2880 post-code.** Fold C at 3rd trigger from S2883.

11. **Carried from S2878 — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger).

12. **Carried from S2877 — Schema-level dead-branch investigation** (1st trigger from S2875).

13. **Carried from S2877 — Schema-layer PA route smoke extension**.

14. **Carried from S2876 — #22.3 orthogonal-contract-axes resolution** (1st trigger).

15. **Carried from S2877 — #22.4 Rigby dispatcher-probe extension** (1st trigger).

16. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (1st trigger). **S2885 corroborates — orphan Daphne from `/development/` was a multi-checkout artifact. 2nd trigger candidate; Chris designated `/development/` legacy, so pattern may not re-fire.**

17. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger).

18. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger).

19. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

20. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr).

21. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

22. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

23. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

24. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

25. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

26. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

27. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

28. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.**

29. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

30. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

31. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

32. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

33. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

34. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

35. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

36. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

37. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

38. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

39. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

40. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

41. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

42. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

43. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → S2879 → S2880 → S2881 → S2882 → S2883 → S2884 → **S2885 (content_tool file-completing + pgbouncer collision resolved)**. See A4 Constraints below.

44. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive. **S2885: character-os collision on `:5433` confirmed as active infra concern; Chris flagged "one of the roadmaps tied both together" + "everything will need to be universal" — universalization coming.**

### What's forbidden at S2886 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2885 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2885: content_tool now emits structured error codes across 3 dispatched tool surfaces (`deliverable_tool` link_initiative/unlink_initiative, `feedback_tool` submit, `content_tool` top-level + `bulk_archive` + `bulk_archive_published`). Second file-completing wave in the S2876 sunset arc — content.py EXITS the population. A4 outreach substrate now has structured error semantics on deliverable-initiative linking, feedback submission, and staff-gated content archival surfaces, extending prior S2884 cost_telemetry+newsletter + S2883 agent-diag + S2882 EXECUTION+AUTH + S2881 write-path + S2880 kill-switch + S2879 governance coverage.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(rr) as ratified at S2884 close. **(ss) `content_tool` (across `deliverable_tool` + `feedback_tool` + `content_tool` gateways) now emits concrete `error_code` from the 5-code taxonomy including `permission_denied` on staff-gated write-paths. Second file-completing wave in the S2876 sunset arc completes 1 additional handler file. A4 messaging that references deliverable-initiative linking, user feedback, or bulk archival flows can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2885 close — what shipped (one slate PR + this docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3394** `5495736fb` — S2885 slate: `td_handlers_content.py` file-completing critical-slice structured error-envelope migration (2 files, +439/-13)
- **PR `<this docs cascade>`** — S2885 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2886 open + `docs/INDEX.md` refresh

**Workspace canonical (Rigby-authored at S2885 first-action):**
- **Rigby Tool Gap Ledger entry #24** — S2884→S2885 pgbouncer auth block resolution + character-os collision root cause, appended to deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (2874 chars, new total 50822 chars).

**Runtime impact:**
- Eighth wave (second file-completing shape) of real handler migrations in the S2876 backfill sunset arc.
- Legacy-file population S2884=5 files → **S2885=4 files** (content.py EXITS).
- Sub-population count 176 → **163 bare-returns** across 4 remaining files.
- Regression suite grew from 207 → **220** (+13 S2885 rows).
- 13 sites no longer surface `error_code='legacy_error'`; consumers can key on 5-code taxonomy.
- No new helper introduced. No taxonomy expansion. No new PLAYBOOK amendment.
- Ledger #13 (`td_error.py` extraction) adopter count = 5/6 — 1 more adopter needed to trigger dedicated arc. Slate B is a natural candidate.

**Session infra work resolved (not shipped as PR):**
- Character-os postgres collision on `:5433` (bypassed via `USE_PGBOUNCER=0` in both `.env` files).
- Orphan Daphne from `/development/` checkout killed; checkout designated legacy.
- 11-day-stale `PA_API_TOKEN` in `.env` synced to current DB value.
- Rigby Tool Gap Ledger entry #24 persisted.

**Slate B pivot ratified:** file-completing retired as the default shape; criticality-first grep on `core.py` + `gateway.py` is the S2886 first-action.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2885)

See:
- **S2885 handoff (current):** `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`
- **S2884 handoff:** `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md`
- **S2883 handoff:** `docs/handoffs/SESSION_2883_AGENT_DIAG_CRITICAL_SLICE.md`
- **S2882 handoff:** `docs/handoffs/SESSION_2882_OPS_EXECUTION_AUTH_CRITICAL_SLICE.md`
- **S2881 handoff:** `docs/handoffs/SESSION_2881_OPS_WRITE_PATH_CRITICAL_SLICE.md`
- **S2880 handoff:** `docs/handoffs/SESSION_2880_OPS_REMAINDER_CRITICAL_SLICE.md`
- **S2879 handoff:** `docs/handoffs/SESSION_2879_GOVERNANCE_OPS_CRITICAL_SLICE.md`
- **S2878 handoff:** `docs/handoffs/SESSION_2878_BPAAS_ERROR_ENVELOPE.md`
- **S2877 handoff:** `docs/handoffs/SESSION_2877_PA_SURFACE_ERROR_CODES_SMOKE.md`
- **S2876 handoff:** `docs/handoffs/SESSION_2876_DISPATCHER_ERROR_CODE_BACKFILL.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
