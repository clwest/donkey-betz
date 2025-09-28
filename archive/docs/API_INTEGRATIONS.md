# API Integrations & Configuration Guide
## Unified Donkey Betz Platform

## ✅ ACTIVE INTEGRATIONS

### 1. AI Language Models
| Provider | Status | Primary Use | Configuration |
|----------|--------|-------------|---------------|
| OpenAI | ✅ Active | GPT-4, Embeddings, DALL-E fallback | `OPENAI_API_KEY` |
| Anthropic | ✅ Active | Claude for complex reasoning | `ANTHROPIC_API_KEY` |
| Google | ✅ Active | Gemini Pro | `GOOGLE_API_KEY` / `GEMINI_API_KEY` |
| Groq | ✅ Active | Fast inference | `GROQ_API_KEY` |

### 2. Image Generation (PRIORITY ORDER)
| Provider | Priority | Status | Models | Configuration |
|----------|----------|--------|--------|---------------|
| Stability AI | 1st | ✅ Active | Stable Diffusion XL | `STABILITY_API_KEY` |
| Replicate | 2nd | ❌ Not configured | SDXL models | `REPLICATE_API_TOKEN` |
| OpenAI | 3rd | ✅ Active | DALL-E 3 | `OPENAI_API_KEY` |

### 3. Voice & Audio
| Provider | Status | Use Case | Configuration |
|----------|--------|----------|---------------|
| ElevenLabs | ✅ Active | Text-to-speech | `ELEVENLABS_API_KEY` |
| Runway | ✅ Active | Advanced audio/video | `RUNWAY_API_KEY` |

### 4. Data & Analytics
| Provider | Status | Use Case | Configuration |
|----------|--------|----------|---------------|
| Polygon | ✅ Active | Financial data | `POLYGON_API_KEY` |
| SEC | ✅ Active | Securities data | `SEC_API_KEY` |
| CoinGecko | ✅ Active | Crypto prices | `COINGECKO_API_KEY` |
| News API | ✅ Active | News aggregation | `NEWS_API_KEY` |

### 5. Other Services
| Provider | Status | Use Case | Configuration |
|----------|--------|----------|---------------|
| GitHub | ✅ Active | Code repository | `GITHUB_TOKEN` |
| Resend | ✅ Active | Email service | `RESEND_API_KEY` |
| Twilio | ✅ Active | SMS/Phone | `TWILIO_SID`, `TWILIO_SECRET` |
| Reddit | ✅ Active | Social data | `REDDIT_CLIENT_ID` |

## 🔧 CONFIGURATION

### Required in `.env` file:
```bash
# Core AI Providers (REQUIRED)
OPENAI_API_KEY="your-key-here"
STABILITY_API_KEY="your-key-here"

# Additional AI (RECOMMENDED)
ANTHROPIC_API_KEY="your-key-here"
GOOGLE_API_KEY="your-key-here"
GROQ_API_KEY="your-key-here"

# Database (REQUIRED)
DATABASE_URL=postgresql://postgres@localhost:5432/unified_donkey_betz
```

### Django Settings Configuration:
The `ai_core/settings.py` file automatically loads these from environment:
```python
AI_PROVIDERS = {
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
    'STABILITY_API_KEY': os.environ.get('STABILITY_API_KEY'),
    # ... other providers
}
```

## 🎨 IMAGE GENERATION SETUP

### Stable Diffusion Configuration:
1. **Get API Key**: Sign up at https://platform.stability.ai/
2. **Add to .env**: `STABILITY_API_KEY="sk-..."`
3. **Verify**: Run `python test_stable_diffusion.py`

### Provider Selection Logic:
```python
# Auto-selection priority (content/image_generation.py)
1. Check STABILITY_API_KEY → Use Stable Diffusion
2. Check REPLICATE_API_TOKEN → Use Replicate SDXL
3. Check OPENAI_API_KEY → Use DALL-E 3
4. No keys → Return error
```

### Available Styles:
- **Total**: 70+ styles optimized for SD/SDXL
- **Categories**: Photography, Digital Art, Traditional Art, Animation, Genre, 3D, Cultural
- **API Endpoint**: `GET /api/v1/styles/`

## 🤖 AGENT & ADVISOR SYSTEM

### Agent Registry:
- **Total Agents**: 149 specialized agents
- **Categories**: Research, Analysis, Content, Trading, Development
- **Access**: Via `agents.registry.AgentRegistry`

### Advisor Network:
- **Total Advisors**: 25 legendary advisors
- **Includes**: Warren Buffett, Cathie Wood, Ray Dalio, etc.
- **Access**: Via `advisors.registry.AdvisorRegistry`

## 📊 MONITORING & TESTING

### Test Commands:
```bash
# Test Stable Diffusion
python test_stable_diffusion.py

# List all available styles
python list_all_styles.py

# Test styles API endpoint
python test_styles_api.py

# Test with specific key
python test_sd_with_key.py
```

### Health Checks:
- **Database**: `psql -U postgres -d unified_donkey_betz -c "SELECT 1;"`
- **Redis**: `redis-cli ping`
- **API**: `curl http://localhost:8000/api/v1/health/`

## ⚠️ TROUBLESHOOTING

### Common Issues:

1. **Stable Diffusion not working**:
   - Check `STABILITY_API_KEY` in .env
   - Ensure key is in `AI_PROVIDERS` dict in settings.py
   - Verify with `python test_sd_with_key.py`

2. **Database connection errors**:
   - Ensure PostgreSQL is running
   - Check DATABASE_URL points to correct database
   - Verify pgvector extension: `SELECT * FROM pg_extension WHERE extname = 'vector';`

3. **Frontend not showing styles**:
   - Check Django server is running
   - Verify `/api/v1/styles/` returns data
   - Check browser console for errors

## 🔐 SECURITY NOTES

1. **Never commit API keys** - Keep them in `.env`
2. **Use environment variables** - Don't hardcode keys
3. **Rotate keys regularly** - Especially for production
4. **Limit API permissions** - Use read-only where possible
5. **Monitor usage** - Set up billing alerts

## 📝 ADDING NEW INTEGRATIONS

To add a new API integration:

1. **Add to .env**:
   ```bash
   NEW_SERVICE_API_KEY="your-key-here"
   ```

2. **Update settings.py**:
   ```python
   AI_PROVIDERS['NEW_SERVICE_API_KEY'] = os.environ.get('NEW_SERVICE_API_KEY')
   ```

3. **Create service class**:
   ```python
   # services/new_service.py
   class NewService:
       def __init__(self):
           self.api_key = settings.AI_PROVIDERS.get('NEW_SERVICE_API_KEY')
   ```

4. **Test integration**:
   ```bash
   python test_new_service.py
   ```

---

**Last Updated**: September 18, 2025
**Status**: All Core APIs Operational ✅