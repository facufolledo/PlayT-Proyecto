/**
 * Hook para manejar notificaciones push
 */
import { useEffect, useState } from 'react';
import { notificationService } from '../services/notification.service';

export function useNotifications(isAuthenticated: boolean) {
  const [permissionStatus, setPermissionStatus] = useState<NotificationPermission | 'unsupported'>('default');
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Actualizar estado del permiso
    setPermissionStatus(notificationService.getPermissionStatus());
  }, []);

  useEffect(() => {
    // Solo inicializar si el usuario está autenticado
    if (!isAuthenticated) return;
    if (!notificationService.isSupported()) return;

    // Configurar listener de mensajes en foreground
    notificationService.setupForegroundListener((payload) => {
      console.log('Notificación en foreground:', payload);
      // Aquí podrías actualizar el estado de la app, mostrar un toast, etc.
    });

    // Si ya tiene permiso, obtener token
    if (Notification.permission === 'granted') {
      notificationService.requestPermission().then(setToken);
    }
  }, [isAuthenticated]);

  const requestPermission = async () => {
    const newToken = await notificationService.requestPermission();
    setToken(newToken);
    setPermissionStatus(notificationService.getPermissionStatus());
    return newToken;
  };

  return {
    isSupported: notificationService.isSupported(),
    permissionStatus,
    token,
    requestPermission
  };
}
