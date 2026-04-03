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
- Optional: get_spider_categories(): Override default categories
"""

import logging
import json
import time
import random
from typing import Dict, Any, List
from abc import abstractmethod

from openai import OpenAI
from django.conf import settings

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class BaseBusinessResearchAgent(BaseAgent):
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
                "description": "Retrieve existing research from the current project including competitor analysis, customer research, brand strategy, and other analyses. ALWAYS call this first to understand existing project context.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "research_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of research to retrieve (competitor, customer, brand_strategy, content_strategy, marketing_strategy, etc.)"
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
                "description": "Trigger spider network to fetch fresh, real-time data from 77 spiders across 20 categories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Spider categories to refresh (tech, news, content, social, creative, etc.)"
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
                "description": "Retrieve relevant past research from previous analyses across all projects.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic to search for in prior research"
                        },
                        "research_type": {
                            "type": "string",
                            "enum": ["competitor", "customer", "brand_strategy", "content_strategy", "marketing_strategy", "seo", "all"],
                            "description": "Type of research to retrieve"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 5,
                            "description": "Maximum number of results"
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
                "description": "Query the spider network for trending data, discussions, and real-time intelligence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for spider data"
                        },
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Spider categories to search"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "description": "Maximum results to return"
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
                "description": "Search the web for current information, best practices, and industry data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "default": 10,
                            "description": "Number of results to return"
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
        # W004 fix: Use _client backing variable since BaseAgent.client is a read-only property
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

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

    def _call_openai_with_retry(
        self,
        messages: List[Dict],
        model: str = "gpt-4o-mini",
        tools: List = None,
        tool_choice: str = "auto",
        max_completion_tokens: int = 6000,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0
    ):
        """
        Session 857: Call OpenAI with retry logic for rate limits and transient errors.

        Handles:
        - Rate limit errors (429)
        - Server errors (5xx)
        - Connection errors

        Uses exponential backoff with jitter.
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                kwargs = {
                    'model': model,
                    'messages': messages,
                    'max_completion_tokens': max_completion_tokens,
                }
                if tools:
                    kwargs['tools'] = tools
                    kwargs['tool_choice'] = tool_choice

                return self.client.chat.completions.create(**kwargs)

            except Exception as e:
                last_exception = e
                error_str = str(e).lower()

                # Check if retryable
                is_rate_limit = '429' in str(e) or 'rate limit' in error_str or 'quota' in error_str
                is_server_error = any(code in str(e) for code in ['500', '502', '503', '504'])
                is_connection_error = 'connection' in error_str or 'timeout' in error_str

                is_retryable = is_rate_limit or is_server_error or is_connection_error

                if not is_retryable or attempt >= max_retries - 1:
                    logger.error(
                        f"[Session 857] {self.name} LLM call failed after {attempt + 1} attempts: {e}"
                    )
                    raise

                # Calculate exponential backoff with jitter
                delay = min(base_delay * (2 ** attempt), max_delay)
                delay = delay * (0.5 + random.random())  # Add jitter

                error_type = 'rate_limit' if is_rate_limit else 'server_error' if is_server_error else 'connection'
                logger.warning(
                    f"[Session 857] {self.name} LLM call failed ({error_type}), "
                    f"retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries}): {e}"
                )

                time.sleep(delay)

        raise last_exception

    def _build_intelligent_prompt(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> str:
        """
        Build intelligent prompt with platform context.

        Session 529: Add platform awareness to business research agents.
        """
        from django.utils import timezone

        parts = []

        # Add temporal awareness
        current_date = timezone.now()
        parts.append(f"## TEMPORAL AWARENESS\n- Current Date: {current_date.strftime('%B %d, %Y')}")

        # Add mood context if available
        if scifi_context and scifi_context.get('mood'):
            mood = scifi_context['mood']
            parts.append(f"## CREATIVE MOOD\nCurrent Mood: **{mood.get('name', 'Calm')}**")

        # Add research context
        parts.append(f"""## RESEARCH CONTEXT
You are {self.name}, a specialized business research agent.
Research Type: {self.research_type}""")

        return "\n\n".join(parts) if parts else ""

    @property
    def tools(self) -> List[Dict]:
        """Combine standard tools with agent-specific tools and synthesis tool."""
        return self.STANDARD_TOOLS + self.additional_tools + [self._get_synthesis_tool()]

    @abstractmethod
    def get_synthesis_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """
        Return the synthesis prompt for this agent type.

        Child classes MUST implement this to define how their research
        should be synthesized.
        """

    def _get_synthesis_tool(self) -> Dict:
        """Get the synthesis tool definition for this agent."""
        return {
            "type": "function",
            "function": {
                "name": f"synthesize_{self.research_type}",
                "description": f"Synthesize all gathered data into a comprehensive {self.research_type.replace('_', ' ')} report. Call this AFTER gathering data from project research, spiders, and web search.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis": {
                            "type": "string",
                            "description": "The comprehensive analysis/strategy in markdown format with headers and sections"
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key actionable recommendations"
                        },
                        "key_insights": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Important insights discovered"
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

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
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
        start_time = time.time()
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}
        self._current_task = task

        # Session 750: Time Travel integration
        with self.time_travel_session("business_research", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action=f"Starting {self.research_type} research",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip research", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

            # Session 529: Build intelligent prompt with full context
            self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            # Session 349: Extract project_id from context if not set in constructor
            # This ensures research results are linked to the project
            if not self.project_id and context.get('project_id'):
                self.project_id = context.get('project_id')
                logger.info(f"{self.name}: Set project_id from context: {self.project_id}")

            try:
                logger.info(f"{self.name}: Starting execution for task: {task[:100]}")

                # Step 1: Auto spider refresh
                self._auto_refresh_spiders(task)

                # Step 2: Get prior research context
                prior_context = self._get_prior_research_context(task)

                # Step 3: Get project context if available
                project_context = self._get_project_context()

                # Step 4: Build enhanced prompt with intelligent context
                enhanced_prompt = self._intelligent_context + "\n\n" + self._build_prompt(task, prior_context, project_context, context)

                # Step 5: Execute GPT loop with tools
                all_data, synthesis = self._execute_gpt_loop(enhanced_prompt, project_context)

                # Step 6: Extract source articles for frontend
                source_articles, sources_used = self._extract_source_articles(all_data)

                # Session 1023: Minimum Evidence Gate — block when data is insufficient
                # Prevents synthesis from thin air (e.g., 0-1 source articles)
                MIN_SOURCE_ARTICLES = 3
                if len(source_articles) < MIN_SOURCE_ARTICLES:
                    execution_time = int((time.time() - start_time) * 1000)
                    gate_reason = (
                        f"Only {len(source_articles)} usable source articles collected "
                        f"(minimum: {MIN_SOURCE_ARTICLES}). "
                        f"Tools used: {list(sources_used) if sources_used else 'none'}"
                    )
                    logger.warning(f"[Evidence Gate] {self.name}: {gate_reason}")
                    return AgentResult(
                        success=True,  # Not an error — just insufficient data
                        message=(
                            f"Insufficient data to produce reliable {self.research_type} analysis. "
                            f"{gate_reason}\n\n"
                            f"Recommendations:\n"
                            f"- Expand spider network coverage for this domain\n"
                            f"- Try broader or more specific search queries\n"
                            f"- Run targeted primary research first"
                        ),
                        data={
                            'type': 'insufficient_evidence',
                            'research_type': self.research_type,
                            'source_articles_found': len(source_articles),
                            'sources_used': list(sources_used),
                            'raw_data': all_data,
                            'gate_reason': gate_reason,
                            'recommended_actions': [
                                'Expand spider network coverage for this domain',
                                'Try broader or more specific search queries',
                                'Run targeted primary research first',
                            ],
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                    )

                # Step 7: Save to BusinessResearchResult
                saved_result = self._save_research_result(task, synthesis, all_data, project_context)

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"{self.name}: {task[:80]}",
                    content=synthesis.get('analysis', str(synthesis)),
                    deliverable_type='research',
                    category='Business Research',
                    tags=[self.research_type, 'business'],
                    metadata={'task': task[:200], 'research_type': self.research_type, 'data_sources': len(all_data)},
                )

                # Step 8: Build and return AgentResult
                execution_time = int((time.time() - start_time) * 1000)

                logger.info(f"{self.name}: Completed in {execution_time}ms with {len(all_data)} data sources")

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
            # Session 340: Try PartnershipProject first (primary project model)
            from core.models_partnership import PartnershipProject
            project = PartnershipProject.objects.get(id=self.project_id)
            return {
                'project_id': self.project_id,
                'project_name': project.project_name,
                'project_description': project.description or ''
            }
        except Exception as e:
            logger.warning(f"{self.name}: PartnershipProject lookup failed, trying legacy Project: {e}")
            # Fallback to legacy Project model
            try:
                from content.models import Project
                project = Project.objects.get(id=self.project_id)
                return {
                    'project_id': self.project_id,
                    'project_name': project.name,
                    'project_description': project.description or ''
                }
            except Exception as e2:
                logger.warning(f"{self.name}: Legacy Project lookup also failed: {e2}")
                return {}

    def _build_prompt(self, task: str, prior_context: str, project_context: Dict, context: Dict) -> str:
        """Build the enhanced prompt with all context."""
        prompt_parts = [task]

        if project_context:
            prompt_parts.append(f"\n\n## Project Context\n- **Name:** {project_context.get('project_name', 'Unknown')}")
            if project_context.get('project_description'):
                prompt_parts.append(f"- **Description:** {project_context['project_description']}")

        if prior_context:
            prompt_parts.append(f"\n\n## Prior Research Context\n{prior_context}")

        if context:
            try:
                prompt_parts.append(f"\n\n## Additional Context\n{json.dumps(context, indent=2, default=str)}")
            except (TypeError, ValueError):
                prompt_parts.append(f"\n\n## Additional Context\n{str(context)}")

        # Add synthesis instructions
        prompt_parts.append(f"\n\n## Instructions\n{self.get_synthesis_prompt(task, context)}")

        return "\n".join(prompt_parts)

    def _execute_gpt_loop(self, prompt: str, project_context: Dict) -> tuple:
        """Execute GPT with tools until synthesis is complete."""
        all_data = []
        synthesis = {}
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        synthesis_tool_name = f"synthesize_{self.research_type}"
        max_iterations = 10

        for iteration in range(max_iterations):
            logger.debug(f"{self.name}: GPT iteration {iteration + 1}")

            # Session 857: Use retry wrapper for rate limit handling
            # Session 338: Use gpt-4o-mini for cost efficiency
            response = self._call_openai_with_retry(
                messages=messages,
                model="gpt-5.2",
                tools=self.get_tools_with_delegation(),
                tool_choice="auto",
                max_completion_tokens=6000,  # High for reasoning + output
            )

            choice = response.choices[0]

            if choice.finish_reason == "stop":
                logger.debug(f"{self.name}: GPT finished with 'stop'")
                break

            if choice.message.tool_calls:
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}

                    logger.info(f"{self.name}: Calling tool {tool_name}")

                    # Execute tool
                    result = self._execute_tool(tool_name, arguments, project_context)

                    # Track data
                    all_data.append({
                        'source': tool_name,
                        'data': result
                    })

                    # Check for synthesis
                    if tool_name == synthesis_tool_name:
                        synthesis = arguments
                        logger.info(f"{self.name}: Synthesis captured")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, default=str) if isinstance(result, dict) else str(result)
                    })
            else:
                logger.debug(f"{self.name}: No tool calls, breaking")
                break

        # If no synthesis was captured, try to extract from last message
        if not synthesis and messages:
            last_msg = messages[-1]
            if hasattr(last_msg, 'content') and last_msg.content:
                synthesis = {'analysis': last_msg.content}

        return all_data, synthesis

    def _execute_tool(self, tool_name: str, arguments: Dict, project_context: Dict) -> Dict:
        """Execute a tool call and return results."""

        if tool_name == "get_project_research":
            return self._handle_get_project_research(arguments, project_context)

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
        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _handle_get_project_research(self, arguments: Dict, project_context: Dict) -> Dict:
        """Get existing research from project."""
        project_id = project_context.get('project_id') or self.project_id

        if not project_id:
            return {"success": True, "research": [], "message": "No project context available"}

        try:
            from core.models_unified_system import BusinessResearchResult

            research_types = arguments.get('research_types', [])
            queryset = BusinessResearchResult.objects.filter(project_id=project_id)

            if research_types:
                queryset = queryset.filter(research_type__in=research_types)

            research = []
            for r in queryset.order_by('-created_at')[:10]:
                research.append({
                    'type': r.research_type,
                    'query': r.query,
                    'summary': r.content[:1000] if r.content else '',
                    'created_at': r.created_at.isoformat() if r.created_at else None
                })

            logger.info(f"{self.name}: Found {len(research)} project research items")
            return {"success": True, "research": research, "count": len(research)}

        except Exception as e:
            logger.error(f"{self.name}: get_project_research error: {e}")
            return {"success": False, "error": str(e)}

    def _handle_refresh_spider_data(self, arguments: Dict) -> Dict:
        """Trigger spider refresh."""
        categories = arguments.get('categories', self.get_spider_categories())
        try:
            result = self.unified_search.refresh_spiders_for_query(
                query=self._current_task or '',
                categories=categories
            )
            return {"success": True, "data": result, "categories": categories}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_get_prior_research(self, arguments: Dict) -> Dict:
        """Get prior research for a topic."""
        topic = arguments.get('topic', '')
        research_type = arguments.get('research_type', 'all')
        limit = arguments.get('limit', 5)

        try:
            results = self.unified_search.unified_search(
                query=topic,
                include_spiders=False,
                include_research=True,
                research_limit=limit
            )
            return {"success": True, "data": results, "topic": topic}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_spider_query(self, arguments: Dict) -> Dict:
        """Query spider network."""
        query = arguments.get('query', '')
        categories = arguments.get('categories', self.get_spider_categories())
        limit = arguments.get('limit', 20)

        try:
            from core.services.spider_intelligence import SpiderIntelligenceService
            service = SpiderIntelligenceService()
            # Session 1002B: Fixed — search_intelligence() doesn't exist, use search_spider_data()
            results = service.search_spider_data(
                query=query,
                category=categories[0] if isinstance(categories, list) and len(categories) == 1 else None,
                hours=72,
                limit=limit
            )
            discussions = results if isinstance(results, list) else []
            logger.info(f"{self.name}: Spider query returned {len(discussions)} results")
            return {"success": True, "discussions": discussions, "query": query}
        except Exception as e:
            logger.error(f"{self.name}: spider_query error: {e}")
            return {"success": False, "error": str(e), "discussions": []}

    def _handle_web_search(self, arguments: Dict) -> Dict:
        """Perform web search."""
        query = arguments.get('query', '')
        num_results = arguments.get('num_results', 10)

        try:
            from core.agents import ResearchAgent
            agent = ResearchAgent()
            results = agent.web_search(query, num_results=num_results)
            logger.info(f"{self.name}: Web search returned {len(results) if results else 0} results")
            return {"success": True, "results": results or [], "query": query}
        except Exception as e:
            logger.error(f"{self.name}: web_search error: {e}")
            return {"success": False, "error": str(e), "results": []}

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
                        if isinstance(d, dict):
                            source_articles.append({
                                'title': d.get('title', ''),
                                'description': str(d.get('description', d.get('content', '')))[:300],
                                'url': d.get('url', ''),
                                'source': d.get('source', source)
                            })

                # Handle web_search results
                elif 'results' in item_data:
                    for r in item_data.get('results', []):
                        if isinstance(r, dict):
                            source_articles.append({
                                'title': r.get('title', ''),
                                'description': str(r.get('snippet', r.get('description', '')))[:300],
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
