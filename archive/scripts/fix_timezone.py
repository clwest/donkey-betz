#!/usr/bin/env python3
"""
🕐 FIX TIMEZONE WARNINGS
Replace datetime.now() with timezone.now() throughout
"""

import os

def fix_timezone_warnings():
    """Fix all timezone warnings in activate_all_agents.py"""
    
    file_path = '/Users/donkeyking/development/unified-donkey-betz/activate_all_agents.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Count how many replacements we'll make
    count = content.count('datetime.now()')
    print(f"Found {count} instances of datetime.now() to fix")
    
    # Replace datetime.now() with timezone.now()
    # First ensure timezone is imported
    if 'from django.utils import timezone' not in content:
        # Add the import after django.setup()
        content = content.replace(
            'django.setup()\n',
            'django.setup()\n\nfrom django.utils import timezone\n'
        )
        print("✅ Added timezone import")
    
    # Replace all datetime.now() with timezone.now()
    content = content.replace('from datetime import datetime', 'from datetime import datetime')
    content = content.replace('datetime.now()', 'timezone.now()')
    
    # Also fix the timedelta import
    if 'timedelta' in content and 'from datetime import datetime, timedelta' not in content:
        content = content.replace(
            'from datetime import datetime',
            'from datetime import datetime, timedelta'
        )
    
    # Save the fixed version
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed {count} timezone issues!")
    print("✅ No more RuntimeWarnings!")
    
    return True

def fix_other_files_too():
    """Also fix timezone issues in other scripts"""
    
    files_to_fix = [
        'execute_test_agent.py',
        'fix_agent_results.py',
        'celebration.py'
    ]
    
    for filename in files_to_fix:
        file_path = f'/Users/donkeyking/development/unified-donkey-betz/{filename}'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            if 'datetime.now()' in content:
                # Add timezone import if needed
                if 'from django.utils import timezone' not in content:
                    content = content.replace(
                        'django.setup()\n',
                        'django.setup()\n\nfrom django.utils import timezone\n'
                    )
                
                # Replace datetime.now() with timezone.now()
                old_count = content.count('datetime.now()')
                content = content.replace('datetime.now()', 'timezone.now()')
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ Fixed {old_count} issues in {filename}")

if __name__ == "__main__":
    print("="*60)
    print("🕐 FIXING TIMEZONE WARNINGS")
    print("="*60)
    print()
    
    fix_timezone_warnings()
    fix_other_files_too()
    
    print("\n✅ All timezone warnings fixed!")
    print("\nNow when you run the scripts, no more warnings!")
    print("\nTest it:")
    print("python activate_all_agents.py")
