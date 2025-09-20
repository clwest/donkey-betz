#!/usr/bin/env python
"""
Fix Sports Betting Bias in Unified Platform
This script updates configuration and prompts to present the platform
as a comprehensive business intelligence system rather than sports-focused.
"""

import os
import json
import re
from pathlib import Path

def update_platform_info():
    """Update platform information files to de-emphasize sports betting"""
    
    # Update .env.example
    env_file = Path('.env.example')
    if env_file.exists():
        content = env_file.read_text()
        
        # Update platform name
        content = content.replace(
            'PLATFORM_NAME=Unified Donkey Betz',
            'PLATFORM_NAME=Unified Intelligence Platform'
        )
        
        # Add comment about sports being optional
        content = content.replace(
            '# Sports Analytics',
            '# Sports Analytics (Optional Module)'
        )
        
        env_file.write_text(content)
        print("✓ Updated .env.example")
    
    # Update settings.py comments
    settings_file = Path('core/settings.py')
    if settings_file.exists():
        content = settings_file.read_text()
        
        content = content.replace(
            'UNIFIED DONKEY BETZ PLATFORM',
            'UNIFIED INTELLIGENCE PLATFORM'
        )
        
        content = content.replace(
            '- Donkey Betz (Sports Analytics)',
            '- Sports Analytics Module (Optional)'
        )
        
        settings_file.write_text(content)
        print("✓ Updated core/settings.py")

def update_assistant_prompt():
    """Update the assistant system prompt to be balanced"""
    
    views_file = Path('core/views.py')
    if not views_file.exists():
        print("❌ core/views.py not found")
        return
    
    content = views_file.read_text()
    
    # Find and replace the system prompt
    old_prompt = '''system_prompt = f"""You are {user.username if hasattr(user, 'username') else user.email}'s personal AI assistant in the Unified Donkey Betz Platform. 

You have access to a comprehensive business intelligence platform with:
- Advanced AI agent orchestration
- Multi-LLM provider integration  
- RAG-powered knowledge management
- Sports betting analytics with Kelly Criterion optimization
- Content creation and management tools
- Real-time workflow automation

Be helpful, concise, and professional. If the user asks about platform features, provide specific guidance on what's available. Keep responses focused and actionable."""'''

    new_prompt = '''system_prompt = f"""You are {user.username if hasattr(user, 'username') else user.email}'s personal AI assistant for the Unified Intelligence Platform. 

This is a comprehensive business automation and intelligence platform that combines multiple advanced capabilities:

**Core Capabilities:**
• AI Agent Orchestration - Manage and coordinate 500+ specialized AI agents
• Content Generation Suite - Create blogs, social media, video scripts, and marketing materials
• Knowledge Management (RAG) - Semantic search and intelligent document processing  
• Workflow Automation - Build and execute complex multi-step business processes
• Multi-LLM Integration - Leverage OpenAI, Anthropic, Google, and local models

**Additional Modules:**
• Business Intelligence & Analytics
• Campaign Management & Marketing Automation
• Self-Awareness & System Introspection
• Real-time Collaboration
• Financial Analysis & Risk Assessment
• Sports Analytics (optional module for specialized use cases)

Be helpful, concise, and professional. Focus on understanding the user's actual needs rather than assuming any particular domain. Keep responses focused and actionable."""'''

    if old_prompt in content:
        content = content.replace(old_prompt, new_prompt)
        views_file.write_text(content)
        print("✓ Updated assistant system prompt in core/views.py")
    else:
        print("⚠ Could not find exact system prompt - may need manual update")

def update_test_plan():
    """Update test plan to be more balanced"""
    
    test_plan_file = Path('test_plan.md')
    if test_plan_file.exists():
        content = test_plan_file.read_text()
        
        # Update sports-specific references
        content = content.replace(
            '- [ ] Sports betting UI functional',
            '- [ ] All platform modules functional (including optional sports module)'
        )
        
        content = content.replace(
            '- [ ] Sports data loading',
            '- [ ] All data sources loading (content, agents, workflows, analytics)'
        )
        
        test_plan_file.write_text(content)
        print("✓ Updated test_plan.md")

def create_platform_config():
    """Create a new platform configuration file"""
    
    config = {
        "platform": {
            "name": "Unified Intelligence Platform",
            "version": "1.0.0",
            "description": "Comprehensive business automation and AI orchestration platform",
            "modules": {
                "core": [
                    "agent_orchestration",
                    "content_generation", 
                    "knowledge_management",
                    "workflow_automation",
                    "multi_llm_integration"
                ],
                "optional": [
                    "sports_analytics",
                    "financial_analysis",
                    "campaign_management"
                ]
            },
            "default_focus": "business_automation",
            "sports_module_enabled": True,
            "sports_module_priority": "low"
        }
    }
    
    config_file = Path('config/platform_config.json')
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Created config/platform_config.json")

def update_frontend_branding():
    """Generate instructions for frontend updates"""
    
    instructions = """
# Frontend Branding Updates Required

## 1. Update package.json
- Change "name" from "unified-donkey-betz" to "unified-intelligence-platform"
- Update "description" to emphasize business automation

## 2. Update App Title (index.html or App.tsx)
- Change <title> tag from "Unified Donkey Betz" to "Unified Intelligence Platform"
- Update meta descriptions

## 3. Update Navigation/Headers
- Ensure main navigation shows all capabilities, not just sports
- Make sports analytics appear as one module among many

## 4. Update Dashboard
- Default dashboard should show business metrics
- Sports dashboard should be a separate optional view

## 5. Update Welcome/Onboarding
- First-time user experience should showcase all capabilities
- Don't default to sports betting examples

## Example Navigation Structure:
```
- Dashboard (Business Overview)
- Content Studio
  - Blog Generator
  - Social Media
  - Video Scripts
- Agent Orchestra
  - Browse Agents
  - Execute Tasks
  - Multi-Agent Workflows
- Knowledge Base
  - Document Upload
  - Semantic Search
  - RAG Analytics
- Workflows
  - Create Workflow
  - Templates
  - Executions
- Analytics
  - Business Intelligence
  - Performance Metrics
  - Sports Analytics (optional)
- Settings
```
"""
    
    with open('FRONTEND_UPDATES.md', 'w') as f:
        f.write(instructions)
    
    print("✓ Created FRONTEND_UPDATES.md with branding instructions")

def main():
    """Run all updates"""
    
    print("\n🔧 Fixing Sports Betting Bias in Platform\n")
    print("=" * 50)
    
    # Check current directory
    if not Path('manage.py').exists():
        print("❌ Error: Run this script from the project root directory")
        print("   (where manage.py is located)")
        return
    
    print("\n1. Updating configuration files...")
    update_platform_info()
    
    print("\n2. Updating assistant system prompt...")
    update_assistant_prompt()
    
    print("\n3. Updating test plan...")
    update_test_plan()
    
    print("\n4. Creating platform configuration...")
    create_platform_config()
    
    print("\n5. Generating frontend update instructions...")
    update_frontend_branding()
    
    print("\n" + "=" * 50)
    print("✅ Updates Complete!\n")
    print("Next steps:")
    print("1. Review and apply the changes")
    print("2. Update your .env file with the new platform name")
    print("3. Follow instructions in FRONTEND_UPDATES.md for UI changes")
    print("4. Restart all services")
    print("5. Run the comprehensive E2E test plan")
    print("\nConsider rebranding to remove 'Betz' from the project name entirely")
    print("Suggested names:")
    print("  - Unified Intelligence Platform (UIP)")
    print("  - AI Orchestration Suite (AOS)")
    print("  - Business Automation Platform (BAP)")

if __name__ == "__main__":
    main()
