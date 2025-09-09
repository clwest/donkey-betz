import { Platform } from 'react-native';

// Unified sports API client with proper league ID handling
const BASE = (process.env.EXPO_PUBLIC_DBAO_API_URL || "http://localhost:8001/api/v1").replace(/\/$/,"");

export interface League {
  id?: string;
  code: string;
  name: string;
  display_name?: string;
  active?: boolean;
}

export interface Game {
  id: string;
  league: string;
  home_team_name: string;
  away_team_name: string;
  start_time: string;
  status: string;
  venue?: string;
  season?: number;
  week?: number | null;
  home_score?: number | null;
  away_score?: number | null;
}

export interface Market {
  id: string;
  game_id: string;
  kind: string;
  name: string;
  price_american: string;
  implied_probability: number;
}

export async function leagues(): Promise<League[]> {
  const url = `${BASE}/sports/leagues/`;
  console.log("[RN SPORTS] GET", url);
  
  try {
    const r = await fetch(url);
    const t = await r.text();
    
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}: ${t}`);
    }
    
    const j = JSON.parse(t);
    console.log("[RN SPORTS] GET", url, "→", j?.length || 0, "leagues");
    
    // Normalize league data - use code as id
    const normalized = (Array.isArray(j) ? j : []).map(league => ({
      id: league.id || league.code,
      code: league.code,
      name: league.name,
      display_name: league.display_name || league.name,
      active: league.active !== false
    }));
    
    return normalized;
  } catch (error) {
    console.error("[RN SPORTS] Failed to fetch leagues:", error);
    return [];
  }
}

export async function games(q: { league: string; date: string }): Promise<Game[]> {
  // Use league code directly
  const url = `${BASE}/sports/games/?${new URLSearchParams(q).toString()}`;
  console.log("[RN SPORTS] GET", url);
  
  try {
    const r = await fetch(url);
    const t = await r.text();
    
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}: ${t}`);
    }
    
    const j = JSON.parse(t);
    
    // Normalize field names from backend
    const normalizedGames = (Array.isArray(j) ? j : []).map(game => ({
      id: game.id,
      league: game.league,
      home_team_name: game.home_team || game.home_team_name,
      away_team_name: game.away_team || game.away_team_name,
      start_time: game.game_time || game.start_time,
      status: game.status,
      venue: game.venue,
      season: game.season,
      week: game.week,
      home_score: game.home_score,
      away_score: game.away_score
    }));
    
    console.log("[RN SPORTS] GET", url, "→", normalizedGames.length, "games");
    return normalizedGames;
  } catch (error) {
    console.error("[RN SPORTS] Failed to fetch games:", error);
    return [];
  }
}

export async function markets(q: { league: string; game_id: string; kind?: string }): Promise<Market[]> {
  // Use league code directly and include all params
  const params = { ...q, kind: q.kind ?? "moneyline" };
  const url = `${BASE}/sports/markets/?${new URLSearchParams(params).toString()}`;
  console.log("[RN SPORTS] GET", url);
  
  try {
    const r = await fetch(url);
    const t = await r.text();
    
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}: ${t}`);
    }
    
    const j = JSON.parse(t);
    
    // Normalize market data from backend
    const normalizedMarkets = (Array.isArray(j) ? j : []).map(market => ({
      id: market.id,
      game_id: market.game_id,
      kind: market.market_type || market.kind || "moneyline",
      name: `${market.selection === 'home' ? 'Home' : market.selection === 'away' ? 'Away' : market.selection} ${market.market_type || 'Moneyline'}`,
      price_american: formatAmericanOdds(market.odds || market.price_american || "+100"),
      implied_probability: market.implied_probability || 0.5
    }));
    
    console.log("[RN SPORTS] GET", url, "→", normalizedMarkets.length, "markets");
    return normalizedMarkets;
  } catch (error) {
    console.error("[RN SPORTS] Failed to fetch markets:", error);
    return [];
  }
}

// Helper to format American odds consistently
function formatAmericanOdds(odds: string | number): string {
  const str = String(odds).trim();
  if (!str) return "+100";
  
  // Remove any existing +/- and parse
  const withoutSign = str.replace(/^[+-]/, '');
  const num = parseInt(withoutSign);
  
  if (isNaN(num)) return "+100";
  
  // Add proper sign
  if (str.startsWith('-')) {
    return `-${num}`;
  }
  return `+${num}`;
}

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatPercentage = (value: number): string => {
  return `${value.toFixed(2)}%`;
};