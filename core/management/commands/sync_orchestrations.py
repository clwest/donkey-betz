"""
Session 735: Sync Agent Orchestrations based on coordinator agents.

This command populates the AgentOrchestration database table with predefined
multi-agent workflows based on the system's coordinator agents.

Usage:
    python manage.py sync_orchestrations
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models.agents_registry.models import AgentOrchestration

User = get_user_model()


# Predefined orchestrations based on coordinator agents
ORCHESTRATIONS = [
    {
        'name': 'Blockchain Security Audit',
        'description': 'Comprehensive blockchain security audit using BlockchainAuditCoordinator with SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, and ExploitDetectorAgent.',
        'agent_sequence': ['BlockchainAuditCoordinator', 'SmartContractAuditorAgent', 'TransactionMonitorAgent', 'WhaleWatcherAgent', 'ExploitDetectorAgent'],
        'execution_strategy': 'sequential',
        'workflow_definition': {
            'type': 'security_audit',
            'domain': 'blockchain',
            'coordinator': 'BlockchainAuditCoordinator',
            'steps': [
                {'agent': 'SmartContractAuditorAgent', 'action': 'audit_contracts'},
                {'agent': 'TransactionMonitorAgent', 'action': 'monitor_transactions'},
                {'agent': 'WhaleWatcherAgent', 'action': 'track_whales'},
                {'agent': 'ExploitDetectorAgent', 'action': 'detect_exploits'},
            ]
        },
    },
    {
        'name': 'Stock Market Analysis',
        'description': 'Comprehensive stock analysis using StockAuditCoordinator with StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, and Bull/Bear case agents.',
        'agent_sequence': ['StockAuditCoordinator', 'StockAnalystAgent', 'MarketMovementMonitorAgent', 'InstitutionalWatcherAgent', 'BullCaseAgent', 'BearCaseAgent'],
        'execution_strategy': 'parallel',
        'workflow_definition': {
            'type': 'market_analysis',
            'domain': 'stocks',
            'coordinator': 'StockAuditCoordinator',
            'steps': [
                {'agent': 'StockAnalystAgent', 'action': 'analyze_stock'},
                {'agent': 'MarketMovementMonitorAgent', 'action': 'monitor_movements'},
                {'agent': 'BullCaseAgent', 'action': 'make_bull_case'},
                {'agent': 'BearCaseAgent', 'action': 'make_bear_case'},
            ]
        },
    },
    {
        'name': 'Market Intelligence Briefing',
        'description': 'Market intelligence gathering using MarketIntelligenceCoordinator with PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector, and SignalScannerAgent.',
        'agent_sequence': ['MarketIntelligenceCoordinator', 'PredictionMarketAnalyst', 'SportsOddsAnalyst', 'ArbitrageDetector', 'SignalScannerAgent'],
        'execution_strategy': 'parallel',
        'workflow_definition': {
            'type': 'intelligence_briefing',
            'domain': 'markets',
            'coordinator': 'MarketIntelligenceCoordinator',
            'steps': [
                {'agent': 'PredictionMarketAnalyst', 'action': 'analyze_predictions'},
                {'agent': 'SportsOddsAnalyst', 'action': 'analyze_odds'},
                {'agent': 'ArbitrageDetector', 'action': 'find_arbitrage'},
            ]
        },
    },
    {
        'name': 'Narrative Drift Analysis',
        'description': 'Cultural narrative analysis using NarrativeDriftCoordinator with NarrativeHistorianAgent, TrendBreakDetectorAgent, and CulturalImpactAgent.',
        'agent_sequence': ['NarrativeDriftCoordinator', 'NarrativeHistorianAgent', 'TrendBreakDetectorAgent', 'CulturalImpactAgent'],
        'execution_strategy': 'sequential',
        'workflow_definition': {
            'type': 'narrative_analysis',
            'domain': 'culture',
            'coordinator': 'NarrativeDriftCoordinator',
            'steps': [
                {'agent': 'NarrativeHistorianAgent', 'action': 'analyze_history'},
                {'agent': 'TrendBreakDetectorAgent', 'action': 'detect_breaks'},
                {'agent': 'CulturalImpactAgent', 'action': 'assess_impact'},
            ]
        },
    },
    {
        'name': 'Autonomous Content Studio',
        'description': 'Content creation pipeline using AutonomousContentStudioCoordinator with TopicMinerAgent, ContrarianAgent, and PerformanceAnalystAgent.',
        'agent_sequence': ['AutonomousContentStudioCoordinator', 'TopicMinerAgent', 'ContrarianAgent', 'PerformanceAnalystAgent'],
        'execution_strategy': 'sequential',
        'workflow_definition': {
            'type': 'content_creation',
            'domain': 'content',
            'coordinator': 'AutonomousContentStudioCoordinator',
            'steps': [
                {'agent': 'TopicMinerAgent', 'action': 'mine_topics'},
                {'agent': 'ContrarianAgent', 'action': 'challenge_ideas'},
                {'agent': 'PerformanceAnalystAgent', 'action': 'analyze_performance'},
            ]
        },
    },
    {
        'name': 'Podcast Production Pipeline',
        'description': 'Podcast creation workflow using PodcastCoordinatorAgent with DebateAdvocateAgent, DebateSkepticAgent, and ModeratorAgent.',
        'agent_sequence': ['PodcastCoordinatorAgent', 'DebateAdvocateAgent', 'DebateSkepticAgent', 'ModeratorAgent'],
        'execution_strategy': 'sequential',
        'workflow_definition': {
            'type': 'podcast_production',
            'domain': 'media',
            'coordinator': 'PodcastCoordinatorAgent',
            'steps': [
                {'agent': 'DebateAdvocateAgent', 'action': 'present_position'},
                {'agent': 'DebateSkepticAgent', 'action': 'challenge_position'},
                {'agent': 'ModeratorAgent', 'action': 'moderate_debate'},
            ]
        },
    },
]


class Command(BaseCommand):
    help = 'Sync agent orchestrations based on coordinator agents'

    def handle(self, *args, **options):
        system_user = User.objects.filter(is_superuser=True).first()

        self.stdout.write(f'Found {len(ORCHESTRATIONS)} orchestration definitions')

        created = 0
        updated = 0

        for orch in ORCHESTRATIONS:
            obj, was_created = AgentOrchestration.objects.update_or_create(
                name=orch['name'],
                defaults={
                    'description': orch['description'],
                    'agent_sequence': orch['agent_sequence'],
                    'execution_strategy': orch['execution_strategy'],
                    'workflow_definition': orch['workflow_definition'],
                    'user': system_user,
                    'status': 'pending',
                }
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {orch["name"]}'))
            else:
                updated += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Sync complete: {created} created, {updated} updated. '
            f'Total: {AgentOrchestration.objects.count()} orchestrations'
        ))
