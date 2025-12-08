"""
Agent-Advisor-ML Integration Bridge
Connects 102 Agents with 25+ Advisors and ML Pipeline for intelligent decision-making
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from django.db import transaction
from django.core.cache import cache

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
from intelligence.models.advisor_network import (
    Advisor, AdvisorCategory, AdvisorCollaboration, AdvisorVerification
)
from intelligence.services.advisor_network_service import AdvisorNetworkService
from ml.core.ml_engine import MLEngine, PatternPrediction, UserBehaviorProfile
from ml_intelligence.ml_service import MLService

logger = logging.getLogger(__name__)


@dataclass
class AgentAdvisorContext:
    """Context for agent-advisor collaboration"""
    agent_id: str
    agent_name: str
    task_description: str
    domain: str
    input_data: Dict[str, Any]
    required_confidence: float = 0.7
    max_advisors: int = 5
    use_ml_enhancement: bool = True


@dataclass
class CollaborativeDecision:
    """Result of agent-advisor-ML collaboration"""
    decision: str
    confidence: float
    reasoning: List[str]
    participating_advisors: List[str]
    ml_predictions: List[PatternPrediction]
    recommended_actions: List[Dict[str, Any]]
    risk_assessment: Dict[str, float]
    timestamp: datetime


class AgentAdvisorBridge:
    """
    Bridge connecting 102 Agents with 25+ Advisors and ML Pipeline

    This orchestrator enables:
    1. Agents to consult relevant advisors before execution
    2. Advisors to provide expertise to agent decisions
    3. ML Pipeline to enhance both agent and advisor intelligence
    4. Collaborative decision-making across the entire system
    """

    def __init__(self):
        self.advisor_service = AdvisorNetworkService()
        self.ml_service = MLService.get_instance()
        self.ml_engine = self.ml_service.engine if self.ml_service.is_available() else None
        self.logger = logging.getLogger(__name__)

    def get_agent_advisor_mapping(self) -> Dict[str, List[str]]:
        """
        Map agents to relevant advisors based on domain expertise
        Returns mapping of agent specialization to advisor categories
        """
        mapping = {
            # Sports betting agents → Sports advisors
            'sports_analysis': ['Sports Betting', 'Options Trading'],
            'odds_calculation': ['Sports Betting'],
            'arbitrage_detection': ['Sports Betting', 'Crypto Trading'],

            # Crypto agents → Crypto advisors
            'crypto_trading': ['Crypto Trading', 'Options Trading'],
            'defi_analysis': ['Crypto Trading'],
            'nft_valuation': ['Crypto Trading', 'Real Estate'],

            # Financial agents → Options/Real Estate advisors
            'options_trading': ['Options Trading'],
            'portfolio_management': ['Options Trading', 'Crypto Trading'],
            'real_estate_analysis': ['Real Estate'],

            # Research agents → All advisors
            'market_research': ['Sports Betting', 'Crypto Trading', 'Options Trading', 'Real Estate'],
            'pattern_recognition': ['Sports Betting', 'Crypto Trading', 'Options Trading'],
            'sentiment_analysis': ['Crypto Trading', 'Options Trading'],

            # General agents → Context-specific advisors
            'content_generation': [],  # Will use ML pipeline directly
            'data_analysis': ['Sports Betting', 'Crypto Trading'],
            'automation': [],  # Will use ML pipeline directly
        }

        return mapping

    def match_agent_to_advisors(
        self,
        agent: UnifiedAgentTemplate,
        task_context: str
    ) -> List[Advisor]:
        """
        Match an agent to relevant advisors based on:
        1. Agent specialization
        2. Task context
        3. Domain tags
        4. Current advisor availability
        """
        relevant_advisors = []

        # Get mapping
        mapping = self.get_agent_advisor_mapping()

        # Extract agent domain from specialization or domain_tags
        agent_domains = []
        if agent.specialization:
            for key in mapping.keys():
                if key in agent.specialization.lower():
                    agent_domains.extend(mapping[key])

        # Add domain tags if available
        if agent.domain_tags:
            for tag in agent.domain_tags:
                if 'sport' in tag.lower():
                    agent_domains.append('Sports Betting')
                elif 'crypto' in tag.lower() or 'bitcoin' in tag.lower():
                    agent_domains.append('Crypto Trading')
                elif 'option' in tag.lower():
                    agent_domains.append('Options Trading')
                elif 'real' in tag.lower() or 'estate' in tag.lower():
                    agent_domains.append('Real Estate')

        # Get unique domains
        agent_domains = list(set(agent_domains))

        # Fetch advisors from those domains
        for domain in agent_domains:
            try:
                category = AdvisorCategory.objects.get(name=domain)
                advisors = Advisor.objects.filter(
                    category=category,
                    is_available=True,
                    trust_score__gte=7.0
                ).order_by('-performance_rating')[:3]  # Top 3 per category

                relevant_advisors.extend(advisors)
            except AdvisorCategory.DoesNotExist:
                self.logger.warning(f"Advisor category not found: {domain}")

        return relevant_advisors

    def enhance_agent_with_ml(
        self,
        agent: UnifiedAgentTemplate,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance agent decision-making with ML predictions

        Returns:
        - Pattern predictions
        - User behavior insights
        - Cross-domain opportunities
        """
        if not self.ml_engine:
            return {
                'ml_available': False,
                'predictions': [],
                'confidence_adjustment': 1.0
            }

        enhancements = {
            'ml_available': True,
            'predictions': [],
            'confidence_adjustment': 1.0,
            'cross_domain_signals': []
        }

        try:
            # Get user behavior adjustment
            decision_data = {
                'domain': agent.specialization or 'GENERAL',
                'confidence': task_data.get('confidence', 0.5),
                'complexity': len(task_data.get('requirements', [])),
                'agent_name': agent.name
            }

            adjusted_confidence = self.ml_engine.analyze_user_decision_pattern(decision_data)
            enhancements['confidence_adjustment'] = adjusted_confidence

            # Check for cross-domain opportunities
            if 'market_data' in task_data:
                opportunities = self.ml_engine.detect_cross_domain_opportunity(
                    task_data['market_data']
                )
                enhancements['cross_domain_signals'] = [
                    {
                        'pattern': opp.pattern_type,
                        'confidence': opp.confidence,
                        'outcome': opp.predicted_outcome,
                        'signals': opp.cross_domain_signals
                    }
                    for opp in opportunities
                ]

            # Add pattern predictions if relevant
            if agent.specialization and 'sports' in agent.specialization.lower():
                if 'sports_data' in task_data and 'crypto_context' in task_data:
                    pattern = self.ml_engine.analyze_sports_to_crypto_pattern(
                        task_data['sports_data'],
                        task_data['crypto_context']
                    )
                    enhancements['predictions'].append({
                        'type': pattern.pattern_type,
                        'confidence': pattern.confidence,
                        'outcome': pattern.predicted_outcome,
                        'horizon': pattern.time_horizon
                    })

        except Exception as e:
            self.logger.error(f"ML enhancement failed: {e}")

        return enhancements

    def orchestrate_collaborative_decision(
        self,
        context: AgentAdvisorContext
    ) -> CollaborativeDecision:
        """
        Orchestrate a collaborative decision involving:
        1. Agent initial analysis
        2. Advisor consultations
        3. ML enhancement
        4. Consensus building
        """
        self.logger.info(f"Orchestrating decision for agent: {context.agent_name}")

        # Step 1: Get the agent
        try:
            agent = UnifiedAgentTemplate.objects.get(name=context.agent_name)
        except UnifiedAgentTemplate.DoesNotExist:
            self.logger.error(f"Agent not found: {context.agent_name}")
            return self._create_fallback_decision(context)

        # Step 2: Match advisors
        advisors = self.match_agent_to_advisors(agent, context.task_description)
        self.logger.info(f"Matched {len(advisors)} advisors for consultation")

        # Step 3: Get ML enhancements
        ml_enhancements = {}
        if context.use_ml_enhancement:
            ml_enhancements = self.enhance_agent_with_ml(agent, context.input_data)

        # Step 4: Collect advisor opinions
        advisor_opinions = []
        for advisor in advisors[:context.max_advisors]:
            opinion = self._get_advisor_opinion(advisor, context)
            if opinion:
                advisor_opinions.append(opinion)

        # Step 5: Build consensus
        decision = self._build_consensus(
            agent=agent,
            context=context,
            advisor_opinions=advisor_opinions,
            ml_enhancements=ml_enhancements
        )

        # Step 6: Record collaboration
        if advisor_opinions:
            self._record_collaboration(agent, advisors, decision)

        return decision

    def _get_advisor_opinion(
        self,
        advisor: Advisor,
        context: AgentAdvisorContext
    ) -> Optional[Dict[str, Any]]:
        """Get opinion from a single advisor"""
        try:
            # Cache key for advisor opinions
            cache_key = f"advisor_opinion_{advisor.id}_{context.agent_id}_{hash(context.task_description)}"
            cached_opinion = cache.get(cache_key)

            if cached_opinion:
                return cached_opinion

            opinion = {
                'advisor_id': advisor.id,
                'advisor_name': advisor.name,
                'expertise': advisor.expertise_areas,
                'confidence': advisor.performance_rating / 10.0,
                'recommendation': self._generate_recommendation(advisor, context),
                'risk_factors': self._assess_risks(advisor, context)
            }

            # Cache for 5 minutes
            cache.set(cache_key, opinion, 300)

            return opinion

        except Exception as e:
            self.logger.error(f"Failed to get advisor opinion: {e}")
            return None

    def _generate_recommendation(
        self,
        advisor: Advisor,
        context: AgentAdvisorContext
    ) -> str:
        """Generate recommendation based on advisor expertise"""
        # This would normally call the advisor's specific model/logic
        # For now, return structured recommendation

        if advisor.category.name == 'Sports Betting':
            return f"Based on {advisor.expertise_areas}, recommend analyzing team performance metrics and injury reports"
        elif advisor.category.name == 'Crypto Trading':
            return f"Monitor market volatility indicators and whale movements for optimal entry points"
        elif advisor.category.name == 'Options Trading':
            return f"Consider IV levels and theta decay in current market conditions"
        elif advisor.category.name == 'Real Estate':
            return f"Evaluate location trends and comparable sales data for accurate valuation"
        else:
            return f"Proceed with standard analysis based on {advisor.expertise_areas}"

    def _assess_risks(
        self,
        advisor: Advisor,
        context: AgentAdvisorContext
    ) -> Dict[str, float]:
        """Assess risks based on advisor expertise"""
        base_risks = {
            'market_risk': 0.3,
            'execution_risk': 0.2,
            'timing_risk': 0.4,
            'liquidity_risk': 0.25
        }

        # Adjust based on advisor's performance
        risk_multiplier = 2.0 - (advisor.performance_rating / 10.0)

        return {
            risk_type: min(value * risk_multiplier, 1.0)
            for risk_type, value in base_risks.items()
        }

    def _build_consensus(
        self,
        agent: UnifiedAgentTemplate,
        context: AgentAdvisorContext,
        advisor_opinions: List[Dict[str, Any]],
        ml_enhancements: Dict[str, Any]
    ) -> CollaborativeDecision:
        """Build consensus from all inputs"""

        # Calculate weighted confidence
        total_confidence = 0
        weights = []

        # Agent base confidence
        agent_confidence = agent.confidence_score or 0.5
        total_confidence += agent_confidence * 0.3  # 30% weight to agent

        # Advisor confidences
        if advisor_opinions:
            advisor_weight = 0.5 / len(advisor_opinions)  # 50% total weight to advisors
            for opinion in advisor_opinions:
                total_confidence += opinion['confidence'] * advisor_weight
        else:
            total_confidence += agent_confidence * 0.2  # Give agent more weight if no advisors

        # ML confidence adjustment
        if ml_enhancements.get('ml_available'):
            ml_adjustment = ml_enhancements.get('confidence_adjustment', 1.0)
            total_confidence *= ml_adjustment  # Apply ML adjustment

        # Build reasoning
        reasoning = [
            f"Agent {agent.name} initial assessment with confidence {agent_confidence:.2f}"
        ]

        for opinion in advisor_opinions:
            reasoning.append(
                f"Advisor {opinion['advisor_name']}: {opinion['recommendation']}"
            )

        if ml_enhancements.get('predictions'):
            for pred in ml_enhancements['predictions']:
                reasoning.append(
                    f"ML Prediction: {pred['outcome']} with {pred['confidence']:.2f} confidence"
                )

        # Build recommended actions
        actions = []

        # Add agent-specific action
        actions.append({
            'source': 'agent',
            'action': f"Execute {agent.name} with enhanced parameters",
            'priority': 1
        })

        # Add advisor recommendations
        for opinion in advisor_opinions:
            actions.append({
                'source': f"advisor_{opinion['advisor_name']}",
                'action': opinion['recommendation'],
                'priority': 2
            })

        # Add ML-suggested actions
        if ml_enhancements.get('cross_domain_signals'):
            for signal in ml_enhancements['cross_domain_signals']:
                actions.append({
                    'source': 'ml_pipeline',
                    'action': f"Monitor {signal['pattern']} for {signal['outcome']}",
                    'priority': 3
                })

        # Aggregate risk assessment
        risk_assessment = {}
        for opinion in advisor_opinions:
            for risk_type, risk_value in opinion.get('risk_factors', {}).items():
                if risk_type not in risk_assessment:
                    risk_assessment[risk_type] = []
                risk_assessment[risk_type].append(risk_value)

        # Average the risks
        final_risks = {
            risk_type: sum(values) / len(values) if values else 0.5
            for risk_type, values in risk_assessment.items()
        }

        # Build final decision
        decision_text = self._synthesize_decision(
            context=context,
            confidence=total_confidence,
            advisor_count=len(advisor_opinions),
            has_ml=ml_enhancements.get('ml_available', False)
        )

        return CollaborativeDecision(
            decision=decision_text,
            confidence=min(total_confidence, 1.0),  # Cap at 1.0
            reasoning=reasoning,
            participating_advisors=[op['advisor_name'] for op in advisor_opinions],
            ml_predictions=[
                PatternPrediction(
                    pattern_type=pred['type'],
                    confidence=pred['confidence'],
                    predicted_outcome=pred['outcome'],
                    time_horizon=pred.get('horizon', 'unknown'),
                    supporting_features={},
                    cross_domain_signals=[]
                )
                for pred in ml_enhancements.get('predictions', [])
            ],
            recommended_actions=actions[:10],  # Top 10 actions
            risk_assessment=final_risks,
            timestamp=datetime.now()
        )

    def _synthesize_decision(
        self,
        context: AgentAdvisorContext,
        confidence: float,
        advisor_count: int,
        has_ml: bool
    ) -> str:
        """Synthesize final decision text"""

        confidence_level = "high" if confidence > 0.8 else "moderate" if confidence > 0.6 else "low"

        decision_parts = [
            f"After collaborative analysis for {context.task_description}",
            f"with {advisor_count} expert advisors consulted"
        ]

        if has_ml:
            decision_parts.append("and ML-enhanced predictions")

        decision_parts.append(
            f"the recommended decision is to proceed with {confidence_level} confidence ({confidence:.2%})."
        )

        decision_parts.append(
            f"The agent {context.agent_name} should execute with enhanced parameters and continuous monitoring."
        )

        return " ".join(decision_parts)

    def _record_collaboration(
        self,
        agent: UnifiedAgentTemplate,
        advisors: List[Advisor],
        decision: CollaborativeDecision
    ):
        """Record the collaboration for learning"""
        try:
            with transaction.atomic():
                # Create collaboration record
                for advisor in advisors:
                    if advisor.name in decision.participating_advisors:
                        AdvisorCollaboration.objects.create(
                            lead_advisor=advisors[0] if advisors else advisor,
                            topic=f"Agent {agent.name} consultation",
                            description=decision.decision[:500],
                            outcome_summary=json.dumps({
                                'confidence': decision.confidence,
                                'risks': decision.risk_assessment,
                                'action_count': len(decision.recommended_actions)
                            }),
                            consensus_reached=decision.confidence > 0.7,
                            consensus_confidence=decision.confidence
                        )

                        # Record participation
                        # Note: You might want to add a many-to-many through table for this

        except Exception as e:
            self.logger.error(f"Failed to record collaboration: {e}")

    def _create_fallback_decision(
        self,
        context: AgentAdvisorContext
    ) -> CollaborativeDecision:
        """Create fallback decision when agent not found"""
        return CollaborativeDecision(
            decision="Proceeding with default execution path due to system constraints",
            confidence=0.5,
            reasoning=["Agent not found, using fallback logic"],
            participating_advisors=[],
            ml_predictions=[],
            recommended_actions=[{
                'source': 'system',
                'action': 'Execute with default parameters',
                'priority': 1
            }],
            risk_assessment={'execution_risk': 0.5},
            timestamp=datetime.now()
        )

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system integration status"""

        total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        total_advisors = Advisor.objects.filter(is_available=True).count()

        return {
            'integration_active': True,
            'total_agents': total_agents,
            'total_advisors': total_advisors,
            'ml_pipeline_available': self.ml_service.is_available(),
            'ml_models_loaded': len(self.ml_engine.models) if self.ml_engine else 0,
            'advisor_categories': list(
                AdvisorCategory.objects.values_list('name', flat=True)
            ),
            'recent_collaborations': AdvisorCollaboration.objects.count(),
            'average_confidence': AdvisorCollaboration.objects.filter(
                consensus_reached=True
            ).values_list('consensus_confidence', flat=True)[:10]
        }


# Singleton instance
agent_advisor_bridge = AgentAdvisorBridge()