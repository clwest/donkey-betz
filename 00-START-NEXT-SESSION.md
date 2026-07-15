# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2789 CLOSED — BROADER PUBLIC_PATHS AUDIT + PILOT-GATES PREFIX GATED

**Refreshed 2026-07-15 (SESSION 2789 CLOSED — engineering-first session #3 in row per `feedback_engineering_bias_over_audit`. PR #3191 (`8cf1e73a2`) gated 7 pilot-gates POST endpoints in `core/views_agent_learning.py` with `@token_auth_required` (session OR Token/Bearer, JSON 401). Broader PUBLIC_PATHS categorical audit surfaced **76 true-mutating ungated candidates across ~14 prefixes** (up from ~50-entry estimate in S2788 handoff). Shipped one prefix + audit artifact (`docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` + `docs/audits/public_paths_audit_s2789.json`) for mechanical S2790+ continuation. Rigby T1 tool-grounded SIGN caught 2 would-have-shipped bugs: `@login_required` proposal was wrong (302-redirects to HTML LOGIN_URL under PUBLIC_PATHS bypass, breaks Token clients) — correct decorator is existing `@token_auth_required` at `core/auth_middleware.py:36-81`; and classifier heuristic needed mutation-evidence filter (POST≠stateful for simulation views like `/api/agents/execute/`). Both adopted immediately, folds persisted rows 42+43 `same_pr_actionable`. Row 44 `future_trigger`: 3rd consecutive Rigby SIGN response truncation observation — substrate-promotion trigger met (deferred to S2790+ pa_chat.py/PA worker size cap investigation). Regression 11-suite: 191 tests OK (170 prior + 21 new). Post-merge `make recycle-all` clean — TWENTY-SEVENTH close-cycle post-PLAYBOOK-7.4.4 codification. First `same-session audit artifact` ship shape proven.)**

**S2789 ship:**

**PR #3191 · `8cf1e73a2`** — `core/views_agent_learning.py` (7 `@token_auth_required` decorator additions), `core/tests/test_pilot_gates_authz_sweep_2789.py` (new 193-line, 21-test regression), `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` (new 87-line audit index), `docs/audits/public_paths_audit_s2789.json` (new 1321-line 76-candidate inventory), `tools/pa_local.sh` (pin refresh)

**Handoff:** `docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (twenty-seventh cycle, sha=8cf1e73a29fa).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 44 rows (19 same_pr_actionable / 15 same_pr_mitigatable / 10 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2789)

Engineering-first session #3 in row per `feedback_engineering_bias_over_audit`. Chris selected the broader PUBLIC_PATHS audit at S2789 open (from the S2788 candidate menu — highest-priority engineering lean). Author-side classifier surfaced 190 raw candidates → 120 after MRO-aware CBV filter → 76 after Rigby's mutation-evidence heuristic (Concern 1). Chris narrowed scope to one prefix (`/api/pilot-gates/`, 7 endpoints).

Rigby T1 tool-grounded SIGN (7 tool_runs) caught 2 substantive would-have-shipped bugs: `@login_required` proposal (breaks Token clients on PUBLIC_PATHS bypass — 302 to HTML LOGIN_URL) — correct is existing `@token_auth_required`; and classifier POST≠mutation heuristic gap (`/api/agents/execute/` returns `random.uniform()`, not stateful). Both adopted immediately.

T1 response truncation observed (Concern 2 lost mid-response). Needed T2 short dispatch to retrieve — 3rd consecutive truncation, substrate-promotion trigger now met (row 44 future_trigger deferred to S2790+).

Three folds persisted BEFORE D-verdict per PLAYBOOK-6.10.8: rows 42+43 `same_pr_actionable` (adopted this PR) + row 44 `future_trigger` (deferred).

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**First "audit-artifact-as-first-class-deliverable" ship shape.** S2787/S2788 gated 3-31 endpoints against direct evidence. S2789 introduces same-session audit artifact alongside the code gate — categorized inventory of what remains so S2790+ picks next prefix mechanically. Rigby T1 tightening ("avoid illusion-of-coverage") drove this shape.

**Anti-rubber-stamp discipline confirmed working.** T1 had 7 real tool_runs and produced 2 substantive DISAGREE corrections. Both would have shipped bugs (`@login_required` gate + severity over-count). Discipline caught them pre-verdict.

**Third consecutive engineering ship.** After 3-consecutive-constitutional-MINOR streak (v0.6/S2766 → v0.7/S2778 → v0.8/S2786), now 3-consecutive engineering ships (S2787 CSRF + S2788 Fold C + S2789 pilot-gates). Substrate stays out of the way of net-new work.

**Third Rigby SIGN response truncation observation.** Row 44 substrate-promotion trigger now met. Deferred to S2790+ investigation.

---

## S2790 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2789 close); freshness should be FRESH · SHA-match at S2789 close SHA `8cf1e73a2` (or the cascade PR merge SHA).
**Ledger baseline:** 44 rows expected (19/15/10). Any drift = investigate.
**Regression 11-suite:** 191 tests OK at S2789 close.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **Next PUBLIC_PATHS prefix ship** (S2789 audit artifact enumerates 75 remaining candidates) — pick from:
  - `/api/time-travel/` (11 endpoints — largest prefix, decisions/bookmarks/annotations)
  - `/api/teams/` (6 endpoints — team creation, workflow start/complete)
  - `/api/distribution/` (6 endpoints — content publish/submit/sale/seed)
  - `/api/legal/cases/` (6 endpoints — legal case creation/updates)
  - `/api/v1/research/self-blog/` (6 endpoints — self-blog generate/publish)
- **Rigby SIGN truncation substrate fix** (row 44 `future_trigger` — investigate pa_chat.py or PA worker response-size cap, add pagination/continuation)
- **N24 anti-rubber-stamp SIGN codification** — now at 5 F-BLOCKING-equivalent triggers (S2778/S2780/S2786/S2787/S2789). Strong promotion candidate for PLAYBOOK-6.10.10.
- **Auth-gate consolidation into `core/auth_gates.py`** (~1h) — 4 sentinels + `token_auth_required` = 5 gates. Trigger technically met.
- **AudioAgent completion-flip verification** — awaiting next timeout.
- **Model drift arc** — 38 auto-migrations queued.
- **Frontend raw-fetch consolidation** — 30 files with fetch(); deferrable.
- **Something entirely new** — fresh spider / Workspace tab extension / agent capability / pipeline / dashboard.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, N24 anti-rubber-stamp SIGN codification, `SESSION_819_SYSTEM_AUDIT_*` cleanup (7 untracked files from webhook cron).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 44)
- **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — Rigby's dogfooding so far was under prompts, not autonomous
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **`@public_endpoint` opt-in decorator ADR** — 263-entry PUBLIC_PATHS suggests wrong pattern; future ADR sketch (recorded in S2789 audit doc)

### Post-S2789 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.10 slot when opened (re-slotted forward again from 6.10.9 in v0.8.0 provenance)
- **75 remaining PUBLIC_PATHS candidates** across ~13 prefixes (S2789 audit artifact enumerates)
- **N24 anti-rubber-stamp SIGN codification** — now at 5 triggers, promotion candidate
- **Rigby SIGN response truncation substrate fix** — 3rd trigger met (row 44)
- **AudioAgent completion-flip verification**
- **`test_session_freshness_2775` env drift**
- **Ledger split drift audit** — now 19/15/10 (was 17/15/9 at S2788 close)
- **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup** — 7 files from webhook cron

---

## SESSION PIN — S2789 RETIRED (fresh mint required at S2790 open)

**Pin history (S2789):**

- `pa-900603b3356549d9` (label `s2789-public-paths-categorical-audit`) minted S2789 open; **retired at S2789 close (`force=true`, twentieth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-900603b3356549d9` (retired)** — intended failure mode forces S2790 first-action fresh mint.

**S2790 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2789 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2789 close SHA (8cf1e73a2 or cascade PR SHA) — TWENTY-SEVENTH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2790 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Sign Ledger tab shows 44 rows
# http://localhost:8000/workspace?tab=system&sub=sign-ledger

# Ledger check: confirm 44-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==44, r
print('OK — 44 rows, counts:', r['counts_by_classification'])
"

# Regression 11-suite (unchanged from S2789)
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
  --noinput

# Mint fresh pin scoped to selected S2790 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2790 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## OPEN RUNTIME ITEMS (from S2789 close)

1. **75 remaining PUBLIC_PATHS candidates** (`/api/time-travel/`, `/api/teams/`, `/api/distribution/`, `/api/legal/cases/`, `/api/v1/research/self-blog/`, `/api/experiments/`, `/api/memory-clusters/`, `/api/agent-evolution/`, etc.) — S2789 audit doc enumerates
2. **Rigby SIGN response truncation substrate fix** — 3 triggers met (row 44 future_trigger)
3. **N24 anti-rubber-stamp SIGN codification** — now 5 F-BLOCKING-equivalent triggers; PLAYBOOK-6.10.10 promotion candidate
4. **Auth-gate consolidation** — 5 gates now (`token_auth_required` + 4 staff sentinels); trigger met
5. **AudioAgent completion-flip verification** (C1 linkage live)
6. **`test_session_freshness_2775` env drift**
7. **Model drift arc** (38 unrelated auto-migrations queued)
8. **Ledger split drift audit** (19/15/10 now)
9. **S2761 smoke test** (ops-surface, gated)
10. **S2758 D2 canonical decision** (needs joint SIGN)
11. **S2758 D4 HIGH-RISK wiring extension** (REPORT-ONLY)
12. **N13 handoff-date-format normalizer** (hygiene)
13. **P0.5 cost-threshold advance-to-freeze**
14. **P0.75 CI billing**
15. **RUR-C2 open eligible**
16. **S2758 D1 process_pa_chat_task payload strip**
17. **S2758 D5 local shim retirement**
18. **HMAC signing of `x-acting-user-id`**
19. **First observed partial-recycle event** — N10/N11 trigger
20. **Rigby S2774 forward-carry: ops-surface PR pause** — held
21. **30+ other lambda-`__import__` sites**
22. **Rigby S2773 forward-carry #5 (health_summary overlap)**
23. **N15 v2 / N21 v2 candidates** — deferred
24. **`session_lifecycle` refactor trigger** — still armed
25. **`/api/pa/*` future-endpoint audit trigger** — sharp 5-point test
26. **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
27. **N22 v2 time-window filters** — deferred until ~50+ rows temporal spread
28. **N17 smart-command-box creep** — row 21 `future_trigger`
29. **Second non-Rigby consumer of `zoom_out_tool`** — abstraction quality test
30. **Autonomous Rigby consultation of `zoom_out_tool.list`** — truer substrate-payoff signal
31. **I-0302 three-PR pattern amendment → PLAYBOOK-6.10.10** (re-slotted forward again)
32. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
33. **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
34. **S2783 Fold 1 same-PR mitigation deferred** (GovernanceTab subtitle)
35. **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
36. **Postgres cleanup follow-ups (S2774 carryover)**
37. **`@public_endpoint` opt-in decorator ADR** — 263-entry PUBLIC_PATHS wrong-pattern candidate
38. **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup** — 7 files from webhook cron
39. **Frontend raw-fetch consolidation trigger** — first regression from a raw-fetch mutation site

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2789 artifacts:**

- **Ship code:** `core/views_agent_learning.py` (7 `@token_auth_required` decorator additions)
- **Tests:** `core/tests/test_pilot_gates_authz_sweep_2789.py` (193 lines, 21 tests)
- **Audit artifacts:** `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` (87 lines) + `docs/audits/public_paths_audit_s2789.json` (1321 lines, 76 candidates)
- **Handoff:** `docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md`
- **Predecessors:** S2788 (Fold C 3-endpoint sweep), S2787 (CSRF cross-file cleanup), S2786 (Playbook v0.8.0)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — 44 rows, including S2789 rows 42+43+44
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 44 rows at S2789 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2789 open
  - `logs/recycle_events.jsonl` — +1 new event from S2789 close (`sha=8cf1e73a29fa`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `8cf1e73a2` (S2789 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | S2755→S2788 CLOSED · **S2789 ENGINEERING SHIPPED** · RUR-C1 parent OPEN |
| Session pin | `pa-900603b3356549d9` (retired at S2789 close, force=true, twentieth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-900603b3356549d9` (retired; forces fresh mint at S2790 open) |
| Live infra state | S2755→S2788 substrate + S2789 pilot-gates authZ prefix sweep landed |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2789 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3191, sha=8cf1e73a29fa) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **44 rows** (19 actionable / 15 mitigatable / 10 future_trigger) |
| Next move | Chris selects at S2790 open |

---

## Recommended session-open protocol (S2790)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2789 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)
4. **Freshness + regression 11-suite + ledger + Playbook verify** — see S2790 open sequence above
5. **Watch for** ledger 44-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — engineering leans first per `feedback_engineering_bias_over_audit` (next PUBLIC_PATHS prefix from S2789 audit doc + Rigby truncation substrate fix + N24 codification + something entirely new)
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2790 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2790:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md`](docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md) — **S2789 handoff (current)**
4. [`docs/audits/PUBLIC_PATHS_AUDIT_S2789.md`](docs/audits/PUBLIC_PATHS_AUDIT_S2789.md) — **audit artifact (S2790+ per-prefix ship menu)**
5. [`docs/audits/public_paths_audit_s2789.json`](docs/audits/public_paths_audit_s2789.json) — 76-candidate inventory (machine-readable)
6. [`docs/handoffs/SESSION_2788_FOLD_C_AUTHZ_AUDIT_SWEEP.md`](docs/handoffs/SESSION_2788_FOLD_C_AUTHZ_AUDIT_SWEEP.md) — S2788 predecessor
7. [`docs/handoffs/SESSION_2787_CSRF_EXEMPT_CROSS_FILE_CLEANUP.md`](docs/handoffs/SESSION_2787_CSRF_EXEMPT_CROSS_FILE_CLEANUP.md) — S2787 predecessor
8. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 44 rows at S2789 close (rows 42/43/44 are S2789 classifier heuristic + `@login_required` correction + Rigby SIGN truncation)
