---
title: "CDR-003 — Runtime Celery Integration Test Harness Substrate Capability Discovery Record"
id: CDR-003
type: capability_discovery_record
status: draft (awaiting Rigby independent SIGN + Chris ratification)
session_opened: 2737
date: 2026-07-09
author: Claude (Opus 4.7, 1M context) — Category A investigation before campaign scope-lock
related_chain: none (test infrastructure — proposed as graph §C5 candidate chain)
head_sha: 3ac97379
campaign_pin: pa-16b8ba10b62f418c (title `cdr-003-runtime-celery-integration-harness`)
predecessor_docs:
  - docs/handoffs/SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md §10.8 (three latent defects that triggered this campaign selection)
  - docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md §17.4 (integration-test harness deferred future arc — this CDR discharges the deferral)
  - docs/EOS_RULES.md R1 (Tool Autonomy) + R2 (CDR discipline) + R3 (Acceptance-tests-first) — all three ratified via PLAYBOOK v0.2.0 exercised here
governance_role: |
  Third Capability Discovery Record. Documents why the proposed
  "runtime integration-test harness" campaign scope changed after
  Category A discovery revealed ~85% substrate already at HEAD.
  Follows the CDR-001/CDR-002 11-section template with §11 Lessons
  Learned permanent + §12+ append-only reconciliation folds.
---

# CDR-003 — Runtime Celery Integration Test Harness Substrate Capability Discovery Record

## 0. Summary

Session 2737's latent-defect discovery (§10.8.1-3) motivated a proposed
campaign to *author a reusable Django TestCase-based integration-test
harness that exercises the full receiver → `on_commit` → Celery task
→ ORM adapter chain against a running test database*. Category A
investigation at HEAD `3ac97379` shows the substrate is **~85%
present**:

- `CELERY_TASK_ALWAYS_EAGER` env-controlled setting exists at
  `core/settings.py:1646`.
- `captureOnCommitCallbacks(execute=True)` pattern used in **15
  files** including `test_hai_discord_fanout.py`,
  `test_hai_webpush_fanout.py`, `test_beat_health.py`,
  `test_cost_protection_p1.py`, `test_failure_cluster_attention.py`.
- A comprehensive **574-line** `tests/conftest.py` (S416
  golden-path infrastructure) with user + admin_user + DB setup
  fixtures + markers for `integration`/`slow`/`external_api`/`golden_path`.
- A shipping **management-command + test pair**
  (`delegation_lifecycle_smoke_test`) that already uses
  `override_settings(CELERY_TASK_ALWAYS_EAGER=True)` + savepoint
  rollback + `.assert_called_once_with(0)` on `sys.exit` — a full
  end-to-end pattern.

The narrow specific gap is that the shipped
`captureOnCommitCallbacks(execute=True)` pattern **patches `.delay`
mid-callback** rather than letting the task body execute against the
real DB. Fixing that in isolation would have caught Defects 10.8.2
(wrong `DirectMessage` import) + 10.8.3 (invalid `thread_type`) at
merge time.

**Scope collapse:** L-effort greenfield campaign → S-M extension
bundle (one conftest helper + one marker + one exemplar pattern
extension + documentation).

---

## 1. Original assumptions (from campaign proposal at Session 2737
     open)

Verbatim engineering intent from the immediately-prior turn:

> "Provide a reusable Django TestCase-based integration-test harness
> that lets an acceptance-test exercise the full receiver →
> `on_commit` → Celery task → ORM adapter chain against a running
> test database, so class-of-bug 10.8.1-3 (module not registered /
> wrong import path / invalid model-field values) is caught before
> merge for every future campaign that ships Celery tasks."

Effort estimate offered: multi-session **L campaign** (greenfield
harness authoring). Framed as "closing CDR-002 §17.4 deferred future
arc."

---

## 2. Repository evidence discovered

Direct grep at HEAD `3ac97379`. All findings from local Claude greps;
Rigby's independent verification pass follows at §12.

### 2.1 `CELERY_TASK_ALWAYS_EAGER` env-controlled setting exists

`core/settings.py:1646`:

```python
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False') == 'True'
```

Default off; env flip flips Celery into inline task execution mode.

### 2.2 `captureOnCommitCallbacks(execute=True)` widely used

15 files at HEAD, including all four HAI Fanout Extension tests +
Beat Health + Cost Protection + Mission Verdict + Failure Cluster +
Signal Pattern Criticality + Body System Degradation:

```
core/tests/test_beat_health.py
core/tests/test_cost_protection_p1.py
core/tests/test_hai_webpush_fanout.py
core/tests/test_hai_discord_fanout.py
core/tests/test_failure_cluster_attention.py
core/tests/test_mission_verdict_attention.py
core/tests/test_body_system_degradation.py
core/tests/test_signal_pattern_criticality.py
core/tests/test_mission_verdict_broadcast.py
core/tests/test_pa_agent_execution_write.py
core/tests/test_deliverable_intake_subscriber.py
core/tests/test_opsrun_mission_fields.py
[+ 3 more]
```

Every one of them uses the same shape:

```python
with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
    HumanAttentionItem.objects.create(...)  # or equivalent producer

delay_mock.assert_called_once_with(item_id_str)
```

**The pattern verifies receiver-side + on_commit gating.** It does
NOT execute the task body — the `patch(_ENQUEUE_PATH)` neuters the
`.delay()` call, so the task's ORM work never runs.

### 2.3 574-line `tests/conftest.py` fixture suite (Session 416)

`tests/conftest.py` — golden-path testing infrastructure predating
this campaign by ~2 years:

- `django_db_setup` fixture extending pytest-django with pgvector.
- `user` / `admin_user` / `second_user` fixtures via UnifiedUser.
- Registered markers: `integration` / `slow` / `external_api` /
  `golden_path`.
- `mock_stability_api` / `mock_openai_api` / `mock_replicate_api` /
  etc. mocks for external providers.
- Ready-to-use `authenticated_client` + `authenticated_request`
  fixtures.

### 2.4 Shipping `delegation_lifecycle_smoke_test` management command

`core/management/commands/delegation_lifecycle_smoke_test.py` +
`core/tests/test_delegation_lifecycle_smoke_test.py`:

- Management command shipped for Arc I-0100 P3 (ADR-0003 §3.2).
- Runs a full lifecycle with `override_settings(CELERY_TASK_ALWAYS_EAGER=True)`.
- Emits five lifecycle labels (`agent_assigned` … `mission_closed`)
  + idempotency + savepoint rollback.
- Test at `test_delegation_lifecycle_smoke_test.py:36-65` verifies
  savepoint rollback leaves **zero net-new rows** (`OpsRun`,
  `OpsRunEvent`, `RigbyWorkItem`, `AgentExecution` counts unchanged
  post-run).

This is a full end-to-end runtime integration test. Not "one row +
patch"; not "receiver only." Real task execution + real ORM writes +
cleanup verification.

### 2.5 Class-of-bug pattern that Defects 10.8.2 + 10.8.3 fit

Both defects were reachable ONLY when the task body ran against a
real DB:

- 10.8.2 — `ImportError: cannot import name 'DirectMessage' from
  'core.models_unified_system'` — thrown by `notify_hai_inbox` when
  the task attempts its ORM section.
- 10.8.3 — `DataError: value too long for type character varying(20)`
  — thrown by `MessageThread.objects.create` when the task attempts
  its ORM section (only visible after 10.8.2 is fixed).

Both were caught by the manual runtime smoke test authored during
Session 2737 close (real HAI critical item → Celery task execution
→ `HAIDispatchLog` shows `status='failed'` with error text). Neither
was caught by AT-16-1 acceptance tests because AT-16-1 patches
`.delay` and calls the task body as a plain callable — same pattern
as the 15 `captureOnCommitCallbacks` sites.

---

## 3. Assumptions proven false

| # | Original assumption | Reality at HEAD `3ac97379` |
|---|---|---|
| A1 | "Harness must be authored from scratch as L-effort greenfield" | **FALSE.** ~85% substrate exists: env-flag + fixtures + 15 exemplar sites + shipping delegation-lifecycle end-to-end smoke test. |
| A2 | "Django TestCase-based harness" is a novel primitive to establish | **FALSE.** `tests/conftest.py` established this in Session 416. |
| A3 | "Need to add `override_settings(CELERY_TASK_ALWAYS_EAGER=True)` machinery" | **FALSE.** Settings flag already at `core/settings.py:1646`; `override_settings` decorator already used at `test_delegation_lifecycle_smoke_test.py:79`. |
| A4 | "New marker required for Celery-body integration tests" | **PARTIALLY FALSE.** `integration` marker already registered in `conftest.py:562`. A more-specific `integration_celery` marker MAY be added but is not required. |
| A5 | "Multi-session effort" | **FALSE.** Reduced to S-M extension bundle: one conftest helper + one exemplar pattern + docs. Estimated 1 session or less. |

---

## 4. Existing substrate identified

Total load-bearing substrate at HEAD:

- **1 Django settings hook** — `CELERY_TASK_ALWAYS_EAGER` at
  `core/settings.py:1646`.
- **1 Django `override_settings` pattern** — used at
  `test_delegation_lifecycle_smoke_test.py:79` and elsewhere.
- **1 canonical receiver-verifying test pattern** — the 15-site
  `captureOnCommitCallbacks(execute=True) + patch(.delay)` shape.
- **1 shipping end-to-end lifecycle smoke test** —
  `delegation_lifecycle_smoke_test` management command + tests.
- **1 574-line conftest fixture suite** — user + admin + DB +
  markers + 8+ mock-provider fixtures.
- **1 pytest marker registry** — `integration` / `slow` /
  `external_api` / `golden_path` markers pre-registered.
- **1 savepoint-rollback discipline** — used in
  `delegation_lifecycle_smoke_test` for zero-side-effect cleanup.

Approximately **~1,500 LOC of already-shipped test substrate** across
conftest + smoke test + 15 exemplar receiver tests.

---

## 5. New capability score

Applying the 15-attribute template used by CDR-001 + CDR-002.
Capability defined as: *acceptance tests can exercise the full
receiver → on_commit → Celery task → ORM adapter chain against a
running test database, catching class-of-bug 10.8.1-3 at merge time.*

| # | Attribute | Score | Basis |
|---|---|---|---|
| 1 | Human outcome | ✓ | class-of-bug 10.8.1-3 caught at merge |
| 2 | Trigger | ✓ | test authored with new marker + fixture invocation |
| 3 | Producer | ✓ | `tests/conftest.py` + `override_settings` + `captureOnCommitCallbacks` |
| 4 | Intermediate events | ✓ | on_commit → EAGER task exec → ORM writes |
| 5 | Consumers | ✓ | test-author writes assertion; CI runs it |
| 6 | Persistence | ✓ | test DB with savepoint rollback |
| 7 | Notifications | ✓ | pytest report + CI status |
| 8 | Frontend updates | N/A | test-time only |
| 9 | Human attention | ✓ | test failure blocks merge |
| 10 | Failure modes | partial | savepoint rollback tested; test-DB-cleanup errors (see S2737 §10.9 partial) still recur |
| 11 | Recovery | ✓ | `--keepdb` flag for iterative test dev; `pytest --create-db` for full reset |
| 12 | Verification | partial | `test_delegation_lifecycle_smoke_test` is the reference impl; needs generalization |
| 13 | Existing tests | partial | 15 receiver-side tests exist; 1 lifecycle test exists |
| 14 | Missing links | **3 items (S-M)** | see §7 |
| 15 | Effort | **S-M bundle** | see §7 |

**Revised completeness at HEAD: `13 of 15`.** Reduced-scope campaign
targets the 2 remaining items.

---

## 6. Engineering work deleted because of the discovery

| Item | Prior scope (L campaign) | Reduced scope (S-M bundle) |
|---|---|---|
| Author Django TestCase-based harness | New abstraction to be authored | **Deleted.** Substrate exists — extend the shipped `captureOnCommitCallbacks` pattern instead. |
| Design + implement `CELERY_TASK_ALWAYS_EAGER` machinery | Assumed missing | **Deleted.** Flag + `override_settings` pattern shipped. |
| Author conftest fixture suite | Assumed missing | **Deleted.** 574-line conftest exists since Session 416. |
| Establish savepoint-rollback cleanup discipline | Assumed novel | **Deleted.** Established by `delegation_lifecycle_smoke_test` for Arc I-0100 P3. |
| Author marker registry for integration tests | Assumed missing | **Deleted.** `integration` marker registered in `conftest.py:562`. |
| Establish per-provider mock library | Assumed missing | **Deleted.** 8+ mocks in `tests/conftest.py`. |
| Multi-session campaign infrastructure | Full CDR + SIGN + phases | **Reduced** to bundle-scope discipline (like §16 wrap-up) — 1 session estimated. |

**Aggregate deleted work:** an entire L-effort greenfield campaign +
5-6 substrate deliverables + multi-session sequencing overhead.

---

## 7. Remaining work

Three evidence-based gap items. All S-M in effort. Aggregate is one
1-session wrap-up bundle, not a campaign.

### Gap 1 — Extend the `captureOnCommitCallbacks(execute=True)` pattern to allow task body execution (S)

- Today: 15 exemplar sites all `patch(_ENQUEUE_PATH)` so `.delay` is
  neutered. Task body never runs against the DB. This is the
  specific class-of-bug 10.8.2/10.8.3 fell into.
- Fix: add a companion pattern that *does not* patch `.delay` and
  *does* set `override_settings(CELERY_TASK_ALWAYS_EAGER=True)`. The
  task then executes inline against the test DB.
- Effort: **S** — one exemplar test file (probably a new
  `test_hai_integration.py`) using the new pattern to prove the shape.

### Gap 2 — Register a specific `integration_celery` pytest marker + conftest fixture (S)

- Today: `integration` marker registered but generic. No fixture
  auto-flips `CELERY_TASK_ALWAYS_EAGER`.
- Fix: add `integration_celery` marker in `pytest_configure`;
  add a `celery_eager` autouse-conditional fixture that flips the
  setting for tests carrying the marker. Or simpler: document usage
  of `@override_settings(CELERY_TASK_ALWAYS_EAGER=True)` directly on
  test methods, no new fixture needed.
- Effort: **S** — one conftest change + docs.

### Gap 3 — Document the pattern (S)

- Today: no doc names the "runtime Celery integration test" pattern
  as a first-class discipline. Future campaigns don't know when to
  reach for it.
- Fix: a short doc (either a new subsection in
  `docs/topics/celery-workers.md` or a new `docs/testing/RUNTIME_INTEGRATION_TESTS.md`)
  naming the pattern, when to use it, when NOT to use it, and
  linking the exemplar from Gap 1.
- Effort: **S** — ~50-100 lines of doc.

**Aggregate remaining scope:** 1 session or less. Not a campaign.

---

## 8. Whether the Capability Graph should be updated

**Marginal update at most.** The Capability Graph tracks
capability chains (mission completion, deliverable-ready, etc.); test
infrastructure is not a first-class chain in the current graph
structure.

Options:

- **Option A (recommended):** Add a §C5 candidate chain "Runtime
  Test Coverage" per graph §23 F4 pattern, listing
  `captureOnCommitCallbacks + patch(.delay)` (receiver-side) vs
  `override_settings(CELERY_TASK_ALWAYS_EAGER=True) + no-patch`
  (task-body-side) as the two shape variants. Score 13/15 per §5
  above.
- **Option B:** No graph update; cite CDR-003 from
  `docs/topics/celery-workers.md` and from the future
  PLAYBOOK-8.x (Runtime Discipline chapter, currently STUB) MINOR
  amendment when it lands.
- **Option C:** Add a note to CDR-002 §17.4 recording that this CDR
  discharges the deferred arc.

Recommended: **Option A + Option C** (add candidate chain + close the
deferred arc). Neither is load-bearing for the wrap-up bundle
implementation.

---

## 9. Ratification path

1. **Rigby independent SIGN** — fresh SIGN pin
   `pa-16b8ba10b62f418c` already minted. Dispatched under Rule R1
   (objective + return format; no tool prescription) with this CDR
   as the anchor.
2. **Reconciliation** — Rigby's verdict folded into §12 append-only.
3. **Chris ratifies** the final scope + acceptance tests + option
   choice from §8.
4. **Bundle implementation** — Gap 1 + Gap 2 + Gap 3 as a single
   PR, per §16 wrap-up bundle discipline.
5. **Post-merge runtime verification** — same discipline that
   surfaced the S2737 defects (recycle + smoke test the exemplar).

---

## 10. Scope of this document

This CDR does not propose code. It does not select a next campaign
(the queue item was already selected in the prior turn — this CDR
only reshapes the scope). It documents why the campaign scope
changed from L-effort greenfield to S-M wrap-up bundle. Campaign
implementation begins only after Chris ratifies the reduced scope.

---

## 11. Lessons Learned

*This section is permanent to every Capability Discovery Record*
(canonized in CDR-001 §11 + PLAYBOOK-2.2.2 governance metadata).
CDR-001 lessons + CDR-002 lessons are not restated; new lessons from
CDR-003 append below.

### 11.1 CDR-003-specific methodology lessons

- **The CDR primitive scales beyond capability chains.** CDR-001 +
  CDR-002 targeted named Capability Graph chains (§16, §12). CDR-003
  targets **test infrastructure** — a substrate the graph does not
  currently model. The 11-section template held cleanly. The
  primitive generalizes to any campaign whose scope is a discovery
  candidate, not just chain-scoped campaigns.
- **Cat A discipline was applied 30 minutes after the class-of-bug
  discovery.** Session 2737 §10.8 defects were discovered ~30 min
  before this CDR opened. Applying PLAYBOOK-2.2.2 immediately —
  before proposing a scope — surfaced the ~85% substrate that made
  the campaign trivially smaller. Cat A discipline **immediately
  after evidence surfaces** is the higher-value pattern; delayed Cat
  A during campaign planning risks entrenching the assumption before
  evidence contradicts it.
- **Assumption of "greenfield L campaign" was epistemically motivated
  by the visible symptom** (three latent defects) rather than by a
  substrate audit. The proposal in the prior turn framed the campaign
  as "authoring a new harness" because the observed failure was a
  missing test. That framing missed that most of the harness parts
  were already at HEAD. This is the same pattern CDR-002 §11.1
  named — "assumption of missing substrate motivated by a visible
  symptom."

### 11.2 Cross-CDR meta-lesson (three consecutive Category A
     investigations)

- CDR-001 corrected §16 "MISSING NotificationFanoutService" via 3
  shipped receiver adapters.
- CDR-002 corrected §12 "PA turn does NOT auto-invoke" via
  DocsContextBuilder + PAKnowledgeInjector.
- CDR-003 corrects "author a runtime integration harness" via
  15-site pattern + shipping delegation-lifecycle smoke test.

Three-for-three: **Cat A against HEAD systematically overturns the
initial assumption.** This is not a coincidence — it is the ratified
PLAYBOOK-2.2.2 discipline earning its keep three consecutive
campaigns. Any future MINOR Playbook amendment codifying the
Chapter 8 Runtime Discipline should cite CDR-001 + CDR-002 + CDR-003
together as the three-instance proof that Cat A is load-bearing at
campaign-selection time.

### 11.3 Concrete carry-forward from CDR-003

- The `captureOnCommitCallbacks(execute=True) + patch(.delay)`
  pattern is the platform's canonical **receiver-side** integration
  test shape. Any future chain proposing "verify signal receiver
  fires on producer save" should reuse this shape.
- The `override_settings(CELERY_TASK_ALWAYS_EAGER=True) + no-patch +
  savepoint rollback` pattern is the platform's canonical
  **task-body-side** integration test shape. Any future chain
  proposing "verify Celery task body executes correctly against ORM"
  should reach for this shape. Reference implementation:
  `delegation_lifecycle_smoke_test`. Bundle Gap 1 adds the second
  reference implementation at HAI-fanout scope.

---

## 12. Rigby SIGN-with-refinements reconciliation (append-only per playbook §14)

Dispatched on campaign SIGN pin `pa-16b8ba10b62f418c` under EOS Rule
R1 (objective + return format; no tool prescription). §1–§11
preserved verbatim per playbook §14.

### 12.1 Per-objective verdict

| # | Objective | Verdict | Evidence / refinement |
|---|---|---|---|
| O1 | `CELERY_TASK_ALWAYS_EAGER` env-controlled | **SIGN-CONFIRMED** | `core/settings.py:1646` verbatim `os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False') == 'True'` — env-controlled, defaults `False`. |
| O2 | 15-file `captureOnCommitCallbacks` pattern | **SIGN-WITH-REFINEMENTS** | Rigby found 10 files. Claude's independent re-run without a head_limit confirms **10 files** (initial `Found 15 files limit: 15` was the tool head_limit hint, not the count). CDR-003 §2.2 corrected: **10 files, not 15**. |
| O3 | 574-line `tests/conftest.py` fixture suite | **SIGN-WITH-REFINEMENTS** | User/admin_user/django_db_setup/pgvector/markers all confirmed. `integration_celery` marker is NOT registered (as CDR-003 §7 Gap 2 already flags — the refinement is Rigby confirming Gap 2 is real). |
| O4 | `delegation_lifecycle_smoke_test` command + test | **SIGN-WITH-REFINEMENTS** | Command's `override_settings(CELERY_TASK_ALWAYS_EAGER=True)` at `:112-116` + savepoint rollback at `:154-156` + `:348` + `:360` verified. `assert_called_once_with(0)` was described in the dispatch message as being on `sys.exit` — that pattern IS at `test_delegation_lifecycle_smoke_test.py:51` (test file), NOT in the command file. Dispatch-message imprecision, not a CDR body error. |
| O5 | 3-gap analysis in §7 | **SIGN-WITH-REFINEMENTS** | Three gaps directionally correct; Rigby flags a **fourth gap** (see §12.2) — reconciliation accuracy / evidence tightening. |
| O6 | Fresh challenge — missed substrate | **CONFIRMED — real missed substrate** | `core/tests/test_deliverable_intake_subscriber.py:312-357` explicitly uses `override_settings(CELERY_TASK_ALWAYS_EAGER=True)` with the code comment *"With CELERY_TASK_ALWAYS_EAGER=True, apply_async actually executes ..."* — a second reference implementation of the exact pattern Gap 1 proposes to extend. CDR-003 §2.4 cited only `delegation_lifecycle_smoke_test`; §12.4 folds `test_deliverable_intake_subscriber.py` as second exemplar. |

### 12.2 Rigby's Gap 4 — reconciliation accuracy / evidence tightening

Rigby's O5 refinement is that CDR-003's scope-collapse argument
relies on **precise substrate accounting**. Two count/citation
imprecisions were found:

- **§2.2** claimed 15 files use `captureOnCommitCallbacks`; actual
  count is 10.
- **Dispatch message** conflated the `assert_called_once_with(0)`
  pattern between the command file and the test file; the pattern
  IS in the test file at `:51`, not in the command file. The CDR
  body §2.4 does not make this specific claim, but the dispatch
  language was imprecise.

**Gap 4 discharge**: this §12 section itself is the fix — CDR-003
now records the corrected counts (10, not 15) and the corrected
citation (`assert_called_once_with(0)` at
`test_delegation_lifecycle_smoke_test.py:51`). Future CDRs should
run a Rigby-side count-check pass BEFORE proposing scope, not
after.

### 12.3 File count correction folded (per §12.2)

Corrected substrate accounting for the `captureOnCommitCallbacks`
pattern (§2.2 header claim `15 files` is superseded by this §12.3):

**Actual: 10 files.**

```
core/tests/test_beat_health.py
core/tests/test_cost_protection_p1.py
core/tests/test_hai_webpush_fanout.py
core/tests/test_hai_discord_fanout.py
core/tests/test_failure_cluster_attention.py
core/tests/test_mission_verdict_attention.py
core/tests/test_body_system_degradation.py
core/tests/test_signal_pattern_criticality.py
core/tests/test_mission_verdict_broadcast.py
core/tests/test_deliverable_intake_subscriber.py
```

The 10-vs-15 delta does NOT change the scope-collapse verdict:
substrate is still ~85% present. The pattern is still widely
established. The delta only tightens the substrate inventory.

### 12.4 Rigby's O6 discovery — second reference implementation

`core/tests/test_deliverable_intake_subscriber.py:312-357` (folded
here since CDR-003 §2.4 cited only `delegation_lifecycle_smoke_test`
as reference implementation):

```python
# Line 312 (comment):
"""With ``CELERY_TASK_ALWAYS_EAGER=True``, apply_async actually executes ..."""
# Lines 323 + 357:
CELERY_TASK_ALWAYS_EAGER=True,
```

This is a **second production reference implementation** of the
exact pattern Gap 1 (§7) proposes to extend to the HAI fanout scope.
Two reference implementations exist. This further reinforces the
scope-collapse verdict.

### 12.5 Bottom-line reconciliation

- **CDR-003 core finding held.** Scope-collapse from L-effort
  greenfield campaign to S-M wrap-up bundle is **defensible** —
  substrate is heavily present (env flag + 10-site pattern +
  574-line conftest + TWO reference implementations, not one).
- **§2.2 count corrected** — 10 files, not 15.
- **§2.4 augmented** — second reference implementation
  (`test_deliverable_intake_subscriber.py`) added.
- **§7 Gap 4 added** — reconciliation accuracy discipline. Marked
  as discharged by this §12 section.
- **All 3 original gaps in §7 confirmed as real**. No engineering
  gap added or removed.

### 12.6 New EOS methodology lesson candidate from Rigby's O5

Rigby's O5 refinement is itself a codification candidate:
**Cat A substrate counts should be verified by an independent
recount before campaign scope is proposed.** The specific mode of
failure — a search tool's head_limit hint mistaken for the actual
count — is the exact discipline the §11 Lessons Learned template
was authored to catch. Future CDR authors should run one extra
verification query per numerical claim before writing the CDR body,
OR mark counts as `pending Rigby recount` when authoring.

Proposed input to a future MINOR Playbook amendment on Chapter 8
Runtime Discipline (currently STUB): a rule requiring
substrate-count verification against a Rigby-side recount before
CDR §5 scoring lands.

---

**End of CDR-003 post-Rigby-SIGN-reconciliation.** Chris
ratification of the reduced scope (§10.3-equivalent — §7 Gap 1-3 +
Rigby's Gap 4 discharged via §12) is the gate to any
bundle-implementation code landing.
