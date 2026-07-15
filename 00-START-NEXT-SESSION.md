# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2791 CLOSED — Sign Ledger drill-down (aggregations + per-row modal)

**Refreshed 2026-07-15 (SESSION 2791 CLOSED — engineering-first session #5 in row per `feedback_engineering_bias_over_audit`. Broke the 4-consecutive per-prefix authZ sweep streak with a Workspace-tab extension per `feedback_workspace_over_command_center_for_new_ui`. PR #3195 (`e5be876fe`) extended the Sign Ledger UI from a flat list to a drill-down: opt-in `?include=aggregations` on `/api/governance/zoom-out-ledger/` returns `top_arcs_by_count` + `future_trigger_rule_targets` (regex-parsed `PLAYBOOK-\d+\.\d+(\.\d+)?` from `future_trigger` rows only) + `sessions_covered`; frontend adds clickable arc chips (set filter) + future-trigger rule-target chips (informational, amber) + per-row detail modal reusing `ConversationDetailModal` overlay pattern. Rigby T1 tool-grounded SIGN yielded 3 folds: 48 `same_pr_actionable` (backend allowlist add — adopted), 49 `same_pr_mitigatable` (modal-pattern reuse — adopted; no shadcn Dialog in tree), 50 `future_trigger` (aggregation drift guardrail — encoded as regression assertion `test_aggregations_block_repeats_advisory_markers`). Full 13-suite regression: 249 tests OK (235 prior + 14 new). Advisory posture (`is_gate:false` + `semantics: "advisory_pattern_evidence"`) repeated 3× in the modal (header subtitle, footer strip, aggregations block markers) — belt-and-suspenders per S2780 V5 fold. Rigby SIGN response NOT truncated (sample size 2 post-Row 44 — tightened-prompt pattern holding). THIRTIETH close-cycle post-PLAYBOOK-7.4.4 codification.)**

**S2791 ship:**

**PR #3195 · `e5be876fe`** — `core/services/td_handlers_governance.py` (+50 lines: `re` import, `_PLAYBOOK_RULE_RE`, `include` parsing, aggregations block computation), `core/views_governance.py` (+3 lines: `'include'` allowlist + payload passthrough), `frontend/src/pages/workspace/tabs/ZoomOutLedgerSection.tsx` (+286 net: aggregation types, chip strips, per-row detail modal with sister rows + click-to-copy evidence), `core/tests/test_zoom_out_aggregations_2791.py` (new 344-line, 14-test regression with 4 classes), `tools/pa_local.sh` (pin refresh)

**Handoff:** `docs/handoffs/SESSION_2791_SIGN_LEDGER_DRILLDOWN.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirtieth cycle, sha=e5be876fe814).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 50 rows (21 same_pr_actionable / 17 same_pr_mitigatable / 12 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2791)

Engineering-first session #5 in row per `feedback_engineering_bias_over_audit`. Chris selected Workspace-tab extension (Sign Ledger drill-down) at S2791 open, breaking the 4-consecutive per-prefix authZ sweep streak — per `feedback_workspace_over_command_center_for_new_ui` (Workspace is the surface to extend, not Command Center).

Rigby T1 SIGN clean (5 tool_runs — repo_tree + search + 3× read_file, ~55 lines response, no truncation). Three folds surfaced and ALL classified + persisted BEFORE D-verdict per PLAYBOOK-6.10.8/9:
- Row 48 `same_pr_actionable` — backend allowlist reality-check (endpoint would 400 without adding `'include'` to `_GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER`). **Adopted**.
- Row 49 `same_pr_mitigatable` — spec assumed shadcn Dialog; repo_tree confirmed no `frontend/src/components/ui/` dir. Redirected to reuse `ConversationDetailModal` overlay pattern (`frontend/src/components/platform/ConversationDetailModal.tsx:82-101`). **Adopted**.
- Row 50 `future_trigger` — aggregation drift guardrail (richer ledger UI could accrete gate-y feel). Encoded as regression test `test_aggregations_block_repeats_advisory_markers` asserting `is_gate:false` inside the `aggregations` dict — fails loud if any future PR removes the marker.

Zoom-out ask answered per PLAYBOOK-6.10.7: Rigby flagged "dashboard gravity" as coupling risk (progressive Sign Ledger UI enrichment could turn the read surface into a quasi-control-plane). Guardrail = advisory posture repeated 3× in the modal + regression assertion.

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**Workspace tabs are now the default new-UI surface.** S2791 is the first ship after Chris's S2768 directive per `feedback_workspace_over_command_center_for_new_ui` to explicitly extend a Workspace tab rather than propose a Command Center home tile. The Sign Ledger drill-down is proof-of-shape — enrichment lives inside the tab component, not scattered across the shell.

**First aggregation-drift regression pattern.** Row 50 is the first `future_trigger` classification whose trigger condition is expressed as a same-PR regression test rather than an external observation. `test_aggregations_block_repeats_advisory_markers` explicitly asserts `is_gate:false` inside the aggregations dict — if a future PR removes that marker (accident or intentional gate-i-fication), the regression fails loud. New pattern: encode the future-trigger as its own guardrail test in the same PR.

**First Rigby-modified spec adopted whole-cloth.** Both non-trivial modifications Rigby proposed (Row 48 backend reality-check + Row 49 modal pattern reuse) were adopted as-shipped — the modal section of the spec was rewritten from "shadcn Dialog / native `<dialog>`" to "reuse `ConversationDetailModal` overlay" between draft and code. Evidence-admission per PLAYBOOK-6.10.9 supplied all three folds inline with file+line pointers.

**Rigby SIGN response truncation still not recurring.** S2790 clean + S2791 clean = sample size 2 post-Row 44 (S2789 3rd trigger). Tightened-prompt pattern holding. Not yet conclusive but promising.

---

## S2792 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2791 close); freshness should be FRESH · SHA-match at S2791 close SHA `e5be876fe` (or the cascade PR merge SHA).
**Ledger baseline:** 50 rows expected (21/17/12). Any drift = investigate.
**Regression 13-suite:** 249 tests OK at S2791 close.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **PA-tool parity for aggregations** — `zoom_out_tool.list` (Rigby's read path) does NOT yet emit the `aggregations` block. If Rigby ever needs arc-count or rule-target summaries for her own SIGN reasoning, extend PA tool schema plumbing to accept `include` (currently governance REST endpoint only). Small, contained follow-up.
- **Continue Workspace-tab extension pattern** — pick another underweight tab (Deliverables / Initiatives / Files / OpsConsole / Governance) and add a drill-down feature that improves triage speed.
- **Next PUBLIC_PATHS prefix ship** (64 remaining across ~13 prefixes per S2789 audit doc): `/api/teams/` (6), `/api/distribution/` (6), `/api/v1/research/self-blog/` (6), `/api/legal/cases/` (6), `/api/memory-clusters/` (4), `/api/experiments/` (3), `/api/agent-evolution/` (5), `/api/agent-dreams/` (3). Streak was 4-consecutive; S2791 broke it deliberately per Workspace directive.
- **Decorator order codebase migration** — row 45 `same_pr_mitigatable` (S2790). Flip all `@token_auth_required` sites to auth outermost.
- **PLAYBOOK-6.10.11+ codification of per-prefix authZ sweep pattern** — row 47 `future_trigger` (S2790).
- **N24 anti-rubber-stamp SIGN codification** — 5 F-BLOCKING-equivalent triggers.
- **AudioAgent completion-flip verification** — awaiting next timeout.
- **Model drift arc** — 38 auto-migrations queued.
- **Frontend raw-fetch consolidation** — 30 files with fetch(); deferrable.
- **Something entirely new** — fresh spider / agent capability / pipeline / dashboard.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, `SESSION_819_SYSTEM_AUDIT_*` cleanup (9+ untracked files from webhook cron).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 50 — trigger hit; assess S2792)
- **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — Rigby's dogfooding so far was under prompts, not autonomous
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **`@public_endpoint` opt-in decorator ADR** — 263-entry PUBLIC_PATHS wrong-pattern candidate (recorded in S2789 audit doc)
- **Rigby SIGN response truncation follow-up** — S2790/S2791 both clean, watch S2792+ for pattern
- **S2791 Row 50 aggregation drift trigger** — fires if `test_aggregations_block_repeats_advisory_markers` needs to change

### Post-S2791 owed

- **PA-tool aggregations parity** (S2791 §6 follow-up)
- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.10 slot when opened (re-slotted forward again)
- **64 remaining PUBLIC_PATHS candidates** across ~13 prefixes
- **Decorator order codebase migration** (row 45)
- **PLAYBOOK-6.10.11+ per-prefix authZ sweep codification** (row 47)
- **N24 anti-rubber-stamp SIGN codification** — 5 triggers
- **AudioAgent completion-flip verification**
- **Ledger split drift audit** — now 21/17/12
- **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup**

---

## SESSION PIN — S2791 RETIRED (fresh mint required at S2792 open)

**Pin history (S2791):**

- `pa-24fcf1b32a314838` (label `s2791-sign-ledger-drilldown`) minted S2791 open; **retired at S2791 close (`force=true`, twenty-second consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-24fcf1b32a314838` (retired)** — intended failure mode forces S2792 first-action fresh mint.

**S2792 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2791 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2791 close SHA (e5be876fe or cascade PR SHA) — THIRTIETH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2792 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Sign Ledger tab shows 50 rows + new drill-down UI works
# http://localhost:8000/workspace?tab=system&sub=sign-ledger
# Click a row -> modal opens; click an arc chip -> filter applies; see amber future-trigger rule-target chips.

# Ledger check: confirm 50-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==50, r
print('OK — 50 rows, counts:', r['counts_by_classification'])
"

# Regression 13-suite (S2790 12-suite + S2791 aggregations)
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
  --noinput

# Mint fresh pin scoped to selected S2792 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2792 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2791 artifacts:**

- **Ship backend:** `core/services/td_handlers_governance.py` (+50 lines: regex + aggregations block) · `core/views_governance.py` (+3 lines: `include` allowlist + passthrough)
- **Ship frontend:** `frontend/src/pages/workspace/tabs/ZoomOutLedgerSection.tsx` (+286 net: chip strips + modal + sister-rows)
- **Tests:** `core/tests/test_zoom_out_aggregations_2791.py` (344 lines, 14 tests, 4 classes)
- **Handoff:** `docs/handoffs/SESSION_2791_SIGN_LEDGER_DRILLDOWN.md`
- **Predecessors:** S2790 (time-travel authZ), S2789 (pilot-gates), S2780 (Sign Ledger UI shipped), S2786 (Playbook v0.8.0)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — **NEW: drill-down UI**
  - Top-arc chip strip (top 8, click to filter)
  - Future-trigger rule-target chip strip (informational amber)
  - Per-row click → detail modal (full concern, sister rows, click-to-copy evidence)
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — 50 rows (21/17/12)
  - `logs/session_freshness.jsonl` — grew by 1 at S2791 open
  - `logs/recycle_events.jsonl` — +1 event from S2791 close (`sha=e5be876fe814`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `e5be876fe` (S2791 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | S2755→S2790 CLOSED · **S2791 ENGINEERING SHIPPED** · RUR-C1 parent OPEN |
| Session pin | `pa-24fcf1b32a314838` (retired at S2791 close, force=true, twenty-second consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-24fcf1b32a314838` (retired; forces fresh mint at S2792 open) |
| Live infra state | S2755→S2790 substrate + S2791 Sign Ledger drill-down landed |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2791 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3195, sha=e5be876fe814) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **50 rows** (21 actionable / 17 mitigatable / 12 future_trigger) |
| Next move | Chris selects at S2792 open |

---

## Recommended session-open protocol (S2792)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2791 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)
4. **Freshness + regression 13-suite + ledger verify** — see S2792 open sequence above
5. **Watch for** ledger 50-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — engineering leans first per `feedback_engineering_bias_over_audit`; Workspace-tab leans preferred per `feedback_workspace_over_command_center_for_new_ui`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2792 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2792:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2791_SIGN_LEDGER_DRILLDOWN.md`](docs/handoffs/SESSION_2791_SIGN_LEDGER_DRILLDOWN.md) — **S2791 handoff (current)**
4. [`docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md`](docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md) — S2790 predecessor
5. [`docs/audits/PUBLIC_PATHS_AUDIT_S2789.md`](docs/audits/PUBLIC_PATHS_AUDIT_S2789.md) — audit artifact (S2792+ per-prefix ship menu if selected)
6. [`docs/audits/public_paths_audit_s2789.json`](docs/audits/public_paths_audit_s2789.json) — 64-candidate inventory
7. [`docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md`](docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md) — S2789 predecessor
8. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 50 rows at S2791 close (rows 48/49/50 are S2791 backend-allowlist-adopted + modal-pattern-adopted + aggregation-drift-guardrail-encoded)
