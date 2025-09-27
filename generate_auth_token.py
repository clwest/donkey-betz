#!/usr/bin/env python3
"""
Generate Authentication Token
=============================
Utility to generate authentication tokens for API access
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


def create_user_and_token(username='api_user', email='api@localhost', is_staff=False):
    """Create a user and generate an authentication token"""

    # Check if user exists
    user = User.objects.filter(username=username).first()

    if not user:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password='<your-secure-password>',
            is_staff=is_staff,
            is_active=True
        )
        print(f"✅ Created new user: {username}")
    else:
        print(f"ℹ️  Using existing user: {username}")

    # Get or create token
    token, created = Token.objects.get_or_create(user=user)

    if created:
        print(f"✅ Created new token for {username}")
    else:
        print(f"ℹ️  Using existing token for {username}")

    return user, token


def main():
    print("\n" + "="*60)
    print("🔐 AUTHENTICATION TOKEN GENERATOR")
    print("="*60 + "\n")

    # Create regular user
    user, token = create_user_and_token(
        username='api_user',
        email='api@localhost',
        is_staff=False
    )

    print("\n📋 Regular User Credentials:")
    print("-" * 40)
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Token: {token.key}")
    print(f"Is Staff: {user.is_staff}")

    # Create admin user
    admin_user, admin_token = create_user_and_token(
        username='admin_api_user',
        email='admin_api@localhost',
        is_staff=True
    )

    print("\n📋 Admin User Credentials:")
    print("-" * 40)
    print(f"Username: {admin_user.username}")
    print(f"Email: {admin_user.email}")
    print(f"Token: {admin_token.key}")
    print(f"Is Staff: {admin_user.is_staff}")

    print("\n" + "="*60)
    print("🚀 HOW TO USE THE TOKENS:")
    print("="*60)

    print("\n1. Using curl:")
    print(f'   curl -H "Authorization: Token {token.key}" http://localhost:8000/api/v1/status/')

    print("\n2. Using Python requests:")
    print(f"""   import requests
   headers = {{'Authorization': 'Token {token.key}'}}
   response = requests.get('http://localhost:8000/api/v1/status/', headers=headers)""")

    print("\n3. For WebSocket connections:")
    print(f"   ws://localhost:8000/ws/intelligence/?token={token.key}")

    print("\n4. As a query parameter (less secure, for testing only):")
    print(f"   http://localhost:8000/api/v1/status/?token={token.key}")

    print("\n" + "="*60)
    print("✅ Tokens ready for use!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()