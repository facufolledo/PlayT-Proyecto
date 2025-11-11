# PlayT Frontend 🏓

Frontend de la aplicación PlayT, un sistema de gestión de torneos de pádel con ranking dinámico basado en el algoritmo Elo.

## 🚀 Características

- **React 18**: Biblioteca de interfaz de usuario moderna
- **Vite**: Bundler rápido y eficiente
- **Material-UI**: Componentes de UI profesionales
- **React Router**: Navegación entre páginas
- **React Query**: Gestión de estado del servidor
- **Axios**: Cliente HTTP para comunicación con la API
- **Responsive Design**: Diseño adaptable a móviles y tablets

## 🛠️ Tecnologías

- React 18.2.0
- Vite 4.1.0
- Material-UI 5.11.10
- React Router DOM 6.8.1
- React Query 3.39.3
- Axios 1.3.4
- React Hook Form 7.43.5
- React Hot Toast 2.4.0

## 📋 Requisitos

- Node.js 16 o superior
- npm o yarn
- Backend PlayT ejecutándose en `http://localhost:8000`

## 🔧 Instalación

1. **Instalar dependencias**
   ```bash
   npm install
   ```

2. **Configurar variables de entorno** (opcional)
   ```bash
   # Crear archivo .env si es necesario
   cp .env.example .env
   ```

3. **Ejecutar en desarrollo**
   ```bash
   npm run dev
   ```

4. **Abrir en el navegador**
   ```
   http://localhost:3000
   ```

## 📁 Estructura del Proyecto

```
frontend/
├── public/                 # Archivos estáticos
├── src/
│   ├── components/         # Componentes React
│   │   ├── Auth/          # Componentes de autenticación
│   │   ├── Dashboard/     # Dashboard principal
│   │   ├── Partidos/      # Gestión de partidos
│   │   ├── Ranking/       # Sistema de ranking
│   │   ├── Resultados/    # Gestión de resultados
│   │   ├── Usuarios/      # Perfiles de usuario
│   │   ├── Hooks/         # Hooks personalizados
│   │   └── Utils/         # Utilidades y layout
│   ├── services/          # Servicios de API
│   ├── assets/            # Recursos estáticos
│   ├── App.jsx           # Componente principal
│   ├── main.jsx          # Punto de entrada
│   └── index.css         # Estilos globales
├── package.json
├── vite.config.js
└── README.md
```

## 🎯 Funcionalidades Principales

### 🔐 Autenticación
- Login y registro de usuarios
- Gestión de sesiones con JWT
- Protección de rutas

### 📊 Dashboard
- Vista general del sistema
- Estadísticas de partidos
- Ranking actualizado
- Partidos recientes

### 🏆 Gestión de Partidos
- Lista de partidos
- Creación de nuevos partidos
- Detalles de partido
- Estados: pendiente, reportado, confirmado

### 📈 Sistema de Resultados
- Reportar resultados
- Confirmar resultados
- Cálculo automático de Elo
- Historial de cambios de rating

### 🏅 Ranking
- Lista de jugadores ordenados por rating
- Historial de cambios de Elo
- Estadísticas individuales

### 👤 Perfil de Usuario
- Información personal
- Estadísticas de juego
- Historial de partidos

## 🔄 Flujo de Confirmación de Resultados

El sistema implementa un flujo seguro de confirmación:

1. **Reportar Resultado**: Un equipo reporta el resultado del partido
2. **Confirmar Resultado**: El equipo rival confirma el resultado
3. **Calcular Elo**: Se calcula y aplica el nuevo rating

## 🚀 Scripts Disponibles

```bash
# Desarrollo
npm run dev

# Construcción para producción
npm run build

# Vista previa de producción
npm run preview

# Linting
npm run lint
```

## 🔧 Configuración

### Proxy de API
El proyecto está configurado para hacer proxy de las peticiones `/api` al backend en `http://localhost:8000`. Esto se configura en `vite.config.js`.

### Variables de Entorno
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=PlayT
```

## 🎨 Tema y Estilos

El proyecto utiliza Material-UI con un tema personalizado para PlayT:

- **Colores principales**: Azul (#1976d2) y Rojo (#dc004e)
- **Tipografía**: Roboto
- **Diseño**: Responsive y moderno

## 📱 Responsive Design

La aplicación está optimizada para:
- **Desktop**: Navegación completa con sidebar
- **Tablet**: Diseño adaptativo
- **Móvil**: Navegación con drawer

## 🔌 Integración con Backend

El frontend se comunica con el backend PlayT a través de:

- **Autenticación**: JWT tokens
- **Partidos**: CRUD completo
- **Resultados**: Flujo de confirmación
- **Ranking**: Sistema Elo
- **Usuarios**: Gestión de perfiles

## 🚀 Despliegue

### Desarrollo
```bash
npm run dev
```

### Producción
```bash
npm run build
npm run preview
```

### Docker (opcional)
```bash
docker build -t playt-frontend .
docker run -p 3000:3000 playt-frontend
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo
- Revisar la documentación del backend

---

**PlayT** - Sistema de Gestión de Torneos de Pádel 🏓
