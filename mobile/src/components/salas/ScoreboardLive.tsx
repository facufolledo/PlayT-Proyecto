import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ScoreboardLiveProps {
  equipo1: string;
  equipo2: string;
  marcador: {
    equipo1Puntos: number;
    equipo2Puntos: number;
    equipo1Sets: number;
    equipo2Sets: number;
    estado: string;
  };
}

export const ScoreboardLive = ({ equipo1, equipo2, marcador }: ScoreboardLiveProps) => {
  const equipo1Ganando = marcador.equipo1Puntos > marcador.equipo2Puntos;
  const equipo2Ganando = marcador.equipo2Puntos > marcador.equipo1Puntos;

  return (
    <View style={styles.container}>
      {/* Sets */}
      <View style={styles.setsContainer}>
        <View style={styles.setCard}>
          <Text style={styles.setLabel}>Sets</Text>
          <View style={styles.setScores}>
            <Text style={[
              styles.setScore,
              marcador.equipo1Sets > marcador.equipo2Sets && styles.setScoreWinning
            ]}>
              {marcador.equipo1Sets}
            </Text>
            <Text style={styles.setDivider}>-</Text>
            <Text style={[
              styles.setScore,
              marcador.equipo2Sets > marcador.equipo1Sets && styles.setScoreWinning
            ]}>
              {marcador.equipo2Sets}
            </Text>
          </View>
        </View>
      </View>

      {/* Marcador Principal */}
      <View style={styles.mainScoreboard}>
        {/* Equipo 1 */}
        <View style={[
          styles.teamContainer,
          equipo1Ganando && styles.teamContainerWinning
        ]}>
          <Text style={styles.teamName}>{equipo1}</Text>
          <Text style={[
            styles.teamScore,
            equipo1Ganando && styles.teamScoreWinning
          ]}>
            {marcador.equipo1Puntos}
          </Text>
        </View>

        {/* Divider */}
        <View style={styles.divider}>
          <Text style={styles.dividerText}>VS</Text>
        </View>

        {/* Equipo 2 */}
        <View style={[
          styles.teamContainer,
          equipo2Ganando && styles.teamContainerWinning
        ]}>
          <Text style={styles.teamName}>{equipo2}</Text>
          <Text style={[
            styles.teamScore,
            equipo2Ganando && styles.teamScoreWinning
          ]}>
            {marcador.equipo2Puntos}
          </Text>
        </View>
      </View>

      {/* Estado */}
      <View style={styles.statusContainer}>
        <View style={[
          styles.statusBadge,
          { backgroundColor: marcador.estado === 'en_curso' ? '#FFD700' : '#00C853' }
        ]}>
          <Text style={styles.statusText}>
            {marcador.estado === 'en_curso' ? '🎮 En Curso' : '✅ Finalizado'}
          </Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
  },
  setsContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  setCard: {
    backgroundColor: '#0E0F11',
    borderWidth: 2,
    borderColor: '#FFD700',
    borderRadius: 12,
    padding: 16,
    minWidth: 150,
    alignItems: 'center',
  },
  setLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#94A3B8',
    marginBottom: 8,
  },
  setScores: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  setScore: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#E8E9EB',
  },
  setScoreWinning: {
    color: '#FFD700',
  },
  setDivider: {
    fontSize: 24,
    color: '#94A3B8',
  },
  mainScoreboard: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
  },
  teamContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
  },
  teamContainerWinning: {
    backgroundColor: 'rgba(0, 85, 255, 0.1)',
    borderRadius: 12,
    paddingHorizontal: 16,
  },
  teamName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#E8E9EB',
    flex: 1,
  },
  teamScore: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#E8E9EB',
  },
  teamScoreWinning: {
    color: '#0055FF',
  },
  divider: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  dividerText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#94A3B8',
  },
  statusContainer: {
    alignItems: 'center',
  },
  statusBadge: {
    paddingVertical: 8,
    paddingHorizontal: 24,
    borderRadius: 20,
  },
  statusText: {
    color: '#0E0F11',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
