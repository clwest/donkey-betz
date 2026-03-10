#!/usr/bin/env python3
"""
Fix circular imports in ops_autopilot package by:
1. Removing all top-level cross-module imports from individual modules
2. Adding lazy imports inside methods that reference classes from other modules
"""

import re
from pathlib import Path

PKG = Path("core/services/ops_autopilot")

# Build class→module mapping
GROUPS = {
    "core": ["AutopilotConfig", "OpsAutopilot"],
    "verification": ["ActionVerifier", "VerifiableAction"],
    "remediation": ["RemediationEngine", "TimeoutRemediationPlaybook", "DeliberationRemediationPlaybook"],
    "governance": ["BacklogGovernor", "PolicyOptimizer", "PolicyArbitrator", "ReleaseGovernor", "GovernanceEngine"],
    "budget": ["BudgetController", "ROIEnforcer", "BudgetAwareScheduler"],
    "impact": ["ImpactCollector", "PortfolioAllocator", "GoalAwareAllocator", "MultiTouchAttributor", "AttributionDebtController"],
    "experiment": ["ExperimentEngine"],
    "revenue": ["RevenuePipelineAutomator", "OutboundLeadEngine", "OutreachSequencer", "CloseTheDealEngine", "RevenueOrchestrator", "ClosePackAutonomyEngine"],
    "engagement": ["EngagementEngine", "MeetingEngine", "EngagementAutonomyEngine"],
    "intelligence": ["KnowledgeEngine", "GrowthEngine", "CapacityEngine", "SecurityEngine", "ComplianceEngine", "DataIntegrityEngine", "ValueRealizationEngine"],
}

CLASS_TO_MODULE = {}
for mod, classes in GROUPS.items():
    for cls in classes:
        CLASS_TO_MODULE[cls] = mod

ALL_CLASS_NAMES = set(CLASS_TO_MODULE.keys())


def fix_module(mod_name: str):
    mod_path = PKG / f"{mod_name}.py"
    content = mod_path.read_text()
    lines = content.split("\n")

    # Step 1: Remove cross-module import lines
    new_lines = []
    for line in lines:
        if re.match(r'^from core\.services\.ops_autopilot\.\w+ import', line):
            continue  # drop cross-module imports
        new_lines.append(line)

    # Step 2: Find method bodies that reference classes from other modules
    # For each method, find which external classes are referenced, add lazy import
    own_classes = set(GROUPS[mod_name])
    external_classes = ALL_CLASS_NAMES - own_classes

    result_lines = []
    i = 0
    while i < len(new_lines):
        line = new_lines[i]

        # Detect method definitions (def xxx(self, ...):)
        method_match = re.match(r'^(\s+)def (\w+)\(', line)
        if method_match:
            indent = method_match.group(1)
            method_indent = len(indent)

            # Collect the full method body
            method_start = i
            result_lines.append(line)
            i += 1

            # Find method body lines and what external classes they reference
            needed_imports = {}  # module -> set of class names
            body_start = None

            while i < len(new_lines):
                bline = new_lines[i]
                stripped = bline.strip()

                # End of method: line at same or lesser indent (non-empty, non-comment)
                if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    line_indent = len(bline) - len(bline.lstrip())
                    if line_indent <= method_indent and not stripped.startswith('@'):
                        break

                # Track first non-docstring body line for import insertion
                if body_start is None and stripped and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    # Check if this is inside a docstring
                    pass

                # Check for external class references
                for cls_name in external_classes:
                    if re.search(rf'\b{cls_name}\b', bline):
                        # Skip if it's in a comment or string (rough check)
                        code_part = bline.split('#')[0]
                        if cls_name in code_part:
                            mod = CLASS_TO_MODULE[cls_name]
                            needed_imports.setdefault(mod, set()).add(cls_name)

                result_lines.append(bline)
                i += 1

            # If this method needs external classes, insert lazy imports after def line
            if needed_imports:
                # Find where to insert (after docstring if present)
                insert_idx = method_start + 1  # right after def line
                # Check for docstring
                search_idx = insert_idx
                while search_idx < len(result_lines):
                    sline = result_lines[search_idx].strip()
                    if not sline:
                        search_idx += 1
                        continue
                    if sline.startswith('"""') or sline.startswith("'''"):
                        quote = sline[:3]
                        if sline.count(quote) >= 2 and len(sline) > 3:
                            # Single-line docstring
                            insert_idx = search_idx + 1
                        else:
                            # Multi-line docstring - find end
                            search_idx += 1
                            while search_idx < len(result_lines):
                                if quote in result_lines[search_idx]:
                                    insert_idx = search_idx + 1
                                    break
                                search_idx += 1
                            else:
                                insert_idx = search_idx
                    break

                # Build import lines
                body_indent = indent + "    "
                import_lines = []
                for mod in sorted(needed_imports):
                    names = ", ".join(sorted(needed_imports[mod]))
                    import_lines.append(
                        f"{body_indent}from core.services.ops_autopilot.{mod} import {names}"
                    )

                # Insert imports
                for j, imp_line in enumerate(import_lines):
                    result_lines.insert(insert_idx + j, imp_line)

            continue

        result_lines.append(line)
        i += 1

    mod_path.write_text("\n".join(result_lines))
    print(f"Fixed {mod_path}")


def main():
    for mod_name in GROUPS:
        fix_module(mod_name)
    print("\nDone! All cross-module imports converted to lazy imports.")


if __name__ == "__main__":
    main()
