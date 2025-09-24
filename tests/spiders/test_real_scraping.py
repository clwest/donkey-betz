#!/usr/bin/env python3
"""
Test Real Website Scraping Capabilities
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_real_freelance_scraping():
    """Test if we can actually scrape real freelance sites"""

    print("🔍 TESTING REAL FREELANCE SITE SCRAPING")
    print("=" * 50)

    # Test targets - real freelance site endpoints
    test_targets = [
        {
            'name': 'Upwork RSS (if available)',
            'url': 'https://www.upwork.com/ab/feed/jobs/rss',
            'headers': {'User-Agent': 'Mozilla/5.0 (compatible; FreelanceBot/1.0)'}
        },
        {
            'name': 'Freelancer.com Jobs RSS',
            'url': 'https://www.freelancer.com/jobs/rss.xml',
            'headers': {'User-Agent': 'Mozilla/5.0 (compatible; FreelanceBot/1.0)'}
        },
        {
            'name': 'AngelList Jobs API',
            'url': 'https://angel.co/jobs',
            'headers': {'User-Agent': 'Mozilla/5.0 (compatible; FreelanceBot/1.0)'}
        },
        {
            'name': 'RemoteOK API',
            'url': 'https://remoteok.io/api',
            'headers': {'User-Agent': 'Mozilla/5.0 (compatible; FreelanceBot/1.0)'}
        }
    ]

    results = []

    async with aiohttp.ClientSession() as session:
        for target in test_targets:
            print(f"\n🌐 Testing: {target['name']}")
            print(f"📡 URL: {target['url']}")

            try:
                async with session.get(
                    target['url'],
                    headers=target['headers'],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    status = response.status
                    content_type = response.headers.get('content-type', 'unknown')
                    content_length = response.headers.get('content-length', 'unknown')

                    print(f"📊 Status: {status}")
                    print(f"📄 Content-Type: {content_type}")
                    print(f"📐 Content-Length: {content_length}")

                    if status == 200:
                        # Get a sample of the content
                        if 'json' in content_type:
                            try:
                                data = await response.json()
                                print(f"✅ JSON Response - Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                                if isinstance(data, list) and len(data) > 0:
                                    print(f"📋 Sample item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                            except:
                                print("❌ Invalid JSON")
                        else:
                            text = await response.text()
                            print(f"📝 Text Response - Length: {len(text)} chars")
                            if 'xml' in content_type or 'rss' in text[:200].lower():
                                print("🔖 RSS/XML feed detected")
                            if 'job' in text.lower()[:500]:
                                print("💼 Job listings detected in content")

                    elif status == 403:
                        print("🚫 Access Forbidden - Site blocks automated requests")
                    elif status == 404:
                        print("❓ Not Found - Endpoint may have changed")
                    elif status == 429:
                        print("⏳ Rate Limited - Too many requests")
                    else:
                        print(f"⚠️  Unexpected status: {status}")

                    results.append({
                        'name': target['name'],
                        'url': target['url'],
                        'status': status,
                        'content_type': content_type,
                        'accessible': status == 200,
                        'timestamp': datetime.now().isoformat()
                    })

            except asyncio.TimeoutError:
                print("⏰ Timeout - Site not responding")
                results.append({
                    'name': target['name'],
                    'url': target['url'],
                    'status': 'timeout',
                    'accessible': False,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"💥 Error: {e}")
                results.append({
                    'name': target['name'],
                    'url': target['url'],
                    'status': f'error: {e}',
                    'accessible': False,
                    'timestamp': datetime.now().isoformat()
                })

    print("\n" + "=" * 50)
    print("📊 SCRAPING CAPABILITY SUMMARY")
    print("=" * 50)

    accessible_count = sum(1 for r in results if r['accessible'])
    print(f"✅ Accessible endpoints: {accessible_count}/{len(results)}")

    if accessible_count > 0:
        print("🎯 REAL SCRAPING IS POSSIBLE!")
        print("💡 Recommendation: Implement real scrapers for accessible endpoints")
    else:
        print("❌ NO REAL SCRAPING CURRENTLY POSSIBLE")
        print("💡 Recommendation: Use API keys or find alternative data sources")

    print("\n📋 Detailed Results:")
    for result in results:
        status_emoji = "✅" if result['accessible'] else "❌"
        print(f"{status_emoji} {result['name']}: {result['status']}")

    return results

if __name__ == "__main__":
    asyncio.run(test_real_freelance_scraping())