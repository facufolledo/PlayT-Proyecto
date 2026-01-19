#!/usr/bin/env python3
"""
Actualizar disponibilidad de la pareja 421 (Facundo + Facundito)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.torneo_models import TorneoPareja

def actualizar_disponibilidad():
    """Actualizar disponibilidad de pareja 421"""
    db = next(get_db())
    
    try:
        pareja_id = 421
        
        # Buscar pareja
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
        if not pareja:
            print(f"❌ Pareja {pareja_id} no encontrada")
            return False
        
        print(f"👥 Pareja {pareja_id}: {pareja.jugador1_id} / {pareja.jugador2_id}")
        print(f"📋 Disponibilidad actual: {pareja.disponibilidad_horaria}")
        
        # Ejemplo de restricciones (ajusta según lo que necesites)
        # Formato: lista de restricciones con días y horarios que NO pueden jugar
        restricciones = [
            {
                "dias": ["viernes"],
                "horaInicio": "15:00",
                "horaFin": "18:00"
            }
        ]
        
        print(f"\n¿Qué restricciones quieres agregar?")
        print(f"Ejemplo actual: No pueden jugar viernes de 15:00 a 18:00")
        print(f"\nOpciones:")
        print(f"1. Viernes 15:00-18:00 (tarde)")
        print(f"2. Viernes 19:00-23:59 (noche)")
        print(f"3. Sábado 09:00-13:00 (mañana)")
        print(f"4. Domingo 18:00-23:59 (tarde)")
        print(f"5. Sin restricciones")
        
        opcion = input(f"\nSelecciona opción (1-5): ").strip()
        
        if opcion == "1":
            restricciones = [{"dias": ["viernes"], "horaInicio": "15:00", "horaFin": "18:00"}]
        elif opcion == "2":
            restricciones = [{"dias": ["viernes"], "horaInicio": "19:00", "horaFin": "23:59"}]
        elif opcion == "3":
            restricciones = [{"dias": ["sabado"], "horaInicio": "09:00", "horaFin": "13:00"}]
        elif opcion == "4":
            restricciones = [{"dias": ["domingo"], "horaInicio": "18:00", "horaFin": "23:59"}]
        elif opcion == "5":
            restricciones = []
        else:
            print(f"❌ Opción inválida")
            return False
        
        # Actualizar
        pareja.disponibilidad_horaria = restricciones
        db.commit()
        
        print(f"\n✅ Disponibilidad actualizada:")
        print(f"   {restricciones}")
        print(f"\n💡 Ahora elimina y regenera el fixture para que se respeten las restricciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 ACTUALIZAR DISPONIBILIDAD PAREJA 421")
    print("="*60)
    actualizar_disponibilidad()
