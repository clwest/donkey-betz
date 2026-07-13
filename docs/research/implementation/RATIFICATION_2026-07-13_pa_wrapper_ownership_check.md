---
title: "PA Wrapper Token/Pin Ownership Verification Ratification Record (2026-07-13)"
status: active
authority: ratification-record
session_added: 2776
ratification_date: 2026-07-13
ratifier: chris
routing: rigby-pa-chat joint SIGN (single design + zoom-out per S2771 rule SIXTH consecutive application) + Chris D-verdict yes on joint recommendation (with alignment on Rigby's swiss-army-knife pushback)
scope: S2776 — N21 (pa_local.sh wrapper token/pin ownership check). NEW `core/views_pa_whoami.py` (bounded 3-field GET view). NEW `core/management/commands/verify_pa_wrapper_ownership.py` (single-concern command, exit codes 0/2/3/4). Bash prelude in `tools/pa_local.sh` (~20 lines, gated by per-pin cache, escape hatch `PA_LOCAL_ALLOW_MISMATCH=1`). Sharp 5-point test codified in `views_pa_whoami.py` module docstring to prevent `/api/pa/*` becoming a second ops-surface subject to the S2774 pause discipline.
serves_arc: substrate hardening — catches S2774 travel-recovery scenario (wrapper token pointing at a Django user that didn't exist on newly-active DB, blocked dispatch for ~30min) in seconds instead of hours. First arc after S2775 N15 mechanism-now/value-later ship, second consecutive non-ops-surface session.
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md (S2775 — first non-ops-surface session in the streak; introduced `same-PR-mitigatable` zoom-out response classification)
  - docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md (S2774 — introduced `same-PR-actionable` capstone-verification classification + ops-surface pause discipline)
  - docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md (S2766 — PLAYBOOK-7.4.4 codification)
ratified_documents:
  - core/views_pa_whoami.py (NEW — 54 lines; `pa_whoami` view + sharp 5-point test docstring)
  - core/urls.py (amended — imported `pa_whoami`; added `path('api/pa/whoami/', ...)` at the top of the `api/pa/*` block)
  - core/management/commands/verify_pa_wrapper_ownership.py (NEW — 190 lines; single-concern command; UUID-safe string normalization for user_id comparison)
  - tools/pa_local.sh (amended — ~20-line bash prelude between exports and dispatch; per-pin cache file gate + escape hatch env var)
  - core/tests/test_pa_wrapper_ownership_2776.py (NEW — 9 tests: 3 view contract + 6 command exit-code/cache contract)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2776 open freshness (S2775-close-pin dispatch to Rigby, post-recycle) — first natural N15 freshness hook fire landed at pin-mint: verdict FRESH · SHA aa3dccc509b6 matches HEAD (TENTH corroboration cycle after PLAYBOOK-7.4.4). Also observed: N15's mechanism-now/value-later shipped its first natural data point.
  - S2776 joint SIGN (Rigby, pin pa-bc40ba1f5dd343f4) — Q1 DISAGREED with Claude lean (extend `session_lifecycle status`) and folded dedicated `verify_pa_wrapper_ownership` command instead on substrate-simplicity grounds; Q2 AGREED on dedicated `/api/pa/whoami/` view and codified 5-point test to prevent `/api/pa/*` surface-bleed; Q3 MOSTLY AGREED with cache design plus one fold (record `verified_user_id` in cache contents for N21 v2 wrapper-side comparison); Q4 (non-blocking) AGREED silent for v1 with sibling `logs/wrapper_ownership.jsonl` preferred over `session_freshness.jsonl` overload; zoom-out (S2771 rule SIXTH consecutive application) surfaced 4 substantive concerns classified as 1 `same-PR-actionable` (a — substrate accretion refactor trigger) + 2 `same-PR-mitigatable` (c — fail-loud blast radius escape hatch; d — 5-point test codification) + 1 `future-trigger` (b — Python entrypoint alternative substrate).
  - Chris D-verdict yes with explicit alignment on Rigby's substrate-simplicity pushback ("agree with Rigby on trying to prevent swiss army knife effects").
  - S2776 capstone SIGN (Rigby, same pin) — `http_smoke_test` custom suite 7/7 PASS (6 `/api/ops/*` endpoints + `/api/pa/whoami/`) at 14-90ms latencies; `ops_tool.version` returns FRESH · head aa3dccc509b6 · 5/5 celery fresh · daphne_pid_age=183s (post-N21-recycle). Bash prelude live E2E: cold cache → verify → success line printed → cache file written → dispatch continued normally; second invocation silent (cache hit).
frozen: true
---

# PA Wrapper Token/Pin Ownership Verification — Ratification Record

Frozen canonical record of Chris's ratification of the S2776 N21 wrapper ownership check on 2026-07-13. Second non-ops-surface arc consecutive (S2775 → S2776). Novel this session: FIRST joint SIGN where Rigby DISAGREED with Claude's F-BLOCKING lean and Chris explicitly aligned with Rigby's substrate-simplicity concern. Tenth close-cycle post-PLAYBOOK-7.4.4-codification. Append-only.

---

## §1. Context

S2774 recovery from the pg16 fossil DB port-collision burned ~30 minutes because the `tools/pa_local.sh` `PA_API_TOKEN` pointed at a Django user that didn't exist on the newly-active pg15 DB, while the wrapper pin was seeded against pg15. Symptoms surfaced only after multiple dispatch failures + log tails made the token/user mismatch visible.

N21 catches that failure mode in seconds instead of hours by verifying at first-invocation-per-pin that `PA_API_TOKEN` and the wrapper pin resolve to the same user. Cache file at `~/.claude-pa-verified/<pin>.json` marks a pin as verified so subsequent invocations skip the check (0-cost stat).

**Trigger origin:** memory rule `feedback_post_travel_port_collision_triage` recorded S2774 close with "would have caught the S2774 chris/donkeyking wrapper drift in seconds" as N21's stated value. S2776 delivers on that.

---

## §2. Ratified Change

Four production files + one test file (~350 net-new lines total):

### (a) NEW `core/views_pa_whoami.py` (54 lines)

Bounded 3-field GET view:

```python
@require_GET
@login_required
def pa_whoami(request):
    return JsonResponse({
        'username': request.user.username,
        'user_id': str(request.user.id),
        'is_staff': bool(request.user.is_staff),
    })
```

Module docstring codifies the **sharp 5-point test** (Rigby zoom-out mitigation d — `same-PR-mitigatable`) for every future `/api/pa/*` proposal:

> Read-only · Deterministic · No side effects · Bounded output schema · Directly needed for toolchain correctness

If any future `/api/pa/*` proposal fails one, it must go through the stricter `/api/ops/*` surface-pause rubric per S2774 forward-carry. `/api/pa/whoami/` is the canonical exemplar.

### (b) AMENDED `core/urls.py`

Grouped import `from core.views_pa_whoami import pa_whoami` added right after `views_ops_console` import block. New `path('api/pa/whoami/', pa_whoami, name='pa-whoami')` inserted at the top of the `api/pa/*` block with a comment referencing the 5-point test rationale.

Direct-callable pattern per S2774 N19 precedent (no lambda wrapper).

### (c) NEW `core/management/commands/verify_pa_wrapper_ownership.py` (190 lines)

Single-concern command per Rigby Q1 DISAGREE fold. Does NOT accrete into `session_lifecycle` alongside pin+wrapper+freshness. Standalone-debuggable.

Exit-code contract:
- **0** — verified · token owner == pin owner · cache written
- **2** — MISMATCH · token owner != pin owner
- **3** — token invalid (missing env, whoami 4xx, Django unreachable, malformed response)
- **4** — pin belongs to no user (orphan)

Cache payload (Rigby Q3 fold — records `verified_user_id` so N21 v2 wrapper prelude can compare without hitting the API):

```json
{"pin": "pa-bc40ba1f5dd343f4",
 "verified_user_id": "e0c9d44b-a876-4b30-b0da-e4d0b10006f6",
 "verified_username": "chris",
 "verified_at": "2026-07-13T23:11:39.103966+00:00"}
```

UUID-safe: user_id normalized to string on both sides (whoami response + ORM lookup) before compare. Works for both UUID and int PK conventions.

### (d) AMENDED `tools/pa_local.sh`

~20-line bash prelude between exports and dispatch. Reads current pin from wrapper's own dispatch line via regex; stat's cache file; on miss invokes management command; touches cache on success; honors `PA_LOCAL_ALLOW_MISMATCH=1` escape hatch (Rigby zoom-out mitigation c — `same-PR-mitigatable`).

### (e) NEW `core/tests/test_pa_wrapper_ownership_2776.py` (9 tests)

- `PaWhoamiViewTests` (3): bounded 3-field payload · rejects unauthenticated (302/401/403) · GET-only (405 on POST)
- `VerifyPaWrapperOwnershipCommandTests` (6): success writes cache · mismatch exits 2 · missing token exits 3 · whoami rejection exits 3 · orphan pin exits 4 · `--json` flag emits ok payload

All URL/HTTP + ORM paths mocked via `urllib.request.urlopen` patch + `patch.dict("os.environ")`. 9/9 PASS in 0.38s.

---

## §3. What Was NOT Changed

**Explicitly out of scope for N21 v1 (per Rigby fold + Chris alignment):**

- **`session_lifecycle` extension.** Rigby DISAGREED with Claude's original lean to add `--wrapper-check` flag on `session_lifecycle status`. Chris explicitly aligned: "agree with Rigby on trying to prevent swiss army knife effects." Substrate stays single-concern. Refactor trigger codified in command docstring: "if `session_lifecycle` gains a THIRD flag that hits the API or reads/writes the wrapper cache, split into `session_lifecycle` (pin+wrapper) + `toolchain_doctor` (freshness + ownership + other)."
- **TTL on the cache file.** Per-pin only; auto-invalidates on rotation. Token revocation within a session's lifetime = deferred to v2 (YAGNI on TTL for v1 per Rigby Q3 fold).
- **`logs/wrapper_ownership.jsonl` trend log.** Silent for v1 per Rigby Q4 alignment. Sibling substrate (not extension of `session_freshness.jsonl`) if trigger surfaces.
- **Wrapper-side user_id compare** (N21 v2 candidate). Cache file already records `verified_user_id` so a future prelude version can compare without hitting the API — Rigby Q3 forward compatibility.
- **Python entrypoint alternative** (`tools/pa_chat.py` doing the check). Deferred as `future-trigger` per Rigby zoom-out b. Keeping the guardrail at the outermost choke point (`pa_local.sh`) for v1.
- **`/api/pa/whoami/` accessible without login.** `@login_required` enforced; test locks the rejection contract.

---

## §4. Rigby SIGN Summary

**Joint SIGN routing shape (per feedback_claude_rigby_agree_first_chris_yes_no):** Claude drafted the design routing 3 F-BLOCKING + 1 NON-BLOCKING + open-ended zoom-out. Rigby DISAGREED on Q1 (major substrate-simplicity fold), AGREED with fold on Q2, MOSTLY AGREED with fold on Q3, AGREED on Q4, and produced a rich zoom-out with 3 same-PR responses + 1 future-trigger. Claude synthesized joint recommendation. Chris D-verdict yes with explicit alignment on Rigby's swiss-army-knife pushback.

### F-BLOCKING folds (Rigby)

- **Q1 hook location — DISAGREED with Claude lean.** Claude proposed extending `session_lifecycle status --wrapper-check`; Rigby responded: "single-concern preservation. `session_lifecycle` is already trending toward Swiss Army knife (pin + wrapper + freshness in S2775). Ownership verification is a different axis — identity/auth vs runtime/code health. Create dedicated `verify_pa_wrapper_ownership` management command." **Adopted.** Chris aligned: "agree with Rigby on trying to prevent swiss army knife effects." Refactor trigger codified in the command docstring.
- **Q2 whoami mechanism — AGREED with fold.** Dedicated `/api/pa/whoami/` view + sharp 5-point test in docstring to prevent `/api/pa/*` becoming a second ops-surface. Adopted verbatim as module docstring.
- **Q3 cache strategy — MOSTLY AGREED with fold.** Per-pin file cache. Rigby added: also record `verified_user_id` in file contents so a future v2 prelude can compare without hitting the API. Adopted.

### Non-blocking fold (Rigby preference aligned with Claude lean)

- **Q4 freshness log integration — AGREED silent v1.** If future v2 adds a log, prefer sibling `logs/wrapper_ownership.jsonl` over extending `session_freshness.jsonl` (orthogonal substrates: code identity vs auth identity).

### Q4 zoom-out (S2771 rule SIXTH consecutive application — richest classification breakdown to date)

Rigby zoom-out surfaced 4 substantive concerns with **explicit classification per concern** using the emerging pattern (S2774 established `same-PR-actionable`; S2775 established `same-PR-mitigatable`; classification pattern itself now has two triggers of two classes and one of a third — codification candidate):

1. **Substrate accretion in `session_lifecycle` → `same-PR-actionable`.** Split into dedicated command as above; refactor trigger codified.
2. **Python entrypoint alternative → `future-trigger`.** Keep guardrail at outermost choke point for v1.
3. **Blast radius of fail-loud exit 2 → `same-PR-mitigatable`.** Escape hatch env var `PA_LOCAL_ALLOW_MISMATCH=1` — warn-and-continue for emergencies without defeating default recovery-time objective.
4. **`/api/pa/*` surface-bleed → `same-PR-mitigatable`.** Sharp 5-point test codified in `views_pa_whoami.py` module docstring.

### Chris D-verdict

Yes on joint recommendation with explicit alignment on Rigby's substrate-simplicity concern: "Yes on the shape. I also agree with Rigby on trying to prevent swiss army knife effects."

**Meta:** S2771 rule SIXTH consecutive application. Rigby's DISAGREE on Q1 is the FIRST F-BLOCKING disagreement of the S2771-rule streak — validates that the rule genuinely surfaces substantive folds vs devolving into all-PASS ratification. Emerging classification pattern hit third session, all three response categories represented in one session for the first time.

---

## §5. Empirical evidence

**N21 unit suite:**

```
$ python manage.py test core.tests.test_pa_wrapper_ownership_2776 --noinput
Ran 9 tests in 0.380s
OK
```

**Full 4-suite regression stack (S2772 + S2773 + S2775 + S2776):**

```
$ python manage.py test core.tests.test_ops_auth_regression_2772 \
    core.tests.test_ops_query_param_allowlist_2773 \
    core.tests.test_session_freshness_2775 \
    core.tests.test_pa_wrapper_ownership_2776 --noinput
Ran 56 tests in 1.190s
OK
```

**Live E2E (cold cache → verify → cache written):**

```
$ rm -rf ~/.claude-pa-verified
$ bash tools/pa_local.sh "N21 live E2E check — say ok"
[pa_local] ✓ token=chris · pin=pa-bc40ba1f5dd343f4 · pin_owner=chris
ok
$ ls ~/.claude-pa-verified/
pa-bc40ba1f5dd343f4.json
$ cat ~/.claude-pa-verified/pa-bc40ba1f5dd343f4.json
{"pin": "pa-bc40ba1f5dd343f4",
 "verified_user_id": "e0c9d44b-a876-4b30-b0da-e4d0b10006f6",
 "verified_username": "chris",
 "verified_at": "2026-07-13T23:11:39.103966+00:00"}
```

**Live E2E (warm cache → silent skip):**

```
$ bash tools/pa_local.sh "second call — cache hit test"
# no [pa_local] line — silent skip; Rigby dispatched normally
```

**Rigby capstone (7-endpoint suite):**

```
{"ok": true, "suite": "custom", "passed": 7, "failed": 0, "total": 7}
```

- `ops_slo_status` HTTP 200 · 90ms
- `ops_failure_signatures` HTTP 200 · 22ms
- `ops_blocked_agents` HTTP 200 · 14ms
- `ops_health_summary` HTTP 200 · (…)ms
- Plus `close_ceremony_ledger`, `recent_recycles`, and `/api/pa/whoami/` all HTTP 200

`ops_tool.version` returns `staleness_verdict=FRESH · head_commit_sha=aa3dccc509b66d7e7b73be452e70d294bddb591c · daphne_pid_age_seconds=183 · celery_workers_status=5 fresh` — post-N21-recycle state.

---

## §6. Post-ratification bindings

- **First natural N21 verification** already fired this session at S2776 open (see §5 live E2E). Cache file lives on and skips subsequent invocations until pin rotates.
- **Cache dir `~/.claude-pa-verified/`** is user-scoped, not repo-scoped. Not gitignored (nothing to gitignore — outside the repo).
- **`tools/pa_local.sh`** wrapper now includes the prelude; will retire the S2776 pin at close per S2770+ pattern (SEVENTH consecutive `force=true` retirement).
- **CLAUDE.md L3 anchor** — refreshed to reference S2776 N21 landing.
- **N15 freshness log `logs/session_freshness.jsonl`** — S2776 open produced its first natural row (mechanism-now/value-later first payoff). Trend surface now has 2 rows (1 shell-invoke test at S2775 + 1 natural at S2776).

---

## §7. Forward carry

**Rigby S2774 forward-carries (state at S2776 close):**

- **Pause ops-surface PRs** discipline — **still held**. N21 is non-ops-surface; extended the streak. Ops-surface unblock triggers unchanged.
- **30+ other lambda-`__import__` sites in `core/urls.py`** — still forward-carrying; no trigger.
- **Rigby S2773 forward-carry #5 (health_summary vs ops_tool.overview overlap)** — still forward-carrying; no divergence observed.

**Rigby S2775 forward-carries (state at S2776 close):**

- **N15 v2 candidates** (close-time freshness capture, PA-tool read action, UI tile) — still deferred pending row accumulation + user-visible ask. N21 did NOT touch N15 substrate.
- **First `same-PR-mitigatable` case validation** — S2776 delivered TWO more `same-PR-mitigatable` cases (concerns c and d). Classification pattern now has three triggers of one class and two of another — approaching codification threshold under PLAYBOOK-6.10.

**Rigby S2776 zoom-out surfaces (new):**

- **N21 v2 candidates:** wrapper-side user_id compare against cache (0-API-cost invalidation); TTL on cache; sibling `logs/wrapper_ownership.jsonl` trend log. All gated on trigger.
- **Refactor trigger for `session_lifecycle`:** if a THIRD flag hits the API or reads/writes wrapper cache, split into `session_lifecycle` (pin+wrapper) + `toolchain_doctor` (freshness+ownership+other). Codified in command docstring.
- **`/api/pa/*` future-endpoint audit trigger:** every proposal must satisfy the sharp 5-point test or route via stricter ops-surface pause rubric.
- **Codification of the zoom-out classification pattern.** S2776 lands the third session in a row where the classification is explicit and productive. Two-triggers threshold per PLAYBOOK-6.10 satisfied for `same-PR-actionable` and `same-PR-mitigatable` classes independently. Candidate for Playbook v0.7.0 MINOR amendment (new rule) or v0.6.1 PATCH (informative-only classification note). Queued for memory-rule promotion audit.

---

## §8. Meta-observation on the SIGN discipline

**S2771 rule — SIXTH consecutive application.** Streak now:

| Session | Arc | Zoom-out folds surfaced | Same-PR-actionable | Same-PR-mitigatable | Future-trigger | F-BLOCKING disagreements |
|---|---|---|---|---|---|---|
| S2771 | CCL v2 text search | 3 concerns | 0 | 2 | 1 | 0 |
| S2772 | auth-regression + staff gate | 7 concerns | 0 | 2 | 4* | 0 |
| S2773 | param-allowlist + refactor + date fix | 5 concerns | 0 | 3 | 2 | 0 |
| S2774 | URLConf lambda cleanup | 4 concerns | 4 (capstone precedent) | 0 | 0 | 0 |
| S2775 | freshness verdicts JSONL | 4 concerns | 0 | 4 (mitigation precedent) | 0 | 0 |
| **S2776** | **PA wrapper ownership** | **4 concerns** | **1** | **2** | **1** | **1 (Q1)** |

*S2772 forward-carries had explicit trigger criteria rather than the strict `future-trigger` classification that emerged later.

**Novel S2776 signals:**
1. **First F-BLOCKING DISAGREE.** Rigby's Q1 pushback (dedicated command vs session_lifecycle extension) is the FIRST time in the S2771-rule streak Rigby has DISAGREED with Claude's F-BLOCKING lean. Chris explicitly aligned with the disagreement. This validates the rule genuinely surfaces substantive folds vs devolving into all-PASS — a live pressure test against the "SIGN drift to ritual" failure mode Chris flagged at S2771 close.
2. **First single-session with all three classification categories represented.** 1 `same-PR-actionable` + 2 `same-PR-mitigatable` + 1 `future-trigger`. Prior sessions concentrated in one or two categories.
3. **Classification pattern now has TWO independent triggers** for `same-PR-actionable` (S2774 novel + S2776 concern a) AND `same-PR-mitigatable` (S2775 all-4-mitigation + S2776 concerns c and d) AND one for `future-trigger` (S2776 concern b, though S2772/S2773 forward-carries prefigure it). Two-triggers threshold under PLAYBOOK-6.10 satisfied for the first two classes.

**Substrate composition observation:** N21 lands cleanly on top of the existing `ChatConversation.user_id` model + `PA_API_TOKEN` env pattern + `tools/pa_local.sh` wrapper. Zero new tables. Zero new models. Zero new PA tool actions. One new view (bounded read-only), one new command, one bash prelude, one cache file. Substrate maturity signal: N21 was possible in one session because every layer it composes onto is stable + tested + well-understood. Same failure mode two years ago would have required infrastructure work.

**Prior N21 blocker:** S2774 travel-recovery memory rule `feedback_post_travel_port_collision_triage` explicitly named N21 as a "would have caught this in seconds" candidate. Two sessions later, it shipped. Memory-rule-to-code-ship latency: 1 calendar day, 2 sessions.
