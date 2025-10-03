# 🚀 ML Setup Guide & Requirements

## ✅ Completed Implementation

### 1. **ML Models Django App Created**
- ✅ Created `ml_models` Django app with comprehensive models
- ✅ PostgreSQL models with pgvector support
- ✅ Training data storage and model versioning
- ✅ Vector embeddings for similarity search
- ✅ User personalization support

### 2. **ML Infrastructure**
- ✅ Feature extraction utilities
- ✅ Model training scripts (CNN-LSTM and Lightweight models)
- ✅ TensorFlow Lite conversion for mobile deployment
- ✅ Admin interface for model management

### 3. **Database Schema**
- ✅ `MLTrainingData` - Store sensor data for training
- ✅ `MLModelVersion` - Track model versions and performance
- ✅ `SensorEmbedding` - Vector embeddings with pgvector
- ✅ `MLUserModel` - Personalized models per user
- ✅ `MLInferenceMetric` - Track inference performance
- ✅ `WorkoutPattern` - Learned activity patterns

## 🔧 Setup Requirements

### 1. **PostgreSQL Installation**

#### macOS:
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install pgvector
brew install pgvector
```

#### Ubuntu/Debian:
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# Install pgvector
sudo apt install postgresql-15-pgvector
```

### 2. **Database Setup**

Run the provided setup script:
```bash
cd backend
chmod +x setup_postgres.sh
./setup_postgres.sh
```

Or manually:
```sql
-- Create database
CREATE DATABASE moveyourazz_ml;
CREATE USER moveyourazz_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE moveyourazz_ml TO moveyourazz_user;

-- Connect to database and enable pgvector
\c moveyourazz_ml
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. **Environment Configuration**

Add to `.env`:
```
DATABASE_URL=postgresql://moveyourazz_user:${DB_PASSWORD}@localhost:5432/moveyourazz_ml
DB_PASSWORD=your_secure_password
```

### 4. **Install Python Dependencies**

```bash
pip install -r requirements.txt
```

### 5. **Run Migrations**

```bash
python manage.py makemigrations ml_models
python manage.py migrate
```

## ❓ Questions & Answers

### Q1: Should we use a managed PostgreSQL service?
**Recommendation**: 
- **Development**: Local PostgreSQL is fine
- **Production**: Use managed service (AWS RDS, Google Cloud SQL, or Supabase)
- **Benefits**: Automatic backups, scaling, monitoring, security patches

### Q2: What's the preferred PostgreSQL version?
**Answer**: PostgreSQL 15+ is recommended
- Supports latest pgvector features
- Better performance for vector operations
- Enhanced security features

### Q3: Database naming convention preference?
**Current Convention**:
- Database: `moveyourazz_ml`
- Tables: Django default (app_modelname)
- Indexes: Descriptive names with operation type

### Q4: GPU availability for training?
**Options**:
1. **Local GPU**: NVIDIA GPU with CUDA support
2. **Cloud GPU**: Google Colab, AWS EC2 P3 instances
3. **CPU Training**: Possible but slower (current scripts support both)

### Q5: Expected data volume for training?
**Estimates**:
- Initial: 10,000-50,000 samples
- 6 months: 500,000+ samples
- Storage: ~1GB per 100,000 samples

### Q6: Storage requirements?
**Requirements**:
- Models: ~50MB per version
- TFLite models: ~10MB each
- Embeddings: ~1KB per workout
- Total: 10-50GB for first year

### Q7: Model update frequency?
**Recommendation**:
- Base model: Monthly updates
- User models: Weekly fine-tuning
- Real-time: Store data, batch train overnight

### Q8: Federated learning implementation?
**Future Enhancement**:
- Not implemented in current version
- Can add TensorFlow Federated later
- Privacy-preserving on-device training

### Q9: Encryption requirements?
**Current Implementation**:
- Models stored on filesystem
- Database encryption via PostgreSQL
- Add encryption-at-rest if needed

### Q10: Access control for ML endpoints?
**Implemented**:
- JWT authentication required
- User-scoped data access
- Admin-only model management

## 🚦 Next Steps to Complete Setup

### 1. **Install PostgreSQL and pgvector**
```bash
# macOS
brew install postgresql@15 pgvector
brew services start postgresql@15

# Or use Docker
docker run -d \
  --name moveyourazz-postgres \
  -e POSTGRES_DB=moveyourazz_ml \
  -e POSTGRES_USER=moveyourazz_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  ankane/pgvector:latest
```

### 2. **Create Database**
```bash
./setup_postgres.sh
```

### 3. **Update Django Settings**
Already configured to use `DATABASE_URL` from environment

### 4. **Run Migrations**
```bash
python manage.py makemigrations ml_models
python manage.py migrate
```

### 5. **Create Superuser**
```bash
python manage.py createsuperuser
```

### 6. **Train Initial Model**
```bash
cd ml_models
python train_model.py
```

## 🎯 Testing the Setup

### 1. **Check pgvector Installation**
```sql
-- Connect to database
psql -U moveyourazz_user -d moveyourazz_ml

-- Check extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Test vector operations
CREATE TABLE test_vectors (id serial PRIMARY KEY, embedding vector(3));
INSERT INTO test_vectors (embedding) VALUES ('[1,2,3]'), '[4,5,6]');
SELECT embedding <-> '[3,4,5]' AS distance FROM test_vectors;
```

### 2. **Test Django Integration**
```python
python manage.py shell

from ml_models.models import SensorEmbedding
import numpy as np

# Create test embedding
embedding = np.random.rand(128)
print(f"Embedding shape: {embedding.shape}")
```

### 3. **Run Model Training**
```bash
python ml_models/train_model.py
```

## 📊 Performance Optimization

### 1. **pgvector Indexes**
```sql
-- Already configured in models
-- IVFFlat index for large datasets
CREATE INDEX ON sensor_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- HNSW index for better recall (pgvector 0.5.0+)
CREATE INDEX ON sensor_embeddings 
USING hnsw (embedding vector_cosine_ops);
```

### 2. **Connection Pooling**
```python
# In settings.py
DATABASES['default']['CONN_MAX_AGE'] = 600
```

### 3. **Batch Processing**
- Process embeddings in batches of 100
- Use Django's bulk_create for efficiency

## 🐛 Troubleshooting

### Issue: pgvector not found
```bash
# Check installation
psql -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# Reinstall if needed
CREATE EXTENSION vector;
```

### Issue: Memory errors during training
- Reduce batch size in train_model.py
- Use gradient accumulation
- Enable mixed precision training

### Issue: Slow vector searches
- Ensure indexes are created
- Tune index parameters
- Consider dimension reduction

## 🎉 Ready to Go!

Once PostgreSQL is set up with pgvector, the ML system is ready for:
1. Collecting training data from Flutter app
2. Training workout detection models
3. Deploying models to mobile devices
4. Real-time inference with <100ms latency
5. Similarity search for workout patterns

The implementation is modular and can be enhanced progressively based on user feedback and data availability.