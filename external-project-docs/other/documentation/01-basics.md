# Module 1: Platform Basics

## Learning Objectives

By the end of this module, you will be able to:
- Navigate the platform interface
- Understand core concepts
- Perform basic operations
- Configure your workspace

## 1.1 Platform Overview

### What is the Unified Platform?

The Unified AI & Sports Analytics Platform combines:
- **AI Integration**: Multiple AI providers in one interface
- **Sports Analytics**: Advanced betting calculations
- **Real-time Data**: Live updates and monitoring
- **Risk Management**: Optimal betting strategies

### Key Benefits

1. **Unified Interface**: Single point of access
2. **Cost Optimization**: Automatic provider selection
3. **Advanced Analytics**: Mathematical models
4. **Real-time Alerts**: Instant notifications

## 1.2 Core Concepts

### AI Providers

**Definition**: Services that provide AI capabilities (OpenAI, Anthropic)

**Key Features**:
- Text generation
- Embeddings
- Cost tracking
- Automatic failover

### Sports Analytics

**Definition**: Mathematical analysis of betting opportunities

**Key Components**:
- Odds calculation
- Expected value
- Kelly Criterion
- Arbitrage detection

## 1.3 Getting Started

### Step 1: Account Creation

```
1. Navigate to https://platform.com/register
2. Enter email and password
3. Verify email
4. Complete profile
```

### Step 2: Initial Configuration

**Configure AI Settings**:
```python
settings = {
    'default_model': 'gpt-3.5-turbo',
    'temperature': 0.7,
    'max_tokens': 500
}
```

**Set Betting Parameters**:
```python
betting_config = {
    'bankroll': 1000,
    'risk_tolerance': 'medium',
    'max_bet_percentage': 5
}
```

### Step 3: First Operations

#### Your First AI Query

```python
# Simple text generation
response = ai.complete("Explain machine learning")
print(response)
```

#### Your First Odds Calculation

```python
# Convert American to Decimal odds
decimal = convert_odds(-110, 'american', 'decimal')
print(f"Decimal odds: {decimal}")  # Output: 1.909
```

## 1.4 Platform Navigation

### Dashboard Components

```
┌─────────────────────────────────┐
│         Header Menu             │
├────────┬────────────────────────┤
│        │                        │
│  Side  │     Main Content      │
│  Nav   │                        │
│        │                        │
├────────┴────────────────────────┤
│         Status Bar              │
└─────────────────────────────────┘
```

### Key Sections

1. **Dashboard**: Overview and metrics
2. **AI Studio**: AI operations
3. **Sports Analytics**: Betting tools
4. **Reports**: Performance analysis
5. **Settings**: Configuration

## 1.5 Basic Operations

### Using AI Features

#### Example 1: Generate Summary
```python
prompt = "Summarize the benefits of cloud computing in 3 points"
summary = ai.complete(prompt, model='gpt-3.5-turbo')
```

#### Example 2: Compare Models
```python
# Fast, cheap model
quick_response = ai.complete(prompt, model='claude-3-haiku')

# Detailed, expensive model
detailed_response = ai.complete(prompt, model='gpt-4')
```

### Using Sports Analytics

#### Example 1: Calculate Expected Value
```python
# Is this bet worth it?
ev = calculate_ev(
    odds=150,      # +150 underdog
    probability=0.45,  # 45% chance
    stake=100
)
print(f"Expected value: ${ev}")
```

#### Example 2: Find Arbitrage
```python
odds_set = [
    {'book': 'A', 'outcome': 'Team1', 'odds': 120},
    {'book': 'B', 'outcome': 'Team2', 'odds': 110}
]

opportunity = find_arbitrage(odds_set)
if opportunity:
    print("Arbitrage found!")
```

## 1.6 Hands-On Exercises

### Exercise 1: AI Model Comparison

**Task**: Compare responses from different models

```python
prompt = "What are the top 3 programming languages to learn?"

# Try different models
models = ['gpt-3.5-turbo', 'claude-3-haiku', 'gpt-4']

for model in models:
    response = ai.complete(prompt, model=model)
    print(f"{model}: {response[:100]}...")
```

### Exercise 2: Odds Conversion

**Task**: Convert odds between all formats

```python
american_odds = -150

# Convert to decimal
decimal = convert_odds(american_odds, 'american', 'decimal')

# Convert to fractional
fractional = convert_odds(decimal, 'decimal', 'fractional')

print(f"American: {american_odds}")
print(f"Decimal: {decimal}")
print(f"Fractional: {fractional}")
```

### Exercise 3: EV Calculation

**Task**: Determine if bets have value

```python
bets = [
    {'odds': -110, 'probability': 0.55},
    {'odds': 150, 'probability': 0.35},
    {'odds': -200, 'probability': 0.70}
]

for bet in bets:
    ev = calculate_ev(bet['odds'], bet['probability'], 100)
    if ev > 0:
        print(f"Value bet! Odds: {bet['odds']}, EV: ${ev:.2f}")
    else:
        print(f"No value. Odds: {bet['odds']}, EV: ${ev:.2f}")
```

## 1.7 Common Patterns

### Pattern 1: Cost-Effective AI Usage

```python
def smart_ai_query(prompt, complexity='low'):
    """Choose model based on task complexity."""
    if complexity == 'low':
        return ai.complete(prompt, model='claude-3-haiku')
    elif complexity == 'medium':
        return ai.complete(prompt, model='gpt-3.5-turbo')
    else:
        return ai.complete(prompt, model='gpt-4')
```

### Pattern 2: Safe Betting

```python
def safe_bet_size(bankroll, probability, odds):
    """Calculate safe bet using fractional Kelly."""
    kelly = kelly_criterion(bankroll, probability, odds)
    safe_stake = kelly.recommended_stake * 0.25  # Quarter Kelly
    return min(safe_stake, bankroll * 0.02)  # Max 2% of bankroll
```

## 1.8 Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| AI timeout | Large request | Reduce max_tokens |
| Invalid odds | Wrong format | Check input format |
| No arbitrage found | Efficient market | Try more bookmakers |
| High costs | Using GPT-4 | Switch to GPT-3.5 |

## 1.9 Best Practices

### DO's
✅ Start with small bets
✅ Use appropriate AI models
✅ Track all operations
✅ Set budget limits
✅ Verify calculations

### DON'Ts
❌ Bet more than 5% per wager
❌ Use GPT-4 for simple tasks
❌ Ignore error messages
❌ Skip verification steps
❌ Chase losses

## 1.10 Knowledge Check

### Quiz Questions

1. **What is the decimal equivalent of -110 odds?**
   - a) 1.810
   - b) 1.909 ✓
   - c) 2.100
   - d) 0.909

2. **Which model is most cost-effective for simple tasks?**
   - a) GPT-4
   - b) GPT-3.5 Turbo
   - c) Claude 3 Haiku ✓
   - d) Claude 3 Opus

3. **What does positive EV indicate?**
   - a) Guaranteed win
   - b) Long-term profitability ✓
   - c) Low risk
   - d) High odds

## Module Summary

You've learned:
- Platform navigation and setup
- Basic AI operations
- Fundamental sports analytics
- Common patterns and best practices

## Next Steps

1. Complete the exercises
2. Practice with real examples
3. Move to [Module 2: AI Providers](./02-ai-providers.md)

---

*Questions? Visit the [FAQ](../faq.md) or contact support@platform.com*