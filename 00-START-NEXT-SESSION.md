# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2796 CLOSED — `td_handlers_ops` validation slice 1 (4 tools)

**Refreshed 2026-07-15 (SESSION 2796 CLOSED — engineering-first session #10 in row. Session opened with a market-shipping priority signal from Chris ("we need to start making real progress to get this app to market and getting some users") — persisted as `project_market_shipping_priority_2026_07_15`. Chris picked `td_handlers_ops` slice (from the S2795 gap map's top 5 triage slices) — the cheapest cheapest AND user-visible payoff because Rigby-as-operator surface reliability directly affects Chris's autonomy. Ship: 4 per-tool validation docs (`ops_tool`, `status_snapshot_tool`, `diagnostics_tool`, `active_priority_tool`) using Rigby's 6-section template. Doc-only per Chris "validation quickest" — no code changes, no regression tests. Rigby T1 SIGN-WITH-EDITS with 8+ `repo_tool` tool_runs verifying schemas + handlers + no-pre-existing-docs. 4 folds classified + persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8: F1 doc evidence admission (adopted), F2 6-section doc template (adopted), F3 5th-tool `scheduled_tasks_tool` deferred (Rigby Z2), F4 next-incident-critical slice named in PR body (Rigby Z4). Latent classifier bug caught mid-ship: gap-map `NEXT_HEADING_RE` truncates parse at first h3 — restructured 4 docs to flat bulleted list under `## Covered actions` with per-action inline admission markers. Second regen confirmed all 4 upgraded from `validated_partial` to `validated_full`. Full 17-suite regression 318 tests OK (3.7s, unchanged from S2795 close — no code). Post-merge dogfood deferred to Rigby's first autonomous `build_pa_tool_audit` invocation (still-pending trigger from S2795). Rigby SIGN response non-truncated (sample size 7 — pattern very strongly holds). THIRTY-SIXTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2796 ship:**

**PR #3205 · `ec44778f9`** — 7 files, +972 / -161. 4 new per-tool validation docs (~430 lines total) + new S2796 gap map snapshot + refreshed DOC-AUTOGEN'd `PA_TOOL_AUDIT.md` + fresh session pin. Zero code changes.

**Handoff:** `docs/handoffs/SESSION_2796_TD_HANDLERS_OPS_SLICE1.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirty-sixth cycle, sha=`ec44778f9de1`).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **68 rows** (28 same_pr_actionable / 23 same_pr_mitigatable / 16 future_trigger).

**Gap map delta at close:** `untested 105 → 101 (-4)`, `validated_full 0 → 4 (+4)`, `validated_doc_exists_unknown 8 → 8 (unchanged)`.

---

## SESSION-OPEN INFRA STORY (S2796)

Engineering-first session #10 in row. **First market-shipping priority signal from Chris** — refines (does not replace) `feedback_engineering_bias_over_audit`. User-visible / UX / feature-shipping leans now go FIRST in candidate menus; substrate leans below with explicit trigger justification. Chris still picked substrate this session (validation slice) because it has direct user-visible payoff via Rigby-as-operator reliability.

**Latent bug caught mid-ship:** gap-map classifier's `NEXT_HEADING_RE = re.compile(r'\n#+\s+', ...)` cuts the "Covered actions" parse at the first h3 sub-heading. My initial docs used `## Covered actions` + `### In scope` + `### Deferred` structure — classifier only saw the intro paragraph (zero backticks) and classified as `validated_partial`. Restructured to flat bulleted list under `## Covered actions` with per-action inline admission markers (e.g. `` - `version` — **in scope this ship** — ... `` / `` - `slo_status` — runtime-not-executed. ...``). Second regen confirmed 4 tools upgraded to `validated_full`. **Doc-note follow-up:** annotate the S2795 F2 6-section template spec to warn future authors about the h3 truncation.

**Evidence capture pattern established:** dispatched Rigby to invoke 3 tools in one PA turn (`status_snapshot`, `diagnostics.advisor_invocations`, `active_priority.list`) — got live observed-run snippets for all 3 docs. Combined with earlier `ops_tool.version` + `ops_tool.recent_recycles` observations from freshness check, every doc has real observed-run evidence in §Evidence per F1 requirement.

---

## S2797 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2796 close); freshness should be FRESH · SHA-match at S2796 close SHA `ec44778f9` (or cascade PR merge SHA).
**Ledger baseline:** 68 rows expected (28/23/16). Any drift = investigate.
**Regression 17-suite:** 318 tests OK at S2796 close.
**Gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` (4 full · 0 partial · 8 unknown · 101 untested).

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit` + `project_market_shipping_priority`)

**⭐ USER-VISIBLE / UX leans (per market-shipping priority):**
- **Something that puts a working feature in front of a user** — Chris directive emphasized. Candidate menus were not written up front; Chris to propose or ask for suggestions.
- **Workspace-tab extension** per `feedback_workspace_over_command_center_for_new_ui` (e.g. gap-map summary tile, priority list widget, deliverables surface).
- **First alpha-user-facing surface** — the biggest gap between substrate we have and a first user landing.

**Substrate leans (with explicit user-visible payoff — should be trigger-justified per `project_market_shipping_priority`):**
- **Next `td_handlers_ops` sub-slice** — 9 untested tools remain. Options ranked by session cost:
  - **Incident-critical slice** (Rigby Z4 concern): `autopilot_tool`, `governor_tool`, `infra_health_tool`, `spider_status_tool` (~1 slice PR)
  - **Utility slice** (Rigby Z2 pick): `scheduled_tasks_tool` (~1 tool; small)
  - **Remaining slice:** `agent_control_tool`, `agent_memory_tool`, `heartbeat_history_tool`, `ops_digest_tool` (~1 slice PR)
- **Regression tests for the 4 S2796 tools** — deferred per "validation quickest"; queue for follow-up PR. Cheap.
- **Cheap pre-work: add "Covered actions" sections to 8 existing `validated_doc_exists_unknown` docs** — upgrades all 8 to `validated_full` with zero risk. Note: MUST use flat bulleted list under `## Covered actions` (no h3 sub-headings) per the latent classifier truncation bug.
- **Cheap pre-work: fix 23 tools flagged `actions_not_mentioned_in_description`** — zero-code, description-only PR.
- **Open I-0303 (Async Tenant-Boundary Enforcement)** — the ONLY unopened RUR-C1 child arc. Multi-session arc.
- **Wire tenant boundary health umbrella → Celery beat** — S2794 follow-up (~1 PR).
- **Playbook amendment PR — future-trigger-encoded-as-test codification** (third instance still pending: S2791/S2792/S2793).
- **Model drift arc** — 38+ auto-migrations queued.
- **Next PUBLIC_PATHS prefix ship** (64 remaining across ~13 prefixes).
- **Decorator order codebase migration** — row 45 `same_pr_mitigatable`.
- **N24 anti-rubber-stamp SIGN codification** — 5 F-BLOCKING-equivalent triggers.
- **AudioAgent completion-flip verification** — awaiting next timeout.
- **Frontend raw-fetch consolidation** — 30 files with fetch(); deferrable.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, `SESSION_819_SYSTEM_AUDIT_*` cleanup (16 untracked files from webhook cron — unchanged during S2796).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v3 timestamp-based windows** — trigger: session-int windows prove insufficient
- **Second non-Rigby consumer of `zoom_out_tool`** — still awaited
- **Second consumer of `pa_tools_gap_map` service** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **First autonomous Rigby invocation of `tenant_boundary_health` endpoint** — S2794 dogfood was prompted
- **First autonomous Rigby invocation of `build_pa_tool_audit`** — S2795 + S2796 dogfoods were prompted
- **F4 (telemetry-backed complaints, S2795 row 63) future_trigger** — fires when `tool_call_error_rate` query surface exists
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2794 Row 57 autonomy creep trigger** — fires if any sibling PR wires status→flag auto-flip on tenant boundary health
- **Third instance of future_trigger-encoded-as-test pattern — still standing** (S2791/S2792/S2793). S2795 F4 + S2796 folds did not extend or break.
- **`status_snapshot_tool` version-source parity trigger** — fires when a second consumer of `version_sha_short` surfaces; reconcile with `ops_tool.version`

### Post-S2796 owed

- **I-0303 scoping open** — RUR-C1 parent-close direct blocker
- **Regression tests for 4 S2796 validation docs** (`ops_tool`, `status_snapshot_tool`, `diagnostics_tool`, `active_priority_tool`)
- **8 remaining per-tool docs need "Covered actions" flat-list sections** — cheapest gap-map upgrade
- **23 tools schema-lint `actions_not_mentioned_in_description`** — description-only PR
- **`diagnostics_tool` PR-2 placeholders** — implement or remove (`schema_handler_diff`, `learning_bridge_writes`, `discord_health`)
- **`status_snapshot_tool` version-source reconciliation** (`ops.version_sha_short = "dev"` vs `ops_tool.version = 0c38718b0492`)
- **`status_snapshot_tool` cache-age surfacing**
- **`active_priority_tool` TTL clamp response shape verification**
- **Wire tenant boundary health umbrella → Celery beat + CI Action** — S2794 follow-up
- **Playbook amendment PR — future-trigger-encoded-as-test codification** (candidate)
- **64 remaining PUBLIC_PATHS candidates** across ~13 prefixes
- **Decorator order codebase migration** (S2790 row 45)
- **PLAYBOOK-6.10.11+ per-prefix authZ sweep codification** (S2790 row 47)
- **N24 anti-rubber-stamp SIGN codification** — 5 triggers
- **AudioAgent completion-flip verification**
- **Ledger split drift audit** — now 28/23/16
- **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup** (16 files)
- **Doc-note the classifier h3-truncation bug** in the S2795 F2 6-section template spec

---

## SESSION PIN — S2796 RETIRED (fresh mint required at S2797 open)

**Pin history (S2796):**

- `pa-305af57e2bf04406` (label `s2796-td-handlers-ops-validation`) minted S2796 T1 open; **retired at S2796 close (`force=true`, twenty-seventh consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-305af57e2bf04406` (retired)** — intended failure mode forces S2797 first-action fresh mint.

**S2797 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2796 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2796 close SHA (ec44778f9 or cascade PR SHA) — THIRTY-SIXTH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2797 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 68-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==68, r
print('OK — 68 rows, counts:', r['counts_by_classification'])
"

# Regression 17-suite (unchanged; no S2796 code changes)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  core.tests.test_platform_auth_regression_2784 \
  core.tests.test_decision_approve_auth_regression_2785 \
  core.tests.test_csrf_enforcement_2787 \
  core.tests.test_platform_authz_sweep_2788 \
  core.tests.test_pilot_gates_authz_sweep_2789 \
  core.tests.test_time_travel_authz_sweep_2790 \
  core.tests.test_zoom_out_aggregations_2791 \
  core.tests.test_zoom_out_tool_aggregations_2792 \
  core.tests.test_zoom_out_time_window_2793 \
  core.tests.test_tenant_boundary_health_2794 \
  core.tests.test_pa_tools_gap_map_2795 \
  --noinput

# Optional — regenerate gap map to see fresh counts
DJANGO_LOG_LEVEL=WARNING python manage.py build_pa_tool_audit --gap-only --check 2>/dev/null | head -40

# Mint fresh pin scoped to selected S2797 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2797 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2796 artifacts:**

- **Ship docs:** `docs/research/tools/validation/{ops_tool,status_snapshot_tool,diagnostics_tool,active_priority_tool}_validation.md` (4 new)
- **Ship gap map snapshot:** `docs/audits/PA_TOOLS_GAP_MAP_S2796.md`
- **Ship refresh:** `docs/PA_TOOL_AUDIT.md` (DOC-AUTOGEN via `build_pa_tool_audit --include-validation-xref`)
- **Handoff:** `docs/handoffs/SESSION_2796_TD_HANDLERS_OPS_SLICE1.md`
- **Predecessors:** S2795 (gap map), S2733 (campaign retrospective), S2728→S2732 (validation campaign body)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No Workspace tab this ship** — CLI + markdown-only
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **68 rows** (28/23/16)
  - `logs/recycle_events.jsonl` — +1 event (post-#3205, sha=`ec44778f9de1`)
  - `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` — first S2796 snapshot

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `ec44778f9` (S2796 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| RUR-C1 child arcs | I-0301 CLOSED (S2742) · I-0302 CLOSED (S2751) · **I-0303 NOT YET OPENED** |
| Session pin | `pa-305af57e2bf04406` (retired at S2796 close, force=true, twenty-seventh consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-305af57e2bf04406` (retired; forces fresh mint at S2797 open) |
| Live infra state | S2755→S2795 substrate + S2796 4-tool validation slice |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2796 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3205, sha=`ec44778f9de1`) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **68 rows** (28 actionable / 23 mitigatable / 16 future_trigger) |
| PA tool audit | `docs/PA_TOOL_AUDIT.md` — regenerated at close (158/114/157/113) |
| PA tools gap map | `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` — first S2796 snapshot (4 full / 0 partial / 8 unknown / 101 untested) |
| Next move | Chris selects at S2797 open |

---

## Recommended session-open protocol (S2797)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2796 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)
4. **Freshness + regression 17-suite + ledger verify** — see S2797 open sequence above
5. **Watch for** ledger 68-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — **user-visible / UX leans FIRST per `project_market_shipping_priority`**; substrate leans below with explicit trigger justification
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2797 P0 selection (candidate menu is a prior, not a gate — Chris may pivot to something new)
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2797:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2796_TD_HANDLERS_OPS_SLICE1.md`](docs/handoffs/SESSION_2796_TD_HANDLERS_OPS_SLICE1.md) — **S2796 handoff (current)**
4. [`docs/audits/PA_TOOLS_GAP_MAP_S2796.md`](docs/audits/PA_TOOLS_GAP_MAP_S2796.md) — **S2796 gap map (4 full / 8 unknown / 101 untested)**
5. [`docs/PA_TOOL_AUDIT.md`](docs/PA_TOOL_AUDIT.md) — fresh runtime-derived PA tool audit (regen at S2796 close)
6. [`docs/research/tools/validation/`](docs/research/tools/validation/) — 22 existing validation docs (10 substrate + 12 per-tool, of which 4 are S2796 with flat-list Covered actions)
7. [`docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md`](docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md) — S2795 predecessor
8. [`docs/handoffs/SESSION_2733_CAMPAIGN_RETROSPECTIVE.md`](docs/handoffs/SESSION_2733_CAMPAIGN_RETROSPECTIVE.md) — S2728→S2732 validation campaign retrospective
9. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 68 rows at S2796 close (rows 65-68 are S2796 F1-F4 folds)
