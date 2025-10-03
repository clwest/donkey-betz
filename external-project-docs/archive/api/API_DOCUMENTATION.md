# Authentication API Documentation

This document provides a comprehensive overview of all authentication endpoints in the Donkey Betz platform.

## Overview

The authentication system provides comprehensive user management with the following features:
- JWT token-based authentication
- Email verification
- Two-factor authentication (2FA)
- Password management
- User profile management
- Privacy settings

## Base URL

All authentication endpoints are prefixed with `/api/auth/`

## Authentication Methods

The API supports three authentication methods:
1. **JWT Authentication** (recommended): Uses access and refresh tokens
2. **Token Authentication**: Single token authentication
3. **Session Authentication**: Cookie-based sessions

## Rate Limiting

Different endpoints have different rate limits:
- Login: 5 attempts per minute per IP
- Registration: 5 attempts per hour per IP
- Password reset: 3 requests per hour per email
- 2FA verification: 10 attempts per hour per session
- Profile updates: 100 requests per hour per user

## Core Authentication Endpoints

### 1. User Registration
- **POST** `/api/auth/registration/`
- Creates new user account with email verification
- Rate limit: 5 registrations per hour per IP

### 2. User Login
- **POST** `/api/auth/login/`
- Authenticates user and returns tokens
- Supports username or email login
- Handles 2FA flow if enabled
- Rate limit: 5 attempts per minute per IP

### 3. User Logout
- **POST** `/api/auth/logout/`
- Invalidates current authentication
- Requires authentication
- Rate limit: 20 requests per hour per user

### 4. Email Verification
- **POST** `/api/auth/registration/verify-email/`
- Verifies user email with key from email
- No authentication required

### 5. Resend Verification Email
- **POST** `/api/auth/registration/resend-email/`
- Requests new verification email
- Rate limit: 3 requests per hour per email

## Password Management

### 1. Change Password
- **POST** `/api/auth/password/change/`
- Change password for authenticated user
- Requires current password
- Rate limit: 5 changes per day per user

### 2. Request Password Reset
- **POST** `/api/auth/password/reset/`
- Sends password reset email
- Rate limit: 3 requests per hour per email

### 3. Confirm Password Reset
- **POST** `/api/auth/password/reset/confirm/`
- Complete password reset with token
- Rate limit: 5 attempts per hour per token

## User Profile & Settings

### 1. Get/Update Profile
- **GET/PUT/PATCH** `/api/auth/profile/`
- Retrieve or update user profile
- Requires authentication
- Rate limit: 100 requests per hour

### 2. User Settings
- **GET/PUT** `/api/auth/settings/`
- Manage AI budget and notifications
- Requires authentication
- Rate limit: 60 requests per hour

## Two-Factor Authentication (2FA)

### 1. Enable 2FA
- **POST** `/api/auth/2fa/enable/`
- Generate QR code and secret
- Rate limit: 10 requests per hour

### 2. Confirm 2FA Setup
- **POST** `/api/auth/2fa/confirm/`
- Complete 2FA setup with code
- Returns recovery codes
- Rate limit: 10 attempts per hour

### 3. Disable 2FA
- **POST** `/api/auth/2fa/disable/`
- Disable 2FA with password confirmation
- Rate limit: 5 attempts per hour

### 4. 2FA Status
- **GET** `/api/auth/2fa/status/`
- Check if 2FA is enabled
- Rate limit: 100 requests per hour

### 5. Regenerate Recovery Codes
- **POST** `/api/auth/2fa/recovery-codes/`
- Get new set of recovery codes
- Rate limit: 5 requests per day

### 6. Verify 2FA During Login
- **POST** `/api/auth/2fa/verify/`
- Complete login with 2FA code
- Rate limit: 10 attempts per hour per session

## Response Formats

### Successful Registration
```json
{
  "detail": "Verification e-mail sent.",
  "user": {
    "pk": 42,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```

### Successful Login
```json
{
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "pk": 42,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 2FA Required Response
```json
{
  "two_factor_required": true,
  "message": "Please complete 2FA verification"
}
```

### Error Response
```json
{
  "non_field_errors": ["Unable to log in with provided credentials."],
  "email": ["Email is not verified."],
  "password": ["This field is required."]
}
```

## Security Best Practices

1. **Password Requirements**:
   - Minimum 8 characters
   - Cannot be entirely numeric
   - Cannot be too similar to username/email
   - Cannot be a commonly used password

2. **Token Management**:
   - Access tokens expire in 1 hour
   - Refresh tokens expire in 7 days
   - Store tokens securely on client side
   - Use HTTPS for all API calls

3. **2FA Recommendations**:
   - Enable 2FA for enhanced security
   - Store recovery codes securely
   - Use authenticator apps (Google Authenticator, Authy)
   - Regenerate recovery codes when running low

4. **Email Verification**:
   - Required for full platform access
   - Verification links expire after 3 days
   - Can resend verification email if needed

## API Testing

You can view and test all endpoints using the interactive API documentation:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

## Support

For authentication issues or questions:
- Check the error messages for specific issues
- Ensure you're using the correct authentication headers
- Verify rate limits haven't been exceeded
- Contact support if problems persist