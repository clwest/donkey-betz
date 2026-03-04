/**
 * VIP Demo Mode — curated data for investor/VIP demos.
 * All timestamps are relative to "now" so the app always looks fresh.
 */

function ago(minutes: number): string {
  return new Date(Date.now() - minutes * 60_000).toISOString();
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export const DEMO_BODY_SUMMARY = {
  overall_health: 'Healthy',
  health_score: 94,
  healthy_systems: 8,
  total_systems: 9,
  systems: {
    heart: { status: 'healthy', emoji: '\u2764\ufe0f' },
    lungs: { status: 'healthy', emoji: '\ud83e\udec1' },
    brain: { status: 'healthy', emoji: '\ud83e\udde0' },
    spine: { status: 'healthy', emoji: '\ud83e\uddb4' },
    immune: { status: 'healthy', emoji: '\ud83d\udee1\ufe0f' },
    circulatory: { status: 'healthy', emoji: '\ud83e\ude78' },
    muscular: { status: 'healthy', emoji: '\ud83d\udcaa' },
    digestive: { status: 'warning', emoji: '\ud83e\uddea' },
    skin: { status: 'healthy', emoji: '\ud83e\udda0' },
  },
  alert_count: 0,
};

export const DEMO_ATTENTION_STATS = {
  total_items: 12,
  pending_count: 3,
  by_urgency: { critical: 0, high: 1, medium: 2, low: 9 },
  by_status: { pending: 3, resolved: 9 },
  by_item_type: { decision: 2, alert: 1, insight: 9 },
};

export const DEMO_GOVERNANCE_STATS = {
  total_decisions: 48,
  draft_count: 3,
  approved_count: 38,
  rejected_count: 2,
  promoted_count: 5,
  pending_review_count: 3,
  by_impact_area: {},
  by_decision_type: {},
};

export const DEMO_INITIATIVES = [
  { id: 'demo-1', name: 'Content Monetization Pipeline', status: 'ACTIVE', current_stage: 'execution', progress: 72, created_at: ago(4320) },
  { id: 'demo-2', name: 'Sports Analytics v2 Launch', status: 'ACTIVE', current_stage: 'validation', progress: 55, created_at: ago(10080) },
  { id: 'demo-3', name: 'Multi-Platform Distribution', status: 'ACTIVE', current_stage: 'research', progress: 30, created_at: ago(2880) },
  { id: 'demo-4', name: 'SEC Filing Intelligence', status: 'COMPLETED', current_stage: 'completed', progress: 100, created_at: ago(20160) },
];

export const DEMO_ACTIVITY = {
  activities: [
    { type: 'agent', icon: '\ud83e\udd16', title: 'ResearchAgent completed market analysis', subtitle: 'NVDA sector deep-dive', timestamp: ago(8) },
    { type: 'spider', icon: '\ud83d\udd77\ufe0f', title: 'SEC Filing Spider detected new 10-K', subtitle: 'AAPL annual report filed', timestamp: ago(22) },
    { type: 'content', icon: '\ud83d\udcdd', title: 'Blog published: "AI in Sports Betting"', subtitle: '1,240 words, quality 0.89', timestamp: ago(45) },
    { type: 'betting', icon: '\ud83c\udfb0', title: 'Wager settled: Lakers -3.5 (WIN)', subtitle: '+$120 profit', timestamp: ago(90) },
    { type: 'stock', icon: '\ud83d\udcc8', title: 'Stock alert: TSLA breakout signal', subtitle: 'Confidence 78%, bullish', timestamp: ago(120) },
    { type: 'governance', icon: '\ud83d\udce5', title: 'Decision approved: Enable new spider cluster', subtitle: 'Auto-approved by policy', timestamp: ago(180) },
  ],
  counts: { agent: 34, spider: 156, content: 8, betting: 12, stock: 22 },
  total: 232,
};

export const DEMO_DASHBOARD_STATS = {
  total_revenue: 4820,
  active_opportunities: 14,
  success_rate: 73,
  active_agents: 72,
  spider_data_points: 15420,
  agent_executions_24h: 342,
};

// ── Betting ───────────────────────────────────────────────────────────────────

export const DEMO_BETTING_STATS = {
  total_wagers: 87,
  total_stake: 4350,
  total_profit_loss: 1285,
  wins: 48,
  losses: 31,
  pushes: 3,
  pending: 5,
  win_rate: 60.8,
  roi: 29.5,
  current_streak: 3,
  longest_win_streak: 7,
  longest_loss_streak: 4,
  singles_record: { wins: 38, losses: 24, profit: 920 },
  parlays_record: { wins: 10, losses: 7, profit: 365 },
  stats_by_sport: {
    basketball: { wins: 22, losses: 12, profit: 580 },
    football: { wins: 15, losses: 10, profit: 420 },
    baseball: { wins: 11, losses: 9, profit: 285 },
  },
  last_updated: ago(5),
};

export const DEMO_WAGERS = [
  { id: 'dw-1', type: 'single', bet_type: 'spread', pick: 'Lakers -3.5', odds: -110, stake: 100, potential_payout: 191, status: 'won', profit_loss: 91, result_amount: 191, created_at: ago(120), placed_at: ago(120), settled_at: ago(90), legs: [], game_id: 'g1', sport: 'basketball', matchup: 'Lakers vs Celtics' },
  { id: 'dw-2', type: 'single', bet_type: 'moneyline', pick: 'Yankees ML', odds: +135, stake: 50, potential_payout: 117, status: 'won', profit_loss: 67, result_amount: 117, created_at: ago(300), placed_at: ago(300), settled_at: ago(240), legs: [], game_id: 'g2', sport: 'baseball', matchup: 'Yankees vs Red Sox' },
  { id: 'dw-3', type: 'single', bet_type: 'over_under', pick: 'Over 224.5', odds: -105, stake: 75, potential_payout: 146, status: 'pending', profit_loss: null, result_amount: null, created_at: ago(30), placed_at: ago(30), settled_at: null, legs: [], game_id: 'g3', sport: 'basketball', matchup: 'Warriors vs Nuggets' },
  { id: 'dw-4', type: 'parlay', bet_type: 'parlay', pick: '3-leg parlay', odds: +620, stake: 25, potential_payout: 180, status: 'pending', profit_loss: null, result_amount: null, created_at: ago(60), placed_at: ago(60), settled_at: null, legs: [
    { event_id: 'e1', sport: 'basketball', matchup: 'Heat vs Bucks', market_type: 'spread', pick: 'Heat +4.5', odds: -110, line: 4.5, bookmaker: 'DraftKings', status: 'pending', final_score: '' },
    { event_id: 'e2', sport: 'basketball', matchup: 'Suns vs Mavs', market_type: 'moneyline', pick: 'Suns ML', odds: +120, line: null, bookmaker: 'FanDuel', status: 'pending', final_score: '' },
    { event_id: 'e3', sport: 'baseball', matchup: 'Dodgers vs Padres', market_type: 'moneyline', pick: 'Dodgers ML', odds: -140, line: null, bookmaker: 'BetMGM', status: 'pending', final_score: '' },
  ], game_id: '', sport: 'multi', matchup: '3-leg parlay' },
  { id: 'dw-5', type: 'single', bet_type: 'spread', pick: 'Chiefs -7', odds: -110, stake: 100, potential_payout: 191, status: 'lost', profit_loss: -100, result_amount: 0, created_at: ago(1440), placed_at: ago(1440), settled_at: ago(1380), legs: [], game_id: 'g5', sport: 'football', matchup: 'Chiefs vs Bills' },
];

export const DEMO_GAMES = [
  { event_id: 'dg-1', sport_key: 'basketball_nba', sport_name: 'NBA', commence_time: ago(-60), home_team: 'Golden State Warriors', away_team: 'Denver Nuggets', home_score: null, away_score: null, completed: false, predicted_winner: 'Golden State Warriors', period: null, clock: null, status_detail: 'Scheduled' },
  { event_id: 'dg-2', sport_key: 'basketball_nba', sport_name: 'NBA', commence_time: ago(-120), home_team: 'Miami Heat', away_team: 'Milwaukee Bucks', home_score: null, away_score: null, completed: false, predicted_winner: 'Milwaukee Bucks', period: null, clock: null, status_detail: 'Scheduled' },
  { event_id: 'dg-3', sport_key: 'baseball_mlb', sport_name: 'MLB', commence_time: ago(-180), home_team: 'LA Dodgers', away_team: 'San Diego Padres', home_score: null, away_score: null, completed: false, predicted_winner: 'LA Dodgers', period: null, clock: null, status_detail: 'Scheduled' },
];

export const DEMO_ARBITRAGE = [
  { event: 'Warriors vs Nuggets', sport: 'basketball_nba', profit_percent: 2.3, bookmakers: [
    { name: 'DraftKings', odds: +145, pick: 'Warriors ML' },
    { name: 'BetMGM', odds: -135, pick: 'Nuggets ML' },
  ], expires_at: ago(-45) },
];

export const DEMO_TRACK_RECORD = {
  total_predictions: 156,
  correct: 98,
  incorrect: 58,
  accuracy: 62.8,
  by_sport: {
    basketball: { total: 68, correct: 45, accuracy: 66.2 },
    football: { total: 42, correct: 27, accuracy: 64.3 },
    baseball: { total: 46, correct: 26, accuracy: 56.5 },
  },
};

// ── Stocks ────────────────────────────────────────────────────────────────────

export const DEMO_STOCK_HUB = {
  success: true,
  stats: {
    total_briefs: 24,
    total_alerts: 47,
    total_predictions: 82,
    accuracy_7d: 68.5,
    accuracy_30d: 64.2,
    sec_filings_count: 156,
  },
  latest_brief: {
    id: 'db-1',
    brief_date: ago(120),
    executive_summary: 'Markets showing broad strength with tech leading. NVDA up 4.2% on AI infrastructure demand. Defensive sectors underperforming as risk appetite improves.',
    total_stocks_analyzed: 42,
    debate_zone_count: 5,
    situation_health: 'bullish',
  },
  top_alerts: [
    { id: 'da-1', alert_type: 'breakout', symbol: 'NVDA', company_name: 'NVIDIA Corp', sector: 'Technology', title: 'Breakout above $950 resistance', summary: 'NVDA broke through key resistance on high volume. AI capex cycle accelerating.', bull_case: 'AI infrastructure spend continues to grow 40% YoY', bear_case: 'Valuation stretched at 35x forward P/E', confidence_score: 82, bull_score: 85, bear_score: 45, current_price: 962.50, price_change_24h: 4.2, recommended_action: 'BUY', bookmarked: true, detected_at: ago(30) },
    { id: 'da-2', alert_type: 'momentum', symbol: 'AAPL', company_name: 'Apple Inc', sector: 'Technology', title: 'Strong momentum after earnings', summary: 'Services revenue beat estimates by 8%. iPhone shipments stable.', bull_case: 'Services margin expansion to 74%', bear_case: 'China iPhone demand softening', confidence_score: 71, bull_score: 72, bear_score: 55, current_price: 228.30, price_change_24h: 1.8, recommended_action: 'HOLD', bookmarked: false, detected_at: ago(90) },
    { id: 'da-3', alert_type: 'value', symbol: 'GOOGL', company_name: 'Alphabet Inc', sector: 'Technology', title: 'Undervalued on AI search fears', summary: 'Trading at discount to peers despite strong cloud growth and Gemini momentum.', bull_case: 'Cloud revenue growing 28% with improving margins', bear_case: 'Search market share risk from AI competitors', confidence_score: 76, bull_score: 78, bear_score: 52, current_price: 178.45, price_change_24h: -0.4, recommended_action: 'BUY', bookmarked: false, detected_at: ago(150) },
  ],
  top_predictions: [
    { id: 'dp-1', ticker: 'NVDA', prediction_type: 'bullish', conviction_level: 'high', predicted_move: 8.5, price_at_prediction: 920, prediction_date: ago(4320), actual_move_7_days: 4.6, was_correct_7_days: true },
    { id: 'dp-2', ticker: 'TSLA', prediction_type: 'bearish', conviction_level: 'medium', predicted_move: -5.2, price_at_prediction: 248, prediction_date: ago(2880), actual_move_7_days: -3.1, was_correct_7_days: true },
    { id: 'dp-3', ticker: 'AAPL', prediction_type: 'bullish', conviction_level: 'medium', predicted_move: 3.8, price_at_prediction: 222, prediction_date: ago(1440), actual_move_7_days: null, was_correct_7_days: null },
  ],
  market_news: [
    { spider_name: 'MarketWatchSpider', source: 'MarketWatch', title: 'Fed signals potential rate cut in Q2', description: 'Federal Reserve Chair indicates inflation trajectory supports easing.', link: '', published: ago(45), category: 'macro' },
    { spider_name: 'SECFilingSpider', source: 'SEC', title: 'AAPL files 10-K annual report', description: 'Apple annual filing reveals record services revenue.', link: '', published: ago(180), category: 'filing' },
  ],
  sec_recent: [
    { title: 'AAPL 10-K Annual Report', description: 'Annual report for fiscal year 2025', link: '', published: ago(180), filing_type: '10-K' },
    { title: 'MSFT 8-K Current Report', description: 'Azure AI partnership announcement', link: '', published: ago(360), filing_type: '8-K' },
  ],
};

// ── Portfolio ─────────────────────────────────────────────────────────────────

export const DEMO_REVENUE = {
  total: 4820,
  this_month: 1240,
  last_month: 980,
  pending: 320,
  by_platform: { 'Sports Betting': 1285, 'Content': 1840, 'Stock Alerts': 1695 },
};

export const DEMO_PORTFOLIO_STATS = {
  total_revenue: 4820,
  platforms: 5,
  connected: 4,
  distributions: 23,
};

export const DEMO_PLATFORMS = [
  { id: 'dp-1', name: 'Substack', slug: 'substack', description: 'Newsletter monetization', status: 'active', connected: true },
  { id: 'dp-2', name: 'Medium', slug: 'medium', description: 'Long-form content', status: 'active', connected: true },
  { id: 'dp-3', name: 'Gumroad', slug: 'gumroad', description: 'Digital products', status: 'active', connected: true },
  { id: 'dp-4', name: 'Patreon', slug: 'patreon', description: 'Subscription content', status: 'active', connected: true },
  { id: 'dp-5', name: 'YouTube', slug: 'youtube', description: 'Video content', status: 'setup', connected: false },
];

export const DEMO_DISTRIBUTIONS = [
  { id: 'dd-1', title: 'AI Sports Betting Weekly Brief', content_type: 'newsletter', status: 'published', platform: 'Substack', created_at: ago(120) },
  { id: 'dd-2', title: 'Market Intelligence Report: Tech Sector', content_type: 'article', status: 'published', platform: 'Medium', created_at: ago(360) },
  { id: 'dd-3', title: 'Stock Alert Template Pack', content_type: 'digital_product', status: 'published', platform: 'Gumroad', created_at: ago(1440) },
  { id: 'dd-4', title: 'March Betting Playbook', content_type: 'guide', status: 'draft', platform: 'Substack', created_at: ago(60) },
];

export const DEMO_RECOMMENDATIONS = [
  { platform: { id: 'dp-1', name: 'Substack', type: 'newsletter', commission: 0 }, recommendation_type: 'expand', confidence_score: 88, suggested_price: 12, reasoning: 'Your betting analysis content has high engagement. A premium tier could generate $500+/month.', estimated_revenue_potential: 500 },
  { platform: { id: 'dp-3', name: 'Gumroad', type: 'marketplace', commission: 5 }, recommendation_type: 'new_product', confidence_score: 75, suggested_price: 29, reasoning: 'Package your stock alert methodology into a digital course.', estimated_revenue_potential: 1200 },
];

export const DEMO_INTEGRATIONS = [
  { id: 'di-1', platform: 'Substack', status: 'active' as const, last_sync: ago(15), connected_at: ago(43200) },
  { id: 'di-2', platform: 'Medium', status: 'active' as const, last_sync: ago(60), connected_at: ago(30240) },
  { id: 'di-3', platform: 'Gumroad', status: 'active' as const, last_sync: ago(120), connected_at: ago(20160) },
  { id: 'di-4', platform: 'Patreon', status: 'active' as const, last_sync: ago(30), connected_at: ago(14400) },
];

export const DEMO_COMPARISONS = [
  { platform: 'Substack', revenue: 1840, growth_percent: 24, items_count: 12 },
  { platform: 'Gumroad', revenue: 1695, growth_percent: 18, items_count: 5 },
  { platform: 'Medium', revenue: 965, growth_percent: 8, items_count: 6 },
  { platform: 'Patreon', revenue: 320, growth_percent: null, items_count: 3 },
];
