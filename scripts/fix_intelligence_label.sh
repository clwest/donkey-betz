#!/usr/bin/env bash
# scripts/fix_intelligence_label.sh
# One-shot script to normalize the Intelligence app label and fix migrations/FKs.

set -euo pipefail

echo "🔧 Normalizing Intelligence app to label 'intelligence'..."

# --- helpers ---------------------------------------------------------------
backup() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  if [[ ! -f "${f}.bak.fixint" ]]; then
    cp "$f" "${f}.bak.fixint"
  fi
}

safe_sed_inplace() {
  # Cross-platform sed -i (macOS/BSD & GNU)
  local pattern="$1"
  shift
  for file in "$@"; do
    backup "$file"
    if sed --version >/dev/null 2>&1; then
      sed -i -E "$pattern" "$file"
    else
      sed -i '' -E "$pattern" "$file"
    fi
  done
}

exists() { command -v "$1" >/dev/null 2>&1; }

# --- step 0: sanity --------------------------------------------------------
if [[ ! -f "manage.py" ]]; then
  echo "❌ Run this from your Django project root (where manage.py lives)."
  exit 1
fi

# --- step 1: apps.py label -------------------------------------------------
APPS_PY="intelligence/apps.py"
if [[ -f "$APPS_PY" ]]; then
  backup "$APPS_PY"
  python - <<'PY'
import io, os, re, sys
p="intelligence/apps.py"
src=open(p,"r",encoding="utf-8").read()
# Ensure a proper AppConfig with label='intelligence'
if "class IntelligenceConfig(" not in src or "label" not in src or "name" not in src:
    src = "from django.apps import AppConfig\n\nclass IntelligenceConfig(AppConfig):\n    name = 'intelligence'\n    label = 'intelligence'\n"
else:
    src = re.sub(r"(label\s*=\s*)['\"]intelligence_rt['\"]", r"\1'intelligence'", src)
    src = re.sub(r"(name\s*=\s*)['\"][^'\"]+['\"]", r"\1'intelligence'", src)
open(p,"w",encoding="utf-8").write(src)
print("✅ apps.py normalized to label 'intelligence'")
PY
else
  echo "⚠️  intelligence/apps.py not found. Creating a minimal one."
  mkdir -p intelligence
  cat > "$APPS_PY" <<'PY'
from django.apps import AppConfig

class IntelligenceConfig(AppConfig):
    name = 'intelligence'
    label = 'intelligence'
PY
fi

# --- step 2: fix Meta.app_label in intelligence models ---------------------
echo "🧹 Cleaning Meta.app_label in intelligence models → 'intelligence'"
while IFS= read -r -d '' f; do
  safe_sed_inplace "s/(app_label\s*=\s*)'intelligence_rt'/\\1'intelligence'/g" "$f"
done < <(find intelligence -type f -name "*.py" -print0)

# --- step 3: fix string FKs to ActionPlan ---------------------------------
echo "🪛 Rewriting string FKs to use correct label and direct import"

# 3a) In code: 'intelligence.ActionPlan' → 'intelligence.ActionPlan'
while IFS= read -r -d '' f; do
  safe_sed_inplace "s/'intelligence_rt\\.ActionPlan'/'intelligence.ActionPlan'/g" "$f"
  safe_sed_inplace "s/\"intelligence_rt\\.ActionPlan\"/\"intelligence.ActionPlan\"/g" "$f"
done < <(find intelligence -type f -name "*.py" -print0)

# 3b) Prefer direct class reference: ForeignKey(ActionPlan, ...)
while IFS= read -r -d '' f; do
  # Convert string FK to direct reference
  safe_sed_inplace "s/ForeignKey\\((['\"])intelligence\\.ActionPlan\\1/ForeignKey(ActionPlan/g" "$f"
  # Ensure import exists at top
  if grep -q "ForeignKey(ActionPlan" "$f"; then
    if ! grep -Eq "^from \.action_plan import ActionPlan" "$f"; then
      backup "$f"
      # insert import at line 1
      if sed --version >/dev/null 2>&1; then
        sed -i -E '1i from .action_plan import ActionPlan' "$f"
      else
        sed -i '' -E '1i\
from .action_plan import ActionPlan
' "$f"
      fi
    fi
  fi
done < <(find intelligence -type f -name "*.py" -print0)

# --- step 4: update migrations referencing old label -----------------------
echo "🗃️  Aligning migration files to label 'intelligence'"

# Intelligence app migrations
if [[ -d intelligence/migrations ]]; then
  while IFS= read -r -d '' f; do
    safe_sed_inplace "s/'intelligence_rt'/'intelligence'/g" "$f"
    safe_sed_inplace "s/\"intelligence_rt\"/\"intelligence\"/g" "$f"
    safe_sed_inplace "s/'intelligence_rt\\.ActionPlan'/'intelligence.ActionPlan'/g" "$f"
    safe_sed_inplace "s/\"intelligence_rt\\.ActionPlan\"/\"intelligence.ActionPlan\"/g" "$f"
  done < <(find intelligence/migrations -type f -name "*.py" -print0)
fi

# ai_core.intelligence migrations (usually fine, but align if needed)
if [[ -d ai_core/intelligence/migrations ]]; then
  while IFS= read -r -d '' f; do
    safe_sed_inplace "s/'intelligence_rt'/'intelligence'/g" "$f"
    safe_sed_inplace "s/\"intelligence_rt\"/\"intelligence\"/g" "$f"
    safe_sed_inplace "s/'intelligence_rt\\.ActionPlan'/'intelligence.ActionPlan'/g" "$f"
    safe_sed_inplace "s/\"intelligence_rt\\.ActionPlan\"/\"intelligence.ActionPlan\"/g" "$f"
  done < <(find ai_core/intelligence/migrations -type f -name "*.py" -print0)
fi

# --- step 5: ensure INSTALLED_APPS references the AppConfig ----------------
# We try to update a settings.py (first one found) to use IntelligenceConfig.
SETTINGS_FILE=$(git ls-files "*settings.py" | grep -E "/(core|config|project|backend)/settings\.py$|^settings\.py$" | head -n1 || true)
if [[ -n "${SETTINGS_FILE:-}" ]]; then
  backup "$SETTINGS_FILE"
  # If IntelligenceConfig not present but 'intelligence' is, replace first occurrence.
  if ! grep -q "intelligence\.apps\.IntelligenceConfig" "$SETTINGS_FILE" && grep -q "'intelligence'" "$SETTINGS_FILE"; then
    python - "$SETTINGS_FILE" <<'PY'
import io, sys, re
p=sys.argv[1]
s=open(p,"r",encoding="utf-8").read()
# Replace the first bare 'intelligence' entry with the AppConfig path.
s=re.sub(r"(['\"])intelligence\1", r"'intelligence.apps.IntelligenceConfig'", s, count=1)
open(p,"w",encoding="utf-8").write(s)
print(f"✅ Updated {p} to use intelligence.apps.IntelligenceConfig")
PY
  fi
fi

# --- step 6: clean caches --------------------------------------------------
echo "🧽 Clearing __pycache__ and *.pyc"
find intelligence -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find intelligence -name "*.pyc" -delete 2>/dev/null || true

# --- step 7: run migrations ------------------------------------------------
echo "🚀 Running makemigrations + migrate (intelligence → project)"
if exists python; then
  python manage.py makemigrations intelligence || true
  python manage.py migrate intelligence
  python manage.py migrate
  python manage.py check
else
  echo "⚠️  Python not found on PATH; skipping migrate/check."
fi

echo "✅ Done. If you still see FK or app-label errors, run:"
echo "   python manage.py shell -c \"from django.apps import apps; print(sorted([(a.label,a.name) for a in apps.get_app_configs() if 'intelligence' in a.name]))\""