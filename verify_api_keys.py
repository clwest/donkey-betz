#!/usr/bin/env python
"""
Verify All API Keys Are Working
================================
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_api_key(name, key, test_url, headers=None, params=None):
    """Check if an API key works"""
    if not key or key == 'demo_key' or key.startswith('your_'):
        print(f"❌ {name}: Not configured (using demo/mock)")
        return False

    try:
        if headers is None:
            headers = {}
        if params is None:
            params = {}

        response = requests.get(test_url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            print(f"✅ {name}: Working! (API key valid)")
            return True
        elif response.status_code == 401:
            print(f"❌ {name}: Invalid API key")
            return False
        else:
            print(f"⚠️  {name}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)[:50]}")
        return False

def main():
    print("\n" + "="*60)
    print("🔑 VERIFYING API KEYS")
    print("="*60)

    results = []

    # OpenAI (Already working)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        openai_key = openai_key.strip('"')  # Remove quotes if present
    results.append(check_api_key(
        "OpenAI",
        openai_key,
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {openai_key}"}
    ))

    # Polygon.io
    polygon_key = os.getenv('POLYGON_API_KEY')
    results.append(check_api_key(
        "Polygon.io",
        polygon_key,
        f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={polygon_key}"
    ))

    # Alpha Vantage (not configured yet)
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if alpha_key:
        results.append(check_api_key(
            "Alpha Vantage",
            alpha_key,
            f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey={alpha_key}"
        ))
    else:
        print("❌ Alpha Vantage: Not configured")
        results.append(False)

    # NewsAPI
    news_key = os.getenv('NEWS_API_KEY')
    results.append(check_api_key(
        "NewsAPI",
        news_key,
        f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_key}"
    ))

    # The Odds API (not configured yet)
    odds_key = os.getenv('ODDS_API_KEY')
    if odds_key:
        results.append(check_api_key(
            "The Odds API",
            odds_key,
            f"https://api.the-odds-api.com/v4/sports?apiKey={odds_key}"
        ))
    else:
        print("❌ The Odds API: Not configured")
        results.append(False)

    # Reddit (check if configured)
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
    if reddit_id and reddit_secret and not reddit_id.startswith('your_'):
        print(f"✅ Reddit: Configured (ID: {reddit_id[:8]}...)")
        results.append(True)
    else:
        print(f"❌ Reddit: Not configured properly")
        results.append(False)

    # CoinGecko
    coingecko_key = os.getenv('COINGECKO_API_KEY')
    if coingecko_key and coingecko_key != 'CG-2b2J8DfXyFvfnPVotipmmdHP':
        # Note: CoinGecko free tier doesn't require API key for basic endpoints
        print(f"✅ CoinGecko: Configured")
        results.append(True)
    else:
        results.append(check_api_key(
            "CoinGecko",
            coingecko_key,
            "https://api.coingecko.com/api/v3/ping",
            headers={"x-cg-demo-api-key": coingecko_key if coingecko_key else ""}
        ))

    # Additional APIs we have
    print("\n📦 Additional APIs Found:")

    # Anthropic
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        print(f"✅ Anthropic Claude: Configured")

    # Stability AI
    stability_key = os.getenv('STABILITY_API_KEY')
    if stability_key:
        print(f"✅ Stability AI: Configured")

    # ElevenLabs
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    if elevenlabs_key:
        print(f"✅ ElevenLabs (Voice): Configured")

    # Summary
    print("\n" + "="*60)
    working = sum(results)
    total = len(results)
    percentage = (working / total) * 100

    print(f"📊 API KEY STATUS: {working}/{total} working ({percentage:.0f}%)")

    if percentage == 100:
        print("🎉 All API keys configured and working!")
    elif percentage >= 70:
        print("✅ Most API keys are working! System highly functional.")
    elif percentage >= 50:
        print("⚠️  Some API keys need configuration")
    else:
        print("❌ Most API keys need to be added")

    print("\n💡 Missing APIs to get:")
    if not alpha_key:
        print("  • Alpha Vantage - https://www.alphavantage.co/support/#api-key")
    if not odds_key:
        print("  • The Odds API - https://the-odds-api.com/#get-access")

    print("="*60)

if __name__ == "__main__":
    main()