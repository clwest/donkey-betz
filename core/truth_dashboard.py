"""
Truth Dashboard - Reality Visualization Engine
==============================================

This module provides comprehensive visualization and reporting of platform
reality status. It generates human-readable reality reports, provides JSON APIs
for programmatic access, and offers actionable insights for fixing issues.

The TruthDashboard provides:
- Human-readable reality reports
- JSON API for programmatic access
- Visual component status maps
- Critical issue highlighting
- Fix recommendation prioritization
- Real-time monitoring capabilities
"""

import logging
from typing import Dict, Any, List
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils import timezone
from django.core.cache import cache

from .reality_check import system_reality_checker, ComponentType
from .data_flow_tracer import data_flow_tracer, FlowType

logger = logging.getLogger(__name__)


class TruthDashboard:
    """
    Comprehensive reality visualization and reporting engine.

    Provides multiple interfaces for accessing platform reality data:
    - Web dashboard with visual components
    - JSON API for programmatic access
    - Detailed reports with recommendations
    - Real-time monitoring capabilities
    """

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate complete dashboard data with reality status and metrics.

        Returns:
            Comprehensive dashboard data including status, metrics, and recommendations
        """
        logger.info("Generating truth dashboard data")

        # Get reality report
        reality_report = system_reality_checker.generate_reality_report()

        # Get data flow health
        flow_health = {}
        for flow_type in FlowType:
            try:
                health = data_flow_tracer.get_pipeline_health(flow_type, hours=24)
                flow_health[flow_type.value] = health
            except Exception as e:
                logger.error(f"Error getting flow health for {flow_type}: {e}")
                flow_health[flow_type.value] = {
                    'status': 'error',
                    'message': str(e)
                }

        # Calculate overall platform health score
        overall_health = self._calculate_overall_health(reality_report, flow_health)

        # Generate component status map
        component_map = self._generate_component_map(reality_report)

        # Get critical issues and quick wins
        critical_issues = self._extract_critical_issues(reality_report)
        quick_wins = self._identify_quick_wins(reality_report)

        # Get recent activity
        recent_activity = self._get_recent_activity()

        dashboard_data = {
            'generated_at': timezone.now().isoformat(),
            'overall_health': overall_health,
            'reality_report': reality_report,
            'flow_health': flow_health,
            'component_map': component_map,
            'critical_issues': critical_issues,
            'quick_wins': quick_wins,
            'recent_activity': recent_activity,
            'summary': {
                'total_components': len(reality_report.get('components', {})),
                'operational_components': len([
                    c for c in reality_report.get('components', {}).values()
                    if c.get('status') == 'real'
                ]),
                'broken_components': len([
                    c for c in reality_report.get('components', {}).values()
                    if c.get('status') == 'broken'
                ]),
                'mock_components': len([
                    c for c in reality_report.get('components', {}).values()
                    if c.get('status') == 'mock'
                ]),
                'total_issues': len(critical_issues),
                'total_recommendations': len(quick_wins)
            },
            'next_actions': self._generate_next_actions(critical_issues, quick_wins)
        }

        # Cache dashboard data
        cache.set('truth_dashboard_data', dashboard_data, timeout=self.cache_timeout)

        return dashboard_data

    def _calculate_overall_health(self, reality_report: Dict, flow_health: Dict) -> Dict[str, Any]:
        """Calculate overall platform health score"""
        reality_score = reality_report.get('overall_reality_score', 0.0)

        # Calculate average flow health
        flow_scores = []
        for flow_data in flow_health.values():
            if flow_data.get('status') != 'error' and flow_data.get('metrics'):
                success_rate = flow_data['metrics'].get('success_rate', 0.0)
                flow_scores.append(success_rate)

        avg_flow_health = sum(flow_scores) / len(flow_scores) if flow_scores else 0.0

        # Combined health score (weighted)
        combined_score = (reality_score * 0.7) + (avg_flow_health * 0.3)

        # Determine health status
        if combined_score >= 0.9:
            status = "excellent"
            color = "#10B981"  # Green
            message = "Platform is fully operational"
        elif combined_score >= 0.7:
            status = "good"
            color = "#3B82F6"  # Blue
            message = "Platform is mostly operational"
        elif combined_score >= 0.5:
            status = "fair"
            color = "#F59E0B"  # Yellow
            message = "Platform has significant issues"
        elif combined_score >= 0.3:
            status = "poor"
            color = "#EF4444"  # Red
            message = "Platform is mostly non-functional"
        else:
            status = "critical"
            color = "#7C2D12"  # Dark red
            message = "Platform is critically broken"

        return {
            'score': round(combined_score, 3),
            'status': status,
            'color': color,
            'message': message,
            'reality_score': round(reality_score, 3),
            'flow_score': round(avg_flow_health, 3),
            'breakdown': {
                'reality_weight': 0.7,
                'flow_weight': 0.3
            }
        }

    def _generate_component_map(self, reality_report: Dict) -> List[Dict[str, Any]]:
        """Generate visual component status map"""
        components = reality_report.get('components', {})

        component_map = []
        for component_name, component_data in components.items():
            status = component_data.get('status', 'unknown')
            confidence = component_data.get('confidence', 0.0)

            # Determine visual properties
            if status == 'real':
                color = "#10B981"
                icon = "✅"
            elif status == 'partial':
                color = "#F59E0B"
                icon = "⚠️"
            elif status == 'mock':
                color = "#6B7280"
                icon = "🎭"
            elif status == 'broken':
                color = "#EF4444"
                icon = "❌"
            else:
                color = "#9CA3AF"
                icon = "❓"

            component_map.append({
                'name': component_name.replace('_', ' ').title(),
                'key': component_name,
                'status': status,
                'confidence': confidence,
                'color': color,
                'icon': icon,
                'issues_count': len(component_data.get('issues_found', [])),
                'recommendations_count': len(component_data.get('recommendations', [])),
                'last_checked': component_data.get('last_checked'),
                'details': component_data.get('details', {})
            })

        # Sort by status (broken first, then mock, partial, real)
        status_order = {'broken': 0, 'mock': 1, 'partial': 2, 'real': 3, 'unknown': 4}
        component_map.sort(key=lambda x: (status_order.get(x['status'], 5), -x['confidence']))

        return component_map

    def _extract_critical_issues(self, reality_report: Dict) -> List[Dict[str, Any]]:
        """Extract and prioritize critical issues"""
        critical_issues = reality_report.get('critical_issues', [])

        # Add priority scoring
        prioritized_issues = []
        for issue in critical_issues:
            component = issue.get('component', 'unknown')
            issue_text = issue.get('issue', '')

            # Calculate priority score
            priority_score = 0
            if 'broken' in issue_text.lower():
                priority_score += 10
            if 'failed' in issue_text.lower():
                priority_score += 8
            if 'not found' in issue_text.lower():
                priority_score += 6
            if 'not configured' in issue_text.lower():
                priority_score += 4
            if 'no data' in issue_text.lower():
                priority_score += 3

            # Boost priority for core components
            core_components = ['database', 'websocket_hub', 'income_builder']
            if component in core_components:
                priority_score += 5

            prioritized_issues.append({
                'component': component,
                'issue': issue_text,
                'priority_score': priority_score,
                'severity': 'critical' if priority_score >= 10 else 'high' if priority_score >= 6 else 'medium',
                'category': self._categorize_issue(issue_text)
            })

        # Sort by priority score
        prioritized_issues.sort(key=lambda x: x['priority_score'], reverse=True)

        return prioritized_issues[:10]  # Top 10 critical issues

    def _identify_quick_wins(self, reality_report: Dict) -> List[Dict[str, Any]]:
        """Identify quick wins - easy fixes with high impact"""
        all_recommendations = []

        components = reality_report.get('components', {})
        for component_name, component_data in components.items():
            recommendations = component_data.get('recommendations', [])

            for rec in recommendations:
                # Score recommendations for impact and ease
                impact_score = self._score_recommendation_impact(rec)
                ease_score = self._score_recommendation_ease(rec)
                total_score = impact_score + ease_score

                all_recommendations.append({
                    'component': component_name,
                    'recommendation': rec,
                    'impact_score': impact_score,
                    'ease_score': ease_score,
                    'total_score': total_score,
                    'category': self._categorize_recommendation(rec)
                })

        # Sort by total score (high impact + easy implementation)
        all_recommendations.sort(key=lambda x: x['total_score'], reverse=True)

        return all_recommendations[:8]  # Top 8 quick wins

    def _score_recommendation_impact(self, recommendation: str) -> int:
        """Score recommendation impact (0-10)"""
        score = 0
        rec_lower = recommendation.lower()

        if 'configure' in rec_lower and 'api' in rec_lower:
            score += 8  # API configuration is high impact
        if 'deploy' in rec_lower:
            score += 7
        if 'fix' in rec_lower:
            score += 6
        if 'install' in rec_lower:
            score += 5
        if 'update' in rec_lower:
            score += 4
        if 'create' in rec_lower:
            score += 3

        return min(score, 10)

    def _score_recommendation_ease(self, recommendation: str) -> int:
        """Score recommendation ease of implementation (0-10)"""
        score = 0
        rec_lower = recommendation.lower()

        if 'configure' in rec_lower and 'key' in rec_lower:
            score += 9  # API key configuration is easy
        if 'install' in rec_lower:
            score += 7
        if 'update' in rec_lower:
            score += 6
        if 'create' in rec_lower and 'user' in rec_lower:
            score += 8  # Creating users is easy
        if 'debug' in rec_lower:
            score += 3  # Debugging can be complex

        return min(score, 10)

    def _categorize_issue(self, issue: str) -> str:
        """Categorize issue by type"""
        issue_lower = issue.lower()

        if 'not configured' in issue_lower or 'api' in issue_lower:
            return 'configuration'
        elif 'not found' in issue_lower or 'not available' in issue_lower:
            return 'missing_component'
        elif 'connection failed' in issue_lower:
            return 'connectivity'
        elif 'no data' in issue_lower:
            return 'data'
        elif 'broken' in issue_lower or 'failed' in issue_lower:
            return 'functionality'
        else:
            return 'other'

    def _categorize_recommendation(self, recommendation: str) -> str:
        """Categorize recommendation by type"""
        rec_lower = recommendation.lower()

        if 'configure' in rec_lower:
            return 'configuration'
        elif 'deploy' in rec_lower or 'install' in rec_lower:
            return 'deployment'
        elif 'fix' in rec_lower or 'debug' in rec_lower:
            return 'bug_fix'
        elif 'update' in rec_lower or 'upgrade' in rec_lower:
            return 'update'
        elif 'create' in rec_lower:
            return 'setup'
        else:
            return 'optimization'

    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent system activity and changes"""
        activity = []

        # Check for recent traces
        try:
            recent_traces = data_flow_tracer.completed_traces[-5:]  # Last 5 traces
            for trace in recent_traces:
                activity.append({
                    'type': 'trace_completed',
                    'timestamp': trace.end_time.isoformat() if trace.end_time else trace.start_time.isoformat(),
                    'message': f"{trace.flow_type.value} flow {'succeeded' if trace.success else 'failed'}",
                    'details': {
                        'flow_id': trace.flow_id,
                        'processing_time': trace.total_processing_time_ms
                    }
                })
        except Exception as e:
            logger.error(f"Error getting recent traces: {e}")

        # Check for recent reality checks (from cache)
        try:
            for component_type in ComponentType:
                cached_check = cache.get(f"reality_check_{component_type.value}")
                if cached_check:
                    activity.append({
                        'type': 'reality_check',
                        'timestamp': cached_check.get('last_checked'),
                        'message': f"{component_type.value} checked: {cached_check.get('status')}",
                        'details': {
                            'component': component_type.value,
                            'confidence': cached_check.get('confidence')
                        }
                    })
        except Exception as e:
            logger.error(f"Error getting cached reality checks: {e}")

        # Sort by timestamp (newest first)
        activity.sort(key=lambda x: x['timestamp'], reverse=True)

        return activity[:10]  # Return last 10 activities

    def _generate_next_actions(self, critical_issues: List[Dict], quick_wins: List[Dict]) -> List[Dict[str, Any]]:
        """Generate prioritized next actions"""
        next_actions = []

        # Add top critical issues
        for issue in critical_issues[:3]:
            next_actions.append({
                'type': 'fix_critical',
                'priority': 'critical',
                'component': issue['component'],
                'action': f"Fix: {issue['issue']}",
                'category': issue['category'],
                'estimated_effort': 'high' if issue['severity'] == 'critical' else 'medium'
            })

        # Add top quick wins
        for win in quick_wins[:3]:
            next_actions.append({
                'type': 'quick_win',
                'priority': 'high',
                'component': win['component'],
                'action': win['recommendation'],
                'category': win['category'],
                'estimated_effort': 'low' if win['ease_score'] >= 7 else 'medium'
            })

        return next_actions

    def generate_html_report(self) -> str:
        """Generate HTML report for web display"""
        dashboard_data = self.generate_dashboard_data()

        # Create HTML template
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Platform Truth Dashboard</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8fafc;
                    color: #1e293b;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    text-align: center;
                }
                .health-score {
                    font-size: 3em;
                    font-weight: bold;
                    margin: 10px 0;
                }
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .card {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .component {
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 6px;
                    background: #f1f5f9;
                }
                .component-icon {
                    font-size: 1.5em;
                    margin-right: 10px;
                }
                .issue {
                    padding: 10px;
                    margin: 5px 0;
                    border-left: 4px solid #ef4444;
                    background: #fef2f2;
                    border-radius: 4px;
                }
                .quick-win {
                    padding: 10px;
                    margin: 5px 0;
                    border-left: 4px solid #10b981;
                    background: #f0fdf4;
                    border-radius: 4px;
                }
                .status-excellent { color: #10b981; }
                .status-good { color: #3b82f6; }
                .status-fair { color: #f59e0b; }
                .status-poor { color: #ef4444; }
                .status-critical { color: #7c2d12; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Platform Truth Dashboard</h1>
                <div class="health-score status-{{ health.status }}">{{ health.score | floatformat:1 }}%</div>
                <p>{{ health.message }}</p>
                <small>Generated at {{ generated_at }}</small>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>📊 Component Status</h2>
                    {% for component in component_map %}
                    <div class="component">
                        <span class="component-icon">{{ component.icon }}</span>
                        <div>
                            <strong>{{ component.name }}</strong>
                            <br>
                            <small>{{ component.status|title }} ({{ component.confidence|floatformat:1 }}% confidence)</small>
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <div class="card">
                    <h2>🚨 Critical Issues</h2>
                    {% for issue in critical_issues %}
                    <div class="issue">
                        <strong>{{ issue.component|title }}</strong>: {{ issue.issue }}
                        <br>
                        <small>Severity: {{ issue.severity|title }} | Category: {{ issue.category|title }}</small>
                    </div>
                    {% endfor %}
                </div>

                <div class="card">
                    <h2>⚡ Quick Wins</h2>
                    {% for win in quick_wins %}
                    <div class="quick-win">
                        <strong>{{ win.component|title }}</strong>: {{ win.recommendation }}
                        <br>
                        <small>Impact: {{ win.impact_score }}/10 | Ease: {{ win.ease_score }}/10</small>
                    </div>
                    {% endfor %}
                </div>

                <div class="card">
                    <h2>📈 Summary Stats</h2>
                    <ul>
                        <li><strong>{{ summary.operational_components }}</strong> of {{ summary.total_components }} components operational</li>
                        <li><strong>{{ summary.broken_components }}</strong> components broken</li>
                        <li><strong>{{ summary.mock_components }}</strong> components using mock data</li>
                        <li><strong>{{ summary.total_issues }}</strong> total issues found</li>
                        <li><strong>{{ summary.total_recommendations }}</strong> recommendations available</li>
                    </ul>
                </div>
            </div>

            <div class="card">
                <h2>🎯 Next Actions</h2>
                <ol>
                    {% for action in next_actions %}
                    <li>
                        <strong>{{ action.component|title }}</strong>: {{ action.action }}
                        <br>
                        <small>Priority: {{ action.priority|title }} | Effort: {{ action.estimated_effort|title }}</small>
                    </li>
                    {% endfor %}
                </ol>
            </div>
        </body>
        </html>
        """

        # For simplicity, we'll do basic template substitution
        # In a real Django app, you'd use the template engine
        html = html_template.replace('{{ health.status }}', dashboard_data['overall_health']['status'])
        html = html.replace('{{ health.score | floatformat:1 }}', f"{dashboard_data['overall_health']['score']*100:.1f}")
        html = html.replace('{{ health.message }}', dashboard_data['overall_health']['message'])
        html = html.replace('{{ generated_at }}', dashboard_data['generated_at'])

        return html

    def generate_json_report(self) -> Dict[str, Any]:
        """Generate JSON report for API access"""
        return self.generate_dashboard_data()

    def get_component_detail(self, component_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific component"""
        dashboard_data = self.generate_dashboard_data()
        components = dashboard_data['reality_report'].get('components', {})

        if component_name not in components:
            return {'error': f'Component {component_name} not found'}

        component_data = components[component_name]

        # Add flow health for this component if applicable
        related_flows = []
        for flow_name, flow_data in dashboard_data['flow_health'].items():
            if component_name in flow_name or any(component_name in stage for stage in flow_data.get('stage_performance', {}).get('avg_times_ms', {}).keys()):
                related_flows.append({
                    'flow_type': flow_name,
                    'health': flow_data
                })

        return {
            'component': component_name,
            'status': component_data.get('status'),
            'confidence': component_data.get('confidence'),
            'details': component_data.get('details', {}),
            'checks_performed': component_data.get('checks_performed', []),
            'issues_found': component_data.get('issues_found', []),
            'recommendations': component_data.get('recommendations', []),
            'last_checked': component_data.get('last_checked'),
            'related_flows': related_flows
        }


# Global instance for easy access
truth_dashboard = TruthDashboard()


# Django Views for web access
class TruthDashboardView(View):
    """Django view for accessing truth dashboard"""

    def get(self, request):
        """Return HTML dashboard"""
        try:
            html_report = truth_dashboard.generate_html_report()
            return HttpResponse(html_report, content_type='text/html')
        except Exception as e:
            logger.error(f"Error generating HTML dashboard: {e}")
            return HttpResponse(f"Error generating dashboard: {str(e)}", status=500)


class TruthDashboardAPIView(View):
    """Django API view for accessing truth dashboard data"""

    def get(self, request):
        """Return JSON dashboard data"""
        try:
            json_report = truth_dashboard.generate_json_report()
            return JsonResponse(json_report)
        except Exception as e:
            logger.error(f"Error generating JSON dashboard: {e}")
            return JsonResponse({'error': str(e)}, status=500)


class ComponentDetailAPIView(View):
    """Django API view for component details"""

    def get(self, request, component_name):
        """Return detailed component information"""
        try:
            component_detail = truth_dashboard.get_component_detail(component_name)
            return JsonResponse(component_detail)
        except Exception as e:
            logger.error(f"Error getting component detail: {e}")
            return JsonResponse({'error': str(e)}, status=500)