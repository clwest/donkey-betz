#!/usr/bin/env python3
"""
Test trigger word matching in TrainedCreationAgent - Session 134
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.agents.training import TrainedCreationAgent

User = get_user_model()

def test_trigger_word_resolution():
    """Test that trigger words are matched correctly."""
    print("=" * 80)
    print("🧪 Testing Trigger Word Resolution - Session 134")
    print("=" * 80)

    user = User.objects.get(username='admin')
    agent = TrainedCreationAgent(user=user, project_id=None)

    test_cases = [
        # Exact match (should work - existing logic)
        "ai-content-generation-company-style",

        # Trigger word variations (should work - new logic)
        "AI-CONTENT-GENERATION-COMPANY-STYLE",
        "ai content generation company style",
        "AI CONTENT GENERATION COMPANY STYLE",
        "aicontentgenerationcompanystyle",
        "AICONTENTGENERATIONCOMPANYSTYLE",

        # Should NOT match
        "wrong-model-name",
        "some-other-style"
    ]

    print(f"\n✅ User: {user.username}")
    print(f"\n📊 Testing {len(test_cases)} variations:\n")

    for i, identifier in enumerate(test_cases, 1):
        print(f"{i}. Testing: '{identifier}'")
        model = agent._resolve_character_model(identifier)

        if model:
            print(f"   ✅ MATCH → {model.name} (trigger: {model.trigger_word})")
        else:
            print(f"   ❌ NO MATCH")
        print()

    print("=" * 80)

if __name__ == "__main__":
    test_trigger_word_resolution()
