import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { theme } from '../../styles/theme';
import { styleMemoryService } from '../../services/api';

interface StyleSuggestion {
  style: string;
  confidence: number;
  reason: string;
  basedOn?: string[];
}

interface StyleSuggestionsProps {
  prompt?: string;
  onSelectStyle?: (style: string) => void;
  compact?: boolean;
}

export const StyleSuggestions: React.FC<StyleSuggestionsProps> = ({
  prompt,
  onSelectStyle,
  compact = false,
}) => {
  const [suggestions, setSuggestions] = useState<StyleSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState<any>(null);

  useEffect(() => {
    loadSuggestions();
    loadInsights();
  }, [prompt]);

  const loadSuggestions = async () => {
    setLoading(true);
    try {
      const data = await styleMemoryService.getSuggestions();
      setSuggestions(data || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadInsights = async () => {
    try {
      const data = await styleMemoryService.getInsights();
      setInsights(data);
    } catch (error) {
      console.error('Failed to load insights:', error);
    }
  };

  const handleSelectStyle = (style: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    onSelectStyle?.(style);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#10B981';
    if (confidence >= 0.6) return '#F59E0B';
    return '#6B7280';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'Strong Match';
    if (confidence >= 0.6) return 'Good Match';
    return 'Possible Match';
  };

  if (loading && suggestions.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="small" color={theme.colors.primary.main} />
        <Text style={styles.loadingText}>Learning your style...</Text>
      </View>
    );
  }

  if (compact) {
    return (
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.compactContainer}
      >
        <View style={styles.compactHeader}>
          <Text style={styles.compactIcon}>✨</Text>
          <Text style={styles.compactTitle}>AI Suggests:</Text>
        </View>
        {suggestions.slice(0, 3).map((suggestion, index) => (
          <TouchableOpacity
            key={index}
            style={styles.compactChip}
            onPress={() => handleSelectStyle(suggestion.style)}
          >
            <LinearGradient
              colors={['#6366F1', '#8B5CF6']}
              style={styles.compactChipGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
            >
              <Text style={styles.compactChipText}>{suggestion.style}</Text>
              <Text style={styles.compactChipConfidence}>
                {Math.round(suggestion.confidence * 100)}%
              </Text>
            </LinearGradient>
          </TouchableOpacity>
        ))}
      </ScrollView>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🎨 Style Suggestions</Text>
        {insights && (
          <Text style={styles.subtitle}>
            Based on your {insights.total_interactions || 0} preferences
          </Text>
        )}
      </View>

      {suggestions.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>🎭</Text>
          <Text style={styles.emptyText}>
            Rate more images to get personalized suggestions
          </Text>
        </View>
      ) : (
        <ScrollView showsVerticalScrollIndicator={false}>
          {suggestions.map((suggestion, index) => (
            <TouchableOpacity
              key={index}
              style={styles.suggestionCard}
              onPress={() => handleSelectStyle(suggestion.style)}
              activeOpacity={0.8}
            >
              <View style={styles.suggestionHeader}>
                <Text style={styles.suggestionStyle}>{suggestion.style}</Text>
                <View style={styles.confidenceBadge}>
                  <View
                    style={[
                      styles.confidenceDot,
                      { backgroundColor: getConfidenceColor(suggestion.confidence) },
                    ]}
                  />
                  <Text style={styles.confidenceText}>
                    {getConfidenceLabel(suggestion.confidence)}
                  </Text>
                </View>
              </View>

              <Text style={styles.suggestionReason}>{suggestion.reason}</Text>

              {suggestion.basedOn && suggestion.basedOn.length > 0 && (
                <View style={styles.basedOnContainer}>
                  <Text style={styles.basedOnLabel}>Based on:</Text>
                  <View style={styles.basedOnTags}>
                    {suggestion.basedOn.slice(0, 3).map((item, i) => (
                      <View key={i} style={styles.tag}>
                        <Text style={styles.tagText}>{item}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              )}

              <View style={styles.suggestionFooter}>
                <Text style={styles.selectText}>Tap to use this style →</Text>
              </View>
            </TouchableOpacity>
          ))}

          {insights && insights.style_preferences && (
            <View style={styles.insightsCard}>
              <Text style={styles.insightsTitle}>Your Style DNA</Text>
              <View style={styles.dnaContainer}>
                {Object.entries(insights.style_preferences)
                  .slice(0, 5)
                  .map(([style, count]: [string, any], index) => (
                    <View key={index} style={styles.dnaItem}>
                      <Text style={styles.dnaStyle}>{style}</Text>
                      <View style={styles.dnaBar}>
                        <View
                          style={[
                            styles.dnaBarFill,
                            { width: `${(count / insights.total_interactions) * 100}%` },
                          ]}
                        />
                      </View>
                    </View>
                  ))}
              </View>
            </View>
          )}
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    padding: 24,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 8,
    fontSize: 14,
    color: theme.colors.text.secondary,
  },
  header: {
    marginBottom: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
  },
  subtitle: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginTop: 4,
  },
  suggestionCard: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  suggestionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  suggestionStyle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text.primary,
  },
  confidenceBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  confidenceDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  confidenceText: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  suggestionReason: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginBottom: 12,
  },
  basedOnContainer: {
    marginTop: 8,
  },
  basedOnLabel: {
    fontSize: 12,
    color: theme.colors.text.secondary,
    marginBottom: 6,
  },
  basedOnTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  tag: {
    backgroundColor: theme.colors.background.tertiary,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tagText: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  suggestionFooter: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.secondary,
  },
  selectText: {
    fontSize: 14,
    color: theme.colors.primary.main,
    fontWeight: '500',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 48,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  insightsCard: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 16,
    padding: 16,
    marginTop: 8,
  },
  insightsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: 12,
  },
  dnaContainer: {
    gap: 8,
  },
  dnaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  dnaStyle: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    width: 100,
  },
  dnaBar: {
    flex: 1,
    height: 4,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: 2,
  },
  dnaBarFill: {
    height: '100%',
    backgroundColor: theme.colors.primary.main,
    borderRadius: 2,
  },
  // Compact styles
  compactContainer: {
    paddingVertical: 8,
  },
  compactHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
  },
  compactIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  compactTitle: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    fontWeight: '500',
  },
  compactChip: {
    marginRight: 8,
    borderRadius: 20,
    overflow: 'hidden',
  },
  compactChipGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 6,
    gap: 6,
  },
  compactChipText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  compactChipConfidence: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 12,
  },
});