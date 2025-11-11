# PlayT Backend API 🎾

Backend de la aplicación PlayT, un sistema de pádel con ranking dinámico basado en el algoritmo Elo.

## 🚀 Características

- **FastAPI**: API moderna y rápida con documentación automática
- **PostgreSQL**: Base de datos robusta con Neon
- **SQLAlchemy**: ORM para Python
- **Algoritmo Elo**: Sistema de rating dinámico para jugadores
- **JWT**: Autenticación segura
- **CORS**: Soporte para aplicaciones web y móviles

## 🛠️ Tecnologías

- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL (Neon)
- Alembic (migraciones)
- Pydantic (validación)
- JWT (autenticación)

## 📋 Requisitos

- Python 3.8 o superior
- PostgreSQL (recomendado Neon)
- pip

## 🔧 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Copiar el template
   cp env.template .env
   
   # Editar .env con tus credenciales
   nano .env
   ```

5. **Configurar base de datos**
   - Crear base de datos en Neon
   - Actualizar `DATABASE_URL` en `.env`

## 🚀 Ejecución

### Desarrollo
```bash
python main.py
```

### Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Endpoints Disponibles

- `GET /` - Información de la API
- `GET /health` - Estado del servicio
- `GET /docs` - Documentación interactiva (Swagger)
- `GET /redoc` - Documentación alternativa

## 🗄️ Estructura de la Base de Datos

### Tablas Principales

- **users**: Jugadores del sistema
- **matches**: Partidos de pádel
- **elo_history**: Historial de cambios de rating

### Modelos

- **User**: Información del jugador y estadísticas
- **Match**: Detalles del partido y resultados
- **EloHistory**: Seguimiento de cambios de rating

## 🎯 Algoritmo Elo

El sistema implementa el algoritmo Elo con:

- **Rating inicial**: 1200
- **Factor K**: 32 (ajustable por experiencia)
- **Categorías**: Novice, Beginner, Intermediate, Advanced, Expert, Master, International Master, Grand Master

## 🔐 Autenticación

- JWT tokens
- Expiración configurable
- Middleware de seguridad
- Hashing de contraseñas con bcrypt

## 📊 Estadísticas

- Rating Elo dinámico
- Historial de partidos
- Porcentaje de victorias
- Progreso del jugador

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=src
```

## 📝 Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@host:port/db

# Seguridad
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Elo
INITIAL_ELO_RATING=1200
K_FACTOR=32
```

## 🚀 Despliegue

### Railway/Render
1. Conectar repositorio
2. Configurar variables de entorno
3. Deploy automático

### Docker
```bash
docker build -t playt-backend .
docker run -p 8000:8000 playt-backend
```

## 📈 Monitoreo

- Health checks automáticos
- Logs estructurados
- Métricas de rendimiento
- Documentación automática

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🆘 Soporte

- Documentación: `/docs`
- Issues: GitHub Issues
- Email: [tu-email@ejemplo.com]

---

**PlayT** - Transformando el pádel amateur 🎾
