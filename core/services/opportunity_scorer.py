"""
Unified Opportunity Scorer
==========================

Single source of truth for scoring opportunities across all types:
freelance, sports_betting, content, trading, consulting.

Two public functions:
  - infer_opportunity_type(spider_name, data_type, ...) -> str
  - score_opportunity(raw_data, ...) -> dict

Session 1076: Created to replace three separate scoring functions that were
all hardcoded for freelance/job signals.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Spider-name → opportunity type mapping
# ---------------------------------------------------------------------------
SPIDER_TYPE_MAP: Dict[str, str] = {
    # Freelance / jobs
    'remoteok': 'freelance',
    'weworkremotely': 'freelance',
    'upwork': 'freelance',
    'fiverr': 'freelance',
    'freelancer': 'freelance',
    'toptal': 'freelance',
    'real_job': 'freelance',
    'job_opportunity': 'freelance',
    # Sports betting
    'theodds': 'sports_betting',
    'odds_api': 'sports_betting',
    'sports_odds': 'sports_betting',
    'sports_data': 'sports_betting',
    'live_betting': 'sports_betting',
    'prop_betting': 'sports_betting',
    'esports_gaming': 'sports_betting',
    # Trading / finance
    'yahoo_finance': 'trading',
    'coingecko': 'trading',
    'stock_options': 'trading',
    'forex_crypto': 'trading',
    'financial_api': 'trading',
    'crypto_intelligence': 'trading',
    # Content / social
    'reddit': 'content',
    'youtube': 'content',
    'tiktok': 'content',
    'instagram': 'content',
    'twitter': 'content',
    'news': 'content',
    'trending_content': 'content',
    'social_api': 'content',
    'news_intelligence': 'content',
    # Consulting
    'ai_startup': 'consulting',
}

# data_type → opportunity type mapping
_DATA_TYPE_MAP: Dict[str, str] = {
    'job_listing': 'freelance',
    'freelance_gig': 'freelance',
    'job': 'freelance',
    'sports_odds': 'sports_betting',
    'live_odds': 'sports_betting',
    'prop_bet': 'sports_betting',
    'game_odds': 'sports_betting',
    'stock_data': 'trading',
    'crypto_price': 'trading',
    'market_data': 'trading',
    'forex_data': 'trading',
    'options_data': 'trading',
    'social_trend': 'content',
    'trending_topic': 'content',
    'viral_content': 'content',
    'news_article': 'content',
}

# Keyword sets for fallback inference
_TYPE_KEYWORDS = {
    'sports_betting': [
        'odds', 'spread', 'moneyline', 'over/under', 'parlay',
        'bookmaker', 'sportsbook', 'betting', 'wager',
    ],
    'trading': [
        'stock', 'ticker', 'market cap', 'dividend', 'forex',
        'crypto', 'bitcoin', 'ethereum', 'trading', 'portfolio',
        '52-week', 'volume', 'bull', 'bear',
    ],
    'content': [
        'viral', 'trending', 'engagement', 'subscribers', 'views',
        'social media', 'influencer', 'content creator', 'blog',
    ],
    'consulting': [
        'strategy', 'advisory', 'consultant', 'retainer',
        'enterprise', 'transformation',
    ],
}

# Channel substring → type
_CHANNEL_TYPE_MAP = {
    'freelance': 'freelance',
    'job': 'freelance',
    'betting': 'sports_betting',
    'odds': 'sports_betting',
    'sports': 'sports_betting',
    'trading': 'trading',
    'finance': 'trading',
    'crypto': 'trading',
    'content': 'content',
    'social': 'content',
    'news': 'content',
}


# ===================================================================
# Public API
# ===================================================================

def infer_opportunity_type(
    spider_name: str = '',
    data_type: str = '',
    title: str = '',
    description: str = '',
    channel: str = '',
    raw_data: Optional[Dict] = None,
) -> str:
    """
    Infer the opportunity type from available metadata.

    Priority chain:
      1. spider_name exact lookup
      2. spider_name substring match
      3. data_type lookup
      4. keyword match in title+description
      5. channel substring match
      6. default → 'freelance'
    """
    spider_lower = (spider_name or '').lower().strip()
    data_type_lower = (data_type or '').lower().strip()

    # 1. Exact spider name match
    if spider_lower in SPIDER_TYPE_MAP:
        return SPIDER_TYPE_MAP[spider_lower]

    # 2. Substring match on spider name
    for key, opp_type in SPIDER_TYPE_MAP.items():
        if key in spider_lower:
            return opp_type

    # 3. data_type lookup
    if data_type_lower in _DATA_TYPE_MAP:
        return _DATA_TYPE_MAP[data_type_lower]

    # 4. Keyword match in title + description
    text = f"{title} {description}".lower()
    for opp_type, keywords in _TYPE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return opp_type

    # 5. Channel substring match
    channel_lower = (channel or '').lower()
    for substr, opp_type in _CHANNEL_TYPE_MAP.items():
        if substr in channel_lower:
            return opp_type

    # 6. Default
    return 'freelance'


def score_opportunity(
    raw_data: Optional[Dict] = None,
    opportunity_type: str = '',
    spider_name: str = '',
    data_type: str = '',
    title: str = '',
    description: str = '',
    channel: str = '',
) -> Dict:
    """
    Score an opportunity and return a unified result dict.

    If opportunity_type is not provided, it will be inferred.

    Returns dict with:
      - score_0_1       (float 0.3-0.95) — for spider_opportunity_connector
      - score_0_100     (int 1-100)      — for rescore command
      - profit_potential, competition_level, effort_required, time_sensitivity (1-100)
      - overall_score   (int 1-100)      — weighted composite
      - opportunity_type, scoring_method
    """
    raw_data = raw_data or {}

    # Fill in title/description from raw_data if not provided directly
    title = title or raw_data.get('title', raw_data.get('name', ''))
    description = description or raw_data.get('description', raw_data.get('summary', ''))

    if not opportunity_type:
        opportunity_type = infer_opportunity_type(
            spider_name=spider_name,
            data_type=data_type,
            title=title,
            description=description,
            channel=channel,
            raw_data=raw_data,
        )

    # Dispatch to type-specific scorer
    scorer = _SCORERS.get(opportunity_type, _score_freelance)
    dimensions = scorer(raw_data, title, description)

    profit = dimensions['profit_potential']
    competition = dimensions['competition_level']
    effort = dimensions['effort_required']
    timing = dimensions['time_sensitivity']

    # Weighted composite (same 35/35/20/10 used everywhere)
    competition_inv = 100 - competition
    effort_inv = 100 - effort
    overall = int(
        profit * 0.35
        + competition_inv * 0.35
        + effort_inv * 0.20
        + timing * 0.10
    )
    overall = max(1, min(100, overall))

    # Convert to 0-1 scale for spider_opportunity_connector
    score_float = max(0.30, min(0.95, overall / 100.0))

    return {
        'score_0_1': round(score_float, 3),
        'score_0_100': overall,
        'profit_potential': profit,
        'competition_level': competition,
        'effort_required': effort,
        'time_sensitivity': timing,
        'overall_score': overall,
        'opportunity_type': opportunity_type,
        'scoring_method': f'{opportunity_type}_heuristic',
    }


# ===================================================================
# Type-specific scorers (private)
# Each returns {profit_potential, competition_level, effort_required, time_sensitivity}
# All values 1-100.
# ===================================================================

def _score_freelance(raw_data: Dict, title: str, description: str) -> Dict:
    """Score freelance/job opportunities using budget, skills, client signals."""
    profit = 35

    # Budget / salary signals
    budget = raw_data.get('budget', {})
    if isinstance(budget, dict):
        if budget.get('min') or budget.get('max'):
            bmax = float(budget.get('max') or budget.get('min') or 0)
            profit += 15 if bmax >= 500 else 10 if bmax > 0 else 0
    elif isinstance(budget, str) and budget.strip():
        profit += 10
    if raw_data.get('salary_min') or raw_data.get('salary_max'):
        profit += 15

    # Description quality
    if len(description) > 200:
        profit += 5
    elif len(description) > 50:
        profit += 2

    # Company presence (legitimacy signal)
    if raw_data.get('company', '').strip():
        profit += 5

    profit = min(95, profit)

    # Competition
    competition = 50
    skills = raw_data.get('skills_required', raw_data.get('skills', raw_data.get('tags', [])))
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]
    skill_count = len(skills) if isinstance(skills, list) else 0

    if skill_count >= 5:
        competition = 35  # Niche = less competition
    elif skill_count >= 3:
        competition = 45
    else:
        competition = 60

    # Effort
    effort = 40 if skill_count <= 2 else 55 if skill_count <= 5 else 65

    # Time sensitivity
    timing = 50
    if raw_data.get('urgency') == 'high':
        timing = 80
    elif raw_data.get('deadline'):
        timing = 65

    # Client rating boost to profit
    try:
        rating = raw_data.get('client_rating')
        if rating is not None and float(rating) >= 4.5:
            profit = min(95, profit + 5)
    except (ValueError, TypeError):
        pass

    # Application URL (actionable)
    if raw_data.get('application_url') or raw_data.get('url'):
        profit = min(95, profit + 3)

    return {
        'profit_potential': max(1, profit),
        'competition_level': max(1, min(100, competition)),
        'effort_required': max(1, min(100, effort)),
        'time_sensitivity': max(1, min(100, timing)),
    }


def _score_sports_betting(raw_data: Dict, title: str, description: str) -> Dict:
    """Score sports betting opportunities using odds, bookmaker count, timing."""
    profit = 40
    competition = 55
    effort = 25  # Betting is low-effort to execute
    timing = 70  # Most sports bets are time-sensitive

    # Odds values — presence of multiple odds formats is a quality signal
    odds_keys = ['h2h', 'spreads', 'totals', 'odds', 'home_odds', 'away_odds',
                 'moneyline', 'spread', 'over_under']
    odds_present = sum(1 for k in odds_keys if raw_data.get(k))
    if odds_present >= 3:
        profit += 20
    elif odds_present >= 1:
        profit += 10

    # Bookmaker count — more bookmakers = better line shopping
    bookmakers = raw_data.get('bookmakers', raw_data.get('bookmaker_count', 0))
    if isinstance(bookmakers, list):
        bookmakers = len(bookmakers)
    try:
        bookmakers = int(bookmakers)
    except (ValueError, TypeError):
        bookmakers = 0
    if bookmakers >= 5:
        profit += 10
        competition += 10  # Popular events = more competition
    elif bookmakers >= 2:
        profit += 5

    # Live / in-play
    if raw_data.get('is_live') or raw_data.get('live'):
        timing = 95
        effort += 10  # Requires real-time attention

    # Commence time proximity
    commence = raw_data.get('commence_time', '')
    if commence:
        timing = max(timing, 75)

    # Sport type affects profit ceiling
    sport = raw_data.get('sport', raw_data.get('sport_key', '')).lower()
    high_volume_sports = ['football', 'basketball', 'soccer', 'nfl', 'nba', 'mlb']
    if any(s in sport for s in high_volume_sports):
        profit += 5
        competition += 10
    elif sport:
        profit += 3

    return {
        'profit_potential': max(1, min(95, profit)),
        'competition_level': max(1, min(100, competition)),
        'effort_required': max(1, min(100, effort)),
        'time_sensitivity': max(1, min(100, timing)),
    }


def _score_content(raw_data: Dict, title: str, description: str) -> Dict:
    """Score content/trending opportunities using engagement, recency, keywords."""
    profit = 35
    competition = 55
    effort = 50
    timing = 60

    # Engagement signals
    score_val = raw_data.get('score', raw_data.get('upvotes', raw_data.get('likes', 0)))
    try:
        score_val = int(score_val)
    except (ValueError, TypeError):
        score_val = 0

    if score_val >= 1000:
        profit += 20
        timing += 15
    elif score_val >= 100:
        profit += 10
        timing += 5

    comments = raw_data.get('num_comments', raw_data.get('comments', 0))
    try:
        comments = int(comments)
    except (ValueError, TypeError):
        comments = 0
    if comments >= 100:
        profit += 10
    elif comments >= 20:
        profit += 5

    # Trending / viral signals
    text = f"{title} {description}".lower()
    if any(kw in text for kw in ['viral', 'trending', 'breaking', 'exploding']):
        timing += 15
        profit += 5

    # Keyword richness (more specific = better opportunity)
    word_count = len(text.split())
    if word_count >= 20:
        effort -= 5  # More context = easier to produce content
        profit += 5

    # Platform presence
    if raw_data.get('subreddit') or raw_data.get('channel'):
        competition -= 5  # Niche community

    return {
        'profit_potential': max(1, min(95, profit)),
        'competition_level': max(1, min(100, competition)),
        'effort_required': max(1, min(100, effort)),
        'time_sensitivity': max(1, min(100, timing)),
    }


def _score_trading(raw_data: Dict, title: str, description: str) -> Dict:
    """Score trading/investment opportunities using price, volume, market cap."""
    profit = 40
    competition = 60
    effort = 35  # Trading is moderate effort
    timing = 55

    # Price change percentage
    change_pct = raw_data.get('price_change_percentage_24h',
                              raw_data.get('change_percent',
                              raw_data.get('percent_change', 0)))
    try:
        change_pct = float(change_pct)
    except (ValueError, TypeError):
        change_pct = 0

    abs_change = abs(change_pct)
    if abs_change >= 10:
        profit += 20
        timing += 20
    elif abs_change >= 5:
        profit += 10
        timing += 10
    elif abs_change >= 2:
        profit += 5

    # Volume signals
    volume = raw_data.get('total_volume', raw_data.get('volume', 0))
    try:
        volume = float(volume)
    except (ValueError, TypeError):
        volume = 0
    if volume >= 1_000_000:
        profit += 10
        competition += 10
    elif volume >= 100_000:
        profit += 5

    # Market cap (larger = more liquid but less upside)
    market_cap = raw_data.get('market_cap', 0)
    try:
        market_cap = float(market_cap)
    except (ValueError, TypeError):
        market_cap = 0
    if market_cap >= 1_000_000_000:
        competition += 10
        effort -= 5  # Blue chip = easier analysis
    elif market_cap >= 100_000_000:
        profit += 5

    # 52-week proximity
    high_52 = raw_data.get('52_week_high', raw_data.get('ath', 0))
    current = raw_data.get('current_price', raw_data.get('price', 0))
    try:
        high_52 = float(high_52)
        current = float(current)
        if high_52 > 0 and current > 0:
            proximity = current / high_52
            if proximity >= 0.9:
                timing += 10  # Near ATH — momentum
            elif proximity <= 0.5:
                profit += 10  # Deep value play
    except (ValueError, TypeError):
        pass

    # Sector presence
    if raw_data.get('sector') or raw_data.get('category'):
        profit += 3

    return {
        'profit_potential': max(1, min(95, profit)),
        'competition_level': max(1, min(100, competition)),
        'effort_required': max(1, min(100, effort)),
        'time_sensitivity': max(1, min(100, timing)),
    }


def _score_consulting(raw_data: Dict, title: str, description: str) -> Dict:
    """Score consulting opportunities using description quality, budget, keywords."""
    profit = 45
    competition = 45
    effort = 55
    timing = 40  # Consulting is less time-sensitive

    # Description quality — longer = more serious client
    if len(description) > 300:
        profit += 15
        competition -= 5
    elif len(description) > 100:
        profit += 8

    # Company presence
    if raw_data.get('company', '').strip():
        profit += 10
        competition -= 5

    # Budget signals
    budget = raw_data.get('budget', {})
    if isinstance(budget, dict):
        bmax = float(budget.get('max') or budget.get('min') or 0)
        if bmax >= 5000:
            profit += 15
        elif bmax > 0:
            profit += 8
    elif isinstance(budget, str) and budget.strip():
        profit += 5

    # Strategy keywords boost
    text = f"{title} {description}".lower()
    strategy_kw = ['strategy', 'roadmap', 'transformation', 'architecture',
                   'advisory', 'assessment', 'audit', 'optimization']
    matches = sum(1 for kw in strategy_kw if kw in text)
    if matches >= 3:
        profit += 10
        effort += 10
    elif matches >= 1:
        profit += 5

    return {
        'profit_potential': max(1, min(95, profit)),
        'competition_level': max(1, min(100, competition)),
        'effort_required': max(1, min(100, effort)),
        'time_sensitivity': max(1, min(100, timing)),
    }


# Scorer dispatch table
_SCORERS = {
    'freelance': _score_freelance,
    'sports_betting': _score_sports_betting,
    'content': _score_content,
    'trading': _score_trading,
    'consulting': _score_consulting,
}
