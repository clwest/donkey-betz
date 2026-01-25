# Video Production Workflow

**Category:** Creator
**Last Updated:** January 24, 2026
**Owner:** Creative Director Agent

---

## Overview

This playbook defines the standard workflow for producing video content using the platform's AI-powered tools. It covers everything from ideation to final export.

---

## Prerequisites

- [ ] DaVinci Resolve installed and configured
- [ ] Access to AI Image Studio for thumbnail/asset generation
- [ ] Content strategy approved for video topic
- [ ] Audio recording equipment ready (if voiceover needed)

---

## Workflow Stages

### Stage 1: Pre-Production (1-2 days)

#### 1.1 Topic Research
```
Agent: ResearchAgent
Task: Generate topic brief with:
- Target audience analysis
- Competitive landscape
- Key talking points
- SEO keywords
```

#### 1.2 Script Generation
```
Agent: ContentWriterAgent
Task: Create video script with:
- Hook (first 10 seconds)
- Main content sections
- Call-to-action
- Timestamps for B-roll
```

#### 1.3 Asset Preparation
```
Agent: ImageAgent
Task: Generate:
- Thumbnail options (3 variants)
- Lower thirds graphics
- Intro/outro cards
- B-roll placeholder images
```

### Stage 2: Production (1 day)

#### 2.1 Recording Setup
- Configure recording environment
- Test audio levels
- Set up lighting
- Prepare teleprompter with script

#### 2.2 Recording
- Record main content
- Capture B-roll footage
- Record alternate takes for key sections
- Log good takes with timestamps

### Stage 3: Post-Production (2-3 days)

#### 3.1 Rough Cut
```
Agent: VideoEditingAgent
Tool: DaVinci Resolve
Tasks:
- Import footage
- Sync audio
- Create timeline structure
- Add placeholder graphics
```

#### 3.2 Fine Cut
- Add transitions
- Color correction
- Audio mixing
- Add music/sound effects

#### 3.3 Graphics & Effects
- Insert lower thirds
- Add intro/outro
- Motion graphics
- Text overlays

#### 3.4 Review Cycle
```
Gate: Human Review Required
Checklist:
- [ ] Content accuracy verified
- [ ] Brand guidelines followed
- [ ] Audio levels consistent
- [ ] No copyright issues
- [ ] Captions accurate
```

### Stage 4: Distribution (1 day)

#### 4.1 Export
- Export master file (4K ProRes)
- Export platform-specific versions:
  - YouTube (1080p H.264)
  - TikTok (1080x1920 vertical)
  - Instagram (1080x1080 square)

#### 4.2 Upload & Optimize
```
Agent: SocialMediaAgent
Tasks:
- Upload to platforms
- Set metadata (title, description, tags)
- Schedule publish time
- Create social posts
```

---

## Quality Checklist

### Technical Quality
- [ ] Resolution: 1080p minimum
- [ ] Frame rate: 24/30/60fps consistent
- [ ] Audio: -14 LUFS integrated loudness
- [ ] Color: Rec. 709 color space
- [ ] Export: H.264/H.265 codec

### Content Quality
- [ ] Hook captures attention in first 5 seconds
- [ ] Content matches title/thumbnail promise
- [ ] Clear call-to-action included
- [ ] No dead air or awkward pauses
- [ ] Pacing maintains engagement

### Platform Compliance
- [ ] YouTube: No copyright strikes risk
- [ ] TikTok: Under 3 minutes for reach
- [ ] Instagram: Caption-ready (many watch muted)

---

## Agents Involved

| Agent | Role | Stage |
|-------|------|-------|
| ResearchAgent | Topic research | Pre-Production |
| ContentWriterAgent | Script creation | Pre-Production |
| ImageAgent | Thumbnail/graphics | Pre-Production |
| VideoEditingAgent | Editing | Post-Production |
| SocialMediaAgent | Distribution | Distribution |

---

## Templates & Assets

- Script template: `docs/templates/video_script.md`
- Thumbnail PSD: `assets/templates/thumbnail.psd`
- Lower thirds: `assets/motion/lower_thirds.drp`
- Intro sequence: `assets/motion/intro_v3.drp`

---

## Metrics & KPIs

Track these after publish:
- View count (24h, 7d, 30d)
- Watch time / retention rate
- Click-through rate (CTR)
- Engagement rate (likes/comments/shares)
- Subscriber conversion

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-24 | 1.0 | Initial playbook |
