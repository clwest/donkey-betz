# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2792 CLOSED — PA-tool aggregations parity (`zoom_out_tool` schema exposes `include`)

**Refreshed 2026-07-15 (SESSION 2792 CLOSED — engineering-first session #6 in row per `feedback_engineering_bias_over_audit`. Schema-only PR extending `zoom_out_tool` PA-tool schema so Rigby can invoke the S2791 aggregations block through GPT-5.2 function calling. PR #3197 (`43b6ef8af`) added `include` string property to `pa_tool_schemas.py:2614-2695` with advisory language + rule_target-not-proposal pushback + Chris D-verdict-as-gate language baked into schema copy per S2792 F1+F2 mitigations. Handler plumbing (`td_handlers_governance.py:229-266`) already emitted the block on `payload['include']='aggregations'` (shipped S2791 PR #3195 via REST); sole gap was schema advertisement. New 336-line test file locks 8 contracts across 2 classes (15 tests). Rigby T1 tool-grounded SIGN yielded 3 folds via zoom-out ask: 51 `same_pr_mitigatable` (schema advisory language — adopted), 52 `same_pr_actionable` (rule_target-not-proposal warning — adopted), 53 `future_trigger` (aggregations-over-all-rows-while-items-filtered scope mismatch — deferred, encoded as locked test contract 6). Full 14-suite regression: 264 tests OK (249 prior + 15 new). Post-merge verification: Rigby invoked `zoom_out_tool.list include=aggregations` with real function-calling dispatch (tool_runs non-empty), returned top-3 arcs / 2 rule targets / 19 sessions. Rigby SIGN response NOT truncated (sample size 3 post-Row 44 — tightened-prompt pattern holding). THIRTY-FIRST close-cycle post-PLAYBOOK-7.4.4 codification.)**

**S2792 ship:**

**PR #3197 · `43b6ef8af`** — `core/services/pa_tool_schemas.py` (+32 lines: `include` string property + description language), `core/tests/test_zoom_out_tool_aggregations_2792.py` (new 336-line, 15-test regression with 2 classes), `tools/pa_local.sh` (pin refresh)

**Handoff:** `docs/handoffs/SESSION_2792_PA_TOOL_AGGREGATIONS_PARITY.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirty-first cycle, sha=`43b6ef8af1d9`).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 53 rows (22 same_pr_actionable / 18 same_pr_mitigatable / 13 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2792)

Engineering-first session #6 in row per `feedback_engineering_bias_over_audit`. Chris selected S2791 §6 explicit follow-up at open: PA-tool parity for aggregations. Investigation revealed the start-here framing was HALF right — the handler plumbing already accepted `include`; only the schema advertisement was missing. Small, contained schema-only PR.

Rigby T1 SIGN tool-grounded (3 `read_file` calls verifying claims (i)/(ii)/(iii)). Three folds surfaced by the zoom-out ask and ALL classified + persisted BEFORE D-verdict per PLAYBOOK-6.10.8/9:
- Row 51 `same_pr_mitigatable` — schema advertises capability → autonomy creep via summaries-as-authority. Mitigation: advisory language in schema description ("aggregations are advisory summaries; not gates; cite raw rows"). **Adopted**.
- Row 52 `same_pr_actionable` — regex-derived `rule_targets` could become pseudo-requirements interface. Mitigation: schema warns rule_target counts ≠ proposals; downstream workflows MUST retrieve+quote raw future_trigger rows; Chris D-verdict remains explicit codification gate. **Adopted**.
- Row 53 `future_trigger` — aggregations computed over ALL rows while items[] filtered; scope mismatch risk as ledger grows. Deferred trigger: ~200 rows OR first user complaint. Encoded as locked test contract 6 (`test_aggregations_over_all_rows_not_filtered_tail`) so eventual refactor becomes visible contract change.

Post-merge dogfooding: Rigby invoked the new capability via function-calling; `tool_runs` confirmed real dispatch.

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**Second same-PR future_trigger-encoded-as-test pattern.** S2791 F3 was encoded as `test_aggregations_block_repeats_advisory_markers`; S2792 F3 is encoded as `test_aggregations_over_all_rows_not_filtered_tail`. Two instances now — the pattern of encoding deferred future_triggers as test guardrails (so refactors become visible contract changes) is a two-instance pattern. Watch for third instance to consider Playbook amendment.

**First same-session dogfooding verification of a shipped tool.** At post-merge, Rigby invoked `zoom_out_tool.list include=aggregations` — the exact capability just shipped. `tool_runs` confirmed real function-calling dispatch. This is the fastest possible feedback loop on a schema-exposure change.

**Rigby SIGN response non-truncation streak now sample size 3.** S2790/S2791/S2792 all clean. Tightened-prompt pattern strengthening but still not conclusive.

**Zoom-out ask (PLAYBOOK-6.10.7) is proven load-bearing.** All 3 S2792 folds were surfaced by the zoom-out ask, none by the direct-verify claim scan. Without PLAYBOOK-6.10.7, the F1/F2/F3 substrate would not exist.

---

## S2793 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2792 close); freshness should be FRESH · SHA-match at S2792 close SHA `43b6ef8af` (or cascade PR merge SHA).
**Ledger baseline:** 53 rows expected (22/18/13). Any drift = investigate.
**Regression 14-suite:** 264 tests OK at S2792 close.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **Continue Workspace-tab extension pattern** per `feedback_workspace_over_command_center_for_new_ui` — pick another underweight tab (Deliverables / Initiatives / Files / OpsConsole / Governance) and add a drill-down feature that improves triage speed.
- **Next PUBLIC_PATHS prefix ship** (64 remaining across ~13 prefixes per S2789 audit doc): `/api/teams/` (6), `/api/distribution/` (6), `/api/v1/research/self-blog/` (6), `/api/legal/cases/` (6), `/api/memory-clusters/` (4), `/api/experiments/` (3), `/api/agent-evolution/` (5), `/api/agent-dreams/` (3). Streak was 4-consecutive; S2791/S2792 broke it deliberately (Workspace / PA-tool leans).
- **Decorator order codebase migration** — row 45 `same_pr_mitigatable` (S2790). Flip all `@token_auth_required` sites to auth outermost.
- **PLAYBOOK-6.10.11+ codification of per-prefix authZ sweep pattern** — row 47 `future_trigger` (S2790).
- **N24 anti-rubber-stamp SIGN codification** — 5 F-BLOCKING-equivalent triggers.
- **AudioAgent completion-flip verification** — awaiting next timeout.
- **Model drift arc** — 38 auto-migrations queued.
- **Frontend raw-fetch consolidation** — 30 files with fetch(); deferrable.
- **Something entirely new** — fresh spider / agent capability / pipeline / dashboard.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, `SESSION_819_SYSTEM_AUDIT_*` cleanup (11 untracked files from webhook cron — grew from 9 during S2791/S2792).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 53 — trigger hit; assess S2793)
- **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — S2792 dogfooding was prompted at post-merge; first autonomous invocation is next trigger
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **`@public_endpoint` opt-in decorator ADR** — 263-entry PUBLIC_PATHS wrong-pattern candidate (recorded in S2789 audit doc)
- **Rigby SIGN response truncation follow-up** — S2790/S2791/S2792 all clean, watch S2793+ for pattern
- **S2791 Row 50 aggregation drift trigger** — fires if `test_aggregations_block_repeats_advisory_markers` needs to change
- **S2792 Row 53 aggregation scope mismatch trigger** — fires at ~200 ledger rows OR first user complaint; contract 6 in `test_zoom_out_tool_aggregations_2792.py` locks the invariant
- **Third instance of future_trigger-encoded-as-test pattern** — S2791 F3 + S2792 F3 = 2 instances; watch for third to consider Playbook amendment

### Post-S2792 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.10 slot when opened (re-slotted forward again)
- **64 remaining PUBLIC_PATHS candidates** across ~13 prefixes
- **Decorator order codebase migration** (S2790 row 45)
- **PLAYBOOK-6.10.11+ per-prefix authZ sweep codification** (S2790 row 47)
- **N24 anti-rubber-stamp SIGN codification** — 5 triggers
- **AudioAgent completion-flip verification**
- **Ledger split drift audit** — now 22/18/13
- **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup** (11 files)

---

## SESSION PIN — S2792 RETIRED (fresh mint required at S2793 open)

**Pin history (S2792):**

- `pa-3f82874b672d44c8` (label `s2792-pa-tool-aggregations-parity`) minted S2792 open; **retired at S2792 close (`force=true`, twenty-third consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-3f82874b672d44c8` (retired)** — intended failure mode forces S2793 first-action fresh mint.

**S2793 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2792 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2792 close SHA (43b6ef8af or cascade PR SHA) — THIRTY-FIRST close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2793 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 53-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==53, r
print('OK — 53 rows, counts:', r['counts_by_classification'])
"

# Regression 14-suite (S2791 13-suite + S2792 aggregations parity)
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
  --noinput

# Mint fresh pin scoped to selected S2793 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2793 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2792 artifacts:**

- **Ship schema:** `core/services/pa_tool_schemas.py:2614-2695` (`zoom_out_tool` block with `include` param, description language, `action` sub-description mention)
- **Ship tests:** `core/tests/test_zoom_out_tool_aggregations_2792.py` (336 lines, 15 tests, 2 classes)
- **Handoff:** `docs/handoffs/SESSION_2792_PA_TOOL_AGGREGATIONS_PARITY.md`
- **Predecessors:** S2791 (Sign Ledger UI + aggregations block ship), S2790 (time-travel authZ), S2786 (Playbook v0.8.0)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — unchanged (REST already had `include=aggregations` since S2791)
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — 53 rows (22/18/13)
  - `logs/session_freshness.jsonl` — grew by 1 at S2792 open
  - `logs/recycle_events.jsonl` — +1 event from S2792 close (`sha=43b6ef8af1d9`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `43b6ef8af` (S2792 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | S2755→S2791 CLOSED · **S2792 ENGINEERING SHIPPED** · RUR-C1 parent OPEN |
| Session pin | `pa-3f82874b672d44c8` (retired at S2792 close, force=true, twenty-third consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-3f82874b672d44c8` (retired; forces fresh mint at S2793 open) |
| Live infra state | S2755→S2791 substrate + S2792 PA-tool aggregations parity landed |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2792 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3197, sha=`43b6ef8af1d9`) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **53 rows** (22 actionable / 18 mitigatable / 13 future_trigger) |
| Next move | Chris selects at S2793 open |

---

## Recommended session-open protocol (S2793)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2792 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)
4. **Freshness + regression 14-suite + ledger verify** — see S2793 open sequence above
5. **Watch for** ledger 53-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — engineering leans first per `feedback_engineering_bias_over_audit`; Workspace-tab leans preferred per `feedback_workspace_over_command_center_for_new_ui`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2793 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2793:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2792_PA_TOOL_AGGREGATIONS_PARITY.md`](docs/handoffs/SESSION_2792_PA_TOOL_AGGREGATIONS_PARITY.md) — **S2792 handoff (current)**
4. [`docs/handoffs/SESSION_2791_SIGN_LEDGER_DRILLDOWN.md`](docs/handoffs/SESSION_2791_SIGN_LEDGER_DRILLDOWN.md) — S2791 predecessor
5. [`docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md`](docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md) — S2790 predecessor
6. [`docs/audits/PUBLIC_PATHS_AUDIT_S2789.md`](docs/audits/PUBLIC_PATHS_AUDIT_S2789.md) — audit artifact (S2793+ per-prefix ship menu if selected)
7. [`docs/audits/public_paths_audit_s2789.json`](docs/audits/public_paths_audit_s2789.json) — 64-candidate inventory
8. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 53 rows at S2792 close (rows 51/52/53 are S2792 F1+F2 adopted + F3 encoded-as-test-contract)
