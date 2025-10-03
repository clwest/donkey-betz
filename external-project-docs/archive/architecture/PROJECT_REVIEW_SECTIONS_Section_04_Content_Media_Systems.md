# Section 4: Content & Media Systems
**Agent Name: Content Platform Analyst**

## Scope Overview
This section analyzes the comprehensive content creation and media generation systems that power creative output across the platform.

### Primary Directories:
- `backend/content/` - Content management system
- `backend/media_studio/` - Media generation and processing
- `backend/vision/` - Image and visual processing
- `backend/voice_journals/` - Audio processing and transcription
- `backend/api/content_creation/` - Content API layer

## Analysis Instructions for Claude Code Agent

### 1. Content Management Architecture
**Investigate:**
- `backend/content/models/` - Content, Article, Blog models
- `backend/content/services/content_service.py` - Content operations
- `backend/content/services/content_generator.py` - AI content generation

**Key Questions:**
- What content types are supported?
- How is content versioned?
- What is the publishing workflow?
- How is content metadata managed?

### 2. Image Generation Systems
**Investigate:**
- `backend/media_studio/services/dalle_service.py` - DALL-E integration
- `backend/media_studio/services/stable_diffusion_service.py` - Stable Diffusion
- `backend/media_studio/services/image_processor.py` - Image processing
- `backend/content/services/visual_styles/` - Style system

**Key Questions:**
- How are image prompts constructed?
- What are the 32 visual styles?
- How is style selection handled?
- What are the image generation limits?

### 3. Video Generation Pipeline
**Investigate:**
- `backend/media_studio/services/video_generator.py` - Video generation
- `backend/media_studio/services/animation_service.py` - Animation logic
- `backend/media_studio/models/video_project.py` - Video project model

**Key Questions:**
- What video generation methods exist?
- How are video timelines managed?
- What formats are supported?
- How is rendering handled?

### 4. Audio Processing
**Investigate:**
- `backend/voice_journals/services/transcription_service.py` - Speech-to-text
- `backend/voice_journals/services/audio_processor.py` - Audio processing
- `backend/media_studio/services/tts_service.py` - Text-to-speech

**Key Questions:**
- Which transcription services are used?
- How is audio quality enhanced?
- What audio formats are supported?
- How are voice profiles managed?

### 5. Document Generation
**Investigate:**
- `backend/content/services/pdf_generator.py` - PDF creation
- `backend/content/services/document_formatter.py` - Document formatting
- `backend/universal_builder/services/` - Code/document generation

**Key Questions:**
- How are PDFs generated?
- What templates are available?
- How is formatting controlled?
- What export formats exist?

### 6. Style Management System
**Investigate:**
- `backend/content/services/visual_styles/prompt_helpers.py` - Style definitions
- `backend/content/services/visual_styles/style_mapper.py` - Style mapping
- `backend/content/services/visual_styles/prompt_categories.py` - Categories

**Key Questions:**
- What are all 32 visual styles?
- How are styles categorized?
- How do styles modify prompts?
- What negative prompts are used?

### 7. Media Storage & CDN
**Investigate:**
- `backend/media_studio/services/storage_service.py` - Media storage
- `backend/media_studio/services/cdn_service.py` - CDN integration
- `backend/media_studio/models/media_asset.py` - Asset tracking

**Key Questions:**
- Where are media files stored?
- How is CDN distribution handled?
- What are the storage limits?
- How is media optimized?

### 8. Content Moderation
**Investigate:**
- `backend/content/services/moderation_service.py` - Content moderation
- `backend/content/services/safety_filter.py` - Safety filtering
- `backend/content/utils/content_policy.py` - Policy enforcement

**Key Questions:**
- What content is filtered?
- How are violations handled?
- What moderation APIs are used?
- How are appeals processed?

### 9. Integration with AI Agents
**Investigate:**
- `backend/agent_orchestra/agents/content_creation_agent.py` - Content agent
- `backend/content/services/agent_content_service.py` - Agent integration
- `backend/content/api/agent_endpoints.py` - Agent APIs

**Key Questions:**
- How do agents create content?
- What content can agents generate?
- How is quality controlled?
- What are the agent limits?

### 10. Performance & Optimization
**Investigate:**
- `backend/media_studio/services/queue_service.py` - Job queuing
- `backend/media_studio/services/cache_service.py` - Media caching
- `backend/content/tasks.py` - Celery tasks

**Key Questions:**
- How are generation jobs queued?
- What caching strategies exist?
- How is load balanced?
- What are the timeouts?

## Critical Files to Review
1. `backend/media_studio/services/stable_diffusion_service.py` - SD integration
2. `backend/content/services/visual_styles/prompt_helpers.py` - All 32 styles
3. `backend/media_studio/services/dalle_service.py` - DALL-E integration
4. `backend/content/services/content_generator.py` - AI content creation
5. `backend/media_studio/tasks.py` - Async media generation

## Visual Styles Inventory
Verify all 32 styles from magical_mountains project:
1. Photorealistic
2. Cinematic
3. Digital Art
4. Oil Painting
5. Watercolor
6. Pencil Sketch
7. Anime/Manga
8. Studio Ghibli
9. Pixar 3D
10. Cyberpunk
11. Steampunk
12. Gothic
13. Minimalist
14. Abstract
15. Surreal
16. Fantasy Art
17. Sci-Fi Concept
18. Comic Book
19. Low Poly 3D
20. Vaporwave
21. Dark Academia
22. Cottagecore
23. Film Noir
24. Retro 80s
25. Art Nouveau
26. Bauhaus
27. Memphis Design
28. Swiss Design
29. Brutalist
30. Psychedelic
31. Children's Book
32. Technical Diagram

## Expected Outputs from Analysis
1. Complete content pipeline diagram
2. Media generation workflow
3. Style system documentation
4. Performance metrics
5. Storage architecture
6. Integration patterns
7. Content moderation report
8. API endpoint inventory

## Special Considerations
- The style normalization fix (kebab-case to Title Case)
- DALL-E vs Stable Diffusion selection logic
- Token costs for AI generation
- Storage costs for media files
- Copyright and licensing for generated content
- Content moderation false positives
- Generation queue bottlenecks
- The "magical mountains" style system origin