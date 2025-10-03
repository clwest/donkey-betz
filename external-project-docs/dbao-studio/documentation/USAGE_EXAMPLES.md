# DBAO SDK Usage Examples

This document provides comprehensive usage examples for both the TypeScript and Python SDKs of the Donkey Betz Agent Orchestra system.

## Table of Contents
- [Installation](#installation)
- [TypeScript SDK](#typescript-sdk)
- [Python SDK](#python-sdk)
- [NCAAF Examples](#ncaaf-examples)
- [Agent Orchestra](#agent-orchestra)
- [Sports Analytics](#sports-analytics)
- [Odds Conversion](#odds-conversion)
- [WebSocket Integration](#websocket-integration)

## Installation

### TypeScript
```bash
# Install dependencies
npm install axios ws

# Import the SDK
import { DBAO, OddsClient, SportsClient, AgentOrchestra } from './sdk/ts/tools'
```

### Python
```bash
# Install dependencies
pip install requests websocket-client

# Import the SDK
from sdk.py.tools import DBAO, SportsClient, AgentOrchestra, ApiError
```

## TypeScript SDK

### Basic Initialization

```typescript
import { DBAO } from './sdk/ts/tools';

// Basic initialization
const dbao = new DBAO({ 
  baseUrl: 'http://localhost:8000' 
});

// With authentication
const dbao = DBAO.withToken('your-api-token');

// For development
const dbao = DBAO.dev();
```

### Sports Data Access

```typescript
// Get all supported leagues
const leagues = await dbao.sports.getLeagues();
console.log('Supported leagues:', leagues);

// Get NCAAF games for today
const ncaafGames = await dbao.sports.getNCAACFGames();
console.log('NCAAF games:', ncaafGames);

// Get games with filters
const games = await dbao.sports.getGames({
  league: 'NCAAF',
  date: '2025-09-06',
  limit: 10
});

// Get markets for a specific game
const markets = await dbao.sports.getMarkets({
  game_id: 'game-uuid',
  kind: 'moneyline',
  detailed: true
});
```

### NCAAF Line Ingestion

```typescript
// Ingest NCAAF moneyline
await dbao.sports.ingestNCAAFMoneyline(
  'ncaaf_2025_week1_alabama_georgia',
  'Georgia Bulldogs',
  'Alabama Crimson Tide',
  -150, // Georgia home odds
  +130, // Alabama away odds
  '2025-09-06T19:00:00Z'
);

// Ingest NCAAF spread
await dbao.sports.ingestNCAAFSpread(
  'ncaaf_2025_week1_alabama_georgia',
  'Georgia Bulldogs',
  'Alabama Crimson Tide',
  -3.5, // Georgia spread
  3.5,  // Alabama spread
  -110, // Georgia odds
  -110, // Alabama odds
  '2025-09-06T19:00:00Z'
);

// Ingest NCAAF total
await dbao.sports.ingestNCAAFTotal(
  'ncaaf_2025_week1_alabama_georgia',
  'Georgia Bulldogs', 
  'Alabama Crimson Tide',
  55.5, // Total points
  -110, // Over odds
  -110, // Under odds
  '2025-09-06T19:00:00Z'
);
```

### Odds Conversion

```typescript
// Convert American odds to all formats
const conversion = await dbao.odds.convertOdds({
  odds: '-110',
  from_format: 'american'
});
console.log('Decimal:', conversion.decimal); // 1.91
console.log('Implied probability:', conversion.implied_probability); // 0.524

// Kelly criterion calculation
const kelly = await dbao.odds.kellycriterion({
  odds: '-110',
  odds_format: 'american',
  true_probability: 0.58,
  bankroll: 5000,
  kelly_multiplier: 0.25
});
console.log('Recommended stake:', kelly.recommended_stake);
console.log('Kelly percentage:', kelly.kelly_percentage);
```

### Agent Orchestration

```typescript
// Execute single agent
const execution = await dbao.orchestra.executeAgent({
  agent_type: 'research',
  task_description: 'Analyze NCAAF betting trends for Week 1'
});

// Multi-agent workflow
const orchestration = await dbao.orchestra.businessAnalysisWorkflow(
  'NCAAF betting market opportunities'
);

// Get agent suggestions
const suggestions = await dbao.orchestra.suggestAgent({
  task_description: 'I need help analyzing player props for NCAAF'
});
console.log('Recommended agent:', suggestions.top_recommendation);
```

## Python SDK

### Basic Initialization

```python
from sdk.py.tools import DBAO

# Basic initialization
dbao = DBAO(base_url='http://localhost:8000')

# With authentication
dbao = DBAO.with_token('your-api-token')

# From environment variables
dbao = DBAO.from_env()
```

### Sports Data Access

```python
# Get all supported leagues
leagues = await dbao.sports.get_leagues()
print('Supported leagues:', leagues)

# Get NCAAF games
ncaaf_games = await dbao.sports.get_ncaaf_games('2025-09-06')
print(f'Found {len(ncaaf_games)} NCAAF games')

# Get games with filters
games = await dbao.sports.get_games({
    'league': 'NCAAF',
    'date': '2025-09-06',
    'limit': 10
})

# Get markets
markets = await dbao.sports.get_markets({
    'league': 'NCAAF',
    'kind': 'moneyline',
    'detailed': True
})
```

### NCAAF Line Ingestion

```python
# Ingest NCAAF moneyline
await dbao.sports.ingest_ncaaf_moneyline(
    game_external_id='ncaaf_2025_week1_alabama_georgia',
    home_team='Georgia Bulldogs',
    away_team='Alabama Crimson Tide',
    home_odds=-150,
    away_odds=130,
    start_time='2025-09-06T19:00:00Z'
)

# Ingest NCAAF spread
await dbao.sports.ingest_ncaaf_spread(
    game_external_id='ncaaf_2025_week1_alabama_georgia',
    home_team='Georgia Bulldogs',
    away_team='Alabama Crimson Tide',
    home_spread=-3.5,
    away_spread=3.5,
    home_odds=-110,
    away_odds=-110,
    start_time='2025-09-06T19:00:00Z'
)
```

### Agent Orchestration

```python
from sdk.py.tools import ExecuteAgentRequest, OrchestrationRequest

# Execute single agent
execution = dbao.orchestra.execute_agent(ExecuteAgentRequest(
    agent_type='research',
    task_description='Analyze NCAAF betting trends for Week 1'
))

# Multi-agent workflow
orchestration = dbao.orchestra.business_analysis_workflow(
    'NCAAF betting market opportunities'
)

# Wait for completion
completed_instance = dbao.orchestra.execute_and_wait(
    agent_type='financial',
    task_description='Calculate NCAAF betting ROI projections',
    max_wait=300
)
print('Results:', completed_instance.result)
```

## NCAAF Examples

### Complete NCAAF Game Setup

```typescript
// TypeScript
const gameData = {
  league: 'NCAAF',
  book: 'DraftKings',
  game_external_id: 'ncaaf_2025_week1_alabama_georgia',
  kind: 'moneyline',
  game_meta: {
    home_team: 'Georgia Bulldogs',
    away_team: 'Alabama Crimson Tide',
    start_time: '2025-09-06T19:00:00Z',
    venue: 'Sanford Stadium',
    week: 1
  },
  lines: [
    { side: 'home', price_american: -150 },
    { side: 'away', price_american: 130 }
  ]
};

const result = await dbao.sports.ingestLines(gameData);
console.log('Game created:', result.game_id);
```

```python
# Python  
game_data = {
    'league': 'NCAAF',
    'book': 'DraftKings', 
    'game_external_id': 'ncaaf_2025_week1_alabama_georgia',
    'kind': 'moneyline',
    'game_meta': {
        'home_team': 'Georgia Bulldogs',
        'away_team': 'Alabama Crimson Tide',
        'start_time': '2025-09-06T19:00:00Z',
        'venue': 'Sanford Stadium',
        'week': 1
    },
    'lines': [
        {'side': 'home', 'price_american': -150},
        {'side': 'away', 'price_american': 130}
    ]
}

result = await dbao.sports.ingest_lines(game_data)
print(f'Game created: {result["game_id"]}')
```

### NCAAF Analytics Workflow

```typescript
// Get week 1 NCAAF games and analyze them
const week1Games = await dbao.sports.getGames({
  league: 'NCAAF',
  date: '2025-09-06'
});

for (const game of week1Games) {
  // Get markets for this game
  const markets = await dbao.sports.getNCAACFMarkets(game.id, true);
  
  // Analyze with agent
  const analysis = await dbao.orchestra.executeAgent({
    agent_type: 'research',
    task_description: `Analyze betting value for ${game.away_team.name} @ ${game.home_team.name}`,
    context: { 
      game_id: game.id, 
      league: 'NCAAF',
      markets: markets 
    }
  });
  
  console.log(`Analysis for ${game.away_team.name} @ ${game.home_team.name}:`, analysis.instance_id);
}
```

## WebSocket Integration

### TypeScript WebSocket

```typescript
// Connect to sports updates
const ws = dbao.orchestra.connectWebSocket({
  onOpen: () => {
    console.log('Connected to DBAO WebSocket');
  },
  onMessage: (message) => {
    if (message.type === 'sports.update') {
      console.log('Sports update:', message.league, message.game_info);
    }
  },
  onError: (error) => {
    console.error('WebSocket error:', error);
  }
});

// Subscribe to specific instance updates
dbao.orchestra.subscribeToInstance(ws, execution.instance_id);
```

### Python WebSocket

```python
def handle_message(message):
    if message.get('type') == 'sports.update':
        print(f"Sports update: {message['league']} - {message['game_info']}")

def handle_error(error):
    print(f"WebSocket error: {error}")

# Connect to WebSocket
ws_client = dbao.orchestra.connect_websocket({
    'onMessage': handle_message,
    'onError': handle_error
})

# Subscribe to instance updates
dbao.orchestra.subscribe_to_instance(ws_client, execution.instance_id)
```

## Error Handling

### TypeScript

```typescript
try {
  const result = await dbao.odds.convertOdds({
    odds: 'invalid',
    from_format: 'american'
  });
} catch (error) {
  if (error.response?.status === 400) {
    console.error('Invalid odds format:', error.message);
  } else {
    console.error('API error:', error);
  }
}
```

### Python

```python
from sdk.py.tools import ApiError

try:
    result = await dbao.client.get('/api/v1/sports/games/')
except ApiError as e:
    if e.status == 404:
        print('Endpoint not found')
    else:
        print(f'API error {e.status}: {e}')
except Exception as e:
    print(f'Unexpected error: {e}')
```

## Complete Example: NCAAF Betting Analysis

```typescript
// Complete NCAAF betting analysis workflow
async function analyzeNCAAFWeek() {
  const dbao = DBAO.dev();
  
  // 1. Get current NCAAF games
  const games = await dbao.sports.getGames({
    league: 'NCAAF',
    date: new Date().toISOString().split('T')[0],
    limit: 20
  });
  
  console.log(`Found ${games.length} NCAAF games`);
  
  // 2. For each game, get markets and analyze
  const analyses = [];
  
  for (const game of games) {
    // Get detailed markets
    const markets = await dbao.sports.getMarkets({
      game_id: game.id,
      detailed: true
    });
    
    // Run multi-agent analysis
    const analysis = await dbao.orchestra.businessAnalysisWorkflow(
      `Comprehensive betting analysis for ${game.away_team.name} @ ${game.home_team.name}`
    );
    
    analyses.push({
      game: game,
      markets: markets,
      analysis_id: analysis.orchestration_id
    });
  }
  
  // 3. Convert odds and calculate Kelly for top opportunities
  for (const gameAnalysis of analyses) {
    for (const market of gameAnalysis.markets) {
      if (market.kind === 'moneyline') {
        for (const line of market.lines || []) {
          // Convert odds
          const conversion = await dbao.odds.convertOdds({
            odds: line.price_american.toString(),
            from_format: 'american'
          });
          
          // Calculate Kelly (assuming 55% win probability)
          const kelly = await dbao.odds.quickKelly(
            line.price_american.toString(),
            'american',
            0.55,
            5000,  // $5000 bankroll
            0.25   // 25% fractional Kelly
          );
          
          if (kelly.recommended_stake > 50) {
            console.log(`Opportunity: ${gameAnalysis.game.away_team.name} @ ${gameAnalysis.game.home_team.name}`);
            console.log(`Side: ${line.side}, Odds: ${line.price_american}, Stake: $${kelly.recommended_stake}`);
          }
        }
      }
    }
  }
  
  return analyses;
}

// Run the analysis
analyzeNCAAFWeek().then(results => {
  console.log('Analysis complete:', results.length, 'games analyzed');
}).catch(error => {
  console.error('Analysis failed:', error);
});
```

This completes the comprehensive usage examples for both TypeScript and Python SDKs, with special emphasis on NCAAF functionality and the newly synchronized endpoints.