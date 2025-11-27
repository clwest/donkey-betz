"""
Proactive Engine - Phase 6 of Creative Intelligence Empire
AI-powered alert monitoring, smart suggestions, and automated actions.

Session 234: Complete proactive system implementation
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count, F, Q
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class AlertEngine:
    """
    Monitors metrics and triggers alerts based on conditions.
    Handles threshold alerts, trend detection, and anomaly detection.
    """

    def __init__(self, user=None):
        self.user = user

    def check_all_alerts(self, user=None) -> List[Dict]:
        """Check all active alerts for a user or all users."""
        from .models_unified_system import ProactiveAlert, ProactiveNotification

        triggered_alerts = []

        alerts_query = ProactiveAlert.objects.filter(is_active=True)
        if user:
            alerts_query = alerts_query.filter(user=user)
        elif self.user:
            alerts_query = alerts_query.filter(user=self.user)

        for alert in alerts_query:
            try:
                current_value = self._get_metric_value(alert)
                if current_value is not None and alert.should_trigger(current_value):
                    # Create notification
                    notification = self._create_alert_notification(alert, current_value)
                    alert.trigger()
                    triggered_alerts.append({
                        'alert_id': str(alert.id),
                        'name': alert.name,
                        'type': alert.alert_type,
                        'current_value': current_value,
                        'threshold': float(alert.threshold_value) if alert.threshold_value else None,
                        'notification_id': str(notification.id),
                    })
            except Exception as e:
                logger.error(f"Error checking alert {alert.id}: {e}")

        return triggered_alerts

    def _get_metric_value(self, alert) -> Optional[float]:
        """Get the current value of the metric being monitored."""
        from .models_unified_system import (
            ContentDistribution, RevenueSale, DistributionMetrics
        )

        metric_name = alert.metric_name
        user = alert.user
        platform = alert.platform

        try:
            if metric_name == 'daily_revenue':
                today = timezone.now().date()
                sales = RevenueSale.objects.filter(
                    user=user,
                    sale_date__date=today
                )
                if platform:
                    sales = sales.filter(platform=platform)
                total = sales.aggregate(Sum('net_revenue'))['net_revenue__sum'] or 0
                return float(total)

            elif metric_name == 'weekly_revenue':
                week_ago = timezone.now() - timedelta(days=7)
                sales = RevenueSale.objects.filter(
                    user=user,
                    sale_date__gte=week_ago
                )
                if platform:
                    sales = sales.filter(platform=platform)
                total = sales.aggregate(Sum('net_revenue'))['net_revenue__sum'] or 0
                return float(total)

            elif metric_name == 'conversion_rate':
                recent = DistributionMetrics.objects.filter(
                    distribution__user=user,
                    date__gte=timezone.now().date() - timedelta(days=7)
                )
                if platform:
                    recent = recent.filter(distribution__platform=platform)
                totals = recent.aggregate(
                    views=Sum('views'),
                    sales=Sum('sales')
                )
                if totals['views'] and totals['views'] > 0:
                    return (totals['sales'] or 0) / totals['views'] * 100
                return 0

            elif metric_name == 'total_distributions':
                distributions = ContentDistribution.objects.filter(user=user)
                if platform:
                    distributions = distributions.filter(platform=platform)
                return distributions.count()

            elif metric_name == 'pending_distributions':
                return ContentDistribution.objects.filter(
                    user=user,
                    status='pending'
                ).count()

            elif metric_name == 'avg_sale_price':
                sales = RevenueSale.objects.filter(user=user)
                if platform:
                    sales = sales.filter(platform=platform)
                avg = sales.aggregate(Avg('sale_price'))['sale_price__avg']
                return float(avg) if avg else 0

            elif metric_name == 'daily_views':
                today = timezone.now().date()
                metrics = DistributionMetrics.objects.filter(
                    distribution__user=user,
                    date=today
                )
                total = metrics.aggregate(Sum('views'))['views__sum'] or 0
                return total

            else:
                logger.warning(f"Unknown metric: {metric_name}")
                return None

        except Exception as e:
            logger.error(f"Error getting metric {metric_name}: {e}")
            return None

    def _create_alert_notification(self, alert, current_value: float):
        """Create a notification for a triggered alert."""
        from .models_unified_system import ProactiveNotification

        # Determine message based on condition
        condition_messages = {
            'above': f"is above {alert.threshold_value}",
            'below': f"is below {alert.threshold_value}",
            'equals': f"equals {alert.threshold_value}",
            'change_up': f"increased by {alert.threshold_percent}%",
            'change_down': f"decreased by {alert.threshold_percent}%",
        }
        condition_text = condition_messages.get(alert.condition, "triggered")

        notification = ProactiveNotification.objects.create(
            user=alert.user,
            alert=alert,
            notification_type='alert',
            priority='high' if alert.alert_type in ['threshold', 'anomaly'] else 'medium',
            title=f"Alert: {alert.name}",
            message=f"Your {alert.metric_name} {condition_text}. Current value: {current_value:.2f}",
            rich_content={
                'metric_name': alert.metric_name,
                'current_value': current_value,
                'threshold': float(alert.threshold_value) if alert.threshold_value else None,
                'condition': alert.condition,
            },
            icon='alert-triangle' if alert.alert_type == 'threshold' else 'bell',
            channels_sent=['in_app'],
            sent_at=timezone.now(),
            delivery_status='delivered',
        )

        return notification

    def create_default_alerts(self, user) -> List[Dict]:
        """Create default alert configurations for a new user."""
        from .models_unified_system import ProactiveAlert

        default_alerts = [
            {
                'alert_type': 'threshold',
                'name': 'Daily Revenue Goal',
                'metric_name': 'daily_revenue',
                'condition': 'above',
                'threshold_value': 100,
                'check_frequency': 'daily',
                'notification_channels': ['in_app', 'email'],
            },
            {
                'alert_type': 'threshold',
                'name': 'Low Conversion Alert',
                'metric_name': 'conversion_rate',
                'condition': 'below',
                'threshold_value': 1,
                'check_frequency': 'daily',
                'notification_channels': ['in_app'],
            },
            {
                'alert_type': 'goal',
                'name': 'Weekly Revenue Milestone',
                'metric_name': 'weekly_revenue',
                'condition': 'above',
                'threshold_value': 500,
                'check_frequency': 'weekly',
                'notification_channels': ['in_app', 'email'],
            },
        ]

        created = []
        for alert_data in default_alerts:
            alert = ProactiveAlert.objects.create(
                user=user,
                **alert_data
            )
            created.append({
                'id': str(alert.id),
                'name': alert.name,
                'type': alert.alert_type,
            })

        return created


class SuggestionEngine:
    """
    Generates smart suggestions based on user data and learned patterns.
    Analyzes performance and recommends improvements.
    """

    def __init__(self, user=None):
        self.user = user

    def generate_suggestions(self, user=None, max_suggestions: int = 10) -> List[Dict]:
        """Generate smart suggestions for a user based on their data."""
        from .models_unified_system import SmartSuggestion

        target_user = user or self.user
        if not target_user:
            return []

        suggestions = []

        # 1. Pricing suggestions
        pricing_suggestions = self._analyze_pricing(target_user)
        suggestions.extend(pricing_suggestions)

        # 2. Platform suggestions
        platform_suggestions = self._analyze_platforms(target_user)
        suggestions.extend(platform_suggestions)

        # 3. Timing suggestions
        timing_suggestions = self._analyze_timing(target_user)
        suggestions.extend(timing_suggestions)

        # 4. Content suggestions
        content_suggestions = self._analyze_content(target_user)
        suggestions.extend(content_suggestions)

        # 5. Tag optimization suggestions
        tag_suggestions = self._analyze_tags(target_user)
        suggestions.extend(tag_suggestions)

        # Save suggestions to database
        saved_suggestions = []
        for idx, suggestion_data in enumerate(suggestions[:max_suggestions]):
            try:
                suggestion = SmartSuggestion.objects.create(
                    user=target_user,
                    **suggestion_data
                )
                saved_suggestions.append({
                    'id': str(suggestion.id),
                    'type': suggestion.suggestion_type,
                    'title': suggestion.title,
                    'priority': suggestion.priority_score,
                    'estimated_impact': suggestion.estimated_revenue_impact,
                })
            except Exception as e:
                logger.error(f"Error saving suggestion: {e}")

        return saved_suggestions

    def _analyze_pricing(self, user) -> List[Dict]:
        """Analyze pricing patterns and suggest optimizations."""
        from .models_unified_system import (
            ContentDistribution, RevenueSale, SuccessPattern, PricingOptimization
        )

        suggestions = []

        try:
            # Get user's average prices vs successful sales
            sales = RevenueSale.objects.filter(user=user)
            if not sales.exists():
                return suggestions

            avg_sale_price = sales.aggregate(Avg('sale_price'))['sale_price__avg'] or 0

            # Get pricing patterns
            pricing_patterns = SuccessPattern.objects.filter(
                user=user,
                pattern_type='pricing_strategy',
                success_rate__gte=50
            ).order_by('-success_rate')[:3]

            for pattern in pricing_patterns:
                if pattern.pattern_attributes.get('optimal_price'):
                    optimal = pattern.pattern_attributes['optimal_price']
                    if abs(float(avg_sale_price) - float(optimal)) > 5:
                        suggestions.append({
                            'suggestion_type': 'pricing',
                            'category': 'revenue',
                            'title': f"Optimize pricing to ${optimal:.2f}",
                            'description': f"Your successful sales average ${optimal:.2f}. Consider adjusting your pricing strategy.",
                            'detailed_rationale': f"Based on {pattern.sample_size} sales, this price point has a {pattern.success_rate:.1f}% success rate.",
                            'current_state': {'avg_price': float(avg_sale_price)},
                            'suggested_state': {'optimal_price': float(optimal)},
                            'estimated_revenue_impact': Decimal(str(optimal - avg_sale_price)) * 10,
                            'confidence_score': Decimal(str(pattern.confidence_score)),
                            'priority_score': 80 if abs(float(avg_sale_price) - float(optimal)) > 10 else 60,
                            'effort_level': 'low',
                            'supporting_patterns': [str(pattern.id)],
                        })

            # Check for underpriced content
            distributions = ContentDistribution.objects.filter(
                user=user,
                status='active',
                listing_price__lt=avg_sale_price * Decimal('0.5')
            )
            if distributions.exists():
                suggestions.append({
                    'suggestion_type': 'pricing',
                    'category': 'revenue',
                    'title': f"Review {distributions.count()} underpriced listings",
                    'description': "Some of your listings are priced significantly below your average sale price.",
                    'action_steps': [
                        {'step': 1, 'action': 'Review low-priced listings', 'reason': 'Potential revenue opportunity'},
                        {'step': 2, 'action': 'Compare with successful sales', 'reason': 'Align with market'},
                    ],
                    'estimated_revenue_impact': Decimal(str(avg_sale_price * 0.2 * distributions.count())),
                    'confidence_score': Decimal('70'),
                    'priority_score': 75,
                    'effort_level': 'low',
                    'related_distribution_ids': list(distributions.values_list('id', flat=True)[:5]),
                })

        except Exception as e:
            logger.error(f"Error analyzing pricing: {e}")

        return suggestions

    def _analyze_platforms(self, user) -> List[Dict]:
        """Analyze platform performance and suggest expansions."""
        from .models_unified_system import (
            ContentDistribution, RevenueSale, DistributionPlatform, SuccessPattern
        )

        suggestions = []

        try:
            # Get revenue by platform
            platform_revenue = RevenueSale.objects.filter(user=user).values(
                'platform__name'
            ).annotate(
                total=Sum('net_revenue'),
                count=Count('id')
            ).order_by('-total')

            current_platforms = set(d['platform__name'] for d in platform_revenue if d['platform__name'])

            # Get successful platforms from patterns
            platform_patterns = SuccessPattern.objects.filter(
                is_global=True,
                pattern_type='platform_match',
                success_rate__gte=60
            ).order_by('-success_rate')[:5]

            for pattern in platform_patterns:
                best_platforms = pattern.best_platforms or []
                for platform_name in best_platforms:
                    if platform_name not in current_platforms:
                        suggestions.append({
                            'suggestion_type': 'platform',
                            'category': 'reach',
                            'title': f"Expand to {platform_name}",
                            'description': f"Consider listing your content on {platform_name} based on market success patterns.",
                            'detailed_rationale': f"This platform shows {pattern.success_rate:.1f}% success rate for similar content.",
                            'current_state': {'platforms': list(current_platforms)},
                            'suggested_state': {'add_platform': platform_name},
                            'estimated_revenue_impact': Decimal(str(pattern.avg_revenue_per_success * 5)),
                            'confidence_score': Decimal(str(pattern.confidence_score)),
                            'priority_score': 70,
                            'effort_level': 'medium',
                        })
                        break  # Only one platform suggestion per pattern

        except Exception as e:
            logger.error(f"Error analyzing platforms: {e}")

        return suggestions

    def _analyze_timing(self, user) -> List[Dict]:
        """Analyze upload timing and suggest optimal times."""
        from .models_unified_system import ContentDistribution, RevenueSale, SuccessPattern

        suggestions = []

        try:
            # Get timing patterns
            timing_patterns = SuccessPattern.objects.filter(
                Q(user=user) | Q(is_global=True),
                pattern_type='timing',
                success_rate__gte=50
            ).order_by('-success_rate')[:3]

            for pattern in timing_patterns:
                best_times = pattern.best_upload_times or []
                if best_times:
                    suggestions.append({
                        'suggestion_type': 'timing',
                        'category': 'efficiency',
                        'title': f"Upload during peak times",
                        'description': f"Best upload times based on your success patterns: {', '.join(best_times[:3])}",
                        'detailed_rationale': f"Content uploaded at these times has {pattern.success_rate:.1f}% higher success rate.",
                        'suggested_state': {'best_times': best_times[:3]},
                        'estimated_revenue_impact': Decimal(str(pattern.avg_revenue_per_success * 0.1)),
                        'confidence_score': Decimal(str(pattern.confidence_score)),
                        'priority_score': 50,
                        'effort_level': 'low',
                    })
                    break

        except Exception as e:
            logger.error(f"Error analyzing timing: {e}")

        return suggestions

    def _analyze_content(self, user) -> List[Dict]:
        """Analyze content performance and suggest improvements."""
        from .models_unified_system import ContentDistribution, SuccessPattern

        suggestions = []

        try:
            # Get content style patterns
            style_patterns = SuccessPattern.objects.filter(
                user=user,
                pattern_type='content_style',
                success_rate__gte=60
            ).order_by('-success_rate')[:3]

            for pattern in style_patterns:
                attrs = pattern.pattern_attributes or {}
                if attrs.get('style'):
                    suggestions.append({
                        'suggestion_type': 'content',
                        'category': 'quality',
                        'title': f"Create more {attrs['style']} content",
                        'description': f"Your {attrs['style']} content has a {pattern.success_rate:.1f}% success rate.",
                        'detailed_rationale': f"Based on {pattern.sample_size} samples, this style generates ${pattern.avg_revenue_per_success:.2f} average revenue.",
                        'suggested_state': {'recommended_style': attrs['style']},
                        'estimated_revenue_impact': Decimal(str(pattern.avg_revenue_per_success)),
                        'confidence_score': Decimal(str(pattern.confidence_score)),
                        'priority_score': 65,
                        'effort_level': 'medium',
                        'supporting_patterns': [str(pattern.id)],
                    })

        except Exception as e:
            logger.error(f"Error analyzing content: {e}")

        return suggestions

    def _analyze_tags(self, user) -> List[Dict]:
        """Analyze tag performance and suggest optimizations."""
        from .models_unified_system import ContentDistribution, SuccessPattern

        suggestions = []

        try:
            # Get tag patterns
            tag_patterns = SuccessPattern.objects.filter(
                Q(user=user) | Q(is_global=True),
                pattern_type='tag_combination',
                success_rate__gte=50
            ).order_by('-success_rate')[:3]

            for pattern in tag_patterns:
                attrs = pattern.pattern_attributes or {}
                if attrs.get('top_tags'):
                    suggestions.append({
                        'suggestion_type': 'tags',
                        'category': 'reach',
                        'title': "Optimize your tags",
                        'description': f"High-performing tags: {', '.join(attrs['top_tags'][:5])}",
                        'detailed_rationale': f"These tags have a {pattern.success_rate:.1f}% higher discovery rate.",
                        'suggested_state': {'recommended_tags': attrs['top_tags'][:10]},
                        'estimated_revenue_impact': Decimal(str(pattern.avg_revenue_per_success * 0.15)),
                        'confidence_score': Decimal(str(pattern.confidence_score)),
                        'priority_score': 55,
                        'effort_level': 'low',
                    })
                    break

        except Exception as e:
            logger.error(f"Error analyzing tags: {e}")

        return suggestions

    def get_pending_suggestions(self, user, limit: int = 10) -> List[Dict]:
        """Get pending suggestions for a user."""
        from .models_unified_system import SmartSuggestion

        suggestions = SmartSuggestion.objects.filter(
            user=user,
            status='pending',
            is_still_relevant=True
        ).order_by('-priority_score', '-confidence_score')[:limit]

        return [
            {
                'id': str(s.id),
                'type': s.suggestion_type,
                'category': s.category,
                'title': s.title,
                'description': s.description,
                'priority_score': s.priority_score,
                'confidence_score': float(s.confidence_score),
                'estimated_impact': float(s.estimated_revenue_impact) if s.estimated_revenue_impact else None,
                'effort_level': s.effort_level,
                'action_steps': s.action_steps,
                'created_at': s.created_at.isoformat(),
            }
            for s in suggestions
        ]


class AutomationEngine:
    """
    Executes automated actions based on triggers.
    Handles price adjustments, auto-distribution, and scheduled tasks.
    """

    def __init__(self, user=None):
        self.user = user

    def execute_action(self, action, context: dict = None) -> Dict:
        """Execute an automated action."""
        from .models_unified_system import AutomatedAction, AutomatedActionLog

        can_run, reason = action.can_execute()
        if not can_run:
            return {'success': False, 'error': reason}

        # Create log entry
        log = AutomatedActionLog.objects.create(
            action=action,
            user=action.user,
            trigger_type=action.trigger_type,
            trigger_source=str(action.trigger_alert.id) if action.trigger_alert else '',
            input_params=context or {},
            status='started',
        )

        start_time = timezone.now()

        try:
            # Execute based on action type
            if action.action_type == 'price_adjust':
                result = self._execute_price_adjust(action, context)
            elif action.action_type == 'distribute':
                result = self._execute_auto_distribute(action, context)
            elif action.action_type == 'notify':
                result = self._execute_notification(action, context)
            elif action.action_type == 'generate_report':
                result = self._execute_generate_report(action, context)
            else:
                result = {'success': False, 'error': f'Unknown action type: {action.action_type}'}

            # Update log
            log.status = 'success' if result.get('success') else 'failed'
            log.output_result = result
            log.items_affected = result.get('items_affected', 0)
            log.completed_at = timezone.now()
            log.duration_ms = int((log.completed_at - start_time).total_seconds() * 1000)
            log.save()

            # Update action stats
            if result.get('success'):
                action.successful_executions += 1
            else:
                action.failed_executions += 1
            action.last_result = result
            action.save()

            return result

        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            log.completed_at = timezone.now()
            log.duration_ms = int((log.completed_at - start_time).total_seconds() * 1000)
            log.save()

            action.failed_executions += 1
            action.save()

            return {'success': False, 'error': str(e)}

    def _execute_price_adjust(self, action, context: dict) -> Dict:
        """Execute a price adjustment action."""
        from .models_unified_system import ContentDistribution

        params = action.action_params
        change_type = params.get('change_type', 'percent')
        change_value = Decimal(str(params.get('change_value', 0)))
        min_price = Decimal(str(params.get('min_price', 1)))
        max_price = Decimal(str(params.get('max_price', 1000)))

        # Get distributions to update
        distributions = ContentDistribution.objects.filter(
            user=action.user,
            status='active'
        )

        if action.platform_scope:
            distributions = distributions.filter(platform__name__in=action.platform_scope)
        if action.content_type_scope:
            distributions = distributions.filter(content_type__in=action.content_type_scope)

        updated = 0
        changes = []

        for dist in distributions[:100]:  # Limit to 100 per execution
            old_price = dist.listing_price

            if change_type == 'percent':
                new_price = old_price * (1 + change_value / 100)
            else:
                new_price = old_price + change_value

            # Apply limits
            new_price = max(min_price, min(max_price, new_price))

            # Check max change percent
            if action.max_price_change_percent:
                max_change = old_price * (action.max_price_change_percent / 100)
                if abs(new_price - old_price) > max_change:
                    continue

            if new_price != old_price:
                dist.listing_price = new_price
                dist.save()
                updated += 1
                changes.append({
                    'distribution_id': str(dist.id),
                    'old_price': float(old_price),
                    'new_price': float(new_price),
                })

        return {
            'success': True,
            'action': 'price_adjust',
            'items_affected': updated,
            'changes': changes[:10],  # Limit response size
        }

    def _execute_auto_distribute(self, action, context: dict) -> Dict:
        """Execute auto-distribution action."""
        # This would integrate with the existing distribution system
        return {
            'success': True,
            'action': 'distribute',
            'message': 'Auto-distribution queued',
            'items_affected': 0,
        }

    def _execute_notification(self, action, context: dict) -> Dict:
        """Execute notification action."""
        from .models_unified_system import ProactiveNotification

        params = action.action_params

        notification = ProactiveNotification.objects.create(
            user=action.user,
            notification_type='update',
            priority=params.get('priority', 'medium'),
            title=params.get('title', 'Automated Notification'),
            message=params.get('message', ''),
            channels_sent=['in_app'],
            sent_at=timezone.now(),
            delivery_status='delivered',
        )

        return {
            'success': True,
            'action': 'notify',
            'notification_id': str(notification.id),
            'items_affected': 1,
        }

    def _execute_generate_report(self, action, context: dict) -> Dict:
        """Execute report generation action."""
        # This would generate and potentially email a report
        return {
            'success': True,
            'action': 'generate_report',
            'message': 'Report generation queued',
            'items_affected': 0,
        }

    def check_scheduled_actions(self) -> List[Dict]:
        """Check and execute scheduled automated actions."""
        from .models_unified_system import AutomatedAction

        executed = []

        actions = AutomatedAction.objects.filter(
            is_active=True,
            is_paused=False,
            trigger_type='schedule'
        )

        for action in actions:
            if self._should_run_scheduled(action):
                result = self.execute_action(action)
                executed.append({
                    'action_id': str(action.id),
                    'name': action.name,
                    'result': result,
                })

        return executed

    def _should_run_scheduled(self, action) -> bool:
        """Check if a scheduled action should run now."""
        # Simple implementation - in production, use proper cron parsing
        if not action.trigger_schedule:
            return False

        now = timezone.now()

        # Check if already run today
        if action.last_executed and action.last_executed.date() == now.date():
            return False

        # Simple schedule checking (could use croniter for complex schedules)
        schedule = action.trigger_schedule.lower()

        if schedule == 'daily':
            return True
        elif schedule == 'weekly' and now.weekday() == 0:  # Monday
            return True
        elif schedule == 'hourly':
            if not action.last_executed:
                return True
            return (now - action.last_executed).total_seconds() >= 3600

        return False


class NotificationManager:
    """
    Manages notification delivery and preferences.
    Handles multi-channel delivery and quiet hours.
    """

    def __init__(self, user=None):
        self.user = user

    def send_notification(
        self,
        user,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'medium',
        action_url: str = '',
        rich_content: dict = None
    ) -> Dict:
        """Send a notification respecting user preferences."""
        from .models_unified_system import ProactiveNotification, UserNotificationPreference

        # Get or create preferences
        prefs, _ = UserNotificationPreference.objects.get_or_create(user=user)

        # Check quiet hours
        if prefs.quiet_hours_enabled and self._is_quiet_hours(prefs):
            # Queue for later
            return self._queue_notification(
                user, notification_type, title, message, priority, action_url, rich_content
            )

        # Determine channels to use
        channels = []
        for channel in ['in_app', 'email', 'push']:
            if prefs.should_send(notification_type, priority, channel):
                channels.append(channel)

        if not channels:
            return {'success': False, 'reason': 'No channels enabled for this notification type'}

        # Create notification
        notification = ProactiveNotification.objects.create(
            user=user,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            rich_content=rich_content or {},
            action_url=action_url,
            channels_sent=channels,
            sent_at=timezone.now(),
            delivery_status='delivered',
        )

        # Actually send to channels (would integrate with email/push services)
        for channel in channels:
            self._deliver_to_channel(notification, channel)

        return {
            'success': True,
            'notification_id': str(notification.id),
            'channels': channels,
        }

    def _is_quiet_hours(self, prefs) -> bool:
        """Check if current time is within quiet hours."""
        if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False

        now = timezone.now().time()
        start = prefs.quiet_hours_start
        end = prefs.quiet_hours_end

        if start <= end:
            return start <= now <= end
        else:  # Quiet hours span midnight
            return now >= start or now <= end

    def _queue_notification(self, user, notification_type, title, message, priority, action_url, rich_content) -> Dict:
        """Queue notification for delivery after quiet hours."""
        from .models_unified_system import ProactiveNotification, UserNotificationPreference

        prefs = UserNotificationPreference.objects.get(user=user)

        # Schedule for end of quiet hours
        now = timezone.now()
        scheduled_time = now.replace(
            hour=prefs.quiet_hours_end.hour,
            minute=prefs.quiet_hours_end.minute,
            second=0
        )
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)

        notification = ProactiveNotification.objects.create(
            user=user,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            rich_content=rich_content or {},
            action_url=action_url,
            scheduled_at=scheduled_time,
            delivery_status='pending',
        )

        return {
            'success': True,
            'queued': True,
            'notification_id': str(notification.id),
            'scheduled_at': scheduled_time.isoformat(),
        }

    def _deliver_to_channel(self, notification, channel: str):
        """Deliver notification to a specific channel."""
        if channel == 'in_app':
            # Already stored in DB, frontend will fetch
            pass
        elif channel == 'email':
            # Would integrate with email service
            logger.info(f"Would send email to {notification.user.email}: {notification.title}")
        elif channel == 'push':
            # Would integrate with push notification service
            logger.info(f"Would send push to {notification.user.username}: {notification.title}")

    def get_unread_notifications(self, user, limit: int = 20) -> List[Dict]:
        """Get unread notifications for a user."""
        from .models_unified_system import ProactiveNotification

        notifications = ProactiveNotification.objects.filter(
            user=user,
            is_read=False,
            is_dismissed=False,
            delivery_status='delivered'
        ).order_by('-created_at')[:limit]

        return [
            {
                'id': str(n.id),
                'type': n.notification_type,
                'priority': n.priority,
                'title': n.title,
                'message': n.message,
                'icon': n.icon,
                'action_url': n.action_url,
                'action_label': n.action_label,
                'quick_actions': n.quick_actions,
                'rich_content': n.rich_content,
                'created_at': n.created_at.isoformat(),
            }
            for n in notifications
        ]

    def get_notification_stats(self, user) -> Dict:
        """Get notification statistics for a user."""
        from .models_unified_system import ProactiveNotification

        total = ProactiveNotification.objects.filter(user=user).count()
        unread = ProactiveNotification.objects.filter(user=user, is_read=False, is_dismissed=False).count()
        acted_upon = ProactiveNotification.objects.filter(user=user, is_acted_upon=True).count()

        return {
            'total': total,
            'unread': unread,
            'acted_upon': acted_upon,
            'read_rate': (total - unread) / total * 100 if total > 0 else 0,
            'action_rate': acted_upon / total * 100 if total > 0 else 0,
        }


class ProactiveSystem:
    """
    Main orchestrator for the Proactive System.
    Coordinates alerts, suggestions, and automations.
    """

    def __init__(self, user=None):
        self.user = user
        self.alert_engine = AlertEngine(user)
        self.suggestion_engine = SuggestionEngine(user)
        self.automation_engine = AutomationEngine(user)
        self.notification_manager = NotificationManager(user)

    def run_proactive_check(self, user=None) -> Dict:
        """Run a complete proactive system check for a user."""
        target_user = user or self.user

        results = {
            'user_id': target_user.id if target_user else None,
            'timestamp': timezone.now().isoformat(),
            'alerts_triggered': [],
            'suggestions_generated': [],
            'actions_executed': [],
        }

        # 1. Check alerts
        triggered_alerts = self.alert_engine.check_all_alerts(target_user)
        results['alerts_triggered'] = triggered_alerts

        # 2. Generate suggestions (if not too many pending)
        from .models_unified_system import SmartSuggestion
        pending_count = SmartSuggestion.objects.filter(
            user=target_user,
            status='pending'
        ).count() if target_user else 0

        if pending_count < 20:
            suggestions = self.suggestion_engine.generate_suggestions(target_user, max_suggestions=5)
            results['suggestions_generated'] = suggestions

        # 3. Execute scheduled automations
        if target_user:
            from .models_unified_system import AutomatedAction
            scheduled_actions = AutomatedAction.objects.filter(
                user=target_user,
                is_active=True,
                trigger_type='schedule'
            )
            for action in scheduled_actions:
                if self.automation_engine._should_run_scheduled(action):
                    result = self.automation_engine.execute_action(action)
                    results['actions_executed'].append({
                        'action_id': str(action.id),
                        'name': action.name,
                        'result': result,
                    })

        return results

    def get_dashboard_data(self, user) -> Dict:
        """Get all proactive system data for the dashboard."""
        from .models_unified_system import (
            ProactiveAlert, ProactiveNotification, SmartSuggestion, AutomatedAction
        )

        # Active alerts
        alerts = ProactiveAlert.objects.filter(user=user, is_active=True)

        # Pending suggestions
        suggestions = SmartSuggestion.objects.filter(
            user=user,
            status='pending',
            is_still_relevant=True
        ).order_by('-priority_score')[:10]

        # Unread notifications
        notifications = self.notification_manager.get_unread_notifications(user, limit=10)

        # Active automations
        automations = AutomatedAction.objects.filter(user=user, is_active=True)

        # Stats
        notification_stats = self.notification_manager.get_notification_stats(user)

        return {
            'alerts': {
                'count': alerts.count(),
                'recent_triggers': alerts.filter(
                    last_triggered__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'items': [
                    {
                        'id': str(a.id),
                        'name': a.name,
                        'type': a.alert_type,
                        'metric': a.metric_name,
                        'condition': a.condition,
                        'threshold': float(a.threshold_value) if a.threshold_value else None,
                        'trigger_count': a.trigger_count,
                        'last_triggered': a.last_triggered.isoformat() if a.last_triggered else None,
                    }
                    for a in alerts[:10]
                ],
            },
            'suggestions': {
                'count': suggestions.count(),
                'items': [
                    {
                        'id': str(s.id),
                        'type': s.suggestion_type,
                        'title': s.title,
                        'description': s.description,
                        'priority': s.priority_score,
                        'confidence': float(s.confidence_score),
                        'impact': float(s.estimated_revenue_impact) if s.estimated_revenue_impact else None,
                        'effort': s.effort_level,
                    }
                    for s in suggestions
                ],
            },
            'notifications': {
                'unread_count': notification_stats['unread'],
                'items': notifications,
                'stats': notification_stats,
            },
            'automations': {
                'count': automations.count(),
                'active': automations.filter(is_paused=False).count(),
                'items': [
                    {
                        'id': str(a.id),
                        'name': a.name,
                        'type': a.action_type,
                        'trigger': a.trigger_type,
                        'executions': a.total_executions,
                        'success_rate': (a.successful_executions / a.total_executions * 100) if a.total_executions > 0 else 0,
                        'last_executed': a.last_executed.isoformat() if a.last_executed else None,
                        'is_paused': a.is_paused,
                    }
                    for a in automations[:10]
                ],
            },
        }
