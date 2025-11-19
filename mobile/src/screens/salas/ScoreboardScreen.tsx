import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { useWebSocket } from '../../hooks/useWebSocket';
import { Button } from '../../components/common/Button';
import { ScoreboardLive } from '../../components/salas/ScoreboardLive';
import { MarcadorInteractivo } from '../../components/salas/MarcadorInteractivo';

export const ScoreboardScreen = ({ route, navigation }: any) => {
  const { salaId, esJugador = false } = route.params;
  const { isConnected, updateScore, finalizarPartido } = useWebSocket({ salaId });
  
  const [marcador, setMarcador] = useState({
    equipo1Puntos: 0,
    equipo2Puntos: 0,
    equipo1Sets: 0,
    equipo2Sets: 0,
    estado: 'en_curso',
  });

  const [sala, setSala] = useState({
    nombre: 'Partido en Vivo',
    equipo1: 'Equipo 1',
    equipo2: 'Equipo 2',
  });

  // Escuchar actualizaciones del marcador
  useEffect(() => {
    const handleScoreUpdate = (data: any) => {
      setMarcador({
        equipo1Puntos: data.equipo1Puntos,
        equipo2Puntos: data.equipo2Puntos,
        equipo1Sets: data.equipo1Sets,
        equipo2Sets: data.equipo2Sets,
        estado: data.estado,
      });
    };

    const handlePartidoFinalizado = (data: any) => {
      Alert.alert(
        'Partido Finalizado',
        `Ganador: ${data.ganador}\nResultado: ${data.resultado}`,
        [
          { text: 'OK', onPress: () => navigation.goBack() }
        ]
      );
    };

    // Suscribirse a eventos
    const ws = require('../../services/websocket.service').websocketService;
    ws.onScoreUpdate(handleScoreUpdate);
    ws.onPartidoFinalizado(handlePartidoFinalizado);

    // Cleanup
    return () => {
      ws.off('score-updated', handleScoreUpdate);
      ws.off('partido-finalizado', handlePartidoFinalizado);
    };
  }, [navigation]);

  const handleUpdateScore = (nuevoMarcador: any) => {
    const data = {
      salaId,
      ...nuevoMarcador,
    };
    updateScore(data);
    setMarcador(nuevoMarcador);
  };

  const handleFinalizarPartido = () => {
    Alert.alert(
      'Finalizar Partido',
      '¿Estás seguro de que quieres finalizar el partido?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Finalizar',
          style: 'destructive',
          onPress: () => {
            const ganador = marcador.equipo1Sets > marcador.equipo2Sets 
              ? sala.equipo1 
              : sala.equipo2;
            
            finalizarPartido({
              salaId,
              ganador,
              resultado: `${marcador.equipo1Sets}-${marcador.equipo2Sets}`,
            });
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backIcon}>←</Text>
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.title}>{sala.nombre}</Text>
          <View style={styles.connectionStatus}>
            <View style={[
              styles.connectionDot,
              { backgroundColor: isConnected ? '#00C853' : '#FF0055' }
            ]} />
            <Text style={styles.connectionText}>
              {isConnected ? 'En vivo' : 'Desconectado'}
            </Text>
          </View>
        </View>
      </View>

      {/* Scoreboard */}
      <ScoreboardLive
        equipo1={sala.equipo1}
        equipo2={sala.equipo2}
        marcador={marcador}
      />

      {/* Marcador Interactivo (solo para jugadores) */}
      {esJugador && (
        <View style={styles.interactiveSection}>
          <MarcadorInteractivo
            marcador={marcador}
            onUpdateScore={handleUpdateScore}
          />
          
          <Button
            title="Finalizar Partido"
            onPress={handleFinalizarPartido}
            variant="ghost"
          />
        </View>
      )}

      {/* Espectador */}
      {!esJugador && (
        <View style={styles.spectatorSection}>
          <Text style={styles.spectatorIcon}>👁️</Text>
          <Text style={styles.spectatorText}>Modo Espectador</Text>
          <Text style={styles.spectatorSubtext}>
            Estás viendo el partido en tiempo real
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1A1F2E',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    gap: 16,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#3A4558',
    alignItems: 'center',
    justifyContent: 'center',
  },
  backIcon: {
    fontSize: 24,
    color: '#E8E9EB',
  },
  headerInfo: {
    flex: 1,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 4,
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  connectionDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  connectionText: {
    fontSize: 14,
    color: '#94A3B8',
  },
  interactiveSection: {
    flex: 1,
    padding: 20,
  },
  spectatorSection: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  spectatorIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  spectatorText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 8,
  },
  spectatorSubtext: {
    fontSize: 16,
    color: '#94A3B8',
    textAlign: 'center',
  },
});
