#!/usr/bin/env python
"""
Test script to verify all new sports pages are accessible
"""
import requests
import sys

BASE_URL = 'http://localhost:8000'

pages = [
    ('Sports Hub', '/sports/'),
    ('Betting History', '/sports/betting-history/'),
    ('Odds Calculator', '/sports/odds-calculator/'),
    ('Live Scores', '/sports/live-scores/'),
]

print("Testing Sports Hub Pages...")
print("=" * 60)

all_passed = True

for page_name, url in pages:
    full_url = BASE_URL + url
    try:
        response = requests.get(full_url, timeout=5)
        status = "✓ PASS" if response.status_code == 200 else f"✗ FAIL (Status: {response.status_code})"

        if response.status_code != 200:
            all_passed = False

        print(f"{page_name:20} {full_url:40} {status}")

        # Check for key elements
        if response.status_code == 200:
            if 'Sports Hub' in page_name and 'AI Predictions' in response.text:
                print(f"  → Contains AI Predictions section")
            elif 'Betting History' in page_name and 'Betting History' in response.text:
                print(f"  → Contains betting history content")
            elif 'Odds Calculator' in page_name and 'Odds Converter' in response.text:
                print(f"  → Contains odds calculator tools")
            elif 'Live Scores' in page_name and 'Live Scores' in response.text:
                print(f"  → Contains live scores content")

    except requests.exceptions.ConnectionError:
        print(f"{page_name:20} {full_url:40} ✗ FAIL (Server not responding)")
        all_passed = False
    except Exception as e:
        print(f"{page_name:20} {full_url:40} ✗ FAIL ({str(e)})")
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("✓ All pages are accessible!")
    sys.exit(0)
else:
    print("✗ Some pages failed to load")
    sys.exit(1)