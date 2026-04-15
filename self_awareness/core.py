"""
Core Self-Awareness Engine for Unified Donkey Betz Platform

This module implements the fundamental self-awareness capabilities:
- System introspection and monitoring
- Performance analysis and optimization
- Code analysis and understanding
- Self-healing mechanisms
"""

import ast
import psutil
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import connection
from django.core.cache import cache

from .models import (
    SystemMetrics,
    CodebaseSnapshot,
    SelfAnalysisReport,
    SelfHealingAction
)


logger = logging.getLogger(__name__)


class SelfAwarenessEngine:
    """
    Central orchestrator for all self-awareness capabilities
    """
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.code_introspector = CodeIntrospector()
        self.performance_analyzer = PerformanceAnalyzer()
        self.self_healing_agent = SelfHealingAgent()
        self.running = False
        
    def start(self):
        """Start the self-awareness engine"""
        logger.info("Starting Self-Awareness Engine...")
        self.running = True
        
        # Initialize all subsystems
        self.system_monitor.start_monitoring()
        self.code_introspector.analyze_codebase()
        
        logger.info("Self-Awareness Engine started successfully")
        
    def stop(self):
        """Stop the self-awareness engine"""
        logger.info("Stopping Self-Awareness Engine...")
        self.running = False
        
        # Cleanup subsystems
        self.system_monitor.stop_monitoring()
        
        logger.info("Self-Awareness Engine stopped")
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'timestamp': timezone.now().isoformat(),
            'running': self.running,
            'system_metrics': self.system_monitor.get_current_metrics(),
            'codebase_status': self.code_introspector.get_codebase_status(),
            'performance_status': self.performance_analyzer.get_performance_status(),
            'healing_status': self.self_healing_agent.get_healing_status(),
        }
        
    def perform_self_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive self-analysis"""
        logger.info("Performing comprehensive self-analysis...")
        
        start_time = time.time()
        
        # Collect system metrics
        metrics = self.system_monitor.collect_metrics()
        
        # Analyze codebase
        codebase_analysis = self.code_introspector.analyze_codebase()
        
        # Performance analysis
        performance_analysis = self.performance_analyzer.analyze_performance()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            metrics, codebase_analysis, performance_analysis
        )
        
        execution_time = time.time() - start_time
        
        # Store analysis report
        report = SelfAnalysisReport.objects.create(
            analysis_type='comprehensive',
            score=self._calculate_overall_score(metrics, codebase_analysis, performance_analysis),
            findings=recommendations.get('findings', []),
            recommendations=recommendations.get('actions', []),
            execution_time=execution_time,
            confidence=0.85,  # Base confidence for comprehensive analysis
            critical_issues=len([r for r in recommendations.get('findings', []) if r.get('severity') == 'critical']),
            warning_issues=len([r for r in recommendations.get('findings', []) if r.get('severity') == 'warning']),
            info_issues=len([r for r in recommendations.get('findings', []) if r.get('severity') == 'info']),
        )
        
        result = {
            'report_id': report.id,
            'execution_time': execution_time,
            'overall_score': report.score,
            'recommendations': recommendations,
            'timestamp': timezone.now().isoformat(),
        }
        
        logger.info(f"Self-analysis completed in {execution_time:.2f}s with score {report.score:.2f}")
        return result
        
    def _generate_recommendations(self, metrics: Dict, codebase: Dict, performance: Dict) -> Dict[str, List]:
        """Generate actionable recommendations based on analysis"""
        findings = []
        actions = []
        
        # Performance recommendations
        if metrics.get('cpu_usage', 0) > 80:
            findings.append({
                'category': 'performance',
                'severity': 'warning',
                'message': f"High CPU usage detected: {metrics['cpu_usage']:.1f}%",
                'details': "System may be under heavy load"
            })
            actions.append({
                'type': 'optimization',
                'priority': 8,
                'action': 'Investigate and optimize high CPU usage processes'
            })
            
        if metrics.get('memory_usage', 0) > 85:
            findings.append({
                'category': 'performance',
                'severity': 'critical',
                'message': f"High memory usage detected: {metrics['memory_usage']:.1f}%",
                'details': "Risk of out-of-memory errors"
            })
            actions.append({
                'type': 'optimization',
                'priority': 9,
                'action': 'Optimize memory usage and implement memory cleanup'
            })
            
        # Code quality recommendations
        if codebase.get('complexity_score', 0) > 7.0:
            findings.append({
                'category': 'code_quality',
                'severity': 'warning',
                'message': f"High code complexity detected: {codebase['complexity_score']:.1f}",
                'details': "Consider refactoring complex functions"
            })
            actions.append({
                'type': 'refactor',
                'priority': 6,
                'action': 'Refactor high-complexity functions for better maintainability'
            })
            
        if codebase.get('test_coverage', 0) < 70:
            findings.append({
                'category': 'testing',
                'severity': 'warning',
                'message': f"Low test coverage: {codebase['test_coverage']:.1f}%",
                'details': "Increase test coverage for better code quality"
            })
            actions.append({
                'type': 'testing',
                'priority': 7,
                'action': 'Implement additional tests to improve coverage'
            })
            
        return {
            'findings': findings,
            'actions': actions
        }
        
    def _calculate_overall_score(self, metrics: Dict, codebase: Dict, performance: Dict) -> float:
        """Calculate overall system health score (0-1)"""
        scores = []
        
        # Performance score
        cpu_score = max(0, (100 - metrics.get('cpu_usage', 0)) / 100)
        memory_score = max(0, (100 - metrics.get('memory_usage', 0)) / 100)
        disk_score = max(0, (100 - metrics.get('disk_usage', 0)) / 100)
        perf_score = (cpu_score + memory_score + disk_score) / 3
        scores.append(perf_score * 0.4)  # 40% weight
        
        # Code quality score
        complexity_score = max(0, min(1, (10 - codebase.get('complexity_score', 5)) / 10))
        coverage_score = codebase.get('test_coverage', 50) / 100
        quality_score = (complexity_score + coverage_score) / 2
        scores.append(quality_score * 0.3)  # 30% weight
        
        # System stability score (based on error rates)
        error_rate = metrics.get('error_count', 0) / max(1, metrics.get('request_count', 1))
        stability_score = max(0, 1 - error_rate * 10)
        scores.append(stability_score * 0.3)  # 30% weight
        
        return sum(scores)


class SystemMonitor:
    """
    Monitor system performance and health metrics
    """
    
    def __init__(self):
        self.monitoring = False
        self.last_metrics = {}
        
    def start_monitoring(self):
        """Start continuous system monitoring"""
        self.monitoring = True
        logger.info("System monitoring started")
        
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        logger.info("System monitoring stopped")
        
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Django database metrics
            db_queries = len(connection.queries)
            
            # Application metrics
            from core.models_unified_system import Agent  # Session 758: Fixed import path
            
            active_agents = Agent.objects.filter(status='running').count()
            pending_tasks = Agent.objects.filter(status='pending').count()
            completed_tasks = Agent.objects.filter(status='completed').count()
            
            # Calculate error rate from recent logs
            error_count = self._get_recent_error_count()
            request_count = self._get_recent_request_count()
            
            metrics = {
                'timestamp': timezone.now(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'active_agents': active_agents,
                'pending_tasks': pending_tasks,
                'completed_tasks': completed_tasks,
                'error_count': error_count,
                'db_query_count': db_queries,
                'db_avg_response_time': self._calculate_avg_db_response_time(),
                'request_count': request_count,
                'avg_response_time': self._calculate_avg_response_time(),
                'self_analysis_score': self._calculate_self_analysis_score(),
                'optimization_opportunities': self._count_optimization_opportunities(),
            }
            
            # Store metrics in database
            SystemMetrics.objects.create(**metrics)
            
            self.last_metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
            
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent metrics"""
        if not self.last_metrics:
            return self.collect_metrics()
        return self.last_metrics
        
    def _get_recent_error_count(self) -> int:
        """Count errors in the last hour"""
        # This would integrate with Django logging or external log aggregation
        # For now, return a placeholder
        return 0
        
    def _get_recent_request_count(self) -> int:
        """Count requests in the last hour"""
        # This would integrate with web server metrics
        # For now, return a placeholder
        return 100
        
    def _calculate_avg_db_response_time(self) -> float:
        """Calculate average database response time"""
        # This would analyze database query performance
        # For now, return a placeholder
        return 0.05
        
    def _calculate_avg_response_time(self) -> float:
        """Calculate average API response time"""
        # This would analyze request/response times
        # For now, return a placeholder
        return 0.2
        
    def _calculate_self_analysis_score(self) -> float:
        """Calculate how well the system understands itself"""
        # This would be based on embedding coverage, analysis completion, etc.
        return 0.75
        
    def _count_optimization_opportunities(self) -> int:
        """Count potential optimization opportunities"""
        # This would analyze code, performance, and architecture
        return 3


class CodeIntrospector:
    """
    Analyze and understand the platform's own codebase
    """
    
    def __init__(self):
        self.base_dir = Path(settings.BASE_DIR)
        self.last_analysis = {}
        
    def analyze_codebase(self) -> Dict[str, Any]:
        """Perform comprehensive codebase analysis"""
        logger.info("Analyzing codebase...")
        
        start_time = time.time()
        
        # Get all Python files (excluding venv)
        python_files = list(self.base_dir.rglob('*.py'))
        python_files = [f for f in python_files if '.venv' not in str(f) and '__pycache__' not in str(f)]
        
        # Get other important files
        js_files = list(self.base_dir.rglob('*.js'))
        js_files = [f for f in js_files if 'node_modules' not in str(f)]
        
        # Calculate statistics
        total_files = len(python_files) + len(js_files)
        total_lines = sum(self._count_lines(f) for f in python_files + js_files)
        
        # Analyze code complexity
        complexity_score = self._calculate_complexity(python_files)
        
        # Count models, views, APIs, etc.
        architecture_stats = self._analyze_architecture(python_files)
        
        # Analyze dependencies
        dependencies = self._analyze_dependencies()
        
        # Calculate test coverage (placeholder)
        test_coverage = self._calculate_test_coverage()
        
        # Detect code duplication (placeholder)
        code_duplication = self._detect_code_duplication()
        
        analysis = {
            'timestamp': timezone.now(),
            'total_files': total_files,
            'total_lines': total_lines,
            'python_files': len(python_files),
            'javascript_files': len(js_files),
            'complexity_score': complexity_score,
            'test_coverage': test_coverage,
            'code_duplication': code_duplication,
            'total_models': architecture_stats['models'],
            'total_views': architecture_stats['views'],
            'total_apis': architecture_stats['apis'],
            'total_agents': architecture_stats['agents'],
            'third_party_packages': dependencies['packages'],
            'api_integrations': dependencies['apis'],
            'files_changed': 0,  # Would track git changes
            'lines_added': 0,
            'lines_removed': 0,
        }
        
        # Store snapshot
        CodebaseSnapshot.objects.create(**analysis)
        
        execution_time = time.time() - start_time
        logger.info(f"Codebase analysis completed in {execution_time:.2f}s")
        
        self.last_analysis = analysis
        return analysis
        
    def get_codebase_status(self) -> Dict[str, Any]:
        """Get current codebase status"""
        if not self.last_analysis:
            return self.analyze_codebase()
        return self.last_analysis
        
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len(f.readlines())
        except Exception as _e:
            logger.warning(
                "core._count_lines: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0
            
    def _calculate_complexity(self, python_files: List[Path]) -> float:
        """Calculate cyclomatic complexity"""
        total_complexity = 0
        total_functions = 0
        
        for file_path in python_files[:20]:  # Sample first 20 files for performance
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = self._calculate_function_complexity(node)
                        total_complexity += complexity
                        total_functions += 1
                        
            except Exception as e:
                logger.debug(f"Could not analyze {file_path}: {e}")
                continue
                
        return total_complexity / max(1, total_functions)
        
    def _calculate_function_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
        
    def _analyze_architecture(self, python_files: List[Path]) -> Dict[str, int]:
        """Analyze Django architecture components"""
        stats = {'models': 0, 'views': 0, 'apis': 0, 'agents': 0}
        
        for file_path in python_files:
            if 'models.py' in str(file_path):
                stats['models'] += self._count_django_models(file_path)
            elif 'views.py' in str(file_path):
                stats['views'] += self._count_django_views(file_path)
            elif 'agents' in str(file_path) and 'models.py' in str(file_path):
                stats['agents'] += self._count_agents(file_path)
                
        return stats
        
    def _count_django_models(self, file_path: Path) -> int:
        """Count Django models in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            tree = ast.parse(content)
            count = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from models.Model
                    for base in node.bases:
                        if isinstance(base, ast.Attribute) and base.attr == 'Model':
                            count += 1
                            
            return count
        except Exception as _e:
            logger.warning(
                "core._count_django_models: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0
            
    def _count_django_views(self, file_path: Path) -> int:
        """Count Django views in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            tree = ast.parse(content)
            count = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Simple heuristic: functions that return HttpResponse or have request parameter
                    if any(arg.arg == 'request' for arg in node.args.args):
                        count += 1
                        
            return count
        except Exception as _e:
            logger.warning(
                "core._count_django_views: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0
            
    def _count_agents(self, file_path: Path) -> int:
        """Count agent classes"""
        return self._count_django_models(file_path)  # Agents are models too
        
    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze third-party dependencies and API integrations"""
        packages = []
        apis = []
        
        # Read requirements.txt
        req_file = self.base_dir / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package = line.split('==')[0].split('>=')[0].split('<=')[0]
                        packages.append(package)
                        
        # Detect API integrations from settings
        if hasattr(settings, 'AI_PROVIDERS'):
            for key in settings.AI_PROVIDERS:
                if '_API_KEY' in key:
                    api_name = key.replace('_API_KEY', '').lower()
                    apis.append(api_name)
                    
        return {
            'packages': packages[:20],  # Limit for storage
            'apis': apis
        }
        
    def _calculate_test_coverage(self) -> float:
        """Calculate test coverage percentage"""
        # This would integrate with coverage.py or similar
        # For now, return a reasonable estimate
        return 65.0
        
    def _detect_code_duplication(self) -> float:
        """Detect code duplication percentage"""
        # This would use AST comparison or similar techniques
        # For now, return a reasonable estimate
        return 8.5


class PerformanceAnalyzer:
    """
    Analyze system performance and identify bottlenecks
    """
    
    def __init__(self):
        self.last_analysis = {}
        
    def analyze_performance(self) -> Dict[str, Any]:
        """Perform comprehensive performance analysis"""
        logger.info("Analyzing system performance...")
        
        analysis = {
            'database_performance': self._analyze_database_performance(),
            'api_performance': self._analyze_api_performance(),
            'memory_usage': self._analyze_memory_usage(),
            'bottlenecks': self._identify_bottlenecks(),
            'optimization_suggestions': self._generate_optimization_suggestions(),
        }
        
        self.last_analysis = analysis
        return analysis
        
    def get_performance_status(self) -> Dict[str, Any]:
        """Get current performance status"""
        if not self.last_analysis:
            return self.analyze_performance()
        return self.last_analysis
        
    def _analyze_database_performance(self) -> Dict[str, Any]:
        """Analyze database query performance"""
        return {
            'query_count': len(connection.queries),
            'slow_queries': 0,  # Would analyze query times
            'index_usage': 0.85,  # Would analyze index efficiency
            'connection_pool': 'healthy'
        }
        
    def _analyze_api_performance(self) -> Dict[str, Any]:
        """Analyze API endpoint performance"""
        return {
            'avg_response_time': 0.2,
            'slow_endpoints': [],
            'error_rate': 0.01,
            'throughput': 150  # requests per minute
        }
        
    def _analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        memory = psutil.virtual_memory()
        return {
            'current_usage': memory.percent,
            'peak_usage': memory.percent + 5,  # Estimate
            'memory_leaks': [],
            'gc_efficiency': 0.92
        }
        
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify system bottlenecks"""
        bottlenecks = []
        
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            bottlenecks.append({
                'type': 'memory',
                'severity': 'high',
                'description': f'High memory usage: {memory.percent:.1f}%',
                'impact': 'System slowdown and potential OOM errors'
            })
            
        return bottlenecks
        
    def _generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate performance optimization suggestions"""
        return [
            {
                'type': 'database',
                'suggestion': 'Add database indexes for frequently queried fields',
                'impact': 'medium',
                'effort': 'low'
            },
            {
                'type': 'caching',
                'suggestion': 'Implement Redis caching for API responses',
                'impact': 'high',
                'effort': 'medium'
            },
            {
                'type': 'async',
                'suggestion': 'Convert blocking operations to async where possible',
                'impact': 'medium',
                'effort': 'high'
            }
        ]


class SelfHealingAgent:
    """
    Detect issues and automatically apply fixes
    """
    
    def __init__(self):
        self.healing_actions = []
        self.last_check = timezone.now()
        
    def detect_and_heal(self) -> Dict[str, Any]:
        """Detect issues and apply healing actions"""
        logger.info("Running self-healing detection...")
        
        issues = self._detect_issues()
        actions_taken = []
        
        for issue in issues:
            action = self._plan_healing_action(issue)
            if action:
                success = self._execute_healing_action(action)
                actions_taken.append({
                    'issue': issue,
                    'action': action,
                    'success': success
                })
                
        return {
            'issues_detected': len(issues),
            'actions_taken': len(actions_taken),
            'actions': actions_taken,
            'timestamp': timezone.now().isoformat()
        }
        
    def get_healing_status(self) -> Dict[str, Any]:
        """Get current healing status"""
        recent_actions = SelfHealingAction.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        return {
            'active_healing_actions': recent_actions.filter(status__in=['executing', 'verifying']).count(),
            'recent_successes': recent_actions.filter(success=True).count(),
            'recent_failures': recent_actions.filter(success=False).count(),
            'last_check': self.last_check.isoformat()
        }
        
    def _detect_issues(self) -> List[Dict[str, Any]]:
        """Detect system issues that can be automatically healed"""
        issues = []
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            issues.append({
                'type': 'high_memory',
                'severity': 'critical',
                'description': f'Critical memory usage: {memory.percent:.1f}%',
                'metrics': {'memory_percent': memory.percent}
            })
            
        # Check disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            issues.append({
                'type': 'high_disk',
                'severity': 'critical',
                'description': f'Critical disk usage: {disk.percent:.1f}%',
                'metrics': {'disk_percent': disk.percent}
            })
            
        # Check database health
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            issues.append({
                'type': 'database_connection',
                'severity': 'critical',
                'description': f'Database connection issue: {e}',
                'metrics': {'error': str(e)}
            })
            
        return issues
        
    def _plan_healing_action(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Plan appropriate healing action for an issue"""
        if issue['type'] == 'high_memory':
            return {
                'type': 'clear_cache',
                'description': 'Clear Django cache to free memory',
                'commands': ['cache.clear()'],
                'rollback': None
            }
            
        elif issue['type'] == 'database_connection':
            return {
                'type': 'restart_service',
                'description': 'Restart database connection',
                'commands': ['connection.close()', 'connection.connect()'],
                'rollback': None
            }
            
        return None
        
    def _execute_healing_action(self, action: Dict[str, Any]) -> bool:
        """Execute a healing action"""
        try:
            # Record the action
            healing_action = SelfHealingAction.objects.create(
                action_type=action['type'],
                issue_description=action['description'],
                issue_severity='high',
                detected_by='self_healing_agent',
                detection_confidence=0.9,
                action_plan=action,
                status='executing'
            )
            
            # Execute the action based on type
            if action['type'] == 'clear_cache':
                cache.clear()
                logger.info("Cache cleared successfully")
                
            elif action['type'] == 'restart_service':
                connection.close()
                connection.connect()
                logger.info("Database connection restarted")
                
            # Update action status
            healing_action.status = 'completed'
            healing_action.success = True
            healing_action.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Healing action failed: {e}")
            if 'healing_action' in locals():
                healing_action.status = 'failed'
                healing_action.success = False
                healing_action.action_logs.append(str(e))
                healing_action.save()
            return False