<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Django management command catalog
>
> **Where to look now:**
> - [core/management/commands/ (source)](/core/management/commands/ (source))
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Management Commands Documentation

**Total Commands:** 43
**Location:** `core/management/commands/`
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Command Categories](#command-categories)
3. [Complete Command List](#complete-command-list)
4. [Key Commands Detail](#key-commands-detail)
5. [Usage](#usage)

---

## Overview

Django management commands provide CLI tools for system administration, debugging, data management, and automation.

### Running Commands

```bash
# Basic usage
python manage.py <command_name>

# With arguments
python manage.py <command_name> --option=value

# With virtual environment
.venv/bin/python manage.py <command_name>
```

---

## Command Categories

### System Health & Diagnostics (6)

| Command | Purpose |
|---------|---------|
| `system_health_check` | Comprehensive system health diagnostics |
| `system_reality_check` | Verify system reality score |
| `reality_check` | Quick reality verification |
| `validate_data_integrity` | Validate database integrity |
| `validate_section` | Validate specific section |
| `validate_security` | Security validation |

### Agent Management (8)

| Command | Purpose |
|---------|---------|
| `agent_introduction_party` | Initialize all agents with introductions |
| `force_agent_cycle` | Force run agent execution cycle |
| `cleanup_agents` | Clean up stale agent data |
| `connect_all_agents` | Connect agents to ecosystem |
| `register_cto_agent` | Register CTO agent |
| `register_coo_agent` | Register COO agent |
| `register_creative_agents` | Register creative agents |
| `load_all_agents_advisors` | Load agents and advisors |

### Spider Management (5)

| Command | Purpose |
|---------|---------|
| `activate_spiders` | Activate spider network |
| `boost_spiders` | Boost spider performance |
| `bulk_embed_spiders` | Bulk generate spider embeddings |
| `process_spider_data` | Process collected spider data |
| `sync_spider_agents` | Sync spiders with agents |

### Learning & Training (6)

| Command | Purpose |
|---------|---------|
| `sync_agent_learning` | Sync agent learning data |
| `discover_learning_cohorts` | Discover learning cohorts |
| `start_learning_demo` | Start learning demonstration |
| `fetch_training_data` | Fetch training datasets |
| `ingest_codebase` | Ingest codebase for RAG |
| `ragtest` | Test RAG functionality |

### Demo & Testing (5)

| Command | Purpose |
|---------|---------|
| `full_system_demo` | Run full system demonstration |
| `seed_golden_path_demo` | Seed golden path demo data |
| `seed_test_scenarios` | Seed test scenarios |
| `generate_sample_data` | Generate sample data |
| `test_agent_scenarios` | Test agent scenarios |

### Database & Data (4)

| Command | Purpose |
|---------|---------|
| `audit_database` | Audit database structure |
| `backfill_decisions` | Backfill boardroom decisions |
| `regenerate_pilots` | Regenerate pilot data |
| `achieve_95_reality` | Achieve 95% reality score |

### Platform & Deployment (4)

| Command | Purpose |
|---------|---------|
| `deploy_platform_unification` | Deploy platform unification |
| `init_platform` | Initialize platform |
| `start_bridge` | Start system bridge |
| `sync_celery_beat` | Sync Celery Beat schedules |

### Discord & Integration (2)

| Command | Purpose |
|---------|---------|
| `run_discord_bot` | Start Discord bot |
| `create_test_token` | Create test API token |

### Documentation & Self-Dev (3)

| Command | Purpose |
|---------|---------|
| `write_self_blog` | Generate self-documentation blog |
| `selfpatch` | Self-patching system |
| `askdocs` | Query documentation |

---

## Complete Command List (43)

```
achieve_95_reality
activate_spiders
agent_introduction_party
askdocs
audit_database
backfill_decisions
boost_spiders
bulk_embed_spiders
cleanup_agents
connect_all_agents
create_test_token
deploy_platform_unification
discover_learning_cohorts
fetch_training_data
force_agent_cycle
full_system_demo
generate_sample_data
ingest_codebase
init_platform
load_all_agents_advisors
process_spider_data
ragtest
reality_check
regenerate_pilots
register_coo_agent
register_creative_agents
register_cto_agent
run_discord_bot
seed_golden_path_demo
seed_test_scenarios
selfpatch
start_bridge
start_learning_demo
sync_agent_learning
sync_celery_beat
sync_spider_agents
system_health_check
system_reality_check
test_agent_scenarios
validate_data_integrity
validate_section
validate_security
write_self_blog
```

---

## Key Commands Detail

### system_health_check

Comprehensive system health diagnostics.

```bash
python manage.py system_health_check
```

**Checks:**
- Database connectivity
- Redis connection
- Celery workers status
- Spider network health
- Agent ecosystem status
- API key validity
- Disk space
- Memory usage

**Output:**
```
✅ Database: Connected (324 models)
✅ Redis: Connected
✅ Celery: 3 workers active
✅ Spiders: 72/77 working
✅ Agents: 71 registered
✅ API Keys: All valid
✅ Disk: 45% used
✅ Memory: 62% used
Overall: HEALTHY
```

### force_agent_cycle

Force run agent execution cycle for testing.

```bash
python manage.py force_agent_cycle
python manage.py force_agent_cycle --agent=ImageAgent
python manage.py force_agent_cycle --category=creation
```

**Options:**
- `--agent` - Run specific agent
- `--category` - Run category of agents
- `--dry-run` - Preview without execution
- `--verbose` - Detailed output

### agent_introduction_party

Initialize all agents with introductions.

```bash
python manage.py agent_introduction_party
```

**Actions:**
- Creates Agent database records
- Initializes agent personalities
- Sets initial mood states
- Creates introduction memories
- Posts to Discord #agent-introductions

### activate_spiders

Activate and test spider network.

```bash
python manage.py activate_spiders
python manage.py activate_spiders --category=financial
python manage.py activate_spiders --spider=hackernews
```

**Options:**
- `--category` - Activate by category
- `--spider` - Activate specific spider
- `--test` - Run test collection
- `--force` - Force activation even if rate limited

### sync_celery_beat

Synchronize Celery Beat schedules with database.

```bash
python manage.py sync_celery_beat
```

**Actions:**
- Creates PeriodicTask records
- Updates schedules from celery.py
- Removes stale schedules
- Verifies schedule integrity

### run_discord_bot

Start the Discord bot.

```bash
python manage.py run_discord_bot
```

**Requirements:**
- `DISCORD_BOT_TOKEN` environment variable
- Bot invited to server with proper permissions

### seed_golden_path_demo

Seed demonstration data for golden path.

```bash
python manage.py seed_golden_path_demo
```

**Creates:**
- Sample agents with history
- Spider data samples
- Demo opportunities
- Example workflows
- Sample content

### ingest_codebase

Ingest codebase for RAG/semantic search.

```bash
python manage.py ingest_codebase
python manage.py ingest_codebase --path=/path/to/code
python manage.py ingest_codebase --extensions=py,js,ts
```

**Options:**
- `--path` - Directory to ingest
- `--extensions` - File extensions to include
- `--chunk-size` - Chunk size for embeddings
- `--model` - Embedding model to use

---

## Usage Examples

### Daily Operations

```bash
# Morning health check
python manage.py system_health_check

# Force spider collection
python manage.py activate_spiders --test

# Sync schedules after celery.py changes
python manage.py sync_celery_beat
```

### Development/Testing

```bash
# Seed demo data
python manage.py seed_golden_path_demo

# Test agent execution
python manage.py force_agent_cycle --dry-run

# Run full system demo
python manage.py full_system_demo
```

### Maintenance

```bash
# Audit database
python manage.py audit_database

# Clean up old data
python manage.py cleanup_agents

# Validate integrity
python manage.py validate_data_integrity
```

### Debugging

```bash
# Reality check
python manage.py reality_check

# Test RAG
python manage.py ragtest "How do agents work?"

# Query docs
python manage.py askdocs "What is the spider network?"
```

---

## Creating New Commands

```python
# core/management/commands/my_command.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of my command'

    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='Option description')

    def handle(self, *args, **options):
        self.stdout.write('Running my command...')
        # Command logic here
        self.stdout.write(self.style.SUCCESS('Done!'))
```

---

## Related Documentation

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [CELERY_TASKS.md](CELERY_TASKS.md) - Background task management
- [INDEX.md](INDEX.md) - System overview