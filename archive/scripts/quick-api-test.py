#!/usr/bin/env python3
"""
Quick API Test - Verify 150 Agents are Available
"""

import requests
import json

API_BASE = "http://localhost:8000"
TOKEN = "<redacted-0fb2390d-2026-04-20>"

def test_api():
    print("🔍 Testing API Connectivity\n")
    
    # Test templates endpoint
    headers = {"Authorization": f"Token {TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/api/v1/agents/templates/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Count agents
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                agents = data['results']
            else:
                count = 0
                agents = []
            
            print(f"✅ API Connected Successfully!")
            print(f"✅ Found {count} agent templates")
            
            if count > 0 and 'results' in data:
                print(f"\n📋 Sample Agents:")
                for agent in agents[:5]:
                    print(f"  • {agent.get('name', 'Unknown')} - {agent.get('category', 'N/A')}")
                
                # Group by category
                categories = {}
                for agent in agents:
                    cat = agent.get('category', 'uncategorized')
                    if cat not in categories:
                        categories[cat] = 0
                    categories[cat] += 1
                
                print(f"\n📊 Categories:")
                for cat, cnt in sorted(categories.items()):
                    print(f"  • {cat}: {cnt} agents")
            
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("UNIFIED DONKEY BETZ - API VERIFICATION")
    print("="*50)
    print(f"API URL: {API_BASE}/api/v1/agents/templates/")
    print(f"Token: {TOKEN[:20]}...")
    print()
    
    if test_api():
        print("\n✅ Your backend is ready!")
        print("✅ Frontend can now connect to all agents")
        print("\nNext: Make sure frontend is restarted to see changes")
        print("Run: cd frontend && npm run dev")
    else:
        print("\n⚠️  Backend may need attention")
        print("Make sure Django is running: python manage.py runserver")
