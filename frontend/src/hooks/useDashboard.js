import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { dashboardService } from '../services/dashboardService'

export const useDashboard = () => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Verificar autenticación al cargar
  useEffect(() => {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData))
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Error al parsear datos de usuario:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }, [])

  // Query para obtener datos del usuario actual
  const { data: currentUser, isLoading: loadingUser, error: userError } = useQuery({
    queryKey: ['currentUser'],
    queryFn: dashboardService.getCurrentUser,
    enabled: isAuthenticated,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutos
  })

  // Query para obtener ranking general
  const { data: ranking = [], isLoading: loadingRanking, error: rankingError } = useQuery({
    queryKey: ['ranking'],
    queryFn: () => dashboardService.getRanking(10, 0),
    enabled: isAuthenticated,
    retry: 2,
    staleTime: 2 * 60 * 1000, // 2 minutos
  })

  // Query para obtener top semanal
  const { data: topWeekly = [], isLoading: loadingTopWeekly, error: topWeeklyError } = useQuery({
    queryKey: ['topWeekly'],
    queryFn: () => dashboardService.getTopWeekly(5),
    enabled: isAuthenticated,
    retry: 2,
    staleTime: 2 * 60 * 1000, // 2 minutos
  })

  // Query para obtener partidos del usuario
  const { data: userMatches = [], isLoading: loadingMatches, error: matchesError } = useQuery({
    queryKey: ['userMatches', currentUser?.id_usuario],
    queryFn: () => {
      console.log('🏓 Obteniendo partidos para usuario:', currentUser?.id_usuario)
      return dashboardService.getUserMatches(currentUser?.id_usuario, 10)
    },
    enabled: isAuthenticated && !!currentUser?.id_usuario,
    retry: 2,
    staleTime: 1 * 60 * 1000, // 1 minuto
    onSuccess: (data) => {
      console.log('🏓 Partidos obtenidos:', data)
    },
    onError: (error) => {
      console.error('❌ Error al obtener partidos:', error)
    }
  })

  // Query para obtener historial de rating
  const { data: ratingHistory, isLoading: loadingHistory, error: historyError } = useQuery({
    queryKey: ['ratingHistory', currentUser?.id_usuario],
    queryFn: () => dashboardService.getUserRatingHistory(currentUser?.id_usuario, 10),
    enabled: isAuthenticated && !!currentUser?.id_usuario,
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutos
  })

  // Función para cerrar sesión
  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    setIsAuthenticated(false)
    window.location.href = '/login'
  }

  // Calcular estadísticas del usuario
  const getUserStats = () => {
    if (!currentUser) return null

    const partidosGanados = userMatches.filter(match => {
      // Determinar si el usuario ganó el partido
      if (match.id_creador === currentUser.id_usuario) {
        return match.ganador_id === currentUser.id_usuario
      }
      return match.ganador_id === currentUser.id_usuario
    }).length

    const partidosPerdidos = userMatches.length - partidosGanados
    const winRate = userMatches.length > 0 ? (partidosGanados / userMatches.length) * 100 : 0

    return {
      nombre: currentUser.nombre || currentUser.nombre_usuario,
      apellido: currentUser.apellido || '',
      ranking: ranking.findIndex(player => player.id_usuario === currentUser.id_usuario) + 1 || 'N/A',
      rating: currentUser.rating || 1000,
      partidosJugados: currentUser.partidos_jugados || 0,
      partidosGanados,
      partidosPerdidos,
      winRate: Math.round(winRate * 10) / 10,
      ciudad: currentUser.ciudad || '',
      pais: currentUser.pais || '',
      imagen: currentUser.url_avatar || null
    }
  }

  // Formatear partidos para el dashboard
  const getFormattedMatches = () => {
    console.log('🏓 Formateando partidos:', userMatches)
    return userMatches.map(match => {
      console.log('🏓 Procesando partido:', match)
      
      // Determinar el oponente y el equipo del usuario
      let oponente = 'Jugador'
      let oponenteId = null
      let usuarioEquipo = null
      let oponenteEquipo = null
      
      if (match.jugadores && match.jugadores.length > 0) {
        // Buscar el usuario actual en los jugadores
        const usuarioJugador = match.jugadores.find(j => j.id_usuario === currentUser?.id_usuario)
        const otroJugador = match.jugadores.find(j => j.id_usuario !== currentUser?.id_usuario)
        
        if (usuarioJugador) {
          usuarioEquipo = usuarioJugador.equipo
          console.log('🏓 Usuario equipo:', usuarioEquipo)
        }
        
        if (otroJugador) {
          oponente = otroJugador.nombre || otroJugador.nombre_usuario || 'Jugador'
          oponenteId = otroJugador.id_usuario
          oponenteEquipo = otroJugador.equipo
          console.log('🏓 Oponente:', oponente, 'Equipo:', oponenteEquipo)
        }
      } else if (match.creador && match.creador.id_usuario !== currentUser?.id_usuario) {
        // Fallback si no hay jugadores en la respuesta
        oponente = match.creador.nombre_usuario || 'Jugador'
        oponenteId = match.creador.id_usuario
      }

      // Determinar si ganó y el resultado detallado
      let ganado = false
      let resultado = 'Pendiente'
      let setsDetalle = []
      let puntosSumados = 0

      if (match.resultado) {
        console.log('🏓 Resultado del partido:', match.resultado)
        const setsEq1 = match.resultado.sets_eq1 || 0
        const setsEq2 = match.resultado.sets_eq2 || 0
        console.log('🏓 Sets equipo 1:', setsEq1, 'Sets equipo 2:', setsEq2)
        
        // Determinar qué equipo es el usuario actual
        let usuarioEsEq1 = false
        if (usuarioEquipo !== null) {
          usuarioEsEq1 = usuarioEquipo === 1
        } else {
          // Fallback: asumir que el creador es equipo 1
          usuarioEsEq1 = match.id_creador === currentUser?.id_usuario
        }
        
        console.log('🏓 Usuario es equipo 1:', usuarioEsEq1)
        
        // Determinar quién ganó
        if (usuarioEsEq1) {
          ganado = setsEq1 > setsEq2
          resultado = `${setsEq1}-${setsEq2}`
        } else {
          ganado = setsEq2 > setsEq1
          resultado = `${setsEq2}-${setsEq1}`
        }
        
        console.log('🏓 Ganado:', ganado, 'Resultado:', resultado)
        
        // Procesar detalle de sets desde el JSON
        if (match.resultado.detalle_sets && Array.isArray(match.resultado.detalle_sets)) {
          setsDetalle = match.resultado.detalle_sets.map((set, index) => ({
            set: index + 1,
            usuario: usuarioEsEq1 ? (set.eq1 || 0) : (set.eq2 || 0),
            oponente: usuarioEsEq1 ? (set.eq2 || 0) : (set.eq1 || 0)
          }))
          console.log('🏓 Sets detalle desde JSON:', setsDetalle)
        } else {
          // Fallback: crear sets básicos basados en el resultado total
          // Si no hay detalle, asumir que se jugaron 2 sets
          setsDetalle = [
            {
              set: 1,
              usuario: usuarioEsEq1 ? Math.ceil(setsEq1 / 2) : Math.ceil(setsEq2 / 2),
              oponente: usuarioEsEq1 ? Math.ceil(setsEq2 / 2) : Math.ceil(setsEq1 / 2)
            },
            {
              set: 2,
              usuario: usuarioEsEq1 ? Math.floor(setsEq1 / 2) : Math.floor(setsEq2 / 2),
              oponente: usuarioEsEq1 ? Math.floor(setsEq2 / 2) : Math.floor(setsEq1 / 2)
            }
          ]
          console.log('🏓 Sets detalle calculado:', setsDetalle)
        }
        
        // Obtener puntos reales del historial de rating
        if (match.historial_rating) {
          puntosSumados = match.historial_rating.cambio_rating || 0
          console.log('🏓 Puntos reales del historial:', puntosSumados)
        } else {
          // Fallback si no hay historial de rating
          const diferenciaSets = Math.abs(setsEq1 - setsEq2)
          if (ganado) {
            puntosSumados = 20 + (diferenciaSets * 5)
          } else {
            puntosSumados = -10 - (diferenciaSets * 2)
          }
          console.log('🏓 Puntos calculados (fallback):', puntosSumados)
        }
      }

      return {
        id: match.id_partido,
        oponente: oponente,
        oponenteId: oponenteId,
        resultado: resultado,
        ganado: ganado,
        fecha: match.fecha || match.creado_en,
        categoria: match.categoria || 'A',
        estado: match.estado || 'Pendiente',
        setsDetalle: setsDetalle,
        puntosSumados: puntosSumados,
        club: match.club?.nombre || 'Sin especificar',
        // Datos completos del partido para el modal
        partidoCompleto: match
      }
    })
  }

  // Formatear ranking para el dashboard
  const getFormattedRanking = () => {
    return ranking.slice(0, 5).map((player, index) => ({
      posicion: player.posicion || index + 1,
      nombre: player.nombre || player.nombre_usuario,
      rating: player.rating || 1000,
      partidos: player.partidos_jugados || 0,
      ciudad: player.ciudad || '',
      imagen: player.imagen_url || null
    }))
  }

  return {
    // Estado de autenticación
    user,
    isAuthenticated,
    currentUser,
    
    // Estados de carga
    loadingUser,
    loadingRanking,
    loadingMatches,
    loadingTopWeekly,
    loadingHistory,
    
    // Errores
    userError,
    rankingError,
    matchesError,
    topWeeklyError,
    historyError,
    
    // Datos formateados
    userStats: getUserStats(),
    recentMatches: getFormattedMatches(),
    topRankings: getFormattedRanking(),
    topWeekly,
    ratingHistory,
    
    // Acciones
    logout
  }
}
