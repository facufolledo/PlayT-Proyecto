import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const authService = {
  // Login
  async login(email, password) {
    try {
      console.log('🔐 Iniciando proceso de login...')
      
      // Crear FormData para OAuth2PasswordRequestForm
      const formData = new FormData()
      formData.append('username', email) // OAuth2 usa 'username' para email/usuario
      formData.append('password', password)
      
      console.log('📤 Enviando datos al backend...')
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      
      console.log('📥 Respuesta del login:', response.data)
      
      if (response.data.access_token) {
        console.log('✅ Token recibido, obteniendo datos del usuario...')
        
        // Obtener información del usuario después del login
        const userResponse = await api.get('/auth/me', {
          headers: {
            'Authorization': `Bearer ${response.data.access_token}`
          }
        })
        
        console.log('👤 Datos del usuario:', userResponse.data)
        
        // Guardar token y datos del usuario
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(userResponse.data))
        
        const result = {
          ...response.data,
          user: userResponse.data
        }
        
        console.log('💾 Datos guardados en localStorage')
        return result
      }
      
      throw new Error('No se recibió token de acceso')
    } catch (error) {
      console.error('❌ Error en login:', error)
      console.error('❌ Error response:', error.response?.data)
      throw error
    }
  },

  // Register
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      
      if (response.data.access_token) {
        // Guardar token y datos del usuario
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        return response.data
      }
      
      throw new Error('No se recibió token de acceso')
    } catch (error) {
      console.error('Error en registro:', error)
      throw error
    }
  },

  // Logout
  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  // Obtener token actual
  getToken() {
    return localStorage.getItem('token')
  },

  // Verificar si está autenticado
  isAuthenticated() {
    const token = this.getToken()
    return !!token
  },

  // Obtener usuario actual
  getCurrentUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
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

export default authService
