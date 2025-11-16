# 🏆 Golden Paths v1 - Demo-Ready User Flows

**Date:** November 15, 2025
**Session:** 110 - Golden Path Demo & Launch Polish
**Purpose:** Define the 2-3 official "demo-ready" flows that showcase the platform's unique value

---

## 🎯 What Are Golden Paths?

**Golden Paths** are carefully crafted user journeys that:
- **Showcase core platform capabilities** in 5-10 minutes
- **Work reliably** end-to-end without errors
- **Tell a compelling story** to potential users, investors, or stakeholders
- **Feel magical** - demonstrating human-AI co-leadership and automation

---

## 🌟 Golden Path #1: Strategic Decision Loop

**Tagline:** "AI-Human Co-Leadership: Collaborative Decision-Making with Outcome Tracking"

**Value Proposition:**
Show how the platform enables **equal collaboration** between AI agents and humans for strategic decisions, with full accountability and "I told you so" tracking that helps both sides learn.

### Entry Point
**Donkey Cockpit → Leadership & Co-Leadership Card**
- Button: "Start Boardroom Meeting"

### Step-by-Step Flow

#### Step 1: Initiate Decision (BoardroomFormScreen)
**User Action:**
1. Tap "Start Boardroom Meeting" from Donkey Cockpit
2. Enter topic: "Q1 2026 AI Feature Roadmap"
3. (Optional) Select project context
4. Tap "Submit"

**System Response:**
- Creates `CoLeadershipDecision` record
- Triggers `MeetingCoordinatorAgent` to consult CTO, COO, Product Manager agents
- Collects `AgentRecommendation` records (support/concern/objection/alternative)
- Navigates to Leadership Cockpit or Decisions List

**Demo Highlight:**
> "Watch as our AI executive team - CTO, COO, and Product Manager - each provide their strategic perspective in real-time."

#### Step 2: Review AI Recommendations (DecisionDetailScreen)
**User Action:**
1. From Leadership Cockpit or Decisions List, tap the decision
2. Review recommendations from each agent:
   - **CTO** (stance: support, confidence: 0.85)
   - **COO** (stance: concern, confidence: 0.70)
   - **Product Manager** (stance: alternative, confidence: 0.90)

**System Response:**
- Displays all agent recommendations with:
  - Stance badges (color-coded)
  - Summary text
  - Full recommendation text
  - Risk analysis
  - Alternative paths
  - Confidence levels

**Demo Highlight:**
> "Each AI agent brings domain expertise - technical feasibility, operational concerns, product-market fit - just like a real executive team."

#### Step 3: Human Decision (DecisionCommitScreen)
**User Action:**
1. Tap "Commit Decision"
2. Choose path:
   - Option A: Follow CTO's recommendation (build full automation)
   - Option B: Follow Product Manager's alternative (MVP first)
   - Option C: Custom path (hybrid approach)
3. Enter justification: "Product Manager's MVP-first approach reduces risk while validating market fit"
4. Tap "Commit"

**System Response:**
- Creates `HumanDecision` record
- Marks `is_override = True` (if human chose different path than consensus)
- Sets `decision.frozen_at` timestamp
- Updates decision status to "pending_outcome"

**Demo Highlight:**
> "The human is ALWAYS the final decision-maker. AI provides expert input, but you choose the path."

#### Step 4: Log Outcome (DecisionDetailScreen - Later)
**User Action:** (Simulated for demo or real after 1 week)
1. Return to decision detail
2. Tap "Log Outcome"
3. Enter:
   - Status: "Success"
   - Summary: "MVP validated market fit, signed 5 beta customers"
   - Metrics: `{"revenue": 50000, "customers": 5}`
   - Attribution: "Product Manager more correct" (human followed PM's advice)
4. Tap "Submit"

**System Response:**
- Creates `DecisionOutcome` record
- Calculates attribution (AI vs Human correctness)
- Generates reflection (if user preferences allow "I told you so")
- Updates leadership stats

**Demo Highlight:**
> "The platform tracks outcomes and learns who tends to be right - AI or human - for different types of decisions. This builds trust and improves collaboration over time."

#### Step 5: View Reflection & Stats (LeadershipDashboard)
**User Action:**
1. Navigate back to Leadership Cockpit
2. View updated stats:
   - Total Decisions: 5 → 6
   - Override Rate: 40% (human overrode AI 2 out of 5 times)
   - Success Rate: 83% (5/6 decisions had successful outcomes)
   - AI Correctness: 60% (3/5 completed decisions)
   - Human Correctness: 80% (4/5 completed decisions)

**System Response:**
- Displays aggregate performance metrics
- Shows trend charts (if enough data)
- Optionally shows playful "I told you so" message if enabled:
  > "🎯 The Product Manager's intuition paid off again! That's 3 wins in a row for the AI product team. Maybe we should listen more? 😉"

**Demo Highlight:**
> "Over time, both AI and humans learn from each other. The platform quantifies who tends to be right in different contexts, building mutual trust."

### Expected Outputs

**Screens Visited:**
1. Donkey Cockpit
2. BoardroomFormScreen
3. DecisionDetailScreen (recommendations view)
4. DecisionCommitScreen
5. DecisionDetailScreen (outcome view)
6. LeadershipDashboard

**Data Created:**
- 1 CoLeadershipDecision
- 3 AgentRecommendations (CTO, COO, PM)
- 1 HumanDecision
- 1 DecisionOutcome

**Demo Duration:** 4-6 minutes

### Success Criteria

✅ All agent recommendations load within 5 seconds
✅ Decision commits without errors
✅ Outcome logging works smoothly
✅ Stats update in real-time
✅ No confusing error messages or broken navigation
✅ User feels like they're collaborating with AI peers, not tools

---

## 🎨 Golden Path #2: Idea to Publish-Ready Assets

**Tagline:** "One-Tap Creative Workflows: From Concept to Professional Content"

**Value Proposition:**
Show how the platform **automates complex multi-step creative workflows** that would normally take hours of manual work across multiple tools.

### Entry Point
**Donkey Cockpit → Creative Pipelines Card** ⚠️ **NEEDS TO BE ADDED**
- Button: "Idea → Image Set" (shortcut)
- Button: "Idea → Promo Video" (shortcut)
- Button: "View All Pipelines" → PipelinesScreen

### Step-by-Step Flow

#### Step 1: Choose Template (PipelinesScreen)
**User Action:**
1. From Donkey Cockpit, tap "Idea → Image Set" shortcut
   OR
   Tap "Creative Pipelines" → Templates tab → Select "Idea to Image Set"

**System Response:**
- Displays template info:
  - **Name:** Idea to Image Set
  - **Description:** Transform a creative idea into 3-5 AI-generated images
  - **Steps:** 3 (GPT Expansion → Image Generation → Save Assets)
  - **Inputs:** idea (required), num_images (optional, default: 5)
  - **Outputs:** images array with URLs

**Demo Highlight:**
> "Each pipeline is a reusable workflow recipe. This one takes a simple idea and produces professional AI-generated images, ready to use."

#### Step 2: Launch Pipeline (LaunchPipelineDialog)
**User Action:**
1. View dynamic form with inputs:
   - **Idea:** "A futuristic co-working space where humans and AI robots collaborate at desks"
   - **Number of Images:** 3
2. (Optional) Select project context
3. Tap "Launch Pipeline"

**System Response:**
- Creates `CreativePipelineRun` (status: pending)
- Dispatches Celery task for async execution
- Navigates to PipelineRunDetailScreen
- Returns run ID immediately (API responds in <500ms)

**Demo Highlight:**
> "Notice how fast that was? The pipeline starts immediately and runs in the background. No waiting around."

#### Step 3: Watch Live Progress (PipelineRunDetailScreen)
**User Action:**
1. Observe live polling (every 3 seconds)
2. Watch status card update:
   - **Status:** Pending → Running
   - **Current Step:** 1 of 3 → 2 of 3 → 3 of 3
   - **Progress Bar:** 0% → 33% → 66% → 100%
   - **Step Tracker:**
     - ✅ Step 1: GPT Expansion (GPT-4o expanded idea into 3 detailed prompts)
     - ✅ Step 2: Image Generation (Stability AI generating images...)
     - 🔄 Step 3: Save Assets (Storing in ImageHistory...)

**System Response:**
- Backend orchestrator (`pipelines/services.py`) executes:
  1. `execute_gpt_expansion_step()`: Calls OpenAI GPT-4o to create N detailed prompts
  2. `execute_image_generation_step()`: Calls Stability AI for each prompt
  3. `execute_save_assets_step()`: Stores in ImageHistory + links to AISession
- Updates `current_step`, `progress_percentage`, and `log` field after each step
- Sets `status = completed` when done

**Demo Highlight:**
> "Behind the scenes, the pipeline is coordinating multiple AI services - GPT-4o for creative expansion, Stability AI for image generation, and our database for asset management."

#### Step 4: View Outputs (PipelineRunDetailScreen - Outputs Card)
**User Action:**
1. When status shows "Complete", scroll to Outputs card
2. View generated content:
   - **Images:** 3 images displayed in horizontal scroll grid
   - **Expanded Prompts:**
     1. "A modern co-working space bathed in natural light, with sleek desks where a female professional works alongside a friendly humanoid AI robot..."
     2. "Close-up shot of a human hand and robotic hand collaborating on a digital tablet screen..."
     3. "Wide-angle view of a futuristic open-plan office with glass walls..."
3. Tap any image to view full-screen
4. Long-press to save or share

**System Response:**
- Displays all outputs from `output_payload` JSON field
- Images load from Stability AI URLs (or S3 if saved)
- Prompts shown as expandable list

**Demo Highlight:**
> "In just 45 seconds, we went from a simple idea to 3 professional, prompt-engineered, AI-generated images. This would normally take 30+ minutes of manual work."

#### Step 5: Review Execution Log (PipelineRunDetailScreen - Log Card)
**User Action:**
1. Tap "Execution Log" to expand
2. Review timestamped log:
   ```
   [2025-11-15 14:32:01] Pipeline started
   [2025-11-15 14:32:02] Step 1/3: GPT Expansion
   [2025-11-15 14:32:05] Generated 3 detailed prompts
   [2025-11-15 14:32:05] Step 2/3: Image Generation
   [2025-11-15 14:32:35] Generated image 1/3
   [2025-11-15 14:32:42] Generated image 2/3
   [2025-11-15 14:32:48] Generated image 3/3
   [2025-11-15 14:32:48] Step 3/3: Save Assets
   [2025-11-15 14:32:49] Saved 3 images to ImageHistory
   [2025-11-15 14:32:49] Pipeline completed successfully
   ```

**Demo Highlight:**
> "Full transparency. Every step is logged so you can see exactly what happened, debug issues, or understand timing."

#### Step 6: Navigate to Recent Runs (PipelinesScreen - Recent Runs Tab)
**User Action:**
1. Tap back to PipelinesScreen
2. Switch to "Recent Runs" tab
3. See completed run with:
   - ✅ Complete status icon
   - 100% progress bar
   - "Idea to Image Set" template name
   - Timestamp

**Demo Highlight:**
> "All your pipeline runs are saved. Come back anytime to review outputs, reuse assets, or learn from past workflows."

### Optional: Golden Path 2 Extension (Future)
**Step 7:** Open images in Video Studio for editing
**Step 8:** Create promo video from images using another pipeline
**Step 9:** Render final video via DaVinci Resolve Node

### Expected Outputs

**Screens Visited:**
1. Donkey Cockpit
2. PipelinesScreen (Templates tab)
3. LaunchPipelineDialog
4. PipelineRunDetailScreen (live polling view)
5. PipelinesScreen (Recent Runs tab)

**Data Created:**
- 1 CreativePipelineRun (with status, log, outputs)
- 3 AI-generated images (in ImageHistory)
- 1 AISession record (optional, if project context provided)

**Demo Duration:** 2-4 minutes (including 45 seconds of actual pipeline execution)

### Success Criteria

✅ Template selection is intuitive
✅ Launch dialog validates inputs properly
✅ Live polling shows smooth progress updates (no lag)
✅ All 3 images generate successfully
✅ Outputs display correctly (images load, prompts readable)
✅ Execution log is detailed and helpful
✅ No errors, no crashes, no confusing states
✅ User feels like they just unlocked creative superpowers

---

## 🎯 Golden Path Comparison

| Aspect | Strategic Decision Loop | Idea to Assets |
|--------|-------------------------|----------------|
| **Primary Value** | AI-Human collaboration | Creative automation |
| **Key Feature** | Co-Leadership System | Creative Pipelines |
| **User Emotion** | Trust & Partnership | Speed & Power |
| **Demo Duration** | 4-6 minutes | 2-4 minutes |
| **Data Created** | 1 decision + 3 recommendations + outcome | 1 pipeline run + 3 images |
| **Best For** | Investors, Enterprise buyers | Creators, Marketing teams |
| **Wow Factor** | "AI and I work as equals" | "Idea to images in 45 seconds" |

---

## 🚧 Current Blockers

### Golden Path 1: Strategic Decision Loop
✅ **READY** - All components exist and are integrated
- Minor: Terminology inconsistency ("executive meeting" vs "boardroom meeting")

### Golden Path 2: Idea to Assets
❌ **BLOCKED** - Missing Donkey Cockpit integration!
- **Critical:** No Creative Pipelines card/section in Donkey Cockpit
- **Critical:** No shortcuts for popular templates
- Users cannot discover this feature without navigating manually

**Required Fix:** Add Creative Pipelines card to Donkey Cockpit (Phase 2)

---

## 📊 Success Metrics for Demo Readiness

**Each Golden Path Must:**
1. ✅ Have a clear, obvious entry point (from Donkey Cockpit)
2. ✅ Complete in <10 minutes
3. ✅ Work 100% reliably (no errors, no edge cases)
4. ✅ Tell a compelling value story
5. ✅ Show real, functional outputs (not mocks)
6. ✅ Feel smooth and polished (no jarring UX)
7. ✅ Be replicable with seeded demo data

**Platform Must:**
- ✅ Start cleanly (no stale data or broken states)
- ✅ Handle empty states gracefully
- ✅ Show helpful error messages (if something does go wrong)
- ✅ Have consistent terminology and visual design

---

## 🎬 Demo Script Outline

### Opening (30 seconds)
> "This is the Donkey Cockpit - your command center for AI-Human Co-Leadership. Today I'll show you two breakthrough capabilities: strategic decision-making with AI advisors, and one-tap creative workflows."

### Golden Path 1 Demo (5 minutes)
> "Let's say I need to make a strategic decision about our Q1 roadmap. I'll start a Boardroom Meeting..."
- Show agent recommendations
- Commit decision
- Log outcome (or preview)
- Show learning stats

### Golden Path 2 Demo (3 minutes)
> "Now watch this - I have an idea for marketing imagery. In the next 45 seconds, I'll turn this concept into professional AI-generated images..."
- Launch pipeline
- Show live progress
- Review outputs
- Highlight speed and quality

### Closing (30 seconds)
> "That's AI-Human Co-Leadership: AI as your peer, not your tool. Strategic decisions with accountability, and creative superpowers at your fingertips."

**Total Demo Time:** 9 minutes

---

**Golden Paths v1 - Defined!**
**Next:** Implement in Phase 2 (UI Enhancements)
