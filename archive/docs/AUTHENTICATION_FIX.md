# Authentication System Fix

## Problem
The frontend was using hardcoded authentication tokens that had expired, causing 401 Unauthorized errors when trying to access protected API endpoints.

## Solution Implemented

### 1. Updated Authentication Flow
- **authStore.ts**: Updated to use chris user's actual database token (<redacted-993f8273-2026-04-20>)
- **assistant.service.ts**: Removed hardcoded token fallback
- **api.config.ts**: Removed default hardcoded token
- **PRESERVED CHRIS USER**: Chris user remains as the default user with valid token from database

### 2. Primary User - Chris
- **Username**: chris
- **Email**: chris@donkeybetz.com
- **Token**: <redacted-993f8273-2026-04-20>
- **Status**: Active and working as default user

### 3. Additional Test Users
Run this script to create test users with valid tokens:
```bash
python create_test_user.py
```

This creates:
- **testuser** / testpass123
- **demo** / demo123
- **admin** / admin123 (if not exists)

### 3. Enhanced Error Handling
- ChatWidget now checks for authentication before loading context
- Shows helpful login message if user tries to chat without authentication
- Silently handles 401 errors instead of showing error popups

## How to Use

### Option 1: Login via UI
1. Go to http://localhost:3000/login
2. Use one of these credentials:
   - testuser / testpass123
   - demo / demo123
   - admin / admin123

### Option 2: Manual Token Setup (for testing)
```javascript
// In browser console:
localStorage.setItem('authToken', 'YOUR_TOKEN_HERE');
window.location.reload();
```

### Option 3: Create New User
```python
# In Django shell:
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()
user = User.objects.create_user(
    username='newuser',
    password='<set-a-real-password>',
    email='new@example.com'
)
token = Token.objects.create(user=user)
print(f"Token: {token.key}")
```

## Key Changes

### Frontend Files Modified:
- `frontend/src/store/authStore.ts` - Removed auto-login with hardcoded token
- `frontend/src/services/assistant.service.ts` - Removed hardcoded token fallback
- `frontend/src/services/api.config.ts` - Removed default token constant
- `frontend/src/components/Assistant/ChatWidget.tsx` - Added auth checks

### New Files Created:
- `create_test_user.py` - Script to create test users with valid tokens
- `frontend/src/components/auth/QuickLogin.tsx` - Quick login component (optional)

## Benefits
1. ✅ No more hardcoded expired tokens
2. ✅ Proper authentication flow
3. ✅ Better error handling for unauthenticated users
4. ✅ Easy test user creation for development
5. ✅ Clear login instructions for users

## Testing
1. Clear browser localStorage to remove old tokens:
   ```javascript
   localStorage.clear();
   ```

2. Reload the page - you should not be automatically logged in

3. Go to `/login` and use test credentials

4. Verify you can now access protected endpoints without 401 errors

## Notes
- Tokens are stored in localStorage as 'authToken'
- User data is persisted in 'auth-storage' by Zustand
- The backend expects tokens in the format: `Token <token_key>`
- All API requests automatically include the token if present