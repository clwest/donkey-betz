# Frontend Integration Test Guide

This directory contains test components to verify the integration between the Django backend and React frontend.

## Quick Start

1. **Copy the test component to your frontend:**
   ```bash
   cp MemoryPalaceTest.tsx ../donkey-betz-frontend/src/components/
   ```

2. **Add to your React routes:**
   ```jsx
   import MemoryPalaceTest from './components/MemoryPalaceTest';
   
   // In your routes
   <Route path="/test/memory-palace" element={<MemoryPalaceTest />} />
   ```

3. **Navigate to test page:**
   ```
   http://localhost:3000/test/memory-palace
   ```

## What This Tests

✅ **Memory Palace Statistics API**
- Endpoint: `GET /api/memory-palace/statistics/`
- Tests connection and data retrieval

✅ **Memory Entries API**
- Endpoint: `GET /api/memory/entries/`
- Tests listing recent memories

✅ **Semantic Search API**
- Endpoint: `POST /api/memory/palace/semantic_search/`
- Tests search functionality

## Common Integration Issues

### 1. CORS Errors

If you see CORS errors in the browser console:

**Fix in Django settings.py:**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 2. Authentication Issues

If you get 401 Unauthorized:

**Fix in test component:**
```javascript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
  // OR
  'Authorization': `Token ${localStorage.getItem('authToken')}`,
}
```

### 3. Field Name Mismatches

The component handles common variations:
- `content` vs `text`
- `created_at` vs `timestamp`
- `results` array vs direct array response

### 4. 404 Not Found

Check your URL patterns:

**backend/memory/urls.py:**
```python
urlpatterns = [
    path('memory-palace/statistics/', MemoryPalaceOptimizedView.as_view(), name='memory-palace-stats'),
    path('palace/semantic_search/', semantic_search_view, name='semantic-search'),
    # etc...
]
```

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/memory-palace/statistics/` | GET | Get memory statistics |
| `/api/memory/entries/` | GET | List memory entries |
| `/api/memory/palace/semantic_search/` | POST | Search memories |
| `/api/memory/palace/timeline/` | GET | Get memory timeline |
| `/api/memory/palace/knowledge_graph/` | GET | Get knowledge graph |

## Next Steps

After successful integration test:

1. **Fix any API issues** identified by the test
2. **Update the main Memory Palace component** with correct endpoints
3. **Add proper authentication** if needed
4. **Implement WebSocket support** for real-time updates

## Production Checklist

- [ ] CORS properly configured
- [ ] Authentication working
- [ ] API endpoints accessible
- [ ] Error handling in place
- [ ] Loading states implemented
- [ ] Pagination working
- [ ] Search functionality tested
- [ ] WebSocket connection (if used)

## Debugging Tips

1. **Check Network Tab**: See exact request/response
2. **Console Logs**: Component logs all API calls
3. **Debug Info**: Expand debug section in UI
4. **Django Logs**: Check backend console for errors

Happy debugging! 🚀