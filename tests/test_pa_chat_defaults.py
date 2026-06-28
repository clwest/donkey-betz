"""Defaults for tools/pa_chat.py — local-by-default + opt-in prod.

Session 1249 P2(b): wrapper-trap cleanup. Bare invocation must hit local.
Explicit PA_API_URL env var wins over both the flag and the default.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
PA_CHAT_PATH = REPO_ROOT / "tools" / "pa_chat.py"

sys.path.insert(0, str(REPO_ROOT))
from tools import pa_chat  # noqa: E402


class DefaultBaseUrlTests(unittest.TestCase):
    """The DEFAULT_BASE_URL constant + _get_base_url() resolver."""

    def test_default_base_url_constant_is_localhost(self) -> None:
        self.assertEqual(pa_chat.DEFAULT_BASE_URL, "http://localhost:8000")

    def test_prod_base_url_constant_is_railway(self) -> None:
        self.assertEqual(
            pa_chat.PROD_BASE_URL,
            "https://donkey-betz-platform-production.up.railway.app",
        )

    def test_get_base_url_no_env_returns_localhost(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PA_API_URL", None)
            self.assertEqual(pa_chat._get_base_url(), "http://localhost:8000")

    def test_get_base_url_env_override_wins(self) -> None:
        with mock.patch.dict(os.environ, {"PA_API_URL": "https://staging.example.com"}):
            self.assertEqual(pa_chat._get_base_url(), "https://staging.example.com")

    def test_get_base_url_prod_constant_when_set_explicitly(self) -> None:
        with mock.patch.dict(os.environ, {"PA_API_URL": pa_chat.PROD_BASE_URL}):
            self.assertEqual(pa_chat._get_base_url(), pa_chat.PROD_BASE_URL)


class EnvFlagPrecedenceTests(unittest.TestCase):
    """CLI --env flag wiring: prod opt-in sets PA_API_URL, env var beats flag."""

    def _run_argparse(self, argv: list[str]) -> tuple[str, str]:
        """Invoke pa_chat.py with argv and return (stdout, stderr).

        We use a tiny harness that calls main() but never sends a real request
        by passing --watch with a bogus conversation id. That path exits before
        hitting the network for the URL probe we care about. Simpler approach:
        spawn the script with --help-like args won't trigger the env switch,
        so we exercise the env-resolution block directly.
        """
        raise NotImplementedError  # pragma: no cover

    def test_env_prod_sets_pa_api_url_when_unset(self) -> None:
        """`--env prod` (no PA_API_URL set) flips to prod + emits warning."""
        env = {k: v for k, v in os.environ.items() if k != "PA_API_URL"}
        # Invoke with --env prod --help so main() runs the env block then argparse exits.
        # Easier: run as subprocess, capture stderr, assert the warning + that PA_API_URL leaked nowhere.
        result = subprocess.run(
            [sys.executable, str(PA_CHAT_PATH), "--env", "prod", "--watch", "pa-nonexistent"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertIn("WARNING: PA_CHAT targeting PRODUCTION", result.stderr)
        self.assertIn(pa_chat.PROD_BASE_URL, result.stderr)

    def test_env_local_does_not_emit_warning(self) -> None:
        """Bare invocation (default --env local) is silent on the URL."""
        env = {k: v for k, v in os.environ.items() if k != "PA_API_URL"}
        result = subprocess.run(
            [sys.executable, str(PA_CHAT_PATH), "--watch", "pa-nonexistent"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotIn("WARNING: PA_CHAT targeting PRODUCTION", result.stderr)

    def test_env_prod_does_not_override_explicit_pa_api_url(self) -> None:
        """If PA_API_URL is already set, --env prod must NOT clobber it."""
        env = {k: v for k, v in os.environ.items() if k != "PA_API_URL"}
        env["PA_API_URL"] = "https://staging.example.com"
        result = subprocess.run(
            [sys.executable, str(PA_CHAT_PATH), "--env", "prod", "--watch", "pa-nonexistent"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # The warning is suppressed when PA_API_URL is already set (precedence: env > flag).
        self.assertNotIn("WARNING: PA_CHAT targeting PRODUCTION", result.stderr)


if __name__ == "__main__":
    unittest.main()
