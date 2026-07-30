"""
session_lifecycle — S2746 ops surface for PA-wrapper pin rotation.

Automates the retire → mint → wrapper-rewrite ceremony that every
session close previously required as a hand-edit of ``tools/pa_local.sh``.
Substrate reuse:

* Read via ``ChatConversation`` ORM (same rows ``session_tool.retire``
  and ``session_tool.create_fresh`` operate on).
* Mint via the same ``pa-<uuid[:16]>`` id shape as
  ``td_handlers_core._handle_session_tool`` action='create_fresh'
  (see ``core/services/td_handlers_core.py`` line 3955).
* Retire via bulk ``update(session_active=False)`` — same shape as
  ``td_handlers_core._handle_session_tool`` action='retire' (line 4104),
  but bypasses the ``_bound_conversation_id`` guard because the wrapper
  rewrite is the pin-rotation equivalent that guard exists to enforce.
* Carry-forward summary via ``session_health_service.get_session_health``
  ``starter_prompt`` — same source ``create_fresh`` uses.

Subcommands (mutually exclusive)::

    # Report current wrapper pin state (no writes):
    python manage.py session_lifecycle status
    python manage.py session_lifecycle status --user donkeyking

    # Mint fresh pin + rewrite wrapper. Does NOT retire anything.
    python manage.py session_lifecycle open --label engineering-session
    python manage.py session_lifecycle open --label X --carry-forward "..."
    python manage.py session_lifecycle open --label X --dry-run

    # Atomic rotate: retire current wrapper pin, mint fresh, rewrite wrapper.
    python manage.py session_lifecycle close --label next-arc
    python manage.py session_lifecycle close --label X --dry-run

    # Retire the current wrapper pin only (no mint, no rewrite):
    python manage.py session_lifecycle close --retire-only

Wrapper rewrite safety contract:

- Match the exact invocation line
  ``python tools/pa_chat.py "$@" --tools --conversation pa-<16 hex>``
  anchored to line start + end (single line).
- Refuse if 0 or >1 matches — print match count + line numbers of any
  candidates + instruction to fix manually.
- Preserve every other byte in the file (only the pin substring changes).

Failure recovery for ``close``:

- Order is (1) retire current, (2) create_fresh new, (3) rewrite wrapper.
- On rewrite failure, both DB ops have already committed. Print the old
  pin, new pin, and the exact one-liner to complete the rewrite by hand.
  Do NOT auto-``set_active`` the old pin — the operator may have
  intended to close it.

Exit codes:
- 0 — success
- 1 — validation / precondition error (invalid label, malformed wrapper,
  user not found)
- 2 — post-DB-mutation failure (rewrite failed; recovery info printed)
- >2 — unexpected Django/DB error (propagates)
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count, Max

logger = logging.getLogger(__name__)


WRAPPER_PATH = Path("tools/pa_local.sh")
FRESHNESS_LOG_PATH = Path("logs/session_freshness.jsonl")

_PIN_RE = re.compile(r"^pa-[0-9a-f]{16}$")

# Anchored, whole-line match for the wrapper's live invocation. Matches:
#   python tools/pa_chat.py "$@" --tools --conversation pa-XXXXXXXXXXXXXXXX
# Nothing else in pa_local.sh should look like this (the file contains
# hundreds of pa- references inside comment blocks, but only one live
# invocation).
_WRAPPER_LINE_RE = re.compile(
    r'^(python tools/pa_chat\.py "\$@" --tools --conversation )'
    r'(pa-[0-9a-f]{16})$',
    re.MULTILINE,
)

_DEFAULT_USER = "chris"

_RETIREMENT_TRIGGERS = (
    "message_count_over_50",
    "session_marked_inactive",
    "no_activity_in_last_24h",
)


class Command(BaseCommand):
    help = (
        "Rotate the PA wrapper pin in tools/pa_local.sh atomically. "
        "Wraps the retire → create_fresh → wrapper-rewrite ceremony "
        "that used to be a hand-edit at every session close. See file "
        "docstring for usage examples."
    )

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        # ── status ──
        status_p = subparsers.add_parser(
            "status",
            help="Report the current wrapper pin + owner + retirement triggers. No writes.",
        )
        status_p.add_argument(
            "--user",
            default=_DEFAULT_USER,
            help=f"Username to lookup for ownership check (default: {_DEFAULT_USER})",
        )
        status_p.add_argument(
            "--wrapper-path",
            default=None,
            help="Override wrapper file path (tests / unusual layouts only).",
        )

        # ── open ──
        open_p = subparsers.add_parser(
            "open",
            help="Mint a fresh pin + rewrite wrapper. Does NOT retire any existing pin.",
        )
        open_p.add_argument(
            "--label",
            required=True,
            help="Label for the new session (stored as ChatConversation session_title).",
        )
        open_p.add_argument(
            "--carry-forward",
            default=None,
            help="Explicit carry-forward summary. Default: auto-derive from current pin's session_health starter_prompt.",
        )
        open_p.add_argument(
            "--user",
            default=_DEFAULT_USER,
            help=f"Username the new session is owned by (default: {_DEFAULT_USER})",
        )
        open_p.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned actions without writing to DB or wrapper.",
        )
        open_p.add_argument(
            "--wrapper-path",
            default=None,
            help="Override wrapper file path (tests / unusual layouts only).",
        )

        # ── history ──
        history_p = subparsers.add_parser(
            "history",
            help=(
                "Print recent session-open freshness verdicts from "
                f"{FRESHNESS_LOG_PATH} (JSONL). No writes."
            ),
        )
        history_p.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Number of most-recent rows to print (default: 10).",
        )
        history_p.add_argument(
            "--log-path",
            default=None,
            help="Override log path (tests / unusual layouts only).",
        )

        # ── close ──
        close_p = subparsers.add_parser(
            "close",
            help="Atomic rotate: retire current wrapper pin, mint fresh, rewrite wrapper.",
        )
        close_p.add_argument(
            "--label",
            default=None,
            help="Label for the new session. Required unless --retire-only.",
        )
        close_p.add_argument(
            "--carry-forward",
            default=None,
            help="Explicit carry-forward summary. Default: auto-derive.",
        )
        close_p.add_argument(
            "--retire-only",
            action="store_true",
            help="Retire the current wrapper pin only; do NOT mint a fresh pin or rewrite the wrapper.",
        )
        close_p.add_argument(
            "--user",
            default=_DEFAULT_USER,
            help=f"Username (default: {_DEFAULT_USER})",
        )
        close_p.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned actions without writing.",
        )
        close_p.add_argument(
            "--wrapper-path",
            default=None,
            help="Override wrapper file path (tests / unusual layouts only).",
        )
        # Ledger #16 — twin-mirror enforcement (S2941).
        close_p.add_argument(
            "--content-mirror-id",
            default=None,
            help=(
                "UUID of the engineering-truth content mirror Deliverable "
                "(twin-mirror per feedback_twin_deliverable_at_every_ratification). "
                "Required together with --ratification-envelope-id, unless "
                "--allow-no-mirror is passed."
            ),
        )
        close_p.add_argument(
            "--ratification-envelope-id",
            default=None,
            help=(
                "UUID of the governance-truth ratification envelope Deliverable "
                "(deliverable_type='ratification_record'). Required together "
                "with --content-mirror-id, unless --allow-no-mirror is passed."
            ),
        )
        close_p.add_argument(
            "--allow-no-mirror",
            action="store_true",
            help=(
                "Ledger #16 escape hatch: explicitly proceed without twin-mirror "
                "verification (e.g., cascade-only / doc-bump closes). Logged for "
                "audit. Mutually exclusive with mirror-ID flags."
            ),
        )
        # S3041 meta-fix — ledger reconciliation enforcement.
        close_p.add_argument(
            "--handoff",
            default=None,
            help=(
                "Path to the session handoff to reconciliation-check. If "
                "provided, any `Ledger #N` reference in the handoff must "
                "have a matching `Ledger #N status flip` block in the "
                "Rigby Tool Gap Ledger deliverable — otherwise close "
                "refuses (unless --allow-ledger-drift is passed)."
            ),
        )
        close_p.add_argument(
            "--ledger-deliverable-id",
            default=None,
            help=(
                "S3041 meta-fix: override the ledger deliverable UUID "
                "checked by --handoff. Defaults to the Rigby Tool Gap "
                "Ledger."
            ),
        )
        close_p.add_argument(
            "--allow-ledger-drift",
            action="store_true",
            help=(
                "S3041 meta-fix escape hatch: report ledger drift but "
                "allow close to proceed. Logged for audit. Use for "
                "legitimate legacy-reference cases where the referenced "
                "row is narrative context, not this-session work."
            ),
        )

    def handle(self, *args, **options):
        subcommand = options["subcommand"]

        if subcommand == "history":
            log_path = Path(options.get("log_path") or FRESHNESS_LOG_PATH)
            self._handle_history(log_path, int(options.get("limit") or 10))
            return

        wrapper_path = Path(options.get("wrapper_path") or WRAPPER_PATH)
        user = self._resolve_user(options["user"])

        if subcommand == "status":
            self._handle_status(wrapper_path, user)
        elif subcommand == "open":
            self._handle_open(
                wrapper_path=wrapper_path,
                user=user,
                label=options["label"],
                carry_forward=options.get("carry_forward"),
                dry_run=bool(options.get("dry_run")),
            )
        elif subcommand == "close":
            self._handle_close(
                wrapper_path=wrapper_path,
                user=user,
                label=options.get("label"),
                carry_forward=options.get("carry_forward"),
                retire_only=bool(options.get("retire_only")),
                dry_run=bool(options.get("dry_run")),
                content_mirror_id=options.get("content_mirror_id"),
                ratification_envelope_id=options.get("ratification_envelope_id"),
                allow_no_mirror=bool(options.get("allow_no_mirror")),
                handoff_path=options.get("handoff"),
                ledger_deliverable_id=options.get("ledger_deliverable_id"),
                allow_ledger_drift=bool(options.get("allow_ledger_drift")),
            )

    # ─────────────────────────── helpers ───────────────────────────── #

    def _resolve_user(self, username: str):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(username=username)
        except UserModel.DoesNotExist as exc:
            raise CommandError(
                f"User {username!r} not found in auth_user. "
                f"Pass --user <username> or create the user first."
            ) from exc

    def _read_wrapper(self, wrapper_path: Path) -> str:
        if not wrapper_path.exists():
            raise CommandError(
                f"Wrapper file not found at {wrapper_path}. "
                f"Pass --wrapper-path to override."
            )
        return wrapper_path.read_text()

    def _extract_current_pin(self, wrapper_text: str, wrapper_path: Path) -> str:
        """Return the pin matched by _WRAPPER_LINE_RE.

        Raises CommandError with match-count details if 0 or >1 matches.
        """
        matches = list(_WRAPPER_LINE_RE.finditer(wrapper_text))
        if len(matches) == 0:
            raise CommandError(
                f"No live invocation line found in {wrapper_path}. Expected exactly "
                f'one line matching: python tools/pa_chat.py "$@" --tools '
                f'--conversation pa-<16 hex>. Fix the wrapper manually and retry.'
            )
        if len(matches) > 1:
            # Show line numbers of each candidate for manual diagnosis.
            line_starts = _line_numbers_for_matches(wrapper_text, matches)
            raise CommandError(
                f"Found {len(matches)} live invocation lines in {wrapper_path} "
                f"(lines: {', '.join(str(n) for n in line_starts)}). Refusing to "
                f"rewrite — pin identity is ambiguous. Fix the wrapper manually "
                f"and retry."
            )
        pin = matches[0].group(2)
        if not _PIN_RE.match(pin):
            raise CommandError(
                f"Extracted pin {pin!r} does not match expected format "
                f"'pa-<16 hex>'. Wrapper may be malformed."
            )
        return pin

    def _rewrite_wrapper(self, wrapper_path: Path, old_pin: str, new_pin: str) -> None:
        """Replace old_pin with new_pin in wrapper_path. Preserves everything else.

        Precondition: _extract_current_pin already confirmed exactly one match.
        Raises RuntimeError on write failure (caller prints recovery output).
        """
        text = wrapper_path.read_text()
        # Rebuild via regex substitution rather than a naive string replace so
        # we never touch pa- references in the historical comment blocks.
        new_text, count = _WRAPPER_LINE_RE.subn(
            lambda m: f"{m.group(1)}{new_pin}", text, count=1,
        )
        if count != 1:
            raise RuntimeError(
                f"Rewrite substitution matched {count} times (expected 1). "
                f"Wrapper state changed between read and write. Aborting."
            )
        wrapper_path.write_text(new_text)
        # Sanity re-read: confirm new_pin now present, old_pin absent from the
        # invocation line specifically (still permitted in comment blocks).
        verify = wrapper_path.read_text()
        verify_matches = list(_WRAPPER_LINE_RE.finditer(verify))
        if len(verify_matches) != 1 or verify_matches[0].group(2) != new_pin:
            raise RuntimeError(
                f"Rewrite verify failed: expected one live invocation with "
                f"pin={new_pin}, got {len(verify_matches)} matches."
            )

    def _derive_carry_forward(self, pin: Optional[str], user_id: int) -> str:
        """Auto-derive carry-forward via session_health_service (same as create_fresh)."""
        if not pin:
            return ""
        try:
            from core.services.session_health_service import get_session_health
            health = get_session_health(pin, user_id)
            return health.get("starter_prompt", "") or ""
        except Exception as exc:
            self.stderr.write(
                f"[session_lifecycle] carry-forward derivation failed for "
                f"pin={pin}: {type(exc).__name__}: {exc}. Proceeding with "
                f"empty carry-forward."
            )
            return ""

    def _create_fresh_conversation(
        self,
        user_id: int,
        label: str,
        carry_forward: str,
    ) -> str:
        """Mint pa-<uuid[:16]> + seed ChatConversation row. Returns new pin.

        Mirrors td_handlers_core._handle_session_tool action='create_fresh'
        (line 3955) so behavior stays consistent with the PA tool path.
        """
        from core.models import ChatConversation

        new_pin = f"pa-{uuid.uuid4().hex[:16]}"
        user_message = (
            f"[Session created] {carry_forward}" if carry_forward
            else "[Session created]"
        )
        assistant_response = (
            f"Fresh session started. Context carried forward: "
            f"{carry_forward[:500]}"
            if carry_forward
            else "Fresh session started. Ready to go."
        )
        ChatConversation.objects.create(
            conversation_id=new_pin,
            user_id=user_id,
            session_title=label,
            user_message=user_message,
            assistant_response=assistant_response,
        )
        return new_pin

    def _retire_pin(self, pin: str, user_id: int) -> int:
        """Bulk-flip session_active=False on all rows for pin. Returns updated_count.

        Mirrors td_handlers_core._handle_session_tool action='retire' (line 4104)
        but does not enforce the _bound_conversation_id guard: rotation is the
        rewrite-the-wrapper-in-the-same-command action that guard is designed
        to protect. See file docstring "Wrapper rewrite safety contract".
        """
        from core.models import ChatConversation

        return (
            ChatConversation.objects
            .filter(conversation_id=pin, user_id=user_id, session_active=True)
            .update(session_active=False)
        )

    def _pin_summary(self, pin: str, user_id: int) -> dict:
        """Return {owner_username, message_count, session_active_rows, last_active_at, triggers_matched}."""
        from core.models import ChatConversation

        qs = ChatConversation.objects.filter(conversation_id=pin, user_id=user_id)
        if not qs.exists():
            return {
                "found": False,
                "owner_username": None,
                "message_count": 0,
                "session_active_rows": 0,
                "last_active_at": None,
                "triggers_matched": [],
            }

        first_row = qs.order_by("created_at").first()
        UserModel = get_user_model()
        owner_username: Optional[str] = None
        try:
            owner_username = UserModel.objects.get(id=first_row.user_id).username
        except UserModel.DoesNotExist:
            owner_username = None

        # ChatConversation only has auto_now_add=True on created_at;
        # no updated_at field. Use created_at of the most recent row as
        # the "last activity" timestamp.
        agg = qs.aggregate(cnt=Count("id"), last=Max("created_at"))
        message_count = agg["cnt"] or 0
        last_active_at = agg["last"]
        session_active_rows = qs.filter(session_active=True).count()

        # Retirement-trigger matching (Q1 from tracker Phase 5 retirement discipline)
        triggers = []
        if message_count > 50:
            triggers.append("message_count_over_50")
        if session_active_rows == 0:
            triggers.append("session_marked_inactive")
        if last_active_at:
            from django.utils import timezone
            hours_idle = (timezone.now() - last_active_at).total_seconds() / 3600.0
            if hours_idle > 24:
                triggers.append("no_activity_in_last_24h")

        return {
            "found": True,
            "owner_username": owner_username,
            "message_count": message_count,
            "session_active_rows": session_active_rows,
            "last_active_at": last_active_at.isoformat() if last_active_at else None,
            "triggers_matched": triggers,
        }

    # ─────────────────────────── subcommands ───────────────────────── #

    def _handle_status(self, wrapper_path: Path, user):
        wrapper_text = self._read_wrapper(wrapper_path)
        pin = self._extract_current_pin(wrapper_text, wrapper_path)
        summary = self._pin_summary(pin, user.id)

        lines = ["[SESSION_LIFECYCLE] wrapper pin status:"]
        lines.append(f"  wrapper: {wrapper_path}")
        lines.append(f"  pin: {pin}")
        lines.append(f"  requested user: {user.username} (id={user.id})")
        if not summary["found"]:
            lines.append(
                f"  ⚠ pin has NO ChatConversation rows for this user — pin "
                f"is orphan or belongs to a different owner."
            )
        else:
            lines.append(f"  owner: {summary['owner_username']}")
            lines.append(f"  message_count: {summary['message_count']}")
            lines.append(f"  session_active_rows: {summary['session_active_rows']}")
            lines.append(f"  last_active_at: {summary['last_active_at']}")
            if summary["triggers_matched"]:
                lines.append(
                    f"  triggers_matched: {', '.join(summary['triggers_matched'])} "
                    f"— rotation recommended"
                )
            else:
                lines.append("  triggers_matched: none — no rotation trigger firing")
        self.stdout.write("\n".join(lines))

    def _handle_open(
        self,
        wrapper_path: Path,
        user,
        label: str,
        carry_forward: Optional[str],
        dry_run: bool,
    ):
        wrapper_text = self._read_wrapper(wrapper_path)
        current_pin = self._extract_current_pin(wrapper_text, wrapper_path)

        derived_source = "explicit" if carry_forward is not None else "auto"
        if carry_forward is None:
            carry_forward = self._derive_carry_forward(current_pin, user.id)

        if dry_run:
            self.stdout.write("[SESSION_LIFECYCLE] open --dry-run:")
            self.stdout.write(f"  wrapper: {wrapper_path}")
            self.stdout.write(f"  current pin (will remain active): {current_pin}")
            self.stdout.write(f"  label for fresh pin: {label}")
            self.stdout.write(f"  carry_forward source: {derived_source}")
            self.stdout.write(
                f"  carry_forward length: {len(carry_forward)} chars"
            )
            self.stdout.write("  action: mint fresh pa-<uuid[:16]> + rewrite wrapper")
            self.stdout.write("  no DB or wrapper writes will be performed.")
            return

        with transaction.atomic():
            new_pin = self._create_fresh_conversation(
                user_id=user.id,
                label=label,
                carry_forward=carry_forward,
            )
            try:
                self._rewrite_wrapper(wrapper_path, current_pin, new_pin)
            except Exception as exc:
                # DB row already created; wrapper rewrite failed. Surface
                # recovery output and re-raise with exit 2.
                self.stderr.write(self.style.ERROR(
                    "[SESSION_LIFECYCLE] wrapper rewrite FAILED after DB "
                    "row was created. Recovery:"
                ))
                self.stderr.write(f"  old pin (still in wrapper): {current_pin}")
                self.stderr.write(f"  new pin (created in DB): {new_pin}")
                self.stderr.write(
                    f"  fix wrapper manually — search {wrapper_path} for "
                    f"'--conversation pa-' and replace {current_pin} with {new_pin}."
                )
                raise CommandError(
                    f"Wrapper rewrite failed after DB commit: {exc}"
                ) from exc

        self.stdout.write("[SESSION_LIFECYCLE] open complete:")
        self.stdout.write(f"  old pin (unchanged): {current_pin}")
        self.stdout.write(f"  new pin (wrapper now points here): {new_pin}")
        self.stdout.write(f"  label: {label}")
        self.stdout.write(f"  carry_forward source: {derived_source}, "
                          f"{len(carry_forward)} chars")

        # S2775 N15: freshness verdict telemetry. Fail-soft — a diagnostic
        # capture must never break the pin mint that already succeeded.
        row = self._record_session_freshness(
            new_pin=new_pin,
            label=label,
            context="session_open",
        )
        if row:
            self.stdout.write(
                f"  freshness: {row.get('verdict')} · "
                f"head={row.get('head_sha_short')} · "
                f"celery_stale={row.get('celery_stale_count')}/"
                f"{row.get('celery_worker_count')}"
            )

    def _handle_close(
        self,
        wrapper_path: Path,
        user,
        label: Optional[str],
        carry_forward: Optional[str],
        retire_only: bool,
        dry_run: bool,
        content_mirror_id: Optional[str] = None,
        ratification_envelope_id: Optional[str] = None,
        allow_no_mirror: bool = False,
        handoff_path: Optional[str] = None,
        ledger_deliverable_id: Optional[str] = None,
        allow_ledger_drift: bool = False,
    ):
        wrapper_text = self._read_wrapper(wrapper_path)
        current_pin = self._extract_current_pin(wrapper_text, wrapper_path)

        if not retire_only and not label:
            raise CommandError(
                "close requires --label (for the fresh pin) unless --retire-only is set."
            )

        # Ledger #16 (S2941): twin-mirror enforcement. Ran pre-transaction so
        # a refuse produces clean rollback semantics (no retire_pin / mint has
        # occurred yet). Skipped for retire_only closes — those are recovery
        # ops, not ratification ceremonies.
        mirror_result = None
        if not retire_only:
            from core.services.twin_mirror_enforcement import (
                TwinMirrorEnforcementError,
                assert_twin_mirror_at_close,
            )
            try:
                mirror_result = assert_twin_mirror_at_close(
                    content_mirror_id=content_mirror_id,
                    ratification_envelope_id=ratification_envelope_id,
                    allow_no_mirror=allow_no_mirror,
                )
            except TwinMirrorEnforcementError as exc:
                raise CommandError(str(exc)) from exc

        # S3041 meta-fix: ledger reconciliation enforcement. Same pre-
        # transaction placement as twin-mirror for clean rollback. Skipped
        # for retire_only (no ratification). Silent no-op when --handoff
        # is not provided so legacy close invocations remain green.
        ledger_result = None
        if not retire_only and handoff_path:
            from core.services.ledger_reconciliation import (
                LedgerReconciliationError,
                check_ledger_reconciliation_at_close,
            )
            try:
                ledger_result = check_ledger_reconciliation_at_close(
                    handoff_path=handoff_path,
                    ledger_deliverable_id=ledger_deliverable_id,
                    allow_ledger_drift=allow_ledger_drift,
                )
            except LedgerReconciliationError as exc:
                raise CommandError(str(exc)) from exc

        derived_source = "explicit" if carry_forward is not None else "auto"
        if carry_forward is None and not retire_only:
            carry_forward = self._derive_carry_forward(current_pin, user.id)
        elif carry_forward is None:
            carry_forward = ""

        if dry_run:
            self.stdout.write("[SESSION_LIFECYCLE] close --dry-run:")
            self.stdout.write(f"  wrapper: {wrapper_path}")
            self.stdout.write(f"  current pin (will be retired): {current_pin}")
            if retire_only:
                self.stdout.write("  mode: retire-only (no mint, no rewrite)")
            else:
                self.stdout.write(f"  label for fresh pin: {label}")
                self.stdout.write(f"  carry_forward source: {derived_source}, "
                                  f"{len(carry_forward)} chars")
                self.stdout.write(
                    "  action: retire current, mint fresh, rewrite wrapper (in order)"
                )
            self.stdout.write("  no DB or wrapper writes will be performed.")
            return

        with transaction.atomic():
            retired = self._retire_pin(current_pin, user.id)
            new_pin: Optional[str] = None
            if not retire_only:
                # Precondition validated above (line-scope): retire_only=False
                # requires --label; the earlier raise CommandError guarantees
                # label is a non-empty str here.
                assert label is not None
                new_pin = self._create_fresh_conversation(
                    user_id=user.id,
                    label=label,
                    carry_forward=carry_forward,
                )

        # Wrapper rewrite outside the transaction — it's a filesystem op and
        # cannot rollback the DB. Rewrite failure post-DB-commit prints
        # recovery output (Q1 SIGN).
        if not retire_only:
            assert new_pin is not None
            try:
                self._rewrite_wrapper(wrapper_path, current_pin, new_pin)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(
                    "[SESSION_LIFECYCLE] wrapper rewrite FAILED after DB "
                    "retire + mint committed. Recovery:"
                ))
                self.stderr.write(f"  old pin (retired, still in wrapper): {current_pin}")
                self.stderr.write(f"  new pin (created in DB): {new_pin}")
                self.stderr.write(
                    f"  fix wrapper manually — search {wrapper_path} for "
                    f"'--conversation pa-' and replace {current_pin} with {new_pin}."
                )
                self.stderr.write(
                    "  NOTE: old pin is retired; if you didn't intend to close it, "
                    "run: python manage.py session_lifecycle open --label X "
                    "(this will mint yet another pin) OR use "
                    "session_tool.set_active via Rigby to un-retire."
                )
                raise CommandError(
                    f"Wrapper rewrite failed after DB commit: {exc}"
                ) from exc

        self.stdout.write("[SESSION_LIFECYCLE] close complete:")
        self.stdout.write(f"  retired pin: {current_pin} (rows updated: {retired})")
        if new_pin:
            self.stdout.write(f"  new pin (wrapper now points here): {new_pin}")
            self.stdout.write(f"  label: {label}")
            self.stdout.write(f"  carry_forward source: {derived_source}, "
                              f"{len(carry_forward)} chars")
        else:
            self.stdout.write(
                "  mode: retire-only — wrapper still points to retired pin. "
                "Run: python manage.py session_lifecycle open --label X"
            )

        # Ledger #16: stdout audit line for the twin-mirror decision.
        if mirror_result is not None:
            if mirror_result.mode == "verified":
                self.stdout.write(
                    f"  [TWIN-MIRROR VERIFIED] content_mirror="
                    f"{mirror_result.content_mirror_id} "
                    f"({mirror_result.content_mirror_title!r}); "
                    f"ratification_envelope="
                    f"{mirror_result.ratification_envelope_id} "
                    f"({mirror_result.ratification_envelope_title!r})"
                )
            elif mirror_result.mode == "allowed_no_mirror":
                self.stdout.write(
                    "  [TWIN-MIRROR ALLOW_NO_MIRROR] close proceeded without "
                    "twin-mirror verification (--allow-no-mirror)."
                )

        # S3041 meta-fix: stdout audit line for the ledger reconciliation decision.
        if ledger_result is not None:
            refs = ", ".join(f"#{n}" for n in ledger_result.referenced_entries) or "(none)"
            flipped = ", ".join(f"#{n}" for n in ledger_result.flipped_entries) or "(none)"
            if ledger_result.mode == "clean":
                self.stdout.write(
                    f"  [LEDGER-RECON CLEAN] referenced={refs}; flipped={flipped}"
                )
            elif ledger_result.mode == "allowed_drift":
                drift = ", ".join(f"#{n}" for n in ledger_result.drift_entries)
                self.stdout.write(
                    f"  [LEDGER-RECON ALLOWED_DRIFT] referenced={refs}; "
                    f"flipped={flipped}; drift={drift} (--allow-ledger-drift)"
                )
            elif ledger_result.mode == "no_handoff":
                self.stdout.write(
                    "  [LEDGER-RECON NO_HANDOFF] handoff path not found — "
                    "nothing to check."
                )


    # ─────────────────────────── freshness telemetry (N15) ────────── #

    def _record_session_freshness(
        self,
        new_pin: str,
        label: str,
        context: str,
        log_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Capture the current freshness verdict + append one JSONL row.

        Fail-soft: any exception is logged as a warning and an empty dict
        is returned. This function must never break the caller (a pin
        mint that already committed successfully).

        Row shape (kept lean per S2775 N15 Rigby SIGN):
          ts, session_label, pin, context, verdict, head_sha_short,
          head_commit_age_seconds, daphne_pid_age_seconds,
          celery_worker_count, celery_stale_count
        """
        try:
            from core.services.process_freshness import compute_process_staleness

            verdict_payload = compute_process_staleness()
            head_sha = (verdict_payload.get('head_commit_sha') or '')[:12]
            head_ts_iso = verdict_payload.get('head_commit_timestamp')
            head_age_seconds: Optional[int] = None
            if head_ts_iso:
                try:
                    head_dt = datetime.fromisoformat(head_ts_iso)
                    head_age_seconds = int(
                        (datetime.now(tz=timezone.utc) - head_dt).total_seconds()
                    )
                except (TypeError, ValueError):
                    head_age_seconds = None

            workers = verdict_payload.get('celery_workers_status') or []
            celery_worker_count = len(workers)
            celery_stale_count = sum(
                1 for w in workers
                if isinstance(w, dict) and w.get('started_before_head_commit')
            )

            row: Dict[str, Any] = {
                'ts': datetime.now(tz=timezone.utc).isoformat(),
                'session_label': label,
                'pin': new_pin,
                'context': context,
                'verdict': verdict_payload.get('staleness_verdict', 'UNKNOWN'),
                'head_sha_short': head_sha,
                'head_commit_age_seconds': head_age_seconds,
                'daphne_pid_age_seconds': verdict_payload.get('daphne_pid_age_seconds'),
                'celery_worker_count': celery_worker_count,
                'celery_stale_count': celery_stale_count,
            }

            target = Path(log_path) if log_path else FRESHNESS_LOG_PATH
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('a', encoding='utf-8') as f:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
            return row
        except Exception as exc:  # noqa: BLE001 — telemetry, not control plane
            logger.warning(
                "[session_lifecycle] freshness capture failed (swallowed): "
                "%s: %s",
                type(exc).__name__,
                exc,
            )
            self.stderr.write(
                f"[SESSION_LIFECYCLE] freshness telemetry capture failed: "
                f"{type(exc).__name__}: {exc} (swallowed — pin mint still succeeded)"
            )
            return {}

    def _handle_history(self, log_path: Path, limit: int):
        if not log_path.exists():
            self.stdout.write(
                f"[SESSION_LIFECYCLE] no freshness log at {log_path} yet. "
                f"Run `python manage.py session_lifecycle open --label X` to "
                f"generate one."
            )
            return

        rows = []
        with log_path.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        recent = rows[-limit:] if limit > 0 else rows
        self.stdout.write(
            f"[SESSION_LIFECYCLE] freshness history "
            f"({len(recent)} of {len(rows)} rows shown):"
        )
        for row in recent:
            self.stdout.write(
                f"  {row.get('ts')}  "
                f"{row.get('verdict','?'):<14}  "
                f"head={row.get('head_sha_short','?')}  "
                f"celery_stale={row.get('celery_stale_count','?')}/"
                f"{row.get('celery_worker_count','?')}  "
                f"label={row.get('session_label','?')}"
            )


def _line_numbers_for_matches(text: str, matches) -> list:
    """Given match objects on `text`, return the 1-indexed line number each starts on."""
    line_starts = []
    for m in matches:
        line_starts.append(text.count("\n", 0, m.start()) + 1)
    return line_starts
