# YouTube Upload Setup Guide

## Prerequisites

You already have:
- ✅ `GOOGLE_API_KEY` in your `.env` file
- ✅ YouTube upload service implementation

## Setup Steps

### 1. Enable YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Go to "APIs & Services" > "Library"
4. Search for "YouTube Data API v3"
5. Click on it and press "ENABLE"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace account)
   - Fill in the required fields:
     - App name: "Donkey Betz Platform Content Creator"
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes: `https://www.googleapis.com/auth/youtube.upload`
   - Add test users: Your Google account email

4. Create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "YouTube Upload Client"
   - Click "CREATE"

5. Download the credentials JSON file
6. Save it as `youtube_credentials.json` in your backend directory

### 3. Update Environment Variables

Add these to your `.env` file:

```bash
# YouTube Upload Configuration
YOUTUBE_CREDENTIALS_FILE=youtube_credentials.json
YOUTUBE_TOKEN_FILE=youtube_token.pickle
```

### 4. First-Time Authentication

Run the authentication script below. It will:
- Open a browser window for Google sign-in
- Request permission to upload videos to YouTube
- Save the authentication token for future use

### 5. Security Notes

- Add `youtube_credentials.json` and `youtube_token.pickle` to `.gitignore`
- Keep these files secure - they provide upload access to your YouTube channel
- The token will auto-refresh when needed

## Usage Example

```python
from content.services.youtube_upload_service import get_youtube_service

# Initialize service
youtube = get_youtube_service()

# Upload a video
result = youtube.upload_video(
    video_path="path/to/video.mp4",
    title="My AI-Generated Video",
    description="Created with our content pipeline",
    tags=["AI", "automated", "content"],
    category="Science & Technology",
    privacy_status="private"  # Start with private for testing
)

if result['success']:
    print(f"Video uploaded: {result['video_url']}")
else:
    print(f"Upload failed: {result['error']}")
```

## Troubleshooting

1. **"Credentials file not found"**: Make sure `youtube_credentials.json` exists
2. **"Access blocked"**: Ensure YouTube Data API v3 is enabled
3. **"Quota exceeded"**: Check your API quotas in Google Cloud Console
4. **"Invalid credentials"**: Delete `youtube_token.pickle` and re-authenticate

## API Quotas

YouTube Data API has quotas:
- Default: 10,000 units per day
- Video upload: ~1600 units per upload
- Approximately 6 video uploads per day with default quota

To increase quota:
1. Go to APIs & Services > YouTube Data API v3
2. Click "Quotas"
3. Request quota increase if needed