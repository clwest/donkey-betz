#!/usr/bin/env python3
"""
Extract views_image.py (631KB, 113 functions) into domain modules.

Strategy: Split top-level view functions by route group, keep a thin
re-export shim so url patterns don't break.
"""

import re
import shutil
from pathlib import Path

SRC = Path("core/views_image.py")


def find_function_ranges(lines):
    """Find all top-level function ranges (including their decorators).

    Returns dict of name -> (start_line, end_line) where start includes
    decorators and end is the line AFTER the last line of the function body.
    """
    total = len(lines)

    # Step 1: Find all 'def name(' at indent level 0
    func_defs = []  # (line_idx, name)
    for i, line in enumerate(lines):
        m = re.match(r'^def (\w+)\(', line)
        if m:
            func_defs.append((i, m.group(1)))

    # Step 2: For each function, find start (including decorators) and end
    ranges = {}
    for idx, (def_line, name) in enumerate(func_defs):
        # Start: walk backwards to find decorators
        start = def_line
        j = def_line - 1
        while j >= 0:
            stripped = lines[j].strip()
            if stripped.startswith('@') or stripped == '':
                if stripped.startswith('@'):
                    start = j
                j -= 1
            else:
                break

        # End: find the next top-level definition (def/class at indent 0)
        # or end of file
        end = total
        for j in range(def_line + 1, total):
            line = lines[j]
            if line and not line[0].isspace() and not line.startswith('#') and line.strip():
                # Top-level non-empty, non-comment line
                if re.match(r'^(def |class |@)', line):
                    end = j
                    # But back up past blank lines before this next def
                    while end > def_line + 1 and lines[end - 1].strip() == '':
                        end -= 1
                    break

        ranges[name] = (start, end)

    return ranges


def main():
    with open(SRC) as f:
        lines = f.readlines()

    total_lines = len(lines)
    func_ranges = find_function_ranges(lines)

    print(f"Found {len(func_ranges)} functions in {total_lines} lines")

    # Find the imports section (everything before the first function/decorator)
    first_start = min(start for start, _ in func_ranges.values())
    imports_block = "".join(lines[:first_start])

    # Make sure csrf_exempt is in the imports
    if 'csrf_exempt' not in imports_block:
        imports_block += "from django.views.decorators.csrf import csrf_exempt\n"

    # Group functions by domain
    all_func_names = set(func_ranges.keys())

    GROUPS = {}

    # Gallery/generation views
    generate_funcs = [n for n in all_func_names if 'generate' in n.lower() and not n.startswith('_')]
    GROUPS["views_image_generate"] = sorted(generate_funcs)

    # Edit/transform views
    edit_funcs = [n for n in all_func_names if any(k in n.lower() for k in ['upscale', 'remove_background', 'adjust', 'crop', 'enhance', 'style_transfer', 'resize', 'color', 'filter'])]
    GROUPS["views_image_edit"] = sorted(edit_funcs)

    # Workflow views
    workflow_funcs = [n for n in all_func_names if 'workflow' in n.lower()]
    GROUPS["views_image_workflow"] = sorted(workflow_funcs)

    # Gallery/browse views
    gallery_funcs = [n for n in all_func_names if any(k in n.lower() for k in ['gallery', 'batch', 'download'])]
    GROUPS["views_image_gallery"] = sorted(gallery_funcs)

    # Portfolio views
    portfolio_funcs = [n for n in all_func_names if 'portfolio' in n.lower()]
    GROUPS["views_image_portfolio"] = sorted(portfolio_funcs)

    # Tool/assistant views
    tool_funcs = [n for n in all_func_names if any(k in n.lower() for k in ['execute_tool', 'assistant', 'chat'])]
    GROUPS["views_image_tools"] = sorted(tool_funcs)

    # Collect what's been grouped
    grouped = set()
    for names in GROUPS.values():
        grouped.update(names)

    # Private helpers
    helpers = sorted([n for n in all_func_names if n.startswith('_') and n not in grouped])
    GROUPS["views_image_helpers"] = helpers
    grouped.update(helpers)

    # Everything else
    misc = sorted([n for n in all_func_names if n not in grouped])
    GROUPS["views_image_misc"] = misc

    # Print groupings
    for mod, names in GROUPS.items():
        print(f"  {mod}: {len(names)} functions")

    # Backup
    backup = SRC.with_suffix(".py.bak")
    shutil.copy2(SRC, backup)

    # Write domain modules
    for module_name, func_names in GROUPS.items():
        if not func_names:
            continue

        module_path = SRC.parent / f"{module_name}.py"

        with open(module_path, "w") as f:
            f.write(f'"""\nImage views — {module_name.replace("views_image_", "")} functions.\n"""\n\n')
            f.write(imports_block)
            f.write("\n")

            for fname in func_names:
                start, end = func_ranges[fname]
                f.write("\n")
                f.write("".join(lines[start:end]))
                f.write("\n")

        size_kb = module_path.stat().st_size / 1024
        print(f"    -> {module_path.name} ({len(func_names)} functions, {size_kb:.0f}KB)")

    # Syntax check all modules
    import py_compile
    all_ok = True
    for module_name, func_names in GROUPS.items():
        if not func_names:
            continue
        module_path = SRC.parent / f"{module_name}.py"
        try:
            py_compile.compile(str(module_path), doraise=True)
        except py_compile.PyCompileError as e:
            print(f"    SYNTAX ERROR in {module_path.name}: {e}")
            all_ok = False

    if not all_ok:
        print("\nSyntax errors found! Restoring backup...")
        shutil.copy2(backup, SRC)
        backup.unlink()
        # Remove broken modules
        for module_name in GROUPS:
            p = SRC.parent / f"{module_name}.py"
            if p.exists():
                p.unlink()
        return

    # Write re-export shim
    shim_lines = [
        '"""',
        'Image views — re-export shim for backwards compatibility.',
        '',
        'All functions have been extracted to views_image_*.py modules.',
        '"""',
        '',
    ]

    all_exports = []
    for module_name, func_names in GROUPS.items():
        if not func_names:
            continue
        if len(func_names) > 3:
            shim_lines.append(f"from core.{module_name} import (  # noqa: F401")
            for n in func_names:
                shim_lines.append(f"    {n},")
            shim_lines.append(")")
        else:
            names_str = ", ".join(func_names)
            shim_lines.append(f"from core.{module_name} import {names_str}  # noqa: F401")
        all_exports.extend(func_names)

    shim_lines.append("")
    shim_lines.append("__all__ = [")
    for n in all_exports:
        shim_lines.append(f'    "{n}",')
    shim_lines.append("]")
    shim_lines.append("")

    with open(SRC, "w") as f:
        f.write("\n".join(shim_lines))

    size_kb = SRC.stat().st_size / 1024
    print(f"\n  views_image.py (shim, {size_kb:.0f}KB)")

    backup.unlink()
    print("Done!")


if __name__ == "__main__":
    main()
