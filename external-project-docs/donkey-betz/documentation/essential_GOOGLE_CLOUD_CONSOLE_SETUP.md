# Google Cloud Console Setup for YouTube OAuth2

## Required Redirect URIs

Add these redirect URIs to your Google OAuth2 client in the Google Cloud Console:

### Development
```
http://localhost:8001/api/content/youtube/oauth/callback/
http://localhost:8000/api/content/youtube/oauth/callback/
```

### Production (when deployed)
```
https://your-domain.com/api/content/youtube/oauth/callback/
```

## Steps to Update

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Click on your OAuth 2.0 Client ID
4. Under "Authorized redirect URIs", add the URIs above
5. Click "Save"

## Testing the Flow

1. Make sure Django server is running on port 8001:
   ```bash
   cd backend
   python manage.py runserver 8001
   ```

2. Make sure frontend is running on port 5173:
   ```bash
   cd donkey-betz-frontend
   npm run dev
   ```

3. Navigate to http://localhost:5173/content-studio
4. Click on the YouTube tab
5. Click "Connect YouTube"
6. You'll be redirected to Google OAuth
7. After authorization, you'll be redirected back to the Content Studio with YouTube connected

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Make sure the redirect URI in Google Cloud Console matches exactly
- The URI should be: `http://localhost:8001/api/content/youtube/oauth/callback/`
- Note the trailing slash is important!

### Error: "The redirect URI in the request does not match"
- Check that Django is running on port 8001
- Verify ALLOWED_HOSTS in settings.py includes 'localhost'

### Still getting redirected to API endpoint
- Clear browser cookies and cache
- Try in an incognito/private window
- Make sure you've restarted Django server after changes