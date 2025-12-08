#!/usr/bin/env python
"""
Session 142: Fix AgentContribution field names in all modified files

This script properly handles multi-line AgentContribution.objects.create() calls
and fixes the field names to match the actual model definition.
"""

import re
import os

def fix_agent_contribution_block(match):
    """
    Replace an AgentContribution.objects.create() call with correct field names.

    Extracts key information and rebuilds with simpler, correct fields.
    """
    original = match.group(0)

    # Extract indentation
    indent_match = re.search(r'^(\s*)', original, re.MULTILINE)
    indent = indent_match.group(1) if indent_match else '            '

    # Extract agent name
    agent_match = re.search(r"name='([^']+)'", original)
    agent_name = agent_match.group(1) if agent_match else 'Unknown'

    # Extract content reference (image, video, or minifig_asset)
    content_ref = None
    content_var = None
    if 'image=' in original:
        content_match = re.search(r'image=([^,\)]+)', original)
        if content_match:
            content_ref = 'image'
            content_var = content_match.group(1).strip()
    elif 'video=' in original:
        content_match = re.search(r'video=([^,\)]+)', original)
        if content_match:
            content_ref = 'video'
            content_var = content_match.group(1).strip()
    elif 'minifig_asset=' in original:
        content_match = re.search(r'minifig_asset=([^,\)]+)', original)
        if content_match:
            content_ref = 'minifig_asset'
            content_var = content_match.group(1).strip()

    # Extract project reference
    project_match = re.search(r'project=([^,\)]+)', original)
    project_ref = project_match.group(1).strip() if project_match else 'None'

    # Determine contribution type from agent name or operation
    if 'editing' in agent_name.lower() or 'upscale' in original.lower() or 'recolor' in original.lower() or 'background_removal' in original.lower():
        contribution_type = 'editing'
    else:
        contribution_type = 'generation'

    # Create simplified task description
    if 'video' in content_ref:
        task_desc = f"Generated video using {agent_name}"
    elif 'image' in content_ref:
        if contribution_type == 'editing':
            task_desc = f"Edited image using {agent_name}"
        else:
            task_desc = f"Generated image using {agent_name}"
    else:
        task_desc = f"Generated 3D model using {agent_name}"

    # Build replacement
    replacement = f"""{indent}# Session 142: Track agent contribution
{indent}try:
{indent}    from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
{indent}    agent = UnifiedAgentTemplate.objects.get(name='{agent_name}')
{indent}    AgentContribution.objects.create(
{indent}        agent=agent,
{indent}        {content_ref}={content_var},
{indent}        project={project_ref},
{indent}        contribution_type='{contribution_type}',
{indent}        task_description="{task_desc}",
{indent}        execution_time_seconds=0.0
{indent}    )
{indent}    logger.info(f"✅ Agent contribution tracked for {content_ref} {{{{ {content_var}.id }}}}")
{indent}except Exception as e:
{indent}    logger.error(f"❌ Failed to create agent contribution: {{e}}")
{indent}    # Don't fail content creation if contribution tracking fails"""

    return replacement

def fix_file(filepath):
    """Fix all AgentContribution blocks in a file"""
    print(f"\nProcessing: {filepath}")

    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content

    # Pattern to match entire AgentContribution block
    # Matches from "# Session 142" comment to the end of except block
    # Updated to match any text after "Track agent contribution" and make final comment optional
    pattern = r'([ \t]*)# Session 142: Track agent contribution[^\n]*\n\1try:\n.*?except Exception as e:.*?(?:\n\1    # Don\'t fail content creation if contribution tracking fails)?'

    matches = list(re.finditer(pattern, content, re.DOTALL))
    print(f"Found {len(matches)} AgentContribution blocks")

    if matches:
        content = re.sub(pattern, fix_agent_contribution_block, content, flags=re.DOTALL)

        with open(filepath, 'w') as f:
            f.write(content)

        print(f"✅ Fixed {len(matches)} blocks in {filepath}")
        return True
    else:
        print(f"⚠️  No blocks found in {filepath}")
        return False

def main():
    print("\n" + "="*80)
    print("SESSION 142: FIXING AGENTCONTRIBUTION FIELD NAMES")
    print("="*80)

    # Note: minifig_services.py already fixed manually
    files = [
        'core/views_video.py',
        'core/views_davinci.py',
        'core/views_image.py'
    ]

    fixed_count = 0
    for filepath in files:
        if fix_file(filepath):
            fixed_count += 1

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Fixed {fixed_count} files")
    print(f"\nNote: content/minifig_services.py was already fixed manually (2 blocks)")

if __name__ == '__main__':
    main()
