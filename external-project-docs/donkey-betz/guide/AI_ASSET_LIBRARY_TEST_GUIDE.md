# AI-First Asset Library - Test Guide

## Prerequisites

1. **Backend Setup**
   ```bash
   cd backend
   
   # Apply migrations
   python manage.py migrate content 0022
   
   # Start Django server
   python manage.py runserver
   
   # In another terminal, start Celery worker
   celery -A server worker -l info --pool=solo
   
   # Ensure Redis is running
   redis-server
   ```

2. **Frontend Setup**
   ```bash
   cd donkey-betz-frontend
   
   # Install dependencies (if needed)
   npm install
   
   # Start dev server
   npm run dev
   ```

3. **Authentication**
   - Ensure you're logged in to the application
   - The frontend should have your auth token in localStorage

## Testing Flow

### 1. Navigate to Content Studio
- Go to: http://localhost:5173/content-studio
- Click on "Asset Library" in the sidebar

### 2. Initial State
- You should see the "Generate" view by default
- The AI Generation Panel should display:
  - 6 asset type options (Logo, Brand Colors, Typography, Marketing, Product, Social)
  - Quota status at the bottom
  - Active brand indicator (or it will create a default brand)

### 3. Test Brand Guidelines
- Click "Guidelines" tab
- Should auto-load or create a default brand identity
- Try clicking the Edit button (pencil icon)
- Make changes and save
- Check that the compliance score updates

### 4. Test AI Generation
- Go back to "Generate" tab
- Select "Logo & Brand Mark"
- Choose 3 variations
- Select a style (e.g., "Modern & Minimalist")
- Optionally add custom instructions
- Click "Generate Logo & Brand Mark"

**Expected Results:**
- Progress bar should appear showing percentage
- Quota should update after generation
- Toast notification on success
- Auto-switch to Gallery view

### 5. Test Gallery View
- Should see your generated assets
- Each asset should have:
  - AI-generated badge (purple sparkle icon)
  - Category grouping
  - Brand compliance score (if visible)
- Try toggling "AI-Generated Only" filter
- Test grid/list view toggle

### 6. Test Asset Actions
- Click on an asset to select it
- Try the delete action (if available in bulk actions)
- Test approve action (creates shared asset)

### 7. Test Quota Management
- Check quota display in Generate view
- Should show:
  - Current tier (free/basic/pro/enterprise)
  - Daily usage (X/Y)
  - Monthly usage (X/Y)  
  - Credits remaining
  - Progress bar

### 8. Error Scenarios
- Try generating when quota is exhausted
- Test with network disconnected
- Check empty states work correctly

## API Verification

You can also test the API directly:

```bash
# Get your auth token from browser localStorage
TOKEN="your-auth-token"

# Test quota status
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/content/quota/status/

# Test brand identity
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/content/brand-identity/active/

# List assets
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/content/assets/?ai_only=true
```

## Common Issues

1. **"Authentication Required" Error**
   - Ensure you're logged in
   - Check that apiClient has your token

2. **Generation Fails**
   - Check Celery worker is running
   - Verify OpenAI API key is set
   - Check Redis is running

3. **No Assets Showing**
   - Toggle AI-only filter off/on
   - Check browser console for errors
   - Verify API is returning data

4. **Quota Shows 0**
   - Default quota should be created automatically
   - Check backend logs for errors

## Success Indicators

✅ Brand identity loads/creates automatically
✅ Generation shows real-time progress
✅ Assets appear in gallery after generation
✅ Quota updates after each generation
✅ Toast notifications appear for all actions
✅ Loading states show during async operations
✅ Error messages are user-friendly

## Next Steps

If everything works:
1. Try different asset types
2. Test with multiple variations
3. Edit brand guidelines and regenerate
4. Test the search and filters
5. Check responsive design on mobile

Report any issues with:
- Browser console errors
- Network tab responses
- Backend server logs
- Celery worker output