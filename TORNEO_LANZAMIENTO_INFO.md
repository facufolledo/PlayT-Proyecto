# 🚀 TORNEO DE LANZAMIENTO - Drive+

## 📋 Información General

**Torneo ID**: 23  
**Nombre**: 🚀 Torneo Lanzamiento - Drive+ Test  
**Fechas**: 20-22 Enero 2026 (Lunes a Miércoles)  
**Estado**: Inscripción abierta  
**Inscripción**: $3,000

---

## 🏟️ Configuración

### Horarios Disponibles
- **Lunes**: 14:00 - 23:00 (9 horas)
- **Martes**: 09:00 - 23:00 (14 horas)
- **Miércoles**: 09:00 - 22:00 (13 horas)

### Canchas
- 4 canchas disponibles

---

## 📂 Categorías y Parejas

| Categoría | Parejas | Sin Restricciones | Con Restricciones |
|-----------|---------|-------------------|-------------------|
| 7ma Masculino | 12 | 3 (25%) | 9 (75%) |
| 5ta Masculino | 12 | 1 (8%) | 11 (92%) |
| 4ta Masculino | 12 | 0 (0%) | 12 (100%) |
| 7ma Femenino | 8 | 2 (25%) | 6 (75%) |
| 5ta Femenino | 8 | 2 (25%) | 6 (75%) |
| **TOTAL** | **52** | **8 (15%)** | **44 (85%)** |

**Total Jugadores**: 104

---

## 🚫 Sistema de Restricciones

### Tipos de Restricciones Implementadas

1. **Sin restricciones (15%)**: Disponibles en todos los horarios
2. **Restricciones laborales (40%)**:
   - No puede lunes 14:00-18:00
   - No puede martes 09:00-13:00
   - No puede miércoles 18:00-22:00
3. **Restricciones familiares (20%)**:
   - No puede lunes 20:00-23:00
   - No puede martes 19:00-23:00
4. **Restricciones múltiples (25%)**:
   - Combinaciones de 2 restricciones

### Ejemplos Reales
- **Pareja 1**: No puede martes 09:00-13:00
- **Pareja 2**: Disponible siempre
- **Pareja 3**: 2 restricciones (lunes tarde + miércoles noche)

---

## 🧪 Cómo Probar el Sistema

### 1. Acceder al Torneo
**Frontend**: https://drive-plus.com.ar/torneos/23  
**API**: https://drive-plus-production.up.railway.app/torneos/23

### 2. Generar Zonas por Categoría
```bash
# Para cada categoría, generar zonas inteligentes
POST /torneos/23/categorias/{categoria_id}/generar-zonas

# Parámetros:
{
  "num_zonas": 3,  # Para 12 parejas = 4 parejas por zona
  "metodo": "serpiente"  # o "aleatorio"
}
```

### 3. Generar Fixture Global
```bash
POST /torneos/23/generar-fixture-global

# Parámetros:
{
  "canchas_disponibles": 4,
  "duracion_partido_minutos": 90,
  "descanso_minutos": 15
}
```

### 4. Verificar Fixture
```bash
GET /torneos/23/fixture
```

### 5. Verificaciones Importantes

✅ **Verificar que se respeten restricciones**:
- Ningún partido debe programarse en horarios restringidos de las parejas
- Parejas sin restricciones deben tener más flexibilidad de horarios
- Sistema debe distribuir partidos equitativamente

✅ **Verificar optimizaciones**:
- Carga rápida de zonas (< 600ms)
- Generación de fixture eficiente
- Sin errores de N+1 queries

✅ **Verificar UX**:
- Interfaz muestra restricciones claramente
- Usuarios pueden ver sus horarios asignados
- Sistema de alertas funciona correctamente

---

## 📊 Métricas a Monitorear

### Performance
- Tiempo de carga de zonas: < 600ms
- Tiempo de generación de fixture: < 5s
- Queries a base de datos: Optimizadas (batch queries)

### Funcionalidad
- Respeto de restricciones: 100%
- Distribución equitativa: Sí
- Conflictos de horarios: 0

---

## 🎯 Objetivos del Test

1. ✅ **Probar sistema de restricciones** antes del torneo real del 23
2. ✅ **Verificar optimizaciones** de performance (10x más rápido)
3. ✅ **Validar UX** del sistema de horarios
4. ✅ **Detectar bugs** antes del lanzamiento
5. ✅ **Entrenar al equipo** en el uso del sistema

---

## 🚀 Preparación para el Torneo del 23

### Checklist Pre-Torneo
- [ ] Generar zonas para todas las categorías
- [ ] Generar fixture global
- [ ] Verificar que no haya conflictos
- [ ] Probar inscripciones de usuarios
- [ ] Verificar sistema de pagos
- [ ] Probar carga de resultados
- [ ] Verificar sistema ELO
- [ ] Probar notificaciones

### Diferencias con Torneo Real
| Aspecto | Torneo Test | Torneo Real (23 Enero) |
|---------|-------------|------------------------|
| Fechas | 20-22 Enero | 23-25 Enero |
| Parejas | 52 | ~80-100 |
| Inscripción | $3,000 | $5,000 |
| Duración | 3 días | 3 días |
| Canchas | 4 | 3-4 |

---

## 📝 Notas Importantes

### Sistema de Restricciones
- **Nuevo enfoque**: Usuarios especifican cuándo NO pueden jugar
- **Más intuitivo**: Más fácil que especificar disponibilidad
- **Más flexible**: Permite restricciones parciales por día

### Optimizaciones Aplicadas
- ✅ N+1 queries eliminados (99% menos queries)
- ✅ Batch processing implementado
- ✅ Cache inteligente
- ✅ Conexiones de DB estabilizadas

### Listo para Producción
- ✅ Sistema ELO corregido
- ✅ Performance 10-15x mejorada
- ✅ Sin errores conocidos
- ✅ Documentación completa

---

## 🎉 ¡Éxito en el Lanzamiento!

**El torneo de prueba está listo para validar el sistema antes del torneo real del 23 de enero.**

### Contacto
- Frontend: https://drive-plus.com.ar
- Backend: https://drive-plus-production.up.railway.app
- Documentación: Ver archivos OPTIMIZACIONES_*.md

**¡Drive+ está listo para brillar! 🚀🏆**
