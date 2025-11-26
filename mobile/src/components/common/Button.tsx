import React, { useRef } from 'react';
import { TouchableOpacity, Text, ActivityIndicator, StyleSheet, Animated } from 'react-native';

interface ButtonProps {
  onPress: () => void;
  title: string;
  variant?: 'primary' | 'secondary' | 'ghost' | 'accent';
  disabled?: boolean;
  loading?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export const Button: React.FC<ButtonProps> = ({
  onPress,
  title,
  variant = 'primary',
  disabled = false,
  loading = false,
  size = 'medium',
}) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.97,
      useNativeDriver: true,
      speed: 50,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      speed: 50,
    }).start();
  };

  const getButtonStyle = () => {
    if (disabled) return styles.disabled;
    switch (variant) {
      case 'primary':
        return styles.primary;
      case 'secondary':
        return styles.secondary;
      case 'ghost':
        return styles.ghost;
      case 'accent':
        return styles.accent;
      default:
        return styles.primary;
    }
  };

  const getTextColor = () => {
    if (variant === 'ghost') return '#E8E9EB';
    if (variant === 'accent') return '#0E0F11';
    return '#fff';
  };

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <TouchableOpacity
        style={[styles.button, getButtonStyle(), styles[size]]}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled || loading}
        activeOpacity={0.9}
      >
        {loading ? (
          <ActivityIndicator color={getTextColor()} />
        ) : (
          <Text style={[styles.text, { color: getTextColor() }]}>{title}</Text>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: 24, // Más redondeado (rounded-3xl)
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 6,
    minHeight: 48, // Altura mínima accesible
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  primary: {
    backgroundColor: '#0055FF',
  },
  secondary: {
    backgroundColor: '#3A4558',
  },
  ghost: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: '#3A4558',
    shadowOpacity: 0,
    elevation: 0,
  },
  accent: {
    backgroundColor: '#FFD700',
  },
  disabled: {
    backgroundColor: '#3A4558',
    opacity: 0.5,
  },
  small: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    minHeight: 40,
  },
  medium: {
    paddingVertical: 14,
    paddingHorizontal: 28,
    minHeight: 48,
  },
  large: {
    paddingVertical: 18,
    paddingHorizontal: 36,
    minHeight: 52,
  },
  text: {
    fontSize: 16,
    fontWeight: '600',
  },
});
