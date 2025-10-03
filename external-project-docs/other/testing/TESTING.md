# Frontend Testing Guide

This guide covers the testing infrastructure and best practices for the Donkey Betz frontend application.

## 🏗️ Test Infrastructure

### Tools Used
- **Jest** - JavaScript testing framework
- **React Testing Library** - React component testing utilities
- **User Event** - User interaction simulation
- **TypeScript** - Type safety in tests
- **Jest-JUnit** - CI/CD test reporting

### Configuration
- **Jest Config**: `jest.config.js`
- **Test Setup**: `src/setupTests.ts`
- **TypeScript**: `tsconfig.json`

## 📁 Test Structure

```
src/
├── __tests__/
│   ├── templates/           # Test templates for different scenarios
│   ├── services/           # Service layer tests
│   ├── store/             # State management tests
│   ├── shared/components/ # Shared component tests
│   ├── features/          # Feature-specific tests
│   └── integration/       # Integration tests
├── [feature]/
│   ├── components/
│   │   └── Component.test.tsx
│   ├── hooks/
│   │   └── useHook.test.tsx
│   └── services/
│       └── service.test.ts
```

## 🧪 Test Types

### 1. Unit Tests
Test individual components, hooks, and services in isolation.

**Example: Component Test**
```typescript
import { render, screen } from '@testing-library/react';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

### 2. Integration Tests
Test interactions between multiple components and services.

**Example: Feature Integration**
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FeatureWorkflow } from './FeatureWorkflow';

describe('FeatureWorkflow Integration', () => {
  it('completes full user workflow', async () => {
    const user = userEvent.setup();
    render(<FeatureWorkflow />);
    
    // Test complete user journey
    await user.click(screen.getByRole('button', { name: /start/i }));
    await waitFor(() => {
      expect(screen.getByText('Success!')).toBeInTheDocument();
    });
  });
});
```

### 3. Service Tests
Test API clients and business logic.

**Example: Service Test**
```typescript
import { apiService } from './apiService';

describe('apiService', () => {
  it('handles successful API response', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: 'test' })
    });
    
    const result = await apiService.getData();
    expect(result.data).toBe('test');
  });
});
```

## 📋 Test Templates

Use the provided templates in `src/__tests__/templates/` for consistent test structure:

- **component.test.template.tsx** - React component tests
- **hook.test.template.tsx** - Custom hook tests
- **service.test.template.ts** - Service/API tests
- **integration.test.template.tsx** - Integration tests

## 🚀 Running Tests

### Local Development
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- ComponentName.test.tsx

# Run tests matching pattern
npm test -- --testNamePattern="should render"
```

### CI/CD
```bash
# Run tests for CI (no watch mode)
npm run test:ci
```

## 📊 Coverage Requirements

### Minimum Coverage Thresholds
- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

### Coverage Reports
- **HTML Report**: `coverage/lcov-report/index.html`
- **LCOV**: `coverage/lcov.info` (for CI)
- **JSON**: `coverage/coverage-final.json`

## 🔧 Test Utilities

### Test Wrapper
Common providers wrapper for consistent test setup:

```typescript
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};
```

### Mock Setup
Common mocks are configured in `src/setupTests.ts`:

- **localStorage/sessionStorage**
- **fetch API**
- **WebSocket**
- **ResizeObserver**
- **IntersectionObserver**
- **matchMedia**

## 🎯 Best Practices

### 1. Test Structure
- **Arrange**: Set up test data and mocks
- **Act**: Execute the code being tested
- **Assert**: Verify the expected behavior

### 2. Test Naming
```typescript
// ✅ Good: Descriptive test names
it('displays error message when API call fails', () => {});

// ❌ Bad: Vague test names
it('handles error', () => {});
```

### 3. User-Centric Testing
```typescript
// ✅ Good: Test user interactions
await user.click(screen.getByRole('button', { name: /submit/i }));

// ❌ Bad: Test implementation details
fireEvent.click(component.find('.submit-button'));
```

### 4. Async Testing
```typescript
// ✅ Good: Proper async handling
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});

// ❌ Bad: Missing async handling
expect(screen.getByText('Success')).toBeInTheDocument();
```

### 5. Mock Management
```typescript
// ✅ Good: Clean mocks after each test
beforeEach(() => {
  jest.clearAllMocks();
});

afterEach(() => {
  jest.resetAllMocks();
});
```

## 🔍 Debugging Tests

### Common Issues
1. **Component not rendering**: Check if proper wrapper is used
2. **Async operations**: Use `waitFor` or `findBy` queries
3. **Mock not working**: Verify mock setup and clearing
4. **State updates**: Use `act()` for state changes

### Debug Tools
```typescript
// View rendered component
screen.debug();

// View specific element
screen.debug(screen.getByRole('button'));

// Check what's in the DOM
console.log(screen.getByRole('button').outerHTML);
```

## 📈 Performance Testing

### Test Performance
```typescript
// Test component render performance
it('renders quickly with large dataset', () => {
  const start = performance.now();
  render(<DataTable data={largeMockData} />);
  const end = performance.now();
  
  expect(end - start).toBeLessThan(100); // Less than 100ms
});
```

### Memory Leaks
```typescript
// Test for memory leaks
it('cleans up properly on unmount', () => {
  const { unmount } = render(<Component />);
  unmount();
  
  // Verify cleanup (no lingering timers, listeners, etc.)
});
```

## 🎨 Visual Testing

### Screenshot Testing
```typescript
// Basic snapshot test
it('matches snapshot', () => {
  const { container } = render(<Component />);
  expect(container.firstChild).toMatchSnapshot();
});

// Component-specific snapshot
it('renders loading state correctly', () => {
  render(<Component isLoading={true} />);
  expect(screen.getByTestId('loading-spinner')).toMatchSnapshot();
});
```

## 🔄 Continuous Integration

### GitHub Actions
Tests run automatically on:
- **Push** to main/develop branches
- **Pull requests** to main/develop
- **Multiple Node versions** (18.x, 20.x)

### Test Reports
- **Coverage reports** uploaded to Codecov
- **Test results** in JUnit format
- **Build artifacts** stored for 30 days

## 📚 Additional Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro)
- [User Event Documentation](https://testing-library.com/docs/user-event/intro)
- [Common Testing Patterns](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## 🤝 Contributing

When adding new tests:
1. Follow the existing test structure
2. Use appropriate test templates
3. Ensure coverage thresholds are met
4. Update this documentation if needed

## 📝 Test Checklist

Before submitting code, ensure:
- [ ] All tests pass locally
- [ ] New features have corresponding tests
- [ ] Coverage thresholds are met
- [ ] Tests follow naming conventions
- [ ] Integration tests cover critical paths
- [ ] Mocks are properly configured
- [ ] Async operations are handled correctly