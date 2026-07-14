# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2785 CLOSED — DECISION-APPROVE AUTH AUDIT (C-lite; third same-arc continuation)

**Refreshed 2026-07-14 (SESSION 2785 CLOSED — third session in the S2783→S2784→S2785 authZ arc, ~1h. PR #3183 (`130955ec`) gates 15 /api/human/* class-based views + 4 /api/boardroom/decisions/* mutation endpoints — same S2772 N16 contract now applied to 3 more files/19 more endpoints. views_human_interface.py: decorator swap on 15 CBVs (adds _human_staff_only to @method_decorator stack). views_agent_learning.py: extracts _require_boardroom_staff inline helper on 4 boardroom endpoints, **preserving the S887 Token auth codepath** — C-lite over C because decorator gating would have redirected Token requests before falling through to Token auth logic. New regression test file (358 lines, 45 tests). Full 4-suite auth sweep clean (93 tests OK across ops_2772 + governance_2780 + platform_2784 + decision_approve_2785). Novel: **Fold-authoring drift RECURRED (2nd trigger)** — original 'boardroom completely ungated' claim was wrong; Rigby tool_read revealed inline authN + Token fallback. Two triggers of the fold-authoring hygiene pattern = **Playbook amendment candidate**, ready for codification. Also novel: **longest same-arc-continuation streak observed** — 3 sessions of continuous authZ work, no gap sessions, no scope drift. Chris E2E verified by approving + dismissing decisions in DecisionDetailModal under the new gate. Post-merge `make recycle-all` clean — TWENTY-SECOND close-cycle post-PLAYBOOK-7.4.4 codification. Ledger grew 31 → 34 rows.)**

**S2785 ship:**

**PR #3183 · `130955ec`** — `core/views_human_interface.py` (15 CBV decorator swaps + module gate), `core/views_agent_learning.py` (4 boardroom endpoints + `_require_boardroom_staff` helper extraction), `core/tests/test_decision_approve_auth_regression_2785.py` (new, 358 lines / 45 tests), `tools/pa_local.sh` (+1/-1 pin refresh)

**Handoff:** `docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (twenty-second cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 34 rows (15 same_pr_actionable / 13 same_pr_mitigatable / 6 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2785)

Third session-in-session opener. S2785 continued the authZ arc immediately after S2784 close with no gap. Chris chose the DecisionApprove audit candidate — the natural continuation of S2784's Fold 4 mitigation and the direct follow-up to his eyeball-verify question about the DecisionDetailModal Approve/Dismiss buttons.

Investigation revealed the decision-approve surface spans **3 files with 3 different auth postures**:
- ✅ `views_diagnostics.py` — already `@superuser_required` (properly gated; no change)
- ⚠️ `views_human_interface.py` — 15 CBVs with `@login_required` decorator only (authN, no authZ)
- ⚠️ `views_agent_learning.py` — 4 boardroom endpoints with inline authN + **S887 Token auth fallback** (authN with Token support, no authZ)

Initial audit claimed boardroom endpoints were "completely ungated." Rigby's tool_read of `views_agent_learning.py:2105-2195` revealed the actual state — inline authN with Token auth fallback. **Fold-authoring drift recurred (2nd trigger of S2784 Fold 31).** Corrected framing routed to Chris as C-lite (extract inline helper rather than decorator swap, to preserve Token codepath) → D-verdict.

Implementation was two-file surgical: decorator swap on 15 CBVs, helper extraction on 4 endpoints. Full 4-suite auth sweep clean (93 tests). Chris E2E-verified by approving + dismissing decisions in DecisionDetailModal under the new gate.

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**S2772 N16 contract's reach is now three files across three sessions.** The "governance/platform endpoints MUST be login_required AND staff-only" rule now applies to 4 files: `views_governance.py` (S2780) + `views_platform_command.py` (S2784) + `views_human_interface.py` (S2785) + `views_agent_learning.py` (S2785 boardroom). 20 additional endpoints gated this session, 44 total endpoints across the 4 files.

**Fold-authoring drift is now a 2-trigger pattern.** Both S2784 Fold 31 and S2785 Fold 32 recorded the same phenomenon: initial fold characterization understated or overstated the actual code state, driving mis-scoped mitigation work. Ready for Playbook §6 amendment. Suggested rule: "when recording a zoom-out fold that names a specific code gap, verify the gap's actual character (BOTH decorator AND inline runtime auth blocks for auth gaps) before persistence."

**C-lite design decision preserved a real feature.** Naive decorator gating would have broken the S887 Token auth codepath (`@login_required` redirects unauthenticated to `/accounts/login/` BEFORE the view body runs → Token auth callers get 302 instead of 200/400/500). **New precedent:** for endpoints with non-standard authN (Token, custom middleware, etc.), extract inline helper; don't layer decorators. Codified in `_require_boardroom_staff` helper pattern.

**Third consecutive arc-continuation session.** S2783 wired GovernanceTab → S2784 gated 12 platform mutations → S2785 audits + gates 19 decision-approve endpoints. Each session's eyeball-verify or investigation drove the next session's P0. No gap sessions, no scope drift. Longest same-arc streak observed.

---

## S2786 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired; freshness should be FRESH · SHA-match at S2785 close SHA.
**Ledger baseline:** 34 rows expected (15/13/6). Any drift = investigate.
**Regression 8-suite:** now includes `test_decision_approve_auth_regression_2785` (see updated open sequence below).

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **Fold-authoring hygiene Playbook amendment (v0.7.1 PATCH)** — 2 triggers observed (S2784 Fold 31 + S2785 Fold 32); ready for codification. Small ship (~30 LOC Playbook edit + ratification envelope + workspace deliverable). Closes a meta-substrate gap; blocks fewer future fold-mischaracterizations.
- **CSRF exemption cross-file cleanup** — S2784+S2785 combined = 31 mutation endpoints with `@csrf_exempt` (12 platform + 15 human + 4 boardroom). Cross-file substrate PR. Frontend must start sending CSRF tokens; not just decorator swap. **Non-trivial (~1-3h)** — requires frontend fetch layer update + backend decorator removal + full E2E test that mutations still work from GovernanceTab.
- **Auth-gate consolidation** — 3 files each define their own `_*_staff_only = user_passes_test(...)` sentinel. Single shared `core/auth_gates.py` module candidate. Non-urgent (3 sentinels is not painful yet); watch for 4th before promoting.
- **AudioAgent completion-flip verification** — C1 linkage live; awaiting next timeout for one-query verification.
- **Model drift arc** — 38 unrelated auto-migrations queued.
- **Something entirely new** — new spider / UI page / agent capability / pipeline / dashboard. Fresh direction OK.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit.

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 34)
- **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — Rigby's 4-session dogfooding was under my prompts, not autonomous
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **4th auth-gate sentinel** — trigger for consolidation into `core/auth_gates.py`

### Post-S2785 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.9 slot when opened
- **Fold-authoring hygiene Playbook amendment** (see net-new — ready)
- **CSRF exemption cleanup on 31 mutation endpoints** (see net-new)
- **AudioAgent completion-flip verification**
- **`test_session_freshness_2775` env drift**
- **Ledger split drift audit** — 12/8/2 → 12/8/3 shift at S2782 open

---

## SESSION PIN — S2785 RETIRED (fresh mint required at S2786 open)

**Pin history (S2785):**

- `pa-ad6b2c423b514728` (label `s2785-decision-approve-audit`) minted S2785 open; **retired at S2785 close (`force=true`, sixteenth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-ad6b2c423b514728` (retired)** — intended failure mode forces S2786 first-action fresh mint.

**S2786 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2785 handoff §2 (Fold-authoring drift 2nd trigger + longest same-arc streak) + §3 (C-lite design principle) + §8 (open items)

# Freshness check. Should be FRESH · SHA-match at S2785 close SHA (130955ec) — TWENTY-SECOND close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2786 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Self-Healing tab + DecisionDetailModal still work as staff (Chris eyeball)
# http://localhost:8000/workspace?tab=system&sub=self-healing

# Ledger check: confirm 34-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==34, r
print('OK — 34 rows, counts:', r['counts_by_classification'])
"

# Regression 8-suite (NEW: adds test_decision_approve_auth_regression_2785)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  core.tests.test_platform_auth_regression_2784 \
  core.tests.test_decision_approve_auth_regression_2785 \
  --noinput

# Playbook v0.7.0 verify — rules still present
grep -c 'PLAYBOOK-6\.10\.[7-8]' docs/ENGINEERING_PLAYBOOK.md  # expect >=5

# Mint fresh pin scoped to selected S2786 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2786 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 constitutional at v0.7.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict.

---

## OPEN RUNTIME ITEMS (from S2785 close)

1. **Fold-authoring hygiene Playbook amendment** (2 triggers observed; ready for v0.7.1 PATCH — natural S2786 P0 candidate)
2. **CSRF exemption cross-file cleanup** — 31 mutation endpoints across 3 files
3. **Auth-gate consolidation** — 3 sentinel modules; wait for 4th before consolidation
4. **AudioAgent completion-flip verification** (C1 linkage live, 0 rows populated)
5. **`test_session_freshness_2775` env drift**
6. **Model drift arc** (38 unrelated auto-migrations queued)
7. **Ledger split drift audit** (12/8/2 → 12/8/3 shift at S2782 open)
8. **S2761 smoke test** (ops-surface, gated)
9. **S2758 D2 canonical decision** (needs joint SIGN)
10. **S2758 D4 HIGH-RISK wiring extension** (REPORT-ONLY)
11. **N13 handoff-date-format normalizer** (hygiene)
12. **P0.5 cost-threshold advance-to-freeze**
13. **P0.75 CI billing**
14. **RUR-C2 open eligible**
15. **S2758 D1 process_pa_chat_task payload strip**
16. **S2758 D5 local shim retirement**
17. **HMAC signing of `x-acting-user-id`**
18. **Memory rule promotion audit** — N24 anti-rubber-stamp SIGN at 2+ triggers
19. **First observed partial-recycle event** — N10/N11 trigger
20. **Rigby S2774 forward-carry: ops-surface PR pause** — held; S2785 was in-scope
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
31. **N24 anti-rubber-stamp SIGN codification** — 2+ triggers; ready when authorized
32. **I-0302 three-PR pattern amendment** — take PLAYBOOK-6.10.9 when it opens
33. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
34. **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
35. **S2783 Fold 1 same-PR mitigation deferred** (GovernanceTab subtitle if label confusion appears)
36. **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
37. **4th auth-gate sentinel trigger** — consolidation into `core/auth_gates.py`
38. **Postgres cleanup follow-ups (S2774 carryover)**

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2785 artifacts:**

- **Ship code:** `core/views_human_interface.py` (15 CBV decorator swaps + `_human_staff_only` gate), `core/views_agent_learning.py` (4 boardroom endpoints + `_require_boardroom_staff` helper), `core/tests/test_decision_approve_auth_regression_2785.py` (new 358 lines), `tools/pa_local.sh` (+1/-1)
- **Handoff:** `docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md`
- **Predecessors:** S2784 handoff (platform mutations), S2783 handoff (wire GovernanceTab)

🖥️ **Workspace UI — `/workspaces` surface:**

- **Self-Healing tab** (`?tab=system&sub=self-healing`) — DecisionDetailModal Approve/Dismiss buttons now backed by staff-only endpoint (anon → 401, non-staff → 401/302, staff (Chris) → 200)
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 34 rows at S2785 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2785 open
  - `logs/recycle_events.jsonl` — +1 new event from S2785 close (`sha=130955ec07ea`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `130955ec` (S2785 ship) — cascade PR advances this at close |
| Playbook version | v0.7.0 (RATIFIED S2778) |
| Playbook rule count | 204 |
| RUR-C1 state | S2755→S2784 CLOSED · **S2785 decision-approve authZ CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-ad6b2c423b514728` (retired at S2785 close, force=true, sixteenth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-ad6b2c423b514728` (retired; forces fresh mint at S2786 open) |
| Live infra state | S2755→S2784 substrate + **44 endpoints across 4 files staff-only gated (governance+platform+human+boardroom)** |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2785 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3183) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **34 rows** (15 actionable / 13 mitigatable / 6 future_trigger) |
| Next move | Chris selects at S2786 open |

---

## Recommended session-open protocol (S2786)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2785 handoff §2 (novel-precedent moments) + §3 (C-lite design principle) + §8 (open items)
4. **Freshness + regression 8-suite + ledger + eyeball verify + Playbook verify** — see S2786 open sequence above
5. **Watch for** ledger 34-row baseline surviving cascade merge; freshness FRESH · SHA-match; fold-authoring hygiene Playbook amendment as strong small-ship candidate (ready for v0.7.1 PATCH)
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — Fold-authoring hygiene rule (Playbook v0.7.1) is natural closure of the arc's meta-substrate learning
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2786 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2786:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.7.0 (latest ratified); v0.7.1 PATCH candidate ready
3. [`docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md`](docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md) — **S2785 handoff (current)**
4. [`docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md`](docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md) — S2784 handoff
5. [`docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md`](docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md) — S2783 handoff
6. [`docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md`](docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md) — S2782 handoff
7. `core/views_human_interface.py` — 15 staff-gated CBVs + `_human_staff_only`
8. `core/views_agent_learning.py` — 4 staff-gated boardroom endpoints + `_require_boardroom_staff` helper (S887 Token codepath preserved)
9. `core/tests/test_decision_approve_auth_regression_2785.py` — S2785 auth regression file (45 tests)
10. `logs/zoom_out_classifications.jsonl` — 34 rows
