import { useState, useEffect, createContext, useContext } from 'react'
import { authService } from '../../services/api'
import toast from 'react-hot-toast'

// Contexto de autenticación
const AuthContext = createContext()

// Hook personalizado para usar el contexto de autenticación
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }
  return context
}

// Provider del contexto de autenticación
export const AuthProvider = ({ children }) => {
  console.log('Renderizando AuthProvider')
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  // Verificar si hay un usuario guardado al cargar la aplicación
  useEffect(() => {
    const checkAuth = () => {
      console.log('Verificando autenticación...')
      const token = localStorage.getItem('playt_token')
      const savedUser = localStorage.getItem('playt_user')
      
      console.log('Token:', token ? 'Existe' : 'No existe')
      console.log('Usuario guardado:', savedUser ? 'Existe' : 'No existe')
      
      if (token && savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          setUser(userData)
          setIsAuthenticated(true)
          console.log('Usuario autenticado:', userData)
        } catch (error) {
          console.error('Error al parsear usuario guardado:', error)
          localStorage.removeItem('playt_token')
          localStorage.removeItem('playt_user')
        }
      }
      setLoading(false)
      console.log('Verificación de autenticación completada')
    }

    checkAuth()
  }, [])

  // Función de login
  const login = async (credentials) => {
    try {
      setLoading(true)
      const response = await authService.login(credentials)
      
      const { access_token } = response
      
      // Guardar token en localStorage
      localStorage.setItem('playt_token', access_token)
      
      // Obtener datos del usuario usando el token
      const userResponse = await authService.getCurrentUser()
      const userData = userResponse
      
      // Guardar usuario en localStorage
      localStorage.setItem('playt_user', JSON.stringify(userData))
      
      // Actualizar estado
      setUser(userData)
      setIsAuthenticated(true)
      
      toast.success('¡Bienvenido a PULSE!')
      return { success: true }
    } catch (error) {
      console.error('Error en login:', error)
      toast.error('Error al iniciar sesión')
      return { success: false, error }
    } finally {
      setLoading(false)
    }
  }

  // Función de registro
  const register = async (userData) => {
    try {
      setLoading(true)
      const response = await authService.register(userData)
      
      toast.success('Usuario registrado exitosamente. Por favor, inicia sesión.')
      return { success: true }
    } catch (error) {
      console.error('Error en registro:', error)
      return { success: false, error }
    } finally {
      setLoading(false)
    }
  }

  // Función de logout
  const logout = () => {
    authService.logout()
    setUser(null)
    setIsAuthenticated(false)
    toast.success('Sesión cerrada exitosamente')
  }

  // Función para actualizar datos del usuario
  const updateUser = (newUserData) => {
    setUser(newUserData)
    localStorage.setItem('playt_user', JSON.stringify(newUserData))
  }

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    updateUser,
  }

  console.log('AuthProvider - Estado actual:', { user, isAuthenticated, loading })

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthProvider
