# Platform Capabilities

**Last Updated:** Session 409 (December 10, 2025)

---

## Quick Reference

| Category | Count | Status |
|----------|-------|--------|
| Image Generation Features | 13 | Production |
| Video Generation Features | 5 | Production |
| Audio Generation Features | 2 | Production |
| Video Editing Operations | 14 | Production |
| 3D Generation | Complete | Production |
| Character Training | 3 | Production |
| Workflows | 6 | Production |
| Spiders | 64 | Active (59 working) |
| Clean Agents | 13 | Production |
| Legacy Agents | 22 | Production |
| Advisors | 25 | Production |
| Sci-Fi Features | 15 | Production |
| Style Presets | 80+ | Built-in |
| Multi-Agent Orchestration | Yes | Production |
| Collective Intelligence Search | Yes | Production |
| **Legal Assistant** | **1** | **Production (Session 409)** |
| **Document Brain** | **1** | **Production (Session 409)** |
| **OCR PDF Support** | **Yes** | **Production (Session 409)** |

---

## Image Generation (Stability AI)

### Generation Modes

| Mode | Resolution | Best For |
|------|------------|----------|
| Core | 1024x1024 | Fast drafts |
| SDXL | 1024x1024 | High quality |
| SD3 | 1024x1024 | Latest quality |
| Ultra | 1024x1024 | Maximum quality |

### Editing Operations

| Operation | Description |
|-----------|-------------|
| Upscale | 4x resolution increase |
| Remove Background | Transparent PNG output |
| Search & Replace | Replace objects in image |
| Search & Recolor | Change object colors |
| Outpaint | Extend image boundaries |
| Inpaint | Edit specific regions |
| Erase Object | Remove objects seamlessly |
| Create Variations | Generate similar images |
| Style Transfer | Apply artistic styles |
| Sketch to Image | Convert sketches |
| Structure Control | Maintain composition |
| Control Sketch | Detailed sketch control |
| 3D Character | Generate 3D-style characters |

---

## Video Generation (Runway ML)

| Feature | Description |
|---------|-------------|
| Text-to-Video | Generate video from text prompt |
| Image-to-Video | Animate still images |
| Video Extension | Extend existing videos |
| Lip Sync | Sync video to audio |
| Video Chaining | Concatenate multiple clips |

### Supported Resolutions
- 1280x720 (720p)
- 1920x1080 (1080p)

### Duration Options
- 5 seconds
- 10 seconds
- Extended via chaining

---

## Audio Generation (ElevenLabs)

| Feature | Description |
|---------|-------------|
| Text-to-Speech | Multiple voice options |
| Voiceover | Add narration to video |

### Voice Options
- 10+ built-in voices
- Custom voice training (coming)

---

## Video Editing

| Operation | Description |
|-----------|-------------|
| Trim | Cut video start/end |
| Crop | Change frame dimensions |
| Add Text | Overlay text/titles |
| Add Effects | Visual effects |
| Color Grading | Adjust colors |
| Speed Change | Slow-mo/fast-forward |
| Concatenate | Join multiple videos |
| Extract Frame | Get still from video |
| Add Audio | Overlay audio track |
| Add Voiceover | TTS voiceover |
| Auto-Caption | Generate subtitles |
| ProRes Render | Professional output |
| DNxHD Render | Broadcast quality |
| GIF Export | Animated GIF output |

---

## 3D Generation (Replicate)

| Feature | Description |
|---------|-------------|
| Image-to-3D | Convert 2D image to 3D model |
| 3D Scene | Generate complete scenes |

### Output Formats
- GLB
- OBJ
- GLTF

---

## Character Training (LoRA)

| Feature | Description |
|---------|-------------|
| Train Character | Create custom LoRA |
| Generate with LoRA | Use trained character |
| Style Consistency | Maintain character across images |

### Training Requirements
- 10-20 reference images
- ~30 minute training time

---

## Built-in Style Presets (80+)

### Animation Styles
```
pixar, disney, dreamworks, south_park, simpsons, family_guy,
ghibli, anime, manga, looney_tunes, rick_and_morty, archer,
adventure_time, gravity_falls, bojack, cartoon, chibi
```

### Art Styles
```
watercolor, oil_painting, pencil, charcoal, pastel,
impressionist, surreal, cubist, pop_art, art_deco,
minimalist, abstract, geometric, vintage, retro
```

### Genre Styles
```
cyberpunk, steampunk, fantasy, scifi, gothic, horror,
noir, western, medieval, futuristic, post_apocalyptic
```

### Photography Styles
```
portrait, landscape, macro, street, product,
fashion, food, architecture, nature, studio
```

**Usage:** Just mention the style name - "Create a cyberpunk cityscape"

---

## Workflows (Multi-Step)

| Workflow | Steps |
|----------|-------|
| `research_and_create_logos` | Research trends + Generate logos (1024x1024) |
| `youtube_thumbnail_package` | Research + Thumbnails (1280x720) |
| `brand_identity_package` | Research + Full brand kit |
| `product_photography_kit` | Research + Product photos |
| `video_thumbnail_series` | Consistent thumbnail series |
| `logo_to_video` | Animate logo into video |

---

## Spider Network (70 Spiders)

### Data Sources by Category

| Category | Count | Real Sources |
|----------|-------|--------------|
| Tech News | 9 | HackerNews, TechCrunch, DevTo, Wired, MIT Tech Review, Axios, The Verge |
| Financial | 8 | CoinGecko API, Yahoo Finance API, SeekingAlpha |
| Jobs | 7 | RemoteOK (JSON), WeWorkRemotely (RSS), Adzuna API, FlexJobs |
| Creative | 5 | Dribbble, Behance, Unsplash API, ProductHunt |
| AI Tools | 4 | HuggingFace, Midjourney, Civitai, RunwayML |
| Digital Products | 5 | Gumroad, Etsy, LemonSqueezy, AppSumo, Sellfy |
| Content | 3 | Medium, Substack, Patreon |
| Education | 3 | Teachable, Udemy, Skillshare |
| Legal | 4 | CourtListener, Justia, FindLaw, LII |
| Community | 1 | Reddit (20+ subreddits) |
| + 10 more... | | |

### Topic Filters

Filter spider results by topic:
- `ai` - AI/ML, machine learning, neural networks
- `web` - Web development, JavaScript, React, CSS
- `security` - Cybersecurity, encryption, privacy
- `cloud` - AWS, Azure, Kubernetes, DevOps
- `design` - UI/UX, graphic design, typography

---

## Clean Agent Architecture (9 Agents)

| Agent | Purpose | Isolated Tools |
|-------|---------|----------------|
| PersonalAssistantAgent | Routes requests | delegate_to_agent |
| ImageAgent | Image generation | generate_image |
| VideoAgent | Video generation | generate_video, animate_image |
| AudioAgent | Audio generation | generate_voice, generate_sfx |
| ThreeDAgent | 3D generation | convert_to_3d |
| ImageEditingAgent | Image editing | upscale, remove_bg, etc. |
| VideoEditingAgent | Video editing | trim, add_text, etc. |
| ResearchAgent | Web + spider search | web_search, spider_query |
| WorkflowAgent | Multi-step orchestration | delegate_to_agent |

---

## 15 Sci-Fi Features

| Feature | Purpose |
|---------|---------|
| Agent Learning | Agents learn from each other |
| Agent Conversations | Real-time AI-to-AI chat |
| Agent Dreams | Creative thoughts when idle |
| Hive Mind Mode | Collective intelligence |
| Memory Palace | Persistent agent memory |
| Mood System | Emotional states affect behavior |
| Rivalries/Alliances | Agent relationships |
| Evolution System | XP, levels, progression |
| Time Travel Debug | Replay agent decisions |
| Personality Profiles | Distinct agent personalities |
| Memory Clusters | Grouped related memories |
| Prophecies | Agent predictions |
| Time Capsules | Messages to future selves |
| Conversation Contract | Quality scoring |
| Spider Integration | Real-time data feed |

---

## API Access

All capabilities accessible via REST API:

```bash
# Main chat endpoint (Clean Architecture)
POST /api/super-platform/process/
{"message": "Create a cyberpunk logo"}

# System status
GET /api/super-platform/status/

# Image generation
POST /api/generate/image/

# Video generation
POST /api/generate/video/

# Spider data
GET /api/spiders/trending/
GET /api/spiders/search/?q=AI

# Document ingestion (Session 402)
GET /api/documents/
POST /api/documents/ingest-url/
GET /api/documents/<uuid>/
DELETE /api/documents/<uuid>/delete/
```

---

## Document Ingestion & RAG (Session 402)

Build your knowledge base by ingesting documents from multiple sources.

### Supported Sources

| Source | Method | Features |
|--------|--------|----------|
| YouTube Videos | URL paste | Transcript extraction with timestamps |
| Web Pages | URL paste | Playwright-powered JS rendering |
| PDF Documents | File upload | Text extraction |
| Text/Markdown | File upload | Direct processing |

### Processing Pipeline

1. **URL Detection** - Automatically detects YouTube vs web pages
2. **Content Extraction** - Uses requests (fast) or Playwright (JS-rendered)
3. **Text Processing** - Cleans HTML, extracts main content
4. **Embedding Generation** - Creates vector embeddings for RAG search

### Playwright Integration

For JavaScript-rendered SPAs:
- Automatically falls back to Playwright when content is insufficient
- Launches headless Chromium browser
- Waits for network idle + JS rendering
- Attempts to dismiss cookie banners
- Extracts fully rendered content

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/` | GET | List all documents with stats |
| `/api/documents/ingest-url/` | POST | Ingest YouTube or web page |
| `/api/documents/<id>/` | GET | Get document with full content |
| `/api/documents/<id>/delete/` | DELETE | Delete document and embeddings |

### UI Location

Intelligence Tab → Documents sub-tab

---

## Pro Se Legal Assistant (Session 403, Enhanced 404F + Patch 4C)

AI-powered legal document assistant for Colorado family law self-represented litigants.

### Features

| Feature | Description |
|---------|-------------|
| Legal Guidance | General legal information for Colorado family law |
| Motion Templates | Generate motion templates (continuance, modify parenting time, etc.) |
| Meet-and-Confer Emails | Professional correspondence templates |
| Declaration Templates | Sworn statement templates |
| Procedure Explanations | Step-by-step guides for common procedures |
| JDF Form Reference | Colorado Judicial Department form information |
| **Case File Upload** | Upload PDFs, DOC, TXT for AI analysis |
| **Document Analysis** | AI identifies issues and recommends corrections |
| **Corrective Filing Generation** | Generate properly formatted refilings |
| **Motion Rewriter (404)** | Transform denied motion into correct JDF format |
| **Non-Party Detection (404)** | Warn when relief sought against non-parties |
| **Evidence Checklist (404)** | Motion-type specific exhibit requirements |
| **Statutory Alignment (404)** | Map facts to criteria categories (no statute citations) |
| **County/State Inference (404F)** | Auto-detects jurisdiction from court address |
| **Incident Normalization (Patch 4C)** | Clean numbered allegations from messy PDF text |

### Session 404 Motion Rewriting Tools

| Tool | Purpose |
|------|---------|
| `analyze_denied_motion` | Identify all deficiencies in denied motion |
| `rewrite_motion` | Generate corrected motion with affidavit + proposed order |
| `generate_evidence_checklist` | Create motion-type specific exhibit checklist |
| `check_non_party_issues` | Detect/correct non-party relief requests |

### Session 404F - County/State Inference

When a court address is extracted but county/state fields are blank, the system now:
- Parses city name from address (e.g., "Fort Collins, CO 80521")
- Maps Colorado cities to counties (Fort Collins → LARIMER)
- Expands state abbreviations (CO → COLORADO)

### Session 404 Patch 4C - Incident & Enumeration Normalization

Completely rewrote fact extraction for court-ready output:

| Problem | Solution |
|---------|----------|
| Inline semicolon lists ("1. Today...; 2. Aug 29...") | Split into separate numbered allegations |
| Raw PDF numbering fragments ("1." "2.") | Filtered out, only complete sentences kept |
| Subheadings in facts ("Today's Incident –") | Stripped from output |
| Missing impact summary | Allegation 4 auto-generated from petitioner's language |
| Content verification | PART 5: Full Restatement with 1:1 mapping log |

**Output Format (Patch 4C):**
```
SPECIFIC FACTUAL ALLEGATIONS:
1. On [DATE], [INCIDENT DESCRIPTION].
2. On [DATE], [INCIDENT DESCRIPTION].
3. On [DATE], [INCIDENT DESCRIPTION].
4. [IMPACT PARAGRAPH - pattern/harm summary using petitioner's language]
```

### JDF Form Mapping

| Relief Type | Primary Form |
|-------------|--------------|
| Emergency Parenting | Motion and Affidavit for Emergency Orders |
| Restrict Parenting | JDF 1220 (Motion to Modify) |
| Modify Parenting Time | JDF 1220 + JDF 1221 (Affidavit) |
| Enforce Order | Motion for Citation for Contempt |
| Modify Child Support | JDF 1820 or JDF 1821 |

### Document Types Supported

| Type | Use Case |
|------|----------|
| Court Order / Ruling | Analyze orders and understand requirements |
| Denied Motion | Understand why motion was denied, get correction guidance |
| Filed Motion | Review filed motions |
| Correspondence | Opposing party communications |
| Opposing Filing | Analyze other party's filings |
| Financial Document | Support worksheets, disclosures |
| Evidence / Exhibit | Supporting documents |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/legal/case-files/` | GET | List uploaded legal documents |
| `/api/legal/case-files/upload/` | POST | Upload and process document |
| `/api/legal/case-files/<id>/` | GET | Get document details |
| `/api/legal/case-files/<id>/analyze/` | POST | AI-powered document analysis |
| `/api/legal/case-files/<id>/delete/` | DELETE | Delete document |

### UI Location

Legal Assistant Tab → My Case Files sub-tab

### Important Notes

- Provides **general legal information only**, NOT legal advice
- Does NOT create an attorney-client relationship
- Users should consult a licensed Colorado attorney
- Generated documents are **templates** requiring review
- Court-ready output contains NO AI disclaimers (Session 404E removed them)

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [AGENTS.md](AGENTS.md) - Agent reference
- [SPIDERS.md](SPIDERS.md) - Spider network
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Sci-fi features
