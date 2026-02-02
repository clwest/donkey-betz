# Persona Agents Reference

**Last Updated:** Session 901 (February 1, 2026)
**Status:** 141 Persona Agents | 15 Categories | Active in ConceptForge & Content Production

---

## What Are Persona Agents?

**Persona Agents** are database-only AI agents that don't have Python code implementations. Unlike the 73 **Core Agents** (ImageAgent, VideoAgent, ResearchAgent, etc.) that have actual Python classes in `core/agents/`, Persona Agents exist only as database records and participate in the system through:

1. **LLM Conversations** - Their perspective is generated via prompts enriched with real-world spider data
2. **ConceptForge Pipeline** - They serve as advisors during the 6-stage think tank process
3. **Content Production** - They provide domain expertise during planning, creation, and review phases

### The Two Agent Types

| Type | Count | Has Python Code? | Example |
|------|-------|------------------|---------|
| **Core Agents** | 73 | Yes (`core/agents/*.py`) | ImageAgent, ResearchAgent, ThinkingAgent |
| **Persona Agents** | 141 | No (database only) | Income Builder Pro, SEO Content Optimizer |
| **Total** | 214 | | |

---

## Persona Agent Categories (15 Types)

| Category | Count | Examples | Spider Data Sources |
|----------|-------|----------|---------------------|
| **income** | 20 | Income Builder Pro, Passive Income Architect, Revenue Stream Analyzer | RemoteOK, WeWorkRemotely, Adzuna |
| **career** | 15 | Resume Optimizer AI, Salary Negotiation Expert, Career Path Strategist | Job boards, HackerNews, Medium |
| **content** | 15 | SEO Content Optimizer, Content Strategy Planner, Social Media Content Creator | Medium, Substack, YouTube |
| **business** | 14 | Business Model Canvas Expert, Startup Pitch Consultant | TechCrunch, Crunchbase |
| **job_search** | 12 | Job Application Optimizer, Interview Coach Pro | RemoteOK, WeWorkRemotely, GitHub Jobs |
| **finance** | 12 | Investment Portfolio Manager, Budget Optimization Expert, Personal Finance Manager | Yahoo Finance, Polygon, Finnhub |
| **ai_ml** | 11 | AI Implementation Specialist, Machine Learning Advisor | HuggingFace, Kaggle, GitHub |
| **marketing** | 10 | Digital Marketing Strategist, Growth Hacker Pro, Conversion Rate Optimizer | Medium, ProductHunt, Reddit |
| **creative** | 10 | Brand Identity Designer, Visual Content Creator | Behance, Awwwards, Unsplash |
| **analytics** | 7 | Data Analytics Expert, Metrics Dashboard Designer | Kaggle, HackerNews |
| **research** | 5 | Market Research Analyst, Trend Analysis Expert | HackerNews, Science feeds |
| **automation** | 4 | Workflow Automation Expert, Process Optimizer | HackerNews, ProductHunt, GitHub |
| **consulting** | 3 | Business Strategy Consultant | Medium, Business news |
| **investment** | 1 | Investment Analyst | Yahoo Finance, Kalshi |
| **clean_architecture** | 2 | Clean Code Expert | GitHub, DevTo |

---

## How Persona Agents Work

### 1. PersonaAdvisorService (`core/services/persona_advisor_service.py`)

This service enables Persona Agents to provide advisory input:

```python
from core.services.persona_advisor_service import PersonaAdvisorService

advisor = PersonaAdvisorService()
result = advisor.get_advice(
    persona_name='Content Strategy Planner',
    topic='AI trends for 2026',
    advice_type='content_strategy',  # or seo_optimization, marketing_angle, quality_review, trend_analysis
    context={'content_type': 'blog_post'}
)
```

**Advice Types Available:**
- `content_strategy` - Key angles, hooks, must-include points, pitfalls
- `seo_optimization` - Keywords, titles, meta descriptions, structure
- `marketing_angle` - Target audiences, platforms, timing, CTAs
- `quality_review` - Relevance score, completeness, go/no-go
- `trend_analysis` - What's trending, emerging themes, opportunity windows

### 2. PersonaAgentContextBuilder (`core/services/persona_agent_context.py`)

Maps Persona Agent types to relevant spider data sources:

```python
PERSONA_SPIDER_MAPPINGS = {
    'income': {
        'spiders': ['remoteok', 'weworkremotely', 'adzuna', 'github_jobs'],
        'keywords': ['remote', 'freelance', 'gig', 'income'],
        'description': 'job opportunities and income sources',
    },
    'finance': {
        'spiders': ['yahoo_finance', 'polygon_finance', 'finnhub', 'coingecko'],
        'keywords': ['market', 'stock', 'investment', 'finance'],
        'description': 'market data and investment opportunities',
    },
    # ... 15 categories total
}
```

### 3. Content Production Integration

Persona Agents are automatically suggested based on content type and production phase:

```python
CONTENT_PRODUCTION_ADVISORS = {
    'blog_post': {
        'planning': ['Content Strategy Planner', 'SEO Content Optimizer'],
        'creation': ['Content Writer Pro', 'Copywriting Specialist'],
        'optimization': ['Digital Marketing Strategist'],
        'review': ['Trend Analysis Expert', 'Audience Engagement Specialist'],
    },
    'podcast': {
        'planning': ['Content Strategy Planner', 'Audio Content Creator'],
        'creation': ['Podcast Script Writer', 'Storytelling Expert'],
        # ...
    },
    # ... video, newsletter, social_campaign
}
```

---

## Where Personas Are Used

### 1. ConceptForge Pipeline (Session 863)

The autonomous think tank uses Persona Agents as domain advisors:

```python
# core/conceptforge/labs.py
@dataclass
class DomainLab:
    name: str
    domain: str
    persona_advisors: List[str]  # Persona agents for input

# Example: Legal Lab
DomainLab(
    name='Legal Lab',
    domain='legal',
    persona_advisors=['Personal Finance Manager', 'Tax Strategy Advisor'],
)
```

### 2. Content Production Teams (Session 812)

Content creation workflows consult relevant Persona Agents for planning and review.

### 3. HiveMind Conversations

When agents discuss topics, Persona Agents can be invited based on their domain expertise.

---

## Database Structure

Persona Agents are stored in the `Agent` model (`core/models_unified_system.py`):

```python
class Agent(models.Model):
    name = models.CharField(max_length=255)          # "Income Builder Pro"
    agent_type = models.CharField(max_length=50)     # "income"
    description = models.TextField()                  # What they do
    specialization = models.CharField(max_length=100) # Domain specialty
    capabilities = models.JSONField()                # What they can do
    # ... other fields
```

**Key difference from Core Agents:**
- Core Agents: name matches a class in `core/agents/` (e.g., "ImageAgent" → `ImageAgent`)
- Persona Agents: name does NOT match any Python class, exist only in database

---

## How to Check if an Agent is a Persona

```python
from core.services.persona_agent_context import get_persona_context_builder

builder = get_persona_context_builder()
agent = Agent.objects.get(name='Income Builder Pro')

is_persona = builder.is_persona_agent(agent)  # True
```

The check works by seeing if the agent name exists in `AgentRouter.AGENT_MAP`. If not, it's a Persona Agent.

---

## Creating New Persona Agents

Persona Agents are loaded via management command from `load_all_agents_advisors.py`:

```bash
python manage.py load_all_agents_advisors
```

To add new Persona Agents, add them to the appropriate category in that file.

---

## Production Stats

```
=== Agent Type Breakdown (Production) ===
core: 73          # Python-implemented agents
income: 20        # Persona: job/income opportunities
career: 15        # Persona: career development
content: 15       # Persona: content creation
business: 14      # Persona: business strategy
job_search: 12    # Persona: job hunting
finance: 12       # Persona: financial planning
ai_ml: 11         # Persona: AI/ML expertise
marketing: 10     # Persona: marketing strategy
creative: 10      # Persona: design/creative
analytics: 7      # Persona: data analytics
research: 5       # Persona: research methods
automation: 4     # Persona: workflow automation
consulting: 3     # Persona: consulting
investment: 1     # Persona: investment
clean_architecture: 2  # Persona: code quality
─────────────────────────────────────────
Total: 214 agents (73 core + 141 persona)
```

---

## Key Files

| File | Purpose |
|------|---------|
| `core/services/persona_advisor_service.py` | Main service for getting Persona advice |
| `core/services/persona_agent_context.py` | Spider data context builder for Personas |
| `core/management/commands/load_all_agents_advisors.py` | Loads Persona Agents to database |
| `core/conceptforge/labs.py` | Uses Personas as advisors in ConceptForge |

---

## "Persona" in Agent Dreams & Conversations

**Important Clarification:** When you see "persona" mentioned in agent dreams and conversations (792+ occurrences), the agents are typically discussing **marketing/customer personas** - NOT the system's Persona Agents.

### The Two Different "Personas"

| Term | What It Means | Where It Appears |
|------|---------------|------------------|
| **Customer Persona** | Marketing concept - fictional representation of target customer (e.g., "Maya the solo maker") | Agent dreams, content strategy, marketing outputs |
| **Persona Agent** | System component - 141 database-only AI agents that provide domain expertise | Code only (`core/services/persona_*.py`) |

### Examples from Agent Dreams

- **"Living Persona Playbooks for Growth"** - Ideas about making customer persona templates more dynamic
- **"Solo-maker Maya wants to ship something professional..."** - A fictional customer persona
- **"prioritized personas built from learned notes"** - Marketing strategy about audience segments

These are normal content strategy outputs. The agents (Content Strategy Planner, Trend Analysis Expert, etc.) generate creative business ideas, and "customer personas" is a standard marketing concept.

### No Dynamic Agent Creation

All 214 agents were bulk-loaded on **Jan 22-23, 2026** via management command. The system does NOT dynamically create new agents. When you see "persona" in agent output, it's marketing content, not system introspection.

---

## Relationship to Signal Intelligence

The Signal Intelligence system (Session 900) can detect patterns like "persona research demand spike" when spider data shows increased interest in persona-related topics. When this happens:

1. `SignalCluster` records the pattern
2. `AutoTopic` suggests a conversation topic
3. Relevant Persona Agents can be invited to discuss

*Note: As of Session 901, no SignalClusters currently mention "persona" - the examples in Session 900 docs were illustrative.*

---

## See Also

- [AGENTS.md](AGENTS.md) - Core agent documentation (73 agents with Python code)
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [handoffs/SESSION_812_CONTENT_PRODUCTION_TEAMS.md](handoffs/SESSION_812_CONTENT_PRODUCTION_TEAMS.md) - When Persona Advisors were added
- [handoffs/SESSION_790_PERSONA_CONTEXT.md](handoffs/SESSION_790_PERSONA_CONTEXT.md) - Persona context builder
