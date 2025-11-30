# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""Quick test to verify real data collection is working"""

import asyncio
import aiohttp
import json

async def test_apis():
    """Test if we can fetch real data from APIs"""

    results = {
        'github_api': False,
        'coingecko': False,
        'remoteok': False,
        'hackernews': False
    }

    async with aiohttp.ClientSession() as session:
        # Test GitHub API
        try:
            async with session.get('https://api.github.com') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results['github_api'] = True
                    print(f"✅ GitHub API: Working")
        except Exception as e:
            print(f"❌ GitHub API: {e}")

        # Test CoinGecko
        try:
            async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    btc_price = data.get('bitcoin', {}).get('usd', 0)
                    results['coingecko'] = True
                    print(f"✅ CoinGecko: Bitcoin at ${btc_price:,.2f}")
        except Exception as e:
            print(f"❌ CoinGecko: {e}")

        # Test HackerNews
        try:
            async with session.get('https://hacker-news.firebaseio.com/v0/topstories.json') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results['hackernews'] = True
                    print(f"✅ HackerNews: {len(data)} top stories")
        except Exception as e:
            print(f"❌ HackerNews: {e}")

        # Test RemoteOK (might require specific headers)
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            async with session.get('https://remoteok.io/api', headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    jobs_count = len(data) - 1 if isinstance(data, list) else 0
                    results['remoteok'] = True
                    print(f"✅ RemoteOK: {jobs_count} jobs available")
        except Exception as e:
            print(f"❌ RemoteOK: {e}")

    # Calculate reality score
    working = sum(1 for v in results.values() if v)
    total = len(results)
    score = (working / total) * 100

    print(f"\n🎯 Reality Score: {score:.1f}%")
    print(f"   Working APIs: {working}/{total}")

    if score >= 75:
        print("   ✅ Real data collection is working!")
    elif score >= 50:
        print("   ⚠️ Partial success - some APIs working")
    else:
        print("   ❌ Need to fix API connections")

    return score

if __name__ == "__main__":
    print("🕷️ Testing Real Data Collection...\n")
    score = asyncio.run(test_apis())
    print(f"\nFinal Score: {score:.1f}%")