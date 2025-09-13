#!/usr/bin/env python
"""
Test script to simulate agent progress WebSocket messages.
Run this after starting an agent to see real-time updates.
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_agent_progress(game_id, agent_id, agent_name, message_type, content, phase="analysis", status="running"):
    """Send an agent progress message via WebSocket."""
    channel_layer = get_channel_layer()
    
    message = {
        "type": "agent_progress",
        "data": {
            "game_id": game_id,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "message_type": message_type,
            "content": content,
            "phase": phase,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Send to the general agents group
    async_to_sync(channel_layer.group_send)(
        "agents_general",
        message
    )
    print(f"✅ Sent: {content}")


def simulate_agent_analysis(game_id="7229ae57-ec62-4637-a0d6-1e69f43a6bc4"):
    """Simulate a complete agent analysis flow."""
    
    print(f"\n🚀 Starting agent simulation for game {game_id}\n")
    
    # Simulate multiple agents analyzing
    agents = [
        ("betting-intelligence-analyzer", "Betting Intelligence Analyzer"),
        ("market-value-analyzer", "Market Value Analyzer"),
        ("kelly-bet-sizing", "Kelly Bet Sizing Agent"),
    ]
    
    for agent_id, agent_name in agents:
        # Start analysis
        send_agent_progress(
            game_id, agent_id, agent_name,
            "thinking",
            f"🧠 Starting analysis for game...",
            "initialization", "running"
        )
        
        # Analysis phase
        import time
        time.sleep(1)
        send_agent_progress(
            game_id, agent_id, agent_name,
            "analysis",
            f"📊 Analyzing historical data and market trends...",
            "data_analysis", "running"
        )
        
        # Result
        time.sleep(1)
        if agent_id == "betting-intelligence-analyzer":
            result = "✅ Analysis: Houston -3.5 offers 4.2% value based on model projections"
        elif agent_id == "market-value-analyzer":
            result = "✅ Market: Line movement indicates sharp money on Houston"
        else:
            result = "✅ Kelly: Recommend 2.8% of bankroll on Houston -3.5"
            
        send_agent_progress(
            game_id, agent_id, agent_name,
            "result",
            result,
            "completed", "completed"
        )
        
        time.sleep(0.5)
    
    print("\n✨ Simulation complete!\n")


if __name__ == "__main__":
    # Get game_id from command line or use default
    game_id = sys.argv[1] if len(sys.argv) > 1 else "7229ae57-ec62-4637-a0d6-1e69f43a6bc4"
    simulate_agent_analysis(game_id)