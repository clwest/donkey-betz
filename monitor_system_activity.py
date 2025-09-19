#!/usr/bin/env python3
"""
🔍 REAL-TIME SYSTEM MONITOR
Track the activity of your activated agents, spiders, and revenue generation
"""

import os
import sys
import django
import time
import asyncio
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Dict, List

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.db.models import Count, Sum, Avg
from agents.models import UnifiedAgentTemplate, AgentExecution
from django.contrib.auth import get_user_model

console = Console()


class SystemMonitor:
    """Real-time monitoring of the activated platform"""
    
    def __init__(self):
        self.console = Console()
        self.refresh_rate = 2  # seconds
        
    def get_agent_activity(self) -> Dict:
        """Get current agent activity metrics"""
        try:
            total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            
            # Get recent executions
            recent_time = datetime.now() - timedelta(minutes=10)
            recent_executions = AgentExecution.objects.filter(
                created_at__gte=recent_time
            ).count()
            
            # Get agent groups
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COALESCE(metadata->>'group', 'ungrouped') as group_name,
                        COUNT(*) as agent_count
                    FROM agents_unifiedagenttemplate
                    WHERE is_active = true
                    GROUP BY metadata->>'group'
                """)
                groups = dict(cursor.fetchall())
            
            return {
                'total': total_agents,
                'recent_executions': recent_executions,
                'groups': groups,
                'active_rate': (recent_executions / total_agents * 100) if total_agents > 0 else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_spider_activity(self) -> Dict:
        """Get spider harvesting metrics"""
        try:
            # Check for spider data in the database
            with connection.cursor() as cursor:
                # Count AI strategies
                cursor.execute("""
                    SELECT COUNT(*) FROM core_aistrategy
                    WHERE created_at >= NOW() - INTERVAL '10 minutes'
                """)
                recent_strategies = cursor.fetchone()[0]
                
                # Count generated projects
                cursor.execute("""
                    SELECT COUNT(*) FROM core_generatedproject
                    WHERE created_at >= NOW() - INTERVAL '10 minutes'
                """)
                recent_projects = cursor.fetchone()[0]
                
                # Get spider categories
                cursor.execute("""
                    SELECT 
                        strategy_type,
                        COUNT(*) as count
                    FROM core_aistrategy
                    GROUP BY strategy_type
                    LIMIT 5
                """)
                categories = dict(cursor.fetchall())
            
            return {
                'recent_strategies': recent_strategies,
                'recent_projects': recent_projects,
                'categories': categories,
                'harvest_rate': f"{recent_strategies * 6}/hour"  # 10 min * 6 = hourly
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_revenue_metrics(self) -> Dict:
        """Get revenue generation metrics"""
        try:
            with connection.cursor() as cursor:
                # Get project values
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_projects,
                        AVG(CAST(metadata->>'estimated_revenue' AS FLOAT)) as avg_revenue,
                        SUM(CAST(metadata->>'estimated_revenue' AS FLOAT)) as total_potential
                    FROM core_generatedproject
                    WHERE metadata->>'estimated_revenue' IS NOT NULL
                """)
                result = cursor.fetchone()
                
                return {
                    'total_projects': result[0] or 0,
                    'avg_project_value': result[1] or 0,
                    'total_potential': result[2] or 0,
                    'conversion_rate': 10,  # 10% assumed
                    'projected_monthly': (result[2] or 0) * 0.1
                }
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_health(self) -> Dict:
        """Get overall system health metrics"""
        try:
            with connection.cursor() as cursor:
                # Database size
                cursor.execute("""
                    SELECT pg_database_size(current_database()) / 1024 / 1024 as size_mb
                """)
                db_size = cursor.fetchone()[0]
                
                # Embedding count
                cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
                embeddings = cursor.fetchone()[0]
                
                # Active connections
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_stat_activity 
                    WHERE state = 'active'
                """)
                connections = cursor.fetchone()[0]
            
            return {
                'db_size_mb': round(db_size, 2),
                'embeddings': embeddings,
                'connections': connections,
                'status': 'HEALTHY' if connections < 50 else 'STRESSED'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def create_dashboard(self) -> Table:
        """Create the monitoring dashboard"""
        # Get all metrics
        agents = self.get_agent_activity()
        spiders = self.get_spider_activity()
        revenue = self.get_revenue_metrics()
        health = self.get_system_health()
        
        # Create main table
        table = Table(title=f"🚀 Unified Donkey Betz Platform Monitor - {datetime.now().strftime('%H:%M:%S')}")
        table.add_column("System", style="cyan", width=20)
        table.add_column("Metric", style="magenta", width=30)
        table.add_column("Value", style="green", width=20)
        table.add_column("Status", style="yellow", width=15)
        
        # Agent metrics
        table.add_row(
            "🤖 AGENTS",
            "Total Active",
            str(agents.get('total', 0)),
            "✅ ONLINE" if agents.get('total', 0) > 0 else "⚠️ OFFLINE"
        )
        table.add_row(
            "",
            "Recent Executions (10min)",
            str(agents.get('recent_executions', 0)),
            f"{agents.get('active_rate', 0):.1f}% active"
        )
        table.add_row(
            "",
            "Collaboration Groups",
            str(len(agents.get('groups', {}))),
            "CONNECTED"
        )
        
        # Spider metrics
        table.add_row(
            "🕷️ SPIDERS",
            "Strategies Found",
            str(spiders.get('recent_strategies', 0)),
            spiders.get('harvest_rate', '0/hour')
        )
        table.add_row(
            "",
            "Projects Generated",
            str(spiders.get('recent_projects', 0)),
            "HARVESTING" if spiders.get('recent_strategies', 0) > 0 else "IDLE"
        )
        
        # Revenue metrics
        table.add_row(
            "💰 REVENUE",
            "Total Projects",
            str(revenue.get('total_projects', 0)),
            "GENERATING"
        )
        table.add_row(
            "",
            "Average Value",
            f"${revenue.get('avg_project_value', 0):,.0f}",
            f"{revenue.get('conversion_rate', 0)}% conv"
        )
        table.add_row(
            "",
            "Monthly Potential",
            f"${revenue.get('projected_monthly', 0):,.0f}",
            "📈 GROWING"
        )
        
        # System health
        table.add_row(
            "⚡ SYSTEM",
            "Database Size",
            f"{health.get('db_size_mb', 0)} MB",
            health.get('status', 'UNKNOWN')
        )
        table.add_row(
            "",
            "Embeddings",
            f"{health.get('embeddings', 0):,}",
            "INDEXED"
        )
        table.add_row(
            "",
            "Connections",
            str(health.get('connections', 0)),
            "STABLE" if health.get('connections', 0) < 20 else "BUSY"
        )
        
        return table
    
    async def run_monitor(self):
        """Run the live monitoring dashboard"""
        self.console.clear()
        self.console.print("[bold cyan]Starting System Monitor...[/bold cyan]")
        
        with Live(self.create_dashboard(), refresh_per_second=0.5) as live:
            while True:
                try:
                    # Update dashboard
                    live.update(self.create_dashboard())
                    
                    # Wait before next refresh
                    await asyncio.sleep(self.refresh_rate)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[bold red]Monitor stopped by user[/bold red]")
                    break
                except Exception as e:
                    self.console.print(f"[red]Error: {e}[/red]")
                    await asyncio.sleep(5)


def main():
    """Run the system monitor"""
    monitor = SystemMonitor()
    
    console.print("[bold green]="*60)
    console.print("🔍 UNIFIED DONKEY BETZ SYSTEM MONITOR")
    console.print("="*60)
    console.print("[cyan]Press Ctrl+C to stop monitoring[/cyan]\n")
    
    # Run the monitor
    asyncio.run(monitor.run_monitor())


if __name__ == "__main__":
    # Check if rich is installed
    try:
        from rich import console
    except ImportError:
        print("Installing required package: rich")
        os.system("pip install rich")
        print("Please run the script again")
        sys.exit(1)
    
    main()
