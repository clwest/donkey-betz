# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Security Validation Script
Validates that all critical security fixes have been properly implemented
"""

import os
import sys
import django
from pathlib import Path
from dotenv import load_dotenv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from core.security import validate_environment, get_env_manager

def check_env_file():
    """Check .env file security"""
    print("\n🔍 Checking .env file security...")
    issues = []
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            
        # Check for exposed API keys
        dangerous_patterns = [
            'sk-proj-',  # OpenAI
            'sk-ant-',   # Anthropic
            'gsk_',      # Groq
            'AIzaSy',    # Google
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content:
                issues.append(f"❌ Found exposed API key pattern: {pattern}***")
    
    # Check .gitignore
    gitignore = Path('.gitignore')
    if gitignore.exists():
        with open(gitignore, 'r') as f:
            gitignore_content = f.read()
        if '.env' not in gitignore_content:
            issues.append("❌ .env not in .gitignore")
        else:
            print("✅ .env is properly gitignored")
    
    return issues

def check_websocket_auth():
    """Check WebSocket authentication configuration"""
    print("\n🔍 Checking WebSocket authentication...")
    issues = []
    
    # Check consumers.py
    consumers_file = Path('agents/consumers.py')
    if consumers_file.exists():
        with open(consumers_file, 'r') as f:
            content = f.read()
        
        if 'ENABLE_WEBSOCKET_AUTH' not in content:
            issues.append("❌ WebSocket auth not checking ENABLE_WEBSOCKET_AUTH")
        else:
            print("✅ WebSocket authentication is configurable")
        
        if 'await self.close(code=4001)' in content:
            print("✅ WebSocket closes unauthenticated connections")
        else:
            issues.append("⚠️  WebSocket may not properly close unauthenticated connections")
    
    return issues

def check_cors_configuration():
    """Check CORS configuration"""
    print("\n🔍 Checking CORS configuration...")
    issues = []
    
    # Check CORS settings
    if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS'):
        if settings.CORS_ALLOW_ALL_ORIGINS and not settings.DEBUG:
            issues.append("❌ CORS_ALLOW_ALL_ORIGINS is True in production!")
        elif settings.CORS_ALLOW_ALL_ORIGINS and settings.DEBUG:
            print("⚠️  CORS_ALLOW_ALL_ORIGINS is True (OK for development)")
        else:
            print("✅ CORS_ALLOW_ALL_ORIGINS is False")
    
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"✅ CORS allowed origins: {settings.CORS_ALLOWED_ORIGINS[:3]}...")
    
    return issues

def check_test_files():
    """Check for hardcoded tokens in test files"""
    print("\n🔍 Checking test files for hardcoded tokens...")
    issues = []
    
    test_files = [
        'test_assistant.py',
        'test_integration.py',
        'test_connections.py',
        'verify_api_endpoints.py',
    ]
    
    for test_file in test_files:
        filepath = Path(test_file)
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for hardcoded tokens
            if 'os.getenv' in content and 'TEST_AUTH_TOKEN' in content:
                print(f"✅ {test_file} uses environment variables")
            else:
                # Check for hardcoded tokens
                import re
                token_pattern = r"os\.environ\.get\('TOKEN',\s*'test-token'\)\s*=\s*['\"][a-f0-9]{40}['\"]"
                if re.search(token_pattern, content):
                    issues.append(f"❌ {test_file} has hardcoded token")
    
    return issues

def check_security_settings():
    """Check Django security settings"""
    print("\n🔍 Checking Django security settings...")
    issues = []
    warnings = []
    
    # Production security checks
    if not settings.DEBUG:
        security_settings = {
            'SECURE_SSL_REDIRECT': True,
            'SECURE_HSTS_SECONDS': 0,  # Should be > 0
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
            'SECURE_CONTENT_TYPE_NOSNIFF': True,
            'SECURE_BROWSER_XSS_FILTER': True,
        }
        
        for setting, expected in security_settings.items():
            actual = getattr(settings, setting, None)
            if setting == 'SECURE_HSTS_SECONDS':
                if actual and actual > 0:
                    print(f"✅ {setting} = {actual}")
                else:
                    issues.append(f"❌ {setting} not properly configured")
            elif actual == expected:
                print(f"✅ {setting} = {actual}")
            else:
                issues.append(f"❌ {setting} = {actual} (expected {expected})")
    else:
        print("ℹ️  Running in DEBUG mode - production security checks skipped")
    
    # Password validation
    if hasattr(settings, 'AUTH_PASSWORD_VALIDATORS'):
        validators = settings.AUTH_PASSWORD_VALIDATORS
        if len(validators) >= 4:
            print(f"✅ {len(validators)} password validators configured")
        else:
            warnings.append(f"⚠️  Only {len(validators)} password validators")
    
    return issues, warnings

def check_environment_validation():
    """Run environment validation"""
    print("\n🔍 Running environment validation...")
    
    validation_results = validate_environment()
    
    if validation_results['valid']:
        print("✅ Environment validation passed")
    else:
        print("❌ Environment validation failed")
    
    for error in validation_results['errors']:
        print(f"  ❌ {error}")
    
    for warning in validation_results['warnings']:
        print(f"  ⚠️  {warning}")
    
    for info in validation_results['info']:
        print(f"  ℹ️  {info}")
    
    return validation_results

def main():
    """Run all security checks"""
    print("=" * 60)
    print("🛡️  SECURITY VALIDATION REPORT")
    print("=" * 60)
    
    all_issues = []
    all_warnings = []
    
    # Check .env file
    issues = check_env_file()
    all_issues.extend(issues)
    
    # Check WebSocket auth
    issues = check_websocket_auth()
    all_issues.extend(issues)
    
    # Check CORS
    issues = check_cors_configuration()
    all_issues.extend(issues)
    
    # Check test files
    issues = check_test_files()
    all_issues.extend(issues)
    
    # Check security settings
    issues, warnings = check_security_settings()
    all_issues.extend(issues)
    all_warnings.extend(warnings)
    
    # Run environment validation
    validation_results = check_environment_validation()
    if not validation_results['valid']:
        all_issues.extend(validation_results['errors'])
    all_warnings.extend(validation_results['warnings'])
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} critical issues:")
        for issue in all_issues:
            print(f"  • {issue}")
    else:
        print("\n✅ No critical security issues found!")
    
    if all_warnings:
        print(f"\n⚠️  Found {len(all_warnings)} warnings:")
        for warning in all_warnings[:5]:  # Show first 5 warnings
            print(f"  • {warning}")
        if len(all_warnings) > 5:
            print(f"  ... and {len(all_warnings) - 5} more warnings")
    
    print("\n" + "=" * 60)
    print("🔒 SECURITY RECOMMENDATIONS")
    print("=" * 60)
    print("""
1. IMMEDIATE ACTIONS:
   • Rotate ALL API keys that were exposed
   • Ensure .env file is never committed to git
   • Enable WebSocket authentication in production
   • Restrict CORS origins in production

2. BEFORE PRODUCTION:
   • Set ENVIRONMENT=production in .env
   • Enable all security headers (HSTS, CSP, etc.)
   • Configure proper SSL certificates
   • Set up rate limiting
   • Enable audit logging
   • Configure backup encryption

3. ONGOING SECURITY:
   • Regularly rotate API keys and tokens
   • Monitor security logs
   • Keep dependencies updated
   • Perform regular security audits
   • Train team on security best practices
""")
    
    # Exit code
    if all_issues:
        print("\n❌ Security validation FAILED - fix critical issues before deployment")
        sys.exit(1)
    else:
        print("\n✅ Security validation PASSED - ready for next steps")
        sys.exit(0)

if __name__ == '__main__':
    main()