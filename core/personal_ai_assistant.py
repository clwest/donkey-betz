"""
Enhanced Personal AI Assistant with User Learning
==================================================

This module implements a personal AI assistant that learns from user profiles,
tracks patterns, and provides increasingly personalized assistance over time.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg

from core.models import ExtendedUserProfile, JobApplication, UserEmbedding
from core.agent_context_middleware import AgentContextMiddleware
from core.agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
try:
    from ml.core.ml_engine import MLEngine
except ImportError:
    MLEngine = None
try:
    from self_awareness.embeddings import CodebaseEmbeddings
except ImportError:
    # Fallback if CodebaseEmbeddings is not available
    class CodebaseEmbeddings:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)
User = get_user_model()


class PersonalAIAssistant:
    """
    Personal AI Assistant that learns from user interactions and profile data
    to provide increasingly personalized assistance.
    """

    def __init__(self, user: User):
        self.user = user
        self.profile = self._get_or_create_profile()
        self.context_middleware = AgentContextMiddleware()
        # Session 1078: Lazy-load heavy objects — MLEngine (~800MB), CodebaseEmbeddings,
        # agent/advisor registries are NOT needed by get_personalized_context() and were
        # causing +1.1GB RSS spikes in rebuild_pa_context_task.
        self._agent_registry = None
        self._advisor_registry = None
        self._ml_engine = None
        self._embeddings = None
        self.learning_history = []
        self.session_context = {}

        # Learning parameters
        self.confidence_threshold = 0.7
        self.learning_rate = 0.1
        self.memory_window = 30  # days

        logger.info(f"Personal AI Assistant initialized for {user.username}")

    @property
    def agent_registry(self):
        if self._agent_registry is None:
            self._agent_registry = get_agent_registry()
        return self._agent_registry

    @property
    def advisor_registry(self):
        if self._advisor_registry is None:
            self._advisor_registry = get_advisor_registry()
        return self._advisor_registry

    @property
    def ml_engine(self):
        if self._ml_engine is None:
            self._ml_engine = MLEngine()
        return self._ml_engine

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = CodebaseEmbeddings()
        return self._embeddings

    def _get_or_create_profile(self) -> ExtendedUserProfile:
        """Get or create extended user profile."""
        profile, created = ExtendedUserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'full_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                'metadata': {'ai_assistant': {'initialized': datetime.now().isoformat()}}
            }
        )
        if created:
            logger.info(f"Created new extended profile for {self.user.username}")
        return profile

    def learn_from_interaction(self, message: str, response: str, context: Dict[str, Any]) -> None:
        """
        Learn from user interactions to improve future responses.

        Args:
            message: User's message
            response: Assistant's response
            context: Interaction context including intent, entities, sentiment
        """
        try:
            # Extract learning signals
            learning_data = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'response': response,
                'intent': context.get('intent'),
                'entities': context.get('entities', []),
                'sentiment': context.get('sentiment'),
                'confidence': context.get('confidence', 0.5),
                'topic': context.get('topic'),
                'action_taken': context.get('action_taken'),
                'feedback': context.get('feedback')
            }

            # Store in learning history
            self.learning_history.append(learning_data)

            # Update user embeddings for pattern recognition
            self._update_user_embeddings(learning_data)

            # Update profile metadata with patterns
            self._update_user_patterns(learning_data)

            logger.info(f"📚 Learned from interaction: {context.get('intent')} (confidence: {learning_data['confidence']:.2f})")

        except Exception as e:
            logger.error(f"Failed to learn from interaction: {e}")

    def _update_user_embeddings(self, learning_data: Dict[str, Any]) -> None:
        """Update user-specific embeddings for better personalization."""
        try:
            # Create embedding from the interaction
            embedding_text = f"{learning_data['message']} {learning_data.get('intent', '')}"

            # Store in UserEmbedding model
            UserEmbedding.objects.create(
                user=self.user,
                content=embedding_text,
                metadata=learning_data,
                confidence_score=learning_data.get('confidence', 0.5)
            )

            # Clean old embeddings (keep last N)
            old_date = datetime.now() - timedelta(days=self.memory_window)
            UserEmbedding.objects.filter(
                user=self.user,
                created_at__lt=old_date
            ).delete()

        except Exception as e:
            logger.error(f"Failed to update user embeddings: {e}")

    def _update_user_patterns(self, learning_data: Dict[str, Any]) -> None:
        """Update recognized patterns in user behavior."""
        try:
            metadata = self.profile.metadata or {}
            patterns = metadata.get('behavior_patterns', {})

            # Update intent frequency
            intent = learning_data.get('intent')
            if intent:
                intent_counts = patterns.get('intents', {})
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
                patterns['intents'] = intent_counts

            # Update topic interests
            topic = learning_data.get('topic')
            if topic:
                topic_counts = patterns.get('topics', {})
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
                patterns['topics'] = topic_counts

            # Update time patterns
            hour = datetime.now().hour
            time_patterns = patterns.get('active_hours', {})
            time_patterns[str(hour)] = time_patterns.get(str(hour), 0) + 1
            patterns['active_hours'] = time_patterns

            # Save patterns
            metadata['behavior_patterns'] = patterns
            metadata['last_pattern_update'] = datetime.now().isoformat()
            self.profile.metadata = metadata
            self.profile.save()

        except Exception as e:
            logger.error(f"Failed to update user patterns: {e}")

    def get_personalized_context(self) -> Dict[str, Any]:
        """
        Get comprehensive personalized context for the user.

        Returns:
            Dictionary containing user profile, patterns, and recommendations
        """
        # Get base context from middleware
        base_context = self.context_middleware.get_user_context(self.user)

        # Enhance with learned patterns
        metadata = self.profile.metadata or {}
        patterns = metadata.get('behavior_patterns', {})

        # Get recent interactions
        recent_embeddings = UserEmbedding.objects.filter(
            user=self.user
        ).order_by('-created_at')[:10]

        recent_interactions = [
            {
                'content': emb.content,
                'confidence': emb.confidence_score,
                'timestamp': emb.created_at.isoformat()
            }
            for emb in recent_embeddings
        ]

        # Get job application patterns
        job_apps = JobApplication.objects.filter(user=self.user)
        app_stats = {
            'total_applications': job_apps.count(),
            'success_rate': job_apps.filter(status='offer').count() / max(job_apps.count(), 1) * 100,
            'avg_match_score': job_apps.aggregate(Avg('match_score'))['match_score__avg'] or 0,
            'preferred_platforms': list(job_apps.values('platform').annotate(
                count=Count('id')
            ).order_by('-count')[:3])
        }

        # Build enhanced context
        enhanced_context = {
            **base_context,
            'learning': {
                'patterns': patterns,
                'recent_interactions': recent_interactions,
                'confidence_level': self._calculate_confidence_level(),
                'personalization_score': self._calculate_personalization_score()
            },
            'job_insights': app_stats,
            'recommendations': self._generate_recommendations(patterns),
            'assistant_memory': {
                'session_context': self.session_context,
                'interaction_count': len(self.learning_history),
                'last_interaction': self.learning_history[-1] if self.learning_history else None
            }
        }

        return enhanced_context

    def _calculate_confidence_level(self) -> float:
        """Calculate confidence level based on interaction history."""
        if not self.learning_history:
            return 0.0

        recent = self.learning_history[-10:]  # Last 10 interactions
        avg_confidence = sum(h.get('confidence', 0.5) for h in recent) / len(recent)

        # Boost confidence based on interaction count
        interaction_boost = min(len(self.learning_history) / 100, 0.2)

        return min(avg_confidence + interaction_boost, 1.0)

    def _calculate_personalization_score(self) -> float:
        """Calculate how well the assistant knows the user."""
        score = 0.0

        # Profile completeness
        if self.profile.profile_completeness:
            score += self.profile.profile_completeness * 0.3

        # Interaction history
        interaction_score = min(len(self.learning_history) / 50, 1.0)
        score += interaction_score * 0.3

        # Pattern recognition
        metadata = self.profile.metadata or {}
        patterns = metadata.get('behavior_patterns', {})
        pattern_score = min(len(patterns.get('intents', {})) / 10, 1.0)
        score += pattern_score * 0.2

        # Embedding count
        embedding_count = UserEmbedding.objects.filter(user=self.user).count()
        embedding_score = min(embedding_count / 100, 1.0)
        score += embedding_score * 0.2

        return min(score, 1.0)

    def _generate_recommendations(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on patterns."""
        recommendations = []

        # Recommend based on frequent intents
        top_intents = sorted(
            patterns.get('intents', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        for intent, count in top_intents:
            if intent == 'job_search' and count > 5:
                recommendations.append({
                    'type': 'action',
                    'priority': 'high',
                    'title': 'Optimize Job Search',
                    'description': 'You frequently search for jobs. Consider setting up automated alerts.',
                    'action': 'setup_job_alerts'
                })
            elif intent == 'skill_inquiry' and count > 3:
                recommendations.append({
                    'type': 'learning',
                    'priority': 'medium',
                    'title': 'Skill Development',
                    'description': 'Based on your interests, consider adding trending skills to your profile.',
                    'action': 'suggest_skills'
                })

        # Recommend based on profile gaps
        if self.profile.profile_completeness < 70:
            recommendations.append({
                'type': 'profile',
                'priority': 'high',
                'title': 'Complete Your Profile',
                'description': f'Your profile is {self.profile.profile_completeness:.0f}% complete. Complete it for better matches.',
                'action': 'complete_profile'
            })

        # Time-based recommendations
        active_hours = patterns.get('active_hours', {})
        if active_hours:
            peak_hour = max(active_hours.items(), key=lambda x: x[1])[0]
            recommendations.append({
                'type': 'scheduling',
                'priority': 'low',
                'title': 'Optimal Timing',
                'description': f'You\'re most active around {peak_hour}:00. Schedule important tasks for this time.',
                'action': 'optimize_schedule'
            })

        return recommendations

    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user message with personalized context and learning.

        Args:
            message: User's message
            context: Optional additional context

        Returns:
            Response dictionary with personalized response and metadata
        """
        # Get personalized context
        user_context = self.get_personalized_context()

        # Detect intent and entities
        intent_data = self._detect_intent(message)

        # Merge contexts
        full_context = {
            **user_context,
            **intent_data,
            **(context or {})
        }

        # Generate personalized response
        response_data = self._generate_response(message, full_context)

        # Learn from this interaction
        self.learn_from_interaction(message, response_data['response'], full_context)

        # Update session context
        self.session_context.update({
            'last_message': message,
            'last_intent': intent_data.get('intent'),
            'timestamp': datetime.now().isoformat()
        })

        return {
            'response': response_data['response'],
            'suggestions': response_data.get('suggestions', []),
            'actions': response_data.get('actions', []),
            'confidence': response_data.get('confidence', 0.5),
            'personalization': {
                'score': self._calculate_personalization_score(),
                'recommendations': user_context['recommendations'][:3]
            },
            'metadata': {
                'intent': intent_data.get('intent'),
                'entities': intent_data.get('entities'),
                'learning_applied': True,
                'interaction_count': len(self.learning_history)
            }
        }

    def _detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect intent and entities from message."""
        # Simple intent detection (can be enhanced with NLP)
        message_lower = message.lower()

        intent = 'general'
        entities = []
        confidence = 0.5

        # Job-related intents
        if any(word in message_lower for word in ['job', 'opportunity', 'position', 'apply', 'application']):
            intent = 'job_search'
            confidence = 0.8
        elif any(word in message_lower for word in ['salary', 'pay', 'compensation', 'money']):
            intent = 'salary_inquiry'
            confidence = 0.7
        elif any(word in message_lower for word in ['skill', 'learn', 'training', 'course']):
            intent = 'skill_inquiry'
            confidence = 0.7
        elif any(word in message_lower for word in ['profile', 'resume', 'cv']):
            intent = 'profile_management'
            confidence = 0.8
        elif any(word in message_lower for word in ['help', 'how', 'what', 'why']):
            intent = 'help'
            confidence = 0.6

        # Extract entities (simplified)
        if '$' in message:
            entities.append({'type': 'money', 'value': message})
        if any(word in message_lower for word in ['python', 'javascript', 'react', 'django']):
            entities.append({'type': 'skill', 'value': 'technology'})

        return {
            'intent': intent,
            'entities': entities,
            'confidence': confidence,
            'raw_message': message
        }

    def _generate_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized response based on context."""
        intent = context.get('intent', 'general')
        user_name = context.get('first_name', 'there')

        responses = {
            'job_search': {
                'response': f"Hi {user_name}! I can help you find opportunities that match your profile. Based on your skills in {', '.join(context.get('skills', {}).get('top_skills', ['your expertise'])[:3])}, I'll look for relevant positions.",
                'suggestions': ['View matched jobs', 'Update skills', 'Set job alerts'],
                'actions': ['search_jobs', 'update_profile'],
                'confidence': 0.8
            },
            'salary_inquiry': {
                'response': f"Based on your experience level ({context.get('professional_profile', {}).get('experience_level', 'your level')}) and location, I can provide salary insights. Your current range is ${context.get('professional_profile', {}).get('salary_range', {}).get('min') or 0:,} - ${context.get('professional_profile', {}).get('salary_range', {}).get('max') or 0:,}.",
                'suggestions': ['View salary trends', 'Negotiate tips', 'Market analysis'],
                'actions': ['show_salary_data'],
                'confidence': 0.7
            },
            'profile_management': {
                'response': f"Your profile is currently {context.get('professional_profile', {}).get('profile_completeness', 0):.0f}% complete. Let me help you enhance it for better opportunities.",
                'suggestions': ['Complete profile', 'Add skills', 'Upload resume'],
                'actions': ['edit_profile', 'profile_wizard'],
                'confidence': 0.9
            },
            'skill_inquiry': {
                'response': f"I see you're interested in skill development. Based on your profile, trending skills in your field include data science, cloud computing, and AI/ML.",
                'suggestions': ['Skill recommendations', 'Learning paths', 'Certifications'],
                'actions': ['suggest_skills', 'learning_resources'],
                'confidence': 0.7
            },
            'help': {
                'response': f"I'm your personal AI assistant, {user_name}. I learn from our interactions to provide better assistance. How can I help you today?",
                'suggestions': ['Find jobs', 'Update profile', 'View insights'],
                'actions': ['show_help_menu'],
                'confidence': 0.6
            },
            'general': {
                'response': f"Hi {user_name}! I'm here to help with your career journey. What would you like to explore today?",
                'suggestions': ['Browse opportunities', 'Profile settings', 'Career insights'],
                'actions': [],
                'confidence': 0.5
            }
        }

        return responses.get(intent, responses['general'])

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of what the assistant has learned about the user."""
        metadata = self.profile.metadata or {}
        patterns = metadata.get('behavior_patterns', {})

        return {
            'user': self.user.username,
            'personalization_score': self._calculate_personalization_score(),
            'confidence_level': self._calculate_confidence_level(),
            'total_interactions': len(self.learning_history),
            'patterns': {
                'top_intents': sorted(
                    patterns.get('intents', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5],
                'top_topics': sorted(
                    patterns.get('topics', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5],
                'peak_activity_hours': sorted(
                    patterns.get('active_hours', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
            },
            'profile_insights': {
                'completeness': self.profile.profile_completeness,
                'skills_count': len(self.profile.skills or []),
                'applications_count': JobApplication.objects.filter(user=self.user).count()
            },
            'recommendations': self._generate_recommendations(patterns)
        }