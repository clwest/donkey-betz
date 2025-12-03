# tests/factories.py
"""
Model factories for testing the Unified Donkey Betz Platform.

Uses factory_boy to create model instances for testing. These factories
provide a clean way to create test data with sensible defaults while
allowing customization for specific test cases.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# =============================================================================
# User Factories
# =============================================================================

class UserFactory(DjangoModelFactory):
    """Factory for creating UnifiedUser instances."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    platform_role = 'unified_user'
    subscription_tier = 'free'
    is_active = True


class AdminUserFactory(UserFactory):
    """Factory for creating admin users."""

    platform_role = 'admin'
    is_staff = True
    is_superuser = True


class ProUserFactory(UserFactory):
    """Factory for creating professional tier users."""

    subscription_tier = 'pro'


# =============================================================================
# Project Factories
# =============================================================================

class CreativeProjectFactory(DjangoModelFactory):
    """Factory for creating CreativeProject instances."""

    class Meta:
        model = 'core.PartnershipProject'  # Session 324: Unified from CreativeProject

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'Test Project {n}')
    description = 'Test project description'
    project_type = 'logo'


# =============================================================================
# Content Factories
# =============================================================================

class ImageHistoryFactory(DjangoModelFactory):
    """Factory for creating ImageHistory instances."""

    class Meta:
        model = 'content.ImageHistory'

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(CreativeProjectFactory, user=factory.SelfAttribute('..user'))
    filename = factory.Sequence(lambda n: f'image_{n}.png')
    file_path = factory.LazyAttribute(lambda o: f'generated_images/test/{o.filename}')
    image_type = 'generated'
    prompt = factory.Sequence(lambda n: f'Test prompt {n}')
    parameters = {'width': 1024, 'height': 1024}
    model_used = 'ultra'
    style = 'photographic'
    image_width = 1024
    image_height = 1024


class VideoHistoryFactory(DjangoModelFactory):
    """Factory for creating VideoHistory instances."""

    class Meta:
        model = 'content.VideoHistory'

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(CreativeProjectFactory, user=factory.SelfAttribute('..user'))
    video_id = factory.Sequence(lambda n: f'video-{n}')
    video_url = factory.LazyAttribute(lambda o: f'https://example.com/{o.video_id}.mp4')
    video_type = 'text_to_video'
    prompt = factory.Sequence(lambda n: f'Test video prompt {n}')
    parameters = {'duration': 10, 'ratio': '16:9'}
    model_used = 'gen4_turbo'
    status = 'completed'
    duration = 10


class MiniFigAssetFactory(DjangoModelFactory):
    """Factory for creating MiniFigAsset instances."""

    class Meta:
        model = 'content.MiniFigAsset'

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(CreativeProjectFactory, user=factory.SelfAttribute('..user'))
    source_image = factory.SubFactory(ImageHistoryFactory, user=factory.SelfAttribute('..user'))
    name = factory.Sequence(lambda n: f'MiniFig {n}')
    status = 'completed'
    glb_file_path = factory.Sequence(lambda n: f'minifigs/test/minifig_{n}.glb')
    stl_file_path = factory.Sequence(lambda n: f'minifigs/test/minifig_{n}.stl')


# =============================================================================
# Session Factories
# =============================================================================

class AISessionFactory(DjangoModelFactory):
    """Factory for creating AISession instances."""

    class Meta:
        model = 'content.AISession'

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(CreativeProjectFactory, user=factory.SelfAttribute('..user'))
    title = factory.Sequence(lambda n: f'Test Session {n}')
    transcript = [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi there!'}
    ]


# =============================================================================
# Template and Workflow Factories
# =============================================================================

class ContentTemplateFactory(DjangoModelFactory):
    """Factory for creating ContentTemplate instances."""

    class Meta:
        model = 'content.ContentTemplate'

    name = factory.Sequence(lambda n: f'template_{n}')
    display_name = factory.Sequence(lambda n: f'Test Template {n}')
    description = 'A test content template'
    template_type = 'article'
    system_prompt = 'You are a helpful assistant.'
    user_prompt_template = 'Write about {{ topic }}'
    variables = {'topic': {'type': 'string', 'required': True}}
    output_format = 'markdown'
    creator = factory.SubFactory(UserFactory)
    is_public = True


class WorkflowHistoryFactory(DjangoModelFactory):
    """Factory for creating WorkflowHistory instances."""

    class Meta:
        model = 'content.WorkflowHistory'

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(CreativeProjectFactory, user=factory.SelfAttribute('..user'))
    workflow_type = 'logo_package'
    status = 'completed'
    parameters = {'brand_name': 'TestBrand'}
    results = {'images': ['image1.png']}


class WorkflowFavoriteFactory(DjangoModelFactory):
    """Factory for creating WorkflowFavorite instances."""

    class Meta:
        model = 'content.WorkflowFavorite'

    user = factory.SubFactory(UserFactory)
    workflow_type = 'logo_package'


# =============================================================================
# Document and Embedding Factories
# =============================================================================

class DocumentFactory(DjangoModelFactory):
    """Factory for creating Document instances."""

    class Meta:
        model = 'content.Document'

    title = factory.Sequence(lambda n: f'Document {n}')
    content = 'This is test document content for embedding and retrieval testing.'
    document_type = 'text'
    source = 'upload'
    file_path = factory.Sequence(lambda n: f'documents/test/doc_{n}.txt')
    creator = factory.SubFactory(UserFactory)


# =============================================================================
# Knowledge Base Factories
# =============================================================================

class KnowledgeBaseFactory(DjangoModelFactory):
    """Factory for creating KnowledgeBase instances."""

    class Meta:
        model = 'content.KnowledgeBase'

    name = factory.Sequence(lambda n: f'Knowledge Base {n}')
    description = 'Test knowledge base for testing'
    category = 'general'
    creator = factory.SubFactory(UserFactory)


# =============================================================================
# Content Generation Factories
# =============================================================================

class ContentGenerationFactory(DjangoModelFactory):
    """Factory for creating ContentGeneration instances."""

    class Meta:
        model = 'content.ContentGeneration'

    template = factory.SubFactory(ContentTemplateFactory)
    creator = factory.SubFactory(UserFactory)
    input_variables = {'topic': 'AI Testing'}
    status = 'completed'
    output_content = 'This is generated test content about AI Testing.'


# =============================================================================
# User Profile Factories (from core app)
# =============================================================================

class UserProfileFactory(DjangoModelFactory):
    """Factory for creating UserProfile instances."""

    class Meta:
        model = 'core.UserProfile'

    user = factory.SubFactory(UserFactory)
    bio = 'Test user bio'
    location = 'Test City'
    website = 'https://example.com'


class ExtendedUserProfileFactory(DjangoModelFactory):
    """Factory for creating ExtendedUserProfile instances."""

    class Meta:
        model = 'core.ExtendedUserProfile'

    user = factory.SubFactory(UserFactory)
    skills = ['Python', 'Django', 'AI']
    experience_years = 5


# =============================================================================
# Agent Factories
# =============================================================================

class UnifiedAgentTemplateFactory(DjangoModelFactory):
    """Factory for creating UnifiedAgentTemplate instances."""

    class Meta:
        model = 'agents.UnifiedAgentTemplate'

    name = factory.Sequence(lambda n: f'Test Agent {n}')
    agent_type = 'content_generation'
    description = 'A test agent for unit testing'
    system_prompt = 'You are a test agent.'
    configuration = {'temperature': 0.7}
    creator = factory.SubFactory(UserFactory)
