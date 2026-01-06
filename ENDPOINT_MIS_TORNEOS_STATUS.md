# 📊 Estado del Endpoint `/torneos/mis-torneos`

## ✅ PROBLEMA IDENTIFICADO Y SOLUCIONADO

**Error 422 (Unprocessable Content)** - **CAUSA ENCONTRADA:**

### 🐛 **Error en el filtro de estados**

El endpoint estaba filtrando por estados que no existen en el enum:

```python
# ❌ INCORRECTO (causaba error 422)
TorneoPareja.estado.in_(['pendiente', 'inscripta', 'confirmada'])

# ✅ CORRECTO (estados que existen en EstadoPareja enum)
TorneoPareja.estado.in_(['inscripta', 'confirmada'])
```

### 📋 **Estados válidos en EstadoPareja enum:**
- `INSCRIPTA = "inscripta"`
- `CONFIRMADA = "confirmada"`  
- `BAJA = "baja"`

**El estado `'pendiente'` NO EXISTE en el enum**, por eso daba error 422.

## 🔧 SOLUCIÓN APLICADA

### ✅ Corregido en `torneo_controller.py` línea 584:
```python
parejas = db.query(TorneoPareja).filter(
    or_(
        TorneoPareja.jugador1_id == current_user.id_usuario,
        TorneoPareja.jugador2_id == current_user.id_usuario
    ),
    TorneoPareja.estado.in_(['inscripta', 'confirmada'])  # Removido 'pendiente'
).all()
```

### ✅ Corregido en `torneo_inscripcion_controller.py`:
```python
TorneoPareja.estado.in_(['inscripta', 'confirmada'])  # Removido 'pendiente'
```

## � RESULITADO ESPERADO

Ahora el endpoint debe funcionar correctamente y retornar:

```json
{
  "torneos": [
    {
      "id": 1,
      "nombre": "Torneo de Prueba",
      "descripcion": "Descripción del torneo",
      "tipo": "eliminacion_directa",
      "categoria": "Libre",
      "genero": "masculino",
      "estado": "inscripcion",
      "fecha_inicio": "2024-01-15T00:00:00",
      "fecha_fin": "2024-01-16T00:00:00",
      "lugar": "Club de Pádel",
      "mi_inscripcion": {
        "pareja_id": 123,
        "estado_inscripcion": "confirmada",
        "categoria_id": 1
      }
    }
  ]
}
```

## 🚀 PRÓXIMOS PASOS

1. **Aplicar los cambios en Railway** (redeploy)
2. **Probar el endpoint** - debería funcionar sin error 422
3. **Verificar que el frontend recibe los datos correctamente**

## 📝 NOTA TÉCNICA

Este error es común cuando hay inconsistencias entre:
- Definiciones de enum en el código
- Valores reales en la base de datos  
- Filtros en las queries

**Siempre verificar que los valores usados en filtros coincidan con los definidos en los enums.**