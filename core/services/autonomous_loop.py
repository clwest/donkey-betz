"""
Autonomous Intelligence Loop - Session 460

The conductor that makes all the pieces work together:
- Monitors spider data for high-value opportunities
- Routes to agents for analysis
- Generates alerts to Discord
- Creates content opportunities

This is the missing piece that transforms isolated components
into a self-operating intelligence machine.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

from django.db.models import Count
from django.utils import timezone as dj_timezone

logger = logging.getLogger(__name__)


class AutonomousIntelligenceLoop:
    """
    The conductor for the AI Studio intelligence machine.

    Runs periodically to:
    1. Check for new high-value spider data
    2. Analyze with appropriate agents
    3. Generate alerts and opportunities
    4. Send notifications to Discord
    """

    def __init__(self):
        self.last_run = None
        self.last_sec_check = None
        self.last_news_check = None
        self.last_jobs_check = None
        self.last_stock_check = None  # Session 461
        self.last_blockchain_check = None  # Session 461

    def run_full_cycle(self) -> Dict[str, Any]:
        """
        Run a full intelligence cycle.

        Returns:
            Dict with cycle results
        """
        logger.info("🔄 Starting Autonomous Intelligence Loop cycle")

        results = {
            'started_at': datetime.now(timezone.utc).isoformat(),
            'sec_alerts': 0,
            'content_opportunities': 0,
            'job_opportunities': 0,
            'errors': []
        }

        try:
            # Check SEC filings
            sec_results = self.check_sec_filings()
            results['sec_alerts'] = sec_results.get('alerts_sent', 0)
            results['sec_details'] = sec_results
        except Exception as e:
            logger.error(f"SEC check error: {e}")
            results['errors'].append(f"SEC: {str(e)}")

        try:
            # Check for content opportunities
            content_results = self.check_content_opportunities()
            results['content_opportunities'] = content_results.get('opportunities_found', 0)
            results['content_details'] = content_results
        except Exception as e:
            logger.error(f"Content check error: {e}")
            results['errors'].append(f"Content: {str(e)}")

        try:
            # Check for job opportunities
            job_results = self.check_job_opportunities()
            results['job_opportunities'] = job_results.get('opportunities_found', 0)
            results['job_details'] = job_results
        except Exception as e:
            logger.error(f"Job check error: {e}")
            results['errors'].append(f"Jobs: {str(e)}")

        try:
            # Session 461: Stock audit monitoring
            stock_results = self.check_stock_security()
            results['stock_alerts'] = stock_results.get('total_alerts', 0)
            results['stock_details'] = stock_results
        except Exception as e:
            logger.error(f"Stock check error: {e}")
            results['errors'].append(f"Stocks: {str(e)}")

        try:
            # Session 461: Blockchain security monitoring
            blockchain_results = self.check_blockchain_security()
            results['blockchain_alerts'] = blockchain_results.get('total_alerts', 0)
            results['blockchain_details'] = blockchain_results
        except Exception as e:
            logger.error(f"Blockchain check error: {e}")
            results['errors'].append(f"Blockchain: {str(e)}")

        results['completed_at'] = datetime.now(timezone.utc).isoformat()
        self.last_run = datetime.now(timezone.utc)

        logger.info(f"✅ Intelligence Loop complete: {results['sec_alerts']} SEC alerts, "
                   f"{results['content_opportunities']} content opps, "
                   f"{results['job_opportunities']} job opps, "
                   f"{results.get('stock_alerts', 0)} stock alerts, "
                   f"{results.get('blockchain_alerts', 0)} blockchain alerts")

        return results

    def check_sec_filings(self) -> Dict[str, Any]:
        """
        Check for new high-impact SEC filings and send alerts.

        Returns:
            Dict with results
        """
        from ai_core.spiders.specialized.sec_spider import SECSpider
        from core.services.discord_notifications import discord_notify

        results = {
            'filings_checked': 0,
            'high_impact': 0,
            'alerts_sent': 0,
            'companies': []
        }

        try:
            # Fetch recent filings
            spider = SECSpider()
            filings = spider.fetch_data(max_results=30)
            results['filings_checked'] = len(filings)

            # Filter for high-impact filings
            high_impact_filings = [f for f in filings if f.get('is_high_impact')]
            results['high_impact'] = len(high_impact_filings)

            # Send alerts for high-impact filings
            for filing in high_impact_filings[:5]:  # Limit to 5 to avoid spam
                company = filing.get('company', 'Unknown')
                results['companies'].append(company)

                success = discord_notify.send_sec_filing_alert(
                    company=company,
                    form_type=filing.get('form_type', 'Unknown'),
                    description=filing.get('description', ''),
                    filed_at=filing.get('filed_at', 'Unknown'),
                    url=filing.get('url', ''),
                    is_high_impact=True,
                    items=filing.get('items', [])
                )

                if success:
                    results['alerts_sent'] += 1
                    logger.info(f"🚨 SEC Alert sent: {company} - {filing.get('form_type')}")

            # Send market digest if we have filings
            if filings:
                discord_notify.send_market_digest(
                    filings_count=len(filings),
                    high_impact_count=len(high_impact_filings),
                    companies=list(set(f.get('company', '') for f in filings))[:10],
                    period="latest"
                )

        except Exception as e:
            logger.error(f"SEC filing check error: {e}")
            results['error'] = str(e)

        self.last_sec_check = datetime.now(timezone.utc)
        return results

    def check_content_opportunities(self) -> Dict[str, Any]:
        """
        Check spider data for content/satire opportunities.

        Looks for:
        - Controversial tech news
        - Ironic situations
        - Hypocritical statements
        - Absurd developments

        Returns:
            Dict with results
        """
        from core.models_unified_system import SpiderData
        from core.services.discord_notifications import discord_notify

        results = {
            'data_checked': 0,
            'opportunities_found': 0,
            'alerts_sent': 0
        }

        # Satire-worthy keywords
        satire_keywords = [
            'controversy', 'backlash', 'outrage', 'ironic', 'hypocrit',
            'absurd', 'ridiculous', 'claims', 'despite', 'fails',
            'backfires', 'criticized', 'slammed', 'mocked', 'roasted',
            'billionaire', 'layoffs', 'record profits'
        ]

        try:
            # Get recent spider data (last 24 hours)
            cutoff = dj_timezone.now() - timedelta(hours=24)
            recent_data = SpiderData.objects.filter(
                created_at__gte=cutoff
            ).order_by('-created_at')[:100]

            results['data_checked'] = recent_data.count()

            for item in recent_data:
                # Extract title/content from raw_data JSON
                raw = item.raw_data or {}
                title = str(raw.get('title', raw.get('headline', ''))).lower()
                content = str(raw.get('content', raw.get('description', raw.get('summary', '')))).lower()
                combined = f"{title} {content}"

                # Check for satire-worthy content
                matches = [kw for kw in satire_keywords if kw in combined]

                if len(matches) >= 2:  # At least 2 keyword matches
                    results['opportunities_found'] += 1

                    # Generate satire angle (simplified for now)
                    display_title = raw.get('title', raw.get('headline', 'Trending Topic'))
                    satire_angle = self._generate_satire_angle(display_title, matches)

                    success = discord_notify.send_content_opportunity(
                        topic=display_title,
                        satire_angle=satire_angle,
                        style_suggestion="South Park / Political Cartoon",
                        source=item.spider_name or 'Unknown',
                        urgency="normal"
                    )

                    if success:
                        results['alerts_sent'] += 1

                    # Limit to 3 opportunities per cycle
                    if results['alerts_sent'] >= 3:
                        break

        except Exception as e:
            logger.error(f"Content opportunity check error: {e}")
            results['error'] = str(e)

        self.last_news_check = datetime.now(timezone.utc)
        return results

    def _generate_satire_angle(self, title: str, keywords: List[str]) -> str:
        """Generate a simple satire angle suggestion."""
        if 'billionaire' in keywords:
            return f"Billionaire behavior parody - exaggerate the disconnect from reality"
        elif 'layoffs' in keywords and 'profit' in ' '.join(keywords):
            return f"Corporate doublespeak - contrast layoffs with executive bonuses"
        elif 'backlash' in keywords or 'outrage' in keywords:
            return f"Internet mob mentality - show the absurdity of pile-on culture"
        elif 'claims' in keywords or 'despite' in keywords:
            return f"Reality vs PR - show the gap between what's said and what's real"
        else:
            return f"General absurdity - highlight the irony in: {title[:100]}"

    def check_job_opportunities(self) -> Dict[str, Any]:
        """
        Check for job opportunities matching user profile.

        Returns:
            Dict with results
        """
        from core.models_unified_system import SpiderData, Opportunity
        from core.services.discord_notifications import discord_notify

        results = {
            'data_checked': 0,
            'opportunities_found': 0,
            'alerts_sent': 0
        }

        try:
            # Get recent job data (last 24 hours)
            cutoff = dj_timezone.now() - timedelta(hours=24)
            recent_jobs = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=['remoteok', 'weworkremotely', 'adzuna', 'adzuna_jobs']
            ).order_by('-created_at')[:50]

            results['data_checked'] = recent_jobs.count()

            # High-value job indicators
            high_value_keywords = [
                'senior', 'lead', 'principal', 'staff', 'architect',
                'remote', 'fully remote', '$150', '$200', '$250',
                'python', 'django', 'ai', 'ml', 'machine learning'
            ]

            for job in recent_jobs:
                # Extract job info from raw_data JSON
                raw = job.raw_data or {}
                title = str(raw.get('title', raw.get('position', ''))).lower()
                content = str(raw.get('description', raw.get('content', raw.get('company', '')))).lower()
                combined = f"{title} {content}"

                # Check for high-value job
                matches = [kw for kw in high_value_keywords if kw in combined]

                if len(matches) >= 3:  # At least 3 matches = high value
                    results['opportunities_found'] += 1

                    # Send opportunity alert
                    display_title = raw.get('title', raw.get('position', 'Job Opportunity'))
                    success = discord_notify.send_opportunity(
                        title=display_title,
                        score=75 + (len(matches) * 5),  # Base 75 + bonus per match
                        category='jobs',
                        potential='$100K-250K',
                        source=job.spider_name or 'Job Spider',
                        description=f"Matching keywords: {', '.join(matches[:5])}",
                        urgency='normal'
                    )

                    if success:
                        results['alerts_sent'] += 1

                    # Limit to 5 job alerts per cycle
                    if results['alerts_sent'] >= 5:
                        break

        except Exception as e:
            logger.error(f"Job opportunity check error: {e}")
            results['error'] = str(e)

        self.last_jobs_check = datetime.now(timezone.utc)
        return results

    def generate_daily_digest(self) -> bool:
        """
        Generate and send the daily intelligence digest.

        Returns:
            True if sent successfully
        """
        from django.utils import timezone as dj_timezone
        from core.models_unified_system import SpiderData, AgentDream, AgentConversation, AgentKnowledge
        from core.services.discord_notifications import discord_notify

        try:
            today = dj_timezone.now().date()
            yesterday = dj_timezone.now() - timedelta(hours=24)

            # SEC Summary
            sec_data = SpiderData.objects.filter(
                collected_at__gte=yesterday,
                spider_id='sec_edgar'
            )
            sec_summary = {
                'filings': sec_data.count(),
                'high_impact': 0,  # Would need to parse content
                'top_companies': list(sec_data.values_list('title', flat=True)[:5])
            }

            # Tech News
            tech_data = SpiderData.objects.filter(
                collected_at__gte=yesterday,
                spider_id__in=['techcrunch', 'the_verge', 'hackernews', 'wired']
            ).values_list('title', flat=True)[:5]
            tech_news = list(tech_data)

            # Agent Activity
            agent_activity = {
                'dreams': AgentDream.objects.filter(created_at__gte=yesterday).count(),
                'conversations': AgentConversation.objects.filter(created_at__gte=yesterday).count(),
                'learnings': AgentKnowledge.objects.filter(created_at__gte=yesterday).count(),
            }

            # Send digest
            return discord_notify.send_daily_digest(
                date=today.strftime('%B %d, %Y'),
                sec_summary=sec_summary,
                tech_news=tech_news,
                agent_activity=agent_activity
            )

        except Exception as e:
            logger.error(f"Daily digest error: {e}")
            return False

    def check_stock_security(self) -> Dict[str, Any]:
        """
        Session 461: Run stock audit using the Stock Audit Agent Group.

        Coordinates all stock audit agents:
        - StockAnalystAgent: SEC filing analysis
        - MarketMovementMonitorAgent: Price/volume monitoring
        - InstitutionalWatcherAgent: Insider trading tracking
        - MarketAnomalyDetectorAgent: Manipulation detection

        Returns:
            Dict with audit results
        """
        from core.services.discord_notifications import discord_notify

        results = {
            'total_alerts': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'tickers_flagged': [],
            'correlated': 0,
        }

        try:
            # Run the Stock Audit Coordinator
            from core.agents.stocks.stock_audit_coordinator import run_stock_audit_cycle

            audit_results = run_stock_audit_cycle()

            # Extract summary from coordinator results
            summary = audit_results.get('data', {}).get('summary', {})

            results['total_alerts'] = summary.get('total_alerts', 0)
            results['critical'] = summary.get('critical', 0)
            results['high'] = summary.get('high', 0)
            results['medium'] = summary.get('medium', 0)
            results['low'] = summary.get('low', 0)
            results['tickers_flagged'] = summary.get('tickers_flagged', [])
            results['correlated'] = summary.get('correlated_findings', 0)

            # Send summary to Discord
            if results['total_alerts'] > 0:
                discord_notify.send_stock_audit_summary(
                    total_alerts=results['total_alerts'],
                    critical_count=results['critical'],
                    high_count=results['high'],
                    tickers_flagged=results['tickers_flagged'],
                    correlated_count=results['correlated']
                )

            logger.info(f"📈 Stock audit complete: {results['total_alerts']} alerts "
                       f"({results['critical']} critical, {results['high']} high)")

        except Exception as e:
            logger.error(f"Stock security check error: {e}")
            results['error'] = str(e)

        self.last_stock_check = datetime.now(timezone.utc)
        return results

    def check_blockchain_security(self) -> Dict[str, Any]:
        """
        Session 461: Run blockchain security audit using the Blockchain Audit Agent Group.

        Coordinates all blockchain audit agents:
        - SmartContractAuditorAgent: Solidity code vulnerability detection
        - TransactionMonitorAgent: Suspicious transaction pattern monitoring
        - WhaleWatcherAgent: Large token movement tracking
        - ExploitDetectorAgent: Known exploit signature matching

        Returns:
            Dict with audit results
        """
        from core.services.discord_notifications import (
            send_blockchain_alert_notification,
            send_whale_alert_notification,
            send_exploit_alert_notification
        )

        results = {
            'total_alerts': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'whale_alerts': 0,
            'exploit_alerts': 0,
            'contract_vulnerabilities': 0,
            'suspicious_transactions': 0,
        }

        try:
            # Run the Blockchain Audit Coordinator
            from core.agents.blockchain import BlockchainAuditCoordinator

            coordinator = BlockchainAuditCoordinator()
            audit_results = coordinator.run_security_cycle()

            # Extract summary from coordinator results
            summary = audit_results.get('summary', {})
            alerts = audit_results.get('alerts', [])

            results['total_alerts'] = len(alerts)

            # Count by severity
            for alert in alerts:
                severity = alert.get('severity', 'LOW').upper()
                if severity == 'CRITICAL':
                    results['critical'] += 1
                elif severity == 'HIGH':
                    results['high'] += 1
                elif severity == 'MEDIUM':
                    results['medium'] += 1
                else:
                    results['low'] += 1

                # Count by type
                alert_type = alert.get('type', '')
                if 'whale' in alert_type.lower():
                    results['whale_alerts'] += 1
                elif 'exploit' in alert_type.lower():
                    results['exploit_alerts'] += 1
                elif 'contract' in alert_type.lower() or 'vulnerability' in alert_type.lower():
                    results['contract_vulnerabilities'] += 1
                elif 'transaction' in alert_type.lower():
                    results['suspicious_transactions'] += 1

            # Send Discord alerts for critical/high severity items
            for alert in alerts:
                severity = alert.get('severity', 'LOW').upper()
                if severity in ['CRITICAL', 'HIGH']:
                    alert_type = alert.get('type', '')

                    if 'whale' in alert_type.lower():
                        send_whale_alert_notification(
                            token=alert.get('token', 'ETH'),
                            amount=alert.get('amount', 'Unknown'),
                            from_address=alert.get('from', 'Unknown'),
                            to_address=alert.get('to', 'Unknown'),
                            usd_value=alert.get('usd_value'),
                            market_impact=alert.get('market_impact', 'medium'),
                            tx_hash=alert.get('tx_hash')
                        )
                    elif 'exploit' in alert_type.lower():
                        send_exploit_alert_notification(
                            protocol=alert.get('protocol', 'Unknown'),
                            exploit_type=alert.get('exploit_type', 'Unknown'),
                            severity=severity,
                            details=alert.get('details', ''),
                            status=alert.get('status', 'detected'),
                            tx_hash=alert.get('tx_hash')
                        )
                    else:
                        send_blockchain_alert_notification(
                            title=alert.get('title', 'Blockchain Alert'),
                            description=alert.get('description', ''),
                            severity=severity,
                            source=alert.get('source', 'blockchain_audit'),
                            tx_hash=alert.get('tx_hash'),
                            address=alert.get('address')
                        )

            logger.info(f"🔗 Blockchain audit complete: {results['total_alerts']} alerts "
                       f"({results['critical']} critical, {results['high']} high, "
                       f"{results['whale_alerts']} whale, {results['exploit_alerts']} exploit)")

        except ImportError as e:
            logger.warning(f"Blockchain audit agents not available: {e}")
            results['error'] = f"Import error: {str(e)}"
        except Exception as e:
            logger.error(f"Blockchain security check error: {e}")
            results['error'] = str(e)

        self.last_blockchain_check = datetime.now(timezone.utc)
        return results


# Singleton instance
autonomous_loop = AutonomousIntelligenceLoop()


def run_intelligence_cycle():
    """Convenience function for Celery tasks."""
    return autonomous_loop.run_full_cycle()


def run_daily_digest():
    """Convenience function for Celery tasks."""
    return autonomous_loop.generate_daily_digest()


def run_stock_audit():
    """Session 461: Convenience function for stock audit Celery tasks."""
    return autonomous_loop.check_stock_security()


def run_blockchain_audit():
    """Session 461: Convenience function for blockchain audit Celery tasks."""
    return autonomous_loop.check_blockchain_security()
