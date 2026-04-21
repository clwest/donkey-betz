# Authentication Setup for Unified Platform

## Overview
After implementing the unified memory sharing system, authentication needed to be reconfigured for both AI Content Studio and DBAO to work with the shared database.

## User Accounts Created

### Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: admin@example.com
- **Permissions**: Superuser (full access)
- **API Token**: `<redacted-cd802334-2026-04-20>`

### Test User
- **Username**: `testuser`
- **Password**: `test123`
- **Email**: test@example.com
- **Permissions**: Regular user
- **API Token**: `<redacted-c4ba8e9a-2026-04-20>`

## Configuration Files Updated

### AI Content Studio Frontend
**File**: `/ai-content-studio/ai-studio-web/.env`
```env
VITE_AUTH_TOKEN=<redacted-cd802334-2026-04-20>
```

### Both Backend Systems
Users and tokens are synchronized in both:
- AI Content Studio backend (port 8000)
- DBAO backend (port 8000)

## Testing Authentication

### API Test
```bash
# Test with admin token
curl -H "Authorization: Token <redacted-cd802334-2026-04-20>" \
  http://localhost:8000/api/dashboard/stats/

# Test with test user token
curl -H "Authorization: Token <redacted-c4ba8e9a-2026-04-20>" \
  http://localhost:8000/api/dashboard/stats/
```

### Frontend Access
1. Open http://localhost:8081 (AI Content Studio Web)
2. The application will automatically use the configured token
3. Dashboard and all features should work without authentication errors

## Django Admin Access

### AI Content Studio Admin
- URL: http://localhost:8000/admin/
- Username: `admin`
- Password: `admin123`

### DBAO Admin
- URL: http://localhost:8000/admin/ (when DBAO is running)
- Username: `admin`
- Password: `admin123`

## Troubleshooting

### If Authentication Fails
1. Check that the backend server is running
2. Verify the token in the .env file matches the database
3. Restart the frontend after changing the .env file
4. Clear browser cache/cookies if needed

### Create New Token
```python
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()
user = User.objects.get(username='admin')
Token.objects.filter(user=user).delete()
token = Token.objects.create(user=user)
print(f'New token: {token.key}')
```

## Security Notes

⚠️ **Important**: These are development credentials only!
- Change all passwords before deploying to production
- Use environment variables for production tokens
- Enable HTTPS for production deployments
- Consider implementing OAuth2 or JWT for production

## Memory Sharing with Authentication

The unified memory system respects authentication:
- Each user's memories are isolated
- API endpoints require valid authentication tokens
- Memory sync operations are user-specific
- Cross-user memory access is not permitted

## Next Steps for Production

1. **Implement proper user registration flow**
2. **Add password reset functionality**
3. **Set up email verification**
4. **Implement session management**
5. **Add role-based access control (RBAC)**
6. **Set up API rate limiting**
7. **Implement audit logging**
8. **Add two-factor authentication (2FA)**