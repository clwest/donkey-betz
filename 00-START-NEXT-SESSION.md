# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2779 CLOSED — N22 v2 SHIPPED (ops_tool.zoom_out_ledger PA-tool read surface)

**Refreshed 2026-07-13 (SESSION 2779 CLOSED — N22 v2 shipped as PR #3170, merged as `c4a5f4766`. First S2779 in-wild exercise of Playbook v0.7.0 constitutional discipline (PLAYBOOK-6.10.7 zoom-out ask mandate + PLAYBOOK-6.10.8 fold classification + persistence). Read path for `logs/zoom_out_classifications.jsonl` promoted from CLI-only (`zoom_out_streak_report`) to PA-tool action so Rigby can consult prior folds inside SIGN loops. Advisory posture preserved via 3 redundant response fields (`advisory` header + `is_gate: false` + `semantics: "advisory_pattern_evidence"`). Joint SIGN outcome: V1..V5 PASS + V6 zoom-out produced 1 fold classified `future_trigger` (ops_tool scope creep, factor out dedicated tool when 2nd non-runtime action added OR first non-Rigby consumer). Fold persisted to ledger row 18 BEFORE D-verdict per PLAYBOOK-6.10.8. Anti-rubber-stamp gate PASS on turn 1 (6+ real `search_docs`/`repo_tool` invocations). No F-BLOCKING DISAGREE — smoothest close-cycle in the S2771 streak (substrate coherence: N22 write path S2777 → v0.7.0 codification S2778 → N22 v2 read surface S2779). Fourteenth close-cycle post-PLAYBOOK-7.4.4-codification. Ledger grew 17 → 18 rows.)**

**S2779 shipped as 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **PA tool schema:** `core/services/pa_tool_schemas.py` — `zoom_out_ledger` added to `ops_tool` action enum + description; new `classification` / `session` / `arc` param definitions; `limit` extended to cover new action.
- **Handler:** `core/services/td_handlers_ops.py` — new `_ops_zoom_out_ledger` (182 lines) + dispatch elif branch.
- **Test suite:** `core/tests/test_ops_zoom_out_ledger_2779.py` — 17 tests, 8 contracts.
- **Handoff:** `docs/handoffs/SESSION_2779_N22V2_ZOOM_OUT_LEDGER_READ_SURFACE.md`
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (fourteenth cycle).
- **Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 18 rows (9 same_pr_actionable / 7 same_pr_mitigatable / 2 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2779)

S2779 opened as continuation of S2778 close-ceremony flow. Post-S2778-merge state at S2779 open was **STALE_BOTH** at pin mint (celery_stale=5/5) — expected: the previous session's post-merge recycle was executed but the workers had been running since the pre-merge close-ceremony recycle. Session-open protocol calls out this exact case; ran `make recycle-all` to bootstrap S2779 workers against HEAD.

Fresh pin `pa-ded8f613d04c4753` minted with label `s2779-n22v2-zoom-out-pa-tool-read-surface`. Wrapper `tools/pa_local.sh` repointed. Ownership check PASS via wrapper (`token=chris · pin_owner=chris`).

**Anti-rubber-stamp gate operationalized (S2777 lesson still standing).** S2779 T1 SIGN dispatch included explicit "empty tool_runs = anti-rubber-stamp signal" directive. Rigby returned V1..V6 with 6+ real `search_docs` + `repo_tool` invocations. Gate held on first application post-v0.7.0.

**V6 zoom-out fold classified + persisted before D-verdict.** Rigby surfaced 1 fold (ops_tool scope creep). Classified `future_trigger`. Persisted to ledger row 18 via `record_zoom_out_concern` BEFORE routing to Chris for D-verdict — first application of PLAYBOOK-6.10.8 discipline as constitutional rule (v0.7.0), not memory rule.

**Chris D-verdict: "ship it"** — full ship cycle authorized in one turn (no design correction needed).

---

## THE PIVOT — WHY THIS SHIP MATTERS

**Substrate coherence produces tight amendment cycles.** N22 shipped the write path (S2777) → v0.7.0 codified the discipline (S2778) → N22 v2 shipped the read surface the codification implied (S2779). Three sessions, three cleanly-scoped shipments, each building on the last with no framing debt. The v0.7.0 constitutional discipline was designed to make SIGN loops MORE substantive; N22 v2 gives Rigby the surface to consult her own SIGN history when she's asked to zoom out — closing the loop between codification and in-wild use.

**No F-BLOCKING DISAGREE this session** — contrast S2778 V1 rule-ID collision catch and S2776 Q1 pin lifecycle catch. Every substantive fold this session was non-blocking. This is not a rubber-stamp signal (the anti-rubber-stamp gate held with 6+ real tool_runs); it's what a healthy joint SIGN looks like when the substrate is coherent and the design has no ship-time hazards.

**First v0.7.0 in-wild exercise held on all three constitutional axes:**

- PLAYBOOK-6.10.7 (zoom-out ask mandate) — V6 phrased open-endedly, produced substantive fold
- PLAYBOOK-6.10.8 (fold classification + ledger persistence before D-verdict) — followed exactly (18th ledger row entered before Chris was asked)
- Anti-rubber-stamp discipline (still memory rule, N24 codification candidate) — held on turn 1

**S2771 rule streak now covers 9 sessions (S2771–S2779)** with 2 F-BLOCKING DISAGREEs and 1 constitutional codification. Every session has produced substantive folds or a novel-precedent moment — no drift into ritual.

---

## S2780 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

**Note discipline:** ops-surface PRs still paused per S2774 forward-carry. Unblock triggers unchanged. N22 v2 was a PA-tool surface (not `/api/ops/*`) — unaffected.

- **N17** — `session_number` pill in the search chip when text is set — small UX polish. **Non-ops-surface — not gated.**
- **N24** — Anti-rubber-stamp SIGN codification. **2 triggers observed** (S2777 T1 rubber-stamp catch + S2778 V1 rule-ID collision that would have shipped without tool-grounded verification). S2779 T1 gate PASS is not a new trigger (rule already followed). MINOR amendment candidate extending PLAYBOOK-6.10.7 or 6.10.8 with explicit tool_runs assertion. Ready for authoring — same shape as N23.
- **N22 v3 candidates** — Workspace UI surface for the ledger (trigger: Chris eyeball-read request); Django model migration (trigger unchanged); JSONL rotation (~500 rows away); auto-hook into ratification envelope creation (docstring still names as future_trigger).
- **N22 v2 usage-in-wild** — S2780 will be the first session where Rigby can consult the ledger via PA tool during her own SIGN loops. Watch for actual consultation invocations at V6 slots.
- **N15 v2 / N21 v2 candidates** — deferred pending row accumulation.

**Gated by ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ lambda-`__import__` sites in `core/urls.py`

**Housekeeping (non-net-new):** S2758 D2 canonical decision (needs joint SIGN), S2758 D4 REPORT-ONLY, N13 handoff-date-format normalizer

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5 (health_summary/ops_tool.overview overlap)** — trigger unchanged
- **30+ other lambda-`__import__` sites** — no trigger yet
- **N22 v2 time-window filters (`since`/`before`)** — deferred until ledger has enough temporal spread (~50+ rows across weeks)
- **Dedicated `zoom_out_tool` factor-out** — persisted to ledger row 18; explicit trigger: 2nd non-runtime observability action added to ops_tool OR first non-Rigby consumer

### Post-S2779 owed

- **I-0302 three-PR pattern amendment** — when it opens, take PLAYBOOK-6.10.9 (per S2778 sequencing note).
- **Anti-rubber-stamp SIGN codification (N24)** — 2 triggers observed; ready for MINOR when Chris authorizes.
- **Memory rule promotion audit** — sweep MEMORY.md for two-trigger candidates.
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — watch for `record_zoom_out_concern` command failure that invokes the fallback path (validates degradation clause in-wild).

---

## SESSION PIN — S2779 RETIRED (fresh mint required at S2780 open)

**Pin history (S2779):**

- `pa-ded8f613d04c4753` (label `s2779-n22v2-zoom-out-pa-tool-read-surface`) minted S2779 open; **retired at S2779 close (force=true, TENTH consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-ded8f613d04c4753` (retired)** — intended failure mode forces S2780 first-action fresh mint.

**S2780 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2779 handoff §2 (first v0.7.0 in-wild exercise) + §8 (substrate coherence meta-observation)

# Freshness check. Should be FRESH · SHA-match at S2779 close SHA (c4a5f4766) — FOURTEENTH close-cycle after PLAYBOOK-7.4.4.
# N15 hook fires automatically at open — inspect the row landing in logs/session_freshness.jsonl.
bash tools/pa_local.sh "S2780 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2779 close at top; all N7-enriched)"

# NEW at S2780: Rigby can now consult the zoom-out ledger via PA tool
bash tools/pa_local.sh "S2780 open — smoke ops_tool.zoom_out_ledger (default) — confirm 18-row baseline + advisory posture intact post-S2779 merge"

# Regression check: run 6-suite ops+substrate stack (S2779 adds the new test file)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_session_freshness_2775 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_ops_zoom_out_ledger_2779 \
  --noinput

# Ledger check: confirm 18-row baseline survived merge
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
start = d.find('{')
r = json.loads(d[start:])
assert r['total_rows']==18, r
print('OK — 18 rows, counts:', r['counts_by_classification'])
"

# Playbook v0.7.0 verify — new rules still present
grep -c 'PLAYBOOK-6\.10\.[7-8]' docs/ENGINEERING_PLAYBOOK.md  # expect >=5

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - All 6 ops endpoints still return same shapes
#   - /api/pa/whoami/ still returns {username, user_id, is_staff} when authenticated

# Mint fresh pin scoped to selected S2780 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed. N21 prelude will fire on first invocation of the new pin.

**Anti-rubber-stamp check on S2780 first Rigby SIGN:** verify `tool_runs` non-empty in the task result before treating any SIGN verdict as substantive. **PLAYBOOK-6.10.7 + 6.10.8 constitutional at v0.7.0** — every joint SIGN routing MUST include ≥1 zoom-out ask, and any folds MUST be classified + persisted via `record_zoom_out_concern` before D-verdict. Rigby can now consult prior folds via `ops_tool.zoom_out_ledger` during SIGN loops.

---

## OPEN RUNTIME ITEMS (from S2779 close)

1. **N17 / N24 / N22 v3 net-new engineering** — see Candidates above
2. **S2761 smoke test** — ops-surface (gated)
3. **S2758 D2 canonical decision** — needs Rigby joint SIGN (governed by v0.7.0 now)
4. **S2758 D4 HIGH-RISK wiring extension** — REPORT-ONLY
5. **N13 handoff-date-format normalizer** — hygiene one-shot
6. **P0.5 cost-threshold advance-to-freeze**
7. **P0.75 CI billing**
8. **RUR-C2 open eligible**
9. **S2758 D1 process_pa_chat_task payload strip**
10. **S2758 D5 local shim retirement**
11. **HMAC signing of `x-acting-user-id`**
12. **Memory rule promotion audit** — `feedback_zoom_out_ask_per_rigby_sign` DISCHARGED; N24 anti-rubber-stamp SIGN candidate at 2 triggers
13. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
14. **Rigby S2774 forward-carry: pause ops-surface PRs** — still held; unblock triggers unchanged
15. **30+ other lambda-`__import__` sites** — refactor when future arc naturally touches
16. **Rigby S2773 forward-carry #5 (health_summary overlap)** — trigger unchanged
17. **N15 v2 candidates** — deferred pending row accumulation + user-visible ask
18. **N21 v2 candidates** — deferred pending trigger
19. **`session_lifecycle` refactor trigger** — still armed
20. **`/api/pa/*` future-endpoint audit trigger** — every proposal must satisfy the sharp 5-point test
21. **N22 v3 candidates** — Workspace UI surface / Django model / JSONL rotation / auto-hook
22. **Dedicated `zoom_out_tool` factor-out** — persisted to ledger row 18; explicit trigger: 2nd non-runtime action OR first non-Rigby consumer
23. **N22 v2 time-window filters** — deferred until ~50+ rows temporal spread
24. **N24 anti-rubber-stamp SIGN codification** — 2 triggers observed; ready for future MINOR amendment
25. **I-0302 three-PR pattern amendment** — when it opens, take PLAYBOOK-6.10.9
26. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — watch for `record_zoom_out_concern` command failure
27. **Postgres cleanup follow-ups (S2774 carryover):**
    - Decide whether to `brew uninstall postgresql@16` (data preserved as archive)
    - Decide whether to drop pg15's `test_unified_donkey_betz` DB or leave for future test runs

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2779 artifacts:**

- **PA tool schema:** `core/services/pa_tool_schemas.py` — `zoom_out_ledger` action + new filter params
- **Handler:** `core/services/td_handlers_ops.py` — `_ops_zoom_out_ledger` (182 lines)
- **Test suite:** `core/tests/test_ops_zoom_out_ledger_2779.py` — 17 tests, 8 contracts
- **Handoff:** `docs/handoffs/SESSION_2779_N22V2_ZOOM_OUT_LEDGER_READ_SURFACE.md`
- **Predecessor:** `docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md` (constitutional context)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §6.10.7-§6.10.8 (v0.7.0, S2778)
- **Substrate:** `core/management/commands/record_zoom_out_concern.py` (write path, S2777)
- **CLI companion:** `core/management/commands/zoom_out_streak_report.py` (unchanged; still authoritative for terminal reads)

🖥️ **Workspace UI — `/workspaces` surface:**

- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — Playbook v0.7.0 envelope + content mirror live here
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` grows +N per session per PLAYBOOK-6.10.8 (18 rows at S2779 close)
  - `logs/session_freshness.jsonl` — 4 rows (grows +1 per session_lifecycle open)
  - `logs/recycle_events.jsonl` — grows per `make recycle-all` (S2779 close cycle: 2 clean recycles)
  - `/api/pa/whoami/` returns `{username, user_id, is_staff}` when authenticated
  - `/api/ops/*` endpoints unchanged
  - **NEW:** `ops_tool.zoom_out_ledger` PA tool action (Rigby-consumable read of the ledger)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `c4a5f4766` (S2779 close, N22 v2 merge) |
| Playbook version | v0.7.0 (RATIFIED S2778) |
| Playbook rule count | 204 |
| RUR-C1 state | S2755→S2778 CLOSED · **S2779 N22 v2 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-ded8f613d04c4753` (retired at S2779 close, force=true, tenth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-ded8f613d04c4753` (retired; forces fresh mint at S2780 open) |
| Live infra state | S2755→S2778 diagnostic infra + Playbook v0.7.0 zoom-out SIGN discipline + N15/N19/N21/N22 substrate operational + **N22 v2 PA-tool read surface live** |
| Postgres :5432 | pg15 (July DB, S2779 state) — brew launchd `started`, survives reboot |
| Postgres pg16 | Parked (April fossil, data preserved on disk, plist unloaded) |
| Freshness log | `logs/session_freshness.jsonl` — 4 rows (S2779 pin mint added 1) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **18 rows** (9 actionable / 7 mitigatable / 2 future_trigger) |
| Wrapper ownership cache | `~/.claude-pa-verified/<pin>.json` — populates on first bash invocation per pin |
| Next move | Chris selects at S2780 open |

---

## Recommended session-open protocol (S2780)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2779 handoff §2 (first v0.7.0 in-wild exercise on all 3 constitutional axes) + §8 (substrate coherence meta-observation)
4. **Freshness + regression + ledger + zoom_out_ledger smoke + Playbook verify + browser eyeball** — see S2780 open sequence in §SESSION PIN above
5. **Watch for** the N15 fourth natural row landing at S2780 pin mint + N21 prelude firing at first bash invocation of the new pin + ledger 18-row baseline surviving merge + Playbook §6.10.7/6.10.8 grep hits >=5 + `ops_tool.zoom_out_ledger` returning advisory posture correctly
6. If `staleness_verdict != FRESH` → escalate to Chris (fourteenth-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
7. **Check `brew services list | grep postgres` FIRST** if freshness fails in unusual pattern
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — **PLAYBOOK-6.10.7 + 6.10.8 constitutional at v0.7.0**; joint SIGN MUST include ≥1 zoom-out ask, folds MUST be classified + persisted before D-verdict. Rigby can now consult prior folds via `ops_tool.zoom_out_ledger` during SIGN loops.
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty (memory rule still applies; N24 codification pending 3rd trigger)
11. Chris directs S2780 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2780:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — **v0.7.0 (latest ratified)**
3. [`docs/handoffs/SESSION_2779_N22V2_ZOOM_OUT_LEDGER_READ_SURFACE.md`](docs/handoffs/SESSION_2779_N22V2_ZOOM_OUT_LEDGER_READ_SURFACE.md) — S2779 handoff
4. [`docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`](docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md) — S2778 handoff (constitutional context)
5. [`docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md`](docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md) — v0.7.0 envelope
6. `core/services/td_handlers_ops.py` `_ops_zoom_out_ledger` — S2779 read path handler
7. `core/management/commands/record_zoom_out_concern.py` — write path (constitutionally mandated per PLAYBOOK-6.10.8)
8. `logs/zoom_out_classifications.jsonl` — 18 rows; grows per PLAYBOOK-6.10.8
