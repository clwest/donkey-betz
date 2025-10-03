# Memory UI Testing Guide
**Session 233** - Memory Palace UI Implementation

## ✅ What Was Built

### 1. Memory Components Created
- `src/components/memory/DocumentUpload.tsx` - File upload with drag-and-drop
- `src/components/memory/MemorySearch.tsx` - Semantic and keyword search
- `src/components/memory/MemoryDashboard.tsx` - Complete memory management dashboard
- `src/pages/MemoryPalace.tsx` - Main memory page

### 2. Features Implemented
- **Document Upload**: PDF, TXT, MD, JSON support with progress tracking
- **ChatGPT Import**: Automatic detection of conversations.json
- **Search**: Semantic (AI) and keyword modes with filters
- **Dashboard**: Stats showing 70,662 accessible memories
- **Privacy Breakdown**: Shows own/public/commons/marketplace
- **Recent Memories**: List of latest memory entries

## 🧪 Testing Steps

### Prerequisites
```bash
# Start backend services
cd /Users/donkeyking/development/donkey_betz/backend
make run-backend-ws-dual

# In another terminal, start frontend
cd /Users/donkeyking/development/donkey_betz/donkey-betz-ui-fresh
npm run dev
```

### Test Authentication
1. Navigate to http://localhost:5174/
2. Login with: `testuser` / `testpass123`
3. You should see the main dashboard

### Test Memory Palace
1. Click on "Memory Palace" card (or navigate to http://localhost:5174/memory)
2. You should see:
   - Overview tab with 70,662 accessible memories
   - Stats showing breakdown by privacy level
   - Four tabs: Overview, Search, Upload, Recent

### Test Document Upload
1. Go to Upload tab
2. Try drag-and-drop of a .txt or .pdf file
3. Watch progress bar during upload
4. Verify success message shows number of memories created

### Test ChatGPT Import
1. In Upload tab, drag a `conversations.json` file from ChatGPT export
2. System should auto-detect and use ChatGPT import endpoint
3. Watch for processing status
4. Verify conversations are imported

### Test Memory Search
1. Go to Search tab
2. Type a query (e.g., "business", "AI", "privacy")
3. Toggle between Semantic and Keyword search
4. Try filters:
   - Date range (Today, Week, Month, Year)
   - Content type (Conversations, Documents, etc.)
   - Importance threshold slider
5. Click on results to expand full content

### Test Recent Memories
1. Go to Recent tab
2. Should show last 10 memories with timestamps
3. Each memory shows source system and preview

## 🔍 What to Verify

### Backend Endpoints
```bash
# Test auth
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Get token from response, then test memories
curl -X GET http://localhost:8000/api/memories/ \
  -H "Authorization: Token YOUR_TOKEN"

# Test search
curl -X POST http://localhost:8000/api/memories/search/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "business", "search_type": "semantic"}'
```

### Expected Results
- ✅ 70,662 memories should be accessible
- ✅ Search should return relevant results
- ✅ Upload should create new memories
- ✅ ChatGPT import should parse conversations
- ✅ Embeddings should generate for new uploads

## 🐛 Known Issues to Check

1. **Stats endpoints might 500** - Non-critical, use fallback data
2. **WebSocket updates** - Check if real-time updates work
3. **Large file uploads** - Test with files > 5MB
4. **Embedding generation** - Verify new memories get vectors

## 📊 Success Metrics

The Memory UI is working if:
1. Users can see their 70,662 accessible memories
2. Search returns relevant results quickly
3. Document upload creates searchable memories
4. ChatGPT import successfully parses conversations
5. Privacy breakdown shows correct counts

## 🚀 Next Steps

If everything works:
1. Test embedding generation for uploaded content
2. Verify WebSocket real-time updates
3. Test bulk operations
4. Add memory deletion/editing features
5. Implement export functionality

## 📝 Notes

- Backend must be running for features to work
- Use `testuser/testpass123` for testing
- Old frontend archived at `archive/frontend_old_deprecated_2025-08-17/`
- All memory endpoints are at `/api/memories/` and `/api/ai-partner/`