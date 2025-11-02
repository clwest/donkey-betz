"""
Opportunity Storage Service
Persists spider-discovered opportunities to database for viewing and tracking
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from intelligence.models import OpportunityTracking
from intelligence.spider_opportunity_connector import SpiderOpportunity

logger = logging.getLogger(__name__)


class OpportunityStorageService:
    """
    Manages storage and retrieval of opportunities discovered by spiders
    """

    @staticmethod
    def store_opportunity(
        spider_opp: SpiderOpportunity,
        user: Optional[User] = None
    ) -> OpportunityTracking:
        """
        Store a spider-discovered opportunity in the database

        Args:
            spider_opp: SpiderOpportunity object from spider network
            user: Optional user to associate this opportunity with

        Returns:
            OpportunityTracking instance
        """
        try:
            # Create unique opportunity_id from spider data
            opportunity_id = spider_opp.id or f"{spider_opp.platform}_{spider_opp.title[:50].replace(' ', '_')}"

            # Prepare opportunity data
            opportunity_data = {
                'id': spider_opp.id,
                'title': spider_opp.title,
                'description': spider_opp.description[:500] if spider_opp.description else '',
                'platform': spider_opp.platform,
                'spider_source': spider_opp.spider_source,
                'url': spider_opp.raw_data.get('url', '#') if spider_opp.raw_data else '#',
                'budget_min': spider_opp.budget_min or 0,
                'budget_max': spider_opp.budget_max or 0,
                'skills_required': spider_opp.skills_required[:10],  # Limit to 10 skills
                'quality_score': spider_opp.quality_score,
                'experience_level': spider_opp.experience_level,
                'opportunity_type': spider_opp.opportunity_type,
                'posted_at': spider_opp.posted_at or datetime.now(),
                'deadline': spider_opp.deadline,
            }

            # Get or create opportunity tracking
            tracking, created = OpportunityTracking.objects.get_or_create(
                opportunity_id=opportunity_id[:100],  # Ensure ID fits in CharField
                defaults={
                    'user': user if user else User.objects.first(),  # Fallback to first user
                    'opportunity_title': spider_opp.title[:255],
                    'opportunity_type': spider_opp.opportunity_type or 'freelance',
                    'opportunity_data': opportunity_data,
                    'status': 'identified',
                }
            )

            if not created:
                # Update existing opportunity data
                tracking.opportunity_data = opportunity_data
                tracking.updated_at = timezone.now()
                tracking.save()

            logger.info(f"{'✅ Stored' if created else '🔄 Updated'} opportunity: {spider_opp.title[:50]}")
            return tracking

        except Exception as e:
            logger.error(f"❌ Error storing opportunity: {e}")
            return None

    @staticmethod
    def store_opportunities_batch(
        spider_opps: List[SpiderOpportunity],
        user: Optional[User] = None
    ) -> List[OpportunityTracking]:
        """
        Store multiple opportunities in a batch

        Args:
            spider_opps: List of SpiderOpportunity objects
            user: Optional user to associate opportunities with

        Returns:
            List of stored OpportunityTracking instances
        """
        stored = []

        with transaction.atomic():
            for spider_opp in spider_opps:
                tracking = OpportunityStorageService.store_opportunity(spider_opp, user)
                if tracking:
                    stored.append(tracking)

        logger.info(f"✅ Stored {len(stored)}/{len(spider_opps)} opportunities")
        return stored

    @staticmethod
    def get_opportunities_for_user(
        user: User,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve opportunities for a user

        Args:
            user: User to get opportunities for
            status: Optional status filter (identified, analyzing, etc.)
            limit: Maximum number of opportunities to return

        Returns:
            List of opportunity dictionaries formatted for frontend
        """
        query = OpportunityTracking.objects.filter(user=user)

        if status:
            query = query.filter(status=status)

        # Get recent opportunities, sorted by created date
        opportunities = query.order_by('-created_at')[:limit]

        # Format for frontend
        formatted_opps = []
        for opp in opportunities:
            opp_data = opp.opportunity_data

            quality_score = opp_data.get('quality_score', 0.75)

            # Handle posted_at datetime
            posted_at = opp_data.get('posted_at')
            if posted_at and hasattr(posted_at, 'isoformat'):
                posted_at = posted_at.isoformat()
            elif isinstance(posted_at, str):
                posted_at = posted_at  # Already string
            else:
                posted_at = None

            formatted_opp = {
                'id': opp_data.get('id', opp.opportunity_id),
                'title': opp.opportunity_title,
                'description': opp_data.get('description', '')[:200] + '...',
                'platform': opp_data.get('platform', 'Unknown'),
                'source': opp_data.get('spider_source', 'spider_network'),
                'url': opp_data.get('url', '#'),
                'budget_min': opp_data.get('budget_min', 0),
                'budget_max': opp_data.get('budget_max', 0),
                'skills': opp_data.get('skills_required', []),
                'match_score': int(quality_score * 100),
                'score': quality_score,  # Frontend expects this for success rate calculation
                'experience_level': opp_data.get('experience_level', 'intermediate'),
                'opportunity_type': opp_data.get('opportunity_type', 'freelance'),
                'status': opp.status,
                'posted_at': posted_at,
                'created_at': opp.created_at.isoformat(),

                # Frontend-specific fields
                'stream_type': opp.opportunity_type.replace('_', ' ').title(),
                'time_to_income': '1-2 weeks',
                'potential_monthly': f"${opp_data.get('budget_min', 2000)}-${opp_data.get('budget_max', 5000)}",
                'difficulty': opp_data.get('experience_level', 'intermediate'),
                'initial_investment': 0,
                'success_rate': int(quality_score * 100),
                'market_demand': 85,
                'required_skills': opp_data.get('skills_required', [])[:5],
                'match_reasons': [
                    f"Match score: {int(quality_score * 100)}%",
                    f"Platform: {opp_data.get('platform', 'Unknown')}",
                    f"Source: {opp_data.get('spider_source', 'spider_network')}"
                ],
                'action_steps': [
                    'Review opportunity details',
                    'Prepare tailored proposal',
                    'Submit application within 24 hours',
                    'Follow up if no response in 3 days'
                ],
            }

            formatted_opps.append(formatted_opp)

        logger.info(f"📤 Retrieved {len(formatted_opps)} opportunities for user {user.username}")
        return formatted_opps

    @staticmethod
    def get_all_opportunities(limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all opportunities across all users (for development/testing)

        Args:
            limit: Maximum number of opportunities to return

        Returns:
            List of opportunity dictionaries
        """
        opportunities = OpportunityTracking.objects.all().order_by('-created_at')[:limit]

        formatted_opps = []
        for opp in opportunities:
            # Use opportunity_data if available, otherwise use model fields directly
            opp_data = opp.opportunity_data if opp.opportunity_data else {}

            # Get quality score from either source
            quality_score = opp_data.get('quality_score', opp.confidence_score)

            formatted_opp = {
                'id': opp_data.get('id', opp.opportunity_id),
                'title': opp.title or opp.opportunity_title,
                'description': (opp.description or opp_data.get('description', ''))[:200],
                'platform': opp_data.get('platform', 'Direct'),
                'source': opp_data.get('spider_source', 'database'),
                'url': opp_data.get('url', '#'),
                'budget_min': opp_data.get('budget_min', int(opp.potential_revenue)),
                'budget_max': opp_data.get('budget_max', int(opp.potential_revenue * 1.5)),
                'skills': opp_data.get('skills_required', []),
                'match_score': int(opp.match_score * 100),
                'score': quality_score,  # Frontend expects this for success rate calculation
                'experience_level': opp_data.get('experience_level', 'intermediate'),
                'opportunity_type': opp_data.get('opportunity_type', opp.opportunity_type),
                'status': opp.status,
                'created_at': opp.created_at.isoformat() if opp.created_at else None,

                # Frontend formatting
                'stream_type': opp.opportunity_type.replace('_', ' ').title(),
                'time_to_income': '1-2 weeks',
                'potential_monthly': f"${int(opp.potential_revenue)}-${int(opp.potential_revenue * 1.5)}",
                'difficulty': opp_data.get('experience_level', 'intermediate'),
                'success_rate': int(opp.confidence_score * 100),
                'required_skills': opp_data.get('skills_required', [])[:5],
                'match_reasons': [
                    f"{int(quality_score * 100)}% match",
                    f"From {opp_data.get('spider_source', 'spider')}"
                ],
            }

            formatted_opps.append(formatted_opp)

        logger.info(f"📤 Retrieved {len(formatted_opps)} total opportunities")
        return formatted_opps

    @staticmethod
    def cleanup_old_opportunities(days_old: int = 30):
        """
        Remove opportunities older than specified days

        Args:
            days_old: Remove opportunities created more than this many days ago
        """
        cutoff_date = timezone.now() - timedelta(days=days_old)
        deleted_count = OpportunityTracking.objects.filter(
            created_at__lt=cutoff_date,
            status='identified'  # Only remove unactioned opportunities
        ).delete()[0]

        logger.info(f"🧹 Cleaned up {deleted_count} old opportunities")
        return deleted_count


# Singleton instance
opportunity_storage = OpportunityStorageService()
