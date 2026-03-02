"""
PA Tool Schema Drift Guard
===========================

Session G3: Fails CI if pa_tool_schemas.py action enums diverge from
tool_dispatcher.py handler branches + ACTION_ALIASES.

Ensures:
1. Every schema-declared action is handled in the dispatcher.
2. Every registered schema tool has a dispatcher handler.
3. run_agent agent_name enums all map to registered handlers.
"""

import ast
import inspect
import re
import textwrap
from unittest import TestCase

from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
from core.services.tool_dispatcher import ToolDispatcher


class TestToolSchemaDrift(TestCase):
    """Verify PA tool schemas stay aligned with dispatcher handlers."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()
        cls.schema_map = {}  # tool_name -> schema dict
        for schema in PA_TOOL_SCHEMAS:
            name = schema.get('name', '')
            if name:
                cls.schema_map[name] = schema

    # ── 1. Every schema tool must have a registered handler ────────────────

    def test_all_schema_tools_have_handlers(self):
        """Every tool in PA_TOOL_SCHEMAS must be registered in ToolDispatcher."""
        missing = []
        for tool_name in self.schema_map:
            # run_agent delegates to individual agent handlers via _handle_agent_tool
            if tool_name == 'run_agent':
                continue
            if tool_name not in self.dispatcher._tool_handlers:
                missing.append(tool_name)

        self.assertEqual(
            missing, [],
            f"Schema tools with no dispatcher handler: {missing}"
        )

    # ── 2. Every schema action must be handled in the dispatcher ───────────

    def test_schema_actions_covered_by_handler(self):
        """For each action-based tool, every schema action enum value must
        appear in the handler source (as an == comparison or in an
        ACTION_ALIASES dict)."""
        drift = {}

        for tool_name, schema in self.schema_map.items():
            if tool_name == 'run_agent':
                continue

            # Extract action enum from schema
            props = schema.get('parameters', {}).get('properties', {})
            action_enum = props.get('action', {}).get('enum', [])
            if not action_enum:
                continue  # non-action-based tool

            # Get handler source
            handler = self.dispatcher._tool_handlers.get(tool_name)
            if not handler:
                continue  # covered by test_all_schema_tools_have_handlers

            try:
                source = inspect.getsource(handler)
            except (OSError, TypeError):
                continue

            # Collect actions referenced in handler source:
            # - action == 'xxx' / action == "xxx"
            # - 'xxx': 'yyy' in ACTION_ALIASES dicts
            handled = set()

            # Direct comparisons: action == 'xxx'
            for m in re.finditer(r"""action\s*==\s*['"](\w+)['"]""", source):
                handled.add(m.group(1))

            # in-set checks: action in ('xxx', 'yyy') or action not in (...)
            for m in re.finditer(r"""action\s+(?:not\s+)?in\s+\(([^)]+)\)""", source):
                for inner in re.finditer(r"""['"](\w+)['"]""", m.group(1)):
                    handled.add(inner.group(1))

            # ACTION_ALIASES keys (aliased actions also count as handled)
            for m in re.finditer(r"""['"](\w+)['"]\s*:\s*['"](\w+)['"]""", source):
                handled.add(m.group(1))   # the alias key
                handled.add(m.group(2))   # the target action

            # Check coverage
            unhandled = set(action_enum) - handled
            if unhandled:
                drift[tool_name] = sorted(unhandled)

        self.assertEqual(
            drift, {},
            f"Schema actions not handled by dispatcher:\n"
            + "\n".join(f"  {tool}: {actions}" for tool, actions in sorted(drift.items()))
        )

    # ── 3. run_agent agent_name enums must all be registered ───────────────

    def test_run_agent_names_registered(self):
        """Every agent_name in the run_agent schema must be a registered
        tool handler (since _handle_agent_tool is registered per agent name)."""
        run_agent_schema = self.schema_map.get('run_agent')
        if not run_agent_schema:
            self.skipTest("run_agent schema not found")

        props = run_agent_schema.get('parameters', {}).get('properties', {})
        agent_names = props.get('agent_name', {}).get('enum', [])

        missing = []
        for name in agent_names:
            if name not in self.dispatcher._tool_handlers:
                missing.append(name)

        self.assertEqual(
            missing, [],
            f"run_agent agent_name enums with no handler: {missing}"
        )
