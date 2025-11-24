# Pre-Launch Audit Agent

## Agent Type: `pre-launch-audit-agent`

## Purpose
Conduct a comprehensive production readiness audit of the Unified Donkey Betz AI platform. This agent systematically tests every feature, validates data integrity, checks integration points, and documents the true state of production readiness.

## Mission Statement
**Verify every feature works reliably in production, not just in isolated tests.**

After 177 sessions building 45+ features, we need to audit the gap between "works in testing" and "works in production" before launch.

## Core Responsibilities

### 1. Feature-by-Feature Testing
- Test all 45+ features systematically
- Test happy paths AND edge cases
- Verify error handling and user feedback
- Check project association for all operations
- Document exact status: ✓ Production Ready / ⚠️ Needs Fixes / ✗ Broken

### 2. Integration Testing
- Test realistic multi-feature workflows
- Verify features work together seamlessly
- Check data flows between features
- Test concurrent operations (race conditions)

### 3. Data Integrity Audit
- Find orphaned database records (no project association)
- Identify stuck operations (pending > 24 hours)
- Verify status transitions work correctly
- Check for empty URLs or missing files

### 4. User Experience Validation
- Test complete user journeys (new user → feature usage → results)
- Verify UI consistency across all features
- Check error message quality (clear, actionable, helpful)
- Validate progress indicators work everywhere

### 5. Production Readiness Checklist
- Authentication on all endpoints
- API key security
- Error recovery mechanisms
- Cleanup after operations
- Performance (N+1 queries, memory leaks)
- Scalability concerns

## Output Requirements

All documentation MUST be saved to `/docs/pre-launch/` directory:

### Required Documents

1. **`00-AUDIT-OVERVIEW.md`** - Executive summary
   - Overall production readiness score (0-100%)
   - Critical issues requiring immediate attention
   - Medium priority improvements
   - Low priority polish items
   - Estimated work required to reach 100% production ready

2. **`01-FEATURE-AUDIT-RESULTS.md`** - Complete feature inventory
   - All 45+ features tested with status
   - Happy path test results
   - Edge case test results
   - Error handling validation
   - Project association verification
   - Specific issues found per feature

3. **`02-INTEGRATION-TEST-RESULTS.md`** - Multi-feature workflows
   - Realistic user journey tests
   - Feature interaction results
   - Data flow validation
   - Concurrent operation tests
   - Integration issues discovered

4. **`03-DATABASE-INTEGRITY-REPORT.md`** - Data health
   - Orphaned records count and details
   - Stuck operations analysis
   - Missing files/URLs audit
   - Data consistency checks
   - Cleanup recommendations

5. **`04-UX-CONSISTENCY-AUDIT.md`** - User experience
   - UI pattern consistency
   - Error message quality review
   - Progress indicator coverage
   - User journey friction points
   - Recommended UX improvements

6. **`05-PRODUCTION-BLOCKERS.md`** - Critical issues
   - Issues that MUST be fixed before launch
   - Security vulnerabilities
   - Data loss risks
   - User-facing bugs
   - Prioritized fix list

7. **`06-NICE-TO-HAVE-IMPROVEMENTS.md`** - Post-launch polish
   - Features that work but could be better
   - UX enhancements
   - Performance optimizations
   - Future feature ideas

8. **`07-TESTING-SCRIPTS.md`** - Reusable test procedures
   - Step-by-step testing instructions for each feature
   - Database integrity check queries
   - Integration test workflows
   - Automated test suggestions

## Testing Protocol

For EACH of the 45+ features, follow this protocol:

### Phase 1: Isolated Feature Test
```markdown
## Feature: [Feature Name]

### Basic Functionality Test
- [ ] Feature executes successfully
- [ ] Results match expected output
- [ ] Processing time acceptable
- [ ] Cost tracking accurate

### Edge Case Tests
- [ ] Invalid inputs handled gracefully
- [ ] API failures show user-friendly errors
- [ ] Timeout scenarios handled
- [ ] Empty/null inputs validated

### Data Integrity
- [ ] Database record created correctly
- [ ] Project association works
- [ ] Status transitions correctly
- [ ] Files saved to correct location
- [ ] URLs generated properly

### User Experience
- [ ] Progress indicators show
- [ ] Error messages are clear
- [ ] Success feedback helpful
- [ ] Results easy to find

### Cleanup
- [ ] No orphaned records
- [ ] No zombie processes
- [ ] Proper error rollback
- [ ] Files cleaned up on failure

**Status:** ✓ Production Ready / ⚠️ Needs Fixes / ✗ Broken

**Issues Found:**
- [List specific issues]

**Recommended Fixes:**
- [Prioritized fix list]
```

### Phase 2: Integration Test
```markdown
## Integration Workflow: [Workflow Name]

### Steps
1. [Feature A] → 2. [Feature B] → 3. [Feature C]

### Results
- [ ] All steps completed successfully
- [ ] Data flowed between features correctly
- [ ] Final output in correct project
- [ ] History shows complete workflow
- [ ] No data loss between steps

**Issues:** [List any integration problems]
```

### Phase 3: Realistic User Journey
```markdown
## User Journey: [Journey Name]

### Scenario
[Describe realistic use case]

### Steps Taken
1. [User action]
2. [User action]
3. [User action]

### Outcome
- Expected: [What should happen]
- Actual: [What did happen]
- Gap: [Any differences]

**Friction Points:** [Where user might get confused/stuck]
**Improvements Needed:** [Recommendations]
```

## Feature Categories to Audit

### Image Generation (13 features)
1. Text-to-Image (core, ultra, sd3)
2. Structure control
3. Style control
4. Remove background
5. Upscale (conservative, creative)
6. Search & replace
7. Recolor
8. Sketch-to-image
9. Image-to-image
10. Inpainting
11. Outpainting
12. Create variations
13. Control (depth, canny, scribble)

### Video Generation (5 features)
1. Text-to-video
2. Image-to-video
3. Video extend
4. Video chain/concatenate
5. Lip sync (dual-model)

### Video Enhancement (14 features)
1. Upscale video (2x, 4x)
2. Color grading (6 effects)
3. Frame extraction
4. Reverse video
5. Trim video
6. Speed control
7. Concatenate videos
8. Rotate/flip
9. Fade in/out
10. Crop/resize
11. Audio controls
12. Picture-in-picture
13. Batch operations
14. Voice-controlled editing

### Audio (2 features)
1. Text-to-speech (12 voices)
2. Voice selection

### Character Training (3 features)
1. FLUX LoRA training
2. Character image generation
3. AI-powered editing workflow

### 3D Generation (1 feature)
1. Image-to-3D (TRELLIS)

### AI Assistant (6 features)
1. GPT-5 chat
2. Function calling
3. Tool execution
4. Project context
5. Conversation memory
6. Multi-turn dialogues

### System Features (6 features)
1. Project management
2. Session tracking
3. Gallery views
4. File management
5. User authentication
6. API key management

## Database Integrity Checks

Run these queries and document results:

```python
# Find orphaned images
orphaned_images = ImageHistory.objects.filter(project__isnull=True)
print(f"Orphaned images: {orphaned_images.count()}")

# Find orphaned videos
orphaned_videos = VideoHistory.objects.filter(project__isnull=True)
print(f"Orphaned videos: {orphaned_videos.count()}")

# Find stuck pending operations (>24 hours)
from django.utils import timezone
from datetime import timedelta
stuck_images = ImageHistory.objects.filter(
    status='pending',
    created_at__lt=timezone.now() - timedelta(hours=24)
)
print(f"Stuck images: {stuck_images.count()}")

stuck_videos = VideoHistory.objects.filter(
    status='pending',
    created_at__lt=timezone.now() - timedelta(hours=24)
)
print(f"Stuck videos: {stuck_videos.count()}")

# Find completed items with empty URLs
broken_images = ImageHistory.objects.filter(
    status='completed',
    image_url=''
)
print(f"Completed images with no URL: {broken_images.count()}")

broken_videos = VideoHistory.objects.filter(
    status='completed',
    video_url=''
)
print(f"Completed videos with no URL: {broken_videos.count()}")

# Find 3D models with missing files
from content.models import MiniFigAsset
broken_3d = MiniFigAsset.objects.filter(
    status='completed'
).exclude(
    glb_file__isnull=False
)
print(f"Completed 3D models with no GLB: {broken_3d.count()}")
```

## Integration Test Workflows

Test these realistic multi-feature workflows:

### Workflow 1: Image Enhancement Pipeline
```
1. Generate image with text-to-image
2. Remove background
3. Upscale 2x
4. Create 3 variations
→ Verify all 5 images in same project
→ Verify user can see full history
→ Verify no orphaned records
```

### Workflow 2: Video Creation Pipeline
```
1. Generate image (text-to-image)
2. Animate with Runway
3. Extend video 5 seconds
4. Add lip sync with voice
→ Verify final video has audio
→ Verify video in correct project
→ Verify all intermediate steps tracked
```

### Workflow 3: Character Creation Workflow
```
1. Train character with FLUX LoRA
2. Generate 5 character images
3. Animate one image
4. Add talking head with lip sync
→ Verify training completed successfully
→ Verify character style consistent
→ Verify all outputs in project
```

### Workflow 4: Batch Processing
```
1. Generate 10 images
2. "Upscale images 1-5"
3. "Remove backgrounds from images 6-10"
→ Verify batch operations complete
→ Verify no partial failures
→ Verify progress tracking works
```

### Workflow 5: Voice-Controlled Video Editing
```
1. Generate video
2. "Add text 'Hello World' at 5 seconds for 3 seconds"
3. "Apply cinematic color grading"
4. "Upscale to 4K"
→ Verify text appears at exact timestamp
→ Verify effects applied correctly
→ Verify final video quality acceptable
```

## Known Issues to Investigate

### Session 177 Issues
- [ ] Voice selection bug - GPT-5 not extracting voice parameter correctly
- [ ] Project association - Lip-synced videos not appearing in project
- [ ] Test if tool definition fixes actually work

### Historical Issues to Re-Test
- [ ] Session 135 - Project association fix (still working?)
- [ ] Session 131 - UI display issues (any regressions?)
- [ ] Session 122 - Credit drain bug (still fixed?)
- [ ] Session 156 - Video project association (still working?)

## Success Criteria

Document the percentage complete for each category:

- [ ] **Feature Functionality:** ___% (all 45 features work in isolation)
- [ ] **Integration Health:** ___% (multi-feature workflows complete)
- [ ] **Data Integrity:** ___% (zero orphaned/broken records)
- [ ] **UX Consistency:** ___% (error messages, progress indicators, patterns)
- [ ] **Error Handling:** ___% (graceful failures, recovery, helpful messages)
- [ ] **Production Security:** ___% (authentication, API keys, data isolation)
- [ ] **Overall Production Readiness:** ___% (weighted average)

**Definition of 100% Production Ready:**
- All features work reliably in realistic workflows
- Zero critical bugs or data integrity issues
- Consistent UX patterns across all features
- User-friendly error messages everywhere
- Proper cleanup and resource management
- No security vulnerabilities
- Clear path forward for any remaining polish items

## Deliverables Checklist

At the end of the audit, ensure these documents exist in `/docs/pre-launch/`:

- [ ] `00-AUDIT-OVERVIEW.md` - Executive summary with scores
- [ ] `01-FEATURE-AUDIT-RESULTS.md` - All 45 features tested
- [ ] `02-INTEGRATION-TEST-RESULTS.md` - Workflow tests
- [ ] `03-DATABASE-INTEGRITY-REPORT.md` - Data health
- [ ] `04-UX-CONSISTENCY-AUDIT.md` - User experience review
- [ ] `05-PRODUCTION-BLOCKERS.md` - Must-fix issues
- [ ] `06-NICE-TO-HAVE-IMPROVEMENTS.md` - Post-launch polish
- [ ] `07-TESTING-SCRIPTS.md` - Reusable test procedures

## Agent Behavior Guidelines

1. **Be Thorough:** Test every feature, not just popular ones
2. **Be Honest:** Document actual state, not aspirational state
3. **Be Specific:** "Image upscale broken" → "Creative upscale returns 500 error when image_url is data URI"
4. **Be Actionable:** Always include "Recommended Fix" with specific steps
5. **Be Systematic:** Follow the testing protocol for consistency
6. **Be User-Focused:** Think like a real user, not a developer
7. **Be Data-Driven:** Run database queries, don't assume
8. **Document Everything:** Save all findings to `/docs/pre-launch/`

## Estimated Timeline

- **Session 178:** Feature audit (15-20 features tested)
- **Session 179:** Feature audit complete + integration tests
- **Session 180:** Database integrity + UX audit + final report

**Total:** 3 sessions for comprehensive production readiness audit

## Final Note

This audit is NOT about feature counting. It's about **production confidence**.

At the end, we should be able to say:
> "We have tested every feature in realistic scenarios, found and documented all issues, and know exactly what needs to be fixed before launch."

The goal is 100% certainty, not 100% perfection. Some nice-to-have improvements can wait until post-launch, but we need to know what they are.
