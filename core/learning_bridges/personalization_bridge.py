"""
Personalization Feedback Bridge
Learns from user interactions to improve opportunity matching and personalization

Session 461: Extended to capture preferences from chat conversations, not just
opportunity interactions. Now learns from:
- Opportunity interactions (view, click, apply, etc.)
- Chat conversations (extracting preferences like "remote work", "AI jobs", etc.)
"""

import logging
import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Dict, List

logger = logging.getLogger(__name__)


# Preference extraction patterns - keywords that indicate user preferences
PREFERENCE_PATTERNS = {
    'work_style': {
        'remote': [r'\bremote\b', r'\bwork from home\b', r'\bwfh\b', r'\bfully remote\b'],
        'hybrid': [r'\bhybrid\b', r'\bflexible\b'],
        'onsite': [r'\bon-?site\b', r'\bin-?office\b', r'\bin person\b'],
    },
    'job_type': {
        'full_time': [r'\bfull[- ]?time\b', r'\bpermanent\b', r'\bfte\b'],
        'part_time': [r'\bpart[- ]?time\b'],
        'contract': [r'\bcontract\b', r'\bfreelance\b', r'\bgig\b', r'\bconsulting\b'],
        'freelance': [r'\bfreelance\b', r'\bindependent\b', r'\bself[- ]employed\b'],
    },
    'industry': {
        'tech': [r'\btech\b', r'\btechnology\b', r'\bsoftware\b', r'\bstartup\b'],
        'ai': [r'\bai\b', r'\bartificial intelligence\b', r'\bmachine learning\b', r'\bml\b', r'\bllm\b'],
        'finance': [r'\bfinance\b', r'\bfintech\b', r'\bbanking\b', r'\btrading\b'],
        'healthcare': [r'\bhealthcare\b', r'\bhealth\b', r'\bmedical\b', r'\bbiotech\b'],
        'crypto': [r'\bcrypto\b', r'\bblockchain\b', r'\bweb3\b', r'\bdefi\b'],
    },
    'skills': {
        'python': [r'\bpython\b'],
        'javascript': [r'\bjavascript\b', r'\bjs\b', r'\breact\b', r'\bnode\b', r'\btypescript\b'],
        'data': [r'\bdata\b', r'\banalytics\b', r'\bdata science\b'],
        'devops': [r'\bdevops\b', r'\baws\b', r'\bcloud\b', r'\bkubernetes\b', r'\bdocker\b'],
        'design': [r'\bdesign\b', r'\bui\b', r'\bux\b', r'\bfigma\b'],
    },
    'salary': {
        'high': [r'\$\d{3}k', r'\$\d{6,}', r'\bhigh paying\b', r'\btop salary\b'],
        'mention': [r'\$\d+', r'\bsalary\b', r'\bcompensation\b', r'\bpay\b'],
    },
    'experience_level': {
        'senior': [r'\bsenior\b', r'\blead\b', r'\bstaff\b', r'\bprincipal\b'],
        'mid': [r'\bmid[- ]?level\b', r'\b3-5 years\b', r'\bintermediate\b'],
        'junior': [r'\bjunior\b', r'\bentry[- ]?level\b', r'\bintern\b'],
    },
}


class PersonalizationFeedbackLoop:
    """
    Learns from user interactions to personalize content and opportunities.

    Session 461: Now learns from both:
    1. OpportunityInteraction signals (view, click, apply, etc.)
    2. ConversationMemory signals (chat messages that reveal preferences)
    """

    def process_conversation(self, conversation_memory):
        """
        Process a chat conversation to extract user preferences.

        Session 461: New method to learn from chat interactions.
        Extracts preferences like "I prefer remote work" or "looking for AI jobs"
        from the user's message text.
        """
        try:
            pass

            message = conversation_memory.message or ''
            user = conversation_memory.user

            if not message or len(message) < 5:
                return  # Skip very short messages

            # Extract preferences from the message
            extracted = self._extract_preferences_from_text(message)

            if not extracted:
                return  # No preferences detected

            logger.info(f"💡 Extracted preferences from chat: {extracted}")

            # Update user's chat-derived preferences
            self._update_chat_preferences(user, extracted, message)

            logger.info(f"✅ Chat preference learning complete for {user.username}")

        except Exception as e:
            logger.error(f"Error processing conversation for personalization: {e}", exc_info=True)

    def _extract_preferences_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract preference signals from text using pattern matching.

        Returns a dict of category -> list of detected preferences.
        """
        text_lower = text.lower()
        extracted = {}

        for category, preferences in PREFERENCE_PATTERNS.items():
            detected = []
            for pref_name, patterns in preferences.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        detected.append(pref_name)
                        break  # Found this preference, move to next

            if detected:
                extracted[category] = list(set(detected))  # Dedupe

        return extracted

    def _update_chat_preferences(self, user, extracted: Dict[str, List[str]], original_text: str):
        """Update user preferences based on chat-extracted signals."""
        from core.models_unified_system import UserAgentLearning
        from django.utils import timezone

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=user,
            agent_name='SystemIntelligence',
            learning_domain='chat_preferences',
            defaults={
                'learning_content': {
                    'work_style': {},
                    'job_type': {},
                    'industry': {},
                    'skills': {},
                    'experience_level': {},
                    'extraction_history': []
                },
                'confidence_score': 0.3,  # Lower initial confidence for chat
                'learning_source': 'conversational'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}

        # Update each preference category
        for category, preferences in extracted.items():
            if category not in content:
                content[category] = {}

            for pref in preferences:
                if pref not in content[category]:
                    content[category][pref] = {'count': 0, 'last_mentioned': None}

                content[category][pref]['count'] += 1
                content[category][pref]['last_mentioned'] = timezone.now().isoformat()

        # Track extraction history (keep last 20)
        if 'extraction_history' not in content:
            content['extraction_history'] = []

        content['extraction_history'].append({
            'timestamp': timezone.now().isoformat(),
            'extracted': extracted,
            'message_preview': original_text[:100]
        })
        content['extraction_history'] = content['extraction_history'][-20:]

        learning.learning_content = content

        # Increase confidence slightly with each extraction
        if learning.confidence_score < 0.9:
            learning.confidence_score = min(0.9, learning.confidence_score + 0.05)

        learning.save()

    def process_interaction(self, interaction):
        """Process opportunity interaction for personalization learning"""

        logger.info(f"👤 Processing interaction: {interaction.interaction_type}")

        try:
            from core.models_unified_system import Opportunity

            # Get the opportunity
            opportunity = Opportunity.objects.filter(id=interaction.opportunity_id).first()
            if not opportunity:
                return

            # Extract interaction patterns
            patterns = self._extract_interaction_patterns(opportunity, interaction)

            # Update user preference learning
            self._update_user_preferences(interaction.user, patterns, interaction.interaction_type)

            # Update opportunity type preferences
            if hasattr(opportunity, 'opportunity_type'):
                self._update_opportunity_type_preferences(
                    interaction.user,
                    opportunity.opportunity_type,
                    interaction.interaction_type
                )

            logger.info(f"✅ Personalization learning complete")

        except Exception as e:
            logger.error(f"Error in personalization learning: {e}", exc_info=True)

    def _extract_interaction_patterns(self, opportunity, interaction) -> Dict:
        """Extract patterns from opportunity and interaction"""
        patterns = {
            'source': opportunity.source if hasattr(opportunity, 'source') else 'unknown',
            'opportunity_type': opportunity.opportunity_type if hasattr(opportunity, 'opportunity_type') else 'unknown',
            'salary_range': float(opportunity.potential_revenue) if hasattr(opportunity, 'potential_revenue') else 0,
            'match_score': opportunity.match_score if hasattr(opportunity, 'match_score') else 0,
            'interaction_type': interaction.interaction_type,
            'interaction_depth': self._calculate_interaction_depth(interaction.interaction_type)
        }

        # Extract metadata features
        if hasattr(opportunity, 'metadata') and isinstance(opportunity.metadata, dict):
            metadata = opportunity.metadata
            patterns['remote'] = metadata.get('remote', False)
            patterns['industry'] = metadata.get('industry', 'unknown')
            patterns['company_size'] = metadata.get('company_size', 'unknown')
            patterns['tech_stack'] = metadata.get('tech_stack', [])

        return patterns

    def _calculate_interaction_depth(self, interaction_type: str) -> int:
        """Calculate depth/engagement level of interaction"""
        depth_map = {
            'view': 1,
            'click': 2,
            'bookmark': 3,
            'apply': 4,
            'interview': 5,
            'accept': 6
        }
        return depth_map.get(interaction_type, 1)

    def _update_user_preferences(self, user, patterns: Dict, interaction_type: str):
        """Update user's opportunity preferences based on interactions"""
        from core.models_unified_system import UserAgentLearning

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=user,
            agent_name='SystemIntelligence',
            learning_domain='user_preferences',
            defaults={
                'learning_content': {
                    'preferred_sources': {},
                    'preferred_salary_range': {'min': 0, 'max': 0},
                    'preferred_industries': {},
                    'preferred_remote': None,
                    'interaction_history': []
                },
                'confidence_score': 0.5,
                'learning_source': 'behavioral'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}

        # Update source preferences
        source = patterns['source']
        if 'preferred_sources' not in content:
            content['preferred_sources'] = {}
        if source not in content['preferred_sources']:
            content['preferred_sources'][source] = {'count': 0, 'depth_sum': 0}

        content['preferred_sources'][source]['count'] += 1
        content['preferred_sources'][source]['depth_sum'] += patterns['interaction_depth']
        content['preferred_sources'][source]['avg_depth'] = (
            content['preferred_sources'][source]['depth_sum'] /
            content['preferred_sources'][source]['count']
        )

        # Update salary preferences (if applied or deeper engagement)
        if patterns['interaction_depth'] >= 3:
            salary = patterns['salary_range']
            if 'preferred_salary_range' not in content:
                content['preferred_salary_range'] = {'min': salary, 'max': salary, 'count': 0}

            current_min = content['preferred_salary_range'].get('min', 0)
            current_max = content['preferred_salary_range'].get('max', 0)

            # Adjust range based on interactions
            if salary > 0:
                content['preferred_salary_range']['min'] = min(current_min, salary) if current_min > 0 else salary
                content['preferred_salary_range']['max'] = max(current_max, salary)
                content['preferred_salary_range']['count'] = content['preferred_salary_range'].get('count', 0) + 1

        # Update industry preferences
        if 'industry' in patterns and patterns['industry'] != 'unknown':
            industry = patterns['industry']
            if 'preferred_industries' not in content:
                content['preferred_industries'] = {}
            if industry not in content['preferred_industries']:
                content['preferred_industries'][industry] = {'count': 0, 'depth_sum': 0}

            content['preferred_industries'][industry]['count'] += 1
            content['preferred_industries'][industry]['depth_sum'] += patterns['interaction_depth']

        # Track interaction history (keep last 50)
        if 'interaction_history' not in content:
            content['interaction_history'] = []
        content['interaction_history'].append({
            'type': interaction_type,
            'patterns': patterns,
            'depth': patterns['interaction_depth']
        })
        content['interaction_history'] = content['interaction_history'][-50:]

        learning.learning_content = content

        # Adjust confidence based on engagement
        if patterns['interaction_depth'] >= 3:
            learning.record_success()

        learning.save()

        logger.info(f"✅ Updated user preferences for {user.username}")

    def _update_opportunity_type_preferences(self, user, opportunity_type: str, interaction_type: str):
        """Update preferences for specific opportunity types"""
        from core.models_unified_system import UserAgentLearning

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=user,
            agent_name='SystemIntelligence',
            learning_domain=f'opportunity_type_{opportunity_type}',
            defaults={
                'learning_content': {
                    'interaction_count': 0,
                    'engagement_score': 0
                },
                'confidence_score': 0.5,
                'learning_source': 'behavioral'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['interaction_count'] = content.get('interaction_count', 0) + 1

        # Calculate engagement score
        depth = self._calculate_interaction_depth(interaction_type)
        current_score = content.get('engagement_score', 0)
        new_score = ((current_score * (content['interaction_count'] - 1)) + depth) / content['interaction_count']
        content['engagement_score'] = new_score

        learning.learning_content = content

        # High engagement increases confidence
        if depth >= 3:
            learning.record_success()

        learning.save()


# Global instance
personalization_feedback_loop = PersonalizationFeedbackLoop()


# Signal integration for OpportunityInteraction
try:
    from core.models_engagement_metrics import OpportunityInteraction

    @receiver(post_save, sender=OpportunityInteraction)
    def on_opportunity_interaction_for_personalization(sender, instance, created, **kwargs):
        """Learn from user interactions for personalization"""
        if created:
            try:
                personalization_feedback_loop.process_interaction(instance)
            except Exception as e:
                logger.error(f"Error in personalization learning signal: {e}", exc_info=True)
except ImportError:
    logger.warning("OpportunityInteraction model not found - personalization signals not registered")


# Session 461: Signal integration for ConversationMemory (chat preference extraction)
# Session 729: Extended to generate embeddings for semantic search
try:
    from core.models import ConversationMemory

    @receiver(post_save, sender=ConversationMemory)
    def on_conversation_for_personalization(sender, instance, created, **kwargs):
        """
        Extract preferences from chat conversations and generate embeddings.

        Session 461: Listens for new ConversationMemory entries and extracts
        user preferences like work style, industry interests, skills, etc.

        Session 729: Also generates embeddings for semantic search across
        conversation history.
        """
        if created:
            try:
                personalization_feedback_loop.process_conversation(instance)
            except Exception as e:
                logger.error(f"Error in conversation personalization signal: {e}", exc_info=True)

            # Session 729: Generate embedding for semantic search
            try:
                if not instance.embedding:
                    from core.services.memory_embedding_service import get_memory_embedding_service
                    service = get_memory_embedding_service()

                    # Build text from message and response for embedding
                    text = f"User: {instance.message}\nAssistant: {instance.response}"
                    embedding = service._generate_embedding(text)

                    if embedding:
                        instance.embedding = embedding
                        instance.save(update_fields=['embedding'])
                        logger.debug(f"✅ Generated embedding for ConversationMemory {instance.id}")
            except Exception as e:
                logger.debug(f"Embedding generation failed for ConversationMemory (non-critical): {e}")

    logger.info("✅ ConversationMemory personalization signal registered")
except ImportError:
    logger.warning("ConversationMemory model not found - chat personalization signals not registered")
