import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { torneoService } from '../../services/torneo.service';
import { Torneo } from '../../types';
import { Button } from '../../components/common/Button';
import { TorneoCard } from '../../components/torneos/TorneoCard';
import { BackgroundPattern } from '../../components/common/BackgroundPattern';

export const TorneosScreen = ({ navigation }: any) => {
  const [torneos, setTorneos] = useState<Torneo[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filtro, setFiltro] = useState<'todos' | 'activos' | 'finalizados'>('activos');

  const cargarTorneos = async () => {
    try {
      const data = await torneoService.obtenerTorneos();
      setTorneos(data);
    } catch (error) {
      console.error('Error al cargar torneos:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    cargarTorneos();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    cargarTorneos();
  };

  const torneosFiltrados = torneos.filter(t => {
    if (filtro === 'activos') return t.estado === 'activo' || t.estado === 'programado';
    if (filtro === 'finalizados') return t.estado === 'finalizado';
    return true;
  });

  const getEstadoBadge = (estado: string) => {
    const badges = {
      activo: { text: 'Activo', color: '#00C853' },
      programado: { text: 'Programado', color: '#FFD700' },
      finalizado: { text: 'Finalizado', color: '#64748B' },
    };
    return badges[estado as keyof typeof badges] || badges.activo;
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Cargando torneos...</Text>
      </View>
    );
  }

  return (
    <BackgroundPattern>
      <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Torneos</Text>
        <Button
          title="Crear"
          onPress={() => navigation.navigate('CrearTorneo')}
          variant="accent"
          size="small"
        />
      </View>

      {/* Filtros */}
      <View style={styles.filtrosContainer}>
        {['todos', 'activos', 'finalizados'].map((f) => (
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
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Lista de Torneos */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#0055FF" />
        }
      >
        {torneosFiltrados.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="trophy-outline" size={64} color="#94A3B8" />
            <Text style={styles.emptyText}>No hay torneos disponibles</Text>
            <Text style={styles.emptySubtext}>Sé el primero en crear uno</Text>
          </View>
        ) : (
          torneosFiltrados.map((torneo) => (
            <TorneoCard
              key={torneo.id}
              torneo={torneo}
              onPress={() => navigation.navigate('TorneoDetalle', { torneoId: torneo.id })}
            />
          ))
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
    backgroundColor: '#FFD700',
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
});
