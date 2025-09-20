#!/usr/bin/env python
"""
Simulate agent activity by sending messages to agent channels via WebSocket.
This demonstrates the real-time "Slack for AI Agents" functionality.
"""

import os
import sys
import django
import json
from datetime import datetime
import time
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

django.setup()

from agents.models import AgentChannel, AgentChannelMessage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def simulate_agent_messages():
    """Simulate agent messages being sent to channels"""
    
    print("🤖 Starting agent activity simulation...")
    
    # Get channels
    channels = list(AgentChannel.objects.filter(is_active=True))
    if not channels:
        print("❌ No active channels found. Run create_sample_channels.py first.")
        return
    
    print(f"📊 Found {len(channels)} active channels")
    
    # Sample agent messages
    agent_messages = [
        {
            'agent_name': 'Research Assistant',
            'messages': [
                '🔍 Starting research on market trends...',
                '📊 Found interesting correlation in the data.',
                '✅ Research complete. Summary ready.',
                '🤝 Can someone help validate these findings?'
            ]
        },
        {
            'agent_name': 'Content Generator',
            'messages': [
                '✏️ Beginning content generation task...',
                '🎨 Generating creative variations...',
                '📝 First draft completed.',
                '🔄 Refining based on feedback...'
            ]
        },
        {
            'agent_name': 'Odds Calculator',
            'messages': [
                '🎯 Calculating betting odds for upcoming games...',
                '⚡ Found potential arbitrage opportunity!',
                '📈 Updating Kelly Criterion recommendations.',
                '🚨 High value bet detected for review.'
            ]
        },
        {
            'agent_name': 'Risk Analyst',
            'messages': [
                '🛡️ Performing risk assessment...',
                '⚖️ Balancing portfolio recommendations.',
                '📉 Market volatility detected, adjusting strategy.',
                '✨ Risk-adjusted returns optimized.'
            ]
        }
    ]
    
    # Create messages in the database and broadcast via channel layer
    channel_layer = get_channel_layer()
    
    for i in range(20):  # Send 20 messages
        # Pick random channel and agent
        channel = random.choice(channels)
        agent_data = random.choice(agent_messages)
        message_content = random.choice(agent_data['messages'])
        
        # Create message in database
        message = AgentChannelMessage.objects.create(
            channel=channel,
            message_type='agent_message',
            content=message_content,
            rich_content={
                'agent_id': f'agent_{i}',
                'simulation': True,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        print(f"📨 Created message in #{channel.name}: {message_content}")
        
        # Broadcast via WebSocket
        message_data = {
            'type': 'agent_message',
            'channel_id': channel.id,
            'agent_id': f'agent_{i}',
            'agent_name': agent_data['agent_name'],
            'content': message_content,
            'message': message_content,
            'timestamp': datetime.now().isoformat(),
            'rich_content': {
                'simulation': True,
                'task_progress': random.randint(10, 100)
            }
        }
        
        # Send to channel group
        channel_group_name = f'agent_channel_{channel.id}'
        try:
            async_to_sync(channel_layer.group_send)(
                channel_group_name,
                {
                    'type': 'agent_message',
                    **message_data
                }
            )
            print(f"📡 Broadcasted to WebSocket group: {channel_group_name}")
        except Exception as e:
            print(f"❌ Error broadcasting: {e}")
        
        # Wait between messages
        time.sleep(random.uniform(2, 5))
    
    print("🎉 Simulation complete!")

if __name__ == '__main__':
    simulate_agent_messages()