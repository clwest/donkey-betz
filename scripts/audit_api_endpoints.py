#!/usr/bin/env python3
"""
API Endpoint Reality Audit Script
Tests all API endpoints for hardcoded/mock data patterns
Usage: python3 scripts/audit_api_endpoints.py
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import get_resolver, URLPattern, URLResolver

print("=" * 80)
print("API ENDPOINT REALITY AUDIT")
print("=" * 80)
print()

# Mock data patterns to detect
MOCK_PATTERNS = {
    'example.com': 'Mock URL pattern',
    'placeholder': 'Placeholder text',
    'demo': 'Demo data',
    'test@': 'Test email',
    'fake': 'Fake data',
    'mock': 'Mock data',
    '149': 'Hardcoded agent count',
    '2600': 'Hardcoded revenue amount',
    'lorem ipsum': 'Lorem ipsum text',
}

# Hardcoded numbers to watch for
SUSPICIOUS_NUMBERS = ['149', '2600', '1393', '196', '25', '40']

# Initialize test client
client = Client()
factory = RequestFactory()
User = get_user_model()

# Create or get test user
try:
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser('testadmin', 'test@example.com', 'testpass123')
        print("✅ Created test superuser")
    else:
        print(f"✅ Using existing superuser: {user.username}")
except Exception as e:
    print(f"⚠️  Could not create/get test user: {e}")
    user = None

# Login client
if user:
    client.force_login(user)
    print("✅ Test client authenticated")
print()

def extract_urls(urlpatterns, base='', namespace=None):
    """Recursively extract all URL patterns"""
    url_list = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            path = base + str(pattern.pattern)
            url_list.append({
                'path': path,
                'name': pattern.name,
                'namespace': namespace
            })
        elif isinstance(pattern, URLResolver):
            namespace_prefix = f"{namespace}:" if namespace else ""
            new_namespace = f"{namespace_prefix}{pattern.namespace}" if pattern.namespace else namespace
            url_list.extend(extract_urls(pattern.url_patterns, base + str(pattern.pattern), new_namespace))
    return url_list

def check_response_for_mock_data(url, response):
    """Check response content for mock data patterns"""
    issues = []

    try:
        # Try to parse as JSON
        if response.get('Content-Type', '').startswith('application/json'):
            try:
                content = json.loads(response.content.decode('utf-8'))
                content_str = json.dumps(content, indent=2)
            except:
                content_str = response.content.decode('utf-8', errors='ignore')
        else:
            content_str = response.content.decode('utf-8', errors='ignore')

        # Check for mock patterns
        for pattern, description in MOCK_PATTERNS.items():
            if pattern.lower() in content_str.lower():
                issues.append({
                    'pattern': pattern,
                    'description': description,
                    'sample': content_str[max(0, content_str.lower().find(pattern.lower())-50):
                                         content_str.lower().find(pattern.lower())+100]
                })

        return issues
    except Exception as e:
        return [{'error': str(e)}]

def test_endpoint(url_info):
    """Test a single endpoint"""
    path = url_info['path']

    # Skip static/media URLs
    if any(skip in path for skip in ['^static/', '^media/', '<path:', 'debug']):
        return None

    # Convert Django URL pattern to test URL
    test_url = '/' + path.replace('^', '').replace('$', '')

    # Skip URLs with required parameters for now (would need proper values)
    if '<' in test_url or '(' in test_url:
        return {
            'url': test_url,
            'status': 'skipped',
            'reason': 'requires_parameters'
        }

    result = {
        'url': test_url,
        'name': url_info['name'],
        'namespace': url_info['namespace']
    }

    try:
        # Test GET request
        response = client.get(test_url, follow=True)
        result['status_code'] = response.status_code

        if response.status_code == 200:
            issues = check_response_for_mock_data(test_url, response)
            if issues:
                result['status'] = 'issues_found'
                result['issues'] = issues
            else:
                result['status'] = 'clean'
        elif response.status_code in [301, 302]:
            result['status'] = 'redirect'
        elif response.status_code == 403:
            result['status'] = 'forbidden'
        elif response.status_code == 404:
            result['status'] = 'not_found'
        else:
            result['status'] = 'other'

    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)

    return result

# Get all URL patterns
print("🔍 Extracting all URL patterns...")
resolver = get_resolver()
all_urls = extract_urls(resolver.url_patterns)
print(f"📊 Found {len(all_urls)} URL patterns\n")

# Test endpoints
print("=" * 80)
print("TESTING API ENDPOINTS")
print("=" * 80)
print()

results = {
    'clean': [],
    'issues_found': [],
    'skipped': [],
    'errors': [],
    'other': []
}

for i, url_info in enumerate(all_urls, 1):
    # Only test API endpoints and key views
    path = url_info['path']
    if not any(api in path for api in ['api/', 'ajax/', 'ws/', 'intelligence', 'revenue', 'income', 'decision', 'control', 'neural', 'monetization']):
        results['skipped'].append(url_info['path'])
        continue

    print(f"[{i}/{len(all_urls)}] Testing: {url_info['path']}")

    result = test_endpoint(url_info)
    if result:
        status = result.get('status', 'other')

        if status == 'issues_found':
            print(f"  ⚠️  ISSUES FOUND:")
            for issue in result['issues']:
                if 'pattern' in issue:
                    print(f"     - {issue['description']}: '{issue['pattern']}'")
            results['issues_found'].append(result)
        elif status == 'clean':
            print(f"  ✅ Clean (status {result['status_code']})")
            results['clean'].append(result)
        elif status == 'error':
            print(f"  ❌ Error: {result.get('error', 'Unknown')}")
            results['errors'].append(result)
        elif status == 'skipped':
            results['skipped'].append(result)
        else:
            results['other'].append(result)

    print()

# Summary Report
print("=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)
print()
print(f"Total URLs analyzed: {len(all_urls)}")
print(f"✅ Clean endpoints: {len(results['clean'])}")
print(f"⚠️  Endpoints with issues: {len(results['issues_found'])}")
print(f"⏭️  Skipped (requires params): {len(results['skipped'])}")
print(f"❌ Errors: {len(results['errors'])}")
print(f"ℹ️  Other (redirects, etc.): {len(results['other'])}")
print()

# Detailed issues
if results['issues_found']:
    print("=" * 80)
    print("DETAILED ISSUES")
    print("=" * 80)
    print()

    for result in results['issues_found']:
        print(f"URL: {result['url']}")
        print(f"Status: {result['status_code']}")
        print(f"Issues:")
        for issue in result['issues']:
            if 'pattern' in issue:
                print(f"  - {issue['description']}: '{issue['pattern']}'")
                print(f"    Context: {issue['sample'][:100]}...")
        print()

# Save results to JSON
output_file = f"endpoint_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'total_urls': len(all_urls),
        'summary': {
            'clean': len(results['clean']),
            'issues_found': len(results['issues_found']),
            'skipped': len(results['skipped']),
            'errors': len(results['errors']),
            'other': len(results['other'])
        },
        'results': results
    }, f, indent=2)

print(f"📁 Full results saved to: {output_file}")
print()
print("=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
