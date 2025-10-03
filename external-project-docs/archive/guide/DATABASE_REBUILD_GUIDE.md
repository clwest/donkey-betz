# Database Rebuild Guide

## Overview
This guide documents the complete database rebuild process performed on July 16, 2025, after catastrophic data loss. Follow these steps if you ever need to rebuild the Donkey Betz database from scratch.

## Prerequisites
- Fresh PostgreSQL database with all migrations applied
- Virtual environment activated
- Redis running
- All required environment variables set

## Step-by-Step Rebuild Process

### 1. Create AI Agent Templates
```bash
cd backend
python manage.py create_agent_templates
python manage.py create_financial_agents
python manage.py create_research_agents
python manage.py create_stock_analysis_agents
```

Expected result: 25 AI agents created

### 2. Create Content Templates
```bash
python manage.py create_content_templates
```

Expected result: 14 content templates created

### 3. Import Markdown Content
First, ensure the ingestion script uses a valid user ID:
```bash
# Check existing users
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print([f'ID: {u.id}, Username: {u.username}' for u in User.objects.all()])"

# Edit scripts/markdown_ingestion.py if needed to use correct user ID
```

Then run the ingestion:
```bash
python manage.py ingest_markdown --path /path/to/project/root/
```

Expected result: ~18,000+ memories created

### 4. Set Up Automated Backups
```bash
# Make backup script executable
chmod +x /path/to/project/scripts/backup_database.sh

# Add to crontab (runs daily at 2 AM)
crontab -e
# Add line: 0 2 * * * /path/to/project/scripts/backup_database.sh >> /path/to/project/logs/backup.log 2>&1
```

### 5. Verify Rebuild
```bash
python manage.py shell << EOF
from agent_orchestra.models import AgentTemplate
from content.models import ContentTemplate
from ai_partner.models import ConversationMemory

print(f'Agents: {AgentTemplate.objects.count()}')
print(f'Content Templates: {ContentTemplate.objects.count()}')
print(f'Memories: {ConversationMemory.objects.count():,}')
EOF
```

## Additional Data Sources to Import

### From External Services
1. **ChatGPT Conversations**: Export and convert to markdown
2. **Anthropic/Claude Conversations**: Export and convert to markdown
3. **PDF Documents**: Use PDF ingestion scripts (if available)

### Manual Recreation
1. **User Profiles**: Re-register users
2. **Business Plans**: Re-generate from templates
3. **Reddit/Stock Ideas**: Will be populated by auto-scout scripts

## Backup Strategy

### Daily Backups
- PostgreSQL dump via cron job
- Store backups for 30 days
- Consider cloud storage (S3, Google Cloud Storage)

### Before Major Changes
```bash
# Manual backup before risky operations
pg_dump -U postgres -d donkeybetz -f backup_$(date +%Y%m%d_%H%M%S).sql
```

### Recovery Testing
- Test restore process monthly
- Document any schema changes
- Keep backup verification logs

## Lessons Learned

1. **Always verify migrations**: Use --dry-run first
2. **Never use --fake without backups**: This caused our data loss
3. **Monitor disk space**: Ensure backup storage available
4. **Test recovery process**: Regular drills prevent panic

## Emergency Contacts

- Database Admin: [Your contact]
- System Admin: [Your contact]
- Cloud Provider Support: [Provider details]

---

Last Updated: July 16, 2025
Next Review: August 16, 2025