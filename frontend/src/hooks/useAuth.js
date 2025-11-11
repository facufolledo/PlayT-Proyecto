import { useEffect, useState } from 'react'
import { dashboardService } from '../services/dashboardService'

export function useAuth() {
  const [status, setStatus] = useState('checking') // 'checking' | 'auth' | 'noauth'
  const [user, setUser] = useState(null)

  useEffect(() => {
    let alive = true
    
    const checkAuth = async () => {
      try {
        console.log('🔍 Verificando autenticación con /auth/me...')
        
        // Verificar si hay token en localStorage
        const token = localStorage.getItem('token')
        if (!token) {
          console.log('❌ No hay token en localStorage')
          if (alive) setStatus('noauth')
          return
        }
        
        // Hacer request a /auth/me para verificar el token
        const response = await dashboardService.getCurrentUser()
        console.log('✅ Usuario autenticado:', response)
        
        if (alive) {
          setUser(response)
          setStatus('auth')
        }
      } catch (error) {
        console.error('❌ Error en verificación de auth:', error)
        
        if (alive) {
          // Si hay error 401, limpiar datos y marcar como no autenticado
          if (error.response?.status === 401) {
            console.log('🔓 Token inválido, limpiando datos')
            localStorage.removeItem('token')
            localStorage.removeItem('user')
          }
          setStatus('noauth')
        }
      }
    }

    checkAuth()
    
    return () => { 
      alive = false 
    }
  }, [])

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    setStatus('noauth')
    window.location.href = '/login'
  }

  return { 
    status, 
    user, 
    isAuthenticated: status === 'auth',
    isLoading: status === 'checking',
    logout 
  }
}


