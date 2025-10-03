# Test Assertion Guidelines

## Overview

This document provides comprehensive guidelines for writing quality tests with meaningful assertions. Following these guidelines ensures that tests provide real value and catch regressions effectively.

## Current Status

**Critical Finding**: Our test assertion audit revealed that **88.7%** of test files lack meaningful assertions. This is a high-priority issue that undermines code quality and confidence in our testing suite.

## Testing Philosophy

### 1. **Assertions are the Heart of Tests**
- Tests without assertions are not tests—they're scripts
- Every test method should have at least 2 meaningful assertions
- Assertions should validate behavior, not just execution

### 2. **Quality Over Quantity**
- Better to have 10 tests with strong assertions than 100 tests with weak ones
- Focus on testing critical paths and edge cases
- Avoid assertion patterns that provide false confidence

### 3. **Test What Matters**
- Test the "why" not just the "what"
- Validate business logic and user-facing behavior
- Ensure error conditions are properly handled

## Assertion Standards

### Minimum Requirements

1. **At least 2 assertions per test method**
2. **Maximum 50% weak assertions** (status code checks only)
3. **No empty test methods**
4. **No print-only test methods**
5. **Meaningful error messages** in all assertions

### Assertion Quality Levels

#### ❌ **Poor Quality (Avoid)**
```python
def test_api_endpoint(self):
    response = self.client.get('/api/users/')
    self.assertEqual(response.status_code, 200)  # Only status check
```

#### ⚠️ **Weak Quality (Improve)**
```python
def test_api_endpoint(self):
    response = self.client.get('/api/users/')
    self.assertEqual(response.status_code, 200)
    self.assertIsNotNone(response.content)  # Minimal content check
```

#### ✅ **Good Quality (Target)**
```python
def test_api_endpoint(self):
    # Create test data
    users = [User.objects.create_user(f'user{i}', f'user{i}@example.com') for i in range(3)]
    
    # Make request
    response = self.client.get('/api/users/')
    
    # Assert response structure
    AssertionTemplates.assert_api_response(
        self, response, 
        expected_keys=['results', 'count'],
        expected_structure={'results': [{'id': int, 'username': str}]}
    )
    
    # Assert response content
    data = response.json()
    self.assertEqual(data['count'], 3)
    self.assertEqual(len(data['results']), 3)
    
    # Assert user data integrity
    for i, user_data in enumerate(data['results']):
        self.assertEqual(user_data['username'], f'user{i}')
        self.assertNotIn('password', user_data)  # Security check
```

## Assertion Templates

Use the provided `AssertionTemplates` class from `core.testing` for consistent, high-quality assertions:

### Model Testing
```python
from core.testing import AssertionTemplates, TestDataFactory

def test_user_creation(self):
    # Create user
    user = TestDataFactory.create_test_user('johndoe', 'john@example.com')
    
    # Assert user creation
    AssertionTemplates.assert_user_creation(
        self, user, 'johndoe', 'john@example.com'
    )
    
    # Assert database state
    AssertionTemplates.assert_database_state(
        self, User, expected_count=1, filters={'username': 'johndoe'}
    )
```

### API Testing
```python
def test_api_authentication_required(self):
    # Test endpoint requires authentication
    AssertionTemplates.assert_authentication_required(
        self, '/api/protected-endpoint/', 'POST'
    )
    
    # Test with valid authentication
    client = TestDataFactory.create_authenticated_client(self.user)
    response = client.post('/api/protected-endpoint/', {'data': 'test'})
    
    # Assert successful response
    AssertionTemplates.assert_api_response(
        self, response, 
        expected_status=201,
        expected_keys=['id', 'status', 'created_at']
    )
```

### Database Testing
```python
def test_database_operations(self):
    # Initial state
    initial_count = User.objects.count()
    
    # Perform operation
    user = User.objects.create_user('testuser', 'test@example.com')
    
    # Assert database state changed
    AssertionTemplates.assert_database_state(
        self, User, expected_count=initial_count + 1
    )
    
    # Assert specific record
    retrieved_user = User.objects.get(username='testuser')
    AssertionTemplates.assert_model_fields(
        self, retrieved_user, 
        {'username': 'testuser', 'email': 'test@example.com', 'is_active': True}
    )
```

### Async Testing
```python
def test_async_task(self):
    # Execute async task
    result = my_async_task.delay(test_data)
    
    # Assert task execution
    AssertionTemplates.assert_async_task_success(
        self, result, expected_status='SUCCESS'
    )
    
    # Assert task results
    task_result = result.result
    self.assertIsInstance(task_result, dict)
    self.assertEqual(task_result['status'], 'completed')
```

## Common Patterns to Avoid

### 1. **Status Code Only Tests**
```python
# ❌ Bad
def test_endpoint(self):
    response = self.client.get('/api/data/')
    self.assertEqual(response.status_code, 200)
```

### 2. **Print Statement Tests**
```python
# ❌ Bad
def test_data_processing(self):
    result = process_data(input_data)
    print(f"Result: {result}")  # Not a test!
```

### 3. **Empty Tests**
```python
# ❌ Bad
def test_important_feature(self):
    pass  # TODO: Write test
```

### 4. **Assertion-less Scripts**
```python
# ❌ Bad
def test_system_integration(self):
    service = MyService()
    service.connect()
    service.process()
    service.disconnect()
    # No assertions about what happened!
```

## Test Structure Best Practices

### 1. **AAA Pattern (Arrange, Act, Assert)**
```python
def test_user_registration(self):
    # Arrange
    user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword123'
    }
    
    # Act
    response = self.client.post('/api/auth/register/', user_data)
    
    # Assert
    self.assertEqual(response.status_code, 201)
    self.assertIn('user', response.json())
    self.assertEqual(User.objects.count(), 1)
    
    # Assert user was created correctly
    user = User.objects.get(username='newuser')
    self.assertEqual(user.email, 'newuser@example.com')
    self.assertTrue(user.is_active)
```

### 2. **Test One Thing Well**
```python
# ✅ Good - Tests one specific behavior
def test_user_cannot_register_with_duplicate_email(self):
    # Arrange
    existing_user = User.objects.create_user('existing', 'test@example.com')
    duplicate_data = {'username': 'newuser', 'email': 'test@example.com'}
    
    # Act
    response = self.client.post('/api/auth/register/', duplicate_data)
    
    # Assert
    AssertionTemplates.assert_validation_error(
        self, response, expected_fields=['email']
    )
    self.assertEqual(User.objects.count(), 1)  # No new user created
```

### 3. **Edge Case Testing**
```python
def test_pagination_edge_cases(self):
    # Test empty results
    response = self.client.get('/api/users/?page=1')
    AssertionTemplates.assert_pagination_response(
        self, response, expected_count=0
    )
    
    # Test invalid page
    response = self.client.get('/api/users/?page=999')
    self.assertEqual(response.status_code, 404)
    
    # Test negative page
    response = self.client.get('/api/users/?page=-1')
    self.assertEqual(response.status_code, 400)
```

## Error Handling Tests

### 1. **Exception Testing**
```python
def test_invalid_input_raises_exception(self):
    with self.assertRaises(ValueError) as context:
        process_invalid_data(None)
    
    self.assertIn('cannot be None', str(context.exception))
```

### 2. **Error Response Testing**
```python
def test_api_error_responses(self):
    # Test 400 Bad Request
    response = self.client.post('/api/users/', {'invalid': 'data'})
    AssertionTemplates.assert_validation_error(
        self, response, expected_fields=['username', 'email']
    )
    
    # Test 403 Forbidden
    response = self.client.delete('/api/admin/users/1/')
    AssertionTemplates.assert_permission_denied(self, response)
```

## Performance and Integration Tests

### 1. **Database Query Testing**
```python
def test_query_efficiency(self):
    # Create test data
    users = [User.objects.create_user(f'user{i}', f'user{i}@example.com') for i in range(10)]
    
    # Test with query counting
    with self.assertNumQueries(2):  # Should only need 2 queries
        response = self.client.get('/api/users/?include_profile=true')
    
    # Assert response
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.json()['results']), 10)
```

### 2. **Integration Testing**
```python
def test_full_workflow_integration(self):
    # Step 1: User registration
    registration_data = {'username': 'testuser', 'email': 'test@example.com'}
    response = self.client.post('/api/auth/register/', registration_data)
    self.assertEqual(response.status_code, 201)
    
    # Step 2: Email verification
    user = User.objects.get(username='testuser')
    self.assertFalse(user.is_verified)
    
    # Step 3: Login attempt should fail
    login_response = self.client.post('/api/auth/login/', {
        'username': 'testuser', 'password': 'password'
    })
    self.assertEqual(login_response.status_code, 400)
    
    # Step 4: Verify email
    user.is_verified = True
    user.save()
    
    # Step 5: Login should now succeed
    login_response = self.client.post('/api/auth/login/', {
        'username': 'testuser', 'password': 'password'
    })
    self.assertEqual(login_response.status_code, 200)
    self.assertIn('access_token', login_response.json())
```

## Tools and Automation

### 1. **Pre-commit Hooks**
The project includes pre-commit hooks that automatically check test assertion quality:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run test-assertions --all-files
```

### 2. **Test Audit Script**
Regular audit of test quality:

```bash
# Run full audit
python backend/scripts/audit_tests.py --project-root . --verbose

# Generate JSON report
python backend/scripts/audit_tests.py --project-root . --format json --output test_audit.json
```

### 3. **Assertion Templates**
Use the provided templates for consistent testing:

```python
from core.testing import AssertionTemplates, TestDataFactory

class MyTestCase(TestCase):
    def test_with_templates(self):
        # Templates provide consistent, high-quality assertions
        user = TestDataFactory.create_test_user()
        AssertionTemplates.assert_user_creation(self, user, 'testuser', 'test@example.com')
```

## Test Quality Metrics

### Success Criteria
- ✅ **90%+ tests have meaningful assertions**
- ✅ **Average 3+ assertions per test method**
- ✅ **<30% weak assertions (status-only checks)**
- ✅ **0 empty test methods**
- ✅ **0 print-only test methods**

### Current Status (After Improvements)
- **Files with good assertions**: 12 (8.5% → Target: 90%+)
- **Files with weak assertions**: 4 (2.8% → Target: <10%)
- **Files without assertions**: 126 (88.7% → Target: <10%)

## Common Issues and Solutions

### Issue 1: "My test runs but doesn't assert anything"
**Solution**: Add assertions that verify expected behavior:
```python
# Before
def test_user_creation(self):
    User.objects.create_user('test', 'test@example.com')

# After
def test_user_creation(self):
    user = User.objects.create_user('test', 'test@example.com')
    self.assertIsNotNone(user.id)
    self.assertEqual(user.username, 'test')
    self.assertEqual(User.objects.count(), 1)
```

### Issue 2: "My test only checks status codes"
**Solution**: Add content and structure validation:
```python
# Before
def test_api_endpoint(self):
    response = self.client.get('/api/users/')
    self.assertEqual(response.status_code, 200)

# After
def test_api_endpoint(self):
    response = self.client.get('/api/users/')
    AssertionTemplates.assert_api_response(
        self, response,
        expected_keys=['results', 'count'],
        expected_structure={'results': [{'id': int, 'username': str}]}
    )
```

### Issue 3: "My async test is hard to assert"
**Solution**: Use async assertion patterns:
```python
def test_async_operation(self):
    # Use async test helpers
    result = await async_function()
    
    # Assert async result
    self.assertIsInstance(result, dict)
    self.assertEqual(result['status'], 'completed')
    
    # Assert side effects
    self.assertEqual(Model.objects.count(), 1)
```

## Getting Help

1. **Review existing good tests** in the codebase
2. **Use AssertionTemplates** for common patterns
3. **Run the audit script** to identify issues
4. **Check pre-commit hooks** for immediate feedback
5. **Ask for code review** when unsure about assertion quality

## Future Improvements

1. **Automated test generation** for basic CRUD operations
2. **Property-based testing** for complex logic
3. **Performance regression tests** for critical paths
4. **Visual regression tests** for UI components
5. **Contract testing** for API endpoints

---

**Remember**: Good tests with strong assertions are an investment in code quality, developer confidence, and system reliability. Every assertion should tell a story about what your code is supposed to do.