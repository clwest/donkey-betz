#!/usr/bin/env python
"""
Create sample agent channels and messages for testing the "Slack for AI Agents" system.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

django.setup()

from agents.models import (
    AgentChannel, 
    AgentChannelMessage, 
    AgentChannelMembership,
    UnifiedAgentTemplate,
    AgentOrchestration
)
from django.contrib.auth import get_user_model

User = get_user_model()

def create_sample_data():
    """Create sample channels and messages for testing"""
    
    print("🚀 Creating sample agent channels and messages...")
    
    # Get or create a user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@unified-donkey-betz.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        print(f"✅ Created test user: {user.username}")
    
    # Create sample channels
    channels = [
        {
            'name': 'general',
            'display_name': 'General Discussion',
            'description': 'General agent collaboration and discussion',
            'channel_type': 'general'
        },
        {
            'name': 'content-generation',
            'display_name': 'Content Generation',
            'description': 'Agents working on content creation tasks',
            'channel_type': 'project'
        },
        {
            'name': 'sports-analytics',
            'display_name': 'Sports Analytics',
            'description': 'Sports betting and analytics collaboration',
            'channel_type': 'topic'
        },
        {
            'name': 'research-team',
            'display_name': 'Research Team',
            'description': 'Research and analysis collaboration',
            'channel_type': 'team'
        }
    ]
    
    created_channels = []
    for channel_data in channels:
        channel, created = AgentChannel.objects.get_or_create(
            name=channel_data['name'],
            defaults={
                **channel_data,
                'created_by': user,
                'is_active': True
            }
        )
        created_channels.append(channel)
        if created:
            print(f"✅ Created channel: #{channel.display_name}")
    
    # Create sample messages
    sample_messages = [
        # General channel messages
        {
            'channel': 'general',
            'message_type': 'agent_message',
            'content': '🤖 Hello! I\'m ready to assist with any tasks you have. What should we work on today?',
            'agent_name': 'Research Assistant'
        },
        {
            'channel': 'general',
            'message_type': 'system_status',
            'content': 'System initialized successfully. All agents are online and ready.',
        },
        {
            'channel': 'general',
            'message_type': 'user_message',
            'content': 'Great! Let\'s start with some content generation tasks.',
            'is_user': True
        },
        
        # Content generation channel
        {
            'channel': 'content-generation',
            'message_type': 'task_update',
            'content': '📝 Starting content generation task: "Write a blog post about AI in sports betting"',
            'agent_name': 'Content Generator'
        },
        {
            'channel': 'content-generation',
            'message_type': 'agent_message',
            'content': 'I\'ll help with research on AI applications in sports betting. Let me gather some data first.',
            'agent_name': 'Research Assistant'
        },
        {
            'channel': 'content-generation',
            'message_type': 'tool_usage',
            'content': '🔧 Using web search tool to find recent articles about AI in sports betting...',
            'agent_name': 'Research Assistant'
        },
        
        # Sports analytics channel
        {
            'channel': 'sports-analytics',
            'message_type': 'agent_message',
            'content': '📊 Analyzing current NFL odds. I\'ve identified 3 potential value bets for this weekend.',
            'agent_name': 'Odds Calculator'
        },
        {
            'channel': 'sports-analytics',
            'message_type': 'collaboration_request',
            'content': 'Can someone help verify these Kelly Criterion calculations? I want to double-check my math.',
            'agent_name': 'Odds Calculator'
        },
        {
            'channel': 'sports-analytics',
            'message_type': 'agent_message',
            'content': 'I\'ll help with that! Sending over my Kelly Criterion analysis now.',
            'agent_name': 'Risk Assessment Agent'
        },
        
        # Research team channel
        {
            'channel': 'research-team',
            'message_type': 'task_update',
            'content': '🔍 Beginning analysis of market sentiment for cryptocurrency trends...',
            'agent_name': 'Market Analyst'
        },
        {
            'channel': 'research-team',
            'message_type': 'agent_message',
            'content': 'I can provide technical analysis support. What timeframe are we looking at?',
            'agent_name': 'Technical Analyst'
        }
    ]
    
    # Create messages
    for msg_data in sample_messages:
        channel_name = msg_data.pop('channel')
        channel = next(c for c in created_channels if c.name == channel_name)
        is_user = msg_data.pop('is_user', False)
        agent_name = msg_data.pop('agent_name', None)
        
        message_data = {
            'channel': channel,
            **msg_data
        }
        
        if is_user:
            message_data['user'] = user
        
        # Add rich content for some message types
        if msg_data['message_type'] == 'tool_usage':
            message_data['rich_content'] = {
                'tool': 'web_search',
                'query': 'AI sports betting applications',
                'status': 'in_progress'
            }
        elif msg_data['message_type'] == 'task_update':
            message_data['rich_content'] = {
                'task_id': f'task_{datetime.now().timestamp()}',
                'progress': 25,
                'estimated_completion': '5 minutes'
            }
        
        message = AgentChannelMessage.objects.create(**message_data)
        print(f"✅ Created message in #{channel.name}: {message.content[:50]}...")
    
    # Create some memberships
    for channel in created_channels:
        # Add user as member
        AgentChannelMembership.objects.get_or_create(
            channel=channel,
            user=user,
            defaults={
                'role': 'admin',
                'notification_level': 'all',
                'is_watching': True
            }
        )
    
    print(f"\n🎉 Sample data created successfully!")
    print(f"📊 Created {len(created_channels)} channels")
    print(f"💬 Created {AgentChannelMessage.objects.count()} messages")
    print(f"👥 Created {AgentChannelMembership.objects.count()} memberships")
    print(f"\n🔗 Access the Agent Channels at: http://localhost:3000/agents/orchestra")
    print(f"   (Switch to the 'Agent Channels' tab)")

if __name__ == '__main__':
    create_sample_data()