# Platform Capabilities

**Last Updated:** Session 438 (December 13, 2025)

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
| Spiders | 65 | Active (60 working) |
| Clean Agents | 17 | Production |
| **Development Agents** | **4** | **Production (Session 436)** |
| Legacy Agents | 22 | Production |
| Advisors | 25 | Production |
| Sci-Fi Features | 15 | Production |
| Style Presets | 80+ | Built-in |
| Multi-Agent Orchestration | Yes | Production |
| Collective Intelligence Search | Yes | Production |
| **Legal Assistant** | **1** | **Production** |
| **Document Brain** | **1** | **Production** |
| **OCR PDF Support** | **Yes** | **Production** |
| **Document Threading** | **Yes** | **Production (Session 410)** |
| **Response Session UI** | **Yes** | **Production (Session 410)** |
| **Discord Integration** | **33 Commands + Monetization** | **Production (Session 438)** |
| **Discord User Linking** | **Yes** | **Production (Session 429)** |
| **Discord Server Setup** | **3 Templates** | **Production (Session 431)** |
| **Discord Client Management** | **4 Commands** | **Production (Session 432)** |
| **Subscription Tiers** | **Free/Pro/Premium** | **Production (Session 438)** |
| **Stripe Integration** | **Subscription Billing** | **Production (Session 438)** |
| **Training Data Collection** | **14 Datasets** | **Production (Session 420)** |

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

## Clean Agent Architecture (17 Agents)

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
| CompetitorAnalysisAgent | Competitive intelligence | web_search, spider_query, analyze |
| CustomerResearchAgent | Customer personas | web_search, build_persona |
| LegalDocDrafterAgent | Legal document assistance | draft_motion, analyze_motion |
| **CodeGeneratorAgent** | Code generation | generate_code, explain_code |
| **FullStackDeveloperAgent** | Full-stack features | design_feature, implement_* |
| **CodeReviewAgent** | Code review | review_code, check_security |
| **DevOpsAgent** | CI/CD, Docker, K8s | create_dockerfile, create_pipeline |

---

## Development Agents (Session 436)

Four new agents for software development tasks:

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| CodeGeneratorAgent | Generate code from specs | `generate_code`, `explain_code`, `refactor_code` |
| FullStackDeveloperAgent | Build complete features | `design_feature`, `implement_backend`, `implement_frontend` |
| CodeReviewAgent | Review code quality | `review_code`, `check_security`, `check_performance` |
| DevOpsAgent | Infrastructure automation | `create_dockerfile`, `create_pipeline`, `create_k8s_manifests` |

### Supported Languages
Python, JavaScript, TypeScript, Go, Rust, Java, C#, PHP, Ruby

### Supported Platforms
- Docker, Docker Compose
- Kubernetes (deployment, service, ingress)
- GitHub Actions, GitLab CI, Jenkins
- AWS (ECS, EKS), GCP (Cloud Run, GKE)

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

## Discord Integration (Sessions 419-432)

Real-time notifications to Discord when agents are active, plus interactive bot commands. Full Discord-First platform with server setup, client management, and content delivery.

### Discord Channels

| Channel | Purpose | Color |
|---------|---------|-------|
| `#agent-dreams` | Agent dream notifications | Purple |
| `#agent-conversations` | HiveMind sessions + knowledge sharing | Pink/Blue |
| `#system-status` | System health and status updates | Variable |
| `#gallery` | Auto-delivery of created images (Phase 1) | - |
| `#client-*` | Per-client delivery channels (Phase 3) | - |

### Discord Bot Commands (23 Total - Sessions 426-433)

| Command | Description | Phase |
|---------|-------------|-------|
| `/status` | System health check | Core |
| `/agents [limit]` | List active agents with stats | Core |
| `/agent <name>` | Get details for a specific agent | Core |
| `/trending [category]` | Get trending topics from spider data | Core |
| `/spiders` | Spider network stats | Core |
| `/ask <question>` | Ask the Personal Assistant (remembers context!) | Core |
| `/create <prompt>` | Generate an image with AI | Core |
| `/research <topic>` | Search spider data | Core |
| `/clear` | Clear conversation history | Core |
| `/link <code>` | Link Discord to web account | Core |
| `/unlink` | Check link status | Core |
| `/gallery [count]` | View your recent images (#320, #321...) | Phase 1 |
| `/profile` | View your AI Studio profile and stats | Phase 1 |
| `/opportunities [count]` | Browse matching income opportunities | Phase 1 |
| `/setup [template]` | Set up AI Studio channels in your server | Phase 2 |
| `/server-info` | View your server's configuration | Phase 2 |
| `/client-add <name> [email]` | Create client with dedicated channel | Phase 3 |
| `/client-list` | List all your clients with stats | Phase 3 |
| `/client-deliver <client> <id>` | Send deliverable to client (uploads image!) | Phase 3 |
| `/client-invite <client>` | Generate 7-day invite link for client | Phase 3 |
| `/apply <id> [message]` | Apply to an income opportunity | Phase 4 |
| `/track [status]` | Track your job applications | Phase 4 |
| `/help` | Show all commands | Core |

### Discord-First Platform Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 1. Content Delivery | `/gallery`, `/profile`, `/opportunities`, auto-delivery | ✅ Done (Session 430) |
| 2. Server Setup | `/setup`, `/server-info`, 3 templates | ✅ Done (Session 431) |
| 3. Client Management | `/client-add`, `/client-list`, `/client-deliver`, `/client-invite` | ✅ Done (Session 432) |
| 4. Income Pipeline | `/apply`, `/track`, user-friendly opportunity IDs | ✅ Done (Session 433) |
| 5. Full Agent Access | `/agent-task`, `/consult`, `/workflow-run` | ✅ Done (Session 434) |
| 6. Automation | Proactive notifications, daily digests | Pending |

### Server Setup Templates (Phase 2)

| Template | Description | Channels Created |
|----------|-------------|------------------|
| Solo Creator | Personal workspace | #creations, #research, #assistant, #dashboard |
| Freelancer | With client management | + CLIENTS category for per-client channels |
| Agency | Team + clients | + TEAM category with #general, #projects, #resources |

### Client Management (Phase 3)

Freelancers and agencies can manage clients directly via Discord:

1. **Add Client:** `/client-add "Acme Corp" contact@acme.com`
   - Creates `#client-acme-corp` channel
   - Sends welcome message to client

2. **View Clients:** `/client-list`
   - Shows all clients with status, deliverables count, revenue

3. **Send Deliverable:** `/client-deliver "Acme Corp" 320`
   - Uses image ID from `/gallery` (e.g., #320)
   - Uploads image directly to client's channel
   - Tracks delivery in database

4. **Invite Client:** `/client-invite "Acme Corp"`
   - Generates 7-day, single-use invite link

### Discord User Linking (Session 429)

Link your Discord account to your AI Studio web account so images created via `/create` appear in your personal gallery.

**How to Link:**
1. Go to AI Studio → Preferences tab → Discord Integration
2. Click "Generate Link Code" to get a 6-character code (e.g., `ABC123`)
3. In Discord, type `/link ABC123`
4. Account linked! Images now save to your gallery

**API Endpoints:**
- `POST /api/discord/generate-link-code/` - Generate temp code for linking
- `GET /api/discord/status/` - Check if Discord is linked
- `POST /api/discord/unlink/` - Remove Discord link
- `POST /api/discord/verify-link-code/` - Bot calls this to verify & link

### Notification Types

| Type | Channel | Trigger |
|------|---------|---------|
| Agent Dreams | `#agent-dreams` | When agents dream (creative_idea, what_if, prediction, observation) |
| HiveMind Sessions | `#agent-conversations` | When multi-agent conversations complete |
| Knowledge Sharing | `#agent-conversations` | When agents share learned knowledge |
| System Status | `#system-status` | System health updates, spider activity |

### Usage

```python
from core.services.discord_notifications import discord_notify

# Send a dream notification
discord_notify.send_dream(
    agent_name="Research Agent",
    dream_title="Future of AI",
    dream_content="What if AI could dream?",
    dream_type="what_if",
    vividness=0.85
)

# Send a conversation notification
discord_notify.send_conversation(
    participants=["Image Agent", "Video Agent"],
    topic="Content optimization strategies",
    synthesis="Agreed on new approach...",
    mode="brainstorm"
)

# Send a status notification
discord_notify.send_status(
    title="System Online",
    message="All services running",
    status_type="success"  # info, success, warning, error
)

# Test connection to all channels
results = discord_notify.test_connection()
```

### Configuration

Requires `DISCORD_BOT_TOKEN` environment variable. When set, all agent activity automatically posts to Discord.

### Integration Points

- `core/tasks.py` - `generate_agent_dreams()` posts to Discord
- `force_agent_cycle` command - Posts dreams, conversations, knowledge to Discord
- `core/services/discord_notifications.py` - Main notification service
- `core/services/discord_bot.py` - Interactive bot with slash commands
- `core/views_discord.py` - User linking API endpoints

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [AGENTS.md](AGENTS.md) - Agent reference
- [SPIDERS.md](SPIDERS.md) - Spider network
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Sci-fi features
