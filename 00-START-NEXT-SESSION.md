# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2886 CLOSE → td_handlers_core.py criticality-first slate shipped + 4-trigger /development/ bleed pattern confirmed + Ledger #13 6/6 adopter gate MET (2026-07-22; picks up as S2887) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2886 close).** S2886 was the ninth handler migration slate — **first criticality-first slate** after the S2885-close pivot retired file-completing as the default shape. **One PR shipped.** `td_handlers_core.py` 73 → 56 (17 sites migrated across `_handle_messaging` + `_handle_remember` + `_handle_session`). **Session infra work: 4 stacked faults, all legacy `/development/` bleed** (Redis cwd, Celery shebangs × 157, Daphne interpreter, all fixed). **Ledger #13 (`td_error.py` extraction) adopter gate MET at 6/6** — S2887 first-action opens the extraction arc.

- **PR #3396** `64ea19d1d` — S2886 slate (2 files, +510/-17)
  - **core cluster** (`_handle_messaging` L3844/L3849/L3875/L3877/L3979/L3986/L4018, `_handle_remember` L2224/L2230/L2331/L2345/L2365, `_handle_session` L4031/L4206/L4311/L4347/L4389): 17 sites across 3 handlers, 3 dispatched tool surfaces (`messaging_tool`, `remember_tool`, `session_tool`).
  - **Codes:** 3× `unknown_action`, 10× `invalid_params`, 2× `not_found`, 2× `permission_denied`. All 17 sites map cleanly to existing 5-code taxonomy — no broad-except, no `internal_error`, no new codes.
  - **Micro-decisions (Rigby SIGN F1/F2 AGREE):** L3986 `Thread not found or access denied` dual-semantic message PRESERVED as single `not_found` branch (splitting would leak thread-existence to non-participants — enumeration oracle). Test asserts `'access denied'` substring to lock the semantics contract.
  - **Helper-choice = uniform `_handler_error`** (file-local copy, same shape as S2879/S2882/S2883/S2884/S2885). **Ledger #13 adopter count now 6/6 — extraction gate MET.**
  - **Two folds re-fire at 2nd trigger, both Playbook amendment candidates:** Fold 1 (`TransactionTestCase` required for dispatcher-DB tests; predicted by Rigby in Q3 zoom-out and materialized in remember + messaging test classes), Fold 2 (shared-taxonomy branches within a single handler must be fortified via action string or message body substring — L3849 vs L3986 both `not_found`, L2230/L2331/L2345 all `invalid_params`).
  - **Combined regression:** S2879 → **S2886** + `test_zoom_out_tool_2780` = **100/100 pass**.
- **PR `<docs cascade>`** — S2886 handoff + this file refresh + wrapper pin bump (`pa-35b93928b15f4a9c` → S2887 mint) + `docs/INDEX.md` refresh.

### S2886 open — 4 stacked infra faults, all legacy `/development/` bleed (all resolved)

S2885 close deferred the `/development/` deletion decision to S2886 open. Chris had already removed the directory between sessions, but four long-running processes still bound to the deleted path blocked normal work until resolved:

1. **Redis MISCONF (RDB write disabled).** `redis-server` (PID 5417, started 2026-05-04) held phantom `cwd=/development/unified-donkey-betz` (unlinked inode). Mitigated via `redis-cli config set stop-writes-on-bgsave-error no`; clean restart deferred to S2886 close.
2. **Celery worker startup fail.** 157 `.venv/bin/*` scripts had shebangs pointing at `/development/` python. Fixed in-place via bulk `sed -i.bak` rewrite → `/Donkey_Betz/`.
3. **Daphne interpreter mismatch.** PID 16615 ran the `/development/` Python interpreter → task enqueue KeyError `process_pa_chat_task`. Killed + restarted from `/Donkey_Betz/`.
4. **Directory removal already done.** Pre-check confirmed `/development/unified-donkey-betz/` gone; parent `/development/` intact (51 other projects).

**Trigger count:** S2885 orphan Daphne = 1st; S2886 Redis + Celery + Daphne = 2nd/3rd/4th. Pattern retroactively ratified.

Full context: `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`.

## PRIOR SESSIONS — S2885 close + S2884 close + S2883 close + S2882 close + S2881 close

- **PR #3395** `706cfb2a5` — S2885 docs cascade. See `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`.
- **PR #3394** `5495736fb` — S2885 slate: `td_handlers_content.py` file-completing (2 files, +439/-13).
- **PR #3393** `43f40edd5` — S2884 docs cascade. See `docs/handoffs/SESSION_2884_AGENTS_NEWSLETTER_CRITICAL_SLICE.md`.
- **PR #3392** `65e4da587` — S2884 slate: agents_tool + newsletter_tool file-completing (4 files, +294/-25).
- **PR #3391** `444b28a5e` — S2883 docs cascade + wrapper pin bump.
- **PR #3390** `ca61c7725` — S2883 slate: agent-diag family critical-slice (2 files, +396/-10).
- **PR #3389** `de78ba609` — S2882 docs cascade + wrapper pin bump.
- **PR #3388** `377f39364` — S2882 close follow-on: `permission_denied` 5th taxonomy code + not-staff branch migration.
- **PR #3387** `6331c833e` — S2882 slate: `ops_tool` EXECUTION + AUTH critical-slice.

---

## S2887 open sequence

### Step 1 — `td_error.py` extraction arc (Ledger #13 gate MET at S2886 close)

**Adopter count trajectory:**
- Post-S2879: 1 (`td_handlers_ops.py`) → Post-S2883: 2 → Post-S2884: 4 → Post-S2885: 5 → **Post-S2886: 6 (gate MET)**

**Extraction plan:**
1. New file `core/services/td_error.py` — module containing the canonical `_handler_error` helper.
2. Update 6 adopter files' import blocks:
   ```python
   from core.services.td_error import _handler_error
   ```
3. Remove 6 file-local `_handler_error` copies (~28 lines × 6 files = ~168 lines removed).
4. Verify 100/100 regression suite still passes (S2879 → S2886 + zoom_out_tool_2780).
5. Ensure no circular imports (each adopter file already imports from `core.services.*`; a new leaf module should be safe).

**Expected diff:** ~30 lines added (new file + 6 import lines), ~168 lines removed. Net **~-140 lines**. Single PR, single review.

**Rigby SIGN Q1 (routing map):** verify at HEAD that the 6 copies are byte-identical (or differ only in the docstring's session-number attribution). If they diverge on shape (e.g., an adopter later added an extra field), the extraction needs a shape-reconciliation SIGN cycle before proceeding.

**Rigby SIGN Q_zoom_out:** Any concerns about naming (`td_error.py` vs `td_handler_error.py` vs `handler_envelope.py`)? Any adopters where the file-local docstring adds meaningful context that would be lost in a shared module?

### Step 2 — Playbook amendment candidates (both at 2nd trigger post-S2886)

1. **Fold 1 (2nd trigger): `TransactionTestCase` discipline for dispatcher-DB tests.** S2885 (1st) + S2886 (2nd). Rule shape: "Handler tests that require `setUp`-created ORM fixtures to be visible to `ToolDispatcher.execute_sync` MUST inherit from `TransactionTestCase`, not `TestCase`. Rationale: `execute_sync` spins up a fresh asyncio event loop; the handler's ORM connection doesn't see the test's wrapping transaction." Candidate slot: **PLAYBOOK-6.10.11** or **PLAYBOOK-7.4.5**.

2. **Fold 2 (2nd trigger): Shared-taxonomy branch fortification.** S2885 (1st) + S2886 (2nd). Rule shape: "When multiple return branches within a single handler emit the same `error_code`, the migrated-envelope test MUST assert either the distinguishing `action` field or a message-body substring to prevent false-pass on branch-crossing." Candidate slot: EXTENDS to **PLAYBOOK-6.10.9** or fresh sibling rule.

Both are ratifiable in a single MINOR amendment cycle (v0.9.0) — 2-rule slate at 2nd trigger each is well within the shape ratified for v0.7.0 (2-rule slate) and v0.8.0 (1-rule slate).

### Step 3 — Deferred S2886 close artifacts (housekeeping)

1. **Redis clean restart** — clears the phantom cwd fd, restores normal RDB persistence semantics, and reverts `stop-writes-on-bgsave-error` to default. Chris authorized at S2886 mid-session; deferred to end-of-session to avoid mid-slate worker disruption. Do at S2887 open OR verify done at S2886 close.
2. **`.env` `USE_PGBOUNCER` restoration triggers:** stay `=0` until cross-repo port ownership resolved (unchanged from S2885).
3. **`.venv/bin/activate*` (3 files)** still reference legacy `/development/` in `VIRTUAL_ENV` shell var. Only affects `source .venv/bin/activate` users; runtime processes unaffected. Fix optional.

### Step 4 — Net-new engineering candidates for S2887 (broader list)

Per `feedback_engineering_bias_over_audit`, list net-new first.

1. **NEW at S2886 close — `td_error.py` extraction arc.** Ledger #13 6/6 gate MET. S2887 first-action.

2. **NEW at S2886 close — Playbook v0.9.0 amendment cycle (2 rules).** Fold 1 + Fold 2 both at 2nd trigger. Ratify alongside or after S2887 extraction PR.

3. **NEW at S2886 close — Redis persistence hardening.** Consider `stop-writes-on-bgsave-error=no` as the persistent default for local-dev (`redis.conf` override), OR document as part of `feedback_post_travel_port_collision_triage` extension. 2 triggers observed (S2886 open + implicit S2882 dispatch backlog).

4. **NEW at S2886 close — `/development/` shebang audit hygiene.** After deleting a cross-checkout venv, sweep sibling checkouts' `.venv/bin/*` shebangs. Consider `make doctor` extension.

5. **Carried from S2885 close — `TransactionTestCase` requirement as first-class testing rule.** Fold 1 substrate. **2nd trigger at S2886.** Playbook amendment candidate (Step 2 above).

6. **Carried from S2885 close — false-pass discipline for shared-taxonomy branches.** Fold 2 substrate. **2nd trigger at S2886.** Playbook amendment candidate (Step 2 above).

7. **Carried from S2885 close — Cross-repo Docker infra collision documentation.** Character-os collision on `:5433` was 1st trigger; no 2nd trigger at S2886 (character-os not the issue). Hold.

8. **Carried from S2885 close — `.env` `PA_API_TOKEN` drift alarm.** Consider CI check that `.env` token matches DB token for the wrapper-owning user. Deferred.

9. **Carried from S2883 — Fold X test-authoring convention documentation** — 2nd trigger at S2883. **S2885 Fold 1 corroborated; S2886 Fold 1 = 2nd trigger.** Now part of Step 2 v0.9.0 amendment.

10. **Carried from S2882 — Fold Y `_authorize_staff` broad `except Exception:` narrowing** to `User.DoesNotExist` — behavior change, requires own SIGN.

11. **Carried from S2882 — PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers + Rigby zoom-out (b) refinement.

12. **Carried from S2881 — Grep-based CI audit metric** — count bare `return {'error':}` returns across `core/services/*.py`; fail CI on regression.

13. **Carried from S2880 — Fold A/B/C from S2880 post-code.** Fold C at 3rd trigger from S2883.

14. **Carried from S2878 — `_s2876_fake_tool` breadcrumb noise refinement** (1st trigger).

15. **Carried from S2877 — Schema-level dead-branch investigation** (1st trigger from S2875).

16. **Carried from S2877 — Schema-layer PA route smoke extension**.

17. **Carried from S2876 — #22.3 orthogonal-contract-axes resolution** (1st trigger).

18. **Carried from S2877 — #22.4 Rigby dispatcher-probe extension** (1st trigger).

19. **Carried from S2874 — `feedback_recycle_after_merge` extension for multi-checkout setups** (1st trigger). **S2885 corroborated (1st→2nd); S2886 corroborated via /development/ 4-trigger pattern. Now 3rd trigger. Chris deleted /development/ so pattern may not re-fire, but feedback rule extension candidate.**

20. **Carried from S2873 — `orm_inspect_tool` JSONField type predicate** (1st trigger).

21. **Carried from S2873 — kalshi-only distribution on canonical SpiderData** (1st trigger).

22. **Carried from S2873 — "post-allowlist smoke checklist" UX pattern** (1st trigger).

23. **Ledger #5 — schema/handler drift detection lint / CI wiring** (~2 hr).

24. **Carried from S2872 — Category B cosmetic `raw_data_dict` migration** (~30 min).

25. **Ledger #16 — close-ceremony twin-mirror enforcement gap** (S2863).

26. **Carried — Exemption-list telemetry** (Rigby zoom-out from S2868 slate #1, 1st trigger).

27. **Carried — Stale-cleared row GC** (Rigby zoom-out from S2868 slate #1).

28. **Carried — `group_key_note` UX hint on `count_by`** (S2867 Q2 fold, 1st trigger).

29. **Carried — High-cardinality guardrail on `count_by`** (S2867 Q5 fold, 1st trigger).

30. **Carried — Per-model `allowed_fields` explicit allowlist on `orm_inspect_tool`** (S2866 fold, 1st trigger).

31. **Carried — Promote S2862 Q5.a bimodal-collector fold to tracked spec_backlog entry.**

32. **Carried — Codify "verify at persisted source of truth" as SIGN discipline** (Playbook amendment candidate, 1st trigger only).

33. **Carried — Provider-specific composite additions.** Reactive; watch for new integrations.

34. **Carried — `simulate_enforcement` auto-clear-after-N-seconds** (S2857 fold).

35. **Carried — `enforcement_action_types` shared constant** (S2856 Q5b, 1st trigger).

36. **Carried — `actor_user_id` as first-class column on `AutopilotAction`** (S2856 Q5a, MIGRATION required).

37. **Carried — `EnforcementContext` dataclass consolidation** (S2857 Q5, 1st trigger).

38. **Carried — `list_caps include_defaults=true` remaining perf costs** (S2858, 1st trigger).

39. **Carried — Second-trigger candidate for expanding `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`** (S2859+S2868 cycle observed).

40. **Carried — Q5.3 fold from S2859 SIGN — "diagnostic == effectively hidden in workspace UI"**.

41. **Carried — Fold C from S2861 close: shared JSONField projection helper**.

42. **Carried — Fold D from S2861 close: operator-surface discoverability for advanced PA-tool params**.

43. **Carried — openmeteo → SignalCluster drop (fold-carry from S2862)** — product decision.

44. **Carried — Middleware `log_injected_params` spec candidate** (S2870 Q6 zoom-out fold, 1st trigger).

45. **Carried — Phase 2B pricing arc (only if reconciliation trigger surfaces)** — 4 deferred items from S2855.

46. **Carried — A4 warm-up under ratified constraints** — S2846 6-line block still in force. A4 capabilities extended at S2875 → S2876 → S2877 → S2878 → S2879 → S2880 → S2881 → S2882 → S2883 → S2884 → S2885 → **S2886 (core.py criticality-first + 4-trigger /development/ pattern resolved)**. See A4 Constraints below.

47. **Carried — Character-os Rigby integration (5-gap analysis from S2872 mid-session, D6 moratorium hold)** — parked; unlock requires Chris directive.

### What's forbidden at S2887 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

### What's queued but deferred (do NOT open unless Chris directs)

- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind wedge execution
- W2 #1 UX polish / #2b cap templates / #2c ownership transfer — pending Chris re-slate
- W2-2b bounded attribution expansion — Chris explicitly skipped at S2849
- `requested_model_id` field split on `LLMCallLog` — migration required
- `was_policy_reroute` field on `LLMCallLog` — migration required
- Bulk `workspace_budget_tool` operations (S2847 ledger candidate)

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2886 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2886: `core.py` user-identity handlers now emit structured error codes across 3 dispatched tool surfaces (`messaging_tool`, `remember_tool`, `session_tool`). First criticality-first slate after S2885-close pivot; targets the highest-criticality clusters (auth + write-path + user-identity boundary). A4 outreach substrate now has structured error semantics on in-app messaging, persistent user memory, and conversation lifecycle surfaces, extending prior S2885 content_tool + S2884 cost_telemetry+newsletter + S2883 agent-diag + S2882 EXECUTION+AUTH + S2881 write-path + S2880 kill-switch + S2879 governance coverage.**
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(ss) as ratified at S2885 close. **(tt) `messaging_tool` + `remember_tool` + `session_tool` now emit concrete `error_code` from the 5-code taxonomy including `permission_denied` on unauthenticated write-paths. First criticality-first slate in the S2876 sunset arc — 17 sites migrated across 3 handlers. A4 messaging that references in-app DMs, user memory persistence, or conversation session lifecycle can rely on structured error semantics for downstream integrations.**
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## S2886 close — what shipped (one slate PR + this docs cascade)

**Repo canonical (Claude-authored):**
- **PR #3396** `64ea19d1d` — S2886 slate: `td_handlers_core.py` criticality-first structured error-envelope migration (2 files, +510/-17)
- **PR `<this docs cascade>`** — S2886 handoff + 00-START-NEXT-SESSION refresh + wrapper pin bump for S2887 open + `docs/INDEX.md` refresh

**Workspace canonical (Rigby-authored at S2886 close):**
- **Content mirror** — S2886 slate substrate → workspace `b4503364-2573-4401-9e28-61a739e0ce50`, category `initiative_phase_doc`
- **Ratification envelope** — S2886 SIGN F1/F2 AGREE + Q3-Q5 verdicts + Chris D-verdict → workspace `b4503364-2573-4401-9e28-61a739e0ce50`, category `governance`, deliverable_type `ratification_record`
- **Rigby Tool Gap Ledger entry #25** (queued) — 4-trigger `/development/` bleed pattern documentation, appended to deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`.

**Runtime impact:**
- Ninth wave (first criticality-first shape after S2885-close pivot) of real handler migrations in the S2876 backfill sunset arc.
- Legacy-file population unchanged at **4 files** (`core.py=56`, `gateway.py=57`, `railway.py=18`, `codejobs.py=15`).
- Sub-population count **163 → 146 bare-returns** across 4 files.
- Combined regression suite S2879 → **S2886** + zoom_out_tool_2780: **100/100 pass**.
- 17 sites no longer surface as bare `{'error': ...}`; consumers can key on 5-code taxonomy.
- No new helper introduced. No taxonomy expansion. No new PLAYBOOK amendment shipped (2 candidates queued for v0.9.0).
- **Ledger #13 (`td_error.py` extraction) adopter count = 6/6 — extraction gate MET.** S2887 first-action opens the extraction arc.

**Session infra work resolved (not shipped as PR):**
- 4 stacked infra faults from legacy `/development/` checkout (Redis cwd, Celery shebangs × 157, Daphne interpreter, all mitigated).
- Redis clean restart deferred to S2886 close (phantom cwd fd from long-running process).
- 157 `.venv/bin/*` shebangs bulk-rewritten in-place.

**S2886 pivot from S2885 confirmed:** file-completing retired as the default shape; criticality-first grep is now the standard for the remaining 4 files.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2886)

See:
- **S2886 handoff (current):** `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`
- **S2885 handoff:** `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md`
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
