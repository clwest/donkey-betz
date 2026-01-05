# tests/services/test_side_chat_service.py
"""
Unit tests for SideChatService.

Session 662: Core Services Testing Initiative
Tests the Pro/Con side chat debate system.
"""
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from django.core.exceptions import ObjectDoesNotExist

from core.services.side_chat import SideChatService


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_openai():
    """Mock OpenAI client for SideChatService."""
    with patch('core.services.side_chat.OpenAI') as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_choice = MagicMock()
        mock_choice.message.content = "This is a thoughtful response from the advocate."
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
def side_chat_service(mock_openai):
    """Create a SideChatService with mocked OpenAI."""
    return SideChatService()


@pytest.fixture
def mock_review_doc():
    """Create a mock review document for testing."""
    mock = MagicMock()
    mock.id = uuid4()
    mock.target_type = 'artifact'
    mock.target_id = uuid4()
    mock.neutral_summary = 'This is a neutral summary of the proposal.'
    mock.pro_case = '- Pro point 1\n- Pro point 2'
    mock.con_case = '- Con point 1\n- Con point 2'
    mock.open_questions = ['Question 1?', 'Question 2?']
    mock.key_evidence = {'pro': ['Evidence 1'], 'con': ['Counter evidence 1']}
    mock.ai_recommendation = 'Consider implementing with modifications.'
    mock.ai_lean = 'lean_approve'
    mock.ai_confidence = 0.75
    mock.questions_asked_pro = 0
    mock.questions_asked_con = 0
    return mock


@pytest.fixture
def mock_side_chat():
    """Create a mock side chat for testing."""
    mock = MagicMock()
    mock.messages = []
    mock.message_count = 0
    mock.side = 'pro'
    return mock


@pytest.fixture
def mock_artifact():
    """Create a mock artifact for context building."""
    mock = MagicMock()
    mock.get_artifact_type_display.return_value = 'Proposal'
    mock.title = 'Test Proposal'
    mock.description = 'A test proposal description'
    mock.importance_score = 0.75
    mock.urgency_score = 0.5
    return mock


@pytest.fixture
def mock_dream():
    """Create a mock dream for context building."""
    mock = MagicMock()
    mock.title = 'Test Dream'
    mock.dream_type = 'creative_idea'
    mock.agent = MagicMock()
    mock.agent.name = 'TestAgent'
    mock.inspiration_source = 'Market trends'
    mock.content = 'Dream content goes here'
    mock.actionability_score = 0.8
    mock.creativity_score = 0.9
    mock.composite_score = 0.85
    return mock


# =============================================================================
# Test: Initialization
# =============================================================================

class TestSideChatServiceInit:
    """Tests for SideChatService initialization."""

    def test_init_creates_openai_client(self, mock_openai):
        """Test that initialization creates OpenAI client."""
        service = SideChatService()
        assert service.client is not None
        mock_openai['openai'].assert_called_once()

    def test_system_prompts_exist(self, side_chat_service):
        """Test that system prompts are defined."""
        assert 'Pro Advocate' in side_chat_service.PRO_SYSTEM_PROMPT
        assert 'Con Skeptic' in side_chat_service.CON_SYSTEM_PROMPT

    def test_question_warning_threshold(self, side_chat_service):
        """Test that question warning threshold is set."""
        assert side_chat_service.QUESTION_WARNING_THRESHOLD == 5


# =============================================================================
# Test: Ask Side
# =============================================================================

class TestAskSide:
    """Tests for ask_side method."""

    def test_ask_side_pro(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test asking the pro side."""
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, True)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                result = side_chat_service.ask_side(mock_review_doc, 'pro', 'Why should we approve?')

                assert result['side'] == 'pro'
                assert result['question'] == 'Why should we approve?'
                assert 'answer' in result
                mock_openai['client'].chat.completions.create.assert_called_once()

    def test_ask_side_con(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test asking the con side."""
        mock_side_chat.side = 'con'
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, True)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                result = side_chat_service.ask_side(mock_review_doc, 'con', 'What are the risks?')

                assert result['side'] == 'con'
                mock_openai['client'].chat.completions.create.assert_called_once()

    def test_ask_side_invalid_side(self, side_chat_service, mock_review_doc):
        """Test that invalid side raises error."""
        with pytest.raises(ValueError) as exc_info:
            side_chat_service.ask_side(mock_review_doc, 'invalid', 'Question')

        assert "Side must be 'pro' or 'con'" in str(exc_info.value)

    def test_ask_side_updates_question_count_pro(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test that pro question count is updated."""
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, False)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                side_chat_service.ask_side(mock_review_doc, 'pro', 'Question')

                assert mock_review_doc.questions_asked_pro == 1
                mock_review_doc.save.assert_called()

    def test_ask_side_updates_question_count_con(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test that con question count is updated."""
        mock_side_chat.side = 'con'
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, False)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                side_chat_service.ask_side(mock_review_doc, 'con', 'Question')

                assert mock_review_doc.questions_asked_con == 1
                mock_review_doc.save.assert_called()

    def test_ask_side_adds_messages(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test that messages are added to chat history."""
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, False)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                side_chat_service.ask_side(mock_review_doc, 'pro', 'My question')

                # Verify add_message was called twice (user and assistant)
                assert mock_side_chat.add_message.call_count == 2

    def test_ask_side_analysis_paralysis_warning(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test that analysis paralysis warning is added after threshold."""
        mock_review_doc.questions_asked_pro = 3
        mock_review_doc.questions_asked_con = 2

        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, False)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                result = side_chat_service.ask_side(mock_review_doc, 'pro', 'Another question')

                assert "You've asked" in result['answer']
                assert "Consider making a decision" in result['answer']

    def test_ask_side_api_error_fallback(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test fallback message on API error."""
        mock_openai['client'].chat.completions.create.side_effect = Exception("API Error")

        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, False)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                result = side_chat_service.ask_side(mock_review_doc, 'pro', 'Question')

                assert 'apologize' in result['answer'].lower()
                assert 'rephrasing' in result['answer'].lower()

    def test_ask_side_returns_total_questions(self, side_chat_service, mock_openai, mock_review_doc, mock_side_chat):
        """Test that result includes total questions count."""
        mock_review_doc.questions_asked_pro = 2
        mock_review_doc.questions_asked_con = 1

        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
                mock_side_chat_class.objects.get_or_create.return_value = (mock_side_chat, False)
                mock_artifact_class.DoesNotExist = ObjectDoesNotExist
                mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

                result = side_chat_service.ask_side(mock_review_doc, 'pro', 'Question')

                assert result['total_questions'] == 4  # 2 + 1 + 1 new


# =============================================================================
# Test: Build Context
# =============================================================================

class TestBuildContext:
    """Tests for context building."""

    def test_build_context_includes_review_doc_fields(self, side_chat_service, mock_review_doc):
        """Test that context includes all review doc fields."""
        with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
            mock_artifact_class.DoesNotExist = ObjectDoesNotExist
            mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

            context = side_chat_service._build_context(mock_review_doc, 'pro')

            assert 'neutral summary' in context.lower()
            assert 'pro case' in context.lower()
            assert 'con case' in context.lower()
            assert 'pro' in context.lower()

    def test_build_context_artifact_type(self, side_chat_service, mock_review_doc, mock_artifact):
        """Test context building for artifact target."""
        with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
            mock_artifact_class.objects.get.return_value = mock_artifact

            context = side_chat_service._build_context(mock_review_doc, 'pro')

            assert 'Test Proposal' in context
            assert 'Proposal' in context

    def test_build_context_dream_type(self, side_chat_service, mock_review_doc, mock_dream):
        """Test context building for dream target."""
        mock_review_doc.target_type = 'dream'

        with patch('core.models_unified_system.AgentDream') as mock_dream_class:
            mock_dream_class.objects.get.return_value = mock_dream

            context = side_chat_service._build_context(mock_review_doc, 'con')

            assert 'Test Dream' in context
            assert 'TestAgent' in context

    def test_build_context_handles_missing_artifact(self, side_chat_service, mock_review_doc):
        """Test context handles missing artifact gracefully."""
        with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
            mock_artifact_class.DoesNotExist = ObjectDoesNotExist
            mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

            context = side_chat_service._build_context(mock_review_doc, 'pro')

            assert 'not available' in context.lower()

    def test_build_context_includes_side_instruction(self, side_chat_service, mock_review_doc):
        """Test that context includes side-specific instruction."""
        with patch('core.models_conversation_artifacts.ExtractedArtifact') as mock_artifact_class:
            mock_artifact_class.DoesNotExist = ObjectDoesNotExist
            mock_artifact_class.objects.get.side_effect = ObjectDoesNotExist

            context_pro = side_chat_service._build_context(mock_review_doc, 'pro')
            context_con = side_chat_service._build_context(mock_review_doc, 'con')

            assert 'PRO' in context_pro
            assert 'CON' in context_con


# =============================================================================
# Test: Build Messages
# =============================================================================

class TestBuildMessages:
    """Tests for message building."""

    def test_build_messages_includes_system_prompt(self, side_chat_service, mock_side_chat):
        """Test that messages include system prompt."""
        messages = side_chat_service._build_messages(mock_side_chat, 'Context', 'Question', 'pro')

        assert messages[0]['role'] == 'system'
        assert 'Pro Advocate' in messages[0]['content']

    def test_build_messages_uses_con_prompt(self, side_chat_service, mock_side_chat):
        """Test that con side uses con system prompt."""
        mock_side_chat.side = 'con'
        messages = side_chat_service._build_messages(mock_side_chat, 'Context', 'Question', 'con')

        assert 'Con Skeptic' in messages[0]['content']

    def test_build_messages_includes_context(self, side_chat_service, mock_side_chat):
        """Test that context is included in system message."""
        messages = side_chat_service._build_messages(mock_side_chat, 'My Context', 'Question', 'pro')

        assert 'My Context' in messages[0]['content']

    def test_build_messages_includes_history(self, side_chat_service, mock_side_chat):
        """Test that conversation history is included."""
        mock_side_chat.messages = [
            {'role': 'user', 'content': 'Previous question'},
            {'role': 'assistant', 'content': 'Previous answer'}
        ]

        messages = side_chat_service._build_messages(mock_side_chat, 'Context', 'New question', 'pro')

        # System + 2 history + new question = 4
        assert len(messages) == 4
        assert messages[1]['content'] == 'Previous question'
        assert messages[2]['content'] == 'Previous answer'

    def test_build_messages_new_question_last(self, side_chat_service, mock_side_chat):
        """Test that new question is added last."""
        messages = side_chat_service._build_messages(mock_side_chat, 'Context', 'New question', 'pro')

        assert messages[-1]['role'] == 'user'
        assert messages[-1]['content'] == 'New question'


# =============================================================================
# Test: Get Chat History
# =============================================================================

class TestGetChatHistory:
    """Tests for getting chat history."""

    def test_get_chat_history_returns_messages(self, side_chat_service, mock_review_doc, mock_side_chat):
        """Test getting chat history returns messages."""
        mock_side_chat.messages = [
            {'role': 'user', 'content': 'Question'},
            {'role': 'assistant', 'content': 'Answer'}
        ]

        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            mock_side_chat_class.objects.get.return_value = mock_side_chat

            history = side_chat_service.get_chat_history(mock_review_doc, 'pro')

            assert len(history) == 2
            assert history[0]['content'] == 'Question'

    def test_get_chat_history_empty_returns_list(self, side_chat_service, mock_review_doc):
        """Test getting empty chat history returns empty list."""
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            mock_side_chat_class.DoesNotExist = ObjectDoesNotExist
            mock_side_chat_class.objects.get.side_effect = ObjectDoesNotExist

            history = side_chat_service.get_chat_history(mock_review_doc, 'pro')

            assert history == []


# =============================================================================
# Test: Clear Chat History
# =============================================================================

class TestClearChatHistory:
    """Tests for clearing chat history."""

    def test_clear_chat_history_success(self, side_chat_service, mock_review_doc, mock_side_chat):
        """Test successfully clearing chat history."""
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            mock_side_chat_class.objects.get.return_value = mock_side_chat

            result = side_chat_service.clear_chat_history(mock_review_doc, 'pro')

            assert result is True
            assert mock_side_chat.messages == []
            assert mock_side_chat.message_count == 0
            mock_side_chat.save.assert_called_once()

    def test_clear_chat_history_resets_question_count_pro(self, side_chat_service, mock_review_doc, mock_side_chat):
        """Test that clearing pro chat resets pro question count."""
        mock_review_doc.questions_asked_pro = 5

        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            mock_side_chat_class.objects.get.return_value = mock_side_chat

            side_chat_service.clear_chat_history(mock_review_doc, 'pro')

            assert mock_review_doc.questions_asked_pro == 0
            mock_review_doc.save.assert_called_once()

    def test_clear_chat_history_resets_question_count_con(self, side_chat_service, mock_review_doc, mock_side_chat):
        """Test that clearing con chat resets con question count."""
        mock_review_doc.questions_asked_con = 3
        mock_side_chat.side = 'con'

        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            mock_side_chat_class.objects.get.return_value = mock_side_chat

            side_chat_service.clear_chat_history(mock_review_doc, 'con')

            assert mock_review_doc.questions_asked_con == 0

    def test_clear_chat_history_not_exists(self, side_chat_service, mock_review_doc):
        """Test clearing non-existent chat returns False."""
        with patch('core.models_conversation_artifacts.SideChat') as mock_side_chat_class:
            mock_side_chat_class.DoesNotExist = ObjectDoesNotExist
            mock_side_chat_class.objects.get.side_effect = ObjectDoesNotExist

            result = side_chat_service.clear_chat_history(mock_review_doc, 'pro')

            assert result is False


# =============================================================================
# Test: Get Both Histories
# =============================================================================

class TestGetBothHistories:
    """Tests for getting both chat histories."""

    def test_get_both_histories_returns_dict(self, side_chat_service, mock_review_doc):
        """Test that get_both_histories returns correct structure."""
        with patch.object(side_chat_service, 'get_chat_history') as mock_get_history:
            mock_get_history.return_value = []

            result = side_chat_service.get_both_histories(mock_review_doc)

            assert 'pro' in result
            assert 'con' in result
            assert mock_get_history.call_count == 2


# =============================================================================
# Test: Singleton Instance
# =============================================================================

class TestSingletonInstance:
    """Tests for the module-level singleton instance."""

    def test_side_chat_service_singleton_exists(self, mock_openai):
        """Test that side_chat_service singleton is created."""
        from core.services.side_chat import side_chat_service
        assert side_chat_service is not None
        assert isinstance(side_chat_service, SideChatService)
