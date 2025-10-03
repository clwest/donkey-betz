# Detailed Investigation: Testing & Quality

## Common Issues to Investigate

### Issue 1: Low Test Coverage
**Problem**: Many components lack tests, making refactoring risky

**Investigation Steps:**

1. **Coverage Analysis**
   ```bash
   # Generate coverage report
   cd backend
   pytest --cov=. --cov-report=html --cov-report=term-missing
   
   # Find untested files
   find . -name "*.py" -not -path "*/test*" -not -path "*/migrations/*" | while read file; do
       if ! grep -q "$file" htmlcov/index.html; then
           echo "No coverage: $file"
       fi
   done
   ```

2. **Critical Path Coverage**
   ```bash
   # Check coverage for critical services
   pytest --cov=ai_partner --cov=agent_orchestra --cov=memory --cov=api_services
   
   # Find untested views
   grep -r "class.*View\|def.*view" backend/api/ --include="*.py" | while read line; do
       file=$(echo $line | cut -d: -f1)
       view=$(echo $line | cut -d: -f2)
       if ! grep -q "${file##*/}" backend/*/tests/; then
           echo "Untested: $line"
       fi
   done
   ```

3. **Test Type Distribution**
   ```bash
   # Count test types
   echo "Unit tests: $(grep -r "TestCase" backend/*/tests/ | wc -l)"
   echo "Integration tests: $(grep -r "TransactionTestCase\|APITestCase" backend/*/tests/ | wc -l)"
   echo "Async tests: $(grep -r "async def test" backend/*/tests/ | wc -l)"
   ```

### Issue 2: Flaky Tests
**Problem**: Tests that pass/fail intermittently

**Investigation Steps:**

1. **Identify Flaky Tests**
   ```bash
   # Run tests multiple times
   for i in {1..10}; do
       echo "Run $i"
       pytest backend/agent_orchestra/tests/test_orchestration.py -v > test_run_$i.log 2>&1
   done
   
   # Check for inconsistencies
   grep -h "FAILED\|PASSED" test_run_*.log | sort | uniq -c
   ```

2. **Common Flaky Patterns**
   ```python
   # Look for time-dependent tests
   grep -r "datetime.now\|time.time\|sleep" backend/*/tests/ --include="*.py"
   
   # Look for order-dependent tests
   grep -r "\.objects\.all\|\.objects\.filter" backend/*/tests/ --include="*.py" | grep -v "order_by"
   
   # Look for external dependencies
   grep -r "requests\.\|http\|external.*api" backend/*/tests/ --include="*.py" | grep -v "mock\|patch"
   ```

### Issue 3: Missing Integration Tests
**Problem**: Unit tests pass but features break in production

**Investigation Steps:**

1. **API Integration Tests**
   ```bash
   # Find API views without integration tests
   find backend/api -name "views.py" | while read view_file; do
       test_file="${view_file/views/tests/test_views}"
       if [ ! -f "$test_file" ]; then
           echo "Missing integration tests: $view_file"
       fi
   done
   ```

2. **WebSocket Tests**
   ```bash
   # Check for WebSocket test coverage
   find backend -name "consumers.py" | while read consumer_file; do
       app_name=$(dirname $consumer_file | xargs basename)
       if ! grep -q "WebsocketCommunicator" backend/$app_name/tests/; then
           echo "No WebSocket tests: $consumer_file"
       fi
   done
   ```

## Specific Testing Queries

### Query 1: Test Quality Analysis
```bash
# Find tests without assertions
grep -r "def test" backend/*/tests/ --include="*.py" -A 20 | grep -B 20 "def test" | grep -v "assert\|self.assert"

# Find tests with generic names
grep -r "def test_1\|def test_foo\|def test_something" backend/*/tests/ --include="*.py"

# Find disabled tests
grep -r "@skip\|@unittest.skip\|pytest.skip" backend/*/tests/ --include="*.py"
```

### Query 2: Mock Usage Analysis
```bash
# Find unmocked external calls
grep -r "requests\.\|openai\.\|polygon\." backend/*/tests/ --include="*.py" | grep -v "@mock\|@patch\|Mock"

# Find excessive mocking
grep -r "@patch" backend/*/tests/ --include="*.py" -c | sort -nr | head -10

# Find mock assertions
grep -r "assert_called\|assert_not_called" backend/*/tests/ --include="*.py"
```

### Query 3: Test Performance
```bash
# Find slow tests
pytest --durations=10 backend/

# Find tests with sleep
grep -r "time.sleep\|sleep(" backend/*/tests/ --include="*.py"

# Memory-intensive tests
grep -r "range(1000\|range(10000\|\.objects\.bulk_create" backend/*/tests/ --include="*.py"
```

## Test Implementation Examples

### Test 1: Proper API Test
```python
# test_views.py
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class StockAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    @patch('api_services.polygon_service.PolygonService.get_quote')
    def test_get_stock_quote(self, mock_get_quote):
        # Arrange
        mock_get_quote.return_value = {
            'symbol': 'AAPL',
            'price': 150.00,
            'change': 2.50
        }
        
        # Act
        response = self.client.get('/api/stocks/AAPL/')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['symbol'], 'AAPL')
        self.assertEqual(response.data['price'], 150.00)
        mock_get_quote.assert_called_once_with('AAPL')
```

### Test 2: WebSocket Test
```python
# test_consumers.py
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from ai_partner.consumers import ChatConsumer

class TestChatConsumer(TransactionTestCase):
    @database_sync_to_async
    def create_user(self):
        return User.objects.create_user('testuser', 'test@test.com', 'pass')
    
    async def test_chat_message(self):
        # Setup
        user = await self.create_user()
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            "/ws/chat/"
        )
        communicator.scope['user'] = user
        
        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send message
        await communicator.send_json_to({
            'type': 'chat.message',
            'message': 'Hello AI'
        })
        
        # Receive response
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'chat.response')
        self.assertIn('message', response)
        
        # Disconnect
        await communicator.disconnect()
```

### Test 3: Memory System Test
```python
# test_memory_integration.py
from django.test import TransactionTestCase
from memory.services import ConversationMemoryService
from ai_partner.models import ConversationSession, Message

class MemoryIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.service = ConversationMemoryService()
        self.user = User.objects.create_user('testuser')
        self.session = ConversationSession.objects.create(user=self.user)
    
    def test_memory_creation_from_conversation(self):
        # Create message
        message = Message.objects.create(
            session=self.session,
            user=self.user,
            content="Remember that my favorite color is blue",
            role="user"
        )
        
        # Process message
        memory = self.service.create_from_message(message)
        
        # Verify memory
        self.assertIsNotNone(memory)
        self.assertEqual(memory.user, self.user)
        self.assertIn("blue", memory.content)
        self.assertIsNotNone(memory.embedding)
        
        # Verify searchability
        results = self.service.search("favorite color", user=self.user)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].id, memory.id)
```

## Test Fixtures and Factories

### Create Test Factories
```python
# factories.py
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class ConversationSessionFactory(DjangoModelFactory):
    class Meta:
        model = ConversationSession
    
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=4)
    is_active = True

class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message
    
    session = factory.SubFactory(ConversationSessionFactory)
    user = factory.LazyAttribute(lambda obj: obj.session.user)
    content = factory.Faker('text')
    role = 'user'
```

## Testing Best Practices

### Proper Test Structure
```python
# Follow AAA pattern
class TestBusinessLogic(TestCase):
    def test_calculate_opportunity_score(self):
        # Arrange
        reddit_post = RedditPostFactory(
            title="Need help with inventory management",
            score=150,
            num_comments=45
        )
        
        # Act
        opportunity_score = calculate_opportunity_score(reddit_post)
        
        # Assert
        self.assertGreater(opportunity_score, 0.7)
        self.assertLess(opportunity_score, 1.0)
```

### Test Isolation
```python
# Use transactions for database isolation
class TestWithDatabase(TransactionTestCase):
    def setUp(self):
        # Each test gets clean database
        super().setUp()
        
    def test_concurrent_updates(self):
        # Test can modify database freely
        pass

# Mock external dependencies
class TestExternalAPIs(TestCase):
    @patch('api_services.polygon_service.requests.get')
    def test_stock_api_failure(self, mock_get):
        mock_get.side_effect = RequestException("API Down")
        
        result = get_stock_quote('AAPL')
        
        self.assertEqual(result['error'], 'API unavailable')
```

### Performance Testing
```python
# test_performance.py
from django.test.utils import override_settings
from django.test import TestCase
import time

class PerformanceTest(TestCase):
    @override_settings(DEBUG=False)
    def test_memory_search_performance(self):
        # Setup - create 1000 memories
        memories = [
            ConversationMemoryFactory()
            for _ in range(1000)
        ]
        
        # Test search performance
        start_time = time.time()
        results = memory_search("test query")
        duration = time.time() - start_time
        
        # Assert performance threshold
        self.assertLess(duration, 1.0, "Search took too long")
        
    def test_api_response_time(self):
        # Measure API response time
        start_time = time.time()
        response = self.client.get('/api/stocks/AAPL/')
        duration = time.time() - start_time
        
        self.assertLess(duration, 0.5, "API response too slow")
```

## Quality Improvement Plan

### 1. Increase Test Coverage
```bash
# Set coverage goals
echo "Minimum coverage targets:
- Overall: 80%
- Critical paths: 95%
- New code: 100%
" > .coveragerc

# Add pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
pytest --cov=. --cov-fail-under=80
EOF
chmod +x .git/hooks/pre-commit
```

### 2. Continuous Testing
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          docker-compose run backend pytest
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### 3. Test Documentation
```python
# Add docstrings to tests
class TestComplexFeature(TestCase):
    """
    Tests for the complex feature implementation.
    
    These tests cover:
    - Happy path scenarios
    - Edge cases
    - Error conditions
    - Performance requirements
    """
    
    def test_happy_path(self):
        """
        Test that the feature works correctly under normal conditions.
        
        Given: Valid input data
        When: Feature is executed
        Then: Expected output is produced
        """
        pass
```