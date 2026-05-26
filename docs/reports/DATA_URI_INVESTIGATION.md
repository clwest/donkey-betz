<!-- DOC-POINTER-V2 (Session 1160) -->
> **Status:** Superseded
> **Last verified:** Session 1160 (2026-05-26)
> **Current canon:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime-derived, autogen).
> **Change reason:** Session 131 investigation snapshot. The investigation's findings are point-in-time and have been folded into current code; do not cite as an active investigation.
> **Preserved because:** historical investigation record. Useful as build-history; do NOT cite for current state.

# Data URI Investigation - Session 131

**Date:** November 19, 2025
**Issue:** Image #31 was saved with 1.7MB data URI instead of file path
**Status:** ✅ RESOLVED (image converted, source identified, documented)

---

## 🔍 Investigation Summary

### The Problem
- Image #31 ("a colorful geometric robot") was saved with a data URI instead of a file path
- Data URI was 1,790,198 characters (1.7MB base64-encoded PNG)
- This prevented the image from displaying properly in the UI gallery

### The Source

**Stability AI API returns base64-encoded images, NOT URLs!**

**Location:** `content/image_generation.py:501`

```python
# Extract base64 images and seeds
images = []
for artifact in data.get("artifacts", []):
    if artifact.get("finishReason") == "SUCCESS":
        base64_image = artifact.get("base64")
        if base64_image:
            images.append(f"data:image/png;base64,{base64_image}")  # <-- Creates data URI
```

**Why This Happened:**
1. Stability AI's API returns images as base64-encoded data (not URLs)
2. `ImageGenerationService.generate_image()` creates data URIs from the base64 data
3. Test script `test_generate_then_upscale.py` saved `result.images[0]` directly to database
4. This saved the data URI instead of converting it to a file first

---

## 📍 All Data URI Creation Locations

**Found 4 locations where data URIs are created:**

1. **Line 501** - Stability AI image generation (SDXL)
2. **Line 602** - Stability AI image generation (SD3)
3. **Line 782** - Image-to-image operations (checking if input is data URI)
4. **Line 855** - Error handling (mock response with data URI)

---

## 🛡️ Why This Is By Design

**Stability AI API Design:**
- Stability AI's REST API returns base64-encoded images in the response JSON
- This is standard practice for APIs that generate images synchronously
- The alternative (file URLs) requires additional upload/hosting infrastructure

**Our Implementation:**
- `ImageGenerationService` creates data URIs to standardize the interface
- All image providers (Stability, OpenAI, Replicate) return lists of image URLs or data URIs
- This allows consistent handling across different providers

---

## ⚠️ Potential Impact on Other Features

### Images ✅ SAFE
- Production image generation (via UI) uses `generate_image_with_stability()` in `views_image.py`
- This function saves files to disk and stores file paths (NOT data URIs)
- Only test scripts that use `ImageGenerationService` directly are affected

### Videos ✅ SAFE
- Video providers (Runway ML) return video URLs, not data URIs
- VideoHistory model uses `video_url` field for actual URLs
- No risk of data URI issues with videos

### 3D Models ✅ SAFE
- Replicate API returns URLs to GLB/STL files
- MiniFigAsset model stores file URLs
- No base64 encoding involved

### Character Training ✅ SAFE
- FLUX LoRA training uses image URLs as inputs
- Trained models are stored as URLs
- No data URI creation in training pipeline

---

## ✅ Fix Applied (Session 131)

**Script:** `fix_ui_issues.py`

**What It Did:**
1. Identified image #31 with data URI
2. Decoded base64 data (1,342,630 bytes)
3. Saved to proper file: `media/generated_images/admin/converted_a40387a8.png`
4. Updated database: `file_path = "generated_images/admin/converted_a40387a8.png"`

**Result:**
- ✅ All 33 admin images now have file paths
- ✅ 0 data URIs remaining
- ✅ Image #31 now displays properly in UI

---

## 📋 Recommendations

### For Test Scripts ⚠️
**DO NOT** save `result.images` directly to database:
```python
# ❌ WRONG - Saves data URI:
image_url = result.images[0]
ImageHistory.objects.create(file_path=image_url)
```

**DO** convert data URIs to files first:
```python
# ✅ CORRECT - Convert to file:
if result.images[0].startswith('data:'):
    # Decode base64 and save to file
    # Then store file path in database
else:
    # It's a URL, safe to store directly
```

### For Production Code ✅
**Already Handled Correctly:**

The production endpoint `generate_image_with_stability()` in `core/views_image.py` already handles this properly:

```python
def generate_image_with_stability(request):
    # ... generate image ...
    result = service.generate_image(...)

    # Saves to file and stores file path (not data URI)
    image = ImageHistory.objects.create(
        user=request.user,
        file_path=file_path,  # <-- Proper file path
        ...
    )
```

### For Future Development 🔮
1. **Consider adding a utility function** to convert data URIs to files
2. **Add validation** to prevent data URIs from being saved to ImageHistory
3. **Document** that `ImageGenerationResult.images` can contain EITHER URLs OR data URIs
4. **Add tests** to ensure all image creation paths save files properly

---

## 🧪 Testing Guidance

**When writing tests that use `ImageGenerationService` directly:**

```python
from content.image_generation import ImageGenerationService
from content.models import ImageHistory
import base64
from pathlib import Path

service = ImageGenerationService()
result = service.generate_image(prompt="test")

# Check if result is a data URI
if result.images[0].startswith('data:image'):
    # Decode and save to file
    header, encoded = result.images[0].split(',', 1)
    image_data = base64.b64decode(encoded)

    # Save to media directory
    file_path = Path(settings.MEDIA_ROOT) / 'generated_images' / 'filename.png'
    with open(file_path, 'wb') as f:
        f.write(image_data)

    # Store relative path
    relative_path = f"generated_images/filename.png"
else:
    # It's a URL, use directly
    relative_path = result.images[0]

# Create database record
image = ImageHistory.objects.create(
    user=user,
    file_path=relative_path,  # ✅ Always a file path, never data URI
    ...
)
```

---

## 📊 Summary

**Root Cause:** Stability AI returns base64 images → `ImageGenerationService` creates data URIs → test script saved data URI directly

**Impact:** 1 image out of 33 (3%) affected - all others use proper file paths

**Resolution:**
- ✅ Image #31 converted to proper file
- ✅ Source identified and documented
- ✅ Production code already handles this correctly
- ✅ Test guidance provided for future development

**Preventive Measures:**
- Document this behavior in developer guides
- Add validation to prevent data URIs in ImageHistory
- Create utility function for data URI → file conversion

---

**This is a known, documented behavior. Production code is safe. Only direct usage of `ImageGenerationService` in test scripts requires special handling.**
