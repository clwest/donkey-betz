# SESSION_2737 — Engineering Playbook v0.2.0 Ratified

**Date:** 2026-07-09 (Session 2736 arc — v0.2.0 ratification appended)
**Session type:** Constitutional MINOR amendment ratification
**Predecessor handoff:** [`SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md`](SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md)
**Predecessor ratification:** [`SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md`](SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md)
**Ratified canonical artifact:** `docs/ENGINEERING_PLAYBOOK.md` v0.2.0 at merge commit `3dc2c588`; body commit `ab3c88fa1ddc689a3fbe4cb59d13a5f5fb71cb9b`; content_hash `sha256:ae3228d9b9673dec672300b56b2076790b1548d946852fe08f594c3a37b46938`; git tag `playbook-v0.2.0`
**Workspace ratification record:** `RATIFICATION_20260709_PLAYBOOK_v0_2_0` (deliverable `fbcfcfde-9da9-48b1-8bd8-187885382521` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`), status=`completed`

---

## 1. Executive Summary

**The Engineering Playbook v0.2.0 MINOR amendment is ratified as of 2026-07-09.** Codifies three previously-live EOS rules from `docs/EOS_RULES.md` into the ratified Playbook body as new [GR] Governance Rules:

- **PLAYBOOK-5.2.2** (Chapter 5 §5.2) — Tool Autonomy Principle
- **PLAYBOOK-2.2.2** (Chapter 2 §2.2) — Capability Discovery Records precede engineering
- **PLAYBOOK-3.2.2** (Chapter 3 §3.2) — Acceptance-tests-first

Rule count: **190 → 193**. Version: **0.1.0 → 0.2.0**. Backward compatibility per PLAYBOOK-10.5.4 preserved.

Version bump per PLAYBOOK-10.5.1 + PLAYBOOK-10.3.3 = **MINOR**. Chris's initial directive was "PATCH — codify R1, R2, R3" but I flagged the constitutional constraint at PLAYBOOK-10.4.1 (PATCH MUST NOT introduce rules) and presented three options (A: correct MINOR path, B: PATCH-scoped clarification, C: System Owner Directive override). Chris chose **Option A** — the correct constitutional path.

## 2. Timeline

| UTC | Event |
|---|---|
| Session open | Chris directive: "Playbook v0.1.1 PATCH — codify R1, R2, R3" |
| Constitutional constraint flagged | PLAYBOOK-10.4.1 forbids new rules under PATCH; PLAYBOOK-10.5.1 requires MINOR minimum. Three options presented to Chris. |
| Chris directive: "Option A" | Correct MINOR path chosen; body edits begin |
| Body edits | Three new [GR] rules drafted in Chapters 2/3/5 STUB slots; frontmatter version bump (0.1.0 → 0.2.0); chapter frontmatter updated (Status annotation + Ch5 Statement classes [EP] → [EP], [GR]) |
| SIGN Batch 1 | Fresh pin `pa-89451b8072224824`; 4 criteria × 3 rules (A1-A4 + B1-B4 + C1-C4) + Objectives D/E/F; mixed CONFIRMED + REFINE |
| Body refinements | Multi-directive sentences split per PLAYBOOK-0.3.2; R3 descriptive sentence rewritten as normative MUST NOT |
| SIGN Batch 1 pin fatigue | Retired `pa-89451b8072224824` after 2-substantive-turn threshold per SIGN worker-instability recovery memory rule |
| SIGN Batch 2 | Fresh pin `pa-5d691c432e484ef7`; re-verdict R3 + D/E/F + final R1 further-split; final verdict 15/15 CONFIRMED |
| Body finalization | R1 first sentence further-split into two single-directive sentences per strict §0.3.2 |
| Workspace ratification record created | Deliverable `fbcfcfde-9da9-48b1-8bd8-187885382521`; body written via ORM (10,375 chars); title cleaned of "Rigby:" prefix; workspace bound to `a9a16593-...` |
| Chris directive: "Ratify v0.2.0" | Verbatim directive captured in deliverable §8; status transitioned draft → completed |
| Ratifiable body commit | `ab3c88fa` — frontmatter set to ratified state |
| Post-ratification frontmatter fill | `97f4cd22` — commit_sha + content_hash + git_tag populated |
| PR #3048 opened | Body + fill commits pushed; PR opened |
| PR #3048 merged | `--admin --squash --delete-branch`; merge commit `3dc2c588` |
| Tag `playbook-v0.2.0` applied | Annotated tag on merge commit `3dc2c588`; pushed to origin |
| Docs cascade | 4-step per `feedback_docs_cascade_at_every_close`: build_docs_index (3045 docs) → build_rag_corpus (36,817 chunks) → sync (2 updated / 3,043 skipped) → embed_documents --all-unembedded (0 unembedded found) |
| build_docs_provenance | 2,495 docs (HIGH=1601 / MEDIUM=394 / LOW=5 / UNKNOWN=495) |
| Ratification record mirror | `mirror_deliverable_to_document --ratification-record-id <UUID> --deliverable-id <UUID>` (self-override per memory rule) — Document `01586501-548c-4023-ac08-f2b678bcb8b0` created, 15 embedded chunks, `canonical_authority=workspace_canonical` |
| KFI-2 backfill | 18 docs upgraded to `repo_canonical` |
| Handoff (this file) | Session close |

## 3. SIGN discipline record (per PLAYBOOK-10.5.3)

**Full SIGN cycle discharged 15/15 CONFIRMED** across two batches, both on retired pins per §16 arc-close discipline.

| # | Objective | Verdict |
|---|---|---|
| A1-A4 | PLAYBOOK-5.2.2 (RFC-2119 + evidence + ID monotonic + single directive) | All CONFIRMED |
| B1-B4 | PLAYBOOK-2.2.2 (same 4 criteria) | All CONFIRMED |
| C1-C4 | PLAYBOOK-3.2.2 (same 4 criteria) | All CONFIRMED |
| D | Frontmatter integrity | CONFIRMED |
| E | Chapter frontmatter integrity | CONFIRMED |
| F | Fresh challenge (R1 keyword count review) | Resolved via R1 further-split |

**Body refinements folded during SIGN:**

- R3 descriptive sentence "A test authored to match what an implementation happens to do rather than what the capability specification requires is not an acceptance test" rewritten to normative "MUST NOT be admitted as an acceptance test for the campaign."
- R1 first sentence "the author MUST state the verification objective and the return format" further-split into "the author MUST state the verification objective. The author MUST state the expected return format." per strict §0.3.2 one-directive-per-sentence interpretation.

## 4. Repository state at HEAD

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `3dc2c588` (merge commit for PR #3048) |
| Playbook body commit_sha | `ab3c88fa1ddc689a3fbe4cb59d13a5f5fb71cb9b` |
| Playbook content_hash | `sha256:ae3228d9b9673dec672300b56b2076790b1548d946852fe08f594c3a37b46938` |
| Git tag | `playbook-v0.2.0` (annotated) |
| Rule count | 193 (was 190) |
| Rules added | PLAYBOOK-5.2.2, PLAYBOOK-2.2.2, PLAYBOOK-3.2.2 |
| Ratification record UUID | `fbcfcfde-9da9-48b1-8bd8-187885382521` (workspace `a9a16593-...`) |
| Ratification Document mirror | `01586501-548c-4023-ac08-f2b678bcb8b0` (workspace_canonical, 15 embedded chunks) |
| Playbook Document | `30dacfe1-6bb8-46d8-a6b6-05e10da744c7` (repo_canonical) |
| Wrapper pin | `pa-c9ec61a4512d40c7` (admin pin from v0.2.0 arc; can be retired at next session open) |

## 5. Constitutional debt at v0.2.0

- **CD-48** (from v0.1.0) — carried forward. Not addressed by v0.2.0.
- **CD-49** (from v0.1.0) — carried forward. Not addressed by v0.2.0.
- **No new constitutional debt** introduced by v0.2.0.

## 6. `docs/EOS_RULES.md` status after v0.2.0

Per PLAYBOOK-10.5.1, MINOR amendments MAY introduce new rules. The three R1/R2/R3 rules were previously Layer-6 authority at `docs/EOS_RULES.md`. After v0.2.0 ratification they are Layer-2 constitutional codification. `docs/EOS_RULES.md` remains as the live-rule ledger for FUTURE candidate rules that have not yet been codified — its authority for R1/R2/R3 becomes cross-reference material only.

The doc should NOT be deleted — the "Codification path" annotations at the bottom of each rule entry now resolve to shipped Playbook rules, providing a stable ratification audit trail.

## 7. Follow-ups queued

- **§16 CDR-001 wrap-up bundle** — 4 items, S-M effort. Queued from Session 2736.
- **CD-48 + CD-49 codification** — v0.3.x targets from v0.1.0 handoff, still queued.
- **Playbook v0.2.0 Rigby SIGN pass on 190 unaudited rules** — the v0.1.0 SIGN covered 95/190 rules; the balance remain unaudited. Not blocking; incremental verification at System Owner discretion.
- **Rigby integration-test harness** (CDR-002 §17.4) — deferred future arc.

## 8. Session close discipline

- **PRs merged this session:** #3048 (v0.2.0 MINOR).
- **Prior session PRs on main:** #3047 (Session 2736 §12 Knowledge Retrieval close).
- **Files changed via #3048:** `docs/ENGINEERING_PLAYBOOK.md` (+90 / -30), `tools/pa_local.sh` (wrapper rotation).
- **PA worker:** Post-S2728 restart; S2736 §12 P1-P3.1 code + S2737 v0.2.0 body all in main but the worker was not restarted this session. `make celery-recycle` before next Rigby dispatch.
- **Wrapper default pin:** `pa-c9ec61a4512d40c7` (v0.2.0 admin). Retire + fresh at next session open per §16.
- **Handoff + anchor updates:** this file + `00-START-NEXT-SESSION.md` (pending) + CLAUDE.md L7 anchor (unchanged — still points at Playbook, which is now v0.2.0).

---

## 9. Reference documents

1. This file — `SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md`
2. Predecessor arc close — `SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md`
3. Predecessor ratification — `SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md`
4. Ratified Playbook body — `docs/ENGINEERING_PLAYBOOK.md` v0.2.0 (rule_count 193, git tag `playbook-v0.2.0`)
5. Ratification record body — workspace deliverable `fbcfcfde-9da9-48b1-8bd8-187885382521` + Document mirror `01586501-548c-4023-ac08-f2b678bcb8b0`
6. Live-rule ledger — `docs/EOS_RULES.md` (still current; R1/R2/R3 now cross-reference to shipped Playbook rules)
7. Rules-added CDRs — CDR-001 (`docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md`) + CDR-002 (`docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md`)

---

## 10. Post-ratification bundle — §16 Notification Fanout wrap-up (CDR-001 §7 Gap 1-4)

Immediately after the v0.2.0 ratification landed (merge commit `5bcb9777`),
the §16 Notification Fanout wrap-up bundle from CDR-001 §7 was shipped as
**the first engineering work authored under the ratified Playbook v0.2.0
rules**. It exercises PLAYBOOK-2.2.2 (Category A before code) and
PLAYBOOK-3.2.2 (acceptance-tests-first) in production for the first time.

### 10.1 Category A verification (per PLAYBOOK-2.2.2)

At HEAD `5bcb9777`, grepped each of the 4 gap markers:

| Gap | Symbol | Files matching | Verdict |
|---|---|---|---|
| 1 — Inbox receiver | `signals_inbox*` / `@receiver.*DirectMessage` | 0 | Real |
| 2 — HAIDispatchLog | `HAIDispatchLog` | 0 in code | Real |
| 3 — channels_fired convention | `channels_fired` | 0 in code | Real |
| 4 — Cross-channel contract | `payload_channel_dispatch_state` | 0 | Real |

**Cat A confirms CDR-001 §7 scope.** No material scope change → no CDR-003
required. Existing CDR-001 §7 remains authoritative scope for the bundle.

### 10.2 Acceptance tests authored pre-implementation (per PLAYBOOK-3.2.2)

`core/tests/test_hai_wrap_up_bundle.py` — 14 tests across 4 AT classes +
meta guard. Test file docstring cites PLAYBOOK-3.2.2 and the Cat A audit
verbatim; guard against reverse-engineering codified per PLAYBOOK-3.2.2
last sentence.

### 10.3 Shipped code (PR #3050 merged as `a3b04af7`)

- **Gap 3+4 shared helper** — `core/services/hai_dispatch_state.py`:
  `ChannelDispatchState` enum (6 canonical states) + 3 payload helpers
  (`mark_channel_fired`, `has_channel_fired`, `channels_fired`) with
  backward-compat legacy `discord_sent` read.
- **Gap 2 audit table** — `core/models_hai_dispatch_log.py` +
  hand-authored migration `0380_session_2737_hai_dispatch_log.py`.
  10-field `HAIDispatchLog` model with UniqueConstraint (user,
  source_type, source_id, channel) + 3 indexes + identity carriage per
  CDR-001 §21 F6 (executor_actor + sponsor_actor + principal_user).
  Migration was hand-authored to scope to only HAIDispatchLog — Django's
  makemigrations at HEAD would have batched in unrelated pending
  Narrative* drift out-of-scope for the bundle.
- **Gap 1 Inbox receiver** — `core/signals_inbox_notifications.py`
  (`@receiver(post_save, sender='core.HumanAttentionItem')`) +
  `notify_hai_inbox` Celery task appended to
  `core/tasks_push_notifications.py`. Kill switch
  `settings.HAI_INBOX_DISPATCH_ENABLED` (default True). Urgency floor
  `'critical'`. Reuses `_pref_gates_pass` from Discord signal module.
  Writes `DirectMessage` + `HAIDispatchLog` per dispatch. Registered
  in `core/apps.py._register_signals`.

### 10.4 Test suite state at bundle close

- **14 passed, 0 failed** — all AT-16 tests green
- **Regression:** 77 passed across S2728 + S2736 + S2735 test surfaces
- **5 pre-existing test-DB cleanup errors** on
  `test_hai_discord_fanout.py` — `psycopg2.errors.DuplicateDatabase` /
  `ObjectInUse` from stale fixture state; unrelated to this bundle

### 10.5 Runtime state

- **PA worker:** post-S2728 restart; S2736 §12 P1-P3.1 + S2737 v0.2.0
  body + S2737 §16 bundle all in `main` but the worker has NOT been
  restarted. Run `make celery-recycle` before the next Inbox HAI is
  produced so `notify_hai_inbox` loads into the worker.
- **Migration state:** `0380` applied locally + at HEAD.

### 10.6 Governance stamps

- **PLAYBOOK-2.2.2 exercised** — Cat A run + CDR-001 confirmed → no
  CDR-003
- **PLAYBOOK-3.2.2 exercised** — 14 acceptance tests authored
  pre-implementation, `@skip`/`@expectedFailure` markers not used (all
  tests write the code path they exercise, so were red-then-green as
  each Gap shipped)
- **PLAYBOOK-5.2.2** not exercised — no Rigby SIGN dispatched
  (bundle-scale work does not require SIGN per PLAYBOOK-10.4.2
  lightweight discretion; the wrap-up bundle is not a Playbook amendment)

### 10.7 Commit graph

```
c3b79689  fix(hai_inbox): DirectMessage import + thread_type (#3053)
6b2841ef  fix(celery): register core.tasks_push_notifications at boot (#3052)
a3a0c51b  docs(session-2737): §16 bundle close — handoff §10 + cascade (#3051)
a3b04af7  feat(session-2737): §16 Notification Fanout — wrap-up bundle (#3050)
5bcb9777  docs(session-2737): Playbook v0.2.0 ratified — handoff + cascade (#3049)
3dc2c588  feat(playbook): v0.2.0 MINOR — codify R1/R2/R3 (#3048)
```

### 10.8 Latent integration defects discovered by post-recycle runtime verification

**This subsection was authored on Chris's directive** ("record this as a
latent integration defect discovered by the §16 wrap-up bundle — this
is exactly why the restart/registry verification discipline exists")
after the initial §16 bundle merge. It preserves the discovery pattern
so future post-merge close-outs run the same verification cycle.

The §16 wrap-up bundle merge (PR #3050 `a3b04af7`) shipped with three
latent integration defects that unit tests did NOT catch. All three
were discovered by executing `make celery-recycle` + `celery -A core
inspect registered` + a real HAI-critical-item smoke check against the
running workers. All three were fixed post-merge on the same day.

#### Defect 10.8.1 — `core.tasks_push_notifications` not registered at worker boot

**Latent since:** PR #1458 (2026-02-24, ~5 months) for the two Expo
tasks; PR #3038 (2026-07-09 S2735, ~24h) for Discord; PR #3040
(2026-07-09 S2735) for Web Push; PR #3050 (2026-07-09 S2737) for
Inbox — ALL five HAI push task names were latent-broken.

**Root cause:** four HAI signal modules (`signals_push_notifications`,
`signals_discord_notifications`, `signals_webpush_notifications`,
`signals_inbox_notifications`) all import from
`core.tasks_push_notifications` **inside function bodies** (lazy
`from core.tasks_push_notifications import ...` in the `_enqueue_*`
helpers). Django's app-boot only imports the signal modules at the
top level; the task module never loaded → `@shared_task` decorators
never fired → task registry never populated → `.delay()` calls would
have silent-`KeyError` on the running worker.

**Why tests missed it:** `test_hai_discord_fanout.py` (S2735) and
`test_hai_wrap_up_bundle.py` (S2737 §16 bundle) both patch `.delay`
directly and invoke the task functions as plain callables. Neither
exercises the Celery task registry lookup that production dispatches
depend on. Same class of production-only failure the memory rule
`feedback_procfile_makefile_queue_parity` captures.

**Fix:** PR #3052 `6b2841ef` — added `'core.tasks_push_notifications'`
to `core/celery.py::app.conf.imports` alongside the existing
hotfix-driven entries (S1253 docs-manager, S1257 platform-auditor +
chief-of-staff, S1267 bug-triage, S2735 cost-protection + beat-health).

**Verification:** `celery -A core inspect registered` post-recycle
returns all 5 tasks (`notify_critical_attention_item`,
`notify_hai_discord`, `notify_hai_inbox`, `notify_hai_webpush`,
`notify_needs_classification`) across all 5 workers (default,
broadcast, pa, long_running, code_jobs).

#### Defect 10.8.2 — `notify_hai_inbox` wrong `DirectMessage` import path

**Latent since:** PR #3050 (2026-07-09 S2737) merge — ~24 hours.

**Root cause:** `notify_hai_inbox` did
`from core.models_unified_system import DirectMessage` but
`DirectMessage` lives at `core/models_messaging.py:99`. The wrong
import raised `ImportError` on every task run.

**Why tests missed it:** AT-16-1 acceptance tests all inspect module
structure + patched delays; none of them execute the task's ORM path.
The class of "which module does X live in?" bugs cannot be caught by
static-inspection tests. Same category as Defect 10.8.1.

**Fix:** PR #3053 `c3b79689` — import `DirectMessage` +
`MessageThread` + `ThreadParticipant` from `core/models_messaging`.

**Verification:** smoke test 3 (post-recycle) shows
`HAIDispatchLog(channel='inbox', status='succeeded')` +
`DirectMessage` row created.

#### Defect 10.8.3 — `notify_hai_inbox` invalid `thread_type`

**Latent since:** PR #3050 (2026-07-09 S2737) merge — ~24 hours.
Surfaced only after Defect 10.8.2 was fixed.

**Root cause:** task created `MessageThread(thread_type='hai_system_notification')`
but `MessageThread.thread_type` is `max_length=20` with fixed choices
`{dm, group, rigby_routed}`. String was 23 chars AND not in the choice
list — `DataError: value too long for type character varying(20)`.

**Why tests missed it:** same class as 10.8.2 — static-inspection
tests do not exercise Django model validation or the actual `.create`
call path.

**Fix:** PR #3053 `c3b79689` — use `thread_type='rigby_routed'` per
`td_handlers_core.py:3820` precedent; store HAI-source metadata on
the `DirectMessage.metadata` JSONField instead of trying to shove it
into a new `thread_type` value.

**Verification:** smoke test 4 (on main after PR #3053 merge):
`HAIDispatchLog: 3 → 4` (+1 succeeded row);
`DirectMessage: 35 → 36` (+1 new inbox message);
`channel=inbox status=succeeded error=''`.

### 10.9 Post-verification governance stamps

Per Chris's directive: *"Do not open the next queue item until the
worker registry and enqueue path are confirmed healthy."*

- ✅ Worker registry: 5/5 tasks registered across 5/5 workers
- ✅ Enqueue path: real HAI-critical → `on_commit` → `.delay()` → task
  execution → `DirectMessage` + `HAIDispatchLog(status='succeeded')`
  written, all confirmed on main HEAD `c3b79689`
- ✅ Three latent defects fixed on the same day discovered

**Class of bug 10.8.1/10.8.2/10.8.3 lesson (candidate for a future
memory-rule addition):** any wrap-up bundle that ships a Celery task
MUST run `make celery-recycle` + `celery inspect registered` +
end-to-end runtime smoke check before the bundle is considered closed.
Static-inspection acceptance tests are insufficient; production-only
failure classes surface only against a running worker. The ratified
PLAYBOOK-2.2.2 (Category A before code) discipline should be extended
in future MINOR amendments to include a PLAYBOOK-8.x (Runtime
Discipline chapter, currently STUB) rule requiring post-recycle
runtime verification for Celery-task-shipping campaigns.

### 10.10 Commit graph — full session

```
c3b79689  fix(hai_inbox): DirectMessage import + thread_type (#3053)
6b2841ef  fix(celery): register core.tasks_push_notifications at boot (#3052)
a3a0c51b  docs(session-2737): §16 bundle close — handoff §10 + cascade (#3051)
a3b04af7  feat(session-2737): §16 Notification Fanout — wrap-up bundle (#3050)
5bcb9777  docs(session-2737): Playbook v0.2.0 ratified — handoff + cascade (#3049)
3dc2c588  feat(playbook): v0.2.0 MINOR — codify R1/R2/R3 (#3048)
```

---

## §11. Post-defect-ledger bundle — §C5 Celery Eager-Mode Integration Verification (CDR-003)

The class-of-bug lesson captured in §10.8 immediately motivated the
authoring of CDR-003 and a follow-on wrap-up bundle. Both proceeded
under the ratified Playbook v0.2.0 rules — the first end-to-end
exercise of the full EOS process on a single arc (Cat A → CDR →
Rigby SIGN → Chris ratification → acceptance-tests-first →
implementation → post-implementation SIGN → PR → merge).

### 11.1 CDR-003 authoring + Rigby Cat A SIGN

- CDR-003 authored at `docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md`
  documenting the discovery that a proposed L-effort greenfield
  "runtime integration-test harness" campaign was materially
  over-scoped — ~85% substrate already at HEAD (env flag +
  `captureOnCommitCallbacks` pattern in 10 files + 574-line conftest
  + 2 shipping reference implementations).
- Cat A SIGN pin `pa-16b8ba10b62f418c` minted; Rigby dispatched under
  Rule R1. SIGN-with-refinements:
  - O2 count correction: 15 files claim → **actual 10 files**
    (author mistook a search-tool `head_limit` hint for a real count)
  - O6 second reference implementation:
    `test_deliverable_intake_subscriber.py::EagerModeEndToEndTests`
    (S1250 vintage) surfaced as a second exemplar
  - Gap 4 discipline candidate: quantitative repository claims used
    to justify engineering scope MUST be independently recounted or
    produced by a count-returning mechanism before ratification
    (queued as future methodology-rule input; not codified this arc)
- All refinements folded into CDR-003 §12 append-only.
- Chris ratified all 3 decisions (CDR + §8 Option A + reduced scope
  with additional acceptance requirement: exemplar test must prove
  a real ORM side effect from the task body, not merely enqueue args).

### 11.2 Bundle implementation

Fresh implementation SIGN pin `pa-06f2e56fb9444f53` minted.
Acceptance tests written pre-implementation per PLAYBOOK-3.2.2.
Shipped as a single PR (`eac0f4da` / PR #3056):

- `core/tests/test_hai_runtime_integration.py` — 3 tests, all PASS.
  Uses `TestCase` + `self.captureOnCommitCallbacks(execute=True)` +
  `@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)`
  — no `.delay` patching. Asserts real ORM side effects: `DirectMessage`
  row created + `HAIDispatchLog(status='succeeded')` row written by
  the task body.
- `integration_celery` pytest marker registered in
  `tests/conftest.py::pytest_configure` + `pytest.ini` markers list
  + `pytest.ini testpaths` extended to `tests core/tests` (Rigby O5
  refinement).
- `docs/testing/RUNTIME_INTEGRATION_TESTS.md` — pattern doc with an
  explicit **Boundary** section listing all six items Chris directive
  named as things this pattern does NOT replace: worker task-registry
  verification, `make celery-recycle`, `celery inspect registered`,
  queue-routing verification, serialization/concurrency verification,
  end-to-end runtime smoke tests on live workers.
- Capability Graph §26 new candidate chain **§C5 Celery Eager-Mode
  Integration Verification** with 15-attribute template + explicit
  boundary + explicit discharge of CDR-002 §17.4 deferred arc.
- CDR-002 §17.4 DISCHARGED note added.

### 11.3 Post-implementation SIGN

- Rigby SIGN on pin `pa-06f2e56fb9444f53` returned 4× SIGN-CONFIRMED
  (O1-O4) + O5 REFINE flagging that `pytest.ini testpaths` was
  `tests` only, so `pytest -m integration_celery` would not discover
  the exemplar in `core/tests/`. Discharged via one-line
  `testpaths = tests core/tests` fix.
- Rigby final: *"bundle is ratifiable for PR + merge now."*
- Chris authorized PR + merge.

### 11.4 Runtime-appropriate verification

For this bundle the "runtime-appropriate" verification was
`pytest core/tests/test_hai_runtime_integration.py` (the tests
themselves ARE the runtime proof). 3/3 pass locally. Rigby's Rule R1
tool autonomy was exercised across two SIGN dispatches — she picked
her own tools each time and found substrate/refinements Claude's
grep would have missed with a tool-prescribed dispatch.

### 11.5 Governance stamps

- **PLAYBOOK-2.2.2** (CDR discipline) — third consecutive campaign
  where Cat A materially changed proposed scope; CDR authored and
  ratified before code. Three-for-three across CDR-001 / CDR-002 /
  CDR-003.
- **PLAYBOOK-3.2.2** (acceptance-tests-first) — the exemplar test IS
  the acceptance test for the bundle; authored pre-implementation
  with Chris's additional acceptance requirement folded in ("prove
  a real ORM side effect from the task body, not merely enqueue
  args").
- **PLAYBOOK-5.2.2** (Tool Autonomy) — two Rigby SIGN dispatches
  under Rule R1; both produced material refinements that a
  tool-prescribed dispatch would have suppressed.

### 11.6 Queued methodology candidate

Rigby's Gap 4 refinement flagged that quantitative repository claims
should be Rigby-recount-verified before CDR §5 scoring lands. This
lesson is **queued for future codification** (a potential
Chapter 8 Runtime Discipline MINOR OR a new Chapter 2 §2.4 rule).
Not codified this arc per Chris directive: *"Queue the following
methodology candidate without expanding this PR."*

### 11.7 SIGN pin retirement + wrapper rotation

Two pins retired at bundle close:
- `pa-16b8ba10b62f418c` — Cat A pin, retired after §12 fold
- `pa-06f2e56fb9444f53` — post-implementation SIGN pin, retired after
  Chris authorized merge

Wrapper `tools/pa_local.sh` rotated at each stage.

### 11.8 Commit graph — full session

```
eac0f4da  feat(session-2737): §C5 Celery Eager-Mode Integration Verification — CDR-003 bundle (#3056)
3ac97379  docs(session-2737-defect-ledger-cascade): INDEX + provenance refresh after PR #3054 (#3055)
fe6a1b3d  docs(session-2737): record 3 latent integration defects in handoff §10.8 (#3054)
c3b79689  fix(hai_inbox): DirectMessage import + thread_type (#3053)
6b2841ef  fix(celery): register core.tasks_push_notifications at boot (#3052)
a3a0c51b  docs(session-2737): §16 bundle close — handoff §10 + cascade (#3051)
a3b04af7  feat(session-2737): §16 Notification Fanout — wrap-up bundle (#3050)
5bcb9777  docs(session-2737): Playbook v0.2.0 ratified — handoff + cascade (#3049)
3dc2c588  feat(playbook): v0.2.0 MINOR — codify R1/R2/R3 (#3048)
```

---

**End of Session 2737.** Engineering Playbook v0.2.0 ratified + §16
Notification Fanout wrap-up bundle (CDR-001 §7 Gap 1-4) shipped +
three latent integration defects discovered by post-recycle runtime
verification + fixed same-day + reference lesson captured in §10.8 +
§C5 Celery Eager-Mode Integration Verification (CDR-003 bundle)
shipped as first end-to-end exercise of the full EOS process on a
single arc.
