# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2777 CLOSED — ZOOM-OUT CLASSIFICATION LEDGER RATIFIED

**Refreshed 2026-07-13 (SESSION 2777 CLOSED — N22 shipped. `logs/zoom_out_classifications.jsonl` seeded to 13 rows (12 backfilled from S2774+S2775+S2776 envelope §4 SIGN Summary + envelope frontmatter + 1 live S2777). NEW `core/management/commands/record_zoom_out_concern.py` (147-line JSONL writer, 7-field schema, enum-validated classification). NEW `core/management/commands/zoom_out_streak_report.py` (128-line CLI reader with advisory-only report language, `--as-json` for downstream consumption). 10-test suite covering both commands; 10/10 PASS in 0.008s. Full 5-suite regression 66/66 PASS in 0.916s. Third consecutive non-ops-surface arc. Ledger state at close: 5 same_pr_actionable · 7 same_pr_mitigatable · 1 future_trigger. **SECOND F-BLOCKING DISAGREE of the S2771-rule streak** — this one on Claude's *claim* rather than design lean: original N22 rationale referenced "PLAYBOOK-6.10 two-triggers threshold" as if it were a codified rule; Rigby's turn-2 tool-grounded verification refuted with citations; framing corrected before ship. **First mid-arc rubber-stamp catch:** Rigby's turn-1 SIGN was AGREE x4 with 0 tool_runs; Chris pressure-tested at decision time; tool-grounded re-route recovered in one turn. Twelfth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2777 shipped as 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Code:** `core/management/commands/record_zoom_out_concern.py` NEW (147 lines) · `core/management/commands/zoom_out_streak_report.py` NEW (128 lines) · `logs/zoom_out_classifications.jsonl` NEW (13 seed rows)
- **Tests:** `core/tests/test_zoom_out_classifications_2777.py` NEW (10 tests, 10/10 PASS in 0.008s)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_zoom_out_classifications_helper.md`
- **Handoff:** `docs/handoffs/SESSION_2777_ZOOM_OUT_CLASSIFICATIONS_HELPER_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2777; L7 unchanged
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (twelfth cycle)

---

## SESSION-OPEN INFRA STORY (S2777)

S2777 opened in-session as a continuation of the S2776 close-ceremony flow. Post-S2776-merge recycle produced second natural N15 hook fire at S2777 pin mint — verdict FRESH · SHA `eaccf3acfb02` · 5/5 celery fresh. Trend surface at `logs/session_freshness.jsonl` now has 3 rows (1 shell-invoke test at S2775 + 2 natural at S2776 and S2777).

Fresh pin `pa-f19df7828f2843e5` minted for N22 arc.

**Turn 1 rubber-stamp catch.** Rigby's initial joint SIGN was AGREE x4 with pushback text but ZERO `tool_runs` and `intent: general`. No `search_docs` invocations. No citations to prior envelopes or Playbook §s. Chris flagged at decision time before proceeding: "make sure Rigby is not just rubber stamping what you suggest, and that she's using tools when needed and not just guess."

**Turn 2 substantive DISAGREE.** Re-routed with 5 explicit tool-use directives (targeted `search_docs` queries against S2774/S2775/S2776 envelopes + Playbook §6.10 + `session_lifecycle` source). Rigby executed 6+ `search_docs` calls with narrowing queries. Produced substantive DISAGREE on Claude's "PLAYBOOK-6.10 two-triggers threshold" rationale (surfaced §6.10 has rules 6.10.1–6.10.6 for provenance verification; two-triggers convention appears as informative note language + methodology record, NOT as a codified normative rule). Claude verified independently via direct file read — DISAGREE correct. Two clean FOLDs (S2776 a/b/c/d mapping missed by RAG chunking; `session_lifecycle --help` output not in corpus).

**Turn 3 folds closed.** Claude fed verbatim ground-truth (envelope frontmatter §sign_sessions for a/b/c/d + `python manage.py session_lifecycle --help` for the 4 subcommands: status/open/history/close). Framing corrected: N22 rationale rewritten to "evidence substrate for a future rule that does not exist yet." Rigby re-rendered clean AGREE Q1-Q4 with citations + reiterated §6.10 DISAGREE + direct zoom-out answer + 1 new same-PR-mitigatable concern (schema ossification) folded in.

**Chris D-verdict yes** at turn 3 synthesis: "yes ship it."

**Lesson for S2778 open:** the anti-rubber-stamp discipline paid off — one prior claim would have shipped wrong without Chris's pressure test. Consider always checking `tool_runs` non-empty when a SIGN routing expected substantive verification of prior claims. Codification candidate (memory rule / Playbook amendment) once second trigger surfaces.

---

## THE PIVOT — WHY THIS SHIP MATTERS

Three novel-precedent moments this session:

1. **First mid-arc rubber-stamp SIGN detection.** Chris's pressure test at decision time ("make sure Rigby is not just rubber stamping") caught a text-only SIGN with 0 tool_runs before it shipped. Recovery: 1 additional turn with explicit tool-grounded verification directives. Prior sessions relied on retrospective observation that outputs *looked* substantive; S2777 established a decision-time check pattern.

2. **Second F-BLOCKING DISAGREE of the S2771-rule streak.** First (S2776 Q1) was on Claude's design *lean*. This one (S2777 §6.10) was on Claude's *claim*. Both would have shipped wrong artifacts. Different axes of failure, same defense: tool-grounded verification.

3. **Substrate is self-hosting.** N22's own S2777 turn-3 zoom-out concern (schema ossification) is row 13 of the seed ledger. The classification pattern documents itself from ship-day.

Meta-discipline observation: **the S2771 rule keeps producing substantive folds SEVEN sessions in.** Streak table now covers S2771-S2777. Two independent F-BLOCKING DISAGREEs. Three independent classification categories. No drift into ritual. If a session ever produces AGREE x4 + generic zoom-out with 0 tool_runs, the next session should treat it as a rubber-stamp signal and re-route.

---

## S2778 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

**Note discipline:** ops-surface PRs paused per S2774 forward-carry. Unblock triggers: real incident on any `/api/ops/*` endpoint; new user-visible feature request touching ops; substrate concern from Rigby SIGN on a non-ops-adjacent arc.

- **N17** — `session_number` pill in the search chip when text is set — small UX polish. **Non-ops-surface — not gated.**
- **N23** — Codify zoom-out classification pattern as Playbook v0.6.1 PATCH (informative note in §11.3 template or §6.10 extension-point) OR v0.7.0 MINOR (new [GR] rule). N22 ledger provides evidence substrate (13 rows: 5+7+1). Amendment cycle required (own SIGN + D-verdict).
- **N24 (new candidate)** — Anti-rubber-stamp SIGN workflow codification. One trigger observed at S2777 turn 1. Two-trigger threshold not yet met — first candidate for memory rule ("check tool_runs before proceeding when SIGN expected substantive verification of prior claims"). If second trigger surfaces, promote to Playbook amendment (STUB-appropriate for Ch 7 SIGN methodology). Not proposed as immediate action; watch-and-wait.
- **N22 v2 candidates** — Django model migration; PA-tool read surface for live SIGN queries; JSONL rotation/archival (~500 rows). All gated on trigger.
- **N15 v2 candidates** — close-time freshness capture (`context='session_close'`); PA-tool read; UI tile after ~30-50 natural rows. Freshness log at 3 rows now — trigger for tile still far off.
- **N21 v2 candidates** — wrapper-side user_id cache compare; TTL; sibling `logs/wrapper_ownership.jsonl`.

**Gated by ops-surface pause** (need incident / user-visible feature / non-ops SIGN concern to unblock): N9, N20, Candidate 1 (S2761 smoke), 30+ lambda-`__import__` sites in `core/urls.py`

**Housekeeping (non-net-new):** S2758 D2 canonical decision (needs joint SIGN), S2758 D4 REPORT-ONLY, N13 handoff-date-format normalizer

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, PA celery bounce (#3119), memory rule promotion audit

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge on Recent Recycles rows (gated on observing at least one real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching — clean N7 entries streak continues through S2777)
- **Q3 #5 (health_summary/ops_tool.overview overlap)** — trigger unchanged
- **30+ other lambda-`__import__` sites in `core/urls.py`** — no trigger yet

### Post-S2766 owed

- **Memory rule promotion audit** — sweep MEMORY.md for two-trigger candidates for future MINOR amendments. **N23 (zoom-out classification codification)** now has strongest evidence substrate (13 rows). **N24 (anti-rubber-stamp)** waiting on second trigger.

---

## SESSION PIN — S2777 RETIRED (fresh mint required at S2778 open)

**Pin history (S2777):**

- `pa-f19df7828f2843e5` (label `s2777-n22-zoom-out-classification-persist`) minted S2777 open via same-session flow from S2776 close; **retired at S2777 close (force=true, EIGHTH consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-f19df7828f2843e5` (retired)** — intended failure mode forces S2778 first-action fresh mint. N21 cache file `~/.claude-pa-verified/pa-f19df7828f2843e5.json` will be orphaned (harmless).

**S2778 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2777 envelope §4 (Rigby SIGN 3-turn loop with rubber-stamp catch + §6.10 DISAGREE)
# Read S2777 envelope §8 (Meta-observation — streak table update with SECOND F-BLOCKING DISAGREE)

# Freshness check. Should be FRESH · SHA-match at S2777 close SHA — TWELFTH close-cycle after PLAYBOOK-7.4.4.
# N15 hook fires automatically at open — inspect the row landing in logs/session_freshness.jsonl.
bash tools/pa_local.sh "S2778 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2777 close at top; all N7-enriched)"

# N21 prelude fires on first bash invocation of S2778 pin (cold cache after pin rotation)
# Expected: [pa_local] ✓ token=chris · pin=pa-<new> · pin_owner=chris

# Regression check: run 5-suite ops+substrate stack
python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773 core.tests.test_session_freshness_2775 core.tests.test_pa_wrapper_ownership_2776 core.tests.test_zoom_out_classifications_2777 --noinput

# Ledger check: confirm 13-row baseline survived merge
python manage.py zoom_out_streak_report --as-json | python -c "import json, sys; d=json.load(sys.stdin); assert d['total_rows']==13, d; print('OK — 13 rows, counts:', d['counts_by_classification'])"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - All 6 ops endpoints still return same shapes
#   - /api/pa/whoami/ still returns {username, user_id, is_staff} when authenticated

# Mint fresh pin scoped to selected S2778 candidate. Third natural N15 row lands here.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed. N21 prelude will fire on first invocation of the new pin.

**Anti-rubber-stamp check (S2778 first Rigby SIGN):** verify `tool_runs` non-empty in the task result before treating any SIGN verdict as substantive. If the first SIGN comes back with `intent: general` + `tool_runs: []` when substrate claims were being verified, re-route with explicit tool-grounded directives before proceeding.

---

## OPEN RUNTIME ITEMS (from S2777 close)

1. **N17 / N23 / N24 net-new engineering** — see Candidates above
2. **S2761 smoke test** — ops-surface (gated)
3. **S2758 D2 canonical decision** — needs Rigby joint SIGN
4. **S2758 D4 HIGH-RISK wiring extension** — REPORT-ONLY
5. **N13 handoff-date-format normalizer** — hygiene one-shot
6. **P0.5 cost-threshold advance-to-freeze**
7. **P0.75 CI billing**
8. **PA celery worker bounce**
9. **RUR-C2 open eligible**
10. **S2758 D1 process_pa_chat_task payload strip**
11. **S2758 D5 local shim retirement**
12. **HMAC signing of `x-acting-user-id`**
13. **Memory rule promotion audit** — includes N23 zoom-out classification codification + N24 anti-rubber-stamp candidates
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby S2774 forward-carry: pause ops-surface PRs** — still held; unblock triggers unchanged
16. **30+ other lambda-`__import__` sites** — refactor when future arc naturally touches
17. **Rigby S2773 forward-carry #5 (health_summary overlap)** — trigger unchanged
18. **N15 v2 candidates** — deferred pending row accumulation + user-visible ask
19. **N21 v2 candidates** — deferred pending trigger
20. **`session_lifecycle` refactor trigger** — still armed (4 subcommands; trigger at 3rd API/cache flag)
21. **`/api/pa/*` future-endpoint audit trigger** — every proposal must satisfy the sharp 5-point test
22. **N22 v2 candidates** — Django model, PA-tool read, JSONL rotation
23. **Anti-rubber-stamp SIGN workflow** — one trigger observed; wait for second trigger before codifying
24. **Postgres cleanup follow-ups (S2774 carryover):**
    - Decide whether to `brew uninstall postgresql@16` (data preserved as archive)
    - Decide whether to drop pg15's `test_unified_donkey_betz` DB or leave for future test runs

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2777 artifacts:**

- **New backend commands:**
  - `core/management/commands/record_zoom_out_concern.py` (147 lines, JSONL writer)
  - `core/management/commands/zoom_out_streak_report.py` (128 lines, CLI reader)
- **New seed data:** `logs/zoom_out_classifications.jsonl` (13 rows)
- **New test file:** `core/tests/test_zoom_out_classifications_2777.py` (10 tests)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_zoom_out_classifications_helper.md`
- **Handoff:** `docs/handoffs/SESSION_2777_ZOOM_OUT_CLASSIFICATIONS_HELPER_RATIFIED.md`
- **Predecessor envelopes:** S2776 (PA wrapper ownership), S2775 (freshness verdicts JSONL), S2774 (URLConf lambda cleanup), S2773 (query-param allowlist), S2772 (auth-regression + staff gate)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2777
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` grows +N per session on Rigby SIGN zoom-out concerns (manual capture via `record_zoom_out_concern`)
  - `logs/session_freshness.jsonl` has 3 rows (1 shell + 2 natural); grows +1 per session_lifecycle open
  - `~/.claude-pa-verified/<pin>.json` cache dir populates on first bash wrapper invocation per pin
  - `/api/pa/whoami/` returns `{username, user_id, is_staff}` when authenticated
  - `/api/ops/*` endpoints unchanged

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2777 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | S2755→S2776 CLOSED · **S2777 N22 zoom-out ledger CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-f19df7828f2843e5` (retired at S2777 close, force=true, eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-f19df7828f2843e5` (retired; forces fresh mint at S2778 open) |
| Live infra state | S2755→S2776 diagnostic infra + Playbook v0.6.0 + N15 freshness + N19 URLConf cleanup + N21 wrapper ownership + **N22 zoom-out ledger** operational |
| Postgres :5432 | pg15 (July DB, S2777 state) — brew launchd `started`, survives reboot |
| Postgres pg16 | Parked (April fossil, data preserved on disk, plist unloaded) |
| Freshness log | `logs/session_freshness.jsonl` — 3 rows |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 13 rows (5 actionable / 7 mitigatable / 1 future-trigger) |
| Wrapper ownership cache | `~/.claude-pa-verified/<pin>.json` — populates on first bash invocation per pin |
| Next move | Chris selects at S2778 open |

---

## Recommended session-open protocol (S2778)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2777 envelope §4 (3-turn Rigby SIGN loop with rubber-stamp catch + §6.10 DISAGREE) + §8 (updated streak table with SECOND F-BLOCKING DISAGREE + novel signals)
4. Skim the S2777 close-ceremony bundle — third consecutive non-ops-surface arc; substrate maturity compounding
5. **Freshness + regression + ledger + browser eyeball** — see S2778 open sequence in §SESSION PIN above
6. **Watch for** the N15 third natural row landing at S2778 pin mint + N21 prelude firing at first bash invocation of the new pin + ledger 13-row baseline surviving merge
7. If `staleness_verdict != FRESH` → escalate to Chris (twelfth-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
8. **Check `brew services list | grep postgres` FIRST** if freshness fails in unusual pattern (missing roles / stale conversations) — port-collision root cause is the fast path
9. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
10. Present candidate menu with **at least one open-ended zoom-out ask in the Rigby SIGN** (per S2771 rule, validated 7 sessions with 2 F-BLOCKING DISAGREEs)
11. **Anti-rubber-stamp check on first SIGN**: verify `tool_runs` non-empty before treating verdicts as substantive when substrate claims were expected to be verified
12. Chris directs S2778 P0 selection
13. Mint fresh pin with candidate-scoped label
14. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2778:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2777; L7 unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-13_zoom_out_classifications_helper.md`](docs/research/implementation/RATIFICATION_2026-07-13_zoom_out_classifications_helper.md) — S2777 envelope
4. [`docs/handoffs/SESSION_2777_ZOOM_OUT_CLASSIFICATIONS_HELPER_RATIFIED.md`](docs/handoffs/SESSION_2777_ZOOM_OUT_CLASSIFICATIONS_HELPER_RATIFIED.md) — S2777 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md`](docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md) — S2776 predecessor
6. `core/management/commands/record_zoom_out_concern.py` — new this session (JSONL writer)
7. `core/management/commands/zoom_out_streak_report.py` — new this session (CLI reader)
8. `logs/zoom_out_classifications.jsonl` — new this session (13 seed rows)
