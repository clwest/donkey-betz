#!/usr/bin/env python
"""Step 1: Generate Threads OAuth URL - Open this in your browser"""

import os
import sys
from urllib.parse import urlencode

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

THREADS_APP_ID = os.getenv('THREADS_APP_ID')
REDIRECT_URI = 'https://localhost:8000/api/meta/callback/'

SCOPES = [
    'threads_basic',
    'threads_content_publish',
    'threads_manage_insights',
    'threads_manage_replies',
]

base_url = 'https://threads.net/oauth/authorize'
params = {
    'client_id': THREADS_APP_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': ','.join(SCOPES),
    'response_type': 'code',
    'state': 'threads_auth',
}

auth_url = f"{base_url}?{urlencode(params)}"

print("=" * 70)
print("STEP 1: Open this URL in your browser:")
print("=" * 70)
print()
print(auth_url)
print()
print("=" * 70)
print("After authorizing, you'll be redirected to a URL like:")
print(f"{REDIRECT_URI}?code=XXXXXX#_")
print()
print("Copy the 'code' value and run:")
print("  .venv/bin/python scripts/threads_exchange_code.py YOUR_CODE_HERE")
print("=" * 70)
