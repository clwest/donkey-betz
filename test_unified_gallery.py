#!/usr/bin/env python3
"""
Test script for Unified Gallery API
Session 53 - Phase 2
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from content.models import ImageHistory, VideoHistory
import json

User = get_user_model()

def test_unified_gallery():
    """Test the unified gallery API endpoint"""

    # Get or create admin user
    try:
        user = User.objects.get(username='admin')
        print(f"✅ Using existing admin user: {user.username}")
    except User.DoesNotExist:
        print("❌ Admin user not found. Please create one first.")
        return

    # Create test client and login using session authentication
    client = Client()
    client.force_login(user)  # This sets session authentication that middleware recognizes

    print("\n📊 Testing Unified Gallery API...\n")

    # Test 1: Get all content
    print("Test 1: Get all content (images + videos)")
    response = client.get('/api/v1/gallery/all/', {'type': 'all', 'limit': 5})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Total count: {data['count']}")
        print(f"✅ Results returned: {len(data['results'])}")
        if data['results']:
            first = data['results'][0]
            print(f"✅ First item type: {first['type']}")
            print(f"✅ First item prompt: {first['prompt'][:50]}...")
    else:
        print(f"❌ Error: {json.loads(response.content)}")

    # Test 2: Get only images
    print("\n\nTest 2: Get only images")
    response = client.get('/api/v1/gallery/all/', {'type': 'images', 'limit': 5})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Total images: {data['count']}")
        print(f"✅ Results returned: {len(data['results'])}")
        if data['results']:
            types = [item['type'] for item in data['results']]
            print(f"✅ All types are 'image': {all(t == 'image' for t in types)}")
    else:
        print(f"❌ Error: {json.loads(response.content)}")

    # Test 3: Get only videos
    print("\n\nTest 3: Get only videos")
    response = client.get('/api/v1/gallery/all/', {'type': 'videos', 'limit': 5})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Total videos: {data['count']}")
        print(f"✅ Results returned: {len(data['results'])}")
        if data['results']:
            types = [item['type'] for item in data['results']]
            print(f"✅ All types are 'video': {all(t == 'video' for t in types)}")
    else:
        print(f"❌ Error: {json.loads(response.content)}")

    # Test 4: Search by prompt
    print("\n\nTest 4: Search by prompt")
    response = client.get('/api/v1/gallery/all/', {'type': 'all', 'search': 'donkey', 'limit': 5})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Search results: {data['count']}")
        if data['results']:
            print(f"✅ First result prompt: {data['results'][0]['prompt'][:80]}...")
    else:
        print(f"❌ Error: {json.loads(response.content)}")

    # Test 5: Filter favorites
    print("\n\nTest 5: Filter favorites only")
    response = client.get('/api/v1/gallery/all/', {'type': 'all', 'favorite': 'true', 'limit': 5})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Total favorites: {data['count']}")
        if data['results']:
            all_favorites = all(item['is_favorite'] for item in data['results'])
            print(f"✅ All results are favorites: {all_favorites}")
    else:
        print(f"❌ Error: {json.loads(response.content)}")

    # Test 6: Pagination
    print("\n\nTest 6: Pagination")
    response = client.get('/api/v1/gallery/all/', {'type': 'all', 'limit': 2, 'offset': 0})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Has next page: {data['next'] is not None}")
        print(f"✅ Has previous page: {data['previous'] is not None}")
    else:
        print(f"❌ Error: {json.loads(response.content)}")

    print("\n\n" + "="*60)
    print("🎉 Unified Gallery API Testing Complete!")
    print("="*60)

if __name__ == '__main__':
    test_unified_gallery()
