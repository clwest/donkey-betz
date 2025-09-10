#!/usr/bin/env python
"""
Create a test user with a valid auth token for development
"""

import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

def create_test_users():
    """Create test users with auth tokens"""
    
    test_users = [
        {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        },
        {
            'username': 'demo',
            'email': 'demo@example.com',
            'password': 'demo123',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    ]
    
    print("Creating test users...")
    print("=" * 60)
    
    for user_data in test_users:
        username = user_data['username']
        password = user_data.pop('password')
        
        # Check if user exists
        user, created = User.objects.get_or_create(
            username=username,
            defaults=user_data
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Created user: {username}")
        else:
            # Update password for existing user
            user.set_password(password)
            user.save()
            print(f"✅ Updated user: {username}")
        
        # Get or create token
        token, token_created = Token.objects.get_or_create(user=user)
        
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Token: {token.key}")
        print(f"   Email: {user.email}")
        print("-" * 60)
    
    print("\n📝 To use in the frontend:")
    print("1. Go to http://localhost:3000/login")
    print("2. Use one of the above username/password combinations")
    print("3. The system will automatically get and store the auth token")
    
    print("\n🔧 Or manually set a token in browser console:")
    print("localStorage.setItem('authToken', '<token-from-above>');")
    print("window.location.reload();")

if __name__ == "__main__":
    create_test_users()