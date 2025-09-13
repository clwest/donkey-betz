"""
Caching Service for Odds and Sports Data
Implements intelligent caching with TTL and invalidation strategies
"""

from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_CONFIGS = {
    'odds': {
        'ttl': 60,  # 1 minute for live odds
        'prefix': 'odds',
        'version': 1
    },
    'games': {
        'ttl': 300,  # 5 minutes for game data
        'prefix': 'games',
        'version': 1
    },
    'teams': {
        'ttl': 3600,  # 1 hour for team data
        'prefix': 'teams',
        'version': 1
    },
    'leagues': {
        'ttl': 86400,  # 24 hours for league data
        'prefix': 'leagues',
        'version': 1
    },
    'weather': {
        'ttl': 1800,  # 30 minutes for weather data
        'prefix': 'weather',
        'version': 1
    },
    'injuries': {
        'ttl': 600,  # 10 minutes for injury reports
        'prefix': 'injuries',
        'version': 1
    },
    'kelly': {
        'ttl': 30,  # 30 seconds for Kelly calculations
        'prefix': 'kelly',
        'version': 1
    },
    'arbitrage': {
        'ttl': 10,  # 10 seconds for arbitrage opportunities
        'prefix': 'arb',
        'version': 1
    }
}


class CacheService:
    """
    Centralized caching service for sports and odds data
    """
    
    @staticmethod
    def generate_cache_key(prefix, *args):
        """
        Generate a consistent cache key from arguments
        
        Args:
            prefix: Cache key prefix
            *args: Variable arguments to include in key
            
        Returns:
            str: Cache key
        """
        # Convert all args to strings and join
        key_parts = [str(arg) for arg in args if arg is not None]
        key_string = ':'.join(key_parts)
        
        # For long keys, use hash
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return f"{prefix}:{key_string}"
    
    @staticmethod
    def get(cache_type, *key_args):
        """
        Get cached value
        
        Args:
            cache_type: Type of cache (odds, games, etc.)
            *key_args: Arguments for cache key
            
        Returns:
            Cached value or None
        """
        config = CACHE_CONFIGS.get(cache_type, CACHE_CONFIGS['odds'])
        cache_key = CacheService.generate_cache_key(config['prefix'], *key_args)
        
        try:
            value = cache.get(cache_key, version=config['version'])
            if value:
                logger.debug(f"Cache HIT: {cache_key}")
            else:
                logger.debug(f"Cache MISS: {cache_key}")
            return value
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None
    
    @staticmethod
    def set(cache_type, value, *key_args, ttl_override=None):
        """
        Set cached value
        
        Args:
            cache_type: Type of cache
            value: Value to cache
            *key_args: Arguments for cache key
            ttl_override: Override default TTL
            
        Returns:
            bool: Success status
        """
        config = CACHE_CONFIGS.get(cache_type, CACHE_CONFIGS['odds'])
        cache_key = CacheService.generate_cache_key(config['prefix'], *key_args)
        ttl = ttl_override or config['ttl']
        
        try:
            cache.set(cache_key, value, ttl, version=config['version'])
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
    @staticmethod
    def delete(cache_type, *key_args):
        """
        Delete cached value
        
        Args:
            cache_type: Type of cache
            *key_args: Arguments for cache key
            
        Returns:
            bool: Success status
        """
        config = CACHE_CONFIGS.get(cache_type, CACHE_CONFIGS['odds'])
        cache_key = CacheService.generate_cache_key(config['prefix'], *key_args)
        
        try:
            cache.delete(cache_key, version=config['version'])
            logger.debug(f"Cache DELETE: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error: {e}")
            return False
    
    @staticmethod
    def invalidate_pattern(pattern):
        """
        Invalidate all cache keys matching pattern
        
        Args:
            pattern: Pattern to match (e.g., "odds:*")
            
        Returns:
            int: Number of keys deleted
        """
        try:
            # This requires Redis backend
            if hasattr(cache, '_cache'):
                redis_client = cache._cache.get_client()
                keys = redis_client.keys(f"*{pattern}*")
                if keys:
                    deleted = redis_client.delete(*keys)
                    logger.info(f"Invalidated {deleted} cache keys matching {pattern}")
                    return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache pattern invalidation error: {e}")
            return 0


def cache_response(cache_type='odds', key_params=None, ttl_override=None):
    """
    Decorator to cache API responses
    
    Args:
        cache_type: Type of cache to use
        key_params: List of request params to include in cache key
        ttl_override: Override default TTL
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Build cache key from request parameters
            cache_key_parts = [request.method]
            
            if key_params:
                for param in key_params:
                    value = request.GET.get(param) or request.POST.get(param)
                    if value:
                        cache_key_parts.append(f"{param}:{value}")
            
            # Add user ID for personalized caching
            if request.user and request.user.is_authenticated:
                cache_key_parts.append(f"user:{request.user.id}")
            
            # Check cache
            cached_response = CacheService.get(cache_type, *cache_key_parts)
            if cached_response:
                logger.info(f"Returning cached response for {request.path}")
                # Add cache headers
                response = cached_response
                if hasattr(response, '__setitem__'):
                    response['X-Cache'] = 'HIT'
                return response
            
            # Call view function
            response = view_func(request, *args, **kwargs)
            
            # Cache successful responses only
            if response.status_code == 200:
                CacheService.set(
                    cache_type,
                    response,
                    *cache_key_parts,
                    ttl_override=ttl_override
                )
                if hasattr(response, '__setitem__'):
                    response['X-Cache'] = 'MISS'
            
            return response
        
        return wrapped_view
    return decorator


class OddsCache:
    """
    Specialized cache for odds data with smart invalidation
    """
    
    @staticmethod
    def cache_game_odds(game_id, bookmaker, odds_data):
        """Cache odds for a specific game and bookmaker"""
        cache_key = f"odds:{game_id}:{bookmaker}"
        
        # Add timestamp to track freshness
        odds_data['cached_at'] = datetime.now().isoformat()
        
        # Shorter TTL for live games
        if odds_data.get('is_live'):
            ttl = 30  # 30 seconds for live games
        else:
            ttl = 60  # 1 minute for upcoming games
        
        CacheService.set('odds', odds_data, game_id, bookmaker, ttl_override=ttl)
        return True
    
    @staticmethod
    def get_game_odds(game_id, bookmaker=None):
        """Get cached odds for a game"""
        if bookmaker:
            return CacheService.get('odds', game_id, bookmaker)
        
        # Get all bookmakers for this game
        all_odds = {}
        for bm in ['draftkings', 'fanduel', 'betmgm', 'caesars']:
            odds = CacheService.get('odds', game_id, bm)
            if odds:
                all_odds[bm] = odds
        
        return all_odds if all_odds else None
    
    @staticmethod
    def invalidate_game_odds(game_id):
        """Invalidate all odds for a game"""
        pattern = f"odds:{game_id}:*"
        return CacheService.invalidate_pattern(pattern)


class GamesCache:
    """
    Specialized cache for game data
    """
    
    @staticmethod
    def cache_games_list(league, date, games_data):
        """Cache games list for a league and date"""
        cache_key_parts = ['games_list', league, date]
        return CacheService.set('games', games_data, *cache_key_parts)
    
    @staticmethod
    def get_games_list(league, date):
        """Get cached games list"""
        cache_key_parts = ['games_list', league, date]
        return CacheService.get('games', *cache_key_parts)
    
    @staticmethod
    def cache_game_detail(game_id, game_data):
        """Cache detailed game information"""
        return CacheService.set('games', game_data, 'detail', game_id)
    
    @staticmethod
    def get_game_detail(game_id):
        """Get cached game detail"""
        return CacheService.get('games', 'detail', game_id)


class KellyCache:
    """
    Cache for Kelly Criterion calculations
    """
    
    @staticmethod
    def cache_calculation(odds, probability, bankroll, multiplier, result):
        """Cache Kelly calculation result"""
        # Create hash of inputs for key
        inputs = f"{odds}:{probability}:{bankroll}:{multiplier}"
        input_hash = hashlib.md5(inputs.encode()).hexdigest()[:8]
        
        return CacheService.set('kelly', result, input_hash)
    
    @staticmethod
    def get_calculation(odds, probability, bankroll, multiplier):
        """Get cached Kelly calculation"""
        inputs = f"{odds}:{probability}:{bankroll}:{multiplier}"
        input_hash = hashlib.md5(inputs.encode()).hexdigest()[:8]
        
        return CacheService.get('kelly', input_hash)


# Cache warming functions
def warm_leagues_cache():
    """Pre-populate league cache"""
    try:
        from sports.models import League
        leagues = League.objects.filter(is_active=True)
        
        for league in leagues:
            cache_data = {
                'id': league.id,
                'name': league.name,
                'abbreviation': league.abbreviation,
                'sport_type': league.sport_type
            }
            CacheService.set('leagues', cache_data, league.abbreviation)
        
        logger.info(f"Warmed cache for {leagues.count()} leagues")
        return True
    except Exception as e:
        logger.error(f"Cache warming error: {e}")
        return False


def warm_todays_games_cache():
    """Pre-populate today's games cache"""
    try:
        from sports.models import Game
        from django.utils import timezone
        
        today = timezone.now().date()
        games = Game.objects.filter(
            scheduled_start__date=today,
            is_active=True
        ).select_related('home_team', 'away_team', 'league')
        
        for game in games:
            game_data = {
                'id': game.id,
                'home_team': game.home_team.name,
                'away_team': game.away_team.name,
                'scheduled_start': game.scheduled_start.isoformat(),
                'status': game.status
            }
            GamesCache.cache_game_detail(game.id, game_data)
        
        logger.info(f"Warmed cache for {games.count()} games")
        return True
    except Exception as e:
        logger.error(f"Cache warming error: {e}")
        return False


# Cache statistics
def get_cache_stats():
    """Get cache usage statistics"""
    try:
        if hasattr(cache, '_cache'):
            redis_client = cache._cache.get_client()
            info = redis_client.info('stats')
            
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': info.get('keyspace_hits', 0) / 
                           (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)),
                'memory_used': info.get('used_memory_human', 'N/A'),
                'keys': redis_client.dbsize()
            }
        return {}
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return {}
