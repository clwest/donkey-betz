"""
Brand Strategy Agent - Business Intelligence
=============================================

Session 334: New agent for comprehensive brand strategy research

This agent synthesizes existing project research (competitor analysis, customer research)
and creates a comprehensive brand strategy report with actionable recommendations.

Unlike the old brand_identity_package workflow that just generated logos, this agent:
1. Reads existing project research (competitor + customer insights)
2. Conducts additional brand-specific research
3. Synthesizes a comprehensive brand strategy report with:
   - Brand Positioning Analysis
   - Target Audience Alignment
   - Competitive Differentiation Strategy
   - Visual Direction Recommendations
   - Messaging Guidelines
   - Actionable Brand Recommendations
4. Saves to BusinessResearchResult for project learning

Tools Available:
    - get_project_research: Fetch existing competitor/customer research from project
    - spider_query: Search for brand/design trends and best practices
    - web_search: Search for industry branding examples
    - synthesize_brand_strategy: Generate comprehensive brand strategy report

Tools NOT Available (by design):
    - image/video/audio generation (use ImageAgent after brand strategy)
    - editing operations
"""

import logging
import re
import time
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_brand_strategy_with_ml(strategy_data: dict) -> dict:
    """Analyze brand strategy data using ML models (Text + Clustering)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for strategic text analysis
        result = router.auto_route(
            data=strategy_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'strategy_clusters': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML brand strategy analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class BrandStrategyAgent(BaseAgent):
    """
    Agent specialized in brand strategy research and recommendations.

    This agent:
    1. Takes a project with existing research OR a brand/business topic
    2. Fetches existing competitor and customer research from project
    3. Conducts brand-specific research (trends, best practices, visual direction)
    4. Synthesizes a comprehensive brand strategy report
    5. Provides actionable recommendations for brand identity

    Key difference from old brand_identity_package workflow:
    - Produces RESEARCH like CompetitorAnalysisAgent (rich text report)
    - Builds on existing project research (cumulative intelligence)
    - Does NOT generate images (use ImageAgent after getting brand strategy)
    """

    name = "BrandStrategyAgent"
    create_deliverable_on_schedule = True  # Fixed: was False (Session 1077), outputs were lost in AgentExecution

    system_prompt = """You are BrandStrategyAgent, a specialist in brand strategy and identity development.

Your ONLY job is to analyze brand positioning and provide strategic recommendations. You do NOT create images.

You have these tools:
- get_project_research: ALWAYS USE FIRST - Fetch existing competitor/customer research from the project
- spider_query: Search for branding trends, design inspiration, and industry best practices
- web_search: Search for brand examples, visual trends, and positioning strategies
- synthesize_brand_strategy: Generate the final comprehensive brand strategy report

CRITICAL WORKFLOW:
1. FIRST: Call get_project_research to fetch ALL existing research from the project
   - This gives you competitor analysis, customer personas, pain points, market insights
   - This is the FOUNDATION of your brand strategy
2. THEN: Call spider_query to find current branding trends and visual direction
3. OPTIONALLY: Call web_search for specific brand examples or industry standards
4. FINALLY: Call synthesize_brand_strategy with all gathered data

Your output should include:
1. BRAND POSITIONING ANALYSIS
   - Market position based on competitor analysis
   - Unique value proposition derived from research

2. TARGET AUDIENCE ALIGNMENT
   - Customer personas (from existing research)
   - Pain points the brand should address visually
   - Emotional triggers and messaging hooks

3. COMPETITIVE DIFFERENTIATION STRATEGY
   - How to stand out from competitors (based on competitor analysis)
   - Visual differentiation opportunities
   - Messaging differentiation

4. VISUAL DIRECTION RECOMMENDATIONS
   - Color palette suggestions (with rationale tied to audience)
   - Typography direction
   - Imagery style (abstract, photographic, illustrative)
   - Logo concept directions (icon-only, wordmark, combination)

5. MESSAGING GUIDELINES
   - Brand voice and tone
   - Key messages tied to customer pain points
   - Tagline suggestions

6. ACTIONABLE RECOMMENDATIONS
   - Immediate next steps
   - Priority visual assets to create
   - Brand consistency guidelines

You CANNOT create images, videos, or audio. Only research and strategize.
After your brand strategy is complete, the user can use ImageAgent to generate visual assets."""

    tools = [
        # Tool 1: MOST IMPORTANT - Get existing project research
        {
            "type": "function",
            "function": {
                "name": "get_project_research",
                "description": "MUST USE FIRST: Fetch all existing research from the project (competitor analysis, customer research, market insights). This is the foundation of your brand strategy.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_competitor": {
                            "type": "boolean",
                            "description": "Include competitor analysis research",
                            "default": True
                        },
                        "include_customer": {
                            "type": "boolean",
                            "description": "Include customer research (personas, pain points)",
                            "default": True
                        },
                        "include_market": {
                            "type": "boolean",
                            "description": "Include market research if available",
                            "default": True
                        }
                    },
                    "required": []
                }
            }
        },
        # Tool 2: Spider query for brand/design trends
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "Search spider network for branding trends, design inspiration, visual direction, and industry best practices.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for brand/design trends (e.g., 'AI startup branding trends 2025', 'podcast brand identity')"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                            "enum": ["creative", "tech", "news", "all"],
                            "default": "creative"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        # web_search tool definition removed — handled by BaseAgent fallback (Session 1090)
        # Tool 4: Synthesize brand strategy
        {
            "type": "function",
            "function": {
                "name": "synthesize_brand_strategy",
                "description": "Generate comprehensive brand strategy report from all gathered research and data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project/brand"
                        },
                        "project_context": {
                            "type": "string",
                            "description": "Brief description of the project/business"
                        },
                        "competitor_insights": {
                            "type": "string",
                            "description": "Key insights from competitor analysis"
                        },
                        "customer_insights": {
                            "type": "string",
                            "description": "Key insights from customer research (personas, pain points)"
                        },
                        "brand_trends": {
                            "type": "string",
                            "description": "Current branding trends and visual direction from spider/web research"
                        }
                    },
                    "required": ["project_name"]
                }
            }
        },
        # Tool 5: Session 336 - Refresh spider data for fresh insights
        {
            "type": "function",
            "function": {
                "name": "refresh_spider_data",
                "description": "Trigger spider network to fetch fresh, real-time data before analysis. Use this at the START of analysis to ensure you have the latest branding trends and market data.",
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
        # Tool 6: Session 336 - Get prior research from unified intelligence
        {
            "type": "function",
            "function": {
                "name": "get_prior_research",
                "description": "Retrieve relevant past research from previous competitor, customer, and brand analyses. Use this to build on existing knowledge rather than starting from scratch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "market_topic": {
                            "type": "string",
                            "description": "Market/topic to find related research for (e.g., 'AI tools branding', 'podcast brand identity')"
                        },
                        "research_type": {
                            "type": "string",
                            "description": "Type of research to retrieve",
                            "enum": ["competitor", "customer", "brand_strategy", "all"],
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
        }
    ]

    def __init__(self, user=None, project_id: str = None):
        super().__init__(user)
        self.project_id = project_id
        self._spider_service = None
        self._semantic_search = None
        self._unified_search = None

    @property
    def semantic_search(self):
        """Lazy-load Spider Semantic Search Service."""
        if self._semantic_search is None:
            from core.services.spider_semantic_search import get_spider_semantic_search
            self._semantic_search = get_spider_semantic_search()
        return self._semantic_search

    @property
    def unified_search(self):
        """Session 336: Lazy-load Unified Intelligence Search Service."""
        if self._unified_search is None:
            from core.services.unified_intelligence_search import get_unified_intelligence_search
            self._unified_search = get_unified_intelligence_search()
        return self._unified_search

    def _get_project_context(self) -> Dict[str, Any]:
        """Fetch project context including existing research."""
        if not self.project_id:
            return {'has_project': False}

        try:
            from core.models_partnership import PartnershipProject
            from core.models_unified_system import BusinessResearchResult

            project = PartnershipProject.objects.get(id=self.project_id)

            context = {
                'has_project': True,
                'project_id': str(project.id),
                'project_name': project.project_name,
                'project_description': project.description or '',
                'project_type': project.project_type or 'general',
                'competitor_analysis': '',
                'customer_research': '',
                'customer_personas': [],
                'customer_pain_points': [],
                'market_overview': '',
            }

            # Get existing research from BusinessResearchResult
            research_results = BusinessResearchResult.objects.filter(
                project=project
            ).order_by('-created_at')

            for result in research_results[:10]:
                if result.research_type == 'competitor' and not context['competitor_analysis']:
                    context['competitor_analysis'] = result.analysis or ''
                    if result.recommendations:
                        context['competitor_recommendations'] = result.recommendations
                elif result.research_type == 'customer' and not context['customer_research']:
                    context['customer_research'] = result.analysis or ''
                    if result.personas:
                        context['customer_personas'] = result.personas
                    if result.pain_points:
                        context['customer_pain_points'] = result.pain_points
                elif result.research_type == 'market' and not context['market_overview']:
                    context['market_overview'] = result.analysis or ''

            # Also check metadata for research summaries (Session 325 format)
            if project.metadata and project.metadata.get('research_summaries'):
                for summary in project.metadata['research_summaries']:
                    if summary.get('type') == 'competitor_analysis' and not context['competitor_analysis']:
                        context['competitor_analysis'] = summary.get('summary', '')
                    elif summary.get('type') == 'customer_research' and not context['customer_research']:
                        context['customer_research'] = summary.get('summary', '')

            # Determine if we have meaningful research
            context['has_research'] = bool(
                context['competitor_analysis'] or
                context['customer_research'] or
                context['customer_personas']
            )

            logger.info(f"BrandStrategyAgent: Found project context for {project.project_name}, has_research={context['has_research']}")

            return context

        except Exception as e:
            logger.warning(f"Failed to fetch project context: {e}")
            return {'has_project': False}

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute brand strategy research."""
        start_time = time.time()
        tool_calls_made = []
        all_brand_data = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        # Get project_id from context if not set
        if not self.project_id:
            self.project_id = context.get('project_id')

        with self.time_travel_session("brand_strategy", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # Get project context
                project_context = self._get_project_context()
                self._project_context = project_context  # Store for tool access

                # Enhance task with project name if available
                if project_context.get('has_project'):
                    project_name = project_context.get('project_name', '')
                    if project_name and project_name.lower() not in task.lower():
                        task = f"{task} for '{project_name}'"
                        logger.info(f"Enhanced task with project name: {task}")

                # Session 336: Store current task for tool access
                self._current_task = task

                # Session 336: Auto-trigger spider refresh for fresh branding data
                try:
                    refresh_result = self.unified_search.refresh_spiders_for_query(task)
                    logger.info(f"Auto-triggered spider refresh: {refresh_result.get('categories', [])}")
                    self.record_decision(
                        decision_type="data_refresh",
                        action="Triggered spider network refresh",
                        reasoning=f"Ensuring fresh branding data for: {task[:50]}",
                        confidence=0.9
                    )
                except Exception as e:
                    logger.warning(f"Auto spider refresh failed (continuing anyway): {e}")

                # Session 336: Get prior research context
                prior_context = ""
                try:
                    prior_context = self.unified_search.get_research_context(
                        query=task,
                        max_spider_items=3,
                        max_research_items=2
                    )
                    if prior_context:
                        logger.info(f"Found prior research context ({len(prior_context)} chars)")
                except Exception as e:
                    logger.warning(f"Prior research lookup failed (continuing anyway): {e}")

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing brand strategy request",
                    reasoning=f"Task: {task[:100]}, Has project research: {project_context.get('has_research', False)}",
                    confidence=0.9
                )

                # Build prompt with context
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)

                # Add project research context to prompt
                if project_context.get('has_research'):
                    full_prompt += f"""

EXISTING PROJECT RESEARCH (use this as the foundation):
- Project: {project_context.get('project_name', 'Unknown')}
- Description: {project_context.get('project_description', 'N/A')[:500]}
- Competitor Analysis Available: {'Yes' if project_context.get('competitor_analysis') else 'No'}
- Customer Research Available: {'Yes' if project_context.get('customer_research') else 'No'}
- Customer Personas: {len(project_context.get('customer_personas', []))} defined
- Pain Points: {len(project_context.get('customer_pain_points', []))} identified

IMPORTANT: Call get_project_research FIRST to load the full research data."""

                # Session 336: Add prior research context if available
                if prior_context:
                    full_prompt += f"""

PRIOR RESEARCH CONTEXT (from unified intelligence):
{prior_context[:2000]}"""

                full_prompt += """

WORKFLOW:
1. FIRST: Call get_project_research to load existing competitor/customer research
2. THEN: Call spider_query for branding trends relevant to this industry
3. OPTIONALLY: Call web_search for brand examples
4. FINALLY: Call synthesize_brand_strategy with all gathered insights

Return a comprehensive brand strategy report that builds on existing project research."""

                # Make GPT call
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for brand strategy",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_brand_data.append({
                                'source': tool_name,
                                'data': tool_result.get('data', tool_result)
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    # Fallback: if GPT didn't call web_search, make an explicit call
                    tools_used = {tc['tool'] for tc in tool_calls_made}
                    if 'web_search' not in tools_used:
                        search_query = self._extract_search_query(task)
                        if search_query:
                            logger.info(f"[Fallback] GPT skipped web_search, running: {search_query[:80]}")
                            web_result = self._execute_tool_call('web_search', {'query': search_query, 'num_results': 10})
                            if web_result.get('success'):
                                all_brand_data.append({'source': 'web_search', 'data': web_result.get('data', web_result)})
                                tool_calls_made.append({'tool': 'web_search', 'arguments': {'query': search_query}, 'result': web_result})

                execution_time = int((time.time() - start_time) * 1000)

                if all_brand_data:
                    # Find the synthesized strategy in the tool results
                    synthesis = None
                    for data in all_brand_data:
                        if data['source'] == 'synthesize_brand_strategy':
                            synthesis = data['data']
                            break

                    # If no synthesis yet, create one from gathered data
                    if not synthesis:
                        synthesis = self._synthesize_brand_strategy_fallback(
                            project_context.get('project_name', task),
                            all_brand_data
                        )

                    # Save to database
                    saved_result = None
                    try:
                        from core.models_unified_system import BusinessResearchResult
                        from core.models_partnership import PartnershipProject

                        project = None
                        if self.project_id:
                            try:
                                project = PartnershipProject.objects.get(id=self.project_id)
                            except:
                                pass

                        saved_result = BusinessResearchResult.objects.create(
                            user=self.user,
                            project=project,
                            research_type='brand_strategy',
                            market_topic=project_context.get('project_name', task),
                            analysis=synthesis.get('strategy', synthesis.get('analysis', str(synthesis))),
                            recommendations=synthesis.get('recommendations', []),
                            execution_time_ms=execution_time
                        )
                        logger.info(f"Saved brand strategy to database: {saved_result.id}")
                    except Exception as e:
                        logger.warning(f"Failed to save brand strategy: {e}")

                    # Session 337: Extract source articles for frontend display (like CustomerResearchAgent)
                    # Filter out the synthesis tool result - we only want spider/web data sources
                    source_articles = []
                    sources_used = set()
                    for data_item in all_brand_data:
                        if data_item['source'] not in ['synthesize_brand_strategy', 'get_project_research', 'get_prior_research']:
                            sources_used.add(data_item['source'])
                            # Extract articles from the data
                            item_data = data_item.get('data', {})
                            if isinstance(item_data, dict):
                                # Handle spider_query results
                                if 'discussions' in item_data:
                                    for d in item_data.get('discussions', []):
                                        source_articles.append({
                                            'title': d.get('title', ''),
                                            'description': d.get('description', d.get('content', ''))[:300],
                                            'url': d.get('url', ''),
                                            'source': d.get('source', data_item['source'])
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
                                # Handle raw list items
                                elif 'items' in item_data:
                                    for item in item_data.get('items', []):
                                        source_articles.append({
                                            'title': item.get('title', ''),
                                            'description': item.get('description', '')[:300],
                                            'url': item.get('url', ''),
                                            'source': data_item['source']
                                        })

                    # Session 1200: Use synthesis content as message
                    analysis_text = synthesis.get('strategy', synthesis.get('analysis', '')) if isinstance(synthesis, dict) else str(synthesis)
                    analysis_msg = analysis_text if analysis_text else f"Brand strategy completed with {len(all_brand_data)} data sources"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'analysis': synthesis.get('strategy', synthesis.get('analysis', str(synthesis))),
                            'visual_direction': synthesis.get('visual_direction', {}),
                            'recommendations': synthesis.get('recommendations', []),
                            'raw_data': all_brand_data,  # Session 337: Include raw data for frontend
                            'sources_used': list(sources_used),  # Session 337: Track sources
                            'data_points_analyzed': len(source_articles),  # Session 337: Count articles
                            'project_name': project_context.get('project_name', ''),
                            'query': task,
                            'saved_id': str(saved_result.id) if saved_result else None,
                            'research_type': 'brand_strategy'
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Learning infrastructure
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=True,
                        scifi_context_used=bool(scifi_context)
                    )

                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.8  # Brand strategy is important
                    )

                    if saved_result:
                        self._track_contribution(
                            content_type='research',
                            content_id=saved_result.id,
                            contribution_type='primary_creator',
                            contribution_score=1.0
                        )

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"Brand Strategy: {task[:80]}",
                        content=result.message,
                        deliverable_type='analysis',
                        category='Brand Strategy',
                        tags=['brand', 'strategy'],
                        metadata={'task': task[:200]},
                    )

                    return result

                else:
                    # Return conversational response if no tools called
                    content = gpt_response.get('content') or ''

                    # If no content but we have a simple query, provide self-description
                    if not content and ('name' in task.lower() or 'capability' in task.lower() or 'who are you' in task.lower()):
                        content = f"I am {self.name}, a specialist in brand strategy and identity development. One capability: I can synthesize competitor analysis, customer research, and market trends into comprehensive brand positioning recommendations with visual direction guidelines."
                    elif not content:
                        content = 'No brand strategy data generated. Please provide a brand or business to analyze.'

                    return AgentResult(
                        success=True,
                        message=content,
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

            except Exception as e:
                logger.error(f"BrandStrategyAgent error: {e}")
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
        """Execute a tool call for brand strategy."""

        if tool_name == "get_project_research":
            # Return the pre-loaded project context
            project_context = getattr(self, '_project_context', {})

            if not project_context.get('has_project'):
                return {
                    'success': False,
                    'error': "No project context available. Please provide a project_id or specify a brand/business to research."
                }

            return {
                'success': True,
                'data': {
                    'project_name': project_context.get('project_name', ''),
                    'project_description': project_context.get('project_description', ''),
                    'competitor_analysis': project_context.get('competitor_analysis', ''),
                    'customer_research': project_context.get('customer_research', ''),
                    'customer_personas': project_context.get('customer_personas', []),
                    'customer_pain_points': project_context.get('customer_pain_points', []),
                    'market_overview': project_context.get('market_overview', ''),
                    'has_research': project_context.get('has_research', False)
                }
            }

        elif tool_name == "spider_query":
            try:
                results = self.semantic_search.semantic_search(
                    query=arguments.get('query', ''),
                    category=arguments.get('category'),
                    hours=168,
                    limit=arguments.get('limit', 20),
                    min_similarity=0.3
                )
                data = [
                    {
                        'title': r.title,
                        'description': r.description,
                        'url': r.url,
                        'source': r.source,
                        'category': r.category
                    }
                    for r in results
                ]
                return {
                    'success': True,
                    'data': data
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Spider query failed: {str(e)}"
                }

        elif tool_name == "web_search":
            # Session 1090: Deprecated — fall through to BaseAgent universal handler
            logger.warning(f"[{self.__class__.__name__}] web_search is deprecated — falling through to BaseAgent handler")
            return super()._execute_tool_call(tool_name, arguments)

        elif tool_name == "synthesize_brand_strategy":
            return self._generate_brand_strategy(
                project_name=arguments.get('project_name', ''),
                project_context=arguments.get('project_context', ''),
                competitor_insights=arguments.get('competitor_insights', ''),
                customer_insights=arguments.get('customer_insights', ''),
                brand_trends=arguments.get('brand_trends', '')
            )

        elif tool_name == "refresh_spider_data":
            # Session 336: Trigger fresh spider crawls for branding data
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
            # Session 336: Get prior research from unified intelligence
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

        return super()._execute_tool_call(tool_name, arguments)

    def _generate_brand_strategy(
        self,
        project_name: str,
        project_context: str = '',
        competitor_insights: str = '',
        customer_insights: str = '',
        brand_trends: str = ''
    ) -> Dict[str, Any]:
        """Generate comprehensive brand strategy using GPT with style library awareness."""

        # Session 394: Get style library recommendations based on the business idea
        from core.services.style_library import (
            get_brand_recommendations,
            get_style_library_summary
        )

        # Detect industry and get recommendations
        brand_recs = get_brand_recommendations(project_name + ' ' + project_context)
        style_summary = get_style_library_summary()

        # Build list of recommended style names for the prompt
        rec_style_names = [s['display_name'] for s in brand_recs.get('style_options', [])]
        avoid_style_names = brand_recs.get('avoid_styles', [])

        # Build color palette descriptions
        rec_palette_desc = ""
        for p in brand_recs.get('color_palettes', []):
            colors_hex = ' '.join(p['colors'])
            rec_palette_desc += f"- {p['name']}: {p['description']} ({colors_hex})\n"

        # Build logo direction descriptions
        rec_logo_desc = ""
        for l in brand_recs.get('logo_directions', []):
            rec_logo_desc += f"- {l['name']}: {l['description']} (e.g., {', '.join(l['examples'])})\n"

        strategy_prompt = f"""You are a senior brand strategist with access to a comprehensive style library of 80+ visual styles.

PROJECT: {project_name}
{f'CONTEXT: {project_context}' if project_context else ''}
DETECTED INDUSTRY: {brand_recs.get('detected_industry', 'general')}

COMPETITOR ANALYSIS INSIGHTS:
{competitor_insights if competitor_insights else 'No competitor analysis available yet.'}

CUSTOMER RESEARCH INSIGHTS:
{customer_insights if customer_insights else 'No customer research available yet.'}

CURRENT BRANDING TRENDS:
{brand_trends if brand_trends else 'No specific trends data gathered.'}

=== STYLE LIBRARY GUIDANCE (Session 394) ===
Based on the detected industry, here are the recommended approaches:

RECOMMENDED VISUAL STYLES (pick 2-3):
{', '.join(rec_style_names) if rec_style_names else 'minimalist, vector, digital_art'}

STYLES TO AVOID for this industry:
{', '.join(avoid_style_names) if avoid_style_names else 'None specifically - use judgment'}

INDUSTRY NOTES:
{brand_recs.get('industry_notes', 'Consider the target audience and competitive landscape.')}

RECOMMENDED COLOR PALETTES:
{rec_palette_desc if rec_palette_desc else '- Professional: Trust-inspiring blues and neutrals'}

RECOMMENDED LOGO DIRECTIONS:
{rec_logo_desc if rec_logo_desc else '- Icon + Wordmark: A symbol paired with the brand name'}

CRITICAL: Do NOT default to "cyberpunk" style just because something involves AI or tech.
Most AI/tech brands benefit more from minimalist, clean, or friendly styles that build trust.
Only recommend cyberpunk if it genuinely fits the brand's rebellious or edgy positioning.

=== END STYLE LIBRARY GUIDANCE ===

Based on this research and style guidance, create a COMPREHENSIVE BRAND STRATEGY REPORT with:

1) BRAND POSITIONING ANALYSIS
- Market position recommendation based on competitor landscape
- Unique value proposition that differentiates from competitors
- Key brand pillars (3-4 core values/attributes)

2) TARGET AUDIENCE ALIGNMENT
- Primary and secondary audience profiles (based on customer research)
- Key pain points the brand should address
- Emotional triggers and psychological hooks for brand connection

3) COMPETITIVE DIFFERENTIATION STRATEGY
- How to visually differentiate from competitors
- Messaging differentiation opportunities
- Positioning statement recommendation

4) VISUAL DIRECTION RECOMMENDATIONS (IMPORTANT - use style library!)
- PRIMARY STYLE: Pick ONE main style from the recommended list above
- SECONDARY STYLE: Pick ONE complementary style
- COLOR PALETTE: Recommend ONE palette from the options above with specific hex codes
- TYPOGRAPHY: Direction (modern, classic, playful, authoritative)
- LOGO DIRECTION: Pick ONE from the recommended logo types above
- MOOD: One word describing the overall feel (friendly, professional, bold, etc.)

5) MESSAGING GUIDELINES
- Brand voice and tone recommendations
- Key messages that address customer pain points
- Tagline suggestions (3 options)

6) ACTIONABLE NEXT STEPS
- Priority visual assets to create
- Brand consistency guidelines

OUTPUT FORMAT: Be specific with your style recommendations. Instead of vague suggestions,
name the exact styles from the library (e.g., "minimalist", "pixar", "vector") and
provide specific hex color codes."""

        try:
            # Session 857: Use retry-enabled completion call
            response = self._call_completion_with_retry(
                messages=[{"role": "user", "content": strategy_prompt}],
                model="gpt-5-mini",  # Session 857: Fixed model name
                max_completion_tokens=6000,
            )

            strategy_text = response.choices[0].message.content

            # Session 394: Extract structured visual direction for the review UI
            visual_direction = {
                'has_color_recommendations': True,
                'has_typography_recommendations': True,
                'has_logo_recommendations': True,
                # Include the style library recommendations for the UI
                'style_options': brand_recs.get('style_options', []),
                'color_palettes': brand_recs.get('color_palettes', []),
                'logo_directions': brand_recs.get('logo_directions', []),
                'detected_industry': brand_recs.get('detected_industry', ''),
                'avoid_styles': brand_recs.get('avoid_styles', [])
            }

            # Try to extract the primary style recommendation from GPT response
            strategy_lower = strategy_text.lower()
            primary_style = None
            for style in brand_recs.get('style_options', []):
                if style['name'] in strategy_lower or style['display_name'].lower() in strategy_lower:
                    primary_style = style['name']
                    break
            if primary_style:
                visual_direction['recommended_primary_style'] = primary_style

            recommendations = [
                'See detailed recommendations in report',
                f"Detected industry: {brand_recs.get('detected_industry', 'general')}",
                f"Style options: {', '.join(rec_style_names)}"
            ]

            return {
                'success': True,
                'data': {
                    'strategy': strategy_text,
                    'project_name': project_name,
                    'visual_direction': visual_direction,
                    'recommendations': recommendations,
                    'analysis': strategy_text,  # Alias for compatibility
                    # Session 394: Include structured data for Human-in-the-Loop review
                    'brand_review_data': {
                        'detected_industry': brand_recs.get('detected_industry', ''),
                        'style_options': brand_recs.get('style_options', []),
                        'color_palettes': brand_recs.get('color_palettes', []),
                        'logo_directions': brand_recs.get('logo_directions', []),
                        'avoid_styles': brand_recs.get('avoid_styles', []),
                        'industry_notes': brand_recs.get('industry_notes', ''),
                        'requires_human_review': True  # Flag for UI to show review step
                    }
                }
            }

        except Exception as e:
            logger.error(f"Brand strategy generation failed: {e}")
            return {
                'success': False,
                'error': f"Strategy generation failed: {str(e)}"
            }

    def _extract_search_query(self, task: str) -> str:
        """Extract a concise web search query from a verbose task description."""
        patterns = [
            r'(?:brand|branding|strategy)\s+(?:for|of)\s+(.{5,120}?)(?:\.|$)',
            r'(?:for|about|covering)\s+(.{10,120}?)(?:\.|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                fragment = match.group(1).strip().rstrip(',.')
                return f"brand strategy {fragment}"

        cleaned = re.sub(
            r'^(create|develop|build|generate)\s+(a\s+)?'
            r'(comprehensive\s+|detailed\s+)?'
            r'(brand\s+)?(strategy|identity|positioning)\s+'
            r'(for|on|of|about)\s+',
            '', task, flags=re.IGNORECASE
        ).strip()

        if cleaned and len(cleaned) > 5:
            return f"brand strategy {cleaned[:100]}"

        return task[:100]

    def _synthesize_brand_strategy_fallback(
        self,
        project_name: str,
        all_data: List[Dict]
    ) -> Dict[str, Any]:
        """Fallback synthesis if GPT tool call wasn't made."""

        # Collect insights from gathered data
        competitor_insights = ""
        customer_insights = ""
        brand_trends = ""

        for source in all_data:
            source_name = source.get('source', '')
            data = source.get('data', {})

            if source_name == 'get_project_research':
                competitor_insights = data.get('competitor_analysis', '')[:2000]
                customer_insights = data.get('customer_research', '')[:2000]
            elif source_name in ['spider_query', 'web_search']:
                # Normalize dict data: web_search returns {'results': [...]}, etc.
                if isinstance(data, dict):
                    data = data.get('results', data.get('data', data.get('discussions', [data])))
                    if not isinstance(data, list):
                        data = [data]
                if isinstance(data, list):
                    trend_items = [f"- {item.get('title', '')}" for item in data[:5] if isinstance(item, dict)]
                    brand_trends += "\n".join(trend_items)

        # Generate strategy with gathered data
        return self._generate_brand_strategy(
            project_name=project_name,
            competitor_insights=competitor_insights,
            customer_insights=customer_insights,
            brand_trends=brand_trends
        ).get('data', {'strategy': 'Brand strategy synthesis failed'})
