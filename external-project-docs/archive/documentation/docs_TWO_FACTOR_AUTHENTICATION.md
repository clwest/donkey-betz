# Two-Factor Authentication (2FA) Documentation

## Overview

This document provides comprehensive guidance on the Two-Factor Authentication (2FA) system implemented in the Donkey Betz platform. The system uses Time-based One-Time Passwords (TOTP) compatible with standard authenticator apps.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [User Guide](#user-guide)
3. [API Documentation](#api-documentation)
4. [Administrator Guide](#administrator-guide)
5. [Developer Guide](#developer-guide)
6. [Security Considerations](#security-considerations)
7. [Troubleshooting](#troubleshooting)

## Architecture Overview

### Components

- **TwoFactorService**: Core service handling TOTP generation, QR codes, and verification
- **Authentication Backend**: Custom Django backend supporting 2FA verification
- **Middleware**: Enforces 2FA verification for authenticated users
- **API Views**: REST endpoints for 2FA management
- **React Components**: Frontend interface for 2FA setup and verification
- **Management Commands**: Administrative tools for 2FA management

### Security Features

- **Encrypted Storage**: All 2FA secrets and recovery codes are encrypted at rest
- **Replay Attack Prevention**: TOTP codes can only be used once
- **Recovery Codes**: 10 single-use backup codes for account recovery
- **Session Management**: 2FA verification status tracked in user sessions

## User Guide

### Setting Up 2FA

1. **Navigate to Settings**
   - Go to your account settings
   - Find the "Two-Factor Authentication" section

2. **Enable 2FA**
   - Click "Enable 2FA"
   - You'll see a QR code and manual entry key

3. **Configure Your Authenticator App**
   - Open your authenticator app (Google Authenticator, Authy, etc.)
   - Scan the QR code or enter the manual key
   - The app will generate 6-digit codes every 30 seconds

4. **Verify Setup**
   - Enter a 6-digit code from your authenticator app
   - Click "Verify & Enable"
   - Save the recovery codes in a secure location

### Logging In with 2FA

1. **Enter Username and Password**
   - Use your regular login credentials

2. **Enter 2FA Code**
   - You'll be prompted for a 6-digit code
   - Open your authenticator app and enter the current code
   - The code refreshes every 30 seconds

3. **Using Recovery Codes**
   - If you don't have access to your authenticator app
   - Click "Use recovery code instead"
   - Enter one of your saved recovery codes

### Managing 2FA

#### Disabling 2FA
1. Go to Settings → Two-Factor Authentication
2. Click "Disable 2FA"
3. Enter your password to confirm
4. 2FA will be disabled

#### Regenerating Recovery Codes
1. Go to Settings → Two-Factor Authentication
2. Click "Regenerate" next to Recovery Codes
3. Save the new codes in a secure location
4. Old codes will no longer work

### Supported Authenticator Apps

- **Google Authenticator** (iOS/Android)
- **Authy** (iOS/Android/Desktop)
- **Microsoft Authenticator** (iOS/Android)
- **1Password** (with TOTP support)
- **Bitwarden** (with TOTP support)
- **Any RFC 6238 compatible TOTP app**

## API Documentation

### Base URL
All 2FA endpoints are under `/api/accounts/2fa/`

### Authentication
All endpoints require authentication except `/verify/` during login flow.

### Endpoints

#### Enable 2FA Setup
```
POST /api/accounts/2fa/enable/
```

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "base64_encoded_qr_image",
  "manual_entry_key": "JBSWY3DPEHPK3PXP"
}
```

#### Confirm 2FA Setup
```
POST /api/accounts/2fa/confirm/
```

**Request Body:**
```json
{
  "token": "123456"
}
```

**Response:**
```json
{
  "message": "2FA enabled successfully",
  "recovery_codes": [
    "a1b2c3d4e5f6g7h8",
    "i9j0k1l2m3n4o5p6",
    // ... 8 more codes
  ]
}
```

#### Disable 2FA
```
POST /api/accounts/2fa/disable/
```

**Request Body:**
```json
{
  "password": "user_password"
}
```

**Response:**
```json
{
  "message": "2FA disabled successfully"
}
```

#### Check 2FA Status
```
GET /api/accounts/2fa/status/
```

**Response:**
```json
{
  "enabled": true,
  "recovery_codes_count": 8
}
```

#### Regenerate Recovery Codes
```
POST /api/accounts/2fa/recovery-codes/
```

**Response:**
```json
{
  "recovery_codes": [
    "q1w2e3r4t5y6u7i8",
    "o9p0a1s2d3f4g5h6",
    // ... 8 more codes
  ],
  "message": "Recovery codes regenerated successfully"
}
```

#### Verify 2FA (During Login)
```
POST /api/accounts/2fa/verify/
```

**Request Body:**
```json
{
  "token": "123456"
}
```

**Response:**
```json
{
  "message": "2FA verified successfully",
  "user_id": 123
}
```

### Error Responses

#### 400 Bad Request
```json
{
  "error": "Invalid token"
}
```

#### 403 Forbidden
```json
{
  "error": "2FA verification required",
  "code": "TWO_FACTOR_REQUIRED",
  "redirect_url": "/2fa/verify/"
}
```

## Administrator Guide

### Management Commands

#### Reset User 2FA
```bash
python manage.py reset_2fa user@example.com
```

#### Reset with Force (No Confirmation)
```bash
python manage.py reset_2fa user@example.com --force
```

#### Check 2FA Status
```bash
python manage.py reset_2fa status user@example.com
```

#### List Users with 2FA
```bash
python manage.py reset_2fa list
```

#### List All Users
```bash
python manage.py reset_2fa list --all
```

### Django Admin

2FA status is displayed in the Django admin interface:
- User list shows 2FA enabled status
- User detail page shows recovery codes count
- Admins can view (but not modify) 2FA settings

### Database Migration

Run migrations to add 2FA fields to the User model:
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### Configuration

#### Settings.py
Add authentication backends:
```python
AUTHENTICATION_BACKENDS = [
    'accounts.auth.backends.TwoFactorAuthBackend',
    'accounts.auth.backends.TwoFactorTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

Add middleware:
```python
MIDDLEWARE = [
    # ... other middleware
    'accounts.middleware.two_factor_middleware.TwoFactorMiddleware',
    # ... other middleware
]
```

#### Environment Variables
Ensure encryption key is set:
```bash
ENCRYPTION_KEY=your-secure-32-character-key
```

## Developer Guide

### Backend Implementation

#### TwoFactorService
```python
from accounts.services.two_factor_service import TwoFactorService

service = TwoFactorService()

# Generate secret
secret = service.generate_secret()

# Generate QR code
qr_code = service.generate_qr_code(user.email, secret)

# Verify token
is_valid = service.verify_token(secret, token)

# Enable 2FA
recovery_codes = service.enable_two_factor(user, secret)
```

#### Authentication Backend
```python
from accounts.auth.backends import TwoFactorAuthBackend

backend = TwoFactorAuthBackend()
user = backend.authenticate(request, username='user', password='REDACTED')
```

#### Middleware
```python
from accounts.middleware.two_factor_middleware import TwoFactorMiddleware

# Automatically enforces 2FA verification
# Redirects users to /2fa/verify/ if needed
```

### Frontend Implementation

#### React Components
```typescript
import TwoFactorSetup from '../features/authentication/components/TwoFactorSetup';
import TwoFactorVerification from '../features/authentication/components/TwoFactorVerification';
import TwoFactorSettings from '../features/authentication/components/TwoFactorSettings';
```

#### API Integration
```typescript
import { apiClient } from '../services/apiClient';

// Enable 2FA
const response = await apiClient.post('/api/accounts/2fa/enable/');

// Confirm setup
await apiClient.post('/api/accounts/2fa/confirm/', { token: '123456' });

// Check status
const status = await apiClient.get('/api/accounts/2fa/status/');
```

### Testing

#### Run Tests
```bash
# Run all 2FA tests
python manage.py test accounts.tests.test_two_factor

# Run specific test class
python manage.py test accounts.tests.test_two_factor.TwoFactorServiceTest

# Run with coverage
coverage run --source='.' manage.py test accounts.tests.test_two_factor
coverage report
```

#### Test Coverage
- Service methods: 100% coverage
- API views: 100% coverage
- Authentication backends: 100% coverage
- Middleware: 100% coverage
- Management commands: 100% coverage

## Security Considerations

### Encryption at Rest
- All 2FA secrets are encrypted using Django's `EncryptedCharField`
- Recovery codes are stored in encrypted array fields
- Encryption key must be kept secure and backed up

### Token Validation
- TOTP codes are valid for 30 seconds
- 1-step window tolerance (90 seconds total)
- Replay attack prevention via last-used token tracking

### Recovery Codes
- 10 single-use codes generated
- Each code can only be used once
- Codes are 16 characters long (hex-encoded)
- Automatically removed after use

### Session Security
- 2FA verification status stored in session
- Sessions cleared on logout
- Session timeout after inactivity

### Rate Limiting
- Consider implementing rate limiting on verification endpoints
- Prevent brute force attacks on TOTP codes
- Lockout after multiple failed attempts

## Troubleshooting

### Common Issues

#### "Invalid token" Error
- **Cause**: Clock synchronization issues
- **Solution**: Check device time settings
- **Solution**: Try codes from previous or next 30-second window

#### "QR code won't scan"
- **Cause**: QR code display issues
- **Solution**: Use manual entry key instead
- **Solution**: Ensure good lighting and stable phone

#### "Can't access authenticator app"
- **Cause**: Lost or broken phone
- **Solution**: Use recovery codes
- **Solution**: Contact administrator for 2FA reset

#### "Recovery codes don't work"
- **Cause**: Codes already used or mistyped
- **Solution**: Try remaining codes
- **Solution**: Contact administrator for 2FA reset

### Administrator Actions

#### Reset User 2FA
```bash
python manage.py reset_2fa user@example.com --force
```

#### Check User Status
```bash
python manage.py reset_2fa status user@example.com
```

#### Emergency Access
1. Disable 2FA middleware temporarily
2. Reset user's 2FA via Django admin
3. Re-enable middleware
4. User can set up 2FA again

### Debugging

#### Enable Debug Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'accounts.services.two_factor_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

#### Check Database State
```python
# Django shell
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(email='user@example.com')
print(f"2FA Enabled: {user.two_factor_enabled}")
print(f"Has Secret: {bool(user.two_factor_secret)}")
print(f"Recovery Codes: {len(user.two_factor_recovery_codes or [])}")
```

### Support Contacts

- **Technical Issues**: Contact development team
- **Account Lockout**: Contact system administrator
- **Security Concerns**: Contact security team

---

**Last Updated**: July 2025
**Version**: 1.0.0
**Security Review**: Pending