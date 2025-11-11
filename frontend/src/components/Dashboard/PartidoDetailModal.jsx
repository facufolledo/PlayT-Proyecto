import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  Avatar,
  Stack,
  Paper,
} from '@mui/material'
import {
  Close,
  SportsTennis,
  EmojiEvents,
  TrendingUp,
  TrendingDown,
  LocationOn,
  CalendarToday,
} from '@mui/icons-material'

const PartidoDetailModal = ({ open, onClose, partido, usuarioActual }) => {
  if (!partido) return null

  const { partidoCompleto } = partido

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
              Detalles del Partido
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
              ID: {partido.id}
            </Typography>
          </Box>
          <Button
            onClick={onClose}
            sx={{ minWidth: 'auto', p: 1 }}
          >
            <Close />
          </Button>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 2 }}>
        {/* Información general */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CalendarToday color="primary" />
                  Información General
                </Typography>
                <Stack spacing={1}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Fecha
                    </Typography>
                    <Typography variant="body1">
                      {new Date(partido.fecha).toLocaleDateString('es-ES', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Club
                    </Typography>
                    <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <LocationOn fontSize="small" />
                      {partido.club}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Categoría
                    </Typography>
                    <Chip label={partido.categoria} size="small" color="primary" />
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Estado
                    </Typography>
                    <Chip 
                      label={partido.estado} 
                      size="small" 
                      color={partido.estado === 'Completado' ? 'success' : 'default'}
                    />
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <EmojiEvents color="primary" />
                  Resultado
                </Typography>
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h3" component="div" sx={{ 
                    fontWeight: 'bold',
                    color: partido.ganado ? 'success.main' : 'error.main'
                  }}>
                    {partido.resultado}
                  </Typography>
                  <Typography variant="h6" color="text.secondary" sx={{ mt: 1 }}>
                    {partido.ganado ? '¡Ganaste!' : 'Perdiste'}
                  </Typography>
                  
                  {partido.puntosSumados !== 0 && (
                    <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                      {partido.puntosSumados > 0 ? (
                        <TrendingUp color="success" />
                      ) : (
                        <TrendingDown color="error" />
                      )}
                      <Typography 
                        variant="h6" 
                        color={partido.puntosSumados > 0 ? 'success.main' : 'error.main'}
                        sx={{ fontWeight: 'bold' }}
                      >
                        {partido.puntosSumados > 0 ? '+' : ''}{partido.puntosSumados} puntos
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Detalle de sets */}
        {partido.setsDetalle && partido.setsDetalle.length > 0 && (
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SportsTennis color="primary" />
                Detalle de Sets
              </Typography>
              
              <Grid container spacing={2}>
                {partido.setsDetalle.map((set, index) => (
                  <Grid item xs={12} sm={4} key={set.set}>
                    <Paper 
                      elevation={1} 
                      sx={{ 
                        p: 2, 
                        textAlign: 'center',
                        backgroundColor: set.usuario > set.oponente ? 'success.light' : 
                                       set.usuario < set.oponente ? 'error.light' : 'grey.100'
                      }}
                    >
                      <Typography variant="h6" color="text.secondary" gutterBottom>
                        Set {set.set}
                      </Typography>
                      <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                        {set.usuario} - {set.oponente}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {set.usuario > set.oponente ? 'Ganado' : 
                         set.usuario < set.oponente ? 'Perdido' : 'Empate'}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Jugadores */}
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Jugadores
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Avatar sx={{ width: 60, height: 60, mx: 'auto', mb: 1 }}>
                    {usuarioActual?.nombre?.charAt(0) || 'T'}
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {usuarioActual?.nombre || 'Tú'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {usuarioActual?.ciudad || ''}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Avatar sx={{ width: 60, height: 60, mx: 'auto', mb: 1 }}>
                    {partido.oponente.charAt(0)}
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {partido.oponente}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Oponente
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button onClick={onClose} variant="contained" fullWidth>
          Cerrar
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default PartidoDetailModal
