# Authentication API Documentation

The Donkey Betz platform uses JWT (JSON Web Token) authentication with optional two-factor authentication (2FA) for enhanced security.

## Table of Contents
1. [Overview](#overview)
2. [Registration](#registration)
3. [Login](#login)
4. [Token Management](#token-management)
5. [Two-Factor Authentication](#two-factor-authentication)
6. [Password Management](#password-management)
7. [Profile Management](#profile-management)
8. [Security Best Practices](#security-best-practices)

## Overview

### Authentication Flow
1. User registers with email and password
2. Email verification (optional but recommended)
3. User logs in and receives JWT tokens
4. Access token used for API requests
5. Refresh token used to obtain new access tokens
6. Optional 2FA for enhanced security

### Token Types
- **Access Token**: Short-lived (8 hours), used for API requests
- **Refresh Token**: Long-lived (7 days), used to refresh access tokens

## Registration

### Create New Account
```http
POST /api/auth/registration/
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com",
  "password1": "SecurePassword123!",
  "password2": "SecurePassword123!",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Response (201 Created)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "pk": 123,
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

#### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Email Verification

#### Verify Email
```http
POST /api/auth/registration/verify-email/
Content-Type: application/json
```

#### Request Body
```json
{
  "key": "verification-key-from-email"
}
```

#### Resend Verification Email
```http
POST /api/auth/registration/resend-email/
Content-Type: application/json
Authorization: Bearer {access_token}
```

## Login

### Standard Login
```http
POST /api/auth/login/
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

Or using username:
```json
{
  "username": "johndoe",
  "password": "SecurePassword123!"
}
```

#### Response (200 OK)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "pk": 123,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Login with 2FA
If 2FA is enabled, include the token:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "two_factor_token": "123456"
}
```

### Logout
```http
POST /api/auth/logout/
Authorization: Bearer {access_token}
```

## Token Management

### Refresh Access Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json
```

#### Request Body
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Response
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access_expiration": "2025-01-15T20:30:00Z"
}
```

### Token Verification
```http
POST /api/auth/token/verify/
Content-Type: application/json
```

#### Request Body
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Two-Factor Authentication

### Enable 2FA

#### Step 1: Generate Setup
```http
POST /api/user/2fa/enable/
Authorization: Bearer {access_token}
```

#### Response
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "secret": "JBSWY3DPEHPK3PXP",
  "backup_codes": [
    "12345678",
    "87654321",
    "24681357",
    "13572468",
    "98765432"
  ]
}
```

#### Step 2: Confirm Setup
```http
POST /api/user/2fa/confirm/
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### Request Body
```json
{
  "token": "123456"
}
```

### Disable 2FA
```http
POST /api/user/2fa/disable/
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### Request Body
```json
{
  "password": "CurrentPassword123!"
}
```

### Check 2FA Status
```http
GET /api/user/2fa/status/
Authorization: Bearer {access_token}
```

#### Response
```json
{
  "enabled": true,
  "backup_codes_remaining": 5,
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Verify 2FA Token
```http
POST /api/user/2fa/verify/
Content-Type: application/json
```

#### Request Body
```json
{
  "user_id": 123,
  "token": "123456"
}
```

## Password Management

### Change Password (Authenticated)
```http
POST /api/auth/password/change/
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### Request Body
```json
{
  "old_password": "CurrentPassword123!",
  "new_password1": "NewSecurePassword456!",
  "new_password2": "NewSecurePassword456!"
}
```

### Reset Password (Forgot Password)

#### Step 1: Request Reset
```http
POST /api/auth/password/reset/
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com"
}
```

#### Step 2: Confirm Reset
```http
POST /api/auth/password/reset/confirm/
Content-Type: application/json
```

#### Request Body
```json
{
  "uid": "MQ",
  "token": "reset-token-from-email",
  "new_password1": "NewSecurePassword456!",
  "new_password2": "NewSecurePassword456!"
}
```

## Profile Management

### Get Profile
```http
GET /api/user/profile/
Authorization: Bearer {access_token}
```

#### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "AI enthusiast and entrepreneur",
  "avatar": "https://api.donkeybetz.com/media/avatars/johndoe.jpg",
  "date_joined": "2025-01-01T00:00:00Z",
  "last_login": "2025-01-15T10:00:00Z",
  "is_verified": true,
  "two_factor_enabled": false
}
```

### Update Profile
```http
PUT /api/user/profile/
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### Request Body
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "bio": "Building the future with AI",
  "timezone": "America/New_York"
}
```

### User Settings
```http
GET /api/user/settings/
Authorization: Bearer {access_token}
```

#### Response
```json
{
  "notifications": {
    "email": true,
    "push": true,
    "agent_updates": true,
    "marketing": false
  },
  "privacy": {
    "profile_public": false,
    "show_activity": true
  },
  "preferences": {
    "theme": "dark",
    "language": "en",
    "timezone": "America/New_York"
  },
  "ai_settings": {
    "default_model": "gpt-4",
    "monthly_budget": 100.00,
    "budget_alerts": true
  }
}
```

## Security Best Practices

### Token Storage
- **Web Applications**: Store in memory or secure cookies with HttpOnly and Secure flags
- **Mobile Apps**: Use secure device storage (Keychain on iOS, Keystore on Android)
- **Never store tokens in**: LocalStorage, SessionStorage, or plain text

### Token Refresh Strategy
```javascript
// Example token refresh implementation
async function makeAuthenticatedRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${getAccessToken()}`
      }
    });
    
    if (response.status === 401) {
      // Token expired, try to refresh
      const newToken = await refreshAccessToken();
      if (newToken) {
        // Retry with new token
        return fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${newToken}`
          }
        });
      }
    }
    
    return response;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}
```

### Rate Limiting
- Registration: 3 attempts per minute
- Login: 5 attempts per minute
- Password reset: 3 attempts per hour
- 2FA attempts: 5 attempts per 15 minutes

### Security Headers
Always include these headers in production:
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### Additional Security Measures
1. **IP Whitelisting**: Available for enterprise accounts
2. **Session Management**: Automatic logout after inactivity
3. **Device Tracking**: Monitor and manage logged-in devices
4. **Audit Logging**: Track all authentication events
5. **Anomaly Detection**: Automatic alerts for suspicious activity

## Error Responses

### Common Authentication Errors

#### Invalid Credentials (401)
```json
{
  "detail": "Invalid email or password."
}
```

#### Account Locked (423)
```json
{
  "detail": "Account temporarily locked due to multiple failed login attempts."
}
```

#### Email Not Verified (403)
```json
{
  "detail": "Email verification required. Please check your email."
}
```

#### Invalid Token (401)
```json
{
  "detail": "Token is invalid or expired."
}
```

#### Rate Limited (429)
```json
{
  "detail": "Request was throttled. Expected available in 43 seconds."
}
```

## Code Examples

### Python (requests)
```python
import requests

# Login
response = requests.post('https://api.donkeybetz.com/api/auth/login/', json={
    'email': 'user@example.com',
    'password': 'SecurePassword123!'
})
tokens = response.json()

# Make authenticated request
headers = {'Authorization': f'Bearer {tokens["access"]}'}
profile = requests.get('https://api.donkeybetz.com/api/user/profile/', headers=headers)
```

### JavaScript (fetch)
```javascript
// Login
const response = await fetch('https://api.donkeybetz.com/api/auth/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePassword123!'
  })
});
const tokens = await response.json();

// Make authenticated request
const profile = await fetch('https://api.donkeybetz.com/api/user/profile/', {
  headers: {'Authorization': `Bearer ${tokens.access}`}
});
```

### cURL
```bash
# Login
curl -X POST https://api.donkeybetz.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123!"}'

# Make authenticated request
curl https://api.donkeybetz.com/api/user/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```