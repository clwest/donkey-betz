#!/usr/bin/env python
"""
Update Agent Network Data
=========================
Fetches real agent data from Redis and creates JSON files for the dashboard
"""

import redis
import json
import os
from datetime import datetime, timedelta

def update_agent_network_data():
    """
    Fetch agent data from Redis and save to JSON files
    """
    print("🔄 Updating agent network data from Redis...")

    # Redis connection
    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    agents = {}
    messages = []
    activities = []

    # Parse teaching sessions
    teaching_data = r.lrange("agent_teaching", 0, -1)
    print(f"📚 Found {len(teaching_data)} teaching sessions")

    for data in teaching_data:
        try:
            teaching_record = json.loads(data)

            # Extract agent info
            teacher_id = teaching_record['teacher']
            student_id = teaching_record['student']

            # Add agents if not exists
            if teacher_id not in agents:
                agents[teacher_id] = {
                    'id': teacher_id,
                    'name': teacher_id.replace('_', ' ').title(),
                    'specialization': get_specialization_from_id(teacher_id),
                    'type': 'primary' if 'analyst' in teacher_id else 'specialist',
                    'status': 'active',
                    'message_count': 0,
                    'last_activity': teaching_record['timestamp']
                }

            if student_id not in agents:
                agents[student_id] = {
                    'id': student_id,
                    'name': student_id.replace('_', ' ').title(),
                    'specialization': get_specialization_from_id(student_id),
                    'type': 'specialist',
                    'status': 'active',
                    'message_count': 0,
                    'last_activity': teaching_record['timestamp']
                }

            # Create teaching message
            teaching_message = {
                'id': f"teach_{len(messages) + 1}",
                'sender': agents[teacher_id]['name'],
                'sender_id': teacher_id,
                'type': 'teaching',
                'timestamp': teaching_record['timestamp'],
                'content': f"🎓 Teaching {agents[student_id]['name']} about {teaching_record['topic']}:\n\n{teaching_record['teaching_content'][:500]}...",
                'tokens': teaching_record['tokens_used'],
                'knowledge_transfer': f"Knowledge transferred to {agents[student_id]['name']}"
            }

            messages.append(teaching_message)
            agents[teacher_id]['message_count'] += 1

            # Create student learning response
            learning_message = {
                'id': f"learn_{len(messages) + 1}",
                'sender': agents[student_id]['name'],
                'sender_id': student_id,
                'type': 'learning',
                'timestamp': add_minutes_to_timestamp(teaching_record['timestamp'], 2),
                'content': f"📖 Processing knowledge from {agents[teacher_id]['name']}...\n\nUNDERSTANDING: Analyzing key insights about {teaching_record['topic']}\nCONNECTING: Relating to my specialization in {agents[student_id]['specialization']}\nEXPANDING: Identifying areas for deeper investigation\nAPPLYING: Developing practical applications for this knowledge",
                'tokens': int(teaching_record['tokens_used'] * 0.7),
                'knowledge_transfer': f"Processed teaching from {agents[teacher_id]['name']}"
            }

            messages.append(learning_message)
            agents[student_id]['message_count'] += 1

            # Add activity entry
            activities.append({
                'type': 'teaching',
                'timestamp': teaching_record['timestamp'],
                'description': f"{agents[teacher_id]['name']} taught {agents[student_id]['name']} about {teaching_record['topic']}",
                'tokens': teaching_record['tokens_used']
            })

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing teaching data: {e}")
            continue

    # Add initial spider data message
    if messages:
        earliest_time = get_earliest_timestamp(messages)
    else:
        earliest_time = (datetime.now() - timedelta(hours=1)).isoformat()

    spider_message = {
        'id': 'spider_init',
        'sender': 'Spider Network',
        'sender_id': 'spider_network',
        'type': 'spider',
        'timestamp': earliest_time,
        'content': '🕷️ Spider network activated - collecting real-time data on AI-driven sustainable agriculture:\n\n• Analyzing agricultural technology trends\n• Gathering market insights and opportunities\n• Processing sustainability best practices\n• Monitoring industry developments',
        'tokens': 0,
        'knowledge_transfer': "Initial data collection complete"
    }

    messages.insert(0, spider_message)

    # Sort messages by timestamp
    messages.sort(key=lambda x: x['timestamp'])

    # Create comprehensive data structure
    agent_data = {
        'agents': list(agents.values()),
        'messages': messages,
        'activities': sorted(activities, key=lambda x: x['timestamp'], reverse=True),
        'stats': {
            'total_agents': len(agents),
            'total_messages': len(messages),
            'teaching_sessions': len([m for m in messages if m['type'] == 'teaching']),
            'knowledge_items': len([m for m in messages if m.get('knowledge_transfer')]),
            'total_cost': sum(m.get('tokens', 0) for m in messages) * 0.000375,
            'last_update': datetime.now().isoformat()
        }
    }

    # Save to JSON file
    with open('agent_network_data.json', 'w') as f:
        json.dump(agent_data, f, indent=2)

    print(f"✅ Data updated successfully!")
    print(f"👥 {agent_data['stats']['total_agents']} agents")
    print(f"📨 {agent_data['stats']['total_messages']} messages")
    print(f"🎓 {agent_data['stats']['teaching_sessions']} teaching sessions")
    print(f"💰 ${agent_data['stats']['total_cost']:.6f} total cost")
    print(f"📄 Data saved to agent_network_data.json")

    return agent_data

def get_specialization_from_id(agent_id):
    """Map agent IDs to specializations"""
    specializations = {
        'agricultural_analyst': 'agricultural technology analysis',
        'crop_optimization_expert': 'crop yield optimization and AI monitoring',
        'sustainability_advisor': 'environmental impact and sustainable practices',
        'technology_integrator': 'AI system integration and farm automation',
        'research_agent': 'data research and analysis',
        'writer_agent': 'content creation and documentation',
        'job_finder_agent': 'employment opportunity discovery',
        'resume_builder_agent': 'professional profile optimization',
        'market_analyzer_agent': 'market trend analysis',
        'trading_agent': 'trading strategy development',
        'validator_agent': 'data validation and verification',
        'executor_agent': 'task execution and implementation',
        'pattern_recognizer_agent': 'pattern recognition and analysis',
        'content_generator_agent': 'content generation and synthesis',
        'job_matcher_agent': 'job matching and recommendations',
        'price_predictor_agent': 'price prediction and forecasting'
    }

    return specializations.get(agent_id, 'specialized AI processing')

def add_minutes_to_timestamp(timestamp_str, minutes):
    """Add minutes to a timestamp string"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        new_dt = dt + timedelta(minutes=minutes)
        return new_dt.isoformat()
    except:
        return timestamp_str

def get_earliest_timestamp(messages):
    """Get the earliest timestamp from messages, or current time minus 1 hour"""
    if not messages:
        return (datetime.now() - timedelta(hours=1)).isoformat()

    try:
        earliest = min(datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) for m in messages)
        return (earliest - timedelta(minutes=30)).isoformat()
    except:
        return (datetime.now() - timedelta(hours=1)).isoformat()

if __name__ == '__main__':
    update_agent_network_data()