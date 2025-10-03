# Vector Embeddings for ML Scoring System

## 🚀 Overview

The Donkey Betz platform extensively uses **pgvector** (PostgreSQL vector extension) for storing and searching vector embeddings. This document explains how we're extending the existing vector infrastructure for enhanced ML scoring.

## 🎯 Current Vector Usage

### Existing Vector Models

1. **ConversationEmbedding** (1536-dim)
   - Stores conversation chunks as vectors
   - Enables semantic search in chat history
   - Powers context retrieval for AI responses

2. **CodeEmbedding** (1536-dim)
   - Powers the Codebase Oracle feature
   - Natural language queries about code
   - "How does authentication work?" → Relevant code snippets

3. **ConversationSegment** (1536-dim)
   - Tracks conversation topics
   - Enables context-aware agent routing
   - Finds similar discussion patterns

### Vector Search Capabilities

```python
# Semantic similarity search using pgvector
from pgvector.django import CosineDistance

similar_items = Model.objects.annotate(
    distance=CosineDistance('embedding', query_embedding)
).order_by('distance')[:10]
```

## 🤖 New ML Scoring Vector Models

### 1. RedditIdeaEmbedding
Stores vector representations of Reddit startup ideas:
- **title_embedding**: 1536-dim vector of post title
- **content_embedding**: 1536-dim vector of post content
- **ML features**: engagement_score, user_credibility, sentiment
- **Outcome tracking**: successful/failed/unknown labels for training

### 2. StockNewsEmbedding
Vector embeddings for financial news:
- **headline_embedding**: 1536-dim vector of news headline
- **content_embedding**: 1536-dim vector of article content
- **Market impact**: price_change_24h, volume_change_24h
- **Sentiment features**: sentiment_score, source_credibility

### 3. CompanyDescriptionEmbedding
Company profiles as vectors:
- **description_embedding**: 1536-dim combined vector
- **Sources**: SEC filings, website, analyst summaries
- **Performance metrics**: revenue_growth, profit_margin
- **Sector classification**: For industry comparisons

### 4. IdeaCompanySimilarity
Pre-computed similarities between ideas and companies:
- **Similarity scores**: title, content, combined
- **Company performance**: market_cap, growth_rate at comparison time
- **Use case**: "This Reddit idea is 87% similar to early Airbnb"

### 5. MLScoringVector
Compressed feature vectors for ML models:
- **feature_vector**: 512-dim compressed representation
- **Predictions**: success_probability, confidence_score
- **Feature importance**: top contributing features
- **Model versioning**: Track which model version scored it

## 📊 ML Features from Vectors

### Reddit Idea Similarity Features
```python
{
    'avg_similarity_to_successful': 0.82,  # How similar to successful ideas
    'avg_similarity_to_failed': 0.45,      # How similar to failed ideas
    'success_failure_ratio': 1.82,         # Ratio of similarities
    'top_similar_success_score': 0.91,     # Closest successful match
    'similar_ideas': [...]                 # List of similar ideas
}
```

### Company Match Features
```python
{
    'avg_similar_company_market_cap': 2.5e9,  # Avg market cap of similar cos
    'avg_similar_company_growth': 0.35,       # Avg growth rate
    'top_company_similarity': 0.78,           # Best company match
    'matched_sectors': ['SaaS', 'B2B'],       # Common sectors
    'similar_companies': [...]                # List of matches
}
```

### News Pattern Features
```python
{
    'avg_similar_news_impact': 2.3,      # Avg price change from similar news
    'similar_news_sentiment': 0.65,      # Avg sentiment of similar news
    'news_pattern_confidence': 0.88,     # How similar to past patterns
    'historical_patterns': [...]         # Past similar events
}
```

## 🔧 Implementation Flow

### 1. Data Ingestion
```python
# When new Reddit post arrives
embedding = await embedding_service.get_embedding(post_text)
reddit_embedding = RedditIdeaEmbedding.objects.create(
    title_embedding=title_emb,
    content_embedding=content_emb,
    engagement_score=calculate_engagement(post)
)
```

### 2. Similarity Calculation
```python
# Find similar successful ideas
similar = RedditIdeaEmbedding.objects.filter(
    outcome_label='successful'
).annotate(
    similarity=CosineDistance('content_embedding', new_embedding)
).order_by('similarity')[:10]
```

### 3. Feature Extraction
```python
# Extract ML features using vector similarities
vector_features = await vector_ml_service.get_reddit_similarity_features(
    idea_text=post.content,
    top_k=10
)
```

### 4. ML Scoring
```python
# Combine all features including vector similarities
all_features = {
    **api_features,      # From NewsAPI, SEC, etc.
    **vector_features,   # From similarity search
    **technical_features # From market data
}

# Create scoring vector
scoring_vector = await vector_ml_service.create_ml_scoring_vector(
    features=all_features,
    entity_type='reddit_idea',
    entity_id=post.id
)

# Get ML prediction
score = ml_model.predict(scoring_vector)
```

## 🚀 Advanced Use Cases

### 1. Pattern Recognition
- "Ideas similar to this one typically grow to $10M market cap"
- "News with this pattern usually causes 3% price movement"
- "Companies with similar descriptions have 75% survival rate"

### 2. Cross-Modal Matching
- Match Reddit ideas to SEC company descriptions
- Compare social sentiment vectors to news sentiment
- Find correlations between idea patterns and market success

### 3. Temporal Evolution
- Track how idea embeddings evolve over time
- Monitor sentiment vector changes in news cycles
- Identify trending concept clusters

### 4. Ensemble Scoring
```python
# Multiple vector-based scores
similarity_score = vector_similarity_to_successful_ideas
company_match_score = similarity_to_unicorn_descriptions  
news_pattern_score = similarity_to_positive_news_patterns

# Weighted ensemble
final_score = (
    0.4 * similarity_score +
    0.3 * company_match_score +
    0.3 * news_pattern_score
)
```

## 📈 Performance Considerations

### Indexing
- pgvector automatically creates indexes for vector columns
- Use `ivfflat` index for large datasets (>1M vectors)
- Optimal settings: `lists = 100` for 1M vectors

### Query Optimization
- Pre-compute common similarities (IdeaCompanySimilarity)
- Use approximate nearest neighbor for speed
- Batch embedding generation for efficiency

### Storage
- 1536-dim float32 vector = ~6KB
- 1M vectors = ~6GB storage
- Consider dimension reduction for archived data

## 🎯 Next Steps

1. **Collect Training Data**
   - Label successful/failed Reddit ideas
   - Track stock performance after news
   - Build outcome datasets

2. **Train Similarity Models**
   - Fine-tune embeddings for startup domain
   - Create sector-specific embeddings
   - Optimize for predictive power

3. **Build ML Pipeline**
   - Real-time embedding generation
   - Similarity feature extraction
   - Model serving infrastructure

4. **Advanced Features**
   - Multi-modal embeddings (text + images)
   - Temporal embedding sequences
   - Cross-lingual support

## 🔮 Future Vision

The vector embedding system transforms Donkey Betz into a **semantic intelligence platform** that understands:
- What makes ideas similar to successful startups
- How news patterns predict market movements
- Which Reddit discussions lead to real businesses
- When social sentiment aligns with market opportunity

By combining **30+ APIs** with **semantic vector search**, we're building the most sophisticated opportunity scoring system in the market.