# User Guide

Comprehensive guide for using the Unified AI & Sports Analytics Platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [AI Features](#ai-features)
3. [Sports Analytics](#sports-analytics)
4. [Advanced Features](#advanced-features)
5. [Troubleshooting](#troubleshooting)

## Getting Started

### Account Setup

1. **Create an Account**
   - Navigate to the registration page
   - Provide email and password
   - Verify your email address

2. **Configure API Keys** (Optional)
   - Go to Settings → API Keys
   - Add your OpenAI or Anthropic keys
   - Save configuration

3. **Set Preferences**
   - Choose default AI model
   - Set betting bankroll
   - Configure risk tolerance

### Dashboard Overview

The main dashboard provides:
- Quick stats and metrics
- Recent activity
- Active alerts
- System status

## AI Features

### Using AI Completions

#### Basic Text Generation

Generate text for various purposes:

```python
# Example: Generate a summary
prompt = "Summarize the key points of machine learning"
response = ai.get_completion(prompt)
```

#### Choosing Models

Select the best model for your needs:

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| GPT-3.5 Turbo | General tasks | Fast | Low |
| GPT-4 | Complex reasoning | Slower | High |
| Claude 3 Haiku | Quick responses | Very Fast | Very Low |
| Claude 3 Sonnet | Balanced tasks | Fast | Medium |

#### Advanced Parameters

Fine-tune responses with parameters:

- **Temperature** (0.0-1.0): Controls randomness
  - 0.0: Deterministic, focused
  - 0.7: Balanced creativity
  - 1.0: Maximum creativity

- **Max Tokens**: Limit response length
  - Short: 50-150 tokens
  - Medium: 150-500 tokens
  - Long: 500+ tokens

### Cost Management

Monitor and control AI costs:

1. **View Usage**
   - Dashboard → AI Usage
   - See daily/monthly spend
   - Track by model

2. **Set Budgets**
   - Settings → Budget Limits
   - Daily limit: $10
   - Monthly limit: $200

3. **Optimize Costs**
   - Use cheaper models when possible
   - Cache frequent requests
   - Batch similar queries

## Sports Analytics

### Odds Analysis

#### Understanding Odds Formats

**American Odds**
- Negative (-110): Bet $110 to win $100
- Positive (+150): Bet $100 to win $150

**Decimal Odds**
- 1.91: Total return = stake × 1.91
- Includes original stake

**Fractional Odds**
- 10/11: Win $10 for every $11 bet
- Traditional UK format

#### Converting Between Formats

Use the odds converter:
```python
# American to Decimal
decimal = convert_odds(-110, 'american', 'decimal')
# Result: 1.909

# Decimal to Fractional
fractional = convert_odds(2.5, 'decimal', 'fractional')
# Result: 3/2
```

### Expected Value (EV)

Calculate if a bet has positive expected value:

```python
# Your assessment: 55% chance of winning
# Odds: -110
ev = calculate_ev(
    odds=-110,
    win_probability=0.55,
    stake=100
)

if ev > 0:
    print(f"Positive EV: ${ev:.2f}")
else:
    print(f"Negative EV: ${ev:.2f}")
```

**EV Interpretation:**
- Positive EV: Long-term profitable
- Negative EV: Long-term loss
- 0 EV: Break-even

### Kelly Criterion Betting

Optimize bet sizing for maximum growth:

#### Full Kelly
Maximum growth but high variance:
```python
kelly = kelly_criterion(
    bankroll=1000,
    win_probability=0.55,
    odds=-110
)
# Might recommend 5% of bankroll
```

#### Fractional Kelly
Reduced variance, smoother growth:
```python
# Quarter Kelly (25% of full Kelly)
kelly = fractional_kelly(
    bankroll=1000,
    win_probability=0.55,
    odds=-110,
    fraction=0.25
)
# Recommends 1.25% of bankroll
```

#### Risk Levels

| Strategy | Risk | Variance | Growth |
|----------|------|----------|---------|
| Full Kelly | High | High | Maximum |
| Half Kelly | Medium | Medium | Good |
| Quarter Kelly | Low | Low | Steady |
| Fixed 2% | Very Low | Very Low | Slow |

### Arbitrage Detection

Find risk-free profit opportunities:

1. **Single Market Arbitrage**
   ```python
   odds_set = [
       {'book': 'A', 'outcome': 'Team1', 'odds': 120},
       {'book': 'B', 'outcome': 'Team2', 'odds': 110}
   ]
   
   opportunity = find_arbitrage(odds_set)
   if opportunity:
       print(f"Arbitrage! ROI: {opportunity.roi}%")
   ```

2. **Optimal Stakes**
   The system calculates exact stakes:
   - Total investment: $1000
   - Stake on Team1: $476.19
   - Stake on Team2: $523.81
   - Guaranteed profit: $23.81

### Parlay Calculations

#### Standard Parlay
Combine multiple bets:
```python
legs = [
    {'odds': -110, 'description': 'Lakers -5.5'},
    {'odds': 150, 'description': 'Over 220.5'},
    {'odds': -105, 'description': 'Celtics ML'}
]

parlay = calculate_parlay(legs, stake=100)
print(f"Parlay odds: {parlay.combined_odds}")
print(f"Potential payout: ${parlay.payout:.2f}")
```

#### Round Robin
Generate all combinations:
```python
# 3 teams, 2-team parlays
round_robin = calculate_round_robin(
    legs=legs,
    parlay_size=2,
    stake_per_parlay=10
)
# Creates 3 separate 2-team parlays
```

### Line Movement Analysis

Track odds changes over time:

```python
movement = track_line_movement(
    opening_line=-110,
    current_line=-105,
    time_elapsed=24
)

if movement.volume_indicator == "heavy":
    print("Sharp money detected!")
```

**Indicators:**
- **Heavy**: Major sharp action
- **Moderate**: Notable movement
- **Light**: Normal fluctuation

## Advanced Features

### AI-Enhanced Sports Analysis

Combine AI with traditional analytics:

```python
game_analysis = analyze_with_ai({
    'home_team': 'Lakers',
    'away_team': 'Celtics',
    'home_odds': -110,
    'away_odds': -110,
    'recent_form': {...}
})

print(f"AI Confidence: {game_analysis.confidence}%")
print(f"Key Factors: {game_analysis.factors}")
```

### Real-time Monitoring

#### WebSocket Connections
```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://api/ws/odds/');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Odds update:', data);
};
```

#### Arbitrage Alerts
Set up automatic notifications:
1. Settings → Alerts
2. Enable "Arbitrage Opportunities"
3. Set minimum ROI threshold
4. Choose notification method

### Performance Tracking

Monitor your betting performance:

```python
history = get_bet_history()
analysis = analyze_performance(history)

print(f"Win Rate: {analysis.win_rate:.1%}")
print(f"ROI: {analysis.roi:.1%}")
print(f"Current Streak: {analysis.streak}")
```

**Key Metrics:**
- **Win Rate**: Percentage of winning bets
- **ROI**: Return on investment
- **Average Odds**: Typical bet odds
- **Profit/Loss**: Net result

## Best Practices

### Risk Management

1. **Never bet more than 5% on a single wager**
2. **Use fractional Kelly for reduced variance**
3. **Track all bets for analysis**
4. **Set stop-loss limits**

### AI Usage

1. **Choose appropriate models for tasks**
2. **Cache frequent queries**
3. **Monitor costs regularly**
4. **Use temperature settings wisely**

### Sports Betting

1. **Always calculate EV before betting**
2. **Verify arbitrage opportunities quickly**
3. **Consider correlation in parlays**
4. **Track line movements for value**

## Troubleshooting

### Common Issues

#### AI Not Responding
- Check API key configuration
- Verify model availability
- Check rate limits

#### Incorrect Odds Calculations
- Verify input format
- Check for invalid odds (0, -100)
- Ensure proper conversion

#### WebSocket Disconnections
- Check network connectivity
- Verify authentication
- Review firewall settings

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| 401 Unauthorized | Invalid credentials | Check API key |
| 429 Too Many Requests | Rate limit hit | Wait and retry |
| 500 Server Error | System issue | Contact support |

### Getting Help

1. **Documentation**
   - Check this guide
   - Review API docs
   - Read best practices

2. **Support Channels**
   - Email: support@platform.com
   - Discord: [Join Server]
   - GitHub Issues

3. **Community**
   - Forum discussions
   - User examples
   - Tips and tricks

## Glossary

**EV (Expected Value)**: Long-term average outcome of a bet

**Kelly Criterion**: Mathematical formula for optimal bet sizing

**Arbitrage**: Risk-free profit from price differences

**Juice/Vig**: Bookmaker's commission

**CLV (Closing Line Value)**: Beating the closing line

**ROI**: Return on Investment

**Implied Probability**: Probability derived from odds

**No-Vig Odds**: Odds without bookmaker margin

---

*Next: [Developer Guide](./developer-guide.md) →*