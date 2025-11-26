import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { salaService } from '../../services/sala.service';
import { Sala } from '../../types';
import { Button } from '../../components/common/Button';
import { useAuthStore } from '../../store/authStore';

export const SalaDetalleScreen = ({ route, navigation }: any) => {
  const { salaId } = route.params;
  const [sala, setSala] = useState<Sala | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const usuario = useAuthStore((state) => state.usuario);

  const cargarSala = async () => {
    try {
      const data = await salaService.obtenerSalaPorId(salaId);
      setSala(data);
    } catch (error) {
      console.error('Error al cargar sala:', error);
      Alert.alert('Error', 'No se pudo cargar la sala');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarSala();
  }, [salaId]);

  const handleUnirse = async () => {
    if (!sala) return;
    
    setActionLoading(true);
    try {
      await salaService.unirseASala(sala.id);
      Alert.alert('Éxito', 'Te has unido a la sala');
      cargarSala();
    } catch (error: any) {
      Alert.alert('Error', error.message || 'No se pudo unir a la sala');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSalir = async () => {
    if (!sala) return;
    
    Alert.alert(
      'Confirmar',
      '¿Estás seguro de que quieres salir de esta sala?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Salir',
          style: 'destructive',
          onPress: async () => {
            setActionLoading(true);
            try {
              await salaService.salirDeSala(sala.id);
              Alert.alert('Éxito', 'Has salido de la sala');
              navigation.goBack();
            } catch (error: any) {
              Alert.alert('Error', error.message || 'No se pudo salir de la sala');
            } finally {
              setActionLoading(false);
            }
          },
        },
      ]
    );
  };

  const handleIniciar = async () => {
    if (!sala) return;
    
    Alert.alert(
      'Confirmar',
      '¿Iniciar el partido?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Iniciar',
          onPress: async () => {
            setActionLoading(true);
            try {
              await salaService.iniciarPartido(sala.id);
              Alert.alert('Éxito', 'Partido iniciado');
              cargarSala();
            } catch (error: any) {
              Alert.alert('Error', error.message || 'No se pudo iniciar el partido');
            } finally {
              setActionLoading(false);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Cargando sala...</Text>
      </View>
    );
  }

  if (!sala) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Sala no encontrada</Text>
        <Button title="Volver" onPress={() => navigation.goBack()} />
      </View>
    );
  }

  const esCreador = sala.creador_id === usuario?.id;
  const estaUnido = sala.jugadores?.some(j => j.id === usuario?.id);
  const puedeUnirse = sala.estado === 'esperando' && sala.jugadores_actuales < sala.max_jugadores;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backIcon}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Detalle de Sala</Text>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Nombre y Estado */}
        <View style={styles.card}>
          <Text style={styles.salaNombre}>{sala.nombre}</Text>
          <View style={[
            styles.estadoBadge,
            { backgroundColor: sala.estado === 'esperando' ? '#00C853' : '#FFD700' }
          ]}>
            <Text style={styles.estadoText}>
              {sala.estado === 'esperando' ? 'Esperando' : 'En Curso'}
            </Text>
          </View>
        </View>

        {/* Información */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Información</Text>
          <View style={styles.infoGrid}>
            <InfoItem icon="📍" label="Ubicación" value={sala.ubicacion} />
            <InfoItem 
              icon="📅" 
              label="Fecha" 
              value={new Date(sala.fecha_hora).toLocaleDateString()} 
            />
            <InfoItem 
              icon="⏰" 
              label="Hora" 
              value={new Date(sala.fecha_hora).toLocaleTimeString('es-AR', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })} 
            />
            <InfoItem 
              icon="👥" 
              label="Jugadores" 
              value={`${sala.jugadores_actuales}/${sala.max_jugadores}`} 
            />
            <InfoItem icon="🎯" label="Categoría" value={sala.categoria} />
            <InfoItem icon="🎮" label="Tipo" value={sala.tipo_juego} />
          </View>
        </View>

        {/* Descripción */}
        {sala.descripcion && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Descripción</Text>
            <Text style={styles.descripcion}>{sala.descripcion}</Text>
          </View>
        )}

        {/* Jugadores */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>
            Jugadores ({sala.jugadores_actuales}/{sala.max_jugadores})
          </Text>
          {sala.jugadores && sala.jugadores.length > 0 ? (
            sala.jugadores.map((jugador, index) => (
              <View key={jugador.id} style={styles.jugadorItem}>
                <View style={styles.jugadorAvatar}>
                  <Text style={styles.jugadorAvatarText}>
                    {jugador.nombre?.charAt(0) || 'J'}
                  </Text>
                </View>
                <View style={styles.jugadorInfo}>
                  <Text style={styles.jugadorNombre}>
                    {jugador.nombre} {jugador.apellido}
                    {jugador.id === sala.creador_id && (
                      <Text style={styles.creadorBadge}> (Creador)</Text>
                    )}
                  </Text>
                  <Text style={styles.jugadorRating}>Rating: {jugador.rating || 1000}</Text>
                </View>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>No hay jugadores aún</Text>
          )}
        </View>

        {/* Acciones */}
        <View style={styles.actionsContainer}>
          {esCreador && sala.estado === 'esperando' && (
            <Button
              title="Iniciar Partido"
              onPress={handleIniciar}
              loading={actionLoading}
              variant="accent"
            />
          )}
          
          {!estaUnido && puedeUnirse && (
            <Button
              title="Unirse a la Sala"
              onPress={handleUnirse}
              loading={actionLoading}
              variant="primary"
            />
          )}
          
          {estaUnido && !esCreador && (
            <Button
              title="Salir de la Sala"
              onPress={handleSalir}
              loading={actionLoading}
              variant="ghost"
            />
          )}
        </View>
      </ScrollView>
    </View>
  );
};

const InfoItem = ({ icon, label, value }: { icon: string; label: string; value: string }) => (
  <View style={styles.infoItem}>
    <Text style={styles.infoIcon}>{icon}</Text>
    <View>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1A1F2E',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1A1F2E',
    padding: 20,
  },
  loadingText: {
    color: '#94A3B8',
    fontSize: 16,
  },
  errorText: {
    color: '#FF0055',
    fontSize: 16,
    marginBottom: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    gap: 16,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#3A4558',
    alignItems: 'center',
    justifyContent: 'center',
  },
  backIcon: {
    fontSize: 24,
    color: '#E8E9EB',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E8E9EB',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  card: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  salaNombre: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 12,
  },
  estadoBadge: {
    alignSelf: 'flex-start',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  estadoText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 16,
  },
  infoGrid: {
    gap: 12,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  infoIcon: {
    fontSize: 24,
  },
  infoLabel: {
    fontSize: 12,
    color: '#94A3B8',
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#E8E9EB',
  },
  descripcion: {
    fontSize: 14,
    color: '#94A3B8',
    lineHeight: 20,
  },
  jugadorItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#3A4558',
  },
  jugadorAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#0055FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  jugadorAvatarText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  jugadorInfo: {
    flex: 1,
  },
  jugadorNombre: {
    fontSize: 16,
    fontWeight: '600',
    color: '#E8E9EB',
  },
  creadorBadge: {
    color: '#FFD700',
    fontSize: 14,
  },
  jugadorRating: {
    fontSize: 14,
    color: '#94A3B8',
    marginTop: 2,
  },
  emptyText: {
    color: '#94A3B8',
    fontSize: 14,
    textAlign: 'center',
    paddingVertical: 20,
  },
  actionsContainer: {
    gap: 12,
    marginTop: 8,
  },
});
