# YouTube OAuth2 - Quick Reference

## Status: ✅ COMPLETE & WORKING

### Key URLs
- **Content Studio**: http://localhost:5173/content-studio (YouTube tab)
- **YouTube Studio**: http://localhost:5173/studio/youtube
- **OAuth Callback**: http://localhost:8001/api/content/youtube/oauth/callback/

### Google Cloud Console
**Required Redirect URI**: `http://localhost:8001/api/content/youtube/oauth/callback/`

### Environment Variables
```bash
GOOGLE_OAUTH_CLIENT_ID=306301228528-hmuv74gl1e0e4imh8r96n8m3o4hh8dqv.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-secret-here
```

### Quick Test
1. Go to http://localhost:5173/content-studio
2. Click YouTube tab
3. Click "Connect YouTube"
4. Authorize with Google
5. Upload a video

### API Endpoints
- `GET /api/content/youtube/oauth/status/` - Check connection
- `GET /api/content/youtube/oauth/connect-url/` - Get OAuth URL
- `POST /api/content/youtube/oauth/upload/` - Upload video
- `GET /api/content/youtube/oauth/history/` - Upload history
- `POST /api/content/youtube/oauth/disconnect/` - Disconnect

### Common Issues & Fixes

**Tables Missing Error**:
```bash
python manage.py migrate content 0019 --fake
python manage.py migrate content
```

**OAuth Error**: Update redirect URI in Google Cloud Console

**Import Error**: Frontend uses `useAuthStore`, not `AuthContext`

### Files to Check if Issues
- Backend: `content/views_youtube_oauth_callback.py`
- Frontend: `features/content-studio/components/YouTubeIntegration.tsx`
- Settings: `server/settings.py` (SOCIALACCOUNT_PROVIDERS)

### Upload Data Structure
```javascript
{
  video_path: "url-or-path",
  title: "Video Title",
  description: "Description",
  tags: ["tag1", "tag2"],
  category: "Science & Technology",
  privacy_status: "private",
  thumbnail_path: "optional-thumbnail-url"
}
```

### Next Features to Implement
- [ ] Scheduled uploads
- [ ] Bulk metadata editing  
- [ ] Analytics integration
- [ ] Auto-upload from OBS/DaVinci
- [ ] Thumbnail generation