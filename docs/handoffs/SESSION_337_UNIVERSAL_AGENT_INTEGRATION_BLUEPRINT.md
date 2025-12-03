# Session 337: Universal Agent Integration Blueprint

**Date:** December 3, 2025
**Branch:** `feature/session-52-ai-assistant`
**Status:** ARCHITECTURAL BLUEPRINT - The Foundation for Everything

---

## The Vision

After 337 sessions, we have built something extraordinary:

- **199 total agents** (36 active)
- **74 spiders** gathering real-time intelligence
- **15 sci-fi features** (learning, dreams, conversations, evolution)
- **Cumulative intelligence** where research builds on research

But there's a gap: **Only 3 agents** are fully integrated with the cumulative intelligence pipeline. This blueprint shows how to connect ALL agents to the same living, learning system.

---

## Current State

### Fully Integrated Agents (The Gold Standard)
Located in `core/agents/business/`:

| Agent | Lines | Features |
|-------|-------|----------|
| CompetitorAnalysisAgent | ~41KB | Full integration |
| CustomerResearchAgent | ~62KB | Full integration |
| BrandStrategyAgent | ~42KB | Full integration (Session 336-337) |

**What makes them special:**
- `unified_search` service for cumulative intelligence
- Auto spider refresh at execute() start
- Auto prior research context injection
- `refresh_spider_data` tool
- `get_prior_research` tool
- `get_project_research` tool
- `spider_query` tool
- `web_search` tool
- `raw_data` in AgentResult for frontend display
- Save to `BusinessResearchResult` model
- Frontend dropdown with "Add to Project" button

### Clean Architecture Agents (Not Integrated)
Located in `core/agents/strategy/` and `core/agents/`:

| Agent | Location | Status |
|-------|----------|--------|
| ContentStrategyAgent | strategy/ | Not connected to PA |
| SEOOptimizerAgent | strategy/ | Not connected to PA |
| ImageAgent | core/agents/ | Different purpose (generation) |
| VideoAgent | core/agents/ | Different purpose (generation) |
| AudioAgent | core/agents/ | Different purpose (generation) |
| ResearchAgent | core/agents/ | Could be integrated |
| TrendAnalysisAgent | core/agents/ | Could be integrated |

### Legacy Agents (In `agents/` folder)
22 legacy agents that could potentially be migrated.

---

## The Problem

Each fully integrated agent is **40-60KB of code** with massive duplication:
- Same unified_search property
- Same tool definitions (refresh_spider_data, get_prior_research, etc.)
- Same execute() flow (spider refresh → prior context → tools → synthesis → save)
- Same AgentResult structure
- Same error handling

To add a new agent, we currently copy 1000+ lines and modify ~200.

---

## The Solution: BaseBusinessResearchAgent

Create a parent class that handles ALL the common functionality, so child agents only define what's unique.

### Architecture

```
BaseBusinessResearchAgent (NEW - ~800 lines)
    ├── unified_search property
    ├── Standard tools (refresh_spider_data, get_prior_research, spider_query, web_search)
    ├── Auto spider refresh
    ├── Prior research context injection
    ├── Tool execution framework
    ├── raw_data extraction
    ├── BusinessResearchResult saving
    └── Standard AgentResult structure

    ↓ Child agents only define:

ContentStrategyAgent (~200 lines)
    ├── research_type = "content_strategy"
    ├── system_prompt (agent-specific)
    ├── synthesis_prompt (what to synthesize)
    └── Optional: custom tools

MarketingStrategyAgent (~200 lines)
    ├── research_type = "marketing_strategy"
    ├── system_prompt
    ├── synthesis_prompt
    └── Optional: custom tools

SEOResearchAgent (~200 lines)
    ├── research_type = "seo_research"
    ├── system_prompt
    ├── synthesis_prompt
    └── Optional: custom tools
```

### Code Reduction

| Approach | Lines per Agent | Total for 10 Agents |
|----------|----------------|---------------------|
| Current (copy everything) | ~1200 lines | 12,000 lines |
| With BaseBusinessResearchAgent | ~200 lines | 2,800 lines (base + 10 agents) |

**77% code reduction** + easier maintenance + consistent behavior.

---

## BaseBusinessResearchAgent Design

### File: `core/agents/business/base_business_research_agent.py`

```python
"""
BaseBusinessResearchAgent - Universal Integration Pattern
=========================================================

Session 337: The foundation for ALL business research agents.

Every agent that:
- Gathers intelligence from spiders
- Searches prior research
- Synthesizes with GPT
- Saves to BusinessResearchResult
- Displays in frontend with "Add to Project"

...should inherit from this class.

Child agents only need to define:
- research_type: str (e.g., "content_strategy")
- name: str (e.g., "ContentStrategyAgent")
- system_prompt: str (agent-specific instructions)
- get_synthesis_prompt(): Method returning synthesis instructions
- Optional: additional_tools: list (agent-specific tools)
- Optional: handle_custom_tool(): For agent-specific tool handling
"""

import logging
import json
from typing import Dict, Any, List, Optional
from abc import abstractmethod

from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)


class AgentResult:
    """Standard result structure for all business research agents."""

    def __init__(
        self,
        success: bool,
        message: str = "",
        data: Dict[str, Any] = None,
        error: str = None,
        agent_name: str = "",
        execution_time_ms: int = 0
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.error = error
        self.agent_name = agent_name
        self.execution_time_ms = execution_time_ms


class BaseBusinessResearchAgent:
    """
    Base class for all business research agents.

    Provides:
    - unified_search service integration
    - Auto spider refresh
    - Prior research context injection
    - Standard tools (refresh_spider_data, get_prior_research, spider_query, web_search)
    - Tool execution framework
    - raw_data extraction for frontend
    - BusinessResearchResult saving

    Child classes must define:
    - research_type: str
    - name: str
    - system_prompt: str
    - get_synthesis_prompt(task, context): str

    Child classes may override:
    - additional_tools: list
    - handle_custom_tool(tool_name, arguments): dict
    - get_spider_categories(): list
    """

    # Must be set by child class
    research_type: str = None  # e.g., "content_strategy"
    name: str = None  # e.g., "ContentStrategyAgent"
    system_prompt: str = None  # Agent-specific system prompt

    # Optional overrides
    additional_tools: List[Dict] = []  # Agent-specific tools

    # Standard tools available to all business research agents
    STANDARD_TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "get_project_research",
                "description": "Retrieve existing research from the current project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "research_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of research to retrieve"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "refresh_spider_data",
                "description": "Trigger spider network to fetch fresh, real-time data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Spider categories to refresh"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_prior_research",
                "description": "Retrieve relevant past research from previous analyses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic to search for"
                        },
                        "research_type": {
                            "type": "string",
                            "enum": ["competitor", "customer", "brand_strategy", "content_strategy", "marketing", "seo", "all"]
                        },
                        "limit": {
                            "type": "integer",
                            "default": 5
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "Query the spider network for trending data and discussions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    def __init__(self, user=None, project_id=None):
        self.user = user
        self.project_id = project_id
        self._unified_search = None
        self._current_task = None
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Validate child class configuration
        if not self.research_type:
            raise ValueError(f"{self.__class__.__name__} must define research_type")
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define name")
        if not self.system_prompt:
            raise ValueError(f"{self.__class__.__name__} must define system_prompt")

    @property
    def unified_search(self):
        """Lazy-load Unified Intelligence Search Service."""
        if self._unified_search is None:
            from core.services.unified_intelligence_search import get_unified_intelligence_search
            self._unified_search = get_unified_intelligence_search()
        return self._unified_search

    @property
    def tools(self) -> List[Dict]:
        """Combine standard tools with agent-specific tools."""
        return self.STANDARD_TOOLS + self.additional_tools + [self._get_synthesis_tool()]

    @abstractmethod
    def get_synthesis_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """
        Return the synthesis prompt for this agent type.

        Child classes MUST implement this to define how their research
        should be synthesized.
        """
        pass

    def _get_synthesis_tool(self) -> Dict:
        """Get the synthesis tool definition for this agent."""
        return {
            "type": "function",
            "function": {
                "name": f"synthesize_{self.research_type}",
                "description": f"Synthesize all gathered data into a comprehensive {self.research_type.replace('_', ' ')} report.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis": {
                            "type": "string",
                            "description": "The comprehensive analysis/strategy"
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "key_insights": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["analysis"]
                }
            }
        }

    def get_spider_categories(self) -> List[str]:
        """
        Return spider categories relevant to this agent.
        Override in child class for specific categories.
        """
        return ["tech", "news", "content", "social"]

    def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute the agent's research task.

        Flow:
        1. Auto-refresh spiders for fresh data
        2. Auto-inject prior research context
        3. Call GPT with tools
        4. Execute tool calls
        5. Synthesize results
        6. Save to BusinessResearchResult
        7. Return AgentResult with raw_data
        """
        import time
        start_time = time.time()
        context = context or {}
        self._current_task = task

        try:
            # Step 1: Auto spider refresh
            self._auto_refresh_spiders(task)

            # Step 2: Get prior research context
            prior_context = self._get_prior_research_context(task)

            # Step 3: Get project context if available
            project_context = self._get_project_context()

            # Step 4: Build enhanced prompt
            enhanced_prompt = self._build_prompt(task, prior_context, project_context, context)

            # Step 5: Execute GPT loop with tools
            all_data, synthesis = self._execute_gpt_loop(enhanced_prompt)

            # Step 6: Extract source articles for frontend
            source_articles, sources_used = self._extract_source_articles(all_data)

            # Step 7: Save to BusinessResearchResult
            saved_result = self._save_research_result(task, synthesis, all_data, project_context)

            # Step 8: Build and return AgentResult
            execution_time = int((time.time() - start_time) * 1000)

            return AgentResult(
                success=True,
                message=f"{self.name} completed with {len(all_data)} data sources",
                data={
                    'analysis': synthesis.get('analysis', str(synthesis)),
                    'recommendations': synthesis.get('recommendations', []),
                    'key_insights': synthesis.get('key_insights', []),
                    'raw_data': all_data,
                    'sources_used': list(sources_used),
                    'data_points_analyzed': len(source_articles),
                    'project_name': project_context.get('project_name', ''),
                    'query': task,
                    'saved_id': str(saved_result.id) if saved_result else None,
                    'research_type': self.research_type
                },
                agent_name=self.name,
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"{self.name} error: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _auto_refresh_spiders(self, task: str):
        """Trigger spider refresh for fresh data."""
        try:
            result = self.unified_search.refresh_spiders_for_query(
                query=task,
                categories=self.get_spider_categories()
            )
            logger.info(f"{self.name}: Auto-refreshed spiders: {result.get('categories', [])}")
        except Exception as e:
            logger.warning(f"{self.name}: Spider refresh failed (continuing): {e}")

    def _get_prior_research_context(self, task: str) -> str:
        """Get prior research context for cumulative intelligence."""
        try:
            return self.unified_search.get_research_context(
                query=task,
                max_spider_items=3,
                max_research_items=2
            )
        except Exception as e:
            logger.warning(f"{self.name}: Prior research lookup failed (continuing): {e}")
            return ""

    def _get_project_context(self) -> Dict[str, Any]:
        """Get project context if project_id is set."""
        if not self.project_id:
            return {}

        try:
            from content.models import Project
            project = Project.objects.get(id=self.project_id)
            return {
                'project_id': self.project_id,
                'project_name': project.name,
                'project_description': project.description or ''
            }
        except Exception as e:
            logger.warning(f"{self.name}: Project lookup failed: {e}")
            return {}

    def _build_prompt(self, task: str, prior_context: str, project_context: Dict, context: Dict) -> str:
        """Build the enhanced prompt with all context."""
        prompt_parts = [task]

        if project_context:
            prompt_parts.append(f"\n\nProject Context:\n- Name: {project_context.get('project_name', 'Unknown')}")
            if project_context.get('project_description'):
                prompt_parts.append(f"- Description: {project_context['project_description']}")

        if prior_context:
            prompt_parts.append(f"\n\nPrior Research Context:\n{prior_context}")

        if context:
            prompt_parts.append(f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}")

        return "\n".join(prompt_parts)

    def _execute_gpt_loop(self, prompt: str) -> tuple:
        """Execute GPT with tools until synthesis is complete."""
        all_data = []
        synthesis = {}
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        max_iterations = 10
        for iteration in range(max_iterations):
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            choice = response.choices[0]

            if choice.finish_reason == "stop":
                break

            if choice.message.tool_calls:
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Execute tool
                    result = self._execute_tool(tool_name, arguments)

                    # Track data
                    all_data.append({
                        'source': tool_name,
                        'data': result
                    })

                    # Check for synthesis
                    if tool_name == f"synthesize_{self.research_type}":
                        synthesis = arguments

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
            else:
                break

        return all_data, synthesis

    def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute a tool call and return results."""

        if tool_name == "get_project_research":
            return self._handle_get_project_research(arguments)

        elif tool_name == "refresh_spider_data":
            return self._handle_refresh_spider_data(arguments)

        elif tool_name == "get_prior_research":
            return self._handle_get_prior_research(arguments)

        elif tool_name == "spider_query":
            return self._handle_spider_query(arguments)

        elif tool_name == "web_search":
            return self._handle_web_search(arguments)

        elif tool_name == f"synthesize_{self.research_type}":
            return {"success": True, "message": "Synthesis recorded"}

        else:
            # Check for custom tool handler in child class
            return self.handle_custom_tool(tool_name, arguments)

    def handle_custom_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Override in child class to handle agent-specific tools.

        Default implementation returns an error.
        """
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def _handle_get_project_research(self, arguments: Dict) -> Dict:
        """Get existing research from project."""
        if not self.project_id:
            return {"success": True, "research": [], "message": "No project context"}

        try:
            from core.models_unified_system import BusinessResearchResult

            research_types = arguments.get('research_types', [])
            queryset = BusinessResearchResult.objects.filter(project_id=self.project_id)

            if research_types:
                queryset = queryset.filter(research_type__in=research_types)

            research = []
            for r in queryset.order_by('-created_at')[:10]:
                research.append({
                    'type': r.research_type,
                    'query': r.query,
                    'summary': r.content[:500] if r.content else '',
                    'created_at': r.created_at.isoformat()
                })

            return {"success": True, "research": research}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_refresh_spider_data(self, arguments: Dict) -> Dict:
        """Trigger spider refresh."""
        categories = arguments.get('categories', self.get_spider_categories())
        result = self.unified_search.refresh_spiders_for_query(
            query=self._current_task or '',
            categories=categories
        )
        return {"success": True, "data": result}

    def _handle_get_prior_research(self, arguments: Dict) -> Dict:
        """Get prior research for a topic."""
        topic = arguments.get('topic', '')
        research_type = arguments.get('research_type', 'all')
        limit = arguments.get('limit', 5)

        results = self.unified_search.unified_search(
            query=topic,
            include_spiders=False,
            include_research=True,
            research_limit=limit
        )

        return {"success": True, "data": results}

    def _handle_spider_query(self, arguments: Dict) -> Dict:
        """Query spider network."""
        query = arguments.get('query', '')
        categories = arguments.get('categories', self.get_spider_categories())
        limit = arguments.get('limit', 20)

        try:
            from core.services.spider_intelligence import SpiderIntelligenceService
            service = SpiderIntelligenceService()
            results = service.search_intelligence(
                query=query,
                categories=categories,
                limit=limit
            )
            return {"success": True, "discussions": results.get('results', [])}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_web_search(self, arguments: Dict) -> Dict:
        """Perform web search."""
        query = arguments.get('query', '')
        num_results = arguments.get('num_results', 10)

        try:
            from agents.research_agent import ResearchAgent
            agent = ResearchAgent()
            results = agent.web_search(query, num_results=num_results)
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_source_articles(self, all_data: List[Dict]) -> tuple:
        """Extract source articles from collected data for frontend display."""
        source_articles = []
        sources_used = set()

        synthesis_tool = f"synthesize_{self.research_type}"
        excluded_sources = {synthesis_tool, 'get_project_research', 'get_prior_research'}

        for data_item in all_data:
            source = data_item.get('source', '')
            if source in excluded_sources:
                continue

            sources_used.add(source)
            item_data = data_item.get('data', {})

            if isinstance(item_data, dict):
                # Handle spider_query results
                if 'discussions' in item_data:
                    for d in item_data.get('discussions', []):
                        source_articles.append({
                            'title': d.get('title', ''),
                            'description': d.get('description', d.get('content', ''))[:300],
                            'url': d.get('url', ''),
                            'source': d.get('source', source)
                        })

                # Handle web_search results
                elif 'results' in item_data:
                    for r in item_data.get('results', []):
                        source_articles.append({
                            'title': r.get('title', ''),
                            'description': r.get('snippet', r.get('description', ''))[:300],
                            'url': r.get('link', r.get('url', '')),
                            'source': 'web_search'
                        })

        return source_articles, sources_used

    def _save_research_result(
        self,
        task: str,
        synthesis: Dict,
        all_data: List[Dict],
        project_context: Dict
    ):
        """Save research to BusinessResearchResult."""
        try:
            from core.models_unified_system import BusinessResearchResult

            content = synthesis.get('analysis', str(synthesis))

            result = BusinessResearchResult.objects.create(
                research_type=self.research_type,
                query=task,
                content=content,
                raw_data=all_data,
                project_id=project_context.get('project_id'),
                user=self.user
            )

            logger.info(f"{self.name}: Saved research result {result.id}")
            return result

        except Exception as e:
            logger.error(f"{self.name}: Failed to save research: {e}")
            return None
```

---

## Child Agent Example: ContentStrategyAgent

### File: `core/agents/business/content_strategy_agent.py`

```python
"""
ContentStrategyAgent - Business Research Agent
===============================================

Session 337+: Inherits from BaseBusinessResearchAgent.

Analyzes existing research + spider data to recommend
what content the user should create next.
"""

from typing import Dict, Any, List
from core.agents.business.base_business_research_agent import BaseBusinessResearchAgent


class ContentStrategyAgent(BaseBusinessResearchAgent):
    """
    Agent specialized in content strategy recommendations.

    Uses cumulative intelligence from:
    - Prior competitor analysis
    - Prior customer research
    - Prior brand strategy
    - Spider trending data
    - Web search for content trends
    """

    research_type = "content_strategy"
    name = "ContentStrategyAgent"

    system_prompt = """You are ContentStrategyAgent, a strategic content advisor.

Your job is to analyze the user's existing research (competitor analysis, customer
personas, brand strategy) and recommend what content they should create.

You have access to:
1. Project research - existing analyses for this project
2. Spider network - real-time trending topics and discussions
3. Web search - current content trends and best practices
4. Prior research - relevant past analyses

Workflow:
1. First, get any existing project research to understand context
2. Query spider network for trending content topics in their niche
3. Search web for content strategy best practices
4. Synthesize into actionable content recommendations

Your synthesis should include:
- Content pillars (3-5 main themes)
- Content formats (blog, video, social, podcast, etc.)
- Content calendar recommendations
- Topic ideas with titles
- SEO/keyword opportunities
- Distribution channel recommendations

Always ground recommendations in the data you gather."""

    def get_synthesis_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Return synthesis prompt for content strategy."""
        return f"""Based on all gathered data, synthesize a comprehensive content strategy for: {task}

Include:
1. Content Pillars - Main themes based on competitor gaps and customer needs
2. Format Recommendations - What content formats work best for this audience
3. Topic Ideas - Specific content pieces with working titles
4. Publishing Cadence - How often to publish each format
5. Distribution Strategy - Where to share content
6. Quick Wins - Content that can be created immediately"""

    def get_spider_categories(self) -> List[str]:
        """Spider categories for content strategy."""
        return ["content", "tech", "social", "news", "creative"]

    # No additional_tools needed - standard tools are sufficient
    # No handle_custom_tool needed - no custom tools
```

**That's it!** ~80 lines instead of 1000+.

---

## Migration Roadmap

### Phase 1: Create Base Class (Session 338)
1. Create `base_business_research_agent.py`
2. Test with a new agent (ContentStrategyAgent)
3. Verify full flow works

### Phase 2: Migrate Existing Agents (Session 339-340)
1. Refactor CompetitorAnalysisAgent to use base class
2. Refactor CustomerResearchAgent to use base class
3. Refactor BrandStrategyAgent to use base class
4. Verify nothing breaks

### Phase 3: Add New Agents (Session 341+)
| Agent | research_type | Purpose |
|-------|--------------|---------|
| ContentStrategyAgent | content_strategy | What content to create |
| MarketingStrategyAgent | marketing_strategy | How to market content |
| SEOResearchAgent | seo_research | Keywords and optimization |
| SocialMediaStrategyAgent | social_strategy | Platform-specific strategy |
| EmailMarketingAgent | email_strategy | Email campaign planning |
| PricingStrategyAgent | pricing_strategy | Product/service pricing |
| PartnershipAgent | partnership_research | Partnership opportunities |

### Phase 4: Frontend Unification (Session 342)
1. Make `formatAnalysisReport` data-driven
2. Config object for icons/labels per research_type
3. Universal "Add to Project" handling
4. Research type filtering in project view

### Phase 5: Legacy Agent Migration (Session 343+)
Migrate relevant agents from `agents/` folder to new pattern.

---

## Frontend Configuration

### Add to `ai_image_studio.html`:

```javascript
// Research type configuration - add new types here
const RESEARCH_TYPES = {
    'competitor': {
        icon: '🎯',
        label: 'Competitor Analysis',
        color: 'blue'
    },
    'customer': {
        icon: '👥',
        label: 'Customer Research',
        color: 'green'
    },
    'brand_strategy': {
        icon: '🎨',
        label: 'Brand Strategy',
        color: 'purple'
    },
    'content_strategy': {
        icon: '📝',
        label: 'Content Strategy',
        color: 'orange'
    },
    'marketing_strategy': {
        icon: '📢',
        label: 'Marketing Strategy',
        color: 'red'
    },
    'seo_research': {
        icon: '🔍',
        label: 'SEO Research',
        color: 'teal'
    }
};

// Use in dropdown generation
function getResearchTypeConfig(type) {
    return RESEARCH_TYPES[type] || {
        icon: '📊',
        label: type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        color: 'gray'
    };
}
```

---

## Tool Definitions Addition

### Add to `core/assistant/tool_definitions.py`:

```python
{
    "type": "function",
    "function": {
        "name": "content_strategy_agent",
        "description": "Analyze existing research and trends to recommend content strategy. Use when user asks about content planning, content calendars, what content to create, or content recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The content strategy request"
                }
            },
            "required": ["task"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "marketing_strategy_agent",
        "description": "Create marketing strategy based on brand and content. Use when user asks about marketing plans, promotion strategies, or how to market their content/products.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The marketing strategy request"
                }
            },
            "required": ["task"]
        }
    }
}
```

---

## The Living System

With this architecture, every agent becomes part of the living, learning ecosystem:

```
User Request
    ↓
Personal Assistant (routes to agent)
    ↓
BaseBusinessResearchAgent
    ├── Auto Spider Refresh → Fresh data from 74 spiders
    ├── Prior Research → Cumulative intelligence from all past analyses
    ├── Project Context → Builds on existing project research
    ├── GPT + Tools → Intelligent data gathering
    ├── Synthesis → Comprehensive analysis
    └── Save to DB → Becomes prior research for future agents
    ↓
Frontend Display
    ├── Formatted Report
    ├── Source Data Dropdown
    └── "Add to Project" Button
    ↓
Project Intelligence Hub
    ├── All research visible
    ├── Knowledge connections
    └── Agent conversations about project
    ↓
Agent Learning System
    ├── Learns from user feedback
    ├── Shares knowledge across agents
    └── Dreams about improvements
```

**Every analysis makes the system smarter. Every agent contributes to collective intelligence.**

---

## Files to Create/Modify

### New Files
| File | Purpose |
|------|---------|
| `core/agents/business/base_business_research_agent.py` | Base class (~800 lines) |
| `core/agents/business/content_strategy_agent.py` | Content strategy (~80 lines) |
| `core/agents/business/marketing_strategy_agent.py` | Marketing strategy (~80 lines) |
| `core/agents/business/seo_research_agent.py` | SEO research (~80 lines) |

### Modify Files
| File | Changes |
|------|---------|
| `core/agents/business/__init__.py` | Export new agents |
| `core/assistant/tool_definitions.py` | Add tool definitions |
| `core/personal_ai_assistant_enhanced.py` | Add operation_keywords, handlers |
| `ai_core/templates/ai_image_studio.html` | Add RESEARCH_TYPES config |

---

## Success Metrics

After full implementation:

| Metric | Before | After |
|--------|--------|-------|
| Integrated agents | 3 | 10+ |
| Lines per new agent | 1000+ | ~100 |
| Time to add agent | Hours | Minutes |
| Code duplication | High | Minimal |
| Consistency | Variable | Guaranteed |

---

## Conclusion

This blueprint transforms the platform from "3 special agents + many disconnected agents" into a **unified ecosystem** where:

1. **Every agent follows the same pattern**
2. **Every analysis builds on previous work**
3. **Every insight is preserved and searchable**
4. **Adding new agents is trivial**
5. **The system gets smarter with every use**

This is what 337 sessions have been building towards - a truly intelligent, self-improving AI platform.

---

**Status:** BLUEPRINT COMPLETE. Ready for implementation in Session 338+.

**Next Session:** Create `BaseBusinessResearchAgent` and `ContentStrategyAgent` to prove the pattern.
