import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { salaService } from '../../services/sala.service';
import { Sala } from '../../types';
import { Button } from '../../components/common/Button';
import { BackgroundPattern } from '../../components/common/BackgroundPattern';

export const SalasScreen = ({ navigation }: any) => {
  const [salas, setSalas] = useState<Sala[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filtro, setFiltro] = useState<'todas' | 'disponibles' | 'en_curso'>('disponibles');

  const cargarSalas = async () => {
    try {
      const data = await salaService.obtenerSalas();
      setSalas(data);
    } catch (error) {
      console.error('Error al cargar salas:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    cargarSalas();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    cargarSalas();
  };

  const salasFiltradas = salas.filter(s => {
    if (filtro === 'disponibles') return s.estado === 'programada';
    if (filtro === 'en_curso') return s.estado === 'activa';
    return true;
  });

  const getEstadoBadge = (estado: string) => {
    const badges = {
      programada: { text: 'Disponible', color: '#00C853' },
      activa: { text: 'En Curso', color: '#FF6B00' },
      finalizada: { text: 'Finalizada', color: '#64748B' },
    };
    return badges[estado as keyof typeof badges] || badges.programada;
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Cargando salas...</Text>
      </View>
    );
  }

  return (
    <BackgroundPattern>
      <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Salas</Text>
        <Button
          title="Crear"
          onPress={() => navigation.navigate('CrearSala')}
          variant="accent"
          size="small"
        />
      </View>

      {/* Filtros */}
      <View style={styles.filtrosContainer}>
        {['todas', 'disponibles', 'en_curso'].map((f) => (
          <TouchableOpacity
            key={f}
            style={[
              styles.filtroButton,
              filtro === f && styles.filtroButtonActive
            ]}
            onPress={() => setFiltro(f as any)}
          >
            <Text style={[
              styles.filtroText,
              filtro === f && styles.filtroTextActive
            ]}>
              {f === 'todas' ? 'Todas' : f === 'disponibles' ? 'Disponibles' : 'En Curso'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Lista de Salas */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#0055FF" />
        }
      >
        {salasFiltradas.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="game-controller-outline" size={64} color="#94A3B8" />
            <Text style={styles.emptyText}>No hay salas disponibles</Text>
            <Text style={styles.emptySubtext}>Crea una sala para empezar a jugar</Text>
          </View>
        ) : (
          salasFiltradas.map((sala) => {
            const badge = getEstadoBadge(sala.estado);
            return (
              <TouchableOpacity
                key={sala.id}
                style={styles.salaCard}
                onPress={() => navigation.navigate('SalaDetalle', { salaId: sala.id })}
              >
                <View style={styles.salaHeader}>
                  <Text style={styles.salaNombre}>{sala.nombre}</Text>
                  <View style={[styles.estadoBadge, { backgroundColor: badge.color }]}>
                    <Text style={styles.estadoText}>{badge.text}</Text>
                  </View>
                </View>

                <View style={styles.salaInfo}>
                  <View style={styles.infoRow}>
                    <View style={styles.iconLabel}>
                      <Ionicons name="calendar-outline" size={16} color="#0055FF" />
                      <Text style={styles.infoLabel}>Fecha:</Text>
                    </View>
                    <Text style={styles.infoValue}>
                      {new Date(sala.fecha).toLocaleDateString()}
                    </Text>
                  </View>
                  <View style={styles.infoRow}>
                    <View style={styles.iconLabel}>
                      <Ionicons name="ribbon-outline" size={16} color="#FFD700" />
                      <Text style={styles.infoLabel}>Categoría:</Text>
                    </View>
                    <Text style={styles.infoValue}>{sala.categoria}</Text>
                  </View>
                  <View style={styles.infoRow}>
                    <View style={styles.iconLabel}>
                      <Ionicons name="people-outline" size={16} color="#00C853" />
                      <Text style={styles.infoLabel}>Equipo A:</Text>
                    </View>
                    <Text style={styles.infoValue}>
                      {sala.equipoA.jugador1.nombre} / {sala.equipoA.jugador2.nombre}
                    </Text>
                  </View>
                  <View style={styles.infoRow}>
                    <View style={styles.iconLabel}>
                      <Ionicons name="people-outline" size={16} color="#9C27B0" />
                      <Text style={styles.infoLabel}>Equipo B:</Text>
                    </View>
                    <Text style={styles.infoValue}>
                      {sala.equipoB.jugador1.nombre} / {sala.equipoB.jugador2.nombre}
                    </Text>
                  </View>
                  {sala.estado === 'activa' && (
                    <View style={styles.infoRow}>
                      <View style={styles.iconLabel}>
                        <Ionicons name="stats-chart-outline" size={16} color="#FF6B00" />
                        <Text style={styles.infoLabel}>Marcador:</Text>
                      </View>
                      <Text style={styles.infoValue}>
                        {sala.equipoA.puntos} - {sala.equipoB.puntos}
                      </Text>
                    </View>
                  )}
                </View>
              </TouchableOpacity>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#E8E9EB',
  },
  filtrosContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 8,
    marginBottom: 16,
  },
  filtroButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#3A4558',
  },
  filtroButtonActive: {
    backgroundColor: '#00C853',
  },
  filtroText: {
    color: '#94A3B8',
    fontWeight: '600',
    fontSize: 14,
  },
  filtroTextActive: {
    color: '#E8E9EB',
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
  iconLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#E8E9EB',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#94A3B8',
  },
  salaCard: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  salaHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  salaNombre: {
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
  salaInfo: {
    gap: 8,
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
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
  salaDescripcion: {
    color: '#94A3B8',
    fontSize: 14,
    lineHeight: 20,
  },
});
