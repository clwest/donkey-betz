#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate

print('Available agents:')
for agent in UnifiedAgentTemplate.objects.filter(is_active=True):
    print(f'  - {agent.name} (specialization: {agent.specialization})')

print(f'\nTotal agents: {UnifiedAgentTemplate.objects.filter(is_active=True).count()}')

# Check specifically for Intelligent Prompting Agent
try:
    intelligent_agent = UnifiedAgentTemplate.objects.get(name="Intelligent Prompting Agent", is_active=True)
    print(f'\nIntelligent Prompting Agent found: {intelligent_agent.name}')
    print(f'  System prompt preview: {intelligent_agent.system_prompt[:100]}...')
except UnifiedAgentTemplate.DoesNotExist:
    print('\nIntelligent Prompting Agent NOT found in database')