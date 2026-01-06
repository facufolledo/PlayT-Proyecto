import React, { useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/common/Button';
import { BackgroundPattern } from '../../components/common/BackgroundPattern';

const ActionCard = ({ iconName, title, subtitle, onPress, color = '#0055FF' }: any) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.95,
      useNativeDriver: true,
      speed: 50,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      speed: 50,
    }).start();
  };

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <TouchableOpacity 
        style={styles.actionCard}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={0.9}
      >
        <View style={[styles.iconContainer, { backgroundColor: `${color}15` }]}>
          <Ionicons name={iconName} size={28} color={color} />
        </View>
        <View style={styles.actionContent}>
          <Text style={styles.actionTitle}>{title}</Text>
          <Text style={styles.actionSubtitle}>{subtitle}</Text>
        </View>
        <Ionicons name="chevron-forward" size={24} color={color} />
      </TouchableOpacity>
    </Animated.View>
  );
};

export const HomeScreen = ({ navigation }: any) => {
  const { usuario, logout } = useAuthStore();

  const stats = {
    partidosJugados: 45,
    partidosGanados: 30,
    rating: usuario?.rating || 1000,
    categoria: usuario?.categoria_inicial || 'Sin categoría',
  };

  const porcentajeVictorias = Math.round((stats.partidosGanados / stats.partidosJugados) * 100);

  return (
    <BackgroundPattern>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>¡Hola, {usuario?.nombre || 'Jugador'}!</Text>
          <Text style={styles.subtitle}>Bienvenido a Drive+</Text>
        </View>
        <TouchableOpacity style={styles.avatar} onPress={() => navigation.navigate('Perfil')}>
          <Text style={styles.avatarText}>
            {usuario?.nombre?.charAt(0) || 'U'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.rating}</Text>
          <Text style={styles.statLabel}>Rating</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.partidosJugados}</Text>
          <Text style={styles.statLabel}>Partidos</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{porcentajeVictorias}%</Text>
          <Text style={styles.statLabel}>Victorias</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.categoria}</Text>
          <Text style={styles.statLabel}>Categoría</Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Acciones Rápidas</Text>
        
        <ActionCard 
          iconName="trophy-outline"
          title="Ver Torneos"
          subtitle="Únete a competencias"
          onPress={() => navigation.navigate('Torneos')}
          color="#FFD700"
        />

        <ActionCard 
          iconName="game-controller-outline"
          title="Buscar Salas"
          subtitle="Encuentra partidos"
          onPress={() => navigation.navigate('Salas')}
          color="#00C853"
        />

        <ActionCard 
          iconName="bar-chart-outline"
          title="Ver Rankings"
          subtitle="Tabla de posiciones"
          onPress={() => navigation.navigate('Rankings')}
          color="#9C27B0"
        />
      </View>

      {/* Próximos Partidos */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Próximos Partidos</Text>
        <View style={styles.emptyState}>
          <Ionicons name="calendar-outline" size={48} color="#94A3B8" />
          <Text style={styles.emptyText}>No tienes partidos programados</Text>
          <Text style={styles.emptySubtext}>Únete a una sala para jugar</Text>
        </View>
      </View>

      {/* Logout Button */}
      <Button
        title="Cerrar Sesión"
        onPress={logout}
        variant="ghost"
      />
    </ScrollView>
    </BackgroundPattern>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E8E9EB',
  },
  subtitle: {
    fontSize: 16,
    color: '#94A3B8',
    marginTop: 4,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#0055FF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  statsContainer: {
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
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#3A4558',
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0055FF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#94A3B8',
    textAlign: 'center',
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 16,
  },
  actionCard: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 20,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  actionContent: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#E8E9EB',
    marginBottom: 4,
  },
  actionSubtitle: {
    fontSize: 14,
    color: '#94A3B8',
  },
  emptyState: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 20,
    padding: 32,
    alignItems: 'center',
  },

  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#E8E9EB',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
  },
});
