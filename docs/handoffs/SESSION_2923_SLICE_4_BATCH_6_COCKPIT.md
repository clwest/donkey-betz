# Session 2923 — Slice 4 batch 6 (cockpit solo — first `external` PRIMARY + latent-cascade authoring pattern)

**Session:** S2923
**Date:** 2026-07-23
**HEAD at open:** `2161c47a4`
**HEAD at close:** `183d1eeef`
**Ship PR:** [u-d-b #3476](https://github.com/clwest/donkey-betz-platform/pull/3476) merged at `183d1eeef`.
**Wrapper pin at open:** `pa-e3b8a120b81d46f9` (bumped at S2922 close cascade).

---

## What shipped

**1 tool CLOSED** — Slice 4 `td_handlers_gateway`: **15/17** shipped (from 14/17 post-S2922).

- **cockpit_tool** (8 actions: help + beat_schedule + task_status + worker_health + recent_failures + queue_lengths + trigger_task + revoke_task) — handler 431 lines at `td_handlers_gateway.py:1022`; schema at `pa_tool_schemas.py:4562`; register at `tool_dispatcher.py:571`. Category upgrade: `untested` → `validated_full`.

Doc: `docs/research/tools/validation/cockpit_tool_validation.md` (426 lines authored — sweep variant, v1 template compliance ✓).

---

## Reclassification — S2922 pre-classified `cascading`, S2923 corrected to `external` PRIMARY

**Substrate correction (T0/T1 Rigby SIGN + Claude independent grep):**

The S2922 close 00-START pre-labeled cockpit as first Slice-4 `cascading` example based on the FAILURE_CLUSTER dynamic-connect discovery in the S2922 close cascade. During S2923 authoring, handler-line-range re-verification surfaced two issues:

1. S2922 close 00-START referenced `CeleryTaskEvent.save at 1030-1039` — this is the help-payload text return (`'tool': 'cockpit_tool'` self-reference literal at line 1030), NOT a save.
2. Actual mutation sites in cockpit are:
   - `trigger_task` at line 1367–1372: `CeleryTaskEvent.objects.create(status='QUEUED')` — status NOT `'FAILURE'`.
   - `revoke_task` at line 1420–1421: `event.save(update_fields=['status'])` with `status='REVOKED'` — status NOT `'FAILURE'`.
3. The gate at `failure_cluster_signals.py:141`: `if status != 'FAILURE': return` — cockpit's mutations FIRE the signal but hit the early-return gate.

**Corrected classification (both mutation actions):**
- **`external` PRIMARY** (Celery `send_task` fan-out + `control.revoke` broadcast + Redis I/O — leaves the process; highest-tier blast-radius reached).
- **`cascading` documented as gate-exempt side-effect** with 5 explicit reclassify triggers enumerated (any future FAILURE-status write path in cockpit / gate literal change / kill-switch semantics change / new @receiver or .connect on CeleryTaskEvent that accepts QUEUED-or-REVOKED / new dispatcher-re-entry site inside allowlisted tasks).

**New §5a authoring convention (doc-level, not template-level) — codified at S2923 T1 Rigby SIGN Q5(ii) AGREE:** for tools with latent-but-gated signal cascades, use "gate-quoted + reclassify-trigger enumerated" pattern. Cockpit's §5a is the reference exemplar. Not an unconditional "external always beats cascading" rule — guardrail preserved that classification is EFFECT-based, not merely wiring-based.

---

## Rigby SIGN discipline (3-turn cycle, zero rubber-stamp)

**T0 SIGN** (9 `repo_tool` receipts):
- Q1 AGREE cockpit solo over trio/pair alternatives — first `cascading` (later corrected to `external`) exercise cleanly.
- Q2 first-hop-literal per-tool grep: confirmed cockpit line 1030 SELF-reference is help-payload, not outbound dispatch; gateway-wide count now 1/17 post-batch (first substantive Appendix A tool).
- Q3 full cascading-tier signal-chain trace line-by-line: `escalate_failure_cluster` at `:123` → `transaction.on_commit(_dispatch(snapshot))` at `:173` → `attention_bridge.create_failure_cluster_attention` → `HumanInterfaceService.create_attention_item(source_type='failure_cluster')` → `HumanAttentionItem` inbox row. Dedup: two-key OR (`idempotency_key` OR `(task_name, urgency_band)`) inside 30-min window; fails safe to `False` on lookup error → allows escalation (documented preference for false-positive over swallowed critical).
- Q4 proactive + profile spreading pre-audit: confirmed both are `spreading` (no signal receivers, no `.connect(`, no `transaction.on_commit` dispatch chain in handler regions); direct ORM writes only. Batch 7 shape confirmed as spreading pair.
- Q5 zoom-out: Slice 4 close horizon S2924 reasonable; legacy-error refresh keep deferred; orm_inspect_tool allowlist gap = Slice-4-close engineering follow-up; combined-pattern grep mandate NOW for latent-cascade classification (don't wait for 2nd instance).

**T1 SIGN** (grep-grounded reclassification + Appendix A A4 spot-check, 9 total tool_runs):
- Q1 AGREE reclassification `external` PRIMARY over `cascading` PRIMARY. All 5 grounding claims confirmed via `repo_tool.read_file` at handler + signal file spans.
- Q2 AGREE 11-item ALLOWED_TASKS enumeration matches. Spot-checked `content_autonomy_loop` + `generate_self_blog_deliberation_task` both have `BudgetAwareScheduler().preflight(...)` in implementations.
- Q3 AGREE HAI non-fire ORM query shape (with caveat: `payload__task_name` predicate assumes attention_bridge stores task_name at top level of payload; fallback to `payload__icontains` if key path shifts).
- Q4 AGREE 1/17 first-hop-literal gateway count shift.
- Q5 zoom-out feedback: (i) `check_content_diversity` UNSAFE for verify target (auto-creates content — verified via `_impl_check_content_diversity` grep at `core/tasks_misc.py:3488-3503`, ContentDiversityOrchestrator.execute); (ii) codify "gate-quoted + reclassify-trigger enumerated" as doc-level rationale-writing pattern with guardrails (require quoted gate + status literals + registration mechanism + reclassify triggers); (iii) reclassification substrate creates maintenance tripwire (relies on negative: signal doesn't fire) — mitigate via prominent latent-cascade callout + explicit reclassify-trigger recheck in verify.

**T2 SIGN confirmation** (post-amendments AGREE Q1 + Q2):
- Amendments applied: (a) bold "⚠ Latent cascade exists on `CeleryTaskEvent`, currently gated" callout at top of §5a with gate literal + status literals + reclassify hook; (b) 5 explicit reclassify triggers enumerated at end of §5a; (c) `check_content_diversity` swapped for `run_body_system_check` as verify target with note that none of the 11 ALLOWED_TASKS are truly no-op safe; (d) verify §6 step 8 latent-cascade probe (DEV-LOCAL ONLY + tagged task_name `__s2923_cockpit_probe__` per Rigby optional nicety).
- Ready for gap-map regen + PR ship.

**Claude independent verification:**
- Verified cockpit handler starts at line 1022 (matches Rigby claim).
- Verified `escalate_failure_cluster` at `failure_cluster_signals.py:123` + `transaction.on_commit` at `:173` + `.connect()` at `:183-189` (matches Rigby claims).
- Verified `core/apps.py:234-235` calls `connect_failure_cluster_signals()` at startup (matches Rigby claims).
- Verified `check_content_diversity` unsafe: `ContentDiversityOrchestrator.execute` auto-creates content per `_impl_check_content_diversity` at `core/tasks_misc.py:3488-3503`.

---

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- PR #3476 recycled clean at `sha=183d1eeef`: 5 fresh workers + beat, zero surviving old PIDs. `[emit_recycle_event] clean recycle recorded (sha=183d1eeef, surviving=none)`.

**Rigby dispatch results (8/8 PASS):**

| Action | Result | Envelope highlights |
|---|---|---|
| `help` | PASS | 7-action inventory returned |
| `beat_schedule` (limit=5) | PASS shape | `total=99`, first entry `aggregate-roi-metrics-daily` |
| `worker_health` | PASS | 4 workers reported post-recycle |
| `recent_failures` | PASS | count=1 (`claude_code_engineer_task` FAILURE from 2026-07-10) |
| `queue_lengths` | PASS | `overall_state=GREEN` across 8 allowlisted queues |
| `task_status` | PASS | `source='celery_event'` for known recent failure task_id |
| `trigger_task` (run_body_system_check) | PASS | `task_id=12096db8-ca85-4b26-a49d-a28263b65690`, `status='dispatched'` |
| `revoke_task` | PASS | `revoked=true` (broker-level acknowledgment, may race with worker pickup) |

**Rigby-blocked ORM checks (Ledger #31 recurrence — orm_inspect_tool allowlist gap):**
- `PeriodicTask` / `CeleryTaskEvent` / `HumanAttentionItem` all missing from `orm_inspect_tool` allowlist; blocked ORM cross-checks for steps 2 (PeriodicTask ordering) + 6 (recent CeleryTaskEvent selection) + HAI non-fire check.
- Handled by Claude direct via `python manage.py shell`.

**Claude direct ORM verifications:**
1. **HAI cascade non-fire from cockpit mutations: PASS.** `HumanAttentionItem.objects.filter(source_type='failure_cluster', created_at__gte=<10min ago>).count() = 0` post trigger_task + revoke_task. Confirms cockpit's own mutations do not fire the cascade.
2. **Receiver-wired verification: PASS.** `[FAILURE_CLUSTER_SIGNALS] receiver wired on CeleryTaskEvent.post_save (dedup_window_min=30)` line present in `celery.log` + `celery-long-running.log` at recycle time (both workers).
3. **Latent-cascade probe (scratch FAILURE row): PARTIAL — receiver-wired confirmed but cascade correctly blocked by threshold gate.** Single-row `CeleryTaskEvent(status='FAILURE', task_name='__s2923_cockpit_probe__')` insert did NOT create HAI. Reason: `compute_cluster(task_name)` in `escalate_failure_cluster` returns `snapshot.exceeds_threshold=False` for isolated single-row inserts (threshold is 5 distinct task_ids for 'high' urgency, 15 for 'critical' per `apps.py:227-228`). Cleanup completed.

**Doc-authoring gap surfaced by verify:** doc §6 step 8 was authored assuming single-row FAILURE would fire the cascade. This is inaccurate — receiver runs but threshold gate returns early. Step 8 in current form cannot distinguish "receiver not wired" from "receiver wired + threshold-gated"; both produce zero HAI. Recorded as close-cascade follow-up doc-fix candidate + Ledger row (not a re-open of this ship).

---

## Ledger updates + candidates

**Rigby Tool Gap Ledger updates (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`):**

- **Entry #31 (MEDIUM — orm_inspect_tool allowlist gap) — SEVERITY NOTE BUMP.** Now blocks post-merge verification across MULTIPLE Slice 4 tools. Additional required read-only models to add to allowlist:
  - `CeleryTaskEvent` (blocked step 6 + step 8 verify)
  - `PeriodicTask` (blocked step 2 verify)
  - `HumanAttentionItem` (blocked cascade non-fire check)
  - (Retains S2922 note: VIPInvite + User for vip_invite verify.)
  Impact: post-merge verify for Slice 4 spreading + external tier tools requires Claude-side ORM shell drops → fragmenting the "Rigby exercises tool surface" post-merge contract. Expansion should be Slice-4-close engineering item (recorded as engineering-backlog deliverable candidate; not open now).

- **NEW Ledger candidate (post-S2923 close):** doc §6 step 8 latent-cascade probe as-authored is not a valid `external` classification test — threshold and dedup gates block observable cascade for isolated single-row inserts. Correct verify pattern for "receiver-wired" check = startup init log-line grep (`[FAILURE_CLUSTER_SIGNALS] receiver wired ...`) + threshold-exceeding batch of ≥5 tagged FAILURE rows for "cascade path fires when threshold met." Fold candidate at 1st instance — post-close follow-up for cockpit doc amendment.

- **NEW Fold candidate (post-S2923 close — 1st observation):** verify-protocol authoring SIGN checkpoint — "what negative result would this test fail to detect?" should become a SIGN verify-protocol authoring question. Would have caught the step 8 authoring gap at T0/T1. Recorded for 2nd-instance evaluation.

**Doc-in-tree Ledger entries recorded (in cockpit_tool_validation.md §Related):**
- Legacy-error envelope 19th corroborating instance (dispatcher backfill at `tool_dispatcher.py:862-885`; still Chris-gated post-D6).
- First Slice-4 exercise of §5a `external` PRIMARY tier (first tool with substantive Appendix A — Async-Fanout section authored substantively for the first time in Slice 4; gateway-wide first-hop-literal count 0/17 → 1/17).
- First tool where signal wiring exists on mutation-target model + gate exempts tool's mutation shape — nuanced rationale-authoring pattern (1st observation).
- S2922 close 00-START pre-classification correction — handler-line-range re-verification value.
- Cockpit cross-reference proxy pattern (`td_handlers_ops.py:295-296` + `:905-914` proxy into `_handle_cockpit` — intentional composition, not dispatcher re-entry; 1st observation in-sweep).
- 11-item ALLOWED_TASKS audit surface (recorded for future PR review — any addition expands cockpit's downstream reach).
- 00-START span-math regen 3rd time (cockpit 431 lines matched between S2922 close 00-START pre-count + this ship's re-count; Rigby Q5(ii) permanent close-ceremony step per S2922 AGREE now validated on 3 consecutive sessions — self_awareness S2921 batch 4 + podcast S2922 batch 5 + cockpit S2923 batch 6).

---

## Sweep progress (post-S2923)

- **Slice 4 (`td_handlers_gateway`): 15/17 shipped.**
- Remaining 2 (both pre-audited this session as `spreading`):
  - **proactive** — handler 1560–1699 = 140 lines. `spreading` (ProactiveNotification.filter(...).update() for mark_read/bulk_ack/dismiss; bulk_ack capped at 200 rows).
  - **profile** — handler 2294–2481 = 188 lines. `spreading` (EnhancedUserProfile get_or_create × 2 + save × 1 for profile/update_preferences).
- Total corpus untested: 33 → **32** post-S2923 (cockpit shift).
- Gap map: **67 full · 10 partial · 7 unknown · 32 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).
- Session cumulative pace: 1 tool / 1 session (single-tool batch matching S2921 self_awareness pilot precedent; reclassification substrate + latent-cascade authoring pattern shipped alongside).

---

## S2924 open queue

Batch 7 = final Slice 4 batch. Composition:
- **proactive + profile spreading pair** — both pre-audited this session; symmetric `spreading` tier exercises; matches S2922 batch 5 mixed-pair success. Slice 4 CLOSES at S2924.

Alternatives:
- **Doc-only cockpit §6 step 8 amendment** (threshold-aware probe reframing + startup log-line grep as receiver-wired check). Small; could ship alongside batch 7 or as its own tiny doc-fix PR.
- **orm_inspect_tool allowlist expansion** — engineering task from bumped Ledger #31. Not a sweep item; unblocks post-merge ORM verify for batch 7 tools. Slice-4-close engineering candidate.

---

## Full doc pointers

- **Ship doc:** `docs/research/tools/validation/cockpit_tool_validation.md`
- **Auto-generated gap map:** `docs/audits/PA_TOOLS_GAP_MAP.md`
- **Auto-generated audit md:** `docs/PA_TOOL_AUDIT.md`
- **Template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a 4-tier taxonomy from S2921 — unchanged this ship; cockpit's §5a authoring convention is doc-level, not template-level)
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #31 severity bumped this session)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
