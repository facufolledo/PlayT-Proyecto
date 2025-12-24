# SOLUCIÓN Error HistorialEnfrentamiento.id_sala

# Error: type object 'HistorialEnfrentamiento' has no attribute 'id_sala'

# OPCIÓN 1: Verificar el modelo HistorialEnfrentamiento
class HistorialEnfrentamiento(BaseModel):
    id: int
    # id_sala: int  # ← Este campo puede estar faltando
    jugador1_id: int
    jugador2_id: int
    fecha: datetime
    # Agregar otros campos necesarios

# OPCIÓN 2: Si el modelo no tiene id_sala, ajustar la query
# BUSCAR en el código donde se usa HistorialEnfrentamiento.id_sala

# Ejemplo de query problemática:
# DELETE FROM historial_enfrentamientos WHERE id_sala = %s

# SOLUCIÓN A: Si la tabla SÍ tiene id_sala
def eliminar_sala_con_historial(sala_id: int):
    """Eliminar sala y su historial"""
    try:
        # Primero eliminar historial
        query_historial = """
        DELETE FROM historial_enfrentamientos 
        WHERE id_sala = %s
        """
        
        # Luego eliminar sala
        query_sala = """
        DELETE FROM salas 
        WHERE id = %s
        """
        
        # Ejecutar en transacción
        await database.execute(query_historial, [sala_id])
        await database.execute(query_sala, [sala_id])
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"❌ Error eliminando sala: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# SOLUCIÓN B: Si la tabla NO tiene id_sala, usar otra relación
def eliminar_sala_sin_id_sala(sala_id: int):
    """Eliminar sala cuando historial no tiene id_sala"""
    try:
        # Opción 1: Eliminar por fecha o rango
        query_historial = """
        DELETE FROM historial_enfrentamientos 
        WHERE fecha >= (SELECT fecha_creacion FROM salas WHERE id = %s)
        AND fecha <= (SELECT fecha_creacion FROM salas WHERE id = %s) + INTERVAL '1 day'
        """
        
        # Opción 2: Eliminar por jugadores de la sala
        query_historial_alt = """
        DELETE FROM historial_enfrentamientos 
        WHERE (jugador1_id IN (SELECT jugador_id FROM sala_jugadores WHERE sala_id = %s)
           OR jugador2_id IN (SELECT jugador_id FROM sala_jugadores WHERE sala_id = %s))
        """
        
        # Opción 3: No eliminar historial, solo la sala
        query_solo_sala = """
        DELETE FROM salas WHERE id = %s
        """
        
        # Usar la opción más segura
        await database.execute(query_solo_sala, [sala_id])
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"❌ Error eliminando sala: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# SOLUCIÓN C: Verificar estructura de tabla
async def verificar_estructura_historial():
    """Verificar qué campos tiene la tabla historial_enfrentamientos"""
    try:
        query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'historial_enfrentamientos'
        ORDER BY ordinal_position
        """
        
        columns = await database.fetch_all(query)
        print("📋 Estructura de historial_enfrentamientos:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
            
        return columns
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return []

# SOLUCIÓN D: Endpoint para verificar y arreglar
@app.get("/debug/historial-estructura")
async def debug_historial_estructura():
    """Endpoint para verificar estructura de historial_enfrentamientos"""
    try:
        columns = await verificar_estructura_historial()
        
        tiene_id_sala = any(col['column_name'] == 'id_sala' for col in columns)
        
        return {
            "tiene_id_sala": tiene_id_sala,
            "columnas": [col['column_name'] for col in columns],
            "solucion": "usar_id_sala" if tiene_id_sala else "usar_alternativa"
        }
        
    except Exception as e:
        return {"error": str(e)}

print("✅ Soluciones para error HistorialEnfrentamiento.id_sala preparadas")