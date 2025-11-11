import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, Typography } from '@mui/material'

// Componentes de autenticación
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'
import Dashboard from './components/Dashboard/Dashboard'
import ProtectedRoute from './components/Auth/ProtectedRoute'

function App() {
  console.log('Renderizando componente App')

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Routes>
        {/* Rutas públicas */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Ruta protegida */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        
        {/* Ruta principal - redirige al login */}
        <Route path="/" element={<Navigate to="/login" />} />
        
        {/* Ruta por defecto */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Box>
  )
}

export default App
