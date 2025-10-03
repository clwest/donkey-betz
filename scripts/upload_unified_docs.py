#!/usr/bin/env python3
"""
Upload Unified Donkey Betz Documentation to Database
ONLY processes unified-donkey-betz files - keeps /docs/ intact
"""

import os
import sys
import json
from pathlib import Path
import openai
import psycopg2
from psycopg2.extras import execute_values
import time

# Add pgvector if available
try:
    from pgvector.psycopg2 import register_vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    print("⚠️  pgvector not available - install with: pip install pgvector")

PROJECT_ROOT = Path('/Users/donkeyking/development/unified-donkey-betz')
ANALYSIS_DIR = PROJECT_ROOT / 'scripts/doc_analysis'

def load_inventory():
    """Load unified-donkey-betz inventory"""
    inventory_file = ANALYSIS_DIR / 'unified_inventory.json'

    if not inventory_file.exists():
        print(f"❌ Run clean_unified_docs.py first!")
        print(f"   Expected: {inventory_file}")
        sys.exit(1)

    with open(inventory_file, 'r') as f:
        return json.load(f)

def chunk_content(content: str, max_tokens: int = 1000) -> list:
    """Split content into chunks"""
    max_chars = max_tokens * 4
    chunks = []
    start = 0

    while start < len(content):
        end = min(start + max_chars, len(content))

        # Try to break at sentence
        if end < len(content):
            search_start = int(end * 0.8)
            for char in ['.', '!', '?', '\n\n']:
                pos = content.rfind(char, search_start, end)
                if pos > 0:
                    end = pos + 1
                    break

        chunk_text = content[start:end].strip()
        if chunk_text:
            chunks.append({
                'text': chunk_text,
                'index': len(chunks)
            })

        start = end

    return chunks

def prepare_docs_for_embedding(inventory):
    """Prepare unified docs for embedding"""
    print("📋 Preparing unified-donkey-betz documents...")

    prepared = []

    for doc in inventory:
        try:
            with open(doc['path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            chunks = chunk_content(content)

            for chunk in chunks:
                prepared.append({
                    'file_path': doc['path'],
                    'relative_path': doc['relative_path'],
                    'title': doc['title'],
                    'category': doc['category'],
                    'chunk_index': chunk['index'],
                    'total_chunks': len(chunks),
                    'text': chunk['text'],
                    'project': 'unified-donkey-betz',  # CRITICAL: Project identifier
                    'metadata': {
                        'filename': doc['filename'],
                        'size_kb': doc['size_kb'],
                        'modified': doc['modified']
                    }
                })

        except Exception as e:
            print(f"   ⚠️  Error: {doc['path']}: {e}")

    print(f"   ✅ Prepared {len(prepared)} chunks from {len(inventory)} files")
    return prepared

def generate_embeddings(prepared_docs, batch_size=20):
    """Generate embeddings using OpenAI"""
    print(f"\n🧠 Generating embeddings...")

    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set")
        sys.exit(1)

    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    embeddings = []
    texts = [doc['text'] for doc in prepared_docs]
    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in range(0, len(texts), batch_size):
        batch_num = i // batch_size + 1
        batch = texts[i:i+batch_size]

        print(f"   Batch {batch_num}/{total_batches} ({len(batch)} texts)...", end=' ')

        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            print(f"✅")
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ {e}")
            embeddings.extend([None] * len(batch))

    # Combine with docs
    embedded_docs = []
    for doc, embedding in zip(prepared_docs, embeddings):
        if embedding:
            doc['embedding'] = embedding
            embedded_docs.append(doc)

    return embedded_docs

def get_db_connection():
    """Get database connection"""
    db_config = {
        'dbname': os.getenv('DB_NAME', 'unified_donkey_betz'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }

    try:
        conn = psycopg2.connect(**db_config)
        if PGVECTOR_AVAILABLE:
            register_vector(conn)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def setup_database(conn):
    """Create table and indexes"""
    print("\n🔧 Setting up database...")

    cursor = conn.cursor()

    # Create extension
    if PGVECTOR_AVAILABLE:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unified_documentation (
            id SERIAL PRIMARY KEY,
            project VARCHAR(100) DEFAULT 'unified-donkey-betz',
            file_path TEXT NOT NULL,
            relative_path TEXT,
            title TEXT,
            content TEXT NOT NULL,
            embedding vector(1536),
            category VARCHAR(50),
            chunk_index INTEGER DEFAULT 0,
            total_chunks INTEGER DEFAULT 1,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    print("   ✅ Table 'unified_documentation' ready")

    # Create indexes
    indexes = [
        ("CREATE INDEX IF NOT EXISTS unified_docs_project_idx ON unified_documentation(project)"),
        ("CREATE INDEX IF NOT EXISTS unified_docs_category_idx ON unified_documentation(category)"),
        ("CREATE INDEX IF NOT EXISTS unified_docs_path_idx ON unified_documentation(relative_path)"),
    ]

    if PGVECTOR_AVAILABLE:
        indexes.append(
            """CREATE INDEX IF NOT EXISTS unified_docs_embedding_idx
               ON unified_documentation
               USING hnsw (embedding vector_cosine_ops)
               WITH (m = 16, ef_construction = 64)"""
        )

    for idx_sql in indexes:
        cursor.execute(idx_sql)

    conn.commit()
    print("   ✅ Indexes created")
    cursor.close()

def upload_docs(conn, embedded_docs, batch_size=100):
    """Upload to database"""
    print(f"\n📤 Uploading {len(embedded_docs)} chunks...")

    cursor = conn.cursor()

    data = []
    for doc in embedded_docs:
        data.append((
            'unified-donkey-betz',  # project
            doc['file_path'],
            doc['relative_path'],
            doc['title'],
            doc['text'],
            doc.get('embedding'),
            doc['category'],
            doc['chunk_index'],
            doc['total_chunks'],
            json.dumps(doc['metadata'])
        ))

    total_batches = (len(data) + batch_size - 1) // batch_size

    for i in range(0, len(data), batch_size):
        batch_num = i // batch_size + 1
        batch = data[i:i+batch_size]

        print(f"   Batch {batch_num}/{total_batches} ({len(batch)} rows)...", end=' ')

        try:
            execute_values(
                cursor,
                """
                INSERT INTO unified_documentation
                (project, file_path, relative_path, title, content, embedding,
                 category, chunk_index, total_chunks, metadata)
                VALUES %s
                """,
                batch
            )
            conn.commit()
            print("✅")

        except Exception as e:
            conn.rollback()
            print(f"❌ {e}")

    cursor.close()
    print("   ✅ Upload complete!")

def verify_upload(conn):
    """Verify uploaded data"""
    print("\n🔍 Verifying upload...")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM unified_documentation
        WHERE project = 'unified-donkey-betz'
    """)
    count = cursor.fetchone()[0]
    print(f"   • Total chunks: {count:,}")

    cursor.execute("""
        SELECT category, COUNT(*) FROM unified_documentation
        WHERE project = 'unified-donkey-betz'
        GROUP BY category
        ORDER BY COUNT(*) DESC
    """)

    print("\n   By Category:")
    for category, cnt in cursor.fetchall():
        print(f"      • {category}: {cnt:,}")

    cursor.close()

def main():
    """Main execution"""
    print("=" * 70)
    print("📤 Unified Donkey Betz Documentation Upload")
    print("=" * 70)
    print("\n⚠️  PROJECT ISOLATION:")
    print("   ✅ ONLY unified-donkey-betz files")
    print("   ✅ /docs/ directory untouched")
    print("   ✅ Other projects excluded\n")

    # 1. Load inventory
    inventory = load_inventory()
    print(f"   Loaded {len(inventory)} files")

    # 2. Prepare docs
    prepared_docs = prepare_docs_for_embedding(inventory)

    # 3. Estimate cost
    total_tokens = sum(len(d['text']) // 4 for d in prepared_docs)
    cost = (total_tokens / 1000) * 0.00002
    print(f"\n💰 Cost Estimate:")
    print(f"   • Chunks: {len(prepared_docs):,}")
    print(f"   • Tokens: ~{total_tokens:,}")
    print(f"   • Cost: ~${cost:.2f}")

    response = input("\n❓ Generate embeddings? (yes/no): ").strip().lower()
    if response != 'yes':
        print("   Cancelled")
        return

    # 4. Generate embeddings
    embedded_docs = generate_embeddings(prepared_docs)

    # 5. Save to file
    embeddings_file = ANALYSIS_DIR / 'unified_embeddings.json'
    with open(embeddings_file, 'w') as f:
        json.dump(embedded_docs, f, indent=2)
    print(f"\n💾 Saved embeddings: {embeddings_file}")

    # 6. Upload to database
    response = input("\n❓ Upload to database? (yes/no): ").strip().lower()
    if response != 'yes':
        print("   Cancelled - embeddings saved for later")
        return

    conn = get_db_connection()
    if not conn:
        return

    setup_database(conn)
    upload_docs(conn, embedded_docs)
    verify_upload(conn)

    conn.close()

    print("\n" + "=" * 70)
    print("✅ UPLOAD COMPLETE")
    print("=" * 70)
    print(f"\n📊 Results:")
    print(f"   • Project: unified-donkey-betz ONLY")
    print(f"   • Chunks uploaded: {len(embedded_docs):,}")
    print(f"   • Table: unified_documentation")
    print(f"   • /docs/ directory: UNTOUCHED ✅")
    print(f"\n🔍 Search with:")
    print(f"   SELECT * FROM unified_documentation")
    print(f"   WHERE project = 'unified-donkey-betz'")
    print(f"   AND category = 'agents';")

if __name__ == "__main__":
    main()
