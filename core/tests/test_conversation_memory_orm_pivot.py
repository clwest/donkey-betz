"""Session 1235 P5#3 audit Tranche 1 PR #2 — conversation_memory ORM pivot.

Verifies the ``core.conversation_memory.ConversationMemory`` facade now
persists / reads / counts via the real ``core.models.ConversationMemory``
Django model instead of the dead `unified_embeddings` substrate. Plus
preserves the hallucination filter and shape contracts that the chat
path callers (`core/views.py:1094`, `core/views/main.py:925`) depend on.

Per Session 1234 D16 memory rule
``feedback_test_real_db_for_queryset_semantics``: real DB throughout;
no MagicMock'd querysets.

Run::

    python manage.py test core.tests.test_conversation_memory_orm_pivot -v 2 --keepdb
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.conversation_memory import (
    ConversationMemory as ConversationMemoryFacade,
    HALLUCINATION_INDICATORS,
    conversation_memory,
)
from core.models import ConversationMemory as ConvModel
from content.models import Document, DocumentEmbedding, EmbeddingModel

User = get_user_model()


def _make_embedding_chunk(owner, title='Chunk doc'):
    """Helper to add a real DocumentEmbedding row for the
    total_knowledge_base count assertion."""
    doc = Document.objects.create(
        title=title,
        document_type='markdown',
        raw_content='content',
        owner=owner,
    )
    DocumentEmbedding.objects.create(
        document=doc,
        embedding_model=EmbeddingModel.OPENAI_SMALL,
        chunk_index=0,
        chunk_text='chunk',
        chunk_size=5,
        embedding_dimension=1536,
    )
    return doc


class SaveConversationORMTests(TestCase):
    """save_conversation persists into core.models.ConversationMemory."""

    def setUp(self):
        self.memory = ConversationMemoryFacade()
        self.user = User.objects.create_user(
            username=f'test_save_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_save_persists_real_row(self):
        result = self.memory.save_conversation(
            user_id=self.user.id,
            user_message='What is RAG?',
            assistant_response='Retrieval Augmented Generation.',
            metadata={'agents_used': ['rag-agent'], 'intent': 'definition'},
        )
        self.assertTrue(result)

        rows = ConvModel.objects.filter(user=self.user)
        self.assertEqual(rows.count(), 1)
        row = rows.first()
        self.assertEqual(row.message, 'What is RAG?')
        self.assertEqual(row.response, 'Retrieval Augmented Generation.')
        self.assertEqual(row.agents_used, ['rag-agent'])
        self.assertEqual(row.intent, 'definition')
        self.assertTrue(row.success)

    def test_save_with_no_metadata_uses_defaults(self):
        result = self.memory.save_conversation(
            user_id=self.user.id,
            user_message='Hello',
            assistant_response='Hi there.',
        )
        self.assertTrue(result)

        row = ConvModel.objects.get(user=self.user)
        self.assertEqual(row.agents_used, [])
        self.assertEqual(row.intent, '')

    def test_save_rejects_hallucination_indicators(self):
        for indicator in HALLUCINATION_INDICATORS:
            result = self.memory.save_conversation(
                user_id=self.user.id,
                user_message='Tell me about my dashboard',
                assistant_response=f'Looking at your {indicator}, you can see...',
            )
            self.assertFalse(
                result,
                f"Should reject responses containing {indicator!r}",
            )

        self.assertEqual(
            ConvModel.objects.filter(user=self.user).count(), 0,
            "Hallucination-filtered messages must not persist."
        )

    def test_save_returns_false_when_user_missing(self):
        nonexistent_user_id = 999999
        result = self.memory.save_conversation(
            user_id=nonexistent_user_id,
            user_message='Q',
            assistant_response='A',
        )
        self.assertFalse(result)
        self.assertEqual(ConvModel.objects.count(), 0)

    def test_save_truncates_long_intent_to_charfield_limit(self):
        long_intent = 'x' * 200  # CharField max_length=100
        result = self.memory.save_conversation(
            user_id=self.user.id,
            user_message='Q',
            assistant_response='A',
            metadata={'intent': long_intent},
        )
        self.assertTrue(result)
        row = ConvModel.objects.get(user=self.user)
        self.assertEqual(len(row.intent), 100)


class GetConversationHistoryORMTests(TestCase):
    """get_conversation_history returns shape-compatible dicts from ORM."""

    def setUp(self):
        self.memory = ConversationMemoryFacade()
        self.user = User.objects.create_user(
            username=f'test_hist_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_returns_recent_conversations_in_descending_order(self):
        # Create 3 conversations
        for i in range(3):
            ConvModel.objects.create(
                user=self.user,
                message=f'msg {i}',
                response=f'reply {i}',
            )

        history = self.memory.get_conversation_history(self.user.id, limit=10)
        self.assertEqual(len(history), 3)
        # Most recent first (ConvModel.Meta.ordering = ['-created_at'])
        self.assertEqual(history[0]['user_message'], 'msg 2')
        self.assertEqual(history[2]['user_message'], 'msg 0')

    def test_respects_limit(self):
        for i in range(5):
            ConvModel.objects.create(
                user=self.user, message=f'm{i}', response=f'r{i}',
            )
        history = self.memory.get_conversation_history(self.user.id, limit=2)
        self.assertEqual(len(history), 2)

    def test_returns_empty_list_for_user_with_no_history(self):
        history = self.memory.get_conversation_history(self.user.id)
        self.assertEqual(history, [])

    def test_shape_preserves_legacy_keys(self):
        """The chat path's view depends on the exact dict shape from
        pre-pivot: {content, user_message, assistant_response, timestamp}."""
        ConvModel.objects.create(
            user=self.user, message='hello', response='hi',
        )
        history = self.memory.get_conversation_history(self.user.id)
        entry = history[0]
        self.assertSetEqual(
            set(entry.keys()),
            {'content', 'user_message', 'assistant_response', 'timestamp'},
        )
        self.assertEqual(
            entry['content'], 'User: hello\nAssistant: hi',
        )
        self.assertIsNotNone(entry['timestamp'])

    def test_isolates_users(self):
        other = User.objects.create_user(
            username=f'other_{uuid.uuid4().hex[:8]}', password='test',
        )
        ConvModel.objects.create(user=self.user, message='mine', response='r')
        ConvModel.objects.create(user=other, message='theirs', response='r')

        mine = self.memory.get_conversation_history(self.user.id)
        theirs = self.memory.get_conversation_history(other.id)
        self.assertEqual(len(mine), 1)
        self.assertEqual(len(theirs), 1)
        self.assertEqual(mine[0]['user_message'], 'mine')
        self.assertEqual(theirs[0]['user_message'], 'theirs')


class UpdateKnowledgeMetricsORMTests(TestCase):
    """update_knowledge_metrics counts via ORM, preserves legacy shape."""

    def setUp(self):
        self.memory = ConversationMemoryFacade()
        self.user = User.objects.create_user(
            username=f'test_metrics_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_counts_match_orm(self):
        # Create 3 conversations today, then 2 documents-with-embeddings
        for i in range(3):
            ConvModel.objects.create(
                user=self.user, message=f'm{i}', response=f'r{i}',
            )
        for i in range(2):
            _make_embedding_chunk(self.user, title=f'doc {i}')

        metrics = self.memory.update_knowledge_metrics(self.user.id)

        self.assertEqual(metrics['total_conversations'], 3)
        self.assertEqual(metrics['today_conversations'], 3)
        self.assertEqual(metrics['total_knowledge_base'], 2)
        self.assertEqual(metrics['learning_rate'], 3)

    def test_today_filter_uses_localdate(self):
        """today_conversations must use timezone.localdate() so Denver-tz
        rows that crossed midnight UTC still count as today. Same lesson
        as Session 1235 PR #2636 dashboard pivot."""
        # Create a row dated yesterday explicitly
        old_row = ConvModel.objects.create(
            user=self.user, message='old', response='r',
        )
        # Push it back via raw update (auto_now_add blocks normal assignment)
        ConvModel.objects.filter(id=old_row.id).update(
            created_at=timezone.now() - timedelta(days=2),
        )
        # Create one today
        ConvModel.objects.create(user=self.user, message='new', response='r')

        metrics = self.memory.update_knowledge_metrics(self.user.id)
        self.assertEqual(metrics['total_conversations'], 2)
        self.assertEqual(metrics['today_conversations'], 1)

    def test_returns_zero_metrics_for_user_with_no_data(self):
        metrics = self.memory.update_knowledge_metrics(self.user.id)
        self.assertEqual(metrics, {
            'total_conversations': 0,
            'today_conversations': 0,
            'total_knowledge_base': 0,
            'learning_rate': 0,
        })

    def test_shape_preserves_legacy_keys(self):
        metrics = self.memory.update_knowledge_metrics(self.user.id)
        self.assertSetEqual(
            set(metrics.keys()),
            {
                'total_conversations',
                'today_conversations',
                'total_knowledge_base',
                'learning_rate',
            },
        )


class SingletonImportContractTests(TestCase):
    """Both call sites import the module-level `conversation_memory`
    singleton — guard that the import still works after the pivot."""

    def test_singleton_is_facade_instance(self):
        self.assertIsInstance(conversation_memory, ConversationMemoryFacade)

    def test_singleton_methods_callable(self):
        # Smoke check — verifies methods exist with expected names
        self.assertTrue(hasattr(conversation_memory, 'save_conversation'))
        self.assertTrue(hasattr(conversation_memory, 'get_conversation_history'))
        self.assertTrue(hasattr(conversation_memory, 'update_knowledge_metrics'))


class NoDeadSubstrateReferencesTests(TestCase):
    """Source-level guard: conversation_memory.py contains zero live
    psycopg2.connect calls or unified_embeddings/ai_unified_platform
    queries outside of explanatory comments."""

    def _read_non_comment_lines(self, path):
        from pathlib import Path
        text = Path(path).read_text()
        out_lines = []
        in_docstring = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    continue
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if stripped.startswith('#'):
                continue
            out_lines.append(line)
        return '\n'.join(out_lines)

    def test_no_psycopg2_connect(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent.parent
        code = self._read_non_comment_lines(base / 'core/conversation_memory.py')
        self.assertNotIn('psycopg2.connect', code)
        self.assertNotIn('import psycopg2', code)

    def test_no_unified_embeddings_query(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent.parent
        code = self._read_non_comment_lines(base / 'core/conversation_memory.py')
        for marker in ('FROM unified_embeddings', 'INTO unified_embeddings'):
            self.assertNotIn(marker, code)

    def test_no_ai_unified_platform_connect(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent.parent
        code = self._read_non_comment_lines(base / 'core/conversation_memory.py')
        self.assertNotIn("database='ai_unified_platform'", code)
