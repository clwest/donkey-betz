---
title: "Rigby SIGN Zoom-Out Classification Ledger Ratification Record (2026-07-13)"
status: active
authority: ratification-record
session_added: 2777
ratification_date: 2026-07-13
ratifier: chris
routing: rigby-pa-chat joint SIGN (single design + zoom-out per S2771 rule SEVENTH consecutive application) + Chris D-verdict yes on joint recommendation. Novel this session: Rigby's Q1-Q4 first pass was rubber-stamp text-only (0 tool_runs); Chris flagged; re-routed with explicit tool-grounded verification directives; Rigby's second pass produced substantive DISAGREE on Claude's PLAYBOOK-6.10 rationale + 2 clean FOLDs; third pass (fold-close) surfaced 1 new same-PR-mitigatable concern (schema ossification). SECOND F-BLOCKING DISAGREE of the S2771-rule streak (first at S2776 Q1).
scope: S2777 — N22 (Rigby SIGN zoom-out concern persistence helper). NEW `core/management/commands/record_zoom_out_concern.py` (147-line JSONL writer with 7-field enum-validated schema). NEW `core/management/commands/zoom_out_streak_report.py` (128-line CLI reader with advisory-only report language). NEW `logs/zoom_out_classifications.jsonl` (13-row seed: 12 backfilled from S2774+S2775+S2776 + 1 live S2777). NEW `core/tests/test_zoom_out_classifications_2777.py` (10-test suite covering both commands). Rationale explicitly REFRAMED per Rigby DISAGREE: N22 is evidence substrate for a *future* rule, not accelerator for an already-codified §6.10 threshold.
serves_arc: substrate hardening — surfaces the emerging zoom-out classification pattern (`same-PR-actionable` / `same-PR-mitigatable` / `future-trigger`) as an observable longitudinal ledger. Two-triggers convention (present as informative note language + methodology record, NOT as a codified §6.10 rule) can now be evaluated on evidence rather than session-to-session narrative. N23 (Playbook amendment codifying the classification) becomes a separately-ratifiable follow-on gated on its own D-verdict.
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-13_pa_wrapper_ownership_check.md (S2776 — FIRST F-BLOCKING DISAGREE in S2771-rule streak; three-triggers threshold on classification pattern first surfaced)
  - docs/research/implementation/RATIFICATION_2026-07-13_session_freshness_verdicts_jsonl.md (S2775 — JSONL substrate precedent; introduced `same-PR-mitigatable` classification)
  - docs/research/implementation/RATIFICATION_2026-07-13_ops_urlconf_lambda_cleanup.md (S2774 — introduced `same-PR-actionable` classification via capstone precedent)
  - docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0.md (S2766 — PLAYBOOK-7.4.4 codification; ancestor for close-cycle discipline)
ratified_documents:
  - core/management/commands/record_zoom_out_concern.py (NEW — 147 lines; JSONL writer with 7-field schema + enum validation)
  - core/management/commands/zoom_out_streak_report.py (NEW — 128 lines; CLI reader with advisory-only language)
  - logs/zoom_out_classifications.jsonl (NEW — 13 seed rows; 12 backfilled + 1 live)
  - core/tests/test_zoom_out_classifications_2777.py (NEW — 10 tests covering both commands + `--log-path` override for isolation)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2777 open freshness (S2776-close-pin dispatch to Rigby, post-recycle) — second natural N15 freshness hook fire at pin mint: verdict FRESH · SHA `eaccf3acfb02` matches HEAD. `logs/session_freshness.jsonl` now has 3 rows (1 shell test at S2775 + 2 natural at S2776 and S2777).
  - S2777 joint SIGN turn 1 (Rigby, pin pa-f19df7828f2843e5) — RUBBER STAMP EVENT. Rigby returned AGREE x4 with pushback text but ZERO tool_runs; intent routed to `general`. Chris flagged: "make sure Rigby is not just rubber stamping what you suggest, and that she's using tools when needed and not just guess."
  - S2777 joint SIGN turn 2 (same pin, tool-grounded re-route with 5 explicit search_docs directives) — Rigby executed 6+ search_docs calls; produced SUBSTANTIVE DISAGREE on Claude's "PLAYBOOK-6.10 two-triggers threshold" rationale (surfaced §6.10 has rules 6.10.1-6.10.6 for provenance verification; two-triggers convention appears as informative note language + methodology record, NOT as a codified normative rule); FOLD on S2776 a/b/c/d mapping (RAG missed envelope frontmatter); FOLD on session_lifecycle flag count (docs corpus lacked argparse listing). Claude verified independently via file reads — Rigby's DISAGREE is correct.
  - S2777 joint SIGN turn 3 (same pin, folds closed with verbatim ground-truth + framing correction) — Rigby re-rendered clean AGREE Q1-Q4 with citations; reiterated DISAGREE on original PLAYBOOK-6.10 framing (would have shipped an incorrect claim); direct zoom-out answer: "risk goes DOWN under corrected framing, tail-wagging-dog becomes salient"; ONE new same-PR-mitigatable concern surfaced (schema ossification → mitigated via schema_version + additive-only fields + advisory language).
  - Chris D-verdict yes at turn 3 synthesis ("yes ship it").
frozen: true
---

# Rigby SIGN Zoom-Out Classification Ledger — Ratification Record

Frozen canonical record of Chris's ratification of the S2777 N22 zoom-out classification persistence helper on 2026-07-13. Third consecutive non-ops-surface arc (S2775 → S2776 → S2777). Novel this session: FIRST rubber-stamp SIGN event detected mid-arc + successfully corrected via tool-grounded re-route. Append-only.

---

## §1. Context

Zoom-out classification (`same-PR-actionable` / `same-PR-mitigatable` / `future-trigger`) is a pattern that emerged organically across S2774-S2776:

- **S2774** established `same-PR-actionable` when Chris D-verdicted a Rigby zoom-out concern (capstone verification) into the same PR as the primary change rather than deferring it as a forward-carry.
- **S2775** established `same-PR-mitigatable` when all 4 Rigby zoom-out concerns became design-time mitigations folded into implementation (helper stays private, commit message language, atomic append) rather than same-PR verification actions.
- **S2776** was the first session with all three classifications represented in one zoom-out breakdown (1 actionable + 2 mitigatable + 1 future-trigger).

As of S2777 open, the pattern is documented in three ratification envelopes' §4 SIGN Summary sections + a summary table in the S2776 envelope §8. But it lives only in narrative — no way to compute streak length per classification, no way to catalog concerns for retrospective review, no way to distinguish "we've seen this pattern twice" from "we've seen this once and forgotten."

N22 makes the pattern **observable and longitudinal** by persisting each concern to an append-only JSONL ledger with a minimally committal schema.

**Framing correction (from Rigby S2777 turn 2 DISAGREE):** Original N22 rationale was "accelerates two-triggers threshold detection per PLAYBOOK-6.10." Rigby's tool-grounded verification found §6.10 has provenance-verification rules (6.10.1–6.10.6) but no "when triggers=N you MUST codify" normative rule. The two-triggers convention shows up as informative note language + methodology record in ratification envelopes. Chris ratified the corrected framing: **N22 is evidence substrate for a rule that does not exist yet.** If N23 (a proposed Playbook amendment codifying the classification) is ever pursued, it becomes a separately-ratifiable follow-on requiring its own SIGN + D-verdict.

---

## §2. Ratified Change

Two production files + one test file + one seed data file (~430 net-new lines):

### (a) NEW `core/management/commands/record_zoom_out_concern.py` (147 lines)

Write path. Single-concern command per S2776 substrate-simplicity precedent. Does NOT accrete into `session_lifecycle` — pin+wrapper+freshness stay one command; zoom-out ledger stays another. Every write is one row.

**7-field schema (v1, locked at ratification):**

| Field             | Type              | Required | Notes |
|-------------------|-------------------|----------|-------|
| `ts`              | ISO 8601 datetime | auto     | UTC timestamp at write |
| `schema_version`  | int               | auto     | Starts at 1; future evolution via additive fields + alias mapping |
| `session`         | int               | yes      | Originating session number (e.g., 2774) |
| `arc`             | slug string       | yes      | Short arc label (e.g., `ops_urlconf_lambda_cleanup`) |
| `classification`  | enum              | yes      | One of {`same_pr_actionable`, `same_pr_mitigatable`, `future_trigger`} — argparse-validated |
| `concern_text`    | string            | yes      | One-sentence concern description |
| `evidence_ref`    | string or null    | no       | Optional pointer (PR#, envelope §, handoff path) |
| `backfilled`      | bool              | no       | Flags historical reconstruction vs live capture |
| `entered_by`      | string            | no       | Defaults to `$USER` |

Enum + non-empty validation rejects malformed writes before any bytes hit the log.

### (b) NEW `core/management/commands/zoom_out_streak_report.py` (128 lines)

Read path. CLI-only per Rigby Q4 AGREE + Chris D-verdict. PA-tool read action explicitly deferred as future-trigger (S2777 forward-carry) — unblocks when Chris explicitly wants streak counts inside a Rigby SIGN review loop.

**Advisory header (verbatim in both text + JSON output):**

> "Rigby SIGN zoom-out concern ledger — pattern evidence for review. Rows are longitudinal signal, not automatic escalation triggers. Any Playbook codification decision requires its own ratification."

Filters: `--last N`, `--classification <enum>`, `--session <n>`. `--as-json` emits full payload for downstream tooling (still advisory, still evidence).

### (c) NEW `logs/zoom_out_classifications.jsonl` (13 seed rows)

12 backfilled rows (`backfilled=true`, `entered_by=claude`) reconstructing S2774+S2775+S2776 zoom-out concerns from `RATIFICATION_2026-07-13_*.md` §4 SIGN Summary + envelope frontmatter:

- **S2774** (4 rows, all `same_pr_actionable`): PR churn without capstone · not over-hardening ops · adjacent risk = URLConf fragility · review fatigue after 5-PR streak.
- **S2775** (4 rows, all `same_pr_mitigatable`): session_lifecycle charter dilution · misread risk on first STALE row · alternative substrates rejected · atomicity + hook order.
- **S2776** (4 rows, 1+2+1): substrate accretion → actionable · Python entrypoint → future-trigger · fail-loud escape hatch → mitigatable · /api/pa/* surface-bleed → mitigatable.

1 live row (`backfilled=false`, S2777): schema ossification risk from Rigby S2777 turn 3 zoom-out.

Immediate streak state (per `zoom_out_streak_report`): **13 total rows · 5 same_pr_actionable · 7 same_pr_mitigatable · 1 future_trigger.**

### (d) NEW `core/tests/test_zoom_out_classifications_2777.py` (10 tests)

`RecordZoomOutConcernTests` (6): valid write appends 7-field row · invalid classification raises · empty concern raises · empty arc raises · evidence_ref optional (defaults None) · backfilled flag marks row.

`ZoomOutStreakReportTests` (4): empty ledger reports zero + advisory header · counts by classification correct across mixed rows · `--classification` filter narrows · `--session` filter narrows.

All tests use `--log-path` override + `TemporaryDirectory` isolation. 10/10 PASS in 0.008s.

---

## §3. What Was NOT Changed

**Explicitly out of scope for N22 v1 (per Rigby folds + Chris alignment):**

- **Django model for storage.** Would raise tail-wagging-dog risk by making the ontology feel official earlier + adds migration cost. Future-trigger: promote when cross-table joins or multi-writer concurrency become load-bearing.
- **Auto-hook into ratification envelope creation.** Auto-hooking creates coupling to §4 SIGN Summary formatting variability + encourages "if it's logged it's binding" reflex. Future-trigger.
- **PA tool read action for streak report.** Kept CLI-only. Future-trigger: unblocks when Chris asks for streak counts inside a live SIGN loop.
- **N23 Playbook amendment.** Ledger surfaces evidence; N23 codification is a separately-ratifiable decision requiring its own SIGN + D-verdict per S2777 framing correction.
- **Threshold semantics baked into storage.** No "two triggers → fire" logic in the write or read paths. Streak counts are computed at read time; interpretation is human.
- **`session_lifecycle` extension.** Extends S2776 substrate-simplicity discipline: N22 lives standalone; refactor trigger for `session_lifecycle` (still 4 subcommands: status/open/history/close) unchanged.

---

## §4. Rigby SIGN Summary

**Joint SIGN routing shape (per feedback_claude_rigby_agree_first_chris_yes_no):** Claude drafted 4 F-BLOCKING + 1 NON-BLOCKING + open-ended zoom-out design questions. First SIGN turn produced rubber stamp. Second SIGN turn (post-Chris-flag) with explicit tool-grounded verification directives produced substantive corrections. Third SIGN turn (post-fold-close) produced clean synthesis. Chris D-verdict yes.

### Turn 1 — RUBBER STAMP (novel failure mode caught mid-arc)

Rigby returned AGREE x4 with generic pushback text + 4 zoom-out concerns classified. **`tool_runs: []`, `intent: general`.** No `search_docs` invocations. No citations to prior envelopes, playbook §s, or command source. Chris flagged before proceeding: "make sure Rigby is not just rubber stamping what you suggest, and that she's using tools when needed and not just guess."

**Novel signal:** first mid-arc catch of a Rigby-produced SIGN as substantively hollow. Prior sessions relied on retrospective observation that outputs *looked* substantive. This session Chris pressure-tested at decision time. Recovery latency: 1 additional SIGN turn.

### Turn 2 — GROUNDED, one DISAGREE + two FOLDs

Re-routed with 5 explicit tool-use directives (targeted `search_docs` queries against S2774/S2775/S2776 envelopes + Playbook §6.10 + session_lifecycle source). Rigby executed 6+ `search_docs` calls with narrowing queries.

**Substantive DISAGREE (§6.10 framing):** Rigby found the Playbook has PLAYBOOK-6.10.6 (verify-before-build, normative MUST-rule) but no "two-triggers threshold" normative rule. The "two-trigger threshold met" phrasing appears in informative notes + ratification methodology records only. Cited [ENGINEERING_PLAYBOOK.md#89] + [#95] + [SESSION_2740#4]. Claude verified independently via direct file read — DISAGREE is correct. Original N22 rationale carried an incorrect claim.

**Two clean FOLDs:** (a) S2776 a/b/c/d zoom-out mapping — RAG chunking of envelope missed frontmatter §sign_sessions (authoritative source); (b) session_lifecycle current flag count — docs corpus lacked argparse listing.

### Turn 3 — Folds closed with verbatim ground-truth + framing correction

Claude closed both FOLDs with verbatim source (S2776 envelope frontmatter §sign_sessions for a/b/c/d + `python manage.py session_lifecycle --help` for the 4 subcommands: status/open/history/close). Framing corrected: N22 rationale rewritten to "evidence substrate for a future rule that does not exist yet."

**Rigby re-rendered:** clean AGREE Q1-Q4 with citations. Explicit reiteration of DISAGREE on original PLAYBOOK-6.10 framing (would have shipped incorrect claim). Direct zoom-out answer:

> "Risk goes DOWN without a codified §6.10-style two-trigger rule. Newly salient: tail-wagging-dog — the act of logging can *define* the conceptual model that N23 later feels obligated to adopt."

**New concern surfaced (turn 3):** `same-PR-mitigatable` — schema ossification risk (log categories become "the law"). Mitigation: `schema_version` field + additive-only field evolution + advisory report language. Adopted verbatim into implementation.

### Chris D-verdict

Yes on joint recommendation at turn 3 synthesis: "yes ship it."

**Meta signals for the streak:**

- **Second F-BLOCKING DISAGREE of the S2771-rule streak** (first was S2776 Q1). Different substrate — this DISAGREE was on *Claude's framing / claim*, not on Claude's design lean.
- **Rubber-stamp failure mode caught mid-arc** — first documented occurrence. Chris's pressure test + tool-grounded re-route = recovery mechanism. Codification candidate for future memory rule: at each Rigby SIGN, verify `tool_runs` non-empty before proceeding when substantive verification of prior claims was expected.
- **S2771 rule seventh consecutive application.** Zoom-out surfaced 1 same-PR-mitigatable concern this session (schema ossification) — leanest breakdown of the streak. Not drift into ritual — the S2777 arc genuinely required fewer material folds because the substrate is small + Rigby already surfaced the biggest issue (§6.10 framing) via the DISAGREE.

---

## §5. Empirical evidence

**N22 unit suite:**

```
$ python manage.py test core.tests.test_zoom_out_classifications_2777 --noinput
Ran 10 tests in 0.008s
OK
```

**Full 5-suite regression stack:**

```
$ python manage.py test core.tests.test_ops_auth_regression_2772 \
    core.tests.test_ops_query_param_allowlist_2773 \
    core.tests.test_session_freshness_2775 \
    core.tests.test_pa_wrapper_ownership_2776 \
    core.tests.test_zoom_out_classifications_2777 --noinput
Ran 66 tests in ~1.2s
OK
```

**Live backfill + streak report:**

```
$ wc -l logs/zoom_out_classifications.jsonl
      13 logs/zoom_out_classifications.jsonl

$ python manage.py zoom_out_streak_report --as-json
{
  "advisory": "Rigby SIGN zoom-out concern ledger — pattern evidence for review. …",
  "total_rows": 13,
  "counts_by_classification": {
    "same_pr_actionable": 5,
    "same_pr_mitigatable": 7,
    "future_trigger": 1
  },
  "rows": [ … 13 rows … ]
}
```

---

## §6. Post-ratification bindings

- **CLAUDE.md L3 anchor** — refreshed to reference S2777 N22.
- **N15 freshness log** — third row landed at S2777 pin mint (SHA `eaccf3acfb02`, FRESH). Streak now 3 rows.
- **N21 wrapper ownership** — first natural verification on the new S2777 pin fired cleanly at first bash invocation (`token=chris · pin=pa-f19df7828f2843e5 · pin_owner=chris`). Cache file `~/.claude-pa-verified/pa-f19df7828f2843e5.json` populated.
- **Zoom-out ledger** — `logs/zoom_out_classifications.jsonl` seeded to 13 rows. Grows +N per session where Rigby SIGN surfaces zoom-out concerns.
- **`tools/pa_local.sh`** — will retire S2777 pin at close per S2770+ pattern (EIGHTH consecutive `force=true` retirement).

---

## §7. Forward carry

**Rigby S2777 zoom-out surfaces (new):**

- **N22 v2 candidates:** Django model migration (join with PR/mission ids); PA-tool read surface for live SIGN queries; JSONL rotation or archival strategy once row count crosses ~500 entries. All gated on trigger — no calendar schedule.
- **N23 Playbook amendment candidate:** codify zoom-out classification pattern as Playbook v0.7.0 MINOR (new [GR] rule) or v0.6.1 PATCH (informative note in §11.3 template or §6.10 extension-point). N22 ledger provides evidence substrate; N23 authoring requires its own SIGN + D-verdict.
- **Rubber-stamp SIGN failure mode codification candidate:** add memory rule requiring `tool_runs` non-empty verification before proceeding when a SIGN request expected substantive verification of prior claims. Not yet codified — one trigger observed; wait for second trigger per PLAYBOOK amendment convention.

**Rigby S2774 forward-carries (state at S2777 close):**

- **Pause ops-surface PRs** discipline — **still held**. N22 is non-ops-surface; third consecutive non-ops-surface arc. Unblock triggers unchanged.
- **30+ other lambda-`__import__` sites in `core/urls.py`** — still forward-carrying; no trigger.
- **Rigby S2773 forward-carry #5 (health_summary vs ops_tool.overview overlap)** — still forward-carrying; no divergence observed.

**Rigby S2775 forward-carries (state at S2777 close):**

- **N15 v2 candidates** (close-time freshness capture, PA-tool read action, UI tile) — still deferred pending row accumulation + user-visible ask.

**Rigby S2776 forward-carries (state at S2777 close):**

- **N21 v2 candidates** (wrapper-side user_id compare, TTL on cache, sibling `logs/wrapper_ownership.jsonl`) — still deferred pending trigger.
- **`session_lifecycle` refactor trigger** — still armed. Current flag count: 4 subcommands. Trigger fires when a THIRD flag hits the API or wrapper cache.
- **`/api/pa/*` future-endpoint audit trigger** — every proposal must satisfy the sharp 5-point test.

---

## §8. Meta-observation on the SIGN discipline

**S2771 rule — SEVENTH consecutive application.** Streak table update:

| Session | Arc | Zoom-out folds | Same-PR-actionable | Same-PR-mitigatable | Future-trigger | F-BLOCKING disagreements |
|---|---|---|---|---|---|---|
| S2771 | CCL v2 text search | 3 concerns | 0 | 2 | 1 | 0 |
| S2772 | auth-regression + staff gate | 7 concerns | 0 | 2 | 4* | 0 |
| S2773 | param-allowlist + refactor | 5 concerns | 0 | 3 | 2 | 0 |
| S2774 | URLConf lambda cleanup | 4 concerns | 4 (capstone precedent) | 0 | 0 | 0 |
| S2775 | freshness verdicts JSONL | 4 concerns | 0 | 4 (mitigation precedent) | 0 | 0 |
| S2776 | PA wrapper ownership | 4 concerns | 1 | 2 | 1 | 1 (Q1) |
| **S2777** | **zoom-out ledger** | **1 concern** | **0** | **1** | **0** | **1 (framing/§6.10)** |

*S2772 forward-carries pre-date the strict `future-trigger` classification.

**Novel S2777 signals:**

1. **First mid-arc rubber-stamp catch.** Chris's pressure test caught a text-only SIGN with zero tool_runs before it shipped. Recovery mechanism (tool-grounded re-route with explicit search_docs directives) worked. Codification candidate for the anti-rubber-stamp workflow: at any Rigby SIGN expected to verify substrate claims, check `tool_runs` before proceeding.
2. **Second F-BLOCKING DISAGREE on a different axis.** S2776's DISAGREE was on Claude's design lean (extend session_lifecycle). S2777's DISAGREE was on Claude's *claim* (PLAYBOOK-6.10 semantics). Both would have shipped wrong artifacts without the DISAGREE.
3. **Substrate is recursive.** N22 catalogs the zoom-out classification pattern, which N22 itself contributes a row to (S2777 schema ossification concern). Ledger is self-hosting from row 1.

**Substrate composition observation:** N22 lands cleanly on top of the existing JSONL-ledger + management-command patterns established by S2775 (N15). Zero new tables, models, or PA tool actions. Two new commands + one JSONL file + one test file. Composition-over-extension continues the S2776 substrate-simplicity precedent.
