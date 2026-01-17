#!/usr/bin/env python3
"""
Test script para verificar si hay parejas faltantes en las zonas (referencias a parejas que ya no existen)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.services.torneo_zona_service import TorneoZonaService
from src.models.torneo_models import TorneoZonaPareja, TorneoPareja

def test_verificar_parejas_faltantes():
    """Test para verificar si hay referencias a parejas eliminadas en las zonas"""
    db = next(get_db())
    
    try:
        # Usar torneo 17 que tiene zonas generadas
        torneo_id = 17
        
        print(f"🔍 Verificando parejas faltantes en torneo {torneo_id}...")
        
        # Obtener todas las asignaciones de zona del torneo
        from src.models.torneo_models import TorneoZona
        
        asignaciones = db.query(TorneoZonaPareja).join(
            TorneoZona,
            TorneoZonaPareja.zona_id == TorneoZona.id
        ).filter(
            TorneoZona.torneo_id == torneo_id
        ).all()
        
        print(f"📊 Total de asignaciones zona-pareja: {len(asignaciones)}")
        
        parejas_faltantes = []
        
        for asignacion in asignaciones:
            # Verificar si la pareja existe
            pareja = db.query(TorneoPareja).filter(
                TorneoPareja.id == asignacion.pareja_id
            ).first()
            
            if not pareja:
                parejas_faltantes.append(asignacion)
                print(f"❌ Pareja faltante: ID {asignacion.pareja_id} en zona {asignacion.zona_id}")
        
        if parejas_faltantes:
            print(f"\n⚠️ Encontradas {len(parejas_faltantes)} parejas faltantes")
            
            # Probar el servicio con estas parejas faltantes
            print("\n🧪 Probando servicio con parejas faltantes...")
            zonas = TorneoZonaService.listar_zonas(db, torneo_id)
            
            for zona in zonas:
                parejas_eliminadas = [p for p in zona['parejas'] if p.get('eliminada', False)]
                if parejas_eliminadas:
                    print(f"✅ Zona {zona['nombre']}: {len(parejas_eliminadas)} parejas eliminadas detectadas")
                    
                    # Probar tabla de posiciones
                    tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona['id'])
                    eliminadas_en_tabla = [item for item in tabla['tabla'] if item.get('eliminada', False)]
                    print(f"   📋 Tabla: {len(eliminadas_en_tabla)} parejas eliminadas en posiciones")
        else:
            print("✅ No se encontraron parejas faltantes")
            
            # Simular creando una referencia huérfana para probar
            print("\n🧪 Simulando referencia huérfana para probar...")
            
            # Crear una asignación temporal con ID inexistente
            asignacion_test = TorneoZonaPareja(
                zona_id=asignaciones[0].zona_id,  # Usar zona existente
                pareja_id=99999  # ID que no existe
            )
            db.add(asignacion_test)
            db.commit()
            
            print("📝 Referencia huérfana creada temporalmente")
            
            # Probar el servicio
            zonas = TorneoZonaService.listar_zonas(db, torneo_id)
            zona_test = next((z for z in zonas if z['id'] == asignaciones[0].zona_id), None)
            
            if zona_test:
                parejas_eliminadas = [p for p in zona_test['parejas'] if p.get('eliminada', False)]
                if parejas_eliminadas:
                    print(f"✅ Servicio detectó correctamente {len(parejas_eliminadas)} parejas eliminadas")
                    
                    # Probar tabla
                    tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona_test['id'])
                    eliminadas_en_tabla = [item for item in tabla['tabla'] if item.get('eliminada', False)]
                    if eliminadas_en_tabla:
                        print(f"✅ Tabla detectó correctamente {len(eliminadas_en_tabla)} parejas eliminadas")
                        for item in eliminadas_en_tabla:
                            print(f"   ❌ {item['pareja_nombre']} (ID: {item['pareja_id']})")
                else:
                    print("❌ Servicio no detectó parejas eliminadas")
            
            # Limpiar
            db.delete(asignacion_test)
            db.commit()
            print("🧹 Referencia huérfana eliminada")
        
        print("\n✅ Test completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_verificar_parejas_faltantes()