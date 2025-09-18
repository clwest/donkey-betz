#!/usr/bin/env python
"""Simple test for content API"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from content.models import ContentGeneration

User = get_user_model()

# Create test user
user, _ = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)

# Get or create token
token, _ = Token.objects.get_or_create(user=user)
print(f"Using token: {token.key}")

# Create API client
client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

# Test the endpoint
response = client.post('/api/v1/content/create/', {
    'content_type': 'image',
    'prompt': 'A beautiful sunset',
    'style': 'photographic',
    'size': '1024x1024'
}, format='json')

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200 or response.status_code == 201:
    data = response.json()
    print("✅ Success!")
    print(f"Response keys: {data.keys()}")

    if 'content' in data:
        content = data['content']
        print(f"Content type: {content.get('type')}")

        if 'images' in content:
            images = content['images']
            print(f"Images generated: {len(images)}")
            if images:
                print(f"First image URL: {images[0].get('url', 'No URL')[:100]}")

        if 'metadata' in content:
            print(f"Metadata: {content['metadata']}")
else:
    print(f"❌ Failed!")
    print(f"Response: {response.content.decode()[:500]}")

# Check database
generations = ContentGeneration.objects.filter(user=user).order_by('-created_at')[:5]
print(f"\nDatabase records for user: {generations.count()}")
for gen in generations:
    print(f"  - {gen.prompt[:50]} | Status: {gen.status} | Created: {gen.created_at}")