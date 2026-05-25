# 🧪 Test Plan - Session 158
**Created:** November 21, 2025
**Purpose:** Verify Sessions 148-151 implementations committed in `42b6fd9`

---

## 📋 Feature Test Matrix

### ✅ Code Verification (COMPLETE)
- [x] All export functions exist (ZIP, PDF, CSV)
- [x] All share functions exist (create, view, revoke, get)
- [x] Image editing agent methods implemented
- [x] Image editing view functions exist
- [x] Django check passes (no errors)
- [x] Routes configured in urls.py

---

## 🧪 Manual Test Suite

### 1. Project Export Features (Session 148)

#### Test 1.1: Export to ZIP
**Route:** `GET /api/creative-projects/<uuid>/export/zip/`
**Function:** `core/views_image.py:12033` - `export_project_zip()`

**Steps:**
1. Create a project with images, videos, 3D models
2. Call export endpoint: `curl http://localhost:8000/api/creative-projects/{PROJECT_ID}/export/zip/`
3. Verify ZIP file downloads
4. Extract ZIP and verify all assets included

**Expected:**
- ZIP file named `{project_name}_export.zip`
- Contains all images, videos, 3D models
- Organized folder structure
- README.txt with project info

#### Test 1.2: Export to PDF
**Route:** `GET /api/creative-projects/<uuid>/export/pdf/`
**Function:** `core/views_image.py:12147` - `export_project_pdf()`

**Steps:**
1. Use same project from Test 1.1
2. Call PDF export endpoint
3. Verify PDF downloads and opens correctly

**Expected:**
- PDF file named `{project_name}_report.pdf`
- Contains project summary, asset list, stats
- Formatted professionally with images

#### Test 1.3: Export to CSV
**Route:** `GET /api/creative-projects/<uuid>/export/csv/`
**Function:** `core/views_image.py:12299` - `export_project_csv()`

**Steps:**
1. Use same project
2. Call CSV export endpoint
3. Open in spreadsheet software

**Expected:**
- CSV file with columns: asset_type, filename, created_at, etc.
- One row per asset
- Proper CSV formatting (commas, quotes)

---

### 2. Public Share Links (Session 149)

#### Test 2.1: Create Public Share Link
**Route:** `POST /api/creative-projects/<uuid>/share/create/`
**Function:** `core/views_share.py:32` - `create_project_share()`

**Steps:**
1. Create project with content
2. POST to create share endpoint:
```json
{
  "is_public": true
}
```
3. Verify response contains `share_token` and `share_url`

**Expected:**
```json
{
  "success": true,
  "share_token": "abc123...",
  "share_url": "http://localhost:8000/share/abc123/",
  "expires_at": null,
  "is_protected": false
}
```

#### Test 2.2: View Shared Project (Public)
**Route:** `GET /share/<share_token>/`
**Function:** `core/views_share.py:118` - `view_shared_project()`

**Steps:**
1. Use share_token from Test 2.1
2. Open share URL in incognito/private browser
3. Verify project loads without authentication

**Expected:**
- Project title and description visible
- All images/videos displayed
- Read-only view (no edit buttons)
- View count increments

#### Test 2.3: Password-Protected Share
**Route:** `POST /api/creative-projects/<uuid>/share/create/`
**Function:** `core/views_share.py:32`

**Steps:**
1. Create share with password:
```json
{
  "is_public": true,
  "password": "test123"
}
```
2. Visit share URL in incognito
3. Should see password prompt
4. Enter correct password
5. Verify access granted

**Expected:**
- Password form displayed (template: `share_password.html`)
- Incorrect password → error message
- Correct password → project loads
- Password stored as hash (never plaintext)

#### Test 2.4: Expiring Share Links
**Steps:**
1. Create share with expiration:
```json
{
  "is_public": true,
  "expires_in_days": 7
}
```
2. Verify `expires_at` set correctly (7 days from now)
3. Mock date past expiration
4. Visit share URL → should see "Share Expired" page

**Expected:**
- Template: `share_expired.html`
- View count NOT incremented for expired links

#### Test 2.5: Revoke Share Link
**Route:** `POST /api/creative-projects/<uuid>/share/revoke/`
**Function:** `core/views_share.py:198` - `revoke_project_share()`

**Steps:**
1. Create active share
2. POST to revoke endpoint
3. Try visiting share URL

**Expected:**
- Share marked as `is_active=false`
- Visiting share URL → "Share Not Found" (template: `share_not_found.html`)

---

### 3. Advanced Image Editing (Session 151)

#### Test 3.1: Search and Replace (Replacement Mode)
**Route:** `POST /api/stability/search-and-replace/`
**Function:** `core/views_image.py:11790` - `search_and_replace_view()`

**Steps:**
1. Upload image with a skateboard
2. Via AI Assistant: "Replace the skateboard with a scooter in image X"
3. Or API call:
```json
{
  "image_id": "...",
  "search_prompt": "skateboard",
  "replace_prompt": "scooter"
}
```

**Expected:**
- New image created with skateboard → scooter
- Original image preserved
- ~25 Stability AI credits used (~$0.07)
- Agent contribution tracked

#### Test 3.2: Search and Replace (Removal Mode)
**Agent:** `ImageEditingAgent._search_and_replace()`

**Steps:**
1. Upload image with text overlay
2. Via AI Assistant: "Remove the text from image X"
3. API call with empty replace_prompt:
```json
{
  "image_id": "...",
  "search_prompt": "text",
  "replace_prompt": ""
}
```

**Expected:**
- Text removed from image
- Background filled intelligently
- Works same as erase_object (backward compatible)

#### Test 3.3: Creative Upscale
**Route:** `POST /api/stability/creative-upscale/`
**Function:** `core/views_image.py:12399` - `creative_upscale_view()`

**Steps:**
1. Select any image
2. Via AI Assistant: "Enhance image X and add dramatic sunset lighting using creative upscale"
3. Or API call:
```json
{
  "image_id": "...",
  "prompt": "dramatic sunset lighting",
  "creativity": 0.35
}
```

**Expected:**
- Image upscaled to 4x resolution
- AI-added details based on prompt
- ~40 Stability AI credits (~$0.11)
- More dramatic/artistic than regular upscale

---

### 4. Video Enhancement Routes (Session 154)

#### Test 4.1: Video Upscale
**Route:** `POST /api/video/upscale/`
**Function:** `core/views_video.py` - `upscale_video()`

**Steps:**
1. Upload video
2. Via AI Assistant: "Upscale video 1"
3. Check if route exists and returns response

**Expected:**
- Route accessible
- Function exists and handles request
- Video upscaled using ffmpeg lanczos
- Free operation (no API cost)

#### Test 4.2: Video Effects
**Route:** `POST /api/video/effects/`
**Function:** `core/views_video.py` - `apply_video_effect()`

**Steps:**
1. Use same video
2. Via AI Assistant: "Apply cinematic effect to video 1"

**Expected:**
- 6 effects available: cinematic, vintage, noir, warm, cool, vibrant
- FFmpeg filter chains applied
- Processing ~10 seconds

---

## 🐛 Known Issues / Watch For

### Potential Issues:
1. **ProjectShare Migration** - May need manual migration if table doesn't exist
2. **Export Permissions** - Ensure user owns project before export
3. **Share Token Uniqueness** - Verify no collisions in token generation
4. **Password Storage** - Confirm using Django's make_password (hashed)
5. **File Cleanup** - Export ZIPs/PDFs should be temporary (cleanup job?)

### Testing Tips:
- Use different browsers for share link testing (avoid session cookies)
- Check database after each test (verify records created)
- Monitor Stability AI credits during image editing tests
- Check logs for any errors: `tail -f logs/django.log`

---

## 📊 Test Results Template

```
Feature: [Feature Name]
Test: [Test Number]
Date: [Date]
Tester: [Your Name]

Result: [ ] PASS  [ ] FAIL  [ ] PARTIAL

Notes:
-
-
-

Bugs Found:
1.
2.

Screenshots/Evidence:
-
```

---

## ✅ Completion Checklist

- [ ] All 4 Export tests pass
- [ ] All 5 Share Link tests pass
- [ ] All 3 Advanced Image Editing tests pass
- [ ] Both Video Enhancement routes respond
- [ ] No errors in Django logs
- [ ] Database records created correctly
- [ ] No memory leaks or performance issues

**When complete, create bug fix commit if issues found, or mark Session 158 as COMPLETE!**
