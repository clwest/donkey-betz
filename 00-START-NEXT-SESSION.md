# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2780 CLOSED — N22 v3 SHIPPED (zoom_out_tool factor-out + SIGN Ledger UI)

**Refreshed 2026-07-13 (SESSION 2780 CLOSED — N22 v3 shipped as PR #3172, merged as `b16b3b981`. Same-session discharge of the S2779 V6 fold's `future_trigger` — Trigger B ("first non-Rigby consumer of zoom_out_ledger") fired with the UI ship, and the corresponding amendment (factor-out to dedicated `zoom_out_tool`) shipped in the same PR per PLAYBOOK-6.10.8 discipline. First in-wild example of the future_trigger→amendment loop closing without a gap session. Third F-BLOCKING DISAGREE of the S2771 streak (V1 Trigger B disposition + V3 canonical home) — resolved by SCOPE EXPANSION rather than reduction. Rigby's anti-rubber-stamp gate caught two BLOCKING design leans on turn 1. Ledger grew 18 → 20 rows (V7 folds A + B classified `same_pr_actionable` + persisted before D-verdict). Sixteenth close-cycle post-PLAYBOOK-7.4.4-codification. Chris D-verdict: "A: factor-out + UI".)**

**S2780 shipped as 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **New PA tool:** `core/services/td_handlers_governance.py` — `GovernanceHandlersMixin` with `_handle_zoom_out` + `_zoom_out_list` (moved from `_ops_zoom_out_ledger`). LLM autofill guard for `session=0` per `_d14_resolve_min_session` pattern.
- **New tool schema:** `zoom_out_tool` in `pa_tool_schemas.py` — action `list`, filters `{session, classification, arc, limit}`.
- **New tool dispatch:** `tool_dispatcher.py` — `GovernanceHandlersMixin` added to MRO; `zoom_out_tool` registered.
- **Removed:** `ops_tool.zoom_out_ledger` action + `_ops_zoom_out_ledger` handler + orphaned params from `ops_tool` schema.
- **New REST endpoint:** `/api/governance/zoom-out-ledger/` in `core/views_governance.py` — separate namespace from `/api/ops/*` respects S2774 pause + preserves semantic boundary.
- **New Workspace sub-tab:** `system.sign-ledger` (label "SIGN Ledger", ScrollText icon) → `ZoomOutLedgerSection.tsx`. Advisory-posture-first UI (banner + repeat + `is_gate: false`), non-severity color palette (indigo/slate/amber), inline help toggle, 4 filter controls.
- **OpsConsole preview card:** compact link → `?tab=system&sub=sign-ledger` for discoverability without semantic mixing.
- **Test suites:** 21 tests in `test_zoom_out_tool_2780.py` (10 contracts) + 5 tests in `test_governance_auth_regression_2780.py` + route-inventory guard.
- **Removed:** `test_ops_zoom_out_ledger_2779.py` (superseded).
- **Handoff:** `docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md`.
- **Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 (sixteenth cycle).
- **Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 20 rows (11 same_pr_actionable / 7 same_pr_mitigatable / 2 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2780)

S2780 opened with FRESH pin `pa-922038da42334842` (no STALE_BOTH this session — S2779 close ceremony's second recycle stayed fresh). 5-suite regression baseline 83/83 PASS.

**Anti-rubber-stamp gate PASS on turn 1** — Rigby returned 6+ real `search_docs` + `repo_tool` invocations on the T1 SIGN dispatch. Discipline held.

**T1 V1 F-BLOCKING DISAGREE:** Rigby caught that Trigger B (first non-Rigby consumer of zoom_out_ledger) fires with this PR, and per PLAYBOOK-6.10.8 `future_trigger` discipline that means same-PR factor-out — not deferrable. I had proposed shipping the UI as a new consumer of `ops_tool.zoom_out_ledger`; Rigby's tool-grounded reading of the rule text corrected me.

**T1 V3 F-BLOCKING DISAGREE:** Rigby caught that OpsConsoleTab is the wrong canonical home for a governance-scope ledger (semantic boundary erosion). She proposed GovernanceTab (dead code in this repo — never mounted) OR a dedicated sub-tab. I chose the dedicated sub-tab route since GovernanceTab wire-up is separate work.

**T1 V7 zoom-out folds:** 2 folds surfaced, both classified `same_pr_actionable` (semantic boundary + trigger B mandate). Persisted to ledger rows 19 + 20 BEFORE D-verdict per PLAYBOOK-6.10.8.

**Chris D-verdict "A":** authorize expanded scope (factor-out + UI). One turn, no revision needed.

**Live smoke exposed autofill bug:** initial `_zoom_out_list` treated `session=0` (LLM autofill idiom) as "filter to session 0" and dropped everything. Fixed with same guard as `_d14_resolve_min_session` (session > 0 only). Regression test added.

---

## THE PIVOT — WHY THIS SHIP MATTERS

**Substrate arc N22 is now 3 sessions deep** — S2777 write path → S2778 constitutional codification → S2779 read surface → S2780 factor-out + UI. Four coherent shipments; each session's fold or trigger determined the next session's work.

**S2780 closed the future_trigger→amendment loop in a single session.** S2779 fold classified `future_trigger` on trigger B ("first non-Rigby consumer"); S2780's Chris-facing UI IS the trigger firing; the corresponding factor-out shipped in the same PR. Prior in-wild examples had a session gap between trigger firing and amendment (e.g., memory rule authored → apply → codify pattern). S2780 is the first same-session close.

**F-BLOCKING was resolved by scope EXPANSION, not reduction.** Prior F-BLOCKINGs (S2776 Q1, S2778 V1) trimmed the ship. S2780 V1 said "you're shipping too little" and expanded scope to include factor-out. Chris authorized the expansion in one turn.

**Anti-rubber-stamp gate paid off twice on turn 1.** Rigby's tool-grounded verification caught two BLOCKING design leans (V1 + V3) that would have shipped semantically-mixed code with a misclassified trigger. Both catches required reading rule text (PLAYBOOK-6.10.8) or the actual frontend structure (GovernanceTab dead-code discovery) — not something the LLM would have surfaced from priors alone.

**S2771 rule streak now covers 10 sessions (S2771–S2780)** with 3 F-BLOCKING DISAGREEs and 1 constitutional codification. No drift into ritual.

---

## S2781 CANDIDATES (Chris selects at open)

### First — visual verification of S2780 ship

**Chris eyeball verification** is the last-mile check for N22 v3 per `feedback_last_mile_ui`. Hard-refresh `localhost:8000/workspace?tab=system&sub=sign-ledger` and confirm:
- Amber advisory banner at top ("advisory pattern evidence — not gates")
- Counts row with color-coded classification badges
- Filter chips (session / classification / arc / limit selector)
- 20 ledger rows visible with concern_text + evidence_ref + timestamps
- OpsConsole tab (`?tab=system&sub=ops`) shows a preview card near recycles → click hops to SIGN Ledger

If any of the above is missing/broken, that's the first fix.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **N17** — `session_number` pill in the search chip when text is set — small UX polish. Non-ops-surface, not gated.
- **N24** — Anti-rubber-stamp SIGN codification (Playbook MINOR). 2 triggers observed (S2777 T1 catch + S2778 V1 catch). S2780 T1 gate PASS on TWO F-BLOCKINGs is not a new trigger (rule already followed). Ready when authorized.
- **First N22 v2 usage in-wild by Rigby** — Watch for Rigby actually consulting `zoom_out_tool.list` during her own SIGN loops this session.
- **Wire GovernanceTab into WorkspacePageNew** — dead-code cleanup; would surface the self-healing UI alongside the SIGN Ledger.
- **New spider / agent capability / dashboard** — something else you have in mind.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit.

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap) — trigger unchanged
- **N22 v2 time-window filters** (`since` / `before`) — deferred until ledger has ~50+ rows temporal spread (currently 20)
- **N22 v4+ candidates** — Django model, JSONL rotation (~500 rows away), auto-hook into ratification envelope creation

### Post-S2780 owed

- **I-0302 three-PR pattern amendment** — when it opens, take PLAYBOOK-6.10.9 (per S2778 sequencing note).
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — watch for `record_zoom_out_concern` command failure that invokes the fallback path.
- **Second SIGN Ledger consumer** — if a non-Rigby, non-Workspace consumer emerges (Slack, mobile, external dashboard), `zoom_out_tool` abstraction gets exercised heterogeneously.

---

## SESSION PIN — S2780 RETIRED (fresh mint required at S2781 open)

**Pin history (S2780):**

- `pa-922038da42334842` (label `s2780-n22v3-zoom-out-ledger-workspace-tab`) minted S2780 open; **retired at S2780 close (force=true, ELEVENTH consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-922038da42334842` (retired)** — intended failure mode forces S2781 first-action fresh mint.

**S2781 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2780 handoff §2 (novel-precedent moments) + §9 (meta-observation on arc coherence)

# Freshness check. Should be FRESH · SHA-match at S2780 close SHA (b16b3b981) — SIXTEENTH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2781 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# NEW: verify SIGN Ledger PA tool + endpoint still work post-merge
bash tools/pa_local.sh "S2781 open — smoke zoom_out_tool.list (default) — confirm 20-row baseline + advisory posture intact"

# Regression check: 7-suite ops+governance stack
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_session_freshness_2775 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  --noinput

# Ledger check: confirm 20-row baseline survived merge
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
start = d.find('{')
r = json.loads(d[start:])
assert r['total_rows']==20, r
print('OK — 20 rows, counts:', r['counts_by_classification'])
"

# Playbook v0.7.0 verify — new rules still present
grep -c 'PLAYBOOK-6\.10\.[7-8]' docs/ENGINEERING_PLAYBOOK.md  # expect >=5

# Browser eyeball (Chris's task):
#   /workspace?tab=system&sub=sign-ledger — SIGN Ledger tab renders?
#   /workspace?tab=system&sub=ops — preview card visible?

# Mint fresh pin scoped to selected S2781 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2781 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 constitutional at v0.7.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; any folds MUST be classified + persisted BEFORE D-verdict. Rigby can now consult prior folds via `zoom_out_tool.list` (dedicated tool) OR via the Workspace SIGN Ledger tab (Chris eyeball).

---

## OPEN RUNTIME ITEMS (from S2780 close)

1. **N17 / N24 net-new engineering** — see Candidates above
2. **Chris eyeball verification of N22 v3 UI** — `localhost:8000/workspace?tab=system&sub=sign-ledger`
3. **S2761 smoke test** — ops-surface (gated)
4. **S2758 D2 canonical decision** — needs joint SIGN (governed by v0.7.0)
5. **S2758 D4 HIGH-RISK wiring extension** — REPORT-ONLY
6. **N13 handoff-date-format normalizer** — hygiene
7. **P0.5 cost-threshold advance-to-freeze**
8. **P0.75 CI billing**
9. **RUR-C2 open eligible**
10. **S2758 D1 process_pa_chat_task payload strip**
11. **S2758 D5 local shim retirement**
12. **HMAC signing of `x-acting-user-id`**
13. **Memory rule promotion audit** — N24 anti-rubber-stamp SIGN at 2 triggers (S2780 T1 held, not new trigger)
14. **First observed partial-recycle event** — N10/N11 trigger
15. **Rigby S2774 forward-carry: ops-surface PR pause** — still held; N22 v3 REST used `/api/governance/*` so unaffected
16. **30+ other lambda-`__import__` sites** — refactor when arc naturally touches
17. **Rigby S2773 forward-carry #5 (health_summary overlap)** — trigger unchanged
18. **N15 v2 candidates** — deferred pending row accumulation
19. **N21 v2 candidates** — deferred pending trigger
20. **`session_lifecycle` refactor trigger** — still armed
21. **`/api/pa/*` future-endpoint audit trigger** — every proposal must satisfy the sharp 5-point test
22. **N22 v4+ candidates** — Django model, JSONL rotation (~500 rows away), auto-hook
23. **N22 v2 time-window filters** — deferred until ~50+ rows temporal spread (currently 20)
24. **N24 anti-rubber-stamp SIGN codification** — 2 triggers; ready when authorized
25. **I-0302 three-PR pattern amendment** — take PLAYBOOK-6.10.9 when it opens
26. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
27. **Second SIGN Ledger consumer** — abstraction quality test if one emerges
28. **Wire GovernanceTab into WorkspacePageNew** — dead-code cleanup (self-healing UI absent from mount)
29. **Postgres cleanup follow-ups (S2774 carryover):**
    - Decide whether to `brew uninstall postgresql@16`
    - Decide whether to drop pg15's `test_unified_donkey_betz` DB

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2780 artifacts:**

- **New PA tool:** `core/services/td_handlers_governance.py` (`GovernanceHandlersMixin`)
- **Tool schema:** `core/services/pa_tool_schemas.py` (new `zoom_out_tool`)
- **Tool dispatch:** `core/services/tool_dispatcher.py`
- **REST endpoint:** `core/views_governance.py` (`/api/governance/zoom-out-ledger/`)
- **URL wiring:** `core/urls.py`
- **Backend tests:** `core/tests/test_zoom_out_tool_2780.py` + `core/tests/test_governance_auth_regression_2780.py`
- **UI component:** `frontend/src/pages/workspace/tabs/ZoomOutLedgerSection.tsx`
- **UI mount:** `frontend/src/pages/WorkspacePageNew.tsx` (`system.sign-ledger` sub-tab)
- **Types:** `frontend/src/pages/workspace/types.ts` (`'sign-ledger'` in `WorkspaceTab` union)
- **OpsConsole preview:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`
- **Handoff:** `docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md`
- **Substrate:** `core/management/commands/record_zoom_out_concern.py` (write path, S2777)
- **CLI companion:** `core/management/commands/zoom_out_streak_report.py`
- **Constitutional:** `docs/ENGINEERING_PLAYBOOK.md` §6.10.7-§6.10.8 (v0.7.0, S2778)

🖥️ **Workspace UI — `/workspaces` surface:**

- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — Playbook v0.7.0 envelope + content mirror
- **NEW: Workspace → System → SIGN Ledger** (`?tab=system&sub=sign-ledger`) — Chris-facing zoom-out concern ledger
- **NEW: OpsConsole preview card** (`?tab=system&sub=ops`) — discoverability link to SIGN Ledger
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 20 rows at S2780 close
  - `logs/session_freshness.jsonl` — 5 rows (grows +1 per session_lifecycle open)
  - `logs/recycle_events.jsonl` — grows per `make recycle-all`
  - `zoom_out_tool.list` — Rigby PA-tool surface
  - `GET /api/governance/zoom-out-ledger/` — Chris frontend surface

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `b16b3b981` (S2780 close, N22 v3 merge) |
| Playbook version | v0.7.0 (RATIFIED S2778) |
| Playbook rule count | 204 |
| RUR-C1 state | S2755→S2779 CLOSED · **S2780 N22 v3 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-922038da42334842` (retired at S2780 close, force=true, eleventh consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-922038da42334842` (retired; forces fresh mint at S2781 open) |
| Live infra state | S2755→S2779 substrate + **N22 v3 PA-tool factor-out + Workspace UI live** |
| Postgres :5432 | pg15 (July DB, S2780 state) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — 5 rows (S2780 pin mint added 1) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **20 rows** (11 actionable / 7 mitigatable / 2 future_trigger) |
| Next move | Chris selects at S2781 open (start with N22 v3 UI eyeball) |

---

## Recommended session-open protocol (S2781)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2780 handoff §2 (novel-precedent moments — same-session future_trigger discharge, F-BLOCKING via scope expansion) + §9 (meta-observation on 3-session arc coherence)
4. **Freshness + regression + ledger + zoom_out_tool smoke + Playbook verify + browser eyeball** — see S2781 open sequence in §SESSION PIN above
5. **Watch for** the N15 fifth natural row landing at S2781 pin mint + N21 prelude firing at first bash invocation of the new pin + ledger 20-row baseline surviving merge + `zoom_out_tool.list` returning advisory posture + SIGN Ledger sub-tab reachable in browser
6. If `staleness_verdict != FRESH` → escalate to Chris (sixteenth-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
7. **Check `brew services list | grep postgres` FIRST** if freshness fails in unusual pattern
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — Chris eyeball verification of N22 v3 SIGN Ledger UI first, THEN net-new engineering candidate
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty (N24 codification pending 3rd trigger)
11. Chris directs S2781 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2781:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — **v0.7.0 (latest ratified)**
3. [`docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md`](docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md) — S2780 handoff
4. [`docs/handoffs/SESSION_2779_N22V2_ZOOM_OUT_LEDGER_READ_SURFACE.md`](docs/handoffs/SESSION_2779_N22V2_ZOOM_OUT_LEDGER_READ_SURFACE.md) — S2779 handoff (N22 v2 substrate)
5. [`docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`](docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md) — S2778 handoff (constitutional codification)
6. `core/services/td_handlers_governance.py` `_zoom_out_list` — S2780 read path handler
7. `core/views_governance.py` — S2780 REST endpoint
8. `frontend/src/pages/workspace/tabs/ZoomOutLedgerSection.tsx` — S2780 UI component
9. `core/management/commands/record_zoom_out_concern.py` — write path (constitutional per PLAYBOOK-6.10.8)
10. `logs/zoom_out_classifications.jsonl` — 20 rows; grows per PLAYBOOK-6.10.8
