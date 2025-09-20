# Fix for UI Fallback Deployment to Include Real-Time Odds

## The Issue
When the main orchestration fails, the UI falls back to individual agent deployment but doesn't include betting odds data. This causes agents to give generic analysis instead of specific betting recommendations.

## The Solution
Update the frontend's `BettingAgentPanel.tsx` to fetch and include odds data in the fallback deployment.

## Changes Needed in `frontend/src/components/betting/BettingAgentPanel.tsx`

### 1. Add a function to fetch markets (around line 600):

```typescript
const fetchGameMarkets = async (gameId: string) => {
  try {
    const response = await fetch(`/api/odds/markets/${gameId}/`);
    if (response.ok) {
      const data = await response.json();
      return data.markets || [];
    }
  } catch (error) {
    console.error('Failed to fetch markets:', error);
  }
  return [];
};
```

### 2. Update `executeAgentWithGameContext` to include odds (around line 604):

```typescript
const executeAgentWithGameContext = async (agent: Agent, customTask?: string) => {
  // Fetch current odds
  const markets = await fetchGameMarkets(game.id);
  
  let oddsContext = '';
  if (markets.length > 0) {
    oddsContext = '\n\nCURRENT BETTING LINES:';
    
    // Find spread market
    const spreadMarket = markets.find(m => m.market_type === 'spreads');
    if (spreadMarket && spreadMarket.current_lines?.length > 0) {
      const line = spreadMarket.current_lines[0];
      oddsContext += `\n• Spread: ${game.home_team_name} ${line.home_spread} (${line.home_odds})`;
    }
    
    // Find totals market
    const totalMarket = markets.find(m => m.market_type === 'totals');
    if (totalMarket && totalMarket.current_lines?.length > 0) {
      const line = totalMarket.current_lines[0];
      oddsContext += `\n• Total: ${line.total_line} O/U (${line.over_odds}/${line.under_odds})`;
    }
    
    // Find moneyline market
    const mlMarket = markets.find(m => m.market_type === 'moneyline');
    if (mlMarket && mlMarket.current_lines?.length > 0) {
      const line = mlMarket.current_lines[0];
      oddsContext += `\n• Moneyline: ${game.home_team_name} ${line.home_odds}, ${game.away_team_name} ${line.away_odds}`;
    }
  }
  
  const gameContext = `
Game Context:
- Matchup: ${game.away_team_name} @ ${game.home_team_name}
- League: ${game.league}
- Date: ${new Date(game.scheduled_start).toLocaleDateString()}
- Time: ${new Date(game.scheduled_start).toLocaleTimeString()}
- Venue: ${game.venue_name || 'TBD'}
- Season: ${game.season || 'Current'}
${game.week ? `- Week: ${game.week}` : ''}
${oddsContext}

Task: ${customTask || `Analyze this ${game.league} matchup between ${game.away_team_name} and ${game.home_team_name}. Provide betting insights using the exact odds provided above.`}
`;

  // Rest of the function remains the same...
```

### 3. Also update the input_data passed to executeAgent (around line 627):

```typescript
// Parse odds from the context for input_data
let marketsData = {};
if (markets.length > 0) {
  const spreadMarket = markets.find(m => m.market_type === 'spreads');
  const totalMarket = markets.find(m => m.market_type === 'totals');
  const mlMarket = markets.find(m => m.market_type === 'moneyline');
  
  marketsData = {
    spread: spreadMarket?.current_lines?.[0] ? {
      line: spreadMarket.current_lines[0].home_spread,
      home_spread: spreadMarket.current_lines[0].home_spread,
      home_odds: spreadMarket.current_lines[0].home_odds,
      away_spread: spreadMarket.current_lines[0].away_spread,
      away_odds: spreadMarket.current_lines[0].away_odds
    } : null,
    total: totalMarket?.current_lines?.[0] ? {
      line: totalMarket.current_lines[0].total_line,
      over_odds: totalMarket.current_lines[0].over_odds,
      under_odds: totalMarket.current_lines[0].under_odds
    } : null,
    moneyline: mlMarket?.current_lines?.[0] ? {
      home_odds: mlMarket.current_lines[0].home_odds,
      away_odds: mlMarket.current_lines[0].away_odds
    } : null
  };
}

await executeAgent(
  agent.name.toLowerCase().replace(/\s+/g, '-'),
  gameContext,
  {
    game_id: game.id,
    home_team: game.home_team_name,
    away_team: game.away_team_name,
    league: game.league,
    markets: marketsData  // Add this line
  }
);
```

## Result
With these changes, when the UI falls back to individual agent deployment, it will:
1. Fetch the current betting markets for the game
2. Include the odds in the task description (Alabama -16.5, O/U 54.5, etc.)
3. Pass the odds data in the input_data
4. Agents will provide specific betting analysis instead of generic responses