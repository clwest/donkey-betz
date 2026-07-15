# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2790 CLOSED — /api/time-travel/ authZ sweep (11 endpoints)

**Refreshed 2026-07-15 (SESSION 2790 CLOSED — engineering-first session #4 in row per `feedback_engineering_bias_over_audit`. PR #3193 (`29c69911e`) gated 11 /api/time-travel/ mutation endpoints in `core/views_time_travel.py` — added `@token_auth_required`, removed `@csrf_exempt` (S2787 pattern). 4-consecutive per-prefix authZ sweep pattern now stable (S2787 CSRF 31-endpoint / S2788 3-endpoint / S2789 7-endpoint / S2790 11-endpoint). Rigby T1 tool-grounded SIGN yielded 2 folds: A `same_pr_mitigatable` (decorator order swap deferred as codebase-wide migration for consistency), B `same_pr_actionable` (4th test class for session-auth-without-CSRF → 403, adopted this PR). Row 47 `future_trigger` records the 4-consecutive-sweep pattern as PLAYBOOK-6.10.11+ codification candidate. Regression 12-suite: 235 tests OK (191 prior + 44 new). Ungated PUBLIC_PATHS candidates remaining: 64 (was 76). Rigby SIGN response NOT truncated this session — tightened prompt worked (sample size 1 post-row-44). TWENTY-NINTH close-cycle post-PLAYBOOK-7.4.4 codification.)**

**S2790 ship:**

**PR #3193 · `29c69911e`** — `core/views_time_travel.py` (11 decorator swaps: added `@token_auth_required` + removed `@csrf_exempt`, added import), `core/tests/test_time_travel_authz_sweep_2790.py` (new 320-line, 44-test regression with 4 classes), `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` (S2790 UPDATE banner), `docs/audits/public_paths_audit_s2789.json` (11 entries moved to `closed_at_S2790`), `tools/pa_local.sh` (pin refresh)

**Handoff:** `docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (twenty-ninth cycle, sha=29c69911e3b4).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 47 rows (20 same_pr_actionable / 16 same_pr_mitigatable / 11 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2790)

Engineering-first session #4 in row per `feedback_engineering_bias_over_audit`. Chris selected `/api/time-travel/` prefix at S2790 open (largest remaining bucket per S2789 audit doc, 11 endpoints). Ship shape mirrored S2789 pilot-gates + added S2787 CSRF cleanup pattern (removed `@csrf_exempt` from all 11 views).

Rigby T1 SIGN clean (5 tool_runs, ~30 lines response, no truncation despite S2789 row 44 3-trigger — tightened prompt worked). Two folds surfaced: A (decorator order swap) deferred as codebase-wide migration; B (session-auth-without-CSRF test class) adopted this PR as `TimeTravelAuthzSweepSessionWithoutCSRFTest` = 4th test class × 11 endpoints = 11 extra tests. Also added zoom-out response codifying the 4-consecutive-sweep pattern as PLAYBOOK-6.10.11+ candidate.

Three folds persisted BEFORE D-verdict per PLAYBOOK-6.10.8: row 45 (`same_pr_mitigatable` deferred) + row 46 (`same_pr_actionable` adopted) + row 47 (`future_trigger` codification candidate).

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**4-consecutive per-prefix authZ sweep pattern stable.** S2787 (CSRF 31-endpoint cross-file) → S2788 (3 platform) → S2789 (7 pilot-gates) → S2790 (11 time-travel). Ship-shape "one prefix + `@token_auth_required` + `@csrf_exempt` removal + regression test file + audit doc update" is now consistent enough to codify. Row 47 recorded.

**First 4-test-class regression.** Prior sweeps used 3 classes (anon/authed/Token). S2790 adds Rigby Fold B's belt-and-suspenders class (session-auth without CSRF → 403). Catches regressions if `frontend/src/lib/api.ts:32-56` CSRF interceptor breaks. Pattern to inherit for future prefix ships.

**Consistency preferred over Rigby's decorator suggestion.** Rigby T1 Fold A (auth outermost) was architecturally reasonable but conflicted with 20+ existing sites in `views_agent_learning.py`. Deferred as `same_pr_mitigatable` — codebase-wide migration in dedicated PR if adopted.

**Rigby SIGN response truncation NOT recurring (this session).** Tightened prompt ("keep response under 60 lines") worked. S2789 row 44 marked 3rd trigger; S2790 clean is a promising counter-observation. Not conclusive with sample size 1.

---

## S2791 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2790 close); freshness should be FRESH · SHA-match at S2790 close SHA `29c69911e` (or the cascade PR merge SHA).
**Ledger baseline:** 47 rows expected (20/16/11). Any drift = investigate.
**Regression 12-suite:** 235 tests OK at S2790 close.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **Next PUBLIC_PATHS prefix ship** (64 remaining across ~13 prefixes per updated audit doc):
  - `/api/teams/` (6 endpoints — team creation, workflow start/complete/execute)
  - `/api/distribution/` (6 endpoints — content publish/submit/sale/seed)
  - `/api/v1/research/self-blog/` (6 endpoints — self-blog generate/publish)
  - `/api/legal/cases/` (6 endpoints — legal case creation/updates)
  - `/api/memory-clusters/` (4 endpoints)
  - `/api/experiments/` (3 endpoints — experiment create/start/stop/convert)
  - `/api/agent-evolution/` (5 endpoints)
  - `/api/agent-dreams/` (3 endpoints)
- **Decorator order codebase migration** — row 45 `same_pr_mitigatable`. Flip all `@token_auth_required` sites to auth outermost (`views_agent_learning.py` ~20+ sites, `views_time_travel.py` 11, `views_agent_learning.py` pilot-gates 7).
- **Rigby SIGN truncation substrate fix** — row 44 (S2789) still deferred; S2790 landed clean but 1 counter-observation isn't conclusive.
- **N24 anti-rubber-stamp SIGN codification** — 5 F-BLOCKING-equivalent triggers. PLAYBOOK-6.10.10+ candidate.
- **PLAYBOOK-6.10.11+ codification of per-prefix authZ sweep pattern** — row 47 `future_trigger` recorded.
- **AudioAgent completion-flip verification** — awaiting next timeout.
- **Model drift arc** — 38 auto-migrations queued.
- **Frontend raw-fetch consolidation** — 30 files with fetch(); deferrable.
- **Something entirely new** — fresh spider / Workspace tab extension / agent capability / pipeline / dashboard.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, `SESSION_819_SYSTEM_AUDIT_*` cleanup (7+ untracked files from webhook cron).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 47)
- **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — Rigby's dogfooding so far was under prompts, not autonomous
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **`@public_endpoint` opt-in decorator ADR** — 263-entry PUBLIC_PATHS wrong-pattern candidate (recorded in S2789 audit doc)
- **Rigby SIGN response truncation follow-up** — S2790 clean, watch S2791+ for pattern

### Post-S2790 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.10 slot when opened (re-slotted forward again)
- **64 remaining PUBLIC_PATHS candidates** across ~13 prefixes
- **Decorator order codebase migration** (row 45)
- **PLAYBOOK-6.10.11+ per-prefix authZ sweep codification** (row 47)
- **N24 anti-rubber-stamp SIGN codification** — 5 triggers
- **Rigby SIGN response truncation substrate fix** — 3 triggers, 1 counter-observation
- **AudioAgent completion-flip verification**
- **Ledger split drift audit** — now 20/16/11
- **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup**

---

## SESSION PIN — S2790 RETIRED (fresh mint required at S2791 open)

**Pin history (S2790):**

- `pa-83e0c0e0f2f544a6` (label `s2790-public-paths-time-travel-prefix`) minted S2790 open; **retired at S2790 close (`force=true`, twenty-first consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-83e0c0e0f2f544a6` (retired)** — intended failure mode forces S2791 first-action fresh mint.

**S2791 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2790 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2790 close SHA (29c69911e or cascade PR SHA) — TWENTY-NINTH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2791 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Sign Ledger tab shows 47 rows
# http://localhost:8000/workspace?tab=system&sub=sign-ledger

# Ledger check: confirm 47-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==47, r
print('OK — 47 rows, counts:', r['counts_by_classification'])
"

# Regression 12-suite (unchanged from S2790)
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
  --noinput

# Mint fresh pin scoped to selected S2791 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2791 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2790 artifacts:**

- **Ship code:** `core/views_time_travel.py` (11 decorator swaps + import)
- **Tests:** `core/tests/test_time_travel_authz_sweep_2790.py` (320 lines, 44 tests, 4 classes)
- **Audit updates:** `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` + `docs/audits/public_paths_audit_s2789.json`
- **Handoff:** `docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md`
- **Predecessors:** S2789 (pilot-gates), S2788 (Fold C), S2787 (CSRF cross-file), S2786 (Playbook v0.8.0)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — 47 rows, including S2790 rows 45+46+47
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 47 rows at S2790 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2790 open
  - `logs/recycle_events.jsonl` — +1 new event from S2790 close (`sha=29c69911e3b4`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `29c69911e` (S2790 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | S2755→S2789 CLOSED · **S2790 ENGINEERING SHIPPED** · RUR-C1 parent OPEN |
| Session pin | `pa-83e0c0e0f2f544a6` (retired at S2790 close, force=true, twenty-first consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-83e0c0e0f2f544a6` (retired; forces fresh mint at S2791 open) |
| Live infra state | S2755→S2789 substrate + S2790 time-travel authZ sweep landed |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2790 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3193, sha=29c69911e3b4) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **47 rows** (20 actionable / 16 mitigatable / 11 future_trigger) |
| Next move | Chris selects at S2791 open |

---

## Recommended session-open protocol (S2791)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2790 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)
4. **Freshness + regression 12-suite + ledger + Playbook verify** — see S2791 open sequence above
5. **Watch for** ledger 47-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — engineering leans first per `feedback_engineering_bias_over_audit` (next PUBLIC_PATHS prefix from S2789 audit doc + decorator order migration + something entirely new)
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2791 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2791:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md`](docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md) — **S2790 handoff (current)**
4. [`docs/audits/PUBLIC_PATHS_AUDIT_S2789.md`](docs/audits/PUBLIC_PATHS_AUDIT_S2789.md) — **audit artifact (S2791+ per-prefix ship menu)**
5. [`docs/audits/public_paths_audit_s2789.json`](docs/audits/public_paths_audit_s2789.json) — 64-candidate inventory (post-S2790 update)
6. [`docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md`](docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md) — S2789 predecessor
7. [`docs/handoffs/SESSION_2788_FOLD_C_AUTHZ_AUDIT_SWEEP.md`](docs/handoffs/SESSION_2788_FOLD_C_AUTHZ_AUDIT_SWEEP.md) — S2788 predecessor
8. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 47 rows at S2790 close (rows 45/46/47 are S2790 decorator-order-deferred + CSRF-gap-test-adopted + per-prefix-sweep-codification-candidate)
