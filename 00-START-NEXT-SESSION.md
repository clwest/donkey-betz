# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2784 CLOSED — FOLD 4 STAFF-ONLY GATE (same-session mitigation)

**Refreshed 2026-07-14 (SESSION 2784 CLOSED — same-session mitigation of S2783 Fold 4 discovery, ~1h. PR #3181 (`814c2452d`) adds staff-only gating to all 12 mutation POST endpoints in `core/views_platform_command.py` — module-level `_platform_staff_only` + `@login_required @_platform_staff_only` decorator stack on 12 views, mirrors S2772 N16 Rigby-ratified contract + `_governance_staff_only` pattern from `core/views_governance.py`. Removes 12 inline `if not is_authenticated` checks. New regression test file `test_platform_auth_regression_2784.py` — 28 tests. Cross-file auth sweep clean (48 tests OK across 3 suites). Fold 4 was ORIGINALLY worded 'no auth gating' but investigation revealed actual gap was 'no STAFF-only gating' (all 12 already had authN checks, missing authZ). Scope started at 4 endpoints, expanded to 12 after Claude discovered wider pattern via `grep -B 3` — Rigby SIGN Option B AGREE (single concern with 12 sites per PLAYBOOK-7.4.1, not a violation). Novel: **first observed fold-authoring discipline drift** — recorded as Fold 31 (`same_pr_mitigatable`) with a process fix. Live curl on Daphne confirmed 401 for anon POST on emergency-halt, skin-lock, run-remediation. Chris eyeball-verified GovernanceTab still renders + operates (he's staff+superuser, transparent). Post-merge `make recycle-all` clean — TWENTY-FIRST close-cycle post-PLAYBOOK-7.4.4 codification. Ledger grew 27 → 31 rows (13/12/6). Chris asked about the pending-decision Approve buttons during eyeball — noted DecisionApprove endpoint auth posture is unaudited (outside this PR's scope) and added as follow-up candidate.)**

**S2784 ship:**

**PR #3181 · `814c2452d`** — `core/views_platform_command.py` (12 view decorations + module gate), `core/tests/test_platform_auth_regression_2784.py` (new, 236 lines), `tools/pa_local.sh` (+1/-1 pin refresh)

**Handoff:** `docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (twenty-first cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 31 rows (13 same_pr_actionable / 12 same_pr_mitigatable / 6 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2784)

Clean session-in-session opener. S2784 started immediately after S2783 close with no gap. Chris chose S2783's Fold 4 same-PR mitigation candidate as the S2784 P0.

Investigation phase caught a Fold-authoring discrepancy: S2783 Fold 4 was recorded as "no auth gating" but the actual code state was "authN checks present, no staff-only authZ check." Rewording didn't change the fix — it changed the *scope*. Same investigation surfaced 8 additional inline-auth sites beyond the original 4 (all in `views_platform_command.py`), all with the same pattern.

Rigby SIGN Option B AGREE — "consistent staff-only gating for platform mutation endpoints in core/views_platform_command.py" is one concern with 12 sites, not a 7.4.1 violation. Chris D-verdict "Let's do B — comprehensive fix" confirmed the scope expansion.

Implementation was mechanical (atomic Python script transformation: add module gate + imports, remove 12 inline checks + 2 obsolete comments, inject decorator pair before each of 12 view definitions). Full auth regression sweep (3 test files, 48 tests) clean. Live curl confirmed 401 on anon POST. Chris eyeball-verified GovernanceTab still renders + operates.

Chris raised a question about "Approve" buttons in the pending-decision cards during eyeball — the DecisionApprove endpoint lives outside `views_platform_command.py`, wasn't touched by this PR, and its auth posture is unaudited. Added as follow-up candidate.

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**Same-session Fold mitigation is the tightest feedback loop this platform has run.** S2783 Fold 4 was recorded → S2784 opened seconds later → mitigation shipped in ~1h. The recorded fold framed the work; investigation reframed the fold; the resulting patch is broader (12 endpoints instead of 4) but more correct.

**Fold-authoring hygiene is a substrate concern.** Fold 4 said "no auth gating" but the actual gap was authZ (staff-only) missing. If we hadn't investigated, we might have shipped a smaller patch against the wrong framing. Recorded as Fold 31 (this session's fold-of-a-fold). If a second trigger surfaces, this becomes a Playbook amendment candidate: "when recording a fold that names a specific gap, verify the gap's actual character before recording."

**S2772 N16 contract's reach expands.** The "governance/platform endpoints MUST be login_required AND staff-only" rule was authored for `/api/governance/*` and `/api/ops/*`. This PR is the first extension to `/api/platform/*` mutations. The contract is quietly becoming the canonical authZ posture for the entire aggregated command-center surface.

**Regression test file gives future drift a fail-loud contract.** `_PLATFORM_MUTATION_ENDPOINTS` + route inventory guard means any new mutation endpoint added to `core/views_platform_command.py` without an accompanying `test_<name>_blocks_anonymous` + `test_<name>_blocks_non_staff` will fail this test on CI. Mirrors the S2772/S2780 pattern.

---

## S2785 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired; freshness should be FRESH · SHA-match at S2784 close SHA.
**Ledger baseline:** 31 rows expected (13/12/6). Any drift = investigate.
**Regression 7-suite:** now includes `test_platform_auth_regression_2784` (see updated open sequence below).

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **DecisionApprove endpoint auth audit + gate** — surfaced during S2784 eyeball verify. Chris asked about "Approve" buttons on pending decision cards. Audit `views_decisions.py` (or wherever decision approve/dismiss lives) for `@login_required @_platform_staff_only` (or equivalent), and gate if missing. Small ship (~10-30 LOC depending on endpoint count). Natural continuation of S2784 authZ work.
- **AudioAgent completion-flip verification** — C1 linkage is live but 0 rows populated yet. On-demand voiceover test run → join to `CeleryTaskEvent` → prove/disprove false-positive-timeout hypothesis. Could unblock a fix in `core/agents/ai_series_workflow_agent.py:1310`.
- **Model drift arc** — S2782 discovered 38 unrelated auto-generated migrations queued by `makemigrations core`. Housekeeping candidate: isolated branch, review the 38 ops. Non-trivial (~1-3h).
- **CSRF exemption follow-up on the 12 platform mutation endpoints** (S2784 Fold 30) — staff-only shrinks blast radius but doesn't fix CSRF exposure. Non-trivial (frontend has to start sending CSRF token; not just decorator swap). Larger scope than the S2784 gate PR.
- **N24 anti-rubber-stamp SIGN codification** — Playbook MINOR (2+ triggers observed, ready when authorized).
- **Something entirely new** — new spider / UI page / agent capability / pipeline / dashboard / command. Fresh direction OK.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit.

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 31)
- **N22 v4+ candidates** — Django model, JSONL rotation (~500 rows away), auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — watching (Rigby's 3-session dogfooding was under my prompt, not autonomous)
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle (deferred; track for label confusion)
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **S2784 Fold 31 fold-authoring discipline drift** — 1 trigger observed; watch for 2nd

### Post-S2784 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.9 slot when opened
- **DecisionApprove endpoint auth audit** (see net-new — natural S2785 P0 candidate)
- **CSRF exemption cleanup** on the 12 platform mutation endpoints (see net-new)
- **AudioAgent completion-flip verification** (C1 linkage live)
- **`test_session_freshness_2775` env drift** (test guard or always-populate)
- **Ledger split drift audit** — 12/8/2 → 12/8/3 shift at S2782 open

---

## SESSION PIN — S2784 RETIRED (fresh mint required at S2785 open)

**Pin history (S2784):**

- `pa-f2bd82d8c76f4e32` (label `s2784-fold4-auth-mitigation`) minted S2784 open; **retired at S2784 close (`force=true`, fifteenth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-f2bd82d8c76f4e32` (retired)** — intended failure mode forces S2785 first-action fresh mint.

**S2785 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2784 handoff §3 (Fold-framing correction novel-precedent) + §8 (open items)

# Freshness check. Should be FRESH · SHA-match at S2784 close SHA (814c2452d) — TWENTY-FIRST close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2785 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Self-Healing tab still renders as staff (Chris eyeball)
# http://localhost:8000/workspace?tab=system&sub=self-healing

# Ledger check: confirm 31-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==31, r
print('OK — 31 rows, counts:', r['counts_by_classification'])
"

# Regression 7-suite (NEW: includes test_platform_auth_regression_2784)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  core.tests.test_platform_auth_regression_2784 \
  --noinput

# Playbook v0.7.0 verify — rules still present
grep -c 'PLAYBOOK-6\.10\.[7-8]' docs/ENGINEERING_PLAYBOOK.md  # expect >=5

# Mint fresh pin scoped to selected S2785 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2785 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 constitutional at v0.7.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict.

---

## OPEN RUNTIME ITEMS (from S2784 close)

1. **DecisionApprove endpoint auth audit** (surfaced during S2784 eyeball verify; natural S2785 P0 candidate)
2. **AudioAgent completion-flip verification** (C1 linkage live, 0 rows populated)
3. **CSRF exemption cleanup** on the 12 platform mutation endpoints (S2784 Fold 30, `same_pr_mitigatable`, deferred)
4. **`test_session_freshness_2775` env drift**
5. **Model drift arc** (38 unrelated auto-migrations queued)
6. **Ledger split drift audit** (12/8/2 → 12/8/3 shift at S2782 open)
7. **S2761 smoke test** (ops-surface, gated)
8. **S2758 D2 canonical decision** (needs joint SIGN)
9. **S2758 D4 HIGH-RISK wiring extension** (REPORT-ONLY)
10. **N13 handoff-date-format normalizer** (hygiene)
11. **P0.5 cost-threshold advance-to-freeze**
12. **P0.75 CI billing**
13. **RUR-C2 open eligible**
14. **S2758 D1 process_pa_chat_task payload strip**
15. **S2758 D5 local shim retirement**
16. **HMAC signing of `x-acting-user-id`**
17. **Memory rule promotion audit** — N24 anti-rubber-stamp SIGN at 2+ triggers
18. **First observed partial-recycle event** — N10/N11 trigger
19. **Rigby S2774 forward-carry: ops-surface PR pause** — held; S2784 was in-scope
20. **30+ other lambda-`__import__` sites**
21. **Rigby S2773 forward-carry #5 (health_summary overlap)**
22. **N15 v2 / N21 v2 candidates** — deferred
23. **`session_lifecycle` refactor trigger** — still armed
24. **`/api/pa/*` future-endpoint audit trigger** — sharp 5-point test
25. **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
26. **N22 v2 time-window filters** — deferred until ~50+ rows temporal spread
27. **N17 smart-command-box creep** — row 21 `future_trigger`
28. **Second non-Rigby consumer of `zoom_out_tool`** — abstraction quality test
29. **Autonomous Rigby consultation of `zoom_out_tool.list`** — truer substrate-payoff signal
30. **N24 anti-rubber-stamp SIGN codification** — 2+ triggers; ready when authorized
31. **I-0302 three-PR pattern amendment** — take PLAYBOOK-6.10.9 when it opens
32. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
33. **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
34. **S2783 Fold 1 same-PR mitigation deferred** (GovernanceTab subtitle if label confusion appears)
35. **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
36. **S2784 Fold 31 fold-authoring discipline drift** — 1 trigger; watch for 2nd
37. **Postgres cleanup follow-ups (S2774 carryover)**

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2784 artifacts:**

- **Ship code:** `core/views_platform_command.py` (module gate + 12 decorators), `core/tests/test_platform_auth_regression_2784.py` (new 236 lines), `tools/pa_local.sh` (+1/-1)
- **Handoff:** `docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md`
- **Predecessors:** S2783 handoff (wire GovernanceTab), S2782 handoff (substrate + C1)

🖥️ **Workspace UI — `/workspaces` surface:**

- **Self-Healing tab** — `?tab=system&sub=self-healing` (unchanged UI, now staff-gated: anon → 401, non-staff → 401/302, staff (Chris) → 200)
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 31 rows at S2784 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2784 open
  - `logs/recycle_events.jsonl` — +1 new event from S2784 close (`sha=814c2452d154`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `814c2452d` (S2784 ship) — cascade PR advances this at close |
| Playbook version | v0.7.0 (RATIFIED S2778) |
| Playbook rule count | 204 |
| RUR-C1 state | S2755→S2783 CLOSED · **S2784 authZ mitigation CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-f2bd82d8c76f4e32` (retired at S2784 close, force=true, fifteenth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-f2bd82d8c76f4e32` (retired; forces fresh mint at S2785 open) |
| Live infra state | S2755→S2783 substrate + **12 platform mutation endpoints now staff-only** |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2784 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3181) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **31 rows** (13 actionable / 12 mitigatable / 6 future_trigger) |
| Next move | Chris selects at S2785 open |

---

## Recommended session-open protocol (S2785)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2784 handoff §3 (Fold-framing correction novel-precedent) + §8 (open items)
4. **Freshness + regression 7-suite + ledger + eyeball verify + Playbook verify** — see S2785 open sequence above
5. **Watch for** ledger 31-row baseline surviving cascade merge; freshness FRESH · SHA-match; DecisionApprove endpoint audit as strong small-ship candidate
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — DecisionApprove auth audit is natural continuation of S2784
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2785 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2785:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.7.0 (latest ratified)
3. [`docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md`](docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md) — **S2784 handoff (current)**
4. [`docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md`](docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md) — S2783 handoff
5. [`docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md`](docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md) — S2782 handoff
6. [`docs/handoffs/SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md`](docs/handoffs/SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md) — S2781 handoff
7. `core/views_platform_command.py` — 12 staff-gated mutation endpoints
8. `core/views_governance.py:26-28` — canonical `_governance_staff_only` pattern (mirrored at S2784)
9. `core/tests/test_platform_auth_regression_2784.py` — S2784 auth regression file (28 tests)
10. `core/tests/test_governance_auth_regression_2780.py` — S2772 N16 contract citation
11. `logs/zoom_out_classifications.jsonl` — 31 rows
