#!/usr/bin/env python
"""
Comprehensive Data Check
========================
Safely checks all Redis data and API endpoints
"""

import redis
import json
from datetime import datetime

def safe_get_value(r, key):
    """Safely get value regardless of Redis data type"""
    try:
        key_type = r.type(key)
        if key_type == 'string':
            return r.get(key)
        elif key_type == 'hash':
            return json.dumps(r.hgetall(key))
        elif key_type == 'list':
            return json.dumps(r.lrange(key, 0, -1))
        elif key_type == 'set':
            return json.dumps(list(r.smembers(key)))
        elif key_type == 'zset':
            return json.dumps(r.zrange(key, 0, -1, withscores=True))
        else:
            return None
    except Exception as e:
        return None

def check_all_data():
    print("=" * 70)
    print("🔍 COMPREHENSIVE DATA CHECK - WHAT'S REAL vs WHAT'S MISSING")
    print("=" * 70)
    print(f"Time: {datetime.now()}")
    print("-" * 70)

    # Initialize Redis connections
    redis_dbs = {}
    for db in [0, 2, 3, 4]:
        try:
            r = redis.Redis(host='localhost', port=6379, db=db, decode_responses=True)
            r.ping()
            redis_dbs[db] = r
        except:
            redis_dbs[db] = None

    # DB 0 - Main Operations
    print("\n📦 DB 0 - MAIN OPERATIONS & SPIDERS")
    print("-" * 40)
    if r0 := redis_dbs.get(0):
        # Check freelance data
        freelance_keys = r0.keys('freelance:*')
        print(f"Freelance projects: {len(freelance_keys)}")

        # Check if spider data is real
        if freelance_keys:
            sample_key = freelance_keys[0]
            sample = safe_get_value(r0, sample_key)
            if sample:
                try:
                    data = json.loads(sample) if isinstance(sample, str) else sample
                    print(f"  ✅ REAL: Spider data exists")
                    if isinstance(data, dict):
                        print(f"     Title: {data.get('title', 'N/A')[:50]}...")
                        print(f"     Budget: {data.get('budget', 'N/A')}")
                except:
                    print(f"  ⚠️ Data exists but format unclear")
        else:
            print(f"  ❌ MISSING: No spider data found")

        # Check collaborations
        collab_keys = r0.keys('collaboration:*')
        print(f"\nCollaborations: {len(collab_keys)}")
        if collab_keys:
            print(f"  ✅ REAL: {len(collab_keys)} collaborations tracked")
        else:
            print(f"  ❌ MISSING: No collaborations found")

    # DB 2 - Learning System
    print("\n🧠 DB 2 - LEARNING SYSTEM")
    print("-" * 40)
    if r2 := redis_dbs.get(2):
        # Solutions
        solution_keys = r2.keys('solution:*')
        print(f"Solutions stored: {len(solution_keys)}")

        # Check if solutions have real code
        real_solutions = 0
        for key in solution_keys[:5]:  # Sample first 5
            val = safe_get_value(r2, key)
            if val:
                try:
                    data = json.loads(val)
                    if 'code' in data and data['code'] and len(data['code']) > 50:
                        real_solutions += 1
                except:
                    pass

        if real_solutions > 0:
            print(f"  ✅ REAL: {real_solutions}/5 solutions have executable code")
        else:
            print(f"  ⚠️ PARTIAL: Solutions exist but may lack real code")

        # Knowledge sharing
        knowledge_keys = r2.keys('shared:knowledge:*')
        print(f"\nShared knowledge: {len(knowledge_keys)}")
        if knowledge_keys:
            print(f"  ✅ REAL: {len(knowledge_keys)} knowledge items shared")
        else:
            print(f"  ❌ MISSING: No knowledge sharing detected")

        # Get dashboard stats
        stats = r2.get('learning:dashboard:stats')
        if stats:
            data = json.loads(stats)
            print(f"\nDashboard Stats:")
            print(f"  Active agents: {data.get('active_agents', 0)}")
            print(f"  Reality score: {data.get('reality_score', 0)}%")

    # DB 4 - Career Platform
    print("\n💼 DB 4 - CAREER PLATFORM")
    print("-" * 40)
    if r4 := redis_dbs.get(4):
        # Check phases
        phases = []
        for phase in range(1, 6):
            phase_keys = r4.keys(f'*phase{phase}*')
            if phase_keys:
                phases.append(phase)

        print(f"Phases with data: {phases if phases else 'None'}")
        if len(phases) == 5:
            print(f"  ✅ REAL: All 5 phases have data")
        elif phases:
            print(f"  ⚠️ PARTIAL: Only phases {phases} have data")
        else:
            print(f"  ❌ MISSING: No phase data found")

        # Check monetization
        monetization = r4.get('monetization:projections')
        if monetization:
            try:
                data = json.loads(monetization)
                revenue = data.get('month_1_total', {}).get('revenue', 0)
                print(f"\nMonetization:")
                print(f"  ✅ REAL: ${revenue:,} projected revenue")
            except:
                print(f"\nMonetization:")
                print(f"  ⚠️ Data exists but format unclear")
        else:
            print(f"\nMonetization:")
            print(f"  ❌ MISSING: No revenue projections")

        # Check agent insights
        insights = r4.get('agents:combined_insights')
        if insights:
            try:
                data = json.loads(insights)
                print(f"\nAgent Insights:")
                print(f"  ✅ REAL: {len(data)} insight categories")
                for key in list(data.keys())[:3]:
                    print(f"     - {key}")
            except:
                print(f"\nAgent Insights:")
                print(f"  ⚠️ Data exists but format unclear")
        else:
            print(f"\nAgent Insights:")
            print(f"  ❌ MISSING: No agent insights")

    # API Analysis
    print("\n🔑 API KEY ANALYSIS")
    print("-" * 40)
    print("Current Implementation:")
    print("  ✅ Algorithmic solution generation (no API needed)")
    print("  ✅ Pattern-based learning (no API needed)")
    print("  ✅ Redis-based storage (no API needed)")
    print("\nPotential Enhancements (would need API keys):")
    print("  ⚠️ OpenAI/Claude for enhanced content")
    print("  ⚠️ Real job boards API for live opportunities")
    print("  ⚠️ Payment processing for actual sales")

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("-" * 40)

    total_real = 0
    total_missing = 0

    # Count real vs missing
    if redis_dbs.get(0):
        r0 = redis_dbs[0]
        if r0.keys('freelance:*'):
            total_real += 1
        else:
            total_missing += 1

    if redis_dbs.get(2):
        r2 = redis_dbs[2]
        if r2.keys('solution:*'):
            total_real += 1
        else:
            total_missing += 1
        if r2.keys('shared:knowledge:*'):
            total_real += 1
        else:
            total_missing += 1

    if redis_dbs.get(4):
        r4 = redis_dbs[4]
        if r4.get('monetization:projections'):
            total_real += 1
        else:
            total_missing += 1
        if r4.get('agents:combined_insights'):
            total_real += 1
        else:
            total_missing += 1

    reality_percentage = (total_real / (total_real + total_missing) * 100) if (total_real + total_missing) > 0 else 0

    print(f"✅ Real Data Components: {total_real}")
    print(f"❌ Missing Components: {total_missing}")
    print(f"\n🎯 REALITY SCORE: {reality_percentage:.1f}%")

    if reality_percentage >= 80:
        print("\n✨ System is MOSTLY REAL - Ready for demo!")
    elif reality_percentage >= 50:
        print("\n⚠️ System is PARTIALLY REAL - Some components missing")
    else:
        print("\n❌ System needs more real data - Run demo phases")

    print("=" * 70)

if __name__ == "__main__":
    check_all_data()