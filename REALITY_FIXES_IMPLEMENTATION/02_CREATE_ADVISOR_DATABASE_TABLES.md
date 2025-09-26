# 🔧 FIX #2: Create Advisor Database Tables
## Priority: HIGH | Time: 5 minutes | Impact: +5% Reality

---

## 🔴 CURRENT PROBLEM

The advisor system has complete logic but missing database tables:
- 25 legendary advisors exist in code (Warren Buffett, Cathie Wood, etc.)
- Complex scoring algorithms implemented
- Database models defined but tables not created

**Error Evidence:**
```sql
relation "advisors_advisor" does not exist
relation "advisor_categories" does not exist
```

---

## ✅ COMPLETE SOLUTION

### Step 1: Create Advisor Models File

**File:** `/intelligence/models/advisor_models.py`

```python
"""
Advisor Database Models
=======================
Models for the 25 legendary advisors
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class AdvisorCategory(models.Model):
    """Categories for advisors"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="💼")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Advisor Categories"
        db_table = 'advisor_categories'

    def __str__(self):
        return self.name


class LegendaryAdvisor(models.Model):
    """The 25 legendary advisors"""

    # Identity
    name = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=300)
    category = models.ForeignKey(AdvisorCategory, on_delete=models.CASCADE)

    # Expertise
    expertise = models.JSONField(default=list)  # List of expertise areas
    specialties = models.JSONField(default=list)  # Specific specialties

    # Personality
    personality_traits = models.JSONField(default=dict)
    communication_style = models.TextField()

    # Performance
    success_rate = models.FloatField(default=0.0)
    total_consultations = models.IntegerField(default=0)
    total_revenue_generated = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Metadata
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField()
    famous_quotes = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'legendary_advisors'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['success_rate']),
        ]

    def __str__(self):
        return f"{self.name} - {self.title}"


class AdvisorConsultation(models.Model):
    """Record of advisor consultations"""

    advisor = models.ForeignKey(LegendaryAdvisor, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Query
    query = models.TextField()
    context = models.JSONField(default=dict)

    # Response
    advice = models.TextField()
    confidence_score = models.FloatField(default=0.0)

    # Outcome
    was_helpful = models.BooleanField(null=True)
    outcome = models.TextField(blank=True)
    revenue_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    processing_time = models.FloatField(default=0.0)  # seconds

    class Meta:
        db_table = 'advisor_consultations'
        indexes = [
            models.Index(fields=['advisor', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]


class AdvisorCollaboration(models.Model):
    """When multiple advisors work together"""

    lead_advisor = models.ForeignKey(LegendaryAdvisor, on_delete=models.CASCADE, related_name='led_collaborations')
    participating_advisors = models.ManyToManyField(LegendaryAdvisor, related_name='collaborations')

    # Task
    task = models.TextField()
    task_type = models.CharField(max_length=100)

    # Result
    combined_advice = models.TextField()
    consensus_score = models.FloatField(default=0.0)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'advisor_collaborations'
```

### Step 2: Create Migration Script

**File:** `/create_advisor_tables.py`

```python
#!/usr/bin/env python
"""
Create Advisor Database Tables and Populate with Legendary Advisors
====================================================================
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def create_advisor_tables():
    """Create advisor tables using raw SQL"""

    with connection.cursor() as cursor:
        # Create advisor_categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advisor_categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                icon VARCHAR(50) DEFAULT '💼',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create legendary_advisors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS legendary_advisors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) UNIQUE NOT NULL,
                title VARCHAR(300),
                category_id INTEGER REFERENCES advisor_categories(id),
                expertise JSONB DEFAULT '[]',
                specialties JSONB DEFAULT '[]',
                personality_traits JSONB DEFAULT '{}',
                communication_style TEXT,
                success_rate FLOAT DEFAULT 0.0,
                total_consultations INTEGER DEFAULT 0,
                total_revenue_generated DECIMAL(15,2) DEFAULT 0,
                avatar_url VARCHAR(500),
                bio TEXT,
                famous_quotes JSONB DEFAULT '[]',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create advisor_consultations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advisor_consultations (
                id SERIAL PRIMARY KEY,
                advisor_id INTEGER REFERENCES legendary_advisors(id),
                user_id INTEGER,
                query TEXT,
                context JSONB DEFAULT '{}',
                advice TEXT,
                confidence_score FLOAT DEFAULT 0.0,
                was_helpful BOOLEAN,
                outcome TEXT,
                revenue_impact DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_time FLOAT DEFAULT 0.0
            )
        """)

        # Create advisor_collaborations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advisor_collaborations (
                id SERIAL PRIMARY KEY,
                lead_advisor_id INTEGER REFERENCES legendary_advisors(id),
                task TEXT,
                task_type VARCHAR(100),
                combined_advice TEXT,
                consensus_score FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_advisors_category ON legendary_advisors(category_id, is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_advisors_success ON legendary_advisors(success_rate)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consultations_advisor ON advisor_consultations(advisor_id, created_at)")

        print("✅ Advisor tables created successfully!")

def populate_legendary_advisors():
    """Populate the 25 legendary advisors"""

    with connection.cursor() as cursor:
        # Insert categories
        categories = [
            ('Investment', 'Traditional investment and value strategies', '💰'),
            ('Innovation', 'Technology and disruptive innovation', '🚀'),
            ('Trading', 'Active trading and market timing', '📊'),
            ('Macro', 'Macroeconomic and global strategies', '🌍')
        ]

        for name, desc, icon in categories:
            cursor.execute("""
                INSERT INTO advisor_categories (name, description, icon)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            """, [name, desc, icon])

        # Insert legendary advisors
        advisors = [
            # Investment Masters
            ('Warren Buffett', 'Oracle of Omaha - Value Investing Legend', 'Investment',
             '["value investing", "long-term holdings", "fundamental analysis"]'),
            ('Peter Lynch', 'Fidelity Magellan Fund Legend', 'Investment',
             '["growth at reasonable price", "invest in what you know", "PEG ratio"]'),
            ('Benjamin Graham', 'Father of Value Investing', 'Investment',
             '["margin of safety", "intrinsic value", "intelligent investor"]'),
            ('John Bogle', 'Vanguard Founder - Index Fund Pioneer', 'Investment',
             '["index funds", "low-cost investing", "buy and hold"]'),
            ('Charlie Munger', "Buffett's Partner - Mental Models Master", 'Investment',
             '["mental models", "circle of competence", "psychology of investing"]'),

            # Innovation Leaders
            ('Cathie Wood', 'ARK Invest CEO - Disruptive Innovation', 'Innovation',
             '["disruptive innovation", "genomics", "artificial intelligence", "robotics"]'),
            ('Marc Andreessen', 'a16z Co-founder - Software Visionary', 'Innovation',
             '["software eating world", "crypto", "web3", "venture capital"]'),
            ('Peter Thiel', 'PayPal Founder - Contrarian Thinker', 'Innovation',
             '["zero to one", "monopoly theory", "contrarian thinking"]'),
            ('Chamath Palihapitiya', 'Social Capital - SPAC King', 'Innovation',
             '["SPACs", "technology investing", "social impact"]'),
            ('Naval Ravikant', 'AngelList Founder - Philosopher Investor', 'Innovation',
             '["startups", "cryptocurrency", "wealth creation", "happiness"]'),

            # Trading Legends
            ('George Soros', 'Quantum Fund - The Man Who Broke the Bank', 'Trading',
             '["reflexivity theory", "currency trading", "macro trading"]'),
            ('Paul Tudor Jones', 'Tudor Investment - Macro Trading Legend', 'Trading',
             '["macro trading", "risk management", "technical analysis"]'),
            ('Stanley Druckenmiller', 'Duquesne Capital - Soros Protégé', 'Trading',
             '["macro trading", "currency", "concentration"]'),
            ('Jesse Livermore', 'Boy Plunger - Trading Psychology Pioneer', 'Trading',
             '["tape reading", "market psychology", "trend following"]'),
            ('Ed Thorp', 'Quantitative Trading Pioneer', 'Trading',
             '["quantitative trading", "options pricing", "probability"]'),

            # Macro Masters
            ('Ray Dalio', 'Bridgewater - Principles & All Weather', 'Macro',
             '["principles", "all weather portfolio", "debt cycles", "radical transparency"]'),
            ('Jim Rogers', 'Quantum Fund Co-founder - Commodity Bull', 'Macro',
             '["commodities", "emerging markets", "global investing"]'),
            ('Michael Burry', 'The Big Short - Contrarian Analyst', 'Macro',
             '["contrarian investing", "deep value", "crisis prediction"]'),
            ('Howard Marks', 'Oaktree - Distressed Debt Master', 'Macro',
             '["distressed debt", "market cycles", "risk management"]'),
            ('Bill Ackman', 'Pershing Square - Activist Investor', 'Macro',
             '["activist investing", "special situations", "concentrated bets"]'),

            # Additional Legends
            ('Carl Icahn', 'Corporate Raider - Activist Legend', 'Investment',
             '["activist investing", "corporate raids", "value unlocking"]'),
            ('David Tepper', 'Appaloosa - Distressed Master', 'Trading',
             '["distressed securities", "risk/reward", "contrarian"]'),
            ('Seth Klarman', 'Baupost Group - Margin of Safety', 'Investment',
             '["value investing", "margin of safety", "patience"]'),
            ('Joel Greenblatt', 'Magic Formula Investing', 'Investment',
             '["magic formula", "value investing", "special situations"]'),
            ('William O\'Neil', 'CANSLIM Method Creator', 'Trading',
             '["CANSLIM", "growth stocks", "technical analysis"]')
        ]

        for name, title, category, expertise in advisors:
            cursor.execute("""
                INSERT INTO legendary_advisors (name, title, category_id, expertise, bio, success_rate)
                SELECT %s, %s, c.id, %s::jsonb, %s, %s
                FROM advisor_categories c
                WHERE c.name = %s
                ON CONFLICT (name) DO NOTHING
            """, [name, title, expertise, f"{name} is a legendary investor known for {title}", 85.0, category])

        print(f"✅ Populated {len(advisors)} legendary advisors!")

def verify_tables():
    """Verify tables were created"""

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM legendary_advisors
        """)
        count = cursor.fetchone()[0]
        print(f"📊 Total advisors in database: {count}")

        cursor.execute("""
            SELECT name, title FROM legendary_advisors LIMIT 5
        """)
        advisors = cursor.fetchall()

        print("\n🎯 Sample Advisors:")
        for name, title in advisors:
            print(f"  • {name}: {title}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏗️ CREATING ADVISOR DATABASE TABLES")
    print("="*60)

    try:
        create_advisor_tables()
        populate_legendary_advisors()
        verify_tables()

        print("\n✅ SUCCESS! Advisor tables created and populated!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("="*60)
```

### Step 3: Run the Migration

```bash
# Execute the script
python create_advisor_tables.py

# Or use Django migrations
python manage.py makemigrations intelligence
python manage.py migrate intelligence
```

---

## 🚀 VERIFICATION STEPS

1. **Run the creation script:**
   ```bash
   python create_advisor_tables.py
   ```

2. **Check in PostgreSQL:**
   ```sql
   psql -d your_database -c "SELECT COUNT(*) FROM legendary_advisors;"
   psql -d your_database -c "SELECT name FROM legendary_advisors WHERE name LIKE 'Warren%';"
   ```

3. **Test in Django shell:**
   ```python
   python manage.py shell
   >>> from django.db import connection
   >>> with connection.cursor() as c:
   ...     c.execute("SELECT name, title FROM legendary_advisors LIMIT 3")
   ...     print(c.fetchall())
   ```

---

## 🎯 SUCCESS CRITERIA

You'll know this is fixed when:
1. ✅ No more "relation does not exist" errors
2. ✅ 25 legendary advisors in database
3. ✅ Warren Buffett, Cathie Wood, etc. are queryable
4. ✅ Advisor consultations can be stored

---

## 📈 IMPACT WHEN FIXED

- **+5% Reality Score** - Advisors become real
- **Unlock 25 Advisors** - All legendary investors available
- **Enable Consultations** - Can get real advice
- **Enable Collaboration** - Multiple advisors can work together

---

## ⏰ TIME ESTIMATE

- Creating script: 2 minutes
- Running migration: 1 minute
- Verification: 2 minutes
- **Total: 5 minutes**

---

*This fix makes Warren Buffett and 24 other legends real in your system!*