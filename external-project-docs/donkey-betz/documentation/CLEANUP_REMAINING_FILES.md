# Cleanup Plan for Remaining Documentation Files

## 📊 Current Status
60 loose files in `/documentation/` root directory need organization

## 📁 Categorized Cleanup Plan

### 1. Session Files (32 files) → `/session-archive/`
Move all SESSION_*.md files to appropriate archive folders:
- SESSION_123-149 → `session-archive/older/`
- SESSION_150 → `session-archive/sessions-150-159/`
- SESSION_92 → `session-archive/older/`

**Command:**
```bash
mv SESSION_[0-9]*.md session-archive/older/
mv SESSION_1[0-4]*.md session-archive/older/
mv SESSION_15*.md session-archive/sessions-150-159/
```

### 2. Fix & Error Documentation (9 files) → `/audits-reports/fixes/`
- DATABASE_FIX_*.md
- ERROR_FIX_*.md
- ERROR_ANALYSIS_AND_FIX_PLAN.md
- Error-Research.md

**Command:**
```bash
mv *FIX*.md audits-reports/fixes/
mv Error-Research.md audits-reports/fixes/
```

### 3. Migration & Consolidation (5 files) → `/audits-reports/migrations/`
Create new subdirectory for migration documentation:
- CONSOLIDATION_*.md
- MIGRATION_REPORT.md
- DEPRECATION_REPORT.md

**Command:**
```bash
mkdir -p audits-reports/migrations
mv CONSOLIDATION*.md audits-reports/migrations/
mv MIGRATION_REPORT.md audits-reports/migrations/
mv DEPRECATION_REPORT.md audits-reports/migrations/
```

### 4. Planning & Analysis (12 files) → `/08-planning/`
These files are planning/analysis documents:
- BATCH_PROCESSING_PHASE7.md
- CELERY_HANGING_ANALYSIS.md
- FINAL_CLEANUP_ROADMAP.md
- FRONTEND_ALIGNMENT_CHECKLIST.md
- FRONTEND_LOCATION.md
- NESTED_FRONTEND_ANALYSIS.md
- PHASE_HANDOFF_TEMPLATE.md
- TASK_CONFIGURATION_FLOW.md

**Command:**
```bash
mv BATCH_PROCESSING_PHASE7.md 08-planning/
mv CELERY_HANGING_ANALYSIS.md 08-planning/
mv FINAL_CLEANUP_ROADMAP.md 08-planning/
mv FRONTEND_*.md 08-planning/
mv NESTED_FRONTEND_ANALYSIS.md 08-planning/
mv PHASE_HANDOFF_TEMPLATE.md 08-planning/
mv TASK_CONFIGURATION_FLOW.md 08-planning/
```

### 5. Special Files (Keep in root)
- README.md (main documentation index)
- REORGANIZATION_PLAN.md (current work)
- REORGANIZATION_COMPLETE.md (current work)

### 6. Already Handled
- CONTENT_STUDIO_SYSTEM_COMPLETE_GUIDE.md → Already in system-guides/content-studio/
- session-151.md → Move to session-archive/

## 🔄 Execution Order

1. Create missing directories
2. Move session files to archive
3. Move fix/error files to audits-reports
4. Move migration files to new subdirectory
5. Move planning files to 08-planning
6. Clean up duplicates

## ✅ End Result

After cleanup, documentation root will only contain:
- README.md (main index)
- REORGANIZATION_*.md (temporary, can be archived later)
- Directory structure folders

All content properly organized by type and purpose!