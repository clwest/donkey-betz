#!/usr/bin/env python
"""
Real-Time Content Creation Agent for AI-Proof Career Guide 2025
================================================================
Creates actual content using GPT-4o-mini and collaborates with other agents
"""

import os
import sys
import json
import redis
import time
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_settings import OPENAI_CONFIG, get_openai_client, NEWS_API_CONFIG
from intelligence.enhanced_problem_solver import EnhancedProblemSolver

class RealContentCreator:
    """
    Creates real content for AI-Proof Career Guide using actual APIs
    """

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        self.client = get_openai_client()
        self.content_queue = []
        self.chapters_created = 0

    def generate_chapter_content(self, chapter_title: str, context: Dict = None) -> Dict:
        """
        Generate real chapter content using GPT-4o-mini
        """
        try:
            prompt = f"""
            Create detailed content for this chapter of the AI-Proof Career Guide 2025:

            Chapter: {chapter_title}
            Context: {json.dumps(context) if context else 'Current job market trends'}

            Include:
            1. Key insights (3-5 bullet points)
            2. Actionable strategies (3-5 items)
            3. Real-world examples
            4. Tools and resources
            5. Success metrics

            Format as structured content with clear sections.
            Make it practical and immediately actionable.
            """

            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG['model'],
                messages=[
                    {"role": "system", "content": "You are an expert career strategist helping people navigate the AI revolution."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            content = response.choices[0].message.content
            self.chapters_created += 1

            return {
                'success': True,
                'chapter': chapter_title,
                'content': content,
                'word_count': len(content.split()),
                'timestamp': datetime.now().isoformat(),
                'chapter_number': self.chapters_created
            }

        except Exception as e:
            print(f"Error generating content: {e}")
            return {
                'success': False,
                'chapter': chapter_title,
                'error': str(e)
            }

    def get_current_job_trends(self) -> List[Dict]:
        """
        Get real job market trends using News API
        """
        try:
            import requests

            response = requests.get(
                'https://newsapi.org/v2/everything',
                params={
                    'q': 'AI jobs 2024 career trends',
                    'apiKey': NEWS_API_CONFIG['api_key'],
                    'sortBy': 'relevancy',
                    'pageSize': 5,
                    'language': 'en'
                }
            )

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])

                trends = []
                for article in articles[:3]:
                    trends.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'url': article.get('url', '')
                    })

                return trends

        except Exception as e:
            print(f"Error fetching trends: {e}")

        return []

    def create_ai_proof_guide(self):
        """
        Create the complete AI-Proof Career Guide 2025
        """
        print("\n" + "=" * 60)
        print("📚 CREATING AI-PROOF CAREER GUIDE 2025")
        print("Using Real APIs for Unique Content")
        print("=" * 60)

        # Get current trends first
        print("\n📊 Fetching current job market trends...")
        trends = self.get_current_job_trends()
        if trends:
            print(f"   ✓ Found {len(trends)} current trends")
            for trend in trends:
                print(f"     - {trend['title'][:60]}...")

        # Define guide structure
        chapters = [
            {
                'title': 'The AI Revolution: What It Really Means for Your Career',
                'focus': 'Understanding the current landscape'
            },
            {
                'title': 'Skills That AI Cannot Replace',
                'focus': 'Human-only capabilities'
            },
            {
                'title': 'Becoming an AI Partner, Not a Competitor',
                'focus': 'Collaboration strategies'
            },
            {
                'title': 'Industry-Specific Survival Strategies',
                'focus': 'Tailored approaches by sector'
            },
            {
                'title': 'Your 90-Day Transformation Plan',
                'focus': 'Actionable roadmap'
            }
        ]

        guide_content = {
            'title': 'AI-Proof Career Guide 2025',
            'created': datetime.now().isoformat(),
            'chapters': [],
            'trends': trends,
            'total_words': 0
        }

        # Generate each chapter
        for i, chapter_info in enumerate(chapters):
            print(f"\n📝 Creating Chapter {i+1}: {chapter_info['title']}")

            # Add trends as context for first chapter
            context = {'trends': trends} if i == 0 else {'focus': chapter_info['focus']}

            result = self.generate_chapter_content(
                chapter_info['title'],
                context
            )

            if result['success']:
                guide_content['chapters'].append(result)
                guide_content['total_words'] += result['word_count']

                # Store in Redis for real-time updates
                self.redis.set(
                    f"guide:chapter:{i+1}",
                    json.dumps(result)
                )

                # Update dashboard metrics
                self.redis.hset('guide:metrics', mapping={
                    'chapters_complete': i + 1,
                    'total_words': guide_content['total_words'],
                    'last_update': datetime.now().isoformat()
                })

                print(f"   ✓ Generated {result['word_count']} words")

                # Small delay to show real-time generation
                time.sleep(1)
            else:
                print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")

        # Store complete guide
        self.redis.set('guide:complete', json.dumps(guide_content))

        print("\n" + "=" * 60)
        print("✅ AI-PROOF CAREER GUIDE 2025 COMPLETE")
        print(f"   Chapters: {len(guide_content['chapters'])}")
        print(f"   Total Words: {guide_content['total_words']}")
        print(f"   Current Trends: {len(trends)}")
        print("=" * 60)

        return guide_content


class ContentCollaborationOrchestrator:
    """
    Orchestrates collaboration between Content Creator and other agents
    """

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        self.content_creator = RealContentCreator()
        self.market_analyst = EnhancedProblemSolver('market_analyst')
        self.skill_advisor = EnhancedProblemSolver('skill_advisor')

    def collaborative_content_creation(self):
        """
        Multiple agents collaborate to create comprehensive content
        """
        print("\n🤝 COLLABORATIVE CONTENT CREATION")
        print("-" * 40)

        # Market Analyst provides data
        print("\n1️⃣ Market Analyst gathering intelligence...")
        market_data = self.market_analyst.solve_problem(
            "Analyze current AI impact on job market",
            context={'focus': 'technology and finance sectors'}
        )

        if market_data['success']:
            print("   ✓ Market analysis complete")
            self.redis.set('collab:market_data', json.dumps(market_data))

        # Skill Advisor provides recommendations
        print("\n2️⃣ Skill Advisor identifying critical skills...")
        skill_data = self.skill_advisor.solve_problem(
            "Identify top 5 skills for AI-proof careers",
            context={'timeframe': '2025-2027'}
        )

        if skill_data['success']:
            print("   ✓ Skill analysis complete")
            self.redis.set('collab:skill_data', json.dumps(skill_data))

        # Content Creator synthesizes everything
        print("\n3️⃣ Content Creator synthesizing insights...")
        guide = self.content_creator.create_ai_proof_guide()

        # Store collaboration result
        collaboration = {
            'timestamp': datetime.now().isoformat(),
            'agents_involved': ['content_creator', 'market_analyst', 'skill_advisor'],
            'content_created': {
                'chapters': len(guide['chapters']),
                'words': guide['total_words']
            },
            'status': 'complete'
        }

        self.redis.set('collaboration:latest', json.dumps(collaboration))

        return guide


def start_real_time_content_creation():
    """
    Start real-time content creation for dashboard
    """
    orchestrator = ContentCollaborationOrchestrator()

    # Create content with agent collaboration
    guide = orchestrator.collaborative_content_creation()

    # Signal dashboard that content is ready
    orchestrator.redis.set('content:status', 'ready')
    orchestrator.redis.publish('content:updates', json.dumps({
        'event': 'guide_complete',
        'chapters': len(guide['chapters']),
        'timestamp': datetime.now().isoformat()
    }))

    return guide


if __name__ == "__main__":
    print("\n🚀 Starting Real-Time Content Creation System")
    print("=" * 60)
    guide = start_real_time_content_creation()
    print("\n✨ Content creation system ready for dashboard!")