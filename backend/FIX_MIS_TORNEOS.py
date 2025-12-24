# SOLUCIÓN Error 422 en /torneos/mis-torneos

# El error 422 indica "Unprocessable Content" - problema de validación

# OPCIÓN 1: Verificar el endpoint actual
@app.get("/torneos/mis-torneos")
async def get_mis_torneos(current_user = Depends(get_current_user)):
    """
    VERIFICAR que el endpoint no requiera parámetros adicionales
    que no se están enviando desde el frontend
    """
    try:
        # Tu código actual aquí
        pass
    except Exception as e:
        print(f"Error en mis-torneos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# OPCIÓN 2: Si requiere parámetros, hacerlos opcionales
@app.get("/torneos/mis-torneos")
async def get_mis_torneos(
    limit: int = Query(50, ge=1, le=100),  # Parámetro opcional
    offset: int = Query(0, ge=0),          # Parámetro opcional
    estado: str = Query(None),             # Parámetro opcional
    current_user = Depends(get_current_user)
):
    """Obtener torneos del usuario con parámetros opcionales"""
    try:
        query = """
        SELECT t.*, 
               COUNT(tp.id_usuario) as participantes
        FROM torneos t
        LEFT JOIN torneo_participantes tp ON t.id = tp.id_torneo
        WHERE t.organizador_id = %s OR tp.id_usuario = %s
        """
        
        params = [current_user.id_usuario, current_user.id_usuario]
        
        if estado:
            query += " AND t.estado = %s"
            params.append(estado)
            
        query += " GROUP BY t.id ORDER BY t.fecha_inicio DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        result = await database.fetch_all(query, params)
        return result
        
    except Exception as e:
        print(f"❌ Error en mis-torneos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# OPCIÓN 3: Endpoint simplificado sin parámetros
@app.get("/torneos/mis-torneos-simple")
async def get_mis_torneos_simple(current_user = Depends(get_current_user)):
    """Versión simplificada sin parámetros"""
    try:
        query = """
        SELECT t.id, t.nombre, t.estado, t.fecha_inicio, t.fecha_fin
        FROM torneos t
        LEFT JOIN torneo_participantes tp ON t.id = tp.id_torneo
        WHERE t.organizador_id = %s OR tp.id_usuario = %s
        GROUP BY t.id, t.nombre, t.estado, t.fecha_inicio, t.fecha_fin
        ORDER BY t.fecha_inicio DESC
        LIMIT 50
        """
        
        result = await database.fetch_all(query, [
            current_user.id_usuario, 
            current_user.id_usuario
        ])
        
        return result
        
    except Exception as e:
        print(f"❌ Error en mis-torneos-simple: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

print("✅ Soluciones para error 422 en /torneos/mis-torneos preparadas")