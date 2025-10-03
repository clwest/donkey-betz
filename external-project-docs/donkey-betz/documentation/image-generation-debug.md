# Image Generation Debug Guide

## Status Summary

### ✅ Backend Working Correctly
1. **API Keys Configured**: Both OpenAI and Stability AI keys are set in .env
2. **Celery Workers Running**: 5 worker processes active
3. **API Endpoint Functional**: `/api/content/images/unified/generate/` returns proper responses
4. **Test Results**:
   - DALL-E 3: Successfully generates images (returns image immediately)
   - Stable Diffusion: Successfully initiates generation (returns task_id)
   - Debug mode: Works correctly

### 🔍 Potential Frontend Issues

If the Image Generation appears "stuck" in the frontend, check:

1. **Browser Console**: Open DevTools (F12) and check for:
   - Network errors (401, 403, 500)
   - JavaScript errors
   - CORS issues

2. **Authentication**: Ensure the user is logged in with a valid JWT token
   - Check localStorage for `access_token`
   - Token should be sent as `Bearer <token>` in Authorization header

3. **Network Tab**: When clicking "Generate":
   - Request should go to `http://localhost:8001/api/content/images/unified/generate/`
   - Should include Authorization header
   - Response should be 200 or 201

4. **Common Issues**:
   - Token expired: Try logging out and back in
   - CORS: Backend should be running on port 8001
   - Frontend expects specific response format

### 📝 Test Commands

```bash
# Test API directly
python test_image_api.py

# Check Celery workers
ps aux | grep celery

# Monitor Redis queue
redis-cli llen celery

# Check Django logs
tail -f server.log | grep -E "image|generation"
```

### 🛠️ Quick Fixes

1. **Restart Services**:
   ```bash
   # Kill and restart Celery
   pkill -f celery
   celery -A server worker -l info --pool=solo
   
   # Restart Django
   python manage.py runserver 8001
   ```

2. **Clear Browser Cache**: 
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
   - Clear localStorage and sessionStorage

3. **Test with cURL**:
   ```bash
   curl -X POST http://localhost:8001/api/content/images/unified/generate/ \
     -H "Authorization: Token YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "test", "backend": "dalle3", "style": "minimalist"}'
   ```