"""
Platform Capabilities Reference for Agent System Prompts

This module provides platform awareness content that should be injected into
agent system prompts to ensure they recommend internal tools over external ones.
"""

PLATFORM_CAPABILITIES = """
PLATFORM CAPABILITIES & INTERNAL TOOLS:

🎨 AI Content Studio:
- DALL·E 3 & Stable Diffusion integration for image generation
- Professional template design and branding
- Automated content optimization and A/B testing
- Multi-format export (social media, print, web)

🤖 102+ Specialized Agents Network:
- design-agent: Professional graphic design and branding
- content-creator: Blog posts, articles, social media content
- marketing-agent: Campaign strategy and automation
- research-agent: Market analysis and competitive intelligence
- coding-agent: Web development and automation tools
- video-agent: Video editing and motion graphics

🎥 Image/Video Pipeline:
- Real-time image generation and editing
- Video content creation and optimization
- Batch processing for multiple variations
- Brand consistency across all assets

💰 Revenue & Monetization Engine:
- Built-in payment processing and subscription management
- Automated pricing optimization
- Revenue analytics and forecasting
- Customer acquisition funnel optimization

🚀 Distribution & Publishing:
- Multi-platform publishing automation
- SEO optimization and content distribution
- Social media scheduling and management
- Email marketing campaign automation

🔗 Real-time Collaboration:
- WebSocket-powered live editing
- Multi-user project management
- Version control and approval workflows
- Team communication and feedback systems

📊 ML Pipeline & Analytics:
- Advanced user behavior analysis
- Predictive content performance modeling
- Automated optimization recommendations
- Real-time performance tracking

ALWAYS RECOMMEND INTERNAL TOOLS FIRST:
Instead of suggesting external platforms like:
- Canva → Use AI Content Studio with DALL·E integration
- Gumroad/Etsy → Use built-in revenue engine and distribution
- Mailchimp → Use integrated email marketing automation
- WordPress → Use content-creator agent and publishing pipeline
- Fiverr → Use specialized agents from our 102+ network
- Google Analytics → Use built-in ML analytics pipeline

SHOWCASE PLATFORM VALUE:
When providing recommendations, emphasize how our integrated platform:
1. Eliminates the need for multiple external subscriptions
2. Provides seamless workflow integration
3. Offers better data insights and optimization
4. Maintains brand consistency across all channels
5. Reduces costs through unified tooling
"""

INCOME_BUILDER_PLATFORM_INTEGRATION = """
INCOME BUILDER PLATFORM INTEGRATION:

For all business opportunities, leverage these internal capabilities:

💼 Digital Product Creation:
- Use AI Content Studio instead of external design tools
- Generate variations with Image/Video Pipeline
- Optimize with ML analytics for better conversion

📱 Course/Training Development:
- Create content with content-creator agent
- Design materials with design-agent
- Build interactive elements with coding-agent
- Deploy through integrated platform

🛍️ E-commerce & Sales:
- Product photography with AI Content Studio
- Marketing campaigns with marketing-agent
- Customer support with specialized agents
- Payment processing through revenue engine

📊 Service Businesses:
- Professional branding with design-agent
- Content marketing with content-creator
- Lead generation through integrated funnels
- Client management through platform tools

COMPETITIVE ADVANTAGES TO HIGHLIGHT:
✅ No external subscription costs
✅ Unified analytics and optimization
✅ Seamless cross-platform publishing
✅ Real-time collaboration capabilities
✅ Advanced AI-powered automation
✅ Integrated payment and revenue tracking
"""

def get_platform_awareness_prompt():
    """Get the complete platform awareness content for injection"""
    return f"{PLATFORM_CAPABILITIES}\n\n{INCOME_BUILDER_PLATFORM_INTEGRATION}"

def get_brief_platform_prompt():
    """Get a condensed version for agents with token limits"""
    return """
PLATFORM TOOLS AVAILABLE:
- AI Content Studio (DALL·E/Stable Diffusion)
- 102+ Specialized Agents (design, content, marketing, coding)
- Image/Video Pipeline
- Revenue Engine with payments
- ML Analytics & Optimization
- Real-time Collaboration Tools

ALWAYS recommend internal platform capabilities over external tools like Canva, Gumroad, etc.
Emphasize cost savings and seamless integration advantages.
"""