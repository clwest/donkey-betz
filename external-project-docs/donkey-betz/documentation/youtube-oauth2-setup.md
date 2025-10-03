# YouTube OAuth2 Setup Guide

## Overview

This guide explains how to set up YouTube OAuth2 authentication for the web application, replacing the desktop OAuth flow with a proper web-based flow using Django Allauth.

## Prerequisites

1. Google Cloud Project with YouTube Data API v3 enabled
2. OAuth 2.0 credentials configured for web application
3. Django Allauth installed and configured

## Setup Steps

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Enable YouTube Data API v3:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "ENABLE"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
3. Configure OAuth consent screen if not already done:
   - Choose "External" for public apps
   - Fill in required fields:
     - App name: "Your App Name"
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes:
     - `.../auth/youtube.upload`
     - `.../auth/youtube.readonly`
     - `.../auth/youtube.force-ssl`
   - Add test users if in testing mode

4. Create OAuth client ID:
   - Application type: "Web application"
   - Name: "YouTube Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:8000` (development)
     - `http://localhost:5173` (frontend development)
     - Your production URL
   - Authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://localhost:8000/api/content/youtube/oauth/connected/`
     - Your production callback URLs
   - Click "CREATE"

5. Download the credentials and note:
   - Client ID
   - Client Secret

### 3. Configure Django Settings

Add to your `.env` file:

```bash
# Google OAuth2 for YouTube
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

The settings are already configured in `settings.py`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': env('GOOGLE_OAUTH_CLIENT_SECRET', ''),
        },
        'SCOPE': [
            'profile',
            'email',
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt': 'consent',
        }
    }
}
```

### 4. Run Migrations

Apply the YouTube models migration:

```bash
cd backend
python manage.py migrate content
```

### 5. Configure Allauth Social App (Admin)

1. Run the Django server: `python manage.py runserver`
2. Go to Django Admin: `http://localhost:8000/admin/`
3. Navigate to "Social applications"
4. Click "Add social application"
5. Fill in:
   - Provider: Google
   - Name: YouTube OAuth
   - Client id: (from Google Cloud Console)
   - Secret key: (from Google Cloud Console)
   - Sites: Select your site (usually example.com for development)
6. Save

## API Endpoints

### Check Connection Status
```
GET /api/content/youtube/oauth/status/
```

Response:
```json
{
  "connected": true,
  "channel": {
    "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "title": "My Channel",
    "subscriber_count": 1000,
    "video_count": 50,
    "view_count": 100000
  }
}
```

### Get Connect URL
```
GET /api/content/youtube/oauth/connect-url/
```

Response:
```json
{
  "success": true,
  "connected": false,
  "connect_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "message": "Use connect_url to start YouTube OAuth2 flow"
}
```

### Upload Video
```
POST /api/content/youtube/oauth/upload/
```

Request body:
```json
{
  "video_path": "/path/to/video.mp4",
  "title": "My Video Title",
  "description": "Video description",
  "tags": ["tag1", "tag2"],
  "category": "Science & Technology",
  "privacy_status": "private"
}
```

### Get Upload History
```
GET /api/content/youtube/oauth/history/?limit=20&offset=0&status=completed
```

### Disconnect Account
```
POST /api/content/youtube/oauth/disconnect/
```

## Frontend Integration

### 1. Check Connection Status

```javascript
const checkYouTubeConnection = async () => {
  const response = await fetch('/api/content/youtube/oauth/status/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  return data.connected;
};
```

### 2. Connect YouTube Account

```javascript
const connectYouTube = async () => {
  // Get the connect URL
  const response = await fetch('/api/content/youtube/oauth/connect-url/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  
  if (!data.connected) {
    // Redirect user to Google OAuth
    window.location.href = data.connect_url;
  }
};
```

### 3. Handle OAuth Callback

After user authorizes, they'll be redirected to `/api/content/youtube/oauth/connected/`. 
You should configure this endpoint to redirect back to your frontend with success/error status.

### 4. Upload Video

```javascript
const uploadVideo = async (videoData) => {
  const response = await fetch('/api/content/youtube/oauth/upload/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(videoData)
  });
  
  const result = await response.json();
  if (result.success) {
    console.log('Video uploaded:', result.video_url);
  }
};
```

## Security Considerations

1. **Token Storage**: OAuth tokens are stored securely in Django Allauth's SocialToken model
2. **Refresh Tokens**: Automatically handled by Allauth when tokens expire
3. **Scopes**: Only request necessary YouTube scopes
4. **HTTPS**: Always use HTTPS in production
5. **State Parameter**: Used to prevent CSRF attacks in OAuth flow

## Troubleshooting

### "YouTube account not connected"
- Ensure user has completed OAuth flow
- Check Django admin for SocialAccount entry

### "Invalid scope" error
- Verify scopes in Google Cloud Console match settings.py
- Ensure YouTube Data API v3 is enabled

### Token expired
- Allauth should auto-refresh, but you can manually refresh:
  ```python
  from allauth.socialaccount.models import SocialToken
  token = SocialToken.objects.get(account__user=user, account__provider='google')
  # Token will auto-refresh on next API call
  ```

### Quota limits
- YouTube API has daily quota limits
- Monitor usage in Google Cloud Console
- Implement rate limiting if necessary

## Migration from Desktop OAuth

If migrating from the old desktop OAuth flow:

1. Users need to reconnect their YouTube accounts
2. Old tokens (pickle files) can be deleted
3. Update any references to `youtube_upload_service.py` to use `youtube_oauth_service.py`
4. The old endpoints remain for backward compatibility but should be deprecated

## Next Steps

1. Implement frontend YouTube connection UI
2. Add progress tracking for uploads
3. Implement playlist management UI
4. Add video analytics dashboard
5. Set up webhooks for upload status updates