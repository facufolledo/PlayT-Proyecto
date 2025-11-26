import React from 'react';
import { View, StyleSheet, ImageBackground } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

interface BackgroundPatternProps {
  children: React.ReactNode;
}

export const BackgroundPattern = ({ children }: BackgroundPatternProps) => {
  return (
    <View style={styles.container}>
      {/* Imagen de fondo de pádel */}
      <ImageBackground
        source={{ uri: 'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800&q=80' }}
        style={styles.backgroundImage}
        resizeMode="cover"
      >
        {/* Overlay oscuro con gradiente */}
        <LinearGradient
          colors={['rgba(26, 31, 46, 0.95)', 'rgba(26, 31, 46, 0.98)', 'rgba(26, 31, 46, 1)']}
          style={styles.gradient}
        />
      </ImageBackground>
      
      {/* Contenido */}
      <View style={styles.content}>
        {children}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    position: 'relative',
  },
  backgroundImage: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    width: '100%',
    height: '100%',
  },
  gradient: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    width: '100%',
    height: '100%',
  },
  content: {
    flex: 1,
    position: 'relative',
    zIndex: 1,
  },
});
