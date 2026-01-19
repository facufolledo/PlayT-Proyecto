# 🎾 Torneo Weekend - Información Completa

## 📅 Fecha de Creación: 18 de Enero, 2026

---

## 🏆 DATOS DEL TORNEO

**ID**: 24  
**Nombre**: 🎾 Torneo Weekend - 3 Canchas  
**Fechas**: 24-26 Enero 2026 (Viernes a Domingo)  
**Estado**: Inscripción  
**Lugar**: Club Drive+ - Canchas 1, 2 y 3

---

## ⏰ HORARIOS DISPONIBLES

| Día | Horario | Duración |
|-----|---------|----------|
| **Viernes** | 15:00 - 23:59 | 9 horas |
| **Sábado** | 09:00 - 23:59 | 15 horas |
| **Domingo** | 09:00 - 23:59 | 15 horas |
| **TOTAL** | - | **39 horas** |

---

## 🏟️ INFRAESTRUCTURA

- **Canchas**: 3 disponibles
- **Capacidad total**: 117 horas-cancha (39 horas × 3 canchas)
- **Partidos estimados**: ~78 partidos (1.5h promedio por partido)

---

## 📂 CATEGORÍAS (6 categorías)

| Categoría | Género | Parejas |
|-----------|--------|---------|
| 7ma Masculino | Masculino | 12 |
| 6ta Masculino | Masculino | 12 |
| 5ta Masculino | Masculino | 12 |
| 4ta Masculino | Masculino | 12 |
| 7ma Femenino | Femenino | 8 |
| 5ta Femenino | Femenino | 8 |
| **TOTAL** | - | **64 parejas** |

---

## 👥 PARTICIPANTES

- **Parejas**: 64
- **Jugadores**: 128
- **Usuarios creados**: IDs desde 3000 en adelante

---

## 🚫 RESTRICCIONES HORARIAS

### Distribución General
- ✅ **Sin restricciones**: 21 parejas (32.8%)
- 🚫 **Con restricciones**: 43 parejas (67.2%)

### Restricciones por Día
| Día | Parejas con Restricción |
|-----|------------------------|
| Viernes | 15 parejas |
| Sábado | 16 parejas |
| Domingo | 25 parejas |

### Tipos de Restricciones Implementadas

1. **Sin restricciones (30%)**
   - Disponibles todo el fin de semana

2. **Restricciones viernes (30%)**
   - No puede viernes 15:00-19:00 (tarde)
   - No puede viernes 20:00-23:59 (noche)

3. **Restricciones sábado (20%)**
   - No puede sábado 09:00-13:00 (mañana)
   - No puede sábado 19:00-23:59 (noche)

4. **Restricciones domingo (10%)**
   - No puede domingo 09:00-13:00 (mañana)
   - No puede domingo 18:00-23:59 (tarde)

5. **Restricciones múltiples (10%)**
   - Combinaciones de 2 restricciones en diferentes días

---

## 📊 ANÁLISIS DE CAPACIDAD

### Horas-Cancha Disponibles
```
Viernes:  9h × 3 canchas = 27 horas-cancha
Sábado:  15h × 3 canchas = 45 horas-cancha
Domingo: 15h × 3 canchas = 45 horas-cancha
─────────────────────────────────────────
TOTAL:                    117 horas-cancha
```

### Partidos Estimados
- **Duración promedio**: 1.5 horas por partido
- **Capacidad**: ~78 partidos
- **Necesarios**: ~224 partidos (estimado)
- **Estado**: ⚠️ Capacidad ajustada (requiere optimización)

### Nota sobre Capacidad
El sistema está diseñado para optimizar la programación:
- Fase de grupos con menos partidos por pareja
- Playoffs solo para clasificados
- Distribución inteligente según restricciones
- Uso eficiente de las 3 canchas

---

## 🧪 PRÓXIMOS PASOS

### 1. Generar Zonas
```bash
# Desde Python
python -c "from src.services.torneo_zona_service import TorneoZonaService; TorneoZonaService().generar_zonas_automaticas(24)"

# O desde el frontend
POST /torneos/24/zonas/generar
```

### 2. Generar Fixture Global
```bash
# Desde el frontend
POST /torneos/24/fixture/generar
```

### 3. Verificar Restricciones
- Revisar que los partidos respeten las restricciones horarias
- Confirmar que no hay conflictos de horarios
- Verificar distribución en las 3 canchas

### 4. Verificar Distribución
- Confirmar que los partidos se distribuyen equitativamente
- Verificar que se aprovechan las 3 canchas
- Revisar que los horarios son realistas

---

## 📝 SCRIPTS DISPONIBLES

### Crear Torneo
```bash
python backend/crear_torneo_con_horarios.py
```

### Verificar Torneo
```bash
python backend/verificar_torneo_weekend.py
```

---

## 🎯 CARACTERÍSTICAS ESPECIALES

### Sistema de Restricciones
- ✅ Restricciones por día y horario
- ✅ Múltiples restricciones por pareja
- ✅ Validación automática en fixture
- ✅ Optimización de horarios

### Sistema de Horarios
- ✅ Horarios diferentes por día
- ✅ Viernes tarde (15:00-23:59)
- ✅ Fin de semana completo (09:00-23:59)
- ✅ 3 canchas simultáneas

### Optimizaciones
- ✅ Distribución inteligente de partidos
- ✅ Respeto de restricciones horarias
- ✅ Uso eficiente de canchas
- ✅ Minimización de tiempos muertos

---

## 🔗 ACCESO

**URL Frontend**: https://drive-plus.com.ar/torneos/24  
**API Endpoint**: https://drive-plus-production.up.railway.app/torneos/24

---

## ⚠️ NOTAS IMPORTANTES

1. **Capacidad Ajustada**: El torneo tiene más parejas de las que la capacidad estricta permite. El sistema optimizará:
   - Reduciendo partidos en fase de grupos
   - Usando formato de eliminación directa en algunas categorías
   - Distribuyendo eficientemente en 3 canchas

2. **Restricciones Realistas**: Las restricciones simulan casos reales:
   - Trabajo (no disponible viernes tarde)
   - Familia (no disponible noches)
   - Compromisos (no disponible mañanas)

3. **Testing Completo**: Este torneo permite probar:
   - Sistema de horarios con 3 canchas
   - Restricciones variadas
   - Optimización de fixture
   - Distribución de partidos

---

## 📞 SOPORTE

**Documentación**:
- `backend/crear_torneo_con_horarios.py` - Script de creación
- `backend/verificar_torneo_weekend.py` - Script de verificación
- `TORNEO_WEEKEND_INFO.md` - Este documento

---

**Estado**: ✅ CREADO Y LISTO PARA TESTING  
**Fecha**: 18 de Enero, 2026  
**Próximo paso**: 🎯 Generar zonas y fixture
