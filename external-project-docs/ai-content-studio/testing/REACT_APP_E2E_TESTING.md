# React Native Web App - End-to-End Testing Documentation

## Testing Status Overview

| Section | Feature | Status | Notes | Last Tested |
|---------|---------|--------|-------|-------------|
| **Studio** | Text Generation | 🔄 Testing | - | - |
| | Image Generation | ⏳ Pending | - | - |
| | Voice Recording | ⏳ Pending | - | - |
| **Gallery** | View Content | ⏳ Pending | - | - |
| | Filter/Search | ⏳ Pending | - | - |
| | Delete Content | ⏳ Pending | - | - |
| **Campaign** | Create Campaign | ⏳ Pending | - | - |
| | View Campaigns | ⏳ Pending | - | - |
| | Analytics | ⏳ Pending | - | - |
| **Profile** | User Info | ⏳ Pending | - | - |
| | Settings | ⏳ Pending | - | - |
| | Achievements | ⏳ Pending | - | - |

Legend: ✅ Working | ❌ Broken | 🔄 Testing | ⏳ Pending | ⚠️ Partial

---

## Section 1: Studio (Content Generation)

### Fixes Applied (2025-08-31)
1. **API Response Mapping** - Updated `api.ts` to properly map backend responses:
   - Text: Maps `result` → `text` and `content`
   - Image: Maps `result` → `image_url`
   - Blog: Extracts `blog_post` object
   - Social: Extracts `social_posts` object
2. **Parameter Naming** - Fixed `type` vs `content_type` mismatch
3. **App Restarted** - Changes applied and ready for testing

### 1.1 Text Generation

#### Test Cases

| Test ID | Description | Steps | Expected Result | Actual Result | Status |
|---------|-------------|-------|-----------------|---------------|--------|
| ST-001 | Generate Blog Post | 1. Navigate to Studio<br>2. Select "Blog Post"<br>3. Enter topic<br>4. Click Generate | Blog post generated and displayed | API works, returns blog with title, content, meta | ✅ API |
| ST-002 | Generate Social Media | 1. Navigate to Studio<br>2. Select "Social Media"<br>3. Enter topic<br>4. Select platforms<br>5. Click Generate | Social posts for selected platforms | API works, returns posts for Twitter/LinkedIn | ✅ API |
| ST-003 | Generate Custom Text | 1. Navigate to Studio<br>2. Select "Custom Text"<br>3. Enter prompt<br>4. Click Generate | Text content generated | API works, returns generated text | ✅ API |
| ST-004 | Generate AI Image | 1. Navigate to Studio<br>2. Select "AI Image"<br>3. Enter prompt<br>4. Click Generate | Image generated and displayed | API works, returns image URL | ✅ API |
| ST-005 | Select Visual Style | 1. Select "AI Image"<br>2. Choose style (e.g., Cyberpunk)<br>3. Generate | Image with selected style | - | ⏳ UI |

#### API Endpoints Used
- `POST /api/content/create/` - Main text generation
- `POST /api/content/blog/generate/` - Blog generation
- `POST /api/content/social/generate/` - Social media generation
- `GET /api/memory/search/` - Memory context

#### Known Issues
- [ ] Issue description here

#### Test Environment
- Backend URL: http://localhost:8001
- Frontend URL: http://localhost:8081
- Test User: testuser / testpass123
- Auth Token: <redacted-993f8273-2026-04-20>

---

### 1.2 Image Generation

#### Test Cases

| Test ID | Description | Steps | Expected Result | Actual Result | Status |
|---------|-------------|-------|-----------------|---------------|--------|
| SI-001 | Generate Single Image | 1. Navigate to Studio<br>2. Select "Image"<br>3. Enter prompt<br>4. Click Generate | Image generated and displayed | - | ⏳ |
| SI-002 | Batch Generation | 1. Select batch mode<br>2. Set count to 4<br>3. Generate | 4 images generated | - | ⏳ |
| SI-003 | Apply Style | 1. Select a style<br>2. Generate image | Image with style applied | - | ⏳ |
| SI-004 | Custom Parameters | 1. Adjust CFG, steps<br>2. Generate | Image respects parameters | - | ⏳ |
| SI-005 | Image-to-Image | 1. Upload image<br>2. Enter transformation<br>3. Generate | Transformed image | - | ⏳ |

#### API Endpoints Used
- `POST /api/content/create/` - Single image
- `POST /api/content/batch/` - Batch generation
- `POST /api/content/img2img/` - Image transformation
- `GET /api/styles/` - Get available styles

#### Known Issues
- [ ] Issue description here

---

### 1.3 Voice Recording & Processing

#### Test Cases

| Test ID | Description | Steps | Expected Result | Actual Result | Status |
|---------|-------------|-------|-----------------|---------------|--------|
| SV-001 | Record Audio | 1. Click record<br>2. Speak<br>3. Stop recording | Audio recorded successfully | - | ⏳ |
| SV-002 | Transcribe Audio | 1. Record/upload audio<br>2. Click transcribe | Text transcription displayed | - | ⏳ |
| SV-003 | Format Conversation | 1. Upload multi-speaker<br>2. Process | Speaker diarization works | - | ⏳ |
| SV-004 | Voice Command | 1. Record command<br>2. Process | Command executed | - | ⏳ |
| SV-005 | Save to Memory | 1. Transcribe<br>2. Save | Saved in memory system | - | ⏳ |

#### API Endpoints Used
- `POST /api/voice/transcribe/` - Transcription
- `POST /api/voice/format-conversation/` - Conversation formatting
- `POST /api/voice/command/` - Voice commands
- `GET /api/voice/history/` - Voice history

#### Known Issues
- [ ] Issue description here

---

## Testing Procedure

### Pre-Test Setup
1. Start all services: `make full-stack`
2. Verify services running: `make status`
3. Open React app: http://localhost:8081
4. Login with test credentials
5. Open browser console for error monitoring

### During Testing
1. Clear browser cache before each section
2. Monitor network tab for API calls
3. Check console for errors
4. Take screenshots of issues
5. Note exact error messages

### Post-Test
1. Document all findings
2. Update status in this document
3. Create GitHub issues for bugs
4. Move to next section only when current is ✅

---

## Error Log Template

```
Date: [YYYY-MM-DD HH:MM]
Test ID: [e.g., ST-001]
Error Type: [API/UI/Logic/Other]
Description: [What happened]
Expected: [What should happen]
Actual: [What actually happened]
Console Error: [Copy exact error]
Network Error: [Status code and message]
Screenshot: [Link or description]
Steps to Reproduce: [Exact steps]
```

---

## Quick Commands

```bash
# Start everything
make full-stack

# Check status
make status

# View logs
tail -f /tmp/django.log  # Backend
tail -f /tmp/mobile.log   # React app

# Test specific API
curl -X POST http://localhost:8001/api/content/create/ \
  -H "Authorization: Token <redacted-993f8273-2026-04-20>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "content_type": "text"}'
```

---

## Next Steps After Each Section

1. **All Tests Pass (✅)**
   - Move to next section
   - Update documentation

2. **Some Tests Fail (❌)**
   - Fix critical issues first
   - Re-test failed cases
   - Document workarounds

3. **Blocked Tests (🚫)**
   - Identify dependencies
   - Fix blocking issues
   - Resume testing

---

Last Updated: 2025-08-31
Current Section: Studio - Text Generation