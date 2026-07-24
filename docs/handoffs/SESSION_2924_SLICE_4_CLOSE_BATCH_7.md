# Session 2924 — Slice 4 batch 7 (proactive + profile spreading pair — CLOSES Slice 4 at 17/17)

**Session:** S2924
**Date:** 2026-07-23
**HEAD at open:** `1706952e6`
**HEAD at close:** filled in post-merge of the close-cascade PR (below)
**Ship PRs:**
- [u-d-b #3478](https://github.com/clwest/donkey-betz-platform/pull/3478) — cockpit doc §6 step 8 threshold-aware reframing (standalone tiny doc-fix), merged at `592f72214`.
- [u-d-b #3479](https://github.com/clwest/donkey-betz-platform/pull/3479) — Slice 4 batch 7 proactive+profile validated_full, merged at `2fc8c66ae`.
- u-d-b PR `<TBD>` — S2924 close cascade (this handoff + 00-START refresh + wrapper pin bump + Ledger #33 add via Rigby + profile doc dev-env note + Slice 4 close artifact).
**Wrapper pin at open:** `pa-fb4d19205921420c` (bumped at S2923 close cascade).
**Wrapper pin at close:** `pa-a5fee83d2afb4932` (S2925-fresh, via `session_lifecycle close --label s2924-slice-4-close-batch-7` at 2026-07-23 21:38).

---

## What shipped

**Slice 4 CLOSED at 17/17.** Two tools shipped this session (batch 7 final pair) + one tiny doc-fix PR (cockpit §6 step 8) preceding batch 7.

**Tools shipped this session:**
- **proactive_tool** (8 actions: dashboard/alerts/notifications/suggestions/automations/mark_read/bulk_ack/dismiss) — handler 140 lines at `td_handlers_gateway.py:1560`; schema at `pa_tool_schemas.py:4718`; register at `tool_dispatcher.py:580`. Category upgrade: `untested` → `validated_full`. §5a: `spreading` × 3 mutations (bulk_ack row-count reach up to 200; mark_read + dismiss cross-user reach via missing user_id predicate).
- **profile_tool** (6 actions: profile/skills/learning_summary/preferences/update_preferences/desk_preferences) — handler 188 lines at `td_handlers_gateway.py:2294`; schema at `pa_tool_schemas.py:4960`. Category upgrade: `untested` → `validated_full`. §5a: `spreading` × 2 (`preferences` implicit `get_or_create` first-touch; `update_preferences` explicit `.save()`; both USER-SCOPED via explicit `User.objects.filter(id=user_id).first()` gate — clean archetype vs proactive's gap archetype).

Docs authored: `docs/research/tools/validation/proactive_tool_validation.md` (178 lines) + `docs/research/tools/validation/profile_tool_validation.md` (187 lines + dev-env drift amendment in this close cascade).

**Also shipped:** cockpit_tool_validation.md §6 step 8 threshold-aware reframing per S2923 post-close doc-fix candidate + S2924 Q4 (b) standalone-PR ratification. Substep A = receiver-wired via startup log grep (immediate); Substep B = ≥5-tagged-FAILURE-rows probe for gate-mechanics re-verify (optional).

---

## Rigby SIGN discipline (T0 SIGN — grep-grounded joint recommendation, zero rubber-stamp)

**T0 SIGN** (10 `repo_tool` receipts):
- Q1 AGREE (a) proactive + profile spreading pair. Handler blocks read at HEAD 1706952e6.
- Q2 AGREE 0 first-hop-literal additions for both tools; gateway-wide count stays 1/17 post-Slice-4. Honest caveat: could not independently confirm gateway-wide count without registry (`first-hop-literal` grep returned 0 matches). Signable: these two tools don't increment.
- **Q3 DISAGREE with Claude's initial 00-START rationale (real correction, not rubber-stamp):** proactive mutations are NOT uniformly user-scoped. Line-by-line grep evidence:
  - `mark_read` at :1660: `ProactiveNotification.objects.filter(id=notif_id, is_read=False).update(is_read=True)` — NO `user_id` predicate. Cross-user reach possible.
  - `bulk_ack` at :1668-1670: `qs = ProactiveNotification.objects.filter(is_read=False)` then `if user_id: qs = qs.filter(user_id=user_id)` — CONDITIONAL. When `user_id` falsy, acks up to 200 GLOBAL unread notifs.
  - `dismiss` at :1688: `ProactiveNotification.objects.filter(id=notif_id).update(...)` — NO `user_id` predicate + NO `is_read=False` guard.
  - Profile is clean: `User.objects.filter(id=user_id).first()` gate at :2361/:2390/:2431 — returns `{error: 'No user context'}` when `user_id` absent.
  - Claude adopted correction; §5a rationale tightened to "spreading, user-scoping conditional; multi-tenant hardening deferred" per Ledger row. Absorbed by `project_single_user_pre_prod_operating_context`.
- Q4 AGREE (b) cockpit doc §6 step 8 fix as standalone tiny PR BEFORE batch 7 (avoids review-scope confusion on the closing batch).
- Q5 zoom-out AGREE all: (i) compact one-table Slice 4 close artifact worth doing; (ii) orm_inspect allowlist defer to Slice 5 (not batch-7 dependency); (iii) legacy-error at 20+ → short "now systemic" note at close; (iv) proactive user-scoping gap is real, incorporable-not-blocking.

**Chris D-verdict:** "ship it" (compact yes-across-all-5-items) after plain-English decision framing with two questions plainly answered (do we lose anything: no; more work later: no) per `feedback_plain_english_decision_framing_for_chris`.

---

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- PR #3479 recycled clean at `sha=2fc8c66ae`: 5 fresh workers + beat, zero surviving old PIDs.

**Rigby dispatch results (11/14 PASS · 2 SKIP · 2 pre-existing dev-env drift):**

| Tool | Action | Result | Notes |
|---|---|---|---|
| proactive | dashboard | PASS | `{unread:0, alerts:0, suggestions:0, automations:0}` |
| proactive | alerts (limit=3) | PASS | `{count:0, alerts:[]}` |
| proactive | notifications (limit=3) | PASS | `{count:0, notifications:[]}` |
| proactive | suggestions (limit=3) | PASS | `{count:0, suggestions:[]}` |
| proactive | automations (limit=3) | PASS | `{count:0, automations:[]}` |
| proactive | mark_read | SKIP | no unread notifs in dev DB to select an id |
| proactive | bulk_ack (max_items=3) | PASS | `{acknowledged:0, filters:{...}}` |
| proactive | dismiss | SKIP | no notifs in dev DB to select an id |
| profile | profile | PASS | non-null profile dict; profile_completeness=0 |
| profile | skills | FAIL (dev-env) | `relation "core_userskill" does not exist` — Ledger #33 |
| profile | learning_summary | FAIL (dev-env) | same UserSkill migration miss — Ledger #33 |
| profile | preferences | PASS | 12 preference fields; time_zone='America/Los_Angeles' captured for restore |
| profile | update_preferences (probe→restore) | PASS | probe set time_zone → probe value → restored |
| profile | desk_preferences (sports) | PASS | correct context + available_desks list |

**Dev-env drift acknowledged:** UserSkill migration not applied to local DB. Not a batch 7 code regression — the code path in td_handlers_gateway.py:2320-2353 is correct and unchanged. Rigby appended **Ledger #33 (LOW)** via `deliverable_tool.append` (1193 chars, receipt confirmed) to Rigby Tool Gap Ledger (deliverable `5c84e75a-...`). profile doc §Covered actions + §6 amended in this close cascade to reflect verify-blocked status pending Ledger #33 resolution.

**Rigby-blocked ORM checks (Ledger #31 continuing):** post-merge ORM cross-checks skipped because Rigby's dev DB is empty for proactive/profile substrate — different from the S2923 orm_inspect_tool allowlist gap. No Ledger #31 severity bump this session.

---

## Slice 4 close artifact — §5a tier distribution table (17 tools)

Compact one-table reference for future Slice-N slice-planning. §5a tier assignment per each mutation action (READ-only tools listed as such — no §5a table needed).

| # | Tool | Batch | Shape | §5a tier(s) | Notes |
|---|---|---|---|---|---|
| 1 | analytics | 1 | READ | — | Pure ORM SELECTs; view-reuse via `stage3_dashboard` |
| 2 | audit | 1 | READ | — | AuditFinding / WiringDefect / CitationViolation reads |
| 3 | campaign | 1 | READ | — | ORM SELECTs, no writes |
| 4 | experiment | 1 | READ | — | A/B test reads |
| 5 | discord | 2 | READ | — | Filesystem-read shape (bot activity introspection) |
| 6 | distribution | 2 | READ | — | Platforms/listings/revenue reads |
| 7 | ats | 2 | READ | — | ATS pipeline reads |
| 8 | narrative | 2 | READ | — | Drift/shifts diagnostics; NarrativeShift reads |
| 9 | mobile | 3 | READ | — | Mobile-app introspection reads |
| 10 | calendar | 3 | READ | — | Content channels/episodes reads |
| 11 | conceptforge | 3 | READ | — | ConceptForge run reads |
| 12 | podcast | 5 | READ | — | Podcast reads (mixed pair with vip_invite) |
| 13 | self_awareness | 4 | READ+MUTATION | `contained` | Pilot for template mutation-shape (S2921 §5a 4-tier amendment shipped alongside); `collect` = single-row `SystemMetrics.create` |
| 14 | vip_invite | 5 | READ+MUTATION×2 | `contained` + `spreading` | `create` contained; `revoke` spreading (cross-table `User.is_active` flip when redeemed) |
| 15 | cockpit | 6 | READ+MUTATION×2 | `external` PRIMARY | First `external` tier; Celery `send_task` + `control.revoke` + Redis leaves process; latent-cascade authoring convention codified doc-level (gate-quoted + reclassify-triggers) |
| 16 | proactive | 7 | READ+MUTATION×3 | `spreading` × 3 | "gap" archetype — bulk_ack row-count reach ≤200; mark_read + dismiss cross-user reach via missing user_id predicate |
| 17 | profile | 7 | READ+MUTATION×2 | `spreading` × 2 | "clean" archetype — `preferences` implicit get_or_create + `update_preferences` explicit save; USER-SCOPED strictly |

**Aggregate:**
- **Read-only:** 12/17 (70.6%)
- **Mutation tools:** 5/17 (29.4%) — 1 `external`, 4 with `spreading` mutations, 2 with `contained` mutations (mix)

**Appendix N (Network-Preflight) count:** 0/17 gateway-wide (no network first-hop across any Slice 4 tool).

**Appendix A (Async-Fanout) — first-hop-literal count:** 1/17 gateway-wide (cockpit's `send_task` + `control.revoke` are the sole first-hop Celery dispatchers).

---

## Legacy-error envelope threshold-crossed short note

**Status:** 21 corroborating instances of the unmigrated-handler pattern (dispatcher-backfill at `tool_dispatcher.py:862-885`). Post-S2923: 19. Batch 7 adds proactive (20th, verified live during `mark_read`/`dismiss` NON-PATH — but the pattern is present in handler; will fire on exception at line 1697) + profile (21st, verified live during `skills` + `learning_summary` which hard-fail with `error_code: 'legacy_error'` due to dev-env drift).

**Threshold-crossed observation:** 20+ instances now systemic across Slice 4. Dispatcher-backfill semantic-nuance refresh (Rigby S2920 Q4(a) proposal: treat `error_code` values as first-class semantics) remains **deferred post-D6** per S2921 Q5(c) Chris ratification. This short note surfaces the threshold crossing per S2924 Q5(iii) AGREE — **NOT** opening the substrate arc; that requires explicit Chris directive per 00-START forbidden-list.

For future evaluation: 21 corroborating instances is sufficient corpus for a Chris-directive-gated design decision on whether to migrate all Slice 4 handlers to emit `error_code` explicitly (removing dispatcher-backfill dependency) OR codify the dispatcher-backfill as permanent semantic layer. Either direction requires post-D6 arc opening.

---

## Ledger updates + candidates

**Rigby Tool Gap Ledger updates (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`):**

- **NEW Entry #33 (LOW) — profile_tool skills + learning_summary dev-env drift (UserSkill migration miss).** Appended by Rigby via `deliverable_tool.append` (1193 chars, 31368 total post-append). Symptom: hard-fail with `relation "core_userskill" does not exist`. Root cause: UserSkill migration not applied to local dev DB. Scope: dev-env only. Fix estimate: ~15 min migration replay. Same shape as S2919 narrative_tool dev-env drift Ledger entry.
- **Entry #31 (MEDIUM — orm_inspect_tool allowlist gap):** unchanged this session (no Slice 5 dependency check yet).

**Doc-in-tree Ledger entries recorded (in proactive_tool_validation.md + profile_tool_validation.md §Related):**

- **Legacy-error envelope 20th (proactive) + 21st (profile) corroborating instances.** Short "now systemic" note surfaced per Q5(iii) Chris ratification. Substrate arc still gated on explicit Chris directive.
- **User-scoping gap on notification-inbox mutations** (proactive) — 1st Slice-4 instance of "mutation-with-scoping-gap" in a user-facing inbox tool. Absorbed by `project_single_user_pre_prod_operating_context`. Recorded as Ledger candidate.
- **`dismiss` observable-idempotency divergence from `mark_read`** — schema-consistency Ledger note. 1st observation.
- **Schema description omits substantive mutation quirk** (proactive) — 2nd instance (1st was vip_invite hardcoded-superuser). Not yet at Fold threshold.
- **`updates` bulk-dict form accepted by handler but absent from schema** (profile) — 1st Slice-4 instance. Ledger candidate; 2nd instance triggers Fold evaluation.
- **`preferences` action implicit first-touch write** (profile) — Ledger candidate: "READ action name with side effect of new-row creation". 1st observation.
- **Error-envelope-shape divergence for `preferences`/`update_preferences`/`desk_preferences`** (profile) — in-shape `{action, error: <str>}` vs standard `{error: <str>}`. 1st Slice-4 instance; Ledger candidate.
- **Silent-drop of unknown fields in `update_preferences`** (profile) — no per-field rejection feedback. Ledger candidate for "silent whitelist filtering" pattern.

---

## Sweep progress (post-S2924 — SLICE 4 CLOSED)

- **Slice 1 (`td_handlers_ops`, 17 registered tools):** UNCHANGED.
- **Slice 2 (`td_handlers_agents`, 25 tools):** CLOSED at S2912.
- **Slice 3 (`td_handlers_core`, 22 tools):** CLOSED at S2917.
- **Slice 4 (`td_handlers_gateway`, 17 tools):** **CLOSED at S2924 (17/17).** Distribution: 12 READ + 5 mutation (1 external, 4 spreading, 2 contained; some tools have multiple mutation actions across tiers).
- **Slice 5 (`tool_dispatcher`, 14 tools):** queued for S2925+.

**Total remaining tools to close:** ~28 (post-S2924).

**Gap map (post-batch-7):** **69 full · 10 partial · 7 unknown · 30 untested** (161 tool names total; 44 agent-via-run_agent + 1 meta-no-handler).

---

## S2925 open queue

**Slice 5 opens.** Tool inventory in `tool_dispatcher.py`:

```bash
grep -oE 'self\.register\("[^"]+"' core/services/tool_dispatcher.py | wc -l
```

Recommendation: composition SIGN cycle with Rigby to size batch 1 shape based on tier-mix in Slice 5 candidates. Slice 5 tools may include cross-cutting dispatch orchestration (retry logic, workspace-scope handlers) which could shift authoring shape compared to Slice 4's per-handler-file organization.

**Also queued (do NOT open unless Chris directs):**
- orm_inspect_tool allowlist expansion (Ledger #31 MEDIUM) — becomes relevant when Slice 5 verify path requires it.
- narrative_tool dev-env drift (Ledger from S2919) + profile skills/learning_summary dev-env drift (Ledger #33 this session) — group both as "dev-env migration drift" engineering slate candidate for a batched fix session.
- Legacy-error envelope 21+ instances — post-D6 substrate arc candidate; requires explicit Chris directive.
- Everything else per 00-START forbidden list.

---

## Full doc pointers

- **Ship docs:**
  - `docs/research/tools/validation/proactive_tool_validation.md`
  - `docs/research/tools/validation/profile_tool_validation.md` (with dev-env drift amendment in this cascade)
  - `docs/research/tools/validation/cockpit_tool_validation.md` (§6 step 8 threshold-aware reframing at #3478)
- **Auto-generated gap map:** `docs/audits/PA_TOOLS_GAP_MAP.md`
- **Auto-generated audit md:** `docs/PA_TOOL_AUDIT.md`
- **Template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a 4-tier taxonomy from S2921 — unchanged this ship)
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #33 added by Rigby this session)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

## Prior handoffs (Slice 4 arc)

- S2918 batch 1: `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- S2919 batch 2: `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- S2920 batch 3: `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- S2921 batch 4: `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
- S2922 batch 5: `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`
- S2923 batch 6: `docs/handoffs/SESSION_2923_SLICE_4_BATCH_6_COCKPIT.md`
- **S2924 batch 7 (this doc):** Slice 4 CLOSED at 17/17.
