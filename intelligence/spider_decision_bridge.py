#!/usr/bin/env python
"""
Spider-Decision Command Bridge
============================
Connects real spider job data to Decision Command for live opportunity analysis and decision making
"""

import asyncio
import os
import redis
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Import our real components
from ai_core.spiders.real_job_spider import RealJobSpider
from intelligence.income_builder import income_builder

logger = logging.getLogger(__name__)

# Redis URL for production - use DB 4 for decision bridge.
# Session 1083 (Rigby audit): previous `_REDIS_URL.rsplit('/', 1)[0] + '/4'`
# was broken when REDIS_URL had no explicit database number. For a URL like
# `redis://localhost:6379` the rsplit ate one slash of `://` and produced
# `redis://4`, which parses as host=`4` port=`6379` and threw
# `Error 65 connecting to 4:6379` on every spider_decision_bridge call.
# Fixed via urllib.parse to rebuild the URL safely regardless of whether
# the source URL had a trailing `/db` segment. Surfaced while monitoring
# a run_spider_network log after unsticking the long_running worker
# deadlock — had been producing Redis errors for ~30 opportunities/minute
# for an unknown amount of time.
from urllib.parse import urlparse, urlunparse
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
_parsed_redis = urlparse(_REDIS_URL)
_REDIS_URL_DB4 = urlunparse(_parsed_redis._replace(path='/4'))

@dataclass
class OpportunityDecision:
    """Represents a decision opportunity for the user"""
    id: str
    source: str
    title: str
    company: str
    budget: float
    description: str
    skills_required: List[str]
    platform: str
    url: str
    urgency: str
    success_probability: float
    recommended_action: str
    reasoning: str
    decision_factors: List[Dict[str, Any]]
    time_commitment: str
    created_at: str
    expires_at: str

class SpiderDecisionBridge:
    """
    Bridge between spider network and Decision Command
    Transforms real job opportunities into actionable decisions
    """

    def __init__(self):
        self.redis = redis.Redis.from_url(_REDIS_URL_DB4, decode_responses=True)
        self.spider = RealJobSpider()
        self.income_builder = income_builder
        self.active_opportunities = {}
        self.decision_history = []

    async def initialize(self):
        """Initialize the bridge components"""
        await self.spider.initialize()
        logger.info("🌉 Spider-Decision Bridge initialized")

    async def scan_for_opportunities(self) -> List[OpportunityDecision]:
        """
        Scan for new opportunities using real spiders and convert to decisions
        """
        logger.info("🕷️ Scanning for new opportunities...")

        try:
            # Get real job opportunities from spider
            raw_opportunities = await self.spider.search_real_jobs([
                'python', 'ai', 'automation', 'content writing', 'data analysis'
            ])

            logger.info(f"Found {len(raw_opportunities)} raw opportunities")

            # Cap per-scan to prevent worker starvation (10 items x ~90s = ~15min)
            _MAX_PER_SCAN = 10
            if len(raw_opportunities) > _MAX_PER_SCAN:
                logger.info(f"Capping {len(raw_opportunities)} opportunities to {_MAX_PER_SCAN}")
                raw_opportunities = raw_opportunities[:_MAX_PER_SCAN]

            # Convert to decision opportunities
            decision_opportunities = []

            for opp in raw_opportunities:
                try:
                    # Analyze opportunity with Income Builder
                    analysis = await self.income_builder.analyze_external_opportunity(opp)

                    # Create decision opportunity
                    decision_opp = await self._create_decision_opportunity(opp, analysis)
                    decision_opportunities.append(decision_opp)

                    # Store in Redis for persistence
                    await self._store_opportunity(decision_opp)

                except Exception as e:
                    logger.error(f"Error analyzing opportunity {opp.get('title', 'Unknown')}: {e}")
                    continue

            logger.info(f"✅ Created {len(decision_opportunities)} decision opportunities")

            # Store scan results
            scan_result = {
                'timestamp': datetime.now().isoformat(),
                'opportunities_found': len(raw_opportunities),
                'decisions_created': len(decision_opportunities),
                'success_rate': len(decision_opportunities) / max(len(raw_opportunities), 1)
            }

            self.redis.set('spider_decision_bridge:last_scan', json.dumps(scan_result))

            return decision_opportunities

        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")
            return []

    async def _create_decision_opportunity(self, raw_opp: Dict, analysis: Dict) -> OpportunityDecision:
        """Convert raw opportunity to decision opportunity"""

        # Extract key information
        title = raw_opp.get('title', 'Unknown Position')
        company = raw_opp.get('company', 'Unknown Company')
        source = raw_opp.get('source', 'Unknown Source')

        # Parse budget
        budget = self._parse_budget(raw_opp)

        # Extract skills
        skills_required = self._extract_skills(raw_opp)

        # Get success probability from analysis
        success_probability = analysis.get('success_probability', 0.5)

        # Determine urgency
        urgency = self._determine_urgency(raw_opp, analysis)

        # Create recommendation
        recommended_action, reasoning = self._create_recommendation(raw_opp, analysis)

        # Create decision factors
        decision_factors = self._create_decision_factors(raw_opp, analysis)

        # Generate unique ID
        opportunity_id = f"opp_{int(datetime.now().timestamp())}_{hash(title)%10000}"

        # Save to database NOW (CRITICAL FIX)
        await self._save_opportunity_to_database(
            opportunity_id=opportunity_id,
            title=title,
            source=source,
            budget=budget,
            description=raw_opp.get('description', ''),
            skills_required=skills_required,
            raw_opp=raw_opp,
            analysis=analysis
        )

        return OpportunityDecision(
            id=opportunity_id,
            source=source,
            title=title,
            company=company,
            budget=budget,
            description=raw_opp.get('description', '')[:500],
            skills_required=skills_required,
            platform=source,
            url=raw_opp.get('url', ''),
            urgency=urgency,
            success_probability=success_probability,
            recommended_action=recommended_action,
            reasoning=reasoning,
            decision_factors=decision_factors,
            time_commitment=self._estimate_time_commitment(raw_opp),
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=7)).isoformat()
        )

    def _parse_budget(self, opp: Dict) -> float:
        """Parse budget from opportunity"""
        # Try different budget fields
        for field in ['salary_max', 'budget', 'salary_min']:
            if field in opp and opp[field]:
                try:
                    budget = float(str(opp[field]).replace('$', '').replace(',', ''))
                    if budget > 0:
                        return budget
                except:
                    continue

        # Default budget based on source
        source = opp.get('source', '').lower()
        if 'github' in source:
            return 5000  # Typical full-time job
        elif 'remote' in source:
            return 3000  # Remote work average
        else:
            return 1000  # Freelance project average

    def _extract_skills(self, opp: Dict) -> List[str]:
        """Extract required skills from opportunity"""
        skills = []

        # Check explicit skills field
        if 'skills_required' in opp:
            skills.extend(opp['skills_required'])

        # Extract from tags
        if 'tags' in opp and opp['tags']:
            skills.extend(opp['tags'])

        # Extract from title and description
        text = f"{opp.get('title', '')} {opp.get('description', '')}".lower()

        # Common skill keywords
        skill_keywords = [
            'python', 'javascript', 'react', 'node', 'django', 'flask',
            'ai', 'machine learning', 'data analysis', 'automation',
            'content writing', 'copywriting', 'seo', 'marketing',
            'design', 'ui', 'ux', 'figma', 'photoshop',
            'project management', 'scrum', 'agile'
        ]

        for keyword in skill_keywords:
            if keyword in text and keyword not in skills:
                skills.append(keyword)

        return skills[:5]  # Limit to top 5 skills

    def _determine_urgency(self, opp: Dict, analysis: Dict) -> str:
        """Determine urgency level"""
        text = f"{opp.get('title', '')} {opp.get('description', '')}".lower()

        if any(word in text for word in ['urgent', 'asap', 'immediate', 'rush']):
            return 'high'
        elif any(word in text for word in ['soon', 'quick', 'fast']):
            return 'medium'
        else:
            return 'normal'

    def _create_recommendation(self, opp: Dict, analysis: Dict) -> tuple[str, str]:
        """Create recommendation and reasoning"""
        success_prob = analysis.get('success_probability', 0.5)
        budget = self._parse_budget(opp)

        if success_prob > 0.8 and budget > 1000:
            return 'APPLY NOW', f"High success probability ({success_prob:.1%}) and excellent budget (${budget:.0f})"
        elif success_prob > 0.6:
            return 'CONSIDER', f"Good success probability ({success_prob:.1%}) worth pursuing"
        elif budget > 2000:
            return 'APPLY NOW', f"High-value opportunity (${budget:.0f}) justifies the risk"
        else:
            return 'REVIEW', f"Moderate opportunity - review against current priorities"

    def _create_decision_factors(self, opp: Dict, analysis: Dict) -> List[Dict[str, Any]]:
        """Create decision factors for evaluation"""
        factors = []

        # Budget factor
        budget = self._parse_budget(opp)
        budget_score = min(budget / 1000 * 20, 100)
        factors.append({
            'factor': 'Budget Match',
            'score': int(budget_score),
            'description': f"${budget:.0f} budget"
        })

        # Skill alignment
        ml_score = analysis.get('ml_score', {})
        skill_score = ml_score.get('factors', {}).get('skill_match', 0.5) * 100
        factors.append({
            'factor': 'Skill Alignment',
            'score': int(skill_score),
            'description': f"Matches {len(self._extract_skills(opp))} required skills"
        })

        # Time availability
        factors.append({
            'factor': 'Time Available',
            'score': 80,  # Default assumption
            'description': 'Good availability for project timeline'
        })

        # Competition level
        competition = analysis.get('market_context', {}).get('competition_analysis', {}).get('level', 0.5)
        competition_score = (1 - competition) * 100
        factors.append({
            'factor': 'Competition Level',
            'score': int(competition_score),
            'description': f"{'Low' if competition < 0.5 else 'High'} competition expected"
        })

        return factors

    def _estimate_time_commitment(self, opp: Dict) -> str:
        """Estimate time commitment"""
        text = f"{opp.get('title', '')} {opp.get('description', '')}".lower()

        if 'full time' in text or 'full-time' in text:
            return '40 hours/week'
        elif 'part time' in text or 'part-time' in text:
            return '20 hours/week'
        elif any(word in text for word in ['project', 'contract', 'freelance']):
            return '1-2 weeks'
        else:
            return '10-20 hours'

    async def _store_opportunity(self, opportunity: OpportunityDecision):
        """Store opportunity in Redis"""
        key = f"decision_opportunities:{opportunity.id}"
        data = asdict(opportunity)

        # Store individual opportunity
        self.redis.setex(key, 7*24*3600, json.dumps(data))  # Expires in 7 days

        # Add to opportunities list
        self.redis.lpush("decision_opportunities:all", opportunity.id)
        self.redis.ltrim("decision_opportunities:all", 0, 99)  # Keep last 100

        logger.info(f"Stored opportunity: {opportunity.title}")

    async def get_active_opportunities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get active opportunities for Decision Command"""
        try:
            # Get recent opportunity IDs
            opportunity_ids = self.redis.lrange("decision_opportunities:all", 0, limit-1)

            opportunities = []
            for opp_id in opportunity_ids:
                key = f"decision_opportunities:{opp_id}"
                data = self.redis.get(key)

                if data:
                    try:
                        opp_data = json.loads(data)

                        # Convert to Decision Command format
                        decision_opp = {
                            'id': opp_data['id'],
                            'type': 'income',
                            'title': opp_data['title'],
                            'description': opp_data['description'],
                            'value': opp_data['budget'],
                            'time_commitment': opp_data['time_commitment'],
                            'success_probability': opp_data['success_probability'],
                            'required_skills': opp_data['skills_required'],
                            'decision_factors': opp_data['decision_factors'],
                            'recommended_action': opp_data['recommended_action'],
                            'reasoning': opp_data['reasoning'],
                            'platform': opp_data['platform'],
                            'urgency': opp_data['urgency'],
                            'url': opp_data['url'],
                            'company': opp_data['company'],
                            'created_at': opp_data['created_at'],
                            'expires_at': opp_data['expires_at']
                        }

                        opportunities.append(decision_opp)

                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON data for opportunity {opp_id}")
                        continue

            logger.info(f"Retrieved {len(opportunities)} active opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Error getting active opportunities: {e}")
            return []

    async def execute_decision(self, decision_id: str, action: str, user_context: Dict = None) -> Dict[str, Any]:
        """Execute a decision on an opportunity"""
        try:
            # Get opportunity data
            key = f"decision_opportunities:{decision_id}"
            data = self.redis.get(key)

            if not data:
                return {'success': False, 'error': 'Opportunity not found'}

            opportunity_data = json.loads(data)

            result = {
                'decision_id': decision_id,
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }

            if action == 'ACCEPT':
                # Generate real proposal using Income Builder
                proposal_result = await self.income_builder.generate_real_time_proposal(
                    opportunity_data,
                    user_context
                )

                result.update({
                    'status': 'proposal_generated',
                    'proposal': proposal_result.get('proposal_content', ''),
                    'pricing_strategy': proposal_result.get('pricing_strategy', {}),
                    'estimated_win_rate': proposal_result.get('estimated_win_rate', 0.5),
                    'next_steps': [
                        'Review and customize proposal',
                        'Prepare portfolio examples',
                        'Submit application',
                        'Set up tracking for responses'
                    ]
                })

                # Store decision in history
                self._store_decision_history(decision_id, action, result)

                logger.info(f"Generated proposal for opportunity: {opportunity_data['title']}")

            elif action == 'REJECT':
                result.update({
                    'status': 'rejected',
                    'reason': 'User decided not to pursue this opportunity',
                    'next_steps': ['Opportunity marked as not interested']
                })

            elif action == 'DEFER':
                result.update({
                    'status': 'deferred',
                    'reason': 'Opportunity saved for later consideration',
                    'next_steps': ['Added to watchlist', 'Will revisit in 48 hours']
                })

            return result

        except Exception as e:
            logger.error(f"Error executing decision: {e}")
            return {'success': False, 'error': str(e)}

    def _store_decision_history(self, decision_id: str, action: str, result: Dict):
        """Store decision in history"""
        history_entry = {
            'decision_id': decision_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'result': result
        }

        self.redis.lpush("decision_history", json.dumps(history_entry))
        self.redis.ltrim("decision_history", 0, 499)  # Keep last 500 decisions

    async def get_statistics(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        try:
            # Get last scan info
            last_scan_data = self.redis.get('spider_decision_bridge:last_scan')
            last_scan = json.loads(last_scan_data) if last_scan_data else {}

            # Count active opportunities
            active_count = self.redis.llen("decision_opportunities:all")

            # Count decisions made
            decisions_count = self.redis.llen("decision_history")

            return {
                'last_scan': last_scan,
                'active_opportunities': active_count,
                'decisions_made': decisions_count,
                'bridge_status': 'active',
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}

    async def _save_opportunity_to_database(self, opportunity_id: str, title: str, source: str,
                                            budget: float, description: str, skills_required: List[str],
                                            raw_opp: Dict, analysis: Dict):
        """
        CRITICAL FIX: Save opportunity to Django database
        This is the missing link that caused 0 opportunities in the database
        """
        from channels.db import database_sync_to_async
        from core.models import Opportunity
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            @database_sync_to_async
            def create_opportunity():
                # Get the first user (or a system user if available)
                # In production, this should be tied to the user requesting opportunities
                user = User.objects.first()
                if not user:
                    logger.warning("No users found - cannot save opportunity")
                    return None

                # Check if opportunity already exists
                existing = Opportunity.objects.filter(
                    source=source,
                    metadata__spider_id=opportunity_id
                ).first()

                if existing:
                    logger.info(f"Opportunity {opportunity_id} already exists in database")
                    return existing

                # Calculate match score from analysis
                ml_score = analysis.get('ml_score', {})
                match_score = int(ml_score.get('final_score', 0.5) * 100)

                # Create new opportunity
                opportunity = Opportunity.objects.create(
                    user=user,
                    title=title,
                    opportunity_type=raw_opp.get('type', 'freelance_services'),
                    source=source,
                    potential_revenue=budget,
                    hourly_rate=raw_opp.get('hourly_rate'),
                    status='active',
                    match_score=match_score,
                    description=description,
                    requirements=skills_required,
                    metadata={
                        'spider_id': opportunity_id,
                        'platform': source,
                        'url': raw_opp.get('url', ''),
                        'company': raw_opp.get('company', ''),
                        'analysis': analysis,
                        'raw_data': raw_opp,
                        'created_via': 'spider_decision_bridge'
                    }
                )

                logger.info(f"✅ SAVED opportunity to database: {opportunity.id} - {title}")
                return opportunity

            # Execute the database operation
            result = await create_opportunity()
            return result

        except Exception as e:
            logger.error(f"❌ ERROR saving opportunity to database: {e}", exc_info=True)
            return None

    async def close(self):
        """Close bridge connections"""
        await self.spider.close()
        logger.info("🌉 Spider-Decision Bridge closed")

# Global bridge instance
spider_decision_bridge = SpiderDecisionBridge()

async def start_opportunity_monitoring():
    """Start monitoring for opportunities"""
    await spider_decision_bridge.initialize()

    logger.info("🚀 Starting opportunity monitoring...")

    while True:
        try:
            # Scan for new opportunities every 30 minutes
            opportunities = await spider_decision_bridge.scan_for_opportunities()

            if opportunities:
                logger.info(f"Found {len(opportunities)} new opportunities")

                # Store summary stats
                stats = await spider_decision_bridge.get_statistics()
                logger.info(f"Bridge stats: {stats}")

            # Wait 30 minutes before next scan
            await asyncio.sleep(1800)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retry

if __name__ == "__main__":
    asyncio.run(start_opportunity_monitoring())