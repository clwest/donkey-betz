#!/usr/bin/env python
"""
Content Stream Monitor for Real-Time Dashboard Updates
======================================================
Monitors content creation and pushes updates to dashboard
"""

import redis
import json
import time
from datetime import datetime
import threading

class ContentStreamMonitor:
    """
    Monitors content creation and provides real-time updates
    """

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.running = True

    def monitor_content_creation(self):
        """
        Monitor content creation progress
        """
        print("\n📡 Content Stream Monitor Active")
        print("-" * 40)

        while self.running:
            try:
                # Check guide metrics
                metrics = self.redis.hgetall('guide:metrics')

                if metrics:
                    print(f"\r📚 Progress: {metrics.get('chapters_complete', 0)}/5 chapters | "
                          f"{metrics.get('total_words', 0)} words", end="")

                    # Broadcast update
                    update = {
                        'type': 'progress',
                        'chapters_complete': metrics.get('chapters_complete', 0),
                        'total_words': metrics.get('total_words', 0),
                        'timestamp': datetime.now().isoformat()
                    }

                    self.redis.set('dashboard:content:latest', json.dumps(update))

                # Check for completed chapters
                for i in range(1, 6):
                    chapter_key = f"guide:chapter:{i}"
                    if self.redis.exists(chapter_key):
                        chapter = json.loads(self.redis.get(chapter_key))

                        # Store for dashboard
                        self.redis.hset(
                            'dashboard:chapters',
                            f"chapter_{i}",
                            json.dumps({
                                'title': chapter['chapter'],
                                'preview': chapter['content'][:200] + '...',
                                'words': chapter['word_count'],
                                'timestamp': chapter['timestamp']
                            })
                        )

                time.sleep(2)  # Update every 2 seconds

            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"\nError in monitor: {e}")
                time.sleep(5)

        print("\n\n✅ Content Stream Monitor stopped")

    def start(self):
        """
        Start monitoring in a separate thread
        """
        monitor_thread = threading.Thread(target=self.monitor_content_creation)
        monitor_thread.daemon = True
        monitor_thread.start()
        return monitor_thread


def simulate_live_content_creation():
    """
    Simulate live content creation for testing
    """
    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    print("\n🎬 Simulating Live Content Creation")
    print("-" * 40)

    chapters = [
        "Understanding the AI Revolution",
        "Skills That Matter in 2025",
        "Building Your AI Partnership",
        "Industry Transformation Strategies",
        "Your Action Plan"
    ]

    for i, chapter in enumerate(chapters, 1):
        print(f"\n📝 Creating: {chapter}")

        # Simulate content creation
        content = f"Chapter {i} content about {chapter}. " * 50

        chapter_data = {
            'chapter': chapter,
            'content': content,
            'word_count': len(content.split()),
            'timestamp': datetime.now().isoformat(),
            'chapter_number': i
        }

        # Store chapter
        r.set(f"guide:chapter:{i}", json.dumps(chapter_data))

        # Update metrics
        r.hset('guide:metrics', mapping={
            'chapters_complete': i,
            'total_words': i * 100,
            'last_update': datetime.now().isoformat()
        })

        time.sleep(3)  # Simulate processing time

    print("\n✅ Simulation complete!")


if __name__ == "__main__":
    monitor = ContentStreamMonitor()

    print("=" * 60)
    print("🚀 CONTENT STREAM MONITOR")
    print("=" * 60)
    print("Options:")
    print("1. Monitor real content creation")
    print("2. Run simulation for testing")

    choice = input("\nChoice (1/2): ")

    if choice == "2":
        # Start monitor
        monitor.start()
        # Run simulation
        simulate_live_content_creation()
    else:
        # Just monitor
        monitor.monitor_content_creation()