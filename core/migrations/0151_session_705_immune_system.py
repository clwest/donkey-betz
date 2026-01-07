"""
Session 705: IMMUNE SYSTEM Migration

Creates tables for the IMMUNE SYSTEM - Security & Threat Detection:
- ThreatPattern: Known threat signatures
- ThreatEvent: Individual threat detections
- ImmuneResponse: Actions taken in response
- Quarantine: Blocked entities
- ImmuneStatus: Current immune health

Also creates 15 default threat patterns covering common security threats.
"""

import uuid
from django.db import migrations, models
import django.db.models.deletion


def create_default_patterns(apps, schema_editor):
    """Create default threat detection patterns."""
    ThreatPattern = apps.get_model('core', 'ThreatPattern')

    default_patterns = [
        # Rate Limit Abuse
        {
            'name': 'rate_limit_burst',
            'display_name': 'Rate Limit Burst Attack',
            'category': 'rate_abuse',
            'severity': 'high',
            'detection_type': 'threshold',
            'pattern': '{"type": "request_count", "scope": "ip"}',
            'description': 'Excessive requests from single IP in short time window',
            'threshold_count': 100,
            'threshold_window_seconds': 60,
            'auto_respond': True,
            'response_action': 'rate_limit',
            'block_duration_minutes': 15,
            'is_builtin': True,
        },
        {
            'name': 'rate_limit_sustained',
            'display_name': 'Sustained High Rate',
            'category': 'rate_abuse',
            'severity': 'medium',
            'detection_type': 'threshold',
            'pattern': '{"type": "request_count", "scope": "ip"}',
            'description': 'Sustained high request rate over longer period',
            'threshold_count': 500,
            'threshold_window_seconds': 300,
            'auto_respond': True,
            'response_action': 'rate_limit',
            'block_duration_minutes': 30,
            'is_builtin': True,
        },

        # Authentication Attacks
        {
            'name': 'brute_force_login',
            'display_name': 'Brute Force Login Attempt',
            'category': 'auth_attack',
            'severity': 'high',
            'detection_type': 'threshold',
            'pattern': '{"type": "failed_auth", "scope": "ip"}',
            'description': 'Multiple failed login attempts from same IP',
            'threshold_count': 5,
            'threshold_window_seconds': 300,
            'auto_respond': True,
            'response_action': 'block_temp',
            'block_duration_minutes': 60,
            'is_builtin': True,
        },
        {
            'name': 'credential_stuffing',
            'display_name': 'Credential Stuffing Attack',
            'category': 'auth_attack',
            'severity': 'critical',
            'detection_type': 'behavioral',
            'pattern': '{"type": "auth_pattern", "indicators": ["multiple_users", "same_ip", "sequential"]}',
            'description': 'Attempting logins with multiple usernames from same IP',
            'threshold_count': 10,
            'threshold_window_seconds': 600,
            'auto_respond': True,
            'response_action': 'block_perm',
            'is_builtin': True,
        },

        # Injection Attacks
        {
            'name': 'sql_injection',
            'display_name': 'SQL Injection Attempt',
            'category': 'injection',
            'severity': 'critical',
            'detection_type': 'signature',
            'pattern': r"(?i)(union\s+select|select\s+\*|drop\s+table|insert\s+into|delete\s+from|update\s+.*set|'--|\bor\b\s+1\s*=\s*1)",
            'description': 'SQL injection patterns in request parameters',
            'auto_respond': True,
            'response_action': 'block_temp',
            'block_duration_minutes': 1440,
            'is_builtin': True,
        },
        {
            'name': 'xss_attempt',
            'display_name': 'XSS Attempt',
            'category': 'injection',
            'severity': 'high',
            'detection_type': 'signature',
            'pattern': r"(?i)(<script|javascript:|onerror=|onload=|onclick=|<iframe|<object|<embed)",
            'description': 'Cross-site scripting patterns in input',
            'auto_respond': True,
            'response_action': 'block_temp',
            'block_duration_minutes': 60,
            'is_builtin': True,
        },
        {
            'name': 'path_traversal',
            'display_name': 'Path Traversal Attempt',
            'category': 'injection',
            'severity': 'high',
            'detection_type': 'signature',
            'pattern': r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.%2e/|%2e\./)",
            'description': 'Directory traversal patterns in paths',
            'auto_respond': True,
            'response_action': 'block_temp',
            'block_duration_minutes': 60,
            'is_builtin': True,
        },

        # Scraping/Bot Detection
        {
            'name': 'aggressive_scraping',
            'display_name': 'Aggressive Web Scraping',
            'category': 'scraping',
            'severity': 'medium',
            'detection_type': 'behavioral',
            'pattern': '{"type": "sequential_access", "indicators": ["no_js", "fast_pace", "full_coverage"]}',
            'description': 'Systematic scraping of content',
            'threshold_count': 50,
            'threshold_window_seconds': 60,
            'auto_respond': True,
            'response_action': 'rate_limit',
            'block_duration_minutes': 30,
            'is_builtin': True,
        },
        {
            'name': 'known_bot_ua',
            'display_name': 'Known Bad Bot User Agent',
            'category': 'bot',
            'severity': 'low',
            'detection_type': 'signature',
            'pattern': '(?i)(scrapy|curl|wget|python-requests|httpie|postman)',
            'description': 'Known automation tool user agents',
            'auto_respond': False,
            'response_action': 'log',
            'is_builtin': True,
        },

        # DoS Patterns
        {
            'name': 'connection_flood',
            'display_name': 'Connection Flood',
            'category': 'dos',
            'severity': 'critical',
            'detection_type': 'threshold',
            'pattern': '{"type": "connection_count", "scope": "ip"}',
            'description': 'Excessive concurrent connections from single IP',
            'threshold_count': 50,
            'threshold_window_seconds': 10,
            'auto_respond': True,
            'response_action': 'block_temp',
            'block_duration_minutes': 60,
            'is_builtin': True,
        },
        {
            'name': 'slow_loris',
            'display_name': 'Slow Loris Attack',
            'category': 'dos',
            'severity': 'high',
            'detection_type': 'behavioral',
            'pattern': '{"type": "slow_request", "indicators": ["incomplete_headers", "long_duration"]}',
            'description': 'Slow HTTP attack pattern',
            'auto_respond': True,
            'response_action': 'block_temp',
            'block_duration_minutes': 120,
            'is_builtin': True,
        },

        # Enumeration
        {
            'name': 'user_enumeration',
            'display_name': 'User Enumeration Attempt',
            'category': 'enumeration',
            'severity': 'medium',
            'detection_type': 'threshold',
            'pattern': '{"type": "user_lookup", "scope": "ip"}',
            'description': 'Attempting to enumerate valid usernames',
            'threshold_count': 20,
            'threshold_window_seconds': 300,
            'auto_respond': True,
            'response_action': 'rate_limit',
            'block_duration_minutes': 30,
            'is_builtin': True,
        },
        {
            'name': 'api_enumeration',
            'display_name': 'API Endpoint Enumeration',
            'category': 'enumeration',
            'severity': 'medium',
            'detection_type': 'behavioral',
            'pattern': '{"type": "404_rate", "indicators": ["sequential_paths", "common_wordlist"]}',
            'description': 'Scanning for API endpoints',
            'threshold_count': 30,
            'threshold_window_seconds': 60,
            'auto_respond': True,
            'response_action': 'block_temp',
            'block_duration_minutes': 60,
            'is_builtin': True,
        },

        # Anomaly Detection
        {
            'name': 'unusual_hours',
            'display_name': 'Unusual Activity Hours',
            'category': 'anomaly',
            'severity': 'low',
            'detection_type': 'anomaly',
            'pattern': '{"type": "time_anomaly", "baseline": "user_history"}',
            'description': 'Activity outside normal user patterns',
            'auto_respond': False,
            'response_action': 'log',
            'is_builtin': True,
        },
    ]

    for pattern_data in default_patterns:
        ThreatPattern.objects.create(**pattern_data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0150_session_704_spine_router'),
    ]

    operations = [
        # ThreatPattern - Known threat signatures
        migrations.CreateModel(
            name='ThreatPattern',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(blank=True, max_length=150)),
                ('category', models.CharField(choices=[
                    ('rate_abuse', 'Rate Limit Abuse'),
                    ('auth_attack', 'Authentication Attack'),
                    ('injection', 'Injection Attempt'),
                    ('scraping', 'Aggressive Scraping'),
                    ('dos', 'Denial of Service'),
                    ('enumeration', 'Resource Enumeration'),
                    ('privilege', 'Privilege Escalation'),
                    ('data_exfil', 'Data Exfiltration'),
                    ('bot', 'Bot/Automation'),
                    ('anomaly', 'Behavioral Anomaly'),
                    ('other', 'Other'),
                ], max_length=20)),
                ('severity', models.CharField(choices=[
                    ('critical', 'Critical'),
                    ('high', 'High'),
                    ('medium', 'Medium'),
                    ('low', 'Low'),
                    ('info', 'Informational'),
                ], default='medium', max_length=20)),
                ('detection_type', models.CharField(choices=[
                    ('signature', 'Signature Match'),
                    ('threshold', 'Threshold Exceeded'),
                    ('anomaly', 'Anomaly Detection'),
                    ('reputation', 'Reputation Based'),
                    ('behavioral', 'Behavioral'),
                ], default='signature', max_length=20)),
                ('pattern', models.TextField(help_text='Regex pattern, threshold config, or detection rules (JSON)')),
                ('description', models.TextField(blank=True)),
                ('threshold_count', models.IntegerField(default=0, help_text='Number of occurrences to trigger')),
                ('threshold_window_seconds', models.IntegerField(default=60, help_text='Time window for threshold')),
                ('auto_respond', models.BooleanField(default=True, help_text='Automatically respond to detections')),
                ('response_action', models.CharField(choices=[
                    ('log', 'Log Only'),
                    ('rate_limit', 'Rate Limit'),
                    ('block_temp', 'Temporary Block'),
                    ('block_perm', 'Permanent Block'),
                    ('quarantine', 'Quarantine'),
                    ('alert', 'Alert Only'),
                ], default='log', max_length=20)),
                ('block_duration_minutes', models.IntegerField(default=60, help_text='Duration for temporary blocks')),
                ('is_active', models.BooleanField(default=True)),
                ('is_builtin', models.BooleanField(default=False, help_text='System-defined pattern')),
                ('total_detections', models.BigIntegerField(default=0)),
                ('last_detection', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Threat Pattern',
                'verbose_name_plural': 'Threat Patterns',
                'db_table': 'core_threat_pattern',
                'ordering': ['severity', 'category', 'name'],
            },
        ),

        # ThreatEvent - Individual threat detections
        migrations.CreateModel(
            name='ThreatEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('detected', 'Detected'),
                    ('analyzing', 'Analyzing'),
                    ('responded', 'Responded'),
                    ('resolved', 'Resolved'),
                    ('false_positive', 'False Positive'),
                    ('escalated', 'Escalated'),
                ], default='detected', max_length=20)),
                ('severity', models.CharField(choices=[
                    ('critical', 'Critical'),
                    ('high', 'High'),
                    ('medium', 'Medium'),
                    ('low', 'Low'),
                    ('info', 'Informational'),
                ], max_length=20)),
                ('category', models.CharField(choices=[
                    ('rate_abuse', 'Rate Limit Abuse'),
                    ('auth_attack', 'Authentication Attack'),
                    ('injection', 'Injection Attempt'),
                    ('scraping', 'Aggressive Scraping'),
                    ('dos', 'Denial of Service'),
                    ('enumeration', 'Resource Enumeration'),
                    ('privilege', 'Privilege Escalation'),
                    ('data_exfil', 'Data Exfiltration'),
                    ('bot', 'Bot/Automation'),
                    ('anomaly', 'Behavioral Anomaly'),
                    ('other', 'Other'),
                ], max_length=20)),
                ('source_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('source_user_id', models.IntegerField(blank=True, null=True)),
                ('source_user_agent', models.TextField(blank=True)),
                ('source_path', models.CharField(blank=True, max_length=500)),
                ('source_method', models.CharField(blank=True, max_length=10)),
                ('detection_details', models.JSONField(default=dict, help_text='Details of what triggered detection')),
                ('confidence_score', models.FloatField(default=1.0, help_text='0-1 confidence in detection')),
                ('request_count', models.IntegerField(default=1, help_text='Number of requests in this event')),
                ('correlation_ids', models.JSONField(default=list, help_text='Related request correlation IDs')),
                ('response_taken', models.CharField(blank=True, max_length=20)),
                ('response_at', models.DateTimeField(blank=True, null=True)),
                ('detected_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('pattern', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='core.threatpattern')),
            ],
            options={
                'verbose_name': 'Threat Event',
                'verbose_name_plural': 'Threat Events',
                'db_table': 'core_threat_event',
                'ordering': ['-detected_at'],
            },
        ),

        # Indexes for ThreatEvent
        migrations.AddIndex(
            model_name='threatevent',
            index=models.Index(fields=['-detected_at'], name='core_threat_detecte_c8d7e6_idx'),
        ),
        migrations.AddIndex(
            model_name='threatevent',
            index=models.Index(fields=['status', '-detected_at'], name='core_threat_status_d9e8f7_idx'),
        ),
        migrations.AddIndex(
            model_name='threatevent',
            index=models.Index(fields=['severity', '-detected_at'], name='core_threat_severit_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='threatevent',
            index=models.Index(fields=['source_ip', '-detected_at'], name='core_threat_source__d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='threatevent',
            index=models.Index(fields=['category', '-detected_at'], name='core_threat_categor_g7h8i9_idx'),
        ),

        # ImmuneResponse - Actions taken
        migrations.CreateModel(
            name='ImmuneResponse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[
                    ('log', 'Logged'),
                    ('rate_limit', 'Rate Limited'),
                    ('block_temp', 'Temporarily Blocked'),
                    ('block_perm', 'Permanently Blocked'),
                    ('quarantine', 'Quarantined'),
                    ('alert_sent', 'Alert Sent'),
                    ('escalated', 'Escalated to Human'),
                    ('whitelisted', 'Whitelisted'),
                ], max_length=20)),
                ('is_automatic', models.BooleanField(default=True)),
                ('success', models.BooleanField(default=True)),
                ('target_type', models.CharField(choices=[
                    ('ip', 'IP Address'),
                    ('user', 'User Account'),
                    ('path', 'API Path'),
                    ('session', 'Session'),
                ], max_length=20)),
                ('target_value', models.CharField(max_length=200)),
                ('duration_minutes', models.IntegerField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('details', models.JSONField(default=dict)),
                ('responded_at', models.DateTimeField(auto_now_add=True)),
                ('responded_by', models.CharField(default='immune_system', max_length=100)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='core.threatevent')),
            ],
            options={
                'verbose_name': 'Immune Response',
                'verbose_name_plural': 'Immune Responses',
                'db_table': 'core_immune_response',
                'ordering': ['-responded_at'],
            },
        ),

        # Quarantine - Blocked entities
        migrations.CreateModel(
            name='Quarantine',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('entity_type', models.CharField(choices=[
                    ('ip', 'IP Address'),
                    ('ip_range', 'IP Range'),
                    ('user', 'User Account'),
                    ('user_agent', 'User Agent'),
                    ('path', 'API Path Pattern'),
                ], max_length=20)),
                ('entity_value', models.CharField(db_index=True, max_length=200)),
                ('reason', models.CharField(choices=[
                    ('rate_abuse', 'Rate Limit Abuse'),
                    ('auth_attack', 'Authentication Attack'),
                    ('injection', 'Injection Attempt'),
                    ('scraping', 'Aggressive Scraping'),
                    ('dos', 'Denial of Service'),
                    ('manual', 'Manual Block'),
                    ('reputation', 'Bad Reputation'),
                    ('other', 'Other'),
                ], max_length=20)),
                ('is_permanent', models.BooleanField(default=False)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('total_events', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('blocked_requests', models.BigIntegerField(default=0)),
                ('last_blocked_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='immune_system', max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('related_events', models.ManyToManyField(blank=True, related_name='quarantines', to='core.threatevent')),
            ],
            options={
                'verbose_name': 'Quarantine Entry',
                'verbose_name_plural': 'Quarantine Entries',
                'db_table': 'core_quarantine',
                'ordering': ['-created_at'],
                'unique_together': {('entity_type', 'entity_value')},
            },
        ),

        # Indexes for Quarantine
        migrations.AddIndex(
            model_name='quarantine',
            index=models.Index(fields=['entity_type', 'entity_value'], name='core_quaran_entity__j1k2l3_idx'),
        ),
        migrations.AddIndex(
            model_name='quarantine',
            index=models.Index(fields=['is_active', 'expires_at'], name='core_quaran_is_acti_m4n5o6_idx'),
        ),

        # ImmuneStatus - Current system health
        migrations.CreateModel(
            name='ImmuneStatus',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('healthy', 'Healthy'),
                    ('alert', 'Alert'),
                    ('fighting', 'Fighting'),
                    ('overwhelmed', 'Overwhelmed'),
                    ('compromised', 'Compromised'),
                ], default='healthy', max_length=20)),
                ('is_healthy', models.BooleanField(default=True)),
                ('health_score', models.FloatField(default=100.0, help_text='0-100% immune health')),
                ('threat_level', models.CharField(choices=[
                    ('none', 'None'),
                    ('low', 'Low'),
                    ('elevated', 'Elevated'),
                    ('high', 'High'),
                    ('severe', 'Severe'),
                ], default='none', max_length=20)),
                ('active_threats', models.IntegerField(default=0)),
                ('threats_detected_24h', models.IntegerField(default=0)),
                ('threats_blocked_24h', models.IntegerField(default=0)),
                ('false_positives_24h', models.IntegerField(default=0)),
                ('quarantined_ips', models.IntegerField(default=0)),
                ('quarantined_users', models.IntegerField(default=0)),
                ('total_quarantined', models.IntegerField(default=0)),
                ('active_patterns', models.IntegerField(default=0)),
                ('patterns_triggered_24h', models.IntegerField(default=0)),
                ('auto_responses_24h', models.IntegerField(default=0)),
                ('manual_responses_24h', models.IntegerField(default=0)),
                ('avg_response_time_ms', models.FloatField(default=0)),
                ('threats_by_category', models.JSONField(default=dict)),
                ('threats_by_severity', models.JSONField(default=dict)),
                ('spine_connected', models.BooleanField(default=False)),
                ('heart_connected', models.BooleanField(default=False)),
                ('last_scan', models.DateTimeField(auto_now=True)),
                ('last_threat', models.DateTimeField(blank=True, null=True)),
                ('status_changed_at', models.DateTimeField(blank=True, null=True)),
                ('alert_sent', models.BooleanField(default=False)),
                ('last_alert_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Immune Status',
                'verbose_name_plural': 'Immune Statuses',
                'db_table': 'core_immune_status',
            },
        ),

        # Create default threat patterns
        migrations.RunPython(create_default_patterns, migrations.RunPython.noop),
    ]
