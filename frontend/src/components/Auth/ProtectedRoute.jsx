import React, { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Box, CircularProgress, Typography } from '@mui/material'
import { authService } from '../../services/authService'

const ProtectedRoute = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const checkAuth = () => {
      // Verificar si hay token y usuario en localStorage
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        try {
          // Verificar que el usuario es un objeto válido
          const userData = JSON.parse(user)
          if (userData && userData.id_usuario) {
            setIsAuthenticated(true)
          } else {
            // Datos inválidos, limpiar
            authService.logout()
          }
        } catch (error) {
          // Error al parsear, limpiar
          authService.logout()
        }
      }
      
      setIsLoading(false)
    }

    // Verificar inmediatamente
    checkAuth()
  }, [])

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          Verificando autenticación...
        </Typography>
      </Box>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute
