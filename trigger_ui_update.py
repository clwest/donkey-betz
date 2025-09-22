#!/usr/bin/env python3
"""
Trigger UI update to show job details
"""
import json
import redis
from datetime import datetime

def trigger_update():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Get a job with details
    job_keys = r.keys('freelance:opportunity:*')

    if job_keys:
        # Get first job
        job_data = r.get(job_keys[0])
        if job_data:
            job = json.loads(job_data)

            print(f"Triggering update for job: {job['title']}")
            print(f"Description preview: {job.get('description', '')[:100]}...")
            print(f"Platform: {job.get('platform')}")
            print(f"Skills: {', '.join(job.get('skills_required', []))}")
            print(f"Budget: ${job.get('budget', 0):,}")

            # Update timestamp to trigger refresh
            job['ui_refresh_trigger'] = datetime.now().isoformat()
            r.set(job_keys[0], json.dumps(job))

            print("\n✅ Update triggered - UI should now show full job details")
            print("Check http://localhost:5173")

if __name__ == "__main__":
    trigger_update()