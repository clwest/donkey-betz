"""
Income Builder Spider Orchestrator
Connects the spider network to Income Builder for real-time opportunity discovery
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from intelligence.spider_opportunity_connector import spider_connector, SpiderOpportunity
from ai_core.spiders.freelance_opportunity_spider import FreelanceOpportunitySpider
from intelligence.income_builder import AIIncomeBuilder, UserProfile

logger = logging.getLogger(__name__)


@dataclass
class OpportunityDiscoveryResult:
    """Result of opportunity discovery"""
    opportunities: List[SpiderOpportunity]
    spider_sources: List[str]
    discovery_time: float
    total_found: int
    filtered_count: int
    user_profile: Dict


class IncomeSpiderOrchestrator:
    """
    Orchestrates spider network to discover income opportunities for Income Builder

    This is the missing link that connects:
    1. Spider Network (real data gathering)
    2. Income Builder (user matching & analysis)
    3. Agent System (intelligent processing)
    """

    def __init__(self):
        self.income_builder = AIIncomeBuilder()
        self.freelance_spider = FreelanceOpportunitySpider()
        self.active_spiders = []
        self.opportunity_cache = {}
        self.last_fetch_time = None

    async def discover_opportunities_for_user(
        self,
        user_profile: UserProfile,
        use_real_data: bool = True,
        max_opportunities: int = 20
    ) -> OpportunityDiscoveryResult:
        """
        Main orchestration method - discovers opportunities from spider network

        Args:
            user_profile: User profile with skills and preferences
            use_real_data: If True, fetches from real APIs (HackerNews, RemoteOK, etc.)
            max_opportunities: Maximum opportunities to return

        Returns:
            OpportunityDiscoveryResult with discovered opportunities
        """
        start_time = datetime.now()
        logger.info(f"🕷️ Starting opportunity discovery for user {user_profile.id}")
        logger.info(f"   Skills: {', '.join(user_profile.skills[:5])}")
        logger.info(f"   Experience: {user_profile.skill_level.value}")
        logger.info(f"   Use real data: {use_real_data}")

        all_opportunities = []
        spider_sources = []

        try:
            # Step 1: Initialize freelance spider
            await self.freelance_spider.initialize()

            # Step 2: Fetch opportunities from spider network
            logger.info("🔍 Fetching opportunities from spider network...")

            # Get opportunities from Freelance Spider (real APIs)
            freelance_opps = await self.freelance_spider.find_opportunities(
                use_real_data=use_real_data
            )

            logger.info(f"   Found {len(freelance_opps)} opportunities from freelance spider")

            # Convert FreelanceOpportunity to SpiderOpportunity format
            for opp in freelance_opps:
                spider_opp = self._convert_to_spider_opportunity(opp)
                all_opportunities.append(spider_opp)

            spider_sources.append('freelance_spider')

            # Step 3: Try to get additional opportunities from spider connector (Redis)
            try:
                user_profile_dict = {
                    'skills': user_profile.skills,
                    'skillLevel': user_profile.skill_level.value,
                    'availableHours': user_profile.available_hours_per_week,
                    'currentBalance': user_profile.current_balance
                }

                redis_opps = await spider_connector.get_opportunities_for_user(user_profile_dict)
                logger.info(f"   Found {len(redis_opps)} opportunities from Redis connector")

                all_opportunities.extend(redis_opps)
                spider_sources.append('redis_connector')

            except Exception as e:
                logger.warning(f"Redis connector not available: {e}")

            # Step 4: Filter and score opportunities using Income Builder
            logger.info(f"📊 Scoring {len(all_opportunities)} opportunities...")

            scored_opportunities = await self._score_opportunities_with_ml(
                all_opportunities,
                user_profile
            )

            # Step 5: Sort by score and limit
            scored_opportunities.sort(key=lambda x: x.quality_score, reverse=True)
            filtered_opportunities = scored_opportunities[:max_opportunities]

            # Step 6: Clean up
            await self.freelance_spider.cleanup()

            discovery_time = (datetime.now() - start_time).total_seconds()

            result = OpportunityDiscoveryResult(
                opportunities=filtered_opportunities,
                spider_sources=spider_sources,
                discovery_time=discovery_time,
                total_found=len(all_opportunities),
                filtered_count=len(filtered_opportunities),
                user_profile=user_profile_dict
            )

            logger.info(f"✅ Discovery complete in {discovery_time:.2f}s")
            logger.info(f"   Total found: {result.total_found}")
            logger.info(f"   After filtering: {result.filtered_count}")
            logger.info(f"   Sources: {', '.join(spider_sources)}")

            return result

        except Exception as e:
            logger.error(f"❌ Opportunity discovery failed: {e}", exc_info=True)

            # Return empty result on failure
            return OpportunityDiscoveryResult(
                opportunities=[],
                spider_sources=[],
                discovery_time=(datetime.now() - start_time).total_seconds(),
                total_found=0,
                filtered_count=0,
                user_profile={}
            )

    def _convert_to_spider_opportunity(self, freelance_opp) -> SpiderOpportunity:
        """Convert FreelanceOpportunity to SpiderOpportunity format"""
        return SpiderOpportunity(
            id=freelance_opp.job_id,
            title=freelance_opp.title,
            description=freelance_opp.description,
            platform=freelance_opp.platform,
            opportunity_type='freelance',
            budget_min=freelance_opp.budget if freelance_opp.budget else None,
            budget_max=freelance_opp.budget if freelance_opp.budget else None,
            skills_required=freelance_opp.skills_required,
            experience_level=self._map_difficulty_to_experience(
                freelance_opp.confidence_score
            ),
            deadline=freelance_opp.deadline,
            urgency='high' if freelance_opp.agent_suitability > 0.8 else 'medium',
            quality_score=freelance_opp.agent_suitability,
            competition_level='low' if freelance_opp.agent_suitability > 0.7 else 'medium',
            client_rating=freelance_opp.client_rating,
            spider_source='freelance_opportunity_spider',
            discovered_at=datetime.now(),
            raw_data={
                'recommended_agents': freelance_opp.recommended_agents,
                'estimated_completion_time': freelance_opp.estimated_completion_time,
                'confidence_score': freelance_opp.confidence_score
            }
        )

    def _map_difficulty_to_experience(self, confidence_score: float) -> str:
        """Map confidence score to experience level"""
        if confidence_score >= 0.8:
            return 'beginner'
        elif confidence_score >= 0.6:
            return 'intermediate'
        else:
            return 'advanced'

    async def _score_opportunities_with_ml(
        self,
        opportunities: List[SpiderOpportunity],
        user_profile: UserProfile
    ) -> List[SpiderOpportunity]:
        """Score opportunities using Income Builder's ML pipeline"""
        scored_opportunities = []

        for opp in opportunities:
            try:
                # Prepare data for ML scoring
                user_dict = {
                    'current_balance': user_profile.current_balance,
                    'skills': user_profile.skills,
                    'skill_level': user_profile.skill_level,
                    'available_hours_per_week': user_profile.available_hours_per_week,
                    'total_earned': user_profile.total_earned,
                    'reputation_score': user_profile.reputation_score
                }

                opp_dict = {
                    'title': opp.title,
                    'description': opp.description,
                    'skills_required': opp.skills_required,
                    'initial_investment': 0,  # Most freelance opps are zero investment
                    'success_rate': opp.quality_score,
                    'market_demand': 0.8,  # High demand if from real APIs
                    'competition_level': 0.5 if opp.competition_level == 'medium' else 0.3,
                    'scalability': 0.7,
                    'budget': opp.budget_min or 0,
                    'client_rating': opp.client_rating or 4.0,
                    'platform': opp.platform,
                    'difficulty': opp.experience_level
                }

                # Get ML score from Income Builder
                ml_result = await self.income_builder.ml_pipeline.predict_opportunity_fit(
                    user_dict,
                    opp_dict
                )

                # Update opportunity score with ML prediction
                ml_score = ml_result.get('fit_score', opp.quality_score)

                # Combine original score with ML score (weighted average)
                combined_score = (opp.quality_score * 0.3) + (ml_score * 0.7)
                opp.quality_score = combined_score

                # Add ML metadata to raw_data
                if opp.raw_data is None:
                    opp.raw_data = {}
                opp.raw_data['ml_score'] = ml_score
                opp.raw_data['ml_confidence'] = ml_result.get('confidence', 0.8)
                opp.raw_data['ml_engine'] = ml_result.get('ml_engine', 'unknown')

                scored_opportunities.append(opp)

            except Exception as e:
                logger.warning(f"Failed to score opportunity {opp.id}: {e}")
                # Keep original score if ML scoring fails
                scored_opportunities.append(opp)

        return scored_opportunities

    async def create_income_pipeline(
        self,
        user_profile: UserProfile,
        opportunities: List[SpiderOpportunity]
    ) -> Dict[str, Any]:
        """
        Create complete income pipeline: discovery → analysis → action plan

        This integrates:
        1. Spider discovery (real data)
        2. ML scoring (intelligent matching)
        3. Agent analysis (deep insights)
        4. Action plan generation (practical steps)
        """
        logger.info(f"🏗️ Creating income pipeline for {len(opportunities)} opportunities")

        pipeline_result = {
            'user_id': user_profile.id,
            'opportunities': [],
            'top_opportunity': None,
            'action_plan': None,
            'agent_insights': [],
            'created_at': datetime.now().isoformat()
        }

        try:
            # Step 1: Convert opportunities to Income Builder format
            for opp in opportunities[:5]:  # Top 5
                opportunity_data = {
                    'id': opp.id,
                    'title': opp.title,
                    'description': opp.description,
                    'platform': opp.platform,
                    'budget': opp.budget_min,
                    'skills_required': opp.skills_required,
                    'quality_score': opp.quality_score,
                    'url': opp.raw_data.get('url') if opp.raw_data else None,
                    'ml_score': opp.raw_data.get('ml_score') if opp.raw_data else None
                }

                pipeline_result['opportunities'].append(opportunity_data)

            # Step 2: Use agents to analyze top opportunity
            if opportunities:
                top_opp = opportunities[0]
                pipeline_result['top_opportunity'] = {
                    'id': top_opp.id,
                    'title': top_opp.title,
                    'score': top_opp.quality_score,
                    'budget': top_opp.budget_min,
                    'platform': top_opp.platform
                }

                # Step 3: Get agent insights
                try:
                    agent_opportunities = await self.income_builder.discover_opportunities_with_agents(
                        user_profile,
                        domains=[top_opp.platform]
                    )

                    pipeline_result['agent_insights'] = agent_opportunities[:3]
                    logger.info(f"   Got {len(agent_opportunities)} agent insights")

                except Exception as e:
                    logger.warning(f"Agent analysis failed: {e}")

            # Step 4: Generate action plan for top opportunity
            if opportunities:
                # Find matching Income Builder opportunity or create custom one
                # For now, use the content_writing opportunity as template
                action_plan = await self.income_builder.create_action_plan(
                    user_id=user_profile.id,
                    selected_opportunity='content_writing'  # Default template
                )

                # Customize action plan with real opportunity data
                top_opp = opportunities[0]
                action_plan['real_opportunity'] = {
                    'title': top_opp.title,
                    'platform': top_opp.platform,
                    'budget': top_opp.budget_min,
                    'url': top_opp.raw_data.get('url') if top_opp.raw_data else None,
                    'skills_required': top_opp.skills_required
                }

                pipeline_result['action_plan'] = action_plan
                logger.info(f"   Generated action plan with {len(action_plan.get('files_created', []))} files")

            logger.info(f"✅ Income pipeline created successfully")

        except Exception as e:
            logger.error(f"❌ Income pipeline creation failed: {e}", exc_info=True)
            pipeline_result['error'] = str(e)

        return pipeline_result

    async def start_continuous_discovery(
        self,
        user_profile: UserProfile,
        interval_minutes: int = 30
    ):
        """
        Start continuous opportunity discovery for a user
        Runs in background, updating opportunities every N minutes
        """
        logger.info(f"🔄 Starting continuous discovery for user {user_profile.id}")
        logger.info(f"   Interval: {interval_minutes} minutes")

        while True:
            try:
                # Discover opportunities
                result = await self.discover_opportunities_for_user(
                    user_profile,
                    use_real_data=True,
                    max_opportunities=20
                )

                # Store in cache
                self.opportunity_cache[user_profile.id] = {
                    'opportunities': result.opportunities,
                    'last_updated': datetime.now(),
                    'sources': result.spider_sources
                }

                logger.info(f"✅ Cached {len(result.opportunities)} opportunities for {user_profile.id}")

                # Wait for next cycle
                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                logger.error(f"❌ Continuous discovery error: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)

    def get_cached_opportunities(self, user_id: str) -> Optional[List[SpiderOpportunity]]:
        """Get cached opportunities for a user"""
        cache_entry = self.opportunity_cache.get(user_id)

        if cache_entry:
            # Check if cache is still valid (< 1 hour old)
            if datetime.now() - cache_entry['last_updated'] < timedelta(hours=1):
                return cache_entry['opportunities']

        return None


# Global orchestrator instance
income_spider_orchestrator = IncomeSpiderOrchestrator()


# Convenience functions for easy integration

async def get_opportunities_for_user(user_profile: UserProfile, use_real_data: bool = True) -> List[SpiderOpportunity]:
    """
    Simple function to get opportunities for a user

    Usage:
        from intelligence.income_spider_orchestrator import get_opportunities_for_user

        opportunities = await get_opportunities_for_user(user_profile, use_real_data=True)
    """
    result = await income_spider_orchestrator.discover_opportunities_for_user(
        user_profile,
        use_real_data=use_real_data
    )

    return result.opportunities


async def create_complete_income_plan(user_profile: UserProfile, use_real_data: bool = True) -> Dict[str, Any]:
    """
    Create complete income plan: spider discovery + ML analysis + agent insights + action plan

    Usage:
        from intelligence.income_spider_orchestrator import create_complete_income_plan

        plan = await create_complete_income_plan(user_profile, use_real_data=True)
    """
    # Step 1: Discover opportunities
    result = await income_spider_orchestrator.discover_opportunities_for_user(
        user_profile,
        use_real_data=use_real_data
    )

    # Step 2: Create pipeline with discovered opportunities
    pipeline = await income_spider_orchestrator.create_income_pipeline(
        user_profile,
        result.opportunities
    )

    # Add discovery metadata
    pipeline['discovery_metadata'] = {
        'sources': result.spider_sources,
        'discovery_time': result.discovery_time,
        'total_found': result.total_found,
        'filtered_count': result.filtered_count
    }

    return pipeline