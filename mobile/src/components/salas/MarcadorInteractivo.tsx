import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface MarcadorInteractivoProps {
  marcador: {
    equipo1Puntos: number;
    equipo2Puntos: number;
    equipo1Sets: number;
    equipo2Sets: number;
    estado: string;
  };
  onUpdateScore: (nuevoMarcador: any) => void;
}

export const MarcadorInteractivo = ({ marcador, onUpdateScore }: MarcadorInteractivoProps) => {
  const agregarPunto = (equipo: 1 | 2) => {
    const nuevoMarcador = { ...marcador };
    
    if (equipo === 1) {
      nuevoMarcador.equipo1Puntos++;
      // Verificar si ganó el set
      if (nuevoMarcador.equipo1Puntos >= 11 && nuevoMarcador.equipo1Puntos - nuevoMarcador.equipo2Puntos >= 2) {
        nuevoMarcador.equipo1Sets++;
        nuevoMarcador.equipo1Puntos = 0;
        nuevoMarcador.equipo2Puntos = 0;
      }
    } else {
      nuevoMarcador.equipo2Puntos++;
      // Verificar si ganó el set
      if (nuevoMarcador.equipo2Puntos >= 11 && nuevoMarcador.equipo2Puntos - nuevoMarcador.equipo1Puntos >= 2) {
        nuevoMarcador.equipo2Sets++;
        nuevoMarcador.equipo1Puntos = 0;
        nuevoMarcador.equipo2Puntos = 0;
      }
    }
    
    onUpdateScore(nuevoMarcador);
  };

  const restarPunto = (equipo: 1 | 2) => {
    const nuevoMarcador = { ...marcador };
    
    if (equipo === 1 && nuevoMarcador.equipo1Puntos > 0) {
      nuevoMarcador.equipo1Puntos--;
    } else if (equipo === 2 && nuevoMarcador.equipo2Puntos > 0) {
      nuevoMarcador.equipo2Puntos--;
    }
    
    onUpdateScore(nuevoMarcador);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Actualizar Marcador</Text>
      
      {/* Equipo 1 */}
      <View style={styles.equipoContainer}>
        <Text style={styles.equipoLabel}>Equipo 1</Text>
        <View style={styles.controls}>
          <TouchableOpacity
            style={styles.buttonMinus}
            onPress={() => restarPunto(1)}
          >
            <Text style={styles.buttonText}>-</Text>
          </TouchableOpacity>
          <View style={styles.scoreDisplay}>
            <Text style={styles.scoreText}>{marcador.equipo1Puntos}</Text>
          </View>
          <TouchableOpacity
            style={styles.buttonPlus}
            onPress={() => agregarPunto(1)}
          >
            <Text style={styles.buttonText}>+</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Equipo 2 */}
      <View style={styles.equipoContainer}>
        <Text style={styles.equipoLabel}>Equipo 2</Text>
        <View style={styles.controls}>
          <TouchableOpacity
            style={styles.buttonMinus}
            onPress={() => restarPunto(2)}
          >
            <Text style={styles.buttonText}>-</Text>
          </TouchableOpacity>
          <View style={styles.scoreDisplay}>
            <Text style={styles.scoreText}>{marcador.equipo2Puntos}</Text>
          </View>
          <TouchableOpacity
            style={styles.buttonPlus}
            onPress={() => agregarPunto(2)}
          >
            <Text style={styles.buttonText}>+</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Información */}
      <View style={styles.infoContainer}>
        <Text style={styles.infoText}>
          💡 Los sets se actualizan automáticamente al llegar a 11 puntos con 2 de diferencia
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#0E0F11',
    borderWidth: 1,
    borderColor: '#3A4558',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E8E9EB',
    marginBottom: 20,
    textAlign: 'center',
  },
  equipoContainer: {
    marginBottom: 20,
  },
  equipoLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#94A3B8',
    marginBottom: 12,
  },
  controls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
  },
  buttonMinus: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#FF0055',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonPlus: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#00C853',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
  },
  scoreDisplay: {
    width: 80,
    height: 80,
    borderRadius: 12,
    backgroundColor: '#3A4558',
    alignItems: 'center',
    justifyContent: 'center',
  },
  scoreText: {
    fontSize: 40,
    fontWeight: 'bold',
    color: '#E8E9EB',
  },
  infoContainer: {
    backgroundColor: 'rgba(0, 85, 255, 0.1)',
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
  },
  infoText: {
    fontSize: 12,
    color: '#94A3B8',
    textAlign: 'center',
    lineHeight: 18,
  },
});
