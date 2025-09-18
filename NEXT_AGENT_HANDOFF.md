# 🚀 UNIFIED DONKEY BETZ PLATFORM - AGENT HANDOFF DOCUMENT

## Executive Summary
This platform is a sophisticated AI-powered job application and income generation system built by Chris (transitioning from car dealer to developer). The core architecture is solid, but many "AI" features are currently mocked and need real implementation.

**Current Reality Score: 55% Real / 45% Mocked**

## 🎯 CRITICAL PRIORITIES (Complete These First!)

### 1. Fix Authentication & Profile Data Flow
**Problem**: Profile data doesn't persist properly between sessions
**Location**: `/core/views_enhanced_profile.py` and `/intelligence/views_ai_jobs.py`
**Steps**:
```bash
1. cd /Users/donkeyking/development/unified-donkey-betz
2. Fix the profile data synchronization:
   - Edit core/views_enhanced_profile.py:141-173
   - Ensure profile saves to BOTH database AND session
3. Test: Update profile at http://localhost:3000/profile
4. Verify: Apply to job at http://localhost:3000/ai-job-tracker
```

### 2. Connect Real LLM APIs (Currently Mocked!)
**Problem**: Many components return fake responses instead of using OpenAI
**Critical Files**:
- `/intelligence/ai_job_application_pipeline.py` (LINE 89-95: Returns mock data!)
- `/backend/intelligence/income_builder.py` (LINE 245: Fake opportunity generation)
- `/agents/factory.py` (LINE 112: Mock agent creation)

**Implementation Steps**:
```python
# 1. Ensure OpenAI client is initialized:
import openai
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 2. Replace ALL mock returns with real API calls:
# FIND: return {"mock": True, "data": "fake"}
# REPLACE WITH:
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "system", "content": prompt}],
    temperature=0.7
)
return {"real": True, "data": response.choices[0].message.content}
```

### 3. Implement Real Web Scraping for Spiders
**Problem**: All 13 spiders return hardcoded job data
**Location**: `/intelligence/views_ai_jobs.py` (LINES 39-85)
**Current State**: Static array of 5 fake jobs

**Real Implementation**:
```python
# Install required packages:
pip install beautifulsoup4 requests scrapy selenium

# Create real spider at /backend/spiders/real_job_spider.py:
import requests
from bs4 import BeautifulSoup

class RealJobSpider:
    def scrape_guru_jobs(self):
        response = requests.get('https://www.guru.com/d/jobs/')
        soup = BeautifulSoup(response.content, 'html.parser')
        jobs = []
        for job in soup.find_all('div', class_='job-listing'):
            jobs.append({
                'title': job.find('h3').text,
                'company': job.find('span', class_='employer').text,
                'budget': job.find('span', class_='budget').text,
                'description': job.find('p').text
            })
        return jobs
```

## 📁 PROJECT STRUCTURE & KEY FILES

```
unified-donkey-betz/
├── frontend/                      # React Frontend (Port 3000)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AIJobTrackerPage.tsx    # Job application UI
│   │   │   └── ProfilePage.tsx         # User profile (NEEDS WORK)
│   │   ├── components/
│   │   │   ├── PersonalAssistant.tsx   # AI Chat (75% REAL)
│   │   │   └── profile/
│   │   │       └── ProfessionalProfile.tsx # Profile form
│   │   └── services/
│   │       └── api.config.ts           # API configuration
│   │
├── backend/                       # Django Backend (Port 8000)
│   ├── intelligence/
│   │   ├── views_ai_jobs.py           # Job endpoints (MOCKED!)
│   │   ├── ai_job_application_pipeline.py # Application generator (MOCKED!)
│   │   └── income_builder.py          # Income opportunities (PARTIAL MOCK)
│   │
│   ├── core/
│   │   ├── views_profile.py           # Profile management
│   │   ├── views_enhanced_profile.py  # Extended profile
│   │   └── views_personal_assistant_dev.py # Assistant API (REAL!)
│   │
│   └── agents/
│       ├── registry.py                # 149 agents (REGISTERED ONLY)
│       └── factory.py                 # Agent creation (MOCKED!)
```

## 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE

### Phase 1: Fix Core Infrastructure (Days 1-2)

#### A. Database & Session Management
```bash
# 1. Ensure PostgreSQL is running
brew services start postgresql

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Create test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('testuser', 'test@example.com', 'password123')
>>> user.save()
```

#### B. Fix Profile Synchronization
Edit `/core/views_enhanced_profile.py`:
```python
# Line 141-173, ensure both DB and session save:
profile.save()  # Save to database
request.session[f'extended_profile_{request.user.id}'] = {
    'full_name': profile.full_name,
    'professional_summary': profile.professional_summary,
    'skills': profile.skills,
    'work_history': profile.work_history,
    # ... all fields
}
request.session.modified = True
```

### Phase 2: Connect Real AI Services (Days 3-4)

#### A. Configure API Keys
Create `.env` file:
```bash
OPENAI_API_KEY=sk-...your-key...
ANTHROPIC_API_KEY=sk-ant-...your-key...
HUGGINGFACE_TOKEN=hf_...your-token...
```

#### B. Replace Mock Implementations

**File: `/intelligence/ai_job_application_pipeline.py`**
```python
# CURRENT (Line 89-95):
def generate_application(self, job_data, user_profile):
    return {
        "resume": "Mock resume content",
        "cover_letter": "Mock cover letter"
    }

# REPLACE WITH:
def generate_application(self, job_data, user_profile):
    prompt = f"""
    Create a job application for:
    Job: {job_data['title']} at {job_data['company']}

    Applicant Profile:
    Name: {user_profile.get('full_name')}
    Experience: {user_profile.get('professional_summary')}
    Skills: {', '.join(user_profile.get('skills', []))}

    Generate:
    1. Tailored cover letter
    2. Key resume points
    """

    response = self.openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content
    # Parse and structure the response
    return {
        "resume": extract_resume_section(content),
        "cover_letter": extract_cover_letter_section(content),
        "personalized": True,
        "match_score": calculate_real_match_score(job_data, user_profile)
    }
```

### Phase 3: Implement Real Data Collection (Days 5-6)

#### A. Real Job Scraping
Create `/backend/spiders/live_job_scraper.py`:
```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict

class LiveJobScraper:
    def __init__(self):
        self.sources = {
            'indeed': 'https://www.indeed.com/jobs?q=developer&l=remote',
            'linkedin': 'https://www.linkedin.com/jobs/search/?keywords=developer',
            'remoteok': 'https://remoteok.io/remote-dev-jobs',
            'weworkremotely': 'https://weworkremotely.com/categories/remote-programming-jobs'
        }

    async def scrape_all(self) -> List[Dict]:
        """Scrape all job sources concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.scrape_indeed(session),
                self.scrape_remoteok(session),
                # Add more scrapers
            ]
            results = await asyncio.gather(*tasks)
            return [job for sublist in results for job in sublist]

    async def scrape_indeed(self, session) -> List[Dict]:
        """Scrape Indeed jobs"""
        async with session.get(self.sources['indeed']) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            jobs = []
            for job_card in soup.find_all('div', class_='job_seen_beacon'):
                try:
                    jobs.append({
                        'id': job_card.get('data-jk'),
                        'title': job_card.find('h2', class_='jobTitle').text.strip(),
                        'company': job_card.find('span', class_='companyName').text.strip(),
                        'location': job_card.find('div', class_='companyLocation').text.strip(),
                        'salary': self.extract_salary(job_card),
                        'description': job_card.find('div', class_='job-snippet').text.strip(),
                        'source': 'indeed',
                        'url': f"https://www.indeed.com/viewjob?jk={job_card.get('data-jk')}",
                        'posted_date': job_card.find('span', class_='date').text.strip()
                    })
                except Exception as e:
                    print(f"Error parsing job: {e}")
                    continue

            return jobs
```

#### B. Update Spider View
Edit `/intelligence/views_ai_jobs.py`:
```python
from backend.spiders.live_job_scraper import LiveJobScraper

class AIJobOpportunitiesView(View):
    def get(self, request):
        # Initialize real scraper
        scraper = LiveJobScraper()

        # Get real jobs (with caching)
        cache_key = 'live_jobs'
        jobs = cache.get(cache_key)

        if not jobs:
            # Scrape fresh data
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            jobs = loop.run_until_complete(scraper.scrape_all())

            # Cache for 1 hour
            cache.set(cache_key, jobs, 3600)

        # Apply AI scoring
        for job in jobs:
            job['aiScore'] = self.calculate_ai_score(job, request.user)

        return JsonResponse({
            'success': True,
            'jobs': jobs,
            'stats': {
                'total': len(jobs),
                'sources': len(set(j['source'] for j in jobs)),
                'timestamp': datetime.now().isoformat()
            }
        })
```

### Phase 4: Connect Revenue Systems (Days 7-8)

#### A. Real Payment Integration
```python
# Install Stripe
pip install stripe

# /backend/payments/stripe_handler.py
import stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class PaymentHandler:
    def create_application_payment(self, user, job_id, amount):
        """Charge for premium job applications"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'user_id': user.id,
                    'job_id': job_id,
                    'type': 'job_application'
                }
            )
            return payment_intent
        except stripe.error.StripeError as e:
            return {'error': str(e)}
```

### Phase 5: Activate Agent System (Days 9-10)

#### A. Make Agents Actually Execute
Edit `/agents/factory.py`:
```python
class AgentFactory:
    def create_agent(self, agent_type: str):
        """Create a real, executable agent"""

        # Map agent types to real implementations
        agent_map = {
            'web_scraper': WebScraperAgent,
            'content_writer': ContentWriterAgent,
            'data_analyzer': DataAnalyzerAgent,
            'code_generator': CodeGeneratorAgent
        }

        agent_class = agent_map.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Create and initialize real agent
        agent = agent_class()
        agent.initialize_llm(model="gpt-4")
        return agent

class WebScraperAgent:
    def __init__(self):
        self.name = "WebScraperAgent"
        self.llm = None

    def initialize_llm(self, model):
        self.llm = openai.OpenAI()
        self.model = model

    async def execute(self, task: str):
        """Actually execute the scraping task"""
        # First, use LLM to understand the task
        analysis = self.llm.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"Analyze this web scraping task and provide the URL and selectors: {task}"
            }]
        )

        # Extract URL and selectors from LLM response
        config = json.loads(analysis.choices[0].message.content)

        # Perform actual scraping
        async with aiohttp.ClientSession() as session:
            async with session.get(config['url']) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                results = []
                for selector in config['selectors']:
                    elements = soup.select(selector)
                    results.extend([e.text.strip() for e in elements])

                return {
                    'success': True,
                    'data': results,
                    'source': config['url']
                }
```

## 🔍 VERIFICATION CHECKLIST

After implementing each phase, verify:

### ✅ Phase 1 Verification
```bash
# Test profile persistence
1. Update profile at /profile
2. Logout and login
3. Check profile data is retained
```

### ✅ Phase 2 Verification
```bash
# Test real AI responses
1. Open Personal Assistant
2. Ask: "Generate a Python function to calculate fibonacci"
3. Should receive actual code, not generic response
```

### ✅ Phase 3 Verification
```bash
# Test real job scraping
1. Go to /ai-job-tracker
2. Click "Start Spiders"
3. Should see NEW jobs each time (not same 5)
```

### ✅ Phase 4 Verification
```bash
# Test payment flow
1. Apply to premium job
2. Should redirect to Stripe checkout
3. Check webhook receives payment confirmation
```

### ✅ Phase 5 Verification
```bash
# Test agent execution
curl -X POST http://localhost:8000/api/v1/agents/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "web_scraper",
    "task": "Scrape latest tech news from HackerNews"
  }'
# Should return real, current data
```

## 🚨 CRITICAL WARNINGS

1. **Never commit API keys** - Always use environment variables
2. **Rate limiting** - Implement delays for web scraping (1-2 seconds between requests)
3. **Error handling** - Always have fallbacks when APIs fail
4. **Caching** - Cache expensive API calls (use Redis)
5. **Testing** - Test each component in isolation before integration

## 📊 SUCCESS METRICS

Track progress with these metrics:

| Component | Current | Target | Priority |
|-----------|---------|---------|----------|
| Personal Assistant | 75% | 100% | HIGH |
| Job Scraping | 0% | 100% | CRITICAL |
| Application Generation | 40% | 100% | CRITICAL |
| Agent Execution | 30% | 100% | HIGH |
| Revenue Tracking | 10% | 100% | MEDIUM |
| Spider Network | 0% | 100% | HIGH |

## 🆘 TROUBLESHOOTING GUIDE

### Issue: "403 Forbidden" on API calls
**Solution**: Add CSRF token to request headers
```javascript
headers: {
  'X-CSRFToken': getCookie('csrftoken'),
  'Content-Type': 'application/json'
}
```

### Issue: "OpenAI API key not found"
**Solution**:
```bash
export OPENAI_API_KEY='sk-...'
# OR add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Issue: Jobs not updating
**Solution**: Clear Redis cache
```bash
redis-cli FLUSHALL
```

### Issue: Agent not executing
**Solution**: Check agent is registered
```python
python manage.py shell
>>> from agents.registry import AgentRegistry
>>> registry = AgentRegistry()
>>> registry.list_agents()  # Should show your agent
```

## 📞 SUPPORT RESOURCES

- **Django Docs**: https://docs.djangoproject.com/
- **React Docs**: https://react.dev/
- **OpenAI API**: https://platform.openai.com/docs/
- **Stripe Docs**: https://stripe.com/docs
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

## 🎯 FINAL GOAL

Transform this platform from 55% real to 100% functional:
- All AI features use real LLMs
- All spiders scrape real data
- All agents execute real tasks
- Revenue tracking with real payments
- Full end-to-end job application flow

**Estimated Timeline**: 10 days of focused development
**Required Skills**: Python, React, API Integration, Web Scraping
**Budget for APIs**: ~$50-100/month (OpenAI, Stripe, etc.)

---

## Next Agent Instructions

1. Start with Phase 1 - Fix authentication and profile flow
2. Test each fix before moving to next phase
3. Keep the TodoWrite tool updated with progress
4. Document any issues in this file
5. When complete, system should pass all verification checks

Good luck! The foundation is solid - you just need to connect the dots! 🚀