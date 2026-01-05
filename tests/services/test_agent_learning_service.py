# tests/services/test_agent_learning_service.py
"""
Unit tests for AgentLearningService.

Session 662: Core Services Testing Initiative
Tests the agent learning and personalization system.
"""
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from core.services.agent_learning_service import (
    AgentLearningService,
    InteractionType,
    PreferenceCategory,
    AgentInteraction,
    LearnedPreference,
    AgentMemory,
    get_learning_service,
    record_interaction,
    get_adaptive_context,
    apply_preferences,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    with patch('redis.Redis') as mock_redis_class:
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.zadd.return_value = 1
        mock_client.zremrangebyrank.return_value = 0
        mock_client.hgetall.return_value = {}
        mock_client.hset.return_value = 1
        mock_client.delete.return_value = 1
        mock_client.scan_iter.return_value = iter([])
        mock_redis_class.return_value = mock_client
        yield {
            'redis_class': mock_redis_class,
            'client': mock_client
        }


@pytest.fixture
def learning_service(mock_redis_client):
    """Create a learning service with mocked Redis."""
    return AgentLearningService()


@pytest.fixture
def sample_input_data():
    """Sample input data for interactions."""
    return {
        'prompt': 'Create a cyberpunk cityscape at night',
        'style': 'digital-art',
        'model': 'stable-diffusion',
        'quality': 'high'
    }


@pytest.fixture
def sample_output_data():
    """Sample output data for interactions."""
    return {
        'image_url': 'https://example.com/image.png',
        'dominant_colors': ['#00ffff', '#ff00ff', '#0000ff'],
        'generation_time': 5.2
    }


# =============================================================================
# Test: Initialization
# =============================================================================

class TestAgentLearningServiceInit:
    """Tests for AgentLearningService initialization."""

    def test_init_with_default_config(self, mock_redis_client):
        """Test initialization with default Redis config."""
        service = AgentLearningService()

        assert service.redis_config['host'] == 'localhost'
        assert service.redis_config['port'] == 6379
        assert service.redis_config['db'] == 5
        assert service.redis_client is not None

    def test_init_with_custom_config(self, mock_redis_client):
        """Test initialization with custom Redis config."""
        custom_config = {'host': 'redis.example.com', 'port': 6380, 'db': 10}
        service = AgentLearningService(redis_config=custom_config)

        assert service.redis_config == custom_config

    def test_init_redis_connection_failure(self):
        """Test initialization when Redis connection fails."""
        with patch('redis.Redis') as mock_redis_class:
            mock_client = MagicMock()
            mock_client.ping.side_effect = Exception("Connection refused")
            mock_redis_class.return_value = mock_client

            service = AgentLearningService()
            assert service.redis_client is None

    def test_init_empty_caches(self, mock_redis_client):
        """Test that caches are empty on initialization."""
        service = AgentLearningService()

        assert service._user_memories == {}
        assert service._interaction_buffer == []


# =============================================================================
# Test: Interaction Recording
# =============================================================================

class TestRecordInteraction:
    """Tests for recording user interactions."""

    def test_record_interaction_creates_object(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test recording an interaction creates an AgentInteraction."""
        interaction = learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.CREATED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        assert isinstance(interaction, AgentInteraction)
        assert interaction.user_id == 1
        assert interaction.agent_name == 'ImageAgent'
        assert interaction.interaction_type == InteractionType.CREATED

    def test_record_interaction_with_rating(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test recording an interaction with a rating."""
        interaction = learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.RATED,
            input_data=sample_input_data,
            output_data=sample_output_data,
            rating=5
        )

        assert interaction.rating == 5

    def test_record_interaction_with_modification(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test recording an interaction where output was modified."""
        interaction = learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.EDITED,
            input_data=sample_input_data,
            output_data=sample_output_data,
            was_modified=True
        )

        assert interaction.was_modified is True

    def test_record_interaction_adds_to_buffer(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test that interactions are added to the buffer."""
        initial_buffer_size = len(learning_service._interaction_buffer)

        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.CREATED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        assert len(learning_service._interaction_buffer) == initial_buffer_size + 1

    def test_record_interaction_creates_memory(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test that recording creates user memory."""
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.CREATED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        memory = learning_service._user_memories.get('1:ImageAgent')
        assert memory is not None
        assert memory.user_id == 1
        assert memory.agent_name == 'ImageAgent'

    def test_record_interaction_persists_to_redis(
        self, learning_service, mock_redis_client, sample_input_data, sample_output_data
    ):
        """Test that interactions are persisted to Redis."""
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.SAVED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        mock_redis_client['client'].zadd.assert_called()


# =============================================================================
# Test: Memory Management
# =============================================================================

class TestMemoryManagement:
    """Tests for memory management."""

    def test_update_memory_increments_count(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test that interaction count is incremented."""
        for _ in range(3):
            learning_service.record_interaction(
                user_id=1,
                agent_name='ImageAgent',
                interaction_type=InteractionType.CREATED,
                input_data=sample_input_data,
                output_data=sample_output_data
            )

        memory = learning_service._user_memories.get('1:ImageAgent')
        assert memory.interaction_count == 3

    def test_short_term_memory_limit(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test that short-term memory respects limit."""
        for i in range(25):  # More than SHORT_TERM_LIMIT (20)
            learning_service.record_interaction(
                user_id=1,
                agent_name='ImageAgent',
                interaction_type=InteractionType.CREATED,
                input_data=sample_input_data,
                output_data=sample_output_data
            )

        memory = learning_service._user_memories.get('1:ImageAgent')
        assert len(memory.short_term) <= learning_service.SHORT_TERM_LIMIT

    def test_get_user_memory_returns_cached(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test that get_user_memory returns cached memory."""
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.CREATED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        memory = learning_service.get_user_memory(1, 'ImageAgent')
        assert memory is not None
        assert memory.user_id == 1

    def test_get_user_memory_no_data_returns_none(self, learning_service):
        """Test that get_user_memory returns None for non-existent user."""
        memory = learning_service.get_user_memory(999, 'NonExistentAgent')
        assert memory is None

    def test_save_memory_to_redis(
        self, learning_service, mock_redis_client, sample_input_data, sample_output_data
    ):
        """Test saving memory to Redis."""
        # Record interaction to create memory
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.SAVED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        learning_service.save_memory(1, 'ImageAgent')
        mock_redis_client['client'].hset.assert_called()


# =============================================================================
# Test: Preference Learning
# =============================================================================

class TestPreferenceLearning:
    """Tests for preference learning."""

    def test_learns_style_preference(self, learning_service):
        """Test learning style preferences from interactions."""
        input_data = {'style': 'anime', 'prompt': 'A hero'}
        output_data = {}

        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.FAVORITED,
            input_data=input_data,
            output_data=output_data
        )

        memory = learning_service._user_memories.get('1:ImageAgent')
        assert 'style:anime' in memory.long_term

    def test_learns_model_preference(self, learning_service):
        """Test learning model preferences."""
        input_data = {'model': 'flux-pro', 'prompt': 'Test'}
        output_data = {}

        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.SAVED,
            input_data=input_data,
            output_data=output_data
        )

        memory = learning_service._user_memories.get('1:ImageAgent')
        assert 'model:flux-pro' in memory.long_term

    def test_learns_theme_from_prompt(self, learning_service):
        """Test extracting themes from prompts."""
        input_data = {'prompt': 'A cyberpunk city with neon lights'}
        output_data = {}

        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.FAVORITED,
            input_data=input_data,
            output_data=output_data
        )

        memory = learning_service._user_memories.get('1:ImageAgent')
        assert 'theme:cyberpunk' in memory.long_term

    def test_positive_interaction_increases_confidence(self, learning_service):
        """Test that positive interactions increase confidence."""
        input_data = {'style': 'watercolor', 'prompt': 'Test'}
        output_data = {}

        # Multiple positive interactions
        for _ in range(5):
            learning_service.record_interaction(
                user_id=1,
                agent_name='ImageAgent',
                interaction_type=InteractionType.SAVED,
                input_data=input_data,
                output_data=output_data
            )

        memory = learning_service._user_memories.get('1:ImageAgent')
        pref = memory.long_term.get('style:watercolor')
        assert pref is not None
        assert pref.confidence > 0.5  # Started at 0.5, should increase

    def test_negative_interaction_decreases_confidence(self, learning_service):
        """Test that negative interactions decrease confidence."""
        input_data = {'style': 'photorealistic', 'prompt': 'Test'}
        output_data = {}

        # First positive interaction
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.SAVED,
            input_data=input_data,
            output_data=output_data
        )

        # Then rejection
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.REJECTED,
            input_data=input_data,
            output_data=output_data
        )

        memory = learning_service._user_memories.get('1:ImageAgent')
        pref = memory.long_term.get('style:photorealistic')
        assert pref.negative_signals >= 1

    def test_learns_color_preferences(self, learning_service):
        """Test learning color preferences from output data."""
        input_data = {'prompt': 'Abstract art'}
        output_data = {'dominant_colors': ['#ff0000', '#00ff00']}

        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.FAVORITED,
            input_data=input_data,
            output_data=output_data
        )

        memory = learning_service._user_memories.get('1:ImageAgent')
        assert 'color:#ff0000' in memory.long_term


# =============================================================================
# Test: Theme Extraction
# =============================================================================

class TestThemeExtraction:
    """Tests for theme extraction from prompts."""

    def test_extract_fantasy_theme(self, learning_service):
        """Test extracting fantasy theme."""
        themes = learning_service._extract_themes("A magical dragon in a medieval castle")
        assert 'fantasy' in themes

    def test_extract_nature_theme(self, learning_service):
        """Test extracting nature theme."""
        themes = learning_service._extract_themes("A beautiful mountain landscape with forest")
        assert 'nature' in themes

    def test_extract_multiple_themes(self, learning_service):
        """Test extracting multiple themes."""
        themes = learning_service._extract_themes("A dark gothic portrait of a person")
        assert len(themes) >= 2
        assert 'dark' in themes
        assert 'portrait' in themes

    def test_extract_no_themes(self, learning_service):
        """Test extraction with no matching themes."""
        themes = learning_service._extract_themes("Just some random text")
        assert themes == []

    def test_extract_themes_limit(self, learning_service):
        """Test that theme extraction is limited to 3."""
        prompt = "A cyberpunk fantasy nature portrait abstract"
        themes = learning_service._extract_themes(prompt)
        assert len(themes) <= 3


# =============================================================================
# Test: Get Top Preferences
# =============================================================================

class TestGetTopPreferences:
    """Tests for getting top preferences."""

    def test_get_top_preferences_empty(self, learning_service):
        """Test getting preferences when none exist."""
        prefs = learning_service.get_top_preferences(999, 'ImageAgent')
        assert prefs == []

    def test_get_top_preferences_filters_by_confidence(self, learning_service):
        """Test that low confidence preferences are filtered."""
        # Create a memory with low confidence preference
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:bad'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='bad',
            confidence=0.3,  # Below threshold
            occurrences=5,
            last_seen=datetime.now(timezone.utc),
            positive_signals=1,
            negative_signals=3
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        prefs = learning_service.get_top_preferences(1, 'ImageAgent')
        assert len(prefs) == 0

    def test_get_top_preferences_by_category(self, learning_service):
        """Test filtering preferences by category."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:anime'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='anime',
            confidence=0.8,
            occurrences=10,
            last_seen=datetime.now(timezone.utc),
            positive_signals=8,
            negative_signals=2
        )
        memory.long_term['model:flux'] = LearnedPreference(
            category=PreferenceCategory.MODEL,
            value='flux',
            confidence=0.9,
            occurrences=15,
            last_seen=datetime.now(timezone.utc),
            positive_signals=14,
            negative_signals=1
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        style_prefs = learning_service.get_top_preferences(
            1, 'ImageAgent', category=PreferenceCategory.STYLE
        )
        assert len(style_prefs) == 1
        assert style_prefs[0].value == 'anime'

    def test_get_top_preferences_sorted_by_score(self, learning_service):
        """Test that preferences are sorted by confidence * occurrences."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:low'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='low',
            confidence=0.7,
            occurrences=2,  # Score: 1.4
            last_seen=datetime.now(timezone.utc),
            positive_signals=7,
            negative_signals=3
        )
        memory.long_term['style:high'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='high',
            confidence=0.8,
            occurrences=10,  # Score: 8.0
            last_seen=datetime.now(timezone.utc),
            positive_signals=8,
            negative_signals=2
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        prefs = learning_service.get_top_preferences(1, 'ImageAgent', limit=2)
        assert prefs[0].value == 'high'

    def test_get_top_preferences_respects_limit(self, learning_service):
        """Test that limit parameter is respected."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        for i in range(10):
            memory.long_term[f'style:style{i}'] = LearnedPreference(
                category=PreferenceCategory.STYLE,
                value=f'style{i}',
                confidence=0.7,
                occurrences=5,
                last_seen=datetime.now(timezone.utc),
                positive_signals=7,
                negative_signals=3
            )
        learning_service._user_memories['1:ImageAgent'] = memory

        prefs = learning_service.get_top_preferences(1, 'ImageAgent', limit=3)
        assert len(prefs) == 3


# =============================================================================
# Test: Adaptive Context
# =============================================================================

class TestAdaptiveContext:
    """Tests for adaptive context generation."""

    def test_get_adaptive_context_empty(self, learning_service):
        """Test getting context when no preferences exist."""
        context = learning_service.get_adaptive_context(999, 'ImageAgent')
        assert context == ""

    def test_get_adaptive_context_with_style(self, learning_service):
        """Test context includes style preferences."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:anime'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='anime',
            confidence=0.8,
            occurrences=10,
            last_seen=datetime.now(timezone.utc),
            positive_signals=8,
            negative_signals=2
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        context = learning_service.get_adaptive_context(1, 'ImageAgent')
        assert 'anime' in context
        assert 'Preferred styles' in context

    def test_get_adaptive_context_with_multiple_categories(self, learning_service):
        """Test context includes multiple preference categories."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:watercolor'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='watercolor',
            confidence=0.8,
            occurrences=10,
            last_seen=datetime.now(timezone.utc),
            positive_signals=8,
            negative_signals=2
        )
        memory.long_term['theme:fantasy'] = LearnedPreference(
            category=PreferenceCategory.THEME,
            value='fantasy',
            confidence=0.75,
            occurrences=8,
            last_seen=datetime.now(timezone.utc),
            positive_signals=6,
            negative_signals=2
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        context = learning_service.get_adaptive_context(1, 'ImageAgent')
        assert 'watercolor' in context
        assert 'fantasy' in context


# =============================================================================
# Test: Apply Preferences to Params
# =============================================================================

class TestApplyPreferencesToParams:
    """Tests for applying preferences to generation parameters."""

    def test_apply_preferences_fills_missing(self, learning_service):
        """Test that preferences fill in missing parameters."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:anime'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='anime',
            confidence=0.8,
            occurrences=10,
            last_seen=datetime.now(timezone.utc),
            positive_signals=8,
            negative_signals=2
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        params = {'prompt': 'A hero'}
        result = learning_service.apply_preferences_to_params(1, 'ImageAgent', params)

        assert result['style'] == 'anime'
        assert result['prompt'] == 'A hero'

    def test_apply_preferences_respects_user_params(self, learning_service):
        """Test that user parameters take precedence."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:anime'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='anime',
            confidence=0.8,
            occurrences=10,
            last_seen=datetime.now(timezone.utc),
            positive_signals=8,
            negative_signals=2
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        params = {'prompt': 'A hero', 'style': 'photorealistic'}
        result = learning_service.apply_preferences_to_params(1, 'ImageAgent', params)

        assert result['style'] == 'photorealistic'  # User param preserved

    def test_apply_preferences_no_prefs(self, learning_service):
        """Test with no preferences available."""
        params = {'prompt': 'A hero'}
        result = learning_service.apply_preferences_to_params(999, 'ImageAgent', params)

        assert result == params


# =============================================================================
# Test: Knowledge Sharing
# =============================================================================

class TestKnowledgeSharing:
    """Tests for knowledge sharing integration."""

    def test_share_learning_no_preferences(self, learning_service):
        """Test sharing when no preferences exist (no-op)."""
        # Should not raise
        learning_service.share_learning_as_knowledge(999, 'ImageAgent')

    def test_share_learning_with_preferences(self, learning_service):
        """Test sharing preferences with collaboration hub."""
        memory = AgentMemory(user_id=1, agent_name='ImageAgent')
        memory.long_term['style:anime'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='anime',
            confidence=0.8,
            occurrences=10,
            last_seen=datetime.now(timezone.utc),
            positive_signals=8,
            negative_signals=2
        )
        learning_service._user_memories['1:ImageAgent'] = memory

        # Patch the import inside the function
        with patch('core.services.agent_collaboration_hub.get_collaboration_hub') as mock_get_hub:
            mock_hub = MagicMock()
            mock_get_hub.return_value = mock_hub
            learning_service.share_learning_as_knowledge(1, 'ImageAgent')
            mock_hub.share_knowledge.assert_called_once()


# =============================================================================
# Test: Statistics
# =============================================================================

class TestStatistics:
    """Tests for learning statistics."""

    def test_get_learning_stats_empty(self, learning_service):
        """Test stats with no data."""
        stats = learning_service.get_learning_stats(999)

        assert stats['total_interactions'] == 0
        assert stats['agents_interacted'] == []

    def test_get_learning_stats_with_data(self, learning_service, sample_input_data, sample_output_data):
        """Test stats with interactions."""
        # Record some interactions
        for _ in range(5):
            learning_service.record_interaction(
                user_id=1,
                agent_name='ImageAgent',
                interaction_type=InteractionType.CREATED,
                input_data=sample_input_data,
                output_data=sample_output_data
            )

        stats = learning_service.get_learning_stats(1)

        assert stats['total_interactions'] == 5
        assert 'ImageAgent' in stats['agents_interacted']

    def test_get_user_preferences_summary_no_data(self, learning_service):
        """Test preferences summary with no data."""
        summary = learning_service.get_user_preferences_summary(999, 'ImageAgent')

        assert summary['status'] == 'no_data'

    def test_get_user_preferences_summary_with_data(
        self, learning_service, sample_input_data, sample_output_data
    ):
        """Test preferences summary with data."""
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.SAVED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        summary = learning_service.get_user_preferences_summary(1, 'ImageAgent')

        assert summary['status'] == 'ok'
        assert summary['interaction_count'] >= 1


# =============================================================================
# Test: Clear Preferences
# =============================================================================

class TestClearPreferences:
    """Tests for clearing user preferences."""

    def test_clear_preferences_specific_agent(
        self, learning_service, mock_redis_client, sample_input_data, sample_output_data
    ):
        """Test clearing preferences for a specific agent."""
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.SAVED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        learning_service.clear_user_preferences(1, 'ImageAgent')

        memory = learning_service.get_user_memory(1, 'ImageAgent')
        assert memory is None

    def test_clear_preferences_all_agents(
        self, learning_service, mock_redis_client, sample_input_data, sample_output_data
    ):
        """Test clearing preferences for all agents."""
        learning_service.record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.SAVED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )
        learning_service.record_interaction(
            user_id=1,
            agent_name='VideoAgent',
            interaction_type=InteractionType.SAVED,
            input_data=sample_input_data,
            output_data=sample_output_data
        )

        learning_service.clear_user_preferences(1)

        assert learning_service.get_user_memory(1, 'ImageAgent') is None
        assert learning_service.get_user_memory(1, 'VideoAgent') is None


# =============================================================================
# Test: Global Instance
# =============================================================================

class TestGlobalInstance:
    """Tests for global service instance."""

    def test_get_learning_service_creates_instance(self, mock_redis_client):
        """Test that get_learning_service creates instance."""
        import core.services.agent_learning_service as module
        module._learning_service = None  # Reset

        service = get_learning_service()
        assert service is not None

    def test_get_learning_service_reuses_instance(self, mock_redis_client):
        """Test that get_learning_service reuses existing instance."""
        import core.services.agent_learning_service as module
        module._learning_service = None  # Reset

        service1 = get_learning_service()
        service2 = get_learning_service()

        assert service1 is service2


# =============================================================================
# Test: Convenience Functions
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_record_interaction_function(self, mock_redis_client):
        """Test record_interaction convenience function."""
        import core.services.agent_learning_service as module
        module._learning_service = None  # Reset

        interaction = record_interaction(
            user_id=1,
            agent_name='ImageAgent',
            interaction_type='created',
            input_data={'prompt': 'Test'},
            output_data={}
        )

        assert interaction.user_id == 1

    def test_get_adaptive_context_function(self, mock_redis_client):
        """Test get_adaptive_context convenience function."""
        import core.services.agent_learning_service as module
        module._learning_service = None  # Reset

        context = get_adaptive_context(999, 'ImageAgent')
        assert context == ""

    def test_apply_preferences_function(self, mock_redis_client):
        """Test apply_preferences convenience function."""
        import core.services.agent_learning_service as module
        module._learning_service = None  # Reset

        params = {'prompt': 'Test'}
        result = apply_preferences(999, 'ImageAgent', params)

        assert result == params


# =============================================================================
# Test: AgentInteraction Dataclass
# =============================================================================

class TestAgentInteractionDataclass:
    """Tests for AgentInteraction dataclass."""

    def test_to_dict(self):
        """Test converting interaction to dict."""
        interaction = AgentInteraction(
            id='test-123',
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.CREATED,
            input_data={'prompt': 'Test'},
            output_data={'url': 'http://example.com'},
            rating=5
        )

        result = interaction.to_dict()

        assert result['id'] == 'test-123'
        assert result['user_id'] == 1
        assert result['interaction_type'] == 'created'
        assert result['rating'] == 5


# =============================================================================
# Test: LearnedPreference Dataclass
# =============================================================================

class TestLearnedPreferenceDataclass:
    """Tests for LearnedPreference dataclass."""

    def test_to_dict(self):
        """Test converting preference to dict."""
        pref = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='anime',
            confidence=0.85,
            occurrences=10,
            last_seen=datetime(2025, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            positive_signals=8,
            negative_signals=2
        )

        result = pref.to_dict()

        assert result['category'] == 'style'
        assert result['value'] == 'anime'
        assert result['confidence'] == 0.85
        assert result['occurrences'] == 10


# =============================================================================
# Test: Redis Error Handling
# =============================================================================

class TestRedisErrorHandling:
    """Tests for Redis error handling."""

    def test_persist_interaction_handles_redis_error(self, learning_service, mock_redis_client):
        """Test that Redis errors are handled gracefully."""
        mock_redis_client['client'].zadd.side_effect = Exception("Redis error")

        # Should not raise
        interaction = AgentInteraction(
            id='test-123',
            user_id=1,
            agent_name='ImageAgent',
            interaction_type=InteractionType.CREATED,
            input_data={},
            output_data={}
        )
        learning_service._persist_interaction(interaction)

    def test_load_memory_handles_redis_error(self, learning_service, mock_redis_client):
        """Test that loading memory handles Redis errors."""
        mock_redis_client['client'].hgetall.side_effect = Exception("Redis error")

        result = learning_service._load_memory_from_redis(1, 'ImageAgent')
        assert result is None

    def test_save_memory_handles_redis_error(self, learning_service, mock_redis_client):
        """Test that saving memory handles Redis errors."""
        mock_redis_client['client'].hset.side_effect = Exception("Redis error")

        # Create memory
        learning_service._user_memories['1:ImageAgent'] = AgentMemory(
            user_id=1, agent_name='ImageAgent'
        )
        learning_service._user_memories['1:ImageAgent'].long_term['style:test'] = LearnedPreference(
            category=PreferenceCategory.STYLE,
            value='test',
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(timezone.utc),
            positive_signals=4,
            negative_signals=1
        )

        # Should not raise
        learning_service.save_memory(1, 'ImageAgent')
