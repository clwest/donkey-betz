#!/usr/bin/env python
"""Debug content creation error"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from core.views_content import create_content
import json

User = get_user_model()

# Get or create test user
user, _ = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)

# Create a mock request
factory = RequestFactory()
request = factory.post('/api/v1/content/create/',
    data=json.dumps({
        'content_type': 'image',
        'prompt': 'Test image',
        'style': 'digital-art',
        'size': '1024x1024'
    }),
    content_type='application/json'
)

# Add user to request
request.user = user
request.data = {
    'content_type': 'image',
    'prompt': 'Test image',
    'style': 'digital-art',
    'size': '1024x1024',
    'batch_size': 1,
    'quality': 'standard'
}

# Try to execute the view
try:
    response = create_content(request)
    print(f"Success! Status: {response.status_code}")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()