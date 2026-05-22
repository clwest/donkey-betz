# Session 1120: Corrective DB-only migration for chat_conversations.
#
# History:
# - 0095 (Session 455) declared platform/discord_*/session_* columns via AddField.
# - 0236 (Session 987) was state-only (SeparateDatabaseAndState with
#   database_operations=[]) on the assumption columns already existed.
# - On production (and previously on local — see Session 1118 wrap), the
#   columns went missing after a DB restore while migration history still
#   records 0095 as applied. PA ProgrammingError surfaces from
#   process_pa_chat_task: "column chat_conversations.platform does not exist".
#
# Fix: idempotent RunSQL with ADD COLUMN IF NOT EXISTS + CREATE INDEX IF NOT EXISTS.
# - No-op locally (columns already present from Session 1118's manual ALTER).
# - Adds the missing columns on production where the schema regressed.
# - state_operations=[] because 0236 already declared the fields in Django's state.

from django.db import migrations


SQL_UP = """
ALTER TABLE chat_conversations
    ADD COLUMN IF NOT EXISTS platform varchar(20) NOT NULL DEFAULT 'web',
    ADD COLUMN IF NOT EXISTS discord_user_id varchar(30) NULL,
    ADD COLUMN IF NOT EXISTS discord_channel_id varchar(30) NULL,
    ADD COLUMN IF NOT EXISTS discord_guild_id varchar(30) NULL,
    ADD COLUMN IF NOT EXISTS session_title varchar(200) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS session_active boolean NOT NULL DEFAULT true;

CREATE INDEX IF NOT EXISTS chat_conver_platfor_idx
    ON chat_conversations (platform, created_at DESC);
CREATE INDEX IF NOT EXISTS chat_conver_discord_idx
    ON chat_conversations (discord_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS chat_conver_session_idx
    ON chat_conversations (session_active, created_at DESC);
"""


SQL_DOWN = """
-- Intentionally no-op. Reversing would drop columns the model
-- (and migration 0236's state) require to exist.
"""


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0340_f2f_session"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_UP,
            reverse_sql=SQL_DOWN,
            state_operations=[],
        ),
    ]
