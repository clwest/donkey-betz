# `profile_tool` — Validation Report (S2924)

**Tool:** `profile_tool`
**Schema:** `core/services/pa_tool_schemas.py:4960`
**Handler:** `core/services/td_handlers_gateway.py:2294` (`_handle_profile`)
**Register site:** `core/services/tool_dispatcher.py` (via gateway registration; grep `register("profile_tool"` in `tool_dispatcher.py`)
**Session:** S2924 (Slice 4 batch 7 — FINAL Slice 4 batch, closes the slice at 17/17; shipped as spreading pair with `proactive_tool` per Chris D-verdict on Claude+Rigby joint recommendation (a) proactive+profile pair)
**HEAD at validation:** `592f72214` (2026-07-23 — S2924 doc-fix PR#3478 for cockpit §6 step 8 just landed)
**Ship shape:** Doc-only (S2796 shape) + §5a mutation-containment filled with 4-tier blast-radius classification per `_TEMPLATE §5a` schema shipped at S2921. Post-merge live-dispatch verify per PLAYBOOK-7.4.4 on all 6 actions (4 READ + 1 MUTATION + 1 hybrid).
**Category upgrade target:** `untested` → `validated_full` (all 6 actions in scope this ship — 4 pure-read + 1 mutation + `preferences` which triggers implicit `get_or_create` on first-touch)
**Rigby SIGN:** S2924 T0 SIGN AGREE — 1-turn cycle grounded in 10 `repo_tool` receipts (git_info + 3× search + 3× read_file + 3× Appendix N discovery); zero rubber-stamp; confirmed clean `User.objects.filter(id=user_id).first()` user-scoping gate at `td_handlers_gateway.py:2361` + `:2390` (contrast with proactive's user-scoping gap). Rigby Q3 Profile section: "cross-user reach: none visible; always tied to `user_id` → that `user` instance → that single `EnhancedUserProfile` row." Grep receipts confirm.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`profile_tool` surfaces the platform's user-profile substrate — extended profile + skills list + learning summary (all sourced from `ExtendedUserProfile` at `core/models/__init__.py`; the `skills` field is a JSON list-of-dicts), structured preferences (`EnhancedUserProfile` at `core/models/__init__.py`), and desk-scoped preference projections. Use it when Chris asks "show my profile" / "what skills am I tracked as having?" / "learning summary" / "my preferences" / "update my preference for X" / "what preferences apply on the sports desk?".

**S2925 Ledger #33 resolution note:** `skills` + `learning_summary` originally read from `UserSkill` (`core/models_user_learning.py`), whose backing table was `DeleteModel`'d by migration `0229_initiative_last_activity_at` in Feb 2026. The Django model class was left behind, creating a latent stale-model bug. S2925 rewrote `skills` + `learning_summary` to source from `ExtendedUserProfile.skills` (the same JSON field already used by the `profile` action). Envelope shape changed — see §Covered actions below. Broader stale-model latent bug (5 other services still import UserSkill) filed as separate Ledger entry.

Distinct from `personal_assistant_interviewer` (interview-driven skill discovery — populates the same substrate but via conversation, not view/update), from `governance_tool` (advisor identity/routing — not user profile), from `mobile_tool` (mobile-app introspection — no profile CRUD surface), and from Discord user-mapping (Discord IDs live on `ChatConversation`, not `ExtendedUserProfile`).

## Covered actions

- `profile` — **in scope this ship — pure READ (default action)** — verified live. Returns `ExtendedUserProfile` for the calling user via `ExtendedUserProfile.objects.filter(user_id=user_id).first()` at handler line 2301. Envelope: `{action, profile: {full_name, location, timezone, current_title, years_experience, experience_level, skills, certifications, remote_preference, profile_completeness}}` OR `{action, profile: null, message: 'No extended profile found'}` when no row exists. User-scoped strictly — no user_id → null profile (no fallback to global).
- `skills` — **in scope this ship — pure READ** — **verified live at S2925 (Ledger #33 resolved via code fix)**. Returns up to 50 entries from `ExtendedUserProfile.skills` (JSON list-of-dicts) for the calling user. Fetches profile via `ExtendedUserProfile.objects.filter(user_id=user_id).first()`; normalizes each entry to `{skill_name, category, proficiency_level, years}`, tolerating both dict entries (`{'name': 'Python', 'proficiency': 'Expert', 'years': 5}`) and bare string entries. Envelope: `{action, count, skills: [{skill_name, category, proficiency_level, years}], source: 'extended_user_profile.skills'}`. User-scoped strictly — no user_id → empty list (no fallback to global). Note: hard-coded 50-row cap (no `limit` param); consistent with vip_invite's `list` action. **Envelope change from pre-S2925:** removed `id` / `evidence_count` / `confidence` / `last_demonstrated` (UserSkill-specific fields, no equivalent on JSON schema); added `years` + `source`.
- `learning_summary` — **in scope this ship — pure READ** — **verified live at S2925 (Ledger #33 resolved via code fix)**. Aggregates from `ExtendedUserProfile.skills`: counts entries per `category` (defaulting to `uncategorized`) and computes `avg_years` across entries that have a numeric `years` field. Envelope: `{action, total_skills, by_category: {<category>: <count>, ...}, avg_years, source: 'extended_user_profile.skills'}`. **Envelope change from pre-S2925:** replaced `avg_confidence` (UserSkill-only field) with `avg_years` (derived from ExtendedUserProfile.skills entries).
- `preferences` — **in scope this ship — pure READ (with implicit-write side effect)** — verified live. Fetches (or `get_or_create` inserts if missing) an `EnhancedUserProfile` row via `EnhancedUserProfile.objects.get_or_create(user=user)` at handler line 2365. Returns 12 preference fields as JSON. Envelope: `{action, preferences: {long_term_goals, current_projects, quarterly_objectives, learning_style, communication_style, decision_framework, current_learning_goals, personal_values, delegation_preferences, work_schedule, time_zone, privacy_level}}` OR `{action, error: 'No user context'}` when `user_id` is absent (line 2362–2363). **Note:** classified pure-READ from caller perspective but IS a spreading-tier write on first-touch (see §5a).
- `update_preferences` — **in scope this ship — mutation, classified `spreading`** — verified live. `EnhancedUserProfile.objects.get_or_create(user=user)` at handler line 2394 (may create row) + `enhanced.save()` at line 2415 (persists field changes IFF applied dict is non-empty). Accepts either bulk `updates` dict OR single `field`+`value` pair (line 2405–2406). Only 12 whitelisted `ALLOWED_FIELDS` (line 2397–2402) can be set; unknown fields are silently ignored. Envelope: `{action, updated_fields: [<list>], count, success: <bool>}`.
- `desk_preferences` — **in scope this ship — pure READ** — verified live. Reads BOTH `EnhancedUserProfile` (via `.filter(user=user).first()` at line 2435) AND `ExtendedUserProfile` (via `.filter(user=user).first()` at line 2436), applies a desk-specific projection (`sports` / `stocks` / `content` / `general`) from `DESK_PROJECTIONS` dict at handler lines 2444–2461, and returns a merged view with fallback semantics (Enhanced → Extended → typed empty default). Envelope: `{action, desk, communication_style, long_term_goals, <projected fields>..., context, available_desks}`.

Default action = `profile` (per `payload.get('action', 'profile')` at handler line 2296).

## 3. Schema notes

- **Required:** `action` (enum: `profile` / `skills` / `learning_summary` / `preferences` / `update_preferences` / `desk_preferences`).
- **Optional:** `field` (str; `update_preferences` — allowed values enumerated in schema description at `pa_tool_schemas.py:4981`); `value` (str; `update_preferences`); `desk` (enum: `sports` / `stocks` / `content` / `general`; `desk_preferences`).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4958-4987`.
- **Envelope shape:** each action returns a distinct top-level shape — `profile` returns `{action, profile: {...} | null, message?}`; `skills` returns `{action, count, skills: [...], source}`; `learning_summary` returns `{action, total_skills, by_category, avg_years, source}`; `preferences` returns `{action, preferences: {...}}`; `update_preferences` returns `{action, updated_fields, count, success}`; `desk_preferences` returns `{action, desk, <flat projected fields>, context, available_desks}`. Envelope-key-asymmetry-across-actions pattern (3/3 triggered post-S2919) — this tool is another instance.
- **`updates` param NOT in schema:** handler line 2396 accepts `payload.get('updates', {})` (bulk-dict form) but the schema at `pa_tool_schemas.py:4966-4987` only surfaces `field` + `value`. The bulk-dict form works but is undocumented in the tool-schema. **1st instance of "handler accepts bulk form but schema surfaces only single form"** — Ledger candidate.
- **`ALLOWED_FIELDS` whitelist:** 12 fields (line 2397–2402). Schema description at line 4981 enumerates the same 12 by name. Attempts to set fields outside the whitelist are silently dropped from `applied` dict at line 2410 — no error surfaced. Sharp edge — caller receives `success: false` (or `success: true` with a smaller `count` than requested) but no per-field feedback on which fields were rejected.
- **`get_or_create` on READ path:** `preferences` action's read semantically implies a write on first-touch — `get_or_create(user=user)` at line 2365 will INSERT a new `EnhancedUserProfile` row if the user has never touched preferences. Documented in §5a as an implicit-write side effect. First-touch is idempotent-in-effect (a fresh row with all-null fields materializes; subsequent reads return the same row).
- **No `limit` param on `skills`:** hard-cap at 50 rows (line 2325). Callers wanting >50 skills must query DB directly. Consistent with vip_invite's `list` action (also no `limit`; hard-cap at 20) — both are "surface the essentials, not the tail" tools.

## 4. Golden-path examples

**Example 1 — view calling user's extended profile (default action):**
```json
{"action": "profile"}
```
Expected envelope: `{"action": "profile", "profile": {"full_name": "<str>", "location": "<str>", "timezone": "<str>", "current_title": "<str>", "years_experience": <int|null>, "experience_level": "<str>", "skills": [<list>], "certifications": [<list>], "remote_preference": "<str>", "profile_completeness": <int 0-100>}}`. Returns `{"action": "profile", "profile": null, "message": "No extended profile found"}` if no row exists for `user_id`.

**Example 2 — tracked skills (post-S2925 shape, sourced from `ExtendedUserProfile.skills`):**
```json
{"action": "skills"}
```
Expected envelope: `{"action": "skills", "count": <≤50>, "skills": [{"skill_name": "<str>", "category": "<str>", "proficiency_level": "<str>", "years": <int|null>}, ...], "source": "extended_user_profile.skills"}`.

**Example 3 — structured preferences view (pure READ + implicit-write on first-touch):**
```json
{"action": "preferences"}
```
Expected envelope: `{"action": "preferences", "preferences": {"long_term_goals": [...], "current_projects": [...], "quarterly_objectives": {...}, "learning_style": "<str>", "communication_style": "<str>", "decision_framework": "<str>", "current_learning_goals": [...], "personal_values": [...], "delegation_preferences": {...}, "work_schedule": {...}, "time_zone": "<str>", "privacy_level": "<str>"}}`. Side effect on first-touch only: 1 new `EnhancedUserProfile` row materialized with all-null fields.

**Example 4 — update a single preference field (mutation; spreading):**
```json
{"action": "update_preferences", "field": "learning_style", "value": "hands-on, iterative, high-context"}
```
Expected envelope: `{"action": "update_preferences", "updated_fields": ["learning_style"], "count": 1, "success": true}`. Side effect: 1 `EnhancedUserProfile.learning_style` field mutated; row auto-created via `get_or_create` if user had none. Field must be in the 12-item `ALLOWED_FIELDS` whitelist — unknown fields silently dropped.

**Example 5 — bulk update multiple preferences (mutation; spreading — undocumented bulk form):**
```json
{"action": "update_preferences", "updates": {"time_zone": "America/Denver", "communication_style": "direct + terse", "privacy_level": "high"}}
```
Expected envelope: `{"action": "update_preferences", "updated_fields": ["time_zone", "communication_style", "privacy_level"], "count": 3, "success": true}`. Side effect: up to N fields on one `EnhancedUserProfile` row + one `.save()`. Only fields present in `ALLOWED_FIELDS` are applied.

**Example 6 — desk-scoped preference projection:**
```json
{"action": "desk_preferences", "desk": "sports"}
```
Expected envelope: `{"action": "desk_preferences", "desk": "sports", "communication_style": "<str>", "long_term_goals": [...], "decision_framework": "<val>", "current_learning_goals": [...], "context": "Sports betting preferences and risk tolerance", "available_desks": ["sports", "stocks", "content", "general"]}`. Unknown desk defaults to `general` at line 2463.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": f"Unknown profile_tool action: {action}. Valid: profile, skills, learning_summary, preferences, update_preferences, desk_preferences"}` at handler line 2475. Not raised — in-envelope.
- **Handler exception:** caught at line 2477, logged via `logger.error("[PROFILE] {action} error: {e}", exc_info=True)`, returns `{"error": <str>}`. Handler omits `error_code`; **dispatcher auto-backfills `error_code='legacy_error'`** at `tool_dispatcher.py:862-885` per S2874 mixed-mode migration. **This is the 21st corroborating instance of the unmigrated-handler pattern** post-S2923's 19-instance count (proactive_tool in this same batch is the 20th). Threshold-crossed note surfaced at Slice-4 close per S2924 Q5(iii) Chris ratification.
- **`preferences` / `update_preferences` / `desk_preferences` — no user context:** returns `{action, error: 'No user context'}` at handler lines 2363 / 2392 / 2433. **Note:** the error envelope key is `error` (not `error_code`) — action returns success shape structure with error field, not the standard `{"error": <str>}` envelope. Divergence from other actions' error shapes. Sharp edge — callers should check `'error' in response` regardless of envelope shape.
- **`profile` — no extended profile row:** returns `{action, profile: null, message: 'No extended profile found'}` at handler line 2303. Not treated as error — the `profile: null` signal is sufficient for callers.
- **`skills` empty:** returns `{action, count: 0, skills: [], source: 'extended_user_profile.skills'}`. Not an error. Also the shape when `user_id` is absent (no fallback to global — user-scoped strictly).
- **`learning_summary` empty:** returns `{action, total_skills: 0, by_category: {}, avg_years: 0, source: 'extended_user_profile.skills'}`. Not an error.
- **`update_preferences` — no matching fields:** returns `{action, updated_fields: [], count: 0, success: false}`. Also no `.save()` fires (guarded at line 2414 `if applied:`). Distinguishable from a successful update by `count: 0` + `success: false`.
- **`update_preferences` — unknown field:** silently dropped from `applied` dict at line 2410. Caller sees smaller `count` than requested with no per-field rejection info.
- **`desk_preferences` — unknown desk:** falls back to `general` projection at line 2463. No error surfaced. `desk` field in envelope reflects the caller-supplied string (not the fallback), while `context` reflects the general projection — mild inconsistency, documented sharp edge.
- **50-row cap on `skills` is silent:** if the calling user has >50 skills, only the first 50 entries from `ExtendedUserProfile.skills` are surfaced (JSON list order — no ordering key) with no `has_more` flag. Same divergence-from-count pattern as vip_invite's `list`.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy amended S2921)

Two mutation actions in this tool. One is the explicit `update_preferences` mutation; the other is the implicit `get_or_create` first-touch write on the `preferences` READ path. Both classified `spreading` — user-scoped by explicit gate but implicit-cross-table writes qualify per template.

| Action | Mutation type | Blast-radius tier | Rationale |
|---|---|---|---|
| `preferences` (implicit first-touch write) | `EnhancedUserProfile.objects.get_or_create(user=user)` — 0 or 1 row (handler line 2365) | `spreading` | Implicit new row into `EnhancedUserProfile` (a shared table storing per-user preference state) when the user has never accessed preferences. Match to template §5a definition: "`get_or_create` that implicitly writes a new row into a shared table" = `spreading` archetype. USER-SCOPED strictly via `User.objects.filter(id=user_id).first()` gate at line 2361 — returns `{action, error: 'No user context'}` when `user_id` absent at line 2362 (no fallback to global). Idempotent-in-effect (second touch returns the existing row via `get_or_create`'s existence semantics). No signal cascade on `EnhancedUserProfile.post_save` (grep-clean per Rigby T0 SIGN turn 1). |
| `update_preferences` | `EnhancedUserProfile.objects.get_or_create(user=user)` + `enhanced.save()` — 0-2 writes on 1 row (handler lines 2394 + 2415) | `spreading` | Bounded to (user, single-EnhancedUserProfile-row) tuple. First operation: `get_or_create` may materialize a fresh row (same as `preferences` first-touch shape above). Second operation: `enhanced.save()` mutates ≤12 whitelisted fields (from `ALLOWED_FIELDS` at line 2397–2402) IFF `applied` dict is non-empty (guarded at line 2414). USER-SCOPED strictly via same `User.objects.filter(id=user_id).first()` gate at line 2390. Cross-user reach: none — the `user=user` binding at line 2394 makes ownership physically deterministic (the `EnhancedUserProfile.user` FK is unique per `on_delete=CASCADE` FK from User; can't reach another user's row without another user's PK). Contrast with proactive's user-scoping gap in `mark_read`/`dismiss`. |

**Deferral status:** NOT deferred. Ship-in-scope this batch — this ship exercises both the implicit-write path (`preferences` on a fresh user) and the explicit-mutation path (`update_preferences` with real field changes) post-merge to verify the classifications hold end-to-end (see §6 post-merge verification protocol).

**Comparison to `proactive_tool` (this batch's spreading peer):**
- proactive: `spreading` tier per row-count reach (`bulk_ack` ≤200 rows) AND per cross-user reach (`mark_read`/`dismiss` unscoped). Row-count IS the primary reach dimension for `bulk_ack`; scoping-gap IS the primary reach dimension for `mark_read`/`dismiss`. Proactive is the "gap" spreading archetype.
- profile: `spreading` tier purely per implicit-cross-table-write dimension (`get_or_create` on `EnhancedUserProfile`). USER-SCOPED cleanly via explicit `User.objects.filter(...)` gate + `get_or_create(user=user)` binding. Profile is the "clean" spreading archetype.

**Signal-cascade non-fire assertion for both mutation paths:** `EnhancedUserProfile` + `ExtendedUserProfile` + `UserSkill` — repo-wide grep for `sender=EnhancedUserProfile` / `sender=ExtendedUserProfile` / `sender=UserSkill` returns 0 matches in `core/signals/`; 0 matches in `core/services/` outside of the ORM operations themselves. Grep receipts: `rg 'sender=EnhancedUserProfile' core/ → 0`; same for the other two. This validates the `spreading` (not `cascading`) classification — the implicit-write reaches exactly one row of one shared table with no downstream observer effects.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ExtendedUserProfile.objects.filter(user_id=user_id).first()` | `read` | `td_handlers_gateway.py:2301` | ORM SELECT; documented |
| `ExtendedUserProfile.objects.filter(user_id=user_id).first()` (skills action) | `read` | `td_handlers_gateway.py:2327` | ORM SELECT + `.skills` JSON traversal; documented |
| `ExtendedUserProfile.objects.filter(user_id=user_id).first()` (learning_summary action) | `read` | `td_handlers_gateway.py:2347` | ORM SELECT + in-Python aggregation of `.skills` JSON; documented |
| `User.objects.filter(id=user_id).first()` | `read` | `td_handlers_gateway.py:2361`, `:2390`, `:2431` | ORM SELECT by PK; documented — user-context gate |
| `EnhancedUserProfile.objects.get_or_create(user=user)` | `db_write` | `td_handlers_gateway.py:2365`, `:2394` | ORM UPSERT (0 or 1 row); documented — `preferences` implicit + `update_preferences` explicit |
| `enhanced.save()` | `db_write` | `td_handlers_gateway.py:2415` | ORM UPDATE (≤12 whitelisted fields on 1 row); documented — `update_preferences` mutation |
| `EnhancedUserProfile.objects.filter(user=user).first()` | `read` | `td_handlers_gateway.py:2435` | ORM SELECT; documented — `desk_preferences` |
| `ExtendedUserProfile.objects.filter(user=user).first()` | `read` | `td_handlers_gateway.py:2436` | ORM SELECT; documented — `desk_preferences` fallback source |

**Appendix N (Network-Preflight) — N/A.** No network first-hop. Handler is entirely ORM. `rg 'httpx|requests\.|urllib|urlopen' core/services/td_handlers_gateway.py` within the profile handler span (2294–2479) returns 0 matches.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop. Handler is entirely synchronous. No task dispatch inside handler span.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns at that time; cockpit_tool moved to 1/17 at S2923). This tool does NOT increment either count — gateway-wide first-hop-literal count stays at 1/17 post-batch-7 (also confirmed by peer `proactive_tool` in this batch).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification on all 6 actions (4 pure-READ + 1 mutation + 1 hybrid-write) appended to the S2924 handoff. Expected envelope shapes documented in §4 golden-path examples.

**Post-merge verification protocol:**

For `profile`:
1. Dispatch `{"action": "profile"}`.
2. Response envelope: `{action, profile: {...} | null, message?}`.
3. If profile exists (non-null): ORM cross-check `ExtendedUserProfile.objects.get(user_id=<current_user_id>)` — every field in envelope matches the ORM row.
4. If profile is null: envelope's `message` == 'No extended profile found'. No side effect.

For `skills` (**S2925: Ledger #33 resolved via code fix — verify-unblocked**):
1. Dispatch `{"action": "skills"}`.
2. Expected response envelope: `{action, count, skills: [...], source: 'extended_user_profile.skills'}` with `count == len(skills)` and `count ≤ 50`.
3. ORM cross-check: `ExtendedUserProfile.objects.get(user_id=<current_user_id>).skills[:50]` — envelope entries match the JSON list in list order after per-entry normalization.
4. **Empty case:** user has no `ExtendedUserProfile` row OR `skills` field is empty → envelope is `{action: 'skills', count: 0, skills: [], source: 'extended_user_profile.skills'}` (no error).

For `learning_summary` (**S2925: Ledger #33 resolved via code fix — verify-unblocked**):
1. Dispatch `{"action": "learning_summary"}`.
2. Expected response envelope: `{action, total_skills, by_category: {...}, avg_years, source: 'extended_user_profile.skills'}`.
3. ORM cross-check: `total_skills == len(ExtendedUserProfile.objects.get(user_id=<current_user_id>).skills)`; `by_category` counts match a Python `Counter` over the `category` field (default `uncategorized`); `avg_years == mean(years)` across entries with numeric `years` (0 if none).
4. **Empty case:** returns `{action, total_skills: 0, by_category: {}, avg_years: 0, source: 'extended_user_profile.skills'}`.

For `preferences` (READ + implicit first-touch write):
1. Before dispatch, capture `EnhancedUserProfile.objects.filter(user_id=<current_user_id>).exists()`.
2. Dispatch `{"action": "preferences"}`.
3. Response envelope: `{action, preferences: {...12 fields...}}`.
4. If pre-existed: ORM cross-check `EnhancedUserProfile.objects.get(user_id=<current_user_id>)` — every field in envelope matches.
5. If did NOT pre-exist: ORM cross-check now shows `EnhancedUserProfile.objects.filter(user_id=<current_user_id>).exists() == True` — the implicit first-touch write fired. All 12 preference fields are null/empty defaults. This validates the `spreading` classification's implicit-write half.

For `update_preferences`:
1. Capture current value of a preference field: `enhanced.time_zone` (or any of the 12 whitelisted fields).
2. Dispatch `{"action": "update_preferences", "field": "time_zone", "value": "America/Denver_S2924_probe"}`.
3. Response envelope: `{action, updated_fields: ["time_zone"], count: 1, success: true}`.
4. ORM cross-check: `EnhancedUserProfile.objects.get(user_id=<current_user_id>).time_zone == "America/Denver_S2924_probe"`.
5. Unknown-field silent-drop check: dispatch `{"action": "update_preferences", "field": "nonexistent_field", "value": "x"}` → expect `{action, updated_fields: [], count: 0, success: false}`.
6. Cleanup: restore captured value via same dispatch shape.

For `desk_preferences`:
1. Dispatch `{"action": "desk_preferences", "desk": "sports"}`.
2. Response envelope: `{action, desk: "sports", communication_style, long_term_goals, decision_framework, current_learning_goals, context: "Sports betting preferences and risk tolerance", available_desks: ["sports", "stocks", "content", "general"]}`.
3. Repeat for `"stocks"`, `"content"`, `"general"` — each returns the correct `context` string and the projection fields per `DESK_PROJECTIONS` dict.
4. Unknown-desk fallback check: dispatch `{"action": "desk_preferences", "desk": "unknown"}` → envelope has `desk: "unknown"` but `context: "General platform preferences"` (fallback context, inconsistent-desk-string sharp edge documented in §5).

**Signal-cascade non-fire assertion for both mutation paths:** all writes go to `EnhancedUserProfile`. No `@receiver(post_save|pre_save, sender=EnhancedUserProfile)` decorators + no dynamic `post_save.connect(..., sender=EnhancedUserProfile, ...)` — grep receipts in Rigby T0 SIGN turn 1. If any `[PROFILE_*_SIGNALS]` or `[ENHANCED_PROFILE_*]` action log line appears in worker logs during verify, the `spreading` classification is invalidated (would indicate an unobserved cascade) and this doc is amended.

## Related

- **Adjacent tools:** `proactive_tool` (this batch — spreading peer; proactive is the "gap" archetype vs profile's "clean" archetype); `personal_assistant_interviewer` (populates same substrate via interview, not CRUD); `governance_tool` (advisor identity/routing — different substrate); `self_awareness_tool` (batch 4 — system introspection, not user profile).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1 — §5a 4-tier blast-radius taxonomy from S2921); models: `core/models/__init__.py` (`ExtendedUserProfile`, `EnhancedUserProfile`); `core/models_user_learning.py` (`UserSkill`).
- **Prior ratifications:** S2892 Path B open, S2918–S2923 Slice 4 batches 1–6, S2921 §5a 4-tier taxonomy amendment, S2923 latent-cascade authoring convention.
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 21st instance** — corroborating post-threshold. Short "now systemic" note surfaced at Slice-4 close per S2924 Q5(iii) Chris ratification. Substrate arc still gated on explicit Chris directive per 00-START forbidden-list.
  - **`updates` bulk-dict form accepted by handler but absent from schema** — 1st Slice-4 instance of "handler accepts bulk form but schema surfaces only single form". Recorded as Ledger candidate; 2nd instance triggers Fold evaluation.
  - **`preferences` action implicit first-touch write** — Ledger candidate: "READ action name with side effect of new-row creation". Documented as `spreading` per template but caller-visible name says `preferences` (read shape). Not documented in schema description. 1st observation; 2nd instance triggers Fold evaluation.
  - **Error-envelope-shape divergence for `preferences`/`update_preferences`/`desk_preferences`** — these use `{action, error: <str>}` (in-shape) rather than the standard `{error: <str>}` envelope. 1st Slice-4 instance of "error field embedded in success-shape envelope"; Ledger candidate.
  - **Silent-drop of unknown fields in `update_preferences`** — no per-field rejection feedback. Caller only sees smaller `count` than requested. Sharp edge; Ledger candidate for "silent whitelist filtering without per-item feedback" pattern.
