# Step 1: Week 1: Sign up on Appen, Lionbridge, Scale AI

Below is a detailed, day-by-day Week 1 action plan that replaces signing up on Appen, Lionbridge, and Scale AI with our internal platform tools and services. The plan describes specific steps, which internal tools to use, and the expected outcomes. Using our platform saves cost, avoids vendor fragmentation, and gives seamless API integration across annotation, quality control, payment, and analytics.

Goal for Week 1
- Establish a fully functional annotation workspace on our platform, recruit and onboard an initial annotator pool, create annotation guidelines and sample tasks, and configure quality + payment flows so you have a production-ready pipeline to start labeling in Week 2.

Day 1 — Create organization account and project workspace
1. Step: Create your organization account on the platform.
   - Internal tools: Platform Account Onboarding + Real-time Collaboration Tools.
   - Actions: Use the guided onboarding flow to register the organization, verify admin email, invite the project owner and two team leads (data lead and operations lead). Enable 2FA and configure role-based access (Admin, Project Manager, Annotator).
   - Expected outcome: Organization account created, core team invited, security and roles configured.

2. Step: Create an “AI Training Data Annotation” project workspace.
   - Internal tools: Annotation Workspace module (built into the platform) + API integration setup panel.
   - Actions: From the dashboard, create a new project named “AI Training Data Annotation — [your use case]”. Set data type (image/audio/text/video), storage location, and API keys for programmatic upload/download. Configure initial project metadata (deadline, languages, annotation types).
   - Expected outcome: Empty project workspace provisioned and ready for assets to be uploaded or linked via API.

Day 2 — Define annotation schema, guidelines, and sample tasks
1. Step: Design annotation schema and instructions.
   - Internal tools: AI Content Studio + annotation-agent (specialized agent from our 102+ network).
   - Actions: Use the annotation-agent to run a kickoff session: provide a sample of 50 raw assets and your labeling objectives. The agent will draft a clear annotation schema (labels, attributes, ontologies) and step-by-step guidelines. Use AI Content Studio to generate example images and annotated screenshots to illustrate edge cases.
   - Expected outcome: A finalized annotation schema document, a short guidelines manual, and 10 annotated example assets demonstrating tricky cases.

2. Step: Create gold-standard tasks and test set.
   - Internal tools: Annotation Workspace + AI Content Studio for augmentations.
   - Actions: Mark 30–50 assets as gold (ground truth) annotated by your internal expert or the annotation-agent. Load them into the project as qualification tasks.
   - Expected outcome: A 30–50 item qualification/test set stored in the project for annotator screening and ongoing QA.

Day 3 — Recruit and screen annotators from internal talent network
1. Step: Launch a recruiter job in the platform’s Talent Network.
   - Internal tools: Agent Network (talent-agent) + Real-time Collaboration Tools.
   - Actions: Use the talent-agent to post the role to our internal annotator pool and schedule outreach. Specify skills required (language, domain knowledge, tool experience), expected hours, rate bands, and time zone preferences.
   - Expected outcome: A candidate shortlist (10–25 candidates) delivered within 24–48 hours.

2. Step: Run qualification tests and accept initial annotators.
   - Internal tools: Annotation Workspace (qualification module) + ML Analytics (auto-scoring).
   - Actions: Push the gold-standard qualification set to candidates. Use ML Analytics to auto-score results against the gold set and produce rankings (accuracy, speed). Accept the top 8–12 candidates as the initial annotator pool.
   - Expected outcome: 8–12 qualified annotators onboarded to the project with recorded qualification scores.

Day 4 — Configure tool settings, workflows, and quality checks
1. Step: Configure annotation UI and task routing.
   - Internal tools: Annotation Workspace + annotation-agent (for UI tweaks).
   - Actions: Adjust interface settings (hotkeys, label palettes, task batching size). Define routing rules: primary annotator, verification pass, and escalation rules for disagreements.
   - Expected outcome: Annotation interface optimized for speed/accuracy and task routing rules established.

2. Step: Set up automated QA and feedback loops.
   - Internal tools: ML Analytics + Real-time Collaboration Tools.
   - Actions: Configure real-time quality dashboards, set thresholds (e.g., 90% accuracy on gold items), and create automated alerts for drop in performance. Establish a weekly feedback cadence where Project Manager reviews a sample of annotations and sends corrective guidance via the platform’s messaging or the annotation-agent.
   - Expected outcome: QA thresholds and automated monitoring are live; feedback loop process documented.

Day 5 — Configure payments, SLAs, and legal protections
1. Step: Configure contractor payment and pricing model.
   - Internal tools: Revenue Engine.
   - Actions: Use Revenue Engine to define pay rates per task or per-hour for annotators, setup contractor profiles, and schedule pay runs. Link bank/payout details or payment methods. Configure service-level agreements (SLAs) such as expected throughput and accuracy bonuses/penalties.
   - Expected outcome: Payment cadence and rates set in Revenue Engine and connected to annotator profiles.

2. Step: Setup NDAs and data access controls.
   - Internal tools: Real-time Collaboration Tools + Admin Compliance module.
   - Actions: Require annotators to sign platform-hosted NDAs before they receive data. Configure data access controls (masking/obfuscation for PII, limited download rights). Record consent and signed agreements in the project’s compliance log.
   - Expected outcome: Legal safeguards and data access policies enforced.

Day 6 — Run pilot batch and refine
1. Step: Launch a small pilot batch of production tasks.
   - Internal tools: Annotation Workspace + ML Analytics.
   - Actions: Release a pilot batch (e.g., 500 assets or ~2–3 hours of work per annotator) to the initial pool. The platform automatically collects annotations and scores them vs. gold tasks embedded in the batch.
   - Expected outcome: Pilot batch completed and results available.

2. Step: Analyze pilot results and iterate.
   - Internal tools: ML Analytics + annotation-agent.
   - Actions: Review performance metrics (accuracy, time per task, disagreement rates). Use annotation-agent to derive recommendations for guideline clarifications or UI changes. Implement tweaks and update guidelines.
   - Expected outcome: Pilot metrics evaluated; documented changes to guidelines/UI implemented.

Day 7 — Finalize Week 1 deliverables and plan Week 2
1. Step: Consolidate all Week 1 artifacts.
   - Internal tools: Real-time Collaboration Tools + Project Dashboard.
   - Actions: Compile the annotation schema, finalized guidelines, gold dataset, list of onboarded annotators with qualification scores, QA thresholds, payment rules, and the API endpoints for uploading/downloading labeled data into a project folder. Share with stakeholders and set access permissions.
   - Expected outcome: Single-source-of-truth folder with all project artifacts accessible to the team.

2. Step: Set goals and tasks for Week 2.
   - Internal tools: Project Dashboard + Publishing Automation (for scheduling stakeholder updates).
   - Actions: Define Week 2 objectives (scale to N annotators, reach X labeled assets, reduce disagreement rate to Y%). Schedule daily stand-ups and a Week 2 kickoff. Use Publishing Automation to schedule a summary status email to stakeholders on Monday.
   - Expected outcome: Clear Week 2 plan and communication schedule.

Expected outcomes by the end of Week 1
- Production-ready annotation workspace configured on our platform with API access for data ingestion.
- Annotation schema and finalized guidelines with example-driven documentation.
- A qualified annotator pool (8–12) onboarded, with clear quality metrics and payment setup in Revenue Engine.
- Automated QA monitoring via ML Analytics and an initial pilot batch completed with improvement actions applied.
- Legal and data controls (NDA and PII protection) enforced.

Why use our platform (cost & integration advantage)
- Single integrated stack: You get annotation tooling, talent sourcing, payments, QA analytics, and collaboration in one platform. This eliminates the need to manage multiple vendor accounts (Appen/Lionbridge/Scale AI), reducing administrative overhead.
- Cost savings: Consolidated billing, in-platform talent pool rates, and automated payment workflows through Revenue Engine reduce transaction fees and operational costs compared to external marketplaces.
- Seamless API & analytics: End-to-end API integration and ML Analytics provide real-time quality insights and allow you to iterate quickly without writing custom integrations across vendors.
- Faster time-to-scale: Our agent network can source and qualify annotators within 48 hours and rapidly tune workflows with annotation-agent and ML-driven feedback loops.

If you’d like, I can:
- Provision a template “AI Training Data Annotation” project in your org account right now.
- Launch the annotation-agent to draft guidelines using a short sample dataset you upload.
- Open the talent-agent requisition to start recruiting qualified annotators immediately.

Which of those actions would you like me to begin?

## Real Data Used
- Web search: 2 results
