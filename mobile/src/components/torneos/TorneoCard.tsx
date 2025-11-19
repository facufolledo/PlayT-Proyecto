import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Torneo } from '../../types';

interface TorneoCardProps {
  torneo: Torneo;
  onPress: () => void;
}

export const TorneoCard = ({ torneo, onPress }: TorneoCardProps) => {
  const getEstadoBadge = (estado: string) => {
    const badges = {
      activo: { text: 'Activo', color: '#00C853' },
      programado: { text: 'Programado', color: '#FFD700' },
      finalizado: { text: 'Finalizado', color: '#64748B' },
    };
    return badges[estado as keyof typeof badges] || badges.activo;
  };

  const badge = getEstadoBadge(torneo.estado);

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.header}>
        <Text style={styles.nombre}>{torneo.nombre}</Text>
        <View style={[styles.estadoBadge, { backgroundColor: badge.color }]}>
          <Text style={styles.estadoText}>{badge.text}</Text>
        </View>
      </View>

      <View style={styles.info}>
        <View style={styles.infoRow}>
          <View style={styles.iconLabel}>
            <Ionicons name="calendar-outline" size={16} color="#0055FF" />
            <Text style={styles.infoLabel}>Inicio:</Text>
          </View>
          <Text style={styles.infoValue}>
            {new Date(torneo.fechaInicio).toLocaleDateString()}
          </Text>
        </View>
        <View style={styles.infoRow}>
          <View style={styles.iconLabel}>
            <Ionicons name="people-outline" size={16} color="#9C27B0" />
            <Text style={styles.infoLabel}>Participantes:</Text>
          </View>
          <Text style={styles.infoValue}>
            {torneo.participantes}
          </Text>
        </View>
        <View style={styles.infoRow}>
          <View style={styles.iconLabel}>
            <Ionicons name="ribbon-outline" size={16} color="#FFD700" />
            <Text style={styles.infoLabel}>Categoría:</Text>
          </View>
          <Text style={styles.infoValue}>{torneo.categoria}</Text>
        </View>
      </View>

      {torneo.descripcion && (
        <Text style={styles.descripcion} numberOfLines={2}>
          {torneo.descripcion}
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  nombre: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E8E9EB',
    flex: 1,
  },
  estadoBadge: {
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  estadoText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  info: {
    gap: 8,
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  iconLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  infoLabel: {
    color: '#94A3B8',
    fontSize: 14,
  },
  infoValue: {
    color: '#E8E9EB',
    fontSize: 14,
    fontWeight: '600',
  },
  descripcion: {
    color: '#94A3B8',
    fontSize: 14,
    lineHeight: 20,
  },
});
