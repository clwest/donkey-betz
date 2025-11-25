# Phase 4: Testing & Polish (P3 + Test Infrastructure)

**Execution Mode:** PARALLEL (test files are independent)
**Duration:** 2-4 weeks
**Total Tasks:** 8 major testing tasks + polish

---

## Parallel Execution Guide

Test creation can run in **multiple Claude Code instances simultaneously** since each test file is independent.

### Recommended Parallel Groups

```
Claude Code 1: Tasks 4.1, 4.2 (Model & View tests)
Claude Code 2: Tasks 4.3, 4.4 (Agent & Provider tests)
Claude Code 3: Tasks 4.5, 4.6 (Integration & Frontend tests)
Claude Code 4: Tasks 4.7, 4.8 (E2E tests & Polish)
```

---

## Task Overview

| Task | Focus | Target Coverage | Effort | Parallelizable |
|------|-------|-----------------|--------|----------------|
| 4.1 | Model Unit Tests | 70% models | 16h | Yes |
| 4.2 | View Unit Tests | 60% views | 16h | Yes |
| 4.3 | Agent Tests | 70% agents | 8h | Yes |
| 4.4 | Provider Tests | 70% providers | 8h | Yes |
| 4.5 | Integration Tests | Key workflows | 12h | Yes |
| 4.6 | Frontend Tests | JS functions | 12h | Yes |
| 4.7 | E2E Tests | Critical paths | 16h | Yes |
| 4.8 | Code Polish | P3 issues | 8h | Yes |

---

## Testing Infrastructure Setup

Before starting individual test tasks, set up the testing infrastructure.

### Claude Code Prompt - Test Setup
```
# REMEDIATION TASK 4.0: Testing Infrastructure Setup

## Context
The project needs proper testing infrastructure before writing tests.

## Your Task
1. Review existing test configuration
2. Set up pytest with Django integration
3. Create test fixtures and factories
4. Configure test coverage reporting

## Files to Create/Modify
- `pytest.ini` or `pyproject.toml` (pytest config)
- `conftest.py` (shared fixtures)
- `tests/factories.py` (model factories)
- `tests/__init__.py`

## Setup Configuration

### pyproject.toml (if not exists, add section):
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "core.settings"
python_files = ["test_*.py", "*_test.py"]
addopts = "-v --tb=short --cov=core --cov=content --cov=agents --cov-report=html"
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["core", "content", "agents", "intelligence"]
omit = ["*/migrations/*", "*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

### conftest.py:
```python
"""Shared pytest fixtures."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='test123'
    )

@pytest.fixture
def authenticated_client(user):
    """Return an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()

@pytest.fixture
def project(user, db):
    """Create a test project."""
    from content.models import Project
    return Project.objects.create(
        user=user,
        name='Test Project',
        description='Test project for testing'
    )
```

### tests/factories.py:
```python
"""Model factories for testing."""
import factory
from django.contrib.auth import get_user_model
from content.models import Project, ImageHistory, VideoHistory

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass')

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'Project {n}')
    description = 'Test project'

class ImageHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageHistory

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    prompt = 'Test prompt'
    status = 'completed'
```

## Verification
```bash
pip install pytest pytest-django pytest-cov factory-boy
pytest --collect-only  # Should find test collection
pytest -v  # Run tests
```

Begin by reviewing existing test setup.
```

---

## Task 4.1: Model Unit Tests

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.1: Model Unit Tests

## Context
Create comprehensive unit tests for all database models.

## Your Task
1. Create tests for content/models.py
2. Create tests for core/models.py
3. Test model methods, validations, and relationships
4. Achieve 70% coverage on models

## Test File Structure
```
tests/
├── models/
│   ├── __init__.py
│   ├── test_image_history.py
│   ├── test_video_history.py
│   ├── test_project.py
│   ├── test_minifig_asset.py
│   └── test_unified_base.py
```

## Test Examples

### test_image_history.py:
```python
"""Tests for ImageHistory model."""
import pytest
from django.core.exceptions import ValidationError
from content.models import ImageHistory
from tests.factories import UserFactory, ProjectFactory, ImageHistoryFactory

pytestmark = pytest.mark.django_db

class TestImageHistoryModel:
    """Tests for ImageHistory model."""

    def test_create_image_history(self, user, project):
        """Test creating a basic image history record."""
        image = ImageHistory.objects.create(
            user=user,
            project=project,
            prompt='A beautiful sunset',
            status='completed'
        )
        assert image.id is not None
        assert image.prompt == 'A beautiful sunset'
        assert image.sequential_number > 0

    def test_sequential_number_auto_increment(self, user, project):
        """Test sequential numbers auto-increment per user."""
        img1 = ImageHistoryFactory(user=user, project=project)
        img2 = ImageHistoryFactory(user=user, project=project)
        assert img2.sequential_number == img1.sequential_number + 1

    def test_soft_delete(self, user, project):
        """Test soft delete functionality."""
        image = ImageHistoryFactory(user=user, project=project)
        image_id = image.id
        image.delete()

        # Should not be in default queryset
        assert not ImageHistory.objects.filter(id=image_id).exists()

        # Should be in all_objects queryset
        assert ImageHistory.all_objects.filter(id=image_id).exists()

    def test_get_sequential_number_method(self, user, project):
        """Test get_sequential_number returns correct value."""
        image = ImageHistoryFactory(user=user, project=project)
        assert image.get_sequential_number() == image.sequential_number

    def test_parameters_json_field(self, user, project):
        """Test parameters JSONField stores and retrieves correctly."""
        params = {'width': 1024, 'height': 768, 'style': 'cinematic'}
        image = ImageHistory.objects.create(
            user=user,
            project=project,
            prompt='Test',
            parameters=params
        )
        image.refresh_from_db()
        assert image.parameters == params

    def test_string_representation(self, user, project):
        """Test __str__ method."""
        image = ImageHistoryFactory(user=user, project=project, prompt='Test prompt')
        assert 'Test prompt' in str(image)
```

## Models to Test
- [ ] ImageHistory
- [ ] VideoHistory
- [ ] Project
- [ ] AISession
- [ ] MiniFigAsset
- [ ] CharacterModel
- [ ] UserProfile
- [ ] UnifiedBaseModel (abstract)

Begin by reading content/models.py and creating tests.
```

### Verification
```bash
pytest tests/models/ -v --cov=content.models
# Target: 70% coverage
```

### Completion Sign-off
- [ ] All model tests created
- [ ] Soft delete tested
- [ ] Relationships tested
- [ ] Validations tested
- [ ] 70%+ coverage achieved

---

## Task 4.2: View Unit Tests

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.2: View Unit Tests

## Context
Create unit tests for view functions and API endpoints.

## Your Task
1. Create tests for core/views_image.py endpoints
2. Create tests for core/views_video.py endpoints
3. Create tests for core/views_assistant_bypass.py
4. Test authentication, validation, and error handling

## Test File Structure
```
tests/
├── views/
│   ├── __init__.py
│   ├── test_image_views.py
│   ├── test_video_views.py
│   ├── test_assistant_views.py
│   └── test_gallery_views.py
```

## Test Examples

### test_image_views.py:
```python
"""Tests for image views."""
import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch, MagicMock
from tests.factories import UserFactory, ProjectFactory, ImageHistoryFactory

pytestmark = pytest.mark.django_db

class TestImageGenerationView:
    """Tests for image generation endpoint."""

    def test_unauthenticated_request_rejected(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.post('/api/images/generate/', {
            'prompt': 'test'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_prompt_validation(self, authenticated_client):
        """Test validation error for missing prompt."""
        response = authenticated_client.post('/api/images/generate/', {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'prompt' in response.json().get('error', '').lower()

    @patch('content.image_generation.StabilityAIProvider')
    def test_successful_generation(self, mock_provider, authenticated_client, project):
        """Test successful image generation."""
        mock_provider.return_value.generate.return_value = {
            'success': True,
            'image_url': 'http://example.com/image.png'
        }

        response = authenticated_client.post('/api/images/generate/', {
            'prompt': 'A beautiful landscape',
            'project_id': str(project.id)
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['success'] is True

    def test_rate_limiting(self, authenticated_client):
        """Test rate limiting kicks in after threshold."""
        # Make requests until rate limited
        for i in range(15):
            response = authenticated_client.post('/api/images/generate/', {
                'prompt': f'test {i}'
            })
            if response.status_code == 429:
                break

        # Should eventually get rate limited
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestImageUpscaleView:
    """Tests for image upscale endpoint."""

    def test_invalid_image_id(self, authenticated_client):
        """Test error for invalid image ID."""
        response = authenticated_client.post('/api/images/upscale/', {
            'image_id': 'invalid-uuid'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_image_not_found(self, authenticated_client):
        """Test error for non-existent image."""
        import uuid
        response = authenticated_client.post('/api/images/upscale/', {
            'image_id': str(uuid.uuid4())
        })
        assert response.status_code == status.HTTP_404_NOT_FOUND
```

## Views to Test
- [ ] Image generation
- [ ] Image upscale
- [ ] Background removal
- [ ] Video generation
- [ ] Video operations
- [ ] Assistant chat
- [ ] Gallery listing
- [ ] Project CRUD

Begin by reading the view files and creating tests.
```

### Verification
```bash
pytest tests/views/ -v --cov=core.views
# Target: 60% coverage
```

### Completion Sign-off
- [ ] All key views tested
- [ ] Authentication tested
- [ ] Validation tested
- [ ] Error handling tested
- [ ] 60%+ coverage achieved

---

## Task 4.3: Agent Tests

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.3: Agent Tests

## Context
Create tests for the agent system.

## Your Task
1. Create tests for agents/video_agent.py
2. Create tests for agents/audio_agent.py
3. Create tests for intelligence/agent_orchestrator.py
4. Test agent communication and execution

## Test File Structure
```
tests/
├── agents/
│   ├── __init__.py
│   ├── test_video_agent.py
│   ├── test_audio_agent.py
│   ├── test_orchestrator.py
│   └── test_agent_communication.py
```

## Test Examples

### test_video_agent.py:
```python
"""Tests for VideoAgent."""
import pytest
from unittest.mock import patch, MagicMock
from agents.video_agent import VideoAgent

pytestmark = pytest.mark.django_db

class TestVideoAgent:
    """Tests for VideoAgent class."""

    @pytest.fixture
    def agent(self):
        return VideoAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.agent_id is not None
        assert 'video' in agent.capabilities

    def test_can_handle_video_task(self, agent):
        """Test agent correctly identifies video tasks."""
        task = {'type': 'video_generation', 'prompt': 'test'}
        assert agent.can_handle(task) is True

    def test_cannot_handle_image_task(self, agent):
        """Test agent rejects non-video tasks."""
        task = {'type': 'image_generation', 'prompt': 'test'}
        assert agent.can_handle(task) is False

    @patch('content.video_provider.RunwayMLProvider')
    def test_execute_video_generation(self, mock_provider, agent):
        """Test video generation execution."""
        mock_provider.return_value.generate.return_value = {
            'success': True,
            'task_id': 'test-task-id'
        }

        result = agent.execute({
            'type': 'video_generation',
            'prompt': 'A dog running',
            'image_url': 'http://example.com/image.png'
        })

        assert result['success'] is True

    def test_execute_with_invalid_task(self, agent):
        """Test execution fails gracefully with invalid task."""
        result = agent.execute({'type': 'unknown'})
        assert result['success'] is False
        assert 'error' in result
```

Begin by reading the agent files and creating tests.
```

### Verification
```bash
pytest tests/agents/ -v --cov=agents
# Target: 70% coverage
```

### Completion Sign-off
- [ ] Video agent tested
- [ ] Audio agent tested
- [ ] Orchestrator tested
- [ ] Communication tested
- [ ] 70%+ coverage achieved

---

## Task 4.4: Provider Tests

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.4: Provider Tests

## Context
Create tests for API provider classes.

## Your Task
1. Create tests for content/image_generation.py
2. Create tests for content/video_provider.py
3. Create tests for content/elevenlabs_provider.py
4. Mock external API calls

## Test File Structure
```
tests/
├── providers/
│   ├── __init__.py
│   ├── test_stability_provider.py
│   ├── test_runway_provider.py
│   ├── test_elevenlabs_provider.py
│   └── test_replicate_provider.py
```

## Test Examples

### test_stability_provider.py:
```python
"""Tests for Stability AI provider."""
import pytest
from unittest.mock import patch, MagicMock
import responses
from content.image_generation import StabilityAIProvider

class TestStabilityAIProvider:
    """Tests for StabilityAIProvider."""

    @pytest.fixture
    def provider(self):
        with patch.dict('os.environ', {'STABILITY_API_KEY': 'test-key'}):
            return StabilityAIProvider()

    def test_provider_initialization(self, provider):
        """Test provider initializes with API key."""
        assert provider.api_key == 'test-key'

    @responses.activate
    def test_generate_image_success(self, provider):
        """Test successful image generation."""
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl/text-to-image',
            json={'artifacts': [{'base64': 'dGVzdA=='}]},
            status=200
        )

        result = provider.generate('A sunset', width=1024, height=1024)

        assert result['success'] is True
        assert 'image_data' in result

    @responses.activate
    def test_generate_image_api_error(self, provider):
        """Test handling of API errors."""
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl/text-to-image',
            json={'error': 'Invalid request'},
            status=400
        )

        result = provider.generate('Test', width=1024, height=1024)

        assert result['success'] is False
        assert 'error' in result

    def test_missing_api_key(self):
        """Test error when API key is missing."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                StabilityAIProvider()
```

Begin by reading the provider files and creating tests.
```

### Verification
```bash
pytest tests/providers/ -v --cov=content
# Target: 70% coverage
```

### Completion Sign-off
- [ ] Stability provider tested
- [ ] Runway provider tested
- [ ] ElevenLabs provider tested
- [ ] Replicate provider tested
- [ ] 70%+ coverage achieved

---

## Task 4.5: Integration Tests

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.5: Integration Tests

## Context
Create integration tests for key workflows.

## Your Task
1. Test complete image generation workflow
2. Test complete video generation workflow
3. Test AI assistant workflow
4. Test project management workflow

## Test File Structure
```
tests/
├── integration/
│   ├── __init__.py
│   ├── test_image_workflow.py
│   ├── test_video_workflow.py
│   ├── test_assistant_workflow.py
│   └── test_project_workflow.py
```

## Test Examples

### test_image_workflow.py:
```python
"""Integration tests for image generation workflow."""
import pytest
from django.test import override_settings
from unittest.mock import patch
from tests.factories import UserFactory, ProjectFactory

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

class TestImageGenerationWorkflow:
    """Integration tests for complete image generation workflow."""

    @patch('content.image_generation.StabilityAIProvider')
    def test_complete_image_generation_flow(
        self, mock_provider, authenticated_client, user, project
    ):
        """Test complete flow: generate → view → upscale."""
        # Mock provider
        mock_provider.return_value.generate.return_value = {
            'success': True,
            'image_data': 'base64data',
            'image_url': '/media/test.png'
        }

        # Step 1: Generate image
        response = authenticated_client.post('/api/images/generate/', {
            'prompt': 'A beautiful sunset',
            'project_id': str(project.id)
        })
        assert response.status_code == 200
        image_id = response.json()['data']['id']

        # Step 2: View image details
        response = authenticated_client.get(f'/api/images/{image_id}/')
        assert response.status_code == 200
        assert response.json()['prompt'] == 'A beautiful sunset'

        # Step 3: Upscale image
        mock_provider.return_value.upscale.return_value = {
            'success': True,
            'image_url': '/media/upscaled.png'
        }
        response = authenticated_client.post('/api/images/upscale/', {
            'image_id': image_id
        })
        assert response.status_code == 200

    def test_batch_operation_workflow(self, authenticated_client, user, project):
        """Test batch operations on multiple images."""
        # Create multiple images
        # Test batch upscale
        # Verify all processed
        pass
```

Begin by identifying key workflows and creating tests.
```

### Verification
```bash
pytest tests/integration/ -v -m integration
```

### Completion Sign-off
- [ ] Image workflow tested
- [ ] Video workflow tested
- [ ] Assistant workflow tested
- [ ] Project workflow tested

---

## Task 4.6: Frontend Tests

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.6: Frontend Tests

## Context
Add JavaScript tests for frontend functionality.

## Your Task
1. Set up Jest for JavaScript testing
2. Create tests for core JS functions
3. Test API communication layer
4. Test UI utility functions

## Test File Structure
```
core/static/js/
├── __tests__/
│   ├── api.test.js
│   ├── utils.test.js
│   ├── validation.test.js
│   └── formatting.test.js
├── jest.config.js
└── package.json
```

## Setup

### package.json:
```json
{
  "name": "ai-studio-frontend",
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "jest-environment-jsdom": "^29.0.0"
  }
}
```

### jest.config.js:
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>'],
  testMatch: ['**/__tests__/**/*.test.js'],
  collectCoverageFrom: ['ai_studio/**/*.js', '!**/__tests__/**'],
};
```

## Test Examples

### utils.test.js:
```javascript
const { escapeHtml, formatFileSize, truncateText } = require('../utils/helpers');

describe('escapeHtml', () => {
  test('escapes HTML special characters', () => {
    expect(escapeHtml('<script>')).toBe('&lt;script&gt;');
    expect(escapeHtml('a & b')).toBe('a &amp; b');
    expect(escapeHtml('"quoted"')).toBe('&quot;quoted&quot;');
  });

  test('handles empty string', () => {
    expect(escapeHtml('')).toBe('');
  });

  test('handles null/undefined', () => {
    expect(escapeHtml(null)).toBe('');
    expect(escapeHtml(undefined)).toBe('');
  });
});

describe('formatFileSize', () => {
  test('formats bytes correctly', () => {
    expect(formatFileSize(500)).toBe('500 B');
    expect(formatFileSize(1024)).toBe('1.0 KB');
    expect(formatFileSize(1048576)).toBe('1.0 MB');
    expect(formatFileSize(1073741824)).toBe('1.0 GB');
  });
});

describe('truncateText', () => {
  test('truncates long text', () => {
    const text = 'This is a very long text that should be truncated';
    expect(truncateText(text, 20)).toBe('This is a very lo...');
  });

  test('does not truncate short text', () => {
    expect(truncateText('Short', 20)).toBe('Short');
  });
});
```

Begin by setting up Jest and creating tests.
```

### Verification
```bash
cd core/static/js
npm install
npm test
```

### Completion Sign-off
- [ ] Jest configured
- [ ] Utility tests created
- [ ] API tests created
- [ ] Validation tests created

---

## Task 4.7: E2E Tests

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.7: End-to-End Tests

## Context
Create E2E tests for critical user journeys.

## Your Task
1. Set up Playwright or Cypress for E2E testing
2. Test critical user journeys
3. Test error scenarios
4. Create smoke test suite

## Test File Structure
```
tests/e2e/
├── playwright.config.ts
├── fixtures/
│   └── auth.ts
├── pages/
│   ├── ai-studio.page.ts
│   └── login.page.ts
└── specs/
    ├── smoke.spec.ts
    ├── image-generation.spec.ts
    └── project-management.spec.ts
```

## Setup (Playwright)

### playwright.config.ts:
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './specs',
  use: {
    baseURL: 'http://localhost:8000',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
```

## Test Examples

### smoke.spec.ts:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/AI Studio/);
  });

  test('login page accessible', async ({ page }) => {
    await page.goto('/login/');
    await expect(page.locator('form')).toBeVisible();
  });

  test('AI Studio requires auth', async ({ page }) => {
    await page.goto('/ai-studio/');
    // Should redirect to login
    await expect(page).toHaveURL(/login/);
  });
});
```

### image-generation.spec.ts:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Image Generation', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login/');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass');
    await page.click('button[type="submit"]');
  });

  test('can generate an image', async ({ page }) => {
    await page.goto('/ai-studio/');

    // Enter prompt
    await page.fill('#chat-input', 'Generate a sunset image');
    await page.click('#send-button');

    // Wait for generation
    await expect(page.locator('.image-card')).toBeVisible({ timeout: 60000 });
  });
});
```

Begin by setting up Playwright and creating tests.
```

### Verification
```bash
npx playwright install
npx playwright test
```

### Completion Sign-off
- [ ] E2E framework set up
- [ ] Smoke tests created
- [ ] Critical paths tested
- [ ] Tests pass in CI

---

## Task 4.8: Code Polish (P3 Issues)

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 4.8: Code Polish

## Context
Address remaining P3 (low priority) issues for code polish.

## Your Task
1. Add missing type hints
2. Remove TODO comments or convert to issues
3. Add docstrings to functions
4. Clean up unused imports
5. Standardize logging levels

## Files to Review
- All Python files for type hints
- All files for TODO comments
- Core modules for docstrings

## Polish Examples

### Type Hints:
```python
# Before
def process_image(image_id, options):
    pass

# After
from typing import Dict, Any, Optional
from uuid import UUID

def process_image(
    image_id: UUID,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process an image with the given options.

    Args:
        image_id: UUID of the image to process
        options: Optional processing options

    Returns:
        Dict containing processing result

    Raises:
        ImageNotFoundError: If image doesn't exist
    """
    pass
```

### TODO Cleanup:
```python
# Convert TODOs to documented issues or remove
# Before:
# TODO: Add caching here

# After (if keeping):
# NOTE: Caching could improve performance here. See issue #123.

# Or remove if no longer relevant
```

### Logging Standardization:
```python
# Consistent logging levels:
logger.debug()   # Detailed debugging
logger.info()    # Normal operations
logger.warning() # Potential issues
logger.error()   # Errors that need attention
logger.critical() # System failures
```

Begin by scanning files for P3 issues.
```

### Verification
```bash
# Run linters
flake8 core/ content/ agents/
mypy core/ --ignore-missing-imports
```

### Completion Sign-off
- [ ] Type hints added
- [ ] TODOs addressed
- [ ] Docstrings added
- [ ] Unused imports removed
- [ ] Logging standardized

---

## Phase 4 Completion Checklist

### All Tasks Complete
- [ ] 4.0 Testing infrastructure set up
- [ ] 4.1 Model tests (70% coverage)
- [ ] 4.2 View tests (60% coverage)
- [ ] 4.3 Agent tests (70% coverage)
- [ ] 4.4 Provider tests (70% coverage)
- [ ] 4.5 Integration tests
- [ ] 4.6 Frontend tests
- [ ] 4.7 E2E tests
- [ ] 4.8 Code polish

### Coverage Targets
- [ ] Overall coverage: 70%+
- [ ] Models: 70%+
- [ ] Views: 60%+
- [ ] Agents: 70%+
- [ ] Providers: 70%+

### Quality Gates
- [ ] All tests pass
- [ ] No linter errors
- [ ] Type hints on public APIs
- [ ] Docstrings on public functions

---

## Final Remediation Checklist

After completing ALL phases:

### Phase 1 ✓
- [ ] All credentials rotated
- [ ] Security vulnerabilities fixed
- [ ] SSRF/XSS/CSRF protected

### Phase 2 ✓
- [ ] Rate limiting implemented
- [ ] Input validation in place
- [ ] Error handling standardized

### Phase 3 ✓
- [ ] Code decomposed into modules
- [ ] Architecture improved
- [ ] Technical debt reduced

### Phase 4 ✓
- [ ] 70%+ test coverage
- [ ] E2E tests passing
- [ ] Code polished

### Final Verification
- [ ] `python manage.py check` passes
- [ ] `pytest` all tests pass
- [ ] `make start` succeeds
- [ ] All features work
- [ ] Security scan clean

---

## Success!

After completing all phases, the codebase should have:

- **Security Score:** 8+/10 (was 5.1)
- **Testing Score:** 7+/10 (was 3.5)
- **Overall Score:** 8+/10 (was 6.0)

Create final git tag:
```bash
git tag -a v2.0-remediated -m "Code review remediation complete"
```

Update documentation and celebrate! 🎉
