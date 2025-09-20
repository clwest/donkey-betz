#!/usr/bin/env python3
"""
Diagnose why frontend isn't updating
"""

import os
import subprocess
import time
from pathlib import Path

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def check_file(filepath, description):
    """Check if a file exists and show its modification time"""
    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        print(f"{GREEN}✅ {description}{END}")
        print(f"   Path: {filepath}")
        print(f"   Modified: {time_str}")
        return True
    else:
        print(f"{RED}❌ {description} - NOT FOUND{END}")
        print(f"   Expected at: {filepath}")
        return False

def check_import(filepath, import_str, description):
    """Check if a file contains a specific import"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            if import_str in content:
                print(f"{GREEN}✅ {description}{END}")
                # Show the actual import line
                for line in content.split('\n'):
                    if import_str in line and not line.strip().startswith('//'):
                        print(f"   Found: {line.strip()}")
                        return True
        print(f"{RED}❌ {description}{END}")
        print(f"   Looking for: {import_str}")
        return False
    return False

def check_process(name):
    """Check if a process is running"""
    try:
        result = subprocess.run(['pgrep', '-f', name], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"{GREEN}✅ {name} is running (PIDs: {', '.join(pids)}){END}")
            return True
        else:
            print(f"{YELLOW}⚠️  {name} is not running{END}")
            return False
    except:
        print(f"{YELLOW}⚠️  Could not check {name} process{END}")
        return False

def main():
    print(f"\n{BOLD}{BLUE}{'='*60}{END}")
    print(f"{BOLD}{BLUE}🔍 FRONTEND UPDATE DIAGNOSTIC{END}")
    print(f"{BOLD}{BLUE}{'='*60}{END}\n")
    
    # Check component files
    print(f"{BOLD}Component Files:{END}")
    base_path = "frontend/src/components/"
    
    check_file(f"{base_path}SimpleCommandCenter.tsx", "SimpleCommandCenter (Simplified version)")
    check_file(f"{base_path}EnhancedUserCommandCenter.tsx", "EnhancedUserCommandCenter (Full version)")
    check_file(f"{base_path}UserCommandCenter.tsx", "UserCommandCenter (Original)")
    
    print(f"\n{BOLD}Page Configuration:{END}")
    page_path = "frontend/src/pages/control-center/ControlCenterPage.tsx"
    
    if check_file(page_path, "ControlCenterPage"):
        # Check which component is being imported
        check_import(page_path, "SimpleCommandCenter", "Using SimpleCommandCenter")
        check_import(page_path, "EnhancedUserCommandCenter", "Using EnhancedUserCommandCenter")
        check_import(page_path, "UserCommandCenter", "Using UserCommandCenter")
    
    print(f"\n{BOLD}Process Status:{END}")
    check_process("vite")
    check_process("daphne")
    
    print(f"\n{BOLD}Cache Directories:{END}")
    cache_dirs = [
        "frontend/node_modules/.vite",
        "frontend/.parcel-cache",
        "frontend/dist"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            print(f"{YELLOW}⚠️  Cache exists: {cache_dir}{END}")
            print(f"   Run: rm -rf {cache_dir}")
        else:
            print(f"{GREEN}✅ No cache at: {cache_dir}{END}")
    
    print(f"\n{BOLD}{BLUE}{'='*60}{END}")
    print(f"{BOLD}DIAGNOSIS SUMMARY:{END}")
    print(f"{BOLD}{BLUE}{'='*60}{END}\n")
    
    # Check the actual current setup
    if os.path.exists(page_path):
        with open(page_path, 'r') as f:
            content = f.read()
            if "SimpleCommandCenter" in content and "//" not in content.split("SimpleCommandCenter")[0].split('\n')[-1]:
                print(f"{GREEN}✅ Frontend SHOULD show SimpleCommandCenter{END}")
                print(f"\n{BOLD}If you still see the old UI:{END}")
                print(f"  1. Stop the frontend (Ctrl+C)")
                print(f"  2. Run: {YELLOW}cd frontend && rm -rf node_modules/.vite{END}")
                print(f"  3. Run: {YELLOW}npm run dev{END}")
                print(f"  4. Hard refresh browser: {YELLOW}Cmd+Shift+R (Mac) or Ctrl+Shift+R (PC){END}")
                print(f"  5. Or try incognito/private window")
            elif "EnhancedUserCommandCenter" in content:
                print(f"{BLUE}Frontend is using EnhancedUserCommandCenter{END}")
            else:
                print(f"{YELLOW}Frontend is using original UserCommandCenter{END}")
    
    print(f"\n{BOLD}Quick Fix Command:{END}")
    print(f"{YELLOW}chmod +x force-refresh-frontend.sh && ./force-refresh-frontend.sh{END}")
    print(f"\n{BOLD}{BLUE}{'='*60}{END}\n")

if __name__ == "__main__":
    main()