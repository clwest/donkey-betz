#!/usr/bin/env python3
"""
Trigger agent learning sessions to generate real-time data
"""

import os
import sys
import django
import random
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Agent, AgentInteraction, KnowledgeBase
from real_agent_learning_system import EnhancedAgentLearningSystem
from agent_spider_learning_system import SpiderAgentLearningSystem

def trigger_learning_sessions():
    """Trigger multiple agent learning sessions"""

    print(f"\n🚀 Starting Agent Learning Sessions - {datetime.now()}")
    print("=" * 60)

    # Initialize learning systems
    agent_system = EnhancedAgentLearningSystem()
    spider_system = SpiderAgentLearningSystem()

    # Get all active agents
    agents = Agent.objects.filter(status='active')[:20]  # Start with 20 agents
    print(f"Found {agents.count()} active agents to train")

    learning_topics = [
        "e-commerce optimization strategies",
        "machine learning model deployment",
        "API performance tuning",
        "user experience improvements",
        "data pipeline optimization",
        "security best practices",
        "cloud architecture patterns",
        "real-time data processing"
    ]

    sessions_created = 0

    for agent in agents:
        topic = random.choice(learning_topics)

        try:
            # Create learning prompt
            learning_prompt = f"""
            Learn about: {topic}
            Focus on practical applications and implementation strategies.
            Identify key patterns and best practices.
            """

            print(f"\n📚 Agent '{agent.name}' learning about: {topic}")

            # Trigger learning
            result = agent_system.learn_from_prompt(
                learning_prompt=learning_prompt,
                context={
                    'agent_id': agent.id,
                    'agent_name': agent.name,
                    'specialization': agent.agent_type
                }
            )

            # Store interaction
            if result.get('success'):
                interaction = AgentInteraction.objects.create(
                    agent=agent,
                    interaction_type='learning',
                    content={
                        'topic': topic,
                        'insights': result.get('insights', []),
                        'confidence': result.get('confidence', 0.8)
                    }
                )
                sessions_created += 1
                print(f"   ✅ Learning session completed - Interaction ID: {interaction.id}")

            # Small delay to avoid overwhelming the API
            time.sleep(2)

        except Exception as e:
            print(f"   ❌ Error with agent {agent.name}: {e}")

    print(f"\n✨ Summary:")
    print(f"   • Sessions created: {sessions_created}")
    print(f"   • Agents trained: {sessions_created}/{agents.count()}")
    print(f"   • Time: {datetime.now()}")

    # Trigger some spider data collection
    print(f"\n🕷️ Triggering Spider Data Collection...")
    try:
        spider_data = [
            {'source': 'web', 'content': 'Latest tech trends in AI and ML'},
            {'source': 'reddit', 'content': 'Community discussions on best practices'},
            {'source': 'github', 'content': 'Popular open-source projects'}
        ]

        spider_result = spider_system.learn_from_spider_data(
            spider_data=spider_data,
            learning_focus="technology trends"
        )

        if spider_result.get('success'):
            print("   ✅ Spider data processed successfully")
    except Exception as e:
        print(f"   ❌ Spider error: {e}")

    print("\n" + "=" * 60)
    print("🎉 Agent learning sessions completed!")
    print(f"Check your OpenAI dashboard in a few minutes for API usage.")
    print(f"The visualization will show updated stats after processing.")

if __name__ == "__main__":
    trigger_learning_sessions()