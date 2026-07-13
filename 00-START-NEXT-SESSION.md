# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2775 CLOSED — SESSION-OPEN FRESHNESS VERDICTS JSONL RATIFIED

**Refreshed 2026-07-13 (SESSION 2775 CLOSED — N15 shipped. `_compute_process_staleness` extracted from `OpsHandler` to module-level `core.services.process_freshness.compute_process_staleness` with byte-identical return shape; `session_lifecycle open` post-success hook writes one lean row per mint to `logs/session_freshness.jsonl` (gitignored); `session_lifecycle history --limit N` reads back. 10 new tests + 47/47 ops-stack PASS in 0.829s. Rigby capstone 6/6 PASS on `/api/ops/*`. First non-ops-surface arc since S2770. S2771 rule fifth consecutive application, 4 concerns all folded as design-time mitigations — first `same-PR-mitigatable` exemplar. Tenth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2775 shipped as 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Code:** `core/services/process_freshness.py` NEW (176 lines) · `core/services/td_handlers_ops.py` amended (148-line method body → 8-line wrapper) · `core/management/commands/session_lifecycle.py` amended (+ `history` subcommand + freshness helper + hook)
- **Tests:** `core/tests/test_session_freshness_2775.py` NEW (10 tests, 10/10 PASS in 0.157s)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md`
- **Handoff:** `docs/handoffs/SESSION_2775_SESSION_FRESHNESS_VERDICTS_JSONL_RATIFIED.md`
- **CLAUDE.md L3 anchor:** refreshed to S2775; L7 unchanged
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (tenth cycle)

---

## SESSION-OPEN INFRA STORY (S2775)

Clean session-open — no travel-recovery drama. `context-kit orient` fired at first tool call. HEAD `b31393258` (S2774 close) verified. pg15 owns port 5432 under brew launchd, survives reboot per S2774 recovery. Wrapper still pointed at retired S2774 pin `pa-206d3fa2f64d440b` — intentional fresh-mint gate. Minted `pa-77bdf04032204741` at open with label `s2775-n15-freshness-verdicts-jsonl`. Rigby freshness dispatch confirmed FRESH · SHA `b3139325831a`. Regression 37/37 in 0.657s.

Non-ops-surface arc chosen from candidate menu — first since the S2770→S2774 ops-console streak. Rigby joint SIGN loop validated the pattern (Claude drafts, routes 3 F-BLOCKING + open zoom-out, Rigby folds one row-shape refinement + 4 zoom-out mitigations, Chris D-verdicts yes). E2E via management shell before landing the PR: real compute against real process table produced FRESH · head `b3139325831a` · 5/5 celery fresh, written to `logs/session_freshness.jsonl` and read back via `session_lifecycle history`.

**Lesson for S2776 open:** the first natural `_record_session_freshness` fire will happen when Chris runs `session_lifecycle open --label s2776-<slot>` — that's the first row that will land through the automated hook rather than manual shell. Read it back via `python manage.py session_lifecycle history --limit 5`.

---

## THE PIVOT — WHY THIS SHIP MATTERS

Substrate hardening arc continues but breaks a "type of surface" streak. S2770→S2774 were all `/api/ops/*` iterations. S2775 turned the freshness verdict — which every S2755+ session has read but only eyeballed — into a persisted trend surface. Every future PLAYBOOK-7.4.x amendment now gets its corroboration ladder assembled automatically from `logs/session_freshness.jsonl` rather than reconstructed from handoffs.

Meta-important novel precedent: **first `same-PR-mitigatable` zoom-out response.** S2774 established `same-PR-actionable` (capstone verification action). S2775 established `same-PR-mitigatable` (design-time changes fold in). Together with the traditional `future-trigger` (S2772/S2773 precedent), zoom-out response now has three named response categories. Watch for third case of any classification before proposing codification per PLAYBOOK-6.10.

**Meta discipline:** N15 is the first substrate ship where value depends on OTHER sessions accumulating data. All prior close-cycle ships delivered immediate observable value same-session. N15 lands the mechanism; the value lands over N future sessions. This is a distinct class of substrate work — mechanism-now, value-later — worth naming for future arc planning.

---

## S2776 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

**Note discipline:** ops-surface PRs paused per S2774 forward-carry. Unblock triggers: real incident on any `/api/ops/*` endpoint; new user-visible feature request touching ops; substrate concern from Rigby SIGN on a non-ops-adjacent arc.

- **N21** — `pa_local.sh` runtime user-check: verify token maps to a live user + surface username at first invocation of each session. Would have caught the S2774 chris/donkeyking wrapper drift in seconds. **Non-ops-surface — not gated.** ⭐ (Chris held over from S2775 menu to "check in on context before moving on to N21")
- **N17** — `session_number` pill in the search chip when text is set — small UX polish. **Non-ops-surface — not gated.**
- **N22 (new candidate)** — Persist Rigby zoom-out concern classification (`same-PR-actionable` / `same-PR-mitigatable` / `future-trigger`) as an emerging pattern. First substrate would be a small helper that catalogs the 3 known cases and computes streak length per category, to accelerate two-triggers threshold detection per PLAYBOOK-6.10.

**Gated by ops-surface pause** (need incident / user-visible feature / non-ops SIGN concern to unblock): N9, N20, Candidate 1 (S2761 smoke), 30+ lambda-`__import__` sites

**Housekeeping (non-net-new):** S2758 D2 canonical decision (needs joint SIGN), S2758 D4 REPORT-ONLY, N13 handoff-date-format normalizer

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, PA celery bounce (#3119), memory rule promotion audit

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge on Recent Recycles rows (gated on observing at least one real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching — clean N7 entries streak continues through S2775)
- **Q3 #5 (health_summary/ops_tool.overview overlap)** — trigger unchanged: first bug where UI tile and `ops_tool.overview` diverge on a factual claim
- **30+ other lambda-`__import__` sites in `core/urls.py`** — no trigger yet
- **N15 v2 candidates** — close-time freshness capture; PA-tool read action; UI tile after ~30-50 rows accumulate

### Post-S2766 owed

- **Memory rule promotion audit** — sweep MEMORY.md for two-trigger candidates for future MINOR amendments

---

## SESSION PIN — S2775 RETIRED (fresh mint required at S2776 open)

**Pin history (S2775):**

- `pa-77bdf04032204741` (label `s2775-n15-freshness-verdicts-jsonl`) minted S2775 open; **retired at S2775 close (force=true, SIXTH consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-77bdf04032204741` (retired)** — intended failure mode forces S2776 first-action fresh mint.

**S2776 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2775 envelope §4 (Rigby SIGN summary with fifth consecutive S2771 rule application)
# Read S2775 envelope §8 (Meta-observation — mechanism-now/value-later class + emerging zoom-out classification)

# Freshness check. Should be FRESH · SHA-match at S2775 close SHA — TENTH close-cycle after PLAYBOOK-7.4.4 codification.
# NEW at S2776: read the FIRST natural freshness row from logs/session_freshness.jsonl (dropped by session_lifecycle open at S2776 open)
bash tools/pa_local.sh "S2776 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2775 close at top; all N7-enriched)"

# Regression check: run 3-suite ops stack (S2772 auth-regression + S2773 param-allowlist + S2775 N15)
python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773 core.tests.test_session_freshness_2775 --noinput

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - Everything renders normally for you (staff)
#   - All 6 ops endpoints still return same shapes

# Mint fresh pin scoped to selected S2776 candidate. This is now the FIRST natural N15 fire — check the row it lands.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 3

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2775 close)

1. **N21 / N17 / N22 net-new engineering** — see Candidates above
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
13. **Memory rule promotion audit**
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby S2774 forward-carry: pause ops-surface PRs** — still held; unblock triggers unchanged
16. **30+ other lambda-`__import__` sites** — refactor when future arc naturally touches
17. **Rigby S2773 forward-carry #5 (health_summary overlap)** — trigger unchanged
18. **N15 v2 (close-time freshness / PA-tool read / UI tile)** — deferred pending accumulation + user-visible ask
19. **First `same-PR-mitigatable` case validation** — S2775 was the first exemplar; watch S2776+ for second occurrence before proposing codification
20. **Postgres cleanup follow-ups (S2774 carryover):**
    - Decide whether to `brew uninstall postgresql@16` (data preserved as archive)
    - Decide whether to drop pg15's `test_unified_donkey_betz` DB or leave for future test runs

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2775 artifacts:**

- **New backend module:** `core/services/process_freshness.py` (176-line extraction — module-level `compute_process_staleness()`)
- **Amended backend modules:** `core/services/td_handlers_ops.py` (line 441-454 — method body → wrapper); `core/management/commands/session_lifecycle.py` (+ `history` subparser + freshness helper + hook)
- **New test file:** `core/tests/test_session_freshness_2775.py` (10 tests)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md`
- **Handoff:** `docs/handoffs/SESSION_2775_SESSION_FRESHNESS_VERDICTS_JSONL_RATIFIED.md`
- **Predecessor envelopes:** S2774 (URLConf lambda cleanup + same-PR capstone), S2773 (query-param allowlist + refactor), S2772 (auth-regression + staff gate), S2771 (CCL v2 full-text search + S2771 rule origin)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §7.4.4 (v0.6.0, S2766)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2775
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `/api/ops/*` endpoints unchanged. `logs/session_freshness.jsonl` (local-only, gitignored) will populate with real rows starting at S2776 open.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2775 merge) |
| Playbook version | v0.6.0 (RATIFIED S2766) |
| Playbook rule count | 202 |
| RUR-C1 state | S2755→S2774 CLOSED · **S2775 N15 session-open freshness JSONL CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-77bdf04032204741` (retired at S2775 close, force=true, sixth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-77bdf04032204741` (retired; forces fresh mint at S2776 open) |
| Live infra state | S2755→S2774 diagnostic infra + Playbook v0.6.0 + N19 URLConf cleanup + **S2775 N15 freshness telemetry substrate** operational |
| Postgres :5432 | pg15 (July DB, 382 migrations, S2775 state) — brew launchd `started`, survives reboot |
| Postgres pg16 | Parked (April fossil, data preserved on disk, plist unloaded) |
| Freshness log | `logs/session_freshness.jsonl` (gitignored). First natural row lands at S2776 open. |
| Next move | Chris selects at S2776 open |

---

## Recommended session-open protocol (S2776)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2775 envelope §4 (Rigby SIGN summary, S2771 rule fifth consecutive) + §8 (Meta-observation — emerging zoom-out classification + mechanism-now/value-later class)
4. Skim the S2775 close-ceremony bundle — first non-ops-surface arc since S2770 streak
5. **Freshness + regression + browser eyeball** — see S2776 open sequence in §SESSION PIN above
6. If `staleness_verdict != FRESH` → escalate to Chris (tenth-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
7. **Check `brew services list | grep postgres` FIRST** if freshness fails in unusual pattern (missing roles / stale conversations) — port-collision root cause is the fast path
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. **NEW at S2776:** run `python manage.py session_lifecycle history --limit 3` after minting fresh pin to see the FIRST natural N15 row lands
10. Present candidate menu with **at least one open-ended zoom-out ask in the Rigby SIGN** (per S2771 rule, validated 5 sessions in a row)
11. Chris directs S2776 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2776:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 refreshed to S2775; L7 unchanged)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.6.0 (latest ratified)
3. [`docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md`](docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md) — S2775 envelope
4. [`docs/handoffs/SESSION_2775_SESSION_FRESHNESS_VERDICTS_JSONL_RATIFIED.md`](docs/handoffs/SESSION_2775_SESSION_FRESHNESS_VERDICTS_JSONL_RATIFIED.md) — S2775 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md`](docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md) — S2774 predecessor
6. `core/services/process_freshness.py` — new this session (module-level extraction)
7. `core/management/commands/session_lifecycle.py` — amended this session (freshness hook + history reader)
