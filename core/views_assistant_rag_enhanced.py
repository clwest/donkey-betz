"""
RAG-Enhanced Assistant Views for the Unified Donkey Betz Platform.
This module provides a personal AI assistant with full RAG capabilities.
"""

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
import uuid
import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
User = get_user_model()


class RAGAssistant:
    """
    RAG-Enhanced Assistant that searches through all available knowledge
    """
    
    def __init__(self, user):
        self.user = user
        self.embedding_model = 'text-embedding-ada-002'
        
    def search_embeddings(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search through unified embeddings using keyword matching
        (Enhanced with vector similarity when embedding API is available)
        """
        try:
            from django.db import connection
            
            results = []
            query_lower = query.lower()
            keywords = [word for word in query_lower.split() if len(word) > 2]
            
            with connection.cursor() as cursor:
                for keyword in keywords:
                    cursor.execute("""
                        SELECT DISTINCT
                            content_type, 
                            content_text,
                            source_table,
                            metadata,
                            CASE 
                                WHEN source_table = 'ai_partner_codeembedding' THEN 0.9
                                ELSE 0.8
                            END as relevance
                        FROM unified_embeddings 
                        WHERE LOWER(content_text) LIKE %s
                        ORDER BY relevance DESC
                        LIMIT %s
                    """, [f'%{keyword}%', limit])
                    
                    for content_type, content_text, source_table, metadata, relevance in cursor.fetchall():
                        # Determine result type and title
                        if source_table == 'ai_partner_codeembedding':
                            result_type = 'code'
                            title = f"{content_type} (Django Code)"
                        else:
                            result_type = 'document' 
                            title = content_type.replace('_', ' ').title()
                        
                        result = {
                            'type': result_type,
                            'title': title,
                            'content': content_text[:500],
                            'relevance': relevance,
                            'metadata': metadata or {}
                        }
                        
                        # Avoid duplicates
                        if not any(r['content'][:100] == result['content'][:100] for r in results):
                            results.append(result)
            
            results.sort(key=lambda x: x['relevance'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching embeddings: {str(e)}")
            return []
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback keyword search if embeddings are not available
        """
        try:
            from content.models import Document
            from django.db.models import Q
            
            # Split query into words for better matching
            query_words = query.lower().split()
            
            # Build Q objects for each word
            q_objects = Q()
            for word in query_words:
                # Skip very short words
                if len(word) < 3:
                    continue
                q_objects |= (
                    Q(title__icontains=word) | 
                    Q(description__icontains=word) |
                    Q(raw_content__icontains=word) |
                    Q(processed_content__icontains=word)
                )
            
            # If no valid search terms, search for the full query
            if not q_objects:
                q_objects = (
                    Q(title__icontains=query) | 
                    Q(description__icontains=query) |
                    Q(raw_content__icontains=query) |
                    Q(processed_content__icontains=query)
                )
            
            # Keyword search - search all public documents or user's documents
            docs = Document.objects.filter(q_objects).filter(
                Q(is_public=True) | Q(owner=self.user)
            )[:limit]
            
            results = []
            for doc in docs:
                content = doc.processed_content or doc.raw_content or doc.description or ""
                results.append({
                    'type': 'document',
                    'title': doc.title,
                    'content': content[:500],
                    'relevance': 0.8,  # Default relevance for keyword matches
                    'metadata': doc.metadata
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding for text using available AI provider
        """
        try:
            from content.ai_providers import AIProviderManager
            ai_manager = AIProviderManager()
            
            # Check if OpenAI is available for embeddings
            if 'openai' in ai_manager.get_available_providers():
                import openai
                from django.conf import settings
                
                openai.api_key = settings.OPENAI_API_KEY
                response = openai.Embedding.create(
                    model=self.embedding_model,
                    input=text
                )
                return np.array(response['data'][0]['embedding'])
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
        
        return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        """
        try:
            # Handle different vector formats
            if isinstance(vec1, str):
                vec1 = np.array(json.loads(vec1))
            if isinstance(vec2, str):
                vec2 = np.array(json.loads(vec2))
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm_1 = np.linalg.norm(vec1)
            norm_2 = np.linalg.norm(vec2)
            
            if norm_1 == 0 or norm_2 == 0:
                return 0.0
            
            return dot_product / (norm_1 * norm_2)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def build_context(self, query: str) -> tuple[str, List[Dict[str, Any]]]:
        """
        Build context from available knowledge for the query
        """
        # Always use keyword search since we don't have embeddings yet
        sources = self.search_documents(query)
        
        # Try semantic search if keyword search returns nothing
        if not sources:
            sources = self.search_embeddings(query)
        
        # Build context string
        context_parts = []
        
        if sources:
            context_parts.append("Based on the knowledge base, here's relevant information:\n")
            for source in sources:
                context_parts.append(f"\n[{source['type'].upper()}] {source['title']}:")
                context_parts.append(source['content'])
        
        context = "\n".join(context_parts) if context_parts else ""
        return context, sources


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assistant_chat_enhanced(request):
    """
    RAG-Enhanced Personal AI Assistant Chat
    """
    user = request.user
    
    try:
        # Get request data
        message = request.data.get('message', '').strip()
        conversation_id = request.data.get('conversation_id', str(uuid.uuid4()))
        use_rag = request.data.get('use_rag', True)
        
        logger.info(f"Assistant chat request - Message: {message[:50]}... RAG: {use_rag}")
        
        if not message:
            return Response({
                'error': 'Message is required',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        # Initialize RAG assistant
        rag_assistant = RAGAssistant(user)
        
        # Build context from knowledge base
        context = ""
        sources = []
        rag_actually_used = False
        if use_rag:
            context, sources = rag_assistant.build_context(message)
            rag_actually_used = bool(sources)  # RAG was actually used if we found sources
            logger.info(f"RAG search found {len(sources)} sources")
        
        # Get AI provider
        from content.ai_providers import AIProviderManager
        ai_manager = AIProviderManager()
        available_providers = ai_manager.get_available_providers()
        
        if not available_providers:
            # Fallback response if no AI providers
            logger.warning("No AI providers available")
            response_text = f"I understand you asked: '{message}'. "
            if sources:
                response_text += f"I found {len(sources)} relevant items in the knowledge base. "
            response_text += "However, I'm currently running in mock mode. Please configure AI provider API keys for full functionality."
            
            return Response({
                'message': response_text,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'provider': 'mock',
                'model': 'fallback',
                'rag_used': rag_actually_used,
                'sources': sources[:3] if sources else [],
                'knowledge_base_size': _get_knowledge_base_size(),
                'total_embeddings_available': _get_total_embeddings()
            })
        
        # Select provider and model
        provider = None
        model = None
        
        if 'openai' in available_providers:
            provider = 'openai'
            model = 'gpt-5-mini'
        elif 'anthropic' in available_providers:
            provider = 'anthropic'
            model = 'claude-3-haiku-20240307'
        elif 'google' in available_providers:
            provider = 'google'
            model = 'gemini-pro'
        else:
            provider = available_providers[0]
            model = 'default'
        
        # Build enhanced system prompt
        system_prompt = f"""You are {user.username if hasattr(user, 'username') else user.email}'s personal AI assistant.

You have access to a comprehensive knowledge base with business intelligence, AI capabilities, and domain expertise.
Focus on providing helpful, accurate information based on the user's actual knowledge base and platform capabilities.

Key Platform Features:
- Advanced AI agent orchestration with 87+ specialized agents
- Multi-LLM provider integration (OpenAI, Anthropic, Google)
- RAG-powered knowledge management system
- Content creation and automation tools
- Real-time workflow orchestration
- Self-awareness and code understanding capabilities

Be helpful, accurate, and cite sources when available. Keep responses focused and actionable."""
        
        # Add context to user message if available
        enhanced_message = message
        if context:
            # Simplify context format to avoid confusing the model
            enhanced_message = f"""Based on the following information from the knowledge base:

{context[:1000]}...

User question: {message}

Please provide a helpful response."""
        
        # Generate AI response with correct parameter for GPT-5
        if 'gpt-5' in model.lower():
            config = {'max_completion_tokens': 1000}
        else:
            config = {'max_tokens': 1000, 'temperature': 0.7}
        
        result = ai_manager.generate_content(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            user_prompt=enhanced_message,
            config=config
        )
        
        if result.success:
            # Handle empty responses with fallback
            if not result.content or len(result.content.strip()) == 0:
                logger.warning("Empty response from AI provider, using fallback")
                # Use correct parameter name for GPT-5 models
                fallback_config = {'max_completion_tokens': 200} if 'gpt-5' in model.lower() else {'max_tokens': 200}
                fallback_result = ai_manager.generate_content(
                    provider=provider,
                    model=model,
                    system_prompt="You are a helpful assistant.",
                    user_prompt=message,
                    config=fallback_config
                )
                if fallback_result.success and fallback_result.content:
                    result = fallback_result
                    logger.info("Fallback response successful")
                
            # Make sure content is a string
            response_content = str(result.content) if result.content is not None else ""
            
            # Log for debugging
            if not response_content:
                logger.error(f"Still empty content after all processing. Token usage: {result.token_usage}")
            
            return Response({
                'message': response_content,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'provider': provider,
                'model': result.model_used or model,
                'token_usage': result.token_usage,
                'generation_time_ms': result.generation_time_ms,
                'rag_used': rag_actually_used,
                'sources': sources[:3] if sources else [],
                'knowledge_base_size': _get_knowledge_base_size(),
                'total_embeddings_available': _get_total_embeddings()
            })
        else:
            logger.error(f"AI generation failed: {result.error_message}")
            return Response({
                'message': f"I encountered an error processing your message. Error: {result.error_message}",
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'error': result.error_message
            }, status=500)
            
    except Exception as e:
        logger.error(f"Assistant chat error: {str(e)}")
        return Response({
            'error': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)


def _get_knowledge_base_size() -> int:
    """Get total documents in knowledge base"""
    try:
        from content.models import Document
        return Document.objects.count()
    except:
        return 0


def _get_total_embeddings() -> int:
    """Get total embeddings available"""
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
            return cursor.fetchone()[0]
    except:
        return 0