import axios from 'axios'
import toast from 'react-hot-toast'

// Configuración base de axios
const api = axios.create({
  baseURL: '/api', // Proxy configurado en vite.config.js
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('playt_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar respuestas
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Token expirado o inválido
          localStorage.removeItem('playt_token')
          localStorage.removeItem('playt_user')
          window.location.href = '/login'
          toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.')
          break
        case 403:
          toast.error('No tienes permisos para realizar esta acción.')
          break
        case 404:
          toast.error('Recurso no encontrado.')
          break
        case 422:
          // Errores de validación
          const errors = data.detail || []
          errors.forEach(error => {
            toast.error(error.msg || 'Error de validación')
          })
          break
        case 500:
          toast.error('Error interno del servidor.')
          break
        default:
          toast.error(data.message || 'Error inesperado')
      }
    } else if (error.request) {
      toast.error('Error de conexión. Verifica tu conexión a internet.')
    } else {
      toast.error('Error inesperado')
    }
    
    return Promise.reject(error)
  }
)

// Servicios de autenticación
export const authService = {
  login: async (credentials) => {
    // El backend espera form-data con username y password
    const formData = new FormData()
    formData.append('username', credentials.email) // El backend usa username como email
    formData.append('password', credentials.password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  
  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
  
  logout: () => {
    localStorage.removeItem('playt_token')
    localStorage.removeItem('playt_user')
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
  
  getCategorias: async (sexo = 'masculino') => {
    const response = await api.get('/categorias', { params: { sexo } })
    return response.data
  }
}

// Servicios de partidos
export const partidosService = {
  getPartidos: async (params = {}) => {
    const response = await api.get('/partidos', { params })
    return response.data
  },
  
  getPartido: async (id) => {
    const response = await api.get(`/partidos/${id}`)
    return response.data
  },
  
  createPartido: async (partidoData) => {
    const response = await api.post('/partidos', partidoData)
    return response.data
  },
  
  reportarResultado: async (partidoId, resultado) => {
    const response = await api.post(`/partidos/${partidoId}/resultado`, resultado)
    return response.data
  },
  
  confirmarResultado: async (partidoId) => {
    const response = await api.post(`/partidos/${partidoId}/confirmar`)
    return response.data
  },
  
  calcularElo: async (partidoId) => {
    const response = await api.post(`/partidos/${partidoId}/calcular-elo`)
    return response.data
  }
}

// Servicios de usuarios
export const usuariosService = {
  getUsuarios: async (params = {}) => {
    const response = await api.get('/usuarios', { params })
    return response.data
  },
  
  getUsuario: async (id) => {
    const response = await api.get(`/usuarios/${id}`)
    return response.data
  },
  
  updateUsuario: async (id, userData) => {
    const response = await api.put(`/usuarios/${id}`, userData)
    return response.data
  },
  
  getPerfil: async () => {
    const response = await api.get('/usuarios/me')
    return response.data
  }
}

// Servicios de ranking
export const rankingService = {
  getRanking: async (params = {}) => {
    const response = await api.get('/ranking', { params })
    return response.data
  },
  
  getTopWeekly: async (params = {}) => {
    const response = await api.get('/ranking/top-weekly', { params })
    return response.data
  },
  
  getHistorialElo: async (userId) => {
    const response = await api.get(`/ranking/historial/${userId}`)
    return response.data
  }
}

// Servicios de categorías
export const categoriasService = {
  getCategorias: async (sexo = 'masculino') => {
    const response = await api.get('/categorias', { params: { sexo } })
    return response.data
  }
}

export default api
