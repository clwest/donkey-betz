#!/usr/bin/env python
"""
Launch Real-Time AI-Proof Career Guide 2025 Creation
====================================================
Creates content in real-time using GPT-4o-mini and updates dashboard
"""

import sys
import os
import redis
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.api_settings import get_openai_client, OPENAI_CONFIG

def create_chapter_realtime(chapter_num, title, focus):
    """
    Create a single chapter with real-time updates
    """
    client = get_openai_client()
    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    print(f"\n📝 Creating Chapter {chapter_num}: {title}")

    try:
        # Generate content
        prompt = f"""
        Create Chapter {chapter_num} for the AI-Proof Career Guide 2025.

        Title: {title}
        Focus: {focus}

        Provide:
        1. Executive summary (2-3 sentences)
        2. 3 key insights with explanations
        3. 3 actionable strategies
        4. Real-world example
        5. Quick win tip

        Be specific, practical, and focused on 2025 trends.
        """

        response = client.chat.completions.create(
            model=OPENAI_CONFIG['model'],
            messages=[
                {"role": "system", "content": "You are an expert career coach specializing in AI transformation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        content = response.choices[0].message.content
        word_count = len(content.split())

        # Store chapter
        chapter_data = {
            'chapter': title,
            'content': content,
            'word_count': word_count,
            'timestamp': datetime.now().isoformat(),
            'chapter_number': chapter_num
        }

        r.set(f"guide:chapter:{chapter_num}", json.dumps(chapter_data))

        # Update metrics
        existing_words = int(r.hget('guide:metrics', 'total_words') or 0)
        r.hset('guide:metrics', mapping={
            'chapters_complete': chapter_num,
            'total_words': existing_words + word_count,
            'last_update': datetime.now().isoformat()
        })

        # Store preview for dashboard
        r.hset(
            'dashboard:chapters',
            f'chapter_{chapter_num}',
            json.dumps({
                'title': title,
                'preview': content[:200] + '...',
                'words': word_count,
                'timestamp': datetime.now().isoformat()
            })
        )

        print(f"   ✅ Generated {word_count} words")
        print(f"   Preview: {content[:100]}...")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """
    Main execution - creates the guide in real-time
    """
    print("=" * 60)
    print("🚀 LAUNCHING AI-PROOF CAREER GUIDE 2025")
    print("Real-Time Content Creation with GPT-4o-mini")
    print("=" * 60)

    # Initialize Redis
    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    # Clear previous data
    r.delete('guide:metrics')
    r.delete('dashboard:chapters')
    print("\n🧹 Cleared previous data")

    # Initialize metrics
    r.hset('guide:metrics', mapping={
        'chapters_complete': 0,
        'total_words': 0,
        'last_update': datetime.now().isoformat(),
        'status': 'generating'
    })

    # Chapter definitions
    chapters = [
        {
            'title': 'The AI Revolution: What It Really Means for Your Career',
            'focus': 'Current state of AI adoption, immediate impacts on jobs, timeline of changes'
        },
        {
            'title': 'Skills That AI Cannot Replace',
            'focus': 'Emotional intelligence, creativity, complex reasoning, human connection'
        },
        {
            'title': 'Becoming an AI Partner, Not a Competitor',
            'focus': 'Using AI tools effectively, augmentation strategies, collaboration techniques'
        },
        {
            'title': 'Industry-Specific Survival Strategies',
            'focus': 'Tech, healthcare, finance, education, creative industries'
        },
        {
            'title': 'Your 90-Day Transformation Plan',
            'focus': 'Week-by-week action plan, skill building, networking, portfolio development'
        }
    ]

    print(f"\n📚 Creating {len(chapters)} chapters...")
    print("Check dashboard at: file:///Users/donkeyking/development/unified-donkey-betz/ai_career_survival_realtime.html")

    success_count = 0
    total_words = 0

    for i, chapter in enumerate(chapters, 1):
        if create_chapter_realtime(i, chapter['title'], chapter['focus']):
            success_count += 1
            time.sleep(2)  # Pause between chapters for real-time effect

    # Final statistics
    metrics = r.hgetall('guide:metrics')
    print("\n" + "=" * 60)
    print("✅ GUIDE CREATION COMPLETE")
    print(f"   Chapters: {success_count}/{len(chapters)}")
    print(f"   Total Words: {metrics.get('total_words', 0)}")
    print(f"   Status: Ready for viewing")
    print("=" * 60)

    # Set completion status
    r.hset('guide:metrics', 'status', 'complete')
    r.set('content:status', 'ready')


if __name__ == "__main__":
    main()