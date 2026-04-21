# Complete Authentication System Documentation

## Overview
The Unified Donkey Betz platform now has a comprehensive authentication system that connects user registration through to persistent "remember me" functionality.

## Features Implemented

### 1. User Registration ✅
- **Endpoint**: `POST /api/auth/register/`
- **Frontend**: `/register` page with real-time validation
- **Features**:
  - Username uniqueness check
  - Email validation
  - Password strength requirements (8+ chars, 1 uppercase, 1 number)
  - Password confirmation matching
  - First/Last name optional fields
  - Auto-verification in dev mode
  - Email verification ready for production

### 2. Enhanced Login with Remember Me ✅
- **Endpoint**: `POST /api/auth/login-enhanced/`
- **Frontend**: `/login` page with remember me checkbox
- **Features**:
  - Login with username or email
  - Password visibility toggle
  - "Remember me for 30 days" option
  - Persistent session tokens
  - Automatic chris user fallback (your main data)

### 3. Password Reset Flow ✅
- **Forgot Password Endpoint**: `POST /api/auth/forgot-password/`
- **Reset Password Endpoint**: `POST /api/auth/reset-password/`
- **Frontend Pages**: `/forgot-password` and `/reset-password`
- **Features**:
  - Email-based reset link generation
  - Secure token validation
  - Password strength validation on reset
  - Auto-login after successful reset
  - Dev mode shows reset tokens directly

### 4. Email Verification System ✅
- **Verify Email Endpoint**: `POST /api/auth/verify-email/`
- **Resend Verification**: `POST /api/auth/resend-verification/`
- **Features**:
  - Token-based email verification
  - Resend verification capability
  - Auto-activated in dev mode
  - Production-ready email templates

### 5. Profile Management ✅
- **Profile Endpoint**: `GET/PUT/PATCH /api/auth/profile/`
- **Change Password**: `POST /api/auth/change-password/`
- **Features**:
  - View and edit profile information
  - Update email with uniqueness check
  - Change password with current password verification
  - Preferences management
  - Credits and subscription display

### 6. Session Management ✅
- **Validate Token**: `POST /api/auth/validate-token/`
- **Enhanced Logout**: `POST /api/auth/logout-enhanced/`
- **Features**:
  - Token validation with user data return
  - Remember token with 30-day expiry
  - Automatic session restoration
  - Secure logout clearing all tokens

## Default Users

### Primary User - Chris (Your Main Data)
- **Username**: chris
- **Email**: chris@donkeybetz.com
- **Token**: <redacted-993f8273-2026-04-20>
- **Auto-login**: Yes (defaults to chris if no other auth)

### Test Users
- **testuser** / testpass123
- **demo** / demo123
- **admin** / admin123

## Frontend Components

### Pages Created
1. **LoginPage.tsx**
   - Enhanced with remember me checkbox
   - Password visibility toggle
   - Links to register and forgot password

2. **RegisterPage.tsx**
   - Real-time field validation
   - Password strength indicator
   - Terms acceptance checkbox
   - Social login placeholders

3. **ForgotPasswordPage.tsx**
   - Email input for reset link
   - Success confirmation display
   - Dev mode token display

4. **ResetPasswordPage.tsx**
   - New password creation
   - Password confirmation
   - Auto-login on success

### Auth Store Updates
- `authStore.ts` enhanced with:
  - Remember me token storage
  - Session validation method
  - 30-day persistence
  - Chris user as default

## API Endpoints Summary

### Authentication
- `POST /api/auth/register/` - New user registration
- `POST /api/auth/login/` - Standard login
- `POST /api/auth/login-enhanced/` - Login with remember me
- `POST /api/auth/logout/` - Standard logout
- `POST /api/auth/logout-enhanced/` - Enhanced logout
- `GET /api/auth/user/` - Get current user

### Password Management
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password with token
- `POST /api/auth/change-password/` - Change password (authenticated)

### Email Verification
- `POST /api/auth/verify-email/` - Verify email with token
- `POST /api/auth/resend-verification/` - Resend verification email

### Profile & Session
- `GET/PUT/PATCH /api/auth/profile/` - Profile management
- `POST /api/auth/validate-token/` - Validate session token

## Security Features

1. **Password Requirements**
   - Minimum 8 characters
   - At least 1 uppercase letter
   - At least 1 number
   - Real-time validation feedback

2. **Token Management**
   - Secure token generation
   - Token rotation on password change
   - Remember tokens expire after 30 days
   - All tokens cleared on logout

3. **Email Security**
   - Email uniqueness enforced
   - Verification required (production)
   - Reset tokens expire after 1 hour
   - No user enumeration on forgot password

## Testing the System

### Quick Test Flow
1. **Registration**: Go to `/register` and create a new account
2. **Login**: Sign in at `/login` with remember me checked
3. **Forgot Password**: Click "Forgot password?" and enter email
4. **Reset Password**: Use the reset link (shown in dev mode)
5. **Profile**: Access your profile after login

### API Testing
```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "TestPass123", "confirm_password": "TestPass123"}'

# Login with remember me
curl -X POST http://localhost:8000/api/auth/login-enhanced/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123", "remember_me": true}'

# Validate token
curl -X POST http://localhost:8000/api/auth/validate-token/ \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN_HERE"}'
```

## Development vs Production

### Development Mode (DEBUG=True)
- Email verification auto-completed
- Reset tokens displayed directly
- Chris user auto-login enabled
- Detailed error messages

### Production Mode (DEBUG=False)
- Email verification required
- Reset links sent via email
- No auto-login
- Generic error messages for security

## Next Steps

The authentication system is now fully connected from registration to persistent sessions. Users can:
1. Register new accounts
2. Login with remember me
3. Reset forgotten passwords
4. Manage their profiles
5. Stay logged in for 30 days

Chris user remains the default with all data preserved and accessible.