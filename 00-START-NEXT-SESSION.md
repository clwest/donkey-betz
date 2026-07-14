# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2786 CLOSED — PLAYBOOK v0.8.0 MINOR RATIFIED (PLAYBOOK-6.10.9 fold-authoring evidence admission)

**Refreshed 2026-07-14 (SESSION 2786 CLOSED — third consecutive constitutional MINOR shipped in same-session shape after v0.6.0/S2766 and v0.7.0/S2778. PR #3185 (`d6859acfa`) codifies PLAYBOOK-6.10.9: zoom-out folds asserting concrete code-state facts MUST admit stable-state-pointer (commit SHA; PR/branch refs MUST include SHA under review) + file+line evidence + (i)/(ii)/(iii) verified-state outcome inline in SIGN attestation before classify+persist. First MINOR shipped from a ledger-enumerable two-trigger corpus — row 31 (S2784 T2 Fold 4 "no auth gating" → actual authN-present/authZ-absent) + row 32 (S2785 T1 Fold 1 "completely ungated" → actual inline-authN-with-Token-fallback). Third F-BLOCKING DISAGREE of the S2771-rule streak — Rigby T2 caught "at HEAD" underspecification (HEAD moves after attestation; not replayable) driving T4 revision cycle: hygiene → evidence admission reframe + stable-state-pointer requirement. Substrate dogfooding extended: 2 folds persisted BEFORE D-verdict per PLAYBOOK-6.10.8 (Fold A `same_pr_mitigatable` drove the rule-text reframing; Fold B `future_trigger` recorded as §6.12 helper extension-point note). Ledger 34 → 36 rows. Rule count 204 → 205. I-0302 three-PR candidacy re-slotted forward again to PLAYBOOK-6.10.10 per PLAYBOOK-10.7.5. Post-merge `make recycle-all` clean — TWENTY-THIRD close-cycle post-PLAYBOOK-7.4.4 codification.)**

**S2786 ship:**

**PR #3185 · `d6859acfa`** — `docs/ENGINEERING_PLAYBOOK.md` (v0.7.0 → v0.8.0: new rule 6.10.9 + §6.10 commentary extension + new §6.12 helper extension-point note + Appendix D v0.8.0 row + frontmatter version bump), `docs/research/implementation/RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0.md` (new 201-line envelope), `CLAUDE.md` (anchor bumped to v0.8.0), `tools/pa_local.sh` (+1/-1 pin refresh)

**Handoff:** `docs/handoffs/SESSION_2786_PLAYBOOK_V0_8_0_RATIFIED.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (twenty-third cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 36 rows (15 same_pr_actionable / 14 same_pr_mitigatable / 7 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2786)

Third consecutive constitutional session. Chris selected the fold-authoring hygiene amendment at S2786 open as natural closure of the S2784 + S2785 meta-substrate learning (both sessions surfaced fold-authoring drift as `same_pr_mitigatable` in-flight; two triggers ready for codification).

Author-side draft framed the rule as "fold-authoring hygiene" with "at HEAD" verification. Rigby's T2 tool-grounded SIGN caught two things: **(a) F-BLOCKING** on "at HEAD" underspecification — HEAD moves after attestation; verification isn't replayable — and **(b)** zoom-out Fold A `same_pr_mitigatable` proposing the underlying defect is **evidence admission**, not hygiene (hygiene framing invites drift into optional style vs governance constraint). Rigby also raised Fold B `future_trigger` for a pattern-matching helper to prevent burden creep.

T3 persisted both folds (rows 35 + 36; ledger 34 → 36 rows BEFORE D-verdict per PLAYBOOK-6.10.8). T4 revised rule text: hygiene→evidence-admission reframe throughout + "stable state pointer (commit SHA; PR/branch refs MUST include SHA under review)" + broadened examples beyond auth + explicit complementarity note with 6.10.6. Rigby T4 AGREE with two non-blocking micro-edits incorporated (SHA-under-review tightener + materially-change-classification scope predicate). Chris D-verdict single-yes.

Ratification envelope §8 records four forward-carry lessons; §7 lists PLACEHOLDER fields for post-merge bindings (workspace deliverable ID etc.).

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**First MINOR shipped from a ledger-enumerable two-trigger corpus.** The S2777 N22 substrate is now being used to justify amendments to its own governing discipline. Ratification envelope §3 enumerates the corpus by row number (row 31 + row 32) — future §6.10.x amendments should follow this shape when the empirical basis is ledger-recorded.

**Anti-rubber-stamp discipline is demonstrated to correlate with F-BLOCKING catches.** All three F-BLOCKING DISAGREEs of the S2771-rule streak (V1 slot at S2778 T1; V3 canonical home at S2780 T1; D4 "at HEAD" at S2786 T2) happened on tool-grounded SIGN turns; none happened on text-only turns. Explicit "use tool_runs" directive pays for itself.

**T4 revision cycle is now a demonstrated first-class shape.** v0.7.0 shipped a 3-turn shape (T1 tool-grounded → T2 zoom-out surfaced → T3 lock-in AGREE). v0.8.0 shipped a 4-turn shape (T1 → T2 F-BLOCKING + folds → T3 Claude-persist + rule-text revision → T4 Rigby verify). Two independent examples of substantive re-framing driven by SIGN pressure, both landing clean.

**Third consecutive same-session MINOR.** No cross-session drag on constitutional work when the corpus is prepared + Rigby SIGN is tool-grounded + Chris ratifies via single-yes on joint agreement.

---

## S2787 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired; freshness should be FRESH · SHA-match at S2786 close SHA `d6859acfa`.
**Ledger baseline:** 36 rows expected (15/14/7). Any drift = investigate.
**Regression 8-suite:** unchanged (155 tests OK at S2786 open).

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **CSRF exemption cross-file cleanup** — S2784+S2785 combined = 31 mutation endpoints with `@csrf_exempt` (12 platform + 15 human + 4 boardroom). Cross-file substrate PR. Frontend must start sending CSRF tokens; not just decorator swap. **Non-trivial (~1-3h)** — requires frontend fetch layer update + backend decorator removal + full E2E test that mutations still work from GovernanceTab.
- **Auth-gate consolidation** — 3 files each define their own `_*_staff_only = user_passes_test(...)` sentinel. Single shared `core/auth_gates.py` module candidate. Non-urgent (3 sentinels is not painful yet); watch for 4th before promoting.
- **AudioAgent completion-flip verification** — C1 linkage live; awaiting next timeout for one-query verification.
- **Model drift arc** — 38 unrelated auto-migrations queued.
- **First in-wild application of PLAYBOOK-6.10.9** — the next SIGN cycle that surfaces a code-state-asserting fold will exercise the new rule. Watch for the (i)/(ii)/(iii) outcome capture pattern being followed correctly.
- **Something entirely new** — new spider / UI page / agent capability / pipeline / dashboard. Fresh direction OK.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit.

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 36)
- **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — Rigby's dogfooding so far was under prompts, not autonomous
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **4th auth-gate sentinel** — trigger for consolidation into `core/auth_gates.py`
- **Fold-authoring evidence-admission helper (§6.12 note)** — 3+ SIGN cycles delayed >5min by manual verify OR one SIGN blocked
- **Second amendment with ledger-enumerable two-trigger corpus** — corroborate the amendment shape for codification

### Post-S2786 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.10 slot when opened (re-slotted forward again from 6.10.9 in v0.8.0 provenance)
- **CSRF exemption cleanup on 31 mutation endpoints** (see net-new)
- **AudioAgent completion-flip verification**
- **`test_session_freshness_2775` env drift**
- **Ledger split drift audit** — 12/8/2 → 12/8/3 shift at S2782 open (now 15/14/7)

---

## SESSION PIN — S2786 RETIRED (fresh mint required at S2787 open)

**Pin history (S2786):**

- `pa-d065f1dfadac4cd4` (label `s2786-fold-authoring-hygiene-v0-7-1`) minted S2786 open; **retired at S2786 close (`force=true`, seventeenth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-d065f1dfadac4cd4` (retired)** — intended failure mode forces S2787 first-action fresh mint.

**S2787 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2786 handoff §2 (three novel-precedent moments) + §3 (T1..T4 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2786 close SHA (d6859acfa) — TWENTY-THIRD close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2787 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Sign Ledger tab shows 36 rows
# http://localhost:8000/workspace?tab=system&sub=sign-ledger

# Ledger check: confirm 36-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==36, r
print('OK — 36 rows, counts:', r['counts_by_classification'])
"

# Regression 8-suite (unchanged from S2786)
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

# Playbook v0.8.0 verify — rules still present
grep -c 'PLAYBOOK-6\.10\.[7-9]' docs/ENGINEERING_PLAYBOOK.md  # expect >=6

# Mint fresh pin scoped to selected S2787 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2787 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; **NEW: folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist**.

---

## OPEN RUNTIME ITEMS (from S2786 close)

1. **First in-wild application of PLAYBOOK-6.10.9** — watch next code-state-asserting fold for (i)/(ii)/(iii) capture pattern
2. **Fold-authoring evidence-admission helper (§6.12 extension-point)** — 3+ SIGN cycles delayed OR one SIGN blocked
3. **CSRF exemption cross-file cleanup** — 31 mutation endpoints across 3 files
4. **Auth-gate consolidation** — 3 sentinel modules; wait for 4th
5. **AudioAgent completion-flip verification** (C1 linkage live, 0 rows populated)
6. **`test_session_freshness_2775` env drift**
7. **Model drift arc** (38 unrelated auto-migrations queued)
8. **Ledger split drift audit** (15/14/7 now)
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
19. **Memory rule promotion audit** — N24 anti-rubber-stamp SIGN at 3 triggers now (S2777 + S2780 + S2786 all F-BLOCKING catches on tool-grounded turns)
20. **First observed partial-recycle event** — N10/N11 trigger
21. **Rigby S2774 forward-carry: ops-surface PR pause** — held
22. **30+ other lambda-`__import__` sites**
23. **Rigby S2773 forward-carry #5 (health_summary overlap)**
24. **N15 v2 / N21 v2 candidates** — deferred
25. **`session_lifecycle` refactor trigger** — still armed
26. **`/api/pa/*` future-endpoint audit trigger** — sharp 5-point test
27. **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
28. **N22 v2 time-window filters** — deferred until ~50+ rows temporal spread
29. **N17 smart-command-box creep** — row 21 `future_trigger`
30. **Second non-Rigby consumer of `zoom_out_tool`** — abstraction quality test
31. **Autonomous Rigby consultation of `zoom_out_tool.list`** — truer substrate-payoff signal
32. **I-0302 three-PR pattern amendment → PLAYBOOK-6.10.10** (re-slotted forward again)
33. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
34. **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
35. **S2783 Fold 1 same-PR mitigation deferred** (GovernanceTab subtitle)
36. **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
37. **4th auth-gate sentinel trigger** — consolidation into `core/auth_gates.py`
38. **Postgres cleanup follow-ups (S2774 carryover)**
39. **Second amendment with ledger-enumerable two-trigger corpus** — codify the amendment shape
40. **N24 anti-rubber-stamp SIGN codification** — now 3 F-BLOCKING triggers observed (S2778/S2780/S2786); memory rule promotion window open

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2786 artifacts:**

- **Ship code:** `docs/ENGINEERING_PLAYBOOK.md` (v0.7.0 → v0.8.0: new rule 6.10.9 body + §6.10 commentary extension + new §6.12 helper extension-point note + Appendix D v0.8.0 row + frontmatter), `docs/research/implementation/RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0.md` (new 201-line envelope), `CLAUDE.md` (anchor bumped to v0.8.0), `tools/pa_local.sh` (+1/-1)
- **Handoff:** `docs/handoffs/SESSION_2786_PLAYBOOK_V0_8_0_RATIFIED.md`
- **Predecessors:** S2785 handoff (decision-approve authZ + 2nd fold-authoring trigger), S2784 handoff (platform mutations + 1st fold-authoring trigger), S2778 handoff (v0.7.0 zoom-out SIGN discipline)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — Rigby zoom-out ledger UI now shows 36 rows including the 2 new S2786 folds (Fold A `same_pr_mitigatable` row 35, Fold B `future_trigger` row 36)
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 36 rows at S2786 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2786 open
  - `logs/recycle_events.jsonl` — +1 new event from S2786 close (`sha=d6859acfab07`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `d6859acfa` (S2786 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (RATIFIED S2786) |
| Playbook rule count | 205 |
| RUR-C1 state | S2755→S2785 CLOSED · **S2786 v0.8.0 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-d065f1dfadac4cd4` (retired at S2786 close, force=true, seventeenth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-d065f1dfadac4cd4` (retired; forces fresh mint at S2787 open) |
| Live infra state | S2755→S2785 substrate + **PLAYBOOK-6.10.9 constitutional as of v0.8.0** |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2786 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3185) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **36 rows** (15 actionable / 14 mitigatable / 7 future_trigger) |
| Next move | Chris selects at S2787 open |

---

## Recommended session-open protocol (S2787)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2786 handoff §2 (three novel-precedent moments) + §3 (T1..T4 SIGN cycle) + §6 (open items)
4. **Freshness + regression 8-suite + ledger + eyeball verify + Playbook verify** — see S2787 open sequence above
5. **Watch for** ledger 36-row baseline surviving cascade merge; freshness FRESH · SHA-match; first in-wild PLAYBOOK-6.10.9 application on any code-state-asserting fold
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — no natural third-consecutive-constitutional-amendment candidate (unless a new two-trigger surfaces); recommend engineering candidates from §S2787 CANDIDATES
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2787 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **New at v0.8.0:** any zoom-out fold asserting a concrete code-state fact MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist per PLAYBOOK-6.10.9

---

## Reference documents

Ordered by frequency of use at S2787:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (latest ratified); 205 rules
3. [`docs/research/implementation/RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0.md`](docs/research/implementation/RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0.md) — **v0.8.0 ratification envelope (current)**
4. [`docs/handoffs/SESSION_2786_PLAYBOOK_V0_8_0_RATIFIED.md`](docs/handoffs/SESSION_2786_PLAYBOOK_V0_8_0_RATIFIED.md) — **S2786 handoff (current)**
5. [`docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md`](docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md) — S2785 handoff (2nd trigger record)
6. [`docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md`](docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md) — S2784 handoff (1st trigger record)
7. [`docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`](docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md) — v0.7.0 predecessor
8. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 36 rows at S2786 close (rows 31 + 32 are the two-trigger corpus; rows 35 + 36 are the S2786 dogfooded folds)
