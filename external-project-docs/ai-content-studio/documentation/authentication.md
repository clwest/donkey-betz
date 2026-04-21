# Authentication Guide

## Overview

AI Content Studio uses token-based authentication with Django REST Framework's Token Authentication. This provides a simple, stateless authentication mechanism perfect for API clients and frontend applications.

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    
    Client->>API: POST /api/auth/register/
    API->>Database: Create User & Token
    API-->>Client: Return Token
    
    Client->>API: POST /api/auth/login/
    API->>Database: Validate Credentials
    API-->>Client: Return Token
    
    Client->>API: GET /api/content/list/<br/>Header: Authorization: Token XXX
    API->>Database: Validate Token
    API-->>Client: Return Content
```

## Token Management

### Obtaining a Token

Tokens are obtained through two endpoints:

1. **Registration** - Returns a token immediately upon account creation
2. **Login** - Returns a token for existing users

### Token Format

Tokens are 40-character hexadecimal strings:
```
<redacted-993f8273-2026-04-20>
```

### Using Tokens

Include the token in the `Authorization` header for all authenticated requests:
```http
Authorization: Token <redacted-993f8273-2026-04-20>
```

## Security Best Practices

### Client-Side Storage

**Web Applications:**
```javascript
// Store in memory (most secure for SPAs)
let authToken = null;

// Or in sessionStorage (clears on tab close)
sessionStorage.setItem('authToken', token);

// Avoid localStorage for sensitive tokens
// localStorage.setItem('authToken', token); // ⚠️ Less secure
```

**Mobile Applications:**
```swift
// iOS - Use Keychain
KeychainWrapper.standard.set(token, forKey: "authToken")

// Android - Use EncryptedSharedPreferences
val sharedPreferences = EncryptedSharedPreferences.create(...)
sharedPreferences.edit().putString("authToken", token).apply()
```

### Token Transmission

Always use HTTPS in production:
```javascript
// ✅ Good - HTTPS
fetch('https://api.aicontentstudio.com/api/content/list/', {
    headers: {
        'Authorization': `Token ${token}`
    }
})

// ❌ Bad - HTTP (only for local development)
fetch('http://api.aicontentstudio.com/api/content/list/', ...)
```

## Frontend Integration Examples

### JavaScript/React

```javascript
// api-client.js
class APIClient {
    constructor() {
        this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
        this.token = null;
    }

    setToken(token) {
        this.token = token;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            }
        };

        if (this.token) {
            config.headers['Authorization'] = `Token ${this.token}`;
        }

        const response = await fetch(url, config);
        
        if (response.status === 401) {
            // Token invalid - redirect to login
            this.token = null;
            window.location.href = '/login';
        }

        return response;
    }

    async login(username, password) {
        const response = await this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            this.setToken(data.token);
            return data;
        }
        
        throw new Error('Invalid credentials');
    }

    async createContent(type, prompt) {
        const response = await this.request('/content/create/', {
            method: 'POST',
            body: JSON.stringify({ type, prompt })
        });

        return response.json();
    }
}

// Usage in React component
const api = new APIClient();

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const { token, user } = await api.login(username, password);
            console.log('Logged in:', user);
            // Store token and redirect
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
            />
            <input 
                type="password"
                value={password} 
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
            />
            <button type="submit">Login</button>
        </form>
    );
}
```

### Python Client

```python
import requests
from typing import Optional, Dict, Any

class AIContentStudioClient:
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to API."""
        url = f"{self.base_url}{endpoint}"
        
        headers = kwargs.pop('headers', {})
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        
        response = self.session.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and store authentication token."""
        response = self._request('POST', '/auth/login/', json={
            'username': username,
            'password': password
        })
        data = response.json()
        self.token = data['token']
        return data
    
    def register(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """Register new account and store token."""
        response = self._request('POST', '/auth/register/', json={
            'username': username,
            'password': password,
            'email': email
        })
        data = response.json()
        self.token = data['token']
        return data
    
    def create_content(self, prompt: str, content_type: str = 'text') -> Dict[str, Any]:
        """Generate AI content."""
        return self._request('POST', '/content/create/', json={
            'type': content_type,
            'prompt': prompt
        }).json()
    
    def list_content(self) -> Dict[str, Any]:
        """List user's content."""
        return self._request('GET', '/content/list/').json()
    
    def search_memory(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memories."""
        return self._request('POST', '/memory/search/', json={
            'query': query,
            'limit': limit
        }).json()

# Usage example
client = AIContentStudioClient()

# Login
client.login('testuser', 'testpass123')

# Create content
result = client.create_content(
    prompt="Write a haiku about Python programming",
    content_type="text"
)
print(f"Generated: {result['result']}")

# Search memories
memories = client.search_memory("Python")
for memory in memories['results']:
    print(f"Found: {memory['content'][:50]}...")
```

## Token Lifecycle

### Token Expiration

Currently, tokens don't expire automatically. For production, consider implementing:

1. **Token Rotation**: Periodically generate new tokens
2. **Expiration**: Add timestamp checking
3. **Refresh Tokens**: Implement JWT with refresh tokens

### Token Revocation

To logout/revoke a token, you can:

1. **Client-side**: Simply delete the token from storage
2. **Server-side**: Implement a logout endpoint that deletes the token from the database

## Error Handling

### Common Authentication Errors

**401 Unauthorized**
```json
{
    "detail": "Invalid token."
}
```
**Action**: Token is invalid or missing. User needs to login again.

**403 Forbidden**
```json
{
    "detail": "You do not have permission to perform this action."
}
```
**Action**: Token is valid but user lacks permission for this resource.

### Handling Token Errors

```javascript
// Axios interceptor example
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            // Clear token and redirect to login
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
```

## Testing Authentication

### Manual Testing with curl

```bash
# Store token in variable
TOKEN="<redacted-993f8273-2026-04-20>"

# Make authenticated request
curl -H "Authorization: Token $TOKEN" \
     http://localhost:8000/api/content/list/

# Test invalid token
curl -H "Authorization: Token invalid_token_here" \
     http://localhost:8000/api/content/list/
# Returns 401 Unauthorized
```

### Automated Testing

```python
# test_auth.py
import unittest
import requests

class TestAuthentication(unittest.TestCase):
    def test_login_success(self):
        response = requests.post('http://localhost:8000/api/auth/login/', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())
    
    def test_invalid_token(self):
        response = requests.get(
            'http://localhost:8000/api/content/list/',
            headers={'Authorization': 'Token invalid'}
        )
        self.assertEqual(response.status_code, 401)
```

## Migration from Other Auth Systems

### From JWT to Token Auth

If migrating from JWT:
```python
# Old JWT header
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# New Token header  
Authorization: Token 993f8273f70877e23b5c7d2f...
```

### From Session Auth

If migrating from cookie-based sessions:
```javascript
// Old: Cookies sent automatically
fetch('/api/content/list/', { credentials: 'include' })

// New: Explicit token header
fetch('/api/content/list/', {
    headers: { 'Authorization': `Token ${token}` }
})
```

## Security Checklist

- [ ] Always use HTTPS in production
- [ ] Store tokens securely (not in localStorage for sensitive apps)
- [ ] Implement token expiration for production
- [ ] Add rate limiting on auth endpoints
- [ ] Log authentication attempts
- [ ] Implement account lockout after failed attempts
- [ ] Use strong password requirements
- [ ] Consider 2FA for high-security applications

## Next Steps

- [API Endpoints](endpoints.md) - Full endpoint documentation
- [Frontend Integration](../guides/frontend-integration.md) - Complete React setup
- [Payment Integration](../guides/payment-integration.md) - Add Stripe subscriptions