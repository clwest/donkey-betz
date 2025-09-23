#!/usr/bin/env python
"""
Fix Agent Learning Data with Real Agent Names
===========================================
Replace placeholder agent names with actual agents from the database
"""

import redis
import json
import sys
import os
from datetime import datetime

# Setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from agents.models import UnifiedAgentTemplate

def get_real_agents():
    """Get real agent names from database"""
    agents = UnifiedAgentTemplate.objects.all()[:20]
    return [agent.name for agent in agents]

def fix_learning_data():
    """Replace fake agent names with real ones in Redis"""

    # Get real agent names
    real_agents = get_real_agents()
    print(f"Found {len(real_agents)} real agents")

    # Agent name mappings
    agent_mapping = {
        'learner_001': 'business-agent',
        'novel_001': 'content-creator',
        'expert_001': 'technical-signal-agent',
        'optimizer_001': 'market-research-specialist',
        'solver_001': 'seo-specialist-agent'
    }

    # Connect to Redis learning database
    redis_learning = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

    # Get all solution keys
    solution_keys = redis_learning.keys("solution:*")
    print(f"Found {len(solution_keys)} solution keys")

    updates_made = 0

    for key in solution_keys:
        try:
            # Get the solution data
            solution_data = redis_learning.get(key)
            if not solution_data:
                continue

            # Parse JSON
            data = json.loads(solution_data)
            agent_id = data.get('agent_id', '')

            # Check if this agent needs updating
            if agent_id in agent_mapping:
                old_agent = agent_id
                new_agent = agent_mapping[agent_id]

                # Update the data
                data['agent_id'] = new_agent

                # Create new key with updated agent name
                new_key = key.replace(f":{old_agent}:", f":{new_agent}:")

                # Store updated data with new key
                redis_learning.set(new_key, json.dumps(data))

                # Delete old key
                redis_learning.delete(key)

                print(f"Updated: {old_agent} → {new_agent}")
                updates_made += 1

        except Exception as e:
            print(f"Error updating key {key}: {e}")
            continue

    print(f"\nCompleted! Made {updates_made} updates.")
    print("Learning data now uses real agent names.")

if __name__ == "__main__":
    fix_learning_data()