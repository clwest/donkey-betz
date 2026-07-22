# Session 2890 — Playbook v0.9.0 ratified + ops_tool.recent_bridge_calls shipped + parent-workspace multi-Claude coordination rules

**Date:** 2026-07-22
**Session pin (retired at close):** `pa-b2fbe7ffd4364dce` (labeled `s2890-open`; minted at S2889 close)
**Prior pin retired at S2889 close (not this session):** `pa-bf73f55995144814`
**Slate label:** S2890 — Playbook v0.9.0 amendment cycle (shipped PR #3402) + character-os bridge call observability (shipped PR #3404) + parent-workspace coordination docs
**PRs shipped (this session):**
- u-d-b PR #3402 `147dcc9cc` — Playbook v0.9.0 (PLAYBOOK-3.2.3 + PLAYBOOK-3.2.4)
- u-d-b PR #3403 `aeda6ec6a` — S2889 close cascade (handoff + 00-START refresh + wrapper pin)
- u-d-b PR #3404 `d2f72c428` — S2890 ops_tool.recent_bridge_calls
- u-d-b PR `<this close cascade>` — S2890 close cascade

---

## What Chris asked for at session open

`Please begin.` → clarified scope to Step 1 only (Playbook v0.9.0 amendment cycle) with the character-os multi-Claude concurrency verification as a Step 2 prerequisite. After v0.9.0 shipped, Chris pivoted:

> "I would like to do is start working on the UI and have you and Rigby continue working on Donkey Betz now that we have a plan lol."

That drove the entire second half of the session.

---

## Shipped (in order)

### 1. Playbook v0.9.0 MINOR amendment — PR #3402 (`147dcc9cc`) + tag `playbook-v0.9.0`

Two new [GR] rules under Chapter 3 §3.2 codifying handler-test-authoring discipline observed in-wild across S2879 → S2886 error-envelope migration slates:

- **PLAYBOOK-3.2.3** — handler regression tests exercising a code path that materializes a separate Django DB connection (e.g. `ToolDispatcher.execute_sync`'s fresh asyncio event loop) MUST inherit `TransactionTestCase` when the handler reads ORM state from `setUp` fixtures. Rule scopes to the transaction-visibility invariant, not the event-loop mechanism.
- **PLAYBOOK-3.2.4** — when a handler has two or more return branches emitting the same taxonomy `error_code`, migrated-envelope tests MUST additionally assert `action` field OR a distinguishing substring in the error body. Prevents branch-crossing false-pass.

Rule count 205 → **207**. First Chapter 3 extension since v0.2.0 (8-version gap). Chapter 3 remains STUB.

Ledger 148 → 152 rows (4 backfilled S2885/S2886 corpus) + 2 live S2889 SIGN folds (rows 153-154) via PLAYBOOK-6.10.8 graceful-degradation clause. First MINOR amendment where retroactive ledger backfill preceded T1 SIGN routing.

**Rigby SIGN provenance (T1 + T2 + T3):**
- T1 dispatch: 5 tool-grounded items + zoom-out ask. 10 tool_runs total (repo_tool.read_file × 8 + search × 1 + typo). Anti-rubber-stamp gate PASS.
- T2 attestation: all AGREE. Non-blocking: (a) `--concern` help says "one sentence"; (b) 3.2.3 rationale should name invariant not mechanism. Sub-verdict: KEEP TWO SEPARATE RULES.
- T3 verification: light-touch AGREE. Two trivial clarity nits applied.
- Fold A `same_pr_mitigatable` (row 153): invariant framing → mitigated at §2.1.
- Fold B `future_trigger` (row 154): Testing Discipline chapter candidacy → recorded as §3.5 extension-point note.

Chris D-verdict at S2889: **"yes ship it"** (single-yes following joint Claude+Rigby AGREE).

Workspace deliverables (Rigby-authored):
- Ratification envelope `6f8767c7-0ad4-4d3c-ad1d-c57ecb5144a4` (governance, clean).
- Content mirror `9a9ba3dc-2dc4-423d-acc6-2ccb104ec780` (engineering, diagnostic flags cleared per known Rigby tool gap).

Full context: `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`.

### 2. Parent-workspace multi-Claude coordination docs

At Chris's directive after S2889 close pivot to character-os UI exploration, two docs authored at `/Users/donkeyking/Donkey_Betz/docs/` (parent workspace, not a git repo — jointly readable by both Claudes):

- **`2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md`** — living reference mapping character-os UI surfaces to u-d-b endpoint touchpoints. 34 SPA routes enumerated; 9 realtime tools categorized (3 bridge / 6 local); port map + quick tells + refresh triggers.
- **`MULTI_CLAUDE_COORDINATION.md`** — 11-section rulebook for running u-d-b Claude + character-os Claude concurrently. Sections: governing principles, repo ownership boundaries, Rigby routing (pin isolation), session lifecycle non-overlap, git ops safety, port collision watchlist (S2885/S2886 patterns baked in), shared PA endpoint, parent-workspace docs conventions, escalation triggers, don't-do list, cross-Claude handoff.

Both files address the concurrency-safety concern Chris raised at S2889 open ("before we start anything with Character-OS we make sure that running you and Rigby in one repo and a second Claude in the character-os repo can be done without causing any issues").

### 3. ops_tool.recent_bridge_calls — PR #3404 (`d2f72c428`)

New observability action for the operator surface (Rigby side). Answers **"what bridge calls hit u-d-b in the last N minutes?"** — useful while Chris explores character-os SPA to verify which UI actions actually round-trip through u-d-b.

**Detection surface:** `source__startswith='character-os-'` on `ChatConversation`. Character-os bridge tools POST with source values `character-os-consult-engine` / `character-os-query-spider-data` / `character-os-agent-consult`; `core/tasks_misc.py:4839` persists that verbatim. No new fields, no migration, no schema drift.

**Payload:** `limit` (default 20, max 100), `since` (ISO-8601) or `window` (`1h`/`6h`/`24h`/`7d`/`30d`), `bridge_tool_name` filter (underscore form; converted to wire-format hyphens), `workspace_id` filter.

**Return shape:** `total_count` + `by_tool` aggregate (source → underscore-form bridge_tool_name → count) + `items[]` with `tool_name`, `question` + `question_truncated`, `answer_preview` + `answer_truncated`, `latency_ms` (mapped from `response_time_ms`), `workspace_id`, `user`, `agents_used`, `created_at`. Diagnostic `note` on empty referencing ledger row 155.

**Scoping:** non-staff callers see own bridge rows only; staff see all. No-user or unknown-user returns empty.

**Rigby T1 SIGN provenance:**
- Item 1 AGREE (detection surface): 8 repo_tool.read_file verifications.
- Item 2 AGREE (slot fit): ops_tool natural home.
- Item 3 AGREE with same-PR mitigations: truncation flags + latency_ms remap + diagnostic note applied.
- Item 4 AGREE (scoping): non-staff user scoping + optional workspace_id.
- Item 5 zoom-out Fold A (`future_trigger`, ledger row 155): source-string sniffing rename risk. Future MINOR/PATCH mitigation: character-os adds explicit stable `bridge_tool` marker.

**PLAYBOOK dogfood:** PLAYBOOK-3.2.3 (ratified same session earlier) exercised in the test suite — first dogfood of the just-ratified rule.

**Regression:** 13/13 tests pass. Live post-merge Rigby verify: returned both existing character-os-consult-engine rows with underscore-form `tool_name`, truncation flags, and latency correctly.

Ledger grew 154 → **155 rows** (1 live S2890 SIGN fold).

---

## Rigby SIGN provenance across the session (all tool-grounded)

- **S2889 T1/T2/T3 (v0.9.0):** 15 total tool_runs across three turns. All AGREE with two non-blocking mitigations resolved same-envelope.
- **S2890 T1 (recent_bridge_calls):** 8 tool_runs verifying detection surface + slot + rule text. All items AGREE, zoom-out Fold A `future_trigger` for rename risk.

Zero rubber-stamp SIGN cycles detected; per-question tool_runs verified throughout.

---

## Ledger growth summary

Ledger grew 148 → **155 rows** during S2890:

| Row | Session | Classification | Backfilled | Arc |
|---|---|---|---|---|
| 149 | S2885 | `same_pr_mitigatable` | true | `s2885_transaction_testcase_dispatcher_db` |
| 150 | S2886 | `same_pr_mitigatable` | true | `s2886_transaction_testcase_dispatcher_db` |
| 151 | S2885 | `same_pr_mitigatable` | true | `s2885_shared_taxonomy_branch_fortification` |
| 152 | S2886 | `same_pr_mitigatable` | true | `s2886_shared_taxonomy_branch_fortification` |
| 153 | S2889 | `same_pr_mitigatable` | false | `v0_9_0_invariant_framing` (Fold A) |
| 154 | S2889 | `future_trigger` | false | `v0_9_0_testing_discipline_chapter` (Fold B) |
| 155 | S2890 | `future_trigger` | false | `v0_9_1_bridge_call_observability` (Fold A) |

---

## Deferred / carried forward from S2890

Everything below survives into S2891's queue:

1. **Character-os UI exploration continues.** Chris drives character-os SPA in a second terminal (character-os Claude). u-d-b Claude stands by; ping when a surface identification is needed. Reference sheet lives at `/Donkey_Betz/docs/2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md`.
2. **Multi-Claude coordination rulebook active.** `/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md` is the durable envelope for cross-Claude discipline.
3. **Original Step 2 EB.4/C3 scripted dogfood** — deferred until Chris re-scripts (pivot to exploration mode continues).
4. **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Watch for 2 more test-authoring rules in §3.2 OR one SIGN blocked by ambiguous test-authoring slot.
5. **Bridge call observability rename-risk future_trigger** — ledger row 155. Watch for character-os renaming source markers OR SDK/API-doc stage.
6. **R1 fleet reject-mode flip** — DEFERRED. Fleet HMAC path dormant per S2887 telemetry.
7. **Original C4 PD-1 timeout coordination defect** (character-os side, Sev-1).
8. **C5 non-realtime bridge invocation + C6 tool catalog** — character-os side follow-ons.
9. **LLMCallLog `requested_model_id` field split + `was_policy_reroute` field** — migrations required. Deferred.
10. **Bulk `workspace_budget_tool` operations** (S2847 ledger candidate). Deferred.
11. **Docs restructuring arc** (`project_docs_restructuring_arc_queued`). Deferred behind wedge execution.
12. **Rigby Tool Gap Ledger review** — 1 new entry accreted at S2888 (`fleet_health` mis-routing, low priority). Ledger review as candidate slate whenever Chris returns to net-new engineering slate mode.

---

## Cross-repo docs cascade at this close

**Repo canonical (Claude-authored, this file):**
- u-d-b: `docs/handoffs/SESSION_2890_OPS_TOOL_RECENT_BRIDGE_CALLS.md` — this handoff.
- u-d-b: `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md` — shipped separately at S2889 close cascade PR #3403.
- u-d-b: `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md` — shipped at PR #3402.
- u-d-b: `00-START-NEXT-SESSION.md` refresh for S2891.
- u-d-b: `tools/pa_local.sh` wrapper pin bump `pa-b2fbe7ffd4364dce` → S2891 mint.
- u-d-b: `docs/INDEX.md` auto-refresh.

**Parent workspace canonical (Claude-authored):**
- `/Donkey_Betz/docs/2026-07-22_CHARACTER_OS_UI_TO_UDB_REFERENCE_SHEET.md` — reference sheet.
- `/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md` — 11-section rulebook.

**Workspace canonical (Rigby-authored, S2889 v0.9.0):**
- Ratification envelope `6f8767c7-0ad4-4d3c-ad1d-c57ecb5144a4`.
- Content mirror `9a9ba3dc-2dc4-423d-acc6-2ccb104ec780`.

**Note on this session's shipped code:** S2890 shipped the `ops_tool.recent_bridge_calls` action but no separate workspace ratification envelope is required — this is engineering, not a methodology change. Rigby SIGN provenance lives in this handoff §3 + the commit body of PR #3404.

---

## PLAYBOOK-7.4.4 recycle waiver (this close cascade PR only)

The v0.9.0 amendment PR (#3402) and the recent_bridge_calls PR (#3404) both had post-merge `make recycle-all` runs. The 3404 recycle rebooted Daphne + all Celery workers at SHA `d2f72c428`; live Rigby dispatch of `ops_tool.recent_bridge_calls` verified the new action reached the workers.

This close-cascade PR itself is **docs-only** (`docs/handoffs/`, `00-START-NEXT-SESSION.md`, `tools/pa_local.sh`, `docs/INDEX.md`). No `*.py`, no deps, no settings, no migrations, no worker config. PLAYBOOK-7.4.4 recycle waiver applies.

---

## S2890 close — what shipped

**Repo canonical (Claude-authored):**
- **PR #3402** `147dcc9cc` — Playbook v0.9.0 (2 new [GR] rules, rule count 205 → 207).
- **PR #3403** `aeda6ec6a` — S2889 close cascade.
- **PR #3404** `d2f72c428` — S2890 ops_tool.recent_bridge_calls (~586 lines).
- **PR `<this close cascade>`** — S2890 close cascade.
- Tag `playbook-v0.9.0` pushed.

**Parent workspace canonical (Claude-authored):**
- 2 living rulebooks + 1 reference sheet.

**Workspace canonical (Rigby-authored, S2889):**
- 2 deliverables for v0.9.0 mirror.

**Runtime impact:**
- Rule count 205 → **207**. Chapter 3 §3.2 grows from 2 to 4 rules.
- Ledger 148 → **155 rows** (+4 backfilled + 3 live).
- ops_tool now has 21 actions (was 20); new `recent_bridge_calls` observability surface.
- Rigby can answer "what bridge calls hit u-d-b in the last N minutes?" as a first-class dispatch.
- Chris + parallel character-os Claude have a durable coordination rulebook.
- Fourth consecutive MINOR shipped in single-session shape (v0.6.0/S2766 → v0.7.0/S2778 → v0.8.0/S2786 → v0.9.0/S2889).

**Governance debt disposition:**
- No CDs discharged this session.
- No CDs opened.
- Testing Discipline chapter candidacy (row 154) + bridge observability rename-risk (row 155) held as `future_trigger`, not CDs.
