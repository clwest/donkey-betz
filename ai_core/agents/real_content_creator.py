"""
Real Content Creator Agent - Actually creates content that can be sold
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from ai_core.agents.agent_llm_integration import agent_llm_integration

logger = logging.getLogger(__name__)


class RealContentCreatorAgent:
    """
    Agent that creates REAL content for selling:
    - Blog posts
    - Technical documentation
    - Marketing copy
    - Social media content
    - Email templates

    All LLM calls route through ``agent_llm_integration.generate_for_agent``;
    the raw OpenAI client previously held in ``self.client`` was dead code
    (assigned but never read) and was removed in Session 1086 Tier 4 PR 2.
    """

    def __init__(self):
        self.created_content = []

    async def create_blog_post(self, topic: str, keywords: List[str], word_count: int = 800) -> Dict[str, Any]:
        """
        Create a real blog post that can be sold

        Args:
            topic: The topic to write about
            keywords: SEO keywords to include
            word_count: Target word count

        Returns:
            Dictionary with the created content
        """
        try:
            logger.info(f"📝 Creating real blog post about: {topic}")

            # Create a professional prompt
            prompt = f"""
            Write a professional, SEO-optimized blog post about: {topic}

            Requirements:
            - Target word count: {word_count} words
            - Include these keywords naturally: {', '.join(keywords)}
            - Use engaging headline and subheadings
            - Include introduction, body with 3-5 main points, and conclusion
            - Write in an informative, conversational tone
            - Make it valuable and actionable for readers
            - Format with markdown for easy publishing

            Create a blog post that is ready to publish and sell.
            """

            # Generate the content using GPT-5 Responses API
            result = await agent_llm_integration.generate_for_agent(
                agent_name="ContentCreator",
                prompt=f"You are a professional content writer creating high-quality, sellable content.\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="medium",
                verbosity="high",  # Content needs detail
                max_output_tokens=1500
            )

            if not result['success']:
                logger.error(f"LLM error creating blog post: {result.get('error')}")
                return None

            content = result['response']

            # Create metadata
            blog_post = {
                'type': 'blog_post',
                'title': self._extract_title(content),
                'content': content,
                'topic': topic,
                'keywords': keywords,
                'word_count': len(content.split()),
                'created_at': datetime.now().isoformat(),
                'value_estimate': self._estimate_content_value(word_count),
                'ready_to_sell': True,
                'format': 'markdown',
                'usage': result.get('usage', {})
            }

            # Save the content
            self._save_content(blog_post)
            self.created_content.append(blog_post)

            logger.info(f"✅ Created blog post: {blog_post['title']} ({blog_post['word_count']} words)")

            return blog_post

        except Exception as e:
            logger.error(f"Error creating blog post: {e}")
            return None

    async def create_technical_documentation(self, project: str, sections: List[str]) -> Dict[str, Any]:
        """
        Create technical documentation

        Args:
            project: The project to document
            sections: List of sections to include

        Returns:
            Technical documentation
        """
        try:
            logger.info(f"📚 Creating technical documentation for: {project}")

            prompt = f"""
            Create professional technical documentation for: {project}

            Include these sections:
            {chr(10).join(f'- {section}' for section in sections)}

            Requirements:
            - Clear, concise technical writing
            - Include code examples where relevant
            - Use proper formatting and structure
            - Make it comprehensive and professional
            - Add installation/setup instructions
            - Include troubleshooting section

            Create documentation that developers would pay for.
            """

            result = await agent_llm_integration.generate_for_agent(
                agent_name="ContentCreator",
                prompt=f"You are a technical writer creating professional documentation.\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="medium",
                verbosity="high",
                max_output_tokens=2000
            )

            if not result['success']:
                logger.error(f"LLM error creating documentation: {result.get('error')}")
                return None

            content = result['response']

            documentation = {
                'type': 'technical_documentation',
                'project': project,
                'content': content,
                'sections': sections,
                'created_at': datetime.now().isoformat(),
                'value_estimate': 150,  # Technical docs are valuable
                'ready_to_sell': True,
                'format': 'markdown'
            }

            self._save_content(documentation)
            self.created_content.append(documentation)

            logger.info(f"✅ Created technical documentation for: {project}")

            return documentation

        except Exception as e:
            logger.error(f"Error creating documentation: {e}")
            return None

    async def create_social_media_campaign(self, brand: str, platform: str, posts_count: int = 5) -> List[Dict[str, Any]]:
        """
        Create a social media campaign

        Args:
            brand: The brand/product to promote
            platform: Social media platform (twitter, linkedin, instagram)
            posts_count: Number of posts to create

        Returns:
            List of social media posts
        """
        try:
            logger.info(f"📱 Creating social media campaign for {brand} on {platform}")

            prompt = f"""
            Create {posts_count} engaging social media posts for {brand} on {platform}.

            Requirements:
            - Match the platform's style and best practices
            - Include relevant hashtags
            - Create variety (educational, promotional, engaging)
            - Include call-to-actions
            - Optimize for engagement

            Format each post with:
            - Post text
            - Hashtags
            - Best time to post
            - Content type (educational/promotional/engaging)
            """

            result = await agent_llm_integration.generate_for_agent(
                agent_name="ContentCreator",
                prompt=f"You are a social media expert creating content for {platform}.\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="medium",
                verbosity="high",
                max_output_tokens=1000
            )

            if not result['success']:
                logger.error(f"LLM error creating social campaign: {result.get('error')}")
                return None

            content = result['response']

            campaign = {
                'type': 'social_media_campaign',
                'brand': brand,
                'platform': platform,
                'posts': content,
                'posts_count': posts_count,
                'created_at': datetime.now().isoformat(),
                'value_estimate': posts_count * 20,  # $20 per post
                'ready_to_sell': True
            }

            self._save_content(campaign)
            self.created_content.append(campaign)

            logger.info(f"✅ Created {posts_count} social media posts for {brand}")

            return campaign

        except Exception as e:
            logger.error(f"Error creating social campaign: {e}")
            return None

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#'):
                return line.replace('#', '').strip()
        return "Untitled"

    def _estimate_content_value(self, word_count: int) -> float:
        """Estimate the value of content based on word count"""
        # Industry standard: $0.10 - $0.30 per word for quality content
        rate_per_word = 0.15
        return word_count * rate_per_word

    def _save_content(self, content: Dict[str, Any]):
        """Save content to file for delivery"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"/tmp/content_{content['type']}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(content, f, indent=2)

        logger.info(f"💾 Saved content to: {filename}")

    def get_created_content_value(self) -> float:
        """Get total value of created content"""
        total = sum(c.get('value_estimate', 0) for c in self.created_content)
        return total

    def deliver_content(self, content_id: int, delivery_format: str = 'markdown') -> Dict[str, Any]:
        """
        Deliver content in specified format

        Args:
            content_id: Index of content to deliver
            delivery_format: Format to deliver in

        Returns:
            Content ready for delivery
        """
        if content_id < len(self.created_content):
            content = self.created_content[content_id]

            if delivery_format == 'html':
                # Convert markdown to HTML if needed
                import markdown
                content['html'] = markdown.markdown(content.get('content', ''))

            content['delivered_at'] = datetime.now().isoformat()
            content['delivery_format'] = delivery_format

            logger.info(f"📦 Content delivered: {content.get('title', 'Content')} in {delivery_format}")

            return content

        return None


# Test the content creator
async def test_content_creator():
    """Test the real content creator"""
    agent = RealContentCreatorAgent()

    # Create a blog post
    blog = agent.create_blog_post(
        topic="How AI is Transforming Freelance Work",
        keywords=["AI", "freelance", "automation", "productivity"],
        word_count=500
    )

    if blog:
        print(f"\n📝 Created Blog Post:")
        print(f"Title: {blog['title']}")
        print(f"Words: {blog['word_count']}")
        print(f"Value: ${blog['value_estimate']:.2f}")
        print(f"Ready to sell: {blog['ready_to_sell']}")

    # Create social media campaign
    campaign = agent.create_social_media_campaign(
        brand="AI Freelancer Pro",
        platform="linkedin",
        posts_count=3
    )

    if campaign:
        print(f"\n📱 Created Social Media Campaign:")
        print(f"Platform: {campaign['platform']}")
        print(f"Posts: {campaign['posts_count']}")
        print(f"Value: ${campaign['value_estimate']:.2f}")

    # Total value created
    total_value = agent.get_created_content_value()
    print(f"\n💰 Total Content Value Created: ${total_value:.2f}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_content_creator())