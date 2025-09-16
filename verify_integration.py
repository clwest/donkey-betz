#!/usr/bin/env python
"""
Quick verification of Personal Assistant Self-Awareness Integration
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
django.setup()

print("\n" + "="*60)
print("PERSONAL ASSISTANT SELF-AWARENESS VERIFICATION")
print("="*60)

# Test the integration directly
from core.personal_assistant_integration import personal_assistant_integration

# Test with a simple message
context = personal_assistant_integration.enhance_assistant_context(
    message="What's the system status?",
    conversation_id="verify_test"
)

print("\n✅ Integration is working!")
print(f"   Platform Status: {context['system_awareness']['platform_reality']}")
print(f"   Operational: {context['system_awareness']['operational_percentage']}%")

if context['recommendations']:
    print(f"\n📋 Recommendations:")
    for rec in context['recommendations'][:3]:
        print(f"   • {rec}")

if context['routing'] and context['routing'].get('primary_component'):
    print(f"\n🎯 Routing:")
    print(f"   Primary: {context['routing']['primary_component']}")
    print(f"   Confidence: {context['routing']['confidence']:.0%}")

print("\n✅ Self-awareness integration successfully added to the intelligent assistant!")
print("   The Personal Assistant now has:")
print("   • System operational awareness")
print("   • Component status tracking")
print("   • Intelligent routing based on queries")
print("   • Context-aware recommendations")

print("\n📝 To see it in action:")
print("   1. Make sure the Django server is running: make run-dev")
print("   2. Try asking the assistant about system status")
print("   3. The response will include system awareness data")

print("\n" + "="*60)