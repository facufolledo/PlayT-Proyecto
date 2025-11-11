import React, { useState } from 'react'
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { authService } from '../../services/api'

const Register = () => {
  console.log('Renderizando componente Register')
  
  const [formData, setFormData] = useState({
    nombre_usuario: '',
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    confirmPassword: '',
    sexo: 'masculino',
    id_categoria_inicial: '',
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [activeTab, setActiveTab] = useState(1)
  const navigate = useNavigate()

  // Fetch categorías reales desde la API filtradas por sexo
  const { data: categorias = [], isLoading: loadingCategorias, error: categoriasError } = useQuery({
    queryKey: ['categorias', formData.sexo],
    queryFn: () => authService.getCategorias(formData.sexo),
    staleTime: 5 * 60 * 1000, // 5 minutos
    retry: 2,
    onError: (error) => {
      console.error('Error al cargar categorías:', error)
    }
  })

  console.log('Categorías cargadas:', categorias)

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
    if (newValue === 0) {
      navigate('/login')
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.nombre_usuario) {
      newErrors.nombre_usuario = 'El nombre de usuario es requerido'
    } else if (formData.nombre_usuario.length < 3) {
      newErrors.nombre_usuario = 'El nombre de usuario debe tener al menos 3 caracteres'
    }
    
    if (!formData.nombre) {
      newErrors.nombre = 'El nombre es requerido'
    } else if (formData.nombre.length < 2) {
      newErrors.nombre = 'El nombre debe tener al menos 2 caracteres'
    }
    
    if (!formData.apellido) {
      newErrors.apellido = 'El apellido es requerido'
    } else if (formData.apellido.length < 2) {
      newErrors.apellido = 'El apellido debe tener al menos 2 caracteres'
    }
    
    if (!formData.email) {
      newErrors.email = 'El email es requerido'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'El email no es válido'
    }
    
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida'
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres'
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Confirma tu contraseña'
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden'
    }
    
    if (!formData.id_categoria_inicial) {
      newErrors.id_categoria_inicial = 'Selecciona tu categoría inicial'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    console.log('Enviando formulario de registro')
    
    if (!validateForm()) {
      return
    }
    
    setLoading(true)
    
    try {
      const { confirmPassword, ...userData } = formData
      console.log('Datos de registro:', userData)
      
      // Simular registro por ahora
      setTimeout(() => {
        console.log('Registro simulado exitoso')
        setLoading(false)
        alert('Registro simulado exitoso')
        navigate('/login')
      }, 1000)
    } catch (error) {
      console.error('Error en registro:', error)
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

      {/* Right Section - Register Form */}
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
              Únete a PULSE
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Crea tu cuenta para comenzar a jugar
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

          {/* Register Form */}
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
              Registrarse
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Completa tus datos para crear tu cuenta
            </Typography>

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                id="nombre_usuario"
                label="Nombre de Usuario"
                name="nombre_usuario"
                placeholder="Tu nombre de usuario"
                value={formData.nombre_usuario}
                onChange={handleChange}
                error={!!errors.nombre_usuario}
                helperText={errors.nombre_usuario}
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
                id="nombre"
                label="Nombre"
                name="nombre"
                placeholder="Tu nombre"
                value={formData.nombre}
                onChange={handleChange}
                error={!!errors.nombre}
                helperText={errors.nombre}
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
                id="apellido"
                label="Apellido"
                name="apellido"
                placeholder="Tu apellido"
                value={formData.apellido}
                onChange={handleChange}
                error={!!errors.apellido}
                helperText={errors.apellido}
                disabled={loading}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                  },
                }}
              />

              <FormControl
                fullWidth
                error={!!errors.sexo}
                disabled={loading}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                  },
                }}
              >
                <InputLabel>Sexo</InputLabel>
                <Select
                  id="sexo"
                  name="sexo"
                  value={formData.sexo}
                  onChange={handleChange}
                  label="Sexo"
                >
                  <MenuItem value="masculino">Masculino</MenuItem>
                  <MenuItem value="femenino">Femenino</MenuItem>
                </Select>
                {errors.sexo && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                    {errors.sexo}
                  </Typography>
                )}
              </FormControl>

              <TextField
                fullWidth
                id="email"
                label="Email"
                name="email"
                type="email"
                placeholder="tu@email.com"
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

              <FormControl
                fullWidth
                error={!!errors.id_categoria_inicial}
                disabled={loading || loadingCategorias}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                  },
                }}
              >
                <InputLabel>Categoría Inicial</InputLabel>
                <Select
                  name="id_categoria_inicial"
                  value={formData.id_categoria_inicial}
                  onChange={handleChange}
                  label="Categoría Inicial"
                >
                  <MenuItem value="">
                    <em>
                      {loadingCategorias ? 'Cargando categorías...' : 'Selecciona tu categoría'}
                    </em>
                  </MenuItem>
                  {categorias.map((categoria) => (
                    <MenuItem key={categoria.id_categoria} value={categoria.id_categoria}>
                      {categoria.nombre} 
                      {" "}
                      {categoria.descripcion}
                      
                                          </MenuItem>
                  ))}
                </Select>
                {errors.id_categoria_inicial && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block' }}>
                    {errors.id_categoria_inicial}
                  </Typography>
                )}
                {categoriasError && (
                  <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block' }}>
                    Error al cargar categorías. Intenta recargar la página.
                  </Typography>
                )}
              </FormControl>

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
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                  },
                }}
              />

              <TextField
                fullWidth
                name="confirmPassword"
                label="Confirmar Contraseña"
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Confirma tu contraseña"
                value={formData.confirmPassword}
                onChange={handleChange}
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        edge="end"
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
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
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Crear Cuenta'}
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    </Box>
  )
}

export default Register
