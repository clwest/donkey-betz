# Step 2: Week 1: Build portfolio with 3 sample articles

Goal: By the end of Week 1 you will have a polished portfolio of three SEO-optimized sample articles (800–1,500 words each) with hero images, metadata, hosted on your platform portfolio page, ready for scheduled publishing and tracking. All work uses internal platform capabilities for writing, design, SEO, publishing, and analytics to maximize cost savings and seamless integration.

Overview of tools to use (internal only)
- content-creator agent — create drafts, revisions, and final copy.
- design-agent + AI Content Studio (DALL·E 3 / Stable Diffusion) — produce hero images, thumbnails, and visual assets.
- ML Analytics — keyword research, headline optimization, SEO recommendations, and performance prediction.
- Publishing Automation System (platform CMS + scheduling API) — format, host, and schedule the portfolio articles and distribution.
- Revenue Engine (optional) — to create a gated portfolio product or downloadable PDF for monetization and lead capture.
- (Optional) marketing-agent — prepare short social captions and email blurb for article promotion.

Week 1 action plan (day-by-day with specific steps, tools, and expected outcomes)

Day 1 — Kickoff, audience & topic selection (3 hours)
1. Define target audience and use case for the AI-Assisted Content Writing opportunity (e.g., SMB e‑commerce owners, SaaS marketing teams, freelance content buyers). Outcome: two short audience personas.
2. Use ML Analytics to run a quick landscape scan for content gaps and high-opportunity keywords in your niches. Deliverable: 6 ranked keyword/topic ideas with search intent and difficulty estimate.
   - Tool: ML Analytics — run “topic opportunity” report (API: /analytics/topic-opportunity).
3. Select 3 article topics from the top-ranked opportunities that demonstrate your AI-assisted capability (e.g., how-to, case study, best-practices).
   - Expected outcome: Finalized list of three article topics and working titles.

Day 2 — Create article briefs & outlines (3–4 hours)
1. For each topic, create a structured brief including target persona, goal, target keywords, suggested word count, required sections, tone of voice, CTA, and internal links.
   - Tool: content-creator agent — send brief template and request optimized outline (API: /agents/content-creator/create-brief).
2. Use ML Analytics to refine headlines and meta descriptions (A/B suggestions with predicted CTR).
   - Expected outcome: Three approved article briefs and two headline/meta options per article.

Day 3 — Drafting (4–6 hours)
1. Use the content-creator agent to generate full first drafts for each article based on the approved briefs. Request SEO-aware formatting (H1/H2s, internal link placeholders, meta).
   - Tool: content-creator agent (API: /agents/content-creator/generate-article).
   - Quality controls: specify minimum word counts (800–1,500 words) and require sources for any factual claims.
2. Internal review: quickly scan drafts for alignment with brand voice and factual accuracy. Mark revisions and track edits in the platform’s collaboration tool.
   - Expected outcome: Three first drafts uploaded into the platform’s editor with reviewer comments.

Day 4 — Editing & SEO optimization (3–4 hours)
1. Use the content-creator agent (or editing workflow) to implement revisions: tighten copy, improve transitions, ensure each article includes a clear CTA to your AI-assisted writing service.
2. Apply ML Analytics SEO suggestions: insert prioritized keywords, optimize H2s, meta title/description, and add structured data snippets if appropriate (e.g., article schema).
   - Tools: content-creator agent + ML Analytics (API calls for keyword placement suggestions).
3. Run a readability and plagiarism check using the platform’s built-in QA checks (native to editor).
   - Expected outcome: Three publication-ready article texts with SEO metadata and QA passed.

Day 5 — Visuals & assets (2–3 hours)
1. For each article, brief design-agent to create a hero image and thumbnail. Include brand color, style, and required dimensions.
   - Tool: design-agent + AI Content Studio (DALL·E 3/Stable Diffusion) — generate 2 variations per article.
   - API flow: call AI Content Studio with prompt from design-agent, receive images, and iterate once if needed.
2. Create optional downloadable PDFs (article + lead magnet format) using the platform’s export tool for use with Revenue Engine.
   - Expected outcome: 3 hero images, 3 thumbnails, and optional 3 downloadable PDFs.

Day 6 — Formatting, internal linking, and page creation (3 hours)
1. Use the Publishing Automation System to create portfolio pages or blog posts for each article. Include hero image, meta tags from Day 4, structured data, and internal links to service pages.
   - Tool: Publishing Automation System (CMS + scheduling API).
   - Automation: set canonical URLs, add ALT text for images, and enable Open Graph tags (auto-generated).
2. Add CTAs: contact form link, “Request a sample” or “Book a demo” button connected to your platform lead capture.
   - Expected outcome: 3 fully formatted portfolio article pages in draft state on your platform.

Day 7 — QA, scheduling, analytics setup, and handoff (2–3 hours)
1. Final QA: check mobile responsiveness, image load performance, accessibility alt texts, and link integrity.
2. Use ML Analytics to set performance tracking goals and add tracking tags (views, CTRs, contact conversions).
3. Schedule or publish the articles using the Publishing Automation System. If you prefer staged rollout, schedule timed publishing and automatic social/email distribution prepared by marketing-agent.
4. (Optional) Use Revenue Engine to create a gated “Portfolio Pack” product (bundle PDFs) or lead magnet with a payment/free-lead option, and connect it to your payments and CRM.
   - Expected outcome: 3 live or scheduled portfolio articles, analytics tracking configured, and a handoff document summarizing topics, keywords, assets, and CTAs.

Acceptance criteria (what “done” looks like)
- Three articles of 800–1,500 words each, polished and edited for voice and accuracy.
- Each article includes: H1/H2 structure, target keywords placed, meta title and description, hero image, thumbnail, internal CTA.
- All three articles are formatted in the platform CMS, scheduled or published, with ML Analytics tracking enabled.
- Design assets (hero images and thumbnails) completed via AI Content Studio and stored in the platform asset library.
- Documented briefs, drafts, and revision history in the collaboration workspace.
- Optional: Portfolio Pack configured in Revenue Engine with payment/lead capture settings.

Estimated time and resource allocation
- Total estimated hours: 18–26 developer/editor/designer hours across the week.
- Roles recommended: 1 content lead (works with content-creator), 1 editor (QA), 1 designer (design-agent), 1 marketing/admin (publishing & analytics).
- Cost-saving note: using internal content-creator, AI Content Studio, ML Analytics, and Publishing Automation avoids external subscriptions and manual integration overhead; API-driven workflows enable re-use for future scale.

API/automation suggestions (for repeatability)
- Automate brief -> draft -> edit -> publish pipeline with the following sequence:
  - POST /agents/content-creator/create-brief (input: persona, keywords)
  - POST /agents/content-creator/generate-article (input: brief ID)
  - GET /analytics/seo-suggestions?article_id=XYZ (returns keyword placement and meta recommendations)
  - POST /ai-content-studio/generate-image (input: prompt from design-agent)
  - POST /cms/create-post (input: article HTML, images, metadata)
  - POST /analytics/track-setup (input: post_id, tracking goals)
- This automation reduces manual handoffs and preserves consistency across articles.

Next steps after Week 1
- Monitor performance via ML Analytics for 2–4 weeks, then iterate topics and improved drafts.
- Use marketing-agent to create social/email campaigns from the articles.
- Convert top-performing article into a gated product via Revenue Engine to capture leads or generate revenue.

If you want, I can:
- Generate three topic/title options now based on ML Analytics keyword opportunities.
- Kick off the content-creator agent to create the first brief and draft a sample article.
Which would you like me to start with?

## Real Data Used
