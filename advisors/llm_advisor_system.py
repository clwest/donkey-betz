"""
LLM-Powered Advisor System
==========================

This module enables all 25 legendary advisors (Warren Buffett, Cathie Wood, etc.)
to provide REAL AI-generated advice using their unique perspectives and expertise.

Each advisor:
1. Has a unique personality and expertise
2. Generates personalized advice via LLM
3. Maintains consistency with their real-world philosophy
4. Provides actionable recommendations
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.agents.ai_enforced_base import AIEnforcedAgent
from advisors.registry import advisor_registry
from core.llm_enforcer import get_llm_enforcer

logger = logging.getLogger(__name__)

# Session 461: Domain-to-Spider mappings for advisor intelligence
ADVISOR_DOMAIN_SPIDERS = {
    'investing': ['yahoo_finance', 'coindesk', 'financial_news', 'market_data', 'seeking_alpha'],
    'value_investing': ['yahoo_finance', 'financial_news', 'sec_filings', 'market_data', 'seeking_alpha'],
    'tech_investing': ['techcrunch', 'the_verge', 'wired', 'axios', 'yahoo_finance', 'coindesk'],
    'crypto': ['coindesk', 'cryptonews', 'etherscan_api', 'blockchain_news', 'defi_pulse'],
    'tech': ['techcrunch', 'the_verge', 'wired', 'mit_tech_review', 'axios', 'hackernews_api'],
    'startups': ['techcrunch', 'ycombinator', 'producthunt', 'indiegogo', 'kickstarter'],
    'venture_capital': ['techcrunch', 'crunchbase', 'ycombinator', 'producthunt'],
    'macro': ['financial_news', 'yahoo_finance', 'market_data', 'economic_data'],
    'innovation': ['techcrunch', 'mit_tech_review', 'wired', 'producthunt'],
    'entrepreneurship': ['techcrunch', 'ycombinator', 'producthunt', 'indiegogo', 'forbes'],
    'ai': ['techcrunch', 'the_verge', 'mit_tech_review', 'arxiv_ai', 'huggingface'],
    'blockchain': ['coindesk', 'etherscan_api', 'cryptonews', 'blockchain_news'],
    'general': ['techcrunch', 'financial_news', 'yahoo_finance', 'market_data'],
}


class LLMAdvisor(AIEnforcedAgent):
    """
    An advisor that provides real AI-generated advice in the style
    and expertise of legendary investors, entrepreneurs, and thought leaders.
    """

    def __init__(self, advisor_profile: Dict[str, Any], user=None):
        """Initialize with a specific advisor's profile"""
        # Get advisor details
        self.advisor_id = advisor_profile.get('id', 'unknown')
        self.advisor_profile = advisor_profile

        # Initialize parent with advisor name
        advisor_name = advisor_profile.get('name', self.advisor_id)
        super().__init__(agent_name=f"Advisor_{advisor_name}", user=user)

        # Load advisor-specific attributes
        self.title = advisor_profile.get('title', '')
        self.expertise_level = advisor_profile.get('expertise_level', 'expert')
        self.domain = advisor_profile.get('domain', 'general')
        self.specializations = advisor_profile.get('specializations', [])
        self.philosophy = advisor_profile.get('philosophy', '')
        self.famous_quotes = advisor_profile.get('famous_quotes', [])
        self.decision_framework = advisor_profile.get('decision_framework', {})
        self.net_worth = advisor_profile.get('net_worth', 0)
        self.notable_successes = advisor_profile.get('notable_successes', [])

        logger.info(f"🧠 Initialized LLM Advisor: {advisor_name}")
        logger.info(f"   Expertise: {self.expertise_level} in {self.domain}")

    def _get_domain_spider_intelligence(self, topic: str = "", hours: int = 168, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Session 461: Get fresh spider intelligence relevant to this advisor's domain.

        Each advisor has access to spider data from their area of expertise:
        - Warren Buffett gets financial/market data
        - Cathie Wood gets tech/innovation data
        - Elon Musk gets crypto/blockchain data
        - etc.

        Args:
            topic: The consultation topic (for additional filtering)
            hours: How far back to look (default 7 days)
            limit: Max items to return

        Returns:
            List of spider intelligence items relevant to advisor's domain
        """
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from datetime import timedelta

            cutoff = timezone.now() - timedelta(hours=hours)

            # Get spiders relevant to this advisor's domain
            domain = self.domain.lower().replace(' ', '_')
            spider_sources = ADVISOR_DOMAIN_SPIDERS.get(domain, ADVISOR_DOMAIN_SPIDERS['general'])

            # Also check specializations for additional spider sources
            for spec in self.specializations[:3]:
                spec_key = spec.lower().replace(' ', '_')
                if spec_key in ADVISOR_DOMAIN_SPIDERS:
                    spider_sources = list(set(spider_sources + ADVISOR_DOMAIN_SPIDERS[spec_key]))

            logger.info(f"🕷️ Fetching spider data for {self.advisor_profile['name']} (domain: {domain})")
            logger.info(f"   Sources: {spider_sources[:5]}...")

            # Query SpiderData for domain-relevant content
            query = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=spider_sources
            )

            # If topic provided, try to filter by relevance
            if topic:
                topic_words = [w.lower() for w in topic.split() if len(w) > 3]
                # Note: We can't do complex text search without full-text search
                # So we'll get all and filter in Python for now

            results = query.order_by('-created_at')[:limit * 2]  # Get extra to filter

            intelligence = []
            topic_lower = topic.lower() if topic else ""

            for item in results:
                # SpiderData stores data in raw_data or processed_data JSON fields
                raw_data = item.raw_data or {}
                processed_data = item.processed_data or {}

                title = raw_data.get('title') or processed_data.get('title') or 'Untitled'
                content = raw_data.get('description') or raw_data.get('content') or \
                          raw_data.get('summary') or processed_data.get('summary') or ''

                # Calculate relevance score based on topic match
                relevance = 0
                if topic_lower:
                    text_lower = (title + ' ' + content).lower()
                    for word in topic_lower.split():
                        if len(word) > 3 and word in text_lower:
                            relevance += 1

                intelligence.append({
                    'title': title[:100] if title else 'Untitled',
                    'content': content[:400] if content else '',
                    'source': item.spider_name,
                    'url': item.source_url or raw_data.get('url') or raw_data.get('link') or '',
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'relevance': relevance,
                })

            # Sort by relevance (if topic provided) and limit
            if topic:
                intelligence.sort(key=lambda x: x['relevance'], reverse=True)

            final_intelligence = intelligence[:limit]
            logger.info(f"✅ Found {len(final_intelligence)} spider intelligence items for {self.advisor_profile['name']}")

            return final_intelligence

        except ImportError as e:
            logger.warning(f"Could not import SpiderData model: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching spider intelligence for advisor: {e}")
            return []

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Implementation of abstract execute method from AIEnforcedAgent.
        Routes to provide_consultation for advisors.
        """
        topic = kwargs.get('topic', kwargs.get('task', 'General consultation'))
        context = kwargs.get('context', {})
        consultation_type = kwargs.get('consultation_type', 'strategic')

        return self.provide_consultation(topic, context, consultation_type)

    def provide_consultation(self,
                           topic: str,
                           context: Dict[str, Any],
                           consultation_type: str = "strategic") -> Dict[str, Any]:
        """
        Provide real AI-generated consultation in this advisor's style.

        This is the MAIN method that makes advisors provide real advice.
        """
        try:
            # Build advisor-specific prompt
            prompt = self._build_advisor_prompt(topic, context, consultation_type)

            # Generate response using REAL AI with advisor's personality
            logger.info(f"🎓 {self.advisor_profile['name']} providing consultation...")

            advice = self.generate_ai_text(
                prompt=prompt,
                context=self._build_context_string(context),
                task_type=f"advisor_{consultation_type}",
                max_tokens=1500,  # Advisors give detailed advice
                temperature=0.7,  # Balanced creativity and consistency
                personalize=True  # Include user context
            )

            # Extract key recommendations and action items
            recommendations = self._extract_recommendations(advice)
            action_items = self._extract_action_items(advice)

            # Structure the consultation response
            result = {
                'success': True,
                'advisor': self.advisor_profile['name'],
                'advisor_id': self.advisor_id,
                'title': self.title,
                'expertise_level': self.expertise_level,
                'consultation_type': consultation_type,
                'topic': topic,
                'advice': advice,
                'recommendations': recommendations,
                'action_items': action_items,
                'philosophy_applied': self.philosophy[:200] if self.philosophy else '',
                'ai_generated': True,
                'tokens_used': self.ai_tokens_used,
                'cost': self.ai_cost,
                'timestamp': datetime.now().isoformat()
            }

            # Store in memory if user context exists
            if self.user:
                self.store_agent_memory(
                    memory_type='advisor_consultation',
                    content=f"{self.advisor_profile['name']} advised on {topic}: {advice[:300]}",
                    importance=9,
                    advisor_id=self.advisor_id,
                    topic=topic
                )

            logger.info(f"✅ {self.advisor_profile['name']} consultation complete ({self.ai_tokens_used} tokens)")
            return result

        except Exception as e:
            logger.error(f"❌ Advisor consultation failed: {e}")
            return {
                'success': False,
                'advisor': self.advisor_profile['name'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _build_advisor_prompt(self, topic: str, context: Dict[str, Any], consultation_type: str) -> str:
        """Build a prompt that captures this advisor's unique perspective"""

        # Session 461: Get fresh spider intelligence relevant to this advisor
        spider_intelligence = self._get_domain_spider_intelligence(topic=topic, hours=168, limit=5)

        # Start with advisor identity and philosophy
        prompt = f"""You are {self.advisor_profile['name']}, {self.title}.

Your expertise: {self.expertise_level} level expert in {self.domain}
Specializations: {', '.join(self.specializations[:5])}
Your investment/business philosophy: {self.philosophy}
Your net worth: ${self.net_worth:,} (demonstrating your success)

Notable successes:
{chr(10).join('- ' + s for s in self.notable_successes[:3])}

You are providing {consultation_type} consultation on: {topic}

Context:
{json.dumps(context, indent=2) if context else 'General consultation requested'}
"""

        # Session 461: Add fresh spider intelligence if available
        if spider_intelligence:
            prompt += f"""

FRESH MARKET INTELLIGENCE (from your domain sources):
The following recent data is from sources relevant to your expertise. Consider this fresh intelligence when providing advice:
"""
            for idx, intel in enumerate(spider_intelligence[:5], 1):
                prompt += f"""
{idx}. {intel['title']}
   Source: {intel['source']}
   {intel['content'][:200]}...
"""
            prompt += """
Use this fresh intelligence to inform your advice where relevant.
"""

        prompt += f"""
Instructions:
1. Provide advice that aligns with your known philosophy and approach
2. Reference your real-world experience and successes when relevant
3. Be specific and actionable in your recommendations
4. Maintain your authentic voice and perspective
5. Include 3-5 concrete recommendations
6. Provide clear action items the user can implement

Remember to speak as {self.advisor_profile['name']} would actually speak, with their characteristic insights and wisdom.
"""

        # Add specific examples for legendary advisors
        if 'Warren Buffett' in self.advisor_profile['name']:
            prompt += "\n\nEmphasize value investing, long-term thinking, and the importance of understanding what you invest in. Reference your Berkshire Hathaway experience."

        elif 'Cathie Wood' in self.advisor_profile['name']:
            prompt += "\n\nFocus on disruptive innovation, exponential growth technologies, and long-term transformation. Reference ARK Invest's research and your tech predictions."

        elif 'Ray Dalio' in self.advisor_profile['name']:
            prompt += "\n\nDiscuss principles-based decision making, economic cycles, and risk parity. Reference Bridgewater's approach and your 'Principles' philosophy."

        elif 'Peter Thiel' in self.advisor_profile['name']:
            prompt += "\n\nEmphasize contrarian thinking, monopoly building, and going from 0 to 1. Reference PayPal, Palantir, and your venture capital insights."

        elif 'Naval Ravikant' in self.advisor_profile['name']:
            prompt += "\n\nFocus on leverage, specific knowledge, and wealth creation. Include your philosophical insights on happiness and decision-making."

        # Add famous quotes if available
        if self.famous_quotes:
            prompt += f"\n\nFeel free to reference your famous quotes like: '{self.famous_quotes[0]}'"

        return prompt

    def _build_context_string(self, context: Dict[str, Any]) -> str:
        """Convert context to readable string"""
        if not context:
            return "General consultation"

        parts = []
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                parts.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                parts.append(f"{key}: {value}")

        return "\n".join(parts)

    def _extract_recommendations(self, advice: str) -> List[str]:
        """Extract key recommendations from advice"""
        recommendations = []

        # Look for numbered lists or bullet points
        lines = advice.split('\n')
        for line in lines:
            line = line.strip()
            # Check for numbered items (1., 2., etc.) or bullets
            if (line and (line[0].isdigit() and '.' in line[:3]) or
                line.startswith('-') or line.startswith('•') or
                line.lower().startswith('recommendation')):

                # Clean and add the recommendation
                clean_line = line.lstrip('0123456789.-•* ').strip()
                if clean_line and len(clean_line) > 10:
                    recommendations.append(clean_line)

        # If no structured recommendations found, extract key sentences
        if not recommendations:
            sentences = advice.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['recommend', 'suggest', 'should', 'must', 'important']):
                    clean = sentence.strip()
                    if clean and len(clean) > 20:
                        recommendations.append(clean)

        return recommendations[:5]  # Return top 5 recommendations

    def _extract_action_items(self, advice: str) -> List[str]:
        """Extract actionable items from advice"""
        action_items = []

        # Look for action-oriented phrases
        lines = advice.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if any(word in line_lower for word in ['action:', 'step', 'to do:', 'task:', 'implement', 'execute']):
                clean = line.strip().lstrip('•-*123456789. ')
                if clean and len(clean) > 10:
                    action_items.append(clean)

        # Also look for imperative sentences
        sentences = advice.split('.')
        for sentence in sentences:
            words = sentence.strip().split()
            if words and words[0].lower() in ['create', 'build', 'develop', 'analyze', 'research', 'invest', 'start', 'focus']:
                if len(sentence.strip()) > 20:
                    action_items.append(sentence.strip())

        return action_items[:5]  # Return top 5 action items


class LLMAdvisorNetwork:
    """
    Network that manages all LLM-powered advisors and routes consultations.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.advisor_registry = advisor_registry
        self.llm_enforcer = get_llm_enforcer()
        self.consultation_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0

        # Cache of active advisor instances
        self.active_advisors = {}

        logger.info("🌟 LLM Advisor Network initialized")
        logger.info(f"   Managing {len(self.advisor_registry.list_advisors())} legendary advisors")

        self._initialized = True

    def get_advisor(self, advisor_id: str, user=None) -> Optional[LLMAdvisor]:
        """Get or create an LLM advisor instance"""

        # Check cache first
        cache_key = f"{advisor_id}_{user.id if user else 'anonymous'}"
        if cache_key in self.active_advisors:
            return self.active_advisors[cache_key]

        # Get advisor profile from registry
        advisor_profile = self.advisor_registry.get_advisor(advisor_id)
        if not advisor_profile:
            logger.error(f"Advisor {advisor_id} not found")
            return None

        # Create LLM advisor
        llm_advisor = LLMAdvisor(advisor_profile.__dict__, user=user)
        self.active_advisors[cache_key] = llm_advisor

        return llm_advisor

    def request_consultation(self,
                           advisor_id: str,
                           topic: str,
                           context: Dict[str, Any] = None,
                           consultation_type: str = "strategic",
                           user=None) -> Dict[str, Any]:
        """
        Request consultation from a specific advisor.

        This is the main entry point for all advisor consultations.
        """
        try:
            # Get the advisor
            advisor = self.get_advisor(advisor_id, user)
            if not advisor:
                return {
                    'success': False,
                    'error': f'Advisor {advisor_id} not found'
                }

            # Get consultation
            result = advisor.provide_consultation(
                topic=topic,
                context=context or {},
                consultation_type=consultation_type
            )

            # Track metrics
            if result['success']:
                self.consultation_count += 1
                self.total_tokens += result.get('tokens_used', 0)
                self.total_cost += result.get('cost', 0)

                logger.info(f"📊 Consultation #{self.consultation_count} complete")
                logger.info(f"   Total tokens: {self.total_tokens}")
                logger.info(f"   Total cost: ${self.total_cost:.4f}")

            return result

        except Exception as e:
            logger.error(f"Consultation request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'advisor_id': advisor_id,
                'timestamp': datetime.now().isoformat()
            }

    def get_multi_advisor_panel(self,
                              topic: str,
                              advisor_ids: List[str],
                              context: Dict[str, Any] = None,
                              user=None) -> Dict[str, Any]:
        """
        Get advice from multiple advisors on the same topic.

        This creates a "panel discussion" effect with different perspectives.
        """
        panel_results = {
            'success': True,
            'topic': topic,
            'advisors': [],
            'consensus_recommendations': [],
            'diverse_perspectives': [],
            'timestamp': datetime.now().isoformat()
        }

        all_recommendations = []

        for advisor_id in advisor_ids[:5]:  # Limit to 5 advisors max
            result = self.request_consultation(
                advisor_id=advisor_id,
                topic=topic,
                context=context,
                user=user
            )

            if result['success']:
                panel_results['advisors'].append({
                    'name': result['advisor'],
                    'title': result.get('title', ''),
                    'advice_summary': result['advice'][:500] + '...',
                    'key_recommendation': result['recommendations'][0] if result['recommendations'] else ''
                })

                all_recommendations.extend(result['recommendations'])

        # Find consensus (recommendations that appear multiple times)
        from collections import Counter
        recommendation_counts = Counter(all_recommendations)
        panel_results['consensus_recommendations'] = [
            rec for rec, count in recommendation_counts.most_common(3)
            if count > 1
        ]

        return panel_results

    def find_best_advisor_for_topic(self, topic: str) -> Optional[str]:
        """Find the best advisor for a given topic"""

        best_advisor_id = None
        best_score = 0

        topic_lower = topic.lower()

        for advisor in self.advisor_registry.list_advisors():
            score = 0

            # Check domain match
            if advisor.get('domain', '').lower() in topic_lower:
                score += 3

            # Check specialization match
            for spec in advisor.get('specializations', []):
                if spec.lower() in topic_lower:
                    score += 2

            # Boost legendary advisors
            if advisor.get('expertise_level') == 'legend':
                score += 1

            if score > best_score:
                best_score = score
                best_advisor_id = advisor.get('id')

        return best_advisor_id

    def get_consultation_stats(self) -> Dict[str, Any]:
        """Get consultation statistics"""
        return {
            'total_consultations': self.consultation_count,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost,
            'average_tokens': self.total_tokens / max(1, self.consultation_count),
            'average_cost': self.total_cost / max(1, self.consultation_count),
            'advisors_available': len(self.advisor_registry.list_advisors()),
            'legendary_advisors': len([a for a in self.advisor_registry.list_advisors()
                                     if a.get('expertise_level') == 'legend'])
        }


# Global network instance
_network = None

def get_advisor_network() -> LLMAdvisorNetwork:
    """Get the global advisor network instance"""
    global _network
    if _network is None:
        _network = LLMAdvisorNetwork()
    return _network


# Convenience function for quick consultation
def get_advisor_advice(advisor_name: str,
                      topic: str,
                      context: Dict[str, Any] = None,
                      user=None) -> str:
    """
    Quick function to get advice from a specific advisor.

    Args:
        advisor_name: Name or ID of the advisor
        topic: What to get advice about
        context: Additional context
        user: User object for personalization

    Returns:
        The advisor's advice as a string
    """
    network = get_advisor_network()

    # Find advisor by name
    advisor_id = None
    for advisor in advisor_registry.list_advisors():
        if advisor_name.lower() in advisor.get('name', '').lower():
            advisor_id = advisor.get('id')
            break

    if not advisor_id:
        return f"Advisor '{advisor_name}' not found"

    result = network.request_consultation(
        advisor_id=advisor_id,
        topic=topic,
        context=context,
        user=user
    )

    if result['success']:
        return result['advice']
    else:
        return f"Consultation failed: {result.get('error', 'Unknown error')}"


if __name__ == "__main__":
    # Test the LLM advisor system
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
    django.setup()

    print("\n🧪 Testing LLM Advisor System\n")

    network = get_advisor_network()

    # Test with Warren Buffett
    print("Requesting consultation from Warren Buffett...")

    result = network.request_consultation(
        advisor_id='warren_buffett',
        topic='Should I invest in AI companies given the current market conditions?',
        context={
            'investment_horizon': '10 years',
            'risk_tolerance': 'moderate',
            'current_portfolio': 'mostly index funds'
        }
    )

    if result.get('success'):
        print(f"\n🎓 {result['advisor']} says:")
        print(f"\n{result['advice'][:1000]}...")
        print(f"\n📌 Key Recommendations:")
        for rec in result.get('recommendations', [])[:3]:
            print(f"   • {rec}")
        print(f"\n💰 Cost: ${result.get('cost', 0):.4f}")
    else:
        print(f"\n❌ Consultation failed: {result.get('error')}")

    # Test multi-advisor panel
    print("\n\nTesting Multi-Advisor Panel...")

    panel_result = network.get_multi_advisor_panel(
        topic='Building wealth through technology investments',
        advisor_ids=['warren_buffett', 'cathie_wood', 'naval_ravikant'],
        context={'budget': '$50,000', 'time_horizon': '5 years'}
    )

    if panel_result['success']:
        print("\n🎓 Advisor Panel Results:")
        for advisor in panel_result['advisors']:
            print(f"\n{advisor['name']} ({advisor['title']}):")
            print(f"   {advisor['key_recommendation']}")

        if panel_result['consensus_recommendations']:
            print("\n🤝 Consensus Recommendations:")
            for rec in panel_result['consensus_recommendations']:
                print(f"   • {rec}")

    # Show stats
    stats = network.get_consultation_stats()
    print(f"\n📊 Network Stats:")
    print(f"   Total consultations: {stats['total_consultations']}")
    print(f"   Total cost: ${stats['total_cost']:.4f}")
    print(f"   Legendary advisors: {stats['legendary_advisors']}")