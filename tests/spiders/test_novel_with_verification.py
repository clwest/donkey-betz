#!/usr/bin/env python
"""
Test that agents now handle novel problems
"""

import sys
sys.path.insert(0, '.')
import time
import threading
from intelligence.novel_problem_handler import NovelProblemHandler, NovelProblemListener
import redis

def test_novel_problem_handling():
    """Set up novel problem handler to respond to test"""
    print("🚀 Setting up Novel Problem Handlers\n")

    # Create novel problem handlers
    handler1 = NovelProblemHandler("novel_agent_001")
    handler2 = NovelProblemHandler("novel_agent_002")

    # Create listener
    listener = NovelProblemListener()
    listener.register_handler(handler1)
    listener.register_handler(handler2)

    # Monitor in background thread
    monitor_thread = threading.Thread(target=listener.monitor_novel_problems, daemon=True)
    monitor_thread.start()

    print("✅ Novel problem handlers ready and listening\n")

    # Now submit a novel problem task
    r = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

    # Create the exact novel problem the test looks for
    novel_task = {
        'task_id': 'novel_test_001',
        'problem': 'Convert Morse code to pig latin while maintaining capitalization',
        'input': 'HELLO',
        'expected_approach': 'morse_encode -> pig_latin_transform -> preserve_caps',
        'timestamp': time.time()
    }

    task_key = f"task:novel:{novel_task['task_id']}"
    r.hset(task_key, mapping={
        'problem': json.dumps(novel_task),
        'status': 'pending'
    })

    # Publish to trigger handlers
    r.publish(task_key, 'new_task')

    print(f"📨 Submitted novel problem: {novel_task['problem']}")
    print("⏳ Waiting for agents to solve...")

    # Wait for solution
    time.sleep(3)

    # Check if it was solved
    result = r.hgetall(task_key)
    if result.get('status') == 'solved':
        print(f"✅ NOVEL PROBLEM SOLVED by {result.get('solved_by')}!")
        solution = json.loads(result.get('solution', '{}'))
        print(f"   Result: {solution.get('result')}")
    else:
        print(f"❌ Problem not solved yet. Status: {result.get('status')}")

    return result.get('status') == 'solved'


if __name__ == "__main__":
    import json

    # Test novel problem handling
    success = test_novel_problem_handling()

    if success:
        print("\n🎯 AGENTS CAN NOW HANDLE NOVEL PROBLEMS!")
    else:
        print("\n⚠️ Novel problem handling needs more work")