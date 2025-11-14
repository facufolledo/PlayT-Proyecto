# 🎾 PlayR - Gestión de Rankings de Pádel

PlayR es una aplicación web moderna para gestión de partidos y torneos de pádel, con sistema de ranking dinámico basado en el algoritmo Elo.

## 🎯 Objetivos

Brindar una plataforma completa que permita:
- ✅ Registrar jugadores
- ✅ Crear y gestionar partidos
- ✅ Organizar torneos
- ✅ Reportar resultados set por set
- ✅ Confirmar resultados por el rival
- ✅ Actualizar automáticamente el rating Elo
- ✅ Consultar rankings (global, ciudad, club)
- ✅ Visualizar estadísticas y gráficos

## 👥 Usuarios Objetivo

- **Jugador amateur** → Trackear su nivel y competir con amigos
- **Club de pádel** → Rankings internos para torneos y ligas sociales
- **Organizadores** → Gestionar torneos profesionales

## 🚀 Stack Tecnológico

### Frontend (✅ Completado - Sprint 1)
- **React 19** - Framework UI
- **Vite 7** - Build tool ultrarrápido
- **TailwindCSS 3.4** - Utility-first CSS
- **Framer Motion 11** - Animaciones fluidas
- **Lucide React** - Iconos modernos
- **Recharts 3** - Gráficos y visualizaciones
- **Swapy** - Drag & drop interactivo
- **React Router 7** - Navegación
- **React Query 5** - Gestión de estado servidor
- **React Hot Toast** - Notificaciones

### Backend (En desarrollo por colaborador)
- **Python 3.11+** - Lenguaje principal
- **FastAPI** - Framework web moderno
- **MySQL** - Base de datos
- **SQLAlchemy** - ORM
- **Alembic** - Migraciones
- **JWT** - Autenticación

### Infraestructura
- **Frontend**: Vercel / Cloudflare Pages
- **Backend**: Railway / Render
- **Base de datos**: MySQL en Railway

## 📁 Estructura del Proyecto

```
PlayT/
├── frontend/              ✅ Completado (Sprint 1)
│   ├── src/
│   │   ├── components/    # Componentes UI y Layout
│   │   ├── pages/         # Páginas principales
│   │   ├── context/       # Context API
│   │   ├── services/      # API services
│   │   └── hooks/         # Custom hooks
│   └── [Documentación completa]
│
├── backend/               🔄 En desarrollo
│   ├── src/
│   │   ├── api/           # Endpoints
│   │   ├── models/        # Modelos de datos
│   │   ├── services/      # Lógica de negocio
│   │   └── utils/         # Utilidades
│   └── main.py
│
└── docs/                  📚 Documentación
    ├── 01-vision.md
    ├── 02-alcance.md
    ├── 04-flujos-ux.md
    ├── 05-dominio-y-datos.md
    ├── 06-contrato-api.md
    └── 07-reglas-rating.md
```

## 🎨 Diseño y UX

### Paleta de Colores PlayR
```
Background:     #0F1117  (Negro azulado deportivo)
Primary:        #0055FF  (Azul deportivo)
Secondary:      #7CFF6B  (Verde neón)
Accent:         #FFE600  (Amarillo)
Text Primary:   #FFFFFF  (Blanco)
Text Secondary: #A3A3A3  (Gris)
```

### Características Visuales
- ✅ Modo oscuro deportivo profesional
- ✅ Animaciones fluidas con Framer Motion
- ✅ Diseño responsive (mobile, tablet, desktop)
- ✅ Componentes reutilizables y escalables
- ✅ Transiciones suaves entre páginas

## 🚀 Inicio Rápido

### Frontend

```bash
# Navegar a frontend
cd frontend

# Instalar dependencias
npm install

# Crear archivo .env
copy .env.example .env

# Iniciar servidor de desarrollo
npm run dev

# Abrir en navegador
http://localhost:5173
```

### Backend

```bash
# Navegar a backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy env.template .env

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn main:app --reload

# API disponible en
http://localhost:8000
```

## 📋 Plan de Desarrollo (Sprints)

### ✅ Sprint 1 - Setup Base (COMPLETADO)
- [x] Configuración Vite + React
- [x] TailwindCSS con paleta PlayT
- [x] Componentes UI base (Button, Card, Input, Modal)
- [x] Layout con Sidebar y Navbar
- [x] Páginas Login/Register/Dashboard
- [x] Routing y animaciones
- [x] API service preparado

### ✅ Sprint 2 - Módulo de Salas (COMPLETADO)
- [x] CRUD completo de salas/partidos
- [x] Marcador interactivo con controles +/-
- [x] Sistema de estados (programada/activa/finalizada)
- [x] Historial de partidos con filtros
- [x] Animaciones de actualización en tiempo real
- [x] Context API para gestión de estado
- [x] Integración con Dashboard
- [x] Detección automática de ganador

### ✅ Sprint 3 - Sistema de Autenticación (COMPLETADO)
- [x] AuthContext con gestión de sesión
- [x] Página de Login funcional
- [x] Página de Registro funcional
- [x] Protección de Rutas (PrivateRoute)
- [x] Navbar con info de usuario
- [x] Persistencia con localStorage
- [x] Preparado para backend

### ✅ Sprint 3.5 - Mejoras Visuales y UX (COMPLETADO)
- [x] Cursor personalizado de paleta de pádel
- [x] Estela animada con partículas
- [x] Fondo de pádel unificado en toda la app
- [x] Glows animados sutiles
- [x] Efectos visuales premium
- [x] Diseño cohesivo en todas las páginas

### 📋 Sprint 4 - Sistema de Confirmación de Resultados
- [ ] CRUD de torneos
- [ ] Asociación torneo → partidos
- [ ] Visualización tipo bracket
- [ ] Estadísticas por torneo

### 📋 Sprint 4 - Dashboard y Estadísticas
- [ ] Dashboard con métricas en tiempo real
- [ ] Gráficos con Recharts
- [ ] Ranking de jugadores
- [ ] Filtros dinámicos

### 📋 Sprint 5 - Autenticación Backend
- [ ] Integración con backend Node.js/FastAPI
- [ ] AuthContext funcional
- [ ] Protección de rutas
- [ ] Gestión de roles (Admin/Jugador)

### 📋 Sprint 6 - Refinamiento y Deploy
- [ ] Optimización de rendimiento
- [ ] Testing (Jest/Vitest)
- [ ] Deploy a producción
- [ ] Documentación final

## 📚 Documentación

### Frontend
- [README_NUEVO.md](frontend/README_NUEVO.md) - Documentación técnica completa
- [INICIO_RAPIDO.md](frontend/INICIO_RAPIDO.md) - Guía de inicio rápido
- [INSTRUCCIONES_MIGRACION.md](frontend/INSTRUCCIONES_MIGRACION.md) - Detalles de migración
- [SPRINT_1_COMPLETADO.md](frontend/SPRINT_1_COMPLETADO.md) - Checklist Sprint 1
- [COMANDOS_WINDOWS.md](frontend/COMANDOS_WINDOWS.md) - Comandos para Windows

### Backend
- [README.md](backend/README.md) - Documentación del backend
- [ALGORITMO_ELO_AVANZADO.md](backend/ALGORITMO_ELO_AVANZADO.md) - Sistema de rating
- [FLUJO_CONFIRMACION_RESULTADOS.md](backend/FLUJO_CONFIRMACION_RESULTADOS.md) - Confirmación de partidos

### General
- [MIGRACION_COMPLETADA.md](MIGRACION_COMPLETADA.md) - Resumen de migración frontend

## 🔌 API Endpoints (Preparados)

```javascript
// Autenticación
POST   /api/auth/login
POST   /api/auth/register
GET    /api/auth/me

// Partidos
GET    /api/partidos
POST   /api/partidos
PUT    /api/partidos/:id
DELETE /api/partidos/:id

// Torneos
GET    /api/torneos
POST   /api/torneos
PUT    /api/torneos/:id
DELETE /api/torneos/:id

// Estadísticas
GET    /api/estadisticas/dashboard
GET    /api/estadisticas/ranking
GET    /api/estadisticas/jugador/:id
```

## 🎯 Alcance Actual

### Implementado ✅
- Sistema de autenticación (mock en frontend)
- Layout principal con navegación
- Componentes UI reutilizables
- Diseño responsive
- Animaciones fluidas
- Estructura de API preparada
- **CRUD completo de Salas/Partidos**
- **Marcador interactivo con animaciones**
- **Sistema de filtros y estadísticas**
- **Context API para gestión de estado**
- **Dashboard con datos en tiempo real**
- **Cursor personalizado de paleta de pádel**
- **Estela animada con partículas**
- **Fondo de pádel unificado**
- **Efectos visuales premium**

### En Desarrollo 🔄
- Sistema de confirmación de resultados
- Sistema de torneos
- Integración backend-frontend
- Sistema de rating Elo
- Gráficos con Recharts

### Futuras Mejoras 📋
- Reservas de cancha y pagos
- Retos y logros (gamificación)
- Evidencia de tanteador (foto)
- Moderación de resultados sospechosos
- Estadísticas avanzadas de juego
- App móvil (React Native)
- PWA (Progressive Web App)

## 🤝 Colaboración

- **Frontend**: Completado Sprint 1, listo para desarrollo continuo
- **Backend**: En desarrollo por colaborador
- **Integración**: Endpoints preparados en ambos lados

## 📞 Soporte

Si encuentras problemas:
1. Revisa la documentación en `/frontend` y `/backend`
2. Consulta los archivos de troubleshooting
3. Verifica que todas las dependencias estén instaladas

## 📄 Licencia

Este proyecto es privado y está en desarrollo.

## 👥 Equipo

- **Frontend**: Desarrollador principal
- **Backend**: Colaborador
- **Diseño**: Paleta PlayT profesional

---

**Estado Actual:** ✅ Sprints 1, 2, 3 y 3.5 Completados | 🔄 Sprint 4 Listo para iniciar  
**Stack:** React 19 + Vite + TailwindCSS + Framer Motion + FastAPI + MySQL  
**Última actualización:** Noviembre 2025  
**Nuevas Features:** Cursor de paleta de pádel + Estela animada + Fondo unificado
