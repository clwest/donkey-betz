#!/usr/bin/env python3
"""
Extract PersonalAssistantAgent handler methods into mixin modules.
Same pattern as tool_dispatcher extraction.
"""

import re
import shutil
from pathlib import Path

SRC = Path("core/agents/personal_assistant_agent.py")

# First, let's understand the class structure
def analyze():
    with open(SRC) as f:
        lines = f.readlines()

    methods = []
    for i, line in enumerate(lines):
        m = re.match(r'^    def (\w+)\(self', line)
        if m:
            methods.append((i, m.group(1)))

    method_ranges = {}
    for idx, (start, name) in enumerate(methods):
        end = methods[idx + 1][0] if idx + 1 < len(methods) else len(lines)
        method_ranges[name] = (start, end)

    return lines, methods, method_ranges


def main():
    lines, methods, method_ranges = analyze()
    total_lines = len(lines)

    # Group methods by category
    # Core methods stay in main file
    CORE_METHODS = {
        "__init__", "router", "_detect_agent", "_check_ui_navigation",
        "process_message", "get_capabilities", "get_name",
    }

    # Group handler methods by domain
    GROUPS = {
        "pa_handlers_tools": (
            "PAToolHandlersMixin",
            [n for _, n in methods if n.startswith("_handle_") or n.startswith("_tool_")],
        ),
        "pa_handlers_manage": (
            "PAManageHandlersMixin",
            [n for _, n in methods if n.startswith("_manage_")],
        ),
        "pa_handlers_query": (
            "PAQueryHandlersMixin",
            [n for _, n in methods if n.startswith("_query_")],
        ),
        "pa_handlers_fetch": (
            "PAFetchHandlersMixin",
            [n for _, n in methods if n.startswith("_fetch_") or n.startswith("_get_") or n.startswith("_build_")],
        ),
    }

    # Verify all non-core methods are accounted for
    all_grouped = set()
    for _, (_, method_names) in GROUPS.items():
        all_grouped.update(method_names)

    all_methods = {n for _, n in methods}
    ungrouped = all_methods - CORE_METHODS - all_grouped
    if ungrouped:
        # Add ungrouped to the "tools" mixin
        print(f"Adding {len(ungrouped)} ungrouped methods to pa_handlers_tools: {sorted(ungrouped)}")
        GROUPS["pa_handlers_tools"][1].extend(sorted(ungrouped))
        all_grouped.update(ungrouped)

    print(f"Core methods (stay): {len(CORE_METHODS)}")
    for mod, (cls, meths) in GROUPS.items():
        print(f"  {mod} ({cls}): {len(meths)} methods")

    # Back up
    backup = SRC.with_suffix(".py.bak")
    shutil.copy2(SRC, backup)

    # Find class line and imports block
    class_line = None
    for i, line in enumerate(lines):
        if re.match(r'^class PersonalAssistantAgent', line):
            class_line = i
            break

    imports_block = "".join(lines[:class_line])

    methods_to_remove = set()
    for module_name, (mixin_class, method_names) in GROUPS.items():
        module_path = SRC.parent / f"{module_name}.py"

        method_blocks = []
        for mname in method_names:
            if mname not in method_ranges:
                continue
            start, end = method_ranges[mname]
            block = "".join(lines[start:end])
            method_blocks.append(block)
            methods_to_remove.add(mname)

        with open(module_path, "w") as f:
            f.write(f'"""\nPersonalAssistantAgent {mixin_class} — extracted handler methods.\n"""\n\n')
            f.write(imports_block)
            f.write(f"\n\nclass {mixin_class}:\n")
            f.write(f'    """Mixin providing handler methods for PersonalAssistantAgent."""\n\n')
            for block in method_blocks:
                f.write(block)

        size_kb = module_path.stat().st_size / 1024
        print(f"  {module_path.name} ({len(method_blocks)} methods, {size_kb:.0f}KB)")

    # Rewrite main file without extracted methods
    new_lines = []
    skip_until = None
    for i, line in enumerate(lines):
        if skip_until is not None:
            if i >= skip_until:
                skip_until = None
            else:
                continue

        m = re.match(r'^    def (\w+)\(self', line)
        if m and m.group(1) in methods_to_remove:
            start, end = method_ranges[m.group(1)]
            skip_until = end
            continue

        new_lines.append(line)

    # Add mixin imports and modify class definition
    mixin_imports = []
    mixin_bases = []
    for module_name, (mixin_class, _) in GROUPS.items():
        mixin_imports.append(f"from core.agents.{module_name} import {mixin_class}")
        mixin_bases.append(mixin_class)

    final_lines = []
    for line in new_lines:
        if re.match(r'^class PersonalAssistantAgent', line):
            # Insert mixin imports
            final_lines.append("\n")
            for imp in mixin_imports:
                final_lines.append(imp + "\n")
            final_lines.append("\n\n")
            # Parse original bases
            orig_bases_match = re.match(r'class PersonalAssistantAgent\((.+)\):', line)
            orig_bases = orig_bases_match.group(1) if orig_bases_match else ""
            all_bases = ", ".join(mixin_bases + [orig_bases]) if orig_bases else ", ".join(mixin_bases)
            final_lines.append(f"class PersonalAssistantAgent({all_bases}):\n")
            continue
        final_lines.append(line)

    with open(SRC, "w") as f:
        f.writelines(final_lines)

    size_kb = SRC.stat().st_size / 1024
    print(f"\n  personal_assistant_agent.py (core, {size_kb:.0f}KB)")

    # Clean up backup
    backup.unlink()
    print(f"Done!")


if __name__ == "__main__":
    main()
