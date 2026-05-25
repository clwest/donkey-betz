<!-- DOC-POINTER-V2 (Session 1143) -->
> **Status:** Archived
> **Originally:** see header below for original date/session.
> **Last verified:** Session 1143 (2026-05-25)
> **Change reason:** Nov 2025 snapshot. Superseded by API_KEY_FINAL_STATUS.md and ultimately by PLATFORM_INVENTORY.md runtime check.
> **Preserved because:** white-paper corpus / historical record.

# API Key Status Report
**Generated:** November 2, 2025
**Test Script:** `/scripts/test_api_keys.py`

---

## 🎯 Executive Summary

**Total APIs Tested:** 19
**✓ Valid:** 9 (47%)
**✗ Invalid:** 5 (26%) ← **NEEDS IMMEDIATE ATTENTION**
**⚠ Errors:** 3 (16%)
**○ Skipped:** 2 (11%)

---

## ✅ VALID API KEYS (Working Fine)

These keys are active and working - no action needed:

1. **OpenAI** ✅ - Core AI functionality
2. **Anthropic (Claude)** ✅ - Advanced reasoning
3. **Groq** ✅ - Fast inference
4. **Stability AI** ✅ - Image generation (you just need to update payment card)
5. **ElevenLabs** ✅ - Voice/audio generation
6. **The Odds API** ✅ - Sports betting (65 sports available)
7. **Stripe** ✅ - Payment processing
8. **News API** ✅ - News aggregation
9. **Hugging Face** ✅ - ML models

---

## 🔴 INVALID API KEYS (Require Immediate Action)

### Priority 1: Critical Revenue Features

#### 1. **Runway ML** ❌
- **Status:** Invalid API key
- **Impact:** Video generation features in Content Studio
- **Action:** Update payment card and regenerate API key
- **Where to update:** https://runwayml.com/account/api-keys

#### 2. **Polygon.io** ❌ (You already knew this)
- **Status:** Invalid or expired
- **Impact:** Financial data, stock prices, sports betting analytics
- **Action:** Regenerate API key at Polygon.io
- **Where to update:** https://polygon.io/dashboard/api-keys

### Priority 2: Data Collection & Intelligence

#### 3. **Reddit** ❌
- **Status:** Failed to get access token
- **Impact:** Social sentiment analysis, sports data collection, spider network
- **Action:**
  - Check if password changed during divorce
  - Regenerate Reddit app credentials if needed
  - Update REDDIT_PASSWORD in .env
- **Where to update:** https://www.reddit.com/prefs/apps

#### 4. **Etherscan** ❌
- **Status:** API returned "NOTOK"
- **Impact:** Blockchain data, crypto features
- **Action:** Regenerate API key
- **Where to update:** https://etherscan.io/myapikey

#### 5. **GitHub** ❌
- **Status:** Invalid token
- **Impact:** Code repository integration, deployment automation
- **Action:** Generate new Personal Access Token
- **Where to update:** https://github.com/settings/tokens

---

## ⚠️ ERROR STATUS (Need Investigation)

These returned errors but may just be rate-limited or misconfigured:

#### 1. **SEC API**
- **Error:** HTTP 429 (Rate Limited)
- **Action:** May be valid but rate-limited. Try again in a few hours or check plan limits.

#### 2. **CoinGecko**
- **Error:** HTTP 400 (Bad Request)
- **Action:** Check if API endpoint changed or if key format is incorrect

#### 3. **Serper (Google Search)**
- **Error:** HTTP 400 (Bad Request)
- **Action:** Low priority - verify request format if needed

---

## ○ SKIPPED (Manual Testing Required)

#### 1. **SportsRadar**
- **Reason:** Requires sport-specific endpoints
- **Action:** Test manually with a specific sport endpoint when needed

#### 2. **Coinbase**
- **Reason:** Requires special CDP API authentication
- **Action:** Test manually if crypto trading features needed

---

## 📋 ACTION PLAN

### Immediate (Today)

1. **Runway ML** - Update payment card + regenerate key
   - Login: https://runwayml.com
   - Go to: Account → API Keys
   - Update payment method
   - Generate new API key
   - Update `.env`: `RUNWAY_API_KEY=`

2. **Polygon.io** - Regenerate API key
   - Login: https://polygon.io
   - Go to: Dashboard → API Keys
   - Generate new key
   - Update `.env`: `POLYGON_API_KEY=`

3. **Reddit** - Check credentials
   - Login: https://www.reddit.com
   - Verify account: Photo-dad2017
   - Reset password if needed
   - Update `.env`: `REDDIT_PASSWORD=`
   - Verify app at: https://www.reddit.com/prefs/apps

### High Priority (This Week)

4. **Etherscan** - Regenerate API key
   - Login: https://etherscan.io
   - Go to: My API Keys
   - Generate new key
   - Update `.env`: `ETHERSCAN_API_KEY=`

5. **GitHub** - Generate new Personal Access Token
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Scopes needed: `repo`, `workflow`, `read:org`
   - Update `.env`: `GITHUB_TOKEN=`

### Low Priority (When Needed)

6. **SEC API** - Wait and retry, may be temporary rate limit
7. **CoinGecko** - Investigate if crypto features needed
8. **Serper** - Low impact, can investigate later

---

## 💳 Payment Card Updates Needed

Based on your note about having credits:

1. **OpenAI** ✅ - Working, but verify payment method on file
2. **Stability AI** ✅ - Working, but update card as planned
3. **Runway ML** ❌ - Update card AND regenerate key

### Where to Update Payment Cards:

- **OpenAI:** https://platform.openai.com/settings/organization/billing
- **Stability AI:** https://platform.stability.ai/account/billing
- **Runway ML:** https://runwayml.com/account/billing

---

## 🔧 How to Update .env File

After getting new API keys, update the `.env` file:

```bash
# Open .env in your editor
code /Users/donkeyking/development/unified-donkey-betz/.env

# Update the following lines:
RUNWAY_API_KEY="new_key_here"
POLYGON_API_KEY=new_key_here
REDDIT_PASSWORD="new_password_here"
ETHERSCAN_API_KEY="new_key_here"
GITHUB_TOKEN="new_token_here"

# Save and restart services
make stop
make start
```

---

## 📊 Impact Analysis

### What's Still Working (96% Reality Score Maintained)

- ✅ Core AI features (OpenAI, Anthropic, Groq)
- ✅ Content Studio image generation (Stability AI)
- ✅ Audio generation (ElevenLabs)
- ✅ Sports betting (The Odds API)
- ✅ Payment processing (Stripe)
- ✅ News intelligence (News API)

### What's Broken

- ❌ Video generation (Runway ML)
- ❌ Financial/stock data (Polygon)
- ❌ Reddit spider network (social sentiment)
- ❌ Blockchain data (Etherscan)
- ❌ GitHub integrations

### Critical for Revenue

**Must fix ASAP:**
1. Runway ML - Video content = revenue
2. Polygon - Sports betting analytics = revenue
3. Reddit - Intelligence gathering = quality

**Can wait:**
- Etherscan (only needed for crypto features)
- GitHub (development convenience)

---

## 📝 Notes

- Most CRITICAL APIs are still working (OpenAI, Stability AI, Sports)
- Platform can still operate at ~85% capacity
- Video generation and financial data are the main gaps
- Reddit intelligence gathering is impacted but not critical

---

## ✅ Re-test After Updates

After updating API keys, re-run the test script:

```bash
python3 scripts/test_api_keys.py
```

This will generate a fresh report showing which keys are now valid.

---

**Next Steps:**
1. Update Runway ML payment + regenerate key
2. Regenerate Polygon API key
3. Check/fix Reddit credentials
4. Re-run test script to verify
5. Update this document with new status
