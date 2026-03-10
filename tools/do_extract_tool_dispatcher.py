#!/usr/bin/env python3
"""
Extract ToolDispatcher handler methods into mixin modules.

Strategy:
  - Keep ToolDispatcher in tool_dispatcher.py with core methods
  - Extract handler methods into mixin classes in separate files
  - ToolDispatcher inherits from all mixins
"""

import re
import shutil
from pathlib import Path

SRC = Path("core/services/tool_dispatcher.py")

# Method groupings: module_name -> (mixin_class_name, [method_names])
GROUPS = {
    "td_handlers_agents": (
        "AgentHandlersMixin",
        ["_tool_to_agent_name", "_get_agent_execution_output"],
    ),
    "td_handlers_content": (
        "ContentHandlersMixin",
        ["_record_content_feedback", "_handle_content", "_handle_bulk_archive", "_handle_bulk_archive_published"],
    ),
    "td_handlers_ops": (
        "OpsHandlersMixin",
        [
            "_handle_ops", "_ops_version", "_ops_slo_status",
            "_ops_failure_signatures", "_ops_celery_task_history",
            "_ops_execution_detail", "_ops_execution_search",
            "_ops_timeout_config_read", "_ops_proof_bundle",
            "_ops_tool_migration_report", "_handle_status_snapshot",
        ],
    ),
    "td_handlers_core": (
        "CoreHandlersMixin",
        [
            "_handle_dream", "_handle_learning", "_handle_conversation",
            "_handle_remember", "_handle_work", "_handle_rag_query",
            "_handle_competitor_comparison", "_handle_workflow_run",
            "_handle_intelligence", "_handle_governance",
        ],
    ),
    "td_handlers_gateway": (
        "GatewayHandlersMixin",
        [
            "_handle_repo", "_handle_analytics", "_handle_discord",
            "_handle_mobile", "_handle_vip_invite", "_handle_cockpit",
            "_handle_narrative", "_handle_proactive", "_handle_distribution",
            "_handle_calendar", "_handle_experiment", "_handle_podcast",
            "_handle_campaign", "_handle_audit", "_handle_conceptforge",
            "_handle_profile", "_handle_self_awareness", "_handle_ats",
        ],
    ),
    "td_handlers_codejobs": (
        "CodeJobHandlersMixin",
        [
            "_handle_code_job", "_code_job_submit", "_code_job_status",
            "_code_job_logs", "_code_job_cancel", "_code_job_list",
        ],
    ),
}


def main():
    with open(SRC) as f:
        lines = f.readlines()

    total_lines = len(lines)

    # Back up original
    backup = SRC.with_suffix(".py.bak")
    shutil.copy2(SRC, backup)
    print(f"Backed up {SRC} → {backup}")

    # Find all method boundaries (def xxx(self, ...))
    methods = []
    for i, line in enumerate(lines):
        m = re.match(r'^    def (\w+)\(self', line)
        if m:
            methods.append((i, m.group(1)))

    method_ranges = {}
    for idx, (start, name) in enumerate(methods):
        end = methods[idx + 1][0] if idx + 1 < len(methods) else None
        # Find end: next method at same indent or end of class
        if end is None:
            # Find end of class (next top-level definition or EOF)
            end = total_lines
            for j in range(start + 1, total_lines):
                if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('#'):
                    end = j
                    break
        method_ranges[name] = (start, end)

    # Verify all grouped methods exist
    all_grouped = set()
    for _, (_, method_names) in GROUPS.items():
        all_grouped.update(method_names)

    missing = all_grouped - set(method_ranges.keys())
    if missing:
        print(f"ERROR: Methods in groups but not in file: {missing}")
        return

    # Find the module-level imports block (everything before class ToolDispatcher)
    class_line = None
    for i, line in enumerate(lines):
        if line.startswith("class ToolDispatcher"):
            class_line = i
            break

    imports_block = "".join(lines[:class_line])

    # Extract grouped methods and write mixin modules
    methods_to_remove = set()
    for module_name, (mixin_class, method_names) in GROUPS.items():
        module_path = SRC.parent / f"{module_name}.py"

        # Collect method code
        method_blocks = []
        for mname in method_names:
            start, end = method_ranges[mname]
            block = "".join(lines[start:end])
            method_blocks.append(block)
            methods_to_remove.add(mname)

        # Write mixin module
        with open(module_path, "w") as f:
            f.write(f'"""\n')
            f.write(f"ToolDispatcher {mixin_class} — extracted handler methods.\n")
            f.write(f'"""\n\n')
            f.write(imports_block)
            f.write(f"\n\nclass {mixin_class}:\n")
            f.write(f'    """Mixin providing handler methods for ToolDispatcher."""\n\n')
            for block in method_blocks:
                f.write(block)

        size_kb = module_path.stat().st_size / 1024
        print(f"  {module_path.name} ({mixin_class}, {len(method_names)} methods, {size_kb:.0f}KB)")

    # Rewrite tool_dispatcher.py:
    # - Remove extracted methods
    # - Add mixin imports
    # - Change class definition to inherit from mixins

    # Build new lines, skipping extracted methods
    new_lines = []
    skip_until = None
    for i, line in enumerate(lines):
        if skip_until is not None:
            if i >= skip_until:
                skip_until = None
            else:
                continue

        # Check if this line starts an extracted method
        m = re.match(r'^    def (\w+)\(self', line)
        if m and m.group(1) in methods_to_remove:
            start, end = method_ranges[m.group(1)]
            skip_until = end
            continue

        new_lines.append(line)

    # Add mixin imports before class definition
    mixin_imports = []
    mixin_bases = []
    for module_name, (mixin_class, _) in GROUPS.items():
        mixin_imports.append(
            f"from core.services.{module_name} import {mixin_class}"
        )
        mixin_bases.append(mixin_class)

    # Find and modify the class definition line
    final_lines = []
    for line in new_lines:
        if line.startswith("class ToolDispatcher"):
            # Insert mixin imports before class
            final_lines.append("\n")
            for imp in mixin_imports:
                final_lines.append(imp + "\n")
            final_lines.append("\n\n")
            # Modify class definition
            bases = ", ".join(mixin_bases)
            final_lines.append(f"class ToolDispatcher({bases}):\n")
            continue
        final_lines.append(line)

    with open(SRC, "w") as f:
        f.writelines(final_lines)

    size_kb = SRC.stat().st_size / 1024
    print(f"\n  tool_dispatcher.py (core, {size_kb:.0f}KB)")
    print(f"\nBackup at {backup}")
    print(f"Done! Extracted {len(methods_to_remove)} methods into {len(GROUPS)} mixin modules.")


if __name__ == "__main__":
    main()
