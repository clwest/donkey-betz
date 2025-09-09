import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Animated,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../../styles/theme';
import { promptingService } from '../../services/api';

interface PromptEnhancerProps {
  prompt: string;
  onEnhanced?: (enhancedPrompt: string, metadata?: any) => void;
  contentType?: 'image' | 'blog' | 'social' | 'video';
  compact?: boolean;
}

type EnhancementLevel = 'basic' | 'advanced' | 'expert';

export const PromptEnhancer: React.FC<PromptEnhancerProps> = ({
  prompt,
  onEnhanced,
  contentType = 'image',
  compact = false,
}) => {
  const [selectedLevel, setSelectedLevel] = useState<EnhancementLevel>('advanced');
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancedPrompt, setEnhancedPrompt] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [techniques, setTechniques] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [pulseAnim] = useState(new Animated.Value(1));

  const levels: Array<{
    id: EnhancementLevel;
    label: string;
    icon: string;
    description: string;
    gradient: string[];
  }> = [
    {
      id: 'basic',
      label: 'Basic',
      icon: '✨',
      description: 'Simple improvements',
      gradient: ['#10B981', '#34D399'],
    },
    {
      id: 'advanced',
      label: 'Advanced',
      icon: '🚀',
      description: 'Professional quality',
      gradient: ['#6366F1', '#8B5CF6'],
    },
    {
      id: 'expert',
      label: 'Expert',
      icon: '🎯',
      description: 'Maximum creativity',
      gradient: ['#EC4899', '#F472B6'],
    },
  ];

  useEffect(() => {
    // Pulse animation for enhance button
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.05,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  useEffect(() => {
    // Load suggestions for content type
    loadSuggestions();
  }, [contentType]);

  const loadSuggestions = async () => {
    try {
      const data = await promptingService.getSuggestions(contentType);
      setSuggestions(data?.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
      setSuggestions([]);
    }
  };

  const handleEnhance = async () => {
    if (!prompt.trim()) return;

    setIsEnhancing(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    try {
      const result = await promptingService.testEnhancement({
        prompt,
        level: selectedLevel,
        content_type: contentType,
        use_memory: true,
      });

      setEnhancedPrompt(result.enhanced);
      setTechniques(result.techniques || []);
      setShowResult(true);
      
      // Notify parent
      onEnhanced?.(result.enhanced, {
        level: selectedLevel,
        techniques: result.techniques,
        original: prompt,
      });

      // Success haptic
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      console.error('Enhancement failed:', error);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleSelectLevel = (level: EnhancementLevel) => {
    setSelectedLevel(level);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setShowResult(false); // Reset result when changing level
  };

  if (compact) {
    return (
      <View style={styles.compactContainer}>
        <TouchableOpacity
          style={styles.compactButton}
          onPress={handleEnhance}
          disabled={!prompt.trim() || isEnhancing}
        >
          <LinearGradient
            colors={levels.find(l => l.id === selectedLevel)?.gradient || ['#6366F1', '#8B5CF6']}
            style={styles.compactGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
          >
            {isEnhancing ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <>
                <Text style={styles.compactIcon}>✨</Text>
                <Text style={styles.compactText}>Enhance</Text>
              </>
            )}
          </LinearGradient>
        </TouchableOpacity>
        
        <View style={styles.compactLevels}>
          {levels.map((level) => (
            <TouchableOpacity
              key={level.id}
              style={[
                styles.compactLevel,
                selectedLevel === level.id && styles.compactLevelActive,
              ]}
              onPress={() => handleSelectLevel(level.id)}
            >
              <Text style={[
                styles.compactLevelText,
                selectedLevel === level.id && styles.compactLevelTextActive,
              ]}>
                {level.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🎨 Intelligent Prompting</Text>
        <Text style={styles.subtitle}>AI-powered prompt enhancement</Text>
      </View>

      {/* Level Selector */}
      <View style={styles.levelSelector}>
        {levels.map((level) => (
          <TouchableOpacity
            key={level.id}
            style={[
              styles.levelCard,
              selectedLevel === level.id && styles.levelCardActive,
            ]}
            onPress={() => handleSelectLevel(level.id)}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={selectedLevel === level.id ? level.gradient : ['transparent', 'transparent']}
              style={styles.levelGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              <Text style={styles.levelIcon}>{level.icon}</Text>
              <Text style={[
                styles.levelLabel,
                selectedLevel === level.id && styles.levelLabelActive,
              ]}>
                {level.label}
              </Text>
              <Text style={[
                styles.levelDescription,
                selectedLevel === level.id && styles.levelDescriptionActive,
              ]}>
                {level.description}
              </Text>
            </LinearGradient>
          </TouchableOpacity>
        ))}
      </View>

      {/* Enhance Button */}
      <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
        <TouchableOpacity
          style={[
            styles.enhanceButton,
            (!prompt.trim() || isEnhancing) && styles.enhanceButtonDisabled,
          ]}
          onPress={handleEnhance}
          disabled={!prompt.trim() || isEnhancing}
        >
          <LinearGradient
            colors={levels.find(l => l.id === selectedLevel)?.gradient || ['#6366F1', '#8B5CF6']}
            style={styles.enhanceGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
          >
            {isEnhancing ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <>
                <Text style={styles.enhanceIcon}>
                  {levels.find(l => l.id === selectedLevel)?.icon}
                </Text>
                <Text style={styles.enhanceText}>
                  Enhance with {selectedLevel} AI
                </Text>
              </>
            )}
          </LinearGradient>
        </TouchableOpacity>
      </Animated.View>

      {/* Enhancement Result */}
      {showResult && enhancedPrompt && (
        <Animated.View style={styles.resultContainer}>
          <View style={styles.resultHeader}>
            <Text style={styles.resultTitle}>✨ Enhanced Prompt</Text>
            <TouchableOpacity
              onPress={() => {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                onEnhanced?.(enhancedPrompt, { level: selectedLevel });
              }}
            >
              <Text style={styles.useButton}>Use This</Text>
            </TouchableOpacity>
          </View>
          
          <BlurView intensity={20} tint="dark" style={styles.resultContent}>
            <Text style={styles.enhancedText}>{enhancedPrompt}</Text>
          </BlurView>

          {techniques.length > 0 && (
            <View style={styles.techniquesContainer}>
              <Text style={styles.techniquesTitle}>Techniques Applied:</Text>
              <View style={styles.techniquesList}>
                {techniques.map((technique, index) => (
                  <View key={index} style={styles.techniqueChip}>
                    <Text style={styles.techniqueText}>{technique}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}
        </Animated.View>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && !showResult && (
        <View style={styles.suggestionsContainer}>
          <Text style={styles.suggestionsTitle}>💡 Pro Tips</Text>
          <ScrollView style={styles.suggestionsList}>
            {suggestions.slice(0, 3).map((suggestion, index) => (
              <View key={index} style={styles.suggestionItem}>
                <Text style={styles.suggestionDot}>•</Text>
                <Text style={styles.suggestionText}>{suggestion}</Text>
              </View>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  header: {
    marginBottom: 20,
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
  levelSelector: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  levelCard: {
    flex: 1,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    overflow: 'hidden',
  },
  levelCardActive: {
    borderColor: 'transparent',
  },
  levelGradient: {
    padding: 12,
    alignItems: 'center',
  },
  levelIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  levelLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: 2,
  },
  levelLabelActive: {
    color: 'white',
  },
  levelDescription: {
    fontSize: 11,
    color: theme.colors.text.secondary,
  },
  levelDescriptionActive: {
    color: 'rgba(255, 255, 255, 0.8)',
  },
  enhanceButton: {
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 20,
  },
  enhanceButtonDisabled: {
    opacity: 0.5,
  },
  enhanceGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    gap: 8,
  },
  enhanceIcon: {
    fontSize: 20,
  },
  enhanceText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resultContainer: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.secondary,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text.primary,
  },
  useButton: {
    color: theme.colors.primary.main,
    fontSize: 14,
    fontWeight: '600',
  },
  resultContent: {
    padding: 16,
  },
  enhancedText: {
    fontSize: 14,
    color: theme.colors.text.primary,
    lineHeight: 20,
  },
  techniquesContainer: {
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.secondary,
  },
  techniquesTitle: {
    fontSize: 12,
    color: theme.colors.text.secondary,
    marginBottom: 8,
  },
  techniquesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  techniqueChip: {
    backgroundColor: theme.colors.background.tertiary,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  techniqueText: {
    fontSize: 11,
    color: theme.colors.text.secondary,
  },
  suggestionsContainer: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 16,
    padding: 16,
  },
  suggestionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: 12,
  },
  suggestionsList: {
    maxHeight: 100,
  },
  suggestionItem: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  suggestionDot: {
    color: theme.colors.primary.main,
    marginRight: 8,
  },
  suggestionText: {
    flex: 1,
    fontSize: 13,
    color: theme.colors.text.secondary,
    lineHeight: 18,
  },
  // Compact styles
  compactContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 8,
  },
  compactButton: {
    borderRadius: 20,
    overflow: 'hidden',
  },
  compactGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 6,
  },
  compactIcon: {
    fontSize: 16,
  },
  compactText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  compactLevels: {
    flexDirection: 'row',
    gap: 8,
  },
  compactLevel: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  compactLevelActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  compactLevelText: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  compactLevelTextActive: {
    color: 'white',
  },
});