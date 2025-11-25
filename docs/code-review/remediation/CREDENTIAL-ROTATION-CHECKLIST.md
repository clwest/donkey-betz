# Credential Rotation Checklist

**Created:** 2025-11-25
**Purpose:** Track rotation of all exposed credentials from the .env file
**Priority:** CRITICAL - Complete before any production deployment

---

## Overview

The code review identified **40+ live API credentials** exposed in the `.env` file. All credentials should be considered compromised and must be rotated.

### Priority Levels
- **P0 (CRITICAL):** Financial risk, immediate rotation required
- **P1 (HIGH):** Production services, rotate within 24 hours
- **P2 (MEDIUM):** Secondary services, rotate within 1 week
- **P3 (LOW):** Development/test services, rotate when convenient

---

## P0: CRITICAL - Financial & Security Risk

### 1. Stripe LIVE Keys
- [ ] **Status:** NOT ROTATED
- **Service:** Stripe Payment Processing
- **Keys to Rotate:**
  - `STRIPE_SECRET_KEY` (sk_live_...)
  - `STRIPE_PUBLISHABLE_KEY` (pk_live_...)
- **Rotation URL:** https://dashboard.stripe.com/apikeys
- **Steps:**
  1. Log into Stripe Dashboard
  2. Go to Developers > API Keys
  3. Click "Roll key" on Secret key
  4. Update `.env` with new key
  5. Test payment flow
- **Verification:** Process a $1 test payment

### 2. Coinbase Private Key
- [ ] **Status:** NOT ROTATED
- **Service:** Coinbase Cryptocurrency
- **Keys to Rotate:**
  - `COINBASE_API_KEY`
  - `COINBASE_PRIVATE_KEY` (EC Private Key!)
  - `COINBASE_PROJECT_ID`
- **Rotation URL:** https://www.coinbase.com/settings/api
- **Steps:**
  1. Log into Coinbase
  2. Go to Settings > API
  3. Delete old API key
  4. Create new API key with same permissions
  5. Download new private key
  6. Update `.env` with all new values
- **Verification:** Check account balance API call

### 3. Django SECRET_KEY
- [ ] **Status:** NOT ROTATED
- **Current Value:** `super-secret-donkey-business` (WEAK!)
- **Generate New:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **Steps:**
  1. Generate new key using command above
  2. Update `.env` with new SECRET_KEY
  3. Restart Django server
  4. All existing sessions will be invalidated (expected)
- **Verification:** `python manage.py check`

### 4. Encryption Keys
- [ ] **Status:** NOT ROTATED
- **Keys to Rotate:**
  - `ENCRYPTION_KEY`
  - `ENCRYPTION_KEY_BACKUP`
- **Generate New:**
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- **WARNING:** Rotating encryption keys requires data migration!
- **Steps:**
  1. Keep old ENCRYPTION_KEY as ENCRYPTION_KEY_BACKUP
  2. Generate new ENCRYPTION_KEY
  3. Run data migration script to re-encrypt data
  4. After verifying migration, remove ENCRYPTION_KEY_BACKUP
- **Verification:** Verify encrypted data can still be read

---

## P1: HIGH - Core Production Services

### 5. OpenAI API Key
- [ ] **Status:** NOT ROTATED
- **Service:** GPT-5, DALL-E, Whisper
- **Key:** `OPENAI_API_KEY`
- **Rotation URL:** https://platform.openai.com/api-keys
- **Steps:**
  1. Go to API Keys page
  2. Create new secret key
  3. Delete old key
  4. Update `.env`
- **Verification:** `python scripts/test_api_keys.py`

### 6. Anthropic API Key
- [ ] **Status:** NOT ROTATED
- **Service:** Claude AI
- **Key:** `ANTHROPIC_API_KEY`
- **Rotation URL:** https://console.anthropic.com/settings/keys
- **Steps:**
  1. Create new API key
  2. Update `.env`
  3. Delete old key
- **Verification:** Test AI assistant chat

### 7. Stability AI Keys
- [ ] **Status:** NOT ROTATED
- **Service:** Image Generation
- **Keys to Rotate:**
  - `STABILITY_API_KEY`
  - `STABILITY_KEY`
- **Rotation URL:** https://platform.stability.ai/account/keys
- **Verification:** Generate test image

### 8. Runway ML Key
- [ ] **Status:** NOT ROTATED
- **Service:** Video Generation
- **Key:** `RUNWAY_API_KEY`
- **Rotation URL:** https://app.runwayml.com/account/api
- **Verification:** Generate test video

### 9. ElevenLabs Keys
- [ ] **Status:** NOT ROTATED
- **Service:** Audio/Voice Generation
- **Keys to Rotate:**
  - `ELEVENLABS_API_KEY`
  - `ELEVEN_LABS_API`
- **Rotation URL:** https://elevenlabs.io/app/settings/api-keys
- **Verification:** Generate test audio

### 10. Replicate API Token
- [ ] **Status:** NOT ROTATED
- **Service:** Character Training, 3D Models
- **Key:** `REPLICATE_API_TOKEN`
- **Rotation URL:** https://replicate.com/account/api-tokens
- **Verification:** Test 3D model generation

### 11. GitHub Personal Access Token
- [ ] **Status:** NOT ROTATED
- **Service:** GitHub API
- **Key:** `GITHUB_TOKEN`
- **Rotation URL:** https://github.com/settings/tokens
- **Steps:**
  1. Create new fine-grained token
  2. Set appropriate permissions
  3. Delete old token
  4. Update `.env`
- **Verification:** Test GitHub API call

---

## P2: MEDIUM - Secondary Services

### 12. Cloudinary
- [ ] **Status:** NOT ROTATED
- **Service:** Image/Video CDN
- **Keys to Rotate:**
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`
- **Rotation URL:** https://console.cloudinary.com/settings/api-keys
- **Verification:** Upload test image

### 13. Twilio
- [ ] **Status:** NOT ROTATED
- **Service:** SMS/Voice
- **Keys to Rotate:**
  - `TWILIO_SID`
  - `TWILIO_SECRET`
- **Rotation URL:** https://console.twilio.com/
- **Steps:**
  1. Go to Account > API Keys
  2. Create new Standard API Key
  3. Update `.env`
  4. Delete old key
- **Verification:** Send test SMS

### 14. Reddit Credentials
- [ ] **Status:** NOT ROTATED
- **Service:** Reddit API
- **Keys to Rotate:**
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`
  - `REDDIT_PASSWORD` (Change account password!)
- **Rotation URL:** https://www.reddit.com/prefs/apps
- **Steps:**
  1. Change Reddit account password FIRST
  2. Create new OAuth app
  3. Delete old app
  4. Update `.env`
- **Verification:** Test Reddit API call

### 15. Telegram
- [ ] **Status:** NOT ROTATED
- **Service:** Telegram Bot
- **Keys to Rotate:**
  - `TELEGRAM_API_ID`
  - `TELEGRAM_API_HASH`
  - `TELEGRAM_BOT_TOKEN`
- **Rotation URLs:**
  - App credentials: https://my.telegram.org/apps
  - Bot token: Talk to @BotFather
- **Verification:** Test bot message

### 16. Spotify
- [ ] **Status:** NOT ROTATED
- **Service:** Spotify API
- **Keys to Rotate:**
  - `SPOTIFY_CLIENT_ID`
  - `SPOTIFY_CLIENT_SECRET`
- **Rotation URL:** https://developer.spotify.com/dashboard
- **Verification:** Test Spotify API call

### 17. Bluesky
- [ ] **Status:** NOT ROTATED
- **Service:** Bluesky Social
- **Keys to Rotate:**
  - `BLUESKY_PASSWORD` (Change account password!)
- **Steps:**
  1. Log into Bluesky
  2. Change password
  3. Update `.env`
- **Verification:** Test post creation

### 18. Google OAuth
- [ ] **Status:** NOT ROTATED
- **Service:** YouTube uploads, Google APIs
- **Keys to Rotate:**
  - `GOOGLE_OAUTH_CLIENT_ID`
  - `GOOGLE_OAUTH_CLIENT_SECRET`
  - `GEMINI_API_KEY`
  - `GOOGLE_API_KEY`
- **Rotation URL:** https://console.cloud.google.com/apis/credentials
- **Steps:**
  1. Create new OAuth 2.0 Client ID
  2. Create new API key
  3. Delete old credentials
  4. Update `.env`
- **Verification:** Test YouTube upload

---

## P2: MEDIUM - Data APIs

### 19. Groq
- [ ] **Status:** NOT ROTATED
- **Key:** `GROQ_API_KEY`
- **Rotation URL:** https://console.groq.com/keys

### 20. Hugging Face
- [ ] **Status:** NOT ROTATED
- **Key:** `HUGGING_FACE_API`
- **Rotation URL:** https://huggingface.co/settings/tokens

### 21. ClipDrop
- [ ] **Status:** NOT ROTATED
- **Key:** `CLIPDROP_API_KEY`
- **Rotation URL:** https://clipdrop.co/apis

### 22. SERPER
- [ ] **Status:** NOT ROTATED
- **Key:** `SERPER_API_KEY`
- **Rotation URL:** https://serper.dev/dashboard

### 23. News API
- [ ] **Status:** NOT ROTATED
- **Key:** `NEWS_API_KEY`
- **Rotation URL:** https://newsapi.org/account

### 24. Polygon (Stock Data)
- [ ] **Status:** NOT ROTATED
- **Keys to Rotate:**
  - `POLYGON_API_KEY`
  - `POLYGON_ACCESS_KEY_ID`
  - `POLYGON_SECRET_ACCESS_KEY`
- **Rotation URL:** https://polygon.io/dashboard/api-keys

### 25. Etherscan
- [ ] **Status:** NOT ROTATED
- **Key:** `ETHERSCAN_API_KEY`
- **Rotation URL:** https://etherscan.io/myapikey

### 26. CoinGecko
- [ ] **Status:** NOT ROTATED
- **Key:** `COINGECKO_API_KEY`
- **Rotation URL:** https://www.coingecko.com/en/api/pricing

---

## P3: LOW - Development/Test Services

### 27. Research APIs
- [ ] `CORE_API_KEY`
- [ ] `ELSEVIER_API_KEY`
- [ ] `NCBI_API_KEY`
- [ ] `SEC_API_KEY`
- [ ] `LEGISCAN_API_KEY`
- [ ] `GOVERNMENT_API_KEY`

### 28. Weather APIs
- [ ] `NOAA_API_KEY`
- [ ] `WEATHERAPI_KEY`

### 29. Sports APIs
- [ ] `THE_ODDS_API_KEY`
- [ ] `SPORTSRADAR_API_KEY`

### 30. Monitoring
- [ ] `DATADOG_API_KEY`
- [ ] `RESEND_API_KEY`

### 31. Miscellaneous
- [ ] `GIPHY_API_KEY`
- [ ] `TEST_AUTH_TOKEN`

---

## Post-Rotation Steps

### 1. Test All Integrations
```bash
# Run API key validation
python scripts/test_api_keys.py

# Start the platform
make start

# Test each feature category:
# - Image generation
# - Video generation
# - Audio generation
# - AI Assistant chat
# - 3D model generation
```

### 2. Remove .env from Git History
```bash
# Install BFG Repo Cleaner
brew install bfg

# Create backup
git clone --mirror git@github.com:your/repo.git backup-repo.git

# Remove .env from history
bfg --delete-files .env

# Clean up
git reflog expire --expire=now --all && git gc --prune=now --aggressive

# Force push (CAREFUL!)
git push --force
```

### 3. Update .gitignore
Ensure `.env` is in `.gitignore`:
```
.env
.env.local
.env.*.local
```

### 4. Verify No Credentials in Code
```bash
# Search for hardcoded credentials
grep -r "sk_live" --include="*.py" .
grep -r "sk-proj" --include="*.py" .
grep -r "sk-ant" --include="*.py" .
```

---

## Completion Tracking

| Priority | Total | Completed | Remaining |
|----------|-------|-----------|-----------|
| P0       | 4     | 0         | 4         |
| P1       | 7     | 0         | 7         |
| P2       | 14    | 0         | 14        |
| P3       | 6     | 0         | 6         |
| **Total**| **31**| **0**     | **31**    |

---

**Last Updated:** 2025-11-25
**Completed By:** [Your Name]
**Verified By:** [Reviewer Name]
