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
a3b04af7  feat(session-2737): §16 Notification Fanout — wrap-up bundle (#3050)
5bcb9777  docs(session-2737): Playbook v0.2.0 ratified — handoff + cascade (#3049)
3dc2c588  feat(playbook): v0.2.0 MINOR — codify R1/R2/R3 (#3048)
```

---

**End of Session 2737.** Engineering Playbook v0.2.0 ratified + §16
Notification Fanout wrap-up bundle (CDR-001 §7 Gap 1-4) shipped as
first engineering work under ratified v0.2.0 rules.
