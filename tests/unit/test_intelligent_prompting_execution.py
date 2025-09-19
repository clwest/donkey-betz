#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# Get or create a test user
try:
    user = User.objects.get(username='chris')
except User.DoesNotExist:
    user = User.objects.create_user(username='testuser', email='test@example.com')

# Get the Intelligent Prompting Agent
intelligent_agent = UnifiedAgentTemplate.objects.get(name="Intelligent Prompting Agent", is_active=True)

print(f"Found agent: {intelligent_agent.name}")
print(f"Agent capabilities: {intelligent_agent.capabilities}")

# Create a test execution to optimize a prompt
execution = AgentExecution.objects.create(
    template=intelligent_agent,
    user=user,
    execution_id=f"test_prompt_opt_{uuid.uuid4().hex[:8]}",
    task_description="Optimize this prompt: 'Write a blog post about AI'",
    task_type="prompt_optimization",
    input_data={
        "original_prompt": "Write a blog post about AI",
        "target_model": "gpt-5-mini",
        "desired_outcome": "Comprehensive, engaging blog post with technical depth"
    },
    context={
        "user_intent": "Create high-quality content",
        "content_type": "blog_post",
        "topic": "artificial_intelligence"
    }
)

print(f"\nCreated execution: {execution.execution_id}")
print(f"Task: {execution.task_description}")
print(f"Status: {execution.status}")

# Check if we can execute it manually (without Celery)
print(f"\nAgent system prompt preview:")
print(f"{intelligent_agent.system_prompt[:200]}...")

print(f"\nAgent LLM config: {intelligent_agent.llm_config}")
print(f"Provider: {intelligent_agent.llm_provider}")
print(f"Model: {intelligent_agent.llm_model}")