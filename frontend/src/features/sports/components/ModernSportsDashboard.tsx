/**
 * 🎯 MODERN SPORTS DASHBOARD 🎯
 * 
 * Clean, professional betting interface with subtle gaming accents
 * Improved layout, better spacing, and cleaner visual hierarchy
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { toast } from 'sonner';
import { useWebSocket } from '../../../hooks/useWebSocket';
import '../../../styles/sports-modern.css';
import { 
  RefreshCw, 
  Calendar, 
  TrendingUp, 
  Activity,
  Clock,
  MapPin,
  Wifi,
  Zap,
  Trophy,
  Timer,
  AlertCircle,
  ChevronRight,
  Filter,
  Grid3x3,
  List
} from 'lucide-react';

import type { League, Game } from '../api/sports';
import { 
  SportType,
  GameStatus,
  getSportsTypes,
  getLiveGames,
  getGamesBySport,
  getTrendingGames,
  syncSportsData,
  getSportDisplayName,
  getSportEmoji,
  formatGameTime,
  getGameStatusDisplay,
  isGameLive,
  isGameFinished,
  getInferredGameStatus,
  formatTeamRecord,
  getTodayDateString,
  getThisWeekDateRange,
} from '../api/sports';

interface SportsType {
  sport_type: SportType;
  name: string;
  count: number;
}

export default function ModernSportsDashboard() {
  const navigate = useNavigate();
  const [selectedSport, setSelectedSport] = useState<SportType>(SportType.NCAAF);
  const [selectedDate, setSelectedDate] = useState<string>('thisweek');
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [autoSyncEnabled, setAutoSyncEnabled] = useState(true);
  
  // Data state
  const [sportsTypes, setSportsTypes] = useState<SportsType[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [liveGames, setLiveGames] = useState<Game[]>([]);
  const [trendingGames, setTrendingGames] = useState<Game[]>([]);

  // WebSocket connection
  const { isConnected: wsConnected, sendMessage } = useWebSocket({
    url: '/ws/live-sports/',
    onMessage: (data) => {
      if (data.type === 'game_update') {
        setGames(prevGames => 
          prevGames.map(game => 
            game.id === data.game_id ? { ...game, ...data.data } : game
          )
        );
      }
    },
    reconnect: true,
    maxReconnectAttempts: 5
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (selectedSport) {
      loadGamesForSport();
    }
  }, [selectedSport, selectedDate]);

  // Auto-sync every 2 minutes
  useEffect(() => {
    if (!autoSyncEnabled) return;
    const syncInterval = setInterval(() => {
      handleSyncData(true);
    }, 2 * 60 * 1000);
    return () => clearInterval(syncInterval);
  }, [autoSyncEnabled, selectedSport]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [sportsTypesData, liveGamesData, trendingGamesData] = await Promise.all([
        getSportsTypes(),
        getLiveGames(),
        getTrendingGames(20)
      ]);

      setSportsTypes(sportsTypesData || []);
      setLiveGames(liveGamesData || []);
      setTrendingGames(trendingGamesData || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load sports data');
    } finally {
      setLoading(false);
    }
  };

  const loadGamesForSport = async () => {
    if (!selectedSport) return;
    
    try {
      let gamesData: Game[] = [];
      
      if (selectedDate === 'thisweek') {
        const dateRange = getThisWeekDateRange();
        gamesData = await getGamesBySport(selectedSport, undefined, dateRange);
      } else if (selectedDate === 'today') {
        gamesData = await getGamesBySport(selectedSport, getTodayDateString());
      } else {
        gamesData = await getGamesBySport(selectedSport, selectedDate);
      }

      const sortedGames = gamesData ? 
        [...new Map(gamesData.map(game => [game.id, game])).values()]
          .sort((a, b) => new Date(a.scheduled_start).getTime() - new Date(b.scheduled_start).getTime())
        : [];

      setGames(sortedGames);
    } catch (error) {
      console.error(`Error loading games for ${selectedSport}:`, error);
      toast.error(`Failed to load ${getSportDisplayName(selectedSport)} games`);
    }
  };

  const handleSyncData = async (silent: boolean = false) => {
    setSyncing(true);
    try {
      const syncOptions = {
        leagues: true,
        teams: true,
        games: true,
        odds: true,
        sport: selectedSport
      };
      
      const result = await syncSportsData(syncOptions);

      if (result?.success) {
        setLastSyncTime(new Date());
        if (!silent) {
          toast.success('Data synced successfully');
        }
        await loadDashboardData();
        await loadGamesForSport();
      } else {
        if (!silent) {
          toast.error('Sync failed');
        }
      }
    } catch (error) {
      console.error('Error syncing data:', error);
      if (!silent) {
        toast.error('Failed to sync sports data');
      }
    } finally {
      setSyncing(false);
    }
  };

  // Filter games by status
  const upcomingGames = games.filter(game => {
    const inferredStatus = getInferredGameStatus(game);
    return inferredStatus === 'scheduled' && !isGameLive(game) && !isGameFinished(game);
  });
  
  const inProgressGames = games.filter(game => {
    return isGameLive(game) && !isGameFinished(game);
  });
  
  const completedGames = games.filter(game => {
    return isGameFinished(game);
  });

  const renderGameCard = (game: Game) => {
    const isLive = isGameLive(game);
    const isFinished = isGameFinished(game);
    const inferredStatus = getInferredGameStatus(game);
    
    return (
      <div 
        key={game.id} 
        className="modern-card"
        onClick={() => {
          navigate(`/betting/game/${game.id}`);
          toast.success(`Opening ${game.away_team_name} vs ${game.home_team_name}`);
        }}
        style={{ cursor: 'pointer' }}
      >
        {/* Status Badge */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div className={`modern-status ${
            isLive ? 'modern-status-live' : 
            isFinished ? 'modern-status-final' :
            'modern-status-scheduled'
          }`}>
            {isLive && <div className="modern-pulse" />}
            {getGameStatusDisplay(inferredStatus)}
          </div>
          
          {game.venue_name && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: 'var(--modern-text-muted)' }}>
              <MapPin size={12} />
              {game.venue_name}
            </div>
          )}
        </div>

        {/* Team Matchup */}
        <div className="modern-team-matchup">
          {/* Away Team */}
          <div className="modern-team">
            <div className="modern-team-logo">
              {game.away_team?.logo_url ? (
                <img 
                  src={game.away_team.logo_url} 
                  alt={game.away_team_name}
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div style={game.away_team?.logo_url ? { display: 'none' } : {}}>
                {game.away_team_abbreviation || game.away_team_name.substring(0, 3).toUpperCase()}
              </div>
            </div>
            <div className="modern-team-name">{game.away_team_name}</div>
            <div className="modern-team-record">
              {game.away_team?.current_record?.wins ? 
                `${game.away_team.current_record.wins}-${game.away_team.current_record.losses}` : 
                ''
              }
            </div>
            {game.away_score !== null && (
              <div className={`modern-score ${game.away_score > (game.home_score || 0) ? 'modern-score-leading' : ''}`}>
                {game.away_score}
              </div>
            )}
          </div>

          {/* VS Divider */}
          <div className="modern-vs-divider">
            <div className="modern-vs-line" />
            <div className="modern-vs-text">VS</div>
            <div className="modern-vs-line" />
          </div>

          {/* Home Team */}
          <div className="modern-team">
            <div className="modern-team-logo">
              {game.home_team?.logo_url ? (
                <img 
                  src={game.home_team.logo_url} 
                  alt={game.home_team_name}
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div style={game.home_team?.logo_url ? { display: 'none' } : {}}>
                {game.home_team_abbreviation || game.home_team_name.substring(0, 3).toUpperCase()}
              </div>
            </div>
            <div className="modern-team-name">{game.home_team_name}</div>
            <div className="modern-team-record">
              {game.home_team?.current_record?.wins ? 
                `${game.home_team.current_record.wins}-${game.home_team.current_record.losses}` : 
                ''
              }
            </div>
            {game.home_score !== null && (
              <div className={`modern-score ${game.home_score > (game.away_score || 0) ? 'modern-score-leading' : ''}`}>
                {game.home_score}
              </div>
            )}
          </div>
        </div>

        {/* Betting Markets */}
        <div className="modern-markets">
          <div className="modern-market-item">
            <div className="modern-market-label">Moneyline</div>
            <div className="modern-market-value">
              {game.away_team_abbreviation} +{Math.floor(Math.random() * 200) + 100}
            </div>
          </div>
          <div className="modern-market-item">
            <div className="modern-market-label">Spread</div>
            <div className="modern-market-value">
              -{(Math.random() * 10 + 1).toFixed(1)}
            </div>
          </div>
          <div className="modern-market-item">
            <div className="modern-market-label">Total</div>
            <div className="modern-market-value">
              O/U {(Math.random() * 20 + 40).toFixed(1)}
            </div>
          </div>
        </div>

        {/* Game Footer */}
        <div className="modern-game-footer">
          <div className="modern-game-time">
            <Clock size={12} />
            <span>{formatGameTime(game.scheduled_start)}</span>
            {game.status === 'scheduled' && (isLive || isFinished) && (
              <span style={{ color: 'var(--modern-accent-warning)', marginLeft: '8px' }}>
                <AlertCircle size={12} style={{ display: 'inline', marginRight: '4px' }} />
                {isLive ? 'Should be live' : 'Likely finished'}
              </span>
            )}
          </div>
          <div className="modern-game-meta">
            {game.week && <span>Week {game.week}</span>}
            <ChevronRight size={14} />
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="modern-loading">
        <div className="modern-spinner" />
      </div>
    );
  }

  return (
    <div style={{ background: 'var(--modern-bg-primary)', minHeight: '100vh', padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '700', color: 'var(--modern-text-primary)' }}>
            Sports Betting Dashboard
          </h1>
          
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            {/* Connection Status */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px',
              padding: '8px 12px',
              background: wsConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${wsConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
              borderRadius: '8px',
              fontSize: '12px',
              color: wsConnected ? 'var(--modern-accent-success)' : 'var(--modern-accent-danger)'
            }}>
              <Wifi size={14} />
              {wsConnected ? 'Connected' : 'Disconnected'}
            </div>

            {/* Auto Sync Toggle */}
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={autoSyncEnabled}
                onChange={(e) => setAutoSyncEnabled(e.target.checked)}
                style={{ width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '14px', color: 'var(--modern-text-secondary)' }}>Auto-sync</span>
            </label>

            {/* Last Sync Time */}
            {lastSyncTime && (
              <div style={{ fontSize: '12px', color: 'var(--modern-text-muted)' }}>
                Last sync: {lastSyncTime.toLocaleTimeString()}
              </div>
            )}

            {/* Sync Button */}
            <Button
              onClick={() => handleSyncData(false)}
              disabled={syncing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                background: 'var(--modern-accent-primary)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                fontSize: '14px',
                fontWeight: '500',
                cursor: syncing ? 'not-allowed' : 'pointer',
                opacity: syncing ? 0.5 : 1
              }}
            >
              <RefreshCw size={16} className={syncing ? 'animate-spin' : ''} />
              Refresh Data
            </Button>

            {/* View Mode Toggle */}
            <div style={{ display: 'flex', gap: '4px', background: 'var(--modern-bg-secondary)', borderRadius: '8px', padding: '4px' }}>
              <button
                onClick={() => setViewMode('grid')}
                style={{
                  padding: '6px 12px',
                  background: viewMode === 'grid' ? 'var(--modern-accent-primary)' : 'transparent',
                  border: 'none',
                  borderRadius: '6px',
                  color: viewMode === 'grid' ? 'white' : 'var(--modern-text-secondary)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '14px'
                }}
              >
                <Grid3x3 size={14} />
                Grid
              </button>
              <button
                onClick={() => setViewMode('list')}
                style={{
                  padding: '6px 12px',
                  background: viewMode === 'list' ? 'var(--modern-accent-primary)' : 'transparent',
                  border: 'none',
                  borderRadius: '6px',
                  color: viewMode === 'list' ? 'white' : 'var(--modern-text-secondary)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '14px'
                }}
              >
                <List size={14} />
                List
              </button>
            </div>
          </div>
        </div>

        {/* Sport Filter */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
          {sportsTypes.map((sport) => (
            <button
              key={sport.sport_type}
              onClick={() => setSelectedSport(sport.sport_type)}
              className={`modern-sport-icon ${selectedSport === sport.sport_type ? 'active' : ''}`}
              title={getSportDisplayName(sport.sport_type)}
            >
              {getSportEmoji(sport.sport_type)}
            </button>
          ))}
        </div>

        {/* Date Filter */}
        <div className="modern-filter-tabs">
          <button
            onClick={() => setSelectedDate('today')}
            className={`modern-filter-tab ${selectedDate === 'today' ? 'active' : ''}`}
          >
            Today
          </button>
          <button
            onClick={() => setSelectedDate('thisweek')}
            className={`modern-filter-tab ${selectedDate === 'thisweek' ? 'active' : ''}`}
          >
            This Week
          </button>
        </div>
      </div>

      {/* Games Sections */}
      {inProgressGames.length > 0 && (
        <div style={{ marginBottom: '48px' }}>
          <div className="modern-section-header">
            <div className="modern-section-title">
              <Zap size={24} color="var(--modern-accent-danger)" />
              Live Games
            </div>
            <div className="modern-section-badge">{inProgressGames.length} games</div>
          </div>
          <div className={viewMode === 'grid' ? 'modern-games-grid' : ''}>
            {inProgressGames.map(renderGameCard)}
          </div>
        </div>
      )}

      {upcomingGames.length > 0 && (
        <div style={{ marginBottom: '48px' }}>
          <div className="modern-section-header">
            <div className="modern-section-title">
              <Timer size={24} color="var(--modern-accent-primary)" />
              Upcoming Games
            </div>
            <div className="modern-section-badge">{upcomingGames.length} games</div>
          </div>
          <div className={viewMode === 'grid' ? 'modern-games-grid' : ''}>
            {upcomingGames.map(renderGameCard)}
          </div>
        </div>
      )}

      {/* Empty State */}
      {games.length === 0 && (
        <div className="modern-empty">
          <div className="modern-empty-icon">{getSportEmoji(selectedSport)}</div>
          <div className="modern-empty-text">No games found</div>
          <div className="modern-empty-subtext">Try selecting a different date or sync data</div>
        </div>
      )}

      {/* All Games Completed */}
      {upcomingGames.length === 0 && inProgressGames.length === 0 && completedGames.length > 0 && (
        <div className="modern-empty">
          <Trophy size={48} color="var(--modern-accent-success)" style={{ marginBottom: '16px' }} />
          <div className="modern-empty-text">All games completed</div>
          <div className="modern-empty-subtext">{completedGames.length} games finished for {selectedDate}</div>
        </div>
      )}
    </div>
  );
}
