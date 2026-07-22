# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2884 CLOSE → agents_tool + newsletter_tool file-completing slate shipped + pgbouncer auth block deferred (2026-07-21; picks up as S2885) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-21 (S2884 close).** S2884 was the seventh handler migration slate — **first file-completing slate** after 6 criticality-first slates. **One PR shipped.** Both `td_handlers_agents.py` (1→0) and `td_handlers_newsletter.py` (7→0) EXIT the S2876 backfill sunset population.

- **PR #3392** `65e4da587` — S2884 slate (4 files, +294/-25)
  - **cost_telemetry_tool cluster** (`_handle_cost_telemetry` L5026, 1 site): unknown action → `unknown_action`.
  - **newsletter_tool cluster** (`_handle_newsletter` + 3 per-action helpers, 7 sites): L44 unknown_action, L85/L341/L391 invalid_params (missing id), L90/L346/L396 not_found (Deliverable.DoesNotExist).
  - **Helper-choice = uniform `_handler_error`** (Rigby+Claude joint verdict, Chris D-approved). All 8 sites map cleanly to existing 5-code taxonomy — no broad-except, no `internal_error`, no new codes needed. Contrast with S2883's Path 1 SPLIT.
  - **Ledger #13 adopter count now 4/6** (ops + governance + agents + newsletter). Rigby's 6-adopter gate for `td_error.py` extraction still 2 files short.
  - **Retired S2877 backfill row:** `test_newsletter_unknown_action_backfilled` removed from `LegacyBackfillPASurfaceTests`. Class now defines 0 test methods; kept structurally with docstring re-home log pending S2876 sunset PR trigger.
  - **Combined regression:** S2869 → **S2884** + `test_zoom_out_tool_2780` = **207/207 pass** (200 baseline + 8 new − 1 retired).

### S2884 close blockers (S2885 first-action)

**Rigby PA surface is 503-blocked post-recycle.** `bash tools/pa_local.sh` returns `Error: {'code': 'auth_backend_unavailable'}` — pgbouncer at `:5433` rejects `unified_user` password auth. Postgres direct at `:5432` is fine. `USE_PGBOUNCER=1` in `.env` routes Django through pgbouncer.

- **Chris hypothesis (flag at S2884 close):** Character OS startup captured or mis-configured pgbouncer. Two listeners on `:5433` observed (`pgbouncer` PID 1513 + `com.docker` PID 36957).
- **Not touched at S2884 close** per `feedback_post_travel_port_collision_triage`: no `pgbouncer.ini` reads, no `userlist.txt` rewrites, no password rotation, no `USE_PGBOUNCER=0` flip, no character-os shutdown.
- **Deferred artifacts:** (a) live Rigby envelope verification on `cost_telemetry_tool` + `newsletter_tool`, (b) Rigby Tool Gap Ledger entry #24 (draft inlined in S2884 handoff for persist-once-unblocked), (c) `session_lifecycle close` wrapper pin bump (needs DB — same block).
- **Wrapper still points at `pa-261ad03bdd634e70`** (S2883 close mint). NOT rotated at S2884 close.

## PRIOR SESSIONS — S2883 close + S2882 close + S2881 close + S2880 close + S2879 close

- **PR #3391** `444b28a5e` — S2883 docs cascade + wrapper pin bump. See `docs/handoffs/SESSION_2883_AGENT_DIAG_CRITICAL_SLICE.md`.
- **PR #3390** `ca61c7725` — S2883 slate: agent-diag family critical-slice (2 files, +396/-10).
- **PR #3389** `de78ba609` — S2882 docs cascade + wrapper pin bump.
- **PR #3388** `377f39364` — S2882 close follow-on: `permission_denied` 5th taxonomy code + not-staff branch migration.
- **PR #3387** `6331c833e` — S2882 slate: `ops_tool` EXECUTION + AUTH critical-slice.
- **PR #3385** `0c26d8564` — S2881 slate: `autopilot_tool` write-path critical slice.
- **PR #3383** `e6ae8a1b3a59` — S2880 slate: ops_tool remainder critical-slice.
- **PR #3381** `9a3039e22e69` — S2879 slate: governance_tool + ops_tool critical-slice.

---

## S2885 open sequence

### Step 1 — pgbouncer auth triage (BLOCKING)

**Character-os collision hypothesis first (Chris flag at S2884 close):**

```bash
# 1a. What owns :5433?
lsof -iTCP:5433 -sTCP:LISTEN -n -P
lsof -p 36957   # or whatever docker PID is proxying :5433
docker ps       # look for character-os containers
pgrep -fl "character-os\|characteros"

# 1b. If character-os is up and grabbed the port:
#     coordinate shutdown of its pgbouncer container (or its docker-compose stack)
#     before re-testing u-d-b's Rigby.

# 1c. Verify auth works:
bash tools/pa_local.sh "ping — s2885 post-pgbouncer-fix"
# Expected: normal Rigby response, no 'auth_backend_unavailable'
```

**Fallback (only if character-os collision is ruled out):**

- Read `pgbouncer.ini` + `userlist.txt` (paths TBD via `brew --prefix pgbouncer` or `lsof -p 1513`).
- Compare pgbouncer userlist's `unified_user` password against `.env` `DB_PASSWORD`.
- Options: (a) rewrite userlist entry, (b) rotate Postgres password to match userlist, (c) temporary `USE_PGBOUNCER=0` flip in `.env` + Daphne restart.

### Step 2 — Deferred S2884 close artifacts (after pgbouncer unblock)

1. **Live Rigby envelope verification:** fire `cost_telemetry_tool` + `newsletter_tool` with `{'action': '__bogus_s2884__'}` payloads. Expect `{success: False, error_code: 'unknown_action', action: '__bogus_s2884__', error: ...}` shape from both. If either returns `legacy_error` or bare-error shape, workers didn't pick up PR #3392.
2. **Ledger #24 persist:** Rigby appends the S2884 entry to Tool Gap Ledger (`deliverable_tool.append` on `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`). Draft body inlined in `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md` §S2884 close.
3. **Wrapper pin bump for S2885:** `python manage.py session_lifecycle close --label s2885-<slate>` — atomically retires `pa-261ad03bdd634e70` + mints fresh pin + rewrites `tools/pa_local.sh`. Verify via `grep "^python tools/pa_chat.py" tools/pa_local.sh`.

### Step 3 — S2885 primary slate DECISION POINT

**5 handler files remain in the S2876 sunset population:**

| File | Bare-return count |
|---|---|
| `td_handlers_core.py` | 73 |
| `td_handlers_gateway.py` | 57 |
| `td_handlers_railway.py` | 18 |
| `td_handlers_codejobs.py` | 15 |
| `td_handlers_content.py` | 13 |
| **Total** | **176** |

**Options for S2885 slate framing:**

- **(A) Continue file-completing — pick next smallest.** `td_handlers_content.py` (13 sites) is the smallest remaining. Warm cadence + clean EXIT milestone. First real test of whether Rigby's S2884 zoom-out concern ("file-completing hides risk by leaving nastier files") is actual or hypothetical.
- **(B) Revert to criticality-first across all 5 files.** Grep the 176 sites, categorize by handler criticality (write-path / auth / tenant / read-only), pick highest-risk cluster regardless of file. Preserves S2879→S2883 shape.
- **(C) Ledger #13 `td_error.py` unified extraction arc** — 4/6 adopter signal; not yet at threshold. Rigby's S2875 gate specifically said "wait for 6."
- **(D) PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers on record; constitutional session shape.
- **(E) Shift to net-new engineering** — per `feedback_engineering_bias_over_audit`, pause backfill arc; propose new spider / UI page / agent capability / dashboard candidate.

**Recommended default: (A)** — completes 3rd file in row and stress-tests the file-completing shape. If content.py sites reveal Fold X test-authoring convention triggers or Fold D routing-boundary drift, re-evaluate before Slate 4.

**S2885 pre-code SIGN Q1 (per zoom-out (b) discipline):** for each of the 5 remaining files, grep for `return \{('error'|"error")` returns AND grep for enclosing `def _handle_*` scope BEFORE labeling tool surface. Report routing-map table.

### Step 4 — Net-new engineering candidates for S2885 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2884 close — Cross-repo infra collision documentation.** If Chris's character-os hypothesis is confirmed at S2885 open, this pattern (sibling-repo Docker container captures shared pgbouncer / Redis / port) will recur. Ledger candidate + `feedback_post_travel_port_collision_triage` extension. Not yet at 2nd trigger — watch for corroboration.

2. **Carried from S2883 — Ledger #13 unified helper extraction (`td_error.py`)** — 4/6 adopter signal. Ready for extraction arc scheduling if two more slates add adopters.

3. **Carried from S2883 — Fold X test-authoring convention documentation** — 2nd trigger at S2883. Standardize on `TransactionTestCase` or ORM-boundary mocking for dispatcher-path tests requiring DB-visible state.

4. **Carried from S2882 — Fold Y `_authorize_staff` broad `except Exception:` narrowing** to `User.DoesNotExist` — behavior change, requires own SIGN.

5. **Carried from S2882 — PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers + Rigby zoom-out (b) refinement.

6. **Carried from S2881 — Grep-based CI audit metric** — count bare `return {'error':}` returns across `core/services/*.py`; fail CI on regression.

7. **Carried from S2880 — Fold A/B/C from S2880 post-code.** Fold C at 3rd trigger from S2883.

8. **Carried from S2878 — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger).

9. **Carried from S2877 — Schema-level dead-branch investigation** (1st trigger from S2875).

10. **Carried from S2877 — Schema-layer PA route smoke extension**.

11. **Carried from S2876 — #22.3 orthogonal-contract-axes resolution** (1st trigger).

12. **Carried from S2877 — #22.4 Rigby dispatcher-probe extension** (1st trigger).

13. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (1st trigger).

14. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger).

15. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger).

16. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

17. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr).

18. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

19. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

20. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

21. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

22. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

23. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

24. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

25. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.**

26. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

27. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

28. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

29. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

30. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

31. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

32. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

33. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

34. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

35. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

36. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

37. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

38. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

39. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

40. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → S2879 → S2880 → S2881 → S2882 → S2883 → **S2884 (cost_telemetry + newsletter file-completing)**. See A4 Constraints below.

41. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive. **Note S2884: character-os may be actively touching u-d-b infra (pgbouncer collision hypothesis) — if confirmed, this parked candidate becomes more urgent.**

### What's forbidden at S2885 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2884 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2884: cost_telemetry_tool + newsletter_tool now emit structured error codes (`unknown_action` / `invalid_params` / `not_found`). First file-completing wave in the S2876 sunset arc — TWO handler files EXIT the population in a single slate (agents.py 1→0, newsletter.py 7→0). A4 outreach substrate now has structured error semantics on LLM cost telemetry + newsletter authoring/validation/metrics surfaces, extending prior S2883 agent-diag + S2882 EXECUTION+AUTH + S2881 write-path + S2880 kill-switch + S2879 governance + focus_mode/celery/tenant/staleness coverage.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(qq) as ratified at S2883 close. **(rr) `cost_telemetry_tool` + `newsletter_tool` now emit concrete `error_code` from the 5-code taxonomy. First file-completing wave in the S2876 sunset arc completes 2 additional handler files. A4 messaging that references cost-telemetry or newsletter surfaces can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2884 close — what shipped (one PR + this docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3392** `65e4da587` — S2884 slate: agents_tool + newsletter_tool critical-slice structured error-envelope migration (4 files, +294/-25)
- **PR `<this docs cascade>`** — S2884 handoff + 00-START-NEXT-SESSION refresh (wrapper pin bump DEFERRED to S2885 open after pgbouncer unblock)

**Workspace canonical:** Rigby Tool Gap Ledger entry #24 **DEFERRED to S2885** — draft inlined in `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md` §S2884 close for persist-once-unblocked.

**Runtime impact:**
- Seventh wave (first file-completing shape) of real handler migrations in the S2876 backfill sunset arc.
- Legacy-file population S2883=8 files → **S2884=5 files** (agents.py + newsletter.py both EXIT).
- Sub-population count 184 → **176 bare-returns** across 5 remaining files.
- Regression suite grew from 200 → **207** (+8 S2884 rows − 1 retired S2877 backfill row).
- 8 sites no longer surface `error_code='legacy_error'`; consumers can key on 5-code taxonomy.
- No new helper introduced. No taxonomy expansion. No new PLAYBOOK amendment.
- Ledger #13 (`td_error.py` extraction) adopter count = 4/6 — 2 more adopters needed to trigger dedicated arc.

**Not shipped at S2884 close (deferred to S2885):**
- Live Rigby envelope verification (blocked by pgbouncer auth)
- Rigby Tool Gap Ledger entry #24 (blocked by same auth failure via ORM route)
- Wrapper pin bump / fresh S2885 conversation mint (needs DB)
- All prior deferred items from S2883/S2882/S2881/S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2884)

See:
- **S2884 handoff (current):** `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md`
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
