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