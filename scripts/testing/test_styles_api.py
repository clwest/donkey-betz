#!/usr/bin/env python
"""
Test the /api/v1/styles/ endpoint
"""

import os
import sys
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

# Get or create a test user and token
User = get_user_model()
# Use first existing user or create one
try:
    user = User.objects.filter(email='test@example.com').first()
    if not user:
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            is_active=True
        )
except:
    # Fallback to any active user
    user = User.objects.filter(is_active=True).first()

token, _ = Token.objects.get_or_create(user=user)

print("\n" + "🎨"*30)
print("TESTING /api/v1/styles/ ENDPOINT")
print("🎨"*30)
print(f"\nUsing token: {token.key[:20]}...")

# Make request to styles endpoint
url = 'http://localhost:8000/api/v1/styles/'
headers = {
    'Authorization': f'Token {token.key}',
    'Content-Type': 'application/json'
}

try:
    response = requests.get(url, headers=headers)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # Display summary
        print("\n✅ SUCCESS! Styles loaded from API")
        print("="*60)

        total_styles = data.get('total_styles', 0)
        provider = data.get('provider', 'Unknown')
        message = data.get('message', '')

        print(f"Total Styles: {total_styles}")
        print(f"Provider: {provider}")
        print(f"Message: {message}")

        # Display categories and style counts
        categories = data.get('categories', {})
        if categories:
            print(f"\n📁 Categories ({len(categories)}):")
            print("-"*40)
            for category, styles in categories.items():
                print(f"  {category}: {len(styles)} styles")
                # Show first 3 styles as examples
                for i, style in enumerate(styles[:3], 1):
                    print(f"    {i}. {style['name']} (id: {style['id']})")
                if len(styles) > 3:
                    print(f"    ... and {len(styles) - 3} more")

        print("\n" + "="*60)
        print(f"🎉 Frontend can now access {total_styles} Stable Diffusion styles!")

    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")

except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to server at localhost:8000")
    print("Make sure the Django server is running: python manage.py runserver")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n✨ To test in frontend:")
print("1. Open http://localhost:3000/studio/image")
print("2. Check if style dropdown shows all 70+ styles")
print("3. Try generating an image with different styles")