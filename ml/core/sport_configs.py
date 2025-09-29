"""
Sport-specific configuration for multi-sport prediction system.

This module defines configuration for each sport including:
- Feature definitions
- Home advantage constants
- Training parameters
- Recent games analysis window

Usage:
    from ml.core.sport_configs import SPORT_CONFIGS

    config = SPORT_CONFIGS['nfl']
    print(config.name)  # "NFL"
    print(config.features)  # List of feature names
"""

from dataclasses import dataclass
from typing import List, Callable, Optional


@dataclass
class SportConfig:
    """Configuration for a specific sport's prediction model."""

    sport_type: str              # 'nfl', 'nba', 'mlb', 'nhl'
    name: str                    # 'NFL', 'NBA', 'MLB', 'NHL'
    model_name: str              # 'nfl_predictor', 'nba_predictor', etc.
    home_advantage: float        # Expected points/goals advantage for home team
    recent_games_window: int     # How many recent games to analyze for stats
    min_training_games: int      # Minimum games needed for training
    features: List[str]          # Feature names for model input
    feature_extractor: Optional[Callable] = None  # Function to extract features (set dynamically)


# Sport configurations for all supported sports
SPORT_CONFIGS = {
    'nfl': SportConfig(
        sport_type='nfl',
        name='NFL',
        model_name='nfl_predictor',
        home_advantage=3.0,          # Home teams average ~3 points advantage
        recent_games_window=10,      # Last 10 games for team stats
        min_training_games=100,      # Need at least 100 games to train
        features=[
            'points_differential',    # Home PPG - Away PPG
            'yards_differential',     # Home YPG - Away YPG (if available)
            'defensive_strength',     # Points allowed differential
            'win_rate_differential',  # Home win% - Away win%
            'ats_differential',       # Against the spread differential
            'home_indicator',         # 1.0 for home team
            'rest_differential',      # Days rest difference
            'division_game'           # 1.0 if division matchup
        ]
    ),

    'nba': SportConfig(
        sport_type='nba',
        name='NBA',
        model_name='nba_predictor',
        home_advantage=4.5,          # Home teams average ~4.5 points advantage
        recent_games_window=15,      # Last 15 games (more games per season)
        min_training_games=200,      # Need more games (82-game season)
        features=[
            'points_differential',    # Home PPG - Away PPG
            'rebounds_differential',  # Home RPG - Away RPG
            'assists_differential',   # Home APG - Away APG
            'defensive_rating',       # Defensive efficiency differential
            'win_rate_differential',  # Home win% - Away win%
            'pace_differential',      # Possessions per game differential
            'home_indicator',         # 1.0 for home team
            'back_to_back',          # 1.0 if either team on back-to-back
            'rest_differential'       # Days rest difference
        ]
    ),

    'mlb': SportConfig(
        sport_type='mlb',
        name='MLB',
        model_name='mlb_predictor',
        home_advantage=0.5,          # Home teams average ~0.5 runs advantage
        recent_games_window=10,      # Last 10 games
        min_training_games=300,      # Need many games (162-game season)
        features=[
            'runs_differential',           # Home RPG - Away RPG
            'era_differential',            # ERA differential (lower is better)
            'batting_avg_differential',    # Team batting average differential
            'bullpen_era_differential',    # Bullpen ERA differential
            'win_rate_differential',       # Home win% - Away win%
            'home_indicator',              # 1.0 for home team
            'pitcher_matchup_rating',      # Starting pitcher quality differential
            'weather_factor'               # Weather impact (if available)
        ]
    ),

    'nhl': SportConfig(
        sport_type='nhl',
        name='NHL',
        model_name='nhl_predictor',
        home_advantage=0.5,          # Home teams average ~0.5 goals advantage
        recent_games_window=10,      # Last 10 games
        min_training_games=150,      # Moderate sample needed
        features=[
            'goals_differential',          # Home GPG - Away GPG
            'shots_differential',          # Shots per game differential
            'save_percentage_differential', # Goalie save % differential
            'powerplay_differential',      # Power play % differential
            'penalty_kill_differential',   # Penalty kill % differential
            'win_rate_differential',       # Home win% - Away win%
            'home_indicator',              # 1.0 for home team
            'back_to_back',               # 1.0 if either team on back-to-back
            'goalie_matchup_rating'       # Starting goalie quality differential
        ]
    )
}


def get_sport_config(sport_type: str) -> SportConfig:
    """
    Get configuration for a specific sport.

    Args:
        sport_type: Sport identifier ('nfl', 'nba', 'mlb', 'nhl')

    Returns:
        SportConfig object for the sport

    Raises:
        ValueError: If sport_type is not recognized
    """
    config = SPORT_CONFIGS.get(sport_type)
    if not config:
        raise ValueError(
            f"Unknown sport: {sport_type}. "
            f"Available sports: {', '.join(SPORT_CONFIGS.keys())}"
        )
    return config


def get_all_sports() -> List[str]:
    """Get list of all supported sport types."""
    return list(SPORT_CONFIGS.keys())


def get_feature_count(sport_type: str) -> int:
    """Get the number of features for a specific sport."""
    config = get_sport_config(sport_type)
    return len(config.features)