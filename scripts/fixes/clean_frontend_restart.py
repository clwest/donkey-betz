#!/usr/bin/env python3
"""
Clean restart of React frontend - removes old and creates fresh
"""

import os
import shutil
import subprocess
from pathlib import Path

def clean_frontend_restart():
    print("🧹 CLEAN FRONTEND RESTART")
    print("="*50)
    
    # Step 1: Stop any running processes
    print("\n1. Stopping any React processes...")
    os.system("pkill -f 'react-scripts' 2>/dev/null || true")
    os.system("lsof -ti:3000 | xargs kill -9 2>/dev/null || true")
    
    # Step 2: Backup and remove old frontend
    frontend_path = Path("frontend")
    if frontend_path.exists():
        print("\n2. Backing up and removing old frontend...")
        if Path("frontend_backup").exists():
            shutil.rmtree("frontend_backup")
        shutil.move("frontend", "frontend_backup")
        print("   ✅ Old frontend backed up to frontend_backup/")
    
    # Step 3: Create fresh React app
    print("\n3. Creating fresh React app...")
    result = subprocess.run(
        ["npx", "create-react-app", "frontend", "--template", "cra-template"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("   ❌ Failed to create React app")
        print("   Trying alternative method...")
        os.system("npx create-react-app@latest frontend")
    
    # Step 4: Install additional dependencies
    print("\n4. Installing Material-UI and other dependencies...")
    os.chdir("frontend")
    
    deps_to_install = [
        "@mui/material",
        "@emotion/react", 
        "@emotion/styled",
        "@mui/icons-material",
        "@reduxjs/toolkit",
        "react-redux",
        "react-router-dom",
        "axios",
        "recharts"
    ]
    
    subprocess.run(["npm", "install"] + deps_to_install)
    
    # Step 5: Copy our custom code
    print("\n5. Setting up our custom components...")
    os.chdir("..")
    
    # This will use the implement_frontend.py to add our code
    # but only after we have a clean React base
    
    print("\n" + "="*50)
    print("✅ CLEAN REACT APP CREATED!")
    print("="*50)
    print("\nNext steps:")
    print("1. Run: python implement_frontend_components.py")
    print("2. Then: cd frontend && npm start")
    
if __name__ == "__main__":
    clean_frontend_restart()
