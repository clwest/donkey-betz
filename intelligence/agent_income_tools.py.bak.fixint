"""
Agent Income Tools
Gives agents access to Income Builder and Content Creation Studio
so they can actually BUILD income opportunities, not just discover them!
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentIncomeTools:
    """
    Tools that agents can use to build income opportunities

    This bridges the gap between:
    1. Agent discovery (finding opportunities)
    2. Agent execution (actually building the deliverables)
    """

    def __init__(self):
        self.income_builder = None
        self.content_studio = None
        self.initialized = False

    async def initialize(self):
        """Initialize connections to Income Builder and Content Studio"""
        if self.initialized:
            return True

        try:
            # Import Income Builder
            from intelligence.income_builder import income_builder
            self.income_builder = income_builder
            logger.info("✅ Connected to Income Builder")

            # SESSION 30: Import Content Studio
            try:
                from intelligence.content_creation_studio import content_studio
                self.content_studio = content_studio
                logger.info("✅ Connected to Content Creation Studio")
            except Exception as e:
                logger.warning(f"Content Studio not available: {e}")
                self.content_studio = None

            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize agent income tools: {e}")
            return False

    async def analyze_opportunity(
        self,
        opportunity_data: Dict[str, Any],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Tool: Analyze an income opportunity

        Args:
            opportunity_data: Opportunity details (title, description, budget, etc.)
            user_context: Optional user context for personalization

        Returns:
            Analysis with success probability, approach, and action steps
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"🔍 Agent analyzing opportunity: {opportunity_data.get('title')}")

        try:
            analysis = await self.income_builder.analyze_external_opportunity(
                opportunity_data
            )

            logger.info(f"   Success probability: {analysis.get('success_probability', 0):.2f}")
            logger.info(f"   Recommended approach: {analysis.get('recommended_approach')}")

            return {
                'success': True,
                'analysis': analysis,
                'tool': 'analyze_opportunity',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Opportunity analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': 'analyze_opportunity'
            }

    async def generate_proposal(
        self,
        opportunity_data: Dict[str, Any],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Tool: Generate a proposal for an opportunity

        Args:
            opportunity_data: Opportunity details
            user_context: Optional user context

        Returns:
            Generated proposal with content, pricing, and submission strategy
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"📝 Agent generating proposal for: {opportunity_data.get('title')}")

        try:
            proposal = await self.income_builder.generate_real_time_proposal(
                opportunity_data,
                user_context
            )

            logger.info(f"   Proposal generated")
            logger.info(f"   Estimated win rate: {proposal.get('estimated_win_rate', 0):.2f}")
            logger.info(f"   Revenue potential: ${proposal.get('revenue_potential', {}).get('expected_value', 0):.2f}")

            return {
                'success': True,
                'proposal': proposal,
                'tool': 'generate_proposal',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Proposal generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': 'generate_proposal'
            }

    async def create_content(
        self,
        content_type: str,
        specifications: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Tool: Create content for an opportunity

        Args:
            content_type: Type of content (article, blog, code, design, etc.)
            specifications: Content specifications (length, tone, keywords, etc.)
            context: Additional context

        Returns:
            Generated content
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"✍️ Agent creating {content_type} content")

        try:
            # SESSION 30: Use Content Creation Studio!
            if self.content_studio:
                from intelligence.content_creation_studio import ContentSpecification, ContentType, ContentQuality

                # Map string content type to enum
                content_type_map = {
                    'article': ContentType.ARTICLE,
                    'blog': ContentType.BLOG_POST,
                    'blog_post': ContentType.BLOG_POST,
                    'code': ContentType.CODE,
                    'design': ContentType.DESIGN,
                    'video_script': ContentType.VIDEO_SCRIPT,
                    'social_media': ContentType.SOCIAL_MEDIA,
                    'email_campaign': ContentType.EMAIL_CAMPAIGN,
                    'product_description': ContentType.PRODUCT_DESCRIPTION,
                    'technical_docs': ContentType.TECHNICAL_DOCUMENTATION,
                    'presentation': ContentType.PRESENTATION
                }

                content_type_enum = content_type_map.get(content_type.lower(), ContentType.ARTICLE)

                # Create specification
                spec = ContentSpecification(
                    content_type=content_type_enum,
                    title=specifications.get('title', 'Untitled'),
                    topic=specifications.get('topic', ''),
                    keywords=specifications.get('keywords', []),
                    target_audience=specifications.get('target_audience', 'general'),
                    word_count=specifications.get('word_count'),
                    tone=specifications.get('tone', 'professional'),
                    quality_level=ContentQuality.STANDARD,
                    special_requirements=specifications.get('special_requirements'),
                    reference_materials=specifications.get('reference_materials')
                )

                # Generate content using Content Studio
                result = await self.content_studio.generate_content(spec)

                logger.info(f"   ✅ Created {result.word_count} words")
                logger.info(f"   Quality score: {result.quality_score:.2f}")
                logger.info(f"   Estimated value: ${result.estimated_value}")

                return {
                    'success': True,
                    'content': result.content,
                    'content_type': content_type,
                    'word_count': result.word_count,
                    'quality_score': result.quality_score,
                    'estimated_value': result.estimated_value,
                    'metadata': result.metadata,
                    'tool': 'create_content',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Fallback to AI generation through Income Builder
                logger.warning("⚠️ Content Studio not available, using fallback")
                prompt = f"""Create {content_type} content with the following specifications:

                {specifications}

                Additional context: {context if context else 'None'}
                """

                content = await self.income_builder.generate_ai_content(
                    prompt,
                    specifications
                )

                logger.info(f"   Content created: {len(str(content))} characters")

                return {
                    'success': True,
                    'content': content,
                    'content_type': content_type,
                    'tool': 'create_content',
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'tool': 'create_content'
            }

    async def build_portfolio_item(
        self,
        opportunity_data: Dict[str, Any],
        user_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Tool: Build a portfolio item that matches an opportunity

        Args:
            opportunity_data: Opportunity details
            user_skills: User's skills

        Returns:
            Portfolio item details and files created
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"🎨 Agent building portfolio item for: {opportunity_data.get('title')}")

        try:
            from intelligence.income_builder import UserProfile, SkillLevel

            # Create temporary user profile
            user_profile = UserProfile(
                id='agent_portfolio_builder',
                skills=user_skills,
                skill_level=SkillLevel.INTERMEDIATE
            )

            # Generate portfolio files
            opportunities_list = [{
                'opportunity': opportunity_data,
                'score': 0.8
            }]

            files_created = await self.income_builder.generate_portfolio_files(
                user_profile,
                opportunities_list
            )

            logger.info(f"   Portfolio item created: {len(files_created)} files")

            return {
                'success': True,
                'files_created': files_created,
                'portfolio_item': opportunity_data.get('title'),
                'tool': 'build_portfolio_item',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Portfolio building failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': 'build_portfolio_item'
            }

    async def create_action_plan(
        self,
        opportunity_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Tool: Create detailed action plan for an opportunity

        Args:
            opportunity_id: ID of the opportunity
            user_id: User ID

        Returns:
            Action plan with weekly tasks, metrics, and files
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"📋 Agent creating action plan for opportunity: {opportunity_id}")

        try:
            action_plan = await self.income_builder.create_action_plan(
                user_id,
                opportunity_id
            )

            logger.info(f"   Action plan created")
            logger.info(f"   Files: {len(action_plan.get('files_created', []))}")

            return {
                'success': True,
                'action_plan': action_plan,
                'tool': 'create_action_plan',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Action plan creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': 'create_action_plan'
            }

    async def discover_opportunities(
        self,
        user_profile_data: Dict[str, Any],
        use_real_data: bool = True
    ) -> Dict[str, Any]:
        """
        Tool: Discover income opportunities using spider network

        Args:
            user_profile_data: User profile dict (skills, experience, etc.)
            use_real_data: Use real APIs vs mock data

        Returns:
            Discovered opportunities with analysis
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"🕷️ Agent discovering opportunities...")

        try:
            from intelligence.income_builder import UserProfile, SkillLevel

            # Convert dict to UserProfile
            user_profile = UserProfile(
                id=user_profile_data.get('id', 'agent_user'),
                skills=user_profile_data.get('skills', []),
                skill_level=SkillLevel(user_profile_data.get('skill_level', 'beginner')),
                available_hours_per_week=user_profile_data.get('available_hours', 10),
                current_balance=user_profile_data.get('current_balance', 0)
            )

            # Discover opportunities
            result = await self.income_builder.discover_opportunities_with_spiders(
                user_profile,
                use_real_data=use_real_data
            )

            logger.info(f"   Found {result.get('total_found', 0)} opportunities")

            return {
                'success': True,
                'result': result,
                'tool': 'discover_opportunities',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Opportunity discovery failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': 'discover_opportunities'
            }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools for agents"""
        return [
            {
                'name': 'analyze_opportunity',
                'description': 'Analyze an income opportunity for success probability and approach',
                'parameters': ['opportunity_data', 'user_context (optional)']
            },
            {
                'name': 'generate_proposal',
                'description': 'Generate a winning proposal for an opportunity',
                'parameters': ['opportunity_data', 'user_context (optional)']
            },
            {
                'name': 'create_content',
                'description': 'Create content (articles, code, designs) for opportunities',
                'parameters': ['content_type', 'specifications', 'context (optional)']
            },
            {
                'name': 'build_portfolio_item',
                'description': 'Build portfolio items that match opportunities',
                'parameters': ['opportunity_data', 'user_skills']
            },
            {
                'name': 'create_action_plan',
                'description': 'Create detailed action plan for pursuing an opportunity',
                'parameters': ['opportunity_id', 'user_id']
            },
            {
                'name': 'discover_opportunities',
                'description': 'Discover income opportunities from spider network',
                'parameters': ['user_profile_data', 'use_real_data (optional)']
            }
        ]


# Global instance
agent_income_tools = AgentIncomeTools()


# Convenience functions for agent integration

async def execute_agent_income_tool(
    tool_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute an income tool for an agent

    Usage (from agent code):
        from intelligence.agent_income_tools import execute_agent_income_tool

        result = await execute_agent_income_tool(
            'analyze_opportunity',
            {
                'opportunity_data': {...},
                'user_context': {...}
            }
        )
    """
    if not agent_income_tools.initialized:
        await agent_income_tools.initialize()

    tool_methods = {
        'analyze_opportunity': agent_income_tools.analyze_opportunity,
        'generate_proposal': agent_income_tools.generate_proposal,
        'create_content': agent_income_tools.create_content,
        'build_portfolio_item': agent_income_tools.build_portfolio_item,
        'create_action_plan': agent_income_tools.create_action_plan,
        'discover_opportunities': agent_income_tools.discover_opportunities,
    }

    if tool_name not in tool_methods:
        return {
            'success': False,
            'error': f"Unknown tool: {tool_name}",
            'available_tools': list(tool_methods.keys())
        }

    try:
        tool_method = tool_methods[tool_name]
        result = await tool_method(**parameters)
        return result

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'tool': tool_name
        }