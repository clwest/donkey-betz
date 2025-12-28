"""
Monitor Spider Army Management Command
=====================================

Django management command to monitor the spider army performance,
health, and intelligence flow in real-time.
"""

import time
import json
from datetime import datetime, timezone
from django.core.management.base import BaseCommand, CommandError
import redis


class Command(BaseCommand):
    help = 'Monitor Spider Army performance and health'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Monitoring interval in seconds (default: 30)'
        )

        parser.add_argument(
            '--redis-host',
            type=str,
            default='localhost',
            help='Redis host'
        )

        parser.add_argument(
            '--redis-port',
            type=int,
            default=6379,
            help='Redis port'
        )

        parser.add_argument(
            '--format',
            type=str,
            choices=['table', 'json', 'detailed'],
            default='table',
            help='Output format'
        )

        parser.add_argument(
            '--alerts-only',
            action='store_true',
            help='Show only alerts and critical issues'
        )

        parser.add_argument(
            '--one-shot',
            action='store_true',
            help='Run once and exit (no continuous monitoring)'
        )

    def handle(self, *args, **options):
        """Handle the monitoring command"""

        # Redis connection
        redis_config = {
            'host': options['redis_host'],
            'port': options['redis_port'],
            'db': 0
        }

        try:
            redis_client = redis.Redis(**redis_config)
            redis_client.ping()  # Test connection

        except redis.ConnectionError:
            raise CommandError(f"Cannot connect to Redis at {options['redis_host']}:{options['redis_port']}")

        self.stdout.write(
            self.style.SUCCESS('🕷️ SPIDER ARMY MONITORING DASHBOARD 🕷️')
        )

        if options['one_shot']:
            self._monitor_once(redis_client, options)
        else:
            self._monitor_continuous(redis_client, options)

    def _monitor_once(self, redis_client, options):
        """Run monitoring once and exit"""
        data = self._collect_monitoring_data(redis_client)
        self._display_data(data, options)

    def _monitor_continuous(self, redis_client, options):
        """Run continuous monitoring"""
        interval = options['interval']

        try:
            while True:
                # Clear screen for continuous monitoring
                if not options['alerts_only']:
                    self.stdout.write('\033[2J\033[H')  # Clear screen and move cursor to top

                # Collect and display data
                data = self._collect_monitoring_data(redis_client)
                self._display_data(data, options)

                # Wait for next update
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Monitoring stopped by user')
            )

    def _collect_monitoring_data(self, redis_client):
        """Collect monitoring data from Redis"""
        try:
            data = {
                'timestamp': datetime.now(timezone.utc),
                'army_status': None,
                'pipeline_metrics': None,
                'pipeline_health': None,
                'command_center_alerts': None,
                'spider_health': None,
                'system_resources': None,
                'intelligence_flow': None
            }

            # Get army status (from orchestrator)
            army_status_key = 'spider_army:status'
            army_data = redis_client.get(army_status_key)
            if army_data:
                data['army_status'] = json.loads(army_data)

            # Get pipeline metrics
            pipeline_metrics_key = 'pipeline:metrics'
            pipeline_data = redis_client.get(pipeline_metrics_key)
            if pipeline_data:
                data['pipeline_metrics'] = json.loads(pipeline_data)

            # Get pipeline health
            pipeline_health_key = 'pipeline:health'
            health_data = redis_client.get(pipeline_health_key)
            if health_data:
                data['pipeline_health'] = json.loads(health_data)

            # Get command center alerts
            alerts_key = 'command_center:alerts'
            alerts_data = redis_client.lrange(alerts_key, 0, 10)  # Last 10 alerts
            if alerts_data:
                data['command_center_alerts'] = [json.loads(alert) for alert in alerts_data]

            # Get spider health
            spider_health_key = 'command_center:spider_health'
            spider_health_data = redis_client.get(spider_health_key)
            if spider_health_data:
                data['spider_health'] = json.loads(spider_health_data)

            # Get system resources
            system_resources_key = 'command_center:system_resources'
            resources_data = redis_client.get(system_resources_key)
            if resources_data:
                data['system_resources'] = json.loads(resources_data)

            # Get intelligence flow
            intelligence_flow_key = 'command_center:intelligence_flow'
            flow_data = redis_client.get(intelligence_flow_key)
            if flow_data:
                data['intelligence_flow'] = json.loads(flow_data)

            return data

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error collecting monitoring data: {e}')
            )
            return {}

    def _display_data(self, data, options):
        """Display monitoring data based on format"""
        if not data:
            self.stdout.write(self.style.ERROR('No monitoring data available'))
            return

        output_format = options['format']
        alerts_only = options['alerts_only']

        if output_format == 'json':
            self._display_json_format(data)
        elif output_format == 'detailed':
            self._display_detailed_format(data, alerts_only)
        else:  # table format
            self._display_table_format(data, alerts_only)

    def _display_table_format(self, data, alerts_only):
        """Display data in table format"""
        timestamp = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')

        if not alerts_only:
            self.stdout.write(f'📊 Spider Army Status - {timestamp}')
            self.stdout.write('=' * 80)

            # Army Overview
            army_status = data.get('army_status', {})
            if army_status:
                army_stats = army_status.get('army_stats', {})
                self.stdout.write('🕷️ SPIDER ARMY OVERVIEW')
                self.stdout.write('-' * 40)
                self.stdout.write(f'Total Spiders:     {army_stats.get("total_spiders", 0):,}')
                self.stdout.write(f'Active Spiders:    {army_stats.get("active_spiders", 0):,}')
                self.stdout.write(f'Data Points:       {army_stats.get("total_data_points", 0):,}')
                self.stdout.write(f'Avg Quality:       {army_stats.get("avg_quality_score", 0.0):.2f}')
                self.stdout.write(f'Uptime:           {army_stats.get("uptime_percentage", 0.0):.1f}%')
                self.stdout.write('')

            # Pipeline Metrics
            pipeline_metrics = data.get('pipeline_metrics', {})
            if pipeline_metrics:
                self.stdout.write('🔄 DATA PIPELINE METRICS')
                self.stdout.write('-' * 40)
                self.stdout.write(f'Messages Processed: {pipeline_metrics.get("messages_processed", 0):,}')
                self.stdout.write(f'Messages Routed:   {pipeline_metrics.get("messages_routed", 0):,}')
                self.stdout.write(f'Messages Filtered: {pipeline_metrics.get("messages_filtered", 0):,}')
                self.stdout.write(f'Throughput/sec:    {pipeline_metrics.get("throughput_per_second", 0.0):.1f}')
                self.stdout.write(f'Avg Latency:       {pipeline_metrics.get("avg_latency_ms", 0.0):.1f}ms')
                self.stdout.write(f'Active Channels:   {pipeline_metrics.get("active_channels", 0)}')
                self.stdout.write('')

            # System Resources
            system_resources = data.get('system_resources', {})
            if system_resources:
                self.stdout.write('💻 SYSTEM RESOURCES')
                self.stdout.write('-' * 40)
                cpu_percent = system_resources.get('cpu_percent', 0)
                memory_percent = system_resources.get('memory_percent', 0)
                disk_percent = system_resources.get('disk_percent', 0)

                cpu_style = self._get_resource_style(cpu_percent)
                memory_style = self._get_resource_style(memory_percent)
                disk_style = self._get_resource_style(disk_percent)

                self.stdout.write(f'CPU Usage:         {cpu_style(f"{cpu_percent:.1f}%")}')
                self.stdout.write(f'Memory Usage:      {memory_style(f"{memory_percent:.1f}%")}')
                self.stdout.write(f'Disk Usage:        {disk_style(f"{disk_percent:.1f}%")}')
                self.stdout.write('')

        # Always show alerts (even in alerts-only mode)
        alerts = data.get('command_center_alerts', [])
        if alerts:
            self.stdout.write('🚨 ACTIVE ALERTS')
            self.stdout.write('-' * 40)

            for alert in alerts:
                severity = alert.get('severity', 'low')
                message = alert.get('message', 'Unknown alert')
                timestamp = alert.get('timestamp', '')

                # Style based on severity
                if severity == 'high':
                    alert_style = self.style.ERROR
                elif severity == 'medium':
                    alert_style = self.style.WARNING
                else:
                    alert_style = self.style.NOTICE

                self.stdout.write(f'  {alert_style(severity.upper())}: {message}')

            self.stdout.write('')

        # Spider Health Summary
        spider_health = data.get('spider_health', {})
        if spider_health and not alerts_only:
            unhealthy_count = len(spider_health.get('unhealthy_spiders', []))
            total_spiders = spider_health.get('total_spiders', 0)
            health_score = spider_health.get('health_score', 100)

            self.stdout.write('🏥 SPIDER HEALTH')
            self.stdout.write('-' * 40)
            self.stdout.write(f'Health Score:      {self._get_health_style(health_score)(f"{health_score:.1f}%")}')
            self.stdout.write(f'Healthy Spiders:   {total_spiders - unhealthy_count:,}')

            if unhealthy_count > 0:
                self.stdout.write(f'Unhealthy Spiders: {self.style.WARNING(str(unhealthy_count))}')

        if not alerts_only:
            self.stdout.write('')

    def _display_detailed_format(self, data, alerts_only):
        """Display data in detailed format"""
        self.stdout.write(json.dumps(data, indent=2, default=str))

    def _display_json_format(self, data):
        """Display data in JSON format"""
        # Convert datetime objects to strings for JSON serialization
        json_data = self._convert_datetime_to_string(data)
        self.stdout.write(json.dumps(json_data, indent=2))

    def _convert_datetime_to_string(self, obj):
        """Recursively convert datetime objects to strings"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._convert_datetime_to_string(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetime_to_string(item) for item in obj]
        else:
            return obj

    def _get_resource_style(self, percentage):
        """Get style based on resource usage percentage"""
        if percentage > 90:
            return self.style.ERROR
        elif percentage > 75:
            return self.style.WARNING
        elif percentage > 50:
            return self.style.NOTICE
        else:
            return self.style.SUCCESS

    def _get_health_style(self, health_score):
        """Get style based on health score"""
        if health_score < 70:
            return self.style.ERROR
        elif health_score < 85:
            return self.style.WARNING
        elif health_score < 95:
            return self.style.NOTICE
        else:
            return self.style.SUCCESS