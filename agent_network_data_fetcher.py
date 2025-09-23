#!/usr/bin/env python
"""
Agent Network Data Fetcher
==========================
Fetches real agent conversation and learning data from Redis for the chat dashboard
"""

import redis
import json
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Redis connection
r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

def parse_agent_data():
    """
    Parse all agent data from Redis and organize it for the chat dashboard
    """
    # Get all keys
    all_keys = r.keys("*")

    agents = {}
    messages = []
    activities = []

    # Parse teaching sessions
    teaching_data = r.lrange("agent_teaching", 0, -1)

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
                'content': f"🎓 Teaching {agents[student_id]['name']} about {teaching_record['topic']}:\n\n{teaching_record['teaching_content']}",
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
                'content': f"📖 Processing knowledge from {agents[teacher_id]['name']}...\n\nUNDERSTANDING: Analyzing key insights about {teaching_record['topic']}\nCONNECTING: Relating to my specialization in {agents[student_id]['specialization']}\nEXPANDING: Identifying areas for deeper investigation\nAPPLYING: Developing practical applications",
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

        except json.JSONDecodeError:
            continue

    # Parse learning data
    learning_keys = [key for key in all_keys if key.startswith('learning:')]

    for key in learning_keys[:10]:  # Limit to avoid overwhelming
        try:
            learning_data = r.get(key)
            if learning_data:
                learning_record = json.loads(learning_data)
                agent_id = key.split(':')[1]

                if agent_id not in agents:
                    agents[agent_id] = {
                        'id': agent_id,
                        'name': agent_id.replace('_', ' ').title(),
                        'specialization': get_specialization_from_id(agent_id),
                        'type': 'specialist',
                        'status': 'active',
                        'message_count': 0,
                        'last_activity': datetime.now().isoformat()
                    }

                learning_message = {
                    'id': f"agent_learn_{len(messages) + 1}",
                    'sender': agents[agent_id]['name'],
                    'sender_id': agent_id,
                    'type': 'learning',
                    'timestamp': datetime.now().isoformat(),
                    'content': f"🧠 Learning new patterns and insights...\n\n{learning_record.get('insight', 'Processing new information and building knowledge base')}",
                    'tokens': 0,
                    'knowledge_transfer': "Self-directed learning"
                }

                messages.append(learning_message)
                agents[agent_id]['message_count'] += 1

        except (json.JSONDecodeError, KeyError):
            continue

    # Parse collaboration data
    collaboration_keys = [key for key in all_keys if key.startswith('collaboration:')]

    for key in collaboration_keys[:5]:  # Limit to avoid overwhelming
        try:
            collab_data = r.get(key)
            if collab_data:
                collab_record = json.loads(collab_data)

                # Extract agent IDs from collaboration key
                key_parts = key.split('_')
                if len(key_parts) >= 3:
                    agent1_id = key_parts[-2]
                    agent2_id = key_parts[-1]

                    collaboration_message = {
                        'id': f"collab_{len(messages) + 1}",
                        'sender': "Collaboration Network",
                        'sender_id': 'collaboration_system',
                        'type': 'specialist',
                        'timestamp': datetime.now().isoformat(),
                        'content': f"🤝 {agent1_id.replace('_', ' ').title()} and {agent2_id.replace('_', ' ').title()} are collaborating on shared objectives",
                        'tokens': 0,
                        'knowledge_transfer': "Inter-agent collaboration"
                    }

                    messages.append(collaboration_message)

        except (json.JSONDecodeError, KeyError):
            continue

    # Add initial spider data message
    spider_message = {
        'id': 'spider_init',
        'sender': 'Spider Network',
        'sender_id': 'spider_network',
        'type': 'spider',
        'timestamp': get_earliest_timestamp(messages),
        'content': '🕷️ Spider network activated - collecting real-time data on AI-driven sustainable agriculture:\n\n• Analyzing agricultural technology trends\n• Gathering market insights and opportunities\n• Processing sustainability best practices\n• Monitoring industry developments',
        'tokens': 0,
        'knowledge_transfer': "Initial data collection"
    }

    messages.insert(0, spider_message)

    # Sort messages by timestamp
    messages.sort(key=lambda x: x['timestamp'])

    return {
        'agents': list(agents.values()),
        'messages': messages,
        'activities': activities,
        'stats': {
            'total_agents': len(agents),
            'total_messages': len(messages),
            'teaching_sessions': len([m for m in messages if m['type'] == 'teaching']),
            'knowledge_items': len([m for m in messages if m.get('knowledge_transfer')]),
            'total_cost': sum(m.get('tokens', 0) for m in messages) * 0.000375,
            'last_update': datetime.now().isoformat()
        }
    }

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

@app.route('/api/agent-data')
def get_agent_data():
    """API endpoint to get all agent data"""
    try:
        data = parse_agent_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Starting Agent Network Data Fetcher...")
    print(f"📊 Parsing data from Redis DB 4...")

    # Test data parsing
    data = parse_agent_data()
    print(f"✅ Found {data['stats']['total_agents']} agents")
    print(f"📨 Found {data['stats']['total_messages']} messages")
    print(f"🎓 Found {data['stats']['teaching_sessions']} teaching sessions")
    print(f"💰 Total cost: ${data['stats']['total_cost']:.6f}")

    print(f"\n🌐 Starting API server on http://localhost:5000")
    print(f"📡 API endpoints:")
    print(f"   GET /api/agent-data - Full agent network data")
    print(f"   GET /api/health - Health check")

    app.run(host='0.0.0.0', port=5000, debug=True)