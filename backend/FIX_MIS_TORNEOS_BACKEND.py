# SOLUCIÓN BACKEND: Arreglar endpoint /torneos/mis-torneos

# El frontend llama: GET /torneos/mis-torneos (sin parámetros)
# El backend responde: 422 Unprocessable Content

# PROBLEMA: El endpoint actual probablemente requiere parámetros que no se envían
# SOLUCIÓN: Hacer que el endpoint funcione sin parámetros obligatorios

@app.get("/torneos/mis-torneos")
async def get_mis_torneos(
    # Hacer TODOS los parámetros opcionales
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    current_user = Depends(get_current_user)
):
    """
    Obtener torneos del usuario actual
    - Como organizador
    - Como participante
    """
    try:
        # Query base para obtener torneos donde el usuario participa
        query = """
        SELECT DISTINCT
            t.id,
            t.nombre,
            t.descripcion,
            t.categoria,
            t.genero,
            t.estado,
            t.fecha_inicio,
            t.fecha_fin,
            t.lugar,
            t.organizador_id,
            -- Información de inscripción del usuario
            CASE 
                WHEN tp.id IS NOT NULL THEN tp.id
                ELSE NULL 
            END as pareja_id,
            CASE 
                WHEN tp.estado IS NOT NULL THEN tp.estado
                WHEN t.organizador_id = %s THEN 'organizador'
                ELSE NULL 
            END as estado_inscripcion,
            tp.categoria_id
        FROM torneos t
        LEFT JOIN torneo_participantes tp ON (
            t.id = tp.id_torneo AND 
            (tp.jugador1_id = %s OR tp.jugador2_id = %s)
        )
        WHERE (
            t.organizador_id = %s OR  -- Torneos que organiza
            tp.id IS NOT NULL         -- Torneos donde participa
        )
        """
        
        params = [
            current_user.id_usuario,  # Para CASE WHEN organizador
            current_user.id_usuario,  # Para jugador1_id
            current_user.id_usuario,  # Para jugador2_id  
            current_user.id_usuario   # Para WHERE organizador
        ]
        
        # Agregar filtro de estado si se proporciona
        if estado:
            query += " AND t.estado = %s"
            params.append(estado)
            
        # Ordenar y paginar
        query += """
        ORDER BY t.fecha_inicio DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        # Ejecutar query
        torneos_raw = await database.fetch_all(query, params)
        
        # Formatear respuesta según lo que espera el frontend
        torneos = []
        for torneo in torneos_raw:
            torneo_data = {
                "id": torneo["id"],
                "nombre": torneo["nombre"],
                "descripcion": torneo["descripcion"] or "",
                "categoria": torneo["categoria"] or "",
                "genero": torneo["genero"] or "",
                "estado": torneo["estado"],
                "fecha_inicio": torneo["fecha_inicio"].isoformat() if torneo["fecha_inicio"] else "",
                "fecha_fin": torneo["fecha_fin"].isoformat() if torneo["fecha_fin"] else "",
                "lugar": torneo["lugar"] or "",
                "mi_inscripcion": {
                    "pareja_id": torneo["pareja_id"] or 0,
                    "estado_inscripcion": torneo["estado_inscripcion"] or "no_inscrito",
                    "categoria_id": torneo["categoria_id"]
                }
            }
            torneos.append(torneo_data)
        
        # Respuesta en el formato que espera el frontend
        return {
            "torneos": torneos
        }
        
    except Exception as e:
        print(f"❌ Error en /torneos/mis-torneos: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno del servidor: {str(e)}"
        )

# ALTERNATIVA SIMPLE si la query de arriba es muy compleja:
@app.get("/torneos/mis-torneos-simple")
async def get_mis_torneos_simple(current_user = Depends(get_current_user)):
    """Versión simplificada que siempre funciona"""
    try:
        # Query más simple - solo torneos donde es organizador
        query_organizador = """
        SELECT id, nombre, descripcion, categoria, genero, estado, 
               fecha_inicio, fecha_fin, lugar
        FROM torneos 
        WHERE organizador_id = %s
        ORDER BY fecha_inicio DESC
        LIMIT 50
        """
        
        torneos_organizador = await database.fetch_all(query_organizador, [current_user.id_usuario])
        
        # Formatear respuesta
        torneos = []
        for torneo in torneos_organizador:
            torneo_data = {
                "id": torneo["id"],
                "nombre": torneo["nombre"],
                "descripcion": torneo["descripcion"] or "",
                "categoria": torneo["categoria"] or "",
                "genero": torneo["genero"] or "",
                "estado": torneo["estado"],
                "fecha_inicio": torneo["fecha_inicio"].isoformat() if torneo["fecha_inicio"] else "",
                "fecha_fin": torneo["fecha_fin"].isoformat() if torneo["fecha_fin"] else "",
                "lugar": torneo["lugar"] or "",
                "mi_inscripcion": {
                    "pareja_id": 0,
                    "estado_inscripcion": "organizador",
                    "categoria_id": None
                }
            }
            torneos.append(torneo_data)
        
        return {"torneos": torneos}
        
    except Exception as e:
        print(f"❌ Error en mis-torneos-simple: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# INSTRUCCIONES PARA FACU:
# 1. Reemplazar el endpoint actual /torneos/mis-torneos con el código de arriba
# 2. O crear el endpoint simple si el complejo da problemas
# 3. Asegurar que todos los parámetros sean opcionales
# 4. Probar que responda sin error 422

print("✅ Solución backend para /torneos/mis-torneos preparada")