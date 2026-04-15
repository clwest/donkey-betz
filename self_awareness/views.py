"""
Self-Awareness API Views and Dashboard

This module provides REST API endpoints and views for the self-awareness system:
- System monitoring and metrics
- Codebase analysis and search
- Self-healing actions
- System evolution tracking
- Intelligence dashboard
"""

import logging
from datetime import timedelta
from typing import Dict, Any

from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    SystemMetrics,
    CodebaseSnapshot,
    SelfAnalysisReport,
    SystemEvolution,
    CodeEmbedding,
    SelfHealingAction
)
from .core import SelfAwarenessEngine, SystemMonitor
from .embeddings import CodebaseEmbeddingManager, SemanticCodeSearchEngine, ArchitectureAnalyzer
from .intelligence import AutoOptimizer, SystemEvolutionAgent


logger = logging.getLogger(__name__)


class SelfAwarenessAPIView(APIView):
    """
    Main API view for self-awareness system
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get self-awareness system status"""
        try:
            engine = SelfAwarenessEngine()
            system_status = engine.get_system_status()
            
            return Response({
                'status': 'success',
                'data': system_status,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting self-awareness status: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for system metrics
    """
    queryset = SystemMetrics.objects.all().order_by('-timestamp')
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """List recent system metrics"""
        try:
            # Get time range from query params
            hours = int(request.query_params.get('hours', 24))
            since = timezone.now() - timedelta(hours=hours)
            
            metrics = SystemMetrics.objects.filter(
                timestamp__gte=since
            ).order_by('-timestamp')
            
            # Paginate results
            paginator = Paginator(metrics, 50)
            page_number = request.query_params.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            metrics_data = []
            for metric in page_obj:
                metrics_data.append({
                    'id': metric.id,
                    'timestamp': metric.timestamp.isoformat(),
                    'cpu_usage': metric.cpu_usage,
                    'memory_usage': metric.memory_usage,
                    'disk_usage': metric.disk_usage,
                    'active_agents': metric.active_agents,
                    'pending_tasks': metric.pending_tasks,
                    'completed_tasks': metric.completed_tasks,
                    'error_count': metric.error_count,
                    'avg_response_time': metric.avg_response_time,
                    'self_analysis_score': metric.self_analysis_score,
                    'optimization_opportunities': metric.optimization_opportunities,
                })
                
            return Response({
                'status': 'success',
                'data': metrics_data,
                'pagination': {
                    'page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                },
                'summary': self._get_metrics_summary(metrics)
            })
            
        except Exception as e:
            logger.error(f"Error listing system metrics: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _get_metrics_summary(self, metrics_queryset) -> Dict[str, Any]:
        """Get summary statistics for metrics"""
        if not metrics_queryset.exists():
            return {}
            
        metrics_list = list(metrics_queryset)
        
        return {
            'avg_cpu_usage': sum(m.cpu_usage for m in metrics_list) / len(metrics_list),
            'avg_memory_usage': sum(m.memory_usage for m in metrics_list) / len(metrics_list),
            'avg_response_time': sum(m.avg_response_time for m in metrics_list) / len(metrics_list),
            'total_errors': sum(m.error_count for m in metrics_list),
            'avg_analysis_score': sum(m.self_analysis_score for m in metrics_list) / len(metrics_list),
            'total_optimization_opportunities': sum(m.optimization_opportunities for m in metrics_list),
        }
        
    @action(detail=False, methods=['post'])
    def collect_current(self, request):
        """Manually trigger metrics collection"""
        try:
            monitor = SystemMonitor()
            metrics = monitor.collect_metrics()
            
            return Response({
                'status': 'success',
                'data': metrics,
                'message': 'Current metrics collected successfully'
            })
            
        except Exception as e:
            logger.error(f"Error collecting current metrics: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CodeSearchAPIView(APIView):
    """
    API for semantic code search
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Search code using semantic similarity"""
        try:
            query = request.data.get('query', '')
            limit = int(request.data.get('limit', 10))
            min_similarity = float(request.data.get('min_similarity', 0.5))
            
            if not query:
                return Response({
                    'status': 'error',
                    'error': 'Query parameter is required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            search_engine = SemanticCodeSearchEngine()
            results = search_engine.search_code(query, limit, min_similarity)
            
            return Response({
                'status': 'success',
                'data': {
                    'query': query,
                    'results': results,
                    'count': len(results)
                }
            })
            
        except Exception as e:
            logger.error(f"Error in code search: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CodebaseAnalysisAPIView(APIView):
    """
    API for codebase analysis and embeddings
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get codebase analysis status"""
        try:
            # Get latest snapshot
            latest_snapshot = CodebaseSnapshot.objects.latest('timestamp')
            
            # Get embedding statistics
            embedding_count = CodeEmbedding.objects.count()
            latest_embedding = CodeEmbedding.objects.latest('timestamp') if embedding_count > 0 else None
            
            return Response({
                'status': 'success',
                'data': {
                    'latest_snapshot': {
                        'id': latest_snapshot.id,
                        'timestamp': latest_snapshot.timestamp.isoformat(),
                        'total_files': latest_snapshot.total_files,
                        'total_lines': latest_snapshot.total_lines,
                        'python_files': latest_snapshot.python_files,
                        'complexity_score': latest_snapshot.complexity_score,
                        'test_coverage': latest_snapshot.test_coverage,
                        'total_models': latest_snapshot.total_models,
                        'total_views': latest_snapshot.total_views,
                        'total_apis': latest_snapshot.total_apis,
                    },
                    'embeddings': {
                        'total_embeddings': embedding_count,
                        'latest_embedding': latest_embedding.timestamp.isoformat() if latest_embedding else None,
                        'coverage': self._calculate_embedding_coverage()
                    }
                }
            })
            
        except CodebaseSnapshot.DoesNotExist:
            return Response({
                'status': 'error',
                'error': 'No codebase snapshot found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting codebase analysis: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request):
        """Trigger codebase embedding process"""
        try:
            force_refresh = request.data.get('force_refresh', False)
            
            embedding_manager = CodebaseEmbeddingManager()
            result = embedding_manager.embed_entire_codebase(force_refresh=force_refresh)
            
            return Response({
                'status': 'success',
                'data': result,
                'message': 'Codebase embedding process completed'
            })
            
        except Exception as e:
            logger.error(f"Error triggering codebase embedding: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _calculate_embedding_coverage(self) -> float:
        """Calculate what percentage of codebase has embeddings"""
        try:
            latest_snapshot = CodebaseSnapshot.objects.latest('timestamp')
            embedding_files = set(CodeEmbedding.objects.values_list('file_path', flat=True))
            
            if latest_snapshot.total_files > 0:
                coverage = len(embedding_files) / latest_snapshot.total_files
                return min(1.0, coverage)  # Cap at 100%
            else:
                return 0.0
                
        except Exception as _e:
            logger.warning(
                "views._calculate_embedding_coverage: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0.0


class ArchitectureAnalysisAPIView(APIView):
    """
    API for architecture analysis
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive architecture analysis"""
        try:
            analyzer = ArchitectureAnalyzer()
            analysis = analyzer.analyze_system_architecture()
            
            return Response({
                'status': 'success',
                'data': analysis,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in architecture analysis: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SelfAnalysisAPIView(APIView):
    """
    API for self-analysis operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get recent self-analysis reports"""
        try:
            days = int(request.query_params.get('days', 7))
            since = timezone.now() - timedelta(days=days)
            
            reports = SelfAnalysisReport.objects.filter(
                timestamp__gte=since
            ).order_by('-timestamp')
            
            reports_data = []
            for report in reports:
                reports_data.append({
                    'id': report.id,
                    'timestamp': report.timestamp.isoformat(),
                    'analysis_type': report.analysis_type,
                    'score': report.score,
                    'confidence': report.confidence,
                    'critical_issues': report.critical_issues,
                    'warning_issues': report.warning_issues,
                    'info_issues': report.info_issues,
                    'execution_time': report.execution_time,
                    'findings': report.findings[:5],  # First 5 findings
                    'recommendations': report.recommendations[:5],  # First 5 recommendations
                })
                
            return Response({
                'status': 'success',
                'data': reports_data,
                'summary': self._get_analysis_summary(reports)
            })
            
        except Exception as e:
            logger.error(f"Error getting self-analysis reports: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request):
        """Trigger comprehensive self-analysis"""
        try:
            engine = SelfAwarenessEngine()
            result = engine.perform_self_analysis()
            
            return Response({
                'status': 'success',
                'data': result,
                'message': 'Self-analysis completed successfully'
            })
            
        except Exception as e:
            logger.error(f"Error triggering self-analysis: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _get_analysis_summary(self, reports_queryset) -> Dict[str, Any]:
        """Get summary of analysis reports"""
        if not reports_queryset.exists():
            return {}
            
        reports_list = list(reports_queryset)
        
        return {
            'total_reports': len(reports_list),
            'avg_score': sum(r.score for r in reports_list) / len(reports_list),
            'total_critical_issues': sum(r.critical_issues for r in reports_list),
            'total_warning_issues': sum(r.warning_issues for r in reports_list),
            'avg_execution_time': sum(r.execution_time for r in reports_list) / len(reports_list),
            'analysis_types': list(set(r.analysis_type for r in reports_list)),
        }


class SystemEvolutionAPIView(APIView):
    """
    API for system evolution tracking and management
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get system evolution history"""
        try:
            limit = int(request.query_params.get('limit', 20))
            evolution_type = request.query_params.get('type')
            status_filter = request.query_params.get('status')
            
            evolutions = SystemEvolution.objects.all()
            
            if evolution_type:
                evolutions = evolutions.filter(evolution_type=evolution_type)
            if status_filter:
                evolutions = evolutions.filter(status=status_filter)
                
            evolutions = evolutions.order_by('-timestamp')[:limit]
            
            evolution_data = []
            for evolution in evolutions:
                evolution_data.append({
                    'id': evolution.id,
                    'timestamp': evolution.timestamp.isoformat(),
                    'evolution_type': evolution.evolution_type,
                    'status': evolution.status,
                    'title': evolution.title,
                    'description': evolution.description,
                    'confidence_score': evolution.confidence_score,
                    'priority': evolution.priority,
                    'started_at': evolution.started_at.isoformat() if evolution.started_at else None,
                    'completed_at': evolution.completed_at.isoformat() if evolution.completed_at else None,
                    'expected_benefit': evolution.expected_benefit,
                    'risk_assessment': evolution.risk_assessment,
                })
                
            return Response({
                'status': 'success',
                'data': evolution_data,
                'summary': self._get_evolution_summary(SystemEvolution.objects.all()[:50])
            })
            
        except Exception as e:
            logger.error(f"Error getting system evolution history: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request):
        """Trigger autonomous system evolution"""
        try:
            evolution_agent = SystemEvolutionAgent()
            result = evolution_agent.evolve_system()
            
            return Response({
                'status': 'success',
                'data': result,
                'message': 'System evolution process completed'
            })
            
        except Exception as e:
            logger.error(f"Error triggering system evolution: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _get_evolution_summary(self, evolutions_queryset) -> Dict[str, Any]:
        """Get summary of system evolutions"""
        if not evolutions_queryset.exists():
            return {}
            
        evolutions_list = list(evolutions_queryset)
        
        status_counts = {}
        type_counts = {}
        
        for evolution in evolutions_list:
            status_counts[evolution.status] = status_counts.get(evolution.status, 0) + 1
            type_counts[evolution.evolution_type] = type_counts.get(evolution.evolution_type, 0) + 1
            
        return {
            'total_evolutions': len(evolutions_list),
            'status_distribution': status_counts,
            'type_distribution': type_counts,
            'avg_confidence': sum(e.confidence_score for e in evolutions_list) / len(evolutions_list),
            'success_rate': status_counts.get('completed', 0) / len(evolutions_list) if evolutions_list else 0,
        }


class OptimizationAPIView(APIView):
    """
    API for system optimization operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get optimization opportunities"""
        try:
            optimizer = AutoOptimizer()
            opportunities = optimizer.identify_optimization_opportunities()
            
            opportunities_data = []
            for opp in opportunities:
                opportunities_data.append({
                    'type': opp.type,
                    'description': opp.description,
                    'estimated_impact': opp.estimated_impact,
                    'implementation_effort': opp.implementation_effort,
                    'confidence': opp.confidence,
                    'code_changes': opp.code_changes,
                    'test_requirements': opp.test_requirements,
                    'rollback_plan': opp.rollback_plan,
                })
                
            return Response({
                'status': 'success',
                'data': opportunities_data,
                'count': len(opportunities_data)
            })
            
        except Exception as e:
            logger.error(f"Error getting optimization opportunities: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request):
        """Trigger optimization implementation"""
        try:
            optimization_type = request.data.get('type')
            
            if not optimization_type:
                return Response({
                    'status': 'error',
                    'error': 'Optimization type is required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            optimizer = AutoOptimizer()
            opportunities = optimizer.identify_optimization_opportunities()
            
            # Find the requested optimization
            target_optimization = None
            for opp in opportunities:
                if opp.type == optimization_type:
                    target_optimization = opp
                    break
                    
            if not target_optimization:
                return Response({
                    'status': 'error',
                    'error': f'Optimization type "{optimization_type}" not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
            result = optimizer.implement_optimization(target_optimization)
            
            return Response({
                'status': 'success',
                'data': result,
                'message': f'Optimization "{optimization_type}" implementation attempted'
            })
            
        except Exception as e:
            logger.error(f"Error implementing optimization: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SelfHealingAPIView(APIView):
    """
    API for self-healing operations
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get self-healing action history"""
        try:
            days = int(request.query_params.get('days', 7))
            since = timezone.now() - timedelta(days=days)
            
            actions = SelfHealingAction.objects.filter(
                timestamp__gte=since
            ).order_by('-timestamp')
            
            actions_data = []
            for action in actions:
                actions_data.append({
                    'id': action.id,
                    'timestamp': action.timestamp.isoformat(),
                    'action_type': action.action_type,
                    'status': action.status,
                    'issue_description': action.issue_description,
                    'issue_severity': action.issue_severity,
                    'detected_by': action.detected_by,
                    'detection_confidence': action.detection_confidence,
                    'success': action.success,
                    'effectiveness_score': action.effectiveness_score,
                    'resolution_time': action.resolution_time,
                })
                
            return Response({
                'status': 'success',
                'data': actions_data,
                'summary': self._get_healing_summary(actions)
            })
            
        except Exception as e:
            logger.error(f"Error getting self-healing history: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request):
        """Trigger self-healing detection and action"""
        try:
            from .core import SelfHealingAgent
            
            healing_agent = SelfHealingAgent()
            result = healing_agent.detect_and_heal()
            
            return Response({
                'status': 'success',
                'data': result,
                'message': 'Self-healing process completed'
            })
            
        except Exception as e:
            logger.error(f"Error triggering self-healing: {e}")
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _get_healing_summary(self, actions_queryset) -> Dict[str, Any]:
        """Get summary of healing actions"""
        if not actions_queryset.exists():
            return {}
            
        actions_list = list(actions_queryset)
        
        return {
            'total_actions': len(actions_list),
            'success_count': len([a for a in actions_list if a.success]),
            'failure_count': len([a for a in actions_list if a.success is False]),
            'pending_count': len([a for a in actions_list if a.success is None]),
            'avg_resolution_time': sum(a.resolution_time or 0 for a in actions_list) / len(actions_list),
            'severity_distribution': {
                severity: len([a for a in actions_list if a.issue_severity == severity])
                for severity in ['low', 'medium', 'high', 'critical']
            }
        }


@login_required
def dashboard_view(request):
    """
    Unified intelligence dashboard view
    """
    try:
        # Get recent metrics for dashboard
        recent_metrics = SystemMetrics.objects.order_by('-timestamp')[:24]  # Last 24 data points
        
        # Get latest analysis report
        latest_analysis = SelfAnalysisReport.objects.order_by('-timestamp').first()
        
        # Get active system evolutions
        active_evolutions = SystemEvolution.objects.filter(
            status__in=['proposed', 'analyzing', 'testing', 'implementing']
        ).order_by('-priority', '-timestamp')[:5]
        
        # Get recent healing actions
        recent_healing = SelfHealingAction.objects.order_by('-timestamp')[:5]
        
        # Get embedding status
        embedding_count = CodeEmbedding.objects.count()
        latest_snapshot = CodebaseSnapshot.objects.order_by('-timestamp').first()
        
        context = {
            'metrics_data': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'response_time': m.avg_response_time,
                    'error_count': m.error_count,
                    'analysis_score': m.self_analysis_score,
                } for m in reversed(recent_metrics)
            ],
            'latest_analysis': {
                'id': latest_analysis.id,
                'score': latest_analysis.score,
                'timestamp': latest_analysis.timestamp.isoformat(),
                'critical_issues': latest_analysis.critical_issues,
                'warning_issues': latest_analysis.warning_issues,
                'recommendations': latest_analysis.recommendations[:3],  # Top 3
            } if latest_analysis else None,
            'active_evolutions': [
                {
                    'id': e.id,
                    'title': e.title,
                    'type': e.evolution_type,
                    'status': e.status,
                    'priority': e.priority,
                    'confidence': e.confidence_score,
                } for e in active_evolutions
            ],
            'recent_healing': [
                {
                    'id': h.id,
                    'action_type': h.action_type,
                    'status': h.status,
                    'severity': h.issue_severity,
                    'success': h.success,
                    'timestamp': h.timestamp.isoformat(),
                } for h in recent_healing
            ],
            'codebase_status': {
                'total_embeddings': embedding_count,
                'total_files': latest_snapshot.total_files if latest_snapshot else 0,
                'total_lines': latest_snapshot.total_lines if latest_snapshot else 0,
                'complexity_score': latest_snapshot.complexity_score if latest_snapshot else 0,
                'test_coverage': latest_snapshot.test_coverage if latest_snapshot else 0,
            },
            'system_health': {
                'overall_score': latest_analysis.score if latest_analysis else 0.75,
                'status': 'healthy' if not latest_analysis or latest_analysis.score > 0.8 else 'warning' if latest_analysis.score > 0.6 else 'critical',
            }
        }
        
        return render(request, 'self_awareness/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return render(request, 'self_awareness/dashboard_error.html', {'error': str(e)})


# API endpoint for WebSocket updates
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def realtime_status(request):
    """Get real-time system status for WebSocket updates"""
    try:
        # Get current system status
        engine = SelfAwarenessEngine()
        system_status = engine.get_system_status()
        
        # Get latest metrics
        latest_metrics = SystemMetrics.objects.order_by('-timestamp').first()
        
        # Get active issues
        active_healing = SelfHealingAction.objects.filter(
            status__in=['detecting', 'analyzing', 'planning', 'executing']
        ).count()
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'system_running': system_status['running'],
            'current_metrics': {
                'cpu_usage': latest_metrics.cpu_usage if latest_metrics else 0,
                'memory_usage': latest_metrics.memory_usage if latest_metrics else 0,
                'active_agents': latest_metrics.active_agents if latest_metrics else 0,
                'error_count': latest_metrics.error_count if latest_metrics else 0,
            },
            'active_healing_actions': active_healing,
            'health_score': latest_metrics.self_analysis_score if latest_metrics else 0.0,
        })
        
    except Exception as e:
        logger.error(f"Error getting realtime status: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
