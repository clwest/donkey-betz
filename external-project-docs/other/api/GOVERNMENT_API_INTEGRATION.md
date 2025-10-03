# Government & Legislative API Integration

## 🏛️ Overview

The Government API Integration provides powerful legislative intelligence capabilities, allowing businesses to:
- Track bills and regulations that could impact their operations
- Find government contract opportunities matching their capabilities
- Predict legislative outcomes and prepare for regulatory changes
- Analyze trends in government activity by sector

## 🚀 Quick Start

```python
# Basic bill search
from agent_orchestra.services.government_api_service import GovernmentAPIService

gov_service = GovernmentAPIService()
bills = await gov_service.search_bills(
    query="artificial intelligence",
    states=['US'],  # Federal only
    limit=10
)

# Business opportunity analysis
from agent_orchestra.services.legislative_ml_service import LegislativeMLService

leg_ml = LegislativeMLService()
opportunities = await leg_ml.analyze_legislative_opportunity(
    business_description="AI-powered healthcare analytics platform",
    sectors=["Healthcare", "Technology"],
    states=['US']  # or ['CA', 'NY'] for specific states
)
```

## 📊 Data Sources

### 1. LegiScan API
- **Coverage**: All 50 states + federal legislation
- **Features**: Bill text, sponsors, progress tracking, votes
- **API Key**: `LEGISCAN_API_KEY` in `.env`

### 2. Congress.gov API
- **Coverage**: Federal legislation only
- **Features**: Detailed bill information, committee actions, member data
- **API Key**: `GOVERNMENT_API_KEY` in `.env`

### 3. Federal Register API
- **Coverage**: Federal regulations and rules
- **Features**: Proposed rules, final rules, notices, executive orders
- **No API key required** (public API)

### 4. SAM.gov (simulated)
- **Coverage**: Federal contract opportunities
- **Features**: Active solicitations, set-asides, agency information
- **Note**: Currently using realistic mock data

## 🧠 ML Features Extracted

### Bill Analysis
```python
{
    'progress_score': 0.45,      # 0-1 score of legislative progress
    'momentum_score': 0.72,      # Recent activity indicator
    'bipartisan_score': 0.85,    # Cross-party support metric
    'sponsor_count': 23,         # Number of sponsors
    'affected_industries': ['Technology', 'Healthcare'],
    'implementation_probability': 0.65
}
```

### Regulation Analysis
```python
{
    'impact_score': 0.8,         # Potential business impact
    'compliance_burden': 'high', # Estimated compliance effort
    'comment_sentiment': 0.3,    # Public comment analysis
    'effective_date': '2025-03-01',
    'affected_industries': ['Financial Services']
}
```

### Contract Opportunities
```python
{
    'match_score': 0.87,         # Capability match score
    'competition_level': 'medium',
    'set_asides': ['Small Business'],
    'certifications_required': ['ISO 27001'],
    'value_range': '$1M - $5M'
}
```

## 🔮 Vector Embeddings

The system uses pgvector for semantic search and pattern matching:

### Legislative Bill Embeddings
- **Dimensions**: 1536 (OpenAI standard)
- **Fields**: title_embedding, summary_embedding
- **Use Cases**: Find similar bills, track legislative patterns

### Regulatory Document Embeddings
- **Dimensions**: 1536
- **Fields**: title_embedding, abstract_embedding
- **Use Cases**: Regulation impact analysis, compliance tracking

### Government Contract Embeddings
- **Dimensions**: 1536
- **Fields**: description_embedding
- **Use Cases**: Match company capabilities to opportunities

## 📈 Key Services

### GovernmentAPIService
Main service for fetching government data:

```python
# Search bills
bills = await gov_service.search_bills(
    query="cybersecurity",
    states=['CA', 'NY', 'TX'],  # or ['US'] for federal
    status="passed",            # introduced, passed, enacted, vetoed
    year=2025,
    limit=50
)

# Search regulations
regulations = await gov_service.search_regulations(
    query="data privacy",
    document_type="rule",       # rule, proposed_rule, notice
    agencies=["FTC", "SEC"],
    limit=20
)

# Search contracts
contracts = await gov_service.search_contracts(
    keywords="software development",
    agencies=["DoD", "VA"],
    set_asides=["Small Business", "8(a)"],
    limit=30
)
```

### LegislativeMLService
Advanced ML analysis for business intelligence:

```python
# Analyze business opportunities/threats
analysis = await leg_ml.analyze_legislative_opportunity(
    business_description="Your business description",
    sectors=["Your", "Sectors"],
    states=['US']  # or specific states
)

# Returns:
{
    'opportunities': [
        {
            'bill_id': 'HR-1234',
            'title': 'AI Innovation Act',
            'description': 'Funding opportunities for AI research',
            'value_estimate': 1000000,
            'confidence': 0.85
        }
    ],
    'threats': [...],
    'compliance_requirements': [...],
    'recommendations': [...]
}

# Predict bill outcomes
prediction = await leg_ml.predict_bill_outcome("HR-1234")
# Returns: passage_probability, timeline, key_factors

# Find matching contracts
contracts = await leg_ml.find_contract_opportunities(
    company_capabilities="We provide AI/ML solutions...",
    certifications=["ISO 27001", "CMMI-3"],
    target_agencies=["DoD", "HHS"]
)

# Analyze regulatory trends
trends = await leg_ml.analyze_regulatory_trends(
    sectors=["Technology", "Healthcare"],
    lookback_days=90
)
```

## 🔌 Integration with Enhanced Tools

The government APIs are integrated into the agent tools system:

```python
from agent_orchestra.enhanced_tools import EnhancedAgentTools

# Congress API
bills = await EnhancedAgentTools.congress_api(
    query="artificial intelligence",
    limit=10
)

# Federal Register
regulations = await EnhancedAgentTools.federal_register(
    query="fintech",
    document_type="rule"
)

# Government Contracts
contracts = await EnhancedAgentTools.gov_contracts_api(
    query="technology services",
    agency="Department of Defense"
)
```

## 🎯 Use Cases

### 1. Compliance Monitoring
Track new regulations affecting your industry:
```python
# Set up alerts for your sectors
regulations = await gov_service.search_regulations(
    query=" ".join(your_keywords),
    agencies=relevant_agencies,
    limit=50
)

# Analyze compliance requirements
for reg in regulations['documents']:
    if reg['ml_features']['impact_score'] > 0.7:
        # High impact regulation - needs attention
        compliance_analysis = await leg_ml.analyze_regulation_impact(
            reg, your_business_description
        )
```

### 2. Government Sales Opportunities
Find and pursue government contracts:
```python
# Find matching opportunities
opportunities = await leg_ml.find_contract_opportunities(
    company_capabilities=your_capabilities,
    certifications=your_certs,
    target_agencies=preferred_agencies
)

# Get detailed analysis for top matches
for opp in opportunities[:5]:
    if opp['match_score'] > 0.8:
        # Strong match - prepare proposal
        detailed = await gov_service.get_contract_details(
            opp['opportunity_id']
        )
```

### 3. Strategic Planning
Monitor legislative trends affecting your industry:
```python
# Analyze sector trends
trends = await leg_ml.analyze_regulatory_trends(
    sectors=your_sectors,
    lookback_days=180
)

if trends['trend'] == 'accelerating':
    # Increasing regulatory activity
    # Plan for compliance resources
    
# Track specific bills
for bill_id in bills_to_watch:
    outcome = await leg_ml.predict_bill_outcome(bill_id)
    if outcome['passage_probability'] > 0.7:
        # Likely to pass - prepare for impact
```

## 🔧 Configuration

### Required API Keys
Add to your `.env` file:
```bash
# LegiScan - State and federal bills
LEGISCAN_API_KEY=your_legiscan_key

# Congress.gov - Federal legislation
GOVERNMENT_API_KEY=your_congress_key

# Optional - for enhanced features
OPENAI_API_KEY=your_openai_key  # For embeddings
```

### Database Setup
Run migrations for vector models:
```bash
python manage.py makemigrations agent_orchestra
python manage.py migrate
```

## 📊 Testing

Test the integration:
```bash
# Test all government APIs
python test_government_api.py

# Test specific service
python -c "
import asyncio
from agent_orchestra.services.government_api_service import GovernmentAPIService

async def test():
    service = GovernmentAPIService()
    result = await service.search_bills('AI', ['US'], limit=5)
    print(result)

asyncio.run(test())
"
```

## 🚀 Future Enhancements

1. **Real-time Alerts**: WebSocket notifications for legislative changes
2. **Lobbying Data**: Track lobbying activity on relevant bills
3. **State-specific Analysis**: Deeper integration with state legislatures
4. **Voting Predictions**: ML models for member voting patterns
5. **Regulation Comments**: Automated analysis of public comments
6. **Contract Win Probability**: ML scoring for contract pursuit decisions

## 💡 Pro Tips

1. **Combine Data Sources**: Cross-reference bills with news sentiment
2. **Set Up Alerts**: Use LegislativeAlert model for automated monitoring
3. **Track Competitors**: Monitor government contracts won by competitors
4. **Regulatory Calendar**: Build compliance timeline from effective dates
5. **Historical Analysis**: Use vector similarity to find precedent legislation

## 🆘 Troubleshooting

### API Returns Mock Data
- Check if API keys are configured in `.env`
- Verify `is_configured()` returns True
- Check API rate limits

### Vector Search Not Working
- Ensure pgvector extension is installed
- Run migrations: `python manage.py migrate`
- Check embedding dimensions (should be 1536)

### ML Features Missing
- Verify OpenAI API key is set (for embeddings)
- Check service initialization in logs
- Ensure all required fields are populated