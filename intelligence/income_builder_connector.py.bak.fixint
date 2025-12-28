#!/usr/bin/env python3
"""
Income Builder Connector
Bridges the Income Builder frontend with the Task Delegation Orchestrator
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from intelligence.income_builder_automation import IncomeBuilderAutomation
from intelligence.task_delegation_orchestrator import TaskDelegationOrchestrator

app = Flask(__name__)
CORS(app)

# Global automation instance
automation = IncomeBuilderAutomation()

@app.route('/api/income-builder/process-plan', methods=['POST'])
async def process_plan():
    """
    Endpoint for Income Builder to submit plans for automated execution
    """
    data = request.json
    plan_file = data.get('plan_file')

    if not plan_file:
        return jsonify({"error": "No plan file provided"}), 400

    # Process the plan
    result = await automation.process_new_plan(plan_file)

    return jsonify(result)

@app.route('/api/income-builder/analyze-plan', methods=['POST'])
def analyze_plan():
    """
    Analyze a plan and return task breakdown without executing
    """
    data = request.json
    plan_content = data.get('plan_content')

    if not plan_content:
        return jsonify({"error": "No plan content provided"}), 400

    # Parse tasks
    orchestrator = TaskDelegationOrchestrator()
    tasks = orchestrator.parse_action_plan(plan_content)

    # Create response
    task_breakdown = {
        "total_tasks": len(tasks),
        "phases": {},
        "agents_required": set(),
        "timeline": None,
        "priority_tasks": []
    }

    # Group by phase
    for task in tasks:
        if task.phase not in task_breakdown["phases"]:
            task_breakdown["phases"][task.phase] = []

        task_breakdown["phases"][task.phase].append({
            "title": task.title,
            "agent": task.agent_type,
            "priority": task.priority.name,
            "timeline": task.day_range,
            "tools": task.platform_tools,
            "metrics": task.success_metrics
        })

        task_breakdown["agents_required"].add(task.agent_type)

    # Get priority tasks
    orchestrator.create_execution_queue()
    for task in orchestrator.execution_queue[:5]:
        task_breakdown["priority_tasks"].append({
            "title": task.title,
            "agent": task.agent_type,
            "priority": task.priority.name
        })

    # Convert set to list for JSON
    task_breakdown["agents_required"] = list(task_breakdown["agents_required"])

    return jsonify(task_breakdown)

@app.route('/api/income-builder/execution-status/<execution_id>', methods=['GET'])
async def get_execution_status(execution_id):
    """
    Get the status of an ongoing execution
    """
    status = await automation.monitor_execution(execution_id)
    return jsonify(status)

@app.route('/api/income-builder/delegate-task', methods=['POST'])
def delegate_single_task():
    """
    Delegate a single task to an agent
    """
    data = request.json

    orchestrator = TaskDelegationOrchestrator()

    # Create a synthetic task from the request
    from intelligence.task_delegation_orchestrator import ExtractedTask, TaskPriority
    from datetime import timedelta

    task = ExtractedTask(
        id=f"manual_{data.get('id', 'task')}",
        title=data.get('title', 'Manual Task'),
        description=data.get('description', ''),
        agent_type=data.get('agent', 'general-purpose'),
        phase="Manual",
        day_range="Now",
        priority=TaskPriority[data.get('priority', 'MEDIUM')],
        dependencies=[],
        estimated_duration=timedelta(hours=1),
        platform_tools=data.get('tools', []),
        success_metrics=data.get('metrics', {}),
        metadata={"source": "manual_delegation"}
    )

    # Delegate the task
    delegation = orchestrator.delegate_task(task)

    return jsonify(delegation)

@app.route('/api/income-builder/available-agents', methods=['GET'])
def get_available_agents():
    """
    Get list of available agents for task delegation
    """
    agents = {
        "content_creation": [
            {"id": "ai-content-studio", "name": "AI Content Studio", "capabilities": ["branding", "design", "visuals"]},
            {"id": "content-creator", "name": "Content Creator", "capabilities": ["copy", "templates", "documentation"]},
            {"id": "image-video-pipeline", "name": "Image/Video Pipeline", "capabilities": ["graphics", "videos", "media"]}
        ],
        "research_analysis": [
            {"id": "research-agent", "name": "Research Agent", "capabilities": ["market analysis", "competitor research", "insights"]},
            {"id": "monitoring-dashboard-builder", "name": "Analytics Monitor", "capabilities": ["metrics", "dashboards", "reporting"]}
        ],
        "revenue_business": [
            {"id": "revenue-activation-orchestrator", "name": "Revenue Engine", "capabilities": ["payments", "invoicing", "subscriptions"]},
            {"id": "opportunity-pipeline-orchestrator", "name": "Opportunity Pipeline", "capabilities": ["lead gen", "proposals", "outreach"]}
        ],
        "technical": [
            {"id": "coding-agent", "name": "Coding Agent", "capabilities": ["automation", "scripts", "integration"]},
            {"id": "intelligent-prompting-integrator", "name": "System Integrator", "capabilities": ["api connections", "workflows"]}
        ]
    }

    return jsonify(agents)

@app.route('/api/income-builder/webhook/register', methods=['POST'])
def register_webhook():
    """
    Register a webhook for execution updates
    """
    data = request.json
    endpoint = data.get('endpoint')

    if not endpoint:
        return jsonify({"error": "No endpoint provided"}), 400

    automation.register_webhook(endpoint)

    return jsonify({"message": "Webhook registered", "endpoint": endpoint})

if __name__ == '__main__':
    # For production, run with proper ASGI server
    print("🚀 Income Builder Connector API")
    print("=" * 50)
    print("Endpoints:")
    print("  POST /api/income-builder/process-plan - Execute a plan")
    print("  POST /api/income-builder/analyze-plan - Analyze without executing")
    print("  GET  /api/income-builder/execution-status/<id> - Get execution status")
    print("  POST /api/income-builder/delegate-task - Delegate single task")
    print("  GET  /api/income-builder/available-agents - List available agents")
    print("  POST /api/income-builder/webhook/register - Register webhook")
    print()

    app.run(host='0.0.0.0', port=5001, debug=True)