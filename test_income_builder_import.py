#!/usr/bin/env python
"""Test if Income Builder imports work in WebSocket context"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

try:
    # Test the exact import that the WebSocket consumer uses
    from intelligence.income_builder import income_builder, UserProfile, SkillLevel
    print("✅ Import successful from intelligence.income_builder")

    # Test creating a profile
    profile = UserProfile(
        id='test',
        skills=['python'],
        skill_level=SkillLevel.INTERMEDIATE,
        current_balance=0,
        available_hours_per_week=20
    )
    print(f"✅ Created UserProfile: {profile.id}")

    # Test that income_builder has opportunities
    print(f"✅ Income builder has {len(income_builder.opportunities)} opportunities")

    # Show first opportunity
    if income_builder.opportunities:
        first = income_builder.opportunities[0]
        print(f"   First: {first.title}")

except ImportError as e:
    print(f"❌ Import failed: {e}")

    # Try alternative import
    try:
        from backend.intelligence.income_builder import income_builder
        print("✅ Alternative import worked: backend.intelligence.income_builder")
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")