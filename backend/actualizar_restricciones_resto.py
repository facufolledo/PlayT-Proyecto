"""
Script para actualizar restricciones del resto de parejas del torneo 25
Restricción por defecto: Viernes 09:00 a 16:00
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import PerfilUsuario

TORNEO_ID = 25

def actualizar_resto_parejas():
    """Actualiza restricciones de parejas sin restricciones"""
    
    db = next(get_db())
    
    try:
        print("=" * 80)
        print(f"ACTUALIZAR RESTRICCIONES RESTO DE PAREJAS - Torneo {TORNEO_ID}")
        print("=" * 80)
        
        # Restricción por defecto
        restriccion_default = [
            {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "16:00"}
        ]
        
        print(f"\n📋 Restricción a aplicar:")
        print(f"   🚫 Viernes: 09:00 - 16:00")
        
        # Buscar parejas sin restricciones
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == TORNEO_ID,
            TorneoPareja.disponibilidad_horaria.is_(None)
        ).all()
        
        print(f"\n📊 Parejas sin restricciones encontradas: {len(parejas)}\n")
        
        if len(parejas) == 0:
            print("✅ Todas las parejas ya tienen restricciones configuradas")
            return
        
        actualizadas = 0
        
        for pareja in parejas:
            try:
                # Obtener nombres
                p1 = db.query(PerfilUsuario).filter(
                    PerfilUsuario.id_usuario == pareja.jugador1_id
                ).first()
                p2 = db.query(PerfilUsuario).filter(
                    PerfilUsuario.id_usuario == pareja.jugador2_id
                ).first()
                
                nombre_j1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Usuario {pareja.jugador1_id}"
                nombre_j2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Usuario {pareja.jugador2_id}"
                
                print(f"✅ Pareja {pareja.id}: {nombre_j1:30} / {nombre_j2}")
                print(f"   Estado: {pareja.estado}")
                
                # Actualizar restricción
                pareja.disponibilidad_horaria = restriccion_default
                actualizadas += 1
                
            except Exception as e:
                print(f"❌ Error con pareja {pareja.id}: {e}")
        
        # Resumen y confirmación
        print(f"\n{'=' * 80}")
        print(f"📊 RESUMEN:")
        print(f"   ✅ Parejas a actualizar: {actualizadas}")
        print(f"{'=' * 80}")
        
        if actualizadas > 0:
            confirmar = input("\n¿Confirmar cambios en la base de datos? (si/no): ").strip().lower()
            
            if confirmar == 'si':
                db.commit()
                print("\n✅ Cambios guardados exitosamente en la base de datos")
                
                # Verificar resultado final
                total_con_restricciones = db.query(TorneoPareja).filter(
                    TorneoPareja.torneo_id == TORNEO_ID,
                    TorneoPareja.disponibilidad_horaria.isnot(None)
                ).count()
                
                total_parejas = db.query(TorneoPareja).filter(
                    TorneoPareja.torneo_id == TORNEO_ID
                ).count()
                
                print(f"\n📊 Estado final del torneo {TORNEO_ID}:")
                print(f"   Total de parejas: {total_parejas}")
                print(f"   Con restricciones: {total_con_restricciones}")
                print(f"   Sin restricciones: {total_parejas - total_con_restricciones}")
                
            else:
                db.rollback()
                print("\n❌ Cambios descartados")
        else:
            print("\n⚠️  No se actualizó ninguna pareja")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    actualizar_resto_parejas()
