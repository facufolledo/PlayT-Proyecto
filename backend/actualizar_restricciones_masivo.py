"""
Script para actualizar restricciones masivas del torneo 25
Restriccion por defecto: Viernes 09:00 a 16:00
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import PerfilUsuario

TORNEO_ID = 25

def actualizar_masivo():
    """Actualiza restricciones de todas las parejas sin restricciones"""
    
    db = next(get_db())
    
    try:
        print("=" * 80)
        print(f"ACTUALIZAR RESTRICCIONES MASIVO - Torneo {TORNEO_ID}")
        print("=" * 80)
        
        # Restriccion por defecto
        restriccion_default = [
            {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "16:00"}
        ]
        
        print(f"\nRestriccion a aplicar: Viernes 09:00 - 16:00")
        
        # Buscar parejas confirmadas sin restricciones
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == TORNEO_ID,
            TorneoPareja.estado == 'confirmada',
            TorneoPareja.disponibilidad_horaria == None
        ).all()
        
        print(f"\nParejas sin restricciones encontradas: {len(parejas)}")
        
        if len(parejas) == 0:
            print("\nTodas las parejas confirmadas ya tienen restricciones")
            
            # Mostrar resumen
            total = db.query(TorneoPareja).filter(
                TorneoPareja.torneo_id == TORNEO_ID
            ).count()
            
            con_restricciones = db.query(TorneoPareja).filter(
                TorneoPareja.torneo_id == TORNEO_ID,
                TorneoPareja.disponibilidad_horaria.isnot(None)
            ).count()
            
            print(f"\nResumen torneo {TORNEO_ID}:")
            print(f"  Total parejas: {total}")
            print(f"  Con restricciones: {con_restricciones}")
            print(f"  Sin restricciones: {total - con_restricciones}")
            return
        
        print("\nParejas a actualizar:")
        for i, pareja in enumerate(parejas, 1):
            p1 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador1_id
            ).first()
            p2 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador2_id
            ).first()
            
            nombre_j1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Usuario {pareja.jugador1_id}"
            nombre_j2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Usuario {pareja.jugador2_id}"
            
            print(f"  {i}. ID {pareja.id}: {nombre_j1} / {nombre_j2}")
        
        # Confirmar
        print("\n" + "=" * 80)
        confirmar = input("\nConfirmar actualizacion? (si/no): ").strip().lower()
        
        if confirmar != 'si':
            print("\nCambios descartados")
            return
        
        # Actualizar
        actualizadas = 0
        for pareja in parejas:
            pareja.disponibilidad_horaria = restriccion_default
            actualizadas += 1
        
        db.commit()
        print(f"\nActualizadas exitosamente: {actualizadas} parejas")
        
        # Resumen final
        total = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == TORNEO_ID
        ).count()
        
        con_restricciones = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == TORNEO_ID,
            TorneoPareja.disponibilidad_horaria.isnot(None)
        ).count()
        
        print(f"\nResumen final torneo {TORNEO_ID}:")
        print(f"  Total parejas: {total}")
        print(f"  Con restricciones: {con_restricciones}")
        print(f"  Sin restricciones: {total - con_restricciones}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    actualizar_masivo()
