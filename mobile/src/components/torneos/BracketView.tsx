import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

interface Partido {
  id: number;
  jugador1?: string;
  jugador2?: string;
  ganador?: string;
  ronda: number;
}

interface BracketViewProps {
  partidos: Partido[];
  formato: string;
}

export const BracketView = ({ partidos, formato }: BracketViewProps) => {
  // Agrupar partidos por ronda
  const partidosPorRonda = partidos.reduce((acc, partido) => {
    if (!acc[partido.ronda]) {
      acc[partido.ronda] = [];
    }
    acc[partido.ronda].push(partido);
    return acc;
  }, {} as Record<number, Partido[]>);

  const rondas = Object.keys(partidosPorRonda).sort((a, b) => Number(a) - Number(b));

  if (partidos.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>🏆</Text>
        <Text style={styles.emptyText}>El bracket se generará cuando inicie el torneo</Text>
      </View>
    );
  }

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.container}>
      <View style={styles.bracketContainer}>
        {rondas.map((ronda) => (
          <View key={ronda} style={styles.rondaContainer}>
            <Text style={styles.rondaTitle}>
              {Number(ronda) === rondas.length ? 'Final' : `Ronda ${ronda}`}
            </Text>
            {partidosPorRonda[Number(ronda)].map((partido) => (
              <View key={partido.id} style={styles.partidoCard}>
                <View style={[
                  styles.jugadorRow,
                  partido.ganador === partido.jugador1 && styles.jugadorGanador
                ]}>
                  <Text style={styles.jugadorNombre}>
                    {partido.jugador1 || 'TBD'}
                  </Text>
                  {partido.ganador === partido.jugador1 && (
                    <Text style={styles.checkIcon}>✓</Text>
                  )}
                </View>
                <View style={styles.divider} />
                <View style={[
                  styles.jugadorRow,
                  partido.ganador === partido.jugador2 && styles.jugadorGanador
                ]}>
                  <Text style={styles.jugadorNombre}>
                    {partido.jugador2 || 'TBD'}
                  </Text>
                  {partido.ganador === partido.jugador2 && (
                    <Text style={styles.checkIcon}>✓</Text>
                  )}
                </View>
              </View>
            ))}
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  bracketContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 24,
  },
  rondaContainer: {
    gap: 16,
  },
  rondaTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFD700',
    marginBottom: 8,
    textAlign: 'center',
  },
  partidoCard: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 8,
    padding: 12,
    minWidth: 200,
  },
  jugadorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  jugadorGanador: {
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
  },
  jugadorNombre: {
    fontSize: 14,
    color: '#E8E9EB',
    flex: 1,
  },
  checkIcon: {
    color: '#FFD700',
    fontSize: 16,
    fontWeight: 'bold',
  },
  divider: {
    height: 1,
    backgroundColor: '#3A4558',
    marginVertical: 4,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
  },
});
