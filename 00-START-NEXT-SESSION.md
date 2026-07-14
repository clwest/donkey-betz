# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2778 CLOSED — PLAYBOOK v0.7.0 RATIFIED (ZOOM-OUT SIGN DISCIPLINE)

**Refreshed 2026-07-13 (SESSION 2778 CLOSED — N23 shipped as Playbook v0.7.0 MINOR amendment. Two new [GR] rules ratified into Chapter 6 §6.10: PLAYBOOK-6.10.7 (every joint SIGN routing MUST include ≥1 open-ended zoom-out ask; "joint SIGN routing" definition inlined) + PLAYBOOK-6.10.8 (folds MUST be classified {`same_pr_actionable`/`same_pr_mitigatable`/`future_trigger`} + persisted to `logs/zoom_out_classifications.jsonl` via `record_zoom_out_concern` before D-verdict; no-folds carve-out; graceful-degradation clause). Rule count 202 → 204. Second consecutive same-session MINOR amendment shipped after v0.6.0/S2766 precedent. **Second F-BLOCKING DISAGREE in as many amendments** — V1 rule-ID collision (PLAYBOOK-6.10.7 pre-allocated for I-0302 three-PR pattern candidate) surfaced only because SIGN was tool-grounded per S2777 anti-rubber-stamp lesson; resolved via PLAYBOOK-10.7.5 next-integer rule (N23 takes 6.10.7/6.10.8; I-0302 re-slots to 6.10.9). **First substrate dogfooded at authoring** — 4 V6 zoom-out folds classified + persisted to ledger BEFORE D-verdict, demonstrating PLAYBOOK-6.10.8 in-wild before it was even ratified. Ledger grew 13 → 17 rows. Anti-rubber-stamp gate PASS on turn 1 (6+ real `search_docs` invocations). Thirteenth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2778 shipped as 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Playbook body:** `docs/ENGINEERING_PLAYBOOK.md` — frontmatter version bump 0.6.0 → 0.7.0; §6.10 preamble extended; PLAYBOOK-6.10.7 + 6.10.8 rules added; §6.12 extension points augmented (2 new items); Appendix D v0.7.0 row; Chapter 6 frontmatter rule-ID range extended.
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md`
- **Handoff:** `docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`
- **CLAUDE.md:** L3 anchor + L7 constitutional governance anchor both refreshed to v0.7.0
- **Docs cascade:** 4-step + provenance rebuild
- **Post-merge:** `make recycle-all` invoked per PLAYBOOK-7.4.4 (thirteenth cycle)
- **Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 17 rows (5+7+1 from S2774–S2777 backfill + 4 same_pr_actionable from S2778 dogfood)

---

## SESSION-OPEN INFRA STORY (S2778)

S2778 opened as continuation of S2777 close-ceremony flow. Post-S2777-merge recycle produced third natural N15 hook fire at S2778 pin mint — verdict FRESH · SHA `59db8626324d` · celery_stale=0/5. Trend surface at `logs/session_freshness.jsonl` now has 3 rows (1 shell + 2 natural).

Fresh pin `pa-ced04dddd39346a9` minted for N23 arc.

**Anti-rubber-stamp gate operationalized.** Per S2777 lesson, S2778 turn 1 SIGN dispatch included explicit anti-rubber-stamp directives ("empty tool_runs = anti-rubber-stamp signal per S2777 lesson"). Rigby returned V1..V6 with 6+ real `search_docs` invocations. Contrast S2777 turn 1's 0-tool-runs rubber-stamp; discipline held.

**Turn 1 V1 F-BLOCKING DISAGREE.** Rigby's tool-grounded verification found PLAYBOOK-6.10.7 pre-allocated for I-0302 three-PR pattern candidate (`RATIFICATION_2026-07-10_i0302_arc_close.md` §11 + `SESSION_2751_I0302_ARC_CLOSED.md` §4). Would have shipped rule-ID collision. Resolved by PLAYBOOK-10.7.5 next-integer rule (pre-allocation in candidate doc ≠ ratified reservation) — N23 takes 6.10.7 + 6.10.8; I-0302 re-slots to 6.10.9.

**Turn 2 V6 zoom-out ask produced 4 same_pr_actionable folds** — all classified + persisted via `record_zoom_out_concern` BEFORE D-verdict (dogfooding PLAYBOOK-6.10.8 before it was ratified):
- V6a: sequencing risk → explicit envelope + Appendix D note
- V6b: single-point-of-failure → graceful-degradation clause in rule text
- V6c: definition drift → "joint SIGN routing" inlined in rule 6.10.7
- V6d: tiny-SIGN ceremony → no-folds carve-out in rule 6.10.8

**Turn 3 verdict lock-in.** Rigby AGREE on corrected design with all folds incorporated. Route to Chris per `feedback_claude_rigby_agree_first_chris_yes_no`.

**Chris D-verdict: "yes ship it"** — full amendment cycle authorized.

---

## THE PIVOT — WHY THIS SHIP MATTERS

Four novel-precedent moments this session:

1. **Anti-rubber-stamp discipline paid off on first application.** S2777 lesson (AGREE x4 + 0 tool_runs = rubber-stamp) was operationalized as explicit turn-1 dispatch directive at S2778. Result: 6+ real `search_docs` invocations, F-BLOCKING DISAGREE surfaced, ship-time collision avoided.

2. **Second F-BLOCKING DISAGREE in as many amendments.** v0.6.0/S2766 W1 caught PATCH→MINOR constitutional reclassification; v0.7.0/S2778 V1 caught rule-ID collision. Different axes of failure; same defense: tool-grounded SIGN.

3. **Substrate dogfooded at authoring.** N22's own successor (N23) uses the classification substrate before the codification rule was ratified. 4 V6 folds classified + persisted to ledger during authoring. This is the ideal validation loop — codify what already works, verified by using it during codification.

4. **Second consecutive same-session MINOR amendment.** v0.6.0/S2766 + v0.7.0/S2778 both shipped author+SIGN+ratify+merge in a single session. Substantiates that pre-built substrate (S2765/S2777 respectively) enables tight amendment cycles.

The S2771 rule streak now covers 8 sessions (S2771–S2778) with 2 F-BLOCKING DISAGREEs and 1 constitutional codification. The pattern is:

1. Memory rule authored at close (S2771)
2. In-wild application streak with progressively more evidence (S2772–S2777)
3. Substrate ship when observable-worthy (S2777 N22)
4. Constitutional codification (S2778 N23)
5. Dogfooding at codification (S2778 V6)

If a third memory-rule-to-Playbook pipeline follows this shape, extraction as a §11 or Ch 2 methodology rule becomes a candidate.

---

## S2779 CANDIDATES (Chris selects at open)

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

**Note discipline:** ops-surface PRs paused per S2774 forward-carry. Unblock triggers unchanged.

- **N17** — `session_number` pill in the search chip when text is set — small UX polish. **Non-ops-surface — not gated.**
- **N24** — Anti-rubber-stamp SIGN codification. **2 triggers observed** (S2777 turn 1 rubber-stamp catch + S2778 V1 rule-ID collision that would have shipped without tool-grounded verification). MINOR amendment candidate extending PLAYBOOK-6.10.7 or 6.10.8 with explicit tool_runs assertion. Ready for authoring — same shape as N23.
- **First N23-rule application in-wild** — S2779 will be the first session where PLAYBOOK-6.10.7 + 6.10.8 govern SIGN routing constitutionally (not just as memory rule). Any joint SIGN this session becomes evidence for the rule; watch for graceful-degradation clause activation (would validate degradation path in-wild).
- **N22 v2 candidates** — Django model migration OR PA-tool read surface OR JSONL rotation. Ledger at 17 rows; rotation trigger still ~500 rows away.
- **N15 v2 / N21 v2 candidates** — deferred pending row accumulation.

**Gated by ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ lambda-`__import__` sites in `core/urls.py`

**Housekeeping (non-net-new):** S2758 D2 canonical decision (needs joint SIGN), S2758 D4 REPORT-ONLY, N13 handoff-date-format normalizer

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, PA celery bounce, memory rule promotion audit

### Deferred (waiting on triggers, not just calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5 (health_summary/ops_tool.overview overlap)** — trigger unchanged
- **30+ other lambda-`__import__` sites** — no trigger yet

### Post-S2778 owed

- **I-0302 three-PR pattern amendment** — when it opens, take PLAYBOOK-6.10.9 (per S2778 sequencing note).
- **Anti-rubber-stamp SIGN codification (N24)** — 2 triggers observed; ready for MINOR when Chris authorizes.
- **Memory rule promotion audit** — sweep MEMORY.md for two-trigger candidates. `feedback_zoom_out_ask_per_rigby_sign` now discharged (constitutional at v0.7.0); `feedback_verify_rigby_tool_runs_before_trusting_sign` at 2 triggers.

---

## SESSION PIN — S2778 RETIRED (fresh mint required at S2779 open)

**Pin history (S2778):**

- `pa-ced04dddd39346a9` (label `s2778-n23-zoom-out-classification-playbook-amendment`) minted S2778 open; **retired at S2778 close (force=true, NINTH consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-ced04dddd39346a9` (retired)** — intended failure mode forces S2779 first-action fresh mint.

**S2779 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2778 envelope §5 (joint SIGN 3-turn loop with V1 F-BLOCKING DISAGREE + V6 folds)
# Read S2778 envelope §8 (post-ratification bindings — v0.7.0 now governs SIGN)
# Read S2778 handoff §2 (novel-precedent moments)

# Freshness check. Should be FRESH · SHA-match at S2778 close SHA — THIRTEENTH close-cycle after PLAYBOOK-7.4.4.
# N15 hook fires automatically at open — inspect the row landing in logs/session_freshness.jsonl.
bash tools/pa_local.sh "S2779 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2778 close at top; all N7-enriched)"

# Regression check: run 5-suite ops+substrate stack (unchanged from S2778)
python manage.py test core.tests.test_ops_auth_regression_2772 core.tests.test_ops_query_param_allowlist_2773 core.tests.test_session_freshness_2775 core.tests.test_pa_wrapper_ownership_2776 core.tests.test_zoom_out_classifications_2777 --noinput

# Ledger check: confirm 17-row baseline survived merge
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
start = d.find('{')
r = json.loads(d[start:])
assert r['total_rows']==17, r
print('OK — 17 rows, counts:', r['counts_by_classification'])
"

# Playbook v0.7.0 verify — new rules present
grep -c 'PLAYBOOK-6\.10\.[7-8]' docs/ENGINEERING_PLAYBOOK.md  # expect >=5

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops
#   - All 6 ops endpoints still return same shapes
#   - /api/pa/whoami/ still returns {username, user_id, is_staff} when authenticated

# Mint fresh pin scoped to selected S2779 candidate. Fourth natural N15 row lands here.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed. N21 prelude will fire on first invocation of the new pin.

**Anti-rubber-stamp check on S2779 first Rigby SIGN:** verify `tool_runs` non-empty in the task result before treating any SIGN verdict as substantive. **PLAYBOOK-6.10.7 + 6.10.8 now constitutional at v0.7.0** — every joint SIGN routing MUST include ≥1 zoom-out ask, and any folds MUST be classified + persisted via `record_zoom_out_concern` before D-verdict.

---

## OPEN RUNTIME ITEMS (from S2778 close)

1. **N17 / N24 net-new engineering** — see Candidates above
2. **S2761 smoke test** — ops-surface (gated)
3. **S2758 D2 canonical decision** — needs Rigby joint SIGN (governed by v0.7.0 now)
4. **S2758 D4 HIGH-RISK wiring extension** — REPORT-ONLY
5. **N13 handoff-date-format normalizer** — hygiene one-shot
6. **P0.5 cost-threshold advance-to-freeze**
7. **P0.75 CI billing**
8. **PA celery worker bounce**
9. **RUR-C2 open eligible**
10. **S2758 D1 process_pa_chat_task payload strip**
11. **S2758 D5 local shim retirement**
12. **HMAC signing of `x-acting-user-id`**
13. **Memory rule promotion audit** — `feedback_zoom_out_ask_per_rigby_sign` DISCHARGED; N24 anti-rubber-stamp SIGN candidate at 2 triggers
14. **First observed partial-recycle event** — trigger for N10 UI badge + first N11 tile fire
15. **Rigby S2774 forward-carry: pause ops-surface PRs** — still held; unblock triggers unchanged
16. **30+ other lambda-`__import__` sites** — refactor when future arc naturally touches
17. **Rigby S2773 forward-carry #5 (health_summary overlap)** — trigger unchanged
18. **N15 v2 candidates** — deferred pending row accumulation + user-visible ask
19. **N21 v2 candidates** — deferred pending trigger
20. **`session_lifecycle` refactor trigger** — still armed (4 subcommands; trigger at 3rd API/cache flag)
21. **`/api/pa/*` future-endpoint audit trigger** — every proposal must satisfy the sharp 5-point test
22. **N22 v2 candidates** — Django model, PA-tool read, JSONL rotation (rotation ~500 rows away)
23. **N24 anti-rubber-stamp SIGN codification** — 2 triggers observed; ready for future MINOR amendment
24. **I-0302 three-PR pattern amendment** — when it opens, take PLAYBOOK-6.10.9
25. **First graceful-degradation clause activation** — watch for `record_zoom_out_concern` tool failure that invokes PLAYBOOK-6.10.8 fallback path
26. **Postgres cleanup follow-ups (S2774 carryover):**
    - Decide whether to `brew uninstall postgresql@16` (data preserved as archive)
    - Decide whether to drop pg15's `test_unified_donkey_betz` DB or leave for future test runs

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2778 artifacts:**

- **Playbook body:** `docs/ENGINEERING_PLAYBOOK.md` v0.7.0 (rule count 204; §6.10 grows to 8 rules)
- **New rules:** PLAYBOOK-6.10.7 (zoom-out ask mandate) + PLAYBOOK-6.10.8 (classify + persist)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md`
- **Handoff:** `docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`
- **Predecessor amendments:** v0.6.0 (S2766, PLAYBOOK-7.4.4), v0.5.0 (S2753, 5 rules), v0.4.1 (S2742, informative), v0.4.0 (S2740, PLAYBOOK-6.10.6), v0.3.0 (S2738, PLAYBOOK-6.6.14+6.10.5), v0.2.0 (S2736, 3 EOS rules), v0.1.0 (S2727, inaugural)
- **N22 substrate exercised:** `core/management/commands/record_zoom_out_concern.py` (4 dogfood invocations at S2778 authoring), `logs/zoom_out_classifications.jsonl` (17 rows)
- **Constitutional context:** `docs/ENGINEERING_PLAYBOOK.md` §6.10.7-§6.10.8 (v0.7.0, S2778)

🖥️ **Workspace UI — `/workspaces` surface:**

- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — v0.7.0 ratification envelope + content mirror land here
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` grows +N per session per PLAYBOOK-6.10.8 (17 rows at S2778 close)
  - `logs/session_freshness.jsonl` — 3 rows (grows +1 per session_lifecycle open)
  - `/api/pa/whoami/` returns `{username, user_id, is_staff}` when authenticated
  - `/api/ops/*` endpoints unchanged

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2778 merge) |
| Playbook version | **v0.7.0 (RATIFIED S2778)** |
| Playbook rule count | **204** |
| RUR-C1 state | S2755→S2776 CLOSED · S2777 N22 CLOSED · **S2778 N23 v0.7.0 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-ced04dddd39346a9` (retired at S2778 close, force=true, ninth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-ced04dddd39346a9` (retired; forces fresh mint at S2779 open) |
| Live infra state | S2755→S2777 diagnostic infra + **Playbook v0.7.0 zoom-out SIGN discipline** + N15/N19/N21/N22 substrate operational |
| Postgres :5432 | pg15 (July DB, S2778 state) — brew launchd `started`, survives reboot |
| Postgres pg16 | Parked (April fossil, data preserved on disk, plist unloaded) |
| Freshness log | `logs/session_freshness.jsonl` — 3 rows |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **17 rows** (9 actionable / 7 mitigatable / 1 future-trigger) |
| Wrapper ownership cache | `~/.claude-pa-verified/<pin>.json` — populates on first bash invocation per pin |
| Next move | Chris selects at S2779 open |

---

## Recommended session-open protocol (S2779)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2778 envelope §5 (joint SIGN 3-turn loop with V1 F-BLOCKING DISAGREE + V6 folds) + §7 (provenance chain enumerating v0.7.0 forward-carry)
4. Read S2778 handoff §2 (novel-precedent moments) + §8 (meta-observation on memory-rule-to-Playbook pipeline)
5. **Freshness + regression + ledger + Playbook verify + browser eyeball** — see S2779 open sequence in §SESSION PIN above
6. **Watch for** the N15 fourth natural row landing at S2779 pin mint + N21 prelude firing at first bash invocation of the new pin + ledger 17-row baseline surviving merge + Playbook §6.10.7/6.10.8 grep hits >=5
7. If `staleness_verdict != FRESH` → escalate to Chris (thirteenth-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
8. **Check `brew services list | grep postgres` FIRST** if freshness fails in unusual pattern
9. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
10. Present candidate menu — **PLAYBOOK-6.10.7 is now constitutional**, so joint SIGN MUST include ≥1 zoom-out ask, and any folds MUST be classified + persisted via `record_zoom_out_concern` before D-verdict per PLAYBOOK-6.10.8
11. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty (memory rule still applies; N24 codification pending 3rd trigger)
12. Chris directs S2779 P0 selection
13. Mint fresh pin with candidate-scoped label
14. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2779:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L3 + L7 refreshed to S2778/v0.7.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — **v0.7.0 (latest ratified)**
3. [`docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md`](docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md) — S2778 envelope
4. [`docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`](docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md) — S2778 handoff
5. [`docs/research/implementation/RATIFICATION_2026-07-13_zoom_out_classifications_helper.md`](docs/research/implementation/RATIFICATION_2026-07-13_zoom_out_classifications_helper.md) — S2777 N22 substrate envelope
6. `core/management/commands/record_zoom_out_concern.py` — v0.7.0 constitutionally mandated (PLAYBOOK-6.10.8)
7. `logs/zoom_out_classifications.jsonl` — 17 rows; grows per PLAYBOOK-6.10.8
