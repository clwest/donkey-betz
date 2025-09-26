#!/usr/bin/env python
"""
Create Sample AI Proposals for Testing the Approval System
==========================================================
This script generates realistic AI proposals that would be created by the consciousness system.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from backend.intelligence.proposal_manager import ProposalManager, ProposalRisk
from datetime import datetime
import json

def create_sample_proposals():
    """Create realistic AI proposals for testing"""

    manager = ProposalManager()

    print("🤖 Creating sample AI proposals for testing...")
    print("=" * 60)

    # Proposal 1: Low-risk optimization
    proposal1 = manager.create_proposal(
        title="Optimize WebSocket Connection Pool",
        description="Analysis shows WebSocket connections are creating new instances on each page refresh. Implementing connection pooling could reduce server load by 15% and improve user experience.",
        category="optimization",
        evidence={
            "connection_analysis": "40 new connections per minute during peak usage",
            "server_load": "Current CPU usage: 78% during connection spikes",
            "user_impact": "Average connection time: 2.3 seconds",
            "files_analyzed": [
                "backend/templates/unified_intelligence_dashboard.html",
                "core/consumers_consciousness.py"
            ]
        },
        impact_analysis={
            "impact_score": 7.5,
            "roi": 3.2,
            "confidence": 0.92,
            "components": ["WebSocket", "consciousness", "dashboard"],
            "dependencies": ["Redis", "Django Channels"],
            "steps": [
                "Implement connection pooling in WebSocket consumer",
                "Add heartbeat mechanism to maintain connections",
                "Update frontend to reuse existing connections",
                "Add connection monitoring metrics"
            ],
            "time_estimate": "15 minutes",
            "rollback": "Revert to current connection logic via git reset",
            "reasoning": "High-confidence optimization based on real connection metrics showing inefficient connection patterns"
        }
    )

    # Proposal 2: Medium-risk refactor
    proposal2 = manager.create_proposal(
        title="Consolidate Agent Execution Tracking",
        description="Multiple systems are tracking agent executions separately (execution_tracker.py, concrete_executor.py, proposal_manager.py). Consolidating into a unified tracking system would reduce data inconsistencies and improve performance monitoring.",
        category="refactor",
        evidence={
            "code_analysis": "3 separate tracking systems found",
            "data_duplication": "67% overlap in tracked metrics",
            "performance_impact": "20ms additional latency per agent execution",
            "maintenance_burden": "3 codepaths to maintain for similar functionality"
        },
        impact_analysis={
            "impact_score": 8.0,
            "roi": 2.8,
            "confidence": 0.78,
            "components": ["agents", "tracking", "monitoring"],
            "dependencies": ["Redis", "Django ORM"],
            "steps": [
                "Create unified ExecutionTracker interface",
                "Migrate existing tracking data to unified format",
                "Update all agent execution points to use new tracker",
                "Deprecate old tracking modules"
            ],
            "time_estimate": "45 minutes",
            "rollback": "Revert refactor changes and restore individual trackers",
            "reasoning": "Moderate confidence refactor based on code analysis showing redundant tracking systems"
        }
    )

    # Proposal 3: High-risk security improvement
    proposal3 = manager.create_proposal(
        title="Implement Proposal Execution Sandboxing",
        description="AI proposals currently execute with full system privileges. Implementing sandboxing would prevent potential system damage from malicious or buggy proposals while maintaining functionality.",
        category="security",
        evidence={
            "security_scan": "Proposal execution runs with admin privileges",
            "risk_assessment": "Potential for system-wide damage if proposal contains errors",
            "compliance": "Required for production deployment",
            "vulnerability": "No isolation between proposal execution and core system"
        },
        impact_analysis={
            "impact_score": 9.5,
            "roi": 5.0,
            "confidence": 0.85,
            "components": ["security", "proposals", "execution"],
            "dependencies": ["Docker", "Linux containers", "permission system"],
            "steps": [
                "Design execution sandbox architecture",
                "Implement Docker-based isolation for proposal execution",
                "Create permission validation system",
                "Add execution monitoring and kill switches",
                "Test sandbox escape prevention"
            ],
            "time_estimate": "2 hours",
            "rollback": "Disable sandboxing and revert to direct execution",
            "reasoning": "Critical security improvement needed before production deployment"
        }
    )

    # Proposal 4: Feature addition
    proposal4 = manager.create_proposal(
        title="Add Real-Time Agent Performance Dashboard",
        description="Agents currently report success rates but lack real-time performance visualization. Adding a live performance dashboard would help identify underperforming agents and optimize system efficiency.",
        category="feature",
        evidence={
            "user_feedback": "Operators need visibility into agent performance",
            "monitoring_gaps": "No real-time view of agent efficiency",
            "optimization_opportunities": "5 agents performing below 70% success rate",
            "business_value": "Improved agent performance = higher system ROI"
        },
        impact_analysis={
            "impact_score": 6.5,
            "roi": 2.1,
            "confidence": 0.88,
            "components": ["dashboard", "monitoring", "agents"],
            "dependencies": ["WebSocket", "Chart.js", "Redis"],
            "steps": [
                "Design real-time performance metrics collection",
                "Create WebSocket stream for live agent data",
                "Build interactive performance dashboard UI",
                "Add agent comparison and ranking features",
                "Implement performance alerts and notifications"
            ],
            "time_estimate": "90 minutes",
            "rollback": "Remove dashboard components and disable performance streaming",
            "reasoning": "High-value feature addition based on operational needs and user feedback"
        }
    )

    # Proposal 5: Bug fix
    proposal5 = manager.create_proposal(
        title="Fix Dashboard Data Persistence Issue",
        description="Dashboard loses all data on page refresh, requiring users to wait for fresh data. This was recently identified and needs immediate fixing to improve user experience.",
        category="bugfix",
        evidence={
            "bug_report": "Dashboard shows blank state on page refresh",
            "user_impact": "Poor user experience, longer wait times",
            "frequency": "Occurs on every page refresh",
            "recent_identification": "Bug identified during September 26 testing session"
        },
        impact_analysis={
            "impact_score": 8.5,
            "roi": 4.8,
            "confidence": 0.95,
            "components": ["dashboard", "cache", "localStorage"],
            "dependencies": ["localStorage API", "JavaScript"],
            "steps": [
                "Implement localStorage caching system",
                "Add cache validation and expiration logic",
                "Update dashboard initialization to load cached data",
                "Add manual cache clear functionality"
            ],
            "time_estimate": "20 minutes",
            "rollback": "Remove localStorage code and revert to fresh-load-only",
            "reasoning": "Critical UX bug with high confidence fix based on recent analysis"
        }
    )

    proposals = [proposal1, proposal2, proposal3, proposal4, proposal5]

    print(f"✅ Created {len(proposals)} sample proposals:")
    for i, proposal in enumerate(proposals, 1):
        risk_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴',
            'critical': '⚫'
        }[proposal.risk_level.value]

        category_emoji = {
            'optimization': '⚡',
            'refactor': '🔄',
            'security': '🔒',
            'feature': '✨',
            'bugfix': '🐛'
        }[proposal.category]

        print(f"   {i}. {category_emoji} {proposal.title}")
        print(f"      Risk: {risk_emoji} {proposal.risk_level.value.upper()}")
        print(f"      Impact: {proposal.impact_score}/10 | ROI: {proposal.roi_estimate}x")
        print(f"      Confidence: {int(proposal.confidence_score * 100)}%")
        print(f"      Status: {proposal.status.value}")
        print()

    # Get statistics
    stats = manager.get_proposal_stats()
    print("📊 Proposal Statistics:")
    print(f"   Total: {stats['total']}")
    print(f"   Pending Approval: {stats['pending']}")
    print(f"   Queued for Execution: {stats['queued_for_execution']}")
    print(f"   Auto-approval Enabled: {stats['auto_approval_enabled']}")
    print(f"   Max Auto-approvals/hour: {stats['safety_thresholds']['max_auto_approvals_per_hour']}")
    print()

    print("🎯 Next Steps:")
    print("   1. Visit /intelligence/ to see the proposals in the dashboard")
    print("   2. Test approval/rejection workflow")
    print("   3. Monitor proposal execution results")
    print("   4. Check Redis for stored proposal data")
    print()

    print("💡 Pro Tip: Proposals with 'low' risk and high confidence may auto-approve!")
    print("    Check the auto-approval settings in the dashboard.")

if __name__ == "__main__":
    create_sample_proposals()