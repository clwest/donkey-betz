#!/usr/bin/env python3
"""
🔍 REAL-TIME SYSTEM MONITOR (FIXED FOR YOUR SCHEMA)
Track the activity of your activated agents and system health
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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.db import connection
from django.db.models import Count, Sum, Avg
from agents.models import UnifiedAgentTemplate, AgentExecution
from django.contrib.auth import get_user_model

console = Console()


class SystemMonitor:
    """Real-time monitoring of the activated platform"""
    
    def __init__(self):
        self.console = Console(width=120)  # Set fixed width for consistency
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
            
            # Get total executions
            total_executions = AgentExecution.objects.count()
            
            # Get agent specializations
            specializations = UnifiedAgentTemplate.objects.values('specialization').annotate(
                count=Count('specialization')
            ).order_by('-count')[:5]
            
            return {
                'total': total_agents,
                'recent_executions': recent_executions,
                'total_executions': total_executions,
                'specializations': dict(specializations.values_list('specialization', 'count')),
                'active_rate': (recent_executions / total_agents * 100) if total_agents > 0 else 0
            }
        except Exception as e:
            return {'total': 0, 'recent_executions': 0, 'total_executions': 0, 'specializations': {}, 'active_rate': 0, 'error': str(e)}
    
    def get_income_activity(self) -> Dict:
        """Get income generation metrics from available tables"""
        try:
            with connection.cursor() as cursor:
                # Check what tables we actually have
                income_data = {
                    'opportunities': 0,
                    'revenue_streams': 0,
                    'total_value': 0
                }
                
                # Try different table names that might exist
                tables_to_try = [
                    ('backend_incomebuilderanalysis', 'income_analyses'),
                    ('income_opportunityanalysis', 'opportunities'),
                    ('backend_opportunityscan', 'scans'),
                    ('revenue_revenuestream', 'streams')
                ]
                
                for table_name, label in tables_to_try:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        income_data[label] = count
                    except:
                        pass
                
                return income_data
        except Exception as e:
            return {'opportunities': 0, 'revenue_streams': 0, 'total_value': 0, 'error': str(e)}
    
    def get_system_health(self) -> Dict:
        """Get overall system health metrics"""
        try:
            with connection.cursor() as cursor:
                # Database size
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
                
                # Check embeddings
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
            return {'db_size_mb': 0, 'table_count': 0, 'embeddings': 0, 'connections': 0, 'status': 'UNKNOWN', 'error': str(e)}
    
    def create_dashboard(self) -> Table:
        """Create the monitoring dashboard"""
        # Get all metrics
        agents = self.get_agent_activity()
        income = self.get_income_activity()
        health = self.get_system_health()
        
        # Create main table with fixed widths
        table = Table(
            title=f"🚀 Unified Donkey Betz Platform Monitor - {datetime.now().strftime('%H:%M:%S')}",
            width=110,
            show_header=True,
            header_style="bold magenta"
        )
        
        # Add columns with specific widths
        table.add_column("System", style="cyan", width=18)
        table.add_column("Metric", style="magenta", width=30)
        table.add_column("Value", style="green", width=20)
        table.add_column("Status", style="yellow", width=18)
        
        # Agent metrics
        table.add_row(
            "🤖 AGENTS",
            "Total Active",
            str(agents.get('total', 0)),
            "✅ ACTIVE" if agents.get('total', 0) > 0 else "⚠️ NO AGENTS"
        )
        table.add_row(
            "",
            "Recent Executions (10min)",
            str(agents.get('recent_executions', 0)),
            f"{agents.get('active_rate', 0):.1f}% activity"
        )
        table.add_row(
            "",
            "Total Executions",
            str(agents.get('total_executions', 0)),
            "ALL TIME"
        )
        
        # Add top specializations
        specs = agents.get('specializations', {})
        if specs:
            top_spec = list(specs.keys())[0] if specs else "None"
            table.add_row(
                "",
                "Top Specialization",
                top_spec[:20],
                f"{specs.get(top_spec, 0)} agents"
            )
        
        # Income/Revenue metrics (using whatever tables exist)
        table.add_row(
            "💰 INCOME",
            "Opportunities",
            str(income.get('opportunities', 0)),
            "SCANNING"
        )
        table.add_row(
            "",
            "Revenue Streams", 
            str(income.get('revenue_streams', 0)),
            "TRACKING"
        )
        table.add_row(
            "",
            "Analyses/Scans",
            str(income.get('income_analyses', 0) + income.get('scans', 0)),
            "PROCESSING"
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
            "Total Tables",
            str(health.get('table_count', 0)),
            "SCHEMA"
        )
        table.add_row(
            "",
            "Embeddings",
            str(health.get('embeddings', 0)),
            "INDEXED" if health.get('embeddings', 0) > 0 else "EMPTY"
        )
        table.add_row(
            "",
            "DB Connections",
            str(health.get('connections', 0)),
            "STABLE" if health.get('connections', 0) < 50 else "HIGH"
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
    
    # Create a console instance with fixed width
    console = Console(width=120)
    
    console.print("[bold green]" + "="*60)
    console.print("🔍 UNIFIED DONKEY BETZ SYSTEM MONITOR")
    console.print("="*60)
    console.print("[cyan]Press Ctrl+C to stop monitoring[/cyan]\n")
    
    # Run the monitor
    asyncio.run(monitor.run_monitor())


if __name__ == "__main__":
    # Check if rich is installed
    try:
        from rich.console import Console
    except ImportError:
        print("Installing required package: rich")
        os.system("pip install rich")
        print("Please run the script again")
        sys.exit(1)
    
    main()
