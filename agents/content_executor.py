"""
Donkey Betz Content Creator Execution Engine
==========================================

This module provides the execution engine for the Donkey Betz Content Creator agent.
It handles actual content generation using OpenAI/Claude APIs.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from django.utils import timezone

from core.llm_enforcer import LLMEnforcer
from agents.models import AgentExecution, AgentStatus

logger = logging.getLogger(__name__)


class DonkeyBetzContentExecutor:
    """Execution engine for Donkey Betz Content Creator"""

    def __init__(self):
        self.llm_enforcer = LLMEnforcer()
        self.logger = logging.getLogger(__name__)

    def execute_content_creation(self, execution_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content creation task for Donkey Betz

        Args:
            execution_id: Unique execution identifier
            task_data: Task parameters and requirements

        Returns:
            Dict containing execution results
        """
        try:
            # Get execution record
            execution = AgentExecution.objects.get(id=execution_id)
            execution.status = AgentStatus.RUNNING
            execution.started_at = timezone.now()
            execution.save()

            # Extract task parameters
            task_description = task_data.get('task', 'Create content about Donkey Betz')
            content_type = task_data.get('content_type', 'blog_post')
            target_audience = task_data.get('target_audience', 'sports betting enthusiasts')

            # Generate content using AI
            content_result = self._generate_donkey_betz_content(
                task_description, content_type, target_audience
            )

            if content_result['success']:
                # Update execution with results
                execution.status = AgentStatus.COMPLETED
                execution.completed_at = timezone.now()
                execution.output_data = {
                    'content': content_result['content'],
                    'title': content_result['title'],
                    'tags': content_result['tags'],
                    'word_count': content_result['word_count'],
                    'seo_score': content_result['seo_score'],
                    'generated_at': timezone.now().isoformat()
                }
                execution.save()

                self.logger.info(f"✅ Content created successfully for execution {execution_id}")
                return {
                    'success': True,
                    'execution_id': execution_id,
                    'content': content_result['content'],
                    'metadata': execution.output_data
                }
            else:
                # Handle failure
                execution.status = AgentStatus.FAILED
                execution.error_message = content_result.get('error', 'Content generation failed')
                execution.save()

                self.logger.error(f"❌ Content creation failed for execution {execution_id}")
                return {
                    'success': False,
                    'execution_id': execution_id,
                    'error': content_result.get('error', 'Content generation failed')
                }

        except AgentExecution.DoesNotExist:
            self.logger.error(f"Execution {execution_id} not found")
            return {'success': False, 'error': 'Execution not found'}
        except Exception as e:
            self.logger.error(f"Error executing content creation: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_donkey_betz_content(self, task: str, content_type: str, audience: str) -> Dict[str, Any]:
        """Generate content using AI"""
        try:
            # Build specialized prompt for Donkey Betz content
            prompt = self._build_donkey_betz_prompt(task, content_type, audience)

            # Use OpenAI for content generation
            if self.llm_enforcer.openai_client:
                response = self.llm_enforcer.openai_client.chat.completions.create(
                    model="gpt-5-mini",  # High-quality content with GPT-5-mini
                    messages=[
                        {"role": "system", "content": self._get_donkey_betz_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    # temperature=0.7  # GPT-5 only supports default temperature,
                    max_completion_tokens=2000  # GPT-5 uses max_completion_tokens
                )

                content = response.choices[0].message.content

                # Parse and enhance content
                parsed_content = self._parse_generated_content(content)

                return {
                    'success': True,
                    'content': parsed_content['content'],
                    'title': parsed_content['title'],
                    'tags': parsed_content['tags'],
                    'word_count': len(str(parsed_content['content']).split()),
                    'seo_score': self._calculate_seo_score(parsed_content),
                    'ai_model': 'gpt-5-mini'
                }
            else:
                # Fallback content
                return self._generate_fallback_content(task, content_type)

        except Exception as e:
            self.logger.error(f"Content generation error: {e}")
            return {'success': False, 'error': str(e)}

    def _get_donkey_betz_system_prompt(self) -> str:
        """System prompt for Donkey Betz content creation"""
        return """You are the Donkey Betz Content Creator, an expert in sports betting, AI automation, and revenue generation platforms.

MISSION: Create compelling, accurate, and engaging content that showcases Donkey Betz as the premier AI-powered sports betting and revenue automation platform.

PLATFORM OVERVIEW:
- Donkey Betz is an advanced AI platform for sports betting automation
- Features 149 specialized AI agents for different betting strategies
- Includes 25 legendary advisors (Warren Buffett, Cathie Wood, etc.)
- Provides real-time market analysis and automated decision making
- Generates revenue opportunities through intelligent betting algorithms
- Offers comprehensive risk management and portfolio optimization

CONTENT REQUIREMENTS:
- Professional yet accessible tone
- Data-driven insights with specific examples
- Clear value propositions for users
- Actionable advice and strategies
- SEO-optimized with relevant keywords
- Engaging headlines and subheadings
- Call-to-action that drives platform engagement

BRAND VOICE: Innovative, trustworthy, results-focused, cutting-edge

Always structure content with:
1. Compelling headline
2. Hook/introduction
3. Main content with subheadings
4. Key takeaways
5. Call-to-action

Format response as JSON with fields: title, content, tags, key_points, cta"""

    def _build_donkey_betz_prompt(self, task: str, content_type: str, audience: str) -> str:
        """Build specific prompt for content task"""
        return f"""Create a {content_type} for {audience} based on this request: {task}

Content Type: {content_type}
Target Audience: {audience}
Platform Focus: Donkey Betz AI Sports Betting Platform

Requirements:
- 800-1200 words
- SEO-optimized with relevant keywords
- Include specific Donkey Betz features and benefits
- Add statistical insights where relevant
- Professional but engaging tone
- Clear call-to-action

Generate comprehensive content that educates and converts readers into Donkey Betz users."""

    def _parse_generated_content(self, content: str) -> Dict[str, Any]:
        """Parse AI-generated content"""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                parsed = json.loads(content)
                return {
                    'title': parsed.get('title', 'Donkey Betz: AI-Powered Sports Betting'),
                    'content': parsed.get('content', content),
                    'tags': parsed.get('tags', ['donkey-betz', 'sports-betting', 'ai-automation']),
                    'key_points': parsed.get('key_points', []),
                    'cta': parsed.get('cta', 'Try Donkey Betz today!')
                }
            else:
                # Extract title and content from plain text
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else 'Donkey Betz Content'

                return {
                    'title': title,
                    'content': content,
                    'tags': ['donkey-betz', 'sports-betting', 'ai-automation', 'revenue'],
                    'key_points': [],
                    'cta': 'Experience the power of AI-driven sports betting with Donkey Betz!'
                }
        except Exception as e:
            self.logger.warning(f"Content parsing error: {e}")
            return {
                'title': 'Donkey Betz: Revolutionary AI Sports Betting',
                'content': content,
                'tags': ['donkey-betz', 'sports-betting', 'ai'],
                'key_points': [],
                'cta': 'Join Donkey Betz today!'
            }

    def _calculate_seo_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate basic SEO score for content"""
        score = 0.0
        content = content_data.get('content', '')
        title = content_data.get('title', '')

        # Check for target keywords
        target_keywords = ['donkey betz', 'sports betting', 'ai automation', 'revenue']
        for keyword in target_keywords:
            if keyword.lower() in content.lower():
                score += 0.2
            if keyword.lower() in title.lower():
                score += 0.1

        # Word count bonus
        word_count = len(content.split())
        if 800 <= word_count <= 1200:
            score += 0.2

        return min(score, 1.0)

    def _generate_fallback_content(self, task: str, content_type: str) -> Dict[str, Any]:
        """Generate fallback content when AI is unavailable"""
        content = f"""
# Donkey Betz: Revolutionizing Sports Betting with AI

## The Future of Sports Betting is Here

Donkey Betz represents a paradigm shift in sports betting, leveraging advanced artificial intelligence to automate and optimize betting strategies. Our platform combines 149 specialized AI agents with 25 legendary financial advisors to create the most sophisticated betting automation system available.

## Key Features

### AI-Powered Decision Making
Our advanced algorithms analyze thousands of data points in real-time, including:
- Player statistics and performance trends
- Weather conditions and venue factors
- Historical matchup data
- Market sentiment analysis
- Expert predictions and insights

### Automated Risk Management
Donkey Betz automatically manages your betting portfolio with:
- Dynamic bankroll allocation
- Real-time risk assessment
- Diversified betting strategies
- Stop-loss and profit-taking mechanisms

### Revenue Optimization
Maximize your returns with:
- Multi-strategy betting approaches
- Arbitrage opportunity detection
- Value bet identification
- Systematic profit reinvestment

## Why Choose Donkey Betz?

1. **Proven Results**: Our AI algorithms have demonstrated consistent profitability
2. **Risk Control**: Advanced risk management protects your capital
3. **24/7 Operation**: Never miss a profitable opportunity
4. **Expert Guidance**: Learn from legendary investors and sports analysts
5. **Complete Automation**: Set it and forget it betting strategies

## Get Started Today

Ready to transform your sports betting experience? Join thousands of successful Donkey Betz users who have discovered the power of AI-driven betting automation.

**Start your journey to consistent sports betting profits with Donkey Betz!**
        """.strip()

        return {
            'success': True,
            'content': content,
            'title': 'Donkey Betz: Revolutionizing Sports Betting with AI',
            'tags': ['donkey-betz', 'sports-betting', 'ai-automation', 'revenue', 'betting-strategies'],
            'word_count': len(content.split()),
            'seo_score': 0.8,
            'ai_model': 'fallback'
        }


# Global executor instance
_executor_instance = None

def get_content_executor() -> DonkeyBetzContentExecutor:
    """Get the global content executor instance"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = DonkeyBetzContentExecutor()
    return _executor_instance


def execute_donkey_betz_content(execution_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Donkey Betz content creation (convenience function)"""
    return get_content_executor().execute_content_creation(execution_id, task_data)