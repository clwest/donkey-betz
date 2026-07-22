# Session 2889 — Playbook v0.9.0 ratified (PLAYBOOK-3.2.3 + PLAYBOOK-3.2.4)

**Date:** 2026-07-22
**Session pin (retired at close):** `pa-bf73f55995144814` (labeled `s2889-open`; minted at S2888 close)
**Prior pin retired at S2888 close (not this session):** `pa-35b93928b15f4a9c`
**Slate label:** S2889 — Playbook v0.9.0 MINOR amendment (2 new [GR] rules under Chapter 3 §3.2)
**PRs:** #3402 (`147dcc9cc`) + close cascade at close

---

## S2889 open — Chris directive on scope

Chris directed a two-step framing at S2889 open:
1. First: verify safety of running two Claude terminals concurrently (u-d-b + character-os) before doing anything with character-os.
2. Second: **only Step 1** — Playbook v0.9.0 amendment cycle. Skip Step 2 (character-os EB.4/C3 dogfood) until concurrency is verified.

Claude proceeded through Step 1 as scoped. Chris's D-verdict at Step 1 close: **"yes ship it"** (2026-07-22, terminal single-yes).

---

## Shipped

### PR #3402 `147dcc9cc` — Playbook v0.9.0 MINOR amendment

**Files changed:** 2 files, +276/-16.

- **`docs/ENGINEERING_PLAYBOOK.md`** (+27/-16) — frontmatter version bump (0.8.0 → 0.9.0), rule count (205 → 207), Chapter 3 §3.2 body extended with 2 new [GR] rules + shared commentary block, §3.5 extension-point commentary updated with Testing Discipline chapter future-trigger note, Appendix D v0.9.0 row appended.
- **`docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`** (NEW, 249 lines) — ratification envelope: §1 Context + §2 Ratified scope + §3 Two-trigger corpus + §4 Rigby joint SIGN cycle (T1 + T2 + T3) + §5 Chris D-verdict + §6 CD disposition + §7 PLACEHOLDER post-ratification bindings + §8 What this amendment teaches.

### Rule text summary

- **PLAYBOOK-3.2.3** — When authoring a handler regression test whose exercised code path materializes a separate Django database connection that does not participate in the test's wrapping transaction (e.g. dispatch through `ToolDispatcher.execute_sync`'s fresh asyncio event loop), the test class MUST inherit from `django.test.TransactionTestCase` (not `django.test.TestCase`) whenever the dispatched handler reads ORM state that `setUp` creates. Rule scopes to the **transaction-visibility invariant**, not to any single dispatch mechanism, so it remains valid if `execute_sync`'s internals change.
- **PLAYBOOK-3.2.4** — When a handler under test has two or more return branches that emit the same taxonomy `error_code`, a migrated-envelope regression test asserting that `error_code` MUST additionally assert one of: (a) the `action` field, when branches emit distinct actions; OR (b) a distinguishing substring in the `error` message body, when branches share an action. Prevents branch-crossing false-pass.

Both rules EXTEND PLAYBOOK-3.2.2 (acceptance-tests-first). First Chapter 3 extension since v0.2.0 (8-version gap). Chapter 3 remains STUB.

---

## Rigby SIGN cycles (T1 + T2 + T3)

### T1 dispatch (author-side)

5 tool-grounded items dispatched via `bash tools/pa_local.sh` on pin `pa-bf73f55995144814`:
1. Trigger evidence verification (S2885 + S2886 handoff §Fold 1 + §Fold 2)
2. Slot verification (Chapter 3 vs §6.10 vs §7.4)
3. Ledger-backfill legitimacy (PLAYBOOK-6.10.8 graceful-degradation)
4. Two-rule text review + one-rule-vs-two-rules sub-question
5. PLAYBOOK-6.10.7 zoom-out ask ("what would you push back on if I asked fresh?")

Explicit anti-rubber-stamp directive per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

### T2 attestation (Rigby, tool-grounded)

Rigby ran **10 tool_runs across two response turns** (initial + completion after mid-Item-3 truncation): `repo_tool.read_file × 8` + `repo_tool.search × 1` + 1 typo-file-not-found. **Anti-rubber-stamp gate: PASS.**

- **Item 1 AGREE (informational).** Four folds enumerable; envelope §3 table matches handoff.
- **Item 2 AGREE (informational).** Chapter 3 §3.2 correct natural home over §6.10 / §7.4.
- **Item 3 AGREE (non-blocking):** `--backfilled` legitimizes retroactive persistence. Non-blocking caution: `--concern` help text says "one sentence" (not enforced); recommend Option 1 (compress + pointer via `--evidence-ref`).
- **Item 4 AGREE (non-blocking):** 3.2.3 rationale should name invariant (DB connection / transaction visibility) not mechanism (asyncio event loop). **Sub-verdict: KEEP TWO SEPARATE RULES** (orthogonal disciplines sharing an authoring surface).
- **Item 5 zoom-out:** Not premature; proceed with two mitigations. Two folds surfaced:
  - **Fold A** `same_pr_mitigatable`: 3.2.3 invariant framing → mitigated same-envelope at §2.1
  - **Fold B** `future_trigger`: Testing Discipline chapter candidacy → recorded as §3.5 extension-point note

### T3 verification SIGN (light-touch)

5 tool_runs (envelope × 2, ledger × 2, search × 1). All AGREE. Two trivial non-blocking clarity nits (column header rename + preamble clarification) applied.

---

## Ledger backfill + live-persist (6 rows)

Ledger grew 148 → 154 rows during S2889:

| Row | Session | Classification | Backfilled | Arc |
|---|---|---|---|---|
| 149 | S2885 | `same_pr_mitigatable` | true | `s2885_transaction_testcase_dispatcher_db` |
| 150 | S2886 | `same_pr_mitigatable` | true | `s2886_transaction_testcase_dispatcher_db` |
| 151 | S2885 | `same_pr_mitigatable` | true | `s2885_shared_taxonomy_branch_fortification` |
| 152 | S2886 | `same_pr_mitigatable` | true | `s2886_shared_taxonomy_branch_fortification` |
| 153 | S2889 | `same_pr_mitigatable` | false | `v0_9_0_invariant_framing` (Fold A) |
| 154 | S2889 | `future_trigger` | false | `v0_9_0_testing_discipline_chapter` (Fold B) |

Rows 149-152 backfilled the S2885/S2886 corpus that PLAYBOOK-6.10.8 mandated but the respective sessions failed to persist at trigger time. Rows 153-154 dogfooded this amendment's own SIGN per v0.8.0 precedent.

**Novel-precedent moment:** first amendment where **retroactive ledger backfill precedes T1 SIGN routing** rather than following it, because the amendment's §3 corpus depended on ledger-enumerable rows. This establishes the shape for future amendments whose corpus depends on retroactively-persisted rows: backfill BEFORE T1 SIGN so the reviewer inspects the ratified backfill shape.

---

## Workspace deliverables (Rigby-authored)

Per `feedback_rigby_writes_workspace_deliverables` + `feedback_twin_deliverable_at_every_ratification`:

- **Ratification envelope (governance):** `6f8767c7-0ad4-4d3c-ad1d-c57ecb5144a4` — workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture & Research), category `governance`, type `ratification_record`. Clean; no diagnostic flags.
- **Content mirror (implementation):** `9a9ba3dc-2dc4-423d-acc6-2ccb104ec780` — same workspace, category `engineering`, type `initiative_phase_doc`. Diagnostic flags (`missing_initiative_id`) cleared post-create via ORM per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.

Rigby's tool_runs manifest verified both create paths + detail cross-check.

---

## Chris D-verdict (recorded verbatim)

Chris ratified at S2889 (2026-07-22, terminal): **"yes ship it"** — single-yes following joint Claude+Rigby AGREE on 8 design decisions (D1–D8; see envelope §5 + `d_verdicts` frontmatter).

Per `feedback_claude_rigby_agree_first_chris_yes_no`: all F-BLOCKING findings absent; all non-blocking findings resolved between Claude+Rigby before Chris routing; Chris ratified the resolved design rather than adjudicating.

Per `feedback_plain_english_decision_framing_for_chris`: plain-English framing (what ships / what we lose if no / whether it's more work later) posted to terminal, single recommendation not a menu.

---

## Chris pivot at S2889 close

After D-verdict + ship + workspace mirror, Chris pivoted from the originally-scripted Step 2 (character-os EB.4/C3 live UI dogfood per S2887 audit) to **open exploration mode on character-os UI**. Quote: *"I don't know what parts are going to need to hit u-d-b or what is only on character os."*

Chris directed: **C** (prep character-os UI → u-d-b endpoint reference sheet AND stand by for questions during exploration) + **close S2889 first**.

Concurrency safety envelope reconfirmed at S2889 close:
- Each terminal gets its own Rigby conversation pin — no state collision.
- Different repos, different branches — no git collision.
- **Watch:** character-os Docker postgres previously captured u-d-b's `:5433` via IPv6 wildcard (S2885 mitigation `USE_PGBOUNCER=0` still in force); orphan Redis cwd from `/development/` checkout (resolved S2886 open). If character-os side runs `docker compose up`, verify port ownership.
- Shared u-d-b PA endpoint (`http://localhost:8000`) — both Claudes may drive it; surface handles concurrent conversations.

---

## S2890 first-action queue

1. **Character-os UI → u-d-b endpoint reference sheet** — Claude produces terminal artifact mapping each character-os UI surface to (a) u-d-b endpoint hit, (b) character-os-only, or (c) hybrid. Sources: S2887 audit doc, `consult_engine.py`, engine-connections config spec.
2. **Chris explores character-os UI** — clicks around, tests understanding; pings Claude here for surface-identification when a click looks weird.
3. **Deferred until Chris signals:** original Step 2 EB.4/C3 scripted dogfood + Step 3 broader net-new slate + Playbook v0.10 candidates (if any surface).

---

## Twin canonical mirrors

- **Content mirror:** S2889 slate substrate → workspace `9a9ba3dc-2dc4-423d-acc6-2ccb104ec780` (Architecture & Research), category `engineering`, type `initiative_phase_doc`
- **Ratification envelope:** S2889 SIGN T1/T2/T3 AGREE + Chris D-verdict → workspace `6f8767c7-0ad4-4d3c-ad1d-c57ecb5144a4`, category `governance`, type `ratification_record`

Both authored by Rigby at S2889 mid-session per `feedback_rigby_writes_workspace_deliverables`.

---

## What ships in the close cascade

- This handoff (`docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`)
- `00-START-NEXT-SESSION.md` refresh — S2890 first-action = character-os UI reference sheet + exploration
- `tools/pa_local.sh` wrapper pin bump — `pa-bf73f55995144814` → S2890 mint via `session_lifecycle close --label s2889-playbook-v0.9.0`
- `docs/INDEX.md` refresh (auto-generated, `python manage.py build_docs_index`)

Per PLAYBOOK-7.4.1 bundling + PLAYBOOK-7.4.3 COMBINED cadence (cascade output = INDEX + this close-doc). Per PLAYBOOK-7.4.4 recycle waiver: docs-only diff (no `*.py`, no deps, no settings, no migrations, no worker config) — recycle waived; waiver reason recorded here per rule.

---

## Session infra artifacts

No infra artifacts this session (pure docs/governance amendment). `.env` values unchanged from S2888.

---

## Open items / carry-forward to S2890+

### Immediate (S2890 open first-action)

- **Character-os UI reference sheet** — Claude produces terminal artifact for Chris's exploration.

### Deferred (Chris directive)

- **Original Step 2** (character-os EB.4/C3 scripted dogfood) — deferred until Chris signals return; Chris pivoted to exploration mode.
- **D6 MORATORIUM** — still in force (no new strategic discovery arcs, no R1a-shaped fleet HMAC upgrades, no opportunity portfolio expansions).
- All prior forward-carried backlog items from S2888/S2887/etc. remain carried.

### New candidates surfaced at S2889

- **Testing Discipline chapter candidacy** (ledger row 154, `future_trigger`) — trigger: 2 more test-authoring rules land in §3.2 before Chapter 3 promotion to FULL, OR one SIGN cycle blocked by ambiguous test-authoring slot placement. Recorded as §3.5 extension-point note.

---

## S2889 close — what shipped

**Repo canonical (Claude-authored):**
- **PR #3402** `147dcc9cc` — Playbook v0.9.0 MINOR amendment (2 new [GR] rules, +276/-16, rule count 205 → 207).
- **PR `<this close cascade>`** — S2889 handoff + 00-START refresh + wrapper pin bump.
- **Tag `playbook-v0.9.0`** pushed to remote.

**Workspace canonical (Rigby-authored):**
- Ratification envelope deliverable `6f8767c7-0ad4-4d3c-ad1d-c57ecb5144a4` (clean).
- Content mirror deliverable `9a9ba3dc-2dc4-423d-acc6-2ccb104ec780` (diagnostic flags cleared post-create).

**Runtime impact:**
- Rule count 205 → **207**. Chapter 3 §3.2 grows from 2 to 4 rules.
- Ledger 148 → **154 rows** (+4 backfilled + 2 live).
- First Chapter 3 extension since v0.2.0 (8-version gap).
- First MINOR amendment where retroactive ledger backfill preceded T1 SIGN routing.
- First MINOR amendment bundling two rules that share an authoring surface but are logically orthogonal.
- Fourth consecutive MINOR shipped in single-session shape (v0.6.0/S2766 → v0.7.0/S2778 → v0.8.0/S2786 → v0.9.0/S2889).

**Governance debt disposition:**
- No CDs discharged (folds were amendment candidates, not CDs).
- No CDs opened.
- Testing Discipline chapter candidacy (ledger row 154) held as `future_trigger`, not a CD.
