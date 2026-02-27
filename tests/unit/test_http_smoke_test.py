"""
Unit tests for core/tools/http_smoke_test.py

Covers:
- _resolve_variables: substitution, early-fail on unresolved vars
- _run_step: per-step headers merge, resolve error handling
- run_smoke_test: depends_on / skip semantics, test_run_id injection
- Suite integrity: check counts, no duplicates, required fields
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from core.tools.http_smoke_test import (
    BUILTIN_SUITES,
    _check_assertion,
    _extract_value,
    _resolve_variables,
    _run_step,
    run_smoke_test,
)


# ── _resolve_variables ────────────────────────────────────────────────────


class TestResolveVariables:
    def test_basic_substitution(self):
        result = _resolve_variables("hello {{name}}", {"name": "world"})
        assert result == "hello world"

    def test_multiple_vars(self):
        result = _resolve_variables(
            "{{a}}/{{b}}/{{c}}", {"a": "x", "b": "y", "c": "z"}
        )
        assert result == "x/y/z"

    def test_no_vars(self):
        result = _resolve_variables("no variables here", {})
        assert result == "no variables here"

    def test_unresolved_raises_valueerror(self):
        with pytest.raises(ValueError, match="Unresolved variable.*missing"):
            _resolve_variables("x={{missing}}", {})

    def test_partial_unresolved_raises(self):
        with pytest.raises(ValueError, match="Unresolved variable.*b"):
            _resolve_variables("{{a}}/{{b}}", {"a": "resolved"})

    def test_all_resolved_no_error(self):
        result = _resolve_variables("{{x}}", {"x": "ok"})
        assert result == "ok"

    def test_resolve_in_json_body(self):
        body = json.dumps({"title": "[SMOKE][{{run_id}}] test"})
        result = _resolve_variables(body, {"run_id": "abc123"})
        parsed = json.loads(result)
        assert parsed["title"] == "[SMOKE][abc123] test"


# ── _extract_value ─────────────────────────────────────────────────────────


class TestExtractValue:
    def test_simple_key(self):
        assert _extract_value({"status": "ok"}, "$.status") == "ok"

    def test_nested_key(self):
        assert _extract_value({"a": {"b": "c"}}, "$.a.b") == "c"

    def test_array_index(self):
        assert _extract_value({"items": [10, 20]}, "$.items[1]") == 20

    def test_missing_key(self):
        assert _extract_value({"a": 1}, "$.b") is None

    def test_no_dollar_prefix(self):
        assert _extract_value({"a": 1}, "a") is None


# ── _check_assertion ───────────────────────────────────────────────────────


class TestCheckAssertion:
    def test_status_pass(self):
        r = _check_assertion({"check": "status", "expected": 200}, 200, {})
        assert r["pass"] is True

    def test_status_fail(self):
        r = _check_assertion({"check": "status", "expected": 200}, 500, {})
        assert r["pass"] is False

    def test_has_key_pass(self):
        r = _check_assertion({"check": "has_key", "key": "id"}, 200, {"id": "abc"})
        assert r["pass"] is True

    def test_has_key_fail(self):
        r = _check_assertion({"check": "has_key", "key": "id"}, 200, {"name": "x"})
        assert r["pass"] is False

    def test_json_path_eq(self):
        r = _check_assertion(
            {"check": "json_path", "path": "$.status", "operator": "eq", "expected": "resolved"},
            200,
            {"status": "resolved"},
        )
        assert r["pass"] is True

    def test_json_path_gte(self):
        r = _check_assertion(
            {"check": "json_path", "path": "$.count", "operator": "gte", "expected": 3},
            200,
            {"count": 5},
        )
        assert r["pass"] is True

    def test_json_path_gte_fail(self):
        r = _check_assertion(
            {"check": "json_path", "path": "$.count", "operator": "gte", "expected": 3},
            200,
            {"count": 1},
        )
        assert r["pass"] is False


# ── _run_step ──────────────────────────────────────────────────────────────


class TestRunStep:
    def test_unresolved_path_returns_failed(self):
        step = {"name": "bad_path", "method": "GET", "path": "/api/{{unknown_id}}/"}
        result = _run_step(step, {}, "http://localhost:8000", {}, 5000)
        assert result["ok"] is False
        assert "Variable resolution failed" in result["error"]

    def test_unresolved_body_returns_failed(self):
        step = {
            "name": "bad_body",
            "method": "POST",
            "path": "/api/test/",
            "body": {"key": "{{missing_var}}"},
        }
        result = _run_step(step, {}, "http://localhost:8000", {}, 5000)
        assert result["ok"] is False
        assert "Body variable resolution failed" in result["error"]

    def test_unresolved_header_returns_failed(self):
        step = {
            "name": "bad_header",
            "method": "GET",
            "path": "/api/test/",
            "headers": {"X-Custom": "{{missing}}"},
        }
        result = _run_step(step, {}, "http://localhost:8000", {}, 5000)
        assert result["ok"] is False
        assert "Header variable resolution failed" in result["error"]

    def test_step_headers_merge(self):
        """Step headers override auth + Content-Type defaults."""
        step = {
            "name": "custom_header",
            "method": "GET",
            "path": "/api/test/",
            "headers": {"Content-Type": "text/plain", "X-Custom": "val"},
        }
        auth_headers = {"Authorization": "Token abc"}

        with patch("core.tools.http_smoke_test.urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = b'{"ok": true}'
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            _run_step(step, {}, "http://localhost:8000", auth_headers, 5000)

            req = mock_urlopen.call_args[0][0]
            # Step header overrides Content-Type
            assert req.get_header("Content-type") == "text/plain"
            # Auth header preserved
            assert req.get_header("Authorization") == "Token abc"
            # Custom header added
            assert req.get_header("X-custom") == "val"


# ── run_smoke_test (depends_on + skip + test_run_id) ──────────────────────


class TestRunSmokeTest:
    def test_test_run_id_present(self):
        """run_smoke_test injects test_run_id into the return dict."""
        with patch("core.tools.http_smoke_test._run_step") as mock_step:
            mock_step.return_value = {"name": "s1", "ok": True}
            result = run_smoke_test({
                "steps": [{"name": "s1", "method": "GET", "path": "/"}],
            })
        assert "test_run_id" in result
        assert len(result["test_run_id"]) == 12

    def test_test_run_id_in_variables(self):
        """test_run_id is available for variable substitution in steps."""
        captured_vars = {}

        def fake_run_step(step, variables, *args):
            captured_vars.update(variables)
            return {"name": step["name"], "ok": True}

        with patch("core.tools.http_smoke_test._run_step", side_effect=fake_run_step):
            run_smoke_test({
                "steps": [{"name": "s1", "method": "GET", "path": "/"}],
            })
        assert "test_run_id" in captured_vars

    def test_skip_on_failed_dependency(self):
        """Steps with depends_on a failed step are skipped."""
        call_count = {"n": 0}

        def fake_run_step(step, variables, *args):
            call_count["n"] += 1
            if step["name"] == "step1":
                return {"name": "step1", "ok": False}
            return {"name": step["name"], "ok": True}

        with patch("core.tools.http_smoke_test._run_step", side_effect=fake_run_step):
            result = run_smoke_test({
                "steps": [
                    {"name": "step1", "method": "GET", "path": "/"},
                    {"name": "step2", "method": "GET", "path": "/", "depends_on": ["step1"]},
                ],
                "fail_fast": False,
            })

        assert result["failed"] == 1
        assert result["skipped"] == 1
        assert result["passed"] == 0
        # step2 was never executed
        assert call_count["n"] == 1
        # skipped step has the right marker
        skipped_step = result["results"][1]
        assert skipped_step["skipped"] is True
        assert "step1" in skipped_step["error"]

    def test_skip_on_missing_dependency(self):
        """Steps depending on a non-existent step are skipped."""
        with patch("core.tools.http_smoke_test._run_step") as mock_step:
            mock_step.return_value = {"name": "s1", "ok": True}
            result = run_smoke_test({
                "steps": [
                    {"name": "s1", "method": "GET", "path": "/"},
                    {"name": "s2", "method": "GET", "path": "/", "depends_on": ["nonexistent"]},
                ],
                "fail_fast": False,
            })

        assert result["skipped"] == 1
        skipped = result["results"][1]
        assert skipped["skipped"] is True
        assert "not found" in skipped["error"]

    def test_skip_cascades(self):
        """Skipped steps cause downstream dependents to also skip."""
        def fake_run_step(step, variables, *args):
            if step["name"] == "step1":
                return {"name": "step1", "ok": False}
            return {"name": step["name"], "ok": True}

        with patch("core.tools.http_smoke_test._run_step", side_effect=fake_run_step):
            result = run_smoke_test({
                "steps": [
                    {"name": "step1", "method": "GET", "path": "/"},
                    {"name": "step2", "method": "GET", "path": "/", "depends_on": ["step1"]},
                    {"name": "step3", "method": "GET", "path": "/", "depends_on": ["step2"]},
                ],
                "fail_fast": False,
            })

        assert result["failed"] == 1
        assert result["skipped"] == 2
        assert result["ok"] is False

    def test_all_deps_pass_executes(self):
        """Step executes when all dependencies passed."""
        def fake_run_step(step, variables, *args):
            return {"name": step["name"], "ok": True}

        with patch("core.tools.http_smoke_test._run_step", side_effect=fake_run_step):
            result = run_smoke_test({
                "steps": [
                    {"name": "a", "method": "GET", "path": "/"},
                    {"name": "b", "method": "GET", "path": "/"},
                    {"name": "c", "method": "GET", "path": "/", "depends_on": ["a", "b"]},
                ],
                "fail_fast": False,
            })

        assert result["passed"] == 3
        assert result["skipped"] == 0
        assert result["ok"] is True

    def test_ok_false_when_skipped(self):
        """Overall ok is False if any steps were skipped."""
        def fake_run_step(step, variables, *args):
            if step["name"] == "step1":
                return {"name": "step1", "ok": False}
            return {"name": step["name"], "ok": True}

        with patch("core.tools.http_smoke_test._run_step", side_effect=fake_run_step):
            result = run_smoke_test({
                "steps": [
                    {"name": "step1", "method": "GET", "path": "/"},
                    {"name": "step2", "method": "GET", "path": "/", "depends_on": ["step1"]},
                ],
                "fail_fast": False,
            })

        assert result["ok"] is False

    def test_skipped_counter_in_response(self):
        """Response includes skipped counter."""
        with patch("core.tools.http_smoke_test._run_step") as mock_step:
            mock_step.return_value = {"name": "s1", "ok": True}
            result = run_smoke_test({
                "steps": [{"name": "s1", "method": "GET", "path": "/"}],
            })
        assert "skipped" in result
        assert result["skipped"] == 0


# ── Suite integrity ───────────────────────────────────────────────────────


class TestSuiteIntegrity:
    """Session 1075: Verify built-in suites have correct structure."""

    EXPECTED_COUNTS = {
        'cockpit_health': 18,
        'cockpit_incidents_crud': 8,
        'pa_tools_smoke': 20,
    }

    def test_all_expected_suites_exist(self):
        for name in self.EXPECTED_COUNTS:
            assert name in BUILTIN_SUITES, f"Missing suite: {name}"

    @pytest.mark.parametrize("suite_name,expected", EXPECTED_COUNTS.items())
    def test_suite_check_counts(self, suite_name, expected):
        actual = len(BUILTIN_SUITES[suite_name])
        assert actual == expected, (
            f"{suite_name}: expected {expected} checks, got {actual}"
        )

    @pytest.mark.parametrize("suite_name", EXPECTED_COUNTS.keys())
    def test_no_duplicate_step_names(self, suite_name):
        names = [s['name'] for s in BUILTIN_SUITES[suite_name]]
        dupes = [n for n in names if names.count(n) > 1]
        assert not dupes, f"Duplicate step names in {suite_name}: {set(dupes)}"

    @pytest.mark.parametrize("suite_name", EXPECTED_COUNTS.keys())
    def test_steps_have_required_fields(self, suite_name):
        for step in BUILTIN_SUITES[suite_name]:
            assert 'name' in step, f"Step missing 'name' in {suite_name}"
            assert 'method' in step, f"Step '{step.get('name')}' missing 'method'"
            assert 'path' in step, f"Step '{step.get('name')}' missing 'path'"
