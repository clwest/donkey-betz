---
title: "CDR-001 — Notification Fanout Capability Discovery Record"
id: CDR-001
type: capability_discovery_record
status: ratified by Chris 2026-07-09 + Rigby SIGN-with-refinements reconciled via fresh pin pa-821c1ae4efd3400b — see §12
session_opened: 2736
date: 2026-07-09
ratified_at: 2026-07-09 (Chris directive: ratify + add §11 permanent lessons section + dispatch to Rigby)
author: Claude (Opus 4.7, 1M context) — Category A investigation before campaign selection
related_chain: platform_capability_graph.md §16 Notification Delivery (+ §2 Deliverable Ready producer, §8 HAI Escalation)
head_sha: 2c2c6cc2
predecessor_docs:
  - docs/research/platform/platform_capability_graph.md (S2734 draft + Rigby SIGN §23 fold)
governance_role: |
  A Capability Discovery Record is the governance artifact produced when a Category A
  investigation materially changes the scope of a proposed engineering campaign. It
  explains why the campaign changed. It is NOT an implementation deliverable; no code
  is proposed here. It is the audit trail between "Capability Graph said X" and
  "Repository showed Y". Chris ratifies; Rigby cross-checks; the ledger records.
---

# CDR-001 — Notification Fanout Capability Discovery Record

## 0. Summary

Category A investigation against HEAD `2c2c6cc2` refuted the Capability Graph §16
"Notification Delivery" completeness score (6/15 per Rigby SIGN F2 refinement;
8/15 per Claude draft). Actual completeness is **~12/15**. The proposed
"Unified Notification & Attention Fabric" campaign was materially disqualified
because the abstraction it proposed — a `NotificationFanoutService` — already
exists in a functionally-equivalent shape (`HumanAttentionItem` post_save +
per-channel receivers) and was explicitly rejected as a new class by the
Session 2735 team in shipped code. Campaign scope collapsed from an M-L
campaign to a **1–2 session wrap-up PR bundle**.

---

## 1. Original Capability Graph assumptions

Verbatim from `docs/research/platform/platform_capability_graph.md` §16 (draft
S2734, Rigby SIGN §23 F2 refinement folded 2026-07-09):

- **Score:** `8 of 15` fully wired at HEAD (Claude draft); revised to `6 of 15
  with tracked uncertainty` after Rigby's F2 refinement.
- **Chain diagram:** `any producer → **MISSING: NotificationFanoutService** →
  per-user preferences → dedup by (recipient, source_id) → fan-out to N of
  {Web Push, Expo, Discord, Inbox DirectMessage, HAI} → device / channel →
  Human receives once.`
- **Item 14 (Missing links):** "one `NotificationFanoutService` with (a) user-
  pref lookup, (b) dedup by (recipient, source_type, source_id), (c) N adapter
  calls, (d) `NotificationLog` audit. **This is Sequence L2 from the
  Integration Readiness Matrix.**"
- **Item 15 (Effort):** M (unification service is the whole thing).
- **§21 recommendation (Claude draft):** §16 is FIRST chain to complete; 4
  other chains reuse fanout service once it exists.
- **§23 F2 refinement (Rigby SIGN):**
  - Web Push CONFIRMED
  - Inbox CONFIRMED
  - **Expo push UNEVIDENCED** — "77 files match 'Expo' but zero match 'expo push'"
  - **Discord broadcast infra UNEVIDENCED** — "not spot-checked"
  - **HAI adapter UNEVIDENCED** — "class exists but has not been confirmed as
    a `NotificationFanoutService.dispatch()` target yet"
  - **Channel-preference surface UNEVIDENCED** — "Do NOT assume the preference
    lookup is a query — it may need to be built"
- **§23 F3 revised recommendation:** §16 downgraded to SECOND chain "blocked
  on a discovery pass to evidence Expo / Discord / HAI adapters + channel-
  preference surface." **This CDR is that discovery pass.**

---

## 2. Repository evidence discovered

Direct grep + read at HEAD `2c2c6cc2` (`git log 2026-07-09`).

### 2.1 Three receiver-driven adapters exist and are wired to `HumanAttentionItem.post_save`

| Channel | Signal receiver | Celery task | Adapter service | Shipped |
|---|---|---|---|---|
| Expo push | `core/signals_push_notifications.py:14` `on_critical_attention_item` | `core/tasks_push_notifications.py:59` `notify_critical_attention_item` | `core/services/expo_push.py` | PR #1458 (2026-02-24) |
| Discord | `core/signals_discord_notifications.py:160` `on_hai_discord_dispatch` | `core/tasks_push_notifications.py:106` `notify_hai_discord` | `core/services/discord_notifications.py` (2,319 lines) | PR #3038 (2026-07-09, S2735) |
| Web Push | `core/signals_webpush_notifications.py` | `core/tasks_push_notifications.py:181` `notify_hai_webpush` | `core/services/push_notification_service.py` (284 lines) | PR #3040 (2026-07-09, S2735) |

Every receiver is `@receiver(post_save, sender='core.HumanAttentionItem')`.
The unified event model IS `HumanAttentionItem`. There is no missing "unified
event"; the receivers themselves are the fanout.

### 2.2 `HumanPreference` model exists with all four fields the graph called MISSING

`core/models_human_interface.py:268` — `class HumanPreference(models.Model)`:

- `quiet_hours_start` / `quiet_hours_end` — `TimeField`
- `min_urgency_to_notify` — `CharField(choices=HumanAttentionItem.URGENCY_CHOICES)`
- `preferred_channel` — `CharField(choices=[('discord','Discord'),('web','Web Dashboard'),('email','Email')])`
- `blocked_sources` — `JSONField(default=list)`
- Plus: `trusted_agents`, `topic_weights`, `source_weights`, `avg_decision_time_ms`,
  `approval_rate`, `total_decisions`, `review_depth`, `auto_approve_low_risk`

The Discord signal (`signals_discord_notifications.py:106-142` `_pref_gates_pass`)
uses all five gate fields today and exports the helper for reuse by the Celery
task. This IS the "user-pref lookup" the graph called for.

### 2.3 Rollback safety + async decoupling already ratified

`signals_discord_notifications.py:190` — `transaction.on_commit(lambda: _enqueue_dispatch(item_id))`.

Docstring lines 65-67 explicitly cite the pattern as a Rigby SIGN Q3 REQUIRED
refinement (pin `pa-247f1595c5934325`): "Rollback safety: `transaction.on_commit`
ensures the Celery task is only enqueued if the HAI row actually committed.
Rolled-back transactions produce no Discord alerts."

The (a) `post_save` receiver → (b) synchronous kill-switch + urgency + payload-flag
guards → (c) `transaction.on_commit` → (d) Celery task enqueue → (e) task re-loads
HAI + re-applies preference gates → (f) adapter call pattern is codified across
all three shipped channels. It is the platform's ratified fanout shape.

### 2.4 Producer-side dedup convention exists

`signals_discord_notifications.py:176-184`: if
`instance.payload.get('discord_sent') is True`, skip enqueue. Both the receiver
AND the task check the flag. The docstring calls out `BodyCoordinator._handle_digestive_blocked`
and `heart.alert_if_critical` as producers that fire imperative Discord alerts
first and set the flag on the HAI to suppress double-delivery.

### 2.5 The S2735 shipping team explicitly rejected `NotificationFanoutService`

Load-bearing quote — `signals_discord_notifications.py:12-24`:

> "The same receiver-driven fanout pattern is already used by
> `signals_push_notifications.on_critical_attention_item` for Expo push (which
> enqueues `notify_critical_attention_item.delay(item_id)`). **No new fanout
> service is introduced** — this module wires the existing HAI substrate to the
> existing Discord adapter via the pre-existing Celery worker infrastructure."
>
> "**Cat A discipline: NO new architecture beyond one signal receiver + one
> Celery task.** Dedup + priority + urgency semantics live in
> `HumanInterfaceService.create_attention_item`. The Discord adapter lives in
> `discord_notifications.py`. The Celery worker + queue infrastructure already
> exists."

This is a ratified engineering decision embedded in shipped code from ~24
hours ago.

---

## 3. Assumptions proven false

| # | Graph / §23 assumption | Reality at HEAD `2c2c6cc2` |
|---|---|---|
| A1 | "Expo push UNEVIDENCED" (§23 F2) | FALSE. Expo signal + adapter shipped PR #1458 five months ago; receiver at `signals_push_notifications.py:14`; adapter at `services/expo_push.py`. Grep pattern `expo push` (space) misses the real file names. |
| A2 | "Discord broadcast infra UNEVIDENCED" (§23 F2) | FALSE. `discord_notifications.py` is 2,319 lines. Discord fanout receiver shipped S2735 PR #3038. |
| A3 | "HAI adapter UNEVIDENCED" (§23 F2) | FALSE by re-framing. HAI is not a target adapter — it IS the unified event, and 3 channel adapters receive on `HumanAttentionItem.post_save`. |
| A4 | "Channel-preference surface UNEVIDENCED — do NOT assume the preference lookup is a query" (§23 F2) | FALSE. `HumanPreference` model exists with 5 gate fields (min_urgency / quiet_hours_start / quiet_hours_end / blocked_sources / preferred_channel). The Discord signal uses all five today via `_pref_gates_pass`. |
| A5 | "MISSING NotificationFanoutService" (§16 Item 14) | FALSE. The receiver-driven pattern IS the fanout. S2735 shipped code (~24h ago) explicitly names this as a ratified engineering decision. |
| A6 | Score `8 of 15` / `6 of 15` (Claude / Rigby-refined) | FALSE. Actual score is ~`12 of 15` (see §5 below). |
| A7 | §21 recommendation "§16 is the highest-leverage campaign because 4 other chains reuse fanout service" | FALSE by re-framing. The chains already reuse — they all produce HAIs, which auto-fanout. There is no gated "leverage unlock" waiting for a new service. |

---

## 4. Existing substrate identified

Total substrate load-bearing to the notification-fanout capability at HEAD:

- **1 unified event model** — `HumanAttentionItem` (`core/models_human_interface.py`).
- **1 preference model** — `HumanPreference` (5 gate fields ratified in production use).
- **1 shared preference gate helper** — `_pref_gates_pass(user_id, source_type, urgency)` at `signals_discord_notifications.py:106-142`, exported for cross-adapter reuse.
- **3 shipped channel receivers** — Expo (`signals_push_notifications.py`), Discord (`signals_discord_notifications.py`), Web Push (`signals_webpush_notifications.py`).
- **3 shipped Celery tasks** — `notify_critical_attention_item`, `notify_hai_discord`, `notify_hai_webpush` (all in `core/tasks_push_notifications.py`).
- **3 shipped channel adapters** — `services/expo_push.py`, `services/discord_notifications.py`, `services/push_notification_service.py`.
- **1 ratified async decoupling pattern** — `transaction.on_commit` + Celery task + re-load-and-re-gate inside task.
- **1 ratified producer-side dedup convention** — `payload['discord_sent']=True` (per-channel flag).
- **1 ratified kill-switch pattern per channel** — `HAI_<CHANNEL>_DISPATCH_ENABLED` settings.
- **1 audit table** — `NotificationLog` at `core/models_push_notifications.py:183` (Web-Push-scoped today).
- **1 producer-side entry point** — `HumanAttentionBridge` at `core/services/human_attention_bridge.py` (1,439 lines, 5+ documented producer categories).

Approximately **~4,900 lines of load-bearing code** across signals, tasks,
adapters, models, and bridge, plus the 3 shipped test files (410 lines in
`test_hai_webpush_fanout.py` alone).

---

## 5. New capability score

Reclassifying §16 chain items against the 15-attribute template used by the
graph, using HEAD evidence rather than Rigby's F2 refinement:

| # | Attribute | Prior score | Actual score | Basis |
|---|---|---|---|---|
| 1 | Human outcome | ✓ | ✓ | user receives ≥ 1 alert per HAI produced |
| 2 | Trigger | ✓ | ✓ | `HumanAttentionItem.post_save` |
| 3 | Producer | ✓ | ✓ | `HumanInterfaceService.create_attention_item` |
| 4 | Intermediate events | partial | ✓ | 3 receivers + 3 Celery tasks wired |
| 5 | Consumers | ✓ | ✓ | 3 adapter services (Expo/Discord/WebPush) + Inbox (imperative-only) |
| 6 | Persistence | partial | ✓ | HAI + HumanFeedbackRecord + NotificationLog (Web Push subset); needs cross-channel HAIDispatchLog |
| 7 | Notifications | partial | mostly ✓ | 3 channels wire on `critical` urgency floor; Inbox not yet receiver-wired |
| 8 | Frontend updates | ✓ | ✓ | inbox WS + Web Push handler |
| 9 | Human attention | ✓ | ✓ | receiving IS the human-attention moment |
| 10 | Failure modes | ✓ | ✓ | documented + gated via kill switch, quiet hours, urgency floor |
| 11 | Recovery | ✓ | ✓ | Celery retry per task; kill switch to isolate a broken channel |
| 12 | Verification | partial | ✓ | 3 test files exist; `test_hai_webpush_fanout.py` = 410 lines |
| 13 | Existing tests | partial | ✓ | per-channel + shared-gate tests present |
| 14 | Missing links | 4 items claimed | **3 items (S/S-M)** | see §7 |
| 15 | Effort | M | **S-M wrap-up bundle** | see §7 |

**Revised completeness at HEAD: `12 of 15`.** (Prior claims 8/15 or 6/15 both
materially overstated.)

---

## 6. Engineering work deleted because of the discovery

The following work items are **eliminated** from the proposed campaign scope:

| Item | Prior scope | Now |
|---|---|---|
| Author `core/services/notification_fanout_service.py` (`NotificationFanoutService.dispatch(...)`) | Central abstraction to be built. Est. 400-800 LOC. | **Deleted.** Would duplicate the receiver-driven pattern S2735 explicitly ratified. |
| Build `NotificationPreferences` model + migration | New Django model + `makemigrations` cycle | **Deleted.** `HumanPreference` at `models_human_interface.py:268` covers the preference contract with 5 gate fields already in production use. |
| Build cross-channel dedup at service level | Central `_dedup(recipient, source_type, source_id)` in the new service | **Downgraded** to producer-side flag generalization (see §7 Gap 3). |
| Ship Expo adapter | Rigby F2: UNEVIDENCED — assumed net-new | **Deleted.** Adapter + signal + task all shipped in PR #1458 (2026-02-24). |
| Ship Discord adapter | Rigby F2: UNEVIDENCED — assumed net-new | **Deleted.** Shipped PR #3038 (2026-07-09). |
| Ship "HAI adapter" | Rigby F2: UNEVIDENCED — assumed to be built as a fanout target | **Deleted by re-framing.** HAI is the unified event; there is no separate HAI adapter to build. |
| Build channel-preference query surface | Rigby F2: "may need to be built" | **Deleted.** `_pref_gates_pass(user_id, source_type, urgency)` at `signals_discord_notifications.py:106-142` already implements it and is exported for reuse. |
| Add `executor_actor / sponsor_actor / principal_user` fields to `NotificationLog` from day 1 (§21 F6 tightening) | Explicitly warned in the graph as a P0-companion | **Preserved** — moved to §7 Gap 2 in the reduced scope. |

**Aggregate deleted work**: an entire M-L campaign with ~1000+ LOC net-new,
one Django model + migration, and 5+ deliverables.

---

## 7. Remaining work

Three evidence-based gaps remain. All are S / S-M in effort. Aggregate is
**one 1–2 session wrap-up PR bundle**, not a campaign.

### Gap 1 — Inbox `DirectMessage` receiver not wired to HAI post_save (S)

- Today: 7 imperative `DirectMessage.objects.create` sites exist
  (`views_inbox.py:141,165,223`; `td_handlers_core.py:3830`;
  `user_onboarding_service.py:123,209`; `employees/comms.py:343`), but
  **no `signals_inbox_notifications.py`** — so Inbox receives 0 HAI-driven
  fanout dispatches today.
- Fix: one `signals_inbox_notifications.py` following the exact shape of
  `signals_discord_notifications.py`. Add one Celery task
  `notify_hai_inbox` in `tasks_push_notifications.py`. Add settings kill
  switch `HAI_INBOX_DISPATCH_ENABLED`. Add per-channel test file.
- Effort: **S**.

### Gap 2 — Cross-channel HAI dispatch audit table (S-M)

- Today: `NotificationLog` at `models_push_notifications.py:183` is FK'd to
  `PushSubscription` and enum-scoped to Web-Push-era types (`arb / line_move
  / game_start / bet_result / system`). It cannot audit Discord or Expo
  fanout dispatches. No cross-channel observability today.
- Fix: one new `HAIDispatchLog(user, source_type, source_id, channel,
  dispatched_at, status, error_message, executor_actor, sponsor_actor,
  principal_user)` model. Preserve F6 identity-carriage from graph §21 F6
  from day 1. Write from each of the 3 (later 4) Celery tasks after adapter
  call completes.
- Effort: **S-M** (model + migration + 4 write-sites + basic queries).

### Gap 3 — Formalize `payload['channels_fired']` list convention (S)

- Today: `payload['discord_sent']=True` is Discord-specific and only used
  by `BodyCoordinator._handle_digestive_blocked` and `heart.alert_if_critical`.
  Expo + Web Push have no equivalent producer-side dedup flag.
- Fix: one shared helper `payload_mark_channel_fired(payload, channel)` +
  `payload_has_channel_fired(payload, channel)` producing/consuming a
  canonical `payload['channels_fired']=['discord', ...]` list. Update the
  3 shipped receivers to check the generalized flag. Update the docstring
  boilerplate + the 2 producers using the old flag.
- Effort: **S**.

**Aggregate remaining scope**: 1–2 sessions of engineering, not a campaign.

---

## 8. Whether the Capability Graph should be updated

**Yes — targeted append-only update.** Rationale per playbook §14 append-only
discipline (from prior arc-close audits): don't rewrite §16 body in place;
append a §16-update block referencing this CDR.

### 8.1 Updates the Graph must absorb

- **§16 Item 4 (Score)** — update from `6 of 15 with tracked uncertainty`
  (§23 F2) → `12 of 15` (this CDR §5).
- **§16 Item 14 (Missing links)** — replace the four-item list ("(a) user-
  pref lookup, (b) dedup, (c) N adapter calls, (d) NotificationLog audit")
  with the three-item list from §7 of this CDR.
- **§16 Item 15 (Effort)** — update from `M (unification service is the
  whole thing)` → `S-M wrap-up bundle`.
- **§16 Item 6 (Persistence)** — call out the `NotificationLog` sports-scope
  limitation and preserve the graph §21 F6 identity-carriage prerequisite
  as attached to Gap 2 only.
- **§20 Tier A** — remove §16 from Tier A ("HIGHEST leverage") — actual
  remaining scope is Tier B or wrap-up.
- **§21 recommendation** — the Rigby F3 sequence-revision is stale. §16 is
  no longer "second chain blocked on discovery pass"; it's a small wrap-up
  bundle. The graph should now recommend a different chain (candidates:
  §12 Knowledge Retrieval, §17 P2 Cost Protection, §18 Auth full scope; see
  campaign selection process in-flight this session).

### 8.2 Meta-update the Graph should absorb

The receiver-driven fanout pattern — `post_save` on a unified event model +
`transaction.on_commit` + Celery task + re-load + re-gate — is now the
platform's **canonical fanout shape**. It should be named and documented
in the Graph as a first-class pattern, referenced from any chain that
proposes fan-out. This CDR §2.3 is the reference implementation.

### 8.3 Governance guardrail from this discovery (proposed input to Playbook v0.1.1)

The Rigby SIGN §23 F2 refinement was itself Category A discipline —
attempting to evidence Claude's original score. But the F2 grep was too
narrow: pattern `expo push` (space) missed `signals_push_notifications.py`,
and "not spot-checked" was recorded verbatim rather than expanded to a
proper grep. **This CDR is the second-pass refinement F5 explicitly owed
per graph §23 F5.** Playbook v0.1.1 methodology chapter should codify:
Category A discovery findings that leave "UNEVIDENCED" or "not spot-checked"
in the artifact MUST be revisited before campaign ratification — a
sub-refinement is not a discharge.

---

## 9. Ratification path

1. **Chris ratifies** this CDR (or amends). No engineering proceeds before
   ratification per Chris directive 2026-07-09.
2. **Rigby independent Category A** — fresh SIGN pin, dispatched with this
   CDR as the anchor. Rigby runs her own grep pass and returns a matching
   or differing verdict. Reconciliation happens here.
3. **Capability Graph update PR** — append-only §16 update block +
   canonical fanout pattern section, referencing CDR-001 as authority.
4. **Wrap-up PR bundle** — Gap 1 + Gap 2 + Gap 3 as three linked but
   independently-verifiable PRs. Not a campaign. Queued behind the next
   campaign selection (§12 Knowledge Retrieval is my current pick;
   awaiting reconciliation with Rigby).
5. **Ledger entry** — this CDR referenced in the next handoff and in the
   OPEN_ARCS manifest as the first formal CDR (CDR-001).

---

## 10. Scope of this document

This CDR does not propose any code. It does not select the next campaign.
It documents why the previously-proposed campaign (Candidate A — Unified
Notification & Attention Fabric) is materially disqualified and reduced to
a wrap-up bundle. Campaign selection continues in a separate track and
depends on this discovery being ratified first.

---

## 11. Lessons Learned

**This section is permanent to every Capability Discovery Record.** It exists
to convert each CDR into an improvement to the Engineering Operating System
itself, not just a per-campaign audit trail. Future CDRs replicate this
section; the platform's methodology gets sharper every time a Category A
investigation runs.

### 11.1 Methodology improvements resulting from this discovery

- **Capability Graphs are hypotheses, not implementation truth.** The graph
  is a planning document produced from research and cross-referencing; the
  repository is the only source of truth about what capability exists.
  Treating a graph score as a fact leads to campaigns that reorganize code
  instead of adding capability.
- **Category A investigations exist to invalidate engineering assumptions
  before coding.** The purpose of Category A is not to confirm the plan —
  it is to try, in good faith and with evidence-first discipline, to break
  the plan. A Category A run that produces no invalidations should be
  re-run with wider grep patterns; a run that produces invalidations is
  working correctly.
- **Existing substrate takes precedence over proposed architecture.** When
  ~80% of the intended behavior already lives in shipped code, the
  engineering path is extension of the existing substrate — not a parallel
  abstraction. Parallel abstractions create dual sources of truth and
  become the substrate the next CDR has to reconcile.
- **If repository evidence contradicts the graph, update the graph instead
  of forcing the repository toward the graph.** The graph is cheap to
  amend; the repository is expensive to bend. Amendments to the graph must
  be append-only per playbook §14 discipline, so prior scoring assumptions
  remain auditable while HEAD evidence takes precedence.
- **Future campaign selection should consume prior CDRs before proposing
  engineering work.** A campaign candidate that would recreate a
  capability already documented as existing in a prior CDR is a category
  error. Campaign selection reads the CDR index first, the Capability
  Graph second, and the repository third — because that is the order of
  freshness (CDRs are the newest ratified truth, the graph is a
  point-in-time hypothesis, the repository is the ground state).

### 11.2 Meta-lessons about the Engineering Operating System

These lessons apply not just to Notification Fanout but to how the EOS
itself operates:

- **The Category A checklist is now a governance gate, not a suggestion.**
  Chris's 5-question checklist (exists-under-different-name? / 80-90%
  substrate? / new abstraction vs extension? / smallest change largest
  capability? / real increase or reorg?) is the ratified pre-campaign
  contract. Any proposed campaign that would fail one of the 5 questions
  requires a CDR before proceeding.
- **Rigby SIGN refinements are themselves subject to Category A discipline.**
  Rigby's F2 pass at the graph draft was itself a form of Category A
  review, but the grep patterns were too narrow. A sub-refinement that
  ends "UNEVIDENCED" or "not spot-checked" is a debt, not a discharge —
  it must be revisited before campaign ratification. (Proposed input to
  Playbook v0.1.1 methodology chapter; see §8.3.)
- **CDR-numbered records form a permanent ledger.** CDR-001 is this
  document. CDR-002 will be the next Category A investigation that
  materially changes campaign scope. The numbering is monotonic, the
  format is stable, and the §11 section is permanent — so the EOS
  accumulates methodology fixes over time rather than losing them at
  session close.
- **A CDR is the correct primitive for "we were about to build the wrong
  thing."** Handoffs record what was shipped; ADRs record what was
  decided; the Playbook records how work is done; CDRs record why a
  campaign changed shape before engineering started. Each artifact has a
  distinct role; CDRs fill the gap between "investigation" and
  "implementation" that previously had no home.

### 11.3 Concrete carry-forward from CDR-001 specifically

- The receiver-driven fanout pattern (post_save on unified event → 
  transaction.on_commit → Celery task → re-load + re-gate → adapter) is
  named as the platform's canonical fanout shape. Any future chain
  proposing "fan-out" reads this pattern first.
- The `_pref_gates_pass` shared-gate helper is a reference implementation
  for cross-adapter preference gating. Copy the shape, don't reinvent.
- `HumanAttentionItem` is the platform's unified human-attention event.
  Producers create through `HumanInterfaceService.create_attention_item`;
  channels receive on `post_save`. Proposals to introduce a new "unified
  notification event" model must first justify why HAI is insufficient.

---

**End of CDR-001.**

**Ratified by Chris 2026-07-09.** §11 Lessons Learned added at ratification
per Chris directive: "That turns every CDR into an improvement to the
Engineering Operating System itself." Next action: dispatch this CDR to
Rigby via fresh SIGN pin for independent Category A reconciliation.

---

## 12. Rigby SIGN-with-refinements reconciliation (append-only per playbook §14)

Fresh SIGN pin minted 2026-07-09: **`pa-821c1ae4efd3400b`** (title
`cdr-001-cat-a-reconciliation`, description "Independent Category A pass on
§16 Notification Fanout — reconciling CDR-001 findings"). Dispatched via
prior wrapper conversation `pa-88e3f4c934694408`. §1–§11 preserved verbatim.

### 12.1 Question-by-question verdict

| # | Question dispatched | Rigby verdict | Evidence / refinement |
|---|---|---|---|
| Q1 | Does `signals_push_notifications.on_critical_attention_item` fire on `HumanAttentionItem.urgency='critical'`? | **SIGN-CONFIRMED** | `core/signals_push_notifications.py:14-24` gates `created=True` + `urgency=='critical'` and enqueues `notify_critical_attention_item.delay(...)`. |
| Q2 | Does `HumanPreference` carry the 5 gate fields listed? | **SIGN-WITH-REFINEMENTS** | Present at `core/models_human_interface.py:295-307,320` but field is named `min_urgency_to_notify` (not the `min_urgency` shorthand used in the dispatch summary — the CDR body §2.2 uses the correct name). |
| Q3 | Does `signals_discord_notifications.py:12-24` actually reject a `NotificationFanoutService`? | **SIGN-CONFIRMED** | Docstring lines 16-24 verbatim: "No new fanout service…" / "NO new architecture beyond one signal receiver + one Celery task." |
| Q4 | Are the 3 gaps in §7 the ONLY remaining §16 gaps? | **SIGN-WITH-REFINEMENTS** | 3 gaps confirmed real (no repo hits for `HAIDispatchLog` or `channels_fired`), but "ONLY" is too strong. **Fourth item identified:** cross-channel dedupe/dispatch contract normalization. The `payload['discord_sent']=True` shipped dedupe contract (`signals_discord_notifications.py:52-56`, tests at `test_hai_discord_fanout.py:31-33`) is Discord-specific; generalizing the *contract shape* (not just the flag rename to `channels_fired`) is a distinct §16 completeness item beyond Gap 3 as originally scoped. |
| Q5 | Append-only §16 update per playbook §14, or v2 rewrite? | **SIGN-CONFIRMED** | Append-only, dated correction block citing CDR-001 as authority. |

### 12.2 Refinements folded into the CDR

- **Q2** — Field-name shorthand `min_urgency` used in the dispatch text. The
  CDR body §2.2 already uses the correct `min_urgency_to_notify`; no body
  edit required. Recorded here for future dispatch language hygiene.
- **Q4** — Added as **Gap 4** to the remaining-work list. Sits alongside
  §7 Gap 3 but distinct: Gap 3 renames the flag convention;
  Gap 4 canonizes the *cross-channel dispatch contract* (what does "this
  channel already fired for this HAI" mean semantically, not just how
  producers spell it).

### 12.3 Rigby's Gap 4 — Cross-channel dedupe/dispatch contract normalization (S-M)

- Today: `payload['discord_sent']=True` dedupe is Discord-specific and tested
  in isolation. There is no ratified contract for what "already-fired" means
  across channels — e.g., does firing Discord + Web Push for the same HAI
  count as one dispatch or two? Should a producer that fires imperative
  Discord AND wants Web Push also fire, or is Discord-first a
  suppress-all-others gate?
- Fix: one short contract doc (or CDR-002 if it requires investigation) plus
  a shared helper `payload_channel_dispatch_state(payload, channel)` that
  returns `NOT_ATTEMPTED / SUCCEEDED / FAILED / SUPPRESSED_BY_PRODUCER`,
  producing a canonical `payload['channel_dispatch_state']=dict` map.
  Consumers of Gap 3's `channels_fired` list migrate to reading this map.
- Effort: **S-M** (contract + helper + 3 receiver migrations + 1 test suite
  covering the 4×3 = 12 producer/channel state combinations).

### 12.4 Bottom-line reconciliation

- **CDR-001 core finding held.** Rigby independently confirmed the
  reorganization-vs-capability-increase verdict on Candidate A.
- **§16 remaining scope grows from 3 items to 4 items** (add Gap 4). Total
  effort remains bounded — still a wrap-up PR bundle, not a campaign.
  Aggregate revised estimate: **1–2 sessions** (unchanged; Gap 4 fits in
  the S-M envelope).
- **§12 Knowledge Retrieval pivot ratified with refinement.** Rigby agrees
  §12 is the correct next-campaign pivot for greatest capability jump,
  provided it is framed as **additive capability** (turn-context
  enrichment + lane selector) **with clear acceptance tests written first**
  to prevent recurrence of the "assumed gap" failure mode this CDR
  corrected on §16. Chris will see this framing in the next-campaign
  workspace deliverable.

### 12.5 New §11.2 EOS lesson candidate from Rigby's Q4 refinement

Rigby's Q4 refinement is itself an instance of a §11.2 lesson: even a
Category A investigation can inherit its own too-narrow framing. My
initial Gap 3 conflated "spell the flag differently" with "canonize the
contract"; Rigby's second-pass grep on `discord_sent` (18 files across
5+ models, 4 migrations) surfaced that the shipped dedupe contract has
already accreted meaning beyond a single flag rename. **Proposed input
to Playbook v0.1.1 methodology chapter, extending §11.2's fourth bullet:**
"When a CDR proposes a rename or convention change, the reconciliation
partner should specifically test whether the affected symbol has
accreted contract semantics beyond the surface change. If so, split
the rename item from the contract-canonization item so the two can
land independently."

---

**End of CDR-001, post-Rigby-SIGN-reconciliation.** No engineering
proceeds until the next-campaign workspace deliverable is drafted,
Chris ratifies §12 Knowledge Retrieval as the campaign pick, and a
workspace record is opened.
