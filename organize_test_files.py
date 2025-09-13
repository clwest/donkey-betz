#!/usr/bin/env python3
"""
Organize test files from root directory into proper test directories
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Base directory
BASE_DIR = Path("/Users/donkeyking/development/unified-donkey-betz")

# Test files to move (identified by prefix)
TEST_FILE_PATTERNS = [
    "test_*.py",
    "test_*.html",
    "verify_*.py",
    "check_*.py",
    "debug_*.py",
    "debug_*.html",
    "*_test_*.py",
    "*_test_*.json",
    "*_test_*.html",
]

# Create organized test directory structure
TEST_DIRS = {
    "tests": "Main test directory",
    "tests/unit": "Unit tests",
    "tests/integration": "Integration tests", 
    "tests/frontend": "Frontend/HTML test files",
    "tests/websocket": "WebSocket test files",
    "tests/api": "API test files",
    "tests/verification": "Verification scripts",
    "tests/debug": "Debug scripts and files",
}

def create_test_directories():
    """Create organized test directory structure"""
    for dir_path, description in TEST_DIRS.items():
        full_path = BASE_DIR / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {dir_path} - {description}")
        else:
            print(f"ℹ️  Exists: {dir_path}")

def categorize_test_file(filename):
    """Determine which test directory a file should go to"""
    name_lower = filename.lower()
    
    # HTML files go to frontend tests
    if filename.endswith('.html'):
        return "tests/frontend"
    
    # WebSocket tests
    if 'websocket' in name_lower or '_ws' in name_lower or 'ws_' in name_lower:
        return "tests/websocket"
    
    # API tests
    if 'api' in name_lower or 'endpoint' in name_lower:
        return "tests/api"
    
    # Verification scripts
    if filename.startswith('verify_') or filename.startswith('validate_'):
        return "tests/verification"
    
    # Debug scripts
    if filename.startswith('debug_') or 'debug' in name_lower:
        return "tests/debug"
    
    # Integration tests
    if 'integration' in name_lower or 'comprehensive' in name_lower or 'cross_system' in name_lower:
        return "tests/integration"
    
    # Default to unit tests for other test files
    if filename.startswith('test_'):
        return "tests/unit"
    
    # Check scripts go to verification
    if filename.startswith('check_'):
        return "tests/verification"
    
    # Default to main tests directory
    return "tests"

def move_test_files():
    """Move test files to appropriate directories"""
    moved_count = 0
    skipped_count = 0
    
    # Create a backup list file
    backup_list = BASE_DIR / "test_files_moved.txt"
    
    with open(backup_list, 'w') as f:
        f.write(f"Test Files Organization - {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        
        # Find all test files in root directory
        for pattern in TEST_FILE_PATTERNS:
            for file_path in BASE_DIR.glob(pattern):
                # Skip if it's a directory or already in a test directory
                if file_path.is_dir() or 'test' in str(file_path.parent.name).lower():
                    continue
                
                filename = file_path.name
                target_dir = categorize_test_file(filename)
                target_path = BASE_DIR / target_dir / filename
                
                # Check if file already exists in target
                if target_path.exists():
                    print(f"⚠️  Skipped (exists): {filename} -> {target_dir}")
                    f.write(f"SKIPPED (exists): {filename} -> {target_dir}\n")
                    skipped_count += 1
                else:
                    try:
                        # Move the file
                        shutil.move(str(file_path), str(target_path))
                        print(f"✅ Moved: {filename} -> {target_dir}")
                        f.write(f"MOVED: {filename} -> {target_dir}\n")
                        moved_count += 1
                    except Exception as e:
                        print(f"❌ Error moving {filename}: {str(e)}")
                        f.write(f"ERROR: {filename} - {str(e)}\n")
    
    return moved_count, skipped_count

def main():
    """Main function to organize test files"""
    print("🧹 Starting Test File Organization")
    print("=" * 60)
    
    # Step 1: Create directory structure
    print("\n📁 Creating test directory structure...")
    create_test_directories()
    
    # Step 2: Move test files
    print("\n📦 Moving test files to organized directories...")
    moved, skipped = move_test_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ Test File Organization Complete!")
    print(f"📊 Files moved: {moved}")
    print(f"⏭️  Files skipped: {skipped}")
    print(f"📝 Backup list saved to: test_files_moved.txt")
    
    # Additional cleanup suggestions
    print("\n💡 Additional cleanup suggestions:")
    print("1. Review migration scripts (migrate_*.py) - consider moving to scripts/")
    print("2. Review fix scripts (fix_*.py) - consider moving to scripts/fixes/")
    print("3. Review .md documentation files - consider organizing in docs/")
    print("4. Consider creating a 'tools' directory for utility scripts")

if __name__ == "__main__":
    main()
