import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/common/Button';

export const PerfilScreen = ({ navigation }: any) => {
  const { usuario, logout } = useAuthStore();

  if (!usuario) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>No hay usuario autenticado</Text>
      </View>
    );
  }

  const stats = {
    partidosJugados: 45,
    partidosGanados: 30,
    partidosPerdidos: 15,
    torneosJugados: 8,
    torneosGanados: 2,
  };

  const porcentajeVictorias = Math.round((stats.partidosGanados / stats.partidosJugados) * 100);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.avatarLarge}>
          <Text style={styles.avatarText}>
            {usuario.nombre?.charAt(0) || 'U'}
          </Text>
        </View>
        <Text style={styles.nombre}>
          {usuario.nombre} {usuario.apellido}
        </Text>
        <Text style={styles.email}>{usuario.email}</Text>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{usuario.rating || 1000}</Text>
          <Text style={styles.statLabel}>Rating</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{usuario.categoria_inicial}</Text>
          <Text style={styles.statLabel}>Categoría</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.partidosJugados}</Text>
          <Text style={styles.statLabel}>Partidos</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{porcentajeVictorias}%</Text>
          <Text style={styles.statLabel}>Victorias</Text>
        </View>
      </View>

      {/* Información Personal */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Información Personal</Text>
        
        <View style={styles.infoCard}>
          <InfoRow label="DNI" value={usuario.dni || '-'} />
          <InfoRow label="Fecha de Nacimiento" value={usuario.fecha_nacimiento || '-'} />
          <InfoRow label="Género" value={usuario.genero || '-'} />
          <InfoRow label="Teléfono" value={usuario.telefono || '-'} />
          <InfoRow label="Ciudad" value={usuario.ciudad || '-'} />
        </View>
      </View>

      {/* Información de Juego */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Información de Juego</Text>
        
        <View style={styles.infoCard}>
          <InfoRow label="Mano Hábil" value={usuario.mano_habil || '-'} />
          <InfoRow label="Posición Preferida" value={usuario.posicion_preferida || '-'} />
        </View>
      </View>

      {/* Estadísticas Detalladas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Estadísticas</Text>
        
        <View style={styles.infoCard}>
          <InfoRow label="Partidos Jugados" value={stats.partidosJugados.toString()} />
          <InfoRow label="Partidos Ganados" value={stats.partidosGanados.toString()} />
          <InfoRow label="Partidos Perdidos" value={stats.partidosPerdidos.toString()} />
          <InfoRow label="Torneos Jugados" value={stats.torneosJugados.toString()} />
          <InfoRow label="Torneos Ganados" value={stats.torneosGanados.toString()} />
        </View>
      </View>

      {/* Acciones */}
      <View style={styles.section}>
        <Button
          title="Editar Perfil"
          onPress={() => navigation.navigate('EditarPerfil')}
          variant="primary"
        />
        <Button
          title="Configuración"
          onPress={() => navigation.navigate('Configuracion')}
          variant="primary"
        />
        <Button
          title="Cerrar Sesión"
          onPress={logout}
          variant="ghost"
        />
      </View>
    </ScrollView>
  );
};

const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <View style={styles.infoRow}>
    <Text style={styles.infoLabel}>{label}</Text>
    <Text style={styles.infoValue}>{value}</Text>
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
  },
  errorText: {
    color: '#FF0055',
    fontSize: 16,
  },
  content: {
    padding: 20,
    paddingTop: 60,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  avatarLarge: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#0055FF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  avatarText: {
    color: '#fff',
    fontSize: 40,
    fontWeight: 'bold',
  },
  nombre: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 4,
  },
  email: {
    fontSize: 16,
    color: '#94A3B8',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 32,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#0E0F11',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#3A4558',
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00C853',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#94A3B8',
    textAlign: 'center',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 12,
  },
  infoCard: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 12,
    padding: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#3A4558',
  },
  infoLabel: {
    fontSize: 14,
    color: '#94A3B8',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#E8E9EB',
  },
});
