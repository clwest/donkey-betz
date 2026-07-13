"""S2776 N21 — verify tools/pa_local.sh token + pin resolve to the same user.

Catches the S2774 travel-recovery scenario in seconds instead of the ~30min
log-tail deep-dive that ended it. Called from the `tools/pa_local.sh` bash
prelude on the first invocation per pin. Cache file at
``~/.claude-pa-verified/<pin>.json`` marks a pin as verified so subsequent
invocations of the same pin skip the check.

Single-concern by design (per Rigby S2776 SIGN Q1 fold): identity/auth
verification lives in its own command rather than accreting into
``session_lifecycle`` alongside pin+wrapper+freshness. If a future arc
extends this command with a THIRD flag that hits the API or reads/writes
the wrapper cache, refactor trigger fires — split into
``session_lifecycle`` (pin+wrapper) + ``toolchain_doctor`` (freshness +
ownership + other).

Exit codes:
    0 — verified · token owner == pin owner · cache written
    2 — MISMATCH · token owner != pin owner (recovery: rotate token OR
        run `session_lifecycle open --user <owner>`)
    3 — token invalid · missing env / whoami returned 4xx / Django
        unreachable
    4 — pin belongs to no user · orphan pin (recovery: retire pin +
        mint fresh)

Escape hatch (bash-side): setting ``PA_LOCAL_ALLOW_MISMATCH=1`` in the
environment makes the wrapper warn-and-continue on any non-zero exit
from this command instead of aborting the dispatch. Preserves
close-ceremony continuity for emergencies without defeating the default
fail-loud semantics.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from django.core.management.base import BaseCommand


CACHE_DIR = Path.home() / ".claude-pa-verified"
DEFAULT_API_URL = "http://localhost:8000"


class Command(BaseCommand):
    help = (
        "Verify tools/pa_local.sh PA_API_TOKEN + pin resolve to the same "
        "user. Writes ~/.claude-pa-verified/<pin>.json on success. See "
        "file docstring for exit codes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--pin",
            required=True,
            help="Wrapper pin (format: pa-<16 hex>).",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            dest="as_json",
            help="Emit result as JSON on stdout (stderr silenced).",
        )
        parser.add_argument(
            "--api-url",
            default=None,
            help="Override API URL (tests / non-standard layouts only).",
        )
        parser.add_argument(
            "--cache-dir",
            default=None,
            help="Override cache dir (tests only).",
        )

    def handle(self, *args, **options):
        pin = options["pin"]
        api_url = (
            options.get("api_url")
            or os.environ.get("PA_API_URL")
            or DEFAULT_API_URL
        )
        cache_dir = Path(options["cache_dir"]) if options.get("cache_dir") else CACHE_DIR
        as_json = bool(options.get("as_json"))
        token = os.environ.get("PA_API_TOKEN") or ""

        if not token:
            self._fail(3, "PA_API_TOKEN env var not set", as_json)

        # Step 1: hit /api/pa/whoami/ using the token. This validates:
        #   (a) Django/Daphne is reachable at api_url
        #   (b) Token is accepted by the auth layer
        #   (c) Returns the authenticated user's identity
        try:
            req = urllib.request.Request(
                f"{api_url.rstrip('/')}/api/pa/whoami/",
                headers={"Authorization": f"Token {token}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                whoami = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            self._fail(3, f"whoami HTTP {e.code} — token rejected", as_json)
        except urllib.error.URLError as e:
            self._fail(3, f"whoami connection error: {e.reason}", as_json)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._fail(3, f"whoami response malformed: {e}", as_json)

        token_user_id = whoami.get("user_id")
        token_username = whoami.get("username")
        if token_user_id is None or not token_username:
            self._fail(3, f"whoami missing user_id/username: {whoami!r}", as_json)
        # Normalize to string — user_id is UUID on this platform but the
        # command should behave the same on int PKs. String compare is
        # safe for both after both sides are stringified.
        token_user_id = str(token_user_id)

        # Step 2: look up pin ownership via ORM. ChatConversation rows carry
        # user_id, so first row for this conversation_id gives us the owner.
        from core.models import ChatConversation

        row = (
            ChatConversation.objects
            .filter(conversation_id=pin)
            .order_by("created_at")
            .first()
        )
        if row is None:
            self._fail(4, f"pin {pin} not found in ChatConversation table", as_json)
        pin_user_id = str(row.user_id)

        # Step 3: compare identities.
        if pin_user_id != token_user_id:
            pin_username = self._username_for(pin_user_id)
            self._fail(
                2,
                (
                    f"MISMATCH: token owner={token_username} "
                    f"(id={token_user_id}) vs pin owner={pin_username} "
                    f"(id={pin_user_id}). Fix: rotate PA_API_TOKEN in "
                    f"tools/pa_local.sh OR rotate wrapper pin via "
                    f"session_lifecycle open."
                ),
                as_json,
            )

        # Step 4: write cache. Per-pin file; contents include verified user_id
        # so a future N21 v2 wrapper prelude could compare and invalidate on
        # user_id change without hitting the API (out of scope for v1 per
        # Rigby Q3 fold).
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{pin}.json"
        cache_payload: Dict[str, Any] = {
            "pin": pin,
            "verified_user_id": token_user_id,
            "verified_username": token_username,
            "verified_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        cache_path.write_text(
            json.dumps(cache_payload) + "\n",
            encoding="utf-8",
        )

        # Step 5: success output.
        if as_json:
            self.stdout.write(json.dumps({"ok": True, **cache_payload}))
        else:
            self.stdout.write(
                f"[pa_local] ✓ token={token_username} · pin={pin} "
                f"· pin_owner={token_username}"
            )

    # ─────────────────────────── helpers ───────────────────────────── #

    def _fail(self, exit_code: int, message: str, as_json: bool) -> None:
        """Emit failure message + exit with the given code. Does not return."""
        if as_json:
            self.stdout.write(
                json.dumps({"ok": False, "exit_code": exit_code, "message": message})
            )
        else:
            self.stderr.write(f"[pa_local] ✗ {message}")
        sys.exit(exit_code)

    def _username_for(self, user_id) -> str:
        try:
            from django.contrib.auth import get_user_model
            return get_user_model().objects.get(id=user_id).username
        except Exception:  # noqa: BLE001 — best-effort label for the error message
            return f"user_id={user_id}"
