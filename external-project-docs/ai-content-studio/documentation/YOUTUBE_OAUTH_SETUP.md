# YouTube OAuth Setup Guide

## Error: 400 redirect_uri_mismatch

This error occurs when the redirect URI in your Google Cloud Console doesn't match the one used by the application.

## Quick Fix

### Step 1: Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Add these Authorized redirect URIs:
   ```
   http://localhost:8080/
   http://localhost:8080
   http://localhost:8001/
   http://localhost:8001
   http://localhost:8888/
   http://localhost:8888
   http://127.0.0.1:8080/
   http://127.0.0.1:8080
   ```
6. Click **Save**

### Step 2: Update YouTube Service

The application has been updated to use a fixed port (8888) for OAuth callback.

### Step 3: Download Credentials

1. In Google Cloud Console, download your OAuth 2.0 credentials
2. Save as `youtube_credentials.json` in the backend directory:
   ```
   /Users/donkeyking/development/ai-content-studio/backend/youtube_credentials.json
   ```

### Step 4: Required OAuth Scopes

Make sure your OAuth consent screen has these scopes:
- `https://www.googleapis.com/auth/youtube.upload`
- `https://www.googleapis.com/auth/youtube`

## OAuth Flow

1. When you click "Connect YouTube" in the app
2. Browser opens to Google OAuth consent page
3. You authorize the app
4. Google redirects to `http://localhost:8888/`
5. App receives authorization code
6. Credentials are saved for future use

## Troubleshooting

### If you still get redirect_uri_mismatch:

1. **Check the exact error message** - it will show the redirect URI being used
2. **Add that exact URI** to Google Cloud Console
3. **Wait 5 minutes** for changes to propagate
4. **Clear browser cache** and try again

### Common Issues:

- **Port already in use**: The app uses port 8888. Make sure nothing else is using it.
- **Credentials file missing**: Ensure `youtube_credentials.json` exists
- **Wrong project**: Verify you're using the correct Google Cloud project

## Testing YouTube Upload

Once connected, you can test with:

```python
# In Django shell
from content.youtube_service import YouTubeUploadService
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')
yt = YouTubeUploadService(user=user)
success = yt.authenticate()
print(f"Authentication: {success}")
```

## Security Notes

- Never commit `youtube_credentials.json` to git
- Token files are stored per user: `youtube_token_{user_id}.pickle`
- Tokens expire after 7 days of inactivity
- Users need to re-authenticate if token expires

## API Endpoints

- **POST `/api/youtube/connect/`** - Initialize OAuth flow
- **POST `/api/youtube/upload/`** - Upload video to YouTube
- **GET `/api/youtube/status/`** - Check connection status
- **POST `/api/youtube/disconnect/`** - Revoke YouTube access