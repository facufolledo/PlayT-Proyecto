# 📋 Plan de Integración Backend - Sistema de Marcador de Pádel

## 🎯 Objetivo
Integrar el sistema de marcador de pádel del frontend con el backend para persistencia de datos, cálculo de Elo y actualización de rankings.

---

## 📊 FASE 1: Estructura de Base de Datos (Backend)

### 1.1 Actualizar Modelo de Sala
**Archivo**: `backend/src/models/sala.py` o similar

```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from enum import Enum as PyEnum

class EstadoConfirmacion(PyEnum):
    SIN_RESULTADO = "sin_resultado"
    PENDIENTE_CONFIRMACION = "pendiente_confirmacion"
    CONFIRMADO = "confirmado"
    DISPUTADO = "disputado"

class Sala(Base):
    __tablename__ = "salas"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    fecha = Column(DateTime)
    estado = Column(String(20))  # esperando, activa, finalizada, programada
    creador_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Nuevos campos para sistema de pádel
    resultado = Column(JSON, nullable=True)  # ResultadoPartido completo
    estado_confirmacion = Column(Enum(EstadoConfirmacion), default=EstadoConfirmacion.SIN_RESULTADO)
    ganador = Column(String(10), nullable=True)  # equipoA o equipoB
    
    # Relaciones
    creador = relationship("Usuario", back_populates="salas_creadas")
```

### 1.2 Crear Tabla de Confirmaciones
**Archivo**: `backend/src/models/confirmacion.py`

```python
class Confirmacion(Base):
    __tablename__ = "confirmaciones"
    
    id = Column(Integer, primary_key=True)
    sala_id = Column(Integer, ForeignKey('salas.id'))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    tipo = Column(String(20))  # 'confirmacion' o 'reporte'
    fecha = Column(DateTime, default=datetime.utcnow)
    motivo = Column(String(500), nullable=True)  # Solo para reportes
    
    # Relaciones
    sala = relationship("Sala", back_populates="confirmaciones")
    usuario = relationship("Usuario")
```

### 1.3 Actualizar Modelo de Usuario (Elo)
**Archivo**: `backend/src/models/usuario.py`

```python
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    email = Column(String(100), unique=True)
    
    # Sistema de Elo
    elo_rating = Column(Integer, default=1200)
    partidos_jugados = Column(Integer, default=0)
    partidos_ganados = Column(Integer, default=0)
    partidos_perdidos = Column(Integer, default=0)
    
    # Historial de Elo
    historial_elo = relationship("HistorialElo", back_populates="usuario")
```

### 1.4 Crear Tabla de Historial Elo
**Archivo**: `backend/src/models/historial_elo.py`

```python
class HistorialElo(Base):
    __tablename__ = "historial_elo"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    sala_id = Column(Integer, ForeignKey('salas.id'))
    elo_anterior = Column(Integer)
    elo_nuevo = Column(Integer)
    cambio = Column(Integer)  # Puede ser positivo o negativo
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="historial_elo")
    sala = relationship("Sala")
```

---

## 🔧 FASE 2: Endpoints del Backend

### 2.1 Guardar Resultado (Creador)
**Endpoint**: `POST /api/salas/{sala_id}/resultado`

**Request Body**:
```json
{
  "formato": "best_of_3",
  "sets": [
    {
      "gamesEquipoA": 6,
      "gamesEquipoB": 4,
      "ganador": "equipoA",
      "completado": true
    },
    {
      "gamesEquipoA": 4,
      "gamesEquipoB": 6,
      "ganador": "equipoB",
      "completado": true
    }
  ],
  "supertiebreak": {
    "puntosEquipoA": 10,
    "puntosEquipoB": 8,
    "ganador": "equipoA",
    "completado": true
  },
  "ganador": "equipoA",
  "completado": true
}
```

**Lógica**:
1. Verificar que el usuario es el creador
2. Validar el resultado (reglas de pádel)
3. Guardar en BD
4. Cambiar estado a "pendiente_confirmacion"
5. Notificar a los rivales

**Response**:
```json
{
  "success": true,
  "sala": { /* sala actualizada */ },
  "message": "Resultado guardado. Esperando confirmación de rivales."
}
```

### 2.2 Confirmar Resultado (Rival)
**Endpoint**: `POST /api/salas/{sala_id}/confirmar`

**Request Body**:
```json
{
  "usuario_id": 123
}
```

**Lógica**:
1. Verificar que el usuario es parte del partido
2. Verificar que no es el creador
3. Registrar confirmación
4. Si todos confirmaron → calcular Elo
5. Cambiar estado a "confirmado"
6. Actualizar rankings

**Response**:
```json
{
  "success": true,
  "sala": { /* sala actualizada */ },
  "elo_changes": {
    "usuario_123": { "anterior": 1200, "nuevo": 1215, "cambio": +15 },
    "usuario_456": { "anterior": 1180, "nuevo": 1195, "cambio": +15 }
  }
}
```

### 2.3 Reportar Resultado (Rival)
**Endpoint**: `POST /api/salas/{sala_id}/reportar`

**Request Body**:
```json
{
  "usuario_id": 123,
  "motivo": "El resultado no es correcto, ganamos 6-4 6-3"
}
```

**Lógica**:
1. Verificar que el usuario es parte del partido
2. Registrar reporte
3. Cambiar estado a "disputado"
4. Notificar a admin
5. Bloquear cálculo de Elo hasta resolución

**Response**:
```json
{
  "success": true,
  "sala": { /* sala actualizada */ },
  "message": "Reporte registrado. Un administrador revisará el caso."
}
```

### 2.4 Obtener Confirmaciones Pendientes
**Endpoint**: `GET /api/usuarios/{usuario_id}/confirmaciones-pendientes`

**Response**:
```json
{
  "pendientes": [
    {
      "sala_id": 1,
      "nombre": "Partido Amistoso",
      "fecha": "2024-11-20T18:00:00",
      "resultado": { /* resultado cargado */ },
      "creado_por": "Juan Pérez"
    }
  ]
}
```

---

## 🧮 FASE 3: Sistema de Cálculo de Elo

### 3.1 Implementar Algoritmo de Elo
**Archivo**: `backend/src/services/elo_service.py`

```python
class EloService:
    K_FACTOR = 32  # Factor K estándar
    
    @staticmethod
    def calcular_elo_esperado(rating_a: int, rating_b: int) -> float:
        """
        Calcula la probabilidad esperada de victoria
        """
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    @staticmethod
    def calcular_nuevo_elo(
        rating_actual: int,
        rating_oponente: int,
        resultado: float,  # 1 = victoria, 0 = derrota
        k_factor: int = K_FACTOR
    ) -> int:
        """
        Calcula el nuevo rating Elo
        """
        esperado = EloService.calcular_elo_esperado(rating_actual, rating_oponente)
        cambio = k_factor * (resultado - esperado)
        return round(rating_actual + cambio)
    
    @staticmethod
    def calcular_elo_partido(
        equipo_a_ratings: list[int],
        equipo_b_ratings: list[int],
        ganador: str
    ) -> dict:
        """
        Calcula el cambio de Elo para un partido de dobles
        """
        # Promedio de ratings por equipo
        rating_a = sum(equipo_a_ratings) / len(equipo_a_ratings)
        rating_b = sum(equipo_b_ratings) / len(equipo_b_ratings)
        
        # Calcular cambios
        cambios = {}
        
        for i, rating in enumerate(equipo_a_ratings):
            resultado = 1 if ganador == 'equipoA' else 0
            nuevo_elo = EloService.calcular_nuevo_elo(rating, rating_b, resultado)
            cambios[f'jugador_a_{i}'] = {
                'anterior': rating,
                'nuevo': nuevo_elo,
                'cambio': nuevo_elo - rating
            }
        
        for i, rating in enumerate(equipo_b_ratings):
            resultado = 1 if ganador == 'equipoB' else 0
            nuevo_elo = EloService.calcular_nuevo_elo(rating, rating_a, resultado)
            cambios[f'jugador_b_{i}'] = {
                'anterior': rating,
                'nuevo': nuevo_elo,
                'cambio': nuevo_elo - rating
            }
        
        return cambios
```

### 3.2 Aplicar Elo al Confirmar
**Archivo**: `backend/src/controllers/sala_controller.py`

```python
@router.post("/salas/{sala_id}/confirmar")
async def confirmar_resultado(
    sala_id: int,
    data: ConfirmacionRequest,
    db: Session = Depends(get_db)
):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    
    # Registrar confirmación
    confirmacion = Confirmacion(
        sala_id=sala_id,
        usuario_id=data.usuario_id,
        tipo='confirmacion'
    )
    db.add(confirmacion)
    
    # Verificar si todos confirmaron
    confirmaciones = db.query(Confirmacion).filter(
        Confirmacion.sala_id == sala_id,
        Confirmacion.tipo == 'confirmacion'
    ).count()
    
    # Si todos los jugadores confirmaron (4 jugadores)
    if confirmaciones >= 4:
        # Calcular Elo
        equipo_a_ratings = [
            sala.equipoA.jugador1.elo_rating,
            sala.equipoA.jugador2.elo_rating
        ]
        equipo_b_ratings = [
            sala.equipoB.jugador1.elo_rating,
            sala.equipoB.jugador2.elo_rating
        ]
        
        cambios_elo = EloService.calcular_elo_partido(
            equipo_a_ratings,
            equipo_b_ratings,
            sala.ganador
        )
        
        # Aplicar cambios
        for jugador_id, cambio in cambios_elo.items():
            usuario = db.query(Usuario).filter(Usuario.id == jugador_id).first()
            
            # Guardar historial
            historial = HistorialElo(
                usuario_id=usuario.id,
                sala_id=sala_id,
                elo_anterior=cambio['anterior'],
                elo_nuevo=cambio['nuevo'],
                cambio=cambio['cambio']
            )
            db.add(historial)
            
            # Actualizar usuario
            usuario.elo_rating = cambio['nuevo']
            if sala.ganador == 'equipoA' and usuario in [sala.equipoA.jugador1, sala.equipoA.jugador2]:
                usuario.partidos_ganados += 1
            else:
                usuario.partidos_perdidos += 1
            usuario.partidos_jugados += 1
        
        # Cambiar estado
        sala.estado_confirmacion = EstadoConfirmacion.CONFIRMADO
        
    db.commit()
    
    return {
        "success": True,
        "sala": sala,
        "elo_changes": cambios_elo if confirmaciones >= 4 else None
    }
```

---

## 🔗 FASE 4: Integración Frontend

### 4.1 Crear Servicio de API
**Archivo**: `frontend/src/services/resultado.service.ts`

```typescript
import { ResultadoPartido } from '../utils/padelTypes';

class ResultadoService {
  private baseUrl = import.meta.env.VITE_API_URL;

  async guardarResultado(salaId: string, resultado: ResultadoPartido) {
    const token = await this.getToken();
    const response = await fetch(`${this.baseUrl}/salas/${salaId}/resultado`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(resultado)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Error al guardar resultado');
    }

    return response.json();
  }

  async confirmarResultado(salaId: string, usuarioId: string) {
    const token = await this.getToken();
    const response = await fetch(`${this.baseUrl}/salas/${salaId}/confirmar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ usuario_id: usuarioId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Error al confirmar resultado');
    }

    return response.json();
  }

  async reportarResultado(salaId: string, usuarioId: string, motivo: string) {
    const token = await this.getToken();
    const response = await fetch(`${this.baseUrl}/salas/${salaId}/reportar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ usuario_id: usuarioId, motivo })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Error al reportar resultado');
    }

    return response.json();
  }

  async obtenerConfirmacionesPendientes(usuarioId: string) {
    const token = await this.getToken();
    const response = await fetch(
      `${this.baseUrl}/usuarios/${usuarioId}/confirmaciones-pendientes`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Error al obtener confirmaciones pendientes');
    }

    return response.json();
  }

  private async getToken(): Promise<string> {
    // Obtener token de Firebase
    const user = auth.currentUser;
    if (!user) throw new Error('No hay sesión activa');
    return await user.getIdToken();
  }
}

export const resultadoService = new ResultadoService();
```

### 4.2 Actualizar MarcadorPadel
**Archivo**: `frontend/src/components/MarcadorPadel.tsx`

```typescript
import { resultadoService } from '../services/resultado.service';

// En handleGuardarResultado:
const handleGuardarResultado = async () => {
  setError('');
  setLoading(true);

  try {
    // Validaciones...
    
    const resultado: ResultadoPartido = {
      formato,
      sets: sets.filter(s => s.completado),
      supertiebreak: mostrarSupertiebreak ? supertiebreak : undefined,
      ganador,
      completado: true
    };

    // Llamar al backend
    const response = await resultadoService.guardarResultado(sala.id, resultado);
    
    // Actualizar contexto local
    updateSala(sala.id, {
      resultado: response.sala.resultado,
      estadoConfirmacion: 'pendiente_confirmacion',
      ganador
    });

    // Mostrar mensaje de éxito
    alert('Resultado guardado. Esperando confirmación de rivales.');
    onClose();
  } catch (error: any) {
    setError(error.message || 'Error al guardar resultado');
  } finally {
    setLoading(false);
  }
};
```

---

## 📱 FASE 5: Sistema de Notificaciones

### 5.1 Notificaciones Push (Opcional)
**Tecnología**: Firebase Cloud Messaging (FCM)

```typescript
// frontend/src/services/notification.service.ts
class NotificationService {
  async solicitarPermiso() {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      // Registrar token FCM
      const token = await getToken(messaging);
      await this.enviarTokenAlBackend(token);
    }
  }

  async notificarConfirmacionPendiente(usuarioId: string, salaId: string) {
    // Backend envía notificación push
    await fetch(`${API_URL}/notificaciones/confirmar-resultado`, {
      method: 'POST',
      body: JSON.stringify({ usuario_id: usuarioId, sala_id: salaId })
    });
  }
}
```

### 5.2 Notificaciones In-App
**Componente**: Badge en Sidebar

```tsx
// frontend/src/components/Sidebar.tsx
const { confirmacionesPendientes } = useConfirmaciones();

<Link to="/confirmaciones">
  Confirmaciones
  {confirmacionesPendientes > 0 && (
    <span className="badge">{confirmacionesPendientes}</span>
  )}
</Link>
```

---

## 🧪 FASE 6: Testing

### 6.1 Tests Backend
```python
# tests/test_elo_service.py
def test_calcular_elo_victoria():
    rating_actual = 1200
    rating_oponente = 1200
    resultado = 1  # Victoria
    
    nuevo_elo = EloService.calcular_nuevo_elo(rating_actual, rating_oponente, resultado)
    
    assert nuevo_elo == 1216  # +16 puntos

def test_calcular_elo_derrota():
    rating_actual = 1200
    rating_oponente = 1200
    resultado = 0  # Derrota
    
    nuevo_elo = EloService.calcular_nuevo_elo(rating_actual, rating_oponente, resultado)
    
    assert nuevo_elo == 1184  # -16 puntos
```

### 6.2 Tests Frontend
```typescript
// tests/padelValidation.test.ts
describe('Validaciones de Pádel', () => {
  test('Set válido 6-4', () => {
    expect(validarSet(6, 4)).toBe(true);
  });

  test('Set inválido 8-5', () => {
    expect(validarSet(8, 5)).toBe(false);
  });

  test('SuperTiebreak válido 10-8', () => {
    expect(validarSuperTiebreak(10, 8)).toBe(true);
  });
});
```

---

## 📅 CRONOGRAMA DE IMPLEMENTACIÓN

### Semana 1: Backend Base
- [ ] Día 1-2: Actualizar modelos de BD
- [ ] Día 3-4: Crear endpoints básicos
- [ ] Día 5: Testing de endpoints

### Semana 2: Sistema de Elo
- [ ] Día 1-2: Implementar algoritmo de Elo
- [ ] Día 3-4: Integrar con confirmaciones
- [ ] Día 5: Testing de cálculos

### Semana 3: Integración Frontend
- [ ] Día 1-2: Crear servicios de API
- [ ] Día 3-4: Conectar componentes
- [ ] Día 5: Testing end-to-end

### Semana 4: Notificaciones y Pulido
- [ ] Día 1-2: Sistema de notificaciones
- [ ] Día 3-4: Manejo de errores
- [ ] Día 5: Testing final y deployment

---

## ✅ CHECKLIST DE INTEGRACIÓN

### Backend
- [ ] Modelos de BD actualizados
- [ ] Endpoint guardar resultado
- [ ] Endpoint confirmar resultado
- [ ] Endpoint reportar resultado
- [ ] Endpoint confirmaciones pendientes
- [ ] Algoritmo de Elo implementado
- [ ] Historial de Elo
- [ ] Tests unitarios

### Frontend
- [ ] Servicio de API creado
- [ ] MarcadorPadel conectado
- [ ] Confirmaciones conectadas
- [ ] Manejo de errores
- [ ] Loading states
- [ ] Notificaciones
- [ ] Tests de integración

### DevOps
- [ ] Migraciones de BD
- [ ] Variables de entorno
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Monitoring

---

## 🚀 PRÓXIMOS PASOS INMEDIATOS

1. **Crear rama de desarrollo**: `git checkout -b feature/marcador-padel-backend`
2. **Actualizar modelos**: Comenzar con `sala.py`
3. **Crear endpoints**: Empezar con `/resultado`
4. **Testing local**: Probar con Postman/Thunder Client
5. **Integrar frontend**: Conectar servicios
6. **Deploy staging**: Probar en ambiente de pruebas
7. **Deploy producción**: Lanzar feature completa

---

## 📞 NOTAS IMPORTANTES

- **Prioridad Alta**: Endpoints de guardar y confirmar resultado
- **Prioridad Media**: Sistema de Elo y notificaciones
- **Prioridad Baja**: Historial detallado y analytics

- **Seguridad**: Validar siempre que el usuario tiene permisos
- **Performance**: Cachear rankings para evitar recalcular
- **Escalabilidad**: Considerar queue para cálculos de Elo

**Tiempo estimado total**: 3-4 semanas
**Complejidad**: Media-Alta
**Impacto**: Alto (funcionalidad core)
