# Handoff 05: Test Infrastructure Overhaul

**Priority:** HIGH
**Estimated Sessions:** 2-3
**Dependencies:** None (can run in parallel with others)

---

## Problem Statement

The platform has **166 test files** but:

1. **Many appear to be exploratory/debugging scripts**, not proper tests
2. **Naming is inconsistent** - suggests organic growth
3. **No visible CI/CD integration** or coverage reports
4. **No clear testing strategy** - unit vs integration vs e2e
5. **Test organization is confusing** - files scattered across directories

---

## Current State Analysis

### Test File Distribution

```
tests/
├── __init__.py
├── ai_core_tests/
│   ├── test_agent_income.py
│   └── test_orchestration.py
├── api/
│   ├── test_api_endpoints.py
│   ├── test_odds_api.py
│   ├── test_sports_api.py
│   └── test_sports_integration.py
├── debug/                        # ⚠️ Not proper tests
│   ├── debug_rag_response.py
│   └── debug_websocket.py
├── integration/
│   ├── test_integration.py
│   ├── test_unified_integrations.py
│   ├── test_workflow_scenarios.py
│   └── test_workflow_scenarios_backup.py  # ⚠️ Backup file in tests?
├── root_tests/
│   ├── test_agent_connection.py
│   ├── test_dashboard_realtime.py
│   ├── test_indicators.py
│   ├── test_proposal_approval.py
│   ├── test_spider_feed.py
│   ├── test_websocket_indicators.py
│   ├── test_websocket_stability.py
│   └── test_websocket_working.py
├── spiders/                      # 40+ files, many look exploratory
│   ├── quick_reality_test.py     # ⚠️ "Quick" test?
│   ├── test_agent_collaboration_proof.py
│   ├── test_agent_modes.py
│   ├── test_agent_spider_connection.py
│   ├── test_ai_training_system.py
│   ├── test_api.py
│   ├── test_api_endpoints.py     # ⚠️ Duplicate name?
│   ├── verify_spider_reality.py  # ⚠️ "Verify" script?
│   └── ... (40+ more)
├── unit/
│   ├── test_agent_execution.py
│   ├── test_agent_fix.py         # ⚠️ "Fix" test?
│   ├── test_agent_routing.py
│   ├── test_agent_simple.py      # ⚠️ "Simple" test?
│   ├── test_agent_with_proper_data.py
│   ├── test_ai_keys.py
│   └── ... (40+ more)
└── views/
    └── test_video_views.py
```

### Problems Identified

1. **Debug scripts in tests/** - `debug_*.py` files are not tests
2. **Backup files** - `*_backup.py` shouldn't be in tests
3. **Verification scripts** - `verify_*.py` and `quick_*.py` are scripts, not tests
4. **Duplicate names** - Multiple `test_api_endpoints.py` in different dirs
5. **Unclear organization** - What's `root_tests` vs `unit` vs `spiders`?
6. **No fixtures or factories** - Likely lots of duplicated setup
7. **No coverage configuration** - Unknown what's actually tested

---

## Solution: Professional Test Structure

### Target State

```
tests/
├── conftest.py                 # Shared fixtures, pytest configuration
├── pytest.ini                  # Pytest settings
├── factories/                  # Test data factories
│   ├── __init__.py
│   ├── user_factory.py
│   ├── content_factory.py
│   ├── agent_factory.py
│   └── spider_factory.py
├── fixtures/                   # JSON/static test data
│   ├── sample_images.json
│   ├── sample_prompts.json
│   └── mock_api_responses/
│       ├── stability_ai.json
│       ├── runway_ml.json
│       └── elevenlabs.json
├── unit/                       # Fast, isolated unit tests
│   ├── __init__.py
│   ├── models/
│   │   ├── test_image_history.py
│   │   ├── test_video_history.py
│   │   └── test_agent_models.py
│   ├── services/
│   │   ├── test_image_generation.py
│   │   ├── test_video_generation.py
│   │   └── test_spider_intelligence.py
│   ├── agents/
│   │   ├── test_image_agent.py
│   │   ├── test_video_agent.py
│   │   ├── test_audio_agent.py
│   │   └── test_agent_router.py
│   └── utils/
│       ├── test_prompt_builder.py
│       └── test_error_messages.py
├── integration/                # Tests with database/external services
│   ├── __init__.py
│   ├── test_generation_flow.py
│   ├── test_workflow_execution.py
│   ├── test_spider_to_agent.py
│   └── test_websocket_flow.py
├── api/                        # API endpoint tests
│   ├── __init__.py
│   ├── test_generation_endpoints.py
│   ├── test_project_endpoints.py
│   └── test_spider_endpoints.py
├── e2e/                        # End-to-end tests (if needed)
│   ├── __init__.py
│   └── test_full_workflow.py
└── _archive/                   # Old tests pending review
    └── ... (moved old exploratory tests here)

scripts/                        # Development scripts (NOT tests)
├── debug_rag_response.py       # Moved from tests/debug/
├── debug_websocket.py          # Moved from tests/debug/
├── verify_spider_reality.py    # Moved from tests/spiders/
└── quick_reality_test.py       # Moved from tests/spiders/
```

---

## Implementation Plan

### Session 1: Audit, Categorize, and Setup Infrastructure

**Goal:** Understand current tests, setup pytest infrastructure

**Tasks:**

1. **Audit all test files**
   ```python
   # scripts/audit_tests.py
   import os
   import ast
   from collections import defaultdict

   def analyze_test_file(filepath):
       """Analyze a test file for structure and quality."""
       with open(filepath) as f:
           try:
               content = f.read()
               tree = ast.parse(content)
           except:
               return {'error': 'Parse error', 'lines': 0}

       # Count test functions and classes
       test_functions = []
       test_classes = []
       imports = []

       for node in ast.walk(tree):
           if isinstance(node, ast.FunctionDef):
               if node.name.startswith('test_'):
                   test_functions.append(node.name)
           elif isinstance(node, ast.ClassDef):
               if node.name.startswith('Test'):
                   test_classes.append(node.name)
           elif isinstance(node, ast.Import):
               imports.extend(alias.name for alias in node.names)
           elif isinstance(node, ast.ImportFrom):
               imports.append(node.module)

       # Determine if it's actually a test file
       is_proper_test = len(test_functions) > 0 or len(test_classes) > 0

       return {
           'lines': len(content.split('\n')),
           'test_functions': test_functions,
           'test_classes': test_classes,
           'test_count': len(test_functions),
           'is_proper_test': is_proper_test,
           'uses_pytest': 'pytest' in imports,
           'uses_unittest': 'unittest' in imports,
           'uses_django_test': 'django.test' in str(imports),
       }

   # Scan all test files
   results = defaultdict(list)

   for root, dirs, files in os.walk('tests'):
       for f in files:
           if f.endswith('.py') and not f.startswith('__'):
               filepath = os.path.join(root, f)
               analysis = analyze_test_file(filepath)
               analysis['path'] = filepath

               if analysis.get('error'):
                   results['error'].append(analysis)
               elif not analysis['is_proper_test']:
                   results['not_test'].append(analysis)
               elif analysis['test_count'] == 0:
                   results['empty'].append(analysis)
               else:
                   results['valid'].append(analysis)

   # Report
   print("=== TEST FILE ANALYSIS ===\n")

   print(f"Valid test files: {len(results['valid'])}")
   for r in results['valid'][:10]:
       print(f"  ✓ {r['path']}: {r['test_count']} tests")

   print(f"\nNot proper tests (no test functions): {len(results['not_test'])}")
   for r in results['not_test']:
       print(f"  ⚠ {r['path']}: Move to scripts/")

   print(f"\nEmpty test files: {len(results['empty'])}")
   for r in results['empty']:
       print(f"  ✗ {r['path']}: Remove or add tests")

   print(f"\nParse errors: {len(results['error'])}")
   for r in results['error']:
       print(f"  ✗ {r['path']}")
   ```

2. **Create pytest infrastructure**
   ```ini
   # pytest.ini
   [pytest]
   DJANGO_SETTINGS_MODULE = core.settings
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   testpaths = tests
   addopts =
       --strict-markers
       -v
       --tb=short
       --cov=core
       --cov=content
       --cov=agents
       --cov-report=html
       --cov-report=term-missing
   markers =
       unit: Fast, isolated unit tests
       integration: Tests requiring database or services
       api: API endpoint tests
       slow: Tests that take > 1 second
       external: Tests requiring external APIs (Stability, Runway, etc.)
   filterwarnings =
       ignore::DeprecationWarning
   ```

3. **Create conftest.py with shared fixtures**
   ```python
   # tests/conftest.py
   """
   Shared pytest fixtures for the unified platform.
   """
   import pytest
   from django.test import Client
   from django.contrib.auth import get_user_model

   User = get_user_model()


   @pytest.fixture
   def user(db):
       """Create a test user."""
       return User.objects.create_user(
           username='testuser',
           email='test@example.com',
           password=os.environ.get('TEST_USER_PASSWORD', 'change_in_env')
       )


   @pytest.fixture
   def authenticated_client(db, user):
       """Create an authenticated test client."""
       client = Client()
       client.login(username='testuser', password=os.environ.get('TEST_USER_PASSWORD', 'change_in_env'))
       return client


   @pytest.fixture
   def api_client(db, user):
       """Create an authenticated API client."""
       from rest_framework.test import APIClient
       client = APIClient()
       client.force_authenticate(user=user)
       return client


   @pytest.fixture
   def mock_stability_response():
       """Mock Stability AI response."""
       return {
           'artifacts': [
               {
                   'base64': 'iVBORw0KGgo...',  # Truncated
                   'seed': 12345,
                   'finishReason': 'SUCCESS'
               }
           ]
       }


   @pytest.fixture
   def mock_runway_response():
       """Mock Runway ML response."""
       return {
           'id': 'task_123456',
           'status': 'PENDING',
           'estimatedTime': 60
       }


   @pytest.fixture
   def mock_elevenlabs_response():
       """Mock ElevenLabs response (audio bytes)."""
       # Return minimal valid audio data
       return b'\x00\x00\x00\x00'  # Placeholder


   @pytest.fixture
   def sample_prompt():
       """Sample prompt for generation tests."""
       return "A professional logo for a tech startup, minimalist design, blue and white colors"


   @pytest.fixture
   def sample_spider_data():
       """Sample spider intelligence data."""
       return {
           'trends': [
               {'topic': 'AI Art', 'score': 85, 'source': 'techcrunch'},
               {'topic': 'Generative AI', 'score': 90, 'source': 'wired'},
           ],
           'market': {
               'hot_skills': ['AI', 'Machine Learning', 'Python'],
               'average_rate': 150
           }
       }
   ```

4. **Create test factories**
   ```python
   # tests/factories/content_factory.py
   """
   Test factories for content models.
   """
   import factory
   from factory.django import DjangoModelFactory
   from django.contrib.auth import get_user_model

   User = get_user_model()


   class UserFactory(DjangoModelFactory):
       class Meta:
           model = User

       username = factory.Sequence(lambda n: f'user{n}')
       email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
       password = factory.PostGenerationMethodCall('set_password', 'password123')


   class ImageHistoryFactory(DjangoModelFactory):
       class Meta:
           model = 'content.ImageHistory'

       user = factory.SubFactory(UserFactory)
       prompt = factory.Faker('sentence')
       image_url = factory.Faker('image_url')
       provider = 'stability'
       model = 'sdxl'
       size = '1024x1024'


   class VideoHistoryFactory(DjangoModelFactory):
       class Meta:
           model = 'content.VideoHistory'

       user = factory.SubFactory(UserFactory)
       prompt = factory.Faker('sentence')
       provider = 'runway'
       model = 'gen3a_turbo'
       status = 'completed'
   ```

**Deliverables:**
- [ ] Test audit completed
- [ ] List of files to move to scripts/
- [ ] List of files to archive/delete
- [ ] pytest.ini configured
- [ ] conftest.py with shared fixtures
- [ ] Test factories created

---

### Session 2: Reorganize and Write Core Tests

**Goal:** Move files to proper locations, write missing core tests

**Tasks:**

1. **Move non-test files to scripts/**
   ```bash
   # Create scripts directory if needed
   mkdir -p scripts/debug

   # Move debug files
   mv tests/debug/debug_rag_response.py scripts/debug/
   mv tests/debug/debug_websocket.py scripts/debug/

   # Move verification scripts
   mv tests/spiders/verify_spider_reality.py scripts/
   mv tests/spiders/quick_reality_test.py scripts/

   # Remove backup files
   rm tests/integration/test_workflow_scenarios_backup.py

   # Remove empty tests directory
   rmdir tests/debug
   ```

2. **Create archive for old tests**
   ```bash
   mkdir -p tests/_archive

   # Move questionable tests for later review
   # (Identify from audit results)
   mv tests/spiders/test_mythology_learning.py tests/_archive/
   mv tests/spiders/test_unknown_learning.py tests/_archive/
   # ... etc
   ```

3. **Write core unit tests for agents**
   ```python
   # tests/unit/agents/test_image_agent.py
   """
   Unit tests for ImageAgent.
   """
   import pytest
   from unittest.mock import Mock, patch
   from core.agents import ImageAgent


   class TestImageAgent:
       """Tests for ImageAgent."""

       @pytest.fixture
       def agent(self):
           """Create an ImageAgent instance."""
           return ImageAgent(user=None)

       def test_agent_has_correct_name(self, agent):
           """Agent should have correct name."""
           assert agent.name == "ImageAgent"

       def test_agent_has_tools(self, agent):
           """Agent should have defined tools."""
           assert len(agent.tools) > 0

       def test_agent_has_generate_image_tool(self, agent):
           """Agent should have generate_image tool."""
           tool_names = [t['name'] for t in agent.tools]
           assert 'generate_image' in tool_names

       @pytest.mark.unit
       def test_execute_without_task_fails(self, agent):
           """Execute without task should fail gracefully."""
           result = agent.execute(task="")
           assert not result.success

       @pytest.mark.unit
       @patch('content.image_generation.ImageGenerationService')
       def test_execute_with_valid_prompt(self, mock_service, agent, sample_prompt):
           """Execute with valid prompt should attempt generation."""
           mock_service.return_value.generate_image.return_value = Mock(
               success=True,
               images=['http://example.com/image.png']
           )

           result = agent.execute(task=f"Generate image: {sample_prompt}")

           # Agent should process the task
           assert result is not None

       @pytest.mark.unit
       def test_agent_records_decisions(self, agent):
           """Agent should record decisions via TimeTravelMixin."""
           agent.record_decision("test_decision", {"key": "value"})

           assert len(agent.decisions_made) > 0
           assert agent.decisions_made[-1]['decision_type'] == "test_decision"
   ```

4. **Write core unit tests for services**
   ```python
   # tests/unit/services/test_image_generation.py
   """
   Unit tests for ImageGenerationService.
   """
   import pytest
   from unittest.mock import patch, Mock
   from content.image_generation import ImageGenerationService, ImageGenerationResult


   class TestImageGenerationService:
       """Tests for ImageGenerationService."""

       @pytest.fixture
       def service(self):
           """Create service instance."""
           with patch.object(ImageGenerationService, '__init__', lambda x: None):
               svc = ImageGenerationService()
               svc.openai_key = ''
               svc.stability_key = 'test_key'
               svc.replicate_key = ''
               svc.openai_client = None
               svc.replicate_client = None
               return svc

       @pytest.mark.unit
       def test_auto_provider_selects_stability(self, service):
           """Auto provider should select Stability when key is available."""
           with patch.object(service, '_generate_with_stability') as mock:
               mock.return_value = ImageGenerationResult(success=True, images=['url'])
               service.generate_image("test prompt", provider='auto')
               mock.assert_called_once()

       @pytest.mark.unit
       def test_style_application(self, service):
           """Style should be applied to prompt."""
           styled = service._apply_style_to_prompt("a cat", "cyberpunk")
           assert "cyberpunk" in styled.lower()

       @pytest.mark.unit
       def test_no_provider_returns_error(self):
           """No available provider should return error."""
           with patch.object(ImageGenerationService, '__init__', lambda x: None):
               svc = ImageGenerationService()
               svc.openai_key = ''
               svc.stability_key = ''
               svc.replicate_key = ''
               svc.openai_client = None
               svc.replicate_client = None

               result = svc.generate_image("test", provider='auto')
               assert not result.success
               assert "No image generation providers" in result.error_message
   ```

5. **Write integration tests for workflows**
   ```python
   # tests/integration/test_generation_flow.py
   """
   Integration tests for generation flows.
   """
   import pytest
   from django.test import TransactionTestCase
   from unittest.mock import patch


   @pytest.mark.integration
   class TestImageGenerationFlow:
       """Test complete image generation flow."""

       @pytest.fixture
       def coordinator(self, user):
           """Create SuperPlatformCoordinator."""
           from core.super_platform import SuperPlatformCoordinator
           return SuperPlatformCoordinator(user=user)

       @pytest.mark.integration
       @patch('content.image_generation.ImageGenerationService.generate_image')
       def test_create_image_request(self, mock_generate, coordinator, sample_prompt):
           """Test image creation through coordinator."""
           mock_generate.return_value = Mock(
               success=True,
               images=['http://example.com/image.png'],
               provider_used='stability',
               model_used='sdxl'
           )

           result = coordinator.process(f"Create an image: {sample_prompt}")

           assert result.success
           # Classification should detect creation intent
           assert result.classification.primary_type.value in ['creation', 'conversation']
   ```

6. **Write API endpoint tests**
   ```python
   # tests/api/test_generation_endpoints.py
   """
   API endpoint tests for generation.
   """
   import pytest
   from django.urls import reverse
   from unittest.mock import patch


   @pytest.mark.api
   class TestGenerationEndpoints:
       """Test generation API endpoints."""

       @pytest.mark.api
       def test_image_generation_requires_auth(self, client):
           """Image generation endpoint requires authentication."""
           response = client.post('/api/generate/image/', {})
           assert response.status_code in [401, 403]

       @pytest.mark.api
       def test_image_generation_with_auth(self, authenticated_client, sample_prompt):
           """Authenticated user can generate images."""
           with patch('content.image_generation.ImageGenerationService.generate_image') as mock:
               mock.return_value = Mock(success=True, images=['url'])

               response = authenticated_client.post(
                   '/api/generate/image/',
                   {'prompt': sample_prompt},
                   content_type='application/json'
               )

               # Should either succeed or return validation error
               assert response.status_code in [200, 400, 422]

       @pytest.mark.api
       def test_video_generation_endpoint_exists(self, authenticated_client):
           """Video generation endpoint should exist."""
           response = authenticated_client.post(
               '/api/generate/video/',
               {'prompt': 'test'},
               content_type='application/json'
           )
           # Should not be 404
           assert response.status_code != 404
   ```

**Deliverables:**
- [ ] Non-test files moved to scripts/
- [ ] Old tests archived
- [ ] New directory structure in place
- [ ] Core unit tests for agents
- [ ] Core unit tests for services
- [ ] Integration tests for flows
- [ ] API endpoint tests
- [ ] All tests passing with `pytest`

---

### Session 3: CI/CD and Coverage

**Goal:** Setup CI/CD pipeline, establish coverage baselines

**Tasks:**

1. **Create GitHub Actions workflow**
   ```yaml
   # .github/workflows/test.yml
   name: Tests

   on:
     push:
       branches: [main, develop, feature/*]
     pull_request:
       branches: [main, develop]

   jobs:
     test:
       runs-on: ubuntu-latest

       services:
         redis:
           image: redis:7
           ports:
             - 6379:6379
         postgres:
           image: postgres:15
           env:
             POSTGRES_USER: test
             POSTGRES_PASSWORD: test
             POSTGRES_DB: test
           ports:
             - 5432:5432
           options: >-
             --health-cmd pg_isready
             --health-interval 10s
             --health-timeout 5s
             --health-retries 5

       steps:
         - uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.11'

         - name: Cache pip
           uses: actions/cache@v4
           with:
             path: ~/.cache/pip
             key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
             pip install pytest pytest-django pytest-cov factory-boy

         - name: Run unit tests
           run: pytest tests/unit -v --cov --cov-report=xml -m "unit"

         - name: Run integration tests
           run: pytest tests/integration -v -m "integration"

         - name: Upload coverage
           uses: codecov/codecov-action@v4
           with:
             files: ./coverage.xml
             fail_ci_if_error: false

     lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: '3.11'
         - run: pip install ruff
         - run: ruff check .
   ```

2. **Create coverage configuration**
   ```ini
   # .coveragerc
   [run]
   source = core,content,agents
   omit =
       */migrations/*
       */tests/*
       */__pycache__/*
       */venv/*
       */.venv/*

   [report]
   exclude_lines =
       pragma: no cover
       def __repr__
       raise AssertionError
       raise NotImplementedError
       if __name__ == .__main__.:
       if TYPE_CHECKING:
   fail_under = 50

   [html]
   directory = htmlcov
   ```

3. **Create Makefile targets for testing**
   ```makefile
   # Add to Makefile

   # ---------- Testing ----------
   .PHONY: test test-unit test-integration test-api test-coverage

   test: ## Run all tests
   	pytest tests/ -v

   test-unit: ## Run unit tests only
   	pytest tests/unit -v -m "unit"

   test-integration: ## Run integration tests only
   	pytest tests/integration -v -m "integration"

   test-api: ## Run API tests only
   	pytest tests/api -v -m "api"

   test-coverage: ## Run tests with coverage report
   	pytest tests/ --cov --cov-report=html --cov-report=term-missing
   	@echo "Coverage report: htmlcov/index.html"

   test-fast: ## Run fast tests only (no external APIs)
   	pytest tests/ -v -m "not slow and not external"
   ```

4. **Establish coverage baseline**
   ```bash
   # Run coverage and document baseline
   pytest tests/ --cov --cov-report=term-missing > coverage_baseline.txt

   # Document in handoff
   echo "=== COVERAGE BASELINE ===" >> coverage_baseline.txt
   echo "Date: $(date)" >> coverage_baseline.txt
   ```

**Deliverables:**
- [ ] GitHub Actions workflow created
- [ ] Coverage configuration in place
- [ ] Makefile test targets added
- [ ] Coverage baseline documented
- [ ] All tests passing in CI

---

## Validation Checklist

After all sessions, verify:

- [ ] `make test` runs successfully
- [ ] `make test-unit` runs fast (< 30 seconds)
- [ ] `make test-coverage` generates report
- [ ] CI pipeline runs on push
- [ ] Coverage is at least 50% for core modules
- [ ] No non-test files in tests/

---

## Files to Create/Modify

1. `pytest.ini` - Pytest configuration
2. `tests/conftest.py` - Shared fixtures
3. `tests/factories/*.py` - Test factories
4. `tests/unit/**/*.py` - Unit tests
5. `tests/integration/**/*.py` - Integration tests
6. `tests/api/**/*.py` - API tests
7. `.github/workflows/test.yml` - CI pipeline
8. `.coveragerc` - Coverage configuration
9. `Makefile` - Add test targets

---

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Test files (proper tests) | ~50? | 30-40 focused |
| Debug scripts in tests/ | Many | 0 |
| Coverage | Unknown | > 50% |
| CI pipeline | None | Passing |
| Test run time (unit) | Unknown | < 30 seconds |

---

## Commands for Next Claude Session

```bash
# Start here
cd /Users/donkeyking/development/unified-donkey-betz

# Read this handoff
cat docs/handoffs/HANDOFF_05_TEST_INFRASTRUCTURE.md

# Check current test count
find tests -name "*.py" -type f | wc -l

# Try running existing tests
pytest tests/ --collect-only | head -50

# Begin Session 1 tasks
```
