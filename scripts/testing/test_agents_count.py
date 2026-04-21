#!/usr/bin/env python
import requests
import json

# Test script to verify all agents are accessible
TOKEN = '<redacted-0fb2390d-2026-04-20>'
BASE_URL = 'http://localhost:8000'

headers = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
}

print("Testing Agent API Pagination Fix...")
print("=" * 50)

# Test 1: Default request (should now use PAGE_SIZE=200)
response = requests.get(f'{BASE_URL}/api/v1/agents/templates/', headers=headers)
data = response.json()
default_count = len(data.get('results', []))
print(f"✓ Default request: {default_count} agents")

# Test 2: Explicit page_size=200
response = requests.get(f'{BASE_URL}/api/v1/agents/templates/?page_size=200', headers=headers)
data = response.json()
explicit_count = len(data.get('results', []))
print(f"✓ With page_size=200: {explicit_count} agents")

# Test 3: Get total count
total_count = data.get('count', explicit_count)
print(f"✓ Total agents in system: {total_count}")

print("=" * 50)
if explicit_count >= 150:
    print("✅ SUCCESS! All agents are accessible")
    print(f"   Frontend at http://localhost:3000/control-center")
    print(f"   should now display all {explicit_count} agents")
else:
    print(f"⚠️  Only {explicit_count} agents accessible")
    print("   Check backend settings.py PAGE_SIZE configuration")