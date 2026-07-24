# `vip_invite_tool` — Validation Report (S2922)

**Tool:** `vip_invite_tool`
**Schema:** `core/services/pa_tool_schemas.py:4531`
**Handler:** `core/services/td_handlers_gateway.py:941` (`_handle_vip_invite`)
**Register site:** `core/services/tool_dispatcher.py:600`
**Session:** S2922 (Slice 4 batch 5 — mixed pair: `podcast` pure-READ + `vip_invite` `spreading` mutation; batch shipped per Chris ratification of Claude+Rigby joint recommendation (a) mixed batch)
**HEAD at validation:** `5983f5a23` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape) + §5a mutation-containment filled with 4-tier blast-radius classification per _TEMPLATE §5a schema shipped at S2921. Post-merge live-dispatch verify per PLAYBOOK-7.4.4 on all 3 actions including both mutation actions (`create` classified `contained`, `revoke` classified `spreading`).
**Category upgrade target:** `untested` → `validated_full` (all 3 actions in scope this ship — 1 pure-read + 2 mutation)
**Rigby SIGN:** S2922 T0 SIGN AGREE — 2-turn cycle grounded in 21 `repo_tool` receipts (8 turn 1 + 13 turn 2); zero rubber-stamp; corrected the S2920 close 00-START mutation-verb count (vip_invite = create + save×2 including cross-table `redeemed_by.is_active=False` flip on revoke); verified handler span 941–1018 mutation verbs at exact line receipts (line 973 create; lines 1005–1006 invite.save; lines 1007–1009 cross-table User.save); reversed Claude's initial S2921 Q1(a) "template-purity first" recommendation via ship-progress argument that batch 4 pilot proved single-tool mutation ships are viable, freeing batch 5 to run the amended §5a `spreading` tier on the smallest cross-table archetype (this tool).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`vip_invite_tool` manages the VIP magic-link invite substrate (`core/models_vip_invite.py:VIPInvite`) — one-time-use tokens Chris hands to demo viewers (e.g. investors, prospective clients, prospective advisors) so they land on a read-only VIP account with auto-expiry (72h token / 14d account per `_default_token_expires` + `_default_account_expires` at model lines 22–27). Use it when Chris asks "create a demo link for X" / "list active invites" / "revoke the invite for Y" / "who's redeemed which invite".

Distinct from `discord_tool` (Discord bot introspection, no invite substrate), from `mobile_tool` (mobile-app introspection, no auth mutation), and from `governance_tool` (advisor/human-decision routing, not viewer onboarding). Also distinct from the `views_vip_invite.py` API surface (`/api/v1/vip-invites/{create,exchange,revoke,list}/` at `views_vip_invite.py:27-227`) — the tool intentionally omits the `exchange` action because token-exchange is a public unauthenticated endpoint driven by browser click, not an admin-operator surface.

## Covered actions

- `list` — **in scope this ship — pure READ** — verified live. Returns first 20 `VIPInvite` rows via `VIPInvite.objects.select_related('created_by', 'redeemed_by').all()[:20]` at handler line 952. Envelope: `{action, total, invites: [{id, label, is_valid, token_expires_at, redeemed_by, revoked, created_by}]}`. Note: `total` is the full-table `VIPInvite.objects.count()` at line 955 while `invites` array is capped at 20 — see §5 for `total`-vs-`len(invites)` divergence.
- `create` — **in scope this ship — mutation, classified `contained`** — verified live. Writes 1 `VIPInvite` row via `VIPInvite.objects.create(created_by=admin_user, label=label)` at handler line 973. Returns `{action, id, token, accept_url, token_expires_at, account_expires_at, label}`. See §5a for blast-radius classification.
- `revoke` — **in scope this ship — mutation, classified `spreading`** — verified live. Mutates `VIPInvite.revoked_at = timezone.now()` + `.save(update_fields=['revoked_at'])` at lines 1005–1006; then IF `invite.redeemed_by` is set, ALSO mutates `User.is_active = False` + `.save(update_fields=['is_active'])` at lines 1007–1009. Cross-table effect: revoking an already-redeemed invite deactivates the redeemed user's login capability. Envelope: `{action, id, status: 'revoked'}`. See §5a for blast-radius classification.

Default action = `list` (per `payload.get('action', 'list')` at handler line 948).

## 3. Schema notes

- **Required:** `action` (enum: `list` / `create` / `revoke`).
- **Optional:** `label` (str; used by `create` — internal note for the invite, e.g. "Austin demo Mar-2026"); `id` (str; UUID required by `revoke`).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4529-4557`.
- **Envelope shape:** `list` returns `total` + `invites` (see divergence in §5); `create` returns single-invite rollup with `token` + `accept_url`; `revoke` returns 3-field acknowledgment. Consistent with the envelope-key-asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2.
- **Schema description edge:** the schema description for `revoke` says "disable an invite and deactivate its user" (line 4544) — accurate to the cross-table flip at handler lines 1007–1009. Only schema in Slice 4 that surface-documents a cross-table side effect at the parameter-description layer. Recorded as authoring positive — this is the pattern the amended §5a `spreading` tier wants for cross-row mutations.
- **No `limit` param:** `list` action returns first 20 unconditionally; no `limit` in schema. Distinct from most Slice 4 tools (which surface `limit` with default 20 / cap 50). Recorded as authoring detail; downstream callers wanting >20 must query DB directly.
- **`user_id` param IGNORED for `create`:** handler line 969 hardcodes `admin_user = User.objects.filter(is_superuser=True).first()` — the invite's `created_by` FK is set to the first superuser regardless of the actual caller. Effectively means: any operator with `vip_invite_tool` access acts on behalf of the platform's first superuser. Absorbed by single-user pre-prod context (Chris is the sole superuser); would need redesign in a multi-tenant future.

## 4. Golden-path examples

**Example 1 — list active invites (default action):**
```json
{"action": "list"}
```
Expected envelope: `{"action": "list", "total": <int>, "invites": [{"id": "<uuid>", "label": "<str>", "is_valid": <bool>, "token_expires_at": "<isoformat>", "redeemed_by": "<username|null>", "revoked": <bool>, "created_by": "<username>"}, ...]}`.

**Example 2 — create a labeled invite for a specific demo (mutation; contained):**
```json
{"action": "create", "label": "Austin demo Mar-2026"}
```
Expected envelope: `{"action": "create", "id": "<uuid>", "token": "<url-safe token>", "accept_url": "https://<host>/vip/accept?token=<token>", "token_expires_at": "<isoformat +72h>", "account_expires_at": "<isoformat +14d>", "label": "Austin demo Mar-2026"}`. Side effect: 1 new `VIPInvite` row with `created_by` = first superuser.

**Example 3 — revoke an active invite (mutation; spreading if already-redeemed):**
```json
{"action": "revoke", "id": "<invite-uuid>"}
```
Expected envelope: `{"action": "revoke", "id": "<uuid>", "status": "revoked"}`. Side effect: 1 `VIPInvite.revoked_at` set to now; IF `invite.redeemed_by` is present, ALSO 1 `User.is_active` flipped to False. Any active sessions for the deactivated user become unusable at next `is_active` re-check.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": f"Unknown action: {action}. Use list, create, or revoke."}` at handler line 1014. Not raised — in-envelope.
- **Handler exception:** caught at line 1016, logged via `logger.error("[VIP_INVITE] Error: {e}", exc_info=True)`, returns `{"error": <str>}` from handler. Handler omits `error_code` field; **dispatcher auto-backfills `error_code='legacy_error'`** at `tool_dispatcher.py:862-885` per S2874 mixed-mode migration (S2876 breadcrumb telemetry) — final envelope observed by callers is `{"error": <str>, "error_code": "legacy_error"}`. **Verified live at S2922 close-cascade:** second-revoke idempotency guard returned `{"error": "Already revoked", "error_code": "legacy_error"}` — dispatcher backfill fires as expected. This is the 18th corroborating instance of the unmigrated-handler pattern post-S2921's 16-instance count; podcast_tool in this same batch is the 17th. Substrate arc still gated on explicit Chris directive per 00-START forbidden-list.
- **`create` — no admin user found:** returns `{"error": "No admin user found to create invite"}` at handler line 971. Only fires in a stripped test environment with no superusers.
- **`revoke` — missing `id`:** returns `{"error": "Provide invite id to revoke"}` at handler line 996.
- **`revoke` — invite not found:** returns `{"error": f"Invite {invite_id} not found"}` at handler line 1000 via `VIPInvite.DoesNotExist` catch at line 999.
- **`revoke` — already revoked:** returns `{"error": "Already revoked"}` at handler line 1002. Idempotency guard — second revoke on the same invite is a no-op that surfaces as an error rather than silent success. Callers should treat this as informational, not fatal.
- **`list` `total`-vs-`len(invites)` divergence:** `total = VIPInvite.objects.count()` (line 955) counts every row (including revoked and expired); `invites` array is capped at 20 (line 952). If `total > 20`, the operator sees only the 20 most-recently-created invites (per model `Meta.ordering = ['-created_at']` at `models_vip_invite.py:89`) — the remainder are invisible unless paginated via a direct DB query. No `has_more` flag surfaced. Documented sharp edge; not a defect for the current single-user use case.
- **`accept_url` host resolution:** handler line 977 reads `os.environ.get('VIP_ACCEPT_BASE_URL', 'https://donkey-betz-platform-production.up.railway.app')`. On celery-pa workers, `FRONTEND_URL` / `BACKEND_URL` resolve to the celery service's own domain (NOT the public web frontend) — the tool intentionally uses a dedicated env var to avoid that misdirection. Comment at lines 974–976 documents this. If `VIP_ACCEPT_BASE_URL` is unset on a fresh deploy, the default hardcoded Railway URL is used; test/staging deployments MUST set this env var or generated `accept_url` values will point at prod.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy amended S2921)

Two mutation actions in this tool. Classification and rationale per the 4-tier blast-radius schema at `_TEMPLATE_per_tool_validation.md` §5a.

| Action | Mutation type | Blast-radius tier | Rationale |
|---|---|---|---|
| `create` | `VIPInvite.objects.create(...)` — 1 row (handler line 973) | `contained` | Single-row INSERT into `VIPInvite` (append-only from the tool's perspective; the model inherits `UnifiedBaseModel` — no observable `@receiver(post_save, sender=VIPInvite)` handlers found in a repo-wide grep across 25 signal-registering modules per Rigby T0 SIGN turn 1). No FK cascade at create time (`created_by` FK points at existing superuser; `redeemed_by` / `workspace` / `prospect_profile` are null at creation). No cross-table reach. No bulk. Idempotent-in-effect (each call adds one invite; retries produce duplicate invites but do not corrupt existing rows). Safest possible mutation shape — matches the batch-4 `self_awareness.collect` archetype. |
| `revoke` | `invite.save()` + optional `redeemed_by.save()` — 1 or 2 rows across 2 tables (handler lines 1005–1009) | `spreading` | Cross-table mutation with bounded reach: always 1 `VIPInvite` row (`revoked_at` field only, `update_fields=['revoked_at']`); optionally 1 `User` row (`is_active` field only, `update_fields=['is_active']`) IFF the invite was previously redeemed. Cross-table effect is user-account state (`is_active=False`) — the deactivated user cannot log in after this flip and existing sessions become unusable at next `is_active` re-check. No signal cascade (grep-clean per Rigby T0 SIGN turn 1); no bulk; no FK cascade (`ForeignKey.on_delete=SET_NULL` on `redeemed_by` at model line 80 is defensive-only — this path never deletes). Effect is bounded to (invite, user) tuple; does NOT reach the invite's `created_by` superuser, `workspace`, or `prospect_profile`. Archetype `spreading` case for Slice 4 — one row mutated in the primary table + one row mutated in a distinct downstream table via explicit code path (not signal chain). |

**Deferral status:** NOT deferred. Ship-in-scope this batch — this ship exercises both mutation actions post-merge to verify the classifications hold end-to-end (see §6 post-merge verification protocol).

**Comparison to remaining Slice 4 mutation candidates (batch 6):**
- `proactive.bulk_ack` — `spreading` (bulk multi-row: up to 200 rows in `ProactiveNotification.filter(...).update(is_read=True)` at handler line 1677; user-scoped but broad within that user). Batch 6 will run this.
- `profile.update_preferences` — `spreading` (`get_or_create` × 2 + `save` × 1 per Rigby S2921 turn 1 grep; may implicitly create `EnhancedUserProfile` row at ~line 2394 + persist preference changes at ~line 2415). Batch 6 will run this.
- `cockpit.*` — mutation shape now confirmed via post-SIGN Django-startup discovery. Rigby S2922 T0 SIGN Q4 static-grep found NO `@receiver(post_save, sender=CeleryTaskEvent)` decorators across 25 signal modules — honest caveat preserved (dynamic `.connect()` may exist). **S2922 close-cascade discovery via `python manage.py build_pa_tool_audit` init logs: `FAILURE_CLUSTER_SIGNALS] receiver wired on CeleryTaskEvent.post_save (dedup_window_min=30)` — dynamic connect at `core/signals/failure_cluster_signals.py:183` (`post_save.connect(escalate_failure_cluster, sender=CeleryTaskEvent, ...)`).** Handler fires only on FAILURE status per `escalate_failure_cluster` gate; when it fires, it escalates via `human_attention_bridge` (further downstream reach). Cockpit's `CeleryTaskEvent.save()` at `td_handlers_gateway.py:1030-1039` will therefore hit the dynamic handler if the mutation persists a FAILURE row → cockpit is `cascading` tier (first §5a `cascading` example), NOT `spreading`. Batch 6 SIGN turn will confirm the full escalation path (`escalate_failure_cluster` → `human_attention_bridge` reach breadth) before final classification. **Corroborating Fold candidate:** "static `@receiver` grep alone is insufficient for signal-cascade classification — must also grep `post_save.connect(...)` dynamic connections and cross-check Django-startup init logs". First observation — 2nd instance would trigger Ledger evaluation.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `VIPInvite.objects.select_related(...).all()[:20]` | `read` | `td_handlers_gateway.py:952` | ORM SELECT with JOIN; documented |
| `VIPInvite.objects.count()` | `read` | `td_handlers_gateway.py:955` | ORM aggregate; documented |
| `User.objects.filter(is_superuser=True).first()` | `read` | `td_handlers_gateway.py:969` | ORM SELECT; documented (hardcoded — see §3 quirk) |
| `VIPInvite.objects.create(created_by=admin_user, label=label)` | `db_write` | `td_handlers_gateway.py:973` | ORM INSERT (1 row); documented — `create` mutation |
| `os.environ.get('VIP_ACCEPT_BASE_URL', ...)` | `read` | `td_handlers_gateway.py:977` | Env read; no network I/O |
| `VIPInvite.objects.get(id=invite_id)` | `read` | `td_handlers_gateway.py:998` | ORM SELECT by PK; documented |
| `invite.save(update_fields=['revoked_at'])` | `db_write` | `td_handlers_gateway.py:1006` | ORM UPDATE (1 row, 1 field); documented — `revoke` primary mutation |
| `invite.redeemed_by.save(update_fields=['is_active'])` | `db_write` | `td_handlers_gateway.py:1009` | ORM UPDATE (1 row, 1 field, distinct table); documented — `revoke` cross-table mutation |
| `timezone.now()` | `read` | `td_handlers_gateway.py:1005` | Clock read; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop. `os.environ.get(...)` at line 977 is env-var read, not a network call; the returned string is composed into an `accept_url` for the response envelope but the tool never dereferences the URL itself.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop. Handler is entirely synchronous.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2922 T0 SIGN Q2 per-tool confirmation: vip_invite span 941–1018 contains none of these literals — grep receipts in Rigby T0 SIGN turn 2 (`repo_tool.read_file` on the handler span; `search` for `"vip_invite_tool"` returned 0 matches inside `td_handlers_gateway.py`; no outbound first-hop-literal dispatch).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification on all 3 actions (including both mutation actions) appended to the S2922 handoff. Expected envelope shapes documented in §4 golden-path examples.

**Post-merge verification protocol:**

For `create`:
1. Dispatch `{"action": "create", "label": "S2922 batch 5 verify"}`.
2. Response envelope contains `id` + `token` + `accept_url`.
3. ORM cross-check: `VIPInvite.objects.get(id=<returned_id>)` succeeds; `label == "S2922 batch 5 verify"`; `created_by_id` equals the platform's first superuser PK; `token_expires_at ≈ now + 72h`; `account_expires_at ≈ now + 14d`; `redeemed_at is None`; `revoked_at is None`.
4. If any assertion fails, `contained` classification is invalidated for `create` and this doc is amended.

For `revoke` (on the invite created in step 1 above — never-redeemed path, exercises the single-table branch):
1. Dispatch `{"action": "revoke", "id": "<invite_id>"}`.
2. Response envelope: `{"action": "revoke", "id": "<uuid>", "status": "revoked"}`.
3. ORM cross-check: `VIPInvite.objects.get(id=<invite_id>).revoked_at is not None`; `redeemed_by` still None (never-redeemed); no `User.is_active` flip fired.
4. Second-revoke check: dispatch same payload again → expect `{"error": "Already revoked"}` (idempotency guard, line 1002).

For `revoke` cross-table path (validates `spreading` tier fully — requires a pre-existing redeemed invite; skip if no redeemed test invite exists in the dev DB, note explicitly in handoff):
1. Identify a VIPInvite row with `redeemed_by` set + `revoked_at is None` via `VIPInvite.objects.filter(redeemed_by__isnull=False, revoked_at__isnull=True).first()`.
2. If found, capture `redeemed_by_id` before revoke.
3. Dispatch `{"action": "revoke", "id": "<invite_id>"}`.
4. ORM cross-check: `VIPInvite.revoked_at is not None` AND `User.objects.get(id=<redeemed_by_id>).is_active is False`.
5. If the cross-table `is_active` flip does not fire when `redeemed_by` is present, `spreading` classification is invalidated and this doc is amended.
6. If no redeemed test invite exists, note in handoff — cross-table path exercise deferred; single-table path from step above still validates the `spreading` tier's primary-mutation half.

## Related

- **Adjacent tools:** `podcast_tool` (this batch — pure-READ counterpart in the mixed pair); `discord_tool` (batch 2 — filesystem-read shape, no auth mutation); `governance_tool` (advisor/human-decision routing, not viewer onboarding).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1 — §5a 4-tier blast-radius taxonomy first exercised for `spreading` tier by this doc); model at `core/models_vip_invite.py:VIPInvite`; API views at `core/views_vip_invite.py` (public `exchange` action lives here, intentionally omitted from the tool surface).
- **Prior ratifications:** S2892 Path B open, S2918–S2921 Slice 4 batches 1–4, S2921 §5a 4-tier taxonomy amendment.
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 18th instance** — continued corroboration; still gated on explicit Chris directive per 00-START forbidden-list.
  - **First Slice-4 exercise of §5a `spreading` tier** — vip_invite.revoke is the archetype cross-table mutation with bounded reach. Batch 6 will run the same tier on `proactive.bulk_ack` (bulk-multi-row) and `profile.update_preferences` (get_or_create + save).
  - **`user_id` param IGNORED for `create`** — handler hardcodes first-superuser as `created_by`. Absorbed by single-user pre-prod; would need redesign for multi-tenant. First observation of this specific pattern in Slice 4; recorded for post-D6 evaluation as an ownership-provenance authoring pattern (compare with the "multi-tenant leak on detail/results action" Fold at 3 instances now absorbed by single-user context per `project_single_user_pre_prod_operating_context`).
  - **Schema description surface-documents cross-table side effect** — `pa_tool_schemas.py:4544` says "disable an invite and deactivate its user". First Slice-4 instance of a schema surfacing a cross-row side effect at the parameter-description layer. Recorded as authoring positive — this is the pattern the amended §5a `spreading` tier wants; 2nd instance triggers Fold evaluation for "cross-row side effects MUST be surfaced in schema description".
  - **`list` `total`-vs-`len(invites)` divergence without `has_more`** — `total` counts full table; `invites` capped at 20. First observation in Slice 4; may resurface as a Fold candidate if pagination-cursor absence keeps appearing (2nd instance triggers evaluation).
  - **00-START mutation-verb count corrected** — S2920 close 00-START implied a simpler mutation shape (missed the cross-table `User.is_active` flip); Rigby S2921 T0 SIGN turn 1 grep-caught the miss; corrected shape shipped in S2921 close 00-START and re-verified in this doc.
