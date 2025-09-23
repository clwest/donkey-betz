#!/usr/bin/env python
"""
Live Demo Simulator for Recording
==================================
Creates real-time updates while recording the demo
"""

import redis
import json
import time
from datetime import datetime
import random

def simulate_live_content_creation():
    """
    Simulate live content creation for recording
    """
    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    print("🎬 STARTING LIVE DEMO SIMULATION FOR RECORDING")
    print("=" * 60)
    print("📊 Dashboard: file:///Users/donkeyking/development/unified-donkey-betz/ai_career_survival_realtime.html")
    print("=" * 60)

    # Clear for fresh demo
    r.flushdb()

    chapters = [
        {
            'title': 'The AI Revolution: Understanding the Real Impact',
            'focus': 'Current AI adoption rates and job transformation patterns',
            'words': random.randint(450, 650)
        },
        {
            'title': 'Skills That Make You Irreplaceable in 2025',
            'focus': 'Human capabilities that AI cannot replicate',
            'words': random.randint(400, 550)
        },
        {
            'title': 'Your AI Partnership Strategy',
            'focus': 'How to collaborate with AI rather than compete',
            'words': random.randint(500, 700)
        },
        {
            'title': 'Industry-Specific Survival Playbook',
            'focus': 'Tailored strategies for different sectors',
            'words': random.randint(550, 750)
        },
        {
            'title': 'The 90-Day Career Transformation Plan',
            'focus': 'Step-by-step action plan for immediate implementation',
            'words': random.randint(600, 800)
        }
    ]

    # Initialize
    r.hset('guide:metrics', mapping={
        'chapters_complete': 0,
        'total_words': 0,
        'last_update': datetime.now().isoformat(),
        'status': 'initializing'
    })

    print("\n🚀 Phase 1: System Initialization")
    time.sleep(2)

    r.hset('guide:metrics', 'status', 'generating')

    total_words = 0

    for i, chapter in enumerate(chapters, 1):
        print(f"\n📝 Creating Chapter {i}: {chapter['title']}")
        print(f"   Focus: {chapter['focus']}")

        # Simulate agent collaboration
        agents = ['Content Creator', 'Market Analyst', 'Skill Advisor', 'Trend Predictor']
        active_agent = random.choice(agents)

        print(f"   🤖 Agent: {active_agent} is generating content...")

        # Update status to show current work
        r.hset('guide:metrics', mapping={
            'current_chapter': i,
            'current_agent': active_agent,
            'status': 'generating'
        })

        # Simulate incremental word generation
        chapter_words = 0
        target_words = chapter['words']

        while chapter_words < target_words:
            increment = random.randint(50, 150)
            chapter_words = min(chapter_words + increment, target_words)
            total_words = sum(chapters[j]['words'] for j in range(i-1)) + chapter_words

            # Update metrics
            r.hset('guide:metrics', mapping={
                'chapters_complete': i if chapter_words >= target_words else i-1,
                'total_words': total_words,
                'current_words': chapter_words,
                'last_update': datetime.now().isoformat()
            })

            print(f"      Words: {chapter_words}/{target_words} (+{increment})")
            time.sleep(random.uniform(0.5, 2.0))  # Variable pace

        # Chapter complete
        chapter_data = {
            'chapter': chapter['title'],
            'content': f"This chapter explores {chapter['focus']}. " * 10,  # Sample content
            'word_count': target_words,
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
                'preview': f"This comprehensive chapter examines {chapter['focus']} and provides actionable insights for career transformation...",
                'words': target_words,
                'timestamp': datetime.now().isoformat()
            })
        )

        print(f"   ✅ Chapter {i} Complete: {target_words} words")

        # Brief pause between chapters
        time.sleep(1)

    # Final completion
    final_total = sum(ch['words'] for ch in chapters)

    r.hset('guide:metrics', mapping={
        'chapters_complete': 5,
        'total_words': final_total,
        'status': 'complete',
        'last_update': datetime.now().isoformat()
    })

    r.set('content:status', 'ready')

    print("\n" + "=" * 60)
    print("✅ AI-PROOF CAREER GUIDE 2025 COMPLETE!")
    print(f"   📚 5 Chapters Generated")
    print(f"   📝 {final_total:,} Total Words")
    print(f"   🤖 Multiple Agents Collaborated")
    print(f"   💰 Cost: ~$0.004 (using gpt-4o-mini)")
    print("=" * 60)
    print("\n🎬 Ready for recording! Refresh dashboard to see results.")

    return final_total

if __name__ == "__main__":
    total_words = simulate_live_content_creation()