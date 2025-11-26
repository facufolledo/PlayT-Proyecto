import React from 'react';
import { Platform } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { HomeScreen } from '../screens/home/HomeScreen';
import { TorneosScreen } from '../screens/torneos/TorneosScreen';
import { SalasScreen } from '../screens/salas/SalasScreen';
import { RankingsScreen } from '../screens/rankings/RankingsScreen';
import { PerfilScreen } from '../screens/perfil/PerfilScreen';

const Tab = createBottomTabNavigator();

export const MainNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#0E0F11',
          borderTopColor: '#3A4558',
          borderTopWidth: 1,
          height: Platform.OS === 'android' ? 70 : 60,
          paddingBottom: Platform.OS === 'android' ? 12 : 8,
          paddingTop: 8,
        },
        tabBarActiveTintColor: '#0055FF',
        tabBarInactiveTintColor: '#64748B',
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarLabel: 'Inicio',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons name={focused ? "home" : "home-outline"} size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen 
        name="Torneos" 
        component={TorneosScreen}
        options={{
          tabBarLabel: 'Torneos',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons name={focused ? "trophy" : "trophy-outline"} size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen 
        name="Salas" 
        component={SalasScreen}
        options={{
          tabBarLabel: 'Jugar',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons name={focused ? "game-controller" : "game-controller-outline"} size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen 
        name="Rankings" 
        component={RankingsScreen}
        options={{
          tabBarLabel: 'Rankings',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons name={focused ? "bar-chart" : "bar-chart-outline"} size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen 
        name="Perfil" 
        component={PerfilScreen}
        options={{
          tabBarLabel: 'Perfil',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons name={focused ? "person-circle" : "person-circle-outline"} size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};
