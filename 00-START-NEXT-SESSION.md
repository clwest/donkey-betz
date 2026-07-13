# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2776 CLOSED — PA WRAPPER OWNERSHIP CHECK RATIFIED

**Refreshed 2026-07-13 (SESSION 2776 CLOSED — N21 shipped. `/api/pa/whoami/` bounded 3-field GET view + sharp 5-point test docstring. Dedicated `verify_pa_wrapper_ownership` management command (single-concern per Rigby Q1 DISAGREE fold). `tools/pa_local.sh` bash prelude with per-pin cache + `PA_LOCAL_ALLOW_MISMATCH=1` escape hatch. Exit codes 0/2/3/4. 9-test suite, 56/56 full 4-suite regression. Live E2E: cold cache → verify → cache · warm cache → silent skip. Rigby capstone 7/7 PASS on `/api/ops/*` + `/api/pa/whoami/`. Second consecutive non-ops-surface arc. **FIRST F-BLOCKING DISAGREE in the S2771-rule streak.** Chris explicit alignment with Rigby's substrate-simplicity concern. Eleventh close-cycle post-PLAYBOOK-7.4.4-codification (first double-cycle same calendar day). N15 shipped first natural payoff at S2776 mint.)**

**S2776 shipped as 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Code:** `core/views_pa_whoami.py` NEW (54 lines) · `core/urls.py` amended (import + path) · `core/management/commands/verify_pa_wrapper_ownership.py` NEW (190 lines) · `tools/pa_local.sh` bash prelude (~20 lines)
- **Tests:** `core/tests/test_pa_wrapper_ownership_2776.py` NEW (9 tests, 9/9 PASS in 0.38s)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md`
- **Handoff:** `docs/handoffs/SESSION_2776_PA_WRAPPER_OWNERSHIP_CHECK_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2776; L7 unchanged
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (eleventh cycle)

---

## SESSION-OPEN INFRA STORY (S2776)

S2776 opened in-session as a continuation of the S2775 close-ceremony flow (Chris's explicit directive: "ship s2775 then start n21"). Post-S2775-merge recycle produced first natural N15 hook fire at S2776 pin mint — verdict FRESH · SHA aa3dccc509b6 · 5/5 celery fresh. Trend surface at `logs/session_freshness.jsonl` now has 2 rows (1 shell-invoke test at S2775 + 1 natural at S2776).

Fresh pin `pa-bc40ba1f5dd343f4` minted for N21 arc. Rigby joint SIGN produced the FIRST F-BLOCKING DISAGREE of the S2771-rule streak — Rigby pushed back on Claude's Q1 lean (extend `session_lifecycle status`) with substrate-simplicity argument. Chris explicit alignment: "agree with Rigby on trying to prevent swiss army knife effects." Validates the rule genuinely surfaces substantive folds vs devolving into all-PASS.

Local recycle required mid-session to load N21 URL for live E2E verify. Post-recycle E2E confirmed both cold-cache and warm-cache paths work.

**Lesson for S2777 open:** the N21 wrapper prelude fires automatically before Rigby dispatch. If the freshness verdict or capstone comes back with unexpected state, first-check `~/.claude-pa-verified/<pin>.json` presence + contents — a missing or stale cache means the prelude either just fired (should have printed a `[pa_local]` line) or errored (check stderr).

---

## THE PIVOT — WHY THIS SHIP MATTERS

Two novel-precedent moments this session:

1. **First F-BLOCKING DISAGREE from Rigby in the S2771-rule streak** (six consecutive applications). Chris aligned with the disagreement, folding dedicated command over session_lifecycle extension. This IS the pressure-test for whether the S2771 rule produces substantive folds or drifts into ritual — and it just proved productive. Six sessions in, four with same-PR-mitigatable/actionable material changes, one with a live disagreement Chris ratified. No sign of drift.

2. **First natural N15 payoff.** S2775's mechanism-now/value-later class of substrate delivered its first real data point at S2776 pin mint automatically. `logs/session_freshness.jsonl` now has row #2 — natural, not shell-invoke test. Trend surface working as designed.

Meta-discipline observation: **N21 ships a well-tested, single-concern piece of substrate that was named as a target in a memory rule (`feedback_post_travel_port_collision_triage`) two sessions ago.** Memory-rule-to-code-ship latency: 1 calendar day, 2 sessions. This is a healthy sign of feedback-loop tightness.

Also: **zoom-out classification pattern now has three triggers of `same-PR-actionable` + three of `same-PR-mitigatable` + two of `future-trigger`.** Two-triggers threshold satisfied for two classes independently per PLAYBOOK-6.10. Codification candidate for Playbook v0.7.0 MINOR (new rule) OR v0.6.1 PATCH (informative-only classification note).

---

## S2777 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

**Note discipline:** ops-surface PRs paused per S2774 forward-carry. Unblock triggers: real incident on any `/api/ops/*` endpoint; new user-visible feature request touching ops; substrate concern from Rigby SIGN on a non-ops-adjacent arc.

- **N17** — `session_number` pill in the search chip when text is set — small UX polish. **Non-ops-surface — not gated.**
- **N22** — Persist zoom-out concern classification (`same-PR-actionable` / `same-PR-mitigatable` / `future-trigger`) as a small helper that catalogs the three known cases and computes streak length per category. Accelerates two-triggers threshold detection per PLAYBOOK-6.10. Preferable substrate for future zoom-out rule codification.
- **N23 (new candidate)** — Codify zoom-out classification pattern as Playbook v0.6.1 PATCH (informative-only note in §11.3 or §6.10) OR v0.7.0 MINOR (new [GR] rule). Would move the emerging pattern from "informal streak observation" into constitutional substrate. Ratification cycle required (Playbook amendment).
- **N15 v2 candidates** — close-time freshness capture (`context='session_close'`); PA-tool read action for Rigby SIGN queries; UI tile after ~30-50 natural rows accumulate. Trigger for the first: any evidence that close-time is a load-bearing observability moment. Trigger for the tile: sustained accumulation with a Chris "let me eyeball this" ask.
- **N21 v2 candidates** — wrapper-side user_id cache compare (0-API-cost invalidation on token swap); TTL on cache; sibling `logs/wrapper_ownership.jsonl` trend log. All gated on trigger.

**Gated by ops-surface pause** (need incident / user-visible feature / non-ops SIGN concern to unblock): N9, N20, Candidate 1 (S2761 smoke), 30+ lambda-`__import__` sites in `core/urls.py`

**Housekeeping (non-net-new):** S2758 D2 canonical decision (needs joint SIGN), S2758 D4 REPORT-ONLY, N13 handoff-date-format normalizer

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, PA celery bounce (#3119), memory rule promotion audit

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge on Recent Recycles rows (gated on observing at least one real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching — clean N7 entries streak continues through S2776)
- **Q3 #5 (health_summary/ops_tool.overview overlap)** — trigger unchanged
- **30+ other lambda-`__import__` sites in `core/urls.py`** — no trigger yet
- **First `same-PR-mitigatable` case validation** — reached three-triggers this session (S2775 all-4 + S2776 c + S2776 d)

### Post-S2766 owed

- **Memory rule promotion audit** — sweep MEMORY.md for two-trigger candidates for future MINOR amendments. **N23 (zoom-out classification codification) is a natural addition to this audit's output.**

---

## SESSION PIN — S2776 RETIRED (fresh mint required at S2777 open)

**Pin history (S2776):**

- `pa-bc40ba1f5dd343f4` (label `s2776-n21-pa-local-user-check`) minted S2776 open via same-session flow from S2775 close; **retired at S2776 close (force=true, SEVENTH consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-bc40ba1f5dd343f4` (retired)** — intended failure mode forces S2777 first-action fresh mint. N21 cache file `~/.claude-pa-verified/pa-bc40ba1f5dd343f4.json` will be orphaned (harmless — new pin creates new cache entry on first invocation).

**S2777 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2776 envelope §4 (Rigby SIGN summary with FIRST F-BLOCKING DISAGREE + Chris explicit alignment)
# Read S2776 envelope §8 (Meta-observation — zoom-out classification pattern now at three-triggers threshold)

# Freshness check. Should be FRESH · SHA-match at S2776 close SHA — ELEVENTH close-cycle after PLAYBOOK-7.4.4 codification.
# N15 hook fires automatically at open — inspect the row landing in logs/session_freshness.jsonl.
bash tools/pa_local.sh "S2777 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2776 close at top; all N7-enriched)"

# N21 prelude fires on first bash invocation of S2777 pin (cold cache after pin rotation)
# Expected: [pa_local] ✓ token=chris · pin=pa-<new> · pin_owner=chris

# Regression check: run 4-suite ops+substrate stack
python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773 core.tests.test_session_freshness_2775 core.tests.test_pa_wrapper_ownership_2776 --noinput

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - Everything renders normally for you (staff)
#   - All 6 ops endpoints still return same shapes
#   - /api/pa/whoami/ returns {username, user_id, is_staff} when authenticated

# Mint fresh pin scoped to selected S2777 candidate. Second natural N15 row lands here.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed. N21 prelude will fire on first invocation of the new pin.

---

## OPEN RUNTIME ITEMS (from S2776 close)

1. **N17 / N22 / N23 net-new engineering** — see Candidates above
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
13. **Memory rule promotion audit** — includes N23 zoom-out classification codification candidate
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby S2774 forward-carry: pause ops-surface PRs** — still held; unblock triggers unchanged
16. **30+ other lambda-`__import__` sites** — refactor when future arc naturally touches
17. **Rigby S2773 forward-carry #5 (health_summary overlap)** — trigger unchanged
18. **N15 v2 candidates** (close-time freshness capture / PA-tool read / UI tile) — deferred pending trigger
19. **N21 v2 candidates** (wrapper-side user_id compare / TTL / sibling log) — deferred pending trigger
20. **`session_lifecycle` refactor trigger** — codified in `verify_pa_wrapper_ownership` docstring; if third flag hits API or wrapper cache, split into `session_lifecycle` + `toolchain_doctor`
21. **`/api/pa/*` future-endpoint audit trigger** — every proposal must satisfy the sharp 5-point test in `views_pa_whoami.py` docstring
22. **Zoom-out classification codification** — three triggers now for two classes; Playbook v0.7.0 MINOR or v0.6.1 PATCH candidate
23. **Postgres cleanup follow-ups (S2774 carryover):**
    - Decide whether to `brew uninstall postgresql@16` (data preserved as archive)
    - Decide whether to drop pg15's `test_unified_donkey_betz` DB or leave for future test runs

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2776 artifacts:**

- **New backend view:** `core/views_pa_whoami.py` (54 lines, `pa_whoami` + sharp 5-point test docstring)
- **New management command:** `core/management/commands/verify_pa_wrapper_ownership.py` (190 lines)
- **New test file:** `core/tests/test_pa_wrapper_ownership_2776.py` (9 tests)
- **Amended:** `core/urls.py` (grouped import + path entry with 5-point test comment); `tools/pa_local.sh` (bash prelude + escape hatch)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md`
- **Handoff:** `docs/handoffs/SESSION_2776_PA_WRAPPER_OWNERSHIP_CHECK_RATIFIED.md`
- **Predecessor envelopes:** S2775 (freshness verdicts JSONL), S2774 (URLConf lambda cleanup + same-PR capstone), S2773 (query-param allowlist), S2772 (auth-regression + staff gate)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2776
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surfaces:**
  - `/api/pa/whoami/` returns `{username, user_id, is_staff}` when authenticated (403/redirect otherwise)
  - `/api/ops/*` endpoints unchanged
  - `logs/session_freshness.jsonl` has 2 rows (1 shell test + 1 natural at S2776); grows one per session_lifecycle open going forward
  - `~/.claude-pa-verified/<pin>.json` cache dir populates on first bash wrapper invocation per pin

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2776 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | S2755→S2775 CLOSED · **S2776 N21 wrapper ownership check CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-bc40ba1f5dd343f4` (retired at S2776 close, force=true, seventh consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-bc40ba1f5dd343f4` (retired; forces fresh mint at S2777 open) |
| Live infra state | S2755→S2775 diagnostic infra + Playbook v0.6.0 + N19 URLConf cleanup + N15 freshness telemetry + **N21 wrapper ownership check** operational |
| Postgres :5432 | pg15 (July DB, 382 migrations, S2776 state) — brew launchd `started`, survives reboot |
| Postgres pg16 | Parked (April fossil, data preserved on disk, plist unloaded) |
| Freshness log | `logs/session_freshness.jsonl` — 2 rows (streak begins here). Grows +1 per `session_lifecycle open` |
| Wrapper ownership cache | `~/.claude-pa-verified/<pin>.json` — populates on first bash invocation per pin |
| Next move | Chris selects at S2777 open |

---

## Recommended session-open protocol (S2777)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2776 envelope §4 (Rigby SIGN summary with FIRST F-BLOCKING DISAGREE) + §8 (Meta-observation — three-triggers threshold on zoom-out classification)
4. Skim the S2776 close-ceremony bundle — second consecutive non-ops-surface arc; substrate maturity compounding
5. **Freshness + regression + browser eyeball** — see S2777 open sequence in §SESSION PIN above
6. **Watch for** the N15 second natural row landing at S2777 pin mint + N21 prelude firing at first bash invocation of the new pin
7. If `staleness_verdict != FRESH` → escalate to Chris (eleventh-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
8. **Check `brew services list | grep postgres` FIRST** if freshness fails in unusual pattern (missing roles / stale conversations) — port-collision root cause is the fast path
9. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
10. Present candidate menu with **at least one open-ended zoom-out ask in the Rigby SIGN** (per S2771 rule, validated 6 sessions in a row with first F-BLOCKING DISAGREE at S2776)
11. Chris directs S2777 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2777:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2776; L7 unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md`](docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md) — S2776 envelope
4. [`docs/handoffs/SESSION_2776_PA_WRAPPER_OWNERSHIP_CHECK_RATIFIED.md`](docs/handoffs/SESSION_2776_PA_WRAPPER_OWNERSHIP_CHECK_RATIFIED.md) — S2776 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md`](docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md) — S2775 predecessor
6. `core/views_pa_whoami.py` — new this session (sharp 5-point test in docstring)
7. `core/management/commands/verify_pa_wrapper_ownership.py` — new this session (single-concern command; refactor trigger codified)
