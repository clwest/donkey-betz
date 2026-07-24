# Session 2922 — Slice 4 batch 5 (mixed pair: podcast READ + vip_invite spreading mutation)

**Date:** 2026-07-23
**Branch merged:** `s2922-slice-4-batch-5` → `main` at `3078dd48b`
**PR:** [#3474](https://github.com/clwest/donkey-betz-platform/pull/3474)
**Duration:** single session, ~2 hours end-to-end
**HEAD at open:** `5983f5a23` (S2921 close cascade)
**HEAD at close:** `<TBD>` (this session's close cascade)

---

## Executive summary

Slice 4 batch 5 shipped **2** tools per Chris D-verdict on Claude+Rigby joint recommendation (a) mixed batch:

- **`podcast_tool`** — pure-READ, 4 actions in scope (shows/episodes/scripts/stats). 87-line handler body (span 1959–2045). Zero mutation verbs. Auto-classifier upgrades `untested → validated_full`.
- **`vip_invite_tool`** — first Slice-4 exercise of §5a `spreading` blast-radius tier amended S2921. 3 actions in scope (list/create/revoke). `create` classified `contained` (single-row INSERT); `revoke` classified `spreading` (cross-table VIPInvite.revoked_at flip + optional User.is_active flip on redeemed_by).

**Slice 4 progress: 14/17.** Remaining 3: cockpit (431 lines, cascading tier — confirmed via S2922 close-cascade discovery, see below) + proactive (140 lines, spreading) + profile (188 lines, spreading).

Chris D-verdict: **"Yes"** to option (a) mixed batch — no conditions.

Post-merge live verify: 6/8 dispatches clean at ≤16ms (all podcast actions except `scripts` which was skipped for empty data + all vip_invite actions). Second-revoke idempotency guard verified at 8ms with `{"error": "Already revoked", "error_code": "legacy_error"}`. ORM-hard cross-checks partially blocked by `orm_inspect_tool` allowlist gap (VIPInvite + User both absent) — logged as ledger entry #31; envelope-level proxy verification via `vip_invite_tool.list` stands (revoked=true, created_by=chris, redeemed_by=null all confirmed). Cross-table `spreading` full-exercise path not exercisable in dev DB (0 candidate rows via `redeemed_by__isnull=False, revoked_at__isnull=True` proxy through the tool surface); Rigby correctly refused to synthesize a redeemed invite to force the exercise.

---

## Rigby joint SIGN — 2-turn cycle + Q5 zoom-out, zero rubber-stamp

### T0 SIGN turn 1 — batch 5 composition + vip_invite mutation-shape grep

8 `repo_tool` runs (search/read_file/git_info):
- vip_invite handler read (span 941–1018): confirmed mutation shape at HEAD 5983f5a23 — `.create` at 973, `.save` at 1006 (revoke primary), cross-table `.save` at 1009 (redeemed_by.is_active=False flip). Corroborated Rigby's S2921 turn 1 correction to the S2920 close 00-START mutation-verb count.
- Related views file read: `core/views_vip_invite.py` (lines 1–228) — public API mirrors show cross-table flip also at `views_vip_invite.py:196-199`; admin-only decorators confirmed at `27-29, 171-173, 203-205`.
- CeleryTaskEvent model read: `core/models_celery_telemetry.py:17-101` — plain Django model, no signal wiring in the model file itself.
- Repo-wide `@receiver(post_save)` search: 25 signal-registering modules found; **none** reference `CeleryTaskEvent` as sender. Honest caveat preserved: "not formal proof of absence — could be dynamic connect or wiring without decorator." (See post-SIGN discovery below.)

Q1 verdict: **AGREE (a) mixed batch** — vip_invite is smallest cross-table `spreading` archetype; podcast is pure-READ; both fit one small PR.
Q3 verdict: vip_invite = `spreading` tier per §5a taxonomy; both tables (VIPInvite + User) touched; admin-only access verified; in-scope to ship.
Q4 (cockpit pre-audit): likely `spreading` per static-grep evidence — with honest caveat requiring turn 2 dynamic-connect verification.

### T0 SIGN turn 2 — template read + first-hop-literal grep + Q5 zoom-out

13 `repo_tool` runs (search + read_file):
- Podcast handler read (span 1959–2045): confirmed pure-READ, 0/4 mutation verbs. No first-hop-literal outbound tool dispatch. Discovered inline `'tool': 'cockpit_tool'` at `td_handlers_gateway.py:1030` and `'tool': 'narrative_tool'` at `:1462` — both are SELF-references in respective handler help text, NOT outbound dispatches. Gateway-wide first-hop-literal watch remains 0/17.
- Template file read (`_TEMPLATE_per_tool_validation.md` lines 1–320): confirmed §5a as-amended-S2921 accommodates 4-tier taxonomy without further schema change; taxonomy is authoring guidance, not governance requirement (lines 128–136).
- Cockpit dynamic-connect verification: turn 2 grep for `post_save.connect` / dynamic connections truncated in response — 21st tool_run cut off mid-answer.

Q5 zoom-out verdicts:
- **(i) Slice 4 close horizon S2923 vs S2924:** reasonable — cockpit may force S2924 if async fanout / signal-cascade classification requires extra SIGN turn.
- **(ii) 00-START span-math regen** (podcast 251-claim vs 89-actual, 162-line drift caught this session): **PROMOTE to permanent close-ceremony step**, not one-off hygiene rule.
- **(iii) Cascading/external taxonomy tiers unexercised** — **hold for organic emergence**, do NOT force-surface synthetic examples. Template §128–136 frames taxonomy as authoring-only, not governance requirement.
- **(iv) Ledger row 156** (close-ceremony ledger-staleness gate) — **surface at Slice-4 close (S2923–S2924)**, bundle ceremony changes into one closure moment.

### Post-SIGN discovery — dynamic post_save.connect() on CeleryTaskEvent

During `python manage.py build_pa_tool_audit --gap-only` regeneration at close cascade, Django startup logs surfaced:

```
[FAILURE_CLUSTER_SIGNALS] receiver wired on CeleryTaskEvent.post_save (dedup_window_min=30)
```

Located at `core/signals/failure_cluster_signals.py:183`:

```python
post_save.connect(
    escalate_failure_cluster,
    sender=CeleryTaskEvent,
    ...
)
```

This is a **dynamic `.connect()` registration** that Rigby's static `@receiver` decorator grep missed. Fires on FAILURE-status rows only (`dedup_window_min=30`); when it fires, it escalates via `human_attention_bridge` (further downstream reach).

**Impact for batch 6 cockpit classification:** cockpit `CeleryTaskEvent.save()` at `td_handlers_gateway.py:1030-1039` (trigger_task / revoke_task actions) WILL fire this handler if the mutation persists a FAILURE row → **cockpit is `cascading` tier**, NOT `spreading`. First §5a `cascading` example.

vip_invite doc's forward-looking cockpit note amended in this close cascade to reflect the confirmed discovery.

---

## Post-merge live verify — 6/8 dispatches clean

| Tool | Action | Latency | Envelope shape vs §4 golden-path | Notes |
|---|---|---|---|---|
| podcast | stats | 16ms | ✅ matches | Empty aggregate (0/0/0/{}) — dev env |
| podcast | shows | 3ms | ✅ matches | count=0, empty list |
| podcast | episodes | 4ms | ✅ matches | count=0, empty list |
| podcast | scripts | — | skipped | No episodes to test |
| vip_invite | list | 11ms | ✅ matches | total=1, 1 invite (no divergence in this run) |
| vip_invite | create | 11ms | ✅ matches | Returned id `4648e791-f7d5-4089-9a88-21aa531aba56`, token, accept_url, expiries |
| vip_invite | revoke | 8ms | ✅ matches | status="revoked" |
| **vip_invite** | **revoke (2nd — idempotency)** | 8ms | ✅ matches expected error branch | `{"error": "Already revoked", "error_code": "legacy_error"}` — **dispatcher backfill fires as expected** |

**ORM-hard cross-checks:** partially blocked. `orm_inspect_tool` exposes only 11 models (Agent/AutopilotAction/Budget/Deliverable/Initiative/LLMCallLog/LegacySpiderData/Opportunity/...); VIPInvite + User both absent. Envelope-level proxy verification via `vip_invite_tool.list` confirmed:
- `revoked=true` for `4648e791...` — revoke persisted ✅
- `created_by="chris"` — first-superuser hardcode ✅
- `redeemed_by=null` — never-redeemed path (single-table branch) ✅

Cross-table `spreading` full-exercise not runnable — 0 candidate rows in dev DB (both listed invites are `revoked=true, redeemed_by=null`). Rigby correctly refused to synthesize a redeemed invite. Single-table branch validation stands for the `spreading` tier; full end-to-end cross-table validation deferred to a future organic exercise or dev-DB seeding.

---

## Legacy-error envelope framing corrected (dispatcher backfill discovery)

Live-verify idempotency guard returned `{"error": "Already revoked", "error_code": "legacy_error"}` — the `error_code` field IS present, contrary to podcast + vip_invite docs' initial framing.

Verified at `core/services/tool_dispatcher.py:862-885`:
```python
# (S2874/S2875) emit {'error', 'error_code', ...}; legacy
# handlers return {'error': msg} only. Backfill
# error_code='legacy_error' so consumers can program against a
# stable contract during the mixed-mode migration window.
# Idempotent: presence of error_code short-circuits. Truthy-
# check on 'error' key.
if (
    isinstance(result, dict)
    and result.get('error')
    and 'error_code' not in result
):
    result['error_code'] = 'legacy_error'
```

**Corrected framing** (shipped in close-cascade doc updates):
- Handler omits `error_code` field.
- Dispatcher auto-backfills `error_code='legacy_error'` per S2874 mixed-mode migration (S2876 breadcrumb telemetry).
- Final envelope observed by callers is `{"error": <str>, "error_code": "legacy_error"}`.
- "Legacy-error envelope" ledger substrate is actually a **count of un-migrated handlers**, not "handlers with no error_code". The value `'legacy_error'` is a first-class semantic signal.

Corrected in podcast_tool_validation.md + vip_invite_tool_validation.md §5.

---

## Rigby Tool Gap Ledger entries appended this session (deliverable `5c84e75a-…`)

**Entry #31 (MEDIUM) — orm_inspect_tool missing VIPInvite + User models from allowlist**
Cross-table `spreading`-tier full-exercise verification requires ORM-hard cross-checks (revoked_at persistence, created_by.is_superuser, redeemed_by state, cross-table candidate count). `orm_inspect_tool` exposes 11 models; VIPInvite + User both absent. Sweep-batch workaround via tool-envelope proxy exists but this gap resurfaces on every future user-scoped/auth-scoped tool validation. Fix candidates: (a) expand orm_inspect_tool allowlist with auth-scope review for User; (b) add `vip_invite_tool.detail` action returning full row; (c) safe-read allowlist expansion path.

**Entry #32 (LOW) — Static @receiver grep insufficient for signal-cascade classification (missed CeleryTaskEvent dynamic connect)**
Substrate observation for future signal-shape audits: static `@receiver` grep must be paired with (a) `post_save.connect(...)` dynamic-connect grep AND (b) Django-startup log cross-check for wire-in confirmations. 1st in-sweep instance; 2nd triggers Ledger evaluation for possible Fold promotion (combined-pattern query as sweep-batch template).

---

## Sweep progress (post-S2922)

- **Slice 4 (`td_handlers_gateway`):** **14/17 shipped.** Batch 5 CLOSED as mixed pair.
- Remaining 3 with verified handler line counts (grep + boundary math against `td_handlers_gateway.py` at sha `3078dd48b`):
  - **cockpit** — handler 1022–1452 = **431 lines** — MUTATION `cascading` (S2922 discovery confirms: CeleryTaskEvent.save → dynamic post_save.connect fires escalate_failure_cluster → human_attention_bridge downstream reach).
  - **proactive** — handler 1560–1699 = **140 lines** — MUTATION `spreading` (update×3, bulk-ack up to 200 rows).
  - **profile** — handler 2294–2481 = **188 lines** — MUTATION `spreading` (get_or_create×2 + save×1).
- Total corpus untested (post gap-map regen): 33 (batch 5 flipped 2 untested → validated_full via auto-classifier + self_awareness caught up from S2921 close-cascade miss = 3 total upgrades this regen).
- Gap map: **66 full · 10 partial · 7 unknown · 33 untested** post-regen (was 63/10/7/36 pre-regen).
- Session cumulative pace: 2 tools / 1 session (with 2-turn SIGN + 21 repo_tool receipts + Chris-facing plain-English framing + post-merge live-dispatch + close-cascade dispatcher-backfill discovery + 2 ledger entries).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):** PR #3474 recycled clean at `sha=3078dd48b009`, `surviving=none`. 5 fresh workers + beat.

---

## Ledger candidates opened this session (all deferred per D6 moratorium; watch continues)

1. **First Slice-4 exercise of §5a `spreading` tier** — vip_invite.revoke as archetype cross-table mutation with bounded reach. Batch 6 will scale to `proactive.bulk_ack` (bulk-multi-row) and `profile.update_preferences` (get_or_create + save). **Substrate anchor**, not a Ledger row per se.
2. **Legacy-error envelope 17th (podcast) + 18th (vip_invite) instances** — count semantics REFRAMED this session as "un-migrated handler count" per dispatcher backfill discovery at `tool_dispatcher.py:862-885`. Substrate arc still gated on explicit Chris directive per 00-START forbidden-list; Rigby S2920 Q4(a) semantic-nuance refresh (`error_code='legacy_error'` as first-class not-yet-migrated signal) deferred post-D6 per S2921 Q5(c).
3. **Dispatcher auto-backfill of `error_code='legacy_error'`** — first surfaced formally this session via live-verify idempotency test. Not a new pattern (S2874 migration) but the sweep documentation now explicitly names the dispatcher-layer behavior. Recorded as authoring detail.
4. **Mixed user-scoping ACROSS actions** — podcast `episodes` action does not filter by user_id while `shows` + `stats` do. Candidate 2nd instance of "mixed user-scoping" Fold (1st was S2920 calendar_tool.stats intra-response mix). Related but distinct sub-pattern (cross-action vs intra-response). Absorbed by single-user pre-prod context.
5. **Schema-documented cross-row side effect** — vip_invite `revoke` schema description at `pa_tool_schemas.py:4544` surface-documents the cross-table User deactivation. 1st Slice-4 authoring-positive instance; 2nd triggers Fold evaluation for "cross-row side effects MUST be surfaced in schema description" rule.
6. **`user_id` param IGNORED for admin-scoped mutation** — vip_invite `create` hardcodes first-superuser as `created_by` regardless of caller. 1st Slice-4 instance; absorbed by single-user pre-prod.
7. **`total`-vs-`len(list)` divergence without `has_more`** — vip_invite `list` returns `total = VIPInvite.objects.count()` but `invites` capped at 20 (no `limit` param). 1st Slice-4 instance.
8. **Dynamic post_save.connect() invisible to static @receiver grep** — Rigby SIGN turn 1 missed the FAILURE_CLUSTER wire-in; close-cascade Django-startup log discovery corrected. 1st in-sweep instance; 2nd triggers Ledger evaluation.
9. **orm_inspect_tool allowlist gap for auth-scoped mutation validation** — Ledger entry #31 (MEDIUM). Sweep-batch workaround exists via tool-envelope proxy; will resurface on every future auth-scoped tool validation.
10. **Podcast script hard-truncation without pagination cursor** — 3000-char cap at handler line 2022. 1st Slice-4 instance.
11. **00-START span-math regen validated a 2nd time** — podcast 251-claim vs 89-actual (162-line drift). Chris Q5(b) close-ceremony commitment (span-math regen from live evidence) now permanent per Rigby Q5(ii) AGREE.

---

## D6 moratorium — all forbidden list from S2921 close STILL IN FORCE at S2923 open

Unchanged from S2921 close. See `00-START-NEXT-SESSION.md` for the full forbidden-list.

---

## Files touched

- **New:** `docs/research/tools/validation/podcast_tool_validation.md` (106 lines) — sweep variant v1, 4 actions in scope, pure-READ.
- **New:** `docs/research/tools/validation/vip_invite_tool_validation.md` (145+ lines pre-correction; corrected in close cascade) — sweep variant v1, 3 actions in scope, §5a filled with `contained` + `spreading` classifications.
- **Modified:** `docs/audits/PA_TOOLS_GAP_MAP.md` — regenerated: validated_full 63→66, untested 36→33, template compliance pass 58→61, warn 103→100.

Close cascade PR adds: this handoff + 00-START refresh (regenerated span-math from live evidence per Chris Q5(b) permanent commitment) + wrapper pin bump + legacy-error envelope framing corrections in both validation docs.
