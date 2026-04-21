# Port Configuration Fix
## Fixed: September 10, 2025

## 🐛 Problem
The frontend was trying to connect to port 8001 for gallery and content endpoints, but the backend is running on port 8000, causing:
```
GET http://localhost:8001/api/gallery/list/?limit=200 net::ERR_CONNECTION_REFUSED
GET http://localhost:8001/api/content/list/?type=image&limit=200 net::ERR_CONNECTION_REFUSED
```

## ✅ Solution
Fixed hardcoded port references in frontend components:

### Files Updated:
1. **VideoGenerator.tsx** - Changed all `localhost:8001` to `localhost:8000`
   - Gallery fetch URL
   - Content list URL
   - Media URL helper function

2. **ImageGenerator.tsx** - Changed all `localhost:8001` to `localhost:8000`
   - Image URL construction
   - Media path resolution

## 🧪 Verification
Both endpoints are working correctly on port 8000:

```bash
# Gallery endpoint ✅
curl "http://localhost:8000/api/gallery/list/?limit=2" \
  -H "Authorization: Token <redacted-993f8273-2026-04-20>"
# Returns: {"success": true, "images": [...]}

# Content endpoint ✅
curl "http://localhost:8000/api/content/list/?type=image&limit=2" \
  -H "Authorization: Token <redacted-993f8273-2026-04-20>"
# Returns: {"success": true, "count": 50, "results": [...]}
```

## 📝 Configuration Note
The frontend `.env` file correctly specifies port 8000:
```env
VITE_API_URL=http://localhost:8000/api
VITE_MEDIA_URL=http://localhost:8000
```

However, some components had hardcoded URLs that bypassed these environment variables.

## 🎯 Result
- ✅ Image upload from system now works
- ✅ Gallery loading works
- ✅ Content list loading works
- ✅ All frontend-backend connections on unified port 8000

## 💡 Recommendation
Consider refactoring the frontend to consistently use environment variables:
```javascript
// Instead of hardcoding:
fetch('http://localhost:8000/api/gallery/list/')

// Use environment variables:
fetch(`${import.meta.env.VITE_API_URL}/gallery/list/`)
```

This would make port configuration centralized and easier to manage.