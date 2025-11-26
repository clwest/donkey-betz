# Session 197: UI Consolidation Plan - Project-Centric Workflow

**Date:** November 25, 2025
**Status:** PLANNING - Awaiting Approval
**Scope:** Major UI Redesign

---

## Executive Summary

Consolidate 10 tabs down to 4 by moving all content creation tools into the Project tab, creating a streamlined workflow where users:
1. **Start** in Assistant (ideation, planning)
2. **Work** in Project (all creation & editing)
3. **Showcase** in Portfolio (curated display)
4. **Govern** in Leadership (AI oversight)

---

## Current State Analysis

### Existing Tabs (10 total)
| Tab | Purpose | Lines of Code | Keep/Remove |
|-----|---------|---------------|-------------|
| Assistant | AI chat, voice commands | ~250 | **KEEP** |
| Images | Image generation & editing | ~1,800 | CONSOLIDATE |
| Characters | Character training | ~200 | CONSOLIDATE |
| Video | Video generation & editing | ~1,100 | CONSOLIDATE |
| Audio | Audio generation | ~300 | CONSOLIDATE |
| Gallery | View all content | ~160 | REMOVE (redundant) |
| Projects | Project management | ~160 | **KEEP & EXPAND** |
| Sessions | AI session history | ~150 | REMOVE (merge into Projects) |
| Portfolio | Curated showcase | ~160 | **KEEP** |
| Leadership | AI governance | ~200 | **KEEP** |

### Features to Consolidate into Project Tab

#### From Images Tab (11 sub-features)
- [ ] Generate (text-to-image)
- [ ] Upload
- [ ] Erase (mask-based removal)
- [ ] Inpaint (mask + prompt replacement)
- [ ] Outpaint (extend boundaries)
- [ ] Recolor
- [ ] Upscale
- [ ] Control (ControlNet)
- [ ] Image Gallery
- [ ] Compare
- [ ] MiniFig (3D generation)

#### From Characters Tab (3 sub-features)
- [ ] Create Character (LoRA training)
- [ ] My Characters (gallery)
- [ ] Character Help

#### From Video Tab (7 sub-features)
- [ ] Text-to-Video
- [ ] Image-to-Video
- [ ] Video-to-Video
- [ ] Upscale Video
- [ ] Character Performance
- [ ] DaVinci Editing (text overlay, color grading, audio mixing, chain)
- [ ] Video Gallery

#### From Audio Tab (5 sub-features)
- [ ] Text-to-Speech
- [ ] Text-to-Sound
- [ ] Voice Dubbing
- [ ] Speech-to-Speech
- [ ] Voice Isolation

---

## Target State Design

### New Tab Structure
```
[Assistant] [Project] [Portfolio] [Leadership]
```

### Project Tab - New Layout

```
+--------------------------------------------------+
| PROJECT: [Project Name]              [< Back to List]
+--------------------------------------------------+
|                                                   |
| [Project Chat/Assistant - Embedded]              |
| Voice & text commands within project context     |
+--------------------------------------------------+
|                                                   |
| QUICK ACTIONS                                     |
| [+ Image] [+ Video] [+ Audio] [+ 3D] [+ Character]|
+--------------------------------------------------+
|                                                   |
| TOOLBOX (Collapsible Sections)                   |
|                                                   |
| > IMAGE TOOLS                                     |
|   [Generate] [Edit] [Upscale] [Remove BG]        |
|   [Erase] [Inpaint] [Outpaint] [Recolor]         |
|   [Control] [Compare]                            |
|                                                   |
| > VIDEO TOOLS                                     |
|   [Text-to-Video] [Image-to-Video] [Extend]      |
|   [Upscale] [Color Grade] [Add Text] [Chain]     |
|   [Trim] [Speed] [Reverse] [Extract Frame]       |
|                                                   |
| > AUDIO TOOLS                                     |
|   [Text-to-Speech] [Sound Effects] [Dubbing]     |
|   [Voice Clone] [Isolation]                      |
|                                                   |
| > 3D TOOLS                                        |
|   [Image-to-3D] [Repair Mesh] [Export STL/GLB]   |
|                                                   |
| > CHARACTER TOOLS                                 |
|   [Train New] [My Characters]                    |
|                                                   |
+--------------------------------------------------+
|                                                   |
| PROJECT ASSETS (with filters)                    |
| [All] [Images] [Videos] [Audio] [3D]             |
|                                                   |
| +--------+ +--------+ +--------+ +--------+      |
| | Img 1  | | Img 2  | | Vid 1  | | Audio1 |      |
| +--------+ +--------+ +--------+ +--------+      |
|                                                   |
+--------------------------------------------------+
|                                                   |
| PROJECT INFO (Collapsible)                       |
| Status | Deadline | Tags | Stats                 |
|                                                   |
+--------------------------------------------------+
```

---

## Implementation Phases

### Phase 1: Project Tab Enhancement (Sessions 197-198)
**Goal:** Add all generation & editing tools to Project tab

#### 1.1 Quick Actions Bar
- Add prominent buttons for common operations
- "Generate Image", "Create Video", "Generate Audio", "Create 3D"
- Each opens inline form or modal within project context

#### 1.2 Toolbox Sections (Collapsible)
- **Image Tools**: Move all image sub-tabs here
- **Video Tools**: Move all video sub-tabs here
- **Audio Tools**: Move all audio sub-tabs here
- **3D Tools**: Move minifig tools here
- **Character Tools**: Move character training here

#### 1.3 Asset Gallery Enhancement
- Unified view of all project assets
- Filter buttons: All | Images | Videos | Audio | 3D
- Same card rendering as current implementation
- Click to expand/edit

### Phase 2: Visual Editing Tools (Session 199)
**Goal:** Add mask-based editing within project

#### 2.1 Image Editor Modal
- Canvas with drawing tools
- Brush size selector
- Operations: Erase, Inpaint, Outpaint
- Preview before applying

#### 2.2 Integration
- Click any image → "Edit" button → Opens editor
- Changes create new image in project
- Original preserved

### Phase 3: Tab Removal & Cleanup (Session 200)
**Goal:** Remove redundant tabs

#### 3.1 Remove Tabs
- Delete Images tab (moved to Project)
- Delete Characters tab (moved to Project)
- Delete Video tab (moved to Project)
- Delete Audio tab (moved to Project)
- Delete Gallery tab (redundant with Project assets + Portfolio)
- Delete Sessions tab (merge into Project history)

#### 3.2 Navigation Update
- Update nav bar to 4 tabs only
- Update any JavaScript that references old tabs
- Update deep links/bookmarks

### Phase 4: Polish & Testing (Session 201)
**Goal:** Ensure everything works smoothly

#### 4.1 Testing
- All generation workflows
- All editing workflows
- Project switching
- Asset display
- Voice commands within project

#### 4.2 UX Polish
- Loading states
- Error handling
- Mobile responsiveness (if applicable)
- Keyboard shortcuts

---

## Technical Approach

### Strategy: Progressive Enhancement
1. **Add** new functionality to Project tab first
2. **Test** everything works within project context
3. **Remove** old tabs only after new implementation verified
4. **Clean up** any orphaned code/CSS

### Key Technical Decisions

#### 1. Inline vs Modal for Tools
- **Inline**: Quick actions (generate, common edits)
- **Modal**: Complex tools (mask editing, character training)

#### 2. State Management
- Current project stored in JavaScript variable
- All API calls include project_id
- Assets auto-refresh after operations

#### 3. Code Reuse
- Existing generation functions work unchanged
- Just need to wire them to new UI locations
- Minimal backend changes required

### Files to Modify
1. `ai_core/templates/ai_image_studio.html` - Primary changes
2. `core/static/js/unified_v2/common.js` - Utility functions
3. `core/static/css/` - Any custom styles

### Files to Create
1. None initially - all changes in existing template

### Files to Delete (Phase 3)
1. None - just remove sections from template

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing functionality | High | Test each feature after moving |
| User confusion during transition | Medium | Keep old tabs until Phase 3 |
| Performance (large template) | Low | Template already large, minimal impact |
| Mobile breakage | Low | Current design not mobile-optimized |

---

## Success Criteria

### Phase 1 Complete When:
- [ ] Can generate images from within Project tab
- [ ] Can generate videos from within Project tab
- [ ] Can generate audio from within Project tab
- [ ] Can create 3D from within Project tab
- [ ] All assets display correctly in project view

### Phase 2 Complete When:
- [ ] Can draw mask on image within project
- [ ] Erase operation works with drawn mask
- [ ] Inpaint operation works with drawn mask + prompt
- [ ] Outpaint operation works

### Phase 3 Complete When:
- [ ] Only 4 tabs remain: Assistant, Project, Portfolio, Leadership
- [ ] No broken links or references to old tabs
- [ ] All features accessible from new locations

### Phase 4 Complete When:
- [ ] All 46+ features verified working
- [ ] Voice commands work within project context
- [ ] No console errors
- [ ] User can complete full workflow without leaving Project tab

---

## Timeline Estimate

| Phase | Sessions | Description |
|-------|----------|-------------|
| Phase 1 | 197-198 | Add all tools to Project tab |
| Phase 2 | 199 | Visual editing (mask tools) |
| Phase 3 | 200 | Remove old tabs |
| Phase 4 | 201 | Polish & testing |

**Total: 4-5 Sessions**

---

## Questions for User Approval

1. **Layout preference**: Collapsible toolbox sections vs. horizontal tool tabs?
2. **Quick actions**: Which operations deserve prominent buttons?
3. **Asset display**: Grid view, list view, or toggle between both?
4. **Priority**: Start with generation tools or editing tools first?

---

## Approval

- [ ] User approves overall approach
- [ ] User approves Phase 1 scope
- [ ] User approves layout design
- [ ] Ready to begin implementation

---

**Document Version:** 1.0
**Created:** Session 197
**Author:** Claude Code + User Collaboration
