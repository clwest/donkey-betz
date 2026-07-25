"""Fault-injection selector parser (canon_v2 Item 5).

Slice YAMLs express fault-injection targets as Python attribute-access
strings — ``core.services.foo_service.FooService.bar`` (method) or
``core.services.foo_client_factory.get_client`` (module-level function).
The harness resolves these into ``(holder, attr_name, original_callable)``
tuples so runners can monkey-patch, restore, and re-invoke without
speaking dotted-path lookup at the runner level.

Canon_v2 Item 5 forbid (S2963 ratification): selectors MUST NOT be
handler-registry keys (bare PA tool names like ``orm_inspect_tool`` or
handler function names like ``handle_orm_inspect``). Handler-registry
lookup is a separate indirection layer; using its keys as selectors
couples fault injection to the wrong abstraction. The parser rejects
such selectors at load time with a specific error type so YAML authors
see the mistake in the loader, not at first ``--execute`` invocation.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any


class FaultInjectionSelectorError(ValueError):
    """Raised when a fault-injection selector cannot be resolved."""


@dataclass(frozen=True)
class ResolvedSelector:
    """Result of parsing one fault-injection selector.

    holder:
        The immediate parent object of the target attribute — either the
        module (for module-level functions) or the class (for methods).
        Consumers monkey-patch via ``setattr(holder, attr_name, patch)``
        and restore via ``setattr(holder, attr_name, original)``.

    attr_name:
        The final attribute name on ``holder`` (e.g., ``get_client`` or
        ``get_attention_items``).

    original:
        The resolved callable at parse time. Cached so callers can
        restore the original after the injection completes without
        re-importing.

    selector:
        Verbatim selector string as it appeared in the slice YAML.
        Preserved for error surfaces and audit trails.
    """

    holder: Any
    attr_name: str
    original: Any
    selector: str


def parse_selector(selector: str) -> ResolvedSelector:
    """Resolve a fault-injection selector into a :class:`ResolvedSelector`.

    Accepted shapes:

    * ``module.submodule.function`` — module-level callable.
    * ``module.submodule.ClassName.method`` — method on a class.
    * ``module.submodule.ClassName.classmethod`` — classmethod likewise.

    Rejected shapes (raise :class:`FaultInjectionSelectorError` with a
    specific reason):

    * Bare identifier ``foo_tool`` — canon_v2 Item 5 forbid: looks like a
      handler-registry key.
    * Any selector that fails to import — likely a stale module path or
      a handler-registry key masquerading as a dotted path (e.g.,
      ``pa_tools.orm_inspect``).
    * ``None`` / empty string.

    The parser is deterministic — the same selector string always
    resolves to the same ``(holder, attr_name)`` tuple (or the same
    error), which is why compilation happens at load time, not at
    runtime.
    """
    if not selector or not isinstance(selector, str):
        raise FaultInjectionSelectorError(
            f"selector must be a non-empty string; got {selector!r}"
        )

    if "." not in selector:
        raise FaultInjectionSelectorError(
            f"selector {selector!r} has no dots — this looks like a "
            "handler-registry key (canon_v2 Item 5 forbid). Use a full "
            "Python attribute-access path like "
            "'core.services.foo.Foo.bar' or "
            "'core.services.foo_factory.get_client' instead."
        )

    parts = selector.split(".")
    # Walk the longest importable prefix. Everything after the last
    # importable module is treated as attribute access on the module or
    # on its resolved objects.
    module_path_parts: list[str] = []
    module = None
    for i, part in enumerate(parts):
        candidate = ".".join(parts[: i + 1])
        try:
            module = importlib.import_module(candidate)
            module_path_parts = parts[: i + 1]
        except ImportError:
            break

    if module is None:
        raise FaultInjectionSelectorError(
            f"selector {selector!r} does not begin with an importable module; "
            "canon_v2 Item 5 requires selectors to be Python attribute-access "
            "paths, not handler-registry keys. Check the leading dotted "
            "prefix is a real module (e.g., 'core.services.foo_service')."
        )

    remaining = parts[len(module_path_parts):]
    if not remaining:
        raise FaultInjectionSelectorError(
            f"selector {selector!r} resolves to a module ({module.__name__}); "
            "fault injection needs a callable target — append the "
            "function or Class.method name."
        )

    # Walk remaining attributes from the module downward, tracking the
    # previous holder so the final ``holder + attr_name`` pair is exactly
    # what a monkey-patch call needs.
    current: Any = module
    holder: Any = module
    attr_name: str = remaining[0]
    for i, part in enumerate(remaining):
        try:
            nxt = getattr(current, part)
        except AttributeError as exc:
            resolved_so_far = (
                ".".join(module_path_parts + remaining[: i]) if i else module.__name__
            )
            raise FaultInjectionSelectorError(
                f"selector {selector!r}: attribute {part!r} not found on "
                f"{resolved_so_far!r}. Check the class or function name — a "
                "silent rename between authoring + execution is a common "
                "cause."
            ) from exc
        holder = current
        attr_name = part
        current = nxt

    if not callable(current):
        raise FaultInjectionSelectorError(
            f"selector {selector!r} resolves to a non-callable "
            f"({type(current).__name__}); fault injection targets must be "
            "functions, methods, or classmethods."
        )

    return ResolvedSelector(
        holder=holder,
        attr_name=attr_name,
        original=current,
        selector=selector,
    )


__all__ = [
    "FaultInjectionSelectorError",
    "ResolvedSelector",
    "parse_selector",
]
