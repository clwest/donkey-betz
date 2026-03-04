# Video Upload Guide

## Upload Methods

### 1. Large Upload (Cloudinary Direct) — Recommended
- **Max size:** 10 GB (Cloudinary limit)
- **Path:** Video Studio → Upload tab → "Upload Large Video"
- **Flow:** Browser → Cloudinary directly (no Railway bottleneck)
- **Backend:** `POST /api/upload/cloudinary/sign/` → widget → `POST /api/upload/video/register/`

### 2. Quick Upload (Server-Side)
- **Max size:** 50 MB
- **Path:** Video Studio → Upload tab → "Quick Upload"
- **Flow:** Browser → Django → Cloudinary
- **Backend:** `POST /api/upload/video/`

### 3. Chunked Upload (API only)
- **Max size:** 500 MB
- **Path:** API only (no UI yet)
- **Flow:** Browser → Django (chunks) → Celery assembly → Cloudinary
- **Endpoints:**
  - `POST /api/upload/chunked/init/`
  - `POST /api/upload/chunked/<id>/chunk/`
  - `GET /api/upload/chunked/<id>/status/`

## Compressing Large Videos

Raw screen recordings and ProRes exports can be 10-30+ GB. Compress before uploading.

### ffmpeg (recommended)

**Good quality, much smaller (best for most cases):**
```bash
ffmpeg -i input.mov -c:v libx264 -crf 23 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k output.mp4
```

**Smaller file, faster encode (for quick sharing):**
```bash
ffmpeg -i input.mov -c:v libx264 -crf 28 -preset veryfast -vf "scale=1920:-2" -pix_fmt yuv420p -c:a aac -b:a 128k output_1080p.mp4
```

**Apple Silicon hardware encode (fastest):**
```bash
ffmpeg -i input.mov -c:v h264_videotoolbox -b:v 6000k -maxrate 8000k -bufsize 12000k -c:a aac -b:a 192k output.mp4
```

### Expected compression ratios
| Source Format | Duration | Raw Size | Compressed (CRF 23) |
|--------------|----------|----------|---------------------|
| ProRes 422   | 1 hour   | ~50 GB   | ~2-4 GB            |
| Screen recording (lossless) | 8 min | ~23 GB | ~500 MB - 2 GB |
| OBS recording (high bitrate) | 1 hour | ~15 GB | ~2-3 GB |

### Install ffmpeg (macOS)
```bash
brew install ffmpeg
```

### Check video info before compressing
```bash
ffprobe -hide_banner -i input.mov
```

## For Videos Over 10 GB (After Compression)

If the compressed file is still over 10 GB:
1. **Split into segments:** `ffmpeg -i input.mp4 -c copy -segment_time 3600 -f segment segment_%03d.mp4`
2. **Upload to YouTube (Unlisted):** Use as archive source, then import URL
3. **Extract key clips:** Upload only the 2-5 minute segments you need

## Architecture

```
Browser                    Cloudinary              Django API
  |                           |                       |
  |-- getCloudinarySignature -->                      |
  |<-- {signature, folder} --|                        |
  |                           |                       |
  |-- Upload Widget --------->|                       |
  |   (direct upload)        |                       |
  |<-- {secure_url, etc} ----|                       |
  |                           |                       |
  |-- registerCloudinaryUpload ---------------------->|
  |                           |        VideoHistory.create()
  |<-- {video: {...}} --------------------------------|
```

## Endpoints Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/upload/video/` | POST | Yes | Simple upload (<50 MB) |
| `/api/upload/cloudinary/sign/` | POST | Yes | Get signed Cloudinary params |
| `/api/upload/video/register/` | POST | Yes | Register Cloudinary upload |
| `/api/upload/chunked/init/` | POST | Yes | Init chunked upload |
| `/api/upload/chunked/<id>/chunk/` | POST | Yes | Upload chunk |
| `/api/upload/chunked/<id>/status/` | GET | Yes | Check chunked progress |
| `/api/upload/list/` | GET | Yes | List all uploads |

## Accepted Formats
MP4, MOV, WebM, AVI, MKV (MIME: video/mp4, video/quicktime, video/webm, video/x-msvideo, video/x-matroska)
