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

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


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

                    result = AgentResult(
                        success=True,
                        message=f"Campaign orchestration completed with {len(all_results)} actions",
                        data={
                            'results': all_results,
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
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
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

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

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

    def _generate_ad_copies(self, campaign, trends: List[str]) -> List[Dict[str, Any]]:
        """Generate ad copy variations."""
        # In a full implementation, this would call ContentWriterAgent
        # For now, generate template-based variations

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
                'variant': chr(65 + i),  # A, B, C, D, E
                'tone': 'professional',
                'keywords': trends[:3] if trends else []
            })

        return base_copies

    def _generate_social_posts(self, campaign, trends: List[str]) -> Dict[str, List[str]]:
        """Generate social media posts for each platform."""
        posts = {
            'facebook': [],
            'instagram': [],
            'twitter': []
        }

        # Facebook posts (longer form)
        posts['facebook'] = [
            f"Introducing {campaign.product_name}! {campaign.product_description[:200]}...\n\nPerfect for {campaign.target_market}. Learn more!",
            f"Check out what our customers are saying about {campaign.product_name}! Contact us today.",
        ]

        # Instagram posts (visual-focused captions)
        hashtags = ' '.join([f"#{t.replace(' ', '')}" for t in trends[:5]]) if trends else '#sale #new'
        posts['instagram'] = [
            f"{campaign.product_name} - Available now!\n\n{hashtags}",
            f"Your next favorite {campaign.product_name} is here.\n\n{hashtags}",
        ]

        # Twitter posts (short and punchy)
        posts['twitter'] = [
            f"New: {campaign.product_name}! {campaign.product_description[:80]}... #new",
            f"Looking for {campaign.product_name}? We've got you! Contact us today.",
        ]

        return posts

    def _generate_email_sequence(self, campaign) -> List[Dict[str, str]]:
        """Generate a 5-email sequence."""
        emails = [
            {
                'subject': f"Introducing {campaign.product_name}",
                'body': f"Hi there,\n\nWe're excited to introduce {campaign.product_name}.\n\n{campaign.product_description}\n\nPerfect for {campaign.target_market}.\n\nLearn more by replying to this email!\n\nBest regards"
            },
            {
                'subject': f"Why {campaign.product_name} is right for you",
                'body': f"Hi,\n\nStill thinking about {campaign.product_name}?\n\nHere's why customers love it:\n- Quality you can trust\n- Perfect for {campaign.target_market}\n- Great value\n\nReply to learn more!\n\nBest"
            },
            {
                'subject': f"Special offer on {campaign.product_name}",
                'body': f"Hi,\n\nFor a limited time, we're offering a special deal on {campaign.product_name}.\n\nDon't miss out - reply now to claim your offer!\n\nBest"
            },
            {
                'subject': f"Last chance - {campaign.product_name}",
                'body': f"Hi,\n\nThis is your last chance to take advantage of our special offer on {campaign.product_name}.\n\nReply today!\n\nBest"
            },
            {
                'subject': f"Thank you for your interest in {campaign.product_name}",
                'body': f"Hi,\n\nThank you for your interest in {campaign.product_name}.\n\nWe're here whenever you're ready. Just reply to this email with any questions.\n\nBest regards"
            }
        ]

        return emails


# Factory function for convenience
def get_campaign_orchestrator_agent(user=None) -> CampaignOrchestratorAgent:
    """Get a CampaignOrchestratorAgent instance."""
    return CampaignOrchestratorAgent(user=user)
