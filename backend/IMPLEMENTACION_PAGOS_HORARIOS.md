# Implementación: Sistema de Pagos y Franjas Horarias

## 📋 Resumen de Cambios

### 1. **Sistema de Pagos con QR (Mercado Pago)**

#### Nuevos campos en `torneos_parejas`:
- `pago_estado`: Estado del pago (pendiente, pagado, verificado, rechazado, reembolsado)
- `pago_monto`: Monto a pagar
- `pago_comprobante_url`: URL del comprobante subido
- `pago_mercadopago_id`: ID de transacción de Mercado Pago
- `pago_qr_data`: Datos del QR generado
- `pago_fecha_acreditacion`: Fecha de acreditación del pago
- `pago_verificado_por`: ID del organizador que verificó
- `motivo_rechazo_pago`: Motivo si se rechaza el pago

#### Nuevos campos en `torneos`:
- `monto_inscripcion`: Monto de inscripción del torneo
- `requiere_pago`: Boolean para activar/desactivar pagos
- `mercadopago_access_token`: Token de acceso de Mercado Pago
- `mercadopago_public_key`: Public key de Mercado Pago

### 2. **Franjas Horarias**

#### Nuevos campos en `torneos_parejas`:
- `disponibilidad_lunes` a `disponibilidad_domingo`: Franjas horarias por día
- Valores posibles: `'manana'` (8-10), `'tarde'` (17-21), `'todo_el_dia'`, `'no_disponible'`
- Sábado y domingo por defecto: `'todo_el_dia'`

### 3. **Cambio de Compañero**

#### Nuevos campos en `torneos_parejas`:
- `jugador2_anterior_id`: ID del jugador2 anterior
- `fecha_cambio_jugador2`: Fecha del cambio
- `motivo_cambio`: Motivo del cambio

### 4. **Historial de Pagos**

Nueva tabla `torneos_pagos_historial` para auditoría:
- Registra todos los cambios de estado de pago
- Incluye quién hizo el cambio y cuándo

## 🔧 Endpoints a Implementar

### **Gestión de Pagos**

```python
# 1. Generar QR de pago (después de confirmar pareja)
POST /torneos/{torneo_id}/parejas/{pareja_id}/generar-qr
Response: { qr_data, monto, mercadopago_id }

# 2. Subir comprobante de pago
POST /torneos/{torneo_id}/parejas/{pareja_id}/subir-comprobante
Body: { comprobante_url }

# 3. Verificar pago (organizador)
PATCH /torneos/{torneo_id}/parejas/{pareja_id}/verificar-pago
Body: { aprobado: boolean, motivo_rechazo?: string }

# 4. Solicitar reembolso
POST /torneos/{torneo_id}/parejas/{pareja_id}/solicitar-reembolso
Body: { motivo }
```

### **Gestión de Compañero**

```python
# 5. Cambiar compañero (después de rechazo)
PATCH /torneos/{torneo_id}/parejas/{pareja_id}/cambiar-companero
Body: { nuevo_jugador2_id, motivo }

# 6. Cancelar inscripción
DELETE /torneos/{torneo_id}/parejas/{pareja_id}/cancelar
Response: { mensaje: "Inscripción cancelada, comunícate con el organizador..." }
```

### **Franjas Horarias**

```python
# 7. Actualizar disponibilidad horaria
PATCH /torneos/{torneo_id}/parejas/{pareja_id}/disponibilidad
Body: {
  disponibilidad_lunes: 'manana',
  disponibilidad_martes: 'tarde',
  disponibilidad_jueves: 'tarde',
  disponibilidad_viernes: 'tarde'
}

# 8. Obtener disponibilidad de parejas (para programación)
GET /torneos/{torneo_id}/disponibilidad-parejas
Response: [ { pareja_id, disponibilidad_por_dia } ]
```

## 📱 Flujo de Usuario

### **Flujo de Inscripción Completo:**

1. **Jugador 1 se inscribe y elige compañero**
   - Selecciona jugador2
   - Selecciona franjas horarias disponibles
   - Se envía invitación a jugador2

2. **Jugador 2 responde:**
   
   **Opción A: Acepta**
   - Se genera QR de Mercado Pago
   - Ambos jugadores ven el QR y monto
   - Pueden pagar y subir comprobante
   
   **Opción B: Rechaza**
   - Jugador 1 recibe notificación
   - Puede elegir:
     - Cambiar de compañero (vuelve al paso 1)
     - Cancelar inscripción (mensaje de reembolso)

3. **Después del pago:**
   - Organizador revisa comprobante
   - Aprueba o rechaza
   - Si aprueba: pareja queda confirmada
   - Si rechaza: pareja queda pendiente, puede reintentar pago

4. **Programación de partidos:**
   - Sistema considera franjas horarias
   - Jueves/Viernes: solo franjas seleccionadas
   - Sábado/Domingo: todo el día disponible

## 🎨 Mensajes para Frontend

```javascript
// Mensaje al cancelar inscripción
"Inscripción cancelada. Por favor, comunícate con el organizador del torneo para coordinar la devolución del dinero."

// Aviso de franjas horarias
"⏰ Disponibilidad Horaria:
- Jueves y Viernes: Selecciona tus franjas disponibles (Mañana 8-10hs o Tarde 17-21hs)
- Sábado y Domingo: Disponible todo el día automáticamente"

// Estado de pago pendiente
"⏳ Pago pendiente de verificación por el organizador"

// Pago rechazado
"❌ Pago rechazado: {motivo}. Por favor, vuelve a intentar el pago."

// Pago verificado
"✅ Pago verificado. Tu inscripción está confirmada."
```

## 🔐 Permisos

- **Jugadores**: Pueden cambiar compañero, cancelar, subir comprobante
- **Organizadores**: Pueden verificar pagos, eliminar parejas, ver historial
- **Sistema**: Genera QR automáticamente después de confirmación

## 📊 Estados de Pareja

```
pendiente → (jugador2 acepta) → confirmada → (pago) → pagado → (verificación) → verificado
                ↓
          (jugador2 rechaza) → cambiar_companero o cancelar
```

## 🚀 Próximos Pasos

1. ✅ Migración SQL ejecutada
2. ✅ Modelos actualizados
3. ⏳ Implementar endpoints de pago
4. ⏳ Implementar endpoints de cambio de compañero
5. ⏳ Implementar endpoints de franjas horarias
6. ⏳ Integrar con Mercado Pago API
7. ⏳ Actualizar frontend con nuevos flujos

## 📝 Notas de Implementación

- Los QR de Mercado Pago se generan usando su API oficial
- Los comprobantes se suben a Firebase Storage
- El historial de pagos permite auditoría completa
- Las franjas horarias se validan en el backend
- Los reembolsos se gestionan manualmente por el organizador
