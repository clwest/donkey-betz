# Quick Start Guide: Agent Execution System

## 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env with your API keys

# Setup database
python manage.py migrate
```

## 2. Initialize Executors

```bash
python manage.py initialize_executors --register-all --status
```

## 3. Test Execution

```bash
# Run comprehensive tests
python test_real_agent_execution.py

# Run demo
python demo_working_agents.py
```

## 4. Use Individual Agents

```python
from agents.executor_registry import execute_agent_by_name

# Income Builder
result = await execute_agent_by_name('income_builder', {
    'task_type': 'analyze_opportunities',
    'user_profile': {'skills': ['python', 'ai']}
})

# Content Creator
result = await execute_agent_by_name('content_creator', {
    'content_type': 'blog_post',
    'topic': 'AI productivity tools'
})

# Payment Processor
result = await execute_agent_by_name('payment_processor', {
    'task_type': 'create_invoice',
    'amount': 500.0
})
```

## 5. Monitor Performance

```bash
python manage.py initialize_executors --stats --health-check
```
