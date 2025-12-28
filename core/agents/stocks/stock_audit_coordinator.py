"""
Stock Audit Coordinator
=======================

Session 461: Orchestrates all stock audit agents.
Equivalent to BlockchainAuditCoordinator in the blockchain audit system.

Key capabilities:
- Coordinates all stock audit agents
- Correlates findings across different analyses
- Manages alert severity and deduplication
- Routes findings to Discord
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class StockAuditCoordinator(BaseAgent):
    """
    Orchestrates all stock audit agents for comprehensive market monitoring.

    Coordinates:
    - StockAnalystAgent: SEC filing analysis
    - MarketMovementMonitorAgent: Price/volume monitoring
    - InstitutionalWatcherAgent: Insider trading tracking
    - MarketAnomalyDetectorAgent: Manipulation detection
    """

    name = "StockAuditCoordinator"

    system_prompt = """You are the stock market audit coordinator responsible for:
1. Orchestrating specialized stock analysis agents
2. Correlating findings across different data sources
3. Managing alert severity and prioritization
4. Ensuring comprehensive market coverage
5. Routing critical findings to stakeholders

Coordination workflow:
1. Gather data from all monitoring agents
2. Correlate findings (e.g., insider selling + price drop)
3. Deduplicate and prioritize alerts
4. Route to appropriate channels (Discord, notifications)

Always prioritize:
- Time-sensitive alerts (active manipulation, breaking news)
- High-severity findings
- Correlated signals (multiple agents flagging same stock)"""

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute coordinated stock audit.

        Args:
            task: Audit task description
            context: Additional context (can specify focus areas)
            scifi_context: Sci-fi features context
            spider_context: Spider data context

        Returns:
            AgentResult with comprehensive audit findings
        """
        start_time = datetime.now()
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        logger.info(f"StockAuditCoordinator executing: {task[:100]}...")

        try:
            # Run all sub-agents
            analyst_results = self._run_stock_analyst(context)
            movement_results = self._run_movement_monitor(context)
            institutional_results = self._run_institutional_watcher(context)
            anomaly_results = self._run_anomaly_detector(context)

            # Correlate findings
            correlated = self._correlate_findings(
                analyst_results,
                movement_results,
                institutional_results,
                anomaly_results
            )

            # Generate unified alerts
            unified_alerts = self._generate_unified_alerts(correlated)

            # Session 461: Auto-consult Warren Buffett for high-risk findings
            advisor_consultations = self._request_advisor_consultations(unified_alerts)

            # Send to Discord if configured
            discord_sent = self._send_to_discord(unified_alerts)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            summary = self._generate_summary(unified_alerts)

            result = AgentResult(
                success=True,
                message=f"Stock audit complete. {len(unified_alerts)} alerts generated.",
                data={
                    'analyst_results': analyst_results,
                    'movement_results': movement_results,
                    'institutional_results': institutional_results,
                    'anomaly_results': anomaly_results,
                    'correlated_findings': correlated,
                    'unified_alerts': unified_alerts,
                    'advisor_consultations': advisor_consultations,  # Session 461
                    'discord_sent': discord_sent,
                    'summary': summary,
                },
                agent_name=self.name,
                execution_time_ms=execution_time
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
                        'total_alerts': summary.get('total_alerts', 0),
                        'critical_alerts': summary.get('critical', 0),
                        'correlated_findings': summary.get('correlated_findings', 0),
                    }
                )
            except Exception as le:
                logger.warning(f"Failed to record learning outcome: {le}")

            return result

        except Exception as e:
            logger.error(f"StockAuditCoordinator error: {e}")
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

    def _run_stock_analyst(self, context: Dict) -> Dict[str, Any]:
        """Run the StockAnalystAgent."""
        try:
            from .stock_analyst_agent import StockAnalystAgent
            agent = StockAnalystAgent()
            result = agent.execute(
                task="Analyze recent SEC filings for material information",
                context=context
            )
            return result.to_dict() if hasattr(result, 'to_dict') else {'data': result.data if hasattr(result, 'data') else {}}
        except Exception as e:
            logger.error(f"StockAnalystAgent error: {e}")
            return {'error': str(e)}

    def _run_movement_monitor(self, context: Dict) -> Dict[str, Any]:
        """Run the MarketMovementMonitorAgent."""
        try:
            from .market_movement_monitor_agent import MarketMovementMonitorAgent
            agent = MarketMovementMonitorAgent()
            result = agent.execute(
                task="Scan for unusual price and volume movements",
                context=context
            )
            return result.to_dict() if hasattr(result, 'to_dict') else {'data': result.data if hasattr(result, 'data') else {}}
        except Exception as e:
            logger.error(f"MarketMovementMonitorAgent error: {e}")
            return {'error': str(e)}

    def _run_institutional_watcher(self, context: Dict) -> Dict[str, Any]:
        """Run the InstitutionalWatcherAgent."""
        try:
            from .institutional_watcher_agent import InstitutionalWatcherAgent
            agent = InstitutionalWatcherAgent()
            result = agent.execute(
                task="Monitor insider trading and institutional activity",
                context=context
            )
            return result.to_dict() if hasattr(result, 'to_dict') else {'data': result.data if hasattr(result, 'data') else {}}
        except Exception as e:
            logger.error(f"InstitutionalWatcherAgent error: {e}")
            return {'error': str(e)}

    def _run_anomaly_detector(self, context: Dict) -> Dict[str, Any]:
        """Run the MarketAnomalyDetectorAgent."""
        try:
            from .market_anomaly_detector_agent import MarketAnomalyDetectorAgent
            agent = MarketAnomalyDetectorAgent()
            result = agent.execute(
                task="Detect market anomalies and potential manipulation",
                context=context
            )
            return result.to_dict() if hasattr(result, 'to_dict') else {'data': result.data if hasattr(result, 'data') else {}}
        except Exception as e:
            logger.error(f"MarketAnomalyDetectorAgent error: {e}")
            return {'error': str(e)}

    def _correlate_findings(self, analyst: Dict, movement: Dict,
                            institutional: Dict, anomaly: Dict) -> List[Dict]:
        """Correlate findings across all agents."""
        correlated = []

        # Extract alerts/findings from each agent
        movement_alerts = movement.get('data', {}).get('alerts', [])
        institutional_alerts = institutional.get('data', {}).get('alerts', [])
        anomaly_alerts = anomaly.get('data', {}).get('anomalies', [])

        # Build ticker index
        ticker_findings = {}

        for alert in movement_alerts:
            ticker = alert.get('ticker', '')
            if ticker:
                ticker_findings.setdefault(ticker, {'sources': [], 'alerts': []})
                ticker_findings[ticker]['sources'].append('movement')
                ticker_findings[ticker]['alerts'].append(alert)

        for alert in institutional_alerts:
            ticker = alert.get('company', alert.get('ticker', ''))
            # Try to extract ticker from company name
            if ticker:
                ticker_findings.setdefault(ticker, {'sources': [], 'alerts': []})
                ticker_findings[ticker]['sources'].append('institutional')
                ticker_findings[ticker]['alerts'].append(alert)

        for alert in anomaly_alerts:
            ticker = alert.get('ticker', '')
            if ticker:
                ticker_findings.setdefault(ticker, {'sources': [], 'alerts': []})
                ticker_findings[ticker]['sources'].append('anomaly')
                ticker_findings[ticker]['alerts'].append(alert)

        # Find correlated findings (multiple sources flagging same ticker)
        for ticker, data in ticker_findings.items():
            unique_sources = list(set(data['sources']))

            if len(unique_sources) >= 2:
                # Multiple agents flagged this ticker - correlated finding
                correlated.append({
                    'ticker': ticker,
                    'correlation_strength': len(unique_sources),
                    'sources': unique_sources,
                    'alerts': data['alerts'],
                    'is_correlated': True,
                })
            else:
                correlated.append({
                    'ticker': ticker,
                    'correlation_strength': 1,
                    'sources': unique_sources,
                    'alerts': data['alerts'],
                    'is_correlated': False,
                })

        # Sort by correlation strength
        correlated.sort(key=lambda x: x['correlation_strength'], reverse=True)

        return correlated

    def _generate_unified_alerts(self, correlated: List[Dict]) -> List[Dict]:
        """Generate unified alerts from correlated findings."""
        unified = []

        for finding in correlated:
            # Determine severity based on correlation and individual alert severities
            severities = []
            for alert in finding.get('alerts', []):
                severities.append(alert.get('severity', 'LOW'))

            # Upgrade severity if correlated
            if finding.get('is_correlated'):
                if 'HIGH' in severities:
                    final_severity = 'CRITICAL'
                elif 'MEDIUM' in severities:
                    final_severity = 'HIGH'
                else:
                    final_severity = 'MEDIUM'
            else:
                if 'CRITICAL' in severities:
                    final_severity = 'CRITICAL'
                elif 'HIGH' in severities:
                    final_severity = 'HIGH'
                elif 'MEDIUM' in severities:
                    final_severity = 'MEDIUM'
                else:
                    final_severity = 'LOW'

            # Build unified alert
            alert_types = []
            for alert in finding.get('alerts', []):
                alert_types.append(alert.get('type', 'UNKNOWN'))

            unified.append({
                'ticker': finding['ticker'],
                'severity': final_severity,
                'is_correlated': finding.get('is_correlated', False),
                'correlation_strength': finding.get('correlation_strength', 1),
                'sources': finding.get('sources', []),
                'alert_types': list(set(alert_types)),
                'details': finding.get('alerts', []),
                'message': self._format_unified_message(finding, final_severity),
            })

        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        unified.sort(key=lambda x: severity_order.get(x['severity'], 4))

        return unified

    def _format_unified_message(self, finding: Dict, severity: str) -> str:
        """Format a unified alert message."""
        ticker = finding['ticker']
        sources = finding.get('sources', [])
        is_correlated = finding.get('is_correlated', False)

        if is_correlated:
            return f"[{severity}] CORRELATED ALERT: {ticker} flagged by {len(sources)} systems ({', '.join(sources)})"
        else:
            return f"[{severity}] {ticker}: {', '.join(sources)} alert"

    def _send_to_discord(self, alerts: List[Dict]) -> int:
        """Send high-priority alerts to Discord."""
        try:
            from core.services.discord_notifications import discord_notify

            sent = 0
            for alert in alerts:
                if alert['severity'] in ['CRITICAL', 'HIGH']:
                    success = discord_notify.send_stock_alert(
                        ticker=alert['ticker'],
                        severity=alert['severity'],
                        alert_type=', '.join(alert.get('alert_types', ['ALERT'])),
                        message=alert['message'],
                        details=alert.get('details', []),
                        is_correlated=alert.get('is_correlated', False)
                    )
                    if success:
                        sent += 1

            return sent

        except Exception as e:
            logger.error(f"Discord notification error: {e}")
            return 0

    def _request_advisor_consultations(self, alerts: List[Dict]) -> List[Dict]:
        """
        Session 461: Auto-consult Warren Buffett for high-risk stock findings.

        When CRITICAL or HIGH severity alerts are detected, automatically
        request consultation from the Warren Buffett advisor to get
        value investing perspective on the situation.

        Args:
            alerts: List of unified alerts with severity ratings

        Returns:
            List of advisor consultation results
        """
        consultations = []

        # Filter for high-risk alerts
        high_risk_alerts = [a for a in alerts if a.get('severity') in ['CRITICAL', 'HIGH']]

        if not high_risk_alerts:
            return consultations

        try:
            from advisors.registry import get_advisor_registry
            from advisors.llm_advisor_system import get_llm_advisor_system

            registry = get_advisor_registry()
            llm_system = get_llm_advisor_system()

            # Get Warren Buffett advisor
            buffett = registry.get_advisor('warren_buffett_advisor')
            if not buffett:
                logger.warning("Warren Buffett advisor not found in registry")
                return consultations

            for alert in high_risk_alerts[:3]:  # Limit to 3 consultations per cycle
                ticker = alert.get('ticker', 'UNKNOWN')
                severity = alert.get('severity', 'HIGH')
                message = alert.get('message', '')
                details = alert.get('details', [])

                # Build consultation question
                question = f"""
Stock Alert Analysis Request:

Ticker: {ticker}
Severity: {severity}
Alert: {message}

Details:
{chr(10).join('- ' + str(d) for d in details[:5])}

As a value investor, what's your perspective on this situation?
Should an investor be concerned? What would you recommend?
"""

                try:
                    # Get LLM-powered consultation
                    response = llm_system.consult(
                        advisor_id='warren_buffett_advisor',
                        question=question,
                        context={
                            'ticker': ticker,
                            'severity': severity,
                            'alert_type': 'stock_audit',
                            'is_correlated': alert.get('is_correlated', False),
                        }
                    )

                    consultation = {
                        'ticker': ticker,
                        'severity': severity,
                        'advisor': 'Warren Buffett (AI)',
                        'question': question[:200] + '...',
                        'response': response.get('response', 'No response'),
                        'confidence': response.get('confidence', 0.7),
                        'timestamp': datetime.now().isoformat(),
                        'alert_type': 'stock_audit',  # Session 461: For learning tracking
                    }

                    # Add advisor perspective to the alert
                    alert['advisor_perspective'] = consultation

                    consultations.append(consultation)

                    # Session 461: Track consultation for learning
                    try:
                        from core.learning_bridges.advisor_feedback_bridge import track_audit_advisor_consultation
                        track_audit_advisor_consultation(consultation)
                    except Exception as track_err:
                        logger.warning(f"Could not track consultation for learning: {track_err}")

                    logger.info(f"📊 Warren Buffett consultation complete for {ticker}")

                except Exception as e:
                    logger.error(f"Advisor consultation error for {ticker}: {e}")

            if consultations:
                logger.info(f"✅ Completed {len(consultations)} advisor consultations for high-risk alerts")

        except ImportError as e:
            logger.warning(f"Advisor system not available: {e}")
        except Exception as e:
            logger.error(f"Advisor consultation system error: {e}")

        return consultations

    def _generate_summary(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Generate a summary of the audit."""
        return {
            'total_alerts': len(alerts),
            'critical': len([a for a in alerts if a['severity'] == 'CRITICAL']),
            'high': len([a for a in alerts if a['severity'] == 'HIGH']),
            'medium': len([a for a in alerts if a['severity'] == 'MEDIUM']),
            'low': len([a for a in alerts if a['severity'] == 'LOW']),
            'correlated_findings': len([a for a in alerts if a.get('is_correlated')]),
            'tickers_flagged': list(set(a['ticker'] for a in alerts if a.get('ticker'))),
        }


def run_stock_audit_cycle() -> Dict[str, Any]:
    """
    Convenience function to run a full stock audit cycle.
    Can be called from Celery tasks or autonomous loop.
    """
    coordinator = StockAuditCoordinator()
    result = coordinator.execute(task="Run comprehensive stock market audit")
    return result.to_dict() if hasattr(result, 'to_dict') else {'data': result.data if hasattr(result, 'data') else {}}
