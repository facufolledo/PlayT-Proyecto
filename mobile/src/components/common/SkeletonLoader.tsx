import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';

interface SkeletonLoaderProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: any;
}

export const SkeletonLoader = ({ 
  width = '100%', 
  height = 20, 
  borderRadius = 8,
  style 
}: SkeletonLoaderProps) => {
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 0.7,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    );
    animation.start();
    return () => animation.stop();
  }, [opacity]);

  return (
    <Animated.View
      style={[
        styles.skeleton,
        { width, height, borderRadius, opacity },
        style,
      ]}
    />
  );
};

// Skeleton presets
export const SkeletonCard = () => (
  <View style={styles.skeletonCard}>
    <View style={styles.skeletonHeader}>
      <SkeletonLoader width={40} height={40} borderRadius={20} />
      <View style={styles.skeletonHeaderText}>
        <SkeletonLoader width="70%" height={18} />
        <SkeletonLoader width="50%" height={14} style={{ marginTop: 8 }} />
      </View>
    </View>
    <SkeletonLoader width="100%" height={60} style={{ marginTop: 16 }} />
    <View style={styles.skeletonFooter}>
      <SkeletonLoader width="30%" height={14} />
      <SkeletonLoader width="30%" height={14} />
    </View>
  </View>
);

export const SkeletonList = ({ count = 3 }: { count?: number }) => (
  <View>
    {Array.from({ length: count }).map((_, i) => (
      <SkeletonCard key={i} />
    ))}
  </View>
);

const styles = StyleSheet.create({
  skeleton: {
    backgroundColor: '#3A4558',
  },
  skeletonCard: {
    backgroundColor: '#0E0F11',
    borderRadius: 20,
    padding: 16,
    marginBottom: 12,
  },
  skeletonHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  skeletonHeaderText: {
    flex: 1,
  },
  skeletonFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
  },
});
