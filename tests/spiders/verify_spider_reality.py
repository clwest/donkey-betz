# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Spider Reality Verification Script
===================================
Deep analysis of what spiders are REAL vs FAKE/MOCK
"""

import os
import sys
import django
import redis
import json
import importlib
import inspect
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'ai_core.settings'
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
django.setup()

def check_spider_implementations():
    """Check actual spider class implementations"""
    print("\n🔍 SPIDER IMPLEMENTATIONS CHECK:")
    print("-" * 50)

    real_spiders = []
    mock_spiders = []

    # Check spider registry
    try:
        from ai_core.spiders.spider_registry import spider_registry
        registered = spider_registry.list_spiders()

        for name, info in registered.items():
            is_placeholder = info.get('is_placeholder', False)
            if is_placeholder:
                mock_spiders.append(name)
            else:
                real_spiders.append(name)

        print(f"✅ Real spider implementations: {len(real_spiders)}")
        for spider in real_spiders[:10]:
            print(f"   • {spider}")

        print(f"\n⚠️  Placeholder/Mock spiders: {len(mock_spiders)}")
        for spider in mock_spiders[:10]:
            print(f"   • {spider}")

    except Exception as e:
        print(f"❌ Could not load spider registry: {e}")

    return real_spiders, mock_spiders


def check_spider_processes():
    """Check for running spider processes"""
    print("\n🏃 RUNNING PROCESSES CHECK:")
    print("-" * 50)

    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    spider_processes = [line for line in result.stdout.split('\n') if 'spider' in line.lower() and 'grep' not in line]

    print(f"Found {len(pider_processes)} spider-related processes:")
    for proc in spider_processes[:5]:
        parts = proc.split()
        if len(parts) > 10:
            pid = parts[1]
            cmd = ' '.join(parts[10:])
            print(f"   • PID {pid}: {cmd[:80]}")

    return len(pider_processes)


def check_redis_activity():
    """Check Redis for spider activity"""
    print("\n📡 REDIS ACTIVITY CHECK:")
    print("-" * 50)

    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Check spider keys
    spider_keys = r.keys('spider*')
    print(f"Spider keys in Redis: {len(pider_keys)}")

    # Check feed freshness
    if r.exists('spider:feed'):
        feed_items = r.lrange('spider:feed', 0, -1)
        if feed_items:
            try:
                latest = json.loads(feed_items[0])
                timestamp = latest.get('timestamp', '')
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    age = (datetime.now() - dt.replace(tzinfo=None)).days
                    print(f"Latest feed item age: {age} days old")

                    if age > 30:
                        print("   ⚠️ Feed data is STALE (over 30 days old)")
                    elif age > 7:
                        print("   🟡 Feed data is aging (over 7 days old)")
                    else:
                        print("   ✅ Feed data is FRESH")
            except:
                print("   ❌ Could not parse feed timestamps")

    # Check for opportunities
    opp_keys = r.keys('freelance:opportunity:*')
    print(f"Freelance opportunities: {len(opp_keys)}")

    # Check for active connections
    active = r.keys('active:spider:*')
    print(f"Active spider markers: {len(active)}")

    return {
        'spider_keys': len(pider_keys),
        'opportunities': len(opp_keys),
        'active_markers': len(active)
    }


def check_database_records():
    """Check database for spider records"""
    print("\n💾 DATABASE RECORDS CHECK:")
    print("-" * 50)

    try:
        from core.models_unified_system import SpiderData

        total = SpiderData.objects.count()
        print(f"SpiderData records: {total}")

        if total > 0:
            # Check recent activity
            recent = datetime.now() - timedelta(days=1)
            recent_count = SpiderData.objects.filter(created_at__gte=recent).count()
            print(f"Records from last 24h: {recent_count}")

            # Show sample
            samples = SpiderData.objects.order_by('-created_at')[:3]
            print("\nRecent samples:")
            for s in samples:
                print(f"   • {s.spider_name}: {s.data_type} ({s.created_at})")

        return total
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return 0


def check_spider_code_reality():
    """Check if spider code actually makes real web requests"""
    print("\n🌐 SPIDER CODE REALITY CHECK:")
    print("-" * 50)

    spider_files = list(Path('/Users/donkeyking/development/unified-donkey-betz').rglob('*spider*.py'))

    real_indicators = ['requests.', 'aiohttp', 'urllib', 'scrapy', 'selenium', 'fetch(', 'httpx']
    mock_indicators = ['sleep(', 'random.choice', 'fake_data', 'mock_', 'return {', 'hardcoded']

    real_count = 0
    mock_count = 0

    for file in spider_files[:20]:  # Check first 20 files
        try:
            content = file.read_text()

            has_real = any(indicator in content for indicator in real_indicators)
            has_mock = any(indicator in content for indicator in mock_indicators)

            if has_real and not has_mock:
                real_count += 1
            elif has_mock and not has_real:
                mock_count += 1

        except:
            pass

    print(f"Files with real web requests: {real_count}")
    print(f"Files with mock/simulated data: {mock_count}")

    return real_count, mock_count


def calculate_reality_score(checks):
    """Calculate overall spider reality score"""
    print("\n" + "="*60)
    print("🎯 SPIDER REALITY VERDICT:")
    print("="*60)

    scores = {
        'Has real implementations': checks['real_spiders'] > 5,
        'Processes running': checks['processes'] > 0,
        'Redis activity': checks['redis']['spider_keys'] > 0,
        'Fresh data': checks['feed_fresh'],
        'Database records': checks['db_records'] > 0,
        'Real web code': checks['real_code'] > checks['mock_code']
    }

    for check, passed in scores.items():
        status = '✅' if passed else '❌'
        print(f"{status} {check}")

    reality_percentage = sum(1 for v in scores.values() if v) / len(cores) * 100

    print(f"\n📊 OVERALL SPIDER REALITY: {reality_percentage:.0f}%")

    if reality_percentage >= 80:
        print("\n✅ VERDICT: SPIDERS ARE MOSTLY REAL")
        print("   • Active implementations exist")
        print("   • Processes are running")
        print("   • Data collection happening")
    elif reality_percentage >= 50:
        print("\n🟡 VERDICT: PARTIAL REALITY - MIXED REAL/FAKE")
        print("   • Some real spiders exist")
        print("   • Limited activity detected")
        print("   • Mix of real and simulated data")
    else:
        print("\n❌ VERDICT: MOSTLY FAKE/SIMULATED SPIDERS")
        print("   • Mainly placeholder implementations")
        print("   • Static/mock data being used")
        print("   • No real collection happening")

    print("\n📋 DETAILED FINDINGS:")
    print(f"   • {checks['real_spiders']} real spider implementations")
    print(f"   • {checks['mock_spiders']} placeholder/mock spiders")
    print(f"   • {checks['processes']} spider processes running")
    print(f"   • {checks['redis']['spider_keys']} Redis spider keys")
    print(f"   • {checks['db_records']} database records")

    return reality_percentage


def main():
    print("="*60)
    print("🕷️ SPIDER REALITY VERIFICATION SYSTEM")
    print("="*60)

    # Run all checks
    real_spiders, mock_spiders = check_spider_implementations()
    processes = check_spider_processes()
    redis_data = check_redis_activity()
    db_records = check_database_records()
    real_code, mock_code = check_spider_code_reality()

    # Check feed freshness separately
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    feed_fresh = False
    if r.exists('spider:feed'):
        try:
            feed = json.loads(r.lindex('spider:feed', 0))
            dt = datetime.fromisoformat(feed.get('timestamp', '').replace('Z', '+00:00'))
            age_days = (datetime.now() - dt.replace(tzinfo=None)).days
            feed_fresh = age_days < 7
        except:
            pass

    # Calculate reality score
    checks = {
        'real_spiders': len(real_spiders),
        'mock_spiders': len(mock_spiders),
        'processes': processes,
        'redis': redis_data,
        'db_records': db_records,
        'real_code': real_code,
        'mock_code': mock_code,
        'feed_fresh': feed_fresh
    }

    reality_score = calculate_reality_score(checks)

    print("\n" + "="*60)
    print("✨ Analysis complete!")
    print("="*60)

    return reality_score


if __name__ == "__main__":
    main()