#!/usr/bin/env python3
"""
Upload Sports Betting Knowledge to the Personal Knowledge Base
"""
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "993f8273f70877e23b5c7d2f92ed30562a089fe3"

# Sports Betting Knowledge Documents
BETTING_KNOWLEDGE = [
    {
        "title": "AI-Powered Sports Betting: Introduction",
        "description": "Introduction to using AI agents for sports betting analysis",
        "raw_content": """# AI-Powered Sports Betting: The Complete Guide

## Chapter 1: Introduction to AI in Sports Betting

The integration of artificial intelligence into sports betting has revolutionized how we analyze games and make betting decisions. With over 100 specialized AI agents at your disposal, you can now process vast amounts of data and identify profitable betting opportunities that human analysis might miss.

### Key AI Advantages:
- **Speed**: Process thousands of data points in seconds
- **Consistency**: No emotional bias or fatigue
- **Pattern Recognition**: Identify complex correlations humans cannot see
- **24/7 Availability**: Continuous monitoring of line movements and opportunities

### The 100+ Agent Arsenal
Our platform provides specialized agents for every aspect of sports betting:
- Kelly Criterion calculators for optimal bet sizing
- Line movement analyzers to track sharp money
- Arbitrage hunters for risk-free opportunities
- Bankroll management specialists
- Weather impact analyzers
- Injury report processors

### Getting Started
To leverage AI for sports betting success:
1. Understand your risk tolerance
2. Set up proper bankroll management
3. Learn to interpret agent recommendations
4. Start with small bets to validate strategies
5. Scale up as you gain confidence""",
        "document_type": "betting_analysis",
        "category": "sports-betting",
        "tags": ["ai", "sports-betting", "introduction", "agents"],
        "is_public": True,
        "source": "upload"
    },
    {
        "title": "Kelly Criterion: Mathematical Foundation of Bankroll Management",
        "description": "Complete guide to Kelly Criterion for optimal bet sizing",
        "raw_content": """# The Kelly Criterion: Mathematical Foundation of Professional Betting

## Understanding the Kelly Formula

The Kelly Criterion is the mathematical foundation of professional bankroll management. It calculates the optimal bet size based on your edge and the odds offered.

### The Formula:
```
f = (bp - q) / b
```
Where:
- f = fraction of bankroll to bet
- b = decimal odds - 1
- p = probability of winning
- q = probability of losing (1-p)

### Practical Application

**Example 1: Positive EV Bet**
- Your estimated win probability: 55%
- Odds offered: -110 (1.91 decimal)
- Kelly calculation: f = (0.91 × 0.55 - 0.45) / 0.91 = 5.5%
- Recommended bet: 5.5% of bankroll

### Fractional Kelly

Professional bettors rarely use full Kelly due to variance. Common approaches:
- **Quarter Kelly (25%)**: Very conservative, minimal risk
- **Half Kelly (50%)**: Balanced approach
- **Three-Quarter Kelly (75%)**: Aggressive but manageable

### Risk Management

Kelly Criterion advantages:
- Mathematically optimal growth rate
- Automatic scaling with bankroll
- Built-in risk protection
- Prevents total ruin

### Common Mistakes to Avoid
1. Overestimating your edge
2. Not accounting for simultaneous bets
3. Ignoring correlation between bets
4. Using full Kelly with uncertain probabilities""",
        "document_type": "betting_analysis",
        "category": "sports-betting",
        "tags": ["kelly-criterion", "bankroll", "mathematics", "risk-management"],
        "is_public": True,
        "source": "upload"
    },
    {
        "title": "Line Movement Analysis: Following the Sharp Money",
        "description": "How to track and interpret betting line movements",
        "raw_content": """# Line Movement Analysis: Following the Sharp Money

## Understanding Line Movement

Line movement is one of the most powerful indicators in sports betting. It reveals where professional money is flowing and can help identify value opportunities.

### Types of Line Movement

**1. Steam Moves**
- Rapid, coordinated line movement across multiple books
- Usually indicates sharp action
- Often occurs close to game time

**2. Reverse Line Movement**
- Line moves opposite to public betting percentages
- Strong indicator of sharp money
- Example: 70% of bets on Team A, but line moves toward Team B

**3. Line Freezes**
- Books refuse to move lines despite heavy action
- Indicates books are confident in their position
- Often means sharp money is on the other side

### Tracking Sharp vs Public Money

**Public Money Indicators:**
- High betting percentages (>70%)
- Popular teams and primetime games
- Emotional betting after big wins/losses

**Sharp Money Indicators:**
- Line movement against public percentages
- Early week movement (Sunday night to Tuesday)
- Consistent movement across all books

### Using Our Line Movement Agent

Our AI analyzes:
- Real-time odds from 50+ sportsbooks
- Betting percentage data
- Historical line movement patterns
- Sharp bettor tracking

### Actionable Strategies

1. **Fade the Public**: Bet against heavy public action
2. **Follow Steam**: Quick action on steam moves
3. **Buy on Bad News**: Lines often overreact to injuries/news
4. **Shop for Value**: Use line discrepancies between books""",
        "document_type": "betting_analysis",
        "category": "sports-betting",
        "tags": ["line-movement", "sharp-money", "betting-strategy", "analysis"],
        "is_public": True,
        "source": "upload"
    },
    {
        "title": "AI Agent Integration: Maximizing Your Betting Edge",
        "description": "How to effectively use multiple AI agents together",
        "raw_content": """# AI Agent Integration: Maximizing Your Betting Edge

## Orchestrating Multiple Agents

The true power of AI betting comes from combining multiple specialized agents to create a comprehensive analysis system.

### Agent Combination Strategies

**1. The Statistical Trinity**
- Odds Calculation Agent: Find value in lines
- Kelly Criterion Agent: Determine bet size
- Bankroll Manager Agent: Track and protect capital

**2. The Information Pipeline**
- News Scraper Agent: Gather latest updates
- Injury Analysis Agent: Assess impact
- Weather Forecast Agent: Environmental factors
- Synthesis Agent: Combine all inputs

**3. The Arbitrage Hunter**
- Multi-book Scanner: Find price discrepancies
- Arbitrage Calculator: Determine stakes
- Execution Agent: Place bets quickly

### Real-World Example

**NFL Game Analysis Workflow:**
1. Line Movement Agent detects sharp action
2. Statistical Analysis Agent evaluates teams
3. Weather Agent checks conditions
4. Injury Agent assesses player availability
5. Kelly Agent calculates optimal stake
6. Execution Agent places the bet

### Agent Communication

Our platform enables agents to:
- Share data in real-time
- Trigger cascading analyses
- Validate each other's findings
- Provide consensus recommendations

### Best Practices

1. **Start Simple**: Begin with 2-3 core agents
2. **Add Gradually**: Introduce new agents as you learn
3. **Monitor Performance**: Track each agent's contribution
4. **Adjust Weights**: Fine-tune agent influence based on results
5. **Stay Informed**: Understand what each agent is doing

### Advanced Techniques

**Multi-Agent Voting Systems**
- Agents vote on betting decisions
- Weighted voting based on historical accuracy
- Consensus threshold for bet execution

**Confidence Scoring**
- Each agent provides confidence level
- Aggregate confidence determines bet size
- Low confidence = smaller bets or pass""",
        "document_type": "betting_analysis",
        "category": "sports-betting",
        "tags": ["ai-agents", "integration", "strategy", "orchestration"],
        "is_public": True,
        "source": "upload"
    }
]

def upload_documents():
    """Upload all betting knowledge documents"""
    
    headers = {
        "Authorization": f"Token {AUTH_TOKEN}"
    }
    
    success_count = 0
    
    for doc in BETTING_KNOWLEDGE:
        print(f"\n📚 Uploading: {doc['title']}")
        
        # Create multipart form data
        files = {
            'title': (None, doc['title']),
            'description': (None, doc['description']),
            'content': (None, doc['raw_content']),
            'document_type': (None, doc['document_type']),
            'category': (None, doc['category']),
            'tags': (None, json.dumps(doc['tags'])),
            'is_public': (None, str(doc['is_public'])),
            'source': (None, doc['source'])
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/content/documents/",
                headers=headers,
                files=files
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully uploaded: {doc['title']}")
                success_count += 1
            else:
                print(f"❌ Failed to upload: {doc['title']}")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error uploading {doc['title']}: {str(e)}")
    
    print(f"\n🎯 Upload Summary: {success_count}/{len(BETTING_KNOWLEDGE)} documents uploaded successfully")
    
    # List knowledge bases
    print("\n📖 Available Knowledge Bases:")
    try:
        kb_response = requests.get(
            f"{API_BASE_URL}/api/v1/content/knowledge-bases/",
            headers=headers
        )
        if kb_response.ok:
            kbs = kb_response.json()
            for kb in kbs.get('results', []):
                print(f"   - {kb['name']}: {kb['document_count']} documents")
    except Exception as e:
        print(f"   Error fetching knowledge bases: {e}")

if __name__ == "__main__":
    print("🚀 Starting Sports Betting Knowledge Upload...")
    upload_documents()
    print("\n✨ Done! Your AI Sports Betting knowledge base is ready!")
    print("📱 Visit http://localhost:3001/knowledge to view your documents")