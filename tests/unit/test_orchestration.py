# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test the updated orchestration system with real agents
"""

import requests
import json

def test_orchestration():
    url = "http://localhost:8000/api/v1/sports/orchestrate/"
    
    payload = {
        "game_id": "6f15d777-dc29-4f5c-8760-9d41ef16f211",
        "home_team": "Team A",
        "away_team": "Team B", 
        "league": "NCAAF",
        "subscription_tier": "elite",
        "selected_agents": [
            "betting-intelligence-analyzer", 
            "weather-analyzer",
            "injury-analyzer", 
            "market-value-analyzer",
            "kelly-bet-sizing",
            "public-sentiment-analyzer",
            "line-movement-analyzer",
            "arbitrage-hunter",
            "value-betting-agent",
            "contrarian-betting",
            "situational-analyzer",
            "odds-calculation"
        ]
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("🚀 Testing Orchestration Engine...")
    print(f"📊 Request: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print('✅ Orchestration successful!')
                results = data.get('results', {})
                phase_results = results.get('phase_results', {})
                
                print(f'Phases executed: {len(phase_results)}')
                
                for phase, phase_data in phase_results.items():
                    agents_executed = phase_data.get('agents_executed', [])
                    print(f'\n📋 Phase: {phase}')
                    print(f'   Agents: {len(agents_executed)}')
                    
                    for agent in agents_executed:
                        result = phase_data.get('results', {}).get(agent, {})
                        if result.get('success'):
                            print(f'   ✅ {agent}: Success')
                        else:
                            print(f'   ❌ {agent}: Failed - {result.get("error", "Unknown")}')
                
                # Check final recommendation
                final_rec = results.get('final_recommendation', {})
                if final_rec:
                    print(f'\n🎯 Final Recommendation: {final_rec.get("action", "PASS")}')
                    print(f'   Confidence: {final_rec.get("overall_confidence", 0):.1%}')
                    print(f'   Kelly allocation: {final_rec.get("kelly_allocation", "0%")}')
                
                return True
            else:
                print('❌ Orchestration failed:', data.get('message', 'Unknown error'))
                return False
        else:
            print(f'❌ HTTP Error: {response.status_code}')
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print('❌ Request timed out')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    test_orchestration()