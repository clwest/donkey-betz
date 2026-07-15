# Session 2789 — Broader PUBLIC_PATHS Audit + Pilot-Gates Prefix Gated

**Ship SHA:** `8cf1e73a2` · **PR:** [#3191](https://github.com/clwest/donkey-betz-platform/pull/3191) · **Date:** 2026-07-15

---

## §1 What shipped

Closed the S2788 Fold B row 41 `future_trigger` (proactive; the 4th-site
threshold had not fired). Broader PUBLIC_PATHS categorical audit surfaced 76
true-mutating ungated candidates across ~14 prefixes. This session gates one
prefix (`/api/pilot-gates/`) and lands the audit artifact for mechanical
S2790+ continuation.

**Backend (1 file):**

- `core/views_agent_learning.py` — added `@token_auth_required` on 7
  pilot-gates POST views:
  - `update_gate_status` (line 3712, POST /api/pilot-gates/<uuid>/status/)
  - `update_checklist_item` (line 3780, POST /api/pilot-gates/<uuid>/items/<uuid>/)
  - `create_pilot_gate` (line 3846, POST /api/pilot-gates/create/<uuid:decision_id>/) —
    classifier missed (custom `.create_for_decision()` factory, not
    `.objects.create()`); included for prefix-sweep completeness.
  - `start_pilot_execution` (line 3897, POST /api/pilot-gates/<uuid>/pilot/)
  - `complete_pilot_execution` (line 3979, POST /api/pilot-gates/<uuid>/pilot/<uuid>/complete/)
  - `regenerate_checklist_content` (line 4048, POST /api/pilot-gates/<uuid>/regenerate/)
  - `approve_all_checklist_items` (line 4104, POST /api/pilot-gates/<uuid>/approve-all/)

**Tests (1 new file):**

- `core/tests/test_pilot_gates_authz_sweep_2789.py` — 3 test classes × 7
  endpoints = 21 tests:
  - `PilotGatesAuthzSweepAnonymousTest` — anon → 401 (blocked)
  - `PilotGatesAuthzSweepAuthenticatedTest` — session-authed → view reached
  - `PilotGatesAuthzSweepTokenAuthS887PreservationTest` — Token-authed → view
    reached via `DisableCSRFForAuthEndpoints` middleware

**Audit artifact (2 new files):**

- `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` (87 lines) — categorized inventory
- `docs/audits/public_paths_audit_s2789.json` (76 candidate entries) —
  machine-readable for S2790+ mechanical continuation

---

## §2 Novel-precedent moments

### 2.1 First "audit-artifact-plus-prefix-gate" ship shape

S2787/S2788 gated 3-31 endpoints against direct evidence (CSRF/authZ). S2789
introduces the "audit artifact as first-class ship deliverable" pattern —
alongside the code gate, the PR ships a categorized inventory of what remains
so S2790+ can pick the next prefix mechanically. Adopted from Rigby T1 SIGN
tightening ("avoid illusion-of-coverage").

### 2.2 Rigby T1 SIGN caught a would-have-shipped bug

I proposed `@login_required` for the gate. Rigby's tool-grounded T1 (5
`repo_tool` calls into `auth_middleware.py`, `views_agent_learning.py`,
`_require_boardroom_staff` helper) rejected it: under PUBLIC_PATHS bypass,
`@login_required` 302-redirects anon to `LOGIN_URL` (HTML) rather than
returning JSON 401 — and doesn't accept Token headers. She pointed to the
existing `@token_auth_required` (auth_middleware.py:36-81) as the correct
decorator. Adopted immediately. **Anti-rubber-stamp discipline confirmed** —
this is the kind of substantive correction the check exists for.

### 2.3 Third Rigby SIGN response truncation observation

Row 44 `future_trigger` — S2786 T2 partial + S2787 T1 severe + S2789 T1
severe (Concern 2 lost, needed T2 dispatch to retrieve). S2788 handoff §6
marked 3rd as substrate-promotion candidate. Trigger met. Deferred to S2790+
as pa_chat.py / PA worker response-size cap investigation.

### 2.4 Classifier iteration mid-session

Ran three classifier versions in-session:

- v1 raw: 190 ungated mutating (POST + no auth marker)
- v2 MRO-aware: 120 (CBV parent-class permission_classes filtered)
- v3 mutation-evidence: 76 (POST-not-mutation false positives filtered per
  Rigby Concern 1)

Adopted v3 as the ship inventory. Kept v1/v2 buckets in JSON for verification.

### 2.5 Two `same_pr_actionable` folds from a single Rigby SIGN turn

Both from T1 (rows 42+43). Fold-authoring persistence-before-D-verdict
discipline (PLAYBOOK-6.10.8) had space to absorb both; adopting both this PR
kept scope tight. Previous session-per-fold cadence held; this is the second
"multi-fold-single-turn adoption" post-v0.8.0 codification.

---

## §3 T1 SIGN cycle summary

| Turn | Author | Content | Tool_runs | Outcome |
|---|---|---|---|---|
| T1 | Claude → Rigby | Scope proposal for 15-20 endpoints via `@login_required` + F1/F2/F3 F-BLOCKING + 3 zoom-out asks | Rigby: 7 (repo_tool reads on views_real_data.py, auth_middleware.py 2×, search process_request + _require_boardroom_staff, view_agent_learning.py; zoom_out_tool list 2×) | Rigby DISAGREE-with-substantive-correction on F2 (`@token_auth_required` not `@login_required`) + DISAGREE on `/api/agents/execute/` severity (returns random.uniform, not stateful) + 2 folds classified pre-verdict; response truncated mid-Concern-1 |
| T2 | Claude → Rigby | Ask for truncated Concern 2 only (<40 lines) | short | Concern 2 delivered clean — reaffirmed @login_required breakage; classified `same_pr_actionable` |
| T3 | Claude → Rigby | Final approval SIGN with folds persisted + full 11-suite green | Rigby: 5 (verified 7 decorators in views_agent_learning.py; tree of core/tests to check test file — test file not yet indexed) | AGREE-with-tightening (spot-check 7 decorators + artifacts in-tree) |
| T4 | Claude → Rigby | One-line verdict re-request | none | AGREE-with-tightening confirmed |

**Anti-rubber-stamp check:** T1 had 7 tool_runs and produced 2 substantive
DISAGREE corrections that would have shipped bugs. Discipline confirmed
working.

---

## §4 Ledger delta

- **At S2789 open:** 41 rows (17/15/9)
- **After T1 fold persistence (pre-D-verdict):** 44 rows (19/15/10)
  - Row 42 (S2789, classifier heuristic, `same_pr_actionable`): "Classifier
    heuristic false-positive: POST != DB mutation." Adopted this PR.
  - Row 43 (S2789, decorator choice, `same_pr_actionable`): "@login_required
    breaks S887 Token auth on PUBLIC_PATHS endpoints." Adopted this PR.
  - Row 44 (S2789, SIGN truncation, `future_trigger`): "3rd consecutive Rigby
    SIGN response truncation observation." Substrate-promotion trigger met.

---

## §5 Twin-pointer card

📁 **Repo `/` + `/docs/` — S2789 artifacts:**

- **Ship code:** `core/views_agent_learning.py` (7 decorator additions)
- **Tests:** `core/tests/test_pilot_gates_authz_sweep_2789.py` (193 lines, 21 tests)
- **Audit artifacts:** `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` (87 lines) +
  `docs/audits/public_paths_audit_s2789.json` (1321 lines, 76 candidates)
- **Handoff:** `docs/handoffs/SESSION_2789_BROADER_PUBLIC_PATHS_AUDIT.md` (this file)
- **Predecessors:** S2788 (Fold C 3-endpoint sweep), S2787 (CSRF cross-file
  cleanup), S2786 (Playbook v0.8.0)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — 44 rows,
  including S2789 rows 42/43/44
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 44 rows at S2789 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2789 open
  - `logs/recycle_events.jsonl` — +1 new event from S2789 close (`sha=8cf1e73a29fa`)

---

## §6 Open items forward-carry

1. **Remaining 75 true-mutating candidates** across ~14 prefixes (per
   `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md`) — per-prefix ships for S2790+.
   Priority ordering:
   - HIGH: `/api/time-travel/` (11), `/api/teams/` (6), `/api/distribution/` (6), `/api/legal/cases/` (6)
   - MEDIUM: `/api/v1/research/self-blog/` (6), `/api/experiments/` (3), `/api/initiatives/` (2)
   - LOW: `/api/memory-clusters/` (4), `/api/agent-evolution/` (5), `/api/memory-palace/` (2), etc.
2. **Rigby SIGN response truncation substrate fix** — row 44 `future_trigger`
   now at 3-trigger; investigate pa_chat.py / PA worker response-size cap.
3. **N24 anti-rubber-stamp SIGN codification** — S2789 T1 was
   DISAGREE-with-substantive-correction (F-BLOCKING equivalent since it
   would have shipped bugs). Now at 5 F-BLOCKING triggers total
   (S2778/S2780/S2786/S2787 + S2789). Promotion candidate strong.
4. **Zoom-out fold candidate (recorded in audit doc, not persisted to
   ledger):** 263 PUBLIC_PATHS prefixes + 76 unresolved suggests the
   middleware+prefix-allow-list is the wrong pattern. Future ADR sketch
   for `@public_endpoint` opt-in decorator.
5. **Untracked audit files** — 7 `SESSION_819_SYSTEM_AUDIT_*` files in
   `docs/audits/` triggered by `s2787-csrf-pass-fixture` cron/webhook.
   Deferred cleanup (gitignore or delete).
6. All prior S2788 open runtime items forward-carry unchanged unless S2789
   changed them:
   - #1 Broader PUBLIC_PATHS categorical audit → **PARTIALLY CLOSED**
     (audit shipped, 1 prefix gated, 13+ remain)
   - #3 Rigby SIGN truncation → **NOW 3-TRIGGER** (row 44 future_trigger)
   - Others unchanged.

---

## §7 Rebindings post-merge

- **Ledger:** 44 rows (19 actionable / 15 mitigatable / 10 future_trigger)
- **Rule count:** 205 (unchanged; no Playbook amendment)
- **Playbook version:** v0.8.0 (unchanged)
- **Session pin:** `pa-900603b3356549d9` (S2789) — retire at close per
  S2770+ pattern with `force=true`
- **Wrapper default pin:** to be updated with fresh mint at S2790 open
  (forcing function preserved)
- **Regression 10-suite → 11-suite:** now includes
  `test_pilot_gates_authz_sweep_2789` (21 tests). Total: 191 tests OK.

---

## §8 Post-merge cascade

- ✅ `make recycle-all` (PLAYBOOK-7.4.4, twenty-seventh close-cycle) —
  sha `8cf1e73a29fa`, `logs/recycle_events.jsonl` +1 event
- ⏳ Cascade PR: handoff + start-here + INDEX + provenance
- ⏳ Docs cascade: `build_docs_index` → `build_rag_corpus` →
  `sync_docs_index_to_documents --embed`
- ⏳ Pin retire with `force=true`
