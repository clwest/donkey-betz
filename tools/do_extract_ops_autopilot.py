#!/usr/bin/env python3
"""
Extract ops_autopilot.py (565KB, 37 classes) into a package with domain modules.

Strategy:
  1. Read the monolith
  2. Group 37 classes into ~8 domain modules
  3. Write each module with shared imports + its classes
  4. Replace ops_autopilot.py with a package __init__.py that re-exports everything
"""

import re
import shutil
from pathlib import Path

SRC = Path("core/services/ops_autopilot.py")
PKG = Path("core/services/ops_autopilot")

# ── Domain groupings ────────────────────────────────────────────────────────

GROUPS = {
    "core": [
        "AutopilotConfig",
        "OpsAutopilot",
    ],
    "verification": [
        "ActionVerifier",
        "VerifiableAction",
    ],
    "remediation": [
        "RemediationEngine",
        "TimeoutRemediationPlaybook",
        "DeliberationRemediationPlaybook",
    ],
    "governance": [
        "BacklogGovernor",
        "PolicyOptimizer",
        "PolicyArbitrator",
        "ReleaseGovernor",
        "GovernanceEngine",
    ],
    "budget": [
        "BudgetController",
        "ROIEnforcer",
        "BudgetAwareScheduler",
    ],
    "impact": [
        "ImpactCollector",
        "PortfolioAllocator",
        "GoalAwareAllocator",
        "MultiTouchAttributor",
        "AttributionDebtController",
    ],
    "experiment": [
        "ExperimentEngine",
    ],
    "revenue": [
        "RevenuePipelineAutomator",
        "OutboundLeadEngine",
        "OutreachSequencer",
        "CloseTheDealEngine",
        "RevenueOrchestrator",
        "ClosePackAutonomyEngine",
    ],
    "engagement": [
        "EngagementEngine",
        "MeetingEngine",
        "EngagementAutonomyEngine",
    ],
    "intelligence": [
        "KnowledgeEngine",
        "GrowthEngine",
        "CapacityEngine",
        "SecurityEngine",
        "ComplianceEngine",
        "DataIntegrityEngine",
        "ValueRealizationEngine",
    ],
}


def main():
    with open(SRC) as f:
        lines = f.readlines()

    total_lines = len(lines)

    # ── Find all class boundaries ───────────────────────────────────────────
    classes = []
    for i, line in enumerate(lines):
        m = re.match(r'^class (\w+)', line)
        if m:
            classes.append((i, m.group(1)))

    class_ranges = {}
    for idx, (start, name) in enumerate(classes):
        end = classes[idx + 1][0] if idx + 1 < len(classes) else total_lines
        class_ranges[name] = (start, end)

    # Verify all grouped classes exist
    all_grouped = set()
    for names in GROUPS.values():
        all_grouped.update(names)
    all_found = set(class_ranges.keys())
    missing = all_grouped - all_found
    extra = all_found - all_grouped
    if missing:
        print(f"ERROR: Classes in groups but not in file: {missing}")
        return
    if extra:
        print(f"WARNING: Classes in file but not in any group: {extra}")

    # ── Extract module-level preamble (imports, constants before first class) ──
    first_class_line = classes[0][0]
    preamble = "".join(lines[:first_class_line])

    # ── Identify cross-class references ─────────────────────────────────────
    # Some classes reference others (e.g., OpsAutopilot references AutopilotConfig)
    # We'll add intra-package imports where needed

    # Build class→module mapping
    class_to_module = {}
    for module_name, class_names in GROUPS.items():
        for cn in class_names:
            class_to_module[cn] = module_name

    # ── Create package directory ────────────────────────────────────────────
    # Back up original
    backup = SRC.with_suffix(".py.bak")
    shutil.copy2(SRC, backup)
    print(f"Backed up {SRC} → {backup}")

    PKG.mkdir(exist_ok=True)

    # ── Write domain modules ────────────────────────────────────────────────
    for module_name, class_names in GROUPS.items():
        module_path = PKG / f"{module_name}.py"

        # Collect code for this module's classes
        class_code_blocks = []
        for cn in class_names:
            start, end = class_ranges[cn]
            block = "".join(lines[start:end])
            class_code_blocks.append(block)

        module_code = "".join(class_code_blocks)

        # Find references to classes in OTHER modules
        cross_refs = set()
        for cn, mod in class_to_module.items():
            if mod != module_name and re.search(rf'\b{cn}\b', module_code):
                cross_refs.add((mod, cn))

        # Build cross-reference imports
        cross_imports = {}
        for mod, cn in cross_refs:
            cross_imports.setdefault(mod, []).append(cn)

        cross_import_lines = []
        for mod in sorted(cross_imports):
            names = ", ".join(sorted(cross_imports[mod]))
            cross_import_lines.append(
                f"from core.services.ops_autopilot.{mod} import {names}  # noqa: F401"
            )

        # Assemble module
        parts = [preamble]
        if cross_import_lines:
            parts.append("\n".join(cross_import_lines) + "\n\n")
        parts.append(module_code)

        with open(module_path, "w") as f:
            f.write("".join(parts))

        size_kb = module_path.stat().st_size / 1024
        print(f"  {module_path} ({len(class_names)} classes, {size_kb:.0f}KB)")

    # ── Write __init__.py ───────────────────────────────────────────────────
    init_lines = [
        '"""',
        'Ops Autopilot package — split from monolithic ops_autopilot.py.',
        '',
        'All classes are re-exported here for backwards compatibility.',
        'Consumers can continue to use:',
        '    from core.services.ops_autopilot import OpsAutopilot',
        '"""',
        '',
    ]

    all_classes = []
    for module_name, class_names in GROUPS.items():
        names_str = ", ".join(class_names)
        init_lines.append(
            f"from core.services.ops_autopilot.{module_name} import {names_str}  # noqa: F401"
        )
        all_classes.extend(class_names)

    init_lines.append("")
    init_lines.append("__all__ = [")
    for cn in all_classes:
        init_lines.append(f'    "{cn}",')
    init_lines.append("]")
    init_lines.append("")

    init_path = PKG / "__init__.py"
    with open(init_path, "w") as f:
        f.write("\n".join(init_lines))
    print(f"  {init_path} (re-exports {len(all_classes)} classes)")

    # ── Remove the old monolith (now replaced by package) ───────────────────
    SRC.unlink()
    print(f"\nRemoved {SRC} (replaced by {PKG}/)")
    print(f"Backup at {backup}")
    print(f"\nDone! {len(all_classes)} classes across {len(GROUPS)} modules.")


if __name__ == "__main__":
    main()
