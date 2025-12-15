#!/usr/bin/env python
"""
Meta/Threads OAuth Setup Script
================================

This script helps you obtain access tokens for the Threads API.

Usage:
    1. Run this script: python scripts/meta_oauth_setup.py
    2. Open the URL it prints in your browser
    3. Authorize the app on Threads
    4. Copy the 'code' parameter from the redirect URL
    5. Paste it when prompted
    6. The script will exchange it for access tokens
"""

import os
import sys
import requests
from urllib.parse import urlencode, urlparse, parse_qs

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration - Use THREADS-specific credentials (different from META_APP_ID!)
# These are found in: Meta Developer Portal > Your App > Threads API > Settings
THREADS_APP_ID = os.getenv('THREADS_APP_ID') or os.getenv('META_APP_ID')
THREADS_APP_SECRET = os.getenv('THREADS_APP_SECRET') or os.getenv('META_APP_SECRET')
REDIRECT_URI = 'https://localhost:8000/api/meta/callback/'  # Must match Threads App settings

# Threads API scopes
SCOPES = [
    'threads_basic',           # Read profile and posts
    'threads_content_publish', # Publish content
    'threads_manage_insights', # Access metrics
    'threads_manage_replies',  # Manage replies
]


def get_authorization_url():
    """Generate the OAuth authorization URL for Threads"""
    base_url = 'https://threads.net/oauth/authorize'
    params = {
        'client_id': THREADS_APP_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ','.join(SCOPES),
        'response_type': 'code',
        'state': 'threads_auth',  # CSRF protection
    }
    return f"{base_url}?{urlencode(params)}"


def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_url = 'https://graph.threads.net/oauth/access_token'

    data = {
        'client_id': THREADS_APP_ID,
        'client_secret': THREADS_APP_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': code,
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def get_long_lived_token(short_lived_token):
    """Exchange short-lived token for long-lived token (60 days)"""
    url = 'https://graph.threads.net/access_token'
    params = {
        'grant_type': 'th_exchange_token',
        'client_secret': THREADS_APP_SECRET,
        'access_token': short_lived_token,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting long-lived token: {response.status_code}")
        print(response.text)
        return None


def get_user_profile(access_token):
    """Fetch the authenticated user's Threads profile"""
    url = 'https://graph.threads.net/v1.0/me'
    params = {
        'fields': 'id,username,name,threads_profile_picture_url,threads_biography',
        'access_token': access_token,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching profile: {response.status_code}")
        print(response.text)
        return None


def main():
    print("=" * 60)
    print("Meta/Threads OAuth Setup")
    print("=" * 60)

    if not THREADS_APP_ID or not THREADS_APP_SECRET:
        print("\nError: THREADS_APP_ID and THREADS_APP_SECRET must be set in .env")
        print("Get these from: Meta Developer Portal > Your App > Threads API > Settings")
        print("Note: These are DIFFERENT from META_APP_ID/META_APP_SECRET!")
        return

    print(f"\nThreads App ID: {THREADS_APP_ID[:10]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Scopes: {', '.join(SCOPES)}")

    print("\n" + "-" * 60)
    print("IMPORTANT: Before continuing, make sure you've configured:")
    print("1. Your Meta App at developers.facebook.com/apps")
    print("2. Added 'Threads API' product to your app")
    print("3. In Threads API > Settings, set Redirect URI to:", REDIRECT_URI)
    print("4. Added THREADS_APP_ID and THREADS_APP_SECRET to .env")
    print("   (Found in Threads API > Settings, NOT the main App Settings!)")
    print("-" * 60)

    input("\nPress Enter when ready to continue...")

    # Step 1: Generate authorization URL
    auth_url = get_authorization_url()
    print("\n" + "=" * 60)
    print("STEP 1: Open this URL in your browser:")
    print("=" * 60)
    print(f"\n{auth_url}\n")

    # Step 2: Get the authorization code
    print("=" * 60)
    print("STEP 2: After authorizing, you'll be redirected to a URL like:")
    print(f"{REDIRECT_URI}?code=XXXXXX&state=threads_auth")
    print("=" * 60)

    code_input = input("\nPaste the FULL redirect URL (or just the code): ").strip()

    # Extract code if full URL was pasted
    if 'code=' in code_input:
        parsed = urlparse(code_input)
        params = parse_qs(parsed.query)
        code = params.get('code', [code_input])[0]
    else:
        code = code_input

    if not code:
        print("No code provided. Exiting.")
        return

    # Step 3: Exchange code for token
    print("\n" + "=" * 60)
    print("STEP 3: Exchanging code for access token...")
    print("=" * 60)

    token_data = exchange_code_for_token(code)

    if not token_data:
        print("Failed to get access token.")
        return

    short_lived_token = token_data.get('access_token')
    user_id = token_data.get('user_id')

    print(f"\nShort-lived token obtained!")
    print(f"User ID: {user_id}")

    # Step 4: Get long-lived token
    print("\n" + "=" * 60)
    print("STEP 4: Getting long-lived token (60 days)...")
    print("=" * 60)

    long_lived_data = get_long_lived_token(short_lived_token)

    if long_lived_data:
        long_lived_token = long_lived_data.get('access_token')
        expires_in = long_lived_data.get('expires_in', 0)
        days = expires_in // 86400

        print(f"\nLong-lived token obtained!")
        print(f"Expires in: {days} days")
    else:
        long_lived_token = short_lived_token
        print("\nUsing short-lived token (may expire in 1 hour)")

    # Step 5: Test the token
    print("\n" + "=" * 60)
    print("STEP 5: Testing token by fetching your profile...")
    print("=" * 60)

    profile = get_user_profile(long_lived_token)

    if profile:
        print(f"\nSuccess! Connected as:")
        print(f"  Username: @{profile.get('username', 'N/A')}")
        print(f"  Name: {profile.get('name', 'N/A')}")
        print(f"  User ID: {profile.get('id', 'N/A')}")

    # Output the values to add to .env
    print("\n" + "=" * 60)
    print("ADD THESE TO YOUR .env FILE:")
    print("=" * 60)
    print(f'\nTHREADS_ACCESS_TOKEN="{long_lived_token}"')
    print(f'THREADS_USER_ID="{user_id}"')

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
