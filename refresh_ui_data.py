#!/usr/bin/env python3
"""
Refresh UI Data - Trigger updates to show real jobs
"""
import json
import redis
import asyncio
import websockets
from datetime import datetime

async def send_ui_updates():
    """Send WebSocket updates to trigger UI refresh"""

    # Get real jobs from Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    job_keys = r.keys('freelance:opportunity:*')[:5]  # Get first 5 jobs

    print(f"Found {len(r.keys('freelance:opportunity:*'))} jobs in Redis")
    print(f"Sending updates for {len(job_keys)} jobs to UI...")

    try:
        # Connect to WebSocket
        async with websockets.connect('ws://localhost:8000/ws/freelance/') as websocket:
            print("Connected to WebSocket")

            # Send updates for each job
            for key in job_keys:
                job_data = r.get(key)
                if job_data:
                    job = json.loads(job_data)

                    # Send new opportunity notification
                    message = {
                        'type': 'new_opportunity',
                        'opportunity': job,
                        'timestamp': datetime.now().isoformat()
                    }

                    await websocket.send(json.dumps(message))
                    print(f"✓ Sent update for: {job['title'][:50]}...")

            # Send refresh signal
            refresh_msg = {
                'type': 'refresh_opportunities',
                'count': len(r.keys('freelance:opportunity:*')),
                'timestamp': datetime.now().isoformat()
            }

            await websocket.send(json.dumps(refresh_msg))
            print("\n✓ Sent refresh signal to UI")

            # Keep connection open briefly to receive responses
            await asyncio.sleep(2)

    except Exception as e:
        print(f"WebSocket error: {e}")
        print("\nTrying alternative method...")

        # If WebSocket fails, update Redis to trigger polling
        for key in job_keys:
            job_data = r.get(key)
            if job_data:
                job = json.loads(job_data)
                # Update timestamp to trigger change detection
                job['last_updated'] = datetime.now().isoformat()
                r.set(key, json.dumps(job))

        print("✓ Updated job timestamps to trigger polling refresh")

    print("\n✅ UI should now show real jobs!")
    print("📍 Check http://localhost:5173")

if __name__ == "__main__":
    asyncio.run(send_ui_updates())