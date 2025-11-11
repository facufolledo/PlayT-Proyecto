import axios from 'axios'

const API_BASE_URL = '/api'

// Configurar axios con interceptores para manejar tokens
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar el token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    console.log('🔑 Token para request:', token ? 'Encontrado' : 'No encontrado')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('📤 Agregando Authorization header:', `Bearer ${token.substring(0, 20)}...`)
    }
    return config
  },
  (error) => {
    console.error('❌ Error en interceptor de request:', error)
    return Promise.reject(error)
  }
)

// Interceptor para manejar respuestas y errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const dashboardService = {
  // Obtener información del usuario actual
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me')
      return response.data
    } catch (error) {
      console.error('Error al obtener usuario actual:', error)
      throw error
    }
  },

  // Obtener ranking general
  async getRanking(limit = 10, offset = 0) {
    try {
      const response = await api.get(`/ranking/?limit=${limit}&offset=${offset}`)
      return response.data
    } catch (error) {
      console.error('Error al obtener ranking:', error)
      throw error
    }
  },

  // Obtener top semanal
  async getTopWeekly(limit = 5) {
    try {
      const response = await api.get(`/ranking/top-weekly?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error al obtener top semanal:', error)
      throw error
    }
  },

  // Obtener partidos del usuario
  async getUserMatches(userId, limit = 20) {
    try {
      const response = await api.get(`/partidos/usuario/${userId}?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error al obtener partidos del usuario:', error)
      throw error
    }
  },

  // Obtener historial de rating del usuario
  async getUserRatingHistory(userId, limit = 20) {
    try {
      const response = await api.get(`/ranking/historial/${userId}?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error al obtener historial de rating:', error)
      throw error
    }
  },

  // Obtener categorías
  async getCategorias() {
    try {
      const response = await api.get('/auth/categorias')
      return response.data
    } catch (error) {
      console.error('Error al obtener categorías:', error)
      throw error
    }
  }
}

export default dashboardService
