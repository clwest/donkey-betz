"""
Customer Research Agent - Business Intelligence
================================================

Session 293: Business Research Extension
Session 303: Unified Intelligence Search + Auto Spider Refresh
Session 304: Learning Infrastructure Integration
Session 325: Unified Spider Network - Same semantic search as CompetitorAnalysisAgent

This agent researches potential customers for a business idea.
It uses spider data (Reddit, HackerNews, YouTube, tech news) and web search to:
1. Identify target customer segments
2. Extract pain points and needs
3. Analyze customer sentiment
4. Build customer personas

Tools Available:
    - spider_query: Query spider network with SEMANTIC SEARCH (all categories)
    - web_search: Search for customer reviews and feedback
    - analyze_pain_points: Extract pain points from discussions
    - build_persona: Build customer persona from research
    - refresh_spider_data: Trigger fresh spider crawls for up-to-date data
    - get_prior_research: Retrieve relevant past research
    - reddit_search: Real-time search of any Reddit subreddit

Tools NOT Available (by design):
    - image/video/audio generation
    - editing operations
"""

import logging
import time
import json
import re
from typing import Dict, Any, List
from collections import Counter

from core.agents.base_agent import BaseAgent, AgentResult


def strip_html_tags(text: str) -> str:
    """Strip HTML tags from text (Session 325: aligned with CompetitorAnalysisAgent)."""
    if not text:
        return ''
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text(separator=' ', strip=True)
        clean_text = ' '.join(clean_text.split())
        return clean_text
    except Exception:
        return re.sub(r'<[^>]+>', '', text).strip()


logger = logging.getLogger(__name__)


class CustomerResearchAgent(BaseAgent):
    """
    Agent specialized in customer research and persona development.

    This agent:
    1. Takes a market/product description
    2. Searches Reddit, forums, and reviews for customer discussions
    3. Extracts pain points, needs, and desires
    4. Builds customer personas with demographics and motivations

    It CANNOT:
    - Generate images, videos, or audio
    - Edit any content
    - Create 3D models
    """

    name = "CustomerResearchAgent"

    system_prompt = """You are CustomerResearchAgent, a specialist in customer research and persona development.

Your ONLY job is to research potential customers and build personas. You do NOT create content.

You have these tools:
- spider_query: MUST USE - Query spider network for REAL discussions (Reddit, HackerNews, tech news, community forums)
- reddit_search: Search ANY Reddit subreddit in real-time (use for specific communities!)
- web_search: Search for customer reviews, testimonials, and feedback
- analyze_pain_points: Extract pain points from gathered discussions
- build_persona: Build detailed customer persona from research
- get_prior_research: Optional - retrieve past research for context
- refresh_spider_data: Optional - trigger fresh data collection

CRITICAL - You MUST call spider_query:
Session 325: The spider_query tool connects to our real-time spider network with 74 spiders across 24 sources.
You MUST call spider_query to get actual discussions from Reddit, HackerNews, YouTube, tech news, etc.
WITHOUT spider_query data, you cannot provide a proper customer research report - you'd be guessing!
Prior research (get_prior_research) is just context - it does NOT replace calling spider_query!

IMPORTANT - Dynamic Reddit Search (Session 312):
For specific subreddits NOT in our spider network, use reddit_search:
- Industry-specific: r/podcasting, r/coffee, r/fitness, r/photography
- Business: r/smallbusiness, r/SaaS, r/marketing, r/ecommerce
- Niche: r/solotravel, r/homebrewing, r/woodworking
- Combine subreddits: "smallbusiness+Entrepreneur+startups"

When given a customer research task:
1. FIRST: Call spider_query with a relevant search query to get REAL discussions (MANDATORY!)
2. OPTIONALLY: Check get_prior_research for context from previous analyses
3. Use reddit_search for specific industry subreddits NOT in spider network
4. Use web_search for reviews of existing solutions
5. Extract pain points and desires (analyze_pain_points)
6. Build 2-3 customer personas (build_persona)

Example subreddit choices by market:
- AI Content Generation for Creators: "podcasting+youtube+blogging+contentcreation+NewTubers"
- Podcast tools: reddit_search in "podcasting+podcasts+audioengineering"
- YouTube/Video creators: reddit_search in "youtube+NewTubers+videography+contentcreation"
- Blogging/Writing: reddit_search in "blogging+juststart+writing+copywriting"
- SaaS products: reddit_search in "SaaS+startups+indiehackers"
- Fitness apps: reddit_search in "fitness+running+bodybuilding"

CRITICAL: Match your research to the ACTUAL market requested!
- If asked about "AI for podcasters" → research podcaster pain points, NOT developer pain points
- If asked about "content creators" → research YouTubers, bloggers, podcasters
- Your personas should be REAL people in that market (e.g., "Sarah the Solo Podcaster")

Output Format:
Return structured research with:
- target_market: Description of the target market
- pain_points: List of customer pain points with frequency
- desires: What customers want but can't find
- personas: 2-3 detailed customer personas
- quotes: Direct quotes from customers (anonymized)
- recommendations: Product/messaging recommendations

You CANNOT create images, videos, audio, or edit anything. Only research customers.
If asked to create content, explain you can only research and suggest using the appropriate agent."""

    tools = [
        # Session 325: spider_query FIRST - this is our primary data source!
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "MUST USE FIRST: Query spider network for REAL discussions from Reddit, HackerNews, YouTube, tech news. This provides actual customer data for analysis - without it you're just guessing!",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'AI writing tool frustrating', 'need better podcast hosting')"
                        },
                        "subreddits": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific subreddits to search (optional)",
                            "default": None
                        },
                        "sentiment": {
                            "type": "string",
                            "description": "Filter by sentiment",
                            "enum": ["positive", "negative", "question", "all"],
                            "default": "all"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 720
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 50
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
                "description": "Search for customer reviews, testimonials, and feedback about existing solutions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'Jasper AI reviews', 'podcast hosting complaints')"
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search",
                            "enum": ["reviews", "discussions", "news"],
                            "default": "reviews"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results",
                            "default": 15
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_pain_points",
                "description": "Analyze gathered discussions to extract and rank pain points",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "discussions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of discussion texts to analyze"
                        },
                        "market_context": {
                            "type": "string",
                            "description": "Context about the market/product"
                        }
                    },
                    "required": ["market_context"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "build_persona",
                "description": "Build a detailed customer persona from research findings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "persona_type": {
                            "type": "string",
                            "description": "Type of persona (e.g., 'Early Adopter', 'Price-Sensitive', 'Power User')"
                        },
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key pain points for this persona"
                        },
                        "goals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What this persona wants to achieve"
                        },
                        "market_context": {
                            "type": "string",
                            "description": "The market/product context"
                        }
                    },
                    "required": ["persona_type", "market_context"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "extract_quotes",
                "description": "Extract powerful customer quotes from discussions for messaging/copy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic to find quotes about"
                        },
                        "quote_type": {
                            "type": "string",
                            "description": "Type of quotes to find",
                            "enum": ["pain", "desire", "frustration", "praise", "all"],
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max quotes to return",
                            "default": 10
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "refresh_spider_data",
                "description": "Trigger spider network to fetch fresh, real-time data before research. Use this at the START to ensure you have the latest community discussions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["tech", "financial", "jobs", "news", "creative", "community"]
                            },
                            "description": "Spider categories to refresh (defaults to auto-detect from query)",
                            "default": []
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
                "description": "Retrieve relevant past research from previous competitor and customer analyses. Use this to build on existing knowledge rather than starting from scratch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "market_topic": {
                            "type": "string",
                            "description": "Market/topic to find related research for (e.g., 'AI writing tools', 'coffee industry')"
                        },
                        "research_type": {
                            "type": "string",
                            "description": "Type of research to retrieve",
                            "enum": ["competitor", "customer", "all"],
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 5
                        }
                    },
                    "required": ["market_topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "reddit_search",
                "description": "Search ANY Reddit subreddit in real-time for customer discussions. Use this for specific communities not covered by spider_query (which only caches 15 subreddits). Examples: r/smallbusiness, r/SaaS, r/podcasting, r/coffee, or any industry-specific subreddit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'podcast hosting frustrated', 'need better invoicing')"
                        },
                        "subreddits": {
                            "type": "string",
                            "description": "Subreddit(s) to search, joined with +. Examples: 'podcasting', 'smallbusiness+Entrepreneur', 'SaaS+startups+indiehackers'. Use 'all' to search all of Reddit.",
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 25
                        },
                        "sort": {
                            "type": "string",
                            "description": "Sort order for results",
                            "enum": ["relevance", "hot", "top", "new"],
                            "default": "relevance"
                        },
                        "time_filter": {
                            "type": "string",
                            "description": "Time period to search within",
                            "enum": ["hour", "day", "week", "month", "year", "all"],
                            "default": "month"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    # Pain point indicators for extraction
    PAIN_INDICATORS = [
        'frustrated', 'annoying', 'hate', 'wish', 'problem', 'issue',
        'difficult', 'hard to', 'can\'t find', 'looking for', 'need',
        'expensive', 'too slow', 'doesn\'t work', 'broken', 'buggy',
        'missing', 'lacks', 'want', 'hoping', 'struggling'
    ]

    DESIRE_INDICATORS = [
        'love', 'wish', 'hope', 'want', 'need', 'looking for',
        'would pay for', 'dream', 'ideal', 'perfect', 'best'
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._spider_service = None
        self._semantic_search = None  # Session 325: Added for unified spider network
        self._unified_search = None
        self._gathered_discussions = []

    @property
    def spider_service(self):
        """Lazy-load Spider Intelligence Service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

    @property
    def semantic_search(self):
        """Session 325: Lazy-load Spider Semantic Search Service (same as CompetitorAnalysisAgent)."""
        if self._semantic_search is None:
            from core.services.spider_semantic_search import get_spider_semantic_search
            self._semantic_search = get_spider_semantic_search()
        return self._semantic_search

    @property
    def unified_search(self):
        """Session 303: Lazy-load Unified Intelligence Search Service."""
        if self._unified_search is None:
            from core.services.unified_intelligence_search import get_unified_intelligence_search
            self._unified_search = get_unified_intelligence_search()
        return self._unified_search

    def _get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Session 302: Fetch project context when project_id is provided.
        Session 350: Enhanced with domain targeting for spider queries.

        This enables users to say "Research customer pain points for this project"
        and have the agent automatically use the project's topic/description.

        Args:
            project_id: UUID of the PartnershipProject

        Returns:
            Dict with project context (name, description, type, domain targeting) or empty dict
        """
        if not project_id:
            return {}

        try:
            from core.models_partnership import PartnershipProject
            project = PartnershipProject.objects.get(id=project_id)

            # Session 350: Get or extract domain targeting
            domain_targeting = {}
            try:
                domain_targeting = project.get_domain_targeting()
                logger.info(f"Domain targeting for project: {domain_targeting.get('primary_domain')}, tags: {domain_targeting.get('domain_tags', [])[:5]}")
            except Exception as e:
                logger.warning(f"Failed to get domain targeting: {e}")

            return {
                'project_name': project.project_name,
                'project_description': project.description,
                'project_type': project.project_type,
                'project_id': str(project.id),
                # Session 350: Domain targeting for spider queries
                'domain_targeting': domain_targeting,
                'primary_domain': domain_targeting.get('primary_domain', 'general_startup'),
                'domain_tags': domain_targeting.get('domain_tags', []),
                'spider_queries': domain_targeting.get('spider_queries', []),
                'domain_subreddits': domain_targeting.get('subreddits', [])
            }
        except Exception as e:
            logger.warning(f"Failed to fetch project context: {e}")
            return {}

    def _enhance_task_with_project(self, task: str, project_context: Dict[str, Any]) -> str:
        """
        Session 302: Enhance the task with project context.

        If user says "Research customer pain points" and we have project context,
        enhance it to "Research customer pain points for [project name]: [description]"

        Args:
            task: Original task
            project_context: Dict from _get_project_context()

        Returns:
            Enhanced task with project context
        """
        if not project_context:
            return task

        project_name = project_context.get('project_name', '')
        project_description = project_context.get('project_description', '')

        # If task is vague (doesn't specify what to research), add project context
        vague_indicators = ['pain points', 'customer research', 'personas', 'customers']
        is_vague = any(indicator in task.lower() for indicator in vague_indicators) and \
                   len(task.split()) < 15  # Short task likely needs context

        if is_vague and project_name:
            enhanced = f"{task} for '{project_name}'"
            if project_description and len(project_description) < 200:
                enhanced += f": {project_description}"
            logger.info(f"Enhanced task with project context: {enhanced[:100]}...")
            return enhanced

        return task

    def _check_business_viability(self, task: str) -> Dict[str, Any]:
        """
        Session 350: "Idiot Protector" - Check if business idea is viable.

        Uses GPT to quickly assess if the business idea is:
        1. Viable - Proceed normally
        2. Questionable - Add warning but proceed
        3. Absurd/Joke - Strong warning, still proceed (user might be testing)

        Args:
            task: The business idea or research request

        Returns:
            Dict with viability_score (0-100), assessment, warning (if any)
        """
        try:
            from openai import OpenAI
            client = OpenAI()

            check_prompt = f"""Evaluate this business idea/research request for basic viability.

Business Idea: {task}

Score from 0-100:
- 80-100: Viable, reasonable business idea
- 50-79: Questionable but possible (niche, risky, or unusual)
- 20-49: Highly impractical or likely to fail
- 0-19: Joke/absurd/impossible (e.g., "selling air", "restaurant for invisible food")

Respond in JSON format:
{{
    "viability_score": <0-100>,
    "assessment": "<one sentence assessment>",
    "is_joke": <true/false>,
    "warning": "<warning message if score < 50, otherwise null>",
    "proceed": <true/false - always true, we analyze anyway>
}}

Be direct and honest. Don't sugarcoat absurd ideas."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": check_prompt}],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result['proceed'] = True  # Always proceed - we're warning, not blocking

            logger.info(f"Viability check: score={result.get('viability_score')}, joke={result.get('is_joke')}")

            return result

        except Exception as e:
            logger.warning(f"Viability check failed (proceeding anyway): {e}")
            return {
                'viability_score': 50,
                'assessment': 'Unable to assess viability',
                'is_joke': False,
                'warning': None,
                'proceed': True
            }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute customer research based on the task."""
        start_time = time.time()
        tool_calls_made = []
        all_research_data = []
        self._gathered_discussions = []

        with self.time_travel_session("customer_research", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # Session 302: Check for project_id in context and fetch project data
                project_id = context.get('project_id')
                project_context = self._get_project_context(project_id) if project_id else {}

                # Session 302: Enhance task with project context if available
                enhanced_task = self._enhance_task_with_project(task, project_context)

                # Session 300: Check for vague requests and look up prior research context
                # This enables the "cumulative intelligence" flow where customer research
                # automatically uses context from prior competitor analysis
                enhanced_task = self._enhance_task_with_prior_research(enhanced_task)

                # Session 303: Store current task for tool access
                self._current_task = enhanced_task

                # Session 350: "Idiot Protector" - Check business viability
                viability = self._check_business_viability(enhanced_task)
                viability_warning = None
                if viability.get('viability_score', 100) < 50:
                    viability_warning = viability.get('warning') or viability.get('assessment')
                    if viability.get('is_joke'):
                        viability_warning = f"⚠️ This appears to be a joke or highly impractical idea. {viability_warning}"
                    self.record_decision(
                        decision_type="viability_check",
                        action="Flagged low viability business idea",
                        reasoning=f"Score: {viability.get('viability_score')}, Assessment: {viability.get('assessment')}",
                        confidence=0.85
                    )
                    logger.warning(f"Low viability idea detected (score={viability.get('viability_score')}): {enhanced_task[:50]}...")

                # Session 303: Auto-trigger spider refresh for fresh community data
                try:
                    refresh_result = self.unified_search.refresh_spiders_for_query(enhanced_task)
                    logger.info(f"Auto-triggered spider refresh: {refresh_result.get('categories', [])}")
                    self.record_decision(
                        decision_type="data_refresh",
                        action="Triggered spider network refresh",
                        reasoning=f"Ensuring fresh community discussions for: {enhanced_task[:50]}",
                        confidence=0.9
                    )
                except Exception as e:
                    logger.warning(f"Auto spider refresh failed (continuing anyway): {e}")

                # Session 303: Get prior research context
                prior_context = ""
                try:
                    prior_context = self.unified_search.get_research_context(
                        query=enhanced_task,
                        max_spider_items=3,
                        max_research_items=2
                    )
                    if prior_context:
                        logger.info(f"Found prior research context ({len(prior_context)} chars)")
                except Exception as e:
                    logger.warning(f"Prior research lookup failed: {e}")

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing customer research request",
                    reasoning=f"Received task: {task[:100]}, enhanced: {enhanced_task != task}",
                    confidence=0.9
                )

                # Build prompt with context
                full_prompt = self._build_prompt(enhanced_task, scifi_context, spider_context)

                # Session 303: Inject prior research context if available
                if prior_context:
                    full_prompt += f"\n\n{prior_context}\n"

                # Session 350: Add domain-aware spider targeting instructions
                domain_instructions = ""
                if project_context.get('domain_targeting'):
                    targeting = project_context['domain_targeting']
                    domain_instructions = f"""

DOMAIN-SPECIFIC RESEARCH GUIDANCE (Session 350):
Primary Domain: {targeting.get('primary_domain', 'general_startup')}
Domain Tags: {', '.join(targeting.get('domain_tags', [])[:8])}
Suggested Subreddits: {', '.join(targeting.get('subreddits', [])[:6])}
Suggested Search Queries: {targeting.get('spider_queries', [])[:5]}

CRITICAL: Use these DOMAIN-SPECIFIC subreddits and search queries!
Do NOT use generic developer or tech subreddits unless that's the target domain.
Your research should match the SPECIFIC market: {project_context.get('project_name', enhanced_task)[:100]}
"""

                # Add instruction to be comprehensive - Session 325: Emphasize spider_query is MANDATORY
                # Session 325b: Added explicit instruction to focus on the ACTUAL query topic
                full_prompt += f"""

CRITICAL: For thorough customer research you MUST:
1. FIRST call spider_query to get REAL discussions about the SPECIFIC topic in the user's request
   - This is MANDATORY - without it your analysis is just assumptions!
   - Your spider_query should match the user's topic: "{enhanced_task[:100]}"
   - For content creators: search for podcasters, YouTubers, bloggers pain points
   - For SaaS: search for the specific tool category frustrations
2. Use reddit_search for industry-specific subreddits matching the topic
   - Use the DOMAIN-SPECIFIC subreddits listed above
   - For the user's actual industry, NOT generic developer communities
3. Use web_search to find reviews of existing solutions in that SPECIFIC market
4. Use analyze_pain_points to synthesize your findings
5. Use build_persona to create 2-3 customer personas FOR THE SPECIFIC MARKET
{domain_instructions}
IMPORTANT: Focus your research on the ACTUAL topic requested: "{enhanced_task[:150]}"
Do NOT drift to generic "developer tools" or "AI platforms" unless that's what was asked.
Your personas and pain points must match the TARGET MARKET in the request.

Return comprehensive customer research with personas, pain points, and real quotes from customers in the SPECIFIC market requested."""

                # Make GPT call to determine tools to use
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for customer research",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_research_data.append({
                                'source': tool_name,
                                'data': tool_result.get('data', tool_result)
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                execution_time = int((time.time() - start_time) * 1000)

                if all_research_data:
                    # Synthesize the customer research
                    synthesis = self._synthesize_research(task, all_research_data)

                    # Session 294: Save to database with embedding for semantic search
                    # Session 349: Pass project_id to link research to project
                    saved_result = None
                    try:
                        from core.models_unified_system import BusinessResearchResult
                        project_id = context.get('project_id')
                        saved_result = BusinessResearchResult.save_customer_research(
                            query=task,
                            synthesis=synthesis,
                            execution_time_ms=execution_time,
                            project_id=project_id,  # Session 349: Link to project
                            user=self.user  # Session 349: Link to user
                        )
                        logger.info(f"Saved customer research to database: {saved_result.id}, project_id={project_id}")
                    except Exception as e:
                        logger.warning(f"Failed to save customer research: {e}")

                    # Session 294: Return analysis at top level for frontend compatibility
                    # Frontend checks agentResult.analysis and agentResult.data?.analysis
                    # Session 350: Include viability warning in result
                    result_message = f"Customer research completed with {len(all_research_data)} data sources"
                    if viability_warning:
                        result_message = f"⚠️ VIABILITY WARNING: {viability_warning}\n\n{result_message}"

                    result = AgentResult(
                        success=True,
                        message=result_message,
                        data={
                            'analysis': synthesis,  # Match CompetitorAnalysisAgent pattern
                            'raw_data': all_research_data,
                            'query': task,
                            'saved_id': str(saved_result.id) if saved_result else None,
                            # Session 350: Viability assessment
                            'viability': {
                                'score': viability.get('viability_score', 100),
                                'assessment': viability.get('assessment'),
                                'is_joke': viability.get('is_joke', False),
                                'warning': viability_warning
                            } if viability_warning else None
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # === Session 304: Learning Infrastructure ===
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=True,  # Always uses spider data
                        scifi_context_used=bool(scifi_context)
                    )

                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7  # Customer research is important
                    )

                    # Track contribution to research result
                    if saved_result:
                        self._track_contribution(
                            content_type='research',
                            content_id=saved_result.id,
                            contribution_type='primary_creator',
                            contribution_score=1.0
                        )

                    # Share knowledge about customer insights
                    if synthesis.get('analysis'):
                        self._share_knowledge(
                            knowledge_type='user_behavior',
                            title=f"Customer Research: {task[:80]}",
                            knowledge_value={
                                'query': task,
                                'discussions_analyzed': synthesis.get('discussions_analyzed', 0),
                                'sources': synthesis.get('sources_used', []),
                                'success': True
                            },
                            confidence=0.85
                        )

                    return result
                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', 'No customer data found'),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

            except Exception as e:
                logger.error(f"CustomerResearchAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call for customer research."""

        if tool_name == "spider_query":
            return self._search_customer_discussions(
                query=arguments.get('query', ''),
                subreddits=arguments.get('subreddits'),
                sentiment=arguments.get('sentiment', 'all'),
                hours=arguments.get('hours', 720),
                limit=arguments.get('limit', 50)
            )

        elif tool_name == "web_search":
            try:
                from core.tools.web_search import WebSearchTool
                search_tool = WebSearchTool()

                # Modify query based on search type
                search_type = arguments.get('search_type', 'reviews')
                query = arguments.get('query', '')

                if search_type == 'reviews':
                    query = f"{query} reviews user feedback"
                elif search_type == 'discussions':
                    query = f"{query} forum discussion reddit"

                results = search_tool.search(
                    query=query,
                    max_results=arguments.get('num_results', 15),
                    search_type='search'
                )
                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                logger.warning(f"Web search failed: {e}, using spider fallback")
                return self._search_customer_discussions(
                    query=arguments.get('query', ''),
                    hours=720,
                    limit=20
                )

        elif tool_name == "analyze_pain_points":
            return self._analyze_pain_points(
                discussions=arguments.get('discussions', self._gathered_discussions),
                market_context=arguments.get('market_context', '')
            )

        elif tool_name == "build_persona":
            return self._build_customer_persona(
                persona_type=arguments.get('persona_type', 'Target Customer'),
                pain_points=arguments.get('pain_points', []),
                goals=arguments.get('goals', []),
                market_context=arguments.get('market_context', '')
            )

        elif tool_name == "extract_quotes":
            return self._extract_customer_quotes(
                topic=arguments.get('topic', ''),
                quote_type=arguments.get('quote_type', 'all'),
                limit=arguments.get('limit', 10)
            )

        elif tool_name == "refresh_spider_data":
            # Session 303: Trigger fresh spider crawls
            try:
                categories = arguments.get('categories', [])
                # Use the current task/query to determine categories if not specified
                result = self.unified_search.refresh_spiders_for_query(
                    query=self._current_task if hasattr(self, '_current_task') else '',
                    categories=categories if categories else None
                )
                return {
                    'success': True,
                    'data': result,
                    'message': f"Triggered spider refresh for: {result.get('categories', [])}"
                }
            except Exception as e:
                logger.warning(f"Spider refresh failed: {e}")
                return {
                    'success': False,
                    'error': f"Spider refresh failed: {str(e)}"
                }

        elif tool_name == "get_prior_research":
            # Session 303: Get prior research from unified intelligence
            try:
                market_topic = arguments.get('market_topic', '')
                research_type = arguments.get('research_type', 'all')
                limit = arguments.get('limit', 5)

                # Use unified search for combined results
                results = self.unified_search.unified_search(
                    query=market_topic,
                    include_spiders=False,  # Only get research, not spider data
                    include_research=True,
                    research_limit=limit
                )

                # Also get context string for prompt injection
                context = self.unified_search.get_research_context(
                    query=market_topic,
                    max_spider_items=0,
                    max_research_items=limit
                )

                return {
                    'success': True,
                    'data': [
                        {
                            'title': r.title,
                            'description': r.description,
                            'research_type': r.research_type,
                            'market_topic': r.market_topic,
                            'similarity': r.similarity
                        }
                        for r in results
                    ],
                    'context': context,
                    'count': len(results)
                }
            except Exception as e:
                logger.warning(f"Prior research lookup failed: {e}")
                return {
                    'success': False,
                    'error': f"Prior research lookup failed: {str(e)}"
                }

        elif tool_name == "reddit_search":
            # Session 312: Dynamic Reddit search for ANY subreddit
            return self._reddit_dynamic_search(
                query=arguments.get('query', ''),
                subreddits=arguments.get('subreddits', 'all'),
                limit=arguments.get('limit', 25),
                sort=arguments.get('sort', 'relevance'),
                time_filter=arguments.get('time_filter', 'month')
            )

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

    def _search_customer_discussions(
        self,
        query: str,
        subreddits: List[str] = None,
        sentiment: str = 'all',
        hours: int = 720,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Session 325: Search spider data for customer discussions using SEMANTIC SEARCH.

        Now uses the same semantic search as CompetitorAnalysisAgent for:
        - Better query matching with embeddings
        - Access to all spider categories (tech, news, community, video, etc.)
        - HTML stripping for cleaner results
        """
        try:
            # Session 325: Use semantic search for better results (same as CompetitorAnalysisAgent)
            # This searches across ALL categories with embedding-based similarity
            results = self.semantic_search.semantic_search(
                query=query,
                category=None,  # Search all categories
                hours=hours,
                limit=limit,
                min_similarity=0.3  # Same threshold as CompetitorAnalysisAgent
            )

            # Convert SemanticSearchResult objects to dicts with HTML stripping
            all_results = []
            for r in results:
                # Session 325: Strip HTML from titles and descriptions (aligned with CompetitorAnalysisAgent)
                cleaned_title = strip_html_tags(r.title)
                cleaned_description = strip_html_tags(r.description)

                item = {
                    'title': cleaned_title,
                    'description': cleaned_description[:300],
                    'content': cleaned_description,  # For backward compatibility
                    'url': r.url,
                    'source': r.source,
                    'similarity': r.similarity,
                    'category': r.category
                }
                all_results.append(item)

                # Store for later pain point analysis
                self._gathered_discussions.append(
                    f"[{r.source}] {cleaned_title} - {cleaned_description[:200]}"
                )

            # Filter by sentiment if specified
            if sentiment != 'all':
                all_results = self._filter_by_sentiment(all_results, sentiment)

            # Get unique sources for reporting
            sources = list(set(r.get('source', '') for r in all_results if r.get('source')))

            return {
                'success': True,
                'data': {
                    'discussions': all_results[:limit],
                    'total_found': len(all_results),
                    'sources': sources,
                    'search_type': 'semantic'  # Indicate semantic search was used
                }
            }

        except Exception as e:
            logger.error(f"Semantic search failed: {e}, falling back to basic search")
            # Fallback to basic spider service if semantic search fails
            return self._basic_spider_search(query, hours, limit, sentiment)

    def _basic_spider_search(
        self,
        query: str,
        hours: int,
        limit: int,
        sentiment: str
    ) -> Dict[str, Any]:
        """
        Session 325: Fallback to basic spider service if semantic search fails.

        This uses the original SpiderIntelligenceService for keyword-based search.
        """
        try:
            all_results = []

            # Search across multiple categories
            for category in ['social', 'tech', 'community', 'news']:
                results = self.spider_service.search_spider_data(
                    query=query,
                    category=category,
                    hours=hours,
                    limit=limit // 4
                )
                all_results.extend(results)

            # Deduplicate by title
            seen_titles = set()
            unique_results = []
            for item in all_results:
                title = strip_html_tags(item.get('title', ''))
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    item['title'] = title
                    item['description'] = strip_html_tags(item.get('description', item.get('content', '')))[:300]
                    unique_results.append(item)
                    self._gathered_discussions.append(
                        f"[{item.get('source', '')}] {title} - {item.get('description', '')[:200]}"
                    )

            if sentiment != 'all':
                unique_results = self._filter_by_sentiment(unique_results, sentiment)

            return {
                'success': True,
                'data': {
                    'discussions': unique_results[:limit],
                    'total_found': len(unique_results),
                    'sources': list(set(r.get('source', '') for r in unique_results)),
                    'search_type': 'basic'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Customer discussion search failed: {str(e)}"
            }

    def _filter_by_sentiment(
        self,
        results: List[Dict],
        sentiment: str
    ) -> List[Dict]:
        """Filter results by sentiment."""
        filtered = []
        for item in results:
            text = (item.get('title', '') + ' ' + item.get('content', '')).lower()

            if sentiment == 'negative':
                if any(word in text for word in ['frustrated', 'hate', 'problem', 'issue', 'annoying']):
                    filtered.append(item)
            elif sentiment == 'positive':
                if any(word in text for word in ['love', 'great', 'amazing', 'perfect', 'recommend']):
                    filtered.append(item)
            elif sentiment == 'question':
                if '?' in text or text.startswith(('how', 'what', 'why', 'when', 'where', 'can')):
                    filtered.append(item)
            else:
                filtered.append(item)

        return filtered

    def _analyze_pain_points(
        self,
        discussions: List[str],
        market_context: str
    ) -> Dict[str, Any]:
        """Analyze discussions to extract and rank pain points."""

        if not discussions:
            discussions = self._gathered_discussions

        pain_points = []
        desires = []

        for discussion in discussions:
            text = discussion.lower()

            # Extract pain points
            for indicator in self.PAIN_INDICATORS:
                if indicator in text:
                    # Find the sentence containing the indicator
                    sentences = re.split(r'[.!?]', discussion)
                    for sentence in sentences:
                        if indicator in sentence.lower() and len(sentence) > 20:
                            pain_points.append(sentence.strip())
                            break

            # Extract desires
            for indicator in self.DESIRE_INDICATORS:
                if indicator in text:
                    sentences = re.split(r'[.!?]', discussion)
                    for sentence in sentences:
                        if indicator in sentence.lower() and len(sentence) > 20:
                            desires.append(sentence.strip())
                            break

        # Count and rank pain points by frequency
        pain_counter = Counter(pain_points)
        desire_counter = Counter(desires)

        return {
            'success': True,
            'data': {
                'pain_points': [
                    {'text': text, 'frequency': count}
                    for text, count in pain_counter.most_common(15)
                ],
                'desires': [
                    {'text': text, 'frequency': count}
                    for text, count in desire_counter.most_common(10)
                ],
                'total_discussions_analyzed': len(discussions),
                'market_context': market_context
            }
        }

    def _build_customer_persona(
        self,
        persona_type: str,
        pain_points: List[str],
        goals: List[str],
        market_context: str
    ) -> Dict[str, Any]:
        """Build a detailed customer persona using GPT."""

        persona_prompt = f"""Create a detailed customer persona for this market:

Market Context: {market_context}
Persona Type: {persona_type}
Key Pain Points: {', '.join(pain_points[:5]) if pain_points else 'To be determined from research'}
Goals: {', '.join(goals[:5]) if goals else 'To be determined from research'}

Generate a detailed persona with:
- Name (fictional)
- Demographics (age range, occupation, income level)
- Background (1-2 sentences)
- Goals (what they want to achieve)
- Pain Points (specific frustrations)
- Motivations (why they'd buy)
- Objections (why they might not buy)
- Preferred Channels (where they spend time online)
- Quote (something this persona might say)

Return as JSON with these keys."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": persona_prompt}],
                max_completion_tokens=1000,
                reasoning_effort="medium",
            )

            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    persona_data = json.loads(content[start:end])
                else:
                    persona_data = {'raw_response': content}
            except json.JSONDecodeError:
                persona_data = {'raw_response': content}

            return {
                'success': True,
                'data': {
                    'persona_type': persona_type,
                    'persona': persona_data
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Persona generation failed: {str(e)}"
            }

    def _extract_customer_quotes(
        self,
        topic: str,
        quote_type: str,
        limit: int
    ) -> Dict[str, Any]:
        """Extract powerful customer quotes from gathered discussions."""

        quotes = []

        for discussion in self._gathered_discussions:
            text = discussion

            # Check for quote type indicators
            include = False
            if quote_type == 'all':
                include = True
            elif quote_type == 'pain':
                include = any(word in text.lower() for word in ['frustrated', 'hate', 'problem', 'annoying'])
            elif quote_type == 'desire':
                include = any(word in text.lower() for word in ['wish', 'want', 'need', 'hope'])
            elif quote_type == 'frustration':
                include = any(word in text.lower() for word in ['frustrated', 'hate', 'tired', 'sick of'])
            elif quote_type == 'praise':
                include = any(word in text.lower() for word in ['love', 'amazing', 'great', 'perfect'])

            if include and len(text) > 30:
                # Clean up the quote
                quote = text[:300] + '...' if len(text) > 300 else text
                quotes.append({
                    'text': quote,
                    'type': quote_type,
                    'topic': topic
                })

        return {
            'success': True,
            'data': {
                'quotes': quotes[:limit],
                'total_found': len(quotes),
                'topic': topic
            }
        }

    def _enhance_task_with_prior_research(self, task: str) -> str:
        """
        Session 300: Simple pass-through - context should come from frontend buttons.

        The frontend now properly passes the original query from prior research,
        so this method just logs and returns the task as-is.

        If we need to enhance context in the future (e.g., for voice commands
        that don't go through buttons), we can add semantic search here.
        """
        logger.debug(f"CustomerResearchAgent received task: {task[:100]}...")
        return task

    def _synthesize_research(
        self,
        task: str,
        all_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize all gathered data into coherent customer research using GPT.

        Session 294: Added GPT synthesis like CompetitorAnalysisAgent to generate
        a proper Customer Research Report instead of just returning raw data.
        Session 325: Added HTML stripping (aligned with CompetitorAnalysisAgent).
        """

        # Collect all discussion content for GPT analysis
        all_discussions = []
        all_pain_points = []
        all_personas = []
        all_quotes = []
        discussion_count = 0
        sources_used = set()

        for source in all_data:
            data = source.get('data', {})
            source_name = source.get('source', '')

            if source_name == 'spider_query':
                discussions = data.get('discussions', [])
                discussion_count += len(discussions)
                for d in discussions[:20]:  # Limit per source
                    sources_used.add(d.get('source', 'unknown'))
                    # Session 325: Strip HTML from titles and content (aligned with CompetitorAnalysisAgent)
                    all_discussions.append({
                        'title': strip_html_tags(d.get('title', '')),
                        'content': strip_html_tags(d.get('content', d.get('description', '')))[:300],
                        'source': d.get('source', ''),
                        'url': d.get('url', '')
                    })

            elif source_name == 'analyze_pain_points':
                pain_points = data.get('pain_points', [])
                all_pain_points.extend(pain_points)

            elif source_name == 'build_persona':
                persona = data.get('persona', {})
                if persona:
                    all_personas.append(persona)

            elif source_name == 'extract_quotes':
                quotes = data.get('quotes', [])
                all_quotes.extend(quotes)

        # Limit total discussions to avoid token limits
        all_discussions = all_discussions[:40]

        # Build discussion summary for GPT
        discussions_text = "\n".join([
            f"- [{d['source']}] {d['title']}: {d['content'][:150]}..."
            for d in all_discussions if d['title']
        ])

        # Build GPT synthesis prompt
        synthesis_prompt = f"""You are a customer research analyst. Analyze the following customer discussions and community data to provide actionable customer insights.

RESEARCH QUERY: {task}

CUSTOMER DISCUSSIONS COLLECTED ({len(all_discussions)} from {', '.join(sources_used)}):
{discussions_text}

Based on this data, provide a comprehensive CUSTOMER RESEARCH REPORT with:

1. **TARGET MARKET OVERVIEW** (2-3 sentences about who these customers are)

2. **TOP PAIN POINTS** (5-7 specific pain points with examples from the data)
   - Be specific about what customers are struggling with
   - Include quotes or paraphrased examples where possible

3. **CUSTOMER DESIRES & GOALS** (4-5 things customers want but can't find)
   - What are they trying to achieve?
   - What features/solutions are they asking for?

4. **CUSTOMER PERSONAS** (2-3 distinct customer types you see in the data)
   - Give each a name and brief description
   - What motivates them? What frustrates them?

5. **ACTIONABLE QUOTES** (3-5 powerful quotes from customers that could be used for marketing/copy)
   - Direct quotes that express pain or desire

6. **RECOMMENDATIONS** (3-4 actionable recommendations for product/marketing)
   - Based on the pain points and desires, what should a business do?

Be specific and reference actual data points. This analysis will be used for product development and marketing."""

        try:
            # Session 294: gpt-5-mini uses tokens for internal reasoning first
            # Need 6000+ tokens to ensure room for reasoning + visible output
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_completion_tokens=6000,  # High enough for reasoning + output
            )

            analysis_text = response.choices[0].message.content

            return {
                'query': task,
                'analysis': analysis_text,  # GPT-generated report
                'discussions_analyzed': discussion_count,
                'data_points_analyzed': len(all_discussions),
                'sources_used': list(sources_used),
                'pain_points': all_pain_points[:10],
                'personas': all_personas,
                'customer_quotes': all_quotes[:10],
                'data_sources': len(all_data),
                'raw_data': all_discussions  # Include for reference
            }

        except Exception as e:
            logger.error(f"GPT customer research synthesis failed: {e}")
            # Fallback to basic summary
            return {
                'query': task,
                'analysis': f"Analyzed {discussion_count} discussions from {', '.join(sources_used)}. Synthesis generation failed.",
                'discussions_analyzed': discussion_count,
                'pain_points': all_pain_points[:10],
                'personas': all_personas,
                'customer_quotes': all_quotes[:10],
                'data_sources': len(all_data),
                'error': str(e)
            }

    def _reddit_dynamic_search(
        self,
        query: str,
        subreddits: str = 'all',
        limit: int = 25,
        sort: str = 'relevance',
        time_filter: str = 'month'
    ) -> Dict[str, Any]:
        """
        Session 312: Dynamic Reddit search for ANY subreddit.

        First tries the registered RedditSearchTool (requires API credentials).
        Falls back to public JSON endpoint if credentials aren't configured.

        Args:
            query: Search query
            subreddits: Subreddit(s) to search, joined with +
            limit: Max results
            sort: Sort order (relevance, hot, top, new)
            time_filter: Time period (hour, day, week, month, year, all)

        Returns:
            Dict with success status and search results
        """
        try:
            # Try the registered RedditSearchTool first (uses PRAW with full API)
            from core.tools import ToolRegistry
            reddit_tool = ToolRegistry.get_tool('reddit_api')

            if reddit_tool and reddit_tool.is_configured:
                logger.info(f"Using RedditSearchTool for: {query} in r/{subreddits}")
                result = reddit_tool.execute(
                    query=query,
                    search_type='posts',
                    subreddit=subreddits,
                    limit=limit,
                    sort=sort,
                    time_filter=time_filter
                )

                if result.get('success'):
                    # Store discussions for later pain point analysis
                    for post in result.get('data', {}).get('results', []):
                        self._gathered_discussions.append(
                            f"[r/{post.get('subreddit', '')}] {post.get('title', '')} - {post.get('selftext', '')[:200]}"
                        )
                    return result

            # Fallback: Use public JSON endpoint (no auth required)
            logger.info(f"Using public Reddit JSON for: {query} in r/{subreddits}")
            return self._reddit_public_json_search(query, subreddits, limit)

        except Exception as e:
            logger.error(f"Reddit dynamic search failed: {e}")
            return {
                'success': False,
                'error': f"Reddit search failed: {str(e)}"
            }

    def _reddit_public_json_search(
        self,
        query: str,
        subreddits: str = 'all',
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Session 312: Fallback Reddit search using public JSON endpoints.

        Works without API credentials - uses reddit.com's public JSON API.
        Rate limited but functional for research purposes.

        Args:
            query: Search query
            subreddits: Subreddit(s) to search
            limit: Max results

        Returns:
            Dict with success status and search results
        """
        import requests
        from datetime import datetime

        try:
            headers = {
                'User-Agent': 'DonkeyBetz-CustomerResearch/1.0 (AI Content Studio; Educational Research)'
            }

            # Build search URL
            url = f"https://www.reddit.com/r/{subreddits}/search.json"
            params = {
                'q': query,
                'limit': min(limit, 100),  # Reddit caps at 100
                'restrict_sr': 'true' if subreddits != 'all' else 'false',
                'sort': 'relevance',
                't': 'month'  # Time filter
            }

            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])

                results = []
                for post in posts:
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')[:500]
                    subreddit_name = post_data.get('subreddit', '')

                    results.append({
                        'id': post_data.get('id', ''),
                        'title': title,
                        'selftext': selftext,
                        'subreddit': subreddit_name,
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': datetime.fromtimestamp(
                            post_data.get('created_utc', 0)
                        ).isoformat() if post_data.get('created_utc') else None,
                        'author': post_data.get('author', '[deleted]'),
                        'upvote_ratio': post_data.get('upvote_ratio', 0),
                    })

                    # Store for pain point analysis
                    self._gathered_discussions.append(
                        f"[r/{subreddit_name}] {title} - {selftext[:200]}"
                    )

                logger.info(f"Public Reddit search returned {len(results)} results for '{query}' in r/{subreddits}")

                return {
                    'success': True,
                    'data': {
                        'query': query,
                        'subreddit': subreddits,
                        'results': results,
                        'total_results': len(results),
                        'source': 'reddit_public_json',
                        'timestamp': datetime.now().isoformat()
                    }
                }

            elif response.status_code == 429:
                logger.warning("Reddit rate limit hit, returning empty results")
                return {
                    'success': False,
                    'error': "Reddit rate limit reached. Try again in a few minutes."
                }
            else:
                logger.warning(f"Reddit returned status {response.status_code}")
                return {
                    'success': False,
                    'error': f"Reddit returned status {response.status_code}"
                }

        except requests.Timeout:
            return {
                'success': False,
                'error': "Reddit search timed out"
            }
        except Exception as e:
            logger.error(f"Public Reddit JSON search failed: {e}")
            return {
                'success': False,
                'error': f"Reddit search failed: {str(e)}"
            }
