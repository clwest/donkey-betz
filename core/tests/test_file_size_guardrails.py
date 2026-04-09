"""Guardrail tests to prevent large files from regressing past safe limits.

The CodeJob executor (remote code worker) must be able to read and patch
files.  If any tracked file grows back above 500KB, the executor's
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

# Files that have been split and must stay under the limit
TRACKED_FILES = [
    "core/tasks.py",
    "core/services/tool_dispatcher.py",
    "core/agents/personal_assistant_agent.py",
    "core/personal_ai_assistant_enhanced.py",
    "core/views_image.py",
    # "core/models_unified_system.py",  # TODO: split requires migration handling
]


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

    @pytest.mark.parametrize("rel_path", TRACKED_FILES)
    def test_tracked_files_under_hard_limit(self, rel_path):
        """All tracked files must stay under 500KB."""
        fpath = REPO_ROOT / rel_path
        if not fpath.exists():
            pytest.skip(f"{rel_path} not found (may have been converted to package)")
        size = fpath.stat().st_size
        assert size < HARD_LIMIT, (
            f"{rel_path} is {size:,} bytes ({size/1024:.0f}KB), "
            f"exceeding the {HARD_LIMIT:,}-byte limit. "
            f"Split this file into smaller modules."
        )


class TestImportSmokeTests:
    """Verify all split modules can be imported without errors."""

    def test_import_tasks_and_domain_modules(self):
        from core import tasks  # noqa: F401
        from core import tasks_agents, tasks_content, tasks_ops  # noqa: F401
        from core import tasks_misc, tasks_media, tasks_spiders  # noqa: F401
        from core import tasks_financial, tasks_initiatives  # noqa: F401
        from core import tasks_body_systems, tasks_conversations  # noqa: F401

    def test_import_ops_autopilot_package(self):
        from core.services.ops_autopilot import (  # noqa: F401
            OpsAutopilot, AutopilotConfig, ActionVerifier,
            BudgetController, ROIEnforcer, ExperimentEngine,
        )

    def test_import_tool_dispatcher_with_mixins(self):
        from core.services.tool_dispatcher import (  # noqa: F401
            get_tool_dispatcher, ToolDispatcher, ToolResult,
        )
        d = get_tool_dispatcher()
        assert len(d._tool_handlers) > 100, "Expected 100+ registered handlers"

    def test_import_thinking_agent(self):
        """PersonalAssistantAgent removed — verify ThinkingAgent loads instead."""
        from core.agents.thinking_agent import ThinkingAgent  # noqa: F401

    def test_import_enhanced_pa(self):
        from core.personal_ai_assistant_enhanced import (  # noqa: F401
            EnhancedPersonalAIAssistant,
        )

    def test_import_views_image_reexports(self):
        from core.views_image import (  # noqa: F401
            gallery_generate, unified_gallery, execute_tool,
        )
