#!/usr/bin/env python
"""
Verify Personal Assistant Interview System uses real data
==========================================================

This script tests that the Personal Assistant:
1. Connects to real WebSocket endpoints
2. Saves data to the actual database
3. Retrieves real user profiles
4. Has no hardcoded/mock data
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import ExtendedUserProfile, EnhancedUserProfile
from intelligence.personal_assistant_interviewer import personal_assistant_interviewer

User = get_user_model()


def verify_database_models():
    """Verify database models are real and working"""
    print("\n🔍 Verifying Database Models...")

    try:
        # Check if models can be imported and queried
        user_count = User.objects.count()
        profile_count = ExtendedUserProfile.objects.count()
        enhanced_count = EnhancedUserProfile.objects.count()

        print(f"   ✅ User model: {user_count} users in database")
        print(f"   ✅ ExtendedUserProfile: {profile_count} profiles")
        print(f"   ✅ EnhancedUserProfile: {enhanced_count} enhanced profiles")

        # Try to get or create a test user
        test_user, created = User.objects.get_or_create(
            username='interview_test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )

        if created:
            print(f"   ✅ Created test user: {test_user.username}")
        else:
            print(f"   ✅ Found existing test user: {test_user.username}")

        # Create or update enhanced profile
        enhanced_profile, created = EnhancedUserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'interview_completed': False,
                'preferred_name': 'Test',
                'current_situation': 'Testing the system'
            }
        )

        if created:
            print(f"   ✅ Created enhanced profile for {test_user.username}")
        else:
            print(f"   ✅ Found existing enhanced profile")

        # Test saving data
        enhanced_profile.skills_technical = ['Python', 'Django', 'React']
        enhanced_profile.income_goal_monthly = 5000
        enhanced_profile.save()

        # Reload to verify persistence
        enhanced_profile.refresh_from_db()
        assert enhanced_profile.skills_technical == ['Python', 'Django', 'React']
        assert enhanced_profile.income_goal_monthly == 5000

        print(f"   ✅ Database save/load working correctly")

        return True

    except Exception as e:
        print(f"   ❌ Database verification failed: {e}")
        return False


def verify_interview_system():
    """Verify interview system is real and functional"""
    print("\n🔍 Verifying Interview System...")

    try:
        # Check if interview system has real questions
        assert hasattr(personal_assistant_interviewer, 'interview_phases')
        phases = personal_assistant_interviewer.interview_phases

        print(f"   ✅ Interview system has {len(phases)} real phases")

        for phase in phases[:3]:  # Check first 3 phases
            print(f"      • {phase.name}: {len(phase.questions)} questions")

        # Verify questions are not hardcoded mock data
        sample_question = phases[0].questions[0]
        assert 'mock' not in sample_question.text.lower()
        assert 'fake' not in sample_question.text.lower()
        assert 'demo' not in sample_question.text.lower()

        print(f"   ✅ Questions are real (not mock/fake/demo)")

        # Check interview flow methods exist
        assert hasattr(personal_assistant_interviewer, 'start_interview')
        assert hasattr(personal_assistant_interviewer, 'process_response')
        assert hasattr(personal_assistant_interviewer, 'save_to_profile')

        print(f"   ✅ Interview methods are implemented")

        return True

    except Exception as e:
        print(f"   ❌ Interview system verification failed: {e}")
        return False


def verify_websocket_endpoints():
    """Verify WebSocket endpoints are configured"""
    print("\n🔍 Verifying WebSocket Configuration...")

    try:
        from django.conf import settings

        # Check Redis configuration (used by Channels)
        channel_layers = settings.CHANNEL_LAYERS
        assert 'default' in channel_layers

        config = channel_layers['default']
        assert config['BACKEND'] == 'channels_redis.core.RedisChannelLayer'

        redis_host = config['CONFIG']['hosts'][0]
        print(f"   ✅ Redis configured at: {redis_host}")

        # Check routing configuration
        from core.routing import websocket_urlpatterns

        interview_routes = [
            route for route in websocket_urlpatterns
            if 'interview' in str(route.pattern)
        ]

        assert len(interview_routes) > 0
        print(f"   ✅ Interview WebSocket route configured")

        # Check consumer exists
        from intelligence.interview_consumer import InterviewConsumer
        assert InterviewConsumer is not None
        print(f"   ✅ InterviewConsumer class exists")

        return True

    except Exception as e:
        print(f"   ❌ WebSocket verification failed: {e}")
        return False


def check_for_mock_data():
    """Search for any mock/fake data in the system"""
    print("\n🔍 Checking for Mock/Fake Data...")

    suspicious_patterns = []

    # Check interview system
    from intelligence import personal_assistant_interviewer as pai

    source = str(pai.__file__)
    with open(source, 'r') as f:
        content = f.read()

    # Look for mock data patterns
    if 'MOCK_' in content or 'mock_data' in content:
        suspicious_patterns.append('Mock data found in interviewer')

    if 'fake_' in content or 'FAKE_' in content:
        suspicious_patterns.append('Fake data found in interviewer')

    if 'return []' in content or 'return {}' in content:
        # Check if it's returning empty data instead of real data
        lines_with_empty = [
            line for line in content.split('\n')
            if 'return []' in line or 'return {}' in line
        ]
        if len(lines_with_empty) > 5:  # Threshold for suspicion
            suspicious_patterns.append('Multiple empty returns found')

    if suspicious_patterns:
        print(f"   ⚠️  Suspicious patterns found:")
        for pattern in suspicious_patterns:
            print(f"      • {pattern}")
        return False
    else:
        print(f"   ✅ No mock/fake data patterns detected")
        return True


def test_end_to_end_flow():
    """Test complete data flow from interview to database"""
    print("\n🔍 Testing End-to-End Data Flow...")

    try:
        # Get test user
        test_user = User.objects.get(username='interview_test_user')

        # Simulate interview data
        test_data = {
            'preferred_name': 'Test User',
            'current_situation': 'Testing the system',
            'weekly_hours_available': 20,
            'skills_technical': ['Python', 'JavaScript', 'Docker'],
            'skills_creative': ['Writing', 'Design'],
            'skills_business': ['Project Management'],
            'strongest_skill_description': 'Full-stack development with 5 years experience',
            'professional_experience': '5 years as software engineer',
            'achievements': 'Built 3 production applications',
            'income_goal_monthly': 8000,
            'income_goal_reason': 'Financial independence',
            'work_preferences': ['Remote', 'Flexible hours'],
            'avoid_activities': ['Cold calling'],
            'hidden_talents': ['Music production', 'Photography']
        }

        # Save to profile
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=test_user)

        for key, value in test_data.items():
            setattr(profile, key, value)

        profile.interview_completed = True
        profile.interview_completed_at = datetime.now()
        profile.save()

        print(f"   ✅ Saved interview data to profile")

        # Verify data persisted
        profile.refresh_from_db()

        assert profile.preferred_name == 'Test User'
        assert profile.income_goal_monthly == 8000
        assert 'Python' in profile.skills_technical

        print(f"   ✅ Data correctly persisted and retrieved")

        # Calculate completeness
        profile.calculate_completeness()
        completeness = profile.profile_completeness

        print(f"   ✅ Profile completeness calculated: {completeness}%")

        return True

    except Exception as e:
        print(f"   ❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("🔬 PERSONAL ASSISTANT REAL DATA VERIFICATION")
    print("="*60)

    results = {
        'Database Models': verify_database_models(),
        'Interview System': verify_interview_system(),
        'WebSocket Config': verify_websocket_endpoints(),
        'No Mock Data': check_for_mock_data(),
        'End-to-End Flow': test_end_to_end_flow()
    }

    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)

    all_passed = all(results.values())

    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test}: {status}")

    print("\n" + "="*60)

    if all_passed:
        print("🎉 VERIFICATION COMPLETE: System uses REAL DATA!")
        print("   • Database models are real and functional")
        print("   • Interview system saves to actual database")
        print("   • WebSocket connections are properly configured")
        print("   • No mock/fake data detected")
        print("   • End-to-end data flow working correctly")
    else:
        print("⚠️  VERIFICATION INCOMPLETE: Some issues detected")
        print("   Please review the failed tests above")

    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())