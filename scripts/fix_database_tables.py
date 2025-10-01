#!/usr/bin/env python
"""
Intelligent Database Table Creation Script
Creates only the missing tables needed for Income Builder to work
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]


def get_existing_tables():
    """Get list of all existing intelligence_rt tables"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND (table_name LIKE 'intelligence_rt%%' OR table_name LIKE 'advisor%%')
            ORDER BY table_name;
        """)
        return [row[0] for row in cursor.fetchall()]


def create_missing_tables():
    """Create only the missing tables needed for Income Builder"""

    logger.info("🔍 Checking existing tables...")
    existing_tables = get_existing_tables()
    logger.info(f"Found {len(existing_tables)} existing tables: {existing_tables}")

    # Critical tables needed for Income Builder
    critical_tables = {
        'intelligence_rt_opportunitytracking': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_opportunitytracking (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                opportunity_id varchar(255) NOT NULL UNIQUE,
                title varchar(500) NOT NULL,
                description text NOT NULL,
                opportunity_type varchar(50) NOT NULL,
                stream_type varchar(50) NOT NULL,
                source_url text NOT NULL,
                source_platform varchar(100) NOT NULL,
                discovery_method varchar(100) NOT NULL,
                status varchar(20) NOT NULL DEFAULT 'new',
                confidence_score double precision NOT NULL DEFAULT 0,
                match_score double precision NOT NULL DEFAULT 0,
                potential_value numeric(12, 2) NOT NULL DEFAULT 0,
                time_to_income varchar(50) NOT NULL DEFAULT 'unknown',
                effort_level varchar(20) NOT NULL DEFAULT 'medium',
                requirements jsonb NOT NULL DEFAULT '{}',
                skills_required jsonb NOT NULL DEFAULT '[]',
                match_reasons jsonb NOT NULL DEFAULT '[]',
                discovered_at timestamp with time zone NOT NULL,
                expires_at timestamp with time zone NULL,
                applied_at timestamp with time zone NULL,
                responded_at timestamp with time zone NULL,
                converted_at timestamp with time zone NULL,
                user_id uuid NULL,
                spider_name varchar(100) NOT NULL,
                agent_analysis jsonb NOT NULL DEFAULT '{}',
                advisor_recommendations jsonb NOT NULL DEFAULT '[]',
                action_plan jsonb NOT NULL DEFAULT '{}',
                ml_features jsonb NOT NULL DEFAULT '{}'
            );
        """,
        'intelligence_rt_unifiedrevenuetracking': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_unifiedrevenuetracking (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                revenue_id varchar(255) NOT NULL UNIQUE,
                opportunity_type varchar(50) NOT NULL,
                stream_type varchar(50) NOT NULL,
                source varchar(100) NOT NULL,
                amount numeric(12, 2) NOT NULL,
                currency varchar(3) NOT NULL DEFAULT 'USD',
                status varchar(20) NOT NULL DEFAULT 'pending',
                earned_at timestamp with time zone NOT NULL,
                paid_at timestamp with time zone NULL,
                user_id uuid NULL,
                opportunity_id varchar(255) NULL,
                contributing_spiders jsonb NOT NULL DEFAULT '[]',
                contributing_agents jsonb NOT NULL DEFAULT '[]',
                contributing_advisors jsonb NOT NULL DEFAULT '[]',
                attribution_weights jsonb NOT NULL DEFAULT '{}',
                cross_domain_boost double precision NOT NULL DEFAULT 0,
                ml_prediction_accuracy double precision NULL,
                actual_vs_predicted jsonb NOT NULL DEFAULT '{}',
                payment_details jsonb NOT NULL DEFAULT '{}',
                transaction_id varchar(255) NOT NULL,
                notes text NOT NULL DEFAULT ''
            );
        """,
        'intelligence_rt_earningrecord': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_earningrecord (
                id bigint NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
                amount numeric(10, 2) NOT NULL,
                source varchar(100) NOT NULL,
                description text NOT NULL,
                earned_date date NOT NULL,
                paid_date date NULL,
                payment_method varchar(50) NOT NULL,
                status varchar(20) NOT NULL DEFAULT 'pending',
                transaction_id varchar(100) NOT NULL,
                tax_withheld numeric(10, 2) NOT NULL DEFAULT 0,
                net_amount numeric(10, 2) NOT NULL,
                created_at timestamp with time zone NOT NULL,
                opportunity_tracking_id uuid NULL
            );
        """,
        'intelligence_rt_userincomeprofile': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_userincomeprofile (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                monthly_income_goal numeric(10, 2) NOT NULL DEFAULT 0,
                current_monthly_income numeric(10, 2) NOT NULL DEFAULT 0,
                available_hours_per_week integer NOT NULL DEFAULT 20,
                preferred_work_times jsonb NOT NULL DEFAULT '{}',
                income_streams jsonb NOT NULL DEFAULT '[]',
                active_opportunities integer NOT NULL DEFAULT 0,
                total_opportunities_pursued integer NOT NULL DEFAULT 0,
                conversion_rate double precision NOT NULL DEFAULT 0,
                average_deal_size numeric(10, 2) NOT NULL DEFAULT 0,
                total_earnings numeric(12, 2) NOT NULL DEFAULT 0,
                earnings_this_month numeric(10, 2) NOT NULL DEFAULT 0,
                earnings_last_month numeric(10, 2) NOT NULL DEFAULT 0,
                ml_income_prediction jsonb NOT NULL DEFAULT '{}',
                user_id uuid NOT NULL UNIQUE
            );
        """,
        'intelligence_rt_spiderintelligencenode': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_spiderintelligencenode (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                spider_name varchar(100) NOT NULL UNIQUE,
                spider_type varchar(50) NOT NULL,
                data_category varchar(50) NOT NULL,
                last_execution timestamp with time zone NULL,
                next_scheduled_run timestamp with time zone NULL,
                execution_frequency_minutes integer NOT NULL DEFAULT 60,
                priority_level integer NOT NULL DEFAULT 5,
                is_enabled boolean NOT NULL DEFAULT true,
                total_data_points_collected integer NOT NULL DEFAULT 0,
                successful_distributions integer NOT NULL DEFAULT 0,
                failed_distributions integer NOT NULL DEFAULT 0,
                avg_data_quality_score double precision NOT NULL DEFAULT 0,
                last_data_payload jsonb NOT NULL DEFAULT '{}',
                error_log jsonb NOT NULL DEFAULT '[]',
                performance_metrics jsonb NOT NULL DEFAULT '{}'
            );
        """,
        'intelligence_rt_agentintelligencefeed': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_agentintelligencefeed (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                feed_id varchar(255) NOT NULL UNIQUE,
                agent_name varchar(100) NOT NULL,
                agent_type varchar(50) NOT NULL,
                data_received jsonb NOT NULL DEFAULT '{}',
                data_quality_score double precision NOT NULL DEFAULT 0,
                relevance_score double precision NOT NULL DEFAULT 0,
                action_taken varchar(255) NOT NULL,
                outcome jsonb NOT NULL DEFAULT '{}',
                revenue_generated numeric(12, 2) NOT NULL DEFAULT 0,
                spider_node_id uuid NULL
            );
        """,
        'intelligence_rt_advisorintelligencefeed': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_advisorintelligencefeed (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                feed_id varchar(255) NOT NULL UNIQUE,
                advisor_name varchar(100) NOT NULL,
                advisor_category varchar(50) NOT NULL,
                data_received jsonb NOT NULL DEFAULT '{}',
                data_quality_score double precision NOT NULL DEFAULT 0,
                relevance_score double precision NOT NULL DEFAULT 0,
                recommendation_generated text NOT NULL,
                confidence_level double precision NOT NULL DEFAULT 0,
                revenue_impact numeric(12, 2) NOT NULL DEFAULT 0,
                spider_node_id uuid NULL
            );
        """,
        'intelligence_rt_agentexecution': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_agentexecution (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                execution_id varchar(255) NOT NULL UNIQUE,
                agent_name varchar(100) NOT NULL,
                task_type varchar(100) NOT NULL,
                input_data jsonb NOT NULL DEFAULT '{}',
                output_data jsonb NOT NULL DEFAULT '{}',
                status varchar(20) NOT NULL DEFAULT 'pending',
                started_at timestamp with time zone NULL,
                completed_at timestamp with time zone NULL,
                execution_time_seconds double precision NULL,
                success boolean NULL,
                error_message text NOT NULL DEFAULT '',
                confidence_score double precision NULL,
                revenue_generated numeric(12, 2) NOT NULL DEFAULT 0,
                user_id uuid NULL
            );
        """,
        'intelligence_rt_opportunityactionplan': """
            CREATE TABLE IF NOT EXISTS intelligence_rt_opportunityactionplan (
                id uuid NOT NULL PRIMARY KEY,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{}',
                version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
                is_active boolean NOT NULL DEFAULT true,
                plan_id varchar(255) NOT NULL UNIQUE,
                title varchar(500) NOT NULL,
                description text NOT NULL,
                opportunity_type varchar(50) NOT NULL,
                steps jsonb NOT NULL DEFAULT '[]',
                timeline varchar(100) NOT NULL,
                estimated_time varchar(100) NOT NULL,
                difficulty_level varchar(20) NOT NULL DEFAULT 'medium',
                success_rate double precision NOT NULL DEFAULT 0,
                status varchar(20) NOT NULL DEFAULT 'draft',
                progress_percentage integer NOT NULL DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
                started_at timestamp with time zone NULL,
                completed_at timestamp with time zone NULL,
                agent_assignments jsonb NOT NULL DEFAULT '{}',
                execution_log jsonb NOT NULL DEFAULT '[]',
                results jsonb NOT NULL DEFAULT '{}',
                user_id uuid NULL,
                opportunity_tracking_id uuid NULL
            );
        """
    }

    # Create missing tables
    created_count = 0
    skipped_count = 0

    with connection.cursor() as cursor:
        for table_name, create_sql in critical_tables.items():
            if table_name in existing_tables:
                logger.info(f"✅ Table {table_name} already exists - skipping")
                skipped_count += 1
            else:
                try:
                    logger.info(f"🔧 Creating table {table_name}...")
                    cursor.execute(create_sql)
                    logger.info(f"✅ Created table {table_name}")
                    created_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to create {table_name}: {e}")
                    raise

    # Create indexes for performance
    logger.info("\n🔧 Creating indexes for optimal performance...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_opp_user_id ON intelligence_rt_opportunitytracking(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_opp_status ON intelligence_rt_opportunitytracking(status);",
        "CREATE INDEX IF NOT EXISTS idx_opp_type ON intelligence_rt_opportunitytracking(opportunity_type);",
        "CREATE INDEX IF NOT EXISTS idx_opp_discovered ON intelligence_rt_opportunitytracking(discovered_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_rev_user_id ON intelligence_rt_unifiedrevenuetracking(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_rev_earned ON intelligence_rt_unifiedrevenuetracking(earned_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_rev_opp_id ON intelligence_rt_unifiedrevenuetracking(opportunity_id);",
        "CREATE INDEX IF NOT EXISTS idx_agent_exec_user ON intelligence_rt_agentexecution(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_agent_exec_started ON intelligence_rt_agentexecution(started_at DESC);",
    ]

    with connection.cursor() as cursor:
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(f"✅ Created index")
            except Exception as e:
                logger.warning(f"⚠️ Index creation warning: {e}")

    logger.info(f"\n📊 Summary:")
    logger.info(f"   Tables created: {created_count}")
    logger.info(f"   Tables skipped (already exist): {skipped_count}")
    logger.info(f"   Total tables: {len(critical_tables)}")

    return created_count


def verify_tables():
    """Verify all critical tables exist"""
    logger.info("\n🔍 Verifying all critical tables exist...")

    required_tables = [
        'intelligence_rt_opportunitytracking',
        'intelligence_rt_unifiedrevenuetracking',
        'intelligence_rt_earningrecord',
        'intelligence_rt_userincomeprofile',
        'intelligence_rt_spiderintelligencenode',
        'intelligence_rt_agentintelligencefeed',
        'intelligence_rt_advisorintelligencefeed',
        'intelligence_rt_agentexecution',
        'intelligence_rt_opportunityactionplan',
    ]

    all_exist = True
    for table_name in required_tables:
        exists = check_table_exists(table_name)
        status = "✅" if exists else "❌"
        logger.info(f"   {status} {table_name}")
        if not exists:
            all_exist = False

    return all_exist


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("🔧 INTELLIGENT DATABASE TABLE CREATION SCRIPT")
    logger.info("=" * 80)

    try:
        # Create missing tables
        created_count = create_missing_tables()

        # Verify all tables exist
        all_tables_exist = verify_tables()

        if all_tables_exist:
            logger.info("\n" + "=" * 80)
            logger.info("🎉 SUCCESS! All database tables created successfully!")
            logger.info("=" * 80)
            logger.info("\n📊 Next Steps:")
            logger.info("   1. Run: python scripts/populate_real_opportunities.py")
            logger.info("   2. Navigate to: http://localhost:8000/income/")
            logger.info("   3. See your Income Builder come to life! 🚀")
            logger.info("\n")
            return 0
        else:
            logger.error("\n❌ Some tables are still missing!")
            return 1

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
