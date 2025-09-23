#!/usr/bin/env python
"""
Get Agent Solution Counts
=========================
Count solutions by real agent names for the dashboard
"""

import redis
import sys
from collections import defaultdict

def get_agent_solution_counts():
    """Get solution counts grouped by agent name"""

    # Connect to Redis learning database
    redis_learning = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

    # Get all solution keys
    solution_keys = redis_learning.keys("solution:*")

    # Count solutions by agent
    agent_counts = defaultdict(int)

    for key in solution_keys:
        try:
            # Parse agent name from key format: solution:hash:agent_name:timestamp
            parts = key.split(':')
            if len(parts) >= 3:
                agent_name = parts[2]
                agent_counts[agent_name] += 1
        except Exception as e:
            print(f"Error parsing key {key}: {e}")
            continue

    # Sort by solution count (descending)
    sorted_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)

    print("Agent Solution Counts:")
    print("=" * 40)
    for agent_name, count in sorted_agents:
        print(f"{agent_name}: {count} solutions")

    return dict(sorted_agents)

if __name__ == "__main__":
    get_agent_solution_counts()