#!/usr/bin/env python
"""
Multi-Domain Agent Learning System
================================
Agents learn from ALL types of experiences, not just code:
- Market intelligence & trends
- Communication patterns & strategies
- User behavior & personalization
- Platform optimization tactics
- Financial & business insights
"""

import redis
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

class LearningDomain(Enum):
    """Types of knowledge agents can learn"""
    CODE_SOLUTIONS = "code_solutions"
    MARKET_INTELLIGENCE = "market_intelligence"
    COMMUNICATION_PATTERNS = "communication_patterns"
    USER_BEHAVIOR = "user_behavior"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    FINANCIAL_STRATEGIES = "financial_strategies"
    NEGOTIATION_TACTICS = "negotiation_tactics"
    CONTENT_STRATEGIES = "content_strategies"
    SKILL_DEVELOPMENT = "skill_development"
    BUSINESS_INTELLIGENCE = "business_intelligence"

@dataclass
class Learning:
    """Represents any type of learning, not just code"""
    learning_id: str
    domain: LearningDomain
    agent_id: str
    context: str                    # What situation this applies to
    knowledge: Dict[str, Any]       # The actual learned knowledge
    evidence: List[Dict]            # Supporting evidence/examples
    confidence: float               # How confident agent is (0-1)
    applicability: List[str]        # What situations this applies to
    created_at: str
    last_updated: str
    success_rate: float             # Track effectiveness
    usage_count: int                # How often this learning is applied

@dataclass
class MarketIntelligence:
    """Market trends and opportunities"""
    platform: str
    skill_category: str
    demand_level: float             # 0-1, how in demand
    competition_level: float        # 0-1, how competitive
    average_rate: float
    trending_keywords: List[str]
    success_factors: List[str]
    seasonal_patterns: Dict[str, float]
    geographic_hotspots: List[str]

@dataclass
class CommunicationPattern:
    """Effective communication strategies"""
    pattern_type: str               # "proposal", "follow_up", "negotiation"
    context: str                    # When to use this pattern
    template: str                   # The actual message template
    personalization_points: List[str]  # What to customize
    success_rate: float
    response_rate: float
    conversion_rate: float
    optimal_timing: Dict[str, str]  # Best times to send

@dataclass
class UserBehaviorInsight:
    """Understanding individual user patterns"""
    user_id: str
    behavior_type: str              # "decision_making", "productivity", "preferences"
    pattern: Dict[str, Any]         # The observed pattern
    triggers: List[str]             # What causes this behavior
    outcomes: List[str]             # What results from this behavior
    optimization_suggestions: List[str]

class MultiDomainLearning:
    """
    Comprehensive learning system for agents across all domains
    """

    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=3,  # Multi-domain learning database
            decode_responses=True
        )

    # === Core Learning Methods ===

    def store_learning(self, learning: Learning) -> str:
        """Store any type of learning"""
        key = f"learning:{learning.domain.value}:{learning.learning_id}"

        # Convert to dict and handle enum serialization
        learning_dict = asdict(learning)
        learning_dict['domain'] = learning.domain.value  # Convert enum to string

        # Store the learning
        self.redis.setex(
            key,
            30 * 24 * 3600,  # 30 days
            json.dumps(learning_dict)
        )

        # Index by domain
        self.redis.sadd(f"domain:{learning.domain.value}", learning.learning_id)

        # Index by agent
        self.redis.sadd(f"agent_learnings:{learning.agent_id}", learning.learning_id)

        # Index by context for quick retrieval
        for context in learning.applicability:
            self.redis.sadd(f"context:{context}", learning.learning_id)

        return key

    def get_learnings_for_context(self, context: str, domain: LearningDomain = None) -> List[Learning]:
        """Get all learnings that apply to a specific context"""
        if domain:
            # Get learnings for specific domain and context
            domain_learnings = self.redis.smembers(f"domain:{domain.value}")
            context_learnings = self.redis.smembers(f"context:{context}")
            relevant_ids = domain_learnings.intersection(context_learnings)
        else:
            # Get all learnings for context
            relevant_ids = self.redis.smembers(f"context:{context}")

        learnings = []
        for learning_id in relevant_ids:
            # Find which domain this belongs to
            for domain_type in LearningDomain:
                key = f"learning:{domain_type.value}:{learning_id}"
                data = self.redis.get(key)
                if data:
                    learning_dict = json.loads(data)
                    learning_dict['domain'] = LearningDomain(learning_dict['domain'])
                    learnings.append(Learning(**learning_dict))
                    break

        return sorted(learnings, key=lambda x: x.confidence, reverse=True)

    # === Market Intelligence Learning ===

    def learn_market_trend(self, agent_id: str, platform: str, observation: Dict[str, Any]) -> str:
        """Agent learns about market trends"""
        trend_id = f"market_{int(datetime.now().timestamp())}"

        learning = Learning(
            learning_id=trend_id,
            domain=LearningDomain.MARKET_INTELLIGENCE,
            agent_id=agent_id,
            context=f"Platform analysis for {platform}",
            knowledge={
                'platform': platform,
                'trend_type': observation.get('trend_type'),
                'direction': observation.get('direction'),  # increasing/decreasing/stable
                'magnitude': observation.get('magnitude', 0.5),
                'timeframe': observation.get('timeframe'),
                'supporting_data': observation.get('data', [])
            },
            evidence=[observation],
            confidence=observation.get('confidence', 0.7),
            applicability=[platform, 'market_analysis', 'opportunity_selection'],
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            success_rate=0.0,  # Will be updated based on outcomes
            usage_count=0
        )

        return self.store_learning(learning)

    def learn_successful_proposal(self, agent_id: str, proposal_data: Dict[str, Any]) -> str:
        """Agent learns from successful proposals"""
        proposal_id = f"proposal_{int(datetime.now().timestamp())}"

        learning = Learning(
            learning_id=proposal_id,
            domain=LearningDomain.COMMUNICATION_PATTERNS,
            agent_id=agent_id,
            context="Job proposal writing",
            knowledge={
                'proposal_structure': proposal_data.get('structure'),
                'key_phrases': proposal_data.get('successful_phrases', []),
                'personalization_points': proposal_data.get('personalization', []),
                'pricing_strategy': proposal_data.get('pricing'),
                'timeline_approach': proposal_data.get('timeline'),
                'client_type': proposal_data.get('client_type'),
                'project_category': proposal_data.get('category')
            },
            evidence=[{
                'proposal_text': proposal_data.get('text'),
                'response_time': proposal_data.get('response_time'),
                'client_feedback': proposal_data.get('feedback'),
                'conversion_outcome': proposal_data.get('outcome')
            }],
            confidence=0.8 if proposal_data.get('outcome') == 'hired' else 0.6,
            applicability=['proposal_writing', proposal_data.get('category', 'general'), proposal_data.get('client_type', 'general')],
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            success_rate=1.0 if proposal_data.get('outcome') == 'hired' else 0.0,
            usage_count=0
        )

        return self.store_learning(learning)

    def learn_user_behavior(self, agent_id: str, user_id: str, behavior_observation: Dict[str, Any]) -> str:
        """Agent learns about specific user behavior patterns"""
        behavior_id = f"user_behavior_{user_id}_{int(datetime.now().timestamp())}"

        learning = Learning(
            learning_id=behavior_id,
            domain=LearningDomain.USER_BEHAVIOR,
            agent_id=agent_id,
            context=f"User behavior for {user_id}",
            knowledge={
                'user_id': user_id,
                'behavior_type': behavior_observation.get('type'),
                'pattern': behavior_observation.get('pattern'),
                'triggers': behavior_observation.get('triggers', []),
                'preferences': behavior_observation.get('preferences', {}),
                'decision_factors': behavior_observation.get('decision_factors', []),
                'productivity_patterns': behavior_observation.get('productivity', {}),
                'success_indicators': behavior_observation.get('success_indicators', [])
            },
            evidence=[behavior_observation],
            confidence=behavior_observation.get('confidence', 0.6),
            applicability=[f'user_{user_id}', 'personalization', 'user_optimization'],
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            success_rate=0.0,
            usage_count=0
        )

        return self.store_learning(learning)

    def learn_platform_optimization(self, agent_id: str, platform: str, optimization: Dict[str, Any]) -> str:
        """Agent learns platform-specific optimization tactics"""
        opt_id = f"platform_opt_{platform}_{int(datetime.now().timestamp())}"

        learning = Learning(
            learning_id=opt_id,
            domain=LearningDomain.PLATFORM_OPTIMIZATION,
            agent_id=agent_id,
            context=f"Optimization for {platform}",
            knowledge={
                'platform': platform,
                'optimization_type': optimization.get('type'),
                'tactic': optimization.get('tactic'),
                'implementation': optimization.get('implementation'),
                'expected_outcome': optimization.get('expected_outcome'),
                'metrics_to_track': optimization.get('metrics', []),
                'prerequisites': optimization.get('prerequisites', []),
                'risks': optimization.get('risks', [])
            },
            evidence=[optimization],
            confidence=optimization.get('confidence', 0.7),
            applicability=[platform, 'platform_optimization', optimization.get('type', 'general')],
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            success_rate=0.0,
            usage_count=0
        )

        return self.store_learning(learning)

    def learn_financial_strategy(self, agent_id: str, strategy: Dict[str, Any]) -> str:
        """Agent learns financial and business strategies"""
        strategy_id = f"financial_{int(datetime.now().timestamp())}"

        learning = Learning(
            learning_id=strategy_id,
            domain=LearningDomain.FINANCIAL_STRATEGIES,
            agent_id=agent_id,
            context="Financial optimization",
            knowledge={
                'strategy_type': strategy.get('type'),
                'approach': strategy.get('approach'),
                'target_outcome': strategy.get('target_outcome'),
                'implementation_steps': strategy.get('steps', []),
                'risk_level': strategy.get('risk_level'),
                'time_horizon': strategy.get('time_horizon'),
                'success_metrics': strategy.get('metrics', []),
                'prerequisites': strategy.get('prerequisites', [])
            },
            evidence=[strategy],
            confidence=strategy.get('confidence', 0.6),
            applicability=['financial_planning', 'business_strategy', strategy.get('type', 'general')],
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            success_rate=0.0,
            usage_count=0
        )

        return self.store_learning(learning)

    # === Knowledge Application ===

    def get_recommendations_for_situation(self, situation: str, user_context: Dict = None) -> List[Dict[str, Any]]:
        """Get learned recommendations for a specific situation"""
        relevant_learnings = self.get_learnings_for_context(situation)

        recommendations = []
        for learning in relevant_learnings[:10]:  # Top 10 most relevant
            # Apply user context filtering if provided
            if user_context and learning.domain == LearningDomain.USER_BEHAVIOR:
                if learning.knowledge.get('user_id') != user_context.get('user_id'):
                    continue

            recommendation = {
                'type': learning.domain.value,
                'confidence': learning.confidence,
                'recommendation': self._format_recommendation(learning),
                'evidence': learning.evidence[:3],  # Include some evidence
                'success_rate': learning.success_rate,
                'agent_source': learning.agent_id
            }
            recommendations.append(recommendation)

        return sorted(recommendations, key=lambda x: x['confidence'] * x['success_rate'], reverse=True)

    def _format_recommendation(self, learning: Learning) -> str:
        """Format learning into actionable recommendation"""
        if learning.domain == LearningDomain.COMMUNICATION_PATTERNS:
            return f"Based on successful proposals, use this approach: {learning.knowledge.get('proposal_structure', 'N/A')}"
        elif learning.domain == LearningDomain.MARKET_INTELLIGENCE:
            return f"Market trend indicates: {learning.knowledge.get('trend_type')} is {learning.knowledge.get('direction')} on {learning.knowledge.get('platform')}"
        elif learning.domain == LearningDomain.PLATFORM_OPTIMIZATION:
            return f"For {learning.knowledge.get('platform')}: {learning.knowledge.get('tactic')}"
        elif learning.domain == LearningDomain.FINANCIAL_STRATEGIES:
            return f"Financial strategy: {learning.knowledge.get('approach')} to achieve {learning.knowledge.get('target_outcome')}"
        else:
            return f"Learned insight: {learning.context}"

    # === Learning Analytics ===

    def update_learning_effectiveness(self, learning_id: str, outcome: Dict[str, Any]):
        """Update how effective a learning was based on real outcomes"""
        # Find the learning across all domains
        for domain in LearningDomain:
            key = f"learning:{domain.value}:{learning_id}"
            data = self.redis.get(key)
            if data:
                learning_dict = json.loads(data)

                # Update success rate and usage count
                old_success_rate = learning_dict.get('success_rate', 0.0)
                usage_count = learning_dict.get('usage_count', 0)

                # Calculate new success rate
                new_success = 1.0 if outcome.get('successful', False) else 0.0
                new_success_rate = (old_success_rate * usage_count + new_success) / (usage_count + 1)

                learning_dict['success_rate'] = new_success_rate
                learning_dict['usage_count'] = usage_count + 1
                learning_dict['last_updated'] = datetime.now().isoformat()

                # Add outcome to evidence
                if 'evidence' not in learning_dict:
                    learning_dict['evidence'] = []
                learning_dict['evidence'].append({
                    'outcome': outcome,
                    'timestamp': datetime.now().isoformat()
                })

                # Store updated learning
                self.redis.setex(key, 30 * 24 * 3600, json.dumps(learning_dict))
                break

    def get_agent_learning_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive learning statistics for an agent"""
        learning_ids = self.redis.smembers(f"agent_learnings:{agent_id}")

        stats = {
            'total_learnings': len(learning_ids),
            'domain_breakdown': {},
            'average_confidence': 0.0,
            'average_success_rate': 0.0,
            'most_used_learnings': [],
            'most_successful_learnings': []
        }

        all_learnings = []
        for learning_id in learning_ids:
            for domain in LearningDomain:
                key = f"learning:{domain.value}:{learning_id}"
                data = self.redis.get(key)
                if data:
                    learning_dict = json.loads(data)
                    all_learnings.append(learning_dict)

                    # Domain breakdown
                    domain_name = domain.value
                    if domain_name not in stats['domain_breakdown']:
                        stats['domain_breakdown'][domain_name] = 0
                    stats['domain_breakdown'][domain_name] += 1
                    break

        if all_learnings:
            stats['average_confidence'] = sum(l.get('confidence', 0) for l in all_learnings) / len(all_learnings)
            stats['average_success_rate'] = sum(l.get('success_rate', 0) for l in all_learnings) / len(all_learnings)

            # Most used and successful
            stats['most_used_learnings'] = sorted(all_learnings, key=lambda x: x.get('usage_count', 0), reverse=True)[:5]
            stats['most_successful_learnings'] = sorted(all_learnings, key=lambda x: x.get('success_rate', 0), reverse=True)[:5]

        return stats

    def get_system_learning_overview(self) -> Dict[str, Any]:
        """Get overview of all learning across the system"""
        overview = {
            'total_learnings_by_domain': {},
            'most_active_agents': {},
            'trending_contexts': {},
            'system_intelligence_level': 0.0
        }

        # Count learnings by domain
        for domain in LearningDomain:
            count = self.redis.scard(f"domain:{domain.value}")
            overview['total_learnings_by_domain'][domain.value] = count

        # Calculate system intelligence level
        total_learnings = sum(overview['total_learnings_by_domain'].values())
        diversity_score = len([d for d in overview['total_learnings_by_domain'].values() if d > 0]) / len(LearningDomain)
        overview['system_intelligence_level'] = min(total_learnings / 1000 * diversity_score, 1.0)

        return overview

# Global instance
multi_domain_learning = MultiDomainLearning()

# Example usage functions for agents
def agent_learns_market_trend(agent_id: str, platform: str, trend_data: Dict):
    """Helper for agents to learn market trends"""
    return multi_domain_learning.learn_market_trend(agent_id, platform, trend_data)

def agent_learns_from_proposal(agent_id: str, proposal_outcome: Dict):
    """Helper for agents to learn from proposal outcomes"""
    return multi_domain_learning.learn_successful_proposal(agent_id, proposal_outcome)

def agent_observes_user_behavior(agent_id: str, user_id: str, behavior: Dict):
    """Helper for agents to learn user behavior"""
    return multi_domain_learning.learn_user_behavior(agent_id, user_id, behavior)

def get_smart_recommendations(situation: str, user_context: Dict = None):
    """Get AI recommendations based on all learned knowledge"""
    return multi_domain_learning.get_recommendations_for_situation(situation, user_context)