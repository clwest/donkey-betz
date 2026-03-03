"""
Tool Descriptions - Central Registry for GPT Function Calling
==============================================================

Session 266: All tool/agent descriptions in one place.

These descriptions tell GPT WHEN to use each tool. They are the
"mini-prompts" that guide tool selection.

Structure:
- TOOL_DESCRIPTIONS: Main tool descriptions (what triggers each tool)
- PARAM_DESCRIPTIONS: Parameter-level descriptions for complex params
"""

from typing import Dict


# =============================================================================
# MAIN TOOL DESCRIPTIONS
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, str] = {

    # -------------------------------------------------------------------------
    # WORKFLOW & ORCHESTRATION
    # -------------------------------------------------------------------------

    "workflow_orchestration_agent": """Use this agent for COMPLETE PACKAGES requiring research + creation, OR for BUSINESS RESEARCH workflows.

DO NOT USE FOR:
- Questions asking for advice: "What style would work best?" -> Just answer, don't call any tool
- Simple creation requests: "Create a logo" -> Use image_generation_agent instead
- Single-step operations: "Upscale image 3" -> Use image_editing_agent instead

=== CREATIVE WORKFLOWS (research + images) ===
- "Research and create 3 logos for X" -> workflow='research_and_create_logos'
- "Create a complete brand identity package for X" -> workflow='brand_identity_package'
- "Make a YouTube thumbnail package for X" -> workflow='youtube_thumbnail_package'
- "Animate logo 5 into a video" -> workflow='logo_to_video', image_id='5'

=== BUSINESS RESEARCH WORKFLOWS (no images, uses spider data + GPT) ===
These are FREE - no Stability AI credits used!

- "Analyze my competitors in the X market" -> workflow='competitor_analysis'
  Deep competitor analysis with SWOT and positioning maps

- "Research customer personas for X" -> workflow='customer_personas'
  Find pain points from Reddit, build personas, extract quotes

- "Do business research for starting a X company" -> workflow='business_research'
  Full research: market trends + competitors + customers + synthesis

- "Validate my startup idea for X" -> workflow='startup_validation'
  Comprehensive validation: market opportunity, competitors, customer validation, differentiation, go/no-go

Keywords that trigger this:
- Creative: "research and create", "complete package", "brand identity", "thumbnail package"
- Business: "competitor analysis", "customer personas", "business research", "validate idea", "startup validation", "market research"

For regular creation like "create 2 cyberpunk logos", use image_generation_agent directly.""",


    # -------------------------------------------------------------------------
    # IMAGE TOOLS
    # -------------------------------------------------------------------------

    "image_generation_agent": """Generate BRAND NEW images from scratch using text prompts.

THIS IS THE PRIMARY TOOL FOR CREATING LOGOS, BANNERS, AND ALL STATIC IMAGES.

USE THIS WHEN user wants to CREATE/GENERATE/MAKE/DESIGN any image:
- LOGOS: "create a logo", "design a logo", "make a cyberpunk logo", "tech startup logo"
- BANNERS: "create banner", "make header image", "social media banner"
- AVATARS: "design avatar", "create profile picture"
- ANY STATIC IMAGE: "create illustration", "generate artwork", "make graphic"

Examples that ALWAYS use this tool:
- "Create a cyberpunk logo for my tech startup" -> image_generation_agent
- "Make 3 minimalist logos" -> image_generation_agent with count=3
- "Design a professional banner" -> image_generation_agent

Supports 80+ style presets, custom dimensions, quality levels, and multiple images (count parameter).

DO NOT USE FOR:
- Modifying existing images -> use image_editing_agent
- Creating VIDEOS -> use video_generation_agent
- Questions about styles -> just answer conversationally, no tool needed""",


    "image_editing_agent": """MODIFY EXISTING images only. Requires an existing image_id.

Operations:
- upscale: 4x resolution enhancement
- remove_background: transparent PNG
- create_variations: multiple style variations
- recolor: change colors with prompt
- search_and_replace: REMOVE objects (omit replace_prompt) OR replace with something else
- creative_upscale: 4x upscale + add creative details with prompt

Supports BATCH OPERATIONS - process multiple images at once:
- Range: "20-25"
- List: "5, 8, 12"
- Combined: "10-15, 20, 25-27"

DO NOT USE FOR creating NEW images -> use image_generation_agent instead.""",


    # -------------------------------------------------------------------------
    # VIDEO TOOLS
    # -------------------------------------------------------------------------

    "video_generation_agent": """⚠️ EXPENSIVE VIDEO TOOL - USE SPARINGLY! ⚠️

STOP! Before using this tool, ask yourself:
- Did the user EXPLICITLY ask for a VIDEO?
- Did they say "video", "animation", "animate", "moving"?
- If they said "logo", "banner", "image", "design" -> USE image_generation_agent INSTEAD!

🚫 NEVER USE FOR:
- "Create a logo" -> image_generation_agent
- "Make a cyberpunk logo" -> image_generation_agent
- "Design a banner" -> image_generation_agent
- ANY request containing "logo" -> image_generation_agent
- ANY static image request -> image_generation_agent

✅ ONLY USE WHEN user explicitly says:
- "Create a VIDEO of..."
- "Make a VIDEO showing..."
- "Animate this image into a video"
- "Generate a video clip"

Operations: generate, animate, extend, chain, lip_sync

⚠️ COSTS ~22% of monthly credits per video! Only use when specifically requested.""",


    "video_editing_agent": """Handle all video editing operations.

FREE Operations (no API cost):
- upscale: 2x or 4x quality enhancement
- apply_effect: color grading (cinematic, vibrant, vintage, noir, warm, cool)
- extract_frame: pull a still image from any timestamp
- reverse: play video backwards
- trim: cut video to specific time range
- speed_change: slow motion 0.5x or speed up 2x
- concatenate: combine multiple videos into one
- rotate_flip: rotate 90/180/270 degrees or flip horizontal/vertical
- fade: add fade in/out effects
- crop_resize: crop to region, resize dimensions, or change aspect ratio
- audio_control: adjust volume, mute, or extract audio
- picture_in_picture: overlay one video on another
- add_watermark: overlay logo/image on video
- blur_region: blur part of video for privacy/censoring

Premium Operations:
- add_text_overlay: captions/titles with timing
- apply_color_grading: DaVinci cinematic effects
- render_professional: EXPORT TO ProRes 422/ProRes 4444/DNxHD
- apply_lut: apply color LUT files
- color_grade_professional: DaVinci-style lift/gamma/gain

Supports BATCH OPERATIONS: Process multiple videos using ranges '1-3' or lists '1, 3, 5'.""",


    "talking_character_agent": """PREFERRED for 'make image talk' requests.

Create complete talking character videos from a still image and text script in ONE STEP.
Pipeline: Text-to-Speech (ElevenLabs) + Image-to-Video (Runway) + Lip Sync

WORKS WITH BOTH photorealistic AND cartoon/Pixar-style characters!

Use when user wants:
- "make image X talk and say..."
- "create talking video"
- "add speech to image"
- "animate character with voice"
- "AI spokesperson video"

IMPORTANT: When user says 'using [name] voice' or 'with [name] voice', extract that name as the voice parameter!

Cost: ~$0.60-1.00 per 10-second video.""",


    # -------------------------------------------------------------------------
    # AUDIO TOOLS
    # -------------------------------------------------------------------------

    "audio_generation_agent": """Handle all audio generation.

Operations:
- generate_voice: text-to-speech with ElevenLabs
- add_voiceover: add narration to existing video

Use this for ANY standalone audio generation request.
For talking characters (TTS + animation + lip sync), use talking_character_agent instead.""",


    # -------------------------------------------------------------------------
    # 3D TOOLS
    # -------------------------------------------------------------------------

    "three_d_generation_agent": """Convert images to 3D models using Replicate TRELLIS.

Creates downloadable GLB files for 3D printing.

Use when users want:
- "convert to 3D"
- "make 3D model"
- "3D print"
- "create 3D object"

Currently only supports 'convert' operation from existing image.""",


    # -------------------------------------------------------------------------
    # TRAINING TOOLS
    # -------------------------------------------------------------------------

    "character_training_agent": """Train a FLUX LoRA model to learn a consistent visual style.

Requires 4-10 example images with similar style/aesthetic.
Creates a reusable style model for all future generations.

Use when user wants to:
- "train project style"
- "create custom style"
- "learn my visual aesthetic"
- "make consistent style"

Perfect for brand consistency across all content.""",


    # -------------------------------------------------------------------------
    # COLLABORATION TOOLS
    # -------------------------------------------------------------------------

    "coleadership_agent": """Get collaborative opinions from AI executive team.

Team: CTO, COO, Creative Director, CFO, Data Analyst

Use when user asks:
- "what do you think"
- "should we"
- "get opinions"
- "is this a good direction"
- "thoughts on"
- "feedback on"
- "worth pursuing"
- "ask the team"

Can reference specific images/content to get opinions on style, direction, or training decisions.""",


    # -------------------------------------------------------------------------
    # RESEARCH TOOLS
    # -------------------------------------------------------------------------

    "web_search": """Search the web using Google via Serper API.

Use when user asks for:
- Current information or trends
- Research or competitor analysis
- "find out about", "search for", "look up"
- "what are the latest"

Enables the 'research and create' workflow where you can research a topic then generate content based on findings.""",


    # -------------------------------------------------------------------------
    # BUSINESS RESEARCH TOOLS (Session 293)
    # -------------------------------------------------------------------------

    "competitor_analysis_agent": """Comprehensive competitor and market analysis WITHOUT image/video generation.

Use this for BUSINESS RESEARCH requests like:
- "Research the X market for my startup"
- "Analyze competitors in X industry"
- "Who are the main competitors in X?"
- "Do a competitive analysis of X"
- "What's the competitive landscape for X?"
- "SWOT analysis for X market"

This agent provides:
- Market research with trends and insights
- Competitor identification and deep analysis
- SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
- Feature comparison across competitors
- Pricing analysis when available
- Market positioning recommendations

IMPORTANT: This is for PURE RESEARCH - no image/video generation.
Uses spider network + web search for real data.""",


    "customer_research_agent": """Customer persona and pain point research WITHOUT image/video generation.

Use this for CUSTOMER RESEARCH requests like:
- "Build customer personas for X"
- "What are customer pain points for X?"
- "Research customer needs for X market"
- "Who buys X products?"
- "What do customers complain about in X?"
- "Customer sentiment analysis for X"

This agent provides:
- 2-3 detailed customer personas with demographics
- Pain point extraction from Reddit, forums, reviews
- Customer motivations and goals
- Sentiment analysis
- Direct customer quotes and examples
- Buying behavior insights

IMPORTANT: This is for PURE RESEARCH - no image/video generation.
Uses spider network (especially Reddit) for real customer data.""",


    "brand_strategy_agent": """Comprehensive brand strategy research that READS existing project research.

⭐ BEST FOR: "Create a brand identity" or "Develop brand strategy" when INSIDE a project
that already has competitor/customer research.

Use this for BRAND STRATEGY requests like:
- "Create a brand identity for this project"
- "Develop our brand strategy"
- "What should our brand positioning be?"
- "Create brand guidelines based on our research"
- "Build a brand strategy from the competitor/customer research"

This agent:
1. READS existing project research (competitor analysis, customer research)
2. Synthesizes findings into comprehensive brand strategy
3. Provides positioning, messaging, visual direction, and actionable recommendations

Output includes:
- Brand Positioning (differentiation, market position)
- Target Audience Summary (from customer research)
- Brand Messaging Framework (taglines, value propositions)
- Visual Direction (colors, typography, imagery guidance)
- Competitive Differentiation (how to stand out)
- Actionable Next Steps

IMPORTANT: This is for STRATEGIC RESEARCH - no image/video generation.
Uses existing project research as foundation, enhances with fresh spider/web data.""",


    "content_strategy_agent": """Strategic content planning agent that READS existing project research.

⭐ BEST FOR: "What content should I create?" or "Plan my content strategy" when INSIDE a project
that already has competitor/customer/brand research.

Use this for CONTENT STRATEGY requests like:
- "What content should I create for this project?"
- "Plan my content strategy based on the research"
- "What topics should I write about?"
- "Create a content calendar"
- "What content pillars should I focus on?"

This agent:
1. READS existing project research (competitor, customer, brand strategy)
2. Analyzes current content trends from spider network
3. Provides comprehensive content recommendations

Output includes:
- Content Pillars (3-5 main themes to focus on)
- Recommended Formats (blog, video, social, email, etc.)
- Topic Ideas (10-15 specific content pieces with details)
- Content Calendar (publishing cadence, best times)
- Quick Wins (content that can be created immediately)
- SEO Opportunities (keywords and topics with high potential)

IMPORTANT: This is for STRATEGIC PLANNING - no image/video generation.
Uses existing project research as foundation, enhances with fresh spider/web data.""",


    "marketing_strategy_agent": """Strategic marketing planning agent that READS existing project research.

⭐ BEST FOR: "How should I market this?" or "Create a marketing plan" when INSIDE a project
that already has competitor/customer/brand/content research.

Use this for MARKETING STRATEGY requests like:
- "How should I market this product?"
- "Create a marketing strategy based on the research"
- "What marketing channels should I focus on?"
- "Plan my marketing campaigns"
- "How do I reach my target audience?"

This agent:
1. READS existing project research (competitor, customer, brand, content strategy)
2. Analyzes current marketing trends from spider network
3. Provides comprehensive marketing recommendations

Output includes:
- Target Audience Summary (from customer research)
- Channel Strategy (organic social, paid, search, email, partnerships)
- Campaign Ideas (3-5 campaigns with names, channels, messaging)
- Marketing Funnel (awareness, consideration, conversion, retention)
- Budget Recommendations (channel allocation, priorities)
- Key Metrics (what to track, ROI approach)
- Quick Wins (marketing actions to start immediately)

IMPORTANT: This is for STRATEGIC PLANNING - no image/video generation.
Uses existing project research as foundation, enhances with fresh spider/web data.""",


    "strategic_review": """IMPORTANT: Call this AFTER web_search but BEFORE image_generation_agent.

Get strategic review and creative direction from the executive team (CTO, COO, Creative Director) based on research findings.

They will provide:
1. Key insights to incorporate
2. Creative direction recommendations
3. Technical considerations
4. Specific prompt suggestions for image generation

This ensures co-leadership agents guide the creative process rather than just reviewing finished work.""",


    # -------------------------------------------------------------------------
    # PROJECT TOOLS
    # -------------------------------------------------------------------------

    "create_project_from_research": """⭐ SAVE RESEARCH TO PROJECT - Use this to bundle business research into a project.

Use this AFTER completing ANY of these:
1. Business research (competitor_analysis_agent, customer_research_agent)
2. Image generation workflow (research + image generation)

This packages research, analysis, and any images into an organized project.
Images are OPTIONAL - this works for business research without any images.

TRIGGERS: 'save to project', 'create project from research', 'organize research', 'bundle research'""",


    "create_brand_video": """Create a complete brand video from concept to finished product.

Orchestrates Runway ML video generation with professional styling.
Generates 2-5 video clips that can later be chained with transitions.

Use when user wants:
- Complete brand video
- Promotional video
- Multiple video clips for a brand/project""",


    # -------------------------------------------------------------------------
    # LEGAL AGENTS (Session 403)
    # -------------------------------------------------------------------------

    "legal_doc_drafter_agent": """⚖️ Pro Se Legal Assistant for Colorado Family Law - GENERAL LEGAL INFORMATION ONLY.

⚠️ IMPORTANT DISCLAIMERS:
- This is GENERAL LEGAL INFORMATION, NOT legal advice
- Does NOT create an attorney-client relationship
- Users should ALWAYS consult a licensed Colorado attorney for their specific situation
- Laws change - verify all information with current statutes and court rules

Use this agent for:
- Understanding Colorado divorce procedures and requirements
- General custody/parenting time information
- Child support guideline explanations
- Drafting TEMPLATE documents (motions, emails, declarations)
- Procedural checklists and deadlines
- Locating Colorado JDF (Judicial Department Forms)
- Understanding court procedures and requirements

Document Types Available:
- 'guidance': General legal information and explanations
- 'motion': Court filing templates (continuances, modifications)
- 'email': Meet-and-confer professional correspondence
- 'declaration': Sworn statement templates
- 'checklist': Step-by-step procedural guides

Case Types Covered:
- Divorce (dissolution of marriage)
- Custody (allocation of parental responsibilities)
- Child support (calculation and modification)
- Parenting time (visitation schedules)
- Modification (changing existing orders)
- Enforcement (ensuring compliance)

Keywords that trigger this:
- 'legal', 'law', 'court', 'attorney', 'lawyer', 'judge'
- 'divorce', 'custody', 'child support', 'parenting time'
- 'motion', 'file', 'declaration', 'subpoena'
- 'rights', 'Colorado', 'family law'
- 'JDF', 'forms', 'pro se', 'self-represented'

DO NOT USE FOR:
- Criminal law matters
- Federal court cases
- Legal matters outside Colorado
- Urgent situations requiring immediate legal action
- Cases involving domestic violence (refer to local resources)

ALL OUTPUTS INCLUDE MANDATORY DISCLAIMERS.""",


    # -------------------------------------------------------------------------
    # CONTENT WRITING AGENTS (Session 496)
    # -------------------------------------------------------------------------

    "content_writer_agent": """📝 MANDATORY for all WRITTEN TEXT content! Transforms research into written content.

USE THIS AGENT when user says ANY of these:
- "write a blog post", "write a blog", "blog post based on"
- "write a podcast script", "podcast script from"
- "write a video script", "video script from"
- "write an article", "article based on"
- "write a newsletter", "newsletter from"
- "write a social thread", "social thread from"
- "turn this into a blog", "create a blog from this research"

⚡ TRIGGER WORDS: 'write', 'blog', 'podcast script', 'video script', 'article', 'newsletter', 'social thread'

Content Types:
- blog_post: SEO-optimized blog with title, intro, sections, conclusion
- podcast_script: Conversational script with intro, segments, outro
- video_script: Video script with scenes, narration, b-roll suggestions
- article: Professional article with headline, lead, body, CTA
- social_thread: Series of connected posts for Twitter/X, LinkedIn
- newsletter: Email newsletter with subject, preview, sections

⛔ DO NOT use workflow_orchestration_agent for written content!
⛔ DO NOT use image_generation_agent when user wants TEXT content!

Examples:
- "Write a blog post based on this research" -> content_writer_agent with content_type='blog_post'
- "Turn this into a podcast script" -> content_writer_agent with content_type='podcast_script'
- "Write a video script from this research" -> content_writer_agent with content_type='video_script'
- "Create a newsletter from these findings" -> content_writer_agent with content_type='newsletter'""",


    # -------------------------------------------------------------------------
    # SESSION 672: ML PIPELINE MANAGEMENT TOOLS
    # -------------------------------------------------------------------------

    "opportunity_manager_tool": """Manage and query opportunities from the ML Pipeline.

USE THIS WHEN user wants to:
- VIEW opportunities: "Show my opportunities", "What opportunities do I have?"
- FILTER opportunities: "Show high-scoring opportunities", "What's pending?", "Show job opportunities"
- GET DETAILS: "Tell me more about opportunity X", "Show opportunity details"
- CHECK STATUS: "What's the status of my opportunities?"

Actions:
- list: List opportunities with optional filters (status, category, min_score)
- get: Get detailed info about a specific opportunity by ID
- stats: Get opportunity statistics (counts by status, avg scores)
- search: Search opportunities by keyword

DO NOT USE FOR:
- Scoring new spider data -> use opportunity_scoring_agent
- Managing tasks -> use task_manager_tool
- Tracking revenue -> use revenue_tracker_tool""",


    "task_manager_tool": """Manage OpportunityTasks - the action items from high-scoring opportunities.

USE THIS WHEN user wants to:
- VIEW tasks: "Show my tasks", "What tasks do I have?"
- ACCEPT tasks: "Accept this task", "I'll work on task X"
- UPDATE STATUS: "Mark task X as done", "I applied for this", "I won/lost this"
- CHECK PROGRESS: "What's my task progress?"

Actions:
- list: List tasks with optional filters (status, priority, agent)
- get: Get detailed task info by ID
- accept: Accept a pending task
- start: Mark task as in_progress
- apply: Mark task as applied/submitted
- complete: Mark task as won (success)
- fail: Mark task as lost (rejection)
- add_note: Add a note/update to a task

Task Statuses: pending, accepted, in_progress, applied, waiting, won, lost, expired, cancelled

DO NOT USE FOR:
- Viewing opportunities -> use opportunity_manager_tool
- Executing agents -> use pipeline_orchestrator_tool""",


    "pipeline_orchestrator_tool": """Orchestrate the ML Opportunity Pipeline - trigger agent execution manually.

USE THIS WHEN user wants to:
- EXECUTE pipeline: "Execute task X", "Run the agent for this opportunity"
- CHECK PIPELINE: "What's running?", "Pipeline status"
- TRIGGER AGENTS: "Have the research agent work on this", "Execute this task"

Actions:
- execute_task: Execute a specific OpportunityTask with its assigned agent
- execute_opportunity: Run the full pipeline for an opportunity
- status: Check pipeline execution status
- queue: View pending execution queue

This bypasses the automated Celery scheduler for manual control.

DO NOT USE FOR:
- Viewing tasks -> use task_manager_tool
- Scoring opportunities -> use opportunity_scoring_agent""",


    "revenue_tracker_tool": """Track revenue and outcomes for opportunities - closes the ML feedback loop.

USE THIS WHEN user wants to:
- LOG REVENUE: "I earned $500 from opportunity X", "Log revenue"
- CHECK EARNINGS: "How much have I earned?", "Revenue stats"
- TRACK ACCURACY: "How accurate are the predictions?", "ML accuracy"
- LINK CONTENT: "Link this video to opportunity X"

Actions:
- log_revenue: Record revenue from an opportunity (amount, source, date)
- list_revenue: View revenue history for an opportunity
- stats: Get overall revenue statistics
- accuracy: Compare predicted vs actual revenue
- link_content: Associate created content with an opportunity

This data feeds back into ML model retraining for better predictions.

DO NOT USE FOR:
- Viewing opportunities -> use opportunity_manager_tool
- Managing tasks -> use task_manager_tool""",


    # -------------------------------------------------------------------------
    # SESSION 683: ML ANALYSIS TOOL
    # -------------------------------------------------------------------------

    "ml_analysis": """Analyze data using auto-selected ML models. The system detects data type and picks optimal models.

USE THIS WHEN user wants to:
- ANALYZE DATA: "Analyze this data", "What patterns are in this data?"
- PREDICT: "Predict next price", "Forecast this time series"
- DETECT: "Find anomalies", "Detect outliers", "Find unusual patterns"
- CLUSTER: "Group similar items", "Identify clusters"
- GRAPH ANALYSIS: "Analyze relationships", "Find communities in this network"

Auto-Detection by Data Type:
- Time series data (timestamps, prices, metrics) -> LSTM, Prophet for forecasting
- Graph data (nodes, edges, relationships) -> GNN for community detection, link prediction
- Anomaly detection needs -> VAE Autoencoder, Isolation Forest
- Decision optimization -> Reinforcement Learning (DQN, PPO)
- Text data -> DistilBERT, Embeddings for NLP analysis
- General classification/regression -> LightGBM, XGBoost

Returns:
- Task detected (time_series, graph, anomaly, etc.)
- Models used with confidence scores
- Predictions/analysis results
- Selection reasoning (why these models were chosen)

Example data formats:
- Time series: {"timestamp": ["2024-01-01", "2024-01-02"], "price": [100, 105]}
- Graph: {"nodes": ["A", "B", "C"], "edges": [["A", "B"], ["B", "C"]]}
- Text: {"text": "Analyze this document content..."}

DO NOT USE FOR:
- Simple queries about data -> just answer conversationally
- Image/video generation -> use generation agents
- Web research -> use web_search""",


    # -------------------------------------------------------------------------
    # SESSION 674: UNIVERSAL AGENT TOOL
    # -------------------------------------------------------------------------

    "universal_agent_tool": """Invoke ANY of the 46 specialized agents by name for tasks not covered by dedicated tools.

This is the gateway to ALL agents in the system. Match user requests to the appropriate agent:

=== BLOCKCHAIN & CRYPTO (5 agents) ===
USE FOR: smart contract audits, whale watching, exploit detection, transaction monitoring
- "Audit this smart contract" → BlockchainAuditCoordinator (coordinates full audit)
- "Check for exploits in this contract" → ExploitDetectorAgent
- "Watch whale wallets" → WhaleWatcherAgent
- "Monitor transactions" → TransactionMonitorAgent
- "Audit this Solidity code" → SmartContractAuditorAgent

=== STOCK & FINANCIAL ANALYSIS (9 agents) ===
USE FOR: stock analysis, market movements, institutional activity, bull/bear cases
- "Analyze NVDA stock" → StockAnalystAgent
- "What's the bull case for AAPL?" → BullCaseAgent
- "Bear case for Tesla" → BearCaseAgent
- "Watch market movements" → MarketMovementMonitorAgent
- "Check institutional activity" → InstitutionalWatcherAgent
- "Detect market anomalies" → MarketAnomalyDetectorAgent
- "Scan for trading signals" → SignalScannerAgent
- "Full stock audit" → StockAuditCoordinator (coordinates all stock agents)
- "Market intelligence report" → MarketIntelligenceCoordinator

=== PREDICTION MARKETS & BETTING (3 agents) ===
USE FOR: prediction markets, sports odds, arbitrage opportunities
- "Analyze Kalshi/Polymarket" → PredictionMarketAnalyst
- "Check sports odds" → SportsOddsAnalyst
- "Find arbitrage opportunities" → ArbitrageDetector

=== DEVELOPMENT (3 agents) ===
USE FOR: code review, full-stack development, DevOps
- "Review this code for bugs" → CodeReviewAgent
- "Build a full feature" → FullStackDeveloperAgent
- "Help with CI/CD/Docker" → DevOpsAgent
NOTE: CodeGeneratorAgent is blocked (no codebase access). Use CodeReviewAgent for analysis.

=== PODCAST & DEBATES (4 agents) ===
USE FOR: AI debates, podcast generation, moderated discussions
- "Create a podcast debate about AI" → PodcastCoordinatorAgent (coordinates full podcast)
- "Argue FOR this position" → DebateAdvocateAgent
- "Argue AGAINST this position" → DebateSkepticAgent
- "Moderate a discussion" → ModeratorAgent

=== NARRATIVE & CULTURE (4 agents) ===
USE FOR: narrative analysis, cultural trends, trend detection
- "Track narrative drift on X topic" → NarrativeDriftCoordinator
- "Analyze cultural impact" → CulturalImpactAgent
- "Find historical narrative patterns" → NarrativeHistorianAgent
- "Detect trend breaks" → TrendBreakDetectorAgent

=== CONTENT STUDIO (4 agents) ===
USE FOR: autonomous content, topic mining, contrarian perspectives
- "Run autonomous content generation" → AutonomousContentStudioCoordinator
- "Mine topics for content" → TopicMinerAgent
- "Get contrarian perspective" → ContrarianAgent
- "Analyze content performance" → PerformanceAnalystAgent

=== CAMPAIGNS & WORKFLOWS (2 agents) ===
USE FOR: marketing campaigns, AI series workflows
- "Orchestrate marketing campaign" → CampaignOrchestratorAgent
- "Run AI series workflow" → AISeriesWorkflowAgent

=== ORCHESTRATION (3 agents) ===
USE FOR: workflow execution, opportunity pipelines, content execution
- "Execute workflow" → WorkflowAgent
- "Manage opportunity pipeline" → OpportunityPipelineAgent
- "Execute content plan" → ContentExecutorAgent

=== SYSTEM & ANALYSIS (3 agents) ===
USE FOR: system diagnostics, deep reasoning, technical documentation
- "Check system health" → SystemIntelligenceAgent
- "Deep reasoning on X" → ThinkingAgent
- "Create technical documentation" → TechnicalDocumentAgent

=== SECURITY (2 agents) ===
USE FOR: memory isolation, content auditing
- "Isolate memory" → MemoryIsolationAgent
- "Audit content for compliance" → ContentAuditAgent

=== LEGAL (1 agent) ===
USE FOR: Colorado family law questions (general info only)
- "Help with custody questions" → LegalDocDrafterAgent
- "Draft a motion template" → LegalDocDrafterAgent

=== RENDERING (1 agent) ===
USE FOR: DaVinci Resolve integration, professional video rendering
- "Render video in DaVinci Resolve" → ResolveAgent

=== TRAINING (2 agents) ===
USE FOR: character/style training, trained model generation
- "Train a character style" → CharacterTrainingAgent
- "Generate with trained model" → TrainedCreationAgent

=== MARKET INTELLIGENCE (1 agent) ===
USE FOR: comprehensive market analysis
- "Market intelligence report" → MarketIntelligenceAgent

DO NOT USE FOR:
- Image creation → use image_generation_agent
- Video creation → use video_generation_agent
- General research → use web_search
- Strategy research → use brand_strategy_agent, content_strategy_agent, etc.
- Written content → use content_writer_agent""",


    # -------------------------------------------------------------------------
    # SESSION 695: SKIN LAYER - WORKSPACE MANAGEMENT TOOL
    # -------------------------------------------------------------------------

    "workspace_tool": """🔧 SKIN LAYER: Manage project workspaces where agents write code.

This tool bridges AI agents to real file systems - the "SKIN" where AI touches reality.

USE THIS WHEN user wants to:
- REGISTER a project: "Register this project", "Add workspace at /path/to/project"
- LIST workspaces: "Show my workspaces", "List registered projects"
- SET ACTIVE: "Switch to project X", "Set X as active workspace"
- CHECK STATUS: "Workspace status", "What's the current workspace?"
- SCAN structure: "Rescan the project", "Analyze project structure"
- WRITE FILES: "Write this code to file X", "Create file at path"
- GIT OPERATIONS: "Commit these changes", "Create a branch"
- VIEW OPERATIONS: "Show recent operations", "What did agents change?"
- ROLLBACK: "Undo the last file change", "Rollback operation X"

Actions:
- register: Register a new project directory as workspace
- list: List all user's workspaces
- set_active: Switch active workspace
- status: Get current workspace status with tech stack
- scan: Rescan and update workspace context
- write: Write content to a file (with audit trail)
- read: Read a file from workspace
- git_status: Get git status of workspace
- git_commit: Commit changes with agent attribution
- git_branch: Create a new branch
- operations: View recent operations/audit trail
- rollback: Rollback a specific operation

This enables:
- FullStackDeveloperAgent to actually write code to projects
- CodeReviewAgent to analyze and suggest changes
- DevOpsAgent to execute commands
- Complete audit trail of all agent modifications

⚠️ IMPORTANT: All file operations are logged and can be rolled back.
Protected paths (like .env) cannot be modified by agents.""",

    # =========================================================================
    # Session 709: Body Vitals Tools - Connect Brain to Body Systems
    # =========================================================================

    "get_body_vitals": """Query the health status of body systems (HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR).

Use this tool when:
- User asks about system health, status, or "how am I doing?"
- Before executing expensive operations (check LUNGS budget)
- When troubleshooting issues (check relevant systems)
- For proactive health awareness at session start
- User asks "what needs attention?" (combines with alerts)

The body systems are:
- HEART: Core component health (brain, organs, sensory, memory) - Overall platform health
- LUNGS: Budget/resource management - Token limits, API costs, rate limits
- CIRCULATORY: Data flow health - Redis queues, Celery tasks, WebSockets
- SPINE: API routing health - Latency, error rates, route patterns
- IMMUNE: Security status - Threats detected, quarantined IPs, attack patterns
- DIGESTIVE: Data pipeline - Spider ingestion, processing queue, throughput
- MUSCULAR: Agent execution - Success rates, fatigue levels, active/idle agents

Response includes:
- overall_health: Status string (healthy/degraded/impaired/critical/failing)
- health_score: 0-100% weighted score
- systems: Per-system status with emoji indicators
- alerts: Active alerts sorted by severity
- recommendation: Actionable next step""",

    "check_resource_budget": """Check if the current budget allows for an operation.

ALWAYS use this tool BEFORE:
- Large image generation requests (multiple images, high-res)
- Video generation (expensive, ~$0.50-2.00 per video)
- Complex multi-step workflows
- Operations requiring expensive models (GPT-5, Claude Opus, video models)
- Batch operations that could consume significant tokens

The response tells you:
- can_proceed: Whether to proceed (true/false)
- oxygen_level: Current budget % remaining (0-100)
- status: Current LUNGS status (normal/elevated/hyperventilating/holding)
- warning: Warning message if budget is low
- recommendation: Model selection advice based on budget

Budget levels:
- 80-100%: Healthy - proceed with any operations
- 50-79%: Moderate - avoid very expensive operations
- 20-49%: Low - use efficient models (GPT-4o-mini, Haiku)
- 10-19%: Critical - only essential operations
- 0-9%: Exhausted - operations should be blocked

Example usage:
1. User asks for video generation
2. Call check_resource_budget(estimated_cost=1.50)
3. If can_proceed=false, suggest alternatives or warn user""",

    "get_system_alerts": """Get active alerts from all body systems.

Use this tool when:
- User asks "what needs attention?" or "any issues?"
- Starting a new session (quick health check)
- Something seems wrong with the system
- Before important operations to ensure system is healthy
- User reports errors or slow performance

Returns alerts sorted by severity (critical first) with:
- system: Which body system raised the alert (heart, lungs, immune, etc.)
- message: What the issue is in plain language
- severity: info, warning, or critical
- severity_score: 1 (info), 2 (warning), 3 (critical)

Severity threshold options:
- 'critical': Only show critical issues (system down, budget exhausted, security threat)
- 'warning': Show warnings and critical (default - recommended)
- 'info': Show all alerts including informational

Examples of alerts:
- LUNGS: "Budget low (15% remaining)" - severity: warning
- IMMUNE: "Threat level: high" - severity: critical
- DIGESTIVE: "Queue backlog: 5000 items pending" - severity: warning
- MUSCULAR: "Agent execution: paralyzed" - severity: warning""",

    # -------------------------------------------------------------------------
    # Session 725: INTELLIGENCE TOOLS - Connect Brain to Intelligence System
    # -------------------------------------------------------------------------

    "predictions_tool": """Query agent predictions from the Intelligence system database.

ALWAYS USE THIS TOOL IMMEDIATELY when user asks about predictions. Do NOT ask clarifying questions first - just run the tool and show results.

Trigger phrases (use tool immediately):
- "what predictions have agents made"
- "show me predictions"
- "agent predictions"
- "prediction accuracy"
- "prediction leaderboard"

Actions:
- 'list': Get recent predictions (default 20) - USE THIS FOR GENERAL QUERIES
- 'get': Get a specific prediction by ID
- 'stats': Get prediction statistics (total, accuracy rate, by category)
- 'leaderboard': Get agents ranked by prediction accuracy
- 'by_agent': Get predictions from a specific agent
- 'by_category': Filter predictions by type (trend, market, technology, etc.)

Returns prediction data from AgentPrediction table including:
- title, prediction text, category, source
- confidence score and deadline
- status (pending, verified_true, verified_false, etc.)
- agent who made the prediction""",

    "gates_tool": """Query pilot readiness gates from the Intelligence system database.

ALWAYS USE THIS TOOL IMMEDIATELY when user asks about gates. Do NOT ask clarifying questions first.

Trigger phrases (use tool immediately):
- "what gates are pending"
- "gates status"
- "show gates"
- "pilot gates"
- "what needs approval"

Actions:
- 'list': Get all gates (default 20) - USE THIS FOR GENERAL QUERIES
- 'get': Get a specific gate by ID
- 'stats': Get gate statistics (by status, by risk level)
- 'checklist': Get checklist items for a specific gate
- 'by_status': Filter gates by status (not_started, in_progress, approved, etc.)
- 'by_risk': Filter gates by risk level (low, medium, high, critical)

Returns gate data from PilotReadinessGate table including:
- decision info, summary, success/failure criteria
- status (not_started, in_progress, ready, approved, blocked, waived)
- risk level and risk factors
- approval tracking (who approved, when)""",

    "pilots_tool": """Query pilot executions from the Intelligence system database.

ALWAYS USE THIS TOOL IMMEDIATELY when user asks about pilots. Do NOT ask clarifying questions first.

Trigger phrases (use tool immediately):
- "what pilots are running"
- "show pilots"
- "pilot status"
- "pilot results"
- "running experiments"

Actions:
- 'list': Get all pilots (default 20) - USE THIS FOR GENERAL QUERIES
- 'get': Get a specific pilot by ID
- 'stats': Get pilot statistics (by status, by outcome)
- 'running': Get currently active pilots
- 'completed': Get finished pilots
- 'by_outcome': Filter by outcome (success, partial, failure, etc.)

Returns pilot data from PilotExecution table including:
- name, description, scope, constraints
- status (planned, running, paused, completed, failed)
- outcome (pending, success, partial, failure, inconclusive)
- metrics collected and learnings
- whether kill switch was triggered""",

    # Session 800: Reasoning Engine Tool - Connect PA to ThinkingAgent
    "reasoning_engine_tool": """Access the Autonomous Reasoning Engine (ThinkingAgent) - the system's self-aware thinking layer.

ALWAYS USE THIS TOOL when user asks about:
- "what has the system been thinking"
- "show me recent insights"
- "what patterns have you noticed"
- "reasoning engine status"
- "autonomous thinking"
- "system insights"
- "what actions has the system taken autonomously"

Actions:
- 'thoughts': Get recent thought records (insights, patterns, decisions) - DEFAULT
- 'insights': Get just the insights from recent thinking cycles
- 'actions': Get autonomous actions taken by the system
- 'status': Get reasoning engine status (last cycle, next scheduled)
- 'trigger': Request a new thinking cycle (queues task)

The ThinkingAgent runs autonomously and:
1. GATHERS context from learning, memories, spiders
2. REFLECTS on patterns and trends
3. GENERATES insights and opportunities
4. DECIDES what actions to take
5. EXECUTES actions using other agents

This tool connects you to what the system has been THINKING about autonomously.""",


    "legislation_tool": """DEPRECATED — use intelligence_tool with legislation actions instead.

Migrated actions: search → intelligence_tool.legislation_search, summary → intelligence_tool.legislation_summary,
trending → intelligence_tool.briefs (legislation desk), overview → intelligence_tool.overview (legislation desk).
Sunset date: 2026-04-01.""",

}


# =============================================================================
# PARAMETER DESCRIPTIONS (for complex parameters)
# =============================================================================

PARAM_DESCRIPTIONS: Dict[str, Dict[str, str]] = {

    "workflow_orchestration_agent": {
        "workflow": "Workflow type: 'research_and_create_logos', 'youtube_thumbnail_package', 'brand_identity_package', 'product_photography_kit', 'video_thumbnail_series', 'logo_to_video'",
        "topic": "The main topic INCLUDING any character/mascot. If user mentions a specific character (donkey, owl, lion), INCLUDE it in the topic!",
        "count": "Number of images to create (1-5). Extract from 'create 3 logos' -> count=3",
        "style_preferences": "CRITICAL: Extract ANY style mentioned! Animation: 'pixar', 'disney', 'dreamworks', 'ghibli', 'anime'. Art: 'watercolor', 'cyberpunk', 'minimalist'. ALWAYS extract the style!",
        "image_id": "Image ID to animate (for logo_to_video). Can use sequential number or UUID.",
        "user_message": "CRITICAL: ALWAYS pass the EXACT original user message here! Copy-paste verbatim.",
    },

    "image_generation_agent": {
        "prompt": "Text description of the image to generate",
        "count": "Number of images (1-5). Use when user asks for multiple: 'create 3 logos' -> count=3",
        "character_model_name": "Trained style/model name. Extract if user mentions 'our brand style', 'company style', 'the trained model'. Uses FLUX + custom LoRA.",
    },

    "image_editing_agent": {
        "operation": "upscale | remove_background | create_variations | recolor | search_and_replace | creative_upscale",
        "image_id": "Single: '2' or UUID. BATCH: Range '20-25', List '5, 8, 12', Combined '10-15, 20'",
    },

    "video_generation_agent": {
        "operation": "generate | animate | extend | chain | lip_sync",
    },

    "talking_character_agent": {
        "image_id": "Character image to animate. Should show a clear face for best lip sync.",
        "text": "Script text (1-2 sentences work best for 5-10 second videos)",
        "voice": "MUST extract from user's request if they say 'using [name] voice'. Options: Rachel, Antoni, Daniel, Emily, Bella, George",
        "lipsync_model": "auto (recommended), latentsync (best for cartoon), sync_labs (best for photorealistic)",
    },

}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_tool_description(tool_name: str) -> str:
    """Get the description for a specific tool."""
    return TOOL_DESCRIPTIONS.get(tool_name, f"Tool for {tool_name} operations.")


def get_param_description(tool_name: str, param_name: str) -> str:
    """Get the description for a specific tool parameter."""
    tool_params = PARAM_DESCRIPTIONS.get(tool_name, {})
    return tool_params.get(param_name, "")


def list_available_tools() -> list:
    """List all tools with descriptions defined."""
    return list(TOOL_DESCRIPTIONS.keys())
