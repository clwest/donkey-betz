"""
Session 2846: Handler/Schema Drift Lint for the PA Tool Surface.

Compares each `PA_TOOL_SCHEMAS` entry against its registered handler in
`ToolDispatcher` and reports drift:

    HANDLER_ONLY_PARAM   handler reads a payload key the schema doesn't advertise
                         (S2844 misdiagnosis class — signal_clusters handler read
                          `source_spider` while schema restricted `source` to an enum)
    SCHEMA_ONLY_PARAM    schema advertises a param the handler never reads
    HANDLER_ONLY_ACTION  handler branches on an action the schema enum lacks
    SCHEMA_ONLY_ACTION   schema enum lists an action the handler has no branch for
    MISSING_HANDLER      schema exists but no handler registered under that name

Usage:
    python manage.py check_pa_tool_drift              # human-readable report
    python manage.py check_pa_tool_drift --tool <name>  # single tool
    python manage.py check_pa_tool_drift --json       # machine-readable
    python manage.py check_pa_tool_drift --strict     # exit 1 on any drift
    python manage.py check_pa_tool_drift --verbose    # include CLEAN tools

Static analysis only. Reads `payload.get(...)`, `payload[...]`, `payload.pop(...)`
inside each handler and `action == "X"` / `action in (...)` / `action in NAME_MAP`
branches. Does not chase helpers or aliases (`sp = dict(payload); sp[...]`) — see
LIMITATIONS at the bottom of this module.
"""

from __future__ import annotations

import ast
import inspect
import json
import sys
import textwrap
from typing import Any, Dict, List, Optional, Set

from django.core.management.base import BaseCommand

_PAYLOAD_ALIASES = ("payload", "arguments", "args")


class _PayloadReadVisitor(ast.NodeVisitor):
    """Collect string literals used as keys on payload-like variables."""

    def __init__(self, aliases=_PAYLOAD_ALIASES):
        self.aliases = aliases
        self.params_read: Set[str] = set()

    def _maybe_add(self, key_node):
        if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
            self.params_read.add(key_node.value)

    def _unwrap(self, expr: ast.AST) -> ast.AST:
        """
        Peel off common defensive wrappers used by handlers to safely
        access payload — `payload or {}`, `payload if X else {}`,
        and parenthesized combinations. Returns the innermost expr.
        """
        # (X or Y) → X   — matches the `payload or {}` idiom used by
        # several handlers (e.g. active_repo_tool at td_handlers_core.py:108).
        if isinstance(expr, ast.BoolOp) and isinstance(expr.op, ast.Or):
            return self._unwrap(expr.values[0])
        # (X if cond else Y) → X
        if isinstance(expr, ast.IfExp):
            return self._unwrap(expr.body)
        return expr

    def _refers_to_payload(self, expr: ast.AST) -> bool:
        """True if `expr` (after unwrapping defensive idioms) is a payload alias."""
        unwrapped = self._unwrap(expr)
        return isinstance(unwrapped, ast.Name) and unwrapped.id in self.aliases

    def visit_Call(self, node):
        # payload.get("X"[, default])  |  payload.pop("X"[, default])
        # payload.setdefault("X", default)
        # Also handles (payload or {}).get(...), a defensive idiom used
        # by several handlers where the wrapper is a BoolOp / IfExp.
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in ("get", "pop", "setdefault")
            and node.args
            and self._refers_to_payload(node.func.value)
        ):
            self._maybe_add(node.args[0])
        self.generic_visit(node)

    def visit_Subscript(self, node):
        # payload["X"] — Py 3.9+ exposes the constant directly on `slice`.
        # Also handles (payload or {})["X"] for the same idiom.
        if self._refers_to_payload(node.value):
            self._maybe_add(node.slice)
        self.generic_visit(node)


class _ActionDispatchVisitor(ast.NodeVisitor):
    """Collect string literals used to branch on `action`."""

    def __init__(self):
        self.actions_dispatched: Set[str] = set()
        # dict-name -> set of string keys (for `if action in SOME_MAP:`)
        self.dict_literal_keys: Dict[str, Set[str]] = {}
        # names appearing in `action in NAME`
        self.dict_names_used_for_dispatch: Set[str] = set()

    def visit_Assign(self, node):
        # Capture dict literals assigned to a Name so we can resolve
        # `action in NAME` later without a full symbol table.
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Dict)
        ):
            keys: Set[str] = set()
            for k in node.value.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.add(k.value)
            if keys:
                self.dict_literal_keys.setdefault(
                    node.targets[0].id, set()
                ).update(keys)
        self.generic_visit(node)

    def visit_Compare(self, node):
        # action == "X"
        if (
            isinstance(node.left, ast.Name)
            and node.left.id == "action"
            and node.ops
            and isinstance(node.ops[0], ast.Eq)
            and node.comparators
            and isinstance(node.comparators[0], ast.Constant)
            and isinstance(node.comparators[0].value, str)
        ):
            self.actions_dispatched.add(node.comparators[0].value)

        # action in ("X", "Y") / action in ["X", ...] / action in {"X", ...}
        if (
            isinstance(node.left, ast.Name)
            and node.left.id == "action"
            and node.ops
            and isinstance(node.ops[0], ast.In)
            and node.comparators
        ):
            rhs = node.comparators[0]
            if isinstance(rhs, (ast.Tuple, ast.List, ast.Set)):
                for elt in rhs.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        self.actions_dispatched.add(elt.value)
            elif isinstance(rhs, ast.Name):
                self.dict_names_used_for_dispatch.add(rhs.id)
            elif isinstance(rhs, ast.Dict):
                # inline dict literal used directly in `in`
                for k in rhs.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        self.actions_dispatched.add(k.value)
        self.generic_visit(node)

    def resolve(self) -> Set[str]:
        actions = set(self.actions_dispatched)
        for name in self.dict_names_used_for_dispatch:
            if name in self.dict_literal_keys:
                actions |= self.dict_literal_keys[name]
        return actions


def _extract_schema_info(schemas: List[dict]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for entry in schemas:
        name = entry.get("name")
        if not name:
            continue
        params = entry.get("parameters", {}) or {}
        props = params.get("properties", {}) or {}
        action_enum: Set[str] = set()
        if "action" in props:
            enum = props["action"].get("enum") or []
            action_enum = {a for a in enum if isinstance(a, str)}
        out[name] = {
            "params": set(props.keys()) - {"action"},
            "actions": action_enum,
            "has_action_param": "action" in props,
        }
    return out


def _extract_handler_info(handler_fn) -> dict:
    try:
        src = inspect.getsource(handler_fn)
    except (TypeError, OSError):
        return {
            "params_read": set(),
            "actions_dispatched": set(),
            "source_available": False,
        }
    src = textwrap.dedent(src)
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {
            "params_read": set(),
            "actions_dispatched": set(),
            "source_available": False,
        }

    payload_visitor = _PayloadReadVisitor()
    action_visitor = _ActionDispatchVisitor()
    payload_visitor.visit(tree)
    action_visitor.visit(tree)
    return {
        "params_read": payload_visitor.params_read,
        "actions_dispatched": action_visitor.resolve(),
        "source_available": True,
    }


def _lint(schema_info, handlers, tool_filter: Optional[str] = None):
    results = []
    for name, sinfo in sorted(schema_info.items()):
        if tool_filter and name != tool_filter:
            continue
        handler = handlers.get(name)
        if handler is None:
            results.append(
                {
                    "tool": name,
                    "status": "MISSING_HANDLER",
                    "handler_only_params": [],
                    "schema_only_params": [],
                    "handler_only_actions": [],
                    "schema_only_actions": [],
                }
            )
            continue
        hinfo = _extract_handler_info(handler)
        if not hinfo["source_available"]:
            results.append(
                {
                    "tool": name,
                    "status": "SOURCE_UNAVAILABLE",
                    "handler_only_params": [],
                    "schema_only_params": [],
                    "handler_only_actions": [],
                    "schema_only_actions": [],
                }
            )
            continue

        handler_only_params = sorted(
            hinfo["params_read"] - sinfo["params"] - {"action"}
        )
        schema_only_params = sorted(sinfo["params"] - hinfo["params_read"])
        if sinfo["has_action_param"]:
            handler_only_actions = sorted(
                hinfo["actions_dispatched"] - sinfo["actions"]
            )
            schema_only_actions = sorted(
                sinfo["actions"] - hinfo["actions_dispatched"]
            )
        else:
            handler_only_actions = []
            schema_only_actions = []

        drift = bool(
            handler_only_params
            or schema_only_params
            or handler_only_actions
            or schema_only_actions
        )
        results.append(
            {
                "tool": name,
                "status": "DRIFT" if drift else "CLEAN",
                "handler_only_params": handler_only_params,
                "schema_only_params": schema_only_params,
                "handler_only_actions": handler_only_actions,
                "schema_only_actions": schema_only_actions,
            }
        )
    return results


class Command(BaseCommand):
    help = (
        "Lint PA tool schemas against handler implementations for drift "
        "(the S2844 misdiagnosis class of bug)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--tool", type=str, help="Lint a single tool by name"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Machine-readable JSON output",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit 1 if any drift or MISSING_HANDLER is found",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Include CLEAN tools in the report",
        )

    def handle(self, *args, **opts):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        from core.services.tool_dispatcher import get_tool_dispatcher

        schema_info = _extract_schema_info(PA_TOOL_SCHEMAS)
        dispatcher = get_tool_dispatcher()
        handlers = getattr(dispatcher, "_tool_handlers", {})

        results = _lint(schema_info, handlers, tool_filter=opts.get("tool"))

        if opts.get("json"):
            self.stdout.write(json.dumps(results, indent=2))
        else:
            self._print_human(results, verbose=opts.get("verbose", False))

        any_drift = any(r["status"] == "DRIFT" for r in results)
        any_missing = any(
            r["status"] in ("MISSING_HANDLER", "SOURCE_UNAVAILABLE")
            for r in results
        )
        if opts.get("strict") and (any_drift or any_missing):
            sys.exit(1)

    def _print_human(self, results, verbose: bool = False):
        buckets = {"DRIFT": [], "CLEAN": [], "MISSING_HANDLER": [], "SOURCE_UNAVAILABLE": []}
        for r in results:
            buckets[r["status"]].append(r)

        self.stdout.write(
            f"PA Tool Drift Lint — {len(results)} tool schemas scanned"
        )
        self.stdout.write(
            "  DRIFT: {d} · CLEAN: {c} · MISSING_HANDLER: {m} · SOURCE_UNAVAILABLE: {s}".format(
                d=len(buckets["DRIFT"]),
                c=len(buckets["CLEAN"]),
                m=len(buckets["MISSING_HANDLER"]),
                s=len(buckets["SOURCE_UNAVAILABLE"]),
            )
        )
        self.stdout.write("")

        for r in buckets["DRIFT"]:
            self.stdout.write(f"[DRIFT] {r['tool']}")
            if r["handler_only_params"]:
                self.stdout.write(
                    f"    handler reads (schema missing): "
                    f"{r['handler_only_params']}"
                )
            if r["schema_only_params"]:
                self.stdout.write(
                    f"    schema declares (handler ignores): "
                    f"{r['schema_only_params']}"
                )
            if r["handler_only_actions"]:
                self.stdout.write(
                    f"    handler dispatches (enum missing): "
                    f"{r['handler_only_actions']}"
                )
            if r["schema_only_actions"]:
                self.stdout.write(
                    f"    enum declares (handler ignores): "
                    f"{r['schema_only_actions']}"
                )
            self.stdout.write("")

        for r in buckets["MISSING_HANDLER"]:
            self.stdout.write(
                f"[MISSING_HANDLER] {r['tool']} — schema present, no handler registered"
            )
        for r in buckets["SOURCE_UNAVAILABLE"]:
            self.stdout.write(
                f"[SOURCE_UNAVAILABLE] {r['tool']} — handler source could not be read"
            )

        if verbose:
            for r in buckets["CLEAN"]:
                self.stdout.write(f"[CLEAN] {r['tool']}")


# LIMITATIONS
# -----------
# The static analysis is deliberately shallow — enough to catch the S2844 class
# of bug (schema advertises less than the handler reads) without a full symbol
# table.
#
# Known false positives / false negatives:
#   * Handlers that alias payload via `sp = dict(payload); sp[...] = ...` and
#     then re-dispatch to another handler will not have their inner reads
#     attributed to the outer handler (false negative on outer handler).
#   * Handlers that read nested keys (`payload.get('filters', {}).get('X')`)
#     attribute only the outer key to the handler; the inner keys are invisible.
#     Acceptable, since the outer key is what the schema declares.
#   * Params/actions read via non-literal string variables are invisible.
#   * `schema_only_params` may include params exposed for callers other than the
#     PA (e.g., internal Celery consumers). Review each flagged tool before
#     treating this as a bug.
