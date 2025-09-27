"""
Revenue Opportunity Detection System
Analyzes spider intelligence for money-making opportunities
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RevenueOpportunityDetector:
    """
    Advanced revenue opportunity detection and analysis
    Identifies and scores money-making opportunities from spider data
    """

    def __init__(self):
        self.redis_client = None
        self.opportunity_patterns = {
            'freelance': {
                'keywords': ['hiring', 'contractor', 'remote', 'developer', 'freelance', 'consultant'],
                'value_multiplier': 1.2,
                'priority_boost': 2
            },
            'consulting': {
                'keywords': ['advisor', 'expert', 'consultant', 'advisory', 'consulting'],
                'value_multiplier': 1.5,
                'priority_boost': 3
            },
            'product': {
                'keywords': ['affiliate', 'commission', 'partner', 'reseller', 'revenue share'],
                'value_multiplier': 2.0,
                'priority_boost': 1
            },
            'investment': {
                'keywords': ['funding', 'investor', 'equity', 'startup', 'seed', 'series'],
                'value_multiplier': 3.0,
                'priority_boost': 4
            },
            'contract': {
                'keywords': ['contract', 'project', 'engagement', 'fixed-price', 'retainer'],
                'value_multiplier': 1.3,
                'priority_boost': 2
            },
            'job': {
                'keywords': ['position', 'opening', 'role', 'job', 'career', 'full-time', 'part-time'],
                'value_multiplier': 1.0,
                'priority_boost': 1
            }
        }

        self.value_indicators = {
            'high': ['150k', '200k', '250k', '300k', 'six figure', 'high compensation'],
            'medium': ['100k', '120k', '80k', '90k', 'competitive'],
            'hourly': ['hour', 'hourly', 'hr', 'per hour'],
            'monthly': ['month', 'monthly', 'retainer'],
            'project': ['project', 'fixed', 'milestone']
        }

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await redis.from_url('redis://localhost:6379/0')
            logger.info("Revenue Detector Redis connection established")
        except Exception as e:
            logger.error(f"Revenue Detector Redis connection failed: {e}")

    async def analyze_spider_data(self, data: str) -> List[Dict[str, Any]]:
        """
        Analyze spider intelligence for revenue opportunities
        Returns list of detected opportunities with scores
        """
        opportunities = []
        data_lower = data.lower()

        # Check each pattern category
        for category, config in self.opportunity_patterns.items():
            keywords = config['keywords']
            if any(keyword in data_lower for keyword in keywords):
                opportunity = {
                    'type': category,
                    'source': data,
                    'confidence': self.calculate_confidence(data, keywords),
                    'potential_value': self.estimate_value(data, config['value_multiplier']),
                    'priority': self.calculate_priority(data, config['priority_boost']),
                    'action_required': self.determine_action(category, data),
                    'timestamp': datetime.now().isoformat(),
                    'keywords_matched': [k for k in keywords if k in data_lower]
                }
                opportunities.append(opportunity)

        # Sort by priority
        opportunities.sort(key=lambda x: x['priority'], reverse=True)

        # Store in Redis if opportunities found
        if opportunities and self.redis_client:
            await self.store_opportunities(opportunities)

        return opportunities

    def calculate_confidence(self, data: str, keywords: List[str]) -> float:
        """Calculate confidence score based on keyword matches"""
        data_lower = data.lower()
        matches = sum(1 for k in keywords if k in data_lower)

        # Base confidence from keyword matches
        confidence = min(matches * 0.2, 1.0)

        # Boost for value indicators
        if any(indicator in data_lower for indicator in ['$', 'salary', 'rate', 'compensation']):
            confidence = min(confidence + 0.2, 1.0)

        # Boost for urgency indicators
        if any(urgent in data_lower for urgent in ['urgent', 'immediate', 'asap', 'now hiring']):
            confidence = min(confidence + 0.15, 1.0)

        return round(confidence, 2)

    def estimate_value(self, data: str, multiplier: float) -> Dict[str, Any]:
        """Estimate potential value of opportunity"""
        import re

        data_lower = data.lower()

        # Look for explicit dollar amounts
        dollar_pattern = r'\$[\d,]+[k]?'
        dollar_matches = re.findall(dollar_pattern, data_lower)

        if dollar_matches:
            # Parse the highest value found
            values = []
            for match in dollar_matches:
                value_str = match.replace('$', '').replace(',', '')
                if 'k' in value_str:
                    value = float(value_str.replace('k', '')) * 1000
                else:
                    value = float(value_str)
                values.append(value)

            max_value = max(values) * multiplier

            return {
                'estimated': max_value,
                'range': f"${min(values):,.0f} - ${max_value:,.0f}",
                'confidence': 'high',
                'period': self.detect_period(data_lower)
            }

        # Estimate based on keywords
        if any(high in data_lower for high in self.value_indicators['high']):
            return {
                'estimated': 200000 * multiplier,
                'range': "$150k - $300k",
                'confidence': 'medium',
                'period': 'annual'
            }
        elif any(med in data_lower for med in self.value_indicators['medium']):
            return {
                'estimated': 100000 * multiplier,
                'range': "$80k - $120k",
                'confidence': 'medium',
                'period': 'annual'
            }

        # Default estimate
        return {
            'estimated': 75000 * multiplier,
            'range': "To be determined",
            'confidence': 'low',
            'period': 'unknown'
        }

    def detect_period(self, text: str) -> str:
        """Detect payment period from text"""
        if any(h in text for h in ['hour', 'hourly', '/hr', 'per hour']):
            return 'hourly'
        elif any(m in text for m in ['month', 'monthly', '/mo']):
            return 'monthly'
        elif any(y in text for y in ['year', 'annual', 'yearly', '/yr']):
            return 'annual'
        elif any(p in text for p in ['project', 'fixed', 'one-time']):
            return 'project'
        return 'unknown'

    def calculate_priority(self, data: str, base_priority: int) -> int:
        """Calculate opportunity priority (1-10 scale)"""
        priority = base_priority
        data_lower = data.lower()

        # Urgency boosters
        if any(u in data_lower for u in ['urgent', 'immediate', 'asap', 'deadline']):
            priority += 3

        # Value boosters
        if '$' in data and any(h in data_lower for h in ['200k', '250k', '300k']):
            priority += 2
        elif '$' in data and any(m in data_lower for m in ['100k', '150k']):
            priority += 1

        # Remote work booster
        if 'remote' in data_lower:
            priority += 1

        return min(priority, 10)

    def determine_action(self, category: str, data: str) -> Dict[str, Any]:
        """Determine recommended action for opportunity"""
        actions = {
            'freelance': {
                'primary': 'Submit proposal',
                'steps': ['Review requirements', 'Prepare portfolio', 'Write proposal', 'Submit application'],
                'urgency': 'high'
            },
            'consulting': {
                'primary': 'Schedule consultation',
                'steps': ['Research client', 'Prepare expertise summary', 'Reach out', 'Schedule call'],
                'urgency': 'medium'
            },
            'product': {
                'primary': 'Evaluate partnership',
                'steps': ['Review terms', 'Calculate ROI', 'Negotiate terms', 'Sign agreement'],
                'urgency': 'low'
            },
            'investment': {
                'primary': 'Analyze opportunity',
                'steps': ['Due diligence', 'Risk assessment', 'ROI calculation', 'Investment decision'],
                'urgency': 'medium'
            },
            'contract': {
                'primary': 'Submit bid',
                'steps': ['Review scope', 'Estimate effort', 'Prepare bid', 'Submit proposal'],
                'urgency': 'high'
            },
            'job': {
                'primary': 'Apply now',
                'steps': ['Update resume', 'Write cover letter', 'Submit application', 'Follow up'],
                'urgency': 'high'
            }
        }

        return actions.get(category, {
            'primary': 'Review opportunity',
            'steps': ['Analyze details', 'Assess fit', 'Make decision'],
            'urgency': 'medium'
        })

    async def store_opportunities(self, opportunities: List[Dict[str, Any]]):
        """Store opportunities in Redis for persistence"""
        if not self.redis_client:
            return

        try:
            for opp in opportunities:
                # Create unique key
                key = f"opportunity:{datetime.now().strftime('%Y%m%d%H%M%S')}:{opp['type']}"

                # Store with 7-day TTL
                await self.redis_client.setex(
                    key,
                    604800,  # 7 days
                    json.dumps(opp)
                )

                # Add to opportunity list
                await self.redis_client.lpush('opportunity_list', key)

                # Keep only last 1000 opportunities
                await self.redis_client.ltrim('opportunity_list', 0, 999)

            logger.info(f"Stored {len(opportunities)} opportunities in Redis")

        except Exception as e:
            logger.error(f"Error storing opportunities: {e}")

    async def get_recent_opportunities(self, count: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent opportunities from Redis"""
        if not self.redis_client:
            return []

        try:
            # Get keys from list
            keys = await self.redis_client.lrange('opportunity_list', 0, count - 1)

            opportunities = []
            for key in keys:
                if isinstance(key, bytes):
                    key = key.decode('utf-8')

                data = await self.redis_client.get(key)
                if data:
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    opportunities.append(json.loads(data))

            return opportunities

        except Exception as e:
            logger.error(f"Error retrieving opportunities: {e}")
            return []

    async def notify_agents(self, opportunities: List[Dict[str, Any]]):
        """Notify relevant agents about opportunities"""
        if not self.redis_client or not opportunities:
            return

        try:
            # Publish to agent notification channel
            for opp in opportunities:
                notification = {
                    'type': 'revenue_opportunity',
                    'opportunity': opp,
                    'agents_to_notify': self.select_agents_for_opportunity(opp),
                    'timestamp': datetime.now().isoformat()
                }

                await self.redis_client.publish(
                    'agent_notifications',
                    json.dumps(notification)
                )

            logger.info(f"Notified agents about {len(opportunities)} opportunities")

        except Exception as e:
            logger.error(f"Error notifying agents: {e}")

    def select_agents_for_opportunity(self, opportunity: Dict[str, Any]) -> List[str]:
        """Select which agents should handle this opportunity"""
        opp_type = opportunity.get('type', '')

        agent_mapping = {
            'freelance': ['Market Analyst', 'Content Creator', 'Auto Apply Agent'],
            'consulting': ['Career Coach', 'Market Analyst', 'Content Creator'],
            'product': ['Market Analyst', 'Revenue Optimizer', 'Partnership Manager'],
            'investment': ['Portfolio Manager', 'Risk Assessor', 'Market Analyst'],
            'contract': ['Project Manager', 'Content Creator', 'Auto Apply Agent'],
            'job': ['Career Coach', 'Resume Builder', 'Auto Apply Agent']
        }

        return agent_mapping.get(opp_type, ['Market Analyst', 'Decision Engine'])

    async def cleanup(self):
        """Cleanup Redis connection"""
        if self.redis_client:
            await self.redis_client.close()