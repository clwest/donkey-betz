"""
Session 998B: Recreate OddsSnapshot + GameLineHistory tables on Railway.

Migration 0161 was marked as applied but the underlying tables were dropped.
This migration uses raw SQL with IF NOT EXISTS to safely recreate them.
"""

from django.db import migrations


def create_tables_if_missing(apps, schema_editor):
    """Create odds tables only if they don't exist (safe for re-run)."""
    connection = schema_editor.connection
    cursor = connection.cursor()

    # Check if core_gamelinehistory exists
    cursor.execute(
        "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'core_gamelinehistory')"
    )
    glh_exists = cursor.fetchone()[0]

    cursor.execute(
        "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'core_oddssnapshot')"
    )
    os_exists = cursor.fetchone()[0]

    if not os_exists:
        cursor.execute("""
            CREATE TABLE core_oddssnapshot (
                id BIGSERIAL PRIMARY KEY,
                game_id VARCHAR(100) NOT NULL,
                sport_key VARCHAR(50) NOT NULL,
                home_team VARCHAR(100) NOT NULL,
                away_team VARCHAR(100) NOT NULL,
                commence_time TIMESTAMPTZ NOT NULL,
                bookmaker VARCHAR(50) NOT NULL,
                bookmaker_title VARCHAR(100) DEFAULT '',
                market VARCHAR(20) NOT NULL,
                outcome_name VARCHAR(100) NOT NULL,
                price INTEGER NOT NULL,
                point NUMERIC(5, 1),
                captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        cursor.execute("CREATE INDEX core_os_game_id ON core_oddssnapshot (game_id)")
        cursor.execute("CREATE INDEX core_os_sport_key ON core_oddssnapshot (sport_key)")
        cursor.execute("CREATE INDEX core_os_bookmaker ON core_oddssnapshot (bookmaker)")
        cursor.execute("CREATE INDEX core_os_market ON core_oddssnapshot (market)")
        cursor.execute("CREATE INDEX core_os_captured_at ON core_oddssnapshot (captured_at)")
        cursor.execute("CREATE INDEX core_os_game_bk_mkt_out ON core_oddssnapshot (game_id, bookmaker, market, outcome_name)")
        cursor.execute("CREATE INDEX core_os_sport_cap ON core_oddssnapshot (sport_key, captured_at)")
        cursor.execute("CREATE INDEX core_os_game_cap ON core_oddssnapshot (game_id, captured_at)")

    if not glh_exists:
        cursor.execute("""
            CREATE TABLE core_gamelinehistory (
                id BIGSERIAL PRIMARY KEY,
                game_id VARCHAR(100) NOT NULL UNIQUE,
                sport_key VARCHAR(50) NOT NULL,
                home_team VARCHAR(100) NOT NULL,
                away_team VARCHAR(100) NOT NULL,
                commence_time TIMESTAMPTZ NOT NULL,
                open_spread_home NUMERIC(5, 1),
                open_spread_price INTEGER,
                open_total NUMERIC(5, 1),
                open_ml_home INTEGER,
                open_ml_away INTEGER,
                current_spread_home NUMERIC(5, 1),
                current_spread_price INTEGER,
                current_total NUMERIC(5, 1),
                current_ml_home INTEGER,
                current_ml_away INTEGER,
                spread_movement NUMERIC(5, 1) DEFAULT 0,
                total_movement NUMERIC(5, 1) DEFAULT 0,
                snapshot_count INTEGER DEFAULT 0,
                first_snapshot_at TIMESTAMPTZ,
                last_snapshot_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        cursor.execute("CREATE INDEX core_glh_game_id ON core_gamelinehistory (game_id)")
        cursor.execute("CREATE INDEX core_glh_sport_key ON core_gamelinehistory (sport_key)")
        cursor.execute("CREATE INDEX core_glh_commence ON core_gamelinehistory (commence_time)")
        cursor.execute("CREATE INDEX core_glh_last_snap ON core_gamelinehistory (last_snapshot_at)")
        cursor.execute("CREATE INDEX core_glh_sport_commence ON core_gamelinehistory (sport_key, commence_time)")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0240_session_998_governance"),
    ]

    operations = [
        migrations.RunPython(create_tables_if_missing, migrations.RunPython.noop),
    ]
