# Session 2873 — orm_inspect_tool allowlist +2 (Ledger wish-list #2 + #3)

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-212927a27cf34515` (labeled `s2873-spider-data-opportunity-orm-inspect`)
**Slate label:** S2873 — Rigby Tool Gap Ledger wish-list #2 + #3
**PR shipped:** #3367 (SHA `8423e946b`)
**Combined regression suite:** S2869 + S2870 + S2871 + S2872 + S2873 → **73/73 pass**
**Moratorium status:** D6 in force (no new strategic discovery arcs)

---

## What shipped

Extended `orm_inspect_tool` `_MODEL_POLICIES` from 9 to 11 models. Both entries were carried forward from S2871 as Ledger wish-list items.

### Entry #10 — `persistence.SpiderData`

- **Policy:** `app_label='persistence'`, `sensitive=False`, `expensive_text_fields=('content', 'raw_html')`
- **Rationale:** 116,800+ rows; canonical spider-persistence model. Same public-web-content sensitivity level as `LegacySpiderData`. `content` (article bodies) + `raw_html` (full page source) can each exceed 10KB per row, so both blocked from `contains`/`icontains` lookups.
- **Location:** `core/services/td_handlers_agents.py:764-770`

### Entry #11 — `core.Opportunity`

- **Policy:** `app_label='core'`, `sensitive=False`, `expensive_text_fields=('description',)`
- **Rationale:** 2,631+ rows; revenue-side opportunities model. User-facing scoring/metadata. `description` is the only `TextField` on the model. FKs (user, workspace, spider_data, project, recommended_by) emit as `*_id` per existing FK-attname pattern. Single-tenant pre-prod context (per `project_single_user_pre_prod_operating_context`) means no `workspace_id` gating required at v1.
- **Location:** `core/services/td_handlers_agents.py:772-780`

### Test coverage

New test file `core/tests/test_s2873_orm_inspect_spider_data_opportunity.py` — 13 tests across 2 test classes (`OrmInspectToolSpiderDataAllowlistTests` × 7, `OrmInspectToolOpportunityAllowlistTests` × 6).

Coverage per model: `list_models`, `describe_model`, `get by pk`, `filter`, `count_by`, expensive-field `contains` rejection guard.

---

## Discovery arc — 2 SIGN cycles

### Pre-code SIGN

**F-AGREE ×5** — all 5 questions verified via tool_runs by Rigby.

- Q1: canonical model confirmed at `persistence/models.py:611` via `repo_tool.search`.
- Q2: `password|token|secret|api_key|credential` search returned 0 matches in both target files (`persistence/models.py` + `core/models_unified_system.py`) — `sensitive=False` grounded.
- Q3: `SpiderData` TextField enumeration bounded to `content` + `raw_html` after read of `persistence/models.py` lines 560-920 (Opportunity model enumeration was Claude's responsibility since `core/models_unified_system.py` is 760KB > `repo_tool.read_file` cap).
- Q4: no new tenant boundary concerns for FK chain (allowlist gate still enforces access).
- Q5 (zoom-out): "no folds — proceed as designed" at 11 models.

### Post-code SIGN (live tool_runs after `make celery-recycle`)

**F-AGREE ×5** (Q3 with sub-DISAGREE on data-shape claim).

- Q1 F-AGREE: `list_models` returns 11 entries; both new additions present.
- Q2 F-AGREE: `describe_model SpiderData` returned `app_label='persistence'` + `expensive_text_fields=['content', 'raw_html']`.
- Q3 F-AGREE (with note): `count_by SpiderData spider_name` returned `total_matching=117,000` — live data. **Sub-DISAGREE** on Claude's "multiple distinct spider_names" claim: all 117,000 rows attributed to `kalshi` alone.
- Q4 F-AGREE: `count_by Opportunity opportunity_type` returned `total_matching=2,631` (freelance_services=2,630, task=1).
- Q5 (zoom-out): 2 candidate folds surfaced but neither shipped this slate — see below.

---

## Zoom-out folds observed (per `feedback_zoom_out_ask_per_rigby_sign`)

Both are **1st trigger only** — logged for future ledger review, not opened this slate:

1. **Kalshi-only distribution on canonical `SpiderData`** — 117K rows all attributed to `kalshi` spider. Suggests other spiders write to `LegacySpiderData` (or there's a routing gap). Data-shape observation; not a slate regression. Watch for 2nd corroborating signal before opening as an investigation arc.

2. **"Post-allowlist smoke checklist" UX pattern** — standard diversity check (2-3 low-cost group-bys per new allowlist addition) to catch "all rows collapsed to one key" immediately. Operator-experience friction candidate. Watch for 2nd trigger before promoting.

---

## Working-loop observations

- **`feedback_verify_rigby_tool_runs_before_trusting_sign`** — fired 1× (initial pre-code SIGN returned a tool-run *summary* without F-verdicts; had to re-route asking for explicit verdicts grounded in the same tool_runs Rigby had already dispatched).
- **`feedback_read_full_rigby_response_not_just_tail`** — fired 1× (Bash `| tail -250` on initial dispatch truncated Rigby's response body; had to query `ChatConversation` directly to recover the summary text, then re-dispatch for verdicts).
- **`feedback_zoom_out_ask_per_rigby_sign`** — fired 2× (both SIGN cycles). Yielded 2 candidate folds (both 1st trigger).
- **`feedback_claude_rigby_agree_first_chris_yes_no`** — no Chris routing needed this slate; all decisions Claude+Rigby resolved.
- **`feedback_recycle_after_merge`** (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=8423e946b4de, surviving=none`).
- **`feedback_rigby_writes_workspace_deliverables`** — Rigby Tool Gap Ledger update executed by Rigby via PA `deliverable_tool.append` (1,363 chars appended, total 21,617). Claude verified via detail read-back.
- **`feedback_engineering_bias_over_audit`** — net-new engineering ship. No audit lean.

**Note on tool-surface friction that surfaced this session:**
- Stale test DB from prior session required manual `DROP DATABASE test_unified_donkey_betz` (via `PGPASSWORD=... psql -h localhost -p 5433 -U unified_user`) before `python manage.py test` could run. `--keepdb` failed on stale schema. This is a session-hygiene footgun, not a Rigby tool gap.

---

## Rigby Tool Gap Ledger updates

- **Deliverable ID:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` ("Rigby Tool Gap Ledger")
- **Content length:** 21,617 chars (was 20,254 pre-update)
- **New section:** "S2873 slate close — 2 wish-list items shipped" (1,363 chars appended)
- **Route:** Rigby via `deliverable_tool.append` per `feedback_rigby_writes_workspace_deliverables`

---

## Session pin lifecycle

- **Pin at S2873 open:** `pa-212927a27cf34515` (labeled `s2873-spider-data-opportunity-orm-inspect`)
- **Pin retires at S2873 close.** Fresh mint required at S2874 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.
- **Wrapper (`tools/pa_local.sh`) bump:** committed in the docs cascade PR at close per `feedback_commit_wrapper_pin_bump_at_close`.

---

## For S2874 open

See `00-START-NEXT-SESSION.md` refreshed at S2873 close. Ledger queue advances by 2 (allowlist wish-list carryovers cleared); new observations surfaced above are 1st-trigger only.
