# tests/services/test_review_document_service.py
"""
Unit tests for ReviewDocumentService.

Session 662: Core Services Testing Initiative
Tests the Chief of Staff review document generation system.
"""
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, PropertyMock
from uuid import uuid4

import pytest
from django.core.exceptions import ObjectDoesNotExist

from core.services.review_document import ReviewDocumentService


@contextmanager
def mock_transaction_atomic():
    """Mock context manager for transaction.atomic()."""
    yield


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_openai():
    """Mock OpenAI client for ReviewDocumentService."""
    with patch('core.services.review_document.OpenAI') as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()

        # Default response structure
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            'neutral_summary': 'Test summary of the proposal',
            'pro_case': '- Pro argument 1\n- Pro argument 2',
            'con_case': '- Con argument 1\n- Con argument 2',
            'open_questions': ['Question 1?', 'Question 2?'],
            'key_evidence': {
                'pro': ['Evidence for pro 1'],
                'con': ['Evidence for con 1']
            },
            'ai_recommendation': 'Proceed with caution',
            'ai_lean': 'lean_approve',
            'ai_confidence': 0.75
        })
        mock_response.choices = [mock_choice]

        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        yield {
            'openai': mock_openai_class,
            'client': mock_client,
            'response': mock_response,
            'choice': mock_choice
        }


@pytest.fixture
def review_service(mock_openai):
    """Create a ReviewDocumentService with mocked OpenAI."""
    return ReviewDocumentService()


@pytest.fixture
def mock_artifact():
    """Create a mock artifact for testing."""
    mock = MagicMock()
    mock.id = uuid4()
    mock.artifact_type = 'proposal'
    mock.get_artifact_type_display.return_value = 'Proposal'
    mock.title = 'Test Proposal: New Feature Implementation'
    mock.description = 'This proposal suggests implementing a new feature for the platform.'
    mock.details = {'key': 'value', 'feature': 'test'}
    mock.importance_score = 0.75
    mock.urgency_score = 0.5
    mock.composite_score = 0.65

    # Source agent
    mock.source_agent = MagicMock()
    mock.source_agent.name = 'TestAgent'

    # Conversation with properly named participants
    mock.conversation = MagicMock()
    mock.conversation.topic = 'Test Discussion Topic'
    mock.conversation.conclusion = 'The agents reached a test conclusion.'

    # Create mock participants with proper name property
    participant1 = MagicMock()
    participant1.name = 'Agent1'
    participant2 = MagicMock()
    participant2.name = 'Agent2'
    mock.conversation.participants.all.return_value = [participant1, participant2]

    return mock


@pytest.fixture
def mock_dream():
    """Create a mock dream for testing."""
    mock = MagicMock()
    mock.id = uuid4()
    mock.title = 'Test Dream: Innovative Idea'
    mock.content = 'A detailed description of the dream content that spans multiple sentences.'
    mock.dreamed_at = datetime.now(timezone.utc)
    mock.agent = MagicMock()
    mock.agent.name = 'DreamerAgent'
    mock.vividness_score = 0.8
    mock.creativity_score = 0.9
    mock.actionability_score = 0.7
    mock.relevance_score = 0.6
    mock.composite_score = 0.75
    mock.inspiration_source = 'Recent market trends'
    mock.related_topics = ['AI', 'automation', 'efficiency']
    mock.dream_type = 'creative_idea'

    return mock


@pytest.fixture
def mock_review_document():
    """Create a mock review document for testing."""
    mock = MagicMock()
    mock.id = uuid4()
    mock.target_type = 'artifact'
    mock.target_id = uuid4()
    mock.neutral_summary = 'Original summary'
    mock.pro_case = '- Pro 1'
    mock.con_case = '- Con 1'
    mock.open_questions = ['Question?']
    mock.key_evidence = {'pro': [], 'con': []}
    mock.ai_recommendation = 'Original recommendation'
    mock.ai_lean = 'neutral'
    mock.ai_confidence = 0.5
    return mock


# =============================================================================
# Test: Initialization
# =============================================================================

class TestReviewDocumentServiceInit:
    """Tests for ReviewDocumentService initialization."""

    def test_init_creates_openai_client(self, mock_openai):
        """Test that initialization creates OpenAI client."""
        service = ReviewDocumentService()
        assert service.client is not None
        mock_openai['openai'].assert_called_once()


# =============================================================================
# Test: Context Gathering
# =============================================================================

class TestGatherContext:
    """Tests for context gathering from artifacts."""

    def test_gather_context_basic(self, review_service, mock_artifact):
        """Test gathering basic context from artifact."""
        context = review_service._gather_context(mock_artifact)

        assert context['artifact_type'] == 'proposal'
        assert context['title'] == 'Test Proposal: New Feature Implementation'
        assert context['importance_score'] == 0.75
        assert context['source_agent'] == 'TestAgent'

    def test_gather_context_includes_conversation(self, review_service, mock_artifact):
        """Test context includes conversation details."""
        context = review_service._gather_context(mock_artifact)

        assert context['conversation_topic'] == 'Test Discussion Topic'
        assert context['conversation_conclusion'] == 'The agents reached a test conclusion.'
        assert 'conversation_participants' in context

    def test_gather_context_handles_no_conversation(self, review_service, mock_artifact):
        """Test context handles artifact without conversation."""
        mock_artifact.conversation = None
        context = review_service._gather_context(mock_artifact)

        assert 'conversation_topic' not in context
        assert context['source_agent'] == 'TestAgent'

    def test_gather_context_handles_no_source_agent(self, review_service, mock_artifact):
        """Test context handles artifact without source agent."""
        mock_artifact.source_agent = None
        context = review_service._gather_context(mock_artifact)

        assert context['source_agent'] is None


# =============================================================================
# Test: Analysis Generation
# =============================================================================

class TestGenerateAnalysis:
    """Tests for analysis generation."""

    def test_generate_analysis_calls_openai(self, review_service, mock_openai, mock_artifact):
        """Test that analysis generation calls OpenAI."""
        context = review_service._gather_context(mock_artifact)
        review_service._generate_analysis(mock_artifact, context)

        mock_openai['client'].chat.completions.create.assert_called_once()

    def test_generate_analysis_returns_all_fields(self, review_service, mock_artifact):
        """Test that analysis includes all required fields."""
        context = review_service._gather_context(mock_artifact)
        analysis = review_service._generate_analysis(mock_artifact, context)

        assert 'neutral_summary' in analysis
        assert 'pro_case' in analysis
        assert 'con_case' in analysis
        assert 'open_questions' in analysis
        assert 'key_evidence' in analysis
        assert 'ai_recommendation' in analysis
        assert 'ai_lean' in analysis
        assert 'ai_confidence' in analysis

    def test_generate_analysis_validates_ai_lean(self, review_service, mock_openai, mock_artifact):
        """Test that invalid ai_lean is corrected to neutral."""
        mock_openai['choice'].message.content = json.dumps({
            'neutral_summary': 'Test',
            'pro_case': 'Pro',
            'con_case': 'Con',
            'open_questions': [],
            'key_evidence': {'pro': [], 'con': []},
            'ai_recommendation': 'Test',
            'ai_lean': 'invalid_lean',  # Invalid
            'ai_confidence': 0.5
        })

        context = review_service._gather_context(mock_artifact)
        analysis = review_service._generate_analysis(mock_artifact, context)

        assert analysis['ai_lean'] == 'neutral'

    def test_generate_analysis_validates_ai_confidence_too_high(self, review_service, mock_openai, mock_artifact):
        """Test that ai_confidence above 1.0 is clamped."""
        mock_openai['choice'].message.content = json.dumps({
            'neutral_summary': 'Test',
            'pro_case': 'Pro',
            'con_case': 'Con',
            'open_questions': [],
            'key_evidence': {'pro': [], 'con': []},
            'ai_recommendation': 'Test',
            'ai_lean': 'neutral',
            'ai_confidence': 1.5  # Too high
        })

        context = review_service._gather_context(mock_artifact)
        analysis = review_service._generate_analysis(mock_artifact, context)

        assert analysis['ai_confidence'] == 1.0

    def test_generate_analysis_validates_ai_confidence_negative(self, review_service, mock_openai, mock_artifact):
        """Test that negative ai_confidence is clamped to 0."""
        mock_openai['choice'].message.content = json.dumps({
            'neutral_summary': 'Test',
            'pro_case': 'Pro',
            'con_case': 'Con',
            'open_questions': [],
            'key_evidence': {'pro': [], 'con': []},
            'ai_recommendation': 'Test',
            'ai_lean': 'neutral',
            'ai_confidence': -0.5  # Negative
        })

        context = review_service._gather_context(mock_artifact)
        analysis = review_service._generate_analysis(mock_artifact, context)

        assert analysis['ai_confidence'] == 0.0

    def test_generate_analysis_handles_invalid_confidence_type(self, review_service, mock_openai, mock_artifact):
        """Test that non-numeric ai_confidence defaults to 0.5."""
        mock_openai['choice'].message.content = json.dumps({
            'neutral_summary': 'Test',
            'pro_case': 'Pro',
            'con_case': 'Con',
            'open_questions': [],
            'key_evidence': {'pro': [], 'con': []},
            'ai_recommendation': 'Test',
            'ai_lean': 'neutral',
            'ai_confidence': 'not a number'  # Invalid type
        })

        context = review_service._gather_context(mock_artifact)
        analysis = review_service._generate_analysis(mock_artifact, context)

        assert analysis['ai_confidence'] == 0.5

    def test_generate_analysis_fallback_on_error(self, review_service, mock_openai, mock_artifact):
        """Test that analysis returns fallback on API error."""
        mock_openai['client'].chat.completions.create.side_effect = Exception("API Error")

        context = review_service._gather_context(mock_artifact)
        analysis = review_service._generate_analysis(mock_artifact, context)

        assert analysis['ai_lean'] == 'neutral'
        assert analysis['ai_confidence'] == 0.3
        assert 'Unable to generate' in analysis['ai_recommendation']


# =============================================================================
# Test: Generate Review Document
# =============================================================================

class TestGenerateReviewDocument:
    """Tests for generating review documents."""

    def test_generate_review_document_creates_document(self, review_service, mock_artifact):
        """Test that generate_review_document creates a ReviewDocument."""
        with patch('core.services.review_document.transaction') as mock_transaction:
            mock_transaction.atomic = mock_transaction_atomic
            with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
                with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat:
                    mock_review_doc = MagicMock()
                    mock_review_doc.id = uuid4()
                    mock_review_doc.ai_lean = 'lean_approve'
                    mock_review_doc.ai_confidence = 0.75
                    mock_review_doc_class.objects.create.return_value = mock_review_doc

                    result = review_service.generate_review_document(mock_artifact)

                    mock_review_doc_class.objects.create.assert_called_once()
                    assert result == mock_review_doc

    def test_generate_review_document_creates_side_chats(self, review_service, mock_artifact):
        """Test that side chats are created for pro and con."""
        with patch('core.services.review_document.transaction') as mock_transaction:
            mock_transaction.atomic = mock_transaction_atomic
            with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
                with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat:
                    mock_review_doc = MagicMock()
                    mock_review_doc.id = uuid4()
                    mock_review_doc.ai_lean = 'lean_approve'
                    mock_review_doc.ai_confidence = 0.75
                    mock_review_doc_class.objects.create.return_value = mock_review_doc

                    review_service.generate_review_document(mock_artifact)

                    # Verify two side chats created (pro and con)
                    assert mock_side_chat.objects.create.call_count == 2


# =============================================================================
# Test: Get or Create for Artifact
# =============================================================================

class TestGetOrCreateForArtifact:
    """Tests for get_or_create_for_artifact."""

    def test_get_existing_review_document(self, review_service):
        """Test returning existing review document."""
        artifact_id = uuid4()

        with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
            mock_existing = MagicMock()
            mock_review_doc_class.objects.get.return_value = mock_existing

            result = review_service.get_or_create_for_artifact(artifact_id)

            assert result == mock_existing
            mock_review_doc_class.objects.get.assert_called_once_with(
                target_type='artifact',
                target_id=artifact_id
            )

    def test_create_new_review_document(self, review_service, mock_artifact):
        """Test creating new review document when none exists."""
        artifact_id = mock_artifact.id

        with patch('core.services.review_document.transaction') as mock_transaction:
            mock_transaction.atomic = mock_transaction_atomic
            with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
                with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                    with patch('core.models_conversation_artifacts.SideChat'):
                        mock_review_doc_class.DoesNotExist = ObjectDoesNotExist
                        mock_review_doc_class.objects.get.side_effect = ObjectDoesNotExist
                        mock_artifact_class.objects.get.return_value = mock_artifact

                        mock_new_doc = MagicMock()
                        mock_new_doc.id = uuid4()
                        mock_new_doc.ai_lean = 'neutral'
                        mock_new_doc.ai_confidence = 0.5
                        mock_review_doc_class.objects.create.return_value = mock_new_doc

                        result = review_service.get_or_create_for_artifact(artifact_id)

                        assert result == mock_new_doc


# =============================================================================
# Test: Regenerate Review Document
# =============================================================================

class TestRegenerateReviewDocument:
    """Tests for regenerating review documents."""

    def test_regenerate_updates_fields(self, review_service, mock_review_document, mock_artifact):
        """Test that regeneration updates all fields."""
        with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
            mock_artifact_class.objects.get.return_value = mock_artifact

            result = review_service.regenerate_review_document(mock_review_document)

            mock_review_document.save.assert_called_once()
            assert result == mock_review_document

    def test_regenerate_raises_for_non_artifact(self, review_service, mock_review_document):
        """Test that regeneration raises error for non-artifact targets."""
        mock_review_document.target_type = 'dream'

        with pytest.raises(ValueError) as exc_info:
            review_service.regenerate_review_document(mock_review_document)

        assert "Can only regenerate for artifact targets" in str(exc_info.value)


# =============================================================================
# Test: Get Pending Reviews
# =============================================================================

class TestGetPendingReviews:
    """Tests for getting pending reviews."""

    def test_get_pending_reviews_filters_by_status(self, review_service):
        """Test that pending reviews filters by awaiting_human status."""
        with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
            mock_queryset = MagicMock()
            mock_review_doc_class.objects.filter.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.__getitem__ = MagicMock(return_value=[])

            review_service.get_pending_reviews()

            mock_review_doc_class.objects.filter.assert_called_once_with(
                status='awaiting_human'
            )

    def test_get_pending_reviews_respects_limit(self, review_service):
        """Test that limit parameter is respected."""
        with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
            mock_queryset = MagicMock()
            mock_review_doc_class.objects.filter.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset

            review_service.get_pending_reviews(limit=5)

            mock_queryset.__getitem__.assert_called_with(slice(None, 5, None))


# =============================================================================
# Test: Get Review Stats
# =============================================================================

class TestGetReviewStats:
    """Tests for getting review statistics."""

    def test_get_review_stats_returns_counts(self, review_service):
        """Test that stats returns count breakdowns."""
        with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
            mock_review_doc_class.objects.count.return_value = 100
            mock_review_doc_class.objects.filter.return_value.count.return_value = 25
            mock_review_doc_class.STATUS_CHOICES = [
                ('awaiting_human', 'Awaiting Human'),
                ('approved', 'Approved'),
                ('rejected', 'Rejected'),
            ]
            mock_review_doc_class.AI_LEAN_CHOICES = [
                ('lean_approve', 'Lean Approve'),
                ('neutral', 'Neutral'),
            ]

            stats = review_service.get_review_stats()

            assert stats['total'] == 100
            assert 'by_status' in stats
            assert 'by_ai_lean' in stats


# =============================================================================
# Test: Dream Context Gathering
# =============================================================================

class TestGatherDreamContext:
    """Tests for gathering dream context."""

    def test_gather_dream_context_basic(self, review_service, mock_dream):
        """Test gathering basic context from dream."""
        context = review_service._gather_dream_context(mock_dream)

        assert context['title'] == 'Test Dream: Innovative Idea'
        assert context['source_agent'] == 'DreamerAgent'
        assert context['dream_type'] == 'Agent Dream'

    def test_gather_dream_context_includes_scores(self, review_service, mock_dream):
        """Test context includes dream scores."""
        context = review_service._gather_dream_context(mock_dream)

        assert context['vividness_score'] == 0.8
        assert context['creativity_score'] == 0.9
        assert context['actionability_score'] == 0.7
        assert context['composite_score'] == 0.75

    def test_gather_dream_context_truncates_content(self, review_service, mock_dream):
        """Test that long content is truncated in description."""
        mock_dream.content = 'A' * 500  # Long content
        context = review_service._gather_dream_context(mock_dream)

        assert len(context['description']) <= 203  # 200 + '...'

    def test_gather_dream_context_handles_missing_agent(self, review_service, mock_dream):
        """Test context handles dream without agent."""
        mock_dream.agent = None
        context = review_service._gather_dream_context(mock_dream)

        assert context['source_agent'] == 'Unknown'


# =============================================================================
# Test: Generate Dream Review
# =============================================================================

class TestGenerateDreamReview:
    """Tests for generating dream reviews."""

    def test_generate_dream_review_creates_document(self, review_service, mock_dream):
        """Test that generate_dream_review creates a ReviewDocument."""
        with patch('core.services.review_document.transaction') as mock_transaction:
            mock_transaction.atomic = mock_transaction_atomic
            with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
                with patch('core.models_conversation_artifacts.SideChat'):
                    mock_review_doc = MagicMock()
                    mock_review_doc.id = uuid4()
                    mock_review_doc.ai_lean = 'lean_approve'
                    mock_review_doc.ai_confidence = 0.75
                    mock_review_doc_class.objects.create.return_value = mock_review_doc

                    result = review_service.generate_dream_review(mock_dream)

                    mock_review_doc_class.objects.create.assert_called_once()
                    assert result == mock_review_doc

    def test_generate_dream_review_sets_target_type(self, review_service, mock_dream):
        """Test that target_type is set to 'dream'."""
        with patch('core.services.review_document.transaction') as mock_transaction:
            mock_transaction.atomic = mock_transaction_atomic
            with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
                with patch('core.models_conversation_artifacts.SideChat'):
                    mock_review_doc = MagicMock()
                    mock_review_doc.id = uuid4()
                    mock_review_doc.ai_lean = 'lean_approve'
                    mock_review_doc.ai_confidence = 0.75
                    mock_review_doc_class.objects.create.return_value = mock_review_doc

                    review_service.generate_dream_review(mock_dream)

                    call_kwargs = mock_review_doc_class.objects.create.call_args[1]
                    assert call_kwargs['target_type'] == 'dream'


# =============================================================================
# Test: Dream Analysis
# =============================================================================

class TestGenerateDreamAnalysis:
    """Tests for dream analysis generation."""

    def test_generate_dream_analysis_returns_all_fields(self, review_service, mock_dream):
        """Test that dream analysis includes all required fields."""
        context = review_service._gather_dream_context(mock_dream)
        analysis = review_service._generate_dream_analysis(mock_dream, context)

        assert 'neutral_summary' in analysis
        assert 'pro_case' in analysis
        assert 'con_case' in analysis
        assert 'ai_lean' in analysis
        assert 'ai_confidence' in analysis

    def test_generate_dream_analysis_fallback_on_error(self, review_service, mock_openai, mock_dream):
        """Test fallback analysis on API error."""
        mock_openai['client'].chat.completions.create.side_effect = Exception("API Error")

        context = review_service._gather_dream_context(mock_dream)
        analysis = review_service._generate_dream_analysis(mock_dream, context)

        assert analysis['ai_lean'] == 'neutral'
        assert analysis['ai_confidence'] == 0.3


# =============================================================================
# Test: Fallback Dream Analysis
# =============================================================================

class TestFallbackDreamAnalysis:
    """Tests for fallback dream analysis."""

    def test_fallback_dream_analysis_structure(self, review_service):
        """Test fallback analysis has correct structure."""
        context = {
            'source_agent': 'TestAgent',
            'title': 'Test Dream',
        }

        analysis = review_service._fallback_dream_analysis(context)

        assert 'neutral_summary' in analysis
        assert 'pro_case' in analysis
        assert 'con_case' in analysis
        assert analysis['ai_lean'] == 'neutral'
        assert analysis['ai_confidence'] == 0.3


# =============================================================================
# Test: Get or Create for Dream
# =============================================================================

class TestGetOrCreateForDream:
    """Tests for get_or_create_for_dream."""

    def test_get_existing_dream_review(self, review_service):
        """Test returning existing dream review."""
        dream_id = uuid4()

        with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
            mock_existing = MagicMock()
            mock_review_doc_class.objects.get.return_value = mock_existing

            result = review_service.get_or_create_for_dream(dream_id)

            assert result == mock_existing
            mock_review_doc_class.objects.get.assert_called_once_with(
                target_type='dream',
                target_id=dream_id
            )

    def test_create_new_dream_review(self, review_service, mock_dream):
        """Test creating new dream review when none exists."""
        dream_id = mock_dream.id

        with patch('core.services.review_document.transaction') as mock_transaction:
            mock_transaction.atomic = mock_transaction_atomic
            with patch('core.models_conversation_artifacts.ReviewDocument') as mock_review_doc_class:
                with patch('core.models_unified_system.AgentDream') as mock_dream_class:
                    with patch('core.models_conversation_artifacts.SideChat'):
                        mock_review_doc_class.DoesNotExist = ObjectDoesNotExist
                        mock_review_doc_class.objects.get.side_effect = ObjectDoesNotExist
                        mock_dream_class.objects.get.return_value = mock_dream

                        mock_new_doc = MagicMock()
                        mock_new_doc.id = uuid4()
                        mock_new_doc.ai_lean = 'neutral'
                        mock_new_doc.ai_confidence = 0.5
                        mock_review_doc_class.objects.create.return_value = mock_new_doc

                        result = review_service.get_or_create_for_dream(dream_id)

                        assert result == mock_new_doc


# =============================================================================
# Test: Singleton Instance
# =============================================================================

class TestSingletonInstance:
    """Tests for the module-level singleton instance."""

    def test_review_service_singleton_exists(self, mock_openai):
        """Test that review_service singleton is created."""
        from core.services.review_document import review_service
        assert review_service is not None
        assert isinstance(review_service, ReviewDocumentService)
