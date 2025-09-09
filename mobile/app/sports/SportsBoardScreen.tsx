import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  FlatList,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../../src/styles/theme';
import { NumberField } from '../features/odds/components/NumberField';
import { 
  leagues,
  games,
  markets,
  League, 
  Game, 
  Market, 
  formatCurrency, 
  formatPercentage
} from '../features/sports/api';
import { getKellyThrottled, parseAmericanOddsToNumber } from '../features/odds/kellyClient';

interface ToolbarParams {
  bankroll: string;
  winPct: string;
  fractional: number;
}

interface GameWithMarkets extends Game {
  markets: Market[];
  kellyStakes: { [marketId: string]: number };
}

interface SportsBoardScreenProps {
  initialLeagueId?: string;
}

export default function SportsBoardScreen({ initialLeagueId = 'NCAAF' }: SportsBoardScreenProps) {
  const [selectedLeagueId, setSelectedLeagueId] = useState<string>(initialLeagueId);
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    // Default to today UTC
    const today = new Date();
    today.setUTCHours(0, 0, 0, 0);
    return today.toISOString().split('T')[0];
  });
  
  const [leaguesList, setLeaguesList] = useState<League[]>([]);
  const [gamesList, setGamesList] = useState<GameWithMarkets[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  
  // Toolbar parameters with debounced state
  const [toolbarParams, setToolbarParams] = useState<ToolbarParams>({
    bankroll: '4000',
    winPct: '55',
    fractional: 0.5
  });
  const [toolbarStrings, setToolbarStrings] = useState<ToolbarParams>({
    bankroll: '4000',
    winPct: '55', 
    fractional: 0.5
  });

  // Load leagues on mount
  useEffect(() => {
    loadLeagues();
  }, []);

  // Load games when league or date changes
  useEffect(() => {
    if (selectedLeagueId && selectedDate) {
      loadGames();
    }
  }, [selectedLeagueId, selectedDate]);

  // Debounce toolbar parameter updates
  useEffect(() => {
    const timer = setTimeout(() => {
      setToolbarParams(toolbarStrings);
    }, 200);
    
    return () => clearTimeout(timer);
  }, [toolbarStrings]);

  // Recalculate Kelly when toolbar params change
  useEffect(() => {
    if (gamesList.length > 0 && toolbarParams.bankroll && toolbarParams.winPct) {
      calculateKellyStakes();
    }
  }, [toolbarParams]);

  const loadLeagues = async () => {
    try {
      const fetchedLeagues = await leagues();
      setLeaguesList(fetchedLeagues);
      
      // If initial league not found, use first active league
      const found = fetchedLeagues.find(l => 
        l.code === initialLeagueId || 
        l.id === initialLeagueId || 
        l.name === initialLeagueId
      );
      
      if (!found) {
        const firstActive = fetchedLeagues.find(l => l.active !== false) || fetchedLeagues[0];
        if (firstActive) {
          setSelectedLeagueId(firstActive.code || firstActive.id || firstActive.name);
        }
      } else {
        setSelectedLeagueId(found.code || found.id || found.name);
      }
    } catch (error) {
      console.warn('Failed to load leagues:', error);
      setError('Failed to load leagues');
    }
  };

  const loadGames = useCallback(async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const fetchedGames = await games({
        league: selectedLeagueId,
        date: selectedDate
      });

      // Fetch moneyline markets for each game
      const gamesWithMarkets = await Promise.all(
        fetchedGames.map(async (game) => {
          try {
            const gameMarkets = await markets({
              league: selectedLeagueId,
              game_id: game.id,
              kind: 'moneyline'
            });
            return {
              ...game,
              markets: gameMarkets,
              kellyStakes: {}
            } as GameWithMarkets;
          } catch (error) {
            console.warn(`Failed to load markets for game ${game.id}:`, error);
            return {
              ...game,
              markets: [],
              kellyStakes: {}
            } as GameWithMarkets;
          }
        })
      );

      setGamesList(gamesWithMarkets);
    } catch (error) {
      console.warn('Failed to load games:', error);
      setError(`Failed to load ${selectedLeagueId} games for ${selectedDate}`);
    } finally {
      setIsLoading(false);
    }
  }, [selectedLeagueId, selectedDate]);

  const calculateKellyStakes = useCallback(async () => {
    const bankroll = parseFloat(toolbarParams.bankroll);
    const winPct = parseFloat(toolbarParams.winPct);
    const fractional = toolbarParams.fractional;

    if (isNaN(bankroll) || isNaN(winPct) || bankroll <= 0 || winPct <= 0 || winPct >= 100) {
      return;
    }

    const updatedGames = [...gamesList];
    
    // Process all Kelly calculations in parallel with throttling
    for (let gameIndex = 0; gameIndex < updatedGames.length; gameIndex++) {
      const game = updatedGames[gameIndex];
      const newKellyStakes: { [marketId: string]: number } = {};
      
      const kellyPromises = game.markets.map(async (market) => {
        try {
          // Parse american odds to number
          const americanOdds = parseAmericanOddsToNumber(market.price_american);
          
          const result = await getKellyThrottled({
            american: americanOdds,
            winProbability: winPct / 100,
            bankroll: bankroll,
            fractionalKelly: fractional
          });
          
          newKellyStakes[market.id] = result.recommended_stake || result.stake_recommended || 0;
        } catch (error) {
          console.warn(`Failed to calculate Kelly for market ${market.id}:`, error);
          newKellyStakes[market.id] = 0;
        }
      });
      
      // Wait for all markets in this game to be processed
      await Promise.all(kellyPromises);
      
      updatedGames[gameIndex] = {
        ...game,
        kellyStakes: newKellyStakes
      };
    }
    
    setGamesList(updatedGames);
  }, [gamesList, toolbarParams]);

  const handleRefresh = () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
    loadGames();
  };

  const renderGameItem = ({ item: game }: { item: GameWithMarkets }) => (
    <View style={styles.gameCard}>
      <BlurView intensity={30} tint="dark" style={styles.gameBlur}>
        <LinearGradient
          colors={['rgba(99, 102, 241, 0.1)', 'rgba(139, 92, 246, 0.05)']}
          style={styles.gameGradient}
        >
          <View style={styles.gameHeader}>
            <Text style={styles.gameTitle}>
              {game.away_team_name} @ {game.home_team_name}
            </Text>
            <Text style={styles.gameDate}>
              {new Date(game.start_time).toLocaleDateString()}
            </Text>
          </View>
          
          {game.markets.length > 0 ? (
            <View style={styles.marketsSection}>
              {game.markets.map((market) => {
                const impliedPct = market.implied_probability * 100;
                const kellyStake = game.kellyStakes[market.id] || 0;
                
                return (
                  <View key={market.id} style={styles.marketRow}>
                    <View style={styles.marketInfo}>
                      <Text style={styles.marketName}>{market.name}</Text>
                      <Text style={styles.marketOdds}>{market.price_american}</Text>
                    </View>
                    <View style={styles.marketMetrics}>
                      <Text style={styles.marketImplied}>
                        {formatPercentage(impliedPct)}
                      </Text>
                      <Text style={[
                        styles.marketKelly,
                        kellyStake > 0 ? styles.positiveStake : styles.noStake
                      ]}>
                        {kellyStake > 0 ? formatCurrency(kellyStake) : '$0.00'}
                      </Text>
                    </View>
                  </View>
                );
              })}
            </View>
          ) : (
            <Text style={styles.noMarketsText}>No moneyline yet.</Text>
          )}
        </LinearGradient>
      </BlurView>
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyTitle}>No Games Found</Text>
      <Text style={styles.emptySubtitle}>
        No {selectedLeagueId} games for {selectedDate}
      </Text>
      <TouchableOpacity style={styles.refreshButton} onPress={handleRefresh}>
        <Text style={styles.refreshButtonText}>Try Different Date</Text>
      </TouchableOpacity>
    </View>
  );

  // Get display name for current league
  const currentLeague = useMemo(() => {
    const found = leaguesList.find(l => 
      l.code === selectedLeagueId || 
      l.id === selectedLeagueId || 
      l.name === selectedLeagueId
    );
    return found?.display_name || found?.name || selectedLeagueId;
  }, [leaguesList, selectedLeagueId]);

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />

      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>{currentLeague} Board</Text>
          <Text style={styles.subtitle}>
            Moneyline markets with Kelly stake calculations
          </Text>
        </View>

        {/* Error Banner */}
        {error ? (
          <View style={styles.errorBanner}>
            <Text style={styles.errorText}>⚠️ {error}</Text>
          </View>
        ) : null}

        {/* Toolbar */}
        <View style={styles.toolbar}>
          <BlurView intensity={30} tint="dark" style={styles.toolbarBlur}>
            <LinearGradient
              colors={['rgba(99, 102, 241, 0.1)', 'rgba(139, 92, 246, 0.05)']}
              style={styles.toolbarGradient}
            >
              <Text style={styles.toolbarTitle}>Kelly Parameters</Text>
              <View style={styles.toolbarFields}>
                <View style={styles.toolbarField}>
                  <Text style={styles.fieldLabel}>Bankroll</Text>
                  <NumberField
                    label=""
                    value={toolbarStrings.bankroll}
                    onChangeText={(text) => setToolbarStrings(prev => ({ ...prev, bankroll: text }))}
                    placeholder="4000"
                    prefix="$"
                    keyboardType="decimal-pad"
                  />
                </View>
                <View style={styles.toolbarField}>
                  <Text style={styles.fieldLabel}>Win %</Text>
                  <NumberField
                    label=""
                    value={toolbarStrings.winPct}
                    onChangeText={(text) => setToolbarStrings(prev => ({ ...prev, winPct: text }))}
                    placeholder="55"
                    suffix="%"
                    keyboardType="decimal-pad"
                    min={0}
                    max={100}
                  />
                </View>
                <View style={styles.toolbarField}>
                  <Text style={styles.fieldLabel}>Kelly Fraction</Text>
                  <TouchableOpacity
                    style={styles.fractionSelector}
                    onPress={() => {
                      const options = [0.25, 0.5, 0.75, 1.0];
                      const current = toolbarParams.fractional;
                      const currentIndex = options.indexOf(current);
                      const nextIndex = (currentIndex + 1) % options.length;
                      const nextValue = options[nextIndex];
                      setToolbarStrings(prev => ({ ...prev, fractional: nextValue }));
                    }}
                  >
                    <Text style={styles.fractionText}>{toolbarStrings.fractional}x</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </LinearGradient>
          </BlurView>
        </View>

        {/* Games List */}
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={theme.colors.primary.main} />
            <Text style={styles.loadingText}>Loading {currentLeague} games...</Text>
          </View>
        ) : (
          <FlatList
            data={gamesList}
            renderItem={renderGameItem}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.gamesList}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={renderEmptyState}
            refreshing={isLoading}
            onRefresh={handleRefresh}
          />
        )}
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  safeArea: {
    flex: 1,
  },
  header: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.xl,
    alignItems: 'center',
  },
  title: {
    ...theme.typography.headlineLarge,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    maxWidth: 280,
  },
  errorBanner: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    backgroundColor: theme.colors.error.background,
    borderColor: theme.colors.error.main,
    borderWidth: 1,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
  },
  errorText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.error.main,
    textAlign: 'center',
  },
  toolbar: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
  },
  toolbarBlur: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  toolbarGradient: {
    padding: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  toolbarTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  toolbarFields: {
    flexDirection: 'row',
    gap: theme.spacing.sm,
  },
  toolbarField: {
    flex: 1,
  },
  fieldLabel: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.xs,
    textAlign: 'center',
  },
  fractionSelector: {
    backgroundColor: theme.colors.background.tertiary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    alignItems: 'center',
  },
  fractionText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.md,
  },
  gamesList: {
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: 100,
  },
  gameCard: {
    marginBottom: theme.spacing.lg,
  },
  gameBlur: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  gameGradient: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  gameHeader: {
    marginBottom: theme.spacing.md,
  },
  gameTitle: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.xs,
  },
  gameDate: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
  },
  marketsSection: {
    gap: theme.spacing.sm,
  },
  marketRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  marketInfo: {
    flex: 1,
  },
  marketName: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  marketOdds: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    fontFamily: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
  },
  marketMetrics: {
    alignItems: 'flex-end',
  },
  marketImplied: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
  },
  marketKelly: {
    ...theme.typography.bodyMedium,
    fontWeight: '700',
    marginTop: 2,
  },
  positiveStake: {
    color: theme.colors.success.main,
  },
  noStake: {
    color: theme.colors.text.tertiary,
  },
  noMarketsText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: theme.spacing.xl,
  },
  emptyTitle: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  emptySubtitle: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  refreshButton: {
    backgroundColor: theme.colors.background.tertiary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.lg,
  },
  refreshButtonText: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.primary,
  },
});