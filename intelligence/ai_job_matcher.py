"""
AI Job Matcher - Intelligent Job Opportunity Scoring for AI-Completable Work
============================================================================

This module identifies and scores job opportunities based on their suitability
for completion using AI tools and automation. It focuses on finding jobs where
AI assistance provides a significant competitive advantage.

Key Features:
- Identifies AI-completable tasks in job descriptions
- Scores opportunities based on AI automation potential
- Generates AI-optimized resumes and proposals
- Tracks success rates for continuous improvement
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AIJobCategory(Enum):
    """Categories of jobs highly suitable for AI completion"""

    CONTENT_WRITING = "content_writing"
    DATA_ANALYSIS = "data_analysis"
    CODE_GENERATION = "code_generation"
    GRAPHIC_DESIGN = "graphic_design"
    RESEARCH = "research"
    TRANSLATION = "translation"
    TRANSCRIPTION = "transcription"
    VIRTUAL_ASSISTANT = "virtual_assistant"
    SEO_OPTIMIZATION = "seo_optimization"
    SOCIAL_MEDIA = "social_media"
    EMAIL_MARKETING = "email_marketing"
    CHATBOT_DEVELOPMENT = "chatbot_development"
    API_INTEGRATION = "api_integration"
    WEB_SCRAPING = "web_scraping"
    PROMPT_ENGINEERING = "prompt_engineering"


@dataclass
class AIJobMatch:
    """Represents a job opportunity matched for AI completion"""

    job_id: str
    title: str
    description: str
    category: AIJobCategory
    ai_score: float  # 0-1 score of AI suitability
    required_skills: List[str]
    ai_tools_applicable: List[str]
    estimated_completion_time: float  # hours
    budget: Optional[float] = None
    client_history: Optional[Dict] = None
    success_probability: float = 0.0
    recommended_approach: str = ""
    sample_deliverables: List[str] = field(default_factory=list)


class AIJobMatcher:
    """
    Intelligent matcher for identifying AI-completable job opportunities
    """

    def __init__(self):
        # Keywords that indicate AI-suitable jobs
        self.ai_keywords = {
            'content_writing': [
                'blog', 'article', 'content', 'copywriting', 'seo content',
                'product description', 'website copy', 'email copy', 'newsletter',
                'social media posts', 'press release', 'white paper'
            ],
            'data_analysis': [
                'data analysis', 'excel', 'spreadsheet', 'data entry', 'report',
                'dashboard', 'visualization', 'analytics', 'insights', 'metrics',
                'statistical analysis', 'data cleaning', 'csv', 'json'
            ],
            'code_generation': [
                'python script', 'automation', 'web scraping', 'api integration',
                'bot development', 'script writing', 'code review', 'debugging',
                'sql query', 'database', 'wordpress', 'javascript', 'react'
            ],
            'ai_specific': [
                'chatgpt', 'ai', 'machine learning', 'prompt engineering',
                'llm', 'gpt', 'ai assistant', 'chatbot', 'automation with ai',
                'ai content', 'ai writing', 'ai analysis'
            ],
            'research': [
                'research', 'market research', 'competitor analysis', 'industry research',
                'academic research', 'literature review', 'data collection', 'survey'
            ],
            'translation': [
                'translation', 'localization', 'transcreation', 'subtitle',
                'multilingual', 'language', 'interpreter'
            ]
        }

        # AI tools that can be used for different job types
        self.ai_tools_map = {
            AIJobCategory.CONTENT_WRITING: ['ChatGPT', 'Claude', 'Jasper', 'Copy.ai'],
            AIJobCategory.DATA_ANALYSIS: ['Python', 'Pandas', 'ChatGPT Code Interpreter', 'Excel with AI'],
            AIJobCategory.CODE_GENERATION: ['GitHub Copilot', 'ChatGPT', 'Claude', 'Replit AI'],
            AIJobCategory.GRAPHIC_DESIGN: ['DALL-E', 'Midjourney', 'Stable Diffusion', 'Canva AI'],
            AIJobCategory.RESEARCH: ['Perplexity', 'ChatGPT', 'Claude', 'Google Scholar'],
            AIJobCategory.TRANSLATION: ['DeepL', 'ChatGPT', 'Google Translate API'],
            AIJobCategory.VIRTUAL_ASSISTANT: ['ChatGPT', 'Claude', 'Zapier', 'Make.com'],
            AIJobCategory.SEO_OPTIMIZATION: ['Surfer SEO', 'ChatGPT', 'SEMrush', 'Ahrefs'],
            AIJobCategory.SOCIAL_MEDIA: ['Buffer AI', 'Hootsuite AI', 'ChatGPT', 'Canva'],
            AIJobCategory.CHATBOT_DEVELOPMENT: ['Dialogflow', 'Rasa', 'ChatGPT API', 'Botpress'],
            AIJobCategory.WEB_SCRAPING: ['Python', 'Selenium', 'Beautiful Soup', 'Scrapy'],
            AIJobCategory.PROMPT_ENGINEERING: ['ChatGPT', 'Claude', 'Prompt testing tools']
        }

        # Success indicators in job descriptions
        self.positive_indicators = [
            'remote', 'flexible', 'asap', 'urgent', 'quick turnaround',
            'ongoing', 'long-term', 'regular work', 'bulk', 'multiple',
            'simple', 'straightforward', 'basic', 'entry-level'
        ]

        # Warning indicators
        self.negative_indicators = [
            'on-site', 'in-person', 'local only', 'phone calls required',
            'video calls mandatory', 'complex', 'expert only', 'senior',
            '10+ years experience', 'portfolio required', 'samples required'
        ]

    def analyze_job(self, job_data: Dict[str, Any]) -> Optional[AIJobMatch]:
        """
        Analyze a job posting to determine AI suitability

        Args:
            job_data: Dictionary containing job information

        Returns:
            AIJobMatch object if suitable, None otherwise
        """
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        skills = job_data.get('skills', [])
        budget = job_data.get('budget')

        # Combine text for analysis
        full_text = f"{title} {description} {' '.join(skills)}".lower()

        # Determine job category
        category = self._categorize_job(full_text)
        if not category:
            return None

        # Calculate AI suitability score
        ai_score = self._calculate_ai_score(full_text, category)

        if ai_score < 0.5:  # Threshold for AI suitability
            return None

        # Get applicable AI tools
        ai_tools = self.ai_tools_map.get(category, [])

        # Estimate completion time
        completion_time = self._estimate_completion_time(description, category)

        # Calculate success probability
        success_prob = self._calculate_success_probability(job_data, ai_score)

        # Generate recommended approach
        approach = self._generate_approach(category, job_data)

        # Create sample deliverables
        samples = self._generate_sample_deliverables(category)

        return AIJobMatch(
            job_id=job_data.get('id', 'unknown'),
            title=job_data.get('title', ''),
            description=job_data.get('description', ''),
            category=category,
            ai_score=ai_score,
            required_skills=skills,
            ai_tools_applicable=ai_tools,
            estimated_completion_time=completion_time,
            budget=budget,
            client_history=job_data.get('client_history'),
            success_probability=success_prob,
            recommended_approach=approach,
            sample_deliverables=samples
        )

    def _categorize_job(self, text: str) -> Optional[AIJobCategory]:
        """Categorize job based on keywords"""

        category_scores = {}

        # Check for content writing
        if any(kw in text for kw in self.ai_keywords['content_writing']):
            category_scores[AIJobCategory.CONTENT_WRITING] = sum(
                1 for kw in self.ai_keywords['content_writing'] if kw in text
            )

        # Check for data analysis
        if any(kw in text for kw in self.ai_keywords['data_analysis']):
            category_scores[AIJobCategory.DATA_ANALYSIS] = sum(
                1 for kw in self.ai_keywords['data_analysis'] if kw in text
            )

        # Check for code generation
        if any(kw in text for kw in self.ai_keywords['code_generation']):
            category_scores[AIJobCategory.CODE_GENERATION] = sum(
                1 for kw in self.ai_keywords['code_generation'] if kw in text
            )

        # Check for research
        if any(kw in text for kw in self.ai_keywords['research']):
            category_scores[AIJobCategory.RESEARCH] = sum(
                1 for kw in self.ai_keywords['research'] if kw in text
            )

        # Check for translation
        if any(kw in text for kw in self.ai_keywords['translation']):
            category_scores[AIJobCategory.TRANSLATION] = sum(
                1 for kw in self.ai_keywords['translation'] if kw in text
            )

        # Special boost for AI-specific mentions
        if any(kw in text for kw in self.ai_keywords['ai_specific']):
            # This is definitely AI-suitable
            if category_scores:
                # Boost the highest scoring category
                max_cat = max(category_scores, key=category_scores.get)
                category_scores[max_cat] += 5
            else:
                # Default to content writing for AI jobs
                category_scores[AIJobCategory.CONTENT_WRITING] = 3

        # Additional category checks
        if 'virtual assistant' in text or 'va' in text:
            category_scores[AIJobCategory.VIRTUAL_ASSISTANT] = 3

        if 'seo' in text or 'search engine' in text:
            category_scores[AIJobCategory.SEO_OPTIMIZATION] = 3

        if 'social media' in text or 'instagram' in text or 'facebook' in text:
            category_scores[AIJobCategory.SOCIAL_MEDIA] = 3

        if 'chatbot' in text or 'conversational ai' in text:
            category_scores[AIJobCategory.CHATBOT_DEVELOPMENT] = 4

        if 'scraping' in text or 'scrape' in text or 'crawler' in text:
            category_scores[AIJobCategory.WEB_SCRAPING] = 4

        if 'prompt' in text and ('engineer' in text or 'design' in text):
            category_scores[AIJobCategory.PROMPT_ENGINEERING] = 5

        if not category_scores:
            return None

        return max(category_scores, key=category_scores.get)

    def _calculate_ai_score(self, text: str, category: AIJobCategory) -> float:
        """Calculate how suitable this job is for AI completion"""

        score = 0.5  # Base score

        # Boost for AI-specific mentions
        ai_mentions = sum(1 for kw in self.ai_keywords['ai_specific'] if kw in text)
        score += min(0.3, ai_mentions * 0.1)

        # Check positive indicators
        positive_count = sum(1 for ind in self.positive_indicators if ind in text)
        score += min(0.2, positive_count * 0.05)

        # Check negative indicators
        negative_count = sum(1 for ind in self.negative_indicators if ind in text)
        score -= min(0.3, negative_count * 0.1)

        # Category-specific boosts
        if category in [AIJobCategory.CONTENT_WRITING, AIJobCategory.DATA_ANALYSIS,
                       AIJobCategory.CODE_GENERATION, AIJobCategory.PROMPT_ENGINEERING]:
            score += 0.1  # These are particularly good for AI

        # Specific keyword boosts
        if 'bulk' in text or 'multiple' in text:
            score += 0.1  # Good for automation

        if 'template' in text or 'similar to' in text:
            score += 0.1  # Repetitive work is good for AI

        if 'creative' not in text and 'unique voice' not in text:
            score += 0.05  # Less creative work is easier for AI

        return max(0.0, min(1.0, score))

    def _estimate_completion_time(self, description: str, category: AIJobCategory) -> float:
        """Estimate hours needed to complete with AI assistance"""

        word_count = len(description.split())

        # Base time by category
        base_times = {
            AIJobCategory.CONTENT_WRITING: 1.0,
            AIJobCategory.DATA_ANALYSIS: 2.0,
            AIJobCategory.CODE_GENERATION: 2.0,
            AIJobCategory.GRAPHIC_DESIGN: 1.5,
            AIJobCategory.RESEARCH: 2.0,
            AIJobCategory.TRANSLATION: 0.5,
            AIJobCategory.VIRTUAL_ASSISTANT: 1.0,
            AIJobCategory.SEO_OPTIMIZATION: 1.5,
            AIJobCategory.SOCIAL_MEDIA: 0.5,
            AIJobCategory.CHATBOT_DEVELOPMENT: 3.0,
            AIJobCategory.WEB_SCRAPING: 2.0,
            AIJobCategory.PROMPT_ENGINEERING: 1.0
        }

        base_time = base_times.get(category, 2.0)

        # Adjust based on description length (complexity indicator)
        if word_count > 500:
            base_time *= 1.5
        elif word_count > 300:
            base_time *= 1.2

        # Check for bulk/multiple indicators
        if 'bulk' in description or 'multiple' in description:
            base_time *= 2.0

        return base_time

    def _calculate_success_probability(self, job_data: Dict, ai_score: float) -> float:
        """Calculate probability of successfully completing and getting paid"""

        prob = ai_score * 0.5  # Start with AI score influence

        # Client history factors
        client = job_data.get('client_history', {})
        if client:
            hire_rate = client.get('hire_rate', 0)
            prob += min(0.2, hire_rate / 100 * 0.3)

            # Good payment history
            if client.get('payment_verified', False):
                prob += 0.1

            # Review score
            review_score = client.get('review_score', 0)
            if review_score > 4.5:
                prob += 0.1

        # Budget factors
        budget = job_data.get('budget', 0)
        if budget and budget > 100:
            prob += 0.1  # Decent budget

        # Competition factors
        proposals = job_data.get('proposal_count', 0)
        if proposals < 5:
            prob += 0.15  # Low competition
        elif proposals < 15:
            prob += 0.05  # Medium competition

        return min(1.0, prob)

    def _generate_approach(self, category: AIJobCategory, job_data: Dict) -> str:
        """Generate recommended approach for this job"""

        approaches = {
            AIJobCategory.CONTENT_WRITING:
                "Use ChatGPT/Claude to generate initial drafts, then refine with "
                "human editing for tone and brand voice. Deliver in phases for feedback.",

            AIJobCategory.DATA_ANALYSIS:
                "Use Python with pandas for data processing, ChatGPT for insights "
                "generation, and create visualizations with matplotlib/seaborn.",

            AIJobCategory.CODE_GENERATION:
                "Leverage GitHub Copilot or ChatGPT for initial code generation, "
                "test thoroughly, and provide documentation.",

            AIJobCategory.RESEARCH:
                "Use Perplexity for initial research, ChatGPT for synthesis, "
                "and provide citations for all claims.",

            AIJobCategory.PROMPT_ENGINEERING:
                "Design and test prompts iteratively, provide examples of outputs, "
                "and create documentation for prompt usage.",

            AIJobCategory.VIRTUAL_ASSISTANT:
                "Set up automation workflows with Zapier/Make, use ChatGPT for "
                "communication drafts, and provide clear SOPs.",

            AIJobCategory.WEB_SCRAPING:
                "Build robust scrapers with error handling, use rotating proxies "
                "if needed, and deliver clean, structured data.",

            AIJobCategory.CHATBOT_DEVELOPMENT:
                "Use Dialogflow or ChatGPT API for NLP, implement fallback logic, "
                "and provide testing documentation.",
        }

        base_approach = approaches.get(
            category,
            "Use appropriate AI tools to complete the task efficiently, "
            "maintain communication, and deliver high-quality results."
        )

        # Add urgency note if applicable
        if 'urgent' in job_data.get('description', '').lower():
            base_approach += " Priority: Quick turnaround - aim to deliver within 24 hours."

        return base_approach

    def _generate_sample_deliverables(self, category: AIJobCategory) -> List[str]:
        """Generate list of sample deliverables for the job category"""

        deliverables = {
            AIJobCategory.CONTENT_WRITING: [
                "SEO-optimized blog post (1500+ words)",
                "Meta description and title tags",
                "Content calendar for future posts",
                "Revision based on feedback"
            ],
            AIJobCategory.DATA_ANALYSIS: [
                "Cleaned dataset in CSV/Excel format",
                "Analysis report with insights",
                "Interactive dashboard (if applicable)",
                "Python scripts for reproducibility"
            ],
            AIJobCategory.CODE_GENERATION: [
                "Well-commented source code",
                "README with installation instructions",
                "Test cases and examples",
                "API documentation (if applicable)"
            ],
            AIJobCategory.PROMPT_ENGINEERING: [
                "Tested prompt library",
                "Performance metrics for each prompt",
                "Usage documentation",
                "Example outputs"
            ],
            AIJobCategory.WEB_SCRAPING: [
                "Scraper script/tool",
                "Extracted data in requested format",
                "Error logs and handling",
                "Usage instructions"
            ]
        }

        return deliverables.get(category, ["Completed deliverables as per requirements"])

    def rank_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[AIJobMatch]:
        """
        Rank multiple opportunities by AI suitability

        Args:
            opportunities: List of job opportunities to analyze

        Returns:
            Sorted list of AIJobMatch objects (best first)
        """
        matches = []

        for opp in opportunities:
            match = self.analyze_job(opp)
            if match:
                matches.append(match)

        # Sort by combined score (AI score + success probability)
        matches.sort(key=lambda x: (x.ai_score * 0.6 + x.success_probability * 0.4), reverse=True)

        return matches

    def generate_proposal_template(self, job_match: AIJobMatch) -> str:
        """
        Generate a proposal template optimized for the job

        Args:
            job_match: The analyzed job match

        Returns:
            Proposal template string
        """
        template = f"""
Hi there!

I'm excited about your {job_match.category.value.replace('_', ' ')} project. With my expertise in AI-powered solutions and {', '.join(job_match.ai_tools_applicable[:2])}, I can deliver exceptional results quickly.

**Why I'm the Perfect Fit:**
✅ Specialized in {job_match.category.value.replace('_', ' ')}
✅ Quick turnaround (estimated {job_match.estimated_completion_time} hours)
✅ Using cutting-edge AI tools for superior quality
✅ 100% satisfaction guarantee

**My Approach:**
{job_match.recommended_approach}

**What You'll Receive:**
{chr(10).join('• ' + d for d in job_match.sample_deliverables[:3])}

**Timeline:** I can start immediately and deliver within 24-48 hours.

**Investment:** ${job_match.budget if job_match.budget else '[Your Budget]'}

I'm confident I can exceed your expectations. Let's discuss your specific requirements!

Best regards,
[Your Name]

P.S. I'm online now and ready to start immediately!
"""
        return template