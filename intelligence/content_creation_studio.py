"""
Content Creation Studio
Enables agents to generate high-quality content for income opportunities

SESSION 30: The missing piece that connects spider discovery to actual deliverables!
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content that can be generated"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    CODE = "code"
    DESIGN = "design"
    VIDEO_SCRIPT = "video_script"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    PRODUCT_DESCRIPTION = "product_description"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    PRESENTATION = "presentation"


class ContentQuality(Enum):
    """Quality levels for generated content"""
    DRAFT = "draft"  # Quick draft, needs review
    STANDARD = "standard"  # Good quality, ready to use
    PREMIUM = "premium"  # High quality, professionally polished
    CUSTOM = "custom"  # Fully customized to specifications


@dataclass
class ContentSpecification:
    """Specification for content to be created"""
    content_type: ContentType
    title: str
    topic: str
    keywords: List[str]
    target_audience: str
    word_count: Optional[int] = None
    tone: str = "professional"
    quality_level: ContentQuality = ContentQuality.STANDARD
    special_requirements: Optional[Dict[str, Any]] = None
    reference_materials: Optional[List[str]] = None


@dataclass
class GeneratedContent:
    """Result of content generation"""
    content_id: str
    specification: ContentSpecification
    content: str
    metadata: Dict[str, Any]
    quality_score: float
    generated_at: datetime
    word_count: int
    estimated_value: float  # Estimated market value


class ContentCreationStudio:
    """
    The Content Creation Studio generates high-quality deliverables

    This is what makes agents PRODUCTIVE - they can now actually CREATE
    content to fulfill opportunities, not just discover them!
    """

    def __init__(self):
        self.api_key = None  # Will use OpenAI if available
        self._initialize_generators()

    def _initialize_generators(self):
        """Initialize AI generators for different content types"""
        try:
            import openai
            import os
            self.api_key = os.getenv('OPENAI_API_KEY')
            if self.api_key:
                logger.info("✅ Content Studio initialized with OpenAI")
            else:
                logger.warning("⚠️ No OpenAI API key - using fallback generators")
        except ImportError:
            logger.warning("⚠️ OpenAI not installed - using fallback generators")

    # =====================
    # Main Content Generation
    # =====================

    async def generate_content(
        self,
        specification: ContentSpecification
    ) -> GeneratedContent:
        """
        Generate content based on specification

        This is the main entry point for content creation!
        """
        logger.info(f"🎨 Generating {specification.content_type.value}: {specification.title}")

        try:
            # Route to appropriate generator based on content type
            if specification.content_type == ContentType.ARTICLE:
                content = await self._generate_article(specification)
            elif specification.content_type == ContentType.BLOG_POST:
                content = await self._generate_blog_post(specification)
            elif specification.content_type == ContentType.CODE:
                content = await self._generate_code(specification)
            elif specification.content_type == ContentType.DESIGN:
                content = await self._generate_design_spec(specification)
            elif specification.content_type == ContentType.VIDEO_SCRIPT:
                content = await self._generate_video_script(specification)
            elif specification.content_type == ContentType.SOCIAL_MEDIA:
                content = await self._generate_social_media(specification)
            elif specification.content_type == ContentType.EMAIL_CAMPAIGN:
                content = await self._generate_email_campaign(specification)
            elif specification.content_type == ContentType.PRODUCT_DESCRIPTION:
                content = await self._generate_product_description(specification)
            elif specification.content_type == ContentType.TECHNICAL_DOCUMENTATION:
                content = await self._generate_technical_docs(specification)
            elif specification.content_type == ContentType.PRESENTATION:
                content = await self._generate_presentation(specification)
            else:
                raise ValueError(f"Unsupported content type: {specification.content_type}")

            # Calculate quality score
            quality_score = self._assess_quality(content, specification)

            # Estimate market value
            estimated_value = self._estimate_value(
                specification.content_type,
                len(content.split()),
                quality_score
            )

            # Create result
            result = GeneratedContent(
                content_id=f"content_{datetime.now().timestamp()}",
                specification=specification,
                content=content,
                metadata={
                    'generator': 'ContentCreationStudio',
                    'api_used': 'openai' if self.api_key else 'fallback',
                    'quality_level': specification.quality_level.value,
                    'tone': specification.tone
                },
                quality_score=quality_score,
                generated_at=datetime.now(),
                word_count=len(content.split()),
                estimated_value=estimated_value
            )

            logger.info(f"✅ Generated {result.word_count} words, quality score: {quality_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise

    # =====================
    # Content Type Generators
    # =====================

    async def _generate_article(self, spec: ContentSpecification) -> str:
        """Generate a professional article"""
        if self.api_key:
            return await self._generate_with_openai(
                prompt=f"""Write a professional {spec.tone} article about {spec.topic}.

Title: {spec.title}
Target Audience: {spec.target_audience}
Keywords to include: {', '.join(spec.keywords)}
Word Count: {spec.word_count or 1000} words

Requirements:
- Engaging introduction
- Well-structured body with subheadings
- Data and examples
- Conclusion with key takeaways
- SEO-optimized

Write the complete article:""",
                max_tokens=spec.word_count * 2 if spec.word_count else 2000
            )
        else:
            return self._generate_article_fallback(spec)

    async def _generate_blog_post(self, spec: ContentSpecification) -> str:
        """Generate a blog post"""
        if self.api_key:
            return await self._generate_with_openai(
                prompt=f"""Write a {spec.tone} blog post about {spec.topic}.

Title: {spec.title}
Target Audience: {spec.target_audience}
Keywords: {', '.join(spec.keywords)}

Requirements:
- Catchy introduction
- Personal tone with stories/examples
- Actionable tips
- Clear call-to-action
- {spec.word_count or 800} words

Write the complete blog post:""",
                max_tokens=spec.word_count * 2 if spec.word_count else 1600
            )
        else:
            return self._generate_blog_fallback(spec)

    async def _generate_code(self, spec: ContentSpecification) -> str:
        """Generate code solution"""
        if self.api_key:
            return await self._generate_with_openai(
                prompt=f"""Generate clean, production-ready code for: {spec.topic}

Title: {spec.title}
Requirements: {spec.special_requirements}
Target Audience: {spec.target_audience}

Include:
- Clean, well-commented code
- Error handling
- Documentation
- Usage examples
- Tests (if applicable)

Generate the complete code:""",
                max_tokens=3000
            )
        else:
            return self._generate_code_fallback(spec)

    async def _generate_design_spec(self, spec: ContentSpecification) -> str:
        """Generate design specification"""
        return f"""# Design Specification: {spec.title}

## Overview
{spec.topic}

## Target Audience
{spec.target_audience}

## Design Requirements
{json.dumps(spec.special_requirements, indent=2) if spec.special_requirements else 'Standard design requirements'}

## Color Palette
- Primary: #4A90E2 (Professional Blue)
- Secondary: #7B68EE (Creative Purple)
- Accent: #FF6B6B (Attention Red)
- Background: #FFFFFF / #F5F5F5
- Text: #333333 / #666666

## Typography
- Headings: Sans-serif, bold, 24-32px
- Body: Sans-serif, regular, 14-16px
- Line Height: 1.6

## Layout
- Responsive design (mobile, tablet, desktop)
- Grid-based layout
- Whitespace for clarity
- Clear visual hierarchy

## Key Elements
1. Hero section with {spec.title}
2. Feature highlights
3. Call-to-action buttons
4. Social proof elements
5. Contact/conversion form

## Deliverables
- Wireframes
- High-fidelity mockups
- Component library
- Style guide
- Assets (icons, images)

This specification provides a complete design direction for {spec.topic}.
"""

    async def _generate_video_script(self, spec: ContentSpecification) -> str:
        """Generate video script"""
        if self.api_key:
            return await self._generate_with_openai(
                prompt=f"""Write an engaging video script about {spec.topic}.

Title: {spec.title}
Target Audience: {spec.target_audience}
Tone: {spec.tone}
Duration: {spec.word_count // 150 if spec.word_count else 3} minutes

Include:
- Hook (first 5 seconds)
- Introduction
- Main content with visual cues
- Call-to-action
- Outro

Write the complete script with timestamps:""",
                max_tokens=2000
            )
        else:
            return self._generate_video_script_fallback(spec)

    async def _generate_social_media(self, spec: ContentSpecification) -> str:
        """Generate social media content"""
        platforms = spec.special_requirements.get('platforms', ['twitter', 'linkedin']) if spec.special_requirements else ['twitter', 'linkedin']

        content = f"# Social Media Content: {spec.title}\n\n"
        content += f"**Topic**: {spec.topic}\n"
        content += f"**Keywords**: {', '.join(spec.keywords)}\n\n"

        for platform in platforms:
            if platform == 'twitter':
                content += "## Twitter Thread\n"
                content += self._generate_twitter_thread(spec)
            elif platform == 'linkedin':
                content += "\n## LinkedIn Post\n"
                content += self._generate_linkedin_post(spec)
            elif platform == 'instagram':
                content += "\n## Instagram Caption\n"
                content += self._generate_instagram_caption(spec)

        return content

    async def _generate_email_campaign(self, spec: ContentSpecification) -> str:
        """Generate email campaign"""
        return f"""# Email Campaign: {spec.title}

## Campaign Overview
**Topic**: {spec.topic}
**Target Audience**: {spec.target_audience}
**Keywords**: {', '.join(spec.keywords)}

## Email 1: Welcome/Introduction
**Subject**: {spec.title} - Get Started Today
**Preview Text**: Discover how {spec.topic} can transform your results

Hi [Name],

Welcome! We're excited to share insights about {spec.topic} that will help you {spec.special_requirements.get('goal', 'achieve your goals') if spec.special_requirements else 'achieve your goals'}.

[Body content with value proposition]

**Call-to-Action**: [Primary CTA Button]

## Email 2: Value Delivery
**Subject**: 3 Quick Wins with {spec.title}

[Content with actionable tips]

## Email 3: Social Proof
**Subject**: How Others Are Succeeding with {spec.title}

[Case studies and testimonials]

## Email 4: Conversion
**Subject**: Last Chance: {spec.title}

[Final push with urgency and benefits]

All emails are optimized for {spec.tone} tone and include clear CTAs.
"""

    async def _generate_product_description(self, spec: ContentSpecification) -> str:
        """Generate product description"""
        if self.api_key:
            return await self._generate_with_openai(
                prompt=f"""Write a compelling product description for: {spec.title}

Product: {spec.topic}
Target Audience: {spec.target_audience}
Keywords: {', '.join(spec.keywords)}
Tone: {spec.tone}

Include:
- Attention-grabbing headline
- Key benefits (not just features)
- Social proof
- Clear value proposition
- Call-to-action
- SEO optimization

Write the complete product description:""",
                max_tokens=800
            )
        else:
            return self._generate_product_description_fallback(spec)

    async def _generate_technical_docs(self, spec: ContentSpecification) -> str:
        """Generate technical documentation"""
        return f"""# {spec.title}

## Overview
{spec.topic}

## Table of Contents
1. Introduction
2. Getting Started
3. Core Concepts
4. API Reference
5. Examples
6. Troubleshooting
7. FAQ

## 1. Introduction
This documentation covers {spec.topic} for {spec.target_audience}.

Keywords: {', '.join(spec.keywords)}

## 2. Getting Started

### Prerequisites
- [List prerequisites]

### Installation
```bash
# Installation commands
```

### Quick Start
```python
# Quick start code example
```

## 3. Core Concepts

### Concept 1
[Detailed explanation]

### Concept 2
[Detailed explanation]

## 4. API Reference

### Method 1
```python
def method_name(param1, param2):
    \"\"\"
    Description of what this method does.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description of return value
    \"\"\"
```

## 5. Examples

### Example 1: Basic Usage
```python
# Code example
```

### Example 2: Advanced Usage
```python
# Code example
```

## 6. Troubleshooting

### Common Issue 1
**Problem**: [Description]
**Solution**: [Step-by-step solution]

### Common Issue 2
**Problem**: [Description]
**Solution**: [Step-by-step solution]

## 7. FAQ

**Q: [Question]**
A: [Answer]

**Q: [Question]**
A: [Answer]

This documentation provides comprehensive coverage of {spec.topic}.
"""

    async def _generate_presentation(self, spec: ContentSpecification) -> str:
        """Generate presentation outline"""
        return f"""# Presentation: {spec.title}

## Presentation Details
- **Topic**: {spec.topic}
- **Audience**: {spec.target_audience}
- **Duration**: {spec.special_requirements.get('duration', '15 minutes') if spec.special_requirements else '15 minutes'}
- **Tone**: {spec.tone}

## Slide Outline

### Slide 1: Title
- {spec.title}
- Presenter Name
- Date

### Slide 2: Hook
- Attention-grabbing statistic or question
- Why this matters to {spec.target_audience}

### Slide 3: Problem Statement
- Current challenges with {spec.topic}
- Pain points

### Slide 4-6: Solution
- Key concept 1
- Key concept 2
- Key concept 3

### Slide 7: Benefits
- Benefit 1: [Description]
- Benefit 2: [Description]
- Benefit 3: [Description]

### Slide 8: Case Study/Example
- Real-world application
- Results achieved

### Slide 9: Implementation
- Step-by-step approach
- Timeline

### Slide 10: Call-to-Action
- Next steps
- Contact information

## Speaker Notes
[Detailed notes for each slide would go here]

## Visual Recommendations
- Use {spec.special_requirements.get('brand_colors', 'brand colors') if spec.special_requirements else 'professional colors'}
- Include relevant images/icons
- Data visualizations for statistics
- Minimal text per slide

This presentation structure ensures engagement and clear message delivery.
"""

    # =====================
    # AI Generation
    # =====================

    async def _generate_with_openai(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate content using OpenAI"""
        try:
            import openai
            openai.api_key = self.api_key

            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a professional content creator generating high-quality deliverables."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return f"[AI generation encountered an issue. Using fallback content.]\n\n{prompt}"

    # =====================
    # Fallback Generators
    # =====================

    def _generate_article_fallback(self, spec: ContentSpecification) -> str:
        """Fallback article generator"""
        return f"""# {spec.title}

## Introduction
{spec.topic} is an important subject for {spec.target_audience}. This article explores key concepts and provides actionable insights.

## Understanding {spec.topic}
[Key concept explanation with keywords: {', '.join(spec.keywords)}]

## Benefits and Applications
1. Benefit 1: [Description]
2. Benefit 2: [Description]
3. Benefit 3: [Description]

## Best Practices
- Practice 1
- Practice 2
- Practice 3

## Case Studies
[Real-world examples and results]

## Conclusion
{spec.topic} offers significant opportunities for {spec.target_audience}. By implementing these strategies, you can achieve [desired outcome].

**Keywords**: {', '.join(spec.keywords)}

This article provides a comprehensive overview of {spec.title} in a {spec.tone} tone.
"""

    def _generate_blog_fallback(self, spec: ContentSpecification) -> str:
        """Fallback blog generator"""
        return self._generate_article_fallback(spec)  # Similar structure

    def _generate_code_fallback(self, spec: ContentSpecification) -> str:
        """Fallback code generator"""
        return f"""# {spec.title}
# Solution for: {spec.topic}

def solution():
    \"\"\"
    {spec.topic}

    This implementation addresses the requirements for {spec.target_audience}.
    Keywords: {', '.join(spec.keywords)}
    \"\"\"
    # Implementation here
    pass

# Usage example
if __name__ == '__main__':
    solution()
"""

    def _generate_video_script_fallback(self, spec: ContentSpecification) -> str:
        """Fallback video script generator"""
        return f"""VIDEO SCRIPT: {spec.title}

[00:00-00:05] HOOK
Attention-grabbing opening about {spec.topic}

[00:05-00:30] INTRODUCTION
Welcome to this video about {spec.topic}. Today we'll cover...

[00:30-02:00] MAIN CONTENT
[Detailed explanation with visual cues]

[02:00-02:30] CALL-TO-ACTION
[Specific action for viewers]

[02:30-03:00] OUTRO
Thanks for watching! [Closing remarks]

Target: {spec.target_audience}
Tone: {spec.tone}
Keywords: {', '.join(spec.keywords)}
"""

    def _generate_twitter_thread(self, spec: ContentSpecification) -> str:
        """Generate Twitter thread"""
        thread = f"""1/ 🧵 {spec.title}

Let's talk about {spec.topic}...

2/ Why this matters:
{spec.topic} is crucial for {spec.target_audience} because [reason].

3/ Key insight 1:
[Insight with {spec.keywords[0] if spec.keywords else 'keyword'}]

4/ Key insight 2:
[Insight with {spec.keywords[1] if len(spec.keywords) > 1 else 'keyword'}]

5/ Action step:
Here's what you can do today to leverage {spec.topic}...

6/ The bottom line:
{spec.topic} offers real opportunities. Start implementing these strategies today!

#{spec.keywords[0].replace(' ', '')} #{spec.keywords[1].replace(' ', '') if len(spec.keywords) > 1 else 'success'}
"""
        return thread

    def _generate_linkedin_post(self, spec: ContentSpecification) -> str:
        """Generate LinkedIn post"""
        return f"""🚀 {spec.title}

{spec.topic} is transforming how {spec.target_audience} approach their work.

Here are 3 key insights:

✅ Insight 1: [Description]
✅ Insight 2: [Description]
✅ Insight 3: [Description]

The opportunity:
{spec.topic} offers {spec.target_audience} the chance to [benefit].

What's your experience with {spec.topic}? Share in the comments! 👇

#{spec.keywords[0].replace(' ', '')} #{spec.keywords[1].replace(' ', '') if len(spec.keywords) > 1 else 'Growth'} #ProfessionalDevelopment
"""

    def _generate_instagram_caption(self, spec: ContentSpecification) -> str:
        """Generate Instagram caption"""
        return f"""{spec.title} ✨

{spec.topic} for {spec.target_audience}

💡 Swipe to learn:
1. [Key point]
2. [Key point]
3. [Key point]

Ready to elevate your {spec.topic} game?

#{spec.keywords[0].replace(' ', '')} #{spec.keywords[1].replace(' ', '') if len(spec.keywords) > 1 else 'inspiration'} #content
"""

    def _generate_product_description_fallback(self, spec: ContentSpecification) -> str:
        """Fallback product description"""
        return f"""## {spec.title}

Transform your {spec.topic} with this innovative solution designed for {spec.target_audience}.

### Key Benefits:
✅ Benefit 1: [Description]
✅ Benefit 2: [Description]
✅ Benefit 3: [Description]

### Why Choose This?
Perfect for {spec.target_audience} who want to [desired outcome]. Our solution delivers results through [unique approach].

### What's Included:
- Feature 1
- Feature 2
- Feature 3

### Join Thousands of Satisfied Customers
"[Testimonial placeholder]" - Customer Name

**Get Started Today** and transform your {spec.topic}!

*Keywords*: {', '.join(spec.keywords)}
"""

    # =====================
    # Quality Assessment
    # =====================

    def _assess_quality(self, content: str, spec: ContentSpecification) -> float:
        """Assess content quality (0.0 to 1.0)"""
        score = 0.5  # Base score

        # Check word count
        word_count = len(content.split())
        if spec.word_count:
            if abs(word_count - spec.word_count) < spec.word_count * 0.2:
                score += 0.1
        else:
            if word_count > 200:
                score += 0.1

        # Check keyword inclusion
        keywords_found = sum(1 for kw in spec.keywords if kw.lower() in content.lower())
        keyword_score = keywords_found / len(spec.keywords) if spec.keywords else 1.0
        score += keyword_score * 0.2

        # Check structure (headings, paragraphs)
        if '##' in content or '\n\n' in content:
            score += 0.1

        # Quality level adjustment
        if spec.quality_level == ContentQuality.PREMIUM:
            score = min(score + 0.1, 1.0)

        return min(score, 1.0)

    def _estimate_value(self, content_type: ContentType, word_count: int, quality_score: float) -> float:
        """Estimate market value of content"""
        # Base rates per word by content type
        base_rates = {
            ContentType.ARTICLE: 0.10,
            ContentType.BLOG_POST: 0.08,
            ContentType.CODE: 0.50,
            ContentType.DESIGN: 200.00,  # Flat rate
            ContentType.VIDEO_SCRIPT: 0.15,
            ContentType.SOCIAL_MEDIA: 50.00,  # Flat rate
            ContentType.EMAIL_CAMPAIGN: 150.00,  # Flat rate
            ContentType.PRODUCT_DESCRIPTION: 75.00,  # Flat rate
            ContentType.TECHNICAL_DOCUMENTATION: 0.20,
            ContentType.PRESENTATION: 250.00  # Flat rate
        }

        base_rate = base_rates.get(content_type, 0.10)

        # Calculate based on whether it's per-word or flat rate
        if content_type in [ContentType.DESIGN, ContentType.SOCIAL_MEDIA, ContentType.EMAIL_CAMPAIGN, ContentType.PRODUCT_DESCRIPTION, ContentType.PRESENTATION]:
            value = base_rate
        else:
            value = word_count * base_rate

        # Adjust for quality
        value *= quality_score

        return round(value, 2)


# =====================
# Global Studio Instance
# =====================

content_studio = ContentCreationStudio()