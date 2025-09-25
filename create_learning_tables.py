#!/usr/bin/env python3
"""
Create Learning Tables Migration
Sets up all the database tables for the persistent learning system
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def create_learning_tables():
    """Create the learning system tables"""
    print("🗄️ Creating Learning System Database Tables...")

    try:
        # Import models to register them
        from backend.intelligence.models import (
            AgentLearningEvent,
            LearningDocument,
            AgentKnowledgeBase,
            LearningEmbedding,
            AgentLearningSession,
            LearningInsight
        )

        print("✅ Models imported successfully")

        # Create migrations
        print("📝 Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'intelligence'])

        # Apply migrations
        print("⚡ Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])

        print("🎉 Learning system database tables created successfully!")

        # Verify tables exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE '%learning%'
                OR table_name LIKE '%agent%'
                OR table_name LIKE '%embedding%'
                ORDER BY table_name
            """)

            tables = cursor.fetchall()

            print(f"\n📊 Created {len(tables)} learning-related tables:")
            for table in tables:
                print(f"  - {table[0]}")

        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def check_database_connection():
    """Check if database connection works"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection successful")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def show_table_info():
    """Show information about the created tables"""
    try:
        from backend.intelligence.models import (
            AgentLearningEvent,
            LearningDocument,
            AgentKnowledgeBase,
            LearningEmbedding,
            AgentLearningSession,
            LearningInsight
        )

        print("\n📋 Learning System Tables Overview:")
        print("-" * 60)

        models_info = [
            ("AgentLearningEvent", "Stores every learning event for persistent agent memory"),
            ("LearningDocument", "Auto-generated documents from learning events"),
            ("AgentKnowledgeBase", "Persistent knowledge base for each agent"),
            ("LearningEmbedding", "Vector embeddings for semantic search"),
            ("AgentLearningSession", "Track learning sessions and batch processing"),
            ("LearningInsight", "High-level insights from multiple learning events")
        ]

        for model_name, description in models_info:
            print(f"🔹 {model_name}")
            print(f"   {description}")
            print()

    except Exception as e:
        print(f"Error showing table info: {e}")

if __name__ == "__main__":
    print("🚀 Setting up Persistent Learning System Database")
    print("=" * 50)

    # Check database connection
    if not check_database_connection():
        print("Please check your database configuration and try again.")
        sys.exit(1)

    # Create tables
    if create_learning_tables():
        show_table_info()
        print("🎯 Database setup complete! Your agents now have persistent memory.")
    else:
        print("❌ Database setup failed.")
        sys.exit(1)