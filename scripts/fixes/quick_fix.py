#!/usr/bin/env python3
"""
Quick fix for tsconfig/jsconfig conflict
"""

import os
from pathlib import Path

def quick_fix():
    frontend_path = Path("frontend")
    
    # Remove the conflicting tsconfig.json
    tsconfig = frontend_path / "tsconfig.json"
    if tsconfig.exists():
        os.remove(tsconfig)
        print("✅ Removed conflicting tsconfig.json")
    
    # Also remove jsconfig.json since we don't need it
    jsconfig = frontend_path / "jsconfig.json"
    if jsconfig.exists():
        os.remove(jsconfig)
        print("✅ Removed jsconfig.json")
    
    print("\n✅ Config conflict resolved!")
    print("\nNow run: make unified-dev")

if __name__ == "__main__":
    quick_fix()
