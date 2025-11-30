"""
Script para preparar el torneo ID 25 para pruebas de frontend
- Inscribe 5 parejas y las confirma
- Deja espacio para 1 pareja más (max_parejas = 6)
- Genera zonas
- Genera fixture
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.models.torneo_models import Torneo, TorneoPareja
from src.services.torneo_zona_service import TorneoZonaService
from src.services.torneo_fixture_service import TorneoFixtureService

def preparar_torneo():
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("PREPARANDO TORNEO ID 25 PARA PRUEBAS")
        print("="*70)
        
        # 1. Verificar que existe el torneo
        torneo = db.query(Torneo).filter(Torneo.id == 25).first()
        if not torneo:
            print("❌ ERROR: No existe el torneo con ID 25")
            print("   Crea primero el torneo desde el frontend")
            return
        
        print(f"\n✅ Torneo encontrado: {torneo.nombre}")
        print(f"   Categoría: {torneo.categoria}")
        print(f"   Max parejas: {torneo.max_parejas}")
        
        # 2. Verificar parejas existentes
        parejas_existentes = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == 25
        ).all()
        
        print(f"\n📊 Parejas actuales: {len(parejas_existentes)}")
        
        if len(parejas_existentes) >= 5:
            print("   Ya hay 5 o más parejas inscritas")
            
            # Confirmar todas las parejas
            for pareja in parejas_existentes[:5]:
                if pareja.estado != 'confirmada':
                    pareja.estado = 'confirmada'
                    print(f"   ✅ Confirmada pareja {pareja.id}: {pareja.nombre_pareja}")
            
            db.commit()
        else:
            # Inscribir parejas de prueba
            parejas_a_crear = 5 - len(parejas_existentes)
            print(f"\n📝 Inscribiendo {parejas_a_crear} parejas de prueba...")
            
            # IDs de usuarios de prueba (ajusta según tu BD)
            usuarios_disponibles = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
            
            for i in range(parejas_a_crear):
                idx = len(parejas_existentes) + i
                jugador1 = usuarios_disponibles[idx * 2]
                jugador2 = usuarios_disponibles[idx * 2 + 1]
                
                pareja = TorneoPareja(
                    torneo_id=25,
                    jugador1_id=jugador1,
                    jugador2_id=jugador2,
                    nombre_pareja=f"Pareja {jugador1}/{jugador2}",
                    estado='confirmada'
                )
                db.add(pareja)
                print(f"   ✅ Inscrita pareja: {pareja.nombre_pareja}")
            
            db.commit()
        
        # 3. Recargar parejas confirmadas
        parejas_confirmadas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == 25,
            TorneoPareja.estado == 'confirmada'
        ).all()
        
        print(f"\n✅ Total parejas confirmadas: {len(parejas_confirmadas)}")
        print(f"   Espacio disponible: {torneo.max_parejas - len(parejas_confirmadas)} parejas")
        
        # 4. Generar zonas
        print("\n🎯 Generando zonas...")
        parejas_ids = [p.id for p in parejas_confirmadas]
        
        try:
            zonas = TorneoZonaService.generar_zonas(db, 25, parejas_ids, user_id=4)
            print(f"   ✅ {len(zonas)} zonas generadas")
            
            for zona in zonas:
                print(f"      - {zona['nombre']}: {len(zona['parejas'])} parejas")
        except Exception as e:
            if "ya tiene zonas" in str(e):
                print("   ℹ️  Las zonas ya estaban generadas")
            else:
                raise
        
        # 5. Generar fixture
        print("\n📅 Generando fixture...")
        
        try:
            resultado = TorneoFixtureService.generar_fixture(db, 25, user_id=4)
            print(f"   ✅ {resultado['total_partidos']} partidos generados")
            print(f"      Partidos por zona: {resultado['partidos_por_zona']}")
        except Exception as e:
            if "ya tiene partidos" in str(e):
                print("   ℹ️  El fixture ya estaba generado")
            else:
                raise
        
        print("\n" + "="*70)
        print("✅ TORNEO PREPARADO EXITOSAMENTE")
        print("="*70)
        print("\n📋 RESUMEN:")
        print(f"   • Torneo ID: 25")
        print(f"   • Parejas confirmadas: {len(parejas_confirmadas)}")
        print(f"   • Espacio disponible: {torneo.max_parejas - len(parejas_confirmadas)} pareja(s)")
        print(f"   • Zonas: Generadas")
        print(f"   • Fixture: Generado")
        print("\n🎮 PRÓXIMOS PASOS:")
        print("   1. Abre el frontend en http://localhost:5173")
        print("   2. Ve a Torneos → Torneo ID 25")
        print("   3. Inscribe una pareja más (opcional)")
        print("   4. Ve a la tab 'Zonas' para ver las zonas")
        print("   5. Ve a la tab 'Fixture' para cargar resultados")
        print("   6. Carga resultados partido por partido")
        print("   7. Ve cómo se actualiza la tabla de posiciones")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    preparar_torneo()
