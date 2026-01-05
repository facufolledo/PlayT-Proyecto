import { api } from './api';

export interface EstadisticasAdmin {
  usuarios_totales: number;
  usuarios_activos_mes: number;
  partidos_totales: number;
  partidos_mes: number;
  salas_activas: number;
  torneos_activos: number;
  rating_promedio: number;
  crecimiento_usuarios: number;
  crecimiento_partidos: number;
  top_jugadores: Array<{
    id_usuario: number;
    nombre_usuario: string;
    nombre: string;
    apellido: string;
    rating: number;
    partidos_jugados: number;
  }>;
  actividad_reciente: Array<{
    tipo: string;
    descripcion: string;
    fecha: string;
    usuario?: string;
  }>;
}

export interface LogEntry {
  id: number;
  timestamp: string;
  nivel: string;
  mensaje: string;
  usuario_id?: number;
  usuario_nombre?: string;
  endpoint?: string;
  ip?: string;
  user_agent?: string;
  datos_adicionales?: any;
}

export interface FiltrosLogs {
  nivel?: string;
  usuario_id?: number;
  endpoint?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  limit?: number;
  offset?: number;
}

class AdminService {
  async getEstadisticas(): Promise<EstadisticasAdmin> {
    try {
      const response = await api.get('/admin/estadisticas');
      return response.data;
    } catch (error: any) {
      console.error('Error obteniendo estadísticas admin:', error);
      throw new Error(error?.response?.data?.detail || 'Error al obtener estadísticas');
    }
  }

  async getLogs(filtros: FiltrosLogs = {}): Promise<{ logs: LogEntry[]; total: number }> {
    try {
      const params = new URLSearchParams();
      
      if (filtros.nivel) params.append('nivel', filtros.nivel);
      if (filtros.usuario_id) params.append('usuario_id', filtros.usuario_id.toString());
      if (filtros.endpoint) params.append('endpoint', filtros.endpoint);
      if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
      if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);
      if (filtros.limit) params.append('limit', filtros.limit.toString());
      if (filtros.offset) params.append('offset', filtros.offset.toString());

      const response = await api.get(`/logs?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Error obteniendo logs:', error);
      throw new Error(error?.response?.data?.detail || 'Error al obtener logs');
    }
  }

  async exportarLogs(filtros: FiltrosLogs = {}): Promise<Blob> {
    try {
      const params = new URLSearchParams();
      
      if (filtros.nivel) params.append('nivel', filtros.nivel);
      if (filtros.usuario_id) params.append('usuario_id', filtros.usuario_id.toString());
      if (filtros.endpoint) params.append('endpoint', filtros.endpoint);
      if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
      if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);

      const response = await api.get(`/logs/exportar?${params.toString()}`, {
        responseType: 'blob'
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Error exportando logs:', error);
      throw new Error(error?.response?.data?.detail || 'Error al exportar logs');
    }
  }

  async limpiarLogs(dias_antiguedad: number): Promise<{ eliminados: number }> {
    try {
      const response = await api.delete(`/logs/limpiar?dias_antiguedad=${dias_antiguedad}`);
      return response.data;
    } catch (error: any) {
      console.error('Error limpiando logs:', error);
      throw new Error(error?.response?.data?.detail || 'Error al limpiar logs');
    }
  }
}

export const adminService = new AdminService();