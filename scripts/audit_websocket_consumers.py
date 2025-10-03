#!/usr/bin/env python3
"""
WebSocket Consumer Reality Audit Script
Tests all WebSocket consumers for hardcoded/mock data patterns
Usage: python3 scripts/audit_websocket_consumers.py
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from channels.testing import WebsocketCommunicator
from channels.routing import get_default_application
from django.contrib.auth import get_user_model

print("=" * 80)
print("WEBSOCKET CONSUMER REALITY AUDIT")
print("=" * 80)
print()

# Mock data patterns to detect
MOCK_PATTERNS = {
    'example.com': 'Mock URL pattern',
    'placeholder': 'Placeholder text',
    'demo': 'Demo data',
    'fake': 'Fake data',
    'mock': 'Mock data',
    'lorem ipsum': 'Lorem ipsum text',
}

# Hardcoded numbers to watch for (from Session 31 findings)
SUSPICIOUS_NUMBERS = {
    '149': 'Hardcoded old agent count',
    '2600': 'Hardcoded revenue amount ($2,600)',
    '1393': 'Old mock data count',
    '40': 'Hardcoded spider count',
}

# WebSocket endpoints to test
WEBSOCKET_ENDPOINTS = [
    {
        'path': '/ws/neural-orchestra/',
        'name': 'Neural Orchestra',
        'expected_message_types': ['orchestra_data', 'agent_update']
    },
    {
        'path': '/ws/control-center/',
        'name': 'Control Center',
        'expected_message_types': ['metrics', 'system_status']
    },
    {
        'path': '/ws/monetization-hub/',
        'name': 'Monetization Hub',
        'expected_message_types': ['revenue_update', 'opportunity']
    },
    {
        'path': '/ws/decision-command/',
        'name': 'Decision Command',
        'expected_message_types': ['opportunities', 'analysis']
    },
    {
        'path': '/ws/income-builder/',
        'name': 'Income Builder',
        'expected_message_types': ['opportunities', 'status']
    },
    {
        'path': '/ws/revenue-dashboard/',
        'name': 'Revenue Dashboard',
        'expected_message_types': ['revenue_data', 'stats']
    },
    {
        'path': '/ws/personal-assistant/',
        'name': 'Personal Assistant',
        'expected_message_types': ['message', 'response']
    },
]

User = get_user_model()

def check_message_for_mock_data(message_data):
    """Check WebSocket message for mock data patterns"""
    issues = []

    try:
        # Convert message to string for searching
        if isinstance(message_data, dict):
            content_str = json.dumps(message_data, indent=2)
        else:
            content_str = str(message_data)

        # Check for mock patterns
        for pattern, description in MOCK_PATTERNS.items():
            if pattern.lower() in content_str.lower():
                # Get context around the match
                start = max(0, content_str.lower().find(pattern.lower()) - 50)
                end = min(len(content_str), content_str.lower().find(pattern.lower()) + 100)
                context = content_str[start:end]

                issues.append({
                    'type': 'mock_pattern',
                    'pattern': pattern,
                    'description': description,
                    'context': context
                })

        # Check for suspicious hardcoded numbers
        for number, description in SUSPICIOUS_NUMBERS.items():
            if number in content_str:
                # Avoid false positives in IDs/timestamps
                if not any(avoid in content_str[max(0, content_str.find(number)-20):content_str.find(number)+20]
                          for avoid in ['id', 'timestamp', 'date', 'time', 'uuid']):
                    issues.append({
                        'type': 'suspicious_number',
                        'number': number,
                        'description': description
                    })

        return issues
    except Exception as e:
        return [{'type': 'error', 'error': str(e)}]

async def test_websocket_endpoint(endpoint_info):
    """Test a single WebSocket endpoint"""
    print(f"\n{'=' * 80}")
    print(f"Testing: {endpoint_info['name']}")
    print(f"Path: {endpoint_info['path']}")
    print('=' * 80)

    result = {
        'name': endpoint_info['name'],
        'path': endpoint_info['path'],
        'status': 'unknown',
        'messages_received': 0,
        'issues': []
    }

    try:
        # Get or create test user
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("⚠️  No superuser found, creating one...")
            user = User.objects.create_superuser('testadmin', 'test@example.com', 'testpass123')

        # Create WebSocket communicator
        application = get_default_application()
        communicator = WebsocketCommunicator(
            application,
            endpoint_info['path']
        )

        # Add user to scope for authenticated connection
        communicator.scope['user'] = user

        # Connect
        print("🔌 Attempting to connect...")
        connected, subprotocol = await communicator.connect()

        if not connected:
            result['status'] = 'connection_failed'
            print("❌ Connection failed")
            return result

        print("✅ Connected successfully")
        result['status'] = 'connected'

        # Wait for initial messages (timeout after 5 seconds)
        messages = []
        try:
            for _ in range(10):  # Try to receive up to 10 messages
                message = await asyncio.wait_for(
                    communicator.receive_json_from(),
                    timeout=2.0
                )
                messages.append(message)
                print(f"📨 Received message {len(messages)}")
        except asyncio.TimeoutError:
            print(f"⏱️  Timeout - received {len(messages)} messages total")
        except Exception as e:
            print(f"⚠️  Error receiving: {e}")

        result['messages_received'] = len(messages)

        # Analyze each message for mock data
        all_issues = []
        for i, message in enumerate(messages):
            print(f"\n--- Analyzing Message {i+1} ---")
            issues = check_message_for_mock_data(message)

            if issues:
                print(f"⚠️  Found {len(issues)} issues:")
                for issue in issues:
                    if issue.get('type') == 'mock_pattern':
                        print(f"   - {issue['description']}: '{issue['pattern']}'")
                        print(f"     Context: ...{issue['context'][:80]}...")
                    elif issue.get('type') == 'suspicious_number':
                        print(f"   - {issue['description']}: '{issue['number']}'")
                    else:
                        print(f"   - Error: {issue.get('error', 'Unknown')}")

                all_issues.extend(issues)
            else:
                print("✅ No issues detected")

            # Show message size
            message_size = len(json.dumps(message))
            print(f"   Size: {message_size:,} bytes")

        result['issues'] = all_issues
        if all_issues:
            result['status'] = 'issues_found'
        else:
            result['status'] = 'clean'

        # Disconnect
        await communicator.disconnect()
        print("\n🔌 Disconnected")

    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        print(f"❌ Error: {e}")

    return result

async def run_audit():
    """Run the complete WebSocket audit"""
    results = []

    print("\n🚀 Starting WebSocket consumer audit...")
    print(f"Testing {len(WEBSOCKET_ENDPOINTS)} endpoints\n")

    for endpoint_info in WEBSOCKET_ENDPOINTS:
        result = await test_websocket_endpoint(endpoint_info)
        results.append(result)

    # Summary Report
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print()

    summary = {
        'clean': 0,
        'issues_found': 0,
        'connection_failed': 0,
        'errors': 0
    }

    for result in results:
        status = result['status']
        if status in summary:
            summary[status] += 1
        else:
            summary['errors'] += 1

    print(f"Total WebSocket endpoints tested: {len(WEBSOCKET_ENDPOINTS)}")
    print(f"✅ Clean endpoints: {summary['clean']}")
    print(f"⚠️  Endpoints with issues: {summary['issues_found']}")
    print(f"❌ Connection failures: {summary['connection_failed']}")
    print(f"❌ Errors: {summary['errors']}")
    print()

    # Detailed issues
    endpoints_with_issues = [r for r in results if r['status'] == 'issues_found']
    if endpoints_with_issues:
        print("=" * 80)
        print("DETAILED ISSUES")
        print("=" * 80)
        print()

        for result in endpoints_with_issues:
            print(f"\n{result['name']} ({result['path']})")
            print(f"Messages received: {result['messages_received']}")
            print(f"Issues found: {len(result['issues'])}")
            print()

            # Group issues by type
            mock_patterns = [i for i in result['issues'] if i.get('type') == 'mock_pattern']
            suspicious_numbers = [i for i in result['issues'] if i.get('type') == 'suspicious_number']

            if mock_patterns:
                print("Mock Data Patterns:")
                for issue in mock_patterns:
                    print(f"  - {issue['description']}: '{issue['pattern']}'")

            if suspicious_numbers:
                print("Suspicious Hardcoded Numbers:")
                for issue in suspicious_numbers:
                    print(f"  - {issue['description']}: '{issue['number']}'")

            print()

    # Save results to JSON
    output_file = f"websocket_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_endpoints': len(WEBSOCKET_ENDPOINTS),
            'summary': summary,
            'results': results
        }, f, indent=2)

    print(f"📁 Full results saved to: {output_file}")
    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

    return results

if __name__ == '__main__':
    # Run the async audit
    asyncio.run(run_audit())
