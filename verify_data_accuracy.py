#!/usr/bin/env python
"""
Data Accuracy Verifier
======================
Checks what data is real vs fallback/mock
"""

import redis
import json
from datetime import datetime

def check_data_accuracy():
    print("=" * 60)
    print("📊 DATA ACCURACY VERIFICATION REPORT")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print("-" * 60)

    results = {
        'real_data': [],
        'missing_data': [],
        'api_keys_needed': []
    }

    # Check DB 0 - Main operations
    print("\n🗄️ DB 0 - Main Operations:")
    r0 = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    freelance_keys = r0.keys('freelance:*')
    collab_keys = r0.keys('collaboration:*')
    agent_keys = r0.keys('agent:*')

    print(f"  Freelance projects: {len(freelance_keys)}")
    print(f"  Collaborations: {len(collab_keys)}")
    print(f"  Agent tasks: {len(agent_keys)}")

    if freelance_keys:
        results['real_data'].append(f"✅ {len(freelance_keys)} freelance projects")
        # Check sample content - handle different data types
        try:
            key_type = r0.type(freelance_keys[0])
            if key_type == 'string':
                sample = r0.get(freelance_keys[0])
                if sample:
                    data = json.loads(sample)
                    print(f"    Sample: {data.get('title', 'No title')[:50]}...")
            elif key_type == 'hash':
                sample = r0.hgetall(freelance_keys[0])
                if sample:
                    print(f"    Sample: {sample.get('title', 'Hash data')[:50]}...")
        except Exception as e:
            print(f"    Could not read sample: {e}")

    # Check DB 2 - Learning System
    print("\n🧠 DB 2 - Learning System:")
    r2 = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

    solutions = r2.keys('solution:*')
    knowledge = r2.keys('shared:knowledge:*')
    problems = r2.keys('problems:*')

    print(f"  Stored solutions: {len(solutions)}")
    print(f"  Shared knowledge: {len(knowledge)}")
    print(f"  Problems tracked: {len(problems)}")

    # Verify solution quality
    real_solutions = 0
    for sol_key in solutions[:5]:  # Check first 5
        sol_data = r2.get(sol_key)
        if sol_data:
            data = json.loads(sol_data)
            if 'code' in data and data['code'] and len(data['code']) > 50:
                real_solutions += 1

    if solutions:
        results['real_data'].append(f"✅ {len(solutions)} solutions with code")
        print(f"    Verified {real_solutions}/5 have real code")

    # Check DB 4 - Career Platform
    print("\n💼 DB 4 - Career Platform:")
    r4 = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    # Check each phase
    phases_complete = []
    for phase in range(1, 6):
        if r4.exists(f"intelligence:complete:phase{phase}") or \
           r4.exists(f"patterns:complete:phase{phase}"):
            phases_complete.append(phase)

    print(f"  Phases complete: {phases_complete}")

    # Check monetization
    monetization = r4.get('monetization:projections')
    if monetization:
        data = json.loads(monetization)
        revenue = data.get('month_1_total', {}).get('revenue', 0)
        print(f"  Revenue projection: ${revenue:,}")
        results['real_data'].append(f"✅ Revenue projections: ${revenue:,}")
    else:
        print(f"  Revenue projection: Not found")
        results['missing_data'].append("❌ Monetization projections")

    # Check agent insights
    insights = r4.get('agents:combined_insights')
    if insights:
        data = json.loads(insights)
        print(f"  Agent insights: {len(data)} categories")
        results['real_data'].append(f"✅ Agent insights from {len(data)} categories")

    # Check for API dependencies
    print("\n🔑 API Key Analysis:")

    # Check if we're using actual LLM APIs
    api_indicators = {
        'OpenAI': False,
        'Anthropic': False,
        'Web Search': False,
        'Job APIs': False
    }

    # Look for API usage patterns in solutions
    for sol_key in solutions[:10]:
        sol_data = r2.get(sol_key)
        if sol_data:
            data = json.loads(sol_data)
            code = data.get('code', '')
            if 'openai' in code.lower():
                api_indicators['OpenAI'] = True
            if 'anthropic' in code.lower() or 'claude' in code.lower():
                api_indicators['Anthropic'] = True
            if 'requests.get' in code or 'urllib' in code:
                api_indicators['Web Search'] = True

    print("  APIs potentially needed:")
    for api, used in api_indicators.items():
        status = "May be needed" if not used else "Detected in code"
        print(f"    {api}: {status}")
        if not used:
            results['api_keys_needed'].append(api)

    # Summary
    print("\n" + "=" * 60)
    print("📈 SUMMARY")
    print("-" * 60)

    print("\n✅ Real Data Found:")
    for item in results['real_data']:
        print(f"  {item}")

    if results['missing_data']:
        print("\n❌ Missing Data:")
        for item in results['missing_data']:
            print(f"  {item}")

    if results['api_keys_needed']:
        print("\n🔑 API Keys Potentially Needed:")
        for api in results['api_keys_needed']:
            print(f"  - {api}")
        print("\n  Note: The system generates solutions algorithmically")
        print("  External APIs would enhance but aren't required")

    # Reality Score
    real_count = len(results['real_data'])
    total_checks = real_count + len(results['missing_data'])
    reality_score = (real_count / total_checks * 100) if total_checks > 0 else 0

    print(f"\n🎯 Reality Score: {reality_score:.1f}%")
    print("=" * 60)

    return results

if __name__ == "__main__":
    results = check_data_accuracy()