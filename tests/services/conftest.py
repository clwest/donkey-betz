# tests/services/conftest.py
"""
Service-specific pytest fixtures.

Provides mocks and fixtures for testing core services:
- OpenAI GPT-5-mini mocking
- Redis client mocking
- Kalshi API mocking
- Model fixtures for service tests
"""
import json
import base64
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


# =============================================================================
# OpenAI Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_openai_chat():
    """Mock OpenAI chat completions for GPT-5-mini services."""
    with patch('openai.OpenAI') as mock_openai:
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
        mock_openai.return_value = mock_client

        yield {
            'openai': mock_openai,
            'client': mock_client,
            'response': mock_response,
            'choice': mock_choice
        }


@pytest.fixture
def mock_openai_side_chat():
    """Mock OpenAI for SideChatService responses."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_choice = MagicMock()
        mock_choice.message.content = "This is a thoughtful response from the advocate."
        mock_response.choices = [mock_choice]

        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        yield {
            'openai': mock_openai,
            'client': mock_client,
            'response': mock_response,
            'choice': mock_choice
        }


# =============================================================================
# Redis Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_redis():
    """Mock Redis client for AgentLearningService."""
    with patch('redis.Redis') as mock_redis_class:
        mock_client = MagicMock()

        # Connection
        mock_client.ping.return_value = True

        # Sorted sets (for interaction history)
        mock_client.zadd.return_value = 1
        mock_client.zremrangebyrank.return_value = 0
        mock_client.zrange.return_value = []
        mock_client.zcard.return_value = 0

        # Hashes (for preferences)
        mock_client.hgetall.return_value = {}
        mock_client.hget.return_value = None
        mock_client.hset.return_value = 1
        mock_client.hincrby.return_value = 1
        mock_client.hdel.return_value = 1

        # Keys
        mock_client.delete.return_value = 1
        mock_client.exists.return_value = 0
        mock_client.scan_iter.return_value = iter([])
        mock_client.keys.return_value = []

        # Expiration
        mock_client.expire.return_value = True

        mock_redis_class.return_value = mock_client

        yield {
            'redis_class': mock_redis_class,
            'client': mock_client
        }


# =============================================================================
# Kalshi API Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_rsa_key():
    """Generate a test RSA key pair for Kalshi authentication."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    return {
        'pem': pem,
        'key': private_key
    }


@pytest.fixture
def mock_kalshi_env(mock_rsa_key):
    """Mock Kalshi environment variables."""
    with patch.dict('os.environ', {
        'KALSHI_API_KEY': 'test-api-key-12345',
        'KALSHI_PRIVATE_KEY': mock_rsa_key['pem']
    }):
        yield mock_rsa_key


@pytest.fixture
def mock_kalshi_requests():
    """Mock requests.Session for Kalshi API calls."""
    with patch('requests.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_response = MagicMock()

        # Default successful response
        mock_response.status_code = 200
        mock_response.json.return_value = {'balance': 10000}  # $100.00
        mock_response.content = b'{"balance": 10000}'

        mock_session.request.return_value = mock_response

        # Use MagicMock for headers to allow attribute access
        mock_headers = MagicMock()
        mock_session.headers = mock_headers

        mock_session_class.return_value = mock_session

        yield {
            'session_class': mock_session_class,
            'session': mock_session,
            'response': mock_response
        }


# =============================================================================
# Django Cache Mock
# =============================================================================

@pytest.fixture
def mock_django_cache():
    """Mock Django cache for CollectiveIntelligenceService."""
    with patch('django.core.cache.cache') as mock_cache:
        cache_store = {}

        def cache_get(key, default=None):
            return cache_store.get(key, default)

        def cache_set(key, value, timeout=None):
            cache_store[key] = value
            return True

        def cache_delete(key):
            if key in cache_store:
                del cache_store[key]
                return True
            return False

        mock_cache.get.side_effect = cache_get
        mock_cache.set.side_effect = cache_set
        mock_cache.delete.side_effect = cache_delete

        yield {
            'cache': mock_cache,
            'store': cache_store
        }


# =============================================================================
# Model Fixtures for Service Tests
# =============================================================================

@pytest.fixture
def second_agent(db):
    """Create a second test agent for multi-agent scenarios."""
    from core.models_unified_system import Agent
    return Agent.objects.create(
        name='SecondTestAgent',
        agent_type='research',
        description='A second test agent for collaboration',
        system_prompt='You are a research agent.',
        is_active=True
    )


@pytest.fixture
def agent_conversation(agent, second_agent, db):
    """Create a test agent conversation."""
    from core.models_unified_system import AgentConversation
    conv = AgentConversation.objects.create(
        initiator=agent,
        topic='Test Discussion Topic',
        status='completed',
        conclusion='The agents reached a test conclusion.',
        total_messages=5
    )
    conv.participants.add(agent, second_agent)
    return conv


@pytest.fixture
def extracted_artifact(agent_conversation, agent, db):
    """Create a test extracted artifact for ReviewDocument tests."""
    from core.models_conversation_artifacts import ExtractedArtifact
    return ExtractedArtifact.objects.create(
        conversation=agent_conversation,
        artifact_type='proposal',
        title='Test Proposal: New Feature Implementation',
        description='This proposal suggests implementing a new feature for the platform.',
        source_agent=agent,
        importance_score=0.75,
        urgency_score=0.5,
        confidence_score=0.85
    )


@pytest.fixture
def review_document(extracted_artifact, db):
    """Create a test ReviewDocument."""
    from core.models_conversation_artifacts import ReviewDocument
    return ReviewDocument.objects.create(
        artifact=extracted_artifact,
        status='awaiting_human',
        neutral_summary='This is a neutral summary of the proposal.',
        pro_case='- Pro point 1\n- Pro point 2',
        con_case='- Con point 1\n- Con point 2',
        open_questions=['Question 1?', 'Question 2?'],
        ai_recommendation='Consider implementing with modifications.',
        ai_lean='lean_approve',
        ai_confidence=0.75
    )


@pytest.fixture
def side_chat_pro(review_document, db):
    """Create a pro side chat."""
    from core.models_conversation_artifacts import SideChat
    return SideChat.objects.create(
        review_document=review_document,
        side='pro',
        messages=[
            {'role': 'system', 'content': 'You advocate for this proposal.'},
            {'role': 'user', 'content': 'Why should we approve this?'},
            {'role': 'assistant', 'content': 'Here are the benefits...'}
        ]
    )


@pytest.fixture
def side_chat_con(review_document, db):
    """Create a con side chat."""
    from core.models_conversation_artifacts import SideChat
    return SideChat.objects.create(
        review_document=review_document,
        side='con',
        messages=[
            {'role': 'system', 'content': 'You critique this proposal.'},
            {'role': 'user', 'content': 'What are the risks?'},
            {'role': 'assistant', 'content': 'Here are the concerns...'}
        ]
    )


@pytest.fixture
def shared_knowledge(agent, db):
    """Create test SharedKnowledge entries."""
    from core.models_unified_system import SharedKnowledge
    return SharedKnowledge.objects.create(
        source_agent=agent,
        knowledge_type='insight',
        title='Test Knowledge Item',
        content='This is a test knowledge item about the platform.',
        domain='technology',
        confidence_score=0.85,
        relevance_tags=['test', 'technology', 'platform']
    )


@pytest.fixture
def collaboration_session(agent, second_agent, db):
    """Create a test CollaborationSession."""
    from core.models_unified_system import CollaborationSession
    session = CollaborationSession.objects.create(
        topic='Test Collaboration',
        status='completed',
        session_type='brainstorm',
        result_summary='The collaboration was successful.',
        quality_score=0.85
    )
    session.participants.add(agent, second_agent)
    return session


@pytest.fixture
def agent_performance_metric(agent, db):
    """Create a test AgentPerformanceMetric."""
    from core.models_unified_system import AgentPerformanceMetric
    return AgentPerformanceMetric.objects.create(
        agent=agent,
        metric_type='quality',
        metric_name='output_quality',
        value=0.85,
        period='daily'
    )


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def freeze_time():
    """Fixture to freeze time for consistent timestamp testing."""
    from unittest.mock import patch
    from datetime import datetime

    frozen_time = datetime(2025, 1, 5, 12, 0, 0)

    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = frozen_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield frozen_time
