"""
Fixed Conversation Memory System
================================

Separates chat conversations from document embeddings to eliminate confusion.
- Chat memories: Stored separately for conversation continuity
- Document embeddings: Used only for RAG retrieval from knowledge base documents
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()

# Import the model from models.py instead of defining it here
from .models import ChatConversation


class ConversationMemoryFixed:
    """
    Fixed conversation memory that separates chat history from document embeddings
    """

    def __init__(self):
        self.max_context_messages = 5  # How many recent messages to include in context

    def save_conversation(self, user_id: str, user_message: str,
                         assistant_response: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Save conversation to chat memory (NOT as document embedding)

        Args:
            user_id: User ID
            user_message: User's message
            assistant_response: Assistant's response
            metadata: Additional context

        Returns:
            True if saved successfully
        """
        try:
            logger.info(f"Saving chat conversation (not as document embedding)")

            # Get or create user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found, skipping conversation save")
                return False

            # Extract metadata
            meta = metadata or {}
            conversation_id = meta.get('conversation_id', f"chat_{datetime.now().timestamp()}")

            # Don't save conversations with hallucination indicators
            hallucination_indicators = [
                'dashboard_page.dart',
                'main_navigation_page.dart',
                'FITNESS DASHBOARD',
                'Flutter',
                'weight tracking',
                'Walking, Herd, Profile'
            ]

            for indicator in hallucination_indicators:
                if indicator in assistant_response:
                    logger.warning(f"Detected potential hallucination, not saving conversation")
                    return False

            # Create conversation record
            conversation = ChatConversation.objects.create(
                user=user,
                conversation_id=conversation_id,
                user_message=user_message,
                assistant_response=assistant_response,
                context_used=meta.get('rag_context', {}),
                metadata=meta,
                response_time_ms=meta.get('generation_time_ms'),
                model_used=meta.get('model', ''),
                provider_used=meta.get('provider', ''),
                agents_used=meta.get('agents_involved', []),
                agent_results=meta.get('agent_results', {})
            )

            logger.info(f"✅ Successfully saved chat conversation: {conversation.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False

    def get_conversation_context(self, user_id: str, conversation_id: str = None) -> str:
        """
        Get recent conversation history as context for the assistant

        Args:
            user_id: User ID
            conversation_id: Current conversation ID (optional)

        Returns:
            Formatted conversation context
        """
        try:
            user = User.objects.get(id=user_id)

            # Get recent conversations
            recent_conversations = ChatConversation.objects.filter(
                user=user
            ).order_by('-created_at')[:self.max_context_messages]

            if not recent_conversations:
                return ""

            # Format as context
            context_lines = []
            for conv in reversed(list(recent_conversations)):  # Reverse to get chronological order
                context_lines.append(f"User: {conv.user_message[:100]}...")
                context_lines.append(f"Assistant: {conv.assistant_response[:100]}...")

            return "\n".join(context_lines)

        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found for conversation context")
            return ""
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return ""

    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history for user

        Args:
            user_id: User ID
            limit: Number of conversations to retrieve

        Returns:
            List of conversation records
        """
        try:
            user = User.objects.get(id=user_id)

            conversations = ChatConversation.objects.filter(
                user=user
            ).order_by('-created_at')[:limit]

            return [
                {
                    'id': conv.id,
                    'conversation_id': conv.conversation_id,
                    'user_message': conv.user_message,
                    'assistant_response': conv.assistant_response,
                    'model_used': conv.model_used,
                    'provider_used': conv.provider_used,
                    'agents_used': conv.agents_used,
                    'created_at': conv.created_at.isoformat(),
                    'metadata': conv.metadata
                }
                for conv in conversations
            ]

        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def get_conversation_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get conversation metrics for user

        Args:
            user_id: User ID

        Returns:
            Dictionary with conversation metrics
        """
        try:
            user = User.objects.get(id=user_id)

            total_conversations = ChatConversation.objects.filter(user=user).count()

            today_conversations = ChatConversation.objects.filter(
                user=user,
                created_at__date=timezone.now().date()
            ).count()

            # Count agent executions
            agent_executions = ChatConversation.objects.filter(
                user=user,
                agents_used__len__gt=0
            ).count()

            # Get most used models
            recent_convs = ChatConversation.objects.filter(user=user).order_by('-created_at')[:50]
            models_used = {}
            for conv in recent_convs:
                model = conv.model_used or 'unknown'
                models_used[model] = models_used.get(model, 0) + 1

            return {
                'total_conversations': total_conversations,
                'today_conversations': today_conversations,
                'agent_executions': agent_executions,
                'models_used': models_used,
                'conversation_type': 'chat_memory',  # Distinguish from document embeddings
                'data_source': 'chat_conversations_table'  # Clear data source
            }

        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found")
            return {}
        except Exception as e:
            logger.error(f"Error getting conversation metrics: {e}")
            return {}

    def search_conversations(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search through conversation history (not document embeddings)

        Args:
            user_id: User ID
            query: Search query
            limit: Number of results

        Returns:
            List of matching conversations
        """
        try:
            user = User.objects.get(id=user_id)

            # Simple text search in conversations
            conversations = ChatConversation.objects.filter(
                user=user
            ).filter(
                models.Q(user_message__icontains=query) |
                models.Q(assistant_response__icontains=query)
            ).order_by('-created_at')[:limit]

            return [
                {
                    'id': conv.id,
                    'user_message': conv.user_message[:200],
                    'assistant_response': conv.assistant_response[:200],
                    'created_at': conv.created_at.isoformat(),
                    'relevance_type': 'chat_history_match'  # Distinguish from RAG
                }
                for conv in conversations
            ]

        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []


# Global instance
conversation_memory_fixed = ConversationMemoryFixed()