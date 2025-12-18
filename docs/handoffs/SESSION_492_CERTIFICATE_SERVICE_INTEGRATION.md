# Session 492: Certificate Service Integration

**Date:** December 18, 2025
**Focus:** Connect CertificateService to image generation flow for PDF ownership certificates

---

## Summary

Connected the CertificateService to the image generation pipeline by implementing automatic provenance tracking. When any image is saved to `ImageHistory`, a `ContentProvenance` record is now automatically created via Django signals. Users can download PDF ownership certificates for any generated image.

---

## The Gap Identified

| Component | Status Before | Status After |
|-----------|---------------|--------------|
| CertificateService | Built (Session 295) | Connected |
| API Endpoint | Built (`/api/provenance/<id>/certificate/download/`) | Connected |
| Frontend UI | Built (Certificate modal + download button) | Connected |
| **Provenance Auto-Creation** | **Missing** | **Added** |

The backend and frontend were fully built but never connected - no provenance records were being created when images were generated.

---

## What Was Done

### 1. Added Django Signal for Auto-Provenance

**Location:** `content/signals.py` (lines 213-293)

```python
@receiver(post_save, sender=ImageHistory)
def create_image_provenance(sender, instance, created, **kwargs):
    """
    Session 492: Auto-create provenance record when an image is saved.
    """
    if not created:
        return  # Only process new images

    # Read image bytes (handles data: URIs and file paths)
    # Call ProvenanceService.create_provenance()
    # Log success/failure
```

### 2. Fixed UUID Incompatibility

**Bug:** `ContentProvenance.image_history_id` was `PositiveBigIntegerField` but `ImageHistory.id` is a UUID.

**Fix:** Changed to `UUIDField` via migration `0111_session_492_certificate_service_uuid_fix.py`

```python
# Before (broken)
image_history_id = models.PositiveBigIntegerField(...)

# After (fixed)
image_history_id = models.UUIDField(...)
```

---

## End-to-End Flow

```
User generates image
       ↓
ImageHistory.objects.create() called
       ↓
Django post_save signal fires
       ↓
create_image_provenance() reads image bytes
       ↓
ProvenanceService.create_provenance() called
       ↓
ContentProvenance record created with:
  - SHA-256 content hash
  - Perceptual hash (pHash)
  - HMAC signature
  - Creator reference
       ↓
User clicks "View Certificate" in Gallery
       ↓
Modal shows provenance details
       ↓
User clicks "Download PDF Certificate"
       ↓
CertificateService generates PDF with:
  - Platform branding
  - Content thumbnail
  - QR code
  - Digital signature
```

---

## Test Results

```
Before: ContentProvenance=0
Created test image: d0745144-5d12-4501-9eee-a61282ffe958
After: ContentProvenance=1

✅ SUCCESS! Provenance auto-created:
   ID: d7da8d47-175f-4f2f-86f8-ddbf03c95a95
   Content Hash: 6b7fa434f92a8b80aab0...
   Creator: mobile_test
   Image History ID: d0745144-5d12-4501-9eee-a61282ffe958
   Matches Image: True

✅ PDF Certificate generated! (12,713 bytes)
```

---

## Files Modified

| File | Changes |
|------|---------|
| `content/signals.py` | +80 lines - Added `create_image_provenance` signal |
| `core/models_unified_system.py` | Changed 3 fields from `PositiveBigIntegerField` to `UUIDField` |
| `core/migrations/0111_session_492_certificate_service_uuid_fix.py` | New migration |

---

## Integration Points

| Component | Location | Status |
|-----------|----------|--------|
| Signal | `content/signals.py:219` | New |
| Service | `core/services/certificate_service.py` | Already built |
| View | `core/views_provenance.py:189` | Already built |
| URL | `/api/provenance/<uuid>/certificate/download/` | Already built |
| Frontend JS | `ai_core/templates/ai_image_studio.html:34195` | Already built |
| Frontend Button | `ai_core/templates/ai_image_studio.html:3614` | Already built |

---

## Testing the Integration

```bash
# 1. Start server
make start

# 2. Generate any image in the UI
# Navigate to http://localhost:8000/ai-studio/
# Create an image (any method)

# 3. View Gallery, click on image
# Click "View Certificate"

# 4. Download PDF
# Click "Download PDF Certificate" button
```

---

## What This Enables

- **Ownership Proof**: Users get cryptographic proof of content creation
- **Licensing Ready**: PDF certificates can be shared for licensing discussions
- **Plagiarism Detection**: Content hash enables similarity checking
- **Derivative Tracking**: Parent relationships tracked for variations

---

## Services Status After Session 492

| Session | Service | Status |
|---------|---------|--------|
| 491 | Agent Intelligence Context | Fixed |
| 491 | Classification Integration | Verified (Session 349) |
| 491 | Gumroad Frontend | Connected |
| **492** | **Certificate Service** | **Connected** |
| 492 | Marketplace Discovery | Pending |

**Services: 66 total, 65 connected** (1 remaining)
