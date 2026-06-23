"""Tests for tools/check_reasoning_contract.py.

Session 1216 Phase E (PR #2). Confirms the AST-based lint:

- Fires on chat.completions.create with forbidden kwargs + gpt-5.x model
- Doesn't fire on non-reasoning models
- Doesn't fire when only allowed kwargs are passed
- Treats OPENAI_CONFIG['model'] as gpt-5.x by default
- Ignores docstrings/comments referencing the pattern
"""

import sys
import textwrap
from pathlib import Path
from unittest import TestCase

# Load the lint module without invoking its main() via direct path import.
_TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(_TOOLS_DIR))
from check_reasoning_contract import scan_file  # noqa: E402


class ReasoningContractLintTests(TestCase):
    def _scan_text(self, source: str):
        """Write source to a temp file and run the lint scanner against it."""
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8",
        ) as fh:
            fh.write(textwrap.dedent(source))
            tmp_path = Path(fh.name)
        try:
            return scan_file(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_gpt5_with_max_tokens_flagged(self):
        violations = self._scan_text("""
            def f(client):
                return client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[],
                    max_tokens=500,
                )
        """)
        self.assertEqual(len(violations), 1)
        _, model, forbidden = violations[0]
        self.assertEqual(model, "gpt-5-mini")
        self.assertEqual(forbidden, ["max_tokens"])

    def test_gpt5_with_temperature_flagged(self):
        violations = self._scan_text("""
            def f(client):
                return client.chat.completions.create(
                    model="gpt-5",
                    temperature=0.5,
                )
        """)
        self.assertEqual(len(violations), 1)
        _, _, forbidden = violations[0]
        self.assertEqual(forbidden, ["temperature"])

    def test_gpt5_with_multiple_forbidden_flagged(self):
        violations = self._scan_text("""
            def f(client):
                return client.chat.completions.create(
                    model="gpt-5-mini",
                    max_tokens=500,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1,
                )
        """)
        self.assertEqual(len(violations), 1)
        _, _, forbidden = violations[0]
        self.assertEqual(set(forbidden), {
            "max_tokens", "temperature", "top_p",
            "frequency_penalty", "presence_penalty",
        })

    def test_non_reasoning_model_not_flagged(self):
        for model in ("gpt-4o", "gpt-4.1", "o3-mini", "qwen2.5:14b"):
            violations = self._scan_text(f"""
                def f(client):
                    return client.chat.completions.create(
                        model="{model}",
                        max_tokens=500,
                        temperature=0.7,
                    )
            """)
            self.assertEqual(len(violations), 0, f"unexpectedly flagged: {model}")

    def test_gpt5_with_only_allowed_kwargs_not_flagged(self):
        violations = self._scan_text("""
            def f(client):
                return client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[],
                    max_completion_tokens=500,
                    reasoning_effort="medium",
                )
        """)
        self.assertEqual(len(violations), 0)

    def test_openai_config_model_treated_as_gpt5(self):
        violations = self._scan_text("""
            def f(client, OPENAI_CONFIG):
                return client.chat.completions.create(
                    model=OPENAI_CONFIG['model'],
                    max_tokens=500,
                )
        """)
        self.assertEqual(len(violations), 1)
        _, _, forbidden = violations[0]
        self.assertEqual(forbidden, ["max_tokens"])

    def test_dynamic_model_unknown_not_flagged(self):
        """Models from variables that aren't gpt-5 literals or
        OPENAI_CONFIG references are silently allowed (no false
        positives on routing layers)."""
        violations = self._scan_text("""
            def f(client, model):
                return client.chat.completions.create(
                    model=model,
                    max_tokens=500,
                )
        """)
        self.assertEqual(len(violations), 0)

    def test_self_client_chained_create_flagged(self):
        violations = self._scan_text("""
            def f(self):
                return self.client.chat.completions.create(
                    model="gpt-5-mini",
                    max_tokens=500,
                )
        """)
        self.assertEqual(len(violations), 1)

    def test_docstrings_and_comments_not_flagged(self):
        """The AST-based lint should not match docstring text or
        comments — that was the regex-lint's failure mode."""
        violations = self._scan_text('''
            def f(client):
                """Documents client.chat.completions.create(max_tokens=500)
                for reference but never calls it."""
                # Same: client.chat.completions.create(max_tokens=500)
                pass
        ''')
        self.assertEqual(len(violations), 0)

    def test_non_create_attribute_call_not_flagged(self):
        """Random *.create() calls that aren't on chat.completions
        should pass through cleanly."""
        violations = self._scan_text("""
            def f(obj):
                obj.create(model="gpt-5-mini", max_tokens=500)
                obj.completions.create(model="gpt-5-mini", max_tokens=500)
        """)
        self.assertEqual(len(violations), 0)
