import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Platform,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { theme } from '../../../../src/styles/theme';

export interface SelectFractionProps {
  label: string;
  value: number;
  onValueChange: (value: number) => void;
  options?: { value: number; label: string }[];
  disabled?: boolean;
  error?: string;
}

const DEFAULT_OPTIONS = [
  { value: 0.25, label: '1/4 Kelly (0.25)' },
  { value: 0.5, label: '1/2 Kelly (0.5)' },
  { value: 1.0, label: 'Full Kelly (1.0)' },
];

export const SelectFraction: React.FC<SelectFractionProps> = ({
  label,
  value,
  onValueChange,
  options = DEFAULT_OPTIONS,
  disabled = false,
  error,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const selectedOption = options.find(opt => opt.value === value);

  const handleOptionPress = (optionValue: number) => {
    if (!disabled) {
      if (Platform.OS !== 'web') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
      onValueChange(optionValue);
      setIsExpanded(false);
    }
  };

  const handleToggleExpanded = () => {
    if (!disabled) {
      if (Platform.OS !== 'web') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
      setIsExpanded(!isExpanded);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      
      {/* Selected Value Display */}
      <TouchableOpacity
        style={[
          styles.selector,
          isExpanded && styles.selectorExpanded,
          error && styles.selectorError,
          disabled && styles.selectorDisabled,
        ]}
        onPress={handleToggleExpanded}
        activeOpacity={0.8}
        disabled={disabled}
      >
        <Text style={[
          styles.selectedText,
          disabled && styles.selectedTextDisabled,
        ]}>
          {selectedOption?.label || 'Select Kelly Fraction'}
        </Text>
        <Text style={[
          styles.chevron,
          isExpanded && styles.chevronExpanded,
          disabled && styles.chevronDisabled,
        ]}>
          ▼
        </Text>
      </TouchableOpacity>

      {/* Options List */}
      {isExpanded && (
        <View style={styles.optionsContainer}>
          {options.map((option) => (
            <TouchableOpacity
              key={option.value}
              style={[
                styles.option,
                option.value === value && styles.optionSelected,
              ]}
              onPress={() => handleOptionPress(option.value)}
              activeOpacity={0.8}
            >
              <Text style={[
                styles.optionText,
                option.value === value && styles.optionTextSelected,
              ]}>
                {option.label}
              </Text>
              
              {option.value === value && (
                <Text style={styles.checkmark}>✓</Text>
              )}
            </TouchableOpacity>
          ))}
        </View>
      )}

      {error && (
        <Text style={styles.errorText}>{error}</Text>
      )}
      
      {/* Kelly Fraction Info */}
      <View style={styles.infoContainer}>
        <Text style={styles.infoText}>
          Kelly fraction determines what percentage of the calculated Kelly bet to use.
        </Text>
        <View style={styles.infoGrid}>
          <Text style={styles.infoItem}>• 1/4 Kelly: Conservative (25%)</Text>
          <Text style={styles.infoItem}>• 1/2 Kelly: Moderate (50%)</Text>
          <Text style={styles.infoItem}>• Full Kelly: Aggressive (100%)</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: theme.spacing.md,
  },
  label: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.xs,
  },
  selector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    minHeight: 48,
  },
  selectorExpanded: {
    borderColor: theme.colors.primary.main,
    backgroundColor: theme.colors.background.tertiary,
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
  },
  selectorError: {
    borderColor: theme.colors.error.main,
  },
  selectorDisabled: {
    backgroundColor: theme.colors.background.primary,
    opacity: 0.6,
  },
  selectedText: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.primary,
    flex: 1,
  },
  selectedTextDisabled: {
    color: theme.colors.text.disabled,
  },
  chevron: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    fontSize: 12,
    transform: [{ rotate: '0deg' }],
  },
  chevronExpanded: {
    transform: [{ rotate: '180deg' }],
    color: theme.colors.primary.main,
  },
  chevronDisabled: {
    color: theme.colors.text.disabled,
  },
  optionsContainer: {
    backgroundColor: theme.colors.background.tertiary,
    borderWidth: 1,
    borderColor: theme.colors.primary.main,
    borderTopWidth: 0,
    borderBottomLeftRadius: theme.borderRadius.md,
    borderBottomRightRadius: theme.borderRadius.md,
    ...theme.shadows.md,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.secondary,
  },
  optionSelected: {
    backgroundColor: theme.colors.primary.main + '20',
  },
  optionText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    flex: 1,
  },
  optionTextSelected: {
    color: theme.colors.primary.main,
    fontWeight: '600',
  },
  checkmark: {
    ...theme.typography.bodyMedium,
    color: theme.colors.primary.main,
    fontSize: 16,
    fontWeight: 'bold',
  },
  errorText: {
    ...theme.typography.bodySmall,
    color: theme.colors.error.main,
    marginTop: theme.spacing.xs,
  },
  infoContainer: {
    marginTop: theme.spacing.sm,
    padding: theme.spacing.sm,
    backgroundColor: theme.colors.info.background,
    borderRadius: theme.borderRadius.sm,
    borderLeftWidth: 3,
    borderLeftColor: theme.colors.info.main,
  },
  infoText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.xs,
  },
  infoGrid: {
    gap: theme.spacing.xs / 2,
  },
  infoItem: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.tertiary,
    fontSize: 11,
  },
});

export default SelectFraction;