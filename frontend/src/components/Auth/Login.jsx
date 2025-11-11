import React, { useState, lazy, Suspense } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Container,
  CircularProgress,
  Tabs,
  Tab,
  InputAdornment,
  IconButton,
  Alert,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
} from '@mui/icons-material'
import { authService } from '../../services/authService'

// Lazy load del componente Register para mejor rendimiento
const Register = lazy(() => import('./Register'))

const Login = () => {
  console.log('Renderizando componente Login')
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [activeTab, setActiveTab] = useState(0)
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue)
    if (newValue === 1) {
      navigate('/register')
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.email) {
      newErrors.email = 'El email o nombre de usuario es requerido'
    }
    
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida'
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    console.log('Enviando formulario de login')
    
    if (!validateForm()) {
      return
    }
    
    setLoading(true)
    
    try {
      console.log('Intentando login con:', formData.email)
      const response = await authService.login(formData.email, formData.password)
      console.log('Login exitoso:', response)
      
      // Verificar que tenemos token y usuario
      if (response.access_token && response.user) {
        console.log('Redirigiendo al dashboard...')
        // Redirigir al dashboard
        window.location.href = '/dashboard'
      } else {
        console.error('No se recibieron datos completos del login')
        setErrors({ 
          general: 'Error en la respuesta del servidor. Intenta nuevamente.' 
        })
      }
    } catch (error) {
      console.error('Error en login:', error)
      console.error('Error response:', error.response)
      setErrors({ 
        general: error.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.' 
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Left Section - Promotional */}
      <Box
        sx={{
          flex: '0 0 60%',
          background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
          position: 'relative',
          display: { xs: 'none', md: 'flex' },
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          color: 'white',
          padding: 4,
        }}
      >
        {/* Background Image - Comentado temporalmente para mejorar rendimiento */}
        {/* <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: 'url("/images/padel-court-bg.svg")',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: 0.8,
          }}
        /> */}
        {/* Overlay */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, rgba(30, 60, 114, 0.9) 0%, rgba(42, 82, 152, 0.8) 100%)',
          }}
        />
        
        {/* Logo */}
        <Box sx={{ position: 'relative', zIndex: 1, mb: 4 }}>
          <Typography variant="h3" sx={{ fontWeight: 700 }}>
            PULSE
          </Typography>
        </Box>

        {/* Main Heading */}
        <Typography
          variant="h3"
          sx={{
            fontWeight: 700,
            textAlign: 'center',
            mb: 2,
            position: 'relative',
            zIndex: 1,
          }}
        >
          Tu juego de pádel, elevado al siguiente nivel
        </Typography>

        {/* Sub Heading */}
        <Typography
          variant="h6"
          sx={{
            textAlign: 'center',
            mb: 6,
            opacity: 0.9,
            position: 'relative',
            zIndex: 1,
          }}
        >
          Conecta con jugadores, compite en rankings y mejora tu juego
        </Typography>
      </Box>

      {/* Right Section - Login Form */}
      <Box
        sx={{
          flex: '0 0 40%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 4,
          backgroundColor: 'white',
          minHeight: '100vh',
        }}
      >
        <Container maxWidth="sm">
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
              Bienvenido de vuelta
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Ingresa a tu cuenta para continuar jugando
            </Typography>
          </Box>

          {/* Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 4 }}>
            <Tabs 
              value={activeTab} 
              onChange={handleTabChange}
              sx={{
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: '1rem',
                },
              }}
            >
              <Tab 
                label="Iniciar Sesión" 
                sx={{ 
                  backgroundColor: activeTab === 0 ? 'grey.100' : 'transparent',
                  borderRadius: '8px 8px 0 0',
                }}
              />
              <Tab 
                label="Registrarse" 
                sx={{ 
                  backgroundColor: activeTab === 1 ? 'grey.100' : 'transparent',
                  borderRadius: '8px 8px 0 0',
                }}
              />
            </Tabs>
          </Box>

          {/* Login Form */}
          <Paper
            elevation={0}
            sx={{
              padding: 4,
              border: '1px solid',
              borderColor: 'grey.200',
              borderRadius: 2,
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              Iniciar Sesión
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Ingresa tus credenciales para acceder a tu cuenta
            </Typography>

            <Box component="form" onSubmit={handleSubmit}>
              {errors.general && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {errors.general}
                </Alert>
              )}
              
              <TextField
                fullWidth
                id="email"
                label="Email o Nombre de Usuario"
                name="email"
                type="text"
                placeholder="tu@email.com o tu_usuario"
                value={formData.email}
                onChange={handleChange}
                error={!!errors.email}
                helperText={errors.email}
                disabled={loading}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                  },
                }}
              />

              <TextField
                fullWidth
                name="password"
                label="Contraseña"
                type={showPassword ? 'text' : 'password'}
                placeholder="Tu contraseña"
                value={formData.password}
                onChange={handleChange}
                error={!!errors.password}
                helperText={errors.password}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  mb: 4,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                  },
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{
                  py: 1.5,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: '1rem',
                  backgroundColor: '#1a1a1a',
                  '&:hover': {
                    backgroundColor: '#000000',
                  },
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Iniciar Sesión'}
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    </Box>
  )
}

export default Login
