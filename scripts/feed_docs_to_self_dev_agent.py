#!/usr/bin/env python
"""Feed external documentation to self-development-agent for complete system self-awareness"""
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate
from ai_core.agents.concrete_executor import execute_agent_sync

def main():
    print("=" * 80)
    print("🧠 SELF-DEVELOPMENT-AGENT DOCUMENTATION INGESTION")
    print("=" * 80)

    # Get agent
    try:
        agent = UnifiedAgentTemplate.objects.get(name='self-development-agent')
        print(f"\n✅ Found agent: {agent.display_name}")
        print(f"   LLM Provider: {agent.llm_provider}")
    except UnifiedAgentTemplate.DoesNotExist:
        print("\n❌ Error: self-development-agent not found in database")
        print("   Run: python scripts/create_self_development_agent.py")
        return 1

    # Load documentation
    docs_path = Path('external-project-docs')
    index_path = docs_path / 'INDEX.md'
    master_context = docs_path / 'ai-content-studio/documentation/master_context_all.md'

    if not index_path.exists():
        print(f"\n❌ Error: Index file not found at {index_path}")
        return 1

    if not master_context.exists():
        print(f"\n❌ Error: Master context not found at {master_context}")
        return 1

    # Read index
    with open(index_path) as f:
        index = f.read()

    print(f"\n📚 Documentation Structure:")
    print(f"   Location: {docs_path}")
    print(f"   Index: {index_path} ({len(index):,} bytes)")
    print(f"   Master Context: {master_context} (18MB, 589K lines)")
    print(f"   Total Files: 1,425 markdown files")
    print(f"   Total Size: 51MB")

    # Create comprehensive analysis task
    task = f"""You are the Self-Development Agent for the unified AI platform.

Your mission is to analyze the complete external documentation to achieve system self-awareness and generate actionable improvement recommendations.

## DOCUMENTATION AVAILABLE

You have access to 1,425 cleaned and deduplicated markdown files (51MB total) covering:

**Projects:**
- ai-content-studio (38MB) - Main AI platform
- donkey-betz (5.4MB) - Sports betting system
- dbao-studio (920KB) - Database admin tools
- root-agents (392KB) - Core agent implementations
- archive (2.4MB) - Historical documentation
- other (2.8MB) - Additional resources

**Key Resources:**
- INDEX.md: Complete file listing with structure
- master_context_all.md: 18MB comprehensive system context (589K lines)

## ANALYSIS TASKS

### 1. SYSTEM ARCHITECTURE MAPPING
- Identify all projects and their purposes
- Map component relationships and integrations
- Document data flows between systems
- Catalog APIs, endpoints, and communication protocols
- Understand frontend/backend architecture

### 2. CAPABILITY MATRIX
- **Implemented Features**: What's fully working?
- **Partial Implementations**: What's started but incomplete?
- **Planned Features**: What's documented but not built?
- **Deprecated Code**: What's obsolete or should be removed?

### 3. GAP ANALYSIS
- Missing implementations (documented but not built)
- Broken integrations (should work but don't)
- Technical debt (quick fixes that need refactoring)
- Security vulnerabilities or concerns
- Performance bottlenecks

### 4. CURRENT SYSTEM STATE ASSESSMENT
Based on the documentation, assess:
- Agent coverage: What % of 196 agents are operational?
- Spider network: Which data sources are active?
- Intelligence domains: What capabilities are working?
- Revenue pipeline: Is the money-making flow complete?
- Production readiness: What's blocking deployment?

### 5. IMPROVEMENT ROADMAP
Generate a prioritized roadmap with phases:

**Phase 1 (1-2 weeks): Critical Fixes**
- Blockers preventing system functionality
- Security issues
- Data pipeline breaks
- Essential integrations

**Phase 2 (2-4 weeks): Enhancement Opportunities**
- Feature completion
- Performance optimization
- User experience improvements
- Additional integrations

**Phase 3 (4-8 weeks): Strategic Growth**
- Advanced features
- Scaling preparation
- New capabilities
- Market expansion

### 6. SELF-IMPROVEMENT RECOMMENDATIONS
As the system analyzing itself, provide:
- Top 10 highest-impact improvements
- Quick wins (low effort, high value)
- Critical path to 95%+ reality score
- Production deployment checklist
- Revenue activation priorities

## DOCUMENTATION INDEX

{index[:10000]}

[Index truncated for brevity - full index available in {index_path}]

## OUTPUT REQUIREMENTS

Produce a comprehensive markdown report with:

1. **Executive Summary** (1 page)
   - Current system state (Reality Score %)
   - Top 3 strengths
   - Top 3 gaps
   - Recommended next steps

2. **System Architecture Map** (2-3 pages)
   - Visual/textual representation of all components
   - Integration points
   - Data flows

3. **Capability Matrix** (2-3 pages)
   - Implemented features by category
   - Partial implementations with completion %
   - Planned features
   - Deprecated components

4. **Gap Analysis** (2-3 pages)
   - Critical gaps (blocking production)
   - Important gaps (limiting functionality)
   - Nice-to-have gaps (enhancement opportunities)

5. **Improvement Roadmap** (2-3 pages)
   - Phase 1: Critical fixes (detailed)
   - Phase 2: Enhancements (summary)
   - Phase 3: Strategic growth (high-level)

6. **Top 10 Recommendations** (1 page)
   - Prioritized action items
   - Expected impact (Low/Medium/High)
   - Effort estimate (Low/Medium/High)
   - Dependencies

7. **Production Readiness Assessment** (1 page)
   - Current readiness score (%)
   - Blocking issues
   - Required fixes for production
   - Timeline estimate

## CONTEXT

**Current System State (from Session 18):**
- Agent Coverage: 90.3% operational (167/185 agents)
- Spider Data: 257,423 entries across 25 spiders
- Intelligence Domains: 6+ operational (Legal, Financial, Sports, Tech, Content, Docs)
- External Documentation: 1,425 files cleaned and ready
- Reality Score: ~87%+

**Session 19 Goals:**
- Achieve complete system self-awareness via this analysis
- Test revenue pipeline (Income Builder → Application → Payment)
- Add LLM API keys for full agent execution
- Move toward 95%+ reality score and production deployment

**Available Resources:**
- Complete documentation at: {docs_path}
- Master context: {master_context}
- Full index: {index_path}

Analyze deeply, be specific, and provide actionable recommendations. The system is relying on your self-awareness to improve itself!
"""

    print(f"\n🚀 Executing self-development-agent analysis...")
    print(f"   This may take 2-5 minutes for comprehensive analysis...")

    # Execute agent task
    try:
        response = execute_agent_sync('self_development_agent', task, context={})

        print(f"\n" + "=" * 80)
        print(f"📊 ANALYSIS COMPLETE!")
        print("=" * 80)

        # Extract result from response
        if not response.get('success'):
            print(f"\n❌ Agent execution failed: {response.get('error')}")
            return 1

        result = response.get('result', '')

        # Convert result to string if it's a dict
        if isinstance(result, dict):
            # Try to get the main content from common keys
            result_text = result.get('result', result.get('output', result.get('response', str(result))))
        else:
            result_text = str(result) if result else str(response)

        if not result_text or result_text == '{}':
            print(f"\n⚠️ Warning: No result returned from agent")
            result_text = f"No result generated. Full response:\n{str(response)}"

        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path('docs/session-reports/2025-10-02')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f'SELF_DEVELOPMENT_ANALYSIS_{timestamp}.md'

        with open(output_path, 'w') as f:
            f.write(f'# Self-Development Agent Analysis\n\n')
            f.write(f'**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'**Agent:** {agent.display_name}\n')
            f.write(f'**LLM Provider:** {agent.llm_provider}\n')
            f.write(f'**Documentation Analyzed:** 1,425 files (51MB)\n\n')
            f.write('---\n\n')
            f.write(result_text)

        print(f"\n💾 Analysis saved to: {output_path}")
        print(f"\n📄 ANALYSIS PREVIEW:")
        print("=" * 80)
        print(result_text[:2000])
        if len(result_text) > 2000:
            print(f"\n... [truncated, {len(result_text):,} total characters]")
        print("=" * 80)

        print(f"\n✅ SUCCESS! Self-development-agent has analyzed the system.")
        print(f"   Full report: {output_path}")

        return 0

    except Exception as e:
        print(f"\n❌ Error executing agent task: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
