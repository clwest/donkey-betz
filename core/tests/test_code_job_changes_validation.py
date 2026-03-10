"""Tests for code-job change validation logic.

Covers CODEJOB_FILE_TOO_LARGE and CODEJOB_ANCHOR_NOT_FOUND guardrails.
"""

import pytest

from core.codejobs import (
    CODEJOB_ANCHOR_NOT_FOUND,
    CODEJOB_FILE_TOO_LARGE,
    MAX_CODEJOB_FILE_SIZE,
    CodeJobValidationError,
    validate_anchor_present,
    validate_codejob_change,
    validate_file_size,
)


class TestValidateFileSize:
    def test_accepts_small_file(self):
        validate_file_size("hello world", "test.py")  # should not raise

    def test_accepts_file_at_exact_limit(self):
        content = "x" * MAX_CODEJOB_FILE_SIZE
        validate_file_size(content, "test.py")  # should not raise

    def test_raises_for_oversized_file(self):
        content = "x" * (MAX_CODEJOB_FILE_SIZE + 1)
        with pytest.raises(CodeJobValidationError) as exc_info:
            validate_file_size(content, "big_file.py")
        assert exc_info.value.failure_code == CODEJOB_FILE_TOO_LARGE
        assert "big_file.py" in exc_info.value.message

    def test_raises_for_bytes_content(self):
        content = b"x" * (MAX_CODEJOB_FILE_SIZE + 1)
        with pytest.raises(CodeJobValidationError) as exc_info:
            validate_file_size(content, "binary.bin")
        assert exc_info.value.failure_code == CODEJOB_FILE_TOO_LARGE

    def test_error_details_populated(self):
        content = "x" * (MAX_CODEJOB_FILE_SIZE + 100)
        with pytest.raises(CodeJobValidationError) as exc_info:
            validate_file_size(content, "foo.py")
        details = exc_info.value.details
        assert details["filename"] == "foo.py"
        assert details["size"] > MAX_CODEJOB_FILE_SIZE
        assert details["max_size"] == MAX_CODEJOB_FILE_SIZE


class TestValidateAnchorPresent:
    def test_accepts_present_anchor(self):
        validate_anchor_present("def foo():\n    pass\n", "def foo():", "test.py")

    def test_raises_for_missing_anchor(self):
        with pytest.raises(CodeJobValidationError) as exc_info:
            validate_anchor_present("def bar():\n    pass\n", "def foo():", "test.py")
        assert exc_info.value.failure_code == CODEJOB_ANCHOR_NOT_FOUND
        assert "test.py" in exc_info.value.message

    def test_error_details_contain_anchor_preview(self):
        anchor = "some_unique_function_name"
        with pytest.raises(CodeJobValidationError) as exc_info:
            validate_anchor_present("no match here", anchor, "module.py")
        assert "anchor_preview" in exc_info.value.details


class TestValidateCodejobChange:
    def test_returns_valid_true_for_good_input(self):
        result = validate_codejob_change(
            "module.py",
            "def foo():\n    pass\n",
            anchor="def foo():",
        )
        assert result == {"valid": True}

    def test_returns_valid_false_for_oversized_file(self):
        large_content = "x" * (MAX_CODEJOB_FILE_SIZE + 1)
        result = validate_codejob_change("big.py", large_content)
        assert result["valid"] is False
        assert result["failure_code"] == CODEJOB_FILE_TOO_LARGE

    def test_returns_valid_false_for_missing_anchor(self):
        result = validate_codejob_change(
            "module.py",
            "def bar():\n    pass\n",
            anchor="def foo():",
        )
        assert result["valid"] is False
        assert result["failure_code"] == CODEJOB_ANCHOR_NOT_FOUND

    def test_skip_size_check(self):
        large_content = "x" * (MAX_CODEJOB_FILE_SIZE + 1)
        result = validate_codejob_change("big.py", large_content, check_size=False)
        assert result["valid"] is True

    def test_does_not_raise(self):
        result = validate_codejob_change("f.py", "", anchor="missing anchor")
        assert isinstance(result, dict)
        assert "valid" in result
