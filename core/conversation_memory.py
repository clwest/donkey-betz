"""Conversation memory facade.

Thin wrapper around the ``core.models.ConversationMemory`` Django model
that preserves the legacy `conversation_memory.save_conversation(...)` /
`get_conversation_history(...)` / `update_knowledge_metrics(...)` call
surface used by the chat-path views.

Session 1235 P5#3 audit Tranche 1 PR #2: pivoted from dead
`unified_embeddings` raw-SQL writes (against a DB that existed but a
table that didn't) to the real `core.models.ConversationMemory` model
that has the canonical user-chat shape (user, message, response,
agents_used, intent, success, created_at).

Pre-pivot every save_conversation call silently returned False with
`logger.error("Failed to save conversation: relation "unified_embeddings"
does not exist")` and the chat path's outer try/except logged
"Conversation save result: False" — the "learning loop" had been broken
since this file existed.

The facade pattern is kept for two reasons:
1. Two call sites (`core/views.py:1094`, `core/views/main.py:925`) import
   the singleton; changing both imports would expand PR scope without
   semantic benefit.
2. The hallucination filter (block known bad-content strings before
   persisting) is real functional logic worth preserving at this layer.

Embedding generation was dropped from save_conversation: the new model
has no `embedding` column. If/when semantic search of conversation
history is needed, that's a separate feature on top of this surface
(could write to DocumentEmbedding with a conversation-specific
source_type, or add a new ConversationEmbedding model).
"""

import logging
from typing import Dict, Any, List, Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


# Hallucination filter — real functional content gate preserved from
# pre-pivot version. Strings here are known bad-content markers from
# unrelated Flutter/fitness-tracker hallucinations that surfaced in
# earlier sessions; if the assistant response contains any, we refuse
# to persist it.
HALLUCINATION_INDICATORS = (
    'dashboard_page.dart',
    'main_navigation_page.dart',
    'FITNESS DASHBOARD',
    'Flutter',
    'weight tracking',
    'Walking, Herd, Profile',
)


class ConversationMemory:
    """Facade around the core.models.ConversationMemory Django model."""

    def save_conversation(
        self,
        user_id,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Persist a user/assistant exchange to ConversationMemory.

        Returns True on successful save, False on filter-rejection or
        any DB error. Mirrors pre-pivot return semantics so callers
        don't need to change.
        """
        # Hallucination filter — refuse to persist responses containing
        # known bad-content markers from prior incidents.
        for indicator in HALLUCINATION_INDICATORS:
            if indicator in assistant_response:
                logger.warning(
                    "ConversationMemory.save_conversation: rejected by "
                    "hallucination filter (indicator=%r)",
                    indicator,
                )
                return False

        try:
            from core.models import ConversationMemory as ConvModel

            user = User.objects.filter(id=user_id).first()
            if not user:
                logger.error(
                    "ConversationMemory.save_conversation: user_id=%r not found",
                    user_id,
                )
                return False

            meta = metadata or {}
            # Extract structured fields that map to model columns.
            # Other metadata keys (conversation_id, provider, model,
            # rag_used, ...) have no home in the current model — they
            # only existed in the dead-table JSONB metadata column.
            # Drop them with a comment; if needed later, add a metadata
            # JSONField via migration.
            agents_used = meta.get('agents_used') or []
            intent = (meta.get('intent') or '')[:100]  # CharField max_length=100

            row = ConvModel.objects.create(
                user=user,
                message=user_message,
                response=assistant_response,
                agents_used=agents_used,
                intent=intent,
                success=True,
            )
            logger.info(
                "ConversationMemory.save_conversation: persisted row id=%s "
                "for user_id=%s",
                row.id, user_id,
            )
            return True

        except Exception as e:
            logger.error(
                "ConversationMemory.save_conversation: failed to persist "
                "for user_id=%r: %s",
                user_id, e, exc_info=True,
            )
            return False

    def get_conversation_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent ConversationMemory rows shaped for legacy callers.

        Output shape preserved from pre-pivot version:
            {content, user_message, assistant_response, timestamp}
        """
        try:
            from core.models import ConversationMemory as ConvModel

            qs = ConvModel.objects.filter(user_id=user_id).order_by(
                '-created_at',
            )[:limit]

            return [
                {
                    'content': f"User: {row.message}\nAssistant: {row.response}",
                    'user_message': row.message,
                    'assistant_response': row.response,
                    'timestamp': row.created_at.isoformat() if row.created_at else None,
                }
                for row in qs
            ]

        except Exception as e:
            logger.error(
                "ConversationMemory.get_conversation_history: failed for "
                "user_id=%r: %s",
                user_id, e, exc_info=True,
            )
            return []

    def update_knowledge_metrics(self, user_id: int) -> Dict[str, int]:
        """Return knowledge metrics for a user's conversations + global
        embedding corpus count.

        Output shape preserved from pre-pivot version:
            {total_conversations, today_conversations,
             total_knowledge_base, learning_rate}

        ``total_knowledge_base`` now reflects the live DocumentEmbedding
        chunk count (the real corpus size) instead of the dead
        unified_embeddings table. ``learning_rate`` is today's
        conversation count, matching pre-pivot semantics.
        """
        try:
            from core.models import ConversationMemory as ConvModel
            from content.models import DocumentEmbedding

            # Use TIME_ZONE-aware localdate for created_at__date filter
            # (Session 1235 PR #2636 lesson — same as dashboard pivot).
            today = timezone.localdate()

            user_total = ConvModel.objects.filter(user_id=user_id).count()
            user_today = ConvModel.objects.filter(
                user_id=user_id,
                created_at__date=today,
            ).count()
            total_kb = DocumentEmbedding.objects.count()

            return {
                'total_conversations': user_total,
                'today_conversations': user_today,
                'total_knowledge_base': total_kb,
                'learning_rate': user_today,
            }

        except Exception as e:
            logger.error(
                "ConversationMemory.update_knowledge_metrics: failed for "
                "user_id=%r: %s",
                user_id, e, exc_info=True,
            )
            return {
                'total_conversations': 0,
                'today_conversations': 0,
                'total_knowledge_base': 0,
                'learning_rate': 0,
            }


# Singleton instance — import target used by core/views.py + core/views/main.py
conversation_memory = ConversationMemory()
