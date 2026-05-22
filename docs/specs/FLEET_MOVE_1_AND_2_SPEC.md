---
title: "Fleet Move 1 + Move 2 — Service identity + Artifact push/pull (spec)"
status: spec
session: 1128
date: 2026-05-22
authors: ["rigby (PA, conversation pa-d19c1674b936)", "claude-code"]
implements: ["Session 1129 Phase 2C", "Session 1130 Phase 2D"]
depends_on: ["docs/handoffs/SESSION_1127_FLEET_ROUTING_PHASE_2A.md", "docs/handoffs/SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md"]
---

# Fleet Move 1 + Move 2 — Spec

> **What this doc is.** Concrete implementation spec for the next two
> moves in the fleet connection arc, as drafted by Rigby in
> conversation `pa-d19c1674b936` after Phase 2B shipped. Implement
> straight from this file — endpoints, headers, payloads, edge cases
> are all decided. If you find yourself making a judgment call that
> isn't in this doc, brief Rigby before coding.
>
> Move 1 (service identity + signed requests) is the foundation that
> unlocks every subsequent move in the arc (artifacts, events, global
> user mapping, cross-app workflows). Move 2 (artifact push/pull)
> turns u-d-b from "the brain that answers questions" into "the brain
> that delivers work products," which is the next user-visible win
> after Phase 2.

## Arc context

Five-move connection arc (full version in
`docs/handoffs/SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md`):

1. **Service identity + signed requests** ← this doc
2. **Artifact push/pull** ← this doc
3. Fleet event stream (Redis Streams / NATS / Kafka if needed; start
   DB-stored fanout)
4. Global user mapping (SSO-lite — `global_user_id`, no DB merge)
5. Cross-app workflows (orchestration on top of 1-4)

Rigby's foundation pick: **Move 1**. Difference between "apps can ask
the brain" (today) and "apps can safely participate in a shared
operating system" (where we want to be).

---

# Move 1 — Service identity + signed requests

## 1.1 Goals / non-goals

- **Goal:** u-d-b can *trust* "this request came from
  `contract-concierge` service" independent of user input.
- **Goal:** enforce **token → app_slug binding** and **capabilities per
  route** (e.g., can request `mode=force`, can push artifacts).
- **Goal:** backward compatible with existing PA auth for
  `/api/brain/ask` → `/api/pa/chat/`.
- **Non-goal:** end-user SSO (that's Move 4).

## 1.2 Where service identities live

Django models in u-d-b. Source of truth; secrets stored hashed.

### `FleetServiceIdentity`

| Field | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `app_slug` | string, unique | e.g. `"contract-concierge"` |
| `name` | string | Human label |
| `status` | enum | `active` \| `disabled` \| `rotating` |
| `created_at`, `updated_at`, `last_used_at` | datetime | |
| `allowed_routes` | json list | e.g. `["/api/pa/chat/", "/api/fleet/artifacts/push", "/api/fleet/artifacts/pull"]` |
| `capabilities` | json dict | See shape below |
| `metadata` | json | Optional, e.g. repo url |

**Capabilities shape**:

```json
{
  "routing": {
    "can_request_hint": true,
    "can_request_force": true
  },
  "artifacts": {
    "can_pull": true,
    "can_push": true,
    "max_payload_kb": 512,
    "max_retention_days": 365,
    "can_cross_app": false
  },
  "events": {
    "can_emit": false
  }
}
```

### `FleetServiceKey` (separate from identity for clean rotation)

| Field | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `service_identity_id` | FK | → `FleetServiceIdentity` |
| `key_id` | string, unique | e.g. `"fs_contractconcierge_k1"` |
| `secret_hash` | string | `SHA256(secret)` minimum; `pbkdf2`/`bcrypt` if paranoid (secrets are random 32B so SHA256 is usually fine) |
| `status` | enum | `active` \| `draining` \| `disabled` |
| `created_at`, `last_used_at` | datetime | |
| `not_before`, `not_after` | datetime, nullable | Optional explicit validity window |

### `FleetServiceRotation` (optional but recommended for ops cleanliness)

| Field | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `service_identity_id` | FK | |
| `old_key_id` | string | |
| `new_key_id` | string | |
| `status` | enum | `planned` \| `active` \| `completed` \| `aborted` |
| `starts_at`, `ends_at` | datetime | |
| `notes` | text | |

**Secrets manager**: store raw secrets only in Railway/infra secrets for
the fleet apps. u-d-b stores only hashes.

## 1.3 Token & signature scheme — HMAC-SHA256

HMAC-SHA256 with per-service shared secret. Simplest to implement across
Python services; avoids JWT key distribution overhead.

### Required headers (for service-authenticated requests)

| Header | Example | Purpose |
|---|---|---|
| `X-Fleet-App` | `contract-concierge` | Informational; must match identity |
| `X-Fleet-Key-Id` | `fs_contractconcierge_k1` | Which key to verify against |
| `X-Fleet-Timestamp` | `1716399082` | Unix seconds, string-encoded |
| `X-Fleet-Nonce` | `<uuid4>` | Replay protection |
| `X-Fleet-Signature` | `<base64 HMAC>` | The signature |
| `X-Request-Id` | `<uuid4>` | Optional; tracing |

### Signature base string (canonical)

```
signature_base =
  METHOD          + "\n" +
  PATH            + "\n" +    # URL path only; querystring policy below
  X-FLEET-APP     + "\n" +
  X-FLEET-KEY-ID  + "\n" +
  X-FLEET-TIMESTAMP + "\n" +
  X-FLEET-NONCE   + "\n" +
  SHA256_HEX(RAW_BODY_BYTES)
```

Compute:

```python
sig = hmac.new(secret, signature_base.encode(), hashlib.sha256).digest()
header = base64.b64encode(sig).decode()
```

### Querystring policy

- For `POST/PUT/PATCH`: querystring is **not** signed. Use body for
  parameters.
- For `GET` (pull endpoints): `PATH` in the signature base must
  include the full querystring (path + `?` + sorted query). This
  prevents query tampering on pull requests, which carry filters but
  no body.

### Replay protection

u-d-b verifies, in order:

1. `abs(now - X-Fleet-Timestamp) <= 300` seconds
2. `(key_id, nonce)` tuple not previously seen in last 10 minutes
   (Redis SET with TTL 600s; if `SETNX` returns 0, it's a replay)

## 1.4 What u-d-b enforces

### Binding / trust rules (all must hold)

1. Resolve identity by `X-Fleet-Key-Id`.
2. Verify signature using that key's secret.
3. Enforce `X-Fleet-App == identity.app_slug` (else `app_slug_mismatch`).
4. **Ignore any `context.app_slug` in the JSON body unless
   service-authenticated.** When authenticated, u-d-b **overwrites**
   `context.app_slug = identity.app_slug` server-side. Never trust
   client-supplied app_slug for signed requests.

### Per-route capability gates (examples)

| Route | Service-auth | Additional capability |
|---|---|---|
| `/api/pa/chat/` (no routing block) | optional | none |
| `/api/pa/chat/` (with routing block) | required | `routing.can_request_hint` or `.can_request_force` |
| `/api/pa/chat/` (`routing.mode=force`) | required | `routing.can_request_force=true` |
| `/api/fleet/artifacts/push` | required | `artifacts.can_push=true`, enforce `max_payload_kb` |
| `/api/fleet/artifacts/pull` | required | `artifacts.can_pull=true` |

### Backward-compat invariant

Current `/api/brain/ask` → `/api/pa/chat/` calls must keep working.
Enforcement rules:

- If request is **not** fleet-signed:
  - `/api/pa/chat/` works as user-auth / PA-token (existing behavior).
  - u-d-b **must ignore/strip** any incoming `routing` block AND any
    `context.app_slug` that claims fleet identity.
  - Internal flag: `context._fleet_auth = {"trusted": false, "reason": "missing_signature"}`.

- If request **is** fleet-signed:
  - `context.app_slug` is set from identity (server-side).
  - `routing` block is enforced subject to capabilities.

### Grace-period feature flags

| Setting | Default | Purpose |
|---|---|---|
| `FLEET_AUTH_ENFORCE_ROUTING` | `true` | Reject routing blocks without signature |
| `FLEET_AUTH_ENFORCE_ARTIFACTS` | `true` | Reject artifact endpoints without signature |
| `FLEET_AUTH_LOG_ALL` | `false` | Log every fleet-headers / fleet-route / routing-block request, not just failures |

## 1.5 Failure modes + audit logs

### Canonical error response (4xx)

```json
{
  "error": {
    "code": "signature_mismatch",
    "message": "Invalid fleet signature",
    "request_id": "<uuid4>",
    "app_slug_claimed": "contract-concierge",
    "key_id": "fs_contractconcierge_k1"
  }
}
```

### Canonical error codes (MUST NOT drift)

| Code | Status | Category |
|---|---|---|
| `missing_fleet_headers` | 401 | Required headers absent |
| `malformed_fleet_headers` | 401 | Timestamp non-int, nonce invalid, sig not base64 |
| `unknown_key_id` | 401 | No matching `FleetServiceKey` row |
| `service_disabled` | 401 | Identity or key disabled |
| `timestamp_skew` | 401 | `|now - claimed| > 300s` |
| `replay_nonce` | 401 | `(key_id, nonce)` already seen in TTL |
| `signature_mismatch` | 401 | HMAC didn't match |
| `app_slug_mismatch` | 403 | `X-Fleet-App != identity.app_slug` |
| `capability_denied` | 403 | Signed + bound, but not allowed for this route/mode |
| `route_not_allowlisted` | 403 | (Alias of `capability_denied` if you split allow_routes) |
| `payload_too_large` | 413 | Exceeds `max_payload_kb` |
| `content_type_not_allowed` | 415 | Non-JSON where required |

### `FleetAuthAuditLog` — one shape across all failures

Logged for every request that **either**: presents fleet headers, OR
hits a fleet-only endpoint, OR contains a `routing` block.

```json
{
  "id": "uuid",
  "occurred_at": "2026-05-22T18:31:22Z",
  "request_id": "<uuid4>",

  "method": "POST",
  "path": "/api/pa/chat/",
  "query": "",
  "status_code": 401,
  "result": "deny",
  "deny_code": "signature_mismatch",

  "key_id": "fs_contractconcierge_k1",
  "app_slug_claimed": "contract-concierge",
  "app_slug_resolved": null,

  "timestamp_claimed": 1716399082,
  "timestamp_delta_seconds": 2,
  "nonce": "<uuid4>",
  "replay_detected": false,

  "body_sha256": "<hex>",
  "sig_present": true,

  "ip": "10.0.0.12",
  "user_agent": "contract-concierge/1.2",
  "latency_ms": 4,

  "notes": {
    "capability_required": null,
    "capability_granted": null
  }
}
```

### Per-failure-mode notes (what to fill in `notes`)

| Code | Notes to set |
|---|---|
| `missing_fleet_headers` | `sig_present=false`, `key_id=null`, `notes.reason="required_for_routing_or_artifact"` |
| `unknown_key_id` | `key_id=<claimed>`, `notes.reason="no_matching_key"` |
| `service_disabled` | `app_slug_resolved` may be set, `notes.status="disabled"` |
| `timestamp_skew` | `timestamp_delta_seconds` set, `notes.allowed_window_seconds=300` |
| `replay_nonce` | `replay_detected=true`, `notes.nonce_ttl_seconds=600` |
| `signature_mismatch` | `notes.hash="<sha256-hex>"` (don't log full base string — may include sensitive path/query) |
| `app_slug_mismatch` | `app_slug_resolved=<identity.app_slug>`, `notes.mismatch={"claimed": "...", "resolved": "..."}` |
| `capability_denied` / `route_not_allowlisted` | `app_slug_resolved`, `notes.capability_required`, `notes.capability_granted=false`, `notes.route=<path>` |

## 1.6 Bootstrap + rotation

### Provisioning (admin-only)

`POST /api/admin/fleet/identities/provision`

Request:

```json
{
  "app_slug": "contract-concierge",
  "name": "Contract Concierge",
  "capabilities": {
    "routing": { "can_request_hint": true, "can_request_force": true },
    "artifacts": { "can_pull": true, "can_push": true, "max_payload_kb": 512 }
  },
  "allowed_routes": [
    "/api/pa/chat/",
    "/api/fleet/artifacts/push",
    "/api/fleet/artifacts/pull"
  ]
}
```

Response (**only time raw secret is returned**):

```json
{
  "service": {
    "app_slug": "contract-concierge",
    "status": "active",
    "capabilities": { "...": "..." },
    "allowed_routes": ["..."]
  },
  "key": {
    "key_id": "fs_contractconcierge_k1",
    "secret": "<32-byte base64>",
    "created_at": "2026-05-22T18:31:22Z"
  },
  "next_steps": {
    "set_env": [
      "FLEET_APP_SLUG=contract-concierge",
      "FLEET_KEY_ID=fs_contractconcierge_k1",
      "FLEET_SERVICE_SECRET=<secret>"
    ],
    "verify": "Call POST /api/pa/chat/ with signed headers; confirm audit log allow."
  }
}
```

After provisioning:

- u-d-b persists only `secret_hash` + metadata + capabilities + `allowed_routes`.
- Fleet app stores raw `secret` in its deployment secrets (Railway env).

### Rotation lifecycle

Use explicit key objects + rotation state so transitions are auditable.

#### 1. Plan

`POST /api/admin/fleet/identities/{app_slug}/rotate/plan`

```json
{ "ends_in_hours": 72 }
```

Response:

```json
{
  "rotation": {
    "id": "<uuid>",
    "status": "planned",
    "old_key_id": "fs_contractconcierge_k1",
    "new_key_id": "fs_contractconcierge_k2",
    "ends_at": "..."
  },
  "new_secret": "<raw>"
}
```

Creates `k2` as `active`. Old key stays `active` until activate step.

#### 2. Activate

`POST /api/admin/fleet/rotations/{rotation_id}/activate`

- `rotation.status = active`, `starts_at = now`
- old key `status = draining` (still accepted, flagged in logs)

#### 3. Complete

`POST /api/admin/fleet/rotations/{rotation_id}/complete`

Preconditions:
- `new_key.last_used_at` within last 6 hours, OR admin override `force=true`

Behavior:
- old key `status = disabled`, `not_after = now`
- rotation `status = completed`
- identity `status = active`

#### 4. Abort (if rollout failed)

`POST /api/admin/fleet/rotations/{rotation_id}/abort`

- new key `status = disabled`
- old key restored to `active`
- rotation `status = aborted`

### Verification during rotation

u-d-b accepts signatures from any `FleetServiceKey` where:
- `status in {active, draining}` AND
- `now` within `[not_before, not_after]` if set

### Rotation audit logs

All admin actions → `AdminAuditLog`:
- `action`: `fleet.rotate.plan|activate|complete|abort`, `fleet.key.disable`
- `actor`, `app_slug`, `key_ids`, `rotation_id`
- include `force=true` flag if completion was forced

---

# Move 2 — Artifact push/pull

## 2.1 Artifact data model

### Two IDs

- `artifact_id` (uuid): stable logical identity (same across versions)
- `id` (uuid): specific version row PK (or reuse `(artifact_id, version)` unique constraint)

Constraints:
- Unique: `(artifact_id, version)`
- `latest_version` queryable by `max(version) WHERE status != 'revoked'`

### `FleetArtifact` — canonical shape

```json
{
  "artifact_id": "uuid",
  "version": 1,
  "status": "ready",

  "type": "contract_draft",
  "title": "Mutual NDA Draft (v1)",
  "summary": "Draft NDA based on user inputs ...",

  "format": "markdown",
  "mime_type": "text/markdown",
  "size_bytes": 18234,
  "payload_sha256": "<hex>",
  "payload": "# Agreement...\n...",
  "payload_blob_url": null,

  "created_at": "2026-05-22T18:31:22Z",

  "created_by": {
    "app_slug": "contract-concierge",
    "service_key_id": "fs_contractconcierge_k1",
    "request_id": "<uuid>",
    "user": {
      "global_user_id": "<uuid-or-null>",
      "app_user_id": "<string-or-null>"
    }
  },

  "provenance": {
    "created_by_agent": "LegalDocDrafterAgent",
    "deliberation": {
      "panel": ["EditorAgent", "LegalDocDrafterAgent", "DecisionEnforcerAgent"],
      "quality_gate": "3-reviewer",
      "confidence": 0.82,
      "gate_passed": true,
      "gate_id": "GATE-optional",
      "agent_execution_ids": ["<uuid>"],
      "review_artifacts": {
        "brainstorm_id": "optional",
        "conversation_id": "optional"
      }
    },
    "source": {
      "workspace_id": "<uuid-or-null>",
      "initiative_id": "<uuid-or-null>",
      "deliverable_id": "<uuid-or-null>",
      "blog_id": "<uuid-or-null>",
      "external_source": {
        "type": "user_upload|url|spider_data|kb_document|other",
        "id": "<string-or-null>",
        "url": "<string-or-null>"
      }
    }
  },

  "citations": [
    {
      "citation_id": "<uuid-optional>",
      "type": "url|document|spider_data|kb_chunk|manual_note",
      "title": "<optional>",
      "url": "<optional>",
      "source_id": "<optional>",
      "retrieved_at": "<iso-optional>",
      "sha256": "<hex-optional>",
      "quote": "<optional>",
      "notes": "<optional>"
    }
  ],

  "workspace": {
    "workspace_id": "<uuid-or-null>",
    "workspace_name": "<optional>"
  },

  "visibility": {
    "scope": "service|user|public|internal",
    "allowed_app_slugs": ["contract-concierge"],
    "data_sensitivity": "public|internal|confidential|restricted"
  },

  "lifecycle": {
    "retention_days": 90,
    "expires_at": "<iso-or-null>",
    "revoked_at": "<iso-or-null>",
    "revoked_reason": "<string-or-null>",
    "supersedes": { "artifact_id": "<uuid>", "version": 1 },
    "superseded_by": { "artifact_id": "<uuid>", "version": 2 }
  }
}
```

### Status enums

`status` (version state):

| Value | Meaning |
|---|---|
| `ready` | Normal — return on pulls |
| `superseded` | Older version, still readable |
| `revoked` | Should not be used (bad citation, policy issue) |
| `deleted` | Hard delete — rare; prefer `revoked` |

`delivery.delivery_status` (when push opts into delivery):

| Value | Meaning |
|---|---|
| `pending` | Created, not yet delivered |
| `delivered` | Confirmed |
| `failed` | Final |
| `skipped` | No delivery target / not requested |

### Lifecycle rules

- If `expires_at` is set and `now > expires_at` → treat as unavailable
  for pull (or return with `status=expired` if you add that variant).
- Prefer `revoked` over hard delete.

## 2.2 `POST /api/fleet/artifacts/push`

**Auth:** fleet-signed required; capability `artifacts.can_push=true`
**Content-Type:** `application/json`
**Idempotency:** `Idempotency-Key` header (recommended) OR
`artifact.created_by.request_id`.

### Required headers

Fleet auth headers from Move 1 + optional:
- `X-Request-Id`
- `Idempotency-Key`

### Request JSON

```json
{
  "artifact": {
    "artifact_id": "<optional-uuid>",
    "version": "<optional-int>",

    "type": "contract_draft",
    "title": "Mutual NDA Draft",
    "summary": "First-pass draft ...",

    "format": "markdown",
    "mime_type": "text/markdown",

    "payload": "# NDA...\n...",
    "payload_blob_url": null,
    "payload_sha256": "<optional-hex>",
    "size_bytes": 18234,

    "citations": [ /* see Citation shape */ ],

    "workspace": { "workspace_id": "<uuid-or-null>" },

    "created_by": {
      "request_id": "<uuid>",
      "user": {
        "global_user_id": "<optional>",
        "app_user_id": "<optional>"
      }
    },

    "provenance": {
      "created_by_agent": "<optional>",
      "deliberation": { "...": "..." },
      "source": {
        "deliverable_id": "<uuid-or-null>",
        "initiative_id": "<uuid-or-null>"
      }
    },

    "visibility": {
      "scope": "service",
      "allowed_app_slugs": ["contract-concierge"],
      "data_sensitivity": "confidential"
    },

    "delivery": {
      "target_app_slug": "<optional>",
      "deliver": false
    },

    "lifecycle": {
      "retention_days": 90
    }
  },

  "options": {
    "on_version_conflict": "reject|supersede|create_new_version",
    "require_citations": false
  }
}
```

### Server-side normalization

- `created_by.app_slug` set from fleet identity (ignore if provided).
- If `payload_sha256` missing → compute from payload bytes or blob.
- Enforce `max_payload_kb` from service capabilities.
- Validate `artifact.type` against allowlist (global or per-service).
- If `delivery.deliver=true`, enqueue delivery (Phase 1 may stub).

### Version assignment

- `artifact_id` omitted → new `artifact_id`, `version=1`.
- `artifact_id` present, `version` omitted → `version = latest + 1` (atomic).
- Both present → explicit-create-of-that-version; enforce conflict policy.

### Response 201 Created

```json
{
  "artifact": {
    "artifact_id": "<uuid>",
    "version": 1,
    "status": "ready",

    "type": "contract_draft",
    "title": "Mutual NDA Draft",
    "summary": "First-pass draft ...",

    "format": "markdown",
    "mime_type": "text/markdown",
    "size_bytes": 18234,
    "payload_sha256": "<hex>",

    "payload_included": false,
    "payload_blob_url": null,
    "preview": "# Mutual NDA\n\nThis Agreement ...\n",

    "created_at": "<iso>",

    "created_by": {
      "app_slug": "contract-concierge",
      "service_key_id": "fs_contractconcierge_k1",
      "request_id": "<uuid>",
      "user": {
        "global_user_id": null,
        "app_user_id": "u_123"
      }
    },

    "workspace": { "workspace_id": "<uuid>" },

    "provenance": {
      "created_by_agent": "LegalDocDrafterAgent",
      "deliberation": { "...": "..." },
      "source": { "...": "..." }
    },

    "routing_trace": {
      "mode": "force",
      "requested_agent": "legal_doc_drafter_agent",
      "resolved_agent": "legal_doc_drafter_agent",
      "routed_to": "LegalDocDrafterAgent",
      "was_overridden": false,
      "override_reason": null
    },

    "citations_count": 2,

    "visibility": {
      "scope": "service",
      "allowed_app_slugs": ["contract-concierge"],
      "data_sensitivity": "confidential"
    },

    "lifecycle": {
      "retention_days": 90,
      "expires_at": "<iso>",
      "revoked_at": null,
      "revoked_reason": null,
      "supersedes": null,
      "superseded_by": null
    }
  },

  "delivery": {
    "queued": false,
    "delivery_status": "skipped",
    "target_app_slug": null,
    "error": null
  }
}
```

Notes:
- `payload_included=false` lets you omit large payloads from the
  response. Always return a `preview` (first N chars) for UX/debug.
- If you store payload in-row and want to include it: set
  `payload_included=true` + include `payload`. **Recommend not doing
  that by default.**

### Response 409 Version conflict

```json
{
  "error": {
    "code": "version_conflict",
    "message": "artifact_id/version already exists",
    "artifact_id": "<uuid>",
    "version": 2,
    "existing_payload_sha256": "<hex>",
    "request_id": "<uuid>"
  }
}
```

## 2.3 `GET /api/fleet/artifacts` (pull)

**Auth:** fleet-signed required; capability `artifacts.can_pull=true`
**Signing:** PATH in signature base **must include querystring** (sorted
keys) to prevent query tampering.

### Query params

Pagination (cursor-based, preferred over offset):

| Param | Type | Notes |
|---|---|---|
| `limit` | int | default 20, max 100 |
| `cursor` | opaque string | from previous response's `paging.next_cursor` |

Incremental sync:

| Param | Type | Notes |
|---|---|---|
| `since` | ISO-8601 | return artifacts with `created_at >= since` OR `updated_at >= since` |

Filters:

| Param | Type | Notes |
|---|---|---|
| `type` | string, repeated | e.g. `type=contract_draft&type=pitch_outline` |
| `status` | enum | `ready` \| `superseded` \| `revoked` (default: `ready`) |
| `artifact_id` | uuid | single artifact |
| `workspace_id` | uuid | single workspace |
| `include_payload` | bool | default `false` |
| `min_version`, `max_version` | int | optional |
| `created_by_request_id` | uuid | debug filter |
| `include_expired` | bool | default `false`; requires capability flag |

### Scope rule (CRITICAL)

- Caller's `app_slug` is derived from signature identity.
- Server returns only artifacts where:
  - `visibility.scope == "service"` AND `allowed_app_slugs` contains
    caller's `app_slug`, **OR**
  - broader scopes once policy ships (don't implement cross-app reads
    yet — see "Cross-app constraint" below).

### Response 200

```json
{
  "artifacts": [
    {
      "artifact_id": "<uuid>",
      "version": 2,
      "status": "ready",
      "type": "contract_draft",
      "title": "Mutual NDA Draft (v2)",
      "summary": "Updated term ...",
      "format": "markdown",
      "mime_type": "text/markdown",
      "size_bytes": 19440,
      "payload_sha256": "<hex>",

      "payload_included": false,
      "payload_blob_url": null,
      "preview": "# Mutual NDA\n\nThis Agreement ...\n",

      "created_at": "<iso>",
      "created_by": { "app_slug": "contract-concierge", "request_id": "<uuid>" },
      "workspace": { "workspace_id": "<uuid-or-null>" },
      "provenance": { "created_by_agent": "LegalDocDrafterAgent" },
      "routing_trace": { "mode": "force", "routed_to": "LegalDocDrafterAgent" },
      "citations_count": 2,
      "visibility": {
        "scope": "service",
        "allowed_app_slugs": ["contract-concierge"],
        "data_sensitivity": "confidential"
      },
      "lifecycle": {
        "retention_days": 90,
        "expires_at": "<iso>",
        "revoked_at": null,
        "revoked_reason": null
      }
    }
  ],
  "paging": {
    "limit": 20,
    "next_cursor": "<opaque-or-null>",
    "has_more": false
  },
  "totals": {
    "returned": 1,
    "approx_remaining": 0
  },
  "server_time": "<iso>"
}
```

Notes:
- `totals.approx_remaining` is optional — omit if it can't be computed
  cheaply.
- Cursor should encode a stable sort key like
  `(created_at, artifact_id, version)` so paging is deterministic.

## 2.4 Workspace + Deliverable wiring

**Decision: inherit existing u-d-b `ProjectWorkspace` and `Deliverable`
systems. No parallel workspace model.**

Rules:

1. Artifacts can reference a workspace via
   `workspace.workspace_id` (optional on every version).
2. Artifacts may reference a deliverable when u-d-b generated the
   content:
   - `provenance.source.deliverable_id` set
   - deliverable remains canonical for internal editing / review /
     publishing
   - the artifact is the "exchange wrapper" for fleet transport
3. When a fleet app pushes an artifact:
   - store as `FleetArtifact` in u-d-b
   - **do not** require a deliverable mirror
   - optional flag for later: `ARTIFACTS_MIRROR_TO_DELIVERABLES=true`
     if you want everything searchable in deliverables

Why this is right:
- Preserves the existing initiative pipeline + work tooling.
- Avoids duplicating "workspace" concepts across the fleet.
- Lets artifacts be a transport layer, not a second content system.

## 2.5 Edge cases (canonical behaviors)

### A. Versioning conflicts (`options.on_version_conflict`)

Conflict = request tries to create `(artifact_id, version)` that exists.

**1. `reject` (default)**
- Return `409 version_conflict`.
- Include existing `payload_sha256` for debug.
- No mutation.
- Use when caller treats version as authoritative.

**2. `create_new_version` (recommended for most apps)**
- Ignore provided `version` if it collides.
- Allocate `version = latest_version + 1` atomically.
- Set lifecycle links:
  - `lifecycle.supersedes = {artifact_id, version: latest}`
  - Update prior latest's `lifecycle.superseded_by` to new version.
- Return `201` with new version.
- Use when u-d-b is the canonical version allocator.

**3. `supersede` (discouraged)**
- Audit-hostile. If implemented:
  - mark existing `status = superseded` (NOT `revoked`)
  - create a new version anyway
- Net: identical to `create_new_version` plus a "supersede attempted"
  audit note.
- **Recommendation:** don't expose externally; treat internally as
  alias of `create_new_version`.

**Atomicity requirements**
- Version allocation must be transactional. Options:
  - `SELECT ... FOR UPDATE` on rows for `artifact_id`
  - Separate `FleetArtifactHead` table tracking `latest_version`,
    updated atomically
- Cursor pagination must remain stable while new versions arrive
  (cursor encodes last-seen tuple).

### B. Citation mutability — immutability rule

- Citations are **immutable per version**.
- To change citations → push a new version.
- If a version is later found problematic:
  - set `status = revoked`
  - set `lifecycle.revoked_at` + `lifecycle.revoked_reason`
- Pull behavior:
  - default: do not return `revoked` artifacts unless caller
    explicitly requested `status=revoked`
  - if returned, include `revoked_reason`

### C. Agent attribution (deliberation / multi-step)

When the artifact is produced by multiple agents:
- `provenance.created_by_agent` should be the **final synthesizer**
  (whose output is the artifact payload).
- Also include:
  - `provenance.deliberation.panel` list
  - `provenance.deliberation.agent_execution_ids` list (if available)
  - `provenance.deliberation.winner` (optional alias of `created_by_agent`)

If there's truly no single synthesizer (rare; collection artifact):
- `provenance.created_by_agent = "WorkflowOrchestrator"` (or your
  actual orchestration class name)
- include `provenance.deliberation.components = [{artifact_id, version, agent}]`

This keeps attribution consistent without lying.

### D. Retention policy enforcement

Inputs:
- artifact `lifecycle.retention_days` (bounded)
- service capability `artifacts.max_retention_days` (recommended cap)

Rules:

1. **On push:**
   - clamp `retention_days` to
     `[min_retention_days, max_retention_days]`
   - set `expires_at = created_at + retention_days`
2. **On pull:**
   - default: exclude expired (`now > expires_at`)
   - allow `include_expired=true` only for admin / service with
     explicit capability
3. **Storage cleanup:**
   - scheduled task deletes or nulls **payload** (`payload` and
     `payload_blob_url`) after expiry
   - keep minimal metadata rows for audit/search (`artifact_id`,
     `version`, `type`, hashes, provenance, timestamps,
     revoked/expired markers)
   - if you need hard-delete for compliance, gate it behind an
     admin-only policy flag and log `action=hard_delete` with reason

## 2.6 Cross-app constraint (HARD RULE for Phase 1)

**No cross-app reads/writes yet.**

- `allowed_app_slugs` must contain **only the caller's `app_slug`**
  until app-to-app delivery is intentionally shipped.
- The server must ignore any client-supplied `target_app_slug` unless
  the calling service has a dedicated `artifacts.can_cross_app=true`
  capability.

This protects against accidental data leakage during the early days
of Move 2 — apps will inevitably try to push artifacts marked visible
to other apps before the delivery / consumption story is fully
designed.

---

# Implementation order (recommended)

For Session 1129:

1. **Move 1 models + middleware** — `FleetServiceIdentity`,
   `FleetServiceKey`, signature verification middleware,
   `FleetAuthAuditLog`. Wire into `/api/pa/chat/` enforcement (ignore
   routing block unless signed).
2. **Bootstrap script + provisioning admin endpoint** — make it
   possible to actually issue a service identity for
   contract-concierge so e2e smoke can run.
3. **Update one fleet repo** (contract-concierge) to send signed
   requests. Verify routing block is now honored only with signature.
4. **Rotation lifecycle endpoints + Admin audit logging** — finish
   Move 1 before starting Move 2.

For Session 1130 (or later):

5. **Move 2 model + push endpoint** — `FleetArtifact`,
   `POST /api/fleet/artifacts/push`, idempotency, version
   allocation.
6. **Move 2 pull endpoint** — `GET /api/fleet/artifacts` with
   cursor pagination, scope rule.
7. **Workspace wiring** — artifact ↔ deliverable references; flag
   for opt-in mirror.
8. **Back-prop signed-request client** to the other 6 fleet repos
   (same pattern as Phase 2B brain_client back-prop).

---

# Open questions to confirm with Rigby before coding

- **Slow-hash for secrets**: SHA256 vs pbkdf2/bcrypt for
  `secret_hash`. Spec recommends SHA256 for random 32B secrets but
  flag if you want the slow-hash variant.
- **Querystring policy enforcement**: spec says GET querystring is
  signed, POST is not. Confirm the canonical sort order for query
  keys (alphabetical, presumably).
- **`Idempotency-Key` semantics**: TTL for idempotency replay
  detection? (Implied 24h but not stated.)
- **Bootstrap return secret on plan vs separate reveal**: spec uses
  return-on-plan; confirm she wants that vs separate
  `POST /reveal` step.
- **Payload storage**: in-row JSON column vs S3-equivalent blob with
  `payload_blob_url`. Likely in-row for Phase 1, blob later when
  payloads grow.
