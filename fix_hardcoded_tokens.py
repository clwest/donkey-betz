#!/usr/bin/env python3
"""
Script to fix hardcoded tokens in test files
Replaces hardcoded tokens with environment variable references
"""

import os
import re
from pathlib import Path

# Files to update
FILES_TO_UPDATE = [
    'verify_api_endpoints.py',  # Already fixed
    'verify_and_integrate_embeddings.py',
    'test_assistant.py',
    'test_integration.py',
    'test_connections.py',
    'test_rag_assistant.py',
    'test_embeddings_usage.py',
    'test_workflows_specific.py',
    'test_all_pages.py',
    'verify_embeddings_integration.py',
]

# Common imports to add
SECURITY_IMPORTS = """import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
"""

def fix_file(filepath):
    """Fix hardcoded tokens in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Check if already fixed
        if 'os.getenv' in content and 'TEST_AUTH_TOKEN' in content:
            print(f"✓ {filepath} - Already fixed")
            return False
            
        # Add imports if not present
        if 'from dotenv import load_dotenv' not in content:
            # Find the right place to add imports (after existing imports)
            import_section_end = 0
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_section_end = i + 1
                elif import_section_end > 0 and line and not line.startswith('#'):
                    break
            
            # Insert new imports
            lines.insert(import_section_end, '')
            lines.insert(import_section_end + 1, '# Security fix: Load environment variables')
            lines.insert(import_section_end + 2, 'import os')
            if 'import os' not in content:
                lines.insert(import_section_end + 3, 'from dotenv import load_dotenv')
            else:
                lines.insert(import_section_end + 3, 'from dotenv import load_dotenv')
            lines.insert(import_section_end + 4, 'load_dotenv()')
            content = '\n'.join(lines)
        
        # Replace hardcoded tokens
        patterns = [
            (r'TOKEN\s*=\s*["\'][a-f0-9]{40}["\']', 
             'TOKEN = os.getenv("TEST_AUTH_TOKEN", "")\nif not TOKEN:\n    print("WARNING: No TEST_AUTH_TOKEN found. Please set it in .env file.")\n    import sys\n    sys.exit(1)'),
            (r'AUTH_TOKEN\s*=\s*["\'][a-f0-9]{40}["\'](\s*#.*)?', 
             'AUTH_TOKEN = os.getenv("TEST_AUTH_TOKEN", "")\nif not AUTH_TOKEN:\n    print("WARNING: No TEST_AUTH_TOKEN found. Please set it in .env file.")\n    import sys\n    sys.exit(1)'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Fix BASE_URL if hardcoded
        content = re.sub(
            r'BASE_URL\s*=\s*["\']http://localhost:\d+["\']',
            'BASE_URL = os.getenv("BASE_URL", "http://localhost:8001")',
            content
        )
        
        # Fix WS_URL if hardcoded
        content = re.sub(
            r'WS_URL\s*=\s*["\']ws://localhost:\d+(?:/ws)?["\']',
            'WS_URL = os.getenv("WS_URL", "ws://localhost:8001/ws")',
            content
        )
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✓ {filepath} - Fixed hardcoded tokens")
            return True
        else:
            print(f"✓ {filepath} - No changes needed")
            return False
            
    except FileNotFoundError:
        print(f"✗ {filepath} - File not found")
        return False
    except Exception as e:
        print(f"✗ {filepath} - Error: {str(e)}")
        return False

def main():
    """Fix all test files"""
    print("Fixing hardcoded tokens in test files...")
    print("=" * 50)
    
    fixed_count = 0
    for filename in FILES_TO_UPDATE:
        filepath = Path(filename)
        if fix_file(filepath):
            fixed_count += 1
    
    print("=" * 50)
    print(f"Fixed {fixed_count} files")
    
    # Create a management command to generate test tokens
    management_command = '''"""
Django management command to create a test authentication token
Usage: python manage.py create_test_token [username]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates or retrieves an authentication token for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            nargs='?',
            default='testuser',
            help='Username to create token for'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        
        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@test.com',
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        self.stdout.write(self.style.SUCCESS(f'\\nToken for {username}: {token.key}'))
        self.stdout.write('\\nAdd this to your .env file:')
        self.stdout.write(f'TEST_AUTH_TOKEN={token.key}')
'''
    
    # Create the management command file
    command_dir = Path('core/management/commands')
    command_dir.mkdir(parents=True, exist_ok=True)
    
    command_file = command_dir / 'create_test_token.py'
    with open(command_file, 'w') as f:
        f.write(management_command)
    
    # Create __init__.py files if they don't exist
    (command_dir.parent / '__init__.py').touch(exist_ok=True)
    (command_dir / '__init__.py').touch(exist_ok=True)
    
    print("\n✓ Created management command: create_test_token")
    print("\nTo generate a test token, run:")
    print("  python manage.py create_test_token")
    print("\nThen add the token to your .env file as TEST_AUTH_TOKEN")

if __name__ == '__main__':
    main()