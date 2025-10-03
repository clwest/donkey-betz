# YouTube Upload Integration - Complete Implementation Guide

## Overview

The YouTube Upload Service has been fully integrated into the Donkey Betz Platform, providing seamless video upload capabilities from multiple sources including OBS recordings and Content Studio assets.

## Key Features Implemented

### 1. Backend YouTube Service (`/backend/content/services/youtube_upload_service.py`)
- ✅ OAuth2 authentication with token refresh
- ✅ Single video upload with metadata
- ✅ Batch video uploads
- ✅ Playlist creation and management
- ✅ Channel information retrieval
- ✅ Automatic file handling (local files and URLs)
- ✅ Thumbnail upload support

### 2. API Endpoints (`/backend/content/views_youtube.py`)
- `GET /api/content/youtube/auth-status/` - Check YouTube authentication status
- `POST /api/content/youtube/upload/` - Upload single video
- `POST /api/content/youtube/batch-upload/` - Queue batch upload
- `POST /api/content/youtube/create-playlist/` - Create new playlist
- `GET /api/content/youtube/upload-history/` - Get upload history

### 3. OBS → YouTube Pipeline (`/backend/obs_studio/services/obs_youtube_pipeline.py`)
- ✅ Process OBS recordings for YouTube upload
- ✅ Automatic metadata generation from recordings
- ✅ Batch processing of multiple recordings
- ✅ Folder monitoring for auto-upload
- ✅ Optional file deletion after successful upload

### 4. OBS YouTube API Endpoints (`/backend/obs_studio/views_youtube.py`)
- `POST /api/obs-studio/youtube/process/` - Process single OBS recording
- `POST /api/obs-studio/youtube/batch-process/` - Batch process recordings
- `POST /api/obs-studio/youtube/monitor-folder/` - Monitor recordings folder
- `GET /api/obs-studio/youtube/status/` - Get OBS YouTube upload status

### 5. Frontend Components

#### YouTube Upload Manager (`/frontend/src/features/youtube/`)
- Full-featured upload management interface
- Privacy status selection (private/unlisted/public)
- Category selection
- Tag management
- Batch upload support
- Upload history display

#### YouTube Dashboard Widget
- Channel statistics display
- Recent uploads list
- Pending videos count
- Quick upload access

#### Upload Progress Card
- Real-time upload progress
- Pause/resume/cancel controls
- Error handling and retry

### 6. Integration Points

#### Content Studio Integration
- Direct upload from Asset Library
- Batch processing of generated content
- Metadata preservation

#### OBS Studio Integration
- Automatic recording processing
- Scene-based metadata
- Playlist organization

## Setup Instructions

### 1. YouTube API Setup

1. **Enable YouTube Data API v3**
   ```
   - Go to https://console.cloud.google.com/
   - Select your project
   - APIs & Services > Library
   - Search "YouTube Data API v3"
   - Click ENABLE
   ```

2. **Create OAuth2 Credentials**
   ```
   - APIs & Services > Credentials
   - Create Credentials > OAuth client ID
   - Application type: Desktop app
   - Download JSON file
   - Save as youtube_credentials.json in backend/
   ```

3. **Configure Environment**
   ```bash
   # Add to .env file
   YOUTUBE_CREDENTIALS_FILE=youtube_credentials.json
   YOUTUBE_TOKEN_FILE=youtube_token.pickle
   ```

4. **Initial Authentication**
   ```bash
   cd backend
   python setup_youtube_oauth.py
   ```

### 2. Testing the Integration

#### Backend API Tests
```bash
cd backend
python test_youtube_api.py
```

#### OBS Pipeline Tests
```bash
python test_obs_youtube_pipeline.py
```

#### Manual Upload Test
```bash
python test_youtube_upload.py --upload-test
```

## Usage Examples

### Single Video Upload (API)
```python
POST /api/content/youtube/upload/
{
    "content_item_id": 123,
    "title": "My Video Title",
    "description": "Video description",
    "tags": ["tag1", "tag2"],
    "category": "Science & Technology",
    "privacy_status": "private"
}
```

### Batch Upload (API)
```python
POST /api/content/youtube/batch-upload/
{
    "content_item_ids": [123, 124, 125],
    "playlist_title": "My Playlist",
    "default_privacy": "private",
    "default_tags": ["batch", "upload"]
}
```

### OBS Recording Processing
```python
POST /api/obs-studio/youtube/process/
{
    "recording_id": 456,
    "auto_upload": true,
    "privacy_status": "private",
    "custom_title": "Stream Highlights"
}
```

### Monitor OBS Folder
```python
POST /api/obs-studio/youtube/monitor-folder/
{
    "folder_path": "/Users/username/Videos/OBS",
    "auto_upload": true,
    "privacy_status": "private",
    "delete_after_upload": false
}
```

## Workflow Examples

### 1. Content Creation to YouTube
1. Generate content in Content Studio
2. Navigate to YouTube Upload Manager
3. Select videos from library
4. Configure upload settings
5. Upload individually or as batch

### 2. OBS Recording to YouTube
1. Record in OBS Studio
2. Recording automatically appears in system
3. Process recording through OBS dashboard
4. Auto-upload to YouTube with metadata

### 3. Automated Pipeline
1. Set up folder monitoring
2. OBS saves recordings to monitored folder
3. System auto-processes and uploads
4. Optional: Delete local files after upload

## Security Considerations

1. **OAuth2 Tokens**
   - Stored in `youtube_token.pickle`
   - Auto-refreshed when expired
   - Never commit to version control

2. **API Quotas**
   - Default: 10,000 units/day
   - Upload cost: ~1600 units
   - Monitor usage in Google Console

3. **File Access**
   - Local file paths validated
   - URL downloads verified
   - Temporary files cleaned up

## Troubleshooting

### Common Issues

1. **"YouTube service not authenticated"**
   - Run `python setup_youtube_oauth.py`
   - Ensure credentials file exists
   - Check OAuth consent screen setup

2. **"Quota exceeded"**
   - Check daily quota usage
   - Request quota increase if needed
   - Implement upload scheduling

3. **"File not found"**
   - Verify OBS recording paths
   - Check file permissions
   - Ensure media URLs are accessible

4. **Upload failures**
   - Check video format compatibility
   - Verify file size limits
   - Review API error messages

## Future Enhancements

1. **Scheduled Uploads**
   - Time-based upload scheduling
   - Optimal time suggestions

2. **Analytics Integration**
   - View counts tracking
   - Engagement metrics
   - Performance reports

3. **Advanced Features**
   - Custom thumbnail generation
   - Auto-captioning
   - A/B testing support

4. **Multi-Channel Support**
   - Switch between channels
   - Brand account support
   - Team collaboration

## API Rate Limits

- **Uploads**: ~6 videos/day (default quota)
- **API Calls**: 10,000 units/day
- **File Size**: 128GB max (64GB recommended)
- **Title Length**: 100 characters
- **Description**: 5000 characters
- **Tags**: 500 characters total

## Dependencies

### Python Packages
```
google-api-python-client>=2.100.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
```

### Frontend Packages
- React Query for API state management
- Universal styles for consistent UI
- Lucide icons for YouTube branding

## Testing Checklist

- [ ] OAuth2 authentication flow
- [ ] Single video upload
- [ ] Batch video upload
- [ ] Playlist creation
- [ ] OBS recording processing
- [ ] Folder monitoring
- [ ] Error handling
- [ ] Token refresh
- [ ] Upload progress tracking
- [ ] Mobile responsiveness

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API logs in Django admin
3. Verify Google Cloud Console settings
4. Check browser console for frontend errors