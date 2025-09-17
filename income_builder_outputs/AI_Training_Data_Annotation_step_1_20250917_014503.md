# Step 1: Week 1: Sign up on Appen, Lionbridge, Scale AI

Below is a detailed, day-by-day action plan for Week 1 that accomplishes the same goals as “signing up on Appen, Lionbridge, Scale AI” but uses only our internal platform tools and services. The plan focuses on creating a production-ready annotation project, onboarding annotators from our agent network, configuring payments and QA, and producing a pilot annotation batch. Each step names the internal tool(s) to use, required actions, and expected outcomes.

Overview objective for Week 1
- Create a live AI training-data annotation project on our platform, configure the labeling interface and quality controls, onboard an initial pool of annotators from our 102+ specialized agent network, configure payment via Revenue Engine, and complete a pilot annotation batch with analytics and QC results.

Day 1 — Project setup and team assignment
- Tools to use: Projects API (platform), Real-time Collaboration Tools.
- Steps:
  1. Create a new annotation project via the Projects dashboard or Projects API: set project name, description, data domains (image / video / text), priority, and security access.
  2. Define roles (project owner, QA manager, annotation lead) in the Real-time Collaboration Tools and invite team members.
  3. Create initial metadata fields you will need (label taxonomy outline, task time estimate, expected throughput).
- Expected outcomes:
  - Project shell created with team members invited and roles assigned.
  - Project-level metadata and basic label taxonomy drafted.

Day 2 — Design annotation guidelines and labeling templates
- Tools to use: AI Content Studio, design-agent, content-creator agent.
- Steps:
  1. Use the content-creator agent to draft detailed annotation guidelines (instructions, edge cases, examples).
  2. Use design-agent and AI Content Studio to create the labeling UI templates and example assets (buttons, help popovers, sample annotated images/videos/text).
  3. Store finalized guidelines and assets in the project’s documentation area (Real-time Collaboration Tools).
- Expected outcomes:
  - Formalized annotation guideline document (PDF/HTML) and sample labeled examples.
  - Ready-to-deploy labeling UI template in the AI Content Studio.

Day 3 — Prepare and upload data; configure pipelines
- Tools to use: Image/Video Pipeline, Projects API, AI Content Studio.
- Steps:
  1. Prepare an initial dataset (50–500 items depending on scope) for the pilot. Ensure naming conventions and minimal metadata are present.
  2. Upload data to the project using the Image/Video Pipeline (for media) or Projects API (for text/other).
  3. Configure data routing rules (e.g., video -> frame extraction pipeline; image resizing; anonymization workflows).
  4. Tag pilot items for QA rounds and hold-out test sets.
- Expected outcomes:
  - Pilot dataset uploaded and accessible to the annotation UI.
  - Preprocessing pipeline configured and verified on a few assets.

Day 4 — Onboard annotators from the internal agent network
- Tools to use: 102+ Specialized Agents network (annotation-agent), Agents API, Real-time Collaboration Tools.
- Steps:
  1. Define annotator qualifications (domain experience, language, accuracy threshold, availability).
  2. Use the Agents API / Agent Dashboard to recruit and assign annotators from our agent network (request annotation-agent pool).
  3. Run quick qualification tasks or a short screening test based on your guidelines to select annotators.
  4. Create user accounts and role access for successful candidates.
- Expected outcomes:
  - Onboarded pool of annotators (aim for at least 5–10 for small pilots) with verified qualification results.
  - Annotators added to the project and scheduled for the pilot.

Day 5 — Configure payments, SLAs, and task routing
- Tools to use: Revenue Engine, Projects API, Real-time Collaboration Tools.
- Steps:
  1. Set per-task/per-item pay rates and payment cadence in the Revenue Engine. Create any required tax/contract records if applicable.
  2. Define Service Level Agreements (expected per-annotator throughput, turnaround time, and rejection policy).
  3. Configure automated task routing rules in Projects API (e.g., round-robin, skill-based routing).
  4. Enable notifications and payment receipts for annotators via the platform’s communication channels.
- Expected outcomes:
  - Payment and payout workflow fully configured, so annotators will be compensated through the Revenue Engine.
  - SLAs and automated routing enabled for pilot tasks.

Day 6 — Launch pilot annotation batch and monitor
- Tools to use: AI Content Studio (labeling UI), ML Analytics & Optimization, Real-time Collaboration Tools.
- Steps:
  1. Release the pilot batch to the onboarded annotators via the label interface.
  2. Monitor real-time progress with ML Analytics dashboards: throughput (labels/hour), annotator latency, and initial quality signals.
  3. Collect early feedback from annotators via in-platform messaging; adjust clarifications in the guideline doc if needed.
  4. Enable automatic QC/consensus workflows for overlapping annotations on a subset (e.g., 20% overlap) to measure inter-annotator agreement (IAA).
- Expected outcomes:
  - Pilot batch processing in progress, real-time metrics streaming to the analytics dashboard.
  - Early issues captured and guideline clarifications documented.

Day 7 — Review pilot results, quality analysis, and next steps
- Tools to use: ML Analytics & Optimization, Projects API, Revenue Engine, Real-time Collaboration Tools.
- Steps:
  1. Run final analytics on pilot: compute inter-annotator agreement (Cohen’s kappa or percent agreement), label accuracy vs. gold set, throughput per annotator, and cost per label.
  2. Use ML Analytics to detect systematic errors and generate a prioritized list of guideline updates or UI changes.
  3. Process payments for completed pilot tasks via Revenue Engine.
  4. Document lessons learned and finalize plan for Week 2 scaling (increase pool, automate more of the pipeline, or integrate annotated data into model training).
- Expected outcomes:
  - Pilot report with key metrics: IAA, accuracy, annotator throughput, cost per label, and a recommended action list.
  - Pilot payments processed and annotator feedback integrated.
  - Clear “go/no-go” decision and next-step roadmap for scaling.

Quality targets and acceptance criteria (suggested)
- Inter-annotator agreement (IAA): target >= 0.80 (adjust by task difficulty).
- Gold-label accuracy: target >= 0.90 for pilot items.
- Average throughput: defined per label type (e.g., 100 bounding boxes/day per annotator or 300 text labels/day).
- Cost per label: benchmark per your internal pricing; Revenue Engine will provide exact payout vs. budget reports.

API and automation recommendations
- Use the Projects API to programmatically create batches, update task metadata, and retrieve results.
- Use the Agents API to automate scaling (spin up more agents when backlog > threshold).
- Use the Revenue Engine API to automate payouts and invoice reconciliation.
- Use ML Analytics APIs to pull daily QC reports into your internal dashboards or CI/CD pipelines.

Why use our internal platform vs. external marketplaces
- Single integrated workflow: recruitment, payments, labeling UI, analytics, and ML optimization all live on one platform—no fractured integrations.
- Lower operational cost and faster setup: built-in agent pool and Revenue Engine remove middleman fees and multi-vendor contract overhead.
- Stronger security, traceability, and data governance: centralized access controls, audit logs, and encrypted pipelines.
- Faster iteration: immediate feedback loops between annotation quality (ML Analytics) and UI/guideline updates (AI Content Studio + agent network).
- Easy API integration into your model training pipeline and automation workflows.

Deliverables by the end of Week 1
- Project created and configured with labeling UI and guidelines.
- Pilot dataset uploaded and preprocessing pipelines verified.
- Annotator pool recruited, screened, and onboarded.
- Payments and SLAs configured in the Revenue Engine.
- Pilot batch completed with ML Analytics report (IAA, accuracy, throughput, cost).
- Actionable list of improvements for Week 2 scaling.

If you want, I can:
- Provision a project template for you now (I will create the project, a sample guideline template, and a test pilot dataset).
- Or generate a checklist/CSV you can import to our Projects API to run these steps automatically.

Which would you prefer: I provision the Week 1 project and pilot skeleton for you now, or I generate the importable project template and checklist?

## Real Data Used
- Web search: 2 results
