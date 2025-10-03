# 🔐 SECRET ROTATION GUIDE - CRITICAL SECURITY RESPONSE

## 🚨 IMMEDIATE ACTIONS REQUIRED

**STATUS**: CRITICAL - Multiple API keys and secrets have been exposed in version control

### 1. IMMEDIATE CREDENTIAL ROTATION (DO THIS NOW)

All the following credentials must be rotated immediately as they have been exposed:

#### AI/ML API Keys (HIGH PRIORITY - EXPENSIVE)
- [ ] **OpenAI API Key**: `sk-proj-hd1B1KWFt7rW2UARfx...` → [Rotate at OpenAI Dashboard](https://platform.openai.com/api-keys)
- [ ] **Anthropic API Key**: `sk-ant-api03-gZ6bvJU30wgg...` → [Rotate at Anthropic Console](https://console.anthropic.com/)
- [ ] **Groq API Key**: `[REDACTED - HISTORICAL SECRET]` → [Rotate at Groq Console](https://console.groq.com/)
- [ ] **Gemini API Key**: `[REDACTED - HISTORICAL SECRET]` → [Rotate at Google AI Studio](https://aistudio.google.com/)
- [ ] **Stability AI Key**: `sk-9DSt2cM3yZ7J6ALpna9r...` → [Rotate at Stability AI](https://platform.stability.ai/account/keys)
- [ ] **Runway API Key**: `key_1e5dd7417caf907f50689...` → [Rotate at Runway](https://runwayml.com/account/api-keys)
- [ ] **ElevenLabs API Key**: `sk_659d75e6adf724bede0dc...` → [Rotate at ElevenLabs](https://elevenlabs.io/account/api-keys)
- [ ] **Hugging Face API**: `hf_BfeZQUQhNtlDpbLPvwuy...` → [Rotate at HuggingFace](https://huggingface.co/settings/tokens)
- [ ] **Replicate API Token**: `r8_bEsGdDy7ftH4MNMrHvA2...` → [Rotate at Replicate](https://replicate.com/account/api-tokens)

#### Financial & Cryptocurrency APIs (CRITICAL - FINANCIAL EXPOSURE)
- [ ] **Coinbase Private Key**: `-----BEGIN EC PRIVATE KEY-----...` → [Rotate at Coinbase Advanced Trade](https://www.coinbase.com/advanced-trade/api)
- [ ] **Polygon API Key**: `[REDACTED - HISTORICAL SECRET]` → [Rotate at Polygon.io](https://polygon.io/dashboard/api-keys)
- [ ] **SEC API Key**: `b935b22cdd04effc926a215...` → [Rotate at SEC API](https://sec-api.io/dashboard)
- [ ] **Alpha Vantage API Key**: `GYZDWBV9T7E8B6FE` → [Rotate at Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- [ ] **Etherscan API Key**: `KDCRHB7RDZHRZCDE5ZACJN...` → [Rotate at Etherscan](https://etherscan.io/myapikey)
- [ ] **CoinGecko API Key**: `CG-2b2J8DfXyFvfnPVotipm...` → [Rotate at CoinGecko](https://www.coingecko.com/en/api/pricing)

#### Communication APIs (MODERATE PRIORITY)
- [ ] **Twilio SID/Secret**: `ACb9e199bdf7a8ca0a3519...` → [Rotate at Twilio Console](https://console.twilio.com/)
- [ ] **Telegram API**: `28229112` / `cb79bc1134d37e1613...` → [Rotate at Telegram](https://my.telegram.org/auth)
- [ ] **Telegram Bot Token**: `5119451970:AAFwTKw1MqiPk...` → [Rotate with @BotFather](https://t.me/botfather)

#### Social Media APIs
- [ ] **Reddit Client ID/Secret**: `[REDACTED - HISTORICAL SECRET]` → [Rotate at Reddit Apps](https://www.reddit.com/prefs/apps)
- [ ] **Spotify Client ID/Secret**: `46792cc0b9784b288a6ec3...` → [Rotate at Spotify Dashboard](https://developer.spotify.com/dashboard)

#### Search & Data APIs
- [ ] **Serper API Key**: `ba6bd09c6f712179849a5d...` → [Rotate at Serper](https://serper.dev/api-key)
- [ ] **News API Key**: `efe68addb906464e93d601...` → [Rotate at NewsAPI](https://newsapi.org/account)
- [ ] **GitHub Token**: `github_pat_11AQCTDGQ0hjFHSGNDI...` → [Rotate at GitHub](https://github.com/settings/tokens)

#### Government/Weather APIs
- [ ] **NOAA API Key**: `ybcsemxOyOlnOQaouvBwmg...` → [Rotate at NOAA](https://www.weather.gov/documentation/services-web-api)
- [ ] **WeatherAPI Key**: `56ce00f5b2444f229e919...` → [Rotate at WeatherAPI](https://www.weatherapi.com/my/)
- [ ] **LegiscanAPI Key**: `d6e18bc35ae97873941e32...` → [Rotate at Legiscan](https://legiscan.com/legiscan)

#### Database & Infrastructure
- [ ] **Database Password**: `secure_password` → Change in PostgreSQL and update .env
- [ ] **Django Secret Key**: `super-secret-donkey-business` → Generate new key
- [ ] **Datadog API Key**: `1716264871a418a1a8ac8a...` → [Rotate at Datadog](https://app.datadoghq.com/organization-settings/api-keys)
- [ ] **Resend API Key**: `re_GWojSote_MrgHYSW2vfSp...` → [Rotate at Resend](https://resend.com/api-keys)

### 2. IMMEDIATE SECURITY ACTIONS

#### A. Git History Cleanup
```bash
# WARNING: This will rewrite git history - coordinate with team first
git filter-branch --tree-filter 'rm -f backend/.env' HEAD
git push --force-with-lease origin main
```

#### B. Check for Unauthorized API Usage
1. **OpenAI Dashboard**: Check usage for unusual spikes
2. **Anthropic Console**: Review recent API calls
3. **Financial APIs**: Check for unauthorized transactions
4. **All other APIs**: Review usage patterns for anomalies

#### C. Database Security
```bash
# Change database password
sudo -u postgres psql
ALTER USER moveyourazz_user WITH PASSWORD 'new_secure_password_here';
\q
```

### 3. SECURE REPLACEMENT PROCESS

#### Step 1: Generate New Secrets
```bash
# Generate new Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate secure database password
openssl rand -base64 32
```

#### Step 2: Update .env File
1. Copy `.env.example` to `.env`
2. Fill in all new API keys and secrets
3. Verify all services work with new credentials

#### Step 3: Update Production Environment
1. Update all environment variables in production
2. Restart all services
3. Verify application functionality

### 4. ADDITIONAL FILES TO CLEAN

#### Remove Hardcoded Secrets From:
- [ ] `/backend/setup_postgres.sh` (Line 11: DB_PASSWORD)
- [ ] `/frontend/momentum_flutter/android/app/google-services.json` (Firebase config)
- [ ] `/CURRENT_STATE/POLYGON_API_FIX_INSTRUCTIONS.md` (Line 13: API key)
- [ ] All test files with `testpass123` → Replace with environment variables

#### Universal Builder Files (50+ instances):
- [ ] `/backend/universal_builder/builder_agents.py` (Multiple DB connection strings)
- [ ] All files in `/backend/universal_builder/` with hardcoded passwords
- [ ] All files in `/backend/tests/` with hardcoded test passwords

### 5. PREVENTION MEASURES

#### A. Pre-commit Hooks
```bash
# Install pre-commit hooks to prevent future secret leaks
pip install pre-commit
pre-commit install
```

#### B. Secret Detection
Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

#### C. Environment Variable Validation
Create validation script in `/backend/scripts/validate_env.py`:
```python
import os
import sys

REQUIRED_VARS = [
    'OPENAI_API_KEY',
    'SECRET_KEY',
    'DATABASE_URL',
    # Add all required vars
]

for var in REQUIRED_VARS:
    if not os.getenv(var):
        print(f"ERROR: {var} not set")
        sys.exit(1)
```

### 6. MONITORING & ALERTING

#### A. API Usage Monitoring
- Set up billing alerts for all paid APIs
- Monitor unusual usage patterns
- Set up notifications for failed authentication attempts

#### B. Security Monitoring
- Enable audit logging for database access
- Set up alerts for failed login attempts
- Monitor for unusual API access patterns

### 7. TEAM COORDINATION

#### A. Communication
- [ ] Notify all team members of credential rotation
- [ ] Update shared documentation with new setup process
- [ ] Schedule security review meeting

#### B. Access Control
- [ ] Review who has access to production environment
- [ ] Implement principle of least privilege
- [ ] Set up proper secret management system (AWS Secrets Manager, HashiCorp Vault, etc.)

### 8. VERIFICATION CHECKLIST

After completing rotation:
- [ ] All applications start successfully
- [ ] All API integrations work correctly
- [ ] No secrets visible in git history
- [ ] All team members have updated credentials
- [ ] Monitoring and alerting configured
- [ ] Documentation updated

### 9. EMERGENCY CONTACTS

If you detect unauthorized usage:
- **OpenAI**: support@openai.com
- **Anthropic**: support@anthropic.com
- **Financial APIs**: Contact support immediately
- **Database**: Immediately change passwords and review logs

---

## 🔒 LONG-TERM SECURITY RECOMMENDATIONS

1. **Implement proper secret management** (AWS Secrets Manager, Vault)
2. **Use IAM roles** instead of API keys where possible
3. **Implement API key rotation** automation
4. **Set up comprehensive monitoring** and alerting
5. **Regular security audits** of the codebase
6. **Employee security training** on secret handling

---

**REMEMBER**: This is a critical security incident. All exposed credentials must be rotated immediately to prevent financial losses and data breaches.