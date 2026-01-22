"""
Session 562: Push Notifications for Arbitrage Alerts

Creates tables for:
- PushSubscription: Stores Web Push subscription data
- NotificationPreference: User preferences for notifications
- NotificationLog: History of sent notifications
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0126_session_561_odds_history'),
    ]

    operations = [
        # PushSubscription table
        migrations.CreateModel(
            name='PushSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.URLField(help_text='Push service endpoint URL', max_length=500, unique=True)),
                ('p256dh_key', models.CharField(help_text="Client's P-256 ECDH public key", max_length=200)),
                ('auth_key', models.CharField(help_text='Authentication secret', max_length=50)),
                ('browser', models.CharField(blank=True, default='', max_length=50)),
                ('device_type', models.CharField(blank=True, default='', max_length=20)),
                ('user_agent', models.TextField(blank=True, default='')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_used_at', models.DateTimeField(blank=True, null=True)),
                ('failed_count', models.IntegerField(default=0, help_text='Consecutive failed push attempts')),
                ('user', models.ForeignKey(
                    blank=True,
                    help_text='Associated user (null for anonymous subscriptions)',
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='push_subscriptions',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'db_table': 'push_subscriptions',
            },
        ),
        migrations.AddIndex(
            model_name='pushsubscription',
            index=models.Index(fields=['user', 'is_active'], name='push_subscr_user_id_7b8c3f_idx'),
        ),
        migrations.AddIndex(
            model_name='pushsubscription',
            index=models.Index(fields=['is_active', 'created_at'], name='push_subscr_is_acti_a1c2d3_idx'),
        ),

        # NotificationPreference table
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notifications_enabled', models.BooleanField(default=True)),
                ('arb_alerts_enabled', models.BooleanField(default=True)),
                ('arb_min_profit_pct', models.DecimalField(
                    decimal_places=2,
                    default=1.0,
                    help_text='Minimum profit % to trigger notification',
                    max_digits=4
                )),
                ('arb_sports', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='List of sports to alert on (empty = all)'
                )),
                ('line_movement_enabled', models.BooleanField(default=False)),
                ('line_movement_threshold', models.DecimalField(
                    decimal_places=1,
                    default=1.0,
                    help_text='Minimum point movement to trigger alert',
                    max_digits=3
                )),
                ('quiet_hours_enabled', models.BooleanField(default=False)),
                ('quiet_start_hour', models.IntegerField(default=22, help_text='Hour to start quiet time (0-23)')),
                ('quiet_end_hour', models.IntegerField(default=8, help_text='Hour to end quiet time (0-23)')),
                ('max_notifications_per_hour', models.IntegerField(default=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notification_preferences',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'db_table': 'notification_preferences',
            },
        ),

        # NotificationLog table
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(
                    choices=[
                        ('arb', 'Arbitrage Alert'),
                        ('line_move', 'Line Movement'),
                        ('game_start', 'Game Starting'),
                        ('bet_result', 'Bet Result'),
                        ('system', 'System Message'),
                    ],
                    max_length=20
                )),
                ('title', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('data', models.JSONField(blank=True, default=dict)),
                ('sent_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('delivered', models.BooleanField(default=True)),
                ('error_message', models.TextField(blank=True, default='')),
                ('subscription', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notification_logs',
                    to='core.pushsubscription'
                )),
            ],
            options={
                'db_table': 'notification_logs',
                'ordering': ['-sent_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notificationlog',
            index=models.Index(fields=['subscription', 'sent_at'], name='notificatio_subscri_e4f5g6_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationlog',
            index=models.Index(fields=['notification_type', 'sent_at'], name='notificatio_notific_h7i8j9_idx'),
        ),
    ]
