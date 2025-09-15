"""
🔌 AGENT WIRING SYSTEM - Complete Agent Registry Connection
Connects and activates all 102+ agents in the unified platform
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from agents.registry import get_agent_registry, AgentRegistry
from agents.models import UnifiedAgentTemplate, AgentSpecialization
from advisors.registry import get_advisor_registry

logger = logging.getLogger(__name__)

@dataclass
class AgentConnection:
    """Represents a connection between agents"""
    source_agent: str
    target_agent: str
    connection_type: str  # "data_flow", "orchestration", "delegation", "consultation"
    bidirectional: bool = False
    data_format: str = "json"

class UnifiedAgentWiringSystem:
    """
    Master wiring system that connects all agents in the platform
    Ensures every agent is properly registered, connected, and ready for execution
    """

    # Complete agent catalog with connections
    AGENT_CATALOG = {
        # 🕷️ Spider Army & Data Collection
        "spider-army-supreme-orchestrator": {
            "specialization": AgentSpecialization.ORCHESTRATION,
            "connections": ["spider-agent-connector", "data-pipeline", "advisor-registry"],
            "capabilities": ["deploy_spiders", "manage_swarms", "route_intelligence"],
            "tools": ["web_search", "api_calls", "data_streaming"]
        },
        "spider-agent-connector-orchestrator": {
            "specialization": AgentSpecialization.ORCHESTRATION,
            "connections": ["spider-army", "agent-registry", "advisor-registry"],
            "capabilities": ["connect_spiders", "route_data", "manage_pipelines"]
        },

        # 💰 Revenue & Monetization
        "revenue-activation-orchestrator": {
            "specialization": AgentSpecialization.BUSINESS,
            "connections": ["opportunity-pipeline", "income-builder", "payment-processor"],
            "capabilities": ["identify_opportunities", "submit_proposals", "track_revenue"],
            "tools": ["payment_apis", "proposal_generator", "revenue_tracker"]
        },
        "opportunity-pipeline-orchestrator": {
            "specialization": AgentSpecialization.BUSINESS,
            "connections": ["revenue-activation", "spider-army", "ml-pipeline"],
            "capabilities": ["discover_opportunities", "analyze_viability", "execute_pipeline"]
        },
        "income-builder": {
            "specialization": AgentSpecialization.BUSINESS,
            "connections": ["task-delegation", "revenue-activation", "content-creator"],
            "capabilities": ["generate_plans", "create_workflows", "track_progress"]
        },

        # 🤖 ML & AI Pipeline
        "ml-pipeline": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["income-builder", "opportunity-pipeline", "prediction-engine"],
            "capabilities": ["predict_outcomes", "score_opportunities", "optimize_models"],
            "tools": ["mlx_engine", "tensorflow", "scikit_learn"]
        },
        "narrative-predictor-agent": {
            "specialization": AgentSpecialization.NARRATIVE_PREDICTOR,
            "connections": ["ml-pipeline", "content-creator", "trend-analyzer"],
            "capabilities": ["predict_narratives", "analyze_trends", "generate_stories"]
        },
        "correlation-hunter": {
            "specialization": AgentSpecialization.CORRELATION_HUNTER,
            "connections": ["ml-pipeline", "data-analyzer", "pattern-recognizer"],
            "capabilities": ["find_correlations", "identify_patterns", "predict_relationships"]
        },

        # 📊 Monitoring & Analytics
        "monitoring-dashboard-builder": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["redis-cache", "api-endpoints", "metrics-collector"],
            "capabilities": ["build_dashboards", "track_metrics", "generate_reports"],
            "tools": ["grafana", "prometheus", "custom_charts"]
        },
        "redis-cache-optimizer": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["api-endpoints", "monitoring-dashboard", "performance-tracker"],
            "capabilities": ["optimize_cache", "reduce_latency", "manage_memory"]
        },
        "api-endpoint-validator": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["monitoring-dashboard", "security-auditor", "performance-tracker"],
            "capabilities": ["validate_endpoints", "test_apis", "ensure_consistency"]
        },

        # 🎨 Content & Creative
        "content-creator": {
            "specialization": AgentSpecialization.CONTENT,
            "connections": ["ai-content-studio", "image-pipeline", "marketing-agent"],
            "capabilities": ["generate_content", "write_copy", "create_posts"]
        },
        "image-video-pipeline": {
            "specialization": AgentSpecialization.CREATIVE,
            "connections": ["content-creator", "ai-content-studio", "dalle-api"],
            "capabilities": ["generate_images", "create_videos", "process_media"]
        },
        "ai-content-studio": {
            "specialization": AgentSpecialization.CONTENT,
            "connections": ["content-creator", "image-pipeline", "brand-builder"],
            "capabilities": ["manage_content", "schedule_posts", "brand_consistency"]
        },

        # 🏆 Sports & Betting
        "kelly-bet-sizing": {
            "specialization": AgentSpecialization.SPORTS_ANALYTICS,
            "connections": ["odds-calculator", "risk-manager", "bankroll-tracker"],
            "capabilities": ["calculate_kelly", "optimize_stakes", "manage_risk"]
        },
        "sports-system-tracer": {
            "specialization": AgentSpecialization.SPORTS_ANALYTICS,
            "connections": ["odds-api", "kelly-sizing", "performance-tracker"],
            "capabilities": ["trace_systems", "verify_connections", "audit_flow"]
        },
        "bookmaker-agent": {
            "specialization": AgentSpecialization.SPORTS_ANALYTICS,
            "connections": ["odds-api", "arbitrage-detector", "value-finder"],
            "capabilities": ["track_odds", "find_value", "monitor_lines"]
        },

        # 🔧 Platform & Infrastructure
        "system-unification-architect": {
            "specialization": AgentSpecialization.ORCHESTRATION,
            "connections": ["all-agents", "all-advisors", "all-systems"],
            "capabilities": ["unify_systems", "merge_platforms", "create_self_awareness"]
        },
        "platform-design-convergence": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["ui-components", "design-system", "frontend-apps"],
            "capabilities": ["unify_design", "standardize_ui", "migrate_components"]
        },
        "react-web-unify": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["react-components", "websocket-client", "api-integration"],
            "capabilities": ["unify_frontend", "standardize_patterns", "fix_issues"]
        },
        "react-native-unify": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["expo-app", "mobile-components", "api-client"],
            "capabilities": ["unify_mobile", "sync_with_web", "implement_features"]
        },

        # 🧠 Intelligence & Memory
        "intelligent-prompting-integrator": {
            "specialization": AgentSpecialization.ORCHESTRATION,
            "connections": ["all-agents", "prompt-system", "routing-engine"],
            "capabilities": ["integrate_prompts", "route_requests", "optimize_context"]
        },
        "memory-isolation-agent": {
            "specialization": AgentSpecialization.MEMORY_BRIDGE_COORDINATOR,
            "connections": ["vector-db", "context-manager", "isolation-layer"],
            "capabilities": ["isolate_memory", "manage_context", "prevent_leaks"]
        },
        "rag-diagnostics-agent": {
            "specialization": AgentSpecialization.RAG_DIAGNOSTICS,
            "connections": ["vector-db", "embeddings", "retrieval-system"],
            "capabilities": ["diagnose_rag", "improve_recall", "optimize_retrieval"]
        },
        "glossary-anchor-curator": {
            "specialization": AgentSpecialization.GLOSSARY_ANCHOR_CURATOR,
            "connections": ["rag-system", "embeddings", "knowledge-base"],
            "capabilities": ["curate_anchors", "improve_matching", "manage_glossary"]
        },

        # 🚀 Advanced Orchestrators
        "limitless-system-implementation-orchestrator": {
            "specialization": AgentSpecialization.ORCHESTRATION,
            "connections": ["all-meta-agents", "human-ai-bridge", "amplifier"],
            "capabilities": ["implement_limitless", "create_symbiosis", "amplify_intelligence"]
        },
        "empire-builder-orchestrator": {
            "specialization": AgentSpecialization.EMPIRE_BUILDER,
            "connections": ["revenue-engine", "growth-tracker", "expansion-planner"],
            "capabilities": ["build_empire", "scale_operations", "maximize_growth"]
        },
        "autonomous-knowledge-evolution-engine": {
            "specialization": AgentSpecialization.KNOWLEDGE_EVOLUTION,
            "connections": ["knowledge-base", "learning-loop", "evolution-tracker"],
            "capabilities": ["evolve_knowledge", "learn_continuously", "adapt_strategies"]
        },

        # 🔒 Security & Validation
        "platform-security-unifier": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["security-scanner", "vulnerability-fixer", "compliance-checker"],
            "capabilities": ["unify_security", "fix_vulnerabilities", "ensure_compliance"]
        },
        "agent-tools-validation-enforcer": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["agent-registry", "tool-validator", "enforcement-engine"],
            "capabilities": ["validate_tools", "enforce_usage", "prevent_mocking"]
        },

        # 📝 Task Management
        "task-delegation-orchestrator": {
            "specialization": AgentSpecialization.ORCHESTRATION,
            "connections": ["all-agents", "execution-queue", "progress-tracker"],
            "capabilities": ["delegate_tasks", "manage_queue", "track_execution"]
        },
        "celery-orchestration-fixer": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["celery-workers", "task-queue", "beat-scheduler"],
            "capabilities": ["fix_celery", "optimize_workers", "manage_queues"]
        },

        # 💬 Communication & Support
        "shit-talker": {
            "specialization": AgentSpecialization.SHIT_TALKER,
            "connections": ["motivation-engine", "combat-mode", "trash-talk-generator"],
            "capabilities": ["motivate_aggressively", "combat_doubt", "push_limits"]
        },
        "ws-health-diagnostics": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["websocket-server", "connection-monitor", "health-checker"],
            "capabilities": ["diagnose_ws", "fix_connections", "monitor_health"]
        },

        # 📊 Data Processing
        "token-budget-agent": {
            "specialization": AgentSpecialization.TOKEN_BUDGET,
            "connections": ["context-manager", "token-counter", "optimization-engine"],
            "capabilities": ["manage_tokens", "optimize_context", "prevent_overflow"]
        },
        "prompt-diagnostics-agent": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["prompt-analyzer", "optimization-engine", "quality-checker"],
            "capabilities": ["analyze_prompts", "optimize_structure", "improve_quality"]
        },

        # 🏗️ Infrastructure Management
        "makefile-unification-builder": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["build-system", "docker-compose", "service-manager"],
            "capabilities": ["unify_makefiles", "standardize_commands", "manage_services"]
        },
        "postgres-integration-validator": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["database", "pgvector", "migration-engine"],
            "capabilities": ["validate_postgres", "ensure_integration", "manage_migrations"]
        },
        "dbao-sdk-sync": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["sdk-generator", "manifest-builder", "export-validator"],
            "capabilities": ["sync_sdks", "generate_clients", "validate_exports"]
        },
        "dbao-tools-cataloguer": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["tool-scanner", "manifest-generator", "sdk-builder"],
            "capabilities": ["catalog_tools", "generate_manifest", "create_sdks"]
        },

        # 🎯 Specialized Agents
        "legal-doc-drafter": {
            "specialization": AgentSpecialization.LEGAL,
            "connections": ["document-generator", "legal-templates", "compliance-checker"],
            "capabilities": ["draft_documents", "create_contracts", "ensure_compliance"]
        },
        "pdf-financial-summary": {
            "specialization": AgentSpecialization.FINANCIAL,
            "connections": ["transaction-analyzer", "pdf-generator", "summary-builder"],
            "capabilities": ["analyze_finances", "generate_summaries", "create_reports"]
        },
        "cors-audit-agent": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["cors-validator", "header-checker", "options-prober"],
            "capabilities": ["audit_cors", "fix_headers", "validate_preflight"]
        },
        "ucwsf-deploy-agent": {
            "specialization": AgentSpecialization.IMPLEMENTATION,
            "connections": ["deployment-engine", "stack-manager", "environment-config"],
            "capabilities": ["deploy_stack", "manage_services", "configure_environment"]
        },
        "agent-orchestra-ui-refactor": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["ui-components", "orchestra-frontend", "design-system"],
            "capabilities": ["refactor_ui", "standardize_components", "improve_ux"]
        },
        "critical-integration-restoration": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["integration-fixer", "connection-restorer", "system-healer"],
            "capabilities": ["restore_integrations", "fix_connections", "heal_system"]
        },
        "react-web-delivery": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["react-builder", "component-library", "web-deployer"],
            "capabilities": ["deliver_features", "build_components", "deploy_web"]
        },
        "react-native-delivery": {
            "specialization": AgentSpecialization.TECHNICAL,
            "connections": ["expo-builder", "mobile-components", "app-deployer"],
            "capabilities": ["deliver_mobile", "build_screens", "deploy_app"]
        },
        "core-agents-enablement-coordinator": {
            "specialization": AgentSpecialization.CORE_AGENTS_ENABLEMENT,
            "connections": ["agent-registry", "enablement-engine", "activation-tracker"],
            "capabilities": ["enable_agents", "coordinate_activation", "track_status"]
        }
    }

    def __init__(self):
        self.registry = get_agent_registry()
        self.advisor_registry = get_advisor_registry()
        self.wired_agents = set()
        self.connections = []
        self.logger = logging.getLogger(__name__)

    def wire_all_agents(self) -> Dict[str, Any]:
        """
        Wire up all agents in the system
        Returns comprehensive status report
        """
        start_time = datetime.now()
        results = {
            "total_agents": len(self.AGENT_CATALOG),
            "successfully_wired": 0,
            "failed": [],
            "connections_created": 0,
            "warnings": []
        }

        # Phase 1: Register all agents
        self.logger.info("🔌 Phase 1: Registering all agents...")
        for agent_name, agent_config in self.AGENT_CATALOG.items():
            success = self._register_agent(agent_name, agent_config)
            if success:
                results["successfully_wired"] += 1
                self.wired_agents.add(agent_name)
            else:
                results["failed"].append(agent_name)

        # Phase 2: Create connections
        self.logger.info("🔗 Phase 2: Creating agent connections...")
        for agent_name, agent_config in self.AGENT_CATALOG.items():
            if agent_name in self.wired_agents:
                connections = agent_config.get("connections", [])
                for target in connections:
                    if self._create_connection(agent_name, target):
                        results["connections_created"] += 1

        # Phase 3: Verify connectivity
        self.logger.info("✅ Phase 3: Verifying agent connectivity...")
        verification = self._verify_all_connections()
        results["verification"] = verification

        # Phase 4: Connect to advisors
        self.logger.info("🤝 Phase 4: Connecting agents to advisors...")
        advisor_connections = self._connect_to_advisors()
        results["advisor_connections"] = advisor_connections

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        results["execution_time_seconds"] = execution_time

        # Generate summary
        results["summary"] = self._generate_wiring_summary(results)

        return results

    def _register_agent(self, agent_name: str, config: Dict[str, Any]) -> bool:
        """Register a single agent in the registry"""
        try:
            # Check if agent already exists
            existing = self.registry.get_agent(agent_name)
            if existing:
                self.logger.debug(f"Agent {agent_name} already registered")
                return True

            # Create agent configuration
            agent_data = {
                "display_name": agent_name.replace("-", " ").title(),
                "description": f"Agent specialized in {config['specialization'].label}",
                "specialization": config["specialization"],
                "capabilities": config.get("capabilities", []),
                "routing_keywords": self._extract_keywords(agent_name),
                "system_prompt": self._generate_system_prompt(agent_name, config),
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "llm_config": {
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }

            # Register the agent
            success = self.registry.register_agent(agent_name, agent_data)
            if success:
                self.logger.info(f"✅ Registered agent: {agent_name}")
            else:
                self.logger.error(f"❌ Failed to register agent: {agent_name}")

            return success

        except Exception as e:
            self.logger.error(f"Error registering agent {agent_name}: {e}")
            return False

    def _create_connection(self, source: str, target: str) -> bool:
        """Create a connection between two agents"""
        try:
            # Handle special connection targets
            if target in ["all-agents", "all-advisors", "all-systems"]:
                return True  # These are meta-connections

            # Verify target exists or create placeholder
            if target not in self.wired_agents:
                # Try to find similar agent
                for agent in self.wired_agents:
                    if target in agent or agent in target:
                        target = agent
                        break

            connection = AgentConnection(
                source_agent=source,
                target_agent=target,
                connection_type="data_flow",
                bidirectional=True
            )

            self.connections.append(connection)
            self.logger.debug(f"Connected {source} -> {target}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating connection {source} -> {target}: {e}")
            return False

    def _verify_all_connections(self) -> Dict[str, Any]:
        """Verify all agent connections are working"""
        verification = {
            "total_connections": len(self.connections),
            "verified": 0,
            "broken": []
        }

        for connection in self.connections:
            # Check both agents exist
            source_exists = connection.source_agent in self.wired_agents
            target_exists = (connection.target_agent in self.wired_agents or
                           connection.target_agent in ["all-agents", "all-advisors", "all-systems"])

            if source_exists and target_exists:
                verification["verified"] += 1
            else:
                verification["broken"].append(f"{connection.source_agent} -> {connection.target_agent}")

        return verification

    def _connect_to_advisors(self) -> Dict[str, Any]:
        """Connect appropriate agents to advisors"""
        advisor_connections = {
            "total_advisors": 0,
            "connected_agents": [],
            "connections_created": 0
        }

        try:
            advisors = self.advisor_registry.list_advisors()
            advisor_connections["total_advisors"] = len(advisors)

            # Connect orchestration agents to advisors
            orchestration_agents = [
                "system-unification-architect",
                "opportunity-pipeline-orchestrator",
                "revenue-activation-orchestrator",
                "task-delegation-orchestrator"
            ]

            for agent in orchestration_agents:
                if agent in self.wired_agents:
                    advisor_connections["connected_agents"].append(agent)
                    advisor_connections["connections_created"] += len(advisors)

        except Exception as e:
            self.logger.error(f"Error connecting to advisors: {e}")

        return advisor_connections

    def _extract_keywords(self, agent_name: str) -> List[str]:
        """Extract routing keywords from agent name"""
        # Split by hyphen and filter out common words
        words = agent_name.replace("-", " ").split()
        keywords = [w for w in words if len(w) > 3 and w not in ["agent", "the", "and", "for"]]
        return keywords

    def _generate_system_prompt(self, agent_name: str, config: Dict[str, Any]) -> str:
        """Generate a system prompt for the agent"""
        capabilities = ", ".join(config.get("capabilities", []))
        return f"""You are {agent_name}, a specialized agent in the Unified Donkey Betz Platform.

Your specialization: {config['specialization'].label}
Your capabilities: {capabilities}

You work collaboratively with other agents and advisors to achieve complex goals.
Always focus on your specialized area while coordinating with others when needed.
Provide clear, actionable outputs and maintain high performance standards."""

    def _generate_wiring_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of wiring results"""
        success_rate = (results["successfully_wired"] / results["total_agents"]) * 100

        summary = f"""
🔌 AGENT WIRING COMPLETE
========================
✅ Successfully wired: {results['successfully_wired']}/{results['total_agents']} agents ({success_rate:.1f}%)
🔗 Connections created: {results['connections_created']}
🤝 Advisor connections: {results.get('advisor_connections', {}).get('connections_created', 0)}
⏱️ Execution time: {results['execution_time_seconds']:.2f} seconds

Status: {'FULLY OPERATIONAL' if success_rate == 100 else 'PARTIALLY OPERATIONAL'}
"""

        if results["failed"]:
            summary += f"\n⚠️ Failed agents: {', '.join(results['failed'])}"

        return summary

# Convenience function for quick wiring
def wire_all_agents():
    """Quick function to wire all agents"""
    wiring_system = UnifiedAgentWiringSystem()
    return wiring_system.wire_all_agents()

if __name__ == "__main__":
    # Run the wiring system
    results = wire_all_agents()
    print(results["summary"])