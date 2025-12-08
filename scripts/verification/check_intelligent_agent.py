# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate

try:
    intelligent_agent = UnifiedAgentTemplate.objects.get(name="Intelligent Prompting Agent", is_active=True)
    print(f'Intelligent Prompting Agent Details:')
    print(f'  Name: {intelligent_agent.name}')
    print(f'  Specialization: {intelligent_agent.specialization}')
    print(f'  Routing Keywords: {intelligent_agent.routing_keywords}')
    print(f'  Capabilities: {intelligent_agent.capabilities}')
    print(f'  LLM Provider: {intelligent_agent.llm_provider}')
    print(f'  LLM Model: {intelligent_agent.llm_model}')
    print(f'  System Prompt:')
    print(f'    {intelligent_agent.system_prompt}')
except UnifiedAgentTemplate.DoesNotExist:
    print('Intelligent Prompting Agent NOT found in database')