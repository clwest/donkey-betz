#!/usr/bin/env python
"""
Run Handoff Diagnostic with Django Context
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now run the diagnostic
from intelligence.handoff_diagnostic import HandoffDiagnostic

if __name__ == "__main__":
    diagnostic = HandoffDiagnostic()
    results = diagnostic.run_diagnostic()

    # Generate fix plan
    fixes = diagnostic.generate_fix_plan()
    if fixes:
        print("\n" + "="*40)
        print("🔧 FIX PLAN")
        print("="*40)
        for i, fix in enumerate(fixes, 1):
            print(f"\n{i}. [{fix['priority'].upper()}] {fix['source']} → {fix['destination']}")
            print(f"   Fix: {fix['suggested_fix']}")
            if 'error' in fix:
                print(f"   Error: {fix['error']}")

    # Save results
    import json
    with open('handoff_diagnostic_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n📄 Report saved to handoff_diagnostic_report.json")