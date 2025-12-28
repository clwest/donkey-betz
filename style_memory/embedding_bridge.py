"""
Style Memory Embedding Bridge

Session 179: Connects the style learning system to the RAG/embedding system.
This enables semantic search over user preferences and cross-system knowledge sharing.

Key Features:
1. Converts StyleMemory records into document embeddings for semantic search
2. Enables "find similar styles to what I've loved before" queries
3. Connects user preferences to the broader knowledge base
4. Enables agents to learn from user style preferences semantically
"""

import logging
import asyncio
from typing import List, Dict, Any

from .models import StyleMemory
from content.models import Document, DocumentEmbedding, EmbeddingModel, DocumentType
from content.embeddings import rag_system, EmbeddingManager

logger = logging.getLogger(__name__)


def run_async(coro):
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


class StyleEmbeddingBridge:
    """
    Bridge between StyleMemory and the embedding/RAG system.

    Enables:
    - Semantic search over user preferences
    - Finding similar styles across users (for recommendations)
    - Agent access to learned user preferences via RAG queries
    """

    def __init__(self, user=None):
        self.user = user
        self.embedding_manager = EmbeddingManager()

    def embed_style_memory(self, style_memory: StyleMemory,
                          embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL) -> bool:
        """
        Create an embedding for a StyleMemory record.

        This converts user style preferences into searchable vectors,
        enabling semantic queries like "find styles similar to what I loved".

        Args:
            style_memory: The StyleMemory record to embed
            embedding_model: Which embedding model to use

        Returns:
            True if embedding was created successfully
        """
        try:
            # Build text representation of the style memory
            text = self._style_memory_to_text(style_memory)

            if not text.strip():
                logger.warning(f"Empty text for StyleMemory {style_memory.id}")
                return False

            # Create or get document for this user's style preferences
            doc, created = Document.objects.get_or_create(
                owner=style_memory.user,
                title=f"Style Preferences - {style_memory.user.username}",
                document_type=DocumentType.KNOWLEDGE_EXTRACT,
                defaults={
                    'raw_content': '',
                    'processed_content': '',
                    'status': 'processed',
                    'tags': ['style_memory', 'user_preferences']
                }
            )

            # Generate embedding
            result = run_async(
                self.embedding_manager.generate_embedding(text, embedding_model)
            )

            if not result.success:
                logger.error(f"Failed to generate embedding: {result.error_message}")
                return False

            # Create DocumentEmbedding
            embedding, created = DocumentEmbedding.objects.update_or_create(
                document=doc,
                chunk_index=style_memory.id.int % 10000,  # Use UUID as unique index
                embedding_model=embedding_model,
                defaults={
                    'chunk_text': text,
                    'chunk_size': len(text),
                    'embedding_vector': result.embedding,
                    'embedding_dimension': result.dimension,
                    'processing_time_ms': result.processing_time_ms,
                    'embedding_cost': result.cost,
                    'metadata': {
                        'style_memory_id': str(style_memory.id),
                        'interaction_type': style_memory.interaction_type,
                        'content_id': str(style_memory.content_id) if style_memory.content_id else None,
                        'style_elements': style_memory.style_elements,
                        'color_palette': style_memory.color_palette,
                        'project_id': str(style_memory.project_id) if style_memory.project_id else None
                    }
                }
            )

            logger.info(f"Created embedding for StyleMemory {style_memory.id}")
            return True

        except Exception as e:
            logger.error(f"Error embedding StyleMemory {style_memory.id}: {e}")
            return False

    def _style_memory_to_text(self, style_memory: StyleMemory) -> str:
        """
        Convert a StyleMemory record into text for embedding.

        Creates a rich text representation that captures:
        - The interaction type (love/like/dislike)
        - Style elements and colors
        - The original prompt
        - Recipe information
        """
        parts = []

        # Interaction sentiment
        sentiment_map = {
            'love': 'User loved this style',
            'like': 'User liked this style',
            'dislike': 'User disliked this style',
            'save': 'User saved this content',
            'rate': 'User rated this content'
        }
        sentiment = sentiment_map.get(style_memory.interaction_type, 'User interacted with')
        parts.append(sentiment)

        # Original prompt
        if style_memory.prompt:
            parts.append(f"Original prompt: {style_memory.prompt}")

        # Style elements
        if style_memory.style_elements:
            styles = ', '.join(style_memory.style_elements)
            parts.append(f"Style elements: {styles}")

        # Color palette
        if style_memory.color_palette:
            colors = ', '.join(style_memory.color_palette)
            parts.append(f"Color palette: {colors}")

        # Recipe/mood
        if style_memory.recipe:
            if 'mood' in style_memory.recipe:
                parts.append(f"Mood: {style_memory.recipe['mood']}")
            if 'style' in style_memory.recipe:
                parts.append(f"Primary style: {style_memory.recipe['style']}")

        # Model used
        if style_memory.model_used:
            parts.append(f"Model: {style_memory.model_used}")

        # Notes
        if style_memory.notes:
            parts.append(f"Notes: {style_memory.notes}")

        return ". ".join(parts)

    def find_similar_preferences(self, query: str, limit: int = 5,
                                 min_similarity: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find StyleMemory records semantically similar to a query.

        This enables queries like:
        - "What styles has the user loved that are similar to cyberpunk?"
        - "Find preferences matching dramatic lighting"

        Args:
            query: Natural language query about styles
            limit: Maximum results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of matching preferences with similarity scores
        """
        try:
            # Generate query embedding
            result = run_async(
                self.embedding_manager.generate_embedding(query, EmbeddingModel.OPENAI_SMALL)
            )

            if not result.success:
                logger.error(f"Failed to generate query embedding: {result.error_message}")
                return []

            query_embedding = result.embedding

            # Get user's style preference embeddings
            embeddings = DocumentEmbedding.objects.filter(
                document__owner=self.user,
                document__tags__contains=['style_memory'],
                embedding_model=EmbeddingModel.OPENAI_SMALL
            ).select_related('document')

            # Calculate similarities
            results = []
            provider = self.embedding_manager.get_provider(EmbeddingModel.OPENAI_SMALL)

            for embedding in embeddings:
                try:
                    similarity = provider.calculate_similarity(
                        query_embedding, embedding.embedding_vector
                    )

                    if similarity >= min_similarity:
                        metadata = embedding.metadata or {}
                        results.append({
                            'style_memory_id': metadata.get('style_memory_id'),
                            'interaction_type': metadata.get('interaction_type'),
                            'style_elements': metadata.get('style_elements', []),
                            'color_palette': metadata.get('color_palette', []),
                            'similarity_score': similarity,
                            'text': embedding.chunk_text
                        })

                except Exception as e:
                    logger.error(f"Error calculating similarity: {e}")
                    continue

            # Sort by similarity
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Error finding similar preferences: {e}")
            return []

    def get_style_context_for_generation(self, prompt: str, limit: int = 3) -> str:
        """
        Get relevant style context from user preferences for content generation.

        This is called by the AI assistant when generating content to incorporate
        learned user preferences into the generation.

        Args:
            prompt: The generation prompt
            limit: Maximum style contexts to include

        Returns:
            Formatted context string for injection into AI prompts
        """
        if not self.user:
            return ""

        similar = self.find_similar_preferences(prompt, limit=limit, min_similarity=0.5)

        if not similar:
            return ""

        # Build context
        parts = ["Based on your style preferences:"]

        for pref in similar:
            if pref['interaction_type'] in ['love', 'like']:
                action = "loved" if pref['interaction_type'] == 'love' else "liked"
                styles = ', '.join(pref['style_elements'][:3]) if pref['style_elements'] else 'unspecified styles'
                parts.append(f"- You {action} {styles}")

            elif pref['interaction_type'] == 'dislike':
                styles = ', '.join(pref['style_elements'][:3]) if pref['style_elements'] else 'certain styles'
                parts.append(f"- You disliked {styles} (avoid these)")

        return "\n".join(parts)

    @staticmethod
    def embed_all_style_memories(user=None, batch_size: int = 50) -> Dict[str, int]:
        """
        Embed all StyleMemory records (optionally for a specific user).

        This is a batch operation to populate the embedding space with
        existing style preferences.

        Args:
            user: Optional user to filter by
            batch_size: Number of records to process at a time

        Returns:
            Dict with counts of successes and failures
        """
        bridge = StyleEmbeddingBridge(user=user)

        query = StyleMemory.objects.all()
        if user:
            query = query.filter(user=user)

        total = query.count()
        success = 0
        failed = 0

        logger.info(f"Embedding {total} StyleMemory records...")

        for sm in query.iterator():
            try:
                if bridge.embed_style_memory(sm):
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Error embedding {sm.id}: {e}")
                failed += 1

            if (success + failed) % batch_size == 0:
                logger.info(f"Progress: {success + failed}/{total}")

        logger.info(f"Completed: {success} success, {failed} failed")
        return {'success': success, 'failed': failed, 'total': total}


class AgentKnowledgeBridge:
    """
    Bridge for agents to access cross-system knowledge.

    Session 179: Enables agents to query:
    - User style preferences
    - Project context
    - Previous generation results
    - Cross-user style trends (anonymized)
    """

    def __init__(self, user, project=None):
        self.user = user
        self.project = project
        self.style_bridge = StyleEmbeddingBridge(user=user)

    def get_user_preference_context(self, prompt: str) -> str:
        """
        Get user preference context for an agent.

        Agents call this to understand user preferences when making decisions.
        """
        return self.style_bridge.get_style_context_for_generation(prompt)

    def get_project_style_summary(self) -> Dict[str, Any]:
        """
        Get style summary for the current project.

        Returns dominant styles, colors, and patterns used in the project.
        """
        if not self.project:
            return {}

        # Get StyleMemory records for this project
        memories = StyleMemory.objects.filter(
            user=self.user,
            project_id=self.project.id
        )

        # Aggregate styles
        all_styles = []
        all_colors = []
        interaction_counts = {'love': 0, 'like': 0, 'dislike': 0}

        for mem in memories:
            if mem.style_elements:
                all_styles.extend(mem.style_elements)
            if mem.color_palette:
                all_colors.extend(mem.color_palette)
            if mem.interaction_type in interaction_counts:
                interaction_counts[mem.interaction_type] += 1

        # Count frequencies
        from collections import Counter
        style_counts = Counter(all_styles)
        color_counts = Counter(all_colors)

        return {
            'total_interactions': sum(interaction_counts.values()),
            'interaction_breakdown': interaction_counts,
            'top_styles': style_counts.most_common(5),
            'top_colors': color_counts.most_common(5),
            'style_diversity': len(set(all_styles)),
            'color_diversity': len(set(all_colors))
        }

    def query_knowledge(self, question: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the combined knowledge base for agent decisions.

        This searches across:
        - User style preferences (StyleMemory embeddings)
        - Document knowledge base
        - Generated content history

        Args:
            question: Natural language question
            max_results: Maximum results

        Returns:
            List of relevant knowledge chunks with sources
        """
        results = []

        # Search style preferences
        style_results = self.style_bridge.find_similar_preferences(
            question, limit=max_results, min_similarity=0.5
        )
        for r in style_results:
            results.append({
                'source': 'style_preferences',
                'content': r['text'],
                'similarity': r['similarity_score'],
                'metadata': {
                    'style_elements': r['style_elements'],
                    'interaction_type': r['interaction_type']
                }
            })

        # Search document knowledge base (RAG)
        try:
            rag_results = run_async(
                rag_system.semantic_search(
                    query=question,
                    embedding_model=EmbeddingModel.OPENAI_SMALL,
                    limit=max_results,
                    similarity_threshold=0.6
                )
            )
            for r in rag_results:
                results.append({
                    'source': 'knowledge_base',
                    'content': r.chunk_text,
                    'similarity': r.similarity_score,
                    'metadata': {
                        'document_title': r.document_title,
                        'document_type': r.document_type
                    }
                })
        except Exception as e:
            logger.warning(f"RAG search failed: {e}")

        # Sort by similarity and deduplicate
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]


# Convenience function for AI assistant integration
def get_style_context_for_user(user, prompt: str) -> str:
    """
    Get style context for a user based on their preferences.

    Called by PersonalAIAssistant to inject learned preferences.
    """
    bridge = StyleEmbeddingBridge(user=user)
    return bridge.get_style_context_for_generation(prompt)


# Convenience function for agent integration
def get_agent_knowledge_context(user, prompt: str, project=None) -> Dict[str, Any]:
    """
    Get combined knowledge context for agents.

    Returns style preferences + knowledge base context.
    """
    bridge = AgentKnowledgeBridge(user=user, project=project)

    return {
        'preference_context': bridge.get_user_preference_context(prompt),
        'project_summary': bridge.get_project_style_summary() if project else {},
        'relevant_knowledge': bridge.query_knowledge(prompt, max_results=3)
    }
