#!/bin/bash

# Quick Storage Recovery Script for your Development Folder
# Run this to immediately free up space

echo "=========================================="
echo "🚀 QUICK STORAGE RECOVERY"
echo "=========================================="

DEV_DIR="$HOME/development"

# Step 1: Show current situation
echo -e "\n📊 Current Storage Situation:"
df -h ~ | grep -E "disk|iCloud|Users"

# Step 2: Identify the biggest culprits
echo -e "\n🔍 Analyzing your development folder..."

# The main culprits based on your scan:
echo -e "\n🎯 FOUND MAJOR SPACE HOGS:"
echo "----------------------------------------"

# Count node_modules
NODE_COUNT=$(find "$DEV_DIR" -type d -name "node_modules" 2>/dev/null | wc -l)
echo "• $NODE_COUNT node_modules folders found"

# Projects with node_modules
echo -e "\n📦 Projects with node_modules (sorted by age):"
find "$DEV_DIR" -type d -name "node_modules" -exec stat -f "%Sm %N" -t "%Y-%m-%d" {} \; 2>/dev/null | sed 's|/node_modules||' | sort | head -20

echo -e "\n=========================================="
echo "💊 QUICK FIX OPTIONS"
echo "=========================================="

echo "
Option 1: DELETE OLD PROJECT NODE_MODULES (Safest)
----------------------------------------------------
These projects look old and can have node_modules deleted:

# Old ai-content-studio modules
rm -rf '$DEV_DIR/ai-content-studio/ai-studio-premium/node_modules'
rm -rf '$DEV_DIR/ai-content-studio/ai-studio-web/node_modules'
rm -rf '$DEV_DIR/ai-content-studio/shared/node_modules'

# Old test projects
rm -rf '$DEV_DIR/apps/aidentifier/node_modules'
rm -rf '$DEV_DIR/apps/api_playground/client/node_modules'
rm -rf '$DEV_DIR/apps/game_models/.web/node_modules'
rm -rf '$DEV_DIR/apps/reflex-gpt/.web/node_modules'
rm -rf '$DEV_DIR/apps/testing-front-end/node_modules'

# Old portfolio/tutorial projects
rm -rf '$DEV_DIR/apps/Nextjs-Creative-Portfolio-Starter-Code-Files/node_modules'
rm -rf '$DEV_DIR/apps/r3f-animated-book-slider-starter/node_modules'
rm -rf '$DEV_DIR/apps/tailwind_udemy/node_modules'

Option 2: DELETE ALL REFLEX PROJECT BUILDS (Medium Impact)
-----------------------------------------------------------
# Reflex projects generate huge .web folders
rm -rf '$DEV_DIR/apps/reflex-*/.web/node_modules'
rm -rf '$DEV_DIR/apps/game_models/.web'
rm -rf '$DEV_DIR/apps/working_reflex/reflex-project/.web/.next'

Option 3: CLEAN PYTHON VENVS (Big Win)
---------------------------------------
# Your unified-donkey-betz venv is probably huge
echo 'Size of unified-donkey-betz venv:'
du -sh '$DEV_DIR/unified-donkey-betz/.venv' 2>/dev/null

# To delete it (you can recreate with pip install -r requirements.txt):
# rm -rf '$DEV_DIR/unified-donkey-betz/.venv'

Option 4: NUCLEAR OPTION - Delete ALL node_modules
---------------------------------------------------
# This will free up GIGABYTES but you'll need to npm install in active projects
# find '$DEV_DIR' -type d -name 'node_modules' -prune -exec rm -rf {} \;
"

echo -e "\n=========================================="
echo "🎯 RECOMMENDED ACTION PLAN"
echo "=========================================="

echo "
1. START HERE (Safe & Big Impact):
   --------------------------------
   Copy and run these commands:

   # Delete old project node_modules
   rm -rf ~/development/apps/aidentifier/node_modules
   rm -rf ~/development/apps/tailwind_udemy/node_modules
   rm -rf ~/development/apps/testing-front-end/node_modules
   rm -rf ~/development/apps/Nextjs-Creative-Portfolio-Starter-Code-Files/node_modules
   
   # Delete reflex build folders
   rm -rf ~/development/apps/reflex-gpt/.web
   rm -rf ~/development/apps/reflex-practice/.web
   rm -rf ~/development/apps/reflex-project/.web
   
   # Clear Python cache
   find ~/development -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
   find ~/development -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null

2. CHECK SPACE FREED:
   ------------------
   df -h ~

3. IF YOU NEED MORE SPACE:
   ------------------------
   # Delete the ai-content-studio node_modules (old project)
   rm -rf ~/development/ai-content-studio/*/node_modules
   
   # Consider removing unified-donkey-betz venv (can recreate later)
   rm -rf ~/development/unified-donkey-betz/.venv

4. NUCLEAR OPTION (if desperate):
   --------------------------------
   # Delete ALL node_modules (frees up several GB)
   find ~/development -type d -name 'node_modules' -prune -exec rm -rf {} \;
"

echo -e "\n💡 PRO TIPS:"
echo "=========================================="
echo "• You can always run 'npm install' to restore node_modules"
echo "• Python venvs can be recreated with 'python -m venv .venv && pip install -r requirements.txt'"
echo "• Consider using pnpm instead of npm - it shares packages between projects"
echo "• Move completed projects to an external drive or cloud storage"

echo -e "\n📊 Potential Space Recovery:"
echo "=========================================="
echo "Estimated: 5-10 GB minimum, possibly 20+ GB"
echo "Most of it is from node_modules folders!"
