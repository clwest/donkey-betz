#!/usr/bin/env python3
"""
🔍 REAL-TIME SYSTEM MONITOR - WORKING VERSION
Fixed to show actual data and handle timezones correctly
"""

import os
import sys
import django
import asyncio
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.live import Live
from django.utils import timezone

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.db import connection
from django.db.models import Count, Sum, Avg
from agents.models import UnifiedAgentTemplate, AgentExecution
from django.contrib.auth import get_user_model


class SystemMonitor:
    """Real-time monitoring of the platform"""
    
    def __init__(self):
        self.console = Console(width=120)
        self.refresh_rate = 2  # seconds
        
    def get_agent_activity(self) -> dict:
        """Get current agent activity metrics"""
        try:
            # Total active agents - THIS WORKS
            total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            
            # Get executions from different time periods (using timezone-aware datetime)
            now = timezone.now()
            recent_10min = AgentExecution.objects.filter(
                created_at__gte=now - timedelta(minutes=10)
            ).count()
            recent_hour = AgentExecution.objects.filter(
                created_at__gte=now - timedelta(hours=1)
            ).count()
            recent_day = AgentExecution.objects.filter(
                created_at__gte=now - timedelta(days=1)
            ).count()
            total_executions = AgentExecution.objects.count()
            
            # Get agent groups - THIS WORKS
            groups = {}
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
            
            # Get last execution time
            last_exec = AgentExecution.objects.order_by('-created_at').first()
            last_exec_time = last_exec.created_at if last_exec else None
            
            return {
                'total': total_agents,
                'recent_10min': recent_10min,
                'recent_hour': recent_hour,
                'recent_day': recent_day,
                'total_executions': total_executions,
                'groups': groups,
                'last_execution': last_exec_time,
                'active_rate': (recent_day / total_agents * 100) if total_agents > 0 else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_health(self) -> dict:
        """Get overall system health metrics"""
        try:
            with connection.cursor() as cursor:
                # Database size - THIS WORKS
                cursor.execute("""
                    SELECT pg_database_size(current_database()) / 1024 / 1024 as size_mb
                """)
                db_size = cursor.fetchone()[0]
                
                # Table count
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                
                # Active connections
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_stat_activity 
                    WHERE state = 'active'
                """)
                connections = cursor.fetchone()[0]
                
                # Embeddings count
                try:
                    cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
                    embeddings = cursor.fetchone()[0]
                except:
                    embeddings = 0
            
            return {
                'db_size_mb': round(db_size, 2),
                'table_count': table_count,
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
        health = self.get_system_health()
        
        # Create main table
        table = Table(
            title=f"🚀 Unified Donkey Betz Platform Monitor - {datetime.now().strftime('%H:%M:%S')}",
            width=110,
            show_header=True,
            header_style="bold magenta"
        )
        
        # Add columns
        table.add_column("System", style="cyan", width=20)
        table.add_column("Metric", style="magenta", width=30)
        table.add_column("Value", style="green", width=25)
        table.add_column("Status", style="yellow", width=25)
        
        # Agent metrics
        table.add_row(
            "🤖 AGENTS",
            "Total Active",
            str(agents.get('total', 0)),
            "✅ READY" if agents.get('total', 0) > 0 else "⚠️ NO AGENTS"
        )
        
        # Agent groups
        groups = agents.get('groups', {})
        if groups:
            top_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)[:3]
            groups_str = ", ".join([f"{g[0]}({g[1]})" for g in top_groups])
            table.add_row("", "Agent Groups", groups_str[:25], f"{len(groups)} groups")
        
        # Execution metrics - show different time ranges
        table.add_row(
            "",
            "Executions (Last 10min)",
            str(agents.get('recent_10min', 0)),
            "⚡ ACTIVE" if agents.get('recent_10min', 0) > 0 else "💤 IDLE"
        )
        table.add_row(
            "",
            "Executions (Last Hour)",
            str(agents.get('recent_hour', 0)),
            f"{agents.get('recent_hour', 0) * 60 // 60}/hour rate"
        )
        table.add_row(
            "",
            "Executions (Last 24h)",
            str(agents.get('recent_day', 0)),
            f"{agents.get('active_rate', 0):.1f}% daily activity"
        )
        table.add_row(
            "",
            "Total Executions",
            str(agents.get('total_executions', 0)),
            "ALL TIME"
        )
        
        # Last execution time
        last_exec = agents.get('last_execution')
        if last_exec:
            time_since = timezone.now() - last_exec
            if time_since.days > 0:
                time_str = f"{time_since.days}d ago"
            elif time_since.seconds > 3600:
                time_str = f"{time_since.seconds // 3600}h ago"
            else:
                time_str = f"{time_since.seconds // 60}m ago"
            table.add_row("", "Last Execution", time_str, last_exec.strftime("%Y-%m-%d %H:%M"))
        
        # System health
        table.add_row(
            "⚡ SYSTEM",
            "Database Size",
            f"{health.get('db_size_mb', 0)} MB",
            health.get('status', 'UNKNOWN')
        )
        table.add_row(
            "",
            "Total Tables",
            str(health.get('table_count', 0)),
            "PostgreSQL"
        )
        table.add_row(
            "",
            "DB Connections",
            str(health.get('connections', 0)),
            "✅ STABLE" if health.get('connections', 0) < 50 else "⚠️ HIGH"
        )
        table.add_row(
            "",
            "Embeddings",
            str(health.get('embeddings', 0)),
            "INDEXED" if health.get('embeddings', 0) > 0 else "EMPTY"
        )
        
        return table
    
    async def run_monitor(self):
        """Run the live monitoring dashboard"""
        self.console.clear()
        self.console.print("[bold cyan]Starting System Monitor...[/bold cyan]")
        
        with Live(
            self.create_dashboard(), 
            refresh_per_second=0.5, 
            console=self.console,
            transient=False
        ) as live:
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
    
    console = Console(width=120)
    
    console.print("[bold green]" + "="*60)
    console.print("🔍 UNIFIED DONKEY BETZ SYSTEM MONITOR")
    console.print("="*60)
    console.print("[cyan]Press Ctrl+C to stop monitoring[/cyan]\n")
    
    # Run the monitor
    asyncio.run(monitor.run_monitor())


if __name__ == "__main__":
    main()
