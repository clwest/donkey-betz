#!/usr/bin/env python3
"""
verify_demo_mode.py — Check whether Resolve node demo-mode guardrails are active.

Usage:
    python resolve_node/demo_assets/verify_demo_mode.py

Exit codes:
    0 = demo mode is ON and enforced
    1 = demo mode is OFF (real footage allowed)
"""
import os
import sys
from pathlib import Path

DEMO_ASSETS_DIR = Path(__file__).parent.resolve()
RESOLVE_DIR = DEMO_ASSETS_DIR.parent

def check():
    demo_mode = os.getenv("RESOLVE_DEMO_MODE", "false").lower() == "true"
    allowed_prefixes = [
        p.strip()
        for p in os.getenv("RESOLVE_DEMO_ALLOWED_URL_PREFIXES", "").split(",")
        if p.strip()
    ]
    demo_clip = DEMO_ASSETS_DIR / "demo_test_clip.mp4"

    print(f"RESOLVE_DEMO_MODE={demo_mode}")
    print(f"Demo assets dir: {DEMO_ASSETS_DIR}")
    print(f"Demo clip exists: {demo_clip.exists()}")
    if allowed_prefixes:
        print(f"Allowed URL prefixes: {allowed_prefixes}")
    else:
        print("Allowed URL prefixes: (none — only local demo_assets/ paths allowed)")

    if demo_mode:
        print("\nStatus: DEMO MODE ACTIVE")
        print("  - Only clips inside demo_assets/ are allowed")
        print("  - Remote URLs blocked unless in RESOLVE_DEMO_ALLOWED_URL_PREFIXES")
        return 0
    else:
        print("\nStatus: DEMO MODE OFF — real footage is permitted")
        return 1

if __name__ == "__main__":
    sys.exit(check())
