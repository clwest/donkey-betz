"""Session 1243 — rename core.SpiderData → core.LegacySpiderData.

Removes the cross-app class-name collision with `persistence.SpiderData`.
Both classes had 31,777 rows split between them (8,177 in core, 23,600 in
persistence). The modern canonical model lives in `persistence.SpiderData`
(36 fields, written by `ai_core.spiders.base_spider.BaseSpider`); this
core variant is the 15-field legacy model still referenced by ~93
production files (management commands, older tasks, view-level writers).

This rename is purely a class+table rename — no data loss, no schema
change, no caller behavior change. `RenameModel` is atomic. All ~93
production importers are updated in the same PR (Option D1 — clean cut
per Chris's S1243 directive).

Audit context: Cat 2 deliverable 86870fdd-e8d8-48d3-9760-4bea75ec10e3
Finding 2.3.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0366_session_1243_rebuild_pamessagefeedback"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="SpiderData",
            new_name="LegacySpiderData",
        ),
    ]
