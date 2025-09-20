#!/usr/bin/env python3
"""
Conversation Memory System - Persistent chat memory and context management

This system stores, retrieves, and manages conversation history to enable
contextual interactions and learning from user conversations.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

from core.models import SystemConfiguration, PlatformMetrics
from content.models import ContentGeneration, Feedback

User = get_user_model()
logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Manages persistent conversation memory and context
    """
    
    def __init__(self):
        self.max_context_length = 4000  # Max characters to store
        self.max_interactions_per_user = 100  # Max interactions to keep
        
    def store_interaction(self, user_id: int, user_input: str, assistant_response: str, 
                         context: Dict[str, Any] = None) -> str:
        """Store a conversation interaction (filters out verbose responses)"""
        
        # Filter out verbose responses to prevent feedback loop
        if self._is_response_too_verbose(assistant_response):
            logger.info(f"Skipping storage of verbose response (length: {len(assistant_response)})")
            return "skipped_verbose"
        
        interaction_id = self._generate_interaction_id(user_id, user_input)
        
        interaction_data = {
            'user_id': user_id,
            'user_input': user_input[:self.max_context_length],
            'assistant_response': assistant_response[:800],  # Limit stored responses to 800 chars
            'timestamp': timezone.now().isoformat(),
            'context': context or {},
            'interaction_id': interaction_id
        }
        
        # Store in SystemConfiguration with conversation prefix
        config_key = f"conversation_interaction_{user_id}_{interaction_id}"
        
        SystemConfiguration.set_config(
            config_key,
            interaction_data,
            f"Conversation interaction for user {user_id}",
            'conversation'
        )
        
        # Clean up old interactions if we exceed the limit
        self._cleanup_old_interactions(user_id)
        
        # Record metrics
        PlatformMetrics.objects.create(
            metric_name="conversation_interaction_stored",
            metric_value=1.0,
            metric_type='counter',
            subsystem='conversation',
            labels={
                'user_id': user_id,
                'input_length': len(user_input),
                'response_length': len(assistant_response)
            }
        )
        
        return interaction_id
    
    def _is_response_too_verbose(self, response: str) -> bool:
        """Check if a response is too verbose to store in memory"""
        if not response:
            return False
            
        # Filter criteria for verbose responses (adjusted to match new limits)
        char_limit = 800
        sentence_limit = 5
        
        # Check character count
        if len(response) > char_limit:
            return True
            
        # Check sentence count
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if len(sentences) > sentence_limit:
            return True
            
        return False
    
    def retrieve_user_context(self, user_id: int, max_interactions: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent conversation context for a user"""
        
        # Get all conversation configs for this user
        user_configs = SystemConfiguration.objects.filter(
            key__startswith=f"conversation_interaction_{user_id}_",
            category='conversation',
            is_active=True
        ).order_by('-created_at')[:max_interactions]
        
        interactions = []
        for config in user_configs:
            interaction_data = config.value
            if isinstance(interaction_data, dict):
                interactions.append(interaction_data)
        
        # Sort by timestamp (newest first)
        interactions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return interactions
    
    def search_conversations(self, user_id: int, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search through user's conversation history"""
        
        all_interactions = self.retrieve_user_context(user_id, max_interactions=50)
        
        # Simple text search in user inputs and responses
        matching_interactions = []
        query_lower = query.lower()
        
        for interaction in all_interactions:
            user_input = interaction.get('user_input', '').lower()
            response = interaction.get('assistant_response', '').lower()
            
            if query_lower in user_input or query_lower in response:
                # Calculate relevance score (simple)
                score = 0
                if query_lower in user_input:
                    score += 2
                if query_lower in response:
                    score += 1
                
                interaction['relevance_score'] = score
                matching_interactions.append(interaction)
        
        # Sort by relevance and recency
        matching_interactions.sort(key=lambda x: (x.get('relevance_score', 0), x.get('timestamp', '')), reverse=True)
        
        return matching_interactions[:limit]
    
    def store_user_preference(self, user_id: int, preference_key: str, preference_value: Any) -> None:
        """Store user preferences learned from conversations"""
        
        config_key = f"conversation_preference_{user_id}_{preference_key}"
        
        preference_data = {
            'user_id': user_id,
            'preference_key': preference_key,
            'preference_value': preference_value,
            'timestamp': timezone.now().isoformat(),
            'learned_from_conversation': True
        }
        
        SystemConfiguration.set_config(
            config_key,
            preference_data,
            f"User preference for {preference_key}",
            'conversation'
        )
        
        # Record metrics
        PlatformMetrics.objects.create(
            metric_name="conversation_preference_learned",
            metric_value=1.0,
            metric_type='counter',
            subsystem='conversation',
            labels={
                'user_id': user_id,
                'preference_key': preference_key
            }
        )
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Retrieve user preferences learned from conversations"""
        
        preference_configs = SystemConfiguration.objects.filter(
            key__startswith=f"conversation_preference_{user_id}_",
            category='conversation',
            is_active=True
        )
        
        preferences = {}
        for config in preference_configs:
            pref_data = config.value
            if isinstance(pref_data, dict):
                key = pref_data.get('preference_key')
                value = pref_data.get('preference_value')
                if key and value is not None:
                    preferences[key] = value
        
        return preferences
    
    def analyze_conversation_patterns(self, user_id: int = None) -> Dict[str, Any]:
        """Analyze conversation patterns for insights"""
        
        print("🔍 Analyzing conversation patterns...")
        
        # Get conversation configurations
        if user_id:
            interaction_configs = SystemConfiguration.objects.filter(
                key__startswith=f"conversation_interaction_{user_id}_",
                category='conversation'
            )
        else:
            interaction_configs = SystemConfiguration.objects.filter(
                key__startswith="conversation_interaction_",
                category='conversation'
            )
        
        if not interaction_configs.exists():
            return {
                'total_interactions': 0,
                'unique_users': 0,
                'patterns': [],
                'insights': ["No conversation data available for analysis"]
            }
        
        # Analyze patterns
        user_interactions = defaultdict(int)
        interaction_lengths = []
        response_lengths = []
        topics = defaultdict(int)
        timestamps = []
        
        for config in interaction_configs:
            data = config.value
            if not isinstance(data, dict):
                continue
                
            user_id_from_data = data.get('user_id')
            if user_id_from_data:
                user_interactions[user_id_from_data] += 1
            
            user_input = data.get('user_input', '')
            response = data.get('assistant_response', '')
            
            interaction_lengths.append(len(user_input))
            response_lengths.append(len(response))
            
            # Simple topic extraction (keywords)
            common_topics = ['help', 'create', 'generate', 'write', 'analyze', 'optimize', 'fix', 'explain']
            for topic in common_topics:
                if topic in user_input.lower():
                    topics[topic] += 1
            
            timestamp = data.get('timestamp')
            if timestamp:
                timestamps.append(timestamp)
        
        # Calculate statistics
        total_interactions = len(interaction_lengths)
        unique_users = len(user_interactions)
        
        patterns = []
        
        if interaction_lengths:
            avg_input_length = sum(interaction_lengths) / len(interaction_lengths)
            avg_response_length = sum(response_lengths) / len(response_lengths)
            
            patterns.append({
                'type': 'interaction_length',
                'avg_input_length': round(avg_input_length, 1),
                'avg_response_length': round(avg_response_length, 1),
                'total_interactions': total_interactions
            })
        
        if topics:
            top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns.append({
                'type': 'popular_topics',
                'topics': [{'topic': topic, 'count': count} for topic, count in top_topics]
            })
        
        # User engagement patterns
        if user_interactions:
            most_active_users = sorted(user_interactions.items(), key=lambda x: x[1], reverse=True)[:5]
            avg_interactions_per_user = sum(user_interactions.values()) / len(user_interactions)
            
            patterns.append({
                'type': 'user_engagement',
                'avg_interactions_per_user': round(avg_interactions_per_user, 1),
                'most_active_users': [{'user_id': uid, 'interactions': count} for uid, count in most_active_users]
            })
        
        # Generate insights
        insights = []
        
        if total_interactions > 0:
            insights.append(f"Analyzed {total_interactions} conversation interactions from {unique_users} users")
            
            if avg_input_length > 200:
                insights.append("Users tend to provide detailed inputs - system handles complex requests well")
            elif avg_input_length < 50:
                insights.append("Users prefer brief interactions - consider offering more guided assistance")
            
            if topics:
                top_topic = max(topics.items(), key=lambda x: x[1])
                insights.append(f"Most common topic: '{top_topic[0]}' ({top_topic[1]} mentions)")
            
            if avg_interactions_per_user > 10:
                insights.append("High user engagement - users return for multiple interactions")
            elif avg_interactions_per_user < 3:
                insights.append("Low user retention - consider improving onboarding or user experience")
        
        return {
            'total_interactions': total_interactions,
            'unique_users': unique_users,
            'patterns': patterns,
            'insights': insights
        }
    
    def create_conversation_summary(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Create a summary of user's recent conversations"""
        
        # Get recent interactions
        recent_interactions = self.retrieve_user_context(user_id, max_interactions=50)
        
        # Filter to specified timeframe
        cutoff_time = timezone.now() - timedelta(days=days)
        filtered_interactions = []
        
        for interaction in recent_interactions:
            timestamp_str = interaction.get('timestamp', '')
            try:
                interaction_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if interaction_time >= cutoff_time:
                    filtered_interactions.append(interaction)
            except ValueError:
                continue  # Skip interactions with invalid timestamps
        
        if not filtered_interactions:
            return {
                'user_id': user_id,
                'period_days': days,
                'total_interactions': 0,
                'summary': "No recent conversations found",
                'key_topics': [],
                'preferences_identified': {}
            }
        
        # Analyze topics and themes
        all_inputs = ' '.join([i.get('user_input', '') for i in filtered_interactions])
        all_responses = ' '.join([i.get('assistant_response', '') for i in filtered_interactions])
        
        # Extract key topics (simple keyword approach)
        topic_keywords = {
            'content_creation': ['write', 'create', 'generate', 'blog', 'article'],
            'optimization': ['optimize', 'improve', 'better', 'faster', 'performance'],
            'help_support': ['help', 'how', 'can you', 'explain', 'what is'],
            'technical': ['code', 'function', 'api', 'database', 'error'],
            'analysis': ['analyze', 'review', 'check', 'examine', 'evaluate']
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_inputs.lower())
            if score > 0:
                topic_scores[topic] = score
        
        # Get top topics
        top_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'user_id': user_id,
            'period_days': days,
            'total_interactions': len(filtered_interactions),
            'summary': f"User had {len(filtered_interactions)} interactions in the last {days} days",
            'key_topics': [{'topic': topic, 'mentions': count} for topic, count in top_topics],
            'preferences_identified': self.get_user_preferences(user_id),
            'first_interaction': filtered_interactions[-1].get('timestamp') if filtered_interactions else None,
            'last_interaction': filtered_interactions[0].get('timestamp') if filtered_interactions else None
        }
    
    def _generate_interaction_id(self, user_id: int, user_input: str) -> str:
        """Generate unique interaction ID"""
        content = f"{user_id}_{user_input}_{timezone.now().timestamp()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _cleanup_old_interactions(self, user_id: int) -> None:
        """Clean up old interactions if we exceed the limit"""
        
        user_configs = SystemConfiguration.objects.filter(
            key__startswith=f"conversation_interaction_{user_id}_",
            category='conversation'
        ).order_by('-created_at')
        
        if user_configs.count() > self.max_interactions_per_user:
            # Delete oldest interactions
            old_configs = user_configs[self.max_interactions_per_user:]
            for config in old_configs:
                config.delete()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about conversation memory usage"""
        
        interaction_configs = SystemConfiguration.objects.filter(
            key__startswith="conversation_interaction_",
            category='conversation'
        )
        
        preference_configs = SystemConfiguration.objects.filter(
            key__startswith="conversation_preference_",
            category='conversation'
        )
        
        # Count unique users
        user_ids = set()
        for config in interaction_configs:
            if isinstance(config.value, dict) and 'user_id' in config.value:
                user_ids.add(config.value['user_id'])
        
        return {
            'total_interactions': interaction_configs.count(),
            'total_preferences': preference_configs.count(),
            'unique_users_with_memory': len(user_ids),
            'memory_configs': interaction_configs.count() + preference_configs.count()
        }


# Utility functions for easy integration
def store_chat_interaction(user_id: int, user_message: str, assistant_message: str, 
                          context: Dict[str, Any] = None) -> str:
    """Convenience function to store a chat interaction"""
    memory = ConversationMemory()
    return memory.store_interaction(user_id, user_message, assistant_message, context)


def get_user_chat_history(user_id: int, max_messages: int = 10) -> List[Dict[str, Any]]:
    """Convenience function to get user's chat history"""
    memory = ConversationMemory()
    return memory.retrieve_user_context(user_id, max_messages)


def learn_user_preference(user_id: int, preference: str, value: Any) -> None:
    """Convenience function to learn and store user preference"""
    memory = ConversationMemory()
    memory.store_user_preference(user_id, preference, value)


if __name__ == "__main__":
    # Demo the conversation memory system
    memory = ConversationMemory()
    
    print("🧠 Conversation Memory System Demo")
    print("=" * 50)
    
    # Store some sample interactions
    user_id = 1
    
    memory.store_interaction(
        user_id, 
        "Help me write a blog post about AI",
        "I'll help you create a comprehensive blog post about AI. Let me start with an outline..."
    )
    
    memory.store_interaction(
        user_id,
        "Make it more technical and focus on machine learning",
        "I'll adjust the blog post to be more technical with a focus on machine learning algorithms..."
    )
    
    memory.store_user_preference(user_id, "content_style", "technical")
    memory.store_user_preference(user_id, "preferred_topics", ["AI", "machine learning", "technology"])
    
    # Retrieve and display results
    print("\n📋 User Context:")
    context = memory.retrieve_user_context(user_id)
    for i, interaction in enumerate(context):
        print(f"   {i+1}. Input: {interaction['user_input'][:50]}...")
        print(f"      Response: {interaction['assistant_response'][:50]}...")
    
    print("\n🎯 User Preferences:")
    preferences = memory.get_user_preferences(user_id)
    for key, value in preferences.items():
        print(f"   • {key}: {value}")
    
    print("\n📊 Conversation Analysis:")
    analysis = memory.analyze_conversation_patterns()
    print(f"   Total interactions: {analysis['total_interactions']}")
    print(f"   Unique users: {analysis['unique_users']}")
    for insight in analysis['insights']:
        print(f"   • {insight}")
    
    print("\n📈 Memory Statistics:")
    stats = memory.get_memory_stats()
    for key, value in stats.items():
        print(f"   • {key}: {value}")