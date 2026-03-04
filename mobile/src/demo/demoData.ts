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

// ── Agents ────────────────────────────────────────────────────────────────────

export const DEMO_AGENTS = [
  { id: 'da-1', name: 'ResearchAgent', display_name: 'Research Agent', description: 'Deep-dive research and analysis', specialization: 'research', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 342, successful_executions: 318, success_rate: 93, effectiveness_score: 88, lastActive: ago(8), created_at: ago(43200) },
  { id: 'da-2', name: 'ContentWriterAgent', display_name: 'Content Writer', description: 'Generates blog posts and articles', specialization: 'content', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 156, successful_executions: 148, success_rate: 95, effectiveness_score: 91, lastActive: ago(45), created_at: ago(43200) },
  { id: 'da-3', name: 'SportsAnalyticsAgent', display_name: 'Sports Analytics', description: 'Analyzes games and generates picks', specialization: 'sports-analytics', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 289, successful_executions: 261, success_rate: 90, effectiveness_score: 85, lastActive: ago(15), created_at: ago(43200) },
  { id: 'da-4', name: 'StockIntelligenceAgent', display_name: 'Stock Intelligence', description: 'Market analysis and predictions', specialization: 'financial', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 198, successful_executions: 182, success_rate: 92, effectiveness_score: 87, lastActive: ago(30), created_at: ago(43200) },
  { id: 'da-5', name: 'SECFilingAgent', display_name: 'SEC Filing Analyst', description: 'Processes SEC filings and extracts insights', specialization: 'financial', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 94, successful_executions: 91, success_rate: 97, effectiveness_score: 94, lastActive: ago(180), created_at: ago(43200) },
  { id: 'da-6', name: 'ContentDistributionAgent', display_name: 'Content Distribution', description: 'Distributes content across platforms', specialization: 'content', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 78, successful_executions: 72, success_rate: 92, effectiveness_score: 83, lastActive: ago(120), created_at: ago(43200) },
  { id: 'da-7', name: 'ArbitrageAgent', display_name: 'Arbitrage Scanner', description: 'Scans for arbitrage opportunities', specialization: 'trading', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 456, successful_executions: 430, success_rate: 94, effectiveness_score: 90, lastActive: ago(5), created_at: ago(43200) },
  { id: 'da-8', name: 'NarrativeAgent', display_name: 'Narrative Builder', description: 'Builds narratives from signals', specialization: 'content', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 67, successful_executions: 62, success_rate: 93, effectiveness_score: 86, lastActive: ago(90), created_at: ago(43200) },
  { id: 'da-9', name: 'OddsCompilerAgent', display_name: 'Odds Compiler', description: 'Compiles and compares odds across books', specialization: 'sports-analytics', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 312, successful_executions: 298, success_rate: 96, effectiveness_score: 92, lastActive: ago(10), created_at: ago(43200) },
  { id: 'da-10', name: 'LegalDocDrafterAgent', display_name: 'Legal Doc Drafter', description: 'Drafts legal documents and contracts', specialization: 'business', agent_type: 'specialist', is_active: true, isActive: true, total_executions: 23, successful_executions: 22, success_rate: 96, effectiveness_score: 89, lastActive: ago(1440), created_at: ago(43200) },
];

export const DEMO_AGENT_EXECUTIONS = [
  { id: 'de-1', agent_name: 'ResearchAgent', task: 'Market analysis: NVDA sector', task_summary: 'Deep-dive on NVDA AI infrastructure', status: 'completed' as const, output_data: null, error_message: null, tokens_used: 4200, cost: 0.042, execution_time_ms: 12400, created_at: ago(8), completed_at: ago(6) },
  { id: 'de-2', agent_name: 'ArbitrageAgent', task: 'Scan NBA arbitrage opportunities', task_summary: 'Found 2 opportunities across 4 books', status: 'completed' as const, output_data: null, error_message: null, tokens_used: 1800, cost: 0.018, execution_time_ms: 8200, created_at: ago(12), completed_at: ago(10) },
  { id: 'de-3', agent_name: 'SportsAnalyticsAgent', task: 'Generate picks for NBA slate', task_summary: 'Analyzed 6 games, generated 4 picks', status: 'completed' as const, output_data: null, error_message: null, tokens_used: 5100, cost: 0.051, execution_time_ms: 18600, created_at: ago(15), completed_at: ago(12) },
  { id: 'de-4', agent_name: 'ContentWriterAgent', task: 'Write blog: AI in Sports Betting', task_summary: '1,240 word article, quality 0.89', status: 'completed' as const, output_data: null, error_message: null, tokens_used: 6800, cost: 0.068, execution_time_ms: 24000, created_at: ago(45), completed_at: ago(40) },
  { id: 'de-5', agent_name: 'StockIntelligenceAgent', task: 'Generate daily stock alerts', task_summary: '3 alerts generated: NVDA, AAPL, GOOGL', status: 'completed' as const, output_data: null, error_message: null, tokens_used: 3500, cost: 0.035, execution_time_ms: 15200, created_at: ago(30), completed_at: ago(27) },
  { id: 'de-6', agent_name: 'OddsCompilerAgent', task: 'Compile NBA odds movement', task_summary: 'Tracked 12 lines across 5 books', status: 'in_progress' as const, output_data: null, error_message: null, tokens_used: null, cost: null, execution_time_ms: null, created_at: ago(2), completed_at: null },
];

// ── Intelligence ──────────────────────────────────────────────────────────────

export const DEMO_INTELLIGENCE_STATS = {
  spiders: {
    total: 74,
    categories: 12,
    by_category: {
      'sports-odds': 18,
      'stock-market': 14,
      'sec-filings': 8,
      'news-general': 7,
      'social-media': 6,
      'crypto': 5,
      'weather': 4,
      'legislation': 4,
      'real-estate': 3,
      'commodities': 3,
      'earnings': 2,
    } as Record<string, number>,
  },
  agents: {
    total: 72,
    legacy: 14,
    clean: 58,
  },
  data: {
    total_points: 15420,
    last_24h: 342,
    success_rate: 96,
  },
  learning: {
    collaborations: 234,
    collaboration_sessions: 89,
    learning_events: 1456,
    agent_memories: 3240,
    knowledge_sources: 512,
    learning_connections: 178,
    knowledge_transfers: 67,
    synthesized_insights: 42,
  },
};

// ── Workspace ─────────────────────────────────────────────────────────────────

export const DEMO_WORKSPACES = [
  { id: 'dws-1', name: 'VIP Demo', description: 'Demo workspace for investor presentations', is_active: true, created_at: ago(10080), updated_at: ago(60), initiative_count: 4, deliverable_count: 12 },
  { id: 'dws-2', name: 'Sports Desk', description: 'Sports analytics and betting operations', is_active: false, created_at: ago(20160), updated_at: ago(180), initiative_count: 2, deliverable_count: 8 },
  { id: 'dws-3', name: 'Content Pipeline', description: 'Content creation and distribution workflows', is_active: false, created_at: ago(30240), updated_at: ago(360), initiative_count: 3, deliverable_count: 15 },
];

export const DEMO_WORKSPACE_OPERATIONS = [
  { id: 'dwo-1', type: 'file_create', description: 'Created betting brief template', workspace: 'VIP Demo', status: 'completed', file_path: 'templates/betting-brief.md', created_at: ago(60), completed_at: ago(58), user: 'ResearchAgent' },
  { id: 'dwo-2', type: 'file_modify', description: 'Updated stock alert schema', workspace: 'Content Pipeline', status: 'completed', file_path: 'schemas/stock-alert.json', created_at: ago(180), completed_at: ago(175), user: 'StockIntelligenceAgent' },
  { id: 'dwo-3', type: 'git_commit', description: 'Committed weekly report generation', workspace: 'Sports Desk', status: 'completed', file_path: 'reports/weekly-2026-w09.md', created_at: ago(360), completed_at: ago(355), user: 'ContentWriterAgent' },
];
