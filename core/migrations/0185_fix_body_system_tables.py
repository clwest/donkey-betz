# Generated for Session 807 - Fix Body System Tables (Conditional)
"""
Migration 0184 failed because some tables still existed while others didn't.
This migration uses IF NOT EXISTS to safely create only missing tables.

The issue: Migration 0183 deleted some tables but not all, leaving the database
in an inconsistent state. This migration fixes that by conditionally creating
each table only if it doesn't exist.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0184_restore_body_system_tables_v2'),
    ]

    operations = [
        # Skip this migration - the previous one partially succeeded
        # We need to handle this at the database level
        migrations.RunSQL(
            sql="""
            -- BRAIN SYSTEM
            CREATE TABLE IF NOT EXISTS core_cognitive_channel (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) UNIQUE NOT NULL,
                display_name VARCHAR(150) DEFAULT '',
                channel_type VARCHAR(20) NOT NULL,
                provider VARCHAR(30) DEFAULT '',
                model_name VARCHAR(100) DEFAULT '',
                description TEXT DEFAULT '',
                max_latency_ms INTEGER DEFAULT 30000,
                target_success_rate FLOAT DEFAULT 95.0,
                max_concurrent INTEGER DEFAULT 10,
                max_tokens_per_min INTEGER DEFAULT 100000,
                is_active BOOLEAN DEFAULT TRUE,
                is_critical BOOLEAN DEFAULT FALSE,
                is_builtin BOOLEAN DEFAULT FALSE,
                total_calls BIGINT DEFAULT 0,
                total_tokens BIGINT DEFAULT 0,
                total_errors BIGINT DEFAULT 0,
                last_activity TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS core_brain_pulse (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                overall_status VARCHAR(20) DEFAULT 'focused',
                cognitive_score FLOAT DEFAULT 100.0,
                is_thinking BOOLEAN DEFAULT TRUE,
                llm_calls_24h INTEGER DEFAULT 0,
                llm_success_rate FLOAT DEFAULT 100.0,
                llm_avg_latency_ms FLOAT DEFAULT 0,
                llm_errors_24h INTEGER DEFAULT 0,
                llm_timeouts_24h INTEGER DEFAULT 0,
                tokens_input_24h BIGINT DEFAULT 0,
                tokens_output_24h BIGINT DEFAULT 0,
                tokens_total_24h BIGINT DEFAULT 0,
                active_conversations INTEGER DEFAULT 0,
                conversations_24h INTEGER DEFAULT 0,
                avg_conversation_turns FLOAT DEFAULT 0,
                conversation_success_rate FLOAT DEFAULT 100.0,
                rag_queries_24h INTEGER DEFAULT 0,
                rag_avg_latency_ms FLOAT DEFAULT 0,
                embedding_lookups_24h INTEGER DEFAULT 0,
                memory_hit_rate FLOAT DEFAULT 0,
                agent_thoughts_24h INTEGER DEFAULT 0,
                agent_tool_calls_24h INTEGER DEFAULT 0,
                agent_tool_success_rate FLOAT DEFAULT 100.0,
                routing_decisions_24h INTEGER DEFAULT 0,
                fallback_count_24h INTEGER DEFAULT 0,
                primary_model_usage_pct FLOAT DEFAULT 100.0,
                provider_stats JSONB DEFAULT '{}',
                model_stats JSONB DEFAULT '{}',
                concurrent_tasks_peak INTEGER DEFAULT 0,
                queue_depth INTEGER DEFAULT 0,
                avg_think_time_ms FLOAT DEFAULT 0,
                thoughts_per_minute FLOAT DEFAULT 0,
                tokens_per_minute FLOAT DEFAULT 0,
                channels_checked INTEGER DEFAULT 0,
                channels_healthy INTEGER DEFAULT 0,
                channels_degraded INTEGER DEFAULT 0,
                channels_offline INTEGER DEFAULT 0,
                heart_connected BOOLEAN DEFAULT FALSE,
                lungs_connected BOOLEAN DEFAULT FALSE,
                cognitive_issues JSONB DEFAULT '[]',
                check_duration_ms INTEGER DEFAULT 0,
                recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS core_cognitive_status (
                channel_id UUID PRIMARY KEY REFERENCES core_cognitive_channel(id) ON DELETE CASCADE,
                status VARCHAR(20) DEFAULT 'focused',
                is_healthy BOOLEAN DEFAULT TRUE,
                current_latency_ms FLOAT DEFAULT 0,
                current_concurrent INTEGER DEFAULT 0,
                current_queue_depth INTEGER DEFAULT 0,
                calls_24h INTEGER DEFAULT 0,
                tokens_24h BIGINT DEFAULT 0,
                errors_24h INTEGER DEFAULT 0,
                success_rate_24h FLOAT DEFAULT 100.0,
                avg_latency_24h FLOAT DEFAULT 0,
                throughput_per_min FLOAT DEFAULT 0,
                tokens_per_min FLOAT DEFAULT 0,
                last_call TIMESTAMP WITH TIME ZONE,
                last_success TIMESTAMP WITH TIME ZONE,
                last_error TIMESTAMP WITH TIME ZONE,
                last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                warning_alert_sent BOOLEAN DEFAULT FALSE,
                critical_alert_sent BOOLEAN DEFAULT FALSE,
                last_alert_at TIMESTAMP WITH TIME ZONE,
                last_error_message TEXT DEFAULT ''
            );

            -- SKIN SYSTEM
            CREATE TABLE IF NOT EXISTS core_skin_pulses (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                status VARCHAR(20) DEFAULT 'healthy',
                health_score FLOAT DEFAULT 100.0,
                total_workspaces INTEGER DEFAULT 0,
                active_workspaces INTEGER DEFAULT 0,
                workspaces_with_errors INTEGER DEFAULT 0,
                operations_24h INTEGER DEFAULT 0,
                successful_operations_24h INTEGER DEFAULT 0,
                failed_operations_24h INTEGER DEFAULT 0,
                success_rate_24h FLOAT DEFAULT 100.0,
                files_created_24h INTEGER DEFAULT 0,
                files_modified_24h INTEGER DEFAULT 0,
                files_deleted_24h INTEGER DEFAULT 0,
                bytes_written_24h BIGINT DEFAULT 0,
                rollbacks_available INTEGER DEFAULT 0,
                active_agents INTEGER DEFAULT 0,
                recent_errors JSONB DEFAULT '[]',
                check_duration_ms INTEGER DEFAULT 0,
                recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS core_skin_status (
                id INTEGER PRIMARY KEY DEFAULT 1,
                status VARCHAR(20) DEFAULT 'healthy',
                is_healthy BOOLEAN DEFAULT TRUE,
                health_score FLOAT DEFAULT 100.0,
                total_workspaces INTEGER DEFAULT 0,
                active_workspaces INTEGER DEFAULT 0,
                operations_24h INTEGER DEFAULT 0,
                success_rate_24h FLOAT DEFAULT 100.0,
                files_touched_24h INTEGER DEFAULT 0,
                bytes_written_24h BIGINT DEFAULT 0,
                activity_level VARCHAR(20) DEFAULT 'normal',
                rollbacks_available INTEGER DEFAULT 0,
                last_operation_at TIMESTAMP WITH TIME ZONE,
                last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            -- NERVOUS SYSTEM
            CREATE TABLE IF NOT EXISTS core_nervous_pulses (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                status VARCHAR(20) DEFAULT 'calm',
                health_score FLOAT DEFAULT 100.0,
                websocket_connections INTEGER DEFAULT 0,
                api_latency_ms FLOAT DEFAULT 0,
                events_processed_24h INTEGER DEFAULT 0,
                errors_24h INTEGER DEFAULT 0,
                check_duration_ms INTEGER DEFAULT 0,
                recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS core_nervous_status (
                id INTEGER PRIMARY KEY DEFAULT 1,
                status VARCHAR(20) DEFAULT 'calm',
                is_healthy BOOLEAN DEFAULT TRUE,
                health_score FLOAT DEFAULT 100.0,
                websocket_connections INTEGER DEFAULT 0,
                api_latency_ms FLOAT DEFAULT 0,
                events_processed_24h INTEGER DEFAULT 0,
                last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS core_websocket_connection_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                channel_name VARCHAR(255) NOT NULL,
                connection_type VARCHAR(50) NOT NULL,
                user_id INTEGER,
                connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                disconnected_at TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT TRUE
            );

            -- Create indexes if they don't exist
            CREATE INDEX IF NOT EXISTS core_brain__recorde_idx ON core_brain_pulse (recorded_at DESC);
            CREATE INDEX IF NOT EXISTS core_brain__status_idx ON core_brain_pulse (overall_status, recorded_at DESC);
            """,
            reverse_sql="""
            -- Reverse is a no-op since we're using IF NOT EXISTS
            -- Tables should persist
            """
        ),
    ]
