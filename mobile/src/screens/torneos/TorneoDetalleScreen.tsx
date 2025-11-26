import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { torneoService } from '../../services/torneo.service';
import { Torneo } from '../../types';
import { Button } from '../../components/common/Button';
import { useAuthStore } from '../../store/authStore';

export const TorneoDetalleScreen = ({ route, navigation }: any) => {
  const { torneoId } = route.params;
  const [torneo, setTorneo] = useState<Torneo | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const usuario = useAuthStore((state) => state.usuario);

  const cargarTorneo = async () => {
    try {
      const data = await torneoService.obtenerTorneoPorId(torneoId);
      setTorneo(data);
    } catch (error) {
      console.error('Error al cargar torneo:', error);
      Alert.alert('Error', 'No se pudo cargar el torneo');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarTorneo();
  }, [torneoId]);

  const handleInscribirse = async () => {
    if (!torneo) return;
    
    setActionLoading(true);
    try {
      await torneoService.inscribirseEnTorneo(torneo.id);
      Alert.alert('Éxito', 'Te has inscrito al torneo');
      cargarTorneo();
    } catch (error: any) {
      Alert.alert('Error', error.message || 'No se pudo inscribir al torneo');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDesinscribirse = async () => {
    if (!torneo) return;
    
    Alert.alert(
      'Confirmar',
      '¿Estás seguro de que quieres desinscribirte del torneo?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Desinscribirse',
          style: 'destructive',
          onPress: async () => {
            setActionLoading(true);
            try {
              await torneoService.desinscribirseDelTorneo(torneo.id);
              Alert.alert('Éxito', 'Te has desinscrito del torneo');
              cargarTorneo();
            } catch (error: any) {
              Alert.alert('Error', error.message || 'No se pudo desinscribir del torneo');
            } finally {
              setActionLoading(false);
            }
          },
        },
      ]
    );
  };

  const handleIniciar = async () => {
    if (!torneo) return;
    
    Alert.alert(
      'Confirmar',
      '¿Iniciar el torneo? Esta acción no se puede deshacer.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Iniciar',
          onPress: async () => {
            setActionLoading(true);
            try {
              await torneoService.iniciarTorneo(torneo.id);
              Alert.alert('Éxito', 'Torneo iniciado');
              cargarTorneo();
            } catch (error: any) {
              Alert.alert('Error', error.message || 'No se pudo iniciar el torneo');
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
        <Text style={styles.loadingText}>Cargando torneo...</Text>
      </View>
    );
  }

  if (!torneo) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Torneo no encontrado</Text>
        <Button title="Volver" onPress={() => navigation.goBack()} />
      </View>
    );
  }

  const esOrganizador = torneo.organizador_id === usuario?.id;
  const estaInscrito = torneo.participantes?.some(p => p.id === usuario?.id);
  const puedeInscribirse = torneo.estado === 'inscripcion' && 
    torneo.participantes_actuales < torneo.max_participantes;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backIcon}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Detalle de Torneo</Text>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Nombre y Estado */}
        <View style={styles.card}>
          <Text style={styles.torneoNombre}>{torneo.nombre}</Text>
          <View style={[
            styles.estadoBadge,
            { backgroundColor: 
              torneo.estado === 'inscripcion' ? '#0055FF' : 
              torneo.estado === 'en_curso' ? '#FFD700' : '#94A3B8' 
            }
          ]}>
            <Text style={styles.estadoText}>
              {torneo.estado === 'inscripcion' ? 'Inscripción' : 
               torneo.estado === 'en_curso' ? 'En Curso' : 'Finalizado'}
            </Text>
          </View>
        </View>

        {/* Información */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Información</Text>
          <View style={styles.infoGrid}>
            <InfoItem 
              icon="📅" 
              label="Inicio" 
              value={new Date(torneo.fecha_inicio).toLocaleDateString()} 
            />
            <InfoItem 
              icon="🏁" 
              label="Fin" 
              value={new Date(torneo.fecha_fin).toLocaleDateString()} 
            />
            <InfoItem 
              icon="👥" 
              label="Participantes" 
              value={`${torneo.participantes_actuales}/${torneo.max_participantes}`} 
            />
            <InfoItem icon="🎯" label="Categoría" value={torneo.categoria} />
            <InfoItem icon="🏆" label="Formato" value={torneo.formato} />
          </View>
        </View>

        {/* Descripción */}
        {torneo.descripcion && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Descripción</Text>
            <Text style={styles.descripcion}>{torneo.descripcion}</Text>
          </View>
        )}

        {/* Participantes */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>
            Participantes ({torneo.participantes_actuales}/{torneo.max_participantes})
          </Text>
          {torneo.participantes && torneo.participantes.length > 0 ? (
            torneo.participantes.map((participante) => (
              <View key={participante.id} style={styles.participanteItem}>
                <View style={styles.participanteAvatar}>
                  <Text style={styles.participanteAvatarText}>
                    {participante.nombre?.charAt(0) || 'P'}
                  </Text>
                </View>
                <View style={styles.participanteInfo}>
                  <Text style={styles.participanteNombre}>
                    {participante.nombre} {participante.apellido}
                  </Text>
                  <Text style={styles.participanteRating}>
                    Rating: {participante.rating || 1000}
                  </Text>
                </View>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>No hay participantes aún</Text>
          )}
        </View>

        {/* Acciones */}
        <View style={styles.actionsContainer}>
          {esOrganizador && torneo.estado === 'inscripcion' && (
            <Button
              title="Iniciar Torneo"
              onPress={handleIniciar}
              loading={actionLoading}
              variant="accent"
            />
          )}
          
          {!estaInscrito && puedeInscribirse && (
            <Button
              title="Inscribirse"
              onPress={handleInscribirse}
              loading={actionLoading}
              variant="primary"
            />
          )}
          
          {estaInscrito && torneo.estado === 'inscripcion' && (
            <Button
              title="Desinscribirse"
              onPress={handleDesinscribirse}
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
  torneoNombre: {
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
  participanteItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#3A4558',
  },
  participanteAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFD700',
    alignItems: 'center',
    justifyContent: 'center',
  },
  participanteAvatarText: {
    color: '#0E0F11',
    fontSize: 16,
    fontWeight: 'bold',
  },
  participanteInfo: {
    flex: 1,
  },
  participanteNombre: {
    fontSize: 16,
    fontWeight: '600',
    color: '#E8E9EB',
  },
  participanteRating: {
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
