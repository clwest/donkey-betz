#!/usr/bin/env python
"""
Test the UI orchestration endpoint with real-time odds
"""

import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from sports.models import Game

# Get Wisconsin @ Alabama game
game = Game.objects.filter(
    home_team__name__icontains='Alabama',
    away_team__name__icontains='Wisconsin'
).first()

if not game:
    print("❌ Game not found!")
    exit(1)

print(f"\n{'='*70}")
print(f"🎯 TESTING UI ORCHESTRATION ENDPOINT")
print(f"   {game.away_team.name} @ {game.home_team.name}")
print(f"{'='*70}\n")

# Test the orchestration endpoint
url = "http://localhost:8000/api/odds/orchestrate/"
payload = {
    "game_id": str(game.id),
    "home_team": game.home_team.name,
    "away_team": game.away_team.name,
    "league": "NCAAF",
    "subscription_tier": "premium",
    "selected_agents": ["odds-calculation-agent", "kelly-bet-sizing-agent"]
}

print(f"📡 POST {url}")
print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")

try:
    response = requests.post(url, json=payload)
    
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ SUCCESS! Orchestration initiated")
            print(f"   Task ID: {data.get('task_id', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            
            # Check if it's async
            if data.get('task_id'):
                print(f"\n💡 Agents are being processed asynchronously")
                print(f"   Monitor WebSocket at: {data.get('websocket_channel', 'N/A')}")
        else:
            print(f"⚠️ Orchestration failed: {data.get('error', 'Unknown error')}")
            if 'fallback' in data:
                print(f"   Fallback available: {data['fallback']}")
    else:
        print(f"❌ Request failed")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Error calling endpoint: {e}")

print(f"\n{'='*70}")
print(f"📌 WHAT THIS MEANS:")
print(f"{'='*70}")
print(f"If successful, the UI 'Run Agents' button should now:")
print(f"1. Fetch real odds from the database")
print(f"2. Pass Alabama -16.5, O/U 54.5, ML -650/+475 to agents")
print(f"3. Agents provide specific betting analysis")
print(f"{'='*70}\n")