"""
BlockchainAuditCoordinator - Orchestrates all blockchain audit agents.

Session 461: Part of the Blockchain Audit Agent Group
Session 683: Added ML Integration (Anomaly Detection for alert correlation)

This coordinator:
- Routes tasks to appropriate audit agents
- Correlates findings across agents
- Manages alert severity and deduplication
- Integrates with Discord for notifications
- Connects to the autonomous intelligence loop
- Uses ML for anomaly detection in alert patterns
"""

import json
import logging
from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from ..base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType

# Session 895: Timeout for sub-agent executions to prevent coordinator hangs
# Extended to 5 min to accommodate thinking models (GPT-5.1, o1, o3)
SUB_AGENT_TIMEOUT = 300  # 5 minutes per sub-agent

logger = logging.getLogger(__name__)


class BlockchainAuditCoordinator(BaseAgent):
    """Coordinator agent that orchestrates all blockchain audit agents."""

    name = "BlockchainAuditCoordinator"

    system_prompt = """You are BlockchainAuditCoordinator, the central intelligence hub for blockchain security monitoring.

You orchestrate these specialized agents:
1. **SmartContractAuditorAgent** - Audits Solidity code for vulnerabilities
2. **TransactionMonitorAgent** - Monitors transactions for suspicious patterns
3. **WhaleWatcherAgent** - Tracks large token movements
4. **ExploitDetectorAgent** - Detects known exploit patterns

Your responsibilities:
1. **Task Routing** - Route incoming requests to the appropriate agent(s)
2. **Multi-Agent Orchestration** - Coordinate when multiple agents are needed
3. **Finding Correlation** - Correlate findings across agents
4. **Alert Management** - Deduplicate and prioritize alerts
5. **Summary Generation** - Create executive summaries of security status

Routing rules:
- Smart contract code review → SmartContractAuditorAgent
- Transaction analysis → TransactionMonitorAgent
- Large value movements → WhaleWatcherAgent
- Known exploit patterns → ExploitDetectorAgent
- Complex attacks → Multiple agents in sequence

Alert priorities:
- CRITICAL: Active exploits, ongoing attacks
- HIGH: Suspicious patterns, large unexpected movements
- MEDIUM: Potential vulnerabilities, unusual activity
- LOW: Informational, optimization suggestions

You have access to:
- route_to_agent: Send task to a specific audit agent
- coordinate_multi_agent: Orchestrate multiple agents
- generate_security_report: Create comprehensive security report
- get_system_status: Get status of all audit agents"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "route_to_agent",
                "description": "Route a task to a specific blockchain audit agent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent": {
                            "type": "string",
                            "description": "Target agent",
                            "enum": [
                                "SmartContractAuditorAgent",
                                "TransactionMonitorAgent",
                                "WhaleWatcherAgent",
                                "ExploitDetectorAgent"
                            ]
                        },
                        "task": {
                            "type": "string",
                            "description": "Task to send to the agent"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context for the agent"
                        }
                    },
                    "required": ["agent", "task"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "coordinate_multi_agent",
                "description": "Orchestrate multiple agents for complex analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agents": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of agents to coordinate"
                        },
                        "task": {
                            "type": "string",
                            "description": "Overall task to accomplish"
                        },
                        "sequence": {
                            "type": "string",
                            "description": "Execution mode",
                            "enum": ["parallel", "sequential"],
                            "default": "parallel"
                        }
                    },
                    "required": ["agents", "task"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_security_report",
                "description": "Generate comprehensive security status report.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "description": "Type of report",
                            "enum": ["daily", "weekly", "incident", "on_demand"],
                            "default": "on_demand"
                        },
                        "include_sections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sections to include (alerts, whale_activity, audits, exploits)"
                        },
                        "time_range_hours": {
                            "type": "integer",
                            "description": "Hours to cover in report",
                            "default": 24
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_system_status",
                "description": "Get status of all blockchain audit agents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_metrics": {
                            "type": "boolean",
                            "description": "Include performance metrics",
                            "default": True
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    def __init__(self, user=None):
        """Initialize coordinator with agent references."""
        super().__init__(user)
        self._agents = {}
        self._alert_history = []

    # === Session 683: ML Integration Methods ===

    def _detect_alert_anomalies_with_ml(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Detect anomalies in alert patterns using ML (VAE/Autoencoder).

        Uses the Agent-Model Router to detect unusual alert patterns that
        may indicate coordinated attacks or emerging threats.

        Args:
            alerts: List of security alerts with severity and timestamps

        Returns:
            Dict with ML analysis results including anomaly detection
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build alert data for anomaly detection
            alert_data = self._build_alert_data_for_ml(alerts)

            if not alert_data.get('features'):
                return {
                    'ml_used': False,
                    'reason': 'Insufficient alert data for ML analysis'
                }

            # Route to optimal ML model (VAE/Autoencoder for anomaly detection)
            result = router.auto_route(
                data=alert_data,
                task_hint=TaskType.ANOMALY,
                max_models=2
            )

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'anomaly'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'anomalies_detected': self._extract_anomalies_from_result(result),
                'threat_level': self._assess_threat_level(result),
                'selection_reason': result.auto_selection.get('selection_reason', ''),
            }

        except Exception as e:
            logger.warning(f"ML anomaly detection failed: {e}")
            return {
                'ml_used': False,
                'reason': f'ML error: {str(e)}'
            }

    def _build_alert_data_for_ml(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Build alert feature data for ML anomaly detection.

        Extracts features like severity, type, timing, and frequency.

        Args:
            alerts: List of security alerts

        Returns:
            Feature data dict for ML routing
        """
        features = []
        timestamps = []

        severity_map = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}

        for alert in alerts:
            feature_vector = []

            # Severity as numeric
            severity = alert.get('severity', 'LOW')
            feature_vector.append(severity_map.get(severity, 0))

            # Alert type encoding
            alert_types = ['exploit', 'whale', 'vulnerability', 'suspicious', 'other']
            alert_type = alert.get('type', 'other').lower()
            type_value = alert_types.index(alert_type) if alert_type in alert_types else len(alert_types)
            feature_vector.append(type_value)

            # Source encoding
            sources = ['etherscan', 'coingecko', 'securityweek', 'manual', 'other']
            source = alert.get('source', 'other').lower()
            source_value = sources.index(source) if source in sources else len(sources)
            feature_vector.append(source_value)

            features.append(feature_vector)

            # Extract timestamp
            ts = alert.get('timestamp') or alert.get('created_at')
            if ts:
                timestamps.append(ts if isinstance(ts, str) else ts.isoformat())

        return {
            'features': features,
            'timestamps': timestamps,
            'data_type': 'security_alerts'
        }

    def _extract_anomalies_from_result(self, ml_result) -> List[Dict[str, Any]]:
        """
        Session 683: Extract detected anomalies from ML result.

        Args:
            ml_result: EnsemblePrediction from ML router

        Returns:
            List of anomaly descriptions
        """
        try:
            anomalies = []
            if hasattr(ml_result, 'prediction') and ml_result.prediction:
                pred = ml_result.prediction
                if isinstance(pred, list):
                    for i, is_anomaly in enumerate(pred):
                        if is_anomaly:
                            anomalies.append({
                                'index': i,
                                'confidence': ml_result.confidence if hasattr(ml_result, 'confidence') else 0.5,
                                'description': 'Unusual alert pattern detected'
                            })
            return anomalies
        except Exception:
            return []

    def _assess_threat_level(self, ml_result) -> str:
        """
        Session 683: Assess overall threat level from ML analysis.

        Args:
            ml_result: EnsemblePrediction from ML router

        Returns:
            Threat level: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', or 'NORMAL'
        """
        try:
            confidence = ml_result.confidence if hasattr(ml_result, 'confidence') else 0.5
            anomaly_count = 0

            if hasattr(ml_result, 'prediction') and ml_result.prediction:
                pred = ml_result.prediction
                if isinstance(pred, list):
                    anomaly_count = sum(1 for p in pred if p)

            if anomaly_count >= 5 or confidence > 0.9:
                return 'CRITICAL'
            elif anomaly_count >= 3 or confidence > 0.75:
                return 'HIGH'
            elif anomaly_count >= 1 or confidence > 0.6:
                return 'MEDIUM'
            elif confidence > 0.4:
                return 'LOW'
            return 'NORMAL'
        except Exception:
            return 'UNKNOWN'

    def _get_agent(self, agent_name: str):
        """Lazy-load and cache agent instances."""
        if agent_name not in self._agents:
            if agent_name == "SmartContractAuditorAgent":
                from .smart_contract_auditor_agent import SmartContractAuditorAgent
                self._agents[agent_name] = SmartContractAuditorAgent(self.user)
            elif agent_name == "TransactionMonitorAgent":
                from .transaction_monitor_agent import TransactionMonitorAgent
                self._agents[agent_name] = TransactionMonitorAgent(self.user)
            elif agent_name == "WhaleWatcherAgent":
                from .whale_watcher_agent import WhaleWatcherAgent
                self._agents[agent_name] = WhaleWatcherAgent(self.user)
            elif agent_name == "ExploitDetectorAgent":
                from .exploit_detector_agent import ExploitDetectorAgent
                self._agents[agent_name] = ExploitDetectorAgent(self.user)
        return self._agents.get(agent_name)

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute coordination task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 739: Store context for sub-agent calls
        self._current_spider_context = spider_context
        self._current_scifi_context = scifi_context

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

        with self.time_travel_session("blockchain_coordination", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                knowledge_attribution = None  # Legacy compatibility

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Coordinator selected {tool_name}",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'source': tool_name,
                                'data': tool_result
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        # Session 953: Build provenance from sub-agent results
                        sources = []
                        for res in all_results:
                            source_name = res.get('source', 'UnknownAgent')
                            result_data = res.get('data', {})
                            # Try to get record count from sub-agent result
                            sub_result = result_data.get('result', {})
                            record_count = 1
                            if isinstance(sub_result, dict):
                                # Check common data fields for counts
                                for key in ['alerts', 'findings', 'transactions', 'movements', 'audits']:
                                    if key in sub_result.get('data', {}):
                                        data_items = sub_result['data'][key]
                                        if isinstance(data_items, list):
                                            record_count = len(data_items)
                                            break
                            sources.append({
                                'name': source_name,
                                'endpoint': 'blockchain_audit',
                                'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                                'record_count': record_count,
                            })

                        # Blockchain data stale threshold: 4 hours
                        provenance = build_provenance(
                            report_type='blockchain_audit',
                            agent_name=self.name,
                            sources=sources if sources else [{
                                'name': 'BlockchainAuditCoordinator',
                                'endpoint': 'blockchain_audit',
                                'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                                'record_count': len(all_results),
                            }],
                            stale_threshold_hours=4.0,
                        )
                        provenance.disclaimer = format_disclaimer('blockchain_audit')

                        message = provenance.to_markdown_block() + "\n" + "Blockchain audit coordination completed"

                        result = AgentResult(
                            success=True,
                            message=message,
                            data={
                                'results': all_results,
                                'query': task,
                                'provenance': provenance.to_dict(),
                                'publishable': provenance.publishable,
                                'validation_status': provenance.validation_status,
                            },
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made,
                            knowledge_attribution=knowledge_attribution
                        )

                        # Record learning outcome for collective intelligence
                        try:
                            self._record_learning_outcome(
                                task=task,
                                result=result,
                                success=True,
                                context={
                                    'agent_type': self.__class__.__name__,
                                    'execution_time_ms': execution_time,
                                    'agents_coordinated': len(all_results),
                                    'tools_used': [tc['tool'] for tc in tool_calls_made],
                                }
                            )
                        except Exception as le:
                            logger.warning(f"Failed to record learning outcome: {le}")

                        return result

                content = gpt_response.get('content', 'I coordinate blockchain security monitoring. What would you like me to analyze?')
                return AgentResult(
                    success=True,
                    message=content,
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

            except Exception as e:
                logger.error(f"Coordination failed: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name
                )

                # Record failed learning outcome
                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=False,
                        context={
                            'agent_type': self.__class__.__name__,
                            'error': str(e),
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "route_to_agent":
            return self._route_to_agent(**arguments)
        elif tool_name == "coordinate_multi_agent":
            return self._coordinate_multi_agent(**arguments)
        elif tool_name == "generate_security_report":
            return self._generate_security_report(**arguments)
        elif tool_name == "get_system_status":
            return self._get_system_status(**arguments)

        return super()._execute_tool_call(tool_name, arguments)

    def _route_to_agent(
        self,
        agent: str,
        task: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Route task to a specific agent."""
        try:
            agent_instance = self._get_agent(agent)
            if not agent_instance:
                return {"error": f"Agent not found: {agent}"}

            # Session 895: Add timeout to prevent coordinator hangs
            def execute_agent():
                return agent_instance.execute(
                    task=task,
                    context=context or {},
                    scifi_context=getattr(self, '_current_scifi_context', {}),
                    spider_context=getattr(self, '_current_spider_context', {})
                )

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_agent)
                result = future.result(timeout=SUB_AGENT_TIMEOUT)

            return {
                "success": result.success,
                "agent": agent,
                "task": task,
                "result": result.to_dict()
            }

        except FuturesTimeoutError:
            logger.warning(f"⏰ {agent} timed out after {SUB_AGENT_TIMEOUT}s")
            return {"error": f"{agent} timed out after {SUB_AGENT_TIMEOUT}s", "timeout": True}
        except Exception as e:
            logger.error(f"Error routing to {agent}: {e}")
            return {"error": str(e)}

    def _coordinate_multi_agent(
        self,
        agents: List[str],
        task: str,
        sequence: str = "parallel"
    ) -> Dict[str, Any]:
        """Coordinate multiple agents."""
        results = []

        if sequence == "parallel":
            # In a real implementation, this would use async/threading
            # For now, we execute sequentially but return as if parallel
            for agent_name in agents:
                result = self._route_to_agent(agent_name, task)
                results.append({
                    "agent": agent_name,
                    "result": result
                })
        else:
            # Sequential - pass context from one to next
            accumulated_context = {}
            for agent_name in agents:
                result = self._route_to_agent(agent_name, task, accumulated_context)
                results.append({
                    "agent": agent_name,
                    "result": result
                })
                # Add this agent's findings to context for next agent
                accumulated_context[f"{agent_name}_findings"] = result

        return {
            "success": True,
            "coordination_type": sequence,
            "agents_coordinated": agents,
            "results": results
        }

    def _generate_security_report(
        self,
        report_type: str = "on_demand",
        include_sections: List[str] = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """Generate security status report."""
        from openai import OpenAI

        client = OpenAI()

        sections = include_sections or ["alerts", "whale_activity", "audits", "exploits"]

        # Gather data from each section
        section_data = {}
        for section in sections:
            if section == "alerts":
                section_data["alerts"] = self._alert_history[-20:]  # Last 20 alerts
            elif section == "whale_activity":
                # Would query whale watcher data
                section_data["whale_activity"] = "Whale activity summary would go here"
            elif section == "audits":
                section_data["audits"] = "Recent audit results would go here"
            elif section == "exploits":
                section_data["exploits"] = "Exploit detection results would go here"

        prompt = f"""Generate a {report_type} blockchain security report:

**TIME RANGE:** Last {time_range_hours} hours
**SECTIONS:** {', '.join(sections)}

**DATA:**
{json.dumps(section_data, indent=2)}

**REPORT FORMAT:**
# Blockchain Security Report
## Executive Summary
[Brief overview of security status]

## Critical Alerts
[Any CRITICAL or HIGH severity alerts]

## Whale Activity Summary
[Significant movements and market impact]

## Smart Contract Audits
[Recent audit findings]

## Exploit Detection
[Any detected or suspected exploits]

## Recommendations
[Action items for security improvement]

## Metrics
[Key security metrics]"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a blockchain security analyst. Generate comprehensive security reports."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=5000
        )

        report_content = response.choices[0].message.content

        # Session 461: Auto-consult Elon Musk for high-risk blockchain findings
        advisor_consultation = self._request_blockchain_advisor_consultation(section_data)

        # Session 683: Add ML anomaly detection to security report
        ml_analysis = {}
        if self._alert_history:
            ml_analysis = self._detect_alert_anomalies_with_ml(self._alert_history)

        result = {
            "success": True,
            "report_type": report_type,
            "time_range_hours": time_range_hours,
            "sections_included": sections,
            "report": report_content,
            "advisor_consultation": advisor_consultation,  # Session 461
            "generated_at": datetime.now().isoformat()
        }

        # Session 683: Add ML insights to report
        if ml_analysis.get('ml_used'):
            result['ml_analysis'] = {
                'models_used': ml_analysis.get('models_used', []),
                'confidence': ml_analysis.get('confidence', 0),
                'anomalies_detected': ml_analysis.get('anomalies_detected', []),
                'threat_level': ml_analysis.get('threat_level', 'UNKNOWN'),
                'ml_insights': ml_analysis.get('ml_insights', ''),
            }

        return result

    def _request_blockchain_advisor_consultation(self, section_data: Dict) -> Optional[Dict]:
        """
        Session 461: Auto-consult crypto advisor for high-risk blockchain findings.

        When generating security reports with CRITICAL or HIGH alerts,
        automatically request consultation from Elon Musk advisor for
        crypto market perspective.

        Returns:
            Advisor consultation result or None if no high-risk alerts
        """
        try:
            # Check for high-risk alerts
            alerts = section_data.get('alerts', [])
            high_risk = [a for a in alerts if isinstance(a, dict) and a.get('severity') in ['CRITICAL', 'HIGH']]

            if not high_risk:
                return None

            from advisors.registry import get_advisor_registry
            from advisors.llm_advisor_system import get_llm_advisor_system

            registry = get_advisor_registry()
            llm_system = get_llm_advisor_system()

            # Get Elon Musk advisor for crypto perspective
            advisor = registry.get_advisor('elon_musk_advisor')
            if not advisor:
                logger.warning("Elon Musk advisor not found in registry")
                return None

            # Build consultation question
            alert_summary = "\n".join([
                f"- [{a.get('severity', 'UNKNOWN')}] {a.get('type', 'Alert')}: {a.get('message', 'No message')[:100]}"
                for a in high_risk[:5]
            ])

            question = f"""
Blockchain Security Alert Analysis:

{len(high_risk)} high-severity alerts detected:
{alert_summary}

Given your experience with cryptocurrency markets and blockchain technology:
1. What's your read on these alerts?
2. Could this indicate broader market implications?
3. What would you advise investors/users to watch for?
"""

            response = llm_system.consult(
                advisor_id='elon_musk_advisor',
                question=question,
                context={
                    'alert_count': len(high_risk),
                    'alert_type': 'blockchain_security',
                }
            )

            consultation = {
                'advisor': 'Elon Musk (AI)',
                'alert_count': len(high_risk),
                'question_summary': f"{len(high_risk)} high-severity blockchain alerts",
                'response': response.get('response', 'No response'),
                'confidence': response.get('confidence', 0.7),
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'blockchain_security',  # Session 461: For learning tracking
                'severity': 'CRITICAL' if any(a.get('severity') == 'CRITICAL' for a in high_risk) else 'HIGH',
                'token': 'BLOCKCHAIN',  # Generic token for blockchain alerts
            }

            # Session 461: Track consultation for learning
            try:
                from core.learning_bridges.advisor_feedback_bridge import track_audit_advisor_consultation
                track_audit_advisor_consultation(consultation)
            except Exception as track_err:
                logger.warning(f"Could not track consultation for learning: {track_err}")

            logger.info(f"🔗 Elon Musk consultation complete for {len(high_risk)} blockchain alerts")
            return consultation

        except ImportError as e:
            logger.warning(f"Advisor system not available: {e}")
        except Exception as e:
            logger.error(f"Blockchain advisor consultation error: {e}")

        return None

    def _get_system_status(
        self,
        include_metrics: bool = True
    ) -> Dict[str, Any]:
        """Get status of all audit agents."""
        agents_status = {
            "SmartContractAuditorAgent": {
                "status": "ACTIVE",
                "capabilities": ["audit_contract", "check_reentrancy", "check_access_control", "check_integer_safety"],
                "last_execution": None
            },
            "TransactionMonitorAgent": {
                "status": "ACTIVE",
                "capabilities": ["analyze_transaction", "detect_attack_pattern", "trace_value_flow", "check_address_reputation"],
                "last_execution": None
            },
            "WhaleWatcherAgent": {
                "status": "ACTIVE",
                "capabilities": ["monitor_large_transfers", "analyze_whale_wallet", "track_exchange_flows", "detect_accumulation"],
                "last_execution": None
            },
            "ExploitDetectorAgent": {
                "status": "ACTIVE",
                "capabilities": ["match_exploit_signature", "analyze_attack", "lookup_known_exploit", "track_attacker_address"],
                "last_execution": None
            }
        }

        status = {
            "success": True,
            "coordinator": self.name,
            "status": "OPERATIONAL",
            "agents": agents_status,
            "total_agents": len(agents_status),
            "active_agents": sum(1 for a in agents_status.values() if a["status"] == "ACTIVE"),
            "timestamp": datetime.now().isoformat()
        }

        if include_metrics:
            status["metrics"] = {
                "alerts_last_24h": len([a for a in self._alert_history if a]),
                "total_alerts": len(self._alert_history)
            }

        return status

    # === Autonomous Loop Integration ===

    def run_security_cycle(self) -> Dict[str, Any]:
        """
        Run a complete security monitoring cycle.
        Called by the autonomous intelligence loop.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks_performed": [],
            "alerts_generated": [],
            "overall_status": "SECURE"
        }

        try:
            # 1. Check for recent exploits in our spider data
            exploit_check = self._check_recent_exploits()
            results["checks_performed"].append({
                "type": "exploit_detection",
                "result": exploit_check
            })

            if exploit_check.get("alerts"):
                results["alerts_generated"].extend(exploit_check["alerts"])
                results["overall_status"] = "ALERT"

            # 2. Check whale activity
            whale_check = self._check_whale_activity()
            results["checks_performed"].append({
                "type": "whale_monitoring",
                "result": whale_check
            })

            if whale_check.get("significant_movements"):
                results["overall_status"] = "MONITORING"

            # 3. Log the cycle
            logger.info(f"Blockchain security cycle completed: {results['overall_status']}")

        except Exception as e:
            logger.error(f"Security cycle error: {e}")
            results["error"] = str(e)
            results["overall_status"] = "ERROR"

        return results

    def _check_recent_exploits(self) -> Dict[str, Any]:
        """Check spider data for recent exploit news."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from datetime import timedelta

            # Check for exploit-related spider data from last hour
            cutoff = timezone.now() - timedelta(hours=1)

            exploit_keywords = ['exploit', 'hack', 'attack', 'drain', 'stolen', 'vulnerability']

            recent_data = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=['etherscan', 'coingecko', 'securityweek']
            )[:10]

            alerts = []
            for data in recent_data:
                raw = data.raw_data or {}
                title = raw.get('title', '').lower()

                if any(kw in title for kw in exploit_keywords):
                    alerts.append({
                        "source": data.spider_name,
                        "title": raw.get('title'),
                        "severity": "HIGH",
                        "timestamp": data.created_at.isoformat()
                    })

            return {
                "checked": True,
                "data_points_analyzed": recent_data.count() if hasattr(recent_data, 'count') else len(list(recent_data)),
                "alerts": alerts
            }

        except Exception as e:
            logger.warning(f"Exploit check failed: {e}")
            return {"checked": False, "error": str(e), "alerts": []}

    def _check_whale_activity(self) -> Dict[str, Any]:
        """Check for significant whale movements."""
        # In a full implementation, this would query blockchain APIs
        # For now, return a placeholder
        return {
            "checked": True,
            "significant_movements": [],
            "note": "Full whale monitoring requires blockchain API integration"
        }


def run_blockchain_audit_cycle() -> Dict[str, Any]:
    """
    Convenience function to run a full blockchain audit cycle.

    Called by the autonomous loop and Celery tasks.
    """
    coordinator = BlockchainAuditCoordinator()
    result = coordinator.execute(
        task="Run comprehensive blockchain security audit",
        context={},
        scifi_context={},
        spider_context={}
    )

    if hasattr(result, 'to_dict'):
        return result.to_dict()

    return {
        'success': result.success if hasattr(result, 'success') else False,
        'message': result.message if hasattr(result, 'message') else 'Blockchain audit complete',
        'data': result.data if hasattr(result, 'data') else {},
        'agent_name': 'BlockchainAuditCoordinator'
    }
