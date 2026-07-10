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

import re
import uuid
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count, Max


WRAPPER_PATH = Path("tools/pa_local.sh")

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

    def handle(self, *args, **options):
        subcommand = options["subcommand"]
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

    def _handle_close(
        self,
        wrapper_path: Path,
        user,
        label: Optional[str],
        carry_forward: Optional[str],
        retire_only: bool,
        dry_run: bool,
    ):
        wrapper_text = self._read_wrapper(wrapper_path)
        current_pin = self._extract_current_pin(wrapper_text, wrapper_path)

        if not retire_only and not label:
            raise CommandError(
                "close requires --label (for the fresh pin) unless --retire-only is set."
            )

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


def _line_numbers_for_matches(text: str, matches) -> list:
    """Given match objects on `text`, return the 1-indexed line number each starts on."""
    line_starts = []
    for m in matches:
        line_starts.append(text.count("\n", 0, m.start()) + 1)
    return line_starts
