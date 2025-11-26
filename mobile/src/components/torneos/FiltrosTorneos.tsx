import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface FiltrosTorneosProps {
  filtroActivo: 'todos' | 'activos' | 'finalizados';
  onFiltroChange: (filtro: 'todos' | 'activos' | 'finalizados') => void;
}

export const FiltrosTorneos = ({ filtroActivo, onFiltroChange }: FiltrosTorneosProps) => {
  const filtros = [
    { value: 'todos', label: 'Todos' },
    { value: 'activos', label: 'Activos' },
    { value: 'finalizados', label: 'Finalizados' },
  ] as const;

  return (
    <View style={styles.container}>
      {filtros.map((filtro) => (
        <TouchableOpacity
          key={filtro.value}
          style={[
            styles.filtroButton,
            filtroActivo === filtro.value && styles.filtroButtonActive
          ]}
          onPress={() => onFiltroChange(filtro.value)}
        >
          <Text style={[
            styles.filtroText,
            filtroActivo === filtro.value && styles.filtroTextActive
          ]}>
            {filtro.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: 8,
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  filtroButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#3A4558',
  },
  filtroButtonActive: {
    backgroundColor: '#FFD700',
  },
  filtroText: {
    color: '#94A3B8',
    fontWeight: '600',
    fontSize: 14,
  },
  filtroTextActive: {
    color: '#0E0F11',
  },
});
