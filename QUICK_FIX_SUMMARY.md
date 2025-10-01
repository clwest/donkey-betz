# 🎯 INCOME BUILDER QUICK FIX - EXECUTE THESE 3 COMMANDS

**Problem**: Tables exist but don't match Django model → Can't populate data → UI shows empty

**Solution**: 3 commands, 5 minutes total

---

## ✅ THE FIX

```bash
# Command 1: Drop mismatched table & recreate (30 seconds)
echo "DROP TABLE IF EXISTS intelligence_rt_opportunitytracking CASCADE;" | python manage.py dbshell && python manage.py migrate intelligence_rt 0003 --fake && python manage.py migrate intelligence_rt 0004

# Command 2: Populate with 8 opportunities (10 seconds)
python scripts/quick_populate_opportunities.py

# Command 3: Open browser
open http://localhost:8000/income/
```

---

## 🎉 What You'll See After

8 Active Opportunities including:
- 3 sports betting opportunities with Kelly Criterion
- 3 job opportunities ($120k-$150k remote roles)
- 2 freelance gigs ($3,500-$4,200 projects)

---

## ⚡ One-Line Version

```bash
echo "DROP TABLE IF EXISTS intelligence_rt_opportunitytracking CASCADE;" | python manage.py dbshell && python manage.py migrate intelligence_rt 0003 --fake && python manage.py migrate intelligence_rt 0004 && python scripts/quick_populate_opportunities.py && open http://localhost:8000/income/
```

---

**That's it!** Run the commands and see your Income Builder come alive! 🚀
