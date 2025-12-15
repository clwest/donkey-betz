#!/usr/bin/env python
"""Step 2: Exchange authorization code for access token"""

import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

THREADS_APP_ID = os.getenv('THREADS_APP_ID')
THREADS_APP_SECRET = os.getenv('THREADS_APP_SECRET')
REDIRECT_URI = 'https://localhost:8000/api/meta/callback/'


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
    return response.status_code, response.json() if response.status_code == 200 else response.text


def get_long_lived_token(short_lived_token):
    """Exchange short-lived token for long-lived token (60 days)"""
    url = 'https://graph.threads.net/access_token'
    params = {
        'grant_type': 'th_exchange_token',
        'client_secret': THREADS_APP_SECRET,
        'access_token': short_lived_token,
    }

    response = requests.get(url, params=params)
    return response.status_code, response.json() if response.status_code == 200 else response.text


def get_user_profile(access_token):
    """Fetch the authenticated user's Threads profile"""
    url = 'https://graph.threads.net/v1.0/me'
    params = {
        'fields': 'id,username,name,threads_profile_picture_url,threads_biography',
        'access_token': access_token,
    }

    response = requests.get(url, params=params)
    return response.status_code, response.json() if response.status_code == 200 else response.text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/threads_exchange_code.py <authorization_code>")
        print("\nThe code is from the redirect URL after authorizing.")
        sys.exit(1)

    code = sys.argv[1]

    # Clean up code if full URL was pasted
    if 'code=' in code:
        code = code.split('code=')[1].split('&')[0].split('#')[0]

    print(f"Exchanging code: {code[:20]}...")
    print()

    # Step 1: Exchange code for short-lived token
    status, result = exchange_code_for_token(code)

    if status != 200:
        print(f"Error getting token: {status}")
        print(result)
        sys.exit(1)

    short_token = result.get('access_token')
    user_id = result.get('user_id')
    print(f"Got short-lived token!")
    print(f"User ID: {user_id}")

    # Step 2: Exchange for long-lived token
    print("\nGetting long-lived token (60 days)...")
    status, result = get_long_lived_token(short_token)

    if status == 200:
        long_token = result.get('access_token')
        expires_in = result.get('expires_in', 0)
        print(f"Got long-lived token! Expires in {expires_in // 86400} days")
    else:
        print(f"Could not get long-lived token: {result}")
        long_token = short_token

    # Step 3: Test by fetching profile
    print("\nFetching your Threads profile...")
    status, profile = get_user_profile(long_token)

    if status == 200:
        print(f"\nSuccess! Connected as: @{profile.get('username', 'N/A')}")
        print(f"Name: {profile.get('name', 'N/A')}")
    else:
        print(f"Could not fetch profile: {profile}")

    # Output .env values
    print("\n" + "=" * 70)
    print("ADD THESE TO YOUR .env FILE:")
    print("=" * 70)
    print(f'THREADS_ACCESS_TOKEN="{long_token}"')
    print(f'THREADS_USER_ID="{user_id}"')
    print("=" * 70)
