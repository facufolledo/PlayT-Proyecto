# 🚀 Guía de Desarrollo Local - PlayT

## 📋 Requisitos Previos

- **Python 3.8+** (para el backend)
- **Node.js 18+** (para el frontend)
- **Git** (para control de versiones)

## 🔧 Configuración Inicial

### 1. Clonar el Repositorio
```bash
git clone <url-del-repo>
cd PlayRMain
```

### 2. Configurar Backend
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configurar Frontend
```bash
cd frontend
npm install
```

## 🚀 Iniciar en Desarrollo

### Opción 1: Script Automático (Windows)
```bash
# Desde la raíz del proyecto
start-dev.bat
```

### Opción 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🌐 URLs de Desarrollo

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Docs API**: http://localhost:8000/docs

## 📁 Estructura de Archivos

```
PlayRMain/
├── frontend/           # React + TypeScript + Vite
│   ├── src/
│   ├── .env.local     # Configuración local (usa localhost:8000)
│   └── .env           # Configuración producción
├── backend/           # FastAPI + Python
│   ├── main.py       # Servidor principal
│   └── requirements.txt
└── start-dev.bat     # Script de inicio automático
```

## 🔧 Configuración de Entorno

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Backend
- El backend debe ejecutarse en puerto 8000
- CORS configurado para localhost:5173

## 🐛 Solución de Problemas

### Error: "Backend local no disponible"
1. Verifica que el backend esté ejecutándose en puerto 8000
2. Ejecuta: `cd backend && python main.py`
3. Verifica que no haya errores en la consola del backend

### Error: CORS
- Asegúrate de usar `.env.local` para desarrollo
- El backend debe tener CORS configurado para localhost:5173

### Error: Puerto ocupado
```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Matar proceso si es necesario
taskkill /PID <PID> /F
```

## 📱 Navegación Actualizada

El orden de navegación ahora es:
1. **🎮 Todas las Salas** (Prioridad máxima)
2. **🏠 Dashboard**
3. **🏆 Competición**
4. **📊 Rankings**
5. **👤 Cuenta**

## 🔄 Flujo de Desarrollo

1. **Hacer cambios** en frontend o backend
2. **Hot reload** automático en desarrollo
3. **Probar** en http://localhost:5173
4. **Commit** cambios cuando estén listos
5. **Deploy** a producción cuando sea necesario

## 🚀 Deploy a Producción

### Frontend (Hostinger)
```bash
cd frontend
npm run build
# Subir carpeta dist/ a Hostinger
```

### Backend (Railway)
```bash
# Se despliega automáticamente en Railway
```

## 📞 Soporte

Si tienes problemas:
1. Verifica que ambos servidores estén ejecutándose
2. Revisa la consola del navegador para errores
3. Verifica los logs del backend
4. Usa el indicador de estado en la esquina inferior derecha