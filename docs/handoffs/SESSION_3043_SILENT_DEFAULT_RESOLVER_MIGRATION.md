# Session 3043 — Silent-default resolver migration (T1 Spec v1 Phase 2 shipped)

**Closed:** 2026-07-30
**HEAD at close:** `_TBD_close_` (post-docs-cascade PR)
**Session shape:** Feature session. Discharged S3042 T1 Spec v1 Phase 2 in one PR (#3785, commit `24b27db9d`). Cycle 1A verify-before-build at Phase 2 kickoff caught 4 of T1 v1's 7 targeted sites were mis-scoped; Rigby A1 SIGN + Chris D-verdict ratified the reduction to 3 real silent-default resolvers + substrate hardening + guardrail lint. Rigby A2 SIGN discharged the PLAYBOOK-7.7.5 class-scoped sweep post-code.

---

## What shipped

### PR #3785 — `feat(s3043): silent-default resolver migration — T1 Spec v1 Phase 2` (commit `24b27db9d`)

**6 files, +355/-14 LOC.**

**Substrate hardening:**
- `core/services/platform_config.py` — added `PrimaryWorkspaceUnavailable` exception class; `get_primary_workspace()` now raises when a configured workspace id resolves but the underlying row cannot be fetched. Preserves `None`-return for the "no config at all" case; the two states are distinguishable.

**Site migrations (3):**
- `core/services/operation_recorder.py:148` — wraps `get_primary_workspace()` in `try/except PrimaryWorkspaceUnavailable` → preserves fire-and-forget "op dropped" contract.
- `core/services/deliverable_envelope.py:243` — wraps `get_primary_workspace()` → preserves "UNSCOPED orphan" degradation with explicit misconfiguration log.
- `core/services/deliverable_workspace_resolver.py:149` — Priority 6 fallback now calls `get_primary_workspace()`; preserves `source='global_active'` tag on success.

**Guardrail lint:**
- `scripts/verify_repo_guardrails.py` — new `check_silent_default_workspace_resolvers()` scans `core/**/*.py` for shape signature `ProjectWorkspace.objects.filter(is_active=True)` (comment-line exclusion) and fails strict mode on hits outside the allowlist. 7 allowlisted hits with documented reasons: `heart.py:383` (metric), `skin.py:93` (metric), `backfill_media_workspaces.py:50` (per-user iterator), `tasks.py:12560` (rescan iterator over ALL), `td_handlers_codejobs.py:481` (per-user resolver), `workspace_manager.py:1938` (bulk deactivate write), `agent_router.py:2132` (safety-net fallback).

**Tests (3 per T1 v1 §Test discipline):**
- `tests/services/test_platform_config_fail_fast.py` — get_primary_workspace fail-fast + get_primary_workspace None-when-unconfigured + operation_recorder graceful-drop. All 3 pass in 0.05s.

### Deliverables landed in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)

| id | title | type | status |
|---|---|---|---|
| `e8bb81d1-db81-44af-954f-b26b1a89aafc` | **T1 Spec v2 delta — S3042/Q1 Silent-Default Resolver Migration (Phase 2 scope reduction)** | t1_spec | ready (created S3043) |

Discharges T1 Spec v1 (`bffa6df1`). Documents the Cycle 1A scope reduction with per-site evidence, Rigby A1+A2 SIGN provenance, Fold classifications, and PLAYBOOK-7.7.5 sweep evidence.

### Cycle 1A verify-before-build scope reduction

**28th consecutive session.** T1 v1 Phase 2 kickoff class-wide grep for `ProjectWorkspace.objects.filter(is_active=True)` in `core/**` returned 10 hits. Per-site file:line reads showed only 3 are silent-default resolvers matching T1 v1's Substantive Intent. Details:

| # | Site | T1 v1 verdict | T1 v2 verdict | Reason |
|---|---|---|---|---|
| 1 | `operation_recorder.py:148` | migrate | ✅ migrated | silent-default resolver |
| 2 | `deliverable_envelope.py:243` | migrate | ✅ migrated | silent-default resolver |
| 3 | `deliverable_workspace_resolver.py:149` | migrate | ✅ migrated | silent-default resolver (Priority 6) |
| 4 | `workspace_manager.py:1938` | migrate | ❌ allowlisted | bulk deactivate write during `set_active_workspace` |
| 5 | `tasks.py:12560` | migrate | ❌ allowlisted | `rescan_active_workspaces` iterates ALL active workspaces |
| 6 | `td_handlers_codejobs.py:481` | migrate | ❌ allowlisted | per-user workspace resolver (filtered by `user_id`) |
| 7 | `skin.py` | migrate | ❌ allowlisted (line :93) | observability `.count()` only; T1 v1 listed no specific line |
| 8 | `heart.py:383` | out of scope | ❌ allowlisted | observability metric (unchanged) |
| 9 | `backfill_media_workspaces.py:50` | out of scope | ❌ allowlisted | per-user iterator (unchanged) |
| 10 | `agent_router.py:2131-2132` | already migrated | 2132 allowlisted; 2131 doesn't match strict shape | 2132 is safety-net fallback |

Two consecutive sessions (S3041 + S3042 + S3043) where verify-before-build catch produced a materially cheaper / more correct plan — S3042 caught pre-existing substrate, S3043 caught scope mis-classification.

### Post-merge verification

- **`make recycle-all`** — clean recycle recorded (sha=`24b27db9d959`, surviving=none). Redis + Daphne + 5 Celery workers + beat all restarted.
- **Rigby PA path** — `platform_config_tool.overview` round-trip successful post-recycle.
- **Direct substrate verify** — `python manage.py shell` → `get_primary_workspace()` returns `Donkey Betz (id=b4503364…)` cleanly. Fail-fast branch not exercised (no misconfiguration).

---

## Signals gathered

### Cycle 1A verify-before-build caught scope mis-classification

Second consecutive session where the Cycle 1A discipline paid off in the same arc — S3042 caught pre-existing substrate (`platform_config.get_primary_workspace()` shipped Session 910), S3043 caught scope mis-classification (4 of 7 T1 v1 targets weren't actually silent-default resolvers). Forcing migration on the 4 mis-scoped sites would have introduced regressions (bulk-write becoming single-write, iterator scanning 1 workspace instead of all, per-user resolver ignoring user context).

### PLAYBOOK-7.7.5 class-scoped A2 sweep — first cross-session in-wild application

S3033 codified PLAYBOOK-7.7.5 (class-scoped mandatory A2 sweep for drift/hardening intents). S3043 is the first arc where the sweep was **pre-authored at spec time** (T1 v2 delta §PLAYBOOK-7.7.5) rather than retroactively at A2 SIGN. Rigby's A2 SIGN discharged all 4 sweep dimensions with tool_runs, confirming the pre-authored evidence.

### Deliverable diagnostic surface confirmed resolved

Third `t1_spec` type deliverable created this arc (`bffa6df1` + `200b1b38` in S3042, `e8bb81d1` in S3043) — none tripped the `missing_initiative_id` diagnostic. `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` (S2753 finding) can be reconsidered as CLOSED pending a formal check.

### Rigby SIGN evidence discipline sustained

Both SIGN cycles (A1 + A2) returned substantive tool_runs — 8 + 10 respectively across `repo_tool.search`, `repo_tool.read_file`, cross-file verification. Zero rubber-stamp signals. `feedback_verify_rigby_tool_runs_before_trusting_sign` invariant held across 30+ consecutive SIGN cycles now.

### Fold 2 `future_trigger` — agent_router.py:2132 silent fallback

A2 SIGN surfaced that `core/agent_router.py:2131-2132` still uses `ProjectWorkspace.objects.filter(is_active=True).first()` as a safety-net fallback AFTER `get_primary_workspace()` fails. This is intentionally allowlisted (explicit fallback pattern) but remains a residual silent-default drift vector if the platform ever operates with `platform_config` misconfigured. **1st trigger recorded. Watch for 2nd in future arcs before opening a T2 spec.**

### Comment-line exclusion in guardrail lint

Initial guardrail smoke-test flagged the migration comment on `deliverable_workspace_resolver.py:146` as an unexpected hit — the migration comment literally embeds the shape signature for documentation ("migrated from `ProjectWorkspace.objects.filter(is_active=True)…`"). Same-envelope fix: guardrail now strips inline comments before regex match (`line.split("#", 1)[0]`). A2 SIGN Fold 1 `same_pr_mitigatable` → discharged.

---

## Non-goals of this session (deferred, not dropped)

- **Q2 (Initiative autonomy)** — deferred per Spine Contract v1 §6 until Q1/Q3/Q4 implementation ships
- **Workspace UI redo (Arc C)** — deferred until Phase 2 substrate closes
- **Frontend event instrumentation** (`workspace_home_opened` / `deliverables_list_opened` / `initiative_list_opened`) — validation follow-up per Spine Contract v1 §1
- **`chris-personal` orphan-initiative cleanup pass** — Spine Contract v1 §4, tracked separately
- **Odds API re-enable / betting brief silent-success bug** — carry-forward from S3040
- **A6 Phase 2 / D10 Phase 2 / S9 producer follow-up** — WAIT-STATE
- **T2 spec for `agent_router.py:2132` silent fallback** — 1st trigger recorded; requires 2nd before opening

---

## SIGN provenance (task IDs)

| Cycle | Task ID | Purpose |
|---|---|---|
| Deliverable read | (implicit in bash tool_result) | Fetch T1 v1 + Spine Contract v1 full body |
| A1 SIGN | `34c10716-30c3-4a67-859b-8e97b0810cc7` | Cycle 1A verify per-site (7 sites) + fail-fast callers (D2) + guardrail allowlist review (D3) + zoom-out (D4) + folds (D5); 8 tool_runs |
| T1 v2 delta mirror | `84e9df80-df4d-4e4a-a779-17b11d4f456a` | Create deliverable `e8bb81d1` |
| A2 SIGN | `1397f648-3726-4a4b-969c-3229bc56873c` | PLAYBOOK-7.7.5 class-scoped sweep across 4 dimensions + zoom-out; 10 tool_runs |
| Post-merge verify | `75a577df-7a4a-4a36-bc12-17449ba4f677` | Rigby PA path smoke post-recycle |

Chris D-verdicts (2 in-terminal): (a) approve Cycle 1A reduction to 3 sites + guardrail + tests + T1 v2 delta doc; (b) ship it — post-A2-SIGN ratify.

---

## Cross-cutting workflow references

- **Playbook version:** v0.11.0 (unchanged this session — no [GR] rule firings)
- **Spec→ship contract (PLAYBOOK-7.7.1):** Phase 2-7 shipped for T1; Phases 8-9 (Chris D-verdict + ship) discharged
- **SIGN evidence discipline (PLAYBOOK-7.7.2):** 2 cycles, all substantive tool_runs, zero rubber-stamp
- **Chris-facing decision framing (PLAYBOOK-7.7.3):** 2 mid-flight applications (Cycle 1A reduction + D-verdict)
- **Class-scoped A2 sweep (PLAYBOOK-7.7.5):** pre-authored in T1 v2 delta §PLAYBOOK-7.7.5; discharged via A2 SIGN with all 4 dimensions covered by tool_runs
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` executed post-merge (clean, sha=`24b27db9d959`)
- **Verify-before-build (Cycle 1A):** **28th consecutive session**

---

## S3044 first-action candidates

**No mandatory first-action.** T1 Spec v1 Phase 2 discharged; the S3042 arc's Q1 code component is now complete. Chris chooses direction:

1. **Q3 implementation** — Spine Contract v1 §1 "deliverable = standalone publish-control unit" surfaces (frontend instrumentation, deliverable authoring UI, publish_intent enum audit)
2. **Q4 implementation** — Spine Contract v1 §§1+3 "Deliverables home spine + workspace-first default" — Workspace UI redo (Arc C)
3. **`chris-personal` cleanup pass** — archive 30 orphan initiatives, set `target_workspace` on 3 NULL initiatives
4. **PA tools sweep resume** — Slice 6 (`td_handlers_content.py`, 6 untested tools) per `project_s2935_resume_pa_tools_sweep`
5. **Row 161 substrate arc** — resume per `project_row_161_substrate_arc_opened_s2900`
6. **Something else** — Chris directive

---

## Wrapper pin note

Active PA conversation pin at S3043 close is minted by `session_lifecycle close`. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.
