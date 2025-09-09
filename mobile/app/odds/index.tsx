import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../../src/styles/theme';
import { NumberField } from '../features/odds/components/NumberField';
import { SelectFraction } from '../features/odds/components/SelectFraction';
import {
  dbaoApi,
  DBAOApiError,
  parseAmericanOdds,
  isValidAmericanOdds,
  formatCurrency,
  formatPercentage,
  type OddsConvertResponse,
  type KellyResponse,
} from '../features/odds/api';

interface CalculatorInputs {
  americanOdds: string;
  winProbability: string;
  bankroll: string;
  kellyFraction: number;
}

interface CalculatorResults {
  decimalOdds?: number;
  impliedProbability?: number;
  expectedValue?: number;
  fullKellyPercentage?: number;
  recommendedStake?: number;
  isPositiveEv?: boolean;
}

const STORAGE_KEY = 'odds_calculator_inputs';

const DEFAULT_INPUTS: CalculatorInputs = {
  americanOdds: '',
  winProbability: '58',
  bankroll: '4000',
  kellyFraction: 0.5,
};

export default function OddsCalculatorScreen() {
  const [inputs, setInputs] = useState<CalculatorInputs>(DEFAULT_INPUTS);
  const [results, setResults] = useState<CalculatorResults>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof CalculatorInputs, string>>>({});
  const [apiError, setApiError] = useState<string>('');

  // Load saved inputs on mount
  useEffect(() => {
    loadSavedInputs();
  }, []);

  // Save inputs whenever they change (debounced to avoid excessive writes)
  useEffect(() => {
    const timer = setTimeout(() => {
      saveInputs();
    }, 500);
    
    return () => clearTimeout(timer);
  }, [inputs]);

  const loadSavedInputs = async () => {
    try {
      const saved = await AsyncStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        setInputs({ ...DEFAULT_INPUTS, ...parsed });
      }
    } catch (error) {
      console.warn('Failed to load saved inputs:', error);
    }
  };

  const saveInputs = async () => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(inputs));
    } catch (error) {
      console.warn('Failed to save inputs:', error);
    }
  };

  const validateInputs = (): boolean => {
    const newErrors: Partial<Record<keyof CalculatorInputs, string>> = {};

    // Validate American Odds
    if (!inputs.americanOdds.trim()) {
      newErrors.americanOdds = 'American odds are required';
    } else if (!isValidAmericanOdds(inputs.americanOdds)) {
      newErrors.americanOdds = 'Enter valid odds (e.g., +110, -135)';
    }

    // Validate Win Probability
    const winProb = parseFloat(inputs.winProbability);
    if (isNaN(winProb) || winProb < 0 || winProb > 100) {
      newErrors.winProbability = 'Enter probability between 0-100%';
    }

    // Validate Bankroll
    const bankroll = parseFloat(inputs.bankroll);
    if (isNaN(bankroll) || bankroll <= 0) {
      newErrors.bankroll = 'Enter positive bankroll amount';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCalculate = async () => {
    console.log('[OddsCalculator] Starting calculation with inputs:', inputs);
    setApiError('');
    
    if (!validateInputs()) {
      console.log('[OddsCalculator] Validation failed');
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
      return;
    }

    setIsLoading(true);

    try {
      // Step 1: Convert American odds to decimal
      const parsedOdds = parseAmericanOdds(inputs.americanOdds);
      console.log('[OddsCalculator] Parsed American odds:', parsedOdds);
      
      const oddsResponse: OddsConvertResponse = await dbaoApi.convertOdds({
        american_odds: parsedOdds,
      });
      console.log('[OddsCalculator] Odds conversion response:', oddsResponse);

      // Step 2: Calculate Kelly criterion
      const kellyRequest = {
        decimal_odds: oddsResponse.decimal_odds,
        win_probability: parseFloat(inputs.winProbability),
        bankroll: parseFloat(inputs.bankroll),
        fractional_kelly: inputs.kellyFraction,
      };
      console.log('[OddsCalculator] Kelly request:', kellyRequest);
      
      const kellyResponse: KellyResponse = await dbaoApi.calculateKelly(kellyRequest);
      console.log('[OddsCalculator] Kelly response:', kellyResponse);

      // Update results
      const newResults = {
        decimalOdds: oddsResponse.decimal_odds,
        impliedProbability: oddsResponse.implied_probability,
        expectedValue: kellyResponse.expected_value,
        fullKellyPercentage: kellyResponse.full_kelly_percentage,
        recommendedStake: kellyResponse.recommended_stake,
        isPositiveEv: kellyResponse.is_positive_ev,
      };
      console.log('[OddsCalculator] Setting results:', newResults);
      setResults(newResults);

      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }

    } catch (error) {
      console.error('[OddsCalculator] Calculation error:', error);
      console.error('[OddsCalculator] Error details:', {
        name: (error as any)?.name,
        message: (error as any)?.message,
        status: (error as any)?.status,
        data: (error as any)?.data,
      });
      
      if (error instanceof DBAOApiError) {
        setApiError(error.message);
      } else {
        setApiError('Calculation failed. Please try again.');
      }

      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
    
    setInputs(DEFAULT_INPUTS);
    setResults({});
    setErrors({});
    setApiError('');
  };

  const updateInput = useCallback((field: keyof CalculatorInputs, value: string | number) => {
    setInputs(prev => ({
      ...prev,
      [field]: value,
    }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
      }));
    }
  }, [errors]);

  const hasResults = Object.keys(results).some(key => results[key as keyof CalculatorResults] !== undefined);
  const showNegativeKellyWarning = results.isPositiveEv === false;

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView 
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Odds Calculator</Text>
            <Text style={styles.subtitle}>
              Calculate expected value and Kelly criterion for sports betting
            </Text>
          </View>

          {/* API Error Banner */}
          {apiError ? (
            <View style={styles.errorBanner}>
              <Text style={styles.errorBannerText}>⚠️ {apiError}</Text>
              {apiError.includes('DBAO_API_URL') && (
                <Text style={styles.errorBannerSubtext}>
                  Check your environment configuration
                </Text>
              )}
            </View>
          ) : null}

          {/* Input Card */}
          <View style={styles.card}>
            <BlurView intensity={30} tint="dark" style={styles.blurCard}>
              <LinearGradient
                colors={['rgba(99, 102, 241, 0.1)', 'rgba(139, 92, 246, 0.05)']}
                style={styles.cardGradient}
              >
                <Text style={styles.cardTitle}>Betting Parameters</Text>

                <NumberField
                  label="American Odds"
                  value={inputs.americanOdds}
                  onChangeText={(text) => updateInput('americanOdds', text)}
                  placeholder="+110 or -135"
                  keyboardType="numeric"
                  allowNegative={true}
                  error={errors.americanOdds}
                />

                <NumberField
                  label="Win Probability"
                  value={inputs.winProbability}
                  onChangeText={(text) => updateInput('winProbability', text)}
                  placeholder="58"
                  suffix="%"
                  keyboardType="decimal-pad"
                  min={0}
                  max={100}
                  error={errors.winProbability}
                />

                <NumberField
                  label="Bankroll"
                  value={inputs.bankroll}
                  onChangeText={(text) => updateInput('bankroll', text)}
                  placeholder="4000"
                  prefix="$"
                  keyboardType="decimal-pad"
                  error={errors.bankroll}
                />

                <SelectFraction
                  label="Kelly Fraction"
                  value={inputs.kellyFraction}
                  onValueChange={(value) => updateInput('kellyFraction', value)}
                  error={errors.kellyFraction}
                />
              </LinearGradient>
            </BlurView>
          </View>

          {/* Action Buttons */}
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[styles.button, styles.resetButton]}
              onPress={handleReset}
              activeOpacity={0.8}
            >
              <Text style={styles.resetButtonText}>Reset</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.button,
                styles.calculateButton,
                isLoading && styles.buttonDisabled,
              ]}
              onPress={handleCalculate}
              disabled={isLoading}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={theme.colors.primary.gradient}
                style={styles.buttonGradient}
              >
                {isLoading ? (
                  <ActivityIndicator color="white" size="small" />
                ) : (
                  <Text style={styles.calculateButtonText}>Calculate</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </View>

          {/* Results Card */}
          {hasResults && (
            <View style={styles.card}>
              <BlurView intensity={30} tint="dark" style={styles.blurCard}>
                <LinearGradient
                  colors={['rgba(16, 185, 129, 0.1)', 'rgba(34, 197, 94, 0.05)']}
                  style={styles.cardGradient}
                >
                  <Text style={styles.cardTitle}>Results</Text>

                  {showNegativeKellyWarning && (
                    <View style={styles.warningBox}>
                      <Text style={styles.warningText}>
                        ⚠️ Negative Kelly; no bet recommended
                      </Text>
                    </View>
                  )}

                  <View style={styles.resultsGrid}>
                    <View style={styles.resultItem}>
                      <Text style={styles.resultLabel}>Decimal Odds</Text>
                      <Text style={styles.resultValue}>
                        {results.decimalOdds?.toFixed(2) || '—'}
                      </Text>
                    </View>

                    <View style={styles.resultItem}>
                      <Text style={styles.resultLabel}>Implied Probability</Text>
                      <Text style={styles.resultValue}>
                        {results.impliedProbability ? formatPercentage(results.impliedProbability) : '—'}
                      </Text>
                    </View>

                    <View style={styles.resultItem}>
                      <Text style={styles.resultLabel}>Expected Value</Text>
                      <Text style={[
                        styles.resultValue,
                        results.expectedValue && results.expectedValue > 0 ? styles.positiveValue : styles.negativeValue,
                      ]}>
                        {results.expectedValue ? 
                          `${results.expectedValue > 0 ? '+' : ''}${results.expectedValue.toFixed(2)}%` : '—'}
                      </Text>
                    </View>

                    <View style={styles.resultItem}>
                      <Text style={styles.resultLabel}>Full Kelly %</Text>
                      <Text style={styles.resultValue}>
                        {results.fullKellyPercentage ? formatPercentage(results.fullKellyPercentage) : '—'}
                      </Text>
                    </View>

                    <View style={[styles.resultItem, styles.stakeItem]}>
                      <Text style={styles.resultLabel}>Recommended Stake</Text>
                      <Text style={[styles.resultValue, styles.stakeValue]}>
                        {results.recommendedStake ? formatCurrency(results.recommendedStake) : '—'}
                      </Text>
                    </View>
                  </View>
                </LinearGradient>
              </BlurView>
            </View>
          )}

          {/* Info Card */}
          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>About Kelly Criterion</Text>
            <Text style={styles.infoText}>
              The Kelly criterion helps determine optimal bet sizing based on edge and odds. 
              It maximizes long-term growth while managing risk.
            </Text>
            <Text style={styles.infoNote}>
              💡 Only bet when EV is positive and use fractional Kelly for risk management.
            </Text>
          </View>
        </ScrollView>
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
  scrollContent: {
    paddingBottom: 100,
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
  errorBannerText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.error.main,
    fontWeight: '600',
  },
  errorBannerSubtext: {
    ...theme.typography.bodySmall,
    color: theme.colors.error.main,
    marginTop: theme.spacing.xs,
    opacity: 0.8,
  },
  card: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.xl,
  },
  blurCard: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  cardGradient: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  cardTitle: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.lg,
    textAlign: 'center',
  },
  buttonRow: {
    flexDirection: 'row',
    paddingHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.xl,
    gap: theme.spacing.md,
  },
  button: {
    flex: 1,
    height: 54,
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  resetButton: {
    backgroundColor: theme.colors.background.secondary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  resetButtonText: {
    ...theme.typography.labelLarge,
    color: theme.colors.text.secondary,
    fontWeight: '600',
  },
  calculateButton: {
    flex: 2,
  },
  buttonGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  calculateButtonText: {
    ...theme.typography.labelLarge,
    color: 'white',
    fontWeight: '700',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  warningBox: {
    backgroundColor: theme.colors.error.background,
    borderColor: theme.colors.error.main,
    borderWidth: 1,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.lg,
  },
  warningText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.error.main,
    fontWeight: '600',
    textAlign: 'center',
  },
  resultsGrid: {
    gap: theme.spacing.lg,
  },
  resultItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.sm,
  },
  stakeItem: {
    backgroundColor: theme.colors.background.tertiary,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  resultLabel: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
  },
  resultValue: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    fontWeight: '700',
  },
  stakeValue: {
    ...theme.typography.headlineSmall,
    color: theme.colors.primary.main,
  },
  positiveValue: {
    color: theme.colors.success.main,
  },
  negativeValue: {
    color: theme.colors.error.main,
  },
  infoCard: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.xl,
    backgroundColor: theme.colors.info.background,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.info.main,
  },
  infoTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  infoText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    lineHeight: 22,
    marginBottom: theme.spacing.sm,
  },
  infoNote: {
    ...theme.typography.bodySmall,
    color: theme.colors.info.main,
    fontStyle: 'italic',
  },
});