# tests/unit/test_betting_page.py
"""
Test betting page endpoints.

NOTE: This requires a live server. Run with:
    TOKEN=your-token pytest tests/unit/test_betting_page.py

Skipped by default in pytest runs.
"""
import os
import pytest
import requests

pytestmark = pytest.mark.skip(reason="Integration test requiring live server - run manually with TOKEN env var")

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")

ENDPOINTS = [
    ("/sports/", "Sports Hub"),
    ("/sports/betting-history/", "Betting History"),
    ("/sports/odds-calculator/", "Odds Calculator"),
    ("/sports/live-scores/", "Live Scores"),
]

# If your pages need auth, set TOKEN in env before running pytest.
AUTH_HEADER = (
    {"Authorization": f"Token {os.environ.get('TOKEN', 'test-token')}"}
    if os.environ.get("TOKEN")
    else {}
)

@pytest.mark.parametrize("endpoint,description", ENDPOINTS)
def test_endpoint(endpoint, description):
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, headers=AUTH_HEADER, allow_redirects=False, timeout=10)
    # Many Django pages redirect to /login when unauthenticated; accept 200 or 302.
    assert resp.status_code in (200, 302), f"{description} failed: {resp.status_code} for {url}"