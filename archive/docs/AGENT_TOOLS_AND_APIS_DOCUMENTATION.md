# Agent Tools and APIs Documentation
## Unified Donkey Betz Platform

### Executive Summary
The unified-donkey-betz platform has an extensive collection of integrated tools and APIs available for agents. While the original donkey-betz-agent-orchestra referenced several research tools (web search, DuckDuckGo, ArXiv, Reddit, etc.), these haven't been fully implemented in the current codebase. However, the platform has rich infrastructure ready to support these integrations.

---

## Currently Integrated APIs and Services

### 1. AI/LLM Providers
- **OpenAI API** (`OPENAI_API_KEY`)
  - Models: GPT-5, GPT-5-mini, GPT-4
  - Used for: Agent intelligence, embeddings, content generation
  - Status: ✅ Fully integrated

- **Anthropic API** (`ANTHROPIC_API_KEY`)
  - Models: Claude family
  - Used for: Alternative LLM provider
  - Status: ✅ Configured

- **Google AI** (`GOOGLE_API_KEY`)
  - Used for: Alternative LLM provider
  - Status: ✅ Configured

- **Additional LLM Providers**:
  - Replicate (`REPLICATE_API_KEY`)
  - Mistral (`MISTRAL_API_KEY`)
  - Cohere (`COHERE_API_KEY`)
  - Groq (`GROQ_API_KEY`)
  - DeepSeek (`DEEPSEEK_API_KEY`)

### 2. Media Generation APIs
- **Stability AI** (`STABILITY_API_KEY`)
  - Used for: Image generation (DALL-E alternative)
  - Status: ✅ Configured

- **ElevenLabs** (`ELEVENLABS_API_KEY`)
  - Used for: Voice synthesis/TTS
  - Status: ✅ Configured

- **GIPHY** (`GIPHY_API_KEY`)
  - Used for: GIF integration
  - Status: ✅ Configured

### 3. Financial/Market Data APIs
- **Alpha Vantage** (`ALPHA_VANTAGE_API_KEY`)
  - Used for: Stock market data
  - Status: ✅ Configured

- **Polygon.io** (`POLYGON_API_KEY`)
  - Used for: Financial market data
  - Status: ✅ Configured

- **Coinbase** (`COINBASE_API_KEY`, `COINBASE_PRIVATE_KEY`)
  - Used for: Cryptocurrency data
  - Status: ⚙️ Keys configured

- **Etherscan** (`ETHERSCAN_API_KEY`)
  - Used for: Ethereum blockchain data
  - Status: ⚙️ Keys configured

- **CoinGecko** (`COINGECKO_API_KEY`)
  - Used for: Cryptocurrency market data
  - Status: ⚙️ Keys configured

### 4. Sports Data Providers (Implemented)
- **ESPN Hidden API**
  - Base URL: `https://site.api.espn.com/apis/site/v2/sports`
  - Free, no auth required
  - Rate limit: 100 req/min
  - Status: ✅ Implemented in `sports/data_providers.py`

- **TheSportsDB**
  - Community-driven sports database
  - Status: 🔄 Provider class exists

- **The Odds API**
  - Free tier available
  - Used for: Betting odds
  - Status: 🔄 Provider class exists

- **API-Sports**
  - Free tier with extensive coverage
  - Status: 🔄 Provider class exists

- **SportsDataIO**
  - Free trial available
  - Status: 🔄 Provider class exists

### 5. Communication Services
- **Telegram Bot** (`TELEGRAM_BOT_TOKEN`)
  - Used for: Bot notifications
  - Status: ⚙️ Token configured

- **Resend** (`RESEND_API_KEY`)
  - Used for: Email services
  - Status: ⚙️ Key configured

---

## Agent Tool Infrastructure

### Database Model: AgentTool
Located in `agents/models.py`, the platform has a comprehensive tool management system:

```python
class AgentTool(UnifiedBaseModel):
    # Tool types supported:
    - 'api': API Integration
    - 'computation': Computation Tool
    - 'data_processing': Data Processing
    - 'communication': Communication Tool
    - 'content_generation': Content Generation
    - 'analysis': Analysis Tool
    - 'monitoring': Monitoring Tool
    - 'integration': System Integration
```

### Tool Requirements in Agent Templates
Agents specify tools they need via:
- `required_tools`: Essential tools for agent function
- `optional_tools`: Tools that enhance performance

Example from migration scripts:
```python
"required_tools": ["web_search", "news_api", "arxiv_search", "reddit_api", "data_analyzer"]
```

---

## Missing Research Tools (Referenced but Not Implemented)

### 1. Web Search Tools
- **DuckDuckGo Search** 
  - Referenced in agent configs as `web_search`
  - Status: ❌ Not implemented
  - Integration needed: `duckduckgo-search` Python package

- **Google Search API**
  - Status: ❌ Not implemented
  - Would require: Google Custom Search API

### 2. Academic/Research Tools
- **ArXiv API**
  - Referenced as `arxiv_search`
  - Status: ❌ Not implemented
  - Integration needed: `arxiv` Python package

- **Wikipedia API**
  - Status: ❌ Not implemented
  - Integration needed: `wikipedia-api` Python package

### 3. Social Media/News Tools
- **Reddit API**
  - Referenced as `reddit_api`
  - Status: ❌ Not implemented
  - Integration needed: `praw` Python package

- **News API**
  - Referenced as `news_api`
  - Status: ❌ Not implemented
  - Would require: NewsAPI.org key

### 4. Data Analysis Tools
- **Data Analyzer**
  - Referenced as `data_analyzer`
  - Status: ⚙️ Partially implemented via pandas/numpy

---

## Integration Recommendations

### Priority 1: Essential Research Tools
1. **DuckDuckGo Search Integration**
   ```bash
   pip install duckduckgo-search
   ```
   Create `core/tools/web_search.py`:
   ```python
   from duckduckgo_search import DDGS
   
   class WebSearchTool:
       def search(self, query, max_results=10):
           with DDGS() as ddgs:
               return list(ddgs.text(query, max_results=max_results))
   ```

2. **ArXiv Integration**
   ```bash
   pip install arxiv
   ```
   Create `core/tools/arxiv_search.py`:
   ```python
   import arxiv
   
   class ArXivSearchTool:
       def search(self, query, max_results=10):
           search = arxiv.Search(query=query, max_results=max_results)
           return list(search.results())
   ```

3. **Reddit Integration**
   ```bash
   pip install praw
   ```
   Create `core/tools/reddit_search.py`:
   ```python
   import praw
   
   class RedditSearchTool:
       def __init__(self):
           self.reddit = praw.Reddit(
               client_id="YOUR_CLIENT_ID",
               client_secret="YOUR_SECRET",
               user_agent="unified-donkey-betz"
           )
   ```

### Priority 2: News and Media
1. **NewsAPI Integration**
   ```bash
   pip install newsapi-python
   ```
   Add to `.env`:
   ```
   NEWS_API_KEY=your-newsapi-key
   ```

2. **Wikipedia Integration**
   ```bash
   pip install wikipedia-api
   ```

### Priority 3: Advanced Analysis
1. **PDF Processing**
   ```bash
   pip install pypdf2 pdfplumber
   ```

2. **Web Scraping**
   ```bash
   pip install beautifulsoup4 selenium
   ```

---

## Implementation Strategy

### Step 1: Create Tool Registry
Create `core/tools/__init__.py`:
```python
from typing import Dict, Any, Optional

class ToolRegistry:
    _tools = {}
    
    @classmethod
    def register(cls, name: str, tool_class):
        cls._tools[name] = tool_class
    
    @classmethod
    def get_tool(cls, name: str):
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls):
        return list(cls._tools.keys())
```

### Step 2: Create Base Tool Class
Create `core/tools/base.py`:
```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    name: str
    description: str
    requires_auth: bool = False
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
    
    def validate_input(self, *args, **kwargs):
        pass
```

### Step 3: Register Tools in Database
```python
from agents.models import AgentTool

# Create tool entries
tools_to_create = [
    {
        'name': 'web_search',
        'display_name': 'Web Search (DuckDuckGo)',
        'tool_type': 'api',
        'description': 'Search the web using DuckDuckGo',
        'supported_operations': ['search', 'news', 'images'],
    },
    {
        'name': 'arxiv_search',
        'display_name': 'ArXiv Academic Search',
        'tool_type': 'api',
        'description': 'Search academic papers on ArXiv',
        'supported_operations': ['search', 'download_pdf', 'get_abstract'],
    },
    # ... more tools
]

for tool_data in tools_to_create:
    AgentTool.objects.get_or_create(name=tool_data['name'], defaults=tool_data)
```

### Step 4: Connect Tools to Agents
Update agent execution to use tools:
```python
class AgentExecutor:
    def __init__(self, agent_template):
        self.agent = agent_template
        self.tools = self._load_tools()
    
    def _load_tools(self):
        tools = {}
        for tool_name in self.agent.required_tools:
            tool_class = ToolRegistry.get_tool(tool_name)
            if tool_class:
                tools[tool_name] = tool_class()
        return tools
    
    def execute_with_tools(self, task):
        # Agent can now use self.tools
        pass
```

---

## Testing Integration

### Create Test Script
`test_agent_tools.py`:
```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from core.tools import ToolRegistry

def test_tools():
    # Test web search
    web_search = ToolRegistry.get_tool('web_search')
    results = web_search.execute("AI sports betting")
    print(f"Web search results: {len(results)}")
    
    # Test ArXiv
    arxiv_tool = ToolRegistry.get_tool('arxiv_search')
    papers = arxiv_tool.execute("reinforcement learning betting")
    print(f"ArXiv papers found: {len(papers)}")
    
    # List all available tools
    print(f"Available tools: {ToolRegistry.list_tools()}")

if __name__ == "__main__":
    test_tools()
```

---

## Security Considerations

1. **API Key Management**
   - Store all keys in environment variables
   - Never commit keys to repository
   - Use key rotation regularly
   - Implement rate limiting

2. **Tool Permissions**
   - Implement role-based tool access
   - Log all tool usage
   - Monitor for unusual patterns
   - Implement usage quotas

3. **Data Privacy**
   - Sanitize search queries
   - Don't store sensitive search results
   - Implement data retention policies
   - Comply with API terms of service

---

## Conclusion

The unified-donkey-betz platform has robust infrastructure for tool integration but lacks implementation of several key research tools that agents reference. The priority should be:

1. Implement DuckDuckGo web search (free, no API key needed)
2. Add ArXiv integration for academic research
3. Integrate Reddit API for social sentiment
4. Add NewsAPI for current events
5. Create a unified ToolRegistry for easy management

These integrations would significantly enhance agent capabilities for research, analysis, and real-time information gathering.