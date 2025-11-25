# tests/conftest.py
"""
Shared pytest fixtures for the Unified Donkey Betz Platform.

This module provides fixtures that are shared across all test modules:
- Database fixtures for users, projects, images, videos
- API client fixtures for authenticated and unauthenticated requests
- Mock fixtures for external API providers
- Utility fixtures for file handling and cleanup
"""
import os
import sys
import pathlib
import tempfile
import shutil
from unittest.mock import MagicMock, patch

import pytest

# Setup Django before imports
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.django_test_settings")

import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


# =============================================================================
# Database Setup - Create pgvector extension
# =============================================================================

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Extend the default django_db_setup to ensure pgvector extension is created.
    This runs once per test session before any tests execute.
    """
    with django_db_blocker.unblock():
        from django.db import connection
        with connection.cursor() as cursor:
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            except Exception as e:
                # Extension might already exist or not be available
                print(f"Note: pgvector extension setup: {e}")


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def user(db):
    """Create a test user with default credentials."""
    # Use fields available on UnifiedUser model
    user_obj = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='test123'
    )
    # Set additional fields if they exist
    if hasattr(user_obj, 'platform_role'):
        user_obj.platform_role = 'unified_user'
        user_obj.save()
    return user_obj


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user_obj = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    if hasattr(user_obj, 'platform_role'):
        user_obj.platform_role = 'admin'
        user_obj.save()
    return user_obj


@pytest.fixture
def second_user(db):
    """Create a second test user for multi-user scenarios."""
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='test123'
    )


@pytest.fixture
def project(user, db):
    """Create a test creative project."""
    from content.models import CreativeProject
    return CreativeProject.objects.create(
        user=user,
        name='Test Project',
        description='Test project for testing',
        project_type='logo'
    )


@pytest.fixture
def second_project(user, db):
    """Create a second project for the same user."""
    from content.models import CreativeProject
    return CreativeProject.objects.create(
        user=user,
        name='Second Project',
        description='Another test project',
        project_type='character'
    )


@pytest.fixture
def image_history(user, project, db):
    """Create a test image history record."""
    from content.models import ImageHistory
    return ImageHistory.objects.create(
        user=user,
        project=project,
        filename='test_image.png',
        file_path='generated_images/test/test_image.png',
        image_type='generated',
        prompt='A beautiful sunset over the ocean',
        parameters={'width': 1024, 'height': 1024, 'style': 'photographic'},
        model_used='ultra',
        style='photographic',
        image_width=1024,
        image_height=1024,
        status='completed'
    )


@pytest.fixture
def video_history(user, project, db):
    """Create a test video history record."""
    from content.models import VideoHistory
    return VideoHistory.objects.create(
        user=user,
        project=project,
        video_id='test-video-123',
        video_url='https://example.com/test-video.mp4',
        video_type='text_to_video',
        prompt='A sunset animation',
        parameters={'duration': 10, 'ratio': '16:9'},
        model_used='gen4_turbo',
        status='completed',
        duration=10
    )


@pytest.fixture
def ai_session(user, project, db):
    """Create a test AI session."""
    from content.models import AISession
    return AISession.objects.create(
        user=user,
        project=project,
        title='Test Session',
        transcript=[
            {'role': 'user', 'content': 'Generate a test image'},
            {'role': 'assistant', 'content': 'I\'ll generate that for you.'}
        ]
    )


@pytest.fixture
def minifig_asset(user, project, image_history, db):
    """Create a test 3D minifig asset."""
    from content.models import MiniFigAsset
    return MiniFigAsset.objects.create(
        user=user,
        project=project,
        source_image=image_history,
        name='Test MiniFig',
        status='completed',
        glb_file_path='minifigs/test/test.glb',
        stl_file_path='minifigs/test/test.stl'
    )


# =============================================================================
# API Client Fixtures
# =============================================================================

@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(user):
    """Return an authenticated API client for the test user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    """Return an authenticated API client for an admin user."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


# =============================================================================
# Mock Fixtures for External Services
# =============================================================================

@pytest.fixture
def mock_stability_api():
    """Mock Stability AI API responses."""
    with patch('content.image_generation.requests') as mock_requests:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'artifacts': [{'base64': 'dGVzdGltYWdlZGF0YQ==', 'seed': 12345}]
        }
        mock_response.content = b'test image data'
        mock_requests.post.return_value = mock_response
        yield mock_requests


@pytest.fixture
def mock_runway_api():
    """Mock Runway ML API responses."""
    with patch('content.video_provider.requests') as mock_requests:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'test-task-id-123',
            'status': 'SUCCEEDED',
            'output': ['https://example.com/video.mp4']
        }
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response
        yield mock_requests


@pytest.fixture
def mock_elevenlabs_api():
    """Mock ElevenLabs API responses."""
    with patch('content.elevenlabs_provider.requests') as mock_requests:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'audio data'
        mock_requests.post.return_value = mock_response
        yield mock_requests


@pytest.fixture
def mock_replicate_api():
    """Mock Replicate API responses."""
    with patch('content.replicate_provider.replicate') as mock_replicate:
        mock_replicate.run.return_value = {
            'status': 'succeeded',
            'output': {'glb': 'https://example.com/model.glb'}
        }
        yield mock_replicate


@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API responses."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output = [
            MagicMock(
                type='message',
                content=[MagicMock(type='text', text='Test response')]
            )
        ]
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client
        yield mock_openai


# =============================================================================
# File System Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory that's cleaned up after the test."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_image_file(temp_dir):
    """Create a temporary image file."""
    import base64

    # 1x1 PNG pixel
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    )

    file_path = os.path.join(temp_dir, 'test_image.png')
    with open(file_path, 'wb') as f:
        f.write(png_data)

    return file_path


@pytest.fixture
def temp_video_file(temp_dir):
    """Create a temporary video file (empty file for testing)."""
    file_path = os.path.join(temp_dir, 'test_video.mp4')
    with open(file_path, 'wb') as f:
        f.write(b'fake video data')
    return file_path


# =============================================================================
# Django Request Factory Fixtures
# =============================================================================

@pytest.fixture
def rf():
    """Return Django's RequestFactory."""
    from django.test import RequestFactory
    return RequestFactory()


@pytest.fixture
def authenticated_request(rf, user):
    """Create an authenticated request object."""
    request = rf.get('/')
    request.user = user
    return request


# =============================================================================
# Content Model Fixtures for Complex Scenarios
# =============================================================================

@pytest.fixture
def multiple_images(user, project, db):
    """Create multiple images for batch operation testing."""
    from content.models import ImageHistory

    images = []
    for i in range(5):
        img = ImageHistory.objects.create(
            user=user,
            project=project,
            filename=f'test_image_{i}.png',
            file_path=f'generated_images/test/test_image_{i}.png',
            image_type='generated',
            prompt=f'Test image {i}',
            parameters={'width': 1024, 'height': 1024},
            model_used='ultra',
            status='completed'
        )
        images.append(img)

    return images


@pytest.fixture
def multiple_videos(user, project, db):
    """Create multiple videos for batch operation testing."""
    from content.models import VideoHistory

    videos = []
    for i in range(3):
        vid = VideoHistory.objects.create(
            user=user,
            project=project,
            video_id=f'test-video-{i}',
            video_url=f'https://example.com/test-video-{i}.mp4',
            video_type='text_to_video',
            prompt=f'Test video {i}',
            parameters={'duration': 10},
            model_used='gen4_turbo',
            status='completed'
        )
        videos.append(vid)

    return videos


# =============================================================================
# Workflow and Template Fixtures
# =============================================================================

@pytest.fixture
def content_template(user, db):
    """Create a content generation template."""
    from content.models import ContentTemplate
    return ContentTemplate.objects.create(
        name='test_template',
        display_name='Test Template',
        description='A test template for unit testing',
        template_type='article',
        system_prompt='You are a helpful assistant.',
        user_prompt_template='Write about {{ topic }}',
        variables={'topic': {'type': 'string', 'required': True}},
        output_format='markdown',
        creator=user
    )


@pytest.fixture
def workflow_history(user, project, db):
    """Create a workflow history record."""
    from content.models import WorkflowHistory
    return WorkflowHistory.objects.create(
        user=user,
        project=project,
        workflow_type='logo_package',
        status='completed',
        parameters={'brand_name': 'TestBrand'},
        results={'images': ['image1.png']}
    )


# =============================================================================
# Settings Override Fixtures
# =============================================================================

@pytest.fixture
def override_rate_limits():
    """Temporarily disable rate limiting for tests."""
    with patch('core.decorators.RATE_LIMITS', {
        'default': {'requests': 10000, 'period': 60},
        'ai_generation': {'requests': 10000, 'period': 60},
        'video_generation': {'requests': 10000, 'period': 60},
    }):
        yield


# =============================================================================
# Marker Definitions
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external_api: mark test as requiring external API access"
    )
