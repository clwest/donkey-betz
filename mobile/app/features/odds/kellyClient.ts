// app/features/odds/kellyClient.ts
const BASE = (process.env.EXPO_PUBLIC_DBAO_API_URL || "http://localhost:8001/api/v1").replace(/\/$/,"");

// ---- Local Kelly fallback (pure math) ----
function americanToDecimal(a: number) {
  return a > 0 ? (a/100) + 1 : (100/Math.abs(a)) + 1;
}

function kellyFraction(decimalOdds: number, p: number) {
  // b = decimal - 1
  const b = decimalOdds - 1;
  const q = 1 - p;
  const f = (b*p - q) / b;
  return Math.max(0, isFinite(f) ? f : 0);
}

export function computeKellyLocal(american: number, p: number, bankroll: number, fractional: number) {
  const dec = americanToDecimal(american);
  const full = kellyFraction(dec, p);
  const rec = Math.max(0, full * fractional);
  return {
    decimal_odds: dec,
    full_kelly_fraction: full,
    recommended_fraction: rec,
    stake_recommended: rec * bankroll,
    recommended_stake: rec * bankroll,
    kelly_percentage: rec * 100,
    expected_value: 0,
    is_positive_ev: rec > 0
  };
}

// ---- Token-bucket rate limiter (<=30/min) ----
type Token = number;
const capacity = 30;
const refillMs = 60_000;
let tokens = capacity;
let lastRefill = Date.now();

function takeToken(): boolean {
  const now = Date.now();
  const elapsed = now - lastRefill;
  if (elapsed > refillMs) {
    const buckets = Math.floor(elapsed / refillMs);
    tokens = Math.min(capacity, tokens + buckets * capacity);
    lastRefill = now - (elapsed % refillMs);
  }
  if (tokens > 0) { 
    tokens -= 1; 
    console.log(`[Kelly] Token taken, ${tokens} remaining`);
    return true; 
  }
  console.log('[Kelly] No tokens available, throttling');
  return false;
}

// ---- De-dupe + cache (TTL 5 min) ----
type Key = string;
const inflight = new Map<Key, Promise<any>>();
const cache = new Map<Key, { ts: number; data: any }>();
const TTL = 5 * 60 * 1000;

function keyOf(american: number, p: number, bankroll: number, fractional: number) {
  return `k:${american}|${p.toFixed(4)}|${bankroll}|${fractional}`;
}

// ---- Backoff state (reads retry_after) ----
let nextAllowedAt = 0;

async function postJson(path: string, body: any) {
  const url = `${BASE}${path}`;
  console.log("[DBAO API] POST", url, body);
  
  const r = await fetch(url, { 
    method: "POST", 
    headers: { "Content-Type": "application/json" }, 
    body: JSON.stringify(body) 
  });
  
  const t = await r.text();
  
  if (!r.ok) {
    console.log("[DBAO API] Error response:", t);
    let retryAfter = 0;
    try { 
      const j = JSON.parse(t); 
      retryAfter = Number(j?.retry_after || 0); 
    } catch {}
    
    if (r.status === 429) {
      nextAllowedAt = Date.now() + Math.max(1000, retryAfter * 1000);
      console.log(`[Kelly] 429 detected, backing off for ${retryAfter}s until ${new Date(nextAllowedAt).toISOString()}`);
    }
    throw new Error(`HTTP ${r.status}: ${t}`);
  }
  
  try { 
    return JSON.parse(t); 
  } catch { 
    return {}; 
  }
}

/**
 * Request Kelly with:
 * - token bucket (<=30/min),
 * - global backoff if 429,
 * - de-dupe by identical inputs,
 * - 5-min cache,
 * - local fallback if throttled or 429.
 */
export async function getKellyThrottled(opts: {
  american: number,
  winProbability: number, // 0..1
  bankroll: number,
  fractionalKelly: number
}) {
  const { american, winProbability, bankroll, fractionalKelly } = opts;
  const k = keyOf(american, winProbability, bankroll, fractionalKelly);

  // Cache hit
  const c = cache.get(k);
  if (c && (Date.now() - c.ts) < TTL) {
    console.log('[Kelly] Cache hit for', k);
    return c.data;
  }

  // Respect server backoff
  const now = Date.now();
  if (now < nextAllowedAt) {
    console.log('[Kelly] Server backoff active, using local fallback');
    const local = computeKellyLocal(american, winProbability, bankroll, fractionalKelly);
    cache.set(k, { ts: now, data: local });
    return local;
  }

  // De-dupe inflight
  if (inflight.has(k)) {
    console.log('[Kelly] De-duping inflight request for', k);
    return inflight.get(k)!;
  }

  const run = (async () => {
    // Token check; if none, use local fallback and schedule nothing.
    if (!takeToken()) {
      const local = computeKellyLocal(american, winProbability, bankroll, fractionalKelly);
      cache.set(k, { ts: Date.now(), data: local });
      console.log('[Kelly] Throttled, using local fallback');
      return local;
    }

    // Try server; on 429 or network error, fallback to local and respect backoff.
    try {
      // Convert american to float, removing +/- sign
      const oddsValue = Math.abs(american);
      const res = await postJson("/odds/kelly-criterion/", {
        odds_format: "american",
        odds: oddsValue,
        true_probability: winProbability,
        bankroll,
        fractional_kelly: fractionalKelly
      });
      
      // Handle the backend response format
      const normalizedResult = res.success && res.result ? {
        recommended_stake: res.result.recommended_stake || 0,
        kelly_percentage: res.result.kelly_percentage || 0,
        expected_value: (res.result.edge || 0) * 100,
        is_positive_ev: (res.result.edge || 0) > 0,
        decimal_odds: res.result.decimal_odds || americanToDecimal(american),
        full_kelly_fraction: res.result.kelly_percentage ? res.result.kelly_percentage / 100 : 0,
        recommended_fraction: res.result.kelly_percentage ? (res.result.kelly_percentage / 100) * fractionalKelly : 0,
        stake_recommended: res.result.recommended_stake || 0
      } : computeKellyLocal(american, winProbability, bankroll, fractionalKelly);
      
      cache.set(k, { ts: Date.now(), data: normalizedResult });
      console.log('[Kelly] Server response cached:', normalizedResult);
      return normalizedResult;
    } catch (e: any) {
      console.log('[Kelly] Request failed, using local fallback:', e.message);
      // Already set nextAllowedAt if 429; fallback to local
      const local = computeKellyLocal(american, winProbability, bankroll, fractionalKelly);
      cache.set(k, { ts: Date.now(), data: local });
      return local;
    } finally {
      inflight.delete(k);
    }
  })();

  inflight.set(k, run);
  return run;
}

// Helper to parse American odds string to number
export function parseAmericanOddsToNumber(oddsStr: string): number {
  const cleaned = oddsStr.replace(/[^\d-+]/g, '');
  const num = parseInt(cleaned);
  return isNaN(num) ? 100 : num;
}