"""Guardrail tests to prevent large files from regressing past safe limits.

The CodeJob executor (remote code worker) must be able to read and patch
core/tasks.py.  If the file grows back above 500KB, the executor's
_MAX_EDIT_FILE_SIZE guard will reject patches and the pipeline breaks.

These tests fail CI *before* the damage reaches production.
"""
from pathlib import Path

import pytest

# Absolute cap — executor rejects files above this
HARD_LIMIT = 500_000  # bytes

# Early-warning threshold
WARN_LIMIT = 450_000  # bytes

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestFileSizeGuardrails:
    def test_tasks_py_under_hard_limit(self):
        """core/tasks.py must stay under 500KB for the code-job executor."""
        size = (REPO_ROOT / "core" / "tasks.py").stat().st_size
        assert size < HARD_LIMIT, (
            f"core/tasks.py is {size:,} bytes ({size/1024:.0f}KB), "
            f"exceeding the {HARD_LIMIT:,}-byte executor limit. "
            f"Extract task bodies into core/tasks_<domain>.py modules "
            f"using tools/do_extract.py."
        )

    @pytest.mark.filterwarnings("default")
    def test_tasks_py_warn_approaching_limit(self):
        """Warn when core/tasks.py is approaching the hard limit."""
        size = (REPO_ROOT / "core" / "tasks.py").stat().st_size
        if size >= WARN_LIMIT:
            pytest.skip(
                f"core/tasks.py is {size:,} bytes ({size/1024:.0f}KB), "
                f"approaching the {HARD_LIMIT:,}-byte limit. "
                f"Consider extracting more tasks soon."
            )
