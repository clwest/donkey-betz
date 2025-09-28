# 🔧 FIX #3: Add Remaining API Keys for Full Functionality
## Priority: HIGH | Time: 15 minutes | Impact: +8% Reality

---

## 🔴 CURRENT PROBLEM

Several spiders and agents can't fetch real data because API keys are missing:
- Using demo/mock API keys for sports data
- Reddit API in read-only mode
- No Polygon.io key for real market data
- No Alpha Vantage key for stock data
- No NewsAPI key for news aggregation

**Error Evidence:**
```
WARNING Using demo Odds API key - limited data available
WARNING Using demo SportRadar API key
Reddit API initialized in read-only mode
```

---

## ✅ COMPLETE SOLUTION

### Step 1: Obtain Free API Keys

#### 1. Polygon.io (Real-time Market Data)
- **Website:** https://polygon.io
- **Free Tier:** 5 API calls/minute, unlimited monthly
- **Sign Up:** https://polygon.io/dashboard/signup
- **What You Get:** Real stock prices, crypto data, forex rates

#### 2. Alpha Vantage (Stock Market Data)
- **Website:** https://www.alphavantage.co
- **Free Tier:** 5 API calls/minute, 500 calls/day
- **Get Key:** https://www.alphavantage.co/support/#api-key
- **What You Get:** Historical stock data, technical indicators

#### 3. NewsAPI (News Aggregation)
- **Website:** https://newsapi.org
- **Free Tier:** 100 requests/day
- **Sign Up:** https://newsapi.org/register
- **What You Get:** Headlines from 80,000+ sources

#### 4. Reddit API (Full Access)
- **Website:** https://www.reddit.com/prefs/apps
- **Free Tier:** 60 requests/minute
- **Steps:**
  1. Go to https://www.reddit.com/prefs/apps
  2. Click "Create App" or "Create Another App"
  3. Name: "YourAppName"
  4. Type: Select "script"
  5. Description: "Personal use script"
  6. About URL: (leave blank)
  7. Redirect URI: http://localhost:8080
  8. Click "Create App"
  9. Note your Client ID (under "personal use script")
  10. Note your Secret (the secret key)

#### 5. The Odds API (Sports Betting Data)
- **Website:** https://the-odds-api.com
- **Free Tier:** 500 requests/month
- **Sign Up:** https://the-odds-api.com/#get-access
- **What You Get:** Real sports odds from 70+ bookmakers

#### 6. CoinGecko (Crypto Data)
- **Website:** https://www.coingecko.com/en/api
- **Free Tier:** 50 calls/minute
- **Sign Up:** https://www.coingecko.com/en/api/pricing
- **What You Get:** Crypto prices, market cap, volume

### Step 2: Add Keys to .env File

**File:** `/.env`

Add these lines (replace with your actual keys):

```bash
# Market Data APIs
POLYGON_API_KEY=your_polygon_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# News APIs
NEWS_API_KEY=your_newsapi_key_here

# Reddit API (Full Access)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=YourApp/1.0 by YourUsername

# Sports Data
ODDS_API_KEY=your_odds_api_key_here
SPORTRADAR_API_KEY=your_sportradar_key_here

# Crypto Data
COINGECKO_API_KEY=your_coingecko_key_here

# Financial Data (Optional Premium)
FINNHUB_API_KEY=your_finnhub_key_here
IEX_CLOUD_API_KEY=your_iex_cloud_key_here

# AI Services (Already Have)
OPENAI_API_KEY=sk-proj-... # Already configured ✅

# Social Media (Optional)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
BLUESKY_USERNAME=your_bluesky_username
BLUESKY_PASSWORD=your_bluesky_password
```

### Step 3: Update Configuration Files

**File:** `/ai_core/settings.py`

Add to settings:

```python
# API Keys from environment
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
ODDS_API_KEY = os.getenv('ODDS_API_KEY', 'demo_key')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
```

### Step 4: Update Spider Configurations

**File:** `/ai_core/spiders/market_data_spider.py`

```python
class MarketDataSpider:
    def __init__(self):
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')

        if not self.polygon_key:
            logger.warning("No Polygon API key - using mock data")
            self.use_mock = True
        else:
            self.use_mock = False

    def fetch_stock_data(self, symbol):
        if self.use_mock:
            return self._get_mock_data(symbol)

        # Real API call
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
        headers = {"Authorization": f"Bearer {self.polygon_key}"}
        response = requests.get(url, headers=headers)
        return response.json()
```

### Step 5: Verify API Keys Script

**File:** `/verify_api_keys.py`

```python
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

    # Alpha Vantage
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    results.append(check_api_key(
        "Alpha Vantage",
        alpha_key,
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey={alpha_key}"
    ))

    # NewsAPI
    news_key = os.getenv('NEWS_API_KEY')
    results.append(check_api_key(
        "NewsAPI",
        news_key,
        f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_key}"
    ))

    # The Odds API
    odds_key = os.getenv('ODDS_API_KEY')
    results.append(check_api_key(
        "The Odds API",
        odds_key,
        f"https://api.the-odds-api.com/v4/sports?apiKey={odds_key}"
    ))

    # Reddit (check if configured)
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
    if reddit_id and reddit_secret and not reddit_id.startswith('your_'):
        print(f"✅ Reddit: Configured (ID: {reddit_id[:8]}...)")
        results.append(True)
    else:
        print(f"❌ Reddit: Not configured")
        results.append(False)

    # Summary
    print("\n" + "="*60)
    working = sum(results)
    total = len(results)
    percentage = (working / total) * 100

    print(f"📊 API KEY STATUS: {working}/{total} working ({percentage:.0f}%)")

    if percentage == 100:
        print("🎉 All API keys configured and working!")
    elif percentage >= 50:
        print("⚠️  Some API keys need configuration")
    else:
        print("❌ Most API keys need to be added")

    print("="*60)

if __name__ == "__main__":
    main()
```

---

## 🚀 QUICK SETUP COMMANDS

```bash
# 1. Get your API keys from the websites above (15 mins)

# 2. Add to .env file
echo "POLYGON_API_KEY=your_key_here" >> .env
echo "ALPHA_VANTAGE_API_KEY=your_key_here" >> .env
echo "NEWS_API_KEY=your_key_here" >> .env
echo "REDDIT_CLIENT_ID=your_id_here" >> .env
echo "REDDIT_CLIENT_SECRET=your_secret_here" >> .env
echo "ODDS_API_KEY=your_key_here" >> .env

# 3. Verify all keys work
python verify_api_keys.py

# 4. Restart the server
python manage.py runserver
```

---

## 🎯 SUCCESS CRITERIA

You'll know this is fixed when:
1. ✅ No more "demo API key" warnings
2. ✅ verify_api_keys.py shows 6/6 working
3. ✅ Spiders fetch real market data
4. ✅ Reddit spider gets full post content

---

## 📈 IMPACT WHEN FIXED

- **+8% Reality Score** - Real data flows in
- **Unlock Market Data** - Real stock prices
- **Unlock News** - Real headlines
- **Unlock Reddit** - Full post access
- **Unlock Sports** - Real betting odds
- **Enable Trading** - Can make real market decisions

---

## 💡 PRO TIPS

1. **Start with free tiers** - All these APIs have generous free tiers
2. **Use burner email** - Create a dedicated email for API signups
3. **Track usage** - Most APIs show usage in their dashboards
4. **Rate limiting** - Respect rate limits to avoid bans

---

## 🔍 TROUBLESHOOTING

### If API Key Doesn't Work:
1. Check for typos in the .env file
2. Ensure no quotes around the key in .env
3. Verify the key on the provider's website
4. Check if the API requires activation

### If Rate Limited:
1. Add delays between requests
2. Use caching (Redis already set up!)
3. Upgrade to paid tier if needed

---

## ⏰ TIME ESTIMATE

- Sign up for 6 APIs: 10 minutes
- Add to .env file: 2 minutes
- Test with script: 3 minutes
- **Total: 15 minutes**

---

*These API keys transform your spiders from mock to REAL data collectors!*