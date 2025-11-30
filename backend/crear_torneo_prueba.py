"""
Script para crear un torneo de prueba con el usuario ID 14 como organizador
- Crea el torneo
- Inscribe 5 parejas y las confirma
- Deja espacio para 1 pareja más
- Genera zonas
- Genera fixture
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database.config import SessionLocal
from src.models.torneo_models import Torneo, TorneoPareja
from src.services.torneo_zona_service import TorneoZonaService
from src.services.torneo_fixture_service import TorneoFixtureService

def crear_torneo_prueba():
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("CREANDO TORNEO DE PRUEBA")
        print("="*70)
        
        # 1. Crear el torneo
        print("\n📝 Creando torneo...")
        
        fecha_inicio = datetime.now() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(days=2)
        
        torneo = Torneo(
            nombre="Torneo de Prueba - Sistema de Resultados",
            descripcion="Torneo para probar el sistema de zonas, fixture y resultados. Max 6 parejas.",
            fecha_inicio=fecha_inicio.date(),
            fecha_fin=fecha_fin.date(),
            lugar="Club de Prueba",
            categoria="A",
            estado="inscripcion",
            creado_por=14  # Tu usuario
        )
        
        db.add(torneo)
        db.commit()
        db.refresh(torneo)
        
        print(f"✅ Torneo creado: ID {torneo.id}")
        print(f"   Nombre: {torneo.nombre}")
        print(f"   Organizador: Usuario ID 14")
        print(f"   Max parejas: 6 (configurado)")
        
        # 2. Inscribir 5 parejas de prueba
        print(f"\n📝 Inscribiendo 5 parejas de prueba...")
        
        # Usar IDs de usuarios existentes (ajusta si es necesario)
        parejas_data = [
            (4, 5),
            (6, 7),
            (8, 9),
            (10, 11),
            (12, 13),
        ]
        
        parejas_creadas = []
        for jugador1, jugador2 in parejas_data:
            # Crear pareja sin especificar estado, se asignará el default
            pareja = TorneoPareja(
                torneo_id=torneo.id,
                jugador1_id=jugador1,
                jugador2_id=jugador2
            )
            db.add(pareja)
            db.flush()  # Para obtener el ID
            
            # Actualizar estado manualmente con SQL (usar mayúsculas para el enum)
            db.execute(
                text(f"UPDATE torneos_parejas SET estado = 'CONFIRMADA' WHERE id = {pareja.id}")
            )
            
            parejas_creadas.append(pareja)
            print(f"   ✅ Inscrita y confirmada: Pareja {jugador1}/{jugador2}")
        
        db.commit()
        
        # Refrescar para obtener IDs
        for pareja in parejas_creadas:
            db.refresh(pareja)
        
        print(f"\n✅ Total parejas confirmadas: {len(parejas_creadas)}")
        print(f"   Espacio disponible: 1 pareja (para que pruebes inscribirte)")
        
        # 3. Generar zonas
        print("\n🎯 Generando zonas...")
        
        # Firma: generar_zonas_automaticas(db, torneo_id, user_id, num_zonas=None, balancear_por_rating=True)
        zonas = TorneoZonaService.generar_zonas_automaticas(
            db=db,
            torneo_id=torneo.id,
            user_id=14
        )
        print(f"   ✅ {len(zonas)} zonas generadas")
        
        # Obtener información de las zonas
        from src.models.torneo_models import TorneoZona, TorneoZonaPareja
        zonas_info = db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo.id).all()
        for zona in zonas_info:
            parejas_count = db.query(TorneoZonaPareja).filter(
                TorneoZonaPareja.zona_id == zona.id
            ).count()
            print(f"      - {zona.nombre}: {parejas_count} parejas")
        
        # 4. Generar fixture
        print("\n📅 Generando fixture...")
        
        # Firma: generar_fixture_completo(db, torneo_id, user_id)
        resultado = TorneoFixtureService.generar_fixture_completo(
            db=db,
            torneo_id=torneo.id,
            user_id=14
        )
        print(f"   ✅ {resultado['total_partidos']} partidos generados")
        print(f"      Partidos por zona: {resultado['partidos_por_zona']}")
        
        print("\n" + "="*70)
        print("✅ TORNEO CREADO Y PREPARADO EXITOSAMENTE")
        print("="*70)
        print("\n📋 RESUMEN:")
        print(f"   • Torneo ID: {torneo.id}")
        print(f"   • Nombre: {torneo.nombre}")
        print(f"   • Organizador: Usuario ID 14 (tú)")
        print(f"   • Parejas confirmadas: {len(parejas_creadas)}")
        print(f"   • Espacio disponible: 1 pareja")
        print(f"   • Zonas: {len(zonas)} generadas")
        print(f"   • Partidos: {resultado['total_partidos']} generados")
        print("\n🎮 PRÓXIMOS PASOS:")
        print("   1. Abre el frontend en http://localhost:5173")
        print(f"   2. Ve a Torneos → Torneo ID {torneo.id}")
        print("   3. (Opcional) Inscribe una pareja más")
        print("   4. Ve a la tab 'Zonas' para ver las zonas y tablas")
        print("   5. Ve a la tab 'Fixture' para ver los partidos")
        print("   6. Carga resultados partido por partido")
        print("   7. Ve cómo se actualiza la tabla de posiciones en tiempo real")
        print("\n💡 TIPS:")
        print("   • Como organizador (ID 14), puedes cargar resultados")
        print("   • Prueba diferentes resultados: 2-0, 2-1")
        print("   • Observa cómo cambia la tabla después de cada resultado")
        print("   • Los primeros 2 de cada zona clasifican (marcados con 🏆)")
        print("\n" + "="*70 + "\n")
        
        return torneo.id
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    torneo_id = crear_torneo_prueba()
    if torneo_id:
        print(f"🎉 ¡Listo! Torneo ID {torneo_id} creado exitosamente")
