#!/usr/bin/env python3
"""
Extract EnhancedPersonalAIAssistant handler methods into mixin modules.
Same pattern as tool_dispatcher extraction.
"""

import re
import shutil
from pathlib import Path

SRC = Path("core/personal_ai_assistant_enhanced.py")


def main():
    with open(SRC) as f:
        lines = f.readlines()

    total_lines = len(lines)

    methods = []
    for i, line in enumerate(lines):
        m = re.match(r'^    def (\w+)\(self', line)
        if m:
            methods.append((i, m.group(1)))

    method_ranges = {}
    for idx, (start, name) in enumerate(methods):
        end = methods[idx + 1][0] if idx + 1 < len(methods) else total_lines
        method_ranges[name] = (start, end)

    # Core methods stay
    CORE_METHODS = {
        "__init__", "process_message", "get_tool_definitions",
        "_generate_ai_response", "_execute_tool_call",
        "_get_optimized_tools", "_build_spider_intelligence_section",
        "_handle_conversation_context", "_extract_tool_calls",
        "get_context_summary",
    }

    # Group by prefix
    handle_methods = [n for _, n in methods if n.startswith("_handle_") and n not in CORE_METHODS]
    tool_methods = [n for _, n in methods if n.startswith("_tool_") and n not in CORE_METHODS]
    build_methods = [n for _, n in methods if n.startswith("_build_") and n not in CORE_METHODS]
    get_methods = [n for _, n in methods if n.startswith("_get_") and n not in CORE_METHODS]
    format_methods = [n for _, n in methods if n.startswith("_format_") and n not in CORE_METHODS]

    # Remaining
    all_categorized = set(handle_methods + tool_methods + build_methods + get_methods + format_methods)
    remaining = [n for _, n in methods if n not in CORE_METHODS and n not in all_categorized]

    GROUPS = {
        "epa_handlers_tools": (
            "EPAToolHandlersMixin",
            handle_methods,
        ),
        "epa_handlers_agents": (
            "EPAAgentToolsMixin",
            tool_methods,
        ),
        "epa_handlers_utility": (
            "EPAUtilityMixin",
            build_methods + get_methods + format_methods + remaining,
        ),
    }

    # Filter out core methods and empties
    for mod, (cls, meths) in GROUPS.items():
        GROUPS[mod] = (cls, [m for m in meths if m in method_ranges])

    print(f"Core methods (stay): {len(CORE_METHODS)}")
    for mod, (cls, meths) in GROUPS.items():
        print(f"  {mod} ({cls}): {len(meths)} methods")

    # Back up
    backup = SRC.with_suffix(".py.bak")
    shutil.copy2(SRC, backup)

    # Find class definition
    class_line = None
    for i, line in enumerate(lines):
        if re.match(r'^class EnhancedPersonalAIAssistant', line):
            class_line = i
            break

    imports_block = "".join(lines[:class_line])

    methods_to_remove = set()
    for module_name, (mixin_class, method_names) in GROUPS.items():
        module_path = SRC.parent / f"{module_name}.py"

        method_blocks = []
        for mname in method_names:
            start, end = method_ranges[mname]
            block = "".join(lines[start:end])
            method_blocks.append(block)
            methods_to_remove.add(mname)

        with open(module_path, "w") as f:
            f.write(f'"""\nEnhancedPersonalAIAssistant {mixin_class} — extracted handler methods.\n"""\n\n')
            f.write(imports_block)
            f.write(f"\n\nclass {mixin_class}:\n")
            f.write(f'    """Mixin providing handler methods for EnhancedPersonalAIAssistant."""\n\n')
            for block in method_blocks:
                f.write(block)

        size_kb = module_path.stat().st_size / 1024
        print(f"  {module_path.name} ({len(method_blocks)} methods, {size_kb:.0f}KB)")

    # Rewrite main file
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
        mixin_imports.append(f"from core.{module_name} import {mixin_class}")
        mixin_bases.append(mixin_class)

    final_lines = []
    for line in new_lines:
        if re.match(r'^class EnhancedPersonalAIAssistant', line):
            final_lines.append("\n")
            for imp in mixin_imports:
                final_lines.append(imp + "\n")
            final_lines.append("\n\n")
            orig_bases_match = re.match(r'class EnhancedPersonalAIAssistant\((.+)\):', line)
            orig_bases = orig_bases_match.group(1) if orig_bases_match else ""
            all_bases = ", ".join(mixin_bases + [orig_bases]) if orig_bases else ", ".join(mixin_bases)
            final_lines.append(f"class EnhancedPersonalAIAssistant({all_bases}):\n")
            continue
        final_lines.append(line)

    with open(SRC, "w") as f:
        f.writelines(final_lines)

    size_kb = SRC.stat().st_size / 1024
    print(f"\n  personal_ai_assistant_enhanced.py (core, {size_kb:.0f}KB)")

    backup.unlink()
    print("Done!")


if __name__ == "__main__":
    main()
