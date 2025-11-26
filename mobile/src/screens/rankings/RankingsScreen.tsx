import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { rankingService } from '../../services/ranking.service';
import { useAuthStore } from '../../store/authStore';
import { BackgroundPattern } from '../../components/common/BackgroundPattern';

interface RankingJugador {
  posicion: number;
  usuario_id: number;
  nombre: string;
  apellido: string;
  rating: number;
  partidos_jugados: number;
  partidos_ganados: number;
  categoria: string;
}

export const RankingsScreen = () => {
  const [rankings, setRankings] = useState<RankingJugador[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const usuario = useAuthStore((state) => state.usuario);

  const cargarRankings = async () => {
    try {
      const data = await rankingService.obtenerRankings();
      setRankings(data);
    } catch (error) {
      console.error('Error al cargar rankings:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    cargarRankings();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    cargarRankings();
  };

  const getMedalIcon = (posicion: number) => {
    if (posicion === 1) return '🥇';
    if (posicion === 2) return '🥈';
    if (posicion === 3) return '🥉';
    return `${posicion}°`;
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Cargando rankings...</Text>
      </View>
    );
  }

  return (
    <BackgroundPattern>
      <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Rankings</Text>
        <Text style={styles.subtitle}>Tabla de posiciones</Text>
      </View>

      {/* Mi Posición */}
      {usuario && (
        <View style={styles.miPosicionCard}>
          <Text style={styles.miPosicionLabel}>Tu Posición</Text>
          <View style={styles.miPosicionContent}>
            <Text style={styles.miPosicionNumero}>
              {rankings.findIndex(r => String(r.usuario_id) === String(usuario.id)) + 1 || '-'}°
            </Text>
            <View style={styles.miPosicionInfo}>
              <Text style={styles.miPosicionNombre}>
                {usuario.nombre} {usuario.apellido}
              </Text>
              <Text style={styles.miPosicionRating}>
                Rating: {usuario.rating || 1000}
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* Lista de Rankings */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#0055FF" />
        }
      >
        {rankings.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="bar-chart-outline" size={64} color="#94A3B8" />
            <Text style={styles.emptyText}>No hay rankings disponibles</Text>
          </View>
        ) : (
          rankings.map((jugador) => {
            const isCurrentUser = String(usuario?.id) === String(jugador.usuario_id);
            const porcentajeVictorias = jugador.partidos_jugados > 0
              ? Math.round((jugador.partidos_ganados / jugador.partidos_jugados) * 100)
              : 0;

            return (
              <View
                key={jugador.usuario_id}
                style={[
                  styles.rankingCard,
                  isCurrentUser && styles.rankingCardHighlight,
                  jugador.posicion <= 3 && styles.rankingCardTop
                ]}
              >
                <View style={styles.rankingPosicion}>
                  <Text style={[
                    styles.posicionText,
                    jugador.posicion <= 3 && styles.posicionTextTop
                  ]}>
                    {getMedalIcon(jugador.posicion)}
                  </Text>
                </View>

                <View style={styles.rankingInfo}>
                  <Text style={styles.jugadorNombre}>
                    {jugador.nombre} {jugador.apellido}
                    {isCurrentUser && <Text style={styles.tuBadge}> (Tú)</Text>}
                  </Text>
                  <View style={styles.statsRow}>
                    <View style={styles.statItem}>
                      <Ionicons name="star" size={14} color="#FFD700" />
                      <Text style={styles.statText}>{jugador.rating}</Text>
                    </View>
                    <View style={styles.statItem}>
                      <Ionicons name="game-controller" size={14} color="#94A3B8" />
                      <Text style={styles.statText}>{jugador.partidos_jugados}</Text>
                    </View>
                    <View style={styles.statItem}>
                      <Ionicons name="checkmark-circle" size={14} color="#00C853" />
                      <Text style={styles.statText}>{porcentajeVictorias}%</Text>
                    </View>
                  </View>
                  <Text style={styles.categoriaText}>
                    {jugador.categoria}
                  </Text>
                </View>
              </View>
            );
          })
        )}
      </ScrollView>
    </View>
    </BackgroundPattern>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1A1F2E',
  },
  loadingText: {
    color: '#94A3B8',
    fontSize: 16,
  },
  header: {
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#E8E9EB',
  },
  subtitle: {
    fontSize: 16,
    color: '#94A3B8',
    marginTop: 4,
  },
  miPosicionCard: {
    backgroundColor: '#9C27B0',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 16,
    borderRadius: 12,
  },
  miPosicionLabel: {
    color: '#E8E9EB',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 8,
    opacity: 0.8,
  },
  miPosicionContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  miPosicionNumero: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
  },
  miPosicionInfo: {
    flex: 1,
  },
  miPosicionNombre: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  miPosicionRating: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
    marginTop: 4,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
    gap: 16,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#E8E9EB',
  },
  rankingCard: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  rankingCardHighlight: {
    borderColor: '#9C27B0',
    borderWidth: 2,
  },
  rankingCardTop: {
    backgroundColor: '#1A1F2E',
  },
  rankingPosicion: {
    width: 50,
    alignItems: 'center',
  },
  posicionText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#94A3B8',
  },
  posicionTextTop: {
    fontSize: 28,
  },
  rankingInfo: {
    flex: 1,
  },
  jugadorNombre: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 8,
  },
  tuBadge: {
    color: '#9C27B0',
    fontSize: 14,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 4,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  statText: {
    fontSize: 14,
    color: '#94A3B8',
  },
  categoriaText: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    marginTop: 4,
  },
});
