import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { theme } from '../../../../src/styles/theme';

export interface NumberFieldProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  prefix?: string;
  suffix?: string;
  keyboardType?: 'numeric' | 'decimal-pad' | 'number-pad';
  error?: string;
  disabled?: boolean;
  min?: number;
  max?: number;
  integer?: boolean;
  allowNegative?: boolean;
}

export const NumberField: React.FC<NumberFieldProps> = ({
  label,
  value,
  onChangeText,
  placeholder,
  prefix,
  suffix,
  keyboardType = 'numeric',
  error,
  disabled = false,
  min,
  max,
  integer = false,
  allowNegative = false,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<TextInput>(null);

  const handleChangeText = (text: string) => {
    let processedText = text;

    // Handle special cases for odds (allow +/- at start)
    if (allowNegative && (text.startsWith('+') || text.startsWith('-'))) {
      // Allow +/- prefix for odds
      const sign = text.charAt(0);
      const numberPart = text.slice(1);
      
      if (numberPart === '' || /^\d+$/.test(numberPart)) {
        processedText = sign + numberPart;
      } else {
        return; // Invalid format
      }
    } else {
      // Regular number validation
      if (integer) {
        // Only allow integers
        if (text !== '' && !/^\d+$/.test(text)) {
          return;
        }
      } else {
        // Allow decimals
        if (text !== '' && !/^\d*\.?\d*$/.test(text)) {
          return;
        }
      }

      // Apply min/max constraints if specified
      if (text !== '' && !isNaN(Number(text))) {
        const num = Number(text);
        if (min !== undefined && num < min) {
          return;
        }
        if (max !== undefined && num > max) {
          return;
        }
      }
    }

    onChangeText(processedText);
  };

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  const handleContainerPress = () => {
    if (!disabled) {
      inputRef.current?.focus();
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      
      <TouchableOpacity
        activeOpacity={1}
        onPress={handleContainerPress}
        style={[
          styles.inputContainer,
          isFocused && styles.inputContainerFocused,
          error && styles.inputContainerError,
          disabled && styles.inputContainerDisabled,
        ]}
      >
        {prefix && (
          <Text style={[styles.affix, disabled && styles.affixDisabled]}>
            {prefix}
          </Text>
        )}
        
        <TextInput
          ref={inputRef}
          style={[
            styles.input,
            disabled && styles.inputDisabled,
          ]}
          value={value}
          onChangeText={handleChangeText}
          placeholder={placeholder}
          placeholderTextColor={theme.colors.text.tertiary}
          keyboardType={keyboardType}
          editable={!disabled}
          selectTextOnFocus
          onFocus={handleFocus}
          onBlur={handleBlur}
          returnKeyType="done"
          clearButtonMode="while-editing"
        />
        
        {suffix && (
          <Text style={[styles.affix, disabled && styles.affixDisabled]}>
            {suffix}
          </Text>
        )}
      </TouchableOpacity>
      
      {error && (
        <Text style={styles.errorText}>{error}</Text>
      )}
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
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    paddingHorizontal: theme.spacing.md,
    minHeight: 48,
  },
  inputContainerFocused: {
    borderColor: theme.colors.primary.main,
    backgroundColor: theme.colors.background.tertiary,
  },
  inputContainerError: {
    borderColor: theme.colors.error.main,
  },
  inputContainerDisabled: {
    backgroundColor: theme.colors.background.primary,
    opacity: 0.6,
  },
  input: {
    flex: 1,
    ...theme.typography.bodyLarge,
    color: theme.colors.text.primary,
    paddingVertical: Platform.OS === 'ios' ? theme.spacing.sm : theme.spacing.xs,
    textAlign: 'left',
  },
  inputDisabled: {
    color: theme.colors.text.disabled,
  },
  affix: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    marginHorizontal: theme.spacing.xs,
  },
  affixDisabled: {
    color: theme.colors.text.disabled,
  },
  errorText: {
    ...theme.typography.bodySmall,
    color: theme.colors.error.main,
    marginTop: theme.spacing.xs,
  },
});

export default NumberField;