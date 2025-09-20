#!/usr/bin/env python
"""
Analyze Spider Reality vs Claims
=================================

This script analyzes the true state of the spider army:
- How many spider TYPES actually exist
- How many INSTANCES are configured
- What the reality is vs the claims
"""

import os
import re
from pathlib import Path

def analyze_spiders():
    print("\n" + "="*60)
    print("🕷️ SPIDER ARMY REALITY CHECK")
    print("="*60)

    # 1. Count actual spider class implementations
    spider_dir = Path("intelligence/spiders/spider_army/spiders")
    spider_classes = []

    for file in spider_dir.glob("*.py"):
        if file.name == "__init__.py" or file.name == "base_spider.py":
            continue

        content = file.read_text()
        # Find actual spider classes (not base classes)
        matches = re.findall(r'class (\w+Spider)\([^)]+\):', content)
        for match in matches:
            if 'Base' not in match:
                spider_classes.append((file.name, match))

    print(f"\n📊 ACTUAL SPIDER IMPLEMENTATIONS:")
    print(f"Found {len(spider_classes)} actual spider classes:")
    for filename, classname in spider_classes:
        print(f"  - {classname} ({filename})")

    # 2. Check orchestrator configuration
    orchestrator_file = Path("intelligence/spiders/spider_army/orchestrator.py")
    content = orchestrator_file.read_text()

    # Find spider configurations
    configs = re.findall(r"spider_name='([^']+)'", content)
    print(f"\n📋 ORCHESTRATOR CONFIGURATIONS:")
    print(f"Found {len(configs)} spider configurations:")
    for config in configs:
        print(f"  - {config}")

    # Find spider counts
    counts = re.findall(r"spider_count=(\d+)", content)
    total_instances = sum(int(c) for c in counts)

    print(f"\n🔢 INSTANCE COUNTS:")
    print(f"Spider counts configured: {counts}")
    print(f"Total instances planned: {total_instances}")

    # 3. Check what spider classes are actually referenced
    referenced_classes = re.findall(r"spider_class='([^']+)'", content)
    unique_refs = set()
    for ref in referenced_classes:
        class_name = ref.split('.')[-1]
        unique_refs.add(class_name)

    print(f"\n🔗 REFERENCED SPIDER CLASSES:")
    print(f"Found {len(unique_refs)} unique spider classes referenced:")
    for ref in sorted(unique_refs):
        print(f"  - {ref}")

    # 4. Reality Check
    print("\n" + "="*60)
    print("🎯 REALITY CHECK SUMMARY:")
    print("="*60)

    print(f"\n1. ACTUAL IMPLEMENTATIONS: {len(spider_classes)} spider classes exist")
    print(f"2. ORCHESTRATOR CONFIGS: {len(configs)} spiders configured")
    print(f"3. TOTAL INSTANCES: {total_instances} instances (multiple instances of same spider)")
    print(f"4. UNIQUE REFERENCES: {len(unique_refs)} unique spider types referenced")

    # The reality
    print("\n⚠️ THE TRUTH:")
    print(f"- Only {len(configs)} unique spider types are configured (not 1,770)")
    print(f"- The 1,770 number is INSTANCES (multiple copies of the same {len(configs)} spiders)")
    print(f"- Each spider type runs multiple instances with different IDs")
    print(f"- Example: 500 instances of the SAME financial spider type")

    # Check if referenced spiders actually exist
    missing = []
    for ref in unique_refs:
        found = False
        for _, classname in spider_classes:
            if classname == ref:
                found = True
                break
        if not found:
            missing.append(ref)

    if missing:
        print(f"\n❌ MISSING IMPLEMENTATIONS:")
        print(f"These spiders are referenced but don't exist:")
        for m in missing:
            print(f"  - {m}")
    else:
        print(f"\n✅ All referenced spider classes have implementations")

    # Final verdict
    print("\n" + "="*60)
    print("📊 FINAL VERDICT:")
    print("="*60)
    print(f"Real spider types: {len(spider_classes)}")
    print(f"Configured to deploy: {len(configs)} types")
    print(f"Total instances: {total_instances} (multiple of same types)")
    print(f"\n💡 Reality: Not 1,770 unique spiders, but {len(configs)} types")
    print(f"   deployed {total_instances // len(configs) if len(configs) > 0 else 0} times each on average")

if __name__ == "__main__":
    analyze_spiders()