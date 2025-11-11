import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Avatar,
  Chip,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
  Divider,
  Badge,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stack,
  CircularProgress,
  Alert,
  Skeleton,
} from '@mui/material'
import {
  TrendingUp,
  SportsTennis,
  EmojiEvents,
  Person,
  Notifications,
  Menu as MenuIcon,
  Home,
  BarChart,
  History,
  Settings,
  Logout,
  Add,
  Star,
  CheckCircle,
  Cancel,
  Schedule,
} from '@mui/icons-material'
import { useDashboard } from '../../hooks/useDashboard'
import PartidoDetailModal from './PartidoDetailModal'

const Dashboard = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [mobileOpen, setMobileOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('inicio')
  const [selectedPartido, setSelectedPartido] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)

  // Usar el hook personalizado para obtener datos reales
  const {
    user,
    isAuthenticated,
    currentUser,
    loadingUser,
    loadingRanking,
    loadingMatches,
    userError,
    rankingError,
    matchesError,
    userStats,
    recentMatches,
    topRankings,
    logout
  } = useDashboard()

  // El ProtectedRoute ya maneja la autenticación, no necesitamos verificar aquí

  const menuItems = [
    { id: 'inicio', label: 'Inicio', icon: <Home /> },
    { id: 'estadisticas', label: 'Estadísticas', icon: <BarChart /> },
    { id: 'partidos', label: 'Mis Partidos', icon: <SportsTennis /> },
    { id: 'historial', label: 'Historial', icon: <History /> },
    { id: 'configuracion', label: 'Configuración', icon: <Settings /> },
  ]

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const handlePartidoClick = (partido) => {
    setSelectedPartido(partido)
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setSelectedPartido(null)
  }

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <img 
            src="/images/Pulse-logo.png" 
            alt="Pulse Logo" 
            style={{ width: 32, height: 32 }}
          />
          <Typography variant="h6" noWrap component="div">
            PULSE
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton
              selected={activeTab === item.id}
              onClick={() => setActiveTab(item.id)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.main,
                  color: 'white',
                  '&:hover': {
                    backgroundColor: theme.palette.primary.dark,
                  },
                },
              }}
            >
              <ListItemIcon sx={{ color: activeTab === item.id ? 'white' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={logout}>
            <ListItemIcon>
              <Logout />
            </ListItemIcon>
            <ListItemText primary="Cerrar Sesión" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - 250px)` },
          ml: { md: '250px' },
          backgroundColor: 'white',
          color: 'text.primary',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Dashboard de Pádel
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
              <Avatar sx={{ width: 32, height: 32 }}>
                {userStats?.imagen ? (
                  <img src={userStats.imagen} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <Person />
                )}
              </Avatar>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  {userStats?.nombre || 'Cargando...'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {userStats?.ciudad || ''}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: 250 }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - 250px)` },
          mt: '64px',
          p: 3,
        }}
      >
        <Container maxWidth="xl">
          {/* Mostrar errores si los hay */}
          {(userError || rankingError || matchesError) && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Error al cargar los datos del dashboard. Por favor, recarga la página.
            </Alert>
          )}

          {/* Header con estadísticas principales */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      {loadingUser ? (
                        <Skeleton variant="text" width={60} height={40} />
                      ) : (
                        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                          {userStats?.ranking || 'N/A'}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        Ranking Actual
                      </Typography>
                    </Box>
                    <EmojiEvents sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      {loadingUser ? (
                        <Skeleton variant="text" width={80} height={40} />
                      ) : (
                        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                          {userStats?.rating || 1000}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        Rating ELO
                      </Typography>
                    </Box>
                    <TrendingUp sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #f57c00 0%, #ffb74d 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      {loadingUser ? (
                        <Skeleton variant="text" width={60} height={40} />
                      ) : (
                        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                          {userStats?.partidosJugados || 0}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        Partidos Jugados
                      </Typography>
                    </Box>
                    <SportsTennis sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'linear-gradient(135deg, #7b1fa2 0%, #ba68c8 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      {loadingUser ? (
                        <Skeleton variant="text" width={60} height={40} />
                      ) : (
                        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                          {userStats?.winRate || 0}%
                        </Typography>
                      )}
                      <Typography variant="body2">
                        Win Rate
                      </Typography>
                    </Box>
                    <Star sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Contenido principal */}
          <Grid container spacing={3}>
            {/* Partidos Recientes */}
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      Partidos Recientes
                    </Typography>
                    <Button variant="outlined" size="small" startIcon={<Add />}>
                      Nuevo Partido
                    </Button>
                  </Box>
                  
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Oponente</TableCell>
                          <TableCell>Resultado</TableCell>
                          <TableCell>Fecha</TableCell>
                          <TableCell>Categoría</TableCell>
                          <TableCell>Estado</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {loadingMatches ? (
                          // Mostrar skeletons mientras carga
                          Array.from({ length: 3 }).map((_, index) => (
                            <TableRow key={index}>
                              <TableCell><Skeleton variant="text" width={120} /></TableCell>
                              <TableCell><Skeleton variant="text" width={80} /></TableCell>
                              <TableCell><Skeleton variant="text" width={100} /></TableCell>
                              <TableCell><Skeleton variant="text" width={60} /></TableCell>
                              <TableCell><Skeleton variant="text" width={80} /></TableCell>
                            </TableRow>
                          ))
                        ) : recentMatches.length > 0 ? (
                          recentMatches.map((match) => (
                            <TableRow 
                              key={match.id}
                              hover
                              onClick={() => handlePartidoClick(match)}
                              sx={{ 
                                cursor: 'pointer',
                                '&:hover': {
                                  backgroundColor: 'action.hover'
                                }
                              }}
                            >
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Avatar sx={{ width: 32, height: 32 }}>
                                    {match.oponente.charAt(0)}
                                  </Avatar>
                                  <Box>
                                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                      {match.oponente}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      vs {userStats?.nombre || 'Tú'}
                                    </Typography>
                                  </Box>
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                  {match.resultado}
                                </Typography>
                                {match.puntosSumados !== 0 && (
                                  <Typography 
                                    variant="caption" 
                                    color={match.puntosSumados > 0 ? 'success.main' : 'error.main'}
                                  >
                                    {match.puntosSumados > 0 ? '+' : ''}{match.puntosSumados} pts
                                  </Typography>
                                )}
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" color="text.secondary">
                                  {new Date(match.fecha).toLocaleDateString()}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Chip label={match.categoria} size="small" color="primary" />
                              </TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  {match.ganado ? (
                                    <CheckCircle color="success" fontSize="small" />
                                  ) : (
                                    <Cancel color="error" fontSize="small" />
                                  )}
                                  <Typography variant="body2" color={match.ganado ? 'success.main' : 'error.main'}>
                                    {match.ganado ? 'Ganado' : 'Perdido'}
                                  </Typography>
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={5} sx={{ textAlign: 'center', py: 4 }}>
                              <Typography variant="body2" color="text.secondary">
                                No tienes partidos registrados aún
                              </Typography>
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Rankings y Estadísticas */}
            <Grid item xs={12} md={4}>
              <Stack spacing={3}>
                {/* Top Rankings */}
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                      Top Rankings
                    </Typography>
                    {loadingRanking ? (
                      // Mostrar skeletons mientras carga
                      Array.from({ length: 5 }).map((_, index) => (
                        <Box key={index} sx={{ mb: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Skeleton variant="text" width={30} />
                              <Box>
                                <Skeleton variant="text" width={120} />
                                <Skeleton variant="text" width={80} />
                              </Box>
                            </Box>
                            <Skeleton variant="text" width={60} />
                          </Box>
                          {index < 4 && <Divider sx={{ mt: 1 }} />}
                        </Box>
                      ))
                    ) : topRankings.length > 0 ? (
                      topRankings.map((player, index) => (
                        <Box key={player.posicion} sx={{ mb: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="h6" color="primary">
                                #{player.posicion}
                              </Typography>
                              <Box>
                                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                  {player.nombre}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {player.partidos} partidos
                                </Typography>
                              </Box>
                            </Box>
                            <Typography variant="body2" color="primary" sx={{ fontWeight: 'bold' }}>
                              {player.rating}
                            </Typography>
                          </Box>
                          {index < topRankings.length - 1 && <Divider sx={{ mt: 1 }} />}
                        </Box>
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                        No hay datos de ranking disponibles
                      </Typography>
                    )}
                  </CardContent>
                </Card>

                {/* Próximos Partidos */}
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                      Próximos Partidos
                    </Typography>
                    <Box sx={{ textAlign: 'center', py: 3 }}>
                      <Schedule sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        No tienes partidos programados
                      </Typography>
                      <Button variant="outlined" size="small" sx={{ mt: 1 }}>
                        Programar Partido
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Stack>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Modal de detalles del partido */}
      <PartidoDetailModal
        open={modalOpen}
        onClose={handleCloseModal}
        partido={selectedPartido}
        usuarioActual={userStats}
      />
    </Box>
  )
}

export default Dashboard