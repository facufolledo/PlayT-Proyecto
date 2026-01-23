"""
Actualizar restricciones de las parejas restantes del torneo 25
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import PerfilUsuario

TORNEO_ID = 25

# IDs de parejas que YA tienen restricciones personalizadas
PAREJAS_CON_RESTRICCIONES = [442, 443, 444, 445, 448]

def actualizar():
    db = next(get_db())
    
    try:
        print("=" * 80)
        print(f"ACTUALIZAR RESTO DE PAREJAS - Torneo {TORNEO_ID}")
        print("=" * 80)
        
        # Restriccion por defecto
        restriccion_default = [
            {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "16:00"}
        ]
        
        print(f"\nRestriccion por defecto: Viernes 09:00 - 16:00")
        print(f"Parejas que ya tienen restricciones personalizadas: {PAREJAS_CON_RESTRICCIONES}\n")
        
        # Buscar todas las parejas confirmadas del torneo
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == TORNEO_ID,
            TorneoPareja.estado == 'confirmada',
            ~TorneoPareja.id.in_(PAREJAS_CON_RESTRICCIONES)
        ).all()
        
        print(f"Parejas a actualizar: {len(parejas)}\n")
        
        if len(parejas) == 0:
            print("No hay parejas para actualizar")
            return
        
        for i, pareja in enumerate(parejas, 1):
            p1 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador1_id
            ).first()
            p2 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador2_id
            ).first()
            
            nombre_j1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Usuario {pareja.jugador1_id}"
            nombre_j2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Usuario {pareja.jugador2_id}"
            
            print(f"{i:2}. ID {pareja.id:3}: {nombre_j1:30} / {nombre_j2}")
        
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
        
        # Verificar resultado
        print("\nVerificando...")
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM torneos_parejas 
            WHERE torneo_id = 25 
            AND disponibilidad_horaria IS NOT NULL 
            AND disponibilidad_horaria::text != 'null'
        """))
        
        total_con_restricciones = result.scalar()
        
        print(f"Total parejas con restricciones: {total_con_restricciones}/23")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    actualizar()
