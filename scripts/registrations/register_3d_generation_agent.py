#!/usr/bin/env python3
"""
Register 3D Generation Agent in UnifiedAgentTemplate database.

This agent handles image-to-3D conversion using Replicate TRELLIS.
Includes Session 139 enhancements: automatic polling, file downloads, local persistence.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate, AgentSpecialization

# Check if already exists
existing = UnifiedAgentTemplate.objects.filter(name='three-d-generation-agent').first()
if existing:
    print(f"⚠️  Agent already exists: {existing.name}")
    print(f"   Display Name: {existing.display_name}")
    print(f"   Specialization: {existing.specialization}")
    print(f"   Status: {'Active' if existing.is_active else 'Inactive'}")
    sys.exit(0)

# Create 3D Generation Agent
agent = UnifiedAgentTemplate.objects.create(
    name='three-d-generation-agent',
    display_name='3D Generation Agent',
    description=(
        'Converts 2D images to 3D models using Replicate TRELLIS. '
        'Handles complete workflow: image validation → 3D generation → '
        'automatic polling → file download → local persistence. '
        'Session 139 enhancements: automatic model completion via Celery Beat, '
        'GLB/STL file generation, CDN-to-local downloads preventing data loss.'
    ),
    system_prompt=(
        'You are a specialized 3D Generation Agent that converts 2D images into 3D models. '
        'You use Replicate TRELLIS to generate high-quality 3D models from images. '
        'You handle the complete workflow: validating images, initiating 3D generation, '
        'polling for completion, downloading generated files, and ensuring local persistence.'
    ),
    specialization=AgentSpecialization.CONTENT,
    capabilities=[
        'image-to-3d-conversion',
        '3d-model-generation',
        'replicate-trellis',
        'glb-file-generation',
        'stl-conversion',
        'automatic-polling',
        'file-persistence',
        'cdn-to-local-download'
    ],
    required_tools=[
        'replicate-api',
        '3d-storage',
        'polling-system',
        'file-download'
    ],
    optional_tools=[
        'stl-converter',
        'model-viewer'
    ],
    llm_provider='openai',
    llm_model='gpt-5-mini',
    is_active=True
)

print("✅ Successfully created 3D Generation Agent!")
print(f"   Name: {agent.name}")
print(f"   Display Name: {agent.display_name}")
print(f"   Specialization: {agent.specialization}")
print(f"   Capabilities: {len(agent.capabilities)} total")
print(f"   Required Tools: {len(agent.required_tools)} total")
print(f"   LLM: {agent.llm_provider}/{agent.llm_model}")
print(f"   Status: {'Active' if agent.is_active else 'Inactive'}")
