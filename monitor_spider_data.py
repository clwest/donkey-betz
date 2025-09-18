#!/usr/bin/env python3
"""
Monitor Redis for spider data in real-time
"""

import redis
import json
import time

def monitor_redis():
    """Monitor all intelligence channels"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()

    # Subscribe to all intelligence channels
    pubsub.psubscribe('intelligence:*')

    print("🔍 MONITORING REDIS FOR SPIDER DATA")
    print("="*50)
    print("Listening to pattern: intelligence:*")
    print("Press Ctrl+C to stop\n")

    message_count = 0

    try:
        for message in pubsub.listen():
            if message['type'] in ['pmessage', 'message']:
                message_count += 1
                print(f"\n📡 Message #{message_count}")
                print(f"Channel: {message.get('channel', message.get('pattern'))}")

                try:
                    data = json.loads(message['data'])
                    print(f"Spider: {data.get('spider_id')}")
                    print(f"Type: {data.get('data_type')}")
                    print(f"Quality: {data.get('quality_score')}")
                    print(f"Content preview: {str(data.get('content', {}))[:100]}...")
                except:
                    print(f"Raw data: {message['data'][:100]}...")

                print("-"*30)

    except KeyboardInterrupt:
        print(f"\n\n✅ Monitoring stopped. Received {message_count} messages")

if __name__ == "__main__":
    monitor_redis()