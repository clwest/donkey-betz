#!/usr/bin/env python3
"""
Check if images/videos have agent field populated
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, VideoHistory
from core.models.agents_registry import AgentContribution
from django.contrib.auth import get_user_model

User = get_user_model()

def check_agent_assignments():
    print("=" * 80)
    print("🔍 Checking Agent Assignments")
    print("=" * 80)
    print()

    # Get user
    user = User.objects.get(username='admin')

    # Check images
    images = ImageHistory.objects.filter(user=user).order_by('-created_at')[:10]
    print(f"📸 Last 10 Images:")
    print()

    for img in images:
        print(f"   Image #{img.get_sequential_number()}")
        print(f"   - ID: {img.id}")
        print(f"   - Type: {img.image_type}")
        print(f"   - Project: {img.project.name if img.project else 'None'}")
        print(f"   - Agent (FK): {img.agent.display_name if img.agent else 'None'}")
        print()

    # Check videos
    videos = VideoHistory.objects.filter(user=user).order_by('-created_at')[:10]
    print(f"🎬 Last 10 Videos:")
    print()

    for video in videos:
        print(f"   Video #{video.get_sequential_number()}")
        print(f"   - ID: {video.id}")
        print(f"   - Status: {video.status}")
        print(f"   - Project: {video.project.name if video.project else 'None'}")
        print(f"   - Agent (FK): {video.agent.display_name if video.agent else 'None'}")
        print()

    # Check contributions
    contributions = AgentContribution.objects.filter(project__user=user).count()
    print("=" * 80)
    print(f"📊 Total AgentContributions: {contributions}")
    print("=" * 80)

if __name__ == "__main__":
    check_agent_assignments()
