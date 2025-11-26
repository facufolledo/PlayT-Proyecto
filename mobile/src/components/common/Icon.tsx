import React from 'react';
import { Text, StyleSheet } from 'react-native';

// Sistema de iconos consistente usando emojis modernos
// En producción, reemplazar con Lucide o Phosphor Icons

interface IconProps {
  name: string;
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  color?: string;
}

const ICON_MAP = {
  // Navegación
  home: '🏠',
  trophy: '🏆',
  gamepad: '🎮',
  chart: '📊',
  user: '👤',
  
  // Acciones
  plus: '➕',
  minus: '➖',
  check: '✓',
  close: '✕',
  edit: '✏️',
  delete: '🗑️',
  settings: '⚙️',
  
  // Estados
  live: '🔴',
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️',
  
  // Deportes
  paddle: '🎾',
  medal: '🏅',
  star: '⭐',
  fire: '🔥',
  
  // Comunicación
  bell: '🔔',
  message: '💬',
  email: '📧',
  phone: '📱',
  
  // Otros
  calendar: '📅',
  clock: '⏰',
  location: '📍',
  search: '🔍',
  filter: '🔽',
  arrow: '→',
  back: '←',
};

const SIZE_MAP = {
  small: 20,
  medium: 24,
  large: 28,
  xlarge: 32,
};

export const Icon = ({ name, size = 'medium', color }: IconProps) => {
  const icon = ICON_MAP[name as keyof typeof ICON_MAP] || '•';
  const fontSize = SIZE_MAP[size];

  return (
    <Text style={[styles.icon, { fontSize, color }]}>
      {icon}
    </Text>
  );
};

const styles = StyleSheet.create({
  icon: {
    textAlign: 'center',
  },
});
