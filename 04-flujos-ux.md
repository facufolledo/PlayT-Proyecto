#Flujos de Usuario

## Flujo A: Crear → Jugar → Reportar → Confirmar
1. Crear partido (club, fecha, modalidad, jugadores).
2. Jugar.
3. Reportar resultado (sets).
4. Confirmación rival:
   - ✅ Si confirma → estado = confirmado → recalcular rating.
   - ❌ Si rechaza → vuelve a “pendiente”.
   - ⏰ Si no responde en 24h → pendiente (en futuro: auto-confirmar si doble reporte igual).

## Flujo B: Ranking
1. Ver top jugadores.
2. Tap en jugador → historial rating y perfil con estadisticas..

## Estados de partido
- `pendiente` → `reportado` → `confirmado`
- (opcional: `cancelado`)
