"""
Campaign Orchestrator Agent - The Marketing Campaign Hub
=========================================================

Session 513: The missing connector that ties together:
- Intelligence (spider data, web search, research)
- Agents (creation, strategy, writing)
- Autonomous (performance monitoring)
- Delivery (Discord, download, client management)

This agent takes a client brief and produces a complete marketing campaign.

Pipeline:
1. RESEARCH - Market trends, competitor analysis, customer insights
2. STRATEGY - Content strategy, brand direction, SEO keywords
3. CREATION - Ad copy, images, videos, emails, social posts
4. PACKAGING - Bundle deliverables for client
"""

import logging
import time
from typing import Dict, Any, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from core.agents.base_agent import BaseAgent, AgentResult

# Session 895: Timeout for sub-agent executions to prevent coordinator hangs
# Extended to 5 min to accommodate thinking models (GPT-5.1, o1, o3)
SUB_AGENT_TIMEOUT = 300  # 5 minutes per sub-agent
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_campaign_with_ml(campaign_data: dict) -> dict:
    """Analyze marketing campaign using ML models (Text + Clustering)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=campaign_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'campaign_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML campaign analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class CampaignOrchestratorAgent(BaseAgent):
    """
    Master orchestrator for marketing campaigns.

    Takes a campaign brief and coordinates multiple agents to produce
    a complete marketing package including:
    - Market research and competitor analysis
    - Content strategy and brand direction
    - Ad copy variations
    - Images (hero shots, banners, social graphics)
    - Video ads (optional based on tier)
    - Email sequences
    - Social media posts

    This is the HUB that finally connects all the pieces.
    """

    name = "CampaignOrchestratorAgent"

    system_prompt = """You are CampaignOrchestratorAgent, the master coordinator for marketing campaigns.

Your job is to take a client brief and orchestrate the creation of a complete marketing package.

You have access to specialized agents for each phase:
- ResearchAgent: Market research, competitor analysis, trend discovery
- CompetitorAnalysisAgent: Deep competitor research and SWOT analysis
- CustomerResearchAgent: Customer personas and pain points
- BrandIdentityAgent: Visual direction and brand consistency
- ContentStrategyAgent: Content planning and pillars
- SEOOptimizerAgent: Keywords, hashtags, metadata
- SocialMediaAgent: Platform-specific strategy
- ContentWriterAgent: Ad copy, emails, social posts
- ImageAgent: Hero images, banners, graphics
- VideoAgent: Video ads (for higher tiers)
- AudioAgent: Voiceovers (for higher tiers)

Campaign Flow:
1. RESEARCH PHASE (20% of progress)
   - Analyze market trends for the product/service
   - Research competitors
   - Identify target customer personas

2. STRATEGY PHASE (20% of progress)
   - Define brand direction and visual style
   - Create content strategy
   - Identify SEO keywords and hashtags

3. CREATION PHASE (50% of progress)
   - Generate ad copy variations
   - Create images for each platform
   - Write email sequence
   - Create social media posts
   - Generate video (if tier includes it)

4. PACKAGING PHASE (10% of progress)
   - Bundle all deliverables
   - Create campaign summary
   - Prepare for delivery

For each phase, you should:
1. Call the appropriate tool to delegate to specialized agents
2. Store results in the campaign
3. Update campaign progress
4. Move to the next phase

Always provide status updates and be transparent about what's being created."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_research_phase",
                "description": "Execute the research phase: market trends, competitor analysis, customer research",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_strategy_phase",
                "description": "Execute the strategy phase: brand direction, content strategy, SEO",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_creation_phase",
                "description": "Execute the creation phase: ad copy, images, videos, emails, social posts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_campaign_status",
                "description": "Get the current status and progress of a campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_campaign",
                "description": "Create a new campaign from a client brief",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Campaign name"
                        },
                        "product_name": {
                            "type": "string",
                            "description": "Product or service name"
                        },
                        "product_description": {
                            "type": "string",
                            "description": "Detailed description of the product/service"
                        },
                        "target_market": {
                            "type": "string",
                            "description": "Target audience description"
                        },
                        "budget_tier": {
                            "type": "string",
                            "enum": ["starter", "pro", "enterprise", "premium"],
                            "description": "Budget tier determines deliverables",
                            "default": "starter"
                        },
                        "competitors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of competitor names or URLs"
                        },
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Target platforms (facebook, instagram, craigslist, email, etc.)"
                        }
                    },
                    "required": ["name", "product_name", "product_description", "target_market"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._research_agent = None
        self._competitor_agent = None
        self._customer_agent = None
        self._brand_agent = None
        self._content_strategy_agent = None
        self._seo_agent = None
        self._writer_agent = None
        self._image_agent = None
        self._video_agent = None

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute the campaign orchestration."""
        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 739: Store context for sub-agent calls
        self._current_spider_context = spider_context
        self._current_scifi_context = scifi_context

        with self.time_travel_session("campaign_orchestration", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                attribution = None  # Legacy compatibility

                # Call GPT to determine actions
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []

                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Executing {tool_name}",
                            reasoning=f"Campaign orchestration step",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'action': tool_name,
                                'data': tool_result.get('data', {})
                            })

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                    analysis_msg = synthesis if synthesis else f"Campaign orchestration completed with {len(all_results)} actions"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'results': all_results,
                            'content': synthesis,
                            'task': task
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        tool_calls=tool_calls_made,
                        knowledge_attribution=attribution
                    )

                    # Record learning outcome
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )

                    return result

                else:
                    # Conversational response
                    # Session 757: Return rich conversation data for Memory Palace display
                    response_content = gpt_response.get('content', '')
                    return AgentResult(
                        success=True,
                        message=response_content,
                        data={
                            'type': 'conversation',
                            'content_type': 'campaign_discussion',
                            'response': response_content,
                            'query': task,
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        knowledge_attribution=attribution
                    )

            except Exception as e:
                logger.error(f"CampaignOrchestratorAgent error: {e}")
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
        """Execute a tool call."""

        if tool_name == "create_campaign":
            return self._create_campaign(arguments)

        elif tool_name == "get_campaign_status":
            return self._get_campaign_status(arguments.get('campaign_id'))

        elif tool_name == "run_research_phase":
            return self._run_research_phase(arguments.get('campaign_id'))

        elif tool_name == "run_strategy_phase":
            return self._run_strategy_phase(arguments.get('campaign_id'))

        elif tool_name == "run_creation_phase":
            return self._run_creation_phase(arguments.get('campaign_id'))

        return super()._execute_tool_call(tool_name, arguments)

    def _create_campaign(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign."""
        try:
            from core.models_campaign import Campaign

            campaign = Campaign.objects.create(
                user=self.user,
                name=args.get('name'),
                product_name=args.get('product_name'),
                product_description=args.get('product_description'),
                target_market=args.get('target_market'),
                budget_tier=args.get('budget_tier', 'starter'),
                competitors=args.get('competitors', []),
                platforms=args.get('platforms', ['general']),
                status='intake'
            )

            logger.info(f"Created campaign: {campaign.id} - {campaign.name}")

            return {
                'success': True,
                'data': {
                    'campaign_id': str(campaign.id),
                    'name': campaign.name,
                    'status': campaign.status,
                    'budget_tier': campaign.budget_tier,
                    'included_deliverables': campaign.get_included_deliverables()
                }
            }

        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return {'success': False, 'error': str(e)}

    def _get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign status."""
        try:
            from core.models_campaign import Campaign

            campaign = Campaign.objects.get(id=campaign_id)

            deliverables = list(campaign.deliverables.values(
                'id', 'name', 'deliverable_type', 'status', 'platform'
            ))

            return {
                'success': True,
                'data': {
                    'campaign_id': str(campaign.id),
                    'name': campaign.name,
                    'status': campaign.status,
                    'progress_percent': campaign.progress_percent,
                    'current_phase': campaign.current_phase,
                    'deliverables_count': len(deliverables),
                    'deliverables': deliverables[:10],  # First 10
                    'budget_tier': campaign.budget_tier
                }
            }

        except Exception as e:
            logger.error(f"Failed to get campaign status: {e}")
            return {'success': False, 'error': str(e)}

    def _run_research_phase(self, campaign_id: str) -> Dict[str, Any]:
        """Execute the research phase."""
        try:
            from core.models_campaign import Campaign, CampaignResearch
            from core.services.smart_trending_service import get_smart_trending_service

            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'research'
            campaign.current_phase = 'research'
            campaign.start_campaign()

            research_results = []

            # 1. Market trends research using SmartTrendingService (with web search fallback)
            logger.info(f"[Campaign {campaign_id}] Starting market trends research")
            trending_service = get_smart_trending_service()
            trends = trending_service.get_trending_for_query(
                f"What's trending for {campaign.product_name} in {campaign.target_market}?",
                use_cache=False
            )

            if trends.get('articles'):
                research = CampaignResearch.objects.create(
                    campaign=campaign,
                    research_type='market_trends',
                    title=f"Market Trends for {campaign.product_name}",
                    summary=f"Found {len(trends['articles'])} relevant articles",
                    data={
                        'trends': trends.get('trends', []),
                        'articles': trends.get('articles', [])[:10],
                        'used_web_search': trends.get('used_web_search', False)
                    },
                    source='web_search' if trends.get('used_web_search') else 'spider_network',
                    source_urls=[a.get('url', '') for a in trends.get('articles', [])[:5]],
                    agent_name='SmartTrendingService'
                )
                research_results.append({
                    'type': 'market_trends',
                    'articles_found': len(trends.get('articles', [])),
                    'used_web_search': trends.get('used_web_search', False)
                })

            # 2. Competitor research (if competitors provided)
            if campaign.competitors:
                logger.info(f"[Campaign {campaign_id}] Researching competitors: {campaign.competitors}")

                # Use web search for competitor research
                for competitor in campaign.competitors[:3]:  # Max 3 competitors
                    comp_trends = trending_service.get_trending_for_query(
                        f"{competitor} marketing strategy advertising",
                        use_cache=False
                    )

                    CampaignResearch.objects.create(
                        campaign=campaign,
                        research_type='competitor',
                        title=f"Competitor Analysis: {competitor}",
                        summary=f"Found {len(comp_trends.get('articles', []))} articles about {competitor}",
                        data={
                            'competitor': competitor,
                            'articles': comp_trends.get('articles', [])[:5]
                        },
                        source='web_search',
                        agent_name='SmartTrendingService'
                    )

                research_results.append({
                    'type': 'competitor_analysis',
                    'competitors_analyzed': len(campaign.competitors[:3])
                })

            # Update campaign progress
            campaign.research_data = {
                'trends': trends.get('trends', []),
                'articles_count': len(trends.get('articles', [])),
                'completed_at': datetime.now().isoformat()
            }
            campaign.update_progress('research', 20, {'completed': True})
            campaign.log_execution('research_phase_complete', {'results': research_results})

            logger.info(f"[Campaign {campaign_id}] Research phase complete")

            return {
                'success': True,
                'data': {
                    'campaign_id': campaign_id,
                    'phase': 'research',
                    'progress': 20,
                    'results': research_results
                }
            }

        except Exception as e:
            logger.error(f"Research phase failed: {e}")
            return {'success': False, 'error': str(e)}

    def _run_strategy_phase(self, campaign_id: str) -> Dict[str, Any]:
        """Execute the strategy phase."""
        try:
            from core.models_campaign import Campaign

            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'strategy'
            campaign.current_phase = 'strategy'
            campaign.save()

            strategy_results = []

            # 1. Generate content strategy based on research
            research_items = campaign.research_items.filter(research_type='market_trends').first()
            market_trends = research_items.data if research_items else {}

            # Build content pillars based on trends
            content_pillars = []
            if market_trends.get('trends'):
                for trend in market_trends['trends'][:5]:
                    content_pillars.append({
                        'topic': trend,
                        'content_types': ['ad_copy', 'social_post', 'image']
                    })

            campaign.content_strategy = {
                'pillars': content_pillars,
                'tone': 'professional' if 'enterprise' in campaign.budget_tier else 'conversational',
                'platforms': campaign.platforms,
                'generated_at': datetime.now().isoformat()
            }

            # 2. Generate SEO keywords from trends
            seo_keywords = []
            if market_trends.get('trends'):
                seo_keywords = [campaign.product_name] + market_trends['trends'][:10]

            campaign.seo_keywords = seo_keywords

            # 3. Brand direction
            campaign.brand_direction = {
                'style': campaign.brand_style or 'modern',
                'colors': campaign.brand_colors or ['#2563eb', '#1e40af', '#ffffff'],
                'tone': 'professional',
                'generated_at': datetime.now().isoformat()
            }

            campaign.update_progress('strategy', 40, {'completed': True})
            campaign.log_execution('strategy_phase_complete', {
                'content_pillars': len(content_pillars),
                'seo_keywords': len(seo_keywords)
            })

            logger.info(f"[Campaign {campaign_id}] Strategy phase complete")

            return {
                'success': True,
                'data': {
                    'campaign_id': campaign_id,
                    'phase': 'strategy',
                    'progress': 40,
                    'content_pillars': len(content_pillars),
                    'seo_keywords': seo_keywords[:5]
                }
            }

        except Exception as e:
            logger.error(f"Strategy phase failed: {e}")
            return {'success': False, 'error': str(e)}

    def _run_creation_phase(self, campaign_id: str) -> Dict[str, Any]:
        """Execute the creation phase - generate all deliverables."""
        try:
            from core.models_campaign import Campaign, CampaignDeliverable

            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'creation'
            campaign.current_phase = 'creation'
            campaign.save()

            included_deliverables = campaign.get_included_deliverables()
            creation_results = []

            # Get research data for context
            research = campaign.research_items.filter(research_type='market_trends').first()
            trends = research.data.get('trends', []) if research else []

            # 1. Generate Ad Copy Variations
            if 'ad_copy' in included_deliverables:
                ad_copies = self._generate_ad_copies(campaign, trends)
                for i, copy in enumerate(ad_copies):
                    CampaignDeliverable.objects.create(
                        campaign=campaign,
                        deliverable_type='ad_copy',
                        name=f"Ad Copy Variation {i+1}",
                        status='complete',
                        platform='general',
                        content_text=copy['text'],
                        content_data=copy,
                        created_by_agent='CampaignOrchestratorAgent'
                    )
                creation_results.append({'type': 'ad_copy', 'count': len(ad_copies)})

            # 2. Generate Social Posts
            if 'social_posts' in included_deliverables:
                posts = self._generate_social_posts(campaign, trends)
                for platform, post_list in posts.items():
                    for i, post in enumerate(post_list):
                        CampaignDeliverable.objects.create(
                            campaign=campaign,
                            deliverable_type='social_post',
                            name=f"{platform.title()} Post {i+1}",
                            status='complete',
                            platform=platform,
                            content_text=post,
                            created_by_agent='CampaignOrchestratorAgent'
                        )
                creation_results.append({'type': 'social_posts', 'count': sum(len(p) for p in posts.values())})

            # 3. Generate Email Sequence
            if 'email_sequence' in included_deliverables:
                emails = self._generate_email_sequence(campaign)
                for i, email in enumerate(emails):
                    CampaignDeliverable.objects.create(
                        campaign=campaign,
                        deliverable_type='email',
                        name=f"Email {i+1}: {email['subject'][:30]}",
                        status='complete',
                        platform='email',
                        content_text=email['body'],
                        content_data=email,
                        created_by_agent='CampaignOrchestratorAgent'
                    )
                creation_results.append({'type': 'email_sequence', 'count': len(emails)})

            # Update progress
            campaign.update_progress('creation', 90, {'completed': True})
            campaign.log_execution('creation_phase_complete', {'results': creation_results})

            # Mark campaign as complete
            campaign.complete_campaign()

            logger.info(f"[Campaign {campaign_id}] Creation phase complete")

            return {
                'success': True,
                'data': {
                    'campaign_id': campaign_id,
                    'phase': 'creation',
                    'progress': 100,
                    'deliverables_created': creation_results,
                    'status': 'complete'
                }
            }

        except Exception as e:
            logger.error(f"Creation phase failed: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_ad_copies(self, campaign, trends: List[str], use_agent: bool = True) -> List[Dict[str, Any]]:
        """
        Generate ad copy variations.

        Session 653 COMPOSABILITY FIX: Now uses ContentWriterAgent instead of templates!
        """
        if use_agent:
            try:
                from core.agent_router import AgentRouter
                router = AgentRouter()

                agent_class = router.AGENT_MAP.get('ContentWriterAgent')
                if agent_class:
                    agent = agent_class(user=self.user)
                    task = f"""Write 5 compelling ad copy variations for a marketing campaign:

Product: {campaign.product_name}
Description: {campaign.product_description}
Target Market: {campaign.target_market}
Location: {campaign.target_location or 'global'}
Trending Topics: {', '.join(trends[:5]) if trends else 'none'}

For each ad copy, provide:
1. The ad text (compelling, concise)
2. A variant letter (A, B, C, D, E)
3. The tone (professional, casual, urgent, emotional, etc.)
4. Key keywords used

Format: Return 5 distinct ad variations with different angles (benefit-focused, urgency, social proof, question-based, direct)."""

                    # Session 895: Add timeout to prevent coordinator hangs
                    def execute_agent():
                        return agent.execute(
                            task=task,
                            context={'campaign_id': str(campaign.id), 'phase': 'creation'},
                            scifi_context={},
                            spider_context={'trends': trends}
                        )

                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(execute_agent)
                        result = future.result(timeout=SUB_AGENT_TIMEOUT)

                    # Parse agent response into structured format
                    if result.success and result.message:
                        logger.info(f"✅ ContentWriterAgent generated ad copies for campaign {campaign.id}")
                        return self._parse_ad_copies_from_agent(result.message, trends)

            except FuturesTimeoutError:
                logger.warning(f"⏰ ContentWriterAgent timed out after {SUB_AGENT_TIMEOUT}s for ad copies")
            except Exception as e:
                logger.warning(f"Agent-based ad copy generation failed, falling back to templates: {e}")

        # Fallback to template-based generation
        base_copies = []
        templates = [
            f"Discover {campaign.product_name} - {campaign.product_description[:100]}. {campaign.target_market} love it!",
            f"Looking for the best {campaign.product_name}? We've got you covered. Contact us today!",
            f"Special offer on {campaign.product_name}! Don't miss out. Perfect for {campaign.target_market}.",
            f"{campaign.product_name} - Quality you can trust. Serving {campaign.target_location or 'your area'}.",
            f"Why choose {campaign.product_name}? {campaign.product_description[:80]}. Get yours now!"
        ]

        for i, template in enumerate(templates):
            base_copies.append({
                'text': template,
                'variant': chr(65 + i),
                'tone': 'professional',
                'keywords': trends[:3] if trends else [],
                'generated_by': 'template'
            })

        return base_copies

    def _parse_ad_copies_from_agent(self, agent_response: str, trends: List[str]) -> List[Dict[str, Any]]:
        """Parse ContentWriterAgent response into structured ad copies."""
        copies = []
        # Split by variant markers or numbered sections
        sections = agent_response.split('\n\n')

        for i, section in enumerate(sections[:5]):
            if section.strip():
                copies.append({
                    'text': section.strip()[:500],  # Limit length
                    'variant': chr(65 + i),
                    'tone': 'professional',
                    'keywords': trends[:3] if trends else [],
                    'generated_by': 'ContentWriterAgent'
                })

        # Ensure we have at least 5 copies
        while len(copies) < 5:
            copies.append({
                'text': f"Discover quality with our product. Contact us today!",
                'variant': chr(65 + len(copies)),
                'tone': 'professional',
                'keywords': trends[:3] if trends else [],
                'generated_by': 'fallback'
            })

        return copies[:5]

    def _generate_social_posts(self, campaign, trends: List[str], use_agent: bool = True) -> Dict[str, List[str]]:
        """
        Generate social media posts for each platform.

        Session 653 COMPOSABILITY FIX: Now uses SocialMediaAgent instead of templates!
        """
        if use_agent:
            try:
                from core.agent_router import AgentRouter
                router = AgentRouter()

                agent_class = router.AGENT_MAP.get('SocialMediaAgent')
                if agent_class:
                    agent = agent_class(user=self.user)
                    task = f"""Create social media posts for a marketing campaign:

Product: {campaign.product_name}
Description: {campaign.product_description}
Target Market: {campaign.target_market}
Trending Topics: {', '.join(trends[:5]) if trends else 'none'}

Create posts for each platform:
1. FACEBOOK (2 posts): Longer form, engaging, with call-to-action
2. INSTAGRAM (2 posts): Visual-focused captions with relevant hashtags
3. TWITTER (2 posts): Short, punchy, under 280 characters

Label each post clearly with the platform name."""

                    # Session 895: Add timeout to prevent coordinator hangs
                    def execute_agent():
                        return agent.execute(
                            task=task,
                            context={'campaign_id': str(campaign.id), 'phase': 'creation'},
                            scifi_context={},
                            spider_context={'trends': trends}
                        )

                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(execute_agent)
                        result = future.result(timeout=SUB_AGENT_TIMEOUT)

                    if result.success and result.message:
                        logger.info(f"✅ SocialMediaAgent generated posts for campaign {campaign.id}")
                        return self._parse_social_posts_from_agent(result.message, campaign, trends)

            except FuturesTimeoutError:
                logger.warning(f"⏰ SocialMediaAgent timed out after {SUB_AGENT_TIMEOUT}s for social posts")
            except Exception as e:
                logger.warning(f"Agent-based social post generation failed, falling back to templates: {e}")

        # Fallback to template-based generation
        posts = {
            'facebook': [],
            'instagram': [],
            'twitter': []
        }

        posts['facebook'] = [
            f"Introducing {campaign.product_name}! {campaign.product_description[:200]}...\n\nPerfect for {campaign.target_market}. Learn more!",
            f"Check out what our customers are saying about {campaign.product_name}! Contact us today.",
        ]

        hashtags = ' '.join([f"#{t.replace(' ', '')}" for t in trends[:5]]) if trends else '#sale #new'
        posts['instagram'] = [
            f"{campaign.product_name} - Available now!\n\n{hashtags}",
            f"Your next favorite {campaign.product_name} is here.\n\n{hashtags}",
        ]

        posts['twitter'] = [
            f"New: {campaign.product_name}! {campaign.product_description[:80]}... #new",
            f"Looking for {campaign.product_name}? We've got you! Contact us today.",
        ]

        return posts

    def _parse_social_posts_from_agent(self, agent_response: str, campaign, trends: List[str]) -> Dict[str, List[str]]:
        """Parse SocialMediaAgent response into structured posts."""
        posts = {'facebook': [], 'instagram': [], 'twitter': []}
        response_lower = agent_response.lower()

        # Try to extract platform-specific sections
        for platform in ['facebook', 'instagram', 'twitter']:
            if platform in response_lower:
                # Find content after platform name
                start_idx = response_lower.find(platform)
                # Find next platform or end
                next_platforms = [response_lower.find(p, start_idx + len(platform)) for p in ['facebook', 'instagram', 'twitter'] if response_lower.find(p, start_idx + len(platform)) > 0]
                end_idx = min(next_platforms) if next_platforms else len(agent_response)

                section = agent_response[start_idx:end_idx]
                # Extract lines that look like posts
                lines = [l.strip() for l in section.split('\n') if l.strip() and len(l.strip()) > 20 and platform not in l.lower()[:20]]
                posts[platform] = lines[:2]

        # Ensure each platform has at least 2 posts (fallback)
        hashtags = ' '.join([f"#{t.replace(' ', '')}" for t in trends[:5]]) if trends else '#new'
        defaults = {
            'facebook': [f"{campaign.product_name} - Perfect for {campaign.target_market}!"],
            'instagram': [f"{campaign.product_name} is here! {hashtags}"],
            'twitter': [f"Check out {campaign.product_name}! #new"]
        }

        for platform in posts:
            while len(posts[platform]) < 2:
                posts[platform].append(defaults[platform][0] if defaults[platform] else f"Great {platform} post!")

        return posts

    def _generate_email_sequence(self, campaign, use_agent: bool = True) -> List[Dict[str, str]]:
        """
        Generate a 5-email nurture sequence.

        Session 653 COMPOSABILITY FIX: Now uses ContentWriterAgent instead of templates!
        """
        if use_agent:
            try:
                from core.agent_router import AgentRouter
                router = AgentRouter()

                agent_class = router.AGENT_MAP.get('ContentWriterAgent')
                if agent_class:
                    agent = agent_class(user=self.user)
                    task = f"""Write a 5-email nurture sequence for a marketing campaign:

Product: {campaign.product_name}
Description: {campaign.product_description}
Target Market: {campaign.target_market}

Create 5 emails with this flow:
1. INTRODUCTION: Welcome and introduce the product
2. VALUE: Explain why the product is right for them
3. OFFER: Present a special offer or discount
4. URGENCY: Last chance reminder
5. FOLLOW-UP: Thank you and stay in touch

For each email provide:
- Subject line (compelling, under 60 chars)
- Body (personalized, with greeting and sign-off)

Label each email clearly (Email 1, Email 2, etc.)."""

                    # Session 895: Add timeout to prevent coordinator hangs
                    def execute_agent():
                        return agent.execute(
                            task=task,
                            context={'campaign_id': str(campaign.id), 'phase': 'creation'},
                            scifi_context=getattr(self, '_current_scifi_context', {}),
                            spider_context=getattr(self, '_current_spider_context', {})
                        )

                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(execute_agent)
                        result = future.result(timeout=SUB_AGENT_TIMEOUT)

                    if result.success and result.message:
                        logger.info(f"✅ ContentWriterAgent generated email sequence for campaign {campaign.id}")
                        return self._parse_emails_from_agent(result.message, campaign)

            except FuturesTimeoutError:
                logger.warning(f"⏰ ContentWriterAgent timed out after {SUB_AGENT_TIMEOUT}s for email sequence")
            except Exception as e:
                logger.warning(f"Agent-based email generation failed, falling back to templates: {e}")

        # Fallback to template-based generation
        emails = [
            {
                'subject': f"Introducing {campaign.product_name}",
                'body': f"Hi there,\n\nWe're excited to introduce {campaign.product_name}.\n\n{campaign.product_description}\n\nPerfect for {campaign.target_market}.\n\nLearn more by replying to this email!\n\nBest regards",
                'generated_by': 'template'
            },
            {
                'subject': f"Why {campaign.product_name} is right for you",
                'body': f"Hi,\n\nStill thinking about {campaign.product_name}?\n\nHere's why customers love it:\n- Quality you can trust\n- Perfect for {campaign.target_market}\n- Great value\n\nReply to learn more!\n\nBest",
                'generated_by': 'template'
            },
            {
                'subject': f"Special offer on {campaign.product_name}",
                'body': f"Hi,\n\nFor a limited time, we're offering a special deal on {campaign.product_name}.\n\nDon't miss out - reply now to claim your offer!\n\nBest",
                'generated_by': 'template'
            },
            {
                'subject': f"Last chance - {campaign.product_name}",
                'body': f"Hi,\n\nThis is your last chance to take advantage of our special offer on {campaign.product_name}.\n\nReply today!\n\nBest",
                'generated_by': 'template'
            },
            {
                'subject': f"Thank you for your interest in {campaign.product_name}",
                'body': f"Hi,\n\nThank you for your interest in {campaign.product_name}.\n\nWe're here whenever you're ready. Just reply to this email with any questions.\n\nBest regards",
                'generated_by': 'template'
            }
        ]

        return emails

    def _parse_emails_from_agent(self, agent_response: str, campaign) -> List[Dict[str, str]]:
        """Parse ContentWriterAgent response into structured emails."""
        emails = []
        response = agent_response

        # Try to split by email markers
        for i in range(1, 6):
            markers = [f"Email {i}", f"EMAIL {i}", f"{i}.", f"#{i}"]
            for marker in markers:
                if marker in response:
                    start_idx = response.find(marker)
                    # Find next email marker or end
                    next_starts = []
                    for j in range(i + 1, 7):
                        for next_marker in [f"Email {j}", f"EMAIL {j}", f"{j}.", f"#{j}"]:
                            idx = response.find(next_marker, start_idx + len(marker))
                            if idx > 0:
                                next_starts.append(idx)
                    end_idx = min(next_starts) if next_starts else len(response)

                    section = response[start_idx:end_idx]

                    # Try to extract subject and body
                    subject = f"{campaign.product_name} - Email {i}"
                    body = section

                    if 'subject' in section.lower():
                        subj_idx = section.lower().find('subject')
                        subj_end = section.find('\n', subj_idx)
                        if subj_end > subj_idx:
                            subject = section[subj_idx:subj_end].replace('Subject:', '').replace('subject:', '').strip()[:60]

                    emails.append({
                        'subject': subject,
                        'body': section[:1000],
                        'generated_by': 'ContentWriterAgent'
                    })
                    break

        # Ensure we have 5 emails
        while len(emails) < 5:
            emails.append({
                'subject': f"{campaign.product_name} - Update {len(emails) + 1}",
                'body': f"Hi,\n\nThank you for your interest in {campaign.product_name}.\n\nBest regards",
                'generated_by': 'fallback'
            })

        return emails[:5]


# Factory function for convenience
def get_campaign_orchestrator_agent(user=None) -> CampaignOrchestratorAgent:
    """Get a CampaignOrchestratorAgent instance."""
    return CampaignOrchestratorAgent(user=user)
