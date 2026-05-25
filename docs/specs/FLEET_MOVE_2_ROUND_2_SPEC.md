---
title: "Fleet Move 2 Round 2 — List endpoint + Retention/TTL (spec)"
status: implemented
session_drafted: 1129
session_implemented: 1130
date: 2026-05-22
authors: ["rigby (PA, conversation pa-d19c1674b936)", "claude-code"]
implements: ["Session 1130 (or later) — Move 2 Round 2"]
depends_on:
  - "docs/specs/FLEET_MOVE_1_AND_2_SPEC.md"
  - "docs/handoffs/SESSION_1129_*.md (Move 1 + Move 2 R1)"
  - "PR #2130 (u-d-b Move 2 R1)"
  - "contract-concierge#12 + 6 fleet back-prop PRs"
---

# Fleet Move 2 Round 2 — Spec

> **What this doc is.** Concrete implementation spec for Round 2 of
> Move 2 — the **list endpoint** + **retention/TTL** layer that sits
> on top of Round 1's push/pull surface. Drafted by Rigby in
> conversation `pa-d19c1674b936` after Move 2 Round 1 + back-prop
> shipped. Same format as the Move 1+2 spec: implement straight from
> this file; if you find yourself making a judgment call that isn't
> in the spec, brief Rigby before coding.

## Arc context

Round 1 (shipped) gave fleet apps the smallest push-then-pull surface
under fleet auth. Round 2 makes that surface usable in practice:

- **List endpoint** — apps can see what they've stored. Without this,
  an artifact id lost client-side is unrecoverable.
- **TTL + cleanup** — artifacts don't pile up forever. Soft delete
  semantics in MLC; hard delete deferred.

What Round 2 explicitly does NOT touch: cross-app sharing, multiple
artifact types, versioning, blob storage, search. See "Non-goals"
below.

## Design goals (locked with Rigby)

1. **No existence leaks.** Same posture as Round 1's cross-identity
   pull: a different app's artifact, an expired artifact, and a
   soft-deleted artifact all return the same response (`404` for
   pull, `not in list` for list).
2. **Simple pagination.** Offset/limit. Cursor is a Round 3+ concern.
3. **Soft delete in the contract, hard delete behind the scenes.**
   `deleted_at` is the user-visible state; hard purge is operational.
4. **Deterministic default TTL.** Globally configurable
   (`FLEET_ARTIFACT_DEFAULT_TTL_DAYS = 30`). Per-push override is a
   stretch option, not the default.

---

# 1) List Endpoint

## 1.1 Contract

`GET /api/fleet/artifacts/`

**Auth:** `FleetSignatureExclusiveAuthentication` required (same
pattern as push/pull).

**Ownership rule:** the caller's fleet identity (`app_slug`) is
auto-applied as the scope. The endpoint must never return artifacts
owned by a different identity, regardless of query params.

## 1.2 Query parameters

All optional unless noted.

| Param | Type | Default | Notes |
|---|---|---|---|
| `limit` | int | 25 | Max 100 — clamp, don't 400 |
| `offset` | int | 0 | |
| `artifact_type` | string enum | (any) | `json` for R1; add `markdown` if Round 3 brings it |
| `created_after` | ISO-8601 datetime | (none) | Inclusive lower bound on `created_at` |
| `created_before` | ISO-8601 datetime | (none) | Exclusive upper bound on `created_at` |
| `include_expired` | bool | false | When false, exclude rows where `now > expires_at` |
| `include_deleted` | bool | false | When false, exclude rows where `deleted_at IS NOT NULL` |

**NO `created_by` param.** Caller identity is the only valid scope —
adding a `created_by` param is a footgun and a leak vector.

## 1.3 Ordering

Default: `-created_at` (newest first). **Use a tiebreaker** —
`(-created_at, -id)` — to keep pagination stable across rows sharing
a timestamp. Without the tiebreaker, offset pagination can skip or
duplicate rows.

## 1.4 Response shape

200 OK:

```json
{
  "count": 123,
  "limit": 25,
  "offset": 0,
  "next_offset": 25,
  "results": [
    {
      "id": "<uuid>",
      "artifact_type": "json",
      "sha256": "<hex>",
      "size_bytes": 1234,
      "created_at": "2026-05-22T18:22:11Z",
      "expires_at": "2026-06-21T18:22:11Z",
      "is_expired": false,
      "deleted_at": null,
      "metadata": { "job_id": "..." }
    }
  ]
}
```

Notes:

- **Include `metadata`** in summaries. It's only the caller's own
  artifacts; useful for joining to jobs without extra indexing. Cap
  metadata size at push time if size becomes an issue.
- `count` is post-filter (respects `include_expired` / `include_deleted`).
- `next_offset` is `offset + len(results)` when more results exist,
  else `null`.
- **No payload bodies** in list — that's what pull is for.

## 1.5 Empty + error behavior

- Empty result → 200 with `{"count": 0, "limit": ..., "offset": ..., "next_offset": null, "results": []}`. Not 204.
- Bad datetime format → 400 with DRF-style error body.
- `limit > 100` → clamp to 100 (don't 400). Be consistent.

---

# 2) Retention + TTL

## 2.1 Data model changes (migration 0344)

Add to `FleetArtifact`:

| Column | Type | Notes |
|---|---|---|
| `expires_at` | datetime | Nullable initially (backfill); make non-null after migration |
| `deleted_at` | datetime, nullable | Set by cleanup job on expiry |
| `delete_reason` | string, nullable | `expired` / `manual` / `admin` / `cleanup_hard_delete` (future) |
| `retention_days` | int, nullable | OPTIONAL — only if you support per-push TTL override |

## 2.2 Soft delete vs hard delete

**Contract (R2):** soft delete is the user-visible state.

An artifact is treated as "not found" when **any** of:

- Different identity (cross-identity)
- `deleted_at IS NOT NULL` (soft-deleted)
- `now > expires_at` AND caller didn't pass `include_expired=true` on list
- Expired on pull (always — pull has no `include_expired` knob)

**Cleanup side effects:**

- Cleanup job sets `deleted_at = now` + `delete_reason = "expired"`
- Hard delete (free disk) deferred to Round 3+ or operational toggle
- Do NOT bake hard delete into the Round 2 contract

## 2.3 Default TTL + configuration

Single global setting:

```python
FLEET_ARTIFACT_DEFAULT_TTL_DAYS = 30
```

**Per-type TTLs** are Round 3+. Don't add them unless you add
multiple types in R2 (which is non-goal per below).

## 2.4 How TTL is set (push behavior)

**MLC recommendation (safe):** TTL is **not user-provided**.
`expires_at` is computed server-side at create time:

```python
expires_at = created_at + timedelta(days=FLEET_ARTIFACT_DEFAULT_TTL_DAYS)
```

This avoids:

- Apps setting infinite TTL accidentally
- TTL negotiation / versioning complexity
- Per-identity capability sprawl

**Stretch option (only if explicitly wanted):** allow `ttl_days` in
POST body, constrained:

- `min = 1`, `max = FLEET_ARTIFACT_MAX_TTL_DAYS` (e.g., 90)
- Default to `FLEET_ARTIFACT_DEFAULT_TTL_DAYS` when absent
- Store the requested value in `retention_days`

If you ship the stretch option, add one test that `ttl_days > max`
is clamped to max (and stored consistently — clamp BEFORE compute, not
after).

## 2.5 Pull behavior for expired / deleted

**Use `404 Not Found` for all of these:**

- Artifact doesn't exist
- Artifact exists but belongs to a different fleet identity
- Artifact is expired
- Artifact is soft-deleted

**Rationale:** preserves the no-existence-leak invariant. Don't
introduce `410 Gone` variants. Don't include extra hints in the
response body for these 404s.

For auth failures, the existing `deny_code` body shape stays.

## 2.6 List behavior for expired / deleted (recap)

- Default list excludes expired AND deleted.
- `include_expired=true` includes expired (but still excludes
  deleted unless `include_deleted=true` also).
- `include_deleted=true` includes soft-deleted rows (caller-owned
  only, as always).

---

# 3) Cleanup job

## 3.1 Mechanism

Celery beat scheduled task. Optional management command that calls
the same shared function (DRY).

## 3.2 Frequency

- **Production default:** daily (e.g. 02:10 AM MST).
- Staging may want hourly for faster feedback. Don't ship hourly to
  prod by default.

## 3.3 Selection logic

```sql
WHERE expires_at <= now()
  AND deleted_at IS NULL
```

## 3.4 Action

**Soft delete only:**

- `deleted_at = now()`
- `delete_reason = "expired"`

Do NOT hard-delete in Round 2.

## 3.5 Batching + caps

- Process in batches of **500** to avoid long transactions / locks
- Cap **5,000** rows per run — prevents runaway cleanup if something
  goes off the rails
- Loop until no more eligible rows OR cap reached

## 3.6 Idempotency

Must be idempotent:

- Filter `deleted_at IS NULL` so re-running on an already-cleaned row
  is a no-op
- Repeated runs should not error and should not change already-deleted
  rows

## 3.7 Observability (minimal)

Log per-run counters:

- `scanned` / `eligible`
- `soft_deleted`
- `capped: bool`

Optional lightweight audit/event row, not required for MLC.

---

# 4) Migration story (0344)

## 4.1 Steps

1. **Add columns nullable** to avoid locks:
   - `expires_at` (datetime, null=True)
   - `deleted_at` (datetime, null=True)
   - `delete_reason` (string, null=True)
   - (Optional) `retention_days` (int, null=True)
2. **Data migration:** for rows where `expires_at IS NULL`:
   - `expires_at = created_at + timedelta(days=FLEET_ARTIFACT_DEFAULT_TTL_DAYS)`
   - (Optional) `retention_days = FLEET_ARTIFACT_DEFAULT_TTL_DAYS`
3. **Follow-up schema step (recommended):** set `expires_at`
   `null=False` after backfill completes.

If you'd rather avoid the second migration, leave `expires_at`
nullable and treat null as "not expired" — but only for the pre-
backfill window. Rigby's preference: backfill then make non-null.

## 4.2 Indexes (Postgres)

- `(created_by_identity_id, created_at DESC, id DESC)` — for the
  list endpoint
- `(created_by_identity_id, expires_at)` — for cleanup scans
- Partial index `(expires_at) WHERE deleted_at IS NULL` — optional;
  useful if cleanup queries become global (cross-identity)

No pgvector indexes needed.

---

# 5) Acceptance criteria (R2 is "done" when all pass)

1. **List returns only caller-owned**
   - Create artifacts for identity A and B
   - Signed GET list as A returns only A's artifacts (never B)
   - Count + ordering correct

2. **List pagination works**
   - Create more than `limit` artifacts for identity A
   - `limit=10&offset=0` returns 10, `next_offset=10`
   - `offset=10` returns next page; stable ordering with
     `(-created_at, -id)` even when timestamps tie

3. **List filtering works**
   - Filter by `artifact_type=json` returns correct subset
   - `created_after`/`created_before` window returns the right rows

4. **Expired artifacts hidden by default**
   - Create artifact with `expires_at` in the past
   - Pull returns 404
   - List doesn't include it unless `include_expired=true`

5. **Cleanup job soft-deletes expired**
   - Create expired artifact with `deleted_at IS NULL`
   - Run cleanup task
   - Artifact has `deleted_at != null` + `delete_reason = "expired"`
   - Pull returns 404
   - List excludes unless `include_deleted=true` is passed

6. **Cleanup is idempotent**
   - Run cleanup twice; second run performs 0 updates and does not
     error

If you ship the per-push `ttl_days` stretch option, add one more
test: `ttl_days > max` is clamped to max and persisted consistently.

---

# 6) Non-goals (explicitly NOT in Round 2)

To keep R2 tight:

- Cursor-based pagination
- Full-text search over metadata
- Cross-identity sharing / visibility controls
- Hard deletion / storage reclamation guarantees
- Multiple artifact types beyond what already exists (no
  `markdown` / `binary` in R2 unless explicitly opted in)
- Multipart uploads / streaming downloads
- Presigned URLs / object storage integration (S3/GCS/Cloudinary)
- Artifact versioning (no `version`, no "latest", no overwrite)
- Artifact updates/patches (no `PUT`/`PATCH`)
- Admin "global list" across identities (would need superuser /
  internal-only controls)
- Search beyond simple filters (no metadata search, no tag query
  language)
- Per-identity TTL policies / negotiated capabilities
- Legal hold / retention exceptions
- Webhooks / events on create/expire/delete
- Analytics dashboards beyond basic logging

---

# 7) Final gotchas (before coding)

1. **404 for anything not readable** — missing, cross-identity,
   expired, deleted. Strongest non-leak invariant; don't introduce
   410/403 variants.
2. **List must auto-scope to caller identity.** Do NOT accept
   `created_by=` query param.
3. **Stable ordering with offset pagination** — `(-created_at, -id)`
   tiebreaker. Without it, duplicates/missing rows across pages.
4. **Datetime parsing strict** — ISO-8601. Lock down whether you
   accept `Z` only vs timezone offsets early. DRF handles both;
   tests should pin the contract.
5. **Cleanup: filter `deleted_at IS NULL`, batch updates, cap per
   run.** Idempotency depends on the filter.
6. **Migration backfill safety** — add nullable → backfill →
   (optionally) make `expires_at` non-null. Don't ship a migration
   that table-locks production.
7. **Middleware interactions** — `/api/fleet/artifacts/` is already
   in `OPTIONAL_AUTH_PATHS` from Round 1 (the prefix covers the new
   list endpoint). Any future fleet routes need this added.

---

# 8) Go/no-go staging/prod checklist (for Chris)

## Pre-merge

- [ ] u-d-b PR merged first (models + endpoint + migration 0344)
- [ ] Fleet repo PRs merged after (any list-endpoint client helpers)
- [ ] CI green across u-d-b + all 7 fleet apps

## Provisioning / Identity

- [ ] Fleet identities provisioned for all 7 apps
- [ ] Each fleet app has correct `DEFAULT_APP_SLUG`
- [ ] Signing secrets in deployment env (no placeholders)
- [ ] Clock-sync sanity — timestamp skew bites silently

## Deploy hygiene

- [ ] u-d-b web service deployed
- [ ] Migration 0344 applied
- [ ] Restart celery workers (PA + long-running at minimum)
- [ ] Beat schedule loaded — confirm cleanup task is registered

## Smoke (contract-concierge + one other app first, then scale)

- [ ] Signed POST `/api/fleet/artifacts/` → 201 with id, sha256
- [ ] Signed GET `/api/fleet/artifacts/{id}/` → 200, sha256 matches
- [ ] Signed GET `/api/fleet/artifacts/?limit=5` → 200, includes
      the new artifact
- [ ] Cross-identity GET → 404 (no leak)
- [ ] Missing/invalid signature → 403 with deny_code

## Retention validation

- [ ] Create artifact with `expires_at` forced past (admin tweak OR
      temporary `FLEET_ARTIFACT_DEFAULT_TTL_DAYS = 0` in staging)
- [ ] Run cleanup task manually
- [ ] Artifact non-fetchable (404); excluded from default list
- [ ] `include_deleted=true` shows it with populated `deleted_at`

## Rollback

- [ ] Cleanup beat task can be disabled without touching push/pull
      (feature flag or schedule toggle)
- [ ] `OPTIONAL_AUTH_PATHS` entries are revertable cleanly if a
      conflict emerges
