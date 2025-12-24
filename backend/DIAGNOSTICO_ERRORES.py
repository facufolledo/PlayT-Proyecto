# DIAGNÓSTICO COMPLETO DE ERRORES

# 🔍 SCRIPT PARA DIAGNOSTICAR TODOS LOS ERRORES

@app.get("/debug/diagnostico-completo")
async def diagnostico_completo():
    """Endpoint para diagnosticar todos los errores reportados"""
    
    diagnostico = {
        "timestamp": datetime.now().isoformat(),
        "errores": {},
        "soluciones": {}
    }
    
    # 1. VERIFICAR CORS
    try:
        # Simular request CORS
        diagnostico["errores"]["cors"] = {
            "status": "verificar_manualmente",
            "mensaje": "Verificar origins en main.py",
            "origins_requeridos": [
                "http://localhost:3000",
                "http://localhost:5173",
                "https://kioskito.click", 
                "https://www.kioskito.click"
            ]
        }
        
        diagnostico["soluciones"]["cors"] = "Agregar localhost:5173 a origins en main.py"
        
    except Exception as e:
        diagnostico["errores"]["cors"] = {"error": str(e)}
    
    # 2. VERIFICAR ENDPOINT MIS-TORNEOS
    try:
        # Verificar si el endpoint existe y sus parámetros
        diagnostico["errores"]["mis_torneos"] = {
            "status": "error_422",
            "posibles_causas": [
                "Parámetros requeridos no enviados",
                "Validación de request fallando",
                "Problema en query SQL",
                "Error en get_current_user"
            ]
        }
        
        diagnostico["soluciones"]["mis_torneos"] = "Hacer parámetros opcionales o verificar validación"
        
    except Exception as e:
        diagnostico["errores"]["mis_torneos"] = {"error": str(e)}
    
    # 3. VERIFICAR HISTORIAL_ENFRENTAMIENTOS
    try:
        # Verificar estructura de tabla
        query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'historial_enfrentamientos'
        """
        
        columns = await database.fetch_all(query)
        column_names = [col['column_name'] for col in columns]
        
        tiene_id_sala = 'id_sala' in column_names
        
        diagnostico["errores"]["historial_enfrentamiento"] = {
            "tabla_existe": len(columns) > 0,
            "tiene_id_sala": tiene_id_sala,
            "columnas": column_names
        }
        
        if not tiene_id_sala:
            diagnostico["soluciones"]["historial_enfrentamiento"] = "Eliminar referencias a id_sala o agregar campo"
        else:
            diagnostico["soluciones"]["historial_enfrentamiento"] = "Campo existe, verificar uso en código"
            
    except Exception as e:
        diagnostico["errores"]["historial_enfrentamiento"] = {"error": str(e)}
    
    # 4. VERIFICAR CONECTIVIDAD GENERAL
    try:
        # Test de conectividad básica
        test_query = "SELECT 1 as test"
        result = await database.fetch_one(test_query)
        
        diagnostico["conectividad"] = {
            "database": "ok" if result else "error",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        diagnostico["conectividad"] = {"error": str(e)}
    
    return diagnostico

# 🛠️ ENDPOINTS DE REPARACIÓN AUTOMÁTICA

@app.post("/debug/reparar-cors")
async def reparar_cors():
    """Generar código para reparar CORS"""
    
    codigo_cors = '''
# AGREGAR A main.py - CONFIGURACIÓN CORS CORRECTA

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # ← AGREGAR ESTA LÍNEA
    "https://kioskito.click",
    "https://www.kioskito.click"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''
    
    return {
        "solucion": "cors",
        "codigo": codigo_cors,
        "instrucciones": "Copiar y pegar en main.py, reiniciar servidor"
    }

@app.post("/debug/reparar-mis-torneos")
async def reparar_mis_torneos():
    """Generar endpoint corregido para mis-torneos"""
    
    codigo_endpoint = '''
@app.get("/torneos/mis-torneos")
async def get_mis_torneos(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """Obtener torneos del usuario - VERSIÓN CORREGIDA"""
    try:
        query = """
        SELECT DISTINCT t.id, t.nombre, t.estado, t.fecha_inicio, t.fecha_fin,
               t.organizador_id, t.descripcion
        FROM torneos t
        LEFT JOIN torneo_participantes tp ON t.id = tp.id_torneo
        WHERE t.organizador_id = %s OR tp.id_usuario = %s
        ORDER BY t.fecha_inicio DESC
        LIMIT %s OFFSET %s
        """
        
        result = await database.fetch_all(query, [
            current_user.id_usuario,
            current_user.id_usuario,
            limit,
            offset
        ])
        
        return result
        
    except Exception as e:
        print(f"Error en mis-torneos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    return {
        "solucion": "mis_torneos",
        "codigo": codigo_endpoint,
        "instrucciones": "Reemplazar endpoint existente"
    }

@app.post("/debug/reparar-historial")
async def reparar_historial():
    """Generar solución para historial_enfrentamientos"""
    
    # Verificar si existe id_sala
    try:
        query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'historial_enfrentamientos' 
        AND column_name = 'id_sala'
        """
        
        result = await database.fetch_one(query)
        tiene_id_sala = result is not None
        
        if tiene_id_sala:
            codigo = '''
# SOLUCIÓN: Campo id_sala existe
def eliminar_sala_con_historial(sala_id: int):
    try:
        # Eliminar historial primero
        await database.execute(
            "DELETE FROM historial_enfrentamientos WHERE id_sala = %s", 
            [sala_id]
        )
        
        # Luego eliminar sala
        await database.execute(
            "DELETE FROM salas WHERE id = %s", 
            [sala_id]
        )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(500, str(e))
'''
        else:
            codigo = '''
# SOLUCIÓN: Campo id_sala NO existe
def eliminar_sala_sin_historial(sala_id: int):
    try:
        # Solo eliminar la sala, no tocar historial
        await database.execute(
            "DELETE FROM salas WHERE id = %s", 
            [sala_id]
        )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(500, str(e))
'''
        
        return {
            "solucion": "historial_enfrentamiento",
            "tiene_id_sala": tiene_id_sala,
            "codigo": codigo,
            "instrucciones": "Usar el código según si existe id_sala o no"
        }
        
    except Exception as e:
        return {"error": str(e)}

print("✅ Sistema de diagnóstico y reparación preparado")