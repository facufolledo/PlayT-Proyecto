import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';

export const ConfiguracionScreen = ({ navigation }: any) => {
  const { logout } = useAuthStore();
  const [notificaciones, setNotificaciones] = useState(true);
  const [notificacionesPartidos, setNotificacionesPartidos] = useState(true);
  const [notificacionesTorneos, setNotificacionesTorneos] = useState(true);
  const [perfilPublico, setPerfilPublico] = useState(true);

  const handleLogout = () => {
    Alert.alert(
      'Cerrar Sesión',
      '¿Estás seguro de que quieres cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar Sesión',
          style: 'destructive',
          onPress: () => logout(),
        },
      ]
    );
  };

  const handleEliminarCuenta = () => {
    Alert.alert(
      'Eliminar Cuenta',
      '⚠️ Esta acción es irreversible. Se eliminarán todos tus datos, partidos y estadísticas.\n\n¿Estás seguro?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: () => {
            Alert.alert('Función no disponible', 'Por favor contacta a soporte para eliminar tu cuenta');
          },
        },
      ]
    );
  };

  const handleCambiarPassword = () => {
    Alert.alert('Cambiar Contraseña', 'Se enviará un email a tu correo para restablecer la contraseña');
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#E8E9EB" />
        </TouchableOpacity>
        <Text style={styles.title}>Configuración</Text>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Notificaciones */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notificaciones</Text>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Notificaciones Push</Text>
              <Text style={styles.settingDesc}>Recibir notificaciones en tu dispositivo</Text>
            </View>
            <Switch
              value={notificaciones}
              onValueChange={setNotificaciones}
              trackColor={{ false: '#3A4558', true: '#0055FF' }}
              thumbColor="#fff"
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Partidos</Text>
              <Text style={styles.settingDesc}>Notificaciones de partidos y salas</Text>
            </View>
            <Switch
              value={notificacionesPartidos}
              onValueChange={setNotificacionesPartidos}
              trackColor={{ false: '#3A4558', true: '#0055FF' }}
              thumbColor="#fff"
              disabled={!notificaciones}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Torneos</Text>
              <Text style={styles.settingDesc}>Notificaciones de torneos</Text>
            </View>
            <Switch
              value={notificacionesTorneos}
              onValueChange={setNotificacionesTorneos}
              trackColor={{ false: '#3A4558', true: '#0055FF' }}
              thumbColor="#fff"
              disabled={!notificaciones}
            />
          </View>
        </View>

        {/* Privacidad */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Privacidad</Text>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Perfil Público</Text>
              <Text style={styles.settingDesc}>Otros usuarios pueden ver tu perfil</Text>
            </View>
            <Switch
              value={perfilPublico}
              onValueChange={setPerfilPublico}
              trackColor={{ false: '#3A4558', true: '#0055FF' }}
              thumbColor="#fff"
            />
          </View>
        </View>

        {/* Cuenta */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cuenta</Text>

          <TouchableOpacity style={styles.actionButton} onPress={handleCambiarPassword}>
            <View style={[styles.iconContainer, { backgroundColor: '#FFD70015' }]}>
              <Ionicons name="key-outline" size={24} color="#FFD700" />
            </View>
            <View style={styles.actionInfo}>
              <Text style={styles.actionLabel}>Cambiar Contraseña</Text>
              <Text style={styles.actionDesc}>Actualizar tu contraseña</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#94A3B8" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton} onPress={handleLogout}>
            <View style={[styles.iconContainer, { backgroundColor: '#FF6B0015' }]}>
              <Ionicons name="log-out-outline" size={24} color="#FF6B00" />
            </View>
            <View style={styles.actionInfo}>
              <Text style={styles.actionLabel}>Cerrar Sesión</Text>
              <Text style={styles.actionDesc}>Salir de tu cuenta</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#94A3B8" />
          </TouchableOpacity>
        </View>

        {/* Información */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Información</Text>

          <TouchableOpacity style={styles.actionButton}>
            <View style={[styles.iconContainer, { backgroundColor: '#0055FF15' }]}>
              <Ionicons name="document-text-outline" size={24} color="#0055FF" />
            </View>
            <View style={styles.actionInfo}>
              <Text style={styles.actionLabel}>Términos y Condiciones</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#94A3B8" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <View style={[styles.iconContainer, { backgroundColor: '#00C85315' }]}>
              <Ionicons name="shield-checkmark-outline" size={24} color="#00C853" />
            </View>
            <View style={styles.actionInfo}>
              <Text style={styles.actionLabel}>Política de Privacidad</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#94A3B8" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <View style={[styles.iconContainer, { backgroundColor: '#9C27B015' }]}>
              <Ionicons name="information-circle-outline" size={24} color="#9C27B0" />
            </View>
            <View style={styles.actionInfo}>
              <Text style={styles.actionLabel}>Acerca de Drive+</Text>
              <Text style={styles.actionDesc}>Versión 1.0.0</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#94A3B8" />
          </TouchableOpacity>
        </View>

        {/* Zona de Peligro */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, styles.dangerTitle]}>Zona de Peligro</Text>

          <TouchableOpacity
            style={[styles.actionButton, styles.dangerButton]}
            onPress={handleEliminarCuenta}
          >
            <View style={[styles.iconContainer, styles.dangerIconContainer]}>
              <Ionicons name="warning-outline" size={24} color="#FF0055" />
            </View>
            <View style={styles.actionInfo}>
              <Text style={[styles.actionLabel, styles.dangerText]}>Eliminar Cuenta</Text>
              <Text style={styles.actionDesc}>Esta acción es irreversible</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#FF0055" />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1A1F2E',
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
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 16,
  },
  dangerTitle: {
    color: '#FF0055',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#E8E9EB',
    marginBottom: 4,
  },
  settingDesc: {
    fontSize: 14,
    color: '#94A3B8',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  dangerButton: {
    borderColor: 'rgba(255, 0, 85, 0.3)',
    backgroundColor: 'rgba(255, 0, 85, 0.05)',
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  dangerIconContainer: {
    backgroundColor: 'rgba(255, 0, 85, 0.1)',
  },
  actionInfo: {
    flex: 1,
  },
  actionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#E8E9EB',
  },
  dangerText: {
    color: '#FF0055',
  },
  actionDesc: {
    fontSize: 14,
    color: '#94A3B8',
    marginTop: 2,
  },
});
