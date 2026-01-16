"""
Verificar disponibilidad de todas las parejas del torneo 11
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.models.torneo_models import TorneoPareja

load_dotenv()

def verificar_disponibilidad():
    print("=" * 80)
    print("VERIFICAR DISPONIBILIDAD: TODAS LAS PAREJAS DEL TORNEO 11")
    print("=" * 80)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        torneo_id = 11
        
        # Obtener todas las parejas
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id,
            TorneoPareja.estado.in_(['inscripta', 'confirmada'])
        ).all()
        
        print(f"\n📊 Total de parejas: {len(parejas)}")
        print("=" * 80)
        
        con_disponibilidad = 0
        sin_disponibilidad = 0
        
        for pareja in parejas:
            tiene_disp = pareja.disponibilidad_horaria is not None and pareja.disponibilidad_horaria != {}
            
            if tiene_disp:
                con_disponibilidad += 1
                status = "✅"
            else:
                sin_disponibilidad += 1
                status = "❌"
            
            print(f"{status} Pareja {pareja.id:3} | J1: {pareja.jugador1_id:3} J2: {pareja.jugador2_id:3} | Cat: {pareja.categoria_id} | Disp: {pareja.disponibilidad_horaria}")
        
        print("\n" + "=" * 80)
        print(f"RESUMEN:")
        print(f"  ✅ Con disponibilidad: {con_disponibilidad}")
        print(f"  ❌ Sin disponibilidad: {sin_disponibilidad}")
        print("=" * 80)
        
        if sin_disponibilidad > 0:
            print(f"\n⚠️  PROBLEMA: {sin_disponibilidad} parejas no tienen disponibilidad horaria configurada")
            print(f"   Esto significa que el sistema las tratará como 'disponibles siempre'")
            print(f"   y las programará en cualquier horario.")
            print(f"\n💡 SOLUCIÓN:")
            print(f"   1. Verificar que el frontend esté enviando disponibilidad_horaria al inscribirse")
            print(f"   2. Actualizar manualmente las parejas existentes con su disponibilidad")
            print(f"   3. Eliminar y regenerar el fixture")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_disponibilidad()
