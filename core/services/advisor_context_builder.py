"""
Advisor Context Builder Service
Session 744 Phase 4: Auto-inject advisor wisdom into agent prompts.

This service:
1. Maps agent types to relevant advisor domains
2. Queries the AdvisorRegistry for matching legendary advisors
3. Extracts decision frameworks and wisdom for the task
4. Formats advisor insights for prompt injection

The goal is to make agents aware of advisor expertise,
so a stock analysis task gets Warren Buffett's wisdom injected,
or a marketing task gets Gary Vee's frameworks.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AdvisorContextBuilder:
    """
    Session 744 Phase 4: Automatically builds advisor context for agents.

    Usage:
        from core.services.advisor_context_builder import get_advisor_context_builder

        builder = get_advisor_context_builder()
        context = builder.build_context_for_agent(
            agent_name='StockAnalystAgent',
            task='Analyze Apple stock for long-term value'
        )
    """

    # Map agent patterns to advisor domains
    # Format: agent_pattern -> list of advisor domain values
    AGENT_ADVISOR_MAPPINGS = {
        # Financial/Investment agents
        'stock': ['investment_strategy', 'risk_management', 'financial_planning'],
        'market_intelligence': ['investment_strategy', 'risk_management'],
        'prediction_market': ['investment_strategy', 'sports_analytics'],
        'sports_odds': ['sports_analytics', 'risk_management'],
        'arbitrage': ['investment_strategy', 'financial_planning'],

        # Crypto/Blockchain agents
        'blockchain': ['crypto_analysis', 'risk_management', 'technical_architecture'],
        'whale_watcher': ['crypto_analysis', 'investment_strategy'],
        'crypto': ['crypto_analysis', 'investment_strategy'],

        # Business/Strategy agents
        'cto': ['technical_architecture', 'ai_ml_strategy', 'product_development'],
        'coo': ['operations_management', 'business_strategy'],
        'business': ['business_strategy', 'startup_consulting'],
        'competitor': ['business_strategy', 'marketing_strategy'],
        'customer_research': ['marketing_strategy', 'sales_optimization'],

        # Marketing/Content agents
        'marketing': ['marketing_strategy', 'content_strategy', 'sales_optimization'],
        'social_media': ['marketing_strategy', 'content_strategy'],
        'content_strategy': ['content_strategy', 'marketing_strategy'],
        'content_writer': ['content_strategy', 'marketing_strategy'],
        'seo': ['marketing_strategy', 'content_strategy'],
        'brand': ['marketing_strategy', 'business_strategy'],

        # Creative agents
        'image': ['content_strategy', 'product_development'],
        'video': ['content_strategy', 'product_development'],
        'creative_director': ['content_strategy', 'marketing_strategy'],
        'podcast': ['content_strategy', 'marketing_strategy'],

        # Research/Analysis agents
        'research': ['ai_ml_strategy', 'data_strategy', 'business_strategy'],
        'trend_analysis': ['business_strategy', 'data_strategy'],
        'opportunity': ['business_strategy', 'startup_consulting'],

        # Development agents
        'code': ['technical_architecture', 'ai_ml_strategy'],
        'developer': ['technical_architecture', 'product_development'],
        'devops': ['technical_architecture', 'cybersecurity'],
        'security': ['cybersecurity', 'technical_architecture'],

        # Legal agents
        'legal': ['legal_counsel', 'regulatory_compliance', 'intellectual_property'],

        # Career/Personal agents
        'career': ['career_coaching', 'leadership_development', 'negotiation_strategy'],
        'personal': ['career_coaching', 'leadership_development'],

        # Default mapping
        'default': ['business_strategy', 'ai_ml_strategy'],
    }

    # Map advisor IDs to their key wisdom/decision frameworks
    ADVISOR_WISDOM = {
        'warren_buffett_advisor': {
            'key_principles': [
                'Invest in businesses you understand (circle of competence)',
                'Look for economic moats - sustainable competitive advantages',
                'Always demand a margin of safety',
                'Be fearful when others are greedy, greedy when others are fearful',
                'Focus on long-term intrinsic value, not short-term price movements'
            ],
            'frameworks': ['intrinsic_value', 'margin_of_safety', 'circle_of_competence'],
            'style': 'patient value investor',
        },
        'cathie_wood_advisor': {
            'key_principles': [
                'Focus on disruptive innovation across converging technologies',
                'Use Wright\'s Law - costs decline predictably with cumulative production',
                'Long time horizons (5-10 years) for innovation investments',
                'Embrace volatility as opportunity in high-growth stocks',
                'AI, genomics, energy storage, robotics, and blockchain are key themes'
            ],
            'frameworks': ['disruptive_innovation', 'wrights_law', 'convergence'],
            'style': 'innovation-focused growth investor',
        },
        'ray_dalio_advisor': {
            'key_principles': [
                'The economy is a machine - understand the cycles',
                'Diversification is the only free lunch in investing',
                'Pain + Reflection = Progress',
                'Radical transparency and idea meritocracy',
                'All Weather portfolio - balance across economic environments'
            ],
            'frameworks': ['all_weather', 'economic_machine', 'principles'],
            'style': 'systematic macro investor',
        },
        'elon_musk_advisor': {
            'key_principles': [
                'First principles thinking - break problems to fundamentals',
                'Set audacious goals and work backwards',
                'Vertical integration for control and efficiency',
                'Move fast and iterate - perfection is the enemy of done',
                'Physics is the law, everything else is a recommendation'
            ],
            'frameworks': ['first_principles', 'vertical_integration', '10x_thinking'],
            'style': 'audacious innovator',
        },
        'gary_vaynerchuk_advisor': {
            'key_principles': [
                'Jab, jab, jab, right hook - give value before asking',
                'Day trade attention - be where the eyeballs are',
                'Document, don\'t create - authenticity wins',
                'Speed and volume matter - create massive amounts of content',
                'The brand is the moat in the modern economy'
            ],
            'frameworks': ['jab_jab_right_hook', 'attention_arbitrage', 'personal_brand'],
            'style': 'aggressive content marketer',
        },
        'billy_beane_advisor': {
            'key_principles': [
                'Data over intuition - let statistics guide decisions',
                'Find market inefficiencies and exploit them',
                'On-base percentage matters more than batting average',
                'Embrace statistical arbitrage - find undervalued assets',
                'Process over outcomes - right decisions can have bad results'
            ],
            'frameworks': ['moneyball', 'statistical_arbitrage', 'expected_value'],
            'style': 'data-driven decision maker',
        },
        'haralabos_voulgaris_advisor': {
            'key_principles': [
                'The line is wrong more often than you think',
                'Live betting reveals hidden information',
                'Regression models must account for human factors',
                'Bankroll management is more important than picks',
                'Expected value over win rate'
            ],
            'frameworks': ['live_adjustments', 'regression_models', 'kelly_criterion'],
            'style': 'quantitative sports bettor',
        },
        'chris_voss_advisor': {
            'key_principles': [
                'Tactical empathy - understand their perspective first',
                'Mirroring builds rapport and extracts information',
                'Label emotions to defuse tension',
                'Never split the difference - creative solutions exist',
                '"No" is the start of negotiation, not the end'
            ],
            'frameworks': ['tactical_empathy', 'mirroring', 'calibrated_questions'],
            'style': 'empathetic negotiator',
        },
        'sam_altman_advisor': {
            'key_principles': [
                'Make something people want - nothing else matters',
                'Talk to users - they know what they need',
                'AI will transform every industry',
                'Think in power laws - the best companies are 1000x better',
                'Speed of iteration is everything in startups'
            ],
            'frameworks': ['power_law', 'user_research', 'rapid_iteration'],
            'style': 'tech startup accelerator',
        },
        'mr_beast_advisor': {
            'key_principles': [
                'Retention is everything - optimize the first 30 seconds',
                'Thumbnails and titles determine 80% of success',
                'Bigger is better - go massive with concepts',
                'Reinvest everything back into content',
                'Study analytics obsessively'
            ],
            'frameworks': ['retention_optimization', 'thumbnail_testing', 'viral_mechanics'],
            'style': 'viral content engineer',
        },
    }

    # Task keyword to advisor ID mappings
    TASK_KEYWORD_ADVISORS = {
        # Investment keywords
        'stock': ['warren_buffett_advisor', 'cathie_wood_advisor'],
        'invest': ['warren_buffett_advisor', 'ray_dalio_advisor'],
        'value': ['warren_buffett_advisor'],
        'growth': ['cathie_wood_advisor'],
        'portfolio': ['ray_dalio_advisor', 'warren_buffett_advisor'],
        'risk': ['ray_dalio_advisor'],

        # Tech keywords
        'ai': ['sam_altman_advisor', 'elon_musk_advisor'],
        'tech': ['elon_musk_advisor', 'sam_altman_advisor'],
        'startup': ['sam_altman_advisor'],
        'innovation': ['cathie_wood_advisor', 'elon_musk_advisor'],
        'scale': ['sam_altman_advisor'],

        # Marketing keywords
        'marketing': ['gary_vaynerchuk_advisor'],
        'content': ['mr_beast_advisor', 'gary_vaynerchuk_advisor'],
        'brand': ['gary_vaynerchuk_advisor'],
        'social': ['gary_vaynerchuk_advisor'],
        'viral': ['mr_beast_advisor'],
        'youtube': ['mr_beast_advisor'],

        # Sports/Betting keywords
        'betting': ['haralabos_voulgaris_advisor', 'billy_beane_advisor'],
        'sports': ['billy_beane_advisor', 'haralabos_voulgaris_advisor'],
        'odds': ['haralabos_voulgaris_advisor'],
        'analytics': ['billy_beane_advisor'],

        # Negotiation keywords
        'negotiate': ['chris_voss_advisor'],
        'deal': ['chris_voss_advisor'],
    }

    def __init__(self):
        self._advisor_registry = None

    @property
    def advisor_registry(self):
        """Lazy-load the AdvisorRegistry."""
        if self._advisor_registry is None:
            from advisors.registry import get_advisor_registry
            self._advisor_registry = get_advisor_registry()
        return self._advisor_registry

    def _get_agent_advisor_domains(self, agent_name: str) -> List[str]:
        """Determine which advisor domains are relevant for an agent."""
        agent_lower = agent_name.lower()

        for pattern, domains in self.AGENT_ADVISOR_MAPPINGS.items():
            if pattern in agent_lower:
                return domains

        return self.AGENT_ADVISOR_MAPPINGS['default']

    def _get_task_advisors(self, task: str) -> List[str]:
        """Get advisor IDs based on task keywords."""
        task_lower = task.lower()
        advisors = set()

        for keyword, advisor_ids in self.TASK_KEYWORD_ADVISORS.items():
            if keyword in task_lower:
                advisors.update(advisor_ids)

        return list(advisors)

    def build_context_for_agent(
        self,
        agent_name: str,
        task: str,
        max_advisors: int = 3
    ) -> Dict[str, Any]:
        """
        Build advisor context for an agent.

        Args:
            agent_name: Name of the agent
            task: Current task description
            max_advisors: Maximum number of advisors to include

        Returns:
            Dict with advisor insights and recommendations
        """
        try:
            context = {
                'agent_name': agent_name,
                'relevant_advisors': [],
                'advisor_insights': [],
                'decision_frameworks': [],
                'key_principles': [],
                'recommended_approach': '',
                'summary': '',
                'has_advice': False,
            }

            # Get advisor IDs from task keywords
            task_advisor_ids = self._get_task_advisors(task)

            # Get domains from agent type
            domains = self._get_agent_advisor_domains(agent_name)

            logger.debug(f"🧙 [Session 744] Building advisor context for {agent_name}")
            logger.debug(f"  Task advisor IDs: {task_advisor_ids}")
            logger.debug(f"  Agent domains: {domains}")

            # Collect advisors to consult
            advisors_to_use = []

            # Priority 1: Task-specific advisors
            for advisor_id in task_advisor_ids:
                advisor = self.advisor_registry.get_advisor(advisor_id)
                if advisor and advisor_id not in [a['id'] for a in advisors_to_use]:
                    advisors_to_use.append({
                        'id': advisor_id,
                        'advisor': advisor,
                        'source': 'task_keyword',
                        'relevance': 2.0
                    })

            # Priority 2: Domain-based advisors
            for domain in domains:
                domain_advisors = self.advisor_registry.list_advisors()
                for advisor in domain_advisors:
                    if str(advisor.id) not in [a['id'] for a in advisors_to_use] and advisor.domain.value == domain:
                        advisors_to_use.append({
                            'id': str(advisor.id),
                            'advisor': advisor,
                            'source': 'domain_match',
                            'relevance': 1.0
                        })

            # Sort by relevance and limit
            advisors_to_use.sort(key=lambda x: -x['relevance'])
            advisors_to_use = advisors_to_use[:max_advisors]

            # Build context from selected advisors
            all_principles = []
            all_frameworks = []

            for advisor_data in advisors_to_use:
                advisor = advisor_data['advisor']
                advisor_id = advisor_data['id']

                # Add to relevant advisors list
                context['relevant_advisors'].append({
                    'id': advisor_id,
                    'name': advisor.name,
                    'title': advisor.title,
                    'expertise_level': advisor.expertise_level.value,
                    'specializations': advisor.specializations[:3],
                })

                # Get wisdom from our curated mapping
                wisdom = self.ADVISOR_WISDOM.get(advisor_id, {})
                if wisdom:
                    principles = wisdom.get('key_principles', [])
                    frameworks = wisdom.get('frameworks', [])
                    style = wisdom.get('style', '')

                    all_principles.extend(principles[:3])  # Top 3 principles per advisor
                    all_frameworks.extend(frameworks)

                    context['advisor_insights'].append({
                        'advisor': advisor.name,
                        'style': style,
                        'key_principles': principles[:3],
                        'frameworks': frameworks,
                    })
                else:
                    # Fallback to advisor's decision frameworks from registry
                    all_frameworks.extend(advisor.decision_frameworks[:2])
                    context['advisor_insights'].append({
                        'advisor': advisor.name,
                        'style': f"{advisor.expertise_level.value} in {advisor.domain.value}",
                        'key_principles': [f"Expert in {', '.join(advisor.specializations[:2])}"],
                        'frameworks': advisor.decision_frameworks[:2],
                    })

            # Deduplicate and store
            context['decision_frameworks'] = list(set(all_frameworks))[:5]
            context['key_principles'] = all_principles[:7]  # Top 7 principles overall

            # Generate recommended approach based on advisors
            context['recommended_approach'] = self._generate_recommended_approach(
                advisors_to_use, task
            )

            # Build summary
            context['summary'] = self._build_advisor_summary(context)
            context['has_advice'] = bool(context['relevant_advisors'])

            if context['has_advice']:
                advisor_names = [a['name'] for a in context['relevant_advisors']]
                logger.info(
                    f"🧙 [Session 744] Advisor context built: "
                    f"{len(context['relevant_advisors'])} advisors ({', '.join(advisor_names[:2])})"
                )

            return context

        except Exception as e:
            logger.error(f"Failed to build advisor context for {agent_name}: {e}")
            return {
                'agent_name': agent_name,
                'relevant_advisors': [],
                'advisor_insights': [],
                'decision_frameworks': [],
                'key_principles': [],
                'recommended_approach': '',
                'summary': '',
                'has_advice': False,
                'error': str(e),
            }

    def _generate_recommended_approach(
        self,
        advisors: List[Dict],
        task: str
    ) -> str:
        """Generate a recommended approach based on advisor styles."""
        if not advisors:
            return ""

        styles = []
        for a in advisors[:2]:  # Top 2 advisors
            wisdom = self.ADVISOR_WISDOM.get(a['id'], {})
            if wisdom.get('style'):
                styles.append(wisdom['style'])

        if styles:
            return f"Approach this as a {' and '.join(styles)}."
        return ""

    def _build_advisor_summary(self, context: Dict[str, Any]) -> str:
        """Build a concise summary for prompt injection."""
        parts = []

        # Advisors consulted
        if context.get('relevant_advisors'):
            names = [a['name'].split(' (')[0] for a in context['relevant_advisors'][:2]]
            parts.append(f"Advisors: {', '.join(names)}")

        # Key frameworks
        if context.get('decision_frameworks'):
            frameworks = context['decision_frameworks'][:2]
            framework_names = [f.replace('_', ' ').title() for f in frameworks]
            parts.append(f"Frameworks: {', '.join(framework_names)}")

        return " | ".join(parts) if parts else ""

    def get_advisor_for_task(self, task: str) -> Optional[Dict[str, Any]]:
        """
        Quick method to get the best advisor for a task.

        Args:
            task: Task description

        Returns:
            Dict with best advisor details or None
        """
        try:
            best = self.advisor_registry.find_best_advisor(task)
            if best:
                wisdom = self.ADVISOR_WISDOM.get(best.id, {})
                return {
                    'id': str(best.id),
                    'name': best.name,
                    'title': best.title,
                    'key_principles': wisdom.get('key_principles', [])[:3],
                    'frameworks': wisdom.get('frameworks', best.decision_frameworks[:2]),
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get advisor for task: {e}")
            return None

    def build_summary(
        self,
        agent_name: str,
        task: str,
        max_chars: int = 100
    ) -> str:
        """
        Session 806: Build a compact summary of advisor wisdom.

        This method returns a single-line summary suitable for prompt injection
        with minimal token usage (~25 tokens vs ~150 for full context).

        Args:
            agent_name: Name of the agent
            task: The task being performed
            max_chars: Maximum characters for the summary

        Returns:
            Compact summary string like:
            "Advisors: Warren Buffett | Framework: Margin Of Safety | Key: Focus on..."
        """
        try:
            context = self.build_context_for_agent(agent_name, task)

            if not context.get('has_advice'):
                return ""

            # Use the built-in summary if available and short enough
            summary = context.get('summary', '')
            if summary and len(summary) <= max_chars:
                return summary

            # Build more compact summary
            parts = []

            # Advisor names (most important)
            advisors = context.get('relevant_advisors', [])
            if advisors:
                names = [a.get('name', '').split(' (')[0] for a in advisors[:1] if a.get('name')]
                if names:
                    parts.append(f"Advisor: {names[0]}")

            # Key framework
            frameworks = context.get('decision_frameworks', [])
            if frameworks:
                framework = frameworks[0].replace('_', ' ').title()
                parts.append(f"Use: {framework}")

            result = " | ".join(parts)

            if len(result) > max_chars:
                result = result[:max_chars - 3] + "..."

            logger.debug(f"🧙 [Session 806] Advisor summary: {len(result)} chars")
            return result

        except Exception as e:
            logger.warning(f"Failed to build advisor summary: {e}")
            return ""


# Singleton instance
_advisor_context_builder: Optional[AdvisorContextBuilder] = None


def get_advisor_context_builder() -> AdvisorContextBuilder:
    """Get the singleton AdvisorContextBuilder instance."""
    global _advisor_context_builder
    if _advisor_context_builder is None:
        _advisor_context_builder = AdvisorContextBuilder()
    return _advisor_context_builder
