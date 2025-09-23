#!/usr/bin/env python
"""
Quick Demo - Create AI-Proof Career Guide Content
==================================================
Simulates real-time content creation for demo
"""

import redis
import json
import time
from datetime import datetime

def create_demo_content():
    """
    Create demo content quickly for the dashboard
    """
    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    print("🚀 Creating AI-Proof Career Guide 2025 (Demo Mode)")
    print("-" * 50)

    chapters = [
        {
            'title': 'The AI Revolution: What It Really Means for Your Career',
            'preview': 'The AI revolution isn\'t coming—it\'s here. By 2025, over 40% of current job tasks will be automated or augmented by AI. But this isn\'t a story of replacement; it\'s one of transformation. Understanding how to position yourself...',
            'insights': [
                '85% of new jobs in 2025 will require AI collaboration skills',
                'Soft skills are becoming the new hard skills',
                'Industry boundaries are dissolving faster than ever'
            ]
        },
        {
            'title': 'Skills That AI Cannot Replace',
            'preview': 'While AI excels at pattern recognition and data processing, uniquely human capabilities are becoming more valuable. Emotional intelligence, creative problem-solving, and ethical reasoning are your competitive advantages...',
            'insights': [
                'Empathy and emotional intelligence see 300% increase in demand',
                'Complex reasoning and strategy remain human domains',
                'Cultural understanding and nuance are irreplaceable'
            ]
        },
        {
            'title': 'Becoming an AI Partner, Not a Competitor',
            'preview': 'The future belongs to those who can dance with AI, not fight against it. Learn to leverage AI as your digital amplifier, multiplying your capabilities rather than replacing them. Master the art of prompt engineering...',
            'insights': [
                'AI amplifies human capabilities by 10x when used correctly',
                'Prompt engineering is the new programming',
                'Human-AI teams outperform either alone by 40%'
            ]
        },
        {
            'title': 'Industry-Specific Survival Strategies',
            'preview': 'Every industry faces unique AI challenges and opportunities. Tech workers need to move up the stack, healthcare professionals should focus on patient interaction, finance experts must become strategic advisors...',
            'insights': [
                'Tech: Move from coding to architecture and strategy',
                'Healthcare: Focus on diagnosis interpretation and care',
                'Finance: Transition from analysis to strategic advisory'
            ]
        },
        {
            'title': 'Your 90-Day Transformation Plan',
            'preview': 'Week 1-2: AI tool mastery. Week 3-4: Skill gap analysis. Week 5-8: Strategic upskilling. Week 9-12: Portfolio building and networking. This isn\'t just a plan—it\'s your roadmap to thriving in the AI era...',
            'insights': [
                'Start with 1 hour daily AI tool practice',
                'Build a showcase portfolio in weeks 5-8',
                'Network with AI-forward professionals immediately'
            ]
        }
    ]

    # Clear previous data
    r.delete('guide:metrics')
    r.delete('dashboard:chapters')

    total_words = 0

    for i, chapter in enumerate(chapters, 1):
        print(f"\n📝 Chapter {i}: {chapter['title'][:40]}...")

        # Simulate content generation
        content = f"{chapter['preview']}\n\n"
        content += "Key Insights:\n"
        for insight in chapter['insights']:
            content += f"• {insight}\n"

        word_count = len(content.split())
        total_words += word_count

        # Store chapter
        chapter_data = {
            'chapter': chapter['title'],
            'content': content,
            'word_count': word_count,
            'timestamp': datetime.now().isoformat(),
            'chapter_number': i
        }

        r.set(f"guide:chapter:{i}", json.dumps(chapter_data))

        # Store preview for dashboard
        r.hset(
            'dashboard:chapters',
            f'chapter_{i}',
            json.dumps({
                'title': chapter['title'],
                'preview': chapter['preview'],
                'words': word_count,
                'timestamp': datetime.now().isoformat()
            })
        )

        # Update metrics
        r.hset('guide:metrics', mapping={
            'chapters_complete': i,
            'total_words': total_words,
            'last_update': datetime.now().isoformat(),
            'status': 'generating' if i < 5 else 'complete'
        })

        print(f"   ✓ Generated {word_count} words")
        time.sleep(1)  # Brief pause for real-time effect

    # Final status
    r.set('content:status', 'ready')
    r.hset('guide:metrics', 'status', 'complete')

    print("\n" + "=" * 50)
    print(f"✅ Guide Complete! {len(chapters)} chapters, {total_words} words")
    print("\n🎯 View at: file:///Users/donkeyking/development/unified-donkey-betz/ai_career_survival_realtime.html")
    print("=" * 50)

if __name__ == "__main__":
    create_demo_content()