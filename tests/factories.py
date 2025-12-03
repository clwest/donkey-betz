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


# =============================================================================
# Business Research Factories (Session 334)
# =============================================================================

class PartnershipProjectFactory(DjangoModelFactory):
    """Factory for creating PartnershipProject instances."""

    class Meta:
        model = 'core.PartnershipProject'

    user = factory.SubFactory(UserFactory)
    project_name = factory.Sequence(lambda n: f'Test Project {n}')
    project_type = 'research'
    description = factory.Faker('paragraph')
    goal = factory.Faker('sentence')
    status = 'planning'
    category = 'ai_tech'
    tags = ['test', 'automated']
    metadata = factory.LazyFunction(lambda: {
        'test_scenario_id': None,
        'company_info': {
            'name': 'Test Company',
            'location': 'Test City, USA',
            'founded': 2023,
        }
    })


class BusinessResearchResultFactory(DjangoModelFactory):
    """Factory for creating BusinessResearchResult instances."""

    class Meta:
        model = 'core.BusinessResearchResult'

    project = factory.SubFactory(PartnershipProjectFactory)
    research_type = 'competitor'
    query = factory.Faker('sentence')
    agent_name = 'CompetitorAnalysisAgent'
    market_topic = factory.Faker('catch_phrase')

    # Analysis content
    analysis = factory.LazyAttribute(
        lambda o: f"""## Market Overview
This is a test analysis for {o.query}.

## Key Competitors
- Competitor A
- Competitor B
- Competitor C

## SWOT Analysis
**Strengths:** Test strengths
**Weaknesses:** Test weaknesses
**Opportunities:** Test opportunities
**Threats:** Test threats

## Recommendations
1. Recommendation one
2. Recommendation two
"""
    )

    # Metrics
    data_points_analyzed = factory.Faker('random_int', min=5, max=50)
    sources_used = factory.LazyFunction(lambda: ['reddit', 'hackernews', 'techcrunch'])

    # Structured data
    raw_data = factory.LazyFunction(lambda: [
        {'title': 'Test Article 1', 'source': 'reddit', 'url': 'https://reddit.com/1'},
        {'title': 'Test Article 2', 'source': 'hackernews', 'url': 'https://news.ycombinator.com/1'},
    ])
    pain_points = factory.LazyFunction(lambda: [
        'Pain point 1: Users struggle with X',
        'Pain point 2: Customers want Y',
    ])
    personas = factory.LazyFunction(lambda: [
        {'name': 'Test Persona', 'description': 'A test customer persona'},
    ])
    quotes = factory.LazyFunction(lambda: [
        {'text': 'I wish there was a better way to do X', 'source': 'reddit'},
    ])
    recommendations = factory.LazyFunction(lambda: [
        'Focus on mobile experience',
        'Add AI-powered features',
    ])


class CompetitorAnalysisResultFactory(BusinessResearchResultFactory):
    """Factory specifically for competitor analysis results."""

    research_type = 'competitor'
    agent_name = 'CompetitorAnalysisAgent'
    analysis = factory.LazyAttribute(
        lambda o: f"""## Competitive Analysis: {o.market_topic}

### Market Overview
The market for {o.market_topic} is growing rapidly...

### Key Competitors Identified

1. **Competitor A** - Market leader with 40% share
   - Strengths: Strong brand, extensive features
   - Weaknesses: High pricing, slow innovation

2. **Competitor B** - Rising challenger
   - Strengths: Modern UX, competitive pricing
   - Weaknesses: Limited features

3. **Competitor C** - Niche player
   - Strengths: Specialized focus
   - Weaknesses: Small market share

### Market Gaps & Opportunities
- Gap 1: No solution addresses X
- Gap 2: Underserved segment Y

### Strategic Recommendations
1. Differentiate on speed and simplicity
2. Target underserved mid-market segment
3. Build integrations with popular tools
"""
    )


class CustomerResearchResultFactory(BusinessResearchResultFactory):
    """Factory specifically for customer research results."""

    research_type = 'customer'
    agent_name = 'CustomerResearchAgent'
    analysis = factory.LazyAttribute(
        lambda o: f"""## Customer Research: {o.market_topic}

### Target Market Overview
Our research analyzed discussions from Reddit, HackerNews, and industry forums...

### Top Pain Points

1. **Pain Point 1** (mentioned 45 times)
   - Users frustrated with complex onboarding
   - Quote: "I spent 3 hours just trying to set this up"

2. **Pain Point 2** (mentioned 32 times)
   - Pricing too high for small teams
   - Quote: "Love the product but can't justify the cost"

3. **Pain Point 3** (mentioned 28 times)
   - Missing key integrations
   - Quote: "Why doesn't this work with Slack?"

### Customer Personas

**Persona 1: Sarah the Startup Founder**
- Age: 28-35
- Goals: Move fast, minimize overhead
- Pain points: Too many tools, high costs
- Motivation: Simplicity and speed

**Persona 2: Mike the Marketing Manager**
- Age: 32-45
- Goals: Prove ROI, streamline workflow
- Pain points: Fragmented data, manual reporting
- Motivation: Look good to leadership

### Actionable Quotes
- "I would pay double for something that just works"
- "The learning curve is killing our productivity"
- "If it integrated with X, I'd switch immediately"

### Recommendations
1. Simplify onboarding to under 5 minutes
2. Add Slack/Teams integration as priority
3. Create mid-tier pricing for small teams
"""
    )
    personas = factory.LazyFunction(lambda: [
        {
            'name': 'Sarah the Startup Founder',
            'demographics': '28-35, Tech industry',
            'goals': ['Move fast', 'Minimize overhead'],
            'pain_points': ['Too many tools', 'High costs'],
        },
        {
            'name': 'Mike the Marketing Manager',
            'demographics': '32-45, B2B companies',
            'goals': ['Prove ROI', 'Streamline workflow'],
            'pain_points': ['Fragmented data', 'Manual reporting'],
        },
    ])
