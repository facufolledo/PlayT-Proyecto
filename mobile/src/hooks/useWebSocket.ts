import { useEffect, useState } from 'react';
import { websocketService } from '../services/websocket.service';
import { useAuthStore } from '../store/authStore';
import { logger } from '../utils/logger';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  salaId?: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const { autoConnect = true, salaId } = options;
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const usuario = useAuthStore((state) => state.usuario);

  useEffect(() => {
    if (!autoConnect || !usuario) return;

    // Conectar al WebSocket
    const token = 'mock-token'; // En producción, usar token real
    websocketService.connect(token);

    // Verificar conexión
    const checkConnection = setInterval(() => {
      setIsConnected(websocketService.isConnected());
    }, 1000);

    // Unirse a sala si se especifica
    if (salaId && websocketService.isConnected()) {
      websocketService.joinSala(salaId);
    }

    // Cleanup
    return () => {
      clearInterval(checkConnection);
      if (salaId) {
        websocketService.leaveSala(salaId);
      }
    };
  }, [autoConnect, usuario, salaId]);

  // Funciones helper
  const joinSala = (id: number) => {
    try {
      websocketService.joinSala(id);
      logger.log('Unido a sala:', id);
    } catch (err: any) {
      setError(err.message);
      logger.error('Error al unirse a sala:', err);
    }
  };

  const leaveSala = (id: number) => {
    try {
      websocketService.leaveSala(id);
      logger.log('Salido de sala:', id);
    } catch (err: any) {
      setError(err.message);
      logger.error('Error al salir de sala:', err);
    }
  };

  const updateScore = (data: any) => {
    try {
      websocketService.updateScore(data);
    } catch (err: any) {
      setError(err.message);
      logger.error('Error al actualizar marcador:', err);
    }
  };

  const finalizarPartido = (data: any) => {
    try {
      websocketService.finalizarPartido(data);
    } catch (err: any) {
      setError(err.message);
      logger.error('Error al finalizar partido:', err);
    }
  };

  return {
    isConnected,
    error,
    joinSala,
    leaveSala,
    updateScore,
    finalizarPartido,
    websocketService,
  };
};
