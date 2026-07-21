# Session 2871 — LegacySpiderData raw_data_dict property + orm_inspect allowlist extension + repo_tool conditional timeout

**Date:** 2026-07-21
**Prior session:** S2870 (signal_clusters injection hardening + spider_data_bridge list-form guard)
**Next session:** S2872
**Slate:** Rigby Tool Gap Ledger #22 + #23 + #24, grouped (all three surfaced mid-S2870; all three harden PA tool-surface reliability). Shipped as single PR.

**Merge commit (main):**
- `2c542fd4d` PR #3363 — S2871 slate (15 files, +366/-43)

**D6 moratorium status:** still in force — pure engineering execution against the Rigby Tool Gap Ledger, zero strategic discovery.

---

## What shipped

### PR #3363 — S2871 slate (Ledger #22 + #23 + #24, grouped)

All three entries surfaced mid-S2870 discovery — grouped because all three harden PA tool-surface reliability with disjoint code paths.

#### #22 — LegacySpiderData.raw_data_dict property (promoted from S2870 _safe_dict)

**Root cause:** `LegacySpiderData.raw_data` is `JSONField()` with no default; can hold dict-shaped (usual) or list-shaped (S2869 fixture 6) or null. Any reader doing `instance.raw_data.get(...)` on a list-form row raises `AttributeError`. S2870 shipped a file-local `_safe_dict` helper in `core/learning_bridges/spider_data_bridge.py` for the 5 immediate crash sites but deferred the wider sweep.

**Fix (promoted to model property per Rigby pre-code SIGN mitigation):**

`core/models_unified_system.py:3800-3811`:
```python
@property
def raw_data_dict(self) -> dict:
    """Return ``raw_data`` guaranteed as a dict — ``{}`` when the row
    holds a list, ``None``, or any non-dict JSON."""
    return self.raw_data if isinstance(self.raw_data, dict) else {}
```

The model's own `get_searchable_text()` method (line 3813-3819) was itself a crash site (called `self.raw_data.get(...)` on line 3806 — the model would crash on its own instance for list-form rows). Migrated to `self.raw_data_dict`.

**Callsite migration — 16 external sites across 12 files:**
- `core/services/proactive_intelligence.py:315,346,378,412` (4)
- `core/views_spider_feed.py:40, 464` (2)
- `core/tasks_financial.py:750, 971, 1230, 1339` (4)
- `ai_core/intelligence/consumers.py:1873` (1)
- `core/views_spider_intelligence.py:424, 503, 1170, 1599` (4)
- `core/services/workflow_engine.py:604` (1)
- `core/tasks_conversations.py:2062` (1)
- `core/signals/trigger_signals.py:107` (1)
- `core/tasks.py:5410, 5516` (2)
- `core/views_stock_intelligence.py:119, 143, 512, 726` (4)

Migration pattern: `raw = X.raw_data or {}` → `raw = X.raw_data_dict` (idiomatic, no `or {}` needed since property returns `{}` guaranteed).

**Broader sweep deferred to Ledger #22b:** ~30 additional callsites across agent files (`core/agents/*`), service files (`core/services/model_registry.py`, `smart_trending_service.py`, `autonomous_loop.py`, `living_project_service.py`), `core/tasks_ops.py`, `core/tasks_misc.py`, `core/views_odds_sports.py`, `core/views_project_intelligence.py`, `core/models_situation_triggers.py`. Not currently crash-triggered (Rigby post-code Q3 last-5-row sample was dict-form only). Wait for live crash evidence OR second-file trigger to promote.

#### #23 — LegacySpiderData added to orm_inspect_tool allowlist

**Fix at** `core/services/td_handlers_agents.py:754-761`:
```python
'LegacySpiderData': {
    'app_label': 'core', 'sensitive': False,
    'expensive_text_fields': ('embedding_text',),
},
```

- `sensitive=False`: spider data is public web content
- `expensive_text_fields=('embedding_text',)`: TextField holds ~4KB per row; blocked from contains/icontains lookups per S2866 pre-code SIGN Q3 policy
- No schema update needed — `orm_inspect_tool.model` is free-text string with runtime allowlist check (no enum on schema side)

**Live post-code verified:**
- `describe_model` returns 15 fields including `raw_data`, `processed_data`, `embedding_text`
- `count_by field='spider_name'` returns `total_matching=15610`, `group_count=51` (top: `theodds=615`, `legislation=581`, `remoteok=573`)
- `filter filter_kwargs={'data_type':'sports_odds'}` returns `total_matching=643`
- `filter filter_kwargs={'embedding_text__icontains':'anything'}` rejected with expensive-field policy error

#### #24 — repo_tool conditional wall-clock timeout (Rigby's Option A)

**Original proposal was blanket bump 10s→30s + 5s→10s.** Rigby F-BLOCKING-DISAGREE on the blanket bump — a 30s blocking PA tool call is a meaningful UX degradation; making the slow path the new normal is the wrong trade.

**Option A (Rigby's alternative, adopted):**

In `core/services/td_handlers_gateway.py`:
- Line 226-241: search branch now computes `_is_narrowed = bool(search_path) or bool(file_type)`
- If narrowed: `_list_timeout=30, _per_file_timeout=10` (heavy-verification budget for opted-in queries)
- If repo-wide: `_list_timeout=10, _per_file_timeout=5` (tight cap preserved)
- Line 291-311: `TimeoutExpired` handler returns structured error:
  - Repo-wide timeout: `error_code='search_timeout_repo_wide'`, `timeout_seconds=10`, `narrowing_hint` with `suggested_paths=['core/', 'ai_core/', 'intelligence/', 'frontend/src/']`
  - Narrowed timeout: `error_code='search_timeout_narrowed'`, `timeout_seconds=30`

**Live post-code verified:**
- Repo-wide `query='LegacySpiderData'` → timed out with expected `error_code='search_timeout_repo_wide'` + `suggested_paths`
- Narrowed `query='LegacySpiderData' path='core/'` → completed normally, `files_matched=120`, `sample_matches` returned

---

## Discovery arc — 2 SIGN cycles

### Pre-code SIGN

Rigby routed all three components:

- **#22 F-AGREE with mitigations:** (a) docstring on property clarifying "prefer for reads", (b) migrate `get_searchable_text` to use property, (c) standardize on `raw_data_dict` for read paths, (d) no lint rule yet. Rigby noted Q1 (list-form prevalence) blocked pending #23 merge. Independently verified `item`/`entry` at cited sites are LegacySpiderData instances (grep + read_file evidence).

- **#23 F-AGREE:** independently verified `orm_inspect_tool` currently rejects LegacySpiderData with `"model 'LegacySpiderData' not in allowlist"` + confirmed current 8-model allowlist. Q3 wish-list: SpiderData (canonical) for future addition. Q4: `expensive_text_fields=('embedding_text',)` correct; sensitive=False OK since public web content.

- **#24 F-BLOCKING-DISAGREE (as originally proposed):** blanket 30s bump = UX degradation; PA tool calls block Rigby's turn until they return. Alternative proposed (Option A adopted): conditional timeout based on narrowing (`path`/`file_type`); repo-wide keeps tight cap + returns structured error with narrowing hint.

### Post-code SIGN (live verification, all F-AGREE)

- #22 Q1-Q3: describe_model + count_by + filter all work; last-5-row sample is dict-form only (no live list-form crash confirmed, so #22 is defense-in-depth against the S2869 fixture-6 class + future ingestion, not a currently-crashing bug fix)
- #23 Q4: `list_models` returns 9 models including LegacySpiderData
- #24 Q5-Q6: repo-wide timed out with expected structured error; narrowed completed normally

### Zoom-out folds (Q7)

- **(a)** New coupling risk: minimal and acceptable — #22/#23 together increase reliance on ORM inspection for truth (good); #24 is the escape hatch when code-grep would otherwise stall
- **(b)** New allowlist candidates surfaced: SpiderData (canonical), Opportunity (Rigby's second pick) — added to ledger wish-list, not shipped this pass
- **(c)** Ledger #22b (wider standardization sweep) can wait absent live crash evidence

---

## Working loop observations at S2871

- **`feedback_verify_rigby_tool_runs_before_trusting_sign`** fired 2x — both pre-code and post-code SIGN cycles grounded in Rigby tool_runs evidence (grep/read_file for verification of model provenance; live PA dispatches for post-code F-VERIFY).
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — did NOT fire this session (unlike S2870). #23 shipped removes the previous constraint (LegacySpiderData now inspectable via orm_inspect); the class of blocker that surfaced #23 no longer exists for spider-data verification.
- **`feedback_zoom_out_ask_per_rigby_sign`** yielded 3 usable folds: (1) property mitigations + get_searchable_text self-migration; (2) Option A adoption for #24 (biggest fold — reshaped the design); (3) SpiderData allowlist future candidate + #22b sweep priority.
- **`feedback_claude_directs_rigby_then_verifies`** applied: Claude wrote code + tests, Rigby executed post-merge F-VERIFY dispatches. Ledger update routed to Rigby per `feedback_rigby_writes_workspace_deliverables`.
- **`feedback_gh_pr_merge_admin_until_billing_fixed`** applied: `gh pr merge --admin --squash --delete-branch 3363`.
- **`feedback_recycle_after_merge` (PLAYBOOK-7.4.4)** applied: `make recycle-all` immediately post-merge.
- **`feedback_claude_rigby_agree_first_chris_yes_no`** applied: F-BLOCKING on #24 resolved between Claude+Rigby (adopted Option A) before Chris; presented Chris one recommendation.

**No candidate lessons for Playbook amendment this session** — Option A adoption was straightforward mitigation, not novel governance methodology.

---

## Rigby Tool Gap Ledger updates (via Rigby PA)

Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

- **#22** → shipped_in_pr_S2871 (PR #3363, commit 2c542fd4d)
- **#23** → shipped_in_pr_S2871 (PR #3363, commit 2c542fd4d)
- **#24** → shipped_in_pr_S2871 (PR #3363, commit 2c542fd4d)
- **NEW #22b** — broader raw_data_dict standardization sweep (~30 sites across agent/service files) — low priority, defer until live crash evidence
- **NEW allowlist wish-list** — SpiderData (Rigby's original), Opportunity (Rigby's second pick)

Rigby confirmed via `deliverable_tool.append` — 2,660 chars appended; total content length now 18,681 chars.

---

## Session pin lifecycle

Pin `pa-4aee1a3ab24d42c6` (labeled `s2871-ledger-22-23-24-tool-surface-triple`) retires at S2871 close.

Fresh mint required at S2872 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## Not shipped at S2871 (deferred to S2872 or later)

- **Ledger #22b** — broader `raw_data_dict` standardization sweep across agent + service + tasks_ops/misc + views_odds_sports + models_situation_triggers files (~30 sites). Waiting on live crash evidence or second-file trigger.
- **SpiderData** (canonical, non-legacy) allowlist addition — Rigby wish-list from S2870+S2871 SIGN cycles
- **Opportunity** allowlist addition — Rigby's second pick
- **Ledger #5** — schema/handler drift CI enforcement wiring (still open from S2869 handoff)
- **Ledger #16** — close-ceremony twin-mirror enforcement gap (still open)
- All prior S2867/S2866/S2862/S2861/etc carried items — unchanged.

---

## Substrate verification

- Local tests: 17/17 pass on `core.tests.test_s2871_ledger_22_23_24_tool_surface_triple`; 18/18 pass on S2870 regression; 14/14 pass on S2869 regression (49/49 total in the S2869→S2871 test suite)
- `check_pa_tool_drift` — no new drift on `orm_inspect_tool` or `repo_tool` (pre-existing drift on other tools unchanged)
- `make celery-recycle` — twice: pre-Rigby-SIGN + post-merge (per PLAYBOOK-7.4.4)
- Live Rigby dispatches verified all three components: orm_inspect_tool describe_model + count_by + filter + list_models; repo_tool search repo-wide + narrowed

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2871)

See:
- **S2871 handoff (current):** `docs/handoffs/SESSION_2871_RAW_DATA_DICT_PROPERTY_ORM_INSPECT_LEGACY_SPIDER_DATA_CONDITIONAL_TIMEOUT.md`
- **S2870 handoff:** `docs/handoffs/SESSION_2870_INJECTION_HARDENING_AND_RAW_DATA_GUARD.md`
- **S2869 handoff:** `docs/handoffs/SESSION_2869_SPIDER_SEARCH_PREVIEW_AND_SIGNAL_CLUSTERS_MULTISOURCE.md`
- **S2868 handoff:** `docs/handoffs/SESSION_2868_DELIVERABLE_DIAGNOSTIC_AND_SPIDER_STATUS_PAGINATION.md`
- **A4↔A1 ratification:** `00-START-NEXT-SESSION.md` §A4 Constraints
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`

For older session history (S1-S2845), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
