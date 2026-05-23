"""Fleet service identity + signed-request audit (Move 1).

Implements the data layer of `docs/specs/FLEET_MOVE_1_AND_2_SPEC.md`:

- `FleetServiceIdentity` — one row per fleet app (contract-concierge,
  mentorforge, etc). Carries capabilities + allowed_routes.
- `FleetServiceKey` — one or more keys per identity. Secrets stored as
  SHA256 hashes; raw secrets only exist at provision/rotate-plan time.
- `FleetServiceRotation` — explicit lifecycle for key rotation
  (planned → active → completed | aborted).
- `FleetAuthAuditLog` — every fleet-headers / fleet-only-route /
  routing-block request gets an audit row (allow + deny).

Designed in conversation pa-d19c1674b936 with Rigby. Locked decisions:

- Secrets are 32-byte random; SHA256(secret) is the storage hash (no
  bcrypt/pbkdf2 — the threat model is DB exfiltration of high-entropy
  secrets, not user-chosen password cracking).
- Raw secret is returned exactly once at provisioning / rotation-plan
  time. No reveal endpoint.
- Audit log persists every deny + every allow when
  `FLEET_AUTH_LOG_ALL=true`; deny rows also emit WARN through the
  standard logger.
"""
from __future__ import annotations

import hashlib
import secrets as secrets_module
from typing import Optional

from django.db import models

from .base.models import UnifiedBaseModel


# Hash + secret helpers
# ──────────────────────────────────────────────────────────────────────


SECRET_BYTES = 32  # 256 bits of entropy


def generate_service_secret() -> str:
    """Generate a fresh 32-byte URL-safe secret (returned only once)."""
    return secrets_module.token_urlsafe(SECRET_BYTES)


def hash_service_secret(secret: str) -> str:
    """Storage hash for a service secret.

    SHA256 only — secrets are high-entropy random, not user-chosen, so
    rainbow / dictionary attacks aren't the threat model. A server-side
    pepper can be layered on later if we want belt+suspenders, but the
    spec explicitly approved SHA256-only for the initial cut.
    """
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


# Models
# ──────────────────────────────────────────────────────────────────────


class FleetServiceIdentity(UnifiedBaseModel):
    """One row per fleet app authorized to talk to u-d-b's signed APIs.

    `app_slug` matches the keys in `config/fleet_agent_routing.json`
    (contract-concierge, mentorforge, etc). Capabilities is the JSON
    block defined in spec section 1.2 — controls which routes the
    service can hit and what it can ask for (force routing, artifact
    push, etc).
    """

    STATUS_ACTIVE = "active"
    STATUS_DISABLED = "disabled"
    STATUS_ROTATING = "rotating"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_DISABLED, "Disabled"),
        (STATUS_ROTATING, "Rotating"),
    ]

    app_slug = models.CharField(
        max_length=100,
        unique=True,
        help_text="Fleet app identifier; matches fleet_agent_routing.json keys",
    )
    name = models.CharField(max_length=200, help_text="Human-readable label")
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    capabilities = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-spec capability dict (routing/artifacts/events)",
    )
    allowed_routes = models.JSONField(
        default=list,
        blank=True,
        help_text="Explicit route allowlist; empty list = no fleet routes allowed",
    )
    last_used_at = models.DateTimeField(
        null=True, blank=True, help_text="Updated on any successful verify"
    )

    class Meta:
        verbose_name = "Fleet Service Identity"
        verbose_name_plural = "Fleet Service Identities"
        ordering = ["app_slug"]

    def __str__(self) -> str:
        return f"{self.app_slug} ({self.status})"

    def capability(self, *path: str, default=None):
        """Lookup nested capability key (e.g. ``capability('artifacts', 'can_push')``)."""
        node = self.capabilities or {}
        for part in path:
            if not isinstance(node, dict):
                return default
            node = node.get(part)
            if node is None:
                return default
        return node

    def is_route_allowed(self, path: str) -> bool:
        """True when this identity is allowed to hit the given URL path."""
        allowlist = self.allowed_routes or []
        return path in allowlist


class FleetServiceKey(UnifiedBaseModel):
    """A single HMAC-signing key bound to a FleetServiceIdentity.

    Identities can hold multiple keys during rotation. Each request
    arrives with `X-Fleet-Key-Id`; verification looks up THIS row, not
    the parent identity directly.
    """

    STATUS_ACTIVE = "active"
    STATUS_DRAINING = "draining"
    STATUS_DISABLED = "disabled"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_DRAINING, "Draining"),
        (STATUS_DISABLED, "Disabled"),
    ]

    service = models.ForeignKey(
        FleetServiceIdentity,
        on_delete=models.CASCADE,
        related_name="keys",
    )
    key_id = models.CharField(
        max_length=120,
        unique=True,
        help_text="Public key identifier (e.g. fs_contractconcierge_k1)",
    )
    secret_hash = models.CharField(
        max_length=64,
        help_text="SHA256(secret); raw secret never persisted",
    )
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    not_before = models.DateTimeField(null=True, blank=True)
    not_after = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Fleet Service Key"
        verbose_name_plural = "Fleet Service Keys"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["service", "status"]),
        ]
        ordering = ["service__app_slug", "-created_at"]

    def __str__(self) -> str:
        return f"{self.key_id} [{self.status}]"

    def matches_secret(self, candidate: str) -> bool:
        """Constant-time compare of SHA256(candidate) against stored hash."""
        return secrets_module.compare_digest(
            hash_service_secret(candidate), self.secret_hash
        )

    def is_currently_usable(self, *, now=None) -> bool:
        """Active or draining keys with validity window satisfied are usable."""
        from django.utils import timezone

        if self.status not in (self.STATUS_ACTIVE, self.STATUS_DRAINING):
            return False
        moment = now or timezone.now()
        if self.not_before and moment < self.not_before:
            return False
        if self.not_after and moment > self.not_after:
            return False
        return True


class FleetServiceRotation(UnifiedBaseModel):
    """Tracks one key-rotation operation for a service identity.

    State machine: planned → active → completed | aborted.
    """

    STATUS_PLANNED = "planned"
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_ABORTED = "aborted"

    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_ABORTED, "Aborted"),
    ]

    service = models.ForeignKey(
        FleetServiceIdentity,
        on_delete=models.CASCADE,
        related_name="rotations",
    )
    old_key = models.ForeignKey(
        FleetServiceKey,
        on_delete=models.PROTECT,
        related_name="rotations_as_old",
    )
    new_key = models.ForeignKey(
        FleetServiceKey,
        on_delete=models.PROTECT,
        related_name="rotations_as_new",
    )
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PLANNED
    )
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Fleet Service Rotation"
        verbose_name_plural = "Fleet Service Rotations"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["service", "status"])]

    def __str__(self) -> str:
        return f"{self.service.app_slug}: {self.old_key.key_id} → {self.new_key.key_id} ({self.status})"


class FleetAuthAuditLog(UnifiedBaseModel):
    """One row per fleet-touching request (allow or deny).

    Persisted alongside standard-logger emission so we have a durable
    audit trail independent of log rotation. See spec section 1.5 for
    the per-failure-mode `notes` shape.
    """

    RESULT_ALLOW = "allow"
    RESULT_DENY = "deny"

    RESULT_CHOICES = [
        (RESULT_ALLOW, "Allow"),
        (RESULT_DENY, "Deny"),
    ]

    occurred_at = models.DateTimeField(
        auto_now_add=True, db_index=True
    )
    request_id = models.CharField(
        max_length=64, blank=True, default="", db_index=True
    )

    method = models.CharField(max_length=10)
    path = models.CharField(max_length=512)
    query = models.CharField(max_length=2048, blank=True, default="")
    status_code = models.PositiveSmallIntegerField()
    result = models.CharField(max_length=8, choices=RESULT_CHOICES)
    deny_code = models.CharField(
        max_length=64, blank=True, default="", db_index=True,
        help_text="One of the canonical error codes; empty on allow",
    )

    key_id = models.CharField(max_length=120, blank=True, default="", db_index=True)
    app_slug_claimed = models.CharField(
        max_length=100, blank=True, default="", db_index=True
    )
    app_slug_resolved = models.CharField(
        max_length=100, blank=True, default="", db_index=True
    )

    timestamp_claimed = models.BigIntegerField(null=True, blank=True)
    timestamp_delta_seconds = models.IntegerField(null=True, blank=True)
    nonce = models.CharField(max_length=64, blank=True, default="")
    replay_detected = models.BooleanField(default=False)

    body_sha256 = models.CharField(max_length=64, blank=True, default="")
    sig_present = models.BooleanField(default=False)

    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")
    latency_ms = models.PositiveIntegerField(default=0)

    notes = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Fleet Auth Audit Log"
        verbose_name_plural = "Fleet Auth Audit Logs"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["-occurred_at"]),
            models.Index(fields=["result", "deny_code"]),
            models.Index(fields=["app_slug_resolved", "-occurred_at"]),
        ]

    def __str__(self) -> str:
        suffix = f" code={self.deny_code}" if self.deny_code else ""
        return (
            f"{self.occurred_at:%Y-%m-%d %H:%M:%S} "
            f"{self.method} {self.path} → {self.status_code} ({self.result}){suffix}"
        )


class FleetArtifact(UnifiedBaseModel):
    """A work product pushed by a fleet service for later retrieval.

    Move 2 Round 1 (MLC, Session 1129). Minimal scope per Rigby's
    minimum-lovable-contract: no versioning, no provenance/citations
    panel, no cross-app visibility — just enough to prove the
    push-then-pull round-trip works under fleet auth.

    Future rounds add (per `docs/specs/FLEET_MOVE_1_AND_2_SPEC.md`
    section 2):
    - artifact_id + version with `(artifact_id, version)` unique
    - provenance.deliberation (panel, citations, agent_execution_ids)
    - lifecycle (retention_days, expires_at, supersedes/superseded_by)
    - visibility scope (cross-app allowlists)
    - blob storage offload for large payloads

    For Round 1: flat row keyed by UUID, payload stored in-row as
    JSONField, sha256 computed from the canonicalized JSON form.

    Ownership rule: only the **creating identity's app_slug** can
    retrieve. We compare app_slug (not service_identity_id) so
    rotating a key doesn't lock the owner out of their own
    artifacts.
    """

    artifact_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Caller-chosen type tag (e.g. 'contract_draft', 'lead_list')",
    )
    payload = models.JSONField(
        help_text="The artifact's contents — caller-controlled JSON",
    )
    caller_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional caller-supplied tags. Separate from `metadata` "
                  "which is system-flexible storage on UnifiedBaseModel.",
    )
    sha256 = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Hex SHA-256 of canonical JSON payload. Computed server-side; "
                  "clients can verify after a pull.",
    )
    size_bytes = models.PositiveIntegerField(
        default=0,
        help_text="Bytes of canonical JSON payload — used for "
                  "max_payload_kb capability gating.",
    )
    created_by_identity = models.ForeignKey(
        FleetServiceIdentity,
        on_delete=models.PROTECT,
        related_name="artifacts",
        help_text="The fleet service that pushed this artifact",
    )
    created_by_key_id = models.CharField(
        max_length=120,
        help_text="The specific signing key used at create time (may "
                  "differ from the identity's current active key after "
                  "a rotation)",
    )
    request_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        help_text="X-Request-Id from the signing headers; joins to "
                  "FleetAuthAuditLog for full trace.",
    )

    # Session 1129 Move 2 Round 2 — TTL + soft-delete.
    # See docs/specs/FLEET_MOVE_2_ROUND_2_SPEC.md section 2.
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Server-set at create time: created_at + DEFAULT_TTL_DAYS. "
                  "Past expires_at + deleted_at IS NULL = candidate for cleanup.",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Soft-delete marker. Set by cleanup job on expiry OR "
                  "by manual operator action. Hard delete is Round 3+.",
    )
    delete_reason = models.CharField(
        max_length=32,
        blank=True,
        default="",
        help_text="Why this artifact was soft-deleted. Values: 'expired' "
                  "(cleanup), 'manual', 'admin', '' (not deleted).",
    )

    class Meta:
        verbose_name = "Fleet Artifact"
        verbose_name_plural = "Fleet Artifacts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by_identity", "-created_at"]),
            models.Index(fields=["artifact_type", "-created_at"]),
            # Round 2 — supports the list endpoint's stable ordering
            # with the (-created_at, -id) tiebreaker.
            models.Index(
                fields=["created_by_identity", "-created_at", "-id"],
                name="core_fleeta_list_stable_idx",
            ),
            # Round 2 — supports the cleanup job's selection scan
            # (`expires_at <= now AND deleted_at IS NULL`).
            models.Index(
                fields=["expires_at", "deleted_at"],
                name="core_fleeta_cleanup_scan_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.artifact_type} ({self.created_by_identity.app_slug}) — {self.id}"

    @property
    def is_expired(self) -> bool:
        """True when this artifact has crossed its TTL boundary.

        Independent of soft-delete state — an artifact can be expired
        but not yet deleted (cleanup hasn't run), or deleted but not
        expired (manual delete). Both states return 404 to clients.
        """
        if self.expires_at is None:
            return False
        from django.utils import timezone
        return timezone.now() >= self.expires_at

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class FleetEvent(UnifiedBaseModel):
    """Lifecycle event emitted by u-d-b for downstream fleet consumers.

    Move 3 Round 1 (MLC, Session 1129). Persistence + Redis pub/sub fan-out.
    Persisted rows give us audit + replay (when we add Last-Event-ID
    later); Redis gives low-latency delivery to subscribers.

    Schema is deliberately generic — `event_type` + `payload` JSON — so
    new event types don't require migrations.

    Move 3 MLC emits:
    - `artifact.created` — after FleetArtifact row commit on push
    - `artifact.expired` — after cleanup task soft-deletes a row

    Future rounds will add: `agent.run.completed`, `agent.run.started`,
    `routing.dispatch`, etc. Don't add them in MLC.

    Filtering: events are app-scoped via `app_slug`. CC (or any
    subscriber) sees only its own app's events at the u-d-b layer.
    Per-user filtering happens at the consuming app side (CC matches
    `payload.generated_by_user_id` to the browser session).

    Move 3 Round 2 (Session 1130) — added monotonic `seq` column backed
    by a Postgres sequence. Per Rigby's lock (conversation
    pa-d19c1674b936): `seq` is the canonical ordering cursor for
    replay. UUID `id` is preserved for FK joins; `seq` is what clients
    pass back as `?since=<seq>` to resume.
    """

    seq = models.BigIntegerField(
        unique=True,
        editable=False,
        db_default=models.expressions.RawSQL(
            "nextval('core_fleetevent_seq')", []
        ),
        help_text=(
            "Monotonic event sequence number assigned by Postgres at INSERT "
            "via the `core_fleetevent_seq` sequence. Canonical ordering "
            "cursor for SSE replay (`?since=<seq>` is exclusive). Django 5 "
            "`db_default` omits this column from INSERTs so the sequence "
            "fires server-side."
        ),
    )
    event_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Dotted event name (e.g. 'artifact.created', 'artifact.expired')",
    )
    app_slug = models.CharField(
        max_length=100,
        db_index=True,
        help_text="The fleet app this event belongs to (matches FleetServiceIdentity.app_slug)",
    )
    payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Event body — caller-defined per event_type. Should include "
                  "enough context for subscribers to act without a separate fetch.",
    )
    source_artifact = models.ForeignKey(
        "FleetArtifact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        help_text="Optional FK to the source artifact (for lifecycle events).",
    )

    class Meta:
        verbose_name = "Fleet Event"
        verbose_name_plural = "Fleet Events"
        ordering = ["seq"]
        indexes = [
            # Subscribers stream filtered by app_slug; this composite
            # supports the replay-by-seq path scoped to one app.
            models.Index(
                fields=["app_slug", "seq"],
                name="core_fleete_app_seq_idx",
            ),
            # Legacy index from Round 1 — kept for any callers still
            # ordering by created_at; ordering=["seq"] now though.
            models.Index(
                fields=["app_slug", "-created_at"],
                name="core_fleete_app_recent_idx",
            ),
            models.Index(
                fields=["event_type", "-created_at"],
                name="core_fleete_type_recent_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.app_slug}) @ {self.created_at:%H:%M:%S}"


def compute_payload_sha256(payload) -> tuple[str, int]:
    """Compute canonical SHA-256 + byte size of a JSON-serializable payload.

    Uses `sort_keys=True` + tight separators so the same logical
    payload always hashes identically regardless of insertion order
    or formatting. Returns ``(hex_digest, byte_size)``.
    """
    import json as _json
    canonical = _json.dumps(payload, sort_keys=True, separators=(",", ":"))
    canonical_bytes = canonical.encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest(), len(canonical_bytes)


__all__ = [
    "FleetServiceIdentity",
    "FleetServiceKey",
    "FleetServiceRotation",
    "FleetAuthAuditLog",
    "FleetArtifact",
    "FleetEvent",
    "generate_service_secret",
    "hash_service_secret",
    "compute_payload_sha256",
    "SECRET_BYTES",
]
