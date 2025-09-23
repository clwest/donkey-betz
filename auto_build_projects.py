#!/usr/bin/env python3
"""
Automatically run the real project builder periodically to continuously create new project files
Shows the AI agents actively building REAL projects in real-time
"""

import time
import subprocess
import sys
from datetime import datetime

def run_project_builder():
    """Run the real project builder and display results"""
    try:
        print(f"\n🚀 [{datetime.now().strftime('%H:%M:%S')}] Running Project Builder...")
        print("-" * 50)

        result = subprocess.run(
            ['python', 'real_project_builder.py'],
            capture_output=True,
            text=True,
            cwd='/Users/donkeyking/development/unified-donkey-betz'
        )

        if result.stdout:
            print(result.stdout)

        if result.returncode != 0 and result.stderr:
            print(f"⚠️ Warning: {result.stderr}")

    except Exception as e:
        print(f"❌ Error running project builder: {e}")

def main():
    print("✨ Auto Project Builder Started!")
    print("📁 Building real projects every 60 seconds...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            run_project_builder()
            print(f"\n⏳ Next build in 60 seconds...")
            time.sleep(60)  # Run every minute

    except KeyboardInterrupt:
        print("\n\n🛑 Auto Builder stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()