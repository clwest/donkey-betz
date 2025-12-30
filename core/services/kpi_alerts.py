"""
Session 611: KPI Alerts Service

Monitors experiment KPIs and generates alerts when:
1. KPI drops significantly (>20% decline)
2. Trend turns negative after being positive
3. Experiment is stuck (no progress for 7+ days)
4. KPI is far from target with little time remaining

Integrates with Discord for real-time notifications.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import timedelta
from collections import defaultdict

from django.utils import timezone

logger = logging.getLogger(__name__)


class KPIAlertService:
    """
    Session 611: Monitors KPIs and generates alerts for experiments.
    """

    # Alert severity levels
    SEVERITY_CRITICAL = 'critical'  # Immediate action needed
    SEVERITY_WARNING = 'warning'    # Attention needed soon
    SEVERITY_INFO = 'info'          # FYI, no action needed

    # Alert types
    ALERT_KPI_DROP = 'kpi_drop'           # Significant KPI decrease
    ALERT_TREND_REVERSAL = 'trend_reversal'  # Trend changed from up to down
    ALERT_STALLED = 'stalled'             # No progress for extended period
    ALERT_OFF_TRACK = 'off_track'         # Won't meet target at current pace
    ALERT_TARGET_EXCEEDED = 'target_exceeded'  # Positive: exceeded target!

    # Thresholds
    KPI_DROP_THRESHOLD = 0.20  # 20% drop triggers alert
    STALLED_DAYS = 7           # Days without progress
    OFF_TRACK_THRESHOLD = 0.30 # 30% behind expected progress

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.KPIAlertService")

    def check_all_experiments(self) -> Dict[str, Any]:
        """
        Check all running experiments for alert conditions.

        Returns:
            Dict with alerts generated and summary
        """
        from core.models_pilot_readiness import Experiment, KPISnapshot

        results = {
            'success': True,
            'alerts': [],
            'by_severity': defaultdict(list),
            'by_type': defaultdict(list),
            'experiments_checked': 0,
            'alerts_generated': 0,
        }

        running_experiments = Experiment.objects.filter(status='running')
        results['experiments_checked'] = running_experiments.count()

        for exp in running_experiments:
            try:
                exp_alerts = self._check_experiment(exp)
                for alert in exp_alerts:
                    results['alerts'].append(alert)
                    results['by_severity'][alert['severity']].append(alert)
                    results['by_type'][alert['type']].append(alert)
                    results['alerts_generated'] += 1

            except Exception as e:
                self.logger.error(f"Error checking experiment {exp.id}: {e}")

        # Sort alerts by severity (critical first)
        severity_order = {self.SEVERITY_CRITICAL: 0, self.SEVERITY_WARNING: 1, self.SEVERITY_INFO: 2}
        results['alerts'].sort(key=lambda a: severity_order.get(a['severity'], 99))

        results['summary'] = {
            'total_alerts': results['alerts_generated'],
            'critical': len(results['by_severity'][self.SEVERITY_CRITICAL]),
            'warning': len(results['by_severity'][self.SEVERITY_WARNING]),
            'info': len(results['by_severity'][self.SEVERITY_INFO]),
        }

        return results

    def _check_experiment(self, exp) -> List[Dict]:
        """Check a single experiment for alert conditions."""
        from core.models_pilot_readiness import KPISnapshot

        alerts = []

        # Get recent snapshots
        lookback = timezone.now() - timedelta(days=14)
        snapshots = list(KPISnapshot.objects.filter(
            experiment=exp,
            captured_at__gte=lookback
        ).order_by('captured_at'))

        if len(snapshots) < 2:
            # Not enough data for trend analysis
            return alerts

        # Check for KPI drop
        kpi_drop_alert = self._check_kpi_drop(exp, snapshots)
        if kpi_drop_alert:
            alerts.append(kpi_drop_alert)

        # Check for trend reversal
        trend_alert = self._check_trend_reversal(exp, snapshots)
        if trend_alert:
            alerts.append(trend_alert)

        # Check for stalled progress
        stalled_alert = self._check_stalled(exp, snapshots)
        if stalled_alert:
            alerts.append(stalled_alert)

        # Check for off-track
        off_track_alert = self._check_off_track(exp, snapshots)
        if off_track_alert:
            alerts.append(off_track_alert)

        # Check for target exceeded (positive alert!)
        exceeded_alert = self._check_target_exceeded(exp, snapshots)
        if exceeded_alert:
            alerts.append(exceeded_alert)

        return alerts

    def _check_kpi_drop(self, exp, snapshots: List) -> Optional[Dict]:
        """Check if KPI has dropped significantly."""
        if len(snapshots) < 2:
            return None

        # Get recent values
        recent = snapshots[-1]
        previous = snapshots[-2]

        if recent.numeric_value is None or previous.numeric_value is None:
            return None

        if previous.numeric_value == 0:
            return None

        # Calculate percentage change
        change = (recent.numeric_value - previous.numeric_value) / abs(previous.numeric_value)

        if change < -self.KPI_DROP_THRESHOLD:
            drop_percent = abs(change) * 100
            return {
                'type': self.ALERT_KPI_DROP,
                'severity': self.SEVERITY_WARNING if drop_percent < 40 else self.SEVERITY_CRITICAL,
                'experiment_id': str(exp.id),
                'experiment_name': exp.name[:50],
                'kpi': exp.primary_kpi,
                'message': f"KPI dropped {drop_percent:.1f}%: {previous.value} → {recent.value}",
                'details': {
                    'previous_value': previous.value,
                    'current_value': recent.value,
                    'drop_percent': round(drop_percent, 1),
                    'previous_date': previous.captured_at.isoformat(),
                    'current_date': recent.captured_at.isoformat(),
                },
                'recommended_action': 'Investigate cause of KPI decline and consider intervention',
                'created_at': timezone.now().isoformat(),
            }

        return None

    def _check_trend_reversal(self, exp, snapshots: List) -> Optional[Dict]:
        """Check if trend has reversed from positive to negative."""
        if len(snapshots) < 4:
            return None

        # Calculate trend for first half and second half
        mid = len(snapshots) // 2
        first_half = snapshots[:mid]
        second_half = snapshots[mid:]

        def calc_trend(snaps):
            values = [s.numeric_value for s in snaps if s.numeric_value is not None]
            if len(values) < 2:
                return 0
            return values[-1] - values[0]

        first_trend = calc_trend(first_half)
        second_trend = calc_trend(second_half)

        # Trend reversal: was going up, now going down
        if first_trend > 0 and second_trend < 0:
            return {
                'type': self.ALERT_TREND_REVERSAL,
                'severity': self.SEVERITY_WARNING,
                'experiment_id': str(exp.id),
                'experiment_name': exp.name[:50],
                'kpi': exp.primary_kpi,
                'message': f"Trend reversed: was improving, now declining",
                'details': {
                    'first_half_trend': 'up' if first_trend > 0 else 'down',
                    'second_half_trend': 'up' if second_trend > 0 else 'down',
                    'data_points': len(snapshots),
                },
                'recommended_action': 'Review recent changes that may have caused the reversal',
                'created_at': timezone.now().isoformat(),
            }

        return None

    def _check_stalled(self, exp, snapshots: List) -> Optional[Dict]:
        """Check if experiment has stalled (no progress)."""
        if len(snapshots) < 3:
            return None

        # Check if values have been the same for the last N snapshots
        recent_values = [s.numeric_value for s in snapshots[-5:] if s.numeric_value is not None]

        if len(recent_values) < 3:
            return None

        # Check if all values are the same (stalled)
        if len(set(recent_values)) == 1:
            # Calculate days since last change
            days_since_change = 0
            for i in range(len(snapshots) - 1, 0, -1):
                if snapshots[i].numeric_value != snapshots[i-1].numeric_value:
                    days_since_change = (timezone.now() - snapshots[i].captured_at).days
                    break

            if days_since_change >= self.STALLED_DAYS or len(recent_values) >= 5:
                return {
                    'type': self.ALERT_STALLED,
                    'severity': self.SEVERITY_INFO,
                    'experiment_id': str(exp.id),
                    'experiment_name': exp.name[:50],
                    'kpi': exp.primary_kpi,
                    'message': f"KPI stalled at {recent_values[0]} for {len(recent_values)} readings",
                    'details': {
                        'stalled_value': recent_values[0],
                        'readings_at_same_value': len(recent_values),
                        'days_since_change': days_since_change,
                    },
                    'recommended_action': 'Verify data source is working and experiment is still active',
                    'created_at': timezone.now().isoformat(),
                }

        return None

    def _check_off_track(self, exp, snapshots: List) -> Optional[Dict]:
        """Check if experiment is off track to meet target."""
        if not exp.target_value or not snapshots:
            return None

        # Parse target value
        try:
            target = float(exp.target_value.replace('%', '').replace(',', ''))
        except (ValueError, AttributeError):
            return None

        current = snapshots[-1].numeric_value
        if current is None:
            return None

        # Calculate expected progress based on days elapsed
        if not exp.started_at:
            return None

        days_elapsed = (timezone.now() - exp.started_at).days
        # Use default 30 days if expected_duration_days not set
        expected_duration = getattr(exp, 'expected_duration_days', None) or 30

        if expected_duration <= 0:
            return None

        # Calculate expected progress percentage
        expected_progress_pct = min(1.0, days_elapsed / expected_duration)

        # Get starting value (first snapshot or 0)
        starting_value = 0
        if len(snapshots) > 1:
            first_snap = snapshots[0]
            if first_snap.numeric_value is not None:
                starting_value = first_snap.numeric_value

        # Calculate expected current value
        expected_current = starting_value + (target - starting_value) * expected_progress_pct

        # Calculate actual progress
        if target == starting_value:
            return None

        actual_progress = (current - starting_value) / (target - starting_value)
        expected_progress = expected_progress_pct

        # Check if significantly behind
        if expected_progress > 0 and actual_progress < expected_progress * (1 - self.OFF_TRACK_THRESHOLD):
            behind_pct = (expected_progress - actual_progress) / expected_progress * 100
            return {
                'type': self.ALERT_OFF_TRACK,
                'severity': self.SEVERITY_WARNING,
                'experiment_id': str(exp.id),
                'experiment_name': exp.name[:50],
                'kpi': exp.primary_kpi,
                'message': f"Off track: {behind_pct:.0f}% behind expected progress",
                'details': {
                    'current_value': current,
                    'target_value': target,
                    'expected_progress_pct': round(expected_progress * 100, 1),
                    'actual_progress_pct': round(actual_progress * 100, 1),
                    'days_elapsed': days_elapsed,
                    'expected_duration': expected_duration,
                },
                'recommended_action': 'Consider adjusting approach or extending timeline',
                'created_at': timezone.now().isoformat(),
            }

        return None

    def _check_target_exceeded(self, exp, snapshots: List) -> Optional[Dict]:
        """Check if experiment has exceeded its target (positive alert!)."""
        if not exp.target_value or not snapshots:
            return None

        # Parse target value
        try:
            target = float(exp.target_value.replace('%', '').replace(',', ''))
        except (ValueError, AttributeError):
            return None

        current = snapshots[-1].numeric_value
        if current is None:
            return None

        # Check if current exceeds target
        if current >= target:
            exceeded_by = ((current - target) / target * 100) if target > 0 else 0
            return {
                'type': self.ALERT_TARGET_EXCEEDED,
                'severity': self.SEVERITY_INFO,
                'experiment_id': str(exp.id),
                'experiment_name': exp.name[:50],
                'kpi': exp.primary_kpi,
                'message': f"Target exceeded! {current} vs target {target} (+{exceeded_by:.0f}%)",
                'details': {
                    'current_value': current,
                    'target_value': target,
                    'exceeded_by_pct': round(exceeded_by, 1),
                },
                'recommended_action': 'Consider marking experiment as success or raising target',
                'created_at': timezone.now().isoformat(),
            }

        return None

    def send_discord_alerts(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Send alerts to Discord."""
        from core.services.discord_notifications import DiscordNotificationService

        results = {
            'sent': 0,
            'failed': 0,
            'skipped': 0,
        }

        if not alerts:
            return results

        try:
            discord = DiscordNotificationService()

            # Group alerts by severity
            critical = [a for a in alerts if a['severity'] == self.SEVERITY_CRITICAL]
            warnings = [a for a in alerts if a['severity'] == self.SEVERITY_WARNING]
            info = [a for a in alerts if a['severity'] == self.SEVERITY_INFO]

            # Build message
            if critical or warnings:
                message = "**🚨 KPI Alerts**\n\n"

                if critical:
                    message += "**🔴 CRITICAL:**\n"
                    for alert in critical[:5]:
                        message += f"• **{alert['experiment_name'][:30]}**: {alert['message']}\n"
                    message += "\n"

                if warnings:
                    message += "**🟡 WARNING:**\n"
                    for alert in warnings[:5]:
                        message += f"• **{alert['experiment_name'][:30]}**: {alert['message']}\n"
                    message += "\n"

                # Add summary
                message += f"_Total: {len(critical)} critical, {len(warnings)} warnings, {len(info)} info_"

                discord.send_to_channel('system-status', message)
                results['sent'] = len(critical) + len(warnings)

            # Send positive alerts separately
            target_exceeded = [a for a in alerts if a['type'] == self.ALERT_TARGET_EXCEEDED]
            if target_exceeded:
                message = "**🎉 Experiment Success!**\n\n"
                for alert in target_exceeded:
                    message += f"• **{alert['experiment_name'][:30]}**: {alert['message']}\n"

                discord.send_to_channel('system-status', message)
                results['sent'] += len(target_exceeded)

        except Exception as e:
            self.logger.error(f"Error sending Discord alerts: {e}")
            results['failed'] = len(alerts)

        return results

    def get_weekly_summary(self) -> Dict[str, Any]:
        """Generate weekly KPI trend summary."""
        from core.models_pilot_readiness import Experiment, KPISnapshot
        from core.services.auto_kpi_tracking import get_all_kpi_trends

        # Get trend data
        trends = get_all_kpi_trends(days=7)

        summary = {
            'week_of': timezone.now().isoformat(),
            'experiments_tracked': len(trends.get('experiments', [])),
            'trending_up': trends.get('summary', {}).get('trending_up', 0),
            'trending_down': trends.get('summary', {}).get('trending_down', 0),
            'stable': trends.get('summary', {}).get('stable', 0),
            'highlights': [],
            'concerns': [],
        }

        for exp in trends.get('experiments', []):
            if exp['trend_direction'] == 'up':
                summary['highlights'].append({
                    'name': exp['name'],
                    'kpi': exp['kpi'],
                    'current': exp['current'],
                    'target': exp['target'],
                })
            elif exp['trend_direction'] == 'down':
                summary['concerns'].append({
                    'name': exp['name'],
                    'kpi': exp['kpi'],
                    'current': exp['current'],
                    'target': exp['target'],
                })

        return summary


# Convenience functions
def check_kpi_alerts() -> Dict[str, Any]:
    """Check all experiments for KPI alerts."""
    service = KPIAlertService()
    return service.check_all_experiments()


def send_kpi_alerts_to_discord(alerts: List[Dict]) -> Dict[str, Any]:
    """Send KPI alerts to Discord."""
    service = KPIAlertService()
    return service.send_discord_alerts(alerts)


def get_weekly_kpi_summary() -> Dict[str, Any]:
    """Get weekly KPI trend summary."""
    service = KPIAlertService()
    return service.get_weekly_summary()
